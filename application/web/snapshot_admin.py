"""R-40 and R-41: what has been submitted, and which folder it will be read from.

Two use cases, and the split between them is the accepted separation of duties
the plan states in as many words: **a Platform Administrator alone cannot apply
an import**, and a Council member alone cannot choose the folder. Selecting a
folder is an operational act; applying an import is a game-policy one. So R-41 is
administrator-only and R-42/R-46 refuse an administrator who is not also Council,
and neither capability can be converted into the other by holding the object the
other one needs.

## The invalidation is the interesting half of R-41

Selecting a folder **atomically invalidates every non-terminal job and every
completed-but-unconfirmed preview for that snapshot**, in the same transaction
that writes the selection. Not afterwards, and not by a sweep: a folder change
that left an outstanding preview confirmable for even one request is the exact
gap the mandatory test names — *"an administrator folder/profile change
invalidates an existing Council preview, and Council confirmation displays the
exact changed scope before a new apply"*.

The invalidation is expressed as a state transition with a `stale_reason`, so the
Council member polling that job sees `folder_changed` and is told what moved,
rather than seeing a job that silently stopped being confirmable.

## Nothing here parses an artifact

R-40 renders from the immutable `foundry_snapshots` row and the durable job rows.
R-41 validates the chosen folder against `selected_folder_ids`, which the
submission already recorded. Neither reads a byte of the stored artifact, because
both are page-load-latency paths and the parse is the ten seconds the whole
package exists to move off the request.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.web.errors import RefusalCode, WebRefusal
from application.web.jobs import (
    DEFAULT_FOLDER_PATH,
    JobKind,
    StaleCode,
    snapshot_absent,
)
from application.web.pagination import Page, decode, encode
from application.web.view_models import (
    ACTOR_NAME_BOUND,
    CHARACTER_LONG_NAME_BOUND,
    DISCORD_NAME_BOUND,
    FOLDER_CHOICE_BOUND,
    ISSUE_COUNT_BOUND,
    SNAPSHOT_ROW_BOUND,
    Actor,
    Correlation,
    FolderChoice,
    ImportResultView,
    Instant,
    IssueCount,
    JobStamp,
    SafeText,
    SnapshotListView,
    SnapshotRow,
    SnapshotStamp,
    bounded_tuple,
)

#: The cursor scope for R-40's listing. Scoping is what stops a cursor minted for
#: one listing being replayed into another (N-64).
SNAPSHOT_CURSOR_SCOPE = "p3.3:snapshots"


class SnapshotAdminService:
    """R-40's read and R-41's mutation, over one connection and one transaction."""

    __slots__ = ("_snapshots", "_jobs", "_audit", "_job_service", "_cursor_key")

    def __init__(self, *, snapshots, jobs, audit, job_service, cursor_key) -> None:
        self._snapshots = snapshots
        self._jobs = jobs
        self._audit = audit
        self._job_service = job_service
        self._cursor_key = cursor_key

    # -- R-40 --------------------------------------------------------------
    def snapshot_list(
        self,
        *,
        context,
        cursor_token: str | None,
        csrf_token: str,
        preview_nonce: str,
        size: int,
    ) -> SnapshotListView:
        """VM-14. Council **and** administrator: the administrator needs it to
        choose a folder, and the Council member needs it to preview.

        `can_select_folder` and `can_preview` are rendering hints computed from
        the capability this request already resolved. They make the page honest;
        they do not make it safe. R-41 and R-42 refuse regardless, and the matrix
        tests prove it by issuing those requests without ever fetching this page.

        Listed: snapshots that have **not** been applied, newest first, which is
        the working set — a snapshot whose import committed is history, and its
        receipt is R-47. `SnapshotRow.applied` is computed rather than hardcoded
        `False`, so a snapshot applied between two page loads reads correctly and
        a later widening of this filter needs no view-model change.

        `preview_nonce` arrives from the caller for the same reason `csrf_token`
        does: it is a fact about **this HTTP render**, minted at the composition
        boundary that knows a response is being produced, so this method stays a
        deterministic query over the rows it read. It is placed on the view
        unchanged and never consulted here — R-42 is where a submitted nonce
        means anything.
        """
        context.require_guild_member()
        if not (context.guild_council or context.platform_administrator):
            raise WebRefusal(RefusalCode.INSUFFICIENT_CAPABILITY, status=403)

        position = decode(
            self._cursor_key, cursor_token, scope=SNAPSHOT_CURSOR_SCOPE, arity=2
        )
        rows = self._snapshots.unapplied_page(position=position, size=size)
        page = Page.of(
            rows,
            size=size,
            key=self._cursor_key,
            scope=SNAPSHOT_CURSOR_SCOPE,
            position=lambda row: (row["received_at"].isoformat(), str(row["id"])),
        )
        identifiers = [row["id"] for row in page.rows]
        selections = self._snapshots.folder_selections(identifiers)
        observed = self._snapshots.observed_folder_paths(identifiers)
        stamps = self._jobs.latest_stamps(identifiers)
        applied = self._snapshots.applied_snapshot_ids(identifiers)

        snapshots, _ = bounded_tuple(
            (
                self._row(row, selections, observed, stamps, applied)
                for row in page.rows
            ),
            SNAPSHOT_ROW_BOUND,
        )
        return SnapshotListView(
            state="ready" if snapshots else "empty",
            snapshots=snapshots,
            cursor=page.cursor,
            can_select_folder=bool(context.platform_administrator),
            can_preview=bool(context.guild_council),
            csrf_token=csrf_token,
            preview_nonce=preview_nonce,
        )

    def _row(self, row, selections, observed, stamps, applied) -> SnapshotRow:
        snapshot_id = row["id"]
        exported = tuple(row["selected_folder_ids"] or ())
        paths = observed.get(snapshot_id, {})
        choices, _ = bounded_tuple(
            (
                self._folder_choice(
                    folder_id=folder_id,
                    paths=paths,
                    lone_folder=len(exported) == 1,
                    actor_count=row["actor_count"],
                )
                for folder_id in sorted(exported)
            ),
            FOLDER_CHOICE_BOUND,
        )
        selection = selections.get(snapshot_id)
        selected = None
        if selection is not None:
            selected = self._folder_choice(
                folder_id=selection["folder_id"],
                paths={selection["folder_id"]: selection["folder_path"]},
                lone_folder=len(exported) == 1,
                actor_count=row["actor_count"],
            )
        stamp = stamps.get(snapshot_id)
        return SnapshotRow(
            snapshot_id=snapshot_id,
            # Twelve hex characters, for display. Anything that must *identify* a
            # snapshot uses the full value server-side.
            checksum_short=row["checksum"][:12],
            checksum_full=row["checksum"],
            world_id=row["world_id"],
            world_title=SafeText.bounded(row["world_title"], CHARACTER_LONG_NAME_BOUND),
            core_version=row["core_version"],
            system_id=row["system_id"],
            system_version=row["system_version"],
            actor_count=row["actor_count"],
            size_bytes=row["size_bytes"],
            exported_at=Instant.of(row["exported_at"]),
            received_at=Instant.of(row["received_at"]),
            received_via=row["received_via"],
            selected_folder=selected,
            selectable_folders=choices,
            applied=snapshot_id in applied,
            latest_job=(
                JobStamp(
                    job_id=stamp["id"],
                    kind=stamp["kind"],
                    state=stamp["state"],
                    updated_at=Instant.of(stamp["updated_at"]),
                )
                if stamp
                else None
            ),
        )

    def _folder_choice(
        self, *, folder_id: str, paths, lone_folder: bool, actor_count: int
    ) -> FolderChoice:
        """One folder, said honestly.

        A path the platform has never observed is not invented. See
        `FolderChoice.path_observed`.
        """
        path = paths.get(folder_id)
        return FolderChoice(
            folder_id=folder_id,
            folder_path=SafeText.bounded(path or folder_id, ACTOR_NAME_BOUND),
            # The snapshot's own total is the folder's count exactly when the
            # snapshot exports one folder. Otherwise the platform has not counted
            # per folder and says zero rather than apportioning a guess.
            actor_count=actor_count if lone_folder else 0,
            is_default=(path == DEFAULT_FOLDER_PATH) or (path is None and lone_folder),
            path_observed=path is not None,
        )

    # -- R-41 --------------------------------------------------------------
    def select_folder(
        self,
        *,
        context,
        snapshot_id: UUID,
        folder_id: str,
        now: datetime,
    ) -> tuple[UUID, ...]:
        """Set the Actor folder, and invalidate what it invalidates. One transaction.

        Returns the ids of the jobs that were made `stale`, so the caller can
        record how much was invalidated without querying for it again.

        The folder is validated against `selected_folder_ids` — the exported set
        the submission recorded — rather than trusted. A folder id the artifact
        does not export is refused as input: an import from a folder that is not
        in the bundle is not a thing that could succeed later, and accepting it
        here would move the refusal to a worker ten seconds in.
        """
        context.require_platform_administrator()
        snapshot = self._snapshots.snapshot(snapshot_id)
        if snapshot is None:
            raise snapshot_absent()
        exported = tuple(snapshot["selected_folder_ids"] or ())
        if folder_id not in exported:
            raise WebRefusal(RefusalCode.OBJECT_NOT_REACHABLE, status=422)

        previous = self._snapshots.folder_selection(snapshot_id)
        if previous is not None and previous["folder_id"] == folder_id:
            # Re-selecting the folder that is already selected changes nothing
            # and invalidates nothing. Recording it as a change would make a
            # refresh of the form look like an administrator action, and would
            # invalidate a Council member's outstanding preview for no reason.
            return ()

        observed = self._snapshots.observed_folder_paths([snapshot_id]).get(
            snapshot_id, {}
        )
        correlation_id = uuid4()
        self._snapshots.set_folder_selection(
            snapshot_id=snapshot_id,
            folder_id=folder_id,
            folder_path=observed.get(folder_id) or folder_id,
            account_id=context.account_id,
            correlation_id=correlation_id,
            now=now,
        )
        invalidated = self._job_service.invalidate_for_snapshot(
            snapshot_id=snapshot_id, reason=StaleCode.FOLDER_CHANGED, now=now
        )
        self._audit.record(
            AuditEvent(
                action="snapshot.folder_selected",
                entity_type="foundry_snapshot",
                entity_id=str(snapshot_id),
                source=AuditSource.WEB,
                actor_capability=ActorCapability.PLATFORM_ADMINISTRATOR,
                actor_platform_account_id=context.account_id,
                correlation_id=correlation_id,
                payload={
                    "checksum": snapshot["checksum"],
                    "folder_id_before": (previous or {}).get("folder_id"),
                    "folder_id_after": folder_id,
                    # A count, not a list: how many outstanding jobs a folder
                    # change invalidated is the operational fact; which ones is
                    # in each job's own row.
                    "invalidated_jobs": len(invalidated),
                },
            )
        )
        return invalidated


__all__ = [
    "SNAPSHOT_CURSOR_SCOPE",
    "ImportReceiptService",
    "SnapshotAdminService",
]


class ImportReceiptService:
    """R-47: the immutable receipt of one applied or refused import.

    Council **and** administrator, because plan §6.4 makes import and
    reconciliation audit history visible to both. Neither can change it: the row
    is append-only in the database and this service exposes no write.

    **No download of the artifact exists anywhere in the inventory.** Audit
    visibility does not by itself grant permission to download the raw artifact,
    and the receipt therefore names a checksum rather than offering a link.
    """

    __slots__ = ("_snapshots", "_accounts", "_jobs")

    def __init__(self, *, snapshots, accounts, jobs) -> None:
        self._snapshots = snapshots
        self._accounts = accounts
        self._jobs = jobs

    def receipt(self, *, context, import_id: UUID) -> ImportResultView:
        context.require_guild_member()
        if not (context.guild_council or context.platform_administrator):
            raise WebRefusal(RefusalCode.INSUFFICIENT_CAPABILITY, status=403)
        record = self._snapshots.import_record(import_id)
        if record is None:
            raise snapshot_absent()
        snapshot = self._snapshots.snapshot(record["snapshot_id"])
        summary = record["summary"] or {}
        account_id = record["actor_account_id"]
        labels = self._accounts.labels_for([account_id])
        actor = Actor(
            account_id=account_id,
            label=SafeText.bounded(
                labels.get(account_id)
                or (
                    f"Account {str(account_id)[:8]}"
                    if account_id is not None
                    # A bootstrap import has no interactive user at all, and
                    # migration 0004 records why. Naming it as the platform is
                    # honest; naming it as nobody would render an empty cell a
                    # reader would read as a defect.
                    else "The platform (supervised bootstrap)"
                ),
                DISCORD_NAME_BOUND,
            ),
            capability=ActorCapability(record["actor_capability"]),
        )
        counts, _ = bounded_tuple(
            (
                IssueCount(code=str(code), severity="warning", count=1)
                for code in (summary.get("issue_codes") or [])
            ),
            ISSUE_COUNT_BOUND,
        )
        # A retry presents itself as the original receipt. `duplicate_of` is the
        # job that confirmed this import when a later confirmation resolved to
        # the same durable effect, so the view **says** a retry happened rather
        # than implying a second import did.
        duplicate_of = None
        job = self._jobs.by_request_key(record["request_key"])
        if job is not None and job["parent_job_id"] is not None:
            duplicate_of = job["parent_job_id"]
        return ImportResultView(
            state="ready",
            import_id=record["id"],
            status=record["status"],
            mode=record["mode"],
            actor=actor,
            capability=ActorCapability(record["actor_capability"]),
            snapshot=SnapshotStamp(
                checksum_short=(snapshot or {}).get("checksum", "")[:12],
                world_id=(snapshot or {}).get("world_id", ""),
                exported_at=Instant.of((snapshot or {})["exported_at"])
                if snapshot
                else Instant("", ""),
            ),
            checksum_full=(snapshot or {}).get("checksum", ""),
            folder=FolderChoice(
                folder_id=record["folder_id"],
                folder_path=SafeText.bounded(record["folder_path"], ACTOR_NAME_BOUND),
                actor_count=int(summary.get("actors", 0)),
                is_default=record["folder_path"] == DEFAULT_FOLDER_PATH,
            ),
            profile_version=record["profile_version"],
            created_count=record["created_count"],
            updated_count=record["updated_count"],
            warning_count=record["warning_count"],
            issue_counts=counts,
            occurred_at=Instant.of(record["occurred_at"]),
            correlation=Correlation(record["correlation_id"]),
            duplicate_of=duplicate_of,
        )
