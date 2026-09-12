"""EH-R5-2: cleanup is guaranteed once a mutation may have been reached.

Every test here injects a boundary that **raises** — at a controlled call, on a
controlled step — and asserts what the executor did about it. Nothing starts a
process, and the real boundary is never armed anywhere in this file.

The property under test is the one the class promised and did not have: a
mutation-bearing run that raises, times out, is refused or is interrupted must
still clean up what it may have created, exactly once, without either fact — the
execution failure and the cleanup result — standing in for the other.
"""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

import pytest

from tools.phase_5_0_evidence.approved_target import CONFIRMATION_TOKEN
from tools.phase_5_0_evidence.capture import CapturePolicy
from tools.phase_5_0_evidence.cleanup import (
    RECOVERY_INPUT_RETAINED,
    CleanupStepKind,
)
from tools.phase_5_0_evidence.concrete_plan import ConcretePlan, build_concrete_plan
from tools.phase_5_0_evidence import case_runtime
from tools.phase_5_0_evidence.errors import ObservationRefused
from tools.phase_5_0_evidence.execution import executor as executor_module
from tools.phase_5_0_evidence.execution.boundary import (
    IdentityAbsent,
    LAUNCH_BOUNDARY_FAILURE,
    LAUNCH_VALIDATION_REFUSED,
    CommandResult,
)
from tools.phase_5_0_evidence.execution.materializer import (
    MATERIALIZER_NOT_ARMED,
    MaterializationResult,
)
from tools.phase_5_0_evidence.execution.executor import (
    BEFORE_FIRST_STEP,
    OPERATOR_INTERRUPTION,
    UNEXPECTED_EXECUTION_FAILURE,
    ExecutingRunner,
    ExecutorRefused,
)
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.harness_fixtures import (
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
        }
    )
    groups: dict = field(
        default_factory=lambda: {
            "freedomcoord": 5001,
            "freedomsheet": 5002,
            "fbprobe": 5003,
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



@dataclass
class RaisingBoundary:
    """Answers from a script, and raises where it is told to.

    `raise_on` maps a `step_id` to the exception to raise instead of returning.
    `raise_after` raises once the given number of calls have been made, which is
    how a failure part-way through the cleanup plan is expressed.
    """

    scripted: dict[str, CommandResult] = field(default_factory=dict)
    raise_on: dict[str, BaseException] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)

    def run(self, *, step_id, argv, run_as, capture, timeout_seconds, catalog=None):
        self.calls.append(step_id)
        if step_id in self.raise_on:
            raise self.raise_on[step_id]
        if step_id in self.scripted:
            return self.scripted[step_id]
        return CommandResult(exit_status=0, timed_out=False)


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


def satisfying(plan: ConcretePlan) -> RaisingBoundary:
    """Every step's satisfying exit status, and — R12 — the complete observation
    the two contract-bearing capture policies require. A step that exits as the
    plan says and observes nothing is not satisfied."""
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
    return RaisingBoundary(scripted=scripted)


def runner(plan: ConcretePlan, fake: RaisingBoundary, **overrides) -> ExecutingRunner:
    digest = ReviewManifest.build(plan, SOURCES).digest()
    keywords = dict(
        plan=plan,
        boundary=fake,
        reviewed_digest=digest,
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        materializer=FakeMaterializer(),
        identity_lookup=FakeIdentityLookup(),
    )
    keywords.update(overrides)
    return ExecutingRunner(**keywords)


def first_mutation_step_index(plan: ConcretePlan) -> int:
    return next(
        index for index, step in enumerate(plan.steps) if step.is_mutation_bearing
    )


def representative_mutation_steps(plan: ConcretePlan) -> dict[str, str]:
    """One step id per declared mutation **kind**, the earliest of each.

    Parametrising over the kinds rather than over a sample is what makes the
    claim *"every mutation class"* rather than *"the ones somebody picked"*.
    """
    kind_of = {m.mutation_id: m.kind.value for m in plan.mutations}
    representative: dict[str, str] = {}
    for step in plan.steps:
        for mutation_id in step.mutation_ids:
            representative.setdefault(kind_of[mutation_id], step.step_id)
    return representative


PLAN = runnable_plan()
MUTATION_KINDS = representative_mutation_steps(PLAN)


def assert_applicable_cleanup_ran_once(outcome, plan: ConcretePlan, fake) -> None:
    """Every cleanup step this run was **entitled** to run, run exactly once.

    **R13, EH-R13-1.** The previous form of this helper asserted that the whole
    declared cleanup ran, which is the Blocking finding stated as a passing test:
    a run that stopped on its second `groupadd` was *required* by the suite to go
    on and delete three groups it had never reached and to drop a database no
    step had created. What is asserted now is that the derived, applicable
    cleanup ran once and completely, and — separately and just as importantly —
    that every step outside it was **skipped with a reason** rather than
    silently omitted.
    """
    applicable = plan.cleanup_plan.applicable(
        attempted=outcome.mutations_reached,
        owned=_owned_by(outcome),
        withdrawn=_withdrawn_by(outcome, plan),
    )
    expected = [step.step_id for step in applicable.steps]
    assert [step.step_id for step in outcome.cleanup_steps] == expected
    # **R13, EH-R13-2.** A step that would delete a recovery input is *retained*
    # rather than run when the restoration it serves was not proved complete. It
    # is still in the applicable set and still in the recorded outcome — with the
    # fixed retention reason — and it is the one kind of applicable step that
    # must **not** reach the boundary.
    retained = {
        step.step_id
        for step in outcome.cleanup_steps
        if step.stop_reason == RECOVERY_INPUT_RETAINED
    }
    for step_id in expected:
        assert fake.calls.count(step_id) == (0 if step_id in retained else 1), step_id
    # Nothing outside the applicable set was called at all, and everything
    # outside it is accounted for.
    skipped = {item.step_id for item in outcome.cleanup_skipped}
    assert skipped | set(expected) == {
        step.step_id for step in plan.cleanup_plan.steps
    }
    for step_id in skipped:
        assert fake.calls.count(step_id) == 0, step_id


def _owned_by(outcome) -> list[str]:
    """The ownership a run established, recomputed from its own step outcomes.

    **R16, conflict C-8.** Two routes now, and both are read from the step: a
    baseline that observed its subjects absent before anything changed, and a
    creation that was satisfied — which means `mkdir(2)` returned, so nothing was
    at that path and nothing was under it.
    """
    owned: list[str] = []
    by_id = {step.step_id: step for step in PLAN.steps}
    for step_outcome in outcome.steps:
        if not step_outcome.satisfied:
            continue
        step = by_id.get(step_outcome.step_id)
        if step is not None:
            owned.extend(step.establishes_ownership_of)
            owned.extend(step.establishes_ownership_by_creation)
            owned.extend(step.establishes_ownership_of_contained)
    return owned


def _withdrawn_by(outcome, plan: ConcretePlan) -> list[str]:
    by_id = {step.step_id: step for step in plan.steps}
    withdrawn: list[str] = []
    for step_outcome in outcome.steps:
        step = by_id.get(step_outcome.step_id)
        if (
            step is not None
            and not step_outcome.satisfied
            and step.reports_preexisting(step_outcome.exit_status)
        ):
            withdrawn.extend(step.mutation_ids)
    return withdrawn


# ---------------------------------------------------------------------------
# Before the first mutation, nothing destructive happens
# ---------------------------------------------------------------------------


def test_an_exception_before_the_first_mutation_runs_no_destructive_cleanup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The exception is raised while the first mutation-bearing step is being
    revalidated — before the executor has committed to invoking it — so nothing
    may have been created and the derived cleanup does not run."""
    plan = runnable_plan()
    fake = satisfying(plan)
    target_index = first_mutation_step_index(plan)
    real_timeout_for = executor_module.timeout_for
    calls = {"n": 0}

    def counted(executable: str) -> float:
        # Two calls per step: one in the revalidation, one at the boundary
        # invocation. `2 * target_index + 1` is therefore the revalidation of
        # the first mutation-bearing step.
        calls["n"] += 1
        if calls["n"] == 2 * target_index + 1:
            raise OSError("a failure while the step was being revalidated")
        return real_timeout_for(executable)

    monkeypatch.setattr(executor_module, "timeout_for", counted)
    outcome = runner(plan, fake).execute()

    assert outcome.mutations_reached == ()
    assert outcome.cleanup_steps == ()
    assert outcome.cleanup.state == "S-A"
    assert outcome.stopped_at == plan.steps[target_index].step_id
    assert outcome.stop_reason == UNEXPECTED_EXECUTION_FAILURE
    assert outcome.artifact_admissible is False


def test_an_exception_before_the_first_step_stops_without_cleanup() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    fake.raise_on[plan.steps[0].step_id] = RuntimeError("nothing has run yet")

    outcome = runner(plan, fake).execute()

    assert outcome.mutations_reached == ()
    assert outcome.cleanup_steps == ()
    assert outcome.steps[0].launch_failure == LAUNCH_BOUNDARY_FAILURE
    assert outcome.artifact_admissible is False


def test_a_failure_that_reached_no_step_is_still_recorded_as_a_stop() -> None:
    """`stopped_at` is never empty on a failure: an empty one would read as a
    completed run, and a completed run is the only kind that may produce an
    artifact. A failure that got no further than the plan itself is therefore
    recorded against a marker that cannot collide with a step id."""
    state = executor_module._RunState()
    state.stop("", UNEXPECTED_EXECUTION_FAILURE)

    assert state.stopped_at == BEFORE_FIRST_STEP
    assert state.probe_passed is False
    assert BEFORE_FIRST_STEP not in {step.step_id for step in PLAN.steps}

    # The first stop is the one that is kept: a later failure while unwinding
    # must not overwrite what actually stopped the run.
    state.stop("S-99", "a later failure")
    assert state.stopped_at == BEFORE_FIRST_STEP
    assert state.stop_reason == UNEXPECTED_EXECUTION_FAILURE


# ---------------------------------------------------------------------------
# Once a mutation may have been reached, cleanup is guaranteed
# ---------------------------------------------------------------------------


def test_an_exception_immediately_before_the_first_mutation_call_still_cleans_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The documented responsibility rule.

    Responsibility begins when the executor records the step's mutations, which
    it does **before** invoking the boundary. An exception raised between that
    record and the call therefore runs the full derived cleanup, even though no
    command reported anything and none may have started.
    """
    plan = runnable_plan()
    fake = satisfying(plan)
    target_index = first_mutation_step_index(plan)
    step = plan.steps[target_index]
    real_timeout_for = executor_module.timeout_for
    calls = {"n": 0}

    def counted(executable: str) -> float:
        calls["n"] += 1
        # The second call for this step: the one that computes the timeout for
        # the boundary invocation, after the mutation has been recorded.
        if calls["n"] == 2 * target_index + 2:
            raise OSError("a failure between recording the mutation and the call")
        return real_timeout_for(executable)

    monkeypatch.setattr(executor_module, "timeout_for", counted)
    live = runner(plan, fake)
    outcome = live.execute()

    # The mutation is this run's responsibility even though the command was
    # never invoked and reported nothing.
    assert set(step.mutation_ids) <= set(outcome.mutations_reached)
    assert step.step_id not in fake.calls
    assert_applicable_cleanup_ran_once(outcome, plan, fake)
    recorded = next(one for one in outcome.steps if one.step_id == step.step_id)
    assert recorded.launch_failure == LAUNCH_BOUNDARY_FAILURE
    assert recorded.satisfied is False
    assert outcome.stopped_at == step.step_id
    assert outcome.artifact_admissible is False


@pytest.mark.parametrize(
    "kind, step_id", sorted(MUTATION_KINDS.items()), ids=sorted(MUTATION_KINDS)
)
def test_an_exception_at_each_mutation_class_runs_the_whole_cleanup_once(
    kind: str, step_id: str
) -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    fake.raise_on[step_id] = OSError(f"the {kind} step failed unexpectedly")

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == step_id
    assert outcome.mutations_reached
    assert_applicable_cleanup_ran_once(outcome, plan, fake)
    assert outcome.artifact_admissible is False


def test_a_capture_or_sanitizer_failure_follows_the_same_cleanup_path() -> None:
    """A sanitizer refusal is raised inside the boundary, so it arrives here as
    an exception from the call — and is treated as one."""
    plan = runnable_plan()
    fake = satisfying(plan)
    step_id = plan.steps[first_mutation_step_index(plan) + 1].step_id
    fake.raise_on[step_id] = ObservationRefused(
        "the observation could not be shaped: /var/lib/fb-evidence-p5-0/journal"
    )

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == step_id
    assert_applicable_cleanup_ran_once(outcome, plan, fake)
    recorded = next(step for step in outcome.steps if step.step_id == step_id)
    assert recorded.launch_failure == LAUNCH_BOUNDARY_FAILURE
    assert recorded.satisfied is False
    assert "journal" not in recorded.stop_reason


def test_no_exception_text_reaches_the_recorded_outcome() -> None:
    """The exception may name a path, an account or an operating-system message.
    None of them is serialized: the categories are constants."""
    sentinel = "SENTINEL-0f3a /etc/postgresql/16/main/pg_hba.conf.SENTINEL-0f3a"
    plan = runnable_plan()
    fake = satisfying(plan)
    step_id = MUTATION_KINDS[sorted(MUTATION_KINDS)[0]]
    fake.raise_on[step_id] = OSError(sentinel)

    outcome = runner(plan, fake).execute()

    rendered = repr(outcome)
    assert "SENTINEL-0f3a" not in rendered
    for word in sentinel.split():
        assert word not in rendered

    # **R13.** The sentinel no longer contains `EACCES`. It used to, and the
    # assertion has stopped discriminating: since EH-R13-3 a satisfied negative
    # access case records `errno=EACCES` as a **reviewed observation**, compared
    # against the reviewed expectation the plan declares for it. That value is
    # evidence and belongs in the outcome; the exception's text does not, and is
    # what this test is about. The sentinel is now a token that could only have
    # come from the exception.


# ---------------------------------------------------------------------------
# Interruption
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("interruption", [KeyboardInterrupt, SystemExit])
def test_an_interruption_runs_cleanup_before_it_propagates(interruption) -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    step_id = MUTATION_KINDS[sorted(MUTATION_KINDS)[0]]
    fake.raise_on[step_id] = interruption()

    live = runner(plan, fake)
    with pytest.raises(interruption):
        live.execute()

    outcome = live.last_outcome
    assert outcome is not None
    assert outcome.stop_reason == OPERATOR_INTERRUPTION
    assert_applicable_cleanup_ran_once(outcome, plan, fake)
    assert outcome.artifact_admissible is False


def test_an_interruption_during_cleanup_propagates_and_blocks_the_next_run() -> None:
    """Cleanup itself was interrupted, so what it left behind is unknown. That is
    a stronger reason to refuse the next invocation than a known residue."""
    plan = runnable_plan()
    fake = satisfying(plan)
    fake.raise_on[plan.cleanup_plan.steps[2].step_id] = KeyboardInterrupt()

    live = runner(plan, fake)
    with pytest.raises(KeyboardInterrupt):
        live.execute()

    with pytest.raises(ExecutorRefused) as refusal:
        live.execute()
    assert "could not prove its cleanup complete" in str(refusal.value)


# ---------------------------------------------------------------------------
# The two facts, kept apart
# ---------------------------------------------------------------------------


def test_an_execution_exception_with_successful_cleanup_is_still_a_failed_run() -> None:
    """A failed run whose cleanup completed is S-A, and stays a failed run.

    **R16, conflict C-8** requires the step to be chosen rather than taken from
    the head of a sorted list. An exception on the **exclusive creation** of the
    disposable root is a different situation with a different correct answer: the
    mutation was attempted, `mkdir(2)` never reported, and a directory may exist
    that this run cannot identify — which is bounded residue and S-B, not a clean
    S-A. That path is asserted in `test_r16_c6_c7_c8.py`; this one is about a
    cleanup that completed, so it raises on a mutation the run can still fully
    reverse.
    """
    plan = runnable_plan()
    fake = satisfying(plan)
    creation = {
        step.step_id for step in plan.steps if step.establishes_ownership_by_creation
    }
    step_id = next(
        MUTATION_KINDS[kind]
        for kind in sorted(MUTATION_KINDS)
        if MUTATION_KINDS[kind] not in creation
    )
    fake.raise_on[step_id] = RuntimeError("something the harness did not expect")

    outcome = runner(plan, fake).execute()

    assert outcome.completed is False
    assert outcome.stopped_at == step_id
    assert outcome.cleanup.state == "S-A"
    assert outcome.cleanup.residue == ()
    assert outcome.exit_code == 2
    assert outcome.artifact_admissible is False


def test_execution_failure_plus_cleanup_failure_preserves_both_and_is_s_b() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    step_id = MUTATION_KINDS[sorted(MUTATION_KINDS)[0]]
    fake.raise_on[step_id] = RuntimeError("the run failed")
    # **R13.** Every path reversal, not the first declared one: since EH-R13-1
    # the cleanup that runs is the *applicable* one, and the first declared path
    # reversal may be a step this run was never entitled to carry out. Scripting
    # all of them to fail makes the assertion about what cleanup does with a
    # failure rather than about which step the plan happens to list first.
    for step in plan.cleanup_plan.steps:
        if step.kind is CleanupStepKind.REVERSAL and step.removes.startswith("/"):
            fake.scripted[step.step_id] = CommandResult(exit_status=1, timed_out=False)

    outcome = runner(plan, fake).execute()

    assert outcome.stopped_at == step_id
    assert outcome.stop_reason
    assert outcome.cleanup.state == "S-B"
    assert outcome.cleanup.residue
    assert all(path.startswith("/") for path in outcome.cleanup.residue)
    assert outcome.exit_code == 3
    assert outcome.artifact_admissible is False


# ---------------------------------------------------------------------------
# A cleanup step that fails does not stop the rest
# ---------------------------------------------------------------------------


def test_a_cleanup_boundary_exception_does_not_skip_the_remaining_steps() -> None:
    """The derived plan has no step whose safety depends on an earlier one
    succeeding, and every step is non-destructive when its object is absent — so
    stopping would leave more behind than continuing."""
    plan = runnable_plan()
    fake = satisfying(plan)
    first_cleanup = plan.cleanup_plan.steps[0]
    fake.raise_on[first_cleanup.step_id] = OSError("the restore could not be run")

    outcome = runner(plan, fake).execute()

    assert_applicable_cleanup_ran_once(outcome, plan, fake)
    assert outcome.cleanup.state != "S-C"
    assert outcome.cleanup.state == "S-B"
    failed = outcome.cleanup_steps[0]
    assert failed.satisfied is False
    assert failed.launch_failure == LAUNCH_BOUNDARY_FAILURE
    assert outcome.artifact_admissible is False


def test_a_cleanup_step_is_revalidated_immediately_before_it_runs() -> None:
    """Cleanup runs the destructive half of the plan, and is revalidated for the
    same reason the reviewed steps are: the object that reaches the loop is not
    obliged to be the object that was reviewed."""
    plan = runnable_plan()
    tampered_steps = list(plan.cleanup_plan.steps)
    victim = next(
        (index, step)
        for index, step in enumerate(tampered_steps)
        if step.kind is CleanupStepKind.REVERSAL and step.removes.startswith("/")
    )
    index, step = victim
    tampered_steps[index] = dataclasses.replace(step, run_as="mallory")
    tampered = ConcretePlan(
        execution_plan=plan.execution_plan,
        cleanup_plan=dataclasses.replace(
            plan.cleanup_plan, steps=tuple(tampered_steps)
        ),
        unresolved=(),
    )
    fake = satisfying(tampered)

    outcome = runner(tampered, fake).execute()

    assert step.step_id not in fake.calls
    refused = next(
        recorded
        for recorded in outcome.cleanup_steps
        if recorded.step_id == step.step_id
    )
    assert refused.launch_failure == LAUNCH_VALIDATION_REFUSED
    assert refused.satisfied is False
    assert step.removes in outcome.cleanup.residue
    assert outcome.cleanup.state == "S-B"


# ---------------------------------------------------------------------------
# Cleanup that could not be carried out at all
# ---------------------------------------------------------------------------


def test_a_failure_of_the_cleanup_machinery_is_s_b_and_names_declared_residue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    reversal = next(
        step
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVERSAL and step.removes.startswith("/")
    )
    fake.raise_on[reversal.step_id] = OSError("this object was not removed")

    def refuse(**keywords):
        raise RuntimeError("the cleanup classification itself failed")

    monkeypatch.setattr(executor_module, "classify_cleanup", refuse)
    live = runner(plan, fake)
    outcome = live.execute()

    assert outcome.cleanup.state == "S-B"
    assert outcome.exit_code == 3
    assert reversal.removes in outcome.cleanup.residue
    assert outcome.cleanup.configuration_risk
    assert outcome.artifact_admissible is False
    # Only declared objects are named. Nothing here came from the exception.
    declared = {
        step.removes
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVERSAL and step.removes
    }
    assert set(outcome.cleanup.residue) <= declared

    with pytest.raises(ExecutorRefused) as refusal:
        live.execute()
    assert "could not prove its cleanup complete" in str(refusal.value)


def test_a_rerun_after_an_unresolved_effective_configuration_is_refused() -> None:
    """Residue with no path is still residue: a temporary authentication rule
    that may still be in force blocks the next invocation exactly as a file does."""
    plan = runnable_plan()
    fake = satisfying(plan)
    proof = next(
        step for step in plan.cleanup_plan.verification_steps if step.refusal_required
    )
    fake.scripted[proof.step_id] = CommandResult(exit_status=0, timed_out=False)

    live = runner(plan, fake)
    first = live.execute()
    assert first.cleanup.state == "S-B"
    assert first.cleanup.residue == ()
    assert first.cleanup.configuration_risk

    with pytest.raises(ExecutorRefused) as refusal:
        live.execute()
    assert "refuses while it exists and does not clean it" in str(refusal.value)


def test_a_completed_run_still_reaches_s_c_and_cleans_up_once() -> None:
    """The guarantee added nothing to the ordinary path: a run in which nothing
    raised is unchanged."""
    plan = runnable_plan()
    fake = satisfying(plan)
    outcome = runner(plan, fake).execute()

    assert outcome.completed is True
    assert outcome.cleanup.state == "S-C"
    assert outcome.artifact_admissible is True
    assert_applicable_cleanup_ran_once(outcome, plan, fake)


# ---------------------------------------------------------------------------
# Materializations — the same guarantee, conflict C-4
# ---------------------------------------------------------------------------


@dataclass
class RaisingMaterializer:
    """Raises where it is told to, and applies everywhere else."""

    raise_on: dict[str, BaseException] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)

    def materialize(self, *, step_id, destination, content, sha256, owner, group, mode):
        self.calls.append(step_id)
        if step_id in self.raise_on:
            raise self.raise_on[step_id]
        return MaterializationResult(applied=True)


def test_a_materializer_that_raises_still_runs_the_whole_derived_cleanup() -> None:
    """The responsibility rule, applied to the step that writes a file.

    The configuration mutation is recorded before the write is attempted, so a
    materializer that raises — leaving it unknown whether the bytes reached the
    disk — gets the full restore, one reload, control and proof, exactly as an
    interrupted command would.
    """
    plan = runnable_plan()
    fake = satisfying(plan)
    item = plan.materializations[0]
    raising = RaisingMaterializer(
        raise_on={
            item.step_id: OSError(
                "/etc/postgresql/16/main freedomcoord SENTINEL-91c4"
            )
        }
    )

    outcome = runner(plan, fake, materializer=raising).execute()

    assert outcome.stopped_at == item.step_id
    assert set(item.mutation_ids) <= set(outcome.mutations_reached)
    assert_applicable_cleanup_ran_once(outcome, plan, fake)
    assert outcome.artifact_admissible is False

    recorded = next(step for step in outcome.steps if step.step_id == item.step_id)
    assert recorded.satisfied is False
    assert recorded.launch_failure == LAUNCH_BOUNDARY_FAILURE

    # The exception named a path, an account and an errno. None of them is
    # serialized: the category is a constant. The sentinel is a token that could
    # only have come from the exception — `EACCES` on its own stopped
    # discriminating in R13, because a satisfied negative access case now
    # records it as a **reviewed observation** compared against the plan's
    # declared expectation.
    rendered = repr(outcome)
    assert "SENTINEL-91c4" not in rendered
    assert "freedomcoord SENTINEL-91c4" not in rendered


def test_an_interruption_during_a_materialization_cleans_up_then_propagates() -> None:
    plan = runnable_plan()
    fake = satisfying(plan)
    item = plan.materializations[0]
    raising = RaisingMaterializer(raise_on={item.step_id: KeyboardInterrupt()})

    live = runner(plan, fake, materializer=raising)
    with pytest.raises(KeyboardInterrupt):
        live.execute()

    outcome = live.last_outcome
    assert outcome is not None
    assert outcome.stop_reason == OPERATOR_INTERRUPTION
    assert set(item.mutation_ids) <= set(outcome.mutations_reached)
    assert_applicable_cleanup_ran_once(outcome, plan, fake)
