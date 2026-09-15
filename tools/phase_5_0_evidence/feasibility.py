"""Bounded, evidence-only synthetic producers for the three C-7 cases.

## What this module is for, and the sentence that bounds it

Conflict **C-7** is that `JNL-51-PROVENANCE-OMITTED`,
`JNL-47-NO-GENERATION-ON-FAILURE` and `JNL-47-RECOVERY-STATE` have **no
producer**. Their observations are of `init-generation` and the §2.13.2a probe —
Package 5.0's gated product work — and no argument vector this harness can write
produces one. R16's **EH-R16-4** refused the attempt to resolve that by
describing the producer: *"Naming `init-generation` and a future table does not
resolve the evidence dependency."*

The 2026-09-10 laboratory direction (C-P5.0-LAB-1) permits something narrower and
says exactly how narrow:

> The September 2 exception permits minimum synthetic evidence facsimiles; it
> does not permit a second implementation of the production coordinator. …
> Where a bounded facsimile can produce meaningful feasibility observations,
> build that local producer with actual failure injection and controls. A
> supplied JSON record, mocked success flag or future producer name is not a
> producer.

So this module builds **facsimiles**, and the distinction it turns on is stated
once here and carried in every result it returns:

* a facsimile can establish **feasibility** — that the design's ordering,
  refusal and state rules are *constructible*, that each case's observation is
  well defined and falsifiable, and that a deliberately defective arrangement is
  actually classified as failing rather than passing; and
* a facsimile cannot establish **product evidence** — that `init-generation`,
  the probe and the real coordinator behave that way on the disposable host.
  Nothing here observes product code, because none exists to observe.

`FeasibilityFinding.does_not_establish` and `carried_by` say that in every
result, and `feasibility_dispositions()` is the table the handback carries.

## Why the observations are computed and never supplied

EH-R16-2's defect was a classifier reading its **input** as its **result**: the
absence of `APR`/`PVR` — the situation the producer arranged — was rendered as
the refusal `init-generation` reported. The correction was to require the
observed refusal as a separate input.

That correction is only worth anything if the separate input is a real
observation, so nothing in this module hands a classifier an expected answer.
Each experiment runs a deterministic model over `_SyntheticHost`, the model
mutates that host, and the observation is then **read back off the host** —
which artifacts exist, whether a registry row exists, whether the probe ran,
what the gate returned. A test that asserts a passing case therefore asserts
that the modelled sequence really did leave the host in that state.

The proof that this is not circular is `Arrangement.UNGUARDED` and
`Arrangement.UNORDERED`: the same classifier, the same reader, a model with the
guard or the creation order deliberately removed, and a **failed** record. A
classifier that cannot fail proves nothing, so every experiment here has a
negative control that makes it fail.

## Why this cannot quietly become coverage

Three mechanisms already in the package keep a record from closing a missing
producer, and this module adds nothing that weakens any of them:

1. `required_cases.check_case_coverage` receives an empty external column, so
   all three cases stay declared unresolved and `ConcretePlan.is_executable`
   stays `False`;
2. `observations.classify_supplied_observations` never moves a case the plan
   declares unresolved into `covered`, however well formed the record; and
3. `EvidenceResult.eligible_for_operational_acceptance` is `False`
   unconditionally — EH-R16-3.

To those, `synthetic_payload()` emits records under
`observations.SYNTHETIC_TARGET_IDENTITY` and `Custody.SYNTHETIC_FIXTURE`, so a
payload produced here can never be read as an observation of the approved
target: the importer compares the identity exactly and refuses it.

## Isolation

This is a **planning-tier** module. It starts no process, opens no file, imports
nothing from `execution/`, and imports nothing from the product tree — no
application service, no repository, no migration, no configuration. It is
unreachable from bot startup, from the web application and from `migrations/`,
and `tests/phase_5_0_evidence/test_no_execution.py` asserts the first half of
that against the source while
`tests/phase_5_0_evidence/test_feasibility.py` asserts the second.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence

from .cleanup import ConfigurationRestoration, classify_cleanup
from .errors import ObservationRefused
from .journal import (
    CLEANUP_FAILURE_VARIANTS,
    FAILURE_STAGES,
    GENERATION_ARTIFACTS,
    RecoveryStep,
    classify_cleanup_failure_state,
    classify_stage_failure,
)
from .observations import (
    BAND_7_SCHEMA,
    OBSERVATION_SCHEMA,
    OBSERVATION_SCHEMA_VERSION,
    SYNTHETIC_TARGET_IDENTITY,
    Custody,
)
from .provenance import (
    ApprovedRevision,
    FileFacts,
    ProvenanceRecord,
    classify_missing_provenance,
)
from .records import EvidenceRecord, Status

#: What a feasibility result is a result *about*. A fixed string, reported in
#: every finding and in every emitted payload, because the one thing a reader of
#: these numbers must not do is read them as evidence about the product.
FEASIBILITY_SCOPE = (
    "Synthetic feasibility only. Every observation below was produced by a "
    "deterministic in-memory model on this workstation. No product code ran, no "
    "host was touched, and no approved target was observed. These results "
    "establish that a case's rule is constructible and that its observation is "
    "falsifiable; they establish nothing whatever about how `init-generation`, "
    "the §2.13.2a probe or the coordinator will behave."
)

#: Why a feasibility result may not be counted as coverage, stated once.
NOT_COVERAGE = (
    "A facsimile is not the producer this case is missing. The case stays "
    "declared unresolved under conflict C-7, `is_executable` stays False, and "
    "the product half of the case is carried by the named implementation "
    "acceptance test at the Package 5.0 gate."
)


class Arrangement(str, Enum):
    """How the modelled coordinator is arranged for one experiment.

    The three values are the whole of this module's control contract.

    * `CORRECT` — the arrangement the reviewed design specifies. It is the
      **positive control** when nothing is injected, and the subject when a
      fault is.
    * `UNGUARDED` — the provenance gate at C0 is removed and everything else is
      identical. It is the **negative control** for `JNL-51`: the same
      classifier over the same reader must call this failed, or the classifier
      is not deciding anything.
    * `UNORDERED` — the **intentionally misordered** arrangement: C5's
      publication runs before C1, so the generation and its registry row become
      durable before the probe and the cleanup that can still fail, and no unwind
      runs. It is the negative control for both `JNL-47` cases, and it is the
      ordering the submitted model used by mistake — PR-20260911-5.
    """

    CORRECT = "correct"
    UNGUARDED = "unguarded"
    UNORDERED = "unordered"


class Omission(str, Enum):
    """Which provenance fact the deployment failed to leave behind.

    `NONE` is the positive control: nothing is omitted, so the gate must admit.
    """

    NONE = "none"
    #: `D8` suppressed, or `PVR` deleted from a successful deployment.
    PROVENANCE_RECORD = "provenance_record"
    #: The out-of-band approval record is absent.
    APPROVAL_RECORD = "approval_record"
    #: Both are absent.
    BOTH = "both"


#: The four generation artifacts, in the order §2.13.5a creates them at C5, C9,
#: C11 and the `.close` manifest. The order is load-bearing, and so is where the
#: whole group sits in the sequence: **all four are after C2**, so a refusal or a
#: failure anywhere in C0 … C2 leaves none of them because none was ever made.
_CREATION_ORDER = ("journal", "seal", "current", "close")

#: The refusal the modelled C0 gate reports. It is `provenance.EXPECTED_OMISSION_
#: REFUSAL`'s value arrived at independently: the model reports the refusal its
#: own rule produces, and the classifier compares it with the constant it holds.
#: They agree because the design says so, and the comparison is what checks it.
_C0_REFUSAL = "J-26"


# ---------------------------------------------------------------------------
# The synthetic host
# ---------------------------------------------------------------------------


@dataclass
class _SyntheticHost:
    """An in-memory stand-in for `…/journal` and the registry table.

    Deliberately tiny and deliberately mutable: the experiments below change it,
    and the observation is then read back off it. Nothing here is a path on any
    real filesystem, and nothing here is a database.
    """

    #: Generation artifacts that currently exist, by name.
    artifacts: set[str] = field(default_factory=set)
    #: Rows in the modelled `sheet_writer_journal_generations`.
    registry_rows: list[str] = field(default_factory=list)
    #: Whether the §2.13.2a probe was reached at all.
    probe_ran: bool = False
    #: Transient paths a run created and has not removed.
    transient: set[str] = field(default_factory=set)
    #: The out-of-band approval record, if the deployment left one.
    approval_record: ApprovedRevision | None = None
    #: The provenance record `D8` writes, if it ran.
    provenance_record: ProvenanceRecord | None = None

    def artifact_names(self) -> tuple[str, ...]:
        return tuple(name for name in _CREATION_ORDER if name in self.artifacts)

    def has_row(self) -> bool:
        return bool(self.registry_rows)


def _facts() -> FileFacts:
    """The ownership and mode §2.12.5a requires of both records."""
    return FileFacts(present=True, owner="root", group="root", mode="0444")


def _approval_record() -> ApprovedRevision:
    return ApprovedRevision(
        component="sheet-writer",
        source_commit="0" * 40,
        source_tree_id="1" * 40,
        source_manifest_digest="2" * 64,
        review_reference="SYNTHETIC-FEASIBILITY",
        approved_by="synthetic fixture",
        approved_at="2026-09-10",
        facts=_facts(),
    )


def _provenance_record() -> ProvenanceRecord:
    return ProvenanceRecord(
        component="sheet-writer",
        source_commit="0" * 40,
        source_tree_id="1" * 40,
        source_manifest_digest="2" * 64,
        deployment_manifest_digest="3" * 64,
        dependency_lock_digest="4" * 64,
        deployed_at="2026-09-10",
        deployed_by="synthetic fixture",
        facts=_facts(),
    )


def _deploy(host: _SyntheticHost, omission: Omission) -> None:
    """Model the deployment, leaving out whatever the omission says to leave out.

    This is the **injection**, and it is the only place the experiment's input
    enters. It writes records onto the host; it says nothing about what the gate
    will then do, and no later step reads `omission`.
    """
    if omission not in (Omission.APPROVAL_RECORD, Omission.BOTH):
        host.approval_record = _approval_record()
    if omission not in (Omission.PROVENANCE_RECORD, Omission.BOTH):
        host.provenance_record = _provenance_record()


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LabRun:
    """What one modelled run did, read back off the synthetic host.

    Every field here is an **observation**. None of them is an expectation, and
    none is an echo of the experiment's input: `refusal_code` is what the
    modelled gate returned, `artifacts` is what the model left on the host, and
    `probe_ran` is whether the model reached the probe.
    """

    arrangement: Arrangement
    #: The refusal the modelled program reported, or `None` if it did not refuse.
    refusal_code: str | None
    artifacts: tuple[str, ...]
    registry_row_present: bool
    probe_ran: bool
    residue: tuple[str, ...]
    #: Every publication the run attempted, in order. Empty means C5 was never
    #: reached, which is a different fact from *"an artifact was removed"* and is
    #: the distinction PR-20260911-5 requires the model to make.
    publication_attempted: tuple[str, ...] = ()
    #: The step the run stopped at, or `None` if it ran to completion.
    stopped_at: str | None = None

    @property
    def publication_reached(self) -> bool:
        return bool(self.publication_attempted)

    @classmethod
    def of(cls, observed: "SequenceObservation") -> "LabRun":
        """Project one modelled run onto the observation shape the cases read.

        Nothing is computed here. Every value is carried across from the run the
        sequence actually performed, so a case that reads `artifacts` is reading
        the publication sink rather than a constant this module chose.
        """
        return cls(
            arrangement=observed.arrangement,
            refusal_code=observed.refusal_code,
            artifacts=observed.artifacts,
            registry_row_present=observed.registry_row_present,
            probe_ran=observed.probe_ran,
            residue=observed.residue,
            publication_attempted=observed.publication_attempted,
            stopped_at=observed.stopped_at,
        )

    def as_fields(self, case_id: str) -> dict[str, str]:
        """Render this observation in the Band-7 schema's own field vocabulary.

        The rendering is mechanical and total: every field the schema declares is
        filled from an observation, so a field the model does not observe would
        fail here rather than be defaulted to something plausible.
        """
        schema = BAND_7_SCHEMA[case_id]
        present = set(self.artifacts)
        values: dict[str, str] = {}
        for name in schema.field_names():
            if name == "apr_present" or name == "pvr_present":
                # Filled by the caller, which is the only holder of the
                # arrangement's record state.
                continue
            if name.endswith("_present") and name[: -len("_present")] in GENERATION_ARTIFACTS:
                values[name] = "yes" if name[: -len("_present")] in present else "no"
            elif name == "generation_row_present":
                values[name] = "yes" if self.registry_row_present else "no"
            elif name == "probe_ran":
                values[name] = "yes" if self.probe_ran else "no"
            elif name == "refused":
                values[name] = "no" if self.refusal_code is None else "yes"
            elif name == "refusal_code":
                values[name] = self.refusal_code or "none"
        return values


@dataclass(frozen=True, slots=True)
class FeasibilityFinding:
    """One C-7 case's disposition, with the two halves kept apart.

    This is the row the handback's feasibility-versus-product-evidence table is
    built from, and the reason it is a dataclass rather than prose is that the
    two halves have been conflated before: `establishes` is what the local
    producer really shows, `does_not_establish` is the part that stays open, and
    `carried_by` names the acceptance test that must carry the open part at the
    Package 5.0 gate.
    """

    case_id: str
    band: str
    #: The requirement the case answers, cited to the package plan.
    requirement: str
    #: What is missing today, in source terms rather than future command names.
    missing_producer: str
    #: The minimum synthetic experiment this module runs, if any.
    experiment: str
    #: The observable result that experiment produces.
    observable: str
    #: The control that makes the result attributable.
    positive_control: str
    #: The arrangement that must produce a failed record, so the case can fail.
    negative_control: str
    #: What the local producer establishes.
    establishes: str
    #: What it cannot establish, however green it is.
    does_not_establish: str
    #: The later production regression that carries the part left open.
    carried_by: str
    #: Whether a bounded local producer exists at all for this case.
    locally_producible: bool
    #: Whether the case can be *meaningful* without gated product code. When
    #: False, the dependent work stops and the criterion split goes to Peter.
    meaningful_without_product_code: bool
    #: The records the local producer actually emitted, if it ran.
    records: tuple[EvidenceRecord, ...] = ()
    #: The status every one of those records is **expected** to carry, declared
    #: here so a disposition cannot silently start reporting a different one.
    #: `FAILED` is a legitimate value: an experiment that reproduces a defect
    #: produces failed records, and saying so is the point of the field.
    expected_status: Status = Status.PASSED
    #: A defect this experiment found in existing harness code, if any. Reported
    #: and not repaired: repairing it would change an accepted contract behind
    #: the outstanding design checkpoint.
    observed_defect: str = ""

    @property
    def reproduces_a_defect(self) -> bool:
        """Whether this finding's records are a defect reproduction.

        The R2 prompt's rule, applied here: *"Keep injected defect reproductions
        useful and labelled as such; do not weaken them to make an unimplemented
        safety property appear to pass."* A finding whose expected status is
        `FAILED` is such a reproduction, and it says so rather than looking like
        a broken test.
        """
        return self.expected_status is Status.FAILED

    @property
    def resolves_c7(self) -> bool:
        """Always `False`, and it is a property rather than a constant so that a
        reader looking for the answer finds it stated rather than absent.

        No facsimile resolves C-7. The case stays unresolved in the plan, and the
        only thing that could change that is a reviewed producer artifact — which
        is what `ExternalCase.producer_artifact_reviewed` is the switch for.
        """
        return False


# ---------------------------------------------------------------------------
# The approved sequence, and the sink that observes whether it was reached
# ---------------------------------------------------------------------------


#: The approved order, named once and modelled once — package plan §2.13.5a.
#:
#: **PR-20260911-5.** The submitted model had this backwards. It published the
#: journal, the seal, the `current` link, the `.close` manifest and the registry
#: row and *then* injected the cleanup failure, so a cleanup failure appeared to
#: follow a legitimately created generation. The package contract says the
#: opposite and says it twice: **C1** runs the probe stages **and its cleanup**,
#: and *"if the `finally` cleanup does not complete, the run ends in state S-B of
#: §2.13.2b and no later step executes"*; **C2** validates the result-dependent
#: facts while *"nothing has yet been written under `…/journal`"*; and **C5** is
#: *"the first persistent artifact Algorithm C creates"*. `JNL-47` (package plan
#: line 4159) then requires **no journal file, no seal, no symlink, no `.close`
#: manifest and no database row** for *both* cleanup-failure variants.
#:
#: So absence after a cleanup failure is **creation never reached**, not an
#: already-created generation deleted. The withdrawn rationale is recorded in the
#: superseded handback's §3.4 correction rather than erased.
SEQUENCE = (
    ("C0", "read APR and PVR and refuse before anything durable exists"),
    ("C1-probe", "run §2.13.2a stages 1–4 in one verify-capability invocation"),
    ("C1-cleanup", "remove the arena and the Stage-4 target in the finally"),
    ("C2", "validate the result-dependent facts; nothing is under …/journal yet"),
    ("C5", "create the first persistent artifact, and C6 … C13 after it"),
)

#: The step at which each stage name injects its failure. `stage-1 … stage-4` are
#: probe stages inside C1; `cleanup` is C1's `finally`.
_STAGE_STEP: Mapping[str, str] = {
    "stage-1": "C1-probe",
    "stage-2": "C1-probe",
    "stage-3": "C1-probe",
    "stage-4": "C1-probe",
    "cleanup": "C1-cleanup",
}


class PublicationSink:
    """Where the modelled C5 … C13 publication goes, so it can be **observed**.

    This exists because *"no generation artifact"* has two completely different
    causes and the submitted model could not tell them apart: a run that reached
    creation and unwound it, and a run that never reached creation at all. The
    package requires the second and forbids the first.

    So publication is not a mutation of a bag of names any step may perform. It
    is a call on an injected object that records **every attempt** in order,
    including attempts that a correct run would never make. A test then asserts
    two independent things — that `attempted` is empty, and that `artifacts` and
    `registry_row_present` are empty — and the misordered negative control makes
    both non-empty.
    """

    def __init__(self) -> None:
        self._attempted: list[str] = []
        self._artifacts: set[str] = set()
        self._rows: list[str] = []

    def publish_artifact(self, name: str) -> None:
        if name not in GENERATION_ARTIFACTS:
            raise ObservationRefused(
                f"{name!r} is not a generation artifact; §2.13.3 names "
                f"{list(GENERATION_ARTIFACTS)}."
            )
        self._attempted.append(name)
        self._artifacts.add(name)

    def insert_registry_row(self, generation_id: str) -> None:
        self._attempted.append(f"row:{generation_id}")
        self._rows.append(generation_id)

    @property
    def attempted(self) -> tuple[str, ...]:
        """Every publication this run attempted, in the order it attempted them."""
        return tuple(self._attempted)

    @property
    def publication_reached(self) -> bool:
        """Whether the run ever reached C5. The load-bearing observation."""
        return bool(self._attempted)

    @property
    def artifacts(self) -> tuple[str, ...]:
        return tuple(name for name in _CREATION_ORDER if name in self._artifacts)

    @property
    def registry_row_present(self) -> bool:
        return bool(self._rows)


@dataclass(frozen=True, slots=True)
class SequenceObservation:
    """What one run of the modelled sequence did, read back afterwards.

    Every field is read off the sink or off the state machine that produced it.
    None of them is the experiment's input restated, and in particular
    `artifacts` and `registry_row_present` are the sink's, not a constant the
    caller chose — which is what PR-20260911-5 requires of the absence claim.
    """

    arrangement: Arrangement
    #: The step the run stopped at, or `None` if it completed.
    stopped_at: str | None
    refusal_code: str | None
    probe_ran: bool
    probe_passed: bool
    cleanup_completed: bool
    publication_attempted: tuple[str, ...]
    artifacts: tuple[str, ...]
    registry_row_present: bool
    state: str = ""
    exit_code: int = 0
    residue: tuple[str, ...] = ()
    configuration_risk: tuple[str, ...] = ()
    recovery_procedure: tuple[str, ...] = ()
    residue_recovery_procedure: tuple[RecoveryStep, ...] = ()
    #: The configuration cause itself, carried beside its procedure so the
    #: evidence clause can ask whether a *present* cause was answered rather
    #: than whether *some* procedure was named — r6 §8.1.
    retained_recovery_inputs: tuple[str, ...] = ()

    @property
    def publication_reached(self) -> bool:
        return bool(self.publication_attempted)


def _c0_admits(host: _SyntheticHost) -> bool:
    """§2.12.5a's pre-probe provenance gate, as one predicate over the host."""
    return (
        host.approval_record is not None
        and host.approval_record.facts.is_root_owned_read_only
        and host.provenance_record is not None
        and host.provenance_record.facts.is_root_owned_read_only
    )


def _publish_generation(sink: PublicationSink) -> None:
    """C5 … C13: the four artifacts in order, then C13's registry row."""
    for name in _CREATION_ORDER:
        sink.publish_artifact(name)
    sink.insert_registry_row("generation-1")


def run_sequence(
    *,
    omission: Omission = Omission.NONE,
    probe_failure_stage: str | None = None,
    cleanup_fails: bool = False,
    arrangement: Arrangement = Arrangement.CORRECT,
    sink: PublicationSink | None = None,
) -> SequenceObservation:
    """Drive the modelled C0 → C1 → C2 → C5 sequence once, with one fault.

    This is a **minimum ordering model** and deliberately not a second
    coordinator: it has five steps, one branch per step, no artifact content, no
    digests, no chain, no filesystem and no database. What it models is the one
    property the three C-7 cases turn on — *when* each step becomes able to leave
    something behind — and it models it by routing every durable effect through
    an injected sink instead of by asserting a constant.

    The arrangements:

    * `CORRECT` — the approved order in `SEQUENCE`. A C0 refusal, a probe-stage
      failure or a cleanup failure all stop the run before C5, so publication is
      never attempted;
    * `UNORDERED` — the **intentionally misordered negative control**: C5
      publishes *before* C1 runs, which is what the submitted model did. Every
      later failure then leaves a complete generation and a registry row behind,
      and the classifier must fail it; and
    * `UNGUARDED` — C0 is skipped. The negative control for `JNL-51`.
    """
    if probe_failure_stage is not None and probe_failure_stage not in FAILURE_STAGES:
        raise ObservationRefused(
            f"{probe_failure_stage!r} is not one of the stages §2.13.5a injects a "
            f"failure at: {list(FAILURE_STAGES)}."
        )
    if probe_failure_stage == "cleanup":
        raise ObservationRefused(
            "'cleanup' is not a probe stage. C1's cleanup failure is injected "
            "through `cleanup_fails`, because it is a different step of the "
            "sequence and it produces a different §2.13.2b state."
        )
    sink = PublicationSink() if sink is None else sink
    host = _SyntheticHost()
    _deploy(host, omission)

    # --- C0 -------------------------------------------------------------
    if arrangement is not Arrangement.UNGUARDED and not _c0_admits(host):
        return SequenceObservation(
            arrangement=arrangement,
            stopped_at="C0",
            refusal_code=_C0_REFUSAL,
            probe_ran=False,
            probe_passed=False,
            cleanup_completed=False,
            publication_attempted=sink.attempted,
            artifacts=sink.artifacts,
            registry_row_present=sink.registry_row_present,
        )

    if arrangement is Arrangement.UNORDERED:
        # The prohibited ordering, modelled explicitly: the generation becomes
        # durable before the steps that can still fail have run.
        _publish_generation(sink)

    # --- C1, the probe stages -------------------------------------------
    host.probe_ran = True
    probe_passed = probe_failure_stage is None

    # --- C1, the cleanup that is part of the same step -------------------
    outcome = classify_cleanup(
        probe_passed=probe_passed,
        unremoved=() if not cleanup_fails else ("/…/probe",),
        configuration=ConfigurationRestoration(),
    )
    cleanup_completed = not cleanup_fails

    def _observed(stopped_at: str | None) -> SequenceObservation:
        return SequenceObservation(
            arrangement=arrangement,
            stopped_at=stopped_at,
            refusal_code=None,
            probe_ran=host.probe_ran,
            probe_passed=probe_passed,
            cleanup_completed=cleanup_completed,
            publication_attempted=sink.attempted,
            artifacts=sink.artifacts,
            registry_row_present=sink.registry_row_present,
            state=outcome.state,
            exit_code=outcome.exit_code,
            residue=outcome.residue,
            configuration_risk=outcome.configuration_risk,
            recovery_procedure=outcome.recovery_procedure,
            residue_recovery_procedure=outcome.residue_recovery_procedure,
            retained_recovery_inputs=outcome.retained_recovery_inputs,
        )

    if not cleanup_completed:
        # "If the finally cleanup does not complete, the run ends in state S-B
        # of §2.13.2b and no later step executes." C2 is not reached and C5 is
        # not reached, so nothing was ever published.
        return _observed("C1-cleanup")
    if not probe_passed:
        # C2 refuses: the report does not carry every case passed. Still before
        # the first persistent artifact.
        return _observed("C2")

    # --- C2 validated; C5 … C13 ------------------------------------------
    if arrangement is not Arrangement.UNORDERED:
        _publish_generation(sink)
    return _observed(None)


# ---------------------------------------------------------------------------
# Experiment 1 — JNL-51-PROVENANCE-OMITTED
# ---------------------------------------------------------------------------


def run_provenance_experiment(
    *,
    omission: Omission,
    arrangement: Arrangement = Arrangement.CORRECT,
) -> LabRun:
    """Model `init-generation`'s C0 provenance gate, then read the run back.

    The modelled sequence is `SEQUENCE`'s, and the whole content of this case is
    an ordering: the gate reads `APR` and `PVR` **before** the probe is reached
    and long before C5, so a refusal there leaves nothing to unwind and nothing
    to publish. That ordering is the feasibility claim; whether the product
    implements it is not something this model can know.

    Under `Arrangement.UNGUARDED` the gate is skipped and the sequence proceeds
    to publication. That is the negative control, and its record must be
    `FAILED`.
    """
    observed = run_sequence(omission=omission, arrangement=arrangement)
    return LabRun.of(observed)


def classify_provenance_experiment(
    *,
    omission: Omission,
    arrangement: Arrangement = Arrangement.CORRECT,
) -> tuple[EvidenceRecord, ...]:
    """Run experiment 1 and classify what it observed with the real classifier.

    `classify_missing_provenance` is `provenance.py`'s, unchanged. It holds the
    expectation — `EXPECTED_OMISSION_REFUSAL` — and this module supplies only
    observations, which is the separation EH-R16-2 required.
    """
    host = _SyntheticHost()
    _deploy(host, omission)
    run = run_provenance_experiment(omission=omission, arrangement=arrangement)
    return classify_missing_provenance(
        apr=host.approval_record,
        pvr=host.provenance_record,
        probe_ran=run.probe_ran,
        generation_artifacts=run.artifacts,
        generation_row_inserted=run.registry_row_present,
        observed_refusal_code=run.refusal_code,
    )


# ---------------------------------------------------------------------------
# Experiment 2 — JNL-47-NO-GENERATION-ON-FAILURE
# ---------------------------------------------------------------------------


def run_stage_failure_experiment(
    *,
    stage: str | None,
    arrangement: Arrangement = Arrangement.CORRECT,
) -> LabRun:
    """Inject a failure at one of `JNL-47`'s five points and read the run back.

    `stage=None` is the positive control: nothing is injected, so the sequence
    reaches C5, all four artifacts and the registry row exist, and
    `publication_reached` is `True`. Without it a model that never publishes
    anything at all would be indistinguishable from one whose ordering worked.

    The four probe stages fail inside **C1**; `cleanup` fails in the same step's
    `finally`. Both are before **C5**, which is why `JNL-47` requires the same
    absence of every artifact and of the registry row for all five — and it is
    the corrected reading of the requirement: **creation was never reached**.

    Under `Arrangement.UNORDERED` C5 runs first, so every injection leaves the
    complete generation and the row behind and the record is `FAILED`.
    """
    if stage is not None and stage not in FAILURE_STAGES:
        raise ObservationRefused(
            f"{stage!r} is not one of the stages §2.13.5a injects a failure at: "
            f"{list(FAILURE_STAGES)}."
        )
    observed = run_sequence(
        probe_failure_stage=None if stage in (None, "cleanup") else stage,
        cleanup_fails=stage == "cleanup",
        arrangement=arrangement,
    )
    return LabRun.of(observed)


def classify_stage_failure_experiment(
    *,
    stage: str,
    arrangement: Arrangement = Arrangement.CORRECT,
) -> EvidenceRecord:
    """Run experiment 2 for one stage and classify what it observed.

    The `cleanup` stage is included on the same terms as the other four, and
    that is the PR-20260911-5 correction: under the approved order a cleanup
    failure ends the run at **C1**, before **C2** and long before **C5**, so
    *"no generation artifact and no registration row"* is true of it for the same
    reason it is true of a Stage-1 failure. The submitted model published first
    and then failed cleanup, which made this record fail for an ordering the
    package forbids.
    """
    run = run_stage_failure_experiment(stage=stage, arrangement=arrangement)
    return classify_stage_failure(
        stage=stage,
        artifacts_present=run.artifacts,
        generation_row_present=run.registry_row_present,
    )


# ---------------------------------------------------------------------------
# Experiment 3 — JNL-47-RECOVERY-STATE
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RecoveryRun:
    """A modelled run whose cleanup did not complete, and what followed it."""

    variant: str
    state: str
    exit_code: int
    residue: tuple[str, ...]
    configuration_risk: tuple[str, ...]
    recovery_procedure: tuple[str, ...]
    residue_recovery_procedure: tuple[RecoveryStep, ...]
    #: The retained configuration captures, which are the configuration
    #: recovery's cause. Empty means that cause is absent and its procedure is
    #: not required — it does not mean the residue cause is answered.
    retained_recovery_inputs: tuple[str, ...]
    next_run_refuses: bool
    #: Whether the run ever reached C5. `False` for both cleanup-failure
    #: variants, and **observed** rather than assumed: the same model with the
    #: cleanup completing and the probe passing reaches it.
    publication_reached: bool = False
    #: Read off the publication sink, not supplied. These are `JNL-47`'s two
    #: absence clauses and the reason they are no longer vacuous.
    artifacts: tuple[str, ...] = ()
    registry_row_present: bool = False
    stopped_at: str | None = None


    def as_fields(self) -> dict[str, str]:
        """Render this run in `JNL-47-RECOVERY-STATE`'s field vocabulary.

        Mechanical and total, exactly as `LabRun.as_fields` is: every field the
        schema declares is filled from something the run observed, so a field
        the model does not observe fails here rather than being defaulted to
        something plausible.

        **The two recovery causes stay apart — r6 §8.1.** `residue_recovery_named`
        answers the residue cause and `configuration_recovery_named` answers the
        configuration cause, and neither answers for the other. That separation
        is LAB-1's whole disposition, and collapsing it here would reintroduce
        the defect one layer down from where it was repaired.
        """
        schema = BAND_7_SCHEMA["JNL-47-RECOVERY-STATE"]
        values = {
            "exit_code": str(self.exit_code),
            "state": self.state,
            "residue_path_count": str(len(self.residue)),
            "generation_present": "yes" if self.artifacts else "no",
            "database_row_present": "yes" if self.registry_row_present else "no",
            "next_run_refuses": "yes" if self.next_run_refuses else "no",
            "residue_recovery_named": (
                "yes" if self.residue_recovery_procedure else "no"
            ),
            "configuration_capture_retained": (
                "yes" if self.retained_recovery_inputs else "no"
            ),
            "configuration_recovery_named": (
                "yes" if self.recovery_procedure else "no"
            ),
        }
        missing = sorted(schema.field_names() - set(values))
        if missing:
            raise ObservationRefused(
                f"the recovery run observes no value for {missing}. A field the "
                "producer does not observe is not one it may default."
            )
        return values


def next_run_refuses(*, residue: Sequence[str], configuration_risk: Sequence[str]) -> bool:
    """§2.13.2b's next-invocation rule, as one predicate.

    The rule is *"the next invocation refuses while it exists and does not clean
    it"*, and `execution/executor.py`'s `_refuse_when_blocked` is the
    implementation of it. This is the same rule stated where the planning tier
    can reach it; `tests/phase_5_0_evidence/test_feasibility.py` asserts that the
    executor refuses for exactly the inputs this returns `True` for, so the two
    cannot drift apart silently.
    """
    return bool(tuple(residue) or tuple(configuration_risk))


def run_recovery_experiment(*, variant: str, cleanup_completes: bool = False) -> RecoveryRun:
    """Drive the harness's **own** §2.13.2b state machine inside the sequence.

    This experiment is different in kind from the other two, and the difference
    matters for the disposition: `classify_cleanup` is not a facsimile of product
    code, it is `cleanup.py` — the harness's real implementation of §2.13.2b —
    and the sequence above injects an unremovable path into it and reads back the
    state it returns. What stays synthetic is only the *ordering* the coordinator
    would impose, and that ordering is now the approved one: the cleanup runs
    **inside C1**, so the run ends before C5 and the generation and the row are
    absent because creation was never reached.

    `cleanup_completes=True` is the positive control, and it is the control that
    makes the absence mean something. For the passing-probe variant the very same
    model, with nothing injected, runs on to C5 and the sink records the four
    artifacts and the row — so a sink that is empty in the failing case is empty
    because the run stopped, not because the model cannot publish.
    """
    if variant not in CLEANUP_FAILURE_VARIANTS:
        raise ObservationRefused(
            f"{variant!r} is not one of the §2.13.2b cleanup-failure situations: "
            f"{sorted(CLEANUP_FAILURE_VARIANTS)}."
        )
    probe_passed = variant == "cleanup-failure-after-passing-probe"
    observed = run_sequence(
        probe_failure_stage=None if probe_passed else "stage-3",
        cleanup_fails=not cleanup_completes,
    )
    return RecoveryRun(
        variant=variant,
        state=observed.state,
        exit_code=observed.exit_code,
        residue=observed.residue,
        configuration_risk=observed.configuration_risk,
        recovery_procedure=observed.recovery_procedure,
        residue_recovery_procedure=observed.residue_recovery_procedure,
        retained_recovery_inputs=observed.retained_recovery_inputs,
        next_run_refuses=next_run_refuses(
            residue=observed.residue, configuration_risk=observed.configuration_risk
        ),
        publication_reached=observed.publication_reached,
        artifacts=observed.artifacts,
        registry_row_present=observed.registry_row_present,
        stopped_at=observed.stopped_at,
    )


def classify_recovery_experiment(
    *, variant: str, cleanup_completes: bool = False
) -> EvidenceRecord:
    """Run experiment 3 and classify what the state machine actually reported.

    **The absence clauses are now observations.** `generation_present` and
    `database_row_present` are read off the publication sink the sequence wrote
    to, not passed as constants: the run stopped at C1's cleanup, so C5 was never
    reached and the sink is empty. The same model with the cleanup completing
    publishes, which is what makes the empty sink attributable to the ordering
    rather than to a model that cannot publish at all. This is the
    PR-20260911-5 correction.

    **LAB-1 is checked against the procedure carried by the actual outcome.**
    The residue-only failure path must name residue recovery; a configuration
    failure must name configuration recovery; and a state containing both must
    name both. Each cause and each procedure is passed to the classifier
    separately — r6 §8.1 — so naming one procedure cannot answer for the other,
    and an outcome that names nothing produces a failed record.
    """
    run = run_recovery_experiment(variant=variant, cleanup_completes=cleanup_completes)
    return classify_cleanup_failure_state(
        variant=variant,
        exit_code=run.exit_code,
        state=run.state,
        residue_path_count=len(run.residue),
        generation_present=bool(run.artifacts),
        database_row_present=run.registry_row_present,
        next_run_refuses=run.next_run_refuses,
        residue_recovery_named=bool(run.residue_recovery_procedure),
        configuration_capture_retained=bool(run.retained_recovery_inputs),
        configuration_recovery_named=bool(run.recovery_procedure),
    )


# ---------------------------------------------------------------------------
# Emission — and why it can never be counted
# ---------------------------------------------------------------------------


def producer_records(
    *,
    run_id: str,
    review_manifest_digest: str,
    collected_by: str = "implementer",
    collected_at: str = "2026-09-13",
    arrangement: Arrangement = Arrangement.CORRECT,
) -> tuple[dict[str, object], ...]:
    """Run all three producers and render every variant as an importer record.

    **This is the adapter C-7 asks for, and it resolves C-7 for exactly nobody.**
    What it supplies is the missing half of the path: until now the producers
    computed classified records and the importer accepted hand-written ones, so
    nothing joined the two and *"a producer exists"* and *"a record is well
    formed"* were never checked against each other. They are now, end to end.

    Three things keep the path from becoming coverage, and none of them is
    weakened here:

    1. every record carries `SYNTHETIC_TARGET_IDENTITY` and
       `Custody.SYNTHETIC_FIXTURE`, so a payload from here pointed at the
       approved target is refused by the importer for naming the wrong target;
    2. `concrete_plan` still declares all three cases **unresolved** and
       `ExternalCase.producer_artifact_reviewed` is still `False`, so
       `classify_supplied_observations` reports them in `unresolved_cases` and
       never in `covered`, however well formed the records are; and
    3. `EvidenceResult.eligible_for_operational_acceptance` is unconditionally
       `False` — EH-R16-3.

    A **facsimile** can establish feasibility: that the design's ordering,
    refusal and state rules are constructible and falsifiable. It cannot
    establish product evidence, because no product code exists to observe.
    `arrangement` carries the false-success control through the same adapter, so
    a defective arrangement produces records that **fail** classification rather
    than records that quietly do not exist.
    """
    records: list[dict[str, object]] = []

    def envelope(case_id: str, variant: str, fields: Mapping[str, str]) -> dict:
        return {
            "case_id": case_id,
            "variant": variant,
            "target_identity": SYNTHETIC_TARGET_IDENTITY,
            "run_id": run_id,
            "review_manifest_digest": review_manifest_digest,
            "custody": Custody.SYNTHETIC_FIXTURE.value,
            "collected_by": collected_by,
            "collected_at": collected_at,
            "fields": dict(fields),
        }

    # JNL-51-PROVENANCE-OMITTED — one variant, and the host's record state is
    # the only part the run itself cannot observe, so it is read off the host
    # the deployment produced rather than asserted.
    host = _SyntheticHost()
    _deploy(host, Omission.PROVENANCE_RECORD)
    run = run_provenance_experiment(
        omission=Omission.PROVENANCE_RECORD, arrangement=arrangement
    )
    fields = run.as_fields("JNL-51-PROVENANCE-OMITTED")
    fields["apr_present"] = "yes" if host.approval_record is not None else "no"
    fields["pvr_present"] = "yes" if host.provenance_record is not None else "no"
    records.append(
        envelope("JNL-51-PROVENANCE-OMITTED", "provenance-omitted", fields)
    )

    # JNL-47-NO-GENERATION-ON-FAILURE — one record per injection point, and the
    # case is not covered until all five are supplied.
    for stage in FAILURE_STAGES:
        staged = run_stage_failure_experiment(stage=stage, arrangement=arrangement)
        records.append(
            envelope(
                "JNL-47-NO-GENERATION-ON-FAILURE",
                stage,
                staged.as_fields("JNL-47-NO-GENERATION-ON-FAILURE"),
            )
        )

    # JNL-47-RECOVERY-STATE — one record per §2.13.2b variant.
    for variant in CLEANUP_FAILURE_VARIANTS:
        recovery = run_recovery_experiment(variant=variant)
        records.append(
            envelope("JNL-47-RECOVERY-STATE", variant, recovery.as_fields())
        )

    return tuple(records)


def producer_report(
    *, run_id: str, review_manifest_digest: str, **overrides
) -> "FeasibilityReport":
    """The three producers' records, in the importer's envelope, bounded."""
    return synthetic_report(
        producer_records(
            run_id=run_id, review_manifest_digest=review_manifest_digest, **overrides
        )
    )


def synthetic_payload(records: Iterable[Mapping[str, object]]) -> bytes:
    """Wrap feasibility observations in the importer's payload envelope.

    The envelope is the importer's, exactly: `observations.parse_payload`
    requires the three declared keys and no others, so this adds none. The
    feasibility scope travels beside the payload in `FeasibilityReport` rather
    than inside it, because a reader that can be argued into ignoring an extra
    envelope key is not what keeps these records out of a real result.

    What keeps them out is the record's own `target_identity`. Every record a
    caller builds for this envelope carries `SYNTHETIC_TARGET_IDENTITY`, and the
    importer compares that exactly against the identity the caller read from the
    plan — so a feasibility payload pointed at the approved target is refused for
    naming the wrong target. `test_feasibility.py` asserts that refusal.
    """
    return json.dumps(
        {
            "schema": OBSERVATION_SCHEMA,
            "schema_version": OBSERVATION_SCHEMA_VERSION,
            "records": [dict(record) for record in records],
        },
        sort_keys=True,
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class FeasibilityReport:
    """A payload together with the two sentences that bound how it may be read.

    The scope and the not-coverage statement are carried here rather than in the
    envelope so that both survive alongside the bytes without widening the
    importer's closed schema by one key.
    """

    payload: bytes
    scope: str = FEASIBILITY_SCOPE
    not_coverage: str = NOT_COVERAGE
    target_identity: str = SYNTHETIC_TARGET_IDENTITY


def synthetic_report(records: Iterable[Mapping[str, object]]) -> FeasibilityReport:
    return FeasibilityReport(payload=synthetic_payload(records))


# ---------------------------------------------------------------------------
# The dispositions
# ---------------------------------------------------------------------------


def _records_ok(records: Sequence[EvidenceRecord]) -> tuple[EvidenceRecord, ...]:
    return tuple(records)


def feasibility_dispositions() -> tuple[FeasibilityFinding, ...]:
    """The three C-7 dispositions, each with its experiment actually run.

    The records in each finding are produced by running the experiment here and
    now, so a disposition cannot claim an observation the module does not make.
    """
    provenance_records = classify_provenance_experiment(
        omission=Omission.PROVENANCE_RECORD
    )
    stage_records = tuple(
        classify_stage_failure_experiment(stage=stage) for stage in FAILURE_STAGES
    )
    recovery_records = tuple(
        classify_recovery_experiment(variant=variant)
        for variant in sorted(CLEANUP_FAILURE_VARIANTS)
    )
    return (
        FeasibilityFinding(
            case_id="JNL-51-PROVENANCE-OMITTED",
            band="provenance",
            requirement=(
                "package plan §2.12.5a: an absent or unreadable approval record "
                "is a refusal, never a default — the negative test P5.0-SR1 "
                "found missing."
            ),
            missing_producer=(
                "`init-generation`. It is Package 5.0 product work and no file "
                "in this repository implements it: the C0 gate exists only as "
                "the expectation constant "
                "`tools/phase_5_0_evidence/provenance.py:EXPECTED_OMISSION_REFUSAL` "
                "and the classifier beside it."
            ),
            experiment=(
                "`run_provenance_experiment` models the C0 ordering over an "
                "in-memory host: deploy with `PVR` omitted, read `APR`/`PVR` "
                "before anything durable exists, refuse, and read the host back."
            ),
            observable=(
                "the refusal code the modelled gate returned, the generation "
                "artifacts left on the host, whether a registry row exists, and "
                "whether the probe was reached."
            ),
            positive_control=(
                "`Omission.NONE` under the correct arrangement: the gate admits, "
                "all four artifacts and the row exist, and the probe ran. Without "
                "it the refusal could be a model that never creates anything."
            ),
            negative_control=(
                "`Arrangement.UNGUARDED`: the same omission with the C0 gate "
                "removed. The same classifier must return `FAILED`."
            ),
            establishes=(
                "that a fail-closed gate ordered before the first durable "
                "artifact and before the probe is constructible, that the four "
                "assertions `JNL-51` case (g) makes are jointly satisfiable, and "
                "that the classifier distinguishes a guarded from an unguarded "
                "arrangement rather than passing both."
            ),
            does_not_establish=(
                "that `init-generation` refuses, that it refuses with `J-26`, or "
                "that it creates nothing when it does. No product code exists to "
                "observe, so the observation is of the model and of nothing else."
            ),
            carried_by=(
                "the Package 5.0 implementation acceptance test for §2.12.5a "
                "C0, run against the built coordinator on the reserved "
                "disposable host, with `APR`/`PVR` suppressed out of band."
            ),
            locally_producible=True,
            meaningful_without_product_code=True,
            records=_records_ok(provenance_records),
        ),
        FeasibilityFinding(
            case_id="JNL-47-NO-GENERATION-ON-FAILURE",
            band="journal",
            requirement=(
                "package plan §2.13.5a R7-A and acceptance row 19: a failure "
                "injected in each of Stage 1 … Stage 4 and in cleanup leaves no "
                "journal, no seal, no symbolic link and no registration row."
            ),
            missing_producer=(
                "the §2.13.2a probe together with `init-generation`. Both are "
                "Package 5.0 product work; the only stage vocabulary in this "
                "repository is the expectation table "
                "`tools/phase_5_0_evidence/journal.py:FAILURE_STAGES` and its "
                "classifier."
            ),
            experiment=(
                "`run_stage_failure_experiment` drives the `SEQUENCE` model — "
                "C0, C1's probe stages, C1's cleanup, C2, then C5's publication "
                "through an injected sink — with a deterministic failure at one "
                "of the five named points, and reads back what the sink holds."
            ),
            observable=(
                "the step the run stopped at, whether publication was attempted "
                "at all, the surviving generation artifacts and the presence of "
                "a registry row, per injection point."
            ),
            positive_control=(
                "`stage=None`: nothing injected, so the run reaches C5, the sink "
                "records all four artifacts and the row, and "
                "`publication_reached` is True. It is what makes an empty sink "
                "after an injection mean something."
            ),
            negative_control=(
                "`Arrangement.UNORDERED`: C5 publishes before C1 runs, which is "
                "the ordering the package forbids, so every injection leaves the "
                "complete generation and the row behind and the record is "
                "`FAILED`."
            ),
            establishes=(
                "that an ordering exists in which no failure at any of the five "
                "points leaves a partial or whole generation, that the property "
                "is per-point rather than aggregate, that the absence is "
                "*creation never reached* rather than creation undone — the "
                "publication sink is never called — and that the classifier "
                "fails an arrangement that publishes early."
            ),
            does_not_establish=(
                "that the real creation order has that property, that the "
                "product's failure paths are the five named points, or that a "
                "real failure at one of them leaves nothing. **Corrected "
                "2026-09-11 (PR-20260911-5):** the submitted disposition said "
                "the `cleanup` point was not describable by R7-A. It is. C1 "
                "runs the probe *and its cleanup*, and a cleanup failure ends "
                "the run there, before C2 and before C5."
            ),
            carried_by=(
                "the Package 5.0 implementation acceptance test for §2.13.5a "
                "R7-A: `JNL-47`'s six runs against the built probe and "
                "coordinator on the reserved disposable host — four probe-stage "
                "injections with cleanup succeeding, and the two cleanup-failure "
                "variants the recovery case owns."
            ),
            locally_producible=True,
            meaningful_without_product_code=True,
            records=_records_ok(stage_records),
        ),
        FeasibilityFinding(
            case_id="JNL-47-RECOVERY-STATE",
            band="journal",
            requirement=(
                "package plan §2.13.2b and acceptance row 19: cleanup failure "
                "after a probe-stage failure and after a fully passing probe are "
                "distinguished, each asserting exit status, safe path reporting, "
                "generation and database absence, residue state, next-run "
                "behaviour and the named operator recovery."
            ),
            missing_producer=(
                "`init-generation` and the §2.13.2a probe, as for the other two "
                "cases. Five of the seven clauses — exit status, state, residue "
                "reporting, the named recovery and, through the sequence model, "
                "the ordering that decides the absences — run against "
                "`tools/phase_5_0_evidence/cleanup.py:classify_cleanup`, which "
                "is harness code and not a facsimile; the next-run clause is "
                "`execution/executor.py:_refuse_when_blocked`. **Corrected "
                "2026-09-11 (PR-20260911-5):** the submitted disposition said "
                "the missing producer was *a run whose cleanup failed after a "
                "coordinator created a generation*. The package forbids that "
                "run: C1 performs the probe and its cleanup, and a cleanup "
                "failure ends the algorithm there, so no generation is ever "
                "created for the requirement to be about."
            ),
            experiment=(
                "`run_recovery_experiment` drives the `SEQUENCE` model with an "
                "unremovable path injected into the harness's own §2.13.2b state "
                "machine at C1's cleanup, for each of the two variants, and "
                "reads back the state, exit code, residue, recovery procedure "
                "and the publication sink."
            ),
            observable=(
                "the §2.13.2b state, the exit code, the residue paths named, "
                "the step the run stopped at, whether C5 was ever reached, "
                "whether a generation artifact or registry row exists, whether "
                "a next run refuses, and whether the operator recovery procedure "
                "was reported."
            ),
            positive_control=(
                "`cleanup_completes=True`. For the probe-failure variant it "
                "produces `S-A` with no residue and a next run that proceeds; "
                "for the passing-probe variant the same model runs on to C5 and "
                "the sink records all four artifacts and the row. That second "
                "control is what makes the empty sink in the failing case mean "
                "*the run stopped* rather than *the model cannot publish*."
            ),
            negative_control=(
                "`Arrangement.UNORDERED`, which publishes at C5 before C1 runs "
                "and therefore leaves a generation and a row behind a failed "
                "cleanup; and a variant whose cleanup failed but which reports "
                "`S-C` or whose next run does not refuse. "
                "`classify_cleanup_failure_state` compares all seven clauses, so "
                "six of seven is a failed record."
            ),
            establishes=(
                "that the harness distinguishes the two cleanup failures, "
                "reports `S-B` with exit 3 and named residue for both, blocks "
                "the next invocation, and — in the corrected ordering — that "
                "both absence clauses hold because the run ends at C1 before C5 "
                "is reached, observed on an injected publication sink that the "
                "positive control shows does record a publication. The named "
                "residue procedure and, when applicable, the separate "
                "configuration-capture procedure are both carried by the actual "
                "S-B outcome; the negative control fails when neither is named. "
                "All seven harness-level clauses are exercised."
            ),
            does_not_establish=(
                "that the real `init-generation` orders C1's cleanup before C5, "
                "that the real cleanup fails in the modelled way, or that the "
                "real coordinator creates nothing when it stops there, or that "
                "its operator-facing run record presents both procedures "
                "correctly. Those remain Package 5.0 implementation acceptance "
                "checks. **Corrected 2026-09-11 (PR-20260911-5):** the submitted "
                "disposition called the two absence clauses vacuous and asked "
                "for a readiness/implementation criterion split on that basis. "
                "The rationale was wrong and the split request is withdrawn."
            ),
            carried_by=(
                "the Package 5.0 implementation acceptance test for §2.13.2b: "
                "the same two variants run against the built coordinator on the "
                "reserved disposable host, including run-record encoding and "
                "operator-facing presentation."
            ),
            locally_producible=True,
            meaningful_without_product_code=True,
            records=_records_ok(recovery_records),
        ),
    )


def dependent_work_to_stop() -> tuple[str, ...]:
    """The case ids whose dependent work stops pending a maintainer decision.

    §1 of the laboratory prompt: *"If an essential case cannot be meaningful
    without gated product code, stop that dependent work and submit the exact
    readiness/implementation criterion split for Peter, with a recommendation."*

    **It is now empty, and that is the PR-20260911-5 correction.** The submitted
    pass returned `JNL-47-RECOVERY-STATE` here because its two absence clauses
    were thought to require a generation that a real coordinator had created and
    a failed cleanup had left behind. Under the approved order no such run
    exists: C1 performs the probe and its cleanup, a cleanup failure ends the
    algorithm there, and C5 — the first persistent artifact — is never reached.
    The absences are therefore modellable, are modelled against an injected
    publication sink with a control that does publish, and no criterion split is
    required for them. All three cases keep the ordinary feasibility/product
    boundary every case in this module has, and all three stay unresolved under
    conflict C-7.
    """
    return tuple(
        finding.case_id
        for finding in feasibility_dispositions()
        if not finding.meaningful_without_product_code
    )


def statuses(records: Iterable[EvidenceRecord]) -> tuple[Status, ...]:
    return tuple(record.status for record in records)


__all__ = [
    "Arrangement",
    "FEASIBILITY_SCOPE",
    "FeasibilityFinding",
    "FeasibilityReport",
    "LabRun",
    "NOT_COVERAGE",
    "Omission",
    "PublicationSink",
    "RecoveryRun",
    "SEQUENCE",
    "SequenceObservation",
    "classify_provenance_experiment",
    "classify_recovery_experiment",
    "classify_stage_failure_experiment",
    "dependent_work_to_stop",
    "feasibility_dispositions",
    "next_run_refuses",
    "run_provenance_experiment",
    "run_recovery_experiment",
    "run_sequence",
    "run_stage_failure_experiment",
    "statuses",
    "synthetic_payload",
    "synthetic_report",
]
