# Independent re-review — LIT-FULL WP-2 R5 remediation

Date: 2026-10-09

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R5-20261009-19`

Reviewed deliverables:

- [corrected cumulative operation inventory](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md);
- [R5 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-handback.md);
- [accepted R5 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-claude-prompt.md); and
- [acceptance and Claude activation](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-acceptance-and-claude-activation.md).

## Recommendation

**No findings. Accept the R5 remediation and WP-2.**

This review does not itself accept WP-2, authorize WP-3, establish concrete
Route 3 or select LIT-FULL for implementation. Peter Duscha retains the
acceptance and successor-assignment decisions. WP-3 through WP-7 remain gated.

## Findings

No Blocking, Important or Optional findings.

`WP2-R4-1` is closed. `RT3.SN.1` now separates the accepted SN-RO owner of a
child left behind by stop-post from the observer contract and from recovery of
unfinished cleanup state. PID 1 sends `FINAL_SIGTERM`, then `FINAL_SIGKILL`
after another S, to “what remains”; the sends are class M and are not proof of
exit. Whether “what remains” includes a `setsid` child remains the existing
PO-SN (e) basis, not a new guarantee. The boot is a separate recovery event,
and `attest` has no automatic owner.

The observer contract is separately stated: CS-7, CS-8 and CS-10 leave a
durable child line; CS-1 through CS-6 and CS-9 leave only the missing
`run-end`; a later backstop CL or `attest` may record `children-unknown`, but
no later procedure searches for, signals, reaps or otherwise acts on the
child. The backstop/CP/boot/`attest` chain remains only as cleanup-state
recovery on `RT3.FI.2` and `RT3.CLG` through `RT3.CLOUT`.

Every earlier cumulative correction remains intact: `RT2.AM0.7` is a
non-operative Q6-7 gap row; the replacement child surface retains only the
DI-6 subject intent; the unknown-effect obligation remains unmapped under
Q6-6; BS-4 remains the third DI-4 call site with the SN-10/A-I-16 extension
unanswered under Q6-7; the withdrawn `T_s` expression is not presented as a
requirement; and `RT3.SN.1` supplies the previously missing RT-3 material
sub-role row.

## Checks and evidence

- The inventory matches its handback identity: 1,450 lines, 230,574 bytes,
  SHA-256 `da341efb8c29b862d63c1463e981ccfedbe1f6680de2d416ff285fdae06461fd`.
- The 34-item pre-edit reading ledger identities independently match the files
  that were not edited and the four recorded pre-edit pointer states.
- The delivered tables independently reproduce 318 rows: CN 63, CMP 36, GAP
  1; RT-3 has 15 rows; Q6-6 occurs on 5 rows and Q6-7 on 3; the trace has 77
  steps and 41 DI call sites.
- The four R5-authorization snapshots match their handback-recorded line,
  byte and SHA-256 identities, and each digest appears in its archive index.
- The 14-file terminal-link scope contains 277 Markdown links with no missing
  relative target.
- `git diff --check` reports no whitespace errors on the delivered files.

No host, retained-evidence, network, secret, service, database, package,
build, application test, hook test, formatter, implementation, activation,
rollback, commit or push operation was performed.

## Remaining gate

Peter may accept WP-2. That acceptance permits preparation of a bounded WP-3
assignment for independent review; it does not itself accept or activate a
WP-3 prompt, authorize WP-3 execution, answer a deferred question, establish
concrete Route 3, select LIT-FULL for implementation or relax the no-host
restriction.

Q6-6 and Q6-7 remain unanswered. BC-2 remains unresolved for any later WP-9
selection. The R5 and H-0G retained paths remain untouched pending separately
gated LC-3 through LC-5 authority.
