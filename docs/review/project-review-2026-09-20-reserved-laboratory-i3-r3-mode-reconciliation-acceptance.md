# Independent review acceptance — I3 R3 mode reconciliation — 2026-09-20

## Decision

Peter Duscha accepts Codex's independent technical and security review of
**C-P5.0-LAB-I3-R3** with no Blocking, Important or Optional finding. The
bounded repository reconciliation is accepted: canonical `R` is created
`root:root 0700`; P2 alone creates its exclusive publication temporary as
`0500`; T1, T6 and §2.3.3 retain the shared `0600` default; and P2 applies and
reads back final `root:root 0555` before exclusive publication.

This acceptance closes the repository review of the two mode discrepancies. It
does not confirm I3 and does not itself authorize synchronization, host
inspection, an operational verifier invocation, V7, a participant, the harness,
a generated vector, database access or `--execute`.

## Accepted evidence

Codex independently traced the creation-mode callers and both P2 paths. With
`TEST_DATABASE_URL` explicitly unset, `tests/phase_5_0_evidence` passed **2642
tests**, with zero failures and zero skips. The guard suite passed **41/41**;
`compileall` and `git diff --check` were clean. Deterministic regeneration
matched both checked-in artifacts byte for byte and reproduced review-input
digest `be9e110f9cc8828ba79aaeec7342fd23182dad54eb261852d68654bf8332762b`.
That digest remains review input, not execution authority.

The web and bot suites were not run because the active restriction required
`TEST_DATABASE_URL` to remain unset, under which their database coverage would
skip while still returning success. No action was taken on `oracle-test`.

## Single next step

The maintainer must issue a fresh, explicit, bounded operational authorization
for Claude to run the separately armed I3 verifier on `oracle-test`, against the
accepted manifest-version-16 tree, in the reviewed root invocation followed by
the reviewed `ubuntu` invocation, with stop-on-refusal/discrepancy/residue rules
and a return for independent Codex evidence review. The superseded 2026-09-19
authorization is consumed and cannot be reused.

Until that authorization is issued, the repository-only restriction remains in
force. I3 is unconfirmed, V7 excluded, V8 and V10 unperformed,
`plan.is_executable=False`, and Package 5.0 not ready.
