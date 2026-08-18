"""TC-MIG-07: dump → run the stage → restore → run again → the same result.

The traceability contract classes this row `supervised`, meaning a maintainer runs
`infra/postgresql/backup-restore-drill.sh` and records what happened. This file makes
it **automated** against the guarded disposable database instead, which is a
strengthening rather than a substitution: the drill script remains the operator
procedure for a real host, and this is the same round trip driven by the suite so it
runs on every change rather than once per gate.

## What the round trip has to establish

Not "the dump succeeded" — plan §14.3 is explicit that a restore test is the
requirement, because a backup nobody has restored is a hypothesis. So:

1. the sources are seeded and **then** dumped, so the dump is a pre-run state;
2. a C-04 run writes a run, its proposals and its candidates;
3. the schema is destroyed and the dump restored, and the run is *gone* — which is
   what proves the restore replaced state rather than merging into it; and
4. a second C-04 run over the restored sources produces the **same** resolution: the
   same buckets, the same proposal per character, the same candidate set.

Step 4 is the one that matters for M-2. §7.5 requires a second run over unchanged
sources to produce the same proposal set, and a restore is the strongest available way
to make "unchanged sources" true — the database is byte-restored rather than tidied
up by the test.

## Why this is safe to run inside the suite

`migrated_database` is session-scoped and migrates from `base` to `head`, so a test
that drops and restores the schema leaves an equivalent database behind. The teardown
nonetheless re-migrates from base unconditionally: an assertion that fails between the
drop and the restore would otherwise leave every later case in the session running
against an empty or half-restored database, and a suite that reports twenty unrelated
failures because one case failed early is a suite whose evidence nobody can read.

The connection target is verified as a **Unix-domain socket** before anything is
dumped or dropped, by the same `adapters/database/safety` helper the drill script and
every migration entry point use. A loopback TCP address is not proof that the server
is on this host (`ssh -L 5432:localhost:5432 elsewhere` presents exactly that shape),
and this test drops a schema.
"""
from __future__ import annotations

import os
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import text

from adapters.database.safety import (
    UnsafeDatabaseTargetError,
    verify_connected_unix_socket_target,
)
from adapters.web.repositories import (
    IdentityEvidenceSourceRepository,
    IdentityProposalRepository,
)
from application.web.identity_evidence import (
    IdentityEvidenceRunService,
    SheetCharacterRow,
    SheetPlayer,
)
from tests.conftest import EXPECTED_TEST_DATABASE, run_alembic
from tests.web.conftest import utcnow
from tests.web.portal_fixtures import (
    clean_p3_2_tables,
    make_character,
    map_sheet_row,
    seed_discord_member,
)
from tests.web_fixtures import TEST_GUILD_ID

pytestmark = pytest.mark.database

#: Synthetic. One person resolves; two share a username, making an ambiguity whose
#: candidate rows must come back identically after the restore.
ADA = 700000000000015001
TWIN_A = 700000000000015002
TWIN_B = 700000000000015003

CHARACTER_TAB = "Characters"

#: libpq variables a child process must not inherit: any of them can redirect
#: `--dbname=freedom_test` to another server, and step 3 drops that server's schema.
UNSAFE_LIBPQ = (
    "PGHOST",
    "PGHOSTADDR",
    "PGPORT",
    "PGDATABASE",
    "PGSERVICE",
    "PGSERVICEFILE",
)


def child_environment() -> dict[str, str]:
    return {
        key: value
        for key, value in os.environ.items()
        if key not in UNSAFE_LIBPQ
    }


def sheet_sources():
    """The two shaped source lists a run is given. Identical on both runs."""
    characters = [
        SheetCharacterRow(row_number=3, player_name="Ada"),
        SheetCharacterRow(row_number=4, player_name="Bea"),
        SheetCharacterRow(row_number=5, player_name="Cyd"),
    ]
    players = [
        SheetPlayer("Ada", "ada.one", False),
        SheetPlayer("Bea", "shared.name", True),
        SheetPlayer("Cyd", "nobody.in.guild", False),
    ]
    return characters, players


def execute_run(engine):
    """One C-04 evidence run in one transaction, exactly as the tool drives it.

    There is no mode parameter: every run of `identity_migration_runs` is a C-04
    evidence run, `CHECK`-ed so by the schema, and it is the only mode the
    command has. The drill therefore re-runs C-04, which is also what makes the
    comparison meaningful — the same deterministic resolver over the same
    restored sources has to produce the same evidence.
    """
    characters, players = sheet_sources()
    with engine.begin() as connection:
        return IdentityEvidenceRunService(
            sources=IdentityEvidenceSourceRepository(connection),
            proposals=IdentityProposalRepository(connection),
            guild_id=TEST_GUILD_ID,
        ).run(
            sheet_character_rows=characters,
            sheet_players=players,
            sheet_tab=CHARACTER_TAB,
            source_label="Characters!C + Players!A/B/D",
            profile_version="drill",
            correlation_id=uuid4(),
            now=utcnow(),
        )


def resolution_shape(engine):
    """The run's *content*, keyed by things a restore cannot change.

    Deliberately **not** keyed on the run id or the proposal ids: those are fresh
    UUIDs on every run, so comparing them would compare two things that are supposed
    to differ. What must be identical is the arithmetic and, per character, the
    resolution, the Sheet evidence and the candidate set.
    """
    with engine.begin() as connection:
        totals = (
            connection.execute(
                text(
                    "SELECT source_characters, source_players, already_linked, proposed, "
                    "ambiguous, unresolved, dry_run FROM identity_migration_runs"
                )
            )
            .mappings()
            .all()
        )
        proposals = (
            connection.execute(
                text(
                    "SELECT p.character_id, c.display_name, p.sheet_player_name, "
                    "p.sheet_discord_name, p.active_dm, p.proposed_subject, p.resolution, "
                    "(SELECT string_agg(k.subject, ',' ORDER BY k.subject) FROM "
                    "identity_link_proposal_candidates k WHERE k.proposal_id = p.id) "
                    "AS candidates FROM identity_link_proposals p "
                    "JOIN characters c ON c.id = p.character_id "
                    "ORDER BY c.display_name"
                )
            )
            .mappings()
            .all()
        )
    return (
        [dict(row) for row in totals],
        [dict(row) for row in proposals],
    )


def source_inventory(engine):
    """The seeded sources, so the restore can be shown to have brought them back."""
    with engine.begin() as connection:
        return {
            "characters": connection.execute(
                text("SELECT count(*) FROM characters")
            ).scalar(),
            "mappings": connection.execute(
                text("SELECT count(*) FROM sheet_row_mappings")
            ).scalar(),
            "members": connection.execute(
                text("SELECT count(*) FROM discord_guild_memberships")
            ).scalar(),
        }


def test_backup_run_restore_rerun_produces_the_same_result(
    tmp_path, database_url, migrated_database
):
    """TC-MIG-07, end to end, against the guarded disposable database."""
    # -- 0. The target is a Unix-domain socket on this host, or nothing happens ----
    try:
        with migrated_database.connect() as connection:
            verify_connected_unix_socket_target(
                connection, expected_database=EXPECTED_TEST_DATABASE
            )
    except UnsafeDatabaseTargetError as error:
        pytest.fail(f"refusing to dump and drop a schema: {error}")

    dump = tmp_path / "pre-run.dump"
    try:
        # -- 1. Seed the sources, then dump ---------------------------------------
        with migrated_database.begin() as connection:
            clean_p3_2_tables(connection)
            for offset, name in enumerate(("Alia Storm", "Brand Vale", "Cere Ash")):
                character_id = make_character(connection, display_name=name)
                map_sheet_row(
                    connection, character_id=character_id, row_index=3 + offset
                )
            seed_discord_member(connection, subject=ADA, username="ada.one")
            seed_discord_member(connection, subject=TWIN_A, username="shared.name")
            seed_discord_member(connection, subject=TWIN_B, username="SHARED.NAME")
        before = source_inventory(migrated_database)
        assert before["characters"] == 3 and before["mappings"] == 3

        subprocess.run(
            [
                "pg_dump",
                "--format=custom",
                f"--dbname={EXPECTED_TEST_DATABASE}",
                f"--file={dump}",
            ],
            check=True,
            env=child_environment(),
            capture_output=True,
            text=True,
        )
        assert dump.exists() and dump.stat().st_size > 0, "the dump is empty"

        # -- 2. Run the stage -----------------------------------------------------
        first = execute_run(migrated_database)
        first_shape = resolution_shape(migrated_database)
        assert first.totals.balances()
        assert (first.totals.proposed, first.totals.ambiguous, first.totals.unresolved) == (
            1,
            1,
            1,
        )
        assert first.candidates_written == 3, "one proposed match plus two twins"

        # -- 3. Destroy and restore ----------------------------------------------
        migrated_database.dispose()
        subprocess.run(
            [
                "psql",
                f"--dbname={EXPECTED_TEST_DATABASE}",
                "--quiet",
                "--no-psqlrc",
                "-c",
                "DROP SCHEMA public CASCADE; CREATE SCHEMA public;",
            ],
            check=True,
            env=child_environment(),
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                "pg_restore",
                f"--dbname={EXPECTED_TEST_DATABASE}",
                "--no-owner",
                "--no-privileges",
                str(dump),
            ],
            check=True,
            env=child_environment(),
            capture_output=True,
            text=True,
        )

        # The sources are back, and the run is **gone**: a restore that merged into
        # the current state instead of replacing it would leave the run behind, and
        # step 4 would then be comparing a rerun against its own predecessor.
        assert source_inventory(migrated_database) == before
        with migrated_database.begin() as connection:
            assert (
                connection.execute(
                    text("SELECT count(*) FROM identity_migration_runs")
                ).scalar()
                == 0
            )
            assert (
                connection.execute(
                    text("SELECT count(*) FROM identity_link_proposal_candidates")
                ).scalar()
                == 0
            )

        # -- 4. Run it again: the same result -------------------------------------
        second = execute_run(migrated_database)
        second_shape = resolution_shape(migrated_database)

        assert second.totals == first.totals
        assert second.proposals_written == first.proposals_written
        assert second.candidates_written == first.candidates_written
        assert second_shape == first_shape, (
            "a rerun over restored sources resolved differently: "
            f"{first_shape} != {second_shape}"
        )
        # And still no authorization row, on either side of the restore.
        with migrated_database.begin() as connection:
            assert (
                connection.execute(
                    text("SELECT count(*) FROM character_access")
                ).scalar()
                == 0
            )
    finally:
        # Unconditional, and from `base`: a failure between the drop and the restore
        # would otherwise leave every later case in the session running against an
        # empty database.
        migrated_database.dispose()
        run_alembic(database_url, "downgrade", "base")
        run_alembic(database_url, "upgrade", "head")


def test_the_drill_script_still_refuses_a_non_disposable_target():
    """The operator procedure's own guard, asserted rather than assumed.

    This file automates the round trip; `infra/postgresql/backup-restore-drill.sh`
    remains the procedure for a real host, and the property that makes it safe to
    document is that it refuses anything but the disposable database. Invoked with a
    production-shaped name and expected to refuse **without** connecting.
    """
    from pathlib import Path

    script = Path(__file__).resolve().parents[2] / "infra" / "postgresql" / (
        "backup-restore-drill.sh"
    )
    assert script.exists()
    result = subprocess.run(
        ["bash", str(script), "freedom_prod"],
        capture_output=True,
        text=True,
        env=child_environment(),
        cwd=script.parents[2],
    )
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "freedom_prod" in combined or "refus" in combined.lower(), combined
