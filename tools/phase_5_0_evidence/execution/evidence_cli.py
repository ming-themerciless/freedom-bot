"""Conflict **C-7**'s entry point: import supplied observations, classify them,
and persist the classified artifact. It can start nothing.

    python -m tools.phase_5_0_evidence.execution.evidence_cli \\
        --observations PATH [--artifact-out PATH] [--run-id ID]

## Why this is a separate module from `cli.py`

R14 said what would resolve C-7: an ingestion stage, *"and what stops that input
reaching the component that constructs the process boundary"*. The answer is not
a flag on the existing CLI. `cli.py` is the one module in this repository that
constructs a `SubprocessBoundary` and a `SystemMaterializer`, and a supplied
payload that reached it would be an input on the component that can start
privileged processes — a property no argument parsing makes safe.

So the ingestion stage is **a different program with a different import graph**.
This module imports the planner, the review manifest, the importer and the
records tier. It imports **no** `boundary`, **no** `executor` and **no**
`materializer`, and it does not import `cli`. There is therefore no call path
from a supplied observation to a process, and that is a structural property
rather than a promise: `tests/phase_5_0_evidence/test_no_execution.py` asserts
this module's import set against the three names, and asserts it defines no
`--execute` option.

## What it does with the payload

1. builds the concrete plan and recomputes the review manifest from the live
   tree, so the digest a record is bound to is the digest of the plan that is
   actually here;
2. hands the payload to `observations.import_observations`, which validates it
   against the closed schema, binds it to the target, the run and that digest,
   and refuses malformed, duplicate, unexpected, contradictory and mismatched
   records;
3. classifies the validated observations through the band's own classifiers; and
4. writes the classified artifact only when `--artifact-out` is given — and
   **reads it back, deserializes it through the same constructor that wrote it,
   and compares its digest** before reporting a path.

## Scope, and the two judgements this program does not make — R16, EH-R16-3

The artifact and the summary both carry the importer's **scope**: Band 7's
supplied observations, and nothing else. The required cases outside that scope
are listed rather than skipped, and overall completeness and operational
eligibility are **withheld** rather than computed from the half that is here.
R16 found the previous version reporting `complete=True` for eight Band-7
records with no run record and no capability observation anywhere in the result.

## What it deliberately does not write

The **run record** — what ran and what was observed — is a different document
written by a different program: `execution/artifact.py`, from `cli.py`, after an
`--execute`. This writes the **classified evidence artifact**: one
`records.EvidenceRecord` per case, each carrying its expectation, its
observation and its status. Keeping them apart is not tidiness. A run record
describes a run; an evidence artifact makes a claim about what the evidence
shows, and R13's EH-R13-5 was a CLI that printed the second while producing
neither.

An artifact is written for an **incomplete** result too, and for one that
classified no record at all, and it says so: it carries the covered cases, the
missing ones, the unresolved ones, the ones outside its scope, the custody
levels and every structural disqualification. Refusing to write an incomplete
artifact would lose the part a reviewer most needs to read.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from ..concrete_plan import build_concrete_plan
from ..errors import HarnessError, ObservationRefused
from ..observations import (
    EvidenceResult,
    OBSERVATION_SCHEMA,
    OBSERVATION_SCHEMA_VERSION,
    SYNTHETIC_TARGET_IDENTITY,
    import_observations,
)
from ..records import (
    deserialize_records,
    records_digest,
    serialize_records,
    summarize,
)
from ..review_manifest import COVERED_SOURCES, ReviewManifest

#: The repository root, three levels up from this file. Computed rather than
#: configured, exactly as `cli.py` computes it, so the covered-source read cannot
#: be pointed somewhere else.
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

#: The exit status for a payload this program refused. Distinct from 1 so that
#: *"the observations were not admissible"* is never the same as *"something
#: went wrong"*.
REFUSED_EXIT_CODE = 4

#: The exit status for a result that is admissible and **incomplete**. Also
#: distinct: an incomplete artifact is a legitimate output and not a failure, and
#: a caller that treated it as success would be treating missing evidence as
#: evidence.
INCOMPLETE_EXIT_CODE = 5

#: What the summary prints when no artifact was written, per reason. Fixed
#: strings, for `artifact.py`'s reason: why a document was not written is not a
#: place for a host fact either.
NO_DESTINATION = (
    "no — no output path was given, so nothing was written and nothing is claimed"
)


class ArtifactRefused(ObservationRefused):
    """The classified artifact could not be written, or could not be read back."""


def read_covered_sources(root: Path = REPOSITORY_ROOT) -> dict[str, bytes]:
    """The exact bytes of every file the manifest pins.

    Reads only `COVERED_SOURCES` — an enumerated tuple, not a glob — for the
    reason `cli.read_covered_sources` does: a manifest over a subset would bind a
    record to a digest that approved less than the plan it names.
    """
    contents: dict[str, bytes] = {}
    for relative in COVERED_SOURCES:
        path = root / relative
        if not path.is_file():
            raise HarnessError(
                f"{relative} is covered by the review manifest and is not "
                "present, so the digest a supplied record is bound to cannot be "
                "recomputed."
            )
        contents[relative] = path.read_bytes()
    return contents


#: The document `write_artifact` writes. It is **not** `records.py`'s bare record
#: list: an artifact that carried only classified records would say nothing about
#: what was *not* classified, which is the half EH-R16-3 is about.
ARTIFACT_SCHEMA = "freedom-blades/phase-5.0/classified-evidence"

#: Bumped when the envelope's field set changes. **1** is R16's disposition of
#: EH-R16-3: the scope, the coverage vocabularies and the withheld judgements are
#: persisted beside the records rather than printed to a console and lost.
ARTIFACT_SCHEMA_VERSION = 1


def scope_document(result: EvidenceResult) -> dict:
    """**R16, EH-R16-3.** What this result covers, and what it does not.

    Every field is derived from the result and from the reviewed constants; none
    is supplied by a record. It is persisted, so a reviewer reading the artifact
    alone learns the scope, the required cases outside it, the variants nobody
    supplied, the cases the plan declares unresolved, and the two judgements the
    importer withholds — rather than having to have been at the terminal.
    """
    return {
        "scope": result.scope,
        "covered": list(result.covered),
        "missing": list(result.missing),
        "unresolved_cases": list(result.unresolved_cases),
        "outside_scope": list(result.outside_scope),
        "custody_levels": list(result.custody_levels),
        "synthetic": result.synthetic,
        "band_7_coverage_complete": result.band_7_coverage_complete,
        "band_7_records_all_passed": result.band_7_records_all_passed,
        "band_7_evidence_holds": result.band_7_evidence_holds,
        "overall_completeness_established": result.overall_completeness_established,
        "eligible_for_operational_acceptance": (
            result.eligible_for_operational_acceptance
        ),
        "withheld": list(result.withheld),
        "structural_disqualifications": list(result.structural_disqualifications),
        "producers": [
            {
                "case_id": row.case_id,
                "band": row.band,
                "producer": row.producer,
                "collection_procedure": row.collection_procedure,
                "in_harness_producer": row.in_harness_producer,
                "produced_by_plan_steps": list(row.produced_by_plan_steps),
                "declared_unresolved_by": list(row.declared_unresolved_by),
            }
            for row in result.producers
        ],
    }


def write_artifact(result: EvidenceResult, destination: Path) -> Path:
    """Serialize, write, **read back, re-validate and compare**. Returns the path.

    Three checks, and the middle one is the one R13's EH-R13-5 was missing:

    * `serialize_records` validates the records before they become bytes, so an
      incoherent set cannot be written and discovered later;
    * the bytes are read back from disk, the records half is passed through
      `deserialize_records`, which reconstructs every record **through the same
      constructor** — so a stored status that disagrees with its own stored
      observations is a refusal rather than a value; and
    * the digest of the records that came back is compared with the digest of the
      records that went out, and the scope document is compared byte for byte.

    A truncated write, a full filesystem and a partial flush all produce a file a
    successful `write_bytes` says nothing about. Every failure raises, and the
    caller reports a refusal rather than a path.

    **R16, EH-R16-3.** An artifact is written for a result that classified **no**
    record. The previous version refused one, on the ground that there was
    nothing to write; what there is to write is the scope and the missing
    evidence, and a run that classified nothing is exactly the run whose reader
    most needs them. `records` is then an empty list and the document says so.
    """
    scope = scope_document(result)
    expected = records_digest(result.records) if result.records else ""
    document = {
        "schema": ARTIFACT_SCHEMA,
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "scope": scope,
        "records": (
            json.loads(serialize_records(result.records).decode("utf-8"))
            if result.records
            else []
        ),
    }
    payload = (
        json.dumps(document, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"
    ).encode("utf-8")
    try:
        destination.write_bytes(payload)
        stored = destination.read_bytes()
    except OSError as failure:
        # The message may name a path or an operating-system string; neither is
        # reported, and the caller states a fixed category.
        raise ArtifactRefused(
            "the classified artifact could not be written or read back"
        ) from failure
    try:
        read_back = json.loads(stored.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as failure:
        raise ArtifactRefused(
            "the classified artifact read back is not readable UTF-8 JSON"
        ) from failure
    if not isinstance(read_back, dict) or read_back.get("scope") != scope:
        raise ArtifactRefused(
            "the scope read back is not the scope that was written"
        )
    stored_records = read_back.get("records")
    if not isinstance(stored_records, list):
        raise ArtifactRefused(
            "the classified artifact read back carries no record list"
        )
    if stored_records:
        restored = deserialize_records(
            json.dumps(stored_records).encode("utf-8")
        )
        if records_digest(restored) != expected:
            raise ArtifactRefused(
                "the classified artifact read back is not the artifact that was "
                "written"
            )
    elif expected:
        raise ArtifactRefused(
            "the classified artifact read back is not the artifact that was "
            "written"
        )
    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phase-5-0-evidence-import",
        description=(
            "Import reviewed observations for Package 5.0's externally produced "
            "evidence cases, classify them, and write the classified artifact. "
            "It runs nothing and can start nothing."
        ),
    )
    parser.add_argument(
        "--observations",
        required=True,
        help=(
            "Path to the supplied-observation payload: JSON, written under "
            f"schema {OBSERVATION_SCHEMA} version {OBSERVATION_SCHEMA_VERSION}."
        ),
    )
    parser.add_argument(
        "--run-id",
        default="",
        help=(
            "The run the observations were collected against. Supplied by the "
            "operator; every record must name the same one."
        ),
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help=(
            "Bind this import to the synthetic target identity, for a payload "
            "whose records declare synthetic_fixture custody. A synthetic "
            "payload and a real target are refused against each other, so a "
            "fixture can never be read as an observation of the approved target."
        ),
    )
    parser.add_argument(
        "--artifact-out",
        default="",
        help=(
            "Where to write the classified evidence artifact. It is written, "
            "read back, deserialized and digest-compared before the path is "
            "reported; without this option nothing is written and nothing is "
            "claimed. It is the **classified evidence**, not the run record."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    plan = build_concrete_plan()
    sources = read_covered_sources()
    digest = ReviewManifest.build(plan, sources).digest()
    target_identity = (
        SYNTHETIC_TARGET_IDENTITY if args.synthetic else plan.target.identity
    )

    try:
        payload = Path(args.observations).read_bytes()
    except OSError:
        sys.stderr.write(
            "REFUSED — the supplied observation payload could not be read.\n"
        )
        return REFUSED_EXIT_CODE

    try:
        result = import_observations(
            payload,
            plan=plan,
            target_identity=target_identity,
            run_id=args.run_id,
            review_manifest_digest=digest,
        )
    except (ObservationRefused, HarnessError) as refusal:
        sys.stderr.write(f"REFUSED — no observation was accepted.\n{refusal}\n")
        return REFUSED_EXIT_CODE

    written = NO_DESTINATION
    if args.artifact_out:
        try:
            written = str(write_artifact(result, Path(args.artifact_out)))
        except (ArtifactRefused, ObservationRefused) as refusal:
            written = f"no — {refusal}"

    counts = summarize(result.records)
    sys.stdout.write(
        f"CLASSIFIED — nothing was executed and nothing can be.\n"
        f"  target             : {target_identity}\n"
        f"  review manifest    : {digest}\n"
        f"  scope              : {result.scope}\n"
        f"  records            : {len(result.records)} "
        f"({', '.join(f'{name} {count}' for name, count in counts.items()) or 'none'})\n"
        f"  covered (band 7)   : {', '.join(result.covered) or 'none'}\n"
        f"  missing (band 7)   : {', '.join(result.missing) or 'none'}\n"
        f"  unresolved cases   : {', '.join(result.unresolved_cases) or 'none'}\n"
        f"  outside this scope : {', '.join(result.outside_scope) or 'none'}\n"
        f"  custody            : {', '.join(result.custody_levels) or 'none'}\n"
        f"  synthetic fixture  : {result.synthetic}\n"
        f"  band 7 coverage    : "
        f"{'complete' if result.band_7_coverage_complete else 'incomplete'}\n"
        f"  band 7 outcome     : "
        + (
            "no record was classified"
            if not result.records
            else "every classified record passed"
            if result.band_7_records_all_passed
            else "not every classified record passed"
        )
        + "\n"
        f"  disqualifications  : "
        f"{'; '.join(result.structural_disqualifications) or 'none in scope'}\n"
        f"  overall complete   : WITHHELD\n"
        f"  operationally      : WITHHELD\n"
        + "".join(f"      · {reason}\n" for reason in result.withheld)
        + f"  artifact           : {written}\n"
    )
    if written.startswith("no — the classified artifact") or written.startswith(
        "no — the scope"
    ):
        return REFUSED_EXIT_CODE
    # **R16, EH-R16-3.** Never 0. Overall completeness is withheld, so there is
    # no result this program can report as complete, and a caller that treated a
    # zero exit as *"the evidence is in"* would be treating a Band-7 partial as
    # the whole. The distinction it can still make is whether Band 7's own
    # coverage held, and that is in the summary and in the artifact.
    return INCOMPLETE_EXIT_CODE


if __name__ == "__main__":  # pragma: no cover - the entry point itself
    raise SystemExit(main())
