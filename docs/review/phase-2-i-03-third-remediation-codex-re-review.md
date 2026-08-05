# Phase 2 I-03 third remediation — Codex independent implementation re-review

Date: 2026-08-05

Role: Independent Reviewer under implementation plan §§0.3 and 16.4

Scope: the uncommitted working tree on `docs/platform-plan`, with `HEAD` at
`c8a3da9`: final-target publication, I-1 storage outcomes, reproducibility of
the test evidence, and preservation of I-2 durability behaviour.

This is a recommendation, not approval. Peter Duscha records the gate decision.
No fix was implemented during this review, no Foundry module was installed, and
no Foundry world storage or player data was accessed.

## Result

**The publication Blocking finding is resolved. I-1 is resolved, the automated
evidence is independently reproducible, and I-2 remains preserved. I found no
new Blocking implementation finding. I found one Important evidence-accuracy
finding.**

The implementation may proceed to correction of the evidence record and the
remaining owner-controlled operational checks. This recommendation does not
close I-03 or the Phase 2 gate.

## Important finding I-3R-1 — the handoff overstates temporary cleanup

The third-remediation request says that “no temporary survives success or an
ordinary failure” because `_discard` runs on each path. Running `_discard` does
not establish removal: it intentionally swallows every `OSError`.

The implementation, operations document, and regression test correctly state
the actual contract. If cleanup fails after publication, `store()` returns
success after syncing the directory and a private `.incoming-*` hard link may
remain. `test_a_failing_cleanup_leaves_the_published_artifact_alone` explicitly
asserts that one survives. This does not endanger the published checksum entry,
and the leftover remains private and unservable, but the review evidence's
structural-guarantee table is false and could mislead storage-capacity or hygiene
assessment.

Required remediation: correct the third-remediation review request and any
controlled record that repeats the absolute claim. State the implemented
best-effort cleanup contract and operator hygiene requirement. No code change is
required by this finding.

## Publication finding disposition

`os.link` with both directory descriptors is a create-if-absent operation for
the final name. It cannot replace the destination. On `EEXIST`, `_publish`
reuses the same `_holds` path used before writing: anchored `O_NOFOLLOW` open,
descriptor `fstat`, ownership/mode/type checks, and hashing from that descriptor.
An unsafe or mismatched entry is refused without repair, unlink, or replacement.

`_discard` can only reach names beginning `.incoming-`; every caller supplies an
internally generated temporary or probe name. It cannot remove a checksum entry.
The link, best-effort temporary removal, then directory `fsync` ordering preserves
the publication/durability contract. A failed directory sync leaves the valid
target available for a retry, and the retry revalidates and syncs it.

The startup hard-link probe is sufficient for the property the implementation
needs: the configured filesystem accepts a hard link and refuses creation at an
existing destination. Its cleanup is subject to the same best-effort limitation
described in I-3R-1.

## I-1 disposition

The three outcome sentences are supportable on their call paths:

- `UNCHANGED` is used before this process publishes a checksum entry;
- `PRESERVED` is used only when a checksum-named entry was encountered and the
  code does not repair, replace, or remove it; and
- `UNRESOLVED` makes no positive durable-state claim and remains the conservative
  default.

Passing `PRESERVED` from the `_holds` and `load` callers, while passing
`UNCHANGED` for verification of this attempt's disposable temporary, is the
right distinction. The behavioural race tests tie the stronger preservation
claim to bytes, mode, and inode rather than relying on the textual guard.

## Test-evidence and I-2 disposition

The bounded `TrustedAncestors` seam is acceptable. It has no environment or
deployment configuration surface, production defaults to an unbounded walk,
and separate tests exercise that default and the ancestor rule directly using
real filesystem metadata. Scoping unrelated publication/lifecycle tests to
directories created by pytest improves reproducibility without weakening the
production policy.

The deterministic two-store test enters the precise publication window and is
stronger evidence for the race contract than an uncoordinated stress test. A
multi-process test remains useful residual evidence, not a condition for this
remediation.

I-2 remains intact: a directory-sync refusal is `UNRESOLVED`, does not remove
the published checksum entry, commits no submission result, and a retry validates
and reuses the same artifact before syncing the directory again.

## Design decisions

- The `os.link` design is acceptable. A private `renameat2(RENAME_NOREPLACE)`
  syscall binding would add platform and marshalling risk without improving the
  required no-overwrite property.
- The bounded ancestor walk is acceptable as a test-only injected policy. It
  does not need escalation to the Acceptance Authority as an architecture or
  production-policy change.

## Verification performed

```text
Foundry module: 81 passed, 0 failed
Focused Python suites: 373 passed
Full Python suite: 1941 passed, 1 warning, no skips reported
compileall: passed
alembic check: No new upgrade operations detected
git diff --check: passed
```

The warning is the pre-existing `discord.player` deprecation warning for
`audioop`. No formatter, linter, or type checker is configured, so none was run.

The supervised browser/CORS check, live second-client credential observation,
cross-account storage experiment, multi-process publication experiment, and
operations rehearsals §§6–7 were not performed and remain outside this review's
automated evidence.
