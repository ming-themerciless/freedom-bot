"""Conflict **C-4**: the bounded file-materialization mechanism.

Two questions, and this file is organised around them.

1. **Are the reviewed bytes the bytes the design asks for?** Not asserted by
   restating them — that would compare the content with a copy of itself — but by
   running `hba.analyse_hba()` and `hba.analyse_ident()` over them, which are the
   analyses the evidence band uses on a supplied file and which know nothing
   about this table.
2. **Can the mechanism write anything else?** Every test below that is not the
   first two is a negative one: an unreviewed destination, a production path, a
   digest that does not match its content, a symbolic link where a regular file
   was expected, an absent file, an unarmed materializer, a non-root process, a
   capture that was never taken. None of them writes, and none of them can be
   made to write by an argument.

**Nothing here writes a file the test did not create in `tmp_path`, and nothing
here reads a host configuration file.** The real `SystemMaterializer` is
exercised against synthetic paths under pytest's temporary directory with an
injected identity lookup, and it is armed only where the property under test is
what an armed one refuses.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass

import pytest

from tools.phase_5_0_evidence.approved_target import APPROVED_TARGET
from tools.phase_5_0_evidence.concrete_plan import (
    MAPPED_OS_USER,
    MAPPED_POSTGRES_ROLE,
    build_concrete_plan,
)
from tools.phase_5_0_evidence.errors import PlanRefused
from tools.phase_5_0_evidence.execution.boundary import (
    IdentityAbsent,
    IdentityInconsistent,
)
from tools.phase_5_0_evidence.execution.materializer import (
    MATERIALIZATION_CONTENT_REFUSED,
    MATERIALIZATION_DESTINATION_NOT_REVIEWED,
    MATERIALIZATION_DIGEST_MISMATCH,
    MATERIALIZATION_FAILURES,
    MATERIALIZATION_IDENTITY_UNKNOWN,
    MATERIALIZATION_OBJECT_TYPE,
    MATERIALIZATION_ROOT_UNAVAILABLE,
    MATERIALIZER_NOT_ARMED,
    RecordingMaterializer,
    SystemMaterializer,
)
from tools.phase_5_0_evidence.hba import analyse_hba, analyse_ident
from tools.phase_5_0_evidence.materialization import (
    MATERIALIZED_GROUP,
    MATERIALIZED_MODE,
    MATERIALIZED_OWNER,
    MAX_MATERIALIZED_BYTES,
    MaterializedFile,
    reviewed_configuration,
)
from tools.phase_5_0_evidence.plan import MaterializeStep, MutationKind

PLAN = build_concrete_plan()
CONFIG_DIR = APPROVED_TARGET.postgres_config_directory
REVIEWED = reviewed_configuration(APPROVED_TARGET)


# ---------------------------------------------------------------------------
# The reviewed bytes are the bytes the design asks for
# ---------------------------------------------------------------------------


def test_the_reviewed_hba_bytes_satisfy_the_bands_own_ordering_analysis() -> None:
    """§2.12.3's claim, checked by the analysis rather than by transcription.

    `analyse_hba` is the function the evidence band runs over a supplied file.
    It knows nothing about `materialization.py`, so agreement here is an
    observation about the bytes and not a tautology.
    """
    text = REVIEWED["pg_hba.conf"].content.decode("ascii")
    analysis = analyse_hba(text, production_database=APPROVED_TARGET.database_name)

    assert analysis.ordering_holds is True
    assert analysis.findings == ()
    assert analysis.coordinator_peer_index == 0
    assert analysis.first_matching_index == 0


def test_the_reviewed_ident_bytes_map_exactly_one_system_user() -> None:
    analysis = analyse_ident(REVIEWED["pg_ident.conf"].content.decode("ascii"))
    assert analysis.mapping_is_exact is True
    assert analysis.findings == ()
    assert analysis.coordinator_lines == 1


def test_the_reviewed_bytes_keep_the_cleanup_able_to_connect() -> None:
    """The trailing broader rule is load-bearing.

    Every `psql` step in the derived cleanup — the reload, the post-reload
    control and both drops — connects over the local socket as `postgres`. A
    synthetic file carrying only the five coordinator rules would lock the
    harness out of its own cleanup, which is state S-B for a defect in the plan.
    """
    lines = [
        line
        for line in REVIEWED["pg_hba.conf"].content.decode("ascii").splitlines()
        if line and not line.startswith("#")
    ]
    assert lines[-1].split() == ["local", "all", "all", "peer"]
    assert len(lines) == 6


def test_the_reviewed_content_is_ascii_bounded_and_newline_terminated() -> None:
    for reviewed in REVIEWED.values():
        content = reviewed.content
        assert content.decode("ascii")
        assert content.endswith(b"\n")
        assert b"\n\n" not in content
        assert b"\t" not in content and b"\x00" not in content
        assert 0 < len(content) <= MAX_MATERIALIZED_BYTES
        assert hashlib.sha256(content).hexdigest() == reviewed.sha256


# ---------------------------------------------------------------------------
# The closed table cannot be widened
# ---------------------------------------------------------------------------


def test_a_content_edit_without_a_digest_edit_is_refused() -> None:
    """The digest is a constant, so an edited rule fails at construction."""
    original = REVIEWED["pg_hba.conf"]
    with pytest.raises(PlanRefused) as refusal:
        MaterializedFile(
            filename=original.filename,
            lines=original.lines + ("local        all               all   trust",),
            owner=original.owner,
            group=original.group,
            mode=original.mode,
            sha256=original.sha256,
        )
    assert "pinned digest" in str(refusal.value)


@pytest.mark.parametrize(
    "filename", ["postgresql.conf", "pg_hba.conf.bak", "passwd", "", "pg_hba.conf "]
)
def test_only_the_two_configuration_filenames_can_be_materialized(filename: str) -> None:
    with pytest.raises(PlanRefused):
        MaterializedFile(
            filename=filename,
            lines=("local all all peer",),
            owner=MATERIALIZED_OWNER,
            group=MATERIALIZED_GROUP,
            mode=MATERIALIZED_MODE,
            sha256="0" * 64,
        )


@pytest.mark.parametrize(
    "line",
    [
        "local\tall\tall\tpeer",
        "local all all peer\x00",
        "local all all peer  # naïve",
        "local all all peer $(id)",
    ],
)
def test_a_line_outside_the_permitted_character_set_is_refused(line: str) -> None:
    with pytest.raises(PlanRefused) as refusal:
        MaterializedFile(
            filename="pg_hba.conf",
            lines=(line,),
            owner=MATERIALIZED_OWNER,
            group=MATERIALIZED_GROUP,
            mode=MATERIALIZED_MODE,
            sha256="0" * 64,
        )
    assert "outside the permitted set" in str(refusal.value)


@pytest.mark.parametrize(
    "owner, group, mode",
    [
        ("root", MATERIALIZED_GROUP, MATERIALIZED_MODE),
        (MATERIALIZED_OWNER, "root", MATERIALIZED_MODE),
        (MATERIALIZED_OWNER, MATERIALIZED_GROUP, 0o666),
        (MATERIALIZED_OWNER, MATERIALIZED_GROUP, 0o644),
    ],
)
def test_the_ownership_and_mode_are_pinned_to_one_value(owner, group, mode) -> None:
    with pytest.raises(PlanRefused):
        MaterializedFile(
            filename="pg_ident.conf",
            lines=("freedom_coord freedomcoord freedom_migration_coordinator",),
            owner=owner,
            group=group,
            mode=mode,
            sha256="0" * 64,
        )


def test_content_beyond_the_reviewed_bound_is_refused() -> None:
    filler = ("# " + "a" * 60,) * 200
    with pytest.raises(PlanRefused) as refusal:
        MaterializedFile(
            filename="pg_hba.conf",
            lines=filler,
            owner=MATERIALIZED_OWNER,
            group=MATERIALIZED_GROUP,
            mode=MATERIALIZED_MODE,
            sha256="0" * 64,
        )
    assert "bound" in str(refusal.value)


# ---------------------------------------------------------------------------
# The generated steps
# ---------------------------------------------------------------------------


def test_the_generated_plan_materializes_exactly_the_two_configuration_files() -> None:
    assert len(PLAN.materializations) == 2
    destinations = [item.destination for item in PLAN.materializations]
    assert destinations == [
        f"{CONFIG_DIR}/pg_hba.conf",
        f"{CONFIG_DIR}/pg_ident.conf",
    ]
    for item in PLAN.materializations:
        assert item.run_as == "root"
        assert item.file.owner == MATERIALIZED_OWNER
        assert item.file.group == MATERIALIZED_GROUP
        assert item.file.mode == MATERIALIZED_MODE
        assert item.evidence_case_ids == ("HBA-POST-CHANGE-ORDERING",)
        assert not hasattr(item, "argv")


def test_each_materialization_declares_the_configuration_mutation_it_performs() -> None:
    declared = {
        mutation.mutation_id: mutation
        for mutation in PLAN.mutations
        if mutation.kind is MutationKind.POSTGRES_CONFIG_LINE
    }
    performed: set[str] = set()
    for item in PLAN.materializations:
        assert len(item.mutation_ids) == 1
        (mutation_id,) = item.mutation_ids
        assert mutation_id in declared
        assert declared[mutation_id].file_path == item.destination
        assert declared[mutation_id].maps_os_user == MAPPED_OS_USER
        assert declared[mutation_id].maps_postgres_role == MAPPED_POSTGRES_ROLE
        performed.add(mutation_id)
    assert performed == set(declared)


def test_every_configuration_mutation_is_now_performed_and_reversed() -> None:
    """The traceability row that used to read *"not reached by any generated
    step"* names a step, and still names exactly one reversal."""
    rows = {row[0]: row for row in PLAN.traceability()}
    for item in PLAN.materializations:
        (mutation_id,) = item.mutation_ids
        _identifier, performed, reversed_by = rows[mutation_id]
        assert performed == item.step_id
        assert reversed_by and "NO REVERSAL" not in reversed_by


def test_each_materialization_runs_after_its_own_byte_exact_capture() -> None:
    order = {step.step_id: index for index, step in enumerate(PLAN.steps)}
    for item in PLAN.materializations:
        capture = next(
            step for step in PLAN.steps if step.step_id == item.capture_step_id
        )
        # **r6 §§1.4.3 and 2.3.3, C-P5.0-LAB-I-R1.** The capture is no longer
        # two `install` vectors copying into `R/before`. It is one effect that
        # publishes both reviewed components into the **independent** store and
        # reports every publication barrier crossed; `R/before` is retained as
        # evidence and is not a recovery basis.
        assert capture.is_effect
        assert capture.effect.kind.value == "capture_configuration"
        assert item.destination.rsplit("/", 1)[-1] in capture.effect.components
        assert order[item.capture_step_id] <= order[item.after_step_id]


def test_the_materializations_precede_the_reload_that_makes_them_effective() -> None:
    order = {step.step_id: index for index, step in enumerate(PLAN.steps)}
    reload_step = next(
        step for step in PLAN.steps if "SELECT pg_reload_conf()" in step.argv
    )
    for item in PLAN.materializations:
        assert order[item.after_step_id] < order[reload_step.step_id]


def test_a_materialization_naming_an_unreviewed_destination_is_refused() -> None:
    reviewed = REVIEWED["pg_hba.conf"]
    for destination in (
        "/etc/pg_hba.conf",
        "/var/lib/freedom-sheet-writer/pg_hba.conf",
        f"{APPROVED_TARGET.root_path}/pg_hba.conf",
        "/etc/postgresql/16/main/postgresql.conf",
    ):
        with pytest.raises(PlanRefused):
            MaterializeStep(
                step_id="X-M1",
                band="postgresql",
                run_as="root",
                destination=destination,
                file=reviewed,
                purpose="a destination nobody reviewed",
                capture_step_id="B6-01",
                after_step_id="B6-04",
                mutation_ids=("postgres_config_line:x",),
            ).validate_against(APPROVED_TARGET)


def test_a_materialization_cannot_run_as_anything_but_the_root_harness() -> None:
    with pytest.raises(PlanRefused) as refusal:
        MaterializeStep(
            step_id="X-M1",
            band="postgresql",
            run_as="postgres",
            destination=f"{CONFIG_DIR}/pg_hba.conf",
            file=REVIEWED["pg_hba.conf"],
            purpose="p",
            capture_step_id="B6-01",
            after_step_id="B6-04",
            mutation_ids=("postgres_config_line:x",),
        )
    assert "no child to give another identity to" in str(refusal.value)


def test_a_materialization_that_declares_no_mutation_is_refused() -> None:
    with pytest.raises(PlanRefused) as refusal:
        MaterializeStep(
            step_id="X-M1",
            band="postgresql",
            run_as="root",
            destination=f"{CONFIG_DIR}/pg_hba.conf",
            file=REVIEWED["pg_hba.conf"],
            purpose="p",
            capture_step_id="B6-01",
            after_step_id="B6-04",
        )
    assert "declares no mutation" in str(refusal.value)


def test_a_plan_whose_capture_follows_its_materialization_is_refused() -> None:
    """Ordering is checked, not described: a capture taken after the file has
    been replaced captures the replacement."""
    from tools.phase_5_0_evidence.plan import ExecutionPlan

    real = PLAN.execution_plan
    inverted = tuple(
        item.__class__(
            **{
                **{
                    name: getattr(item, name)
                    for name in item.__dataclass_fields__
                },
                "capture_step_id": PLAN.steps[-1].step_id,
            }
        )
        for item in real.materializations
    )
    with pytest.raises(PlanRefused) as refusal:
        ExecutionPlan(
            target=real.target,
            steps=real.steps,
            mutations=real.mutations,
            materializations=inverted,
        )
    assert "orders later" in str(refusal.value)


# ---------------------------------------------------------------------------
# The materializer itself
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FakeLookup:
    """A synthetic account database. No test here reads a real one.

    `effective_ids` reports 0/0 so the root precondition can be exercised
    without privilege, and it reports something else where the property under
    test is what a non-root process is refused. `account` and `group_id` report
    **this process's own** ids rather than PostgreSQL's, because the one test
    that lets the write through has to be able to `fchown` the result, and a
    process may always chown a file it owns to itself. Neither call reads the
    account database: `os.getuid()` is a property of the process.
    """

    euid: int = 0
    egid: int = 0
    known: bool = True

    def account(self, name: str) -> tuple[int, int]:
        if not self.known:
            raise IdentityAbsent(f"no account named {name!r} exists")
        return os.getuid(), os.getgid()

    def group_id(self, name: str) -> int:
        if not self.known:
            raise IdentityAbsent(f"no group named {name!r} exists")
        return os.getgid()

    def supplementary_group_names(self, name: str, primary_gid: int) -> frozenset[str]:
        return frozenset()

    def effective_ids(self) -> tuple[int, int]:
        return self.euid, self.egid


def config_file(tmp_path, filename: str = "pg_hba.conf"):
    """A synthetic PostgreSQL configuration directory under `tmp_path`.

    `validate_postgres_config_directory` requires a `postgresql` or `pgsql` path
    segment, which is the guard the materializer re-derives independently of the
    plan, so the fixture has to satisfy it the same way a real instance does.
    """
    directory = tmp_path / "etc" / "postgresql" / "16" / "main"
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / filename
    destination.write_bytes(b"# the pre-change file\n")
    return destination


def materialize(materializer, destination, reviewed, **overrides):
    keywords = dict(
        step_id="B6-M1",
        destination=str(destination),
        content=reviewed.content,
        sha256=reviewed.sha256,
        owner=reviewed.owner,
        group=reviewed.group,
        mode=reviewed.mode,
    )
    keywords.update(overrides)
    return materializer.materialize(**keywords)


def test_an_unarmed_materializer_writes_nothing(tmp_path) -> None:
    destination = config_file(tmp_path)
    before = destination.read_bytes()
    result = materialize(
        SystemMaterializer(lookup=FakeLookup()), destination, REVIEWED["pg_hba.conf"]
    )
    assert result.applied is False
    assert result.failure == MATERIALIZER_NOT_ARMED
    assert destination.read_bytes() == before


def test_the_recording_materializer_records_and_writes_nothing(tmp_path) -> None:
    destination = config_file(tmp_path)
    before = destination.read_bytes()
    recording = RecordingMaterializer()
    result = materialize(recording, destination, REVIEWED["pg_hba.conf"])
    assert result.applied is False
    assert result.failure == MATERIALIZER_NOT_ARMED
    assert recording.requests == [
        ("B6-M1", str(destination), REVIEWED["pg_hba.conf"].sha256)
    ]
    assert destination.read_bytes() == before


def test_an_armed_materializer_writes_exactly_the_reviewed_bytes(tmp_path) -> None:
    destination = config_file(tmp_path)
    reviewed = REVIEWED["pg_hba.conf"]
    result = materialize(
        SystemMaterializer(armed=True, lookup=FakeLookup()), destination, reviewed
    )
    assert result.applied is True and result.failure == ""
    assert destination.read_bytes() == reviewed.content
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == reviewed.sha256


def test_content_that_does_not_hash_to_its_digest_is_refused(tmp_path) -> None:
    destination = config_file(tmp_path)
    before = destination.read_bytes()
    result = materialize(
        SystemMaterializer(armed=True, lookup=FakeLookup()),
        destination,
        REVIEWED["pg_hba.conf"],
        content=REVIEWED["pg_hba.conf"].content + b"local all all trust\n",
    )
    assert result.failure == MATERIALIZATION_DIGEST_MISMATCH
    assert destination.read_bytes() == before


@pytest.mark.parametrize(
    "content", [b"", b"x" * (MAX_MATERIALIZED_BYTES + 1)], ids=["empty", "oversized"]
)
def test_content_outside_the_reviewed_bound_is_refused(tmp_path, content: bytes) -> None:
    destination = config_file(tmp_path)
    result = materialize(
        SystemMaterializer(armed=True, lookup=FakeLookup()),
        destination,
        REVIEWED["pg_hba.conf"],
        content=content,
        sha256=hashlib.sha256(content).hexdigest(),
    )
    assert result.failure == MATERIALIZATION_CONTENT_REFUSED


def test_a_destination_outside_a_postgresql_configuration_directory_is_refused(
    tmp_path,
) -> None:
    """Re-derived by the materializer from the guards, without the plan.

    Each of these would already have been refused by the executor's comparison
    with `config_path()`; the point is that the write itself refuses them too.
    """
    reviewed = REVIEWED["pg_hba.conf"]
    armed = SystemMaterializer(armed=True, lookup=FakeLookup())
    victims = tmp_path / "etc"
    victims.mkdir(parents=True, exist_ok=True)
    (victims / "pg_hba.conf").write_bytes(b"# not an instance directory\n")
    for destination in (
        str(victims / "pg_hba.conf"),
        "/etc/passwd",
        "/etc/sudoers.d/pg_hba.conf",
        "/var/lib/freedom-sheet-writer/pg_hba.conf",
        "/etc/postgresql/16/main/postgresql.conf",
        "pg_hba.conf",
        "/etc/postgresql/16/main/../../passwd",
    ):
        result = materialize(armed, destination, reviewed)
        assert result.failure == MATERIALIZATION_DESTINATION_NOT_REVIEWED, destination


def test_a_destination_that_is_not_an_existing_regular_file_is_refused(
    tmp_path,
) -> None:
    reviewed = REVIEWED["pg_hba.conf"]
    armed = SystemMaterializer(armed=True, lookup=FakeLookup())
    directory = tmp_path / "etc" / "postgresql" / "16" / "main"
    directory.mkdir(parents=True, exist_ok=True)

    absent = directory / "pg_hba.conf"
    assert materialize(armed, absent, reviewed).failure == MATERIALIZATION_OBJECT_TYPE

    elsewhere = tmp_path / "elsewhere"
    elsewhere.write_bytes(b"# the file a link would reach\n")
    link = directory / "pg_ident.conf"
    os.symlink(elsewhere, link)
    assert (
        materialize(armed, link, REVIEWED["pg_ident.conf"]).failure
        == MATERIALIZATION_OBJECT_TYPE
    )
    assert elsewhere.read_bytes() == b"# the file a link would reach\n"

    as_directory = directory / "pg_hba.conf"
    as_directory.mkdir()
    assert (
        materialize(armed, as_directory, reviewed).failure
        == MATERIALIZATION_OBJECT_TYPE
    )


def test_a_process_that_is_not_root_cannot_materialize(tmp_path) -> None:
    destination = config_file(tmp_path)
    before = destination.read_bytes()
    for euid, egid in ((1000, 0), (0, 1000), (1000, 1000)):
        result = materialize(
            SystemMaterializer(armed=True, lookup=FakeLookup(euid=euid, egid=egid)),
            destination,
            REVIEWED["pg_hba.conf"],
        )
        assert result.failure == MATERIALIZATION_ROOT_UNAVAILABLE
        assert destination.read_bytes() == before


def test_an_unresolvable_owner_or_group_is_refused(tmp_path) -> None:
    destination = config_file(tmp_path)
    before = destination.read_bytes()
    result = materialize(
        SystemMaterializer(armed=True, lookup=FakeLookup(known=False)),
        destination,
        REVIEWED["pg_hba.conf"],
    )
    assert result.failure == MATERIALIZATION_IDENTITY_UNKNOWN
    assert destination.read_bytes() == before


def test_every_refusal_is_one_of_the_fixed_classifications(tmp_path) -> None:
    """The vocabulary a run may serialize is closed, as it is for a launch
    failure. No path, account, digest or operating-system message is in it."""
    destination = config_file(tmp_path)
    armed = SystemMaterializer(armed=True, lookup=FakeLookup())
    observed = {
        materialize(SystemMaterializer(lookup=FakeLookup()), destination, REVIEWED["pg_hba.conf"]).failure,
        materialize(armed, "/etc/passwd", REVIEWED["pg_hba.conf"]).failure,
        materialize(armed, destination, REVIEWED["pg_hba.conf"], content=b"x", sha256="0" * 64).failure,
    }
    assert observed <= MATERIALIZATION_FAILURES
    assert "" not in observed
    for failure in observed:
        assert "/" not in failure and " " not in failure


def test_the_write_can_neither_create_a_file_nor_follow_a_link() -> None:
    """Asserted on the flags in the source, not on an observed behaviour.

    The three that matter are read off the `os.open` call itself: `O_TRUNC` and
    `O_WRONLY` are what replace the content, `O_NOFOLLOW` is what makes the
    preceding `lstat` meaningful against a link swapped in afterwards, and
    `O_CREAT` is **absent**, which is why a materialization can only ever replace
    a file the reviewed capture step has already copied.

    `test_no_execution.py` already covers this module for a shell, a process
    starter and a network client, over the whole execution tier.
    """
    import ast
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2]
        / "tools"
        / "phase_5_0_evidence"
        / "execution"
        / "materializer.py"
    ).read_text(encoding="utf-8")

    opens = [
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "open"
    ]
    assert len(opens) == 1, "there is one place this module opens anything"
    flags = {
        node.attr
        for node in ast.walk(opens[0].args[1])
        if isinstance(node, ast.Attribute)
    }
    assert flags == {"O_WRONLY", "O_TRUNC", "O_NOFOLLOW"}


def test_nothing_in_the_planning_tier_can_write_the_reviewed_bytes() -> None:
    """The content lives in the planning tier and the write does not.

    `materialization.py` is covered by the review manifest and has no file
    access at all — which `test_no_execution.py` asserts over the whole tier —
    so the reviewed bytes can be reviewed without the module that holds them
    being able to install them.
    """
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2]
        / "tools"
        / "phase_5_0_evidence"
        / "materialization.py"
    ).read_text(encoding="utf-8")
    for forbidden in ("import os", "open(", "write_bytes", "write_text"):
        assert forbidden not in source, forbidden
