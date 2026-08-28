"""Phase 2 against real PostgreSQL.

A mock does not prove a constraint, a trigger, a transaction boundary or a
concurrent outcome. Everything in this file runs against the disposable
`freedom_test` database over the Unix-domain socket, and every assertion here is
about what PostgreSQL actually did.
"""
from __future__ import annotations

import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError, IntegrityError

from application.authorization import SupervisedBootstrap
from application.bootstrap import BootstrapGate
from application.errors import PersistenceError, UniquenessConflict
from application.foundry.import_service import (
    ImportRefused,
    SnapshotImportService,
)
from application.foundry.artifact import ingest_bytes
from adapters.database.unit_of_work import SqlAlchemyUnitOfWork
from domain.foundry import OBSERVED_DEPLOYMENT
from domain.foundry_profile import PROFILE
from domain.identity import Character, DiscordUser
from tests import foundry_fixtures as fx
from tests import snapshot_harness as harness
from tests.fakes import FakeAuthorization

pytestmark = pytest.mark.database

COUNCIL_USER = 4200000000000000001

APPEND_ONLY_TABLES = (
    "audit_events",
    "foundry_snapshots",
    "snapshot_imports",
)


# --- wiring -------------------------------------------------------------------


@pytest.fixture()
def services(committed_database):
    """Real repositories, real transactions, one disposable database."""
    engine = committed_database
    authorization = FakeAuthorization.with_council(COUNCIL_USER)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(engine)

    # Attribution is a foreign key, not a free-text field: an audit row naming a
    # Discord user the platform has never seen is refused by the database.
    with factory() as unit:
        unit.discord_users.add(
            DiscordUser(discord_id=COUNCIL_USER, username="synthetic-council")
        )
        unit.commit()

    gate = BootstrapGate(factory, profile=PROFILE)
    imports = SnapshotImportService(
        factory,
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=authorization,
        bootstrap_gate=gate,
    )
    return {
        "engine": engine,
        "factory": factory,
        "authorization": authorization,
        "imports": imports,
        "gate": gate,
    }


def artifact(document=None):
    return ingest_bytes(fx.encode(document or fx.bundle()))


def apply_import(services, *, request_key="req-1", document=None, source=None, **kwargs):
    source = source or artifact(document)
    preview = services["imports"].preview(source, request_key=request_key, **kwargs)
    return services["imports"].apply(
        source, preview, discord_user_id=COUNCIL_USER
    )


def create_character(services, display_name="Persisted Testcharacter") -> Character:
    character = Character(id=uuid4(), display_name=display_name)
    with services["factory"]() as unit:
        unit.characters.add(character)
        unit.commit()
    return character


def count(engine, table: str) -> int:
    with engine.begin() as connection:
        return connection.execute(text(f"SELECT count(*) FROM {table}")).scalar_one()


#: What must never appear in anything a caller, an operator or a log can see
#: when a database operation fails (finding I-1). SQL and bound parameters come
#: from `IntegrityError.__str__`; `DETAIL:`/`Key (` are PostgreSQL's own
#: diagnostics, which quote the conflicting *values*; the rest are driver,
#: ORM and connection detail.
UNSAFE_FRAGMENTS = (
    "INSERT INTO",
    "UPDATE ",
    "DELETE FROM",
    "[SQL:",
    "[parameters:",
    "DETAIL:",
    "Key (",
    "duplicate key value",
    "psycopg",
    "postgresql://",
    "postgresql+psycopg",
    "sqlalchemy.org",
    "IntegrityError",
)


def assert_safe(error: Exception, *, and_not: tuple[str, ...] = ()) -> None:
    """Nothing about the database, the statement or the data escaped.

    The rendered traceback is checked as well as the message, because a chained
    `__cause__` puts the original statement back into every rendering even when
    the message itself is clean. `raise ... from None` is what severs it, and
    the last two assertions are what hold that in place.
    """
    rendered = "\n".join(
        [str(error), repr(error), *traceback.format_exception(error)]
    )
    for fragment in UNSAFE_FRAGMENTS + and_not:
        assert fragment not in rendered, f"{fragment!r} leaked out of the adapter"
    assert error.__cause__ is None
    assert error.__context__ is None or error.__suppress_context__


# --- an end-to-end import -----------------------------------------------------


def test_a_preview_against_postgresql_writes_nothing(services):
    services["imports"].preview(artifact(), request_key="req-1")

    for table in ("characters", "external_actor_mappings", "foundry_snapshots", "audit_events"):
        assert count(services["engine"], table) == 0


def test_an_applied_import_commits_character_mapping_record_and_audit(services):
    outcome = apply_import(services)

    assert outcome.applied
    engine = services["engine"]
    assert count(engine, "characters") == 1
    assert count(engine, "external_actor_mappings") == 1
    assert count(engine, "foundry_snapshots") == 1
    assert count(engine, "snapshot_imports") == 1
    # One import event plus one per created character.
    assert count(engine, "audit_events") == 2


def test_the_stored_mapping_traces_to_the_snapshot_and_the_folder(services):
    apply_import(services)

    with services["engine"].begin() as connection:
        row = connection.execute(
            text(
                "SELECT m.external_actor_id, m.folder_id, s.checksum "
                "FROM external_actor_mappings m "
                "JOIN foundry_snapshots s ON s.id = m.established_by_snapshot_id"
            )
        ).one()

    assert row.external_actor_id == fx.FIRST_ACTOR_ID
    assert row.folder_id == fx.ACTIVE_FOLDER_ID
    assert len(row.checksum) == 64


# --- immutable artifact identity ----------------------------------------------


def test_two_snapshots_cannot_share_a_checksum(db_connection):
    values = {
        "checksum": "a" * 64,
        "exported_at": datetime(2026, 8, 2, tzinfo=timezone.utc),
        "correlation": uuid4(),
    }
    statement = text(
        "INSERT INTO foundry_snapshots (id, checksum, size_bytes, schema_version, "
        "exporter_id, exporter_version, exported_at, world_id, world_title, "
        "core_version, system_id, system_version, actor_count, "
        "selected_folder_ids, correlation_id) VALUES (:id, :checksum, 10, 1, "
        "'e', '1.0.0', :exported_at, 'the-guild', 'The Guild', '14.367', 'dnd5e', "
        "'5.3.3', 1, '[]'::jsonb, :correlation)"
    )
    db_connection.execute(statement, {"id": uuid4(), **values})

    with pytest.raises(IntegrityError):
        db_connection.execute(statement, {"id": uuid4(), **values})


def test_a_checksum_must_be_a_sha256_hex_digest(db_connection):
    with pytest.raises(IntegrityError):
        db_connection.execute(
            text(
                "INSERT INTO foundry_snapshots (id, checksum, size_bytes, "
                "schema_version, exporter_id, exporter_version, exported_at, "
                "world_id, world_title, core_version, system_id, system_version, "
                "actor_count, selected_folder_ids, correlation_id) VALUES "
                "(:id, 'NOT-A-DIGEST', 10, 1, 'e', '1.0.0', now(), 'the-guild', "
                "'The Guild', '14.367', 'dnd5e', '5.3.3', 1, '[]'::jsonb, :c)"
            ),
            {"id": uuid4(), "c": uuid4()},
        )


def test_a_tampered_artifact_is_a_different_snapshot_in_the_database(services):
    apply_import(services, request_key="req-1")
    tampered = ingest_bytes(
        fx.tamper(fx.encode(fx.bundle()), find=b"Brightlantern", replace=b"Brightlantexn")
    )

    preview = services["imports"].preview(tampered, request_key="req-2")
    outcome = services["imports"].apply(
        tampered, preview, discord_user_id=COUNCIL_USER
    )

    # The changed bytes are a *different* snapshot with its own identity and its
    # own import record; they did not inherit the first one's.
    assert outcome.duplicate is False
    with services["engine"].begin() as connection:
        checksums = connection.execute(
            text("SELECT checksum FROM foundry_snapshots ORDER BY received_at")
        ).scalars().all()
    assert len(set(checksums)) == 2
    # The Actor id did not change, so the rename is a warning against the same
    # character rather than a second one.
    assert count(services["engine"], "characters") == 1
    assert count(services["engine"], "external_actor_mappings") == 1
    summary = outcome.reconciliation.summary()
    assert "character.display_name" in summary["fields_differing"]
    # B-2: the difference runs from Foundry to the platform, so the platform's
    # display record is what is stale. Asserted against PostgreSQL as well as
    # in `test_snapshot_reconciliation.py`, because the summary written here is
    # the one that lands in the append-only import record.
    assert summary["stale_platform_display_names"] == 1
    assert "platform_display_name_stale" in summary["issue_codes"]
    assert "foundry_out_of_date" not in summary["issue_codes"]
    # …and Phase 2 wrote nothing: the stored display name is still the one the
    # first import created the character with.
    with services["engine"].begin() as connection:
        stored = connection.execute(text("SELECT display_name FROM characters")).scalar_one()
    assert stored == harness.FIXTURE_DISPLAY_NAME


# --- idempotency, enforced by the database ------------------------------------


def test_a_repeated_request_key_is_refused_by_the_database(db_connection):
    snapshot_id = _insert_snapshot(db_connection)
    _insert_import(db_connection, snapshot_id, request_key="req-1")

    with pytest.raises(IntegrityError):
        _insert_import(db_connection, snapshot_id, request_key="req-1")


def test_the_same_input_cannot_be_applied_twice(db_connection):
    snapshot_id = _insert_snapshot(db_connection)
    _insert_import(db_connection, snapshot_id, request_key="req-1", status="applied")

    with pytest.raises(IntegrityError):
        _insert_import(db_connection, snapshot_id, request_key="req-2", status="applied")


def test_a_refused_attempt_does_not_claim_the_input_identity(db_connection):
    snapshot_id = _insert_snapshot(db_connection)
    _insert_import(db_connection, snapshot_id, request_key="req-1", status="refused")
    _insert_import(db_connection, snapshot_id, request_key="req-2", status="refused")

    # And the corrected retry can still succeed.
    _insert_import(db_connection, snapshot_id, request_key="req-3", status="applied")


def test_reapplying_the_same_checksum_is_a_no_op_against_postgresql(services):
    first = apply_import(services, request_key="req-1")

    second = apply_import(services, request_key="req-2")

    assert second.duplicate is True
    assert second.import_id == first.import_id
    assert count(services["engine"], "characters") == 1
    assert count(services["engine"], "snapshot_imports") == 1


def race(database_url, source, previews) -> list[object]:
    """Apply `previews` from separate connections at the same instant.

    Each thread builds its own engine and service, so the two applies are two
    real PostgreSQL transactions on two real connections. Whatever each returns
    or raises is collected; the assertions are the caller's.
    """
    results: list[object] = []
    lock = threading.Lock()
    barrier = threading.Barrier(len(previews))

    def run(index: int) -> None:
        engine = create_engine(database_url)
        authorization = FakeAuthorization.with_council(COUNCIL_USER)
        service = SnapshotImportService(
            lambda: SqlAlchemyUnitOfWork(engine),
            deployment=OBSERVED_DEPLOYMENT,
            profile=PROFILE,
            authorization=authorization,
        )
        try:
            barrier.wait(timeout=10)
            outcome = service.apply(
                source, previews[index], discord_user_id=COUNCIL_USER
            )
        except Exception as error:  # noqa: BLE001 - the outcome is the assertion
            outcome = error
        finally:
            engine.dispose()
        with lock:
            results.append(outcome)

    threads = [threading.Thread(target=run, args=(i,)) for i in range(len(previews))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    assert len(results) == len(previews), "a racing thread never finished"
    return results


def assert_one_durable_effect(engine) -> None:
    assert count(engine, "characters") == 1
    assert count(engine, "external_actor_mappings") == 1
    with engine.begin() as connection:
        applied = connection.execute(
            text("SELECT count(*) FROM snapshot_imports WHERE status = 'applied'")
        ).scalar_one()
        successes = connection.execute(
            text(
                "SELECT count(*) FROM audit_events "
                "WHERE action = 'snapshot_import.applied'"
            )
        ).scalar_one()
    assert applied == 1
    # No misleading success audit: the loser wrote no applied event.
    assert successes == 1


def assert_typed_and_consistent(loser, winner) -> None:
    """The loser is a typed duplicate carrying the winner's original result.

    "Typed" is the point of finding I-1: the loser used to be able to escape as
    a raw driver exception, and the test used to accept any exception at all.
    "Consistent" is finding B-1. "The winner's *original* result" is finding
    B-1R: `result_facts()` is every durable fact of the import, so comparing the
    two whole is stronger than comparing the handful of fields this used to, and
    a receptacle that mixed a fresh reconciliation into the receipt would fail
    it.
    """
    assert not isinstance(loser, BaseException), loser
    assert loser.duplicate is True
    assert loser.applied is False
    assert loser.result_facts() == winner.result_facts()
    # …and the loser reconciled nothing, so it has no run of its own to report.
    assert loser.report is None
    assert winner.report is not None


def test_two_concurrent_applies_of_the_same_input_produce_one_effect(
    services, database_url
):
    """Two real connections, two keys, one input. One winner, typed loser."""
    source = artifact()
    previews = [
        services["imports"].preview(source, request_key=f"req-{index}")
        for index in range(2)
    ]

    results = race(database_url, source, previews)

    winners = [r for r in results if getattr(r, "applied", False)]
    losers = [r for r in results if not getattr(r, "applied", False)]
    assert len(winners) == 1, results
    assert len(losers) == 1
    assert_typed_and_consistent(losers[0], winners[0])
    assert_one_durable_effect(services["engine"])


def test_two_concurrent_applies_of_the_same_key_produce_one_effect(
    services, database_url
):
    """The same key twice, concurrently: a retry that happens to overlap.

    Sequentially this is the early idempotency check; concurrently it is a lost
    race on `uq_snapshot_imports_request_key`, resolved by re-reading the
    winning row. Both must end with one durable effect and one typed duplicate.
    """
    source = artifact()
    previews = [
        services["imports"].preview(source, request_key="req-same") for _ in range(2)
    ]

    results = race(database_url, source, previews)

    winners = [r for r in results if getattr(r, "applied", False)]
    losers = [r for r in results if not getattr(r, "applied", False)]
    assert len(winners) == 1, results
    assert_typed_and_consistent(losers[0], winners[0])
    assert_one_durable_effect(services["engine"])
    assert count(services["engine"], "snapshot_imports") == 1


def test_a_concurrent_loser_never_escapes_as_a_driver_exception(
    services, database_url
):
    """The finding, stated as the assertion the old test was missing.

    `test_two_concurrent_applies_produce_one_effect` accepted *any* exception
    from the loser, so a raw `IntegrityError` carrying the failing statement and
    its bound parameters would have passed it.
    """
    source = artifact()
    previews = [
        services["imports"].preview(source, request_key=f"req-{index}")
        for index in range(3)
    ]

    results = race(database_url, source, previews)

    for result in results:
        if isinstance(result, BaseException):
            assert isinstance(result, (ImportRefused, UniquenessConflict)), result
            assert not isinstance(result, (IntegrityError, DBAPIError)), result
            assert_safe(result, and_not=("Brightlantern",))
    assert_one_durable_effect(services["engine"])


def test_a_concurrent_refusal_records_a_safe_audit_payload(services, database_url):
    """Whatever the losers wrote to history carries nothing unsafe."""
    source = artifact()
    previews = [
        services["imports"].preview(source, request_key=f"req-{index}")
        for index in range(3)
    ]

    race(database_url, source, previews)

    with services["engine"].begin() as connection:
        payloads = connection.execute(
            text(
                "SELECT payload FROM audit_events "
                "WHERE action = 'snapshot_import.refused'"
            )
        ).scalars().all()
    for payload in payloads:
        rendered = repr(payload)
        for unsafe in UNSAFE_FRAGMENTS + ("Brightlantern", "paladin", "Synthetic"):
            assert unsafe not in rendered, f"{unsafe!r} reached an audit row"
        assert payload["applied"] is False


# --- B-1: a request key is bound to the operation it was spent on --------------


def test_a_retry_of_the_same_operation_returns_the_original_record(services):
    source = artifact()
    first = apply_import(services, request_key="req-1", source=source)

    retry = apply_import(services, request_key="req-1", source=source)

    assert retry.duplicate is True
    assert retry.result_facts() == first.result_facts()
    assert count(services["engine"], "snapshot_imports") == 1
    assert count(services["engine"], "characters") == 1


# --- B-1R: the retry result is the original one, stored and read back ---------


def test_the_stored_summary_is_exactly_the_result_the_apply_returned(services):
    """The column and the receipt are the same facts, not two renderings.

    This is the storage half of the reconstruction: if `snapshot_imports.summary`
    held anything other than the returned reconciliation, a retry reading it back
    would return something the first apply never said.
    """
    source = artifact()
    outcome = apply_import(services, request_key="req-1", source=source)

    with services["engine"].begin() as connection:
        stored = connection.execute(
            text("SELECT summary FROM snapshot_imports WHERE request_key = 'req-1'")
        ).scalar_one()

    assert stored == outcome.reconciliation.summary()


def test_a_retry_returns_the_original_facts_reconstructed_from_postgresql(services):
    """Read back through the repository, not from anything held in memory.

    The retry runs on a service built over its own engine and its own unit of
    work, so the only route from the first apply to the second result is the
    `snapshot_imports` row: the ORM mapping, the `jsonb` round trip and
    `ReconciliationFacts.from_summary` are all in the path being tested.
    """
    source = artifact()
    first = apply_import(services, request_key="req-1", source=source)

    separate = SnapshotImportService(
        lambda: SqlAlchemyUnitOfWork(services["engine"]),
        deployment=OBSERVED_DEPLOYMENT,
        profile=PROFILE,
        authorization=FakeAuthorization.with_council(COUNCIL_USER),
    )
    preview = separate.preview(source, request_key="req-1")
    retry = separate.apply(source, preview, discord_user_id=COUNCIL_USER)

    assert retry.result_facts() == first.result_facts()
    # The facts the retry returns are the ones PostgreSQL holds, key for key.
    with services["engine"].begin() as connection:
        stored = connection.execute(
            text("SELECT summary FROM snapshot_imports WHERE request_key = 'req-1'")
        ).scalar_one()
    assert retry.reconciliation.summary() == stored


def test_a_retry_is_unchanged_after_the_database_has_moved_on(services):
    """The case that made the old receipt incoherent, against real PostgreSQL.

    Immediately after the first import the Actor is mapped, so a reconciliation
    run *now* reports one mapped Actor where the original reported one unmapped
    create candidate. Add an unrelated character and an unrelated snapshot row on
    top, and a recomputed report drifts further still. The retry's result must be
    the original's regardless.
    """
    source = artifact()
    first = apply_import(services, request_key="req-1", source=source)

    # Unrelated state, of the kinds that actually move a reconciliation: another
    # character in the table, and a second imported snapshot in another folder.
    create_character(services, display_name="Unrelated Later Character")
    other = ingest_bytes(
        fx.encode(
            fx.bundle(
                folders=(fx.folder(fx.ARCHIVE_FOLDER_ID, "Characters (retired)"),),
                selected_folder_ids=(fx.ARCHIVE_FOLDER_ID,),
                actors=(
                    fx.actor(
                        fx.SECOND_ACTOR_ID,
                        name="Retired Somebody",
                        folder_id=fx.ARCHIVE_FOLDER_ID,
                    ),
                ),
            )
        )
    )
    apply_import(services, request_key="req-other", source=other)

    retry = apply_import(services, request_key="req-1", source=source)

    assert retry.result_facts() == first.result_facts()
    # …and the original said what it said: an unmapped Actor it created.
    assert retry.reconciliation.unmapped == 1
    assert retry.reconciliation.mapped == 0
    assert retry.created_count == 1
    # A reconciliation run now would say the opposite, which is the point.
    fresh = services["imports"].preview(source, request_key="req-fresh")
    assert fresh.report.facts().mapped == 1
    assert fresh.report.facts().unmapped == 0


def test_a_retry_writes_no_second_row_event_character_or_mapping(services):
    source = artifact()
    apply_import(services, request_key="req-1", source=source)
    before = {
        table: count(services["engine"], table)
        for table in ("snapshot_imports", "audit_events", "characters",
                      "external_actor_mappings", "foundry_snapshots")
    }

    apply_import(services, request_key="req-1", source=source)

    after = {table: count(services["engine"], table) for table in before}
    assert after == before


def test_a_reused_key_with_a_different_artifact_is_refused_by_postgresql(services):
    """The blocking defect, against the real schema."""
    apply_import(services, request_key="req-1")
    tampered = ingest_bytes(
        fx.tamper(fx.encode(fx.bundle()), find=b"Brightlantern", replace=b"Brightlantexn")
    )
    preview = services["imports"].preview(tampered, request_key="req-1")

    with pytest.raises(ImportRefused) as refusal:
        services["imports"].apply(tampered, preview, discord_user_id=COUNCIL_USER)

    assert refusal.value.code == "request_key_conflict"
    assert "the snapshot artifact" in str(refusal.value)
    with services["engine"].begin() as connection:
        applied = connection.execute(
            text("SELECT count(*) FROM snapshot_imports WHERE status = 'applied'")
        ).scalar_one()
        refused = connection.execute(
            text(
                "SELECT summary FROM snapshot_imports WHERE status = 'refused'"
            )
        ).scalars().all()
    assert applied == 1
    assert len(refused) == 1
    assert refused[0]["refusal_code"] == "request_key_conflict"


def test_the_stored_operation_digest_is_the_binding_of_the_applied_operation(services):
    source = artifact()
    preview = services["imports"].preview(source, request_key="req-1")

    services["imports"].apply(source, preview, discord_user_id=COUNCIL_USER)

    with services["engine"].begin() as connection:
        digest = connection.execute(
            text(
                "SELECT operation_digest FROM snapshot_imports "
                "WHERE request_key = 'req-1'"
            )
        ).scalar_one()
    assert digest == preview.binding.operation_digest()
    assert len(digest) == 64


# --- S-1: the raw request key reaches the lookup column and nothing else ------

#: A printable, valid request key that a caller could plausibly send and that no
#: audit row should ever hold. Synthetic throughout: the address, the name and
#: the token-shaped string are invented for this test and belong to nobody.
PRIVATE_LOOKING_KEY = (
    "MARKER-KEY player=Testperson Nobody email=nobody@example.invalid "
    "token=MARKER-TOKEN-abcdef0123456789"
)

#: Substrings of it that must not appear anywhere permanent, individually — so
#: the assertion does not pass merely because the whole string was reformatted.
PRIVATE_FRAGMENTS = (
    "MARKER-KEY",
    "Testperson Nobody",
    "nobody@example.invalid",
    "MARKER-TOKEN-abcdef0123456789",
)


def test_the_raw_request_key_is_stored_only_in_the_lookup_column(services):
    """Every permanent column in the database, checked for the key's text."""
    from application.foundry.import_service import request_key_digest

    source = artifact()
    apply_import(services, request_key=PRIVATE_LOOKING_KEY, source=source)

    with services["engine"].begin() as connection:
        keys = connection.execute(
            text("SELECT request_key FROM snapshot_imports")
        ).scalars().all()
        # Every text-ish column of every retained table, rendered together. A
        # narrower query would only prove the columns the author thought of.
        rendered = repr(
            [
                dict(row)
                for statement in (
                    "SELECT * FROM audit_events",
                    "SELECT * FROM foundry_snapshots",
                    "SELECT id, snapshot_id, folder_id, folder_path, "
                    "profile_version, operation_digest, status, mode, summary, "
                    "correlation_id FROM snapshot_imports",
                    "SELECT * FROM characters",
                    "SELECT * FROM external_actor_mappings",
                )
                for row in connection.execute(text(statement)).mappings().all()
            ]
        )

    assert keys == [PRIVATE_LOOKING_KEY]
    for fragment in PRIVATE_FRAGMENTS:
        assert fragment not in rendered, f"{fragment!r} escaped the lookup column"
    # …and what the audit row carries instead is the declared digest.
    with services["engine"].begin() as connection:
        payload = connection.execute(
            text(
                "SELECT payload FROM audit_events "
                "WHERE action = 'snapshot_import.applied'"
            )
        ).scalar_one()
    assert payload["request_key_digest"] == request_key_digest(PRIVATE_LOOKING_KEY)
    assert "request_key" not in payload


def test_a_refused_attempt_stores_no_request_key_text_at_all(services):
    """A refused row is never looked up by key, so it does not keep one."""
    apply_import(services, request_key=PRIVATE_LOOKING_KEY)
    tampered = ingest_bytes(
        fx.tamper(fx.encode(fx.bundle()), find=b"Brightlantern", replace=b"Brightlantexn")
    )
    preview = services["imports"].preview(tampered, request_key=PRIVATE_LOOKING_KEY)

    with pytest.raises(ImportRefused) as refusal:
        services["imports"].apply(tampered, preview, discord_user_id=COUNCIL_USER)

    # Not even the refusal message the operator is shown quotes the key.
    for fragment in PRIVATE_FRAGMENTS:
        assert fragment not in str(refusal.value)
    with services["engine"].begin() as connection:
        refused = connection.execute(
            text(
                "SELECT request_key FROM snapshot_imports WHERE status = 'refused'"
            )
        ).scalars().all()
    assert len(refused) == 1
    assert refused[0].startswith("refused:")
    for fragment in PRIVATE_FRAGMENTS:
        assert fragment not in refused[0]


# --- append-only, enforced by PostgreSQL --------------------------------------


@pytest.mark.parametrize("table", APPEND_ONLY_TABLES)
def test_updating_an_append_only_table_is_rejected_by_the_database(
    db_connection, table
):
    _seed_append_only(db_connection, table)

    with pytest.raises(DBAPIError) as refusal:
        db_connection.execute(text(f"UPDATE {table} SET correlation_id = gen_random_uuid()"))

    assert "append-only" in str(refusal.value)


@pytest.mark.parametrize("table", APPEND_ONLY_TABLES)
def test_deleting_from_an_append_only_table_is_rejected_by_the_database(
    db_connection, table
):
    _seed_append_only(db_connection, table)

    with pytest.raises(DBAPIError) as refusal:
        db_connection.execute(text(f"DELETE FROM {table}"))

    assert "append-only" in str(refusal.value)


def test_the_trigger_applies_to_the_schema_owner_too(db_connection):
    # These tests connect as the schema owner. The refusal above is therefore
    # not a grant check: it is the database refusing history mutation outright.
    owner = db_connection.execute(text("SELECT current_user")).scalar_one()
    table_owner = db_connection.execute(
        text("SELECT tableowner FROM pg_tables WHERE tablename = 'audit_events'")
    ).scalar_one()

    assert owner == table_owner


def test_platform_initialization_holds_at_most_one_row(db_connection):
    statement = text(
        "INSERT INTO platform_initialization (singleton, supervisor, "
        "profile_version, correlation_id) VALUES (true, :who, :profile, :c)"
    )
    db_connection.execute(
        statement, {"who": "Peter Duscha", "profile": PROFILE.version, "c": uuid4()}
    )

    with pytest.raises(IntegrityError):
        db_connection.execute(
            statement,
            {"who": "Somebody Else", "profile": PROFILE.version, "c": uuid4()},
        )


# --- mapping constraints ------------------------------------------------------


def test_a_world_actor_pair_can_only_be_mapped_once(services):
    """The constraint fires, and it reaches the caller as a typed rule (I-1)."""
    apply_import(services)
    character = create_character(services, "Another Testcharacter")

    from application.snapshots import ExternalActorMapping

    with pytest.raises(UniquenessConflict) as conflict:
        with services["factory"]() as unit:
            unit.external_actor_mappings.add(
                ExternalActorMapping(
                    character_id=character.id,
                    world_id="the-guild",
                    external_actor_id=fx.FIRST_ACTOR_ID,
                    relink_fingerprint="synthetic",
                )
            )
            unit.commit()

    assert conflict.value.rule == "external_actor_mapping.world_actor"
    assert_safe(conflict.value)


def test_a_character_has_one_mapping_per_world(services):
    from application.snapshots import ExternalActorMapping

    character = create_character(services)
    with services["factory"]() as unit:
        unit.external_actor_mappings.add(
            ExternalActorMapping(
                character_id=character.id,
                world_id="the-guild",
                external_actor_id=fx.FIRST_ACTOR_ID,
                relink_fingerprint="synthetic",
            )
        )
        unit.commit()

    with pytest.raises(UniquenessConflict) as conflict:
        with services["factory"]() as unit:
            unit.external_actor_mappings.add(
                ExternalActorMapping(
                    character_id=character.id,
                    world_id="the-guild",
                    external_actor_id=fx.SECOND_ACTOR_ID,
                    relink_fingerprint="synthetic",
                )
            )
            unit.commit()

    assert conflict.value.rule == "external_actor_mapping.character_world"
    assert_safe(conflict.value)


# --- bootstrap ----------------------------------------------------------------


def test_a_supervised_bootstrap_needs_no_council_member(services):
    source = artifact()
    preview = services["imports"].preview(source, request_key="req-boot")

    outcome = services["imports"].apply(
        source, preview, bootstrap=SupervisedBootstrap("Peter Duscha")
    )

    assert outcome.applied
    with services["engine"].begin() as connection:
        row = connection.execute(
            text("SELECT mode, supervisor, actor_capability FROM snapshot_imports")
        ).one()
    assert row.mode == "bootstrap"
    assert row.supervisor == "Peter Duscha"
    assert row.actor_capability == "system"


def test_the_bootstrap_disables_itself_after_its_first_success(services):
    source = artifact()
    services["imports"].apply(
        source,
        services["imports"].preview(source, request_key="req-boot"),
        bootstrap=SupervisedBootstrap("Peter Duscha"),
    )

    assert services["gate"].state().available is False
    later = artifact(fx.bundle(exported_at="2026-08-03T09:15:00Z"))
    with pytest.raises(ImportRefused) as refusal:
        services["imports"].apply(
            later,
            services["imports"].preview(later, request_key="req-boot-2"),
            bootstrap=SupervisedBootstrap("Peter Duscha"),
        )

    assert refusal.value.code == "bootstrap_unavailable"
    assert "not an authorization bypass" in str(refusal.value)


def test_the_bootstrap_refuses_a_dataset_that_is_not_empty(services):
    create_character(services, "Pre-existing Testcharacter")
    source = artifact()

    with pytest.raises(ImportRefused) as refusal:
        services["imports"].apply(
            source,
            services["imports"].preview(source, request_key="req-boot"),
            bootstrap=SupervisedBootstrap("Peter Duscha"),
        )

    assert refusal.value.code == "bootstrap_requires_empty_dataset"


def test_the_initialization_row_is_written_by_the_same_transaction(services):
    source = artifact()
    services["imports"].apply(
        source,
        services["imports"].preview(source, request_key="req-boot"),
        bootstrap=SupervisedBootstrap("Peter Duscha"),
    )

    with services["engine"].begin() as connection:
        row = connection.execute(
            text(
                "SELECT supervisor, profile_version, snapshot_checksum "
                "FROM platform_initialization"
            )
        ).one()
    assert row.supervisor == "Peter Duscha"
    assert row.profile_version == PROFILE.version
    assert len(row.snapshot_checksum) == 64
    assert count(services["engine"], "characters") == 1


def test_a_bootstrap_that_is_refused_leaves_the_gate_open(services):
    # A blocked run rolls back, so the platform stays uninitialized and the
    # corrected retry can still bootstrap.
    create_character(services, "Testcharacter Brightlantern")
    source = artifact()
    with pytest.raises(ImportRefused):
        services["imports"].apply(
            source,
            services["imports"].preview(source, request_key="req-boot"),
            bootstrap=SupervisedBootstrap("Peter Duscha"),
        )

    assert count(services["engine"], "platform_initialization") == 0


def test_a_bootstrap_requires_a_named_supervisor():
    with pytest.raises(ValueError):
        SupervisedBootstrap("  ")


# --- helpers ------------------------------------------------------------------


def _insert_snapshot(connection, checksum: str | None = None):
    snapshot_id = uuid4()
    connection.execute(
        text(
            "INSERT INTO foundry_snapshots (id, checksum, size_bytes, "
            "schema_version, exporter_id, exporter_version, exported_at, "
            "world_id, world_title, core_version, system_id, system_version, "
            "actor_count, selected_folder_ids, correlation_id) VALUES "
            "(:id, :checksum, 10, 1, 'e', '1.0.0', now(), 'the-guild', "
            "'The Guild', '14.367', 'dnd5e', '5.3.3', 1, '[]'::jsonb, :c)"
        ),
        {
            "id": snapshot_id,
            "checksum": checksum or uuid4().hex + uuid4().hex,
            "c": uuid4(),
        },
    )
    return snapshot_id


#: The Council member these raw fixtures act as.
#:
#: Naming one is not decoration. Migration 0006 added
#: `ck_snapshot_imports_import_has_an_attribution`, which closes the gap that a
#: `guild_council` import row could previously name nobody at all. These fixtures
#: exercise the *uniqueness* rules, so their capability is real and their actor
#: has to be too.
_COUNCIL_ACTOR = 700000000000000101


def _insert_import(
    connection,
    snapshot_id,
    *,
    request_key: str,
    status: str = "refused",
    digest: str | None = "a" * 64,
):
    connection.execute(
        text(
            "INSERT INTO discord_users (id, username) VALUES (:actor, 'council-fixture') "
            "ON CONFLICT (id) DO NOTHING"
        ),
        {"actor": _COUNCIL_ACTOR},
    )
    connection.execute(
        text(
            "INSERT INTO snapshot_imports (id, snapshot_id, folder_id, "
            "folder_path, profile_version, request_key, operation_digest, "
            "status, mode, actor_discord_user_id, actor_capability, summary, "
            "correlation_id) VALUES "
            "(:id, :snapshot, :folder, '/actors/x', :profile, :key, :digest, "
            ":status, 'council', :actor, 'guild_council', '{}'::jsonb, :c)"
        ),
        {
            "id": uuid4(),
            "snapshot": snapshot_id,
            "folder": fx.ACTIVE_FOLDER_ID,
            "profile": PROFILE.version,
            "key": request_key,
            "digest": digest,
            "status": status,
            "actor": _COUNCIL_ACTOR,
            "c": uuid4(),
        },
    )


def _seed_append_only(connection, table: str) -> None:
    if table == "audit_events":
        connection.execute(
            text(
                "INSERT INTO audit_events (id, actor_capability, action, "
                "entity_type, entity_id, source, correlation_id, payload) VALUES "
                "(:id, 'system', 'test', 'character', 'x', 'import', :c, "
                "'{}'::jsonb)"
            ),
            {"id": uuid4(), "c": uuid4()},
        )
        return
    if table == "foundry_snapshots":
        _insert_snapshot(connection)
        return
    if table == "snapshot_imports":
        _insert_import(connection, _insert_snapshot(connection), request_key="seed")
        return
    raise AssertionError(f"no seed defined for append-only table {table!r}")


# --- backup, restore and idempotent rerun -------------------------------------


def _inventory(engine) -> dict[str, int]:
    """Table name → row count, for every table in the schema."""
    with engine.begin() as connection:
        tables = [
            row[0]
            for row in connection.execute(
                text(
                    "SELECT tablename FROM pg_tables WHERE schemaname='public' "
                    "ORDER BY tablename"
                )
            )
        ]
        return {
            table: connection.execute(
                text(f"SELECT count(*) FROM {table}")
            ).scalar_one()
            for table in tables
        }


def test_restore_matches_the_pre_drill_inventory_and_supports_idempotent_rerun(
    services, database_url, tmp_path
):
    """Threshold T-9, end to end.

    Two claims, and the second is the one a backup drill usually skips: that the
    restored database can be *worked on* again. Restoring a database that then
    duplicates every identity on the next import would satisfy a naive inventory
    check and still be useless.
    """
    import shutil
    import subprocess

    for tool in ("pg_dump", "pg_restore", "psql"):
        if shutil.which(tool) is None:
            pytest.skip(f"{tool} is not installed on this host.")

    engine = services["engine"]
    source = artifact()
    first = apply_import(services, source=source, request_key="pre-drill")
    assert first.applied

    before = _inventory(engine)
    assert before["characters"] == 1
    assert before["foundry_snapshots"] == 1
    assert before["snapshot_imports"] == 1

    # Release pooled connections so DROP SCHEMA cannot block on an idle session.
    engine.dispose()

    drill = Path(__file__).resolve().parents[1] / "infra" / "postgresql" / (
        "backup-restore-drill.sh"
    )
    database = make_url(database_url).database
    completed = subprocess.run(
        ["bash", str(drill), database],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "Restore verified" in completed.stdout

    after = _inventory(engine)
    assert after == before, "the restored inventory differs from the pre-drill one"

    # The same immutable input, applied again to the restored database. It is a
    # typed duplicate: one durable effect existed before the drill and one
    # exists now.
    rerun = apply_import(services, source=source, request_key="post-restore")

    assert rerun.duplicate
    assert _inventory(engine) == before


# --- I-1: the loser's resolution, driven deterministically ---------------------
#
# The threaded races above prove the constraints fire and that the invariants
# hold under real concurrency, but which branch of the resolution a loser takes
# depends on timing. These two drive the resolution directly, against the real
# database, so both branches are exercised on every run rather than when the
# scheduler happens to cooperate. Calling the private method is deliberate: the
# thing under test is the resolution, and the alternative is a test that passes
# for the wrong reason most of the time.


def test_conflict_resolution_reads_the_winning_row_from_postgresql(services):
    source = artifact()
    winner = apply_import(services, request_key="req-1", source=source)
    preview = services["imports"].preview(source, request_key="req-1")
    snapshot = services["imports"].parse(source)

    loser = services["imports"]._resolve_conflict(
        snapshot,
        preview,
        conflict=UniquenessConflict("snapshot_import.request_key"),
        folder=fx.ACTIVE_FOLDER_ID,
        digest=preview.binding.operation_digest(),
    )

    assert_typed_and_consistent(loser, winner)
    assert_one_durable_effect(services["engine"])


def test_an_unresolvable_conflict_against_postgresql_is_a_typed_safe_refusal(services):
    """No winning row describes this operation, so it is refused, not duplicated."""
    source = artifact()
    preview = services["imports"].preview(source, request_key="req-1")
    snapshot = services["imports"].parse(source)

    with pytest.raises(ImportRefused) as refusal:
        services["imports"]._resolve_conflict(
            snapshot,
            preview,
            conflict=UniquenessConflict("external_actor_mapping.world_actor"),
            folder=fx.ACTIVE_FOLDER_ID,
            digest=preview.binding.operation_digest(),
        )

    assert refusal.value.code == "concurrent_import"
    assert_safe(refusal.value, and_not=("Brightlantern",))
    assert count(services["engine"], "characters") == 0


def test_a_reused_key_claimed_by_a_different_operation_is_refused_on_the_conflict_path(
    services,
):
    """B-1 holds where the collision is a lost race, not only an early check."""
    other = ingest_bytes(
        fx.tamper(fx.encode(fx.bundle()), find=b"Brightlantern", replace=b"Brightlantexn")
    )
    apply_import(services, request_key="req-1", source=other)

    source = artifact()
    preview = services["imports"].preview(source, request_key="req-1")
    snapshot = services["imports"].parse(source)

    with pytest.raises(ImportRefused) as refusal:
        services["imports"]._resolve_conflict(
            snapshot,
            preview,
            conflict=UniquenessConflict("snapshot_import.request_key"),
            folder=fx.ACTIVE_FOLDER_ID,
            digest=preview.binding.operation_digest(),
        )

    assert refusal.value.code == "request_key_conflict"
    assert "the snapshot artifact" in str(refusal.value)


def test_a_foreign_key_violation_is_a_persistence_error_not_a_conflict(services):
    """`IntegrityError` is wider than "somebody else won".

    A foreign-key violation is the database refusing something the application
    should never have attempted. Filing it as a conflict would send a caller
    looking for a winning row that does not exist, and — worse — could let it
    report a duplicate for an import that never happened.
    """
    from application.audit import ActorCapability, AuditEvent, AuditSource

    with pytest.raises(PersistenceError) as failure:
        with services["factory"]() as unit:
            unit.audit.record(
                AuditEvent(
                    action="synthetic.probe",
                    entity_type="character",
                    entity_id="probe",
                    source=AuditSource.IMPORT,
                    actor_capability=ActorCapability.GUILD_COUNCIL,
                    # No such Discord user: `audit_events` has a foreign key.
                    actor_discord_user_id=4200000000000000999,
                    correlation_id=uuid4(),
                    payload={},
                )
            )
            unit.commit()

    assert failure.value.sqlstate == "23503"
    assert_safe(failure.value)
    assert count(services["engine"], "audit_events") == 0


def test_a_unique_violation_carries_a_conflict_sqlstate(db_connection):
    """The classification is by SQLSTATE, checked against the real server."""
    from adapters.database.translation import CONFLICT_SQLSTATES

    snapshot_id = _insert_snapshot(db_connection)
    _insert_import(db_connection, snapshot_id, request_key="req-1")

    with pytest.raises(IntegrityError) as duplicate:
        _insert_import(db_connection, snapshot_id, request_key="req-1")

    assert duplicate.value.orig.sqlstate in CONFLICT_SQLSTATES


def test_a_check_violation_does_not_carry_a_conflict_sqlstate(db_connection):
    """…so it cannot be mistaken for a lost race and resolved into a duplicate."""
    from adapters.database.translation import CONFLICT_SQLSTATES

    snapshot_id = _insert_snapshot(db_connection)

    with pytest.raises(IntegrityError) as bad_digest:
        _insert_import(
            db_connection, snapshot_id, request_key="req-1", digest="not-a-digest"
        )

    assert bad_digest.value.orig.sqlstate not in CONFLICT_SQLSTATES


def test_the_database_refuses_an_import_row_without_an_operation_digest(db_connection):
    """B-1's binding is a schema rule, not only an application one."""
    snapshot_id = _insert_snapshot(db_connection)

    with pytest.raises(IntegrityError):
        _insert_import(db_connection, snapshot_id, request_key="req-1", digest=None)
