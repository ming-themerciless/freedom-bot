"""**PR-20260907-3 — the capture boundary discarded the evidence of a defect.**

`capture._case_observations()` read a case program's output line by line and
`continue`d on any line that had no `=` separator or whose key was outside the
policy's key set. The line vanished. What reached
`expectations.ObservationContract.check()` was the remaining, valid pairs — and
they satisfied the contract, so the run was recorded as a **pass**.

Codex reproduced all three as accepted, by building an `E1` contract with
synthetic uid/gid/group numbers, serialising `expected_observations()` into the
`key=value` text the case program prints, and passing that text through
`sanitize(CASE_IDENTITY, text)` and then `contract.check()`:

* the valid observation — accepted, correctly;
* the same observation plus `unexpected_key=unexpected_value` — **accepted**;
* the same observation plus `malformed-output-line` — **accepted**.

So the contract's `UNEXPECTED_KEY` and `MALFORMED_OBSERVATIONS` classifications
could never fire against real process output. They could only be produced by
handing `check()` a tuple directly, which no run ever does.

The correction is in the capture boundary, because that is where the information
is lost: for the two policies whose observation is compared against a closed
semantic contract — `CASE_IDENTITY` and `CASE_RUNTIME` — an unexpected key or a
malformed non-blank line now emits a **fixed marker carrying no host text**,
which is outside every contract's key set and therefore refuses. The line's own
content still never reaches an artifact.

**The other policies are unchanged.** `CASE_RESULT` and `UNIT_DIRECTIVES` share
the parser and are not compared against a closed contract; broadening them
because they share a function would be a change nobody asked for.

Every test here drives the **complete path**: raw text → `capture.sanitize` →
`ObservationContract.check`, and for the executor cases raw text → `sanitize` →
`CommandResult` → `ExecutingRunner`. None injects a tuple directly into
`check()`, which is the thing that made the defect invisible.

**Nothing here starts a process, reads a host account or touches a file.**
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from tools.phase_5_0_evidence import capability, case_runtime
from tools.phase_5_0_evidence.approved_target import (
    APPROVED_TARGET,
    CONFIRMATION_TOKEN,
)
from tools.phase_5_0_evidence.capture import (
    MALFORMED_LINE_MARKER,
    STRICT_CASE_POLICIES,
    UNEXPECTED_KEY_MARKER,
    CapturePolicy,
    sanitize,
)
from tools.phase_5_0_evidence.case_runtime import (
    CASE_PROGRAM_SOURCE,
    case_program_path,
)
from tools.phase_5_0_evidence.concrete_plan import ConcretePlan, build_concrete_plan
from tools.phase_5_0_evidence.execution.boundary import CommandResult, IdentityAbsent
from tools.phase_5_0_evidence.execution.executor import ExecutingRunner
from tools.phase_5_0_evidence.execution.materializer import MaterializationResult
from tools.phase_5_0_evidence.expectations import (
    CAPSH_CONSTRUCTED_IDENTITIES,
    DUPLICATED_KEY,
    UNEXPECTED_KEY,
    UNREADABLE_VALUE,
    ROOT_IDENTITY,
    case_runtime_contract,
    constructed_identity_contract,
    root_identity_contract,
)
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.harness_fixtures import (
    RecordingEffects,
    cleanup_observations_for,
    DISPOSABLE_ACCOUNTS,
    DISPOSABLE_GROUPS,
    bound_argv,
    observations_for,
    runnable_plan,
    supply_reviewed_e7_facts,
    load_test_source_bytes,
)

SOURCES = load_test_source_bytes()

REVIEWED_INTERPRETER_DIGEST = "5" * 64
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"

CASE_PROGRAM_DIGEST = ReviewManifest.build(
    build_concrete_plan(), SOURCES
).digest_for(CASE_PROGRAM_SOURCE)

INSTALLED_CASE_PROGRAM = case_program_path(APPROVED_TARGET)

#: The two lines Codex appended to a valid observation. Neither may be accepted,
#: and neither may reach an artifact.
UNEXPECTED_LINE = "unexpected_key=unexpected_value"
MALFORMED_LINE = "malformed-output-line"


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


# ---------------------------------------------------------------------------
# The exact reproduction, as text
# ---------------------------------------------------------------------------


def emitted(contract) -> str:
    """The `key=value` text a compliant case program prints for one contract.

    Sorted and newline-terminated, which is what `_emit` in the case program
    produces — so a test that passes here is a test about the real output shape
    and not about a convenient one.
    """
    return "".join(
        f"{key}={value}\n" for key, value in contract.expected_observations()
    )


def identity_contract_for(name: str):
    identity = capability.EVIDENCE_IDENTITIES[name]
    group_names = (identity.primary_group, *identity.supplementary_groups)
    return constructed_identity_contract(
        name,
        uid=DISPOSABLE_ACCOUNTS[identity.user][0],
        gid=DISPOSABLE_GROUPS[identity.primary_group],
        group_ids=frozenset(DISPOSABLE_GROUPS[group] for group in group_names),
    )


def runtime_contract():
    return case_runtime_contract(
        case_program_installed_path=INSTALLED_CASE_PROGRAM,
        case_program_sha256=CASE_PROGRAM_DIGEST,
    )


#: Every contract compared against a strict policy: the runtime preflight and
#: all eight identities. Named rather than built at import, because `E7`'s
#: contract cannot be constructed until the autouse fixture supplies its
#: reviewed target facts — which ship unconfirmed, and stay that way.
CONTRACT_IDS = ["case-runtime", *sorted(CAPSH_CONSTRUCTED_IDENTITIES), ROOT_IDENTITY]


def contract_named(name: str):
    if name == "case-runtime":
        return runtime_contract()
    if name == ROOT_IDENTITY:
        return root_identity_contract()
    return identity_contract_for(name)


def contracts():
    for name in CONTRACT_IDS:
        yield name, contract_named(name)


@pytest.mark.parametrize("name", CONTRACT_IDS)
def test_the_valid_observation_is_still_accepted_through_the_capture_boundary(
    name: str,
) -> None:
    """The positive control, and it is load-bearing.

    Without it every negative below would be satisfied by a boundary that
    refused everything, which would be a different defect and not a fix.
    """
    contract = contract_named(name)
    observed = sanitize(contract.policy, emitted(contract))
    assert contract.check(observed) == "", (name, observed)


@pytest.mark.parametrize("name", CONTRACT_IDS)
def test_an_unexpected_key_in_real_output_is_refused(name: str) -> None:
    """**PR-20260907-3, case 2.** Accepted before this correction."""
    contract = contract_named(name)
    observed = sanitize(contract.policy, emitted(contract) + UNEXPECTED_LINE + "\n")

    assert contract.check(observed) == UNEXPECTED_KEY, (name, observed)
    assert UNEXPECTED_KEY_MARKER in observed
    # The line's own text never reaches the artifact.
    flat = " ".join(f"{key}={value}" for key, value in observed)
    assert "unexpected_key" not in flat.replace(UNEXPECTED_KEY_MARKER[0], "")
    assert "unexpected_value" not in flat


@pytest.mark.parametrize("name", CONTRACT_IDS)
def test_a_malformed_line_in_real_output_is_refused(name: str) -> None:
    """**PR-20260907-3, case 3.** Accepted before this correction."""
    contract = contract_named(name)
    observed = sanitize(contract.policy, emitted(contract) + MALFORMED_LINE + "\n")

    assert contract.check(observed) == UNEXPECTED_KEY, (name, observed)
    assert MALFORMED_LINE_MARKER in observed
    flat = " ".join(f"{key}={value}" for key, value in observed)
    assert "malformed-output-line" not in flat


@pytest.mark.parametrize("name", CONTRACT_IDS)
def test_both_defects_together_are_refused(name: str) -> None:
    contract = contract_named(name)
    text = emitted(contract) + UNEXPECTED_LINE + "\n" + MALFORMED_LINE + "\n"
    observed = sanitize(contract.policy, text)

    assert contract.check(observed) == UNEXPECTED_KEY, name
    assert UNEXPECTED_KEY_MARKER in observed
    assert MALFORMED_LINE_MARKER in observed


def test_a_hostile_line_carrying_a_secret_is_refused_and_never_recorded() -> None:
    """The reason the marker carries no text at all.

    A skipped line was invisible; a *recorded* line would be an artifact
    containing whatever the process printed. The marker is neither.
    """
    contract = runtime_contract()
    text = emitted(contract) + "password=hunter2 host=10.0.0.1\n"
    observed = sanitize(contract.policy, text)

    assert contract.check(observed) == UNEXPECTED_KEY
    flat = " ".join(f"{key}={value}" for key, value in observed)
    assert "hunter2" not in flat
    assert "10.0.0.1" not in flat
    assert "password" not in flat


def test_many_hostile_lines_cannot_push_the_marker_out_of_the_bounded_capture() -> None:
    """`sanitize` truncates to `MAX_OBSERVATIONS`. If the markers were appended
    they could be truncated away by a flood, and the flood would be accepted."""
    contract = runtime_contract()
    text = emitted(contract) + "".join(f"noise{n}=x\n" for n in range(200))
    observed = sanitize(contract.policy, text)

    assert UNEXPECTED_KEY_MARKER in observed
    assert contract.check(observed) == UNEXPECTED_KEY


# ---------------------------------------------------------------------------
# Blank lines, line termination, and the policies that are deliberately unchanged
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text_builder",
    [
        pytest.param(lambda body: body, id="trailing newline"),
        pytest.param(lambda body: body.rstrip("\n"), id="no trailing newline"),
        pytest.param(lambda body: "\n" + body, id="leading blank line"),
        pytest.param(lambda body: body + "\n\n\n", id="trailing blank lines"),
        pytest.param(
            lambda body: body.replace("\n", "\n   \n", 1), id="whitespace-only line"
        ),
        pytest.param(lambda body: body.replace("\n", "\r\n"), id="CRLF"),
    ],
)
def test_blank_and_whitespace_only_lines_are_ignored(text_builder) -> None:
    """**The stated blank-line policy.** A line that is empty or entirely
    whitespace is line termination, not a record, and is ignored. Every other
    non-blank line must be `key=value` with a reviewed key.

    CRLF is included because `_clean` collapses whitespace runs, so a carriage
    return is not a malformed record — it is the same record with a different
    terminator.
    """
    contract = runtime_contract()
    observed = sanitize(contract.policy, text_builder(emitted(contract)))
    assert contract.check(observed) == "", observed


def test_case_result_and_unit_directives_are_deliberately_unchanged() -> None:
    """They share the parser and are not compared against a closed contract.

    Broadening them because of that shared function would change behaviour
    nobody reviewed, so the strict set is enumerated and asserted.
    """
    assert STRICT_CASE_POLICIES == frozenset(
        {CapturePolicy.CASE_IDENTITY, CapturePolicy.CASE_RUNTIME}
    )
    lenient = sanitize(
        CapturePolicy.CASE_RESULT,
        "verb=open\nresult=returned\nunexpected_key=value\nmalformed-line\n",
    )
    assert dict(lenient) == {"verb": "open", "result": "returned"}
    assert UNEXPECTED_KEY_MARKER not in lenient
    assert MALFORMED_LINE_MARKER not in lenient


def test_the_markers_are_outside_every_contracts_reviewed_key_set() -> None:
    """Which is what makes them a refusal rather than a comparison."""
    for name, contract in contracts():
        assert UNEXPECTED_KEY_MARKER[0] not in contract.keys, name
        assert MALFORMED_LINE_MARKER[0] not in contract.keys, name


def test_duplicate_keys_and_value_shapes_still_refuse_as_before() -> None:
    """The corrections R12 made are preserved, not replaced.

    A **repeated** key does not reach `check()` twice: R12's capture boundary
    marks it `unreadable` in place, so the classification is `UNREADABLE_VALUE`
    naming that key rather than `DUPLICATED_KEY`. `DUPLICATED_KEY` remains the
    classification for a pair list that carries one key twice, which is a shape
    the boundary does not produce and `check()` still refuses — it is asserted
    against `check()` directly in `test_expectations.py`. Both are preserved
    here as refusals; neither is replaced by the new markers.
    """
    contract = identity_contract_for("E1")
    duplicated = sanitize(contract.policy, emitted(contract) + "uid=5002\n")
    refusal = contract.check(duplicated)
    assert refusal.startswith(UNREADABLE_VALUE) and "uid" in refusal
    assert UNEXPECTED_KEY_MARKER not in duplicated
    assert MALFORMED_LINE_MARKER not in duplicated

    body = emitted(contract).replace("cap_bnd=0", "cap_bnd=not-a-mask")
    misshapen = sanitize(contract.policy, body)
    assert contract.check(misshapen).startswith(UNREADABLE_VALUE)

    # And a genuinely duplicated **pair list** is still `DUPLICATED_KEY`.
    assert contract.check(
        tuple(dict(sanitize(contract.policy, emitted(contract))).items())
        + (("uid", "5002"),)
    ).startswith(DUPLICATED_KEY)


# ---------------------------------------------------------------------------
# The executor: raw output → capture → the run stops
# ---------------------------------------------------------------------------


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
    """A recording boundary that **sanitizes** its scripted raw output.

    That is the point of this class: the fake boundaries elsewhere in the suite
    script an already-sanitized observation tuple, which is exactly the shortcut
    that let PR-20260907-3 survive. Here the scripted value is the text a process
    would print, and it goes through `capture.sanitize` under the step's own
    policy — the same call `execution/boundary.py` makes.
    """

    raw: dict = field(default_factory=dict)
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
        if step_id in self.raw:
            return CommandResult(
                exit_status=0,
                timed_out=False,
                observations=sanitize(capture, self.raw[step_id]),
            )
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


def raw_for(step, plan) -> str:
    """The text a compliant case program would print for one step."""
    from tools.phase_5_0_evidence.expectations import contract_for

    contract = contract_for(
        capture=step.capture,
        identity_name=step.identity_name,
        argv=bound_argv(step),
        case_program_installed_path=INSTALLED_CASE_PROGRAM,
        case_program_sha256=CASE_PROGRAM_DIGEST,
    )
    assert contract is not None
    return emitted(contract)


def test_the_whole_plan_runs_when_every_observation_is_real_sanitized_output() -> None:
    """The positive control for the executor half: the compliant text passes
    through `capture.sanitize` and satisfies every contract."""
    plan = runnable_plan()
    boundary = satisfying(plan)
    for step in plan.steps:
        if step.capture in STRICT_CASE_POLICIES:
            boundary.raw[step.step_id] = raw_for(step, plan)

    outcome = runner(plan, boundary).execute()
    assert outcome.completed, outcome.stop_reason
    assert outcome.cleanup.state == "S-C"


@pytest.mark.parametrize("extra", [UNEXPECTED_LINE, MALFORMED_LINE])
@pytest.mark.parametrize("step_id", ["P-05", "P-06", "B5-E1"])
def test_a_defective_observation_stops_the_run_at_that_step(
    step_id: str, extra: str
) -> None:
    """**PR-20260907-3 item 5.** Unsatisfied, and nothing after it is reached.

    The observation is produced by sanitizing raw text, so this is the complete
    path a real run takes and not an injected tuple.
    """
    plan = runnable_plan()
    boundary = satisfying(plan)
    step = next(item for item in plan.steps if item.step_id == step_id)
    boundary.raw[step_id] = raw_for(step, plan) + extra + "\n"

    outcome = runner(plan, boundary).execute()

    assert outcome.stopped_at == step_id, outcome.stop_reason
    assert UNEXPECTED_KEY in outcome.stop_reason
    recorded = {item.step_id: item for item in outcome.steps}[step_id]
    assert recorded.exit_status == 0 and not recorded.satisfied
    assert not outcome.artifact_admissible

    order = [item.step_id for item in plan.steps]
    after = set(order[order.index(step_id) + 1 :])
    assert not (set(boundary.calls) & after), sorted(set(boundary.calls) & after)
    assert {item.step_id for item in outcome.steps} & after == set()


def test_cleanup_still_runs_for_mutations_already_reached() -> None:
    """**PR-20260907-3 item 5, second half.** The refusal must not change what
    the run is responsible for removing."""
    plan = runnable_plan()
    boundary = satisfying(plan)
    step_id = "B5-E1"
    step = next(item for item in plan.steps if item.step_id == step_id)
    boundary.raw[step_id] = raw_for(step, plan) + MALFORMED_LINE + "\n"

    outcome = runner(plan, boundary).execute()

    assert outcome.stopped_at == step_id
    # Band 2 created accounts and groups long before this step, so cleanup has
    # real work and it ran: the state machine reports S-A, "a stage failed or
    # was inconclusive and cleanup completed".
    assert outcome.cleanup.state == "S-A", outcome.cleanup
    assert not outcome.cleanup.residue
