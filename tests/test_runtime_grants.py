"""The runtime role's grants are part of the schema contract (plan §9.3).

A new table that nobody grants is a runtime failure; a new audit table that is
granted UPDATE or DELETE silently breaks the append-only rule in
`.agents/AGENTS.md`. Both are checked against the template here, and the
denials are additionally exercised **against the live restricted role** in
`test_runtime_grants_live.py` — template review alone was the weaker evidence
this milestone was previously criticised for.
"""
from __future__ import annotations

import re
from pathlib import Path

from adapters.database.metadata import metadata
from adapters.database import tables  # noqa: F401 - registers tables on metadata

TEMPLATE = Path(__file__).resolve().parents[1] / "infra" / "postgresql" / "runtime-grants.sql.tmpl"

#: Kept in step with `adapters.database.tables.APPEND_ONLY_TABLES` and the
#: triggers in migration 0002. `platform_initialization` joins them for the same
#: reason: the bootstrap disables itself by writing that row, so a role able to
#: delete it could re-enable the bootstrap.
APPEND_ONLY_TABLES = {
    "audit_events",
    "foundry_snapshots",
    "snapshot_imports",
    "platform_initialization",
}


def granted_tables(statement_pattern: str) -> set[str]:
    body = TEMPLATE.read_text()
    granted: set[str] = set()
    for match in re.finditer(statement_pattern, body, re.IGNORECASE | re.DOTALL):
        granted.update(
            name.strip()
            for name in match.group("tables").replace("\n", " ").split(",")
            if name.strip()
        )
    return granted


def test_every_table_is_granted_to_the_runtime_role():
    mutable = granted_tables(
        r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE,\s*DELETE\s+ON(?P<tables>.*?)TO\s+__APP_ROLE__"
    )
    append_only = granted_tables(r"GRANT\s+SELECT,\s*INSERT\s+ON(?P<tables>.*?)TO\s+__APP_ROLE__")

    expected = set(metadata.tables)
    assert mutable | append_only == expected, "a table is missing from the runtime grants"


def test_audit_tables_receive_no_update_or_delete_grant():
    mutable = granted_tables(
        r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE,\s*DELETE\s+ON(?P<tables>.*?)TO\s+__APP_ROLE__"
    )
    append_only = granted_tables(r"GRANT\s+SELECT,\s*INSERT\s+ON(?P<tables>.*?)TO\s+__APP_ROLE__")

    assert APPEND_ONLY_TABLES & mutable == set()
    assert APPEND_ONLY_TABLES <= append_only


def statements() -> str:
    """The template with `--` comments removed, so prose cannot mask a grant."""
    lines = (line.split("--", 1)[0] for line in TEMPLATE.read_text().splitlines())
    return "\n".join(lines).upper()


def test_the_runtime_role_is_never_granted_schema_creation():
    body = statements()

    assert "GRANT CREATE" not in body
    assert "GRANT ALL" not in body
    assert "SUPERUSER" not in body
    assert "GRANT USAGE ON SCHEMA PUBLIC TO __APP_ROLE__" in body
    for table in sorted(APPEND_ONLY_TABLES):
        assert (
            f"REVOKE UPDATE, DELETE, TRUNCATE ON {table.upper()} FROM __APP_ROLE__"
            in body
        ), table


def test_the_append_only_set_matches_the_schema_and_the_triggers():
    # Three places have to agree, and none of them can import the others by
    # name: the SQLAlchemy metadata, the migration that creates the triggers,
    # and this grants template.
    from adapters.database.tables import APPEND_ONLY_TABLES as SCHEMA_TABLES

    migration = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "0002_foundry_snapshot_and_identity.py"
    ).read_text()

    assert set(SCHEMA_TABLES) <= APPEND_ONLY_TABLES
    for table in SCHEMA_TABLES:
        assert f'"{table}"' in migration, f"{table} has no append-only trigger"
        assert f"CREATE TRIGGER {{table}}_append_only" in migration


def test_no_credential_is_embedded_in_the_template():
    body = TEMPLATE.read_text()

    assert "PASSWORD" not in body.upper()
    assert "__APP_ROLE__" in body, "the role must stay a deployment-time placeholder"
