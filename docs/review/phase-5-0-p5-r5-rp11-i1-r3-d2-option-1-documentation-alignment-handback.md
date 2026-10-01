# Handback — RP-11 Option-1 decision and documentation alignment

Work ID: `C-P5.0-R5-RP11-I1-R3-D2-DOC1`

Date: 2026-09-28

State: **returned repository-only for independent exact-byte review.**

## Outcome

Peter Duscha's Option-1 decision is recorded and propagated through the current
requirements, governance registers, current-state pointers, source/test
documentation and generated review inputs. `RP11-I1-R3-1` is Closed by
decision; `RP11-I1-R3-2` and `RP11-I1-R3-3` are Closed as remediated.

No behavioral source logic changed. The accepted rule remains limited to the
two fixed names Pass A's final state records for one unadmitted regular file:
both names present, one inode, link count two, no third name, metadata only,
never opened, read, digested or admitted. Every other alias shape stops.

RP-11 remains unwired, unaccepted and unmet. C-11 and the pinned launcher
environment remain unresolved; `plan.is_executable=False`; neither pass is
authorized; P5.0-R5 remains Blocking; Package 5.0 remains not ready.

## Archives

The former current status and handover were preserved byte-for-byte and indexed:

* `Handover-information-through-2026-09-28.md` — SHA-256
  `bbffec76f2bc787eebfe3be9d459bc6a017d6f28713161ee21ff015be0e7fc6a`;
* `status-through-2026-09-28.md` — SHA-256
  `c992d327179a2a693b3a7a26cb228a2f4b42b9c95681c868bc25bcc8c0217266`.

The canonical files now contain only current state, restrictions, next action
and archive navigation. Historical prompts, handbacks and reviews were not
rewritten or deleted.

## Exact review inputs

* Operational draft: SHA-256
  `48bef661714c72393d61487470f0ee3619b32ea6d0f126b26dbe43742ca44ce2`.
* `retention_check.py`: SHA-256
  `208bec5a251873a5661e692cd9b541db91629051ef72007336e506fac8803349`.
* `review_manifest.py`: SHA-256
  `709ea407769dd0a46fc5f8131497d9236843744414edd79d74dd549f45cbe983`.
* Manifest version: **25**.
* Review-input digest:
  `f63cf3596a95701e3c24813f5362955dcdb5524e7b4fcaf749159db66f91cdb8`.
* Generated manifest SHA-256:
  `3632270aeaacea6d7b3c80eb515b323d2948bb75ea327a77d207650ff355d4e5`.
* Generated plan SHA-256:
  `f177db4d8abec40769dd93a45a33c15ce44949f7e49a334a27b168437354729c`.

A second dry run produced byte-identical artifacts and reported
`executable=False`.

## Verification

Every pytest process explicitly unset `TEST_DATABASE_URL`, disabled bytecode,
disabled the cache provider, ran serially and included `-rs`.

* RP-11 capture/retention plus structural, manifest, concrete-plan and
  no-execution selection: **774 passed, 0 skipped**.
* `tests/phase_5_0_evidence`, one process, soft descriptor limit 1024:
  **3348 passed, 0 skipped**.
* The same whole package at the default limit: **3348 passed, 0 skipped**.
* Changed Python compilation: passed.
* Scoped and repository-wide `git diff --check`: clean.

Each pytest run emitted only the two known unknown-configuration warnings for
`asyncio_default_fixture_loop_scope` and `asyncio_mode`.

## Restrictions observed

No SSH, synchronization, network or host inspection, `sudo`, database access,
provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, real capture root, protected-artifact access,
secrets scan, commit or push occurred.
