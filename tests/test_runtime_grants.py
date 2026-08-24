"""The runtime role's grants are part of the schema contract (plan §9.3).

A new table that nobody grants is a runtime failure; a new audit table that is
granted UPDATE or DELETE silently breaks the append-only rule in
`.agents/AGENTS.md`. Both are checked against the template here.

**What this file does and does not prove.** It reads the template as text. That
is enough to catch a table nobody listed and a grant nobody intended, and it is
the only way to check a statement that has not been run. It proves nothing about
what PostgreSQL concludes: privileges are cumulative, arrive through role
membership and through PUBLIC, and can be granted by anything else that touches
the cluster. Finding O-1 was precisely a case where the text said one thing and
the effective privileges were another. The decisive evidence is
`test_runtime_grants_live.py`, which seeds hostile PUBLIC grants, applies this
template and then asks the server.
"""
from __future__ import annotations

import re
from pathlib import Path

from adapters.database.metadata import metadata
from adapters.database import tables  # noqa: F401 - registers tables on metadata

TEMPLATE = Path(__file__).resolve().parents[1] / "infra" / "postgresql" / "runtime-grants.sql.tmpl"

#: Kept in step with `adapters.database.tables.APPEND_ONLY_TABLES` and the
#: triggers in migrations 0002 and 0006. `platform_initialization` joins them for
#: the same reason: the bootstrap disables itself by writing that row, so a role
#: able to delete it could re-enable the bootstrap.
APPEND_ONLY_TABLES = {
    "audit_events",
    "foundry_snapshots",
    "snapshot_imports",
    "platform_initialization",
    "role_capability_mapping_events",
}

#: The migrations that install `<table>_append_only` triggers. 0002 introduced
#: the pattern and the shared `reject_history_mutation()` function; 0006 reuses
#: both for the role-capability mapping event log.
TRIGGER_MIGRATIONS = (
    "0002_foundry_snapshot_and_identity.py",
    "0006_platform_identity_stage_a.py",
)

#: Tables the runtime role may read, insert and update, but never delete
#: (schema §11.2). An account is closed and an identity retired rather than
#: removed, because audit attribution resolves through them after a provider is
#: retired; a session, mapping or credential is revoked or disabled in place so
#: the history of who could do what stays readable.
NO_DELETE_TABLES = {
    "platform_accounts",
    "external_identities",
    "sessions",
    "oauth_transactions",
    "webauthn_credentials",
    "recovery_grants",
    "role_capability_mappings",
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


#: Tables the runtime role may read and may not write at all. One entry: the
#: admission fence (migration 0005). A role able to insert one could admit
#: itself, and a role able to update one could reopen a generation settlement had
#: closed — either of which would make the fence advisory rather than enforced.
READ_ONLY_TABLES = {"submission_admissions"}

#: Alembic's own bookkeeping table. It is not an application table and is not in
#: the ORM metadata, so it is excluded from the metadata equalities below and
#: given its own test. The portal cannot start without reading it (S-14).
SCHEMA_VERSION_TABLE = "alembic_version"


def mutable_tables() -> set[str]:
    return granted_tables(
        r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE,\s*DELETE\s+ON(?P<tables>.*?)TO\s+__APP_ROLE__"
    )


def no_delete_granted() -> set[str]:
    return granted_tables(
        r"GRANT\s+SELECT,\s*INSERT,\s*UPDATE\s+ON(?P<tables>.*?)TO\s+__APP_ROLE__"
    )


def append_only_granted() -> set[str]:
    return granted_tables(
        r"GRANT\s+SELECT,\s*INSERT\s+ON(?P<tables>.*?)TO\s+__APP_ROLE__"
    )


def read_only_granted() -> set[str]:
    return granted_tables(r"GRANT\s+SELECT\s+ON(?P<tables>.*?)TO\s+__APP_ROLE__")


def test_every_table_is_granted_to_the_runtime_role():
    granted = (
        mutable_tables()
        | no_delete_granted()
        | append_only_granted()
        | read_only_granted()
    )

    expected = set(metadata.tables)
    # `alembic_version` is granted deliberately and is not an application table;
    # it has its own test rather than being smuggled into this equality.
    assert granted - {SCHEMA_VERSION_TABLE} == expected, (
        "a table is missing from the runtime grants"
    )


def test_audit_tables_receive_no_update_or_delete_grant():
    assert APPEND_ONLY_TABLES & mutable_tables() == set()
    assert APPEND_ONLY_TABLES & no_delete_granted() == set()
    assert APPEND_ONLY_TABLES <= append_only_granted()


def test_identity_tables_are_never_granted_delete():
    """Schema §11.2's middle band, and the reason it is a band rather than a list.

    Deleting an account or an identity would break historical audit attribution,
    which resolves through `external_identities` after a provider is retired
    (ADR 0010 D4). Deleting a session, mapping or credential row would erase the
    record of an authority that existed. Each is revoked, retired, closed or
    disabled in place instead, so the grant is the control rather than the
    convention.
    """
    assert NO_DELETE_TABLES <= no_delete_granted()
    assert NO_DELETE_TABLES & mutable_tables() == set()

    body = statements()
    for table in sorted(NO_DELETE_TABLES):
        assert f"REVOKE DELETE, TRUNCATE ON" in body
        assert table.upper() in body, table


def test_the_admission_fence_is_readable_and_not_writable():
    """C-24. The fence is only a fence if the fenced party cannot move it."""
    assert READ_ONLY_TABLES <= read_only_granted()
    assert READ_ONLY_TABLES & mutable_tables() == set()
    assert READ_ONLY_TABLES & append_only_granted() == set()

    body = statements()
    for table in sorted(READ_ONLY_TABLES):
        assert (
            f"REVOKE INSERT, UPDATE, DELETE, TRUNCATE ON {table.upper()} "
            f"FROM __APP_ROLE__" in body
        ), table


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

    versions = Path(__file__).resolve().parents[1] / "migrations" / "versions"
    migrations = {
        name: (versions / name).read_text() for name in TRIGGER_MIGRATIONS
    }

    assert set(SCHEMA_TABLES) <= APPEND_ONLY_TABLES
    for table in SCHEMA_TABLES:
        installing = [
            body
            for body in migrations.values()
            if f'"{table}"' in body and "CREATE TRIGGER {table}_append_only" in body
        ]
        assert installing, f"{table} has no append-only trigger in any migration"


def test_every_retained_table_has_its_public_privileges_revoked():
    """O-1: PUBLIC is normalised explicitly, for every table.

    Revoking from the runtime role cannot take away a privilege the role holds
    *through* PUBLIC, so before this the template's claim to have "handled
    rights held by PUBLIC" was false. Text-level check only; the effective
    privileges are proven in `test_runtime_grants_live.py`.
    """
    revoked = granted_tables(
        r"REVOKE\s+ALL\s+PRIVILEGES\s+ON(?P<tables>.*?)FROM\s+PUBLIC"
    )

    assert revoked - {SCHEMA_VERSION_TABLE} == set(metadata.tables), (
        "a retained table's PUBLIC privileges are never revoked: "
        f"{set(metadata.tables) - revoked}"
    )


def test_public_is_not_left_able_to_create_in_the_schema():
    assert "REVOKE CREATE ON SCHEMA PUBLIC FROM PUBLIC" in statements()


def test_the_template_makes_no_grant_to_public():
    """The runtime role is the only grantee; PUBLIC is only ever revoked from."""
    body = statements()

    for line in body.splitlines():
        if line.strip().startswith("GRANT"):
            assert "TO PUBLIC" not in line, line


def test_no_credential_is_embedded_in_the_template():
    body = TEMPLATE.read_text()

    assert "PASSWORD" not in body.upper()
    assert "__APP_ROLE__" in body, "the role must stay a deployment-time placeholder"


def test_the_runtime_role_can_read_the_schema_version_and_cannot_write_it():
    """S-14 regression, 2026-08-23.

    The portal refuses to start unless it can read `alembic_version` over its
    *runtime* connection. The template granted every application table and not
    this one, so the restricted role could never start the portal — a defect no
    test could catch while no deployed configuration had ever been started
    (I-06, TC-OPS-04). It is caught here now, at the text level, and by the
    effective-privilege suite in `test_runtime_grants_live.py`.

    SELECT only: migrations run as the schema owner, and a runtime role able to
    write this table could tell the next startup it was serving a schema it was
    not.
    """
    assert SCHEMA_VERSION_TABLE in read_only_granted(), (
        "the runtime role cannot read alembic_version, so S-14 refuses every "
        "startup and the portal can never run under the restricted role"
    )
    for granted in (mutable_tables(), no_delete_granted(), append_only_granted()):
        assert SCHEMA_VERSION_TABLE not in granted, (
            "alembic_version must be readable and not writable by the runtime role"
        )
