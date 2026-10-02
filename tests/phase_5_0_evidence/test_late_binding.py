"""Conflict **C-5**: the four disposable names, the declared substitution sites,
and the rule that the executor may change nothing else.

Two halves again, and they are different guarantees:

* `binding.py` decides *what may be substituted and into what* — the sites, the
  names, the numeric form, and the comparison that refuses a change outside a
  declared site; and
* `executor._bind` decides *when* — immediately before process creation, through
  the injected NSS boundary, with the complete final vector revalidated by the
  same grammar the symbolic one passed.

**No test here reads the host's account database.** Every lookup is injected, and
`test_no_execution.py` asserts that no module in this suite imports `pwd` or
`grp`. Nothing starts a process.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from tools.phase_5_0_evidence.approved_target import CONFIRMATION_TOKEN
from tools.phase_5_0_evidence.binding import (
    LATE_BOUND_NAMES,
    MAX_IDENTIFIER,
    PERMITTED_BINDING_PREFIXES,
    BindingKind,
    BindingRefused,
    BindingSite,
    bind_arguments,
    validate_sites,
)
from tools.phase_5_0_evidence import case_runtime
from tools.phase_5_0_evidence.case_runtime import INTERPRETER_PATH
from tools.phase_5_0_evidence.concrete_plan import ConcretePlan, build_concrete_plan
from tools.phase_5_0_evidence.errors import PlanRefused
from tools.phase_5_0_evidence.execution.boundary import CommandResult, IdentityAbsent
from tools.phase_5_0_evidence.execution.executor import ExecutingRunner
from tools.phase_5_0_evidence.execution.materializer import MaterializationResult
from tools.phase_5_0_evidence.plan import CommandStep
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.harness_fixtures import (
    RecordingEffects,
    bound_argv,
    cleanup_observations_for,
    observations_for,
    runnable_plan,
    supply_reviewed_e7_facts,
    load_test_source_bytes,
)

SOURCES = load_test_source_bytes()
REVIEWED_INTERPRETER_DIGEST = "5" * 64

#: The second reviewed target fact, new in R12. `P-05` reports `interpreter_real`
#: and R12 compares it, so the executor refuses while it is unconfirmed exactly
#: as it does for the digest — which is asserted on its own in `test_executor.py`
#: against the shipped value. It is obviously synthetic: nothing here resolves a
#: real interpreter, because nothing here starts one.
REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"


@pytest.fixture(autouse=True)
def _the_reviewed_target_facts_are_supplied(monkeypatch: pytest.MonkeyPatch) -> None:
    """The executor's separate gates are asserted in `test_executor.py`."""
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
# The sites themselves
# ---------------------------------------------------------------------------


def test_the_late_bound_set_is_exactly_the_four_names_this_run_creates() -> None:
    assert LATE_BOUND_NAMES == {
        "freedomcoord",
        "freedomsheet",
        "fbprobe",
        "freedomjournal",
    }
    # The existing host identities the run reads *as* are deliberately absent:
    # rewriting a vector around an account the harness does not own is not a
    # substitution, it is a different plan.
    for name in ("root", "postgres", "discordbot", "freedomweb", "foundry"):
        assert name not in LATE_BOUND_NAMES


def test_each_kind_carries_exactly_one_prefix() -> None:
    assert PERMITTED_BINDING_PREFIXES == {"--uid=", "--gid=", "--groups="}
    assert BindingSite(1, BindingKind.UID, ("fbprobe",)).prefix == "--uid="
    assert BindingSite(1, BindingKind.GID, ("fbprobe",)).prefix == "--gid="
    assert BindingSite(1, BindingKind.GID_LIST, ("fbprobe",)).prefix == "--groups="


@pytest.mark.parametrize(
    "make",
    [
        pytest.param(lambda: BindingSite(1, BindingKind.UID, ("postgres",)), id="a name the run does not create"),
        pytest.param(lambda: BindingSite(1, BindingKind.UID, ("root",)), id="the superuser"),
        pytest.param(lambda: BindingSite(1, BindingKind.UID, ()), id="no name at all"),
        pytest.param(
            lambda: BindingSite(1, BindingKind.UID, ("fbprobe", "freedomsheet")),
            id="two names for a single identifier",
        ),
        pytest.param(
            lambda: BindingSite(1, BindingKind.GID, ("fbprobe", "freedomsheet")),
            id="two names for a single gid",
        ),
        pytest.param(
            lambda: BindingSite(1, BindingKind.GID_LIST, ("fbprobe", "fbprobe")),
            id="a repeated member",
        ),
        pytest.param(lambda: BindingSite(0, BindingKind.UID, ("fbprobe",)), id="the executable"),
        pytest.param(lambda: BindingSite(-1, BindingKind.UID, ("fbprobe",)), id="a negative index"),
        pytest.param(lambda: BindingSite(True, BindingKind.UID, ("fbprobe",)), id="a boolean index"),
        pytest.param(lambda: BindingSite(1, "uid", ("fbprobe",)), id="a kind outside the closed set"),
    ],
)
def test_a_binding_site_the_rule_does_not_describe_is_refused(make) -> None:
    with pytest.raises(BindingRefused):
        make()


def test_a_site_must_match_the_vector_it_annotates() -> None:
    argv = ("/usr/sbin/capsh", "--uid=freedomsheet")
    site = BindingSite(1, BindingKind.UID, ("freedomsheet",))
    validate_sites(argv, (site,))

    with pytest.raises(BindingRefused):
        validate_sites(("/usr/sbin/capsh", "--uid=fbprobe"), (site,))
    with pytest.raises(BindingRefused):
        validate_sites(("/usr/sbin/capsh", "--gid=freedomsheet"), (site,))
    with pytest.raises(BindingRefused):
        validate_sites(("/usr/sbin/capsh",), (site,))
    with pytest.raises(BindingRefused):
        validate_sites(argv, (site, site))


def test_a_step_whose_declaration_disagrees_with_its_vector_is_refused_at_plan_time() -> None:
    """The check is at `CommandStep` construction, not at execution.

    A declaration that has drifted from its vector is a plan defect, and a plan
    defect discovered immediately before a privileged process is a plan defect
    discovered too late.
    """
    with pytest.raises(PlanRefused):
        CommandStep(
            step_id="X",
            band="capability",
            run_as="root",
            argv=("/usr/sbin/capsh", "--uid=fbprobe"),
            purpose="a step whose site names a different identity",
            bindings=(BindingSite(1, BindingKind.UID, ("freedomsheet",)),),
        )


# ---------------------------------------------------------------------------
# Substitution
# ---------------------------------------------------------------------------

UIDS = {"freedomcoord": 5001, "freedomsheet": 5002, "fbprobe": 5003, "postgres": 900}
GIDS = {
    "freedomcoord": 5001,
    "freedomsheet": 5002,
    "fbprobe": 5003,
    "freedomjournal": 5004,
    # Pre-existing, and the reviewed restoration `fchown`s to it — r6 §2.4.
    "postgres": 900,
}


def uid_of(name: str) -> int:
    return UIDS[name]


def gid_of(name: str) -> int:
    return GIDS[name]


def test_only_the_declared_sites_change() -> None:
    argv = (
        "/usr/sbin/capsh",
        "--secbits=4",
        "--gid=freedomsheet",
        "--groups=freedomsheet,freedomjournal",
        "--uid=freedomsheet",
        f"--shell={INTERPRETER_PATH}",
        "--",
        "-I",
        "-S",
        "/var/lib/fb-evidence-p5-0/bin/case",
        "identity",
    )
    sites = (
        BindingSite(2, BindingKind.GID, ("freedomsheet",)),
        BindingSite(3, BindingKind.GID_LIST, ("freedomsheet", "freedomjournal")),
        BindingSite(4, BindingKind.UID, ("freedomsheet",)),
    )
    bound = bind_arguments(argv, sites, resolve_uid=uid_of, resolve_gid=gid_of)

    assert bound[2] == "--gid=5002"
    assert bound[3] == "--groups=5002,5004"
    assert bound[4] == "--uid=5002"
    # Everything else, byte for byte.
    for index, argument in enumerate(argv):
        if index not in (2, 3, 4):
            assert bound[index] == argument, index
    assert len(bound) == len(argv)


def test_the_group_list_keeps_the_reviewed_order() -> None:
    """`--groups=` is the primary group first, then §2.12.2's supplementary list.

    The order is the reviewed one, so a substitution that sorted numerically
    would be substituting something the plan does not say.
    """
    argv = ("/usr/sbin/capsh", "--groups=fbprobe,freedomcoord")
    site = BindingSite(1, BindingKind.GID_LIST, ("fbprobe", "freedomcoord"))
    bound = bind_arguments(argv, (site,), resolve_uid=uid_of, resolve_gid=gid_of)
    assert bound[1] == "--groups=5003,5001"


@pytest.mark.parametrize(
    "value, why",
    [
        (0, "the superuser id"),
        (-1, "a negative id"),
        (MAX_IDENTIFIER + 1, "a wrapped or sentinel id"),
        (True, "a boolean"),
        ("5002", "text"),
        (5002.0, "a float"),
        (None, "nothing at all"),
    ],
)
def test_a_resolved_value_that_is_not_a_usable_identifier_is_refused(value, why) -> None:
    argv = ("/usr/sbin/capsh", "--uid=freedomsheet")
    site = BindingSite(1, BindingKind.UID, ("freedomsheet",))
    with pytest.raises(BindingRefused):
        bind_arguments(
            argv, (site,), resolve_uid=lambda name: value, resolve_gid=gid_of
        )


def test_two_names_resolving_to_the_same_number_is_refused() -> None:
    """A group list that names two identities and carries one is not that list."""
    argv = ("/usr/sbin/capsh", "--groups=freedomsheet,freedomjournal")
    site = BindingSite(1, BindingKind.GID_LIST, ("freedomsheet", "freedomjournal"))
    with pytest.raises(BindingRefused):
        bind_arguments(
            argv, (site,), resolve_uid=uid_of, resolve_gid=lambda name: 7000
        )


def test_a_lookup_that_cannot_answer_propagates_rather_than_defaulting() -> None:
    argv = ("/usr/sbin/capsh", "--uid=freedomsheet")
    site = BindingSite(1, BindingKind.UID, ("freedomsheet",))

    def missing(name: str) -> int:
        raise IdentityAbsent(name)

    with pytest.raises(IdentityAbsent):
        bind_arguments(argv, (site,), resolve_uid=missing, resolve_gid=gid_of)


def test_a_change_outside_a_declared_site_is_refused_by_comparison() -> None:
    """`_refuse_change_outside_sites` is read back rather than assumed.

    The substitution above builds the vector and this reads the result, so a
    future edit that rewrote something else is caught by the check rather than
    by whoever reads the code that did it.
    """
    from tools.phase_5_0_evidence.binding import _refuse_change_outside_sites

    symbolic = ("/usr/sbin/capsh", "--uid=freedomsheet", "--secbits=4")
    _refuse_change_outside_sites(
        symbolic, ("/usr/sbin/capsh", "--uid=5002", "--secbits=4"), {1: "--uid=5002"}
    )
    with pytest.raises(BindingRefused):
        _refuse_change_outside_sites(
            symbolic,
            ("/usr/sbin/capsh", "--uid=5002", "--secbits=0"),
            {1: "--uid=5002"},
        )
    with pytest.raises(BindingRefused):
        _refuse_change_outside_sites(
            symbolic, ("/usr/sbin/capsh", "--uid=5002"), {1: "--uid=5002"}
        )


# ---------------------------------------------------------------------------
# The generated plan's sites
# ---------------------------------------------------------------------------


def test_only_the_capability_band_declares_a_binding_site() -> None:
    plan = build_concrete_plan()
    with_sites = {step.step_id for step in plan.steps if step.bindings}
    # **R16, conflict C-6.** The three immutable-flag experiments are `capsh`
    # constructions too, so they carry the same three sites for the same reason:
    # `--uid=`, `--gid=` and `--groups=` take numbers and the four disposable
    # names do not exist when the plan is generated. What is asserted is that
    # every step with a site is a capability-band `capsh` construction and every
    # capability-band `capsh` construction has its three sites — not a list of
    # step ids that grows whenever the band does.
    assert with_sites == {
        step.step_id
        for step in plan.steps
        if step.band == "capability"
        and step.argv[:1] == ("/usr/sbin/capsh",)
        and any(argument.startswith("--uid=") for argument in step.argv)
    }
    assert {f"B5-E{n}" for n in (1, 2, 3, 4, 5, 6, 8)} <= with_sites


def test_every_declared_site_names_only_the_four_disposable_identities() -> None:
    plan = build_concrete_plan()
    for step in plan.steps:
        for site in step.bindings:
            assert set(site.names) <= LATE_BOUND_NAMES, step.step_id
            assert step.argv[site.argument_index] == site.symbolic_argument


def test_the_reviewed_vector_carries_names_and_never_a_number() -> None:
    """The manifest pins the symbolic form. That is the whole point of it.

    A plan carrying uids would be pinning numbers nobody has verified, against
    accounts that do not exist until Band 2 creates them.
    """
    plan = build_concrete_plan()
    for step in plan.steps:
        for site in step.bindings:
            value = step.argv[site.argument_index][len(site.prefix) :]
            assert not any(part.isdigit() for part in value.split(",")), step.step_id


def test_the_manifest_pins_the_sites_and_the_symbolic_argument() -> None:
    plan = build_concrete_plan()
    manifest = ReviewManifest.build(plan, SOURCES).as_mapping()
    by_id = {step["step_id"]: step for step in manifest["steps"]}
    e1 = by_id["B5-E1"]
    assert e1["bindings"], "the sites are part of what a reviewer approves"
    for site in e1["bindings"]:
        assert site["prefix"] in PERMITTED_BINDING_PREFIXES
        assert set(site["names"]) <= LATE_BOUND_NAMES
        assert e1["argv"][site["argument_index"]] == site["symbolic_argument"]


# ---------------------------------------------------------------------------
# The executor: when, and what it revalidates
# ---------------------------------------------------------------------------


@dataclass
class Boundary:
    """Records the vector it was handed. Starts nothing."""

    calls: list[tuple[str, tuple[str, ...]]] = field(default_factory=list)
    scripted: dict = field(default_factory=dict)

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
        self.calls.append((step_id, tuple(argv)))
        return self.scripted.get(step_id, CommandResult(exit_status=0, timed_out=False))


@dataclass
class Materializer:
    def materialize(self, **_keywords) -> MaterializationResult:
        return MaterializationResult(applied=True)


@dataclass
class Lookup:
    """The injected NSS boundary. It answers from a table and reads no host."""

    uids: dict = field(default_factory=lambda: dict(UIDS))
    gids: dict = field(default_factory=lambda: dict(GIDS))

    def account(self, name: str) -> tuple[int, int]:
        if name not in self.uids:
            raise IdentityAbsent(name)
        return self.uids[name], self.gids[name]

    def group_id(self, name: str) -> int:
        if name not in self.gids:
            raise IdentityAbsent(name)
        return self.gids[name]

    def supplementary_group_names(self, name, primary_gid):  # pragma: no cover
        raise AssertionError("the executor resolves ids, never memberships")

    def effective_ids(self) -> tuple[int, int]:  # pragma: no cover
        return 0, 0


def make_runner(
    plan: ConcretePlan,
    boundary: Boundary,
    *,
    runner_class=ExecutingRunner,
    **overrides,
) -> ExecutingRunner:
    keywords = dict(
        plan=plan,
        boundary=boundary,
        reviewed_digest=ReviewManifest.build(plan, SOURCES).digest(),
        confirmation_token=CONFIRMATION_TOKEN,
        source_bytes=dict(SOURCES),
        materializer=Materializer(),
        identity_lookup=Lookup(),
        effects=RecordingEffects(),
    )
    keywords.update(overrides)
    return runner_class(**keywords)


def satisfying(plan: ConcretePlan, boundary: Boundary) -> Boundary:
    """Every satisfying exit status, and — R12 — the observation each
    contract-bearing step's reviewed expectation requires."""
    for step in plan.steps:
        status = 1 if step.refusal_required else step.satisfying_statuses[0]
        boundary.scripted[step.step_id] = CommandResult(
            exit_status=status,
            timed_out=False,
            observations=observations_for(step, bound_argv(step), SOURCES),
        )
    for step in plan.cleanup_plan.steps:
        status = 1 if step.refusal_required else step.satisfying_statuses[0]
        boundary.scripted[step.step_id] = CommandResult(
            exit_status=status,
            timed_out=False,
            observations=cleanup_observations_for(step, plan, SOURCES),
        )
    return boundary


def test_the_boundary_is_handed_the_substituted_vector() -> None:
    plan = runnable_plan()
    boundary = satisfying(plan, Boundary())
    make_runner(plan, boundary).execute()

    handed = dict(boundary.calls)
    e1 = handed["B5-E1"]
    assert "--uid=5002" in e1
    assert "--gid=5002" in e1
    assert "--groups=5002,5004" in e1
    assert not any(argument.endswith("=freedomsheet") for argument in e1)
    # And every other **command** step is handed exactly its reviewed vector. A
    # descriptor-bound effect is handed to nobody: it starts no process, so it
    # never reaches the boundary at all.
    for step in plan.steps:
        if step.is_effect:
            assert step.step_id not in handed, step.step_id
            continue
        if not step.bindings:
            assert handed[step.step_id] == tuple(step.argv), step.step_id


def test_a_run_that_cannot_resolve_an_identity_stops_before_the_step() -> None:
    """An unresolvable identity stops the run at the **first** step that needs it.

    Since r6 §6.4 that is earlier than `B5-E1`: the descriptor-bound creation of
    the seal `fchown`s it to `root:freedomjournal`, and it resolves that group
    through the same injected NSS boundary the `capsh` construction does. So the
    run stops before any process is started at all, which is a stronger form of
    the property this test has always asserted — and `B5-E1` is still never
    reached.
    """
    plan = runnable_plan()
    boundary = satisfying(plan, Boundary())
    lookup = Lookup()
    del lookup.gids["freedomjournal"]

    outcome = make_runner(plan, boundary, identity_lookup=lookup).execute()

    stopped = next(
        step for step in plan.steps if step.step_id == outcome.stopped_at
    )
    assert stopped.is_effect
    assert stopped.effect.group == "freedomjournal"
    assert outcome.stopped_at not in dict(boundary.calls)
    assert "B5-E1" not in dict(boundary.calls)
    # The message says nothing about which account, which id or what the
    # operating system said.
    assert "freedomjournal" not in outcome.stop_reason
    assert "5004" not in outcome.stop_reason


def test_the_substituted_vector_is_revalidated_before_the_process_is_created() -> None:
    """The ordering, injected rather than described.

    A subclass refuses exactly the shape only a **substituted** vector has —
    `--uid=` followed by digits — and passes everything else through to the real
    guard. A run that reached the boundary for `B5-E1` would therefore prove the
    revalidation had been skipped.
    """

    class RefusesTheBoundVector(ExecutingRunner):
        def _revalidate_vector(self, argv, run_as):
            for argument in argv:
                if argument.startswith("--uid=") and argument[6:].isdigit():
                    return "a synthetic refusal of the substituted vector"
            return super()._revalidate_vector(argv, run_as)

    plan = runnable_plan()
    boundary = satisfying(plan, Boundary())
    live = make_runner(plan, boundary, runner_class=RefusesTheBoundVector)
    outcome = live.execute()

    assert outcome.stopped_at == "B5-E1"
    assert "the substituted vector was refused" in outcome.stop_reason
    assert "B5-E1" not in dict(boundary.calls)


def test_a_step_with_no_declared_site_consults_no_lookup_at_all() -> None:
    """The four names are resolved for §2.13.5c and for nothing else."""

    class Exploding(Lookup):
        def account(self, name: str):  # pragma: no cover - must not be reached
            raise AssertionError("a step with no binding site resolved a name")

        def group_id(self, name: str):  # pragma: no cover - must not be reached
            raise AssertionError("a step with no binding site resolved a name")

    plan = build_concrete_plan()
    unbound = ConcretePlan(
        execution_plan=type(plan.execution_plan)(
            target=plan.target,
            steps=tuple(step for step in plan.steps if not step.bindings),
            mutations=plan.mutations,
            materializations=plan.materializations,
        ),
        cleanup_plan=plan.cleanup_plan,
        unresolved=(),
    )
    boundary = satisfying(unbound, Boundary())
    make_runner(unbound, boundary, identity_lookup=Exploding()).execute()
