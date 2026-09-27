# Independent review — provisioning CLI exact-detail admission — 2026-09-18

## Disposition

**Accepted with no finding.** C-P5.0-LAB-V6-P-R3 remediates Blocking finding
**PR-20260918-LAB-V6P-R2-1**. Peter Duscha accepted this recommendation on
2026-09-18, so the finding is **Closed**.

`provisioning_cli._detail()` now asks the provisioner's closed contract about
the original complete string before any bounding or rendering transformation.
Reviewed bare and composed details remain unchanged; whitespace-, control- and
Unicode-altered values and non-string candidates are withheld whole. The
positive regression now submits the provisioner's actual values without
pre-normalizing them.

This acceptance also closes **LAB-V6-P1**: the repository now has an
independently reviewed operator invocation for V12, V4, V9 and V5. The separate
Low issue **LAB-V6-P2** remains Open and deferred.

## Evidence independently checked

Review was repository-local with `TEST_DATABASE_URL` explicitly unset.

- focused provisioning CLI: **114 passed**, two disclosed pytest configuration
  warnings;
- complete V6 provisioner: **131 passed**, two warnings;
- complete `tests/phase_5_0_evidence`: **2,492 passed**, two warnings;
- `test_no_execution.py` plus `test_concrete_plan.py`: **320 passed**, two
  warnings;
- `test_p3_4_static_assets.py`: **110 passed, one known tree-shape failure**,
  two warnings;
- guard tests: **31/31 passed**;
- `compileall` and `git diff --check`: passed; and
- an independent probe withheld fifteen altered bare, composed, discrepancy,
  Unicode-whitespace, control and non-string candidates while preserving the
  reviewed positives.

Fresh non-executing regeneration was byte-identical to the repository manifest
and concrete plan. Review-input digest
`593a734954eb650a6f0080776f88023ecb806d31b3407d7a0e52acd2fc0d2db2` is
reproduced but **not approved for execution**. `plan.is_executable` remains
False.

No SSH, host inspection, provisioning, database operation, controlled write,
participant, generated-vector execution, real boundary/materializer or
`--execute` was performed during review.

## Boundary of acceptance and next action

This closes PR-20260918-LAB-V6P-R2-1 and LAB-V6-P1 only. Peter separately
authorizes **C-P5.0-LAB-V6-P-R4**, assigning Claude as implementing operator for
the operational retry on `oracle-test`: safe synchronization and prerequisite
inspection, then V1, V2, V3, V12, V4, V9 and V5 in that exact order, followed
only by read-only I12/V6 verification and an evidence handback for independent
Codex review.

V7, I3, V8, V10, database access, participant wiring, generated-vector
execution, the evidence harness, a real boundary/materializer and `--execute`
remain unauthorized. Package 5.0 remains not ready.
