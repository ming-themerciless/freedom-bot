"""Executing one claimed job: the preview, the apply, and the durable result.

Neither of the two paths below reimplements anything. A preview is
`SnapshotImportService.preview` and an apply is `SnapshotImportService.apply` —
the Phase 2 services that already know how to parse an immutable artifact,
reconcile it, bind what they reconciled, and commit atomically under
`uq_snapshot_imports_applied_input` and `snapshot_imports.request_key`. What this
module adds is the durable *record* of a run, bounded to counts and codes.

## What a result may contain, and the one exception

Delivery plan §8.9: results are bounded summaries and references. So the stored
summary holds counts, closed-vocabulary issue codes, the checksum, the folder
identity and the profile version, and the artifact stays in the restricted store
the Phase 2 package built, reachable by no route.

The single exception is `blocked_entries`: an Actor's external id, its display
name, one issue code and the character ids it might be. It is the minimum a
Council member needs to resolve a blocked create-candidate, it is Council-only,
it is capped at 50, and every other Actor field is dropped. **The issue
*messages* are dropped here** — folded into `{code, severity, count}` triples at
the point the durable record is built — rather than filtered at rendering, so
"artifact text never reaches a response" is a property of the row instead of a
property of a template nobody forgot to change.

## The effect is fenced where it commits, not where it is published

`_apply` builds a `JobLeaseFence` from the job's id and **this claim's** lease
owner and hands it to `SnapshotImportService.apply`, which runs it as the last
statement of the transaction that commits the effect. A Python cancellation
check before the call — which is all this module had before the 2026-08-18
remediation — leaves the entire apply as a window in which the job can be
cancelled, abandoned or reaped while the effect commits anyway. The fence closes
that window in the only place it can be closed: inside the effect's own
transaction. See `application/worker/fence.py`.

The Python check is kept, because refusing before ten seconds of parsing is
cheaper than refusing after it. It is an optimisation now, not a control.

## Staleness is checked where the write happens

The apply recomputes the scope fingerprint from the artifact in hand and the
database as it stands *now*, inside its own attempt, and compares it to the one
the job carries — which the confirmation inherited from the preview a Council
member actually read. One equality comparison. A mismatch applies nothing and
transitions the job to `stale` with the reason that differs, so the Council
member is told what moved rather than that something did.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from application.artifacts import ArtifactNotStored, ArtifactStorageError
from application.authorization import NotAuthorizedError
from application.foundry.import_service import ImportRefused
from application.foundry.parser import SnapshotRejected
from application.foundry.reconciliation import ActorOutcome
from application.web.jobs import (
    FailureCode,
    JobKind,
    StaleCode,
    issue_counts_from,
    scope_fingerprint,
)
from application.web.view_models import BLOCKED_ENTRY_BOUND, CANDIDATE_CHARACTER_BOUND
from application.worker.fence import JobLeaseFence, PendingEffectResult

#: §3.2's bound on an Actor display name, applied at the point the name is
#: **stored** rather than at the point it is rendered. A bound applied only at
#: render leaves the untruncated value in the database for the next reader.
ACTOR_NAME_BOUND = 120


class Cancelled(Exception):
    """The job's cancellation was observed at a heartbeat. Nothing was published."""


@dataclass(frozen=True, slots=True)
class Executed:
    """What one successful attempt produced, before it is committed.

    `fingerprint` is `None` for an apply: an apply does not rewrite the scope it
    was confirmed against, because that scope is the thing the confirmation
    means.
    """

    summary: dict[str, Any]
    blocked_entries: list[dict[str, Any]]
    fingerprint: bytes | None


@dataclass(frozen=True, slots=True)
class Stale:
    """The scope moved. Nothing was applied, and the reason names what moved."""

    reason: StaleCode


@dataclass(frozen=True, slots=True)
class Failed:
    """A terminal, closed-vocabulary failure.

    `deterministic` is what stops a refusal that would recur on every attempt
    from consuming three of them: `parse_refused` and `artifact_unavailable` are
    facts about the artifact, and retrying them three times is thirty seconds of
    work to reach the conclusion the first attempt already had.
    """

    code: FailureCode
    deterministic: bool


class JobExecutor:
    """Runs one claimed job. Holds no lease and writes no job state.

    Deliberately separate from the runtime that owns the lease: this object knows
    how to do the work and what the work produced, and the runtime knows who may
    publish it. Mixing the two would make it possible to write a verdict without
    holding the lease that entitles you to.
    """

    __slots__ = (
        "_imports",
        "_artifacts",
        "_profile_version",
        "_fences",
        "_requester_subject",
        "_requester_account_id",
    )

    def __init__(
        self, *, imports, artifacts, profile_version: str, fences=None
    ) -> None:
        self._imports = imports
        self._artifacts = artifacts
        self._profile_version = profile_version
        #: How this executor builds the commit fence for an apply: a callable
        #: taking `(job_id, owner, pending_result)` and returning something with
        #: `hold()`. The pending result is what the fence makes durable alongside
        #: the effect, so a later recovery can publish it.
        #: Injected rather than constructed inline so a race test can wrap the
        #: real fence in explicit barriers and drive the interleaving
        #: deterministically, instead of sleeping and hoping.
        self._fences = fences or _default_fence
        #: Who an apply commits as: the Discord subject the authority is resolved
        #: from, and the platform account the row is attributed to. Both are read
        #: from the job's `requested_by_account_id` inside the worker's own
        #: transaction, and neither is taken from anything a browser sent. `None`
        #: until `for_requester` binds them, which the runtime does for every job
        #: it hands over.
        self._requester_subject: int | None = None
        self._requester_account_id = None

    def execute(
        self, *, job, snapshot, selection, cancelled, owner, already_applied=None
    ) -> object:
        """Run `job`, returning `Executed`, `Stale` or `Failed`.

        `cancelled` is a callable the runtime supplies; it is consulted at each
        boundary between phases, which is the "at its next heartbeat" of the
        cancellation contract expressed where a phase can actually stop.

        `already_applied` is this attempt's `snapshot_imports` row when its
        request key has already been spent. It is read by the runtime rather than
        looked up here, so this class holds no repository. Since the 2026-08-18
        effect-publication remediation no production path produces it — a job
        whose effect committed is published by `WorkerRuntime.recover()` and never
        requeued — and it is kept as the correct answer if such a row ever arises;
        see `WorkerRuntime._start`.

        `owner` is **this claim's** per-claim fencing token. It is required
        rather than optional: it is what an apply's commit fence proves at its
        commit boundary, and an executor that could run without one would be an
        executor able to commit an effect nothing entitles it to.
        """
        try:
            artifact = self._artifacts.load(snapshot["checksum"])
        except ArtifactNotStored:
            return Failed(code=FailureCode.ARTIFACT_UNAVAILABLE, deterministic=True)
        except ArtifactStorageError:
            # Unreadable rather than absent: also deterministic, because a store
            # that cannot read a checksum on this attempt will not read it on the
            # next one either. An operator fixes it; a retry does not.
            return Failed(code=FailureCode.ARTIFACT_UNAVAILABLE, deterministic=True)

        if cancelled():
            raise Cancelled()

        if selection is None or selection["folder_id"] != job["folder_id"]:
            # The administrator moved the folder while this job sat in the queue.
            # R-41 already transitioned it, but the check is repeated here because
            # the worker must not read a folder nobody currently selects.
            return Stale(reason=StaleCode.FOLDER_CHANGED)
        if self._profile_version != job["profile_version"]:
            return Stale(reason=StaleCode.PROFILE_VERSION_CHANGED)

        if job["kind"] == JobKind.PREVIEW.value:
            # A preview rolls its own transaction back and writes nothing, so it
            # has no effect to fence — which is also why the check constraint
            # added by migration 0012 forbids a preview an `effect_committed_at`.
            return self._preview(job, artifact, selection, cancelled)
        return self._apply(job, artifact, selection, cancelled, already_applied, owner)

    # -- preview -----------------------------------------------------------
    def _preview(self, job, artifact, selection, cancelled) -> object:
        try:
            preview = self._imports.preview(
                artifact,
                request_key=job["request_key"],
                folder_id=job["folder_id"],
            )
        except SnapshotRejected:
            return Failed(code=FailureCode.PARSE_REFUSED, deterministic=True)
        except ImportRefused:
            return Failed(code=FailureCode.PARSE_REFUSED, deterministic=True)
        if cancelled():
            raise Cancelled()

        binding = preview.binding
        return Executed(
            summary=_summary(
                preview,
                selection=selection,
                preview_token=binding.token(),
            ),
            blocked_entries=_blocked_entries(preview.report),
            # The preview's scope, **completed**: the aggregate versions this run
            # actually read, folded into the fingerprint an apply will be checked
            # against. Written in the same transaction as the result, so a
            # `completed` preview can never carry the `unobserved` scope.
            fingerprint=scope_fingerprint(
                checksum=binding.snapshot_checksum,
                folder_id=binding.folder_id,
                folder_path=binding.folder_path,
                profile_version=binding.profile_version,
                aggregate_versions=binding.aggregate_versions,
            ),
        )

    # -- apply -------------------------------------------------------------
    def _apply(
        self, job, artifact, selection, cancelled, already_applied, owner
    ) -> object:
        """Re-parse, re-check the scope, then call the existing apply service.

        The re-preview is not a second preview shown to anybody: it is how the
        binding an apply needs is rebuilt from the artifact in hand rather than
        carried across a queue, and it is the same call the Council member's
        preview made. Its `request_key` is **this apply's** key, because the
        binding's key is what `SnapshotImportService.apply` writes into
        `snapshot_imports.request_key` — which is the durable idempotency lookup.
        """
        try:
            preview = self._imports.preview(
                artifact,
                request_key=job["request_key"],
                folder_id=job["folder_id"],
            )
        except SnapshotRejected:
            return Failed(code=FailureCode.PARSE_REFUSED, deterministic=True)
        except ImportRefused:
            return Failed(code=FailureCode.PARSE_REFUSED, deterministic=True)
        if cancelled():
            raise Cancelled()

        binding = preview.binding
        current = scope_fingerprint(
            checksum=binding.snapshot_checksum,
            folder_id=binding.folder_id,
            folder_path=binding.folder_path,
            profile_version=binding.profile_version,
            aggregate_versions=binding.aggregate_versions,
        )
        # **The one equality comparison** schema §10.1 specifies — but not when
        # this attempt's own effect is what moved the scope.
        #
        # A crash between the commit and the state publication leaves the import
        # applied and the job claimable again. Re-running it re-previews against a
        # database that now contains the characters the first attempt created, so
        # the aggregate versions differ and the comparison would report
        # `aggregate_version_changed` — a job that says its scope moved when what
        # moved it was itself, and a Council member told nothing was applied when
        # something was.
        #
        # SM-05 states the rule the other way: *"the durable effect is fenced by
        # `uq_snapshot_imports_applied_input` and the request key, not by the
        # job's state. If the previous attempt had already committed, the retry
        # finds the existing import and returns it as a duplicate result."* So a
        # spent key goes straight to the import service, which resolves the
        # duplicate from the row the first attempt wrote — every field of the
        # receipt then answers for the instant that import committed, which is
        # finding B-1R's whole point.
        if already_applied is None and current != bytes(job["scope_fingerprint"]):
            return Stale(reason=_what_moved(job, binding, selection))

        # **Built before the apply, because the fence writes it.** The bounded
        # summary and blocked-entry list are everything the durable result needs
        # except the import's own identity and counts, and they are known from the
        # preview in hand. Handing them to the fence makes them commit with the
        # effect, so a process that dies before publishing leaves the publication
        # behind rather than taking it with it — which is what lets recovery finish
        # the job without re-running the attempt or spending one of N-43's three.
        produced = _summary(preview, selection=selection, preview_token=None)
        blocked = _blocked_entries(preview.report)

        try:
            outcome = self._imports.apply(
                artifact,
                preview,
                discord_user_id=self._requester_subject,
                # The stable account the import is **recorded** under (ADR 0010
                # D1). Authority is still resolved from the Discord identity
                # through the `AuthorizationPort`, at the commit; this only
                # decides which attribution column the row carries, so a P3.3
                # apply does not write the legacy-only shape the identity
                # migration is retiring.
                actor_account_id=self._requester_account_id,
                folder_id=selection["folder_id"],
                # The fence, run inside the transaction that commits the effect.
                # Everything above this line is a check that can be overtaken by
                # a cancellation, an abandonment or a reaper; this is the one
                # that cannot, because it and the effect are the same commit.
                commit_fence=self._fences(
                    job["id"],
                    owner,
                    PendingEffectResult(summary=produced, blocked_entries=blocked),
                ),
            )
        except NotAuthorizedError:
            # Council authority was revoked between the preview and this commit,
            # or the membership observation is too old to confirm it. The service
            # has already recorded one refused import row and one audit event
            # under the same correlation id, claiming no partial state.
            return Stale(reason=StaleCode.AUTHORIZATION_CHANGED)
        except ImportRefused as refusal:
            if refusal.args and "stale" in str(refusal.args[0]):
                return Stale(reason=StaleCode.SNAPSHOT_CHANGED)
            return Failed(code=FailureCode.PARSE_REFUSED, deterministic=True)

        # The same bounded summary the fence made durable, plus the half only the
        # committed import can answer for. `recovered_summary` in
        # `application/worker/recovery.py` merges the identical five keys from the
        # `snapshot_imports` row, so the result this attempt publishes and the
        # result a recovery would publish for it are the same document but for the
        # `recovered` marker.
        summary = dict(produced)
        summary.update(
            {
                "import_id": str(outcome.import_id),
                "duplicate": bool(outcome.duplicate),
                "created_count": outcome.created_count,
                "updated_count": outcome.updated_count,
                "warning_count": outcome.warning_count,
            }
        )
        return Executed(summary=summary, blocked_entries=blocked, fingerprint=None)

    def for_requester(self, subject: int | None, account_id=None) -> "JobExecutor":
        """This executor, bound to the identity the apply commits as.

        Returns `self` so the runtime's call site reads as one expression. One
        job is in flight per worker (N-41), so binding on the executor rather
        than threading a parameter through two identical signatures cannot make
        one job commit as another's requester.
        """
        self._requester_subject = subject
        self._requester_account_id = account_id
        return self


def _default_fence(job_id, owner: str, pending: PendingEffectResult) -> JobLeaseFence:
    """The production fence. `utcnow` is imported here to keep the module graph
    acyclic — the runtime imports this module, not the other way round."""
    from application.worker.runtime import utcnow

    return JobLeaseFence(job_id=job_id, owner=owner, clock=utcnow, pending=pending)


def _what_moved(job, binding, selection) -> StaleCode:
    """Name the changed component, from the recomputed binding.

    Checked in the order a Council member would ask: did somebody change the
    folder, did the platform change its profile, or did a character this import
    would touch move underneath it.
    """
    if binding.folder_id != job["folder_id"] or (
        selection is not None and selection["folder_id"] != binding.folder_id
    ):
        return StaleCode.FOLDER_CHANGED
    if binding.profile_version != job["profile_version"]:
        return StaleCode.PROFILE_VERSION_CHANGED
    return StaleCode.AGGREGATE_VERSION_CHANGED


def _summary(preview, *, selection, preview_token: str | None) -> dict[str, Any]:
    """The bounded, durable summary of one run. Counts and codes, nothing else.

    `preview_token` is the Phase 2 `PreviewBinding.token()` digest, stored so
    R-46 can compare the token a browser presents against the one this run
    produced. It lives in the summary rather than in a typed column because it is
    not a searchable fact — nothing filters or orders by it — and schema §10.2
    requires only that searchable facts be typed columns.
    """
    facts = preview.report.facts()
    summary: dict[str, Any] = {
        "checksum": facts.snapshot_checksum,
        "folder_id": facts.folder_id,
        "folder_path": facts.folder_path,
        "profile_version": facts.profile_version,
        "exporter": facts.exporter,
        "canonical_encoding": facts.canonical_encoding,
        "actors": facts.actors,
        "mapped": facts.mapped,
        "unmapped": facts.unmapped,
        "blocked": facts.blocked,
        "absent": facts.absent,
        "errors": facts.errors,
        "warnings": facts.warnings,
        "would_create": preview.would_create,
        "would_update": preview.report.count(ActorOutcome.MAPPED),
        # `{code, severity, count}` triples. The **message is dropped**, because
        # it quotes Actor data and the only reliable place to remove it is before
        # it is stored.
        "issue_counts": issue_counts_from(preview.report.issues),
    }
    if preview_token is not None:
        summary["preview_token"] = preview_token
    if selection is not None:
        summary["selected_folder_path"] = selection["folder_path"]
    return summary


def _blocked_entries(report) -> list[dict[str, Any]]:
    """At most 50 blocked create-candidates, with one bounded name each.

    Everything else about the Actor — every field, every value, every comparison
    — stays server-side. This is the whole of what crosses the boundary, and it
    crosses only to Council.
    """
    entries: list[dict[str, Any]] = []
    for entry in report.entries:
        if entry.outcome is not ActorOutcome.BLOCKED:
            continue
        issue = next(
            (issue.code for issue in report.issues if issue.actor_id == entry.actor_id),
            "unmapped_name_collision",
        )
        # The candidates a blocked entry names are the characters already
        # claiming this display name — which is what `unmapped_name_collision`
        # means and what a Council member has to choose between. Read from the
        # issue's own `character_id` rather than from a field on the entry,
        # because the reconciliation records the collision on the issues.
        candidates = [
            str(candidate.character_id)
            for candidate in report.issues
            if candidate.actor_id == entry.actor_id
            and candidate.character_id is not None
        ]
        if entry.character_id is not None and str(entry.character_id) not in candidates:
            candidates.insert(0, str(entry.character_id))
        entries.append(
            {
                "external_actor_id": str(entry.actor_id),
                # Bounded **here**, where it is stored. A bound applied only at
                # render leaves the untruncated value in the database for the
                # next reader.
                "display_name": (entry.actor_name or "")[:ACTOR_NAME_BOUND],
                "issue_code": issue,
                "candidate_character_ids": candidates[:CANDIDATE_CHARACTER_BOUND],
            }
        )
        if len(entries) >= BLOCKED_ENTRY_BOUND:
            break
    return entries


__all__ = ["Cancelled", "Executed", "Failed", "JobExecutor", "Stale"]
