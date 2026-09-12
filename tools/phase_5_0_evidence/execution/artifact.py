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
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..capture import MAX_VALUE_LENGTH
from ..errors import ObservationRefused

#: The schema version of the run record. Separate from `EVIDENCE_SCHEMA_VERSION`
#: because this is a different document with a different contract, and sharing a
#: version number is how two documents come to be read as one.
RUN_RECORD_SCHEMA_VERSION = 1

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


def validate_run_record(document: Mapping[str, Any], *, expected_steps: int) -> None:
    """Refuse a document that is not the whole of what the run produced.

    This is what makes *"an artifact was written"* a claim about content rather
    than about a filesystem call succeeding. It is applied to the bytes **read
    back from disk**, never to the mapping that was serialized: a truncated
    write, a full filesystem and a partial flush all produce a file that a
    successful `write_text` says nothing about.
    """
    if document.get("schema_version") != RUN_RECORD_SCHEMA_VERSION:
        raise RunRecordRefused("The run record read back carries another schema.")
    if document.get("document_type") != DOCUMENT_TYPE:
        raise RunRecordRefused("The run record read back is another document.")
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


def write_run_record(
    outcome: Any,
    destination: Path,
    *,
    target_identity: str,
    manifest_digest: str,
) -> Path:
    """Serialize, write, **read back and validate**. Returns the path written.

    Every failure raises `RunRecordRefused`, and the CLI reports it as a failure
    to write rather than as a written artifact. There is no path through this
    function that returns a path for a file that was not written and read back
    whole.
    """
    if not outcome.artifact_admissible:
        raise RunRecordRefused(NOT_ADMISSIBLE)
    document = build_run_record(
        outcome, target_identity=target_identity, manifest_digest=manifest_digest
    )
    serialized = json.dumps(document, indent=2, sort_keys=True).encode("utf-8")
    try:
        destination.write_bytes(serialized)
        written = json.loads(destination.read_bytes().decode("utf-8"))
    except OSError as failure:
        # The message may name a path or an operating-system string; neither is
        # serialized, and the caller reports a fixed category.
        raise RunRecordRefused(
            "the run record could not be written or read back"
        ) from failure
    except ValueError as failure:
        raise RunRecordRefused(
            "the run record read back is not the document that was written"
        ) from failure
    validate_run_record(written, expected_steps=len(outcome.steps))
    return destination


__all__ = [
    "DOCUMENT_TYPE",
    "MAX_FIELD_LENGTH",
    "MAX_OBSERVED_LENGTH",
    "NOT_ADMISSIBLE",
    "NO_DESTINATION",
    "RUN_RECORD_SCHEMA_VERSION",
    "RunRecordRefused",
    "build_run_record",
    "validate_run_record",
    "write_run_record",
]
