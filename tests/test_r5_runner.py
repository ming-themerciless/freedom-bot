"""Focused tests for the R-5 successor R4 runner (C-P5.0-R5-RP11-FRESH-D1).

No test contacts `oracle-test`, downloads anything or executes an R-5 block.
Every block is answered by `FakeHost`, which returns scripted transcripts and
records each call. One test drives the real subprocess transport with a
harmless script that is not an R-5 block.

The derivation tests prove the resources are R3's §6 blocks: they extract each
block from the accepted R3 assignment, pinned below by digest and length, apply
exactly R3 §6.0's substitutions except `<RUN>`, and require byte equality.
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
import shlex
import shutil
import sys
from pathlib import Path
from typing import Callable

import pytest

ROOT = Path(__file__).resolve().parents[1]

_SPEC = importlib.util.spec_from_file_location("r5run", ROOT / "tools/r5_runner/r5run.py")
assert _SPEC is not None and _SPEC.loader is not None
R = importlib.util.module_from_spec(_SPEC)
sys.modules["r5run"] = R
_SPEC.loader.exec_module(R)

R3 = ROOT / "docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r3.md"
R3_SHA256 = "039f68fbe7fc0f572b31879087a2e9d91e2a6b17892a4fca075af1c81b767bac"
R3_LENGTH = 108733
R4 = ROOT / R.ASSIGNMENT
PY = "/opt/freedom-blades/runtime/venv-web/bin/python"

#: R3 §6's sixteen blocks in document order, and the resource that holds each.
BLOCK_RESOURCES = (
    "s01.sh", "s02.sh", "s03.sh", "s04a.sh", "s04b-start.sh", "s04b-end.sh",
    "s04c.sh", "s04d.sh", "s05.sh", "s06-s07.sh", "s08.sh", "s09.sh", "s10.sh",
    "s11.sh", "s12-start.sh", "s12-end.sh",
)
SYNC_RESOURCE = "s04b-sync.argv"
RUN = "p5-r5-fresh-20261004T000000Z-0123abcd"
STAMP = "2026-10-04T00:00:00Z"
END_STAMP = "2026-10-04T01:00:00Z"


# ---------------------------------------------------------------------------
# Derivation from R3 (also used once to generate the resources)
# ---------------------------------------------------------------------------


def r3_text() -> str:
    data = R3.read_bytes()
    assert hashlib.sha256(data).hexdigest() == R3_SHA256 and len(data) == R3_LENGTH
    return data.decode("utf-8")


def r3_blocks(text: str) -> list[tuple[str, str]]:
    """(invoking line, body) for every `<<'R5BLOCK'` block, in document order."""
    lines = text.splitlines(keepends=True)
    blocks, index = [], 0
    while index < len(lines):
        if lines[index].endswith("-s <<'R5BLOCK'\n"):
            end = lines.index("R5BLOCK\n", index + 1)
            blocks.append((lines[index].rstrip("\n"), "".join(lines[index + 1 : end])))
            index = end
        index += 1
    return blocks


def appendix(text: str, letter: str) -> str:
    after = text[text.index(f"## Appendix {letter} ") :]
    start = after.index("```text\n") + len("```text\n")
    return after[start : after.index("```\n", start)]


def s16_program(s01: str) -> str:
    """The single-quoted S1.6 program, including its quotes (R3 §6.0)."""
    marker = "python3 -I -B -c 'import hashlib,os,sys"
    start = s01.index(marker) + len("python3 -I -B -c ")
    return s01[start : s01.index(" <<'LIST'", start)]


def substitute(body: str, text: str, s01: str) -> str:
    """R3 §6.0's substitutions, all of them except `<RUN>`."""
    a, b = appendix(text, "A"), appendix(text, "B")
    assert a.count("\n") == 28 and b.count("\n") == 28
    return (
        body.replace("<APPENDIX A>\n", a)
        .replace("<APPENDIX B>\n", b)
        .replace("'<the S1.6 program, verbatim>'", s16_program(s01))
        .replace("<PY>", PY)
        .replace("<HANDBACK>", R.HANDBACK)
    )


def derived_resources() -> dict[str, bytes]:
    text = r3_text()
    blocks = r3_blocks(text)
    assert len(blocks) == len(BLOCK_RESOURCES)
    s01 = blocks[0][1]
    derived = {
        name: substitute(body, text, s01).encode("utf-8")
        for name, (_opener, body) in zip(BLOCK_RESOURCES, blocks)
    }
    derived[SYNC_RESOURCE] = ("\n".join(r3_sync_argv(text)) + "\n").encode("utf-8")
    return derived


def r3_sync_argv(text: str) -> list[str]:
    start = text.index("rsync -avz --delete \\\n")
    return shlex.split(text[start : text.index("\n```", start)].replace("\\\n", " "))


def resource(name: str) -> bytes:
    return (ROOT / R.RESOURCE_DIRECTORY / name).read_bytes()


@pytest.mark.parametrize("name", BLOCK_RESOURCES + (SYNC_RESOURCE,))
def test_each_resource_is_its_r3_block_with_only_the_6_0_substitutions(name: str) -> None:
    assert resource(name) == derived_resources()[name]


def test_the_plan_uses_r3s_invoking_process_for_every_block() -> None:
    openers = [opener for opener, _body in r3_blocks(r3_text())]
    by_resource = {Path(i.resource).name: i for i in R.FULL_PLAN}
    for name, opener in zip(BLOCK_RESOURCES, openers):
        argv = R.REMOTE_BASH if by_resource[name].transport is R.Transport.REMOTE else R.LOCAL_BASH
        assert " ".join(argv) + " <<'R5BLOCK'" == opener
    assert by_resource[SYNC_RESOURCE].transport is R.Transport.SYNC


def test_the_plan_order_is_r3s_order() -> None:
    scopes = [i.scope for i in R.FULL_PLAN]
    assert scopes == [
        "S1", "S2", "S3", "S4a", "S4b.start", "S4b.sync", "S4b.end", "S4c", "S4d",
        "S5", "S6-S7", "S8", "S9", "S10", "S11", "S12.start", "S12.end",
    ]
    names = [Path(i.resource).name for i in R.FULL_PLAN if i.kind is not R.Kind.SYNC]
    assert names == list(BLOCK_RESOURCES)


def test_the_r4_assignment_displays_every_resource_exactly() -> None:
    """R4 shows each block's text; with §6.0's substitutions it is the resource."""
    text, r3 = R4.read_text(encoding="utf-8"), r3_text()
    s01 = r3_blocks(r3)[0][1]
    shown = re.findall(r"Resource: `tools/r5_runner/blocks/([^`]+)`[^\n]*\n\n```bash\n(.*?)```\n", text, re.S)
    assert [name for name, _ in shown] == list(BLOCK_RESOURCES)
    for name, body in shown:
        assert substitute(body, r3, s01).encode("utf-8") == resource(name), name
    argv = re.search(r"Resource: `tools/r5_runner/blocks/s04b-sync.argv`[^\n]*\n\n```text\n(.*?)```\n", text, re.S)
    assert argv is not None and argv.group(1).encode("utf-8") == resource(SYNC_RESOURCE)


def test_resources_have_no_terminal_heredoc_background_retry_or_cleanup_path() -> None:
    for name in BLOCK_RESOURCES + (SYNC_RESOURCE,):
        text = resource(name).decode("utf-8")
        assert "R5BLOCK" not in text
        assert not re.search(r"(?m)&\s*$|\s&\s|\bnohup\b|\bdisown\b|\bsleep\b|\bwait\b", text), name
        assert not re.search(r"\brm\s|\brmdir\b|\bretry\b|\bsudo\b|\bapt(-get)?\b", text), name
        assert "<RUN>" in text or name in {"s01.sh", "s03.sh", "s04b-start.sh", "s04b-end.sh", "s04c.sh", "s12-start.sh", "s12-end.sh"}
        for placeholder in ("<PY>", "<APPENDIX A>", "<APPENDIX B>", "<HANDBACK>", "<the S1.6 program"):
            assert placeholder not in text, (name, placeholder)


def test_runner_source_has_no_interactive_or_shell_path() -> None:
    source = (ROOT / R.RUNNER).read_text(encoding="utf-8")
    for forbidden in ("sys.stdin", "input(", "shell=True", "os.system", "import pty", "time.sleep", "<<'"):
        assert forbidden not in source, forbidden


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def runner_sha256(root: Path = ROOT) -> str:
    return hashlib.sha256((root / R.RUNNER).read_bytes()).hexdigest()


def test_pins_cover_every_resource_and_this_test_with_exact_identities() -> None:
    expected = {f"{R.RESOURCE_DIRECTORY}/{n}" for n in BLOCK_RESOURCES + (SYNC_RESOURCE,)}
    expected.add("tests/test_r5_runner.py")
    assert set(R.PINS) == expected
    for relative, (digest, length) in R.PINS.items():
        data = (ROOT / relative).read_bytes()
        assert (hashlib.sha256(data).hexdigest(), len(data)) == (digest, length), relative
    identity = R.verify_identity(ROOT, runner_sha256())
    assert identity.runner.path == R.RUNNER
    assert set(identity.resources) == {i.resource for i in R.FULL_PLAN}


def copy_controlled(tmp_path: Path) -> Path:
    for relative in [R.RUNNER, *R.PINS]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return tmp_path


def test_an_altered_command_resource_is_refused(tmp_path: Path) -> None:
    root = copy_controlled(tmp_path)
    path = root / R.RESOURCE_DIRECTORY / "s05.sh"
    path.write_bytes(path.read_bytes().replace(b"--snapshot 20261001T000000Z", b"--snapshot 20261002T000000Z"))
    with pytest.raises(R.Refusal, match="s05.sh"):
        R.verify_identity(root, runner_sha256(root))


def test_an_altered_runner_is_refused(tmp_path: Path) -> None:
    root = copy_controlled(tmp_path)
    original = runner_sha256(root)
    with open(root / R.RUNNER, "a", encoding="utf-8") as handle:
        handle.write("# altered\n")
    with pytest.raises(R.Refusal, match="r5run.py has SHA-256"):
        R.verify_identity(root, original)


def test_an_altered_focused_test_is_refused(tmp_path: Path) -> None:
    root = copy_controlled(tmp_path)
    with open(root / "tests/test_r5_runner.py", "a", encoding="utf-8") as handle:
        handle.write("# altered\n")
    with pytest.raises(R.Refusal, match="test_r5_runner.py"):
        R.verify_identity(root, runner_sha256(root))


def test_an_extra_or_linked_resource_is_refused(tmp_path: Path) -> None:
    root = copy_controlled(tmp_path)
    (root / R.RESOURCE_DIRECTORY / "s13.sh").write_text("echo extra\n")
    with pytest.raises(R.Refusal, match="extra"):
        R.verify_identity(root, runner_sha256(root))
    (root / R.RESOURCE_DIRECTORY / "s13.sh").unlink()
    target = root / R.RESOURCE_DIRECTORY / "s09.sh"
    target.rename(root / "s09.sh")
    target.symlink_to(root / "s09.sh")
    with pytest.raises(R.Refusal, match="not a regular file"):
        R.verify_identity(root, runner_sha256(root))


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["--executor", "Codex", "--attest-independence", "--expect-runner-sha256", "0" * 64],
        ["--executor", "Gemini", "--expect-runner-sha256", "0" * 64],
        ["--executor", "Gemini", "--attest-independence", "--expect-runner-sha256", "XYZ"],
        ["--executor", "Gemini", "--attest-independence", "--expect-runner-sha256", "0" * 64, "--retry"],
    ],
)
def test_only_the_assignments_invocation_is_accepted(argv: list[str]) -> None:
    with pytest.raises(R.Refusal):
        R.parse_arguments(argv)


def test_the_runner_refuses_without_isolated_bytecode_free_python() -> None:
    class Flags:
        isolated = 0
        dont_write_bytecode = 1

    with pytest.raises(R.Refusal, match="-I -B"):
        R.check_interpreter(Flags(), (3, 12))
    # Under pytest the interpreter is not isolated, so main refuses before
    # reading arguments, verifying files or touching any host.
    assert R.main(["--executor", "Gemini", "--attest-independence", "--expect-runner-sha256", "0" * 64]) == R.EXIT_REFUSED


def test_run_identifiers_are_fresh_and_never_a_consumed_one() -> None:
    import datetime

    now = datetime.datetime(2026, 10, 4, tzinfo=datetime.timezone.utc)
    assert R.new_run_id(now, "0123abcd") == RUN
    with pytest.raises(R.Refusal):
        R.new_run_id(datetime.datetime(2026, 10, 3, 19, 14, tzinfo=datetime.timezone.utc), "9c3f71e2")


# ---------------------------------------------------------------------------
# A simulated host
# ---------------------------------------------------------------------------

GIT_STATUS = " M docs/review/a.md\n?? docs/review/b.md\n"
CC1CHECK = [
    f"baseline_sha256: {R.BASELINE_SHA256}",
    f"actual_sha256:   {R.BASELINE_SHA256}",
    "is_identical:    True",
    "total_diffs:     0",
    "verdict:         PASS",
]
OBSERVATION = {
    "uname": ["Linux 7.0.0-31-generic #31 SMP x86_64"],
    "cpuinfo-first-processor": ["vendor_id\t: AuthenticAMD", "model name\t: AMD EPYC 7551 32-Core Processor"],
    "bwrap-version": ["bubblewrap 0.11.1"],
    "bwrap-sha256": ["0" * 64 + "  /usr/bin/bwrap"],
}
#: Lines a passing block prints immediately before a status line.
OUTPUT_BEFORE = {
    "S1.2 git-rev-parse": ["9cad3ded6479fb7b423b35c1d815fbfc7e48aaaa"],
    "S1.3 git-status": GIT_STATUS.splitlines()
    + ["git_status_lines=2", "git_status_sha256=" + hashlib.sha256(GIT_STATUS.encode()).hexdigest()],
    "S1.4 repository-state": ["repository_state=clean"],
    "S3.1 qualification": [
        "HA-1 kernel_release=7.0.0-31-generic",
        "HA-2 model_names=AMD EPYC 7551 32-Core Processor",
        "HA-1 qualifies=yes",
        "HA-2 qualifies=yes",
        "HA-3 qualifies=no (version-only differences do not qualify; section 4.2)",
    ],
    "S5.8 root-stat": [f"755 gemini:gemini /var/tmp/{RUN}-root"],
    "S9.1 cc1v-length": ["5120"],
    "S9.4 display": CC1CHECK,
    "S10.4 pytest-counts": ["tests=12 failures=0 errors=0 skipped=0"],
}
for step in ("S2.2", "S11.8"):
    OUTPUT_BEFORE[f"{step} uname"] = OBSERVATION["uname"]
for step in ("S2.5", "S11.9"):
    OUTPUT_BEFORE[f"{step} cpuinfo-first-processor"] = OBSERVATION["cpuinfo-first-processor"]
for step in ("S2.6", "S11.10"):
    OUTPUT_BEFORE[f"{step} bwrap-version"] = OBSERVATION["bwrap-version"]
for step in ("S2.8", "S11.11"):
    OUTPUT_BEFORE[f"{step} bwrap-sha256"] = OBSERVATION["bwrap-sha256"]

CLOSING_RECORD = (
    "\n## Closing record (written by the S12.end block)\n\n~~~text\n"
    "S12.end.3 open-record exit=0\n"
    f"S12.end end_utc={END_STAMP}\nRUN.end end_utc={END_STAMP}\n"
    "S12.end.4 date exit=0\n~~~\n"
)


def invocation(scope: str):
    return next(i for i in R.FULL_PLAN if i.scope == scope)


def transcript(scope: str, *, fail_at: str | None = None, status: int = 1, output: dict | None = None) -> R.Completed:
    """What R3's block for `scope` prints, passing or stopping at `fail_at`."""
    inv = invocation(scope)
    if inv.kind is R.Kind.SYNC:
        if fail_at is not None:
            return R.Completed(status, b"sending incremental file list\ndocs/screenshots/private.png\n", b"rsync error: private.png\n")
        return R.Completed(
            0,
            b"sending incremental file list\ndocs/screenshots/private.png\n\n"
            b"sent 10 bytes  received 20 bytes  30.00 bytes/sec\ntotal size is 40  speedup is 1.33\n",
            b"",
        )
    labels = R.expected_labels(resource(Path(inv.resource).name))
    before = dict(OUTPUT_BEFORE, **(output or {}))
    lines: list[str] = []
    for label in labels:
        if label == f"{scope}.start date":
            if scope == "S1":
                lines.append(f"RUN.start start_utc={STAMP}")
            lines.append(f"{scope}.start start_utc={STAMP}")
        if inv.kind is R.Kind.STAMP and label == f"{scope} date":
            lines.append(f"{scope} {'end_utc' if scope.endswith('.end') else 'start_utc'}={STAMP}")
        if label == "S12.end.2 handback-body-present":
            lines.append("handback_body=present")
        lines += before.get(label, [])
        if label == fail_at:
            lines.append(f"{label} exit={status}")
            break
        lines.append(f"{label} exit=0")
    else:
        lines.append(f"{scope} block exit=0")
        status = 0
    if inv.kind is R.Kind.STEP:
        lines += [f"{scope}.end end_utc={STAMP}", f"{scope}.end date exit=0", f"{scope} final exit={status}"]
    return R.Completed(status, ("\n".join(lines) + "\n").encode(), b"")


Answer = Callable[["FakeHost", bytes | None], R.Completed]


class FakeHost:
    """Scripted answers per scope; S12.end appends the closing record like R3's block."""

    def __init__(self, root: Path, answers: dict[str, R.Completed | Answer] | None = None) -> None:
        self.root = root
        self.answers = answers or {}
        self.calls: list[tuple[str, tuple[str, ...], bytes | None]] = []
        self.handback_after_close: bytes | None = None

    @property
    def scopes(self) -> list[str]:
        return [scope for scope, _argv, _stdin in self.calls]

    def run(self, scope: str, argv, stdin: bytes | None) -> R.Completed:
        self.calls.append((scope, tuple(argv), stdin))
        answer = self.answers.get(scope)
        if callable(answer):
            return answer(self, stdin)
        if answer is not None:
            return answer
        if scope == "S12.end":
            return self.close()
        return transcript(scope)

    def close(self) -> R.Completed:
        path = self.root / R.HANDBACK
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(CLOSING_RECORD)
        self.handback_after_close = path.read_bytes()
        return transcript("S12.end")


@pytest.fixture
def identity():
    return R.verify_identity(ROOT, runner_sha256())


def make_runner(tmp_path: Path, identity, host: FakeHost) -> R.Runner:
    (tmp_path / R.HANDBACK).parent.mkdir(parents=True, exist_ok=True)
    return R.Runner(root=tmp_path, identity=identity, executor=host, run_id=RUN, interpreter="python3 test")


def run(tmp_path: Path, identity, answers=None) -> tuple[R.RunResult, FakeHost, str]:
    host = FakeHost(tmp_path, answers)
    result = make_runner(tmp_path, identity, host).run()
    return result, host, (tmp_path / R.HANDBACK).read_text(encoding="utf-8")


ALL = [i.scope for i in R.FULL_PLAN]
CLOSE = ["S12.start", "S12.end"]


def through(scope: str) -> list[str]:
    return ALL[: ALL.index(scope) + 1]


# ---------------------------------------------------------------------------
# Order, progression and the first terminal condition
# ---------------------------------------------------------------------------


def test_a_complete_run_attempts_every_invocation_once_in_order(tmp_path: Path, identity) -> None:
    result, host, handback = run(tmp_path, identity)
    assert host.scopes == ALL
    assert result.verdict is R.Verdict.PASS and result.conditions == []
    assert result.closeout_complete and result.exit_code == R.EXIT_PASS
    assert handback.endswith(CLOSING_RECORD)
    for heading in ["## 0. Runner identity", "## 1. Executor identity"] + [f"## {n}. " for n in range(2, 17)]:
        assert heading in handback, heading
    assert f"`RUN.start start_utc={STAMP}`" in handback and "| step 12 |" in handback
    assert "**PASS**" in handback


def test_step1_success_progresses_to_step2(tmp_path: Path, identity) -> None:
    def stop_at_two(host: FakeHost, stdin: bytes | None) -> R.Completed:
        assert host.scopes == ["S1", "S2"]
        return transcript("S2", fail_at="S2.21 required-tools")

    result, host, _ = run(tmp_path, identity, {"S2": stop_at_two})
    assert host.scopes == ["S1", "S2"] + CLOSE
    assert result.conditions[0].scope == "S2"
    assert result.conditions[0].evidence == "S2.21 required-tools exit=1"


def test_step1_exit_zero_without_any_output_is_a_hard_stop(tmp_path: Path, identity) -> None:
    """FRESH-R3-HS-1: a transport that runs nothing yet reports 0."""
    result, host, handback = run(tmp_path, identity, {"S1": R.Completed(0, b"", b"")})
    assert host.scopes == ["S1"] + CLOSE
    first = result.conditions[0]
    assert first.scope == "S1" and first.verdict is R.Verdict.HARD_STOP
    assert "exited 0 but its required evidence is missing" in first.reason
    assert "RUN" in first.evidence and "S1 final exit=" in first.evidence
    assert result.verdict is R.Verdict.HARD_STOP and result.exit_code == R.EXIT_HARD_STOP
    assert "| step 1 | `S1.start` / `S1.end` | repository host | absent (invoking status 0) |" in handback
    assert "| step 2 | `S2.start` / `S2.end` | oracle-test | not run |" in handback
    assert handback.endswith(CLOSING_RECORD)


def test_a_partial_transcript_with_exit_zero_is_a_hard_stop(tmp_path: Path, identity) -> None:
    full = transcript("S1").stdout.decode()
    partial = "\n".join(l for l in full.split("\n") if not l.startswith("S1.6 ")) + "\n"
    result, host, _ = run(tmp_path, identity, {"S1": R.Completed(0, partial.encode(), b"")})
    assert host.scopes == ["S1"] + CLOSE
    assert "`S1.6 hashlib-and-tree-check exit=0` printed 0 times" in result.conditions[0].evidence


def test_a_zero_status_that_disagrees_with_the_blocks_final_exit_is_a_hard_stop(tmp_path: Path, identity) -> None:
    failing = transcript("S1", fail_at="S1.6 hashlib-and-tree-check", status=25)
    result, host, _ = run(tmp_path, identity, {"S1": R.Completed(0, failing.stdout, b"")})
    assert host.scopes == ["S1"] + CLOSE
    assert "`S1 final exit=25` disagrees with the invoking status 0" in result.conditions[0].evidence


def test_a_nonzero_first_step_is_a_hard_stop_quoting_its_first_failure(tmp_path: Path, identity) -> None:
    result, host, handback = run(tmp_path, identity, {"S1": transcript("S1", fail_at="S1.5 sha256sum-check")})
    assert host.scopes == ["S1"] + CLOSE
    first = result.conditions[0]
    assert (first.scope, first.verdict, first.evidence) == ("S1", R.Verdict.HARD_STOP, "S1.5 sha256sum-check exit=1")
    assert "First condition: **HARD STOP** at `S1`" in handback
    assert "Not run after the first condition: S2, S3, S4a," in handback


STOPPABLE = [
    (i.scope, R.expected_labels(resource(Path(i.resource).name))[-1])
    for i in R.OPERATIONAL_PLAN
    if i.kind is R.Kind.STEP
]


@pytest.mark.parametrize("scope,label", STOPPABLE)
def test_the_first_failure_stops_every_later_operational_step(tmp_path: Path, identity, scope: str, label: str) -> None:
    result, host, handback = run(tmp_path, identity, {scope: transcript(scope, fail_at=label, status=7)})
    assert host.scopes == through(scope) + CLOSE
    assert len(set(host.scopes)) == len(host.scopes)
    assert result.conditions[0].scope == scope and result.verdict is R.Verdict.HARD_STOP
    assert handback.endswith(CLOSING_RECORD)


def test_a_failed_synchronization_still_records_its_end_then_stops(tmp_path: Path, identity) -> None:
    result, host, handback = run(tmp_path, identity, {"S4b.sync": transcript("S4b.sync", fail_at="x", status=23)})
    assert host.scopes == through("S4b.end") + CLOSE
    assert result.conditions[0].scope == "S4b.sync" and len(result.conditions) == 1
    assert "S4b.sync: invoking status 23" in handback


def test_a_failed_s4b_start_runs_neither_the_synchronization_nor_s4b_end(tmp_path: Path, identity) -> None:
    result, host, _ = run(tmp_path, identity, {"S4b.start": transcript("S4b.start", fail_at="S4b.start date")})
    assert host.scopes == through("S4b.start") + CLOSE


def test_the_synchronization_file_list_and_stderr_are_not_embedded(tmp_path: Path, identity) -> None:
    _, _, passing = run(tmp_path, identity)
    assert "sent 10 bytes  received 20 bytes" in passing and "total size is 40" in passing
    assert "private.png" not in passing
    other = tmp_path / "second"
    _, _, failing = run(other, identity, {"S4b.sync": transcript("S4b.sync", fail_at="x", status=23)})
    assert "private.png" not in failing


def test_step3_status_20_with_complete_evidence_is_an_invalid_run(tmp_path: Path, identity) -> None:
    result, host, handback = run(tmp_path, identity, {"S3": transcript("S3", fail_at="S3.1 qualification", status=20)})
    assert host.scopes == through("S3") + CLOSE
    assert result.verdict is R.Verdict.INVALID_RUN and result.exit_code == R.EXIT_INVALID_RUN
    assert "**INVALID RUN**" in handback


def test_step3_status_20_with_missing_evidence_is_a_hard_stop(tmp_path: Path, identity) -> None:
    result, _, _ = run(tmp_path, identity, {"S3": R.Completed(20, b"S3.1 qualification exit=20\n", b"")})
    assert result.verdict is R.Verdict.HARD_STOP


@pytest.mark.parametrize(
    "scope,output,expected",
    [
        ("S1", {"S1.3 git-status": [" M a", "git_status_lines=2", "git_status_sha256=" + "0" * 64]}, "S1.3 reproduced 1 lines"),
        ("S5", {"S5.8 root-stat": [f"700 gemini:gemini /var/tmp/{RUN}-root"]}, "S5.8 does not show mode 755"),
        ("S9", {"S9.1 cc1v-length": ["5121"]}, "S9.1 printed"),
        ("S9", {"S9.4 display": CC1CHECK[:-1] + ["verdict:         HARD_STOP"]}, "lacks `verdict:         PASS`"),
        ("S11", {"S11.10 bwrap-version": ["bubblewrap 0.11.2"]}, "S11.10 bwrap-version = S2.6 bwrap-version differs"),
    ],
)
def test_pass_outputs_that_no_exit_status_encodes_are_enforced(tmp_path: Path, identity, scope, output, expected) -> None:
    result, host, _ = run(tmp_path, identity, {scope: transcript(scope, output=output)})
    assert host.scopes == through(scope) + CLOSE
    assert result.conditions[0].scope == scope and expected in result.conditions[0].evidence


# ---------------------------------------------------------------------------
# Closeout
# ---------------------------------------------------------------------------


def test_closeout_follows_a_failed_s12_start(tmp_path: Path, identity) -> None:
    result, host, handback = run(tmp_path, identity, {"S12.start": transcript("S12.start", fail_at="S12.start date")})
    assert host.scopes == ALL
    assert result.conditions[0].scope == "S12.start" and result.verdict is R.Verdict.HARD_STOP
    assert "## 14. Verdict" in handback and handback.endswith(CLOSING_RECORD)


@pytest.mark.parametrize(
    "answer",
    [
        R.Completed(None, b"", b"", start_error="FileNotFoundError: ssh"),
        R.Completed(-15, b"S5.trap exit=0\n", b"", interrupted_by=15),
    ],
)
def test_closeout_follows_a_process_that_could_not_start_or_was_interrupted(tmp_path: Path, identity, answer) -> None:
    result, host, handback = run(tmp_path, identity, {"S5": answer})
    assert host.scopes == through("S5") + CLOSE
    assert result.conditions[0].scope == "S5" and handback.endswith(CLOSING_RECORD)


def test_closeout_follows_a_runner_internal_error(tmp_path: Path, identity) -> None:
    def explode(host: FakeHost, stdin: bytes | None) -> R.Completed:
        raise RuntimeError("defect")

    result, host, handback = run(tmp_path, identity, {"S6-S7": explode})
    assert host.scopes == through("S6-S7") + CLOSE
    assert result.conditions[0].reason == "runner internal error: RuntimeError: defect"
    assert handback.endswith(CLOSING_RECORD)


def test_closeout_follows_a_signal_outside_a_process(tmp_path: Path, identity) -> None:
    def signalled(host: FakeHost, stdin: bytes | None) -> R.Completed:
        raise R.Interrupted(15)

    result, host, _ = run(tmp_path, identity, {"S8": signalled})
    assert host.scopes == through("S8") + CLOSE
    assert result.conditions[0].reason == "the runner received signal 15"


def test_a_failed_closing_block_is_reported_as_an_incomplete_closeout(tmp_path: Path, identity) -> None:
    result, host, _ = run(tmp_path, identity, {"S12.end": transcript("S12.end", fail_at="S12.end.2 handback-body-present", status=33)})
    assert host.scopes == ALL
    assert not result.closeout_complete and result.exit_code == R.EXIT_CLOSEOUT_INCOMPLETE


def test_the_body_is_final_before_s12_end_and_nothing_writes_after_it(tmp_path: Path, identity) -> None:
    host = FakeHost(tmp_path)
    runner = make_runner(tmp_path, identity, host)

    def close(fake: FakeHost, stdin: bytes | None) -> R.Completed:
        assert runner.handback.sealed
        with pytest.raises(R.HandbackSealed):
            runner.handback.append_body("late edit")
        assert stdin is not None and R.HANDBACK.encode() in stdin
        return fake.close()

    host.answers["S12.end"] = close
    result = runner.run()
    final = (tmp_path / R.HANDBACK).read_bytes()
    assert host.handback_after_close == final
    assert final.decode().endswith(CLOSING_RECORD) and final.decode().count("## Closing record") == 1
    assert result.closeout_complete and host.scopes[-1] == "S12.end"


def test_an_existing_handback_is_never_overwritten(tmp_path: Path, identity) -> None:
    host = FakeHost(tmp_path)
    runner = make_runner(tmp_path, identity, host)
    (tmp_path / R.HANDBACK).write_text("closed record\n")
    with pytest.raises(R.Refusal):
        runner.run()
    assert host.calls == [] and (tmp_path / R.HANDBACK).read_text() == "closed record\n"


def test_the_attestation_and_identity_are_written_before_step1(tmp_path: Path, identity) -> None:
    def check(host: FakeHost, stdin: bytes | None) -> R.Completed:
        text = (tmp_path / R.HANDBACK).read_text()
        assert "## 1. Executor identity and §2 independence attestation" in text
        assert f"| `{R.RUNNER}` |" in text and "## 2." not in text
        return transcript("S1")

    run(tmp_path, identity, {"S1": check})


def test_a_failed_renderer_still_produces_a_closed_handback(tmp_path: Path, identity, monkeypatch) -> None:
    def broken(runner: R.Runner) -> str:
        raise ValueError("renderer defect")

    monkeypatch.setattr(R, "render_body", broken)
    result, host, handback = run(tmp_path, identity)
    assert "fallback rendering" in handback and "renderer defect" in handback
    assert handback.endswith(CLOSING_RECORD) and host.scopes == ALL


# ---------------------------------------------------------------------------
# Delivery
# ---------------------------------------------------------------------------


def test_each_block_is_sent_as_its_resource_with_only_run_substituted(tmp_path: Path, identity) -> None:
    _, host, _ = run(tmp_path, identity)
    for scope, argv, stdin in host.calls:
        inv = invocation(scope)
        raw = identity.resources[inv.resource]
        if inv.kind is R.Kind.SYNC:
            assert stdin is None
            assert list(argv) == [a.replace("<RUN>", RUN) for a in r3_sync_argv(r3_text())]
            continue
        assert stdin == raw.replace(b"<RUN>", RUN.encode())
        assert argv == (R.REMOTE_BASH if inv.transport is R.Transport.REMOTE else R.LOCAL_BASH)


def test_the_ledger_refuses_a_repeat_or_a_reordering() -> None:
    ledger = R.AttemptLedger(R.FULL_PLAN)
    ledger.attempt("S1")
    with pytest.raises(R.PlanViolation):
        ledger.attempt("S1")
    ledger.attempt("S3")
    with pytest.raises(R.PlanViolation):
        ledger.attempt("S2")


def test_the_subprocess_transport_needs_no_terminal_and_no_eof(tmp_path: Path) -> None:
    """A harmless, non-R-5 script through the real transport: stdin is a closed
    pipe, both streams are separate, the status is the process's own, and the
    child leads its own session, so it has no controlling terminal."""
    script = (
        b"probe() {\n"
        b"  read -r _ _ _ _ _ sid _ < /proc/$$/stat\n"
        b"  if [ \"$sid\" = \"$$\" ]; then printf 'session_leader=yes\\n'; fi\n"
        b"  printf 'to-stderr\\n' >&2\n"
        b"  exit 7\n"
        b"}\n"
        b"probe </dev/null\n"
    )
    completed = R.SubprocessExecutor(tmp_path).run("probe", R.LOCAL_BASH, script)
    assert completed.returncode == 7
    assert completed.stdout == b"session_leader=yes\n"
    assert completed.stderr == b"to-stderr\n"
