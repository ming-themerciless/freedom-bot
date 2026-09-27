"""**C-P5.0-LAB-I3-R2** — the separately armed I3 controlled-write verifier.

Runner contract r6 §9.2 rows 90–105 trace to the tests below. Every test drives
the real mechanism — `execution/i3_verifier.py` and its entry point
`execution/i3_verifier_cli.py` — over a model host under `tmp_path`, with the
account database, `/proc/self/status`, `fs.protected_hardlinks` and
`/proc/self/mountinfo` injected and with faults injected at the real syscalls.

**Nothing here confirms a target fact.** A publication that succeeds in this
suite succeeded on whatever kernel and filesystem ran the suite; it says nothing
about `oracle-test`, and I3 stays unconfirmed. No test here needs root, reads
the host's account database, touches `/var/lib`, `/run` or
`/opt/freedom-blades`, or runs a process.
"""
from __future__ import annotations

import ast
import dataclasses
import errno
import hashlib
import inspect
import os
import re
import stat
import sys
import types
from dataclasses import dataclass
from pathlib import Path

import pytest

from tools.phase_5_0_evidence.capability import CAP_DAC_OVERRIDE, CAP_FOWNER
from tools.phase_5_0_evidence.case_runtime import (
    CASE_PROGRAM_GROUP,
    CASE_PROGRAM_MODE,
    CASE_PROGRAM_OWNER,
    CASE_PROGRAM_TEMPORARY_MODE,
)
from tools.phase_5_0_evidence.errors import HarnessError
from tools.phase_5_0_evidence.execution import descriptors as descriptors_module
from tools.phase_5_0_evidence.execution import i3_verifier as verifier_module
from tools.phase_5_0_evidence.execution import i3_verifier_cli
from tools.phase_5_0_evidence.execution.descriptors import PosixFilesystem
from tools.phase_5_0_evidence.execution.i3_verifier import (
    ADMISSION_REFUSALS,
    CANONICAL_BIN_MODE,
    CANONICAL_ROOT_MODE,
    INVOCATION_CONTEXTS,
    NAME_PREFIX,
    NOT_ATTRIBUTION,
    PAYLOAD,
    PAYLOAD_SHA256,
    STAGE_FAILURES,
    ContextId,
    ContextOutcome,
    ContextStatus,
    I3ControlledWriteVerifier,
    Invocation,
    ObjectFate,
    ObjectKind,
    Stage,
    Status,
    SurveyResult,
    TrackedObject,
    VerificationRun,
    classify_capabilities,
    i3_layout,
    name_is_admissible,
    parse_status,
    verifier_names,
)
from tools.phase_5_0_evidence.execution.i3_verifier_cli import (
    ARM_FLAG,
    FAILED_NO_RESIDUE_EXIT_CODE,
    NOT_ARMED_EXIT_CODE,
    OPERATOR_ATTENTION_EXIT_CODE,
    REFUSED_EXIT_CODE,
    UNCLASSIFIED_EXIT_CODE,
    VERIFIED_EXIT_CODE,
    main,
    render_run,
)
from tools.phase_5_0_evidence.execution.participants import (
    ParticipantRefused,
    validate_run_identifier,
)
from tools.phase_5_0_evidence.execution.recovery_store import (
    RECORD_SUFFIX,
    STORED_OBJECT_MODE,
    TEMPORARY_SUFFIX,
)
from tools.phase_5_0_evidence.provisioning import (
    LABORATORY_LAYOUT,
    PARTICIPANT_IDENTITY,
    LaboratoryLayout,
)

VERIFIER_SOURCE = Path(verifier_module.__file__).read_text(encoding="utf-8")
CLI_SOURCE = Path(i3_verifier_cli.__file__).read_text(encoding="utf-8")
PACKAGE = Path(verifier_module.__file__).resolve().parents[1]

#: Asserted absent from every rendering: an operating-system message, an account
#: record and a secret-looking value are exactly what the surface may not carry.
SECRET = "hunter2-SECRET-TOKEN"
OS_MESSAGE = f"injected {SECRET} operating-system message"

FULL_MASK = "000001ffffffffff"
ZERO_MASK = "0000000000000000"


# ---------------------------------------------------------------------------
# The model host
# ---------------------------------------------------------------------------


@dataclass
class Lab:
    state_parent: Path
    state_root: Path
    laboratory: Path
    runs: Path
    recovery: Path
    canonical_root: Path

    @property
    def layout(self):
        return i3_layout(
            layout=LaboratoryLayout(
                laboratory_directory=str(self.laboratory),
                runs_directory_name=self.runs.name,
                record_name="lifecycle.json",
                recovery_directory=str(self.recovery),
                lock_path=str(self.state_parent / "laboratory.lock"),
            ),
            evidence_root=str(self.canonical_root),
        )

    @property
    def canonical_bin(self) -> Path:
        return self.canonical_root / "bin"

    def snapshot(self) -> dict[str, tuple[int, int, int]]:
        """Every object under the state parent: `(inode, mode, size)`."""
        found: dict[str, tuple[int, int, int]] = {}
        for path in sorted(self.state_parent.rglob("*")):
            facts = path.lstat()
            found[str(path.relative_to(self.state_parent))] = (
                facts.st_ino,
                facts.st_mode,
                facts.st_size,
            )
        return found

    def verifier_names_on_disk(self) -> list[str]:
        return sorted(
            str(path.relative_to(self.state_parent))
            for path in self.state_parent.rglob(f"{NAME_PREFIX}*")
        )


@pytest.fixture
def lab(tmp_path: Path) -> Lab:
    state_parent = tmp_path / "var-lib"
    state_root = state_parent / "freedom-blades"
    laboratory = state_root / "laboratory"
    runs = laboratory / "runs"
    recovery = state_root / "recovery"
    for path, mode in (
        (state_parent, 0o755),
        (state_root, 0o755),
        (laboratory, 0o750),
        (runs, 0o3770),
        (recovery, 0o700),
    ):
        path.mkdir()
        path.chmod(mode)
    return Lab(
        state_parent=state_parent,
        state_root=state_root,
        laboratory=laboratory,
        runs=runs,
        recovery=recovery,
        canonical_root=state_parent / "fb-evidence-p5-0",
    )


class FakeAccounts:
    """Every reviewed name resolves to **this process's own** ids.

    That is what lets the real `fchown` and every ownership comparison run
    without privilege. `uid_shift`/`gid_shift` move one name's answer away from
    the truth; `unknown` makes one name unresolvable, with a message that must
    never be printed.
    """

    def __init__(self, *, uid_shift=None, gid_shift=None, unknown: str = "") -> None:
        self.uid_shift = uid_shift or {}
        self.gid_shift = gid_shift or {}
        self.unknown = unknown
        self.calls: list[str] = []

    def account(self, name: str) -> tuple[int, int]:
        self.calls.append(name)
        if name == self.unknown:
            raise HarnessError(f"no account named {name!r} {SECRET}")
        return os.geteuid() + self.uid_shift.get(name, 0), os.getegid()

    def group_id(self, name: str) -> int:
        self.calls.append(name)
        if name == self.unknown:
            raise HarnessError(f"no group named {name!r} {SECRET}")
        return os.getegid() + self.gid_shift.get(name, 0)


def status_text(
    *,
    uids=None,
    gids=None,
    groups=None,
    cap_inh=ZERO_MASK,
    cap_prm=FULL_MASK,
    cap_eff=FULL_MASK,
    cap_bnd=FULL_MASK,
    cap_amb=ZERO_MASK,
    no_new_privs="0",
    extra: str = "",
    omit: str = "",
) -> bytes:
    uid, gid = os.geteuid(), os.getegid()
    uids = uids or (uid, uid, uid, uid)
    gids = gids or (gid, gid, gid, gid)
    groups = groups if groups is not None else (gid,)
    fields = {
        "Name": "python3",
        "Uid": "\t".join(str(item) for item in uids),
        "Gid": "\t".join(str(item) for item in gids),
        "Groups": " ".join(str(item) for item in groups),
        "CapInh": cap_inh,
        "CapPrm": cap_prm,
        "CapEff": cap_eff,
        "CapBnd": cap_bnd,
        "CapAmb": cap_amb,
        "NoNewPrivs": no_new_privs,
    }
    lines = [f"{key}:\t{value}" for key, value in fields.items() if key != omit]
    return ("\n".join(lines) + "\n" + extra).encode("ascii", "surrogateescape")


class FakeProbe:
    """The four host reads, injected. `statuses` feeds successive reads."""

    def __init__(
        self,
        lab: Lab,
        *,
        status: bytes | None = None,
        statuses: list[bytes] | None = None,
        policy: bytes = b"1\n",
        mountinfo: bytes | None = None,
        ids=None,
        host=("Test", "7.0.0-31-generic", "x86_64"),
    ) -> None:
        self._host = host
        self._statuses = (
            list(statuses)
            if statuses
            else [status if status is not None else status_text()]
        )
        self._policy = policy
        device = lab.state_parent.stat().st_dev
        self._mountinfo = mountinfo if mountinfo is not None else (
            f"29 1 {os.major(device)}:{os.minor(device)} / / rw,relatime "
            "shared:1 - ext4 /dev/sda1 rw,errors=remount-ro\n"
        ).encode()
        self._ids = ids
        self.status_reads = 0
        self.reads: list[str] = []

    def status(self) -> bytes:
        self.reads.append("status")
        index = min(self.status_reads, len(self._statuses) - 1)
        self.status_reads += 1
        value = self._statuses[index]
        if isinstance(value, Exception):
            raise value
        return value

    def protected_hardlinks(self) -> bytes:
        self.reads.append("policy")
        if isinstance(self._policy, Exception):
            raise self._policy
        return self._policy

    def mountinfo(self) -> bytes:
        self.reads.append("mountinfo")
        return self._mountinfo

    def host(self):
        self.reads.append("host")
        if isinstance(self._host, Exception):
            raise self._host
        return self._host

    def process_ids(self):
        self.reads.append("ids")
        if self._ids is not None:
            return self._ids
        return os.getresuid(), os.getresgid()


def make(
    lab: Lab,
    *,
    probe: FakeProbe | None = None,
    accounts: FakeAccounts | None = None,
    armed: bool = True,
    nonce=None,
    cls=I3ControlledWriteVerifier,
):
    kwargs = {}
    if nonce is not None:
        kwargs["nonce"] = nonce
    return cls(
        lookup=accounts or FakeAccounts(),
        probe=probe or FakeProbe(lab),
        armed=armed,
        layout=lab.layout,
        **kwargs,
    )


def outcome_for(run: VerificationRun, context: ContextId) -> ContextOutcome:
    return next(outcome for outcome in run.contexts if outcome.context is context)


def inject(monkeypatch, name: str, when, *, skip: int = 0, times: int = 1, before=None):
    """Make `os.<name>` fail for matching calls, after `skip` matching calls.

    `before` runs first on a failing call, which is how a `close()` that
    released the descriptor and then reported failure is modelled, and how a
    substitution is made at an exact point.
    """
    real = getattr(os, name)
    state = {"seen": 0, "failed": 0}

    def wrapper(*args, **kwargs):
        if when(*args, **kwargs):
            state["seen"] += 1
            if state["seen"] > skip and state["failed"] < times:
                state["failed"] += 1
                if before is not None:
                    before(real, *args, **kwargs)
                raise OSError(errno.EIO, OS_MESSAGE)
        return real(*args, **kwargs)

    monkeypatch.setattr(os, name, wrapper)
    return state


def _fd_is(fd: int, path: Path) -> bool:
    try:
        return os.fstat(fd).st_ino == path.stat().st_ino
    except OSError:
        return False


def _fd_is_file(fd: int) -> bool:
    try:
        return stat.S_ISREG(os.fstat(fd).st_mode)
    except OSError:
        return False


def _fd_is_dir(fd: int) -> bool:
    try:
        return stat.S_ISDIR(os.fstat(fd).st_mode)
    except OSError:
        return False


def _accounting_matches_disk(lab: Lab, run: VerificationRun) -> None:
    """Every tracked object's fate agrees with what is on disk.

    `REMOVED` objects are gone. Every verifier name still on disk is accounted
    for by a non-`REMOVED` fate or by a foreign object the run refused to touch,
    and the run is then never `VERIFIED` or `FAILED_NO_RESIDUE`.
    """
    fates = [obj.fate for outcome in run.contexts for obj in outcome.objects]
    leftover = lab.verifier_names_on_disk()
    if leftover or lab.canonical_root.exists():
        assert run.status is Status.FAILED_OPERATOR_ATTENTION
    if run.status in (Status.VERIFIED, Status.FAILED_NO_RESIDUE):
        assert all(fate is ObjectFate.REMOVED for fate in fates)
        assert not leftover
        assert not lab.canonical_root.exists()


# ---------------------------------------------------------------------------
# 1. Two gates — r6 §9.2 rows 90–91
# ---------------------------------------------------------------------------


class _Forbidden:
    def __init__(self, *_args, **_kwargs) -> None:
        raise AssertionError("constructed on a path that must read nothing")


def test_no_arm_reads_nothing_and_writes_nothing(monkeypatch, lab, capsys) -> None:
    """Row 90. The default invocation constructs no lookup, probe or verifier."""
    before = lab.snapshot()
    monkeypatch.setattr(i3_verifier_cli, "SystemIdentityLookup", _Forbidden)
    monkeypatch.setattr(i3_verifier_cli, "ProcHostProbe", _Forbidden)
    monkeypatch.setattr(i3_verifier_cli, "I3ControlledWriteVerifier", _Forbidden)

    assert main([]) == NOT_ARMED_EXIT_CODE
    assert main(["--identity", "root"]) == NOT_ARMED_EXIT_CODE
    printed = capsys.readouterr().out
    assert "NOT ARMED" in printed and "nothing was written" in printed
    assert lab.snapshot() == before


def test_armed_without_an_identity_reads_nothing(monkeypatch, lab, capsys) -> None:
    before = lab.snapshot()
    monkeypatch.setattr(i3_verifier_cli, "SystemIdentityLookup", _Forbidden)
    monkeypatch.setattr(i3_verifier_cli, "ProcHostProbe", _Forbidden)
    monkeypatch.setattr(i3_verifier_cli, "I3ControlledWriteVerifier", _Forbidden)

    assert main([ARM_FLAG]) == REFUSED_EXIT_CODE
    assert "invocation-identity-not-named" in capsys.readouterr().out
    assert lab.snapshot() == before


def test_an_unarmed_verifier_reads_nothing_and_writes_nothing(lab) -> None:
    accounts, probe = FakeAccounts(), FakeProbe(lab)
    before = lab.snapshot()
    verifier = make(lab, probe=probe, accounts=accounts, armed=False)

    run = verifier.run("root")

    assert run.status is Status.NOT_ARMED and run.refusal == "verifier-not-armed"
    assert accounts.calls == [] and probe.reads == []
    assert verifier.events == []
    assert lab.snapshot() == before


@pytest.mark.parametrize("value", [1, "yes", object()])
def test_the_in_code_gate_admits_only_true_itself(lab, value) -> None:
    """A truthy stand-in is not an arm."""
    run = make(lab, armed=value).run("root")
    assert run.status is Status.NOT_ARMED
    assert not lab.canonical_root.exists()


def _cli_calls(name: str) -> list[ast.Call]:
    tree = ast.parse(CLI_SOURCE)
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
    ]


def test_the_arm_is_the_flag_itself_and_the_route_follows_the_check() -> None:
    constructions = _cli_calls("I3ControlledWriteVerifier")
    assert len(constructions) == 1
    keywords = {keyword.arg: keyword.value for keyword in constructions[0].keywords}
    assert set(keywords) == {"lookup", "probe", "armed"}
    armed = keywords["armed"]
    assert isinstance(armed, ast.Attribute) and armed.attr == "arm_i3_controlled_write"

    tree = ast.parse(CLI_SOURCE)
    main_fn = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    guard = next(node for node in main_fn.body if isinstance(node, ast.If))
    assert any(isinstance(node, ast.Return) for node in ast.walk(guard))
    for name in ("I3ControlledWriteVerifier", "SystemIdentityLookup", "ProcHostProbe"):
        for call in _cli_calls(name):
            assert call.lineno > guard.lineno, name


def _cli_with_the_arm_check_removed() -> dict:
    tree = ast.parse(CLI_SOURCE)
    main_fn = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    guard = next(node for node in main_fn.body if isinstance(node, ast.If))
    main_fn.body = [node for node in main_fn.body if node is not guard]
    ast.fix_missing_locations(tree)
    namespace: dict = {
        "__name__": "i3_verifier_cli_with_the_arm_removed",
        "__package__": "tools.phase_5_0_evidence.execution",
    }
    exec(compile(tree, "<the arm removed>", "exec"), namespace)  # noqa: S102
    return namespace


def test_reversal_the_command_line_arm_removed_still_writes_nothing(lab, capsys) -> None:
    """Row 91, first half. With the early return deleted, a default invocation
    reaches a verifier — armed from the absent flag, so it refuses before its
    first read and nothing is written."""
    before = lab.snapshot()
    accounts, probe = FakeAccounts(), FakeProbe(lab)
    mutated = _cli_with_the_arm_check_removed()
    mutated["SystemIdentityLookup"] = lambda: accounts
    mutated["ProcHostProbe"] = lambda: probe

    real_run = I3ControlledWriteVerifier.run

    class Pinned(I3ControlledWriteVerifier):
        def run(self, invocation):  # noqa: D401 - the layout is the model's
            self.layout = lab.layout
            return real_run(self, invocation)

    mutated["I3ControlledWriteVerifier"] = Pinned
    status = mutated["main"](["--identity", "root"])

    assert status == NOT_ARMED_EXIT_CODE
    assert "verifier-not-armed" in capsys.readouterr().out
    assert accounts.calls == [] and probe.reads == []
    assert lab.snapshot() == before


def _mutated_verifier(function: str, body: str, *, owner: str = "") -> dict:
    """The verifier module with one function's body replaced, compiled and run.

    This is a **single-point reversal**: the edit is made to the syntax tree and
    the result is executed, so a test proves the guard is load-bearing rather
    than asserting that an edit is absent.
    """
    tree = ast.parse(VERIFIER_SOURCE)
    scope = tree.body
    if owner:
        scope = next(
            node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == owner
        ).body
    target = next(
        node for node in scope if isinstance(node, ast.FunctionDef) and node.name == function
    )
    target.body = ast.parse(body).body
    ast.fix_missing_locations(tree)
    return _execute(tree, f"i3_verifier_reversed_{function}")


def _execute(tree: ast.Module, name: str) -> dict:
    """Run a mutated copy as a real, registered module.

    `dataclass` resolves a class's module through `sys.modules` while it builds
    the class, so the copy is registered for exactly as long as it executes.
    """
    module = types.ModuleType(name)
    module.__package__ = "tools.phase_5_0_evidence.execution"
    sys.modules[name] = module
    try:
        exec(compile(tree, f"<{name}>", "exec"), module.__dict__)  # noqa: S102
    finally:
        sys.modules.pop(name, None)
    return module.__dict__


def test_reversal_the_in_code_gate_removed_is_stopped_by_the_arm(
    monkeypatch, lab, capsys
) -> None:
    """Row 91, second half. With the in-code gate deleted, the command line
    without its flag still returns before any construction; and the deleted
    gate is load-bearing, because an unarmed verifier without it writes."""
    mutated = _mutated_verifier("_require_armed", "return None", owner="I3ControlledWriteVerifier")
    Reversed = mutated["I3ControlledWriteVerifier"]
    monkeypatch.setattr(i3_verifier_cli, "I3ControlledWriteVerifier", Reversed)
    monkeypatch.setattr(i3_verifier_cli, "SystemIdentityLookup", _Forbidden)
    monkeypatch.setattr(i3_verifier_cli, "ProcHostProbe", _Forbidden)
    before = lab.snapshot()

    assert main([]) == NOT_ARMED_EXIT_CODE
    assert lab.snapshot() == before

    # The negative control: the same deletion, reached without the command line.
    reversed_run = make(lab, armed=False, cls=Reversed).run("root")
    assert reversed_run.status.value == "verified"
    assert make(lab, armed=False).run("root").status is Status.NOT_ARMED


# ---------------------------------------------------------------------------
# 2. Admission — every precondition refuses before the first write — row 92
# ---------------------------------------------------------------------------


def _refuses_before_write(lab: Lab, verifier, invocation="root", expected: str = "") -> VerificationRun:
    before = lab.snapshot()
    run = verifier.run(invocation)
    assert run.status is Status.REFUSED_BEFORE_WRITE, run
    if expected:
        assert run.refusal == expected
    assert run.refusal in ADMISSION_REFUSALS
    assert verifier.events == []
    assert lab.snapshot() == before
    assert run.contexts == ()
    return run


def _uid() -> int:
    return os.geteuid()


def _gid() -> int:
    return os.getegid()


STATUS_REFUSALS = [
    pytest.param(dict(uids=(_uid(), _uid(), _uid(), _uid() + 1)), "identity-mismatch", id="filesystem-uid"),
    pytest.param(dict(uids=(_uid() + 1,) * 4), "identity-mismatch", id="every-uid"),
    pytest.param(dict(gids=(_gid(), _gid() + 1, _gid(), _gid())), "identity-mismatch", id="effective-gid"),
    pytest.param(dict(omit="CapEff"), "capability-state-unobservable", id="no-CapEff"),
    pytest.param(dict(omit="CapBnd"), "capability-state-unobservable", id="no-CapBnd"),
    pytest.param(dict(extra=f"CapBnd:\t{FULL_MASK}\n"), "capability-state-unobservable", id="two-CapBnd"),
    pytest.param(dict(cap_eff="00000fffffffff"), "capability-state-unobservable", id="short-mask"),
    pytest.param(dict(cap_prm=f"{SECRET[:16]}"), "capability-state-unobservable", id="not-hex"),
    pytest.param(dict(no_new_privs="2"), "capability-state-unobservable", id="no-new-privs"),
    pytest.param(dict(omit="Uid"), "process-status-unobservable", id="no-Uid"),
    pytest.param(dict(extra=f"Uid:\t0\t0\t0\t0 {SECRET}\n"), "process-status-unobservable", id="two-Uid"),
    pytest.param(
        dict(cap_eff="0000000000000008", cap_prm=ZERO_MASK),
        "capability-state-inconsistent",
        id="CapEff-outside-CapPrm",
    ),
    pytest.param(
        dict(cap_amb="0000000000000008", cap_inh=ZERO_MASK),
        "capability-state-inconsistent",
        id="CapAmb-outside-CapInh",
    ),
]


@pytest.mark.parametrize("fields,expected", STATUS_REFUSALS)
def test_every_status_mismatch_refuses_before_the_first_write(lab, fields, expected) -> None:
    probe = FakeProbe(lab, status=status_text(**fields))
    _refuses_before_write(lab, make(lab, probe=probe), expected=expected)


@pytest.mark.parametrize(
    "raw",
    [b"", b"\xff\xfe" + SECRET.encode(), b"x" * (70 * 1024)],
    ids=["empty", "not-ascii", "unbounded"],
)
def test_malformed_status_bytes_refuse(lab, raw) -> None:
    _refuses_before_write(lab, make(lab, probe=FakeProbe(lab, status=raw)))


def test_an_unreadable_status_refuses(lab) -> None:
    probe = FakeProbe(lab, statuses=[OSError(errno.EACCES, OS_MESSAGE)])
    _refuses_before_write(lab, make(lab, probe=probe), expected="process-status-unobservable")


def test_process_ids_that_disagree_with_status_refuse(lab) -> None:
    uid, gid = _uid(), _gid()
    probe = FakeProbe(lab, ids=((uid, uid, uid + 1), (gid, gid, gid)))
    _refuses_before_write(lab, make(lab, probe=probe), expected="identity-mismatch")


def test_the_participant_must_already_hold_the_laboratory_group(lab) -> None:
    probe = FakeProbe(lab, status=status_text(groups=(_gid() + 7,)))
    _refuses_before_write(
        lab, make(lab, probe=probe), invocation=PARTICIPANT_IDENTITY,
        expected="group-membership-missing",
    )


@pytest.mark.parametrize(
    "policy,expected",
    [
        (b"0\n", "hardlink-policy-mismatch"),
        (b"2\n", "hardlink-policy-unobservable"),
        (b"1", "hardlink-policy-unobservable"),
        (b"", "hardlink-policy-unobservable"),
        (SECRET.encode(), "hardlink-policy-unobservable"),
        (OSError(errno.EACCES, OS_MESSAGE), "hardlink-policy-unobservable"),
    ],
    ids=["zero", "two", "no-newline", "empty", "garbage", "unreadable"],
)
def test_the_hardlink_policy_must_be_exactly_one(lab, policy, expected) -> None:
    _refuses_before_write(lab, make(lab, probe=FakeProbe(lab, policy=policy)), expected=expected)


def _mount_line(lab: Lab, *, fstype="ext4", source="/dev/sda1", options="rw,relatime", device=None) -> bytes:
    device = device if device is not None else lab.state_parent.stat().st_dev
    return (
        f"29 1 {os.major(device)}:{os.minor(device)} / / {options} shared:1 - "
        f"{fstype} {source} rw\n"
    ).encode()


@pytest.mark.parametrize(
    "build,expected",
    [
        (lambda lab: _mount_line(lab, fstype="tmpfs"), "mount-mismatch"),
        (lambda lab: _mount_line(lab, source="/dev/sdb1"), "mount-mismatch"),
        (lambda lab: _mount_line(lab, options="ro,relatime"), "mount-mismatch"),
        (lambda lab: _mount_line(lab) + _mount_line(lab, fstype="xfs"), "mount-mismatch"),
        (lambda lab: _mount_line(lab, device=os.makedev(250, 250)), "mount-mismatch"),
        (lambda lab: f"garbage {SECRET}\n".encode(), "mount-unobservable"),
        (lambda lab: b"", "mount-unobservable"),
        (lambda lab: b"\xff" + SECRET.encode(), "mount-unobservable"),
    ],
    ids=["tmpfs", "device", "read-only", "bind-disagrees", "other-device", "malformed", "empty", "binary"],
)
def test_the_mount_must_be_the_approved_filesystem(lab, build, expected) -> None:
    probe = FakeProbe(lab, mountinfo=build(lab))
    _refuses_before_write(lab, make(lab, probe=probe), expected=expected)


@pytest.mark.parametrize(
    "mutate,expected,invocation",
    [
        (lambda lab: lab.laboratory.chmod(0o770), "directory-wrong-mode", "root"),
        (lambda lab: lab.recovery.chmod(0o750), "directory-wrong-mode", "root"),
        (lambda lab: lab.state_root.chmod(0o775), "directory-wrong-mode", "root"),
        (lambda lab: lab.runs.chmod(0o0770), "directory-wrong-mode", PARTICIPANT_IDENTITY),
        (lambda lab: lab.state_parent.chmod(0o775), "state-parent-unsafe", "root"),
        (lambda lab: lab.state_parent.chmod(0o757), "state-parent-unsafe", "root"),
        (lambda lab: lab.recovery.rmdir(), "directory-absent", "root"),
        (lambda lab: _replace_with_symlink(lab.recovery), "directory-wrong-type", "root"),
        (lambda lab: _replace_with_file(lab.runs), "directory-wrong-type", PARTICIPANT_IDENTITY),
        (lambda lab: lab.canonical_root.mkdir(), "canonical-root-present", "root"),
        (lambda lab: lab.canonical_root.symlink_to(lab.recovery), "canonical-root-present", "root"),
        (lambda lab: (lab.laboratory / f"{NAME_PREFIX}old-linked").write_bytes(b""), "prior-verifier-residue", "root"),
        (lambda lab: (lab.runs / f"{NAME_PREFIX}x").mkdir(), "prior-verifier-residue", PARTICIPANT_IDENTITY),
    ],
    ids=[
        "V4-mode", "V5-mode", "V12-mode", "V9-no-setgid-sticky", "parent-group-write",
        "parent-other-write", "V5-absent", "V5-symlink", "V9-file", "R-present",
        "R-symlink", "prior-residue-V4", "prior-residue-V9",
    ],
)
def test_every_directory_mismatch_refuses_before_the_first_write(lab, mutate, expected, invocation) -> None:
    mutate(lab)
    _refuses_before_write(lab, make(lab), invocation=invocation, expected=expected)


def _replace_with_symlink(path: Path) -> None:
    target = path.with_name(path.name + "-real")
    path.rename(target)
    path.symlink_to(target)


def _replace_with_file(path: Path) -> None:
    path.rmdir()
    path.write_bytes(b"")


@pytest.mark.parametrize(
    "accounts,expected,invocation",
    [
        (FakeAccounts(uid_shift={"root": 1}), "identity-mismatch", "root"),
        (FakeAccounts(uid_shift={"root": 1}), "state-parent-unsafe", PARTICIPANT_IDENTITY),
        (FakeAccounts(gid_shift={"freedomlab": 1}), "directory-wrong-group", "root"),
        (FakeAccounts(unknown="freedomlab"), "account-unresolved", "root"),
        (FakeAccounts(unknown="root"), "account-unresolved", PARTICIPANT_IDENTITY),
    ],
    ids=["root-is-not-this-process", "parent-owner", "group", "group-unknown", "root-unknown"],
)
def test_account_and_ownership_mismatches_refuse(lab, accounts, expected, invocation) -> None:
    _refuses_before_write(
        lab, make(lab, accounts=accounts), invocation=invocation, expected=expected
    )


def test_a_directory_owned_by_another_account_refuses(monkeypatch, lab) -> None:
    """The reviewed item's owner is resolved and compared, not assumed root."""
    items = verifier_module.items_by_id()
    items["V4"] = dataclasses.replace(items["V4"], owner="daemon")
    monkeypatch.setattr(verifier_module, "items_by_id", lambda: items)
    accounts = FakeAccounts(uid_shift={"daemon": 5})
    _refuses_before_write(lab, make(lab, accounts=accounts), expected="directory-wrong-owner")


def test_a_participant_that_is_not_the_named_identity_refuses(lab) -> None:
    accounts = FakeAccounts(uid_shift={PARTICIPANT_IDENTITY: 3})
    _refuses_before_write(
        lab, make(lab, accounts=accounts), invocation=PARTICIPANT_IDENTITY,
        expected="identity-mismatch",
    )


@pytest.mark.parametrize(
    "nonce",
    [lambda: b"\x00" * 15, lambda: "not bytes", lambda: (_ for _ in ()).throw(OSError(OS_MESSAGE))],
    ids=["short", "not-bytes", "raises"],
)
def test_an_unavailable_nonce_refuses(lab, nonce) -> None:
    _refuses_before_write(lab, make(lab, nonce=nonce), expected="nonce-unavailable")


def test_an_occupied_name_refuses_when_the_residue_listing_missed_it(monkeypatch, lab) -> None:
    """The occupancy check is independent of the residue listing."""
    fixed = b"\x11" * 16
    _temporary, published = verifier_names(fixed.hex())
    (lab.laboratory / published).write_bytes(b"somebody else's")
    monkeypatch.setattr(
        I3ControlledWriteVerifier, "_listing", staticmethod(lambda inventory, role: ())
    )
    _refuses_before_write(lab, make(lab, nonce=lambda: fixed), expected="name-occupied")
    assert (lab.laboratory / published).read_bytes() == b"somebody else's"


@pytest.mark.parametrize(
    "host,expected",
    [
        (("oracle-test", "7.0.0-31-generic", "x86_64"), "target-mismatch"),
        (("oracle-prod", "7.0.0-31-generic", "x86_64"), "target-mismatch"),
        (("test", "7.0.0-31-generic", "x86_64"), "target-mismatch"),
        (("", "7.0.0-31-generic", "x86_64"), "target-mismatch"),
        (("Test", "7.0.0-32-generic", "x86_64"), "target-mismatch"),
        (("Test", "7.0.0-31-generic", "aarch64"), "target-mismatch"),
        (OSError(errno.EIO, OS_MESSAGE), "target-unobservable"),
    ],
    ids=[
        "ssh-alias-as-nodename",
        "other-nodename",
        "nodename-case",
        "nodename-empty",
        "kernel",
        "architecture",
        "unobservable",
    ],
)
def test_only_the_approved_target_is_admitted(lab, host, expected) -> None:
    """The approved target's **kernel nodename**, kernel and architecture.

    The first case is the C-P5.0-LAB-I3-R4 blocker in reverse. Before Peter's
    Option A decision the verifier compared `uname(2)`'s nodename with
    `APPROVED_TARGET_FACTS.host`, the runbook §2 SSH alias, so `oracle-test` was
    the value that *passed*. It must now refuse: an alias is not a nodename, and
    admitting one here would admit a host the kernel never identified.
    """
    from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET_FACTS

    assert (
        APPROVED_TARGET_FACTS.kernel_nodename,
        APPROVED_TARGET_FACTS.active_kernel,
        APPROVED_TARGET_FACTS.architecture,
    ) == ("Test", "7.0.0-31-generic", "x86_64")
    _refuses_before_write(lab, make(lab, probe=FakeProbe(lab, host=host)), expected=expected)


def test_the_approved_nodename_passes_the_target_portion_of_admission(lab) -> None:
    """`("Test", …)` gets *past* target identity, and the alias does not.

    Admission continues to a later refusal on this synthetic laboratory rather
    than reaching a controlled write, which is what makes the distinction
    visible: the approved tuple is not refused for `target-mismatch`, and
    substituting the SSH alias for the nodename is.
    """
    approved = ("Test", "7.0.0-31-generic", "x86_64")
    run = make(lab, probe=FakeProbe(lab, host=approved)).run("root")
    assert run.refusal != "target-mismatch"

    alias = ("oracle-test", "7.0.0-31-generic", "x86_64")
    aliased = make(lab, probe=FakeProbe(lab, host=alias)).run("root")
    assert aliased.refusal == "target-mismatch"
    assert aliased.status is Status.REFUSED_BEFORE_WRITE


def test_admission_reads_the_nodename_fact_and_never_the_ssh_alias(lab) -> None:
    """The comparison is bound to `kernel_nodename`, not to `host`.

    Moving the nodename fact moves what admission accepts; moving the alias
    moves nothing here. A verifier that had silently gone on comparing `host`
    would pass the first half and fail the second.
    """
    import tools.phase_5_0_evidence.approved_target as approved_target
    from dataclasses import replace

    facts = approved_target.APPROVED_TARGET_FACTS
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            approved_target, "APPROVED_TARGET_FACTS", replace(facts, kernel_nodename="Other")
        )
        patch.setattr(
            verifier_module, "APPROVED_TARGET_FACTS", replace(facts, kernel_nodename="Other")
        )
        moved = make(lab, probe=FakeProbe(lab, host=("Test", "7.0.0-31-generic", "x86_64")))
        assert moved.run("root").refusal == "target-mismatch"
        admitted = make(lab, probe=FakeProbe(lab, host=("Other", "7.0.0-31-generic", "x86_64")))
        assert admitted.run("root").refusal != "target-mismatch"

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(verifier_module, "APPROVED_TARGET_FACTS", replace(facts, host="somewhere"))
        unaffected = make(lab, probe=FakeProbe(lab, host=("Test", "7.0.0-31-generic", "x86_64")))
        assert unaffected.run("root").refusal != "target-mismatch"


def test_a_changed_payload_refuses_before_the_first_write(monkeypatch, lab) -> None:
    monkeypatch.setattr(verifier_module, "PAYLOAD", PAYLOAD + b"x")
    _refuses_before_write(lab, make(lab), expected="payload-digest-mismatch")


def test_an_unrecognized_invocation_refuses(lab) -> None:
    run = make(lab).run("nobody")
    assert run.status is Status.REFUSED_BEFORE_WRITE
    assert run.refusal == "invocation-not-recognized"


@pytest.mark.parametrize(
    "layout",
    [
        dict(laboratory_directory="/a/state/laboratory", recovery_directory="/b/state/recovery"),
        dict(laboratory_directory="/a/state/x", recovery_directory="/a/state/x"),
        dict(laboratory_directory="relative/laboratory", recovery_directory="/a/state/recovery"),
    ],
    ids=["parents-differ", "same-name", "relative"],
)
def test_the_layout_is_derived_or_refused(layout) -> None:
    with pytest.raises(Exception) as caught:
        i3_layout(
            layout=LaboratoryLayout(
                runs_directory_name="runs", record_name="r", lock_path="/l", **layout
            ),
            evidence_root="/a/fb-evidence-p5-0",
        )
    assert getattr(caught.value, "classification", "") == "layout-not-derivable"
    with pytest.raises(Exception):
        i3_layout(evidence_root="/elsewhere/fb-evidence-p5-0")


def test_the_production_layout_is_read_from_the_reviewed_definitions() -> None:
    layout = i3_layout()
    assert layout.state_parent == "/var/lib"
    assert (layout.state_root_name, layout.laboratory_name, layout.runs_name) == (
        "freedom-blades",
        "laboratory",
        "runs",
    )
    assert (layout.recovery_name, layout.canonical_root_name, layout.bin_name) == (
        "recovery",
        "fb-evidence-p5-0",
        "bin",
    )


def test_reversal_the_policy_admission_removed_writes(lab) -> None:
    """Row 92's negative control: with the policy parse reversed to always
    report `1`, a host whose policy is `0` is written to."""
    mutated = _mutated_verifier("parse_policy", "return 1")
    probe = FakeProbe(lab, policy=b"0\n")
    reversed_run = make(lab, probe=probe, cls=mutated["I3ControlledWriteVerifier"]).run("root")
    assert reversed_run.status.value == "verified"
    assert make(lab, probe=FakeProbe(lab, policy=b"0\n")).run("root").status is (
        Status.REFUSED_BEFORE_WRITE
    )


# ---------------------------------------------------------------------------
# 3. The four contexts, P2 and decision B — rows 93–94
# ---------------------------------------------------------------------------


def test_the_four_contexts_and_two_identities_are_the_reviewed_ones() -> None:
    assert INVOCATION_CONTEXTS == {
        Invocation.ROOT: (ContextId.T1, ContextId.CAPTURE, ContextId.P2),
        Invocation.PARTICIPANT: (ContextId.T6,),
    }
    assert Invocation.ROOT.value == "root"
    assert Invocation.PARTICIPANT.value == PARTICIPANT_IDENTITY == "ubuntu"


def test_both_invocations_verify_all_four_contexts_and_leave_nothing(lab, capsys) -> None:
    """Row 93. Root runs T1 under V4, §2.3.3 under V5 and P2 under `R/bin`;
    the participant runs T6 under V9. Each leaves the model host exactly as it
    found it."""
    before = lab.snapshot()
    root = make(lab).run("root")
    participant = make(lab).run(PARTICIPANT_IDENTITY)

    assert root.status is Status.VERIFIED and participant.status is Status.VERIFIED
    assert [outcome.context for outcome in root.contexts] == [
        ContextId.T1,
        ContextId.CAPTURE,
        ContextId.P2,
    ]
    assert [outcome.context for outcome in participant.contexts] == [ContextId.T6]
    for outcome in (*root.contexts, *participant.contexts):
        assert outcome.status is ContextStatus.VERIFIED
        assert outcome.owner_condition_observed
        assert outcome.payload_matched
        assert outcome.link_count_with_both_names == 2
        assert outcome.link_count_after_temporary_removed == 1
        assert all(obj.fate is ObjectFate.REMOVED for obj in outcome.objects)
    assert outcome_for(root, ContextId.T1).file_mode == 0o600
    assert outcome_for(root, ContextId.CAPTURE).file_mode == STORED_OBJECT_MODE
    assert outcome_for(participant, ContextId.T6).file_mode == 0o600
    assert lab.snapshot() == before
    assert root.survey.performed and not root.survey.canonical_root_present
    assert root.unreleased_roles == 0 and participant.unreleased_roles == 0


def test_p2_is_root_root_0555_published_under_the_owner_condition(monkeypatch, lab) -> None:
    """Row 94. The P2 file is chowned to the reviewed root owner and group and
    moded `0555` on its descriptor before `linkat`, and both names are observed
    at exactly that mode."""
    assert (CASE_PROGRAM_OWNER, CASE_PROGRAM_GROUP, CASE_PROGRAM_MODE) == (
        "root",
        "root",
        "0555",
    )
    seen: list[tuple[str, int]] = []
    real_fchmod, real_fchown = os.fchmod, os.fchown

    def fchmod(fd, mode):
        kind = "file" if _fd_is_file(fd) else "directory"
        seen.append((f"fchmod-{kind}", mode))
        return real_fchmod(fd, mode)

    def fchown(fd, uid, gid):
        kind = "file" if _fd_is_file(fd) else "directory"
        seen.append((f"fchown-{kind}", uid))
        return real_fchown(fd, uid, gid)

    monkeypatch.setattr(os, "fchmod", fchmod)
    monkeypatch.setattr(os, "fchown", fchown)
    run = make(lab).run("root")

    p2 = outcome_for(run, ContextId.P2)
    assert p2.status is ContextStatus.VERIFIED
    assert p2.file_mode == 0o555 and p2.applied_ownership
    assert p2.owner_condition_observed
    assert ("fchown-file", os.geteuid()) in seen
    assert ("fchmod-file", 0o555) in seen
    # Decision B's narrow exception: `R` 0700 and `R/bin` 0755, both root:root.
    assert ("fchmod-directory", CANONICAL_ROOT_MODE) in seen
    assert ("fchmod-directory", CANONICAL_BIN_MODE) in seen
    assert (CANONICAL_ROOT_MODE, CANONICAL_BIN_MODE) == (0o700, 0o755)
    kinds = [obj.kind for obj in p2.objects]
    assert kinds == [
        ObjectKind.CANONICAL_ROOT,
        ObjectKind.CANONICAL_BIN,
        ObjectKind.TEMPORARY,
        ObjectKind.PUBLISHED,
    ]
    assert not lab.canonical_root.exists()
    # The other contexts apply no ownership: their real writers apply none.
    assert not outcome_for(run, ContextId.T1).applied_ownership


# ---------------------------------------------------------------------------
# 4. Capability evidence — rows 95–96
# ---------------------------------------------------------------------------


def _status(**fields):
    return parse_status(status_text(**fields))


def test_capability_evidence_keeps_permitted_effective_and_bounding_apart() -> None:
    """Row 95. Each mask is read from its own field and classified separately."""
    fowner = 1 << CAP_FOWNER
    evidence = classify_capabilities(
        _status(cap_prm=f"{fowner:016x}", cap_eff=ZERO_MASK, cap_bnd=FULL_MASK)
    )
    membership = next(item for item in evidence.memberships if item.capability == CAP_FOWNER)
    assert (membership.permitted, membership.effective, membership.bounding) == (
        True,
        False,
        True,
    )
    assert evidence.cap_eff == 0 and evidence.cap_prm == fowner
    assert {item.name for item in evidence.memberships} == {
        "cap_dac_override",
        "cap_dac_read_search",
        "cap_fowner",
    }


@pytest.mark.parametrize("bounding", [ZERO_MASK, "0000000000000008", FULL_MASK])
def test_changing_only_capbnd_never_changes_what_is_reported_effective(bounding) -> None:
    """Row 96. `CapBnd` is never read as `CapEff`."""
    baseline = classify_capabilities(_status(cap_eff="0000000000000002", cap_bnd=ZERO_MASK))
    varied = classify_capabilities(_status(cap_eff="0000000000000002", cap_bnd=bounding))
    assert varied.cap_eff == baseline.cap_eff == 2
    assert [item.effective for item in varied.memberships] == [
        item.effective for item in baseline.memberships
    ]
    assert varied.cap_bnd == int(bounding, 16)


def test_reversal_reading_capbnd_as_capeff_is_caught() -> None:
    """Row 96's negative control: the classification with `CapEff` read from
    `CapBnd` reports an effective capability the process does not hold."""
    tree = ast.parse(VERIFIER_SOURCE)

    class Swap(ast.NodeTransformer):
        def visit_Attribute(self, node):  # noqa: N802
            self.generic_visit(node)
            if node.attr == "cap_eff" and isinstance(node.value, ast.Name) and node.value.id == "status":
                return ast.copy_location(
                    ast.Attribute(value=node.value, attr="cap_bnd", ctx=node.ctx), node
                )
            return node

    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "classify_capabilities"
    )
    Swap().visit(function)
    ast.fix_missing_locations(tree)
    namespace = _execute(tree, "i3_verifier_reversed_capability_swap")
    status = namespace["parse_status"](status_text(cap_eff=ZERO_MASK, cap_bnd=FULL_MASK))
    swapped = namespace["classify_capabilities"](status)
    assert any(item.effective for item in swapped.memberships)
    real = classify_capabilities(_status(cap_eff=ZERO_MASK, cap_bnd=FULL_MASK))
    assert not any(item.effective for item in real.memberships)


def test_capability_state_is_observed_again_at_every_link(lab) -> None:
    """At admission and immediately before each `linkat`: one read each."""
    probe = FakeProbe(lab)
    run = make(lab, probe=probe).run("root")
    assert run.status is Status.VERIFIED
    assert probe.status_reads == 1 + 3
    for outcome in run.contexts:
        assert outcome.capability_at_link is not None
        assert outcome.capability_at_link.cap_eff == int(FULL_MASK, 16)


def test_a_process_state_change_before_the_link_fails_and_cleans_up(lab) -> None:
    changed = status_text(cap_eff=ZERO_MASK)
    probe = FakeProbe(lab, statuses=[status_text(), changed])
    before = lab.snapshot()
    run = make(lab, probe=probe).run("root")

    t1 = outcome_for(run, ContextId.T1)
    assert (t1.failed_stage, t1.failure) == (Stage.OPERATION_STATE, "process-state-changed")
    assert Stage.LINK not in t1.completed
    assert run.status is Status.FAILED_NO_RESIDUE
    assert [outcome.status for outcome in run.contexts[1:]] == [ContextStatus.NOT_ATTEMPTED] * 2
    assert lab.snapshot() == before


# ---------------------------------------------------------------------------
# 5. No CAP_FOWNER claim — row 97
# ---------------------------------------------------------------------------

_ATTRIBUTION = re.compile(
    r"(requir|prov|isolat|depend|attribut|authori[sz])\w*\W+(\w+\W+){0,3}CAP_FOWNER"
    r"|CAP_FOWNER\W+(\w+\W+){0,3}(requir|prov|isolat|authori[sz])",
    re.IGNORECASE,
)


def test_no_result_claims_that_p2_required_or_proved_cap_fowner(lab) -> None:
    """Row 97. The only sentence about `CAP_FOWNER` any rendering carries is the
    fixed disclaimer, and it disclaims."""
    rendered = render_run(make(lab).run("root"))
    assert NOT_ATTRIBUTION in rendered
    assert "does not isolate, require or prove CAP_FOWNER" in NOT_ATTRIBUTION
    without = rendered.replace(NOT_ATTRIBUTION, "")
    assert "CAP_FOWNER" not in without
    assert not _ATTRIBUTION.search(without)
    assert "owner condition    : observed" in rendered


def test_no_operative_source_keeps_p2s_cap_fowner_dependency() -> None:
    from tools.phase_5_0_evidence import provisioning

    text = " ".join(" ".join(row) for row in provisioning.VERIFICATION_PROCEDURE)
    assert "still depends on `CAP_FOWNER`" not in text
    assert "`CapBnd` is never evidence of `CapEff`" in text
    trace = " ".join(provisioning.EVIDENCE_ROOT_TRACE)
    assert "narrow exception" in trace and "0700" in trace and "0755" in trace


def test_p2_and_p04_now_install_and_assert_root_root_0555() -> None:
    from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
    from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan

    plan = build_concrete_plan(APPROVED_TARGET)
    p04 = next(step for step in plan.steps if step.step_id == "P-04")
    assert "root:root 0555" in p04.purpose
    modes = {item.key: item.value for item in p04.observation_expectations}
    assert modes["mode"] == "555"
    install = next(
        step for step in plan.steps
        if step.is_effect and getattr(step.effect, "payload_source", "")
    )
    assert install.effect.mode == 0o555
    assert (install.effect.owner, install.effect.group) == ("root", "root")


# ---------------------------------------------------------------------------
# 6. Exclusive publication and the two-name observation — rows 98–100
# ---------------------------------------------------------------------------


def test_an_occupied_destination_is_never_overwritten(monkeypatch, lab) -> None:
    """Row 98. A name that appears between admission and `linkat` is claimed by
    the kernel's EEXIST: the foreign object keeps its bytes, the temporary is
    removed through its guard, and the run needs an operator."""
    real_link = os.link
    planted: list[Path] = []

    def link(source, destination, *args, **kwargs):
        if not planted:
            fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=kwargs["dst_dir_fd"])
            os.write(fd, b"somebody else's bytes")
            os.close(fd)
            planted.append(lab.laboratory / destination)
        return real_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(os, "link", link)
    run = make(lab).run("root")

    t1 = outcome_for(run, ContextId.T1)
    assert (t1.failed_stage, t1.failure) == (Stage.LINK, "object-exists")
    assert planted[0].read_bytes() == b"somebody else's bytes"
    assert [(obj.kind, obj.fate) for obj in t1.objects] == [
        (ObjectKind.TEMPORARY, ObjectFate.REMOVED)
    ]
    assert run.status is Status.FAILED_OPERATOR_ATTENTION
    assert lab.verifier_names_on_disk() == [str(planted[0].relative_to(lab.state_parent))]


def test_reversal_a_non_exclusive_link_overwrites_the_occupant(monkeypatch, lab) -> None:
    """Row 98's negative control: with the exclusive claim reversed to a rename
    onto the name, the occupant's bytes are destroyed."""

    def replacing(self, source_dirfd, source, destination_dirfd, destination):
        os.rename(source, destination, src_dir_fd=source_dirfd, dst_dir_fd=destination_dirfd)

    monkeypatch.setattr(PosixFilesystem, "linkat", replacing)
    planted: list[Path] = []
    real_rename = os.rename

    def rename(source, destination, *args, **kwargs):
        if not planted:
            fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=kwargs["dst_dir_fd"])
            os.write(fd, b"somebody else's bytes")
            os.close(fd)
            planted.append(lab.laboratory / destination)
        return real_rename(source, destination, *args, **kwargs)

    monkeypatch.setattr(os, "rename", rename)
    make(lab).run("root")
    assert planted and (
        not planted[0].exists() or planted[0].read_bytes() != b"somebody else's bytes"
    )


def test_both_names_are_one_inode_with_link_count_two_and_exact_bytes_before_removal(
    monkeypatch, lab
) -> None:
    """Row 99. At the first removal, both names already existed as one regular
    file with link count two and the pinned bytes, and the verifier had recorded
    that observation before it removed anything."""
    assert hashlib.sha256(PAYLOAD).hexdigest() == PAYLOAD_SHA256
    captured: list[tuple] = []
    real_unlink = os.unlink
    verifier = make(lab)

    def unlink(name, *args, **kwargs):
        if not captured and str(name).startswith(NAME_PREFIX):
            directory = kwargs["dir_fd"]
            temporary = name
            published = name.replace("-staged", "-linked")
            a = os.stat(temporary, dir_fd=directory, follow_symlinks=False)
            b = os.stat(published, dir_fd=directory, follow_symlinks=False)
            fd = os.open(published, os.O_RDONLY, dir_fd=directory)
            data = os.read(fd, 4096)
            os.close(fd)
            captured.append(((a.st_dev, a.st_ino), (b.st_dev, b.st_ino), a.st_nlink, data, list(verifier.events)))
        return real_unlink(name, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", unlink)
    run = verifier.run("root")

    assert run.status is Status.VERIFIED
    first, second, links, data, events = captured[0]
    assert first == second and links == 2 and data == PAYLOAD
    stages = [stage for context, stage in events if context is ContextId.T1]
    assert stages[-2:] == [Stage.LINK, Stage.TWO_NAMES]


def test_success_removes_both_names_barriers_the_parent_and_leaves_no_residue(
    monkeypatch, lab
) -> None:
    """Row 100. The containing directory's barrier follows both removals."""
    order: list[str] = []
    real_unlink, real_fsync = os.unlink, os.fsync

    def unlink(name, *args, **kwargs):
        order.append(f"unlink:{str(name).rsplit('-', 1)[-1]}")
        return real_unlink(name, *args, **kwargs)

    def fsync(fd):
        if _fd_is(fd, lab.laboratory):
            order.append("fsync:laboratory")
        return real_fsync(fd)

    monkeypatch.setattr(os, "unlink", unlink)
    monkeypatch.setattr(os, "fsync", fsync)
    before = lab.snapshot()
    run = make(lab).run("root")

    assert run.status is Status.VERIFIED
    t1_order = order[: order.index("fsync:laboratory") + 1]
    assert t1_order == ["unlink:staged", "unlink:linked", "fsync:laboratory"]
    assert lab.snapshot() == before
    assert run.survey.verifier_names_found == 0


# ---------------------------------------------------------------------------
# 7. Every injected state-boundary failure is accounted, and never success —
#    row 101
# ---------------------------------------------------------------------------


def _exclusive_open(path, flags, *args, **kwargs):
    return bool(flags & os.O_EXCL) and str(path).startswith(NAME_PREFIX)


BOUNDARIES = [
    # (id, os function, predicate factory, skip, expected stage, context, clean)
    ("temporary-create", "open", lambda lab: _exclusive_open, 0, Stage.TEMPORARY_CREATE, ContextId.T1, True),
    ("payload-write", "write", lambda lab: (lambda fd, data: _fd_is_file(fd)), 0, Stage.PAYLOAD_WRITE, ContextId.T1, True),
    ("data-barrier", "fsync", lambda lab: (lambda fd: _fd_is_file(fd)), 0, Stage.DATA_BARRIER, ContextId.T1, True),
    ("mode", "fchmod", lambda lab: (lambda fd, mode: _fd_is_file(fd)), 0, Stage.OWNERSHIP_MODE, ContextId.T1, True),
    ("p2-ownership", "fchown", lambda lab: (lambda fd, uid, gid: _fd_is_file(fd)), 0, Stage.OWNERSHIP_MODE, ContextId.P2, True),
    ("link", "link", lambda lab: (lambda *a, **k: True), 0, Stage.LINK, ContextId.T1, True),
    # Admission looks up T1's and S2.3.3's published names first, so the third
    # lookup of a published name is T1's two-name observation.
    ("two-name-stat", "stat", lambda lab: (lambda name, *a, **k: str(name).endswith("-linked")), 2, Stage.TWO_NAMES, ContextId.T1, True),
    ("two-name-read", "read", lambda lab: (lambda fd, size: _fd_is_file(fd)), 0, Stage.TWO_NAMES, ContextId.T1, True),
    ("temporary-unlink", "unlink", lambda lab: (lambda name, *a, **k: str(name).endswith("-staged")), 0, Stage.TEMPORARY_REMOVE, ContextId.T1, False),
    ("published-unlink", "unlink", lambda lab: (lambda name, *a, **k: str(name).endswith("-linked")), 0, Stage.PUBLISHED_REMOVE, ContextId.T1, False),
    ("entry-barrier", "fsync", lambda lab: (lambda fd: _fd_is(fd, lab.laboratory)), 0, Stage.ENTRY_BARRIER, ContextId.T1, False),
    ("capture-link", "link", lambda lab: (lambda *a, **k: True), 1, Stage.LINK, ContextId.CAPTURE, True),
    ("root-create", "mkdir", lambda lab: (lambda name, *a, **k: str(name) == "fb-evidence-p5-0"), 0, Stage.ROOT_CREATE, ContextId.P2, True),
    ("root-mode", "fchmod", lambda lab: (lambda fd, mode: _fd_is_dir(fd)), 0, Stage.ROOT_OWNERSHIP, ContextId.P2, True),
    ("root-barrier", "fsync", lambda lab: (lambda fd: _fd_is(fd, lab.state_parent)), 0, Stage.ROOT_BARRIER, ContextId.P2, True),
    ("bin-create", "mkdir", lambda lab: (lambda name, *a, **k: str(name) == "bin"), 0, Stage.BIN_CREATE, ContextId.P2, True),
    ("bin-mode", "fchmod", lambda lab: (lambda fd, mode: _fd_is_dir(fd)), 1, Stage.BIN_OWNERSHIP, ContextId.P2, True),
    ("p2-link", "link", lambda lab: (lambda *a, **k: True), 2, Stage.LINK, ContextId.P2, True),
    ("bin-remove", "rmdir", lambda lab: (lambda name, *a, **k: str(name) == "bin"), 0, Stage.BIN_REMOVE, ContextId.P2, False),
    ("root-remove", "rmdir", lambda lab: (lambda name, *a, **k: str(name) == "fb-evidence-p5-0"), 0, Stage.ROOT_REMOVE, ContextId.P2, False),
]


@pytest.mark.parametrize(
    "function,predicate,skip,stage,context,clean",
    [row[1:] for row in BOUNDARIES],
    ids=[row[0] for row in BOUNDARIES],
)
def test_every_injected_boundary_failure_is_accounted_and_never_success(
    monkeypatch, lab, function, predicate, skip, stage, context, clean
) -> None:
    before = lab.snapshot()
    inject(monkeypatch, function, predicate(lab), skip=skip)
    run = make(lab).run("root")

    failed = outcome_for(run, context)
    assert run.status is not Status.VERIFIED
    assert failed.status is ContextStatus.FAILED
    assert failed.failed_stage is stage, (failed.failed_stage, failed.failure)
    assert failed.failure in STAGE_FAILURES
    later = run.contexts[run.contexts.index(failed) + 1 :]
    assert all(outcome.status is ContextStatus.NOT_ATTEMPTED for outcome in later)
    _accounting_matches_disk(lab, run)
    if clean:
        assert run.status is Status.FAILED_NO_RESIDUE
        assert lab.snapshot() == before
    else:
        assert run.status is Status.FAILED_OPERATOR_ATTENTION
    assert i3_verifier_cli.EXIT_CODES[run.status] in (
        FAILED_NO_RESIDUE_EXIT_CODE,
        OPERATOR_ATTENTION_EXIT_CODE,
    )
    assert SECRET not in render_run(run)


def test_the_participant_invocation_is_accounted_the_same_way(monkeypatch, lab) -> None:
    before = lab.snapshot()
    inject(monkeypatch, "link", lambda *a, **k: True)
    run = make(lab).run(PARTICIPANT_IDENTITY)
    t6 = outcome_for(run, ContextId.T6)
    assert (t6.failed_stage, t6.failure) == (Stage.LINK, "operation-failed")
    assert run.status is Status.FAILED_NO_RESIDUE
    assert lab.snapshot() == before


def test_a_temporary_whose_creation_outcome_is_unknown_is_never_removed(monkeypatch, lab) -> None:
    """The open created the name and then reported failure: nobody recorded its
    identity, so it is residue, never removed."""

    def before(real, path, flags, mode, *, dir_fd):
        fd = real(path, flags, mode, dir_fd=dir_fd)
        os.close(fd)

    inject(monkeypatch, "open", _exclusive_open, before=before)
    run = make(lab).run("root")
    t1 = outcome_for(run, ContextId.T1)
    assert (t1.failed_stage, t1.failure) == (Stage.TEMPORARY_CREATE, "outcome-uncertain")
    assert [(obj.kind, obj.fate, obj.identity) for obj in t1.objects] == [
        (ObjectKind.TEMPORARY, ObjectFate.UNIDENTIFIED, "")
    ]
    assert run.status is Status.FAILED_OPERATOR_ATTENTION
    assert len(lab.verifier_names_on_disk()) == 1


# ---------------------------------------------------------------------------
# 8. Foreign or replaced names and directories are never removed — row 102
# ---------------------------------------------------------------------------


def test_a_replaced_published_name_is_left_alone(monkeypatch, lab) -> None:
    real_link = os.link
    moved: list[Path] = []

    def link(source, destination, *args, **kwargs):
        real_link(source, destination, *args, **kwargs)
        if not moved:
            directory = kwargs["dst_dir_fd"]
            os.rename(destination, "ours-moved-away", src_dir_fd=directory, dst_dir_fd=directory)
            fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=directory)
            os.write(fd, b"foreign")
            os.close(fd)
            moved.append(lab.laboratory / destination)

    monkeypatch.setattr(os, "link", link)
    run = make(lab).run("root")
    t1 = outcome_for(run, ContextId.T1)
    assert (t1.failed_stage, t1.failure) == (Stage.TWO_NAMES, "object-identity-mismatch")
    fates = {obj.kind: obj.fate for obj in t1.objects}
    assert fates == {ObjectKind.TEMPORARY: ObjectFate.REMOVED, ObjectKind.PUBLISHED: ObjectFate.REPLACED}
    assert moved[0].read_bytes() == b"foreign"
    assert run.status is Status.FAILED_OPERATOR_ATTENTION


def test_reversal_without_the_identity_comparison_the_foreign_object_is_removed(
    monkeypatch, lab
) -> None:
    """Row 102's negative control: `_same_object` reversed to accept any object
    removes the foreign file at the published name."""
    mutated = _mutated_verifier("_same_object", "return facts is not None")
    real_link = os.link
    moved: list[Path] = []

    def link(source, destination, *args, **kwargs):
        real_link(source, destination, *args, **kwargs)
        if not moved:
            directory = kwargs["dst_dir_fd"]
            os.rename(destination, "ours-moved-away", src_dir_fd=directory, dst_dir_fd=directory)
            fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=directory)
            os.write(fd, b"foreign")
            os.close(fd)
            moved.append(lab.laboratory / destination)

    monkeypatch.setattr(os, "link", link)
    make(lab, cls=mutated["I3ControlledWriteVerifier"]).run("root")
    assert not moved[0].exists()


def _swap_directory_at_fsync(monkeypatch, watched: Path, swapped: Path, skip: int) -> list[Path]:
    """After the watched directory's `skip`-th barrier, replace `swapped`."""
    real_fsync = os.fsync
    seen = {"count": 0}
    done: list[Path] = []

    def fsync(fd):
        result = real_fsync(fd)
        if _fd_is(fd, watched):
            seen["count"] += 1
            if seen["count"] == skip + 1 and not done:
                swapped.rename(swapped.with_name(swapped.name + "-ours"))
                swapped.mkdir()
                done.append(swapped)
        return result

    monkeypatch.setattr(os, "fsync", fsync)
    return done


def test_a_replaced_bin_directory_is_not_removed(monkeypatch, lab) -> None:
    done: list[Path] = []
    real_fsync = os.fsync

    def fsync(fd):
        result = real_fsync(fd)
        if not done and lab.canonical_bin.exists() and _fd_is(fd, lab.canonical_bin):
            lab.canonical_bin.rename(lab.canonical_root / "bin-ours")
            lab.canonical_bin.mkdir()
            done.append(lab.canonical_bin)
        return result

    monkeypatch.setattr(os, "fsync", fsync)
    run = make(lab).run("root")
    p2 = outcome_for(run, ContextId.P2)
    assert (p2.failed_stage, p2.failure) == (Stage.BIN_REMOVE, "object-identity-mismatch")
    fates = {obj.kind: obj.fate for obj in p2.objects}
    assert fates[ObjectKind.CANONICAL_BIN] is ObjectFate.REPLACED
    assert fates[ObjectKind.CANONICAL_ROOT] is ObjectFate.NOT_EMPTY
    assert lab.canonical_bin.is_dir() and (lab.canonical_root / "bin-ours").is_dir()
    assert run.status is Status.FAILED_OPERATOR_ATTENTION
    assert run.survey.canonical_root_present


def test_a_replaced_canonical_root_is_not_removed(monkeypatch, lab) -> None:
    done = _swap_directory_at_fsync(monkeypatch, lab.canonical_root, lab.canonical_root, skip=1)
    run = make(lab).run("root")
    p2 = outcome_for(run, ContextId.P2)
    assert done
    assert (p2.failed_stage, p2.failure) == (Stage.ROOT_REMOVE, "object-identity-mismatch")
    fates = {obj.kind: obj.fate for obj in p2.objects}
    assert fates[ObjectKind.CANONICAL_ROOT] is ObjectFate.REPLACED
    assert fates[ObjectKind.CANONICAL_BIN] is ObjectFate.REMOVED
    assert lab.canonical_root.is_dir()
    assert run.status is Status.FAILED_OPERATOR_ATTENTION


def test_a_foreign_temporary_name_is_never_touched(monkeypatch, lab) -> None:
    real_open = os.open
    planted: list[Path] = []

    def open_(path, flags, *args, **kwargs):
        if not planted and _exclusive_open(path, flags):
            fd = real_open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600, dir_fd=kwargs["dir_fd"])
            os.write(fd, b"foreign")
            os.close(fd)
            planted.append(lab.laboratory / path)
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(os, "open", open_)
    run = make(lab).run("root")
    t1 = outcome_for(run, ContextId.T1)
    assert (t1.failed_stage, t1.failure) == (Stage.TEMPORARY_CREATE, "object-exists")
    assert t1.objects == ()
    assert planted[0].read_bytes() == b"foreign"
    assert run.status is Status.FAILED_OPERATOR_ATTENTION


# ---------------------------------------------------------------------------
# 9. Cleanup, descriptor finalization and barrier failures — row 103
# ---------------------------------------------------------------------------


def test_a_cleanup_barrier_failure_is_non_success(monkeypatch, lab) -> None:
    inject(monkeypatch, "link", lambda *a, **k: True)
    inject(monkeypatch, "fsync", lambda fd: _fd_is(fd, lab.laboratory))
    run = make(lab).run("root")
    t1 = outcome_for(run, ContextId.T1)
    assert t1.failed_stage is Stage.LINK
    assert t1.cleanup_barrier_failures == 1
    assert all(obj.fate is ObjectFate.REMOVED for obj in t1.objects)
    assert run.status is Status.FAILED_OPERATOR_ATTENTION


def test_a_write_descriptor_that_is_not_released_is_non_success(monkeypatch, lab) -> None:
    """The descriptor is released and the release reports failure: it is
    counted, never retried, and the run stops before `linkat`."""
    inject(
        monkeypatch,
        "close",
        lambda fd: _fd_is_file(fd),
        before=lambda real, fd: real(fd),
    )
    run = make(lab).run("root")
    t1 = outcome_for(run, ContextId.T1)
    assert (t1.failed_stage, t1.failure) == (Stage.WRITE_RELEASE, "descriptor-not-released")
    assert t1.descriptor_release_failures == 1
    assert Stage.LINK not in t1.completed
    assert all(obj.fate is ObjectFate.REMOVED for obj in t1.objects)
    assert run.status is Status.FAILED_OPERATOR_ATTENTION


def test_a_directory_descriptor_that_is_not_released_at_the_end_is_non_success(
    monkeypatch, lab
) -> None:
    real_close = os.close
    state = {"armed": False}

    def close(fd):
        if state["armed"] and _fd_is(fd, lab.recovery):
            real_close(fd)
            raise OSError(errno.EIO, OS_MESSAGE)
        return real_close(fd)

    verifier = make(lab)
    real_survey = I3ControlledWriteVerifier._survey

    def survey(self, session):
        result = real_survey(self, session)
        state["armed"] = True
        return result

    monkeypatch.setattr(I3ControlledWriteVerifier, "_survey", survey)
    monkeypatch.setattr(os, "close", close)
    run = verifier.run("root")
    assert all(outcome.status is ContextStatus.VERIFIED for outcome in run.contexts)
    assert run.unreleased_roles == 1
    assert run.status is Status.FAILED_OPERATOR_ATTENTION


def test_reversal_ignoring_residue_would_report_a_clean_failure(monkeypatch, lab) -> None:
    """Row 103's negative control: `final_status` reversed to ignore accounting
    reports a run with residue as `failed-no-residue`."""
    mutated = _mutated_verifier(
        "final_status",
        "return Status.VERIFIED if all(o.status is ContextStatus.VERIFIED for o in contexts) "
        "else Status.FAILED_NO_RESIDUE",
    )
    inject(monkeypatch, "unlink", lambda name, *a, **k: str(name).endswith("-staged"))
    reversed_run = make(lab, cls=mutated["I3ControlledWriteVerifier"]).run("root")
    assert reversed_run.status.value == "failed-no-residue"
    assert lab.verifier_names_on_disk()


def test_the_final_status_needs_every_object_removed_and_a_clean_survey() -> None:
    verified = ContextOutcome(
        context=ContextId.T1,
        status=ContextStatus.VERIFIED,
        objects=(TrackedObject(ContextId.T1, ObjectKind.TEMPORARY, "1:2", ObjectFate.REMOVED),),
    )
    clean = SurveyResult(performed=True)
    assert verifier_module.final_status((verified,), clean, 0) is Status.VERIFIED
    assert verifier_module.final_status((verified,), clean, 1) is Status.FAILED_OPERATOR_ATTENTION
    for survey in (
        SurveyResult(performed=False),
        SurveyResult(performed=True, failed=True),
        SurveyResult(performed=True, verifier_names_found=1),
        SurveyResult(performed=True, canonical_root_present=True),
    ):
        assert verifier_module.final_status((verified,), survey, 0) is (
            Status.FAILED_OPERATOR_ATTENTION
        )
    residue = ContextOutcome(
        context=ContextId.T1,
        status=ContextStatus.VERIFIED,
        objects=(TrackedObject(ContextId.T1, ObjectKind.TEMPORARY, "1:2", ObjectFate.PRESENT),),
    )
    assert verifier_module.final_status((residue,), clean, 0) is Status.FAILED_OPERATOR_ATTENTION


# ---------------------------------------------------------------------------
# 10. Safe output — row 104
# ---------------------------------------------------------------------------

_PRINTABLE = re.compile(r"\A[\x20-\x7e—\n]*\Z")


def test_malformed_host_data_and_exception_text_never_reach_the_output(
    monkeypatch, lab, capsys
) -> None:
    """Row 104. Secret-looking host data, account-lookup text and an
    operating-system message are each injected, and none is printed."""
    renders = []
    probe = FakeProbe(lab, status=status_text(extra=f"Secret:\t{SECRET}\n"))
    renders.append(render_run(make(lab, probe=probe).run("root")))
    renders.append(render_run(make(lab, probe=FakeProbe(lab, status=status_text(cap_eff=SECRET[:16]))).run("root")))
    renders.append(render_run(make(lab, accounts=FakeAccounts(unknown="root")).run("root")))
    renders.append(render_run(make(lab, probe=FakeProbe(lab, mountinfo=f"1 2 3 {SECRET}\n".encode())).run("root")))
    inject(monkeypatch, "link", lambda *a, **k: True)
    renders.append(render_run(make(lab).run("root")))
    for rendered in renders:
        assert SECRET not in rendered and "hunter2" not in rendered
        assert "Traceback" not in rendered and "Errno" not in rendered
        assert str(lab.state_parent) not in rendered
        assert _PRINTABLE.match(rendered)


def test_values_outside_the_vocabulary_render_as_unrecognized() -> None:
    hostile = VerificationRun(
        invocation=Invocation.ROOT,
        status=Status.FAILED_OPERATOR_ATTENTION,
        contexts=(
            ContextOutcome(
                context=ContextId.T1,
                status=ContextStatus.FAILED,
                nonce=f"../../{SECRET}",
                failed_stage=Stage.LINK,
                failure=f"{SECRET} is not a classification",
                object_identity=f"/etc/{SECRET}",
                file_mode=-5,
                link_count_with_both_names=-1,
                objects=(TrackedObject(ContextId.T1, ObjectKind.TEMPORARY, f"1:{SECRET}"),),
            ),
        ),
        survey=SurveyResult(performed=True),
    )
    rendered = render_run(hostile)
    assert SECRET not in rendered and "/etc/" not in rendered
    assert rendered.count("unrecognized") >= 5


def test_the_refusal_field_is_admitted_by_membership() -> None:
    run = VerificationRun(
        invocation=None, status=Status.REFUSED_BEFORE_WRITE, refusal=f"{SECRET}"
    )
    rendered = render_run(run)
    assert SECRET not in rendered and "unrecognized" in rendered


def test_an_unclassified_exception_prints_nothing_about_itself(monkeypatch, capsys) -> None:
    class Exploding:
        def __init__(self, **_kwargs) -> None:
            pass

        def run(self, _invocation):
            raise RuntimeError(f"{SECRET} at /var/lib/fb-evidence-p5-0")

    monkeypatch.setattr(i3_verifier_cli, "I3ControlledWriteVerifier", Exploding)
    monkeypatch.setattr(i3_verifier_cli, "SystemIdentityLookup", lambda: None)
    monkeypatch.setattr(i3_verifier_cli, "ProcHostProbe", lambda: None)
    assert main([ARM_FLAG, "--identity", "root"]) == UNCLASSIFIED_EXIT_CODE
    printed = capsys.readouterr()
    assert SECRET not in printed.out + printed.err
    assert "fb-evidence" not in printed.out + printed.err


def test_the_exit_codes_are_distinct_and_only_verified_is_zero() -> None:
    codes = [
        VERIFIED_EXIT_CODE,
        NOT_ARMED_EXIT_CODE,
        REFUSED_EXIT_CODE,
        FAILED_NO_RESIDUE_EXIT_CODE,
        UNCLASSIFIED_EXIT_CODE,
        OPERATOR_ATTENTION_EXIT_CODE,
    ]
    assert len(set(codes)) == len(codes)
    assert VERIFIED_EXIT_CODE == 0 and 0 not in codes[1:]
    assert set(i3_verifier_cli.EXIT_CODES) == set(Status)


def test_the_cli_exit_status_follows_the_run(monkeypatch, lab, capsys) -> None:
    real = I3ControlledWriteVerifier

    def factory(**kwargs):
        return real(
            lookup=FakeAccounts(), probe=FakeProbe(lab), armed=kwargs["armed"], layout=lab.layout
        )

    monkeypatch.setattr(i3_verifier_cli, "I3ControlledWriteVerifier", factory)
    monkeypatch.setattr(i3_verifier_cli, "SystemIdentityLookup", lambda: None)
    monkeypatch.setattr(i3_verifier_cli, "ProcHostProbe", lambda: None)
    assert main([ARM_FLAG, "--identity", "root"]) == VERIFIED_EXIT_CODE
    assert main([ARM_FLAG, "--identity", PARTICIPANT_IDENTITY]) == VERIFIED_EXIT_CODE
    (lab.recovery / f"{NAME_PREFIX}stale").write_bytes(b"")
    assert main([ARM_FLAG, "--identity", "root"]) == REFUSED_EXIT_CODE
    printed = capsys.readouterr()
    assert "prior-verifier-residue" in printed.out
    assert "NOT VERIFIED" in printed.err


# ---------------------------------------------------------------------------
# 11. Names, payload, primitive and structure — row 105
# ---------------------------------------------------------------------------


def test_names_are_outside_every_lifecycle_ledger_recovery_and_case_program_grammar() -> None:
    temporary, published = verifier_names("0" * 32)
    for name in (temporary, published):
        assert name_is_admissible(name)
        with pytest.raises(ParticipantRefused):
            validate_run_identifier(name)
        assert not name.endswith(TEMPORARY_SUFFIX) and not name.endswith(RECORD_SUFFIX)
        assert name not in {
            LABORATORY_LAYOUT.record_name,
            f"{LABORATORY_LAYOUT.record_name}.tmp",
            "case",
            "case-program",
            ".case-program.tmp",
        }
    assert temporary != published
    for bad in ("lifecycle.json", "run-1", ".fb-i3-verify-x.tmp", f"{NAME_PREFIX}{'0' * 32}.tmp"):
        assert not name_is_admissible(bad)


def test_the_payload_is_fixed_harmless_and_pinned() -> None:
    assert hashlib.sha256(PAYLOAD).hexdigest() == PAYLOAD_SHA256
    assert PAYLOAD.isascii() and len(PAYLOAD) < 256


def test_there_is_one_exclusive_link_and_the_fused_publication_uses_it() -> None:
    """One `linkat` in the package; `renameat(noreplace=True)` calls it."""
    occurrences = []
    for path in sorted(PACKAGE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "link"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "os"
            ):
                occurrences.append(path.name)
    assert occurrences == ["descriptors.py"]
    tree = ast.parse(Path(descriptors_module.__file__).read_text(encoding="utf-8"))
    renameat = next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "renameat"
    )
    assert any(
        isinstance(node, ast.Attribute) and node.attr == "linkat" for node in ast.walk(renameat)
    )
    verifier_tree = ast.parse(VERIFIER_SOURCE)
    attributes = {node.attr for node in ast.walk(verifier_tree) if isinstance(node, ast.Attribute)}
    assert "linkat" in attributes and "renameat" not in attributes


def test_the_verifier_reaches_no_participant_harness_or_executor() -> None:
    forbidden = {
        "cli", "executor", "materializer", "case_program", "lifecycle_record",
        "run_ledger", "host_lock", "participants", "evidence_cli", "boundary",
    }
    for source, allowed in ((VERIFIER_SOURCE, set()), (CLI_SOURCE, {"boundary"})):
        tree = ast.parse(source)
        imported = {
            node.module.split(".")[-1]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not (imported & (forbidden - allowed)), imported & forbidden
        attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        assert not attributes & {"environ", "getenv", "system", "popen", "execve"}
        assert "EVIDENCE_ROLE" not in {
            node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
        }


def test_the_standing_gates_are_unchanged() -> None:
    from tools.phase_5_0_evidence import reservation
    from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
    from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan

    assert build_concrete_plan(APPROVED_TARGET).is_executable is False
    assert reservation.REAL_EXECUTION_REFUSAL
    assert CAP_DAC_OVERRIDE == 1 and CAP_FOWNER == 3


# ---------------------------------------------------------------------------
# C-P5.0-LAB-I3-R3, 2026-09-20 — the two ruled creation modes
#
# Peter accepted the C-P5.0-LAB-I3-R2 review and ruled on the two discrepancies
# it reported. The four tests below are the regression coverage that ruling
# requires: canonical `R` is created `0700`; P2 alone creates its exclusive
# publication temporary `0500`; T1, T6 and §2.3.3 keep the shared `0600`
# default; and P2 still reaches `root:root 0555` on the descriptor, and is read
# back at it, before `linkat`.
#
# Nothing here confirms a target fact, and none of it is authority for
# `--execute`. I3 stays unconfirmed.
# ---------------------------------------------------------------------------


def _creation_modes(monkeypatch) -> list[int]:
    """Every mode argument given to an exclusive `O_CREAT|O_EXCL` file open."""
    modes: list[int] = []
    real_open = os.open

    def opener(path, flags, mode=0o777, **kwargs):
        if flags & os.O_CREAT and flags & os.O_EXCL and not flags & os.O_DIRECTORY:
            modes.append(mode)
        return real_open(path, flags, mode, **kwargs)

    monkeypatch.setattr(os, "open", opener)
    return modes


def test_mkroot_creates_canonical_r_as_0700_not_0755() -> None:
    """**Ruling 1.** The concrete plan creates canonical `R` `root:root 0700`.

    The mode the reviewed case program's `mkroot` verb passes to `mkdir(2)` and
    re-applies with `fchmod(2)`, the mode `B3-02` reads back and compares, and
    the mode the verifier reproduces under decision B's narrow exception are one
    value. `0755` was the C-P5.0-LAB-I3-R2 discrepancy and is gone.
    """
    from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
    from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan
    from tools.phase_5_0_evidence.execution import case_program

    assert case_program.ROOT_DIRECTORY_MODE == 0o700
    # The verifier's narrow-exception constant is the same value.
    assert CANONICAL_ROOT_MODE == 0o700
    # `R/bin` is a separate item and is deliberately **not** narrowed.
    assert CANONICAL_BIN_MODE == 0o755

    plan = build_concrete_plan(APPROVED_TARGET)
    read_back = next(step for step in plan.steps if step.step_id == "B3-02")
    expectations = {
        item.key: item.value for item in read_back.observation_expectations
    }
    assert expectations["mode"] == "700"
    assert (expectations["uid"], expectations["gid"]) == ("0", "0")
    assert expectations["file_type"] == "directory"
    assert "mode 700" in read_back.expected_result
    assert "755" not in read_back.expected_result


def test_p2_alone_creates_its_temporary_0500(monkeypatch, lab) -> None:
    """**Ruling 2.** P2's exclusive temporary is created `0500`.

    The value is `case_runtime.CASE_PROGRAM_TEMPORARY_MODE` and it is passed at
    P2's call, not set as the shared default. The temporary's pathname mode does
    not become the published mode: P2 still publishes `0555`.
    """
    assert CASE_PROGRAM_TEMPORARY_MODE == "0500"
    assert int(CASE_PROGRAM_TEMPORARY_MODE, 8) != descriptors_module.EXCLUSIVE_CREATION_MODE

    modes = _creation_modes(monkeypatch)
    run = make(lab).run("root")

    p2 = outcome_for(run, ContextId.P2)
    assert p2.status is ContextStatus.VERIFIED
    assert 0o500 in modes
    # Exactly one exclusive file creation in the root invocation is 0500: P2's.
    assert modes.count(0o500) == 1
    # And the published mode is still the ruled 0555, not the creation mode.
    assert p2.file_mode == 0o555


def test_t1_capture_and_t6_keep_the_shared_0600_default(monkeypatch, lab) -> None:
    """**Ruling 5.** T1, T6 and §2.3.3 retain `EXCLUSIVE_CREATION_MODE`.

    The explicit creation-mode input exists for P2 alone. Its default is the
    unchanged `0600`, and the three other publication contexts pass no value, so
    every exclusive creation they make is still `0600`.
    """
    assert descriptors_module.EXCLUSIVE_CREATION_MODE == 0o600

    # The root invocation runs T1, §2.3.3 and P2. Every creation but P2's is
    # the default.
    modes = _creation_modes(monkeypatch)
    root_run = make(lab).run("root")
    assert root_run.status is Status.VERIFIED
    assert sorted(modes) == [0o500, 0o600, 0o600]

    # The `ubuntu` invocation runs T6 alone, and takes the default too.
    ubuntu_modes = _creation_modes(monkeypatch)
    ubuntu_run = make(lab).run("ubuntu")
    assert ubuntu_run.status is Status.VERIFIED
    assert ubuntu_modes == [0o600]

    # The default is a default, not a value the three contexts restate: the
    # signature carries it, and `create_file` is called without a mode there.
    signature = inspect.signature(PosixFilesystem.create_file)
    assert signature.parameters["mode"].default == 0o600
    assert signature.parameters["mode"].kind is inspect.Parameter.KEYWORD_ONLY


def test_p2_is_root_root_0555_on_the_descriptor_before_linkat(monkeypatch, lab) -> None:
    """**Ruling 4.** P2 applies and reads back `root:root 0555` before publication.

    The `0500` creation mode is not the published mode, and the already-open
    writable descriptor stays the authority: the payload is written and
    synchronized through it, the ownership and final mode are applied to it, and
    the read-back that gates `linkat` sees `0555`.
    """
    order: list[str] = []
    real_fchmod, real_fchown, real_link = os.fchmod, os.fchown, os.link
    observed: dict[str, int] = {}

    def fchmod(fd, mode):
        if _fd_is_file(fd):
            order.append(f"fchmod:{mode:o}")
        return real_fchmod(fd, mode)

    def fchown(fd, uid, gid):
        if _fd_is_file(fd):
            order.append(f"fchown:{uid}:{gid}")
        return real_fchown(fd, uid, gid)

    def link(src, dst, *, src_dir_fd=None, dst_dir_fd=None, follow_symlinks=True):
        if isinstance(src, str) and src.startswith(NAME_PREFIX) and src_dir_fd is not None:
            facts = os.stat(src, dir_fd=src_dir_fd, follow_symlinks=False)
            observed.setdefault(src, stat.S_IMODE(facts.st_mode))
            order.append(f"link:{stat.S_IMODE(facts.st_mode):o}")
        return real_link(
            src, dst, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd,
            follow_symlinks=follow_symlinks,
        )

    monkeypatch.setattr(os, "fchmod", fchmod)
    monkeypatch.setattr(os, "fchown", fchown)
    monkeypatch.setattr(os, "link", link)

    run = make(lab).run("root")
    p2 = outcome_for(run, ContextId.P2)
    assert p2.status is ContextStatus.VERIFIED
    assert p2.applied_ownership and p2.owner_condition_observed
    assert p2.file_mode == 0o555

    # Each of the root invocation's three links sees its own context's final
    # mode — T1 `0600`, §2.3.3 `STORED_OBJECT_MODE`, P2 the ruled `0555`. The
    # `0500` P2's temporary was created with reached no link at all.
    assert observed and set(observed.values()) == {
        descriptors_module.EXCLUSIVE_CREATION_MODE,
        STORED_OBJECT_MODE,
        0o555,
    }
    assert 0o500 not in set(observed.values())

    # And for P2 the descriptor carried fchown then fchmod 0555 before its link.
    p2_chmod = order.index("fchmod:555")
    assert order.index(f"fchown:{os.geteuid()}:{os.getegid()}") < p2_chmod
    assert p2_chmod < order.index("link:555")
