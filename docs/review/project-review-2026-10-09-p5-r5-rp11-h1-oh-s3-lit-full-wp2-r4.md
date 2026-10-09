# Independent re-review — LIT-FULL WP-2 R4 remediation

Date: 2026-10-09

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R4-20261009-18`

Reviewed deliverables:

- [corrected cumulative operation inventory](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md);
- [R4 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-handback.md);
- [accepted R4 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-claude-prompt.md); and
- [acceptance and Claude activation](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r4-remediation-acceptance-and-claude-activation.md).

## Recommendation

**Do not accept WP-2 yet. A separately authorized focused cumulative
remediation and a new independent re-review are required.**

The R4 return closes `WP2-R3-1`: the withdrawn start-timeout expression is no
longer presented as current. It also adds the missing `RT3.SN.1`, but that row
has one Blocking source-contract defect, `WP2-R4-1`: it conflates recovery of
the interrupted stop-post cleanup with ownership of a child left behind by
stop-post.

This review does not accept WP-2, authorize remediation, authorize WP-3,
establish concrete Route 3 or select LIT-FULL for implementation. Peter Duscha
retains every acceptance and assignment decision. WP-3 through WP-7 remain
gated.

## Finding

### WP2-R4-1 — Blocking — `RT3.SN.1` assigns the wrong owner to a child left behind by stop-post

Inventory row `RT3.SN.1` says that H-SN applies to a stop-post child, that “no
unit owns it”, and that after stop-post ends or is interrupted the next owner is
the backstop's CL if armed and spawnable, otherwise a later CP, then the boot,
then `attest`.

That combines two different accepted contracts. The accepted R8 SN-RO table
defines an *owner* as the first party that can end the child by an act of its
own. For a child left behind by stop-post, that owner is PID 1's
`FINAL_SIGTERM`, followed by `FINAL_SIGKILL` after another S, to “what
remains” in the holder unit's stop-post context. The boot is a later, separate
recovery event. A later backstop CL or `attest` may observe a missing
`run-end` and record `children-unknown`; it does not hunt, signal, reap or
otherwise act on the child. The existing RT-3 interruption rows separately
state who next recovers the unfinished cleanup and activation state: the
backstop's CL if available, otherwise later CP, boot and `attest`. That cleanup
recovery chain is not the SN-RO child-owner chain.

The row therefore contradicts its cited R8 §7.5a.7 source, its own taxonomy
cell (which includes class-M PID 1 signalling at row 3f), and the inventory's
general no-hunting rule. Child ownership and signal authority are security- and
production-reliability-sensitive, so the finding is Blocking.

The accepted R4 prompt caused the conflation by instructing the executor to
carry the cleanup recovery chain into the child-contract row and call it
ownership. That instruction did not and could not override accepted R8. Claude
otherwise followed its accepted R4 authority; the remediation must correct the
cumulative inventory and must not rewrite the historical prompt.

**Required remediation:** under separately accepted authority, revise
`RT3.SN.1` so it:

1. preserves the two-tier child surface and H-SN applicability;
2. states the stop-post child's accepted SN-RO ownership: PID 1's
   `FINAL_SIGTERM`, then `FINAL_SIGKILL` after another S, to “what remains”,
   followed by the boot as a separate event;
3. preserves the qualification that inclusion of a `setsid` child in “what
   remains” is the existing PO-SN (e) basis, not a new guarantee;
4. separately states the later observer contract: the backstop's CL or
   `attest` may record `children-unknown` from the missing `run-end`, but no
   later procedure hunts, signals, reaps or acts on the child; and
5. does not apply the RT-3 cleanup-recovery chain as child ownership. Preserve
   that cleanup chain in the RT-3 interruption rows where it belongs.

Reconcile the row's blocking/class cell, source citations, §8.1, §9, §10,
§11, §13–§15 and every summary or checklist statement affected. Do not change
row, step, call-site or question counts unless the delivered tables actually
change.

Evidence: inventory row `RT3.SN.1`; accepted R8 §7.5a.7 table SN-RO and §7.9
owner/record table; R8 SN-9, IS-6, IS-7, IS-9 and INV-23; accepted R4 prompt
lines 145–149.

## Closed R3 findings and other verified evidence

- `WP2-R3-1` is closed. `RT1.FI.2` and §11.1 retain finite `T_s`, class M and
  necessary-only N1. The withdrawn expression occurs only in text identifying
  it as withdrawn.
- The R4 table arithmetic reproduces: 318 rows, 317 operation/contract/
  composition rows, one gap row, 63 CN rows, 15 RT-3 rows and 77 steps.
- The R3 BS-4 correction remains intact: SN-10 / A-I-16 apply to AK-1, BS-2
  and BS-3 only; BS-4 remains `CALL-DI4-03` under open Q6-7.
- Q6-6 and Q6-7 remain unanswered. No later-package question was answered.
- The 30-item ledger contains 30 rows. All 26 files that R4 did not edit match
  their recorded line, byte and SHA-256 identities. The four pre-edit pointer
  snapshots and archive-index hashes match the handback.
- Inventory: 1,440 lines, 227,365 bytes, SHA-256
  `a981534baba73012ef70035e2ef4be933b970839d22d49509ebba063cd1603c5`.
- R4 handback: 125 lines, 14,787 bytes, SHA-256
  `92cedbf2a37336c2d47015d22648a93a1f71a4fb846d59a7138f5cdefbfad897`.
- The terminal relative-link check was independently reproduced over the same
  scope: 14 files, 246 links, zero broken.
- `git diff --check` reported no whitespace errors.

## Checks not run and boundary

No host, retained-evidence, network, secret, service, database, package,
build, application test, hook test, formatter, implementation, activation,
rollback, commit or push operation was performed. Those operations remain
prohibited and would not resolve this documentation source-contract finding.

The no-host restriction remains unchanged. The R5 and H-0G retained paths
remain untouched pending separately gated LC-3 through LC-5 authority.

## Required next gate

WP-2 remains unaccepted. Peter may decide whether to authorize a focused
cumulative remediation of `WP2-R4-1`. This review itself grants no authority.
No WP-3 prompt may be prepared and no WP-3 through WP-7 work may begin before
a clean independent re-review and Peter's later acceptance.
