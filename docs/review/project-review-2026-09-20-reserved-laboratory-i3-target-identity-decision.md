# Maintainer decision — I3 target identity — 2026-09-20

## Decision

Peter Duscha chooses **Option A** for LAB-I3-TARGET-1.

The approved target model must keep the operational SSH alias and the kernel
nodename as separate facts:

- `host` remains **`oracle-test`**, the stable operational alias used by the
  runbook, planner and operator-facing records; and
- a separately named approved nodename fact is **`Test`**, the value the target
  reports through `os.uname().nodename` and the value I3 admission must compare
  with that observation.

The verifier must not compare a kernel nodename with the SSH alias. The two
values identify different layers and must not be collapsed into one overloaded
field.

## Rationale

Option A preserves the established operational name while making the local
admission observation explicit and auditable. It avoids changing the host
merely to satisfy a modelling mismatch, and avoids redefining every existing
use of `host` to mean a kernel nodename.

The new fact is part of approved target identity. Adding it therefore must
change `TARGET_IDENTITY_DIGEST`, `CONFIRMATION_TOKEN`, the review manifest and
the review-input digest. The previously accepted digest `be9e110f…` must not be
carried forward as evidence for the reconciled tree.

## Effect and authority

LAB-I3-TARGET-1 is **decided and Closed as a decision blocker**. Repository
reconciliation remains pending and must receive fresh independent Codex
technical and security review before any operational retry is considered.

This decision authorizes only the bounded repository implementation described
by C-P5.0-LAB-I3-R5. It authorizes no SSH, synchronization, host inspection,
deletion of `/tmp/fb-i3-root.out` or `/tmp/fb-i3-root.err`, verifier invocation,
controlled write, V7, participant, evidence-harness execution, generated-vector
execution, database operation, real boundary/materializer or `--execute`.

I3 remains unconfirmed and unperformed; V7 remains excluded; V8 and V10 remain
unperformed; `plan.is_executable=False`; and Package 5.0 remains not ready.

