"""**EH-R16-1: what the mechanism now covers, and what it still does not.**

Read the label before the assertions. Until C-P5.0-LAB-I-R1 every case in §1 and
§2 below asserted the behaviour of the **unfixed** tree — that unsafe operations
*are* issued — and the module said in as many words: *"they will have to be
inverted when the mechanism lands."* r6 §6.4's retirement of `/usr/bin/install`
and `/usr/bin/chattr` is the mechanism landing for the effects those two
performed, so the cases that were about a **pathname re-resolved after an
ownership check** are inverted here: there is no longer a vector that resolves
one.

**EH-R16-1 is not closed by that, and this module is where the residual is
stated.** Three things are unchanged and each has its own case below:

* the **removal's final component** is not bindable by any syscall available
  here — r6 §1.4.5 — so `rm --force` and `rmdir` remain pathname-resolved and
  the pre-check detects rather than prevents;
* **in-place content mutation of a file whose inode is unchanged** is not
  covered by a descriptor at all — r6 §1.4.4; and
* the **inventory** in §3 is unchanged: two directories the plan creates are
  group-writable by an identity the run itself creates, and two experimental
  identities hold ambient `CAP_DAC_OVERRIDE`.

A green run of this module is evidence about which half of the finding the
mechanism reaches. It is not verification of anything on `oracle-test`.

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
from tools.phase_5_0_evidence.case_runtime import INTERPRETER_PATH
from tools.phase_5_0_evidence.cleanup import CleanupStepKind
from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan
from tools.phase_5_0_evidence.plan import EffectKind
from tools.phase_5_0_evidence.execution.boundary import (
    LAUNCH_EFFECT_REFUSED,
    CommandResult,
)
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES

from tests.phase_5_0_evidence.harness_fixtures import (
    runnable_plan,
    supply_reviewed_e7_facts,
    load_test_source_bytes,
)
from tests.phase_5_0_evidence.test_r13_remediation import (
    REVIEWED_INTERPRETER_DIGEST,
    REVIEWED_INTERPRETER_REAL_PATH,
    ROOT,
    FakeHost,
    runner,
)

SOURCES = load_test_source_bytes()

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


def test_a_replaced_root_no_longer_has_captures_reinstalled_from_under_it() -> None:
    """**[inverted — the mechanism reaches this one.]**

    R16 read: *"the executor first restores PostgreSQL configuration from that
    replacement's `before/` files"*. That was true of the two `install` vectors
    the restore used to be. Both are gone — r6 §6.4 — and the restoration is a
    descriptor-bound effect that verifies the bytes against the **independent**
    store, whose custody is not the custody this scenario is about. So a
    replaced root no longer supplies the bytes that become the disposable
    instance's authentication configuration.

    Asserted from the call log and from what the effect consumed, not from a
    state label.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    _replaced_root(host, plan)

    outcome = runner(plan, host).execute()

    # There is no `install` in the cleanup at all, and nothing read a source
    # under the disposable root.
    assert not [
        vector
        for vector in _cleanup_vectors(host, plan)
        if vector[0] == "/usr/bin/install"
    ]
    assert not [
        record for record in host.consumed if record.action == "install-source"
    ]
    restored = [record for record in host.consumed if record.action == "restore-source"]
    assert {record.path for record in restored} == {
        "/etc/postgresql/16/main/pg_hba.conf",
        "/etc/postgresql/16/main/pg_ident.conf",
    }

    # The root guard is unchanged: it still protects exactly one inode, and the
    # run is S-B.
    assert outcome.cleanup.state == "S-B"
    assert ROOT in outcome.cleanup.residue
    assert ("/usr/bin/rmdir", "--", ROOT) not in host.vectors


def test_a_root_replaced_before_provisioning_resolves_no_pathname_under_it() -> None:
    """**[inverted — PR-20260909-R2-1's own scenario, after the mechanism.]**

    The root is replaced in the interval between `B3-01`, which created it, and
    `B3-03`, which used to be the first `install -d` under it. What that
    scenario rested on was that every provisioning command **re-resolved a
    pathname** under the root. None of them does any more: P1, P1b, P2, P4 and
    L3's flag half are descriptor-bound effects with no argument vector at all,
    so there is no pathname for the replacement to be found through.

    The residual is stated in the last assertion and it is unchanged: the
    removals and the experiments still resolve names, and EH-R16-1 stays Open
    for them.
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

    # 1. The provisioning the substitution precedes resolves **no pathname**:
    #    every one of those steps is a descriptor-bound effect with no vector.
    provisioning = [
        step
        for step in plan.steps
        if step.mutation_ids
        and any(
            mutation_id.startswith(("directory:", "file:", "file_attribute:"))
            for mutation_id in step.mutation_ids
        )
        and any(ROOT in mutation_id for mutation_id in step.mutation_ids)
    ]
    assert provisioning
    # Everything that is not an effect is one of the reviewed case program's own
    # verbs, run through the approved interpreter. Those resolve names and are
    # the residual §1.4.4 keeps: the mechanism binds the executor's effects, not
    # the experiments', and EH-R16-1 stays Open for them.
    for step in provisioning:
        if step.is_effect:
            continue
        assert step.argv[0] == INTERPRETER_PATH, step.step_id

    # 2. And there is no `install` or `chattr` vector left to find a
    #    replacement through — the executable is not even permitted.
    assert not [
        vector
        for _, vector in execution
        if vector[:1] in (("/usr/bin/install",), ("/usr/bin/chattr",))
    ]

    # 3. The residual, stated rather than closed. No identity reading is issued
    #    between the creation and cleanup, and the case program's own verbs
    #    still resolve names under the root — which is the half of EH-R16-1 the
    #    descriptor chain does not reach, and why it stays Open.
    assert issued_after
    assert not [vector for _, vector in execution if "statroot" in vector]
    assert [
        vector
        for _, vector in execution
        if any(argument.startswith(f"{ROOT}/") for argument in vector)
    ]

    # The single comparison finally disagrees, in cleanup.
    assert outcome.cleanup.state == "S-B"
    assert ROOT in outcome.cleanup.residue


def test_a_root_replaced_before_a_later_flag_change_reaches_no_pathname() -> None:
    """**[inverted — the second injection R2-1 asks for.]**

    The same substitution, injected much later: immediately before `B5-C6-08`,
    which used to be a `chattr +i` on a file under the root. It is now a
    descriptor-bound flag effect, issued on the inode a held descriptor refers
    to after a pre-check against the identity the creating step recorded — so
    the step never reaches the substituted pathname at all, and it is not in the
    boundary's call log because it starts no process.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    host.injections["B4-19"] = lambda current: current.substitute_root()

    outcome = runner(plan, host).execute()

    reset = next(step for step in plan.steps if step.step_id == "B5-C6-08")
    assert reset.is_effect and reset.argv == ()
    assert "B5-C6-08" not in host.calls

    # The capture is one effect and it, too, starts no process.
    capture = next(
        step for step in plan.steps if step.is_effect and step.effect.components
    )
    assert capture.step_id not in host.calls
    assert not [
        vector
        for vector in host.vectors
        if vector[:1] in (("/usr/bin/install",), ("/usr/bin/chattr",))
    ]

    assert outcome.cleanup.state == "S-B"


def test_a_replaced_root_has_its_descendants_removed_before_the_check() -> None:
    """**[residual — unchanged by the mechanism.]** Count what still precedes it.

    R16 counted *"30 cleanup commands referencing the root before that check"*.
    Eight of those are gone: the six `chattr -ia` vectors and the two restoring
    `install` vectors are descriptor-bound effects now and resolve no pathname.
    **The removals are not**, because r6 §1.4.5 says plainly that
    `unlinkat`'s final component is not bindable by any syscall available here —
    so `rm --force` and `rmdir` still resolve names, still precede the only
    comparison, and EH-R16-1 stays Open for exactly them.

    The floor is lowered to the count that remains, and the two facts that
    changed are asserted beside it so the reduction is visible rather than
    silent.
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
    assert len(touching_root) >= 20

    removals = [
        vector
        for vector in before
        if vector[0] in ("/usr/bin/rm", "/usr/bin/rmdir")
    ]
    assert removals, "descendant removals are issued before the only check"

    # What is no longer among them: the flag clears and the restores. Neither
    # resolves a pathname any more, and neither is an executable this plan may
    # name.
    assert not [
        vector
        for vector in before
        if vector[:1] in (("/usr/bin/chattr",), ("/usr/bin/install",))
    ]
    assert [
        step
        for step in plan.cleanup_plan.steps
        if step.is_effect and step.effect.kind is EffectKind.CLEAR_FLAG
    ]


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
    # The restoration still ran — it does not depend on the root's identity any
    # more, because it reads the independent store rather than `R/before`.
    assert [record for record in host.consumed if record.action == "restore-source"]


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
    restored = {
        record.path
        for record in host.consumed
        if record.action == "restore-source"
    }
    assert restored == {
        "/etc/postgresql/16/main/pg_hba.conf",
        "/etc/postgresql/16/main/pg_ident.conf",
    }


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
    `0770` directory the file is in. The root's identity never changes.

    **Both halves of the finding are asserted, and they now differ.** The
    substitution is *detected*: cleanup's flag clear is a descriptor-bound
    effect whose pre-check compares the identity with the one the creating step
    recorded, and it refuses — which is why the run is S-B rather than the S-C
    it used to report. It is **not prevented**: `unlinkat`'s final component is
    not bindable, so the `rm --force` that follows still consumes the
    replacement, and that is the residual r6 §1.4.5 states rather than denies.
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

    # **Detected.** The flag clear for this very object refused at its
    # pre-check, so the run is S-B rather than the clean cleanup it used to
    # report — and the refusal happened before the ioctl, not after it.
    assert outcome.cleanup.state == "S-B"
    refused = [
        recorded
        for recorded in outcome.cleanup_steps
        if not recorded.satisfied and recorded.launch_failure == LAUNCH_EFFECT_REFUSED
    ]
    assert refused
    cleared = {
        step.step_id: step
        for step in plan.cleanup_plan.steps
        if step.is_effect and step.effect.path == subject
    }
    assert cleared
    assert {recorded.step_id for recorded in refused} & set(cleared)

    # **Not prevented.** The other six subjects are removed in the same
    # pathname-resolved way, because the removal's final component is not
    # bindable by any syscall available here.
    removed = {
        vector[-1]
        for vector in _cleanup_vectors(host, plan)
        if vector[0] == "/usr/bin/rm"
    }
    assert set(GROUP_WRITABLE_SUBJECTS) <= removed


def test_a_substituted_evidence_copy_is_no_longer_what_the_restore_reads() -> None:
    """**[inverted — PR-20260909-R2-2's own scenario, after the mechanism.]**

    The copy in `…/before/pg_hba.conf` is replaced with different bytes in the
    interval before the restore. It used to be the restore's source: `install`
    read it at the moment it opened it, so the substituted bytes became the
    disposable instance's authentication configuration. It is **retained
    evidence** now and nothing else — r6 §2.5 — and the restore reads the
    independent store, whose parent is `0700 root:root` and outside the
    disposable root.

    Asserted on **bytes**, not on a command name and not on a state label.
    """
    capture = f"{ROOT}/before/pg_hba.conf"
    live = "/etc/postgresql/16/main/pg_hba.conf"
    substituted = b"# substituted authentication configuration\n"

    plan = runnable_plan()
    host = FakeHost(plan)
    original = host.content_of(live)
    restore = next(
        step.step_id
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.RESTORE
    )
    replaced: dict[str, bytes | None] = {}

    def replace(current: FakeHost) -> None:
        current.substitute(capture, content=substituted)
        replaced["content"] = current.content_of(capture)

    host.injections[restore] = replace

    outcome = runner(plan, host).execute()

    # The evidence copy really was replaced at that instant — cleanup removes it
    # later, which is why the observation is taken in the injection rather than
    # from the end state — and the restore consumed the **store's** bytes.
    assert replaced["content"] == substituted
    assert not [
        record for record in host.consumed if record.action == "install-source"
    ]
    consumed = [
        record
        for record in host.consumed
        if record.step_id == restore and record.action == "restore-source"
    ]
    assert consumed
    assert all(record.content != substituted for record in consumed)
    assert host.content_of(live) == original

    assert outcome.cleanup.state == "S-C"
    assert outcome.cleanup.configuration_risk == ()


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


def test_the_configuration_restores_no_longer_read_from_inside_the_root() -> None:
    """**[inverted]** Structural, on the plan.

    Neither `RESTORE` step names a revalidation and both still precede the only
    one the plan generates — that is unchanged. What changed is why it no longer
    matters: a restore's source is not inside the root at all, so it does not
    depend on the root's identity and a root guard was never the right place for
    it. The binding it does depend on is the record/copy/destination
    correspondence the independent store establishes.
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

    for step in restores:
        assert step.argv == ()
        assert step.is_effect
        assert step.effect.kind is EffectKind.RESTORE_CONFIGURATION
        assert not step.effect.path.startswith(f"{ROOT}/")


# ---------------------------------------------------------------------------
# 3. The inventory the revised design's residual rests on
# ---------------------------------------------------------------------------


def _created_directories(plan) -> dict:
    """`path` → `(mode, owner, group)` for every directory the plan creates.

    Read off the reviewed **effects** rather than off an `install` vector: r6
    §6.4 retired that executable, and the mode, owner and group are now fields a
    reviewer approves rather than words in a command line.
    """
    return {
        step.effect.path: (
            f"{step.effect.mode:04o}",
            step.effect.owner,
            step.effect.group,
        )
        for step in plan.steps
        if step.is_effect and step.effect.kind is EffectKind.CREATE_DIRECTORY
    }


def test_two_directories_are_group_writable_by_a_created_identity() -> None:
    """**[inventory]** §5.1 of the revised design, checked against the plan.

    The rejected design said replacement inside the root requires uid 0 or
    `CAP_DAC_OVERRIDE` and that such an actor is outside the threat model. Two
    directories the plan creates are `0770` with a group the run itself creates,
    so membership of `freedomsheet` is enough.
    """
    plan = build_concrete_plan()
    directories = _created_directories(plan)
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
