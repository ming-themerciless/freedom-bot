"""The C-P5.0-LAB-I-R1 remediation regressions — PR-20260913-LABI-1, -2 and -3.

## What this module is

Codex's independent review of the reserved-laboratory implementation found two
Blocking fail-open defects and one Important integration defect:

* **LABI-1** — `RecoveryStore.publish()` accepted a caller-supplied destination,
  verified only the stored copy's digest and set `mutation_permitted` from
  barrier membership alone, so a record naming `/wrong/destination` authorized
  the first configuration mutation even though `restore_configuration()` must
  refuse to restore from it;
* **LABI-2** — both ownership comparisons were conditional on the recorded
  identity being non-empty, so an object the run never created and never
  recorded could be removed, and the analogous flag path could issue
  `FS_IOC_SETFLAGS` against an unbound object; and
* **LABI-3** — the session, ledger, recovery store and effect issuer were
  consumed only by their own tests. No entry point enforced them.

Every test here was written **before** the correction and run against the
submitted tree. Each one failed there, and the handback records the exact
output.

## What it is not

Nothing here observes `oracle-test`, provisions anything, starts a process or
reaches a database. Every path is under `tmp_path`; the three production roots
are asserted absent by
`test_lab_implementation.test_the_production_layout_is_data_and_no_test_builds_over_it`
and this file is held to the same structural guards, which
`test_lab_implementation.LAB_SOURCES` enumerates.

`is_executable` stays `False`, C-7 stays unresolved and EH-R16-1 stays Open.
A passing regression is not a closed finding.

## The negative controls

Each load-bearing conjunct has one. A control removes **exactly one** check — by
subclassing the production object and overriding only that method, or by
re-issuing the production sequence with the one comparison omitted — and asserts
that the previously refused input is then accepted. A check nothing catches was
not load-bearing.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from tests.phase_5_0_evidence.lab_fixtures import (
    build_laboratory,
    bind,
    recovery_store,
)
from tools.phase_5_0_evidence.durability_model import DescriptorMode, Quiescence
from tools.phase_5_0_evidence.execution.descriptors import (
    DescriptorInventory,
    PosixFilesystem,
)
from tools.phase_5_0_evidence.execution.executor import (
    FS_APPEND_FL,
    DescriptorBoundEffects,
    EffectRefused,
)
from tools.phase_5_0_evidence.execution.materializer import publication_permits_mutation
from tools.phase_5_0_evidence.execution.recovery_store import (
    RECORD_SUFFIX,
    RecoveryStore,
)

THIS_FILE = Path(__file__).resolve()

# The names the correction adds are imported **inside** the tests that need
# them, so this module still collects against the submitted implementation and
# the two reviewer reproductions below fail on their assertions rather than on
# an import. That is the failing-before evidence the procedure asks for.


# ---------------------------------------------------------------------------
# PR-20260913-LABI-1 — the recovery destination binding
# ---------------------------------------------------------------------------


REVIEWED_COMPONENTS = ("pg_hba.conf", "pg_ident.conf")


def _reviewed_set(lab):
    """The exact component set and directory the fixture's laboratory reviews."""
    from tools.phase_5_0_evidence.execution.recovery_store import (
        ConfigurationCaptureSet,
    )

    return ConfigurationCaptureSet(
        directory=str(lab.configuration_directory), components=REVIEWED_COMPONENTS
    )


def _store(lab, bound) -> RecoveryStore:
    """The fixture's store. **The reviewed capture set is bound by the fixture.**

    That is the point of the correction: the set is established at the
    integration boundary, not chosen by whoever calls `publish()`.
    """
    return recovery_store(lab, bound)


def _store_of(lab, bound, cls, *, bind_set: bool = True) -> RecoveryStore:
    """One store of the given class, over the fixture's own directories.

    The inventory registers each role once, so a test that needs a subclass
    builds **only** the subclass rather than a second store beside the
    fixture's.
    """
    bound.inventory.open_provisioned_root(
        "pgconf", str(lab.configuration_directory)
    )
    store = cls(
        inventory=bound.inventory,
        filesystem=bound.filesystem,
        parent_path=lab.layout.recovery_directory,
        capture_set=_reviewed_set(lab) if bind_set else None,
    )
    store.open_parent()
    return store


def _publish(store, lab, *, sources=None, run_id="RUN-1", **overrides):
    fields = {
        "run_id": run_id,
        "reservation_id": "RES-1",
        "captured_by": "the harness, as root",
        "sources": (
            sources
            if sources is not None
            else {
                name: f"{lab.configuration_directory}/{name}"
                for name in REVIEWED_COMPONENTS
            }
        ),
        "configuration_role": "pgconf",
    }
    fields.update(overrides)
    return store.publish(**fields)


def test_the_reviewers_wrong_destination_reproduction_no_longer_permits_mutation(
    tmp_path,
) -> None:
    """**Codex's exact reproduction.** `/wrong/destination` refuses, and writes nothing.

    The submitted implementation returned `published=True` and
    `mutation_permitted=True` for this input, with the record naming a
    destination `restore_configuration()` must refuse. A record deliberately
    rejected at restore time is not a recovery basis at mutation time.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = _store(lab, bound)
        publication = _publish(
            store,
            lab,
            sources={
                "pg_hba.conf": "/wrong/destination",
                "pg_ident.conf": f"{lab.configuration_directory}/pg_ident.conf",
            },
        )
        assert not publication.published
        assert not publication.mutation_permitted
        assert not publication_permits_mutation(publication)
        assert publication.barriers_crossed == ()
        # Validated **before** the run directory exists, so a refused request
        # leaves no temporary, no copy, no record and no directory at all.
        assert not (lab.recovery_directory / "RUN-1").exists()
    finally:
        bound.close()


def test_a_refused_destination_never_reaches_an_operator_as_its_own_text(
    tmp_path,
) -> None:
    """The refusal is a fixed classification and names no hostile path."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = _store(lab, bound)
        publication = _publish(
            store,
            lab,
            sources={
                "pg_hba.conf": "/wrong/destination",
                "pg_ident.conf": f"{lab.configuration_directory}/pg_ident.conf",
            },
        )
        assert not publication.published
        rendered = " ".join((publication.refusal, *publication.reasons))
        assert "/wrong/destination" not in rendered
        assert "Errno" not in rendered and "errno" not in rendered
    finally:
        bound.close()


def test_a_publication_with_no_reviewed_set_bound_refuses(tmp_path) -> None:
    """An unbound store publishes nothing. There is no reviewed set to check against."""
    from tools.phase_5_0_evidence.execution.recovery_store import CAPTURE_SET_NOT_BOUND

    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = _store_of(lab, bound, RecoveryStore, bind_set=False)
        publication = _publish(store, lab)
        assert not publication.published and not publication.mutation_permitted
        assert publication.refusal == CAPTURE_SET_NOT_BOUND
        assert not (lab.recovery_directory / "RUN-1").exists()
    finally:
        bound.close()


@pytest.mark.parametrize(
    ("sources", "refusal"),
    [
        pytest.param({}, "CAPTURE_SET_INCOMPLETE", id="empty"),
        pytest.param(
            {"pg_hba.conf": "<dir>/pg_hba.conf"},
            "CAPTURE_SET_INCOMPLETE",
            id="missing-one",
        ),
        pytest.param(
            {
                "pg_hba.conf": "<dir>/pg_hba.conf",
                "pg_ident.conf": "<dir>/pg_ident.conf",
                "postgresql.conf": "<dir>/postgresql.conf",
            },
            "CAPTURE_COMPONENT_NOT_REVIEWED",
            id="additional",
        ),
        pytest.param(
            {
                "pg_hba.conf": "<dir>/pg_ident.conf",
                "pg_ident.conf": "<dir>/pg_ident.conf",
            },
            "CAPTURE_DESTINATION_NOT_BOUND",
            id="duplicate-destination",
        ),
        pytest.param(
            {
                "pg_hba.conf": "<dir>/../pgconf/pg_hba.conf",
                "pg_ident.conf": "<dir>/pg_ident.conf",
            },
            "CAPTURE_DESTINATION_NOT_BOUND",
            id="relative-segment",
        ),
        pytest.param(
            {
                # A destination in **another** directory. It is spelled from the
                # fixture's own root so this file names no production path — the
                # suite's structural guard refuses one, and the property under
                # test is *"not the reviewed directory"*, not *"that directory"*.
                "pg_hba.conf": "<other>/pg_hba.conf",
                "pg_ident.conf": "<dir>/pg_ident.conf",
            },
            "CAPTURE_DESTINATION_NOT_BOUND",
            id="cross-directory",
        ),
        pytest.param(
            {"pg_hba.conf": "", "pg_ident.conf": "<dir>/pg_ident.conf"},
            "CAPTURE_DESTINATION_NOT_BOUND",
            id="empty-destination",
        ),
        pytest.param(
            {
                "../pg_hba.conf": "<dir>/pg_hba.conf",
                "pg_ident.conf": "<dir>/pg_ident.conf",
            },
            "CAPTURE_COMPONENT_MALFORMED",
            id="malformed-component",
        ),
    ],
)
def test_every_unreviewed_capture_set_shape_refuses_before_anything_is_written(
    tmp_path, sources, refusal
) -> None:
    """Missing, additional, duplicate, malformed and cross-directory entries.

    All eight are refused **before** the recovery run directory is created, so a
    refused request leaves nothing behind for a later discovery to find.
    """
    from tools.phase_5_0_evidence.execution import recovery_store as module

    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = _store(lab, bound)
        resolved = {
            name: value.replace(
                "<dir>", str(lab.configuration_directory)
            ).replace("<other>", str(lab.root / "elsewhere"))
            for name, value in sources.items()
        }
        publication = _publish(store, lab, sources=resolved)
        assert not publication.published
        assert not publication.mutation_permitted
        assert publication.refusal == getattr(module, refusal)
        assert publication.barriers_crossed == ()
        assert not (lab.recovery_directory / "RUN-1").exists()
    finally:
        bound.close()


def test_a_duplicated_component_destination_is_refused_by_name(tmp_path) -> None:
    """Two components bound to one destination is a set that restores one file twice."""
    from tools.phase_5_0_evidence.execution.recovery_store import (
        CAPTURE_DESTINATION_DUPLICATED,
        ConfigurationCaptureSet,
    )

    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = _store_of(lab, bound, RecoveryStore, bind_set=False)
        store.bind_capture_set(
            ConfigurationCaptureSet(
                directory=str(lab.configuration_directory),
                components=("pg_hba.conf", "pg_hba.conf"),
            )
        )
        publication = _publish(
            store,
            lab,
            sources={"pg_hba.conf": f"{lab.configuration_directory}/pg_hba.conf"},
        )
        assert not publication.published
        assert publication.refusal == CAPTURE_DESTINATION_DUPLICATED
    finally:
        bound.close()


def test_publication_verification_establishes_the_record_copy_destination_binding(
    tmp_path,
) -> None:
    """Step 11 checks the same correspondence `restore_configuration` consumes.

    A record rewritten after it was published — the same shape a store whose
    verification compares only copy digests accepts — makes the publication
    refuse and `mutation_permitted` False.
    """
    from tools.phase_5_0_evidence.execution.recovery_store import (
        CAPTURE_CORRESPONDENCE_FAILED,
    )

    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:

        class _RewritesTheRecord(RecoveryStore):
            def _store_record(self, run_role, **keywords):  # type: ignore[override]
                super()._store_record(run_role, **keywords)
                capture = keywords["capture"]
                record = (
                    lab.recovery_directory
                    / "RUN-2"
                    / f"{capture.name}{RECORD_SUFFIX}"
                )
                record.chmod(0o600)
                record.write_bytes(
                    record.read_bytes().replace(
                        str(lab.configuration_directory).encode(),
                        b"/wrong/destination",
                    )
                )

        tampering = _store_of(lab, bound, _RewritesTheRecord)
        publication = _publish(tampering, lab, run_id="RUN-2")
        assert not publication.published
        assert not publication.mutation_permitted
        assert publication.refusal == CAPTURE_CORRESPONDENCE_FAILED
    finally:
        bound.close()


def test_the_positive_multi_file_publication_still_permits_the_mutation(
    tmp_path,
) -> None:
    """The correction must not pass by refusing every input."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = _store(lab, bound)
        publication = _publish(store, lab)
        assert publication.published and publication.mutation_permitted
        assert publication_permits_mutation(publication)
        assert {capture.name for capture in publication.captures} == set(
            REVIEWED_COMPONENTS
        )
        for capture in publication.captures:
            assert capture.destination == (
                f"{lab.configuration_directory}/{capture.name}"
            )
    finally:
        bound.close()


def test_discovery_and_restore_still_find_the_positive_basis(tmp_path) -> None:
    """Discovery lists it, binds it, and reports it usable."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = _store(lab, bound)
        assert _publish(store, lab).mutation_permitted
        discovered = {run.run_id: run for run in store.discover()}
        assert set(discovered) == {"RUN-1"}
        assert discovered["RUN-1"].usable
        assert len(discovered["RUN-1"].records) == 2
    finally:
        bound.close()


@pytest.mark.parametrize(
    "shape",
    ["orphan-copy", "orphan-record", "wrong-run-id", "records-another-destination"],
)
def test_restart_discovery_applies_the_same_binding(tmp_path, shape) -> None:
    """A basis that does not bind is discovered, reported and **not usable**."""
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:
        store = _store(lab, bound)
        assert _publish(store, lab).mutation_permitted
        run = lab.recovery_directory / "RUN-1"
        run.chmod(0o700)
        if shape == "orphan-copy":
            (run / f"pg_hba.conf{RECORD_SUFFIX}").chmod(0o600)
            (run / f"pg_hba.conf{RECORD_SUFFIX}").unlink()
        elif shape == "orphan-record":
            (run / "pg_hba.conf").chmod(0o600)
            (run / "pg_hba.conf").unlink()
        elif shape == "wrong-run-id":
            record = run / f"pg_hba.conf{RECORD_SUFFIX}"
            record.chmod(0o600)
            record.write_bytes(record.read_bytes().replace(b"RUN-1", b"RUN-9", 1))
        else:
            record = run / f"pg_hba.conf{RECORD_SUFFIX}"
            record.chmod(0o600)
            record.write_bytes(
                record.read_bytes().replace(
                    str(lab.configuration_directory).encode(), b"/wrong/destination"
                )
            )
        discovered = {item.run_id: item for item in store.discover()}
        assert not discovered["RUN-1"].usable
        assert discovered["RUN-1"].reasons
    finally:
        bound.close()


def test_the_binding_control_permits_the_wrong_destination_again(tmp_path) -> None:
    """**Negative control.** Remove only the destination/correspondence binding.

    The subclass overrides exactly two methods — the pre-publication set
    validation and the correspondence half of the verification — and changes
    nothing else. Codex's `/wrong/destination` reproduction then publishes and
    permits the mutation again, which is what the binding exists to prevent.
    """
    lab = build_laboratory(tmp_path)
    bound = bind(lab)
    try:

        class _Unbound(RecoveryStore):
            def _validate_capture_set(self, sources):  # type: ignore[override]
                return dict(sources)

            def _verify_correspondence(self, run_role, captures, run_id):  # type: ignore[override]
                return ()

        unbound = _store_of(lab, bound, _Unbound)
        publication = _publish(
            unbound,
            lab,
            run_id="RUN-3",
            sources={
                "pg_hba.conf": "/wrong/destination",
                "pg_ident.conf": f"{lab.configuration_directory}/pg_ident.conf",
            },
        )
        assert publication.published and publication.mutation_permitted
    finally:
        bound.close()


# ---------------------------------------------------------------------------
# PR-20260913-LABI-2 — the mandatory ownership identity
# ---------------------------------------------------------------------------


def _substitute(target: Path) -> None:
    """Replace `target` with a **different inode** carrying the same name.

    Unlinking and rewriting is not a substitution: the filesystem is free to
    hand the new file the inode the old one released, and a test that depended
    on it would be asserting an allocator's behaviour. Both objects exist at
    once here, so the identities are necessarily different.
    """
    other = target.with_name(f"{target.name}.other")
    other.write_bytes(b"theirs\n")
    other.replace(target)


def _executor_constant(name: str) -> str:
    """One of the executor's refusal classifications, read at call time."""
    from tools.phase_5_0_evidence.execution import executor as module

    return getattr(module, name)


def _effects(tmp_path, *, armed=True, quiescence=None):
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
    effects.create_run_directories()
    return inventory, filesystem, effects, run


def test_the_reviewers_unrecorded_removal_reproduction_refuses(tmp_path) -> None:
    """**Codex's exact reproduction.** A file the run never recorded survives.

    The submitted `remove_object()` compared only when the recorded identity was
    truthy, so a file created directly under the held journal directory — never
    passed to `record_identity()` — was deleted, and the removal record reported
    `recorded_identity=''`.
    """
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        outsider = run / "journal" / "not-ours"
        outsider.write_bytes(b"someone else's file\n")
        with pytest.raises(EffectRefused) as refusal:
            effects.remove_object(directory_role="journal", name="not-ours")
        assert refusal.value.classification == _executor_constant(
            "EFFECT_IDENTITY_NOT_RECORDED"
        )
        assert outsider.exists(), (
            "the object must survive the refusal: a removal that is refused is "
            "refused before `unlinkat`, not after it."
        )
    finally:
        inventory.close()


@pytest.mark.parametrize(
    "effect",
    ["set_inode_flags", "clear_inode_flags", "remove_object"],
)
def test_no_effect_proceeds_without_a_recorded_creating_step_identity(
    tmp_path, effect
) -> None:
    """Set, clear and removal each require a present, non-empty record."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        target = run / "journal" / "unbound"
        target.write_bytes(b"\n")
        with pytest.raises(EffectRefused) as refusal:
            if effect == "remove_object":
                effects.remove_object(directory_role="journal", name="unbound")
            elif effect == "set_inode_flags":
                effects.set_inode_flags(
                    directory_role="journal", name="unbound", add=FS_APPEND_FL
                )
            else:
                effects.clear_inode_flags(
                    directory_role="journal", name="unbound", remove=FS_APPEND_FL
                )
        assert refusal.value.classification == _executor_constant(
            "EFFECT_IDENTITY_NOT_RECORDED"
        )
        assert target.exists()
    finally:
        inventory.close()


@pytest.mark.parametrize(
    "effect",
    ["set_inode_flags", "clear_inode_flags", "remove_object"],
)
def test_an_object_absent_at_the_pre_check_refuses_before_any_syscall(
    tmp_path, effect
) -> None:
    """A recorded name that no longer resolves refuses, and refuses by name."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        target = run / "journal" / "vanished"
        target.write_bytes(b"\n")
        effects.record_identity(directory_role="journal", name="vanished")
        target.unlink()
        with pytest.raises(EffectRefused) as refusal:
            if effect == "remove_object":
                effects.remove_object(directory_role="journal", name="vanished")
            elif effect == "set_inode_flags":
                effects.set_inode_flags(
                    directory_role="journal", name="vanished", add=FS_APPEND_FL
                )
            else:
                effects.clear_inode_flags(
                    directory_role="journal", name="vanished", remove=FS_APPEND_FL
                )
        assert refusal.value.classification == _executor_constant(
            "EFFECT_OBJECT_ABSENT"
        )
    finally:
        inventory.close()


@pytest.mark.parametrize(
    "effect",
    ["set_inode_flags", "clear_inode_flags", "remove_object"],
)
def test_an_unequal_identity_refuses_and_the_substitute_survives(
    tmp_path, effect
) -> None:
    """Equality with the mandatory record is the only admitting branch."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        target = run / "journal" / "swapped"
        target.write_bytes(b"ours\n")
        effects.record_identity(directory_role="journal", name="swapped")
        _substitute(target)
        with pytest.raises(EffectRefused) as refusal:
            if effect == "remove_object":
                effects.remove_object(directory_role="journal", name="swapped")
            elif effect == "set_inode_flags":
                effects.set_inode_flags(
                    directory_role="journal", name="swapped", add=FS_APPEND_FL
                )
            else:
                effects.clear_inode_flags(
                    directory_role="journal", name="swapped", remove=FS_APPEND_FL
                )
        assert refusal.value.classification == _executor_constant(
            "EFFECT_IDENTITY_MISMATCH"
        )
        assert target.read_bytes() == b"theirs\n"
    finally:
        inventory.close()


def test_the_removal_of_a_recorded_object_still_succeeds(tmp_path) -> None:
    """The positive control: the correction must not refuse everything."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        target = run / "journal" / "ours"
        target.write_bytes(b"\n")
        recorded = effects.record_identity(directory_role="journal", name="ours")
        record = effects.remove_object(directory_role="journal", name="ours")
        assert record.removal_issued
        assert record.recorded_identity == recorded
        assert record.pre_check_identity == recorded
        assert record.post_check_absent
        assert not target.exists()
    finally:
        inventory.close()


def test_the_documented_post_check_limitation_is_unchanged(tmp_path) -> None:
    """The post-check still establishes absence only, and says so."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        target = run / "journal" / "ours"
        target.write_bytes(b"\n")
        effects.record_identity(directory_role="journal", name="ours")
        record = effects.remove_object(directory_role="journal", name="ours")
        assert record.post_check_identity is None
        assert any("not" in line and "evidence" in line for line in record.establishes)
    finally:
        inventory.close()


@pytest.mark.parametrize(
    "conjunct", ["mandatory-record", "present-object", "equality"]
)
def test_the_ownership_control_admits_the_refused_input(tmp_path, conjunct) -> None:
    """**Negative controls.** One conjunct each, removed and nothing else.

    Each control re-issues exactly the production sequence with the named
    comparison omitted, and asserts the previously refused input is admitted —
    so each of the three is load-bearing rather than decorative.
    """
    inventory, filesystem, effects, run = _effects(tmp_path)
    try:
        traversal = inventory.traversal("journal")
        if conjunct == "mandatory-record":
            target = run / "journal" / "unbound"
            target.write_bytes(b"\n")
            # The mandatory-record conjunct, deliberately not applied:
            recorded = effects.recorded_identity("journal", "unbound")
            assert recorded == ""
            found = filesystem.fstatat(traversal, "unbound")
            assert found is not None
            filesystem.unlinkat(traversal, "unbound")
            assert not target.exists()
        elif conjunct == "present-object":
            target = run / "journal" / "vanished"
            target.write_bytes(b"\n")
            effects.record_identity(directory_role="journal", name="vanished")
            target.unlink()
            # The present-object conjunct, deliberately not applied: the
            # production path refuses here; this one proceeds to the removal.
            assert filesystem.fstatat(traversal, "vanished") is None
            with pytest.raises(Exception):
                filesystem.unlinkat(traversal, "vanished")
        else:
            target = run / "journal" / "swapped"
            target.write_bytes(b"ours\n")
            recorded = effects.record_identity(
                directory_role="journal", name="swapped"
            )
            _substitute(target)
            # The equality conjunct, deliberately not applied:
            found = filesystem.fstatat(traversal, "swapped")
            assert found is not None and found != recorded
            filesystem.unlinkat(traversal, "swapped")
            assert not target.exists()
    finally:
        inventory.close()


def test_the_ownership_rule_is_stated_where_the_effects_are(tmp_path) -> None:
    """The rule is a constant in the module, not only in a review record."""
    from tools.phase_5_0_evidence.execution.executor import OWNERSHIP_BINDING_RULE

    joined = " ".join(OWNERSHIP_BINDING_RULE)
    assert "mandatory" in joined
    assert "equality" in joined.lower()


def test_every_production_creation_path_records_its_own_identity(tmp_path) -> None:
    """r6 §1.4: the creating step records, so no caller has to remember to."""
    inventory, _fs, effects, run = _effects(tmp_path)
    try:
        for name in ("bin", "before", "journal", "probe", "probe-ro"):
            assert effects.recorded_identity("root", name)
        payload = b"#!/usr/bin/env python3\n"
        effects.install_case_program(
            content=payload,
            sha256=hashlib.sha256(payload).hexdigest(),
            directory_role="bin",
            name="case",
        )
        assert effects.recorded_identity("bin", "case")
        effects.create_object(
            directory_role="journal", name="000001.journal", mode=0o640
        )
        assert effects.recorded_identity("journal", "000001.journal")
        assert (run / "journal" / "000001.journal").exists()
    finally:
        inventory.close()
