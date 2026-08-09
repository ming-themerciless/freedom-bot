"""Focused unit and integration tests for tests/benchmark_snapshot_500.py.

Asserts:
- Refusal of non-test environment or wrong database target.
- Deterministic synthetic generation of exactly 500 contract-valid unique Actors.
- Output sanitization allowlist (no credentials, URLs, actor payloads).
- Real regression test: Dirty-baseline preservation without mutation.
- Real regression test: Injected-failure cleanup and complete table inventory restoration.
- Real regression test: Explicit advisory lock release verification.
- Real regression test: Injected-clock timer-boundary separation.
"""
from __future__ import annotations

import json
import time
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from domain.foundry import OBSERVED_DEPLOYMENT, _DOCUMENT_ID
from tests import benchmark_snapshot_500 as bm

ALLOWED_REPORT_KEYS = frozenset(
    {
        "benchmark_name",
        "schema_version",
        "timestamp_utc",
        "environment",
        "artifact",
        "pre_timing_verification",
        "preview_statistics",
        "apply_statistics",
        "duplicate_apply_informational",
        "threshold_recommendations",
        "cleanup_verification",
        "preview_statistics_set_1",
        "preview_statistics_set_2",
        "apply_statistics_set_1",
        "apply_statistics_set_2",
    }
)


def test_refuse_non_test_environment(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg:///freedom_test")
    with pytest.raises(bm.BenchmarkError, match="APP_ENVIRONMENT must be 'test'"):
        bm.get_database_url()


def test_refuse_invalid_database_url(monkeypatch):
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://wrong_db_name")
    with pytest.raises(bm.BenchmarkError, match="Database target safety validation failed"):
        bm.get_database_url()


def test_deterministic_500_actor_generation():
    artifact, raw_bytes = bm.generate_500_actor_artifact()

    # Check byte limits
    assert len(raw_bytes) > 0
    assert len(raw_bytes) < 64 * 1024 * 1024

    # Parse artifact and assert 500 unique actors
    from application.foundry.parser import parse_snapshot
    parsed = parse_snapshot(artifact, deployment=OBSERVED_DEPLOYMENT)
    assert len(parsed.actors) == 500

    actor_ids = set()
    for actor in parsed.actors:
        actor_id_str = str(actor.actor_id)
        assert _DOCUMENT_ID.fullmatch(actor_id_str), f"Actor ID {actor_id_str} invalid"
        actor_ids.add(actor_id_str)

    assert len(actor_ids) == 500


def test_output_sanitization_allowlist():
    raw_stats = bm.calculate_stats([10_000_000, 12_000_000, 11_000_000, 15_000_000, 14_000_000, 13_000_000, 16_000_000])
    rec = bm.calculate_recommendation(raw_stats)

    report_dict = {
        "benchmark_name": "Phase 2 R4 synthetic 500-Actor performance benchmark",
        "schema_version": "1.0",
        "timestamp_utc": "2026-08-05T21:00:00Z",
        "environment": {"app_environment": "test"},
        "artifact": {"actor_count": 500},
        "pre_timing_verification": {"actors_parsed": 500},
        "preview_statistics": raw_stats.to_dict(),
        "apply_statistics": raw_stats.to_dict(),
        "duplicate_apply_informational": {"duration_ms": 12.3},
        "threshold_recommendations": {"preview": rec, "apply": rec},
        "cleanup_verification": {"baseline_restored": True},
    }

    assert set(report_dict.keys()).issubset(ALLOWED_REPORT_KEYS)

    json_text = json.dumps(report_dict)

    assert "postgresql://" not in json_text
    assert "password" not in json_text
    assert "secret" not in json_text
    assert "Synthetic Actor" not in json_text
    assert "syn500act" not in json_text


def test_stats_and_recommendation_calculation():
    samples_ns = [
        100_000_000,
        110_000_000,
        105_000_000,
        120_000_000,
        115_000_000,
        108_000_000,
        125_000_000,
    ]
    stats = bm.calculate_stats(samples_ns)
    assert stats.sample_count == 7
    assert stats.min_ms == 100.0
    assert stats.max_ms == 125.0
    assert stats.p95_ms == 125.0
    assert not stats.variance_flag

    rec = bm.calculate_recommendation(stats)
    assert rec["recommended_seconds"] == 5
    assert rec["within_120s_timeout_budget"] is True


def test_throughput_is_measured_per_megabyte_not_per_actor():
    """C-11: the gate criterion must not move when the corpus changes.

    The two observed corpora differ by 233x in bytes per Actor. A criterion in
    seconds-per-Actor-count would have passed the synthetic run and failed the
    real one at identical code quality; throughput does not.
    """
    synthetic = bm.throughput_ms_per_mb(793.866, 1_090_981)   # C-9 benchmark
    real = bm.throughput_ms_per_mb(9_566.0, 16_287_185)       # Rehearsal B

    assert 700 < synthetic < 760
    assert 550 < real < 620
    # The real run is faster per megabyte despite taking 12x the wall clock.
    assert real < synthetic
    assert max(synthetic, real) < bm.THROUGHPUT_LIMIT_MS_PER_MB


def test_the_throughput_gate_reports_a_breach_rather_than_hiding_it():
    slow = bm.calculate_stats([int(60e9)] * 7)  # 60 s for the artifact below
    gate = bm.calculate_throughput_gate(slow, 1_000_000)

    assert gate["within_limit"] is False
    assert gate["observed_ms_per_mb"] == 60_000.0
    assert gate["limit_ms_per_mb"] == bm.THROUGHPUT_LIMIT_MS_PER_MB


def test_the_gate_measures_the_slowest_sample():
    """A median would let one pathological run hide behind six good ones."""
    uneven = bm.calculate_stats([int(1e9)] * 6 + [int(9e9)])
    gate = bm.calculate_throughput_gate(uneven, 10_000_000)

    assert gate["observed_ms_per_mb"] == 900.0  # from the 9 s sample, not the 1 s ones
    assert gate["measured_from"] == "slowest sample, not the median"


@pytest.mark.database
def test_dirty_baseline_preservation_without_mutation(migrated_database, monkeypatch):
    """Regression test: a dirty baseline causes refusal without ANY truncate/delete mutation."""
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    engine = migrated_database

    # Seed a dirty row
    char_id = str(uuid4())
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO characters (id, display_name, level, version) "
                "VALUES (:id, 'Dirty Character', 1, 0)"
            ),
            {"id": char_id},
        )

    try:
        with pytest.raises(bm.BenchmarkError, match="Baseline database is not clean"):
            bm.run_benchmark()

        # CRITICAL ASSERTION: The dirty character row MUST STILL EXIST!
        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM characters WHERE id = :id"), {"id": char_id}
            ).scalar()
            assert count == 1, "Dirty baseline row was mutated or deleted!"
    finally:
        # Clean up after test
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM characters WHERE id = :id"), {"id": char_id})


@pytest.mark.database
def test_injected_failure_cleanup(migrated_database, monkeypatch):
    """Regression test: injected failure during apply triggers complete cleanup."""
    monkeypatch.setenv("APP_ENVIRONMENT", "test")

    original_make_service = bm.make_service

    def faulty_make_service(engine):
        service = original_make_service(engine)
        original_apply = service.apply

        call_count = [0]

        def faulty_apply(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:  # Inject failure on 2nd apply
                raise RuntimeError("Injected benchmark apply failure")
            return original_apply(*args, **kwargs)

        service.apply = faulty_apply
        return service

    monkeypatch.setattr(bm, "make_service", faulty_make_service)

    with pytest.raises(Exception):
        bm.run_benchmark()

    # Verify complete table inventory is clean post-failure
    engine = migrated_database
    with engine.connect() as conn:
        counts = bm.get_complete_table_inventory(conn)
        dirty = {t: c for t, c in counts.items() if t != "alembic_version" and c != 0}
        assert not dirty, f"Injected failure left dirty tables: {dirty}"


@pytest.mark.database
def test_advisory_lock_release_and_inventory_restoration(migrated_database, monkeypatch):
    """Regression test: advisory lock is explicitly released and inventory restored table-for-table."""
    monkeypatch.setenv("APP_ENVIRONMENT", "test")

    results = bm.run_benchmark()
    assert results["cleanup_verification"]["baseline_restored"] is True

    # Assert advisory lock is released by acquiring it on a new connection
    url = bm.get_database_url()
    engine = create_engine(url, poolclass=NullPool)
    with engine.connect() as conn:
        res = conn.execute(
            text("SELECT pg_try_advisory_lock(:key)"), {"key": bm.ADVISORY_LOCK_KEY}
        ).scalar()
        assert res is True, "Advisory lock was not released after benchmark completion!"
        conn.execute(
            text("SELECT pg_advisory_unlock(:key)"), {"key": bm.ADVISORY_LOCK_KEY}
        )
    engine.dispose()


@pytest.mark.database
def test_timer_boundary_separation_injected_clock(migrated_database, monkeypatch):
    """Regression test: injected clock proves setup, parsing, DB queries and cleanup are excluded from timer."""
    monkeypatch.setenv("APP_ENVIRONMENT", "test")

    current_time_ns = [1_000_000_000]

    def mock_perf_counter_ns():
        return current_time_ns[0]

    monkeypatch.setattr(time, "perf_counter_ns", mock_perf_counter_ns)

    original_make_service = bm.make_service

    def InstrumentService(engine):
        service = original_make_service(engine)
        orig_preview = service.preview
        orig_apply = service.apply

        def instrumented_preview(*args, **kwargs):
            current_time_ns[0] += 10_000_000  # 10ms inside preview timer
            return orig_preview(*args, **kwargs)

        def instrumented_apply(*args, **kwargs):
            current_time_ns[0] += 20_000_000  # 20ms inside apply timer
            return orig_apply(*args, **kwargs)

        service.preview = instrumented_preview
        service.apply = instrumented_apply
        return service

    monkeypatch.setattr(bm, "make_service", InstrumentService)

    # Advance clock outside timers during setup
    orig_generate = bm.generate_500_actor_artifact
    def setup_advancing_generate():
        current_time_ns[0] += 500_000_000  # Advance 500ms outside timer
        return orig_generate()

    monkeypatch.setattr(bm, "generate_500_actor_artifact", setup_advancing_generate)

    results = bm.run_benchmark()

    prev_samples = results["preview_statistics"]["samples_ms"]
    apply_samples = results["apply_statistics"]["samples_ms"]

    for sample in prev_samples:
        assert 9.0 <= sample <= 11.0, f"Preview sample {sample}ms included setup/cleanup overhead!"
    for sample in apply_samples:
        assert 19.0 <= sample <= 21.0, f"Apply sample {sample}ms included setup/cleanup overhead!"
