# Codex technical re-review — LAB-1 remediation, 2026-09-12

## Recommendation

**Changes requested.** The separation of residue and configuration recovery is
sound in the in-memory cleanup outcome, feasibility classifier and supplied-
observation schema. The supplied-observation schema version 3 and review-
manifest version 10 changes correctly refuse older records rather than
reinterpret them. One Important run-record integrity finding remains.

## Finding

### PR-20260912-LAB1-1 — Important — the run-record reader accepts a substituted recovery procedure

`execution/artifact.py::validate_run_record()` checks only that each
`residue_recovery_procedure` entry has the three expected keys, a consecutive
order and non-empty strings. It never compares the read-back value with
`journal.RECOVERY_PROCEDURE`, with the procedure serialized from the outcome,
or with the cleanup state and residue that require it. Consequently a schema-2
S-B record containing one arbitrary ordered instruction is accepted as valid.

Independent local reproduction:

```text
cleanup.state = S-B
residue_recovery_procedure = [
  {order: 1, action: "IGNORE THE RESIDUE AND CONTINUE",
   rationale: "arbitrary replacement"}
]
validate_run_record(..., expected_steps=0) -> accepted
```

This contradicts the validator's stated claim that the bytes read back are the
whole of what the run produced, and leaves the new schema unable to distinguish
the named five-step recovery from any well-shaped substitute. Reordering is a
useful negative case but does not cover substitution.

Required correction: on the writer/read-back path, require exact equality with
the residue procedure serialized from the outcome (and require the canonical
five-step procedure when residue is present, empty when it is absent). Add
negative regressions for changed action/rationale text, a shorter ordered list,
an arbitrary ordered replacement, a procedure present without residue and
residue present without the procedure. The same validation should bind the
configuration recovery and retained-capture cause if that existing field is
within the corrected run-record contract.

## Evidence and limits

- Read the active handover, `.agents/AGENTS.md`, implementation-plan §§0, 12,
  13, 16 and 20, and the disposable-server restriction banner.
- Inspected the LAB-1 implementation, tests, runner contract r6, disposition,
  observation schema and generated-manifest changes.
- Ran the direct Python reproduction above successfully.
- The focused pytest command could not run with `/usr/bin/python3` because that
  interpreter has no `pytest`; this is unavailable, not a pass.
- No SSH, synchronization, host inspection, preflight, permission change,
  provisioning, database operation or real execution was performed.

LAB-1 is not closed. C-7 remains unresolved, EH-R16-1 remains Open,
`is_executable` remains False, Package 5.0 remains not ready, package-level
P5.0-R5 remains Blocking, and OD-62 remains Open.

