"""Preview and apply an offline Foundry snapshot import.

The shape of this use case is fixed by plan §6.5, and it is worth naming why
each part is the way it is.

**Preview persists nothing.** It parses, reads, compares and rolls back. There
is no stored preview row to go stale in the database, and no window in which a
half-prepared import exists.

**The preview's inputs are bound, and apply re-checks all of them.** The binding
covers the snapshot checksum, the world id, the selected folder's id *and*
displayed path, the field-profile version, the exporter schema, the optimistic
version of every character the run would touch, and the request key. Apply
recomputes the binding from the artifact it is given and the database as it
stands *now*; any difference makes the preview stale and applies nothing.

**An import writes identity, mappings and provenance — never a character
field.** ADR 0008 was rejected on 2026-08-02, so there is no selection list, no
correction service and no route from a snapshot value into character game state.
A run creates characters for unmapped Actors, records their mappings, stores the
snapshot's provenance and audits the lot. Everything else it has to say, it says
in the reconciliation report.

**Parsing happens before the transaction opens.** A malformed, wrong-world or
wrong-version artifact is refused with no transaction to roll back.

**Two keys, two jobs.** The request key identifies an *attempt*, so a retry
returns the original result instead of applying twice. The triple (snapshot,
folder, profile version) identifies an *input*, so re-applying the same
checksum is a typed duplicate rather than a second mutation. Both are enforced
by database constraints, not only by the check below — which is what makes them
hold for two concurrent applies rather than only for two sequential ones.

**A refusal is recorded once, safely, after the rollback.** The state
transaction rolls back completely; then a separate transaction writes one
refused import row and one attempted/refused audit event under the same
correlation ID. It claims no partial state and carries no artifact content.
"""
from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.authorization import (
    AuthorizationContext,
    AuthorizationPort,
    SupervisedBootstrap,
)
from application.bootstrap import BootstrapGate
from application.foundry.artifact import SnapshotArtifact
from application.foundry.extraction import SnapshotActorView
from application.foundry.parser import BundleLimits, ParsedSnapshot, parse_snapshot
from application.foundry.reconciliation import (
    ActorOutcome,
    ReconciliationReport,
    ReconciliationSource,
    reconcile,
    relink_fingerprint,
)
from application.repositories import UnitOfWork
from application.snapshots import (
    ExternalActorMapping,
    ImportMode,
    ImportStatus,
    SnapshotImportRecord,
    SnapshotRecord,
)
from domain.field_profile import FieldProfile
from domain.foundry import SupportedDeployment
from domain.identity import Character
from domain.names import DisplayName

SNAPSHOT_ENTITY = "foundry_snapshot"
IMPORT_APPLIED = "snapshot_import.applied"
IMPORT_REFUSED = "snapshot_import.refused"
IMPORT_DUPLICATE = "snapshot_import.duplicate"


class ImportRefused(RuntimeError):
    """The import was refused. Nothing was written by the attempt itself."""

    def __init__(self, code: str, message: str, *, report: ReconciliationReport | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.report = report


@dataclass(frozen=True, slots=True)
class PreviewBinding:
    """Everything an apply must find unchanged.

    Every field here is checked, and the check is generated from the field list
    rather than hand-written, so adding a field to the binding cannot leave it
    unverified. `tests/test_snapshot_import_service.py` asserts that property
    against the dataclass itself.
    """

    snapshot_checksum: str
    world_id: str
    folder_id: str
    #: The displayed folder path. Bound as well as the id because folder
    #: identity is (stable id, displayed path) under ADR 0006: a folder moved or
    #: renamed between preview and apply is a different confirmation from the
    #: one a Council member actually read.
    folder_path: str
    profile_version: str
    #: The exporter schema the artifact declares. A different exporter producing
    #: the same checksum is impossible, but a *re-export* that changes schema
    #: while a preview is outstanding must not slip through on folder identity.
    exporter: str
    #: (character id, optimistic version) for every character the run would read
    #: or touch. A change anywhere in here makes the preview stale.
    aggregate_versions: tuple[tuple[str, int], ...]
    request_key: str

    #: Field name → the sentence a refusal uses for it. Keeping this beside the
    #: fields is what lets the test prove every bound input is also reported.
    _DESCRIPTIONS = {
        "snapshot_checksum": "the snapshot artifact",
        "world_id": "the Foundry world",
        "folder_id": "the selected folder",
        "folder_path": "the selected folder's path",
        "profile_version": "the field-profile version",
        "exporter": "the exporter schema",
        "aggregate_versions": "a character that this import would touch",
        "request_key": "the request key",
    }

    def token(self) -> str:
        """A stable digest of the binding, for comparison and for the record."""
        parts = [
            self.snapshot_checksum,
            self.world_id,
            self.folder_id,
            self.folder_path,
            self.profile_version,
            self.exporter,
            self.request_key,
            "|".join(
                f"{identifier}={version}"
                for identifier, version in self.aggregate_versions
            ),
        ]
        return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()

    def differences(self, other: PreviewBinding) -> tuple[str, ...]:
        """What moved, named — so a refusal says which thing to look at."""
        return tuple(
            description
            for name, description in self._DESCRIPTIONS.items()
            if getattr(self, name) != getattr(other, name)
        )


@dataclass(frozen=True, slots=True)
class SnapshotPreview:
    """A dry run: what would happen, and what it was computed against."""

    binding: PreviewBinding
    report: ReconciliationReport
    selectable_folders: tuple[str, ...]

    @property
    def blocked(self) -> bool:
        return self.report.blocked

    @property
    def would_create(self) -> int:
        return self.report.count(ActorOutcome.UNMAPPED)


@dataclass(frozen=True, slots=True)
class ImportOutcome:
    status: ImportStatus
    report: ReconciliationReport
    correlation_id: UUID
    snapshot_checksum: str
    created_count: int = 0
    updated_count: int = 0
    #: `True` when this exact input had already been applied. A successful
    #: no-op, never a second mutation.
    duplicate: bool = False
    import_id: UUID | None = None
    refusal_code: str | None = None

    @property
    def applied(self) -> bool:
        return self.status is ImportStatus.APPLIED and not self.duplicate


class SnapshotImportService:
    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        *,
        deployment: SupportedDeployment,
        profile: FieldProfile,
        authorization: AuthorizationPort | None = None,
        bootstrap_gate: "BootstrapGate | None" = None,
        limits: BundleLimits | None = None,
        correlation_ids: Callable[[], UUID] = uuid4,
        character_ids: Callable[[], UUID] = uuid4,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._deployment = deployment
        self._profile = profile
        self._authorization = authorization
        self._bootstrap_gate = bootstrap_gate
        self._limits = limits
        self._correlation_ids = correlation_ids
        self._character_ids = character_ids

    # -- preview --------------------------------------------------------------

    def parse(self, artifact: SnapshotArtifact) -> ParsedSnapshot:
        """Validate the artifact. Outside any transaction, always."""
        artifact.verify()
        return parse_snapshot(
            artifact, deployment=self._deployment, limits=self._limits
        )

    def preview(
        self,
        artifact: SnapshotArtifact,
        *,
        request_key: str,
        folder_id: str | None = None,
    ) -> SnapshotPreview:
        """Reconcile without writing anything at all."""
        snapshot = self.parse(artifact)
        folder = folder_id or _default_folder(snapshot)

        with self._unit_of_work_factory() as unit_of_work:
            report, versions = self._reconcile(unit_of_work, snapshot, folder)
            # A preview is a rehearsal against the real schema, rolled back:
            # the same reads, and deliberately no writes to roll back.
            unit_of_work.rollback()

        binding = self._bind(snapshot, folder, report, versions, request_key)
        return SnapshotPreview(
            binding=binding,
            report=report,
            selectable_folders=tuple(
                str(identity.folder_id) for identity in snapshot.selectable_folders()
            ),
        )

    # -- apply ----------------------------------------------------------------

    def apply(
        self,
        artifact: SnapshotArtifact,
        preview: SnapshotPreview,
        *,
        discord_user_id: int | None = None,
        bootstrap: SupervisedBootstrap | None = None,
        folder_id: str | None = None,
    ) -> ImportOutcome:
        """Re-check everything, then commit in one transaction — or refuse.

        `folder_id` is the folder that is selected *now* — in Phase 3, whatever
        the Platform Administrator has configured at the moment of the apply.
        Passing it is how an administrator's folder change between preview and
        apply becomes a stale preview instead of a silent import from a folder
        nobody confirmed. Omitting it means "the preview's folder is still the
        selected one".
        """
        context, capability, mode, supervisor = self._resolve_authority(
            discord_user_id=discord_user_id, bootstrap=bootstrap
        )
        correlation_id = self._correlation_ids()
        snapshot = self.parse(artifact)
        folder = preview.binding.folder_id
        try:
            if folder_id is not None and folder_id != folder:
                raise ImportRefused(
                    "stale_preview",
                    "The preview is stale: the selected folder changed since it "
                    f"was produced ({folder} → {folder_id}). Nothing was "
                    "applied. Produce a new preview against the current folder "
                    "and confirm the exact scope.",
                    report=preview.report,
                )
            return self._apply_within_transaction(
                snapshot,
                preview,
                context=context,
                capability=capability,
                mode=mode,
                supervisor=supervisor,
                bootstrap=bootstrap,
                actor_discord_user_id=discord_user_id,
                correlation_id=correlation_id,
                folder=folder,
            )
        except ImportRefused as refusal:
            # The state transaction has already rolled back. One safe
            # attempted/refused record follows, in its own transaction, under
            # the same correlation ID — claiming no partial state.
            self._record_refusal(
                snapshot,
                preview,
                refusal=refusal,
                capability=capability,
                mode=mode,
                supervisor=supervisor,
                actor_discord_user_id=discord_user_id,
                correlation_id=correlation_id,
                folder=folder,
            )
            raise

    def _apply_within_transaction(
        self,
        snapshot: ParsedSnapshot,
        preview: SnapshotPreview,
        *,
        context: AuthorizationContext | None,
        capability: ActorCapability,
        mode: ImportMode,
        supervisor: str | None,
        bootstrap: SupervisedBootstrap | None,
        actor_discord_user_id: int | None,
        correlation_id: UUID,
        folder: str,
    ) -> ImportOutcome:
        with self._unit_of_work_factory() as unit_of_work:
            if mode is ImportMode.BOOTSTRAP:
                # Checked inside the transaction that would initialize the
                # platform, so two concurrent bootstraps race on the singleton
                # primary key rather than on a check either of them made
                # earlier.
                self._require_uninitialized(unit_of_work)
            existing = unit_of_work.snapshot_imports.find_by_request_key(
                preview.binding.request_key
            )
            if existing is not None:
                # A retry of the same attempt. The original result, not a
                # second application of it.
                unit_of_work.rollback()
                return ImportOutcome(
                    status=existing.status,
                    report=preview.report,
                    correlation_id=existing.correlation_id,
                    snapshot_checksum=snapshot.checksum.hex_digest,
                    created_count=existing.created_count,
                    updated_count=existing.updated_count,
                    duplicate=True,
                    import_id=existing.id,
                )

            report, versions = self._reconcile(unit_of_work, snapshot, folder)
            # Recomputed from the artifact in hand and the database as it
            # stands now — never read back off the preview, which is the object
            # whose freshness is in question.
            current = self._bind(
                snapshot, folder, report, versions, preview.binding.request_key
            )
            if current.token() != preview.binding.token():
                changes = ", ".join(preview.binding.differences(current)) or "an input"
                raise ImportRefused(
                    "stale_preview",
                    f"The preview is stale: {changes} changed since it was "
                    "produced. Nothing was applied. Produce a new preview and "
                    "confirm it.",
                    report=report,
                )

            if report.blocked:
                raise ImportRefused(
                    "blocked",
                    f"The import has {report.error_count} blocking issue(s) and "
                    "applies nothing. Resolve them and import again.",
                    report=report,
                )

            snapshot_record = self._store_snapshot(
                unit_of_work,
                snapshot,
                correlation_id=correlation_id,
                received_by=actor_discord_user_id,
            )
            already = unit_of_work.snapshot_imports.find_applied(
                snapshot_record.id, folder, self._profile.version
            )
            if already is not None:
                unit_of_work.rollback()
                return ImportOutcome(
                    status=ImportStatus.APPLIED,
                    report=report,
                    correlation_id=already.correlation_id,
                    snapshot_checksum=snapshot.checksum.hex_digest,
                    created_count=already.created_count,
                    updated_count=already.updated_count,
                    duplicate=True,
                    import_id=already.id,
                )

            created = self._create_unmapped(
                unit_of_work,
                snapshot,
                report,
                snapshot_record=snapshot_record,
                correlation_id=correlation_id,
                capability=capability,
                actor_discord_user_id=actor_discord_user_id,
            )
            record = SnapshotImportRecord(
                snapshot_id=snapshot_record.id,
                folder_id=folder,
                folder_path=report.folder.path,
                profile_version=self._profile.version,
                request_key=preview.binding.request_key,
                status=ImportStatus.APPLIED,
                mode=mode,
                actor_capability=capability,
                actor_discord_user_id=actor_discord_user_id,
                supervisor=supervisor,
                created_count=created,
                updated_count=0,
                warning_count=report.warning_count,
                summary=report.summary(),
                correlation_id=correlation_id,
            )
            if mode is ImportMode.BOOTSTRAP and bootstrap is not None:
                # Closes the gate in the same transaction as the import that
                # opened it: a rolled-back bootstrap leaves the platform
                # uninitialized, and a committed one can never run again.
                self._require_gate().complete(
                    unit_of_work,
                    supervisor=bootstrap,
                    snapshot_checksum=snapshot.checksum.hex_digest,
                    correlation_id=correlation_id,
                )
            unit_of_work.snapshot_imports.add(record)
            unit_of_work.audit.record(
                AuditEvent(
                    action=IMPORT_APPLIED,
                    entity_type=SNAPSHOT_ENTITY,
                    entity_id=snapshot.checksum.hex_digest,
                    source=AuditSource.IMPORT,
                    actor_capability=capability,
                    actor_discord_user_id=actor_discord_user_id,
                    correlation_id=correlation_id,
                    payload={
                        **report.summary(),
                        "mode": mode.value,
                        "supervisor": supervisor,
                        "request_key": preview.binding.request_key,
                        "preview_token": preview.binding.token(),
                        "characters_created": created,
                    },
                )
            )
            # State, mappings, reconciliation effects, correction transactions
            # and the success audit commit together. An audit failure takes the
            # state with it, because there is one transaction and this is it.
            unit_of_work.commit()

        return ImportOutcome(
            status=ImportStatus.APPLIED,
            report=report,
            correlation_id=correlation_id,
            snapshot_checksum=snapshot.checksum.hex_digest,
            created_count=created,
            updated_count=0,
            import_id=record.id,
        )

    # -- internals ------------------------------------------------------------

    def _resolve_authority(
        self, *, discord_user_id: int | None, bootstrap: SupervisedBootstrap | None
    ) -> tuple[AuthorizationContext | None, ActorCapability, ImportMode, str | None]:
        if bootstrap is not None:
            if discord_user_id is not None:
                raise ImportRefused(
                    "ambiguous_authority",
                    "An import is either a supervised bootstrap or a Council "
                    "action, not both.",
                )
            return None, bootstrap.capability, ImportMode.BOOTSTRAP, bootstrap.supervisor
        if discord_user_id is None or self._authorization is None:
            raise ImportRefused(
                "no_authority",
                "An import requires either one currently authorized Guild "
                "Council member or a supervised bootstrap.",
            )
        # Resolved *now*, not carried from the preview: a role revoked in
        # between refuses the apply.
        context = self._authorization.context_for(discord_user_id)
        context.require_council("Applying a Foundry snapshot import")
        return context, context.capability, ImportMode.COUNCIL, None

    def _require_gate(self) -> BootstrapGate:
        if self._bootstrap_gate is None:
            raise ImportRefused(
                "no_bootstrap_gate",
                "A supervised bootstrap needs a bootstrap gate, which is what "
                "records the initialization and closes the path afterwards.",
            )
        return self._bootstrap_gate

    def _require_uninitialized(self, unit_of_work: UnitOfWork) -> None:
        if unit_of_work.initialization.get() is not None:
            raise ImportRefused(
                "bootstrap_unavailable",
                "The Manager has already been initialized. The supervised "
                "bootstrap disables itself after its first success; later "
                "imports require one currently authorized Guild Council member. "
                "It is not an authorization bypass.",
            )
        if not unit_of_work.initialization.is_dataset_empty():
            raise ImportRefused(
                "bootstrap_requires_empty_dataset",
                "The Manager dataset already holds characters, mappings, "
                "snapshots or history. The supervised bootstrap runs only "
                "against an uninitialized dataset.",
            )

    def _bind(
        self,
        snapshot: ParsedSnapshot,
        folder: str,
        report: ReconciliationReport,
        versions: tuple[tuple[str, int], ...],
        request_key: str,
    ) -> PreviewBinding:
        """Bind a run to its exact inputs.

        One constructor for both the preview and the apply, so the two cannot
        drift into binding different things — which would make the staleness
        check compare two objects built by different rules and pass.
        """
        return PreviewBinding(
            snapshot_checksum=snapshot.checksum.hex_digest,
            world_id=snapshot.world.world_id,
            folder_id=folder,
            folder_path=report.folder.path,
            profile_version=self._profile.version,
            exporter=snapshot.exporter.describe(),
            aggregate_versions=versions,
            request_key=request_key,
        )

    def _reconcile(
        self, unit_of_work: UnitOfWork, snapshot: ParsedSnapshot, folder: str
    ) -> tuple[ReconciliationReport, tuple[tuple[str, int], ...]]:
        world_id = snapshot.world.world_id
        mappings = unit_of_work.external_actor_mappings.list_for_world(world_id)

        characters: dict[UUID, Character] = {}
        for mapping in mappings:
            character = unit_of_work.characters.get(mapping.character_id)
            if character is not None:
                characters[mapping.character_id] = character

        mapped_actor_ids = {mapping.external_actor_id for mapping in mappings}
        claims: dict[str, list[UUID]] = {}
        for actor in snapshot.actors_in(folder):
            if str(actor.actor_id) in mapped_actor_ids:
                continue
            # **Every** candidate, not the first. Under OD-42 a display name is
            # not an identity and several characters may hold one, so stopping
            # at the first match would turn an ambiguous case into an
            # unambiguous-looking one and hide the very collision the
            # reconciliation refuses on.
            key = DisplayName(actor.name).identity_key
            if key in claims:
                continue
            claims[key] = [
                candidate.id
                for candidate in unit_of_work.characters.find_by_display_name(
                    actor.name
                )
            ]

        source = ReconciliationSource(
            mappings=mappings, characters=characters, name_claims=claims
        )
        report = reconcile(
            snapshot, folder_id=folder, profile=self._profile, source=source
        )
        versions = tuple(
            sorted(
                (str(character_id), character.version)
                for character_id, character in characters.items()
            )
        )
        return report, versions

    def _store_snapshot(
        self,
        unit_of_work: UnitOfWork,
        snapshot: ParsedSnapshot,
        *,
        correlation_id: UUID,
        received_by: int | None,
    ) -> SnapshotRecord:
        existing = unit_of_work.snapshots.get_by_checksum(snapshot.checksum.hex_digest)
        if existing is not None:
            # An artifact is recorded once. Re-presenting it does not create a
            # second identity, and its original record is never edited.
            return existing
        return unit_of_work.snapshots.add(
            SnapshotRecord(
                checksum=snapshot.checksum.hex_digest,
                size_bytes=snapshot.size_bytes,
                schema_version=snapshot.schema_version,
                exporter_id=snapshot.exporter.id,
                exporter_version=snapshot.exporter.version,
                exported_at=snapshot.exported_at,
                world_id=snapshot.world.world_id,
                world_title=snapshot.world.title,
                core_version=snapshot.world.core_version,
                system_id=snapshot.world.system_id,
                system_version=snapshot.world.system_version,
                actor_count=len(snapshot.actors),
                selected_folder_ids=snapshot.selected_folder_ids,
                correlation_id=correlation_id,
                received_by_discord_user_id=received_by,
            )
        )

    def _create_unmapped(
        self,
        unit_of_work: UnitOfWork,
        snapshot: ParsedSnapshot,
        report: ReconciliationReport,
        *,
        snapshot_record: SnapshotRecord,
        correlation_id: UUID,
        capability: ActorCapability,
        actor_discord_user_id: int | None,
    ) -> int:
        actors = {str(actor.actor_id): actor for actor in snapshot.actors}
        created = 0
        for entry in report.entries:
            if entry.outcome is not ActorOutcome.UNMAPPED:
                continue
            actor = actors[entry.actor_id]
            view = SnapshotActorView(actor, self._profile)
            character = Character(
                id=self._character_ids(),
                display_name=actor.name,
                # Level, ownership and every other managed field stay unset:
                # this import establishes identity and a mapping, and a Council
                # correction sets the rest deliberately.
            )
            unit_of_work.characters.add(character)
            unit_of_work.external_actor_mappings.add(
                ExternalActorMapping(
                    character_id=character.id,
                    world_id=snapshot.world.world_id,
                    external_actor_id=entry.actor_id,
                    relink_fingerprint=relink_fingerprint(view, actor),
                    folder_id=entry.folder_id,
                    established_by_snapshot_id=snapshot_record.id,
                )
            )
            unit_of_work.audit.record(
                AuditEvent(
                    action="snapshot_import.character.created",
                    entity_type="character",
                    entity_id=str(character.id),
                    source=AuditSource.IMPORT,
                    actor_capability=capability,
                    actor_discord_user_id=actor_discord_user_id,
                    correlation_id=correlation_id,
                    payload={
                        "snapshot_checksum": snapshot.checksum.hex_digest,
                        "profile_version": self._profile.version,
                        "external_actor_id": entry.actor_id,
                        "folder_id": entry.folder_id,
                        "display_name": character.display_name,
                    },
                )
            )
            created += 1
        return created

    def _record_refusal(
        self,
        snapshot: ParsedSnapshot,
        preview: SnapshotPreview,
        *,
        refusal: ImportRefused,
        capability: ActorCapability,
        mode: ImportMode,
        supervisor: str | None,
        actor_discord_user_id: int | None,
        correlation_id: UUID,
        folder: str,
    ) -> None:
        report = refusal.report or preview.report
        try:
            with self._unit_of_work_factory() as unit_of_work:
                snapshot_record = self._store_snapshot(
                    unit_of_work,
                    snapshot,
                    correlation_id=correlation_id,
                    received_by=actor_discord_user_id,
                )
                unit_of_work.snapshot_imports.add(
                    SnapshotImportRecord(
                        snapshot_id=snapshot_record.id,
                        folder_id=folder,
                        folder_path=report.folder.path,
                        profile_version=self._profile.version,
                        # A refused attempt keeps its own request key distinct so
                        # the corrected retry is not mistaken for it.
                        request_key=f"{preview.binding.request_key}:refused:{correlation_id}",
                        status=ImportStatus.REFUSED,
                        mode=mode,
                        actor_capability=capability,
                        actor_discord_user_id=actor_discord_user_id,
                        supervisor=supervisor,
                        warning_count=report.warning_count,
                        summary={**report.summary(), "refusal_code": refusal.code},
                        correlation_id=correlation_id,
                    )
                )
                unit_of_work.audit.record(
                    AuditEvent(
                        action=IMPORT_REFUSED,
                        entity_type=SNAPSHOT_ENTITY,
                        entity_id=snapshot.checksum.hex_digest,
                        source=AuditSource.IMPORT,
                        actor_capability=capability,
                        actor_discord_user_id=actor_discord_user_id,
                        correlation_id=correlation_id,
                        payload={
                            "refusal_code": refusal.code,
                            # A safe category and counts. Never an exception
                            # traceback, and never artifact content.
                            "folder_id": folder,
                            "profile_version": self._profile.version,
                            "errors": report.error_count,
                            "warnings": report.warning_count,
                            "issue_codes": sorted(
                                {issue.code for issue in report.issues}
                            ),
                            "applied": False,
                        },
                    )
                )
                unit_of_work.commit()
        except Exception:  # pragma: no cover - the refusal itself must survive
            # Failing to record a refusal must not replace the refusal with a
            # different error. The original is re-raised by the caller.
            pass


def _default_folder(snapshot: ParsedSnapshot) -> str:
    """The only folder, when there is exactly one. Otherwise, choose one.

    A bundle may export up to eight folders and a Platform Administrator selects
    between them (export contract §2.5). Guessing which of several was meant is
    exactly the decision the contract moved into the Manager, so it is refused.
    """
    if len(snapshot.selected_folder_ids) == 1:
        return snapshot.selected_folder_ids[0]
    raise ImportRefused(
        "folder_selection_required",
        f"This snapshot exports {len(snapshot.selected_folder_ids)} folders. "
        "Select which one to import from; the Manager does not choose.",
    )
