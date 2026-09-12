"""Plan §14.3: prove the restore, not merely that a backup command succeeded."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url

pytestmark = pytest.mark.database

ROOT = Path(__file__).resolve().parents[1]
DRILL = ROOT / "infra" / "postgresql" / "backup-restore-drill.sh"

#: Exit code the drill uses when it could not prove the connection safe.
REFUSED_CONNECTION = 3

#: Every libpq variable that can redirect a database *name* to another server.
LIBPQ_VARIABLES = (
    "PGSERVICE",
    "PGSERVICEFILE",
    "PGOPTIONS",
    "PGDATABASE",
    "PGHOST",
    "PGHOSTADDR",
    "PGPORT",
)


#: Where libpq's Unix-domain socket usually lives on a Debian/Ubuntu host. The
#: drill accepts an absolute socket directory as well as no PGHOST at all.
SOCKET_DIRECTORY_CANDIDATES = ("/var/run/postgresql", "/run/postgresql", "/tmp")


def require_postgresql_tools() -> None:
    for tool in ("pg_dump", "pg_restore", "psql"):
        if shutil.which(tool) is None:
            pytest.skip(f"{tool} is not installed on this host.")


def socket_directory() -> str:
    """The directory holding this host's PostgreSQL socket, or skip."""
    for candidate in SOCKET_DIRECTORY_CANDIDATES:
        directory = Path(candidate)
        if directory.is_dir() and any(directory.glob(".s.PGSQL.*")):
            return candidate
    pytest.skip("No PostgreSQL Unix-domain socket directory was found on this host.")


def run_drill(
    database: str,
    work_directory: Path,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run the drill with a clean libpq environment plus `environment`.

    Clearing the inherited variables first means each test asserts on the value
    it set, not on whatever the developer happened to export before running
    pytest.
    """
    child = {
        key: value
        for key, value in os.environ.items()
        if key not in LIBPQ_VARIABLES
    }
    child.update(environment or {})
    return subprocess.run(
        [str(DRILL), database, str(work_directory)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=child,
    )


# --------------------------------------------------------------------------
# The staging target, added 2026-08-26 under decision D-q (change-log C-P3.5-V)
# as route A of the C-8 proposal. SP-10 -- TC-OPS-02's staging half -- needs this
# instrument, and the script refused staging by design.
#
# The weakening is real, so these three tests exist to bound it: staging must
# need BOTH signals, production must have NO override at all, and the staging
# path must be reachable -- proved without ever drilling staging.
# --------------------------------------------------------------------------


def test_staging_is_refused_without_both_signals(tmp_path):
    require_postgresql_tools()

    for environment in (
        {},
        {"FREEDOM_DRILL_ALLOW_STAGING": "1"},
        {"FREEDOM_DRILL_STAGING_CONFIRM": "freedom_staging"},
        {
            "FREEDOM_DRILL_ALLOW_STAGING": "1",
            "FREEDOM_DRILL_STAGING_CONFIRM": "freedom_dev",
        },
    ):
        completed = run_drill("freedom_staging", tmp_path, environment)

        assert completed.returncode == 2, environment
        assert "needs both" in completed.stderr, environment
        assert not list(tmp_path.iterdir()), "nothing may be written by a refusal"


def test_production_has_no_override_at_all(tmp_path):
    """The signals open staging and nothing else.

    A guard that could be talked into production by the same two variables would
    be a worse guard than the one it replaced.
    """
    require_postgresql_tools()

    completed = run_drill(
        "freedom_production",
        tmp_path,
        {
            "FREEDOM_DRILL_ALLOW_STAGING": "1",
            "FREEDOM_DRILL_STAGING_CONFIRM": "freedom_production",
        },
    )

    assert completed.returncode == 2
    assert not list(tmp_path.iterdir())


def test_both_signals_open_the_name_gate_and_the_connection_gate_still_refuses(
    tmp_path,
):
    """The gate opens -- proved without ever drilling staging.

    Exit 2 is "the name was refused"; exit 3 is "the name was accepted and the
    connection could not be proven safe, so nothing was touched". Asserting 3 is
    what shows the staging path is reachable, while the hostile PGHOSTADDR
    guarantees the drill itself never begins.
    """
    require_postgresql_tools()

    completed = run_drill(
        "freedom_staging",
        tmp_path,
        {
            "FREEDOM_DRILL_ALLOW_STAGING": "1",
            "FREEDOM_DRILL_STAGING_CONFIRM": "freedom_staging",
            "PGHOSTADDR": "203.0.113.5",
        },
    )

    assert completed.returncode == 3
    assert "Nothing was dumped, dropped or restored." in completed.stderr
    assert not list(tmp_path.iterdir())


def test_the_drill_refuses_non_disposable_databases(tmp_path):
    require_postgresql_tools()

    completed = run_drill("freedom_production", tmp_path)

    assert completed.returncode == 2
    assert "Refusing to drill" in completed.stderr


# --------------------------------------------------------------------------
# Codex Phase 1 finding 2: a disposable *name* is not a disposable *target*.
#
# Each of these names freedom_test, which passes the name check, and then
# redirects it elsewhere through libpq. The drill must refuse before it dumps
# anything — so an empty work directory is part of the assertion.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "environment",
    [
        pytest.param({"PGHOST": "db.example.org"}, id="hostile-pghost"),
        pytest.param({"PGHOSTADDR": "203.0.113.5"}, id="hostile-pghostaddr"),
        pytest.param({"PGPORT": "not-a-port"}, id="malformed-pgport"),
    ],
)
def test_the_drill_refuses_a_connection_it_cannot_prove_local(environment, tmp_path):
    completed = run_drill("freedom_test", tmp_path, environment)

    assert completed.returncode == REFUSED_CONNECTION
    assert "Nothing was dumped, dropped or restored." in completed.stderr
    assert list(tmp_path.iterdir()) == []


# --------------------------------------------------------------------------
# Codex Phase 1 second re-review finding: loopback is not proof of a local
# server.
#
# `ssh -L 5432:localhost:5432 elsewhere` makes PGHOST=127.0.0.1 a remote
# PostgreSQL server, and that server reports loopback addresses of its own — so
# neither the variable nor the live address query can tell the difference. Step
# 4 of this drill drops a schema, so a TCP target is refused outright and the
# Unix-domain socket is required.
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "environment",
    [
        pytest.param({"PGHOST": "127.0.0.1"}, id="pghost-ipv4-loopback"),
        pytest.param({"PGHOST": "localhost"}, id="pghost-localhost"),
        pytest.param({"PGHOST": "::1"}, id="pghost-ipv6-loopback"),
        pytest.param({"PGHOSTADDR": "127.0.0.1"}, id="pghostaddr-ipv4-loopback"),
        pytest.param({"PGHOSTADDR": "::1"}, id="pghostaddr-ipv6-loopback"),
    ],
)
def test_the_drill_refuses_a_loopback_tcp_target(environment, tmp_path):
    completed = run_drill("freedom_test", tmp_path, environment)

    assert completed.returncode == REFUSED_CONNECTION
    assert "Unix-domain socket" in completed.stderr or "TCP" in completed.stderr
    assert "Nothing was dumped, dropped or restored." in completed.stderr
    assert list(tmp_path.iterdir()) == [], "nothing may be written before the refusal"


# --------------------------------------------------------------------------
# Codex Phase 1 third re-review finding: `hostaddr` outranks `host`.
#
# The finding's shape — a socket target plus an inherited PGHOSTADDR — reaches
# this drill as `PGHOST=/var/run/postgresql` (or no PGHOST at all) beside
# `PGHOSTADDR=<address>`. Gate 0c refuses PGHOSTADDR outright and does so
# *before* it looks at PGHOST, so the socket spelling cannot rescue an address.
# That was previously asserted by reading the gate; it is asserted by running it
# here.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("address", ["127.0.0.1", "::1", "203.0.113.9", "10.0.0.5"])
@pytest.mark.parametrize(
    "host", [None, "/var/run/postgresql", "/run/postgresql"], ids=["no-pghost", "var-run", "run"]
)
def test_the_drill_refuses_a_host_address_beside_a_socket_directory(
    address, host, tmp_path
):
    environment = {"PGHOSTADDR": address}
    if host is not None:
        environment["PGHOST"] = host

    completed = run_drill("freedom_test", tmp_path, environment)

    assert completed.returncode == REFUSED_CONNECTION
    assert "PGHOSTADDR" in completed.stderr, "the refusal names the variable"
    assert "Nothing was dumped, dropped or restored." in completed.stderr
    assert list(tmp_path.iterdir()) == [], "nothing may be written before the refusal"


@pytest.mark.parametrize(
    "variable", ["PGSERVICE", "PGSERVICEFILE", "PGOPTIONS", "PGDATABASE"]
)
def test_the_drill_refuses_libpq_configuration_it_cannot_verify(variable, tmp_path):
    completed = run_drill("freedom_test", tmp_path, {variable: "defined-elsewhere"})

    assert completed.returncode == REFUSED_CONNECTION
    assert variable in completed.stderr
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "environment",
    [
        pytest.param({"PGHOST": "db.example.org"}, id="remote"),
        pytest.param({"PGHOST": "127.0.0.1"}, id="loopback"),
        pytest.param({"PGHOSTADDR": "127.0.0.1"}, id="loopback-address"),
    ],
)
def test_a_refusal_does_not_echo_the_password(environment, tmp_path):
    password = "correct-horse-battery-staple"

    completed = run_drill(
        "freedom_test", tmp_path, {**environment, "PGPASSWORD": password}
    )

    assert completed.returncode == REFUSED_CONNECTION
    assert password not in completed.stdout
    assert password not in completed.stderr


def test_the_drill_accepts_an_explicit_unix_socket_directory(
    committed_database, database_url, tmp_path
):
    """The other documented spelling: PGHOST naming the socket directory itself.

    The round-trip test below covers the hostless default. This one proves the
    socket requirement is a requirement and not an accident of leaving PGHOST
    unset, and that the live gate reports the connection as a socket.
    """
    require_postgresql_tools()
    database = make_url(database_url).database
    committed_database.dispose()

    completed = run_drill(database, tmp_path, {"PGHOST": socket_directory()})

    assert completed.returncode == 0, completed.stderr
    assert "Unix-domain socket" in completed.stdout, "gate 0 names what it verified"
    assert "Restore verified" in completed.stdout


def test_backup_and_restore_round_trip_preserves_data(
    committed_database, database_url, tmp_path
):
    require_postgresql_tools()
    database = make_url(database_url).database
    character_id = uuid4()
    with committed_database.begin() as connection:
        connection.execute(
            text("INSERT INTO characters (id, display_name) VALUES (:id, :name)"),
            {"id": character_id, "name": "Restore Drill Synthetic"},
        )
    # Release pooled connections so DROP SCHEMA cannot block on an idle session.
    committed_database.dispose()

    # Peer/trust authentication over the local socket ignores this, so it is a
    # sentinel for "did any credential reach the output or the artefacts?".
    password = "correct-horse-battery-staple"

    completed = run_drill(database, tmp_path, {"PGPASSWORD": password})

    assert completed.returncode == 0, completed.stderr
    assert "Restore verified" in completed.stdout
    assert (tmp_path / f"{database}.dump.sha256").exists()
    assert password not in completed.stdout
    assert password not in completed.stderr
    for artefact in tmp_path.iterdir():
        if artefact.suffix != ".dump":
            assert password not in artefact.read_text()
    with committed_database.connect() as connection:
        restored = connection.execute(
            text("SELECT display_name FROM characters WHERE id = :id"),
            {"id": character_id},
        ).scalar_one()
    assert restored == "Restore Drill Synthetic"

# --------------------------------------------------------------------------
# N-20 (2026-08-26): the restore returned every row and every trigger, reported
# success, and left the portal and worker crash-looping because the runtime role
# held no privileges. `pg_restore --no-privileges` discards every GRANT in the
# archive, and a row-count comparison cannot see that.
#
# The drill now re-applies the runtime grants (step 5b) and compares the
# privilege state (step 6b). Both halves are tested: that it restores them, and
# that the comparison actually fails when they are missing.
# --------------------------------------------------------------------------

RUNTIME_GRANTS_TEMPLATE = ROOT / "infra" / "postgresql" / "runtime-grants.sql.tmpl"


def runtime_grantees(engine) -> set[str]:
    with engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT DISTINCT grantee FROM information_schema.table_privileges "
                "WHERE table_schema = 'public' AND grantee NOT IN (current_user, 'PUBLIC')"
            )
        ).scalars()
        return set(rows)


def runtime_privilege_count(engine, role: str) -> int:
    with engine.connect() as connection:
        return int(
            connection.execute(
                text(
                    "SELECT count(*) FROM information_schema.table_privileges "
                    "WHERE table_schema = 'public' AND grantee = :role"
                ),
                {"role": role},
            ).scalar_one()
        )


def _require_runtime_role(engine) -> str:
    grantees = runtime_grantees(engine)
    if len(grantees) != 1:
        pytest.skip(
            "This check needs exactly one non-owner role holding table grants; "
            f"found {sorted(grantees) or 'none'}."
        )
    return grantees.pop()


def test_the_drill_leaves_the_runtime_roles_privileges_intact(migrated_database, tmp_path):
    """The positive half of the N-20 pair.

    On its own this could pass vacuously — grants that were never at risk are
    also grants that are still there afterwards. It is meaningful **because** the
    next test proves they *are* lost when step 5b is removed. Read the two
    together: without the re-application the privileges vanish and the drill now
    says so; with it, they survive and the drill exits 0.

    Deliberately no `REVOKE` first: the drill re-applies grants for the role that
    held them **before** the destroy, so revoking would leave nothing to detect
    and the drill would correctly do nothing.
    """
    require_postgresql_tools()
    role = _require_runtime_role(migrated_database)
    before = runtime_privilege_count(migrated_database, role)
    assert before > 0

    try:
        completed = run_drill("freedom_test", tmp_path)
        assert completed.returncode == 0, completed.stdout + completed.stderr
        assert f"Runtime role: {role}" in completed.stdout
        assert runtime_privilege_count(migrated_database, role) == before
    finally:
        # Never leave the disposable database without its runtime grants, whatever
        # happened above: every later test in this session would fail obscurely.
        applied = RUNTIME_GRANTS_TEMPLATE.read_text().replace("__APP_ROLE__", role)
        with migrated_database.begin() as connection:
            connection.exec_driver_sql(applied)


def test_the_drill_fails_when_the_privilege_state_is_not_restored(
    migrated_database, tmp_path
):
    """Step 6b must fail, or it is decoration.

    The drill is copied beside its own template — the script derives the template
    path from its own location — and the re-application is removed. What remains
    is exactly the pre-N-20 behaviour, and it must now be caught.
    """
    require_postgresql_tools()
    role = _require_runtime_role(migrated_database)
    assert runtime_privilege_count(migrated_database, role) > 0

    source = DRILL.read_text()
    # PR-20260907-1 replaced the `sed | psql` pipeline with an application of the
    # file step 3d rendered before the destroy. That file is what the recovery
    # procedure names, so this is the statement to remove.
    pipeline = (
        '  psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 '
        '-f "${RUNTIME_GRANTS}" >/dev/null'
    )
    assert pipeline in source, "the re-application step moved; this test is stale"

    neutered = tmp_path / "drill-without-reapplication.sh"
    neutered.write_text(source.replace(pipeline, '  : "removed for this test"', 1))
    neutered.chmod(0o755)
    shutil.copy(RUNTIME_GRANTS_TEMPLATE, tmp_path / RUNTIME_GRANTS_TEMPLATE.name)

    workdir = tmp_path / "work"
    try:
        child = {k: v for k, v in os.environ.items() if k not in LIBPQ_VARIABLES}
        completed = subprocess.run(
            [str(neutered), "freedom_test", str(workdir)],
            cwd=ROOT, capture_output=True, text=True, env=child,
        )
        assert completed.returncode == 1, completed.stdout + completed.stderr
        assert "missing after it" in completed.stderr
        assert "The rows came back and the grants did not" in completed.stderr
    finally:
        applied = RUNTIME_GRANTS_TEMPLATE.read_text().replace("__APP_ROLE__", role)
        with migrated_database.begin() as connection:
            connection.exec_driver_sql(
                "ALTER SCHEMA public OWNER TO pg_database_owner; "
                "REVOKE ALL ON SCHEMA public FROM PUBLIC; "
                "GRANT CREATE, USAGE ON SCHEMA public TO pg_database_owner; "
                "GRANT USAGE ON SCHEMA public TO PUBLIC;"
            )
            connection.exec_driver_sql(applied)


def test_the_drill_preserves_pristine_schema_ownership_and_privileges(
    migrated_database, tmp_path
):
    """DS-R2-1: Prove the drill preserves standard PostgreSQL 16 schema ownership
    and PUBLIC/pg_database_owner privileges across the dump/destroy/restore round trip."""
    require_postgresql_tools()
    with migrated_database.connect() as connection:
        owner, acl = connection.execute(
            text(
                "SELECT pg_get_userbyid(nspowner), nspacl::text "
                "FROM pg_namespace WHERE nspname = 'public'"
            )
        ).one()
    assert owner == "pg_database_owner"
    assert "pg_database_owner=UC/pg_database_owner" in (acl or "")

    completed = run_drill("freedom_test", tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr

    # DS-R3-1: verify both dump and schema-grants are recorded with checksums
    dump_sha256 = tmp_path / "freedom_test.dump.sha256"
    schema_grants = tmp_path / "schema-grants.sql"
    schema_grants_sha256 = tmp_path / "schema-grants.sql.sha256"
    assert dump_sha256.is_file()
    assert schema_grants.is_file()
    assert schema_grants_sha256.is_file()
    check = subprocess.run(
        ["sha256sum", "--check", str(schema_grants_sha256)],
        cwd=tmp_path, capture_output=True, text=True,
    )
    assert check.returncode == 0, check.stdout + check.stderr

    with migrated_database.connect() as connection:
        after_owner, after_acl = connection.execute(
            text(
                "SELECT pg_get_userbyid(nspowner), nspacl::text "
                "FROM pg_namespace WHERE nspname = 'public'"
            )
        ).one()
    assert after_owner == owner
    assert after_acl == acl


def test_the_drill_fails_when_schema_privileges_are_not_restored(
    migrated_database, tmp_path
):
    """DS-R2-1 negative: omitting schema grant restoration must fail the drill."""
    require_postgresql_tools()
    source = DRILL.read_text()
    pipeline = 'psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 -f "${SCHEMA_GRANTS}" >/dev/null'
    assert pipeline in source, "schema grant step moved or changed; test is stale"

    with migrated_database.begin() as connection:
        connection.exec_driver_sql(
            "ALTER SCHEMA public OWNER TO pg_database_owner; "
            "REVOKE ALL ON SCHEMA public FROM PUBLIC; "
            "GRANT CREATE, USAGE ON SCHEMA public TO pg_database_owner; "
            "GRANT USAGE ON SCHEMA public TO PUBLIC;"
        )

    neutered = tmp_path / "drill-without-schema-grants.sh"
    neutered.write_text(source.replace(pipeline, ': "schema grants omitted"', 1))
    neutered.chmod(0o755)
    shutil.copy(RUNTIME_GRANTS_TEMPLATE, tmp_path / RUNTIME_GRANTS_TEMPLATE.name)

    workdir = tmp_path / "work"
    try:
        child = {k: v for k, v in os.environ.items() if k not in LIBPQ_VARIABLES}
        completed = subprocess.run(
            [str(neutered), "freedom_test", str(workdir)],
            cwd=ROOT, capture_output=True, text=True, env=child,
        )
        assert completed.returncode == 1, completed.stdout + completed.stderr
        assert "missing after it" in completed.stderr
        assert "SCHEMA public|pg_database_owner" in completed.stderr
    finally:
        with migrated_database.begin() as connection:
            connection.exec_driver_sql(
                "ALTER SCHEMA public OWNER TO pg_database_owner; "
                "REVOKE ALL ON SCHEMA public FROM PUBLIC; "
                "GRANT CREATE, USAGE ON SCHEMA public TO pg_database_owner; "
                "GRANT USAGE ON SCHEMA public TO PUBLIC;"
            )


def test_recovery_instructions_match_database_development_documentation():
    """DS-R3-1: Verify recovery instructions in backup-restore-drill.sh and database-development.md agree.

    Both must document:
    1. Checksum verification for both the dump and schema-grants.sql.
    2. Restoration using safe pg_restore flags followed by psql -f schema-grants.sql.
    3. Explicit explanation that both artifacts must be retained and that omitting
       schema-grants.sql risks diverging schema ownership or ACL.
    4. Migration fallback for disposable scratch databases.
    """
    ops_doc = (ROOT / "docs" / "operations" / "database-development.md").read_text(encoding="utf-8")
    drill_source = DRILL.read_text(encoding="utf-8")

    # Documented commands in operations guide
    assert "sha256sum --check /var/tmp/drill/freedom_dev.dump.sha256" in ops_doc
    assert "sha256sum --check /var/tmp/drill/schema-grants.sql.sha256" in ops_doc
    assert "pg_restore --dbname=freedom_dev --no-owner --no-privileges" in ops_doc
    assert "psql --dbname=freedom_dev -v ON_ERROR_STOP=1 -f /var/tmp/drill/schema-grants.sql" in ops_doc
    assert "APP_ENVIRONMENT=development DATABASE_URL=<url> ./venv/bin/alembic upgrade head" in ops_doc

    # PR-20260907-1: the runtime table grants, and the verification that says
    # the recovery is finished. Both halves must be in **both** documents, or an
    # operator following one of them gets a database whose rows are all present
    # and whose application role can use none of them.
    assert "sha256sum --check /var/tmp/drill/runtime-grants.sql.sha256" in ops_doc
    assert (
        "psql --dbname=freedom_dev -v ON_ERROR_STOP=1 -f /var/tmp/drill/runtime-grants.sql"
        in ops_doc
    )
    assert "-f /var/tmp/drill/grants-inventory.sql" in ops_doc
    assert "/var/tmp/drill/grants-before.txt" in ops_doc
    assert "comm -23" in ops_doc
    assert "Recovery is complete only when that prints nothing" in ops_doc
    assert "If no runtime role held table grants" in ops_doc
    assert "Re-running the drill is **not** a recovery step" in ops_doc

    # The guide's ordering, as an ordering.
    restore_at = ops_doc.index("pg_restore --dbname=freedom_dev --no-owner")
    schema_at = ops_doc.index(
        "psql --dbname=freedom_dev -v ON_ERROR_STOP=1 -f /var/tmp/drill/schema-grants.sql"
    )
    runtime_at = ops_doc.index(
        "psql --dbname=freedom_dev -v ON_ERROR_STOP=1 -f /var/tmp/drill/runtime-grants.sql"
    )
    verify_at = ops_doc.index("-f /var/tmp/drill/grants-inventory.sql")
    assert restore_at < schema_at < runtime_at < verify_at

    # Script on_exit recovery block
    assert "Every artifact this procedure needs was written before the destroy" in drill_source
    assert "${DUMP}.sha256" in drill_source
    assert "${SCHEMA_GRANTS}.sha256" in drill_source
    assert "${RUNTIME_GRANTS}.sha256" in drill_source
    assert "${GRANT_INVENTORY_SQL}" in drill_source
    assert "${GRANTS_BEFORE}" in drill_source
    assert "All of them must be retained." in drill_source
    assert "sha256sum --check '${DUMP}.sha256'" in drill_source
    assert "sha256sum --check '${SCHEMA_GRANTS}.sha256'" in drill_source
    assert "sha256sum --check '${RUNTIME_GRANTS}.sha256'" in drill_source
    assert "psql --dbname=${DATABASE} -v ON_ERROR_STOP=1 -f '${SCHEMA_GRANTS}'" in drill_source
    assert "psql --dbname=${DATABASE} -v ON_ERROR_STOP=1 -f '${RUNTIME_GRANTS}'" in drill_source
    assert "Recovery is complete only when" in drill_source
    assert "Re-running this drill is NOT a recovery step" in drill_source
    assert "No runtime role held table grants before the destroy" in drill_source

    # PR-20260907-R2-2: the stage table, the data-inventory verification and the
    # two artifacts it needs. Both documents must carry them, or an operator
    # following the guide performs half of the printed recovery.
    for stage in (
        # PR-20260908-R3-1 added `destroy_attempted`, which is the stage where
        # the two documents most easily drift: the script's banner and the
        # guide's table both have to say that nothing is known yet.
        "destroy_attempted",
        "destroyed",
        "restore_attempted",
        "restored",
        "schema_grants_applied",
        "grants_applied",
    ):
        assert stage in ops_doc, stage
        assert f'DRILL_STAGE="{stage}"' in drill_source, stage

    assert "-f /var/tmp/drill/inventory-query.sql" in ops_doc
    assert "/var/tmp/drill/inventory-before.txt" in ops_doc
    assert "${INVENTORY_QUERY_SQL}" in drill_source
    assert "${INVENTORY_AFTER_RECOVERY}" in drill_source

    # The claim that must not survive at a stage where the data is restored.
    assert "In none of those stages is the `pg_restore` line run again." in ops_doc
    assert "must not be restored over" in drill_source
    # And the destructive reset neither document prescribes.
    assert "an operator decision, and\nnot part of this procedure" in ops_doc
    assert "this procedure does not make it" in drill_source

    # PR-20260907-R2-1: the transport, in both documents.
    assert "ROLE <the role name's UTF-8 bytes, hex encoded>" in ops_doc
    assert "END <the number of records>" in ops_doc
    assert "a report that cannot be read says nothing about how" in ops_doc
    assert "encode(convert_to(role_name, 'UTF8'), 'hex')" in drill_source
    assert "the runtime-role report could not be read" in drill_source

    # PR-20260908-R3-2: the NUL refusal, in both documents. The guide must state
    # the refusal *and* why a substring search would be the wrong check, or an
    # operator reading only the guide would not know which reports refuse.
    assert "a role record carried a NUL byte" in ops_doc
    assert "a role record carried a NUL byte" in drill_source
    assert "malformed transport" in ops_doc
    assert "hex_record_contains_nul" in drill_source

    # PR-20260908-R3-1: the destroy states, the step-0 reports, and the claim
    # that must never be made for a destroy that did not report success.
    assert "the destroy ran and **did not report success**" in ops_doc
    assert "the destroy **reported success**" in ops_doc
    assert "A failed or uncertain destroy is never described as a" in ops_doc
    # The banner text is line wrapped in the script, so it is read as one run of
    # whitespace-separated words rather than matched across its own wrapping.
    said_by_script = _one_line(drill_source)
    assert "WHAT THE SCHEMA NOW HOLDS IS NOT KNOWN" in said_by_script
    assert "This drill does not call the database empty here" in said_by_script
    # The two state artifacts, in both.
    assert "-f /var/tmp/drill/schema-state.sql" in ops_doc
    assert "/var/tmp/drill/schema-state-before.txt" in ops_doc
    assert "${SCHEMA_STATE_SQL}" in drill_source
    assert "${SCHEMA_STATE_BEFORE}" in drill_source
    assert "${SCHEMA_STATE_AFTER_RECOVERY}" in drill_source
    # The five states, in the guide's own table.
    assert "the state is **still not known**" in ops_doc
    assert "the destroy did not take effect" in ops_doc
    assert "**dropped and recreated**" in ops_doc
    assert "the schema is **absent**" in ops_doc
    assert "an **unexpected** state" in ops_doc

    # PR-20260908-R3-1 continued: what the state report observes, what it cannot
    # establish, and the state it therefore leaves for an operator. Both
    # documents must carry all three, or an operator reading one of them would
    # act on a claim the other withdrew.
    for observation in ("routines", "types", "extensions", "other_objects"):
        assert observation in ops_doc, observation
        assert observation in drill_source, observation
    said_by_guide = _one_line(ops_doc)
    assert "equal counts are not an object-identity inventory" in said_by_guide
    assert "equal counts are not an object-identity inventory" in _one_line(
        "\n".join(
            line.lstrip("#").strip() for line in drill_source.splitlines()
        )
    )
    assert "these reports cannot resolve this state" in said_by_guide.lower()
    assert "THESE REPORTS CANNOT RESOLVE" in said_by_script
    assert 'this is not "there was nothing to lose"' in said_by_guide.lower()
    assert "THIS IS NOT 'THERE WAS NOTHING TO LOSE'" in said_by_script
    # The identity inventory both documents point an operator at.
    assert "pg_restore --list" in ops_doc
    assert "pg_restore --list" in drill_source

    # And the inferences that were withdrawn, in every form either document
    # wrote them. A regression that only required the new sentences would leave
    # the old claim free to sit beside it.
    for withdrawn in (
        "the database held no objects before the drill",
        "Nothing was lost either way",
        "there was nothing to lose",
        "no data restore is required: skip to step 5",
    ):
        assert withdrawn not in drill_source, withdrawn
    # The guide still *narrates* the withdrawn claim, because an operator needs
    # to know it was withdrawn. What must be gone is the claim made as an
    # instruction, so these are the prescriptive forms.
    for withdrawn in (
        "the destroy did not take effect and nothing was lost",
        "since there was nothing to lose",
        "re-apply the grant files and run the two verifications",
    ):
        assert withdrawn not in ops_doc, withdrawn
    assert "nothing was lost either way" not in said_by_guide.lower()

    # The dependent branch, corrected in the same scope: `restore_attempted`
    # read the row inventory alone, and on an archive with no base tables a
    # rolled-back restore and a committed one produce the same output.
    assert "The row inventory alone cannot answer this question" in ops_doc
    assert "THE ROW INVENTORY ALONE CANNOT ANSWER THIS" in said_by_script
    assert "empty output from the query: the transaction rolled back" not in (
        drill_source
    )
    assert "Empty output from the query means the transaction rolled back" not in (
        ops_doc
    )

    # PR-20260908-R5-1: the completion boundary, in both documents. A guide that
    # kept R4's unconditional outcomes beside the script's gated ones would send
    # an operator to skip or repeat a recovery the script refuses to decide.
    assert "Has the server-side transaction ended?" in said_by_guide
    assert "HAS THE DESTROY'S SERVER-SIDE TRANSACTION ENDED?" in said_by_script
    assert "HAS THE RESTORE'S SERVER-SIDE TRANSACTION ENDED?" in said_by_script
    assert "every outcome in step 0b is provisional" in said_by_guide.lower()
    assert "EVERY OUTCOME IN 0b IS PROVISIONAL" in said_by_script
    for boundary in (
        "client_connection_check_interval=0",
        "pg_stat_activity",
        "backend_start",
    ):
        assert boundary in ops_doc, boundary
        assert boundary in drill_source, boundary
    # What is not proof, in both.
    assert "elapsed time" in said_by_guide
    assert "elapsed time" in said_by_script
    assert "running the reports twice and getting the same answer" in said_by_guide
    assert "running the reports twice and getting the same answer" in said_by_script
    # The unresolved stop, in both.
    assert "the outcome is unresolved" in said_by_guide.lower()
    assert "IF COMPLETION CANNOT BE ESTABLISHED, THE OUTCOME IS UNRESOLVED" in (
        said_by_script
    )
    # The authority neither document takes, stated in both and taken in neither.
    assert "do not terminate or cancel a backend" in said_by_guide.lower()
    assert "Do not terminate or cancel a backend to settle this" in said_by_script
    for authority in ("pg_terminate_backend", "pg_cancel_backend"):
        assert authority not in ops_doc, authority
        assert authority not in drill_source, authority
    # And the visibility limit, as PostgreSQL 16 actually draws it: columns are
    # restricted, rows are not. Both documents must say that a session row can
    # be visible while the fields that would settle the question are null, and
    # neither may claim that permissions hide the row itself.
    assert "restricts columns" in said_by_guide.lower()
    assert "restricts columns here, not rows" in said_by_script
    assert "pg_read_all_stats" in said_by_guide
    assert "pg_read_all_stats" in said_by_script
    assert "visible to all users" in said_by_guide
    assert "are visible to all users" in said_by_script
    assert "is not proof that this transaction has ended" in said_by_guide.lower()
    assert "IS NOT PROOF THAT THIS TRANSACTION HAS ENDED" in said_by_script
    # The primary reference, in the guide that an operator reads.
    assert "monitoring-stats.html#MONITORING-STATS-VIEWS" in ops_doc
    # The withdrawn claim, in every form either document wrote it.
    for withdrawn in (
        "a session whose row you cannot see is not a session that has ended",
        "is restricted in what it sees of another role's session",
        "not equally readable to every role",
    ):
        assert withdrawn not in ops_doc, withdrawn
        assert withdrawn not in drill_source, withdrawn

    # The guide's step-0 report is read before its full procedure, as an
    # ordering, so the guide cannot drift into restoring first. Its completion
    # gate is read before the report, for the same reason.
    destroy_step_zero = ops_doc.index("-f /var/tmp/drill/schema-state.sql")
    assert destroy_step_zero < restore_at
    assert ops_doc.index("**Step 0a, at stages") < destroy_step_zero


def test_the_drill_emits_recovery_instructions_with_checksum_verification_on_failure(
    migrated_database, tmp_path
):
    """DS-R3-1: When schema is dropped and restore fails, script must emit recovery instructions with checksum verification."""
    require_postgresql_tools()
    source = DRILL.read_text(encoding="utf-8")
    # Force restore command to fail after schema is dropped
    bad_restore = 'echo "Simulated restore failure" >&2; exit 42'
    neutered = tmp_path / "drill-failing-restore.sh"
    neutered.write_text(source.replace('"${RESTORE_COMMAND[@]}"', bad_restore, 1), encoding="utf-8")
    neutered.chmod(0o755)
    shutil.copy(RUNTIME_GRANTS_TEMPLATE, tmp_path / RUNTIME_GRANTS_TEMPLATE.name)

    workdir = tmp_path / "work"
    try:
        child = {k: v for k, v in os.environ.items() if k not in LIBPQ_VARIABLES}
        completed = subprocess.run(
            [str(neutered), "freedom_test", str(workdir)],
            cwd=ROOT, capture_output=True, text=True, env=child,
        )
        assert completed.returncode == 42
        assert "RECOVERY REQUIRED." in completed.stderr
        assert "freedom_test.dump.sha256" in completed.stderr
        assert "schema-grants.sql.sha256" in completed.stderr
        assert "All of them must be retained." in completed.stderr
        assert "sha256sum --check" in completed.stderr
        assert "schema-grants.sql" in completed.stderr
        # PR-20260907-1: the verification step and the runtime half, whichever
        # of the two forms this database produces.
        assert "grants-inventory.sql" in completed.stderr
        assert "Recovery is complete only when" in completed.stderr
        assert "Re-running this drill is NOT a recovery step" in completed.stderr
        banner = _one_line(completed.stderr)
        assert (
            "runtime-grants.sql.sha256" in banner
            or "No runtime role held table grants before the destroy" in banner
        )

        # Verify the created artifacts exist and their checksums pass
        dump_file = workdir / "freedom_test.dump"
        dump_sha256 = workdir / "freedom_test.dump.sha256"
        schema_grants = workdir / "schema-grants.sql"
        schema_grants_sha256 = workdir / "schema-grants.sql.sha256"

        assert dump_file.is_file()
        assert dump_sha256.is_file()
        assert schema_grants.is_file()
        assert schema_grants_sha256.is_file()

        check_dump = subprocess.run(
            ["sha256sum", "--check", str(dump_sha256)],
            cwd=workdir, capture_output=True, text=True,
        )
        assert check_dump.returncode == 0, check_dump.stdout + check_dump.stderr

        check_schema = subprocess.run(
            ["sha256sum", "--check", str(schema_grants_sha256)],
            cwd=workdir, capture_output=True, text=True,
        )
        assert check_schema.returncode == 0, check_schema.stdout + check_schema.stderr

        # Prove the documented recovery procedure successfully recovers the database
        restore_res = subprocess.run(
            [
                "pg_restore",
                "--dbname=freedom_test",
                "--no-owner",
                "--no-privileges",
                "--single-transaction",
                "--exit-on-error",
                str(dump_file),
            ],
            capture_output=True,
            text=True,
        )
        assert restore_res.returncode == 0, restore_res.stdout + restore_res.stderr

        schema_res = subprocess.run(
            ["psql", "--dbname=freedom_test", "-v", "ON_ERROR_STOP=1", "-f", str(schema_grants)],
            capture_output=True,
            text=True,
        )
        assert schema_res.returncode == 0, schema_res.stdout + schema_res.stderr
    finally:
        with migrated_database.begin() as connection:
            connection.exec_driver_sql(
                "ALTER SCHEMA public OWNER TO pg_database_owner; "
                "REVOKE ALL ON SCHEMA public FROM PUBLIC; "
                "GRANT CREATE, USAGE ON SCHEMA public TO pg_database_owner; "
                "GRANT USAGE ON SCHEMA public TO PUBLIC;"
            )


# --------------------------------------------------------------------------
# DS-R8-1 (2026-09-06): `detect_runtime_role` may return more than one grantee,
# and the script assigned its result through `tr -d '[:space:]'` *before*
# testing RUNTIME_ROLE for a newline. The separator had already been deleted, so
# the ambiguity branch was unreachable: two roles became one concatenated
# identifier, the drill accepted it, and the destructive restore cycle began
# before grant re-application could fail.
#
# These tests answer that question **without a database and without the
# destructive drill**. The drill is run against a PATH shim whose `psql`,
# `pg_dump` and `pg_restore` are stubs that record every invocation to a log, so
# a test can assert that the refusal happened *before* `DROP SCHEMA` was ever
# issued — which is the property the finding is about, and which running the
# real drill would prove only by destroying something.
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# The catalog states the stub boundary can model -- PR-20260908-R3-1, continued.
#
# A modelled `public` is a mapping from object class to how many objects of that
# class it holds. **The report the stub returns is that mapping projected through
# the drill's own `schema-state.sql`**, which is read out of the script rather
# than copied into this module. That projection is the whole point: a report can
# only ever observe the classes its query asks about, so a schema holding one
# function projects to `relations=0|base_tables=0` under a query that counts only
# relations, and the two failing-destroy scenarios become indistinguishable. A
# stub that answered with a literal chosen by the test would hide exactly the
# defect this finding is about.
#
# This is **transport-shaped evidence only**. It establishes which recovery
# decision the drill emits for a given pair of reports, and it establishes
# nothing about whether the SQL counts a real catalog correctly; that needs an
# authorized PostgreSQL run and is not claimed here.
def _schema_state_query(source: str) -> str:
    """The drill's `schema-state.sql` heredoc, read out of the script."""
    body = source[source.index('cat >"${SCHEMA_STATE_SQL}"') :]
    marker = "<<'SQL'\n"
    body = body[body.index(marker) + len(marker) :]
    return body[: body.index("\nSQL\n")]


def _schema_state_fields(source: str) -> tuple[str, ...]:
    """The count fields that query emits, in the order it concatenates them."""
    return tuple(re.findall(r"'\|([a-z_]+)='", _schema_state_query(source)))


#: The classes the drill's report actually counts. Read from the script, so a
#: class the query stops counting disappears from the modelled report too.
SCHEMA_STATE_FIELDS = _schema_state_fields(DRILL.read_text(encoding="utf-8"))


def schema_state_report(catalog: dict[str, int], present: bool = True) -> str:
    """`catalog` as the drill's own query would report it."""
    unknown = set(catalog) - set(SCHEMA_STATE_FIELDS)
    assert not unknown or unknown <= {"relations", "base_tables", "routines",
                                      "types", "extensions", "other_objects"}, (
        f"not a modelled object class: {sorted(unknown)}"
    )
    fields = "".join(f"|{name}={catalog.get(name, 0)}" for name in SCHEMA_STATE_FIELDS)
    return f"schema_present={str(present).lower()}{fields}"


def _counted_objects(report: str) -> int:
    """How many objects a report line counts, across every class it carries.

    The banner's outcomes are keyed on "some count is non-zero" and "every count
    is zero", so the tests read a report the same way rather than matching one
    field. `base_tables` is excluded because it is a subset of `relations` and
    would double-count an ordinary table; it changes no outcome either way.
    """
    fields = dict(pair.split("=", 1) for pair in report.split("|") if "=" in pair)
    return sum(
        int(value)
        for name, value in fields.items()
        if name not in ("schema_present", "base_tables")
    )


#: A `public` that holds nothing at all. It is what a freshly recreated schema
#: holds -- **and what a schema holding only an object of a kind the report does
#: not count reports**, which is why an all-zero baseline is unresolved rather
#: than empty.
CATALOG_NOTHING: dict[str, int] = {}

#: One ordinary table: the state the older stub hard-coded.
CATALOG_ONE_TABLE = {"relations": 1, "base_tables": 1}

#: **The finding.** A schema whose only object is a function. `pg_class` does not
#: describe it and the row inventory does not see it, so under a relations-only
#: report this was indistinguishable from an empty schema.
CATALOG_ONE_FUNCTION = {"routines": 1}

#: A schema whose only object is a standalone type -- the other object kind the
#: finding names, and a second class `pg_class` does not describe. Counting
#: routines alone would have left this exactly where it was.
CATALOG_ONE_TYPE = {"types": 1}

SCHEMA_STATE_NOTHING_COUNTED = schema_state_report(CATALOG_NOTHING)
SCHEMA_STATE_ONE_TABLE = schema_state_report(CATALOG_ONE_TABLE)
SCHEMA_STATE_ONE_FUNCTION = schema_state_report(CATALOG_ONE_FUNCTION)
SCHEMA_STATE_ONE_TYPE = schema_state_report(CATALOG_ONE_TYPE)

#: What `psql -tA` prints for the row inventory of a schema with no base tables:
#: `string_agg` over no rows is NULL, and an unaligned tuples-only result prints
#: it as an empty line.
EMPTY_INVENTORY = ""


STUB_PSQL = r"""#!/usr/bin/env bash
set -u
sql=""
file=""
prev=""
for argument in "$@"; do
  case "${prev}" in
    -c) sql="${argument}" ;;
    -f) file="${argument}" ;;
  esac
  prev="${argument}"
done
if [[ -z "${sql}" && -z "${file}" ]] || [[ "${file}" == "-" ]]; then
  sql="$(cat)"
elif [[ -n "${file}" && -r "${file}" ]]; then
  # PR-20260907-1: the drill now applies saved artifacts with `psql -f PATH`
  # rather than piping them in, so the stub has to read what is actually being
  # executed. Without this the stub would log an empty statement and a test
  # asserting on the emitted SQL would assert on nothing.
  sql="$(cat "${file}")"
fi
printf 'psql\t%s\t%s\n' "$*" "${sql//$'\n'/ }" >>"__LOG__"

# PR-20260907-R2-2: the boundary is **stateful**. It remembers that the
# destructive step has run, so an observation taken after it can differ from the
# same observation taken before -- which is what lets a test drive the drill's
# own verification to a failure at a stage where the data restore has already
# committed. A stateless stub can only ever fail the restore.
# PR-20260908-R3-1: the destroy itself can now fail, and it can fail with the
# schema **intact** or with it already dropped. `__DESTROY_APPLIED__` decides
# which, and it is deliberately independent of `__DESTROY_EXIT__`: the whole
# finding is that the drill cannot tell those two outcomes apart from the
# outside, so the boundary must be able to produce both behind one failing exit
# status.
# PR-20260908-R5-1: **whether that transaction has ENDED is a third thing**, and
# it is independent of both. `__DESTROY_COMPLETED__=0` models a statement that
# reached the server and whose backend is still running it: nothing it did is
# visible to any other session yet, so every report still shows the state that
# was committed before it began, and the outstanding transaction is recorded in
# a marker that no report reads. A test ends it deterministically with
# `resolve_pending_transaction` -- which is what "the commit happens after the
# observation" means here, with no sleep and no timing dependence.
if [[ "${sql}" == *"DROP SCHEMA public CASCADE"* ]]; then
  if [[ "__DESTROY_COMPLETED__" == "1" ]]; then
    if [[ "__DESTROY_APPLIED__" == "1" ]]; then
      : >"__STATE__.dropped"
    fi
  else
    printf '%s\n' "__DESTROY_APPLIED__" >"__STATE__.destroy-pending"
  fi
  if (( __DESTROY_EXIT__ != 0 )); then
    echo "stub: the destroy was refused" >&2
    exit __DESTROY_EXIT__
  fi
fi
after_destroy=0
[[ -e "__STATE__.dropped" ]] && after_destroy=1

# Failure injection by the artifact being applied, so a test can stop the drill
# at exactly one stage: schema grants applied and runtime grants not, or both
# applied and the verification failing.
if [[ -n "${file}" ]]; then
  case "${file##*/}" in
    schema-grants.sql)
      if (( __SCHEMA_GRANTS_EXIT__ != 0 )); then
        echo "stub: schema grants rejected" >&2
        exit __SCHEMA_GRANTS_EXIT__
      fi ;;
    runtime-grants.sql)
      if (( __RUNTIME_GRANTS_EXIT__ != 0 )); then
        echo "stub: runtime grants rejected" >&2
        exit __RUNTIME_GRANTS_EXIT__
      fi ;;
  esac
fi

if [[ "${sql}" == *"current_database()"* ]]; then
  printf '%s|true||\n' "__DATABASE__"
elif [[ "${sql}" == *"'ROLE ' || encode"* ]]; then
  # PR-20260907-R2-1: the drill's runtime-role report is now `ROLE <hex>` records
  # and an `END <count>` terminator, so the stub emits that transport. Exiting
  # non-zero here is how a failing client is exercised.
  if (( __REPORT_EXIT__ != 0 )); then
    echo "stub: the runtime-role query failed" >&2
    exit __REPORT_EXIT__
  fi
  cat "__GRANTEES__"
elif [[ "${sql}" == *"ALTER SCHEMA public OWNER"* ]]; then
  printf 'ALTER SCHEMA public OWNER TO pg_database_owner;\n'
elif [[ "${sql}" == *"to_regnamespace"* ]]; then
  # PR-20260908-R3-1: the structural report the `destroy_attempted` banner tells
  # the operator to run. It answers differently before and after the destroy,
  # which is what makes the two failing-destroy scenarios distinguishable by the
  # printed step 0 even though the drill itself cannot tell them apart.
  #
  # **The two answers are parameters, not literals** (PR-20260908-R3-1
  # continued). The catalog state a test wants to model -- a schema holding one
  # table, one function, one standalone type, or nothing this report counts --
  # is what decides whether the printed step 0 can reach a true conclusion, so
  # it has to be settable independently of `__DESTROY_EXIT__` and of
  # `__DESTROY_APPLIED__`.
  # PR-20260908-R5-1: a third answer, for after a restore's transaction has
  # committed. Until it does -- and while it is still running -- the schema is
  # whatever the destroy left, which is the point: `--single-transaction`
  # publishes nothing until the commit.
  if [[ -e "__STATE__.restored" ]]; then
    printf '%s\n' "__SCHEMA_STATE_RESTORED__"
  elif (( after_destroy == 1 )); then
    printf '%s\n' "__SCHEMA_STATE_DROPPED__"
  else
    printf '%s\n' "__SCHEMA_STATE_INTACT__"
  fi
elif [[ "${sql}" == *"query_to_xml"* ]]; then
  if (( after_destroy == 1 )) && [[ "__INVENTORY_MISMATCH__" == "1" ]]; then
    printf 'characters=2\n'
  else
    printf '%s\n' "__INVENTORY__"
  fi
elif [[ "${sql}" == *"aclexplode"* ]]; then
  if (( after_destroy == 1 )) && [[ "__PRIVILEGE_LOSS__" == "1" ]]; then
    printf '(no grants)\n'
  else
    printf 'SCHEMA public|pg_database_owner|USAGE\n'
  fi
fi
exit 0
"""

STUB_PG_DUMP = r"""#!/usr/bin/env bash
set -u
destination=""
for argument in "$@"; do
  case "${argument}" in
    --file=*) destination="${argument#--file=}" ;;
  esac
done
printf 'stub archive\n' >"${destination}"
printf 'pg_dump\t%s\t\n' "$*" >>"__LOG__"
exit 0
"""

STUB_PG_RESTORE = r"""#!/usr/bin/env bash
set -u
printf 'pg_restore\t%s\t\n' "$*" >>"__LOG__"
# PR-20260908-R5-1: the same three-way split as the destroy. `__RESTORE_APPLIED__`
# says whether this restore's transaction puts the archive's objects back, and
# `__RESTORE_COMPLETED__` says whether it has ENDED. A restore that is still
# running has published nothing -- --single-transaction makes every object it has
# loaded invisible to other sessions until it commits -- so the reports still see
# the empty schema the destroy left, which is exactly the state a rolled-back
# restore leaves too.
if [[ "__RESTORE_COMPLETED__" == "1" ]]; then
  if [[ "__RESTORE_APPLIED__" == "1" ]]; then
    : >"__STATE__.restored"
  fi
else
  printf '%s\n' "__RESTORE_APPLIED__" >"__STATE__.restore-pending"
fi
exit __RESTORE_EXIT__
"""


def encoded_role_report(grantees: list[str]) -> str:
    """The `ROLE <hex>` / `END <count>` report the drill's query emits.

    **This is transport evidence, and only transport evidence** (PR-20260907-R2-1
    item 5). It is what `psql -tA` prints for the drill's query when the catalog
    holds `grantees`, computed here rather than by PostgreSQL. Driving the drill
    with it proves that the shell decodes records losslessly, counts them
    correctly and classifies the decoded bytes — it proves **nothing** about
    whether the SQL encodes the catalog correctly, because no SQL runs. That half
    is `test_a_newline_bearing_role_refuses_against_postgresql`, which is
    deselected here and belongs to an authorized run.

    The ordering matches the query's `ORDER BY ordinal, line`: the records sorted
    by their emitted text, then the terminator.
    """
    lines = sorted(f"ROLE {name.encode('utf-8').hex()}" for name in grantees)
    lines.append(f"END {len(grantees)}")
    return "".join(f"{line}\n" for line in lines)


def _role_report_sql(source: str) -> str:
    """The drill's own runtime-role query, read out of the script.

    Read rather than copied. A PostgreSQL regression that asserted a duplicated
    query would keep passing after the script's query changed, which is the
    failure mode `test_the_cardinality_test_no_longer_reads_a_string_its_
    separator_was_deleted_from` exists to avoid for the shell half.
    """
    body = source[source.index("detect_runtime_role() {") :]
    marker = "<<'SQL'\n"
    body = body[body.index(marker) + len(marker) :]
    return body[: body.index("\nSQL\n")]


def test_the_role_report_query_can_be_read_out_of_the_script():
    """The extraction above, checked without a database.

    The PostgreSQL regression that uses it is deselected here, so this is what
    keeps the helper from silently extracting nothing.
    """
    query = _role_report_sql(DRILL.read_text(encoding="utf-8"))

    assert "encode(convert_to(role_name, 'UTF8'), 'hex')" in query
    assert "'END ' || (SELECT count(*) FROM roles)::text" in query
    assert "information_schema.table_privileges" in query
    assert "ORDER BY ordinal, line" in query


def run_drill_against_stubs(
    tmp_path: Path,
    grantees: list[str],
    database: str = "freedom_test",
    restore_exit: int = 0,
    report_override: str | None = None,
    report_exit: int = 0,
    destroy_exit: int = 0,
    destroy_applied: bool = True,
    destroy_completed: bool = True,
    restore_applied: bool | None = None,
    restore_completed: bool = True,
    schema_grants_exit: int = 0,
    runtime_grants_exit: int = 0,
    inventory_mismatch: bool = False,
    privilege_loss: bool = False,
    schema_state_intact: str = SCHEMA_STATE_ONE_TABLE,
    schema_state_dropped: str = SCHEMA_STATE_NOTHING_COUNTED,
    schema_state_restored: str | None = None,
    inventory: str = "characters=1",
) -> tuple[subprocess.CompletedProcess[str], str]:
    """Run the real drill with stubbed PostgreSQL clients.

    `grantees` is encoded into the report the drill's query emits, so record
    boundaries and record contents both survive exactly as they will in
    production. Returns the completed process and the invocation log, which is
    the evidence for *when* a refusal happened.

    `report_override` replaces that report with raw text, which is how a
    malformed or truncated transport is exercised; `report_exit` makes the query
    itself fail.

    The remaining parameters inject a failure at one **stage** of the drill
    (PR-20260907-R2-2), so the recovery banner can be exercised at each of them
    **without destroying a database**: every `DROP SCHEMA` goes to a stub that
    records it and does nothing.

    * `destroy_exit` / `destroy_applied` — the destroy does not report success
      (PR-20260908-R3-1). The two are independent on purpose: `destroy_applied`
      says whether the schema was really dropped, and the drill cannot see it.
      `destroy_exit=42, destroy_applied=False` is Codex's reproduction — a
      refused DROP with the database untouched.
    * `destroy_completed` / `restore_completed` — whether that statement's
      **server-side transaction has ended** (PR-20260908-R5-1). A third
      independent axis: a client that exited does not establish that the backend
      stopped, so `destroy_completed=False` models a DROP that reached the server
      and is still running. Nothing it did is visible to any other session while
      it runs, and `resolve_pending_transaction` ends it afterwards.
    * `restore_exit` / `restore_applied` — the data restore does not report
      success, and whether its transaction puts the archive's objects back.
      `restore_applied` defaults to "the restore committed exactly when it
      reported success", which is the behaviour every earlier test assumed.
    * `schema_grants_exit` — the restore committed; the schema grants fail.
    * `runtime_grants_exit` — the restore and schema grants committed; the
      runtime grants fail.
    * `privilege_loss` / `inventory_mismatch` — everything applied and the
      drill's own step 6b or step 6 verification fails.

    `schema_state_intact`, `schema_state_dropped` and `inventory` are the
    **catalog state** the boundary models, and they are independent of every
    parameter above (PR-20260908-R3-1, continued). The finding is that a schema
    holding only a function reports no relations and no base tables, so the
    scenario a test needs — what the schema held before the destroy, and what it
    holds after — cannot be derived from the destroy's exit status or from
    whether the drop was applied. It has to be stated. `schema_state_restored`
    is the third of them (PR-20260908-R5-1): what the report says once a restore
    has actually committed, which is how a pending restore is told from a
    rolled-back one *after* the fact rather than from the counts alone.
    """
    if restore_applied is None:
        restore_applied = restore_exit == 0
    if schema_state_restored is None:
        schema_state_restored = schema_state_intact
    # A transaction that never ended behind a command that reported success is
    # not a state this boundary can model coherently, and no test needs it: the
    # drill would have gone on to the next step believing the previous one
    # finished. Refuse it rather than produce a scenario nobody can read.
    assert destroy_completed or destroy_exit != 0, (
        "a destroy that reported success cannot have left its transaction open"
    )
    assert restore_completed or restore_exit != 0, (
        "a restore that reported success cannot have left its transaction open"
    )

    stub_bin = tmp_path / "stub-bin"
    stub_bin.mkdir()
    log = tmp_path / "invocations.log"
    log.write_text("", encoding="utf-8")
    grantee_file = tmp_path / "grantees.txt"
    grantee_file.write_text(
        encoded_role_report(grantees) if report_override is None else report_override,
        encoding="utf-8",
    )

    substitutions = {
        "__LOG__": str(log),
        "__GRANTEES__": str(grantee_file),
        "__STATE__": str(tmp_path / "stub-state"),
        "__DATABASE__": database,
        "__RESTORE_EXIT__": str(restore_exit),
        "__REPORT_EXIT__": str(report_exit),
        "__DESTROY_EXIT__": str(destroy_exit),
        "__DESTROY_APPLIED__": "1" if destroy_applied else "0",
        "__DESTROY_COMPLETED__": "1" if destroy_completed else "0",
        "__RESTORE_APPLIED__": "1" if restore_applied else "0",
        "__RESTORE_COMPLETED__": "1" if restore_completed else "0",
        "__SCHEMA_GRANTS_EXIT__": str(schema_grants_exit),
        "__RUNTIME_GRANTS_EXIT__": str(runtime_grants_exit),
        "__INVENTORY_MISMATCH__": "1" if inventory_mismatch else "0",
        "__PRIVILEGE_LOSS__": "1" if privilege_loss else "0",
        "__SCHEMA_STATE_INTACT__": schema_state_intact,
        "__SCHEMA_STATE_DROPPED__": schema_state_dropped,
        "__SCHEMA_STATE_RESTORED__": schema_state_restored,
        "__INVENTORY__": inventory,
    }
    for name, body in (
        ("psql", STUB_PSQL),
        ("pg_dump", STUB_PG_DUMP),
        ("pg_restore", STUB_PG_RESTORE),
    ):
        for placeholder, value in substitutions.items():
            body = body.replace(placeholder, value)
        executable = stub_bin / name
        executable.write_text(body, encoding="utf-8")
        executable.chmod(0o755)

    child = {
        key: value
        for key, value in os.environ.items()
        if key not in LIBPQ_VARIABLES
    }
    child["PATH"] = f"{stub_bin}{os.pathsep}{os.environ.get('PATH', '')}"

    workdir = tmp_path / "work"
    completed = subprocess.run(
        [str(DRILL), database, str(workdir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=child,
    )
    return completed, log.read_text(encoding="utf-8")


#: The marker the boundary writes for a transaction that reached the server and
#: has not ended, and the marker that records the change once it commits. No
#: report reads the pending marker: an outstanding transaction is invisible to
#: every other session, which is the whole of PR-20260908-R5-1.
PENDING_MARKER = {"destroy": "destroy-pending", "restore": "restore-pending"}
COMMITTED_MARKER = {"destroy": "dropped", "restore": "restored"}


def resolve_pending_transaction(scenario: Path, stage: str, outcome: str) -> None:
    """End a transaction the boundary left outstanding — deterministically.

    This is the barrier the PR-20260908-R5-1 regressions are built on. The
    original client is long gone and the reports have already been read; calling
    this is the moment the backend that outlived it commits or aborts. It is an
    explicit state transition, not a sleep, so the ordering "observe, then the
    transaction ends" is a property of the test rather than of the machine it
    runs on.
    """
    assert outcome in ("commit", "rollback"), outcome
    prefix = scenario / "stub-state"
    pending = prefix.with_name(f"{prefix.name}.{PENDING_MARKER[stage]}")
    assert pending.is_file(), f"the boundary left no pending {stage} transaction"
    # What the transaction would do if it commits, recorded when it was issued.
    applies = pending.read_text(encoding="utf-8").strip() == "1"
    if outcome == "commit" and applies:
        prefix.with_name(f"{prefix.name}.{COMMITTED_MARKER[stage]}").write_text(
            "", encoding="utf-8"
        )
    pending.unlink()


def read_state_report(scenario: Path) -> str:
    """Run the state report the banner prints, through the same stub boundary.

    Exactly the command an operator would run out of the banner, against the
    boundary the drill itself ran against, so what it returns is what that
    operator would see at that moment.
    """
    result = subprocess.run(
        [
            str(scenario / "stub-bin" / "psql"),
            "--dbname=freedom_test",
            "-tAX",
            "-v",
            "ON_ERROR_STOP=1",
            "-f",
            str(scenario / "work" / "schema-state.sql"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def test_zero_runtime_roles_follow_the_existing_empty_path(tmp_path):
    """A zero-row result is still the documented no-runtime-role path."""
    completed, log = run_drill_against_stubs(tmp_path, [])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "No runtime role holds table grants here" in completed.stdout
    assert "Skipped: no runtime role held grants before the destroy." in completed.stdout
    assert "Runtime role:" not in completed.stdout
    # The empty path still performs the round trip; it simply re-applies nothing.
    assert "DROP SCHEMA public CASCADE" in log
    assert "__APP_ROLE__" not in log


def test_one_runtime_role_is_retained_exactly_and_reaches_grant_reapplication(
    tmp_path,
):
    """The single-row path is unchanged in substance: the name is kept exactly
    as the query returned it and reaches step 5b's template.

    **This is also the positive control for the refusal tests below.** Without
    it, "no `DROP SCHEMA` in the log" would be satisfied by a stubbed drill that
    never reached step 4 for some unrelated reason. Here it does reach it, so an
    absent drop elsewhere is attributable to the refusal and not to the shim.
    """
    completed, log = run_drill_against_stubs(tmp_path, ["freedom_runtime_test"])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "    Runtime role: freedom_runtime_test" in completed.stdout
    assert "Applied runtime-grants.sql for freedom_runtime_test" in completed.stdout
    # The template really was rendered with that role and no other.
    assert "GRANT USAGE ON SCHEMA public TO freedom_runtime_test;" in log
    assert "__APP_ROLE__" not in log
    # The control: the destructive step is reachable through this boundary.
    assert "DROP SCHEMA public CASCADE" in log
    assert "Restore verified" in completed.stdout


def test_two_distinct_runtime_roles_refuse_with_exit_status_two(tmp_path):
    """The branch DS-R8-1 found unreachable, now reached.

    **The diagnostic names the roles in their transported form** since
    PR-20260907-R2-1: a catalog role name is arbitrary bytes and may carry
    newlines, control characters or terminal escapes, so the refusal prints the
    hex the report carried rather than pasting catalog content into an operator's
    terminal. Both roles are still identified, which is what the diagnostic is
    for.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test", "freedom_reporting"]
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "more than one non-owner role holds table grants" in completed.stderr
    assert "Roles found: 2, hex encoded:" in completed.stderr
    for name in ("freedom_runtime_test", "freedom_reporting"):
        assert name.encode("utf-8").hex() in completed.stderr, name
        # And the raw bytes are not printed.
        assert name not in completed.stderr, name


def test_the_multiple_role_refusal_happens_before_the_schema_is_dropped(tmp_path):
    """Where the refusal happens, not merely that it happens.

    `DRILL_STAGE="destroy_attempted"` and `DROP SCHEMA` are both in step 4. The refusal
    is in
    step 3b, so neither has run: the log carries no drop, and the exit trap
    prints no recovery banner because there is nothing to recover.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test", "freedom_reporting"]
    )

    assert completed.returncode == 2
    assert "DROP SCHEMA" not in log
    assert "pg_restore" not in log
    assert "RECOVERY REQUIRED" not in completed.stderr
    assert "4. Destroying the schema" not in completed.stdout


def test_whitespace_removal_cannot_concatenate_two_records_into_one_role(tmp_path):
    """The exact defect, in the shape that made it invisible.

    `tr -d '[:space:]'` turned the two records `app` and `role` into the single
    identifier `approle`, which is a perfectly well-formed role name — so no
    later check could have caught it either. Two records must refuse, and the
    concatenation must appear nowhere.
    """
    completed, log = run_drill_against_stubs(tmp_path, ["app", "role"])

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "more than one non-owner role holds table grants" in completed.stderr
    assert "Roles found: 2, hex encoded:" in completed.stderr
    assert "approle" not in completed.stdout
    assert "approle" not in completed.stderr
    assert "approle" not in log
    # The concatenation is not reachable through the encoding either: `app` and
    # `role` transport as two records whose hex forms cannot merge into one.
    assert "approle".encode("utf-8").hex() not in completed.stderr
    assert "DROP SCHEMA" not in log


@pytest.mark.parametrize(
    "role",
    [
        "role-with-dash",
        "role with space",
        "bad; DROP TABLE characters",
        "role/with/slash",
        'quoted"role',
        "1leading_digit",
        "role$dollar",
        "x" * 64,
    ],
)
def test_a_role_name_that_is_not_a_plain_identifier_refuses_before_any_destruction(
    tmp_path, role
):
    """A single row is not enough: the name is interpolated into a `sed`
    replacement and into SQL, so it is validated before the schema is dropped."""
    completed, log = run_drill_against_stubs(tmp_path, [role])

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "is not a supported" in completed.stderr
    # The refusal says only what is true: step 1's dump has already been taken,
    # and nothing has been dropped or restored.
    assert "Nothing was dropped or restored" in completed.stderr
    assert "DROP SCHEMA" not in log
    assert "__APP_ROLE__" not in log
    assert "RECOVERY REQUIRED" not in completed.stderr


def test_the_cardinality_test_no_longer_reads_a_string_its_separator_was_deleted_from():
    """The defective construct is gone, asserted at the source.

    DS-R8-1 was not a missing check — the check was there and could never fire.
    A regression would most likely reintroduce exactly this shape, so the script
    is read rather than trusted.
    """
    source = DRILL.read_text(encoding="utf-8")
    # Comment lines are excluded: the script quotes the defective construct in
    # the comment that explains why it is gone, and that quotation is the point.
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )

    assert "detect_runtime_role | tr -d" not in code
    assert 'RUNTIME_ROLE="$(detect_runtime_role' not in code
    assert 'RUNTIME_ROLE_REPORT="$(detect_runtime_role)"' in code
    assert "${#RUNTIME_ROLE_ROWS[@]} > 1" in code

    # The refusal is textually before the destructive step, which is what makes
    # the ordering a property of the script rather than of one execution.
    #
    # Read over `code` rather than `source`: both phrases also occur in comments
    # -- the exit-code contract quotes the refusal, and step 3b's comment names
    # `DRILL_STAGE="destroy_attempted"` -- so an ordering asserted over the raw text
    # would be
    # ordering of prose. DS-R8-2's correction moved that prose, which is what
    # made the weakness visible.
    refusal = code.index("more than one non-owner role holds table grants")
    dropped = code.index('DRILL_STAGE="destroy_attempted"')
    destroy = code.index("DROP SCHEMA public CASCADE")
    assert refusal < dropped < destroy

    # And the dump precedes the refusal, which is the DS-R8-2 fact.
    assert code.index("pg_dump --format=custom") < refusal


# --------------------------------------------------------------------------
# DS-R8-2 (2026-09-06): the runtime-role refusal is in step 3b, which is after
# the dump. The script's exit-code list, the operations guide and the R8
# handback all said it happened "before touching anything" and that "nothing is
# dumped", which is true of gate 0a's refusal and not of this one.
#
# The correction is a documentation correction, so these tests are static or run
# through the same non-destructive stub boundary the DS-R8-1 regressions use.
# Nothing here contacts a database or runs the destructive drill.
# --------------------------------------------------------------------------


def _one_line(text: str) -> str:
    """Collapse a wrapped message to one whitespace-separated run.

    Every statement asserted below is line wrapped in the source it comes from —
    a shell `echo` sequence, a comment block, a Markdown paragraph — so matching
    it literally would assert the wrapping rather than the sentence.
    """
    return " ".join(text.split())


def test_the_runtime_role_refusal_leaves_the_dump_and_says_so(tmp_path):
    """What actually exists on disk when step 3b refuses, and what the refusal
    claims about it.

    The two must agree: DS-R8-2 is precisely a case where they did not.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test", "freedom_reporting"]
    )
    assert completed.returncode == 2, completed.stdout + completed.stderr

    work = tmp_path / "work"
    # Step 1's dump, step 2's checksum and the two read-only inventories have
    # all been written by the time step 3b decides.
    assert (work / "freedom_test.dump").is_file()
    assert (work / "freedom_test.dump.sha256").is_file()
    assert (work / "inventory-before.txt").is_file()
    assert (work / "grants-before.txt").is_file()
    # Step 3c has not run, so the schema-grants artifact does not exist.
    assert not (work / "schema-grants.sql").exists()

    # The refusal says both halves of the true statement. The messages are line
    # wrapped, so they are read as one run of whitespace-separated words.
    said = _one_line(completed.stderr)
    assert "Nothing was dropped or restored" in said
    assert "no recovery is required" in said
    assert str(work) in said
    # And it does not say the false one.
    assert "Nothing was dumped" not in said
    assert "RECOVERY REQUIRED" not in said

    # The database really is untouched: no destructive command was issued.
    assert "DROP SCHEMA" not in log
    assert "pg_restore" not in log


def test_the_malformed_role_refusal_makes_the_same_true_claim(tmp_path):
    """The other step-3b refusal, held to the same statement."""
    completed, log = run_drill_against_stubs(tmp_path, ["role-with-dash"])
    assert completed.returncode == 2, completed.stdout + completed.stderr

    work = tmp_path / "work"
    assert (work / "freedom_test.dump").is_file()
    said = _one_line(completed.stderr)
    assert "Nothing was dropped or restored" in said
    assert "no recovery is required" in said
    assert "Nothing was dumped" not in said
    assert "DROP SCHEMA" not in log


def test_gate_0a_still_refuses_before_the_work_directory_exists(tmp_path):
    """The contrast that makes DS-R8-2 a distinction rather than a correction of
    everything.

    The non-disposable-name refusal really does happen before anything is
    written, so the exit-code contract must keep saying so for *that* branch.
    """
    workdir = tmp_path / "work"
    completed = subprocess.run(
        [str(DRILL), "freedom_prod", str(workdir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 2
    assert not workdir.exists()


def test_the_exit_code_contract_no_longer_claims_nothing_was_touched(tmp_path):
    """The script's own header, read rather than trusted.

    A regression here is a documentation regression, and documentation is what
    DS-R8-2 was about, so it is asserted at the source.
    """
    source = DRILL.read_text(encoding="utf-8")
    header = _one_line(
        source[source.index("# Exit codes:") : source.index("set -euo pipefail")]
        .replace("#", " ")
        .replace("**", "")
    )

    # The withdrawn phrase survives only inside the sentence that withdraws it.
    assert 'to claim "before touching anything" for all of them' in header
    assert header.count("before touching anything") == 1
    assert "DS-R8-2" in header
    # Both facts, in the branch that needs them.
    assert "may already exist on disk" in header
    assert "no schema is dropped" in header
    assert "no recovery is required" in header
    # And gate 0a's genuinely-untouched claim is retained.
    assert "before the work directory is created" in header


def test_the_operations_guide_states_the_runtime_role_refusal_accurately():
    """`docs/operations/database-development.md` is the operator-facing half of
    the same contract, and it carried the same two false claims."""
    guide = (
        ROOT / "docs" / "operations" / "database-development.md"
    ).read_text(encoding="utf-8")

    section = guide[
        guide.index("#### The runtime role the restore has to put back") :
    ]
    section = _one_line(
        section[: section.index("#### The in-place drill is not failure-atomic")]
    ).replace("**", "").replace("*", "")

    # The false claim is gone as a claim. It survives only inside the sentence
    # that withdraws it, which is deliberate: a correction a reader cannot see
    # is a correction they will re-introduce.
    assert "so nothing is dumped" not in section
    assert 'and that "nothing is dumped"; that was true only of the' in section
    assert "it is withdrawn" in section

    assert "DS-R8-2" in section
    assert "may already exist in the work directory" in section
    assert "no schema is dropped and nothing is restored" in section
    assert "no recovery is required" in section


# --------------------------------------------------------------------------
# PR-20260907-2 (2026-09-07): the role guard changed the SQL identity it was
# guarding.
#
# The parser trimmed surrounding whitespace and accepted uppercase letters, then
# substituted the result into **unquoted** SQL. PostgreSQL preserves the case and
# the whitespace of a quoted role name in its catalog, so:
#
#   * a catalog role `MixedCase` became `mixedcase` the moment the rendered
#     `GRANT … TO MixedCase` reached the server — a different role, or none; and
#   * a catalog role ` padded_role ` became `padded_role` before SQL was built at
#     all, by the trim itself.
#
# Both passed the guard and reached `DROP SCHEMA`. On a stub they exit 0 because
# a stub does not parse SQL; on a real database the grant restoration fails after
# the destruction, or silently grants the wrong existing role.
#
# The corrected contract is identity-preserving: a name is accepted only when the
# unquoted spelling PostgreSQL will parse is byte-for-byte the catalog name, and
# only when it is not a keyword or special role whose literal meaning in SQL is
# something other than an identifier. Everything else refuses in step 3b, before
# the destroy, with no recovery banner.
# --------------------------------------------------------------------------

#: Names whose unquoted SQL spelling is not the catalog identity, or whose
#: literal meaning in SQL is not an identifier at all. Every one of these
#: reached `DROP SCHEMA` before this correction.
ROLE_NAMES_THAT_ARE_NOT_THEIR_OWN_SQL_IDENTITY = [
    # Case folding: PostgreSQL down-cases an unquoted identifier.
    "MixedCase",
    "FREEDOM_RUNTIME",
    "Freedom_Runtime_Test",
    # Surrounding whitespace: part of the catalog name, removed by the old trim.
    " padded_role ",
    "\tleading_tab",
    "trailing_space ",
    # A record that is entirely whitespace is a role named entirely whitespace.
    # It is not a zero-row result, and it must not be discarded as one.
    "   ",
    "\t",
    # Reserved key words: `GRANT … TO select` is a syntax error, not a grant.
    "select",
    "user",
    "table",
    "grant",
    "default",
    "current_user",
    "session_user",
    "current_role",
    # PUBLIC is the pseudo-role every role belongs to. Granting to it would give
    # the whole cluster the runtime role's rights.
    "public",
    # Reserved for the system; a drill must never re-grant one of these.
    "pg_read_all_data",
    "pg_monitor",
]


@pytest.mark.parametrize("role", ROLE_NAMES_THAT_ARE_NOT_THEIR_OWN_SQL_IDENTITY)
def test_a_role_whose_sql_identity_differs_refuses_before_any_destruction(
    tmp_path, role
):
    """**PR-20260907-2.** Refused in step 3b, before the destroy.

    The assertion is not merely `returncode == 2`: it is that the log carries no
    `DROP SCHEMA`, that no rendered grant reached a `psql`, and that the exit
    trap printed no recovery banner — because there is nothing to recover.
    """
    completed, log = run_drill_against_stubs(tmp_path, [role])

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "DROP SCHEMA" not in log
    assert "pg_restore" not in log
    assert "RECOVERY REQUIRED" not in completed.stderr
    assert "__APP_ROLE__" not in log
    # And the name is not silently repaired into something else on the way out.
    assert "Runtime role:" not in completed.stdout
    said = _one_line(completed.stderr)
    assert "is not a supported runtime role name" in said
    assert "Nothing was dropped or restored" in said
    assert "no recovery is required" in said


@pytest.mark.parametrize("role", ["MixedCase", " padded_role ", "   "])
def test_a_role_whose_sql_identity_differs_never_renders_a_grant(tmp_path, role):
    """The specific reproduction Codex recorded: the rendered `GRANT USAGE`.

    `GRANT USAGE ON SCHEMA public TO MixedCase;` and
    `GRANT USAGE ON SCHEMA public TO padded_role;` were both emitted. Neither
    names the role the catalog holds.
    """
    completed, log = run_drill_against_stubs(tmp_path, [role])

    assert completed.returncode == 2
    assert "GRANT USAGE ON SCHEMA public TO" not in log
    # Neither the catalog name nor the repaired one the old guard produced.
    if role.strip():
        assert role.strip() not in log
    assert role.strip().lower() not in log or not role.strip()


@pytest.mark.parametrize("role", ["freedom_runtime", "freedom_runtime_test"])
def test_the_two_supported_runtime_names_are_still_accepted(tmp_path, role):
    """The positive control. A guard that refused everything would pass every
    negative assertion above and would be useless."""
    completed, log = run_drill_against_stubs(tmp_path, [role])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert f"    Runtime role: {role}" in completed.stdout
    assert f"GRANT USAGE ON SCHEMA public TO {role};" in log
    assert "__APP_ROLE__" not in log
    assert "DROP SCHEMA public CASCADE" in log
    assert "Restore verified" in completed.stdout


def test_a_whitespace_only_record_is_not_treated_as_a_zero_row_result(tmp_path):
    """**PR-20260907-2 item 4.** The two are different answers to the question.

    A zero-row `psql -tA` result reaches the loop as one *empty* line. A role
    named `'   '` reaches it as one line of spaces. Counting the second as the
    first would take the "no runtime role holds table grants" path and restore
    nothing, silently, for a database that does have one.
    """
    completed, log = run_drill_against_stubs(tmp_path, ["   "])

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "No runtime role holds table grants here" not in completed.stdout
    assert "Skipped: no runtime role held grants" not in completed.stdout
    assert "DROP SCHEMA" not in log


def test_the_role_guard_no_longer_trims_the_name_it_is_guarding():
    """The defective construct is gone, asserted at the source.

    The trim ran *before* the syntax check, so the check never saw the catalog
    name. A regression would most likely reintroduce exactly this shape.
    """
    source = DRILL.read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )

    assert 'RUNTIME_ROLE="${RUNTIME_ROLE#' not in code
    assert 'RUNTIME_ROLE="${RUNTIME_ROLE%' not in code
    # The accepted shape is lower case only, so the unquoted spelling PostgreSQL
    # parses is the catalog name.
    assert "A-Za-z_][A-Za-z0-9_]" not in code
    assert "^[a-z_][a-z0-9_]{0,62}$" in code
    # And the refusal is still textually before the destructive step. The
    # phrase is matched on the one line that carries it: the message is wrapped
    # across several `echo`s, so a contiguous match would assert the wrapping.
    refusal = code.index("is not a supported")
    dropped = code.index('DRILL_STAGE="destroy_attempted"')
    assert refusal < dropped < code.index("DROP SCHEMA public CASCADE")


# --------------------------------------------------------------------------
# PR-20260907-1 (2026-09-07): the recovery path omitted the runtime table grants
# the normal path requires.
#
# `on_exit()` printed `pg_restore --no-privileges` followed by
# `psql -f schema-grants.sql`. That file carries schema ownership and the schema
# ACL and **nothing else** — no table grants. So an operator who followed the
# printed procedure exactly ended up with every row restored and the application
# role unable to read a single table: finding N-20 again, this time reached by
# doing what the script said.
#
# The correction renders the runtime grants into the work directory **before**
# the destroy, checksums them, applies that same file in step 5b, and names it in
# the recovery procedure together with a privilege verification step.
#
# These tests reach the banner through the stub boundary with a failing
# `pg_restore`. Nothing is dumped, dropped or restored: the `DROP SCHEMA` goes to
# a stub that records it.
# --------------------------------------------------------------------------


def _recovery_banner(stderr: str) -> str:
    return stderr[stderr.index("RECOVERY REQUIRED.") :]


def test_the_recovery_banner_includes_runtime_grants_and_verification_in_order(
    tmp_path,
):
    """**PR-20260907-1.** The emitted sequence, in the order it must be run.

    Asserted as an ordering over the banner's own text rather than as a set of
    words that appear somewhere in it: a procedure that verified privileges
    before restoring them would satisfy a membership test and would be wrong.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], restore_exit=42
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "DROP SCHEMA public CASCADE" in log, "the failure must be after the drop"
    banner = _recovery_banner(completed.stderr)
    work = tmp_path / "work"

    # Every artifact the procedure needs is named in the inventory above it.
    for name in (
        "freedom_test.dump.sha256",
        "schema-grants.sql.sha256",
        "runtime-grants.sql.sha256",
        "grants-inventory.sql",
        "grants-before.txt",
    ):
        assert name in banner, name

    # The ordering is asserted **within the procedure**, not over the whole
    # banner: the artifact inventory names the same files earlier, so an index
    # over the banner would order the list rather than the steps.
    procedure = banner[banner.index("Recovery procedure, in this order:") :]

    dump_check = procedure.index(f"sha256sum --check '{work}/freedom_test.dump.sha256'")
    schema_check = procedure.index(f"sha256sum --check '{work}/schema-grants.sql.sha256'")
    runtime_check = procedure.index(f"sha256sum --check '{work}/runtime-grants.sql.sha256'")
    restore = procedure.index("pg_restore --dbname=freedom_test")
    schema_apply = procedure.index(f"-f '{work}/schema-grants.sql'")
    runtime_apply = procedure.index(f"-f '{work}/runtime-grants.sql'")
    verify = procedure.index(f"-f '{work}/grants-inventory.sql'")
    compare = procedure.index(f"{work}/grants-before.txt")

    assert dump_check < restore
    assert schema_check < restore
    assert runtime_check < restore
    assert restore < schema_apply < runtime_apply < verify < compare
    assert "comm -23" in procedure
    # The verification is stated as a condition on completing recovery, not as a
    # suggestion after it.
    assert "Recovery is complete only when" in procedure


def test_the_recovery_banner_says_the_runtime_grants_are_mandatory(tmp_path):
    """A named file an operator may treat as optional is not a correction."""
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], restore_exit=42
    )
    banner = _one_line(_recovery_banner(completed.stderr))

    assert "runtime-grants.sql" in banner
    assert "N-20" in banner
    assert "unable to use its tables" in banner
    # Re-running the drill is not offered as a way to recover the lost state.
    assert "re-run this drill" not in banner
    assert "Re-running this drill is NOT a recovery step" in banner


def test_the_recovery_artifacts_exist_and_their_checksums_verify(tmp_path):
    """Everything the printed procedure names was written before the destroy and
    is on disk when the banner prints — including the rendered runtime grants,
    so the operator never reconstructs the role from an empty database."""
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], restore_exit=42
    )
    assert completed.returncode == 42

    work = tmp_path / "work"
    for name in (
        "freedom_test.dump",
        "freedom_test.dump.sha256",
        "schema-grants.sql",
        "schema-grants.sql.sha256",
        "runtime-grants.sql",
        "runtime-grants.sql.sha256",
        "grants-inventory.sql",
        "grants-before.txt",
    ):
        assert (work / name).is_file(), name
        # Named by absolute path in the banner, not merely mentioned.
        assert str(work / name) in completed.stderr, name

    rendered = (work / "runtime-grants.sql").read_text(encoding="utf-8")
    assert "__APP_ROLE__" not in rendered
    assert "GRANT USAGE ON SCHEMA public TO freedom_runtime_test;" in rendered

    for checksum in ("freedom_test.dump.sha256", "schema-grants.sql.sha256",
                     "runtime-grants.sql.sha256"):
        verified = subprocess.run(
            ["sha256sum", "--check", str(work / checksum)],
            cwd=work, capture_output=True, text=True,
        )
        assert verified.returncode == 0, verified.stdout + verified.stderr


def test_the_normal_path_applies_the_same_rendered_file_the_recovery_names(
    tmp_path,
):
    """One artifact, used by both paths, so they cannot diverge.

    The previous shape piped `sed` into `psql` in step 5b and named nothing in
    the banner, which is exactly how the two could disagree without anybody
    noticing.
    """
    completed, log = run_drill_against_stubs(tmp_path, ["freedom_runtime_test"])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    work = tmp_path / "work"
    assert (work / "runtime-grants.sql").is_file()
    assert f"-f {work / 'runtime-grants.sql'}" in log
    assert "Applied runtime-grants.sql for freedom_runtime_test" in completed.stdout


def test_the_zero_runtime_role_recovery_says_so_explicitly(tmp_path):
    """**PR-20260907-1 item 4.** The empty case is stated, not left silent.

    A banner that simply omitted the runtime step would be indistinguishable
    from one that forgot it.
    """
    completed, _ = run_drill_against_stubs(tmp_path, [], restore_exit=42)

    assert completed.returncode == 42
    banner = _one_line(_recovery_banner(completed.stderr))
    assert "No runtime role held table grants before the destroy" in banner
    assert "no runtime-grants.sql" in banner
    assert "runtime-grants.sql.sha256" not in banner
    assert not (tmp_path / "work" / "runtime-grants.sql").exists()
    # The schema grants are still required in this case.
    assert "schema-grants.sql" in banner


def test_a_missing_grant_template_refuses_before_the_destroy(tmp_path):
    """The template is read in step 3c now, not in step 5b.

    Discovering it is missing *after* the schema is dropped leaves a database
    that cannot be fully recovered from the artifacts the drill kept.
    """
    source = DRILL.read_text(encoding="utf-8")
    moved = tmp_path / "drill-without-template.sh"
    # Point GRANT_TEMPLATE at a path that does not exist, without touching the
    # repository's own file.
    moved.write_text(
        source.replace(
            'GRANT_TEMPLATE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)'
            '/runtime-grants.sql.tmpl"',
            f'GRANT_TEMPLATE="{tmp_path}/absent-template.sql.tmpl"',
            1,
        ),
        encoding="utf-8",
    )
    moved.chmod(0o755)

    stub_bin = tmp_path / "stub-bin"
    stub_bin.mkdir()
    log = tmp_path / "invocations.log"
    log.write_text("", encoding="utf-8")
    grantee_file = tmp_path / "grantees.txt"
    grantee_file.write_text(
        encoded_role_report(["freedom_runtime_test"]), encoding="utf-8"
    )
    for name, body in (("psql", STUB_PSQL), ("pg_dump", STUB_PG_DUMP),
                       ("pg_restore", STUB_PG_RESTORE)):
        for placeholder, value in (
            ("__LOG__", str(log)),
            ("__GRANTEES__", str(grantee_file)),
            ("__STATE__", str(tmp_path / "stub-state")),
            ("__DATABASE__", "freedom_test"),
            ("__RESTORE_EXIT__", "0"),
            ("__REPORT_EXIT__", "0"),
            ("__DESTROY_EXIT__", "0"),
            ("__DESTROY_APPLIED__", "1"),
            ("__DESTROY_COMPLETED__", "1"),
            ("__RESTORE_APPLIED__", "1"),
            ("__RESTORE_COMPLETED__", "1"),
            ("__SCHEMA_GRANTS_EXIT__", "0"),
            ("__RUNTIME_GRANTS_EXIT__", "0"),
            ("__INVENTORY_MISMATCH__", "0"),
            ("__PRIVILEGE_LOSS__", "0"),
        ):
            body = body.replace(placeholder, value)
        executable = stub_bin / name
        executable.write_text(body, encoding="utf-8")
        executable.chmod(0o755)

    child = {k: v for k, v in os.environ.items() if k not in LIBPQ_VARIABLES}
    child["PATH"] = f"{stub_bin}{os.pathsep}{os.environ.get('PATH', '')}"
    completed = subprocess.run(
        [str(moved), "freedom_test", str(tmp_path / "work")],
        cwd=ROOT, capture_output=True, text=True, env=child,
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "runtime grant template" in completed.stderr
    assert "DROP SCHEMA" not in log.read_text(encoding="utf-8")
    assert "RECOVERY REQUIRED" not in completed.stderr


# --------------------------------------------------------------------------
# PR-20260907-R2-1 (2026-09-08): a newline-bearing role identity was still
# changed, or lost, before the guard saw it.
#
# PR-20260907-2 stopped the guard from *repairing* a name. It did not stop the
# **transport** from doing so. `RUNTIME_ROLE_REPORT="$(detect_runtime_role)"`
# strips trailing newlines, and the line reader below it treats a newline as a
# record boundary and drops empty lines — while a quoted PostgreSQL role name may
# itself contain newlines. Reproduced against the pre-fix script through the stub
# boundary, one catalog role at a time:
#
#     "freedom_runtime_test"     exit 0  DROP reached  correct positive control
#     "MixedCase"                exit 2  no DROP       existing refusal preserved
#     "freedom_runtime_test\n"   exit 0  DROP reached  grant names the WRONG role
#     "\nfreedom_runtime_test"   exit 0  DROP reached  grant names the WRONG role
#     "\n"                       exit 0  DROP reached  mistaken for zero roles
#     "freedom_runtime" + "\n"   exit 0  DROP reached  two records read as one
#
# No further pattern applied after the split can recover a boundary that has
# already been deleted, so the **transport** is changed: the query emits one
# `ROLE <hex>` record per role and one `END <count>` terminator, the shell decodes
# the hex back to the exact catalog bytes, and the existing supported-role
# contract is applied to those bytes. The contract itself is unchanged and
# nothing about it is widened — a quoted name is still refused, it is simply
# refused for what it actually is.
# --------------------------------------------------------------------------

#: Role names carrying a record separator inside the identity. Every one of these
#: either became a *different* supported name or vanished as a record before this
#: correction.
NEWLINE_BEARING_ROLE_NAMES = [
    # Codex's three, exactly.
    "freedom_runtime_test\n",
    "\nfreedom_runtime_test",
    "\n",
    # A newline inside the name rather than at an edge.
    "freedom\nruntime",
    # Multiple line breaks, which the reader turned into several records.
    "a\n\nb",
    "\n\n",
    # A carriage return is a separator to some readers and not to others; it is
    # part of the name to PostgreSQL either way.
    "freedom_runtime\r",
    # Newline beside the whitespace PR-20260907-2 already refuses.
    "freedom_runtime_test\n ",
]


@pytest.mark.parametrize("role", NEWLINE_BEARING_ROLE_NAMES)
def test_a_newline_bearing_role_refuses_before_any_destruction(tmp_path, role):
    """**PR-20260907-R2-1.** The identity survives the transport, and is refused.

    The assertion is not merely `returncode == 2`: it is that the record was
    neither changed into a supported name nor dropped, that the log carries no
    `DROP SCHEMA`, and that the exit trap printed no recovery banner — because
    there is nothing to recover.
    """
    completed, log = run_drill_against_stubs(tmp_path, [role])

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "DROP SCHEMA" not in log
    assert "pg_restore" not in log
    assert "RECOVERY REQUIRED" not in completed.stderr
    assert "__APP_ROLE__" not in log
    # Not repaired into a supported name on the way out, and no grant rendered.
    assert "Runtime role:" not in completed.stdout
    assert "GRANT USAGE ON SCHEMA public TO" not in log
    assert not (tmp_path / "work" / "runtime-grants.sql").exists()


@pytest.mark.parametrize("role", ["freedom_runtime_test\n", "\nfreedom_runtime_test"])
def test_a_newline_bearing_role_is_not_repaired_into_a_supported_one(tmp_path, role):
    """The specific harm: the *supported* name the transport used to produce.

    `freedom_runtime_test\\n` is not `freedom_runtime_test`. It is a different
    role, and the pre-fix script granted to the second while the catalog held the
    first — which on a real database grants an existing unrelated role, or fails
    after the destroy.
    """
    completed, log = run_drill_against_stubs(tmp_path, [role])

    assert completed.returncode == 2
    assert "freedom_runtime_test" not in completed.stdout
    assert "GRANT USAGE ON SCHEMA public TO freedom_runtime_test;" not in log


def test_a_newline_only_role_is_a_record_not_a_zero_row_result(tmp_path):
    """**The row that made the drill silently wrong.** A role named `"\\n"` is a
    record. Read as zero rows, the drill restored no table grants at all and
    exited 0 — finding N-20 reached through a parsing defect.
    """
    completed, log = run_drill_against_stubs(tmp_path, ["\n"])

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "No runtime role holds table grants here" not in completed.stdout
    assert "Skipped: no runtime role held grants" not in completed.stdout
    assert "DROP SCHEMA" not in log


@pytest.mark.parametrize(
    "grantees",
    [
        # A supported name beside an unsupported newline-bearing one.
        ["freedom_runtime", "freedom_runtime_test\n"],
        # The case the pre-fix reader collapsed to a single accepted record: the
        # second role vanished and the drill granted only the first.
        ["freedom_runtime", "\n"],
        ["\n", "freedom_runtime"],
    ],
)
def test_a_valid_role_beside_a_newline_bearing_one_is_still_two_records(
    tmp_path, grantees
):
    """Cardinality survives too, which is the other half of the finding.

    `["freedom_runtime", "\\n"]` reached the pre-fix reader as one record, so the
    drill accepted `freedom_runtime`, dropped the schema and restored grants for
    one of two roles.
    """
    completed, log = run_drill_against_stubs(tmp_path, grantees)

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "more than one non-owner role holds table grants" in completed.stderr
    assert "Roles found: 2, hex encoded:" in completed.stderr
    assert "DROP SCHEMA" not in log
    assert "Runtime role:" not in completed.stdout


@pytest.mark.parametrize("role", ["freedom_runtime", "freedom_runtime_test"])
def test_the_supported_names_still_pass_through_the_new_transport(tmp_path, role):
    """**The positive control for the whole transport.**

    A decoder that refused everything would satisfy every negative assertion
    above. These two decode back to exactly the catalog bytes, satisfy the
    unchanged contract, reach step 5b and render the grant.
    """
    completed, log = run_drill_against_stubs(tmp_path, [role])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert f"    Runtime role: {role}" in completed.stdout
    assert f"GRANT USAGE ON SCHEMA public TO {role};" in log
    assert "DROP SCHEMA public CASCADE" in log
    assert "Restore verified" in completed.stdout


def test_zero_records_are_still_the_documented_empty_path(tmp_path):
    """The other positive control: `END 0` is a real answer, not a failure."""
    completed, log = run_drill_against_stubs(tmp_path, [])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "No runtime role holds table grants here" in completed.stdout
    assert "DROP SCHEMA public CASCADE" in log


#: Reports that are not the transport contract. Each must refuse, and none may be
#: read as "no runtime role holds table grants" (PR-20260907-R2-1 item 3).
MALFORMED_ROLE_REPORTS = [
    # Nothing at all: a client that printed nothing, or was cut off before it
    # printed anything. This is the one that used to look exactly like zero rows.
    ("", "no terminator"),
    # Truncated after the records.
    ("ROLE 66726565646f6d5f72756e74696d65\n", "no terminator"),
    # Terminator without a count.
    ("END\n", "neither a record nor the terminator"),
    ("END x\n", "no record count"),
    # The count and the records disagree, in both directions.
    ("END 1\n", "fewer or more records"),
    ("ROLE 6672\nROLE 6673\nEND 1\n", "fewer or more records"),
    # A record after the terminator.
    ("END 1\nROLE 6672\n", "followed the terminator"),
    # Not hexadecimal, and not even-length hexadecimal.
    ("ROLE zz\nEND 1\n", "not hex encoded"),
    ("ROLE 667\nEND 1\n", "not hex encoded"),
    ("ROLE 66 72\nEND 1\n", "not hex encoded"),
    # Upper-case hex is outside the contract: one spelling, decoded one way.
    ("ROLE 6672EE\nEND 1\n", "not hex encoded"),
    # The pre-fix transport itself — a bare role name per line. A corrected
    # script must not accept the shape it was corrected away from.
    ("freedom_runtime\n", "neither a record nor the terminator"),
    # A hostile line that would otherwise be pasted into an operator's terminal.
    ("\x1b]0;pwned\x07ROLE 6672\nEND 1\n", "neither a record nor the terminator"),
]


@pytest.mark.parametrize("report, reason", MALFORMED_ROLE_REPORTS)
def test_an_unreadable_role_report_refuses_and_is_never_read_as_zero_roles(
    tmp_path, report, reason
):
    """**PR-20260907-R2-1 item 3.** Unreadable is a refusal, not an empty result.

    Inferring "no runtime role" from a report that could not be read is finding
    N-20 with an extra step: the drill would destroy the schema, restore no table
    grants and exit 0.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, [], report_override=report
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    said = _one_line(completed.stderr)
    assert "the runtime-role report could not be read" in said
    assert reason in said
    assert "DROP SCHEMA" not in log
    assert "pg_restore" not in log
    assert "RECOVERY REQUIRED" not in completed.stderr
    # Never taken as the empty path.
    assert "No runtime role holds table grants here" not in completed.stdout
    assert "Skipped: no runtime role held grants" not in completed.stdout


def test_an_unreadable_role_report_does_not_echo_its_contents(tmp_path):
    """The failure text is fixed, and carries no catalog bytes.

    A report that cannot be read is exactly the case in which its bytes cannot be
    assumed to be a role name, valid UTF-8, or free of terminal escapes.
    """
    hostile = "\x1b]0;pwned\x07ROLE 6672\npassword=hunter2\nEND 1\n"
    completed, _ = run_drill_against_stubs(tmp_path, [], report_override=hostile)

    assert completed.returncode == 2
    for fragment in ("pwned", "hunter2", "password", "\x1b"):
        assert fragment not in completed.stderr, fragment
        assert fragment not in completed.stdout, fragment


def test_a_failing_role_query_refuses_rather_than_inferring_zero_roles(tmp_path):
    """A client failure is a refusal with a stated reason, not an empty result."""
    completed, log = run_drill_against_stubs(tmp_path, [], report_exit=3)

    assert completed.returncode == 2, completed.stdout + completed.stderr
    said = _one_line(completed.stderr)
    assert "the runtime-role report could not be read" in said
    assert "the query did not complete" in said
    assert "DROP SCHEMA" not in log
    assert "No runtime role holds table grants here" not in completed.stdout


def test_the_role_transport_no_longer_splits_on_a_character_a_name_may_contain():
    """The defective construct is gone, asserted at the source.

    The regression this guards against is not a missing check — the check exists
    and is unchanged. It is a *reader* that deletes the boundary before the check
    runs, and it would be reintroduced in exactly this shape.
    """
    source = DRILL.read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )

    # The report is transported in an encoding that cannot contain a separator.
    assert "encode(convert_to(role_name, 'UTF8'), 'hex')" in code
    assert "decode_hex_role" in code
    # The old shape read the raw catalog name as the record.
    assert 'RUNTIME_ROLE_ROWS+=("${role_row}")' not in code
    assert 'RUNTIME_ROLE_ROWS+=("${DECODED_ROLE}")' in code
    # Cardinality is checked against a count the server declared, not inferred
    # from how many lines survived.
    assert "RUNTIME_ROLE_DECLARED_TOTAL" in code
    assert "refuse_runtime_report" in code
    # And the guard still runs on the decoded bytes, before the destroy.
    guard = code.index("is not a supported")
    assert code.index('RUNTIME_ROLE="${RUNTIME_ROLE_ROWS[0]}"') < guard
    assert guard < code.index('DRILL_STAGE="destroy_attempted"')


def test_the_supported_role_contract_itself_is_unchanged():
    """The transport was corrected; the contract was not widened.

    PR-20260907-R2-1 item 2: a quoted name must still refuse. It refuses because
    of what it is, not because the reader mangled it into something else.
    """
    source = DRILL.read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )

    assert "^[a-z_][a-z0-9_]{0,62}$" in code
    assert '"${RUNTIME_ROLE}" != "${RUNTIME_ROLE,,}"' in code
    assert "is_reserved_role_spelling" in code
    for spelling in ("select", "public", "current_user", "session_user", "pg_*"):
        assert spelling in code, spelling


# --------------------------------------------------------------------------
# PR-20260908-R3-2 (2026-09-08): hex decoding dropped NUL bytes.
#
# The `ROLE <hex>` / `END <count>` transport survives newlines, which is what
# PR-20260907-R2-1 corrected. It did not survive a NUL. `decode_hex_role`
# accumulates bytes with `printf -v piece '%b'` into a Bash string, and **a Bash
# string cannot hold a NUL** — so an encoded `00` was not decoded into a byte the
# supported-name guard could refuse, it disappeared, and a shorter, different
# name arrived at the guard already looking supported.
#
# Codex supplied this report through `report_override`:
#
#     ROLE 66726565646f6d5f72756e74696d655f7465737400
#     END 1
#
# `freedom_runtime_test` followed by NUL. The drill exited 0 and reached both
# `DROP SCHEMA` and `pg_restore` in the stub log, and rendered a grant naming
# `freedom_runtime_test`. The valid control also exited 0, and the
# newline-bearing control correctly refused with exit 2 before `DROP`.
#
# PostgreSQL cannot store a NUL in a `name`, so this is **malformed transport**
# rather than a claim about a legitimate catalog role — and R2 already requires
# malformed transport to refuse rather than be repaired into an identity. The
# check therefore refuses the report, before the decode, and does so by walking
# whole byte pairs: a raw substring search for `00` would misclassify a sequence
# that spans a pair boundary.
#
# **These are stub reproductions.** They establish transport handling and
# pre-destruction behaviour and nothing about SQL semantics, and no PostgreSQL
# regression is added for this finding: a role name containing a NUL is not a
# thing PostgreSQL can be asked to create.
# --------------------------------------------------------------------------

#: `freedom_runtime_test`, hex encoded. The supported name every case below is
#: built around, so a decoder that dropped the NUL would produce exactly it.
SUPPORTED_HEX = "freedom_runtime_test".encode("utf-8").hex()

#: Encoded records carrying a NUL somewhere in the name.
NUL_BEARING_RECORDS = [
    # Codex's exact report: the supported name followed by NUL.
    pytest.param(f"{SUPPORTED_HEX}00", id="trailing"),
    pytest.param(f"00{SUPPORTED_HEX}", id="leading"),
    pytest.param(
        "freedom".encode("utf-8").hex() + "00" + "runtime".encode("utf-8").hex(),
        id="embedded",
    ),
    # Repeated, adjacent and separated.
    pytest.param(f"{SUPPORTED_HEX}0000", id="repeated-adjacent"),
    pytest.param(f"00{SUPPORTED_HEX}00", id="repeated-at-both-ends"),
    pytest.param(
        "00" + "freedom".encode("utf-8").hex() + "00" + "runtime".encode("utf-8").hex() + "00",
        id="repeated-throughout",
    ),
    # A record that is nothing but NUL. Decoded, it would have been the empty
    # string — indistinguishable from a name that is not there at all.
    pytest.param("00", id="nul-only"),
    pytest.param("0000", id="nul-only-repeated"),
]


@pytest.mark.parametrize("record", NUL_BEARING_RECORDS)
def test_a_nul_bearing_record_refuses_before_any_destruction(tmp_path, record):
    """**PR-20260908-R3-2.** The impossible record refuses; it is not decoded.

    The assertion is not merely `returncode == 2`: it is that no `DROP SCHEMA`
    and no `pg_restore` were issued, that no runtime grant was rendered, and that
    the exit trap printed no recovery banner — because nothing was destroyed.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, [], report_override=f"ROLE {record}\nEND 1\n"
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    said = _one_line(completed.stderr)
    assert "the runtime-role report could not be read" in said
    assert "a role record carried a NUL byte" in said
    assert "DROP SCHEMA" not in log
    assert "pg_restore" not in log
    assert "RECOVERY REQUIRED" not in completed.stderr
    assert "__APP_ROLE__" not in log
    assert "GRANT USAGE ON SCHEMA public TO" not in log
    assert not (tmp_path / "work" / "runtime-grants.sql").exists()


@pytest.mark.parametrize(
    "record",
    [f"{SUPPORTED_HEX}00", f"00{SUPPORTED_HEX}", f"00{SUPPORTED_HEX}00"],
    ids=["trailing", "leading", "both-ends"],
)
def test_a_nul_bearing_record_is_not_repaired_into_a_supported_one(tmp_path, record):
    """**The specific harm.** `freedom_runtime_test\\0` is not
    `freedom_runtime_test`.

    Before this correction the NUL was dropped during decoding and the remainder
    was the supported name, so the guard approved it, the schema was dropped and
    the grant named a role the catalog does not hold.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, [], report_override=f"ROLE {record}\nEND 1\n"
    )

    assert completed.returncode == 2
    assert "Runtime role:" not in completed.stdout
    assert "freedom_runtime_test" not in completed.stdout
    assert "GRANT USAGE ON SCHEMA public TO freedom_runtime_test;" not in log
    # And the refusal carries no catalog bytes of its own.
    assert "freedom_runtime_test" not in completed.stderr


@pytest.mark.parametrize("record", [f"{SUPPORTED_HEX}00", "00"])
def test_a_nul_bearing_record_is_never_read_as_zero_roles(tmp_path, record):
    """Unreadable is a refusal, not an empty result — for this record too.

    `ROLE 00` is the dangerous one: decoded, it was the empty string, which is
    what a zero-row result also looks like. Taking it as "no runtime role" would
    destroy the schema and restore no table grants at all, which is N-20.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, [], report_override=f"ROLE {record}\nEND 1\n"
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    assert "No runtime role holds table grants here" not in completed.stdout
    assert "Skipped: no runtime role held grants" not in completed.stdout
    assert "DROP SCHEMA" not in log


@pytest.mark.parametrize(
    "report",
    [
        pytest.param(
            f"ROLE {'freedom_runtime'.encode('utf-8').hex()}\n"
            f"ROLE {SUPPORTED_HEX}00\nEND 2\n",
            id="valid-then-nul",
        ),
        pytest.param(
            f"ROLE {SUPPORTED_HEX}00\n"
            f"ROLE {'freedom_runtime'.encode('utf-8').hex()}\nEND 2\n",
            id="nul-then-valid",
        ),
    ],
)
def test_a_valid_record_beside_a_nul_bearing_one_still_refuses(tmp_path, report):
    """A malformed record is not rescued by a well-formed neighbour.

    The whole report is refused, in either order, and the valid name is not
    adopted as "the one runtime role" — which is what a reader that skipped the
    record it could not decode would have done.
    """
    completed, log = run_drill_against_stubs(tmp_path, [], report_override=report)

    assert completed.returncode == 2, completed.stdout + completed.stderr
    said = _one_line(completed.stderr)
    assert "a role record carried a NUL byte" in said
    assert "Runtime role:" not in completed.stdout
    assert "GRANT USAGE ON SCHEMA public TO" not in log
    assert "DROP SCHEMA" not in log


#: **The byte-boundary control.** Each record's *text* contains `00`, and none of
#: its *bytes* is NUL. A detector implemented as a substring search over the
#: record would refuse all three as NUL-bearing; the pair scan must not.
#:
#: None of them is a supported role name — no lower-case ASCII name can carry a
#: boundary-crossing `00`, because that needs a byte ending in `0` followed by a
#: control byte — so what distinguishes the two implementations is **which
#: refusal** is emitted, and that is what these assert.
BOUNDARY_CROSSING_RECORDS = [
    # 0x40 '@', 0x04 control.
    pytest.param("4004", id="at-sign-then-control"),
    # 0x70 'p', 0x0a newline.
    pytest.param("700a", id="p-then-newline"),
    # 0x30 '0', 0x01 control, inside a longer record.
    pytest.param(f"{SUPPORTED_HEX}3001", id="digit-zero-then-control"),
]


@pytest.mark.parametrize("record", BOUNDARY_CROSSING_RECORDS)
def test_a_boundary_crossing_zero_pair_is_not_mistaken_for_a_nul(tmp_path, record):
    """**PR-20260908-R3-2 item 1.** Whole byte pairs, not a substring search.

    `4004` is `@` then `\\x04`. Its text contains `00` spanning the boundary
    between the two bytes, and it carries no NUL at all. The record is still
    refused — it is not a supported runtime role name — but it must be refused
    for **that** reason, at the role guard, rather than misclassified as
    malformed transport.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, [], report_override=f"ROLE {record}\nEND 1\n"
    )

    assert completed.returncode == 2, completed.stdout + completed.stderr
    said = _one_line(completed.stderr)
    assert "a role record carried a NUL byte" not in said
    assert "the runtime-role report could not be read" not in said
    assert "is not a supported runtime role name" in said
    # Still before any destruction, and still with nothing to recover.
    assert "DROP SCHEMA" not in log
    assert "pg_restore" not in log
    assert "RECOVERY REQUIRED" not in completed.stderr


@pytest.mark.parametrize("role", ["freedom_runtime", "freedom_runtime_test"])
def test_the_supported_names_are_unaffected_by_the_nul_check(tmp_path, role):
    """**The positive control.** A scan that refused everything would satisfy
    every negative assertion above.

    Neither supported name encodes a `00` pair, and neither is changed by the
    check being added: both still decode to the catalog bytes, reach step 5b and
    render their grant.
    """
    assert "00" not in role.encode("utf-8").hex(), role

    completed, log = run_drill_against_stubs(tmp_path, [role])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert f"    Runtime role: {role}" in completed.stdout
    assert f"GRANT USAGE ON SCHEMA public TO {role};" in log
    assert "DROP SCHEMA public CASCADE" in log
    assert "Restore verified" in completed.stdout


def test_zero_roles_are_unaffected_by_the_nul_check(tmp_path):
    """The other positive control: `END 0` is still an answer, not a refusal."""
    completed, log = run_drill_against_stubs(tmp_path, [])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "No runtime role holds table grants here" in completed.stdout
    assert "DROP SCHEMA public CASCADE" in log


def test_the_nul_check_runs_before_the_decode_that_would_lose_it():
    """**PR-20260908-R3-2 item 1**, asserted at the source.

    Ordering is the whole correction. A NUL inspected *after* `decode_hex_role`
    would be inspected in a representation that no longer contains it, so a check
    placed there could never fire — the DS-R8-1 shape, in which the check exists
    and is unreachable.
    """
    source = DRILL.read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )

    assert "hex_record_contains_nul" in code
    guard = code.index('if hex_record_contains_nul "${role_hex}"; then')
    decode = code.index('decode_hex_role "${role_hex}"')
    assert guard < decode, "the NUL check must precede the decode"

    # The scan steps two characters at a time rather than searching the record.
    scan = code[code.index("hex_record_contains_nul() {") :]
    scan = scan[: scan.index("\n}\n")]
    assert '"${hex:0:2}" == "00"' in scan
    assert 'hex="${hex:2}"' in scan

    # And it is still refused before the destroy.
    assert guard < code.index('DRILL_STAGE="destroy')


# --------------------------------------------------------------------------
# PR-20260907-R2-2 (2026-09-08): the recovery restarted a restore that had
# already completed.
#
# `on_exit()` printed the same full `pg_restore --single-transaction
# --exit-on-error` for every failure while one "the schema was dropped" flag was
# set, and that flag stayed set through the schema grants, the runtime grants and
# both verifications. A failure in any of those happens **after** the data
# restore has committed, so repeating the printed restore fails on the objects
# that are already there instead of reaching the grant repair the operator needs.
#
# `DRILL_STAGE` now records the last step that *succeeded*, and each stage emits
# its own resume point. The stub boundary is stateful so each of them can be
# reached without a database.
# --------------------------------------------------------------------------


def _procedure(stderr: str) -> str:
    """The emitted recovery procedure, without the artifact inventory above it.

    The inventory names the same files, so an index over the whole banner would
    order the list rather than the steps.
    """
    banner = _recovery_banner(stderr)
    return banner[banner.index("Recovery procedure, in this order:") :]


#: Every stage that can print a banner, the injection that reaches it, and the
#: exit status the drill ends with there. `destroy_attempted` was added by
#: PR-20260908-R3-1; it is the earliest of them, and the only one where the drill
#: does not know whether it destroyed anything.
STAGE_INJECTIONS = [
    ("destroy_attempted", {"destroy_exit": 42, "destroy_applied": False}, 42),
    ("restore_attempted", {"restore_exit": 42}, 42),
    ("restored", {"schema_grants_exit": 42}, 42),
    ("schema_grants_applied", {"runtime_grants_exit": 42}, 42),
    ("grants_applied", {"privilege_loss": True}, 1),
]

#: The stages whose banner must still print the data restore, because at neither
#: of them is a committed restore established. Every other stage must not.
STAGES_THAT_MAY_PRINT_A_RESTORE = frozenset(
    {"destroy_attempted", "restore_attempted"}
)


# --------------------------------------------------------------------------
# PR-20260908-R3-1 (2026-09-08): a failed DROP was reported as a known empty
# database.
#
# `DRILL_STAGE="destroyed"` was assigned *before* the destructive command, on the
# reasoning that a failure inside the destroy leaves an unknown state. But the
# `destroyed` banner does not describe an unknown state. It asserts that the
# schema was dropped, that the database is EMPTY, and it prescribes a full
# restore. A command that was refused, that never ran, or whose result was lost
# establishes none of those things.
#
# Codex modified the stub's DROP branch to emit a fixed error and exit 42 without
# changing its state file. The drill exited 42, never called `pg_restore`, and
# printed `database is EMPTY` followed by `4. pg_restore ...`.
#
# The correction splits the two claims. `destroy_attempted` is set before the
# command and means "this drill may have destroyed something"; `destroyed` is set
# after it succeeds and means "the schema is dropped, recreated and empty". The
# `destroy_attempted` banner prescribes **no mutation at all** until a read-only
# step 0 has established which of four states the schema is actually in.
#
# The stub boundary models both failing outcomes behind one exit status, because
# that is precisely what the drill cannot distinguish from the outside.
# --------------------------------------------------------------------------

#: Codex's reproduction, and its twin. The exit status is identical and the
#: database is not, which is the whole reason the drill must not guess.
DESTROY_FAILURES = [
    pytest.param(
        {"destroy_exit": 42, "destroy_applied": False},
        id="refused-schema-intact",
    ),
    pytest.param(
        {"destroy_exit": 42, "destroy_applied": True},
        id="applied-then-lost-result",
    ),
]


@pytest.mark.parametrize("injection", DESTROY_FAILURES)
def test_a_failed_destroy_is_never_described_as_a_known_empty_database(
    tmp_path, injection
):
    """**PR-20260908-R3-1, the finding itself.**

    The drill must not claim the database is empty, and must not prescribe a
    restore, on the strength of a command that did not report success. Both
    injections produce the same exit status and the same banner — the difference
    between them is what step 0 is for.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    # The destroy really was reached, so this is the stage under test and not an
    # earlier refusal.
    assert "DROP SCHEMA public CASCADE" in log
    assert "pg_restore" not in log, "the drill stopped at the destroy"

    banner = _recovery_banner(completed.stderr)
    said = _one_line(banner)
    # The claim the pre-fix banner made.
    assert "so the database is EMPTY" not in said
    assert "the database is EMPTY" not in said
    # And the claim it makes now.
    assert "WHAT THE SCHEMA NOW HOLDS IS NOT KNOWN" in said
    assert "This drill does not call the database empty here" in said
    assert "the schema may be exactly as it was" in said


@pytest.mark.parametrize("injection", DESTROY_FAILURES)
def test_a_failed_destroy_prescribes_no_mutation_before_the_state_is_known(
    tmp_path, injection
):
    """**Item 3.** Nothing is changed until step 0 has answered.

    Asserted as an ordering over the emitted procedure: every mutation step —
    the restore, both grant applications — comes after the read-only reports, and
    step 0 itself is a `diff` of two queries and nothing else. Since
    PR-20260908-R5-1 the completion question comes before even those, so the
    ordering starts at 0a.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )
    procedure = _procedure(completed.stderr)
    work = tmp_path / "work"

    state_report = procedure.index(f"-f '{work}/schema-state.sql'")
    inventory_report = procedure.index(f"-f '{work}/inventory-query.sql'")
    restore = procedure.index("pg_restore --dbname=freedom_test")
    schema_apply = procedure.index(f"-f '{work}/schema-grants.sql'")
    runtime_apply = procedure.index(f"-f '{work}/runtime-grants.sql'")

    assert state_report < restore
    assert inventory_report < restore
    assert restore < schema_apply < runtime_apply
    # Step 0 is where the reports are, and it is step 0. Its first question is
    # whether the transaction that made the state uncertain has ended, and that
    # is asked before the reports it would otherwise be read from.
    assert procedure.index("0. Establish two things before choosing anything") < (
        procedure.index("0a. HAS THE DESTROY'S SERVER-SIDE TRANSACTION ENDED?")
    )
    assert procedure.index("0a. HAS THE DESTROY'S SERVER-SIDE TRANSACTION ENDED?") < (
        state_report
    )


@pytest.mark.parametrize("injection", DESTROY_FAILURES)
def test_the_failed_destroy_banner_accounts_for_every_schema_state(
    tmp_path, injection
):
    """**Item 2**, as corrected by the R4 continuation of this finding.

    Five outcomes and a failed-query non-answer: the destroy did not take
    effect, the schema was dropped and recreated, the schema is absent, the
    counts cannot resolve it, and anything else. Each says what the operator may
    do, and the three that this procedure cannot resolve stop instead of
    choosing a mutation.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )
    procedure = _one_line(_procedure(completed.stderr))

    # What the reports are, before any outcome is read.
    assert "WHAT THESE REPORTS OBSERVE, AND WHAT THEY DO NOT" in procedure
    assert "equal counts are not an object-identity inventory" in procedure
    assert (
        "NOT an exhaustive enumeration of everything PostgreSQL can place in a schema"
        in procedure
    )
    # 1. The destroy did not take effect -- keyed on objects still being counted,
    #    not on two reports merely matching.
    assert "SOME COUNT IS NON-ZERO AND THE WHOLE STATE REPORT MATCHES" in procedure
    assert "THE DESTROY DID NOT TAKE EFFECT" in procedure
    assert "A dropped and recreated 'public' holds nothing at all" in procedure
    assert "NO DATA RESTORE IS REQUIRED and none may be run" in procedure
    # 2. Dropped and recreated -- the `destroyed` state, reached by continuing.
    assert "EVERY COUNT IS ZERO AND" in procedure
    assert "RECORDED AT LEAST ONE OBJECT IN ANY CLASS" in procedure
    assert "That is the 'destroyed' state. Continue at step 1." in procedure
    # 3. Absent.
    assert "schema_present=false: the schema is ABSENT" in procedure
    assert (
        "recreating one is a deliberate change this procedure does not make for you"
        in procedure
    )
    # 4. Unresolved: every count zero on both sides. The claim the R3 banner made
    #    here -- that the database held no objects and there was nothing to lose
    #    -- is gone, and is asserted to be gone.
    assert "RECORDED ZERO IN EVERY CLASS: THESE REPORTS CANNOT RESOLVE" in procedure
    assert "neither report establishes that the schema held nothing" in procedure
    assert "THIS IS NOT 'THERE WAS NOTHING TO LOSE'" in procedure
    assert "Stop here and resolve it with an operator" in procedure
    # 5. Unexpected.
    assert "the schema is in an UNEXPECTED state" in procedure
    assert "this procedure does not choose between them" in procedure
    # The non-answer: a query that failed is not evidence of emptiness.
    assert "EITHER COMMAND FAILED: the state is still not known" in procedure
    assert "is not evidence that the schema is empty" in procedure
    # The identity inventory the operator is pointed at where counts cannot decide.
    assert "pg_restore --list" in procedure

    # 6. PR-20260908-R5-1: every one of those outcomes is provisional until the
    #    destroy's transaction is known to have ended, and the two that direct an
    #    action say so on the line that directs it.
    assert "HAS THE DESTROY'S SERVER-SIDE TRANSACTION ENDED?" in procedure
    assert "EVERY OUTCOME IN 0b IS PROVISIONAL" in procedure
    assert "IF COMPLETION CANNOT BE ESTABLISHED, THE OUTCOME IS UNRESOLVED" in (
        procedure
    )
    assert procedure.count("provided 0a established that its transaction has ended") == 2

    # The inferences PR-20260908-R3-1's first correction left behind, each one
    # false for a schema whose only object is not a relation.
    assert "the database held no objects before the drill" not in procedure
    assert "Nothing was lost either way" not in procedure
    assert "because there was nothing to lose" not in procedure
    assert "THE SCHEMA IS INTACT" not in procedure
    assert "nothing was lost, and NO RECOVERY IS REQUIRED" not in procedure


@pytest.mark.parametrize("injection", DESTROY_FAILURES)
def test_the_failed_destroy_banner_names_the_two_state_artifacts(tmp_path, injection):
    """The reports step 0 runs were written before the destroy and are on disk.

    A procedure that told the operator to inspect the schema without giving them
    the query and the baseline would be asking them to invent a comparison.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )
    work = tmp_path / "work"

    for name in ("schema-state.sql", "schema-state-before.txt"):
        assert (work / name).is_file(), name
        assert str(work / name) in completed.stderr, name

    # The baseline really records the pre-destruction state, not a placeholder.
    baseline = (work / "schema-state-before.txt").read_text(encoding="utf-8")
    assert baseline.strip() == SCHEMA_STATE_ONE_TABLE


def test_the_printed_state_report_distinguishes_the_two_failed_destroys(tmp_path):
    """**Item 2, demonstrated rather than asserted about.**

    The drill emits the same banner for both failures because it cannot tell them
    apart. Step 0 is the thing that can — so both scenarios are driven through the
    boundary and the printed report is then run against it, exactly as an operator
    would. One says the schema still holds its relations; the other says it holds
    none.
    """
    reports = {}
    for label, injection in (
        ("intact", {"destroy_exit": 42, "destroy_applied": False}),
        ("dropped", {"destroy_exit": 42, "destroy_applied": True}),
    ):
        scenario = tmp_path / label
        scenario.mkdir()
        completed, _ = run_drill_against_stubs(
            scenario, ["freedom_runtime_test"], **injection
        )
        assert completed.returncode == 42, completed.stdout + completed.stderr

        work = scenario / "work"
        # The command the banner prints, run through the same stub boundary.
        result = subprocess.run(
            [
                str(scenario / "stub-bin" / "psql"),
                "--dbname=freedom_test",
                "-tAX",
                "-v",
                "ON_ERROR_STOP=1",
                "-f",
                str(work / "schema-state.sql"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        reports[label] = result.stdout.strip()

    assert reports["intact"] == SCHEMA_STATE_ONE_TABLE
    assert reports["dropped"] == SCHEMA_STATE_NOTHING_COUNTED
    assert reports["intact"] != reports["dropped"]


# --------------------------------------------------------------------------
# PR-20260908-R3-1, continued (2026-09-08): zero relations does not mean no
# schema objects.
#
# The `destroy_attempted`/`destroyed` split above is sound. The state report it
# introduced was not sufficient for what its banner then claimed. It checked
# whether `public` exists and counted `pg_class` relations and base tables — and
# **a schema containing only a function reports
# `schema_present=true|relations=0|base_tables=0`**. A function is described by
# `pg_proc`, not `pg_class`, and the table/row inventory does not observe it
# either. So if the DROP committed and recreated `public` while the client result
# was lost, the before and after reports matched, and the banner concluded that
# the schema was intact, that there had been nothing to lose, and that no restore
# was required. The function was gone and the procedure skipped the restore that
# would have recovered it.
#
# Codex reproduced both scenarios by changing only the stub's in-memory answers:
# a pre-destruction report of `relations=0|base_tables=0`, an empty inventory
# before and after, and the existing dropped-state report already at zero. Both
# ran the real drill through the stub boundary, both then ran the two printed
# report commands against that same stub, and in both the diffs matched and the
# banner claimed no recovery was needed.
#
# The correction is in three parts: the report counts every schema-scoped catalog
# class rather than relations alone; the decision is keyed on whether **any**
# counted object is present rather than on two reports merely matching; and the
# one state these counts genuinely cannot resolve — every class zero now *and*
# zero in the baseline — is stated as unresolved and stopped, because zero counts
# over named classes are not evidence that the schema held nothing.
#
# These remain **stub reproductions**. They establish which decision the drill
# emits for a given pair of catalog reports. They establish nothing about whether
# the SQL counts a real catalog correctly; that needs an authorized PostgreSQL
# run and is not claimed here.
# --------------------------------------------------------------------------

#: The finding's scenario, as two runs that differ only in whether the DROP
#: actually took effect — which is exactly what the drill cannot see.
FUNCTION_ONLY_SCENARIOS = [
    pytest.param(
        {"destroy_exit": 42, "destroy_applied": False},
        SCHEMA_STATE_ONE_FUNCTION,
        id="refused-function-still-there",
    ),
    pytest.param(
        {"destroy_exit": 42, "destroy_applied": True},
        SCHEMA_STATE_NOTHING_COUNTED,
        id="applied-function-gone-result-lost",
    ),
]


@pytest.mark.parametrize("injection, after_state", FUNCTION_ONLY_SCENARIOS)
def test_a_function_only_schema_is_never_called_empty_of_objects(
    tmp_path, injection, after_state
):
    """**The R4 finding itself.** `relations=0` is not "no objects".

    The schema holds one function and no relations, so the pre-destruction
    report is `relations=0|base_tables=0` and the row inventory is empty — before
    and after, in both scenarios. Under R3 that made both diffs print nothing,
    and the banner then said the schema was intact, that there was nothing to
    lose and that no restore was required. One of the two scenarios has lost the
    function.
    """
    completed, log = run_drill_against_stubs(
        tmp_path,
        ["freedom_runtime_test"],
        schema_state_intact=SCHEMA_STATE_ONE_FUNCTION,
        schema_state_dropped=SCHEMA_STATE_NOTHING_COUNTED,
        inventory=EMPTY_INVENTORY,
        **injection,
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "DROP SCHEMA public CASCADE" in log
    assert "pg_restore" not in log, "the drill stopped at the destroy"

    work = tmp_path / "work"
    # The state that fools a relation count: an object is there, and neither the
    # relation count nor the row inventory can see it.
    baseline = (work / "schema-state-before.txt").read_text(encoding="utf-8").strip()
    assert baseline == SCHEMA_STATE_ONE_FUNCTION
    assert "relations=0" in baseline
    assert "base_tables=0" in baseline
    assert "routines=1" in baseline
    assert (work / "inventory-before.txt").read_text(encoding="utf-8").strip() == ""

    procedure = _one_line(_procedure(completed.stderr))
    # None of the three claims R3 made for this database.
    assert "the database held no objects before the drill" not in procedure
    assert "Nothing was lost either way" not in procedure
    assert "because there was nothing to lose" not in procedure
    assert "no data restore is required: skip to step 5" not in procedure
    # And the rule that replaces them is keyed on objects, not on relations.
    assert "SOME COUNT IS NON-ZERO" in procedure
    assert "EVERY COUNT IS ZERO" in procedure
    assert "routines" in procedure


def test_the_printed_step_zero_separates_a_lost_function_from_a_refused_drop(
    tmp_path,
):
    """**The correction, demonstrated rather than asserted about.**

    The drill emits one banner for both scenarios because it genuinely cannot
    tell them apart. Step 0 is what can — so both are driven through the boundary
    and the report the banner prints is then run against that same boundary,
    exactly as the operator would run it, and the outcome each report selects is
    read off the printed rules.

    Under R3 both reports were `schema_present=true|relations=0|base_tables=0`
    and this test's central assertion — that they differ — fails.
    """
    reports = {}
    baselines = {}
    for label, injection in (
        ("function-intact", {"destroy_exit": 42, "destroy_applied": False}),
        ("function-lost", {"destroy_exit": 42, "destroy_applied": True}),
    ):
        scenario = tmp_path / label
        scenario.mkdir()
        completed, _ = run_drill_against_stubs(
            scenario,
            ["freedom_runtime_test"],
            schema_state_intact=SCHEMA_STATE_ONE_FUNCTION,
            schema_state_dropped=SCHEMA_STATE_NOTHING_COUNTED,
            inventory=EMPTY_INVENTORY,
            **injection,
        )
        assert completed.returncode == 42, completed.stdout + completed.stderr

        work = scenario / "work"
        result = subprocess.run(
            [
                str(scenario / "stub-bin" / "psql"),
                "--dbname=freedom_test",
                "-tAX",
                "-v",
                "ON_ERROR_STOP=1",
                "-f",
                str(work / "schema-state.sql"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        reports[label] = result.stdout.strip()
        baselines[label] = (
            (work / "schema-state-before.txt").read_text(encoding="utf-8").strip()
        )

    # Both runs started from the same database, and it held the function.
    assert baselines["function-intact"] == baselines["function-lost"]
    assert "routines=1" in baselines["function-intact"]

    # The reports now differ, which is the whole point: the function is observed.
    assert reports["function-intact"] == SCHEMA_STATE_ONE_FUNCTION
    assert reports["function-lost"] == SCHEMA_STATE_NOTHING_COUNTED
    assert reports["function-intact"] != reports["function-lost"]

    # And the printed rules select a different outcome for each of them: a
    # non-zero count matching the baseline means the destroy did not take effect;
    # every count zero against a baseline that recorded an object means it did.
    assert _counted_objects(reports["function-intact"]) > 0
    assert _counted_objects(reports["function-lost"]) == 0
    assert _counted_objects(baselines["function-lost"]) > 0


def test_a_standalone_type_is_not_silently_classified_as_absent(tmp_path):
    """The other object kind the finding names, and the same demonstration.

    A standalone type lives in `pg_type`. Counting routines alone would have
    fixed the function and left this exactly where it was, so the report carries
    a field for it and the same two scenarios separate.
    """
    reports = {}
    for label, injection in (
        ("type-intact", {"destroy_exit": 42, "destroy_applied": False}),
        ("type-lost", {"destroy_exit": 42, "destroy_applied": True}),
    ):
        scenario = tmp_path / label
        scenario.mkdir()
        completed, _ = run_drill_against_stubs(
            scenario,
            ["freedom_runtime_test"],
            schema_state_intact=SCHEMA_STATE_ONE_TYPE,
            schema_state_dropped=SCHEMA_STATE_NOTHING_COUNTED,
            inventory=EMPTY_INVENTORY,
            **injection,
        )
        assert completed.returncode == 42, completed.stdout + completed.stderr
        work = scenario / "work"
        assert (
            (work / "schema-state-before.txt").read_text(encoding="utf-8").strip()
            == SCHEMA_STATE_ONE_TYPE
        )
        result = subprocess.run(
            [
                str(scenario / "stub-bin" / "psql"),
                "--dbname=freedom_test",
                "-tAX",
                "-v",
                "ON_ERROR_STOP=1",
                "-f",
                str(work / "schema-state.sql"),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        reports[label] = result.stdout.strip()

    assert "types=1" in reports["type-intact"]
    assert _counted_objects(reports["type-intact"]) > 0
    assert _counted_objects(reports["type-lost"]) == 0


def test_a_baseline_that_counts_nothing_is_left_explicitly_unresolved(tmp_path):
    """**The conservative stop.** Zero counts are not an inventory of nothing.

    When the baseline itself records zero in every class, an intact schema and a
    recreated one produce the same reports — and neither report establishes that
    the schema held nothing, because both count named classes and no others. R3
    concluded "nothing was lost either way ... no data restore is required" and
    sent the operator on to the grants. That conclusion is withdrawn: the state
    is unresolved, and the procedure stops for an operator rather than mutating.
    """
    completed, log = run_drill_against_stubs(
        tmp_path,
        ["freedom_runtime_test"],
        schema_state_intact=SCHEMA_STATE_NOTHING_COUNTED,
        schema_state_dropped=SCHEMA_STATE_NOTHING_COUNTED,
        inventory=EMPTY_INVENTORY,
        destroy_exit=42,
        destroy_applied=True,
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "pg_restore" not in log
    work = tmp_path / "work"
    assert (
        (work / "schema-state-before.txt").read_text(encoding="utf-8").strip()
        == SCHEMA_STATE_NOTHING_COUNTED
    )
    assert _counted_objects(SCHEMA_STATE_NOTHING_COUNTED) == 0

    procedure = _one_line(_procedure(completed.stderr))
    assert "RECORDED ZERO IN EVERY CLASS: THESE REPORTS CANNOT RESOLVE" in procedure
    assert "THIS IS NOT 'THERE WAS NOTHING TO LOSE'" in procedure
    assert "Do not restore, drop or truncate on the strength of these counts" in (
        procedure
    )
    assert "resolve it with an operator" in procedure
    # The operator is given the one identity inventory that exists.
    assert f"pg_restore --list '{work}/freedom_test.dump'" in procedure

    # The withdrawn conclusion, in every form R3 wrote it.
    assert "held no objects before the drill" not in procedure
    assert "Nothing was lost either way" not in procedure
    assert "there was nothing to lose" not in procedure
    assert "no data restore is required: skip to step 5" not in procedure


def test_the_state_report_counts_every_schema_scoped_catalog_it_claims_to(tmp_path):
    """**At the source**, so a decision cannot outrun the query behind it.

    The banner's outcomes are written over six named classes. If the query stopped
    counting one of them, the field would read zero for a schema that holds such
    an object and the "every count is zero" outcome would fire on a false premise
    — the R3 defect again, one class further down.
    """
    completed, _ = run_drill_against_stubs(tmp_path, ["freedom_runtime_test"])
    assert completed.returncode == 0, completed.stdout + completed.stderr
    query = (tmp_path / "work" / "schema-state.sql").read_text(encoding="utf-8")

    # Named here rather than read from the script: a test that asked the query
    # which classes it counts and then checked that it counts them would pass
    # whatever the query dropped.
    for field in (
        "relations",
        "base_tables",
        "routines",
        "types",
        "extensions",
        "other_objects",
    ):
        assert f"'|{field}=" in query, field
        assert field in SCHEMA_STATE_FIELDS, field
    assert "schema_present=" in query

    # The catalogs each field is counted from, named at the source.
    for catalog in (
        "pg_class",
        "information_schema.tables",
        "pg_proc",
        "pg_type",
        "pg_extension",
        "pg_collation",
        "pg_conversion",
        "pg_operator",
        "pg_opclass",
        "pg_opfamily",
        "pg_ts_config",
        "pg_ts_dict",
        "pg_ts_parser",
        "pg_ts_template",
        "pg_statistic_ext",
    ):
        assert catalog in query, catalog

    # `to_regnamespace` is what separates "no public at all" from "an empty
    # public", and it is preserved.
    assert "to_regnamespace('public')" in query

    # The script says what the report cannot establish, beside the query itself.
    # Read line by line rather than through `_one_line`, which would leave the
    # comment markers between the wrapped halves of a sentence.
    source = DRILL.read_text(encoding="utf-8")
    assert "It does **not** establish *which*" in source
    assert "an exhaustive enumeration of everything PostgreSQL can place" in source
    assert "equal counts are not an object-identity inventory" in source
    assert "pg_restore --list" in source


def test_the_uncertain_restore_is_not_settled_by_an_empty_row_inventory(tmp_path):
    """**The same unsupported inference in the dependent branch** (item 5).

    `restore_attempted`'s step 0 compared the row inventory alone: empty output
    meant rollback, no differences meant the restore committed. On a database
    whose archive holds no base tables those are the *same* output, so a
    rolled-back restore was read as a commit and the operator was told to skip
    the restore. That branch now reads the state report first and stops where the
    counts cannot decide.
    """
    completed, log = run_drill_against_stubs(
        tmp_path,
        ["freedom_runtime_test"],
        schema_state_intact=SCHEMA_STATE_ONE_FUNCTION,
        schema_state_dropped=SCHEMA_STATE_NOTHING_COUNTED,
        inventory=EMPTY_INVENTORY,
        restore_exit=42,
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "pg_restore" in log, "this is the stage after a successful destroy"
    procedure = _procedure(completed.stderr)
    work = tmp_path / "work"
    said = _one_line(procedure)

    # The state report is part of this step 0 now, and it is read before the
    # restore it decides about.
    assert procedure.index(f"-f '{work}/schema-state.sql'") < procedure.index(
        "pg_restore --dbname=freedom_test"
    )
    assert "THE ROW INVENTORY ALONE CANNOT ANSWER THIS" in said
    # The unqualified rules the previous branch used are gone.
    assert "empty output from the query: the transaction rolled back" not in said
    assert "no differences: the restore committed" not in said
    # Each outcome is now conditioned on what the baseline recorded.
    assert "RECORDS ZERO IN EVERY CLASS" in said
    assert (
        "EVERY COUNT IS ZERO while" in said
        and "recorded objects" in said
    )
    assert "BOTH DIFFS PRINT NOTHING while" in said
    assert "SKIP STEP 4" in said


# --------------------------------------------------------------------------
# PR-20260908-R5-1 (2026-09-08): a client that exited does not establish that
# the server-side transaction ended.
#
# The R4 correction reads two reports and, from what they count *now*, decides
# that the destroy did not take effect and that no restore is required — or, one
# stage later, that a restore rolled back and may be run again. Neither decision
# first establishes that the transaction the drill started has finished.
#
# PostgreSQL 16 documents both halves of why that matters:
#
#   * with `client_connection_check_interval=0`, which is the default, the server
#     detects a lost connection at its next socket interaction rather than
#     necessarily stopping the query when the client disappears
#     (runtime-config-connection.html#GUC-CLIENT-CONNECTION-CHECK-INTERVAL); and
#   * a Read Committed `SELECT` sees the data committed before the query began,
#     not the uncommitted changes of another transaction (transaction-iso.html).
#
# So the failure sequence is: `public` holds one function; the DROP reaches the
# server and the client dies without reporting success; both recovery reports see
# the old committed state, `routines=1` and an empty inventory, and both match
# their baselines; R4 directs the operator to conclude that no restore is
# required; the original transaction then commits and the function is gone.
#
# The dependent `restore_attempted` decision has the same omission in the other
# direction: zero counts are also what an uncommitted restore that is *still
# running* looks like from another session, because `--single-transaction`
# publishes nothing until it commits. Repeating the restore on the inference that
# it rolled back would start a second restore beside one still in flight.
#
# Codex demonstrated the missing state by driving the shipped stub with a
# function-only baseline, running both printed reports, and only then creating
# the stub's `.dropped` marker — modelling the original transaction committing
# **after** the observation. The next report read `routines=0`, and no restore
# had been invoked. That is a controlled synthetic sequence showing the missing
# state in the decision contract. It is **not** a PostgreSQL timing reproduction,
# it executes no SQL, and it establishes nothing about the target's
# configuration; the backend-timing concern is an inference from the primary
# documentation above.
#
# The boundary below models completion as its own axis, and the transitions are
# explicit calls rather than sleeps: `destroy_completed=False` leaves the
# transaction outstanding and invisible, and `resolve_pending_transaction` ends
# it at a point the test chooses.
# --------------------------------------------------------------------------


def test_a_pending_destroy_transaction_is_not_settled_by_the_current_reports(
    tmp_path,
):
    """**The R5 finding itself.** The reports are an observation, not an outcome.

    The schema holds one function, the DROP reached the server, the client died
    without reporting success, and the transaction is still open. Both reports
    therefore match their baselines — which is R4's "the destroy did not take
    effect, no data restore is required" premise, arrived at while the destroy is
    still in progress. The transaction then commits and the function is gone.
    """
    completed, log = run_drill_against_stubs(
        tmp_path,
        ["freedom_runtime_test"],
        schema_state_intact=SCHEMA_STATE_ONE_FUNCTION,
        schema_state_dropped=SCHEMA_STATE_NOTHING_COUNTED,
        inventory=EMPTY_INVENTORY,
        destroy_exit=42,
        destroy_applied=True,
        destroy_completed=False,
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "DROP SCHEMA public CASCADE" in log
    assert "pg_restore" not in log, "the drill stopped at the destroy"

    work = tmp_path / "work"
    baseline = (work / "schema-state-before.txt").read_text(encoding="utf-8").strip()
    assert baseline == SCHEMA_STATE_ONE_FUNCTION
    assert (work / "inventory-before.txt").read_text(encoding="utf-8").strip() == ""

    # 1. What an operator running step 0 sees while the transaction is open. The
    #    state report matches the baseline and counts an object, and the row
    #    inventory matches too: R4's "the destroy did not take effect" premise,
    #    exactly.
    observed = read_state_report(tmp_path)
    assert observed == baseline
    assert _counted_objects(observed) > 0

    # 2. The transaction that the client's exit said nothing about now commits.
    resolve_pending_transaction(tmp_path, "destroy", "commit")

    # 3. The same report, run again, now says the function is gone. The
    #    observation in 1 was never the final state of anything.
    after = read_state_report(tmp_path)
    assert after == SCHEMA_STATE_NOTHING_COUNTED
    assert after != observed
    assert _counted_objects(after) == 0

    # 4. So the procedure may not let an operator conclude anything from the
    #    reports until the transaction is known to have ended. **This is the
    #    assertion that fails against R4**, whose step 0 reads the reports first
    #    and never asks the question.
    procedure = _one_line(_procedure(completed.stderr))
    assert "HAS THE DESTROY'S SERVER-SIDE TRANSACTION ENDED?" in procedure
    assert "EVERY OUTCOME IN 0b IS PROVISIONAL" in procedure
    assert "client_connection_check_interval=0" in procedure
    assert (
        "the server does not necessarily stop a statement when its client "
        "disappears" in procedure
    )
    assert "IF COMPLETION CANNOT BE ESTABLISHED, THE OUTCOME IS UNRESOLVED" in (
        procedure
    )
    # And the three things that are not proof of it, named as not proof.
    assert "running the reports twice and getting the same answer" in procedure
    assert "elapsed time" in procedure
    assert "the exit status this drill ended with" in procedure
    # The no-restore conclusion is still reachable, and it is now conditional.
    assert "THE DESTROY DID NOT TAKE EFFECT" in procedure
    assert (
        "provided 0a established that its transaction has ended" in procedure
    )


#: The two completed controls the pending case is read against: a transaction
#: that ended without changing anything, and one that ended having dropped the
#: schema. In both the reports describe a final state, and the outcome the
#: printed rules select is decisive.
COMPLETED_DESTROY_CONTROLS = [
    pytest.param(
        {"destroy_applied": False, "destroy_completed": True},
        SCHEMA_STATE_ONE_FUNCTION,
        id="completed-refused-or-rolled-back",
    ),
    pytest.param(
        {"destroy_applied": True, "destroy_completed": True},
        SCHEMA_STATE_NOTHING_COUNTED,
        id="completed-committed",
    ),
]


@pytest.mark.parametrize("injection, expected", COMPLETED_DESTROY_CONTROLS)
def test_a_completed_destroy_transaction_still_reaches_a_decisive_outcome(
    tmp_path, injection, expected
):
    """**The controls.** The gate must not make every destroy unresolvable.

    When the transaction has ended, the reports do describe the final state, and
    the R4 outcomes are still the ones the printed rules select: a non-zero count
    matching the baseline means the destroy did not take effect, and every count
    zero against a baseline that recorded an object means it did. The correction
    adds a precondition to those outcomes; it does not withdraw them.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path,
        ["freedom_runtime_test"],
        schema_state_intact=SCHEMA_STATE_ONE_FUNCTION,
        schema_state_dropped=SCHEMA_STATE_NOTHING_COUNTED,
        inventory=EMPTY_INVENTORY,
        destroy_exit=42,
        **injection,
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    # Nothing was left outstanding: the completed case leaves no pending marker,
    # so there is no later transition that could change the answer.
    assert not (tmp_path / "stub-state.destroy-pending").exists()

    observed = read_state_report(tmp_path)
    assert observed == expected
    # Re-reading it changes nothing, because nothing is in flight.
    assert read_state_report(tmp_path) == observed

    procedure = _one_line(_procedure(completed.stderr))
    assert "SOME COUNT IS NON-ZERO AND THE WHOLE STATE REPORT MATCHES" in procedure
    assert "THE DESTROY DID NOT TAKE EFFECT" in procedure
    assert "NO DATA RESTORE IS REQUIRED and none may be run" in procedure
    assert "That is the 'destroyed' state. Continue at step 1" in procedure


def test_a_pending_restore_transaction_is_not_called_a_rollback(tmp_path):
    """**The dependent decision**, in the other direction.

    The destroy succeeded and the restore's client died without reporting
    success. Its transaction is still running, so it has published nothing and
    every count is zero — which R4 reads as "the transaction rolled back,
    continue at step 1" and sends the operator to run `pg_restore` again beside a
    restore that is still in flight. Then it commits.
    """
    completed, log = run_drill_against_stubs(
        tmp_path,
        ["freedom_runtime_test"],
        restore_exit=42,
        restore_applied=True,
        restore_completed=False,
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "pg_restore" in log, "this is the stage after a successful destroy"

    work = tmp_path / "work"
    baseline = (work / "schema-state-before.txt").read_text(encoding="utf-8").strip()
    assert baseline == SCHEMA_STATE_ONE_TABLE
    assert _counted_objects(baseline) > 0

    # 1. What the operator sees while the restore is still running: nothing of
    #    what the archive holds, which is also what a rollback leaves.
    observed = read_state_report(tmp_path)
    assert observed == SCHEMA_STATE_NOTHING_COUNTED
    assert _counted_objects(observed) == 0

    # 2. The restore commits after that observation.
    resolve_pending_transaction(tmp_path, "restore", "commit")
    after = read_state_report(tmp_path)
    assert after == SCHEMA_STATE_ONE_TABLE
    assert after != observed

    # 3. **Fails against R4**: its step 0 reads "every count is zero" as a
    #    rollback without asking whether the restore has finished.
    procedure = _one_line(_procedure(completed.stderr))
    assert "HAS THE RESTORE'S SERVER-SIDE TRANSACTION ENDED?" in procedure
    assert "EVERY OUTCOME IN 0b IS PROVISIONAL" in procedure
    assert "client_connection_check_interval=0" in procedure
    assert (
        "an unfinished restore looks exactly like a rolled-back one from another "
        "session" in procedure
    )
    assert "IF COMPLETION CANNOT BE ESTABLISHED, THE OUTCOME IS UNRESOLVED" in (
        procedure
    )
    # The rollback conclusion survives, conditioned on completion.
    assert "the transaction rolled back" in procedure
    assert "provided 0a established that its transaction has ended" in procedure


#: The restore's completed controls: one that ended having committed, and one
#: that ended having rolled back. Neither leaves anything outstanding.
COMPLETED_RESTORE_CONTROLS = [
    pytest.param(True, SCHEMA_STATE_ONE_TABLE, id="completed-committed"),
    pytest.param(False, SCHEMA_STATE_NOTHING_COUNTED, id="completed-rolled-back"),
]


@pytest.mark.parametrize("applied, expected", COMPLETED_RESTORE_CONTROLS)
def test_a_completed_restore_transaction_still_resolves_to_one_outcome(
    tmp_path, applied, expected
):
    """**The controls for the dependent decision.**

    Once the restore's transaction has ended, the reports separate a commit from
    a rollback exactly as R4 had them do, and both printed outcomes are still
    there: skip the restore, or run it.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path,
        ["freedom_runtime_test"],
        restore_exit=42,
        restore_applied=applied,
        restore_completed=True,
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert not (tmp_path / "stub-state.restore-pending").exists()

    observed = read_state_report(tmp_path)
    assert observed == expected
    assert read_state_report(tmp_path) == observed

    procedure = _one_line(_procedure(completed.stderr))
    assert "EVERY COUNT IS ZERO while" in procedure
    assert "the transaction rolled back" in procedure
    assert "BOTH DIFFS PRINT NOTHING while" in procedure
    assert "SKIP STEP 4" in procedure


@pytest.mark.parametrize("stage, injection, status", STAGE_INJECTIONS)
def test_no_recovery_instruction_ends_a_backend_to_settle_the_question(
    tmp_path, stage, injection, status
):
    """**The authority this correction does not take.**

    A completion gate is one termination away from becoming a procedure that
    resolves an uncertain transaction by killing it — which converts an unknown
    outcome into a rollback the operator chose, at a moment when nobody knows
    what the transaction was doing. No stage's banner may prescribe it.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )
    banner = _recovery_banner(completed.stderr)

    for authority in (
        "pg_terminate_backend",
        "pg_cancel_backend",
        "pg_ctl",
        "SIGKILL",
        "kill -9",
    ):
        assert authority not in banner, (stage, authority)

    # And the prohibition is stated where the question is asked, at the two
    # stages that have an open-transaction question at all.
    if stage in ("destroy_attempted", "restore_attempted"):
        said = _one_line(banner)
        assert "Do not terminate or cancel a backend to settle this" in said
        assert "This procedure never does that" in said


def test_the_completion_gate_says_what_would_establish_completion(tmp_path):
    """**What the operator is asked to establish, and its limits.**

    A gate that said only "make sure it finished" would be an instruction to
    guess. The banner names where a still-running backend is visible, and it
    names the two ways that observation is not conclusive: a pid alone is not an
    identity, and PostgreSQL restricts columns rather than rows, so a session's
    existence is visible to every user while the fields that would identify its
    work and show an open transaction may be null (PostgreSQL 16, Viewing
    Statistics). Seeing a row one cannot attribute to this drill, or a null
    where the answer would be, is not an observation that the transaction ended.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path,
        ["freedom_runtime_test"],
        destroy_exit=42,
        destroy_applied=True,
        destroy_completed=False,
    )
    procedure = _one_line(_procedure(completed.stderr))

    assert "pg_stat_activity" in procedure
    assert "A pid is not an identity on its own" in procedure
    assert "match backend_start with it" in procedure
    assert "PostgreSQL restricts" in procedure
    assert "columns here, not rows" in procedure
    assert "are visible to all users" in procedure
    assert "many columns are null unless you are a superuser or hold" in procedure
    assert "pg_read_all_stats" in procedure
    assert (
        "A NULL FIELD, OR BEING UNABLE TO ASSOCIATE A VISIBLE SESSION WITH THIS "
        "DRILL, IS NOT PROOF THAT THIS TRANSACTION HAS ENDED"
    ) in procedure
    # And the claim this replaces: permissions do not hide the session row.
    assert "row you cannot see" not in procedure
    # Absence is stable and presence is not, which is why only one direction of
    # the answer licenses a conclusion.
    assert "A backend that has ended cannot come back" in procedure
    # The reports are re-run after the gate answers, not before it.
    assert "read AFTER 0a has answered" in procedure
    assert "run them again" in procedure


def test_a_successful_destroy_still_reports_a_known_empty_database(tmp_path):
    """**The positive control, and item 4.** `destroyed` keeps its meaning.

    The correction must not turn every destruction into an uncertainty. When the
    destroy reports success and the restore has not started, the database really
    is empty, the banner says so, and its procedure is the full restore. This is
    the pre-existing `destroyed` behaviour, unchanged.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], restore_exit=42
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "DROP SCHEMA public CASCADE" in log
    said = _one_line(_recovery_banner(completed.stderr))
    # `restore_attempted`, which is the stage after a successful destroy, and it
    # is the one that describes the restore as uncertain rather than the destroy.
    assert "WHETHER IT COMMITTED IS NOT KNOWN" in said
    assert "WHAT THE SCHEMA NOW HOLDS IS NOT KNOWN" not in said


def test_the_schema_state_baseline_is_recorded_before_the_destroy(tmp_path):
    """Step 3a runs on the normal path too, before anything is destroyed.

    If the baseline were captured only when something went wrong it would be
    captured after the destroy, and it would describe the state it exists to be
    compared against.
    """
    completed, log = run_drill_against_stubs(tmp_path, ["freedom_runtime_test"])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "3a. Recording the schema state" in completed.stdout
    baseline = tmp_path / "work" / "schema-state-before.txt"
    assert baseline.is_file()
    assert baseline.read_text(encoding="utf-8").strip() == SCHEMA_STATE_ONE_TABLE

    # Captured before the destroy: the report the stub gave is the pre-destroy
    # one, and the drill issued it before it issued the drop.
    drill_log = log.splitlines()
    state_at = next(
        index for index, line in enumerate(drill_log) if "schema-state.sql" in line
    )
    drop_at = next(
        index
        for index, line in enumerate(drill_log)
        if "DROP SCHEMA public CASCADE" in line
    )
    assert state_at < drop_at


def test_the_failed_destroy_offers_neither_a_rerun_nor_a_rebuild(tmp_path):
    """**Item 3**, for the fallback as well as for the procedure.

    Re-running the drill would dump and destroy whatever is actually there, and
    rebuilding from migrations would replace a schema that may be intact. Neither
    is offered while the state is unknown, and the banner says why.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], destroy_exit=42, destroy_applied=False
    )
    banner = _one_line(_recovery_banner(completed.stderr))

    assert "Re-running this drill is NOT a recovery step" in banner
    assert "until step 0 has answered it is not a step of any kind" in banner
    assert "it would replace a schema that may be completely intact" in banner
    # The rebuild is named only as what applies *after* step 0 settles the state.
    assert "If step 0 establishes that the schema was dropped and recreated" in banner


def test_a_restore_that_did_not_report_success_is_described_as_uncertain(tmp_path):
    """**Stage `restore_attempted`.** The honest answer, not a guess.

    `--single-transaction --exit-on-error` rolls back on an ordinary error, so the
    database is normally empty — but a killed process is not an ordinary error,
    and the script cannot tell them apart. The banner says so and gives the
    operator the query that settles it before they decide to restore.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], restore_exit=42
    )
    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "DROP SCHEMA public CASCADE" in log

    banner = _recovery_banner(completed.stderr)
    said = _one_line(banner)
    assert "WHETHER IT COMMITTED IS NOT KNOWN" in said
    # It does not assert the database is empty, and it does not assert it is full.
    assert "so the database is EMPTY" not in said

    procedure = _procedure(completed.stderr)
    work = tmp_path / "work"
    # Step 0 establishes the fact the rest of the procedure depends on, and it is
    # before the restore.
    assert procedure.index(f"-f '{work}/inventory-query.sql'") < procedure.index(
        "pg_restore --dbname=freedom_test"
    )
    assert "SKIP STEP 4" in procedure
    assert "the restore is partial" in _one_line(procedure)


def test_a_schema_grant_failure_after_a_committed_restore_does_not_restore_again(
    tmp_path,
):
    """**Stage `restored`.** Codex's reproduction, one step earlier.

    The restore succeeded and the grants did not. Repeating the data restore over
    the restored objects fails; the resume point is the grants.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], schema_grants_exit=42
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    # The log is the evidence that the restore really did run and report success.
    assert "pg_restore" in log
    assert "5b. Re-applying the runtime grants" in completed.stdout

    banner = _recovery_banner(completed.stderr)
    said = _one_line(banner)
    assert "The data restore COMPLETED SUCCESSFULLY" in said
    assert "must not be restored over" in said or "Do not restore over it" in said

    procedure = _procedure(completed.stderr)
    work = tmp_path / "work"
    assert "pg_restore" not in procedure, "the committed restore must not repeat"
    assert procedure.index(f"-f '{work}/schema-grants.sql'") < procedure.index(
        f"-f '{work}/runtime-grants.sql'"
    )
    assert f"-f '{work}/grants-inventory.sql'" in procedure


def test_a_runtime_grant_failure_resumes_at_the_runtime_grants(tmp_path):
    """**Stage `schema_grants_applied`.** Exactly Codex's reproduction.

    The stub `psql` failed only while applying `runtime-grants.sql`; the log shows
    a successful `pg_restore` and a successful schema-grant application before it.
    The emitted procedure begins at the runtime grants.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], runtime_grants_exit=42
    )

    assert completed.returncode == 42, completed.stdout + completed.stderr
    assert "pg_restore" in log
    assert "schema-grants.sql" in log

    banner = _recovery_banner(completed.stderr)
    said = _one_line(banner)
    assert "The data restore and the schema grants COMPLETED SUCCESSFULLY" in said
    assert "N-20 state" in said

    procedure = _procedure(completed.stderr)
    work = tmp_path / "work"
    assert "pg_restore" not in procedure
    # The schema grants are not re-applied either: they succeeded.
    assert f"-f '{work}/schema-grants.sql'" not in procedure
    assert f"sha256sum --check '{work}/runtime-grants.sql.sha256'" in procedure
    assert procedure.index(f"-f '{work}/runtime-grants.sql'") < procedure.index(
        f"-f '{work}/grants-inventory.sql'"
    )


@pytest.mark.parametrize(
    "injection, failure",
    [
        ({"privilege_loss": True}, "privileges present before the drill are"),
        ({"inventory_mismatch": True}, "the inventory differs"),
    ],
)
def test_a_verification_failure_is_not_answered_by_repeating_the_restore(
    tmp_path, injection, failure
):
    """**Stage `grants_applied`.** A verification failure is not a lost database.

    Both of the drill's own verifications run after everything has been applied.
    The pre-fix banner told the operator to restore the whole database again,
    which fails on the objects that are there.
    """
    completed, log = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )

    assert completed.returncode == 1, completed.stdout + completed.stderr
    assert failure in completed.stderr
    banner = _recovery_banner(completed.stderr)
    said = _one_line(banner)
    assert "ALL COMPLETED" in said
    assert "must not be restored over" in said
    # The claim the pre-fix banner made unconditionally.
    assert "the database is empty or partially restored" not in said

    procedure = _procedure(completed.stderr)
    assert "pg_restore" not in procedure
    assert "grants-inventory.sql" in procedure
    assert "inventory-query.sql" in procedure
    # A repair is offered; a destructive reset is not performed for the operator.
    assert "Re-apply them" in procedure
    assert "operator decision" in _one_line(procedure)


@pytest.mark.parametrize("stage, injection, status", STAGE_INJECTIONS)
def test_no_recovery_path_repeats_a_data_restore_it_knows_committed(
    tmp_path, stage, injection, status
):
    """The acceptance condition, over every stage that can be reached.

    A stage whose data restore is known to have committed must not print the
    restore command at all; the two stages where it is not known must.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )
    assert completed.returncode == status, completed.stdout + completed.stderr

    procedure = _procedure(completed.stderr)
    if stage in STAGES_THAT_MAY_PRINT_A_RESTORE:
        assert "pg_restore --dbname=freedom_test" in procedure
    else:
        assert "pg_restore" not in procedure, stage


@pytest.mark.parametrize("stage, injection, status", STAGE_INJECTIONS)
def test_no_recovery_path_prescribes_an_unrequested_destructive_reset(
    tmp_path, stage, injection, status
):
    """PR-20260907-R2-2 item 2: no `DROP`, no `--clean`, no `TRUNCATE`.

    A banner that solved the ordering problem by resetting the database first
    would pass the previous test and would be worse than the defect.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )
    banner = _recovery_banner(completed.stderr)

    for destructive in ("DROP SCHEMA", "DROP DATABASE", "--clean", "-c ", "TRUNCATE"):
        assert destructive not in banner, (stage, destructive)


@pytest.mark.parametrize("stage, injection, status", STAGE_INJECTIONS)
def test_every_emitted_recovery_procedure_ends_in_both_verifications(
    tmp_path, stage, injection, status
):
    """PR-20260907-R2-2 item 3: privileges **and** the data inventory.

    A recovery that restores the grants and never looks at the rows has verified
    half of what the drill verifies, and a restore command's exit status is not a
    substitute for either.
    """
    completed, _ = run_drill_against_stubs(
        tmp_path, ["freedom_runtime_test"], **injection
    )
    procedure = _procedure(completed.stderr)
    work = tmp_path / "work"

    privileges = procedure.index(f"-f '{work}/grants-inventory.sql'")
    inventory = procedure.rindex(f"-f '{work}/inventory-query.sql'")
    assert privileges < inventory, stage
    assert "comm -23" in procedure
    assert "Recovery is complete only when" in procedure


@pytest.mark.parametrize(
    "stage, injection, status",
    # `schema_grants_applied` is deliberately absent: with no runtime role there
    # is no runtime-grant application to fail at, so the drill goes from the
    # schema grants straight to `grants_applied`. The test below asserts that
    # rather than leaving it as an unexplained gap.
    [row for row in STAGE_INJECTIONS if row[0] != "schema_grants_applied"],
)
def test_the_zero_runtime_role_branch_is_stated_at_every_stage_it_reaches(
    tmp_path, stage, injection, status
):
    """PR-20260907-R2-2 item 6: the empty case, at each resume point.

    A banner that simply omitted the runtime step would be indistinguishable from
    one that had forgotten it — at every stage, not only after a failed restore.
    """
    completed, _ = run_drill_against_stubs(tmp_path, [], **injection)
    assert completed.returncode == status, completed.stdout + completed.stderr

    banner = _one_line(_recovery_banner(completed.stderr))
    assert "No runtime role held table grants before the destroy" in banner
    assert "no runtime-grants.sql" in banner
    assert "runtime-grants.sql.sha256" not in banner
    assert not (tmp_path / "work" / "runtime-grants.sql").exists()
    # The schema grants are still part of whatever this stage still has to do,
    # unless they have already been applied.
    if stage in ("destroy_attempted", "restore_attempted", "restored"):
        assert "schema-grants.sql" in banner


def test_the_zero_runtime_role_path_skips_the_runtime_grant_stage_entirely(tmp_path):
    """The gap the parametrization above leaves out, stated rather than implied.

    With no runtime role there is nothing to apply after the schema grants, so
    the drill advances to `grants_applied` and its resume point is the
    verification. Injecting a runtime-grant failure therefore changes nothing:
    the step it would fail is never run.
    """
    completed, log = run_drill_against_stubs(tmp_path, [], runtime_grants_exit=42)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "Skipped: no runtime role held grants before the destroy." in completed.stdout
    assert "runtime-grants.sql" not in log
    assert "RECOVERY REQUIRED" not in completed.stderr


def test_a_refusal_before_the_destroy_still_prints_no_banner_at_all(tmp_path):
    """The `intact` stage, which is the one that must stay silent.

    DS-R8-2 corrected a banner that claimed a recovery was required when nothing
    had been destroyed. Adding stages must not reintroduce it.
    """
    completed, log = run_drill_against_stubs(tmp_path, ["role-with-dash"])

    assert completed.returncode == 2
    assert "RECOVERY REQUIRED" not in completed.stderr
    assert "DROP SCHEMA" not in log


def test_a_successful_drill_prints_no_banner(tmp_path):
    """And the `verified` stage, the other silent one."""
    completed, log = run_drill_against_stubs(tmp_path, ["freedom_runtime_test"])

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "RECOVERY REQUIRED" not in completed.stderr
    assert "DROP SCHEMA public CASCADE" in log


def test_each_stage_is_recorded_only_after_its_command_succeeded():
    """**PR-20260907-R2-2 item 1**, asserted at the source, and **corrected by
    PR-20260908-R3-1**.

    A stage assigned *before* its command claims a success that has not happened.
    This test used to grant the destroy an exception — `assert destroyed < drop`,
    with the comment "the destroy is the deliberate exception" — and that
    assertion is what made the defect mandatory: it required the script to record
    a *known* empty database before running the command that would empty it.

    There is no exception now. `destroy_attempted` is set before the command,
    because from that point on this drill may have destroyed something and must
    say so whatever happens; it is a statement of responsibility and its banner
    claims no knowledge. `destroyed` is set after the command succeeds, exactly
    like every other stage, because it *is* a claim about what the database
    holds.
    """
    source = DRILL.read_text(encoding="utf-8")
    code = "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith("#")
    )

    attempted_destroy = code.index('DRILL_STAGE="destroy_attempted"')
    destroyed = code.index('DRILL_STAGE="destroyed"')
    drop = code.index("DROP SCHEMA public CASCADE")
    attempted = code.index('DRILL_STAGE="restore_attempted"')
    restore = code.index('"${RESTORE_COMMAND[@]}"')
    restored = code.index('DRILL_STAGE="restored"')
    schema_apply = code.index(
        'psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 -f "${SCHEMA_GRANTS}" >/dev/null'
    )
    schema_done = code.index('DRILL_STAGE="schema_grants_applied"')
    runtime_apply = code.index(
        'psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 -f "${RUNTIME_GRANTS}" >/dev/null'
    )
    grants_done = code.index('DRILL_STAGE="grants_applied"')
    verified = code.index('DRILL_STAGE="verified"')
    privilege_check = code.index("LOST_PRIVILEGES=")

    # Responsibility before the command, knowledge only after it succeeded.
    assert attempted_destroy < drop < destroyed
    assert attempted < restore < restored
    assert restored < schema_apply < schema_done
    assert schema_done < runtime_apply < grants_done
    assert privilege_check < verified


# --------------------------------------------------------------------------
# The two PostgreSQL regressions PR-20260907-1 and PR-20260907-2 require, for a
# **later authorized run**.
#
# Both need a live disposable database and the second creates and drops a role,
# so both are deselected under the pre-execution restriction that governs this
# correction, alongside the seven existing destructive integration cases. They
# are written now so the authorized run has something to execute, and they are
# **not claimed to pass against this tree**.
# --------------------------------------------------------------------------


def test_the_documented_recovery_procedure_restores_runtime_table_grants(
    migrated_database, tmp_path
):
    """**PR-20260907-1 against PostgreSQL.** Follow the printed procedure and
    check what the database actually ends up holding.

    The pre-fix procedure — `pg_restore --no-privileges` then
    `schema-grants.sql` — leaves this assertion failing: every row is back and
    `runtime_privilege_count` is zero.
    """
    require_postgresql_tools()
    role = _require_runtime_role(migrated_database)
    before = runtime_privilege_count(migrated_database, role)
    assert before > 0

    source = DRILL.read_text(encoding="utf-8")
    bad_restore = 'echo "Simulated restore failure" >&2; exit 42'
    neutered = tmp_path / "drill-failing-restore.sh"
    neutered.write_text(
        source.replace('"${RESTORE_COMMAND[@]}"', bad_restore, 1), encoding="utf-8"
    )
    neutered.chmod(0o755)
    shutil.copy(RUNTIME_GRANTS_TEMPLATE, tmp_path / RUNTIME_GRANTS_TEMPLATE.name)

    workdir = tmp_path / "work"
    child = {k: v for k, v in os.environ.items() if k not in LIBPQ_VARIABLES}
    try:
        completed = subprocess.run(
            [str(neutered), "freedom_test", str(workdir)],
            cwd=ROOT, capture_output=True, text=True, env=child,
        )
        assert completed.returncode == 42, completed.stdout + completed.stderr
        assert "RECOVERY REQUIRED." in completed.stderr

        # The database is now empty or partial, and the runtime role holds
        # nothing. This is the state an operator has to recover from.
        assert runtime_privilege_count(migrated_database, role) == 0

        # Follow the printed procedure, in the printed order.
        for artifact in ("freedom_test.dump", "schema-grants.sql",
                         "runtime-grants.sql"):
            checked = subprocess.run(
                ["sha256sum", "--check", str(workdir / f"{artifact}.sha256")],
                cwd=workdir, capture_output=True, text=True,
            )
            assert checked.returncode == 0, checked.stdout + checked.stderr

        restored = subprocess.run(
            ["pg_restore", "--dbname=freedom_test", "--no-owner", "--no-privileges",
             "--single-transaction", "--exit-on-error",
             str(workdir / "freedom_test.dump")],
            capture_output=True, text=True, env=child,
        )
        assert restored.returncode == 0, restored.stdout + restored.stderr

        for script in ("schema-grants.sql", "runtime-grants.sql"):
            applied = subprocess.run(
                ["psql", "--dbname=freedom_test", "-v", "ON_ERROR_STOP=1",
                 "-f", str(workdir / script)],
                capture_output=True, text=True, env=child,
            )
            assert applied.returncode == 0, applied.stdout + applied.stderr

        # **The assertion the pre-fix procedure fails.** The rows came back and
        # so did the grants.
        assert runtime_privilege_count(migrated_database, role) == before

        # And the runtime role can actually use its tables, which is the thing
        # a privilege count is a proxy for.
        with migrated_database.connect() as connection:
            usable = connection.execute(
                text(
                    "SELECT has_schema_privilege(:role, 'public', 'USAGE') "
                    "AND has_table_privilege(:role, 'characters', 'SELECT') "
                    "AND has_table_privilege(:role, 'audit_events', 'INSERT') "
                    "AND NOT has_table_privilege(:role, 'audit_events', 'UPDATE')"
                ),
                {"role": role},
            ).scalar_one()
        assert usable is True

        # The printed verification says the recovery is complete.
        inventory = subprocess.run(
            ["psql", "--dbname=freedom_test", "-tAX", "-v", "ON_ERROR_STOP=1",
             "-f", str(workdir / "grants-inventory.sql")],
            capture_output=True, text=True, env=child,
        )
        assert inventory.returncode == 0, inventory.stdout + inventory.stderr
        before_lines = sorted(
            (workdir / "grants-before.txt").read_text(encoding="utf-8").split("\n")
        )
        after_lines = sorted(inventory.stdout.split("\n"))
        lost = [line for line in before_lines if line and line not in after_lines]
        assert lost == [], lost
    finally:
        applied_sql = RUNTIME_GRANTS_TEMPLATE.read_text().replace("__APP_ROLE__", role)
        with migrated_database.begin() as connection:
            connection.exec_driver_sql(
                "ALTER SCHEMA public OWNER TO pg_database_owner; "
                "REVOKE ALL ON SCHEMA public FROM PUBLIC; "
                "GRANT CREATE, USAGE ON SCHEMA public TO pg_database_owner; "
                "GRANT USAGE ON SCHEMA public TO PUBLIC;"
            )
            connection.exec_driver_sql(applied_sql)


def test_a_role_whose_sql_identity_differs_refuses_against_postgresql(
    migrated_database, tmp_path
):
    """**PR-20260907-2 against PostgreSQL.** The catalog really does keep the
    case and the whitespace of a quoted role name, and the drill really does
    refuse before the destroy.

    Creating and dropping a role is a cluster-wide operation, which is why this
    is deselected here and belongs to an authorized run. It uses a name no
    deployment of this platform has.
    """
    require_postgresql_tools()
    if runtime_grantees(migrated_database):
        pytest.skip(
            "This check grants to its own probe role and needs a database with "
            "no other non-owner grantee."
        )

    probe = f"FbDrillProbe_{uuid4().hex[:8]}"
    with migrated_database.begin() as connection:
        connection.exec_driver_sql(f'CREATE ROLE "{probe}" NOLOGIN')
        connection.exec_driver_sql(f'GRANT SELECT ON characters TO "{probe}"')
    try:
        # PostgreSQL preserved the mixed case, which is the premise.
        assert probe in runtime_grantees(migrated_database)

        rows_before = runtime_privilege_count(migrated_database, probe)
        completed = run_drill("freedom_test", tmp_path)

        assert completed.returncode == 2, completed.stdout + completed.stderr
        assert "is not a supported" in completed.stderr
        # Refused before the destroy: the grant it would have rendered names a
        # role that does not exist, and the schema is untouched.
        assert "4. Destroying the schema" not in completed.stdout
        assert "RECOVERY REQUIRED" not in completed.stderr
        assert runtime_privilege_count(migrated_database, probe) == rows_before
        with migrated_database.connect() as connection:
            assert connection.execute(
                text("SELECT count(*) FROM information_schema.tables "
                     "WHERE table_schema = 'public'")
            ).scalar_one() > 0
    finally:
        with migrated_database.begin() as connection:
            connection.exec_driver_sql(
                f'REVOKE ALL ON ALL TABLES IN SCHEMA public FROM "{probe}"'
            )
            connection.exec_driver_sql(f'DROP ROLE IF EXISTS "{probe}"')


# --------------------------------------------------------------------------
# The two PostgreSQL regressions PR-20260907-R2-1 and PR-20260907-R2-2 require,
# for the same **later authorized run**. Neither is executed under the prompt
# that adds them, and neither is claimed to pass.
#
# The first is the half a stub cannot supply. `encoded_role_report` computes the
# transport in Python, so the stub tests prove that the shell decodes and
# classifies records losslessly and prove **nothing** about whether the SQL
# encodes the catalog correctly. Only PostgreSQL can answer that, and only for a
# role whose name really does contain a newline.
# --------------------------------------------------------------------------


def test_a_newline_bearing_role_refuses_against_postgresql(
    migrated_database, tmp_path
):
    """**PR-20260907-R2-1 against PostgreSQL.** The database-semantic half.

    Creates a `NOLOGIN` probe role whose quoted catalog name contains a newline,
    asserts PostgreSQL really stored it that way, and then asserts three things
    about the drill's own query rather than about a fixture:

    1. the query emits one `ROLE <hex>` record whose hex decodes to the exact
       catalog bytes, newline included — the encoding is correct, not merely
       present;
    2. the terminator declares one record; and
    3. the drill refuses, exit 2, before any destruction.

    Against the pre-fix script this fails at (3): the trailing newline was
    stripped by the command substitution and the drill accepted a different,
    supported name. Creating and dropping a cluster role makes this a deselected
    case for an authorized run.
    """
    require_postgresql_tools()
    if runtime_grantees(migrated_database):
        pytest.skip(
            "This check grants to its own probe role and needs a database with "
            "no other non-owner grantee."
        )

    probe = f"fb_drill_probe_{uuid4().hex[:8]}\n"
    with migrated_database.begin() as connection:
        connection.exec_driver_sql(f'CREATE ROLE "{probe}" NOLOGIN')
        connection.exec_driver_sql(f'GRANT SELECT ON characters TO "{probe}"')
    try:
        # (1) and (2): the catalog kept the newline, and the drill's own query
        # transports it losslessly.
        assert probe in runtime_grantees(migrated_database)
        report_sql = _role_report_sql(DRILL.read_text(encoding="utf-8"))
        with migrated_database.connect() as connection:
            lines = list(
                connection.execute(text(report_sql)).scalars()
            )
        assert lines == [
            f"ROLE {probe.encode('utf-8').hex()}",
            "END 1",
        ], lines

        # (3): the refusal, before the destroy.
        rows_before = runtime_privilege_count(migrated_database, probe)
        completed = run_drill("freedom_test", tmp_path)

        assert completed.returncode == 2, completed.stdout + completed.stderr
        assert "is not a supported" in completed.stderr
        assert "4. Destroying the schema" not in completed.stdout
        assert "RECOVERY REQUIRED" not in completed.stderr
        assert runtime_privilege_count(migrated_database, probe) == rows_before
        with migrated_database.connect() as connection:
            assert connection.execute(
                text("SELECT count(*) FROM information_schema.tables "
                     "WHERE table_schema = 'public'")
            ).scalar_one() > 0
    finally:
        with migrated_database.begin() as connection:
            connection.exec_driver_sql(
                f'REVOKE ALL ON ALL TABLES IN SCHEMA public FROM "{probe}"'
            )
            connection.exec_driver_sql(f'DROP ROLE IF EXISTS "{probe}"')


def test_the_post_restore_recovery_path_restores_grants_without_restoring_again(
    migrated_database, tmp_path
):
    """**PR-20260907-R2-2 against PostgreSQL.** Follow the emitted procedure from
    the stage the failure actually reached.

    The drill is copied with its runtime-grant application replaced by a failing
    command, so the data restore commits and the run stops at
    `schema_grants_applied` — Codex's reproduction. The printed procedure is then
    followed exactly, and the assertions are about what the database ends up
    holding: the rows are still those the drill dumped, the runtime role can use
    its tables and still cannot `UPDATE` an append-only one, and both printed
    verifications print nothing.

    Against the pre-fix banner this fails at the first mutation step, because
    that banner began with the same full `pg_restore` and it aborts on the
    objects the committed restore already created.
    """
    require_postgresql_tools()
    role = _require_runtime_role(migrated_database)
    before = runtime_privilege_count(migrated_database, role)
    assert before > 0

    source = DRILL.read_text(encoding="utf-8")
    runtime_apply = (
        '  psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 '
        '-f "${RUNTIME_GRANTS}" >/dev/null'
    )
    assert runtime_apply in source, "the re-application step moved; this test is stale"
    neutered = tmp_path / "drill-failing-runtime-grants.sh"
    neutered.write_text(
        source.replace(
            runtime_apply,
            '  echo "Simulated runtime grant failure" >&2; exit 42',
            1,
        ),
        encoding="utf-8",
    )
    neutered.chmod(0o755)
    shutil.copy(RUNTIME_GRANTS_TEMPLATE, tmp_path / RUNTIME_GRANTS_TEMPLATE.name)

    workdir = tmp_path / "work"
    child = {k: v for k, v in os.environ.items() if k not in LIBPQ_VARIABLES}
    try:
        completed = subprocess.run(
            [str(neutered), "freedom_test", str(workdir)],
            cwd=ROOT, capture_output=True, text=True, env=child,
        )
        assert completed.returncode == 42, completed.stdout + completed.stderr
        assert "RECOVERY REQUIRED." in completed.stderr
        banner = _one_line(_recovery_banner(completed.stderr))
        assert "The data restore and the schema grants COMPLETED SUCCESSFULLY" in banner

        # The state the operator is actually in: rows restored, runtime grants
        # gone. That is the N-20 shape, and it is what the resume point repairs.
        assert runtime_privilege_count(migrated_database, role) == 0

        # The emitted procedure does not repeat the data restore.
        procedure = _procedure(completed.stderr)
        assert "pg_restore" not in procedure

        # Follow it: checksum, apply, verify. Nothing else.
        checked = subprocess.run(
            ["sha256sum", "--check", str(workdir / "runtime-grants.sql.sha256")],
            cwd=workdir, capture_output=True, text=True,
        )
        assert checked.returncode == 0, checked.stdout + checked.stderr
        applied = subprocess.run(
            ["psql", "--dbname=freedom_test", "-v", "ON_ERROR_STOP=1",
             "-f", str(workdir / "runtime-grants.sql")],
            capture_output=True, text=True, env=child,
        )
        assert applied.returncode == 0, applied.stdout + applied.stderr

        assert runtime_privilege_count(migrated_database, role) == before
        with migrated_database.connect() as connection:
            usable = connection.execute(
                text(
                    "SELECT has_schema_privilege(:role, 'public', 'USAGE') "
                    "AND has_table_privilege(:role, 'characters', 'SELECT') "
                    "AND has_table_privilege(:role, 'audit_events', 'INSERT') "
                    "AND NOT has_table_privilege(:role, 'audit_events', 'UPDATE')"
                ),
                {"role": role},
            ).scalar_one()
        assert usable is True

        # Both printed verifications, and both must print nothing.
        for query, baseline in (
            ("grants-inventory.sql", "grants-before.txt"),
            ("inventory-query.sql", "inventory-before.txt"),
        ):
            result = subprocess.run(
                ["psql", "--dbname=freedom_test", "-tAX", "-v", "ON_ERROR_STOP=1",
                 "-f", str(workdir / query)],
                capture_output=True, text=True, env=child,
            )
            assert result.returncode == 0, result.stdout + result.stderr
            before_lines = sorted(
                (workdir / baseline).read_text(encoding="utf-8").split("\n")
            )
            after_lines = sorted(result.stdout.split("\n"))
            lost = [line for line in before_lines if line and line not in after_lines]
            assert lost == [], (query, lost)
    finally:
        applied_sql = RUNTIME_GRANTS_TEMPLATE.read_text().replace("__APP_ROLE__", role)
        with migrated_database.begin() as connection:
            connection.exec_driver_sql(
                "ALTER SCHEMA public OWNER TO pg_database_owner; "
                "REVOKE ALL ON SCHEMA public FROM PUBLIC; "
                "GRANT CREATE, USAGE ON SCHEMA public TO pg_database_owner; "
                "GRANT USAGE ON SCHEMA public TO PUBLIC;"
            )
            connection.exec_driver_sql(applied_sql)
