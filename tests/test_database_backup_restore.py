"""Plan §14.3: prove the restore, not merely that a backup command succeeded."""
from __future__ import annotations

import os
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
    pipeline = (
        '  sed "s/__APP_ROLE__/${RUNTIME_ROLE}/g" "${GRANT_TEMPLATE}" \\\n'
        '    | psql --dbname="${DATABASE}" -v ON_ERROR_STOP=1 -f - >/dev/null'
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
            connection.exec_driver_sql(applied)
