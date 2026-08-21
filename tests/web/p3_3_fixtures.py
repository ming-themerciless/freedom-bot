"""Seeding helpers for the P3.3 suites: snapshots, folder selections and jobs.

One place where "a snapshot awaiting a folder", "a completed preview" or "a job
whose third lease has expired" becomes rows, because several suites need the same
states and building them per module would be several chances to build one
slightly wrong — a `completed` job with no result row would make a confirmation
test pass for the wrong reason, and the check constraint would not even allow it.

**Nothing here goes through a route.** These are the *arrangements*; the tests
that prove how a state is reached go through R-41, R-42, R-45, R-46 and the
worker. Seeding through the routes would make every case also a test of the route
before the one it is about.

**No real player, Actor, guild or credential appears anywhere.** The snapshots
are the synthetic Phase 2 bundles from `tests/foundry_fixtures.py`, and the
checksums are of those bytes.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import insert, text

from adapters.artifacts.filesystem import FilesystemArtifactStore, TrustedAncestors
from adapters.database.tables import (
    foundry_snapshots,
    reconciliation_job_results,
    reconciliation_jobs,
    snapshot_folder_selections,
    snapshot_imports,
)
from application.web.jobs import JobKind, JobState, scope_fingerprint
from application.web.view_models import PREVIEW_NONCE_BOUND
from domain.foundry import OBSERVED_DEPLOYMENT
from tests import foundry_fixtures as fx

#: The URL/form-safe alphabet `secrets.token_urlsafe` emits, and therefore the
#: only characters R-42 admits.
_NONCE_ALPHABET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"
)

#: The folder path the synthetic bundle's `Characters (active)` folder resolves
#: to. Not `/actors/Characters (active)`: that is the *deployment's* contracted
#: default, and the fixture tree is synthetic on purpose — a test that used the
#: production path would be asserting against a value it invented.
FIXTURE_FOLDER_PATH = "/Characters/Characters (active)"

PROFILE_VERSION_UNSET = "0000-00-00.0"


def preview_nonce(label: str) -> str:
    """A submitted R-42 `nonce` of the accepted shape (VM-14), named for its case.

    R-42 admits exactly what R-40 mints: `PREVIEW_NONCE_BOUND` characters from
    `[A-Za-z0-9_-]`. A test that submitted `nonce=double-click` was therefore
    testing the refusal path, and before the boundary enforced the contract it was
    testing nothing at all — which is how the missing validation stayed invisible.

    `mint_preview_nonce()` is the right value when a test only needs *a* nonce.
    This is for the cases that need a **named** one: the same label twice is the
    same request identity, so a double-click stays a double-click, and two labels
    stay two deliberate previews. The label is folded into the accepted alphabet
    and padded to the accepted width, so it stays legible in a failure message.
    """
    safe = "".join(
        character if character in _NONCE_ALPHABET else "-" for character in label
    )
    return (safe + "-" * PREVIEW_NONCE_BOUND)[:PREVIEW_NONCE_BOUND]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def open_artifact_store(
    root: Path, ancestors: TrustedAncestors
) -> FilesystemArtifactStore:
    """The one way a P3.3 test builds a real artifact store, ready to use.

    Added by the 2026-08-18 second migration-rollback remediation. Every P3.3
    suite previously wrote `FilesystemArtifactStore(artifact_root)` itself, which
    took the **production** unbounded ancestor walk and made the suite's result a
    property of the host's `/`, `/tmp` and `/opt` rather than of the code — see
    the `bounded_ancestors` fixture in `tests/web/conftest.py` for the failure
    that found it.

    The store is otherwise the production one: the real ownership, mode, symlink,
    hard-link and descriptor-anchoring checks, and `ensure_ready()` run here so a
    misconfigured root still fails loudly rather than at the first `store()`.

    **The ceiling is asserted to be a real ancestor of this root.** `TrustedAncestors`
    stops the walk when it *reaches* the ceiling, so a ceiling that is not on the
    path above `root` bounds nothing and the walk silently reaches `/` — the safe
    direction to fail, but also exactly the "hermetic" fixture that quietly is not.
    Comparing resolved paths, because the store resolves its own root before
    walking.
    """
    ceiling = ancestors.ceiling
    assert ceiling is not None, (
        "an ordinary P3.3 test must bound the ancestor walk; only the dedicated "
        "ancestor-security tests use the production unbounded rule"
    )
    resolved_root = root.resolve()
    assert Path(ceiling).resolve() in resolved_root.parents, (
        f"the ancestor ceiling {ceiling} is not above the artifact root {root}, "
        "so it bounds nothing and the walk would reach / after all"
    )
    store = FilesystemArtifactStore(root, ancestors=ancestors)
    store.ensure_ready()
    return store


def snapshot_bytes(**kwargs) -> bytes:
    """One synthetic bundle's canonical bytes, and therefore one checksum."""
    return fx.encode(fx.bundle(**kwargs))


def seed_snapshot(
    connection,
    *,
    payload: bytes | None = None,
    received_by_account_id: UUID | None = None,
    folder_ids: tuple[str, ...] = (fx.ACTIVE_FOLDER_ID,),
    actor_count: int = 1,
    received_at: datetime | None = None,
) -> tuple[UUID, str]:
    """One `foundry_snapshots` row, as the submission endpoint would have written it.

    Returns `(snapshot_id, checksum)`. The checksum is the SHA-256 of the bytes,
    computed here rather than invented, so a worker test that loads the artifact
    from a real store finds the same identity the row claims.
    """
    import hashlib

    data = payload if payload is not None else snapshot_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    snapshot_id = uuid4()
    connection.execute(
        insert(foundry_snapshots).values(
            id=snapshot_id,
            checksum=checksum,
            size_bytes=len(data),
            schema_version=1,
            exporter_id="freedom-blades-export",
            exporter_version="1.0.2",
            exported_at=datetime(2026, 8, 2, 9, 15, tzinfo=timezone.utc),
            world_id=OBSERVED_DEPLOYMENT.world_id,
            world_title="The Guild",
            core_version=OBSERVED_DEPLOYMENT.core_version,
            system_id=OBSERVED_DEPLOYMENT.system_id,
            system_version=OBSERVED_DEPLOYMENT.system_version,
            actor_count=actor_count,
            selected_folder_ids=list(folder_ids),
            artifact_location=f"artifacts/{checksum}",
            received_at=received_at or utcnow(),
            received_by_account_id=received_by_account_id,
            received_via="operator",
            correlation_id=uuid4(),
        )
    )
    return snapshot_id, checksum


def select_folder(
    connection,
    *,
    snapshot_id: UUID,
    account_id: UUID,
    folder_id: str = fx.ACTIVE_FOLDER_ID,
    folder_path: str = FIXTURE_FOLDER_PATH,
) -> UUID:
    """The administrator's folder choice, seeded directly.

    Written here rather than through R-41 because the cases that *use* a selected
    folder are not the cases that prove how one is made. Those go through the
    route, and they also prove the invalidation R-41 performs in the same
    transaction.
    """
    selection_id = uuid4()
    connection.execute(
        insert(snapshot_folder_selections).values(
            id=selection_id,
            snapshot_id=snapshot_id,
            folder_id=folder_id,
            folder_path=folder_path,
            selected_by_account_id=account_id,
            selected_at=utcnow(),
            correlation_id=uuid4(),
            version=1,
        )
    )
    return selection_id


def seed_import(
    connection,
    *,
    snapshot_id: UUID,
    account_id: UUID,
    checksum: str,
    status: str = "applied",
    folder_id: str = fx.ACTIVE_FOLDER_ID,
    folder_path: str = FIXTURE_FOLDER_PATH,
    profile_version: str = "2026-08-09.1",
    request_key: str | None = None,
) -> UUID:
    """One `snapshot_imports` row, as the Phase 2 apply service would have written it.

    Append-only, so there is no update helper and no delete helper — a
    correction is a compensating import, which is the plan's rule for the whole
    platform and is why R-47 renders a receipt rather than a form.
    """
    import_id = uuid4()
    connection.execute(
        insert(snapshot_imports).values(
            id=import_id,
            snapshot_id=snapshot_id,
            folder_id=folder_id,
            folder_path=folder_path,
            profile_version=profile_version,
            request_key=request_key or f"seeded:apply:{import_id}",
            operation_digest="a" * 64,
            status=status,
            mode="council",
            actor_account_id=account_id,
            actor_capability="guild_council",
            created_count=1,
            updated_count=0,
            warning_count=0,
            summary={
                "snapshot_checksum": checksum,
                "folder_id": folder_id,
                "folder_path": folder_path,
                "profile_version": profile_version,
                "exporter": "freedom-blades-export 1.0.2",
                "canonical_encoding": True,
                "actors": 1,
                "mapped": 0,
                "unmapped": 1,
                "blocked": 0,
                "absent": 0,
                "errors": 0,
                "warnings": 0,
                "issue_codes": [],
                "fields_differing": [],
                "stale_platform_display_names": 0,
                "legacy_authority_deferred": {},
            },
            occurred_at=utcnow(),
            correlation_id=uuid4(),
        )
    )
    return import_id


def seed_job(
    connection,
    *,
    snapshot_id: UUID,
    account_id: UUID,
    checksum: str,
    kind: JobKind = JobKind.PREVIEW,
    state: JobState = JobState.QUEUED,
    profile_version: str = "2026-08-09.1",
    folder_id: str = fx.ACTIVE_FOLDER_ID,
    folder_path: str = FIXTURE_FOLDER_PATH,
    attempts: int = 0,
    lease_owner: str | None = None,
    lease_expires_at: datetime | None = None,
    request_key: str | None = None,
    parent_job_id: UUID | None = None,
    aggregate_versions=None,
    queued_at: datetime | None = None,
    result_id: UUID | None = None,
    failure_code: str | None = None,
    stale_reason: str | None = None,
) -> UUID:
    """One `reconciliation_jobs` row in a chosen state.

    The check constraints are **not** worked around: a `running` row is given a
    lease, a terminal row a `finished_at`, a `completed` row a `result_id`, and a
    caller that asks for an impossible combination gets the database's refusal
    rather than a helper that quietly repairs it. That is the point — the
    constraints are the design, and a fixture that could bypass them would let a
    test assert a state production cannot reach.
    """
    job_id = uuid4()
    now = utcnow()
    terminal = state in (
        JobState.COMPLETED,
        JobState.STALE,
        JobState.FAILED,
        JobState.CANCELLED,
    )
    connection.execute(
        insert(reconciliation_jobs).values(
            id=job_id,
            kind=kind.value,
            state=state.value,
            snapshot_id=snapshot_id,
            folder_id=folder_id,
            profile_version=profile_version,
            scope_fingerprint=scope_fingerprint(
                checksum=checksum,
                folder_id=folder_id,
                folder_path=folder_path,
                profile_version=profile_version,
                aggregate_versions=aggregate_versions,
            ),
            requested_by_account_id=account_id,
            requested_capability="guild_council",
            request_key=request_key or f"seeded:{kind.value}:{job_id}",
            parent_job_id=parent_job_id,
            attempts=attempts,
            lease_owner=lease_owner if state is JobState.RUNNING else None,
            lease_expires_at=(
                lease_expires_at if state is JobState.RUNNING else None
            ),
            heartbeat_at=now if state is JobState.RUNNING else None,
            queued_at=queued_at or now,
            started_at=now if state is not JobState.QUEUED else None,
            finished_at=now if terminal else None,
            stale_reason=(
                stale_reason or "folder_changed" if state is JobState.STALE else None
            ),
            failure_code=(
                failure_code or "internal" if state is JobState.FAILED else None
            ),
            result_id=result_id,
            correlation_id=uuid4(),
            version=1,
        )
    )
    return job_id


def complete_preview(
    connection,
    *,
    snapshot_id: UUID,
    account_id: UUID,
    checksum: str,
    preview_token: str = "seeded-preview-token",
    folder_id: str = fx.ACTIVE_FOLDER_ID,
    folder_path: str = FIXTURE_FOLDER_PATH,
    profile_version: str = "2026-08-09.1",
    produced_at: datetime | None = None,
    aggregate_versions=(("11111111-1111-4111-8111-111111111111", 0),),
    summary_overrides: dict | None = None,
    blocked_entries: list | None = None,
) -> tuple[UUID, UUID]:
    """A `completed` preview and its durable result, in one transaction.

    Returns `(job_id, result_id)`. Built in the order the worker builds it —
    result first, then the job naming it — because `CHECK ((state = 'completed')
    = (result_id IS NOT NULL))` admits no other order.
    """
    job_id = seed_job(
        connection,
        snapshot_id=snapshot_id,
        account_id=account_id,
        checksum=checksum,
        state=JobState.RUNNING,
        lease_owner="fixture:seed",
        lease_expires_at=utcnow() + timedelta(seconds=60),
        attempts=1,
        folder_id=folder_id,
        folder_path=folder_path,
        profile_version=profile_version,
        aggregate_versions=aggregate_versions,
    )
    moment = produced_at or utcnow()
    summary = {
        "checksum": checksum,
        "folder_id": folder_id,
        "folder_path": folder_path,
        "profile_version": profile_version,
        "exporter": "freedom-blades-export 1.0.2",
        "canonical_encoding": True,
        "actors": 1,
        "mapped": 0,
        "unmapped": 1,
        "blocked": 0,
        "absent": 0,
        "errors": 0,
        "warnings": 0,
        "would_create": 1,
        "would_update": 0,
        "issue_counts": [],
        "preview_token": preview_token,
    }
    summary.update(summary_overrides or {})
    result_id = uuid4()
    connection.execute(
        insert(reconciliation_job_results).values(
            id=result_id,
            job_id=job_id,
            summary=summary,
            blocked_entries=blocked_entries or [],
            produced_at=moment,
            expires_at=moment + timedelta(days=30),
        )
    )
    connection.execute(
        text(
            "UPDATE reconciliation_jobs SET state = 'completed', result_id = :result, "
            "finished_at = :now, lease_owner = NULL, lease_expires_at = NULL, "
            "heartbeat_at = NULL, version = version + 1 WHERE id = :job"
        ),
        {"result": result_id, "now": moment, "job": job_id},
    )
    return job_id, result_id


def expire_lease(connection, job_id: UUID, *, seconds: int = 1) -> None:
    """Move a running job's lease into the past.

    The reaper's own predicate is `lease_expires_at < now()`, so a test that
    wanted an expired lease could either wait sixty seconds or move the clock in
    the row. Moving the row is the honest one: it exercises the **real** reaper
    statement against real PostgreSQL rather than a shortened lease that would
    also be testing a configuration nobody runs.
    """
    connection.execute(
        text(
            "UPDATE reconciliation_jobs SET lease_expires_at = now() - "
            "make_interval(secs => :seconds) WHERE id = :job"
        ),
        {"seconds": seconds, "job": job_id},
    )


def job_row(connection, job_id: UUID):
    return (
        connection.execute(
            text("SELECT * FROM reconciliation_jobs WHERE id = :id"), {"id": job_id}
        )
        .mappings()
        .one()
    )


#: Emptied with **one** `TRUNCATE`, and every part of that is forced.
#:
#: `foundry_snapshots` and `snapshot_imports` are append-only: migration 0002's
#: trigger refuses `DELETE` on them for the schema owner too, and deliberately
#: does not cover `TRUNCATE` — the asymmetry that lets a disposable test database
#: be reset while the application can never empty history.
#:
#: `TRUNCATE` is **not** `CASCADE`, so every table referencing one of them has to
#: be named in the same statement or PostgreSQL refuses. That is the constraint
#: doing its job rather than a nuisance: a cascade would silently empty whatever
#: a later migration attached to these tables, which is the opposite of what a
#: fixture that establishes a known baseline is for.
#:
#: The two job tables reference **each other**, and naming both in one statement
#: satisfies the cycle in either direction — which is also why the cycle needs no
#: `ON DELETE` weakening anywhere.
#: `external_actor_mappings` is in the list although it is a P3.2/Phase 2 table:
#: it references `foundry_snapshots` too, and `TRUNCATE` refuses unless every
#: referencing table is named. Emptying it here is safe and correct — an Actor
#: mapping whose snapshot has been removed is a dangling row, which is exactly
#: what the reconciliation reports as an issue.
_P3_3_TABLES = (
    "reconciliation_job_results",
    "reconciliation_jobs",
    "snapshot_folder_selections",
    "snapshot_imports",
    "external_actor_mappings",
    "foundry_snapshots",
)


def clean_p3_3_tables(connection) -> None:
    """Return the import surface to the state the migration left it in."""
    connection.execute(text(f"TRUNCATE TABLE {', '.join(_P3_3_TABLES)}"))


__all__ = [
    "preview_nonce",
    "FIXTURE_FOLDER_PATH",
    "clean_p3_3_tables",
    "complete_preview",
    "expire_lease",
    "job_row",
    "open_artifact_store",
    "seed_import",
    "seed_job",
    "seed_snapshot",
    "select_folder",
    "snapshot_bytes",
    "utcnow",
]
