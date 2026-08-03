"""Phase 2 against real PostgreSQL.

A mock does not prove a constraint, a trigger, a transaction boundary or a
concurrent outcome. Everything in this file runs against the disposable
`freedom_test` database over the Unix-domain socket, and every assertion here is
about what PostgreSQL actually did.
"""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError, IntegrityError

from application.authorization import SupervisedBootstrap
from application.bootstrap import BootstrapGate
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
        "'e', '1.0.0', :exported_at, 'the-guild', 'The Guild', '14.365', 'dnd5e', "
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
                "'The Guild', '14.365', 'dnd5e', '5.3.3', 1, '[]'::jsonb, :c)"
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
    assert "character.display_name" in outcome.report.summary()["fields_out_of_date"]


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


def test_two_concurrent_applies_produce_one_effect(services, database_url):
    """Two real connections race the same input. Only one may win."""
    source = artifact()
    previews = [
        services["imports"].preview(source, request_key=f"req-{index}")
        for index in range(2)
    ]
    results: list[object] = []
    barrier = threading.Barrier(2)

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
            results.append(
                service.apply(source, previews[index], discord_user_id=COUNCIL_USER)
            )
        except Exception as error:  # noqa: BLE001 - the outcome is the assertion
            results.append(error)
        finally:
            engine.dispose()

    threads = [threading.Thread(target=run, args=(index,)) for index in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    successes = [r for r in results if getattr(r, "applied", False)]
    assert len(successes) == 1, results
    # One character, one mapping, one applied import — whatever the loser did.
    assert count(services["engine"], "characters") == 1
    assert count(services["engine"], "external_actor_mappings") == 1
    with services["engine"].begin() as connection:
        applied = connection.execute(
            text("SELECT count(*) FROM snapshot_imports WHERE status = 'applied'")
        ).scalar_one()
    assert applied == 1


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
    apply_import(services)
    character = create_character(services, "Another Testcharacter")

    from application.snapshots import ExternalActorMapping

    with pytest.raises(IntegrityError):
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

    with pytest.raises(IntegrityError):
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
            "'The Guild', '14.365', 'dnd5e', '5.3.3', 1, '[]'::jsonb, :c)"
        ),
        {
            "id": snapshot_id,
            "checksum": checksum or uuid4().hex + uuid4().hex,
            "c": uuid4(),
        },
    )
    return snapshot_id


def _insert_import(connection, snapshot_id, *, request_key: str, status: str = "refused"):
    connection.execute(
        text(
            "INSERT INTO snapshot_imports (id, snapshot_id, folder_id, "
            "folder_path, profile_version, request_key, status, mode, "
            "actor_capability, summary, correlation_id) VALUES "
            "(:id, :snapshot, :folder, '/actors/x', :profile, :key, :status, "
            "'council', 'guild_council', '{}'::jsonb, :c)"
        ),
        {
            "id": uuid4(),
            "snapshot": snapshot_id,
            "folder": fx.ACTIVE_FOLDER_ID,
            "profile": PROFILE.version,
            "key": request_key,
            "status": status,
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
