"""Conflict **C-2**: the Option-B interpreter prefix, the closed case-program
grammar, and every operation the program implements.

The suite has three halves and they check different things:

* **the planning-tier validator** (`case_runtime.validate_case_vector`) — what
  may be *planned*, checked positively against the reviewed shape and negatively
  against every deviation the R11 brief names: an unknown verb, an additional
  interpreter flag, an omitted isolation flag, a reordered prefix, a relative
  path, a target outside the disposable root, an arbitrary script path and a
  trailing argument;
* **the program's own refusals** — the same list again, from the program's own
  constants, because a check made only by the caller is a check an edited caller
  can skip; and
* **the operations** — each verb run for real against a directory this suite
  creates, so *"the program does what the plan says it does"* is a fact rather
  than a docstring.

**Nothing here starts a process.** The program is imported and its `main()` is
called in-process; the reviewed vector is validated as data. No test reads the
host's account database, alters a filesystem flag outside `tmp_path`, invokes
systemd, uses SSH or touches `oracle-test`.
"""
from __future__ import annotations

import ast
import errno as errno_module
import io
import os
import re
import stat
import tokenize
from pathlib import Path

import pytest

from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
from tools.phase_5_0_evidence.case_runtime import (
    BOOTSTRAP_VERBS,
    CASE_PROGRAM_GROUP,
    CASE_PROGRAM_MODE,
    CASE_PROGRAM_OWNER,
    CASE_PROGRAM_SOURCE,
    CASE_PROGRAM_SOURCE_PATH,
    CASE_VERBS,
    EXIT_OBSERVATION_UNAVAILABLE,
    EXIT_VECTOR_REFUSED,
    GENERATION_LINK_NAME,
    INTERPRETER_FLAGS,
    INTERPRETER_PATH,
    OPEN_MODES,
    REFUSAL_EXIT_CODES,
    SECUREBITS_MAX,
    WRITE_MODES,
    build_bootstrap_vector,
    build_case_vector,
    case_program_path,
    refused_with,
)
from tools.phase_5_0_evidence.capability import EVIDENCE_IDENTITIES
from tools.phase_5_0_evidence.capture import (
    UNEXPECTED_KEY_MARKER,
    CapturePolicy,
    sanitize,
)
from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan
from tools.phase_5_0_evidence.errors import PlanRefused
from tools.phase_5_0_evidence.execution import case_program
from tools.phase_5_0_evidence.plan import PERMITTED_EXECUTABLES, validate_argv
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES
from tools.phase_5_0_evidence.targets import REPOSITORY_ROOT

TARGET = APPROVED_TARGET
ROOT = TARGET.root_path

#: The repository root, for the source-level assertion about the native call.
SOURCE_ROOT = Path(__file__).resolve().parents[2]
PROGRAM = case_program_path(TARGET)


def reviewed(*arguments: str) -> tuple[str, ...]:
    """The reviewed vector shape, assembled without the validator."""
    return (INTERPRETER_PATH, *INTERPRETER_FLAGS, PROGRAM, *arguments)


# ---------------------------------------------------------------------------
# The interpreter is admitted here and nowhere else
# ---------------------------------------------------------------------------


def test_the_interpreter_is_not_a_member_of_the_general_command_surface() -> None:
    """Option B's stated cost, and the thing that makes it not apply.

    R10 §R10.0 recorded Option B as *"a general-purpose interpreter joins
    `PERMITTED_EXECUTABLES`"*. It does not: the set is unchanged, and the
    interpreter reaches a vector only through the grammar below.
    """
    assert INTERPRETER_PATH not in PERMITTED_EXECUTABLES


def test_an_arbitrary_python_command_is_not_expressible() -> None:
    for argv in (
        (INTERPRETER_PATH, "-c", "print(1)"),
        (INTERPRETER_PATH, "-I", "-S", "-c", "print(1)"),
        (INTERPRETER_PATH, "-I", "-S", "-m", "http.server"),
        (INTERPRETER_PATH,),
        (INTERPRETER_PATH, "-I", "-S"),
    ):
        with pytest.raises(PlanRefused):
            validate_argv(argv, target=TARGET)


def test_the_reviewed_prefix_is_accepted_for_every_verb() -> None:
    """One positive case per verb, built from the table rather than listed.

    **R16.** The bootstrap verbs are built from the bootstrap program path and
    every other verb from the installed one, because conflict C-8's partition is
    total: neither copy runs the other half of the table.
    """
    arguments = {
        "target_path": f"{ROOT}/probe/stage1.target",
        "open_mode": "rdonly",
        "write_mode": "wronly",
        "link_name": GENERATION_LINK_NAME,
        "root_path": ROOT,
        # **r6 §6.2.** An index into the table the step inherits, and one path
        # component. Descriptor 3 is the first entry of a declared set.
        "dirfd": "3",
        "component": "stage1.target",
    }
    for name, spec in CASE_VERBS.items():
        bootstrap = name in BOOTSTRAP_VERBS
        build = build_bootstrap_vector if bootstrap else build_case_vector
        vector = build(
            TARGET, name, *[arguments[kind.value] for kind in spec.arguments]
        )
        assert vector[0] == INTERPRETER_PATH
        assert vector[1:3] == INTERPRETER_FLAGS
        assert vector[3] == (CASE_PROGRAM_SOURCE_PATH if bootstrap else PROGRAM)
        assert vector[4] == name
        assert len(vector) == 5 + spec.arity
        assert validate_argv(vector, target=TARGET) == vector


REFUSED_VECTORS = [
    ("a different interpreter", reviewed("statvfs", f"{ROOT}/journal")[1:]),
    (
        "a relative interpreter",
        ("python3", *INTERPRETER_FLAGS, PROGRAM, "statvfs", f"{ROOT}/journal"),
    ),
    (
        "the isolation flag omitted",
        (INTERPRETER_PATH, "-S", PROGRAM, "statvfs", f"{ROOT}/journal"),
    ),
    (
        "the no-site flag omitted",
        (INTERPRETER_PATH, "-I", PROGRAM, "statvfs", f"{ROOT}/journal"),
    ),
    (
        "the prefix reordered",
        (INTERPRETER_PATH, "-S", "-I", PROGRAM, "statvfs", f"{ROOT}/journal"),
    ),
    (
        "an additional interpreter flag",
        (INTERPRETER_PATH, "-I", "-S", "-v", PROGRAM, "statvfs", f"{ROOT}/journal"),
    ),
    ("an arbitrary script path", reviewed()[:3] + ("/usr/bin/whatever", "statvfs", ROOT)),
    (
        "a case program outside the root",
        (INTERPRETER_PATH, *INTERPRETER_FLAGS, "/var/lib/other/case", "identity"),
    ),
    ("an unknown verb", reviewed("chmod", f"{ROOT}/journal")),
    ("too few arguments", reviewed("rename", f"{ROOT}/a")),
    ("a trailing argument", reviewed("unlink", f"{ROOT}/a", f"{ROOT}/b")),
    ("an argument to a verb that takes none", reviewed("identity", f"{ROOT}/a")),
    ("an unreviewed open mode", reviewed("open", "rdwr", f"{ROOT}/a")),
    ("an unreviewed write mode", reviewed("pwrite", "rdonly", f"{ROOT}/a")),
    ("a target outside the disposable root", reviewed("unlink", "/etc/passwd")),
    ("the disposable root itself", reviewed("unlink", ROOT)),
    ("a relative target", reviewed("unlink", "journal/000001.journal")),
    ("a target with a relative segment", reviewed("unlink", f"{ROOT}/../etc/passwd")),
    ("a target in a prefix-sharing sibling", reviewed("unlink", f"{ROOT}x/a")),
    ("an absolute symlink target", reviewed("symlink", f"{ROOT}/journal/current", f"{ROOT}/x")),
    ("a symlink target with a separator", reviewed("symlink", f"{ROOT}/journal/current", "a/b")),
    ("a symlink target that escapes", reviewed("symlink", f"{ROOT}/journal/current", "..")),
    ("another generation name", reviewed("symlink", f"{ROOT}/journal/current", "000002.journal")),
]


@pytest.mark.parametrize(
    "label, argv", REFUSED_VECTORS, ids=[case[0] for case in REFUSED_VECTORS]
)
def test_a_vector_the_grammar_does_not_describe_is_refused(label: str, argv) -> None:
    with pytest.raises(PlanRefused):
        validate_argv(argv, target=TARGET)


# ---------------------------------------------------------------------------
# The two executables that exec something else
# ---------------------------------------------------------------------------


def test_a_capsh_tail_is_validated_by_the_same_grammar() -> None:
    good = (
        "/usr/sbin/capsh",
        "--secbits=4",
        f"--shell={INTERPRETER_PATH}",
        "--",
        *INTERPRETER_FLAGS,
        PROGRAM,
        "identity",
    )
    assert validate_argv(good, target=TARGET) == good


@pytest.mark.parametrize(
    "argv",
    [
        # `--shell=` names something the grammar does not admit.
        ("/usr/sbin/capsh", "--shell=/usr/bin/id", "--", "identity"),
        # An empty tail is an interactive shell.
        ("/usr/sbin/capsh", f"--shell={INTERPRETER_PATH}", "--"),
        # Two shells: which one execs is not a question a reviewer should have.
        (
            "/usr/sbin/capsh",
            f"--shell={INTERPRETER_PATH}",
            "--shell=/usr/bin/id",
            "--",
            *INTERPRETER_FLAGS,
            PROGRAM,
            "identity",
        ),
        # A tail that is not the reviewed prefix.
        (
            "/usr/sbin/capsh",
            f"--shell={INTERPRETER_PATH}",
            "--",
            "-c",
            "print(1)",
        ),
    ],
)
def test_a_capsh_step_cannot_hide_an_unreviewed_program(argv) -> None:
    with pytest.raises(PlanRefused):
        validate_argv(argv, target=TARGET)


def test_a_systemd_run_payload_is_validated_by_the_same_grammar() -> None:
    good = (
        "/usr/bin/systemd-run",
        "--unit=fb-evidence-s4.service",
        "--wait",
        "--",
        INTERPRETER_PATH,
        *INTERPRETER_FLAGS,
        PROGRAM,
        "append",
        f"{ROOT}/probe/s4-1.target",
    )
    assert validate_argv(good, target=TARGET) == good

    with pytest.raises(PlanRefused):
        validate_argv(
            ("/usr/bin/systemd-run", "--unit=x.service", "--", "/usr/bin/id"),
            target=TARGET,
        )


def test_an_end_of_options_marker_is_not_treated_as_an_exec_delegation() -> None:
    """`rm --force -- PATH` and `rmdir -- PATH` are unaffected.

    The rule reaches `capsh` and `systemd-run` by name. Applying it to every
    `--` would refuse the removal vectors the plan has always carried, which
    would be a guard that fires on the wrong thing. (`chattr +a -- PATH` was the
    third example here until r6 §6.4 retired that executable; `lsattr` keeps the
    same shape and is still permitted.)
    """
    for argv in (
        ("/usr/bin/lsattr", "--", f"{ROOT}/journal/000001.journal"),
        ("/usr/bin/rm", "--force", "--", f"{ROOT}/journal/000001.journal"),
        ("/usr/bin/rmdir", "--", ROOT),
    ):
        assert validate_argv(argv, target=TARGET) == argv


# ---------------------------------------------------------------------------
# The two tiers agree about the program
# ---------------------------------------------------------------------------


def test_the_case_programs_verb_table_matches_the_planning_tiers() -> None:
    assert set(case_program.VERBS) == set(CASE_VERBS)
    for name, spec in CASE_VERBS.items():
        assert case_program.VERBS[name] == tuple(
            kind.value for kind in spec.arguments
        ), name


def test_the_open_and_write_mode_tables_match() -> None:
    assert tuple(case_program.OPEN_FLAGS) == OPEN_MODES
    assert tuple(case_program.WRITE_FLAGS) == WRITE_MODES


def test_the_refusal_exit_code_tables_match_by_errno_name() -> None:
    """Mirrored by name on one side and by number on the other, on purpose.

    The planning tier states the errno a case expects; the program states the
    number the host uses for it. This is where the two meet.
    """
    by_name = {
        errno_module.errorcode[number]: code
        for number, code in case_program.REFUSAL_EXIT_CODES.items()
    }
    for name, code in REFUSAL_EXIT_CODES.items():
        assert by_name.get(name, code) == code, name
    assert set(REFUSAL_EXIT_CODES.values()) == set(
        case_program.REFUSAL_EXIT_CODES.values()
    )
    assert case_program.EXIT_VECTOR_REFUSED == EXIT_VECTOR_REFUSED


def test_refused_with_names_an_errno_rather_than_any_non_zero_exit() -> None:
    assert refused_with("EROFS") == (REFUSAL_EXIT_CODES["EROFS"],)
    assert 0 not in refused_with("EPERM", "EACCES")
    assert EXIT_VECTOR_REFUSED not in refused_with("EPERM", "EACCES")
    with pytest.raises(PlanRefused):
        refused_with("ENOSPC")
    with pytest.raises(PlanRefused):
        refused_with()


# ---------------------------------------------------------------------------
# Source bytes are installed bytes
# ---------------------------------------------------------------------------


def test_the_reviewed_source_is_covered_by_the_review_manifest() -> None:
    assert CASE_PROGRAM_SOURCE in COVERED_SOURCES
    assert CASE_PROGRAM_SOURCE_PATH == f"{REPOSITORY_ROOT}/{CASE_PROGRAM_SOURCE}"


def test_the_plan_installs_the_reviewed_source_byte_for_byte() -> None:
    """The installed bytes are the covered source's. No build step exists.

    The manifest's digest for the source is therefore also the installation
    digest, which is the property R10 §R10.0 showed a compiled program cannot
    have. **r6 §6.4, C-P5.0-LAB-I-R1:** the `install` vector that used to carry
    this is retired, and P2's effect names the covered source instead — so the
    digest the executor compares against is the manifest's rather than a file's.
    """
    plan = build_concrete_plan()
    installs = [
        step
        for step in plan.steps
        if step.is_effect and step.effect.kind.value == "install_payload"
    ]
    assert len(installs) == 1
    step = installs[0]
    assert step.argv == ()
    assert step.effect.path == PROGRAM
    assert step.effect.payload_source == CASE_PROGRAM_SOURCE
    assert step.mutation_ids == (f"file:{PROGRAM}",)
    assert step.effect.mode == int(CASE_PROGRAM_MODE, 8)
    assert step.effect.owner == CASE_PROGRAM_OWNER
    assert step.effect.group == CASE_PROGRAM_GROUP


def test_no_generated_step_builds_downloads_or_compiles_the_program() -> None:
    plan = build_concrete_plan()
    # Compared per **path component**, not as a substring: `--pipe` contains
    # "pip" and a substring scan would fail on the Stage-4 vectors while telling
    # nobody anything about a package manager.
    forbidden = {"gcc", "cc", "g++", "make", "curl", "wget", "pip", "pip3", "uv", "git"}
    for step in (*plan.steps, *plan.cleanup_plan.steps):
        for argument in step.argv:
            if argument.startswith("/"):
                assert argument.rsplit("/", 1)[-1] not in forbidden, step.step_id
        if step.argv:
            assert step.argv[0].rsplit("/", 1)[-1] not in forbidden, step.step_id


# ---------------------------------------------------------------------------
# The program refuses the same things, from its own constants
# ---------------------------------------------------------------------------


class Recorder:
    """Collects the program's output without a process or a file."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def write(self, text: str) -> None:
        self.lines.append(text)

    def observations(self) -> dict[str, str]:
        found: dict[str, str] = {}
        for line in "".join(self.lines).splitlines():
            key, _, value = line.partition("=")
            found.setdefault(key, value)
        return found


def run_case(arguments, *, program_path=None, isolated=True, no_site=True):
    stream = Recorder()
    code = case_program.main(
        list(arguments),
        program_path=case_program.CASE_PROGRAM_PATH
        if program_path is None
        else program_path,
        isolated=isolated,
        no_site=no_site,
        stream=stream,
    )
    return code, stream.observations()


def test_the_program_refuses_when_isolated_mode_is_not_in_effect() -> None:
    for isolated, no_site in ((False, True), (True, False), (False, False)):
        code, observed = run_case(
            ["identity"], isolated=isolated, no_site=no_site
        )
        assert code == case_program.EXIT_VECTOR_REFUSED
        assert observed["result"] == "vector-refused"


def test_the_program_refuses_when_it_is_not_the_installed_program() -> None:
    code, observed = run_case(["identity"], program_path="/tmp/copy-of-case")
    assert code == case_program.EXIT_VECTOR_REFUSED
    assert observed["result"] == "vector-refused"


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["chmod", f"{ROOT}/journal"],
        ["unlink"],
        ["unlink", f"{ROOT}/a", f"{ROOT}/b"],
        ["identity", f"{ROOT}/a"],
        ["open", "rdwr", f"{ROOT}/a"],
        ["pwrite", "rdonly", f"{ROOT}/a"],
        ["unlink", "/etc/passwd"],
        ["unlink", ROOT],
        ["unlink", "journal/000001.journal"],
        ["unlink", f"{ROOT}/../etc/passwd"],
        ["unlink", f"{ROOT}/a;b"],
        ["symlink", f"{ROOT}/journal/current", "/etc/passwd"],
        ["symlink", f"{ROOT}/journal/current", "a/b"],
        ["symlink", f"{ROOT}/journal/current", ".."],
        ["symlink", f"{ROOT}/journal/current", "000002.journal"],
    ],
)
def test_the_program_refuses_the_same_vectors_the_planner_does(arguments) -> None:
    code, observed = run_case(arguments)
    assert code == case_program.EXIT_VECTOR_REFUSED
    assert observed["result"] == "vector-refused"


def test_a_vector_refusal_is_a_different_exit_status_from_a_denial() -> None:
    """The distinction the whole `satisfying_statuses` scheme rests on.

    A step satisfied by *"the kernel refused this with EROFS"* must not also be
    satisfied by *"the program refused the vector"*, or the evidence would be
    consistent with the harness having been misconfigured.
    """
    assert case_program.EXIT_VECTOR_REFUSED not in set(
        case_program.REFUSAL_EXIT_CODES.values()
    )
    assert case_program.EXIT_RETURNED not in set(
        case_program.REFUSAL_EXIT_CODES.values()
    )


# ---------------------------------------------------------------------------
# The operations, run for real inside a directory this suite creates
# ---------------------------------------------------------------------------


@pytest.fixture
def arena(tmp_path, monkeypatch: pytest.MonkeyPatch):
    """A disposable root for this test only.

    The program's root is a module constant — `test_no_execution.py` asserts the
    shipped value is the approved target's — so exercising the operations means
    pointing that constant at a directory pytest made and will remove. Nothing
    outside it is reachable: `validate_path` still refuses everything that is not
    strictly inside whatever the constant says.
    """
    root = tmp_path / "fb-evidence-arena"
    root.mkdir()
    (root / "journal").mkdir()
    monkeypatch.setattr(case_program, "DISPOSABLE_ROOT", str(root))
    monkeypatch.setattr(case_program, "CASE_PROGRAM_PATH", str(root / "bin" / "case"))
    return root


def test_open_returns_for_each_reviewed_mode(arena) -> None:
    target = arena / "journal" / "probe"
    target.write_bytes(b"seed\n")
    for mode in ("rdonly", "wronly", "wronly-trunc", "wronly-append"):
        code, observed = run_case(["open", mode, str(target)])
        assert code == 0, mode
        assert observed["result"] == "returned"
        assert observed["errno"] == "none"


def test_create_excl_returns_once_and_is_then_refused_with_eexist(arena) -> None:
    target = arena / "journal" / "created"
    code, _ = run_case(["open", "create-excl", str(target)])
    assert code == 0
    assert target.exists()
    code, observed = run_case(["open", "create-excl", str(target)])
    assert code == REFUSAL_EXIT_CODES["EEXIST"]
    assert observed["errno"] == "EEXIST"


def test_an_absent_target_is_refused_with_enoent(arena) -> None:
    code, observed = run_case(["unlink", str(arena / "journal" / "absent")])
    assert code == REFUSAL_EXIT_CODES["ENOENT"]
    assert observed["errno"] == "ENOENT"
    assert observed["result"] == "refused"


def test_append_reports_the_size_before_and_after(arena) -> None:
    target = arena / "journal" / "appendable"
    target.write_bytes(b"abc")
    code, observed = run_case(["append", str(target)])
    assert code == 0
    assert observed["pre_size"] == "3"
    assert int(observed["post_size"]) == 3 + len(case_program.REVIEWED_BYTES)
    assert target.read_bytes() == b"abc" + case_program.REVIEWED_BYTES


def test_pwrite_at_offset_zero_overwrites_without_o_append(arena) -> None:
    target = arena / "journal" / "written"
    target.write_bytes(b"x" * 32)
    code, observed = run_case(["pwrite", "wronly", str(target)])
    assert code == 0
    assert observed["post_size"] == "32"
    assert target.read_bytes().startswith(case_program.REVIEWED_BYTES)


def test_pwrite_on_an_append_descriptor_lands_at_the_end(arena) -> None:
    """P-7, asserted rather than assumed.

    POSIX requires `O_APPEND` to ignore `pwrite`'s offset, so the design's claim
    is that the bytes are at the old EOF — not that the call is refused.
    """
    target = arena / "journal" / "appended"
    target.write_bytes(b"abc")
    code, observed = run_case(["pwrite", "wronly-append", str(target)])
    assert code == 0
    assert observed["pre_size"] == "3"
    assert int(observed["post_size"]) == 3 + len(case_program.REVIEWED_BYTES)
    assert target.read_bytes() == b"abc" + case_program.REVIEWED_BYTES


def test_ftruncate_empties_the_file(arena) -> None:
    target = arena / "journal" / "truncated"
    target.write_bytes(b"x" * 64)
    code, observed = run_case(["ftruncate", "wronly", str(target)])
    assert code == 0
    assert observed["post_size"] == "0"
    assert target.read_bytes() == b""


def test_rename_and_unlink_move_and_remove(arena) -> None:
    source = arena / "journal" / "before"
    destination = arena / "journal" / "after"
    source.write_bytes(b"x")
    assert run_case(["rename", str(source), str(destination)])[0] == 0
    assert destination.exists() and not source.exists()
    assert run_case(["unlink", str(destination)])[0] == 0
    assert not destination.exists()


def test_symlink_creates_the_reviewed_relative_link(arena) -> None:
    link = arena / "journal" / "current"
    code, observed = run_case(["symlink", str(link), GENERATION_LINK_NAME])
    assert code == 0
    assert observed["link_target"] == GENERATION_LINK_NAME
    assert link.is_symlink()
    assert os.readlink(link) == GENERATION_LINK_NAME
    assert not os.path.isabs(os.readlink(link))


def test_statvfs_reports_whether_the_filesystem_is_read_only(arena) -> None:
    code, observed = run_case(["statvfs", str(arena / "journal")])
    assert code == 0
    assert observed["st_rdonly"] in ("0", "1")


def test_getflags_and_clearflags_report_the_append_attribute_or_say_they_cannot(
    arena,
) -> None:
    """The flag interface, where the filesystem under `tmp_path` provides one.

    A filesystem without one answers `ENOTTY` or `EOPNOTSUPP`, which §2.13.2a
    treats as a **failed** probe rather than a passing one — so either outcome is
    asserted here, and what is checked is that the reported errno and the exit
    status agree. Nothing sets a flag: `clearflags` only ever clears, and the
    file it is given carries none.
    """
    target = arena / "journal" / "flagged"
    target.write_bytes(b"x")
    code, observed = run_case(["getflags", str(target)])
    if code == 0:
        assert observed["fs_append_fl"] == "0"
        clear_code, clear_observed = run_case(["clearflags", str(target)])
        assert clear_code == 0
        assert clear_observed["fs_append_fl"] == "0"
    else:
        assert observed["errno"] in ("ENOTTY", "EOPNOTSUPP", "ENOTSUP", "EPERM")
        assert code == REFUSAL_EXIT_CODES.get(observed["errno"], case_program.EXIT_REFUSED)


def test_identity_reports_the_numbers_the_masks_and_the_securebits(arena) -> None:
    """The complete identity observation, run against this very process.

    **This reads securebits; it never sets them.** `PR_GET_SECUREBITS` is a
    read, `PR_SET_SECUREBITS` needs `CAP_SETPCAP`, and there is no setter in the
    program to call. The value asserted is therefore whatever this unprivileged
    test process already carries — normally `0` — and the assertion is about its
    *shape* and range, not about a particular securebits word. R12's expected
    `0x0`/`0x4` cases are proved against an injected native boundary below.
    """
    code, observed = run_case(["identity"])
    assert code == 0
    assert observed["uid"] == str(os.getuid())
    assert observed["gid"] == str(os.getgid())
    assert "cap_prm" in observed and "cap_bnd" in observed
    # R12, EH-R11-2: securebits is observed rather than assumed from the
    # `capsh --secbits=` option in the vector.
    assert "securebits" in observed
    assert re.fullmatch(r"[0-9a-f]{1,2}", observed["securebits"])
    assert 0 <= int(observed["securebits"], 16) <= case_program.SECUREBITS_MAX
    for value in observed.values():
        assert str(arena) not in value


def test_a_refusal_names_no_path_and_no_operating_system_message(arena) -> None:
    code, observed = run_case(["unlink", str(arena / "journal" / "absent")])
    assert code != 0
    assert set(observed) == {"verb", "result", "errno"}
    assert str(arena) not in "".join(observed.values())


def test_the_program_writes_only_its_own_reviewed_bytes(arena) -> None:
    """There is no verb that takes content, so there is nothing else to write."""
    for spec in CASE_VERBS.values():
        assert all(kind.value != "content" for kind in spec.arguments)
    assert case_program.REVIEWED_BYTES == b"fb-evidence-p5-0\n"


def test_the_installed_mode_the_plan_asserts_is_not_set_user_id() -> None:
    assert int(CASE_PROGRAM_MODE, 8) & (stat.S_ISUID | stat.S_ISGID) == 0


# ---------------------------------------------------------------------------
# R12 / EH-R11-2 — the one native call, across an injected boundary
# ---------------------------------------------------------------------------
#
# **No test below changes this process's securebits, and none could.** Reading
# them is `PR_GET_SECUREBITS`; setting them is `PR_SET_SECUREBITS`, which needs
# `CAP_SETPCAP`, which no test here holds — and the program contains no setter to
# call in any case. Every value the reviewed identities expect is proved against
# a fixed injected native boundary instead, which is also the only way to prove
# the failure branches at all.


def test_the_native_boundary_is_read_only_and_has_no_setter() -> None:
    """The program can read securebits and cannot write them.

    Asserted as a property of the **code** rather than of a run: with comments
    and string literals removed — the file explains at length what it may not do
    — the setter's name and `capset` appear nowhere, and the one operation
    constant is `PR_GET_SECUREBITS`, whose value is 27 in
    `include/uapi/linux/prctl.h`. `PR_SET_SECUREBITS` is 28 and is named
    nowhere.
    """
    source = SOURCE_ROOT.joinpath(
        "tools", "phase_5_0_evidence", "execution", "case_program.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    constants = {
        target.id: statement.value.value
        for statement in tree.body
        if isinstance(statement, ast.Assign)
        and isinstance(statement.value, ast.Constant)
        for target in statement.targets
        if isinstance(target, ast.Name) and target.id.startswith("PR_")
    }
    assert constants == {"PR_GET_SECUREBITS": 27}
    pieces = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type not in (tokenize.COMMENT, tokenize.STRING):
            pieces.append(token.string)
    code = " ".join(pieces)
    for forbidden in ("PR_SET_SECUREBITS", "capset", "prctl_set", "28"):
        assert forbidden not in code, forbidden


@pytest.mark.parametrize("value", [0x0, 0x4])
def test_the_reviewed_securebits_values_are_reported_as_bounded_hex(value: int) -> None:
    """`0x0` is `E7`'s — the harness's own root process — and `0x4` is
    `SECBIT_NO_SETUID_FIXUP`, which every `capsh`-constructed identity carries
    after §2.13.5c step 1 and after step 7's `execve`.

    The injected boundary returns exactly what the native call returns: the
    `prctl` return value and the errno beside it.
    """
    assert case_program._securebits_text(read=lambda: (value, 0)) == format(value, "x")


def test_every_constructed_identitys_expected_securebits_can_be_reported() -> None:
    """The program's own emission and the reviewed expectation agree in form.

    A value the program could not print would be an expectation nothing can
    satisfy; a value the capture boundary would call `unreadable` would be the
    same defect one step later. Both are checked here for every identity.
    """
    for name, identity in EVIDENCE_IDENTITIES.items():
        if name == "E7":
            # `E7` constructs nothing, so it has no derived securebits at all;
            # its expected value is a reviewed target fact and the whole `0 …
            # SECUREBITS_MAX` range is exercised for it in `test_root_identity.py`.
            continue
        expected = identity.expected_masks()["securebits"]
        emitted = case_program._securebits_text(read=lambda value=expected: (value, 0))
        assert emitted == format(expected, "x")
        observed = dict(
            sanitize(
                CapturePolicy.CASE_IDENTITY,
                f"verb=identity\nresult=returned\nsecurebits={emitted}\n",
            )
        )
        assert observed["securebits"] == emitted, name
        assert int(observed["securebits"], 16) == expected, name


def test_a_failed_prctl_reports_its_errno_through_the_fixed_failure_path() -> None:
    """`-1` is the failure convention, and the errno is read with
    `ctypes.get_errno()` and reported as a **name**. No operating-system message
    reaches the output."""

    with pytest.raises(case_program.ObservationUnavailable) as raised:
        case_program._securebits_text(read=lambda: (-1, errno_module.EPERM))
    assert raised.value.errno_name == "EPERM"
    with pytest.raises(case_program.ObservationUnavailable) as unknown:
        case_program._securebits_text(read=lambda: (-1, 999_999))
    assert unknown.value.errno_name == "UNKNOWN"


@pytest.mark.parametrize(
    "answer",
    [
        (-1, 0),
        (-4, 0),
        (case_program.SECUREBITS_MAX + 1, 0),
        (1 << 40, 0),
        (True, 0),
        ("4", 0),
        (None, 0),
        (4.0, 0),
        # Malformed shapes from the boundary itself.
        4,
        None,
        (4,),
        (4, 0, 0),
    ],
)
def test_a_malformed_or_out_of_range_securebits_is_refused(answer) -> None:
    """A negative value, a value beyond the eight defined bits, a boolean,
    anything that is not an integer, and a boundary answer that is not the pair
    the native call returns, are each refused before anything can be emitted.
    `securebits.h` defines bits 0 … 7, so a wider value is not a securebits
    word."""
    with pytest.raises(case_program.ObservationUnavailable):
        case_program._securebits_text(read=lambda: answer)


def test_an_unobservable_securebits_makes_the_identity_verb_exit_66(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The distinct exit status is the point: it is in no step's
    `satisfying_statuses`, so *"the identity could not be observed"* can never be
    recorded as *"the operation was refused"* or as a pass."""

    monkeypatch.setattr(
        case_program,
        "_prctl_get_securebits",
        lambda: (-1, errno_module.EINVAL),
    )
    code, observed = run_case(["identity"])
    assert code == case_program.EXIT_OBSERVATION_UNAVAILABLE
    assert code == EXIT_OBSERVATION_UNAVAILABLE
    assert observed == {"verb": "identity", "result": "unobserved", "errno": "EINVAL"}


def test_an_out_of_range_securebits_exits_66_and_names_no_errno(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(case_program, "_prctl_get_securebits", lambda: (1 << 31, 0))
    code, observed = run_case(["identity"])
    assert code == case_program.EXIT_OBSERVATION_UNAVAILABLE
    assert observed == {"verb": "identity", "result": "unobserved", "errno": "none"}


def test_an_unobserved_identity_carries_no_reviewed_identity_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The sanitized observation of a failed identity verb carries `verb`,
    `result` and no reviewed identity value, so the contract refuses it rather
    than accepting a partial identity.

    **Updated by PR-20260907-3.** The failure output also carries `errno`, which
    is a key `CASE_RESULT` declares and `CASE_IDENTITY` does not. The capture
    boundary used to drop it silently; it now marks the observation as carrying
    an unexpected name. Either way the step is unsatisfied — this exits 66,
    which is in no step's satisfying statuses — but the refusal is now visible
    in the observation rather than only in the exit status, and no reviewed
    identity key is fabricated.
    """
    monkeypatch.setattr(
        case_program, "_prctl_get_securebits", lambda: (-1, errno_module.EPERM)
    )
    code, observed = run_case(["identity"])
    assert code == case_program.EXIT_OBSERVATION_UNAVAILABLE
    sanitized = dict(
        sanitize(
            CapturePolicy.CASE_IDENTITY,
            "".join(f"{key}={value}\n" for key, value in observed.items()),
        )
    )
    assert set(sanitized) == {"verb", "result", UNEXPECTED_KEY_MARKER[0]}
    assert sanitized[UNEXPECTED_KEY_MARKER[0]] == UNEXPECTED_KEY_MARKER[1]
    # The errno the program reported is not in the artifact under any name.
    assert "EPERM" not in sanitized.values()


def test_the_two_tiers_agree_about_the_securebits_bound_and_the_exit_status() -> None:
    assert case_program.SECUREBITS_MAX == SECUREBITS_MAX
    assert case_program.EXIT_OBSERVATION_UNAVAILABLE == EXIT_OBSERVATION_UNAVAILABLE
    assert case_program.EXIT_OBSERVATION_UNAVAILABLE not in set(
        REFUSAL_EXIT_CODES.values()
    ) | {
        case_program.EXIT_RETURNED,
        case_program.EXIT_REFUSED,
        case_program.EXIT_VECTOR_REFUSED,
        case_program.EXIT_INTERNAL,
    }


def test_the_identity_verbs_emitted_keys_are_exactly_the_policys_key_set() -> None:
    """What the program prints and what the capture policy admits are two halves
    of one thing, and R12 added a key to both."""
    from tools.phase_5_0_evidence.capture import _KEY_VALUE_KEYS

    emitted = set(case_program._do_identity()) | {"verb", "result"}
    assert emitted == set(_KEY_VALUE_KEYS[CapturePolicy.CASE_IDENTITY])
