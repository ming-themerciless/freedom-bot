"""Argument-vector planning, mutation declaration, the dry-run runner, and the
cleanup that is derived rather than written.

**EH-R3-2 is the configuration half of this file.** A `POSTGRES_CONFIG_LINE`
mutation now carries the complete `(OS identity, PostgreSQL role)` pair its
post-reload proof runs as and asks for, because the proof cannot be constructed
without it and a plan that cannot construct its own proof is not a plan. The pair
is validated where the mutation is declared, again when the plan is built, and
once more before either half could become a step's `run_as` or `--username`;
every one of those refusals has a test below, and none of them defaults a half.

`CleanupStep`'s vocabulary is the current one throughout: `kind`, `run_as`,
`mutation_ids` and `satisfying_statuses`. The superseded `mutation_id` /
`absent_statuses` spelling is gone, and the recursion, wildcard and breadth
refusals are asserted through the current constructor.
"""
from __future__ import annotations

import pytest

from tools.phase_5_0_evidence.cleanup import (
    CleanupPlan,
    CleanupStep,
    CleanupStepKind,
    ConfigurationRestoration,
    FORBIDDEN_CLEANUP_TOKENS,
    NON_DESTRUCTIVE_WHEN_ABSENT,
    classify_cleanup,
)
from tools.phase_5_0_evidence.cleanup import _REVERSALS
from tools.phase_5_0_evidence.errors import PlanRefused, TargetRefused
from tools.phase_5_0_evidence.plan import (
    CommandStep,
    DryRunRunner,
    ExecutionPlan,
    Mutation,
    MutationKind,
    read_only_plan,
    validate_argv,
)
from tools.phase_5_0_evidence.records import CleanupState
from tools.phase_5_0_evidence.targets import DisposableTarget


def target(**overrides) -> DisposableTarget:
    base = dict(
        host="fb-evidence-host-1",
        root_path="/var/lib/fb-evidence-r1",
        database_name="fb_evidence_r1",
        postgres_socket_directory="/var/run/postgresql",
        confirmed_disposable=True,
        disposability_evidence="Named by the Operations Owner on 2026-09-02.",
        postgres_config_directory="/etc/postgresql/17/fbevidence",
    )
    base.update(overrides)
    return DisposableTarget(**base)


GROUP = Mutation(MutationKind.OS_GROUP, "freedomjournal", "JNL-52 requires the group")
ACCOUNT = Mutation(MutationKind.OS_ACCOUNT, "freedomsheet", "the writer identity")
MEMBERSHIP = Mutation(
    MutationKind.GROUP_MEMBERSHIP, "freedomsheet", "§2.12.2 membership", group="freedomjournal"
)
JOURNAL_DIR = Mutation(
    MutationKind.DIRECTORY, "/var/lib/fb-evidence-r1/journal", "the journal hierarchy"
)
PROBE_FILE = Mutation(
    MutationKind.FILE, "/var/lib/fb-evidence-r1/probe/target", "a Stage-2 probe file"
)

#: The one temporary authentication mapping the execution plan's Band 6 declares:
#: the coordinator OS identity the run creates, and the PostgreSQL role §2.12.3's
#: identity map would admit it as. It is stated here once, explicitly, and it is
#: **not** a default — `Mutation` has none, and a configuration mutation that does
#: not declare a pair is refused rather than given this one.
MAPPED_OS_USER = "freedomcoord"
MAPPED_POSTGRES_ROLE = "freedom_migration_coordinator"


def config_line(
    identifier: str = "coordinator-peer-line",
    filename: str = "pg_hba.conf",
    **overrides,
) -> Mutation:
    """A complete configuration-line mutation, as Band 6 declares one."""
    fields = dict(
        file_path=f"/etc/postgresql/17/fbevidence/{filename}",
        maps_os_user=MAPPED_OS_USER,
        maps_postgres_role=MAPPED_POSTGRES_ROLE,
    )
    fields.update(overrides)
    return Mutation(
        MutationKind.POSTGRES_CONFIG_LINE, identifier, "§2.12.3's peer rule", **fields
    )


ROLE = Mutation(MutationKind.POSTGRES_ROLE, MAPPED_POSTGRES_ROLE, "the role")


# ---------------------------------------------------------------------------
# Argument vectors
# ---------------------------------------------------------------------------

REFUSED_ARGV = [
    ("empty", ()),
    ("a shell", ("/usr/bin/sh", "-c", "chattr +a x")),
    ("bash", ("/usr/bin/bash", "-c", "true")),
    ("sudo", ("/usr/bin/sudo", "/usr/bin/chattr", "+a", "/var/lib/fb-evidence-r1/x")),
    ("su", ("/usr/bin/su", "freedomsheet")),
    ("an unpermitted binary", ("/usr/local/bin/probe",)),
    ("a relative executable", ("chattr", "+a", "/var/lib/fb-evidence-r1/x")),
    ("a pipe", ("/usr/bin/lsattr", "/var/lib/fb-evidence-r1/x|tee")),
    ("a glob", ("/usr/bin/rm", "/var/lib/fb-evidence-r1/*")),
    ("a variable", ("/usr/bin/chattr", "+a", "$TARGET")),
    ("a braced variable", ("/usr/bin/chattr", "+a", "${TARGET}")),
    ("a redirect", ("/usr/bin/lsattr", ">out")),
    ("a backtick", ("/usr/bin/id", "`whoami`")),
    ("an empty argument", ("/usr/bin/id", "")),
    ("a non-string argument", ("/usr/bin/id", 1000)),
    ("a bare string instead of a vector", "/usr/bin/id"),
]


@pytest.mark.parametrize("label, argv", REFUSED_ARGV, ids=[a[0] for a in REFUSED_ARGV])
def test_an_argument_vector_a_reviewer_could_not_check_is_refused(label: str, argv) -> None:
    with pytest.raises(PlanRefused):
        validate_argv(argv, target=target())


def test_a_program_inside_the_disposable_root_is_no_longer_an_executable() -> None:
    """**Narrowed by conflict C-2's resolution, not widened.**

    Before R11 any absolute path inside the disposable root was admissible as
    `argv[0]`, on the assumption that a case binary would be exec'd directly.
    Option B names the interpreter in the vector instead, so the case program is
    an argument and never `argv[0]` — and the old exception is now a hole
    admitting an arbitrary program the harness would have placed in the root. It
    is gone.
    """
    with pytest.raises(PlanRefused):
        validate_argv(
            ("/var/lib/fb-evidence-r1/bin/case-e2", "--case", "JNL-50-4"),
            target=target(),
        )


def test_a_program_outside_the_disposable_root_is_refused_too() -> None:
    with pytest.raises(PlanRefused):
        validate_argv(("/var/lib/other/bin/case-e2",), target=target())


# ---------------------------------------------------------------------------
# Mutation declaration
# ---------------------------------------------------------------------------


def test_a_mutation_bearing_step_the_plan_does_not_declare_is_refused() -> None:
    step = CommandStep(
        step_id="S1",
        band="identity",
        run_as="root",
        argv=("/usr/sbin/groupadd", "--system", "freedomjournal"),
        purpose="create the freedomjournal group",
        mutation_ids=(GROUP.mutation_id,),
    )
    with pytest.raises(PlanRefused) as refusal:
        ExecutionPlan(target=target(), steps=(step,), mutations=())
    assert "has no cleanup step and no reviewer approval" in str(refusal.value)


def test_a_mutation_bearing_step_against_an_unassigned_target_is_refused() -> None:
    step = CommandStep(
        step_id="S1",
        band="identity",
        run_as="root",
        argv=("/usr/sbin/groupadd", "--system", "freedomjournal"),
        purpose="create the freedomjournal group",
        mutation_ids=(GROUP.mutation_id,),
    )
    with pytest.raises(TargetRefused):
        ExecutionPlan(target=DisposableTarget.unassigned(), steps=(step,), mutations=(GROUP,))


def test_a_read_only_plan_is_admissible_before_a_target_exists() -> None:
    plan = read_only_plan(
        [
            CommandStep(
                step_id="R1",
                band="identity",
                run_as="the authorized reader",
                argv=("/usr/bin/getent", "group", "freedomjournal"),
                purpose="pre-change discovery",
            )
        ]
    )
    assert plan.target.is_unassigned
    assert plan.mutation_bearing_steps == ()
    assert len(plan.read_only_steps) == 1


def test_a_mutation_naming_a_production_path_cannot_be_declared() -> None:
    outside = Mutation(
        MutationKind.DIRECTORY, "/var/lib/freedom-sheet-writer/journal", "production"
    )
    with pytest.raises(TargetRefused):
        ExecutionPlan(target=target(), steps=(), mutations=(outside,))


def test_a_mutation_without_a_stated_reason_is_refused() -> None:
    with pytest.raises(PlanRefused):
        Mutation(MutationKind.OS_GROUP, "freedomjournal", "  ")


def test_a_duplicate_mutation_or_step_id_is_refused() -> None:
    with pytest.raises(PlanRefused):
        ExecutionPlan(target=target(), steps=(), mutations=(GROUP, GROUP))
    step = CommandStep(
        step_id="S1", band="b", run_as="root", argv=("/usr/bin/id",), purpose="p"
    )
    with pytest.raises(PlanRefused):
        ExecutionPlan(target=target(), steps=(step, step), mutations=())


@pytest.mark.parametrize(
    "placeholder",
    ["<TARGET_ROOT>", "<EVIDENCE_DB>", "<PG_CONFIG_DIR>", "<PG_SOCKET_DIR>", "<TARGET_HOST>"],
)
def test_the_execution_plan_documents_placeholder_tokens_cannot_be_run(placeholder: str) -> None:
    """`docs/review/phase-5-0-evidence-harness-execution-plan.md` writes every
    target-derived path as `<TARGET_ROOT>/…` until concrete vectors are
    regenerated and independently reviewed for the assigned target.

    That form is not merely conventional — the planner **refuses** it, because `<`
    and `>` are shell metacharacters and no argument may carry one. So the
    document's vectors cannot be lifted and run: they have to be regenerated by
    the harness against the target the Operations Owner has named, and that
    regeneration is what re-applies every guard in `targets.py`.
    """
    with pytest.raises(PlanRefused):
        validate_argv(("/usr/bin/chattr", "+a", f"{placeholder}/probe/target"), target=target())


def test_a_plan_carries_the_not_executed_banner() -> None:
    plan = ExecutionPlan(target=target(), steps=(), mutations=())
    assert plan.review_state == "NOT EXECUTED — CODEX PRE-EXECUTION REVIEW REQUIRED"


# ---------------------------------------------------------------------------
# The runner
# ---------------------------------------------------------------------------


def test_the_only_runner_records_intent_and_executes_nothing() -> None:
    step = CommandStep(
        step_id="S1",
        band="identity",
        run_as="root",
        argv=("/usr/sbin/groupadd", "--system", "freedomjournal"),
        purpose="create the freedomjournal group",
        mutation_ids=(GROUP.mutation_id,),
    )
    plan = ExecutionPlan(target=target(), steps=(step,), mutations=(GROUP,))

    invocations = plan.dry_run()

    assert [invocation.argv for invocation in invocations] == [step.argv]
    assert all(invocation.executed is False for invocation in invocations)


def test_the_runner_has_no_execute_method_of_any_kind() -> None:
    runner = DryRunRunner()
    for forbidden in ("execute", "call", "spawn", "popen", "check_output"):
        assert not hasattr(runner, forbidden)


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------


def test_every_mutation_kind_has_exactly_one_reversal() -> None:
    """A kind with no reversal cannot exist, which is how 'cleanup is bounded'
    stops being a promise. A future kind fails here on the day it is added."""
    assert set(_REVERSALS) == set(MutationKind)


def test_cleanup_runs_in_reverse_declaration_order() -> None:
    mutations = (GROUP, ACCOUNT, MEMBERSHIP, JOURNAL_DIR, PROBE_FILE)
    plan = CleanupPlan.for_mutations(target(), mutations)
    assert [step.mutation_ids for step in plan.steps] == [
        (mutation.mutation_id,) for mutation in reversed(mutations)
    ]
    assert {step.kind for step in plan.steps} == {CleanupStepKind.REVERSAL}


def test_no_cleanup_step_is_destructive_when_its_object_is_absent() -> None:
    plan = CleanupPlan.for_mutations(
        target(),
        (GROUP, ACCOUNT, MEMBERSHIP, JOURNAL_DIR, PROBE_FILE, ROLE, config_line()),
    )
    assert plan.is_safe_to_rerun()
    assert all(step.argv[0] in NON_DESTRUCTIVE_WHEN_ABSENT for step in plan.steps)


def test_no_generated_cleanup_step_can_express_a_recursive_removal() -> None:
    plan = CleanupPlan.for_mutations(
        target(), (GROUP, ACCOUNT, MEMBERSHIP, JOURNAL_DIR, PROBE_FILE)
    )
    for step in plan.steps:
        assert not set(step.argv) & FORBIDDEN_CLEANUP_TOKENS
        # A directory is removed with `rmdir`, which cannot recurse; a file with
        # `rm --force`, which is one named path and no pattern.
        if step.argv[0] == "/usr/bin/rm":
            assert "--force" in step.argv and step.argv[-1].startswith("/var/lib/fb-evidence-")
        if step.argv[0] == "/usr/bin/rmdir":
            assert step.argv == ("/usr/bin/rmdir", "--", step.removes)


@pytest.mark.parametrize(
    "argv",
    [
        ("/usr/bin/rm", "-rf", "/var/lib/fb-evidence-r1"),
        ("/usr/bin/rm", "-r", "/var/lib/fb-evidence-r1"),
        ("/usr/bin/rm", "--recursive", "/var/lib/fb-evidence-r1"),
        ("/usr/bin/rm", "--force", "*"),
        ("/usr/bin/rm", "--no-preserve-root", "/"),
        ("/usr/bin/rm", "--force", "-a", "/var/lib/fb-evidence-r1/probe"),
    ],
)
def test_a_hand_written_recursive_cleanup_step_is_refused(argv) -> None:
    """The current constructor, with the current vocabulary.

    Recursion and breadth are refused by `CleanupStep.__post_init__`, not by the
    generator alone — so a step written by hand, in the shape a future edit might
    write one, cannot express what the generator cannot.
    """
    with pytest.raises(PlanRefused) as refusal:
        CleanupStep(
            step_id="CL-99",
            kind=CleanupStepKind.REVERSAL,
            run_as="root",
            argv=argv,
            removes="/var/lib/fb-evidence-r1/probe",
            mutation_ids=("file:/var/lib/fb-evidence-r1/probe",),
            satisfying_statuses=(0,),
        )
    assert "cannot be expressed" in str(refusal.value)


def test_a_hand_written_cleanup_step_that_reverses_nothing_is_refused() -> None:
    """Every cleanup command in this harness is generated from a declared
    mutation, so a removal that names none has no declaration behind it."""
    with pytest.raises(PlanRefused) as refusal:
        CleanupStep(
            step_id="CL-99",
            kind=CleanupStepKind.REVERSAL,
            run_as="root",
            argv=("/usr/bin/rm", "--force", "--", "/var/lib/fb-evidence-r1/probe/target"),
            removes="/var/lib/fb-evidence-r1/probe/target",
        )
    assert "reverses no declared mutation" in str(refusal.value)


def test_cleanup_of_a_path_outside_the_target_is_refused() -> None:
    outside = Mutation(MutationKind.FILE, "/etc/passwd", "not ours")
    with pytest.raises(TargetRefused):
        CleanupPlan.for_mutations(target(), (outside,))


def test_the_configuration_restore_reinstalls_the_pre_change_capture() -> None:
    plan = CleanupPlan.for_mutations(target(), (config_line(),))
    argv = plan.steps[0].argv
    assert plan.steps[0].kind is CleanupStepKind.RESTORE
    assert argv[0] == "/usr/bin/install"
    assert argv[-2] == "/var/lib/fb-evidence-r1/before/pg_hba.conf"
    assert argv[-1] == "/etc/postgresql/17/fbevidence/pg_hba.conf"


# ---------------------------------------------------------------------------
# EH-R3-2 — the configuration mapping contract
# ---------------------------------------------------------------------------

INCOMPLETE_MAPPINGS = [
    ("neither half", dict(maps_os_user="", maps_postgres_role="")),
    ("no OS identity", dict(maps_os_user="", maps_postgres_role=MAPPED_POSTGRES_ROLE)),
    ("no PostgreSQL role", dict(maps_os_user=MAPPED_OS_USER, maps_postgres_role="")),
    ("a blank OS identity", dict(maps_os_user="   ", maps_postgres_role=MAPPED_POSTGRES_ROLE)),
    ("a blank role", dict(maps_os_user=MAPPED_OS_USER, maps_postgres_role="   ")),
    (
        "an unusable OS identity",
        dict(maps_os_user="Freedom Coord", maps_postgres_role=MAPPED_POSTGRES_ROLE),
    ),
    (
        "a role that would have to be quoted",
        dict(maps_os_user=MAPPED_OS_USER, maps_postgres_role="Freedom-Migration-Coordinator"),
    ),
]


@pytest.mark.parametrize(
    "label, overrides", INCOMPLETE_MAPPINGS, ids=[m[0] for m in INCOMPLETE_MAPPINGS]
)
def test_a_configuration_mutation_without_a_complete_mapping_cannot_be_declared(
    label: str, overrides: dict
) -> None:
    """EH-R3-2, at the earliest point: the mutation itself.

    The post-reload proof connects **as** the mapped OS identity and asks for the
    mapped role. A configuration mutation that declares neither, or half, or a
    name no host or server could accept, describes a proof that cannot be
    constructed — so it is refused where it is declared, before a plan exists and
    long before a `CleanupStep` could be assembled out of it.
    """
    with pytest.raises(PlanRefused) as refusal:
        config_line(**overrides)
    assert "coordinator-peer-line" in str(refusal.value)


def test_a_configuration_mutation_naming_no_file_cannot_be_declared() -> None:
    with pytest.raises(PlanRefused) as refusal:
        config_line(file_path="")
    assert "names no file" in str(refusal.value)


def test_a_mutation_of_another_kind_cannot_carry_an_authentication_mapping() -> None:
    """Only a configuration line grants one, and only its cleanup proves one gone."""
    with pytest.raises(PlanRefused):
        Mutation(
            MutationKind.POSTGRES_ROLE,
            MAPPED_POSTGRES_ROLE,
            "the role",
            maps_os_user=MAPPED_OS_USER,
            maps_postgres_role=MAPPED_POSTGRES_ROLE,
        )


def test_a_complete_mapping_plans_the_whole_configuration_phase_in_order() -> None:
    """The positive case the finding asks for, end to end.

    Restore, then exactly one reload, then the positive connection control, then
    the refusal proof — and every step's identity, database and role come from
    the declared mapping rather than from a default.
    """
    plan = CleanupPlan.for_mutations(
        target(), (ROLE, config_line("hba-line"), config_line("ident-line", "pg_ident.conf"))
    )
    kinds = [step.kind for step in plan.steps]
    assert kinds == [
        CleanupStepKind.RESTORE,
        CleanupStepKind.RESTORE,
        CleanupStepKind.RELOAD,
        CleanupStepKind.VERIFY,
        CleanupStepKind.VERIFY,
        CleanupStepKind.REVERSAL,
    ]
    assert plan.ordering_holds()
    assert sorted(plan.restored_config_files()) == [
        "/etc/postgresql/17/fbevidence/pg_hba.conf",
        "/etc/postgresql/17/fbevidence/pg_ident.conf",
    ]

    #: Two lines, two files, one mapping: the proof is planned once.
    assert plan.verified_mappings() == (f"{MAPPED_OS_USER}->{MAPPED_POSTGRES_ROLE}",)
    proof = plan.verification_steps[-1]
    assert proof.refusal_required is True
    assert proof.run_as == MAPPED_OS_USER
    assert proof.argv[proof.argv.index("--username") + 1] == MAPPED_POSTGRES_ROLE
    assert proof.is_satisfied_by(2) and not proof.is_satisfied_by(0)

    #: The `DROP ROLE` runs after the reload, so it connects under the restored
    #: rules — and after the proof, so the refusal is attributable to the removed
    #: mapping rather than to a role that no longer exists.
    assert plan.steps[-1].kind is CleanupStepKind.REVERSAL
    assert "/usr/bin/psql" == plan.steps[-1].argv[0]


def test_no_blank_identity_or_role_can_reach_a_cleanup_step() -> None:
    """The last of the three guards, exercised directly.

    `Mutation` refuses an incomplete pair, so this can only be reached by
    bypassing the constructor — which is exactly what a future edit that
    reintroduced an optional mapping would do. The refusal names the mutation and
    both halves, and no production identity is substituted for either.
    """
    from tools.phase_5_0_evidence.cleanup import _require_complete_mapping

    #: Written past the constructor deliberately, because the constructor is the
    #: first guard and this test is about the last one.
    smuggled = config_line()
    object.__setattr__(smuggled, "maps_os_user", "")
    with pytest.raises(PlanRefused) as refusal:
        _require_complete_mapping(smuggled)
    message = str(refusal.value)
    assert "coordinator-peer-line" in message
    assert "no production identity stands in" in message


def test_a_partial_setup_that_reached_one_file_still_restores_reloads_and_verifies() -> None:
    """*"Partial setup after only one configuration-file mutation still restores
    what was changed, reloads, and performs the applicable bounded verification."*

    An interrupted Band 6 that wrote `pg_hba.conf` and never reached
    `pg_ident.conf` declares one configuration mutation, and its cleanup is the
    whole phase over that one file — not a skipped reload, and not a reload with
    no proof after it.
    """
    plan = CleanupPlan.for_mutations(target(), (ROLE, config_line("hba-line")))
    assert plan.restored_config_files() == ("/etc/postgresql/17/fbevidence/pg_hba.conf",)
    assert len(plan.reload_steps) == 1
    assert len(plan.verification_steps) == 2
    assert plan.ordering_holds()

    #: And the completion rule is unchanged by the partiality: restore, reload,
    #: control and proof are all still required before cleanup is complete.
    declared = ConfigurationRestoration.declared_by(plan)
    assert declared.problems()
    complete = ConfigurationRestoration(
        declared_files=declared.declared_files,
        restored_files=declared.declared_files,
        declared_mappings=declared.declared_mappings,
        mappings_proven_ineffective=declared.declared_mappings,
        reload_succeeded=True,
        verification_control_succeeded=True,
    )
    assert complete.is_complete


UNFINISHED_CONFIGURATION = [
    ("the file was not restored", dict(restored_files=())),
    ("no reload was attempted", dict(reload_succeeded=None)),
    ("the reload failed", dict(reload_succeeded=False)),
    ("no post-reload observation was made", dict(verification_control_succeeded=None)),
    ("the control connection failed", dict(verification_control_succeeded=False)),
    ("the mapping was never proved gone", dict(mappings_proven_ineffective=())),
]


@pytest.mark.parametrize(
    "label, overrides",
    UNFINISHED_CONFIGURATION,
    ids=[c[0] for c in UNFINISHED_CONFIGURATION],
)
def test_any_unfinished_configuration_step_is_s_b_and_names_the_risk(
    label: str, overrides: dict
) -> None:
    """Restore, reload, control or proof failing yields S-B and names the risk —
    and a temporary authentication rule that may still be in force is residue
    that has no path, so it produces S-B on its own."""
    plan = CleanupPlan.for_mutations(target(), (config_line(),))
    declared = ConfigurationRestoration.declared_by(plan)
    fields = dict(
        declared_files=declared.declared_files,
        restored_files=declared.declared_files,
        declared_mappings=declared.declared_mappings,
        mappings_proven_ineffective=declared.declared_mappings,
        reload_succeeded=True,
        verification_control_succeeded=True,
    )
    fields.update(overrides)

    outcome = classify_cleanup(
        probe_passed=True, unremoved=(), configuration=ConfigurationRestoration(**fields)
    )
    assert outcome.state == "S-B"
    assert outcome.exit_code == 3
    assert outcome.residue == ()
    assert outcome.configuration_risk
    assert outcome.cleanup_state is CleanupState.RESIDUE
    assert "effective configuration is not proved restored" in outcome.message


def test_a_run_that_declared_no_configuration_mutation_has_nothing_to_restore() -> None:
    """The honest case, and the only one with no problems: a run that changed no
    configuration needs no reload and claims no proof."""
    plan = CleanupPlan.for_mutations(target(), (GROUP, JOURNAL_DIR))
    declared = ConfigurationRestoration.declared_by(plan)
    assert declared.nothing_to_restore
    assert declared.problems() == ()

    outcome = classify_cleanup(probe_passed=True, unremoved=(), configuration=declared)
    assert outcome.state == "S-C"
    assert "No configuration mutation was declared" in outcome.message


#: A run that declared no configuration mutation. `configuration` is a **required**
#: argument of `classify_cleanup`, and deliberately so: a default would let a run
#: that mutated `pg_hba.conf` reach S-C by saying nothing about it, which is the
#: shape of EH-R2-2. The tests below are about the filesystem half of the state
#: machine, so they state the configuration half explicitly rather than omitting it.
NO_CONFIGURATION = ConfigurationRestoration()


def test_the_cleanup_state_machine_separates_its_two_claims() -> None:
    """§2.13.2b: *"no generation or database artifact"* is unconditional;
    *"no transient residue"* is conditional on cleanup succeeding."""
    assert classify_cleanup(
        probe_passed=True, unremoved=(), configuration=NO_CONFIGURATION
    ).state == "S-C"
    assert classify_cleanup(
        probe_passed=False, unremoved=(), configuration=NO_CONFIGURATION
    ).state == "S-A"

    after_pass = classify_cleanup(
        probe_passed=True,
        unremoved=("/var/lib/fb-evidence-r1/probe",),
        configuration=NO_CONFIGURATION,
    )
    after_fail = classify_cleanup(
        probe_passed=False,
        unremoved=("/var/lib/fb-evidence-r1/probe",),
        configuration=NO_CONFIGURATION,
    )
    assert after_pass.state == after_fail.state == "S-B"
    assert after_pass.exit_code == 3
    assert classify_cleanup(
        probe_passed=False, unremoved=(), configuration=NO_CONFIGURATION
    ).exit_code == 2
    assert classify_cleanup(
        probe_passed=True, unremoved=(), configuration=NO_CONFIGURATION
    ).exit_code == 0


def test_cleanup_completion_does_not_rest_on_exit_status_alone() -> None:
    """A rerun evaluation cannot report completion from what the commands returned.

    Both runs below have every step exiting as the plan says it should. They
    differ only in what was *observed* afterwards, and only the second is S-C —
    which is the whole of EH-R2-2: `pg_reload_conf()` returns as soon as the
    signal is sent, so its exit status says the signal was sent and nothing more.
    """
    plan = CleanupPlan.for_mutations(target(), (config_line(),))
    declared = ConfigurationRestoration.declared_by(plan)
    assert all(step.is_satisfied_by(0) for step in plan.steps if not step.refusal_required)

    unobserved = classify_cleanup(probe_passed=True, unremoved=(), configuration=declared)
    assert unobserved.state == "S-B"

    observed = classify_cleanup(
        probe_passed=True,
        unremoved=(),
        configuration=ConfigurationRestoration(
            declared_files=declared.declared_files,
            restored_files=declared.declared_files,
            declared_mappings=declared.declared_mappings,
            mappings_proven_ineffective=declared.declared_mappings,
            reload_succeeded=True,
            verification_control_succeeded=True,
        ),
    )
    assert observed.state == "S-C"
    assert "observed to be in force" in observed.message


def test_residue_is_reported_by_absolute_path_and_never_cleaned() -> None:
    outcome = classify_cleanup(
        probe_passed=True,
        unremoved=("/var/lib/fb-evidence-r1/probe-ro/s4-2.target", "/var/lib/fb-evidence-r1/probe"),
        configuration=NO_CONFIGURATION,
    )
    assert outcome.residue == (
        "/var/lib/fb-evidence-r1/probe",
        "/var/lib/fb-evidence-r1/probe-ro/s4-2.target",
    )
    assert "refuses while these paths exist rather than cleaning them" in outcome.message
    assert outcome.cleanup_state is CleanupState.RESIDUE
