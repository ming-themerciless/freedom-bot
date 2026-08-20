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

**A request key is bound to the operation it was spent on.** The key alone
identifies an attempt but says nothing about *what* was attempted, so on its
own it let a different artifact, folder, profile or exporter be presented under
an already-spent key and receive the original import's identity and correlation
ID beside the new checksum (finding B-1). Every apply records
`operation_digest` — the SHA-256 of the immutable bound inputs — and every
lookup compares it. Same key and same operation is a retry and returns the
original result; same key and anything else is a typed `request_key_conflict`
refusal, never a receipt.

**A retry returns the original result, not a fresh one that resembles it.** The
receipt for an operation that has already been applied is reconstructed from the
immutable row that operation wrote — its import id, correlation id, counts,
operation digest *and* its reconciliation facts, which
`snapshot_imports.summary` has always stored. It used to recompute the report
against the database as it stood at retry time and place that beside the
original's identifiers, so a receipt described two different instants: the
original said "one unmapped Actor, one create candidate" and the retry, moments
later, said "already mapped" (finding B-1R). Nothing in a retry's result is
computed now, and nothing in it is taken from the caller.

**The permanent audit record carries a digest of the request key, never the key.**
The key is caller-supplied text. It has to be stored verbatim in exactly one
place — `snapshot_imports.request_key`, which *is* the idempotency lookup — and
copying it a second time into an append-only audit payload made permanent,
searchable history an arbitrary text channel a caller could put a player name,
an address or a credential into (finding S-1). Audit rows carry
`request_key_digest` instead: a domain-separated, version-stable SHA-256 that
still groups every event of one attempt together and reveals no original text.

**A lost race is resolved by re-reading the winner, never by assuming.** The
adapter translates every uniqueness violation into `UniquenessConflict` naming a
rule, and anything else into `PersistenceError` (finding I-1). A conflict is
resolved in a *fresh* transaction: the winning row is read back, its operation
digest is checked against this attempt's, and only then is a typed duplicate
returned. If no winning row for this operation exists, the attempt is refused —
it is not reported as a duplicate of something nobody can name. A
`PersistenceError` is never resolved at all: an unexpected database failure must
not become a successful no-op.

**A refusal is recorded once, safely, after the rollback.** The state
transaction rolls back completely; then a separate transaction writes one
refused import row and one attempted/refused audit event under the same
correlation ID. It claims no partial state and carries no artifact content.
"""
from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.authorization import (
    AuthorizationContext,
    AuthorizationPort,
    SupervisedBootstrap,
)
from application.bootstrap import BootstrapGate
from application.errors import UniquenessConflict
from application.foundry.artifact import SnapshotArtifact
from application.foundry.audit_policy import (
    CHARACTER_CREATED,
    IMPORT_APPLIED,
    IMPORT_REFUSED,
    enforced,
)
from application.foundry.extraction import SnapshotActorView
from application.foundry.parser import BundleLimits, ParsedSnapshot, parse_snapshot
from application.foundry.reconciliation import (
    ActorOutcome,
    ComparableFieldReaders,
    ReconciliationFacts,
    ReconciliationFactsError,
    ReconciliationReport,
    ReconciliationSource,
    reconcile,
    relink_fingerprint,
)
from application.repositories import UnitOfWork
from application.snapshots import (
    REQUEST_KEY_MAX_LENGTH,
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
IMPORT_DUPLICATE = "snapshot_import.duplicate"

#: Every refusal code this service can raise. A closed vocabulary, because the
#: code is written into an append-only import record and quoted in an audit
#: payload: an operator filters on it, and a value nobody declared would be a
#: free-text field wearing a code's clothes. `tests/test_audit_payload_policy.py`
#: asserts that no refusal escapes with a code that is not here.
REFUSAL_CODES = frozenset(
    {
        "ambiguous_authority",
        "blocked",
        "bootstrap_requires_empty_dataset",
        "bootstrap_unavailable",
        "concurrent_import",
        "folder_selection_required",
        "invalid_request_key",
        "no_authority",
        "no_bootstrap_gate",
        "original_result_unavailable",
        "request_key_conflict",
        "stale_preview",
    }
)


class ImportRefused(RuntimeError):
    """The import was refused. Nothing was written by the attempt itself."""

    def __init__(self, code: str, message: str, *, report: ReconciliationReport | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.report = report


#: The bound inputs that identify the **operation** a request key was spent on.
#:
#: Everything here is immutable for a given operation: the same artifact, the
#: same folder in the same place, the same profile and the same exporter produce
#: the same digest today and on a retry tomorrow.
#:
#: Two `PreviewBinding` fields are deliberately absent.
#:
#: - `aggregate_versions` is *volatile by design*: a genuine retry runs against
#:   a database the first attempt already changed, so including it would make
#:   every retry look like a different operation and fail closed on the one case
#:   idempotency exists for.
#: - `request_key` is the lookup, not the operation. Digesting the key together
#:   with the operation would make every stored digest trivially match its own
#:   key and prove nothing.
#:
#: `test_snapshot_import_service.py` asserts this list against `PreviewBinding`'s
#: own fields, so a new bound input must be classified as one or the other
#: rather than silently ignored here.
OPERATION_FIELDS = (
    "snapshot_checksum",
    "world_id",
    "folder_id",
    "folder_path",
    "profile_version",
    "exporter",
)


def operation_digest(values: Mapping[str, str]) -> str:
    """The SHA-256 of one bound operation. The only place it is computed.

    Both the preview's binding and the apply's own recomputation go through
    here, so the two cannot drift into digesting different things — which would
    make every retry look like a reuse, or worse, the reverse.
    """
    missing = [name for name in OPERATION_FIELDS if name not in values]
    if missing:
        raise KeyError(
            f"An operation digest needs every bound input; missing {missing}."
        )
    return hashlib.sha256(
        "\n".join(f"{name}={values[name]}" for name in OPERATION_FIELDS).encode("utf-8")
    ).hexdigest()


#: The domain separator and version of the request-key digest construction.
#:
#: **Domain-separated** so a request-key digest can never coincide with an
#: operation digest, a snapshot checksum or any other SHA-256 this codebase
#: produces, even over identical text. Comparing two digests therefore compares
#: two request keys and nothing else.
#:
#: **Versioned** so the construction can change without the new digests silently
#: appearing to be the old ones. Changing this string is a decision with a
#: consequence: events written before and after it stop grouping together, which
#: is exactly the visible break a silent change would hide. It is not a secret
#: and does not have to be one — see `request_key_digest`.
REQUEST_KEY_DIGEST_DOMAIN = "freedom-blades/snapshot-import/request-key/v1"


def request_key_digest(request_key: str) -> str:
    """The permanent-history stand-in for a caller-supplied request key.

    Finding S-1: `request_key` accepts any printable text up to 255 characters
    and used to be copied verbatim into the `snapshot_import.applied` audit
    payload. Validating its length and characters stops it corrupting a rendered
    row; it does nothing about a caller putting a player's name, an email
    address or a credential into append-only history that Council and Platform
    Administrators can search. The key is *needed* verbatim in exactly one
    place — `snapshot_imports.request_key`, the column the idempotency lookup
    matches on — and nowhere else.

    So audit rows carry this instead. It is deterministic, so two events of the
    same attempt still group together; it is one-way, so the row no longer holds
    the text; and it is domain-separated and versioned, so it cannot be confused
    with another digest or silently redefined.

    **What it is not.** This is a data-minimisation control, not a secret. A
    digest of a short guessable key can be confirmed by anyone who can guess the
    key and run SHA-256, so it is not a defence against an attacker who already
    suspects a specific value — no unkeyed digest is. It is also never
    authorization: nothing in this service accepts a digest in place of a key.
    A keyed construction was considered and rejected here: it would put a secret
    into an application service, and rotating that secret would silently break
    the grouping this exists to provide.
    """
    return hashlib.sha256(
        f"{REQUEST_KEY_DIGEST_DOMAIN}\n{request_key}".encode("utf-8")
    ).hexdigest()


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

    def operation_digest(self) -> str:
        """The digest of the operation this binding's request key stands for.

        Narrower than `token()`: it covers the bound inputs that stay the same
        across a retry, and not the aggregate versions, which do not.
        """
        return operation_digest(
            {name: getattr(self, name) for name in OPERATION_FIELDS}
        )

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
    """The result of one applied import, as of the moment it committed.

    Every field except `duplicate` and `report` is a **durable fact of the
    import named by `import_id`**, and both of the paths that can produce an
    outcome build them from that import's own immutable row. A first apply reads
    them from the record it just wrote; a retry of the same key and the same
    bound operation reads them back from the record the first apply wrote. So
    `result_facts()` of the two is equal, which is the whole of finding B-1R.

    `report` is the one thing that is *not* a durable fact, and it is typed and
    named to say so. It is the full narrative reconciliation of the run that
    produced this result — per-Actor entries, comparisons and issue messages —
    and it exists only when *this attempt* is that run. A retry did not
    reconcile anything: it found the operation already applied and returned its
    record. Recomputing a report for it was the defect, because a report
    computed now describes the database now, while every other field of the
    receipt describes the instant the import committed. The reconciliation the
    result *does* carry, on both paths, is `reconciliation` — the bounded facts
    the import durably recorded.
    """

    status: ImportStatus
    #: The bounded reconciliation facts this import committed, read from its own
    #: immutable summary. Never recomputed, and never taken from a caller.
    reconciliation: ReconciliationFacts
    correlation_id: UUID
    snapshot_checksum: str
    #: The operation this result is the result *of*. Same key plus this digest
    #: is a retry; same key plus anything else never reaches an outcome.
    operation_digest: str
    import_id: UUID
    created_count: int = 0
    updated_count: int = 0
    warning_count: int = 0
    #: `True` when this exact operation had already been applied. A successful
    #: no-op, never a second mutation — and never a different result.
    duplicate: bool = False
    #: See the class docstring. Present for the attempt that reconciled and
    #: applied; absent for a retry, which reconciled nothing.
    report: ReconciliationReport | None = None

    @property
    def applied(self) -> bool:
        return self.status is ImportStatus.APPLIED and not self.duplicate

    def result_facts(self) -> dict[str, object]:
        """Everything this outcome asserts about the import it names.

        The comparison a retry has to satisfy: a first apply and a retry of the
        same operation return equal `result_facts()`, whatever has happened to
        the database in between. `duplicate` is excluded because it describes
        *this attempt* rather than the import, and `report` because it is the
        narrative of a run rather than a fact the import recorded.
        """
        return {
            "import_id": self.import_id,
            "correlation_id": self.correlation_id,
            "status": self.status,
            "snapshot_checksum": self.snapshot_checksum,
            "operation_digest": self.operation_digest,
            "created_count": self.created_count,
            "updated_count": self.updated_count,
            "warning_count": self.warning_count,
            "reconciliation": self.reconciliation.summary(),
        }


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
        readers: ComparableFieldReaders | None = None,
    ) -> None:
        # Before anything else, and outside any transaction: a service composed
        # with a profile whose comparable fields it cannot read refuses to
        # exist. `ComparableFieldReaders` raises here, at startup, rather than
        # part-way through a run an operator has already confirmed.
        self._readers = readers or ComparableFieldReaders.default(profile)
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
        _require_valid_request_key(request_key)
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
        actor_account_id: UUID | None = None,
        bootstrap: SupervisedBootstrap | None = None,
        folder_id: str | None = None,
        commit_fence=None,
    ) -> ImportOutcome:
        """Re-check everything, then commit in one transaction — or refuse.

        `actor_account_id` is the stable platform account the import is recorded
        under (ADR 0010 D1, schema §11). **Added by P3.3, keyword-only and
        defaulting to `None`**, so the Phase 2 operator path and the supervised
        bootstrap are unchanged and unaffected — neither has an account, and the
        first predates them entirely.

        It is recorded, never trusted. The *authority* for the apply is still
        resolved through the `AuthorizationPort` from `discord_user_id`, at the
        moment of the commit, exactly as before; this only decides which column
        the resulting row's attribution is written to. Passing an account here
        confers nothing.

        `folder_id` is the folder that is selected *now* — in Phase 3, whatever
        the Platform Administrator has configured at the moment of the apply.
        Passing it is how an administrator's folder change between preview and
        apply becomes a stale preview instead of a silent import from a folder
        nobody confirmed. Omitting it means "the preview's folder is still the
        selected one".

        `commit_fence` is an optional `application.worker.fence.CommitFence`
        (added by the 2026-08-18 P3.3 remediation). When one is given, its
        `hold()` runs as the **last statement of the same transaction that
        commits the effect**, and a fence that refuses aborts that transaction
        with nothing written. It is how a caller whose entitlement to commit can
        be revoked concurrently — a worker holding a job lease that may be
        cancelled, abandoned or reaped — proves at the commit boundary that it
        still holds it.

        It defaults to `None` and the parameter is keyword-only, so Phase 2's
        operator path and the supervised bootstrap are unchanged: neither has a
        lease that anything can revoke, so neither has anything to prove.
        """
        context, capability, mode, supervisor = self._resolve_authority(
            discord_user_id=discord_user_id, bootstrap=bootstrap
        )
        correlation_id = self._correlation_ids()
        # Re-checked at apply and not only at preview: the binding is an object
        # the caller holds, and a refusal that could not be recorded because its
        # own key was unwritable would lose the record of the attempt.
        _require_valid_request_key(preview.binding.request_key)
        snapshot = self.parse(artifact)
        folder = preview.binding.folder_id
        # Computed from the artifact in hand and the folder being applied to —
        # never read off the preview, which is the object whose trustworthiness
        # is in question. This is what a stored request key is checked against.
        digest = self._operation_digest(snapshot, folder)
        try:
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
                    actor_account_id=actor_account_id,
                    correlation_id=correlation_id,
                    folder=folder,
                    digest=digest,
                    commit_fence=commit_fence,
                )
            except UniquenessConflict as conflict:
                # Another transaction claimed an identity this one needed. The
                # adapter has already rolled this one back, so there is nothing
                # partial to undo; what remains is to find out *who won* and say
                # so truthfully. Never assumed from the rule name alone: a rule
                # says which identity collided, not whether the winner was this
                # same operation.
                return self._resolve_conflict(
                    snapshot,
                    preview,
                    conflict=conflict,
                    folder=folder,
                    digest=digest,
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
                actor_account_id=actor_account_id,
                correlation_id=correlation_id,
                folder=folder,
                digest=digest,
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
        actor_account_id: UUID | None,
        correlation_id: UUID,
        folder: str,
        digest: str,
        commit_fence=None,
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
                self._require_same_operation(
                    existing, unit_of_work, snapshot, folder, digest, preview
                )
                # A retry of the *same operation*. The original result, not a
                # second application of it and not a fresh one that resembles it.
                return self._duplicate_of(existing, unit_of_work)

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
                # The same input under a different key. The winner's own result,
                # for the same reason a retry gets the original one: this run's
                # report describes a database the winner has already changed.
                return self._duplicate_of(already, unit_of_work)

            created = self._create_unmapped(
                unit_of_work,
                snapshot,
                report,
                snapshot_record=snapshot_record,
                correlation_id=correlation_id,
                capability=capability,
                actor_discord_user_id=actor_discord_user_id,
            )
            # Computed once, stored on the record and returned in the outcome, so
            # what a retry reads back is what this apply returned rather than a
            # second rendering of it.
            facts = report.facts()
            record = SnapshotImportRecord(
                snapshot_id=snapshot_record.id,
                folder_id=folder,
                folder_path=report.folder.path,
                profile_version=self._profile.version,
                request_key=preview.binding.request_key,
                operation_digest=digest,
                status=ImportStatus.APPLIED,
                mode=mode,
                actor_capability=capability,
                actor_discord_user_id=actor_discord_user_id,
                actor_account_id=actor_account_id,
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
                    payload=enforced(
                        IMPORT_APPLIED,
                        {
                            **report.summary(),
                            "mode": mode.value,
                            "supervisor": supervisor,
                            # The digest, never the key (S-1). The key itself is
                            # written exactly once, to the lookup column above.
                            "request_key_digest": request_key_digest(
                                preview.binding.request_key
                            ),
                            # The operation identity, so an event can be traced
                            # to what was applied and not only to who and when.
                            "operation_digest": digest,
                            "preview_token": preview.binding.token(),
                            "characters_created": created,
                        },
                    ),
                )
            )
            if commit_fence is not None:
                # **The last statement before the commit, and deliberately so.**
                # Everything above is already pending in this session; issuing a
                # statement here flushes it and then takes the fence's own row
                # lock, which is therefore held for the commit alone rather than
                # for the whole apply. A fence that refuses raises `FenceLost`,
                # the `with` block rolls the session back, and not one character,
                # mapping, import row or audit event survives.
                commit_fence.hold(unit_of_work)
            # State, mappings, reconciliation effects, correction transactions
            # and the success audit commit together. An audit failure takes the
            # state with it, because there is one transaction and this is it.
            unit_of_work.commit()

        return ImportOutcome(
            status=ImportStatus.APPLIED,
            reconciliation=facts,
            correlation_id=correlation_id,
            snapshot_checksum=snapshot.checksum.hex_digest,
            operation_digest=digest,
            import_id=record.id,
            created_count=created,
            updated_count=0,
            warning_count=report.warning_count,
            report=report,
        )

    # -- request-key binding (B-1) --------------------------------------------

    def _operation_digest(self, snapshot: ParsedSnapshot, folder: str) -> str:
        """The digest of the operation being attempted, from first principles.

        Built from the parsed artifact and the folder actually being applied to,
        so it is a statement about the inputs in hand rather than about anything
        the caller asserted. `_bind` produces the same digest for the same
        operation, and a test holds the two to it.
        """
        return operation_digest(
            {
                "snapshot_checksum": snapshot.checksum.hex_digest,
                "world_id": snapshot.world.world_id,
                "folder_id": folder,
                "folder_path": snapshot.folder_identity(folder).path,
                "profile_version": self._profile.version,
                "exporter": snapshot.exporter.describe(),
            }
        )

    def _require_same_operation(
        self,
        existing: SnapshotImportRecord,
        unit_of_work: UnitOfWork,
        snapshot: ParsedSnapshot,
        folder: str,
        digest: str,
        preview: SnapshotPreview,
    ) -> None:
        """Refuse a request key that was spent on a different operation.

        This is the whole of finding B-1. Returning the earlier record on the
        key alone produced a receipt that mixed the first operation's import id
        and correlation id with the second's checksum and report — a document
        describing no single event, written to an append-only table.

        The refusal names *which* bound inputs differ and none of their values:
        which folder or which artifact is enough to find the mistake, and the
        values are the caller's own inputs rather than anything worth echoing
        back into a refusal record.

        It does not quote the request key either (S-1). The caller supplied it
        and already has it, and a message is the one part of a refusal that gets
        pasted into a ticket, a chat channel or a log — none of which is a place
        for text a caller may have put a name or a credential into.
        """
        if existing.operation_digest == digest:
            return
        raise ImportRefused(
            "request_key_conflict",
            "This request key was already used for a different import: "
            + (
                ", ".join(
                    self._conflicting_inputs(existing, unit_of_work, snapshot, folder)
                )
                or "a bound input"
            )
            + " does not match. Nothing was applied and no result was returned "
            "for the earlier import. A request key identifies one operation; "
            "use a new key for a new one.",
            report=preview.report,
        )

    def _conflicting_inputs(
        self,
        existing: SnapshotImportRecord,
        unit_of_work: UnitOfWork,
        snapshot: ParsedSnapshot,
        folder: str,
    ) -> tuple[str, ...]:
        """Which bound inputs differ, named and never quoted.

        Only four axes are independent: the world and the exporter cannot differ
        without the checksum differing too, because they are content of the
        artifact the checksum covers.
        """
        stored_snapshot = unit_of_work.snapshots.get_by_checksum(
            snapshot.checksum.hex_digest
        )
        differences = []
        if stored_snapshot is None or stored_snapshot.id != existing.snapshot_id:
            differences.append("the snapshot artifact")
        if existing.folder_id != folder:
            differences.append("the selected folder")
        if existing.folder_path != snapshot.folder_identity(folder).path:
            differences.append("the selected folder's path")
        if existing.profile_version != self._profile.version:
            differences.append("the field-profile version")
        return tuple(differences)

    def _duplicate_of(
        self, record: SnapshotImportRecord, unit_of_work: UnitOfWork
    ) -> ImportOutcome:
        """The original result of an operation that has already been applied.

        This is finding B-1R. Every field comes from `record` — the immutable
        row the original apply committed — and **nothing** is computed against
        the database as it stands or read off the caller's preview. There is no
        report parameter to pass one in through, which is what makes "the caller
        cannot supply the original result" a property of the signature rather
        than a rule somebody has to remember.

        What that costs is the narrative report, which is not durable and is
        deliberately not going to be: its entries and messages quote Actor
        names and field values, which the audit-content ruling keeps out of
        append-only history. The reconciliation this returns is the bounded
        facts the import itself recorded — which is what the original result
        *was*, as far as anything permanent is concerned.
        """
        facts = self._original_facts(record)
        unit_of_work.rollback()
        return ImportOutcome(
            status=record.status,
            reconciliation=facts,
            correlation_id=record.correlation_id,
            snapshot_checksum=facts.snapshot_checksum,
            operation_digest=record.operation_digest,
            import_id=record.id,
            created_count=record.created_count,
            updated_count=record.updated_count,
            warning_count=record.warning_count,
            duplicate=True,
            report=None,
        )

    def _original_facts(self, record: SnapshotImportRecord) -> ReconciliationFacts:
        """Read an applied import's own reconciliation facts back, or refuse.

        Validated rather than cast: `summary` is a `jsonb` column, and turning
        whatever it holds into a typed result would mean a receipt whose
        "original facts" were whatever happened to be in the row. Both failures
        below fail **closed** — a retry that cannot be answered with the
        original operation's facts is refused, never answered with invented or
        freshly computed ones. Neither refusal writes durable state, so the
        first import stands and an operator can still read the row.
        """
        if record.status is not ImportStatus.APPLIED:
            raise ImportRefused(
                "original_result_unavailable",
                "The import this request key names was not applied, so there is "
                "no original result to return for it. Nothing was applied by "
                "this attempt. Use a new request key for a new attempt.",
            )
        try:
            return ReconciliationFacts.from_summary(record.summary)
        except ReconciliationFactsError as unreadable:
            raise ImportRefused(
                "original_result_unavailable",
                "This operation has already been applied, but its recorded "
                f"reconciliation cannot be read back: {unreadable} Nothing was "
                "applied by this attempt and nothing was invented in place of "
                "the original result. The applied import "
                f"{record.id} remains valid; read its row directly.",
            ) from None

    # -- lost races (I-1) -----------------------------------------------------

    def _resolve_conflict(
        self,
        snapshot: ParsedSnapshot,
        preview: SnapshotPreview,
        *,
        conflict: UniquenessConflict,
        folder: str,
        digest: str,
    ) -> ImportOutcome:
        """Read the winning row back, then say what actually happened.

        A fresh unit of work, because the losing transaction is gone. Three
        outcomes, and the order matters:

        1. this operation's request key is already recorded — provided its
           operation digest matches, that is a duplicate of *this* operation;
        2. this operation's input is already applied under some other key — also
           a duplicate;
        3. neither — something else collided, and the honest answer is a
           refusal. It is *not* reported as a duplicate: there is no winning row
           describing this operation, so a duplicate receipt would name an
           import that does not exist.
        """
        with self._unit_of_work_factory() as unit_of_work:
            existing = unit_of_work.snapshot_imports.find_by_request_key(
                preview.binding.request_key
            )
            if existing is not None:
                # A concurrent attempt may have claimed this key for something
                # else entirely; the same check as the sequential path applies.
                self._require_same_operation(
                    existing, unit_of_work, snapshot, folder, digest, preview
                )
                return self._duplicate_of(existing, unit_of_work)

            stored = unit_of_work.snapshots.get_by_checksum(
                snapshot.checksum.hex_digest
            )
            already = (
                unit_of_work.snapshot_imports.find_applied(
                    stored.id, folder, self._profile.version
                )
                if stored is not None
                else None
            )
            if already is not None:
                return self._duplicate_of(already, unit_of_work)
            unit_of_work.rollback()

        raise ImportRefused(
            "concurrent_import",
            "Another import committed first and claimed something this one "
            f"needed ({conflict.rule}). Nothing was applied by this attempt, "
            "and no part of it was written. Produce a new preview against the "
            "current database and confirm it.",
            report=preview.report,
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
            snapshot,
            folder_id=folder,
            profile=self._profile,
            source=source,
            readers=self._readers,
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
                    action=CHARACTER_CREATED,
                    entity_type="character",
                    entity_id=str(character.id),
                    source=AuditSource.IMPORT,
                    actor_capability=capability,
                    actor_discord_user_id=actor_discord_user_id,
                    correlation_id=correlation_id,
                    payload=enforced(
                        CHARACTER_CREATED,
                        {
                            "snapshot_checksum": snapshot.checksum.hex_digest,
                            "profile_version": self._profile.version,
                            "external_actor_id": entry.actor_id,
                            "folder_id": entry.folder_id,
                            # `display_name` was here and has been removed
                            # (I-2). `entity_id` is the character's stable UUID
                            # and the three keys above are its provenance; the
                            # Actor's name is mutable game-visible data that
                            # goes stale (B-2), not identity evidence.
                        },
                    ),
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
        actor_account_id: UUID | None,
        correlation_id: UUID,
        folder: str,
        digest: str,
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
                        request_key=_refused_key(
                            preview.binding.request_key, correlation_id
                        ),
                        # The operation that was *attempted*. A refused row
                        # never satisfies an idempotency lookup — its key is
                        # deliberately not the caller's — but recording what was
                        # attempted is what makes the refusal auditable.
                        operation_digest=digest,
                        status=ImportStatus.REFUSED,
                        mode=mode,
                        actor_capability=capability,
                        actor_discord_user_id=actor_discord_user_id,
                        actor_account_id=actor_account_id,
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
                        payload=enforced(
                            IMPORT_REFUSED,
                            {
                                "refusal_code": refusal.code,
                                # A safe category and counts. Never an exception
                                # traceback, never artifact content, and never
                                # the refusal's own message — which names the
                                # inputs that differed and is for the operator
                                # in the moment, not for permanent history.
                                "folder_id": folder,
                                "profile_version": self._profile.version,
                                "errors": report.error_count,
                                "warnings": report.warning_count,
                                "issue_codes": sorted(
                                    {issue.code for issue in report.issues}
                                ),
                                "applied": False,
                            },
                        ),
                    )
                )
                unit_of_work.commit()
        except Exception:  # pragma: no cover - the refusal itself must survive
            # Failing to record a refusal must not replace the refusal with a
            # different error. The original is re-raised by the caller.
            pass


def _require_valid_request_key(request_key: str) -> None:
    """A request key is a bounded, printable token, refused where it arrives.

    It is caller-supplied and is written verbatim into the one column that has
    to hold it, so it is validated as input rather than trusted as an opaque
    handle. Refused here, before any parsing or reading, so the caller gets a
    typed refusal instead of a persistence error much later.

    This validation is deliberately **not** the data-minimisation control. A key
    can be perfectly printable and 40 characters long and still be somebody's
    email address, which is why permanent audit history records
    `request_key_digest` rather than the key (S-1).
    """
    if not request_key or not request_key.strip():
        raise ImportRefused(
            "invalid_request_key",
            "An import needs a request key: it is what makes a retry return the "
            "original result instead of applying twice.",
        )
    if len(request_key) > REQUEST_KEY_MAX_LENGTH:
        raise ImportRefused(
            "invalid_request_key",
            f"A request key may be at most {REQUEST_KEY_MAX_LENGTH} characters; "
            f"this one is {len(request_key)}. Nothing was applied.",
        )
    if any(character < " " or character == "\x7f" for character in request_key):
        raise ImportRefused(
            "invalid_request_key",
            "A request key must be printable text. It is recorded verbatim in "
            "the idempotency lookup column, so a control character in it would "
            "corrupt every later rendering of that row. Nothing was applied.",
        )


def _refused_key(request_key: str, correlation_id: UUID) -> str:
    """The key a refused attempt is recorded under: a digest, never the text.

    Two jobs, and neither of them needs the original characters.

    It must be **distinct from the caller's key**, so a refused row never
    satisfies an idempotency lookup and the corrected retry is not answered with
    the refusal. It must be **distinct between two refusals of the same key**, so
    recording the second is not itself a uniqueness violation; the correlation
    id supplies that.

    It used to be the caller's key truncated to fit, plus a suffix. That was a
    second verbatim copy of caller-supplied text in an append-only table, in a
    row that nothing ever looks up by key — the only copy S-1 leaves standing is
    the one the lookup actually needs (S-1). The digest is fixed-width, so the
    column bound is satisfied by construction rather than by truncation.
    """
    return f"refused:{request_key_digest(request_key)}:{correlation_id}"


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
