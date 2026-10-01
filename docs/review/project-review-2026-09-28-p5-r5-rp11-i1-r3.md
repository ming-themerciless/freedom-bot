# Codex independent review — RP-11 I1-R3 retained-alias implementation — 2026-09-28

Review ID: `C-P5.0-R5-RP11-I1-R3-REV1`

Reviewed return: `C-P5.0-R5-RP11-I1-R3-I1`

Disposition: **changes requested**

## Scope and restrictions

Codex reviewed the I1-R3 handback, assignment, accepted redesign direction,
proposed operational-evidence requirements, unwired RP-11 source, focused tests
and generated review inputs. The review was repository-only. No SSH,
synchronization, network or host inspection, `sudo`, database access,
provisioning, controlled write, reboot, verifier, evidence band, harness
`--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push occurred.

The accepted requirements baseline remains the R5 bytes at SHA-256
`5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3`.
The I1-R3 draft (`402126322f34…`), implementation and version-23 review-input
digest (`264674da…`) remain proposed and unaccepted.

## Findings

### RP11-I1-R3-1 — Blocking — unadmitted-pair policy is not a decision of record

The implementation and amended B0-RA contract permit a recorded unadmitted
staging/final pair to share one inode, checked by metadata only. The assigned
prompt limited the explicit alias exception to an admitted object. The I1-R3
handback records Peter Duscha's in-session choice to permit the unadmitted pair
metadata-only, but also says that answer still requires confirmation as the
decision of record.

This changes X-4 and Pass B admission behavior. The implementation cannot be
accepted until Peter records which policy controls: permit the recorded pair
metadata-only on the stated narrow conditions, or refuse every unadmitted
alias. A remediation may analyze both choices and prepare a recommendation;
it must not silently treat either one as approved.

### RP11-I1-R3-2 — Important — whole-package result did not reproduce

The handback reports `tests/phase_5_0_evidence`: **3320 passed, 0 skipped**.
Codex ran the stated repository-local command with the documented interpreter,
`TEST_DATABASE_URL` unset, bytecode disabled and the pytest cache provider
disabled. The result was **2941 passed, 379 failed, 0 skipped**. The failure
cascade included `OSError: [Errno 24] Too many open files`; the reviewing
shell's soft descriptor limit was 1024.

The focused RP-11 selection was then rerun in a fresh process and reproduced
exactly: **367 passed, 0 skipped**. The discrepancy therefore needs a bounded
suite-order/file-descriptor diagnosis and a truthful evidence correction. The
379 failures are not classified as 379 independent defects.

### RP11-I1-R3-3 — Important — proposed requirements retain stale absence claims

The amended operational-evidence draft describes the retained-alias mechanism
but still says `No such mechanism exists in the repository` and repeats
`Unresolved: RP-11 does not exist` at A0-08, B0-RA and B0-08. Repository source
and focused tests now exist. The accurate state is that the mechanism is
unwired and unaccepted; C-11 and the pinned launcher environment remain open;
no real capture root or Pass A handback exists; and RP-11 remains unmet.

## Technical assessment

Subject to the findings above, the focused implementation follows the accepted
I1-R3 direction: exclusive named staging creation, one no-follow non-replacing
hard link, retention of both names, no cleanup, and admission through a later
durable state. No additional source-level security or durability finding was
identified in the focused review.

## Commands and results

* Focused RP-11 capture and retention suites: **367 passed, 0 skipped**.
* Whole `tests/phase_5_0_evidence` directory: **2941 passed, 379 failed,
  0 skipped**; failure cascade included descriptor exhaustion.
* Scoped `git diff --check`: clean.
* An initial `/usr/bin/python3` invocation could not run because that
  interpreter has no pytest; the documented repository interpreter was then
  used.

No bot, web, database, Foundry or host suite was run because the active
assignment prohibited host and database activity and scoped validation to the
repository-local evidence package.

## Required disposition

Return a bounded remediation that:

1. prepares a clear maintainer decision recommendation for RP11-I1-R3-1 and
   keeps that finding open until Peter decides it;
2. diagnoses and truthfully reports the whole-package discrepancy without
   manipulating test order or resource limits; and
3. corrects stale existence wording without implying acceptance or RP-11
   satisfaction.

RP11-I1-R3-1 remains Open, Blocking. RP11-I1-R3-2 and RP11-I1-R3-3 remain
Open, Important. RP11-I1-R1-1, RP11-I1-R2-1 and RP11-I1-2 remain Open. RP-11
remains unmet; neither pass is executable or authorized; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; `plan.is_executable=False`; Package
5.0 remains not ready.
