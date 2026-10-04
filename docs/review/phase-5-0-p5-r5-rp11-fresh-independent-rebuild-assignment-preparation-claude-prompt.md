# Claude prompt — prepare the fresh R-5 independent-rebuild assignment

Work ID: `C-P5.0-R5-RP11-FRESH-A1`

Date: 2026-10-02

Assignee: Claude

Status: **proposed documentation-only assignment; not executable until Product Owner Peter Duscha explicitly accepts this preparation task and appoints Claude as its drafting assignee**

## 1. Objective

Prepare a decision-ready assignment for one wholly fresh R-5 independent static-
launcher rebuild using the accepted manifest-version-30 baseline contract.

Claude may draft the assignment because Claude has implementation knowledge, but
Claude built the I-7/I-7-R1 launcher and therefore may not:

- execute R-5;
- serve as the independent R-5 assignee;
- select or appoint the R-5 assignee;
- review or accept its own proposed assignment; or
- characterize the future R-5 result as passing.

The resulting assignment must return to Codex for independent review and then to
Peter Duscha for an explicit decision naming the independent executor.

## 2. Controlling accepted state

The proposal must use, and must not silently alter, the following accepted
state:

- manifest version: `30`;
- aggregate review-manifest digest:
  `28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`;
- diagnostic baseline path:
  `infra/rp11-launch/verify/fixtures/cc1.v.baseline`;
- diagnostic baseline length: `5120` bytes;
- diagnostic baseline SHA-256:
  `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`;
- normative launcher-output digests remain the four entries in
  `infra/rp11-launch/expected.sha256`;
- `cc1.v.baseline` is diagnostic comparison evidence and is not a fifth
  normative output;
- `B1-R3-1` and `B1-R3-2` are Closed as remediated;
- R-5 is stopped, Blocking and unaccepted;
- RP-11 is unwired and unmet;
- `plan.is_executable=False`;
- PO-9 and PO-14 remain open; and
- Package 5.0 is not ready.

The acceptance record is:

`docs/review/project-review-2026-10-02-p5-r5-rp11-b1-r4-acceptance.md`

## 3. Required context

Before drafting, read:

1. `.agents/AGENTS.md` completely;
2. the reading map, §0, §13, §16, §17 and §20 of
   `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. `docs/project-management/status.md`;
5. `docs/operations/disposable-test-server.md`, especially its current
   restriction banner;
6. the accepted D2/D2-R2 design and decisions, including LD-7, LD-8 and LD-9;
7. the I-7 and I-7-R1 prompts, handbacks, reviews and acceptance records;
8. the original R-5 assignment, independent review, acceptance, stopped
   handback and bubblewrap authority record;
9. the R2, R3, R4, R4-R1 and B1 through B1-R4 prompts, handbacks, reviews and
   decisions;
10. `infra/rp11-launch/toolchain.lock`;
11. `infra/rp11-launch/build-root.manifest`;
12. `infra/rp11-launch/expected.sha256`;
13. `infra/rp11-launch/buildroot/provision.py`;
14. `infra/rp11-launch/buildroot/enter.py`;
15. `infra/rp11-launch/verify/cc1check.py`;
16. `tests/test_rp11_launch_toolchain.py`; and
17. this prompt.

Inspect `git status` before editing and preserve every unrelated change.

## 4. Required assignment design

Create a proposed R-5 assignment that is complete enough for independent review
and a Product Owner acceptance decision. It must contain all of the following.

### 4.1 Independence and assignee

- Leave the execution assignee as `TBD — must be named by Peter Duscha upon
  acceptance`.
- State that Claude is ineligible because Claude implemented I-7/I-7-R1.
- State that preparing, reviewing or accepting the draft does not itself
  authorize execution.
- Require the named executor to attest that it did not implement I-7/I-7-R1 and
  has not reused an earlier build root, cache, checkout, work directory, trace
  or scratch evidence.
- If Gemini is later selected, require the run to be wholly fresh and forbid
  reuse of every resource or artifact from Gemini's earlier R-5 and B1 runs.

### 4.2 Exact controlling inputs

Pin the values in §2 and require the executor to verify them against the active
tree before any host or provisioning action. Include exact SHA-256 values for:

- `toolchain.lock`;
- `build-root.manifest`;
- all four entries in `expected.sha256`;
- the diagnostic baseline fixture;
- the checked-in review-manifest JSON; and
- any launcher source or verifier artifact whose identity the accepted R-5
  contract requires.

Claude must calculate these values read-only from the current tree and record
the commands used. Any mismatch while preparing the proposal is a stop
condition and must be reported instead of normalized.

### 4.3 Host-assumption variation

Implement LD-8 exactly:

- record HA-1 through HA-5 freshly before provisioning;
- require at least one of HA-1, HA-2 or HA-3 to differ in the actual run from
  Claude's accepted reference environment;
- declare a run invalid if none of HA-1 through HA-3 differs;
- require exact recording of kernel release, CPU model and relevant CPU
  features, and entry mechanism/version;
- record HA-4 and HA-5 as required by D2/LD-8; and
- make every unexplained difference a hard stop.

Do not assume the historical `oracle-test` facts remain current. The proposal
may identify `oracle-test` as the intended disposable target, but every fact
must be observed afresh only after the assignment is independently reviewed and
explicitly accepted.

### 4.4 Freshness and isolation

Require unique, newly created paths for:

- package cache;
- provisioned build root;
- controlled checkout or checkouts;
- build outputs;
- trace and comparison evidence; and
- handback evidence.

Forbid use of every previously retained R-5, B1, I-7 or I-7-R1 root, cache,
checkout, output, trace and scratch directory. The accepted repository fixture
may be read only as the comparison baseline; it must never be copied into the
fresh output position or treated as generated output.

### 4.5 Required ordered procedure

Require, in explicit order:

1. preflight repository identity and digest verification;
2. fresh HA-1 through HA-5 observation;
3. confirmation that at least one of HA-1 through HA-3 differs;
4. creation of unique disposable directories with recorded modes and owners;
5. fresh provisioning from the signed snapshot and accepted lock only;
6. the accepted same-invocation R-1/R-2 manifest gate through the supported
   `enter.py build` path;
7. unprivileged R-2 execution inside the entered root;
8. R-3 exact comparison of the four normative outputs;
9. exact `cc1.v` comparison against the accepted baseline through
   `cc1check.py`, where byte equality is the only `PASS` path;
10. the accepted corroborating toolchain tests against the fresh root;
11. complete evidence capture and digest accounting; and
12. handback followed by an immediate stop.

Do not reintroduce the original run's split R-1/R-2 orchestration. The manifest
gate and build must be the accepted same-invocation implementation.

### 4.6 Pass, invalid-run and hard-stop rules

The proposed assignment must distinguish:

- `PASS`: every required gate ran in order; at least one of HA-1 through HA-3
  differed; the R-1/R-2 gate passed; all four normative outputs matched; the
  diagnostic `cc1.v` bytes matched exactly; required tests passed; and no
  unexplained difference remained;
- `INVALID RUN`: none of HA-1 through HA-3 differed, even if every byte matched;
  and
- `HARD STOP`: any input mismatch, provisioning discrepancy, failed gate,
  missing evidence, output difference, `cc1.v` difference, unexpected command,
  privilege requirement, or unexplained environmental difference.

Forbid manual adjustment of the fixture, `expected.sha256`, lock, manifest,
source, listing, verifier or generated output to obtain a pass.

### 4.7 Authority and safety boundary

The proposed assignment must enumerate the minimum host actions required for
one run and no more. It must explicitly address the current no-access banner in
`docs/operations/disposable-test-server.md` and state that only Peter's later
acceptance of the independently reviewed assignment can replace that banner.

Unless separately justified and accepted, forbid:

- installation or upgrade of packages;
- persistent host configuration;
- service or database changes;
- access to production or staging data;
- launcher installation or RP-11 wiring;
- H-1/H-2, PO-14 discharge or evidence-band execution;
- harness `--execute`;
- reboot;
- secrets access;
- commit, push or Git-history modification; and
- any second run or remediation after a stop.

If a prerequisite such as `bubblewrap`, user namespaces or the pinned Python
environment is unavailable, the executor must stop and report. The draft must
not grant ambient authority to repair it.

### 4.8 Handback contract

Require a new, uniquely named fresh-R-5 handback containing:

- assignee independence attestation;
- start/end timestamps;
- repository state and every controlling digest;
- fresh HA-1 through HA-5 observations and the qualifying variation;
- every created path, mode and owner;
- exact commands in execution order with exit statuses;
- download source and package accounting;
- R-1/R-2 same-invocation evidence;
- all normative output hashes and byte-comparison results;
- `cc1.v` length, hashes and exact comparison verdict;
- complete test results, including skips and warnings;
- all stopped, invalid or unexplained conditions;
- retained evidence locations and cleanup state;
- explicit statement that RP-11 remains unwired and no operational authority
  was exercised; and
- immediate stop pending Codex review and Peter's decision.

## 5. Required output

Write the proposed execution assignment to:

`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`

Its status must be:

`Prepared by Claude for independent Codex review; not accepted, not assigned, and not executable.`

Write the drafting handback to:

`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-handback.md`

The handback must list:

- every source document read;
- every read-only command used;
- every digest independently calculated for the draft;
- every file created or modified;
- confirmation that only the two output documents were written;
- `git diff --check` limited to those documents;
- final `git status --short`;
- unresolved assumptions requiring reviewer or Product Owner disposition; and
- confirmation that no host, remote, provisioning, build, test or execution
  action occurred.

## 6. Authority for this preparation task

Claude may:

- read the repository sources and records required by §3;
- calculate hashes and inspect repository metadata read-only;
- create only the proposed assignment and preparation handback named in §5;
  and
- run documentation-only link and diff checks against those two files.

Claude may not:

- edit any existing file;
- access retained `/tmp` run evidence;
- access `oracle-test` or any remote host;
- use SSH, rsync or network access;
- provision, build, execute or test the launcher;
- run `provision.py`, `enter.py`, `cc1check.py`, IC-1, B1 or R-5;
- use `sudo`, install packages or change host state;
- stage, commit or push; or
- name, appoint, review or accept the future R-5 executor.

## 7. Stop conditions

Stop and write a partial drafting handback if:

- any controlling value differs from §2;
- the accepted records conflict materially;
- a complete assignment requires new policy or broader authority;
- an existing output path would be overwritten;
- another agent creates or changes either authorized output document; or
- any required step would cross the preparation-only boundary.

After writing the proposal and preparation handback, stop. Do not execute R-5
or begin any follow-on work.
