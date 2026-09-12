"""Conflict **C-7**: the supplied-observation importer, and the Band-7
classification it feeds — R16.

## The finding, and why an importer is the answer to only half of it

R13's Blocking finding **EH-R13-4** was that Band 7 produced nothing at all and
declared nothing unresolved. Its classifiers — `provenance`, `journal` and
`manifest` — are pure functions over observations somebody supplies, and no step
and no stage of the CLI supplied any. A scripted run could therefore be
classified complete with the whole provenance, journal-generation and recovery
band missing.

R14 declared the three cases unresolved rather than approximating them, and said
what would resolve it: *"a bounded supplied-observation ingestion stage — where
reviewed observations enter, what validates them against the record schema before
anything classifies them, and what stops that input reaching the component that
constructs the process boundary."* The maintainer approved that on 2026-09-09.

**An importer cannot supply experimental evidence.** That is the half an
ingestion stage does not answer, and it is stated here before the mechanism: a
correctly shaped record is a record, not an experiment. So this module reports,
for every required case, **which producer actually makes the observation** and
whether that producer exists — and `import_observations` refuses to call a case
covered when its producer is missing, however well-formed the record is.

## What a supplied record may say, and what it structurally cannot

There is no free text in this schema. A record names a case and a variant from
the closed table below, and carries exactly that variant's declared fields, each
matched against the closed shape its field can have. Consequently a record
**cannot**:

* select a command, an executable, an interpreter or an argument vector — no
  field is a path, a program or an argument, and this module builds none;
* select a process identity, a uid, a gid or a capability set — no field is one;
* select a target path, a database, a role or a unit — the plan names those and
  a record cannot;
* supply an approval token or a reviewed digest — `import_observations` takes
  the target identity, the run identifier and the manifest digest **from its
  caller** and refuses a record that disagrees with them, so the record can only
  ever fail to match a value it did not choose;
* supply a reviewed *expected* value — every expectation below comes from the
  band classifier's own constants, and there is no path by which a record
  reaches one; or
* construct anything that can start a process. This module is in the planning
  tier: it imports no boundary, no executor and no materializer, opens no file
  and names no process. `tests/phase_5_0_evidence/test_no_execution.py` asserts
  all of that against its syntax tree, and asserts that the entry point which
  *does* read a file — `execution/evidence_cli.py` — imports none of the three
  execution-tier modules that can act on the host.

## Provenance and custody — because target, run and digest authenticate nothing

A record that carries the right target identity, the right run identifier and the
right manifest digest has demonstrated that whoever wrote it had read the plan.
It has not demonstrated where the observation came from. So every record declares
its **custody**, from a closed vocabulary, and the vocabulary is ordered by what
it is worth:

| Custody | What it asserts | Operationally acceptable? |
|---|---|---|
| `synthetic_fixture` | this observation was written to exercise the classifier | **never.** It is a fixture, and it says so in every record it produces |
| `operator_attested` | a named operator ran the collection procedure and reports the result | **no.** An attestation is a person's claim, and this harness cannot check it |
| `reviewer_verified` | the independent reviewer verified the observation against the producer's own output | **yes**, and only then |

`EvidenceResult.structural_disqualifications` names every reason the **in-scope**
half would not qualify: a record that is not `reviewer_verified`, a synthetic
fixture, an uncovered variant, a case the plan still declares unresolved, a
classified record that did not pass. It is a report, not an approval.

**`eligible_for_operational_acceptance` is `False` unconditionally — R16,
EH-R16-3.** This importer holds Band 7 and nothing else; the capability cases and
their controls are produced by the executed plan and are not in this result, so
the question cannot be answered from these inputs and is withheld rather than
answered from the half that is here. `EvidenceResult.outside_scope` lists what is
missing from the question, and `EvidenceResult.withheld` states the position.

**Synthetic fixtures stay visibly synthetic.** A synthetic record's custody is in
the record it produces, its `target_identity` is stamped with the synthetic
marker, and `EvidenceResult.synthetic` is true for the whole result. There is no
combination of fields that makes a synthetic record indistinguishable from an
operational one, because the custody is not a field the classifier ignores.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from enum import Enum
from typing import Any, Mapping, Sequence

from .errors import ObservationRefused
from .journal import (
    classify_cleanup_failure_state,
    classify_stage_failure,
)
from .provenance import (
    ApprovedRevision,
    FileFacts,
    ProvenanceRecord,
    classify_missing_provenance,
)
from .records import EvidenceRecord
from .required_cases import REQUIRED_CASES

#: The schema name a supplied observation is written under. Changing what a
#: record *means* changes this string, so a payload produced under an older
#: meaning is refused rather than silently reinterpreted.
OBSERVATION_SCHEMA = "freedom-blades/phase-5.0/supplied-observation"

#: Bumped when the field set or the case table changes.
#:
#: **2** is R16's disposition of **EH-R16-2**. `JNL-51-PROVENANCE-OMITTED` gains
#: `refused`, and its `refusal_code` admits the value `none`, so a record can say
#: *"the program did not refuse"* — a result the version-1 schema could not
#: express, which is why the classifier inferred one. A version-1 payload is
#: refused rather than read under the new meaning.
OBSERVATION_SCHEMA_VERSION = 2

#: The marker a synthetic fixture's target identity carries, so a synthetic
#: record can never be read as an observation of the approved target. It is
#: compared exactly, like every other identity: a fixture that omitted it would
#: be refused for naming the wrong target rather than quietly accepted.
SYNTHETIC_TARGET_IDENTITY = "SYNTHETIC-FIXTURE"

#: The most records one payload may carry. Bounded for the reason every other
#: limit in this package is: an input surface with no bound is an input surface
#: whose worst case nobody reviewed.
MAX_RECORDS = 64

#: The longest a payload may be, in bytes.
MAX_PAYLOAD_BYTES = 256 * 1024


class Custody(str, Enum):
    """Where a supplied observation came from, from a closed vocabulary."""

    SYNTHETIC_FIXTURE = "synthetic_fixture"
    OPERATOR_ATTESTED = "operator_attested"
    REVIEWER_VERIFIED = "reviewer_verified"


#: The shapes a supplied field value may have. As narrow as `capture._SHAPES`,
#: and for the same reason: a value that is not the shape its field can
#: legitimately have is not an observation of that field.
_SHAPES: Mapping[str, re.Pattern[str]] = {
    "yes_no": re.compile(r"\A(?:yes|no)\Z"),
    "count": re.compile(r"\A[0-9]{1,6}\Z"),
    "refusal_code": re.compile(r"\A(?:J|SW-J|DEP)-[0-9]{2}\Z"),
    # **R16, EH-R16-2.** A refusal code, or the literal `none` meaning the
    # program was observed **not** to refuse. `none` is a value the comparison
    # can fail against; an omitted field would be an unmade observation, and the
    # exact-key rule refuses that separately.
    "refusal_code_or_none": re.compile(r"\A(?:(?:J|SW-J|DEP)-[0-9]{2}|none)\Z"),
    "cleanup_state": re.compile(r"\AS-[ABC]\Z"),
    "exit_code": re.compile(r"\A[0-9]{1,3}\Z"),
}


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """One field a variant declares, and the shape its value may have."""

    name: str
    shape: str

    def __post_init__(self) -> None:
        if self.shape not in _SHAPES:
            raise ObservationRefused(
                f"Field {self.name!r} declares shape {self.shape!r}, which is not "
                f"one of {sorted(_SHAPES)}."
            )


@dataclass(frozen=True, slots=True)
class CaseSchema:
    """One required case: its variants, its fields, and **who produces it**.

    `producer` and `collection_procedure` are the part an importer cannot
    substitute for. They say which actor makes the observation and by what
    procedure, so a reviewer reads *"this record came from a run of
    `init-generation` with the provenance record removed"* rather than *"this
    record was well formed"*.

    `in_harness_producer` is `False` for every case here, and that is a fact
    about this package rather than a placeholder: Band 7's cases are produced by
    the coordinator tooling §2.12.5a and §2.13.5a describe, which Package 5.0's
    work packages build and which this evidence harness does not contain. The
    field exists so that a case whose producer *is* in this harness — as Band 5's
    three immutable-flag experiments now are — cannot be silently satisfied by a
    supplied record instead of by the experiment.
    """

    case_id: str
    band: str
    producer: str
    collection_procedure: str
    in_harness_producer: bool
    variants: tuple[str, ...]
    fields: tuple[FieldSpec, ...]

    def field_names(self) -> frozenset[str]:
        return frozenset(spec.name for spec in self.fields)


def _f(name: str, shape: str) -> FieldSpec:
    return FieldSpec(name=name, shape=shape)


#: The four artifacts §2.13.3 puts under `…/journal`, named once so the omitted
#: provenance case and the stage-failure case ask about the same set.
_GENERATION_ARTIFACTS = ("journal", "seal", "current", "close")

#: The five points §2.13.5a's R7-A injects a failure at.
_FAILURE_STAGES = ("stage-1", "stage-2", "stage-3", "stage-4", "cleanup")

#: The two §2.13.2b cleanup-failure states the recovery case has to
#: distinguish. They are different states, not two spellings of one: a cleanup
#: failure after a probe stage failed and a cleanup failure after a fully
#: passing probe leave the host in the same place and mean different things
#: about what ran.
_RECOVERY_VARIANTS = (
    "cleanup-failure-after-probe-failure",
    "cleanup-failure-after-passing-probe",
)


BAND_7_SCHEMA: Mapping[str, CaseSchema] = {
    schema.case_id: schema
    for schema in (
        CaseSchema(
            case_id="JNL-51-PROVENANCE-OMITTED",
            band="provenance",
            producer=(
                "a run of `init-generation` on the disposable host after the "
                "deployment's D8 step was suppressed, or after PVR was deleted "
                "from a successful deployment"
            ),
            collection_procedure=(
                "record whether APR and PVR are present; run `init-generation` "
                "and record whether it refused and, if it did, the exact code it "
                "reported — an admission is recorded as `refused=no` with "
                "`refusal_code=none` rather than left out; list …/journal and "
                "record which of the four generation artifacts exist; query "
                "sheet_writer_journal_generations for a row; and establish from "
                "the syscall trace whether verify-capability was invoked at all"
            ),
            in_harness_producer=False,
            variants=("provenance-omitted",),
            fields=(
                _f("apr_present", "yes_no"),
                _f("pvr_present", "yes_no"),
                # **R16, EH-R16-2.** Two fields, because *"did it refuse?"* and
                # *"with which code?"* are two observations and the producer
                # makes both. `refused=no` with `refusal_code=none` is the
                # unexpected-admission record the version-1 schema could not
                # write down.
                _f("refused", "yes_no"),
                _f("refusal_code", "refusal_code_or_none"),
                *(_f(f"{name}_present", "yes_no") for name in _GENERATION_ARTIFACTS),
                _f("generation_row_present", "yes_no"),
                _f("probe_ran", "yes_no"),
            ),
        ),
        CaseSchema(
            case_id="JNL-47-NO-GENERATION-ON-FAILURE",
            band="journal",
            producer=(
                "a run of the §2.13.2a probe and `init-generation` on the "
                "disposable host with a failure injected at one named stage"
            ),
            collection_procedure=(
                "inject the failure at the named stage; then list …/journal and "
                "record which of the four generation artifacts exist, and query "
                "sheet_writer_journal_generations for a row. One record per "
                "stage; the case is not covered until all five are supplied"
            ),
            in_harness_producer=False,
            variants=_FAILURE_STAGES,
            fields=(
                *(_f(f"{name}_present", "yes_no") for name in _GENERATION_ARTIFACTS),
                _f("generation_row_present", "yes_no"),
            ),
        ),
        CaseSchema(
            case_id="JNL-47-RECOVERY-STATE",
            band="journal",
            producer=(
                "a run on the disposable host whose cleanup failed, once after a "
                "probe stage had failed and once after a fully passing probe"
            ),
            collection_procedure=(
                "record the exit code and the §2.13.2b state the run reported; "
                "count the residue paths it named; record whether any generation "
                "artifact and any database row exist; attempt a second run and "
                "record whether it refused; and record whether the named operator "
                "recovery procedure was reported. One record per variant"
            ),
            in_harness_producer=False,
            variants=_RECOVERY_VARIANTS,
            fields=(
                _f("exit_code", "exit_code"),
                _f("state", "cleanup_state"),
                _f("residue_path_count", "count"),
                _f("generation_present", "yes_no"),
                _f("database_row_present", "yes_no"),
                _f("next_run_refuses", "yes_no"),
                _f("recovery_procedure_named", "yes_no"),
            ),
        ),
    )
}

#: Every record key, and no other. A payload carrying a key outside this set was
#: written by something else, and one missing a key was truncated; both are
#: refusals rather than a best-effort parse.
_RECORD_KEYS = frozenset(
    {
        "case_id",
        "variant",
        "target_identity",
        "run_id",
        "review_manifest_digest",
        "custody",
        "collected_by",
        "collected_at",
        "fields",
    }
)

#: `collected_by` is a role, never a name, and `collected_at` is a date. Both are
#: shape-checked because they end up in an artifact: a free-text field here would
#: be the one place a supplied record could carry arbitrary content.
_ROLE = re.compile(r"\A[a-z][a-z0-9 -]{0,47}\Z")
_DATE = re.compile(r"\A[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
_RUN_ID = re.compile(r"\A[A-Za-z0-9._-]{1,64}\Z")
_DIGEST = re.compile(r"\A[0-9a-f]{64}\Z")


@dataclass(frozen=True, slots=True)
class SuppliedObservation:
    """One validated record. Every field has already passed its shape."""

    case_id: str
    variant: str
    target_identity: str
    run_id: str
    review_manifest_digest: str
    custody: Custody
    collected_by: str
    collected_at: str
    fields: Mapping[str, str]

    @property
    def key(self) -> str:
        return f"{self.case_id}#{self.variant}"

    def yes(self, name: str) -> bool:
        return self.fields[name] == "yes"


@dataclass(frozen=True, slots=True)
class ProducerMapping:
    """One required case, its producer, and whether that producer exists.

    This is the table the handback carries and the reviewer reads. A case whose
    producer is missing is reported **unresolved** — never covered — however many
    correctly shaped records arrive for it.
    """

    case_id: str
    band: str
    producer: str
    collection_procedure: str
    in_harness_producer: bool
    produced_by_plan_steps: tuple[str, ...]
    declared_unresolved_by: tuple[str, ...]


#: **R16, EH-R16-3.** What this importer's result is a result *about*. It is a
#: fixed string rather than a computed one, it is persisted in the artifact, and
#: it is the sentence a reviewer needs before reading any number below: this
#: result covers Band 7's externally produced cases and nothing else.
IMPORTER_SCOPE = (
    "Band 7 supplied observations only. This result carries no execution "
    "evidence: it is not joined with a run record, it contains no capability "
    "case and no control from the executed bands, and it therefore establishes "
    "nothing about overall required-case coverage."
)

#: **R16, EH-R16-3.** Why overall completeness and operational eligibility are
#: withheld rather than computed. Fixed strings, reported in the artifact, so the
#: withholding is a stated position and not a missing field.
COMPLETENESS_WITHHELD = (
    "Overall required-case completeness is withheld. The required cases outside "
    "this importer's scope are produced by the executed plan, and no validated "
    "execution observation has been joined to this result under the same target, "
    "run and review-manifest digest.",
    "Operational eligibility is withheld for the same reason. A Band-7 result "
    "cannot be the basis for accepting evidence whose capability cases and their "
    "controls are not in it.",
)


@dataclass(frozen=True, slots=True)
class EvidenceResult:
    """What the supplied observations establish, and what they do not.

    ## Important finding EH-R16-3

    R16 found the coverage loop skipping every required case that has no entry in
    `BAND_7_SCHEMA` — which is every capability case — so eight Band-7 records
    produced `complete=True` and `missing=()` with no run record and no
    capability observation anywhere in the result. *"The presence of producing
    steps in a plan does not prove those steps ran or that their controls
    succeeded."*

    The correction is the bounded one R16 offers as acceptable: this importer
    stays a **partial Band-7 result**, says so, and withholds the two judgements
    it is not entitled to make. It does **not** invent execution evidence to
    reach a complete one.

    So there are three coverage vocabularies here and they are kept apart:

    * `covered` / `missing` — Band-7 required case-and-variant keys, in scope;
    * `unresolved_cases` — in-scope cases the **plan** still declares unresolved.
      A validated record never moves one of these into `covered`; and
    * `outside_scope` — required cases this importer does not observe at all.
      They are listed, never counted, and their presence is on its own enough to
      withhold overall completeness.

    Coverage is also kept apart from **passing**: `band_7_coverage_complete` says
    a record exists for every in-scope variant, and `band_7_evidence_holds`
    additionally requires every classified record to have passed.
    """

    records: tuple[EvidenceRecord, ...]
    covered: tuple[str, ...]
    missing: tuple[str, ...]
    unresolved_cases: tuple[str, ...]
    #: **R16, EH-R16-3.** Required cases with no entry in `BAND_7_SCHEMA`: the
    #: ones the executed plan produces. They are outside what an importer can
    #: observe, and they are reported rather than skipped.
    outside_scope: tuple[str, ...]
    producers: tuple[ProducerMapping, ...]
    custody_levels: tuple[str, ...]
    synthetic: bool

    @property
    def scope(self) -> str:
        return IMPORTER_SCOPE

    @property
    def band_7_coverage_complete(self) -> bool:
        """Every **in-scope** required case and variant covered, none unresolved.

        Both halves, because they fail differently. A missing variant is an
        observation nobody supplied; an unresolved case is one the **plan** still
        cannot produce, and a supplied record must not close it.

        This is a statement about Band 7 and about nothing else. It is not
        `complete`, and the name says so: R16's finding was precisely that a
        Band-7 answer was being read as an answer about the whole harness.
        """
        return not self.missing and not self.unresolved_cases

    @property
    def band_7_records_all_passed(self) -> bool:
        """Whether every classified record passed. Coverage is not an outcome."""
        from .records import Status

        return bool(self.records) and all(
            record.status is Status.PASSED for record in self.records
        )

    @property
    def band_7_evidence_holds(self) -> bool:
        """In-scope coverage complete **and** every classified record passed."""
        return self.band_7_coverage_complete and self.band_7_records_all_passed

    @property
    def overall_completeness_established(self) -> bool:
        """Always `False` — **EH-R16-3**.

        Not a computation that happens to come out false. This importer holds no
        execution observation, so there is no input from which the question could
        be answered, and a property that answered it from Band 7 alone would be
        answering a different question under the same name. Joining validated
        execution and external observations under one target, run and manifest
        digest is the work that would make this answerable; until it exists the
        honest value is a withheld one.
        """
        return False

    @property
    def eligible_for_operational_acceptance(self) -> bool:
        """Always `False`, for the reason above — **EH-R16-3**.

        Structural disqualifications inside Band 7 are still computed and
        reported by `structural_disqualifications`, because a reviewer needs to
        know whether the in-scope half would have qualified. What is withheld is
        the *conclusion*, which no Band-7 result is entitled to reach.
        """
        return False

    @property
    def withheld(self) -> tuple[str, ...]:
        return COMPLETENESS_WITHHELD

    @property
    def structural_disqualifications(self) -> tuple[str, ...]:
        """What would disqualify the **in-scope** half, in a fixed order.

        Reported rather than reduced to a boolean, and reported even when it is
        empty — an empty tuple here says *"nothing in Band 7 disqualifies it"*
        and emphatically not *"this result is acceptable"*, which `withheld`
        states in the same summary.
        """
        problems: list[str] = []
        if self.missing:
            problems.append(
                "in-scope required variants have no validated record: "
                + ", ".join(self.missing)
            )
        if self.unresolved_cases:
            problems.append(
                "the plan still declares these required cases unresolved, so no "
                "record can cover them: " + ", ".join(self.unresolved_cases)
            )
        if self.synthetic:
            problems.append(
                "at least one record is a synthetic fixture, which is never "
                "operational evidence"
            )
        if self.custody_levels and tuple(self.custody_levels) != (
            Custody.REVIEWER_VERIFIED.value,
        ):
            problems.append(
                "not every record's custody is reviewer_verified: "
                + ", ".join(self.custody_levels)
            )
        if not self.records:
            problems.append(
                "no record was classified, so there is no outcome to read"
            )
        elif not self.band_7_records_all_passed:
            problems.append(
                "not every classified record passed, so coverage is not an "
                "outcome here"
            )
        return tuple(problems)


def _require_mapping(raw: object, what: str) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        raise ObservationRefused(f"A supplied {what} is a mapping.")
    return raw


def _exact_keys(raw: Mapping[str, Any], expected: frozenset[str], what: str) -> None:
    keys = set(raw)
    unknown = sorted(keys - expected)
    missing = sorted(expected - keys)
    if unknown or missing:
        raise ObservationRefused(
            f"A supplied {what} does not match this schema: unknown {unknown}, "
            f"missing {missing}. A key nobody declared is a key nobody reviewed, "
            "and a missing one is a truncated record."
        )


def _shaped(name: str, value: object, shape: str) -> str:
    if not isinstance(value, str) or not _SHAPES[shape].match(value):
        raise ObservationRefused(
            f"Field {name!r} carries {value!r}, which is not the {shape!r} shape "
            "its field can legitimately have."
        )
    return value


def parse_payload(payload: bytes) -> tuple[Mapping[str, Any], ...]:
    """The raw record mappings, after the payload's own envelope is checked.

    Separate from `import_observations` so a malformed envelope is refused before
    anything is compared with a plan, and so the schema and version are checked
    once rather than per record.
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise ObservationRefused("A supplied payload is bytes.")
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise ObservationRefused(
            f"A supplied payload is at most {MAX_PAYLOAD_BYTES} bytes; this one "
            f"is {len(payload)}."
        )
    try:
        document = json.loads(bytes(payload).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ObservationRefused(
            "The supplied observation payload is not readable UTF-8 JSON."
        ) from exc
    envelope = _require_mapping(document, "payload")
    _exact_keys(envelope, frozenset({"schema", "schema_version", "records"}), "payload")
    if envelope["schema"] != OBSERVATION_SCHEMA:
        raise ObservationRefused(
            f"This payload is written under schema {envelope['schema']!r}; this "
            f"importer reads {OBSERVATION_SCHEMA!r}."
        )
    if envelope["schema_version"] != OBSERVATION_SCHEMA_VERSION:
        raise ObservationRefused(
            f"This payload is version {envelope['schema_version']!r}; this "
            f"importer reads {OBSERVATION_SCHEMA_VERSION}. A payload produced "
            "under another version is not silently compared with one produced "
            "under this."
        )
    records = envelope["records"]
    if not isinstance(records, list) or not records:
        raise ObservationRefused("A supplied payload carries a non-empty record list.")
    if len(records) > MAX_RECORDS:
        raise ObservationRefused(
            f"A supplied payload carries at most {MAX_RECORDS} records; this one "
            f"carries {len(records)}."
        )
    return tuple(_require_mapping(item, "record") for item in records)


def read_records(
    payload: bytes,
    *,
    target_identity: str,
    run_id: str,
    review_manifest_digest: str,
) -> tuple[SuppliedObservation, ...]:
    """Validate every record against the closed schema and against its binding.

    Six families of refusal, and every one of them is a refusal rather than a
    dropped record:

    * **malformed** — a payload that is not the envelope, a record that is not a
      mapping, a key outside the declared set, a missing key, a value that is not
      the shape its field can have;
    * **unexpected** — a `case_id` or a `variant` outside `BAND_7_SCHEMA`, or a
      field name outside the variant's declared set;
    * **duplicate** — two records for one `case_id#variant`;
    * **mismatched** — a `target_identity`, `run_id` or `review_manifest_digest`
      that is not the one the caller supplied. The caller reads those from the
      plan and the manifest, so a record can only fail to match a value it did
      not choose;
    * **contradictory** — a record whose own fields cannot all be true at once;
      and
    * **missing** — a required case or variant with no record, which
      `classify_supplied_observations` reports rather than filling in.
    """
    if not _RUN_ID.match(run_id or ""):
        raise ObservationRefused(
            "The run identifier this import is bound to is a short token; it is "
            "supplied by the caller from the run being classified."
        )
    if not _DIGEST.match(review_manifest_digest or ""):
        raise ObservationRefused(
            "The review-manifest digest this import is bound to is 64 lower-case "
            "hexadecimal characters, recomputed by the caller from the live tree."
        )

    seen: dict[str, SuppliedObservation] = {}
    for position, raw in enumerate(parse_payload(payload)):
        _exact_keys(raw, _RECORD_KEYS, f"record at position {position}")
        case_id = raw["case_id"]
        schema = BAND_7_SCHEMA.get(case_id) if isinstance(case_id, str) else None
        if schema is None:
            raise ObservationRefused(
                f"{case_id!r} is not a case this importer accepts observations "
                f"for. The table is closed: {sorted(BAND_7_SCHEMA)}."
            )
        variant = raw["variant"]
        if not isinstance(variant, str) or variant not in schema.variants:
            raise ObservationRefused(
                f"{variant!r} is not a variant of {case_id!r}; the declared ones "
                f"are {list(schema.variants)}."
            )
        for name, expected in (
            ("target_identity", target_identity),
            ("run_id", run_id),
            ("review_manifest_digest", review_manifest_digest),
        ):
            if raw[name] != expected:
                raise ObservationRefused(
                    f"Record {case_id}#{variant} names {name} {raw[name]!r} and "
                    f"this import is bound to {expected!r}. A record is bound to "
                    "the target, the run and the reviewed plan it was collected "
                    "against, and the binding is compared rather than trusted."
                )
        try:
            custody = Custody(raw["custody"])
        except ValueError as exc:
            raise ObservationRefused(
                f"Record {case_id}#{variant} declares custody "
                f"{raw['custody']!r}; the vocabulary is closed: "
                f"{[member.value for member in Custody]}."
            ) from exc
        if (custody is Custody.SYNTHETIC_FIXTURE) != (
            target_identity == SYNTHETIC_TARGET_IDENTITY
        ):
            raise ObservationRefused(
                f"Record {case_id}#{variant} declares custody "
                f"{custody.value!r} against target {target_identity!r}. A "
                "synthetic fixture is collected against the synthetic target and "
                "an operational observation against a real one; a fixture that "
                "could be read as operational evidence is the defect this rule "
                "exists for."
            )
        collected_by = raw["collected_by"]
        if not isinstance(collected_by, str) or not _ROLE.match(collected_by):
            raise ObservationRefused(
                f"Record {case_id}#{variant} names its collector as "
                f"{collected_by!r}. It is a **role** — 'operations owner', "
                "'independent reviewer' — in a narrow character class, never a "
                "person's name and never free text."
            )
        collected_at = raw["collected_at"]
        if not isinstance(collected_at, str) or not _DATE.match(collected_at):
            raise ObservationRefused(
                f"Record {case_id}#{variant} dates its collection "
                f"{collected_at!r}; a date is YYYY-MM-DD."
            )
        fields = _require_mapping(raw["fields"], f"record {case_id}#{variant} fields")
        _exact_keys(fields, schema.field_names(), f"record {case_id}#{variant}")
        checked = {
            spec.name: _shaped(spec.name, fields[spec.name], spec.shape)
            for spec in schema.fields
        }
        observation = SuppliedObservation(
            case_id=case_id,
            variant=variant,
            target_identity=target_identity,
            run_id=run_id,
            review_manifest_digest=review_manifest_digest,
            custody=custody,
            collected_by=collected_by,
            collected_at=collected_at,
            fields=checked,
        )
        if observation.key in seen:
            raise ObservationRefused(
                f"Two records were supplied for {observation.key}. One "
                "observation per case and variant: a second one is either the "
                "same evidence twice or two different answers, and neither is a "
                "thing to choose between."
            )
        _refuse_contradictions(observation)
        seen[observation.key] = observation
    return tuple(seen[key] for key in sorted(seen))


def _refuse_contradictions(observation: SuppliedObservation) -> None:
    """A record whose own fields cannot all be true at once.

    Deliberately narrow, and deliberately not a re-classification: each rule
    below is a statement two fields make about the same fact, not a judgement
    about whether the case passed. Whether the case passed is the classifier's,
    and it is computed from the record rather than asserted by it.
    """
    fields = observation.fields
    if observation.case_id == "JNL-51-PROVENANCE-OMITTED":
        omitted = fields["apr_present"] == "no" or fields["pvr_present"] == "no"
        if not omitted:
            raise ObservationRefused(
                "JNL-51's omitted-provenance case reports both APR and PVR "
                "present. The case is the omission; a record in which nothing "
                "was omitted is a record of a different situation."
            )
        # **R16, EH-R16-2.** The two halves of the refusal observation have to
        # agree with each other. They are not a re-classification: neither says
        # whether the case passed, and both are facts the producer records.
        refused = fields["refused"] == "yes"
        if refused and fields["refusal_code"] == "none":
            raise ObservationRefused(
                "JNL-51 reports that init-generation refused and names no code. "
                "A refusal has a code; a record with one half of the observation "
                "is a record of half an observation."
            )
        if not refused and fields["refusal_code"] != "none":
            raise ObservationRefused(
                "JNL-51 reports that init-generation did not refuse and names a "
                "refusal code. Those are two different results and a record "
                "cannot hold both."
            )
        if fields["probe_ran"] == "yes" and fields["refusal_code"] == "J-26":
            raise ObservationRefused(
                "JNL-51 reports a J-26 refusal at C0 and a probe that ran. C0 "
                "precedes C1, so a refusal there and an invoked probe cannot "
                "both have happened."
            )
    if observation.case_id == "JNL-47-RECOVERY-STATE":
        if fields["state"] != "S-B":
            raise ObservationRefused(
                "JNL-47's recovery-state case is about a cleanup that did not "
                "complete, which is §2.13.2b state S-B. A record naming another "
                "state is a record of another run."
            )
        if fields["residue_path_count"] == "0" and fields["next_run_refuses"] == "yes":
            raise ObservationRefused(
                "JNL-47 reports no residue path and a next run that refuses. The "
                "next run refuses **because** residue exists, so a record "
                "asserting both is describing two different runs."
            )


def producer_mapping(plan) -> tuple[ProducerMapping, ...]:
    """Every required case, its producer, and where the plan stands on it.

    The mapping is built from `required_cases.REQUIRED_CASES` and from the plan,
    so a required case with no schema entry and no producing step is visible as
    exactly that rather than absent.
    """
    rows: list[ProducerMapping] = []
    for case in REQUIRED_CASES:
        schema = BAND_7_SCHEMA.get(case.case_id)
        produced = tuple(
            sorted(
                step.step_id
                for step in plan.steps
                if case.case_id in step.evidence_case_ids
            )
        )
        blocked = tuple(
            sorted(
                item.conflict_id
                for item in plan.unresolved
                if case.case_id in item.evidence_case_ids
            )
        )
        rows.append(
            ProducerMapping(
                case_id=case.case_id,
                band=case.band,
                producer=(
                    schema.producer
                    if schema is not None
                    else "this harness's own generated steps"
                ),
                collection_procedure=(
                    schema.collection_procedure
                    if schema is not None
                    else "the executor records the step's observation directly"
                ),
                in_harness_producer=schema is None,
                produced_by_plan_steps=produced,
                declared_unresolved_by=blocked,
            )
        )
    return tuple(rows)


def classify_supplied_observations(
    observations: Sequence[SuppliedObservation], *, plan
) -> EvidenceResult:
    """Turn validated observations into band records — conflict **C-7**.

    ## What connects to what

    | Case | Classifier |
    |---|---|
    | `JNL-51-PROVENANCE-OMITTED` | `provenance.classify_missing_provenance` |
    | `JNL-47-NO-GENERATION-ON-FAILURE` | `journal.classify_stage_failure`, once per stage |
    | `JNL-47-RECOVERY-STATE` | `journal.classify_cleanup_failure_state`, once per variant |

    `manifest.py`'s two classifiers are **not** here, and the reason is stated
    rather than left as an omission: their case is `JNL-46`, which is not in
    `required_cases.REQUIRED_CASES`. Adding a required case is a reviewer's
    decision and not an importer's, so this module neither requires an
    observation for it nor accepts one.

    ## What it refuses to call complete

    A required case whose plan step is still declared unresolved is reported in
    `unresolved_cases` and **never** in `covered`, however many well-formed
    records arrive for it. That is the half of EH-R13-4 an ingestion stage does
    not answer: an importer that accepted a correctly shaped record for a missing
    experiment would be manufacturing the evidence the experiment was supposed to
    produce.
    """
    producers = producer_mapping(plan)
    unresolved = tuple(
        sorted(row.case_id for row in producers if row.declared_unresolved_by)
    )
    by_key = {observation.key: observation for observation in observations}
    required_keys: list[str] = []
    # **R16, EH-R16-3.** A required case with no schema entry is not skipped. It
    # is a case this importer cannot observe, and it is reported as exactly that
    # — the previous version's `continue` is why eight Band-7 records could
    # produce `complete=True` with no capability observation in the result.
    outside_scope: list[str] = []
    for case in REQUIRED_CASES:
        schema = BAND_7_SCHEMA.get(case.case_id)
        if schema is None:
            outside_scope.append(case.case_id)
            continue
        required_keys.extend(f"{case.case_id}#{variant}" for variant in schema.variants)

    extra = sorted(set(by_key) - set(required_keys))
    if extra:
        raise ObservationRefused(
            f"{extra} were supplied and are not required cases of this schema. A "
            "record for a case nobody requires is a record nobody reviewed."
        )

    covered = tuple(
        key
        for key in required_keys
        if key in by_key and by_key[key].case_id not in unresolved
    )
    missing = tuple(key for key in required_keys if key not in by_key)

    records: list[EvidenceRecord] = []
    for key in required_keys:
        observation = by_key.get(key)
        if observation is None or observation.case_id in unresolved:
            continue
        records.extend(
            _stamped(record, observation) for record in _classify_one(observation)
        )

    custody_levels = tuple(
        sorted({observation.custody.value for observation in observations})
    )
    return EvidenceResult(
        records=tuple(records),
        covered=covered,
        missing=missing,
        unresolved_cases=unresolved,
        outside_scope=tuple(sorted(outside_scope)),
        producers=producers,
        custody_levels=custody_levels,
        synthetic=any(
            observation.custody is Custody.SYNTHETIC_FIXTURE
            for observation in observations
        ),
    )


def _stamped(
    record: EvidenceRecord, observation: SuppliedObservation
) -> EvidenceRecord:
    """The record, carrying the custody of the observation it came from.

    Two things travel with it, and both are in the **artifact** rather than only
    in the importer's summary:

    * `detail["custody"]`, `detail["collected_by"]` and `detail["collected_at"]`,
      because *where an observation came from* is part of what a reviewer is
      judging and target, run and digest do not say it; and
    * for a synthetic fixture, a `target_identity` **stamped with the synthetic
      marker**. A fixture record that could be read as an observation of the
      approved target is exactly the confusion the marker exists to prevent, and
      putting it in the identity field means every rendering of the record
      carries it.

    The status is not touched: `EvidenceRecord.__post_init__` recomputes it from
    the expectation and the observation on every construction, so a stamp cannot
    move a result.
    """
    identity = record.target_identity
    if observation.custody is Custody.SYNTHETIC_FIXTURE:
        identity = f"{SYNTHETIC_TARGET_IDENTITY} — {identity}"
    return replace(
        record,
        target_identity=identity,
        detail={
            **dict(record.detail),
            "custody": observation.custody.value,
            "collected_by": observation.collected_by,
            "collected_at": observation.collected_at,
            "supplied_run_id": observation.run_id,
        },
    )


def _absent_or_present(observation: SuppliedObservation, name: str):
    """`FileFacts` for one provenance record, from one yes/no field.

    The mode and ownership §2.12.5a requires are **not** reconstructed here: a
    record that carried them would be asserting the integrity the deployment
    algorithm checks, which is not an importer's to assert. Presence is the only
    fact `classify_missing_provenance` reads, and it is the only one supplied.
    """
    return FileFacts(present=observation.yes(name))


def _classify_one(observation: SuppliedObservation) -> tuple[EvidenceRecord, ...]:
    """One validated observation, through the band's own classifier.

    Every expected outcome below comes from the classifier's constants. Nothing
    in a supplied record reaches an expectation, and there is no branch in which
    an observation decides what it is compared against.
    """
    fields = observation.fields
    if observation.case_id == "JNL-51-PROVENANCE-OMITTED":
        apr = (
            ApprovedRevision(
                component="sheet-writer",
                source_commit="",
                source_tree_id="",
                source_manifest_digest="",
                review_reference="",
                approved_by="",
                approved_at="",
                facts=_absent_or_present(observation, "apr_present"),
            )
            if observation.yes("apr_present")
            else None
        )
        pvr = (
            ProvenanceRecord(
                component="sheet-writer",
                source_commit="",
                source_tree_id="",
                source_manifest_digest="",
                deployment_manifest_digest="",
                dependency_lock_digest="",
                deployed_at="",
                deployed_by="",
                facts=_absent_or_present(observation, "pvr_present"),
            )
            if observation.yes("pvr_present")
            else None
        )
        return classify_missing_provenance(
            apr=apr,
            pvr=pvr,
            # **R16, EH-R16-2.** The observed result, passed through to the
            # classifier and compared there with the fixed expectation. `None`
            # is the record saying the program admitted; it is never a value
            # this module chose, and the expectation is never one a record
            # reaches.
            observed_refusal_code=(
                fields["refusal_code"] if fields["refused"] == "yes" else None
            ),
            probe_ran=observation.yes("probe_ran"),
            generation_artifacts=tuple(
                name
                for name in _GENERATION_ARTIFACTS
                if observation.yes(f"{name}_present")
            ),
            generation_row_inserted=observation.yes("generation_row_present"),
        )
    if observation.case_id == "JNL-47-NO-GENERATION-ON-FAILURE":
        return (
            classify_stage_failure(
                stage=observation.variant,
                artifacts_present=tuple(
                    name
                    for name in _GENERATION_ARTIFACTS
                    if observation.yes(f"{name}_present")
                ),
                generation_row_present=observation.yes("generation_row_present"),
            ),
        )
    return (
        classify_cleanup_failure_state(
            variant=observation.variant,
            exit_code=int(fields["exit_code"]),
            state=fields["state"],
            residue_path_count=int(fields["residue_path_count"]),
            generation_present=observation.yes("generation_present"),
            database_row_present=observation.yes("database_row_present"),
            next_run_refuses=observation.yes("next_run_refuses"),
            recovery_procedure_named=observation.yes("recovery_procedure_named"),
        ),
    )


def import_observations(
    payload: bytes,
    *,
    plan,
    target_identity: str,
    run_id: str,
    review_manifest_digest: str,
) -> EvidenceResult:
    """Read, validate and classify one payload. The whole of the C-7 stage.

    It performs no operation on the host, starts no process and writes no file:
    the payload arrives as bytes from a caller authorized to read it, and the
    result is a set of `records.EvidenceRecord`s whose status each classifier
    derived from the observations. Persisting it is `execution/evidence_cli.py`'s
    job, and that module imports no boundary, no executor and no materializer.
    """
    observations = read_records(
        payload,
        target_identity=target_identity,
        run_id=run_id,
        review_manifest_digest=review_manifest_digest,
    )
    return classify_supplied_observations(observations, plan=plan)


__all__ = [
    "BAND_7_SCHEMA",
    "COMPLETENESS_WITHHELD",
    "CaseSchema",
    "Custody",
    "EvidenceResult",
    "FieldSpec",
    "IMPORTER_SCOPE",
    "MAX_PAYLOAD_BYTES",
    "MAX_RECORDS",
    "OBSERVATION_SCHEMA",
    "OBSERVATION_SCHEMA_VERSION",
    "ProducerMapping",
    "SYNTHETIC_TARGET_IDENTITY",
    "SuppliedObservation",
    "classify_supplied_observations",
    "import_observations",
    "producer_mapping",
    "parse_payload",
    "read_records",
]
