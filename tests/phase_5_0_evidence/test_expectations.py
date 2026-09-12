"""**R12 — the semantic expectations, and the enforcement point.**

Codex's R11 review returned two Blocking findings, and both had the same shape:
the harness produced an observation, sanitized it, stored it, and then decided
the step was satisfied from its **exit status alone**.

* **EH-R11-1.** `P-05` — the interpreter preflight — could report a different
  interpreter, a different executable digest, `isolated=no`, an importable
  third-party `sys.path` or a case program whose installed bytes were not the
  reviewed ones, and the run recorded a pass and carried on into every dependent
  case.
* **EH-R11-2.** The identities were the same: exit 0 and the presence of a
  `capsh --secbits=` option stood in for *"the process that ran the operation
  actually had this identity"*, and securebits — which the kernel reports
  through `prctl(2)` and through no file — was never read at all.

This module is the regression suite for both. It has three parts:

1. **the contract**, exercised directly, key by key and refusal by refusal;
2. **the executor**, exercised across an injected boundary, proving the
   comparison happens on the `CommandResult` the executor actually receives,
   before satisfaction is decided, and that a mismatch stops the run before any
   dependent case reaches the boundary; and
3. **the reviewed values themselves** — that the contracts' key sets are exactly
   the capture policies' key sets, that every `capsh`-constructed identity's
   securebits is the value §2.13.5c derives, and that neither expectation can be
   learned from the observation it judges.

**This module exercises the seven `capsh`-constructed identities.** `E7` — the
harness's own root identity, which R12 excluded from the contract altogether —
is `tests/phase_5_0_evidence/test_root_identity.py`, R13's disposition of
Blocking finding **EH-R12-1**. Between them the two modules cover all eight.

**Nothing here starts a process, reads a host account or touches a file.**
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pytest

from tools.phase_5_0_evidence import case_runtime
from tools.phase_5_0_evidence.approved_target import (
    APPROVED_TARGET,
    CONFIRMATION_TOKEN,
)
from tools.phase_5_0_evidence.capability import (
    EVIDENCE_IDENTITIES,
    SECBITS_NO_SETUID_FIXUP,
)
from tools.phase_5_0_evidence.capture import (
    VARIABLE_KEY_POLICIES,
    CapturePolicy,
    sanitize,
)
from tools.phase_5_0_evidence.case_runtime import (
    CASE_PROGRAM_SOURCE,
    case_program_path,
)
from tools.phase_5_0_evidence.concrete_plan import ConcretePlan, build_concrete_plan
from tools.phase_5_0_evidence.errors import PlanRefused
from tools.phase_5_0_evidence.execution.boundary import CommandResult, IdentityAbsent
from tools.phase_5_0_evidence.execution.executor import ExecutingRunner
from tools.phase_5_0_evidence.execution.materializer import MaterializationResult
from tools.phase_5_0_evidence.expectations import (
    DERIVED_CONTRACT_POLICIES,
    capture_policy_keys,
    CAPSH_CONSTRUCTED_IDENTITIES,
    OBSERVED_IDENTITIES,
    DUPLICATED_KEY,
    EXPECTATION_NOT_CONSTRUCTED,
    MALFORMED_OBSERVATIONS,
    MISSING_KEY,
    NO_OBSERVATIONS,
    UNEQUAL_VALUE,
    UNEXPECTED_KEY,
    UNREADABLE_VALUE,
    Comparison,
    Expectation,
    ObservationContract,
    case_runtime_contract,
    constructed_identity_contract,
    contract_for,
    identity_numbers,
)
from tools.phase_5_0_evidence.plan import OBSERVED_IDENTITY, CommandStep
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.harness_fixtures import (
    cleanup_observations_for,
    DISPOSABLE_ACCOUNTS,
    DISPOSABLE_GROUPS,
    bound_argv,
    observations_for,
    runnable_plan,
    supply_reviewed_e7_facts,
)

SOURCES = {name: f"# {name}\n".encode("utf-8") for name in COVERED_SOURCES}

#: The repository root, for the two source-level assertions below.
SOURCE_ROOT = Path(__file__).resolve().parents[2]

#: Stand-ins for the two reviewed target facts, which ship unconfirmed. Both are
#: obviously synthetic: nothing in this file resolves, hashes or starts a real
#: interpreter.
REVIEWED_INTERPRETER_DIGEST = "5" * 64
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"

#: The expected case-program digest, taken the way the executor takes it: from
#: the review manifest's covered-source entry for the reviewed source.
CASE_PROGRAM_DIGEST = ReviewManifest.build(
    build_concrete_plan(), SOURCES
).digest_for(CASE_PROGRAM_SOURCE)

INSTALLED_CASE_PROGRAM = case_program_path(APPROVED_TARGET)


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


def runtime_contract() -> ObservationContract:
    return case_runtime_contract(
        case_program_installed_path=INSTALLED_CASE_PROGRAM,
        case_program_sha256=CASE_PROGRAM_DIGEST,
    )


def runtime_observation(**overrides) -> tuple[tuple[str, str], ...]:
    """The exact complete `P-05` observation, with named keys replaced.

    A key given `None` is **removed**, which is how the missing-key cases are
    written without spelling the other ten out each time.
    """
    values = dict(runtime_contract().expected_observations())
    for key, value in overrides.items():
        if value is None:
            values.pop(key, None)
        else:
            values[key] = value
    return tuple(sorted(values.items()))


# ---------------------------------------------------------------------------
# EH-R11-1 — the contract itself
# ---------------------------------------------------------------------------


def test_the_exact_complete_observation_satisfies_the_contract() -> None:
    assert runtime_contract().check(runtime_observation()) == ""


def test_the_contract_covers_exactly_the_capture_policys_key_set() -> None:
    """The contract and the capture policy are two halves of one thing.

    A key the policy records and the contract does not compare would be an
    observation nobody reads; a key the contract requires and the policy cannot
    record would be an expectation nothing can satisfy. Both are refused by
    keeping the two sets equal, and this is what would fail on the day either is
    edited alone.
    """
    from tools.phase_5_0_evidence.capture import _KEY_VALUE_KEYS

    assert set(runtime_contract().keys) == set(
        _KEY_VALUE_KEYS[CapturePolicy.CASE_RUNTIME]
    )
    for name in sorted(CAPSH_CONSTRUCTED_IDENTITIES):
        contract = constructed_identity_contract(
            name, uid=5002, gid=5002, group_ids=frozenset({5002, 5004})
        )
        assert set(contract.keys) == set(
            _KEY_VALUE_KEYS[CapturePolicy.CASE_IDENTITY]
        )


def test_no_observation_at_all_is_refused() -> None:
    assert runtime_contract().check(()) == NO_OBSERVATIONS


@pytest.mark.parametrize("key", sorted(runtime_contract().keys))
def test_one_missing_key_is_refused(key: str) -> None:
    refusal = runtime_contract().check(runtime_observation(**{key: None}))
    assert refusal.startswith(MISSING_KEY)
    assert key in refusal


@pytest.mark.parametrize("key", sorted(runtime_contract().keys))
def test_a_duplicated_key_is_refused(key: str) -> None:
    """Two values for one fact is not a correction the harness may apply."""
    observation = runtime_observation()
    duplicated = observation + ((key, dict(observation)[key]),)
    refusal = runtime_contract().check(duplicated)
    assert refusal.startswith(DUPLICATED_KEY)
    assert key in refusal


@pytest.mark.parametrize("key", sorted(runtime_contract().keys))
def test_an_unreadable_value_is_refused(key: str) -> None:
    """`unreadable` is what the capture boundary writes for a value that is not
    the shape its field can legitimately have. It is an INCONCLUSIVE observation
    and never a comparable one."""
    refusal = runtime_contract().check(runtime_observation(**{key: "unreadable"}))
    assert refusal.startswith(UNREADABLE_VALUE)
    assert key in refusal


@pytest.mark.parametrize("key", sorted(runtime_contract().keys))
def test_an_empty_value_is_refused(key: str) -> None:
    refusal = runtime_contract().check(runtime_observation(**{key: ""}))
    assert refusal.startswith(UNREADABLE_VALUE)


def test_a_key_outside_the_reviewed_set_is_refused() -> None:
    extra = runtime_observation() + (("something_else", "yes"),)
    assert runtime_contract().check(extra) == UNEXPECTED_KEY


def test_the_capture_boundarys_own_refusal_markers_are_refused() -> None:
    """Unparseable output reaches the contract as a marker carrying no reviewed
    key, and is refused.

    **Updated by PR-20260907-3.** `"this is not key=value output"` does contain
    an `=`, so it parses as a *record with an unexpected name*, and a strict
    policy now says so instead of dropping it. Output with no `=` at all reaches
    the malformed marker. The classification is `UNEXPECTED_KEY` for both,
    because neither marker key is in any reviewed key set — which is the
    property that makes them a refusal.
    """
    named = sanitize(CapturePolicy.CASE_RUNTIME, "this is not key=value output")
    assert named == (("capture_unexpected_key", "refused"),)
    assert runtime_contract().check(named) == UNEXPECTED_KEY

    unnamed = sanitize(CapturePolicy.CASE_RUNTIME, "no separator here at all")
    assert unnamed == (("capture_malformed_line", "refused"),)
    assert runtime_contract().check(unnamed) == UNEXPECTED_KEY

    # Output with nothing in it at all is still the parse marker.
    assert sanitize(CapturePolicy.CASE_RUNTIME, "\n   \n") == (
        ("parse", "unreadable"),
    )


@pytest.mark.parametrize("observations", [None, "verb=runtime", 7, [["verb"]]])
def test_a_malformed_observation_structure_is_refused(observations) -> None:
    assert runtime_contract().check(observations) in (
        MALFORMED_OBSERVATIONS,
        NO_OBSERVATIONS,
    )


@pytest.mark.parametrize(
    ("key", "wrong"),
    [
        ("verb", "identity"),
        ("result", "refused"),
        ("interpreter", "/usr/bin/python3"),
        ("interpreter_real", "/usr/bin/python3.12"),
        ("python_version", "3.11"),
        ("interpreter_sha256", "6" * 64),
        ("isolated", "no"),
        ("no_site", "no"),
        ("third_party_importable", "yes"),
        ("case_program", "/var/lib/fb-evidence-p5-0/bin/other"),
        ("case_program_sha256", "a" * 64),
    ],
)
def test_every_wrong_value_is_refused(key: str, wrong: str) -> None:
    """One case per key of the preflight, and the wrong value for each is the one
    the finding names: another interpreter, another resolved path, another
    version, another executable digest, isolation that did not take effect, an
    importable third-party distribution, another installed program and another
    installed digest."""
    refusal = runtime_contract().check(runtime_observation(**{key: wrong}))
    assert refusal.startswith(UNEQUAL_VALUE)
    assert key in refusal


def test_no_refusal_names_an_observed_value() -> None:
    """The classification is fixed and names the **reviewed** key. It never names
    the value, the path, the digest or the identifier the host supplied."""
    secret = "/var/lib/fb-evidence-p5-0/bin/somewhere-else"
    refusal = runtime_contract().check(runtime_observation(case_program=secret))
    assert secret not in refusal
    assert "somewhere-else" not in refusal
    digest_refusal = runtime_contract().check(
        runtime_observation(interpreter_sha256="b" * 64)
    )
    assert "b" * 64 not in digest_refusal
    assert UNEXPECTED_KEY == runtime_contract().check(
        runtime_observation() + (("leaked_host_fact", "value"),)
    )
    assert "leaked_host_fact" not in UNEXPECTED_KEY


def test_the_expected_digest_is_never_learned_from_the_observation() -> None:
    """The expectation and the observation have different sources, and the
    contract will not accept a digest that is merely internally consistent."""
    observation = runtime_observation(interpreter_sha256="c" * 64)
    assert runtime_contract().check(observation).startswith(UNEQUAL_VALUE)
    # And an expectation that is not a reviewed digest cannot be constructed at
    # all, so a contract can never be built around whatever a run reported.
    with pytest.raises(PlanRefused):
        case_runtime_contract(
            case_program_installed_path=INSTALLED_CASE_PROGRAM,
            case_program_sha256="not-a-digest",
        )
    with pytest.raises(PlanRefused):
        case_runtime_contract(
            case_program_installed_path="bin/case",
            case_program_sha256=CASE_PROGRAM_DIGEST,
        )


def test_an_unconfirmed_reviewed_fact_can_never_be_matched() -> None:
    """The shipped tree carries the sentinel, and no observation can equal it.

    The executor refuses before it starts anything while either interpreter fact
    is unconfirmed, and this is the second line: `UNCONFIRMED` is not the shape
    the capture boundary admits for a digest, so a sanitized observation carrying
    it is `unreadable` — and `unreadable` is a refusal. A run that somehow got
    past the gate could still never record the preflight as a pass.
    """
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            case_runtime,
            "EXPECTED_INTERPRETER_SHA256",
            case_runtime.INTERPRETER_DIGEST_UNCONFIRMED,
        )
        contract = runtime_contract()
        observed = dict(
            sanitize(
                CapturePolicy.CASE_RUNTIME,
                "interpreter_sha256=UNCONFIRMED\n",
            )
        )
        assert observed["interpreter_sha256"] == "unreadable"
        assert contract.check(
            runtime_observation(interpreter_sha256="unreadable")
        ).startswith(UNREADABLE_VALUE)
        # And a real digest does not equal the sentinel either.
        assert contract.check(
            runtime_observation(interpreter_sha256=REVIEWED_INTERPRETER_DIGEST)
        ).startswith(UNEQUAL_VALUE)


def test_both_shipped_interpreter_facts_are_unconfirmed_in_the_source() -> None:
    """Asserted against the source, because the autouse fixture supplies both for
    every other test in this module — and because the whole point of R12's second
    reviewed fact is that this tree does not have it."""
    source = SOURCE_ROOT.joinpath(
        "tools", "phase_5_0_evidence", "case_runtime.py"
    ).read_text(encoding="utf-8")
    assert "EXPECTED_INTERPRETER_SHA256 = INTERPRETER_DIGEST_UNCONFIRMED" in source
    assert (
        "EXPECTED_INTERPRETER_REAL_PATH = INTERPRETER_REAL_PATH_UNCONFIRMED" in source
    )


# ---------------------------------------------------------------------------
# EH-R11-2 — the identity contract
# ---------------------------------------------------------------------------


def identity_observation(name: str, **overrides) -> tuple[tuple[str, str], ...]:
    identity = EVIDENCE_IDENTITIES[name]
    group_names = (identity.primary_group, *identity.supplementary_groups)
    contract = constructed_identity_contract(
        name,
        uid=DISPOSABLE_ACCOUNTS[identity.user][0],
        gid=DISPOSABLE_GROUPS[identity.primary_group],
        group_ids=frozenset(DISPOSABLE_GROUPS[group] for group in group_names),
    )
    values = dict(contract.expected_observations())
    for key, value in overrides.items():
        if value is None:
            values.pop(key, None)
        else:
            values[key] = value
    return contract, tuple(sorted(values.items()))


@pytest.mark.parametrize("name", sorted(CAPSH_CONSTRUCTED_IDENTITIES))
def test_the_exact_identity_observation_satisfies_its_contract(name: str) -> None:
    contract, observation = identity_observation(name)
    assert contract.check(observation) == ""


@pytest.mark.parametrize("name", sorted(CAPSH_CONSTRUCTED_IDENTITIES))
def test_every_identitys_expected_securebits_is_the_derived_value(name: str) -> None:
    """§2.13.5c step 1 sets `SECBIT_NO_SETUID_FIXUP` and clears every other
    securebit, and step 7's `execve` preserves it. Every constructed identity
    therefore expects `0x4`, and the contract carries that value rather than
    inferring it from the `--secbits=` option in the vector."""
    contract, _ = identity_observation(name)
    securebits = {
        expectation.key: expectation for expectation in contract.expectations
    }["securebits"]
    assert securebits.comparison is Comparison.HEX
    assert securebits.expected == SECBITS_NO_SETUID_FIXUP == 4
    assert securebits.canonical == "4"


def test_e7_has_a_contract_of_its_own_and_not_the_constructed_one() -> None:
    """**EH-R12-1.** `E7` is observed like the other seven and its expectation
    comes from a different — and equally independent — source.

    It is not a `capsh` construct, so `constructed_identity_contract` refuses it:
    there is no `--uid=` to read and no `M` to derive from. It is not
    *unobservable*, which is what R12 concluded from the same premise. The full
    `E7` contract is exercised in `test_root_identity.py`."""
    assert "E7" in OBSERVED_IDENTITIES
    assert "E7" not in CAPSH_CONSTRUCTED_IDENTITIES
    with pytest.raises(PlanRefused):
        constructed_identity_contract("E7", uid=0, gid=0, group_ids=frozenset({0}))
    with pytest.raises(PlanRefused):
        constructed_identity_contract("E9", uid=1, gid=1, group_ids=frozenset({1}))


@pytest.mark.parametrize(
    ("key", "wrong"),
    [
        ("verb", "runtime"),
        ("result", "unobserved"),
        ("uid", "0"),
        ("gid", "0"),
        ("groups", "5002"),
        ("cap_inh", "ffffffff"),
        ("cap_prm", "ffffffff"),
        ("cap_eff", "ffffffff"),
        ("cap_bnd", "ffffffff"),
        ("cap_amb", "ffffffff"),
        ("no_new_privs", "1"),
        ("securebits", "0"),
    ],
)
def test_one_mismatch_in_each_identity_field_category_is_refused(
    key: str, wrong: str
) -> None:
    """Every field category the finding names: the numeric credentials, the
    complete supplementary set, each of the five capability masks, `NoNewPrivs`
    and the securebits."""
    contract, observation = identity_observation("E5", **{key: wrong})
    refusal = contract.check(observation)
    assert refusal.startswith(UNEQUAL_VALUE)
    assert key in refusal


@pytest.mark.parametrize("key", ["securebits", "no_new_privs", "cap_bnd", "groups"])
def test_a_missing_or_unreadable_identity_value_is_refused(key: str) -> None:
    contract, missing = identity_observation("E5", **{key: None})
    assert contract.check(missing).startswith(MISSING_KEY)
    contract, unreadable = identity_observation("E5", **{key: "unreadable"})
    assert contract.check(unreadable).startswith(UNREADABLE_VALUE)


def test_a_malformed_securebits_capture_is_refused_by_the_capture_boundary() -> None:
    """The shape is two hexadecimal digits at most. A sixteen-digit value, a
    negative one and a decorated one are each `unreadable` before the contract
    ever sees them, and the contract refuses `unreadable`."""
    for malformed in ("0000000000000004", "-4", "0x4", "zz", "4 4"):
        observed = dict(
            sanitize(
                CapturePolicy.CASE_IDENTITY,
                f"verb=identity\nresult=returned\nsecurebits={malformed}\n",
            )
        )
        assert observed["securebits"] == "unreadable", malformed


def test_a_leading_zero_securebits_still_compares_by_value() -> None:
    """`04` and `4` are the same securebits word. The comparison is numeric, so
    a zero-padded value is not a spurious mismatch — and `40` still is one."""
    contract, padded = identity_observation("E5", securebits="04")
    assert contract.check(padded) == ""
    contract, wrong = identity_observation("E5", securebits="40")
    assert contract.check(wrong).startswith(UNEQUAL_VALUE)


def test_the_supplementary_groups_compare_as_a_set() -> None:
    """The kernel holds a set; recording the order would compare something
    §2.13.5c does not state."""
    contract, observation = identity_observation("E1")
    values = dict(observation)
    reversed_order = ",".join(reversed(values["groups"].split(",")))
    assert contract.check(tuple(sorted({**values, "groups": reversed_order}.items()))) == ""
    assert (
        contract.check(
            tuple(sorted({**values, "groups": values["groups"] + ",99"}.items()))
        ).startswith(UNEQUAL_VALUE)
    )


def test_the_identity_numbers_come_from_the_bound_vector_and_are_required() -> None:
    """The expectation's uid, gid and group set are the numbers the vector asked
    the kernel for — an independent source from the observation, and the only one
    available, because the four names do not exist until Band 2 creates them."""
    uid, gid, groups = identity_numbers(
        ("/usr/sbin/capsh", "--gid=5002", "--groups=5002,5004", "--uid=5002")
    )
    assert (uid, gid, groups) == (5002, 5002, frozenset({5002, 5004}))
    for broken in (
        ("/usr/sbin/capsh", "--gid=5002", "--groups=5002"),
        ("/usr/sbin/capsh", "--gid=5002", "--groups=5002", "--uid=5002", "--uid=0"),
        ("/usr/sbin/capsh", "--gid=x", "--groups=5002", "--uid=5002"),
        ("/usr/sbin/capsh", "--gid=5002", "--groups=root", "--uid=5002"),
    ):
        with pytest.raises(PlanRefused):
            identity_numbers(broken)


# ---------------------------------------------------------------------------
# The plan carries the pairing, and the shapes agree
# ---------------------------------------------------------------------------


def test_the_plans_identity_steps_name_the_identity_they_observe() -> None:
    plan = build_concrete_plan()
    named = {
        step.identity_name
        for step in plan.steps
        if step.capture is CapturePolicy.CASE_IDENTITY
    }
    assert named == OBSERVED_IDENTITIES
    for step in plan.steps:
        if step.capture is not CapturePolicy.CASE_IDENTITY:
            assert step.identity_name == ""


def test_a_step_that_observes_an_identity_must_name_one() -> None:
    with pytest.raises(PlanRefused):
        CommandStep(
            step_id="X",
            band="capability",
            run_as="root",
            argv=("/usr/bin/id",),
            purpose="p",
            capture=CapturePolicy.CASE_IDENTITY,
        )
    with pytest.raises(PlanRefused):
        CommandStep(
            step_id="X",
            band="capability",
            run_as="root",
            argv=("/usr/bin/id",),
            purpose="p",
            capture=CapturePolicy.CASE_IDENTITY,
            identity_name="E9",
        )
    with pytest.raises(PlanRefused):
        CommandStep(
            step_id="X",
            band="capability",
            run_as="root",
            argv=("/usr/bin/id",),
            purpose="p",
            identity_name="E1",
        )


def test_the_planners_identity_shape_and_the_derived_set_agree() -> None:
    for name in sorted(EVIDENCE_IDENTITIES):
        assert bool(OBSERVED_IDENTITY.match(name)) == (
            name in OBSERVED_IDENTITIES
        )


def test_only_the_exit_status_policy_selects_no_contract() -> None:
    """**R13, EH-R13-3.** This test asserted the defect.

    Its previous form required `contract_for` to return `None` for every policy
    but the two case-program observation verbs — that is, it required nine
    policies that record an observation to be compared against nothing, which is
    exactly the Blocking finding. Only `EXIT_STATUS_ONLY` records nothing, and
    only `EXIT_STATUS_ONLY` may select no contract; a policy that records an
    observation and is handed no declaration **raises**, and the executor turns
    that into `EXPECTATION_NOT_CONSTRUCTED` rather than into a pass.
    """
    assert (
        contract_for(
            capture=CapturePolicy.EXIT_STATUS_ONLY,
            identity_name="",
            argv=("/usr/bin/id",),
            case_program_installed_path=INSTALLED_CASE_PROGRAM,
            case_program_sha256=CASE_PROGRAM_DIGEST,
        )
        is None
    )
    for policy in CapturePolicy:
        if policy is CapturePolicy.EXIT_STATUS_ONLY:
            continue
        if policy in DERIVED_CONTRACT_POLICIES:
            continue
        with pytest.raises(PlanRefused):
            contract_for(
                capture=policy,
                identity_name="",
                argv=("/usr/bin/id",),
                case_program_installed_path=INSTALLED_CASE_PROGRAM,
                case_program_sha256=CASE_PROGRAM_DIGEST,
            )


def test_every_observation_bearing_step_in_the_plan_carries_a_contract() -> None:
    """The completeness half of EH-R13-3, over the generated plan itself."""
    plan = build_concrete_plan()
    uncompared = [
        step.step_id
        for step in plan.steps
        if step.capture is not CapturePolicy.EXIT_STATUS_ONLY
        and step.capture not in DERIVED_CONTRACT_POLICIES
        and not step.observation_expectations
    ]
    assert uncompared == []
    for step in plan.steps:
        if step.capture is CapturePolicy.EXIT_STATUS_ONLY:
            assert step.observation_expectations == ()


def test_a_declared_contract_covers_every_key_its_policy_emits() -> None:
    """A declaration that omits an emitted key cannot be built.

    Without this, a step could declare four of five keys, the fifth would reach
    the artifact uncompared, and `check()` would refuse the observation for
    carrying an *unexpected* key rather than for the reason a reviewer cares
    about.
    """
    plan = build_concrete_plan()
    for step in plan.steps:
        if not step.observation_expectations:
            continue
        declared = {item.key for item in step.observation_expectations}
        emitted = capture_policy_keys(step.capture)
        if step.capture in VARIABLE_KEY_POLICIES:
            assert declared <= emitted, step.step_id
        else:
            assert declared == emitted, step.step_id


def test_a_value_that_is_not_compared_says_why() -> None:
    """The two shape-only comparisons are enumerated, with their stated reason.

    They exist for run-time-allocated numeric ids and for sizes that depend on
    what a disposable file holds when the operation runs. Enumerating them here
    is what keeps *"not compared"* from becoming a quiet way of not writing an
    expectation down.
    """
    plan = build_concrete_plan()
    uncompared = [
        (step.step_id, item.key, item.uncompared_because)
        for step in plan.steps
        for item in step.observation_expectations
        if item.comparison
        in (Comparison.NUMBER_PRESENT, Comparison.TEXT_PRESENT)
    ]
    assert uncompared, "the enumeration is meaningless if it is empty"
    for step_id, key, reason in uncompared:
        assert reason.strip(), f"{step_id}.{key}"
    keys = {key for _, key, _ in uncompared}
    assert keys <= {
        "uid",
        "gid",
        "groups",
        "bytes_written",
        "pre_size",
        "post_size",
        # **R16, conflict C-8.** The device and inode of the directory the
        # exclusive creation made. The kernel allocates them, so no plan can
        # state them — and they are not uncompared in the sense that matters:
        # cleanup reads them back and the executor compares the two
        # observations with each other before it removes anything.
        "root_device",
        "root_inode",
    }, sorted(keys)


def test_a_contract_that_declares_nothing_cannot_exist() -> None:
    with pytest.raises(PlanRefused):
        ObservationContract(
            policy=CapturePolicy.CASE_RUNTIME, subject="empty", expectations=()
        )
    with pytest.raises(PlanRefused):
        ObservationContract(
            policy=CapturePolicy.CASE_RUNTIME,
            subject="twice",
            expectations=(
                Expectation("verb", Comparison.TEXT, "runtime"),
                Expectation("verb", Comparison.TEXT, "identity"),
            ),
        )


# ---------------------------------------------------------------------------
# The executor: where the comparison happens, and what it stops
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
    scripted: dict = field(default_factory=dict)
    calls: list = field(default_factory=list)

    def run(self, *, step_id, argv, run_as, capture, timeout_seconds, catalog=None):
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
    )


def outcome_for(step_id: str, replacement: CommandResult):
    """Run the whole reviewed plan with one step's result replaced."""
    plan = runnable_plan()
    boundary = satisfying(plan)
    boundary.scripted[step_id] = replacement
    return plan, boundary, runner(plan, boundary).execute()


def test_the_whole_plan_runs_when_every_observation_matches() -> None:
    plan = runnable_plan()
    boundary = satisfying(plan)
    outcome = runner(plan, boundary).execute()
    assert outcome.completed, outcome.stop_reason
    assert outcome.cleanup.state == "S-C"
    assert all(step.satisfied for step in outcome.steps)


@pytest.mark.parametrize(
    ("label", "observations"),
    [
        ("no observations", ()),
        ("one missing key", runtime_observation(python_version=None)),
        (
            "a duplicate key",
            runtime_observation() + (("isolated", "yes"),),
        ),
        ("an unreadable value", runtime_observation(interpreter_sha256="unreadable")),
        ("a wrong interpreter path", runtime_observation(interpreter="/usr/bin/python3")),
        (
            "a wrong resolved path",
            runtime_observation(interpreter_real="/usr/bin/python3.12"),
        ),
        ("a wrong python version", runtime_observation(python_version="3.11")),
        ("a wrong interpreter digest", runtime_observation(interpreter_sha256="d" * 64)),
        ("isolated=no", runtime_observation(isolated="no")),
        ("no_site=no", runtime_observation(no_site="no")),
        (
            "third_party_importable=yes",
            runtime_observation(third_party_importable="yes"),
        ),
        (
            "a wrong case-program path",
            runtime_observation(case_program="/var/lib/fb-evidence-p5-0/bin/other"),
        ),
        ("a wrong case-program digest", runtime_observation(case_program_sha256="e" * 64)),
        ("an unexpected key", runtime_observation() + (("extra", "1"),)),
    ],
)
def test_p05_exiting_zero_is_not_a_pass(label: str, observations) -> None:
    """**EH-R11-1, end to end.** The preflight exits exactly as the reviewed plan
    requires, and the run still stops there — because the observation does not
    satisfy the reviewed contract."""
    plan, boundary, outcome = outcome_for(
        "P-05", CommandResult(exit_status=0, timed_out=False, observations=observations)
    )
    assert not outcome.completed, label
    assert outcome.stopped_at == "P-05", label
    assert "does not satisfy the reviewed expectation" in outcome.stop_reason, label
    recorded = {step.step_id: step for step in outcome.steps}["P-05"]
    assert recorded.exit_status == 0 and not recorded.satisfied, label
    assert not outcome.artifact_admissible, label


def test_no_dependent_case_reaches_the_boundary_after_a_preflight_mismatch() -> None:
    """The run stops at `P-05` itself: every later step is neither executed nor
    interpreted, and the boundary is never called for one."""
    plan, boundary, outcome = outcome_for(
        "P-05",
        CommandResult(
            exit_status=0, timed_out=False, observations=runtime_observation(isolated="no")
        ),
    )
    order = [step.step_id for step in plan.steps]
    after = set(order[order.index("P-05") + 1 :])
    executed = set(boundary.calls)
    assert not (executed & after), sorted(executed & after)
    assert {step.step_id for step in outcome.steps} & after == set()


@pytest.mark.parametrize("name", sorted(CAPSH_CONSTRUCTED_IDENTITIES))
def test_an_identity_mismatch_stops_the_run_before_its_dependent_operation(
    name: str,
) -> None:
    """**EH-R11-2, end to end.** The `capsh` construction exits 0, the identity
    observation disagrees in its securebits, and the run stops there: no case run
    under that identity is executed, and none is interpreted."""
    step_id = f"B5-{name}"
    _, observation = identity_observation(name, securebits="0")
    plan, boundary, outcome = outcome_for(
        step_id, CommandResult(exit_status=0, timed_out=False, observations=observation)
    )
    assert outcome.stopped_at == step_id
    assert "securebits" in outcome.stop_reason
    order = [step.step_id for step in plan.steps]
    after = set(order[order.index(step_id) + 1 :])
    assert not (set(boundary.calls) & after)
    assert not outcome.artifact_admissible


def test_an_identity_step_that_observed_nothing_is_not_satisfied() -> None:
    plan, boundary, outcome = outcome_for(
        "B5-E1", CommandResult(exit_status=0, timed_out=False, observations=())
    )
    assert outcome.stopped_at == "B5-E1"
    assert NO_OBSERVATIONS in outcome.stop_reason


def test_a_step_whose_contract_cannot_be_built_is_not_satisfied() -> None:
    """Fail-closed: no contract means no comparison, and no comparison means the
    step is not satisfied. The classification names nothing about the host."""
    plan = runnable_plan()
    boundary = satisfying(plan)

    class Broken(ExecutingRunner):
        def _bind(self, step):
            if step.step_id == "B5-E1":
                # A vector the identity contract cannot read numbers out of.
                return ("/usr/sbin/capsh", "--print"), ""
            return super()._bind(step)

    broken = Broken(
        plan=plan,
        boundary=boundary,
        reviewed_digest=ReviewManifest.build(plan, SOURCES).digest(),
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        materializer=Materializer(),
        identity_lookup=Lookup(),
    )
    outcome = broken.execute()
    assert outcome.stopped_at == "B5-E1"
    assert EXPECTATION_NOT_CONSTRUCTED in outcome.stop_reason


def test_the_comparison_uses_the_manifests_digest_not_the_installed_file() -> None:
    """The expected `case_program_sha256` is the review manifest's covered-source
    entry, so changing the reviewed bytes changes the expectation — and changes
    the manifest digest, which the executor already refuses to run without."""
    other = dict(SOURCES)
    other[CASE_PROGRAM_SOURCE] = b"# something else\n"
    plan = runnable_plan()
    boundary = satisfying(plan)
    changed = ExecutingRunner(
        plan=plan,
        boundary=boundary,
        reviewed_digest=ReviewManifest.build(plan, other).digest(),
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=other,
        materializer=Materializer(),
        identity_lookup=Lookup(),
    )
    outcome = changed.execute()
    assert outcome.stopped_at == "P-05"
    assert "case_program_sha256" in outcome.stop_reason
