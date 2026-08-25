"""The existing worker environment file is confirmed completely, or refused.

Codex finding C3, 2026-08-25. `infra/staging/setup-portal-host.sh` promises never
to overwrite an existing environment file, and the first version of that promise
for `worker.env` read the last `WORKER_ENABLED=` assignment and accepted the file
if it said `true`. For this particular file that is the wrong shape of check, and
the reason is the precedence rule that caused F5 pointing the other way: the worker
unit reads this file **after** the shared portal file, so every assignment in it
overrides the portal's. This passed:

    WEB_DATABASE_URL=unexpected-database
    WORKER_ARTIFACT_ROOT=/unexpected/path
    WORKER_ENABLED=true

— a silent redirection of the worker's database and artifact store, adopted by a
script that reported success. Ownership, mode and symlink shape were not checked at
all, so a file the service account could rewrite was equally acceptable.

These cases **execute the installer's own validation**. `worker_env_file_problem`
lives in `infra/staging/lib/worker-env-file.sh` for exactly that reason: the
previous regression asserted that the creation statements *existed in the script
text*, which is not the same as running the check the operator's host will run.

The expected owner, group and mode are parameters of the function, so this suite
can exercise ownership refusal without being root and without creating a file it
could not clean up.
"""

from __future__ import annotations

import grp
import os
import pwd
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "infra" / "staging" / "lib" / "worker-env-file.sh"
CONFORMING = "WORKER_ENABLED=true\n"


def _validate(path: Path, *, owner: str | None = None, group: str | None = None, mode: str = "640"):
    """Run `worker_env_file_problem` in bash, as the installer runs it."""
    owner = owner if owner is not None else pwd.getpwuid(os.getuid()).pw_name
    group = group if group is not None else grp.getgrgid(os.getgid()).gr_name
    completed = subprocess.run(
        [
            "bash",
            "-c",
            f'. "$1"; worker_env_file_problem "$2" "$3" "$4" "$5"',
            "bash",
            str(LIBRARY),
            str(path),
            owner,
            group,
            mode,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def _write(path: Path, content: str, mode: int = 0o640) -> Path:
    path.write_text(content)
    path.chmod(mode)
    return path


@pytest.fixture()
def worker_env(tmp_path) -> Path:
    return _write(tmp_path / "worker.env", CONFORMING)


# ---------------------------------------------------------------------------
# Accepted
# ---------------------------------------------------------------------------


def test_the_file_the_installer_writes_is_the_file_it_accepts(worker_env, tmp_path):
    """The one shape that passes, and it is the installer's own output.

    Written here by the same `printf` the installer uses, so the creation branch
    and the confirmation branch cannot drift into disagreeing about what
    conformance means — a re-run on a host the installer itself provisioned would
    be the first thing to fail if they did.
    """
    written = tmp_path / "installer-written.env"
    subprocess.run(
        ["bash", "-c", 'printf %s "$1" > "$2"', "bash", CONFORMING, str(written)],
        check=True,
    )
    written.chmod(0o640)

    assert _validate(worker_env) == (0, "")
    assert _validate(written) == (0, "")


# ---------------------------------------------------------------------------
# Refused — content
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content,why",
    [
        pytest.param(
            "WEB_DATABASE_URL=unexpected-database\n"
            "WORKER_ARTIFACT_ROOT=/unexpected/path\n"
            "WORKER_ENABLED=true\n",
            "C3's example: extra assignments that override the shared portal file",
            id="extra-variables",
        ),
        pytest.param(
            "WORKER_ENABLED=false\nWORKER_ENABLED=true\n",
            "duplicates whose last parsed value is true",
            id="duplicate-assignments",
        ),
        pytest.param(
            "# the worker's override\nWORKER_ENABLED=true\n",
            "a comment is not part of the permitted content",
            id="comment",
        ),
        pytest.param("WORKER_ENABLED=false\n", "F5 reinstated", id="false"),
        pytest.param("WORKER_ENABLED=TRUE\n", "not the value systemd will read", id="wrong-case"),
        pytest.param("", "an empty file sets nothing", id="empty"),
        pytest.param("WORKER_ENABLED=true", "no final newline", id="no-trailing-newline"),
        pytest.param("WORKER_ENABLED=true\n\n", "a second, blank line", id="trailing-blank-line"),
        pytest.param("  WORKER_ENABLED=true\n", "leading whitespace", id="indented"),
    ],
)
def test_content_that_is_not_exactly_one_permitted_assignment_is_refused(
    tmp_path, content, why
):
    """Byte-exact, because every extra byte in this file is an unreviewed override."""
    status, problem = _validate(_write(tmp_path / "worker.env", content))

    assert status == 1, f"accepted a file with {why}"
    assert "exactly one line" in problem


def test_the_refusal_explains_the_override_hazard_rather_than_only_the_mismatch(tmp_path):
    """The operator has to know *why* an extra line is not a harmless extra line."""
    _, problem = _validate(
        _write(tmp_path / "worker.env", "WEB_DATABASE_URL=elsewhere\nWORKER_ENABLED=true\n")
    )

    assert "after the shared portal file" in problem
    assert "overrides" in problem


# ---------------------------------------------------------------------------
# Refused — shape, ownership and mode
# ---------------------------------------------------------------------------


def test_a_symlink_is_refused_even_when_it_resolves_to_a_conforming_file(
    tmp_path, worker_env
):
    """What the path *is*, not what it points at today.

    systemd reads this file as root. A link is a file whose content is decided
    somewhere else, by whoever can write the link's target — or the link.
    """
    link = tmp_path / "link.env"
    link.symlink_to(worker_env)

    status, problem = _validate(link)

    assert status == 1
    assert "symbolic link" in problem


def test_a_directory_or_other_non_regular_file_is_refused(tmp_path):
    directory = tmp_path / "worker.env"
    directory.mkdir()

    status, problem = _validate(directory)

    assert status == 1
    assert "not a regular file" in problem


def test_a_missing_file_is_refused_rather_than_treated_as_conforming(tmp_path):
    status, problem = _validate(tmp_path / "absent.env")

    assert status == 1
    assert "does not exist" in problem


@pytest.mark.parametrize("mode", [0o644, 0o660, 0o666, 0o600, 0o444])
def test_any_mode_but_the_documented_one_is_refused(tmp_path, mode):
    """`0640` exactly. A group- or world-writable file is the sharp case: the
    service account could then rewrite the configuration it is about to be given.
    """
    status, problem = _validate(_write(tmp_path / "worker.env", CONFORMING, mode))

    assert status == 1
    assert "owned/permissioned" in problem
    assert f"{mode & 0o777:o}" in problem


def test_an_unexpected_owner_or_group_is_refused(worker_env):
    """Exercised by asking for a group the file demonstrably does not have.

    The installer asks for `root` and the service group; this suite is not root, so
    it states an expectation the file fails instead of manufacturing one it cannot
    create. The property under test is the comparison, not the identity.
    """
    actual_group = grp.getgrgid(os.getgid()).gr_name

    status, problem = _validate(worker_env, group=f"{actual_group}-not-this-one")

    assert status == 1
    assert "owned/permissioned" in problem
    assert "reconfigure itself" in problem


# ---------------------------------------------------------------------------
# The installer uses it
# ---------------------------------------------------------------------------


def test_the_installer_validates_the_existing_file_with_this_function(tmp_path):
    """The library is only worth testing if the script actually calls it.

    Asserted on the call, its arguments and the refusal path, because a validation
    the installer sources and then ignores would leave every case above passing
    while the host kept adopting whatever `worker.env` it found.
    """
    installer = (ROOT / "infra" / "staging" / "setup-portal-host.sh").read_text()

    assert '. "$WORKER_ENV_LIBRARY"' in installer, "the installer must source the library"
    assert 'worker_env_file_problem "$WORKER_ENV_FILE" root "$SERVICE_GROUP" 640' in installer, (
        "the installer must validate the existing file against root, the service "
        "group and mode 0640"
    )
    assert "This script will not overwrite it." in installer, (
        "a nonconforming existing file must refuse with operator action, not be repaired"
    )
    # The weaker predecessor, named so it cannot quietly return.
    assert "sed -n 's/^[[:space:]]*WORKER_ENABLED=//p'" not in installer, (
        "the last-assignment-wins check was C3; it must not come back"
    )
