# Codex technical re-review — LAB-1 run-record binding remediation, R2

Date: 2026-09-12. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Submission: [Claude handback](project-review-remediation-2026-09-12-lab1-handback.md).

## Recommendation

**Changes requested.** The cause/content correction is sound: independent
validation now requires the exact canonical residue and configuration recovery
procedures for their respective causes, refuses either procedure without its
cause, and refuses missing or unknown document keys. The incompatible run-record
contract is also correctly moved to schema version 3. One Important read-back
integrity defect remains.

## Finding

### PR-20260912-LAB1-2 — Important — raw substituted read-back bytes are accepted

`execution/artifact.py::write_run_record()` reads bytes, decodes and parses them,
then passes only the parsed mapping to `_read_back_matches()`. That helper compares
the mapping with the emitted document and compares a fresh canonical
re-serialization with the originally serialized bytes. It never receives or
compares the bytes actually read from the destination.

Consequently the public writer accepts altered read-back bytes whenever JSON
parsing collapses them to the same mapping. Two independent local reproductions
were accepted:

```text
read_back = b"\n" + serialized + b"\n"                    -> accepted
read_back = serialized with a duplicate schema_version=3  -> accepted
```

The duplicate-key case is especially material: duplicate JSON member names are
ambiguous across readers, while this writer claims that the read-back is exactly
the document serialized from the outcome. The handback's statement that “the
bytes are the ones that were written” is therefore not established.

Required correction: retain the raw bytes returned by `destination.read_bytes()`
and require exact byte equality with `serialized` before or alongside parsing and
schema validation. Add public-writer regressions for at least changed whitespace
and a duplicate key that resolves to the same value, plus a negative control that
fails when the raw-byte comparison is gutted. Keep fixed refusal messages and the
existing canonical cause/content checks.

## Evidence and limits

- Focused run-record module: **93 passed**.
- LAB-1 focused set (`test_feasibility.py`, `test_plan_and_cleanup.py`,
  `test_r13_remediation.py`): **232 passed**.
- Structural no-execution suite: **217 passed**.
- `git diff --check`: passed.
- The two public-writer reproductions above were run with `TEST_DATABASE_URL`
  unset through the permitted local historical interpreter
  `/opt/discord-bots/venv-web/bin/python` (Python 3.12 / pytest 8.4.2).

No SSH, synchronization, host inspection, preflight, provisioning, database
operation, generated-vector execution, `--execute`, or real execution was
performed. The full bot, web, Foundry and synthetic harness figures in the
handback were not rerun in this review; they remain implementer evidence, not
independent evidence from this pass.

LAB-1 is not closed. C-7 remains unresolved, EH-R16-1 remains Open,
`is_executable` remains False, the twelve target facts remain unconfirmed,
Package 5.0 remains not ready, package-level P5.0-R5 remains Blocking, and OD-62
remains Open.
