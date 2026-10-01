# Codex review — P5.0-R5 RP-11 I1-R1 remediation — 2026-09-28

Reviewer: Codex, independent of the Claude I1-R1 remediation

Reviewed inputs:

* `phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-handback.md`;
* amended `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`,
  SHA-256 `186ff546a7f31ccf16461d0d3fec83978af643bd8d2e63dbac2e9dc2f3a2f9c6`;
* `tests/phase_5_0_evidence/test_rp11_publication_portability.py`, SHA-256
  `1f029491b185e1608c98f0054a6ca9b6545a59f40791126480d6ae0c793d192a`;
* the controlling I1 review and the assigned I1-R1 prompt.

## Result — changes requested

The proposed requirements amendment resolves **RP11-I1-1** in substance: it
consistently replaces the temporary-name/rename language with the intended
unnamed-inode/exclusive-first-link contract, states its platform prerequisites
and failure semantics, identifies the shared I3/RP-11 link primitive as a
contract amendment, defines the behavioural seal, fixes the handback binding
block, and states the capture-tool digest scope.

**RP11-I1-2 remains Open and Blocking**, as the handback correctly reports.
The publication route still fails in this independent review context. One new
Important evidence finding must also be corrected before the I1-R1 remediation
is accepted.

RP-11 remains unmet. Neither operational pass is executable or authorized;
P5.0-R5 remains Blocking, OD-62 G-A remains conditional,
`plan.is_executable=False`, and Package 5.0 remains not ready.

### RP11-I1-R1-1 — Important — the diagnostic prototype does not exercise the proposed check

The amended §9.5.4 check requires, among other things:

* no-follow verification of the probe directory's ownership, exact `0700`
  mode, emptiness and device;
* proof that the probe directory is on the same device as the capture root's
  containing directory;
* writing the complete fixed payload;
* after publication, verifying both inode identity and the exact payload
  bytes; and
* cleanup only after those checks succeed.

The diagnostic `probe_unnamed_publication()` checks only initial emptiness and
`/proc/self`, uses one bare `os.write()` without proving the complete payload
was written, checks the named inode's identity and link count but never opens
or reads it, and unlinks it without verifying its bytes. It also does not
check owner, mode, or same-device binding. The tests therefore do not establish
the handback's claim that the proposed capability-check prototype works; they
exercise only a narrower link-and-cleanup sketch.

Remediation may either:

1. make the diagnostic prototype and tests faithfully exercise every proposed
   §9.5.4 step that can be tested locally, including complete write, exact
   readback, owner/mode and explicit device comparison; or
2. narrow the handback and test-module claims so they state precisely that the
   code demonstrates only the unnamed-inode link route and cleanup skeleton,
   not the proposed capability check as a whole.

Option 1 is preferred because the purpose of the diagnostic is to establish
that the proposed admission design is implementable without weakening it.

## Independent test result

The new diagnostic module was run with `TEST_DATABASE_URL` explicitly unset:

```text
8 passed, 2 failed, 0 skipped
```

The two failures are the expected context-sensitive paths:

* `test_the_production_route_names_a_linkable_unnamed_inode_once`; and
* `test_the_capability_probe_succeeds_here_and_leaves_the_directory_empty`.

Both fail because the exclusive first link through `/proc/self/fd/N` returns
`FileNotFoundError` / `ENOENT`. The recorded facts still show CPython 3.12.3,
Linux 6.8.0-139-generic, ext4 under `/tmp`, procfs at `/proc`, supported Python
follow/dir-fd APIs, and `/proc/self` resolving to the caller. This narrows but
does not resolve the execution-context cause. It confirms the amended draft is
right to keep the selected runtime and successful §9.5.4 check as blockers.

The earlier **991 passed, 179 failed, 0 skipped** focused result remains the
applicable independent result for the unchanged production source. Claude's
1170-pass result is valid only for its reported execution context and does not
establish portability.

## Requirements review

Subject to the Important evidence correction above, the amended contract is
internally consistent on the reviewed points:

* P-5 through P-8 preserve file-before-name ordering, non-replacement and the
  containing-directory durability barrier;
* failures before, during and after the exclusive link have fail-closed,
  bounded residue semantics with no retry or repair;
* X-1 through X-4, stop/finalization ordering and unadmitted-object treatment
  remain consistent;
* the two users of the single `os.link` call site have distinct, explicit
  follow policies and must be re-reviewed together;
* the behavioural terminal seal is explicitly not represented as OS-level
  write protection;
* the binding block is exact, digest-authenticated and the only handback
  content B0-RA parses; and
* C-11 and the launcher environment remain explicit blockers rather than being
  guessed or silently wired.

The amended draft is still only a proposal. This review does not accept it on
Peter Duscha's behalf, pin its digest, approve the implementation, or close
either operational gate.

## Checks and limits

Performed:

* read the governing agreement, required implementation-plan sections, active
  handover and restriction banner;
* inspected the assignment, handback, amended contract, scoped diff,
  diagnostic module and unchanged production interfaces;
* independently re-derived both returned SHA-256 values;
* ran the new diagnostic module locally with `TEST_DATABASE_URL` unset; and
* ran `git diff --check`, which was clean.

Not performed because the active assignment remains repository-only: SSH,
synchronization, network or remote-host inspection, database access, `sudo`,
provisioning, controlled writes, reboot, verifier, evidence band, harness
`--execute`, real capture-root use, protected-artifact access and secrets scan.
The full bot/web suites and `oracle-test` were not run. This review creates no
host or operational authority.
