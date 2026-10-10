# WP-3 R1 remediation handback — HARD STOP preserved

Work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-R1-20261010-22` · executor Claude · 2026-10-10 ·
repository-only, no host, no network, no research.

**WP-3 R1 REMEDIATION RETURNED — HARD STOP PRESERVED — INDEPENDENT RE-REVIEW PENDING**

This return does not accept WP-3, does not authorize WP-4 (or WP-5 through WP-7),
does not establish concrete Route 3 and does not select LIT-FULL. A different
independent reviewer must re-review the complete cumulative return (the corrected
[interface contract](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md)
and this handback), and Peter Duscha decides acceptance afterwards. Baseline v1.8,
F-1 B2-F with both lifecycle acts in and B3-OUT, effective EX-1/EX-2 and no EX-3
are unchanged; Q6-6 and Q6-7 remain unanswered; BC-2 remains a later WP-9 question.

## 1. Findings and remediation

### WP3-HS-R1 — cancellation semantics (Important) — remediated

*Finding.* The original return did not state, for DI-2, DI-3, DI-4 and DI-S, that
cancellation and abandonment semantics are unsupported.

*Remediation, in the contract.* (a) `UF-05` keeps its identifier and now contains,
besides the job-completion mechanism, the four exact missing facts: how a client
cancels or abandons its wait; whether an already accepted or queued job continues;
how the eventual job result and the mutation effect are observed; how
cancellation, client disconnection and an unconfirmed outcome map to the accepted
`refused`/`error` outcomes and unknown-effect boundaries. (b) New §3.0 separates
cancelling a client wait from cancelling a manager job and states obligations
`PO3-X1`…`PO3-X3`, including “A cancelled client wait is not proof that a queued
job stopped or that a mutating request had no effect”, and a seven-row cancellation
treatment table. (c) §§3.2, 3.3, 3.4 and 3.7 name the gap and the no-proof/no-silent-retry
rule (`PO3-2.4`, the DI-3 text, `PO3-4.3`, `PO3-7.2`). (d) Treatments: DI-1 keeps the
proposed fail-closed `error`, now labelled a proposed obligation, not an upstream
fact; DI-2, DI-3, DI-4, DI-S → expanded `UF-05`; DI-5 → `UF-10` owns Polkit-call
cancellation; DI-6 → no separate client-wait cancellation fact, cancellation belongs
to the enclosing DI-5 decision and the later subject cleanup under the accepted SN
contract (mechanics are WP-4's, not designed), identity facts stay `UF-12`/`UF-13`,
and no additional unsupported fact is registered. (e) The Q3 closure table, UF
registry, WP-4 input table, reconciliation, acceptance checklist, header and stop
result are reconciled. Q3-2, Q3-3, Q3-4 and Q3-7 remain not closed. Q6-6 and Q6-7
are not answered; the unknown-effect mapping for DI-3 and DI-4 at BS-2/BS-3 is not
decided and the BS-4 extension is not made.

*Revalidation correction (my own finding).* The original contract's common facts
attributed to WP-2 §7.1 a sentence that calls fail-closed and never retried silently.
WP-2 §7.1 (inventory lines 729–739) defines call-site counting only and contains no
such sentence. The line was replaced by exact sources (R8 SN-10 line 2521, IS-8 line
3212; WP-2 §8.1 lines 851–861 and Q4-7 line 1348; new citation entries `C-33`, `C-34`)
and the classification of the cancellation statements was set as follows: DI-3 and
DI-4 at BS-2/BS-3 child-form rule `DR`, non-child mapping Q6-6 (undecided); DI-2,
DI-S and DI-4 at BS-4 `PO3`, not an upstream fact.

### WP3-HS-R2 — reading ledger (Important) — remediated

*Original defect, quoted.* The original handback's reading ledger
(`phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-handback.md`, rows 3 and 5–19) states
the reading as “completely, or the sections cited in the contract”, and rows 2 and
4 as “reading map, §0, §16, §20; identity is pre-edit” and “restriction banner and
procedure sections; identity is pre-edit”. That wording does not unambiguously prove
complete pre-edit reading. The original handback is left unchanged.

*Statement for this execution.* Every one of the 26 items below was read as
specified in the R1 prompt, from its first byte to its last (for item 2: the reading
map, §0, §16 and §20, and the rest of the file; for item 4: the whole file including
the restriction banner), **before the first remediation edit**. This new read is the
evidence basis of the remediation; it supersedes any reliance on the original
ambiguous ledger and makes no claim about what the original executor read. After
reading and before the first edit, each file was re-hashed and was identical to the
values below.

Pre-edit ledger (path, lines, bytes, SHA-256):

| # | Path | Lines | Bytes | SHA-256 | Read |
|---:|---|---:|---:|---|---|
| 1 | `.agents/AGENTS.md` | 700 | 36014 | `87bab4ab8d67e308af0c59b99c8604235ee84d75cfa12448458b1a04cc88390a` | read completely, first byte to last |
| 2 | `docs/implementation-plan.md` | 2613 | 128704 | `de51835c0bec7e40dd3c9328443c14526c8a3b8faf8c26deb2bb7744d558a383` | reading map (lines 1–184), §0, §16 (lines 2395–2492) and §20 (lines 2559–2613) read first byte to last; the remainder of the file was also read before the first edit |
| 3 | `docs/review/Handover information` | 50 | 3312 | `324e06f2c0640ca2bb9b372d40ba963857b6de6d12d3ac9f36d62915ca5cc82b` | read completely, first byte to last |
| 4 | `docs/operations/disposable-test-server.md` | 328 | 15399 | `4ca5463a7a568d713301a2c63f6a51af62d87a9d19f7afdb01f25f910ffd884b` | whole file read first byte to last (restriction banner lines 1–46 and the procedure sections) |
| 5 | `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-g1-decisions.md` | 46 | 2455 | `09234e4acada1b3487f9147f0c8c76110a90dc1dc491e6a02f68892c07bab00e` | read completely, first byte to last |
| 6 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md` | 4816 | 551246 | `ab5db5010d9d1b2738b04f1ffbd62ab4414d901e9f7f79323ac49f811f660e04` | read completely, first byte to last |
| 7 | `docs/review/project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md` | 46 | 2653 | `594292d44d9ad5b161dc61a6f4cdc6457b56029d73cc1be60da84153c8c01e30` | read completely, first byte to last |
| 8 | `docs/review/phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | 7307 | 525019 | `a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02` | read completely, first byte to last |
| 9 | `docs/review/project-review-2026-10-04-p5-r5-rp11-h1-one-host-design-remediation-r6-acceptance.md` | 59 | 2633 | `afe1f2256259244f207c87a1244be5455ad18aebc6ac9a86db400fc105f729f5` | read completely, first byte to last |
| 10 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s2-r2-citations.md` | 1866 | 177481 | `299f0598bb198572f2edb994234a63956ecafc9ab1873cb10879d0a238dea1a5` | read completely, first byte to last |
| 11 | `docs/review/project-review-2026-10-06-p5-r5-rp11-h1-oh-s2-r2-acceptance.md` | 43 | 2186 | `af72d1e2017292b932148c467004bb096556553cdb6d5e9453846c12e20f258c` | read completely, first byte to last |
| 12 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md` | 1741 | 155403 | `f0c4e92e40f74bf5b4f65919853b9fbac6341a5e677fa6ab90e958246b3f3d2e` | read completely, first byte to last |
| 13 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md` | 88 | 4203 | `18a4288bfb3d572dc9f7a43bfd05ca87a819b002eb72b63081815c67f94fb4c7` | read completely, first byte to last |
| 14 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md` | 46 | 2925 | `13c8b466b666fc53b63e924e283a3bc7effc12389024a5e1327adf1f95a7527f` | read completely, first byte to last |
| 15 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-approval.md` | 50 | 2878 | `ab7b7e54f45ad3600ea4c00cde904aba10582ce44b8dbec6710a580167479332` | read completely, first byte to last |
| 16 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-operation-inventory.md` | 1450 | 230574 | `da341efb8c29b862d63c1463e981ccfedbe1f6680de2d416ff285fdae06461fd` | read completely, first byte to last |
| 17 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5-remediation-handback.md` | 101 | 14909 | `4329dc6cd52251d800c3dee00e9841db047b848e730eb79801bcfe10ec3d0e01` | read completely, first byte to last |
| 18 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-r5.md` | 80 | 3997 | `9a2b7144a464977137fe60667e7d07228e1602975949a7c02ce849f49e168420` | read completely, first byte to last |
| 19 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp2-acceptance.md` | 27 | 1626 | `b9a1691c6cbb9aca6c26e53ceaad08c7548d8e0aa4fb5392378701964b8be202` | read completely, first byte to last |
| 20 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-claude-prompt.md` | 244 | 12650 | `e09605d27daa8d25174302079a43ebccac64f69169007bad78496a8907457576` | read completely, first byte to last |
| 21 | `docs/review/project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp3-acceptance-and-claude-activation.md` | 66 | 2908 | `95522ce45ddd5acc2c8b3f53e5a62f300379e71465db9e16b9444549eac4a0cb` | read completely, first byte to last |
| 22 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md` | 419 | 39708 | `050254be8d42533301d24fe9df55e7ce839893b2c7a49e382310235d8816f733` | read completely, first byte to last |
| 23 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-handback.md` | 122 | 11019 | `b7a8e3724b5c6e5ac4ca18a2b0c8b5730137e255f317be00d02d1bd84e8b1416` | read completely, first byte to last |
| 24 | `docs/review/project-review-2026-10-10-p5-r5-rp11-h1-oh-s3-lit-full-wp3-hard-stop.md` | 77 | 3786 | `f486bab827e935de6fac56a5345f0729f26e0727ed815cc549a0af8b8e97b6a6` | read completely, first byte to last |
| 25 | `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-claude-prompt.md` | 242 | 12684 | `0452dd4c77aa4f92196ffa24ca0292e810f1bf1765133161eab2f57b34f553d9` | read completely, first byte to last |
| 26 | `docs/review/project-review-2026-10-10-p5-r5-rp11-h1-oh-s3-lit-full-wp3-r1-remediation-acceptance-and-claude-activation.md` | 66 | 3132 | `93ecf1877a2ab3f5fad9a5729a21deebf0ba223ff0d7ddd010cec096e32d2291` | read completely, first byte to last |

## 2. Deliverables and identities

Counts and hashes below are of the final files at return time (this handback is not
self-referential; its own identity is stated in the return message).

| Deliverable | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp3-interface-contract.md` (corrected in place; before: 419 / 39,708 / `050254be8d42533301d24fe9df55e7ce839893b2c7a49e382310235d8816f733`) | 469 | 50599 | `b766c10f2c28ac2d32a7dc7ee4ab2c92a3cf80d67fd70f345a9f0dd7ba92c888` |

## 3. Files created and edited

*Edited:* the interface contract (above). *Created:* this handback; four dated
verbatim snapshots with suffix `lit-full-wp3-r1-remediation-authorization`
(handover, status, implementation-plan §20, restriction banner lines 1–40) and four
rows (SHA-256 each) in the four archive indexes. *Replaced at return, the only
current-state files:* `docs/review/Handover information`,
`docs/project-management/status.md`, `docs/implementation-plan.md` §20 current-state
block and the banner (lines 1–40) of `docs/operations/disposable-test-server.md`.
Nothing else was edited; the original WP-3 prompt and handback, the independent
review, the activation records, the WP-2 inventory, all accepted proposals and
acceptances and every historical snapshot are byte-identical to their pre-edit hashes.

## 4. Final counts

Interfaces 7; call sites 41 (23 + 1 + 1 + 3 + 6 + 6 + 1); Q3 identifiers 9 (Q3-1
through Q3-7, Q3-9, Q3-11; none closed except Q3-11 as a fail-closed record);
citation entries 34 (`C-01`…`C-34`; two added); unsupported facts 18 (`UF-01`…`UF-18`,
`UF-05` expanded); WP-2 rows 318; Q3 tag instances/rows 38/34. A mechanical re-parse of
the call-site table confirmed the roster; there are no discrepancies.

## 5. Checks

*Run:* repository-only reads and searches; mechanical Markdown-table parse (call
sites per interface, Q3 ids, UF ids, citation ids, column consistency of 12 tables);
`wc -l -c`; `sha256sum` before and after; link and path check over the contract,
this handback, the four pointers and the four archive indexes; `git diff --check`;
read-only `git status`/`git diff`. All passed (results in the return message).
*Not run, by prohibition:* application or hook suites, builds, formatters, linters.

## 6. Unresolved later-package questions

`UF-01`…`UF-18` (supply by an authorized record); Q4-7 (enforcement of the class-E
deadline and of cancellation on an in-process call; WP-4); Q4-1, Q4-8 (subject
cleanup mechanics); Q6-6 (meaning of `effect: "unknown"` off the child form); Q6-7
(BS-4 extension and other gaps); BC-2 (WP-9); the 109 unclassified run-time-varying
names (C-4); the BS-RM citation obligation (OH-S2b). None is decided here.

## 7. Prohibited actions

None performed: no SSH or host access, no retained evidence, secret, credential,
player data, production, staging, oracle-test, Foundry or database access, no
network research, package operation, implementation, configuration or
infrastructure edit, launcher work, build, test, formatter, service or database
operation, cleanup, workspace recreation, OH-S4/OH-S4p, H-1/H-2, activation,
rollback, commit or push. The R5 and H-0G retained paths were not touched. WP-4
through WP-7 were not prepared.

## 8. Questions for the independent re-review

1. Is the cancellation treatment of all seven interfaces (§3.0) correct, and is
   the DI-6 statement (no additional unsupported fact) acceptable, or should an
   additional `UF` be registered?
2. Are the `DR`/`PO3` classifications of the unknown-effect statements right for
   DI-2 and DI-S, and for DI-4 at BS-4, without deciding Q6-6 or Q6-7?
3. Is the replaced `WP-2 §7.1` citation (revalidation correction) and the new `C-33`,
   `C-34` accurate?
4. Does the new 26-item ledger prove complete pre-edit reading unambiguously?
5. Is the expanded `UF-05` the exact missing fact, with no source silently supplying
   any part of it?

**WP-3 R1 REMEDIATION RETURNED — HARD STOP PRESERVED — INDEPENDENT RE-REVIEW PENDING**
