"""The evidence cases the reviewed design **requires**, and the check that the
generated plan either produces each one or says why it does not.

## Why this module exists — Blocking finding EH-R13-4

R12's generator emitted no `UnresolvedStep` and `ConcretePlan.is_executable` was
therefore `True`. That was read as *"the plan is complete"*, and it was not a
statement about completeness at all: `is_executable` asks whether every step the
generator **tried** to express could be expressed, and a case the generator never
tried to express is invisible to it.

Two whole groups of required evidence were invisible in exactly that way.

* **Band 5 produced no capability-matrix operation.** It emitted seven `capsh`
  vectors ending in the `identity` verb, attributed `JNL-49-<identity>` and
  `JNL-50-<identity>` to them, and stopped. But an identity observation is a
  **prerequisite** for those cases, not their result: §2.13.8's `JNL-49` and
  `JNL-50` are one case per capability/artifact pairing — `E4` and `E6`
  attempting to clear the immutable flag on the root-owned archive, `E5`
  clearing a flag and then being denied the open — and none of those operations
  was in the plan. The identity steps kept the case ids, so a reader counting
  case ids found them all present.
* **Band 7 produced nothing at all**, and declared nothing unresolved. Its
  classifiers — `provenance`, `journal` and `manifest` — are pure functions over
  observations somebody supplies, and no step, and no stage of the CLI, supplies
  any. A scripted run could therefore be classified complete with the whole
  provenance, journal-generation and recovery band missing.

## What this module does about it

It states the required cases as data, and `check_case_coverage()` refuses a plan
in which a required case is neither **produced** by a step nor **declared
unresolved** with the conflict it raises. There is no third state: a case that is
not in the plan and not named as missing cannot exist.

## What it does not do

It does not implement the missing experiments. Both groups need something the
R12/R13 review boundary explicitly forbids this remediation from widening:

* the `E4`/`E5`/`E6` experiments are about the **immutable** flag, and the
  reviewed case program's closed verb set can read and clear `FS_APPEND_FL` and
  nothing else. Adding `FS_IMMUTABLE_FL` operations widens the trusted computing
  base's verb table, its arities and what a bounded `ioctl` may do — a maintainer
  decision about the reviewed program, not an implementation detail; and
* Band 7 needs a **supplied-observation ingestion stage** — a way for reviewed
  observations to enter the CLI, be validated and be classified — which is a new
  input surface on the one component that can start privileged processes.

So they are declared unresolved, with the conflict each raises and what would
resolve it, and `ConcretePlan.is_executable` is `False` while they are. That is
the second half of EH-R13-4's required correction — *"explicitly report them as
incomplete and seek a separately approved narrower execution scope"* — and it
makes *"no complete-harness success may be produced with required bands
missing"* structural rather than promised: the executor's second gate refuses a
plan that carries an unresolved conflict, so there is no run to be classified.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .errors import PlanRefused


@dataclass(frozen=True, slots=True)
class RequiredCase:
    """One evidence case the reviewed design requires, and where it comes from."""

    case_id: str
    band: str
    #: What the case asserts, in the design's own terms.
    asserts: str
    #: Where the requirement is stated, so a reviewer can check the row.
    source: str

    def __post_init__(self) -> None:
        for name in ("case_id", "band", "asserts", "source"):
            if not getattr(self, name).strip():
                raise PlanRefused(f"A required case needs a {name}.")


#: §2.13.8's capability-matrix **operations**, and Band 7's journal, provenance
#: and recovery cases. Deliberately not the whole of `TC-5.0-JNL`: this table is
#: the set whose absence R13 found, stated so that absence is checkable, and it
#: grows when a reviewer adds a row rather than when a generator happens to emit
#: an identifier.
REQUIRED_CASES: tuple[RequiredCase, ...] = (
    RequiredCase(
        "JNL-49-E4-CLEAR-ARCHIVE-IMMUTABLE",
        "capability",
        "E4 — every discretionary right and CAP_LINUX_IMMUTABLE, holding neither "
        "A10 nor A11 — attempts to clear the immutable flag on a root-owned "
        "archive file and is refused. The isolating case for R9-A.",
        "package plan §2.13.5c and acceptance row 20; §2.13.8 JNL-49",
    ),
    RequiredCase(
        "JNL-49-E6-CLEAR-ARCHIVE-IMMUTABLE",
        "capability",
        "E6 — E4 plus CAP_FOWNER and identical in every other option — performs "
        "the same clear and succeeds. It is the C-I control that makes E4's "
        "refusal attributable to CAP_FOWNER rather than to anything else.",
        "package plan §2.13.5c and acceptance row 20; §2.13.8 JNL-49",
    ),
    RequiredCase(
        "JNL-50-E5-CLEAR-THEN-DENIED-OPEN",
        "capability",
        "E5 — fbprobe with CAP_FOWNER, CAP_LINUX_IMMUTABLE and a freedomcoord "
        "membership — clears the immutable flag on an archived file and is then "
        "refused the O_WRONLY open with EACCES, because the file is 0440 and "
        "root-owned. It is what proves CAP_LINUX_IMMUTABLE confers no "
        "discretionary access.",
        "package plan §2.13.5c, R8-C and acceptance row 20; §2.13.8 JNL-50",
    ),
    RequiredCase(
        "JNL-51-PROVENANCE-OMITTED",
        "journal",
        "The provenance step is omitted, and init-generation is then unable to "
        "create or register a generation at all — the negative case P5.0-SR1 "
        "requires.",
        "package plan §2.12.5a and the JNL-51 row of the evidence band",
    ),
    RequiredCase(
        "JNL-47-NO-GENERATION-ON-FAILURE",
        "journal",
        "A failure injected in each of Stage 1 … Stage 4 and in cleanup leaves "
        "no journal, no seal, no symbolic link and no registration row.",
        "package plan §2.13.5a R7-A and acceptance row 19; §2.13.8 JNL-47",
    ),
    RequiredCase(
        "JNL-47-RECOVERY-STATE",
        "journal",
        "Cleanup failure after a probe-stage failure and after a fully passing "
        "probe are distinguished, each asserting exit status, safe path "
        "reporting, generation and database absence, residue state, "
        "next-run behaviour and the named operator recovery.",
        "package plan §2.13.2b and acceptance row 19; §2.13.8 JNL-47",
    ),
)


def check_case_coverage(
    *,
    produced: Sequence[str],
    declared_unresolved: Sequence[str],
    supplied_externally: Sequence[str] = (),
) -> None:
    """Refuse a plan in which a required case is in none of the three columns.

    `produced` is every `CommandStep.evidence_case_ids` entry the generated plan
    carries; `declared_unresolved` is every `UnresolvedStep.evidence_case_ids`
    entry; and — **R16, conflict C-7** — `supplied_externally` is every
    `concrete_plan.ExternalCase` the plan declares.

    The third column is not a third way of saying *"absent"*, and — **R16,
    EH-R16-4** — it is not a way of saying *"a producer is described"* either.
    R16's first submission put Band 7's three cases here on the strength of a
    description of coordinator tooling Package 5.0 has not built, which removed
    every unresolved entry from the band and made `is_executable` true again. The
    review returned that: *"Naming `init-generation` and a future table does not
    resolve the evidence dependency."*

    A case belongs in this column only when a **reviewed producer artifact and a
    runnable collection procedure exist**, which `concrete_plan.ExternalCase.
    resolves_coverage` is the check for. Today no case satisfies it and this
    column is empty: Band 7's three are declared unresolved, and their input
    contracts are documentation the manifest pins rather than coverage.

    A named producer, a declared procedure and a validated schema are what make
    the column *safe to use* when it is used. They are not what makes it
    applicable.

    A case in **more than one** column is a refusal: a plan that says it produces
    a case and simultaneously that it cannot, or that it both produces one and
    takes it from outside, is a plan whose completeness nobody can read.
    """
    columns = {
        "produced": set(produced),
        "unresolved": set(declared_unresolved),
        "external": set(supplied_externally),
    }
    made, blocked, external = (
        columns["produced"],
        columns["unresolved"],
        columns["external"],
    )
    overlap = sorted(
        (made & blocked) | (made & external) | (blocked & external)
    )
    if overlap:
        raise PlanRefused(
            f"{overlap} are declared in more than one of produced, unresolved "
            "and externally supplied. A case is in exactly one; a plan that "
            "claims two cannot be read for completeness, which is the property "
            "EH-R13-4 is about."
        )
    covered = made | blocked | external
    missing = sorted(
        case.case_id for case in REQUIRED_CASES if case.case_id not in covered
    )
    if missing:
        raise PlanRefused(
            f"The generated plan neither produces {missing} nor declares them "
            "unresolved. A required evidence case that is absent from the plan "
            "and absent from its unresolved list is invisible to "
            "`is_executable`, which is exactly how Band 5's capability-matrix "
            "operations and the whole of Band 7 came to be missing from a plan "
            "that reported itself executable — Blocking finding EH-R13-4."
        )


__all__ = ["REQUIRED_CASES", "RequiredCase", "check_case_coverage"]
