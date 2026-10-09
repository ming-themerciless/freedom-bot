# Independent re-review — LIT-FULL WP-2 R3 remediation

Date: 2026-10-09

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R3-20261009-17`

Reviewed deliverables:

- [corrected cumulative operation inventory](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md);
- [R3 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-handback.md);
- [accepted R3 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-claude-prompt.md); and
- [acceptance and Claude activation](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r3-remediation-acceptance-and-claude-activation.md).

## Recommendation

**Do not accept WP-2 yet. A separately authorized focused cumulative
remediation and a new independent re-review are required.**

The R3 return closes `WP2-R2-1`, `WP2-R2-2` and `WP2-R2-3`. It nevertheless
has two Important findings: `WP2-R3-1`, in which two inventory statements
retain a start-timeout lower-bound formula that the accepted R8 text expressly
withdraws; and `WP2-R3-2`, in which the roster names the material `RT-3.SN`
sub-role but the per-procedure tables contain no corresponding row. The R3
handback noticed both discrepancies but, correctly within its three-finding
authority, did not silently repair them.

This review does not accept WP-2, authorize remediation, authorize WP-3,
establish concrete Route 3 or select LIT-FULL for implementation. Peter Duscha
retains every acceptance and assignment decision. WP-3 through WP-7 remain
gated.

## Findings

### WP2-R3-1 — Important — the inventory presents a withdrawn `T_s` formula as current

Inventory row `RT1.FI.2` and the §11.1 `T_s` parameter row state that the
capture unit's start timeout is finite and at least `⌈P/1000⌉ + 30` seconds,
citing AR-4 and R8 §7.6 N1. The accepted R8 text expressly withdraws the earlier
`T_s ≥ ⌈(P + c)/1000⌉ + 30` rule as W-7 and replaces it with N1:
`T_s · 1,000 ≥ W_show + W_series + ρ`, where `W_show = c + g` and
`W_series = P + c + g`. The inventory includes N1 in §11.1, but it also presents
the unrelated `⌈P/1000⌉ + 30` expression as a current accepted condition. That
expression is neither the withdrawn W-7 formula nor its accepted replacement.

This is not a count error and N1 is the stronger operative condition with the
accepted parameter grammar, so the stale statement does not presently loosen
the gate. It is nevertheless an inaccurate source contract in the cumulative
operation inventory that WP-3 is meant to consume. A clean source-authority
review cannot recommend acceptance while it remains.

**Required remediation:** under separately accepted authority, remove the
withdrawn/unsupported lower-bound expression from `RT1.FI.2` and §11.1. Preserve
that `T_s` is finite, is the manager's class-M deadline and must satisfy N1;
reconcile any dependent summary or acceptance text and return the cumulative
inventory for independent re-review. Do not reopen the R3 BS-4 correction or
answer a later-package question.

Evidence: inventory lines 370 and 1022; accepted R8 proposal §7.6 N1 and §7.7
W-7 (lines 2996–3000 and 3021–3035). The R3 handback §9 independently flags the
`T_s` formula/wording for reviewer confirmation.

### WP2-R3-2 — Important — the material `RT-3.SN` sub-role has no per-procedure row

Inventory §3 identifies `RT-3.SN (child contract)` as a stop-post sub-role, but
§5.3 has no `RT3.SN.1` row. The other four root procedures each have a
procedure-specific SN row (`RT1.SN.1`, `RT2.SN.1`, `RT4.SN.1`, `RT5.SN.1`).
The original WP-2 requirement 5 requires rows per procedure and material
sub-role rather than collapsing shared helpers into an unexplained row, and the
inventory's §14 checklist claims §§4–5 provide those rows. `RT3.CL4` composes
the shared H-SN mechanics and §8.1 describes the global child surface, but
neither records the stop-post-specific child surface and recovery owner in the
same per-procedure form used everywhere else.

This does not remove the shared SN mechanics or create an uncovered accepted
step, so it is not Blocking. It is an incomplete material-sub-role inventory
and makes the document's own coverage claim false.

**Required remediation:** under the same separately accepted cumulative
remediation, add the stop-post-specific SN row grounded in the accepted child
surface and owner contract, then reconcile the row, class, tag, identifier-
citation and acceptance-checklist counts. Do not invent new behavior or answer
a later-package question.

Evidence: inventory roster line 125; §5.3 lines 486–505; original WP-2 prompt
operation-inventory requirements 3, 5 and 10; inventory §14. The R3 handback §9
independently notes that no `RT-3.SN` row exists.

## Closure of the R2 findings

- `WP2-R2-1` is closed for this return. The handback contains the required
  26-item pre-edit ledger and unambiguously records complete reading before the
  first edit. The 21 source/non-pointer files that R3 did not edit match their
  ledger hashes; the pre-edit inventory hash matches the independently recorded
  R2 inventory, and the four pre-edit pointer hashes match the four
  byte-preserving R3-authorization snapshots.
- `WP2-R2-2` is closed. `RT4.BS4.2`, `RT4.SN.1`, §§7, 8, 8.1, 11.4, 12, 13 and
  15 keep BS-4 as `CALL-DI4-03` while applying SN-10 / A-I-16 only to AK-1,
  BS-2 and BS-3. Q6-7 carries the BS-4 extension question without selecting an
  answer; Q6-6 is limited to the accepted obligation and its unmapped
  non-child realization.
- `WP2-R2-3` is closed. Handback §6.1 durably records the terminal rerun as 14
  files, 237 links, zero broken and exit status 0.

## Other verified evidence

- Inventory: 1,426 lines, 223,855 bytes, SHA-256
  `e5c32312caf87d337b581a0fa8a8715a6396bcc0755f134d34421503c441d1e2`.
- R3 handback: 151 lines, 19,962 bytes, SHA-256
  `3aadf044dded52f912b1c4abd91a315d31c73a8065c5ce27b4dce0fef83fdbae`.
- The three logical DI-4 sites remain BS-2, BS-3 and the BS-4 terminal disarm.
  Q6-6 occurs on the five reported operation rows and Q6-7 on the three
  reported rows.
- `RA-E` is cited by operation row `H-SN.6`; the inventory's count of one is
  correct. The handback's scratch-parser zero is a parser defect, not an
  inventory-count defect.
- The four R3-authorization snapshots exist and match the hashes recorded in
  the handback and archive indexes.
- The four R3-return snapshots created before this review transition are
  byte-preserving and indexed by their SHA-256 values.
- Final repository-only relative-link check after the review transition:
  **scope 15 files; 239 links checked; 0 broken; exit status 0**.
- `git diff --check` reported no whitespace errors after the review record and
  current-state transition were written.

## Checks not run and boundary

No host, retained-evidence, network, secret, service, database, package, build,
application test, hook test, formatter, implementation, activation, rollback,
commit or push operation was performed. Those operations remain prohibited and
would not resolve this documentation source-contract finding.

The no-host restriction remains unchanged. The R5 and H-0G retained paths
remain untouched pending separately gated LC-3 through LC-5 authority.

## Required next gate

WP-2 remains unaccepted. Peter may decide whether to authorize a focused
cumulative remediation of `WP2-R3-1` and `WP2-R3-2`. This review prepares no
prompt and grants no authority. No WP-3 prompt may be prepared and no WP-3
through WP-7 work may begin before a clean independent re-review and Peter's
later acceptance.
