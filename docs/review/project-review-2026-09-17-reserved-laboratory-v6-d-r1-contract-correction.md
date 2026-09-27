# Independent review — r6 topology-contract correction — 2026-09-17

## Disposition

**Accepted with no finding.** C-P5.0-LAB-V6-D-R1 repairs Blocking finding
**PR-20260917-LAB-V6D-R1-1**. Peter Duscha accepted this recommendation on
2026-09-17, so the finding is **Closed**.

The operative runner-contract rows now agree with the approved topology:

- `R` is `/var/lib/fb-evidence-p5-0`;
- D1 is the descriptor for `R`'s parent `/var/lib`;
- `/opt/freedom-blades/evidence` and V11 survive only as explicitly labelled
  history or withdrawn rows;
- V6 is recorded as performed on 2026-09-16 but not closed; and
- I12 is the separately authorized post-provision read-only repetition.

The D1 interpretation is supported by `plan.ROOT_ROLE` and
`plan.EVIDENCE_ROLE` naming the disposable root and its parent, by the concrete
plan creating `R` through exclusive `mkdirat` of its final component, and by
the executor retaining D1 only for that creation and the later by-name
identity check. No intermediate provisioned evidence directory remains in the
accepted topology.

## Evidence independently checked

Review was repository-local with `TEST_DATABASE_URL` explicitly unset, under
the active restriction.

- `tests/phase_5_0_evidence/test_v6_provisioning.py`: **131 passed**, two
  existing unknown-pytest-option warnings.
- `.claude/hooks/test_guards.py`: **31/31 passed** — 19 refused and 12 allowed.
- `git diff --check`: passed.
- The contract, correction handback, active handover, status, RAID, decision
  and change records, restriction banner, role definitions and concrete-plan
  creation path were cross-checked.

No SSH, synchronization, host inspection, provisioning, permission change,
database operation, controlled write verification, generated-vector execution,
real participant, real boundary/materializer or `--execute` was performed.

## Boundary of acceptance

This closes only **PR-20260917-LAB-V6D-R1-1**. It approves no digest and grants
no provisioning or execution authority. V6 remains performed-but-not-closed;
I3 remains unconfirmed; V7 remains excluded; V8, V10 and I12 remain
unperformed; `plan.is_executable` remains `False`; C-7, EH-R16-1, LAB-R6,
LAB-X1, P5.0-R5 and OD-62 remain Open; and Package 5.0 remains not ready.

