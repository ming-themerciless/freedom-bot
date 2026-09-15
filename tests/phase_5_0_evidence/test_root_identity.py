"""**R13 — `E7` is a real semantic identity prerequisite.**

Codex's R12 review returned one Blocking finding, **EH-R12-1**: the required
semantic identity observation covered `E1 … E6` and `E8`, and **excluded `E7`**.
R12 substituted `P-01` and `P-02` for it and shipped a test asserting that an
`E7` identity step is *rejected*, so the exclusion was encoded in the validator,
in the derived identity set, in the review manifest and in the suite.

The substitution does not hold. `P-01` is `capsh --print` and `P-02` is
`capsh --decode=…`:

* neither runs the case program, so neither observes the process the reviewed
  vector actually produces;
* `capsh --print` reports **`capsh`'s own** securebits, before any `execve` of
  the interpreter, which is not the final securebits §2.13.5c's assertion table
  requires; and
* between them they cover the launcher's bounding set and a name-by-name
  expansion of a documented mask — not `E7`'s uid, gid, complete supplementary
  set, five masks, `NoNewPrivs` and final securebits as one compared
  observation.

So `E7` is now `P-06`: the same `identity` verb, in the same final interpreted
process, through the **direct** Option-B vector rather than a `capsh`
construction, compared against the same twelve keys. `P-01` and `P-02` are
retained and unchanged beside it.

This module is the regression suite for that finding. It has four parts:

1. **the plan** — one `E7` step, the exact direct vector, root, no `capsh`, no
   late binding, inside the validated disposable target, and ordered before
   every operation attributed to `E7`;
2. **the contract** — the same twelve keys as the other seven, every expected
   value from a reviewed target fact, and every refusal category;
3. **the executor** — the pre-execution refusal while a fact is unconfirmed, and
   a mismatch stopping the run before any dependent operation reaches the
   boundary; and
4. **the securebits path** — that the value comes from the case program's real
   `prctl(PR_GET_SECUREBITS)` observation and from no vector, option or
   preflight.

**Nothing here starts a process, reads a host account, touches a file, or states
a real fact about `oracle-test`.** The reviewed `E7` facts these tests inject are
deliberately synthetic — see `harness_fixtures.REVIEWED_E7_FACTS`.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tools.phase_5_0_evidence import capability, case_runtime
from tools.phase_5_0_evidence.approved_target import (
    APPROVED_TARGET,
    CONFIRMATION_TOKEN,
)
from tools.phase_5_0_evidence.capability import (
    DOCUMENTED_ROOT_MASK,
    EVIDENCE_IDENTITIES,
    e7_expected_values,
    e7_fact_confirmed,
    e7_target_facts_confirmed,
    unconfirmed_e7_facts,
)
from tools.phase_5_0_evidence.capture import CapturePolicy, sanitize
from tools.phase_5_0_evidence.case_runtime import (
    BOOTSTRAP_VERBS,
    CASE_PROGRAM_SOURCE,
    INTERPRETER_FLAGS,
    INTERPRETER_PATH,
    SECUREBITS_MAX,
    build_case_vector,
    case_program_path,
)
from tools.phase_5_0_evidence.concrete_plan import ConcretePlan, build_concrete_plan
from tools.phase_5_0_evidence.errors import PlanRefused
from tools.phase_5_0_evidence.execution import case_program
from tools.phase_5_0_evidence.execution.boundary import CommandResult, IdentityAbsent
from tools.phase_5_0_evidence.execution.executor import (
    ExecutingRunner,
    ExecutorRefused,
)
from tools.phase_5_0_evidence.execution.materializer import MaterializationResult
from tools.phase_5_0_evidence.expectations import (
    CAPSH_CONSTRUCTED_IDENTITIES,
    DUPLICATED_KEY,
    EXPECTATION_NOT_CONSTRUCTED,
    IDENTITY_KEYS,
    MALFORMED_OBSERVATIONS,
    MISSING_KEY,
    NO_OBSERVATIONS,
    OBSERVED_IDENTITIES,
    ROOT_IDENTITY,
    UNEQUAL_VALUE,
    UNEXPECTED_KEY,
    UNREADABLE_VALUE,
    constructed_identity_contract,
    contract_for,
    root_identity_contract,
)
from tools.phase_5_0_evidence.plan import ROOT_IDENTITY_NAME, CommandStep, StepRole
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.harness_fixtures import (
    RecordingEffects,
    DISPOSABLE_ACCOUNTS,
    DISPOSABLE_GROUPS,
    REVIEWED_E7_FACTS,
    bound_argv,
    cleanup_observations_for,
    observations_for,
    runnable_plan,
    supply_reviewed_e7_facts,
)

SOURCES = {name: f"# {name}\n".encode("utf-8") for name in COVERED_SOURCES}

SOURCE_ROOT = Path(__file__).resolve().parents[2]

#: The two interpreter facts, as every other executor-driving module states them.
REVIEWED_INTERPRETER_DIGEST = "5" * 64
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"

#: `P-06`'s step id, named once so a rename fails here rather than silently
#: reducing this module to testing nothing.
E7_STEP = "P-06"


@pytest.fixture(autouse=True)
def _the_reviewed_target_facts_are_supplied(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gates 3 and 4, given the values a run would have.

    Gate 4 — the `E7` facts — is asserted on its own against the **shipped**
    `UNCONFIRMED` values in `test_the_shipped_e7_facts_refuse_the_executor`,
    which takes no fixture.
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


@pytest.fixture()
def plan() -> ConcretePlan:
    return build_concrete_plan()


# ---------------------------------------------------------------------------
# 1. The plan: one E7 step, the exact vector, and the ordering
# ---------------------------------------------------------------------------


def test_the_plan_carries_exactly_one_e7_identity_step_and_the_seven_others(
    plan,
) -> None:
    """**EH-R12-1.** Eight identity steps, not seven.

    R12 generated `B5-E1 … B5-E6` and `B5-E8` and nothing for `E7`. The seven are
    unchanged and `P-06` joins them.
    """
    named = [
        (step.identity_name, step.step_id)
        for step in plan.steps
        if step.capture is CapturePolicy.CASE_IDENTITY
    ]
    assert len(named) == 8
    assert dict(named).keys() == OBSERVED_IDENTITIES
    assert [step_id for name, step_id in named if name == ROOT_IDENTITY] == [E7_STEP]
    for name in sorted(CAPSH_CONSTRUCTED_IDENTITIES):
        assert dict(named)[name] == f"B5-{name}"


def test_the_e7_step_is_the_exact_direct_option_b_identity_vector(plan) -> None:
    """The reviewed vector, positionally — no `capsh`, no shebang, no wrapper.

    `build_case_vector` validates through `case_runtime.validate_case_vector`,
    so the path is `contained_path()`-checked against the confirmed disposable
    root and the verb and its zero arity come from the closed table.
    """
    step = next(item for item in plan.steps if item.step_id == E7_STEP)
    expected = build_case_vector(APPROVED_TARGET, "identity")
    assert step.argv == expected
    assert step.argv == (
        INTERPRETER_PATH,
        *INTERPRETER_FLAGS,
        case_program_path(APPROVED_TARGET),
        "identity",
    )
    assert step.argv[-2].startswith(APPROVED_TARGET.root_path + "/")
    assert not any("capsh" in argument for argument in step.argv)
    assert not any(argument.startswith("--") for argument in step.argv[3:])


def test_the_e7_step_runs_as_root_and_substitutes_nothing(plan) -> None:
    """§2.13.5c: *"no invocation … no securebit set and no drop of any kind"*.

    An `E7` step that declared a late-binding site would have a disposable
    account's number substituted into its vector, and would then be observing
    something that is not `E7`.
    """
    step = next(item for item in plan.steps if item.step_id == E7_STEP)
    assert step.run_as == "root"
    assert step.bindings == ()
    assert step.role is StepRole.PREREQUISITE
    assert step.identity_name == ROOT_IDENTITY == ROOT_IDENTITY_NAME
    assert step.capture is CapturePolicy.CASE_IDENTITY


def test_a_step_naming_e7_may_not_bind_or_assume_another_identity() -> None:
    """The two guards, asserted rather than described."""
    vector = build_case_vector(APPROVED_TARGET, "identity")
    # The shape the plan actually generates is accepted.
    CommandStep(
        step_id="X",
        band="capability",
        run_as="root",
        argv=vector,
        purpose="p",
        capture=CapturePolicy.CASE_IDENTITY,
        identity_name=ROOT_IDENTITY,
    )
    with pytest.raises(PlanRefused):
        CommandStep(
            step_id="X",
            band="capability",
            run_as="freedomsheet",
            argv=vector,
            purpose="p",
            capture=CapturePolicy.CASE_IDENTITY,
            identity_name=ROOT_IDENTITY,
        )
    capsh_step = next(
        step
        for step in build_concrete_plan().steps
        if step.step_id == "B5-E1"
    )
    with pytest.raises(PlanRefused):
        CommandStep(
            step_id="X",
            band="capability",
            run_as="root",
            argv=capsh_step.argv,
            purpose="p",
            capture=CapturePolicy.CASE_IDENTITY,
            identity_name=ROOT_IDENTITY,
            bindings=capsh_step.bindings,
        )


def test_the_e7_observation_precedes_every_root_case_program_operation(plan) -> None:
    """**EH-R12-1's ordering half.**

    Every case-program **operation** the root harness performs is downstream of
    `P-06`. The two observation verbs are excluded and stated as such: `runtime`
    and `identity` change nothing and take no path, and `P-05` deliberately runs
    first so the identity is observed through an already-established
    interpreter.

    **R16, conflict C-8 adds the two bootstrap verbs to that exclusion, and it is
    a dependency rather than a convenience.** `P-06` runs `<root>/bin/case`,
    which does not exist until the root does, and `mkroot` is what creates the
    root. No ordering can put the observation first. What stands in its place is
    not an assumption either: `R-01` compares uid 0 and gid 0 through `id` before
    anything is constructed, and `B3-02` reads the created directory's owner and
    group back with `stat` — and `mkdir(2)` gives a directory the creating
    process's uid and gid, so that reading is evidence about the process that
    made it. Neither bootstrap verb asserts what an identity could or could not
    do, which is what the assertion contract governs.
    """
    order = {step.step_id: index for index, step in enumerate(plan.steps)}
    verb_index = 1 + len(INTERPRETER_FLAGS) + 1
    bootstrapped = []
    for step in plan.steps:
        if step.run_as != "root" or len(step.argv) <= verb_index:
            continue
        if step.argv[0] != INTERPRETER_PATH:
            continue
        verb = step.argv[verb_index]
        if verb in ("runtime", "identity"):
            continue
        if verb in BOOTSTRAP_VERBS:
            bootstrapped.append(step.step_id)
            continue
        assert order[step.step_id] > order[E7_STEP], step.step_id
    # The exclusion is exercised rather than merely granted: exactly one step
    # uses it, it precedes `P-06`, and the two steps that stand in for the
    # identity assertion precede it in turn.
    assert bootstrapped == ["B3-01"]
    assert order["B3-01"] < order[E7_STEP]
    assert order["R-01"] < order["B3-01"] < order["B3-02"]


def test_the_generator_refuses_a_plan_whose_e7_observation_is_late() -> None:
    """The ordering is checked over the generated plan, not asserted about it."""
    from tools.phase_5_0_evidence.concrete_plan import (
        _validate_root_identity_ordering,
    )

    steps = list(build_concrete_plan().steps)
    observation = next(index for index, step in enumerate(steps) if step.step_id == E7_STEP)
    operation = next(
        index
        for index, step in enumerate(steps)
        if step.run_as == "root"
        and step.argv[:1] == (INTERPRETER_PATH,)
        and index > observation
    )
    reordered = list(steps)
    reordered.insert(observation, reordered.pop(operation))
    with pytest.raises(PlanRefused) as refusal:
        _validate_root_identity_ordering(reordered)
    assert "before the E7 identity observation" in str(refusal.value)

    without = [step for step in steps if step.step_id != E7_STEP]
    with pytest.raises(PlanRefused) as absent:
        _validate_root_identity_ordering(without)
    assert "0 E7 identity observations" in str(absent.value)


# ---------------------------------------------------------------------------
# 2. The contract: the same twelve keys, from reviewed target facts
# ---------------------------------------------------------------------------


def e7_observation(**overrides) -> tuple[tuple[str, str], ...]:
    """The exact complete `E7` observation, with named keys replaced or removed."""
    values = dict(root_identity_contract().expected_observations())
    for key, value in overrides.items():
        if value is None:
            values.pop(key, None)
        else:
            values[key] = value
    return tuple(sorted(values.items()))


def test_e7s_contract_has_the_same_twelve_keys_as_the_other_seven() -> None:
    """A narrower `E7` contract would be EH-R12-1 in a new shape."""
    root = root_identity_contract()
    assert set(root.keys) == set(IDENTITY_KEYS)
    assert len(root.keys) == 12
    assert set(root.keys) == set(_KEY_VALUE_KEYS()[CapturePolicy.CASE_IDENTITY])
    for name in sorted(CAPSH_CONSTRUCTED_IDENTITIES):
        other = constructed_identity_contract(
            name, uid=5002, gid=5002, group_ids=frozenset({5002, 5004})
        )
        assert set(other.keys) == set(root.keys), name


def _KEY_VALUE_KEYS():
    from tools.phase_5_0_evidence.capture import _KEY_VALUE_KEYS as keys

    return keys


def test_the_contract_cannot_be_built_with_a_narrower_key_set() -> None:
    """The guard that makes the previous test load-bearing."""
    from tools.phase_5_0_evidence.expectations import (
        Comparison,
        Expectation,
        ObservationContract,
    )

    with pytest.raises(PlanRefused):
        ObservationContract(
            policy=CapturePolicy.CASE_IDENTITY,
            subject=ROOT_IDENTITY,
            expectations=(Expectation("verb", Comparison.TEXT, "identity"),),
        )


@pytest.mark.parametrize("key", sorted(REVIEWED_E7_FACTS))
def test_every_expected_e7_value_comes_from_its_reviewed_target_fact(key: str) -> None:
    """Not from the observation, not from `M`, not from a bound vector.

    The injected facts are deliberately not §2.13.5c's documented row, so a
    contract that had fallen back to `DOCUMENTED_ROOT_MASK` fails here.
    """
    expected = dict(root_identity_contract().expected_observations())
    assert expected[key] == REVIEWED_E7_FACTS[key]
    if key.startswith("cap_"):
        assert int(expected[key], 16) != DOCUMENTED_ROOT_MASK


def test_the_two_literals_are_the_case_programs_own_and_not_facts() -> None:
    expected = dict(root_identity_contract().expected_observations())
    assert expected["verb"] == "identity"
    assert expected["result"] == "returned"
    assert set(expected) - set(REVIEWED_E7_FACTS) == {"verb", "result"}


def test_supplying_a_fact_changes_the_contract_where_it_is_supplied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The facts are read through the module, so a substitution takes effect."""
    monkeypatch.setattr(
        capability,
        "E7_TARGET_FACTS",
        {**REVIEWED_E7_FACTS, "securebits": "7"},
    )
    assert dict(root_identity_contract().expected_observations())["securebits"] == "7"


def test_the_complete_matching_observation_satisfies_the_contract() -> None:
    assert root_identity_contract().check(e7_observation()) == ""


@pytest.mark.parametrize(
    ("category", "key", "wrong"),
    [
        ("uid", "uid", "1"),
        ("gid", "gid", "1"),
        ("groups", "groups", "0"),
        ("cap_inh", "cap_inh", "1235"),
        ("cap_prm", "cap_prm", "1235"),
        ("cap_eff", "cap_eff", "1235"),
        ("cap_bnd", "cap_bnd", "1235"),
        ("cap_amb", "cap_amb", "1235"),
        ("no_new_privs", "no_new_privs", "1"),
        ("securebits", "securebits", "4"),
        ("verb", "verb", "runtime"),
        ("result", "result", "unobserved"),
    ],
)
def test_one_mismatch_in_each_e7_field_category_is_refused(
    category: str, key: str, wrong: str
) -> None:
    refusal = root_identity_contract().check(e7_observation(**{key: wrong}))
    assert refusal.startswith(UNEQUAL_VALUE), category
    assert key in refusal, category


@pytest.mark.parametrize(
    ("label", "observations", "expected"),
    [
        ("no observation at all", (), NO_OBSERVATIONS),
        ("a malformed pair list", ("uid=0",), MALFORMED_OBSERVATIONS),
        ("a missing key", None, MISSING_KEY),
        ("a duplicated key", None, DUPLICATED_KEY),
        ("an unreadable value", None, UNREADABLE_VALUE),
        ("an unexpected key", None, UNEXPECTED_KEY),
    ],
)
def test_every_refusal_category_is_a_fixed_safe_classification(
    label: str, observations, expected: str
) -> None:
    """Missing, duplicated, unreadable, malformed and unexpected, each refused —
    and none of the classifications names an observed value."""
    if label == "a missing key":
        observations = e7_observation(securebits=None)
    elif label == "a duplicated key":
        observations = e7_observation() + (("uid", REVIEWED_E7_FACTS["uid"]),)
    elif label == "an unreadable value":
        observations = e7_observation(cap_bnd="unreadable")
    elif label == "an unexpected key":
        observations = e7_observation() + (("extra", "1"),)
    refusal = root_identity_contract().check(observations)
    assert refusal.startswith(expected), label
    for value in REVIEWED_E7_FACTS.values():
        if value in ("0",):
            continue
        assert value not in refusal, label


@pytest.mark.parametrize("key", sorted(REVIEWED_E7_FACTS))
def test_a_missing_e7_key_names_the_reviewed_key_and_nothing_else(key: str) -> None:
    refusal = root_identity_contract().check(e7_observation(**{key: None}))
    assert refusal.startswith(MISSING_KEY)
    assert key in refusal


# ---------------------------------------------------------------------------
# 3. Unconfirmed facts, and the pre-execution refusal
# ---------------------------------------------------------------------------


def test_the_facts_ship_unconfirmed_in_the_tree_being_submitted() -> None:
    """Read from the source rather than from the imported module, so a
    monkeypatch anywhere in this suite cannot make this pass."""
    source = (
        SOURCE_ROOT / "tools/phase_5_0_evidence/capability.py"
    ).read_text(encoding="utf-8")
    assert 'E7_FACT_UNCONFIRMED = "UNCONFIRMED"' in source
    for fact in sorted(REVIEWED_E7_FACTS):
        assert f'"{fact}": E7_FACT_UNCONFIRMED,' in source
    assert "DOCUMENTED_ROOT_MASK" not in source.split("E7_TARGET_FACTS: Mapping")[1].split("}")[0]


def test_every_unconfirmed_fact_is_reported_and_the_set_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for fact in sorted(REVIEWED_E7_FACTS):
        monkeypatch.setattr(
            capability,
            "E7_TARGET_FACTS",
            {**REVIEWED_E7_FACTS, fact: capability.E7_FACT_UNCONFIRMED},
        )
        assert unconfirmed_e7_facts() == (fact,), fact
        assert not e7_target_facts_confirmed(), fact
        assert not e7_fact_confirmed(fact), fact
        with pytest.raises(PlanRefused):
            e7_expected_values()
        with pytest.raises(PlanRefused):
            root_identity_contract()


@pytest.mark.parametrize(
    ("fact", "malformed"),
    [
        ("uid", "-1"),
        ("gid", "zero"),
        ("groups", "0,"),
        ("cap_prm", "0X1234"),
        ("cap_bnd", "GHI"),
        ("securebits", "100"),
        ("no_new_privs", ""),
    ],
)
def test_a_fact_stated_in_a_shape_the_capture_boundary_cannot_report_is_unconfirmed(
    monkeypatch: pytest.MonkeyPatch, fact: str, malformed: str
) -> None:
    """A reviewed value nothing could ever equal is refused here rather than
    compared against forever."""
    monkeypatch.setattr(
        capability, "E7_TARGET_FACTS", {**REVIEWED_E7_FACTS, fact: malformed}
    )
    assert not e7_fact_confirmed(fact)
    with pytest.raises(PlanRefused):
        root_identity_contract()


def test_the_securebits_fact_shape_and_the_programs_range_agree() -> None:
    """Two digits of hexadecimal is `0 … 0xff`, which is `SECUREBITS_MAX`."""
    shape = capability._E7_FACT_SHAPES["securebits"]
    assert shape.match(format(SECUREBITS_MAX, "x"))
    assert not shape.match(format(SECUREBITS_MAX + 1, "x"))
    assert SECUREBITS_MAX == case_program.SECUREBITS_MAX


@dataclass
class Lookup:
    def account(self, name: str) -> tuple[int, int]:
        if name not in DISPOSABLE_ACCOUNTS:
            raise IdentityAbsent(name)
        return DISPOSABLE_ACCOUNTS[name]

    def group_id(self, name: str) -> int:
        if name not in DISPOSABLE_GROUPS:
            raise IdentityAbsent(name)
        return DISPOSABLE_GROUPS[name]

    def supplementary_group_names(self, name, primary_gid):  # pragma: no cover
        raise AssertionError("the executor resolves ids, never memberships")

    def effective_ids(self) -> tuple[int, int]:  # pragma: no cover
        return 0, 0


@dataclass
class Materializer:
    requests: list = field(default_factory=list)

    def materialize(self, *, step_id, destination, content, sha256, owner, group, mode):
        self.requests.append(step_id)
        return MaterializationResult(applied=True)


@dataclass
class Boundary:
    scripted: dict = field(default_factory=dict)
    calls: list = field(default_factory=list)

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
        self.calls.append(step_id)
        if step_id in self.scripted:
            return self.scripted[step_id]
        return CommandResult(exit_status=0, timed_out=False)


def satisfying(plan: ConcretePlan) -> Boundary:
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
    return Boundary(scripted=scripted)


def runner(plan: ConcretePlan, boundary: Boundary) -> ExecutingRunner:
    return ExecutingRunner(
        plan=plan,
        boundary=boundary,
        reviewed_digest=ReviewManifest.build(plan, SOURCES).digest(),
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        materializer=Materializer(),
        identity_lookup=Lookup(),
        effects=RecordingEffects(),
    )


def test_the_shipped_e7_facts_refuse_the_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """**Gate 4.** The refusal happens at construction, before `execute()` and
    therefore before the boundary is called at all.

    The autouse fixture is undone here so the gate is asserted against the
    values this tree actually ships. The scripted boundary is built **first**,
    while the facts are still supplied, because a compliant observation is
    derived from the same contract — and then discarded, unused, because the
    gate refuses before a single call reaches it.
    """
    plan = runnable_plan()
    boundary = satisfying(plan)
    monkeypatch.undo()
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_SHA256", REVIEWED_INTERPRETER_DIGEST
    )
    monkeypatch.setattr(
        case_runtime,
        "EXPECTED_INTERPRETER_REAL_PATH",
        REVIEWED_INTERPRETER_REAL_PATH,
    )
    assert not e7_target_facts_confirmed()
    with pytest.raises(ExecutorRefused) as refusal:
        runner(plan, boundary)
    assert "E7's reviewed target facts are not all stated" in str(refusal.value)
    assert boundary.calls == []


@pytest.mark.parametrize("fact", sorted(REVIEWED_E7_FACTS))
def test_one_unconfirmed_fact_refuses_before_any_command_starts(
    monkeypatch: pytest.MonkeyPatch, fact: str
) -> None:
    plan = runnable_plan()
    boundary = satisfying(plan)
    monkeypatch.setattr(
        capability,
        "E7_TARGET_FACTS",
        {**REVIEWED_E7_FACTS, fact: capability.E7_FACT_UNCONFIRMED},
    )
    with pytest.raises(ExecutorRefused) as refusal:
        runner(plan, boundary)
    assert fact in str(refusal.value)
    assert boundary.calls == []


def test_the_whole_plan_runs_when_the_e7_observation_matches() -> None:
    """The positive case, so the negatives below are about `E7` and not about a
    plan that could never complete."""
    plan = runnable_plan()
    boundary = satisfying(plan)
    outcome = runner(plan, boundary).execute()
    assert outcome.completed, outcome.stop_reason
    recorded = {step.step_id: step for step in outcome.steps}[E7_STEP]
    assert recorded.satisfied
    assert dict(recorded.observations) == dict(e7_observation())


@pytest.mark.parametrize(
    ("label", "observations"),
    [
        ("no observations", ()),
        ("a missing securebits", None),
        ("a duplicated uid", None),
        ("an unreadable mask", None),
        ("an unexpected key", None),
        ("a wrong uid", None),
        ("a wrong gid", None),
        ("a wrong group set", None),
        ("a wrong cap_bnd", None),
        ("a wrong no_new_privs", None),
        ("a wrong securebits", None),
    ],
)
def test_e7_exiting_zero_is_not_a_pass(label: str, observations) -> None:
    """**EH-R12-1, end to end.** The vector exits exactly as the reviewed plan
    requires, and the run still stops at `P-06`."""
    replacements = {
        "a missing securebits": e7_observation(securebits=None),
        "a duplicated uid": e7_observation() + (("uid", REVIEWED_E7_FACTS["uid"]),),
        "an unreadable mask": e7_observation(cap_prm="unreadable"),
        "an unexpected key": e7_observation() + (("extra", "1"),),
        "a wrong uid": e7_observation(uid="1"),
        "a wrong gid": e7_observation(gid="1"),
        "a wrong group set": e7_observation(groups="0"),
        "a wrong cap_bnd": e7_observation(cap_bnd="1235"),
        "a wrong no_new_privs": e7_observation(no_new_privs="1"),
        "a wrong securebits": e7_observation(securebits="4"),
    }
    if observations is None:
        observations = replacements[label]
    plan = runnable_plan()
    boundary = satisfying(plan)
    boundary.scripted[E7_STEP] = CommandResult(
        exit_status=0, timed_out=False, observations=observations
    )
    outcome = runner(plan, boundary).execute()
    assert not outcome.completed, label
    assert outcome.stopped_at == E7_STEP, label
    assert "does not satisfy the reviewed expectation" in outcome.stop_reason, label
    recorded = {step.step_id: step for step in outcome.steps}[E7_STEP]
    assert recorded.exit_status == 0 and not recorded.satisfied, label
    assert not outcome.artifact_admissible, label


def test_an_e7_mismatch_stops_every_dependent_operation() -> None:
    """Nothing after `P-06` reaches the boundary, and nothing after it is
    interpreted — which is every operation this plan attributes to `E7`."""
    plan = runnable_plan()
    boundary = satisfying(plan)
    boundary.scripted[E7_STEP] = CommandResult(
        exit_status=0, timed_out=False, observations=e7_observation(securebits="4")
    )
    outcome = runner(plan, boundary).execute()
    order = [step.step_id for step in plan.steps]
    after = set(order[order.index(E7_STEP) + 1 :])
    assert not (set(boundary.calls) & after), sorted(set(boundary.calls) & after)
    assert {step.step_id for step in outcome.steps} & after == set()
    assert not outcome.artifact_admissible


def test_the_run_refuses_when_the_e7_contract_cannot_be_built(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail-closed twice: if gate 4 were removed, the contract would still be
    unbuildable and the step would still not be satisfied.

    **R13.** The run now stops at `P-01` rather than at `P-06`, and that is the
    remediation of EH-R13-3 showing through rather than a weakening. `P-01`
    observes the **launching process**, which *is* `E7`, so its bounding-set
    mask, ambient-set mask, securebits and no-new-privs are four of the same ten
    reviewed target facts, read from the same source. `e7_expected_values()` is
    all-or-nothing by design — a contract over nine of ten facts would compare
    nine and let the tenth be anything — so withdrawing any one of them makes the
    earlier contract unbuildable first, and the run stops there having compared
    nothing and executed no case. `P-06`'s own half of this is asserted directly
    below, against the contract builder rather than through a run that can no
    longer reach it.
    """
    plan = runnable_plan()
    # Built **before** the fact is withdrawn: the positive fixture derives its
    # scripted observations from the same contracts, so it could not be built
    # afterwards either — which is itself the fail-closed property.
    boundary = satisfying(plan)
    built = runner(plan, boundary)
    monkeypatch.setattr(
        capability,
        "E7_TARGET_FACTS",
        {**REVIEWED_E7_FACTS, "securebits": capability.E7_FACT_UNCONFIRMED},
    )
    outcome = built.execute()
    assert outcome.stopped_at == "P-01"
    assert EXPECTATION_NOT_CONSTRUCTED in outcome.stop_reason
    assert not outcome.artifact_admissible
    # Nothing after `P-01` reached the boundary, so no operation ran under an
    # identity nothing had established.
    order = [step.step_id for step in plan.steps]
    after = set(order[order.index("P-01") + 1 :])
    assert not (set(boundary.calls) & after)

    for withdrawn in ("groups", "uid", "cap_bnd", "no_new_privs"):
        monkeypatch.setattr(
            capability,
            "E7_TARGET_FACTS",
            {**REVIEWED_E7_FACTS, withdrawn: capability.E7_FACT_UNCONFIRMED},
        )
        with pytest.raises(PlanRefused):
            root_identity_contract()


# ---------------------------------------------------------------------------
# 4. The securebits comes from the observation path, not from a vector
# ---------------------------------------------------------------------------


def test_the_e7_vector_carries_no_securebits_option_to_infer_from(plan) -> None:
    """R11's defect was inferring the state from `--secbits=` in the vector.

    `E7`'s vector has no options at all, so there is nothing to infer from even
    if something wanted to: the only source is the case program's own call.
    """
    step = next(item for item in plan.steps if item.step_id == E7_STEP)
    assert not any("secbits" in argument for argument in step.argv)
    assert not any(argument.startswith("--") for argument in step.argv[3:])


def test_the_case_program_reads_e7s_securebits_through_prctl() -> None:
    """The verb the `E7` vector names reaches the one native call.

    Driven across a fixed injected boundary — this process's securebits is never
    changed, and could not be: setting them needs `CAP_SETPCAP`, no test here
    runs as root, and the program contains no setter.
    """
    verb_index = 1 + len(INTERPRETER_FLAGS) + 1
    assert build_case_vector(APPROVED_TARGET, "identity")[verb_index] == "identity"
    for value in (0x0, 0x4, int(REVIEWED_E7_FACTS["securebits"], 16), SECUREBITS_MAX):
        emitted = case_program._securebits_text(read=lambda v=value: (v, 0))
        assert emitted == format(value, "x")
        observed = dict(
            sanitize(
                CapturePolicy.CASE_IDENTITY,
                f"verb=identity\nresult=returned\nsecurebits={emitted}\n",
            )
        )
        assert int(observed["securebits"], 16) == value


def test_p01_and_p02_are_retained_unchanged_and_are_not_the_e7_observation(
    plan,
) -> None:
    """They remain separate root/target preflight evidence.

    Neither runs the case program, so neither can be the observation `P-06` is;
    and `P-06` does not replace them.
    """
    by_id = {step.step_id: step for step in plan.steps}
    assert by_id["P-01"].argv == ("/usr/sbin/capsh", "--print")
    assert by_id["P-02"].argv == ("/usr/sbin/capsh", "--decode=0x000001ffffffffff")
    for step_id in ("P-01", "P-02"):
        assert by_id[step_id].capture is not CapturePolicy.CASE_IDENTITY
        assert by_id[step_id].identity_name == ""
        assert by_id[step_id].argv[0] != INTERPRETER_PATH


def test_the_manifest_pins_e7s_facts_and_their_confirmed_state() -> None:
    """A reviewer approves each value and whether it has been supplied, and
    supplying one changes the digest — which is the re-review it should
    trigger."""
    plan = build_concrete_plan()
    body = ReviewManifest.build(plan, SOURCES).as_mapping()
    root = body["expectations"]["root_identity"]
    assert root["identity"] == ROOT_IDENTITY
    assert root["user"] == EVIDENCE_IDENTITIES[ROOT_IDENTITY].user == "root"
    assert root["confirmed"] is True
    assert {fact["name"] for fact in root["facts"]} == set(REVIEWED_E7_FACTS)
    assert {fact["name"]: fact["value"] for fact in root["facts"]} == REVIEWED_E7_FACTS
    assert {name for name in body["expectations"]["case_identity"][0]}
    assert {
        row["identity"] for row in body["expectations"]["case_identity"]
    } == CAPSH_CONSTRUCTED_IDENTITIES
    assert [
        step["identity_name"]
        for step in body["steps"]
        if step["step_id"] == E7_STEP
    ] == [ROOT_IDENTITY]


def test_the_manifest_digest_changes_when_a_reviewed_e7_fact_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    plan = build_concrete_plan()
    before = ReviewManifest.build(plan, SOURCES).digest()
    monkeypatch.setattr(
        capability, "E7_TARGET_FACTS", {**REVIEWED_E7_FACTS, "securebits": "6"}
    )
    assert ReviewManifest.build(plan, SOURCES).digest() != before


def test_no_expected_e7_value_is_read_from_an_observation() -> None:
    """A source-level assertion, in the spirit of `P-05`'s.

    `root_identity_contract` mentions no observation, no `/proc`, no `capsh` and
    no preflight step id: its only source is `capability.e7_expected_values()`.
    """
    source = (
        SOURCE_ROOT / "tools/phase_5_0_evidence/expectations.py"
    ).read_text(encoding="utf-8")
    body = source.split("def root_identity_contract()")[1].split("\ndef ")[0]
    # The docstring is prose about the finding and names both preflight steps;
    # what this test is about is the executable body, so it is removed first.
    code = re.sub(r'""".*?"""', "", body, count=1, flags=re.S)
    code = "\n".join(
        line for line in code.splitlines() if not line.strip().startswith("#")
    )
    assert "capability.e7_expected_values()" in code
    for forbidden in ("observations", "result.", "/proc", "capsh", "P-01", "P-02"):
        assert forbidden not in code, forbidden
