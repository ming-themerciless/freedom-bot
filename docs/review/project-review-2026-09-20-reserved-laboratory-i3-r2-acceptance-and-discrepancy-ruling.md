# Independent review acceptance and discrepancy ruling — I3 R2 — 2026-09-20

## Decision

Peter Duscha accepts Codex's independent technical and security review of
**C-P5.0-LAB-I3-R2**. The bounded repository implementation is accepted with no
Blocking or Important finding. This acceptance does not confirm I3 and does not
authorize an operational verifier invocation, synchronization, host inspection,
V7 initialization, a participant, the harness, a generated vector, database
access or `--execute`.

## Discrepancy ruling

The two reported contract discrepancies are resolved in favour of runner
contract r6 and the maintainer's controlled ruling:

1. The concrete plan's canonical `R` creation mode is **`0700`**, not `0755`.
   `R` contains security-sensitive execution evidence and has no requirement for
   non-root traversal.
2. P2's exclusive temporary creation mode is **`0500`**, not `0600`. The
   already-open writable descriptor remains the authority for completing and
   synchronizing the write; the descriptor is then used to apply the final
   **`0555`** mode before exclusive publication.

The `0500` choice is P2-specific. It must not change the shared `0600` default
used by T1, T6 and §2.3.3. The implementation should expose an explicit
creation-mode parameter with the existing safe `0600` default and pass `0500`
only for P2.

## Required next action

One bounded repository-only remediation must reconcile the two values in source,
tests, r6 and deterministically generated artifacts. It must add regression
coverage proving that `mkroot` creates `R` as `0700`, that P2 alone creates its
temporary as `0500`, that the other publication contexts remain `0600`, and that
P2 applies final `0555` before publication. The result returns for fresh
independent Codex technical and security review.

Until that review is accepted, no operational I3 invocation is authorized. I3
remains unconfirmed, V7 remains excluded, V8 and V10 remain unperformed,
`plan.is_executable=False`, and Package 5.0 remains not ready.

## Review evidence

The accepted review traced the verifier contract through its admission,
publication, observation, cleanup and safe-output paths. The complete local
`tests/phase_5_0_evidence` suite passed **2637 tests** with
`TEST_DATABASE_URL` unset; the focused review selection passed **524 tests**;
`compileall` and `git diff --check` were clean. No host action was taken.
