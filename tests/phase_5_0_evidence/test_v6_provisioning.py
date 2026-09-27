"""**C-P5.0-LAB-V6-R1** — the completed r6 §7 provisioning contract, and the
applier that would apply its directory items.

Three things are under test and they are deliberately kept apart.

1. **The definitions.** That the delta is eleven items, that V12 explicitly
   owns persistent `/var/lib/freedom-blades` before V4/V5, and
   that every item states an exact owner, group, numeric mode, creation
   mechanism, persistence behaviour, rationale, verification and rollback. A
   field that is missing is a refusal at construction, not a gap discovered by
   whoever applies it.
2. **The location disposition.** `/var/lib/fb-evidence-p5-0` is the sole
   canonical `R`; V11 is withdrawn; and no production caller registers
   `EVIDENCE_ROLE` before a real consumer is separately reviewed.
3. **The applier.** Clean creation, an idempotent re-run that writes nothing,
   every wrong-object refusal, a partial application, the rollback boundaries,
   and the V7 stop — ending with all seven participants refusing on the absent
   lifecycle record, which is the fail-closed state this release is meant to
   leave the host in.

**Nothing here touches a provisioned path.** Every target is built under
`tmp_path`, the account database is a fake that resolves the declared owner to
this process's own ids, and no test needs privilege. A file created here says
nothing about whether V1, V2, V3, V4, V5, V9 or V12 has ever been applied on
`oracle-test` — none has — and nothing here observes that host, creates a link
or bears on **I3**.
"""
from __future__ import annotations

import ast
import contextlib
import errno
import os
import stat
from pathlib import Path

import pytest

from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan
from tools.phase_5_0_evidence.errors import HarnessError, PlanRefused
from tools.phase_5_0_evidence.execution.provisioner import (
    APPLIED_DIRECTORY_ITEMS,
    BARRIER_FAILED,
    CREATION_REFUSED,
    DESCRIPTOR_NOT_RELEASED,
    IDENTITY_UNKNOWN,
    ITEM_NOT_A_DIRECTORY,
    ITEM_NOT_RELEASED,
    MODE_NOT_APPLIED,
    OBJECT_UNEXPECTED_CONTENT,
    OBJECT_UNREADABLE,
    OBJECT_WRONG_GROUP,
    OBJECT_WRONG_LINK_COUNT,
    OBJECT_WRONG_MODE,
    OBJECT_WRONG_OWNER,
    OBJECT_WRONG_TYPE,
    OBSERVATION_DISCREPANCIES,
    OWNERSHIP_NOT_APPLIED,
    PARENT_ABSENT,
    PARENT_NOT_A_DIRECTORY,
    PARENT_UNSAFE_OWNERSHIP,
    POST_CREATION_OPEN_FAILED,
    POST_CREATION_REFUSALS,
    PROVISIONER_NOT_ARMED,
    PROVISIONER_REFUSALS,
    PROVISIONING_IDENTITY_REFUSED,
    ROLLBACK_IDENTITY_MISMATCH,
    ROLLBACK_IDENTITY_UNKNOWN,
    ROLLBACK_NOT_CREATED_HERE,
    ROLLBACK_NOT_EMPTY,
    ROLLBACK_NOT_REMOVED_NOT_RELEASED,
    ROLLBACK_REFUSALS,
    ROLLBACK_REMOVED_NOT_RELEASED,
    ROLLBACK_REMOVING_REFUSALS,
    UNEXPLAINED_OBJECT_REFUSALS,
    VERIFICATION_FAILED,
    VERIFICATION_UNREADABLE,
    AppliedItem,
    DirectoryProvisioner,
    DirectoryTarget,
    ItemObservation,
    Outcome,
    ProvisioningRefused,
    RemovalEffect,
    RollbackRefused,
    directory_targets,
    released_operator_steps,
)
from tools.phase_5_0_evidence.lifecycle_storage import Participant
from tools.phase_5_0_evidence.provisioning import (
    EVIDENCE_ROOT,
    EVIDENCE_ROOT_TRACE,
    PREREQUISITE_PARENTS,
    PROVISIONING_ITEMS,
    RELEASED_PREREQUISITE_SUBSET,
    STATE_ROOT,
    UNCONFIRMED_TARGET_FACTS,
    UNRECONCILED_CONTRACT_DISCREPANCIES,
    V7_EXCLUSION,
    VERIFICATION_PROCEDURE,
    LaboratoryLayout,
    ProvisioningItem,
    ProvisioningKind,
    delta_item_count,
    excluded_item_ids,
    items_by_id,
    released_items,
)

from tests.phase_5_0_evidence.lab_fixtures import AT, Laboratory

TOOLS = Path(__file__).resolve().parents[2] / "tools" / "phase_5_0_evidence"

#: Every `Participant`, so the V7 stop is asserted for all seven rather than for
#: the one that happens to be convenient.
ALL_SEVEN = tuple(Participant)


class FakeAccounts:
    """The account database, as the two reads the provisioner performs.

    It resolves the declared owner and group to **this process's own** ids, so
    the real `fchown` succeeds without privilege and the real mechanism runs
    unchanged. `uid_shift` and `gid_shift` move one answer away from the truth,
    which is how the wrong-owner and wrong-group refusals are reached without a
    second real account.
    """

    def __init__(self, *, uid_shift: int = 0, gid_shift: int = 0, unknown: str = ""):
        self.uid_shift = uid_shift
        self.gid_shift = gid_shift
        self.unknown = unknown

    def account(self, name: str) -> tuple[int, int]:
        if name == self.unknown:
            raise HarnessError(f"no account named {name!r} exists")
        return os.geteuid() + self.uid_shift, os.getegid()

    def group_id(self, name: str) -> int:
        if name == self.unknown:
            raise HarnessError(f"no group named {name!r} exists")
        return os.getegid() + self.gid_shift


def model_targets(root: Path) -> tuple[DirectoryTarget, ...]:
    """The four directory items, at model locations under `root`.

    It calls the production factory with a model layout and a model evidence
    root, so the owner, group, mode and order under test are the reviewed ones
    and only the locations differ.
    """
    return directory_targets(
        layout=LaboratoryLayout(
            laboratory_directory=str(root / "var" / "freedom-blades" / "laboratory"),
            runs_directory_name="runs",
            record_name="lifecycle.json",
            recovery_directory=str(root / "var" / "freedom-blades" / "recovery"),
            lock_path=str(root / "run" / "laboratory.lock"),
        ),
    )


@pytest.fixture()
def model(tmp_path: Path) -> Path:
    """A model host: the two parents exist, and nothing below them does.

    `0700` on each, because the applier requires the parent to belong to the
    provisioning identity alone — which on the target means root-owned and not
    group- or other-writable.
    """
    (tmp_path / "var").mkdir(mode=0o700)
    return tmp_path


def armed(**kwargs) -> DirectoryProvisioner:
    return DirectoryProvisioner(lookup=FakeAccounts(**kwargs), armed=True)


def facts(path: Path) -> os.stat_result:
    return os.stat(path, follow_symlinks=False)


# ---------------------------------------------------------------------------
# 1. The definitions
# ---------------------------------------------------------------------------


def test_the_delta_is_eleven_items_of_which_eight_are_defined() -> None:
    """r6 §7 grew from ten to eleven, and the count is derived rather than typed.

    V12 replaces withdrawn V11 without changing the total: it explicitly owns
    the persistent parent V4 and V5 require.
    """
    assert delta_item_count() == 11
    assert len(PROVISIONING_ITEMS) == 8
    assert len(UNCONFIRMED_TARGET_FACTS) == 3
    assert {item.item_id for item in PROVISIONING_ITEMS} == {
        "V1",
        "V2",
        "V3",
        "V4",
        "V5",
        "V7",
        "V9",
        "V12",
    }


def test_the_state_root_item_states_an_exact_contract() -> None:
    """V12, field by field: the persistent parent, not disposable `R`."""
    item = items_by_id()["V12"]

    assert item.kind is ProvisioningKind.DIRECTORY
    assert item.subject == STATE_ROOT == "/var/lib/freedom-blades"
    assert EVIDENCE_ROOT == APPROVED_TARGET.root_path == "/var/lib/fb-evidence-p5-0"
    assert item.owner == "root"
    assert item.group == "root"
    assert item.mode == 0o755
    assert item.approved is False
    # The mechanism, the reboot behaviour, the read-only check and the reversal.
    assert "mkdirat" in item.creation and "fchmod" in item.creation
    assert "parent-barrier" in item.creation
    assert "survives reboot" in item.persistence
    assert "systemd-tmpfiles" in item.persistence
    assert "0755" in item.verification
    assert "rmdir" in item.rollback and "st_dev, st_ino" in item.rollback
    assert "§2.2" in item.source and "§5.4" in item.source


def test_every_item_states_creation_persistence_verification_and_rollback() -> None:
    """The four fields the completed delta requires, for all eight.

    An item that stated only an owner and a mode is an item whose applier
    chooses the rest, and that is the defect V12 exists to close — so the rule
    is applied to every row rather than to the new one.
    """
    for item in PROVISIONING_ITEMS:
        assert item.creation.strip(), item.item_id
        assert item.persistence.strip(), item.item_id
        assert item.verification.strip(), item.item_id
        assert item.rollback.strip(), item.item_id


@pytest.mark.parametrize(
    "field", ["creation", "persistence", "verification", "rollback"]
)
def test_an_item_missing_one_of_the_four_fields_is_refused(field: str) -> None:
    complete = {
        "item_id": "VX",
        "kind": ProvisioningKind.DIRECTORY,
        "subject": "/var/lib/example",
        "owner": "root",
        "group": "root",
        "mode": 0o700,
        "rationale": "because",
        "source": "r6 §7",
        "creation": "mkdirat",
        "persistence": "survives reboot",
        "verification": "fstatat",
        "rollback": "rmdir",
    }
    complete[field] = "   "
    with pytest.raises(PlanRefused):
        ProvisioningItem(**complete)


def test_the_released_subset_excludes_v7_and_is_parent_before_child() -> None:
    """Peter's 2026-09-16 approval, as an order a reviewer can check.

    V7 is the one defined item outside it. The group resolves before anything
    group-owned is created, and V4 precedes its `runs` child.
    """
    assert excluded_item_ids() == ("V7",)
    assert RELEASED_PREREQUISITE_SUBSET == ("V1", "V2", "V3", "V12", "V4", "V9", "V5")
    order = list(RELEASED_PREREQUISITE_SUBSET)
    assert order.index("V1") < order.index("V4")
    assert order.index("V4") < order.index("V9")
    assert [item.item_id for item in released_items()] == order
    assert [item.item_id for item in released_operator_steps()] == ["V1", "V2", "V3"]
    assert APPLIED_DIRECTORY_ITEMS == ("V12", "V4", "V9", "V5")


def test_the_v7_exclusion_names_its_reason_and_its_stop_condition() -> None:
    joined = " ".join(V7_EXCLUSION)
    assert "I3" in joined
    assert "linkat" in joined
    assert "record absent or unreadable" in joined
    assert "all seven" in joined
    assert "is_executable" in joined and "False" in joined


def test_the_production_targets_are_the_reviewed_definitions() -> None:
    """The factory's defaults are the delta, not a second copy of it."""
    known = items_by_id()
    for target in directory_targets():
        item = known[target.item_id]
        assert target.path == item.subject, target.item_id
        assert (target.owner, target.group, target.mode) == (
            item.owner,
            item.group,
            item.mode,
        ), target.item_id


def test_v12_is_the_parent_of_v4_and_v5_and_names_their_real_children() -> None:
    """The reviewed relationship, asserted rather than assumed.

    V12's definition is *the persistent parent of V4's laboratory directory and
    V5's independent recovery directory*. Both children must therefore resolve
    under it, and the names it is verified to contain must be theirs.
    """
    targets = {target.item_id: target for target in directory_targets()}
    assert targets["V4"].parent_path == targets["V12"].path
    assert targets["V5"].parent_path == targets["V12"].path
    assert targets["V12"].expected_children == (
        targets["V4"].name,
        targets["V5"].name,
    )


def test_v12s_expected_children_follow_the_layout_rather_than_two_literals(
    tmp_path: Path,
) -> None:
    """C-P5.0-LAB-V6-D review regression — the children were hardcoded.

    `expected_children` is the gate `OBJECT_UNEXPECTED_CONTENT` refuses on, so
    two literals that do not track the layout make an idempotent re-application
    over a correctly provisioned tree refuse against objects that are exactly
    what the delta created. V4 already derived its `runs` child; V12 did not.
    """
    targets = {
        target.item_id: target
        for target in directory_targets(
            layout=LaboratoryLayout(
                laboratory_directory=str(tmp_path / "state" / "lab-alt"),
                runs_directory_name="runs",
                record_name="lifecycle.json",
                recovery_directory=str(tmp_path / "state" / "recovery-alt"),
                lock_path=str(tmp_path / "run" / "laboratory.lock"),
            )
        )
    }
    assert targets["V12"].path == str(tmp_path / "state")
    assert targets["V12"].expected_children == ("lab-alt", "recovery-alt")


def test_children_under_two_different_parents_refuse_rather_than_picking_one(
    tmp_path: Path,
) -> None:
    """C-P5.0-LAB-V6-D review regression — V12 was derived from V4 alone.

    Reading only `laboratory_directory` builds a V12 that is not V5's parent,
    reports it created, and leaves V5 refusing `parent-absent` against a parent
    nobody defined. That is the implicit parent V12 exists to prevent, so the
    incoherent layout is refused before anything is created.
    """
    with pytest.raises(ProvisioningRefused) as raised:
        directory_targets(
            layout=LaboratoryLayout(
                laboratory_directory=str(tmp_path / "a" / "freedom-blades" / "laboratory"),
                runs_directory_name="runs",
                record_name="lifecycle.json",
                recovery_directory=str(tmp_path / "b" / "elsewhere" / "recovery"),
                lock_path=str(tmp_path / "run" / "laboratory.lock"),
            )
        )
    assert raised.value.classification == CREATION_REFUSED
    assert raised.value.item_id == "V12"
    assert raised.value.classification in PROVISIONER_REFUSALS


def test_one_name_for_both_children_refuses(tmp_path: Path) -> None:
    """V4 and V5 are two objects and cannot be one entry under V12."""
    shared = str(tmp_path / "state" / "same")
    with pytest.raises(ProvisioningRefused) as raised:
        directory_targets(
            layout=LaboratoryLayout(
                laboratory_directory=shared,
                runs_directory_name="runs",
                record_name="lifecycle.json",
                recovery_directory=shared,
                lock_path=str(tmp_path / "run" / "laboratory.lock"),
            )
        )
    assert raised.value.classification == CREATION_REFUSED
    assert raised.value.item_id == "V12"


@pytest.mark.parametrize(
    "description,laboratory",
    [
        ("a relative path", "var/freedom-blades/laboratory"),
        ("a trailing-slash form", "/var/freedom-blades/laboratory/"),
        ("the root itself", "/"),
    ],
)
def test_a_layout_path_with_no_parent_and_name_reading_refuses(
    description: str, laboratory: str, tmp_path: Path
) -> None:
    """V12's location is derived, so what it is derived from is validated."""
    with pytest.raises(ProvisioningRefused) as raised:
        directory_targets(
            layout=LaboratoryLayout(
                laboratory_directory=laboratory,
                runs_directory_name="runs",
                record_name="lifecycle.json",
                recovery_directory=str(tmp_path / "state" / "recovery"),
                lock_path=str(tmp_path / "run" / "laboratory.lock"),
            )
        )
    assert raised.value.classification == CREATION_REFUSED, description
    assert raised.value.item_id == "V12", description


# ---------------------------------------------------------------------------
# 2. The trace behind V12's mode
# ---------------------------------------------------------------------------


def test_every_reviewed_effect_step_runs_as_root() -> None:
    """The premise the mode rests on, asserted over the real concrete plan.

    Each descriptor-bound effect — C1 among them — is `run_as="root"`, and
    `boundary.ProcessBoundary` refuses such a step from a launcher that is not
    already effective UID and GID 0
    (`test_boundary_identity.py::test_a_non_root_launcher_cannot_run_a_root_step_as_itself`).
    So the process that holds D1 and issues C1 is root, and `0700 root:root` is
    exactly sufficient rather than a number somebody picked.
    """
    plan = build_concrete_plan(APPROVED_TARGET)
    effects = [
        step for step in (*plan.steps, *plan.cleanup_plan.steps) if step.is_effect
    ]
    assert effects
    assert {step.run_as for step in effects} == {"root"}


def test_no_production_caller_registers_the_evidence_role() -> None:
    """**The second unreconciled discrepancy, asserted rather than asserted of.**

    `plan.EVIDENCE_ROLE` exists and is re-exported, and **nothing in the package
    opens a directory under it**: the only `open_provisioned_root("evidence", …)`
    calls in the repository are in this suite, over a temporary directory. D1 is
    specified, named and unbuilt, which is consistent with r6 §1.4.1 being [P]
    and is stated so that a provisioned directory is not read as evidence that
    something opens it.
    """
    offenders: list[str] = []
    for path in sorted(TOOLS.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = node.func
            if not isinstance(function, ast.Attribute):
                continue
            if function.attr != "open_provisioned_root":
                continue
            first = node.args[0] if node.args else None
            if isinstance(first, ast.Constant) and first.value == "evidence":
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == []


def test_the_canonical_evidence_root_is_the_approved_target() -> None:
    """The withdrawn `/opt` location cannot remain a competing `R`."""
    naming = [
        path.name
        for path in sorted(TOOLS.rglob("*.py"))
        if EVIDENCE_ROOT in path.read_text(encoding="utf-8")
    ]
    assert "approved_target.py" in naming
    assert "provisioning.py" in naming


def test_the_trace_records_the_approved_location_disposition() -> None:
    joined = " ".join(EVIDENCE_ROOT_TRACE)
    assert EVIDENCE_ROOT in joined
    assert "/opt/freedom-blades/evidence" in joined and "withdrawn" in joined
    assert "EVIDENCE_ROLE" in joined and "separately reviewed" in joined


def test_no_prerequisite_parent_is_left_undefined() -> None:
    assert PREREQUISITE_PARENTS == ()


def test_the_maintainer_resolved_the_location_discrepancies() -> None:
    assert UNRECONCILED_CONTRACT_DISCREPANCIES == ()


# ---------------------------------------------------------------------------
# 3. The applier — clean creation and idempotence
# ---------------------------------------------------------------------------


def test_a_clean_application_creates_all_four_exactly(model: Path) -> None:
    """Every object, bit for bit, including V9's setgid and sticky bits."""
    targets = model_targets(model)
    run = armed().apply(targets)

    assert run.complete
    assert [item.item_id for item in run.applied] == ["V12", "V4", "V9", "V5"]
    assert all(item.outcome is Outcome.CREATED for item in run.applied)

    known = items_by_id()
    for target in targets:
        observed = facts(Path(target.path))
        assert stat.S_ISDIR(observed.st_mode), target.item_id
        assert observed.st_uid == os.geteuid(), target.item_id
        assert observed.st_gid == os.getegid(), target.item_id
        assert observed.st_mode & 0o7777 == known[target.item_id].mode, target.item_id
    runs = Path(model_targets(model)[2].path)
    assert runs.stat().st_mode & stat.S_ISGID
    assert runs.stat().st_mode & stat.S_ISVTX
    assert {entry.name for entry in Path(targets[0].path).iterdir()} == {
        "laboratory", "recovery"
    }


def test_an_unarmed_provisioner_creates_nothing(model: Path) -> None:
    """Arming is one explicit act, so a mistaken assembly still writes nothing."""
    targets = model_targets(model)
    run = DirectoryProvisioner(lookup=FakeAccounts()).apply(targets)

    assert run.refusal is not None
    assert run.refusal.classification == PROVISIONER_NOT_ARMED
    assert run.applied == ()
    assert run.not_attempted == ("V4", "V9", "V5")
    for target in targets:
        assert not Path(target.path).exists()
    with pytest.raises(ProvisioningRefused):
        run.raise_if_refused()


def test_a_re_run_is_idempotent_and_writes_nothing(model: Path) -> None:
    """The second application verifies; it does not `mkdir` and swallow `EEXIST`.

    `install --directory` succeeds whether or not the directory was there, which
    is what r6 §1.4.2 replaced with an exclusive `mkdirat`. An idempotence built
    on a swallowed `EEXIST` would report success for an object nobody checked,
    so this asserts that the inode and its change time are untouched.
    """
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    before = {target.path: facts(Path(target.path)) for target in targets}

    second = armed()
    run = second.apply(targets)

    assert run.complete
    assert all(item.outcome is Outcome.ALREADY_PROVISIONED for item in run.applied)
    # Nothing was created, so nothing is removable by this application.
    assert second.created == ()
    for target in targets:
        after = facts(Path(target.path))
        assert (after.st_dev, after.st_ino) == (
            before[target.path].st_dev,
            before[target.path].st_ino,
        ), target.item_id
        assert after.st_ctime_ns == before[target.path].st_ctime_ns, target.item_id


# ---------------------------------------------------------------------------
# 4. Every wrong-object refusal
# ---------------------------------------------------------------------------


def test_an_object_of_the_wrong_type_refuses_and_is_left_alone(model: Path) -> None:
    for name, build in (
        ("regular file", lambda path: path.write_bytes(b"not a directory")),
        ("symbolic link", lambda path: path.symlink_to(model)),
    ):
        root = model / name.replace(" ", "-")
        root.mkdir(mode=0o700)
        target = DirectoryTarget(
            item_id="V12",
            path=str(root / "evidence"),
            owner="root",
            group="root",
            mode=0o700,
        )
        build(Path(target.path))
        before = facts(Path(target.path))

        with pytest.raises(ProvisioningRefused) as refusal:
            armed().ensure(target)

        assert refusal.value.classification == OBJECT_WRONG_TYPE, name
        after = facts(Path(target.path))
        assert (after.st_dev, after.st_ino) == (before.st_dev, before.st_ino), name


def test_an_object_with_the_wrong_owner_refuses(model: Path) -> None:
    """The item declares `root`; the object belongs to somebody else.

    Reached by moving the **declared owner** away from the object's real one,
    which is the same disagreement seen from the other side and needs no second
    real account. The parent check asks about the running identity instead, so
    it does not mask this.
    """
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()

    shifted = DirectoryProvisioner(lookup=FakeAccounts(uid_shift=1), armed=True)
    with pytest.raises(ProvisioningRefused) as refusal:
        shifted.ensure(targets[0])

    assert refusal.value.classification == OBJECT_WRONG_OWNER
    observation = shifted.verify(targets)[0]
    assert OBJECT_WRONG_OWNER in observation.discrepancies
    assert observation.matches is False


def test_an_object_with_the_wrong_group_refuses(model: Path) -> None:
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()

    shifted = DirectoryProvisioner(lookup=FakeAccounts(gid_shift=1), armed=True)
    with pytest.raises(ProvisioningRefused) as refusal:
        shifted.ensure(targets[1])

    assert refusal.value.classification == OBJECT_WRONG_GROUP


def test_an_object_with_the_wrong_mode_refuses_and_is_not_repaired(
    model: Path,
) -> None:
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    evidence = Path(targets[0].path)
    evidence.chmod(0o700)

    with pytest.raises(ProvisioningRefused) as refusal:
        armed().ensure(targets[0])

    assert refusal.value.classification == OBJECT_WRONG_MODE
    # Left exactly as it was. Repairing an unexplained object is a write into a
    # state nobody has established.
    assert evidence.stat().st_mode & 0o7777 == 0o700


def test_unexpected_content_refuses(model: Path) -> None:
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    (Path(targets[0].path) / "left-behind").write_bytes(b"")

    with pytest.raises(ProvisioningRefused) as refusal:
        armed().ensure(targets[0])

    assert refusal.value.classification == OBJECT_UNEXPECTED_CONTENT
    assert (Path(targets[0].path) / "left-behind").exists()


def test_an_unexpected_subdirectory_refuses_on_content_and_on_link_count(
    model: Path,
) -> None:
    """Both conjuncts, and the honest statement of how they are exercised.

    A directory's link count is `.`, its parent's entry and one per
    subdirectory, so the only way to make it disagree with the listing on a real
    filesystem is to add a subdirectory — which is also unexpected content. The
    two are therefore exercised together here, and the conjunct that isolates a
    link count is V7's `st_nlink == 1`, which its `verification` states and
    which this release does not apply because V7 is excluded.
    """
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    (Path(targets[3].path) / "surprise").mkdir()

    observation = armed().verify(targets)[3]

    assert OBJECT_UNEXPECTED_CONTENT in observation.discrepancies
    assert OBJECT_WRONG_LINK_COUNT in observation.discrepancies
    assert observation.observed_link_count == 3
    assert items_by_id()["V7"].verification.count("st_nlink == 1") == 1


def test_a_file_left_inside_refuses_on_content_alone(model: Path) -> None:
    """The control for the row above: a regular file changes no link count."""
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    (Path(targets[3].path) / "surprise").write_bytes(b"")

    observation = armed().verify(targets)[3]

    assert observation.discrepancies == (OBJECT_UNEXPECTED_CONTENT,)
    assert observation.observed_link_count == 2


def test_the_six_unexplained_object_refusals_are_all_implemented() -> None:
    """Named as a set, so a conjunct deleted later fails here."""
    assert set(UNEXPLAINED_OBJECT_REFUSALS) <= PROVISIONER_REFUSALS
    source = (TOOLS / "execution" / "provisioner.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    method = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_discrepancies"
    )
    named = {
        node.id
        for node in ast.walk(method)
        if isinstance(node, ast.Name)
    }
    assert {
        "OBJECT_WRONG_TYPE",
        "OBJECT_WRONG_OWNER",
        "OBJECT_WRONG_GROUP",
        "OBJECT_WRONG_MODE",
        "OBJECT_WRONG_LINK_COUNT",
        "OBJECT_UNEXPECTED_CONTENT",
    } <= named


# ---------------------------------------------------------------------------
# 5. The parent, the identity and the unknown account
# ---------------------------------------------------------------------------


def test_an_absent_parent_refuses_rather_than_being_created(tmp_path: Path) -> None:
    """V12 still requires its reviewed `/var/lib` parent to exist."""
    targets = model_targets(tmp_path)
    run = armed().apply(targets)

    assert run.refusal is not None
    assert run.refusal.item_id == "V12"
    assert run.refusal.classification == PARENT_ABSENT
    assert not (tmp_path / "var").exists()


def test_a_parent_the_provisioning_identity_does_not_own_exclusively_refuses(
    model: Path,
) -> None:
    """A writable `/var/lib` model parent refuses before V12 creation.

    A directory `0700 root:root` under a parent another identity may write is
    not a root-only object: the parent's write bit governs renaming and
    unlinking the **entry**.
    """
    (model / "var").chmod(0o777)
    targets = model_targets(model)

    run = armed().apply(targets)

    assert run.refusal is not None
    assert run.refusal.item_id == "V12"
    assert run.refusal.classification == PARENT_UNSAFE_OWNERSHIP
    assert run.applied == ()
    assert not Path(targets[0].path).exists()


def test_a_parent_that_is_not_a_directory_refuses(model: Path) -> None:
    root = model / "file-parent"
    root.write_bytes(b"")
    target = DirectoryTarget(
        item_id="V12",
        path=str(root / "evidence"),
        owner="root",
        group="root",
        mode=0o700,
    )
    with pytest.raises(ProvisioningRefused) as refusal:
        armed().ensure(target)
    assert refusal.value.classification in (PARENT_ABSENT, PARENT_NOT_A_DIRECTORY)


def test_a_run_that_is_not_the_declared_owner_refuses_before_it_creates(
    model: Path,
) -> None:
    """A provisioning run started as the wrong identity stops at the gate.

    It would otherwise create four directories it cannot chown and leave a
    half-provisioned host — the failure mode the identity gate exists for.
    """
    shifted = DirectoryProvisioner(lookup=FakeAccounts(uid_shift=1), armed=True)
    targets = model_targets(model)

    run = shifted.apply(targets)

    assert run.refusal is not None
    assert run.refusal.classification == PROVISIONING_IDENTITY_REFUSED
    assert not Path(targets[0].path).exists()


def test_an_unresolvable_owner_refuses(model: Path) -> None:
    provisioner = DirectoryProvisioner(
        lookup=FakeAccounts(unknown="freedomlab"), armed=True
    )
    targets = model_targets(model)

    run = provisioner.apply(targets)

    assert run.refusal is not None
    assert run.refusal.item_id == "V4"
    assert run.refusal.classification == IDENTITY_UNKNOWN


# ---------------------------------------------------------------------------
# 6. Partial application and rollback
# ---------------------------------------------------------------------------


def test_a_partial_application_reports_what_exists_and_what_was_never_tried(
    model: Path,
) -> None:
    """The state an operator has to read after a refusal, as data."""
    targets = model_targets(model)
    provisioner = armed()
    # V9 lives under V4; removing V4's parent between items is not possible, so
    # the refusal is arranged where a real one would occur — an unexplained
    # object already at V9's name.
    provisioner.ensure(targets[0])
    laboratory = model / "var" / "freedom-blades" / "laboratory"
    laboratory.mkdir(mode=0o750)
    (laboratory / "runs").write_bytes(b"")

    run = provisioner.apply(targets)

    assert run.refusal is not None
    assert run.refusal.item_id == "V9"
    assert run.refusal.classification == OBJECT_WRONG_TYPE
    assert [item.item_id for item in run.applied] == ["V12", "V4"]
    assert run.not_attempted == ("V5",)
    assert not run.complete
    # This apply call verified V12 and V4; V12 was created by the same live
    # provisioner immediately before it and remains in that live account.
    assert run.created == ()
    assert [item.item_id for item in provisioner.created] == ["V12"]
    assert Path(targets[0].path).is_dir()
    assert not Path(targets[3].path).exists()


def test_a_rollback_removes_exactly_what_this_application_created(
    model: Path,
) -> None:
    """In reverse order, so a child goes before its parent, and no further."""
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets).raise_if_refused()

    removed = provisioner.rollback(targets)

    assert [item.item_id for item in removed] == ["V5", "V9", "V4", "V12"]
    for target in targets:
        assert not Path(target.path).exists(), target.item_id
    # The parents are untouched: they were never this application's.
    assert (model / "var").is_dir()
    assert (model / "var").is_dir()
    assert provisioner.created == ()


def test_a_rollback_refuses_a_directory_that_is_not_empty(model: Path) -> None:
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets).raise_if_refused()
    (Path(targets[3].path) / "capture-basis").write_bytes(b"pre-change bytes")

    with pytest.raises(ProvisioningRefused) as refusal:
        provisioner.rollback(targets)

    assert refusal.value.classification == ROLLBACK_NOT_EMPTY
    assert Path(targets[3].path).is_dir()
    assert (Path(targets[3].path) / "capture-basis").read_bytes() == b"pre-change bytes"


def test_a_rollback_refuses_an_object_that_is_no_longer_the_one_created(
    model: Path,
) -> None:
    """The recorded `(st_dev, st_ino)`, re-observed immediately before the
    removal — the same guard `remove_publication_temporary` takes, with the same
    honest limit stated in the method's own docstring."""
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets).raise_if_refused()
    replaced = Path(targets[3].path)
    substitute = replaced.parent / "substitute"
    substitute.mkdir(mode=0o700)
    replaced.rmdir()
    # Renamed rather than re-created, so the object at the name is certainly a
    # different inode: a fresh `mkdir` at a just-freed name may be handed the
    # inode that was released, and a test that depended on that would be
    # asserting an allocator's behaviour.
    substitute.rename(replaced)

    with pytest.raises(ProvisioningRefused) as refusal:
        provisioner.rollback(targets)

    assert refusal.value.classification == ROLLBACK_IDENTITY_MISMATCH
    assert replaced.is_dir()


def test_a_rollback_never_removes_an_object_it_only_verified(model: Path) -> None:
    """An already-provisioned object belongs to whoever provisioned it."""
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()

    second = armed()
    second.apply(targets).raise_if_refused()
    assert second.rollback(targets) == ()

    for target in targets:
        assert Path(target.path).is_dir(), target.item_id


def test_a_rollback_asked_for_an_item_it_did_not_create_refuses(
    model: Path,
) -> None:
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets).raise_if_refused()

    with pytest.raises(ProvisioningRefused) as refusal:
        provisioner.rollback(targets[:1])

    assert refusal.value.classification == ROLLBACK_NOT_CREATED_HERE


# ---------------------------------------------------------------------------
# 7. The V7 stop, and the fail-closed host it leaves
# ---------------------------------------------------------------------------


def test_v7_is_refused_by_name_and_so_is_every_operator_step() -> None:
    """The applier creates directories. It does not initialize a record.

    V7's `linkat` is the first real exclusive publication on the target and
    **I3** is unconfirmed, so it is excluded from this release rather than
    attempted and reported.
    """
    record = DirectoryTarget(
        item_id="V7",
        path="/var/lib/freedom-blades/laboratory/lifecycle.json",
        owner="root",
        group="freedomlab",
        mode=0o640,
    )
    with pytest.raises(ProvisioningRefused) as refusal:
        armed().ensure(record)
    assert refusal.value.classification == ITEM_NOT_RELEASED

    for item_id in ("V1", "V2", "V3"):
        step = DirectoryTarget(
            item_id=item_id,
            path="/var/lib/freedom-blades/example",
            owner="root",
            group="root",
            mode=0o700,
        )
        with pytest.raises(ProvisioningRefused) as operator:
            armed().ensure(step)
        assert operator.value.classification == ITEM_NOT_A_DIRECTORY, item_id


def test_a_provisioned_host_without_v7_refuses_all_seven_participants(
    model: Path,
) -> None:
    """**The stop condition, end to end, over the real admission path.**

    The four directory items are applied by the real applier, the lock inode is
    put where V3's fragment would re-create it, and `lifecycle.json` is absent
    because V7 is excluded. Every one of the seven participants then refuses at
    admission, naming the record it could not read — r6 §5.9's *record absent or
    unreadable*, which §5.10 says initialization is the only way out of and
    which is the operator's act, out of band, on a named attestation.

    So the absence is not a gap the next run fills. It is the fail-closed state,
    and it holds until V7 receives its own release.
    """
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    lock = model / "run" / "laboratory.lock"
    lock.parent.mkdir()
    lock.write_bytes(b"")

    layout = LaboratoryLayout(
        laboratory_directory=str(model / "var" / "freedom-blades" / "laboratory"),
        runs_directory_name="runs",
        record_name="lifecycle.json",
        recovery_directory=str(model / "var" / "freedom-blades" / "recovery"),
        lock_path=str(lock),
    )
    laboratory = Laboratory(layout=layout, root=model)

    assert not (Path(layout.laboratory_directory) / layout.record_name).exists()
    for participant in ALL_SEVEN:
        with laboratory.session(
            participant,
            reservation_id="RES-V6" if participant.writes_the_record else "",
            read_at=AT,
        ) as session:
            admission = session.admit()
        assert not admission.may_proceed, participant
        assert any(
            "could not be read" in reason for reason in admission.refusals
        ), participant
    # And the refusal created nothing: no record, no temporary, no run entry.
    assert sorted(
        entry.name for entry in Path(layout.laboratory_directory).iterdir()
    ) == ["runs"]
    assert list((Path(layout.laboratory_directory) / "runs").iterdir()) == []


# ---------------------------------------------------------------------------
# 8. The read-only verification — the V6 re-observation
# ---------------------------------------------------------------------------


def test_the_verification_procedure_covers_everything_v6_re_observes() -> None:
    """Identity, capabilities, the hard-link policy, the mount, the exact
    type/owner/group/mode, the parent, the group membership and V7's absence —
    and it claims to close none of the unconfirmed facts."""
    subjects = [row[0] for row in VERIFICATION_PROCEDURE]
    assert subjects == [
        "the execution identity",
        "the capability state",
        "the hard-link policy",
        "the mount and filesystem identity",
        "each item's exact type, owner, group and mode",
        "each item's parent",
        "the group and its membership",
        "V7's absence",
    ]
    limits = " ".join(row[3] for row in VERIFICATION_PROCEDURE)
    assert "I3 stays unconfirmed" in limits
    assert "V10" in limits
    assert "V8/I2" in limits
    assert "I8" in limits
    assert "creates no link" in " ".join(row[2] + row[3] for row in VERIFICATION_PROCEDURE)


def test_the_verification_reports_a_clean_host_and_its_parent(model: Path) -> None:
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()

    observations = armed().verify(targets)

    assert [observation.item_id for observation in observations] == [
        "V12",
        "V4",
        "V9",
        "V5",
    ]
    for observation in observations:
        assert observation.matches, observation.item_id
        assert observation.parent_is_exclusive, observation.item_id
        assert observation.observed_mode == items_by_id()[observation.item_id].mode


def test_the_verification_reports_an_unprovisioned_host_as_absent(
    model: Path,
) -> None:
    """Absent is not a discrepancy — **and an absent parent is a different fact.**

    V12, V4 and V5 are simply not there, which is what an unprovisioned host
    looks like. V9 lives under V4, so its report says the parent is absent
    rather than that the object is: an operator reading *"absent"* for a child
    whose parent does not exist would be reading one problem as four.
    """
    observations = {
        observation.item_id: observation
        for observation in armed().verify(model_targets(model))
    }

    assert all(not observation.present for observation in observations.values())
    assert all(not observation.matches for observation in observations.values())
    assert observations["V12"].discrepancies == ()
    for item_id in ("V4", "V9", "V5"):
        assert observations[item_id].discrepancies == (PARENT_ABSENT,), item_id


def test_the_verification_reports_a_writable_parent_without_refusing(
    model: Path,
) -> None:
    """A writable parent is observed rather than raised by verification.

    A verification returns findings; it is the **application** that refuses. An
    operator running the post-provision survey needs the whole picture, not the
    first disagreement.
    """
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    (model / "var").chmod(0o777)

    observations = armed().verify(targets)

    assert observations[0].present
    assert observations[0].discrepancies == ()
    assert observations[0].parent_is_exclusive is False
    assert observations[1].parent_is_exclusive is True


def test_the_verification_writes_nothing_and_creates_no_link() -> None:
    """**Structural**, over the module's own syntax tree.

    The read-only half is read-only because the calls are not there, not because
    a docstring says so — and the mutating half uses exactly the seven `os`
    calls the contract names and no eighth.
    """
    source = (TOOLS / "execution" / "provisioner.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    read_only = {"verify", "_verify_one", "_discrepancies", "_open_parent"}
    mutating = {"mkdir", "rmdir", "fchown", "fchmod", "fsync", "write", "unlink"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in read_only:
            continue
        for call in ast.walk(node):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute):
                assert call.func.attr not in mutating, f"{node.name}: {call.func.attr}"

    used = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "os"
    }
    assert used == {
        "close",
        "fchmod",
        "fchown",
        "fstat",
        "fsync",
        "geteuid",
        "listdir",
        "mkdir",
        "open",
        "rmdir",
        "stat",
    }
    # No link is created anywhere in the module, so nothing here bears on I3.
    for forbidden in ("link", "symlink", "rename"):
        assert f"os.{forbidden}" not in source


# ---------------------------------------------------------------------------
# 9. After the `mkdirat` — C-P5.0-LAB-V6-R2
#
# Codex Blocking finding PR-20260916-LAB-V6R1-1. The 45 tests above never
# inject a failure *inside* creation, so they all passed while two things were
# wrong: an ordinary `OSError` from the post-`mkdirat` open, `fchown`, `fchmod`
# or read-back path escaped raw with the directory already on disk and nothing
# recorded, and the handled barrier failure recorded the object only in the
# live provisioner's private list while the returned run said `applied == ()`.
#
# Every test below drives the real mechanism over real temporary-directory
# objects and injects a real failure at one real syscall.
# ---------------------------------------------------------------------------


#: The path-shaped text the injected errors carry, so that a refusal which
#: passed an operating-system message through would be visible rather than
#: merely suspected.
INJECTED_MESSAGE = "injected failure at /run/freedom-blades/secret"


@contextlib.contextmanager
def failing(name: str, *, when=None, after: int = 0):
    """Replace one `os` call with one that fails, for the length of a block.

    `when` narrows the injection to the calls that matter — the post-creation
    `open` is the only one this module issues with a `dir_fd` — and `after`
    lets it land on a later item, which is how the *earlier objects are still
    reported* case is reached. The replacement is undone in a `finally`, so no
    test leaves a broken `os` behind for the next one.
    """
    real = getattr(os, name)
    seen = 0

    def injected(*args, **kwargs):
        nonlocal seen
        if when is None or when(*args, **kwargs):
            seen += 1
            if seen > after:
                raise OSError(errno.EIO, INJECTED_MESSAGE)
        return real(*args, **kwargs)

    setattr(os, name, injected)
    try:
        yield
    finally:
        setattr(os, name, real)


def _with_dir_fd(*args, **kwargs) -> bool:
    return kwargs.get("dir_fd") is not None


#: One row per failure point after a successful `mkdirat`: the label, the `os`
#: call to break, how to narrow it, the closed classification it must become,
#: and whether the created object's `(st_dev, st_ino)` can still be read.
#:
#: **The identity column is derived, not chosen.** Every failure after the open
#: still holds the descriptor the creation opened, so the identity is there. The
#: open failure has no descriptor at all, and the read-back failure is an
#: `fstat` on that descriptor failing — which is the same call the identity
#: would come from, so it is unknown for the same reason it is unreadable.
POST_CREATION_FAILURES = (
    ("open", "open", {"when": _with_dir_fd}, POST_CREATION_OPEN_FAILED, False),
    ("fchown", "fchown", {}, OWNERSHIP_NOT_APPLIED, True),
    ("fchmod", "fchmod", {}, MODE_NOT_APPLIED, True),
    ("read-back fstat", "fstat", {"after": 2}, VERIFICATION_UNREADABLE, False),
    ("read-back listing", "listdir", {}, VERIFICATION_FAILED, True),
    ("parent barrier", "fsync", {}, BARRIER_FAILED, True),
)


@pytest.mark.parametrize(
    ("label", "call", "narrowing", "classification", "identity_known"),
    POST_CREATION_FAILURES,
    ids=[row[0] for row in POST_CREATION_FAILURES],
)
def test_a_failure_after_creation_is_closed_and_reports_the_residue(
    model: Path,
    label: str,
    call: str,
    narrowing: dict,
    classification: str,
    identity_known: bool,
) -> None:
    """The whole contract for one post-`mkdirat` failure, at every failure point.

    No raw `OSError`; a closed classification; the directory that now exists
    named in the returned result rather than only in the provisioner's private
    state; every later item untried; and an identity that is recorded when it
    could be read and declared unknown when it could not.
    """
    targets = model_targets(model)
    provisioner = armed()

    with failing(call, **narrowing):
        run = provisioner.apply(targets)

    # 1. It refused, in the closed vocabulary, on the item it was applying.
    assert run.refusal is not None, label
    assert run.refusal.item_id == "V12", label
    assert run.refusal.classification == classification, label
    assert classification in POST_CREATION_REFUSALS, label
    assert classification in PROVISIONER_REFUSALS, label

    # 2. The residue is exactly one empty directory, at V12's name.
    residue = Path(targets[0].path)
    assert residue.is_dir(), label
    assert list(residue.iterdir()) == [], label
    for later in targets[1:]:
        assert not Path(later.path).exists(), f"{label}: {later.item_id}"

    # 3. The object that exists is in the returned result, not only in the
    #    live provisioner. This is the half of the finding that returned
    #    `applied == ()` while a root-owned directory sat at the target.
    assert [item.item_id for item in run.applied] == ["V12"], label
    assert [item.item_id for item in run.created] == ["V12"], label
    assert not run.complete, label
    assert run.not_attempted == ("V4", "V9", "V5"), label

    # 4. Whether it can be reversed is stated, and stated the same way twice.
    created = run.created[0]
    assert created.removable is identity_known, label
    assert bool(created.object_id) is identity_known, label
    assert run.recoverable is identity_known, label
    assert (run.unidentified == ()) is identity_known, label
    assert created.outcome is (
        Outcome.CREATED if identity_known else Outcome.CREATED_IDENTITY_UNKNOWN
    ), label

    # 5. The identity, when known, is the object's own.
    if identity_known:
        observed = facts(residue)
        assert created.object_id == f"{observed.st_dev}:{observed.st_ino}", label

    # 6. The refusal is safe to hand an operator: no path, no `errno` text.
    detail = run.refusal.detail
    assert INJECTED_MESSAGE not in detail, label
    assert str(model) not in detail, label
    assert "EIO" not in detail and "Errno" not in detail, label

    # 7. The live provisioner agrees with the result it returned.
    assert provisioner.created == tuple(run.created), label


def test_the_two_reviewer_reproductions_are_closed(model: Path) -> None:
    """Codex's own two reproductions, asserted as they were reported.

    Before the fix, the injected `fsync` returned `applied = ()` and
    `created = ()` while the path existed, and the injected `fchmod` escaped as
    a raw `OSError` with nothing recorded anywhere.
    """
    for call, classification in (
        ("fsync", BARRIER_FAILED),
        ("fchmod", MODE_NOT_APPLIED),
    ):
        # A fresh model host per reproduction, so neither sees the other's
        # residue and each is the reviewer's case exactly.
        root = model / f"host-{call}"
        (root / "opt").mkdir(parents=True, mode=0o700)
        (root / "var").mkdir(parents=True, mode=0o700)
        targets = model_targets(root)
        provisioner = armed()

        with failing(call):
            run = provisioner.apply(targets)

        assert Path(targets[0].path).exists(), call
        assert run.applied != (), call
        assert run.created != (), call
        assert run.refusal is not None and run.refusal.classification == classification


def test_a_post_creation_failure_reports_the_objects_completed_before_it(
    model: Path,
) -> None:
    """The earlier items are in the result too, and the residue is unfinished.

    The injection lands on V9's `fchmod`, which is the one item whose reviewed
    mode differs from the `mkdirat` mode — so *the mode was not applied* is
    observable on disk rather than merely asserted: `3770` is what the item
    defines and the residue does not carry it.
    """
    targets = model_targets(model)
    provisioner = armed()

    # V12's and V4's `fchmod` succeed; V9's is the third and fails.
    with failing("fchmod", after=2):
        run = provisioner.apply(targets)

    assert run.refusal is not None
    assert run.refusal.item_id == "V9"
    assert run.refusal.classification == MODE_NOT_APPLIED
    assert [item.item_id for item in run.applied] == ["V12", "V4", "V9"]
    assert [item.item_id for item in run.created] == ["V12", "V4", "V9"]
    assert run.not_attempted == ("V5",)

    residue = Path(targets[2].path)
    assert residue.is_dir()
    assert residue.stat().st_mode & 0o7777 != items_by_id()["V9"].mode
    assert not residue.stat().st_mode & stat.S_ISGID
    assert not Path(targets[3].path).exists()

    # Every one of the three is this application's to reverse.
    assert run.recoverable
    assert [item.item_id for item in run.removable] == ["V12", "V4", "V9"]


def test_a_rollback_removes_a_residue_whose_identity_is_known(model: Path) -> None:
    """The guarded reversal works on a partly created object, like any other."""
    targets = model_targets(model)
    provisioner = armed()

    with failing("fchmod"):
        run = provisioner.apply(targets)

    assert run.recoverable
    removed = provisioner.rollback(targets)

    assert [item.item_id for item in removed] == ["V12"]
    assert not Path(targets[0].path).exists()
    assert (model / "var").is_dir()
    assert provisioner.created == ()


def test_a_rollback_refuses_a_residue_whose_identity_was_never_established(
    model: Path,
) -> None:
    """No descriptor was ever held on it, so nothing can show it is the same
    object. It is left where it is, and it is reported rather than hidden."""
    targets = model_targets(model)
    provisioner = armed()

    with failing("open", when=_with_dir_fd):
        run = provisioner.apply(targets)

    assert not run.recoverable
    assert [item.item_id for item in run.unidentified] == ["V12"]
    assert run.removable == ()

    with pytest.raises(ProvisioningRefused) as refusal:
        provisioner.rollback(targets)

    assert refusal.value.classification == ROLLBACK_IDENTITY_UNKNOWN
    assert Path(targets[0].path).is_dir()


def test_an_unidentified_residue_stops_the_whole_reversal(model: Path) -> None:
    """Not only its own removal. A reversal that took the objects it could and
    stopped would leave a third state nobody asked for, so it refuses before the
    first `rmdir` and V12 — which *is* identified — is still there afterwards."""
    targets = model_targets(model)
    provisioner = armed()

    # V12's post-creation open succeeds; V4's is the second and fails.
    with failing("open", when=_with_dir_fd, after=1):
        run = provisioner.apply(targets)

    assert [item.item_id for item in run.created] == ["V12", "V4"]
    assert [item.item_id for item in run.removable] == ["V12"]
    assert [item.item_id for item in run.unidentified] == ["V4"]

    with pytest.raises(ProvisioningRefused) as refusal:
        provisioner.rollback(targets)

    assert refusal.value.classification == ROLLBACK_IDENTITY_UNKNOWN
    assert Path(targets[0].path).is_dir()
    assert Path(targets[1].path).is_dir()
    assert provisioner.created != ()


def test_a_rollback_of_a_residue_refuses_an_object_that_has_been_replaced(
    model: Path,
) -> None:
    """The recorded identity is re-observed immediately before the removal, for
    a residue exactly as for a completed object."""
    targets = model_targets(model)
    provisioner = armed()

    with failing("fchmod"):
        provisioner.apply(targets)

    replaced = Path(targets[0].path)
    substitute = replaced.parent / "substitute"
    substitute.mkdir(mode=0o700)
    replaced.rmdir()
    substitute.rename(replaced)

    with pytest.raises(ProvisioningRefused) as refusal:
        provisioner.rollback(targets)

    assert refusal.value.classification == ROLLBACK_IDENTITY_MISMATCH
    assert replaced.is_dir()


def test_a_rollback_of_a_residue_refuses_a_directory_that_is_not_empty(
    model: Path,
) -> None:
    """Somebody put something inside the residue, and it is theirs to account
    for before anything is removed."""
    targets = model_targets(model)
    provisioner = armed()

    with failing("fchmod"):
        provisioner.apply(targets)

    (Path(targets[0].path) / "someone-elses-file").write_bytes(b"not this run's")

    with pytest.raises(ProvisioningRefused) as refusal:
        provisioner.rollback(targets)

    assert refusal.value.classification == ROLLBACK_NOT_EMPTY
    assert Path(targets[0].path).is_dir()
    assert (Path(targets[0].path) / "someone-elses-file").read_bytes() == b"not this run's"


def test_an_applied_item_cannot_pair_an_outcome_with_the_wrong_identity() -> None:
    """The invalid combinations are unconstructible rather than merely unused.

    A `CREATED` item without an identity is a removal guard that compares
    nothing; an already-provisioned or unidentified item *with* one is an
    invitation to remove an object this application cannot attribute to itself.
    """
    identified = AppliedItem(
        item_id="V12", path="/model/evidence", outcome=Outcome.CREATED, object_id="66:5"
    )
    assert identified.removable

    for outcome in (Outcome.ALREADY_PROVISIONED, Outcome.CREATED_IDENTITY_UNKNOWN):
        assert not AppliedItem(
            item_id="V12", path="/model/evidence", outcome=outcome
        ).removable
        with pytest.raises(HarnessError):
            AppliedItem(
                item_id="V12",
                path="/model/evidence",
                outcome=outcome,
                object_id="66:5",
            )

    for absent in ("", "66", "66:", "dev:ino", "66:5:7"):
        with pytest.raises(HarnessError):
            AppliedItem(
                item_id="V12",
                path="/model/evidence",
                outcome=Outcome.CREATED,
                object_id=absent,
            )


def test_every_post_creation_failure_point_has_its_own_closed_classification() -> None:
    """The six are distinct, all closed, and all reachable by the six injections.

    A failure point added to `_complete_creation` without a classification, or a
    classification that is never produced, is visible here rather than in a
    refusal an operator cannot interpret.
    """
    assert len(set(POST_CREATION_REFUSALS)) == len(POST_CREATION_REFUSALS) == 7
    assert set(POST_CREATION_REFUSALS) <= PROVISIONER_REFUSALS
    # **Six operations, and the release of the descriptor each was issued
    # through** — the seventh, added by C-P5.0-LAB-V6-R3. Both halves are
    # derived from the injection tables rather than typed, so a classification
    # no injection reaches, or an injection reaching no classification, fails
    # here rather than in a refusal an operator cannot interpret.
    assert {row[3] for row in POST_CREATION_FAILURES} == set(
        POST_CREATION_REFUSALS
    ) - {DESCRIPTOR_NOT_RELEASED}
    assert {row[2] for row in CLOSE_FAILURE_SITES} == {DESCRIPTOR_NOT_RELEASED}
    # The read-back's two halves are kept apart. A listing that could not be
    # read is a **discrepancy the object carries**, so it arrives inside
    # `VERIFICATION_FAILED` alongside any other disagreement; an `fstat` that
    # failed is a statement about the read-back itself and cannot be one of the
    # object's properties. Neither is an "unexplained object" condition: those
    # six describe an object that was read successfully and disagrees.
    assert OBJECT_UNREADABLE not in UNEXPLAINED_OBJECT_REFUSALS
    assert VERIFICATION_UNREADABLE not in UNEXPLAINED_OBJECT_REFUSALS
    assert OBJECT_UNREADABLE not in POST_CREATION_REFUSALS
    assert {OBJECT_UNREADABLE, VERIFICATION_UNREADABLE} <= PROVISIONER_REFUSALS


# ---------------------------------------------------------------------------
# 10. Releasing the descriptor — C-P5.0-LAB-V6-R3
#
# Codex Blocking finding PR-20260916-LAB-V6R2-1. The 60 tests above inject a
# failure into every *operation* after the `mkdirat` and none into the release
# of the descriptor that operation was issued through, so all 60 passed while
# a `close()` that reported failure escaped raw from three places: the created
# object's descriptor at the end of `_complete_creation`, and the parent's
# synchronizable and traversal descriptors in `ensure`. The reviewer's
# reproduction closed the first of them for real and then raised; the call left
# `OSError: [Errno 5] injected close failure at /secret` with V12 on disk, no
# `ProvisioningRun` returned and `provisioner.created == ()`.
#
# The same `finally` also *replaced* whatever refusal was unwinding through it,
# so an ownership, mode or read-back refusal about an object became an
# unclassified error about a descriptor.
#
# Every test below drives the real mechanism over real temporary-directory
# objects and breaks a real `os.close`.
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def failing_close(*, close_first: bool, nth: int = 1, cascade: bool = False):
    """Break `os.close`, in the two orders in which a real `close()` can fail.

    `close_first=True` releases the descriptor and **then** reports failure,
    which is the reviewer's reproduction and is the shape a deferred write-back
    error actually takes. `close_first=False` reports failure having released
    nothing, which is the shape this application must not assume away. The two
    are indistinguishable to the caller, and that is the point: the module may
    infer nothing about the descriptor from either.

    `nth` is the 1-based release to break; `cascade` also breaks every later
    one, which is how *a failure while unwinding does not skip the descriptor
    after it* is reached.

    **The descriptors the second form withheld are released here, on the way
    out**, so the suite does not leak one per test. The module under test must
    not do that, and `test_a_descriptor_whose_release_failed_is_never_closed_
    again` is what holds it to it: retrying `close()` on a number whose state is
    unknown can close a descriptor something else has since been handed.
    """
    real = os.close
    seen = 0
    withheld: list[int] = []

    def injected(fd: int) -> None:
        nonlocal seen
        seen += 1
        if seen == nth or (cascade and seen > nth):
            if close_first:
                real(fd)
            else:
                withheld.append(fd)
            raise OSError(errno.EIO, INJECTED_MESSAGE)
        real(fd)

    os.close = injected
    try:
        yield
    finally:
        os.close = real
        for fd in withheld:
            with contextlib.suppress(OSError):
                real(fd)


#: One row per descriptor released on the application path: the label, the
#: 1-based release to break, the classification it must become, and whether the
#: created object's identity is established by the time it happens.
#:
#: **The order is the code's, not a guess.** Applying V12 to a model host whose
#: parent exists and whose name is free releases exactly three descriptors, in
#: this order: the one `_complete_creation` opened on the created object, then
#: the synchronizable and traversal parent descriptors `ensure` releases.
#: `_existing` finds nothing at the name and opens none.
#:
#: The identity column is `True` for all three because the read-back that
#: establishes `(st_dev, st_ino)` is issued on the created descriptor **before**
#: it is released. Releasing it is the first thing that can fail once the object
#: is fully identified, which is why guarded rollback survives every row.
CLOSE_FAILURE_SITES = (
    ("the created object's descriptor", 1, DESCRIPTOR_NOT_RELEASED, True),
    ("the synchronizable parent descriptor", 2, DESCRIPTOR_NOT_RELEASED, True),
    ("the traversal parent descriptor", 3, DESCRIPTOR_NOT_RELEASED, True),
)

#: The two orders a failing `close()` can take, as ids a report can read.
CLOSE_ORDERS = ((True, "close-then-raise"), (False, "raise-before-close"))


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
@pytest.mark.parametrize(
    ("label", "nth", "classification", "identity_known"),
    CLOSE_FAILURE_SITES,
    ids=[row[0] for row in CLOSE_FAILURE_SITES],
)
def test_a_close_failure_at_each_descriptor_is_closed_and_accounts_for_the_object(
    model: Path,
    label: str,
    nth: int,
    classification: str,
    identity_known: bool,
    close_first: bool,
    order: str,
) -> None:
    """The whole contract for one descriptor, in both orders a close can fail.

    No raw `OSError`; a closed classification; the object that now exists named
    **exactly once** in the returned result; every later item untried; the
    identity the read-back established still recorded; and the live
    provisioner's private account agreeing with the run it returned.
    """
    case = f"{label} / {order}"
    targets = model_targets(model)
    provisioner = armed()

    with failing_close(close_first=close_first, nth=nth):
        run = provisioner.apply(targets)

    # 1. It refused, in the closed vocabulary, on the item it was applying.
    assert run.refusal is not None, case
    assert run.refusal.item_id == "V12", case
    assert run.refusal.classification == classification, case
    assert classification in POST_CREATION_REFUSALS, case
    assert classification in PROVISIONER_REFUSALS, case

    # 2. The residue is exactly one directory at V12's name, and it carries the
    #    ownership and mode the item declares: those were applied through the
    #    descriptor before it was released.
    residue = Path(targets[0].path)
    assert residue.is_dir(), case
    assert list(residue.iterdir()) == [], case
    assert residue.stat().st_mode & 0o7777 == items_by_id()["V12"].mode, case
    assert residue.stat().st_uid == os.geteuid(), case
    for later in targets[1:]:
        assert not Path(later.path).exists(), f"{case}: {later.item_id}"

    # 3. The object is in the returned result **exactly once**. Both the
    #    creation and the finalization observed it, and a second `AppliedItem`
    #    would report one directory as two.
    assert [item.item_id for item in run.applied] == ["V12"], case
    assert [item.item_id for item in run.created] == ["V12"], case
    assert not run.complete, case
    assert run.not_attempted == ("V4", "V9", "V5"), case

    # 4. The identity survives, so the guarded reversal is still available.
    created = run.created[0]
    assert created.outcome is Outcome.CREATED, case
    assert created.removable is identity_known, case
    assert bool(created.object_id) is identity_known, case
    assert run.recoverable is identity_known, case
    assert run.unidentified == (), case
    observed = facts(residue)
    assert created.object_id == f"{observed.st_dev}:{observed.st_ino}", case

    # 5. The refusal is safe to hand an operator: no path, no `errno` text.
    detail = run.refusal.detail
    assert INJECTED_MESSAGE not in detail, case
    assert str(model) not in detail, case
    assert "EIO" not in detail and "Errno" not in detail, case

    # 6. The live provisioner agrees with the result it returned.
    assert provisioner.created == tuple(run.created), case


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
def test_the_reviewer_reproduction_is_closed(
    model: Path, close_first: bool, order: str
) -> None:
    """**Codex's reproduction, asserted as it was reported.**

    *"Making the first `os.close(fd)` at the end of `_complete_creation()` close
    the real descriptor and then raise"* left `OSError: [Errno 5] injected close
    failure at /secret` escaping raw, while V12 existed, `provisioner.created`
    was `()` and no `ProvisioningRun` was returned. All four are asserted here,
    and the raise-before-close order beside it.
    """
    targets = model_targets(model)
    provisioner = armed()

    with failing_close(close_first=close_first, nth=1):
        run = provisioner.apply(targets)

    assert Path(targets[0].path).is_dir(), order
    assert run is not None, order
    assert run.applied != (), order
    assert run.created != (), order
    assert provisioner.created != (), order
    assert run.refusal is not None, order
    assert run.refusal.classification == DESCRIPTOR_NOT_RELEASED, order


def test_a_failure_to_release_the_created_descriptor_refuses_before_the_barrier(
    model: Path,
) -> None:
    """The barrier is an effect, and it is not issued after the decision to
    refuse.

    This application refuses **before** an effect rather than after it, so a
    release that did not report success stops the sequence where it happened.
    The consequence is stated rather than hidden: the entry is visible and is
    not durable, which is what the refusal's own detail says, and the object is
    recorded so the operator can reverse it.
    """
    targets = model_targets(model)
    provisioner = armed()
    barriers = 0
    real_fsync = os.fsync

    def counted(fd: int) -> None:
        nonlocal barriers
        barriers += 1
        real_fsync(fd)

    os.fsync = counted
    try:
        with failing_close(close_first=True, nth=1):
            run = provisioner.apply(targets)
    finally:
        os.fsync = real_fsync

    assert run.refusal is not None
    assert run.refusal.classification == DESCRIPTOR_NOT_RELEASED
    assert barriers == 0
    assert "is not durable" in run.refusal.detail
    assert Path(targets[0].path).is_dir()


def test_a_close_failure_reports_the_objects_completed_before_it(
    model: Path,
) -> None:
    """The earlier items are in the result too, and the later ones are untried.

    V12 releases three descriptors cleanly, so the fourth release is V4's
    created-object descriptor. V12 is complete, V4 is the unfinished one, and
    the two after it were never attempted.
    """
    targets = model_targets(model)
    provisioner = armed()

    with failing_close(close_first=True, nth=4):
        run = provisioner.apply(targets)

    assert run.refusal is not None
    assert run.refusal.item_id == "V4"
    assert run.refusal.classification == DESCRIPTOR_NOT_RELEASED
    assert [item.item_id for item in run.applied] == ["V12", "V4"]
    assert [item.item_id for item in run.created] == ["V12", "V4"]
    assert run.not_attempted == ("V9", "V5")
    assert provisioner.created == tuple(run.created)

    assert Path(targets[0].path).is_dir()
    assert Path(targets[1].path).is_dir()
    assert not Path(targets[2].path).exists()
    assert not Path(targets[3].path).exists()
    # Both are this application's to reverse: each identity was read from the
    # descriptor before the release that failed.
    assert run.recoverable
    assert [item.item_id for item in run.removable] == ["V12", "V4"]


def test_a_cascading_close_failure_still_releases_the_descriptor_after_it(
    model: Path,
) -> None:
    """A failure on the synchronizable descriptor must not skip the traversal
    one.

    The old `finally: os.close(synchronizable); os.close(traversal)` leaked the
    second whenever the first raised. Here every release from the second onwards
    reports failure, and the module attempts all of them: three descriptors
    opened, three releases attempted, one refusal.
    """
    targets = model_targets(model)
    provisioner = armed()
    attempted: list[int] = []
    real = os.close
    seen = 0

    def injected(fd: int) -> None:
        nonlocal seen
        seen += 1
        attempted.append(fd)
        real(fd)
        if seen >= 2:
            raise OSError(errno.EIO, INJECTED_MESSAGE)

    os.close = injected
    try:
        run = provisioner.apply(targets)
    finally:
        os.close = real

    assert run.refusal is not None
    assert run.refusal.classification == DESCRIPTOR_NOT_RELEASED
    # Three descriptors opened, three releases attempted, all distinct. The
    # third is the one the old `finally` leaked whenever the second raised.
    assert len(attempted) == 3
    assert len(set(attempted)) == 3
    assert [item.item_id for item in run.created] == ["V12"]
    assert provisioner.created == tuple(run.created)


def test_a_descriptor_whose_release_failed_is_never_closed_again(
    model: Path,
) -> None:
    """**No blind retry, and no reuse.**

    A `close()` that reports failure says nothing usable about the descriptor,
    so the module treats the number as spent. Closing it a second time could
    close a descriptor something else has since been handed — turning a reported
    failure into a real one elsewhere — and this asserts that no descriptor is
    passed to `os.close` twice, including the one whose release failed having
    released nothing.
    """
    targets = model_targets(model)
    provisioner = armed()
    passed: list[int] = []
    withheld: list[int] = []
    real = os.close
    seen = 0

    def injected(fd: int) -> None:
        nonlocal seen
        seen += 1
        passed.append(fd)
        if seen == 1:
            withheld.append(fd)
            raise OSError(errno.EIO, INJECTED_MESSAGE)
        real(fd)

    os.close = injected
    try:
        run = provisioner.apply(targets)
    finally:
        os.close = real
        for fd in withheld:
            with contextlib.suppress(OSError):
                real(fd)

    assert run.refusal is not None
    assert run.refusal.classification == DESCRIPTOR_NOT_RELEASED
    assert passed, "the application path releases descriptors"
    assert len(passed) == len(set(passed))
    assert passed.count(withheld[0]) == 1


#: One row per primary refusal, paired with a `close` that also fails: the
#: label, the `os` call to break, how to narrow it, the classification that must
#: survive, and which release to break.
#:
#: **The last column is the honest part.** Five of the six refusals are
#: established while the created object's descriptor is still held, so breaking
#: the first release puts the two failures in the same unwinding. The barrier is
#: not: `fsync` is issued *after* that descriptor has already been released, so
#: breaking the first release would refuse before the barrier was ever reached
#: and the row would assert nothing about precedence. For that row the break
#: moves to the second release, which is the first one that unwinds through the
#: barrier's refusal.
PRIMARY_REFUSALS_WITH_A_FAILING_CLOSE = (
    ("open", "open", {"when": _with_dir_fd}, POST_CREATION_OPEN_FAILED, 1),
    ("fchown", "fchown", {}, OWNERSHIP_NOT_APPLIED, 1),
    ("fchmod", "fchmod", {}, MODE_NOT_APPLIED, 1),
    ("read-back fstat", "fstat", {"after": 2}, VERIFICATION_UNREADABLE, 1),
    ("read-back listing", "listdir", {}, VERIFICATION_FAILED, 1),
    ("parent barrier", "fsync", {}, BARRIER_FAILED, 2),
)


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
@pytest.mark.parametrize(
    ("label", "call", "narrowing", "classification", "nth"),
    PRIMARY_REFUSALS_WITH_A_FAILING_CLOSE,
    ids=[row[0] for row in PRIMARY_REFUSALS_WITH_A_FAILING_CLOSE],
)
def test_a_close_failure_never_replaces_an_established_refusal(
    model: Path,
    label: str,
    call: str,
    narrowing: dict,
    classification: str,
    nth: int,
    close_first: bool,
    order: str,
) -> None:
    """**The precedence rule, over every post-creation refusal.**

    The first causal refusal wins. A cleanup failure while it unwinds is
    subordinate: it is a fact about a descriptor, and replacing a fact about the
    operator's object with it would report the wrong cause. The old
    `finally: os.close(fd)` did exactly that, and turned each of these six into
    a raw `OSError`.
    """
    case = f"{label} / {order}"
    targets = model_targets(model)
    provisioner = armed()

    with failing_close(close_first=close_first, nth=nth, cascade=True):
        with failing(call, **narrowing):
            run = provisioner.apply(targets)

    assert run.refusal is not None, case
    assert run.refusal.item_id == "V12", case
    assert run.refusal.classification == classification, case
    assert run.refusal.classification != DESCRIPTOR_NOT_RELEASED, case
    # The object still travels with the refusal, and still exactly once.
    assert [item.item_id for item in run.applied] == ["V12"], case
    assert [item.item_id for item in run.created] == ["V12"], case
    assert provisioner.created == tuple(run.created), case
    assert run.not_attempted == ("V4", "V9", "V5"), case
    assert Path(targets[0].path).is_dir(), case
    assert INJECTED_MESSAGE not in run.refusal.detail, case
    assert "Errno" not in run.refusal.detail, case


def test_a_close_failure_never_replaces_a_refusal_raised_before_any_creation(
    model: Path,
) -> None:
    """The same rule on the other side of the `mkdirat`, for both parent
    descriptors.

    `_open_parent`'s own cleanup releases them too, and a `close` that failed
    there would replace a `PARENT_UNSAFE_OWNERSHIP` or wrong-object refusal with
    an unclassified error — about a parent nobody created, for an item nothing
    applied.
    """
    targets = model_targets(model)

    # The parent an identity other than the applying one may write: the
    # `/opt/freedom-blades` shape, refused before anything is created.
    (model / "var").chmod(0o777)
    with failing_close(close_first=True, nth=1, cascade=True):
        run = armed().apply(targets)

    assert run.refusal is not None
    assert run.refusal.classification == PARENT_UNSAFE_OWNERSHIP
    assert run.applied == ()
    assert run.created == ()
    assert not Path(targets[0].path).exists()

    # And an unexplained object already at the name, which refuses after the
    # verification has opened and released descriptors of its own.
    (model / "var").chmod(0o700)
    armed().apply(targets).raise_if_refused()
    Path(targets[0].path).chmod(0o700)
    second = armed()
    with failing_close(close_first=True, nth=3, cascade=True):
        wrong = second.apply(targets)

    assert wrong.refusal is not None
    assert wrong.refusal.classification == OBJECT_WRONG_MODE
    assert second.created == ()
    assert Path(targets[0].path).stat().st_mode & 0o7777 == 0o700


def test_a_close_failure_after_identity_is_established_keeps_guarded_rollback(
    model: Path,
) -> None:
    """The reversal is available, guarded exactly as it is for any other
    residue.

    The identity came from the descriptor before the release failed, so the
    guard has something to re-observe — and it is still a guard: a replaced
    object refuses and nothing is removed.
    """
    targets = model_targets(model)
    provisioner = armed()

    with failing_close(close_first=True, nth=1):
        run = provisioner.apply(targets)

    assert run.recoverable
    assert [item.item_id for item in run.removable] == ["V12"]

    removed = provisioner.rollback(targets)
    assert [item.item_id for item in removed] == ["V12"]
    assert not Path(targets[0].path).exists()
    assert (model / "var").is_dir()
    assert provisioner.created == ()

    # The same case, with the object replaced before the reversal: the guard
    # refuses and removes nothing.
    replacing = armed()
    with failing_close(close_first=True, nth=1):
        replacing.apply(targets)

    residue = Path(targets[0].path)
    substitute = residue.parent / "substitute"
    substitute.mkdir(mode=0o700)
    residue.rmdir()
    substitute.rename(residue)

    with pytest.raises(ProvisioningRefused) as refusal:
        replacing.rollback(targets)

    assert refusal.value.classification == ROLLBACK_IDENTITY_MISMATCH
    assert residue.is_dir()


def test_an_already_provisioned_item_whose_descriptor_will_not_release_refuses(
    model: Path,
) -> None:
    """`ensure` releases the same two parent descriptors after a verification.

    Nothing was created, so nothing is in `created` — and the item **is** in
    `applied`, because `applied` answers *what is on disk* and the verified
    object is. The refusal says only what is true: this application cannot state
    that the item finished cleanly.

    **The break is on the third release, and that is a scope boundary rather
    than a convenience.** Verifying an existing object releases two descriptors
    of its own first, inside `_verify_one`, and those two are **not** changed by
    this pass: they are `verify()`'s, they are reached before any `mkdirat`, and
    PR-20260916-LAB-V6R2-1 is about the window after one. They are reported in
    the handback as an observed and deliberately unchanged site. The two this
    test breaks are `ensure`'s own, which are in scope and in the finding.
    """
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    before = facts(Path(targets[0].path))

    second = armed()
    with failing_close(close_first=True, nth=3, cascade=True):
        run = second.apply(targets)

    assert run.refusal is not None
    assert run.refusal.item_id == "V12"
    assert run.refusal.classification == DESCRIPTOR_NOT_RELEASED
    assert [item.item_id for item in run.applied] == ["V12"]
    assert run.applied[0].outcome is Outcome.ALREADY_PROVISIONED
    assert run.applied[0].object_id == ""
    assert run.created == ()
    assert run.removable == ()
    assert run.unidentified == ()
    assert run.not_attempted == ("V4", "V9", "V5")
    # It created nothing, so it may remove nothing, and it wrote nothing.
    assert second.created == ()
    assert second.rollback(targets) == ()
    after = facts(Path(targets[0].path))
    assert (after.st_dev, after.st_ino) == (before.st_dev, before.st_ino)
    assert after.st_ctime_ns == before.st_ctime_ns


def test_the_application_path_releases_every_descriptor_through_one_helper() -> None:
    """**Structural**, over the module's own syntax tree.

    The three functions that release a descriptor on the application path do it
    through `_release` and not through a bare `os.close`, because a bare one
    raises — which is the defect — and because a `finally` holding two of them
    skips the second when the first fails. `_release` itself closes **once**:
    a retry loop would be the unsafe assumption this pass refuses to make.
    """
    source = (TOOLS / "execution" / "provisioner.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    releasing = {"ensure", "_complete_creation", "_open_parent"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in releasing:
            continue
        for call in ast.walk(node):
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "os"
            ):
                assert call.func.attr != "close", node.name

    helper = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_release"
    )
    closes = [
        call
        for call in ast.walk(helper)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "close"
    ]
    assert len(closes) == 1
    # And it reports rather than raising: no `raise` anywhere in it.
    assert not [node for node in ast.walk(helper) if isinstance(node, ast.Raise)]


# ---------------------------------------------------------------------------
# 11. Releasing the verification's and the reversal's descriptors —
#     C-P5.0-LAB-V6-R4
#
# Codex Blocking finding PR-20260916-LAB-V6R3-1. Section 10 routed the three
# descriptors the *application* path holds through `_release`, and said so: four
# bare `os.close` calls were left, two in `_verify_one` and two in `_remove`,
# and all four still raised. They break two public operations:
#
#   verify()   -> _verify_one(): object descriptor      *** RAW OSError ***
#   verify()   -> _verify_one(): parent descriptor      *** RAW OSError ***
#   _existing()-> _verify_one(), inside ensure()        *** RAW OSError ***
#   rollback() -> _remove(): object and parent          *** RAW OSError ***
#
# `verify()` is the read-only V6 re-observation of r6 §9.3 I12, and its contract
# is to return every finding: a raise there abandons every *later* target
# unobserved, over a descriptor rather than over anything about an object. The
# same code reached through `_existing()` turns an already-provisioned
# application into an unclassified error. And in `_remove`, a release failure
# could replace the identity or emptiness refusal that was unwinding — or, worse,
# arrive *after* a successful `rmdir`, so that `rollback()` raised before
# updating `_created` and the live account went on naming an object that had
# just been removed.
#
# Every test below drives the real mechanism over real temporary-directory
# objects and breaks a real `os.close`, in both orders a close can fail in.
# ---------------------------------------------------------------------------


#: The two descriptors `_verify_one` releases, in the order it releases them,
#: as `(label, nth)` for the **first** target a verification reaches.
VERIFICATION_RELEASES = (
    ("the observed object's descriptor", 1),
    ("the observed parent's descriptor", 2),
)

#: The same two, for the one `_remove` holds. The object's is released *before*
#: the `rmdir` and the parent's *after* it, which is why the two rows are not
#: interchangeable and have their own tests below.
REVERSAL_RELEASES = (
    ("the reversal's object descriptor", 1),
    ("the reversal's parent descriptor", 2),
)


def provisioned(model: Path) -> tuple[DirectoryTarget, ...]:
    """A model host with all four items applied, and the targets for them."""
    targets = model_targets(model)
    armed().apply(targets).raise_if_refused()
    return targets


def inode_facts(targets) -> list[tuple[int, int, int]]:
    """`(st_dev, st_ino, st_ctime_ns)` per target — the *nothing was written*
    control, which is `st_ctime_ns` and not merely the inode."""
    return [
        (facts(Path(t.path)).st_dev, facts(Path(t.path)).st_ino,
         facts(Path(t.path)).st_ctime_ns)
        for t in targets
    ]


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
@pytest.mark.parametrize(
    ("label", "nth"), VERIFICATION_RELEASES, ids=[row[0] for row in VERIFICATION_RELEASES]
)
def test_the_verification_returns_every_observation_when_a_release_fails(
    model: Path, label: str, nth: int, close_first: bool, order: str
) -> None:
    """**The V6 re-observation stays complete, and stays read-only.**

    One `ItemObservation` per target, in the order given, with the release
    failure reported as a closed discrepancy on the item it happened to — and
    the three later targets observed exactly as they would have been. Before the
    fix this call left a raw `OSError` and returned nothing at all, so **no**
    target was reported, including the three the failure says nothing about.
    """
    case = f"{label} / {order}"
    targets = provisioned(model)
    before = inode_facts(targets)

    with failing_close(close_first=close_first, nth=nth):
        observations = armed().verify(targets)

    # 1. Every target is observed, in the order it was given.
    assert [o.item_id for o in observations] == [t.item_id for t in targets], case

    # 2. The first carries the closed release discrepancy, and nothing else: the
    #    object itself is exactly what its item defines.
    first = observations[0]
    assert first.present, case
    assert first.discrepancies == (DESCRIPTOR_NOT_RELEASED,), case
    assert DESCRIPTOR_NOT_RELEASED in OBSERVATION_DISCREPANCIES, case
    assert not first.matches, case
    assert first.parent_is_exclusive, case

    # 3. The facts it had already read are still returned. A finding about this
    #    observation's descriptor does not erase what it observed.
    assert first.observed_owner == os.geteuid(), case
    assert first.observed_mode == items_by_id()["V12"].mode, case
    assert first.observed_link_count == 4, case

    # 4. The later targets are observed and clean.
    for later in observations[1:]:
        assert later.matches, f"{case}: {later.item_id}"

    # 5. Read-only: no inode and no `st_ctime_ns` moved, and no operating-system
    #    message reached an operator-facing finding.
    assert inode_facts(targets) == before, case
    for observation in observations:
        for finding in observation.discrepancies:
            assert finding in OBSERVATION_DISCREPANCIES, case
            assert INJECTED_MESSAGE not in finding, case
            assert str(model) not in finding, case


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
def test_a_verification_release_failure_does_not_stop_the_later_targets(
    model: Path, close_first: bool, order: str
) -> None:
    """The failure lands on **V9**, the third target, and V5 is still observed.

    Stated as its own row because *"returns four observations"* and *"goes on
    after the one that failed"* are different claims: the first could be met by
    a verification that collected its findings and raised at the end.
    """
    targets = provisioned(model)
    # V12 obj, V12 parent, V4 obj, V4 parent, V9 obj — the fifth release.
    with failing_close(close_first=close_first, nth=5):
        observations = armed().verify(targets)

    by_id = {o.item_id: o for o in observations}
    assert set(by_id) == {"V12", "V4", "V9", "V5"}, order
    assert by_id["V9"].discrepancies == (DESCRIPTOR_NOT_RELEASED,), order
    assert by_id["V12"].matches and by_id["V4"].matches, order
    assert by_id["V5"].matches, order
    assert by_id["V5"].observed_mode == items_by_id()["V5"].mode, order


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
@pytest.mark.parametrize(
    ("label", "nth"), VERIFICATION_RELEASES, ids=[row[0] for row in VERIFICATION_RELEASES]
)
def test_a_verification_release_failure_never_replaces_the_objects_findings(
    model: Path, label: str, nth: int, close_first: bool, order: str
) -> None:
    """**Precedence, on the read-only path.**

    The object disagrees with its definition *and* the descriptor will not
    release. Both are reported, the object's finding is first, and the release
    is last — which is what lets `_existing` take the first as the primary one.
    """
    case = f"{label} / {order}"
    targets = provisioned(model)
    Path(targets[0].path).chmod(0o700)

    with failing_close(close_first=close_first, nth=nth):
        observations = armed().verify(targets)

    first = observations[0]
    assert first.discrepancies == (OBJECT_WRONG_MODE, DESCRIPTOR_NOT_RELEASED), case
    assert first.observed_mode == 0o700, case
    assert len(observations) == 4, case


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
@pytest.mark.parametrize(
    ("label", "nth"), VERIFICATION_RELEASES, ids=[row[0] for row in VERIFICATION_RELEASES]
)
def test_an_already_provisioned_apply_whose_verification_cannot_release_refuses(
    model: Path, label: str, nth: int, close_first: bool, order: str
) -> None:
    """**The same condition on the application path, closed.**

    `_existing()` reaches `_verify_one` inside `ensure()`, so before the fix an
    idempotent re-run could leave a raw `OSError`. It is now the closed
    `DESCRIPTOR_NOT_RELEASED`, carrying the `ALREADY_PROVISIONED` result the
    verification reached — **once**, because two `AppliedItem`s would report one
    directory as two — with `created` empty because nothing was created, every
    later item untried, and not a byte written.
    """
    case = f"{label} / {order}"
    targets = provisioned(model)
    before = inode_facts(targets)

    second = armed()
    with failing_close(close_first=close_first, nth=nth):
        run = second.apply(targets)

    assert run.refusal is not None, case
    assert run.refusal.item_id == "V12", case
    assert run.refusal.classification == DESCRIPTOR_NOT_RELEASED, case
    assert run.refusal.classification in PROVISIONER_REFUSALS, case
    assert [item.item_id for item in run.applied] == ["V12"], case
    assert run.applied[0].outcome is Outcome.ALREADY_PROVISIONED, case
    assert run.applied[0].object_id == "", case
    assert run.created == (), case
    assert run.removable == (), case
    assert run.unidentified == (), case
    assert run.not_attempted == ("V4", "V9", "V5"), case
    # It created nothing, so it may remove nothing — and it wrote nothing.
    assert second.created == (), case
    assert second.rollback(targets) == (), case
    assert inode_facts(targets) == before, case
    assert INJECTED_MESSAGE not in run.refusal.detail, case
    assert "Errno" not in run.refusal.detail, case


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
@pytest.mark.parametrize(
    ("label", "nth"), VERIFICATION_RELEASES, ids=[row[0] for row in VERIFICATION_RELEASES]
)
def test_a_verification_release_failure_never_replaces_an_apply_refusal(
    model: Path, label: str, nth: int, close_first: bool, order: str
) -> None:
    """An unexplained object at a provisioned name still refuses **as itself**.

    The operator is told their object carries the wrong mode. A refusal about a
    descriptor in its place would send them to look at the wrong thing, and the
    object would still be there either way.
    """
    case = f"{label} / {order}"
    targets = provisioned(model)
    Path(targets[0].path).chmod(0o700)

    second = armed()
    with failing_close(close_first=close_first, nth=nth):
        run = second.apply(targets)

    assert run.refusal is not None, case
    assert run.refusal.classification == OBJECT_WRONG_MODE, case
    assert run.refusal.classification != DESCRIPTOR_NOT_RELEASED, case
    # The release is still reported, in the list of disagreements, rather than
    # being dropped: it is subordinate, not invisible.
    assert DESCRIPTOR_NOT_RELEASED in run.refusal.detail, case
    assert run.applied == (), case
    assert run.created == (), case
    assert second.created == (), case
    assert Path(targets[0].path).stat().st_mode & 0o7777 == 0o700, case


#: One row per **causal** reversal refusal, paired with a release that also
#: fails: the label, how to arrange the refusal, the classification that must
#: survive, and which release to break.
#:
#: **The last column is the honest part, as it was for row 87.** The identity
#: and emptiness guards are established while the object's descriptor is still
#: held, so breaking the first release puts both failures in one unwinding. The
#: `rmdir` refusal is not: the object's descriptor is released *before* the
#: `rmdir` is issued, so breaking the first release would refuse before the
#: `rmdir` was ever reached and the row would assert nothing. For that row the
#: break moves to the parent's release, which is the first one that unwinds
#: through the `rmdir` refusal.
REVERSAL_REFUSALS_WITH_A_FAILING_CLOSE = (
    ("identity mismatch", "replace", ROLLBACK_IDENTITY_MISMATCH, 1),
    ("not empty", "fill", ROLLBACK_NOT_EMPTY, 1),
    ("rmdir refused", "break-rmdir", ROLLBACK_NOT_EMPTY, 2),
)


@contextlib.contextmanager
def _arranged(arrangement: str, path: Path):
    """The three ways a guarded removal refuses, arranged over a real object."""
    if arrangement == "replace":
        substitute = path.parent / "substitute"
        substitute.mkdir(mode=0o700)
        path.rmdir()
        substitute.rename(path)
        yield
    elif arrangement == "fill":
        (path / "capture-basis").write_bytes(b"pre-change bytes")
        yield
    else:
        with failing("rmdir"):
            yield


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
@pytest.mark.parametrize(
    ("label", "arrangement", "classification", "nth"),
    REVERSAL_REFUSALS_WITH_A_FAILING_CLOSE,
    ids=[row[0] for row in REVERSAL_REFUSALS_WITH_A_FAILING_CLOSE],
)
def test_a_reversal_release_failure_never_replaces_the_causal_refusal(
    model: Path,
    label: str,
    arrangement: str,
    classification: str,
    nth: int,
    close_first: bool,
    order: str,
) -> None:
    """**Precedence, on the operator-directed recovery path.**

    An operator running a reversal is answering *what is still on this host*.
    Replacing *the object at this name is not the one you created* with *a
    descriptor did not release* answers a question they did not ask, and hides
    the guard that stopped the removal. Every one of these refused raw before
    the fix.
    """
    case = f"{label} / {order}"
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets[:1]).raise_if_refused()
    created = provisioner.created

    with _arranged(arrangement, Path(targets[0].path)):
        with failing_close(close_first=close_first, nth=nth, cascade=True):
            with pytest.raises(ProvisioningRefused) as refusal:
                provisioner.rollback(targets[:1])

    assert refusal.value.classification == classification, case
    assert refusal.value.classification != ROLLBACK_NOT_REMOVED_NOT_RELEASED, case
    assert refusal.value.classification != ROLLBACK_REMOVED_NOT_RELEASED, case
    # Nothing was removed, and the refusal's own account says so.
    assert isinstance(refusal.value, RollbackRefused), case
    assert refusal.value.removed == (), case
    assert Path(targets[0].path).is_dir(), case
    assert provisioner.created == created, case
    assert INJECTED_MESSAGE not in str(refusal.value), case
    assert "Errno" not in str(refusal.value), case


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
def test_a_release_failure_before_the_rmdir_removes_nothing(
    model: Path, close_first: bool, order: str
) -> None:
    """**The removal is not issued after the decision to refuse.**

    The object's descriptor is what identified it, and the emptiness check ran
    through it. A release that did not report success stops the reversal where
    it happened, exactly as the application path stops before the barrier — so
    the object is untouched, it is still in the live created account, and it is
    still this application's to reverse, which the second reversal proves.
    """
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets[:1]).raise_if_refused()
    before = facts(Path(targets[0].path))

    with failing_close(close_first=close_first, nth=1):
        with pytest.raises(RollbackRefused) as refusal:
            provisioner.rollback(targets[:1])

    assert refusal.value.classification == ROLLBACK_NOT_REMOVED_NOT_RELEASED, order
    assert refusal.value.classification in PROVISIONER_REFUSALS, order
    assert refusal.value.classification in ROLLBACK_REFUSALS, order
    assert refusal.value.removed == (), order
    # The object is exactly where it was.
    after = facts(Path(targets[0].path))
    assert (after.st_dev, after.st_ino) == (before.st_dev, before.st_ino), order
    # And the live account is truthful: it still says the object exists, which
    # it does, and the reversal it was offered still works.
    assert [item.item_id for item in provisioner.created] == ["V12"], order
    assert [item.item_id for item in provisioner.rollback(targets[:1])] == ["V12"], order
    assert not Path(targets[0].path).exists(), order
    assert provisioner.created == (), order


@pytest.mark.parametrize(
    ("close_first", "order"), CLOSE_ORDERS, ids=[row[1] for row in CLOSE_ORDERS]
)
def test_a_release_failure_after_the_rmdir_reports_the_removal(
    model: Path, close_first: bool, order: str
) -> None:
    """**The defect Codex named, and the accounting it broke.**

    `rmdir()` returns success and the parent descriptor then fails to release.
    Before the fix `rollback()` raised an unclassified `OSError` *before*
    updating `_created`, so the live provisioner went on saying an object
    existed that it had just removed — and offered it for a second reversal that
    would have aimed at whatever now stood at the name.

    Now the two facts are both told: the object **was** removed, and this
    application cannot state that the reversal finished cleanly.
    """
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets[:1]).raise_if_refused()

    with failing_close(close_first=close_first, nth=2):
        with pytest.raises(RollbackRefused) as refusal:
            provisioner.rollback(targets[:1])

    # 1. A closed classification, and the one that says the object is gone.
    assert refusal.value.classification == ROLLBACK_REMOVED_NOT_RELEASED, order
    assert refusal.value.classification in PROVISIONER_REFUSALS, order
    assert refusal.value.classification in ROLLBACK_REMOVING_REFUSALS, order

    # 2. The object really is gone, and the parent is untouched.
    assert not Path(targets[0].path).exists(), order
    assert (model / "var").is_dir(), order

    # 3. The raised result and the live account agree that it is gone, and it
    #    appears in the removed account exactly once.
    assert [item.item_id for item in refusal.value.removed] == ["V12"], order
    assert refusal.value.removed[0].outcome is Outcome.CREATED, order
    assert provisioner.created == (), order

    # 4. A retry cannot target it again: there is nothing left to remove, and it
    #    refuses nothing rather than reaching for a name it no longer owns.
    assert provisioner.rollback(targets[:1]) == (), order

    # 5. Safe to hand an operator.
    assert INJECTED_MESSAGE not in str(refusal.value), order
    assert str(model) not in str(refusal.value), order
    assert "Errno" not in str(refusal.value), order


def test_a_reversal_that_refuses_part_way_reports_what_it_already_removed(
    model: Path,
) -> None:
    """The same accounting rule, without a close failure at all.

    `_created` used to be rewritten only after the whole loop, so **any**
    refusal part-way through a reversal left every object it had already removed
    in the live account. Here V5 and V9 are removed and V4 refuses on content
    somebody else put there: the refusal names what is gone, `created` holds only
    what is still on the host, and a second reversal does not aim at V5 or V9.
    """
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets).raise_if_refused()
    (Path(targets[1].path) / "operator-notes").write_bytes(b"not this tool's")

    with pytest.raises(RollbackRefused) as refusal:
        provisioner.rollback(targets)

    assert refusal.value.classification == ROLLBACK_NOT_EMPTY
    assert refusal.value.item_id == "V4"
    assert [item.item_id for item in refusal.value.removed] == ["V5", "V9"]
    assert [item.item_id for item in provisioner.created] == ["V12", "V4"]
    assert not Path(targets[3].path).exists()
    assert not Path(targets[2].path).exists()
    assert Path(targets[1].path).is_dir()
    assert Path(targets[0].path).is_dir()


def test_every_verification_descriptor_after_a_failing_release_is_still_attempted(
    model: Path,
) -> None:
    """Eight descriptors, eight releases attempted, all distinct.

    A verification of four present objects opens two descriptors per target. The
    old shape released the object's in a `finally` the parent's close sat
    outside of, so a failure on one could skip the other — and a failure on the
    first target abandoned the six descriptors of the three after it, because
    nothing was opened for them at all.

    **Every release here reports failure having released nothing**, which is the
    order that makes the distinctness assertion mean something: a descriptor the
    kernel really released has its number handed back, so a later target would
    reuse it and eight releases of eight descriptors would look like two. None
    is released, so the eight numbers are eight objects. They are closed on the
    way out of the test, because the module under test must not retry a close
    whose outcome it cannot know.
    """
    targets = provisioned(model)
    attempted: list[int] = []
    withheld: list[int] = []
    real = os.close

    def injected(fd: int) -> None:
        attempted.append(fd)
        withheld.append(fd)
        raise OSError(errno.EIO, INJECTED_MESSAGE)

    os.close = injected
    try:
        observations = armed().verify(targets)
    finally:
        os.close = real
        for fd in withheld:
            with contextlib.suppress(OSError):
                real(fd)

    assert len(attempted) == 8
    assert len(set(attempted)) == 8
    assert len(observations) == 4
    for observation in observations:
        assert observation.discrepancies == (DESCRIPTOR_NOT_RELEASED,), observation.item_id


def test_a_reversals_parent_descriptor_is_released_after_its_object_descriptor_fails(
    model: Path,
) -> None:
    """**No leak, and no second close.**

    The object's release fails having released nothing, the parent's is still
    attempted, and neither number is passed to `os.close` twice — a second close
    of a descriptor the kernel may already have released can close one something
    else has since been handed.
    """
    targets = model_targets(model)
    provisioner = armed()
    provisioner.apply(targets[:1]).raise_if_refused()
    passed: list[int] = []
    withheld: list[int] = []
    real = os.close
    seen = 0

    def injected(fd: int) -> None:
        nonlocal seen
        seen += 1
        passed.append(fd)
        if seen == 1:
            withheld.append(fd)
            raise OSError(errno.EIO, INJECTED_MESSAGE)
        real(fd)

    os.close = injected
    try:
        with pytest.raises(RollbackRefused) as refusal:
            provisioner.rollback(targets[:1])
    finally:
        os.close = real
        for fd in withheld:
            with contextlib.suppress(OSError):
                real(fd)

    assert refusal.value.classification == ROLLBACK_NOT_REMOVED_NOT_RELEASED
    assert len(passed) == 2
    assert len(set(passed)) == 2
    assert passed.count(withheld[0]) == 1
    assert Path(targets[0].path).is_dir()


def test_the_four_reported_release_sites_no_longer_raise(model: Path) -> None:
    """**The reproduction table of the R3 handback's §3, asserted.**

    Four entry points, each reaching one of the four bare `os.close` calls that
    pass left. Each left a raw `OSError`. None of them raises now, and each
    returns the shape its own contract promises: observations, a run, or a
    reversal refusal that says what it removed.
    """
    targets = provisioned(model)

    # 1 and 2. `verify()` -> `_verify_one`, object and parent descriptors.
    for nth in (1, 2):
        with failing_close(close_first=True, nth=nth):
            observations = armed().verify(targets)
        assert len(observations) == 4, nth
        assert DESCRIPTOR_NOT_RELEASED in observations[0].discrepancies, nth

    # 3. `_existing()` -> `_verify_one`, inside `ensure()`.
    with failing_close(close_first=True, nth=1):
        run = armed().apply(targets)
    assert run.refusal is not None
    assert run.refusal.classification == DESCRIPTOR_NOT_RELEASED

    # 4. `rollback()` -> `_remove`, object descriptor.
    provisioner = armed()
    fresh = model_targets(model / "second")
    (model / "second" / "opt").mkdir(parents=True, mode=0o700)
    (model / "second" / "var").mkdir(mode=0o700)
    provisioner.apply(fresh[:1]).raise_if_refused()
    with failing_close(close_first=True, nth=1):
        with pytest.raises(RollbackRefused) as refusal:
            provisioner.rollback(fresh[:1])
    assert refusal.value.classification == ROLLBACK_NOT_REMOVED_NOT_RELEASED
    assert Path(fresh[0].path).is_dir()


def test_no_release_anywhere_in_the_module_is_a_bare_close() -> None:
    """**Structural**, over the module's own syntax tree, and now total.

    Section 10's guard covered the three functions on the application path.
    The four calls this pass repairs were outside it, so the guard is widened to
    the only shape that cannot be outgrown: **`_release` is the one function in
    this module that calls `os.close` at all**, it calls it once, and it does
    not raise. A release added to a new function tomorrow is caught here rather
    than by whoever runs the reversal.
    """
    source = (TOOLS / "execution" / "provisioner.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name == "_release":
            continue
        for call in ast.walk(node):
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "os"
            ):
                assert call.func.attr != "close", node.name


def test_a_reversal_refusal_cannot_disagree_with_what_it_removed() -> None:
    """**The invalid combination is unconstructible, not merely unused.**

    A reversal refusal answers *what is still on the host*. A classification
    that says an object was removed while the removed account omits it — or one
    that says it was not while the account names it — is a refusal that lies
    about an effect, and neither can be built.
    """
    removed = AppliedItem(
        item_id="V12", path="/model/evidence", outcome=Outcome.CREATED, object_id="7:9"
    )

    # The one classification that says the object is gone requires it to be in
    # the account.
    with pytest.raises(HarnessError):
        RollbackRefused(ROLLBACK_REMOVED_NOT_RELEASED, "V12", removed=())
    intact = RollbackRefused(ROLLBACK_REMOVED_NOT_RELEASED, "V12", removed=(removed,))
    assert intact.removed == (removed,)

    # Every other one says it is still there, so it must not be in the account.
    with pytest.raises(HarnessError):
        RollbackRefused(ROLLBACK_NOT_REMOVED_NOT_RELEASED, "V12", removed=(removed,))
    with pytest.raises(HarnessError):
        RollbackRefused(ROLLBACK_NOT_EMPTY, "V12", removed=(removed,))
    assert RollbackRefused(ROLLBACK_NOT_EMPTY, "V12", removed=()).removed == ()

    # One object, removed once.
    with pytest.raises(HarnessError):
        RollbackRefused(
            ROLLBACK_REMOVED_NOT_RELEASED, "V12", removed=(removed, removed)
        )

    # And the vocabulary is closed: a reversal cannot refuse with a
    # classification nobody specified for one.
    with pytest.raises(HarnessError):
        RollbackRefused(BARRIER_FAILED, "V12")
    assert set(ROLLBACK_REFUSALS) <= PROVISIONER_REFUSALS
    assert ROLLBACK_REMOVING_REFUSALS <= set(ROLLBACK_REFUSALS)
    assert ROLLBACK_REMOVING_REFUSALS == {ROLLBACK_REMOVED_NOT_RELEASED}
    assert isinstance(intact, ProvisioningRefused)


def test_an_observation_reports_only_findings_from_the_closed_vocabulary() -> None:
    """The read-only half of the same rule.

    `ItemObservation.discrepancies` reaches an operator exactly as a refusal
    does, so it carries the same kind of value and no other. `with_discrepancy`
    is additive and idempotent: a release failure on both the object's
    descriptor and the parent's is one finding about one observation, and it
    never displaces what was observed about the object.
    """
    observed = ItemObservation(
        item_id="V12",
        path="/model/evidence",
        present=True,
        discrepancies=(OBJECT_WRONG_MODE,),
        parent_is_exclusive=True,
    )

    with pytest.raises(HarnessError):
        ItemObservation(
            item_id="V12",
            path="/model/evidence",
            present=True,
            discrepancies=("close-failed",),
            parent_is_exclusive=True,
        )

    once = observed.with_discrepancy(DESCRIPTOR_NOT_RELEASED)
    assert once.discrepancies == (OBJECT_WRONG_MODE, DESCRIPTOR_NOT_RELEASED)
    assert once.with_discrepancy(DESCRIPTOR_NOT_RELEASED) is once
    # The observation it was built from is untouched: the finding is added to a
    # copy, so nothing already reported can be rewritten by a later failure.
    assert observed.discrepancies == (OBJECT_WRONG_MODE,)
    assert set(OBSERVATION_DISCREPANCIES) <= PROVISIONER_REFUSALS


def test_a_removal_effect_exists_only_where_the_object_is_gone() -> None:
    """Both members mean removed, and there is no member for *not removed*.

    A removal that did not happen is a refusal, and a refusal is not an effect.
    Giving the effect vocabulary a `NOT_REMOVED` member would make it possible
    to return one — and a caller that stopped checking for the refusal would
    then update its account for an object that is still there.
    """
    assert set(RemovalEffect) == {
        RemovalEffect.REMOVED,
        RemovalEffect.REMOVED_NOT_FINALIZED,
    }
    assert RemovalEffect.REMOVED_NOT_FINALIZED.value.startswith("removed")
