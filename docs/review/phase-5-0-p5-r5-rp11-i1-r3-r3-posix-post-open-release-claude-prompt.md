# Claude prompt — bounded PosixFilesystem post-open descriptor-release remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R3`

Date: 2026-09-29

Assignee: Claude, implementing agent

Independent reviewer: Codex

State: **assigned repository-only. Stop after handback for independent Codex
review.**

## 1. Objective

Repair the two post-open kernel-descriptor leaks observed during the earlier
`DurableRecordStore` lifecycle remediation:

1. `PosixFilesystem.create_file` does not release the descriptor returned by
   `os.open` if `ObjectIdentity.of`/`fstat` refuses, or if the optional initial
   `data` write refuses; and
2. `PosixFilesystem.openat` does not release the descriptor returned by
   `os.open` if `ObjectIdentity.of`/`fstat` refuses.

This is a bounded reliability correction in
`tools/phase_5_0_evidence/execution/descriptors.py`. It does not reopen the
repaired `DurableRecordStore` defect and does not authorize RP-11 wiring.

## 2. Required behavior

After `os.open` returns successfully, the method owns that descriptor until it
returns a `Descriptor` to its caller. On every failure before that return:

* release the acquired descriptor exactly once;
* never retry a failed close, because the descriptor number may already have
  been reused;
* remove any partially registered descriptor from the filesystem object's
  tracking table before or as part of release;
* preserve and re-raise the first causal failure rather than replacing it with
  a cleanup failure;
* do not unlink, rename, truncate, retry, repair or otherwise change a pathname
  to conceal the failure; in particular, a file exclusively created before an
  optional initial write failure remains present exactly as the failed call
  left it; and
* do not release inventory-owned traversal or synchronizable descriptors.

Successful `create_file` and `openat` behavior, returned descriptor metadata,
creation modes, no-follow behavior, refusal classifications and every existing
caller contract must remain unchanged.

## 3. Required regression coverage

Add focused tests that fail against the current implementation and use real
kernel descriptors in pytest temporary directories. At minimum prove:

1. `create_file` releases its new descriptor when identity acquisition fails;
2. `openat` releases its new descriptor when identity acquisition fails;
3. `create_file(data=...)` releases its new descriptor when the initial write
   fails after creation;
4. each acquired descriptor is released exactly once and no inventory
   descriptor is released;
5. a cleanup/close failure is not retried and does not replace the first causal
   failure;
6. the created name remains after an initial-write failure and no cleanup
   mutation occurs; and
7. ordinary successful `create_file`, `create_file(data=...)` and `openat`
   calls still transfer ownership to the caller, which remains responsible for
   their normal release.

An optional `/proc/self/fd` count may supplement the ownership oracle on Linux,
but it must not be the only oracle. Do not add an autouse cleanup fixture, force
garbage collection, raise a descriptor limit, weaken an assertion or hide a
leak through test teardown.

## 4. Authorized files and artifacts

Claude may change only what this remediation requires:

* `tools/phase_5_0_evidence/execution/descriptors.py`;
* focused tests under `tests/phase_5_0_evidence/`;
* `tools/phase_5_0_evidence/review_manifest.py` only to advance the manifest
  version and record this covered-source change;
* the two generated review artifacts produced by a harness dry run;
* this work's handback; and
* concise current-state, change-log and handover pointers required to return
  the work for review.

Because `descriptors.py` is a covered source, increment the manifest from
version 25 to version 26, regenerate the manifest and concrete plan by **dry run
only**, and report their exact SHA-256 values and review-input digest. These are
review inputs, not approvals and not execution authority.

Do not change the operational-evidence draft, RP-11 publication semantics,
retention semantics, `DurableRecordStore`, C-11, launcher environment policy,
any command wiring, any gate, or any existing finding disposition.

## 5. Verification

Run, serially on the repository host with `TEST_DATABASE_URL` unset, bytecode
disabled and pytest's cache provider disabled:

1. the new focused regressions;
2. all tests directly covering `PosixFilesystem` and lifecycle storage;
3. `tests/phase_5_0_evidence` with the soft descriptor limit lowered to 1024
   in a subshell; and
4. the same whole package at the default descriptor limit.

Run the harness only in dry-run mode to scratchpad paths and prove both
generated artifacts are byte-identical to the checked-in versions. Also run
`git diff --check`. Do not claim bot, web, database or operational coverage.

## 6. Restrictions

Repository-only. **No SSH, rsync, synchronization, network or host inspection,
`sudo`, database access, provisioning, controlled write, reboot, verifier,
evidence band, harness `--execute`, real participant, real capture root,
operational path, protected-artifact access, secrets scan, commit or push is
authorized.** Do not read or modify credential files.

RP-11 remains unwired and unmet; C-11 and the pinned launcher environment
remain unresolved; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## 7. Handback and review gate

The handback must include the requirements implemented, files changed, exact
before/after hashes, descriptor-ownership reasoning, tests and exact results,
dry-run digest and artifact hashes, security implications, checks not run,
rollback/recovery, unresolved questions and reviewer focus.

Claude must stop after the handback. Codex independently reviews the exact
returned bytes, failure precedence, descriptor ownership, regressions,
manifest/artifact regeneration and both whole-package runs. Peter Duscha alone
records acceptance or further direction after that review.
