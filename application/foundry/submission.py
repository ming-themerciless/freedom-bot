"""Accept an immutable snapshot artifact from the Foundry module.

A submission is deliberately the *smallest* thing that can be useful: it proves
the bytes are a valid bundle for the supported deployment, stores them, and
records that they exist. It changes no character, creates no mapping, resolves
no identity and applies no import.

**Submission is not import, and the separation is the point.** The Foundry
module holds a submit-only credential and no game-policy authority whatsoever
(ADR 0006: "no administrator credential and no database secret is ever shipped
in a Foundry module"). What arrives is a *pending* artifact. A currently
authorized Guild Council member later previews it and, separately again,
confirms an apply through `SnapshotImportService`, which re-checks every bound
input at the moment it commits. Nothing here shortens that chain.

**The server does not believe the client about anything.** The module computes
a checksum and sends it; the server computes its own over the bytes it actually
received and refuses a mismatch. The module counts Actors and names a folder;
the server takes both from its own parse of the bundle. A filename, a declared
length and a client-supplied folder path are not inputs to any decision here —
the only thing taken from the request besides the bytes is the request key, and
that is an idempotency lookup rather than an assertion about the world.

**One artifact identity, however many times it arrives.** Bytes are stored under
their own SHA-256, and `foundry_snapshots.checksum` is unique. The same export
submitted twice under two keys yields one file, one snapshot row and two
receipts naming it — never a second raw copy, and never a second identity.

**A retry returns the original receipt rather than a new one that resembles it.**
The receipt is stored in `idempotency_keys.response` when the submission
commits, and a retry reads it back. Recomputing one would describe the system as
it is now while every identifier in it claimed to describe the moment of
submission.

**Refusals are recorded once, safely, and only after authentication.** An
unauthenticated request writes nothing at all: append-only history is not a
place to let an anonymous caller append rows. Once a principal is established, a
refusal writes one refused audit event carrying a code, the principal and a
digest of the request key — never the artifact, never a path, never an Actor.
"""
from __future__ import annotations

import hashlib
import hmac
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Mapping
from uuid import UUID, uuid4

from application.admissions import AdmissionState, SubmissionAdmission
from application.artifacts import ArtifactStorageError, ArtifactStore
from application.audit import ActorCapability, AuditEvent, AuditSource
from application.errors import UniquenessConflict
from application.foundry.artifact import (
    IngestionLimits,
    SnapshotArtifact,
    SnapshotRejected,
    ingest_bytes,
)
from application.foundry.audit_policy import (
    SUBMISSION_ACCEPTED,
    SUBMISSION_REFUSED,
    enforced,
)
from application.foundry.parser import BundleLimits, ParsedSnapshot, parse_snapshot
from application.idempotency import (
    IdempotencyKeyError,
    IdempotencyRecord,
    IdempotencyStatus,
    request_hash,
    validate_key,
)
from application.repositories import UnitOfWork
from application.service_principals import ServicePrincipal, ServicePrincipalScope
from application.snapshots import SnapshotRecord, SnapshotSource
from domain.foundry import SupportedDeployment

SNAPSHOT_ENTITY = "foundry_snapshot"

#: The idempotency namespace. Keys are unique *within* a scope, so a request key
#: spent on a submission cannot be confused with one spent on an import.
SUBMISSION_SCOPE = "foundry.snapshot.submission"

#: A submitted artifact has been recorded and validated. It has not been
#: applied, and this is the only status a submission can produce.
PENDING = "pending"

ACTION = "Submitting a Foundry snapshot"

#: Domain separator and version for the submission request-key digest.
#:
#: Distinct from the import service's separator so that the two digests of one
#: literal string differ: a submission key and an import key are different
#: things spent on different operations, and an audit reader must not be able to
#: link them by accident. Versioned so the construction can change without new
#: digests silently appearing to be old ones. It is not a secret, and — as the
#: import service's equivalent already records — an unkeyed digest of a short
#: guessable key can be confirmed by anyone who guesses the key. It is data
#: minimisation, never authorization.
REQUEST_KEY_DIGEST_DOMAIN = "freedom-blades/snapshot-submission/request-key/v1"


def request_key_digest(request_key: str) -> str:
    """The permanent-history stand-in for a caller-supplied request key."""
    return hashlib.sha256(
        f"{REQUEST_KEY_DIGEST_DOMAIN}\n{request_key}".encode("utf-8")
    ).hexdigest()


#: Every refusal this service can raise. Closed, because the code is written into
#: an append-only audit payload and an operator filters on it; a value nobody
#: declared would be a free-text field wearing a code's clothes.
REFUSAL_CODES = frozenset(
    {
        #: The bytes are not an acceptable bundle. `artifact_code` says why.
        "artifact_rejected",
        #: The client's claimed digest is not the digest of what arrived.
        "checksum_mismatch",
        #: Another submission holds this key and was spent on other bytes.
        "request_key_conflict",
        #: The key is unusable — blank, over-long or not printable.
        "invalid_request_key",
        #: A race was lost and its winner could not be identified. Never
        #: resolved into a duplicate: an unresolvable conflict is not a receipt.
        "concurrent_submission",
        #: The stored receipt for an already-spent key could not be read back.
        "original_result_unavailable",
        #: The artifact store could not confirm the write. Nothing was
        #: recorded — which is not the same as nothing having been written, and
        #: the message says only the former (review finding I-1).
        "storage_unavailable",
        #: This credential's admission generation is closed, or it never had
        #: one. Nothing was recorded and nothing may be. **Not retryable**, and
        #: deliberately not spelled as a conflict or an outage: repeating the
        #: request under the same credential can never succeed, whatever the
        #: caller waits for. See `application/admissions.py`.
        "admission_closed",
    }
)

#: Every code `artifact.py` and `parser.py` can refuse with, carried as
#: `artifact_code` beside the `artifact_rejected` refusal so an operator is told
#: what to fix rather than "submission failed".
#:
#: Enumerated here rather than derived, so that adding a refusal to the parser is
#: a decision about what may enter append-only history.
#: `tests/test_snapshot_submission.py` walks both modules' syntax trees and
#: asserts this set is exactly theirs, so a new code cannot slip in unclassified.
ARTIFACT_REFUSAL_CODES = frozenset(
    {
        "actor_outside_selection",
        "artifact_too_large",
        "artifact_unreadable",
        "binary_artifact",
        "byte_order_mark",
        "checksum_mismatch",
        "duplicate_actor_id",
        "duplicate_folder_id",
        "duplicate_selected_folder",
        "empty_artifact",
        "empty_selection",
        "excessive_nesting",
        "folder_cycle",
        "folder_not_selected",
        "invalid_encoding",
        "malformed_actor",
        "malformed_actor_id",
        "malformed_actors",
        "malformed_exporter",
        "malformed_folder_id",
        "malformed_folders",
        "malformed_json",
        "malformed_selection",
        "malformed_timestamp",
        "malformed_world",
        "missing_actor_id",
        "missing_top_level_key",
        "nfc_key_collision",
        "non_finite_number",
        "too_many_actors",
        "too_many_folders",
        "too_many_items",
        "too_many_selected_folders",
        "unexpected_top_level",
        "unknown_actor_key",
        "unknown_folder",
        "unknown_parent_folder",
        "unknown_selected_folder",
        "unknown_top_level_key",
        "unsafe_artifact_name",
        "unsupported_container",
        "unsupported_deployment",
        "unsupported_schema",
        "unsupported_schema_version",
    }
)


class SubmissionRefused(RuntimeError):
    """This attempt recorded nothing and confirmed nothing.

    Deliberately **not** "nothing was stored" (review finding I-1). The artifact
    is written before the transaction commits, so several refusal paths here run
    *after* `_store_and_record` has already put bytes on disk, and none of them
    can establish that the filesystem is unchanged:

    - `storage_unavailable` raised from `durability_unconfirmed` leaves a
      correct content-addressed file whose directory entry was not acknowledged;
    - `concurrent_submission` — from either the unresolvable-conflict branch or
      the unreadable-winner branch — is raised after the store has run;
    - `request_key_conflict` and `original_result_unavailable` are raised from
      `_replay`, which `_fenced_replay` reaches both for a key that was already
      spent before the store ran and for a race resolved by re-reading after it
      did, so neither may assert anything about bytes.

    Such a file is harmless, is re-used by the retry, and is found by the
    operator procedure in `docs/operations/foundry-snapshot-submission.md` §5.6.
    What every one of these paths *does* establish is the two facts a caller can
    act on: this attempt recorded nothing, and retrying with the same request key
    is safe because a retry cannot create a second snapshot.

    Messages here say only that. A path that genuinely ran before any storage —
    a rejected bundle, an unusable key, a mismatched claimed digest — may say so
    narrowly and specifically, but must not reach for a broad phrase merely
    because it happens to be true in one branch.
    """

    def __init__(
        self,
        code: str,
        message: str,
        *,
        artifact_code: str | None = None,
        checksum: str | None = None,
        admission_generation: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.artifact_code = artifact_code
        self.checksum = checksum
        #: The generation the credential holds, when it holds one. Recorded so
        #: an operator reading refusal history can see *which* fence turned a
        #: submission away; absent when the credential has no admission at all.
        self.admission_generation = admission_generation


class SubmissionReceiptError(ValueError):
    """A stored receipt could not be read back as one."""


class _RequestKeyAlreadySpent(Exception):
    """This key already earned a receipt, so this transaction has nothing to do.

    A control-flow signal, private to this module and never raised past
    `_persist`. It exists so that `_store_and_record` — whose job is to make a
    submission durable — cannot also be the thing that hands back somebody
    else's stored receipt. Both ways of discovering that a key is spent (finding
    the row before the store runs, and losing the `idempotency_key.scope_key`
    race after it) leave through here and arrive at one place:
    `SnapshotSubmissionService._fenced_replay`.

    That is the whole shape of review finding C-24-R1. A `SubmissionReceipt` read
    from storage is only safe to return while the presenting credential's
    admission is still open, and an invariant that each returning branch has to
    remember for itself is one a new branch will forget.
    """


@dataclass(frozen=True, slots=True)
class SubmittedFolder:
    """One exported folder, as the server itself parsed it."""

    folder_id: str
    path: str
    actors: int


@dataclass(frozen=True, slots=True)
class SubmissionReceipt:
    """What one submission durably recorded.

    Bounded on purpose. Everything here is a platform-generated identifier, a
    count, or Foundry *deployment structure* — a folder id and its displayed
    path. No Actor name, no Actor mechanic, no item, no embedded document and no
    part of the artifact appears in it, because this value is returned over the
    wire to a Foundry client, stored in `idempotency_keys.response`, and
    rendered in an operator receipt.
    """

    snapshot_id: UUID
    checksum: str
    size_bytes: int
    actor_count: int
    world_id: str
    exporter: str
    folders: tuple[SubmittedFolder, ...]
    canonical_encoding: bool
    correlation_id: UUID
    #: `True` when these exact bytes, or this exact request key, had already been
    #: submitted. A successful no-op, never a second artifact.
    duplicate: bool = False

    @property
    def status(self) -> str:
        return PENDING

    def as_payload(self) -> dict[str, Any]:
        """The JSON form: the wire receipt and the stored idempotency response."""
        return {
            "status": PENDING,
            "snapshot_id": str(self.snapshot_id),
            "checksum": self.checksum,
            "size_bytes": self.size_bytes,
            "actor_count": self.actor_count,
            "world_id": self.world_id,
            "exporter": self.exporter,
            "canonical_encoding": self.canonical_encoding,
            "correlation_id": str(self.correlation_id),
            "duplicate": self.duplicate,
            "folders": [
                {
                    "folder_id": folder.folder_id,
                    "path": folder.path,
                    "actors": folder.actors,
                }
                for folder in self.folders
            ],
        }

    @classmethod
    def from_payload(cls, payload: object) -> SubmissionReceipt:
        """Rebuild a receipt from what was stored, or refuse to invent one.

        Exact keys and exact types, and no defaulting anywhere. A stored receipt
        that cannot be read back is an `original_result_unavailable` refusal; it
        is never patched up, because a patched-up receipt asserts facts about a
        submission that nobody recorded.
        """
        if not isinstance(payload, Mapping):
            raise SubmissionReceiptError("The stored receipt is not an object.")
        expected = {
            "status",
            "snapshot_id",
            "checksum",
            "size_bytes",
            "actor_count",
            "world_id",
            "exporter",
            "canonical_encoding",
            "correlation_id",
            "duplicate",
            "folders",
        }
        if set(payload) != expected:
            raise SubmissionReceiptError(
                "The stored receipt does not carry exactly the recorded keys."
            )
        if payload["status"] != PENDING:
            raise SubmissionReceiptError("The stored receipt has an unknown status.")
        folders_raw = payload["folders"]
        if not isinstance(folders_raw, list):
            raise SubmissionReceiptError("The stored receipt's folders are not a list.")
        folders: list[SubmittedFolder] = []
        for entry in folders_raw:
            if not isinstance(entry, Mapping) or set(entry) != {
                "folder_id",
                "path",
                "actors",
            }:
                raise SubmissionReceiptError(
                    "A stored receipt folder does not carry exactly the recorded "
                    "keys."
                )
            folders.append(
                SubmittedFolder(
                    folder_id=_text(entry["folder_id"]),
                    path=_text(entry["path"]),
                    actors=_count(entry["actors"]),
                )
            )
        try:
            snapshot_id = UUID(_text(payload["snapshot_id"]))
            correlation_id = UUID(_text(payload["correlation_id"]))
        except ValueError as error:
            raise SubmissionReceiptError(
                "The stored receipt carries an identifier that is not a UUID."
            ) from error
        return cls(
            snapshot_id=snapshot_id,
            checksum=_text(payload["checksum"]),
            size_bytes=_count(payload["size_bytes"]),
            actor_count=_count(payload["actor_count"]),
            world_id=_text(payload["world_id"]),
            exporter=_text(payload["exporter"]),
            folders=tuple(folders),
            canonical_encoding=_flag(payload["canonical_encoding"]),
            correlation_id=correlation_id,
            duplicate=_flag(payload["duplicate"]),
        )


def _text(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise SubmissionReceiptError("The stored receipt holds a malformed string.")
    return value


def _count(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SubmissionReceiptError("The stored receipt holds a malformed count.")
    return value


def _flag(value: object) -> bool:
    if not isinstance(value, bool):
        raise SubmissionReceiptError("The stored receipt holds a malformed flag.")
    return value


class SnapshotSubmissionService:
    """Validate, store and record one submitted artifact. Nothing more."""

    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        *,
        deployment: SupportedDeployment,
        artifacts: ArtifactStore,
        ingestion_limits: IngestionLimits | None = None,
        bundle_limits: BundleLimits | None = None,
        correlation_ids: Callable[[], UUID] = uuid4,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._deployment = deployment
        self._artifacts = artifacts
        self._ingestion_limits = ingestion_limits or IngestionLimits()
        self._bundle_limits = bundle_limits
        self._correlation_ids = correlation_ids

    @property
    def max_bytes(self) -> int:
        """The artifact ceiling, so an adapter can bound its read to match."""
        return self._ingestion_limits.max_bytes

    def submit(
        self,
        data: bytes,
        *,
        principal: ServicePrincipal,
        request_key: str,
        claimed_checksum: str | None = None,
    ) -> SubmissionReceipt:
        """Accept `data` as a pending snapshot, or refuse it.

        `claimed_checksum` is the digest the client says it computed. It is
        never used *as* the identity — the identity is always the server's own
        digest of the bytes it received — but disagreeing with it is worth
        refusing over, because it means the two ends do not hold the same
        document and every later comparison would be against the wrong one.
        """
        principal.require(ServicePrincipalScope.SUBMIT_SNAPSHOT, ACTION)
        correlation_id = self._correlation_ids()
        key_digest = request_key_digest(request_key)
        try:
            return self._submit(
                data,
                principal=principal,
                request_key=request_key,
                key_digest=key_digest,
                claimed_checksum=claimed_checksum,
                correlation_id=correlation_id,
            )
        except SubmissionRefused as refusal:
            self._record_refusal(
                refusal,
                principal=principal,
                key_digest=key_digest,
                correlation_id=correlation_id,
            )
            raise

    # -- validation -----------------------------------------------------------

    def _submit(
        self,
        data: bytes,
        *,
        principal: ServicePrincipal,
        request_key: str,
        key_digest: str,
        claimed_checksum: str | None,
        correlation_id: UUID,
    ) -> SubmissionReceipt:
        try:
            validate_key(request_key)
        except IdempotencyKeyError as error:
            raise SubmissionRefused(error.code, str(error)) from None

        # No `source_name`: a submission has no filename, and inventing one from
        # the request would be accepting caller-controlled text into a path.
        try:
            artifact = ingest_bytes(data, limits=self._ingestion_limits)
        except SnapshotRejected as rejection:
            raise _artifact_refusal(rejection) from None

        if claimed_checksum is not None and not hmac.compare_digest(
            claimed_checksum.lower(), artifact.checksum.hex_digest
        ):
            # Constant-time, though nothing secret is being compared: it costs
            # nothing and removes the question of whether it should have been.
            raise SubmissionRefused(
                "checksum_mismatch",
                # Reached before `_persist`, so this one may say specifically
                # that the artifact store was never called — which is the useful
                # fact here, because it tells the client the transfer is what to
                # repeat. It says that rather than the broad phrase the other
                # refusals may not use.
                "The digest the client claimed is not the digest of the bytes "
                "that arrived. The two ends do not hold the same document, so "
                "this attempt recorded nothing and the artifact store was never "
                "asked to hold these bytes. Export again and resubmit.",
                checksum=artifact.checksum.hex_digest,
            )

        try:
            snapshot = parse_snapshot(
                artifact, deployment=self._deployment, limits=self._bundle_limits
            )
        except SnapshotRejected as rejection:
            raise _artifact_refusal(rejection) from None

        return self._persist(
            artifact,
            snapshot,
            principal=principal,
            request_key=request_key,
            key_digest=key_digest,
            correlation_id=correlation_id,
        )

    # -- persistence ----------------------------------------------------------

    def _persist(
        self,
        artifact: SnapshotArtifact,
        snapshot: ParsedSnapshot,
        *,
        principal: ServicePrincipal,
        request_key: str,
        key_digest: str,
        correlation_id: UUID,
    ) -> SubmissionReceipt:
        digest = request_hash(SUBMISSION_SCOPE, artifact.checksum.hex_digest)
        checksum = artifact.checksum.hex_digest

        # At most two attempts: the second exists only for the case where a
        # concurrent submission of the *same bytes* won the snapshot identity,
        # and one more pass then takes the duplicate branch. Written as a bounded
        # loop rather than a nested `try` so that there is exactly one place
        # `_store_and_record` is called from and exactly one place each outcome
        # is decided — the previous nesting had the conflict rules examined in
        # two arms, which is how one of them came to be missing a check.
        retried = False
        while True:
            try:
                return self._store_and_record(
                    artifact,
                    snapshot,
                    principal=principal,
                    request_key=request_key,
                    key_digest=key_digest,
                    correlation_id=correlation_id,
                    digest=digest,
                )
            except _RequestKeyAlreadySpent:
                # An ordinary same-key retry. The receipt exists, and reading it
                # back is **not** this transaction's business: it goes through
                # the one fenced boundary, exactly as the race below does.
                return self._fenced_replay(
                    principal=principal,
                    request_key=request_key,
                    digest=digest,
                    checksum=checksum,
                )
            except UniquenessConflict as conflict:
                # Somebody else claimed an identity this attempt needed. The
                # adapter has already rolled this transaction back, so there is
                # nothing partial to undo; what is left is to find out who won
                # and say so truthfully, in a fresh transaction, rather than
                # assume it from the rule name.
                if conflict.rule == "idempotency_key.scope_key":
                    # A concurrent submission under the *same key* won. Its
                    # receipt is the answer — if this credential's generation is
                    # still open, if the receipt was earned under it, and if it
                    # is for the same bytes. All three are the fence's to decide,
                    # and this transaction is gone, so none of them may be
                    # decided here.
                    return self._fenced_replay(
                        principal=principal,
                        request_key=request_key,
                        digest=digest,
                        checksum=checksum,
                    )
                if conflict.rule == "foundry_snapshot.checksum" and not retried:
                    retried = True
                    continue
                # `_store_and_record` has already run, so the artifact may well
                # be on disk under its checksum. What this path establishes is
                # only that *this attempt* recorded nothing (review finding I-1).
                raise SubmissionRefused(
                    "concurrent_submission",
                    "Another submission claimed an identity this one needed and "
                    "could not be identified. This attempt recorded nothing and "
                    "confirmed nothing. Retry with the same request key: a retry "
                    "cannot create a second snapshot.",
                    checksum=checksum,
                ) from None

    def _store_and_record(
        self,
        artifact: SnapshotArtifact,
        snapshot: ParsedSnapshot,
        *,
        principal: ServicePrincipal,
        request_key: str,
        key_digest: str,
        correlation_id: UUID,
        digest: bytes,
    ) -> SubmissionReceipt:
        checksum = artifact.checksum.hex_digest
        with self._unit_of_work_factory() as unit_of_work:
            # **First statement of the transaction, and the order is the point.**
            # It takes the shared side of the fence lock; closure takes the
            # exclusive side. So this transaction and a closure can never
            # overlap: either the closure has already committed, in which case
            # every read below sees it, or it cannot commit until this
            # transaction ends. Nothing after this line has to reason about how
            # many milliseconds separated two observations, which is what every
            # previous remediation was reduced to arguing about.
            unit_of_work.submission_admissions.hold_against_closure()

            # The admission this credential holds, resolved from the principal id
            # the request itself carried. Never from "which generation is open
            # now": a request paused before this line must resolve to the same
            # admission when it wakes, and a current-generation lookup would
            # silently upgrade it into the one recovery just authorized. That is
            # the defect B-1 is open against, in its purest form.
            admission = unit_of_work.submission_admissions.find_for_principal(
                principal.principal_id
            )
            if admission is None or not admission.is_open:
                # Fail closed on both. An unknown credential is not a credential
                # whose generation happens to be missing — it is one that has
                # never been admitted, and admitting it here would make the
                # absence of a row into permission.
                raise _admission_refusal(admission, checksum=checksum)

            spent = unit_of_work.idempotency.find(SUBMISSION_SCOPE, request_key)
            if spent is not None:
                # This method makes submissions durable. It does not answer with
                # a receipt somebody else earned — `_fenced_replay` does, and it
                # is reached from `_persist` for this signal and for the
                # uniqueness race alike. Raising here rather than replaying in
                # place is what keeps the number of principal-bound replay
                # boundaries at one (review finding C-24-R1).
                #
                # Nothing has been written yet: the artifact store has not run,
                # so leaving this `with` block without committing discards a
                # transaction that only read.
                raise _RequestKeyAlreadySpent

            # Bytes first, row second. The store is content-addressed and
            # idempotent, so a failure between the two leaves an artifact that a
            # retry re-stores harmlessly and *no* database claim. The other
            # order can commit a row pointing at bytes that were never written.
            #
            # This raise leaves the `with` block without committing, so the
            # snapshot row, the idempotency receipt and the accepted audit event
            # are all rolled back together. That is what makes the store's
            # `durability_unconfirmed` refusal (review finding I-2) mean what it
            # says: a directory entry whose persistence was not established
            # cannot be backed by a committed database claim that it was.
            try:
                location = self._artifacts.store(artifact)
            except ArtifactStorageError as error:
                raise SubmissionRefused(
                    "storage_unavailable",
                    # Says what the store established and no more. Some reasons
                    # (`durability_unconfirmed`) leave a correct file behind by
                    # design; the caller cannot act on which, and does not need
                    # to, because the retry is safe either way.
                    "The snapshot artifact could not be confirmed as stored, so "
                    f"nothing was recorded ({error.reason}). Retrying with the "
                    "same request key is safe: a retry cannot create a second "
                    "snapshot.",
                    checksum=checksum,
                ) from None

            record = unit_of_work.snapshots.get_by_checksum(checksum)
            duplicate = record is not None
            if record is None:
                record = unit_of_work.snapshots.add(
                    SnapshotRecord(
                        checksum=checksum,
                        size_bytes=artifact.size_bytes,
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
                        artifact_location=location,
                        received_via=SnapshotSource.FOUNDRY_MODULE,
                        submitted_by_principal=principal.principal_id,
                    )
                )

            receipt = SubmissionReceipt(
                snapshot_id=record.id,
                checksum=checksum,
                size_bytes=artifact.size_bytes,
                actor_count=len(snapshot.actors),
                world_id=snapshot.world.world_id,
                exporter=snapshot.exporter.describe(),
                folders=_folders(snapshot),
                canonical_encoding=snapshot.canonical_encoding,
                correlation_id=record.correlation_id,
                duplicate=duplicate,
            )

            # Writing this row is what makes the submission durable, on this path
            # and on the duplicate-bytes path above where no snapshot row was
            # created — so its `admission_id` foreign key is the one lock every
            # acceptance takes. Checking that key takes `KEY SHARE` on the
            # admission row, which conflicts with the `FOR UPDATE` a closure
            # takes, so this statement is a synchronisation point as well as a
            # write.
            unit_of_work.idempotency.add(
                IdempotencyRecord(
                    scope=SUBMISSION_SCOPE,
                    key=request_key,
                    request_hash=digest,
                    status=IdempotencyStatus.COMPLETED,
                    response=receipt.as_payload(),
                    admission_id=admission.id,
                )
            )
            unit_of_work.audit.record(
                AuditEvent(
                    action=SUBMISSION_ACCEPTED,
                    entity_type=SNAPSHOT_ENTITY,
                    entity_id=checksum,
                    source=AuditSource.FOUNDRY,
                    actor_capability=ActorCapability.SERVICE_PRINCIPAL,
                    correlation_id=correlation_id,
                    payload=enforced(
                        SUBMISSION_ACCEPTED,
                        {
                            "snapshot_checksum": checksum,
                            "size_bytes": artifact.size_bytes,
                            "actor_count": len(snapshot.actors),
                            "world_id": snapshot.world.world_id,
                            "exporter": snapshot.exporter.describe(),
                            "selected_folder_ids": list(
                                snapshot.selected_folder_ids
                            ),
                            "canonical_encoding": snapshot.canonical_encoding,
                            "service_principal_id": principal.principal_id,
                            "request_key_digest": key_digest,
                            "received_via": SnapshotSource.FOUNDRY_MODULE.value,
                            "duplicate": duplicate,
                            "admission_generation": admission.generation,
                        },
                    ),
                )
            )

            # **The last thing before the commit, and the second half of the
            # fence.** The lock at the top of this transaction already excludes
            # an overlapping closure; this excludes one even if that lock were
            # ever removed, because the `idempotency_keys` insert above has taken
            # the admission row's `KEY SHARE` lock and a closure holding
            # `FOR UPDATE` had to finish before that could be granted. Under
            # `READ COMMITTED` this statement takes its own snapshot, so it sees
            # that closure.
            #
            # It answers the sequence B-1 is open against directly: it does not
            # matter where the old request was paused, because what is re-read
            # here is its *own* credential's admission, and a closed one can
            # never be replaced by an open one.
            if (
                unit_of_work.submission_admissions.state_of(admission.id)
                is not AdmissionState.OPEN
            ):
                # Leaves the `with` block without committing, so the snapshot
                # row, the receipt and the acceptance event roll back together.
                # A `None` state lands here too: a missing admission row is a
                # schema fault, and treating it as permission would be the
                # fail-open direction.
                raise SubmissionRefused(
                    "admission_closed",
                    "This credential's admission generation was closed while "
                    "this submission was being recorded, so nothing was "
                    "recorded. A settlement is in progress. Do not retry: an "
                    "operator will issue a new credential if a fresh export is "
                    "authorized.",
                    checksum=checksum,
                    admission_generation=admission.generation,
                )
            unit_of_work.commit()
        return receipt

    def _fenced_replay(
        self,
        *,
        principal: ServicePrincipal,
        request_key: str,
        digest: bytes,
        checksum: str,
    ) -> SubmissionReceipt:
        """**The one boundary a stored successful receipt is ever returned from.**

        Both ways of arriving at "this key already has a receipt" end here: the
        ordinary same-key retry, which finds the row before the store runs, and
        recovery from a lost `idempotency_key.scope_key` race, which finds out
        afterwards. Review finding C-24-R1 was that the second of those returned
        the winner's receipt from a bare read — no lock, no admission, no
        generation check — so a request that lost the race before a settlement
        could answer successfully after it. The fix is not a check in that
        branch; it is that the branch no longer decides anything.

        Everything below happens in **one transaction**, in this order, and the
        order is the fence:

        1. the shared side of the admission lock, taken before any receipt is
           read. Closure takes the exclusive side, so this transaction is wholly
           before or wholly after a closure — never astride one. A replay writes
           no row, takes no foreign key and therefore no `KEY SHARE` lock, so
           this advisory lock is the *only* thing ordering it against a closure;
        2. the admission of the principal id **this request authenticated as**,
           never a globally current generation and never the principal recorded
           on the stored row. A receipt is not a credential, and reading
           authorization out of the record being replayed would let the record
           authorize its own replay;
        3. that admission must still be open;
        4. the stored receipt must have been earned under *that* admission, so no
           key can carry a receipt across a generation boundary; and
        5. the digest check `_replay` has always made, which is what separates a
           retry from a key reused for other bytes.

        The receipt is built before the transaction ends, so the lock still holds
        when the answer is decided.
        """
        with self._unit_of_work_factory() as unit_of_work:
            unit_of_work.submission_admissions.hold_against_closure()
            admission = unit_of_work.submission_admissions.find_for_principal(
                principal.principal_id
            )
            if admission is None or not admission.is_open:
                # Identical to the acceptance path's treatment, and deliberately
                # so: a credential that may not record may not replay either.
                raise _admission_refusal(admission, checksum=checksum)

            spent = unit_of_work.idempotency.find(SUBMISSION_SCOPE, request_key)
            if spent is None:
                # Reachable only from the race: the conflict named this rule, so
                # a row exists, and not finding it means the winner cannot be
                # identified. Refused rather than reported as a duplicate of
                # something nobody can name.
                #
                # Two things this may not claim (review finding I-1): the store
                # has already run for this attempt, and another submission *did*
                # record something — this attempt simply cannot read it back. So
                # it speaks only about itself.
                raise SubmissionRefused(
                    "concurrent_submission",
                    "Another submission claimed this request key and its result "
                    "could not be read back. This attempt recorded nothing and "
                    "confirmed nothing. Retry with the same request key: a retry "
                    "cannot create a second snapshot.",
                )
            if spent.admission_id != admission.id:
                raise SubmissionRefused(
                    "admission_closed",
                    "This request key was spent under a different admission "
                    "generation from the one this credential now holds, so its "
                    "receipt is not this credential's to replay. Nothing was "
                    "recorded. Ask an operator which generation is current.",
                    checksum=checksum,
                    admission_generation=admission.generation,
                )

            # Inside the block, so the advisory lock is still held while the
            # answer is decided. `rollback()` afterwards rather than a bare
            # return: this transaction read and wrote nothing, and saying so is
            # cheaper to verify than inferring it from the absence of a commit.
            receipt = _replay(spent, digest)
            unit_of_work.rollback()
        return receipt

    # -- refusal record -------------------------------------------------------

    def _record_refusal(
        self,
        refusal: SubmissionRefused,
        *,
        principal: ServicePrincipal,
        key_digest: str,
        correlation_id: UUID,
    ) -> None:
        """One safe refused event, in its own transaction, claiming no state.

        Best effort by design. The refusal has already happened and is already
        being raised; if the database cannot record it, turning that into a
        *different* error would tell the caller their valid-but-refused
        submission failed for an unrelated reason. The failure is left to the
        adapter's own safe logging.
        """
        payload: dict[str, Any] = {
            "refusal_code": refusal.code,
            "service_principal_id": principal.principal_id,
            "request_key_digest": key_digest,
            # `recorded`, not `stored` (review finding I-1). A refusal always
            # establishes that no snapshot was recorded; it does not establish
            # that no bytes reached the filesystem, and the old key's name
            # asserted the stronger fact on a path that cannot prove it.
            "recorded": False,
        }
        if refusal.admission_generation is not None:
            payload["admission_generation"] = refusal.admission_generation
        if refusal.artifact_code is not None:
            payload["artifact_code"] = refusal.artifact_code
        if refusal.checksum is not None:
            payload["snapshot_checksum"] = refusal.checksum
        event = AuditEvent(
            action=SUBMISSION_REFUSED,
            entity_type=SNAPSHOT_ENTITY,
            entity_id=refusal.checksum or f"unhashed:{key_digest}",
            source=AuditSource.FOUNDRY,
            actor_capability=ActorCapability.SERVICE_PRINCIPAL,
            correlation_id=correlation_id,
            payload=enforced(SUBMISSION_REFUSED, payload),
        )
        try:
            with self._unit_of_work_factory() as unit_of_work:
                unit_of_work.audit.record(event)
                unit_of_work.commit()
        except Exception:  # noqa: BLE001 - see the docstring
            return


def _replay(record: IdempotencyRecord, digest: bytes) -> SubmissionReceipt:
    """The original receipt for an already-spent key, or a typed conflict.

    **Called from `_fenced_replay` and nowhere else**, which is what makes the
    admission checks there unavoidable rather than customary; a call added
    somewhere more convenient would reintroduce review finding C-24-R1 exactly.
    `tests/test_snapshot_submission.py` asserts that over the module's syntax
    tree, so the constraint fails the suite rather than a later review.

    It is reached for both ways a key can already be spent — found before the
    store ran, and discovered by losing a race after it did — so neither refusal
    below may say anything about bytes on disk (review finding I-1), and neither
    may claim that *nothing* was recorded without qualification, because the
    earlier submission that spent this key recorded a great deal. Both speak only
    about this attempt.
    """
    if not record.matches(digest):
        raise SubmissionRefused(
            "request_key_conflict",
            "This request key was already spent on a different snapshot. This "
            "attempt recorded nothing, and the earlier submission's record is "
            "unchanged. Use a new key for a new export.",
        )
    try:
        receipt = SubmissionReceipt.from_payload(record.response)
    except SubmissionReceiptError as error:
        raise SubmissionRefused(
            "original_result_unavailable",
            "This request key was already spent, but the receipt it earned "
            "could not be read back, so this submission cannot be answered with "
            "it. This attempt recorded nothing, and the earlier submission's "
            "record is unchanged.",
        ) from error
    # `duplicate` describes *this attempt*, not the original submission, so it is
    # set here rather than taken from the stored payload.
    return SubmissionReceipt(
        snapshot_id=receipt.snapshot_id,
        checksum=receipt.checksum,
        size_bytes=receipt.size_bytes,
        actor_count=receipt.actor_count,
        world_id=receipt.world_id,
        exporter=receipt.exporter,
        folders=receipt.folders,
        canonical_encoding=receipt.canonical_encoding,
        correlation_id=receipt.correlation_id,
        duplicate=True,
    )


def _admission_refusal(
    admission: SubmissionAdmission | None, *, checksum: str
) -> SubmissionRefused:
    """One code for both shapes of "this credential may not write".

    Never admitted and no longer admitted are different facts, and the message
    distinguishes them because an operator has to act differently on each. The
    *code* does not, because a caller's options are identical: stop, and ask an
    operator. Neither message names a generation the caller does not already
    hold, and neither suggests a retry — repeating the request under the same
    credential can never succeed, so calling it retryable would be false.
    """
    if admission is None:
        return SubmissionRefused(
            "admission_closed",
            "This credential holds no submission admission, so nothing can be "
            "recorded under it and nothing was. Ask an operator to open one, or "
            "to confirm which credential is current.",
            checksum=checksum,
        )
    return SubmissionRefused(
        "admission_closed",
        "This credential's submission admission is closed, so nothing can be "
        "recorded under it and nothing was. Do not retry: an operator will "
        "issue a new credential if a fresh export is authorized.",
        checksum=checksum,
        admission_generation=admission.generation,
    )


def _artifact_refusal(rejection: SnapshotRejected) -> SubmissionRefused:
    """Wrap a parser or ingestion refusal without losing what it said.

    The code is carried separately as `artifact_code` rather than becoming the
    refusal code, so this service's own vocabulary stays closed while the
    operator still learns which rule the bundle broke. The parser's message is
    passed through: those messages name limits, offsets and key names, and are
    written never to quote the bytes.
    """
    code = rejection.code if rejection.code in ARTIFACT_REFUSAL_CODES else None
    return SubmissionRefused(
        "artifact_rejected",
        str(rejection),
        artifact_code=code,
        checksum=rejection.checksum.hex_digest if rejection.checksum else None,
    )


def _folders(snapshot: ParsedSnapshot) -> tuple[SubmittedFolder, ...]:
    return tuple(
        SubmittedFolder(
            folder_id=str(identity.folder_id),
            path=identity.path,
            actors=len(snapshot.actors_in(str(identity.folder_id))),
        )
        for identity in snapshot.selectable_folders()
    )
