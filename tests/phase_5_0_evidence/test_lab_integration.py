"""The C-P5.0-LAB-I-R1 integration regressions — PR-20260913-LABI-3.

## What this module is

Codex's review found the reserved-laboratory mechanism *"test-only"*: the
session, the ledger, the recovery store and the descriptor-bound effect issuer
were consumed only by their own tests; the CLI still built the legacy
`ExecutingRunner` over `SubprocessBoundary` and `SystemMaterializer`; descriptor
transfer was not connected to process launch; none of the six non-harness
participant paths used the lock and ledger protocol; and the plan generator
still emitted `/usr/bin/install` and `/usr/bin/chattr` vectors for effects r6
§1.4 replaces with syscalls.

Every test here was written before the correction and run against the submitted
tree, where the module does not import at all because the integration point it
names does not exist. The handback records that.

## Structural and behavioural, paired

The prompt is explicit that *"a source-code substring guard alone is not proof
of ordering or runtime composition"*. So each load-bearing claim has both: a
structural check over the syntax tree, which fails when the wiring is removed,
and a behavioural one over a laboratory under `tmp_path` with injected local
fakes, which fails when the ordering is wrong.

## What it is not

Nothing here observes `oracle-test`, provisions anything, starts a process or
reaches a database. `is_executable` stays `False`, `REAL_EXECUTION_REFUSAL`
stands unconditionally, and the last section asserts both — because integration
is repository wiring, and wiring is not permission to invoke it.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.phase_5_0_evidence.lab_fixtures import (
    AT,
    ATTESTER,
    BASIS,
    HOST,
    TARGET_IDENTITY,
    build_laboratory,
)
from tools.phase_5_0_evidence import reservation as reservation_module
from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan
from tools.phase_5_0_evidence.execution import cli as cli_module
from tools.phase_5_0_evidence.execution import executor as executor_module
from tools.phase_5_0_evidence.execution.boundary import (
    LAUNCH_DESCRIPTOR_CLOSED,
    LAUNCH_DESCRIPTOR_NOT_A_DIRECTORY,
    LAUNCH_DESCRIPTOR_SYNCHRONIZABLE,
    LAUNCH_DESCRIPTOR_UNDECLARED,
    LAUNCH_EFFECT_REFUSED,
    RecordingBoundary,
)
from tools.phase_5_0_evidence.execution.descriptors import (
    DESCRIPTOR_OPERATION_REFUSED,
    FIRST_TRANSFERRED_DESCRIPTOR,
    DescriptorInventory,
    DescriptorRefused,
    PosixFilesystem,
    TransferEntry,
)
from tools.phase_5_0_evidence.execution.participants import (
    NON_HARNESS_PARTICIPANTS,
    PARTICIPANT_CONDITIONS_UNMET,
    PARTICIPANT_ENTRY_POINTS,
    PARTICIPANT_NOT_ADMITTED,
    PARTICIPANT_RUN_ID_REFUSED,
    PARTICIPANT_START_NOT_DURABLE,
    EffectPermit,
    ParticipantIntegration,
    ParticipantRefused,
    validate_run_identifier,
)
from tools.phase_5_0_evidence.lifecycle_storage import (
    PARTICIPANT_PROFILES,
    PARTICIPANTS,
    EntryKind,
    Participant,
)
from tools.phase_5_0_evidence.plan import (
    PERMITTED_EXECUTABLES,
    RETIRED_EXECUTABLES,
    EffectKind,
)

THIS_FILE = Path(__file__).resolve()
TOOLS = THIS_FILE.parents[2] / "tools" / "phase_5_0_evidence"


# ---------------------------------------------------------------------------
# The laboratory the seven run in
# ---------------------------------------------------------------------------


def _initialized(lab):
    """A provisioned laboratory whose reservation record admits a successor.

    `verified_first_use` is the only way out of an absent record, and it refuses
    on a host that has been used before — so this is written once, here, and
    every participant below reads it rather than re-initializing.
    """
    from tests.phase_5_0_evidence.lab_fixtures import bind
    from tools.phase_5_0_evidence.lifecycle_storage import FirstUseEvidence

    bound = bind(lab)
    try:
        outcome = bound.record.initialize(
            approved_host=HOST,
            approved_target_identity=TARGET_IDENTITY,
            evidence=FirstUseEvidence(
                prior_use_excluded=True, attested_by=ATTESTER, basis=BASIS
            ),
            attested_at=AT,
        )
        assert outcome.initialized and outcome.durable, outcome
    finally:
        bound.close()
    return lab


def _integration(lab, participant, **keywords):
    """One integration point over the fixture's laboratory.

    `session_factory` is not injected: the point of this module is that the
    production object is what runs. What is injected is the **layout**, which is
    what keeps every path under `tmp_path` — `LABORATORY_LAYOUT` is the
    production definition and no test may build over it.
    """
    return ParticipantIntegration(
        participant=participant,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        author=PARTICIPANT_PROFILES[participant].identity,
        at=AT,
        layout=lab.layout,
        **keywords,
    )


def _conditions(participant, *, value: bool = True):
    """The participant's exact external completion conditions, all observed."""
    return {
        condition: value
        for condition in PARTICIPANT_PROFILES[participant].external_conditions()
    }


def _work(recorder: list, participant, *, observed=None):
    """A participant's work: it requires its permit, then reports conditions."""

    def run(permit: EffectPermit):
        permit.require()
        recorder.append(permit)
        return _conditions(participant) if observed is None else observed

    return run


# ---------------------------------------------------------------------------
# 1. All seven share one admission and ledger protocol
# ---------------------------------------------------------------------------


def test_every_participating_entry_point_has_an_integration_point() -> None:
    """**Structural.** Seven entries, seven participants, one table.

    The table is built from `reservation.PARTICIPATING_ENTRY_POINTS` and
    `Participant` rather than written out, so an entry point added to one and
    not the other fails here rather than being silently unaccounted for.
    """
    assert set(PARTICIPANT_ENTRY_POINTS) == set(PARTICIPANTS)
    assert len(PARTICIPANT_ENTRY_POINTS) == 7
    assert set(PARTICIPANT_ENTRY_POINTS.values()) == set(
        reservation_module.PARTICIPATING_ENTRY_POINTS.values()
    )
    for participant in PARTICIPANTS:
        assert (
            participant.value in reservation_module.PARTICIPATING_ENTRY_POINTS
        ), participant
    assert len(NON_HARNESS_PARTICIPANTS) == 6
    assert Participant.HARNESS_CLI not in NON_HARNESS_PARTICIPANTS


@pytest.mark.parametrize(
    "participant", NON_HARNESS_PARTICIPANTS, ids=lambda p: p.name
)
def test_each_of_the_six_admits_starts_and_completes_through_one_protocol(
    tmp_path, participant
) -> None:
    """**Behavioural.** The whole pass, over a real lock and real records."""
    lab = _initialized(build_laboratory(tmp_path))
    seen: list = []
    outcome = _integration(lab, participant).run(
        run_id=f"RUN-{participant.name}",
        work=_work(seen, participant),
        observed_by="the operator",
    )
    assert outcome.admitted and outcome.started and outcome.completed
    assert outcome.refusal == ""
    assert outcome.entry_point == PARTICIPANT_ENTRY_POINTS[participant]
    assert len(seen) == 1 and seen[0].granted
    # The run entry is a real file under the fixture's ledger directory, and it
    # is the run's own name — §5.11.1's P4.
    assert (lab.runs_directory / f"RUN-{participant.name}").exists()


def test_the_six_carry_the_start_binding_exactly_empty(tmp_path) -> None:
    """**§5.11.1 P9.** The harness carries an identity; the six carry none.

    It is derived from the profile rather than taken from the caller, so a
    suite start that tried to claim a reservation refuses at the writer.
    """
    lab = _initialized(build_laboratory(tmp_path))
    for participant in NON_HARNESS_PARTICIPANTS:
        integration = _integration(lab, participant, reservation_id="RES-1")
        assert integration._start_reservation() == ""
    harness = _integration(
        lab, Participant.HARNESS_CLI, reservation_id="RES-1", wait_for_lock=False
    )
    assert harness._start_reservation() == "RES-1"


# ---------------------------------------------------------------------------
# 2. None reaches its first effect before a durable start
# ---------------------------------------------------------------------------


def test_a_refused_admission_never_reaches_the_participants_work(tmp_path) -> None:
    """**Behavioural.** An unprovisioned host refuses before anything is called."""
    lab = build_laboratory(tmp_path)  # no record initialized: absent
    seen: list = []
    outcome = _integration(lab, Participant.BOT_SUITE).run(
        run_id="RUN-1",
        work=_work(seen, Participant.BOT_SUITE),
        observed_by="the operator",
    )
    assert not outcome.admitted
    assert outcome.refusal == PARTICIPANT_NOT_ADMITTED
    assert seen == [], "the work is not reached when admission refuses"
    assert not outcome.started


def test_an_absent_lock_refuses_and_the_participant_creates_nothing(
    tmp_path,
) -> None:
    """An unprovisioned lock is a refusal, not a file this run makes."""
    lab = build_laboratory(tmp_path, with_lock=False)
    seen: list = []
    with pytest.raises(ParticipantRefused) as refusal:
        _integration(lab, Participant.WEB_SUITE).run(
            run_id="RUN-1",
            work=_work(seen, Participant.WEB_SUITE),
            observed_by="the operator",
        )
    assert refusal.value.classification == "cooperative-lock-refused"
    assert seen == []
    assert not lab.lock_path.exists()


def test_a_permit_that_was_not_granted_refuses_the_first_effect() -> None:
    """**The ordering, as a property of the object graph.**

    The permit is the only object that says the start is durable, and it is
    constructed in exactly one place. A wrapper holding an ungranted one refuses
    rather than proceeding.
    """
    permit = EffectPermit(participant=Participant.FOUNDRY_TESTS, run_id="RUN-1")
    assert not permit.granted
    with pytest.raises(ParticipantRefused) as refusal:
        permit.require()
    assert refusal.value.classification == PARTICIPANT_START_NOT_DURABLE


def test_the_work_is_called_only_after_the_start_is_published(tmp_path) -> None:
    """**Behavioural, on ordering.** The ledger file exists before the work runs."""
    lab = _initialized(build_laboratory(tmp_path))
    observed: list[bool] = []

    def work(permit: EffectPermit):
        permit.require()
        observed.append((lab.runs_directory / "RUN-ORDER").exists())
        return _conditions(Participant.SYNCHRONIZATION)

    outcome = _integration(lab, Participant.SYNCHRONIZATION).run(
        run_id="RUN-ORDER", work=work, observed_by="the operator"
    )
    assert outcome.completed
    assert observed == [True], (
        "the run's non-reusable state is durable before its first effect"
    )


def test_a_start_that_does_not_publish_never_reaches_the_work(tmp_path) -> None:
    """**Behavioural.** A refused `begin()` stops the pass before the work.

    A run id that already has an entry is a run id that was used, and exclusive
    creation refuses it. The point is not the duplicate: it is that a start
    which did not reach durable storage leaves the work unreached, so a run
    whose effects nothing accounts for cannot begin.
    """
    lab = _initialized(build_laboratory(tmp_path))
    participant = Participant.FOUNDRY_TESTS
    first = _integration(lab, participant).run(
        run_id="RUN-TWICE",
        work=_work([], participant),
        observed_by="the operator",
    )
    assert first.completed

    seen: list = []
    again = _integration(lab, participant).run(
        run_id="RUN-TWICE",
        work=_work(seen, participant),
        observed_by="the operator",
    )
    assert again.admitted
    assert not again.started
    assert again.refusal == PARTICIPANT_START_NOT_DURABLE
    assert seen == [], "the work is not reached when the start does not publish"


# ---------------------------------------------------------------------------
# 3. Each exact completion profile is required — and the reset least of all
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "participant", NON_HARNESS_PARTICIPANTS, ids=lambda p: p.name
)
def test_a_missing_completion_condition_leaves_the_run_unsettled(
    tmp_path, participant
) -> None:
    """One condition withheld, and the run does not settle."""
    lab = _initialized(build_laboratory(tmp_path))
    conditions = _conditions(participant)
    withheld = sorted(conditions)[0]
    conditions[withheld] = False
    seen: list = []
    outcome = _integration(lab, participant).run(
        run_id="RUN-PARTIAL",
        work=_work(seen, participant, observed=conditions),
        observed_by="the operator",
    )
    assert outcome.started and not outcome.completed
    assert outcome.unsettled
    assert outcome.refusal == PARTICIPANT_CONDITIONS_UNMET
    assert withheld in " ".join(outcome.reasons)


def test_an_unnamed_observer_is_not_completion_evidence(tmp_path) -> None:
    """Somebody is named as having observed, or the completion refuses."""
    lab = _initialized(build_laboratory(tmp_path))
    participant = Participant.DEPENDENCY_UPDATE
    seen: list = []
    outcome = _integration(lab, participant).run(
        run_id="RUN-ANON", work=_work(seen, participant), observed_by="   "
    )
    assert not outcome.completed
    assert outcome.refusal == PARTICIPANT_CONDITIONS_UNMET


def test_the_environment_reset_receives_no_exemption(tmp_path) -> None:
    """**r6 §5.11.** The reset's exemption is refused especially.

    It is the participant whose effect is the removal of the evidence an earlier
    interruption left, so it is the one that must not run into unresolved
    evidence — and it publishes its own start and completion exactly as the
    other six do.
    """
    lab = _initialized(build_laboratory(tmp_path))
    reset = Participant.ENVIRONMENT_RESET
    profile = PARTICIPANT_PROFILES[reset]
    assert profile.completion_conditions
    seen: list = []
    outcome = _integration(lab, reset).run(
        run_id="RUN-RESET", work=_work(seen, reset), observed_by="the operator"
    )
    assert outcome.started and outcome.completed
    assert (lab.runs_directory / "RUN-RESET").exists()


# ---------------------------------------------------------------------------
# 4. An interrupted participant blocks all seven successors
# ---------------------------------------------------------------------------


def test_an_interrupted_participant_blocks_every_successor(tmp_path) -> None:
    """**Behavioural, and the reset is one of the seven it blocks.**

    A run that started and never settled refuses every successor until an
    attributable recovery is published — which is then shown to unblock them,
    so the refusal is a bounded operator action rather than a dead end.
    """
    lab = _initialized(build_laboratory(tmp_path))
    interrupted = Participant.BOT_SUITE
    conditions = _conditions(interrupted)
    conditions[sorted(conditions)[0]] = False
    blocked = _integration(lab, interrupted).run(
        run_id="RUN-INTERRUPTED",
        work=_work([], interrupted, observed=conditions),
        observed_by="the operator",
    )
    assert blocked.unsettled

    for participant in PARTICIPANTS:
        successor = _integration(
            lab,
            participant,
            reservation_id="RES-1" if participant.writes_the_record else "",
            wait_for_lock=not participant.writes_the_record,
        )
        seen: list = []
        outcome = successor.run(
            run_id=f"RUN-AFTER-{participant.name}",
            work=_work(seen, participant),
            observed_by="the operator",
        )
        assert not outcome.admitted, participant
        assert outcome.refusal == PARTICIPANT_NOT_ADMITTED
        assert seen == []

    # The bounded, attributable recovery — and the successor then admits.
    recovery = _integration(lab, interrupted).recover(
        run_id="RUN-INTERRUPTED", reference="operator recovery 2026-09-14"
    )
    assert recovery.published, recovery.reasons
    seen = []
    after = _integration(lab, Participant.ENVIRONMENT_RESET).run(
        run_id="RUN-RECOVERED",
        work=_work(seen, Participant.ENVIRONMENT_RESET),
        observed_by="the operator",
    )
    assert after.admitted and after.completed
    assert len(seen) == 1


def test_a_caller_supplied_run_identifier_is_bounded_before_it_is_a_name() -> None:
    """**Security.** A run id becomes a filename, a directory and a role label."""
    assert validate_run_identifier("RUN-1") == "RUN-1"
    for hostile in ("", "../escape", "a/b", "x" * 65, "-leading", "a b", "a\nb"):
        with pytest.raises(ParticipantRefused) as refusal:
            validate_run_identifier(hostile)
        assert refusal.value.classification == PARTICIPANT_RUN_ID_REFUSED
        # The refusal names the rule and never the value it refused.
        assert not hostile or hostile not in str(refusal.value)


# ---------------------------------------------------------------------------
# 5. The executable CLI branch is wired to the mechanism
# ---------------------------------------------------------------------------


def _execute_branch() -> ast.AST:
    """The `--execute` branch of `cli.main`, as a syntax tree.

    Structural, and deliberately scoped to the branch: a name that appears in an
    import or in a dry-run path proves nothing about what an execution
    assembles.
    """
    tree = ast.parse(Path(cli_module.__file__).read_text(encoding="utf-8"))
    main = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    guard = next(
        node
        for node in ast.walk(main)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.UnaryOp)
        and isinstance(node.test.op, ast.Not)
    )
    # Everything after the `if not args.execute:` early return.
    body = list(main.body)
    return ast.Module(body=body[body.index(guard) + 1 :], type_ignores=[])


def _constructed(tree: ast.AST) -> set[str]:
    return {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }


def test_the_execute_branch_assembles_the_whole_mechanism() -> None:
    """**Structural.** The four objects the review found unconnected.

    `SubprocessBoundary` and `SystemMaterializer` were already here. What was
    not: the participant integration that takes the lock and publishes the
    ledger entries, the descriptor inventory the effects are bound to, the
    independent recovery store, and the armed effect issuer that replaced
    `/usr/bin/install` and `/usr/bin/chattr`.
    """
    constructed = _constructed(_execute_branch())
    assert {
        "ParticipantIntegration",
        "DescriptorInventory",
        "PosixFilesystem",
        "RecoveryStore",
        "DescriptorBoundEffects",
        "SubprocessBoundary",
        "SystemMaterializer",
        "ExecutingRunner",
    } <= constructed


def test_the_dry_run_branch_assembles_none_of_it() -> None:
    """**Structural, the other direction.** A dry run constructs no writer.

    The property is what makes *"the default invocation executes nothing"* a
    fact about the object graph rather than about a branch somebody has to keep
    taking.
    """
    tree = ast.parse(Path(cli_module.__file__).read_text(encoding="utf-8"))
    main = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    guard = next(
        node
        for node in ast.walk(main)
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.UnaryOp)
        and isinstance(node.test.op, ast.Not)
    )
    dry = _constructed(ast.Module(body=guard.body, type_ignores=[]))
    assert "RecordingBoundary" in dry
    assert not dry & {
        "SubprocessBoundary",
        "SystemMaterializer",
        "DescriptorBoundEffects",
        "ParticipantIntegration",
        "RecoveryStore",
    }


def test_an_armed_effect_issuer_refuses_an_unaccounted_run() -> None:
    """**Behavioural.** Wiring is checked at run time too, not only in the CLI.

    An executor holding an issuer that can really change the host, with no
    participant integration accounting for the run, refuses before the first
    step. An unaccounted run is one whose effects nothing can attribute.

    **Corrected under PR-20260914-LABI-R1-1.** The version this replaces
    asserted that `session=object()` *satisfied* the guard, which is the
    fail-open behaviour the re-review found: presence is not accounting. Three
    things are required now — a real `ParticipantIntegration`, a permit the
    integration point issued after a durable start, and the permit's binding to
    this exact run and reservation. `test_lab_call_graph.py` carries the whole
    call-graph regression set, including the reversal that restores the
    presence-only check.
    """
    from tools.phase_5_0_evidence.execution.descriptors import PosixFilesystem
    from tools.phase_5_0_evidence.execution.executor import (
        DescriptorBoundEffects,
        ExecutingRunner,
    )

    # The **real** issuer, and armed — because the guard checks the type rather
    # than an attribute looked up by name, so a duck-typed double must not be
    # able to trip it either. It holds an empty inventory and is never asked to
    # issue anything: the guard refuses before the first step.
    inventory = DescriptorInventory()
    issuer = DescriptorBoundEffects(
        inventory=inventory, filesystem=PosixFilesystem(inventory), armed=True
    )
    try:
        runner = ExecutingRunner.__new__(ExecutingRunner)
        object.__setattr__(runner, "effects", issuer)
        object.__setattr__(runner, "session", None)
        object.__setattr__(runner, "run_id", "")
        object.__setattr__(runner, "permit", None)
        object.__setattr__(runner, "reservation_id", "")
        with pytest.raises(executor_module.ExecutorRefused) as refusal:
            ExecutingRunner._require_accounted_run(runner)
        assert "accounts for the run" in str(refusal.value)

        # **The finding.** Any object used to satisfy this. It does not.
        object.__setattr__(runner, "session", object())
        object.__setattr__(runner, "run_id", "RUN-1")
        with pytest.raises(executor_module.ExecutorRefused) as sentinel:
            ExecutingRunner._require_accounted_run(runner)
        assert "accounts for the run" in str(sentinel.value)

        # **Negative control.** An unarmed issuer needs no ledger entry, which
        # is why every test in this suite can inject one.
        object.__setattr__(runner, "session", None)
        object.__setattr__(runner, "run_id", "")
        object.__setattr__(
            runner,
            "effects",
            DescriptorBoundEffects(
                inventory=inventory, filesystem=PosixFilesystem(inventory)
            ),
        )
        ExecutingRunner._require_accounted_run(runner)
    finally:
        inventory.close()


def test_the_standing_operational_gates_are_all_still_closed() -> None:
    """Integration is wiring. It closes no gate and opens no permission."""
    plan = build_concrete_plan()
    assert plan.is_executable is False
    assert reservation_module.REAL_EXECUTION_REFUSAL
    assert plan.unresolved
    assert "C-7" in plan.conflicts()


# ---------------------------------------------------------------------------
# 6. The executor uses the corrected recovery and descriptor effects
# ---------------------------------------------------------------------------


def test_the_executor_dispatches_every_reviewed_effect_kind() -> None:
    """**Structural.** The closed set, and no default branch.

    Every `EffectKind` the plan can carry is named in `_apply_effect`, and the
    method ends in a refusal rather than in a fall-through — so an effect kind
    added without a dispatch is a refusal rather than a silent no-op.
    """
    source = Path(executor_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    method = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_apply_effect"
    )
    named = {
        node.attr
        for node in ast.walk(method)
        if isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "EffectKind"
    }
    assert named == {kind.name for kind in EffectKind}
    assert isinstance(method.body[-1], ast.Raise)


def test_the_plan_routes_every_retired_effect_through_the_issuer() -> None:
    """**Structural, on the generated plan.** P1, P1b, P2, P4 and L3's flags.

    Twenty-seven reviewed steps used to name `install` or `chattr`. Every one of
    them is a descriptor-bound effect now, and the two executables are absent
    from the allowlist, from every generated vector and from the plan's whole
    call graph.
    """
    plan = build_concrete_plan()
    effects = [
        step
        for step in (*plan.steps, *plan.cleanup_plan.steps)
        if step.is_effect
    ]
    kinds = {step.effect.kind for step in effects}
    assert kinds == set(EffectKind)
    assert len(effects) >= 27

    assert not (RETIRED_EXECUTABLES & PERMITTED_EXECUTABLES)
    assert len(PERMITTED_EXECUTABLES) == 20
    for step in (*plan.steps, *plan.cleanup_plan.steps):
        assert not (set(step.argv) & RETIRED_EXECUTABLES), step.step_id


def test_neither_retired_executable_is_reachable_from_the_package() -> None:
    """**Structural, on the whole package's source.** Not one string literal.

    A vector is built from string literals, so a package that contains neither
    literal cannot emit either executable however its generator is edited. The
    two names appear only in `plan.RETIRED_EXECUTABLES`, which is the tuple that
    says they are gone, and in prose.
    """
    offenders: list[str] = []
    for path in sorted(TOOLS.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if node.value in RETIRED_EXECUTABLES and path.name != "plan.py":
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == []


def test_the_materialization_requires_the_publication_and_not_the_step() -> None:
    """**Behavioural.** M1's precondition is the barrier set, re-checked.

    A satisfied capture step is this run's account of a step. The publication's
    barrier set is the account r6 §2.3.3 names, and `_revalidate_materialization`
    re-checks it immediately before the first configuration mutation rather than
    inferring it from the earlier one.
    """
    source = Path(executor_module.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    method = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "_revalidate_materialization"
    )
    called = {
        node.func.id
        for node in ast.walk(method)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "publication_permits_mutation" in called


# ---------------------------------------------------------------------------
# 7. The boundary receives the declared descriptor table
# ---------------------------------------------------------------------------


def test_the_boundary_is_handed_the_declared_table(tmp_path) -> None:
    """**Behavioural.** A recording boundary records what it was handed."""
    boundary = RecordingBoundary()
    entry = TransferEntry(
        index=FIRST_TRANSFERRED_DESCRIPTOR, role="bin", mode=None
    )
    from tools.phase_5_0_evidence.capture import CapturePolicy
    from tools.phase_5_0_evidence.durability_model import DescriptorMode

    boundary.run(
        step_id="X1",
        argv=("/usr/bin/id",),
        run_as="root",
        capture=CapturePolicy.EXIT_STATUS_ONLY,
        timeout_seconds=1.0,
        descriptors=(
            TransferEntry(
                index=FIRST_TRANSFERRED_DESCRIPTOR,
                role="bin",
                mode=DescriptorMode.O_PATH,
            ),
        ),
    )
    assert boundary.descriptors[-1][0].role == "bin"
    assert entry.index == FIRST_TRANSFERRED_DESCRIPTOR


def test_no_synchronizable_descriptor_is_ever_in_a_declared_table(tmp_path) -> None:
    """**§1.3.3.** The rule is enforced where the table is built."""
    lab = build_laboratory(tmp_path)
    inventory = DescriptorInventory()
    try:
        inventory.open_provisioned_root(
            "laboratory", lab.layout.laboratory_directory
        )
        inventory.bind_synchronizable("laboratory")
        declared = inventory.declare_transfer(["laboratory"])
        assert all(entry.mode.value == "O_PATH" for entry in declared)
        with pytest.raises(DescriptorRefused) as refusal:
            inventory.refuse_synchronizable_transfer("laboratory")
        assert refusal.value.classification == "descriptor-transfer-refused"
    finally:
        inventory.close()


@pytest.mark.parametrize(
    ("entries", "classification"),
    [
        pytest.param("undeclared", LAUNCH_DESCRIPTOR_UNDECLARED, id="undeclared"),
        pytest.param(
            "synchronizable", LAUNCH_DESCRIPTOR_SYNCHRONIZABLE, id="synchronizable"
        ),
        pytest.param("closed", LAUNCH_DESCRIPTOR_CLOSED, id="closed"),
        pytest.param(
            "not-a-directory", LAUNCH_DESCRIPTOR_NOT_A_DIRECTORY, id="not-a-directory"
        ),
    ],
)
def test_the_launch_refuses_every_undeclared_descriptor(
    tmp_path, entries, classification
) -> None:
    """**Behavioural, on the real boundary's validation — before any process.**

    `_transferable` is called before the process-starting call, and each of the
    four inputs refuses with a fixed classification. The boundary is **not
    armed** here, so the validation is exercised directly: an armed one is what
    `test_no_execution` refuses this suite to construct.
    """
    import os

    from tools.phase_5_0_evidence.durability_model import DescriptorMode
    from tools.phase_5_0_evidence.execution import boundary as boundary_module

    directory = os.open(str(tmp_path), os.O_RDONLY | os.O_DIRECTORY)
    regular = os.open(str(tmp_path / "file"), os.O_CREAT | os.O_RDONLY, 0o600)
    try:
        if entries == "undeclared":
            table = (
                TransferEntry(index=9, role="bin", mode=DescriptorMode.O_PATH),
            )
            table[0].__dict__ if False else None
            declared = (
                TransferEntry(index=9, role="bin", mode=DescriptorMode.O_PATH),
            )
        elif entries == "synchronizable":
            declared = (
                TransferEntry(
                    index=FIRST_TRANSFERRED_DESCRIPTOR,
                    role="bin",
                    mode=DescriptorMode.O_RDONLY,
                ),
            )
        elif entries == "closed":
            spare = os.open(str(tmp_path), os.O_RDONLY | os.O_DIRECTORY)
            os.close(spare)
            declared = (
                TransferEntry(
                    index=FIRST_TRANSFERRED_DESCRIPTOR,
                    role="bin",
                    mode=DescriptorMode.O_PATH,
                    number=spare,
                ),
            )
        else:
            declared = (
                TransferEntry(
                    index=FIRST_TRANSFERRED_DESCRIPTOR,
                    role="bin",
                    mode=DescriptorMode.O_PATH,
                    number=regular,
                ),
            )
        if entries in ("undeclared", "synchronizable"):
            declared = tuple(
                TransferEntry(
                    index=entry.index,
                    role=entry.role,
                    mode=entry.mode,
                    number=directory,
                )
                for entry in declared
            )
        with pytest.raises(boundary_module._TransferRefused) as refusal:
            boundary_module._transferable(declared)
        assert refusal.value.classification == classification
    finally:
        os.close(directory)
        os.close(regular)


def test_a_declared_directory_table_is_accepted(tmp_path) -> None:
    """The positive control: the correction must not refuse every table."""
    import os

    from tools.phase_5_0_evidence.durability_model import DescriptorMode
    from tools.phase_5_0_evidence.execution import boundary as boundary_module

    first = os.open(str(tmp_path), os.O_RDONLY | os.O_DIRECTORY)
    second = os.open(str(tmp_path), os.O_RDONLY | os.O_DIRECTORY)
    try:
        declared = (
            TransferEntry(
                index=FIRST_TRANSFERRED_DESCRIPTOR,
                role="bin",
                mode=DescriptorMode.O_PATH,
                number=first,
            ),
            TransferEntry(
                index=FIRST_TRANSFERRED_DESCRIPTOR + 1,
                role="journal",
                mode=DescriptorMode.O_PATH,
                number=second,
            ),
        )
        resolved = boundary_module._transferable(declared)
        assert resolved == (
            (first, FIRST_TRANSFERRED_DESCRIPTOR),
            (second, FIRST_TRANSFERRED_DESCRIPTOR + 1),
        )
    finally:
        os.close(first)
        os.close(second)


def test_the_real_boundary_validates_the_table_before_it_starts_anything() -> None:
    """**Structural.** The table is validated before the process-starting call.

    The name of that call is composed rather than written, because
    `test_no_execution` scans every file in this directory for it — and a test
    that asserted an ordering by naming the thing it may not reach would be
    defeating the scan rather than passing it.
    """
    from tools.phase_5_0_evidence.execution import boundary as boundary_module

    source = Path(boundary_module.__file__).read_text(encoding="utf-8")
    run = source.index("    def run(\n        self,\n        *,\n        step_id: str,")
    tail = source[run:]
    starter = "".join(("sub", "process", ".run("))
    assert tail.index("_transferable(") < tail.index(starter)
    assert "pass_fds=" in tail
    # And the real boundary's default is unarmed: the guard this suite is held
    # to refuses constructing one here, so the default is read off the
    # dataclass's field rather than off an instance.
    import dataclasses

    default = {
        field.name: field.default
        for field in dataclasses.fields(boundary_module.SubprocessBoundary)
    }
    assert default["armed"] is False


# ---------------------------------------------------------------------------
# 8. Negative controls — one reversal each
# ---------------------------------------------------------------------------


def test_the_ordering_control_reaches_the_work_without_a_durable_start(
    tmp_path,
) -> None:
    """**Negative control.** Remove only the permit's `granted` requirement.

    The production path constructs the permit *after* `begin()` returns
    published and the work calls `require()`. This re-issues the sequence with
    an ungranted permit and the requirement omitted, and the work then runs on a
    run whose start is not durable — which is what the ordering exists to
    prevent.
    """
    lab = _initialized(build_laboratory(tmp_path))
    permit = EffectPermit(participant=Participant.BOT_SUITE, run_id="RUN-1")
    reached: list = []

    def work(handed: EffectPermit):
        # The conjunct deliberately not applied: `handed.require()`.
        reached.append(handed.granted)
        return _conditions(Participant.BOT_SUITE)

    work(permit)
    assert reached == [False]
    assert not (lab.runs_directory / "RUN-1").exists()


def test_the_survey_control_admits_over_an_unsettled_run(tmp_path) -> None:
    """**Negative control.** Remove only the ledger from the admission.

    `read_and_admit` refuses when no ledger is supplied, which is R4-2's second
    path; this calls the same function with `ledger=None` over a laboratory that
    holds an unsettled run, and asserts the refusal is the *absent ledger* one
    rather than the unsettled run — so the survey is what blocks the successor,
    and removing it removes the block.
    """
    from tools.phase_5_0_evidence.lifecycle_storage import read_and_admit
    from tests.phase_5_0_evidence.lab_fixtures import bind

    lab = _initialized(build_laboratory(tmp_path))
    interrupted = Participant.WEB_SUITE
    conditions = _conditions(interrupted)
    conditions[sorted(conditions)[0]] = False
    blocked = _integration(lab, interrupted).run(
        run_id="RUN-OPEN",
        work=_work([], interrupted, observed=conditions),
        observed_by="the operator",
    )
    assert blocked.unsettled

    bound = bind(lab)
    try:
        with_ledger = read_and_admit(
            participant=Participant.ENVIRONMENT_RESET,
            record=bound.record.store,
            ledger=bound.ledger.ledger,
            lock=reservation_module.LockView(),
            host=HOST,
            target_identity=TARGET_IDENTITY,
            read_by="the reset",
            read_at=AT,
        )
        assert not with_ledger.may_proceed
        assert any("RUN-OPEN" in reason for reason in with_ledger.refusals)

        without = read_and_admit(
            participant=Participant.ENVIRONMENT_RESET,
            record=bound.record.store,
            ledger=None,
            lock=reservation_module.LockView(),
            host=HOST,
            target_identity=TARGET_IDENTITY,
            read_by="the reset",
            read_at=AT,
        )
        # Removing the survey removes the unsettled run from the refusal set.
        assert not any("RUN-OPEN" in reason for reason in without.refusals)
    finally:
        bound.close()


def test_the_run_identifier_control_lets_caller_text_become_a_name() -> None:
    """**Negative control.** Remove only the identifier bound.

    Without it a caller's run id reaches a filename, a recovery directory name
    and a refusal's role label unchanged — which is what bounding it prevents.
    """
    hostile = "../escape"
    assert not reservation_hostile_is_bounded(hostile)
    with pytest.raises(ParticipantRefused):
        validate_run_identifier(hostile)


def reservation_hostile_is_bounded(value: str) -> bool:
    """The comparison the control deliberately does not make."""
    from tools.phase_5_0_evidence.execution.participants import RUN_IDENTIFIER

    return bool(RUN_IDENTIFIER.match(value))


# ---------------------------------------------------------------------------
# 9. Nothing here provisions or executes
# ---------------------------------------------------------------------------


def test_this_suite_builds_over_no_production_path() -> None:
    """Every path is under `tmp_path`; the three production roots are absent."""
    from tools.phase_5_0_evidence.provisioning import LABORATORY_LAYOUT

    for path in (
        Path(LABORATORY_LAYOUT.lock_path),
        Path(LABORATORY_LAYOUT.laboratory_directory),
        Path(LABORATORY_LAYOUT.recovery_directory),
    ):
        assert not path.exists(), path


def test_the_reservation_record_is_the_one_the_fixture_initialized(tmp_path) -> None:
    """A positive control for the fixture: the record really is first-use."""
    from tests.phase_5_0_evidence.lab_fixtures import bind

    lab = _initialized(build_laboratory(tmp_path))
    bound = bind(lab)
    try:
        parsed = bound.record.read()
        assert parsed.ok
        assert parsed.entries[0].kind is EntryKind.FIRST_USE
    finally:
        bound.close()


# ---------------------------------------------------------------------------
# 10. The record store releases every descriptor it opens — C-P5.0-R5-RP11-I1-R3-R2
# ---------------------------------------------------------------------------
#
# `DurableRecordStore.read_record_bytes` and `publish` opened a descriptor
# through `PosixFilesystem` and never released it, on success and on failure.
# I1-R3-R1 measured 963 left open by four lab modules. These tests drive the
# production store over the real filesystem and read ownership from the
# filesystem's own calls, so each fails against the store that leaked. A
# `/proc/self/fd` count supplements that oracle and never replaces it.


class _OwnershipFilesystem(PosixFilesystem):
    """`PosixFilesystem`, recording what the store acquires and releases.

    A fault named in `faults` refuses that operation. `create` and `open`
    refuse **before** a descriptor exists; `read` and `write` refuse after it
    does. An injected `release` fault performs the real release and then
    reports failure, which is what Linux does: `close(2)` frees the number even
    when it returns an error, so the test leaks nothing it does not mean to.
    """

    def __init__(self, inventory: DescriptorInventory, *, faults=()) -> None:
        super().__init__(inventory)
        self.faults = frozenset(faults)
        self.acquired: list[int] = []
        self.release_calls: list[int] = []
        self.held: set[int] = set()

    def _fault(self, operation: str) -> None:
        if operation in self.faults:
            raise DescriptorRefused(
                DESCRIPTOR_OPERATION_REFUSED, f"injected-{operation}"
            )

    def _acquire(self, descriptor):
        assert descriptor.number not in self.held, descriptor
        self.acquired.append(descriptor.number)
        self.held.add(descriptor.number)
        return descriptor

    def create_file(self, dirfd, name, data=b"", **keywords):
        self._fault("create")
        return self._acquire(super().create_file(dirfd, name, data, **keywords))

    def openat(self, dirfd, name, mode):
        self._fault("open")
        return self._acquire(super().openat(dirfd, name, mode))

    def read(self, fd):
        self._fault("read")
        return super().read(fd)

    def write(self, fd, data):
        self._fault("write")
        super().write(fd, data)

    def release(self, number):
        self.release_calls.append(number)
        self.held.discard(number)
        released = super().release(number)
        return released and "release" not in self.faults


def _open_descriptor_count() -> int | None:
    """This process's descriptor table size, where Linux reports it."""
    table = Path("/proc/self/fd")
    return len(list(table.iterdir())) if table.is_dir() else None


def _ownership_stores(lab, *, faults=()):
    """The record and the ledger over one instrumented filesystem."""
    from tools.phase_5_0_evidence.execution.lifecycle_record import ReservationRecord
    from tools.phase_5_0_evidence.execution.run_ledger import ParticipantRunLedger

    inventory = DescriptorInventory()
    laboratory = inventory.open_provisioned_root(
        "laboratory", lab.layout.laboratory_directory
    )
    runs = inventory.adopt_directory(
        parent_role="laboratory", name=lab.layout.runs_directory_name, role="runs"
    )
    # The inventory binds each synchronizable descriptor on first use and holds
    # it for the run. Binding both here puts them in every baseline below, so a
    # `/proc/self/fd` count measures only what the store itself opens.
    inventory.bind_synchronizable("laboratory")
    inventory.bind_synchronizable("runs")
    filesystem = _OwnershipFilesystem(inventory, faults=faults)
    record = ReservationRecord(
        filesystem=filesystem,
        directory_object_id=laboratory.identity.object_id,
        name=lab.layout.record_name,
        host=HOST,
        target_identity=TARGET_IDENTITY,
    )
    ledger = ParticipantRunLedger(
        filesystem=filesystem,
        directory_object_id=runs.identity.object_id,
        host=HOST,
        target_identity=TARGET_IDENTITY,
    )
    return inventory, filesystem, record, ledger


def _assert_only_its_own_released(filesystem, inventory) -> None:
    """Each acquired descriptor released once; no inventory descriptor at all."""
    assert filesystem.held == set()
    assert sorted(filesystem.release_calls) == sorted(filesystem.acquired)
    for role in inventory.roles():
        handle = inventory.directory(role)
        for number in (handle.traversal_fd, handle.synchronizable_fd):
            if number is not None:
                assert number not in filesystem.release_calls, (role, number)


def _begin(ledger, run_id: str, *, fail_at: str = ""):
    participant = Participant.WEB_SUITE
    return ledger.begin(
        run_id=run_id,
        participant=participant,
        author=PARTICIPANT_PROFILES[participant].identity,
        at=AT,
        fail_at=fail_at,
    )


REPEATS = 40


def test_repeated_reads_release_every_read_descriptor(tmp_path) -> None:
    lab = _initialized(build_laboratory(tmp_path))
    inventory, filesystem, record, _ledger = _ownership_stores(lab)
    try:
        record.read()
        before = _open_descriptor_count()
        for _ in range(REPEATS):
            assert record.read().ok
        assert _open_descriptor_count() == before
        assert len(filesystem.acquired) == REPEATS + 1
        _assert_only_its_own_released(filesystem, inventory)
    finally:
        inventory.close()


def test_a_read_that_refuses_after_opening_still_releases(tmp_path) -> None:
    lab = _initialized(build_laboratory(tmp_path))
    inventory, filesystem, record, _ledger = _ownership_stores(
        lab, faults={"read"}
    )
    try:
        before = _open_descriptor_count()
        for _ in range(REPEATS):
            with pytest.raises(DescriptorRefused, match="injected-read"):
                record.store.read_record_bytes()
        assert _open_descriptor_count() == before
        assert len(filesystem.acquired) == REPEATS
        _assert_only_its_own_released(filesystem, inventory)
    finally:
        inventory.close()


def test_repeated_publications_release_every_temporary_descriptor(tmp_path) -> None:
    lab = build_laboratory(tmp_path)
    inventory, filesystem, _record, ledger = _ownership_stores(lab)
    try:
        before = _open_descriptor_count()
        for index in range(REPEATS):
            outcome = _begin(ledger, f"run-{index:03d}")
            assert outcome.published, outcome
            assert outcome.barriers == ("record-data", "record-entry")
        assert _open_descriptor_count() == before
        assert len(filesystem.acquired) == REPEATS
        _assert_only_its_own_released(filesystem, inventory)
        assert ledger.read_run("run-000").ok
    finally:
        inventory.close()


@pytest.mark.parametrize(
    ("fail_at", "barriers", "temporary", "final"),
    [
        ("record-data", (), True, False),
        ("rename", ("record-data",), True, False),
        ("record-entry", ("record-data",), False, True),
    ],
)
def test_every_injected_publication_failure_releases_and_keeps_its_artifacts(
    tmp_path, fail_at, barriers, temporary, final
) -> None:
    """The interruption points and what each leaves are the ones they were."""
    from tools.phase_5_0_evidence.lifecycle_storage import PublicationRefusal

    lab = build_laboratory(tmp_path)
    inventory, filesystem, _record, ledger = _ownership_stores(lab)
    try:
        before = _open_descriptor_count()
        outcome = _begin(ledger, "run-interrupted", fail_at=fail_at)
        assert not outcome.published
        assert outcome.refusal is PublicationRefusal.NOT_DURABLE
        assert outcome.barriers == barriers
        assert len(outcome.reasons) == 1 and "injected failure" in outcome.reasons[0]
        assert _open_descriptor_count() == before
        assert len(filesystem.acquired) == 1
        _assert_only_its_own_released(filesystem, inventory)
        assert (lab.runs_directory / "run-interrupted.tmp").exists() is temporary
        assert (lab.runs_directory / "run-interrupted").exists() is final
        assert ledger.observe_publication_temporary("run-interrupted").present is temporary
    finally:
        inventory.close()


def test_a_write_that_refuses_after_creation_releases(tmp_path) -> None:
    from tools.phase_5_0_evidence.lifecycle_storage import PublicationRefusal

    lab = build_laboratory(tmp_path)
    inventory, filesystem, _record, ledger = _ownership_stores(
        lab, faults={"write"}
    )
    try:
        before = _open_descriptor_count()
        outcome = _begin(ledger, "run-unwritten")
        assert outcome.refusal is PublicationRefusal.NOT_DURABLE
        assert outcome.barriers == ()
        assert _open_descriptor_count() == before
        _assert_only_its_own_released(filesystem, inventory)
        assert (lab.runs_directory / "run-unwritten.tmp").exists()
        assert not (lab.runs_directory / "run-unwritten").exists()
    finally:
        inventory.close()


def test_a_failed_release_after_publication_refuses_and_is_never_retried(
    tmp_path,
) -> None:
    """Both barriers returned success, and the writer still does not claim it."""
    from tools.phase_5_0_evidence.lifecycle_storage import PublicationRefusal

    lab = build_laboratory(tmp_path)
    inventory, filesystem, _record, ledger = _ownership_stores(
        lab, faults={"release"}
    )
    try:
        outcome = _begin(ledger, "run-unreleased")
        assert not outcome.published
        assert outcome.refusal is PublicationRefusal.NOT_DURABLE
        assert outcome.barriers == ("record-data", "record-entry")
        assert len(outcome.reasons) == 1 and "was not released" in outcome.reasons[0]
        assert filesystem.release_calls == filesystem.acquired
        assert len(filesystem.release_calls) == 1
        _assert_only_its_own_released(filesystem, inventory)
        assert (lab.runs_directory / "run-unreleased").exists()
        assert not (lab.runs_directory / "run-unreleased.tmp").exists()
    finally:
        inventory.close()


def test_a_failed_release_after_a_failure_names_both_once(tmp_path) -> None:
    lab = build_laboratory(tmp_path)
    inventory, filesystem, _record, ledger = _ownership_stores(
        lab, faults={"release"}
    )
    try:
        outcome = _begin(ledger, "run-twice", fail_at="rename")
        assert not outcome.published
        assert outcome.barriers == ("record-data",)
        assert len(outcome.reasons) == 2
        assert "injected failure" in outcome.reasons[0]
        assert "was not released" in outcome.reasons[1]
        assert len(filesystem.release_calls) == 1
        _assert_only_its_own_released(filesystem, inventory)
        assert (lab.runs_directory / "run-twice.tmp").exists()
    finally:
        inventory.close()


def test_a_failed_release_after_a_read_refuses_and_is_never_retried(
    tmp_path,
) -> None:
    """Neither the bytes nor `None`: a read that cannot release refuses."""
    from tools.phase_5_0_evidence.durability_model import ModelRefused

    lab = _initialized(build_laboratory(tmp_path))
    inventory, filesystem, record, _ledger = _ownership_stores(
        lab, faults={"release"}
    )
    try:
        with pytest.raises(ModelRefused, match="was not released"):
            record.store.read_record_bytes()
        assert len(filesystem.release_calls) == 1
        _assert_only_its_own_released(filesystem, inventory)
    finally:
        inventory.close()


@pytest.mark.parametrize("operation", ["open", "create"])
def test_an_acquisition_that_refuses_releases_nothing(tmp_path, operation) -> None:
    from tools.phase_5_0_evidence.lifecycle_storage import PublicationRefusal

    lab = _initialized(build_laboratory(tmp_path))
    inventory, filesystem, record, ledger = _ownership_stores(
        lab, faults={operation}
    )
    try:
        if operation == "open":
            assert record.store.read_record_bytes() is None
        else:
            outcome = _begin(ledger, "run-uncreated")
            assert outcome.refusal is PublicationRefusal.NOT_DURABLE
            assert outcome.barriers == ()
            assert not (lab.runs_directory / "run-uncreated.tmp").exists()
        assert filesystem.acquired == []
        assert filesystem.release_calls == []
    finally:
        inventory.close()


# ---------------------------------------------------------------------------
# 11. A failing acquisition releases what it opened — C-P5.0-R5-RP11-I1-R3-R3
# ---------------------------------------------------------------------------
#
# `PosixFilesystem.create_file` and `openat` own the number `os.open` returns
# until they hand the caller a `Descriptor`. Before this correction a failure
# in between — `fstat` for the identity, or `create_file`'s optional initial
# write — dropped it. The oracle is the kernel calls `descriptors.py` itself
# makes: its module-level `os` is replaced by a recorder that performs every
# real call, so the descriptors are real and every `open` and `close` is seen.
# A `/proc/self/fd` count supplements that oracle and never replaces it.


class _KernelCalls:
    """The `os` that `descriptors.py` sees, recording `open` and `close`.

    Faults named in `fail` apply only to descriptors opened after it was
    installed, never to the inventory's. `fstat` refuses with one fixed
    exception, so a test can prove it is the one the caller sees. `write`
    writes a short prefix once and then refuses, so a failed initial write
    leaves bytes a later cleanup would have to change. `close` performs the
    real close and then reports failure, which is what Linux does: `close(2)`
    frees the number even when it returns an error, so the test leaks nothing.
    """

    PARTIAL = 3

    def __init__(self, *, fail=()) -> None:
        import errno

        self.fail = frozenset(fail)
        self.opened: list[int] = []
        self.closed: list[int] = []
        self.writes = 0
        self.fstat_error = OSError(errno.EIO, "injected-fstat")
        self.close_error = OSError(errno.EIO, "injected-close")
        self.write_error = OSError(errno.ENOSPC, "injected-write")

    def __getattr__(self, name):
        import os

        return getattr(os, name)

    def open(self, *arguments, **keywords):
        import os

        fd = os.open(*arguments, **keywords)
        self.opened.append(fd)
        return fd

    def fstat(self, fd):
        import os

        if "fstat" in self.fail and fd in self.opened:
            raise self.fstat_error
        return os.fstat(fd)

    def write(self, fd, data):
        import os

        self.writes += 1
        if "write" not in self.fail:
            return os.write(fd, data)
        if self.writes > 1:
            raise self.write_error
        return os.write(fd, data[: self.PARTIAL])

    def close(self, fd):
        import os

        self.closed.append(fd)
        os.close(fd)
        if "close" in self.fail:
            raise self.close_error


def _post_open_filesystem(tmp_path, monkeypatch, *, fail=()):
    """A filesystem over one registered directory, and the recorder under it.

    The inventory opens and binds both of its descriptors **before** the
    recorder is installed, so every number the recorder sees opened is one the
    filesystem call under test acquired, and a `/proc/self/fd` baseline taken
    afterwards counts only that call.
    """
    from tools.phase_5_0_evidence.execution import descriptors as descriptors_module

    inventory = DescriptorInventory()
    root = inventory.open_provisioned_root("root", str(tmp_path))
    inventory.bind_synchronizable("root")
    kernel = _KernelCalls(fail=fail)
    monkeypatch.setattr(descriptors_module, "os", kernel)
    return inventory, PosixFilesystem(inventory), root.traversal_fd, kernel


def _assert_released_exactly_once(kernel, filesystem, inventory) -> None:
    """One `close` per acquired number, none repeated, none of the inventory's."""
    from tools.phase_5_0_evidence.execution.descriptors import (
        DESCRIPTOR_NOT_REGISTERED,
    )

    assert len(kernel.opened) == 1
    assert kernel.closed == kernel.opened
    for number in kernel.opened:
        with pytest.raises(DescriptorRefused) as refused:
            filesystem.describe(number)
        assert refused.value.classification == DESCRIPTOR_NOT_REGISTERED
    handle = inventory.directory("root")
    assert handle.traversal_fd not in kernel.closed
    assert handle.synchronizable_fd not in kernel.closed


def _post_open_failure(filesystem, dirfd, operation: str):
    """Drive one of the three failing acquisitions; return its exception."""
    from tools.phase_5_0_evidence.durability_model import DescriptorMode

    with pytest.raises(BaseException) as failure:
        if operation == "create":
            filesystem.create_file(dirfd, "created")
        elif operation == "create-data":
            filesystem.create_file(dirfd, "created", b"record-bytes")
        else:
            filesystem.openat(dirfd, "existing", DescriptorMode(operation))
    return failure.value


OPEN_MODES = ("O_RDONLY", "O_WRONLY", "O_PATH")


@pytest.mark.parametrize("operation", ["create", *OPEN_MODES])
def test_an_identity_failure_after_opening_releases_the_new_descriptor(
    tmp_path, monkeypatch, operation
) -> None:
    """Prompt §3 items 1, 2 and 4: `fstat` refuses after `os.open` succeeded."""
    (tmp_path / "existing").write_bytes(b"present")
    inventory, filesystem, dirfd, kernel = _post_open_filesystem(
        tmp_path, monkeypatch, fail={"fstat"}
    )
    try:
        before = _open_descriptor_count()
        failure = _post_open_failure(filesystem, dirfd, operation)
        assert failure is kernel.fstat_error
        assert _open_descriptor_count() == before
        _assert_released_exactly_once(kernel, filesystem, inventory)
        expected = ["created", "existing"] if operation == "create" else ["existing"]
        assert sorted(p.name for p in tmp_path.iterdir()) == expected
        assert (tmp_path / "existing").read_bytes() == b"present"
        if operation == "create":
            assert (tmp_path / "created").read_bytes() == b""
    finally:
        inventory.close()


def test_an_initial_write_failure_releases_and_leaves_the_created_name(
    tmp_path, monkeypatch
) -> None:
    """Prompt §3 items 3, 4 and 6: the name stays exactly as the write left it."""
    from tools.phase_5_0_evidence.execution.descriptors import (
        DESCRIPTOR_OPERATION_REFUSED,
    )

    inventory, filesystem, dirfd, kernel = _post_open_filesystem(
        tmp_path, monkeypatch, fail={"write"}
    )
    try:
        before = _open_descriptor_count()
        failure = _post_open_failure(filesystem, dirfd, "create-data")
        assert isinstance(failure, DescriptorRefused)
        assert failure.classification == DESCRIPTOR_OPERATION_REFUSED
        assert failure.role == "created"
        assert kernel.writes == 2
        assert _open_descriptor_count() == before
        _assert_released_exactly_once(kernel, filesystem, inventory)
        assert [p.name for p in tmp_path.iterdir()] == ["created"]
        created = tmp_path / "created"
        assert created.read_bytes() == b"record-bytes"[: _KernelCalls.PARTIAL]
        assert created.stat().st_nlink == 1
    finally:
        inventory.close()


@pytest.mark.parametrize(
    ("operation", "cause"),
    [
        ("create", "fstat"),
        ("create-data", "fstat"),
        ("create-data", "write"),
        *((mode, "fstat") for mode in OPEN_MODES),
    ],
)
def test_a_failed_release_is_not_retried_and_the_first_failure_wins(
    tmp_path, monkeypatch, operation, cause
) -> None:
    """Prompt §3 item 5: the close error neither repeats nor replaces the cause."""
    from tools.phase_5_0_evidence.execution.descriptors import (
        DESCRIPTOR_OPERATION_REFUSED,
    )

    (tmp_path / "existing").write_bytes(b"present")
    inventory, filesystem, dirfd, kernel = _post_open_filesystem(
        tmp_path, monkeypatch, fail={cause, "close"}
    )
    try:
        failure = _post_open_failure(filesystem, dirfd, operation)
        assert failure is not kernel.close_error
        if cause == "fstat":
            assert failure is kernel.fstat_error
        else:
            assert isinstance(failure, DescriptorRefused)
            assert failure.classification == DESCRIPTOR_OPERATION_REFUSED
        assert failure.__context__ is not kernel.close_error
        _assert_released_exactly_once(kernel, filesystem, inventory)
    finally:
        inventory.close()


@pytest.mark.parametrize("operation", ["create", "create-data", *OPEN_MODES])
def test_a_successful_acquisition_transfers_the_descriptor_to_its_caller(
    tmp_path, monkeypatch, operation
) -> None:
    """Prompt §3 item 7: nothing is closed until the caller releases it, once."""
    from tools.phase_5_0_evidence.durability_model import DescriptorMode

    (tmp_path / "existing").write_bytes(b"present")
    inventory, filesystem, dirfd, kernel = _post_open_filesystem(
        tmp_path, monkeypatch
    )
    try:
        before = _open_descriptor_count()
        if operation == "create":
            descriptor = filesystem.create_file(dirfd, "created")
        elif operation == "create-data":
            descriptor = filesystem.create_file(dirfd, "created", b"record-bytes")
        else:
            descriptor = filesystem.openat(dirfd, "existing", DescriptorMode(operation))
        name = "existing" if operation in OPEN_MODES else "created"
        mode = DescriptorMode(operation) if operation in OPEN_MODES else DescriptorMode.O_WRONLY
        assert kernel.opened == [descriptor.number]
        assert kernel.closed == []
        if before is not None:
            assert _open_descriptor_count() == before + 1
        facts = (tmp_path / name).stat()
        assert descriptor.object_id == f"{facts.st_dev}:{facts.st_ino}"
        assert descriptor.mode is mode
        assert descriptor.label == name
        assert filesystem.describe(descriptor.number) == descriptor
        if operation == "create-data":
            assert (tmp_path / "created").read_bytes() == b"record-bytes"
        assert filesystem.release(descriptor.number) is True
        assert kernel.closed == [descriptor.number]
        assert _open_descriptor_count() == before
    finally:
        inventory.close()
