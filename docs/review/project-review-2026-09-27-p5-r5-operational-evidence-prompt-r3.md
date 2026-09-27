# Codex review — P5.0-R5 operational-evidence prompt R3 — 2026-09-27

Reviewer: Codex, independent of the Claude R3 remediation

Reviewed bytes:

* `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
* SHA-256: `026edf43935fb8a837911d66f467596e5ebfe31a4da1135e576f0c03a4dd69f7`
* R3 handback:
  `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-handback.md`

## Result — changes requested

The two R2 findings are resolved in substance. Pass A and Pass B now have
distinct capture roots and index chains, and §9.5.3 states one consistent
stop, finalization and read-only transition.

One Blocking evidence-integrity defect remains.

### OP1-R3-1 — Pass B does not verify Pass A's required retention — Blocking

C-8 requires `MI.capture_root_A` and everything beneath it to remain retained
and unmodified throughout Pass B. B0-08 compares the two supplied path values,
checks that `MI.capture_root_B` is absent and promises not to touch Pass A's
root, but it does not verify that Pass A's root still exists or remains bound
to Pass A's recorded durable final-index state. Pass B can therefore be
admitted after Pass A's retained primary evidence has been removed or changed
outside this procedure, violating C-8 without detecting it.

Before Pass B is admitted, a reviewed, non-mutating repository-host check must
verify that:

1. `MI.capture_root_A` is the exact root recorded by the Pass A handback;
2. the root and Pass A's recorded final index state still exist;
3. the re-derived SHA-256 of that final index state equals the capture-index
   SHA-256 recorded by the Pass A handback; and
4. X-4 still validates Pass A's retained chain and bound files without writing,
   repairing, completing, adopting or removing anything.

Absence, mismatch, invalidity or inability to perform the check must stop Pass
B before X-1 creates `MI.capture_root_B` and before any host command. The check
may read Pass A's root only for retention verification. It must not reuse the
root or any of its contents as Pass B evidence, continue Pass A's index chain,
or weaken the rule that Pass A's root remains unmodified.

The correction is requirements-only. Its exact interface and proof remain
part of RP-11's later implementation and review.

## Preserved conclusions

* The separate-root correction OP1-R2-1 is otherwise resolved.
* The ordered-stop correction OP1-R2-2 is resolved.
* The rule that no X-3 attempt is made without a durable *I*-0 is internally
  necessary and acceptable.
* RP-11 remains absent and unmet; neither operational pass is executable or
  authorized.
* P5.0-R5 remains Blocking, OD-62 G-A remains conditional,
  `plan.is_executable=False`, and Package 5.0 remains not ready.

No host command, suite, database operation, secrets scan or protected-artifact
access was performed for this review.
