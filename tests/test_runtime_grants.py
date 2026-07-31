"""The runtime role's grants are part of the schema contract (plan §9.3).

A new table that nobody grants is a runtime failure; a new audit table that is
granted UPDATE or DELETE silently breaks the append-only rule in
`.agents/AGENTS.md`. Both are checked here rather than at deployment time,
because this host has no privilege to create a role and rehearse the grants.
"""
from __future__ import annotations

import re
from pathlib import Path

from adapters.database.metadata import metadata
from adapters.database import tables  # noqa: F401 - registers tables on metadata

TEMPLATE = Path(__file__).resolve().parents[1] / "infra" / "postgresql" / "runtime-grants.sql.tmpl"

APPEND_ONLY_TABLES = {"audit_events"}


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
    assert "REVOKE UPDATE, DELETE, TRUNCATE ON AUDIT_EVENTS FROM __APP_ROLE__" in body


def test_no_credential_is_embedded_in_the_template():
    body = TEMPLATE.read_text()

    assert "PASSWORD" not in body.upper()
    assert "__APP_ROLE__" in body, "the role must stay a deployment-time placeholder"
