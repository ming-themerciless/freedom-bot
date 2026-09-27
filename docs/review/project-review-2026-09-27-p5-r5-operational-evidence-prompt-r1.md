# Codex independent re-review — C-P5.0-R5-OP1-R1 operational-evidence prompt

Date: 2026-09-27

Reviewer: Codex, Independent Reviewer

Disposition: **Changes requested — Pass A and Pass B are not authorized**

## Exact reviewed artifacts

- `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
  - SHA-256: `7a73d3da474562eb098548cd44270c9d1f39adecb3ab073a6ed02409295ffe61`
- `phase-5-0-p5-r5-operational-evidence-prompt-remediation-handback.md`
  - SHA-256: `43f38b508d2803d4e0e93d83252f5bba438639b05eea901c680e9daf28d69382`

The re-review compared those exact bytes with the governing agreement, the
implementation-plan controls, the active handover and disposable-host
restriction, the original Codex review and the remediation assignment. No
command was issued to `oracle-test`.

## Disposition

The remediation resolves the original OP1-R1, OP1-R2 and OP1-R3 findings in
substance: target expectations are no longer learned from Pass A; row 40 is
P5.0-R5 feasibility work; and the absent capture implementation is an unmet,
fail-closed prerequisite. One Blocking defect remains in the new capture
contract.

P5.0-R5 remains **Blocking**. `plan.is_executable=False` remains controlling;
Package 5.0 remains not ready; OD-62 G-A remains conditional. This review
creates no implementation, synchronization, host, database, verifier,
evidence-band, reboot, deployment or production authority.

## Blocking finding

### OP1-R1-1 — the capture durability sequence is incomplete

Section 9.5 C-5 calls each per-act record durable after it is written, flushed
and atomically renamed. The contract does not require:

- each stdout and stderr stream file to be flushed and synchronized before the
  record that publishes its digest;
- the completed record file to be synchronized;
- the containing directory to be synchronized after each atomic rename; or
- durable creation and finalization of the pass-level capture index.

Therefore a record may survive while one or both primary-evidence stream files
do not, or a renamed record or the capture index may be lost after a crash or
reboot. C-10 likewise treats only a record durability failure as a capture
failure and does not expressly cover the streams, directory-entry barriers or
index. That is inconsistent with the draft's claim that the retained stream
files and records are durable primary evidence, and is material to the
mandatory reboot band and the no-retry rule.

**Required correction:** amend RP-11 and §9.5 to require a reviewed,
crash-consistent publication sequence for both stream files, the per-act
record and the capture index. At minimum the contract must require successful
file synchronization of each completed stream before its digest is published,
successful synchronization of each completed record, and synchronization of
the containing directory after every atomic rename or creation whose survival
is required. It must define how the index is created, advanced and finalized
durably without mutating already-published records, and make failure of any
file or directory durability barrier an `inconclusive` stop under C-10 and
§11.2. The remediation must not select implementation APIs or claim RP-11 is
satisfied; that belongs to the later RP-11 implementation and review.

## Resolved original findings

1. **OP1-R1 resolved:** RP-1 is blocked by RP-10; Pass A observations are
   corroborative only and cannot become expectations.
2. **OP1-R2 resolved:** row 40 and A-5.0-5(k) are feasibility work blocked by
   RP-12, with no silent production-gate deferral.
3. **OP1-R3 resolved in design:** RP-11 is explicitly absent and blocks all
   host commands; the client transcript is not evidence. OP1-R1-1 concerns the
   completeness of the new RP-11 requirements, not an assertion that an
   implementation exists.

## Required next action

Claude performs the bounded repository-only correction in
`phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md`,
amends the authorization draft and returns a new handback. Codex then reviews
the exact amended bytes. Only a later explicit maintainer decision may accept
or authorize an operational pass.

## Checks and non-actions

- Re-derived both reviewed-artifact SHA-256 values.
- Ran repository-local whitespace checks on the returned documentation; no
  whitespace error was reported.
- Did not run a suite, harness, verifier or database command.
- Did not SSH, synchronize, inspect or otherwise contact `oracle-test`.
- Did not access any protected historical `/tmp` artifact.
- Did not run a secrets scan or alter a guard.
