"""The reserved-laboratory mechanism, over a real filesystem — C-P5.0-LAB-I.

## What these tests are, and what they are not

`test_r2_proposal_models.py`, `test_r3_lifecycle.py`, `test_r4_remediation.py`
and `test_r5_remediation.py` exercise runner contract r6's rules over
`durability_model`'s synthetic filesystem, whose whole state is a dictionary.
Every row they establish is **[M] modelled**: it shows the proposed rule is
constructible and falsifiable, and it establishes nothing about Linux and
nothing about `oracle-test`.

This module exercises the same rules over **real descriptors, real files and
real `fsync` calls**, under a temporary directory. That converts a set of r6 §9
rows from `[P]` — specified, with no test, because they need the mechanism — into
rows an implementation actually satisfies.

It converts **nothing** into evidence about the target. In particular:

* no test here observes `oracle-test`, and none may be cited for it;
* `tmp_path` is almost always `tmpfs` or `ext4` on this workstation, so a
  passing barrier here says nothing about V6 or V8 on the target's filesystem;
  those remain unconfirmed preflight items;
* nothing here provisions anything. Every path is under `tmp_path`, and no
  object is created under `/run` or `/var/lib` — which C-P5.0-LAB-I forbids and
  `test_the_laboratory_suite_creates_nothing_outside_the_temporary_tree`
  asserts against this file's own source; and
* `is_executable` stays `False`, C-7 stays unresolved and EH-R16-1 stays Open.
  Code that exists is not a finding that closed.

## The negative controls

Every load-bearing check has one. A test that asserts a refusal proves nothing
unless removing the check makes it pass, so the controls here remove exactly one
conjunct — the identity comparison, the barrier, the binding — and assert that
the previously refused input is then accepted. They are named
`…_control` and each says which line it removes.
"""
from __future__ import annotations

import ast
import errno
import os
from pathlib import Path

import pytest

from tests.phase_5_0_evidence.lab_fixtures import (
    AT,
    ATTESTER,
    BASIS,
    HOST,
    OTHER_TARGET,
    TARGET_IDENTITY,
    bind,
    build_laboratory,
    recovery_store,
)
from tests.phase_5_0_evidence.lifecycle_fixtures import observed
from tools.phase_5_0_evidence.durability_model import DescriptorMode, Quiescence
from tools.phase_5_0_evidence.execution import descriptors as descriptors_module
from tools.phase_5_0_evidence.execution.descriptors import (
    DESCRIPTOR_BARRIER_FAILED,
    DESCRIPTOR_IDENTITY_MISMATCH,
    DESCRIPTOR_MODE_REFUSED,
    DESCRIPTOR_NOT_BOUND,
    DESCRIPTOR_NOT_REGISTERED,
    DESCRIPTOR_OBJECT_EXISTS,
    DESCRIPTOR_REFUSALS,
    DescriptorInventory,
    DescriptorRefused,
    ObjectIdentity,
    PosixFilesystem,
)
from tools.phase_5_0_evidence.execution.executor import (
    RUN_DIRECTORIES,
    DescriptorBoundEffects,
    EffectRefused,
    FS_APPEND_FL,
    _read_inode_flags,
)
from tools.phase_5_0_evidence.execution.host_lock import (
    LOCK_ABSENT,
    LOCK_HELD,
    LOCK_NOT_HELD,
    HostLock,
    LockRefused,
)
from tools.phase_5_0_evidence.execution.materializer import (
    RESTORE_BARRIER_FAILED,
    RESTORE_DESTINATION_MISMATCH,
    RESTORE_DIGEST_MISMATCH,
    RESTORE_LEFTOVER_TEMPORARY,
    RESTORE_RECORD_MISSING,
    RESTORE_TEMPORARY_SUFFIX,
    publication_permits_mutation,
    restore_configuration,
)
from tools.phase_5_0_evidence.execution.recovery_store import (
    BARRIER_ORDER,
    CAPTURE_BARRIER_FAILED,
    CAPTURE_RUN_DIRECTORY_EXISTS,
    CAPTURE_SOURCE_UNREADABLE,
    DISCOVERY_LEFTOVER_TEMPORARY,
    RECORD_SUFFIX,
    STORED_OBJECT_MODE,
    TEMPORARY_SUFFIX,
)
from tools.phase_5_0_evidence.execution.participants import (
    PARTICIPANT_NOT_ADMITTED,
    HarnessObservations,
    ParticipantIntegration,
)
from tools.phase_5_0_evidence.execution.run_ledger import TerminalSequence
from tools.phase_5_0_evidence.lifecycle_storage import (
    PARTICIPANT_PROFILES,
    PARTICIPANTS,
    DurableRecordStore,
    EntryKind,
    FirstUseEvidence,
    FirstUseRefusal,
    Participant,
    PublicationRefusal,
    RecordRefusal,
    TemporaryRemovalRefusal,
    serialize_history,
)
from tools.phase_5_0_evidence.reservation import (
    ReleaseEvidence,
    ReservationRequest,
    ReservationState,
    ResidueObservation,
)

pytestmark = pytest.mark.filterwarnings("error")

THIS_FILE = Path(__file__).resolve()
FIXTURE_FILE = THIS_FILE.parent / "lab_fixtures.py"


# ---------------------------------------------------------------------------
# r6 §1.3 — descriptor custody, over real descriptors
# ---------------------------------------------------------------------------


def test_a_directory_is_held_twice_and_the_two_descriptors_differ(tmp_path) -> None:
    """§1.3.2: one object, two modes, and a reader can tell them apart."""
    lab = build_laboratory(tmp_path)
    inventory = DescriptorInventory()
    try:
        handle = inventory.open_provisioned_root(
            "laboratory", lab.layout.laboratory_directory
        )
        synchronizable = inventory.bind_synchronizable("laboratory")
        assert synchronizable != handle.traversal_fd
        # Two descriptions of one object: the identities agree.
        assert ObjectIdentity.of(synchronizable) == handle.identity
    finally:
        inventory.close()


def test_fsync_on_the_traversal_descriptor_is_refused(tmp_path) -> None:
    """`open(2)` does not list `fsync` among an `O_PATH` description's operations.

    r2 required it on `bin_fd` and on `pgconf_fd`, both of which it had defined
    `O_PATH`. Neither call can succeed, and this asserts that the mechanism
    refuses it as a rule of its own rather than waiting for `EBADF` — so the
    refusal does not depend on which kernel the mechanism happens to run on.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        traversal = bound.inventory.traversal("laboratory")
        with pytest.raises(DescriptorRefused) as refusal:
            bound.filesystem.fsync(traversal)
        assert refusal.value.classification == DESCRIPTOR_MODE_REFUSED
    finally:
        bound.close()


def test_the_kernel_also_refuses_fsync_on_an_o_path_description(tmp_path) -> None:
    """The documented behaviour, observed rather than asserted from the page.

    It is issued directly, outside the mechanism's own guard, so the row is
    about the kernel and not about this module's rule.
    """
    directory = tmp_path / "plain"
    directory.mkdir()
    fd = os.open(str(directory), os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        with pytest.raises(OSError):
            os.fsync(fd)
    finally:
        os.close(fd)


def test_a_substitution_between_the_two_opens_is_detected(tmp_path) -> None:
    """§1.3.2's second property: the result is **compared**, not assumed.

    The entry is replaced between the traversal open and the synchronizable one,
    so the second lookup reaches a different object. The comparison refuses the
    publication; it does not retry and does not fall back to a path.
    """
    lab = build_laboratory(tmp_path)
    inventory = DescriptorInventory()
    try:
        inventory.open_provisioned_root(
            "laboratory", lab.layout.laboratory_directory
        )
        inventory.adopt_directory(
            parent_role="laboratory", name="runs", role="runs"
        )
        # An unrelated cooperating writer replaces the entry.
        runs = lab.runs_directory
        runs.rename(runs.parent / "runs.moved")
        (runs.parent / "runs").mkdir()
        with pytest.raises(DescriptorRefused) as refusal:
            inventory.bind_synchronizable("runs")
        assert refusal.value.classification == DESCRIPTOR_IDENTITY_MISMATCH
    finally:
        inventory.close()


def test_the_substitution_control_accepts_it_when_the_comparison_is_removed(
    tmp_path,
) -> None:
    """**Negative control.** Remove the identity comparison, accept the swap.

    It re-issues exactly the two calls `bind_synchronizable` issues and omits
    the one comparison between them. The swapped directory is then bound, which
    is what the check exists to prevent — so the check is load-bearing rather
    than decorative.
    """
    lab = build_laboratory(tmp_path)
    inventory = DescriptorInventory()
    try:
        inventory.open_provisioned_root(
            "laboratory", lab.layout.laboratory_directory
        )
        handle = inventory.adopt_directory(
            parent_role="laboratory", name="runs", role="runs"
        )
        runs = lab.runs_directory
        runs.rename(runs.parent / "runs.moved")
        (runs.parent / "runs").mkdir()
        parent = inventory.traversal("laboratory")
        fd = os.open(
            "runs",
            os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY,
            dir_fd=parent,
        )
        try:
            # The comparison that is deliberately not made here:
            assert ObjectIdentity.of(fd) != handle.identity
        finally:
            os.close(fd)
    finally:
        inventory.close()


def test_an_unregistered_descriptor_is_never_used_as_one(tmp_path) -> None:
    """A number from outside the declared table is refused, not dereferenced."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    spare = os.open(str(tmp_path), os.O_RDONLY | os.O_DIRECTORY)
    try:
        with pytest.raises(DescriptorRefused) as refusal:
            bound.filesystem.fstatat(spare, "pgconf")
        assert refusal.value.classification == DESCRIPTOR_NOT_REGISTERED
    finally:
        os.close(spare)
        bound.close()


def test_a_synchronizable_descriptor_may_not_be_traversed(tmp_path) -> None:
    """The two use sites stay apart, so a reader can tell the two apart by them."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        synchronizable = bound.inventory.bind_synchronizable("laboratory")
        with pytest.raises(DescriptorRefused) as refusal:
            bound.filesystem.fstatat(synchronizable, "runs")
        assert refusal.value.classification == DESCRIPTOR_MODE_REFUSED
    finally:
        bound.close()


def test_no_synchronizable_descriptor_is_ever_in_a_transferred_set(tmp_path) -> None:
    """r2's unstated narrowing, stated: a step that cannot `fsync` cannot claim.

    Every entry a transfer table hands out is a traversal descriptor, and the
    rule has its own refusal so that weakening it is a visible edit.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        bound.inventory.bind_synchronizable("laboratory")
        table = bound.inventory.declare_transfer(["laboratory", "runs"])
        assert [entry.index for entry in table] == [3, 4]
        assert all(entry.mode is DescriptorMode.O_PATH for entry in table)
        for entry in table:
            assert bound.inventory.dirfd_for_index(entry.index) == (
                bound.inventory.traversal(entry.role)
            )
        with pytest.raises(DescriptorRefused) as refusal:
            bound.inventory.refuse_synchronizable_transfer("laboratory")
        assert refusal.value.classification == "descriptor-transfer-refused"
    finally:
        bound.close()


def test_an_index_outside_the_declared_table_refuses(tmp_path) -> None:
    """`DIRFD` is an index into a table this run declared, and into nothing else."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        bound.inventory.declare_transfer(["laboratory"])
        assert bound.inventory.dirfd_for_index(3) > 0
        for index in (0, 2, 4, 99):
            with pytest.raises(DescriptorRefused) as refusal:
                bound.inventory.dirfd_for_index(index)
            assert refusal.value.classification == DESCRIPTOR_NOT_REGISTERED
    finally:
        bound.close()


@pytest.mark.parametrize("name", ["a/b", ".", "..", "", " leading", "trailing "])
def test_a_component_is_exactly_one_component(tmp_path, name: str) -> None:
    """The prefix binding covers a component; it does not cover a pathname."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        traversal = bound.inventory.traversal("laboratory")
        with pytest.raises(DescriptorRefused):
            bound.filesystem.fstatat(traversal, name)
    finally:
        bound.close()


def test_every_refusal_this_module_raises_is_in_the_closed_vocabulary() -> None:
    """A refusal that reaches an operator carries a fixed classification.

    The vocabulary is closed so an operator-facing refusal cannot acquire a new
    meaning by being raised, and the constructor refuses a value outside it.
    """
    with pytest.raises(Exception):
        DescriptorRefused("a new meaning nobody reviewed", "laboratory")
    assert len(DESCRIPTOR_REFUSALS) == 11


def test_a_refusal_names_a_role_and_never_a_path(tmp_path) -> None:
    """Fixed refusals expose no path, no bytes and no operating-system text."""
    lab = build_laboratory(tmp_path)
    inventory = DescriptorInventory()
    try:
        with pytest.raises(DescriptorRefused) as refusal:
            inventory.open_provisioned_root("laboratory", str(tmp_path / "absent"))
        message = str(refusal.value)
        assert str(tmp_path) not in message
        assert "No such file" not in message
        assert refusal.value.role == "laboratory"
    finally:
        inventory.close()


# ---------------------------------------------------------------------------
# r6 §5.3 — the cooperative lock
# ---------------------------------------------------------------------------


def test_an_absent_lock_refuses_and_is_never_created(tmp_path) -> None:
    """An absent lock means the host was not provisioned. A participant waits."""
    lab = build_laboratory(tmp_path, with_lock=False)
    lock = HostLock(path=lab.layout.lock_path)
    with pytest.raises(LockRefused) as refusal:
        lock.acquire()
    assert refusal.value.classification == LOCK_ABSENT
    assert not lab.lock_path.exists()


def test_a_held_lock_refuses_rather_than_proceeding(tmp_path) -> None:
    """Wait or refuse, never proceed — the rule for all seven participants."""
    lab = build_laboratory(tmp_path)
    first = HostLock(path=lab.layout.lock_path)
    first.acquire()
    try:
        second = HostLock(path=lab.layout.lock_path)
        with pytest.raises(LockRefused) as refusal:
            second.acquire()
        assert refusal.value.classification == LOCK_HELD
        assert not second.held
    finally:
        first.release()


def test_the_lock_is_takeable_again_once_released(tmp_path) -> None:
    """The preserved positive control: the refusals do not refuse everything."""
    lab = build_laboratory(tmp_path)
    with HostLock(path=lab.layout.lock_path) as first:
        assert first.held
    second = HostLock(path=lab.layout.lock_path)
    second.acquire()
    assert second.held
    second.release()


def test_a_participant_that_holds_no_lock_supplies_no_observation(tmp_path) -> None:
    """A lock view is an observation, and an observation needs an observer."""
    lab = build_laboratory(tmp_path)
    lock = HostLock(path=lab.layout.lock_path)
    with pytest.raises(LockRefused) as refusal:
        lock.view()
    assert refusal.value.classification == LOCK_NOT_HELD


def test_the_lock_file_is_never_unlinked_or_replaced(tmp_path) -> None:
    """The inode is persistent: taking and releasing it does not touch the name."""
    lab = build_laboratory(tmp_path)
    before = lab.lock_path.stat()
    with HostLock(path=lab.layout.lock_path):
        pass
    after = lab.lock_path.stat()
    assert (before.st_dev, before.st_ino) == (after.st_dev, after.st_ino)


# ---------------------------------------------------------------------------
# r6 §§5.4–5.10 — the reservation record, on disk
# ---------------------------------------------------------------------------


def _initialize(bound, **overrides):
    fields = {
        "approved_host": HOST,
        "approved_target_identity": TARGET_IDENTITY,
        "evidence": FirstUseEvidence(
            prior_use_excluded=True, attested_by=ATTESTER, basis=BASIS
        ),
        "attested_at": AT,
    }
    fields.update(overrides)
    return bound.record.initialize(**fields)


def test_verified_first_use_writes_a_durable_record(tmp_path) -> None:
    """§5.10, over real bytes: exclusive creation, both barriers, then readable."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        outcome = _initialize(bound)
        assert outcome.initialized and outcome.durable
        assert outcome.barriers == ("record-data", "record-entry")
        assert lab.record_path.exists()
        parsed = bound.record.read()
        assert parsed.ok
        assert [entry.kind for entry in parsed.entries] == [EntryKind.FIRST_USE]
        assert parsed.entries[0].fields["basis"] == BASIS
    finally:
        bound.close()


def test_a_second_initialization_never_overwrites_the_history(tmp_path) -> None:
    """`already_initialized`: the existing record **is** the history."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        before = lab.record_path.read_bytes()
        outcome = _initialize(bound)
        assert not outcome.initialized
        assert outcome.refusal is FirstUseRefusal.ALREADY_INITIALIZED
        assert lab.record_path.read_bytes() == before
    finally:
        bound.close()


def test_initialization_bound_to_an_unapproved_target_refuses(tmp_path) -> None:
    """R3-3: `BINDING_MISMATCH` has a branch that produces it, and no record."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab, target_identity=OTHER_TARGET)
    try:
        outcome = _initialize(bound)
        assert not outcome.initialized
        assert outcome.refusal is FirstUseRefusal.BINDING_MISMATCH
        assert not lab.record_path.exists()
    finally:
        bound.close()


def test_an_unattested_first_use_refuses(tmp_path) -> None:
    """A first use is a positive claim, and its absence is not the claim."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        outcome = _initialize(bound, evidence=FirstUseEvidence())
        assert outcome.refusal is FirstUseRefusal.NO_FIRST_USE_EVIDENCE
        assert not lab.record_path.exists()
    finally:
        bound.close()


def test_a_missing_record_on_a_used_host_is_never_reinitialized(tmp_path) -> None:
    """The dangerous refusal. Missing history on a used host is not first use."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        outcome = _initialize(bound, host_previously_used=True)
        assert outcome.refusal is FirstUseRefusal.PRIOR_USE_NOT_EXCLUDED
        assert not lab.record_path.exists()
        assert any("rebuild" in line for line in outcome.recovery)
    finally:
        bound.close()


@pytest.mark.parametrize("point", ["record-data", "rename", "record-entry"])
def test_an_interruption_at_each_publication_point_is_distinguished(
    tmp_path, point: str
) -> None:
    """§5.6's three points, over real files.

    `record-data` and `rename` leave a temporary and no record. `record-entry`
    is R3-1: the record is **visible** and this writer is the only party that
    knows its containing entry was never synchronized.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        outcome = _initialize(bound, fail_at=point)
        assert not outcome.initialized
        assert outcome.refusal is FirstUseRefusal.NOT_DURABLE
        if point == "record-entry":
            assert lab.record_path.exists(), "R3-1: the record is visible"
            assert bound.record.present()
        else:
            assert not lab.record_path.exists()
            assert bound.record.temporary_present()
    finally:
        bound.close()


def test_a_leftover_publication_temporary_blocks_and_is_not_removed(
    tmp_path,
) -> None:
    """§2.13.2b's precedent: reported, never cleaned by the next participant."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound, fail_at="rename")
        assert bound.record.temporary_present()
        outcome = _initialize(bound)
        assert outcome.refusal is FirstUseRefusal.INTERRUPTED_INITIALIZATION
        assert bound.record.temporary_present(), "still there, by design"
    finally:
        bound.close()


def test_the_reseal_needs_no_write_permission_and_is_idempotent(tmp_path) -> None:
    """§5.6 and preflight item I8, as far as a local filesystem can show it.

    The successor `fsync`es the record's containing entry through a descriptor
    that grants no write permission on anything. Re-sealing an already durable
    entry is a successful no-op, so the reader never has to know which case it
    is in.

    **This is not V8.** Whether the target's filesystem implements a directory
    `fsync` as the containing-entry barrier is unconfirmed, and a successful
    call here is not that observation.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        bound.record.reseal()
        bound.record.reseal()
        bound.ledger.reseal()
    finally:
        bound.close()


def test_a_failed_reseal_refuses_the_whole_pass(tmp_path) -> None:
    """A failed barrier is an attributable operator recovery, never a continue."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        bound.record.store.reseal_fails = True
        with pytest.raises(Exception):
            bound.record.reseal()
    finally:
        bound.close()


def test_a_tampered_stored_record_refuses_and_is_never_normalized(tmp_path) -> None:
    """§5.5's ten tampers, over bytes on disk rather than bytes in a dictionary.

    A refusal returns **no entries at all**: handing back the prefix that parsed
    is precisely how a truncated history gets read as a shorter one, and a
    shorter history can end on an admitting entry.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        good = lab.record_path.read_bytes()
        tampers = (
            # The magic line is the first thing a reader compares, and bytes
            # from elsewhere are not a history.
            ("missing magic", RecordRefusal.MALFORMED,
             good.replace(b"freedom-blades-laboratory-lifecycle", b"other", 1)),
            # r6 raises the schema to 2, so an r5 record refuses **by name**
            # rather than being reinterpreted under the new meanings.
            ("an r5 schema", RecordRefusal.UNSUPPORTED_SCHEMA,
             good.replace(b"schema=2", b"schema=1", 1)),
            # The terminator is the truncation detector: a record whose tail was
            # lost spells a shorter history, and a shorter history can end on an
            # admitting entry.
            ("a lost tail", RecordRefusal.TRUNCATED,
             good.replace(b"end-history\n", b"", 1)),
            ("another approved target", RecordRefusal.WRONG_BINDING,
             good.replace(f"target={TARGET_IDENTITY}".encode(),
                          f"target={OTHER_TARGET}".encode(), 1)),
            # An unknown kind is a refusal rather than something to skip:
            # skipping an unrecognised entry hides the run it describes.
            ("an unknown kind", RecordRefusal.MALFORMED,
             good.replace(b"kind=first_use", b"kind=something_new", 1)),
            # The schema is bounded, so an added field is a refusal and not
            # something a writer can smuggle past a reader.
            ("an added field", RecordRefusal.MALFORMED,
             good.replace(b"end-entry\n", b"smuggled=value\nend-entry\n", 1)),
            # Two meanings, and a reader that took the last would be choosing.
            ("a duplicate key", RecordRefusal.MALFORMED,
             good.replace(b"kind=first_use\n", b"kind=first_use\nkind=first_use\n", 1)),
            ("an emptied binding", RecordRefusal.MISSING_BINDING,
             good.replace(f"target={TARGET_IDENTITY}\n".encode(), b"target=\n", 1)),
            ("a renumbered sequence", RecordRefusal.HISTORY_ORDER,
             good.replace(b"sequence=1", b"sequence=7", 1)),
            # An entry begun and never closed is a lost tail, which is the
            # truncation detector rather than a shape refusal.
            ("an unclosed entry", RecordRefusal.TRUNCATED,
             good.replace(b"end-entry\n", b"", 1)),
        )
        for label, expected, raw in tampers:
            lab.record_path.write_bytes(raw)
            parsed = bound.record.read()
            assert not parsed.ok, label
            assert parsed.entries == (), "a refusal returns no entries at all"
            assert parsed.refusal is expected, label
        lab.record_path.write_bytes(good)
        assert bound.record.read().ok, "the preserved positive control"
    finally:
        bound.close()


# ---------------------------------------------------------------------------
# r6 §§5.11–5.12 — the ledger and the terminal sequence, on disk
# ---------------------------------------------------------------------------


def _request(reservation_id: str) -> ReservationRequest:
    return ReservationRequest(
        reservation_id=reservation_id,
        owner="root, the executor",
        host=HOST,
        target_identity=TARGET_IDENTITY,
        requested_at=AT,
        deadline="2026-09-13T14:00:00Z",
        recovery_owner=ATTESTER,
    )


def _evidence(reservation_id: str, **overrides) -> ReleaseEvidence:
    fields = {
        "reservation_id": reservation_id,
        "target_identity": TARGET_IDENTITY,
        "lock_held_by": reservation_id,
        "child_processes_ended": True,
        "database_transactions_settled": True,
        "residue": ResidueObservation.empty(
            observed_by="the operator, post-run sweep", searched_at=AT
        ),
        "configuration_restored": True,
    }
    fields.update(overrides)
    return ReleaseEvidence(**fields)


def _running_reservation(bound, reservation_id: str, run_id: str) -> None:
    """Initialize, admit, start the harness run, and go RUNNING — in that order.

    The run's start is published **before** the first effect and carries the
    reservation it owns, which is the whole of R5-1's stored repair.
    """
    _initialize(bound)
    assert bound.record.admit_reservation(
        reservation_id=reservation_id, author="root", at=AT
    ).published
    assert bound.ledger.begin(
        run_id=run_id,
        participant=Participant.HARNESS_CLI,
        author="root",
        at=AT,
        reservation_id=reservation_id,
    ).published
    assert bound.record.start_running(
        reservation_id=reservation_id, author="root", at=AT
    ).published


def test_the_complete_terminal_sequence_settles_both_halves(tmp_path) -> None:
    """§5.12's four steps, over real files, on a correctly bound run."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _running_reservation(bound, "RES-1", "RES-1-harness")
        sequence = TerminalSequence(record=bound.record, ledger=bound.ledger)
        result = sequence.conclude(
            request=_request("RES-1"),
            current_state=ReservationState.RUNNING,
            evidence=_evidence("RES-1"),
            run_id="RES-1-harness",
            author="root",
            at=AT,
            observed_by="the operator, post-run sweep",
        )
        assert result.concluded, result.refusals
        assert result.decision is ReservationState.RELEASED
        survey = bound.ledger.survey()
        assert survey.completed == ("RES-1-harness",)
        assert survey.unsettled == () and survey.invalid == ()
    finally:
        bound.close()


def test_the_wrong_reservation_conclusion_publishes_nothing(tmp_path) -> None:
    """**R5-1's reproduction, against the mechanism.**

    A release of reservation `A` offered to conclude a run started for `B`.
    Step 0 refuses before the release decision, so A's RELEASED entry is never
    published — the record's bytes are unchanged — and B's started bytes are
    byte-identical.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _running_reservation(bound, "RES-1", "RES-2-harness-for-another")
        # The run above belongs to RES-1 by its stored start. Conclude RES-9
        # against it: the name says nothing, the stored field does.
        record_before = lab.record_path.read_bytes()
        run_before = (lab.runs_directory / "RES-2-harness-for-another").read_bytes()
        sequence = TerminalSequence(record=bound.record, ledger=bound.ledger)
        result = sequence.conclude(
            request=_request("RES-9"),
            current_state=ReservationState.RUNNING,
            evidence=_evidence("RES-9"),
            run_id="RES-2-harness-for-another",
            author="root",
            at=AT,
            observed_by="the operator",
        )
        assert not result.concluded
        assert result.release_entry is None, "nothing was published"
        assert result.completion is None
        assert lab.record_path.read_bytes() == record_before
        assert (
            lab.runs_directory / "RES-2-harness-for-another"
        ).read_bytes() == run_before
        # The run still blocks every successor.
        assert bound.ledger.survey().unsettled == ("RES-2-harness-for-another",)
    finally:
        bound.close()


def test_the_binding_is_not_inferred_from_the_run_name(tmp_path) -> None:
    """A run named `RES-9-harness` started for `RES-1` belongs to `RES-1`.

    This row fails the moment an implementation reads a reservation out of a
    filename, which is why no filename convention is adopted.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _running_reservation(bound, "RES-1", "RES-9-harness")
        sequence = TerminalSequence(record=bound.record, ledger=bound.ledger)
        assert sequence.conclude(
            request=_request("RES-1"),
            current_state=ReservationState.RUNNING,
            evidence=_evidence("RES-1"),
            run_id="RES-9-harness",
            author="root",
            at=AT,
            observed_by="the operator",
        ).concluded
    finally:
        bound.close()


def test_failure_between_the_release_and_the_completion_blocks(tmp_path) -> None:
    """§5.12's window, over real files.

    The release is published and durable, the completion is not, and the
    executor's own run is still `participant_started` in the ledger — so the
    release alone admits nobody. That is the whole argument for the order.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _running_reservation(bound, "RES-1", "RES-1-harness")
        sequence = TerminalSequence(record=bound.record, ledger=bound.ledger)
        result = sequence.conclude(
            request=_request("RES-1"),
            current_state=ReservationState.RUNNING,
            evidence=_evidence("RES-1"),
            run_id="RES-1-harness",
            author="root",
            at=AT,
            observed_by="the operator",
            fail_completion_at="rename",
        )
        assert not result.concluded
        assert result.release_entry is not None and result.release_entry.published
        assert result.completion is not None and not result.completion.published
        survey = bound.ledger.survey()
        assert "RES-1-harness" in (survey.unsettled + survey.unreadable)
    finally:
        bound.close()


def test_a_harness_start_with_no_reservation_refuses_at_the_writer(tmp_path) -> None:
    """R5-1's stored half: the binding is not optional for the one that owns it."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        for value in ("", "   ", " RES-1 ", "RES|1", "RES\n1"):
            outcome = bound.ledger.begin(
                run_id="RES-1-harness",
                participant=Participant.HARNESS_CLI,
                author="root",
                at=AT,
                reservation_id=value,
            )
            assert not outcome.published, value
            assert outcome.refusal is PublicationRefusal.INVALID_HISTORY
            assert not (lab.runs_directory / "RES-1-harness").exists()
    finally:
        bound.close()


@pytest.mark.parametrize(
    "participant", [p for p in PARTICIPANTS if p is not Participant.HARNESS_CLI]
)
def test_the_six_carry_the_binding_exactly_empty(tmp_path, participant) -> None:
    """One representation, required in both directions.

    The six whose completion conditions are **external** carry the reservation
    field exactly empty, and any non-empty value refuses for them.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        assert bound.ledger.begin(
            run_id=f"{participant.name.lower()}-run",
            participant=participant,
            author="ubuntu",
            at=AT,
        ).published
        refused = bound.ledger.begin(
            run_id=f"{participant.name.lower()}-claiming",
            participant=participant,
            author="ubuntu",
            at=AT,
            reservation_id="RES-1",
        )
        assert not refused.published
        assert refused.refusal is PublicationRefusal.INVALID_HISTORY
    finally:
        bound.close()


@pytest.mark.parametrize("participant", list(PARTICIPANTS))
def test_every_participant_completes_and_blocks_until_it_does(
    tmp_path, participant
) -> None:
    """All seven, and no exemption — including the environment reset.

    The harness goes through §5.12's order because its two conditions are
    lifecycle-owned; the six complete on their own external conditions.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        run_id = f"{participant.name.lower()}-run"
        if participant is Participant.HARNESS_CLI:
            _running_reservation(bound, "RES-1", run_id)
            assert bound.ledger.survey().unsettled == (run_id,)
            sequence = TerminalSequence(record=bound.record, ledger=bound.ledger)
            assert sequence.conclude(
                request=_request("RES-1"),
                current_state=ReservationState.RUNNING,
                evidence=_evidence("RES-1"),
                run_id=run_id,
                author="root",
                at=AT,
                observed_by="the operator",
            ).concluded
        else:
            _initialize(bound)
            assert bound.ledger.begin(
                run_id=run_id, participant=participant, author="ubuntu", at=AT
            ).published
            assert bound.ledger.survey().unsettled == (run_id,)
            assert bound.ledger.complete(
                run_id=run_id,
                participant=participant,
                observation=observed(participant),
                author="ubuntu",
                at=AT,
            ).published
        assert bound.ledger.survey().completed == (run_id,)
    finally:
        bound.close()


@pytest.mark.parametrize("participant", list(PARTICIPANTS))
def test_a_clean_wrapper_exit_is_not_completion_evidence(tmp_path, participant) -> None:
    """A wrapper's fate is not its effects' fate, for every one of the seven."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        run_id = f"{participant.name.lower()}-run"
        if participant is Participant.HARNESS_CLI:
            _running_reservation(bound, "RES-1", run_id)
        else:
            _initialize(bound)
            assert bound.ledger.begin(
                run_id=run_id, participant=participant, author="ubuntu", at=AT
            ).published
        profile = PARTICIPANT_PROFILES[participant]
        gaps = observed(participant).missing(profile) if profile.external_conditions() else ()
        outcome = bound.ledger.complete(
            run_id=run_id,
            participant=participant,
            observation=observed(
                participant,
                observed={},
                wrapper_exit_status=0,
                lock_released=True,
            ),
            author="ubuntu",
            at=AT,
        )
        assert not outcome.published, gaps
        assert bound.ledger.survey().unsettled == (run_id,)
    finally:
        bound.close()


def test_an_attributable_recovery_settles_a_run_and_admits_the_next(
    tmp_path,
) -> None:
    """An interruption is not an indefinite dead end; it is a bounded action."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        assert bound.ledger.begin(
            run_id="web-1", participant=Participant.WEB_SUITE, author="ubuntu", at=AT
        ).published
        assert bound.ledger.survey().unsettled == ("web-1",)
        assert bound.ledger.recover(
            run_id="web-1",
            participant=Participant.WEB_SUITE,
            reference="operator note 2026-09-13, schema dropped and recreated",
            author=ATTESTER,
            at=AT,
        ).published
        survey = bound.ledger.survey()
        assert survey.unsettled == () and survey.recovered == ("web-1",)
    finally:
        bound.close()


def test_a_missing_ledger_directory_refuses_rather_than_reading_as_empty(
    tmp_path,
) -> None:
    """R4-2's second path: unavailable accounting is not empty accounting."""
    lab = build_laboratory(tmp_path)
    lab.runs_directory.rmdir()
    session = lab.session()
    with pytest.raises(DescriptorRefused) as refusal:
        session.open()
    assert refusal.value.classification == "object-absent"
    session.close()


def test_a_provisioned_ledger_observed_empty_still_admits(tmp_path) -> None:
    """The preserved control: the rule refuses unavailable, not empty."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
    finally:
        bound.close()
    with lab.session(Participant.BOT_SUITE) as session:
        decision = session.admit()
        assert decision.may_proceed, decision.refusals
        assert decision.resealed
        assert decision.runs is not None and decision.runs.settled


def test_an_unsettled_run_refuses_every_successor_including_the_reset(
    tmp_path,
) -> None:
    """R3-2, end to end. The reset is refused **especially**, not exempted."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        assert bound.ledger.begin(
            run_id="sync-1",
            participant=Participant.SYNCHRONIZATION,
            author="ubuntu",
            at=AT,
        ).published
    finally:
        bound.close()
    for participant in PARTICIPANTS:
        with lab.session(participant) as session:
            decision = session.admit()
            assert not decision.may_proceed, participant
            assert any("sync-1" in reason for reason in decision.refusals)


def test_an_admitted_record_refuses_even_with_a_free_lock(tmp_path) -> None:
    """A free process lock is never reuse evidence. **The record decides.**"""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        assert bound.record.admit_reservation(
            reservation_id="RES-1", author="root", at=AT
        ).published
    finally:
        bound.close()
    assert not lab.lock_path.stat().st_size  # the lock carries no state
    with lab.session(Participant.BOT_SUITE) as session:
        decision = session.admit()
        assert not decision.may_proceed
        assert any("RES-1" in reason for reason in decision.refusals)


def test_a_record_for_another_approved_target_refuses_all_seven(tmp_path) -> None:
    """R3-3's reproduction: same hostname, different approved target."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
    finally:
        bound.close()
    for participant in PARTICIPANTS:
        with lab.session(participant, target_identity=OTHER_TARGET) as session:
            decision = session.admit()
            assert not decision.may_proceed, participant


def test_a_contradictory_history_refuses(tmp_path) -> None:
    """Two entries disagreeing about the host are refused, never reconciled."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        raw = lab.record_path.read_bytes()
        lab.record_path.write_bytes(
            raw.replace(f"host={HOST}".encode(), b"host=another-host", 1)
        )
        parsed = bound.record.read()
        assert not parsed.ok
        assert parsed.refusal in (
            RecordRefusal.CONTRADICTORY,
            RecordRefusal.WRONG_BINDING,
        )
    finally:
        bound.close()


def test_a_duplicate_terminal_entry_refuses_explicitly(tmp_path) -> None:
    """The stated policy: the record is append-only, so a second delivery refuses."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _running_reservation(bound, "RES-1", "RES-1-harness")
        sequence = TerminalSequence(record=bound.record, ledger=bound.ledger)
        assert sequence.conclude(
            request=_request("RES-1"),
            current_state=ReservationState.RUNNING,
            evidence=_evidence("RES-1"),
            run_id="RES-1-harness",
            author="root",
            at=AT,
            observed_by="the operator",
        ).concluded
        before = lab.record_path.read_bytes()
        again = bound.record.append(
            kind=EntryKind.RELEASED,
            author="root",
            at=AT,
            fields={"reservation": "RES-1", "released_at": AT},
        )
        assert not again.published
        assert lab.record_path.read_bytes() == before
    finally:
        bound.close()


# ---------------------------------------------------------------------------
# r6 §§2.2–2.5 — the independent recovery store
# ---------------------------------------------------------------------------


def _publish(store, *, run_id="RUN-1", reservation="RES-1", lab=None, **overrides):
    fields = {
        "run_id": run_id,
        "reservation_id": reservation,
        "captured_by": "the harness, as root",
        "sources": {
            "pg_hba.conf": f"{lab.configuration_directory}/pg_hba.conf",
            "pg_ident.conf": f"{lab.configuration_directory}/pg_ident.conf",
        },
        "configuration_role": "pgconf",
    }
    fields.update(overrides)
    return store.publish(**fields)


def test_the_positive_sequence_crosses_every_barrier_and_permits_the_mutation(
    tmp_path,
) -> None:
    """§2.3.3's ordered graph, over real `fsync` calls, in the contract's order."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        publication = _publish(store, lab=lab)
        assert publication.published and publication.mutation_permitted
        assert publication.barriers_crossed == BARRIER_ORDER
        assert publication_permits_mutation(publication)
        assert publication.not_barriers == (
            "a read-back of the stored copy",
            "a digest comparison",
            "a successful rename",
        )
    finally:
        bound.close()


@pytest.mark.parametrize("barrier", BARRIER_ORDER)
def test_failure_at_any_barrier_prevents_the_first_configuration_mutation(
    tmp_path, barrier: str
) -> None:
    """All five, parametrized. Every failure refuses **before M1**."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        publication = _publish(store, lab=lab, fail_at=barrier)
        assert not publication.published
        assert not publication.mutation_permitted
        assert not publication_permits_mutation(publication)
        assert publication.refusal == CAPTURE_BARRIER_FAILED
        assert barrier not in publication.barriers_crossed
    finally:
        bound.close()


def test_the_recovery_parent_entry_barrier_is_the_one_revision_2_omitted(
    tmp_path,
) -> None:
    """PR-20260911-R2-2, named: it is barrier **one**, before any capture.

    Placed at the earliest safe point so that even a crash mid-capture leaves a
    *discoverable* run directory rather than nothing.
    """
    assert BARRIER_ORDER[0] == "recovery-parent-entry"
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        publication = _publish(store, lab=lab, fail_at="recovery-parent-entry")
        assert publication.barriers_crossed == ()
        assert publication.captures == (), "no capture was taken"
    finally:
        bound.close()


def test_a_reused_run_id_refuses_rather_than_publishing_a_second_basis(
    tmp_path,
) -> None:
    """`EEXIST` is the refusal: a run id with a directory is one that was used."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        assert _publish(store, lab=lab).published
        bound.inventory.close()
        second = bind(lab)
        try:
            again = recovery_store(lab, second)
            publication = _publish(again, lab=lab)
            assert publication.refusal == CAPTURE_RUN_DIRECTORY_EXISTS
        finally:
            second.close()
    finally:
        pass


def test_discovery_is_a_listing_of_the_recovery_parent(tmp_path) -> None:
    """§2.5: `readdir` is the discovery mechanism, and no index is proposed."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        found = {run.run_id: run for run in store.discover()}
        assert set(found) == {"RUN-1"}
        basis = found["RUN-1"]
        assert basis.usable
        assert basis.copy_names == ("pg_hba.conf", "pg_ident.conf")
        assert basis.record_names == (
            f"pg_hba.conf{RECORD_SUFFIX}",
            f"pg_ident.conf{RECORD_SUFFIX}",
        )
        for record in basis.records:
            assert record.destination.startswith(str(lab.configuration_directory))
    finally:
        bound.close()


def test_a_stored_copy_is_read_only_and_owned_by_the_writer(tmp_path) -> None:
    """The mode is set on the descriptor before the rename, not on the name."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        stored = lab.recovery_directory / "RUN-1" / "pg_hba.conf"
        assert stored.stat().st_mode & 0o777 == STORED_OBJECT_MODE
    finally:
        bound.close()


def test_a_tampered_stored_copy_is_reported_present_and_not_usable(
    tmp_path,
) -> None:
    """Discoverable, complete and verifying are three questions, not one boolean."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        stored = lab.recovery_directory / "RUN-1" / "pg_hba.conf"
        stored.chmod(0o600)
        stored.write_bytes(b"not what was captured\n")
        basis = {run.run_id: run for run in store.discover()}["RUN-1"]
        assert basis.copy_names and basis.record_names
        assert not basis.usable
        assert not basis.verifiable
    finally:
        bound.close()


def test_an_absent_source_refuses_the_publication_and_the_mutation(
    tmp_path,
) -> None:
    """No recoverable copy, no mutation. §2.1's rule, mechanized."""
    lab = build_laboratory(tmp_path)
    (lab.configuration_directory / "pg_hba.conf").unlink()
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        publication = _publish(store, lab=lab)
        assert publication.refusal == CAPTURE_SOURCE_UNREADABLE
        assert not publication_permits_mutation(publication)
    finally:
        bound.close()


# ---------------------------------------------------------------------------
# r6 §2.4 — verify-and-write restoration
# ---------------------------------------------------------------------------


def _restore(lab, bound, store, **overrides):
    fields = {
        "inventory": bound.inventory,
        "filesystem": bound.filesystem,
        "store": store,
        "run_id": "RUN-1",
        "configuration_role": "pgconf",
        "destination_directory": str(lab.configuration_directory),
        "owner_uid": os.getuid(),
        "owner_gid": os.getgid(),
    }
    fields.update(overrides)
    return restore_configuration(**fields)


def test_a_complete_restoration_is_durable_and_says_so(tmp_path) -> None:
    """Both barriers, in order, and the destination holds the captured bytes."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        bound.inventory.bind_synchronizable("pgconf")
        (lab.configuration_directory / "pg_hba.conf").write_bytes(b"MUTATED\n")
        outcome = _restore(lab, bound, store)
        assert outcome.durable and not outcome.failure
        assert outcome.barriers_crossed == ("restore-data", "restore-entry")
        assert (
            lab.configuration_directory / "pg_hba.conf"
        ).read_bytes() == b"local all all peer\n"
    finally:
        bound.close()


def test_a_rename_without_its_directory_barrier_is_not_a_durable_restoration(
    tmp_path,
) -> None:
    """The case the re-review names: visible, and not durable.

    `renamed` and `durable` are two fields precisely so that L2's reload
    verification can have `durable` as its prerequisite.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        bound.inventory.bind_synchronizable("pgconf")
        (lab.configuration_directory / "pg_hba.conf").write_bytes(b"MUTATED\n")
        outcome = _restore(lab, bound, store, fail_at="restore-entry")
        assert outcome.renamed  # the names resolve to the restored bytes
        assert not outcome.durable  # and the restoration is not reported durable
        assert outcome.failure == RESTORE_BARRIER_FAILED
        assert outcome.mixed
    finally:
        bound.close()


def test_a_restoration_interrupted_before_its_rename_leaves_the_destination_alone(
    tmp_path,
) -> None:
    """The bytes go to a temporary, so the destination is never half-written."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        bound.inventory.bind_synchronizable("pgconf")
        (lab.configuration_directory / "pg_hba.conf").write_bytes(b"MUTATED\n")
        outcome = _restore(lab, bound, store, fail_at="restore-data")
        assert not outcome.renamed and not outcome.durable
        assert (
            lab.configuration_directory / "pg_hba.conf"
        ).read_bytes() == b"MUTATED\n"
    finally:
        bound.close()


def test_a_leftover_restoration_temporary_is_reported_and_blocks(tmp_path) -> None:
    """Detected by listing the destination directory, reported, never cleaned."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        bound.inventory.bind_synchronizable("pgconf")
        leftover = (
            lab.configuration_directory / f"pg_hba.conf{RESTORE_TEMPORARY_SUFFIX}"
        )
        leftover.write_bytes(b"half a restoration\n")
        outcome = _restore(lab, bound, store)
        assert outcome.failure == RESTORE_LEFTOVER_TEMPORARY
        assert outcome.leftovers == (leftover.name,)
        assert leftover.exists(), "reported and not removed"
    finally:
        bound.close()


def test_a_record_naming_another_destination_restores_nowhere(tmp_path) -> None:
    """The destination is part of the binding, not a convenience."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        bound.inventory.bind_synchronizable("pgconf")
        outcome = _restore(
            lab, bound, store, destination_directory=str(tmp_path / "elsewhere")
        )
        assert outcome.failure == RESTORE_DESTINATION_MISMATCH
        assert not outcome.renamed
    finally:
        bound.close()


def test_a_restoration_with_no_basis_refuses(tmp_path) -> None:
    """`R/before` is not an alternative: §2.1's whole point."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        bound.inventory.bind_synchronizable("pgconf")
        outcome = _restore(lab, bound, store)
        assert outcome.failure == RESTORE_RECORD_MISSING
    finally:
        bound.close()


def test_a_tampered_copy_is_never_written_over_the_destination(tmp_path) -> None:
    """Verify first, then write. The digest is over the buffer that gets written."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = recovery_store(lab, bound)
        _publish(store, lab=lab)
        bound.inventory.bind_synchronizable("pgconf")
        stored = lab.recovery_directory / "RUN-1" / "pg_hba.conf"
        stored.chmod(0o600)
        stored.write_bytes(b"tampered\n")
        (lab.configuration_directory / "pg_hba.conf").write_bytes(b"MUTATED\n")
        outcome = _restore(lab, bound, store)
        assert outcome.failure in (RESTORE_DIGEST_MISMATCH, RESTORE_RECORD_MISSING)
        assert (
            lab.configuration_directory / "pg_hba.conf"
        ).read_bytes() == b"MUTATED\n"
    finally:
        bound.close()


# ---------------------------------------------------------------------------
# r6 §§1.4 and 1.6 — the executor's effects and the quiescence gate
# ---------------------------------------------------------------------------


def _effects(tmp_path, *, quiescence=None, armed=True):
    root = tmp_path / "evidence"
    root.mkdir()
    run = root / "run-1"
    inventory = DescriptorInventory()
    inventory.open_provisioned_root("evidence", str(root))
    inventory.create_directory(parent_role="evidence", name="run-1", role="root")
    filesystem = PosixFilesystem(inventory)
    effects = DescriptorBoundEffects(
        inventory=inventory,
        filesystem=filesystem,
        quiescence=quiescence or Quiescence.verified(observed_by="the executor"),
        armed=armed,
    )
    return inventory, filesystem, effects, run


def test_the_five_run_directories_are_created_exclusively(tmp_path) -> None:
    """**P1.** Success *is* the ownership proof; `EEXIST` is the refusal."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        assert effects.create_run_directories() == RUN_DIRECTORIES
        for name in RUN_DIRECTORIES:
            assert (run / name).is_dir()
        with pytest.raises(DescriptorRefused) as refusal:
            inventory.create_directory(
                parent_role="root", name="bin", role="bin-again"
            )
        assert refusal.value.classification == DESCRIPTOR_OBJECT_EXISTS
    finally:
        inventory.close()


def test_an_unarmed_effect_issuer_changes_nothing(tmp_path) -> None:
    """Fails closed in the direction that leaves the host alone."""
    inventory, _fs, effects, run = _effects(tmp_path, armed=False)
    try:
        with pytest.raises(EffectRefused):
            effects.create_run_directories()
        assert list(run.iterdir()) == []
    finally:
        inventory.close()


@pytest.mark.parametrize(
    "quiescence",
    [
        Quiescence.not_observed(),
        Quiescence(observed=True, observed_by="x", processes_ended=False,
                   transactions_settled=True, transient_units_inactive=True),
        Quiescence(observed=True, observed_by="x", processes_ended=True,
                   transactions_settled=None, transient_units_inactive=True),
    ],
    ids=["unobserved", "observed-false", "incomplete"],
)
def test_an_unestablished_quiescence_refuses_every_b3_effect(
    tmp_path, quiescence
) -> None:
    """§1.6: three different inputs and all three refuse. None defaults to true."""
    inventory, _fs, effects, run = _effects(tmp_path, quiescence=quiescence)
    try:
        effects.create_run_directories()
        (run / "journal" / "seal").write_bytes(b"seal\n")
        effects.record_identity(directory_role="journal", name="seal")
        with pytest.raises(EffectRefused) as refusal:
            effects.remove_object(directory_role="journal", name="seal")
        assert "quiescence" in str(refusal.value)
        assert (run / "journal" / "seal").exists(), "the object survives a refusal"
    finally:
        inventory.close()


def test_a_substitution_before_the_pre_check_is_genuinely_detected(
    tmp_path,
) -> None:
    """§1.4.5(2): the one genuine detection, and it refuses before the removal."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        effects.create_run_directories()
        subject = run / "journal" / "seal"
        subject.write_bytes(b"the object this run created\n")
        effects.record_identity(directory_role="journal", name="seal")
        # An unrelated writer replaces the entry.
        subject.rename(run / "journal" / "seal.moved")
        (run / "journal" / "seal").write_bytes(b"a different object\n")
        with pytest.raises(EffectRefused) as refusal:
            effects.remove_object(directory_role="journal", name="seal")
        assert "recorded" in str(refusal.value) and "found" in str(refusal.value)
        assert (run / "journal" / "seal").exists()
    finally:
        inventory.close()


def test_the_post_check_cannot_tell_the_two_removals_apart(tmp_path) -> None:
    """§1.4.5(4)'s counterexample, stated rather than denied.

    The pre-check succeeds for **A**; a writer renames A away and installs **B**
    at the name; the removal takes B; the post-check reports the name absent.
    That is byte-for-byte the observation a correct removal of A produces, and A
    still exists under its new name.
    """
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        effects.create_run_directories()
        journal = run / "journal"

        (journal / "correct").write_bytes(b"A\n")
        effects.record_identity(directory_role="journal", name="correct")
        correct = effects.remove_object(directory_role="journal", name="correct")

        (journal / "substituted").write_bytes(b"A\n")
        identity = effects.record_identity(
            directory_role="journal", name="substituted"
        )
        # The substitution happens **after** the pre-check the removal makes, so
        # the recorded identity is replayed onto the new object to model the
        # window exactly: what the production observation sees is unchanged.
        (journal / "substituted").rename(journal / "A-survives")
        (journal / "substituted").write_bytes(b"B\n")
        effects._recorded[("journal", "substituted")] = (
            effects.record_identity(directory_role="journal", name="substituted")
        )
        substituted = effects.remove_object(
            directory_role="journal", name="substituted"
        )

        assert correct.post_check_absent and substituted.post_check_absent
        assert correct.post_check_identity == substituted.post_check_identity is None
        assert not correct.detected_substitution
        assert not substituted.detected_substitution
        assert (journal / "A-survives").exists(), "A is still alive, unobserved"
        assert identity  # the pre-check value the counterexample turns on
    finally:
        inventory.close()


def test_the_flag_effect_is_issued_on_the_descriptor_and_not_on_a_name(
    tmp_path,
) -> None:
    """**P4** as B2, over a real `ioctl`, and with the privilege honestly stated.

    Two observations, and neither is skipped:

    1. `FS_IOC_GETFLAGS` **succeeds** through the descriptor the pre-check
       verified, so the request reaches the object the descriptor refers to
       rather than a name resolved again; and
    2. `FS_IOC_SETFLAGS` adding `FS_APPEND_FL` is **refused with EPERM** for
       this unprivileged identity, because `FS_APPEND_FL` and `FS_IMMUTABLE_FL`
       require `CAP_LINUX_IMMUTABLE`. That is the same refusal §2.13.5c's `E4`
       expects, and this test does not seek the capability: an implementation
       pass does not acquire privilege to make an assertion pass.

    So what is established here is the **binding** — that the effect is issued
    on a held descriptor — and not that the flag can be set on the target. The
    positive flag-setting case needs root on the disposable host and is a
    separately authorized observation.
    """
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        effects.create_run_directories()
        (run / "journal" / "journal.log").write_bytes(b"\n")
        effects.record_identity(directory_role="journal", name="journal.log")
        descriptor = effects._open_and_verify("journal", "journal.log")
        try:
            current = _read_inode_flags(descriptor)
            assert isinstance(current, int)
            assert not current & FS_APPEND_FL
        finally:
            os.close(descriptor)
        with pytest.raises(OSError) as failure:
            effects.set_inode_flags(
                directory_role="journal", name="journal.log", add=FS_APPEND_FL
            )
        assert failure.value.errno == errno.EPERM, (
            "the refusal is the want of CAP_LINUX_IMMUTABLE, which is the "
            "documented one; any other errno is a different fact and this "
            "assertion would be citing it as this one."
        )
    finally:
        inventory.close()


def test_a_flag_change_on_a_substituted_name_refuses(tmp_path) -> None:
    """The pre-check refuses before the flag change, so the replacement misses it."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        effects.create_run_directories()
        subject = run / "journal" / "journal.log"
        subject.write_bytes(b"\n")
        effects.record_identity(directory_role="journal", name="journal.log")
        subject.rename(run / "journal" / "moved")
        subject.write_bytes(b"a different object\n")
        with pytest.raises(EffectRefused):
            effects.set_inode_flags(
                directory_role="journal", name="journal.log", add=FS_APPEND_FL
            )
    finally:
        inventory.close()


def test_the_reviewed_payload_is_installed_from_one_held_buffer(tmp_path) -> None:
    """**P2.** The bytes written are the bytes digested, from one buffer."""
    import hashlib

    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        effects.create_run_directories()
        content = b"#!/usr/bin/false\n# the reviewed payload\n"
        digest = hashlib.sha256(content).hexdigest()
        identity = effects.install_case_program(content=content, sha256=digest)
        installed = run / "bin" / "case-program"
        assert installed.read_bytes() == content
        assert installed.stat().st_mode & 0o777 == 0o555
        assert (installed.stat().st_dev, installed.stat().st_ino) == (
            identity.device,
            identity.inode,
        )
        assert not (run / "bin" / ".case-program.tmp").exists()
    finally:
        inventory.close()


def test_p2_creates_its_temporary_0500_and_publishes_0555(tmp_path) -> None:
    """**C-P5.0-LAB-I3-R3, 2026-09-20 — ruling 2, on P2's real install path.**

    `install_case_program` is P2. Its exclusive `openat` is given the ruled
    `0500` creation mode, and that mode is **not** the published one: the
    descriptor `openat` returned is what the payload is written to and what
    `fchmod` applies `CASE_PROGRAM_MODE` to, so the published name is `0555`.
    The default of the creation-mode input it passes remains `0600`, which is
    what T1, T6 and §2.3.3 continue to take.
    """
    import hashlib
    import inspect

    from tools.phase_5_0_evidence.case_runtime import CASE_PROGRAM_TEMPORARY_MODE
    from tools.phase_5_0_evidence.execution.descriptors import (
        EXCLUSIVE_CREATION_MODE,
        PosixFilesystem,
    )

    assert CASE_PROGRAM_TEMPORARY_MODE == "0500"
    assert EXCLUSIVE_CREATION_MODE == 0o600
    signature = inspect.signature(PosixFilesystem.create_file)
    assert signature.parameters["mode"].default == EXCLUSIVE_CREATION_MODE

    inventory, _fs, effects, run = _effects(tmp_path)
    modes: list[int] = []
    real_open = os.open

    def opener(path, flags, mode=0o777, **kwargs):
        if flags & os.O_CREAT and flags & os.O_EXCL and not flags & os.O_DIRECTORY:
            modes.append(mode)
        return real_open(path, flags, mode, **kwargs)

    try:
        effects.create_run_directories()
        content = b"the reviewed payload\n"
        digest = hashlib.sha256(content).hexdigest()
        os.open = opener
        try:
            effects.install_case_program(content=content, sha256=digest)
        finally:
            os.open = real_open
        # P2 made exactly one exclusive file creation, and it was 0500.
        assert modes == [0o500]
        installed = run / "bin" / "case-program"
        assert installed.stat().st_mode & 0o777 == 0o555
        assert installed.read_bytes() == content
        assert not (run / "bin" / ".case-program.tmp").exists()
    finally:
        inventory.close()


def test_a_payload_whose_digest_moved_is_refused_rather_than_installed(
    tmp_path,
) -> None:
    """Content that changed between the manifest and the write is refused."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        effects.create_run_directories()
        with pytest.raises(EffectRefused):
            effects.install_case_program(
                content=b"edited after review\n", sha256="0" * 64
            )
        assert list((run / "bin").iterdir()) == []
    finally:
        inventory.close()


def test_the_payload_is_published_exclusively(tmp_path) -> None:
    """`RENAME_NOREPLACE`'s property, through the documented substitute.

    `link(2)` fails with `EEXIST` when the destination exists, so the final name
    is claimed by the kernel rather than by a check this mechanism performs.
    """
    import hashlib

    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        effects.create_run_directories()
        (run / "bin" / "case-program").write_bytes(b"something already there\n")
        content = b"the reviewed payload\n"
        with pytest.raises(DescriptorRefused) as refusal:
            effects.install_case_program(
                content=content, sha256=hashlib.sha256(content).hexdigest()
            )
        assert refusal.value.classification == DESCRIPTOR_OBJECT_EXISTS
        assert (
            run / "bin" / "case-program"
        ).read_bytes() == b"something already there\n"
    finally:
        inventory.close()


# ---------------------------------------------------------------------------
# r6 §6.2, amendment D1 — the stop between `linkat` and `unlinkat`
# ---------------------------------------------------------------------------


def _stop_between_link_and_unlink(monkeypatch, temporary: str) -> list[str]:
    """Make the exclusive publication's `unlinkat` of `temporary` fail, once.

    `linkat` has already claimed the final name when this fires, so the state
    left behind is D1's own: the published final name, and the temporary beside
    it as a second name for the same inode. A process killed between the two
    calls leaves the same namespace; this reaches it through the real writer
    without killing the test process. Every other unlink is the real one.
    """
    real_unlink = os.unlink
    fired: list[str] = []

    def unlink(path, *args, **kwargs):
        if (
            not fired
            and os.fspath(path) == temporary
            and kwargs.get("dir_fd") is not None
        ):
            fired.append(temporary)
            raise OSError(errno.EIO, "injected: stopped between link and unlink")
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", unlink)
    return fired


def _assert_two_names_for_one_inode(final: Path, temporary: Path) -> None:
    """The second interruption state of r6 §6.2, and nothing else."""
    final_facts = final.stat(follow_symlinks=False)
    temporary_facts = temporary.stat(follow_symlinks=False)
    assert (final_facts.st_dev, final_facts.st_ino) == (
        temporary_facts.st_dev,
        temporary_facts.st_ino,
    )
    assert final_facts.st_nlink == 2


def test_d1_a_first_use_record_stopped_between_link_and_unlink_is_kept_and_refused(
    tmp_path, monkeypatch
) -> None:
    """T1: the record **was** published, and the recovery must not say otherwise.

    The publication does not report success; a second initialization refuses
    rather than cleaning; the reservation record's next publication refuses; and
    the operator recovery distinguishes this state from one in which nothing was
    published.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    temporary_name = f"{lab.layout.record_name}.tmp"
    temporary = lab.record_path.with_name(temporary_name)
    try:
        fired = _stop_between_link_and_unlink(monkeypatch, temporary_name)
        first = _initialize(bound)
        assert fired, "the injected stop was reached"
        assert not first.initialized
        assert first.refusal is FirstUseRefusal.NOT_DURABLE
        _assert_two_names_for_one_inode(lab.record_path, temporary)
        monkeypatch.undo()

        again = _initialize(bound)
        assert again.refusal is FirstUseRefusal.INTERRUPTED_INITIALIZATION
        recovery = " ".join(again.recovery)
        assert "same inode" in recovery
        assert "not repeated" in recovery
        assert "published nothing" not in recovery

        admitted = bound.record.admit_reservation(
            reservation_id="RES-1", author="root", at=AT
        )
        assert not admitted.published
        assert admitted.refusal is PublicationRefusal.INTERRUPTED_PUBLICATION
        _assert_two_names_for_one_inode(lab.record_path, temporary)
    finally:
        bound.close()


def test_d1_a_run_start_stopped_between_link_and_unlink_blocks_every_successor(
    tmp_path, monkeypatch
) -> None:
    """T6: the survey and a retry both refuse, and nothing removes the temporary."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    final = lab.runs_directory / "sync-1"
    temporary = lab.runs_directory / "sync-1.tmp"
    try:
        _initialize(bound)
        fired = _stop_between_link_and_unlink(monkeypatch, temporary.name)
        started = bound.ledger.begin(
            run_id="sync-1",
            participant=Participant.SYNCHRONIZATION,
            author="ubuntu",
            at=AT,
        )
        assert fired, "the injected stop was reached"
        assert not started.published
        _assert_two_names_for_one_inode(final, temporary)
        monkeypatch.undo()

        retry = bound.ledger.begin(
            run_id="sync-1",
            participant=Participant.SYNCHRONIZATION,
            author="ubuntu",
            at=AT,
        )
        assert retry.refusal is PublicationRefusal.INTERRUPTED_PUBLICATION
        assert temporary.name in bound.ledger.survey().unreadable
    finally:
        bound.close()
    for participant in PARTICIPANTS:
        with lab.session(participant) as session:
            assert not session.admit().may_proceed, participant
    _assert_two_names_for_one_inode(final, temporary)


def test_d1_a_capture_stopped_between_link_and_unlink_permits_no_mutation(
    tmp_path, monkeypatch
) -> None:
    """§2.3.3: no M1, and restart discovery reports the basis unusable."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    temporary_name = f"pg_hba.conf{TEMPORARY_SUFFIX}"
    run_directory = lab.recovery_directory / "RUN-1"
    try:
        store = recovery_store(lab, bound)
        fired = _stop_between_link_and_unlink(monkeypatch, temporary_name)
        publication = _publish(store, lab=lab)
        assert fired, "the injected stop was reached"
        assert not publication.published
        assert not publication.mutation_permitted
        assert not publication_permits_mutation(publication)
        _assert_two_names_for_one_inode(
            run_directory / "pg_hba.conf", run_directory / temporary_name
        )
        monkeypatch.undo()

        found = {run.run_id: run for run in store.discover()}
        assert not found["RUN-1"].usable
        assert DISCOVERY_LEFTOVER_TEMPORARY in found["RUN-1"].reasons
        _assert_two_names_for_one_inode(
            run_directory / "pg_hba.conf", run_directory / temporary_name
        )
    finally:
        bound.close()


def test_d1_a_payload_stopped_between_link_and_unlink_is_neither_recorded_nor_removed(
    tmp_path, monkeypatch
) -> None:
    """P2: installation raises, records no identity, and neither name is removable."""
    import hashlib

    inventory, _fs, effects, run = _effects(tmp_path)
    final = run / "bin" / "case-program"
    temporary = run / "bin" / ".case-program.tmp"
    content = b"the reviewed payload\n"
    try:
        effects.create_run_directories()
        fired = _stop_between_link_and_unlink(monkeypatch, temporary.name)
        with pytest.raises(DescriptorRefused):
            effects.install_case_program(
                content=content, sha256=hashlib.sha256(content).hexdigest()
            )
        assert fired, "the injected stop was reached"
        _assert_two_names_for_one_inode(final, temporary)
        assert ("bin", final.name) not in effects._recorded
        assert ("bin", temporary.name) not in effects._recorded
        monkeypatch.undo()

        for name in (temporary.name, final.name):
            with pytest.raises(EffectRefused):
                effects.remove_object(directory_role="bin", name=name)
        with pytest.raises(DescriptorRefused) as retry:
            effects.install_case_program(
                content=content, sha256=hashlib.sha256(content).hexdigest()
            )
        assert retry.value.classification == DESCRIPTOR_OBJECT_EXISTS
        _assert_two_names_for_one_inode(final, temporary)
    finally:
        inventory.close()


# ---------------------------------------------------------------------------
# PR-20260915-LAB-D12-1 — the record's temporary refuses all seven at T4
# ---------------------------------------------------------------------------


OPERATOR = "peter duscha, operations owner"
RECOVERY_REFERENCE = "INC-2026-09-15-D1"
D12_RESERVATION = "RES-D12"


def _interrupted_record(lab, monkeypatch):
    """Reach D1's second interruption state on the **reservation record**.

    The real writer publishes the first-use record and its one `unlinkat`
    fails, so the final name carries the synchronized bytes and the temporary
    beside it is a second name for the same inode. This is row 70's state, and
    every test below reads it rather than arranging one of its own.
    """
    bound = bind(lab)
    temporary = lab.record_path.with_name(f"{lab.layout.record_name}.tmp")
    try:
        fired = _stop_between_link_and_unlink(monkeypatch, temporary.name)
        outcome = _initialize(bound)
        assert fired, "the injected stop was reached"
        assert not outcome.initialized
        monkeypatch.undo()
        _assert_two_names_for_one_inode(lab.record_path, temporary)
    finally:
        bound.close()
    return temporary


def _bytes_of(directory: Path) -> dict:
    """Every name under `directory` and its bytes — the unchanged-state check."""
    return {
        entry.name: entry.read_bytes()
        for entry in sorted(directory.iterdir())
        if entry.is_file()
    }


def _refuse_participant(lab, participant, *, run_id: str):
    """Drive one participant's real integration point and record whether its
    work was ever reached.

    The six go through `run()` and the harness through `run_harness()`, because
    r6 §5.12 derives the harness's two completion conditions rather than taking
    them injected. Both return before the work when admission refuses, and the
    recorder is what proves it.
    """
    called: list = []
    integration = ParticipantIntegration(
        participant=participant,
        host=HOST,
        target_identity=TARGET_IDENTITY,
        author=PARTICIPANT_PROFILES[participant].identity,
        at=AT,
        layout=lab.layout,
        # The harness holds the reservation it concludes and refuses rather than
        # waiting behind a held lock; the six carry the field empty and wait.
        reservation_id=D12_RESERVATION if participant.writes_the_record else "",
        wait_for_lock=not participant.writes_the_record,
    )
    if participant.writes_the_record:

        def harness_work(permit):
            called.append(permit)
            return HarnessObservations(
                residue=ResidueObservation.empty(observed_by=OPERATOR),
                configuration_restored=True,
                child_processes_ended=True,
                database_transactions_settled=True,
            )

        outcome = integration.run_harness(
            run_id=run_id,
            work=harness_work,
            request=ReservationRequest(
                reservation_id=D12_RESERVATION,
                owner=OPERATOR,
                host=HOST,
                target_identity=TARGET_IDENTITY,
                requested_at=AT,
                deadline="2026-09-15T20:00:00Z",
                recovery_owner=OPERATOR,
                real_execution=False,
            ),
            observed_by=OPERATOR,
        ).run
    else:

        def work(permit):
            called.append(permit)
            return {
                condition: True
                for condition in PARTICIPANT_PROFILES[participant].external_conditions()
            }

        outcome = integration.run(
            run_id=run_id, work=work, observed_by=OPERATOR
        )
    return outcome, called


def test_d1_a_record_publication_temporary_refuses_all_seven_before_their_work(
    tmp_path, monkeypatch
) -> None:
    """**PR-20260915-LAB-D12-1**, and it is the finding's own reproduction.

    r6 §9.2 row 74. After T1's `linkat` succeeded and its `unlinkat` failed, the
    final lifecycle record is valid, complete and readable. Codex found that
    `read_and_admit` re-sealed and parsed exactly that record without ever
    asking whether its publication had finished, so the six ordinary
    participants admitted and only the harness refused later, at T7, when it
    tried to publish `admitted` over the leftover temporary.

    Every one of the seven must now refuse at **T4**, through the one
    authoritative admission path, before its work is called — and both names,
    the record's bytes and the ledger must be exactly as they were afterwards.
    """
    lab = build_laboratory(tmp_path)
    temporary = _interrupted_record(lab, monkeypatch)
    before = _bytes_of(lab.laboratory_directory)
    ledger_before = _bytes_of(lab.runs_directory)
    identities_before = {
        path: path.stat(follow_symlinks=False)[:]
        for path in (lab.record_path, temporary)
    }

    for participant in PARTICIPANTS:
        outcome, called = _refuse_participant(
            lab, participant, run_id=f"RUN-{participant.name}"
        )
        assert not outcome.admitted, participant
        assert not outcome.started, participant
        assert not outcome.effects_permitted, participant
        assert not outcome.completed, participant
        assert outcome.refusal == PARTICIPANT_NOT_ADMITTED, participant
        assert called == [], f"{participant} reached its work"

        # The refusal is the admission path's, not a second check bolted beside
        # it: it arrives on the `SuccessorAdmission` this pass produced, and it
        # carries the one `(st_dev, st_ino)` comparison that produced it.
        admission = outcome.admission
        assert admission is not None and not admission.may_proceed, participant
        assert admission.participant is participant
        assert admission.resealed, "the re-seal still precedes the read"
        assert admission.interruption is not None
        assert admission.interruption.present and admission.interruption.same_inode
        assert admission.refusals[0] in outcome.reasons
        joined = " ".join(admission.refusals)
        assert temporary.name in joined
        assert "PR-20260915-LAB-D12-1" in joined
        assert "§6.2" in joined and "D1" in joined

    _assert_two_names_for_one_inode(lab.record_path, temporary)
    assert _bytes_of(lab.laboratory_directory) == before
    assert _bytes_of(lab.runs_directory) == ledger_before
    assert {
        path: path.stat(follow_symlinks=False)[:]
        for path in (lab.record_path, temporary)
    } == identities_before


def test_d1_a_temporary_whose_resolution_is_unknown_is_not_an_absent_one(
    tmp_path, monkeypatch
) -> None:
    """A refusing `fstatat` refuses the participant — the lock's rule, here too.

    r6 §5.9 says an unreadable lock is not an unheld lock. The same holds of the
    publication temporary: if the name's resolution cannot be established, then
    nothing has established that the publication finished, and reading *absent*
    from a call that refused would be the fail-open the whole check exists to
    close.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        assert _initialize(bound).initialized
    finally:
        bound.close()

    real_stat = os.stat
    temporary_name = f"{lab.layout.record_name}.tmp"

    def refusing_stat(path, *args, **kwargs):
        if (
            isinstance(path, str)
            and path == temporary_name
            and kwargs.get("dir_fd") is not None
        ):
            raise OSError(errno.EACCES, "injected: the name cannot be resolved")
        return real_stat(path, *args, **kwargs)

    monkeypatch.setattr(os, "stat", refusing_stat)
    with lab.session(Participant.BOT_SUITE) as session:
        admission = session.admit()
    assert not admission.may_proceed
    assert admission.interruption is not None
    assert admission.interruption.observation_failed
    assert not admission.interruption.present
    joined = " ".join(admission.refusals)
    assert "could not be observed" in joined
    assert "is not an absent name" in joined


def test_d1_a_clean_record_with_no_temporary_still_admits_all_seven_control(
    tmp_path,
) -> None:
    """The successful control for the row above. **It must keep passing.**

    A check that refuses everything refuses correctly by accident. The same
    seven passes, over a record published without interruption, reach their work
    and settle — so the new refusal is the temporary's and not the check's.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        assert _initialize(bound).initialized
    finally:
        bound.close()
    assert not lab.record_path.with_name(f"{lab.layout.record_name}.tmp").exists()

    for participant in PARTICIPANTS:
        outcome, called = _refuse_participant(
            lab, participant, run_id=f"RUN-{participant.name}"
        )
        assert outcome.admitted, participant
        assert outcome.effects_permitted, participant
        assert outcome.completed, participant
        assert len(called) == 1, participant
        assert outcome.admission is not None
        assert outcome.admission.interruption is not None
        assert not outcome.admission.interruption.present


def test_d1_a_temporary_that_is_not_the_record_refuses_and_is_never_removed(
    tmp_path,
) -> None:
    """A leftover temporary whose inode differs from the record — and it stays.

    This is the third of r6 §6.2's dispositions: neither *"nothing was
    published"* nor *"published between the two calls"*, so no recovery in the
    contract applies to it. Every participant refuses, the refusal says the two
    names are different objects, and **nothing removes it**: the automatic
    cleanup of an object nobody has identified is the behaviour §2.13.2b's
    precedent exists to forbid.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        assert _initialize(bound).initialized
    finally:
        bound.close()
    temporary = lab.record_path.with_name(f"{lab.layout.record_name}.tmp")
    temporary.write_bytes(b"an object of unestablished provenance\n")
    record_before = lab.record_path.read_bytes()
    temporary_before = temporary.read_bytes()
    assert (
        temporary.stat(follow_symlinks=False).st_ino
        != lab.record_path.stat(follow_symlinks=False).st_ino
    )

    for participant in PARTICIPANTS:
        outcome, called = _refuse_participant(
            lab, participant, run_id=f"RUN-{participant.name}"
        )
        assert not outcome.admitted and called == [], participant
        joined = " ".join(outcome.admission.refusals)
        assert "different objects" in joined
        assert not outcome.admission.interruption.same_inode

    assert temporary.exists() and temporary.read_bytes() == temporary_before
    assert lab.record_path.read_bytes() == record_before


# ---------------------------------------------------------------------------
# r6 §6.2 — T1's and T6's operator recovery, with the comparison made mandatory
# ---------------------------------------------------------------------------


def test_d1_the_t1_recovery_removes_the_temporary_only_on_an_identity_match(
    tmp_path, monkeypatch
) -> None:
    """The **identity-match** case: the comparison holds, so one name goes.

    r6 §6.2's T1 recovery is *remove only the temporary; do not repeat the
    initialization*. The record survives byte for byte, the publication is not
    repeated, and the seven admit again afterwards — which is what makes this a
    bounded recovery rather than a dead end.
    """
    lab = build_laboratory(tmp_path)
    temporary = _interrupted_record(lab, monkeypatch)
    record_before = lab.record_path.read_bytes()
    bound = bind(lab)
    try:
        comparison = bound.record.observe_publication_temporary()
        assert comparison.present and comparison.same_inode
        removal = bound.record.remove_publication_temporary(
            comparison=comparison, author=OPERATOR, reference=RECOVERY_REFERENCE
        )
    finally:
        bound.close()

    assert removal.removed and removal.refusal is None
    assert removal.presented is comparison
    assert removal.confirmed is not None and removal.confirmed.same_inode
    assert removal.after is not None and not removal.after.present
    assert OPERATOR in " ".join(removal.reasons)
    assert RECOVERY_REFERENCE in " ".join(removal.reasons)

    assert not temporary.exists()
    assert lab.record_path.read_bytes() == record_before
    assert lab.record_path.stat(follow_symlinks=False).st_nlink == 1
    for participant in PARTICIPANTS:
        with lab.session(participant) as session:
            assert session.admit().may_proceed, participant


def test_d1_the_t1_recovery_refuses_a_mismatch_and_removes_nothing(
    tmp_path,
) -> None:
    """The **mismatch** case: two names, two inodes, and neither is touched."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        assert _initialize(bound).initialized
        temporary = lab.record_path.with_name(f"{lab.layout.record_name}.tmp")
        temporary.write_bytes(b"an object of unestablished provenance\n")
        comparison = bound.record.observe_publication_temporary()
        assert comparison.present and not comparison.same_inode
        removal = bound.record.remove_publication_temporary(
            comparison=comparison, author=OPERATOR, reference=RECOVERY_REFERENCE
        )
    finally:
        bound.close()

    assert not removal.removed
    assert removal.refusal is TemporaryRemovalRefusal.IDENTITY_MISMATCH
    assert removal.after is None
    assert temporary.exists()
    assert lab.record_path.exists()


def test_d1_the_t1_recovery_refuses_an_unobserved_comparison(
    tmp_path, monkeypatch
) -> None:
    """The **unobserved** case, and it is the one the prose could not enforce.

    `comparison=None` is a removal taken without ever comparing the two names.
    It refuses before `unlinkat`, so a caller that skipped r6 §6.2's comparison
    does not remove anything — the requirement is mechanical rather than a step
    an operator is asked to remember.
    """
    lab = build_laboratory(tmp_path)
    temporary = _interrupted_record(lab, monkeypatch)
    bound = bind(lab)
    try:
        removal = bound.record.remove_publication_temporary(
            comparison=None, author=OPERATOR, reference=RECOVERY_REFERENCE
        )
        assert not removal.removed
        assert removal.refusal is TemporaryRemovalRefusal.NO_OBSERVED_COMPARISON
        assert removal.presented is None and removal.after is None

        # A comparison of some **other** record's two names is not a comparison
        # of these, however true it is of its own.
        other = DurableRecordStore(
            bound.filesystem,
            directory=bound.record.directory_object_id,
            name="another-record.json",
            label="another-record.json",
        )
        foreign = bound.record.remove_publication_temporary(
            comparison=other.observe_publication_temporary(),
            author=OPERATOR,
            reference=RECOVERY_REFERENCE,
        )
        assert not foreign.removed
        assert foreign.refusal is TemporaryRemovalRefusal.FOREIGN_COMPARISON

        # And an attributed recovery names who performed it.
        unattributed = bound.record.remove_publication_temporary(
            comparison=bound.record.observe_publication_temporary(),
            author="",
            reference=RECOVERY_REFERENCE,
        )
        assert not unattributed.removed
        assert unattributed.refusal is TemporaryRemovalRefusal.UNATTRIBUTED
    finally:
        bound.close()
    _assert_two_names_for_one_inode(lab.record_path, temporary)


def test_d1_the_t1_recovery_refuses_a_comparison_that_no_longer_holds(
    tmp_path, monkeypatch
) -> None:
    """*Immediately preceding* is a claim about the moment of the call.

    The comparison is taken, the state changes underneath it — here another
    operator completed the same recovery — and the stale comparison is refused
    rather than removing whatever now answers to the name.
    """
    lab = build_laboratory(tmp_path)
    temporary = _interrupted_record(lab, monkeypatch)
    bound = bind(lab)
    try:
        comparison = bound.record.observe_publication_temporary()
        assert comparison.same_inode
        temporary.unlink()
        replacement = b"a different object at the same name\n"
        temporary.write_bytes(replacement)
        removal = bound.record.remove_publication_temporary(
            comparison=comparison, author=OPERATOR, reference=RECOVERY_REFERENCE
        )
    finally:
        bound.close()

    assert not removal.removed
    assert removal.refusal is TemporaryRemovalRefusal.STALE_COMPARISON
    assert removal.confirmed is not None and not removal.confirmed.same_inode
    assert temporary.exists() and temporary.read_bytes() == replacement


def test_d1_the_t6_recovery_uses_the_same_guard_and_settles_nothing(
    tmp_path, monkeypatch
) -> None:
    """T6's run file, on **one** implementation of the guard — and it settles nothing.

    Removing the temporary makes the run visible as started and unsettled. It
    still blocks every successor, because only T16's attributed
    `participant_recovered` settles a run, and the removal of a temporary is not
    that entry.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    final = lab.runs_directory / "sync-1"
    temporary = lab.runs_directory / "sync-1.tmp"
    try:
        _initialize(bound)
        fired = _stop_between_link_and_unlink(monkeypatch, temporary.name)
        bound.ledger.begin(
            run_id="sync-1",
            participant=Participant.SYNCHRONIZATION,
            author="ubuntu",
            at=AT,
        )
        assert fired, "the injected stop was reached"
        monkeypatch.undo()
        _assert_two_names_for_one_inode(final, temporary)

        assert not bound.ledger.remove_publication_temporary(
            "sync-1", comparison=None, author=OPERATOR, reference=RECOVERY_REFERENCE
        ).removed
        _assert_two_names_for_one_inode(final, temporary)

        removal = bound.ledger.remove_publication_temporary(
            "sync-1",
            comparison=bound.ledger.observe_publication_temporary("sync-1"),
            author=OPERATOR,
            reference=RECOVERY_REFERENCE,
        )
        assert removal.removed
        assert not temporary.exists() and final.exists()

        survey = bound.ledger.survey()
        assert survey.unreadable == ()
        assert "sync-1" in survey.unsettled
    finally:
        bound.close()
    for participant in PARTICIPANTS:
        with lab.session(participant) as session:
            assert not session.admit().may_proceed, participant


# ---------------------------------------------------------------------------
# Structural guards — what this suite may not reach
# ---------------------------------------------------------------------------


#: The remediation's two modules are held to the same guards — C-P5.0-LAB-I-R1.
REMEDIATION_FILE = THIS_FILE.parent / "test_lab_remediation.py"
INTEGRATION_FILE = THIS_FILE.parent / "test_lab_integration.py"

LAB_SOURCES = (THIS_FILE, FIXTURE_FILE, REMEDIATION_FILE, INTEGRATION_FILE)

#: The three roots C-P5.0-LAB-I forbids creating any object under.
FORBIDDEN_ROOTS = ("/run/", "/var/lib/", "/etc/")

#: **The suite-wide guards these two files are already held to.**
#: `test_no_execution.test_no_test_in_this_suite_needs_root_or_a_database`
#: scans every `.py` in this directory, these two included, and refuses the
#: process-starting module, the database URL environment variable, the database
#: marker and every read of the process environment. That scan names those four
#: and excludes itself from its own text search, which is why this comment
#: describes them rather than spelling them.
#:
#: Since no test in this suite can start a process at all, no test here can
#: invoke a remote shell, a tree synchronization, an account or group creation,
#: a tmpfiles run or a database client — each of those is a process, and there
#: is no way to reach one.
#:
#: What that leaves for this file to establish is the part a no-process
#: property does not cover: that these two files construct **no armed real
#: writer** and pass **no execution flag** to anything. The two scans below do
#: it at the level of call sites rather than of raw text, so the check cannot be
#: defeated by a name that only looks like prose, and so this file can name what
#: it refuses without tripping its own scan.
#: Written as plain tuples rather than `frozenset({…})` calls, because the scan
#: below walks call nodes and a `frozenset(…)` construction would be a call
#: carrying every one of these literals — the guard would then fail on itself.
FORBIDDEN_CALLEES = (
    "SubprocessBoundary",
    "SystemMaterializer",
    "Popen",
    "system",
    "connect",
    "execv",
    "execve",
)

#: Strings no call in these two files may receive as an argument. `--execute` is
#: the execution flag; the rest would each be a command reaching the host.
FORBIDDEN_CALL_ARGUMENTS = (
    "--execute",
    "/usr/bin/rsync",
    "/usr/sbin/useradd",
    "/usr/sbin/groupadd",
    "/usr/bin/systemd-tmpfiles",
    "/usr/bin/psql",
    "/usr/bin/ssh",
)


def _string_arguments(call: ast.Call):
    """Every string literal this call receives, including inside a list/tuple."""
    for node in ast.walk(call):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.value


@pytest.mark.parametrize("path", LAB_SOURCES, ids=[p.name for p in LAB_SOURCES])
def test_the_laboratory_suite_arms_no_real_writer_and_executes_nothing(
    path: Path,
) -> None:
    """No call site here constructs an armed real writer or passes an execution
    flag.

    Asserted over the syntax tree rather than over the text, so a name that
    appears only in prose is not a finding and a name that appears in a call is.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        name = (
            function.id
            if isinstance(function, ast.Name)
            else function.attr
            if isinstance(function, ast.Attribute)
            else ""
        )
        if name in FORBIDDEN_CALLEES:
            pytest.fail(f"{path.name}:{node.lineno} calls {name!r}")
        for argument in _string_arguments(node):
            assert argument not in FORBIDDEN_CALL_ARGUMENTS, (
                f"{path.name}:{node.lineno} passes {argument!r}"
            )


@pytest.mark.parametrize("path", LAB_SOURCES, ids=[p.name for p in LAB_SOURCES])
def test_the_laboratory_suite_creates_nothing_outside_the_temporary_tree(
    path: Path,
) -> None:
    """No path this suite **opens** is under `/run`, `/var/lib` or `/etc`.

    C-P5.0-LAB-I forbids creating any object under those roots. The check is
    structural rather than behavioural so that a future edit which reached for a
    production constant fails here rather than on the host, and it reads every
    string literal that is not an assertion's expected value: the three
    production paths appear in this file exactly once each, inside
    `test_the_production_layout_is_data_and_no_test_builds_over_it`, which
    asserts they do **not** exist.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    exempt = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_the_production_layout_is_data_and_no_test_builds_over_it"
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in exempt:
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            for root in FORBIDDEN_ROOTS:
                # `len(value) > len(root)` skips the root strings this guard
                # names itself. A path that reaches an object is longer than the
                # root it is under.
                if value.startswith(root) and len(value) > len(root):
                    pytest.fail(f"{path.name} names {value!r}")


def test_the_production_layout_is_data_and_no_test_builds_over_it() -> None:
    """The production paths exist as definitions and are never opened here.

    The three roots C-P5.0-LAB-I forbids creating under are asserted **absent**,
    so a run that provisioned one by mistake fails here. They are unapproved
    items V3, V4 and V5.
    """
    from tools.phase_5_0_evidence.provisioning import LABORATORY_LAYOUT

    for path in (
        Path(LABORATORY_LAYOUT.lock_path),
        Path(LABORATORY_LAYOUT.laboratory_directory),
        Path(LABORATORY_LAYOUT.recovery_directory),
    ):
        assert not path.exists(), (
            f"{path} is an unapproved, unprovisioned r6 §7 item. Finding it "
            "here would mean something created it, which this authorization "
            "does not permit."
        )


def test_the_module_under_test_names_its_two_amendments() -> None:
    """D1 and D2 are stated where a reader of the mechanism will see them.

    Both began as reported deviations and are now r6 amendments, so the listing
    descriptor is no longer an open contract gap.
    """
    joined = " ".join(descriptors_module.EXCLUSIVE_PUBLICATION_SUBSTITUTE)
    assert "RENAME_NOREPLACE" in joined and "linkat" in joined and "D1" in joined
    assert "already published" in joined
    listing = " ".join(descriptors_module.LISTING_DESCRIPTOR)
    assert "readdir" in listing and "D20" in listing
    assert descriptors_module.CONTRACT_GAPS == ()


def test_the_unimplemented_execveat_route_has_an_owner_and_a_stop_condition() -> None:
    """r6 §6.4's open item, stated with the three things an open item needs.

    Codex's disposition of 2026-09-15 is that the unresolved `execveat` route
    *"needs an explicit owner and execution stop condition before execution
    readiness"*. **No route is chosen here**: C-P5.0-LAB-D12-R1 forbids choosing
    or implementing one, so what this asserts is that the item is owned, that
    what would close it is written down, and that execution is stopped while it
    is open — not that anything was decided.
    """
    route = descriptors_module.UNIMPLEMENTED_EXECUTION_ROUTE
    joined = " ".join(route)
    assert "execveat" in joined and "X1" in joined
    assert "unimplemented and no route is chosen" in joined
    assert any(statement.startswith("Owner:") for statement in route)
    assert "Technical Lead" in joined
    assert any(statement.startswith("Required evidence") for statement in route)
    assert "I7" in joined and "ctypes" in joined
    assert "Execution stop condition:" in joined
    assert "`plan.is_executable` stays False" in joined
    assert "reservation.REAL_EXECUTION_REFUSAL" in joined
    # And the stop condition names two states that actually hold right now.
    from tools.phase_5_0_evidence.reservation import REAL_EXECUTION_REFUSAL

    from tools.phase_5_0_evidence.concrete_plan import build_concrete_plan

    assert REAL_EXECUTION_REFUSAL
    assert not build_concrete_plan().is_executable


def test_serialized_history_is_what_reaches_the_disk(tmp_path) -> None:
    """The bytes on disk are the codec's bytes, not a re-rendering of them."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        _initialize(bound)
        parsed = bound.record.read()
        assert lab.record_path.read_bytes() == serialize_history(parsed.entries)
    finally:
        bound.close()


def test_the_temporary_suffix_is_the_one_the_store_reports(tmp_path) -> None:
    """One spelling of the temporary, so a survey and a writer cannot disagree."""
    assert TEMPORARY_SUFFIX == ".tmp"
    assert RECORD_SUFFIX == ".record"
    assert DESCRIPTOR_BARRIER_FAILED in DESCRIPTOR_REFUSALS
    assert DESCRIPTOR_NOT_BOUND in DESCRIPTOR_REFUSALS
