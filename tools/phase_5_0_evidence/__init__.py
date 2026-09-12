"""Package 5.0 pre-implementation evidence harness — **planning and
classification only. Nothing here executes a privileged command.**

Authority: Peter Duscha approved the bounded pre-implementation evidence harness
on 2026-09-02 (`docs/review/phase-5-0-evidence-harness-authorization-draft.md`).
Claude's controlling handoff is
`docs/review/phase-5-0-evidence-harness-implementation-prompt.md`. That handoff
authorizes **evidence scaffolding only**: the harness is written and tested here,
its exact command and cleanup plan is produced at
`docs/review/phase-5-0-evidence-harness-execution-plan.md`, and **Codex must
approve that plan before a single mutation-bearing command runs**.

Package 5.0 remains `not ready`. Nothing in this package implements migration
`0014`, production schema, production application behavior, deployment, authority
transition or cutover, and nothing here closes P5.0-R4, P5.0-R5, A-5.0-3,
A-5.0-4, A-5.0-5 or any check `C-1`/`C-3`/`C-4`.

## The modules

| Module | What it owns |
|---|---|
| `errors` | the three refusals, typed so a caller cannot confuse them |
| `records` | the evidence record, the closed outcome grammar, the classification rule and the deterministic artifact |
| `targets` | the disposable target, and every forbidden path and database guard |
| `plan` | argument-vector command planning, mutation declaration, and `DryRunRunner` |
| `case_runtime` | **C-2** — the one named interpreter, the closed case-program grammar, and the two reviewed interpreter facts |
| `expectations` | the typed, closed semantic expectations `P-05` and `E1 … E8` are compared against before a step may be satisfied |
| `binding` | **C-5** — the four late-bound disposable names and the declared substitution sites |
| `cleanup` | bounded, reverse-order, idempotent cleanup derived from declared mutations, and §2.13.2b's S-A/S-B/S-C state machine |
| `sudoers` | **C-1** — analysis of drop-in content an authorized reader supplies |
| `hba` | pre-change and post-change `pg_hba.conf` / `pg_ident.conf` ordering and breadth analysis |
| `identity` | **C-4** / `JNL-52` — §2.12.2's canonical membership table and the access matrix |
| `capability` | `JNL-49` / `JNL-50` — `E1 … E8`, the `capsh` construction, the two control forms, and `E7`'s ten reviewed target facts |
| `filesystem` | **C-3** / §2.13.2a — the four probe stages and the attribution table |
| `manifest` | `JNL-46` — the two manifest functions and the closed two-region partition |
| `provenance` | `JNL-51` / `JNL-53` — the four provenance facts, and the missing-provenance refusal P5.0-SR1 requires |
| `journal` | P5.0-R5 — generation lifecycle, the five refusal conditions, and the named operator recovery |

## What this package is

Three things, and deliberately not a fourth.

1. **Command planning.** Every privileged step is modelled as an
   *argument vector* (`plan.CommandStep`), never as a shell string, so a reviewer
   reads exactly what would be executed and no quoting question exists. The plan
   names its disposable target and **every mutation it intends**, and a
   mutation-bearing case refuses to be planned unless the plan declares it.
2. **Observation classification.** The bands — `sudoers`, `pg_hba`/`pg_ident`
   ordering, `FS_APPEND_FL`, the `E1 … E8` capability matrix, the manifest
   functions, reviewed-source provenance and the journal generation lifecycle —
   are implemented as **pure functions over supplied observations**. They decide
   `passed` / `failed` / `inconclusive`, and they apply the package plan's
   standing rule that a failed positive control or a mismatched identity is
   `inconclusive` and **never** a pass (stop conditions 10i, 10m, 10n).
3. **Cleanup planning.** Bounded, ordered, idempotent, and unable to express a
   recursive or unresolved deletion (`cleanup`).

The fourth thing — **a runner that actually executes** — is not here. `plan`
defines a `Runner` protocol and ships exactly one implementation, `DryRunRunner`,
which records intent and executes nothing. **No module in this package imports
`subprocess`, `os.system`, `os.exec*`, `os.popen`, `socket`, `http`, `urllib`,
`ssl` or a database driver**, and `tests/phase_5_0_evidence/test_no_execution.py`
asserts that by reading the source. Adding an executing runner is a separate,
separately reviewed change that may be made only after Codex's pre-execution
approval of the named target, the exact commands and the cleanup.

## Why it is shaped this way

The evidence this package exists to produce is evidence about *refusals*. A
refusal is only evidence when its cause is attributable, so every negative case
here carries the positive control the package plan names for it, the control is
evaluated first, and the negative result is not interpreted at all when the
control did not pass. That rule is `records.classify`, and it is the one piece of
logic every band shares.

The control's result is a fact about **another record**, so it is read from that
record and never from a copy of its status stored beside the dependent case
(EH-R2-1). Each band declares, per case, whether the case is a `CONTROL`, a
`DEPENDENT` or `STANDALONE`; a dependent case is classified beside the control
record itself; and reading an artifact back resolves every reference against the
other records in the same artifact, refusing a missing, duplicated,
self-referential, cyclic, cross-band or inadmissible one.

The second shared rule is that **an unrun case is `not_run`, never a pass.** No
function in this package returns `passed` for a case whose observation it was not
given.
"""
from __future__ import annotations

#: Bumped whenever a record's field set or its serialization changes, so an
#: artifact produced by an older harness cannot be silently compared with a newer
#: one. It is the first field of every serialized record.
EVIDENCE_SCHEMA_VERSION = 3

#: The harness's own identity, recorded in every artifact it emits.
HARNESS_NAME = "phase-5-0-evidence-harness"
HARNESS_VERSION = "0.7.0-pre-execution"

__all__ = [
    "EVIDENCE_SCHEMA_VERSION",
    "HARNESS_NAME",
    "HARNESS_VERSION",
]
