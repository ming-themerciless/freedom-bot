"""The durable reconciliation job: its vocabulary, its scope, and its use cases.

**PostgreSQL is the queue and the source of job truth.** A request enqueues or
reads work; it never performs a real preview or apply. That is not a preference —
Rehearsal B previewed a real 32-Actor folder in 9.566 seconds of GIL-holding
`json.loads` and pure-Python NFC normalization, and an apply re-parses the same
artifact before it can re-check anything, so its floor is the same ~9.6 seconds
(route contract §6.3, findings F-1 and F-2). A design in which watching a job
prevents the job from being watched is not a design.

## What this module is, and what it deliberately is not

It is the **application** side of SM-05: the closed vocabularies, the scope
fingerprint, and the four use cases a request can invoke — enqueue a preview,
enqueue an apply, cancel, and read status. Every one of them is a small amount of
decision-making around a statement the repository owns.

It is **not** the worker. Claiming, leasing, heartbeating, reaping and executing
live in `application/worker/`, because the process that does them is a different
process (N-40) and mixing the two here would make it possible to call one from a
request handler by accident.

It is **not** a second importer. `SnapshotImportService.preview` and `.apply` do
the work, unchanged; this module decides *when* they are invoked and by *whom*,
and records the outcome. There is no second field-ownership system, no second
profile, no second calculation path and no second authorization path.

## The scope fingerprint, and why it is one comparison

Schema §10.1 defines `scope_fingerprint` as SHA-256 over the checksum, the
folder, the profile version and the aggregate versions, and says why: **the
staleness test is one equality comparison**, not a list of separate checks that
can drift apart.

The aggregate versions are not knowable when a preview is *enqueued* — finding
out which characters a run would touch requires parsing the artifact, which is
the ten seconds of work the request must not do. So the fingerprint is written
in two phases, and the phase is part of the value rather than a nullable column:

| Job | At enqueue | At completion |
|---|---|---|
| `preview` | over the checksum, folder identity and profile version, with the aggregate component the literal `unobserved` | rewritten by the worker, in the **same transaction** as the result and the state change, with the aggregate versions the run actually read |
| `apply` | **inherited** from the parent preview's completed fingerprint | never rewritten |

The apply's worker recomputes the fingerprint from the artifact in hand and the
database as it stands *now*, and compares it to the one stored. One equality
comparison, exactly as the schema requires, and the thing it is compared against
is the scope a Council member actually confirmed.

Nothing about a preview is made stale by an aggregate version moving, and that is
correct: a preview reports what it sees. What invalidates a preview is the folder
changing (R-41), the profile version changing, the snapshot changing, N-46
elapsing, or authority changing — and each of those is known without parsing.
"""
from __future__ import annotations

import hashlib
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Iterable, Sequence
from uuid import UUID, uuid4

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.errors import RefusalCode, WebRefusal
from application.web.view_models import (
    ACTOR_NAME_BOUND,
    BLOCKED_ENTRY_BOUND,
    CANDIDATE_CHARACTER_BOUND,
    DISCORD_NAME_BOUND,
    ISSUE_COUNT_BOUND,
    PREVIEW_NONCE_BOUND,
    PREVIEW_NONCE_BYTES,
    Actor,
    BlockedEntry,
    ConfirmScope,
    Correlation,
    FolderChoice,
    Instant,
    IssueCount,
    JobFailure,
    JobProgress,
    JobStatusView,
    ReconciliationSummary,
    SafeText,
    StaleReason,
    bounded_tuple,
)

#: N-46. A `completed` preview older than this is treated as `stale` and cannot
#: be confirmed. It bounds the window in which authorization, snapshot, folder,
#: profile and aggregate versions are *assumed* unchanged, and it is independent
#: of — and additional to — the version rechecks, which is why it is a separate
#: control rather than a fallback for them.
#:
#: A constant rather than a setting, deliberately. The numeric register defines
#: it once with no configuration variable, and inventing `WEB_PREVIEW_VALIDITY_*`
#: would make an accepted number an operator's to weaken.
PREVIEW_VALIDITY_SECONDS = 30 * 60

#: N-24. Job and result presentation records are retained 30 days after the job
#: reaches a terminal state. **Nothing here deletes an import or an audit row**:
#: `snapshot_imports` and `audit_events` are append-only and indefinite, so a
#: retention sweep that has run its course removes the working papers and leaves
#: the decision.
RESULT_RETENTION_DAYS = 30

#: N-44. The reaper runs this often — three checks inside one 60-second lease.
#: Consumed by the worker and by the `expired_leases` health check, which is why
#: it lives beside the lease rather than inside the worker package.
REAPER_INTERVAL_SECONDS = 15

#: The contracted default (plan §12 Phase 3, route contract §6.1). An
#: administrator may select any folder the artifact exports; this is what is
#: offered first.
DEFAULT_FOLDER_PATH = "/actors/Characters (active)"

#: Domain separation for the fingerprint and the request key, so a digest minted
#: for one purpose cannot verify as another.
_SCOPE_DOMAIN = b"freedom-blades/p3.3/scope-fingerprint/v1"
_REQUEST_KEY_DOMAIN = "freedom-blades/p3.3/request-key/v1"

#: The aggregate component of a fingerprint that has not observed any yet. A
#: literal rather than an empty string, so "no aggregates" and "an empty set of
#: aggregates" are different values and cannot collide.
_UNOBSERVED = "unobserved"


class JobKind(Enum):
    PREVIEW = "preview"
    APPLY = "apply"


class JobState(Enum):
    """Exactly N-27's six. There is no seventh, and cancellation is not one of
    them: `cancel_requested_at` is a **request**."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    STALE = "stale"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_terminal(self) -> bool:
        return self in _TERMINAL_STATES

    @property
    def is_live(self) -> bool:
        return self in (JobState.QUEUED, JobState.RUNNING)


_TERMINAL_STATES = frozenset(
    {JobState.COMPLETED, JobState.STALE, JobState.FAILED, JobState.CANCELLED}
)


class StaleCode(Enum):
    """VM-15's closed `StaleReason` vocabulary, matched to SM-05's triggers."""

    SNAPSHOT_CHANGED = "snapshot_changed"
    FOLDER_CHANGED = "folder_changed"
    PROFILE_VERSION_CHANGED = "profile_version_changed"
    AGGREGATE_VERSION_CHANGED = "aggregate_version_changed"
    PREVIEW_EXPIRED = "preview_expired"
    AUTHORIZATION_CHANGED = "authorization_changed"


class FailureCode(Enum):
    """VM-15's closed `JobFailure` vocabulary.

    `PARSE_REFUSED` and `ARTIFACT_UNAVAILABLE` are **deterministic**: a refusal
    that would recur on every attempt is failed immediately, whatever `attempts`
    says. Retrying a deterministic refusal three times is thirty seconds of work
    to reach the conclusion the first attempt already had.
    """

    PARSE_REFUSED = "parse_refused"
    ARTIFACT_UNAVAILABLE = "artifact_unavailable"
    ATTEMPTS_EXHAUSTED = "attempts_exhausted"
    TIMEOUT = "timeout"
    INTERNAL = "internal"


#: The two codes above that must never consume a second attempt.
DETERMINISTIC_FAILURES = frozenset(
    {FailureCode.PARSE_REFUSED, FailureCode.ARTIFACT_UNAVAILABLE}
)


@dataclass(frozen=True, slots=True)
class Abandonment:
    """What a worker's self-abandon actually did, told apart rather than guessed.

    Added by the 2026-08-18 P3.3 remediation. Before it, `abandon` returned the
    new state or `None`, and `None` meant only "zero rows" — which after the
    commit fence has two very different causes:

    - `state=None, effect_committed=False` — the reaper acted first and the job
      belongs to somebody else now. The worker exits quietly, as it always did.
    - `state=None, effect_committed=True` — the attempt's effect **committed**
      while the timeout or the kill switch was being observed. Requeueing or
      failing the job here would be abandoning an attempt that has already
      changed the database, so the worker instead waits a bounded moment for the
      thread to hand back its result and publishes it.

    Collapsing the two into `None` is what would let a job say `queued` or
    `failed` over a committed import.
    """

    state: str | None
    effect_committed: bool


@dataclass(frozen=True, slots=True)
class Cancellation:
    """What R-45's request actually did, told apart rather than guessed.

    Added by the 2026-08-18 effect-publication remediation, on the precedent
    `Abandonment` set. `request_cancel` used to answer with a bare `JobState`, and
    `JobState.COMPLETED` was doing double duty as "the job completed" and as "this
    cancellation matched nothing, for one of four different reasons". The route
    then had to guess the conflict word from the job's *state*, which for the
    defect this remediation fixes — a `running` apply whose import has committed —
    said `stale_version` when the truth is `already_applied`.

    - `state=CANCELLED` — a `queued` job was cancelled outright.
    - `state=RUNNING` — a `running` job's request was recorded; the worker
      observes it at its next heartbeat.
    - `state=None` — **refused.** `observed_state` and `effect_committed` say
      which refusal it was, read from the row in the same transaction that failed
      to match it rather than inferred.
    """

    state: JobState | None
    effect_committed: bool
    observed_state: JobState | None

    @property
    def accepted(self) -> bool:
        return self.state is not None

    @property
    def conflict(self) -> str:
        """VM-19's closed `conflict` vocabulary, for a refusal.

        A committed effect answers `already_applied` whatever the job's state
        says, because that is what the Council member needs to know: the import is
        durable and the receipt is the answer. The state only decides the word
        when no effect committed.
        """
        if self.effect_committed or self.observed_state is JobState.COMPLETED:
            return "already_applied"
        if self.observed_state is JobState.CANCELLED:
            return "already_cancelled"
        return "stale_version"


class JobRefused(WebRefusal):
    """A typed refusal from one of this module's use cases.

    Each carries the route contract's own name for the condition (§6.1), so a
    response body and an audit payload say the same word an operator will find
    in the contract.
    """

    def __init__(self, code: RefusalCode, *, status: int) -> None:
        super().__init__(code, status=status)


class CancellationRefused(JobRefused):
    """R-45 matched nothing, and knows which conflict to say so with.

    Carries the VM-19 word rather than leaving the route to derive one from a
    state that no longer describes the refusal. The code is the accepted
    `already_terminal`, whose own definition in `RefusalCode` already reads
    "including an apply that has already committed".
    """

    __slots__ = ("conflict",)

    def __init__(self, *, conflict: str) -> None:
        super().__init__(RefusalCode.ALREADY_TERMINAL, status=409)
        self.conflict = conflict


def queue_full() -> JobRefused:
    """N-42: at most five jobs `queued` for the whole platform, and **no row**.

    `503` rather than `429`: the platform is temporarily unable to accept more
    durable work, and the caller should retry rather than correct anything.
    """
    return JobRefused(RefusalCode.QUEUE_FULL, status=503)


def snapshot_absent() -> JobRefused:
    return JobRefused(RefusalCode.SNAPSHOT_ABSENT, status=404)


def folder_unselected() -> JobRefused:
    """`422`: correctable, and by somebody else. An administrator selects the
    folder (R-41); a Council member cannot, and the form tells them so."""
    return JobRefused(RefusalCode.FOLDER_UNSELECTED, status=422)


def blocked_by_running_apply() -> JobRefused:
    return JobRefused(RefusalCode.BLOCKED_BY_RUNNING_APPLY, status=409)


def preview_not_confirmable() -> JobRefused:
    return JobRefused(RefusalCode.PREVIEW_NOT_CONFIRMABLE, status=409)


# ---------------------------------------------------------------------------
# The scope fingerprint
# ---------------------------------------------------------------------------


def scope_fingerprint(
    *,
    checksum: str,
    folder_id: str,
    folder_path: str,
    profile_version: str,
    aggregate_versions: Sequence[tuple[str, int]] | None = None,
) -> bytes:
    """Schema §10.1's SHA-256, over a delimiter-safe encoding of the scope.

    `\\x1f` separates fields because it cannot occur in any of them — checksums
    are hex, folder ids and profile versions are bounded identifiers, and a
    folder path is a Foundry path — so no value can forge a field boundary and
    make two different scopes hash the same.

    Both halves of folder identity are covered. ADR 0006 makes a folder's
    identity the pair `(stable id, displayed path)`: a folder renamed between
    preview and apply is a different confirmation from the one a Council member
    read, and a fingerprint over the id alone could not say so.
    """
    aggregates = (
        _UNOBSERVED
        if aggregate_versions is None
        else "\x1e".join(
            f"{identifier}={version}"
            for identifier, version in sorted(aggregate_versions)
        )
    )
    material = "\x1f".join(
        (checksum, folder_id, folder_path, profile_version, aggregates)
    )
    digest = hashlib.sha256()
    digest.update(_SCOPE_DOMAIN)
    digest.update(b"\x1f")
    digest.update(material.encode("utf-8"))
    return digest.digest()


def mint_preview_nonce() -> str:
    """A fresh R-42 request identity for **one** R-40 render (VM-14).

    Lives here rather than in the adapter because this module owns the other half
    of the pair: `request_key` below is the only thing that consumes a nonce, and
    a value minted somewhere with no view of that algorithm is a value nobody can
    reason about. The R-40 handler calls it once per successful render and hands
    the result to `SnapshotAdminService.snapshot_list`, in the same position as
    the CSRF token it already passes and for the same reason the handler passes
    `now=` to this module's other use cases: a service that generated its own
    randomness would be a service whose output no test could predict.

    **Opaque, and deliberately empty of meaning.** `secrets.token_urlsafe` over
    `PREVIEW_NONCE_BYTES` is 256 bits of CSPRNG output rendered as exactly
    `PREVIEW_NONCE_BOUND` URL/form-safe characters. It encodes no account, no
    capability, no snapshot, no folder and no timestamp, because every one of
    those is a server-owned fact that R-42 re-reads rather than believes, and
    putting one here would be inviting a caller to edit it.

    It is **not** a bearer token and shares nothing with `crypto.mint_token`
    beyond the primitive: possessing it authorizes nothing, it is never checked
    for validity, and it is never stored in this form.
    """
    return secrets.token_urlsafe(PREVIEW_NONCE_BYTES)


#: The exact rendered shape of a `preview_nonce`, and therefore the exact shape
#: R-42 accepts back. Built from `PREVIEW_NONCE_BOUND` rather than restating 43,
#: so the width the page renders and the width the boundary admits cannot drift:
#: they are the same number read once.
#:
#: `secrets.token_urlsafe` emits base64url without padding, whose alphabet is
#: exactly `A-Za-z0-9_-`. No `=`, no `+`, no `/`, no whitespace and nothing
#: outside ASCII was ever minted, so nothing outside this class is a value this
#: platform produced.
_PREVIEW_NONCE_GRAMMAR = re.compile(f"[A-Za-z0-9_-]{{{PREVIEW_NONCE_BOUND}}}")


def parse_preview_nonce(submitted: object) -> str | None:
    """The submitted R-42 nonce if it is **exactly** what R-40 mints, else `None`.

    The one place the R-42 grammar is stated, consumed by the route boundary so
    that "what the page renders" and "what the server accepts" are one rule rather
    than two that agree today. `mint_preview_nonce` above produces the only values
    that satisfy it.

    **Nothing is normalized.** No strip, no case fold, no Unicode normalization,
    no percent-decoding. Every one of those turns some submitted value that is
    not a minted nonce into one that looks like it, and a boundary whose job is
    "accept exactly this" must not be the thing that manufactures a match. A
    value with a leading space is refused rather than trimmed into acceptance.

    **This is not authentication.** A well-formed nonce is not checked against
    anything, grants nothing, and is never compared to a stored value — R-42
    re-resolves Council capability and every server-owned snapshot, folder and
    profile fact regardless. All this function establishes is that the request
    carries a *request identity of the accepted shape*, so that `request_key`
    below hashes something bounded and the idempotency it provides is the
    idempotency VM-14 describes.

    Takes `object` because a form value is whatever the framework parsed: a
    `str` for an ordinary field, an upload object for a multipart part. Anything
    that is not a `str` is refused rather than coerced.
    """
    if not isinstance(submitted, str):
        return None
    # Width first, so an oversized body — a megabyte of `A` inside the global
    # body bound — is refused by a length comparison rather than by running a
    # quantified pattern over all of it.
    if len(submitted) != PREVIEW_NONCE_BOUND:
        return None
    if _PREVIEW_NONCE_GRAMMAR.fullmatch(submitted) is None:
        return None
    return submitted


def request_key(
    *,
    kind: JobKind,
    snapshot_checksum: str,
    folder_id: str,
    profile_version: str,
    account_id: UUID,
    nonce: str,
) -> str:
    """R-42's idempotency key: `(snapshot, folder, profile version, account, nonce)`.

    **A digest, never the caller's text.** The nonce arrives in a form field, and
    an apply's key is written verbatim into `snapshot_imports.request_key` —
    which is exactly the column finding S-1 established must not become an
    arbitrary text channel a caller could put a player name, an address or a
    credential into. Hashing at the boundary means the durable column holds a
    fixed-width value the platform minted, and a double-click still produces the
    identical key because every input to it is identical.

    The kind is in the material, so a preview and the apply confirmed from it
    never collide on `uq_reconciliation_jobs_request_key`.
    """
    material = "\x1f".join(
        (
            _REQUEST_KEY_DOMAIN,
            kind.value,
            snapshot_checksum,
            folder_id,
            profile_version,
            str(account_id),
            nonce,
        )
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return f"p3.3:{kind.value}:{digest}"


# ---------------------------------------------------------------------------
# The use cases
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConfirmationRefused:
    """R-46 refused, **and the refusal may have changed durable state**.

    Returned rather than raised, and that is not a style choice. Marking a
    preview `stale` is a state change, and the adapter's unit of work rolls back
    on an exception — so raising out of the transaction that made the mark would
    undo it, and the next confirmation would be refused all over again by a check
    that had already run once. A returned refusal commits with its mark.

    `reason` is `None` when nothing moved: the token did not match, or the job is
    not a confirmable preview. Those refusals change nothing, and reporting a
    stale code for them would name a cause that did not happen.

    The three conditions that produce `reason = None` are **one code** on the
    wire. Distinguishing "wrong token" from "not completed" from "already
    confirmed" would tell a caller which half of a confirmation they guessed
    right.
    """

    reason: StaleCode | None = None


@dataclass(frozen=True, slots=True)
class EnqueuedJob:
    """What a request learns from enqueuing: an id, and whether it made one.

    `created` is `False` for the second of two identical submissions. The route
    redirects to the same place either way — a double-click is indistinguishable
    from a single click at the user's level while remaining one durable effect.
    """

    job_id: UUID
    created: bool
    correlation_id: UUID


class ReconciliationJobService:
    """R-42, R-45 and R-46's enqueue half, and R-43/R-44's read half.

    Every method takes the caller's *current* `WebAuthorizationContext` — the one
    the request preamble resolved moments ago, never a claim carried from a
    previous request — and every one of them is called inside a transaction the
    adapter opened, so a state change and its audit event commit together or not
    at all.
    """

    __slots__ = ("_jobs", "_snapshots", "_accounts", "_audit", "_bounds", "_worker")

    def __init__(self, *, jobs, snapshots, accounts, audit, bounds, worker) -> None:
        self._jobs = jobs
        self._snapshots = snapshots
        self._accounts = accounts
        self._audit = audit
        self._bounds = bounds
        self._worker = worker

    # -- R-42 --------------------------------------------------------------
    def enqueue_preview(
        self,
        *,
        context,
        snapshot_id: UUID,
        nonce: str,
        now: datetime,
    ) -> EnqueuedJob:
        """Enqueue a `preview`, or return the job an identical submission made.

        The order is the contract's, and each step refuses before the next costs
        anything: the snapshot must exist, a folder must be selected, no apply of
        the same input may be in flight, and only then is the queue bound tested
        — because N-42 is a bound on *accepted* work and refusing a request that
        was going to be refused anyway should not consume it.
        """
        context.require_council()
        snapshot = self._snapshots.snapshot(snapshot_id)
        if snapshot is None:
            raise snapshot_absent()
        selection = self._snapshots.folder_selection(snapshot_id)
        if selection is None:
            raise folder_unselected()
        profile_version = self._snapshots.profile_version()

        if self._jobs.live_apply_exists(
            snapshot_id=snapshot_id,
            folder_id=selection["folder_id"],
            profile_version=profile_version,
        ):
            # An apply of this exact input is queued or running. Previewing
            # underneath it would produce a confirmation against a scope that is
            # about to move.
            raise blocked_by_running_apply()

        key = request_key(
            kind=JobKind.PREVIEW,
            snapshot_checksum=snapshot["checksum"],
            folder_id=selection["folder_id"],
            profile_version=profile_version,
            account_id=context.account_id,
            nonce=nonce,
        )
        existing = self._jobs.by_request_key(key)
        if existing is not None:
            return EnqueuedJob(
                job_id=existing["id"],
                created=False,
                correlation_id=existing["correlation_id"],
            )

        if self._jobs.queued_count() >= self._worker.queue_max_depth:
            raise queue_full()

        correlation_id = uuid4()
        job_id = self._jobs.insert(
            kind=JobKind.PREVIEW,
            snapshot_id=snapshot_id,
            folder_id=selection["folder_id"],
            profile_version=profile_version,
            fingerprint=scope_fingerprint(
                checksum=snapshot["checksum"],
                folder_id=selection["folder_id"],
                folder_path=selection["folder_path"],
                profile_version=profile_version,
            ),
            requested_by_account_id=context.account_id,
            requested_capability=ActorCapability.GUILD_COUNCIL,
            request_key=key,
            parent_job_id=None,
            correlation_id=correlation_id,
            now=now,
        )
        self._audit.record(
            AuditEvent(
                action="reconciliation.job_queued",
                entity_type="reconciliation_job",
                entity_id=str(job_id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.GUILD_COUNCIL,
                actor_platform_account_id=context.account_id,
                correlation_id=correlation_id,
                payload={
                    "kind": JobKind.PREVIEW.value,
                    "snapshot_id": str(snapshot_id),
                    "checksum": snapshot["checksum"],
                    "folder_id": selection["folder_id"],
                    "profile_version": profile_version,
                },
            )
        )
        return EnqueuedJob(job_id=job_id, created=True, correlation_id=correlation_id)

    # -- R-46 --------------------------------------------------------------
    def enqueue_apply(
        self,
        *,
        context,
        job_id: UUID,
        preview_token: str,
        nonce: str,
        now: datetime,
    ) -> "EnqueuedJob | ConfirmationRefused":
        """Confirm a completed preview by enqueuing an `apply`. Never applies inline.

        The five checks route contract §6.1 requires, in its order:

        1. the submitted `preview_token` equals the job's stored token;
        2. the job is `completed` and within N-46;
        3. **current** Council authority — re-resolved by the request preamble
           for *this* request, and asserted again here rather than carried from
           the preview;
        4. checksum, selected folder, field-profile version and the database
           aggregate versions are re-checked — the first three now, and all four
           again inside the worker's own transaction, because the ones that can
           move between here and there must be checked where the write happens;
        5. an `apply` job is enqueued with the caller's request key, and the
           existing `SnapshotImportService.apply` performs the atomic commit.

        Idempotency is **not** invented here. It comes from
        `uq_snapshot_imports_applied_input` and `snapshot_imports.request_key`,
        both of which already exist and are already tested. What this method adds
        is `uq_reconciliation_jobs_one_live_apply`, which stops the second of two
        concurrent applies from starting and spending ten seconds of parsing to
        discover the first won.
        """
        context.require_council()
        preview = self._jobs.job(job_id)
        if preview is None or preview["kind"] != JobKind.PREVIEW.value:
            raise snapshot_absent()

        result = self._jobs.result_for_job(job_id)
        stored_token = (result or {}).get("summary", {}).get("preview_token")
        if (
            preview["state"] != JobState.COMPLETED.value
            or result is None
            or not stored_token
            or not _constant_time_equal(stored_token, preview_token)
        ):
            # Nothing moved and nothing is written: this confirmation named a
            # preview that is not confirmable, and saying which of the three
            # reasons applies would be an oracle.
            return ConfirmationRefused()
        if _expired(result["produced_at"], now):
            # N-46, applied before anything else is read: an old preview is not
            # confirmable however unchanged everything else is.
            self._jobs.mark_stale(
                job_id=job_id, reason=StaleCode.PREVIEW_EXPIRED, now=now
            )
            return ConfirmationRefused(reason=StaleCode.PREVIEW_EXPIRED)

        selection = self._snapshots.folder_selection(preview["snapshot_id"])
        snapshot = self._snapshots.snapshot(preview["snapshot_id"])
        profile_version = self._snapshots.profile_version()
        if snapshot is None:
            raise snapshot_absent()
        if selection is None:
            raise folder_unselected()
        if (
            selection["folder_id"] != preview["folder_id"]
            or profile_version != preview["profile_version"]
            or snapshot["checksum"] != (result["summary"] or {}).get("checksum")
        ):
            # The scope moved between the preview and this confirmation. Nothing
            # is applied and the preview is marked with the reason, so the
            # Council member sees *what* changed rather than a bare refusal.
            moved = (
                StaleCode.FOLDER_CHANGED
                if selection["folder_id"] != preview["folder_id"]
                else StaleCode.PROFILE_VERSION_CHANGED
                if profile_version != preview["profile_version"]
                else StaleCode.SNAPSHOT_CHANGED
            )
            self._jobs.mark_stale(job_id=job_id, reason=moved, now=now)
            return ConfirmationRefused(reason=moved)

        key = request_key(
            kind=JobKind.APPLY,
            snapshot_checksum=snapshot["checksum"],
            folder_id=selection["folder_id"],
            profile_version=profile_version,
            account_id=context.account_id,
            nonce=nonce,
        )
        existing = self._jobs.by_request_key(key)
        if existing is not None:
            return EnqueuedJob(
                job_id=existing["id"],
                created=False,
                correlation_id=existing["correlation_id"],
            )
        if self._jobs.live_apply_exists(
            snapshot_id=preview["snapshot_id"],
            folder_id=selection["folder_id"],
            profile_version=profile_version,
        ):
            raise blocked_by_running_apply()
        if self._jobs.queued_count() >= self._worker.queue_max_depth:
            raise queue_full()

        correlation_id = uuid4()
        apply_id = self._jobs.insert(
            kind=JobKind.APPLY,
            snapshot_id=preview["snapshot_id"],
            folder_id=selection["folder_id"],
            profile_version=profile_version,
            # **Inherited, not recomputed.** The apply is a confirmation of the
            # scope this preview observed, aggregate versions included, and the
            # worker's one equality comparison is against exactly that.
            fingerprint=bytes(preview["scope_fingerprint"]),
            requested_by_account_id=context.account_id,
            requested_capability=ActorCapability.GUILD_COUNCIL,
            request_key=key,
            parent_job_id=job_id,
            correlation_id=correlation_id,
            now=now,
        )
        self._audit.record(
            AuditEvent(
                action="reconciliation.apply_requested",
                entity_type="reconciliation_job",
                entity_id=str(apply_id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.GUILD_COUNCIL,
                actor_platform_account_id=context.account_id,
                correlation_id=correlation_id,
                payload={
                    "preview_job_id": str(job_id),
                    "snapshot_id": str(preview["snapshot_id"]),
                    "checksum": snapshot["checksum"],
                    "folder_id": selection["folder_id"],
                    "profile_version": profile_version,
                },
            )
        )
        return EnqueuedJob(job_id=apply_id, created=True, correlation_id=correlation_id)

    # -- R-45 --------------------------------------------------------------
    def cancel(self, *, context, job_id: UUID, now: datetime) -> JobState:
        """Best effort. A `queued` job cancels now; a `running` one at its next
        heartbeat; a committed apply **never**.

        Both cancel statements filter `effect_committed_at IS NULL`, so a job
        whose apply has already committed matches zero rows and this raises the
        `409` the route answers with the committed result — the difference between
        "your cancellation was too late" and "your cancellation worked", stated
        truthfully.

        **A refusal writes no audit event** (2026-08-18 effect-publication
        remediation). Before it, a cancellation that matched nothing still recorded
        `reconciliation.job_cancel_requested` and the route still answered `303`,
        so the append-only history said a Council member's cancellation request had
        been accepted for a job whose import was durable and whose state never
        changed. Nothing was requested, so nothing is recorded; the refusal itself
        reaches the operator as the `409` and its correlation id.

        Cancelling does not erase history: the job's audit events and, if the
        apply committed, the `snapshot_imports` row remain.
        """
        context.require_council()
        job = self._jobs.job(job_id)
        if job is None:
            raise snapshot_absent()
        state = JobState(job["state"])
        if state.is_terminal:
            raise CancellationRefused(conflict=_terminal_conflict(state))

        outcome = self._jobs.request_cancel(job_id=job_id, now=now)
        if not outcome.accepted:
            # Refused at the write boundary: the effect committed, or the job
            # reached a terminal state between the read above and the statement.
            # The typed outcome says which, so the conflict word is the row's
            # rather than a guess from a state that no longer describes it.
            raise CancellationRefused(conflict=outcome.conflict)

        correlation_id = uuid4()
        self._audit.record(
            AuditEvent(
                action="reconciliation.job_cancel_requested",
                entity_type="reconciliation_job",
                entity_id=str(job_id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.GUILD_COUNCIL,
                actor_platform_account_id=context.account_id,
                correlation_id=correlation_id,
                payload={
                    "kind": job["kind"],
                    "observed_state": state.value,
                    "outcome": outcome.state.value,
                },
            )
        )
        return outcome.state

    # -- R-43 and R-44 -----------------------------------------------------
    def status(self, *, context, job_id: UUID, csrf_token: str) -> JobStatusView:
        """VM-15, bounded. **No audit event**: a poll is a read.

        Auditing a poll would flood the append-only table with the fact that
        somebody looked at their own guild's operational state, at up to one
        event every two seconds per watcher, forever.
        """
        context.require_council()
        job = self._jobs.job(job_id)
        if job is None:
            raise snapshot_absent()
        return self.render(job=job, csrf_token=csrf_token)

    def render(self, *, job, csrf_token: str) -> JobStatusView:
        """One job row, and its result if it has one, as VM-15."""
        state = JobState(job["state"])
        # Read from the **result** side rather than through `job["result_id"]`.
        # A preview that went `stale` no longer names its result — the check
        # constraint reserves that pointer for `completed` — but the result
        # itself is untouched, and a Council member looking at a preview that has
        # just become unconfirmable needs to see what it said as well as why it
        # is stale.
        result_row = self._jobs.result_for_job(job["id"])
        summary = (result_row or {}).get("summary") or {}
        labels = self._accounts.labels_for([job["requested_by_account_id"]])
        account_id = job["requested_by_account_id"]
        requested_by = Actor(
            account_id=account_id,
            label=SafeText.bounded(
                labels.get(account_id) or f"Account {str(account_id)[:8]}",
                DISCORD_NAME_BOUND,
            ),
            capability=ActorCapability(job["requested_capability"]),
        )
        confirm = None
        if (
            state is JobState.COMPLETED
            and job["kind"] == JobKind.PREVIEW.value
            and result_row is not None
        ):
            confirm = _confirm_scope(job, summary, result_row)
        return JobStatusView(
            state=_page_state(state),
            job_id=job["id"],
            kind=job["kind"],
            job_state=state.value,
            progress=_progress(job, state),
            requested_by=requested_by,
            requested_at=Instant.of(job["queued_at"]),
            attempts=job["attempts"],
            # N-22's floor, from the validated bound rather than a literal, so
            # the number the response asks a browser to honour is the number the
            # settings graph accepted.
            poll_after_seconds=self._bounds.poll_min_seconds,
            result=_summary_view(summary, (result_row or {}).get("blocked_entries")),
            stale_reason=(
                StaleReason(code=job["stale_reason"]) if job["stale_reason"] else None
            ),
            failure=(
                JobFailure(
                    code=job["failure_code"],
                    correlation=Correlation(job["correlation_id"]),
                )
                if job["failure_code"]
                else None
            ),
            cancel_available=state.is_live and job["cancel_requested_at"] is None,
            confirm=confirm,
            csrf_token=csrf_token,
            correlation=Correlation(job["correlation_id"]),
        )

    # -- R-41's other half -------------------------------------------------
    def invalidate_for_snapshot(
        self, *, snapshot_id: UUID, reason: StaleCode, now: datetime
    ) -> tuple[UUID, ...]:
        """Every non-terminal job and every completed-but-unconfirmed preview.

        Called from inside R-41's transaction so the selection and the
        invalidation commit together: a folder change that left an outstanding
        preview confirmable would be exactly the gap the mandatory test names.
        """
        return self._jobs.invalidate_for_snapshot(
            snapshot_id=snapshot_id, reason=reason, now=now
        )


# ---------------------------------------------------------------------------
# Rendering helpers — bounded, closed-vocabulary, and artifact-free
# ---------------------------------------------------------------------------


def _terminal_conflict(state: JobState) -> str:
    """VM-19's word for a cancellation that arrived after the job finished.

    The same vocabulary `Cancellation.conflict` uses for a refusal at the write
    boundary, so the two paths into R-45's `409` cannot describe the same
    situation with two different words.
    """
    if state is JobState.CANCELLED:
        return "already_cancelled"
    if state is JobState.COMPLETED:
        return "already_applied"
    return "stale_version"


def _page_state(state: JobState) -> str:
    if state in (JobState.QUEUED, JobState.RUNNING):
        return "loading"
    if state is JobState.STALE:
        return "stale"
    if state is JobState.FAILED:
        return "error"
    return "ready"


def _progress(job, state: JobState) -> JobProgress | None:
    """`percent` is always `None`.

    The parser reports no fraction, and VM-15 says a fabricated progress bar is
    worse than an indeterminate one. The step is a real observation: `queued`
    until a worker claims it, `parsing` once one has — which is where every
    second of the measured 9.566 is spent.
    """
    if state is JobState.QUEUED:
        return JobProgress(step="queued", percent=None, updated_at=Instant.of(job["queued_at"]))
    if state is JobState.RUNNING:
        moment = job["heartbeat_at"] or job["started_at"] or job["queued_at"]
        return JobProgress(step="parsing", percent=None, updated_at=Instant.of(moment))
    return None


def _summary_view(summary, blocked_entries) -> ReconciliationSummary | None:
    """The stored bounded summary as VM-15's `ReconciliationSummary`.

    Every field is a count or a closed-vocabulary code. The one exception is a
    blocked entry's display name, which is the minimum a Council member needs to
    resolve a blocked create-candidate — bounded at §3.2's 120 characters,
    limited to 50 entries, and carrying no other Actor field.
    """
    if not summary or "actors" not in summary:
        return None
    counts, _ = bounded_tuple(
        (
            IssueCount(
                code=str(entry["code"]),
                severity=("error" if entry.get("severity") == "error" else "warning"),
                count=int(entry["count"]),
            )
            for entry in (summary.get("issue_counts") or [])
        ),
        ISSUE_COUNT_BOUND,
    )
    entries, _ = bounded_tuple(
        (
            BlockedEntry(
                external_actor_id=str(entry["external_actor_id"]),
                display_name=SafeText.bounded(
                    entry.get("display_name"), ACTOR_NAME_BOUND
                ),
                issue_code=str(entry["issue_code"]),
                candidate_character_ids=tuple(
                    UUID(value)
                    for value in (entry.get("candidate_character_ids") or [])[
                        :CANDIDATE_CHARACTER_BOUND
                    ]
                ),
            )
            for entry in (blocked_entries or [])
        ),
        BLOCKED_ENTRY_BOUND,
    )
    return ReconciliationSummary(
        actor_count=int(summary["actors"]),
        mapped=int(summary["mapped"]),
        unmapped=int(summary["unmapped"]),
        blocked=int(summary["blocked"]),
        absent=int(summary["absent"]),
        would_create=int(summary.get("would_create", summary["unmapped"])),
        would_update=int(summary.get("would_update", 0)),
        issue_counts=counts,
        blocked_entries=entries,
    )


def _confirm_scope(job, summary, result_row) -> ConfirmScope:
    return ConfirmScope(
        preview_token=str(summary.get("preview_token", "")),
        checksum_full=str(summary.get("checksum", "")),
        folder=FolderChoice(
            folder_id=job["folder_id"],
            folder_path=SafeText.bounded(summary.get("folder_path"), ACTOR_NAME_BOUND),
            actor_count=int(summary.get("actors", 0)),
            is_default=str(summary.get("folder_path")) == DEFAULT_FOLDER_PATH,
        ),
        profile_version=job["profile_version"],
        expires_at=Instant.of(
            result_row["produced_at"] + timedelta(seconds=PREVIEW_VALIDITY_SECONDS)
        ),
        would_create=int(summary.get("would_create", summary.get("unmapped", 0))),
        would_update=int(summary.get("would_update", 0)),
        blocked=bool(summary.get("blocked", 0)) or int(summary.get("errors", 0)) > 0,
    )


def _expired(produced_at: datetime, now: datetime) -> bool:
    return now - produced_at > timedelta(seconds=PREVIEW_VALIDITY_SECONDS)


def _constant_time_equal(left: str, right: str) -> bool:
    """The stored token is a digest and the presented one is caller input.

    Compared in constant time for the same reason the synchronizer token is: a
    comparison that returns early tells an attacker how much of a guess was
    right, one character at a time.
    """
    import hmac

    return hmac.compare_digest(left, right)


def issue_counts_from(issues: Iterable) -> list[dict]:
    """Fold reconciliation issues into `{code, severity, count}` triples.

    The **message is dropped here**, at the point the durable result is built,
    rather than filtered later at rendering. A message quotes Actor data, so the
    only reliable place to remove it is before it is stored — which is what makes
    "artifact text never reaches a response" a property of the record instead of
    a property of a template nobody forgot to change.
    """
    folded: dict[tuple[str, str], int] = {}
    for issue in issues:
        key = (issue.code, issue.severity.value)
        folded[key] = folded.get(key, 0) + 1
    return [
        {"code": code, "severity": severity, "count": count}
        for (code, severity), count in sorted(folded.items())
    ]


__all__ = [
    "Abandonment",
    "Cancellation",
    "CancellationRefused",
    "ConfirmationRefused",
    "DEFAULT_FOLDER_PATH",
    "DETERMINISTIC_FAILURES",
    "EnqueuedJob",
    "FailureCode",
    "JobKind",
    "JobRefused",
    "JobState",
    "PREVIEW_VALIDITY_SECONDS",
    "REAPER_INTERVAL_SECONDS",
    "RESULT_RETENTION_DAYS",
    "ReconciliationJobService",
    "StaleCode",
    "blocked_by_running_apply",
    "folder_unselected",
    "issue_counts_from",
    "mint_preview_nonce",
    "parse_preview_nonce",
    "preview_not_confirmable",
    "queue_full",
    "request_key",
    "scope_fingerprint",
    "snapshot_absent",
]
