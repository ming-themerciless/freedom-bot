# Codex R2 re-review and RP-11 unadmitted-pair decision — 2026-09-28

Review ID: `C-P5.0-R5-RP11-I1-R3-R2-REV1`

Decision ID: `C-P5.0-R5-RP11-I1-R3-D2`

Reviewed return:
[`phase-5-0-p5-r5-rp11-i1-r3-r2-lifecycle-descriptor-release-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r2-lifecycle-descriptor-release-remediation-handback.md)

Decision input:
[`phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r1-unadmitted-pair-decision-proposal.md)

Disposition: **R2 has no new Blocking or Important finding; Peter Duscha
accepts Option 1; exact amended bytes still require review and acceptance.**

## Independent review

Codex found the descriptor-release remediation technically, operationally and
evidentially sound. Store-owned descriptors are released exactly once after
acquisition on success and failure; inventory-owned and unsuccessfully
acquired descriptors are not released; a failed release is not retried or
reported as success; and publication order, interruption artifacts and barrier
reporting remain intact.

Independent repository-local verification, with `TEST_DATABASE_URL` unset,
bytecode disabled and pytest's cache provider disabled, reproduced:

* the 12 focused descriptor regressions: **12 passed, 0 skipped**;
* the entire evidence package in one process at soft descriptor limit 1024:
  **3348 passed, 0 skipped**;
* the entire evidence package at the default limit:
  **3348 passed, 0 skipped**; and
* a dry-run regeneration byte-identical to both checked-in artifacts, with
  manifest version 24, digest
  `bccd26e59aa94a64dc8888eb6265c68da7d4c8c7d1705d85932e5ebad01a05d7`
  and `executable=False`.

Only the two disclosed unknown-pytest-option warnings appeared. No host,
network, database, operational pass, `--execute`, secret scan, commit or push
occurred.

`RP11-I1-R3-2` and `RP11-I1-R3-3` are **Closed as remediated**. The separate
post-open failure observations in `PosixFilesystem.create_file` and `openat`
should receive a bounded reliability assignment; they do not reopen R2.

## Maintainer decision

Peter Duscha accepts **Option 1: permit the recorded unadmitted staging/final
pair by metadata only**.

The exception applies only when Pass A's final state records both fixed names
as the staging/final pair of one unadmitted regular file, both names are
present, both reach one inode at link count two, and no other name reaches that
inode. The verifier does not open, read or digest either member, and the pair
does not become admitted or evidence. A missing member, divergent inode, third
link, cross-object alias, duplicate category or pair, wrong type, unexpected
name, escape, or incomplete/changing enumeration remains a fail-closed stop.

This choice preserves R5's evidentiary limit for unadmitted objects, matches
the accepted retained-alias publication design and avoids making 15 modeled
post-link interruption states permanently inconclusive without adding an
evidentiary claim.

`RP11-I1-R3-1` is **Closed by maintainer decision**.

## Effect and limits

The decision settles policy only. Current source already implements Option 1,
but stale pending-decision wording and covered-source documentation require a
bounded exact-byte acceptance remediation and independent review. This record
does not accept the operational draft, implementation, digest or manifest as
an executable baseline.

RP-11 remains unwired and unmet; C-11 and the pinned launcher environment
remain unresolved; neither pass is executable or authorized; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; `plan.is_executable=False`; and
Package 5.0 remains not ready.
