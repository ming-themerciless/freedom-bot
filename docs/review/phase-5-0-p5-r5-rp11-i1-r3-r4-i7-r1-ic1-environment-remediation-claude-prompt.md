# Claude prompt — remediate I-7 IC-1 exact-environment enforcement

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-I7-R1`

Date: 2026-10-01

Assignee: Claude, remediating implementer

Independent reviewer: Codex

State: **assigned narrow repository remediation and repository-host evidence
only. Stop after the remediation handback for independent Codex re-review.**

## 1. Maintainer decisions

Peter Duscha accepted Codex's recommendations on 2026-10-01:

1. **D-1 is accepted.** R-1's two manifest vectors and R-2 may be consecutive
   entries made by one `enter.py build` invocation over the same read-only
   root. HA-3 remains an explicit residual input; this does not claim to
   eliminate it.
2. **D-2 is not accepted as implemented.** The named environment additions
   may be retained as a bounded clarification only after IC-1 requires their
   exact names and values, negative tests cover missing and changed values, a
   fresh pinned-root IC-1 run passes with byte-identical R-2 outputs, and Codex
   accepts the remediation.

Controlling review and Blocking finding:
[`project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md`](project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md),
`I7-R1-1`.

## 2. Objective

Remediate only `I7-R1-1`: make IC-1 prove the exact environment received by
every class-B/class-E process rather than merely allowing a set of additional
variable names.

The accepted launcher image and decoder result are frozen. Do not redesign or
rebuild them into a different contract. The following returned digests must
remain unchanged:

* image: `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572`;
* listing: `8c1fedee1c717b17a14d7c746669ffcec3c41d155e5cc4c63d24a5f2527cd188`;
* `launch.s`: `b37280d53eecce690210021a793cde5d5b73a8f9c027d187e4bd1338e7e27706`;
* map: `5a8b058084edcb1e3f6f7ddea13b60da6af71102300ea276225ae4ab0e8bc34d`;
* XD source: `84598d0683f377fcdb2282ae8080d07d4ce144e46adcc236d1d0677766038c97`;
* XD spelling table:
  `d20406488804d7d3559917a3d55512d44b40789c018849977d6737a86ba67b66`;
  and
* agreed stream:
  `e1354c29e4abddd115fad9b1f83fd69b3b93aae2971db6a448964baa8edbf8e0`.

Any change to one of those bytes or digests is a hard stop and requires a new,
broader assignment rather than this remediation.

## 3. Controlling inputs

Read completely before editing:

* `.agents/AGENTS.md`;
* the implementation-plan reading map, §0, §13, §16, §17 and §20;
* `docs/review/Handover information`;
* the accepted D2 proposal;
* the I-7 implementation prompt and handback;
* Codex's I-7 review above;
* `infra/rp11-launch/verify/ic1check.py`;
* the IC-1 tests in `tests/test_rp11_launch_source.py` and
  `tests/test_rp11_launch_toolchain.py`; and
* the build-root and manifest contracts whose serialized bytes may be affected.

Inspect and preserve unrelated worktree changes. Do not silently resolve a
conflict between these inputs.

## 4. Required remediation

1. Define the exact expected environment for each successful `execve` in the
   traced build:
   * the entry `/usr/bin/env` process;
   * `/bin/sh`;
   * ordinary compiler/assembler/linker/listing children; and
   * `cc1`, including every driver-added variable.
2. Make `ic1check.py` compare complete name/value mappings for equality.
   Missing required variables, extra variables, duplicate/malformed entries
   and changed values must all fail.
3. The expected values for `COLLECT_GCC`, `COLLECT_GCC_OPTIONS`,
   `OFFLOAD_TARGET_NAMES` and `OFFLOAD_TARGET_DEFAULT` must be independently
   specified or deterministically derived from pinned inputs and the fixed
   invocation. Do not learn expected values from the trace being checked.
4. Validate exact `PWD` and `OLDPWD` values for every process class where they
   are required. The R-4 path variant must use the corresponding controlled
   checkout path rather than hard-coding only `/rp11/co`.
5. Add focused negative tests covering, at minimum:
   * each required addition missing individually;
   * each required addition with a changed value;
   * an extra variable;
   * duplicate and malformed variables;
   * incorrect `PWD` and `OLDPWD` under both the R-2 path and R-4(a) path; and
   * each of the four driver-added variables missing and changed individually.
6. Keep the lock, contract module, manifest section and documentation mutually
   consistent. Advance the review-manifest version only if its serialized
   contract changes under the existing versioning rules. Regenerate artifacts
   only through the documented non-executing dry-run path.
7. Run IC-1 on a fresh pinned-root build and prove its outputs are byte-equal
   to R-2. Re-run R-1 and the affected T-L/T-L11/T-L10 checks needed to show
   that the frozen image and evidence digests did not move.

Do not weaken the check by changing “exact” into “allowed”, by wildcarding
driver values, by accepting arbitrary values copied from the trace, or by
removing variables from the traced process environment.

## 5. Required verification

Run narrow tests first, then all affected repository-local suites. Report exact
commands and results, including:

* focused IC-1 unit and negative tests;
* `tests/test_rp11_launch_source.py`;
* `tests/test_rp11_launch_toolchain.py` against a freshly provisioned or
  freshly verified pinned root;
* the complete `tests/phase_5_0_evidence` suite;
* fresh R-1, R-2 and IC-1 results and output digests;
* T-L11 and its T-L10 gate over the unchanged image/listing digests;
* relevant syntax/type checks and `git diff --check`; and
* generated-artifact byte equality or the exact reviewed version/digest change
  where regeneration is contractually required.

Do not cite carried-over counts as fresh results. A test that only demonstrates
that an unknown variable is rejected does not close the finding; missing and
changed required variables must be exercised.

## 6. Restrictions

No SSH, rsync, synchronization, `oracle-test` access, `sudo`, host package
installation, system configuration, service operation, database access,
provisioning outside an isolated repository/scratch build root, launcher
installation, H-1/H-2, PO-14 discharge, RP-11 wiring, controlled write,
reboot, evidence band, harness `--execute`, real participant, real capture
root, operational path, protected-artifact access, secrets scan, commit or
push is authorized.

Do not perform or claim R-5. Do not change the operational authorization
draft, make either pass executable, or modify the accepted launcher, XD,
spelling table, listing, source-to-image contract, control-transfer contract
or game/platform behavior.

PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; Package 5.0 remains not ready.

## 7. Handback and stop gate

Create
`phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-handback.md`.
Include:

* the exact environment contract for every process class;
* files and serialized contracts changed;
* a finding-to-test trace for every item in §4.5;
* fresh R-1/R-2/IC-1 evidence and exact output digests;
* proof that every frozen digest in §2 is unchanged;
* exact tests and results, checks not run and why;
* security implications and residual HA-1 … HA-5/TD-1 … TD-4 trust;
* rollback/recovery instructions;
* unresolved discrepancies; and
* focused questions for Codex.

Update only the concise current-state pointers needed to return the work. Stop
after the handback. Codex independently re-reviews the narrow remediation;
Peter Duscha alone accepts it or authorizes later R-5, host or operational
work.
