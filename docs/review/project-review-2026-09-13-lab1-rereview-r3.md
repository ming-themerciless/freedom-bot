# Codex technical re-review — LAB-1 raw read-back byte binding remediation, R3

Date: 2026-09-13. Direction: C-P5.0-LAB-1, reserved disposable laboratory.
Submission: [Claude handback](project-review-remediation-2026-09-13-lab1-r2-handback.md).

## Recommendation

**Accepted in the reviewed local scope; no findings.** PR-20260912-LAB1-2 is
resolved. `write_run_record()` retains the exact bytes returned by
`destination.read_bytes()` and `_read_back_matches()` requires
`raw == serialized` as its first, short-circuiting conjunct. The writer then
requires the parsed mapping to equal the emitted document and applies the
unchanged schema-3 validation, including the exact recovery procedure for each
present cause. Added whitespace, re-indentation and duplicate top-level or
nested JSON members can no longer be reported as the document written.

The public-writer regressions exercise ten byte-distinct inputs that parse to
the emitted mapping. The negative control removes only the raw-byte conjunct and
accepts all ten again; faithful read-back and all four accepted cleanup-cause
combinations remain accepted. The run-record, supplied-observation and review-
manifest schema versions correctly remain 3, 3 and 10 respectively.

## Independent evidence and limits

- Run-record module: **121 passed**.
- Focused LAB-1 set (`test_feasibility.py`, `test_plan_and_cleanup.py`,
  `test_r13_remediation.py`, `test_r16_c6_c7_c8.py`,
  `test_r16_remediation.py`): **364 passed**.
- `artifact.py` SHA-256 independently matches the manifest entry:
  `64ad95ce188316111c4f3f205580f500bf85ce3992882b2ecd1fe7af46006e27`.
- `git diff --check`: passed.
- Interpreter: `/opt/discord-bots/venv-web/bin/python`, with
  `TEST_DATABASE_URL` unset under the task-specific restricted-local exception.

No SSH, synchronization, host inspection, preflight, provisioning, database
operation, generated-vector execution, `--execute`, or real execution was
performed. The full bot, web, Foundry, structural and complete synthetic-harness
figures in the handback were not rerun in this review; they remain implementer
evidence rather than independent evidence from this pass.

This review closes the local LAB-1 remediation only. C-7 remains unresolved,
EH-R16-1 remains Open, `is_executable` remains False, the twelve target facts
remain unconfirmed, Package 5.0 remains not ready, package-level P5.0-R5 remains
Blocking, and OD-62 remains Open. No execution is authorized.
