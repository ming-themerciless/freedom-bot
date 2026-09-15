"""The executing runner, proved across an injected process boundary.

**No test in this file starts a process, and none can.** Every one of them
injects a fake boundary; the real `SubprocessBoundary` is exercised only for the
properties that do not require running anything — that it refuses when it is not
armed, that its environment is fixed, that its timeouts are bounded — and it is
never armed here.

The suite is organised around the four gates and the stop conditions, because
those are what a reviewer is being asked to trust: everything else about this
class is bookkeeping.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tools.phase_5_0_evidence.approved_target import (
    APPROVED_TARGET,
    CONFIRMATION_TOKEN,
)
from tools.phase_5_0_evidence.capture import CapturePolicy
from tools.phase_5_0_evidence.cleanup import CleanupPlan, CleanupStepKind
from tools.phase_5_0_evidence.concrete_plan import (
    ConcretePlan,
    UnresolvedStep,
    build_concrete_plan,
    build_mutations,
)
from tools.phase_5_0_evidence import case_runtime
from tools.phase_5_0_evidence.case_runtime import CASE_PROGRAM_SOURCE
from tools.phase_5_0_evidence.errors import PlanRefused, TargetRefused
from tools.phase_5_0_evidence.execution import boundary as boundary_module
from tools.phase_5_0_evidence.execution.boundary import (
    IdentityAbsent,
    DEFAULT_TIMEOUT_SECONDS,
    MINIMAL_ENVIRONMENT,
    POSTGRES_16_BIN,
    CommandResult,
    RecordingBoundary,
    SubprocessBoundary,
    environment_for,
    timeout_for,
)
from tools.phase_5_0_evidence.execution.cli import build_parser, main, render_plan
from tools.phase_5_0_evidence.execution.materializer import (
    MATERIALIZER_NOT_ARMED,
    MaterializationResult,
)
from tools.phase_5_0_evidence.execution.executor import (
    PERMITTED_RUN_AS,
    REFUSED_EXIT_CODE,
    ExecutingRunner,
    ExecutorRefused,
)
from tools.phase_5_0_evidence.plan import ExecutionPlan, StepRole
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest
from tools.phase_5_0_evidence.targets import DisposableTarget

from tests.phase_5_0_evidence.harness_fixtures import (
    RecordingEffects,
    refusing_effects,
    cleanup_observations_for,
    bound_argv,
    observations_for,
    runnable_plan,
    supply_reviewed_e7_facts,
)

SOURCES = {name: f"# {name}\n".encode("utf-8") for name in COVERED_SOURCES}

#: A stand-in for the reviewed target fact a maintainer supplies before any run.
#:
#: `case_runtime.EXPECTED_INTERPRETER_SHA256` ships **unconfirmed**, and the
#: executor refuses while it is — which is asserted on its own below, against the
#: shipped value. Every other test in this file is about a different gate or a
#: different property, so they are given the fact the way a run would have it.
#: The value is obviously synthetic: nothing here compares it with a real
#: interpreter, because nothing here starts one.
REVIEWED_INTERPRETER_DIGEST = "5" * 64

#: The second reviewed target fact, new in R12. `P-05` reports `interpreter_real`
#: and R12 compares it, so the executor refuses while it is unconfirmed exactly
#: as it does for the digest — which is asserted on its own in `test_executor.py`
#: against the shipped value. It is obviously synthetic: nothing here resolves a
#: real interpreter, because nothing here starts one.
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"


@pytest.fixture(autouse=True)
def _the_reviewed_target_facts_are_supplied(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gates 3 and 4, given the values a run would have.

    Each gate is asserted on its own against the **shipped** value elsewhere;
    every other test in this file is about a different gate or a different
    property, so it is given the facts rather than blocked on them.
    """
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_SHA256", REVIEWED_INTERPRETER_DIGEST
    )
    monkeypatch.setattr(
        case_runtime,
        "EXPECTED_INTERPRETER_REAL_PATH",
        REVIEWED_INTERPRETER_REAL_PATH,
    )
    supply_reviewed_e7_facts(monkeypatch)


@dataclass
class FakeIdentityLookup:
    """The four disposable identities, resolved from a table rather than a host.

    **No test in this file reads a real account.** The executor's default lookup
    is the real one and would consult `pwd`/`grp`; every runner built here is
    given this instead, so the C-5 substitution is exercised against numbers this
    file states and against nothing the machine running the suite happens to have.
    """

    accounts: dict = field(
        default_factory=lambda: {
            "freedomcoord": (5001, 5001),
            "freedomsheet": (5002, 5002),
            "fbprobe": (5003, 5003),
            # `postgres` is **pre-existing**, not disposable. The reviewed
            # restoration `fchown`s the configuration back to it — r6 §2.4 —
            # so the injected NSS boundary has to answer for it. The numbers
            # are this file's, like every other one here.
            "postgres": (900, 900),
        }
    )
    groups: dict = field(
        default_factory=lambda: {
            "freedomcoord": 5001,
            "freedomsheet": 5002,
            "fbprobe": 5003,
            "postgres": 900,
            "freedomjournal": 5004,
        }
    )

    def account(self, name: str) -> tuple[int, int]:
        if name not in self.accounts:
            raise IdentityAbsent(name)
        return self.accounts[name]

    def group_id(self, name: str) -> int:
        if name not in self.groups:
            raise IdentityAbsent(name)
        return self.groups[name]

    def supplementary_group_names(self, name: str, primary_gid: int):  # pragma: no cover
        raise AssertionError("the executor resolves ids, never memberships")

    def effective_ids(self) -> tuple[int, int]:  # pragma: no cover
        return 0, 0



# ---------------------------------------------------------------------------
# A plan the executor will accept: the real one with its conflicts resolved.
#
# The submitted plan carries unresolved conflicts and the executor refuses it,
# which is correct and is asserted below — and it would leave every other
# property of this class untested. So the runnable fixture is the real plan with
# `unresolved` emptied: the same vectors, the same mutations, the same derived
# cleanup, and nothing invented.
# ---------------------------------------------------------------------------


@dataclass
class FakeBoundary:
    """Records every call and answers from a script. Starts nothing.

    Keyed by **`step_id`**, not by argument vector: two steps in the plan share
    a vector on purpose — `getent group freedomjournal` asserts the group is
    absent before provisioning and asserts its membership after — and a fake
    keyed by argv would answer both with whichever was scripted last.
    """

    default_status: int = 0
    scripted: dict[str, CommandResult] = field(default_factory=dict)
    calls: list[tuple[str, str, tuple[str, ...], CapturePolicy, float]] = field(
        default_factory=list
    )

    def run(
        self,
        *,
        step_id,
        argv,
        run_as,
        capture,
        timeout_seconds,
        catalog=None,
        descriptors=(),
    ):
        vector = tuple(argv)
        self.calls.append((step_id, run_as, vector, capture, timeout_seconds))
        if step_id in self.scripted:
            return self.scripted[step_id]
        return CommandResult(exit_status=self.default_status, timed_out=False)


@dataclass
class FakeMaterializer:
    """Applies every reviewed write, and writes nothing.

    It is here for the same reason `FakeBoundary` is: the executor's behaviour
    around a materialization — the capture prerequisite, the responsibility
    ordering, the stop and the cleanup that follows — is what the suite is about,
    and none of it needs a real file. `applied` flips it to the refusing
    behaviour the real materializer has when it is not armed.
    """

    applied: bool = True
    failure: str = MATERIALIZER_NOT_ARMED
    requests: list[tuple[str, str, bytes]] = field(default_factory=list)

    def materialize(self, *, step_id, destination, content, sha256, owner, group, mode):
        self.requests.append((step_id, destination, content))
        if self.applied:
            return MaterializationResult(applied=True)
        return MaterializationResult(applied=False, failure=self.failure)


def satisfying(plan: ConcretePlan) -> FakeBoundary:
    """A boundary that gives every step exactly what the reviewed plan requires.

    Two things now, not one. The exit status the plan says satisfies the step —
    including the `getent` exit 2 and every required refusal — **and**, for the
    two capture policies that carry a semantic expectation, the complete
    observation that contract requires. R12 made the second half load-bearing:
    a `P-05` or `B5-E*` step that exits 0 with no observation is unsatisfied, so
    a boundary that scripted only a status would stop every run at the
    preflight.
    """
    scripted: dict[str, CommandResult] = {}
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
    return FakeBoundary(scripted=scripted)


def runner(plan: ConcretePlan, fake: FakeBoundary, **overrides) -> ExecutingRunner:
    digest = ReviewManifest.build(plan, SOURCES).digest()
    keywords = dict(
        plan=plan,
        boundary=fake,
        reviewed_digest=digest,
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        materializer=FakeMaterializer(),
        identity_lookup=FakeIdentityLookup(),
        effects=RecordingEffects(),
    )
    keywords.update(overrides)
    return ExecutingRunner(**keywords)


# ---------------------------------------------------------------------------
# Gate 1 — the target
# ---------------------------------------------------------------------------


def test_the_executor_refuses_a_plan_whose_target_is_not_the_approved_one() -> None:
    other = DisposableTarget(
        host="oracle-test",
        root_path="/var/lib/fb-evidence-p5-1",
        database_name="fb_evidence_p5_1",
        postgres_socket_directory="/var/run/postgresql",
        confirmed_disposable=True,
        disposability_evidence="a synthetic sibling target nobody confirmed",
        postgres_config_directory="/etc/postgresql/16/main",
    )
    mutations = build_mutations(other)
    plan = ConcretePlan(
        execution_plan=ExecutionPlan(target=other, steps=(), mutations=mutations),
        cleanup_plan=CleanupPlan.for_mutations(other, mutations),
        unresolved=(),
    )
    with pytest.raises(TargetRefused):
        runner(plan, FakeBoundary())


def test_the_executor_refuses_an_unassigned_or_unconfirmed_target() -> None:
    unassigned = DisposableTarget.unassigned()
    plan = ConcretePlan(
        execution_plan=ExecutionPlan(target=unassigned, steps=(), mutations=()),
        cleanup_plan=CleanupPlan(target=unassigned, steps=()),
        unresolved=(),
    )
    with pytest.raises(TargetRefused):
        runner(plan, FakeBoundary())


# ---------------------------------------------------------------------------
# Gate 2 — unresolved conflicts
# ---------------------------------------------------------------------------


def test_the_executor_refuses_a_plan_that_still_carries_an_unresolved_item() -> None:
    """The submitted plan no longer has one, so the gate is proved with one.

    R11 resolves the last of C-2, C-3 and C-5, so `build_concrete_plan()` now
    reports no unresolved item. The gate is unchanged and is still the second
    thing the constructor checks; it is exercised here against a plan carrying a
    single synthetic item rather than against the shipped one.
    """
    real = build_concrete_plan()
    blocked = ConcretePlan(
        execution_plan=real.execution_plan,
        cleanup_plan=real.cleanup_plan,
        unresolved=(
            UnresolvedStep(
                step_ref="B9-synthetic",
                band="identity",
                conflict_id="C-9",
                design_requires="a step this suite invents to exercise the gate",
                why_not_a_vector="it is not a real design step",
                what_would_resolve_it="deleting this test's fixture",
            ),
        ),
    )
    with pytest.raises(ExecutorRefused) as refusal:
        runner(blocked, FakeBoundary())
    assert "unresolved conflicts" in str(refusal.value)
    assert "C-9" in str(refusal.value)


def test_the_executor_refuses_while_the_interpreter_digest_is_unconfirmed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """**Gate 2a — conflict C-2's reviewed target fact.**

    Every syscall-level case runs through the named interpreter, and the
    preflight that establishes it is the reviewed one has nothing to compare
    against until a maintainer states its digest and the independent reviewer
    verifies it on the host. Learning it from the run being judged would make the
    preflight a check against itself, so the executor refuses instead — and the
    shipped value is the sentinel, which this asserts against
    `case_runtime`'s own constant rather than against a copy.
    """
    monkeypatch.setattr(
        case_runtime,
        "EXPECTED_INTERPRETER_SHA256",
        case_runtime.INTERPRETER_DIGEST_UNCONFIRMED,
    )
    plan = runnable_plan()
    with pytest.raises(ExecutorRefused) as refusal:
        runner(plan, FakeBoundary())
    assert "interpreter digest" in str(refusal.value)
    assert case_runtime.INTERPRETER_PATH in str(refusal.value)


def test_the_executor_refuses_while_the_resolved_path_is_unconfirmed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """**Gate 2b — R12's second reviewed target fact.**

    `P-05` reports `interpreter_real`, and R12 requires every key of that
    observation to be compared with an expectation the observation cannot
    supply. A virtual environment's `bin/python` normally resolves outside the
    environment, so there is no derivation that neither refuses the reviewed host
    nor learns the expectation from the run being judged — and the value is
    therefore a stated reviewed fact, unconfirmed in this tree, with the executor
    refusing while it is.
    """
    monkeypatch.setattr(
        case_runtime,
        "EXPECTED_INTERPRETER_REAL_PATH",
        case_runtime.INTERPRETER_REAL_PATH_UNCONFIRMED,
    )
    plan = runnable_plan()
    with pytest.raises(ExecutorRefused) as refusal:
        runner(plan, FakeBoundary())
    assert "resolved interpreter path" in str(refusal.value)


def test_a_reviewed_resolved_path_the_capture_boundary_could_never_report_is_refused() -> None:
    """The fact is checked for the shape `capture`'s `absolute_path` admits.

    A relative path, a `..` segment, an over-long one or one carrying a character
    the boundary strips would be an expectation no observation could ever equal —
    which is a preflight that can only fail, not a preflight that compares.
    """
    for wrong in ("python3.12", "/usr/bin/../bin/python", "", "/usr/bin/py thon", "/" + "a" * 120):
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(case_runtime, "EXPECTED_INTERPRETER_REAL_PATH", wrong)
            assert not case_runtime.interpreter_real_path_confirmed(), wrong
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(case_runtime, "EXPECTED_INTERPRETER_REAL_PATH", "/usr/bin/python3.12")
        assert case_runtime.interpreter_real_path_confirmed()


def test_the_shipped_interpreter_digest_is_unconfirmed() -> None:
    """Asserted against the module, not against a copy of the value.

    If a maintainer supplies the fact, this test fails and has to be deleted
    deliberately — which is the point: the change is a decision, and it changes
    the review-manifest digest, so it is re-reviewed rather than absorbed.

    It reads the **source text** rather than the imported value, because the
    autouse fixture above supplies the fact for every other test in this file
    and reloading the module mid-suite would rebind constants other modules
    already hold.
    """
    source = Path(case_runtime.__file__).read_text(encoding="utf-8")
    assert (
        "EXPECTED_INTERPRETER_SHA256 = INTERPRETER_DIGEST_UNCONFIRMED" in source
    ), (
        "case_runtime.py ships the sentinel. Supplying the real digest is a "
        "maintainer decision that changes a covered source, changes the "
        "review-manifest digest and requires re-review — so it deletes this "
        "assertion deliberately rather than passing quietly."
    )


# ---------------------------------------------------------------------------
# Gate 3 — the confirmation token
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "token",
    [
        "",
        "   ",
        "yes",
        "oracle-test",
        CONFIRMATION_TOKEN[:-1],
        CONFIRMATION_TOKEN + "0",
        CONFIRMATION_TOKEN.upper(),
    ],
)
def test_execution_requires_the_exact_confirmation_token(token: str) -> None:
    plan = runnable_plan()
    with pytest.raises(ExecutorRefused) as refusal:
        runner(plan, satisfying(plan), confirmation_token=token)
    assert "confirmation token" in str(refusal.value)


def test_the_exact_token_is_accepted() -> None:
    plan = runnable_plan()
    assert runner(plan, satisfying(plan)) is not None


# ---------------------------------------------------------------------------
# Gate 4 — the reviewer's digest
# ---------------------------------------------------------------------------


def test_execution_refuses_when_no_reviewed_digest_is_supplied() -> None:
    plan = runnable_plan()
    with pytest.raises(ExecutorRefused) as refusal:
        runner(plan, satisfying(plan), reviewed_digest="")
    assert "reviewer's input" in str(refusal.value)


def test_execution_refuses_an_unreviewed_plan_digest() -> None:
    plan = runnable_plan()
    with pytest.raises(ExecutorRefused) as refusal:
        runner(plan, satisfying(plan), reviewed_digest="0" * 64)
    assert "does not match the plan in this tree" in str(refusal.value)


def test_a_changed_source_file_invalidates_a_previously_reviewed_digest() -> None:
    """The tree cannot approve itself.

    The reviewed digest is the value from *before* the edit; the executor
    recomputes from the live sources and refuses. That is the whole mechanism:
    the expectation comes from outside, and nothing in the tree updates it.
    """
    plan = runnable_plan()
    approved = ReviewManifest.build(plan, SOURCES).digest()
    edited = dict(SOURCES)
    edited[COVERED_SOURCES[0]] += b"# an edit made after the review\n"
    with pytest.raises(ExecutorRefused):
        runner(plan, satisfying(plan), reviewed_digest=approved, source_bytes=edited)


def test_the_executor_neither_reads_nor_writes_an_expected_digest() -> None:
    """Source-level, because the property is about what the code can do.

    The executor takes the expected value as a constructor argument. If it read
    one from a file, editing the generator would edit the expectation in the same
    commit.
    """
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2]
        / "tools"
        / "phase_5_0_evidence"
        / "execution"
        / "executor.py"
    ).read_text(encoding="utf-8")
    for forbidden in ("open(", "read_text", "read_bytes", "write_text", "write_bytes"):
        assert forbidden not in source


# ---------------------------------------------------------------------------
# The dry-run path
# ---------------------------------------------------------------------------


def test_the_default_cli_invocation_executes_nothing(capsys) -> None:
    exit_code = main([])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert output.startswith("DRY RUN — nothing was executed.")
    # **R16.** What R13's EH-R13-4 required was that the dry run report what the
    # plan cannot produce rather than reporting itself complete. C-8 is closed —
    # the creation-ownership line is the fact that replaced the blocked
    # filesystem baseline — and **C-7 is not**: EH-R16-4 restored Band 7's three
    # producers to the unresolved column, so `executable` is `False` and the dry
    # run says which conflict and how many contracts resolve nothing.
    assert "executable            : False" in output
    assert "unresolved conflicts  : 3 (C-7)" in output
    assert "blocked baselines     : 0 mutations proved absent by nothing" in output
    assert "creation ownership    : 1 step(s) owning 29 mutations" in output
    assert "external contracts    : 3 documented input contract(s)" in output
    assert "of which 0 have a reviewed producer artifact" in output
    # **And executable is still not permission.** The dry run names every
    # reviewed target fact that refuses the executor before a command starts.
    # This module's autouse fixture supplies them, so the line reads `none`
    # here; `test_root_identity.py` asserts the shipped, unsupplied values
    # against the executor's own refusal.
    assert "unconfirmed facts     :" in output
    assert "each one refuses the executor before any command starts" in output
    # Nothing was started, nothing was written, and no account database was
    # consulted.
    assert "binding sites declared" in output
    assert "no account database was read" in output


def test_the_cli_defaults_to_not_executing() -> None:
    args = build_parser().parse_args([])
    assert args.execute is False
    assert args.confirm_target == ""
    assert args.reviewed_digest == ""


def test_the_cli_refuses_execute_without_the_token_or_the_digest(capsys) -> None:
    assert main(["--execute"]) == REFUSED_EXIT_CODE
    assert "REFUSED" in capsys.readouterr().err
    assert main(["--execute", "--confirm-target", CONFIRMATION_TOKEN]) == REFUSED_EXIT_CODE
    assert "REFUSED" in capsys.readouterr().err


def test_the_recording_boundary_starts_nothing() -> None:
    recording = RecordingBoundary()
    result = recording.run(
        step_id="R-01",
        argv=("/usr/bin/id",),
        run_as="root",
        capture=CapturePolicy.EXIT_STATUS_ONLY,
        timeout_seconds=1.0,
    )
    assert recording.calls == [("root", ("/usr/bin/id",))]
    assert result.observations == ()


def test_the_real_boundary_is_unarmed_by_default_and_refuses_to_start_anything() -> None:
    result = SubprocessBoundary().run(
        step_id="R-01",
        argv=("/usr/bin/id",),
        run_as="root",
        capture=CapturePolicy.EXIT_STATUS_ONLY,
        timeout_seconds=5.0,
    )
    assert result.launch_failure == "boundary-not-armed"
    assert result.exit_status == -1


# ---------------------------------------------------------------------------
# Identity, environment and timeouts
# ---------------------------------------------------------------------------


def test_every_step_runs_as_one_of_the_closed_identity_set() -> None:
    plan = runnable_plan()
    for step in plan.steps:
        assert step.run_as in PERMITTED_RUN_AS, step.step_id
    for step in plan.cleanup_plan.steps:
        assert step.run_as in PERMITTED_RUN_AS, step.step_id
    assert "" not in PERMITTED_RUN_AS


def test_an_identity_cannot_be_blank_and_cannot_default() -> None:
    """Two different refusals, and both are needed.

    A **blank** identity is refused where a step is constructed, so no step with
    one exists to reach the executor. An **unknown** one is refused immediately
    before execution, because a name that is a plausible account is exactly the
    kind that survives review. Neither falls back to `root`, and `root` is not a
    default — it is a member of the closed set that a step has to name.
    """
    import dataclasses

    plan = runnable_plan()
    live = runner(plan, satisfying(plan))
    original = plan.steps[0]

    for blank in ("", "   "):
        with pytest.raises(PlanRefused):
            dataclasses.replace(original, run_as=blank)

    for unknown in ("nobody", "mallory", "Root", "postgres-16"):
        refusal = live._revalidate(dataclasses.replace(original, run_as=unknown))
        assert "is not one of the identities" in refusal
        assert "no default" in refusal

    assert live._revalidate(original) == ""


def test_an_identity_transition_is_not_composed_into_the_argument_vector() -> None:
    """`setpriv`, `sudo` and `su` are absent from every generated vector.

    The identity is honoured by the boundary's own `user=` parameter, so the
    vector that was reviewed is the vector that is executed.
    """
    plan = runnable_plan()
    for step in list(plan.steps) + list(plan.cleanup_plan.steps):
        # A descriptor-bound effect names no executable at all, which is the
        # same property one step further: there is no vector for a privilege
        # helper to be composed into.
        assert step.argv[:1] not in (
            ("/usr/bin/setpriv",),
            ("/usr/bin/sudo",),
            ("/usr/bin/su",),
        )


def test_the_environment_is_minimal_and_fixed() -> None:
    env = environment_for("/usr/bin/id")
    assert env == dict(MINIMAL_ENVIRONMENT)
    assert "HOME" not in env and "PGPASSWORD" not in env and "PYTHONPATH" not in env


def test_psql_gets_the_explicit_postgresql_16_path() -> None:
    env = environment_for("/usr/bin/psql")
    assert env["PATH"].startswith(POSTGRES_16_BIN + ":")
    assert env["PGCONNECT_TIMEOUT"] == "10"


def test_every_step_has_a_bounded_non_zero_timeout() -> None:
    """Every step that starts a process. An effect starts none.

    A descriptor-bound effect is a syscall the executor issues in its own
    process, so there is no child to kill and no timeout to bound. What bounds
    it instead is that it refuses before issuing: an unarmed issuer, an
    unrecorded identity, an absent object, an unequal identity and an
    unestablished quiescence each refuse, and none of them blocks.
    """
    plan = runnable_plan()
    for step in list(plan.steps) + list(plan.cleanup_plan.steps):
        if step.is_effect:
            assert step.argv == ()
            continue
        seconds = timeout_for(step.argv[0])
        assert 0 < seconds <= 120.0, step.step_id
    assert timeout_for("/usr/bin/id") == DEFAULT_TIMEOUT_SECONDS


def test_a_timeout_stops_the_run() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    fake.scripted[plan.steps[2].step_id] = CommandResult(exit_status=-1, timed_out=True)

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == plan.steps[2].step_id
    assert "bounded timeout" in outcome.stop_reason
    assert outcome.steps[-1].timed_out is True
    assert len(outcome.steps) == 3


# ---------------------------------------------------------------------------
# Stopping, and what a stop protects
# ---------------------------------------------------------------------------


def test_a_completed_run_reaches_s_c_and_admits_an_artifact() -> None:
    plan = runnable_plan()
    outcome = runner(plan, satisfying(plan)).execute()
    assert outcome.completed
    assert outcome.stopped_at == ""
    assert outcome.cleanup.state == "S-C"
    assert outcome.exit_code == 0
    assert outcome.artifact_admissible is True


def test_a_failed_prerequisite_stops_before_any_mutation() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    prerequisite = next(
        step for step in plan.steps if step.role is StepRole.PREREQUISITE
    )
    fake.scripted[prerequisite.step_id] = CommandResult(exit_status=7, timed_out=False)

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == prerequisite.step_id
    assert outcome.mutations_reached == ()
    assert outcome.cleanup_steps == ()


def test_a_positive_control_failure_prevents_dependent_interpretation() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    control = next(
        step
        for step in plan.steps
        if step.role is StepRole.CONTROL and step.band == "postgresql"
    )
    fake.scripted[control.step_id] = CommandResult(exit_status=2, timed_out=False)

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == control.step_id
    executed = {step.step_id for step in outcome.steps}
    dependents = {
        step.step_id
        for step in plan.steps
        if step.role is StepRole.DEPENDENT and step.band == "postgresql"
    }
    assert dependents and not (dependents & executed)
    assert outcome.artifact_admissible is False


def test_a_refusal_that_did_not_refuse_stops_the_run() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    denial = next(step for step in plan.steps if step.refusal_required)
    fake.scripted[denial.step_id] = CommandResult(exit_status=0, timed_out=False)

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == denial.step_id
    assert "did not deny" in outcome.stop_reason


def test_an_unexpected_exit_status_is_not_quietly_accepted() -> None:
    """The JNL-52 precondition is satisfied by `getent`'s exit **2**, and exit 0
    there means the group already exists — which is a stop, not a pass."""
    plan = runnable_plan()
    precondition = next(step for step in plan.steps if step.satisfying_statuses == (2,))
    fake = satisfying(plan)
    fake.scripted[precondition.step_id] = CommandResult(exit_status=0, timed_out=False)

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == precondition.step_id


# ---------------------------------------------------------------------------
# Cleanup after every mutation prefix
# ---------------------------------------------------------------------------


def _mutation_prefixes(plan: ConcretePlan) -> list[int]:
    return [
        index for index, step in enumerate(plan.steps) if step.mutation_ids
    ]


def test_interruption_after_each_mutation_prefix_still_runs_the_whole_derived_cleanup() -> None:
    """Every prefix, not a sample.

    The derived cleanup is a function of the **declared** mutations, not of the
    prefix that ran, and every reversal is non-destructive when its object is
    absent — so the correct behaviour after any interruption is the same complete
    cleanup. Asserting it for each prefix is what makes that a property rather
    than a claim.
    """
    plan = runnable_plan()
    for index in _mutation_prefixes(plan):
        step = plan.steps[index]
        fake = satisfying(plan)
        overrides = {}
        if step.is_effect:
            # An effect starts no process, so it is failed by refusing it at the
            # issuer rather than by scripting an exit status at the boundary.
            overrides["effects"] = refusing_effects(step)
        else:
            fake.scripted[step.step_id] = CommandResult(
                exit_status=99, timed_out=False
            )
        outcome = runner(plan, fake, **overrides).execute()

        assert outcome.stopped_at == plan.steps[index].step_id
        # **R13, EH-R13-1.** The *applicable* cleanup, not the whole declared
        # one. A prefix that reached three mutations is entitled to reverse
        # those three; reversing the rest would delete objects it never made and
        # may never have proved absent, which is the Blocking finding. Every
        # step outside the applicable set is still accounted for — by a skip
        # with a fixed reason — so nothing is quietly omitted.
        applicable = plan.cleanup_plan.applicable(
            attempted=outcome.mutations_reached,
            owned=_owned_by(plan, outcome),
        )
        assert [step.step_id for step in outcome.cleanup_steps] == [
            step.step_id for step in applicable.steps
        ]
        assert {item.step_id for item in outcome.cleanup_skipped} | {
            step.step_id for step in applicable.steps
        } == {step.step_id for step in plan.cleanup_plan.steps}
        owned = set(_owned_by(plan, outcome))
        for mutation_id in outcome.mutations_reached:
            if mutation_id not in owned:
                # **R16, conflict C-8.** The interruption fell on the exclusive
                # creation itself. The mutation was attempted — responsibility
                # begins before the boundary is called — and nothing owns it,
                # because `mkdir(2)` did not return. That is deliberately not a
                # reversal: a directory may exist and this run cannot identify
                # it, so the path is reported as residue with the named operator
                # recovery and is never deleted.
                assert mutation_id == f"directory:{plan.target.root_path}"
                assert plan.target.root_path in outcome.cleanup.residue
                assert outcome.cleanup.state == "S-B"
                continue
            assert any(
                mutation_id in step.mutation_ids for step in applicable.steps
            ), mutation_id


def _owned_by(plan, outcome) -> list[str]:
    """The ownership a run established, recomputed from its own step outcomes.

    **R13, EH-R13-1.** Cleanup applies to a mutation only when a baseline step
    proved its subject absent before anything changed, so a test that asks what
    cleanup should have done has to know what the run proved.
    """
    by_id = {step.step_id: step for step in plan.steps}
    owned: list[str] = []
    for step_outcome in outcome.steps:
        step = by_id.get(step_outcome.step_id)
        if step is not None and step_outcome.satisfied:
            owned.extend(step.establishes_ownership_of)
            owned.extend(step.establishes_ownership_by_creation)
            owned.extend(step.establishes_ownership_of_contained)
    return owned


def test_a_run_that_reached_no_mutation_runs_no_cleanup() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    fake.scripted[plan.steps[0].step_id] = CommandResult(exit_status=42, timed_out=False)
    outcome = runner(plan, fake).execute()
    assert outcome.mutations_reached == ()
    assert outcome.cleanup_steps == ()
    assert outcome.cleanup.state == "S-A"


def test_cleanup_restores_before_reloading_and_reloads_before_verifying() -> None:
    plan = runnable_plan()
    outcome = runner(plan, satisfying(plan)).execute()
    kinds = [
        next(
            step.kind
            for step in plan.cleanup_plan.steps
            if step.step_id == executed.step_id
        )
        for executed in outcome.cleanup_steps
    ]
    reload_at = kinds.index(CleanupStepKind.RELOAD)
    assert all(index < reload_at for index, kind in enumerate(kinds) if kind is CleanupStepKind.RESTORE)
    assert all(index > reload_at for index, kind in enumerate(kinds) if kind is CleanupStepKind.VERIFY)
    last_verify = max(
        index for index, kind in enumerate(kinds) if kind is CleanupStepKind.VERIFY
    )
    psql_reversals = [
        index
        for index, executed in enumerate(outcome.cleanup_steps)
        if executed.argv[:1] == ("/usr/bin/psql",)
        and kinds[index] is CleanupStepKind.REVERSAL
    ]
    assert psql_reversals and min(psql_reversals) > last_verify


def test_an_unrestored_configuration_file_is_s_b_and_names_the_risk() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    restore = plan.cleanup_plan.restore_steps[0]
    # **r6 §2.4.** The restore is a descriptor-bound effect since r6 §6.4
    # retired `install`, so it is failed at the issuer rather than scripted.
    outcome = runner(plan, fake, effects=refusing_effects(restore)).execute()

    assert outcome.cleanup.state == "S-B"
    assert outcome.exit_code == 3
    assert any("was not restored" in risk for risk in outcome.cleanup.configuration_risk)
    assert outcome.artifact_admissible is False


def test_a_proof_that_succeeded_means_the_mapping_may_still_be_effective() -> None:
    """The post-reload proof is satisfied by being **refused**. Exit 0 there
    means the temporary mapping is still in force, which is residue with no
    path."""
    plan = runnable_plan()
    fake = satisfying(plan)
    proof = next(
        step for step in plan.cleanup_plan.verification_steps if step.refusal_required
    )
    fake.scripted[proof.step_id] = CommandResult(exit_status=0, timed_out=False)

    outcome = runner(plan, fake).execute()

    assert outcome.cleanup.state == "S-B"
    assert any(
        "was not observed to be refused" in risk
        for risk in outcome.cleanup.configuration_risk
    )


def test_failed_cleanup_blocks_a_rerun_rather_than_retrying_it() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    reversal = next(
        step
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVERSAL
        and not step.is_effect
        and step.removes.startswith("/")
    )
    fake.scripted[reversal.step_id] = CommandResult(exit_status=1, timed_out=False)

    live = runner(plan, fake)
    first = live.execute()
    assert first.cleanup.state == "S-B"
    assert reversal.removes in first.cleanup.residue

    with pytest.raises(ExecutorRefused) as refusal:
        live.execute()
    assert "refuses while it exists and does not clean it" in str(refusal.value)


def test_cleanup_is_never_retried_within_a_run() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    reversal = plan.cleanup_plan.steps[-1]
    fake.scripted[reversal.step_id] = CommandResult(exit_status=1, timed_out=False)

    runner(plan, fake).execute()

    attempts = [call for call in fake.calls if call[0] == reversal.step_id]
    assert len(attempts) == 1


# ---------------------------------------------------------------------------
# Materializations — conflict C-4
# ---------------------------------------------------------------------------


def test_a_materialization_is_handed_exactly_the_reviewed_bytes() -> None:
    plan = runnable_plan()
    fake_materializer = FakeMaterializer()
    outcome = runner(
        plan, satisfying(plan), materializer=fake_materializer
    ).execute()

    assert outcome.completed
    assert [request[0] for request in fake_materializer.requests] == [
        item.step_id for item in plan.materializations
    ]
    for (step_id, destination, content), item in zip(
        fake_materializer.requests, plan.materializations
    ):
        assert step_id == item.step_id
        assert destination == item.destination
        assert content == item.file.content


def test_a_materialization_runs_immediately_after_the_step_it_names() -> None:
    plan = runnable_plan()
    outcome = runner(plan, satisfying(plan)).execute()
    order = [step.step_id for step in outcome.steps]
    for item in plan.materializations:
        assert order.index(item.after_step_id) < order.index(item.step_id)
        assert order.index(item.capture_step_id) < order.index(item.step_id)
    reload_step = next(
        step for step in plan.steps if "SELECT pg_reload_conf()" in step.argv
    )
    for item in plan.materializations:
        assert order.index(item.step_id) < order.index(reload_step.step_id)


def test_a_materialization_records_no_argument_vector() -> None:
    """It is not a command, and its outcome does not pretend to be one."""
    plan = runnable_plan()
    outcome = runner(plan, satisfying(plan)).execute()
    by_id = {step.step_id: step for step in outcome.steps}
    for item in plan.materializations:
        recorded = by_id[item.step_id]
        assert recorded.argv == ()
        assert recorded.observations == ()
        assert recorded.launch_failure == ""
        assert recorded.satisfied is True
    # And the process boundary was never asked to run one.
    materialization_ids = {item.step_id for item in plan.materializations}
    assert not (materialization_ids & {call[0] for call in fake_calls(plan)})


def fake_calls(plan: ConcretePlan) -> list:
    fake = satisfying(plan)
    runner(plan, fake).execute()
    return fake.calls


def test_an_unapplied_materialization_stops_the_run_and_cleans_up() -> None:
    """Its mutation is recorded **before** the write is attempted, so a
    materialization whose outcome is a refusal still gets the whole derived
    restore, reload and proof."""
    plan = runnable_plan()
    fake = satisfying(plan)
    first = plan.materializations[0]

    outcome = runner(
        plan, fake, materializer=FakeMaterializer(applied=False)
    ).execute()

    assert outcome.stopped_at == first.step_id
    assert set(first.mutation_ids) <= set(outcome.mutations_reached)
    applicable = plan.cleanup_plan.applicable(
        attempted=outcome.mutations_reached, owned=_owned_by(plan, outcome)
    )
    assert [step.step_id for step in outcome.cleanup_steps] == [
        step.step_id for step in applicable.steps
    ]
    # The materialization's own mutation is among the ones reversed: its
    # responsibility began before the write was attempted.
    reversed_ids = {
        mutation_id
        for step in applicable.steps
        for mutation_id in step.mutation_ids
    }
    assert set(first.mutation_ids) <= reversed_ids
    assert outcome.artifact_admissible is False
    recorded = next(step for step in outcome.steps if step.step_id == first.step_id)
    assert recorded.launch_failure == MATERIALIZER_NOT_ARMED
    assert recorded.satisfied is False


def test_an_executor_assembled_without_a_materializer_refuses_to_write() -> None:
    """The default is the recording implementation, so the failure mode of
    forgetting one is a refused step and a clean host — never a silent write."""
    plan = runnable_plan()
    live = ExecutingRunner(
        plan=plan,
        boundary=satisfying(plan),
        reviewed_digest=ReviewManifest.build(plan, SOURCES).digest(),
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        identity_lookup=FakeIdentityLookup(),
        effects=RecordingEffects(),
    )
    outcome = live.execute()
    assert outcome.stopped_at == plan.materializations[0].step_id
    assert outcome.completed is False


def test_a_materialization_refuses_when_its_capture_step_was_not_satisfied() -> None:
    """The one check the plan cannot make.

    Whether a step *did* what the plan says is a fact about a run, so the
    executor holds it. Without the byte-exact pre-change capture there is
    nothing for the reviewed cleanup to reinstall, and the configuration is not
    changed at all.
    """
    from tools.phase_5_0_evidence.execution import executor as executor_module

    plan = runnable_plan()
    live = runner(plan, satisfying(plan))
    item = plan.materializations[0]

    empty = executor_module._RunState()
    refusal = live._revalidate_materialization(item, empty)
    assert item.capture_step_id in refusal
    assert "nothing to reinstall" in refusal

    # **r6 §§2.3.3 and 1.4.4 M1, C-P5.0-LAB-I-R1.** A satisfied capture step is
    # necessary and **not sufficient**: M1's own precondition is that the
    # independent publication reported every barrier crossed, and that is
    # re-checked here rather than inferred from the step's satisfaction.
    satisfied = executor_module._RunState()
    satisfied.satisfied_steps.add(item.capture_step_id)
    assert "recovery basis" in live._revalidate_materialization(item, satisfied)

    live._publication = _published_basis()
    assert live._revalidate_materialization(item, satisfied) == ""


def test_a_materialization_whose_destination_drifted_is_refused_twice_over() -> None:
    """Once where the step is built, and again immediately before the write.

    Swapping one reviewed file's destination for the other's cannot even be
    constructed — the content and the destination have to name the same file —
    and a destination that is a valid configuration path for some *other* target
    is refused by the executor's revalidation against this plan's target.
    """
    import dataclasses

    plan = runnable_plan()
    live = runner(plan, satisfying(plan))
    item = plan.materializations[0]

    with pytest.raises(PlanRefused) as swapped:
        dataclasses.replace(
            item, destination="/etc/postgresql/16/main/pg_ident.conf"
        )
    assert "name the same file" in str(swapped.value)

    elsewhere = dataclasses.replace(
        item, destination="/etc/postgresql/17/other/pg_hba.conf"
    )
    state = executor_module_state(item.capture_step_id)
    refusal = live._revalidate_materialization(elsewhere, state)
    assert "configuration path" in refusal
    live._publication = _published_basis()
    assert live._revalidate_materialization(item, state) == ""


def _published_basis():
    """A publication reporting every §2.3.3 barrier crossed.

    Built here rather than taken from a store, because these two tests are about
    the materialization's revalidation and not about the store — and because a
    test in this suite may not hold a real recovery store.
    """
    from tools.phase_5_0_evidence.execution.recovery_store import (
        BARRIER_ORDER,
        StorePublication,
    )

    return StorePublication(
        published=True,
        mutation_permitted=True,
        barriers_crossed=BARRIER_ORDER,
        run_directory_name="RUN-TEST",
    )


def executor_module_state(capture_step_id: str):
    from tools.phase_5_0_evidence.execution import executor as executor_module

    state = executor_module._RunState()
    state.satisfied_steps.add(capture_step_id)
    return state


# ---------------------------------------------------------------------------
# What is recorded
# ---------------------------------------------------------------------------


def test_only_sanitized_observations_are_recorded() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    first = plan.steps[0]
    fake.scripted[first.step_id] = CommandResult(
        exit_status=first.satisfying_statuses[0],
        timed_out=False,
        observations=(("uid", "0"), ("gid", "0")),
        stderr_present=True,
    )

    outcome = runner(plan, fake).execute()

    recorded = outcome.steps[0]
    assert recorded.observations == (("uid", "0"), ("gid", "0"))
    assert recorded.stderr_present is True
    assert not hasattr(recorded, "stdout")
    assert not hasattr(recorded, "stderr")


def test_a_command_result_has_no_field_that_could_hold_raw_output() -> None:
    fields = set(CommandResult.__dataclass_fields__)
    assert fields == {
        "exit_status",
        "timed_out",
        "observations",
        "stderr_present",
        "launch_failure",
    }


def test_cleanup_steps_record_the_exit_status_and_nothing_else() -> None:
    """A step whose purpose is a side effect has no observation to make.

    **R16, conflict C-8** makes exactly one cleanup step an exception, and the
    exception is the rule's own reason: the revalidation removes nothing and
    exists *for* its observation — the created root's device and inode, compared
    with what the creation reported before the `rmdir` it guards may run. Every
    other cleanup step still records its exit status and nothing else, and
    `CleanupStep.__post_init__` refuses any other kind that tries to.
    """
    plan = runnable_plan()
    fake = satisfying(plan)
    runner(plan, fake).execute()
    by_id = {step.step_id: step for step in plan.cleanup_plan.steps}
    cleanup_calls = [call for call in fake.calls if call[0] in by_id]
    assert cleanup_calls
    for call in cleanup_calls:
        step = by_id[call[0]]
        if step.kind is CleanupStepKind.REVALIDATE:
            assert call[3] is CapturePolicy.CASE_RESULT
        else:
            assert call[3] is CapturePolicy.EXIT_STATUS_ONLY, step.step_id
    assert sum(1 for call in cleanup_calls if call[3] is CapturePolicy.CASE_RESULT) == 1


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_the_rendered_plan_is_deterministic_and_carries_the_banner() -> None:
    plan = build_concrete_plan()
    manifest = ReviewManifest.build(plan, SOURCES)
    digest = manifest.digest()
    source_digest = manifest.digest_for(CASE_PROGRAM_SOURCE)
    first = render_plan(plan, digest, source_digest)
    second = render_plan(build_concrete_plan(), digest, source_digest)
    assert first == second
    assert first.startswith("# NOT EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED")
    assert first.rstrip().endswith("# NOT EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED")
    assert digest in first
    for step in plan.steps:
        assert " ".join(step.argv) in first
    for step in plan.cleanup_plan.steps:
        assert " ".join(step.argv) in first
    for item in plan.unresolved:
        assert item.step_ref in first


def test_the_module_exposes_no_armed_boundary_at_import_time() -> None:
    assert boundary_module.SubprocessBoundary().armed is False
