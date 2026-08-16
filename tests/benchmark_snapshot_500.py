"""Executable 500-Actor synthetic benchmark harness and deterministic generator.

Remediated to satisfy all Codex review findings:
- Strict fail-closed dirty baseline refusal BEFORE any mutation.
- No generic TRUNCATE CASCADE into unchecked tables; explicit checked table list.
- Comprehensive database query assertions for character identities, mappings,
  snapshot provenance, audit records, prohibited game-state tables, and
  duplicate idempotency.
- Explicit and verified advisory lock release (fails if pg_advisory_unlock returns False).
- Complete table inventory restoration comparison (initial vs final table-for-table).
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import NullPool

from adapters.database.config import EXPECTED_DATABASES
from adapters.database.metadata import metadata
from adapters.database import tables  # noqa: F401 - registers tables on metadata
from adapters.database.safety import (
    ConnectionPolicy,
    UnsafeDatabaseTargetError,
    assert_disposable_target,
    verify_connected_unix_socket_target,
)
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from application.foundry.artifact import SnapshotArtifact, ingest_bytes
from application.foundry.import_service import (
    ImportOutcome,
    SnapshotImportService,
    SnapshotPreview,
)
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from domain.identity import DiscordUser
from tests import foundry_fixtures as fx
from tests.fakes import FakeAuthorization

ADVISORY_LOCK_KEY = 1129530869150000500
COUNCIL_USER = 4200000000000000001
EXPECTED_ACTOR_COUNT = 500

CHECKED_MUTATED_TABLES = (
    "external_actor_mappings",
    "snapshot_imports",
    "foundry_snapshots",
    "audit_events",
    "character_access",
    "sheet_row_mappings",
    "characters",
    "discord_guild_memberships",
    "discord_membership_roles",
    "discord_users",
    "platform_initialization",
    "idempotency_keys",
)


class BenchmarkError(RuntimeError):
    """Refusal or failure during benchmark execution."""


def get_database_url() -> str:
    env_app = os.environ.get("APP_ENVIRONMENT", "")
    if env_app != "test":
        raise BenchmarkError(
            f"APP_ENVIRONMENT must be 'test' to run benchmark; observed {env_app!r}."
        )

    url = os.environ.get("DATABASE_URL") or os.environ.get("TEST_DATABASE_URL")
    if not url:
        raise BenchmarkError(
            "Neither DATABASE_URL nor TEST_DATABASE_URL environment variable is set."
        )

    try:
        assert_disposable_target(
            url,
            expected_database=EXPECTED_DATABASES["test"],
            variable="DATABASE_URL",
            policy=ConnectionPolicy.UNIX_SOCKET_ONLY,
        )
    except UnsafeDatabaseTargetError as error:
        raise BenchmarkError(f"Database target safety validation failed: {error}") from error

    return url


def verify_connection_and_lock(engine: Engine) -> Any:
    connection = engine.connect()
    try:
        verify_connected_unix_socket_target(
            connection, expected_database=EXPECTED_DATABASES["test"]
        )
    except UnsafeDatabaseTargetError as error:
        connection.close()
        raise BenchmarkError(
            f"Live connection unix socket verification failed: {error}"
        ) from error

    result = connection.execute(
        text("SELECT pg_try_advisory_lock(:key)"), {"key": ADVISORY_LOCK_KEY}
    ).scalar()
    if not result:
        connection.close()
        raise BenchmarkError(
            f"Could not acquire advisory lock {ADVISORY_LOCK_KEY}; another benchmark or test may be running."
        )

    return connection


def release_advisory_lock(connection: Any) -> None:
    try:
        res = connection.execute(
            text("SELECT pg_advisory_unlock(:key)"), {"key": ADVISORY_LOCK_KEY}
        ).scalar()
        if not res:
            raise BenchmarkError(
                f"Explicit pg_advisory_unlock({ADVISORY_LOCK_KEY}) returned {res!r}; lock was not held or failed to release."
            )
    except BenchmarkError:
        raise
    except Exception as err:
        raise BenchmarkError(f"Failed to release advisory lock: {err}") from err


def get_complete_table_inventory(connection: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table_name in sorted(metadata.tables.keys()):
        res = connection.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        counts[table_name] = int(res or 0)

    try:
        res_alembic = connection.execute(text("SELECT COUNT(*) FROM alembic_version")).scalar()
        counts["alembic_version"] = int(res_alembic or 0)
    except Exception:
        pass

    return counts


#: Rows a **migration** puts there, which are therefore part of an empty
#: database rather than evidence somebody has been using it.
#:
#: Migration 0006 inserts the protected Server Administrator role-capability
#: mapping (OD-24, ADR 0010 D10). It cannot be revoked, edited or deleted by any
#: caller — that is the whole point of it — so "clean means every table has zero
#: rows" stopped being true of a freshly migrated database at that revision.
#: Naming the expected count here keeps the check as strict as it was: a
#: *second* mapping, or a row in any other table, is still dirt.
MIGRATION_SEEDED_ROWS: dict[str, int] = {"role_capability_mappings": 1}


def baseline_dirt(counts: dict[str, int]) -> dict[str, int]:
    """The rows in `counts` that a freshly migrated database would not have."""
    return {
        table: count
        for table, count in counts.items()
        if table != "alembic_version" and count != MIGRATION_SEEDED_ROWS.get(table, 0)
    }


def assert_clean_baseline_no_mutation(counts: dict[str, int]) -> None:
    dirty = baseline_dirt(counts)
    if dirty:
        raise BenchmarkError(
            f"Baseline database is not clean. Refusing execution without modifying database. Dirty tables: {dirty}"
        )


def truncate_checked_tables_without_cascade(connection: Any) -> None:
    existing_tables = [t for t in CHECKED_MUTATED_TABLES if t in metadata.tables]
    if existing_tables:
        statement = f"TRUNCATE TABLE {', '.join(existing_tables)} RESTART IDENTITY"
        connection.execute(text(statement))
        connection.commit()


def generate_500_actor_artifact() -> tuple[SnapshotArtifact, bytes]:
    actors = []
    for i in range(1, EXPECTED_ACTOR_COUNT + 1):
        actor_id = f"syn500act{i:07d}"  # Exactly 16 alphanumeric characters
        actor_name = f"Synthetic Actor {i:04d}"
        actors.append(
            fx.actor(
                actor_id=actor_id,
                name=actor_name,
                folder_id=fx.ACTIVE_FOLDER_ID,
            )
        )
    doc = fx.bundle(
        actors=tuple(actors),
        selected_folder_ids=(fx.ACTIVE_FOLDER_ID,),
    )
    raw_bytes = fx.encode(doc)
    artifact = ingest_bytes(raw_bytes)
    return artifact, raw_bytes


def seed_council_user(engine: Engine) -> None:
    with SqlAlchemyUnitOfWork(engine) as unit:
        unit.discord_users.add(
            DiscordUser(discord_id=COUNCIL_USER, username="synthetic-council")
        )
        unit.commit()


def make_service(engine: Engine) -> SnapshotImportService:
    authorization = FakeAuthorization.with_council(COUNCIL_USER)
    return SnapshotImportService(
        unit_of_work_factory=lambda: SqlAlchemyUnitOfWork(engine),
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=authorization,
    )


def verify_apply_database_effects(
    connection: Any, outcome: ImportOutcome, snapshot_checksum: str
) -> None:
    # 1. Characters count
    char_count = connection.execute(text("SELECT COUNT(*) FROM characters")).scalar()
    if char_count != EXPECTED_ACTOR_COUNT:
        raise BenchmarkError(
            f"DB Query Verification failed: characters table count = {char_count}, expected {EXPECTED_ACTOR_COUNT}"
        )

    # 2. Snapshot record count and id lookup
    snap_row = connection.execute(
        text("SELECT id FROM foundry_snapshots WHERE checksum = :checksum"),
        {"checksum": snapshot_checksum},
    ).fetchone()
    if not snap_row:
        raise BenchmarkError(
            f"DB Query Verification failed: foundry_snapshots record for checksum {snapshot_checksum} not found"
        )
    snapshot_id = snap_row[0]

    # 3. Mappings count and snapshot provenance
    map_res = connection.execute(
        text(
            "SELECT COUNT(*), COUNT(DISTINCT character_id) "
            "FROM external_actor_mappings "
            "WHERE established_by_snapshot_id = :snap_id AND folder_id = :folder_id"
        ),
        {"snap_id": snapshot_id, "folder_id": fx.ACTIVE_FOLDER_ID},
    ).fetchone()
    if not map_res or map_res[0] != EXPECTED_ACTOR_COUNT or map_res[1] != EXPECTED_ACTOR_COUNT:
        raise BenchmarkError(
            f"DB Query Verification failed: mappings count = {map_res}, expected {EXPECTED_ACTOR_COUNT}"
        )

    # 4. Import record count
    import_count = connection.execute(
        text("SELECT COUNT(*) FROM snapshot_imports WHERE id = :import_id AND status = 'applied'"),
        {"import_id": outcome.import_id},
    ).scalar()
    if import_count != 1:
        raise BenchmarkError(
            f"DB Query Verification failed: snapshot_imports count = {import_count}, expected 1"
        )

    # 5. Audit events count and correlation id
    audit_count = connection.execute(
        text("SELECT COUNT(*) FROM audit_events WHERE correlation_id = :corr_id"),
        {"corr_id": outcome.correlation_id},
    ).scalar()
    if not audit_count or audit_count < 1:
        raise BenchmarkError(
            "DB Query Verification failed: no audit_events found for import correlation_id"
        )

    # 6. Prohibited game-state tables
    prohibited = ("sheet_row_mappings", "idempotency_keys", "character_access")
    for t in prohibited:
        cnt = connection.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
        if cnt != 0:
            raise BenchmarkError(
                f"DB Query Verification failed: prohibited table {t} has {cnt} rows, expected 0"
            )


def verify_duplicate_apply_database_effects(
    connection: Any,
    dup_outcome: ImportOutcome,
    pre_dup_counts: dict[str, int],
) -> None:
    if not dup_outcome.duplicate:
        raise BenchmarkError("Duplicate apply verification failed: duplicate flag is False")
    post_dup_counts = get_complete_table_inventory(connection)
    if post_dup_counts != pre_dup_counts:
        raise BenchmarkError(
            "Duplicate apply verification failed: database state mutated during duplicate apply."
        )


@dataclass(frozen=True)
class TimingStats:
    sample_count: int
    samples_ms: list[float]
    min_ms: float
    median_ms: float
    mean_ms: float
    p95_ms: float
    max_ms: float
    stdev_ms: float
    variance_flag: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_count": self.sample_count,
            "samples_ms": [round(x, 3) for x in self.samples_ms],
            "min_ms": round(self.min_ms, 3),
            "median_ms": round(self.median_ms, 3),
            "mean_ms": round(self.mean_ms, 3),
            "p95_ms": round(self.p95_ms, 3),
            "max_ms": round(self.max_ms, 3),
            "stdev_ms": round(self.stdev_ms, 3),
            "max_exceeds_125pct_median": self.variance_flag,
        }


def calculate_stats(samples_ns: list[int]) -> TimingStats:
    samples_ms = [ns / 1_000_000.0 for ns in samples_ns]
    n = len(samples_ms)
    sorted_ms = sorted(samples_ms)
    min_ms = sorted_ms[0]
    max_ms = sorted_ms[-1]
    mean_ms = sum(samples_ms) / n

    if n % 2 == 1:
        median_ms = sorted_ms[n // 2]
    else:
        median_ms = (sorted_ms[n // 2 - 1] + sorted_ms[n // 2]) / 2.0

    p95_index = math.ceil(0.95 * n) - 1
    p95_index = max(0, min(p95_index, n - 1))
    p95_ms = sorted_ms[p95_index]

    variance = sum((x - mean_ms) ** 2 for x in samples_ms) / n
    stdev_ms = math.sqrt(variance)

    variance_flag = max_ms > (1.25 * median_ms)

    return TimingStats(
        sample_count=n,
        samples_ms=samples_ms,
        min_ms=min_ms,
        median_ms=median_ms,
        mean_ms=mean_ms,
        p95_ms=p95_ms,
        max_ms=max_ms,
        stdev_ms=stdev_ms,
        variance_flag=variance_flag,
    )


#: The Phase 2 gate criterion, in the only unit that survives a change of
#: corpus — change-log C-11, which amends C-9.
#:
#: C-9 set thresholds in *seconds against an Actor count*, measured on synthetic
#: Actors of 2,182 bytes. Rehearsal B then previewed real Actors of 508,975
#: bytes each — 233x larger, and consistent with discovery finding F-F5, which
#: had recorded "an actor is 1.1-3.3 MB of JSON" long before the benchmark was
#: written. A 32-Actor real folder is 15x the bytes of the 500-Actor synthetic
#: one, so a count-based threshold measures the corpus rather than the code.
#:
#: Throughput does not have that defect. Observed: 728 ms/MB synthetic (C-9),
#: 587 ms/MB real (Rehearsal B). The limit is set with headroom for a shared
#: host and catches what a threshold is actually for — an N+1 query or a
#: quadratic parse, which change this number by an order of magnitude.
THROUGHPUT_LIMIT_MS_PER_MB = 1200.0


def throughput_ms_per_mb(duration_ms: float, byte_size: int) -> float:
    return duration_ms / (byte_size / 1_000_000.0)


def calculate_throughput_gate(stats: TimingStats, byte_size: int) -> dict[str, Any]:
    """The gate criterion, reported whether or not it passes."""
    observed = throughput_ms_per_mb(stats.max_ms, byte_size)
    return {
        "observed_ms_per_mb": round(observed, 1),
        "limit_ms_per_mb": THROUGHPUT_LIMIT_MS_PER_MB,
        "within_limit": observed <= THROUGHPUT_LIMIT_MS_PER_MB,
        "measured_from": "slowest sample, not the median",
    }


def calculate_recommendation(stats: TimingStats) -> dict[str, Any]:
    p95_sec = stats.p95_ms / 1000.0
    max_sec = stats.max_ms / 1000.0

    candidate_sec = max(3.0 * p95_sec, 2.0 * max_sec)
    recommended_sec = int(math.ceil(candidate_sec))
    recommended_sec = max(recommended_sec, 5)

    return {
        "candidate_seconds": round(candidate_sec, 3),
        "recommended_seconds": recommended_sec,
        "within_120s_timeout_budget": recommended_sec <= 120,
    }


def run_benchmark() -> dict[str, Any]:
    url = get_database_url()
    engine = create_engine(url, poolclass=NullPool)
    connection = None
    initial_counts: dict[str, int] = {}

    try:
        connection = verify_connection_and_lock(engine)

        # 1. FAIL-CLOSED Baseline Check (NO MUTATION ALLOWED IF DIRTY)
        initial_counts = get_complete_table_inventory(connection)
        assert_clean_baseline_no_mutation(initial_counts)

        # Baseline is proven clean; now proceed
        artifact, raw_bytes = generate_500_actor_artifact()
        service = make_service(engine)

        # Pre-timing correctness assertions & DB query verification
        truncate_checked_tables_without_cascade(connection)
        seed_council_user(engine)

        parsed = service.parse(artifact)
        if len(parsed.actors) != EXPECTED_ACTOR_COUNT:
            raise BenchmarkError(
                f"Expected {EXPECTED_ACTOR_COUNT} actors in parsed snapshot, got {len(parsed.actors)}"
            )

        preview_assert = service.preview(artifact, request_key="pre-timing-prev-1")
        if preview_assert.blocked:
            raise BenchmarkError("Pre-timing preview had blocking errors.")
        if preview_assert.would_create != EXPECTED_ACTOR_COUNT:
            raise BenchmarkError(
                f"Pre-timing preview would create {preview_assert.would_create}, expected {EXPECTED_ACTOR_COUNT}"
            )

        apply_assert = service.apply(
            artifact, preview_assert, discord_user_id=COUNCIL_USER
        )
        if not apply_assert.applied or apply_assert.created_count != EXPECTED_ACTOR_COUNT:
            raise BenchmarkError("Pre-timing apply failed or created unexpected count.")

        # Database Query Assertions
        verify_apply_database_effects(connection, apply_assert, artifact.checksum.hex_digest)

        # Duplicate apply verification with DB query assertions
        pre_dup_counts = get_complete_table_inventory(connection)
        duplicate_assert = service.apply(
            artifact, preview_assert, discord_user_id=COUNCIL_USER
        )
        verify_duplicate_apply_database_effects(connection, duplicate_assert, pre_dup_counts)

        truncate_checked_tables_without_cascade(connection)

        # Warm-up iterations (2 untimed)
        for w in range(1, 3):
            seed_council_user(engine)
            prev = service.preview(artifact, request_key=f"warmup-prev-{w}")
            service.apply(artifact, prev, discord_user_id=COUNCIL_USER)
            truncate_checked_tables_without_cascade(connection)

        # Measured Preview Iterations (7 samples)
        preview_samples_ns: list[int] = []
        for i in range(1, 8):
            truncate_checked_tables_without_cascade(connection)
            seed_council_user(engine)

            t0 = time.perf_counter_ns()
            prev = service.preview(artifact, request_key=f"bench-prev-{i}")
            t1 = time.perf_counter_ns()

            preview_samples_ns.append(t1 - t0)
            if prev.would_create != EXPECTED_ACTOR_COUNT:
                raise BenchmarkError("Preview iteration failed count assertion.")
            truncate_checked_tables_without_cascade(connection)

        preview_stats = calculate_stats(preview_samples_ns)

        second_preview_stats = None
        if preview_stats.variance_flag:
            preview_samples_ns_2: list[int] = []
            for i in range(8, 15):
                truncate_checked_tables_without_cascade(connection)
                seed_council_user(engine)

                t0 = time.perf_counter_ns()
                prev = service.preview(artifact, request_key=f"bench-prev-{i}")
                t1 = time.perf_counter_ns()

                preview_samples_ns_2.append(t1 - t0)
                truncate_checked_tables_without_cascade(connection)

            second_preview_stats = calculate_stats(preview_samples_ns_2)
            combined_preview_stats = calculate_stats(preview_samples_ns + preview_samples_ns_2)
        else:
            combined_preview_stats = preview_stats

        # Measured Fresh Apply Iterations (7 samples)
        apply_samples_ns: list[int] = []
        for i in range(1, 8):
            truncate_checked_tables_without_cascade(connection)
            seed_council_user(engine)

            prev = service.preview(artifact, request_key=f"bench-app-{i}")

            t0 = time.perf_counter_ns()
            outcome = service.apply(artifact, prev, discord_user_id=COUNCIL_USER)
            t1 = time.perf_counter_ns()

            apply_samples_ns.append(t1 - t0)
            if not outcome.applied or outcome.created_count != EXPECTED_ACTOR_COUNT or outcome.duplicate:
                raise BenchmarkError("Fresh apply iteration failed assertions.")

            # DB Query Verification on each fresh apply iteration
            verify_apply_database_effects(connection, outcome, artifact.checksum.hex_digest)

            truncate_checked_tables_without_cascade(connection)

        apply_stats = calculate_stats(apply_samples_ns)

        second_apply_stats = None
        if apply_stats.variance_flag:
            apply_samples_ns_2: list[int] = []
            for i in range(8, 15):
                truncate_checked_tables_without_cascade(connection)
                seed_council_user(engine)

                prev = service.preview(artifact, request_key=f"bench-app-{i}")

                t0 = time.perf_counter_ns()
                outcome = service.apply(artifact, prev, discord_user_id=COUNCIL_USER)
                t1 = time.perf_counter_ns()

                apply_samples_ns_2.append(t1 - t0)
                truncate_checked_tables_without_cascade(connection)

            second_apply_stats = calculate_stats(apply_samples_ns_2)
            combined_apply_stats = calculate_stats(apply_samples_ns + apply_samples_ns_2)
        else:
            combined_apply_stats = apply_stats

        # Duplicate Apply Iteration (1 sample, informational)
        truncate_checked_tables_without_cascade(connection)
        seed_council_user(engine)
        prev_dup = service.preview(artifact, request_key="bench-dup-1")
        service.apply(artifact, prev_dup, discord_user_id=COUNCIL_USER)

        pre_dup_info_counts = get_complete_table_inventory(connection)
        t0 = time.perf_counter_ns()
        outcome_dup = service.apply(artifact, prev_dup, discord_user_id=COUNCIL_USER)
        t1 = time.perf_counter_ns()
        dup_ns = t1 - t0

        verify_duplicate_apply_database_effects(connection, outcome_dup, pre_dup_info_counts)
        truncate_checked_tables_without_cascade(connection)

        # Calculate recommendations based on combined stats
        prev_rec = calculate_recommendation(combined_preview_stats)
        apply_rec = calculate_recommendation(combined_apply_stats)

        report_dict: dict[str, Any] = OrderedDict(
            [
                ("benchmark_name", "Phase 2 R4 synthetic 500-Actor performance benchmark"),
                ("schema_version", "1.0"),
                ("timestamp_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
                (
                    "environment",
                    {
                        "app_environment": "test",
                        "database_name": EXPECTED_DATABASES["test"],
                        "connection_type": "unix_domain_socket",
                    },
                ),
                (
                    "artifact",
                    {
                        "actor_count": EXPECTED_ACTOR_COUNT,
                        "byte_size": len(raw_bytes),
                        "checksum_short": artifact.checksum.short,
                    },
                ),
                (
                    "pre_timing_verification",
                    {
                        "actors_parsed": EXPECTED_ACTOR_COUNT,
                        "dispositions_evaluated": EXPECTED_ACTOR_COUNT,
                        "preview_blocked": False,
                        "fresh_apply_created_identities": EXPECTED_ACTOR_COUNT,
                        "game_state_rows_created": 0,
                        "duplicate_apply_idempotent": True,
                        "database_queries_verified": True,
                    },
                ),
                ("preview_statistics", combined_preview_stats.to_dict()),
                ("apply_statistics", combined_apply_stats.to_dict()),
                (
                    "duplicate_apply_informational",
                    {
                        "duration_ms": round(dup_ns / 1_000_000.0, 3),
                        "duplicate_flag": True,
                    },
                ),
                (
                    "throughput_gate",
                    {
                        "preview": calculate_throughput_gate(
                            combined_preview_stats, len(raw_bytes)
                        ),
                        "apply": calculate_throughput_gate(
                            combined_apply_stats, len(raw_bytes)
                        ),
                        "note": (
                            "The Phase 2 gate criterion (change-log C-11). Expressed "
                            "per megabyte because a count-based threshold measures the "
                            "corpus rather than the code: this artifact's Actors are "
                            "2 KB each and real ones are ~500 KB."
                        ),
                    },
                ),
                (
                    "threshold_recommendations",
                    {
                        "preview": prev_rec,
                        "apply": apply_rec,
                        "note": (
                            "Nearest-rank p95 over 7 samples equals sample maximum. "
                            "Wall-clock seconds on THIS synthetic corpus, retained as "
                            "smoke-test context. Superseded as a gate criterion by "
                            "throughput_gate above (C-11 amending C-9); a real folder "
                            "of the same Actor count would be ~250 MB and could not "
                            "meet these numbers."
                        ),
                    },
                ),
                ("cleanup_verification", {"baseline_restored": True}),
            ]
        )

        if second_preview_stats:
            report_dict["preview_statistics_set_1"] = preview_stats.to_dict()
            report_dict["preview_statistics_set_2"] = second_preview_stats.to_dict()
        if second_apply_stats:
            report_dict["apply_statistics_set_1"] = apply_stats.to_dict()
            report_dict["apply_statistics_set_2"] = second_apply_stats.to_dict()

        return report_dict

    finally:
        if connection:
            try:
                connection.rollback()
            except Exception:
                pass

            # If initial_counts was clean, truncate and compare exact initial vs final inventory table-for-table
            dirty_initial = baseline_dirt(initial_counts)
            if not dirty_initial:
                truncate_checked_tables_without_cascade(connection)
                final_counts = get_complete_table_inventory(connection)
                if final_counts != initial_counts:
                    raise BenchmarkError(
                        f"Complete table inventory comparison failed. Initial: {initial_counts}, Final: {final_counts}"
                    )

            release_advisory_lock(connection)
            connection.close()

        engine.dispose()


def main() -> int:
    try:
        results = run_benchmark()
        json_output = json.dumps(results, indent=2)
        print(json_output)
        return 0
    except BenchmarkError as err:
        print(f"BENCHMARK ERROR: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"UNEXPECTED FAILURE: {err.__class__.__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
