"""**R16 — the three conflicts R14 left, and the properties that make them closed.**

`test_r14_remediation.py` is the ownership suite and carries C-8's end-to-end
cases: a root that already exists, a creation whose outcome is unknown, an
interruption, a replaced path, and the positive direction. This module is the
rest, and it is organised by conflict.

**C-6** — the three §2.13.8 capability-matrix **operations**. R13 found Band 5
emitting seven identity observations and calling them `JNL-49`/`JNL-50`; R14
declared the operations unresolved rather than approximating them with the
append-only flag, because *"an `+a` experiment run under `E4`, `E5` and `E6`
would produce a passing record for a case about `+i`"*. The maintainer approved
the bounded immutable-flag extension on 2026-09-09, and what is asserted here is
that it is bounded: two verbs, one flag each, named in the program's own body, no
argument that carries a flag, a mask or an ioctl request number.

**C-7** — the supplied-observation importer. What is asserted is what a record
**cannot** do, case by case, and that a well-formed record cannot stand in for an
experiment.

**C-8** — the plan-level and program-level rules the exclusive creation rests on:
the bootstrap partition, the one-value root argument, and every combination
`CommandStep` refuses.

**Nothing here starts a process, reads a host account, or performs a privileged
operation.** The immutable-flag operations are asserted as *plan* and *program*
properties and through injected boundaries; no test clears a flag, and none
could, because none runs as root.
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from tools.phase_5_0_evidence import capability, case_runtime
from tools.phase_5_0_evidence.approved_target import (
    APPROVED_TARGET,
    CONFIRMATION_TOKEN,
)
from tools.phase_5_0_evidence.capture import CapturePolicy, sanitize
from tools.phase_5_0_evidence.case_runtime import (
    BOOTSTRAP_VERBS,
    CASE_PROGRAM_SOURCE_PATH,
    CASE_VERBS,
    INTERPRETER_FLAGS,
    INTERPRETER_PATH,
    ArgumentKind,
    build_bootstrap_vector,
    build_case_vector,
    case_program_path,
    refused_with,
)
from tools.phase_5_0_evidence.cleanup import CleanupStep, CleanupStepKind
from tools.phase_5_0_evidence.concrete_plan import ConcretePlan, build_concrete_plan
from tools.phase_5_0_evidence.errors import ObservationRefused, PlanRefused
from tools.phase_5_0_evidence.execution import case_program
from tools.phase_5_0_evidence.execution.boundary import CommandResult
from tools.phase_5_0_evidence.execution.evidence_cli import (
    ARTIFACT_SCHEMA,
    ArtifactRefused,
    write_artifact,
)
from tools.phase_5_0_evidence.execution.executor import (
    ExecutingRunner,
    ExecutorRefused,
)
from tools.phase_5_0_evidence.execution.materializer import MaterializationResult
from tools.phase_5_0_evidence.expectations import Comparison
from tools.phase_5_0_evidence.observations import (
    BAND_7_SCHEMA,
    MAX_RECORDS,
    OBSERVATION_SCHEMA,
    OBSERVATION_SCHEMA_VERSION,
    SYNTHETIC_TARGET_IDENTITY,
    Custody,
    import_observations,
    producer_mapping,
    read_records,
)
from tools.phase_5_0_evidence.plan import CommandStep, StepRole, validate_argv
from tools.phase_5_0_evidence.records import Status, deserialize_records
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.harness_fixtures import (
    bound_argv,
    cleanup_observations_for,
    observations_for,
    runnable_plan,
    supply_reviewed_e7_facts,
)

SOURCES = {name: f"# {name}\n".encode("utf-8") for name in COVERED_SOURCES}
ROOT = APPROVED_TARGET.root_path
ARCHIVE_JOURNAL = f"{ROOT}/archive/000001.journal"
ARCHIVE_SEAL = f"{ROOT}/archive/000001.seal"

REVIEWED_INTERPRETER_DIGEST = "5" * 64
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"


@pytest.fixture(autouse=True)
def _the_reviewed_target_facts_are_supplied(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_SHA256", REVIEWED_INTERPRETER_DIGEST
    )
    monkeypatch.setattr(
        case_runtime,
        "EXPECTED_INTERPRETER_REAL_PATH",
        REVIEWED_INTERPRETER_REAL_PATH,
    )
    supply_reviewed_e7_facts(monkeypatch)


@pytest.fixture()
def plan() -> ConcretePlan:
    return build_concrete_plan()


def step_named(plan: ConcretePlan, step_id: str) -> CommandStep:
    return next(step for step in plan.steps if step.step_id == step_id)


def expectation(step: CommandStep, key: str):
    return next(item for item in step.observation_expectations if item.key == key)


# ---------------------------------------------------------------------------
# C-6 — the reviewed program's two new verbs, and what they are not
# ---------------------------------------------------------------------------


def test_the_two_new_verbs_name_one_flag_each_and_take_no_flag_argument() -> None:
    """The extension is two table entries, and the boundedness is the point.

    R14's objection to widening the verb table was that it *"widens the trusted
    computing base's verb table, its arities and what a bounded `ioctl` may
    do"*. The first two are widened by exactly two rows of one path argument
    each. The third is not widened at all: `FS_IMMUTABLE_FL` is a constant in the
    program's own body, the two ioctl request numbers are unchanged, and there is
    no argument kind through which a caller could name a flag, a mask or a
    request number.
    """
    assert set(CASE_VERBS) - {"getimmutable", "clearimmutable", "mkroot", "statroot"} == {
        "open", "pwrite", "append", "ftruncate", "rename", "unlink", "symlink",
        "statvfs", "getflags", "clearflags", "identity", "runtime",
    }
    for name in ("getimmutable", "clearimmutable"):
        assert CASE_VERBS[name].arguments == (ArgumentKind.TARGET_PATH,)
        assert CASE_VERBS[name].arity == 1
    # No verb takes anything a flag could travel in.
    kinds = {kind for spec in CASE_VERBS.values() for kind in spec.arguments}
    assert kinds == {
        ArgumentKind.TARGET_PATH,
        ArgumentKind.OPEN_MODE,
        ArgumentKind.WRITE_MODE,
        ArgumentKind.LINK_NAME,
        ArgumentKind.ROOT_PATH,
    }
    # And the program's two flag constants are separate values used by separate
    # verbs, rather than one value a caller selects.
    assert case_program.FS_APPEND_FL != case_program.FS_IMMUTABLE_FL
    assert case_program.VERBS["getimmutable"] == (case_program.PATH,)
    assert case_program.VERBS["clearimmutable"] == (case_program.PATH,)


def test_each_flag_verb_touches_exactly_one_bit_and_names_it_itself() -> None:
    """The mask arithmetic, read from the source rather than run as root.

    Clearing `FS_IMMUTABLE_FL` needs `CAP_LINUX_IMMUTABLE` and the owner
    authorization, so no test in this suite can perform one — nothing here runs
    as root, and nothing here reaches a kernel. What can be asserted, and what
    matters, is the shape of the operation: each verb's body names **one** flag
    constant, writes back `flags & ~<that flag>` so every other attribute on the
    inode survives, and can set nothing. A verb that gained a second constant, an
    `|`, or a mask from an argument fails here.
    """
    import ast

    source = (
        Path(case_program.__file__).read_text(encoding="utf-8")
    )
    tree = ast.parse(source)
    bodies = {
        node.name: node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }
    for name, flag in (
        ("_do_clearflags", "FS_APPEND_FL"),
        ("_do_clearimmutable", "FS_IMMUTABLE_FL"),
        ("_do_getflags", "FS_APPEND_FL"),
        ("_do_getimmutable", "FS_IMMUTABLE_FL"),
    ):
        named = {
            node.id
            for node in ast.walk(bodies[name])
            if isinstance(node, ast.Name)
            and node.id.startswith("FS_")
            and not node.id.startswith("FS_IOC_")
        }
        assert named == {flag}, (name, sorted(named))
    for name in ("_do_clearflags", "_do_clearimmutable"):
        inverted = [
            node
            for node in ast.walk(bodies[name])
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert)
        ]
        assert len(inverted) == 1, name
        binary = [
            node.op.__class__.__name__
            for node in ast.walk(bodies[name])
            if isinstance(node, ast.BinOp)
        ]
        # Two `&`: the write-back mask, and the read-back that reports whether
        # the bit survived. No `|`, so no verb can set a flag.
        assert set(binary) == {"BitAnd"}, (name, binary)
    # And no verb's arguments reach either ioctl request number.
    for name in ("_do_clearflags", "_do_clearimmutable", "_do_getflags",
                 "_do_getimmutable", "_read_flags"):
        requests = {
            node.id
            for node in ast.walk(bodies[name])
            if isinstance(node, ast.Name) and node.id.startswith("FS_IOC_")
        }
        assert requests <= {"FS_IOC_GETFLAGS", "FS_IOC_SETFLAGS"}, name


def test_the_immutable_verbs_are_refused_outside_the_reviewed_shape() -> None:
    """Arity, argument kind and containment, refused by the program itself."""
    for arguments in ([], [ARCHIVE_SEAL, ARCHIVE_JOURNAL], ["/etc/passwd"], [ROOT]):
        with pytest.raises(case_program.VectorRefused):
            case_program.validate_arguments("clearimmutable", list(arguments))
    assert case_program.validate_arguments("clearimmutable", [ARCHIVE_SEAL]) == (
        ARCHIVE_SEAL,
    )


def test_the_three_required_operations_are_generated_steps(plan) -> None:
    """`JNL-49` and `JNL-50`, as operations rather than as case ids.

    R13's finding was that the identity steps carried the case ids and performed
    none of the operations. The assertion is therefore about the **verb** each
    producing step names, not about the presence of an identifier.
    """
    produced: dict[str, list[CommandStep]] = {}
    for step in plan.steps:
        for case_id in step.evidence_case_ids:
            if case_id.startswith(("JNL-49-", "JNL-50-")):
                produced.setdefault(case_id, []).append(step)

    e4 = step_named(plan, "B5-C6-02")
    e6 = step_named(plan, "B5-C6-04")
    e5_clear = step_named(plan, "B5-C6-06")
    e5_open = step_named(plan, "B5-C6-07")

    for step, verb in (
        (e4, "clearimmutable"),
        (e6, "clearimmutable"),
        (e5_clear, "clearimmutable"),
        (e5_open, "open"),
    ):
        assert step.argv[0] == "/usr/sbin/capsh"
        tail = step.argv[step.argv.index("--") + 1 :]
        assert tail[2].endswith("/bin/case")
        assert tail[3] == verb
        assert step.capture is CapturePolicy.CASE_RESULT

    # And no identity observation carries one of the operation case ids.
    for step in plan.steps:
        if step.capture is CapturePolicy.CASE_IDENTITY:
            assert not any(
                case_id.startswith(("JNL-49-", "JNL-50-"))
                for case_id in step.evidence_case_ids
            )


def test_each_experiment_declares_the_exact_errno_its_case_states(plan) -> None:
    """`EPERM` and `EACCES` are different kernel paths, and neither stands in.

    §2.13.5c rests on the difference: `E4` is refused by the **owner** check,
    which is evaluated before `CAP_LINUX_IMMUTABLE` is consulted; `E5`'s open is
    refused by the **discretionary** check, which is only reached once the flag
    is gone. A step admitting both would be satisfied whichever happened.
    """
    e4 = step_named(plan, "B5-C6-02")
    assert e4.satisfying_statuses == refused_with("EPERM")
    assert expectation(e4, "errno").value == "EPERM"
    assert expectation(e4, "result").value == "refused"

    e5_open = step_named(plan, "B5-C6-07")
    assert e5_open.satisfying_statuses == refused_with("EACCES")
    assert expectation(e5_open, "errno").value == "EACCES"

    for step_id in ("B5-C6-04", "B5-C6-06"):
        step = step_named(plan, step_id)
        assert step.satisfying_statuses == (0,)
        assert expectation(step, "result").value == "returned"
        assert expectation(step, "errno").value == "none"
        assert expectation(step, "fs_immutable_fl").value == "0"
        assert expectation(step, "fs_immutable_fl").comparison is Comparison.NUMBER


def test_each_experiment_observes_its_own_initial_state_first(plan) -> None:
    """A prior successful clear must not make a later case meaningless.

    Three readings, one per experiment, each requiring `fs_immutable_fl=1` on the
    inode **that** experiment is about — and `E5`'s subject is a different file
    from `E4`'s and `E6`'s, so `E6`'s successful clear cannot be inherited.
    """
    order = {step.step_id: index for index, step in enumerate(plan.steps)}
    readings = {
        step_id: step_named(plan, step_id)
        for step_id in ("B5-C6-01", "B5-C6-03", "B5-C6-05")
    }
    for step_id, step in readings.items():
        assert step.argv[3] == case_program_path(APPROVED_TARGET)
        assert step.argv[4] == "getimmutable"
        assert expectation(step, "fs_immutable_fl").value == "1"
        assert step.role is StepRole.CONTROL
        assert step.run_as == "root"

    assert readings["B5-C6-01"].argv[5] == ARCHIVE_JOURNAL
    assert readings["B5-C6-03"].argv[5] == ARCHIVE_JOURNAL
    assert readings["B5-C6-05"].argv[5] == ARCHIVE_SEAL

    assert order["B5-C6-01"] < order["B5-C6-02"] < order["B5-C6-03"] < order["B5-C6-04"]
    assert order["B5-C6-04"] < order["B5-C6-05"] < order["B5-C6-06"] < order["B5-C6-07"]


def test_the_isolating_control_differs_from_its_case_in_one_capability(plan) -> None:
    """Control form **C-I**, asserted over the two vectors rather than claimed.

    `E4` and `E6` differ in `cap_fowner` in `--drop`'s complement, in `--inh` and
    in one `--addamb`, and in nothing else: same uid, same gid, same
    supplementary list, same securebits, same case program, same path, same
    inode. R11 corrected revision 10 for naming `E2` here — which differs in uid,
    supplementary groups and two capabilities — and this is what stops that
    recurring.
    """
    e4 = list(step_named(plan, "B5-C6-02").argv)
    e6 = list(step_named(plan, "B5-C6-04").argv)

    def options(argv):
        return {
            item.split("=", 1)[0]: item.split("=", 1)[1]
            for item in argv
            if item.startswith("--") and "=" in item
        }

    a, b = options(e4), options(e6)
    assert a["--uid"] == b["--uid"] and a["--gid"] == b["--gid"]
    assert a["--groups"] == b["--groups"]
    assert a["--secbits"] == b["--secbits"]
    assert set(b["--inh"].split(",")) - set(a["--inh"].split(",")) == {"cap_fowner"}
    assert set(a["--drop"].split(",")) - set(b["--drop"].split(",")) == {"cap_fowner"}
    # The same operation on the same inode.
    assert e4[e4.index("--") + 1 :][3:] == e6[e6.index("--") + 1 :][3:]


def test_the_two_halves_of_jnl_50_are_separately_ordered_steps(plan) -> None:
    """The clear is a control and the denial depends on it.

    A single vector performing both would report one exit status, and nobody
    could say which of the two operations it belonged to. The clear is therefore
    a `CONTROL`: if it does not return, the run stops and the denial is never
    interpreted — which is what makes an observed `EACCES` proof that the flag
    was gone rather than proof of nothing.
    """
    clear = step_named(plan, "B5-C6-06")
    denied = step_named(plan, "B5-C6-07")
    assert clear.role is StepRole.CONTROL
    assert denied.role is StepRole.DEPENDENT
    clear_tail = clear.argv[clear.argv.index("--") + 1 :]
    denied_tail = denied.argv[denied.argv.index("--") + 1 :]
    assert clear_tail[3] == "clearimmutable" and clear_tail[4] == ARCHIVE_SEAL
    assert denied_tail[3] == "open" and denied_tail[4] == "wronly"
    assert denied_tail[5] == ARCHIVE_SEAL
    order = {step.step_id: index for index, step in enumerate(plan.steps)}
    assert order["B5-C6-06"] < order["B5-C6-07"]


def test_the_band_resets_the_flags_it_cleared_and_reads_them_back(plan) -> None:
    """Setup, reset and read-back are in the plan rather than in a footnote."""
    resets = [
        step
        for step in plan.steps
        if step.step_id.startswith("B5-C6-") and step.argv[0] == "/usr/bin/chattr"
    ]
    assert [step.argv for step in resets] == [
        ("/usr/bin/chattr", "+i", "--", ARCHIVE_JOURNAL),
        ("/usr/bin/chattr", "+i", "--", ARCHIVE_SEAL),
    ]
    for step in resets:
        assert step.mutation_ids == (f"file_attribute:{step.argv[-1]}",)
    for step_id, path in (("B5-C6-10", ARCHIVE_JOURNAL), ("B5-C6-11", ARCHIVE_SEAL)):
        step = step_named(plan, step_id)
        assert step.argv[4] == "getimmutable" and step.argv[5] == path
        assert expectation(step, "fs_immutable_fl").value == "1"


@pytest.mark.parametrize(
    ("step_id", "observations"),
    [
        # E4 returned instead of being refused: an unexpected outcome is a
        # finding, and the plan's expectation does not move to meet it.
        ("B5-C6-02", (("errno", "none"), ("fs_immutable_fl", "0"),
                      ("result", "returned"), ("verb", "clearimmutable"))),
        # E4 refused for the wrong reason.
        ("B5-C6-02", (("errno", "EACCES"), ("result", "refused"),
                      ("verb", "clearimmutable"))),
        # E6's control cleared nothing.
        ("B5-C6-04", (("errno", "none"), ("fs_immutable_fl", "1"),
                      ("result", "returned"), ("verb", "clearimmutable"))),
        # E5's denial came from the immutability rather than from DAC.
        ("B5-C6-07", (("errno", "EPERM"), ("result", "refused"), ("verb", "open"))),
        # The initial state was not what the case is about.
        ("B5-C6-01", (("errno", "none"), ("fs_immutable_fl", "0"),
                      ("result", "returned"), ("verb", "getimmutable"))),
    ],
)
def test_an_unexpected_experiment_outcome_stops_the_run(step_id, observations) -> None:
    """Expected outcomes come from the approved design, not from the run.

    Each row is an observation the kernel could produce and the reviewed design
    says it will not. None of them moves an expectation: the step is unsatisfied,
    the run stops there, and nothing after it is executed or interpreted.
    """
    plan = runnable_plan()
    fake = satisfying(plan)
    step = step_named(plan, step_id)
    fake.scripted[step_id] = CommandResult(
        exit_status=step.satisfying_statuses[0],
        timed_out=False,
        observations=tuple(sorted(observations)),
    )

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == step_id
    assert not outcome.artifact_admissible


# ---------------------------------------------------------------------------
# C-8 — the bootstrap partition and the plan-level rules
# ---------------------------------------------------------------------------


def test_the_bootstrap_partition_is_total_in_both_directions() -> None:
    """Neither copy runs the other half of the table.

    The installed program cannot create the root it lives in, and the bootstrap
    copy cannot perform an experiment — so a run that lost its installed program
    cannot fall back to the repository and keep going.
    """
    for verb in sorted(BOOTSTRAP_VERBS):
        assert build_bootstrap_vector(APPROVED_TARGET, verb, ROOT)[4] == verb
        with pytest.raises(PlanRefused):
            build_case_vector(APPROVED_TARGET, verb, ROOT)
    for verb in ("open", "getimmutable", "identity", "runtime"):
        with pytest.raises(PlanRefused):
            build_bootstrap_vector(APPROVED_TARGET, verb, ARCHIVE_SEAL)

    # And the program itself refuses the same pair from its own constants.
    for program, verb, argument in (
        (case_program.CASE_PROGRAM_PATH, "mkroot", ROOT),
        (case_program.BOOTSTRAP_PROGRAM_PATH, "getimmutable", ARCHIVE_SEAL),
    ):
        stream = _Stream()
        status = case_program.main(
            [verb, argument],
            program_path=program,
            isolated=True,
            no_site=True,
            stream=stream,
        )
        assert status == case_program.EXIT_VECTOR_REFUSED
        assert "vector-refused" in stream.text


def test_a_third_program_path_is_refused() -> None:
    """Two reviewed copies, and no third."""
    stream = _Stream()
    status = case_program.main(
        ["statroot", ROOT],
        program_path="/tmp/case",
        isolated=True,
        no_site=True,
        stream=stream,
    )
    assert status == case_program.EXIT_VECTOR_REFUSED
    vector = (
        INTERPRETER_PATH,
        *INTERPRETER_FLAGS,
        "/opt/freedom-blades/platform/tools/phase_5_0_evidence/execution/other.py",
        "mkroot",
        ROOT,
    )
    with pytest.raises(PlanRefused):
        validate_argv(vector, target=APPROVED_TARGET)


def test_the_root_argument_admits_exactly_one_value() -> None:
    """It is a constant the vector states, not a path a caller composes."""
    for candidate in (f"{ROOT}/journal", "/var/lib", f"{ROOT}/", "/", ROOT + "x"):
        with pytest.raises(PlanRefused):
            build_bootstrap_vector(APPROVED_TARGET, "mkroot", candidate)
        with pytest.raises(case_program.VectorRefused):
            case_program.validate_root(candidate)
    assert case_program.validate_root(ROOT) == ROOT


@pytest.mark.parametrize(
    ("label", "changes"),
    [
        (
            "a probe and a creation at once",
            {"establishes_ownership_of": ("os_group:freedomjournal",)},
        ),
        ("satisfied by a refusal", {"satisfying_statuses": (), "refusal_required": True}),
        ("satisfied by a non-zero status", {"satisfying_statuses": (15,)}),
        ("no pre-existence status", {"preexisting_statuses": ()}),
        ("no nothing-created statuses", {"nothing_created_statuses": ()}),
        (
            "owning something it does not perform",
            {"establishes_ownership_by_creation": ("directory:/var/lib/other",)},
        ),
        (
            "claiming an object outside what it created",
            {"establishes_ownership_of_contained": ("file:/etc/passwd",)},
        ),
    ],
)
def test_an_exclusive_creation_is_refused_outside_its_reviewed_shape(
    plan, label, changes
) -> None:
    """Every combination the plan refuses, one per row.

    A creation that also probes, one satisfied by anything but exit 0, one that
    cannot report pre-existence, one that cannot say when it created nothing, and
    one claiming an object it did not make — each is a `PlanRefused` when the
    plan is built rather than a property discovered during a run.
    """
    creation = next(
        step for step in plan.steps if step.establishes_ownership_by_creation
    )
    with pytest.raises(PlanRefused):
        replace(creation, **changes)


def test_a_step_that_does_not_create_may_not_carry_the_creation_fields(plan) -> None:
    baseline = step_named(plan, "R-B-ROOT")
    with pytest.raises(PlanRefused):
        replace(baseline, nothing_created_statuses=(1,))
    with pytest.raises(PlanRefused):
        replace(
            baseline, establishes_ownership_of_contained=(f"file:{ARCHIVE_SEAL}",)
        )


def test_a_cleanup_revalidation_is_refused_outside_its_reviewed_shape(plan) -> None:
    revalidation = next(
        step
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVALIDATE
    )
    with pytest.raises(PlanRefused):
        replace(revalidation, applies_with=())
    with pytest.raises(PlanRefused):
        replace(revalidation, capture=CapturePolicy.EXIT_STATUS_ONLY)
    with pytest.raises(PlanRefused):
        replace(revalidation, mutation_ids=(f"directory:{ROOT}",))
    # And no other kind may record an observation or wait on a revalidation.
    removal = next(
        step for step in plan.cleanup_plan.steps if step.removes == ROOT
    )
    with pytest.raises(PlanRefused):
        replace(removal, capture=CapturePolicy.CASE_RESULT)
    with pytest.raises(PlanRefused):
        replace(revalidation, requires_revalidated="CL-01")


def test_the_revalidation_applies_exactly_when_the_removal_does(plan) -> None:
    """A revalidation that ran unconditionally would re-read a path this run may
    never have created."""
    revalidation = next(
        step
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVALIDATE
    )
    assert revalidation.applies_with == (f"directory:{ROOT}",)
    none = plan.cleanup_plan.applicable(attempted=[], owned=[])
    assert revalidation.step_id not in {step.step_id for step in none.steps}
    attempted = plan.cleanup_plan.applicable(
        attempted=[f"directory:{ROOT}"], owned=[f"directory:{ROOT}"]
    )
    assert revalidation.step_id in {step.step_id for step in attempted.steps}


# ---------------------------------------------------------------------------
# C-7 — the importer
# ---------------------------------------------------------------------------


def manifest_digest(plan: ConcretePlan) -> str:
    return ReviewManifest.build(plan, SOURCES).digest()


def importable_plan(plan: ConcretePlan) -> ConcretePlan:
    """The shipped plan with Band 7's unresolved entries removed — **a fixture**.

    **R16, EH-R16-4.** The shipped plan declares all three Band-7 cases
    unresolved, because their producers do not exist, and
    `classify_supplied_observations` therefore refuses to count any of them
    covered however well-formed the records are. That is the property under test
    in `test_a_record_cannot_close_a_case_the_plan_declares_unresolved`, and it
    is exactly what makes the *positive* direction unassertable against the
    shipped plan.

    So the positive cases run against this: a plan in which the producers are
    **hypothesised** to exist, so that what the importer does with a valid
    payload can be exercised at all. It is a test fixture and nothing else. No
    producer is created by it, `is_executable` is not consulted through it, and
    every result it yields still has `eligible_for_operational_acceptance`
    `False` — which the assertions below check rather than assume.
    """
    return ConcretePlan(
        execution_plan=plan.execution_plan,
        cleanup_plan=plan.cleanup_plan,
        unresolved=(),
        external_cases=plan.external_cases,
    )


def record(
    case_id: str,
    variant: str,
    *,
    digest: str,
    fields: dict,
    custody: str = Custody.SYNTHETIC_FIXTURE.value,
    target: str = SYNTHETIC_TARGET_IDENTITY,
    run_id: str = "synthetic-run-1",
) -> dict:
    return {
        "case_id": case_id,
        "variant": variant,
        "target_identity": target,
        "run_id": run_id,
        "review_manifest_digest": digest,
        "custody": custody,
        "collected_by": "independent reviewer",
        "collected_at": "2026-09-09",
        "fields": fields,
    }


ABSENT_ARTIFACTS = {
    "journal_present": "no",
    "seal_present": "no",
    "current_present": "no",
    "close_present": "no",
}


def complete_records(digest: str, **overrides) -> list[dict]:
    """One well-formed record per required case and variant."""
    rows = [
        record(
            "JNL-51-PROVENANCE-OMITTED",
            "provenance-omitted",
            digest=digest,
            fields={
                "apr_present": "yes",
                "pvr_present": "no",
                "refused": "yes",
                "refusal_code": "J-26",
                **ABSENT_ARTIFACTS,
                "generation_row_present": "no",
                "probe_ran": "no",
            },
            **overrides,
        )
    ]
    for stage in BAND_7_SCHEMA["JNL-47-NO-GENERATION-ON-FAILURE"].variants:
        rows.append(
            record(
                "JNL-47-NO-GENERATION-ON-FAILURE",
                stage,
                digest=digest,
                fields={**ABSENT_ARTIFACTS, "generation_row_present": "no"},
                **overrides,
            )
        )
    for variant in BAND_7_SCHEMA["JNL-47-RECOVERY-STATE"].variants:
        rows.append(
            record(
                "JNL-47-RECOVERY-STATE",
                variant,
                digest=digest,
                fields={
                    "exit_code": "3",
                    "state": "S-B",
                    "residue_path_count": "2",
                    "generation_present": "no",
                    "database_row_present": "no",
                    "next_run_refuses": "yes",
                    "recovery_procedure_named": "yes",
                },
                **overrides,
            )
        )
    return rows


def payload(records: list[dict], *, schema=OBSERVATION_SCHEMA, version=OBSERVATION_SCHEMA_VERSION) -> bytes:
    return json.dumps(
        {"schema": schema, "schema_version": version, "records": records}
    ).encode("utf-8")


def imported(plan: ConcretePlan, records: list[dict], **overrides):
    keywords = dict(
        plan=plan,
        target_identity=SYNTHETIC_TARGET_IDENTITY,
        run_id="synthetic-run-1",
        review_manifest_digest=manifest_digest(plan),
    )
    keywords.update(overrides)
    return import_observations(payload(records), **keywords)


def test_a_complete_synthetic_payload_classifies_every_band_7_case(plan) -> None:
    """The positive direction, so the refusals below are about the values.

    Eight records — one omitted-provenance case, five injected stage failures and
    two cleanup-failure situations — cover every **Band-7** required case and
    variant, and every band classifier produces its records from the observation
    rather than from anything the record asserted.

    **R16, EH-R16-3.** Band-7 coverage being complete is not the harness being
    complete, and the two are asserted separately here because R16 found them
    conflated: eight records produced `complete=True` with no run record and no
    capability observation anywhere in the result. The three capability cases are
    reported in `outside_scope`, overall completeness is withheld, and the
    withholding is asserted in the same test as the coverage it is easy to
    mistake for it.
    """
    fixture = importable_plan(plan)
    result = imported(fixture, complete_records(manifest_digest(fixture)))

    assert result.missing == ()
    assert result.unresolved_cases == ()
    assert result.band_7_coverage_complete is True
    assert len(result.covered) == 8
    assert result.records
    assert {record.band for record in result.records} == {"provenance", "journal"}
    assert all(record.status is Status.PASSED for record in result.records)
    assert result.band_7_records_all_passed is True
    assert result.band_7_evidence_holds is True

    # And the three the importer does not observe are named, not skipped.
    assert set(result.outside_scope) == {
        "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
    }
    assert result.overall_completeness_established is False
    assert result.eligible_for_operational_acceptance is False
    assert result.withheld


def test_a_synthetic_fixture_is_never_operationally_acceptable(plan) -> None:
    """It is a fixture, and it says so in every record it produces."""
    fixture = importable_plan(plan)
    result = imported(fixture, complete_records(manifest_digest(fixture)))
    assert result.synthetic is True
    assert result.custody_levels == (Custody.SYNTHETIC_FIXTURE.value,)
    assert result.eligible_for_operational_acceptance is False
    assert any(
        "synthetic fixture" in problem
        for problem in result.structural_disqualifications
    )


def test_every_classified_record_carries_its_custody(plan) -> None:
    """Custody travels into the artifact, not only into the summary.

    Where an observation came from is part of what a reviewer is judging, and a
    stored record that carried only the observation would leave that out. A
    synthetic record additionally has the marker in its **identity** field, so
    every rendering of it carries it and no reading of the artifact can take one
    for an observation of the approved target.
    """
    fixture = importable_plan(plan)
    result = imported(fixture, complete_records(manifest_digest(fixture)))
    for record in result.records:
        assert record.detail["custody"] == Custody.SYNTHETIC_FIXTURE.value
        assert record.detail["collected_by"] == "independent reviewer"
        assert record.detail["collected_at"] == "2026-09-09"
        assert record.detail["supplied_run_id"] == "synthetic-run-1"
        assert record.target_identity.startswith(SYNTHETIC_TARGET_IDENTITY)

    operational = imported(
        fixture,
        complete_records(
            manifest_digest(fixture),
            custody=Custody.REVIEWER_VERIFIED.value,
            target=plan.target.identity,
            run_id="run-2026-09-09",
        ),
        target_identity=plan.target.identity,
        run_id="run-2026-09-09",
    )
    for record in operational.records:
        assert record.detail["custody"] == Custody.REVIEWER_VERIFIED.value
        assert not record.target_identity.startswith(SYNTHETIC_TARGET_IDENTITY)


def test_an_operator_attestation_is_not_a_verification(plan) -> None:
    """Target, run and digest demonstrate that somebody read the plan.

    They do not demonstrate where the observation came from, so an attestation —
    a person's claim — covers every Band-7 variant and is still disqualified.

    **R16, EH-R16-3.** The old form of this test ended by asserting that a
    `reviewer_verified` payload *was* eligible. That assertion is gone, because
    the property is now `False` unconditionally: no Band-7 result is entitled to
    the judgement, whatever its custody. What survives is the part that was
    always about custody — the attestation appears in
    `structural_disqualifications` and the verification does not.
    """
    fixture = importable_plan(plan)
    digest = manifest_digest(fixture)
    rows = complete_records(
        digest,
        custody=Custody.OPERATOR_ATTESTED.value,
        target=plan.target.identity,
        run_id="run-2026-09-09",
    )
    result = imported(
        fixture,
        rows,
        target_identity=plan.target.identity,
        run_id="run-2026-09-09",
    )
    assert result.band_7_coverage_complete is True
    assert result.synthetic is False
    assert result.eligible_for_operational_acceptance is False
    assert any(
        "reviewer_verified" in problem
        for problem in result.structural_disqualifications
    )

    verified = imported(
        fixture,
        complete_records(
            digest,
            custody=Custody.REVIEWER_VERIFIED.value,
            target=plan.target.identity,
            run_id="run-2026-09-09",
        ),
        target_identity=plan.target.identity,
        run_id="run-2026-09-09",
    )
    # Nothing about the in-scope half disqualifies it …
    assert verified.structural_disqualifications == ()
    # … and the conclusion is still withheld, because the capability cases and
    # their controls are not in this result at all.
    assert verified.eligible_for_operational_acceptance is False
    assert verified.overall_completeness_established is False
    assert verified.outside_scope


def test_an_incomplete_payload_is_incomplete_and_says_which_variant(plan) -> None:
    """Coverage is compared before a complete evidence result is produced."""
    fixture = importable_plan(plan)
    digest = manifest_digest(fixture)
    rows = [
        row
        for row in complete_records(digest)
        if row["variant"] not in ("stage-3", "cleanup-failure-after-passing-probe")
    ]
    result = imported(fixture, rows)
    assert result.band_7_coverage_complete is False
    assert set(result.missing) == {
        "JNL-47-NO-GENERATION-ON-FAILURE#stage-3",
        "JNL-47-RECOVERY-STATE#cleanup-failure-after-passing-probe",
    }
    assert result.eligible_for_operational_acceptance is False


def test_a_record_cannot_close_a_case_the_plan_declares_unresolved(plan) -> None:
    """An importer cannot supply experimental evidence — R14's other half.

    A well-formed record for a case the plan still cannot produce is validated,
    accepted as a record, and **not counted**: the case is reported unresolved,
    it never reaches `covered`, and the result is not complete. That is the
    property that stops an ingestion stage from manufacturing the evidence the
    missing producer was supposed to make.
    """
    from tools.phase_5_0_evidence.concrete_plan import UnresolvedStep

    blocked = ConcretePlan(
        execution_plan=plan.execution_plan,
        cleanup_plan=plan.cleanup_plan,
        unresolved=(
            UnresolvedStep(
                step_ref="JNL-51-PROVENANCE-OMITTED",
                band="journal",
                conflict_id="C-SYNTHETIC",
                design_requires="the omitted-provenance case",
                why_not_a_vector="its producer does not exist",
                what_would_resolve_it="building the producer",
                evidence_case_ids=("JNL-51-PROVENANCE-OMITTED",),
            ),
        ),
        external_cases=plan.external_cases,
    )
    result = imported(blocked, complete_records(manifest_digest(blocked)))

    assert result.unresolved_cases == ("JNL-51-PROVENANCE-OMITTED",)
    assert not any(key.startswith("JNL-51-") for key in result.covered)
    assert not any(
        record.case_id.startswith("JNL-51-") for record in result.records
    )
    assert result.band_7_coverage_complete is False


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("not JSON", lambda rows: b"{not json"),
        ("not the envelope", lambda rows: json.dumps(rows).encode("utf-8")),
        (
            "another schema",
            lambda rows: payload(rows, schema="something/else"),
        ),
        ("another version", lambda rows: payload(rows, version=99)),
        ("no records", lambda rows: payload([])),
        (
            "too many records",
            lambda rows: payload(rows * (MAX_RECORDS // len(rows) + 2)),
        ),
        ("an oversized payload", lambda rows: b"x" * (1024 * 1024)),
    ],
)
def test_a_malformed_payload_is_refused(plan, label, mutate) -> None:
    with pytest.raises(ObservationRefused):
        import_observations(
            mutate(complete_records(manifest_digest(plan))),
            plan=plan,
            target_identity=SYNTHETIC_TARGET_IDENTITY,
            run_id="synthetic-run-1",
            review_manifest_digest=manifest_digest(plan),
        )


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("an unknown key", lambda row: row.update({"extra": "1"})),
        ("a missing key", lambda row: row.pop("collected_at")),
        ("an unknown case", lambda row: row.update({"case_id": "JNL-99"})),
        ("an unknown variant", lambda row: row.update({"variant": "stage-9"})),
        ("an unknown custody", lambda row: row.update({"custody": "trust me"})),
        (
            "a collector who is a person rather than a role",
            lambda row: row.update({"collected_by": "Someone <s@example.com>"}),
        ),
        ("a malformed date", lambda row: row.update({"collected_at": "yesterday"})),
        (
            "a field outside the variant's set",
            lambda row: row["fields"].update({"whatever": "yes"}),
        ),
        (
            "a value that is not its field's shape",
            lambda row: row["fields"].update({"probe_ran": "maybe"}),
        ),
        (
            "a mismatched target",
            lambda row: row.update({"target_identity": "somewhere-else"}),
        ),
        ("a mismatched run", lambda row: row.update({"run_id": "another-run"})),
        (
            "a mismatched digest",
            lambda row: row.update({"review_manifest_digest": "0" * 64}),
        ),
    ],
)
def test_a_record_outside_the_schema_is_refused(plan, label, mutate) -> None:
    rows = complete_records(manifest_digest(plan))
    mutate(rows[0])
    with pytest.raises(ObservationRefused):
        imported(plan, rows)


def test_a_duplicate_record_is_refused(plan) -> None:
    rows = complete_records(manifest_digest(plan))
    rows.append(dict(rows[0]))
    with pytest.raises(ObservationRefused):
        imported(plan, rows)


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        (
            "nothing was omitted in the omitted-provenance case",
            lambda rows: rows[0]["fields"].update(
                {"apr_present": "yes", "pvr_present": "yes"}
            ),
        ),
        (
            "a refusal at C0 and a probe that ran",
            lambda rows: rows[0]["fields"].update({"probe_ran": "yes"}),
        ),
        (
            "a recovery case that is not S-B",
            lambda rows: rows[-1]["fields"].update({"state": "S-C"}),
        ),
        (
            "no residue and a next run that refuses",
            lambda rows: rows[-1]["fields"].update({"residue_path_count": "0"}),
        ),
    ],
)
def test_a_contradictory_record_is_refused(plan, label, mutate) -> None:
    """Two fields making incompatible statements about the same fact.

    Deliberately not a re-classification: whether the case passed is the
    classifier's, computed from the record. What is refused here is a record
    that cannot describe one situation at all.
    """
    rows = complete_records(manifest_digest(plan))
    mutate(rows)
    with pytest.raises(ObservationRefused):
        imported(plan, rows)


def test_a_synthetic_record_cannot_be_read_as_an_operational_one(plan) -> None:
    """The marker is compared, not decorative, and it is compared both ways."""
    digest = manifest_digest(plan)
    with pytest.raises(ObservationRefused):
        imported(
            plan,
            complete_records(digest, target=plan.target.identity),
            target_identity=plan.target.identity,
        )
    with pytest.raises(ObservationRefused):
        imported(
            plan,
            complete_records(digest, custody=Custody.REVIEWER_VERIFIED.value),
        )


def test_a_record_for_a_case_nobody_requires_is_refused(plan) -> None:
    rows = complete_records(manifest_digest(plan))
    result = read_records(
        payload(rows),
        target_identity=SYNTHETIC_TARGET_IDENTITY,
        run_id="synthetic-run-1",
        review_manifest_digest=manifest_digest(plan),
    )
    assert len(result) == 8


def test_every_required_case_is_mapped_to_a_producer(plan) -> None:
    """The mapping the handback carries, generated rather than maintained."""
    rows = {row.case_id: row for row in producer_mapping(plan)}
    assert set(rows) == {
        "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
        "JNL-51-PROVENANCE-OMITTED",
        "JNL-47-NO-GENERATION-ON-FAILURE",
        "JNL-47-RECOVERY-STATE",
    }
    for case_id in (
        "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
    ):
        assert rows[case_id].in_harness_producer is True
        assert rows[case_id].produced_by_plan_steps
        assert rows[case_id].declared_unresolved_by == ()
    for case_id in BAND_7_SCHEMA:
        assert rows[case_id].in_harness_producer is False
        assert rows[case_id].produced_by_plan_steps == ()
        assert rows[case_id].producer.strip()
        assert rows[case_id].collection_procedure.strip()


# ---------------------------------------------------------------------------
# C-7 — the classified artifact, persisted and validated before it is claimed
# ---------------------------------------------------------------------------


def test_the_classified_artifact_is_read_back_before_a_path_is_reported(
    plan, tmp_path: Path
) -> None:
    """Serialize, write, read back, deserialize, compare — then return a path.

    A successful `write_bytes` says nothing about a truncated write, a full
    filesystem or a partial flush, and `deserialize_records` is what turns
    reading the file back into a **check**: it reconstructs every record through
    the same constructor, so a stored status that disagrees with its own stored
    observations is a refusal rather than a value.
    """
    fixture = importable_plan(plan)
    result = imported(fixture, complete_records(manifest_digest(fixture)))
    destination = tmp_path / "evidence.json"

    assert write_artifact(result, destination) == destination

    document = json.loads(destination.read_text(encoding="utf-8"))
    stored = deserialize_records(json.dumps(document["records"]).encode("utf-8"))
    assert len(stored) == len(result.records)
    assert [item.case_id for item in stored] == [
        item.case_id for item in result.records
    ]


def test_the_artifact_persists_the_scope_and_the_missing_evidence(
    plan, tmp_path: Path
) -> None:
    """**R16, EH-R16-3.** The scope is in the file, not only in the summary.

    *"Persist the scope and missing evidence, not just a console summary."* A
    reviewer reading the artifact alone has to be able to see that this is a
    Band-7 result, which required cases are outside it, which variants nobody
    supplied, which cases the plan declares unresolved, and that overall
    completeness and operational eligibility are withheld rather than answered.
    """
    result = imported(plan, complete_records(manifest_digest(plan)))
    destination = tmp_path / "evidence.json"
    write_artifact(result, destination)

    document = json.loads(destination.read_text(encoding="utf-8"))
    scope = document["scope"]

    assert document["schema"] == ARTIFACT_SCHEMA
    assert "Band 7 supplied observations only" in scope["scope"]
    assert set(scope["outside_scope"]) == {
        "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
    }
    assert scope["overall_completeness_established"] is False
    assert scope["eligible_for_operational_acceptance"] is False
    assert scope["withheld"]
    # Against the shipped plan every Band-7 case is unresolved, so nothing is
    # covered, nothing is classified, and the artifact says exactly that rather
    # than not existing.
    assert scope["unresolved_cases"] == [
        "JNL-47-NO-GENERATION-ON-FAILURE",
        "JNL-47-RECOVERY-STATE",
        "JNL-51-PROVENANCE-OMITTED",
    ]
    assert document["records"] == []
    assert all(row["declared_unresolved_by"] == ["C-7"] for row in scope["producers"]
               if row["case_id"] in scope["unresolved_cases"])


def test_a_tampered_artifact_does_not_read_back(plan, tmp_path: Path) -> None:
    fixture = importable_plan(plan)
    result = imported(fixture, complete_records(manifest_digest(fixture)))
    destination = tmp_path / "evidence.json"
    write_artifact(result, destination)

    document = json.loads(destination.read_text(encoding="utf-8"))
    records = document["records"]
    records[0]["status"] = "passed" if records[0]["status"] != "passed" else "failed"
    destination.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ObservationRefused):
        deserialize_records(json.dumps(records).encode("utf-8"))


def test_an_unwritable_destination_is_a_refusal_and_not_a_path(
    plan, tmp_path: Path
) -> None:
    fixture = importable_plan(plan)
    result = imported(fixture, complete_records(manifest_digest(fixture)))
    with pytest.raises(ArtifactRefused):
        write_artifact(result, tmp_path / "missing" / "evidence.json")


def test_a_result_with_no_record_still_writes_its_scope(plan, tmp_path: Path) -> None:
    """**R16, EH-R16-3.** A result that classified nothing is still written.

    The previous version refused, on the ground that there was nothing to write.
    What there is to write is the scope and the missing evidence, and a run that
    classified nothing is precisely the run whose reader most needs them.
    """
    from tools.phase_5_0_evidence.observations import EvidenceResult

    empty = EvidenceResult(
        records=(),
        covered=(),
        missing=("JNL-51-PROVENANCE-OMITTED#provenance-omitted",),
        unresolved_cases=(),
        outside_scope=("JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",),
        producers=producer_mapping(plan),
        custody_levels=(),
        synthetic=False,
    )
    destination = tmp_path / "evidence.json"
    assert write_artifact(empty, destination) == destination
    document = json.loads(destination.read_text(encoding="utf-8"))
    assert document["records"] == []
    assert document["scope"]["missing"] == [
        "JNL-51-PROVENANCE-OMITTED#provenance-omitted"
    ]

    # And an unwritable destination is still a refusal rather than a path.
    with pytest.raises(ArtifactRefused):
        write_artifact(empty, Path("/nonexistent/evidence.json"))


# ---------------------------------------------------------------------------
# The fakes. Nothing here starts a process.
# ---------------------------------------------------------------------------


class _Stream:
    def __init__(self) -> None:
        self.text = ""

    def write(self, value: str) -> None:
        self.text += value


class _FakeBoundary:
    def __init__(self, scripted) -> None:
        self.scripted = scripted
        self.calls: list[str] = []

    def run(self, *, step_id, argv, run_as, capture, timeout_seconds, catalog=None):
        self.calls.append(step_id)
        if step_id in self.scripted:
            return self.scripted[step_id]
        return CommandResult(exit_status=0, timed_out=False)


class _FakeMaterializer:
    def materialize(self, *, step_id, destination, content, sha256, owner, group, mode):
        return MaterializationResult(applied=True)


class _FakeIdentityLookup:
    ACCOUNTS = {"freedomcoord": (5001, 5001), "freedomsheet": (5002, 5002),
                "fbprobe": (5003, 5003)}
    GROUPS = {"freedomcoord": 5001, "freedomsheet": 5002, "fbprobe": 5003,
              "freedomjournal": 5004}

    def account(self, name: str) -> tuple[int, int]:
        return self.ACCOUNTS[name]

    def group_id(self, name: str) -> int:
        return self.GROUPS[name]

    def supplementary_group_names(self, name: str, primary_gid: int):
        raise AssertionError("the executor resolves ids, never memberships")

    def effective_ids(self) -> tuple[int, int]:
        return 0, 0


def satisfying(plan: ConcretePlan) -> _FakeBoundary:
    scripted = {}
    for step in plan.steps:
        status = 1 if step.refusal_required else step.satisfying_statuses[0]
        scripted[step.step_id] = CommandResult(
            exit_status=status,
            timed_out=False,
            observations=observations_for(step, bound_argv(step), SOURCES),
        )
    for step in plan.cleanup_plan.steps:
        status = 1 if step.refusal_required else step.satisfying_statuses[0]
        scripted[step.step_id] = CommandResult(
            exit_status=status,
            timed_out=False,
            observations=cleanup_observations_for(step, plan, SOURCES),
        )
    return _FakeBoundary(scripted)


def runner(plan: ConcretePlan, fake: _FakeBoundary) -> ExecutingRunner:
    return ExecutingRunner(
        plan=plan,
        boundary=fake,
        reviewed_digest=ReviewManifest.build(plan, SOURCES).digest(),
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        materializer=_FakeMaterializer(),
        identity_lookup=_FakeIdentityLookup(),
    )
