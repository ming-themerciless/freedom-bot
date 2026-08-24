"""R35-09: the gate-rotation script is executed, not read.

Source-text assertions could not have caught what review did: `tr … | head -c 20`
exits 141 under `pipefail`, so the script could never have rotated anything. These
tests run it against a temporary filesystem with controlled stand-ins for `caddy`,
`systemctl`, `getent` and `id`, so no real `/etc`, service or credential is touched.

**Nothing here prints a secret.** Assertions compare and report *shapes* — lengths,
character classes, presence — never values.
"""

from __future__ import annotations

import os
import re
import signal
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "infra" / "staging" / "rotate-test-gate.sh"

VERIFIER_SHAPE = re.compile(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$")
PASSWORD_LINE = re.compile(r"^\s*password:\s*(\S+)\s*$", re.M)
FAKE_VERIFIER = "$2a$14$" + "x" * 53


def _write(path: Path, text: str, mode: int = 0o755) -> None:
    path.write_text(text)
    path.chmod(mode)


@pytest.fixture()
def host(tmp_path: Path):
    """A fake host: temporary /etc, stand-in commands, and an argv recorder."""
    bin_dir = tmp_path / "bin"
    etc = tmp_path / "etc"
    bin_dir.mkdir()
    etc.mkdir()
    argv_log = tmp_path / "argv.log"
    argv_log.write_text("")
    (etc / "Caddyfile").write_text("# fake\n")

    # `id -u` says root without the test being root; the script's own check stands.
    _write(bin_dir / "id", '#!/bin/sh\n[ "$1" = "-u" ] && echo 0 || exec /usr/bin/id "$@"\n')
    _write(bin_dir / "getent", '#!/bin/sh\nexit 0\n')
    # Post-commit housekeeping tools, each independently faultable (R35-19). They
    # delegate to the real binary unless the matching marker exists, so only the
    # step under test fails.
    for tool in ("mv", "find", "sort", "rm"):
        _write(
            bin_dir / tool,
            "#!/bin/sh\n"
            f'if [ -f "{tmp_path}/FAIL_{tool.upper()}" ] && [ -f "{tmp_path}/COMMITTED" ]; then\n'
            f'  echo "injected {tool} failure" >&2; exit 1\n'
            "fi\n"
            f'exec /usr/bin/{tool} "$@"\n',
        )
    _write(
        bin_dir / "chown",
        '#!/bin/sh\n'
        f'printf "chown %s\\n" "$*" >> "{argv_log}"\n'
        'exit 0\n',
    )  # no real ownership changes inside a tmpdir; the call is recorded instead
    _write(
        bin_dir / "systemctl",
        '#!/bin/sh\n'
        f'printf "systemctl %s\\n" "$*" >> "{argv_log}"\n'
        'case "$1" in\n'
        '  show) echo caddy ;;\n'
        f'  reload) [ -f "{tmp_path}/RELOAD_FAILS" ] && exit 1 ; : > "{tmp_path}/COMMITTED" ; exit 0 ;;\n'
        'esac\nexit 0\n',
    )
    _write(
        bin_dir / "caddy",
        '#!/bin/sh\n'
        f'printf "caddy %s\\n" "$*" >> "{argv_log}"\n'
        'case "$1" in\n'
        '  hash-password)\n'
        # Records only how many bytes arrived, never the bytes: a test rig that
        # persisted the plaintext would defeat the disk sweep below.
        f'    head -c 4096 | wc -c > "{tmp_path}/hash-stdin" 2>/dev/null\n'
        "    echo '" + FAKE_VERIFIER + "' ;;\n"

        f'  validate)\n'
        f'    if [ -f "{tmp_path}/BLOCK_VALIDATE" ]; then\n'
        f'      : > "{tmp_path}/AT_VALIDATE"\n'
        f'      while [ ! -f "{tmp_path}/RELEASE" ]; do sleep 0.05; done\n'
        f'    fi\n'
        f'    [ -f "{tmp_path}/VALIDATE_FAILS" ] && exit 1 ; exit 0 ;;\n'
        'esac\nexit 0\n',
    )

    fragment = etc / "freedom-blades-test.gate"
    environment = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "FREEDOM_GATE_FRAGMENT": str(fragment),
        "FREEDOM_GATE_CADDYFILE": str(etc / "Caddyfile"),
        "FREEDOM_GATE_USERNAME": "peter",
    }

    class Host:
        def __init__(self) -> None:
            self.tmp, self.etc, self.fragment = tmp_path, etc, fragment
            self.argv_log, self.env = argv_log, environment

        def run(self):
            return subprocess.run(
                ["bash", str(SCRIPT)], env=self.env, capture_output=True, text=True, timeout=60
            )

        def fail_validation(self): (tmp_path / "VALIDATE_FAILS").write_text("")
        def fail_reload(self): (tmp_path / "RELOAD_FAILS").write_text("")

        def run_until_validate(self):
            """Start the script and stop it, deterministically, mid-transaction.

            The fake `caddy validate` blocks and announces that it has been
            reached, so the test signals at a known point — the candidate is
            installed and nothing is committed — rather than guessing at a delay.
            """
            (tmp_path / "BLOCK_VALIDATE").write_text("")
            process = subprocess.Popen(
                ["bash", str(SCRIPT)], env=self.env,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                start_new_session=True,
            )
            marker = tmp_path / "AT_VALIDATE"
            for _ in range(400):
                if marker.exists():
                    return process
                if process.poll() is not None:
                    raise AssertionError(
                        "the script exited before reaching validation:\n"
                        + process.communicate()[1]
                    )
                time.sleep(0.02)
            process.kill()
            raise AssertionError("the script never reached validation")

        def signal_group(self, process, signal_number: int):
            # The whole group, as a terminal's Ctrl-C would: bash defers its trap
            # until the foreground child returns, so the blocking fake must be
            # signalled too or the test would depend on delivery timing.
            os.killpg(os.getpgid(process.pid), signal_number)
            return process.wait(timeout=30)

        @property
        def argv(self) -> str: return self.argv_log.read_text()

    return Host()


def test_the_happy_path_installs_validates_reloads_and_prints_once(host):
    result = host.run()

    assert result.returncode == 0, "the script did not complete"
    assert host.fragment.exists(), "no gate fragment was installed"
    assert "validate" in host.argv and "reload" in host.argv
    assert host.argv.index("validate") < host.argv.index("reload"), (
        "the configuration must be validated before the reload"
    )
    assert len(PASSWORD_LINE.findall(result.stdout)) == 1, "the password must be printed exactly once"


def test_generation_survives_a_finite_read(host):
    """The defect itself: `tr | head` exited 141 under pipefail and rotated nothing."""
    result = host.run()
    assert result.returncode != 141, "password generation died on a closed pipe"
    assert result.returncode == 0


def test_the_generated_password_meets_the_documented_policy(host):
    result = host.run()
    password = PASSWORD_LINE.search(result.stdout).group(1)
    # Shape only. The value is never asserted against, printed, or written down.
    assert len(password) == 20, f"expected a 20-character password, got {len(password)}"
    assert re.fullmatch(r"[A-Za-z0-9]+", password), "password left the documented alphabet"


def test_the_plaintext_never_reaches_a_child_process_argv(host):
    result = host.run()
    password = PASSWORD_LINE.search(result.stdout).group(1)

    assert password not in host.argv, (
        "the plaintext appeared in a child process command line, where any local "
        "user could read it from /proc"
    )
    assert "--plaintext" not in host.argv
    # It must have gone somewhere: prove the stdin path was actually used.
    received = (host.tmp / "hash-stdin")
    assert received.exists(), "the hashing command received no stdin"
    assert int(received.read_text().strip()) > 0, "the hashing command received empty stdin"


def test_the_plaintext_is_never_written_to_disk(host):
    result = host.run()
    password = PASSWORD_LINE.search(result.stdout).group(1)

    for path in host.tmp.rglob("*"):
        if not path.is_file() or path == host.argv_log:
            continue
        try:
            content = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        assert password not in content, f"the plaintext was written into {path.name}"


def test_the_fragment_contains_only_the_username_and_verifier(host):
    host.run()
    body = host.fragment.read_text()

    assert "basic_auth {" in body and "peter" in body
    verifier = body.split()[-2]
    assert VERIFIER_SHAPE.fullmatch(verifier), "the fragment's second field is not a verifier"
    assert body.count("\n") <= 4, "the fragment carries more than the gate it is for"
    for leak in ("password", "PLAINTEXT", "--plaintext"):
        assert leak not in body


def test_validation_failure_restores_the_previous_gate_and_prints_nothing(host):
    host.fragment.write_text("basic_auth {\n\tpeter previous-verifier\n}\n")
    host.fail_validation()

    result = host.run()

    assert result.returncode != 0
    assert "previous-verifier" in host.fragment.read_text(), "the working gate was lost"
    assert "reload" not in host.argv, "a failed validation must not reach the reload"
    assert not PASSWORD_LINE.search(result.stdout), "an unused password was printed"


def test_reload_failure_is_truthful_about_which_password_is_active(host):
    host.fragment.write_text("basic_auth {\n\tpeter previous-verifier\n}\n")
    host.fail_reload()

    result = host.run()

    assert result.returncode != 0
    assert "previous-verifier" in host.fragment.read_text()
    assert not PASSWORD_LINE.search(result.stdout), "an inactive password was printed as if live"
    assert "OLD password remains active" in result.stderr, (
        "the operator must be told which password is actually in force"
    )


def test_a_first_installation_that_fails_leaves_no_gate_behind(host):
    """No prior fragment: failure must not leave an unvalidated one in place."""
    assert not host.fragment.exists()
    host.fail_validation()

    result = host.run()

    assert result.returncode != 0
    assert not host.fragment.exists(), "a fragment survived a failed first installation"


def test_no_replacement_or_temporary_file_is_left_behind(host):
    for prepare in (lambda: None, host.fail_validation):
        for stale in host.etc.glob("*.new-*"):
            stale.unlink()
        prepare()
        host.run()
        assert not list(host.etc.glob("*.new-*")), "a staged replacement was left behind"


def test_only_one_generation_of_replaced_gates_is_retained(host):
    host.fragment.write_text("basic_auth {\n\tpeter previous-verifier\n}\n")
    for old in range(3):
        (host.etc / f"freedom-blades-test.gate.replaced-2026010{old}T000000Z").write_text("old\n")

    host.run()

    retained = list(host.etc.glob("freedom-blades-test.gate.replaced-*"))
    assert len(retained) == 1, (
        f"{len(retained)} historical verifiers retained; each is credential material"
    )


# ---------------------------------------------------------------------------
# R35-13 / R35-15: interruption between installation and commit
# ---------------------------------------------------------------------------
# The defect review caught: after the atomic `mv`, a signal left an unvalidated
# verifier on disk whose password had never been shown. A later unrelated Caddy
# reload would then have activated a gate nobody knew the password to.

PREVIOUS_GATE = "basic_auth {\n\tpeter $2a$14$" + "p" * 53 + "\n}\n"


@pytest.mark.parametrize(
    "signal_number,expected_status",
    [(signal.SIGINT, 130), (signal.SIGTERM, 143)],
    ids=["sigint", "sigterm"],
)
def test_interruption_before_commit_restores_the_previous_gate(
    host, signal_number, expected_status
):
    host.fragment.write_text(PREVIOUS_GATE)

    process = host.run_until_validate()
    # The candidate really is installed at this point; otherwise the test proves
    # nothing about rollback.
    assert host.fragment.read_text() != PREVIOUS_GATE, (
        "the candidate was not installed yet, so this signal tests nothing"
    )
    status = host.signal_group(process, signal_number)

    assert host.fragment.read_text() == PREVIOUS_GATE, (
        "an uncommitted verifier survived the interruption; a later reload would "
        "have activated a gate whose password was never shown"
    )
    assert status in (expected_status, -signal_number), f"unexpected status {status}"
    assert not list(host.etc.glob("*.candidate.*"))
    assert not list(host.etc.glob("*.rollback.*"))
    assert not list(host.etc.glob("*.restoring.*"))


@pytest.mark.parametrize(
    "signal_number", [signal.SIGINT, signal.SIGTERM], ids=["sigint", "sigterm"]
)
def test_interruption_with_no_previous_gate_returns_to_absent(host, signal_number):
    assert not host.fragment.exists()

    process = host.run_until_validate()
    assert host.fragment.exists(), "the candidate was not installed yet"
    host.signal_group(process, signal_number)

    assert not host.fragment.exists(), (
        "an uncommitted verifier was left behind where there had been no gate at all"
    )
    assert not list(host.etc.glob("*.candidate.*"))
    assert not list(host.etc.glob("*.rollback.*"))


@pytest.mark.parametrize(
    "signal_number", [signal.SIGINT, signal.SIGTERM], ids=["sigint", "sigterm"]
)
def test_interruption_prints_no_password(host, signal_number):
    host.fragment.write_text(PREVIOUS_GATE)
    process = host.run_until_validate()
    host.signal_group(process, signal_number)
    stdout, _ = process.communicate()
    assert not PASSWORD_LINE.search(stdout or ""), "a password was printed for a gate never activated"


def test_interruption_creates_no_retained_generation(host):
    host.fragment.write_text(PREVIOUS_GATE)
    process = host.run_until_validate()
    host.signal_group(process, signal.SIGINT)
    assert not list(host.etc.glob("*.replaced-*")), (
        "an interrupted attempt left a historical verifier behind"
    )


# ---------------------------------------------------------------------------
# R35-14: failure paths must not accumulate verifier material
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("failure", ["validation", "reload"], ids=["validate", "reload"])
def test_repeated_failures_accumulate_no_verifier_backups(host, failure):
    host.fragment.write_text(PREVIOUS_GATE)
    getattr(host, f"fail_{'validation' if failure == 'validation' else 'reload'}")()

    for _ in range(3):
        result = host.run()
        assert result.returncode != 0

    assert not list(host.etc.glob("*.replaced-*")), (
        "failed attempts left historical verifiers behind, one per attempt"
    )
    assert not list(host.etc.glob("*.rollback.*"))
    assert not list(host.etc.glob("*.candidate.*"))
    assert host.fragment.read_text() == PREVIOUS_GATE, "the working gate was lost"


def test_a_successful_rotation_retains_exactly_one_generation(host):
    host.fragment.write_text(PREVIOUS_GATE)

    result = host.run()

    assert result.returncode == 0
    retained = list(host.etc.glob("*.replaced-*"))
    assert len(retained) == 1, f"{len(retained)} generations retained, expected exactly one"
    assert not list(host.etc.glob("*.rollback.*"))


def test_a_pre_existing_backup_survives_a_rollback_that_still_needs_it(host):
    """Cleanup must not mistake a retained generation for transaction scratch."""
    host.fragment.write_text(PREVIOUS_GATE)
    keeper = host.etc / "freedom-blades-test.gate.replaced-20260101T000000Z"
    keeper.write_text("basic_auth {\n\tpeter $2a$14$" + "k" * 53 + "\n}\n")
    host.fail_validation()

    assert host.run().returncode != 0

    assert keeper.exists(), "rollback destroyed a retained recovery generation"
    assert host.fragment.read_text() == PREVIOUS_GATE


def test_a_committed_rotation_is_not_rolled_back_by_exit_cleanup(host):
    host.fragment.write_text(PREVIOUS_GATE)

    result = host.run()

    assert result.returncode == 0
    assert host.fragment.read_text() != PREVIOUS_GATE, (
        "exit cleanup rolled back a rotation that had already been committed"
    )


def test_ownership_is_applied_to_the_candidate_through_the_seam(host):
    """The candidate is owned and moded *before* it becomes the gate."""
    host.run()

    chown_calls = [line for line in host.argv.splitlines() if line.startswith("chown ")]
    assert chown_calls, "ownership was never applied"
    assert any("candidate" in call for call in chown_calls), (
        "ownership must be applied to the candidate before it is moved into place, "
        "so the gate is never briefly readable by the wrong account"
    )
    assert host.fragment.read_text().startswith("basic_auth {")


# ---------------------------------------------------------------------------
# R35-19: nothing fallible may stand between a confirmed reload and the password
# ---------------------------------------------------------------------------
# The defect: `STATE=committed` disabled rollback, then the script did retention
# work — a rename, an enumeration, a sort, a removal — and only then printed the
# password. Under `set -e` any of those exited with the new gate already serving
# and its plaintext never shown, locking the operator out with no known password.


@pytest.mark.parametrize("tool", ["mv", "find", "sort", "rm"], ids=lambda t: f"{t}-fails")
def test_post_commit_housekeeping_failure_still_shows_the_active_password(host, tool):
    host.fragment.write_text(PREVIOUS_GATE)
    (host.tmp / f"FAIL_{tool.upper()}").write_text("")

    result = host.run()

    printed = PASSWORD_LINE.findall(result.stdout)
    assert len(printed) == 1, (
        f"a post-commit {tool} failure cost the operator the active password; "
        "the gate is serving and nobody knows how to get in"
    )
    assert "is active" in result.stdout
    # The gate that is actually serving is the new one, and it is well-formed.
    body = host.fragment.read_text()
    assert body.startswith("basic_auth {")
    assert VERIFIER_SHAPE.fullmatch(body.split()[-2])


@pytest.mark.parametrize("tool", ["mv", "find", "sort", "rm"], ids=lambda t: f"{t}-fails")
def test_post_commit_housekeeping_failure_is_warned_about_truthfully(host, tool):
    """R35-28. A swallowed failure is worse than a noisy one.

    `find` and `sort` ran inside a pipeline whose status nobody inspected, so their
    failures were silently ignored: the operator was told everything was fine while
    superseded verifier generations piled up in the gate directory. Each step is now
    a controlled operation with its own status, and each one that fails is named.
    """
    host.fragment.write_text(PREVIOUS_GATE)
    # Two superseded generations, so pruning has real work: without them `rm` is
    # never reached and the case would assert a warning for an operation that
    # correctly never ran.
    for old in range(2):
        (host.etc / f"freedom-blades-test.gate.replaced-2026010{old}T000000Z").write_text("old\n")
    (host.tmp / f"FAIL_{tool.upper()}").write_text("")

    result = host.run()
    password = PASSWORD_LINE.search(result.stdout).group(1)
    combined = result.stdout + result.stderr

    assert "WARNING: post-commit housekeeping did not complete" in result.stderr, (
        f"a failing {tool} was swallowed; the operator was told nothing"
    )
    assert "IS active and correct" in result.stderr, (
        "the warning must say the displayed password is still the live one"
    )
    assert "$2a$" not in combined, "a verifier was printed"
    assert combined.count(password) == 1, "the password was printed more than once"
    assert result.returncode == 0, (
        "a tidy-up problem must not be reported as a failed rotation"
    )
    # The committed gate is untouched by a housekeeping fault.
    assert host.fragment.read_text().split()[-2].startswith("$2a$")


def test_post_commit_failure_does_not_roll_back_the_committed_gate(host):
    """Rollback is a no-op once committed, even when housekeeping fails."""
    host.fragment.write_text(PREVIOUS_GATE)
    (host.tmp / "FAIL_MV").write_text("")

    host.run()

    assert host.fragment.read_text() != PREVIOUS_GATE, (
        "a housekeeping failure rolled back a gate Caddy had already reloaded"
    )
