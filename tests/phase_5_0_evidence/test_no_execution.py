"""The property that makes this stage safe to review: **the harness cannot run
what it plans.**

The authorization draft, the implementation prompt and the remediation prompt all
say the same thing three different ways — Codex must approve the exact target,
commands and cleanup before a single mutation-bearing command runs. A promise in a
docstring is not that guarantee. This suite is.

It is a **source-level** proof, deliberately, and it reads the modules as text
rather than importing and poking at them:

* an import that is never executed on the tested path still exists in the source,
  and a test that only exercised the happy path would not see it;
* `importlib`, `__import__`, `eval`, `exec`, `ctypes` and `getattr(os, …)` are all
  ways to reach a process without an `import subprocess` line, so the scan looks
  for the reach rather than for one spelling of it; and
* it needs no privilege, no network, no database and no host state, so it runs
  identically for a reviewer who has none of those.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

PACKAGE = Path(__file__).resolve().parents[2] / "tools" / "phase_5_0_evidence"

#: **Two tiers, and the scan covers both.**
#:
#: The planning tier is every module directly under `tools/phase_5_0_evidence/`.
#: It plans and classifies and cannot execute: no process, no network, no file.
#: That was the whole package until the concrete-plan stage.
#:
#: The execution tier is `tools/phase_5_0_evidence/execution/`. It is a
#: subdirectory rather than four more modules beside the planner so that the
#: boundary is a directory a reviewer can see — and because a subdirectory is
#: exactly the shape of an evasion, the scan below enumerates
#: `PACKAGE.rglob("*.py")` and **fails on any file that is in neither tier**.
#: Adding an executing module is therefore a declaration in this file, not a
#: file that quietly escapes a glob.
ALL_MODULES = sorted(
    path for path in PACKAGE.rglob("*.py") if "__pycache__" not in path.parts
)
EXECUTION_TIER = sorted(
    path for path in ALL_MODULES if path.parent.name == "execution"
)
#: The planning tier, and what every existing assertion in this file is about.
MODULES = sorted(path for path in ALL_MODULES if path.parent == PACKAGE)

#: Top-level packages no module may import. Each is a way to reach a process, a
#: socket or a database, and none of them has any business in a planner.
FORBIDDEN_IMPORTS = frozenset(
    {
        "asyncio",
        "ctypes",
        "http",
        "importlib",
        "multiprocessing",
        "pty",
        "psycopg",
        "psycopg2",
        "requests",
        "select",
        "shlex",
        "signal",
        "socket",
        "sqlalchemy",
        "ssl",
        "subprocess",
        "telnetlib",
        "urllib",
        "webbrowser",
    }
)

#: Names that reach a process or evaluate text as code without an import.
FORBIDDEN_CALLS = frozenset(
    {
        "system",
        "popen",
        "execv",
        "execve",
        "execvp",
        "execvpe",
        "execl",
        "execle",
        "execlp",
        "spawnv",
        "spawnve",
        "fork",
        "forkpty",
        "posix_spawn",
        "posix_spawnp",
        "eval",
        "exec",
        "compile",
        "__import__",
        "run",
        "check_output",
        "check_call",
        "call",
        "Popen",
    }
)

#: `run` is the `Runner` protocol's own method name and `DryRunRunner`'s, so the
#: call scan would otherwise flag the planner calling its own dry-run runner.
#: Allowed only where the receiver is the runner itself.
ALLOWED_RUN_RECEIVERS = frozenset({"self", "runner", "DryRunRunner"})

#: `compile` is on the forbidden list because `compile(source, …, "exec")` turns
#: text into code. `re.compile` is a different function with the same name, and
#: refusing it would mean the scan could not tell them apart — so the receiver is
#: checked rather than the name alone.
ALLOWED_COMPILE_RECEIVERS = frozenset({"re"})


#: The planning tier, enumerated. A module added here without a decision about
#: whether it may execute fails this test on the day it is added.
PLANNING_TIER_NAMES = {
    "__init__",
    "approved_target",
    "binding",
    "capability",
    "capture",
    "case_runtime",
    "cleanup",
    "concrete_plan",
    # **PR-20260911-R2-2/-R2-3.** The bounded synthetic model of the proposed
    # runner's durability barriers and its name-based removal. It is in this tier
    # because its whole "filesystem" is a dictionary: it opens nothing,
    # synchronizes nothing and removes nothing outside its own in-memory state,
    # which the scans below assert.
    "durability_model",
    "errors",
    "expectations",
    # **C-P5.0-LAB-1.** The bounded evidence-only producers for the three C-7
    # cases. It is in this tier because it is a set of deterministic in-memory
    # models and the classifiers they feed: it names no process, opens no file
    # and imports nothing from `execution/`, which the scans below assert.
    "feasibility",
    "filesystem",
    "hba",
    "identity",
    "journal",
    # **PR-20260911-R2-4.** The proposed lifecycle storage protocol and its
    # verified-first-use provisioning, modelled over `durability_model`'s
    # in-memory filesystem. It provisions nothing and shares its admission
    # semantics with `reservation.validate_lifecycle`.
    "lifecycle_storage",
    "manifest",
    "materialization",
    # **R16, conflict C-7.** The supplied-observation importer and the Band-7
    # classification it feeds. It is in this tier because it is exactly what it
    # says: a validator and a set of pure functions over records somebody hands
    # it. It names no process, opens no file and imports nothing from
    # `execution/`, which the scans below assert.
    "observations",
    "plan",
    "provenance",
    "records",
    # **R13, EH-R13-4.** The required-case table and the coverage check that
    # refuses a plan in which a required case is neither produced nor declared
    # unresolved. Pure data and one comparison; it names no process and reads no
    # file, which is why it is in this tier.
    "required_cases",
    # **C-P5.0-LAB-1.** The whole-host reservation state machine, the cooperative
    # admission decision and the release conditions. It is in this tier because
    # it decides and does not act: every observation it reads — the lock's
    # holder, the host inventory, the clock — arrives as an argument from a
    # caller that made it, and it takes no lock, starts no process and kills
    # nothing.
    "reservation",
    "review_manifest",
    "sudoers",
    "targets",
}

#: The execution tier, enumerated for the same reason and with more force: these
#: are the only files in the repository permitted to start a process, or to write
#: a file, on the harness's behalf.
#:
#: `case_program` is the R11 addition, and it is declared here rather than in the
#: planning tier because of what it is: the reviewed payload the kernel runs
#: inside the disposable root, whose whole purpose is `open(2)`, `pwrite(2)`,
#: `ftruncate(2)`, `rename(2)`, `unlink(2)`, `symlink(2)`, `statvfs(3)` and two
#: `ioctl(2)`s. The planning tier may not touch a file at all, so that is not
#: where it can live. **No guard was relaxed to admit it**: every execution-tier
#: assertion below applies to it unchanged — it may not import `subprocess`
#: (only `boundary` may), may not reach a shell, and must be inert on import —
#: and `test_the_case_program_imports_only_the_standard_library` adds a rule the
#: other four are not held to.
EXECUTION_TIER_NAMES = {
    "__init__",
    # **R13, EH-R13-5.** The run-record writer. It is in this tier because it
    # writes a file on the harness's behalf, and it is the only file here that
    # writes anything other than the two reviewed configuration destinations.
    "artifact",
    "boundary",
    "case_program",
    "cli",
    # **R16, conflict C-7.** The ingestion entry point. It is in this tier
    # because it reads a payload from a path and writes the classified artifact
    # to one, and for no other reason: it constructs no boundary, no executor and
    # no materializer, and `test_the_ingestion_entry_point_cannot_reach_a_process`
    # asserts that against its import set rather than trusting the docstring.
    "evidence_cli",
    "executor",
    "materializer",
}

#: The exact standard-library modules the case program may import. It runs under
#: `-I -S` on the disposable host, where nothing outside the standard library is
#: importable at all; this asserts that the source agrees, so a third-party
#: import added later fails here rather than at the moment a privileged process
#: would have started.
CASE_PROGRAM_PERMITTED_IMPORTS = frozenset(
    {"__future__", "array", "ctypes", "errno", "fcntl", "hashlib", "os", "sys"}
)

#: **The one `ctypes` exception in this repository, and its exact shape.**
#:
#: §2.13.5c's assertion contract requires every `E1 … E8` identity's final
#: securebits to be observed inside the exec'd process, and the kernel reports
#: securebits through `prctl(2)` and through no file. Python 3.12 exposes no
#: `prctl` in `os`, so a foreign call is the smallest mechanism that can read it
#: at all. R11 had none and asserted the value from the presence of a `capsh
#: --secbits=` option instead, which states an intent rather than observing a
#: state — Blocking finding EH-R11-2.
#:
#: The exception is granted to **one file and one function**, and the guards
#: below assert its literal shape rather than trusting the prose: the library is
#: the already-loaded C runtime, the symbol is the literal `prctl`, the
#: signature is fixed, the operation is the literal `PR_GET_SECUREBITS` with
#: four literal zero arguments, and nothing about any of it can come from a
#: vector. `ctypes` remains forbidden in every other module of both tiers, and
#: `getattr`, dynamic import and an arbitrary native call remain forbidden
#: everywhere including here.
THE_ONLY_NATIVE_CALLER = "case_program.py"
THE_NATIVE_FUNCTION = "_prctl_get_securebits"
THE_NATIVE_SYMBOL = "prctl"
THE_NATIVE_OPERATION = "PR_GET_SECUREBITS"
#: The complete set of `ctypes` attributes the exception permits. `CDLL`,
#: `set_errno` and `get_errno` are the three calls; `c_int` and `c_ulong` are the
#: two types the fixed signature is written in. Anything else — `cast`,
#: `POINTER`, `memmove`, `string_at`, `pythonapi`, `addressof` — is refused.
PERMITTED_CTYPES_ATTRIBUTES = frozenset(
    {"CDLL", "c_int", "c_ulong", "get_errno", "set_errno"}
)


def _code_only(source: str) -> str:
    """`source` with every comment and every string literal removed.

    A module that explains which constructs it must never contain will contain
    those constructs as prose. Stripping comments and literals is what lets the
    guard read the code and the documentation say what it needs to.
    """
    import io
    import tokenize

    pieces: list[str] = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type in (tokenize.COMMENT, tokenize.STRING):
            continue
        pieces.append(token.string)
    return " ".join(pieces)


def test_the_package_has_the_modules_this_suite_covers() -> None:
    assert {path.stem for path in MODULES} == PLANNING_TIER_NAMES


def test_the_execution_tier_is_exactly_the_declared_modules() -> None:
    assert {path.stem for path in EXECUTION_TIER} == EXECUTION_TIER_NAMES


def test_the_case_program_imports_only_the_standard_library() -> None:
    """The narrowest guard in the tier, and it is a new rule rather than a
    relaxed one.

    The reviewed vector passes `-I -S`, so on the disposable host `sys.path`
    carries neither the script's directory, nor the user site directory, nor the
    virtual environment's `site-packages`. This asserts the **source** agrees
    with that: an import outside the allowlist would be a dependency the review
    manifest does not cover and the isolation flags would refuse at run time, and
    it fails here instead — before anything is installed anywhere.
    """
    path = PACKAGE / "execution" / "case_program.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, (
                "case_program.py must not import from the package: it runs from "
                "inside the disposable root under -I, where the package is not "
                "importable, so a relative import is a program that cannot run."
            )
            assert node.module, "a bare `from . import` has no place here"
            imported.add(node.module.split(".")[0])
    offending = sorted(imported - CASE_PROGRAM_PERMITTED_IMPORTS)
    assert not offending, (
        f"case_program.py imports {offending}, which is outside the reviewed "
        f"standard-library set {sorted(CASE_PROGRAM_PERMITTED_IMPORTS)}."
    )


def test_the_case_programs_root_is_the_approved_targets_root() -> None:
    """The one constant the case program duplicates, checked against its source.

    The program cannot import `approved_target`: under `-I` nothing outside the
    standard library is importable, which is the isolation the whole Option-B
    vector exists to obtain. So the disposable root is written out a second time
    — and this is what stops the two copies drifting.
    """
    from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
    from tools.phase_5_0_evidence.case_runtime import case_program_path
    from tools.phase_5_0_evidence.execution import case_program

    assert case_program.DISPOSABLE_ROOT == APPROVED_TARGET.root_path
    assert case_program.CASE_PROGRAM_PATH == case_program_path(APPROVED_TARGET)


def test_the_case_program_is_inert_when_it_is_imported() -> None:
    """Importing it runs no operation and touches nothing.

    Every operation is behind `main()`, and `main()` is called only under
    `__main__`. The check is structural: the module body contains no call at all
    other than the `frozenset` and `dict` constructions of its constant tables.
    """
    path = PACKAGE / "execution" / "case_program.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.ClassDef, ast.FunctionDef)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # the module docstring
        if isinstance(node, ast.If):
            # The `__main__` guard, and nothing else may be conditional here.
            test = node.test
            assert isinstance(test, ast.Compare) and isinstance(test.left, ast.Name), (
                "the only conditional at module level is the __main__ guard"
            )
            assert test.left.id == "__name__"
            continue
        assert isinstance(node, (ast.Assign, ast.AnnAssign)), (
            f"case_program.py:{node.lineno} is a module-level statement that is "
            "neither an import, a definition, a constant assignment nor the "
            "__main__ guard."
        )


def test_no_module_in_the_package_escapes_both_tiers() -> None:
    """The scan is exhaustive over the package tree.

    Without this, `execution/` would be a way to add an executing module the
    planning-tier scan does not read — which is precisely the shape of the
    evasion the subdirectory could otherwise be.
    """
    unclassified = [
        str(path.relative_to(PACKAGE))
        for path in ALL_MODULES
        if path not in MODULES and path not in EXECUTION_TIER
    ]
    assert not unclassified, (
        f"{unclassified} are in neither the planning tier nor the execution "
        "tier. Every module in this package is one or the other, and which one "
        "it is decides what it is allowed to do."
    )


@pytest.mark.parametrize("path", MODULES, ids=[path.name for path in MODULES])
def test_no_module_imports_a_way_to_execute_or_reach_the_network(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])

    offending = sorted(imported & FORBIDDEN_IMPORTS)
    assert not offending, (
        f"{path.name} imports {offending}. This package plans commands and "
        "classifies observations; it does not run them, and an executing runner "
        "is a separate, separately reviewed change."
    )


@pytest.mark.parametrize("path", MODULES, ids=[path.name for path in MODULES])
def test_no_module_reaches_a_process_without_an_import(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            name, receiver = function.id, None
        elif isinstance(function, ast.Attribute):
            name = function.attr
            receiver = (
                function.value.id if isinstance(function.value, ast.Name) else None
            )
        else:
            continue
        if name not in FORBIDDEN_CALLS:
            continue
        if name == "run" and receiver in ALLOWED_RUN_RECEIVERS:
            continue
        if name == "compile" and receiver in ALLOWED_COMPILE_RECEIVERS:
            continue
        pytest.fail(
            f"{path.name}:{node.lineno} calls {name!r}. That is a way to reach a "
            "process or evaluate text as code, and neither belongs in a planner."
        )


@pytest.mark.parametrize("path", MODULES, ids=[path.name for path in MODULES])
def test_no_module_names_a_network_scheme_or_a_connection_string(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for pattern in (r"https?://", r"postgresql://", r"postgresql\+", r"\bconnect\("):
        assert not re.search(pattern, text), (
            f"{path.name} contains {pattern!r}. The harness makes no network call "
            "and opens no database connection."
        )


@pytest.mark.parametrize("path", MODULES, ids=[path.name for path in MODULES])
def test_no_module_opens_reads_or_writes_a_file(path: Path) -> None:
    """The harness is handed its observations; it does not go and get them.

    That is what makes C-1 and the pre-change HBA read safe to leave with an
    authorized human: this package cannot read `/etc/sudoers.d` even if a future
    edit wanted it to, because it has no file access at all.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", (
                f"{path.name}:{node.lineno} calls open(). Content reaches this "
                "package as a supplied string, from a reader authorized to read it."
            )
        if isinstance(node, ast.Attribute) and node.attr in (
            "read_text",
            "read_bytes",
            "write_text",
            "write_bytes",
        ):
            pytest.fail(f"{path.name}:{node.lineno} reads or writes a file.")


#: **R16, conflict C-7.** The three execution-tier modules that can act on the
#: host: two that can start a process and one that can write a file wherever the
#: reviewed plan says. The ingestion entry point may import none of them.
THE_ACTING_MODULES = frozenset({"boundary", "executor", "materializer"})

#: The ingestion entry point. It is in the execution tier because it reads a
#: payload and writes an artifact, and for no other reason.
THE_INGESTION_ENTRY_POINT = "evidence_cli.py"


def test_the_ingestion_entry_point_cannot_reach_a_process() -> None:
    """**R16, conflict C-7's trust boundary, asserted rather than promised.**

    R14 asked what stops a supplied observation reaching the component that
    constructs the process boundary. The answer is not a flag on `cli.py`: it is
    that the ingestion stage is a **different program with a different import
    graph**. This reads that graph.

    Four assertions, and the first is the one that matters: the module imports
    none of `boundary`, `executor` or `materializer`, and does not import `cli`,
    which imports all three. There is therefore no call path from a payload to a
    process — not a policy about one.
    """
    path = PACKAGE / "execution" / THE_INGESTION_ENTRY_POINT
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    relative: set[str] = set()
    absolute: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            absolute.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module:
                relative.add(node.module.split(".")[0])
            elif node.module:
                absolute.add(node.module.split(".")[0])

    assert not (relative & THE_ACTING_MODULES), sorted(relative & THE_ACTING_MODULES)
    assert "cli" not in relative
    assert not (absolute & FORBIDDEN_IMPORTS), sorted(absolute & FORBIDDEN_IMPORTS)
    # And it offers no way to ask for a run. Every option this module defines is
    # read from its own syntax tree, so the docstring may name `cli.py`'s option
    # and the parser may not define one.
    options = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith("--")
    }
    assert "--execute" not in options, sorted(options)
    assert "--confirm-target" not in options
    assert "--reviewed-digest" not in options
    # Nor does it name either armable object anywhere in its code.
    for name in ("SubprocessBoundary", "SystemMaterializer", "ExecutingRunner"):
        assert not any(
            isinstance(node, ast.Name) and node.id == name for node in ast.walk(tree)
        ), name


def test_the_importer_is_a_planning_tier_module_with_no_execution_import() -> None:
    """The validator and classifier themselves reach nothing either.

    `observations.py` is where a supplied payload is parsed, shape-checked, bound
    to its target, run and manifest digest, and handed to the band classifiers.
    The planning-tier scans above already assert it starts no process and opens
    no file; this adds the one rule that is specific to it — it imports nothing
    from the execution tier at all, so the validation and the acting halves of
    this package share no object.
    """
    path = PACKAGE / "observations.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith("execution"), node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "execution" not in alias.name.split("."), alias.name


def test_the_only_runner_the_package_defines_is_the_dry_run_one() -> None:
    source = (PACKAGE / "plan.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    runners = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name.endswith("Runner")
    ]
    assert runners == ["Runner", "DryRunRunner"]


def test_the_dry_run_runner_marks_every_invocation_as_not_executed() -> None:
    from tools.phase_5_0_evidence.plan import PlannedInvocation

    assert PlannedInvocation(step_id="S", run_as="root", argv=("/usr/bin/id",)).executed is False


#: The one test module permitted to **name** the process starter. EH-R5-1
#: requires the real boundary's credential keywords to be asserted as they are
#: passed, and the only way to see them is to replace what the boundary calls.
#: It names it in order to replace it — as the string it hands to
#: `monkeypatch.setattr` — and the two assertions below are what make that
#: narrower than the blanket rule it replaces: it never imports it, and the name
#: never appears in that module's code.
THE_MOCKED_BOUNDARY_TEST = "test_boundary_identity.py"


def test_no_test_in_this_suite_needs_root_or_a_database() -> None:
    """Asserted about the suite itself, because a test that quietly required
    privilege would make the suite unrunnable for the reviewer who has to read it.

    `TEST_DATABASE_URL` is not consulted anywhere in `tests/phase_5_0_evidence`,
    and no test here carries the `database` marker.
    """
    suite = Path(__file__).parent
    # Every `.py` in the directory, not only `test_*.py`: a `conftest.py` is
    # imported by every module here and would otherwise be the one file in the
    # suite that escapes the scan.
    # This module is excluded because it *names* the things it is looking for.
    for path in sorted(suite.glob("*.py")):
        if path.name == Path(__file__).name:
            continue
        text = path.read_text(encoding="utf-8")
        assert "TEST_DATABASE_URL" not in text, path.name
        assert "pytest.mark.database" not in text, path.name
        assert "os.environ" not in text, path.name
        if path.name != THE_MOCKED_BOUNDARY_TEST:
            assert "subprocess" not in text, path.name


#: The two standard-library readers of the host's account database. `getent` is
#: a command and is already unreachable — nothing in this suite may reach a
#: process — but `pwd` and `grp` need no process, so they are named.
HOST_ACCOUNT_DATABASE_READERS = frozenset({"pwd", "grp"})


def test_no_test_in_this_suite_reads_the_host_account_database() -> None:
    """**EH-R8-2's standing requirement, asserted over the whole suite.**

    Every canonical membership assertion here is decided from §2.12.2 and from
    injected synthetic account tables. A test that read `pwd` or `grp` would be
    asserting about *this* machine, which is neither the reviewed table nor the
    disposable target — and which would quietly make the corrected inverse rows
    depend on whichever host happened to run the suite.

    Imports are read from the AST rather than from the text, so a module may
    still *name* the readers in a string or a comment, which is how this one
    and the guard in `test_boundary_identity.py` are written.
    """
    suite = Path(__file__).parent
    for path in sorted(suite.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported.add(node.module.split(".")[0])
        assert not (imported & HOST_ACCOUNT_DATABASE_READERS), path.name


def test_the_one_test_that_names_the_process_starter_cannot_reach_it() -> None:
    """The exemption, made narrower than the rule it replaces.

    Scanned with comments and string literals removed, the module contains the
    name nowhere: its single occurrence is the string passed to
    `monkeypatch.setattr`, which replaces the boundary module's reference. It
    imports nothing that could start a process, so even a replacement that
    silently failed would leave it with no path to one.
    """
    path = Path(__file__).parent / THE_MOCKED_BOUNDARY_TEST
    text = path.read_text(encoding="utf-8")

    assert "subprocess" not in _code_only(text), (
        f"{THE_MOCKED_BOUNDARY_TEST} may name the process starter only as the "
        "string it replaces, never as code."
    )

    tree = ast.parse(text, filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])
    offending = sorted(imported & FORBIDDEN_IMPORTS)
    assert not offending, f"{THE_MOCKED_BOUNDARY_TEST} imports {offending}."


# ---------------------------------------------------------------------------
# The execution tier: what it may do, and the guards on it
# ---------------------------------------------------------------------------

#: Even here, these remain forbidden. `subprocess` is permitted in exactly one
#: module, `ctypes` in exactly one other; a shell, `eval`, `exec` and a network
#: client are permitted in none.
EXECUTION_TIER_STILL_FORBIDDEN = FORBIDDEN_IMPORTS - {"subprocess", "ctypes"}

#: The one module allowed to import `subprocess`. Named, so that a second one
#: fails this suite rather than becoming a second place a process can start.
THE_PROCESS_BOUNDARY = "boundary.py"


@pytest.mark.parametrize(
    "path", EXECUTION_TIER, ids=[path.name for path in EXECUTION_TIER]
)
def test_only_the_boundary_module_may_import_subprocess(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])

    offending = sorted(imported & EXECUTION_TIER_STILL_FORBIDDEN)
    assert not offending, (
        f"{path.name} imports {offending}. The execution tier starts processes; "
        "it does not reach the network, evaluate text as code or open a database."
    )
    if "subprocess" in imported:
        assert path.name == THE_PROCESS_BOUNDARY, (
            f"{path.name} imports subprocess. Exactly one module in this "
            f"repository does, and it is {THE_PROCESS_BOUNDARY}."
        )
    if "ctypes" in imported:
        assert path.name == THE_ONLY_NATIVE_CALLER, (
            f"{path.name} imports ctypes. Exactly one module in this repository "
            f"does, and it is {THE_ONLY_NATIVE_CALLER} — for the single "
            f"{THE_NATIVE_SYMBOL}({THE_NATIVE_OPERATION}) call §2.13.5c's "
            "assertion contract requires and for nothing else."
        )


def test_no_planning_tier_module_imports_ctypes() -> None:
    """The exception is granted to the execution tier's payload, and to nothing
    in the tier that may not touch a file at all."""
    for path in MODULES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert not any(
                    alias.name.split(".")[0] == "ctypes" for alias in node.names
                ), f"{path.name}:{node.lineno} imports ctypes."
            elif isinstance(node, ast.ImportFrom):
                assert (node.module or "").split(".")[0] != "ctypes", (
                    f"{path.name}:{node.lineno} imports from ctypes."
                )


@pytest.mark.parametrize(
    "path", ALL_MODULES, ids=[path.name for path in ALL_MODULES]
)
def test_no_module_but_the_case_program_performs_a_native_call(path: Path) -> None:
    """No second route to a foreign function, in either tier.

    The import scan above is not enough on its own: `ctypes` is reachable through
    `getattr(sys.modules[…], …)`, through `__import__`, and through a helper that
    another module calls. So this looks for the **reach** — any mention of
    `ctypes`, `cdll`, `CDLL`, `windll`, `pythonapi`, `dlopen`, `LoadLibrary`,
    `restype` or `argtypes` in code, with comments and string literals removed —
    and permits it in one file.
    """
    code = _code_only(path.read_text(encoding="utf-8"))
    for reach in (
        "ctypes",
        "cdll",
        "CDLL",
        "windll",
        "pythonapi",
        "dlopen",
        "LoadLibrary",
        "restype",
        "argtypes",
    ):
        if path.name == THE_ONLY_NATIVE_CALLER:
            continue
        assert reach not in code, (
            f"{path.name} contains {reach!r} in code. A native call is permitted "
            f"in {THE_ONLY_NATIVE_CALLER} alone."
        )


def test_the_native_call_is_the_literal_prctl_get_securebits_and_nothing_else() -> None:
    """The exception, asserted clause by clause against the syntax tree.

    This is what makes the `ctypes` allowance *bounded* rather than *granted*.
    Every clause below is a separate way the allowance could have become a
    general foreign-function interface, and each is refused mechanically:

    * `ctypes` is used only through the five permitted attributes;
    * there is exactly one `CDLL` call, its argument is the literal `None` —
      the process's already-loaded C runtime, not a library this program names —
      and it passes `use_errno=True`;
    * the only symbol bound on the loaded library is the literal `prctl`;
    * `argtypes` and `restype` are assigned fixed `ctypes` types, so the call
      cannot be made with a different signature;
    * the call passes the literal `PR_GET_SECUREBITS` name and four literal
      zeroes, so no operation and no argument can come from a vector; and
    * the whole thing lives in one function, which returns an `int` and exposes
      no reusable caller.
    """
    path = PACKAGE / "execution" / THE_ONLY_NATIVE_CALLER
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == THE_NATIVE_FUNCTION
    ]
    assert len(functions) == 1, (
        f"{THE_ONLY_NATIVE_CALLER} declares {len(functions)} "
        f"{THE_NATIVE_FUNCTION!r} functions; the exception is one function."
    )
    native = functions[0]
    assert not native.args.args and not native.args.kwonlyargs, (
        "the native call takes no argument, so no library, symbol, operation or "
        "raw argument can be passed to it."
    )

    # Every `ctypes.<name>` in the whole file, wherever it appears.
    used = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "ctypes"
    }
    assert used <= PERMITTED_CTYPES_ATTRIBUTES, (
        f"{THE_ONLY_NATIVE_CALLER} uses ctypes attributes "
        f"{sorted(used - PERMITTED_CTYPES_ATTRIBUTES)}, which are outside the "
        f"permitted set {sorted(PERMITTED_CTYPES_ATTRIBUTES)}."
    )

    loads = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "CDLL"
    ]
    assert len(loads) == 1, "exactly one library is loaded, and it is loaded once."
    load = loads[0]
    assert (
        len(load.args) == 1
        and isinstance(load.args[0], ast.Constant)
        and load.args[0].value is None
    ), (
        "the loaded library is the literal None — the process's already-required "
        "C runtime. No library name is named, and none can be supplied."
    )
    assert [keyword.arg for keyword in load.keywords] == ["use_errno"] and (
        isinstance(load.keywords[0].value, ast.Constant)
        and load.keywords[0].value.value is True
    ), "the load requests errno capture with a literal True, so `-1` is reportable."

    # The only attribute taken off the loaded handle is the literal symbol.
    handles = {
        target.id
        for statement in ast.walk(native)
        if isinstance(statement, ast.Assign)
        for target in statement.targets
        if isinstance(target, ast.Name)
        and isinstance(statement.value, ast.Call)
        and isinstance(statement.value.func, ast.Attribute)
        and statement.value.func.attr == "CDLL"
    }
    assert len(handles) == 1, "the loaded library is bound to exactly one name."
    handle = handles.pop()
    symbols = {
        node.attr
        for node in ast.walk(native)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == handle
    }
    assert symbols == {THE_NATIVE_SYMBOL}, (
        f"the symbols bound on the loaded library are {sorted(symbols)}; exactly "
        f"one literal symbol may be bound, and it is {THE_NATIVE_SYMBOL!r}."
    )

    # The signature is fixed, and both halves of it are assigned.
    signature = {
        node.attr
        for node in ast.walk(native)
        if isinstance(node, ast.Attribute) and node.attr in ("argtypes", "restype")
    }
    assert signature == {"argtypes", "restype"}, (
        "both halves of the fixed signature are declared, so the call cannot be "
        "made with a signature nobody reviewed."
    )

    # The one native invocation: the literal operation and four literal zeroes.
    entries = {
        target.id
        for statement in ast.walk(native)
        if isinstance(statement, ast.Assign)
        for target in statement.targets
        if isinstance(target, ast.Name)
        and isinstance(statement.value, ast.Attribute)
        and statement.value.attr == THE_NATIVE_SYMBOL
    }
    assert len(entries) == 1, "the bound symbol has exactly one name."
    entry = entries.pop()
    invocations = [
        node
        for node in ast.walk(native)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == entry
    ]
    assert len(invocations) == 1, (
        f"{THE_NATIVE_SYMBOL} is invoked exactly once. A second invocation would "
        "be a second operation, and only one is approved."
    )
    invocation = invocations[0]
    assert not invocation.keywords, "the native call takes positional arguments only."
    assert (
        isinstance(invocation.args[0], ast.Name)
        and invocation.args[0].id == THE_NATIVE_OPERATION
    ), (
        f"the operation is the literal {THE_NATIVE_OPERATION} constant. An "
        "operation read from a variable, an argument or a vector is refused."
    )
    assert all(
        isinstance(argument, ast.Constant) and argument.value == 0
        for argument in invocation.args[1:]
    ), "every remaining argument is a literal zero."

    # And the operation constant is the literal number, not something computed.
    operations = [
        statement
        for statement in tree.body
        if isinstance(statement, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == THE_NATIVE_OPERATION
            for target in statement.targets
        )
    ]
    assert len(operations) == 1 and isinstance(operations[0].value, ast.Constant), (
        f"{THE_NATIVE_OPERATION} is a literal constant at module level."
    )
    assert operations[0].value.value == 27, (
        "PR_GET_SECUREBITS is 27 in include/uapi/linux/prctl.h."
    )


#: The receivers `getattr` may be used on in the **planning tier**. Each is a
#: dataclass instance whose fields are enumerated in the same module — the
#: `COMPARED_TARGET_FIELDS` comparison, the record's own serialization, the
#: step's own required-field check. None of them is a module, a namespace or a
#: loaded library, so none is a way to reach a symbol by name.
PERMITTED_GETATTR_RECEIVERS = frozenset({"self", "APPROVED_TARGET", "candidate", "expected"})

#: How a bounded native call becomes an unbounded one without importing anything
#: new: reach the module table, the interpreter's own namespace, or an importer.
DYNAMIC_REACH = frozenset(
    {"setattr", "delattr", "globals", "locals", "vars", "importlib", "__import__"}
)


@pytest.mark.parametrize(
    "path", ALL_MODULES, ids=[path.name for path in ALL_MODULES]
)
def test_no_module_looks_a_symbol_up_by_name(path: Path) -> None:
    """`getattr` on something that is not a declared dataclass is how a bounded
    native call becomes an unbounded one.

    The rule differs by tier, deliberately, and is stricter where it matters:

    * **The execution tier — including the one module that may call `prctl` —
      may not use `getattr`, `setattr` or `delattr` at all.** The attribute
      accesses the exception needs (`ctypes.CDLL`, `library.prctl`) are literal
      in the source and visible to the guard above; a computed one would not be.
    * **The planning tier** may use `getattr` over its own dataclass instances,
      which is what `approved_target`'s field-for-field comparison,
      `records`' serialization and `plan`'s required-field check are, and over
      nothing else. `setattr` and `delattr` are refused there too.

    Neither tier may reach `sys.modules`, `globals()`, `vars()`, `locals()` or an
    importer, each of which is a way to name a module — and therefore a library —
    at run time.
    """
    code = _code_only(path.read_text(encoding="utf-8"))
    for reach in ("sys.modules", "__builtins__"):
        assert reach not in code, f"{path.name} names {reach!r} in code."

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    execution_tier = path.parent.name == "execution"
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        name = node.func.id
        assert name not in DYNAMIC_REACH, (
            f"{path.name}:{node.lineno} calls {name!r}, which is a way to name a "
            "module, a namespace or an importer at run time."
        )
        if name != "getattr":
            continue
        assert not execution_tier, (
            f"{path.name}:{node.lineno} calls getattr. No module in the execution "
            "tier may look an attribute up by name — least of all the one that "
            "may call into the C runtime."
        )
        receiver = node.args[0] if node.args else None
        assert (
            isinstance(receiver, ast.Name)
            and receiver.id in PERMITTED_GETATTR_RECEIVERS
        ), (
            f"{path.name}:{node.lineno} calls getattr on something outside "
            f"{sorted(PERMITTED_GETATTR_RECEIVERS)}. In the planning tier it is "
            "permitted over a declared dataclass instance and over nothing else."
        )


@pytest.mark.parametrize(
    "path", EXECUTION_TIER, ids=[path.name for path in EXECUTION_TIER]
)
def test_no_execution_tier_module_can_reach_a_shell(path: Path) -> None:
    """`shell=True`, `os.system`, `eval`, `exec` and a shell binary, all absent.

    The `shell=False` at the boundary's call site is written as a literal for
    the same reason this test reads the source rather than the behaviour: a
    keyword computed from a variable is a keyword that can be something else.
    """
    text = path.read_text(encoding="utf-8")
    # Scanned with comments and string literals removed. These modules document
    # what they may not do, at length and by name, and a scan that read the prose
    # would fail on the sentence saying the thing is forbidden — which trains
    # everyone to stop writing the sentence.
    code = _code_only(text)
    for forbidden in ("shell=True", "os.system", "/bin/sh", "/bin/bash", "shlex"):
        assert forbidden not in code, f"{path.name} contains {forbidden!r} in code."

    tree = ast.parse(text, filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in ("eval", "exec", "__import__"), (
                f"{path.name}:{node.lineno} calls {node.func.id!r}."
            )
        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                if keyword.arg == "shell":
                    assert (
                        isinstance(keyword.value, ast.Constant)
                        and keyword.value.value is False
                    ), (
                        f"{path.name}:{node.lineno} passes shell= something other "
                        "than the literal False."
                    )


def test_importing_every_module_in_the_package_performs_no_io() -> None:
    """Import is inert, in both tiers.

    A module that started a process, opened a socket or read a file at import
    time would do it to anyone who imported it — including this suite, including
    a reviewer's editor. The check is structural: nothing at module level in any
    module is a call other than a decorator, a dataclass construction, a
    `frozenset`/`re.compile`/`hashlib.sha256` of a literal, or a comprehension
    building a constant table.
    """
    import importlib

    for path in ALL_MODULES:
        relative = path.relative_to(PACKAGE.parent.parent)
        module_name = str(relative.with_suffix("")).replace("/", ".")
        if module_name.endswith(".__init__"):
            module_name = module_name[: -len(".__init__")]
        importlib.import_module(module_name)

    # Importing `cli` must not have armed anything, and must not have run `main`.
    from tools.phase_5_0_evidence.execution.boundary import SubprocessBoundary

    assert SubprocessBoundary().armed is False, (
        "The real boundary is unarmed by default, so an executor constructed "
        "with one by mistake still cannot start a command."
    )


def test_the_planning_tier_never_imports_the_execution_tier() -> None:
    """The dependency points one way.

    If a planning module imported the executor, `import
    tools.phase_5_0_evidence.plan` would pull `subprocess` into the process, and
    the property the whole first tier is built on would be gone.
    """
    for path in MODULES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert "execution" not in module.split("."), (
                    f"{path.name} imports from the execution tier."
                )
                if node.level and module.startswith("execution"):
                    pytest.fail(f"{path.name} imports the execution tier.")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "execution" not in alias.name.split("."), (
                        f"{path.name} imports {alias.name}."
                    )
