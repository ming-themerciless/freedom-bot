# Independent review — R2 completeness remediation requires R3

Date: 2026-10-06

Reviewer: Codex, independent reviewer

Reviewed work ID:
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR2-20261006-04`

## Disposition

R2 is not ready for acceptance. Its HF-15 correction is sound, but two
Blocking D-7 findings and one Important evidence-retention finding require a
repository-only R3 remediation and independent re-review. Nothing in this
review authorizes host access, retained-evidence access, cleanup, H-0G or a
later slice.

## Findings

### R2-F1 — Blocking — CK-9 is not an executable closed contract

CK-9 requires the top-level entries of `.git` to be a subset of a closed set,
but says that set is “to be fixed by review” and asks the reviewer to select
its evidentiary basis. The R2 assignment required a bounded inventory. A
future slice cannot implement or evaluate CK-9 fail-closed while its accepted
set remains an open design question.

R3 must replace CK-9 with a complete deterministic rule, grounded in the
accepted retrieval procedure and Git state requirements. It must not leave a
value, allowlist or security decision for the acceptance reviewer to invent.

### R2-F2 — Blocking — CK-3 claims an escaping-symlink control it does not perform

CK-3 verifies that a worktree symlink corresponds to a committed Git mode
`120000`, but it does not inspect or constrain the link target. Its “Rejects”
column nevertheless says it rejects “symlinks that escape.” The pinned tree
contains the intentional absolute `venv` symlink, so a blanket ban on all
tracked symlinks would not accurately model the repository.

R3 must separate inventory from consumption. It must authenticate each
tracked symlink's link text against the pinned tree without dereferencing it,
record absolute or checkout-escaping targets as non-consumable, and require
every repository path actually consumed by an RP-11 slice to have no symlink
in any component and to terminate in an owned, non-writable regular file
whose bytes are covered by the applicable accepted digest. No RP-11 command
may dereference a checkout-escaping symlink as repository source.

### R2-F3 — Important — digests do not reproduce retained evidence bytes

Section 12.4 says no preservation copy is required because durable handbacks
“reproduce the retained bytes' manifests and digests.” Manifests and digests
describe or authenticate bytes; they do not reproduce them. R3 must remove
that rationale. Eligibility for deletion must rest only on explicit closure
or Peter's explicit abandonment of every evidentiary dependency, followed by
the already-required exact-path enumeration, review and separate authority.

## Checks

Local, read-only review only. The R2 prompt, authority and proposal hashes and
reported sizes matched; `git diff --check` passed. No application tests,
network access, `oracle-test` access, retained-path access, cleanup or other
host mutation was performed.

