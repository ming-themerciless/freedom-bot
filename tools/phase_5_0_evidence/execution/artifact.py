"""Writing the run record, and refusing to claim a write that did not happen.

## The finding this module answers — EH-R13-5

After a run, the CLI printed

```text
  artifact written : True
```

and never wrote anything. The only files it could produce were the pre-execution
manifest and the rendered plan, both written **before** the run and neither
containing an observation. So a successful scripted outcome reported an artifact
that did not exist, and the step observations and band records it would have
contained were discarded with the process.

The line was not merely misleading. `outcome.artifact_admissible` answers *"may
an artifact be written?"* — eligibility — and it was printed under a label that
answers *"was one written?"* — persistence. Those are different questions, and
the second one had no implementation at all.

## What is written, and what is deliberately not

This module writes the **run record**: what ran, in order, with the sanitized
observations each step produced, what stopped the run if anything did, and what
cleanup did, skipped, preserved and retained. Every value in it has already
passed `capture.sanitize`, and `_scalar` refuses anything that is not a bounded
scalar on the way out — so the file cannot acquire a path, a message or a
credential that the capture boundary would not have allowed into an observation.

It is **not** the classified evidence artifact. That is a set of
`records.EvidenceRecord`s, one per evidence case, each carrying its expectation,
its observation, its identity assertion and its positive control — and producing
one requires the band classification that Band 7 does not have a caller for
(finding EH-R13-4, conflict C-7). Writing a file of the right shape with the
cases that happen to be available would be the same defect in a new place: a
document that reads as complete evidence and is not.

So the run record says what it is, in a `document_type` field a reader cannot
miss, and `write_run_record()` refuses to write one for a run that is not
admissible. The CLI then reports the path it actually wrote, or the reason there
is none.

## What version 3 adds — PR-20260912-LAB1-1

Version 2 introduced `residue_recovery_procedure` and checked it for **shape**:
three keys, a consecutive order, non-empty strings. That is not a check on
*content*, and the independent re-review reproduced the consequence — a schema-2
S-B record carrying the single step

```text
{order: 1, action: "IGNORE THE RESIDUE AND CONTINUE",
 rationale: "arbitrary replacement"}
```

was **accepted**, so the reader could not tell the named five-step recovery from
any well-shaped substitute. A record that says the run reported the operator
recovery while carrying the opposite instruction is the reporting gap LAB-1
named, one document further out.

Version 3 makes two claims the earlier revisions only appeared to make.

1. **Content is bound to cause.** Residue present requires exactly
   `journal.RECOVERY_PROCEDURE` — every order, action and rationale compared with
   the canonical value — and residue absent requires an empty residue procedure.
   Retained recovery inputs require exactly `cleanup.RECOVERY_PROCEDURE`, and no
   retained inputs require it empty. The two procedures are independent: neither
   satisfies the other's requirement, which is the LAB-1 clause itself.
2. **The read-back is the document that was written**, whole. `write_run_record`
   compares the bytes read from disk with the bytes serialized from the outcome,
   so a partial flush or a substituted-but-well-shaped value is refused whatever
   `expected_steps` says. *(Corrected 2026-09-13: as first written this sentence
   overstated what the code did — see PR-20260912-LAB1-2 below. It describes the
   implementation from that correction onward.)*

The version is raised rather than widened because these are incompatible
meanings of the same field: under version 2 an arbitrary procedure was a valid
record, and under version 3 it is not. A version-2 document is refused by name
rather than reinterpreted under either reading.

## What the raw-byte binding adds — PR-20260912-LAB1-2

The claim in point 2 was made by a function that never received the bytes. The
writer read them, decoded them, parsed them, and passed **only the parsed
mapping** to the comparison, which compared that mapping with the emitted
document and a fresh canonical re-serialization of it with the emitted bytes.
Both are statements about what a reader made of the file. Neither is a statement
about the file, so every difference JSON parsing collapses was accepted. The
independent re-review reproduced two through the public writer:

```text
read_back = b"\n" + serialized + b"\n"                    -> accepted
read_back = serialized with a duplicate schema_version=3  -> accepted
```

The duplicate is the material one. A repeated member name is not an error to
`json.loads`, which keeps the last occurrence — but RFC 8259 leaves the handling
of duplicates to the implementation, so the file has no single agreed meaning
while the writer asserts it is exactly the document serialized from the outcome.

`write_run_record` now retains the bytes `destination.read_bytes()` returned and
requires `raw == serialized` before it can report a written artifact. The three
claims the completed path makes are deliberately kept apart:

1. the raw bytes read back **are** the bytes serialized and written;
2. those bytes decode and parse as the document the run produced; and
3. the parsed document satisfies `validate_run_record` — including the exact
   per-cause canonical recovery contract version 3 introduced.

Raw equality proves what came back; validation proves what it means. Neither
stands in for the other, and no digest, normalized form, re-serialized mapping,
length or decoded-text comparison stands in for the first.

**This is a writer implementation fix, not a document-contract change.** A valid
schema-3 record means exactly what it meant before: the bytes a conforming writer
emits are unchanged, and every document version 3 accepted it still accepts. The
run-record schema therefore stays at **3**, the supplied-observation schema at
**3** and the review manifest at **10**; only `artifact.py`'s pinned covered-source
hash moves.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..capture import MAX_VALUE_LENGTH
from ..cleanup import RECOVERY_PROCEDURE as CONFIGURATION_RECOVERY_PROCEDURE
from ..errors import ObservationRefused
from ..journal import RECOVERY_PROCEDURE as RESIDUE_RECOVERY_PROCEDURE

#: The schema version of the run record. Separate from `EVIDENCE_SCHEMA_VERSION`
#: because this is a different document with a different contract, and sharing a
#: version number is how two documents come to be read as one.
#:
#: **3** — PR-20260912-LAB1-1: the residue and configuration recovery procedures
#: are bound to their exact canonical values and to the cause that requires each,
#: and the read-back is compared whole. **2** was the version that carried the
#: residue procedure as a shape-checked list, which an arbitrary ordered
#: replacement satisfied.
RUN_RECORD_SCHEMA_VERSION = 3

#: What this document is, written into the document so a reader cannot take it
#: for the classified evidence artifact.
DOCUMENT_TYPE = "freedom-blades/phase-5.0/run-record"

#: The longest **reviewed** field this document may carry: an argument vector's
#: argument, a fixed classification, a cleanup message. §2.13.5c's `capsh`
#: constructions name every capability the identity does not hold, which is one
#: argument of about six hundred characters, so the bound is generous — and it
#: is a bound on text the *plan* wrote, which a reviewer has already read.
MAX_FIELD_LENGTH = 1024

#: The longest **observed** value, which is `capture.MAX_VALUE_LENGTH` and is
#: read from there so the two cannot drift. Anything longer did not come through
#: the capture boundary, and this document is not the place to discover that.
MAX_OBSERVED_LENGTH = MAX_VALUE_LENGTH

#: What the CLI prints when there is no artifact, per reason. Fixed strings: the
#: reason a document was not written is not a place for a host fact either.
NOT_ADMISSIBLE = (
    "no — the run is not admissible: it stopped, a step was unsatisfied, or "
    "cleanup did not reach S-C"
)
NO_DESTINATION = (
    "no — no output path was given, so nothing was written and nothing is claimed"
)

#: `journal.RECOVERY_PROCEDURE` in the shape the document carries it, flattened
#: to a comparable tuple. Derived from the canonical value rather than restated,
#: so the document contract cannot drift from the procedure an operator is
#: actually told to follow.
CANONICAL_RESIDUE_RECOVERY: tuple[tuple[int, str, str], ...] = tuple(
    (step.order, step.action, step.rationale) for step in RESIDUE_RECOVERY_PROCEDURE
)

#: `cleanup.RECOVERY_PROCEDURE`, the four configuration-recovery lines, likewise
#: derived rather than restated.
CANONICAL_CONFIGURATION_RECOVERY: tuple[str, ...] = tuple(
    CONFIGURATION_RECOVERY_PROCEDURE
)

#: Every key `build_run_record` emits at the top level, and every key it emits
#: under `cleanup`. A document with a missing or an unknown key is refused rather
#: than read around: *"the whole of what the run produced"* is a claim about the
#: key set as much as about the values, and a reader that ignores an unexpected
#: field cannot say what the field meant.
DOCUMENT_FIELDS = frozenset(
    {
        "schema_version",
        "document_type",
        "target_identity",
        "review_manifest_digest",
        "completed",
        "stopped_at",
        "stop_reason",
        "steps",
        "cleanup",
        "mutations_reached",
    }
)

CLEANUP_FIELDS = frozenset(
    {
        "state",
        "exit_code",
        "residue",
        "configuration_risk",
        "preserved",
        "retained_recovery_inputs",
        "recovery_procedure",
        "residue_recovery_procedure",
        "steps",
        "skipped",
    }
)

#: The three keys one residue-recovery step carries, and no others.
RECOVERY_STEP_FIELDS = frozenset({"order", "action", "rationale"})

#: The refusals, as fixed strings. Each names the property that failed and
#: nothing that was read: a hostile record is refused, never quoted back.
NOT_THE_DOCUMENT_WRITTEN = (
    "the run record read back is not the document that was written"
)
UNEXPECTED_FIELDS = (
    "The run record read back does not carry exactly the fields this schema "
    "defines."
)
RESIDUE_PROCEDURE_MALFORMED = (
    "The run record read back has a malformed residue-recovery step."
)
RESIDUE_PROCEDURE_NOT_CANONICAL = (
    "The run record read back leaves residue and does not carry the canonical "
    "residue-recovery procedure that residue requires."
)
RESIDUE_PROCEDURE_WITHOUT_RESIDUE = (
    "The run record read back carries a residue-recovery procedure for a run "
    "that reported no residue."
)
CONFIGURATION_PROCEDURE_NOT_CANONICAL = (
    "The run record read back retains recovery inputs and does not carry the "
    "canonical configuration-recovery procedure those inputs require."
)
CONFIGURATION_PROCEDURE_WITHOUT_RETENTION = (
    "The run record read back carries a configuration-recovery procedure for a "
    "run that retained no recovery inputs."
)


class RunRecordRefused(ObservationRefused):
    """The run record could not be written, or could not be read back."""


def _scalar(value: Any) -> Any:
    """One field, or a refusal. Bounded strings, integers and booleans only."""
    if isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, str):
        if len(value) > MAX_FIELD_LENGTH:
            raise RunRecordRefused(
                "A run-record field is longer than a reviewed observation can "
                "be, so it did not come from the capture boundary."
            )
        return value
    raise RunRecordRefused(
        "A run record carries scalars. Command output, file content and host "
        "configuration do not belong in one."
    )


def _observed(value: Any) -> str:
    """One recorded observation value, bounded as the capture boundary bounds it."""
    if not isinstance(value, str) or len(value) > MAX_OBSERVED_LENGTH:
        raise RunRecordRefused(
            "A recorded observation is longer than the capture boundary permits, "
            "so it did not come through it."
        )
    return value


def _step_mapping(step: Any) -> dict[str, Any]:
    return {
        "step_id": _scalar(step.step_id),
        "band": _scalar(step.band),
        "run_as": _scalar(step.run_as),
        "argv": [_scalar(argument) for argument in step.argv],
        "exit_status": _scalar(step.exit_status),
        "satisfied": _scalar(step.satisfied),
        "timed_out": _scalar(step.timed_out),
        "stderr_present": _scalar(step.stderr_present),
        "launch_failure": _scalar(step.launch_failure),
        "stop_reason": _scalar(step.stop_reason),
        "observations": [
            [_scalar(key), _observed(value)] for key, value in step.observations
        ],
    }


def build_run_record(
    outcome: Any, *, target_identity: str, manifest_digest: str
) -> dict[str, Any]:
    """The complete document, as a mapping, with every field checked."""
    return {
        "schema_version": RUN_RECORD_SCHEMA_VERSION,
        "document_type": DOCUMENT_TYPE,
        "target_identity": _scalar(target_identity),
        "review_manifest_digest": _scalar(manifest_digest),
        "completed": _scalar(outcome.completed),
        "stopped_at": _scalar(outcome.stopped_at),
        "stop_reason": _scalar(outcome.stop_reason),
        "steps": [_step_mapping(step) for step in outcome.steps],
        "cleanup": {
            "state": _scalar(outcome.cleanup.state),
            "exit_code": _scalar(outcome.cleanup.exit_code),
            "residue": [_scalar(item) for item in outcome.cleanup.residue],
            "configuration_risk": [
                _scalar(item) for item in outcome.cleanup.configuration_risk
            ],
            "preserved": [_scalar(item) for item in outcome.cleanup.preserved],
            "retained_recovery_inputs": [
                _scalar(item) for item in outcome.cleanup.retained_recovery_inputs
            ],
            "recovery_procedure": [
                _scalar(item) for item in outcome.cleanup.recovery_procedure
            ],
            "residue_recovery_procedure": [
                {
                    "order": _scalar(step.order),
                    "action": _scalar(step.action),
                    "rationale": _scalar(step.rationale),
                }
                for step in outcome.cleanup.residue_recovery_procedure
            ],
            "steps": [_step_mapping(step) for step in outcome.cleanup_steps],
            "skipped": [
                {
                    "step_id": _scalar(item.step_id),
                    "subject": _scalar(item.subject),
                    "reason": _scalar(item.reason),
                }
                for item in outcome.cleanup_skipped
            ],
        },
        "mutations_reached": [
            _scalar(item) for item in outcome.mutations_reached
        ],
    }


def _matches_canonical(read: tuple[Any, ...], canonical: tuple[Any, ...]) -> bool:
    """Exact equality with a reviewed, bounded canonical value.

    The one comparison the whole of PR-20260912-LAB1-1 rests on, in one place so
    that gutting it is a visible edit rather than a weakened condition inside a
    longer predicate. It is deliberately not `bool(read)`, not a length check, not
    a consecutive-order check and not a digest the record supplied about itself:
    each of those is satisfied by a well-shaped substitute, which is what the
    re-review reproduced.
    """
    return len(read) == len(canonical) and all(
        element == expected for element, expected in zip(read, canonical)
    )


def _read_back_matches(
    raw: bytes, written: Any, document: Mapping[str, Any], serialized: bytes
) -> bool:
    """Whether the bytes read from the destination are the bytes written.

    The second comparison the repair rests on, in one place for the same reason
    as the first — and it takes the **raw** bytes, which is the correction
    PR-20260912-LAB1-2 required.

    Three conjuncts, in the order their claims are established.

    1. `raw == serialized` — the bytes that came back are the bytes that went
       out. This is the load-bearing one. Everything weaker is a statement about
       what a *reader* made of those bytes, and the re-review reproduced two
       files that no reader distinguishes from the document written:
       `b"\n" + serialized + b"\n"`, and a repeated `schema_version` member
       carrying the value it already had. Both parse to the emitted mapping, both
       re-serialize to the emitted bytes, and neither is the document written.
       Duplicate member names are the material case: RFC 8259 leaves their
       handling to the implementation, so a file carrying one does not have a
       single agreed meaning, and a writer claiming *"this is what I wrote"* may
       not accept it.
    2. `written == document` — those bytes decode and parse as the document the
       run produced. Byte equality already implies this for anything
       `build_run_record` emits, so it is a **restatement**, not an independent
       barrier: it is kept because the read-back's two claims are different
       statements, and a later change that relaxes the first must be made to
       confront the second rather than find it already gone.
    3. The canonical re-serialization is those same bytes, which is what
       separates a `true` read back from the `1` that was written where mapping
       equality would not.

    Gutting this function is therefore a single visible edit, and the negative
    controls exercise exactly that.
    """
    return (
        raw == serialized
        and written == document
        and json.dumps(written, indent=2, sort_keys=True).encode("utf-8") == serialized
    )


def _residue_procedure(cleanup: Mapping[str, Any]) -> tuple[tuple[int, str, str], ...]:
    """The residue procedure as read, shape-checked, flattened for comparison.

    The shape check stays because the order **is** the procedure: an entry whose
    `order` is not its position is a differently sequenced instruction and is
    refused before its text is compared with anything.
    """
    procedure = cleanup.get("residue_recovery_procedure")
    if not isinstance(procedure, list):
        raise RunRecordRefused(
            "The run record read back omits the residue-recovery procedure field."
        )
    read: list[tuple[int, str, str]] = []
    for index, step in enumerate(procedure, start=1):
        if (
            not isinstance(step, dict)
            or set(step) != RECOVERY_STEP_FIELDS
            or isinstance(step.get("order"), bool)
            or step.get("order") != index
            or not isinstance(step.get("action"), str)
            or not step.get("action")
            or not isinstance(step.get("rationale"), str)
            or not step.get("rationale")
        ):
            raise RunRecordRefused(RESIDUE_PROCEDURE_MALFORMED)
        read.append((step["order"], step["action"], step["rationale"]))
    return tuple(read)


def _configuration_procedure(cleanup: Mapping[str, Any]) -> tuple[str, ...]:
    procedure = cleanup.get("recovery_procedure")
    if not isinstance(procedure, list) or not all(
        isinstance(line, str) for line in procedure
    ):
        raise RunRecordRefused(
            "The run record read back omits the configuration-recovery procedure "
            "field."
        )
    return tuple(procedure)


def _string_list(cleanup: Mapping[str, Any], field: str) -> tuple[str, ...]:
    value = cleanup.get(field)
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise RunRecordRefused(
            "The run record read back does not carry the cleanup lists this "
            "schema defines as bounded strings."
        )
    return tuple(value)


def validate_run_record(document: Mapping[str, Any], *, expected_steps: int) -> None:
    """Refuse a document that is not the whole of what the run produced.

    This is what makes *"an artifact was written"* a claim about content rather
    than about a filesystem call succeeding. It is applied to the bytes **read
    back from disk**, never to the mapping that was serialized: a truncated
    write, a full filesystem and a partial flush all produce a file that a
    successful `write_text` says nothing about.

    **It validates a document independently of the outcome it came from** —
    PR-20260912-LAB1-1. Given only the bytes, it requires the cleanup contract to
    hold within them: the recovery a cause requires is the exact canonical
    procedure for that cause, and a cause that is absent requires its procedure
    to be absent too. `write_run_record` adds the separate claim that these bytes
    are the ones it serialized; the two are different statements and neither
    stands in for the other.
    """
    if document.get("schema_version") != RUN_RECORD_SCHEMA_VERSION:
        raise RunRecordRefused("The run record read back carries another schema.")
    if document.get("document_type") != DOCUMENT_TYPE:
        raise RunRecordRefused("The run record read back is another document.")
    if set(document) != DOCUMENT_FIELDS:
        raise RunRecordRefused(UNEXPECTED_FIELDS)
    steps = document.get("steps")
    if not isinstance(steps, list) or len(steps) != expected_steps:
        raise RunRecordRefused(
            "The run record read back does not contain one entry for every step "
            "the run produced."
        )
    for entry in steps:
        if not isinstance(entry, dict) or not entry.get("step_id"):
            raise RunRecordRefused("A run-record step has no identifier.")
    cleanup = document.get("cleanup")
    if not isinstance(cleanup, dict) or not cleanup.get("state"):
        raise RunRecordRefused("The run record read back names no cleanup state.")
    if set(cleanup) != CLEANUP_FIELDS:
        raise RunRecordRefused(UNEXPECTED_FIELDS)

    residue_present = bool(_string_list(cleanup, "residue"))
    retained_present = bool(_string_list(cleanup, "retained_recovery_inputs"))
    residue_procedure = _residue_procedure(cleanup)
    configuration_procedure = _configuration_procedure(cleanup)

    #: Each cause is bound to its own procedure and to nothing else. A run that
    #: left residue and carried only the configuration procedure is refused here
    #: as well as in the evidence classifier, because a record that reports the
    #: wrong recovery is the defect whichever layer reads it.
    if residue_present:
        if not _matches_canonical(residue_procedure, CANONICAL_RESIDUE_RECOVERY):
            raise RunRecordRefused(RESIDUE_PROCEDURE_NOT_CANONICAL)
    elif residue_procedure:
        raise RunRecordRefused(RESIDUE_PROCEDURE_WITHOUT_RESIDUE)

    if retained_present:
        if not _matches_canonical(
            configuration_procedure, CANONICAL_CONFIGURATION_RECOVERY
        ):
            raise RunRecordRefused(CONFIGURATION_PROCEDURE_NOT_CANONICAL)
    elif configuration_procedure:
        raise RunRecordRefused(CONFIGURATION_PROCEDURE_WITHOUT_RETENTION)


def write_run_record(
    outcome: Any,
    destination: Path,
    *,
    target_identity: str,
    manifest_digest: str,
) -> Path:
    """Serialize, write, **read back, compare and validate**. Returns the path.

    Every failure raises `RunRecordRefused`, and the CLI reports it as a failure
    to write rather than as a written artifact. There is no path through this
    function that returns a path for a file that was not written and read back
    whole.

    **Whole-document comparison — PR-20260912-LAB1-1.** *Read back whole* used to
    mean *read back and found structurally plausible*, which a substituted value
    in any unchecked field survives. The document read from disk is now compared
    with the document serialized from the supplied outcome, mapping and bytes:
    the mapping comparison states the property, and re-serializing under the same
    canonical settings makes it a byte comparison, which additionally separates
    `true` from `1` where mapping equality would not. A partial flush, a
    substituted scalar and a replaced list are all refused, whatever
    `expected_steps` happens to match.

    **Raw-byte binding — PR-20260912-LAB1-2.** Both comparisons above are made
    *after* parsing, so both describe the parsed mapping rather than the file, and
    added whitespace and a repeated member name were accepted. The bytes
    `destination.read_bytes()` returns are now **retained** and compared directly
    with `serialized`; the order is read, then decode and parse, then
    `_read_back_matches` — whose first conjunct is that byte comparison — then
    `validate_run_record`. Any byte difference raises the same fixed
    `NOT_THE_DOCUMENT_WRITTEN` refusal, and no path returns a destination without
    having made all three claims. The refusals stay fixed and bounded: none of
    them carries a path, the raw bytes, parsed content or operating-system text.
    """
    if not outcome.artifact_admissible:
        raise RunRecordRefused(NOT_ADMISSIBLE)
    document = build_run_record(
        outcome, target_identity=target_identity, manifest_digest=manifest_digest
    )
    serialized = json.dumps(document, indent=2, sort_keys=True).encode("utf-8")
    try:
        destination.write_bytes(serialized)
        raw = destination.read_bytes()
    except OSError as failure:
        # The message may name a path or an operating-system string; neither is
        # serialized, and the caller reports a fixed category.
        raise RunRecordRefused(
            "the run record could not be written or read back"
        ) from failure
    try:
        written = json.loads(raw.decode("utf-8"))
    except ValueError as failure:
        # `UnicodeDecodeError` is a `ValueError`, so bytes that are not UTF-8 and
        # bytes that are not JSON refuse by the same fixed name.
        raise RunRecordRefused(NOT_THE_DOCUMENT_WRITTEN) from failure
    if not _read_back_matches(raw, written, document, serialized):
        raise RunRecordRefused(NOT_THE_DOCUMENT_WRITTEN)
    validate_run_record(written, expected_steps=len(outcome.steps))
    return destination


__all__ = [
    "CANONICAL_CONFIGURATION_RECOVERY",
    "CANONICAL_RESIDUE_RECOVERY",
    "CLEANUP_FIELDS",
    "CONFIGURATION_PROCEDURE_NOT_CANONICAL",
    "CONFIGURATION_PROCEDURE_WITHOUT_RETENTION",
    "DOCUMENT_FIELDS",
    "DOCUMENT_TYPE",
    "MAX_FIELD_LENGTH",
    "MAX_OBSERVED_LENGTH",
    "NOT_ADMISSIBLE",
    "NOT_THE_DOCUMENT_WRITTEN",
    "NO_DESTINATION",
    "RECOVERY_STEP_FIELDS",
    "RESIDUE_PROCEDURE_MALFORMED",
    "RESIDUE_PROCEDURE_NOT_CANONICAL",
    "RESIDUE_PROCEDURE_WITHOUT_RESIDUE",
    "RUN_RECORD_SCHEMA_VERSION",
    "RunRecordRefused",
    "UNEXPECTED_FIELDS",
    "build_run_record",
    "validate_run_record",
    "write_run_record",
]
