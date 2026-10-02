"""The generated vectors, the derived cleanup, and the review manifest.

The question this file answers is not *"does the generator run?"* but *"can the
generator emit something a reviewer would refuse?"* — so almost every test below
is a property over **every** generated vector rather than a spot check on one,
and the few spot checks are on the orderings §6 is specifically about.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.phase_5_0_evidence.approved_target import (
    APPROVED_TARGET,
    APPROVED_TARGET_FACTS,
    CONFIRMATION_TOKEN,
    TARGET_IDENTITY_DIGEST,
)
from tools.phase_5_0_evidence.capture import (
    MAX_VALUE_LENGTH,
    CapturePolicy,
    sanitize,
)
from tools.phase_5_0_evidence.cleanup import (
    FORBIDDEN_CLEANUP_TOKENS,
    CleanupPlan,
    CleanupStepKind,
    ConfigurationRestoration,
    classify_cleanup,
)
from tools.phase_5_0_evidence.cleanup import _REVERSALS
from tools.phase_5_0_evidence.concrete_plan import (
    COORDINATOR_ROLE,
    MAPPED_OS_USER,
    MAPPED_POSTGRES_ROLE,
    ConcretePlan,
    UnresolvedStep,
    build_concrete_plan,
    build_mutations,
)
from tools.phase_5_0_evidence.case_runtime import (
    BOOTSTRAP_VERBS,
    CASE_PROGRAM_SOURCE_PATH,
    INTERPRETER_PATH,
)
from tools.phase_5_0_evidence.errors import PlanRefused, TargetRefused
from tools.phase_5_0_evidence.required_cases import (
    REQUIRED_CASES,
    check_case_coverage,
)
from tools.phase_5_0_evidence.plan import (
    CONFIGURATION_ROLE,
    PERMITTED_EXECUTABLES,
    RETIRED_EXECUTABLES,
    CommandStep,
    EffectKind,
    MutationKind,
    StepRole,
    validate_argv,
)
from tools.phase_5_0_evidence import rp11_launch
from tools.phase_5_0_evidence.review_manifest import (
    COVERED_SOURCES,
    RP11_LAUNCH_COVERED,
    ReviewManifest,
    digests_match,
)
from tests.phase_5_0_evidence.harness_fixtures import load_test_source_bytes

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PLAN = build_concrete_plan()
ROOT = APPROVED_TARGET.root_path
CONFIG_DIR = APPROVED_TARGET.postgres_config_directory


@pytest.fixture(scope="module")
def plan() -> ConcretePlan:
    return PLAN


# ---------------------------------------------------------------------------
# No placeholder survives generation
# ---------------------------------------------------------------------------

PLACEHOLDERS = (
    "<TARGET_ROOT>",
    "<EVIDENCE_DB>",
    "<PG_CONFIG_DIR>",
    "<PG_SOCKET_DIR>",
    "<TARGET_HOST>",
    "TARGET_ROOT",
    "EVIDENCE_DB",
    "UNASSIGNED",
)


def test_no_generated_argument_carries_a_placeholder_or_a_variable(plan) -> None:
    for step in list(plan.steps) + list(plan.cleanup_plan.steps):
        for argument in step.argv:
            for placeholder in PLACEHOLDERS:
                assert placeholder not in argument, (step.step_id, argument)
            assert "$" not in argument, (step.step_id, argument)
            assert "%" not in argument or argument.startswith("--format="), (
                step.step_id,
                argument,
            )
            assert "*" not in argument and "?" not in argument
            assert "~" not in argument
            assert argument == argument.strip()


def commands(plan):
    """Every step that is a **command**. The descriptor-bound effects are not.

    r6 §6.4 retired `/usr/bin/install` and `/usr/bin/chattr`, and what replaced
    them carries no argument vector at all — so a test about argument vectors
    asks this for its subjects, and `test_every_effect_step_carries_no_vector`
    below asserts that the complement really is vectorless.
    """
    return [
        step
        for step in list(plan.steps) + list(plan.cleanup_plan.steps)
        if not step.is_effect
    ]


def effect_steps(plan):
    """Every descriptor-bound effect, from both halves of the plan."""
    return [
        step
        for step in list(plan.steps) + list(plan.cleanup_plan.steps)
        if step.is_effect
    ]


def test_every_generated_vector_revalidates_against_the_target(plan) -> None:
    """The generator's output is put back through the guard that would have
    refused it. A vector that only validates at construction is a vector nobody
    checked after the last edit."""
    for step in commands(plan):
        assert validate_argv(step.argv, target=plan.target) == step.argv


def test_every_effect_step_carries_no_vector_and_no_executable(plan) -> None:
    """**r6 §6.4.** An effect names no program, so there is none to validate.

    This is what retiring `install` and `chattr` means: the effects that
    replaced them are issued by the executor on a descriptor it holds, and there
    is no argument vector in which a different program could be named.
    """
    issued = effect_steps(plan)
    assert issued, "the generator emits descriptor-bound effects"
    for step in issued:
        assert step.argv == ()
        assert step.run_as == "root"
        with pytest.raises(PlanRefused):
            validate_argv(step.argv, target=plan.target)


def test_neither_retired_executable_appears_anywhere_in_the_plan(plan) -> None:
    """**r6 §6.4.** `install` and `chattr` are gone from every reviewed vector."""
    for step in list(plan.steps) + list(plan.cleanup_plan.steps):
        assert not (set(step.argv) & RETIRED_EXECUTABLES), step.step_id
    assert not (RETIRED_EXECUTABLES & PERMITTED_EXECUTABLES)
    assert len(PERMITTED_EXECUTABLES) == 20


def test_no_generated_command_resolves_through_path(plan) -> None:
    for step in commands(plan):
        executable = step.argv[0]
        assert executable.startswith("/"), step.step_id
        assert executable in PERMITTED_EXECUTABLES or executable == INTERPRETER_PATH


def test_no_generated_vector_names_a_shell_or_a_privilege_helper(plan) -> None:
    forbidden = {
        "/bin/sh",
        "/bin/bash",
        "/usr/bin/sh",
        "/usr/bin/bash",
        "/usr/bin/sudo",
        "/usr/bin/su",
        "/usr/bin/env",
    }
    for step in list(plan.steps) + list(plan.cleanup_plan.steps):
        assert not (set(step.argv) & forbidden), step.step_id


# ---------------------------------------------------------------------------
# Every path is the approved one
# ---------------------------------------------------------------------------


def _paths_in(argv) -> list[str]:
    return [argument for argument in argv if argument.startswith("/")]


def test_every_path_is_inside_the_target_or_is_one_of_the_named_exceptions(plan) -> None:
    """Three exceptions, each named and each with a reason.

    `/dev/null` is the read source `install` needs to create an empty file. The
    permitted distribution binaries are executables, not objects. The two
    PostgreSQL configuration files are the only paths the harness *writes*
    outside its root, and they are reached through `config_path()`, which knows
    two filenames and no third.
    """
    permitted_outside = set(PERMITTED_EXECUTABLES) | {
        f"{CONFIG_DIR}/pg_hba.conf",
        f"{CONFIG_DIR}/pg_ident.conf",
        "/usr/sbin/nologin",
        APPROVED_TARGET.postgres_socket_directory,
        # Conflict C-2, Option B. The interpreter is an executable, not an
        # object, and it is admitted only by the case-program grammar.
        INTERPRETER_PATH,
        # The reviewed case-program source. `install` is retired — r6 §6.4 — so
        # this no longer appears as its source; the path stays admitted because
        # the case-program grammar names the reviewed script as the
        # interpreter's argument.
        CASE_PROGRAM_SOURCE_PATH,
    }
    for step in list(plan.steps) + list(plan.cleanup_plan.steps):
        for path in _paths_in(step.argv):
            if path in permitted_outside:
                continue
            assert path == ROOT or path.startswith(ROOT + "/"), (step.step_id, path)


def test_only_pg_hba_and_pg_ident_are_written_outside_the_target_root(plan) -> None:
    """A *write* outside the root, specifically.

    Since r6 §6.4 there is no `install` vector to read a destination off. Every
    object this plan creates or changes outside the root is a descriptor-bound
    configuration effect, and both of them bind the same two reviewed
    components — which is now checked against the effect's declared set rather
    than inferred from the last word of a vector.
    """
    outside: set[str] = set()
    for step in effect_steps(plan):
        if not step.effect.components:
            assert step.effect.path.startswith(ROOT), step.step_id
            continue
        for component in step.effect.components:
            outside.add(f"{CONFIG_DIR}/{component}")
    assert outside == {
        f"{CONFIG_DIR}/pg_hba.conf",
        f"{CONFIG_DIR}/pg_ident.conf",
    }


def test_the_generated_plan_names_the_approved_database_and_never_freedom_test(plan) -> None:
    joined = " ".join(
        argument for step in list(plan.steps) + list(plan.cleanup_plan.steps)
        for argument in step.argv
    )
    assert "fb_evidence_p5_0" in joined
    assert "freedom_test" not in joined
    assert "freedom_prod" not in joined
    assert "freedom_platform" not in joined


def test_every_psql_step_uses_the_approved_socket_directory(plan) -> None:
    for step in commands(plan):
        if step.argv[0] != "/usr/bin/psql":
            continue
        assert "--host" in step.argv
        host = step.argv[step.argv.index("--host") + 1]
        assert host in (APPROVED_TARGET.postgres_socket_directory, "127.0.0.1")
        assert "--no-password" in step.argv, step.step_id


def test_postgresql_is_reloaded_and_never_restarted(plan) -> None:
    joined = " ".join(
        argument for step in list(plan.steps) + list(plan.cleanup_plan.steps)
        for argument in step.argv
    )
    assert "pg_reload_conf()" in joined
    for word in ("restart", "postgresql@16-main", "pg_ctl"):
        assert word not in joined


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------


def test_every_mutation_bearing_step_declares_its_mutations(plan) -> None:
    declared = {mutation.mutation_id for mutation in plan.mutations}
    for step in plan.steps:
        for mutation_id in step.mutation_ids:
            assert mutation_id in declared, step.step_id


def test_an_undeclared_mutation_cannot_be_planned() -> None:
    from tools.phase_5_0_evidence.plan import ExecutionPlan

    rogue = CommandStep(
        step_id="X-01",
        band="identity",
        run_as="root",
        argv=("/usr/sbin/groupadd", "--system", "freedomjournal"),
        purpose="create a group the plan does not declare",
        mutation_ids=("os_group:freedomjournal",),
    )
    with pytest.raises(PlanRefused):
        ExecutionPlan(target=APPROVED_TARGET, steps=(rogue,), mutations=())


def test_every_declared_mutation_is_bound_to_the_approved_target(plan) -> None:
    for mutation in plan.mutations:
        mutation.validate_against(plan.target)
        if mutation.kind in (MutationKind.FILE, MutationKind.FILE_ATTRIBUTE):
            assert mutation.identifier.startswith(ROOT + "/")
        if mutation.kind is MutationKind.DIRECTORY:
            assert mutation.identifier == ROOT or mutation.identifier.startswith(ROOT + "/")


def test_the_configuration_mutations_carry_the_complete_mapping(plan) -> None:
    config = [
        mutation
        for mutation in plan.mutations
        if mutation.kind is MutationKind.POSTGRES_CONFIG_LINE
    ]
    assert len(config) == 2
    for mutation in config:
        assert mutation.maps_os_user == MAPPED_OS_USER
        assert mutation.maps_postgres_role == MAPPED_POSTGRES_ROLE
        assert mutation.file_path.startswith(CONFIG_DIR + "/")
        assert mutation.file_path.rsplit("/", 1)[1] in ("pg_hba.conf", "pg_ident.conf")


def test_the_mapping_names_an_identity_and_a_role_and_nothing_else(plan) -> None:
    """No rule text, no address, no authentication method, no credential."""
    for mutation in plan.mutations:
        blob = f"{mutation.maps_os_user} {mutation.maps_postgres_role}"
        for leak in ("scram", "md5", "peer", "trust", "password=", "127.0.0.1", "/32"):
            assert leak not in blob


def test_a_target_deviation_is_refused_downstream_of_generation() -> None:
    """A plan built against a different root cannot be built at all when the
    root is not a valid mutation root, and is refused by the executor when it
    is. This proves the first half; `test_executor.py` proves the second."""
    from tools.phase_5_0_evidence.targets import DisposableTarget

    with pytest.raises(TargetRefused):
        build_mutations(
            DisposableTarget(
                host="oracle-test",
                root_path="/var/lib",
                database_name="fb_evidence_p5_0",
                postgres_socket_directory="/var/run/postgresql",
                confirmed_disposable=True,
                disposability_evidence="synthetic",
                postgres_config_directory="/etc/postgresql/16/main",
            )
        )


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------


def test_every_declared_mutation_has_exactly_one_reversal(plan) -> None:
    for mutation in plan.mutations:
        reversing = [
            step
            for step in plan.cleanup_plan.steps
            if mutation.mutation_id in step.mutation_ids
        ]
        assert len(reversing) == 1, mutation.mutation_id


def test_every_mutation_kind_can_actually_build_a_reversal() -> None:
    """**EH-R4-1's regression.**

    The suite used to assert that `_REVERSALS` had an entry per kind. It did —
    and the `FILE_ATTRIBUTE` entry emitted `chattr -i -a`, whose `-a` is a member
    of `FORBIDDEN_CLEANUP_TOKENS`, so `CleanupStep.__post_init__` refused it
    outright and the reversal could not be constructed under any input. A table
    with an entry is not a table with a working entry.
    """
    from tools.phase_5_0_evidence.plan import Mutation

    samples = {
        MutationKind.OS_GROUP: Mutation(MutationKind.OS_GROUP, "freedomjournal", "r"),
        MutationKind.OS_ACCOUNT: Mutation(MutationKind.OS_ACCOUNT, "fbprobe", "r"),
        MutationKind.GROUP_MEMBERSHIP: Mutation(
            MutationKind.GROUP_MEMBERSHIP, "fbprobe", "r", group="freedomjournal"
        ),
        MutationKind.DIRECTORY: Mutation(MutationKind.DIRECTORY, f"{ROOT}/journal", "r"),
        MutationKind.FILE: Mutation(MutationKind.FILE, f"{ROOT}/journal/x", "r"),
        MutationKind.FILE_ATTRIBUTE: Mutation(
            MutationKind.FILE_ATTRIBUTE, f"{ROOT}/journal/x", "r", file_path=f"{ROOT}/journal/x"
        ),
        MutationKind.POSTGRES_ROLE: Mutation(
            MutationKind.POSTGRES_ROLE, COORDINATOR_ROLE, "r"
        ),
        MutationKind.POSTGRES_DATABASE: Mutation(
            MutationKind.POSTGRES_DATABASE, APPROVED_TARGET.database_name, "r"
        ),
        MutationKind.POSTGRES_CONFIG_LINE: Mutation(
            MutationKind.POSTGRES_CONFIG_LINE,
            "pg_hba.conf:x",
            "r",
            file_path=f"{CONFIG_DIR}/pg_hba.conf",
            maps_os_user=MAPPED_OS_USER,
            maps_postgres_role=MAPPED_POSTGRES_ROLE,
        ),
        MutationKind.TRANSIENT_UNIT: Mutation(
            MutationKind.TRANSIENT_UNIT, "fb-evidence-s4.service", "r"
        ),
    }
    assert set(samples) == set(_REVERSALS) == set(MutationKind)
    for kind, mutation in samples.items():
        built = CleanupPlan.for_mutations(APPROVED_TARGET, [mutation])
        assert built.steps, kind
        assert built.is_safe_to_rerun()


def test_no_generated_cleanup_step_can_express_a_recursive_or_broad_removal(plan) -> None:
    for step in plan.cleanup_plan.steps:
        assert not (set(step.argv) & FORBIDDEN_CLEANUP_TOKENS), step.step_id
        if step.is_effect:
            # An effect expresses no breadth at all: it names one path
            # component under one held descriptor, and `DescriptorEffect`
            # refuses a separator, `.` and `..` at construction.
            assert "/" not in step.effect.name
            continue
        if step.argv[0] == "/usr/bin/rm":
            assert step.argv[1] == "--force" and step.argv[2] == "--"
            assert len(step.argv) == 4
        if step.argv[0] == "/usr/bin/rmdir":
            assert step.argv[1] == "--" and len(step.argv) == 3


def test_directories_are_removed_deepest_first_and_only_with_rmdir(plan) -> None:
    order = [
        step.argv[-1]
        for step in plan.cleanup_plan.steps
        if step.argv[:1] == ("/usr/bin/rmdir",)
    ]
    assert order[-1] == ROOT
    for shallower, deeper in zip(order, order[1:]):
        assert not shallower.startswith(deeper + "/") or len(shallower) >= len(deeper)
    # And nothing else **removes** a directory. **R16, conflict C-8** adds one
    # cleanup step that names the root and removes nothing: the revalidation that
    # re-reads its device and inode immediately before the `rmdir`, so a path
    # whose object was replaced does not inherit permission to have its
    # replacement deleted. It is a `REVALIDATE`, it reverses no mutation, and
    # `CleanupStep.__post_init__` refuses one that claims to.
    for step in plan.cleanup_plan.steps:
        if step.kind is CleanupStepKind.REVALIDATE:
            assert step.removes == "" and step.mutation_ids == ()
            continue
        if step.argv and step.argv[-1] in order:
            assert step.argv[0] == "/usr/bin/rmdir"


def test_attributes_are_cleared_before_their_files_are_removed(plan) -> None:
    """The ordering, now over the descriptor-bound clear rather than `chattr`."""
    positions = {step.step_id: index for index, step in enumerate(plan.cleanup_plan.steps)}
    cleared = [
        step
        for step in plan.cleanup_plan.steps
        if step.is_effect and step.effect.kind is EffectKind.CLEAR_FLAG
    ]
    assert cleared, "the derived cleanup clears the flags it set"
    for step in cleared:
        path = step.effect.path
        removal = [
            other
            for other in plan.cleanup_plan.steps
            if other.argv[:1] == ("/usr/bin/rm",) and other.argv[-1] == path
        ]
        assert removal, path
        assert positions[step.step_id] < positions[removal[0].step_id]


def test_memberships_are_removed_before_users_and_users_before_groups(plan) -> None:
    def first(executable: str) -> int:
        return min(
            index
            for index, step in enumerate(plan.cleanup_plan.steps)
            if step.argv[:1] == (executable,)
        )

    assert first("/usr/sbin/gpasswd") < first("/usr/sbin/userdel") < first("/usr/sbin/groupdel")


def test_configuration_is_restored_reloaded_verified_then_roles_dropped(plan) -> None:
    kinds = [step.kind for step in plan.cleanup_plan.steps]
    assert plan.cleanup_plan.ordering_holds()
    assert kinds.count(CleanupStepKind.RELOAD) == 1
    reload_at = kinds.index(CleanupStepKind.RELOAD)
    assert all(index < reload_at for index, kind in enumerate(kinds) if kind is CleanupStepKind.RESTORE)
    assert all(index > reload_at for index, kind in enumerate(kinds) if kind is CleanupStepKind.VERIFY)

    verifications = plan.cleanup_plan.verification_steps
    assert len(verifications) == 2
    control, proof = verifications
    assert control.refusal_required is False and control.run_as == "postgres"
    assert proof.refusal_required is True and proof.run_as == MAPPED_OS_USER
    assert proof.argv[proof.argv.index("--username") + 1] == MAPPED_POSTGRES_ROLE

    drops = [
        index
        for index, step in enumerate(plan.cleanup_plan.steps)
        if "DROP ROLE IF EXISTS " + COORDINATOR_ROLE in step.argv
        or f"DROP DATABASE IF EXISTS {APPROVED_TARGET.database_name}" in step.argv
    ]
    assert drops and min(drops) > max(
        index for index, kind in enumerate(kinds) if kind is CleanupStepKind.VERIFY
    )


def test_the_restore_verifies_the_byte_exact_capture_it_writes(plan) -> None:
    """**r6 §2.4.** The restore is verify-and-write, not a reinstall.

    The `install` this replaces copied from `R/before`, whose custody is the
    custody in question. The effect names the **independent** store's component
    instead, and the destination is derived from the reviewed configuration
    directory rather than read off the last word of a vector.
    """
    assert plan.cleanup_plan.restore_steps
    for step in plan.cleanup_plan.restore_steps:
        assert step.is_effect
        assert step.effect.kind is EffectKind.RESTORE_CONFIGURATION
        assert step.effect.configuration_role == CONFIGURATION_ROLE
        assert len(step.effect.components) == 1
        (component,) = step.effect.components
        assert step.effect.path == f"{CONFIG_DIR}/{component}"


def test_the_capture_the_restore_needs_is_published_before_the_configuration_changes(
    plan,
) -> None:
    """One capture effect, binding both reviewed components, before M1."""
    captures = [
        step
        for step in plan.steps
        if step.is_effect and step.effect.kind is EffectKind.CAPTURE_CONFIGURATION
    ]
    assert len(captures) == 1
    (capture,) = captures
    assert set(capture.effect.components) == {"pg_hba.conf", "pg_ident.conf"}
    order = {step.step_id: index for index, step in enumerate(plan.steps)}
    for materialization in plan.materializations:
        assert materialization.capture_step_id == capture.step_id
        assert order[materialization.after_step_id] >= order[capture.step_id]


def test_a_partial_run_that_reached_one_configuration_file_still_gets_the_whole_phase(plan) -> None:
    one = [
        mutation
        for mutation in plan.mutations
        if mutation.kind is MutationKind.POSTGRES_CONFIG_LINE
    ][:1]
    partial = CleanupPlan.for_mutations(APPROVED_TARGET, one)
    assert len(partial.restore_steps) == 1
    assert len(partial.reload_steps) == 1
    assert len(partial.verification_steps) == 2
    assert partial.ordering_holds()


def test_failed_cleanup_is_s_b_and_names_the_residue(plan) -> None:
    outcome = classify_cleanup(
        probe_passed=True,
        unremoved=(f"{ROOT}/journal",),
        configuration=ConfigurationRestoration.declared_by(plan.cleanup_plan),
    )
    assert outcome.state == "S-B" and outcome.exit_code == 3
    assert f"{ROOT}/journal" in outcome.residue
    assert "refuses while these paths exist" in outcome.message
    assert outcome.configuration_risk


# ---------------------------------------------------------------------------
# C-1 — the ruled target-root boundary, at the level of the generated plan
# ---------------------------------------------------------------------------


def test_the_only_vector_that_removes_the_root_is_a_non_recursive_rmdir(plan) -> None:
    """One reversal, one executable, three arguments, and no second primitive.

    `rmdir` removes an empty directory and nothing else. There is no `rm -r`, no
    `find -delete`, no second cleanup primitive for a directory, and
    `FORBIDDEN_CLEANUP_TOKENS` makes a recursive or wildcard form unexpressible
    even if one were written.
    """
    root_steps = [
        step for step in plan.cleanup_plan.steps if step.removes == ROOT
    ]
    assert len(root_steps) == 1
    (removal,) = root_steps
    assert removal.argv == ("/usr/bin/rmdir", "--", ROOT)
    assert removal.mutation_ids == (f"directory:{ROOT}",)
    assert not (set(removal.argv) & FORBIDDEN_CLEANUP_TOKENS)

    # And nothing else in the whole plan names the root as an object to remove.
    for step in list(plan.steps) + list(plan.cleanup_plan.steps):
        if not step.argv or step.argv[-1] != ROOT:
            continue
        # `stat` is R14's precondition `R-B-ROOT`: it stops a run early when the
        # root plainly already exists, and — since R14 — establishes nothing.
        #
        # **R16, conflict C-8** adds the interpreter, and only for the two
        # bootstrap verbs: `mkroot`, which creates the root exclusively and whose
        # success **is** the ownership the `rmdir` below rests on, and
        # `statroot`, which re-reads its identity before that `rmdir` runs.
        # Neither removes anything, and `case_runtime.BOOTSTRAP_VERBS` is what
        # confines them.
        assert step.argv[0] in ("/usr/bin/rmdir", "/usr/bin/install", "/usr/bin/namei",
                                "/usr/bin/findmnt", "/usr/bin/stat",
                                INTERPRETER_PATH), step.step_id
        if step.argv[0] == INTERPRETER_PATH:
            assert step.argv[-2] in BOOTSTRAP_VERBS, step.step_id
            assert step.argv[3] == CASE_PROGRAM_SOURCE_PATH, step.step_id


def test_the_root_is_created_by_exactly_one_step_and_reversed_by_exactly_one(plan) -> None:
    creators = [
        step.step_id for step in plan.steps if f"directory:{ROOT}" in step.mutation_ids
    ]
    reversers = [
        step.step_id
        for step in plan.cleanup_plan.steps
        if f"directory:{ROOT}" in step.mutation_ids
    ]
    assert len(creators) == 1 and len(reversers) == 1


def test_an_unexpectedly_non_empty_root_is_reported_as_residue_not_deleted(plan) -> None:
    """The consequence of `rmdir` refusing a non-empty directory.

    A root still holding an artifact the plan did not declare makes the reversal
    unsatisfied, which makes the path **residue**: state S-B, the path named in
    full, and the next invocation refusing rather than cleaning it. Nothing in
    the derived plan escalates to a recursive removal, which is the property the
    C-1 ruling turns on.
    """
    outcome = classify_cleanup(
        probe_passed=True,
        unremoved=(ROOT,),
        configuration=ConfigurationRestoration(),
    )
    assert outcome.state == "S-B" and outcome.exit_code == 3
    assert outcome.residue == (ROOT,)
    assert "refuses while these paths exist rather than cleaning them" in outcome.message
    assert not any(
        token in outcome.message for token in ("rm -r", "--recursive", "-rf")
    )


def test_a_cleanup_step_outside_the_target_cannot_be_generated() -> None:
    from tools.phase_5_0_evidence.plan import Mutation
    from tools.phase_5_0_evidence.targets import DisposableTarget

    with pytest.raises(TargetRefused):
        Mutation(
            MutationKind.FILE, "/etc/passwd", "r"
        ).validate_against(APPROVED_TARGET)
    assert isinstance(APPROVED_TARGET, DisposableTarget)


# ---------------------------------------------------------------------------
# Unresolved conflicts
# ---------------------------------------------------------------------------


def test_the_plan_declares_the_evidence_it_cannot_produce(plan) -> None:
    """**R16.** C-1 … C-8 are resolved, and nothing is unresolved any more.

    ## What this assertion used to be, and why the change is not a relaxation

    R13's **EH-R13-4** was that `is_executable` said `True` while two whole
    groups of required evidence were missing. It asks whether every step the
    generator *tried* to express could be expressed, and it says nothing about a
    case the generator never tried to express. R14 then added C-8, a third
    blocker of a different kind: a missing **ownership proof** rather than
    missing evidence.

    All three are now implemented, and each is asserted against the property that
    would have been false before:

    * **C-6** — the three immutable-flag experiments are generated steps under
      `E4`, `E5` and `E6`, not case ids attached to identity observations;
    * **C-8** — the disposable root is created by an exclusive `mkdir(2)` whose
      success is its own ownership, so the 29 path mutations R14 left owned by
      nothing are owned again, by a claim the manifest pins; and
    * **C-7** — Band 7's observations have a validated ingestion route and a
      classifier that can start nothing.

    **C-7 is not closed, and R16's EH-R16-4 is why.** The route in is not a
    producer: the coordinator tooling that would arrange these three situations
    on the disposable host is Package 5.0's gated product work and does not
    exist. So the three cases are `UnresolvedStep`s under C-7, and
    `is_executable` is `False`. What is asserted here is that C-6 and C-8 are
    implemented **and** that the one remaining conflict is exactly C-7 and
    exactly those three cases — not that the plan is runnable.

    **C-P5.0-R5-R2, PLAN-1.** A second conflict, **C-S4-3**, now declares S4-3's
    producer dependency: the Stage-4 capture cannot pass condition 4.
    `test_r5_r2_s4_3_dependency.py` is its suite; here C-7 is asserted
    unchanged beside it.
    """
    assert plan.conflicts() == ("C-7", "C-S4-3")
    band_7 = [item for item in plan.unresolved if item.conflict_id == "C-7"]
    assert {item.band for item in band_7} == {"provenance", "journal"}
    assert {
        case_id for item in band_7 for case_id in item.evidence_case_ids
    } == {
        "JNL-51-PROVENANCE-OMITTED",
        "JNL-47-NO-GENERATION-ON-FAILURE",
        "JNL-47-RECOVERY-STATE",
    }
    assert [
        item.evidence_case_ids for item in plan.unresolved if item.conflict_id != "C-7"
    ] == [("S4-3",)]
    assert plan.is_executable is False

    # C-6: three experiments, run under the three identities §2.13.5c names.
    experiments = {
        case_id: step.step_id
        for step in plan.steps
        for case_id in step.evidence_case_ids
        if case_id.startswith(("JNL-49-", "JNL-50-"))
    }
    assert set(experiments) == {
        "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
        "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
    }

    # C-8: one exclusive creation, owning the root and everything inside it.
    creations = [step for step in plan.steps if step.establishes_ownership_by_creation]
    assert len(creations) == 1
    (creation,) = creations
    assert creation.establishes_ownership_by_creation == (f"directory:{ROOT}",)
    # 29 path mutations were blocked under R14: the root and the 28 inside it.
    # The root is owned by the creation itself and the 28 by what that creation
    # returned, which is an empty directory.
    assert len(creation.establishes_ownership_of_contained) == 28
    assert (
        len(creation.establishes_ownership_by_creation)
        + len(creation.establishes_ownership_of_contained)
        == 29
    )
    assert creation.establishes_ownership_of == ()

    # C-7: three externally produced cases, each with a producer and a procedure.
    assert {item.case_id for item in plan.external_cases} == {
        "JNL-51-PROVENANCE-OMITTED",
        "JNL-47-NO-GENERATION-ON-FAILURE",
        "JNL-47-RECOVERY-STATE",
    }
    for item in plan.external_cases:
        assert item.producer.strip() and item.collection_procedure.strip()
        assert item.variants and item.why_not_a_step.strip()


def test_an_identity_observation_does_not_carry_a_matrix_case_id(plan) -> None:
    """EH-R13-4's other half: a case id names the step that produces it.

    R12 attributed `JNL-49-<identity>` and `JNL-50-<identity>` to the seven
    `capsh` steps that run the `identity` verb. Those steps observe an identity
    and perform no capability-matrix operation at all, so the matrix looked
    present in a plan containing none of it.
    """
    for step in plan.steps:
        if step.capture is CapturePolicy.CASE_IDENTITY:
            for case_id in step.evidence_case_ids:
                assert not case_id.startswith("JNL-49"), step.step_id
                assert not case_id.startswith("JNL-50"), step.step_id


def test_an_unresolved_step_is_not_a_command_step(plan) -> None:
    for item in plan.unresolved:
        assert isinstance(item, UnresolvedStep)
        assert not hasattr(item, "argv")
        assert item.design_requires and item.why_not_a_vector
        assert item.what_would_resolve_it


def test_an_unresolved_step_without_a_stated_resolution_is_refused() -> None:
    with pytest.raises(PlanRefused):
        UnresolvedStep(
            step_ref="X",
            band="identity",
            conflict_id="C-9",
            design_requires="something",
            why_not_a_vector="reasons",
            what_would_resolve_it="  ",
        )


def test_the_capability_band_generates_every_constructible_identity(plan) -> None:
    """`E1 … E6` and `E8` are `capsh` vectors; `E7` is not, and it is neither
    unresolved nor unobserved.

    `E7` is the harness's own root identity, produced by dropping nothing, so a
    `capsh` construction for it would be something §2.13.5c does not describe.
    R12 concluded from that that it could not be **observed** either, which was
    Blocking finding EH-R12-1; it is observed by `P-06`, which runs the same
    `identity` verb through the direct Option-B vector. `test_root_identity.py`
    is that step's suite.
    """
    generated = {step.step_id for step in plan.steps if step.step_id.startswith("B5-E")}
    assert generated == {f"B5-E{n}" for n in (1, 2, 3, 4, 5, 6, 8)}
    assert "B5-E7" not in generated
    observed = {
        step.identity_name
        for step in plan.steps
        if step.capture is CapturePolicy.CASE_IDENTITY
    }
    assert "E7" in observed and len(observed) == 8
    for step in plan.steps:
        if step.step_id.startswith("B5-E"):
            assert step.argv[0] == "/usr/sbin/capsh"
            assert any(argument.startswith("--drop=") for argument in step.argv)
            assert f"--shell={INTERPRETER_PATH}" in step.argv


# ---------------------------------------------------------------------------
# Step expectations
# ---------------------------------------------------------------------------


def test_no_mutation_bearing_step_may_record_more_than_its_exit_status(plan) -> None:
    """A step whose purpose is a side effect has no observation to make.

    **R16, conflict C-8** carves out exactly one exception, and it is not a
    relaxation of the rule but an instance of its reason. The exclusive creation
    of the disposable root has an observation to make: `created=yes` and the
    device and inode of the directory `mkdir(2)` just returned **are** the
    ownership evidence, and cleanup compares them before it removes anything. A
    step that recorded only its exit status could not tie ownership to an object.

    The carve-out is bounded by `CommandStep._validate_exclusive_creation`, which
    refuses the combination for any step that does not also declare its unique
    pre-existence status and the statuses in which it created nothing.
    """
    for step in plan.steps:
        if step.mutation_ids and not step.establishes_ownership_by_creation:
            assert step.capture is CapturePolicy.EXIT_STATUS_ONLY, step.step_id
    creations = [step for step in plan.steps if step.establishes_ownership_by_creation]
    assert len(creations) == 1
    (creation,) = creations
    assert creation.capture is CapturePolicy.CASE_RESULT
    assert creation.preexisting_statuses and creation.nothing_created_statuses


def test_a_mutation_bearing_step_cannot_require_a_refusal() -> None:
    with pytest.raises(PlanRefused):
        CommandStep(
            step_id="X",
            band="identity",
            run_as="root",
            argv=("/usr/sbin/groupadd", "--system", "freedomjournal"),
            purpose="p",
            mutation_ids=("os_group:freedomjournal",),
            satisfying_statuses=(),
            refusal_required=True,
        )


def test_every_step_declares_how_its_exit_status_is_judged(plan) -> None:
    for step in plan.steps:
        assert step.refusal_required or step.satisfying_statuses
        assert not (step.refusal_required and step.satisfying_statuses)
        assert isinstance(step.role, StepRole)


def test_the_positive_controls_precede_the_cases_that_depend_on_them(plan) -> None:
    first_control = min(
        index for index, step in enumerate(plan.steps) if step.role is StepRole.CONTROL
    )
    first_dependent = min(
        index for index, step in enumerate(plan.steps) if step.role is StepRole.DEPENDENT
    )
    assert first_control < first_dependent
    for band in {step.band for step in plan.steps if step.role is StepRole.DEPENDENT}:
        controls = [
            index
            for index, step in enumerate(plan.steps)
            if step.band == band and step.role is StepRole.CONTROL
        ]
        dependents = [
            index
            for index, step in enumerate(plan.steps)
            if step.band == band and step.role is StepRole.DEPENDENT
        ]
        assert controls and min(controls) < min(dependents), band


def test_prerequisites_about_the_host_come_before_every_mutation(plan) -> None:
    """The prerequisites whose subject is the **host** precede every mutation.

    `P-03`, `P-04`, `P-05` and `P-06` are the exception, and it is a ruled one
    rather than a leftover: their subject is the case program, which Band 3
    installs, so they cannot hold before it exists. R10 §R10.7 flagged the first
    two's position as inherited; conflict C-2's resolution settles it, and the
    next test asserts where all four now sit. `P-06` — the `E7` observation R13
    adds — is in that group for the same reason and for one more: it observes the
    identity by **running** the case program.
    """
    first_mutation = min(
        index for index, step in enumerate(plan.steps) if step.mutation_ids
    )
    host_prerequisites = [
        index
        for index, step in enumerate(plan.steps)
        if step.role is StepRole.PREREQUISITE
        and step.step_id not in ("P-03", "P-04", "P-05", "P-06")
    ]
    assert host_prerequisites and max(host_prerequisites) < first_mutation


def test_the_case_program_prerequisites_sit_between_its_install_and_its_first_use(
    plan,
) -> None:
    """The ordering R10 left unresolved, asserted rather than described."""
    order = {step.step_id: index for index, step in enumerate(plan.steps)}
    install = next(
        index
        for index, step in enumerate(plan.steps)
        if step.is_effect
        and step.effect.kind is EffectKind.INSTALL_PAYLOAD
        and step.effect.path.endswith("/bin/case")
    )
    # The first use **of the installed program**. The bootstrap vector runs the
    # reviewed source from the repository tree instead — conflict C-8 — because
    # a helper that creates the disposable root cannot first be installed inside
    # it, so it necessarily precedes the install and is not what `P-03` and
    # `P-04` are prerequisites for.
    first_use = min(
        index
        for index, step in enumerate(plan.steps)
        if (INTERPRETER_PATH in step.argv or f"--shell={INTERPRETER_PATH}" in step.argv)
        and CASE_PROGRAM_SOURCE_PATH not in step.argv
    )
    for step_id in ("P-03", "P-04"):
        assert install < order[step_id] < first_use, step_id
    # `P-05` is itself the first use: it runs the reviewed vector to establish
    # the runtime every later case depends on.
    assert order["P-05"] == first_use
    assert plan.steps[first_use].argv == plan.steps[order["P-05"]].argv
    # `P-06` — the `E7` observation — is the second, immediately after it: the
    # identity is observed through an interpreter already established as the
    # reviewed one, and before any case-program **operation**.
    assert order["P-06"] == order["P-05"] + 1


# ---------------------------------------------------------------------------
# Capture sanitisation
# ---------------------------------------------------------------------------

SENTINEL = "SUPERSECRETsentinelVALUE"


@pytest.mark.parametrize("policy", list(CapturePolicy))
def test_a_planted_secret_sentinel_cannot_reach_an_observation(policy: CapturePolicy) -> None:
    """The sentinel is planted in every field shape a policy might read.

    It survives only where it would be a legitimate value of a field whose
    meaning the reviewed plan already fixed — a group *name*, say — and never as
    free text, never in a field the policy does not read, and never longer than
    the bound.
    """
    hostile = "\n".join(
        [
            f"password={SENTINEL} host=10.0.0.1 rule='local all all trust'",
            f"CapPrm: {SENTINEL}",
            f"Securebits: {SENTINEL}",
            f"junk:{SENTINEL}:{SENTINEL}:{SENTINEL}",
            f"uid=0({SENTINEL}) gid=0({SENTINEL})",
            SENTINEL * 20,
        ]
    )
    observations = sanitize(policy, hostile)
    for name, value in observations:
        assert len(value) <= MAX_VALUE_LENGTH
        assert "password=" not in value
        assert "trust" not in value
        assert "10.0.0.1" not in value
        assert "'" not in value and '"' not in value
        assert isinstance(name, str) and isinstance(value, str)


def test_the_exit_status_only_policy_records_nothing_at_all() -> None:
    assert sanitize(CapturePolicy.EXIT_STATUS_ONLY, "anything at all") == ()


def test_an_unreadable_output_is_marked_rather_than_guessed() -> None:
    assert sanitize(CapturePolicy.GROUP_MEMBERS, "not a group line") == (
        ("parse", "unreadable"),
    )
    assert sanitize(CapturePolicy.MOUNT_FACTS, "") == (("parse", "unreadable"),)


def test_the_capture_policies_read_the_field_they_claim_to() -> None:
    assert sanitize(CapturePolicy.GROUP_MEMBERS, "freedomjournal:x:998:freedomsheet,freedomcoord") == (
        ("group", "freedomjournal"),
        ("gid", "998"),
        ("members", "freedomcoord,freedomsheet"),
    )
    # **R13.** The two flags §2.13.3 is about, each a yes/no, and no other
    # letter: `e` is on every ext4 inode and absent elsewhere, so the whole
    # letter set could not be compared against a reviewed expectation without
    # the plan knowing the host's filesystem.
    assert sanitize(CapturePolicy.ATTRIBUTE_FLAGS, "-----a-------------- /var/lib/x") == (
        ("append_only", "yes"),
        ("immutable", "no"),
    )
    assert sanitize(
        CapturePolicy.ATTRIBUTE_FLAGS, "----i---------e------ /var/lib/x"
    ) == (("append_only", "no"), ("immutable", "yes"))
    assert sanitize(CapturePolicy.MOUNT_FACTS, "ext4 /dev/sda1 rw,relatime") == (
        ("fstype", "ext4"),
        ("source", "/dev/sda1"),
        ("read_only", "no"),
    )
    assert sanitize(CapturePolicy.FILE_CAPABILITIES, "") == (
        ("file_capability_present", "no"),
    )


# ---------------------------------------------------------------------------
# The review manifest
# ---------------------------------------------------------------------------


def _sources() -> dict[str, bytes]:
    return load_test_source_bytes()


def test_the_manifest_is_byte_deterministic(plan) -> None:
    first = ReviewManifest.build(plan, _sources()).serialize()
    second = ReviewManifest.build(build_concrete_plan(), _sources()).serialize()
    assert first == second
    assert first.endswith(b"\n")


def test_the_manifest_carries_every_vector_mutation_and_cleanup_step(plan) -> None:
    body = ReviewManifest.build(plan, _sources()).as_mapping()
    assert len(body["steps"]) == len(plan.steps)
    assert len(body["mutations"]) == len(plan.mutations)
    assert len(body["cleanup_steps"]) == len(plan.cleanup_plan.steps)
    assert len(body["unresolved"]) == len(plan.unresolved)
    assert len(body["source_digests"]) == len(COVERED_SOURCES)
    assert body["target_identity"] == "oracle-test:/var/lib/fb-evidence-p5-0"
    assert {row["state"] for row in body["exit_classifications"]} == {
        "S-A",
        "S-B",
        "S-C",
        "REFUSED",
    }
    facts = {row["name"]: row["value"] for row in body["target_facts"]}
    assert facts["active_kernel"] == APPROVED_TARGET_FACTS.active_kernel
    # **C-P5.0-LAB-I3-R5.** The kernel nodename is pinned as approved identity
    # in its own right, beside — never instead of — the operational SSH alias,
    # so a reviewer approves both names and a change to either moves the digest.
    assert facts["kernel_nodename"] == APPROVED_TARGET_FACTS.kernel_nodename == "Test"
    assert facts["host"] == APPROVED_TARGET_FACTS.host == "oracle-test"
    assert body["target_identity_digest"] == TARGET_IDENTITY_DIGEST
    assert body["confirmation_token"] == CONFIRMATION_TOKEN


def test_a_changed_source_file_changes_the_digest(plan) -> None:
    baseline = ReviewManifest.build(plan, _sources()).digest()
    tampered = _sources()
    tampered[COVERED_SOURCES[0]] += b"# one more comment\n"
    assert ReviewManifest.build(plan, tampered).digest() != baseline


def test_a_manifest_over_a_subset_of_the_sources_is_refused(plan) -> None:
    incomplete = _sources()
    incomplete.pop(COVERED_SOURCES[0])
    with pytest.raises(PlanRefused):
        ReviewManifest.build(plan, incomplete)

    extra = _sources()
    extra["tools/phase_5_0_evidence/somewhere_else.py"] = b""
    with pytest.raises(PlanRefused):
        ReviewManifest.build(plan, extra)


def test_the_covered_sources_are_exactly_the_package(plan) -> None:
    """A module added to either tier without being covered would be a module the
    reviewed digest says nothing about."""
    from pathlib import Path

    package = Path(__file__).resolve().parents[2] / "tools" / "phase_5_0_evidence"
    on_disk = {
        str(path.relative_to(package.parents[1]))
        for path in package.rglob("*.py")
        if "__pycache__" not in path.parts
    }
    # **27.** The package, exactly, plus the enumerated launcher files proposal
    # §5.11 binds — and nothing else.
    assert on_disk.isdisjoint(RP11_LAUNCH_COVERED)
    assert on_disk | set(RP11_LAUNCH_COVERED) == set(COVERED_SOURCES)
    assert len(COVERED_SOURCES) == len(set(COVERED_SOURCES))


def test_digest_comparison_is_exact_but_tolerates_surrounding_whitespace() -> None:
    assert digests_match("  ABCdef  ", "abcdef")
    assert not digests_match("", "abcdef")
    assert not digests_match("abcde", "abcdef")
    assert not digests_match("abcdef", "abcdeg")


# ---------------------------------------------------------------------------
# C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R2 — cc1.v baseline contract integration tests
# ---------------------------------------------------------------------------


def test_baseline_fixture_is_explicitly_in_reviewed_coverage_set() -> None:
    """The cc1.v baseline fixture is explicitly enumerated in RP11_LAUNCH_COVERED
    and COVERED_SOURCES (prompt §3 items 1 & 7).
    """
    assert rp11_launch.CC1_V_BASELINE_PATH == "infra/rp11-launch/verify/fixtures/cc1.v.baseline"
    assert rp11_launch.CC1_V_BASELINE_PATH in RP11_LAUNCH_COVERED
    assert rp11_launch.CC1_V_BASELINE_PATH in COVERED_SOURCES
    assert len(COVERED_SOURCES) == len(set(COVERED_SOURCES))


def _real_fixture_sources() -> dict[str, bytes]:
    return _sources()


def test_baseline_contract_serialized_in_manifest(plan) -> None:
    """The baseline contract is serialized in rp11_launch section of the review manifest
    with stable field names and deterministic values (prompt §3 item 2).
    """
    manifest = ReviewManifest.build(plan, _real_fixture_sources())
    body = manifest.as_mapping()
    assert "cc1_v_baseline" in body["rp11_launch"]
    contract = body["rp11_launch"]["cc1_v_baseline"]
    assert contract == {
        "byte_length": 5120,
        "path": "infra/rp11-launch/verify/fixtures/cc1.v.baseline",
        "sha256": "b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b",
    }


def test_baseline_contract_rejects_missing_fixture(plan) -> None:
    """Manifest construction rejects when the baseline fixture is omitted (prompt §3 item 7)."""
    incomplete = dict(_sources())
    incomplete.pop(rp11_launch.CC1_V_BASELINE_PATH)
    with pytest.raises(PlanRefused, match="covers every source file"):
        ReviewManifest.build(plan, incomplete)


def test_baseline_contract_rejects_one_byte_mutation(plan) -> None:
    """Manifest construction and contract verification reject a 1-byte mutation (prompt §3 item 7)."""
    tampered = _real_fixture_sources()
    orig = tampered[rp11_launch.CC1_V_BASELINE_PATH]
    mutated = bytes([orig[0] ^ 0x01]) + orig[1:]
    assert len(mutated) == len(orig) == 5120
    tampered[rp11_launch.CC1_V_BASELINE_PATH] = mutated

    with pytest.raises(PlanRefused, match="sha256.*does not match expected sha256"):
        ReviewManifest.build(plan, tampered)
    with pytest.raises(PlanRefused, match="sha256.*does not match expected sha256"):
        rp11_launch.verify_cc1_v_baseline(mutated)


def test_baseline_contract_rejects_appended_byte(plan) -> None:
    """Manifest construction and contract verification reject an appended byte (prompt §3 item 7)."""
    tampered = _real_fixture_sources()
    appended = tampered[rp11_launch.CC1_V_BASELINE_PATH] + b"\x00"
    assert len(appended) == 5121
    tampered[rp11_launch.CC1_V_BASELINE_PATH] = appended

    with pytest.raises(PlanRefused, match="length 5121 does not match expected length 5120"):
        ReviewManifest.build(plan, tampered)
    with pytest.raises(PlanRefused, match="length 5121 does not match expected length 5120"):
        rp11_launch.verify_cc1_v_baseline(appended)


def test_baseline_contract_rejects_truncated_fixture(plan) -> None:
    """Manifest construction and contract verification reject a truncated fixture (prompt §3 item 7)."""
    tampered = _real_fixture_sources()
    truncated = tampered[rp11_launch.CC1_V_BASELINE_PATH][:-1]
    assert len(truncated) == 5119
    tampered[rp11_launch.CC1_V_BASELINE_PATH] = truncated

    with pytest.raises(PlanRefused, match="length 5119 does not match expected length 5120"):
        ReviewManifest.build(plan, tampered)
    with pytest.raises(PlanRefused, match="length 5119 does not match expected length 5120"):
        rp11_launch.verify_cc1_v_baseline(truncated)


def test_baseline_contract_rejects_wrong_expected_length() -> None:
    """Contract verification rejects a wrong expected length (prompt §3 item 7)."""
    fixture_bytes = _real_fixture_sources()[rp11_launch.CC1_V_BASELINE_PATH]
    with pytest.raises(PlanRefused, match="length 5120 does not match expected length 5119"):
        rp11_launch.verify_cc1_v_baseline(fixture_bytes, expected_length=5119)
    with pytest.raises(PlanRefused, match="length 5120 does not match expected length 5121"):
        rp11_launch.verify_cc1_v_baseline(fixture_bytes, expected_length=5121)


def test_baseline_contract_rejects_wrong_expected_digest() -> None:
    """Contract verification rejects a wrong expected digest (prompt §3 item 7)."""
    fixture_bytes = _real_fixture_sources()[rp11_launch.CC1_V_BASELINE_PATH]
    wrong_digest = "0" * 64
    with pytest.raises(PlanRefused, match="does not match expected sha256"):
        rp11_launch.verify_cc1_v_baseline(fixture_bytes, expected_sha256=wrong_digest)


def test_baseline_fixture_omission_from_coverage_set_detected() -> None:
    """Omission of the fixture from the reviewed coverage set is detected (prompt §3 item 7)."""
    assert rp11_launch.CC1_V_BASELINE_PATH in RP11_LAUNCH_COVERED
    # If the fixture were omitted from RP11_LAUNCH_COVERED:
    hypothetical_covered = tuple(p for p in RP11_LAUNCH_COVERED if p != rp11_launch.CC1_V_BASELINE_PATH)
    assert rp11_launch.CC1_V_BASELINE_PATH not in hypothetical_covered
    assert len(hypothetical_covered) == len(RP11_LAUNCH_COVERED) - 1


# ---------------------------------------------------------------------------
# C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R3 — cc1.v verification bypass regression tests
# ---------------------------------------------------------------------------


def test_baseline_contract_rejects_former_51_byte_synthetic_placeholder(plan) -> None:
    """The former 51-byte synthetic placeholder is rejected by ReviewManifest.build()
    and rp11_launch.verify_cc1_v_baseline() (finding B1-R3-1 remediation, prompt §4.2 item 1).
    """
    synthetic_placeholder = f"# {rp11_launch.CC1_V_BASELINE_PATH}\n".encode("utf-8")
    assert len(synthetic_placeholder) == 51

    # 1. Direct contract verification rejects with length mismatch:
    with pytest.raises(PlanRefused, match="length 51 does not match expected length 5120"):
        rp11_launch.verify_cc1_v_baseline(synthetic_placeholder)

    # 2. ReviewManifest construction rejects unconditionally:
    tampered = _sources()
    tampered[rp11_launch.CC1_V_BASELINE_PATH] = synthetic_placeholder
    with pytest.raises(PlanRefused, match="length 51 does not match expected length 5120"):
        ReviewManifest.build(plan, tampered)


def test_baseline_contract_rejects_arbitrary_bytes_of_correct_length(plan) -> None:
    """Arbitrary bytes of the correct length (5120) are rejected by ReviewManifest.build()
    and rp11_launch.verify_cc1_v_baseline() (prompt §4.2 item 2).
    """
    arbitrary_bytes = b"\x00" * rp11_launch.CC1_V_BASELINE_LENGTH
    assert len(arbitrary_bytes) == 5120

    # 1. Direct contract verification rejects with sha256 mismatch:
    with pytest.raises(PlanRefused, match="sha256.*does not match expected sha256"):
        rp11_launch.verify_cc1_v_baseline(arbitrary_bytes)

    # 2. ReviewManifest construction rejects:
    tampered = _sources()
    tampered[rp11_launch.CC1_V_BASELINE_PATH] = arbitrary_bytes
    with pytest.raises(PlanRefused, match="sha256.*does not match expected sha256"):
        ReviewManifest.build(plan, tampered)


def test_baseline_contract_accepts_actual_fixture_bytes(plan) -> None:
    """Actual accepted fixture bytes are accepted by ReviewManifest.build()
    and rp11_launch.verify_cc1_v_baseline() (prompt §4.2 item 3).
    """
    actual_bytes = (REPOSITORY_ROOT / rp11_launch.CC1_V_BASELINE_PATH).read_bytes()
    assert len(actual_bytes) == 5120

    contract = rp11_launch.verify_cc1_v_baseline(actual_bytes)
    assert contract["byte_length"] == 5120
    assert contract["path"] == rp11_launch.CC1_V_BASELINE_PATH
    assert contract["sha256"] == rp11_launch.CC1_V_BASELINE_SHA256

    manifest = ReviewManifest.build(plan, _sources())
    assert manifest.baseline_contract == contract


def test_baseline_contract_serialized_from_verified_contract(plan) -> None:
    """The serialized path, length and digest come from a successfully verified
    fixture contract (prompt §4.2 item 4).
    """
    manifest = ReviewManifest.build(plan, _sources())
    body = manifest.as_mapping()
    assert "rp11_launch" in body
    assert "cc1_v_baseline" in body["rp11_launch"]
    serialized = body["rp11_launch"]["cc1_v_baseline"]
    assert serialized == {
        "byte_length": 5120,
        "path": "infra/rp11-launch/verify/fixtures/cc1.v.baseline",
        "sha256": "b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b",
    }
    assert manifest.baseline_contract == serialized
