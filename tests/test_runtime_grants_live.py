"""Restricted-role denial, exercised against a real role rather than reviewed.

The previous milestone could only offer *template review* for this: the host's
PostgreSQL login could not create a role, so the grants were read rather than
run. That was recorded as an unmet criterion, and it is what this file closes.

The role already exists (`freedom_runtime_test`, created by the maintainer). It
is `NOLOGIN`, non-superuser, cannot create roles or databases, cannot replicate
and cannot bypass RLS, and the owner/test login `foundry` is a member — so the
evidence method is `SET ROLE`, which exercises the *privileges* without needing
a second connection identity.

What is proven here, per plan §12 Phase 2 and threshold T-8:

- every allowed operation succeeds under the restricted role; and
- `UPDATE`, `DELETE` and `TRUNCATE` are each denied on every append-only table,
  with the SQLSTATE recorded.

`SET ROLE` is reset in a fixture teardown rather than trusted to the test body,
because a leaked role would silently weaken every later test in the session.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

pytestmark = pytest.mark.database

RUNTIME_ROLE = "freedom_runtime_test"

#: Append-only in the database as well as the application. `platform_initialization`
#: joins the three trigger-protected tables for a different reason: the
#: supervised bootstrap disables itself by writing that row, so a role able to
#: delete it could re-open the bootstrap.
APPEND_ONLY_TABLES = (
    "audit_events",
    "foundry_snapshots",
    "snapshot_imports",
    "platform_initialization",
)

#: PostgreSQL's insufficient-privilege class. A denial must be a *privilege*
#: denial: a syntax error or a missing table would also raise, and would prove
#: nothing about the grants.
INSUFFICIENT_PRIVILEGE = "42501"


TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "infra"
    / "postgresql"
    / "runtime-grants.sql.tmpl"
)


def grant_statements() -> list[str]:
    """The template rendered for the test role, one statement per entry.

    Comments are stripped first so a `--` line cannot be mistaken for SQL.
    """
    body = TEMPLATE.read_text(encoding="utf-8").replace("__APP_ROLE__", RUNTIME_ROLE)
    without_comments = "\n".join(
        line.split("--", 1)[0] for line in body.splitlines()
    )
    return [
        statement.strip()
        for statement in without_comments.split(";")
        if statement.strip()
    ]


#: Every retained table, for the PUBLIC-drift evidence. Kept as a literal rather
#: than read from the metadata so that a table quietly dropped from the ORM does
#: not quietly drop out of the hostile-grant seeding too.
RETAINED_TABLES = (
    "discord_users",
    "discord_guild_memberships",
    "discord_membership_roles",
    "characters",
    "character_access",
    "external_actor_mappings",
    "sheet_row_mappings",
    "idempotency_keys",
    "audit_events",
    "foundry_snapshots",
    "snapshot_imports",
    "platform_initialization",
)

#: What the runtime role must not end up holding on append-only history,
#: however it might have come by it.
PROHIBITED_PRIVILEGES = ("UPDATE", "DELETE", "TRUNCATE")


def apply_template(connection) -> None:
    for statement in grant_statements():
        connection.execute(text(statement))


def seed_hostile_public_grants(connection) -> None:
    """The drift the template must be able to undo.

    `GRANT ALL ... TO PUBLIC` is not a hypothetical: PUBLIC includes every role
    in the cluster, so one such statement — from a migration, a restore, a
    recovery session — hands the runtime role UPDATE, DELETE and TRUNCATE on
    append-only history without naming it.
    """
    for table in RETAINED_TABLES:
        connection.execute(text(f"GRANT ALL PRIVILEGES ON {table} TO PUBLIC"))


@pytest.fixture()
def restricted(migrated_database):
    """A connection with the restricted role assumed, reset afterwards.

    The fixture **applies the grants template itself**, for two reasons. The
    schema fixture migrates from empty on every run, which drops each table and
    its ACL with it — so grants applied by hand beforehand would not survive to
    be tested. And applying the real template makes this evidence about the
    deployed artifact rather than about whatever a human once typed.

    Teardown rolls back before resetting the role: a denied statement aborts its
    transaction, and `RESET ROLE` would fail inside an aborted one, leaving the
    role assumed for whatever ran next.
    """
    engine = migrated_database

    with engine.begin() as owner:
        role_exists = owner.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
            {"role": RUNTIME_ROLE},
        ).scalar()
        if not role_exists:
            pytest.skip(
                f"{RUNTIME_ROLE} does not exist; create it to exercise "
                "restricted-role denial"
            )
        for statement in grant_statements():
            owner.execute(text(statement))

    connection = engine.connect()
    connection.execute(text(f"SET ROLE {RUNTIME_ROLE}"))
    try:
        yield connection
    finally:
        connection.rollback()
        connection.execute(text("RESET ROLE"))
        connection.close()


def sqlstate(error: Exception) -> str | None:
    return getattr(getattr(error, "orig", None), "sqlstate", None)


def test_the_restricted_role_is_not_privileged(db_connection):
    """The role itself must be as narrow as the evidence assumes."""
    row = db_connection.execute(
        text(
            "SELECT rolsuper, rolcreaterole, rolcreatedb, rolreplication, "
            "rolbypassrls, rolcanlogin FROM pg_roles WHERE rolname = :role"
        ),
        {"role": RUNTIME_ROLE},
    ).first()

    if row is None:
        pytest.skip(f"{RUNTIME_ROLE} does not exist")
    assert not any(row), f"{RUNTIME_ROLE} holds a privilege it must not have"


def test_set_role_permits_the_allowed_operations(restricted):
    """Denial evidence is only meaningful if the role can do its job."""
    assert restricted.execute(text("SELECT count(*) FROM characters")).scalar() >= 0
    assert restricted.execute(text("SELECT count(*) FROM audit_events")).scalar() >= 0

    # INSERT on an append-only table is permitted; that is the whole point of
    # append-only rather than read-only.
    restricted.execute(
        text(
            "INSERT INTO audit_events (id, actor_capability, action, entity_type, "
            "entity_id, source, correlation_id, payload) VALUES "
            "(gen_random_uuid(), 'system', 'runtime_role_probe', 'character', "
            "'probe', 'import', gen_random_uuid(), '{}'::jsonb)"
        )
    )


@pytest.mark.parametrize("table", APPEND_ONLY_TABLES)
def test_set_role_denies_update_on_every_append_only_table(restricted, table):
    with pytest.raises(ProgrammingError) as denial:
        restricted.execute(text(f"UPDATE {table} SET correlation_id = correlation_id"))

    assert sqlstate(denial.value) == INSUFFICIENT_PRIVILEGE, (
        f"UPDATE on {table} failed for a reason other than privilege"
    )


@pytest.mark.parametrize("table", APPEND_ONLY_TABLES)
def test_set_role_denies_delete_on_every_append_only_table(restricted, table):
    with pytest.raises(ProgrammingError) as denial:
        restricted.execute(text(f"DELETE FROM {table}"))

    assert sqlstate(denial.value) == INSUFFICIENT_PRIVILEGE


@pytest.mark.parametrize("table", APPEND_ONLY_TABLES)
def test_set_role_denies_truncate_on_every_append_only_table(restricted, table):
    with pytest.raises(ProgrammingError) as denial:
        restricted.execute(text(f"TRUNCATE {table}"))

    assert sqlstate(denial.value) == INSUFFICIENT_PRIVILEGE


def test_the_restricted_role_cannot_create_a_table(restricted):
    """No CREATE, so the role cannot escape the schema it was granted."""
    with pytest.raises(ProgrammingError) as denial:
        restricted.execute(text("CREATE TABLE runtime_role_probe (id int)"))

    assert sqlstate(denial.value) == INSUFFICIENT_PRIVILEGE


# --- O-1: PUBLIC ACL drift cannot widen the runtime role ----------------------
#
# These are the decisive evidence for finding O-1. They do not parse SQL: they
# put the cluster into the state the template claims to handle, apply the
# template, and then ask PostgreSQL what the runtime role can actually do.
# `has_table_privilege` answers with the role's *effective* privilege, which is
# the union of what it was granted directly, what it inherits through role
# membership, and what it holds through PUBLIC — so it is the only question
# whose answer means anything here.


def effective(connection, table: str, privilege: str) -> bool:
    return connection.execute(
        text("SELECT has_table_privilege(:role, :table, :privilege)"),
        {"role": RUNTIME_ROLE, "table": table, "privilege": privilege},
    ).scalar_one()


def public_holds(connection, table: str, privilege: str) -> bool:
    """Whether PUBLIC itself still holds `privilege`, per the table's ACL."""
    return connection.execute(
        text(
            "SELECT EXISTS (SELECT 1 FROM aclexplode("
            "  COALESCE((SELECT relacl FROM pg_class c "
            "            JOIN pg_namespace n ON n.oid = c.relnamespace "
            "            WHERE c.relname = :table AND n.nspname = 'public'), "
            "           '{}'::aclitem[])"
            ") a WHERE a.grantee = 0 AND a.privilege_type = :privilege)"
        ),
        {"table": table, "privilege": privilege},
    ).scalar_one()


@pytest.fixture()
def role_required(migrated_database):
    engine = migrated_database
    with engine.begin() as owner:
        exists = owner.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
            {"role": RUNTIME_ROLE},
        ).scalar()
    if not exists:
        pytest.skip(f"{RUNTIME_ROLE} does not exist")
    return engine


def test_hostile_public_grants_would_widen_the_role_if_nothing_revoked_them(
    role_required,
):
    """The premise, proven rather than assumed.

    If this failed, the rest of the O-1 evidence would be vacuous — it would be
    proving that a revoke removed something that was never there.
    """
    with role_required.begin() as owner:
        seed_hostile_public_grants(owner)
        for privilege in PROHIBITED_PRIVILEGES:
            assert effective(owner, "audit_events", privilege), (
                f"a PUBLIC grant did not confer {privilege}; the premise of the "
                "O-1 evidence does not hold on this server"
            )


@pytest.mark.parametrize("table", APPEND_ONLY_TABLES)
@pytest.mark.parametrize("privilege", PROHIBITED_PRIVILEGES)
def test_the_template_removes_public_drift_from_append_only_tables(
    role_required, table, privilege
):
    """Seed the drift, apply the template, ask the server."""
    with role_required.begin() as owner:
        seed_hostile_public_grants(owner)
        apply_template(owner)

        assert not effective(owner, table, privilege), (
            f"{RUNTIME_ROLE} can still {privilege} {table} after the template "
            "was applied over hostile PUBLIC grants"
        )
        assert not public_holds(owner, table, privilege), (
            f"PUBLIC still holds {privilege} on {table}"
        )


@pytest.mark.parametrize("table", RETAINED_TABLES)
def test_the_template_leaves_public_holding_nothing_on_any_retained_table(
    role_required, table
):
    with role_required.begin() as owner:
        seed_hostile_public_grants(owner)
        apply_template(owner)

        for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE"):
            assert not public_holds(owner, table, privilege), (
                f"PUBLIC still holds {privilege} on {table}"
            )


def test_the_template_preserves_the_runtime_roles_intended_operations(
    role_required,
):
    """Normalising PUBLIC must not take away what the role is meant to have."""
    with role_required.begin() as owner:
        seed_hostile_public_grants(owner)
        apply_template(owner)

        for table in (
            "characters",
            "external_actor_mappings",
            "discord_users",
            "idempotency_keys",
        ):
            for privilege in ("SELECT", "INSERT", "UPDATE", "DELETE"):
                assert effective(owner, table, privilege), (
                    f"{RUNTIME_ROLE} lost {privilege} on {table}"
                )
        for table in APPEND_ONLY_TABLES:
            assert effective(owner, table, "SELECT")
            assert effective(owner, table, "INSERT")


def test_the_template_is_idempotent_over_repeated_application(role_required):
    """It is applied after every migration, so applying it twice must be safe."""
    with role_required.begin() as owner:
        seed_hostile_public_grants(owner)
        apply_template(owner)
        apply_template(owner)

        assert effective(owner, "characters", "UPDATE")
        for privilege in PROHIBITED_PRIVILEGES:
            assert not effective(owner, "audit_events", privilege)


def test_public_drift_cannot_let_the_runtime_role_delete_the_initialization_row(
    role_required,
):
    """The specific escalation O-1 names: re-opening the supervised bootstrap.

    `platform_initialization` holds one row whose existence is what disables the
    one-time bootstrap. A role able to delete it could run the bootstrap again,
    which is why the table is in the append-only set despite having no trigger.
    """
    with role_required.begin() as owner:
        seed_hostile_public_grants(owner)
        apply_template(owner)

        assert not effective(owner, "platform_initialization", "DELETE")
        assert not effective(owner, "platform_initialization", "TRUNCATE")
        assert not effective(owner, "platform_initialization", "UPDATE")
        assert effective(owner, "platform_initialization", "INSERT")


def test_the_denials_still_hold_as_the_role_after_public_drift(migrated_database):
    """Effective-privilege answers and actual statements must agree.

    `has_table_privilege` is a catalogue query; this executes the statement as
    the role, over a cluster that had hostile PUBLIC grants applied to it, so
    the two independent methods have to reach the same conclusion.
    """
    engine = migrated_database
    with engine.begin() as owner:
        exists = owner.execute(
            text("SELECT 1 FROM pg_roles WHERE rolname = :role"),
            {"role": RUNTIME_ROLE},
        ).scalar()
        if not exists:
            pytest.skip(f"{RUNTIME_ROLE} does not exist")
        seed_hostile_public_grants(owner)
        apply_template(owner)

    connection = engine.connect()
    try:
        for table in APPEND_ONLY_TABLES:
            for statement in (
                f"UPDATE {table} SET correlation_id = correlation_id",
                f"DELETE FROM {table}",
                f"TRUNCATE {table}",
            ):
                # Re-assumed for every statement, and not once at the top:
                # `SET ROLE` is transactional, so the rollback each denial
                # requires would silently hand the rest of the loop back to the
                # owner — which can delete from an empty table quite happily,
                # and the test would pass while proving nothing.
                connection.execute(text(f"SET ROLE {RUNTIME_ROLE}"))
                assert (
                    connection.execute(text("SELECT current_role")).scalar()
                    == RUNTIME_ROLE
                )
                with pytest.raises(ProgrammingError) as denial:
                    connection.execute(text(statement))
                assert sqlstate(denial.value) == INSUFFICIENT_PRIVILEGE, statement
                connection.rollback()
    finally:
        connection.rollback()
        connection.execute(text("RESET ROLE"))
        connection.close()
