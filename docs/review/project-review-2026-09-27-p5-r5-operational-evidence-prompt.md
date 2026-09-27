# Codex independent review — C-P5.0-R5-OP1 operational-evidence prompt

Date: 2026-09-27  
Reviewer: Codex, Independent Reviewer  
Disposition: **Changes requested — Pass A and Pass B are not authorized**

## Reviewed artifacts

- `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
  - SHA-256 at review: `9bd4f5b54b3bf9fad9a1070dc88f62225e6d25b2d4deafbb59432cf11ad7785c`
- `phase-5-0-p5-r5-operational-evidence-prompt-drafting-handback.md`
  - SHA-256 at review: `e7db948d4f61938b02d6c8115fd0a1ffcccdbfc5d61115f34dcb0ede6ae24a1b`

The review compared those exact bytes with `.agents/AGENTS.md`, implementation
plan §§0, 16 and 20 and the Package 5.0 material, the current handover, the
disposable-server restrictions, the accepted P5.0-R5 reconciliation, and the
reviewed evidence-harness sources. No command was issued to `oracle-test`.

## Disposition

The draft is not technically or evidentially admissible. Pass B already states
that RP-1 through RP-9 are unmet. Pass A also cannot be authorized because its
RP-1 sequencing contradicts the reviewed E7 contract and because the evidence
capture required by the prompt has no executable method.

P5.0-R5 remains **Blocking**. `plan.is_executable=False` remains controlling;
Package 5.0 remains not ready; OD-62 G-A remains conditional. This review
creates no implementation, synchronization, host, database, verifier,
evidence-band, reboot, deployment or production authority.

## Blocking findings

### OP1-R1 — RP-1 makes E7 expectations self-derived

The draft says the ten `capability.E7_TARGET_FACTS` come from Pass A's
observations and from nothing else. Pass A obtains them through
`sudo grep ... /proc/self/status` and `sudo capsh --print` and then makes those
observations RP-1 inputs.

That contradicts the reviewed harness contract:

- `tools/phase_5_0_evidence/capability.py` states that learning an E7 target
  fact from P-01, P-02 or E7's own observation makes the comparison a check
  against itself; and
- `tools/phase_5_0_evidence/concrete_plan.py` requires the expectations to be
  supplied from outside and independently reviewed, and explicitly excludes
  learning them from `/proc`, `id` or `capsh`.

The two proposed Pass A commands also observe the `grep` and `capsh` processes,
not the final interpreted E7 process.

**Required correction:** Pass A observations may be labelled corroborative,
but must not be the source of the executable E7 expectations. RP-1 must require
owner-stated, independently reviewed target expectations from a source that
does not compare an observation with itself. If no such reviewed source or
method exists, retain a typed blocker rather than inventing a value or method.

### OP1-R2 — `fsync` failure injection is omitted from feasibility work

The draft classifies reconciliation row 40, JNL-17 `fsync` injection, as a
later production gate. A-5.0-5(k) remains an unconfirmed readiness premise,
and the accepted reconciliation lists an `fsync` fault-injection mechanism in
the remaining controlled-host-mutation evidence.

**Required correction:** classify the bounded `fsync` failure-injection
mechanism and evidence as remaining P5.0-R5 feasibility work. Add a fail-closed
repository prerequisite if no reviewed producer exists. It may be deferred
only by a new explicit maintainer disposition that identifies the resulting
residual; the remediation pass must not make that decision.

### OP1-R3 — the evidence-capture contract is not executable

Section 9.3 requires a record per case or act containing separate
`stdout_sha256` and `stderr_sha256`, UTC start and end times, exit status and a
safe excerpt. Pass A instead requires plain SSH calls whose output exists only
in the client transcript. A merged or truncated transcript cannot establish
separate byte-exact stream digests.

**Required correction:** specify a reviewed client-side capture procedure that
preserves stdout and stderr separately, records exact argv, UTC bounds and exit
status, calculates the two digests, and produces the required record without
creating unauthorized target-host files. If the repository has no reviewed
mechanism, represent it as an unmet prerequisite and do not describe either
pass as executable.

## Important corrections

1. Name Pass A accurately as synchronization plus read-only host preflight.
   Its approved future shape contains `rsync --delete`, so the pass as a whole
   is not read-only even though its post-synchronization host inspection is.
2. Resolve or retain as explicit blockers every placeholder, including
   `MI.run_record_path`; do not substitute an invented location.
3. Retain MD-5 as unmet until the corrected classifier has a recorded,
   independent acceptance. A green local preflight is not that acceptance.
4. Require a clean pinned commit and review digest for the exact amended bytes
   before any authorization can be considered.
5. Keep feasibility evidence and later production-code evidence separate and
   non-substitutable, preserve MD-1 through MD-6, and keep the mandatory reboot
   and recovery rehearsals in scope.

## Required next action

Claude performs the bounded repository-only remediation in
`phase-5-0-p5-r5-operational-evidence-prompt-remediation-claude-prompt.md`,
amends the authorization prompt, and returns a new remediation handback.
Codex then independently reviews the new exact bytes. Only a later explicit
maintainer decision may authorize an operational pass.

## Checks and non-actions

- Reviewed the named documentation and relevant harness source locally.
- Re-derived the two reviewed-artifact SHA-256 values.
- Ran `git diff --check` on the two returned drafting artifacts; it reported no
  whitespace error.
- Did not run an evidence harness, verifier, test suite or database command.
- Did not SSH, synchronize, inspect or otherwise contact `oracle-test`.
- Did not access any protected historical `/tmp` artifact.
- Did not run a secrets scan or alter a guard.

