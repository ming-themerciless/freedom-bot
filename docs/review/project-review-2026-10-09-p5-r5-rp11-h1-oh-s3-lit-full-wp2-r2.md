# Independent re-review — LIT-FULL WP-2 R2 remediation

Date: 2026-10-09

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP2-R2-20261009-16`

Reviewed deliverables:

- [corrected cumulative operation inventory](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md);
- [R2 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-handback.md);
- [accepted R2 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-claude-prompt.md); and
- [acceptance and Claude activation](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r2-remediation-acceptance-and-claude-activation.md).

## Recommendation

**Do not accept WP-2. A separately authorized cumulative remediation and a new
independent re-review are required.**

The R2 return has two Blocking findings and one Important finding. The proposed
inventory does correct the R1 AM-0 row into a non-operative gap, separates the
historical DI-3/DI-4 children from the replacement child set, defines the
call-site counting unit and reconciles the three DI-4 sites. Those corrections
do not make the return acceptable because the one-time execution did not follow
its binding source-reading precondition and the resulting document extends a
fail-closed unknown-effect obligation beyond the accepted text.

This review does not accept WP-2, authorize remediation, authorize WP-3,
establish concrete Route 3 or select LIT-FULL for implementation. Peter Duscha
retains every acceptance and assignment decision. WP-3 through WP-7 remain
gated.

## Findings

### WP2-R2-1 — Blocking — the one-time execution did not satisfy its binding complete-reading precondition

The accepted R2 prompt requires, before editing, a complete first-byte-through-
EOF read of every source required by R1 items 5 through 15. The activation
record expressly makes the prompt's reading clause binding. Claude's handback
states that four governing sources were not read end-to-end: the cumulative R8
proposal, the accepted one-host design amendment proposal, the OH-S2 R2
citations and the accepted WP-1 R6 proposal. Searches and selected passages were
used instead.

This is not merely an unreported check. It is a failed precondition of the exact
one-time assignment, and the handback acknowledges that its claims about Q6-7
and the DI-4 sites therefore do not rest on the required complete source review.
The current pointers nevertheless describe the prompt as executed and the
handback as complete. Because source completeness is what prevents an inventory
from omitting or changing accepted procedure behavior, the deviation blocks the
gate.

**Required remediation:** Peter must decide whether to authorize another
cumulative remediation execution. Any new execution must read every required
source completely before editing, revalidate all affected and allegedly
unaffected inventory content against those sources, report that coverage
accurately, and return for independent review. The consumed one-time authority
cannot be treated as if it had satisfied this requirement.

Evidence: accepted prompt lines 22–44, especially item 6; activation record
lines 23–39; R2 handback lines 116–121.

### WP2-R2-2 — Blocking — the inventory extends SN-10 to BS-4 without accepted authority

The remediation correctly counts BS-2, BS-3 and BS-4 terminal disarm as three
logical DI-4 call sites. Counting the site does not establish that every
failure contract attached to BS-2/BS-3 also applies to BS-4.

The inventory repeatedly states that SN-10 names BS-2 and BS-3 and that accepted
text does not separately state BS-4's unknown-effect treatment. Despite that,
`RT4.SN.1` says the `effect: "unknown"` obligation “must still be honoured for
each DI-4 interaction”; §8.1 says Q6-6 carries it “at all three sites”; and
`RT4.BS4.2` tags the BS-4 row with Q6-6 while its blocking cell describes the
disarm as mutating under SN-10. Q6-6 similarly treats the BS-4 call as within
the obligation while acknowledging the missing accepted statement.

That is the same category of inconsistency R2 was meant to avoid: the inventory
states that authority is missing and simultaneously selects the affirmative
extension. “Same call form” is not accepted authority for extending a
fail-closed interruption/indeterminate-completion contract. A later package
could consume this as required behavior, so this is procedure-correctness and
production-reliability blocking.

**Required remediation:** preserve BS-4 as the third DI-4 call site, but do not
state that SN-10 or A-I-16 applies there unless a governing accepted passage
actually says so. Represent the absence as an unanswered later-package gap,
without selecting either extension or exclusion, and reconcile `RT4.BS4.2`,
`RT4.SN.1`, §8.1, Q6-6, the tags/counts, the acceptance checklist and the
handback. If a complete source read finds accepted text that resolves the point,
cite it and apply the prompt's stop rule rather than infer from the call form.

Evidence: inventory rows `RT4.BS4.2` and `RT4.SN.1`; inventory §§8.1 and 12
Q6-6; the handback itself says accepted SN-10 names only AK-1 and BS-2/BS-3.

### WP2-R2-3 — Important — the durable handback omits the final exact link-check result

The accepted prompt requires the handback to report checks run and exact
results, and the repository protocol requires the complete terminal handback to
be durable before chat return. Handback §5 item 6 reports the pre-handback link
check, then defers the final result to the terminal chat message. Chat is not
durable handoff evidence.

Independent repository-only checking of the four pointers, four archive
indexes, inventory and handback found **230 relative links, 0 broken**. That
result is not present in the handback.

**Required remediation:** include the final exact link/path result in the
durable cumulative handback. Do not rely on terminal chat to complete a required
check record.

## Verified evidence

- Prompt: 205 lines, 9,640 bytes, SHA-256
  `4fb48bcd3c482fe053623256ebe54d5d2cf379913605099146a04544cb10d14b`.
- Inventory: 1,410 lines, 220,050 bytes, SHA-256
  `e2960f233d4d5e540a68011f6dab2bc297442088eab28d36867b5736f13e3012`.
- Handback: 155 lines, 22,952 bytes, SHA-256
  `72d5e4eef058f81f839a57d9138eb98b17bf8c6bb10be355bfd9b68790d25fc2`.
- Independent parsing of the operation tables reproduced 317 rows and every
  reported class total, including 316 operation/contract/composition rows and
  one GAP row.
- `RT2.AM0.7` is non-operative, carries Q6-7 alone and selects neither answer.
- The replacement child-surface text removes DI-3/DI-4 distribution children
  and retains only the DI-6 subject; the defect is the separate BS-4 contract
  extension described above.
- The three DI-4 logical sites are present: BS-2, BS-3 and BS-4 terminal
  disarm.
- The four R2-authorization snapshots exist, their SHA-256 values match the R2
  handback and all four archive indexes.
- The four R2-return snapshots made before this review are byte-preserving and
  indexed as part of this current-state transition.
- The final relative-link check over the four pointers, four archive indexes,
  inventory and handback found 230 links and 0 broken.
- `git diff --check` reported no whitespace errors before this review record
  and current-state transition were written.

## Checks not run and boundary

No host, retained-evidence, network, secret, service, database, package, build,
application test, hook test, formatter, implementation, activation, rollback,
commit or push operation was performed. Those operations remain prohibited and
would not cure the source-authority defects in this documentation return.

The no-host restriction remains unchanged. The R5 and H-0G retained paths
remain untouched pending separately gated LC-3 through LC-5 authority.

## Required next gate

WP-2 remains unaccepted. Peter may decide whether to authorize a cumulative R3
remediation that closes `WP2-R2-1` through `WP2-R2-3`. This review prepares no
prompt and grants no authority. No WP-3 prompt may be prepared and no WP-3
through WP-7 work may begin before a clean independent re-review and Peter's
later acceptance.
