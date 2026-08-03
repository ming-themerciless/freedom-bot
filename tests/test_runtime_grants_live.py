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
