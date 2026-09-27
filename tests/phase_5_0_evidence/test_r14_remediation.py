"""R14's Blocking finding, and the audit of every other ownership baseline.

**EH-R14-1.** R13 proved an object absent with a **failure** wherever its tool
had one. Three of the six baselines did that, and none of the three failures
means *absent*:

| Baseline | R13's proof | What the status actually means |
|---|---|---|
| `R-B-DB` | `psql` exit 2 | a **connection** failure. `pg_database.datallowconn = false` produces it for a database that plainly exists |
| `R-B-ROLE` | `psql` exit 3 | **any** statement error under `ON_ERROR_STOP=1` |
| `R-B-ROOT` | `stat` exit 1 | every failure coreutils' `stat` has, ENOENT and EIO alike |

Each one then established ownership, and cleanup acted on it: the reviewer's
reproduction ended with `DROP DATABASE IF EXISTS fb_evidence_p5_0` against a
database no step had created. The pre-fix behaviour of all three is recorded in
this module's first three tests, as the properties that now hold instead.

The corrections are not the same, because the tools are not:

* the two PostgreSQL baselines read a listing the server **returns** — a
  successful `SELECT` over `pg_database` or `pg_roles`, compared with a subject
  that must be absent and a control that must be present. Three states,
  distinguished: absent, present, and unknown; and
* the filesystem baseline is **blocked** (conflict C-8). No permitted executable
  reports path absence as anything but a generic failure, and the two ways round
  it — admitting another binary, or parsing the operating system's error prose —
  are the grammar changes R14 rules out. So it establishes nothing, the
  twenty-nine path mutations are owned by nothing, and the executor refuses the
  first step that would create one.

Everything here runs across the **injected** fakes in `test_r13_remediation.py`,
which is where the stateful `FakeHost` lives. Nothing starts a process, opens a
socket, reads an account database or touches a host: `test_no_execution.py`
scans this file with the rest.
"""
from __future__ import annotations

from dataclasses import replace

import pytest

from tools.phase_5_0_evidence import case_runtime
from tools.phase_5_0_evidence.case_runtime import (
    CASE_PROGRAM_SOURCE_PATH,
    EXIT_OBSERVATION_UNAVAILABLE,
    INTERPRETER_PATH,
    ROOT_NOTHING_CREATED_STATUSES,
    ROOT_PREEXISTING_STATUS,
)
from tools.phase_5_0_evidence.capture import (
    CATALOG_QUESTION_MISSING_MARKER,
    MALFORMED_LINE_MARKER,
    CapturePolicy,
    CatalogQuestion,
    sanitize,
)
from tools.phase_5_0_evidence.cleanup import CleanupStepKind
from tools.phase_5_0_evidence.concrete_plan import (
    COORDINATOR_ROLE,
    build_concrete_plan,
)
from tools.phase_5_0_evidence.errors import PlanRefused
from tools.phase_5_0_evidence.execution.executor import ExecutorRefused
from tools.phase_5_0_evidence.expectations import Comparison, DeclaredExpectation
from tools.phase_5_0_evidence.execution.boundary import CommandResult
from tools.phase_5_0_evidence.plan import CommandStep, StepRole
from tools.phase_5_0_evidence.review_manifest import COVERED_SOURCES, ReviewManifest

from tests.phase_5_0_evidence.harness_fixtures import (
    cleanup_observations_for,
    runnable_plan,
    supply_reviewed_e7_facts,
)
from tests.phase_5_0_evidence.test_r13_remediation import (
    EVIDENCE_DATABASE,
    REVIEWED_INTERPRETER_DIGEST,
    REVIEWED_INTERPRETER_REAL_PATH,
    ROOT,
    FakeHost,
    creation_step_for,
    runner,
    step_named,
)

SOURCES = {name: f"# {name}\n".encode("utf-8") for name in COVERED_SOURCES}

DATABASE_QUERY = "SELECT datname FROM pg_database"
ROLE_QUERY = "SELECT rolname FROM pg_roles"


@pytest.fixture(autouse=True)
def _reviewed_target_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_SHA256", REVIEWED_INTERPRETER_DIGEST
    )
    monkeypatch.setattr(
        case_runtime, "EXPECTED_INTERPRETER_REAL_PATH", REVIEWED_INTERPRETER_REAL_PATH
    )
    supply_reviewed_e7_facts(monkeypatch)


def plan_with_blocked_ownership():
    """The submitted plan, with any remaining blocker waived.

    **R16.** The plan carries none, because C-6, C-7 and C-8 are implemented, so
    this is now the submitted plan itself. It is kept as a named helper because
    the tests below are about the *ownership* question rather than about gate 2:
    suppose a blocker were waived tomorrow and nothing else changed — does the
    run still refuse to remove a path it did not create? It must, because gate 2
    is a statement about the plan and the ownership check is a statement about
    the object.
    """
    real = build_concrete_plan()
    return replace(real, unresolved=())


def path_mutations() -> set[str]:
    """Every path mutation the generated plan declares under the root."""
    return {
        mutation_id
        for step in build_concrete_plan().steps
        for mutation_id in (
            *step.establishes_ownership_by_creation,
            *step.establishes_ownership_of_contained,
        )
    }


def removal_vectors(host: FakeHost, fragment: str) -> list[tuple[str, ...]]:
    return [
        vector
        for vector in host.vectors
        if any(fragment in argument for argument in vector)
    ]


# ---------------------------------------------------------------------------
# EH-R14-1 — the three baselines that read a failure as absence
# ---------------------------------------------------------------------------


def test_a_database_that_refuses_connections_is_not_read_as_absent() -> None:
    """**The reviewer's reproduction, as the property that now holds.**

    R14's independent review seeded a pre-existing `fb_evidence_p5_0`, made its
    connection probe return 2 and the later `CREATE DATABASE` return 3, and
    recorded:

        creation B6-03 stopped_at B6-03
        baseline_satisfied True
        database_survives False
        drop_requested CL-08: DROP DATABASE IF EXISTS fb_evidence_p5_0

    The baseline was satisfied by the connection failure, the creation failed
    because the database was there, and cleanup dropped it. The same host state
    now stops the run **at the baseline**, because the catalog lists the database
    whether or not it accepts connections.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    # The pre-existing database. `FakeHost` answers a connection to it with the
    # very exit 2 the old baseline read as absence — `datallowconn = false` is
    # one way a real server produces it — and lists it in `pg_database`, which
    # is what a real server does whether or not it accepts connections.
    host.objects.add(f"database:{EVIDENCE_DATABASE}")

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == "R-B-DB"
    assert outcome.mutations_reached == ()
    assert host.has(f"database:{EVIDENCE_DATABASE}")
    assert outcome.cleanup_steps == ()
    assert removal_vectors(host, "DROP DATABASE") == []
    baseline = next(step for step in outcome.steps if step.step_id == "R-B-DB")
    assert not baseline.satisfied
    assert baseline.exit_status == 0, "the catalog query itself succeeded"
    assert ("subject_present", "yes") in baseline.observations
    assert ("control_present", "yes") in baseline.observations
    # And the baseline never connected to the database it is about, which is the
    # structural half of the correction: connectability is not observability.
    assert EVIDENCE_DATABASE not in baseline.argv


def test_a_role_that_exists_is_not_read_as_absent_from_a_statement_error() -> None:
    """The same finding on `R-B-ROLE`, whose R13 proof was `SET ROLE`'s exit 3.

    Exit 3 under `ON_ERROR_STOP=1` is any statement error, so a permission
    refusal, a catalog failure or a server that rejects the statement produced
    the same observation as an absent role — and the run then owned, and dropped,
    a role somebody else had created.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    host.objects.add(f"role:{COORDINATOR_ROLE}")

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == "R-B-ROLE"
    assert outcome.mutations_reached == ()
    assert host.has(f"role:{COORDINATOR_ROLE}")
    assert removal_vectors(host, "DROP ROLE") == []


def test_a_root_that_already_exists_is_refused_and_is_never_removed() -> None:
    """The R14 case, under R16's mechanism — and the same object survives.

    Pre-R14, a `stat` exit 1 over an existing root granted ownership of all
    twenty-nine path mutations, the first `install` was attempted, and cleanup
    requested `rmdir -- /var/lib/fb-evidence-p5-0`. R14 blocked the baseline, so
    the run stopped before creating anything and removed nothing.

    **R16 replaces the probe with the creation**, and the property this test
    exists for is unchanged: the pre-existing directory survives, and no removal
    is requested for it. What changes is where the run stops and why. `stat` is
    made to report the generic failure it reports for everything — an existing
    directory on a filesystem returning EIO — so the precondition passes, and
    `mkdir(2)` then reports **`EEXIST`**, which means exactly one thing.
    """
    plan = plan_with_blocked_ownership()
    host = FakeHost(plan)
    host.overrides["R-B-ROOT"] = CommandResult(exit_status=1, timed_out=False)
    host.objects.add(f"path:{ROOT}")

    outcome = runner(plan, host).execute()

    creation = creation_step_for(plan, f"directory:{ROOT}")
    assert outcome.stopped_at == creation
    assert "exit 15" in outcome.stop_reason
    # Ownership is **withdrawn**, not merely unclaimed: the attempt was made and
    # it is the attempt that reported the object was somebody else's.
    assert f"directory:{ROOT}" in outcome.mutations_reached
    assert not any(
        step.removes == ROOT for step in plan.cleanup_plan.steps
        if step.step_id in {item.step_id for item in outcome.cleanup_steps}
    )
    assert host.has(f"path:{ROOT}")
    assert removal_vectors(host, "/usr/bin/rmdir") == []
    assert removal_vectors(host, "/usr/bin/rm") == []
    assert ROOT in outcome.cleanup.preserved


def test_the_run_creates_no_path_when_the_root_creation_is_refused() -> None:
    """No `install` is reached, because the container was never made."""
    plan = plan_with_blocked_ownership()
    host = FakeHost(plan)
    host.overrides["R-B-ROOT"] = CommandResult(exit_status=1, timed_out=False)
    host.objects.add(f"path:{ROOT}")

    runner(plan, host).execute()

    assert not any(vector[0] == "/usr/bin/install" for vector in host.vectors)


# ---------------------------------------------------------------------------
# Absent, present, unknown — the three states, and the two that grant nothing
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("step_id", ["R-B-DB", "R-B-ROLE"])
@pytest.mark.parametrize(
    ("label", "result"),
    [
        (
            "the query could not be run at all",
            CommandResult(exit_status=2, timed_out=False),
        ),
        (
            "the listing was empty, so it carries no control",
            CommandResult(
                exit_status=0,
                timed_out=False,
                observations=(("control_present", "no"), ("subject_present", "no")),
            ),
        ),
        (
            "a line was not a catalog name",
            CommandResult(
                exit_status=0, timed_out=False, observations=(MALFORMED_LINE_MARKER,)
            ),
        ),
        (
            "the plan declared no question",
            CommandResult(
                exit_status=0,
                timed_out=False,
                observations=(CATALOG_QUESTION_MISSING_MARKER,),
            ),
        ),
        (
            "nothing was observed",
            CommandResult(exit_status=0, timed_out=False),
        ),
    ],
)
def test_an_unknown_catalog_reading_establishes_no_ownership(
    step_id: str, label: str, result: CommandResult
) -> None:
    """**Unknown is not absent, and never authorizes a deletion.**

    This is the half the R13 baselines had no representation for: *absent* and
    *could not tell* were the same observation, so an unreachable catalog handed
    the run ownership of an object it had never been able to look for. Each row
    here is a different way of not being able to tell, and every one stops the
    run at the baseline with nothing owned and nothing removed.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    host.overrides[step_id] = result

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == step_id, label
    assert outcome.mutations_reached == ()
    assert outcome.cleanup_steps == ()
    assert removal_vectors(host, "DROP DATABASE") == []
    assert removal_vectors(host, "DROP ROLE") == []


@pytest.mark.parametrize("step_id", ["R-B-DB", "R-B-ROLE"])
def test_an_absent_subject_beside_a_present_control_grants_ownership(
    step_id: str,
) -> None:
    """The positive direction, so the correction is not merely a way to refuse.

    The plan's own fake catalog carries `postgres` and does not carry the
    subject, the baseline is satisfied, and the mutation it owns is created and
    then removed by cleanup — which is the behaviour the harness needs and which
    a refusal-only correction would have destroyed.
    """
    plan = runnable_plan()
    host = FakeHost(plan)

    outcome = runner(plan, host).execute()

    baseline = next(step for step in outcome.steps if step.step_id == step_id)
    assert baseline.satisfied
    assert ("subject_present", "no") in baseline.observations
    assert ("control_present", "yes") in baseline.observations
    step = step_named(plan, step_id)
    assert set(step.establishes_ownership_of) <= set(outcome.mutations_reached)


# ---------------------------------------------------------------------------
# The audit — every ownership baseline in the generated plan
# ---------------------------------------------------------------------------

#: How each surviving baseline proves absence, and why that proof is unique.
#: A baseline whose absence claim rests on a status its tool also returns for
#: something else is the finding; a baseline is admitted here only with a reason
#: naming the documented behaviour it depends on.
PERMITTED_ABSENCE_PROOFS = {
    "/usr/bin/getent": (
        (2,),
        "getent(1) documents exit 2 as *one or more supplied key could not be "
        "found in the database*, distinct from 1 for a missing argument or "
        "unknown database and 3 for an unsupported enumeration.",
    ),
}


def test_no_ownership_baseline_proves_absence_with_a_generic_failure() -> None:
    """The audit R14 asks for, asserted over the generated plan.

    Every step that establishes ownership either exits **zero** and has its
    observation compared, or exits non-zero with a status its own tool documents
    as *not found*. There is no third kind, and a new baseline that took a
    generic failure as absence would fail here rather than in a review.
    """
    plan = build_concrete_plan()
    baselines = [step for step in plan.steps if step.establishes_ownership_of]
    assert baselines, "the plan has ownership baselines at all"
    for step in baselines:
        if step.satisfying_statuses == (0,):
            assert step.observation_expectations or step.capture is not (
                CapturePolicy.EXIT_STATUS_ONLY
            ), step.step_id
            continue
        permitted, _reason = PERMITTED_ABSENCE_PROOFS[step.argv[0]]
        assert step.satisfying_statuses == permitted, step.step_id


def test_every_surviving_baseline_compares_an_observation_or_a_documented_status() -> None:
    """The same audit, written as the roll call a reviewer reads.

    Six baseline kinds, and what each one is after R14. The list is exact rather
    than a filter, so a baseline that appeared or disappeared would fail here.
    """
    plan = build_concrete_plan()
    by_id = {step.step_id: step for step in plan.steps}
    # The two PostgreSQL baselines: a successful listing, compared.
    for step_id, query, subject in (
        ("R-B-DB", DATABASE_QUERY, EVIDENCE_DATABASE),
        ("R-B-ROLE", ROLE_QUERY, COORDINATOR_ROLE),
    ):
        step = by_id[step_id]
        assert step.satisfying_statuses == (0,)
        assert step.capture is CapturePolicy.CATALOG_MEMBERSHIP
        assert step.catalog_question == CatalogQuestion(
            subject=subject, control="postgres"
        )
        assert query in step.argv
        assert "--tuples-only" in step.argv and "--no-align" in step.argv
        # It reads the `postgres` database, not the object it is asking about:
        # a database that refuses connections must still be observable.
        assert step.argv[step.argv.index("--dbname") + 1] == "postgres"
        assert dict(
            (item.key, item.value) for item in step.observation_expectations
        ) == {"subject_present": "no", "control_present": "yes"}
    # The transient unit: a successful `systemctl show`, compared.
    unit = by_id["R-B-UNIT"]
    assert unit.satisfying_statuses == (0,)
    assert [item.value for item in unit.observation_expectations] == ["not-found"]
    # The accounts and groups: `getent`'s documented key-not-found status.
    getent = [
        step
        for step in plan.steps
        if step.establishes_ownership_of and step.argv[0] == "/usr/bin/getent"
    ]
    assert len(getent) == 7
    assert {step.satisfying_statuses for step in getent} == {(2,)}
    # The filesystem: nothing at all.
    assert by_id["R-B-ROOT"].establishes_ownership_of == ()


@pytest.mark.parametrize("status", [0, 1, 3, 4])
def test_a_getent_baseline_is_not_satisfied_by_any_other_status(status: int) -> None:
    """`getent`'s other statuses are error states, and none of them is absence.

    Exit 1 is a missing argument or an unknown database and exit 3 is an
    unsupported enumeration; exit 0 is the object being there. The run stops on
    each, owning nothing — so a name-service failure cannot hand this run a group
    it never saw.
    """
    plan = runnable_plan()
    host = FakeHost(plan)
    host.overrides["R-02"] = CommandResult(exit_status=status, timed_out=False)

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == "R-02"
    assert outcome.mutations_reached == ()
    assert not any(vector[0] == "/usr/sbin/groupadd" for vector in host.vectors)


# ---------------------------------------------------------------------------
# The blocked baseline, declared rather than approximated
# ---------------------------------------------------------------------------


def test_the_filesystem_baseline_still_establishes_nothing() -> None:
    """**R16 does not reattach ownership to `R-B-ROOT`.**

    That is the thing R14 was clearest about and the thing an ordinary repair
    would have done: `stat --format=%F` exits 1 for every failure it has, and no
    amount of surrounding machinery makes that status mean *absent*. The step is
    retained as a precondition — exit 0 soundly means something is there and
    rightly stops the run early — and it establishes ownership of nothing at all.
    """
    plan = build_concrete_plan()
    baseline = next(step for step in plan.steps if step.step_id == "R-B-ROOT")
    assert baseline.establishes_ownership_of == ()
    assert baseline.establishes_ownership_by_creation == ()
    assert baseline.establishes_ownership_of_contained == ()
    assert baseline.satisfying_statuses == (1,)
    assert not baseline.is_mutation_bearing
    # **R16, EH-R16-4.** C-8 is not among the plan's conflicts; C-7 is, because
    # Band 7's three producers do not exist. The distinction matters here: this
    # test is about the filesystem baseline, and a bare `conflicts() == ()` would
    # start failing for a reason that has nothing to do with it.
    assert "C-8" not in plan.conflicts()


def test_the_filesystem_ownership_comes_from_a_creation_and_not_a_probe() -> None:
    """Conflict **C-8**, resolved: exactly one step, and it is the creation.

    `mkdir(2)` has the property R14 searched the permitted executables for and
    did not find: a **unique, documented** status for *"something is already at
    this path"*, reported for a directory, a file, a symbolic link and a dangling
    symbolic link alike. So there is no probe, and therefore no window between
    an observation and a creation for an object to arrive in.
    """
    plan = build_concrete_plan()
    creations = [step for step in plan.steps if step.establishes_ownership_by_creation]
    assert len(creations) == 1
    (creation,) = creations
    assert creation.establishes_ownership_by_creation == (f"directory:{ROOT}",)
    assert creation.satisfying_statuses == (0,)
    assert creation.preexisting_statuses == (ROOT_PREEXISTING_STATUS,)
    assert creation.nothing_created_statuses == ROOT_NOTHING_CREATED_STATUSES
    assert 0 not in creation.nothing_created_statuses
    # The vector is the bootstrap copy: the reviewed source in the repository
    # tree, because a helper that creates this root cannot first be installed
    # inside it.
    assert creation.argv[0] == INTERPRETER_PATH
    assert creation.argv[3] == CASE_PROGRAM_SOURCE_PATH
    assert creation.argv[4] == "mkroot"
    assert creation.argv[5] == ROOT


def test_every_path_mutation_is_owned_by_that_one_creation() -> None:
    """The 29 mutations R14 left owned by nothing, and what owns them now.

    The root by the creation itself; the 28 inside it because `mkdir(2)` returns
    an **empty** directory, so at the instant the creation was satisfied there
    was nothing under that path for a later step to overwrite. The contained set
    is enumerated in the plan and pinned in the manifest rather than derived at
    run time, so a reviewer approves exactly which objects that reasoning covers.
    """
    plan = build_concrete_plan()
    (creation,) = [
        step for step in plan.steps if step.establishes_ownership_by_creation
    ]
    owned = set(creation.establishes_ownership_by_creation) | set(
        creation.establishes_ownership_of_contained
    )
    assert len(owned) == 29
    assert owned == path_mutations()
    for mutation_id in creation.establishes_ownership_of_contained:
        assert mutation_id.split(":", 1)[1].startswith(f"{ROOT}/")
    probed = {
        mutation_id
        for step in plan.steps
        for mutation_id in step.establishes_ownership_of
    }
    assert not (owned & probed)
    # Every reversal of a path mutation is now applicable-in-principle again,
    # and by this claim rather than by a probe.
    reversals = [
        step
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVERSAL and set(step.mutation_ids) & owned
    ]
    assert len(reversals) == 29


def test_a_creation_whose_outcome_is_unknown_removes_nothing() -> None:
    """The conservative half — an uncertain creation is residue, not absence.

    `mkdir(2)` returned and the identity read that follows it did not, so the
    case program exits 66: a directory may exist and this run cannot say which
    one. It is neither owned — nothing may remove it — nor absent, and reporting
    it as *preserved* would be claiming this run did not create it. It is
    bounded residue with the named operator recovery, and the run is S-B.
    """
    plan = plan_with_blocked_ownership()
    host = FakeHost(plan)
    creation = creation_step_for(plan, f"directory:{ROOT}")
    host.overrides[creation] = CommandResult(
        exit_status=EXIT_OBSERVATION_UNAVAILABLE,
        timed_out=False,
        observations=(("errno", "EIO"), ("result", "unobserved"), ("verb", "mkroot")),
    )

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == creation
    assert f"directory:{ROOT}" in outcome.mutations_reached
    assert ROOT in outcome.cleanup.residue
    assert ROOT not in outcome.cleanup.preserved
    assert outcome.cleanup.state == "S-B"
    assert removal_vectors(host, "/usr/bin/rmdir") == []
    assert not outcome.artifact_admissible


def test_an_interrupted_creation_is_treated_the_same_way() -> None:
    """A launch that never reported is the uncertain case too.

    `nothing_created_statuses` does not admit the executor's own `-1`, and it is
    the conservative default rather than an omission: a boundary that raised
    tells this run nothing about whether `mkdir(2)` ran.
    """
    plan = plan_with_blocked_ownership()
    host = FakeHost(plan)
    creation = creation_step_for(plan, f"directory:{ROOT}")
    host.overrides[creation] = RuntimeError("the boundary did not report")

    outcome = runner(plan, host).execute()

    assert outcome.stopped_at == creation
    assert ROOT in outcome.cleanup.residue
    assert outcome.cleanup.state == "S-B"
    assert removal_vectors(host, "/usr/bin/rmdir") == []


def test_a_replaced_root_does_not_have_its_replacement_deleted() -> None:
    """Cleanup revalidates the created object's identity before removing it.

    The run creates the root and everything in it, and then — between the
    creation and the cleanup — the object at that path is replaced. `statroot`
    reports a different inode, the executor's comparison fails, the `rmdir` is
    skipped, and the path is reported as residue for the operator recovery.
    Replacement of a path does not inherit permission to delete its replacement.
    """
    plan = plan_with_blocked_ownership()
    host = FakeHost(plan)
    revalidation = next(
        step.step_id
        for step in plan.cleanup_plan.steps
        if step.kind is CleanupStepKind.REVALIDATE
    )
    host.overrides[revalidation] = CommandResult(
        exit_status=0,
        timed_out=False,
        observations=(
            ("errno", "none"),
            ("result", "returned"),
            ("root_device", str(host.root_device)),
            ("root_inode", str(host.root_inode + 1)),
            ("verb", "statroot"),
        ),
    )

    outcome = runner(plan, host).execute()

    assert outcome.completed is True
    assert ROOT in outcome.cleanup.residue
    assert outcome.cleanup.state == "S-B"
    assert ("/usr/bin/rmdir", "--", ROOT) not in host.vectors
    assert host.has(f"path:{ROOT}")


def test_a_matching_revalidation_lets_the_removal_run() -> None:
    """The positive direction, so the check is not merely a way to refuse."""
    plan = plan_with_blocked_ownership()
    host = FakeHost(plan)

    outcome = runner(plan, host).execute()

    assert outcome.completed is True
    assert outcome.cleanup.state == "S-C"
    assert not host.has(f"path:{ROOT}")
    assert removal_vectors(host, "/usr/bin/rmdir")


# ---------------------------------------------------------------------------
# The reading itself
# ---------------------------------------------------------------------------


QUESTION = CatalogQuestion(subject="fb_evidence_p5_0", control="postgres")


@pytest.mark.parametrize(
    ("label", "listing", "expected"),
    [
        (
            "absent beside a present control",
            "postgres\ntemplate0\ntemplate1\n",
            (("control_present", "yes"), ("subject_present", "no")),
        ),
        (
            "present",
            "postgres\nfb_evidence_p5_0\n",
            (("control_present", "yes"), ("subject_present", "yes")),
        ),
        (
            "a listing with no control is unknown, not absent",
            "template0\ntemplate1\n",
            (("control_present", "no"), ("subject_present", "no")),
        ),
        (
            "blank lines are termination, not records",
            "\npostgres\n\ntemplate1\n\n",
            (("control_present", "yes"), ("subject_present", "no")),
        ),
        (
            "no output at all",
            "",
            (("control_present", "no"), ("subject_present", "no")),
        ),
        (
            "a psql notice, an error sentence or a header refuses",
            "postgres\nFATAL:  the connection was closed\n",
            (MALFORMED_LINE_MARKER,),
        ),
        (
            "a padded name is not a name",
            "postgres\nfb_evidence_p5_0 | UTF8\n",
            (MALFORMED_LINE_MARKER,),
        ),
    ],
)
def test_a_catalog_listing_reads_as_the_two_answers_and_nothing_else(
    label: str, listing: str, expected: tuple[tuple[str, str], ...]
) -> None:
    assert sanitize(
        CapturePolicy.CATALOG_MEMBERSHIP, listing, catalog=QUESTION
    ) == expected, label


def test_a_catalog_listing_never_records_a_name_it_read() -> None:
    """The rule this module exists for, on the one policy that reads a list.

    Other people's database and role names are operational data, they are
    unbounded, and none of them is a reviewed expectation. What survives the
    reading is two yes/no answers about names the plan already stated.
    """
    listing = "postgres\nsomebody_elses_database\nanother_one\n"
    observations = sanitize(
        CapturePolicy.CATALOG_MEMBERSHIP, listing, catalog=QUESTION
    )
    text = " ".join(f"{key}={value}" for key, value in observations)
    assert "somebody_elses_database" not in text
    assert "another_one" not in text
    assert {key for key, _ in observations} == {"subject_present", "control_present"}


def test_a_reading_with_no_question_is_refused_rather_than_answered() -> None:
    assert sanitize(CapturePolicy.CATALOG_MEMBERSHIP, "postgres\n") == (
        CATALOG_QUESTION_MISSING_MARKER,
    )


def test_a_question_handed_to_another_policy_is_refused() -> None:
    with pytest.raises(ValueError):
        sanitize(CapturePolicy.FILE_MODE, "0 0 755 directory", catalog=QUESTION)


@pytest.mark.parametrize(
    ("subject", "control"),
    [("postgres", "postgres"), ("", "postgres"), ("Fb_Evidence", "postgres")],
)
def test_a_catalog_question_refuses_a_shape_it_cannot_compare(
    subject: str, control: str
) -> None:
    with pytest.raises(ValueError):
        CatalogQuestion(subject=subject, control=control)


# ---------------------------------------------------------------------------
# The plan refuses a baseline that could not mean what it says
# ---------------------------------------------------------------------------


CATALOG_EXPECTATIONS = (
    DeclaredExpectation(
        key="control_present", comparison=Comparison.TEXT, value="yes"
    ),
    DeclaredExpectation(
        key="subject_present", comparison=Comparison.TEXT, value="no"
    ),
)


def a_catalog_step(**overrides) -> CommandStep:
    keywords = dict(
        step_id="X-01",
        band="discovery",
        run_as="postgres",
        argv=("/usr/bin/psql", "--command", DATABASE_QUERY),
        purpose="read a catalog",
        role=StepRole.DEPENDENT,
        capture=CapturePolicy.CATALOG_MEMBERSHIP,
        catalog_question=QUESTION,
        observation_expectations=CATALOG_EXPECTATIONS,
    )
    keywords.update(overrides)
    return CommandStep(**keywords)


def test_a_catalog_step_without_a_question_is_refused() -> None:
    with pytest.raises(PlanRefused, match="states no question"):
        a_catalog_step(catalog_question=None)


def test_a_question_on_a_step_that_reads_no_catalog_is_refused() -> None:
    with pytest.raises(PlanRefused, match="does not read a catalog"):
        a_catalog_step(
            capture=CapturePolicy.EXIT_STATUS_ONLY, observation_expectations=()
        )


def test_a_baseline_may_not_own_an_object_it_did_not_look_for() -> None:
    """The substitution one level up: proving one name absent, owning another."""
    with pytest.raises(PlanRefused, match="claims ownership"):
        a_catalog_step(
            establishes_ownership_of=("postgres_database:some_other_database",)
        )


# ---------------------------------------------------------------------------
# What the reviewer approves
# ---------------------------------------------------------------------------


def test_the_manifest_pins_the_question_and_the_blocked_mutations() -> None:
    """A vector that names no object needs its question in the reviewed record.

    `SELECT datname FROM pg_database` is the same nine words whichever database
    a baseline is about, so a manifest that pinned only the vector would approve
    a plan and admit a different one.
    """
    plan = build_concrete_plan()
    body = ReviewManifest.build(plan, SOURCES).as_mapping()
    steps = {step["step_id"]: step for step in body["steps"]}
    assert steps["R-B-DB"]["catalog_question"] == {
        "subject": EVIDENCE_DATABASE,
        "control": "postgres",
    }
    assert steps["R-B-ROLE"]["catalog_question"] == {
        "subject": COORDINATOR_ROLE,
        "control": "postgres",
    }
    assert steps["R-01"]["catalog_question"] is None
    # **R16.** C-8's blocker is gone, and what replaced it is pinned in its
    # place: which step owns by creating, which objects that creation carries,
    # and the statuses that separate *"nothing was created"* from *"it may exist
    # and cannot be identified"*. A reviewer approves the claim the deletions
    # rest on, and the digest changes when any of it does.
    # **R16, EH-R16-4.** The unresolved list is not empty: Band 7's three cases
    # are declared unresolved under C-7 because their producers do not exist.
    # What C-8 no longer contributes is a *filesystem* blocker, and that is what
    # is asserted, together with the claim that replaced it.
    # **C-P5.0-R5-R2, PLAN-1.** S4-3's producer dependency is declared under
    # C-S4-3 in the filesystem band. It is a missing producer, not a blocked
    # ownership baseline, so it blocks no mutation.
    assert {item["conflict_id"] for item in body["unresolved"]} == {"C-7", "C-S4-3"}
    assert {
        item["band"] for item in body["unresolved"] if item["conflict_id"] == "C-7"
    } == {"provenance", "journal"}
    assert [
        (item["band"], item["evidence_case_ids"], item["blocks_mutation_ids"])
        for item in body["unresolved"]
        if item["conflict_id"] == "C-S4-3"
    ] == [("filesystem", ["S4-3"], [])]
    creation = next(
        step for step in body["steps"] if step["establishes_ownership_by_creation"]
    )
    assert creation["establishes_ownership_by_creation"] == [f"directory:{ROOT}"]
    assert len(creation["establishes_ownership_of_contained"]) == 28
    assert creation["nothing_created_statuses"] == list(
        ROOT_NOTHING_CREATED_STATUSES
    )
    assert creation["preexisting_statuses"] == [ROOT_PREEXISTING_STATUS]
    assert steps["R-B-ROOT"]["establishes_ownership_by_creation"] == []
    # And the cleanup revalidation that guards the removal is pinned too.
    revalidation = next(
        step for step in body["cleanup_steps"] if step["kind"] == "revalidate"
    )
    assert revalidation["applies_with"] == [f"directory:{ROOT}"]
    assert revalidation["capture"] == "case_result"
    guarded = next(
        step for step in body["cleanup_steps"] if step["removes"] == ROOT
    )
    assert guarded["requires_revalidated"] == revalidation["step_id"]


def test_changing_only_the_subject_changes_the_reviewed_digest() -> None:
    """The pin is load-bearing, not decorative."""
    plan = build_concrete_plan()
    before = ReviewManifest.build(plan, SOURCES).digest()
    steps = tuple(
        replace(
            step,
            catalog_question=CatalogQuestion(
                subject="another_database", control="postgres"
            ),
            establishes_ownership_of=("postgres_database:another_database",),
        )
        if step.step_id == "R-B-DB"
        else step
        for step in plan.steps
    )
    altered = replace(
        plan, execution_plan=replace(plan.execution_plan, steps=steps)
    )
    assert ReviewManifest.build(altered, SOURCES).digest() != before
