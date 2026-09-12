"""**EH-R16-1, reproduced. These tests assert a defect, not a fix.**

Read the label before the assertions. Every case in §1 and §2 below asserts the
behaviour of the **current, unfixed** tree: that unsafe operations *are* issued.
They exist because the project-review prompt of 2026-09-09 permits synthetic
reproduction work while the corrected C-8 mechanism awaits Codex's technical
acceptance, and because a Blocking finding that no test demonstrates is a claim
rather than a defect.

**They will have to be inverted when the mechanism lands.** A green run of this
module is evidence that EH-R16-1 is still open. It is not verification of
anything, and nothing here models the proposed design: the proposed cases are
listed in §8 of
`docs/review/phase-5-0-evidence-harness-c8-ownership-design-r16-3.md` and are
marked there as unwritable until the mechanism exists.

**PR-20260909-R2-1/2, evidence correction.** Four cases in §1 and §2 now inject
an actual substitution through `FakeHost.injections`, applied in the interval
immediately before a named step, and assert on the **identity of the object** or
the **bytes** an effect consumed rather than on a command name or a state label:
the root replaced between its creation and the first `install -d`; the root
replaced before a later experiment; a descendant replaced in a
`freedomsheet`-writable directory while the root's identity stays correct; and a
recovery input replaced before the restore that installs it as the disposable
instance's authentication configuration. The earlier descendant case ran an
unchanged fake and checked that configured paths were removed — structural
evidence that no descendant identity is consulted, and not an injected
substitution. That distinction is why the fake now models identity and content.

§3 is different. It asserts the **inventory** §5 of that design rests on —
which directories the generated plan makes writable by which identity — against
the plan itself rather than against prose, so the residual a reviewer is asked
to size is checked rather than asserted. Those assertions hold before and after
the fix.

Everything runs across the injected fakes in `test_r13_remediation.py`. Nothing
starts a process, opens a socket, reads an account database or touches a host;
`test_no_execution.py` scans this file with the rest.
"""
from __future__ import annotations

import pytest

from tools.phase_5_0_evidence import case_runtime
from tools.phase_5_0_evidence.cleanup import CleanupStepKind
from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan
from tools.phase_5_0_evidence.execution.boundary import CommandResult
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES

from tests.phase_5_0_evidence.harness_fixtures import (
    runnable_plan,
    supply_reviewed_e7_facts,
)
from tests.phase_5_0_evidence.test_r13_remediation import (
    REVIEWED_INTERPRETER_DIGEST,
    REVIEWED_INTERPRETER_REAL_PATH,
    ROOT,
    FakeHost,
    runner,
)

SOURCES = {name: f"# {name}\n".encode("utf-8") for name in COVERED_SOURCES}

#: The two configuration files cleanup reinstalls from a capture that lives
#: **inside** the disposable root. They are the recovery inputs, and installing a
#: substituted one is the highest-consequence effect in the finding.
CAPTURES = (
    f"{ROOT}/before/pg_hba.conf",
    f"{ROOT}/before/pg_ident.conf",
)

#: The seven declared subjects that live in a directory the generated plan makes
#: group-writable by `freedomsheet` — §5.2 of the revised design.
GROUP_WRITABLE_SUBJECTS = (
    f"{ROOT}/probe/stage1.target",
    f"{ROOT}/probe/stage1.moved",
    f"{ROOT}/probe/stage2.target",
    f"{ROOT}/probe/s4-1.target",
    f"{ROOT}/probe-ro/s4-0.unlink",
    f"{ROOT}/probe-ro/s4-0.moved",
    f"{ROOT}/probe-ro/s4-2.target",
)


@pytest.fixture(autouse=True)
def _reviewed_target_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_SHA256", REVIEWED_INTERPRETER_DIGEST
    )
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_REAL_PATH", REVIEWED_INTERPRETER_REAL_PATH
    )
    supply_reviewed_e7_facts(monkeypatch)


def _revalidation_id(plan) -> str:
    return next(
        step.step_id
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVALIDATE
    )


def _replaced_root(host: FakeHost, plan, *, unreadable: bool = False) -> None:
    """Script the one revalidation as a root that is not the created one.

    Two shapes, because the design has to answer both: an object with a
    different inode, and an identity that could not be read at all.
    """
    observations = (
        (
            ("errno", "none"),
            ("result", "returned"),
            ("root_device", str(host.root_device)),
            ("root_inode", "unreadable"),
            ("verb", "statroot"),
        )
        if unreadable
        else (
            ("errno", "none"),
            ("result", "returned"),
            ("root_device", str(host.root_device)),
            ("root_inode", str(host.root_inode + 1)),
            ("verb", "statroot"),
        )
    )
    host.overrides[_revalidation_id(plan)] = CommandResult(
        exit_status=0, timed_out=False, observations=observations
    )


def _cleanup_vectors(host: FakeHost, plan) -> list[tuple[str, ...]]:
    """Every vector issued from the cleanup phase, in order."""
    cleanup_ids = {step.step_id for step in plan.cleanup_plan.steps}
    return [
        vector
        for step_id, vector in zip(host.calls, host.vectors)
        if step_id in cleanup_ids
    ]


def _index_of_guard(host: FakeHost, plan) -> int:
    cleanup_ids = {step.step_id for step in plan.cleanup_plan.steps}
    guard = _revalidation_id(plan)
    ordered = [step_id for step_id in host.calls if step_id in cleanup_ids]
    return ordered.index(guard)


def _cleanup_step_ids(host: FakeHost, plan) -> list[str]:
    cleanup_ids = {step.step_id for step in plan.cleanup_plan.steps}
    return [step_id for step_id in host.calls if step_id in cleanup_ids]


# ---------------------------------------------------------------------------
# 1. Root replacement before cleanup — the review's own reproduction
# ---------------------------------------------------------------------------


def test_a_replaced_root_still_has_its_configuration_captures_installed() -> None:
    """**[reproduction of an open defect]** The two `install` steps run first.

    R16: *"the executor first restores PostgreSQL configuration from that
    replacement's `before/` files"*. The run completes, every cleanup step is
    entitled to run, and the only ownership comparison is the one immediately
    before the root `rmdir` — so both restores are issued against sources that
    are, in this scenario, not the files this run wrote.

    Asserted from the boundary's call log, as the review requires: the presence
    of the commands, not the eventual state label.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    _replaced_root(host, plan)

    outcome = runner(plan, host).execute()

    installs = [
        vector
        for vector in _cleanup_vectors(host, plan)
        if vector[0] == "/usr/bin/install"
    ]
    assert len(installs) == 2
    assert {vector[-2] for vector in installs} == set(CAPTURES)

    # And they precede the only check there is.
    guard_at = _index_of_guard(host, plan)
    install_positions = [
        index
        for index, vector in enumerate(_cleanup_vectors(host, plan))
        if vector[0] == "/usr/bin/install"
    ]
    assert max(install_positions) < guard_at

    # The run is S-B and the root survives, which is the part that already works
    # — and which protects the root's inode and nothing else.
    assert outcome.cleanup.state == "S-B"
    assert ROOT in outcome.cleanup.residue
    assert ("/usr/bin/rmdir", "--", ROOT) not in host.vectors


def test_a_root_replaced_before_provisioning_receives_every_dependent_effect() -> None:
    """**[reproduction of an open defect]** — PR-20260909-R2-1's own scenario.

    The root is replaced in the interval between `B3-01`, which created it and
    recorded its identity, and `B3-03`, the first `install -d` under it. Every
    provisioning command, every flag change, the installed case program, the two
    configuration captures and every experiment then act on the replacement.

    A cleanup guard cannot undo any of that, and this is not the residual
    interval that follows a guard: **no execution-time guard is proposed at that
    point**, which the third assertion states structurally — not one `statroot`
    is issued between the creation and cleanup.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    recorded: dict[str, int] = {}
    replacement: dict[str, int] = {}

    def replace(current: FakeHost) -> None:
        recorded["identity"] = current.identity_of(ROOT)
        replacement["identity"] = current.substitute_root()

    host.injections["B3-03"] = replace

    outcome = runner(plan, host).execute()

    assert replacement["identity"] != recorded["identity"]

    cleanup_ids = {step.step_id for step in plan.cleanup_plan.steps}
    execution = [
        (step_id, vector)
        for step_id, vector in zip(host.calls, host.vectors)
        if step_id not in cleanup_ids
    ]
    issued_after = [
        step_id
        for step_id, _ in execution
        if step_id not in ("R-B-ROOT", "B3-01", "B3-02")
    ]

    # 1. The provisioning the substitution precedes is issued in full.
    directories = [
        vector
        for step_id, vector in execution
        if vector[0] == "/usr/bin/install" and "--directory" in vector
    ]
    assert {vector[-1] for vector in directories} >= {
        f"{ROOT}/journal", f"{ROOT}/archive", f"{ROOT}/before", f"{ROOT}/bin"
    }

    # 2. So are the flag changes and both configuration captures, all of which
    #    resolve names under a root this run no longer owns.
    assert any(vector[0] == "/usr/bin/chattr" for _, vector in execution)
    captures = [
        vector
        for step_id, vector in execution
        if step_id in ("B6-01", "B6-02")
    ]
    assert {vector[-1] for vector in captures} == set(CAPTURES)

    # 3. And nothing looked. Between `B3-01` and cleanup the plan issues no
    #    identity reading of any kind, so there is no guard for a replacement to
    #    race — there is no guard.
    assert issued_after
    assert not [
        vector for _, vector in execution if "statroot" in vector
    ]

    # The single comparison finally disagrees, in cleanup, after every effect
    # above has already landed.
    assert outcome.cleanup.state == "S-B"
    assert ROOT in outcome.cleanup.residue


def test_a_root_replaced_before_a_later_experiment_receives_its_effects() -> None:
    """**[reproduction of an open defect]** — the second injection R2-1 asks for.

    The same substitution, injected much later: immediately before `B5-C6-08`,
    a `chattr +i` on a file under the root, and well after the run has recorded
    the identity it will eventually compare. The flag change and every step
    after it are issued against the replacement.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    host.injections["B5-C6-08"] = lambda current: current.substitute_root()

    outcome = runner(plan, host).execute()

    order = list(host.calls)
    assert "B5-C6-08" in order
    after = order[order.index("B5-C6-08"):]
    by_id = dict(zip(host.calls, host.vectors))

    # The guarded-in-name-only flag change is issued.
    assert by_id["B5-C6-08"][0] == "/usr/bin/chattr"
    # As are the two captures, which come later in the plan and read and write
    # under the replacement.
    assert {"B6-01", "B6-02"} <= set(after)
    assert not [
        step_id for step_id in after if "statroot" in by_id[step_id]
        and step_id not in {step.step_id for step in plan.cleanup_plan.steps}
    ]

    assert outcome.cleanup.state == "S-B"


def test_a_replaced_root_has_its_descendants_removed_before_the_check() -> None:
    """**[reproduction of an open defect]** Count the commands that precede it.

    R16 counted *"30 cleanup commands referencing the root before that check"*.
    The count is asserted as a floor rather than an equality, so a step added to
    the plan does not turn a reproduction of the defect into a failure about
    arithmetic.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    _replaced_root(host, plan)

    runner(plan, host).execute()

    ordered = _cleanup_vectors(host, plan)
    guard_at = _index_of_guard(host, plan)
    before = ordered[:guard_at]
    touching_root = [
        vector
        for vector in before
        if any(argument.startswith(ROOT) for argument in vector)
    ]
    assert len(touching_root) >= 30

    removals = [
        vector
        for vector in before
        if vector[0] in ("/usr/bin/rm", "/usr/bin/rmdir", "/usr/bin/chattr")
    ]
    assert removals, "descendant removals are issued before the only check"


def test_an_unreadable_root_identity_also_only_stops_the_final_removal() -> None:
    """**[reproduction of an open defect]** A failed read fails closed — once.

    The guard itself is sound: an identity that could not be read is treated as a
    mismatch and the `rmdir` is skipped. What the finding is about is that this
    is the *only* place the answer is consulted, so an unreadable identity
    protects exactly one inode and nothing that was already removed.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    _replaced_root(host, plan, unreadable=True)

    outcome = runner(plan, host).execute()

    assert outcome.cleanup.state == "S-B"
    assert ROOT in outcome.cleanup.residue
    assert ("/usr/bin/rmdir", "--", ROOT) not in host.vectors
    assert [
        vector
        for vector in _cleanup_vectors(host, plan)
        if vector[0] == "/usr/bin/install"
    ]


def test_independently_safe_recovery_already_proceeds() -> None:
    """**[control, and a property the fix must preserve]** — P5 of the design.

    A failed root guard must not suppress the reversals whose subjects are not
    filesystem objects, or a root-replacement scenario would additionally leave
    three accounts, four groups, a role and a database behind. That holds today
    and the revised design keeps it; it is asserted here so a future change that
    gated everything on the guard would fail.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    _replaced_root(host, plan)

    runner(plan, host).execute()

    executables = {vector[0] for vector in _cleanup_vectors(host, plan)}
    assert "/usr/sbin/userdel" in executables
    assert "/usr/sbin/groupdel" in executables
    assert any(
        "DROP DATABASE IF EXISTS" in argument
        for vector in _cleanup_vectors(host, plan)
        for argument in vector
    )
    assert any(
        "DROP ROLE IF EXISTS" in argument
        for vector in _cleanup_vectors(host, plan)
        for argument in vector
    )


def test_ordinary_cleanup_still_completes() -> None:
    """**[control]** The guard is not merely a way to refuse.

    Without a successful control the reproductions above would pass against a
    cleanup that never did anything.
    """
    plan = runnable_plan()
    host = FakeHost(plan)

    outcome = runner(plan, host).execute()

    assert outcome.completed is True
    assert outcome.cleanup.state == "S-C"
    assert outcome.cleanup.residue == ()
    assert not host.has(f"path:{ROOT}")
    installs = [
        vector
        for vector in _cleanup_vectors(host, plan)
        if vector[0] == "/usr/bin/install"
    ]
    assert {vector[-2] for vector in installs} == set(CAPTURES)


# ---------------------------------------------------------------------------
# 2. Descendant replacement — undetected, and undetectable by the root guard
# ---------------------------------------------------------------------------


def test_a_replaced_descendant_is_removed_while_the_root_matches() -> None:
    """**[reproduction of an open defect]** An **injected** descendant substitution.

    R2's evidence correction: the earlier form of this case ran an unchanged
    fake and checked that the configured paths were removed, which is structural
    evidence that no descendant identity is consulted and *not* an injected
    substitution of an object. This form injects one.

    `…/probe/stage2.target` is unlinked and a different object is created under
    the same name, in the interval before `B4-19`, by an identity the plan
    itself constructs — `freedomsheet`, a member of the group that owns the
    `0770` directory the file is in. The root's identity never changes, so every
    guard the current design has agrees, and cleanup's `rm --force` consumes the
    **replacement**. The assertion names the identity of the object the removal
    acted on, not the command that was issued.
    """
    subject = f"{ROOT}/probe/stage2.target"
    plan = runnable_plan()
    host = FakeHost(plan)

    created: dict[str, int | None] = {}
    replacement: dict[str, int] = {}

    def replace(current: FakeHost) -> None:
        created["identity"] = current.identity_of(subject)
        replacement["identity"] = current.substitute(
            subject, content=b"# not this run's object\n"
        )

    host.injections["B4-19"] = replace

    outcome = runner(plan, host).execute()

    assert created["identity"] is not None
    assert replacement["identity"] != created["identity"]

    removals = [
        record
        for record in host.consumed
        if record.action == "rm" and record.path == subject
    ]
    assert len(removals) == 1
    # The object the removal consumed is the replacement, and it is
    # distinguishable from the object this run created.
    assert removals[0].identity == replacement["identity"]
    assert removals[0].identity != created["identity"]
    assert removals[0].content == b"# not this run's object\n"

    # And nothing objected: the root's identity is untouched, the single
    # comparison agrees, and the run reports a clean cleanup.
    assert outcome.cleanup.state == "S-C"

    # The other six subjects are removed in the same unguarded way.
    removed = {
        vector[-1]
        for vector in _cleanup_vectors(host, plan)
        if vector[0] == "/usr/bin/rm"
    }
    assert set(GROUP_WRITABLE_SUBJECTS) <= removed


def test_a_substituted_capture_is_installed_as_authentication_configuration() -> None:
    """**[reproduction of an open defect]** — PR-20260909-R2-2's own scenario.

    The recovery input in `…/before/pg_hba.conf` is replaced with different
    bytes in the interval before `CL-02`, the restore that installs it over the
    disposable instance's live `pg_hba.conf`. Nothing in the current tree reads
    the capture's content, so the substituted bytes are what reach the live
    file. The root's identity is unchanged throughout, which is the point: no
    identity claim in the design is violated, and the highest-consequence effect
    in the finding still lands.

    Asserted on **bytes**, not on a command name and not on a state label.
    """
    capture = f"{ROOT}/before/pg_hba.conf"
    live = "/etc/postgresql/16/main/pg_hba.conf"
    substituted = b"# substituted authentication configuration\n"

    plan = runnable_plan()
    host = FakeHost(plan)
    original = host.content_of(live)
    host.injections["CL-02"] = lambda current: current.substitute(
        capture, content=substituted
    )

    outcome = runner(plan, host).execute()

    # The bytes the restore consumed came from the replacement, and the bytes
    # now at the live pathname are those bytes rather than the ones captured.
    consumed = [
        record
        for record in host.consumed
        if record.step_id == "CL-02" and record.action == "install-source"
    ]
    assert len(consumed) == 1
    assert consumed[0].path == capture
    assert consumed[0].content == substituted
    assert host.content_of(live) == substituted
    assert host.content_of(live) != original

    # No guard fired, and the run reports the restoration as complete: no
    # configuration risk, no retained recovery input, no operator procedure.
    assert outcome.cleanup.state == "S-C"
    assert outcome.cleanup.configuration_risk == ()
    assert outcome.cleanup.retained_recovery_inputs == ()
    assert outcome.cleanup.recovery_procedure == ()


def test_no_cleanup_step_compares_a_descendant_identity() -> None:
    """**[reproduction of an open defect]** Structural, so it cannot pass by luck.

    Exactly one cleanup step reads an identity back, it names the root, and no
    other step carries a `requires_revalidated`.
    """
    plan = build_concrete_plan()
    revalidations = [
        step
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVALIDATE
    ]
    assert len(revalidations) == 1
    assert revalidations[0].argv[-1] == ROOT

    guarded = [
        step for step in plan.cleanup_plan.steps if step.requires_revalidated
    ]
    assert len(guarded) == 1
    assert guarded[0].removes == ROOT
    assert guarded[0].argv[0] == "/usr/bin/rmdir"

    # And the guard is the last thing before the removal it protects, which is
    # the whole of what the current mechanism achieves.
    ids = [step.step_id for step in plan.cleanup_plan.steps]
    assert ids.index(revalidations[0].step_id) + 1 == ids.index(guarded[0].step_id)


def test_the_configuration_restores_are_not_guarded_at_all() -> None:
    """**[reproduction of an open defect]** Structural, on the plan.

    Neither `RESTORE` step names a revalidation, and both precede the only one
    the plan generates. That is the shape of the finding stated against the plan
    rather than against a run.
    """
    plan = build_concrete_plan()
    restores = [
        step
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.RESTORE
    ]
    assert len(restores) == 2
    assert all(not step.requires_revalidated for step in restores)

    ids = [step.step_id for step in plan.cleanup_plan.steps]
    guard_at = ids.index(
        next(
            step.step_id
            for step in plan.cleanup_plan.steps
            if step.kind is CleanupStepKind.REVALIDATE
        )
    )
    assert all(ids.index(step.step_id) < guard_at for step in restores)

    # Each restore's source is inside the root, which is why it depends on the
    # root's identity in the first place.
    for step in restores:
        assert step.argv[-2].startswith(f"{ROOT}/before/")


# ---------------------------------------------------------------------------
# 3. The inventory the revised design's residual rests on
# ---------------------------------------------------------------------------


def _install_vectors(plan) -> list[tuple[str, ...]]:
    return [
        tuple(step.argv)
        for step in plan.steps
        if step.argv and step.argv[0] == "/usr/bin/install"
    ]


def test_two_directories_are_group_writable_by_a_created_identity() -> None:
    """**[inventory]** §5.1 of the revised design, checked against the plan.

    The rejected design said replacement inside the root requires uid 0 or
    `CAP_DAC_OVERRIDE` and that such an actor is outside the threat model. Two
    directories the plan creates are `0770` with a group the run itself creates,
    so membership of `freedomsheet` is enough.
    """
    plan = build_concrete_plan()
    directories = {
        vector[-1]: (vector[vector.index("--mode") + 1],
                     vector[vector.index("--owner") + 1],
                     vector[vector.index("--group") + 1])
        for vector in _install_vectors(plan)
        if "--directory" in vector
    }
    assert directories[f"{ROOT}/probe"] == ("0770", "root", "freedomsheet")
    assert directories[f"{ROOT}/probe-ro"] == ("0770", "root", "freedomsheet")
    # The four that are not group-writable, for contrast — and because `before`
    # holding the recovery inputs at 0700 is what the design leans on for them.
    assert directories[f"{ROOT}/before"] == ("0700", "root", "root")
    assert directories[f"{ROOT}/bin"] == ("0755", "root", "root")
    assert directories[f"{ROOT}/journal"][0] == "0750"
    assert directories[f"{ROOT}/archive"][0] == "0750"


def test_the_run_itself_unlinks_and_renames_inside_those_directories() -> None:
    """**[inventory]** The replacement sequence is the plan's own control flow.

    `freedomsheet` renames and unlinks entries in `probe` and `probe-ro` as part
    of the reviewed design, so *"the object this run created is gone and
    something else may be at its name"* is not a hypothesis about an adversary.
    """
    plan = build_concrete_plan()
    mutating = [
        step
        for step in plan.steps
        if step.run_as == "freedomsheet"
        and step.argv
        and len(step.argv) > 4
        and step.argv[4] in ("unlink", "rename")
    ]
    assert mutating, "the plan runs mutating verbs as freedomsheet"
    subjects = {argument for step in mutating for argument in step.argv[5:]}
    assert any(subject.startswith(f"{ROOT}/probe/") for subject in subjects)
    assert any(subject.startswith(f"{ROOT}/probe-ro/") for subject in subjects)


def test_two_experimental_identities_hold_ambient_dac_override() -> None:
    """**[inventory]** §5.1 again: `CAP_DAC_OVERRIDE` is inside the plan.

    An identity holding it may write in every directory under the root, `before`
    and `bin` included. That is why the rejected design's *"outside the threat
    model"* did not hold, and it is why the revised design proposes comparing the
    captures' **content** rather than reasoning about who could reach them.
    """
    plan = build_concrete_plan()
    ambient = [
        step
        for step in plan.steps
        if step.argv and "--addamb=cap_dac_override" in step.argv
    ]
    assert ambient
    assert all("--uid=fbprobe" in step.argv for step in ambient)
    assert {step.step_id for step in ambient} >= {"B5-E4", "B5-E6"}


def test_the_seven_replaceable_subjects_are_declared_mutations() -> None:
    """**[inventory]** §5.2's list is the plan's, not this file's.

    A hand-written list would drift. Every path in `GROUP_WRITABLE_SUBJECTS` is
    a declared mutation, and no declared path mutation outside the two `0770`
    directories is in it.
    """
    plan = build_concrete_plan()
    declared = {
        mutation.identifier
        for mutation in plan.mutations
        if mutation.identifier.startswith(f"{ROOT}/")
    }
    assert set(GROUP_WRITABLE_SUBJECTS) <= declared
    group_writable = {
        path
        for path in declared
        if path.startswith((f"{ROOT}/probe/", f"{ROOT}/probe-ro/"))
    }
    assert group_writable == set(GROUP_WRITABLE_SUBJECTS)


def test_the_root_parent_is_not_a_reviewed_target_fact() -> None:
    """**[inventory]** §4.3: the trust boundary is currently unestablished.

    The revised design's P1 proposes five parent facts. This asserts the premise
    that makes P1 necessary — the harness records nothing about the directory the
    root is created in, so an argument that leans on the parent's permissions
    leans on a value nobody has stated or verified.
    """
    from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET_FACTS

    names = {name for name, _ in APPROVED_TARGET_FACTS.as_fields()}
    assert not any("parent" in name for name in names)
