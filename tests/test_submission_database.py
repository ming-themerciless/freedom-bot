"""Snapshot submission against real PostgreSQL.

A fake unit of work cannot lose a real race, cannot enforce a check constraint
and cannot prove a trigger. Everything here runs against the disposable
`freedom_test` database over the Unix-domain socket, and every assertion is
about what PostgreSQL actually did.

All bytes are synthetic and the artifact store is a per-test temporary
directory. Nothing here reads an existing export directory.
"""
from __future__ import annotations

import hashlib
import threading
import traceback
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from adapters.artifacts.filesystem import FilesystemArtifactStore
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from application.foundry.submission import (
    SUBMISSION_SCOPE,
    SnapshotSubmissionService,
    SubmissionRefused,
)
from application.service_principals import ServicePrincipal, ServicePrincipalScope
from domain.foundry import OBSERVED_DEPLOYMENT
from tests import foundry_fixtures as fx
from tests.conftest import close_admission, open_admission

pytestmark = pytest.mark.database

SUBMITTER = ServicePrincipal(
    principal_id="foundry-the-guild",
    scopes=frozenset({ServicePrincipalScope.SUBMIT_SNAPSHOT}),
)


@pytest.fixture()
def service(committed_database, tmp_path: Path):
    engine = committed_database
    # The admission generation an operator opens at deployment. Without one
    # nothing can be accepted at all — see `application/admissions.py`.
    open_admission(engine, SUBMITTER.principal_id)
    store = FilesystemArtifactStore(tmp_path / "artifacts")

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(engine)

    return SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=store
    ), engine, store


def payload(document=None) -> bytes:
    return fx.encode(document or fx.bundle())


def rows(engine, statement: str, **parameters):
    with engine.begin() as connection:
        return connection.execute(text(statement), parameters).mappings().all()


# --- provenance ---------------------------------------------------------------


def test_a_submission_commits_provenance_and_nothing_else(service):
    submissions, engine, _ = service

    receipt = submissions.submit(payload(), principal=SUBMITTER, request_key="k1")

    (snapshot,) = rows(
        engine,
        "SELECT * FROM foundry_snapshots WHERE checksum = :checksum",
        checksum=receipt.checksum,
    )
    assert snapshot["received_via"] == "foundry_module"
    assert snapshot["submitted_by_principal"] == "foundry-the-guild"
    assert snapshot["received_by_discord_user_id"] is None
    assert snapshot["artifact_location"] == f"snapshot/{receipt.checksum}.json"

    assert rows(engine, "SELECT 1 FROM characters") == []
    assert rows(engine, "SELECT 1 FROM external_actor_mappings") == []
    assert rows(engine, "SELECT 1 FROM snapshot_imports") == []


def test_the_audit_row_names_the_service_principal_and_no_discord_user(service):
    submissions, engine, _ = service

    receipt = submissions.submit(payload(), principal=SUBMITTER, request_key="k1")

    (event,) = rows(
        engine,
        "SELECT * FROM audit_events WHERE correlation_id = :correlation",
        correlation=receipt.correlation_id,
    )
    assert event["action"] == "snapshot_submission.accepted"
    assert event["actor_capability"] == "service_principal"
    assert event["source"] == "foundry"
    assert event["actor_discord_user_id"] is None
    assert event["payload"]["service_principal_id"] == "foundry-the-guild"
    assert "request_key" not in event["payload"]


def test_a_module_row_without_a_principal_is_refused_by_the_database(service):
    """The check constraint, not the application, is what makes this hold."""
    _, engine, _ = service
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO foundry_snapshots (id, checksum, size_bytes, "
                    "schema_version, exporter_id, exporter_version, exported_at, "
                    "world_id, world_title, core_version, system_id, "
                    "system_version, actor_count, selected_folder_ids, "
                    "received_via, submitted_by_principal, correlation_id) VALUES "
                    "(gen_random_uuid(), :checksum, 10, 1, 'x', '1.0.0', now(), "
                    "'the-guild', 'The Guild', '14.367', 'dnd5e', '5.3.3', 1, "
                    "'[]'::jsonb, 'foundry_module', NULL, gen_random_uuid())"
                ),
                {"checksum": "a" * 64},
            )


def test_an_operator_row_naming_a_principal_is_refused_by_the_database(service):
    _, engine, _ = service
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO foundry_snapshots (id, checksum, size_bytes, "
                    "schema_version, exporter_id, exporter_version, exported_at, "
                    "world_id, world_title, core_version, system_id, "
                    "system_version, actor_count, selected_folder_ids, "
                    "received_via, submitted_by_principal, correlation_id) VALUES "
                    "(gen_random_uuid(), :checksum, 10, 1, 'x', '1.0.0', now(), "
                    "'the-guild', 'The Guild', '14.367', 'dnd5e', '5.3.3', 1, "
                    "'[]'::jsonb, 'operator', 'someone', gen_random_uuid())"
                ),
                {"checksum": "b" * 64},
            )


def test_an_unknown_received_via_is_refused_by_the_database(service):
    _, engine, _ = service
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO foundry_snapshots (id, checksum, size_bytes, "
                    "schema_version, exporter_id, exporter_version, exported_at, "
                    "world_id, world_title, core_version, system_id, "
                    "system_version, actor_count, selected_folder_ids, "
                    "received_via, correlation_id) VALUES "
                    "(gen_random_uuid(), :checksum, 10, 1, 'x', '1.0.0', now(), "
                    "'the-guild', 'The Guild', '14.367', 'dnd5e', '5.3.3', 1, "
                    "'[]'::jsonb, 'smuggled', gen_random_uuid())"
                ),
                {"checksum": "c" * 64},
            )


# --- idempotency and uniqueness ----------------------------------------------


def test_the_checksum_is_unique_in_the_database(service):
    submissions, engine, _ = service
    receipt = submissions.submit(payload(), principal=SUBMITTER, request_key="k1")

    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO foundry_snapshots (id, checksum, size_bytes, "
                    "schema_version, exporter_id, exporter_version, exported_at, "
                    "world_id, world_title, core_version, system_id, "
                    "system_version, actor_count, selected_folder_ids, "
                    "received_via, correlation_id) VALUES "
                    "(gen_random_uuid(), :checksum, 10, 1, 'x', '1.0.0', now(), "
                    "'the-guild', 'The Guild', '14.367', 'dnd5e', '5.3.3', 1, "
                    "'[]'::jsonb, 'operator', gen_random_uuid())"
                ),
                {"checksum": receipt.checksum},
            )


def test_a_retry_produces_one_snapshot_one_artifact_and_one_receipt(service):
    submissions, engine, store = service
    data = payload()

    first = submissions.submit(data, principal=SUBMITTER, request_key="k1")
    second = submissions.submit(data, principal=SUBMITTER, request_key="k1")

    assert second.snapshot_id == first.snapshot_id
    assert second.duplicate is True
    assert len(rows(engine, "SELECT 1 FROM foundry_snapshots")) == 1
    assert len(list(store.root.glob("*.json"))) == 1
    assert (
        len(
            rows(
                engine,
                "SELECT 1 FROM idempotency_keys WHERE scope = :scope",
                scope=SUBMISSION_SCOPE,
            )
        )
        == 1
    )


def test_the_stored_receipt_survives_a_round_trip_through_postgresql(service):
    submissions, engine, _ = service
    receipt = submissions.submit(payload(), principal=SUBMITTER, request_key="k1")

    (record,) = rows(
        engine,
        "SELECT * FROM idempotency_keys WHERE scope = :scope AND key = :key",
        scope=SUBMISSION_SCOPE,
        key="k1",
    )
    assert record["status"] == "completed"
    assert record["response"]["snapshot_id"] == str(receipt.snapshot_id)
    assert bytes(record["request_hash"]) == hashlib.sha256(
        f"{SUBMISSION_SCOPE}\n{receipt.checksum}".encode("utf-8")
    ).digest()


def test_the_same_key_with_other_bytes_conflicts_and_writes_nothing(service):
    submissions, engine, _ = service
    submissions.submit(payload(), principal=SUBMITTER, request_key="k1")
    other = payload(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),)))

    with pytest.raises(SubmissionRefused) as refusal:
        submissions.submit(other, principal=SUBMITTER, request_key="k1")

    assert refusal.value.code == "request_key_conflict"
    assert len(rows(engine, "SELECT 1 FROM foundry_snapshots")) == 1


def test_the_same_bytes_under_two_keys_share_one_artifact_identity(service):
    submissions, engine, store = service
    data = payload()

    first = submissions.submit(data, principal=SUBMITTER, request_key="k1")
    second = submissions.submit(data, principal=SUBMITTER, request_key="k2")

    assert second.snapshot_id == first.snapshot_id
    assert len(rows(engine, "SELECT 1 FROM foundry_snapshots")) == 1
    assert len(list(store.root.glob("*.json"))) == 1


# --- concurrency --------------------------------------------------------------


def _concurrently(work, count=2):
    """Run `work(index)` on `count` threads and collect outcomes."""
    results: list[object] = [None] * count
    barrier = threading.Barrier(count)

    def run(index: int) -> None:
        barrier.wait()
        try:
            results[index] = work(index)
        except Exception as error:  # noqa: BLE001 - recorded and asserted on
            results[index] = error
            traceback.clear_frames(error.__traceback__)

    threads = [threading.Thread(target=run, args=(index,)) for index in range(count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    return results


def test_two_concurrent_identical_submissions_produce_one_snapshot(service):
    submissions, engine, store = service
    data = payload()

    results = _concurrently(
        lambda index: submissions.submit(
            data, principal=SUBMITTER, request_key=f"key-{index}"
        )
    )

    for result in results:
        assert not isinstance(result, Exception), result
    assert results[0].snapshot_id == results[1].snapshot_id
    assert len(rows(engine, "SELECT 1 FROM foundry_snapshots")) == 1
    assert len(list(store.root.glob("*.json"))) == 1


def test_two_concurrent_submissions_of_one_key_return_one_result(service):
    submissions, engine, _ = service
    data = payload()

    results = _concurrently(
        lambda index: submissions.submit(data, principal=SUBMITTER, request_key="same")
    )

    for result in results:
        assert not isinstance(result, Exception), result
    assert results[0].snapshot_id == results[1].snapshot_id
    assert (
        len(
            rows(
                engine,
                "SELECT 1 FROM idempotency_keys WHERE scope = :scope",
                scope=SUBMISSION_SCOPE,
            )
        )
        == 1
    )


def test_two_concurrent_conflicting_submissions_leave_one_key_and_no_partial_state(
    service,
):
    submissions, engine, _ = service
    first = payload()
    second = payload(fx.bundle(actors=(fx.actor(fx.SECOND_ACTOR_ID),)))

    results = _concurrently(
        lambda index: submissions.submit(
            first if index == 0 else second, principal=SUBMITTER, request_key="same"
        )
    )

    refusals = [r for r in results if isinstance(r, SubmissionRefused)]
    successes = [r for r in results if not isinstance(r, Exception)]
    assert len(successes) == 1
    assert len(refusals) == 1
    assert refusals[0].code == "request_key_conflict"
    assert (
        len(
            rows(
                engine,
                "SELECT 1 FROM idempotency_keys WHERE scope = :scope",
                scope=SUBMISSION_SCOPE,
            )
        )
        == 1
    )


# --- failure and immutability -------------------------------------------------


class _RefusingStore:
    """An artifact store that always refuses the write."""

    def store(self, artifact):
        from application.artifacts import ArtifactStorageError

        raise ArtifactStorageError("write_failed")

    def load(self, checksum):  # pragma: no cover - never reached
        from application.artifacts import ArtifactNotStored

        raise ArtifactNotStored()

    def contains(self, checksum):
        return False


def test_a_storage_failure_commits_no_provenance(committed_database):
    engine = committed_database
    open_admission(engine, SUBMITTER.principal_id)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(engine)

    submissions = SnapshotSubmissionService(
        factory, deployment=OBSERVED_DEPLOYMENT, artifacts=_RefusingStore()
    )

    with pytest.raises(SubmissionRefused) as refusal:
        submissions.submit(payload(), principal=SUBMITTER, request_key="k1")

    assert refusal.value.code == "storage_unavailable"
    assert rows(engine, "SELECT 1 FROM foundry_snapshots") == []
    assert (
        rows(
            engine,
            "SELECT 1 FROM idempotency_keys WHERE scope = :scope",
            scope=SUBMISSION_SCOPE,
        )
        == []
    )


def test_a_refusal_records_one_refused_event_and_no_snapshot(service):
    submissions, engine, _ = service

    with pytest.raises(SubmissionRefused):
        submissions.submit(b"{not json", principal=SUBMITTER, request_key="k1")

    events = rows(
        engine,
        "SELECT * FROM audit_events WHERE action = 'snapshot_submission.refused'",
    )
    assert len(events) == 1
    assert events[0]["payload"]["recorded"] is False
    assert rows(engine, "SELECT 1 FROM foundry_snapshots") == []


def test_the_runtime_role_cannot_rewrite_a_submitted_snapshot(service):
    """`foundry_snapshots` remains append-only after this revision's columns."""
    submissions, engine, _ = service
    receipt = submissions.submit(payload(), principal=SUBMITTER, request_key="k1")

    for statement in (
        "UPDATE foundry_snapshots SET submitted_by_principal = 'someone-else'",
        "UPDATE foundry_snapshots SET received_via = 'operator'",
        "DELETE FROM foundry_snapshots WHERE checksum = :checksum",
    ):
        with pytest.raises(DBAPIError):
            with engine.begin() as connection:
                connection.execute(
                    text(statement), {"checksum": receipt.checksum}
                )
