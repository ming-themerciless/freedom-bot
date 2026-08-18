"""Revision 0010: `upgrade → downgrade → upgrade`, and what the downgrade costs.

The reversibility half of TC-MIG-04 and TC-MIG-15's inventory discipline, applied to
the one revision P3.2 adds. Three properties, and the third is the one a
round-trip test usually forgets:

1. **The objects appear and disappear.** Three tables, two indexes, every check
   constraint and every foreign key, read from the catalogue rather than from the
   migration's source — a migration asserted against itself proves nothing.
2. **The round trip is exact.** The schema after `upgrade → downgrade → upgrade`
   equals the schema after the first upgrade, constraint for constraint and index
   for index, and every row outside the three tables survives untouched.
3. **The downgrade's data cost is what the revision says it is.** It drops evidence
   and decisions and *never* an authorization row: a `character_access` row created
   by a confirmation survives with its own reason, grantor and correlation id, so
   what is lost is the record of **which proposal** prompted a link and never the
   link itself or its audit event.

Constraint names are checked because they are load-bearing. The reviewed revision
spelled them in full — `name="ck_identity_migration_runs_buckets_balance_against_source"`
— and the project's naming convention (`ck_%(table_name)s_%(constraint_name)s`)
applied its prefix on top, producing
`ck_identity_migration_runs_ck_identity_migration_runs_b_642c`: the prefix twice and
then a hash, because PostgreSQL truncates at 63 characters. The result disagreed with
`adapters/database/tables.py`'s declaration of the same table and no test could
identify a constraint by name. These cases are why that is now visible.
"""
from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text

from tests.conftest import run_alembic

pytestmark = pytest.mark.database

HEAD = "head"
REVISION = "0010"
BEFORE = "0009"

TABLES = (
    "identity_migration_runs",
    "identity_link_proposals",
    "identity_link_proposal_candidates",
)

#: Exactly the constraints `adapters/database/tables.py` declares, in the form the
#: naming convention produces. Listed rather than derived so a constraint silently
#: dropped by a later edit fails here.
EXPECTED_CHECKS = {
    "identity_migration_runs": {
        "ck_identity_migration_runs_source_label_not_blank",
        "ck_identity_migration_runs_profile_version_not_blank",
        "ck_identity_migration_runs_source_characters_non_negative",
        "ck_identity_migration_runs_source_players_non_negative",
        "ck_identity_migration_runs_buckets_non_negative",
        "ck_identity_migration_runs_buckets_balance_against_source",
        # `dry_run` is `CHECK`-ed true rather than merely defaulted: every row of
        # this table is a C-04 evidence run.
        "ck_identity_migration_runs_run_is_a_c04_evidence_run",
        # **No `apply_state`.** A confirmation is the activation (change-log
        # entry C-P3.2-A, OD-46), so there is no gap between deciding and
        # linking for a run-level apply state to describe.
    },
    "identity_link_proposals": {
        "ck_identity_link_proposals_resolution",
        "ck_identity_link_proposals_player_name_not_blank",
        "ck_identity_link_proposals_resolved_subject_matches_resolution",
        "ck_identity_link_proposals_decision_state",
        "ck_identity_link_proposals_decider",
        "ck_identity_link_proposals_decision_reason_not_blank",
        # Reason presence agrees with decision state (change-log entry
        # C-P3.2-C). The restricted runtime role holds `UPDATE` here, so
        # "R-29 and R-30 require a reason" has to be the database's rule and
        # not only the service's.
        "ck_identity_link_proposals_a_decision_states_its_reason",
        # §7.2's whole pipeline, as one constraint: a confirmation **is** a link
        # and nothing else is. It refuses a grant on a `proposed`, `ambiguous`,
        # `unresolved` or `rejected` row — so C-04 cannot authorize and a
        # rejection cannot link — and refuses a `confirmed` row that names none,
        # so "decided but not linked" is not a storable state.
        "ck_identity_link_proposals_a_confirmation_is_a_link",
    },
    "identity_link_proposal_candidates": {
        "ck_identity_link_proposal_candidates_subject_not_blank",
    },
}


def catalogue(engine, table):
    """One table's constraints and indexes, from `pg_catalog`.

    Read from the catalogue rather than from SQLAlchemy's reflection of the
    declared metadata, because the question is what the *migration* built.
    """
    with engine.begin() as connection:
        checks = set(
            connection.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE conrelid = CAST(:table AS regclass) AND contype = 'c'"
                ),
                {"table": table},
            ).scalars()
        )
        keys = set(
            connection.execute(
                text(
                    "SELECT conname || ' ' || confdeltype::text FROM pg_constraint "
                    "WHERE conrelid = CAST(:table AS regclass) AND contype = 'f'"
                ),
                {"table": table},
            ).scalars()
        )
        uniques = set(
            connection.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE conrelid = CAST(:table AS regclass) AND contype = 'u'"
                ),
                {"table": table},
            ).scalars()
        )
        indexes = set(
            connection.execute(
                text("SELECT indexname || ' ' || indexdef FROM pg_indexes "
                     "WHERE tablename = :table"),
                {"table": table},
            ).scalars()
        )
    return {"checks": checks, "keys": keys, "uniques": uniques, "indexes": indexes}


def tables_exist(engine):
    with engine.begin() as connection:
        return {
            name
            for name in connection.execute(
                text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                    "AND tablename = ANY(:names)"
                ),
                {"names": list(TABLES)},
            ).scalars()
        }


@pytest.fixture()
def at_head(database_url, migrated_database):
    """Always leaves the database at head, whatever the case does to it."""
    try:
        yield
    finally:
        run_alembic(database_url, "upgrade", HEAD)


def test_the_revision_creates_exactly_the_declared_objects(migrated_database):
    """Property 1, at head: the three tables and their full constraint inventory.

    Named constraints, so a rename is a failure rather than a silent difference from
    `tables.py`. This is the case that would have failed against the reviewed
    revision, whose names carried their prefix twice and then a hash.
    """
    assert tables_exist(migrated_database) == set(TABLES)
    for table, expected in EXPECTED_CHECKS.items():
        assert catalogue(migrated_database, table)["checks"] == expected, table

    proposals = catalogue(migrated_database, "identity_link_proposals")
    # `CASCADE` from the run and the character — a proposal is evidence about a
    # character and dies with it — and `RESTRICT` to the account and the access row,
    # because a decision names a person and a grant and neither may be removed out
    # from under the record of the decision.
    assert proposals["keys"] == {
        "fk_identity_link_proposals_run_id_identity_migration_runs c",
        "fk_identity_link_proposals_character_id_characters c",
        "fk_identity_link_proposals_decided_by_account_id_accounts r",
        "fk_identity_link_proposals_granted_access_id_character_access r",
    }
    assert proposals["uniques"] == {"uq_identity_link_proposals_run_character"}
    assert {
        name.split(" ", 1)[0] for name in proposals["indexes"]
    } >= {"ix_identity_link_proposals_run", "ix_identity_link_proposals_character"}

    candidates = catalogue(migrated_database, "identity_link_proposal_candidates")
    assert candidates["keys"] == {
        "fk_identity_link_proposal_candidates_proposal_id_proposals c"
    }
    assert candidates["uniques"] == {"uq_identity_link_proposal_candidates_subject"}


def test_the_migration_and_the_declared_metadata_name_the_same_constraints(
    migrated_database,
):
    """Migration 0010 and `adapters/database/tables.py`, compared to each other.

    The literal inventory above is a list somebody maintains; this is the pair
    that has to agree whatever anyone maintains. `tables.py` is what the
    repositories build statements against and what the application believes the
    schema is; the migration is what the database actually got. A constraint
    added to one and not the other is a rule the application thinks it has and
    does not, or one PostgreSQL enforces that no reviewer read in the
    declaration — and the C-P3.2-A remediation removed five of them across the
    two tables and replaced them with one, which is exactly when the two drift.
    """
    from adapters.database.tables import metadata

    for table in TABLES:
        # `constraint.name` is already the convention-expanded name
        # (`adapters/database/metadata.py`: `ck_%(table_name)s_%(constraint_name)s`),
        # which is the same expansion the migration relies on and the reason the
        # migration spells its constraints in the short form.
        declared = {
            constraint.name
            for constraint in metadata.tables[table].constraints
            if type(constraint).__name__ == "CheckConstraint"
        }
        assert declared == catalogue(migrated_database, table)["checks"], table
        assert declared == EXPECTED_CHECKS[table], table


def test_the_migration_and_the_declared_metadata_hold_the_same_columns(
    migrated_database,
):
    """The **columns**, on all three tables, in both declarations.

    Names and nullability, from `information_schema` against `tables.py`. A
    column present in one declaration and not the other is a repository building
    a statement against a column PostgreSQL does not have — or a column nothing
    reads. The C-P3.2-A remediation removed five columns across two tables, which
    is exactly the edit that leaves one declaration behind.
    """
    from adapters.database.tables import metadata

    for table in TABLES:
        with migrated_database.begin() as connection:
            live = {
                row[0]: row[1] == "YES"
                for row in connection.execute(
                    text(
                        "SELECT column_name, is_nullable FROM "
                        "information_schema.columns WHERE table_schema = 'public' "
                        "AND table_name = :table"
                    ),
                    {"table": table},
                ).all()
            }
        declared = {
            column.name: column.nullable for column in metadata.tables[table].columns
        }
        assert live == declared, table

    # And the withdrawn apply state is **absent** from both sides, rather than
    # merely equal on them. A nullable column no writer sets is a column a later
    # reader will interpret, so the assertion is that they are gone.
    assert not {"applied_at", "apply_correlation_id"} & set(
        metadata.tables["identity_migration_runs"].columns.keys()
    )
    assert not {"applied_at", "apply_outcome"} & set(
        metadata.tables["identity_link_proposals"].columns.keys()
    )
    # `granted_access_id` stays: it is what a confirmation records, and its
    # presence is the difference between removing an apply *state* and removing
    # the link between a decision and the row it created.
    assert "granted_access_id" in metadata.tables["identity_link_proposals"].columns


def check_constraint_sources(path, table_names):
    """`{table: {name: expression}}` for every `CheckConstraint` in one module.

    Read from the **source** rather than from a live object, because the
    question is whether two declarations agree with each other, and evaluating
    one of them through SQLAlchemy would answer a different question.
    """
    import ast

    tree = ast.parse(path.read_text())
    found: dict[str, dict[str, str]] = {name: {} for name in table_names}

    def constraints_under(node):
        pairs = {}
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            callee = child.func
            name = (
                callee.attr if isinstance(callee, ast.Attribute) else
                callee.id if isinstance(callee, ast.Name) else None
            )
            if name != "CheckConstraint":
                continue
            expression = ast.literal_eval(child.args[0])
            keyword = next(k for k in child.keywords if k.arg == "name")
            pairs[ast.literal_eval(keyword.value)] = " ".join(expression.split())
        return pairs

    for node in ast.walk(tree):
        # `identity_migration_runs = Table("identity_migration_runs", …)` in
        # `tables.py`, and `op.create_table("identity_migration_runs", …)` in the
        # revision. Both name the table in their first positional argument.
        if not isinstance(node, ast.Call) or not node.args:
            continue
        first = node.args[0]
        if not isinstance(first, ast.Constant) or first.value not in found:
            continue
        found[first.value].update(constraints_under(node))
    return found


def test_the_revision_and_the_declared_tables_spell_the_same_expressions():
    """The names above agree; this is whether the **rules** agree.

    Two constraints can share a name and say different things, and the pair that
    matters is `migrations/versions/0010_identity_link_proposals.py` against
    `adapters/database/tables.py`: the first is what the database got and the
    second is what every repository statement is built against. The F6
    remediation added the apply-state rules to both, and a test that compared
    only names would pass while one of them permitted an applied `rejected` row.

    Compared as source text with whitespace normalized, so a re-wrapped string
    is not a failure and a changed operator is.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    revision = check_constraint_sources(
        root / "migrations/versions/0010_identity_link_proposals.py", TABLES
    )
    declared = check_constraint_sources(root / "adapters/database/tables.py", TABLES)
    for table in TABLES:
        assert revision[table] == declared[table], table
        # And the short names expand to the inventory the catalogue holds.
        assert {
            f"ck_{table}_{name}" for name in revision[table]
        } == EXPECTED_CHECKS[table], table


def test_upgrade_downgrade_upgrade_leaves_an_identical_schema(
    database_url, migrated_database, at_head
):
    """Property 2. The schema is compared to itself across a full round trip.

    A downgrade that dropped one index and an upgrade that recreated it as a
    different index would pass a "does the table exist?" test and fail this one.
    """
    before = {table: catalogue(migrated_database, table) for table in TABLES}

    run_alembic(database_url, "downgrade", BEFORE)
    assert tables_exist(migrated_database) == set()

    run_alembic(database_url, "upgrade", REVISION)
    after = {table: catalogue(migrated_database, table) for table in TABLES}
    assert after == before


def test_the_downgrade_keeps_every_link_a_confirmation_created(
    database_url, migrated_database, at_head
):
    """Property 3, and the sentence the revision's docstring makes a promise of.

    A confirmed proposal and the `character_access` row it created are set up, then
    the revision is downgraded. The proposal and its candidates go — they are
    evidence and a decision — and the link does not: it keeps its grantor, its
    reason, its timestamps and its correlation id. So a downgrade loses the record of
    *which proposal* prompted a link, and never the link or its audit event.

    The `granted_access_id` foreign key is `RESTRICT`, so this also proves the
    downgrade drops the referencing table rather than being blocked by it — which is
    the difference between a reversible revision and one that needs a manual step.
    """
    with migrated_database.begin() as connection:
        character_id = uuid4()
        connection.execute(
            text("INSERT INTO characters (id, display_name) VALUES (:id, 'Round Trip')"),
            {"id": character_id},
        )
        account_id, grantor_id = uuid4(), uuid4()
        for identifier, label in ((account_id, "owner"), (grantor_id, "council")):
            connection.execute(
                text(
                    "INSERT INTO platform_accounts (id, status, display_label) "
                    "VALUES (:id, 'active', :label)"
                ),
                {"id": identifier, "label": label},
            )
        subjects = {}
        for identifier, subject in ((account_id, 700000000000009001), (grantor_id, 700000000000009002)):
            connection.execute(
                text("INSERT INTO discord_users (id, username) VALUES (:id, :name)"),
                {"id": subject, "name": f"round-trip-{subject}"},
            )
            connection.execute(
                text(
                    "INSERT INTO external_identities (id, platform_account_id, "
                    "provider_key, subject, state, audit_correlation_id) "
                    "VALUES (:id, :account, 'discord', :subject, 'active', :c)"
                ),
                {
                    "id": uuid4(),
                    "account": identifier,
                    "subject": str(subject),
                    "c": uuid4(),
                },
            )
            subjects[identifier] = subject

        access_id, correlation_id = uuid4(), uuid4()
        connection.execute(
            text(
                "INSERT INTO character_access (id, character_id, platform_account_id, "
                "access_kind, granted_by_account_id, reason, audit_correlation_id) "
                "VALUES (:id, :character, :account, 'co_owner', :grantor, "
                "'confirmed a Sheet-era proposal', :c)"
            ),
            {
                "id": access_id,
                "character": character_id,
                "account": account_id,
                "grantor": grantor_id,
                "c": correlation_id,
            },
        )

        run_id, proposal_id = uuid4(), uuid4()
        connection.execute(
            text(
                "INSERT INTO identity_migration_runs (id, source_label, "
                "profile_version, source_characters, source_players, already_linked, "
                "proposed, ambiguous, unresolved, correlation_id) "
                "VALUES (:id, 'Characters!C + Players!A/B/D', 'v', 1, 1, 0, 1, 0, 0, "
                ":c)"
            ),
            {"id": run_id, "c": uuid4()},
        )
        # A **confirmed** proposal naming its access row, because that is the
        # only shape that may carry a `granted_access_id`:
        # `ck_identity_link_proposals_a_confirmation_is_a_link` refuses one on
        # any other resolution and refuses a confirmation without one. So the
        # link this case is about is the one the confirmation created, which is
        # the whole shape of the pipeline after C-P3.2-A.
        connection.execute(
            text(
                "INSERT INTO identity_link_proposals (id, run_id, character_id, "
                "sheet_player_name, proposed_subject, resolution, decided_at, "
                "decided_by_account_id, decision_reason, granted_access_id, "
                "audit_correlation_id) VALUES (:id, :run, :character, 'Ada', "
                ":subject, 'confirmed', now(), :grantor, 'Council confirmed it', "
                ":access, :c)"
            ),
            {
                "id": proposal_id,
                "run": run_id,
                "character": character_id,
                "subject": str(subjects[account_id]),
                "grantor": grantor_id,
                "access": access_id,
                "c": uuid4(),
            },
        )
        connection.execute(
            text(
                "INSERT INTO identity_link_proposal_candidates (id, proposal_id, "
                "subject, observed_username) VALUES (:id, :proposal, :subject, 'ada.one')"
            ),
            {
                "id": uuid4(),
                "proposal": proposal_id,
                "subject": str(subjects[account_id]),
            },
        )

    run_alembic(database_url, "downgrade", BEFORE)

    with migrated_database.begin() as connection:
        row = (
            connection.execute(
                text("SELECT * FROM character_access WHERE id = :id"), {"id": access_id}
            )
            .mappings()
            .one()
        )
    assert row["reason"] == "confirmed a Sheet-era proposal"
    assert row["audit_correlation_id"] == correlation_id
    assert row["granted_by_account_id"] == grantor_id
    assert row["active"] is True
    assert tables_exist(migrated_database) == set()

    run_alembic(database_url, "upgrade", REVISION)
    # And the link is still there afterwards, with the three tables empty: the
    # re-upgrade recreates the evidence schema and does not invent evidence.
    with migrated_database.begin() as connection:
        assert (
            connection.execute(
                text("SELECT count(*) FROM character_access WHERE id = :id"),
                {"id": access_id},
            ).scalar()
            == 1
        )
        for table in TABLES:
            assert (
                connection.execute(text(f"SELECT count(*) FROM {table}")).scalar() == 0
            ), table

    with migrated_database.begin() as connection:
        connection.execute(text("DELETE FROM character_access"))
        connection.execute(text("DELETE FROM characters"))
        connection.execute(text("DELETE FROM external_identities"))
        connection.execute(text("DELETE FROM platform_accounts"))
        connection.execute(text("DELETE FROM discord_users"))


def test_the_revision_adds_no_third_jsonb_column(migrated_database):
    """TC-STRUCT-03's rule, applied to this revision's tables.

    Implementation plan §7.3.1 prohibits delimited text, JSON/JSONB collections and
    PostgreSQL arrays for multi-valued facts and prescribes typed foreign-keyed child
    rows instead. `identity_link_proposal_candidates` is that representation rather
    than a preference, and this is the assertion that keeps it one.
    """
    with migrated_database.begin() as connection:
        offending = connection.execute(
            text(
                "SELECT table_name, column_name, data_type FROM information_schema.columns "
                "WHERE table_schema = 'public' AND table_name = ANY(:names) "
                "AND (data_type IN ('json', 'jsonb') OR data_type = 'ARRAY')"
            ),
            {"names": list(TABLES)},
        ).all()
    assert offending == []
