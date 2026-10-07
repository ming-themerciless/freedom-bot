# Proposal — R5 H-0 remediation: complete checkout contract, symlink-safe source consumption and retained-evidence rationale (R3)

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR3-20261006-05`

Date: 2026-10-06

Author: Claude (repository-only documentation remediation)

Independent reviewer: Codex

Decision owner and Acceptance Authority: Peter Duscha

Prompt:
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-claude-prompt.md)
(SHA-256 `752e227e2221369547240ae5c088eb5b251b87f5ef4a9a42f67f041d121bd196`,
8944 bytes, equal to the authority's pin)

Authority:
[`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-authority.md)
(SHA-256 `d589cbc16cfe1aac07026eaa473a3c9169567c4a1a9dcf48dc502f1b78d61833`)

Findings remediated:
[`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-findings.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-findings.md)
(SHA-256 `70582c3cba15348c271ab37bdcf26534e8acdc4a36100682ba38a5e80e53eda5`)

Handback:
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-handback.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-handback.md)

Supersedes, if accepted: the R2 proposal
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-proposal.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-proposal.md)
(SHA-256 `04a4abb4aa83c89b8e44479b1e56a12e423da9eb1967f8be0a9c85f9b11ce105`,
88131 bytes), which itself would have superseded the DR1 proposal
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-proposal.md)
(SHA-256 `403b2bc1acec24ceea4fb7e5ad327efde52f200f29fd09ac6e0d0ff357582d60`).
R2 and DR1, their handbacks, prompts, authorities and the R2 review are
consumed records and are not edited.

**State: proposal, unreviewed and unaccepted.** Peter Duscha's decisions D-1
through D-7 and the disposable-Test lifecycle policy remain **recorded** as
decided by the R2 authority; the R3 authority records no new decision. R2
itself remains unaccepted. Everything else in this file — every amendment
text, every command specification, every gate and the cleanup/recreation
sequence — is **proposed text** for Codex's independent re-review and Peter's
later acceptance. Nothing here changes the accepted one-host design file,
accepts an R5 fact, composes an `H-0 PASS`, creates an authority or authorizes
any host access, cleanup, H-0G, CPP, OH-S2, OH-S4p or later slice. A decision
is not execution authority. Labels *(R2)* mark amendments first proposed by
R2 and carried here; labels *(R3)* mark amendments new or changed in R3. The
accepted design is cited, not edited.

---

## 0. Outcome

Independent Codex review accepted R2's HF-15 correction and found three
defects (R2 review):

* **R2-F1 (Blocking).** CK-9 left the closed set of `.git` top-level entries
  "to be fixed by review" and asked the reviewer to choose its evidentiary
  basis, so no slice could implement or evaluate it fail-closed.
* **R2-F2 (Blocking).** CK-3 matched each worktree symlink to Git mode
  `120000` but never inspected its link text or target, yet claimed to reject
  "symlinks that escape". The pinned tree's intentional absolute `venv`
  symlink shows that a blanket ban would misdescribe the repository, while
  mode-matching alone protects nothing.
* **R2-F3 (Important).** §12.4 said durable handbacks "reproduce the retained
  bytes' manifests and digests" as the reason no preservation copy is needed.
  Manifests and digests authenticate or describe bytes; they do not reproduce
  them.

This R3 proposal resolves all three in the proposal itself:

1. **CK-9 *(R3)*** is a complete, executable `.git` contract of the second form
   the R3 prompt allows: a **bounded structural inventory** in which every
   path under `.git` must match one row of a closed table, each row derived
   from the accepted CR retrieval sequence (R5 c015 … c025) and the Git
   repository layout that sequence produces, together with an **explicit
   rejection** of every Git mechanism that can redirect, replace, execute,
   import or borrow state. It does not claim that an unobserved incidental
   file set is authoritative: entries the accepted procedure may or may not
   create are admitted only as optional rows with exact structural
   constraints, and anything outside the table is `HARD STOP` (§8.2, §8.5).
   The open review question is removed.
2. **CK-3 *(R3)*** authenticates every worktree symlink's link text against
   the pinned blob without dereferencing it, classifies absolute and
   lexically escaping targets as **checkout-escaping and non-consumable**,
   and no longer claims that inventory rejects them. A new **source-
   consumption contract SC-1 … SC-8** (§8.6) requires every consumed path to
   be named in the slice's covered-source list, to have no symlink in any
   component, and to terminate in an owned, non-writable, single-link regular
   file whose bytes equal the accepted digest, read through a defined
   no-follow walk. CK-10, the slice matrix, `source_checkout`, A-2, `ACT`,
   TR-2, TR-10, A0-02, H-1, the rebuild and every test path are reconciled
   (§8.3, §8.4).
3. **§12.4 item 8 *(R3)*** is replaced. Cleanup eligibility now rests only on
   explicit closure, or Peter's explicit abandonment, of every dependency on
   the host bytes, followed by the existing CE enumeration, review,
   literal-list approval and separately authorized cleanup; a path whose
   bytes a future review or recovery needs stays retained unless a separately
   authorized preservation or export succeeds and is accepted (§12.7).

Everything else is carried forward from R2 unchanged in substance: the HF-15
repair, D-1 … D-7, Route 1, P-0p/AM-0, HF-20/CL-21i, FI-1 … FI-5, the
composition anchors, the slice gates and the lifecycle policy (§3 … §7, §9 …
§11, §13).

| # | Subject | Decided | Where |
|---|---|---|---|
| D-1 | capture-root parent and template | `/var/lib/rp11-capture`, `ubuntu:ubuntu` `0700`, not a mount point, no POSIX ACL xattr; `/var/lib/rp11-capture/<activation_id>-pass-a` | §4 |
| D-1b | parent creation | only CPP, after H-1 PASS and before the first A-2 | §4.4 |
| D-1c | HF-15 completion | direct H-0G observation, not DR1's ancestor inference alone | §4.3, §11 |
| D-2 | HF-18 | withdrawn from H-0; per-slice fail-closed client preflight; human-shell slices record the no-hook case | §5 |
| D-3 | interpreter | Route 1, exact `/usr/bin/python3.14`, with every DR1 consequence | §6 |
| D-3b | drift control | version- and digest-equality gates; a package hold is not a substitute and is not authorized | §6.7 |
| D-4 | Polkit collision | P-0p at H-1 before mutation; AM-0 root re-check; `unreadable` is never absence | §7.1 |
| D-5 | PO-21 (i) | HF-20 split; CL-21i is an OH-S2 result; AP-0/AM-0 fail closed until accepted | §7.2 |
| D-6 | successor | narrow H-0G composing with R5; any changed anchor → full fresh H-0 under separate authority | §10, §11 |
| D-7 | repository source on Test | normal workspace preserved and not an RP-11 source; fresh exclusive pinned checkout per source-consuming slice; HF-03 repository ownership leaves H-0 | §8 |
| — | disposable-Test lifecycle | approved policy; bounded exact-path cleanup and recreation, each separately authorized later | §12 |

---

## 1. Sources examined

All reads were local and read-only. Digests are of the working-tree files at
the start of this assignment. Every source R2 cited by digest was recomputed
where it is relied on here and is unchanged, so R2's and DR1's line citations
remain valid.

| Source | SHA-256 | Read |
|---|---|---|
| `.agents/AGENTS.md` | `28ce54ef69b94e21eb82e298aef5bef5fded36bb34dde202eea438acc7c84ad2` | completely |
| `docs/implementation-plan.md` | `39f72198f379fac3b33ccf3784d90e013fc205b8ebea988c06b92a3e594218c9` (before this assignment's §20 update) | reading map, §0, §16, §17, §20 |
| `docs/review/Handover information` | `68c9397a76f32344709b8dc06cb55171e946a5d1a54c270f8e6ffbd7baba60f7` (before update) | completely |
| `docs/project-management/status.md` | `a722a62ea09fa9351cbbae552d887b0c8b93884f55331dca380b0594af5725e1` (before update) | current-status section |
| `docs/operations/disposable-test-server.md` | `6c6ea256b1121e3905232afe684e153f52574d478bb4301f36f7966b67ba47a1` | restriction banner and §1 profile |
| R3 prompt | `752e227e2221369547240ae5c088eb5b251b87f5ef4a9a42f67f041d121bd196` | completely |
| R3 authority | `d589cbc16cfe1aac07026eaa473a3c9169567c4a1a9dcf48dc502f1b78d61833` | completely |
| R2 independent review (findings) | `70582c3cba15348c271ab37bdcf26534e8acdc4a36100682ba38a5e80e53eda5` | completely |
| R2 authority | `f84d23306a9d4b1de2e5b6887ac9af6758d0e471566b4d297553555fc6ac1e16` | completely |
| R2 consumed prompt | `c13d7177ba92bc7e24e2b19073e650d3f91f903a4279e5bbbbe2a3a9cf287169` | completely |
| R2 proposal | `04a4abb4aa83c89b8e44479b1e56a12e423da9eb1967f8be0a9c85f9b11ce105` | completely |
| R2 handback | `6c256a18ee9e8aa059b68d0b06f60ef7cda2612a97fb140c4590a832bdfc7d47` | completely |
| DR1 proposal | `403b2bc1acec24ceea4fb7e5ad327efde52f200f29fd09ac6e0d0ff357582d60` | completely |
| DR1 handback | `0a42d9266abd5fa6bc9a2849c6280baf38903218c42762eb5128ea47398f3509` | completely |
| R5 prompt | `57d23c1ba683ce8c2be15fe101da959a9dc1334ff89a1b0c66f917f26cf42e8e` | completely |
| R5 handback | `5bbc72a56cf43de8de149c27703fec5c7d80115113567de8778f83896fa652af` | through **Checks not run**; Appendix B records c013 … c027, to ground CR and CK in the exact accepted retrieval sequence |
| R5 independent review | `eb5506b228604a6621c91b652a7a2ffec5e8364be0dfb10195ea69c65e2f49ea` | completely |
| accepted one-host design `phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md` | `a752a4b8fe7eb1edf3e3a25decd3a7517ecccc85fedbb0b0b7e003cb7e615d02` (unmodified) | §2 IA-12; §4.1.3 TR-0 … TR-12 and the D3-R2/D3-R4 notes; §4.1.4; §4.1.5; §4.2.5-R1 (a) … (c); §4.3.2; §4.5.1 … §4.5.3; §4.6.2 |
| C11 `phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md` | `f6405cd94a826e7883b80589c1edcd2be1e5b56b4481987d7cacdea96312f70b` (equal to R2 §1) | targeted: C-6 (`:515`) and its failure rows (`:1459` … `:1461`) |
| operational draft `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | `5c6046fc3dc0b9a931cc32076233b1ea9185dc14c5d0ea1abc193687dcca7de6` (equal to R2 §1) | targeted: `PIN.worktree`, `MI.capture_root_A`, A0-02, A1-S1, A1-S2 |
| pinned commit `46d1c35a029ca8287779ae87d08a370ba0a0f2ef` in the controller's local object store | content-addressed; tree `56ccab51963de051d67426be8c560d69c8f3638c`, equal to R5 c019 | `git ls-tree -r --full-tree` and `git cat-file` only, to establish the tree's symlink, gitlink and attribute facts (§8.6.1) |

No remote host, retained evidence directory, secret, credential, SSH
configuration, application or player data was read. No network access
occurred. The pinned commit was read from the controller's own object store;
because Git objects are content-addressed, its tree is byte-identical to the
one R5 retrieved (both name tree `56ccab51…f3638c`).

---

## 2. Decision and finding traceability

### 2.1 Decisions (recorded by the R2 authority) to amendments

| Decision | Recorded text (summary of the R2 authority's prompt) | Amendment(s) in this proposal | Later gate that still applies |
|---|---|---|---|
| D-1 | parent `/var/lib/rp11-capture`, `ubuntu:ubuntu`, `0700`, not a mount point, no POSIX ACL xattr; root `/var/lib/rp11-capture/<activation_id>-pass-a`, exact accepted activation-ID grammar | §4.2 §4.1.5 *(R2)*; §4.5 AP-0 *(R2)*; §4.6 OH-S3 input | Codex review of R3; OH-S3 draft re-review |
| D-1b | parent created only by CPP after H-1 PASS and before the first A-2 | §4.4 CPP | CPP's own authority, Codex review, Peter acceptance |
| D-1c | HF-15 completed by direct H-0G observation | §4.3 HF-15 *(R2)*; §11 H-0G | H-0G authority; Codex review of H-0G and composition |
| D-2 | HF-18 withdrawn from H-0; per-slice exact-executable preflight; human-shell slices record the no-hook case | §5.2 HF-18 *(R2)*; §9 FI-1 | each client-running slice's authority |
| D-3 | Route 1, exact `/usr/bin/python3.14`, all DR1 consequences preserved | §6 (Role A–H inventory; OH-S2, OH-S4p, U-9, tests) | OH-S2, OH-S4p, OH-S5 reviews; Peter's U-9 restatement |
| D-3b | version- and digest-equality gates; no package hold authorized | §6.7 | H-2/AP-0 implementation (OH-S4) |
| D-4 | P-0p at H-1 before mutation; AM-0 root re-check; `unreadable` never absence | §7.1 | OH-S7/OH-S8 H-1 authority |
| D-5 | HF-20 split; CL-21i an OH-S2 result; AP-0/AM-0 fail closed until its closed list is accepted | §7.2 | OH-S2 acceptance of CL-21i |
| D-6 | narrow H-0G composing with R5; a changed anchor requires a full fresh H-0 under separate authority | §10, §11 | H-0G authority; composition review |
| D-7 | normal workspace preserved and not an RP-11 source; fresh pinned checkout per source-consuming slice; HF-03 repository ownership leaves H-0; H-0G repository-free | §8 (HF-03, U-3, IA-12, §4.1.4, §4.1.5, TR-2, TR-10, H-1 record, H-2, A-2, `ACT`, A0-02, FI-1, CR, CK *(R3)*, SC *(R3)*, slice matrix) | each source-consuming slice's authority |
| lifecycle | Test is disposable; nothing deleted now; exact-path cleanup and recreation after gates | §12, including §12.7 *(R3)* | §12.3 gates LC-1 … LC-7 |

### 2.2 Findings to changes

| Finding | Source | Change | Section |
|---|---|---|---|
| **R2-F1** CK-9 is not an executable closed contract | R2 review (Blocking) | CK-9 *(R3)*: closed structural table G-1 … G-14 for every path under `.git`; mechanism rejection table GX-1 … GX-12; Git self-location checks; exact PASS/`HARD STOP` outcomes and bounded evidence; review question 13 withdrawn | §3.2, §8.2, §8.5, §15 |
| **R2-F2** CK-3 claims an escaping-symlink control it does not perform | R2 review (Blocking) | CK-3 *(R3)*: `lstat`-only inventory; link text equal to the pinned blob; lexical classification; escaping symlinks recorded **non-consumable**; symlink permission bits not misread. CK-10 *(R3)* hashes through the no-follow walk, not `sha256sum`. SC-1 … SC-8 source-consumption contract; the pinned tree's one symlink, `venv`, reconciled; interpreter-path clarification; slice matrix, `source_checkout`, A-2, `ACT`, TR-2, TR-10, A0-02, A1-S1/A1-S2, H-1, rebuild and test paths reconciled | §3.2, §8.2, §8.3, §8.4, §8.6 |
| **R2-F3** digests do not reproduce retained bytes | R2 review (Important) | §12.4 item 8 replaced; LC-2 and CE require a per-path host-byte dependency statement; retention rule RD-1 … RD-5 | §3.2, §12.3, §12.4, §12.7 |
| H-0G runs `df`/`findmnt` against the expected-absent parent | Codex review of DR1 (Blocking); **accepted fixed** by the R2 review | carried unchanged: HF-15 *(R2)*, G-15a … G-15d, exit contract, CPP pre/postcondition | §4.3, §4.4, §11 |
| HF-15 capture-root parent not observed | R5 review finding 1 (Blocking) | D-1 binding; FI-1; H-0G observation | §4, §9, §11 |
| HF-18 client path not observed | R5 review finding 2 (Blocking) | HF-18 withdrawn (D-2) | §5 |
| `/usr/bin/python3.12` absent; CPython 3.14.4 present | R5 review finding 3 (Important) | Route 1 (D-3) | §6 |
| `/etc/polkit-1/rules.d` unreadable; collision unknown | R5 review finding 4 (Important) | P-0p, AM-0 (D-4) | §7.1 |
| PO-21 (i) condition paths unnamed | R5 review, closing paragraph | HF-20 split, CL-21i (D-5) | §7.2 |
| unprivileged H-1 P-0 and AP-0 cannot establish absence in a `0750 root:polkitd` directory | found by DR1 | P-0p, AP-0 *(R2)* | §7.1 |
| the static launcher image embeds `/usr/bin/python3.12` | found by DR1 | Route 1 includes the rebuild | §6.2, §6.5 |
| HF-03 repository ownership not observed; fixed checkout dirty and uncontrolled | R3 review; R5 HF-03 and HF-NOTES | D-7: element withdrawn from H-0, replaced by per-slice CK inventory | §8 |
| H-0 contract allowed `not specified` at PASS | R5 terminal state | FI-1 … FI-5 *(R2)* | §9 |
| Test objects accumulate with no lifecycle | Peter's lifecycle decision | §12 | §12 |

---

## 3. What changed, exactly

### 3.1 What R2 corrected in DR1 (carried)

| DR1 text | Defect | R2 replacement (carried) |
|---|---|---|
| §3.5 (a): "`findmnt --target` and `df --output` on that path (which resolve to its nearest existing ancestor)" | false: both commands fail on a nonexistent operand (R5 c142, c143) | §4.3: `lstat`/`listxattr` on the parent; ancestor determined from the literal; `findmnt`/`df` on `/var/lib` only |
| §3.6 HF-15 (DR1): "If it does not exist, it records `ENOENT` and the same two commands on the parent path, naming the mount they resolve to" | same | HF-15 *(R2)*, §4.3 |
| §9 H-0G command set: `findmnt --target /var/lib/rp11-capture`; `df --output … /var/lib/rp11-capture` | same; and H-0G PASS required "every command observed", so PASS was unreachable | §11 G-15a … G-15d and the exit contract §11.5 |
| §3.5 (b) ancestor-rule alternative | not selected (D-1c) | withdrawn; the ancestor facts are now **directly observed** by H-0G, and CPP proves same-filesystem non-mount at creation |
| §7 FI-1 "the repository root's identity (HF-03, once Peter decides …)" | superseded by D-7 | §9 FI-1 *(R2)* |
| §8 HF-03 repository ownership "incomplete … depends on Peter's pending decision" | superseded by D-7 | §10: withdrawn from H-0 |
| §9 "no access … to `/opt/freedom-blades/platform` on `oracle-test`" | correct, now stated as a D-7 rule | §11.6 |
| §10 D-7 "existing open decision" | decided | §8 |

### 3.2 What R3 corrects in R2

| R2 text | Defect | R3 replacement |
|---|---|---|
| CK-9: "a subset of the closed set observed for a fresh retrieval of this form (`HEAD`, `config`, `objects`, `refs`, `shallow`, `index`, `FETCH_HEAD`, `logs`), the set to be fixed by review (question 13)" | R2-F1: no executable rule; the listed set was never observed (R5 recorded no `.git` listing), and the reviewer was asked to choose it | CK-9 *(R3)* and §8.5: a closed structural table covering every path under `.git`, not only its top level; optional rows for entries the accepted procedure may or may not create; mechanism rejections; self-location checks; outcomes and evidence. Question 13 withdrawn |
| CK-3: "a worktree symlink only where the commit's tree records mode `120000`", with "Rejects … symlinks that escape" | R2-F2: mode-matching inspects no link text or target, and inventory does not stop a later dereference | CK-3 *(R3)*: link text authenticated against the pinned blob without dereferencing; lexical classification; escaping symlinks recorded **non-consumable**; the "Rejects" column no longer claims escape rejection. Prevention moves to SC-1 … SC-8 (§8.6), which governs every consumption |
| CK-3: "no entry group- or world-writable" applied to symlinks | Linux `lstat` reports permission bits `0777` for every symlink and never uses them, so the rule would stop every checkout containing `venv` | CK-3 *(R3)*: permission and set-ID rules apply to regular files and directories; a symlink is checked for type, owner, group, link text and placement only |
| CK-10: "the SHA-256 of each … covered source the slice reads equals the authority's pinned value (R5 c026 pattern)" | R5 c026 used `sha256sum`, which follows symlinks, so the "pattern" could hash a symlink's target as repository source | CK-10 *(R3)*: hashing only through the no-follow walk NFW (§8.6.3); `sha256sum`, `cat` or any following reader on a checkout path is prohibited for source verification |
| CR-3: R5's `-c` list without `advice.detachedHead=false` and `init.defaultBranch=h0-unborn`; CR-4 without `timeout 900` | an incomplete transcription of the accepted sequence (R5 c015, c016). Neither omission weakened a security control, but CK-9 now derives from the exact sequence | CR-3 and CR-4 *(R3)* carry R5's exact options |
| §8.4 TR-2, TR-10, A-2, `ACT`, `source_checkout`, A0-02 | named the checkout but not how a consumer avoids a symlink component | §8.4 *(R3)* amendments bind each to SC-1 … SC-8 |
| §12.4 item 8: "the accepted reviews rely on the durable repository handbacks, which reproduce the retained bytes' manifests and digests" | R2-F3: a manifest or digest authenticates bytes; it does not reproduce them | §12.4 item 8 *(R3)* and §12.7 RD-1 … RD-5 |
| §15 questions 6 and 13 | asked the reviewer to supply the CK-9 set and its evidentiary basis | §15 rewritten: every question asks only whether a completed rule is sufficient |

Everything else in R2 is carried forward with its substance unchanged.

---

## 4. HF-15 and the capture root (D-1, D-1b, D-1c)

### 4.1 Constraints on `MI.capture_root_A` (carried from DR1 §3.1, K-5 amended)

| # | Constraint | Source |
|---|---|---|
| K-1 | a maintainer input, reviewed by Codex | operational draft `MI.capture_root_A`; design §4.1.5 |
| K-2 | absolute; on `oracle-test` | design §4.1.5; OH-D-3 decision |
| K-3 | pass-specific; distinct from `MI.capture_root_B`, neither inside the other | OH-D-3 decision; draft C-6, `MI.capture_root_B` |
| K-4 | does not exist before its pass; created **exclusively** by the entry at X-1 (TR-11), which runs as `ubuntu` with `NoNewPrivileges=yes`, `UMask=0077` and no `sudo` | draft A0-08, C-6; design TR-11, §4.2.5-R4 (b) unit text |
| K-5 | outside the Git worktree `/opt/freedom-blades/platform` | draft C-6; design §4.1.5 |
| K-6 | outside `/tmp` and `/var/tmp` | draft C-6; design §4.1.5 |
| K-7 | outside `/var/lib/fb-evidence-p5-0` and `/var/lib/freedom-blades` | design §4.1.5 |
| K-8 | neither contains nor lies under any §4.2.3 path, nor under `/var/lib/freedom-blades-rp11` | design §4.1.5 |
| K-9 | on a filesystem whose type and mount options H-0 records (HF-15) and RP-11's review accepts: directory and file synchronization semantics and same-directory hard links (PO-20) | design §4.1.5; draft `MI.capture_root_A` |
| K-10 | owned by the operator account (`ubuntu`); directory `0700`, files `0600` | draft C-7; U-3 binding |
| K-11 | its creation is made durable by a directory barrier on the directory that contains it | draft C-6 |
| K-12 | a common parent, if any, already exists and is not created, cleaned up or otherwise written by the mechanism or operator beyond each root's own entry, and holds no capture file | draft C-6 |
| K-13 | retained unmodified after the pass; never removed, renamed or reused | draft C-8 |
| K-14 | `pass-a.json` names exactly one capture root, and AP-0 requires it absent | design §4.2.5-R1 (a), §4.2.5-R2 (d) |
| K-15 | the holder and CP read the capture root's presence as root (HL, CQ-4, `pass-ended` predicates) | design §4.2.5-R2 (g), §4.2.5-R5 |

Two consequences follow, and neither is stated in the accepted text.

* **K-4 with K-12 requires a pre-existing parent writable by `ubuntu`.** The
  entry is unprivileged and may not create the parent (K-12), so the parent
  exists before the pass and grants `ubuntu` write and search permission.
* **K-13 excludes `/run`.** A `tmpfs` does not survive a kernel boot (PO-20 (g)),
  so retained evidence cannot live there.

*(R2)* **K-5** is extended by D-7: the capture root and its parent also lie
outside every RP-11 fresh checkout (§8.2) and every retained checkout. Both
are component-wise exclusions, never string-prefix tests.

The candidate analysis that led to D-1 is DR1 §3.2, carried for the record:

R5 recorded filesystem facts (HF-15) for `/`, `/usr/local`,
`/usr/local/libexec`, `/etc`, `/etc/systemd/system`, `/etc/polkit-1/rules.d`,
`/var/lib`, `/var/tmp` and `/run` (c124–c141), and owner/mode facts (HF-11,
c105) for the §4.2.3 parents.

| Candidate parent | R5 facts | Verdict |
|---|---|---|
| `/var/tmp` | ext4 `/`, `1777`, 30-day ageing (c138, c139, c105, c150) | **excluded** by K-6; ageing contradicts K-13 |
| `/run` | `tmpfs` (c140, c141) | **excluded** by K-13 |
| `/`, `/usr/local`, `/usr/local/libexec`, `/etc`, `/etc/systemd/system`, `/var/lib` | ext4 `/` (c124–c133, c136, c137); `root:root` `0755` (c105) | **not usable as the direct parent**: `ubuntu` cannot create an entry in a `root:root` `0755` directory, so X-1 would fail (K-4). `/usr/local/libexec` and `/etc/systemd/system` also hold §4.2.3 paths |
| `/etc/polkit-1/rules.d` | `root:polkitd` `0750` | **excluded**: polkit rules directory; not writable by `ubuntu` |
| `/home/ubuntu/…` | password-database entry only (c035); no filesystem fact | **rejected**: H-0 forbids home-directory content; the directory co-locates the operator's credentials and any agent client's state with evidence; not observed by R5 |
| `/srv/…`, `/opt/…` (outside the worktree) | none | **rejected**: no R5 fact; `/opt/freedom-blades` holds the worktree and the test runtime |
| **a new directory `/var/lib/rp11-capture`** | its containing filesystem is `/var/lib`'s: ext4 on `/dev/sda1`, `rw,relatime,discard,errors=remount-ro,commit=30`, 46167704 1K-blocks about 17 % used, 5707520 inodes (c136, c137); `/var/lib` is `root:root` `0755`, dev 2049, ino 97831, no xattr names (c105) | **recommended** by DR1; **decided** as D-1, created by CPP (§4.4) |

**No directory whose facts R5 collected satisfies every constraint as the
direct parent.** The recommendation therefore prefers the closest compatible
choice: a new dedicated directory on the one filesystem (`/` ext4) that R5
observed for every candidate and that PO-20 must already cite for `/var/lib`
and `/var/tmp` (HF-15 D3-R1 amendment). It introduces no new filesystem type.

The name avoids textual prefixes of the excluded subtrees.
`/var/lib/freedom-blades-capture`, for example, is not under
`/var/lib/freedom-blades` as a path, but a naive string-prefix check would
misclassify it.

### 4.2 The decided binding, as amendment text

**§4.1.5 *(R2)*, appended to the accepted constraints:**

> *(R2)* `⟨MI.capture_root_A⟩` is `/var/lib/rp11-capture/⟨activation_id⟩-pass-a`,
> with `⟨activation_id⟩` exactly the A-2 value of §4.2.5-R1 (a). Its full
> grammar is
> `^/var/lib/rp11-capture/rp11-act-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{8}-pass-a$`.
> Its parent `/var/lib/rp11-capture` is a directory, `ubuntu:ubuntu`, mode
> `0700`, without a POSIX ACL extended attribute, not a mount point, and on
> the filesystem that holds `/var/lib`. Only the provisioning act CPP creates
> the parent, under its own authority, after H-1 PASS and before the first
> A-2. No RP-11 slice, CL, RB-1 or cleanup removes, renames or writes inside
> the parent, except that X-1 creates exactly one capture root per pass in
> it. No `tmpfiles.d` line names the parent. The parent and root lie outside
> `/opt/freedom-blades/platform` and outside every RP-11 checkout, retained
> or fresh. Every exclusion is tested on path components, never by string
> prefix. `pass-a.json` carries the full capture-root path, and A-2 pins it.

A future `MI.capture_root_B` would use `-pass-b` under a different activation;
Pass B is outside M-11 and this proposal.

### 4.3 HF-15 *(R2)* — corrected observation semantics

**HF-15 *(R2)*, replacing the D3-R1 annotation and DR1's HF-15 (DR1):**

> HF-15 records, for the capture-root parent named by the assignment's fixed
> input (FI-1), the following, in order.
>
> 1. **Parent.** Python `os.lstat(P)` and `os.listxattr(P,
>    follow_symlinks=False)` for the literal `P` = `/var/lib/rp11-capture`.
>    The expected pre-CPP result of each is `FileNotFoundError` (`ENOENT`),
>    recorded as `absent`. If `P` exists, its type, owner, group, mode,
>    `(dev, ino)`, `nlink` and extended-attribute names are recorded without
>    following a symlink and without listing it.
> 2. **Nearest existing ancestor.** Determined only from the literal's own
>    path components, nearest first, by `os.lstat` of each — for this binding
>    the single candidate `/var/lib`. No directory is listed and no other
>    path is examined. For the decided binding, while `P` is absent, the
>    nearest existing ancestor must be exactly `/var/lib`, and it must be a
>    directory and not a symlink. Its type, owner, group, mode, `(dev, ino)`
>    and extended-attribute names are recorded.
> 3. **Ancestor filesystem facts.** `findmnt --target /var/lib -o
>    TARGET,SOURCE,FSTYPE,OPTIONS` and `df
>    --output=source,fstype,size,used,avail,pcent,itotal,iused,iavail,target
>    -- /var/lib`, in exactly R5's forms (c136, c137). **Neither command is
>    ever run against `P` while `P` is absent.**
> 4. **Labelling.** The record states that items 2 and 3 are facts of the
>    ancestor `/var/lib` and of the filesystem mounted at the reported
>    `TARGET`. They are **not** a stat of the parent, and they do not show
>    that a later-created parent will be on that filesystem. That proof is
>    CPP's postcondition (§4.4).
>
> A capture-root parent absent from the assignment's fixed inputs is a
> pre-execution `HARD STOP` (FI-2). It is never recorded as `not specified`.
> An `lstat` or `listxattr` error other than `ENOENT` on `P`, a missing or
> non-directory or symlinked `/var/lib`, or a non-zero exit of either command
> in item 3 is a `HARD STOP` of the collecting run (§11.5).

The rule for a later H-0 or H-0G with a different parent is the same: `findmnt`
and `df` run only on the recorded nearest existing ancestor, never on an
absent path.

### 4.4 CPP — capture-parent provisioning (D-1b), with the R2 pre- and postcondition

CPP is a one-time privileged act under its own authority, after H-1 PASS and
before the first A-2. Its design (DR1 §3.4 option (i)) is unchanged: exclusive
`mkdir` (never `-p`), `chown ubuntu:ubuntu`, `chmod 0700`, `fsync` of
`/var/lib`. CPP never removes, renames or repairs anything.

*(R2)* **CPP preflight (all before any mutation; any failure is `HARD STOP`
with nothing created):**

* E-1 (nodename and machine-id SHA-256 equal the composed H-0 values);
* `lstat /var/lib/rp11-capture` → `ENOENT`;
* `lstat /var/lib` → directory, not a symlink, with `(dev, ino)`, owner,
  group and mode equal to H-0G's G-15b record;
* `findmnt --target /var/lib` `TARGET`, `SOURCE`, `FSTYPE` and `OPTIONS` equal
  to H-0G's G-15c record.

*(R2)* **CPP postcondition (observed as root and then re-observed
unprivileged as `ubuntu`; any failure is `HARD STOP`, and the created object
is retained, unmodified, for Peter's decision):**

1. `lstat /var/lib/rp11-capture`: a directory, not a symlink, owner
   `ubuntu`, group `ubuntu`, mode `0700`, `nlink` `2`;
2. `listxattr` (no follow) returns no names — in particular neither
   `system.posix_acl_access` nor `system.posix_acl_default`;
3. **same filesystem:** its `st_dev` equals `lstat /var/lib`'s `st_dev`;
4. **not a mount point:** no `/proc/self/mountinfo` line has a mount-point
   field (after octal-escape decoding) equal to `/var/lib/rp11-capture`.
   Item 3 alone is insufficient, because a bind mount of the same filesystem
   would share `st_dev`; item 4 closes that case;
5. `findmnt --target /var/lib/rp11-capture -o TARGET,SOURCE,FSTYPE,OPTIONS`
   — valid now that the path exists — reports the same row as for `/var/lib`;
6. `df --output=… -- /var/lib/rp11-capture` reports the same `source`,
   `fstype` and `target` as for `/var/lib`.

CPP records the H-0G record digest it compared against, every result above,
and the parent's `(dev, ino)`, which AP-0 and later slices use as its
identity.

### 4.5 AP-0 *(R2)* additional conditions

AP-0 (unprivileged, as `ubuntu`) requires: the parent satisfies §4.1.5 *(R2)*
with `(dev, ino)` equal to CPP's record; `listxattr` returns no names; no
`/proc/self/mountinfo` mount point equals the parent; the capture root is
absent; and no `tmpfiles.d` line names the parent. AM-0 repeats the
capture-root absence check as root.

### 4.6 OH-S3 note

The operational draft's `MI.capture_root_A` and C-6/C-7 rows still say "on the
repository host" and "no file is created on `oracle-test`". The one-host
restatement belongs to OH-S3 (§4.7.4). OH-S3 receives the parent, the template,
CPP's identity record and the D-7 checkout model (§8) as inputs. This proposal
edits no draft text.

---

## 5. HF-18 and the interactive client (D-2)

### 5.1 Basis (carried from DR1 §4)

No specific interactive-client executable is load-bearing for any accepted
security property. The hook grammar C-3 is defense in depth and fixed in the
repository (C11 C-3, §4.4.6: the in-entry guarantee "is identical for Claude
and non-Claude operators"). Local-only topology rests on E-1 … E-3 and OH-D-2.
The only authorization decision is polkit's at TR-5 under the start-only rule,
CP (TR-6a) and A-2, reached only through kernel peer credentials (TR-4). LB-2S
begins at TR-6, and S-8/PO-14 make TR-0 … TR-4 irrelevant to the entry's state.
HF-18 is a readiness precondition of each slice that runs a client, observed at
that slice's time.

### 5.2 Amendment (decided D-2)

**§4.4.1 HF-18 *(R2)*:**

> *(R2)* HF-18 is withdrawn from H-0 and from H-0G. Every later assignment
> that runs an agent client on `oracle-test` names that client's exact
> executable path as a fixed input (FI-1). After E-1 and before any other act,
> its preflight records `lstat`, the real path, owner, group and mode of that
> exact path, and, if it is a symlink, of its resolved target. An absent path,
> a path missing from the assignment, a group- or world-writable object, or an
> unexpected type or owner is a `HARD STOP` before any act. It is never
> remedied by installing, updating, configuring or searching for a client, and
> no other path is examined. An assignment whose operator is a human shell user
> names no client and records the accepted no-hook case: C-3 is absent, as C11
> §4.4.6 allows.

R5's HF-18 `not specified` is superseded by the withdrawal and is not converted
into a pass. Nothing is inferred from the controller's installation or from the
agent-client bootstrap records (which name `/opt/freedom-blades/agent-tools`
on `oracle-test`); a client-running slice names and verifies its own path.

---

## 6. CPython 3.12 versus 3.14 (D-3, D-3b) — Route 1

### 6.1 Observed facts used (R5; not accepted by this proposal)

| Fact | R5 evidence |
|---|---|
| `/usr/bin/python3.12` absent: `stat` exit 1, `sha256sum` exit 1, invocation exit 127; `readlink -f` printing the path is not presence | c092–c095 |
| `python3.12`, `python3.12-minimal`, `libpython3.12-minimal`, `libpython3.12-stdlib` not installed; no `dpkg -S` owner of `/usr/bin/python3.12` | c054–c057, c063, c081–c084 |
| `apt-cache policy` printed **nothing** for `python3.12` or `libpython3.12-*` from the configured lists (only two unrelated `postgresql-plpython3-12*` entries matched the pattern) | c091; R5 unexpected fact 8 |
| `/usr/bin/python3` is a `root:root` `777` symlink resolving to `/usr/bin/python3.14` | c009, c010 |
| `/usr/bin/python3.14`: regular file, `root:root`, `755`, 7468968 bytes, SHA-256 `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` | c096, c097 |
| `/usr/bin/python3.14` owned by `python3.14-minimal` `3.14.4-1ubuntu0.2` (source `python3.14`); `/usr/bin/python3` owned by `python3-minimal` `3.14.3-0ubuntu2` (source `python3-defaults`); `dpkg --verify` silent for both | c068, c069, c071, c072, c089, c090 |
| `/usr/bin/python3 -I -S -c …`: `3.14.4 (main, Aug 20 2026, 10:41:58) [GCC 15.2.0]`, `isolated=1`, `no_site=1`, `executable=/usr/bin/python3`, `prefix=/usr`, `path=['/usr/lib/python314.zip', '/usr/lib/python3.14', '/usr/lib/python3.14/lib-dynload']` | c012 |
| `unattended-upgrades.service` active and enabled; `apt-daily*` timers enabled | c145, c146 |

**c012 invoked the symlink `/usr/bin/python3`, not `/usr/bin/python3.14`.**
Its `sys.executable` is the symlink path. An exact-path invocation of
`/usr/bin/python3.14` was never observed. The packages `python3.14`,
`libpython3.14-minimal` and `libpython3.14-stdlib` were never queried.

### 6.2 Inventory of affected references, by semantic role (carried unchanged from DR1 §5.2)

Method (DR1): `git grep -n -i -E 'python3\.12|python ?3\.12|cpython ?3\.12|libpython3\.12|py3\.?12|cp312'`
over all tracked files, plus the launcher listing's split byte string. DR1's
completeness check found 55 normative matches in the design, C11, D2,
`launch.c`, `rp11_launch.py` and the manifest, all cited. Every cited file's
digest is unchanged (§1), so the line numbers below are still exact. This
assignment re-ran the completeness check against this file (handback §5).

**Role A — executed literals: the program a process `execve`s, in an
installed, compiled or privileged artifact.**

| Location | Text | Route 1 replacement |
|---|---|---|
| `infra/rp11-launch/launch.c:207`, `:221` | `argv_out[0] = "/usr/bin/python3.12"`; `rp11_syscall3(RP11_SYS_EXECVE, (long)"/usr/bin/python3.12", …)` | `/usr/bin/python3.14` in both; then a rebuild (new image, listing, map and `launch.s` digests, `expected.sha256`) |
| `infra/rp11-launch/rp11-launch.x86_64.listing:412–413` | `.rodata` bytes `/usr/bin/python3` `.12` at `0x40067f` | regenerated by the rebuild, never hand-edited |
| launcher image `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | the compiled literal | superseded by a new reviewed digest. Every pin of `04218ed2…` (`rp11_launch.py`, `expected.sha256`, `tools/r5_runner/blocks/s08.sh`, design §4.2.4 P-0 and §4.5.2, IA-8) moves to the new value only through review |
| `tools/phase_5_0_evidence/rp11_launch.py:47`, `:49` | `EXECVE_PATH`, `EXECVE_ARGV[0]` | `/usr/bin/python3.14` |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json:2732`, `:2744`, `:2824`, `:2841` | `rp11_launch` contract `execve_argv`, `execve_path`, `execve.argv`, `execve.path` | `/usr/bin/python3.14`, in a new manifest version, with the new image digests |
| design §4.2.5-R4 (b) unit (`:2857`); also quoted at `:228`, `:2481`, `:2509`, `:5242` | `ExecStartPre=+/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume` | `ExecStartPre=+/usr/bin/python3.14 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_h1.py consume`. T-B1 admits exactly this line |
| design §4.2.4 (`:1257`) | `sudo -n /usr/bin/python3.12 -I -S -c '⟨verified-exec stub⟩' …` | `sudo -n /usr/bin/python3.14 -I -S -c '⟨verified-exec stub⟩' …` |
| design §4.2.5-R2 (e), (f), (i) (`:1996`, `:1997`, `:2016`, `:2147`) | holder `ExecStopPost=`, holder command, backstop command, attest command | each `/usr/bin/python3.12` → `/usr/bin/python3.14`; the (e)/(f) grammar tests apply unchanged |
| design §4.2.5-R4 (h) (`:3124`) | `ExecStartPre` normalization `path` and `argv[0]` | `/usr/bin/python3.14` |
| C11 §4.4.3.4 item 5 (`:688`, `:903`–`:904`); D2 OD-1 (`:436`), §5.8 (`:1256`, `:1258`, `:1567`, `:1568`) | the `rp11-launch/1` `execve` contract | `/usr/bin/python3.14`, as a dated amendment to each accepted text, not a rewrite |

**Role B — trust-path and proof-obligation statements naming the interpreter.**

| Location | Text | Route 1 treatment |
|---|---|---|
| design TR-9 (`:945`) | `/usr/bin/python3.12 -I -S` (dynamic); PO-12, PO-19 | `/usr/bin/python3.14 -I -S`; PO-12 and PO-19 **re-cited** for 3.14 (§6.6) |
| design §4.4.2 PO-19 (a) (`:4497`) | "when `/usr/bin/python3.12` is started with exactly …" | `/usr/bin/python3.14`; the whole of PO-19 is re-cited for the HF-07 `libc6` *and* the new executable's `DT_RUNPATH`/`DT_RPATH` |
| C11 PO-12 (`:2426`), AS-8 (`:456`) | "CPython 3.12 `-I -S <script>` reads no `PYTHON*` variable …" | "CPython 3.14, at the HF-07-recorded `python3.14-minimal` version, …"; **re-cited** from that version's documentation and `getpath` source |
| C11 M-5 (`:2404`); design §4.7.1 M-5 (`:5154`) | "the entry interpreter `/usr/bin/python3.12`" | `/usr/bin/python3.14` |
| C11 C-5 (`:514`), T5 (`:576`), interpreter lookup row (`:598`), (`:619`), (`:809`), (`:941`), (`:1748`); C11 (`:62`), (`:281`) | descriptive trust-path text | `/usr/bin/python3.14` in a dated C11 amendment note. Withdrawn LB-2 (R1) and LB-3 rows (`:226`, `:798`, `:1019`, `:2529`, `:2533`) stay **as history**, unchanged |
| U-9 decision (prerequisite decisions `:24`) | "trusted loader inputs relevant to `/usr/bin/python3.12`" | a Peter-recorded restatement naming `/usr/bin/python3.14`. U-9 is a decision and is not edited silently |

**Role C — H-0 fact definitions and command classes.**

| Location | Route 1 replacement |
|---|---|
| HF-06 (`:4436`) | unchanged wording ("CPython version"); the observed value becomes 3.14.4 |
| HF-07 (`:4437`) | packages `python3.14`, `python3.14-minimal`, `libpython3.14-minimal`, `libpython3.14-stdlib` replace the four `3.12` names; `dpkg -S /usr/bin/python3.14` replaces `dpkg -S /usr/bin/python3.12` |
| HF-08 (`:4438`) | `/usr/bin/python3.14`: owner, mode, real path, SHA-256; `/usr/bin/python3.14 -I -S -c` printing `sys.version`, `sys.flags.isolated`, `sys.flags.no_site`, `sys.executable`, `sys.prefix`, `sys.path` |
| HF-10 (`:4440`) | `/usr/bin/python3.14` replaces `/usr/bin/python3.12` |
| C-VER (`:4472`) | `/usr/bin/python3.14 -I -S -c` with a fixed literal |

**Role D — standard-library capability claims that RP-11 code running under
the system interpreter relies on.**

| Location | Claim | Treatment |
|---|---|---|
| design §4.2.4-R1 PT-8 (`:1437`) | "glibc's `renameat2` … through standard-library `ctypes` (Python 3.12 has no wrapper)" | becomes an **OH-S2 citation item** for 3.14: does `os` expose `renameat2`/`RENAME_NOREPLACE`? The `ctypes` mechanism stays until the citation is accepted. No claim about 3.14 is made here |
| the bootstrap, the capture mechanism (`capture_contract.py`, `execution/capture_mechanism.py`, `execution/capture_store.py`) and the future `rp11_h1.py` | no version literal, but they run under TR-9's interpreter | OH-S4 must run their tests under the target interpreter version (§6.5, reproducibility) |

**Role E — verification and test artifacts derived from Role A.**
`tests/test_rp11_launch_source.py` (`:129`, `:134`, `:336`) and
`infra/rp11-launch/verify/ctverify.py` (`:796`) read the constants or the
manifest contract and need no literal edit, but their expected values change
with Role A. D2's test methods (`:1525`, `:2207`) and the I-7 handback's
decoded `execve` record (`:224`) are D9 evidence for the **old** image. They
remain history and are superseded by re-run evidence for the new image.

**Role F — development, test and Pass A act runtimes (not the installed
contract; unaffected).**

* `venv-web` CPython 3.12.14 (`disposable-test-server.md:44`, `:108`; operational
  draft `PIN.interpreter` `:342`; `tools/phase_5_0_evidence/case_runtime.py:111`).
  This interpreter runs the test suites and the Pass A acts A1-S1 and A1-13.
  It is uv-managed under `ubuntu`'s home (`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-handback.md`,
  lines 589 and 665), so it cannot be the root-owned M-5 entry interpreter. It is not a
  route (§6.3). It is unaffected, and H-0 does not observe it.
* Local controller CPython 3.12.3 records: the I-7 handbacks (`:178`, `:345`,
  `:356`), the IC1 handback (`:244`, `:274`, `:362`), `change-log.md:4521`,
  `:4631`, and reviews of 2026-09-28.
* Production deployment Python 3.12 (`docs/adr/0002-web-application-stack.md:19`,
  `:36`; `.agents/AGENTS.md` coding standards); `phase-5-0-package-plan.md`
  (`:1508`, `:5647`, `:5648`); `decision-register.md:58`; `change-log.md:128`
  (C-P5.0-AH).
* Evidence-harness and laboratory statements (`execution/descriptors.py:74`,
  `:157`, `:253`; `execution/case_program.py:839`;
  `tests/phase_5_0_evidence/test_no_execution.py:326`;
  `decision-register.md:1498`; `phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md:24`,
  `:33`; `phase-5-0-p5-r5-rp11-capture-mechanism-implementation-handback.md:35`,
  `:342`). These describe the harness runtime. If any of them is later relied
  on for code that runs under TR-9's interpreter, it joins Role D.
* The synthetic lab constant `REVIEWED_INTERPRETER_REAL_PATH = "/opt/fb-reviewed/python3.12"`
  in ten test files, and `test_executor.py:400`, `:405`,
  `test_expectations.py:270`, `:822`. These are test fixtures for the reserved
  laboratory runner contract (r2–r6) and are unrelated to RP-11.

**Role G — current-state records describing the mismatch.**
`implementation-plan.md:2566`, `status.md:17`, `Handover information` and
`change-log.md:8`. These are descriptive and are updated only as pointers.

**Role H — historical or consumed evidence; never edited.** The R3–R5 prompts,
authorities, handbacks and reviews; the design's §0-R4 summary (`:228`) and
§16 check row 8 (`:6979`), as revision history; the preparation handback
(`:185`, `:188`, `:283`); the 2026-09-29 C11 review (`:35`); and the
`*-through-*` snapshots.

**No blanket replacement is proposed.** Role A and C texts get exact
replacements. Role B texts get replacements **plus** re-citation. Role D texts
become citation or test items. Roles E–H are unchanged.

### 6.3 Routes (record)

DR1 §5.3 compared Route 1 (exact `/usr/bin/python3.14`), Route 2 (a separately
authorized Python 3.12, with no candidate in the configured lists, c091) and
Route 3 (abandon the Python-dependent route). Unversioned `/usr/bin/python3`, a
`python3.12` symlink or copy to 3.14, and `venv-web`'s uv-managed 3.12.14 were
rejected as non-routes (DR1 §5.4). **Peter decided Route 1 (D-3).** Route 3
remains the destination only if OH-S2 refutes PO-12 or PO-19 for 3.14.

### 6.4 Why textual replacement discharges nothing

Changing `3.12` to `3.14` discharges no obligation. PO-12, AS-8, PO-19, the
PT-8 capability claim, PO-17 against the new image, and D9-1 … D9-4 are all
version- or image-bound. Each returns to OH-S2 citation or I-7-style evidence
and then to independent review. Until then every Role A replacement is an
unexecuted proposal.

### 6.5 Route 1 consequences (preserved from DR1 §5.5, each under its own authority)

1. **OH-S2 (amended).** Re-cite PO-12 and AS-8 for CPython 3.14 at the accepted
   `python3.14-minimal` version, and PO-19 for the accepted `libc6` **and**
   `/usr/bin/python3.14`'s dynamic section (`DT_RUNPATH`/`DT_RPATH`). Add the
   PT-8 `renameat2` question. Re-run PO-17 (§4.3.6) against the new launcher
   image. A refuted PO-12 or PO-19 sends the design to Route 3 review.
2. **OH-S4p: interpreter retarget, repository only.** Apply the Role A and C
   replacements to `launch.c`, `rp11_launch.py`, the manifest (a new version),
   tests and design texts. Rebuild the launcher deterministically. Record the
   new image, listing, map and `launch.s` digests. Re-run D9-1, D9-2 and D9-4
   evidence, then an independent rebuild for D9-3. OH-S5 on `oracle-test`
   inherits the new digest. Every pin of image `04218ed2…2668572` moves only
   through review.
3. **Tests under the target version.** OH-S4's RP-11 code tests (bootstrap,
   capture mechanism, `rp11_h1.py`) run under CPython 3.14 as well as the
   suite interpreter. Without a 3.14 test interpreter the handback states the
   gap. *(R2, D-7)* A 3.14 test run on `oracle-test` reads repository bytes
   there and is therefore a source-consuming slice (§8.3).
4. **U-9 restated** by Peter for `/usr/bin/python3.14`. U-9 is a decision and is
   not edited silently.
5. **H-0G** observes the 3.14 facts R5 lacks (§11).

### 6.6 Version-bound obligations that return to review

| Obligation | Bound to | Returns to |
|---|---|---|
| PO-12 / AS-8 | CPython version and `getpath` | OH-S2 |
| PO-19 (a)–(d) | `libc6` version and the interpreter's dynamic section | OH-S2 |
| PT-8 capability | CPython 3.14 `os` API | OH-S2 |
| PO-17 | launcher image bytes and HF-14 entries (R5 recorded a `python3.14` `binfmt_misc` entry, magic `2b0e0d0a`, interpreter `/usr/bin/python3.14`) | OH-S4p / H-1 P-0 |
| D9-1 … D9-4 | launcher image | OH-S4p, OH-S5 |
| §4.3.3 baseline `ExecStartPre` | unit text | PO-15 in OH-S2 |
| HF-07, HF-08, HF-10 values | observed host | H-0G |

### 6.7 Drift control (decided D-3b)

* H-1 P-0 already requires re-observed HF-04 … HF-10 versions equal to H-0's.
  *(R2)* H-2 and AP-0 also require the `python3.14-minimal` version and the
  `/usr/bin/python3.14` SHA-256 to equal the values the accepted PO-12/PO-19
  citations name. Any difference is INVALID RUN, followed by re-citation. It
  is never accepted at run time.
* A package hold or disabling `unattended-upgrades` is **not** a substitute for
  these gates and is **not authorized**. It may be considered later only under
  its own authority.

---

## 7. The Polkit unknown and PO-21 (i) (D-4, D-5)

### 7.1 Polkit collision (decided D-4)

R5's result stands: `/etc/polkit-1/rules.d` is `root:polkitd` `0750` (gid 983,
ino 1625) and unreadable to `ubuntu`; whether
`50-freedom-blades-rp11.rules` exists there is **unknown** (`PermissionError
errno=13`, c105–c107). Nothing infers absence.

The accepted H-1 P-0 ("preflight, read-only, unprivileged … every §4.2.3 path
**absent**") and `ACT` AP-0 ("executor, unprivileged … the rule basename absent
from every PO-11 (f) directory") cannot establish that absence, because
`ubuntu` is not in `polkitd` (HF-03). An implementation that maps `EACCES` to
absent would silently pass.

> **P-0p *(R2)*, H-1, privileged and read-only, after P-0 and before M-0.**
> Through the H-1 tool's verified-exec stub under `sudo -n`, `lstat` exactly
> `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules`, and for every other
> rules directory that the accepted PO-11 (f)(i) citation lists,
> `⟨dir⟩/50-freedom-blades-rp11.rules`. Each result must be `ENOENT`. Any
> other result, including `EACCES` or a present object of any type, is
> **INVALID RUN** with nothing mutated, and it returns to Peter. The object is
> never removed, renamed or read beyond `lstat`. P-0's unprivileged form
> records `/etc/polkit-1/rules.d` as `unreadable` and defers the basename to
> P-0p. **`unreadable` is never reported as absent.**

> **AP-0 *(R2)*.** For a rules directory that `ubuntu` cannot read, AP-0
> records `unreadable` and does not pass that condition by itself. **AM-0
> *(R2)*** performs the same `lstat` set as root and requires `ENOENT` for
> each before AK-1. Otherwise the holder exits non-zero before any activation
> file exists, and CL follows (stop-post).

HF-11 and HF-12 are **not** extended with privilege; H-0 and H-0G stay
unprivileged.

*(R3)* R2 left P-0p's compatibility with the accepted role text open as a
review question. R3 resolves it with an exact amendment. The accepted §4.1.1
H-1 row reads "Root through `ubuntu`'s `sudo -n` for the mutation steps only
(§4.2.4)". **§4.1.1 H-1 row *(R3)*:** "Root through `ubuntu`'s `sudo -n` for
P-0p's read-only `lstat` set and for the mutation steps only (§4.2.4). P-0p
creates, opens for writing, removes and renames nothing." No other privilege
is added.

### 7.2 PO-21 (i) (decided D-5)

No accepted local source enumerates PO-21 (i)'s condition paths. Only its
OH-S2 citation (under U-10) can.

> **HF-20 *(R2)*** is split. **HF-20a**, the `LoadState` of
> `systemd-soft-reboot.service` and `soft-reboot.target`, remains an H-0 fact
> (R5 c151). **HF-20b**, the presence of each PO-21 (i) condition path, leaves
> H-0.
>
> **CL-21i**, a required OH-S2 result: PO-21 (i)'s accepted citation states a
> closed list of condition paths and any non-path conditions for the HF-07
> systemd version. For each it gives the exact absolute path, the predicate
> (present, absent, or a named content property), whether `ubuntu` can observe
> it unprivileged, and how it is disarmed. If the version cannot soft-reboot
> automatically, the citation says so and CL-21i is the empty list, which is
> then an accepted result and not an omission.
>
> **AP-0 *(R2)*** evaluates every CL-21i condition that `ubuntu` can observe,
> and **AM-0 *(R2)*** evaluates every condition as root. A condition that is
> present, armed or unobservable is INVALID RUN. A CL-21i entry that cannot be
> disarmed returns the design to review (DF-1).
>
> **Fail-closed.** Until CL-21i is accepted, no record may report HF-20b, or
> any PO-21 (i) host check, as observed or successful, and AP-0 and AM-0
> cannot pass, so no grant can be linked.

---

## 8. D-7 — repository source on `oracle-test`

### 8.1 Three objects, never conflated

| Object | Path | What it is | What it may be used for | What it may never be |
|---|---|---|---|---|
| **W — the normal Test workspace** | `/opt/freedom-blades/platform` on `oracle-test` | the ordinary disposable-server workspace (disposable-test-server.md §1, §3). Its current state is **uncontrolled**: R3 observed tracked and untracked changes (c017 of R3) | today: nothing; it is preserved untouched until a later cleanup authority (§12). After accepted recreation (§12.5): ordinary disposable-server testing | an RP-11 evidence or execution source, while uncontrolled **and** after recreation, wherever independent pinned provenance is required; inspected, read, `stat`ed, repaired or cleaned by any RP-11 slice, H-0G or this proposal |
| **F — a fresh run-specific pinned RP-11 checkout** | an exact path fixed by the consuming slice's authority, of the accepted form `/var/tmp/⟨RUN⟩-checkout` (R5; §4.5.2's `/var/tmp/⟨BRUN⟩-checkout`), absent before that slice | an exclusive, anonymously retrieved checkout at the accepted commit, created for exactly one source-consuming slice (or one activation chain, §8.3) | the only repository-byte source for that slice, after CK-0 … CK-11 pass, and only through the source-consumption contract SC-1 … SC-8 *(R3)* (§8.6) | reused by any other slice; written by anything except its creating retrieval; a fallback for W |
| **R — a retained checkout or evidence path** | e.g. `/var/tmp/p5-r5-rp11-h0-20261006-02-checkout` and every other path recorded by a consumed run | immutable evidence of a consumed run | citation from its durable repository record only | an execution input, a source, a comparison baseline, or a target of inspection, reuse, repair or cleanup without its own exact-path authority (§12) |

**R5 did not observe checkout ownership.** R5's `INVENTORY.owner-mode` covers
its **evidence** directory only (623 file rows, all `ubuntu:ubuntu` `0600`),
and its handback states "Repository ownership is not observed" (HF-03 row,
HF-NOTES). R5's Git records show retrieval under `umask 077` by `ubuntu` and a
clean detached tree (c015–c025), but no owner or mode of any checkout file was
recorded, and **no listing of its `.git` directory was recorded**.
**Ownership is not inferred from the fact that `ubuntu` created the
checkout.** CK-3 observes it.

*(R3)* Every F and every retained checkout of the pinned commit contains the
tracked symlink `venv` (§8.6.1). A retained checkout is never inspected under
this proposal; any later exact-path cleanup of one removes the link itself and
never follows it (§12.4 item 5).

### 8.2 The fresh-checkout contract

**Retrieval (CR), reusing R5's accepted controls exactly.** A
source-consuming slice (or a separately authorized retrieval step bound to it)
creates F exactly as R5 created its isolated checkout (R5 c013 … c020):

* **CR-1** freshness: `lstat` (or `test -e` and `test -L`) of the exact literal
  path only, never a listing of its parent; present → `HARD STOP`. The path
  must not equal, contain or lie under W, any R path, the capture-root parent
  or any §4.2.3 path (component-wise), and its name must not collide with a
  recorded R prefix;
* **CR-2** environment: every Git command is `/usr/bin/git`, run under exactly
  `env -i HOME=/nonexistent LC_ALL=C PATH=/usr/bin:/bin GIT_CONFIG_NOSYSTEM=1
  GIT_CONFIG_GLOBAL=/dev/null GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/false
  SSH_ASKPASS=/bin/false GIT_SSH_COMMAND=/bin/false GIT_ALLOW_PROTOCOL=https
  GIT_NO_REPLACE_OBJECTS=1`, under `umask 077` (R5 c014–c025). No other
  variable is present; in particular none of `GIT_DIR`, `GIT_WORK_TREE`,
  `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`,
  `GIT_INDEX_FILE`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT`,
  `GIT_EXEC_PATH`, `GIT_TEMPLATE_DIR`, `GIT_CEILING_DIRECTORIES` or
  `GIT_DISCOVERY_ACROSS_FILESYSTEM` (CK-9 L-1);
* **CR-3 *(R3)*** every Git invocation carries exactly R5's options: `-c
  credential.helper= -c credential.interactive=never -c
  core.askPass=/bin/false -c core.hooksPath=/dev/null -c core.fsmonitor=false
  -c maintenance.auto=false -c gc.auto=0 -c fetch.recurseSubmodules=false -c
  submodule.recurse=false -c protocol.allow=never -c protocol.https.allow=always
  -c http.followRedirects=false -c fetch.writeCommitGraph=false -c
  advice.detachedHead=false`, and `init` additionally carries `-c
  init.defaultBranch=h0-unborn` (R5 c015 … c025). The unborn branch name never
  becomes a ref: no commit is made, and CK-9 G-9/G-10 admit no file under
  `refs/`;
* **CR-4 *(R3)*** in order: `git … init --quiet --template= -- ⟨F⟩`;
  `/usr/bin/timeout 900 /usr/bin/git -C ⟨F⟩ … fetch --no-tags --depth=1
  --no-recurse-submodules -- https://github.com/ming-themerciless/freedom-platform.git
  ⟨commit⟩`; `cat-file -t ⟨commit⟩` = `commit`; `rev-parse --verify
  --end-of-options ⟨commit⟩^{commit}` = the pin; `cat-file -p ⟨commit⟩`
  recorded (its `tree` line is part of the evidence); `checkout --detach
  ⟨commit⟩` (R5 c015 … c020). Authentication, a redirect, a missing pin, a
  timeout or any credential/helper need is `HARD STOP`.

**Pre-use inventory (CK), run with CR-2/CR-3 in force, after retrieval and
immediately before the slice's first consumption of repository bytes.** Every
failure is `HARD STOP` before use; nothing is repaired, re-fetched, followed
or cleaned. Every filesystem observation in CK is made with `lstat`,
`readlink` of the link text, or a no-follow descriptor (§8.6.3); no CK step
dereferences a symlink.

| # | Check | Rejects |
|---|---|---|
| CK-0 | the path is byte-equal to the authority's fixed input; the work ID and authority digest are those of the consuming slice | substitution of path or authority |
| CK-1 | `lstat` of the checkout root: a directory, **not a symlink**, owner and group equal to HF-03's `ubuntu` UID/GID, mode `0700`; every ancestor component up to and including `/var/tmp` is a non-symlink directory | symlink substitution at the root; unexpected owner/group |
| CK-2 | the root's `(dev, ino)` equals the value recorded at its creation (CR-4) and is re-checked at every later authority boundary within the slice | replacement between creation and use |
| CK-3 *(R3)* | bounded no-follow inventory of the root and everything under it (worktree and `.git`), by `lstat` through directory descriptors, never following or descending into a symlink, never crossing to another `st_dev` (a directory on another device is a mount inside F and stops the check), with the entry count recorded. (a) Types: regular file, directory or symlink only. (b) Every entry's UID and GID equal HF-03's `ubuntu`. (c) Regular files and directories: not group- or world-writable; no set-user-ID, set-group-ID or sticky bit; every regular file has `nlink` `1`. (d) Symlinks: none under `.git`; in the worktree, the set of symlink paths equals **exactly** the set of mode-`120000` paths in the pinned tree, and each symlink's link text, read with `readlink` (no follow), is byte-equal to its pinned blob's bytes. A symlink's permission bits are not evaluated: Linux reports `0777` for every symlink and never uses them for access. (e) Each symlink is classified lexically (§8.6.2) and recorded with its class; every symlink is **non-consumable** (SC-3), and absolute or lexically escaping ones are recorded as **checkout-escaping** | group/world-writable files or directories; foreign owner or group; device, FIFO or socket nodes; set-ID or sticky bits; hard-linked files; a mount inside F; an extra, missing or retyped symlink; link text that differs from the pinned blob; any symlink under `.git`. **CK-3 does not by itself prevent a later dereference; SC-1 … SC-8 do (§8.6)** |
| CK-4 | `rev-parse HEAD` = the pinned commit; `symbolic-ref -q HEAD` exits `1` (detached); `status --porcelain=v1 --untracked-files=all --ignored` prints nothing | dirty, untracked or ignored content (for example a planted `__pycache__`); commit mismatch; an attached branch |
| CK-5 | `remote -v` prints nothing; `config --local --list` is **exactly** the four keys R5 recorded (c025): `core.repositoryformatversion=0`, `core.filemode=true`, `core.bare=false`, `core.logallrefupdates=true` | remotes; `credential.*`, `url.*.insteadOf`, `http.*`, `core.sshCommand`, `core.hooksPath`, `core.fsmonitor`, `core.worktree`, `core.symlinks`, `include*`, `filter.*`, `submodule.*`, `extensions.*` and every other key (CK-9 GX-8) |
| CK-6 | `.git/hooks` absent or an empty directory (CK-9 G-14) | active hooks |
| CK-7 *(R3)* | the pinned tree (`ls-tree -r -z --full-tree ⟨commit⟩`) has no mode-`160000` entry, no `.gitmodules` path and no `.gitattributes` path at any depth; `.git/modules` absent (CK-9 GX-7) | submodule recursion or state; attribute-driven conversion of checkout bytes |
| CK-8 *(R3)* | `.git/shallow` is exactly the pinned commit followed by one LF (CK-9 G-4); no replace ref, graft or alternate exists (CK-9 G-7, G-9, G-10, GX-3 … GX-5) | replacement objects; grafts; borrowed object stores; a different shallow boundary |
| CK-9 *(R3)* | the `.git` structural contract of §8.5: `.git` is a non-symlink directory at the root; every path under it matches exactly one row G-1 … G-14 and satisfies that row's constraint; every required row is present; Git's self-location checks L-1 … L-5 hold | worktree or common-directory indirection; object borrowing; replace refs; grafts; hooks; submodule state; alternative reference or object back-ends; interrupted or in-progress operation state; template residue; **any unlisted entry** (GX-1 … GX-12 name the mechanisms) |
| CK-10 *(R3)* | for each applicable accepted governing file and each path in the slice's covered-source list CS (SC-1): the path passes SC-2's lexical check against CK-3's symlink set, and the SHA-256 of the bytes read through the no-follow walk NFW (§8.6.3) equals the authority's pinned value. `sha256sum`, `cat`, `stat -L` or any other reader that follows symlinks is never used on a path in F for this check (this replaces R2's "R5 c026 pattern") | wrong or altered bytes; a symlink at the leaf or in any component; a hard-linked, writable or foreign-owned source |
| CK-11 *(R3)* | the slice records the checkout path, `(dev, ino)`, every CK result, the CK-3 symlink set with each link-text SHA-256 and class, the CK-9 inventory (§8.5.4) and its SHA-256, CS and its SHA-256, and its retention disposition (§12.6) in its evidence | an unrecorded or unreviewable source |

CK-3 and CK-9 are **additions** to R5's controls; CK-4's `--ignored` is a
**strengthening** of R5's c022; CK-7's `.gitattributes` and `.gitmodules`
prohibitions and CK-8's "absent" in place of R2's "absent or empty" are
**strengthenings** of R2. Nothing in CR or CK is weaker than R5 or R2.

**After use.** F becomes an R path: immutable evidence, never reused, removed
only under a later exact-path cleanup authority (§12).

### 8.3 Slice matrix *(R3: consumer column added)*

"Class" is SC-5's consumer class (§8.6.4): **B** reads bytes itself through
NFW; **T** is a tool whose own opens are not NFW-confined and is admissible
only under T-1 … T-6.

| Slice | Reads repository bytes on `oracle-test`? | Consumers and class | Checkout | Work ID / authority | Freshness check | Retention record | Cleanup disposition |
|---|---|---|---|---|---|---|---|
| **H-0G** | **no.** Repository-free; touches no repository path, not even `stat` | none | none | its own | its evidence path only (CR-1 form) | its evidence directory | exact-path, after its review and composition (§12.7) |
| OH-S2 (citations) | no; controller repository documentation and upstream source under U-10 | none on Test | none on Test | its own | — | — | — |
| OH-S3 (operational draft) | no; documentation | none on Test | none on Test | its own | — | — | — |
| OH-S4, OH-S4p (repository implementation; retarget) | no on the controller. **A 3.14 test run on `oracle-test` is a separate source-consuming slice** | if run on Test: pytest under `/usr/bin/python3.14` (**T**); CK helper (**B**) | if run on Test: its own F | separate | CR-1 | F + its evidence | exact-path, after its review |
| OH-S5 (launcher rebuild, §4.5) | **yes** | `provision.py`, `enter.py build`, `build.sh` under the fixed host interpreter (**T**); CK helper (**B**) | its own F: `/var/tmp/⟨BRUN⟩-checkout` (already the accepted shape), now also under CK and SC | its own | CR-1 | F + `/var/tmp/⟨BRUN⟩-*` | as §4.5.3: after H-1 is accepted |
| OH-S8 (H-1, including P-0p) | **yes**: installs the bootstrap, unit, staged rule and `rp11_h1.py` from repository bytes | H-1 tool's reads of the bytes it installs (**B**); CK helper (**B**) | its own F | its own | CR-1 | F + `-h1-evidence` | exact-path, after H-1 acceptance |
| CPP | no; repository-free | none | none | its own | its evidence path | CPP record | the parent is **never** cleanup-eligible except by Peter's explicit decision after every root under it is dispositioned (K-13) |
| OH-S8b (fault drill) | yes if it reads repository bytes (test `pass-a.json`, test A-2) | as for H-2/`ACT` below, per what it reads | its own F | its own | CR-1 | F + drill evidence | exact-path, after its review |
| H-2 → A-2 → `ACT` → Pass A → `DEACT`/CL (one activation chain) | **yes**: H-2 recomputes `baseline.repository`; `ACT` reads A-2's file "from the verified repository tree"; TR-2's catalogue and hook files; TR-10's covered sources; A0-02; A1-S1/A1-S2 working directory | H-2 recompute (**B**); `ACT` A-2 read (**B**); TR-10 bootstrap (**B**); TR-2 client hooks (**T**); A0-02 Git (**T**); A1-S1 harness dry run (**T**); A1-S2 digests (**B**, after OH-S3 restatement) | **one** F per activation chain, created before H-2 under the chain's first authority and pinned by path and `(dev, ino)` in A-2 and `pass-a.json` (note below) | the chain's authorities | CR-1 | F + act/deact evidence + capture root | F exact-path after the pass's records are accepted (§12.7); the capture root is never cleanup-eligible under this policy (K-13) |
| OH-S10 (RB-1 / RS-1) | no; uses installed tool and records | none | none | its own | — | its evidence | exact-path |
| ordinary disposable-server testing (non-RP-11) | yes | outside RP-11 | recreated W (§12.5) | its own | — | — | — |

Every row that reads repository bytes is bound to CK-10 (no-symlink-component
and digest check through NFW) before use and to SC-1 … SC-8 at use; §8.6.5
traces each consumer.

*(R3)* **One checkout per activation chain.** "A retained checkout is never
reused" applies between slices and chains. Within one chain, F is that
chain's own checkout from creation before H-2 until the chain's last act. It
is pinned by path, `(dev, ino)`, CK record digest and `covered_sources_sha256`
in A-2 and `pass-a.json`, and is re-checked (CK-1, CK-2, CK-4 and CK-3's
symlink-set comparison) at every authority boundary of the chain. It becomes
an R path only when the chain ends and is never used by another chain. H-2
and `ACT` therefore share one F and do not use separate checkouts.

### 8.4 Normative amendments for D-7

**HF-03 *(R2)*:** "`ubuntu`: UID, primary GID, supplementary groups; home
directory and shell path from the password database." The repository-ownership
element is **withdrawn from H-0**. Repository ownership becomes CK-1/CK-3 of
each source-consuming slice.

**U-3 binding *(R2)*,** replacing its third sentence: "H-0 re-observes the
account's UID, primary GID and supplementary groups. Each source-consuming
slice observes its own checkout's ownership (CK-1, CK-3)."

**IA-12 *(R2)*,** replacing the disposition: "`oracle-test:/opt/freedom-blades/platform`
is the normal Test workspace. It is not an RP-11 evidence or execution source
while its state is uncontrolled, and is never substituted for a fresh pinned
checkout where independent pinned provenance is required. Each
source-consuming slice uses its own fresh checkout (§8.2), and the bootstrap
verifies every covered source against the root-owned pinned digest (C11 C-6)."
*(R3)* appended: "Every consumption of repository bytes from that checkout
follows SC-1 … SC-8: no symlink component, a verified regular file, and no
dereference of the tracked `venv` symlink or any other symlink."
**Restated:** §4.1.4, §4.5.

**§4.1.4 *(R2)*,** replacing the D3-R1 introductory paragraph: "Repository
bytes reach `oracle-test` only by direct anonymous retrieval of the pinned
commit from the canonical public remote, run on `oracle-test`, into a fresh
run-specific checkout created for exactly one source-consuming slice or
activation chain (§8.2 CR). The checkout passes CK-0 … CK-11 before first use.
`/opt/freedom-blades/platform` is never an RP-11 source. The workspace host is
never a source, controller or relay. Nothing in that transport is trusted:"
followed by the existing items 1–4, with "A0-02's `git rev-parse HEAD` and
empty `git status --porcelain=v1` run locally" now run on the activation
chain's F, and item 4 read as "No retrieval runs while ST-2 holds or a pass is
running." *(R3)* Items 1–3 additionally read "… through the no-follow walk
NFW, never through a symlink component (SC-2, SC-4)"; item 2's "file by file
against digests pinned in its assignment" is CK-10 *(R3)*.

**§4.1.5 *(R2)*:** the first exclusion bullet reads "lie outside
`/opt/freedom-blades/platform` and outside every RP-11 checkout, fresh or
retained, …" (also §4.2 above).

**TR-2 *(R2, R3)*:** "the catalogue file in `/opt/freedom-blades/platform`"
becomes "the catalogue file in the activation chain's checkout named in
`pass-a.json`". *(R3)* The catalogue, `.claude/settings.json` and every hook
file the client reads are in the chain's CS, none has a symlink component, and
the client is a Class T consumer (T-1 … T-6). TR-2 remains defense in depth
only; nothing in this amendment makes it trusted.

**TR-10 *(R2, R3)*:** "every covered source under `/opt/freedom-blades/platform`"
becomes "every covered source under the activation chain's checkout named in
`pass-a.json`". *(R3)* The bootstrap opens each covered source and each hook
file through NFW (§8.6.3) relative to that checkout's root, whose `(dev, ino)`
`pass-a.json` pins, and reads it once from that descriptor. An `ELOOP` or
`ENOTDIR`, a non-regular file, `nlink` ≠ 1, a foreign owner or a group- or
world-writable mode refuses before X-1 with a new diagnostic
`entry-source-not-verifiable`, in the same failure class as C11's
`manifest-digest-mismatch` (C11 `:1460`). C-6's digest comparison and its
import finder, which serves only the verified in-memory bytes, are unchanged.

**§4.3.2 `baseline.operator` *(R2, R3)*:** `repository_root` is removed from
`baseline`, because H-1 and the activation chain use different fresh checkouts
and H-2 requires byte-equality of `baseline`. The H-1 record instead carries,
outside `baseline`, `source_checkout` = `{path, dev, ino, owner, group, mode,
ck_record_sha256}` for H-1's own F. *(R3)* `source_checkout` also carries
`covered_sources_sha256` (the SHA-256 of the CS list with its digests),
`ck9_inventory_sha256`, and `nonconsumable_symlinks`, a sorted list of
`[path, link_text_sha256, class]` from CK-3 (for the pinned commit exactly
`[["venv", "7e566c75a8237ea1f6762242355a1bac4d5baee9253161287ea2a34ba356ef08", "absolute"]]`, the SHA-256 of the 36-byte link text).
`baseline.repository` (commit, manifest version, digests) stays inside
`baseline` and remains the binding. H-2 records its chain's `source_checkout`
the same way, outside `baseline`.

**H-1 *(R3)*,** §4.2.4: the H-1 tool reads every repository file it installs
(the bootstrap, the unit, the staged rule and `rp11_h1.py`) through NFW from
H-1's F, verifies the in-memory bytes against their pinned SHA-256 and
publishes **those bytes**, as §4.2.4 already requires for the launcher image.
No installation source is read through a symlink or by a following opener.

**H-2 *(R3)*:** H-2's recomputation of `baseline.repository` reads the
manifest, `expected.sha256` and every other repository input through NFW from
the chain's F.

**A-2 *(R2, R3)*,** §4.2.5-R1 (b), adds: the activation chain's checkout path,
its `(dev, ino)`, its CK record digest and *(R3)* its `covered_sources_sha256`
and the repository-relative path of A-2's own file, which must pass SC-2.
`ACT` reads A-2's file from that checkout after re-running CK-1, CK-2 and CK-4
*(R3)* and CK-3's symlink-set comparison, **through NFW**, and requires the
SHA-256 of the bytes so read to equal A-2's SHA-256 argument. A symlink at
any component of that path is `HARD STOP` before AP-0's first act.

**A0-02 *(R3)*,** operational draft (restated in OH-S3): `git rev-parse HEAD`
and `git status --porcelain=v1` run on the chain's F under CR-2/CR-3, as Class
T consumers. Git records and compares symlink link text and does not follow
worktree symlinks for tracked content; with CK-5's exact key set
`core.symlinks` is unset and therefore takes Git's default on a
symlink-capable filesystem. A0-02 is preceded by CK-3's symlink-set
comparison.

**§4.6.2 "Never touched by any procedure" *(R2)*:** adds "every RP-11 checkout,
fresh or retained".

**Operational-draft restatement (OH-S3 scope) *(R2, R3)*:** A0-02 runs on the
activation chain's F; A1-S1/A1-S2's working directory is that F; the draft's
§5 `rsync --delete` synchronization and its "synchronized worktree" sentences
(A1-Z) are withdrawn for RP-11 and replaced by CR/CK. *(R3)* A1-S2's
`sha256sum` of five harness files is replaced by NFW hashing (CK-10 form),
because `sha256sum` follows symlinks. A1-S1 runs
`/opt/freedom-blades/runtime/venv-web/bin/python` by its fixed host path, with
`PYTHONDONTWRITEBYTECODE=1` (already in A1-S1), as a Class T consumer under
T-1 … T-6, and its T-4 review covers the fact that `-m` places F's root on
`sys.path`. OH-S3 performs this restatement; this proposal edits no draft
text.

### 8.5 CK-9 *(R3)* — the `.git` structural contract

#### 8.5.1 Choice of form, and why

The R3 prompt allows (1) a complete exact allowlist derived from durable
accepted evidence of the same procedure, or (2) a bounded structural
inventory plus explicit rejection of every Git mechanism that can redirect,
replace, execute, import or borrow state. **Form (2) is chosen.** No durable
accepted record lists the `.git` directory produced by the accepted CR
sequence: R5 recorded `HEAD`, status, symbolic-ref, remotes and local config
(c021 … c025) but never listed `.git`, and R4's checkout was never listed. A
form (1) allowlist would require new host observation, which this assignment
forbids, or would present an unobserved incidental set as authoritative, which
the R3 prompt prohibits. R2's listed set was such a presentation and is
withdrawn.

Form (2) is still a **closed** contract: every path under `.git` must match a
row of §8.5.2, and anything else is `HARD STOP`. The rows are derived from the
accepted CR sequence and the security role of each entry:

* `init --quiet --template=` copies no template, so it creates no `hooks/`,
  `info/`, `description` or `branches/`;
* one `fetch --no-tags --depth=1 --no-recurse-submodules` of one commit by
  object ID from a URL, with no remote configured and no destination refspec,
  writes objects, the shallow boundary and `FETCH_HEAD`, and no ref;
* `cat-file` and `rev-parse` are read-only;
* `checkout --detach` writes `index` and `HEAD` and, because CK-5's
  `core.logallrefupdates=true`, may write `logs/HEAD`;
* `gc.auto=0`, `maintenance.auto=false` and `fetch.writeCommitGraph=false`
  prevent gc, maintenance and commit-graph writes; and
* CK-5's exact key set has no `extensions.*`, so the reference back-end is
  the files back-end and the object format is SHA-1 (40 hexadecimal digits).

An entry is **required** only where the accepted, observed results
necessarily imply it: a resolvable detached `HEAD` (c021, c023), a local
config (c025), an object store holding the pin (c017 … c019), a references
directory, an index after a checkout (c020, c022), and a shallow boundary
after a depth-1 fetch. An entry the procedure may or may not create,
depending on Git's version or the number of fetched objects, is **optional**:
its absence is never a failure, and its presence is admitted only within its
row's constraints. **No optional row is a claim that the entry was observed.**

A benign Git-version incidental outside the table therefore produces a
fail-closed `HARD STOP`. The remedy is a reviewed amendment of this table,
never a run-time admission. The first CK-9 run's inventory (§8.5.4) becomes
the first durable observation of the layout.

#### 8.5.2 Admitted structure (paths relative to `.git`)

Depth is bounded: no admitted path is more than three components below
`.git`. Every regular file must also satisfy CK-3 (owner, group, not group-
or world-writable, no set-ID bit, `nlink` `1`); every directory must satisfy
CK-3 and contain only the children its row admits.

| Row | Path | Type | Presence | Constraint |
|---|---|---|---|---|
| G-1 | `HEAD` | regular | required | exactly the 40 lowercase hexadecimal digits of the pin followed by one LF (41 bytes): detached HEAD in the files back-end |
| G-2 | `config` | regular | required | `config --local --list` prints exactly CK-5's four `key=value` lines and nothing else |
| G-3 | `index` | regular | required | no constraint beyond CK-3; its meaning is verified by CK-4 |
| G-4 | `shallow` | regular | required | exactly the pin followed by one LF |
| G-5 | `objects` | directory | required | children only G-6, G-7 and G-8 |
| G-6 | `objects/pack` | directory | optional | children only regular files named `pack-⟨40 hex⟩.pack`, `pack-⟨40 hex⟩.idx` or `pack-⟨40 hex⟩.rev`; every `.idx` and `.rev` has a `.pack` of the same stem, and every `.pack` has an `.idx` |
| G-7 | `objects/info` | directory | optional | **empty** |
| G-8 | `objects/⟨2 hex⟩` | directory | optional (any number up to 256) | children only regular files named by exactly 38 lowercase hexadecimal digits |
| G-9 | `refs` | directory | required | children only G-10; **no regular file anywhere under `refs`** |
| G-10 | `refs/heads`, `refs/tags` | directory | optional | **empty** |
| G-11 | `FETCH_HEAD` | regular | optional | exactly one line, whose first 41 bytes are the pin followed by a TAB |
| G-12 | `logs` | directory | optional | children only G-13 |
| G-13 | `logs/HEAD` | regular | optional | at most two lines; in each, the first field is 40 zeros or the pin and the second field is the pin |
| G-14 | `hooks` | directory | optional | **empty** (CK-6) |

#### 8.5.3 Mechanisms explicitly rejected, and self-location checks

Each GX row names a mechanism and examples of the state that carries it. Its
presence is `HARD STOP` with the GX identifier. **The GX list is diagnostic,
not the boundary:** an entry that matches no G row is `HARD STOP: CK-9
unlisted .git entry ⟨path⟩` whether or not a GX row names it.

| Row | Mechanism | State rejected (examples, not limits) |
|---|---|---|
| GX-1 | gitfile or symlink indirection of the repository | `.git` is a regular file (`gitdir:`) or a symlink; any symlink under `.git` (also CK-3) |
| GX-2 | common-directory or worktree indirection | `commondir`, `gitdir`, `worktrees/`, `config.worktree` |
| GX-3 | object borrowing or derived object indexes | anything in `objects/info`, including `alternates`, `http-alternates`, `packs`, `commit-graph`, `commit-graphs/`, `multi-pack-index` |
| GX-4 | replacement objects and unexpected references | `refs/replace/`, `refs/remotes/`, any file under `refs/`, `packed-refs` |
| GX-5 | grafts, attributes, ignore masking and sparse views | `info/` and anything in it (`grafts`, `attributes`, `exclude`, `sparse-checkout`) |
| GX-6 | executable hooks | any entry in `hooks/` |
| GX-7 | submodule state | `modules/`; also a gitlink or `.gitmodules` in the tree (CK-7) |
| GX-8 | configuration that redirects, executes, authenticates, rewrites URLs, selects transport, filters, monitors or maintains | any key beyond CK-5's four, including `include.*`, `includeIf.*`, `credential.*`, `url.*`, `http.*`, `remote.*`, `core.sshCommand`, `core.hooksPath`, `core.fsmonitor`, `core.worktree`, `core.attributesFile`, `core.alternateRefsCommand`, `filter.*`, `diff.*`, `merge.*`, `submodule.*`, `maintenance.*`, `extensions.*`, `protocol.*` |
| GX-9 | alternative reference or object-store state | `reftable/`, `*.promisor`, `*.keep`, `*.bitmap`, `*.mtimes` |
| GX-10 | interrupted or concurrent Git operation | any `*.lock` (including `index.lock`, `shallow.lock`, `HEAD.lock`), `tmp_*`, `incoming-*` |
| GX-11 | operation state not produced by CR | `ORIG_HEAD`, `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `REBASE_HEAD`, `AUTO_MERGE`, `BISECT_*`, `rebase-merge/`, `rebase-apply/`, `sequencer/` |
| GX-12 | template residue, monitors, large-file or split-index state | `description`, `branches/`, `COMMIT_EDITMSG`, `fsmonitor--daemon*`, `lfs/`, `sharedindex.*` |

**Self-location checks**, run with CR-2/CR-3 in force:

| Row | Check | Required result |
|---|---|---|
| L-1 | the literal environment prefix of every CK Git command | exactly CR-2's assignments; no other variable (the prohibited indirection variables of CR-2 are therefore absent) |
| L-2 | `rev-parse --absolute-git-dir` | exactly `⟨F⟩/.git` |
| L-3 | `rev-parse --show-toplevel` | exactly `⟨F⟩` |
| L-4 | `rev-parse --path-format=absolute --git-common-dir` | exactly `⟨F⟩/.git` |
| L-5 | `rev-parse --is-bare-repository`, `--is-shallow-repository`, `--show-object-format` | `false`, `true`, `sha1` |

#### 8.5.4 Outcomes and bounded evidence

* **PASS** if and only if: `.git` is a non-symlink directory directly under
  F's root; the no-follow walk of `.git` (CK-3's method) finds only paths
  that each match exactly one G row and satisfy its constraint; G-1, G-2,
  G-3, G-4, G-5 and G-9 are present; no GX row matches; and L-1 … L-5 hold.
* **`HARD STOP`** at the first failure, in the form `HARD STOP: CK-9 ⟨G-n
  constraint | GX-n | unlisted .git entry | missing required G-n | L-n⟩
  ⟨relative path⟩`. CK-9 runs before CK-10 and before any consumption.
  Nothing is repaired, removed, re-fetched or retried.
* **Evidence recorded** (bounded by the table): `ck9.tsv`, one row per path
  under `.git` — relative path, type, size, mode, UID, GID, `(dev, ino)`,
  `nlink`, matched row — with the SHA-256 of every regular file except the
  object files of G-6 and G-8, whose names and sizes are recorded and whose
  integrity is Git's content addressing; the verbatim contents of G-1, G-4
  and the G-2 key list (none of them secret); the digests, not the contents,
  of G-11 and G-13; the L-1 … L-5 outputs; the entry count; and the SHA-256
  of `ck9.tsv`, which CK-11 and `source_checkout` carry. No other `.git`
  content is copied into evidence.

### 8.6 Source consumption *(R3)*

#### 8.6.1 Facts of the pinned tree

Read from the controller's local object store with `git ls-tree -r
--full-tree` and `git cat-file` only (content-addressed; tree
`56ccab51963de051d67426be8c560d69c8f3638c`, equal to R5 c019):

* 1324 entries: 1271 of mode `100644`, 52 of mode `100755`, **1 of mode
  `120000`** and **none of mode `160000`**;
* no `.gitmodules` and no `.gitattributes` at any path; one `.gitignore`, at
  the root;
* the one symlink is **`venv`**, blob
  `0550fe8b3d5be23f92028239269c821dad0f4601`, 36 bytes, whose link text is
  `/opt/freedom-blades/runtime/venv-bot` with no trailing newline (SHA-256
  `7e566c75a8237ea1f6762242355a1bac4d5baee9253161287ea2a34ba356ef08`). It is
  absolute and therefore **checkout-escaping**;
* no tracked shell, Python or infrastructure file under `infra/` or `tools/`
  refers to `venv` by a relative path, and no tracked Python file imports a
  top-level module named `venv` (handback §5). The runtimes those files name
  are fixed absolute host paths, such as
  `/opt/freedom-blades/runtime/venv-web/bin/python` in the R5 runner blocks
  `s02` … `s05` and `/opt/freedom-blades/runtime/venv-bot/bin/python` in the
  bot's systemd template.

`venv` is intentional (the Freedom bot's deployment link) and is **not**
banned: banning it would misdescribe the accepted tree and make every F fail.
It is inventoried, authenticated and never consumed.

#### 8.6.2 Symlink classification (CK-3 (e))

For a symlink at repository path `p` with link text `t`, read by `readlink`
without following:

1. an empty `t` is `HARD STOP`;
2. if `t` begins with `/`, the class is **`absolute`**;
3. otherwise `q` is computed **lexically** from `dirname(p)` and `t`,
   component by component: an empty or `.` component is dropped, `..` removes
   one component, and removing a component when none remains (that is, going
   above F's root) makes the class **`relative-escaping`**;
4. otherwise the class is **`relative-internal`**. `q` is never resolved,
   even if it names another symlink.

`absolute` and `relative-escaping` are **checkout-escaping**. All three
classes are **non-consumable** (SC-3); the class is recorded evidence and
grants nothing. The classification processes path text only: it never calls
`stat` with following, `realpath` or `readlink -f`, and never accesses the
target. For the pinned commit the result is exactly one symlink, `venv`,
class `absolute`.

**Mode `120000` alone prevents nothing.** CK-3's correspondence with the
pinned tree proves only that the link is the committed one with the
committed text. Whether a command escapes the checkout depends on whether it
dereferences the link, which SC-1 … SC-8 prohibit.

#### 8.6.3 NFW — the no-follow walk

NFW is the only admissible way for an RP-11 consumer to read repository bytes
for verification or in-process use. Inputs: F's root (CK-0's literal), the
root's recorded `(dev, ino)` (CK-2) and a repository-relative path `r`.

1. **Lexical check.** `r` is non-empty and relative; its components are
   separated by single `/`; no component is empty, `.` or `..`; it contains
   no NUL; it is at most 4096 bytes; its first component is not `.git`; and
   neither `r` nor any proper prefix of `r` is in CK-3's recorded symlink set
   (SC-2).
2. **Root.** `d = open(⟨root⟩, O_RDONLY | O_DIRECTORY | O_NOFOLLOW |
   O_CLOEXEC)`; `fstat(d)` is a directory with the recorded `(dev, ino)`,
   owner and group `ubuntu`, mode `0700`.
3. **Each intermediate component `c`.** `d′ = openat(d, c, O_RDONLY |
   O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC)`; `fstat(d′)` is a directory on the
   root's `st_dev`, owner and group `ubuntu`, not group- or world-writable;
   then `d` is closed and replaced by `d′`.
4. **Leaf.** `f = openat(d, ⟨leaf⟩, O_RDONLY | O_NOFOLLOW | O_NONBLOCK |
   O_CLOEXEC)`; `fstat(f)` is a regular file on the root's `st_dev`, owner and
   group `ubuntu`, not group- or world-writable, without a set-ID bit, with
   `nlink` `1`.
5. **Read.** The bytes are read to end of file from `f` only; their SHA-256 is
   computed; a second `fstat(f)` shows the same size and modification time.
6. **Failure.** `ELOOP` or `ENOTDIR` (what Linux returns for `O_NOFOLLOW` on a
   symlink), any other error, or any failed condition is `HARD STOP: source
   path ⟨r⟩ ⟨reason⟩` **before the bytes are used**. No following opener is
   tried as a fallback, and nothing is resolved, repaired or retried.

NFW is implemented with Python's `os.open(…, dir_fd=…)` and `os.fstat` under
the slice's fixed interpreter (§8.6.6). No shell utility reads a path in F for
verification or in-process use.

#### 8.6.4 The source-consumption contract SC-1 … SC-8

**Consumption** means opening for reading, executing, sourcing, importing,
hashing as source, using as a working directory, passing as a path argument
to a tool, copying, archiving, or traversing as a directory component.
**Inventory** — `lstat`, `readlink` of the link text, and Git's index and
status operations — is not consumption.

* **SC-1 Covered-source list.** Every RP-11 slice that consumes repository
  bytes has an accepted covered-source list CS: repository-relative paths,
  each with its accepted SHA-256 (from the reviewed manifest, the slice's
  Appendix-A-style list, or the governing-file pins). A slice consumes no
  repository path outside CS. A slice whose tooling would read a path outside
  CS is not admissible, and its assignment is not accepted.
* **SC-2 No symlink component.** No CS path equals, or has a proper prefix
  equal to, a mode-`120000` path of the pinned tree. This is checked when CS
  is accepted and again at run time against CK-3's recorded set (NFW step 1).
  For the pinned commit: no CS path is `venv` or begins with `venv/`.
* **SC-3 Symlinks are non-consumable.** No RP-11 command may open, read,
  execute, source, import, hash as source, `chdir` into, traverse through,
  `stat` with following, copy, archive or otherwise dereference any symlink in
  F, or any path through one. For the pinned commit this is `venv`.
* **SC-4 Verified bytes.** Every consumed CS path resolves through NFW to a
  regular file owned by `ubuntu:ubuntu`, not group- or world-writable, with
  `nlink` `1`, whose bytes equal its accepted digest (CK-10).
* **SC-5 Consumer classes.**
  * **Class B (byte consumers)** read the bytes themselves through NFW and use
    only those bytes: the CK-10 helper, H-1's installation reads, H-2's
    `baseline.repository` recomputation, `ACT`'s read of A-2's file,
    A1-S2 after restatement, and the bootstrap at TR-10.
  * **Class T (tool consumers)** are tools whose own opens are not
    NFW-confined: Git (A0-02, CK-4), the rebuild's `provision.py`,
    `enter.py build` and `build.sh`, a pytest run, A1-S1's harness dry run,
    and the agent client reading its settings and hooks at TR-2. A Class T
    consumer is admissible only if all of the following hold:
    * **T-1** CK-10 verified the complete CS immediately before the
      invocation, with no intervening act;
    * **T-2** the executable is a fixed absolute host path outside F
      (§8.6.6), never a path in F; `PATH` and `PYTHONPATH` contain no path in
      F; no argument or environment value names a symlink in F or a path
      through one;
    * **T-3** every path argument and the working directory are F's root or
      a CS-covered path reached without a symlink component, and any
      recursive discovery starts only from declared roots that contain no
      symlink. For the pinned commit, F's root may be a working directory
      but is never a recursive collection or discovery root, because it
      contains `venv`; explicit roots such as `tests/test_*.py` or
      `tests/web` are acceptable;
    * **T-4** the slice's assignment carries a static review item showing
      that the tool's configured read set lies within CS and reaches no
      symlink. For a Python tool that places F's root on `sys.path` (for
      example `-m` with F as working directory), the item shows that nothing
      imports a top-level module whose name equals a root-level symlink —
      for the pinned commit, `venv` — which today holds for every tracked
      Python file (§8.6.1);
    * **T-5** the tool writes nothing into F (`PYTHONDONTWRITEBYTECODE=1` or
      `-B`; no tool cache under F); and
    * **T-6** after the tool exits, CK-3, CK-4 (with `--ignored`) and CK-10
      are re-run, and any difference from the pre-use record makes the slice's
      terminal state `INVALID RUN`, or the slice's defined fail-closed state,
      with nothing repaired.
  * Git is symlink-safe as a Class T consumer by construction: it records and
    compares link text and does not follow worktree symlinks for tracked
    content.
* **SC-6 Stated residual.** A Class T tool is not confined at the system-call
  level. For it, the guarantee rests on T-1 … T-6 and on F being
  `ubuntu`-owned `0700`, so that only `ubuntu` and root can change F between
  T-1 and use; that is the authority boundary of OH-D-6, not a privilege
  boundary. A slice whose tool cannot satisfy T-2 … T-5 is not admissible.
* **SC-7 Attempted consumption is a pre-use `HARD STOP`.** An attempt to
  consume a symlink, or a path with a symlink component, detected before the
  bytes are used — by SC-2's lexical check, by NFW's `ELOOP` or `ENOTDIR`, or
  by T-2/T-3's argument check — is `HARD STOP` before use. Nothing is
  followed, resolved, substituted, repaired or retried. T-6's post-run
  difference is a separate terminal `INVALID RUN`.
* **SC-8 Records.** The slice records CS and its SHA-256, every NFW result,
  CK-3's symlink set with classes, every Class T invocation literal, and the
  T-6 comparison, in its evidence and in `source_checkout` (§8.4).

#### 8.6.5 Trace of every consumer

| Consumer | Slice | Class | Reads | Rule applied |
|---|---|---|---|---|
| CK-10 helper | every source-consuming slice | B | governing files; CS | NFW; never `sha256sum` (CK-10 *(R3)*) |
| H-1 tool (§4.2.4) | OH-S8 | B | bootstrap, unit, staged rule, `rp11_h1.py` | NFW, then in-memory verification and publication (H-1 *(R3)*) |
| H-2 recomputation | H-2 | B | manifest, `expected.sha256` and other `baseline.repository` inputs | NFW (H-2 *(R3)*) |
| `ACT` | activation | B | A-2's file | NFW; digest equal to A-2's SHA-256 argument (A-2 *(R3)*) |
| bootstrap `rp11_entry.py` (TR-10) | Pass A | B | covered sources and hook files | NFW per file, then C11 C-6 unchanged (TR-10 *(R3)*) |
| A1-S2 | Pass A | B after OH-S3 restatement | five harness files | NFW hashing replaces `sha256sum` |
| A0-02 | Pass A | T (Git) | index and worktree metadata | CR-2/CR-3; CK-3 symlink-set comparison first; T-1 … T-6, with Git comparing link text and never following worktree symlinks (A0-02 *(R3)*) |
| A1-S1 | Pass A | T | harness covered sources | fixed `/opt/freedom-blades/runtime/venv-web/bin/python`; T-1 … T-6, including T-4's `sys.path` item |
| agent client hooks (TR-2) | pass operator | T | `.claude/settings.json`, hook files, catalogue | in CS; T-1 … T-6; defense in depth only (TR-2 *(R3)*) |
| rebuild `provision.py`, `enter.py build`, `build.sh` | OH-S5 | T | the rebuild's Appendix-A-style list (§4.5.2) as CS | fixed host interpreter as in R5 `s05` (`/opt/freedom-blades/runtime/venv-web/bin/python -B`); F's root as working directory only; outputs only under `/var/tmp/⟨BRUN⟩-{index,cache,root,work,evidence}`; T-1 … T-6 |
| RP-11 tests under CPython 3.14 | OH-S4 Test run | T | explicit test paths and the code under test | `/usr/bin/python3.14`; explicit roots; `-B` and no pytest cache under F; T-1 … T-6. A missing test dependency is that slice's stated gap, never an installation under this proposal |
| fault drill | OH-S8b | B or T per read | test `pass-a.json`, test A-2 | as the matching row above |

#### 8.6.6 Interpreters and runtimes are host paths, not checkout consumption

Invoking a separately installed interpreter or runtime by its fixed accepted
host path — `/usr/bin/python3.14` (TR-9, Route 1) or
`/opt/freedom-blades/runtime/venv-web/bin/python` (Role F) — is **not**
consumption through F's `venv` symlink and involves no path in F. Those
executables are governed by their own accepted checks (HF-07, HF-08, HF-10,
M-5 and the D-3b equality gates for the system interpreter; Role F's status
for `venv-web`), not by CK or SC. Conversely, `⟨F⟩/venv`,
`⟨F⟩/venv/bin/python` or any `venv/…` path is never an executable,
interpreter, `PATH` element, import root or working directory of an RP-11
command (SC-3). That `venv`'s link text names
`/opt/freedom-blades/runtime/venv-bot` neither establishes nor relies on that
host path; RP-11 never uses it.

#### 8.6.7 Tests required of OH-S4 *(R3)*

In addition to R2's list (§13): NFW refuses a leaf symlink, an intermediate
symlink (both `relative-internal` and escaping), an escaping absolute link
named like `venv`, a symlinked root, a regular file with `nlink` `2`, a group-
or world-writable file or directory, a foreign owner, a FIFO, and a size or
modification-time change during the read; CK-3 accepts a `venv` symlink whose
link text equals the blob, ignores symlink permission bits, and refuses
altered link text, an extra or missing symlink, and a symlink under `.git`;
CK-9 accepts the required rows alone and with each optional row, refuses each
GX example, an unlisted entry, a missing required row, a gitfile `.git` and
each L-row failure (for example `GIT_DIR` present in the environment); and
CK-10's helper is shown, by test, never to call a following opener.

---

## 9. Future H-0 contract (FI-1 … FI-5, *R2*)

Proposed as §4.4.1 *(R2)*, applying to every future H-0 or H-0G assignment:

* **FI-1 Fixed inputs.** Every fact whose definition depends on a
  maintainer-supplied value is listed with that value as a fixed input. Today
  that is the capture-root parent `/var/lib/rp11-capture` and its fixed
  ancestor `/var/lib` (HF-15), the interpreter path `/usr/bin/python3.14` and
  the package names `python3.14`, `python3.14-minimal`,
  `libpython3.14-minimal`, `libpython3.14-stdlib` (Route 1), and the R5 anchor
  values of §10.2. *(R2)* No client path (D-2) and no repository path (D-7) is
  an H-0 input.
* **FI-2 Pre-execution `HARD STOP`.** The executor checks every FI-1 input
  before any connection, command or write. A missing, empty or malformed input
  is `HARD STOP: missing fixed input ⟨name⟩` and produces a handback and
  nothing else.
* **FI-3 No `not specified` at PASS.** PASS requires every listed fact to be
  observed, or to carry an outcome its definition permits (`absent`,
  `unreadable`, a recorded non-zero exit **where the definition names it**).
* **FI-4 No fact whose input comes from a later slice** (e.g. HF-20b).
* **FI-5 No inference** from controller-side state, another host, an earlier
  run's retained paths, or the normal workspace W.

---

## 10. R5 fact disposition and composition

### 10.1 Disposition

R5's handback and retained-evidence digests (`MANIFEST.payload`
`f116244f94ca3ea42e51b0d1c2ea3e0c99257cecfafc5b9c13bd7fb742724503`;
`MANIFEST.final`
`b8da7875b2f87a44483d9c744426855360279cc5f332f120fcac20bafe397553`;
`INVENTORY.owner-mode`
`70117b92702aa4690a75d6c23f5a93f620dc5117dc943a61d1417469842bee78`) and its
independent review are preserved unchanged. "Accepted from R5" means *proposed
for acceptance as observed at R5's time*, subject to Codex and Peter.

| Fact | Disposition | Note |
|---|---|---|
| retrieval, clean detached isolated checkout, governing-file digests | **accepted from R5** (independent review) | the checkout is now an R path (§8.1): evidence only, never reused |
| HF-01, HF-02 | **accepted from R5** | re-observed by H-0G as anchors; E-1 in every executing slice |
| HF-03 account, groups, home, shell | **accepted from R5** | UID/GID/groups feed CK-1 |
| HF-03 repository ownership | **withdrawn from H-0 (D-7)** | never observed by R5 and never inferred; replaced by CK-1/CK-3 per slice |
| HF-04, HF-05 | **accepted from R5** | kernel release is an anchor |
| HF-06 | **accepted from R5** as observed (CPython 3.14.4) | invalidates the 3.12 premise; Route 1 |
| HF-07 systemd, polkit, glibc, coreutils, util-linux, sudo, dbus rows | **accepted from R5** | `systemd`, `polkitd`, `libc6` versions are anchors |
| HF-07 `python3.12*` rows | **accepted from R5** as `not installed`; **invalidated as a contract** (Route 1) | replaced by `python3.14*` rows |
| HF-07 `python3.14`, `libpython3.14-minimal`, `libpython3.14-stdlib` | **requires a fresh observation** (H-0G) | never queried |
| HF-07 `python3.14-minimal`, `python3-minimal`, `dpkg -S` of both paths | **accepted from R5** | `python3.14-minimal` version is an anchor |
| HF-08 `/usr/bin/python3.12` | **accepted from R5** as absent; invalidated as a contract | — |
| HF-08 `/usr/bin/python3.14` owner, mode, size, SHA-256 | **accepted from R5** (c096, c097) | SHA-256 is an anchor |
| HF-08 exact-path `/usr/bin/python3.14 -I -S -c` output | **requires a fresh observation** (H-0G) | c012 used the symlink `/usr/bin/python3` |
| HF-09 | **accepted from R5** | PO-19 re-citation uses it |
| HF-10 | **accepted from R5** (python3.14 through c097; others c103/c104) | link targets of `sha256sum`, `stat`, `sleep`, `sudo` not recorded (Optional) |
| HF-11 | **accepted from R5**, except `/etc/polkit-1/rules.d/50-freedom-blades-rp11.rules`: **unknown** | established only at P-0p/AM-0 (§7.1), never in H-0 |
| HF-12 | **accepted from R5**, including `unreadable` | — |
| HF-13, HF-14, HF-16, HF-17, HF-19 | **accepted from R5** | HF-17 motivates §6.7 |
| HF-15 listed paths, `/run` | **accepted from R5** (c124–c143) | c136/c137 (`/var/lib`) are re-observed by H-0G as anchors |
| HF-15 capture-root parent | **requires a fresh observation** (D-1c) | H-0G G-15a … G-15d (§11) |
| HF-18 | **withdrawn from H-0 (D-2)** | per-slice preflight |
| HF-20a | **accepted from R5** (c151) | — |
| HF-20b | **withdrawn from H-0 (D-5)** | CL-21i; AP-0/AM-0 |

### 10.2 Composition anchors (complete)

The composed H-0 record is R5's record plus H-0G's record, joined by a
composition statement that cites both evidence digests and both observation
times. It is valid only if H-0G re-observes every anchor below equal to R5's
value. Every later version-equality gate uses H-0G's values.

| # | Anchor | R5 value | R5 evidence | H-0G command |
|---|---|---|---|---|
| A-1 | nodename (HF-01) | `Test` | c007 | `uname -n` |
| A-2 | `/etc/machine-id` SHA-256 (HF-02) | `e38397f175bbfcfd1554b74ebdc2c8cd01a5f2d6c816491568ca50445799cc5d` | c008 | `sha256sum /etc/machine-id` |
| A-3 | kernel release (HF-04) | `7.0.0-31-generic` | c043 | `uname -r` |
| A-4 | `systemd` version (HF-07) | `259.5-0ubuntu3.4` | c046 | `dpkg-query -W -f` |
| A-5 | `polkitd` version | `127-2ubuntu1.1` | c050 | `dpkg-query -W -f` |
| A-6 | `libc6` version | `2.43-2ubuntu2.4` | c052 | `dpkg-query -W -f` |
| A-7 | `python3.14-minimal` version | `3.14.4-1ubuntu0.2` | c072 | `dpkg-query -W -f` |
| A-8 | `/usr/bin/python3.14` SHA-256 | `be9a2a5eada8c89c1c399fdfb8397179e877c20d8db0739c802f726d4d0e69fd` | c096 | `sha256sum /usr/bin/python3.14` |
| A-9 *(R2, new)* | `/var/lib` type, owner, group, mode, `(dev, ino)`, xattr names | directory, `root:root`, `0755`, `(2049, 97831)`, none | c105 | G-15b |
| A-10 *(R2, new)* | `/var/lib`'s mount row: `TARGET`, `SOURCE`, `FSTYPE`, `OPTIONS` | `/`, `/dev/sda1`, `ext4`, `rw,relatime,discard,errors=remount-ro,commit=30` | c136 | G-15c |

A-9 and A-10 are new: the HF-15 composition is only sound if the ancestor
whose filesystem R5 recorded is the same object H-0G observes. `df` capacity
values (c137) are recorded but are **not** anchors; the `df` `source`, `fstype`
and `target` columns must equal R5's. Any anchor difference ends H-0G with
`HARD STOP: composition anchor changed`, and a full fresh H-0 under separate
authority is then required (D-6).

---

## 11. H-0G — narrow gap collection (D-6), corrected command semantics

**This section specifies a shape. It creates no authority and marks nothing
authorized.**

### 11.1 Entry criteria (all before any connection)

1. Codex acceptance of this cumulative R3 proposal and Peter's acceptance of
   it.
2. A separate H-0G authority with a **fresh work ID** and a fresh exclusive
   evidence path `/var/tmp/⟨RUN0⟩-h0g-evidence`, differing from every R1 … R5
   path, checked by `test -e`/`test -L` only; `/var/tmp` is never listed.
3. The FI-1 inputs of §9, including the R5 anchor values of §10.2 copied from
   the R5 handback.
4. A separately authorized execution topology (for example R5's single
   forwarding-disabled connection); its form is Peter's to authorize.

### 11.2 Command set (read-only, unprivileged; classes C-ID, C-PROC, C-STAT, C-DIG, C-VER, C-PKG only)

* **Anchors A-1 … A-8:** `uname -n`; `sha256sum /etc/machine-id`; `uname -r`;
  `dpkg-query -W -f` for `systemd`, `polkitd`, `libc6`, `python3.14-minimal`;
  `sha256sum /usr/bin/python3.14`.
* **HF-07 (Route 1):** `dpkg-query -W -f`, `dpkg --verify` and `apt-cache
  policy` (local lists only, no `apt update`) for `python3.14`,
  `libpython3.14-minimal`, `libpython3.14-stdlib`.
* **HF-08 (Route 1):** `stat` of `/usr/bin/python3.14`; `/usr/bin/python3.14
  -I -S -c` with a fixed literal printing `sys.version`,
  `sys.flags.isolated`, `sys.flags.no_site`, `sys.executable`, `sys.prefix`,
  `sys.path`. The bounded evidence helpers (C-STAT) also run under the exact
  path `/usr/bin/python3.14 -I -S`, never the unversioned symlink.

### 11.3 HF-15 *(R2)* commands

| ID | Command (exact form) | Expected result | Recorded as |
|---|---|---|---|
| G-15a | Python helper: `os.lstat("/var/lib/rp11-capture")`, then `os.listxattr("/var/lib/rp11-capture", follow_symlinks=False)` | both raise `FileNotFoundError` (`ENOENT`) | `parent=/var/lib/rp11-capture absent (lstat ENOENT; listxattr ENOENT)` |
| G-15b | Python helper: `os.lstat("/var/lib")` and `os.listxattr("/var/lib", follow_symlinks=False)`; the candidate list is the literal's own components only, nearest first; no listing | directory, not a symlink; values equal to A-9 | `nearest_existing_ancestor=/var/lib` with type, owner, group, mode, `(dev, ino)`, xattr names |
| G-15c | `/usr/bin/findmnt --target /var/lib -o TARGET\,SOURCE\,FSTYPE\,OPTIONS` | exit 0; one row equal to A-10 | **ancestor** mount facts |
| G-15d | `/usr/bin/df --output=source\,fstype\,size\,used\,avail\,pcent\,itotal\,iused\,iavail\,target -- /var/lib` | exit 0; `source`, `fstype`, `target` equal to R5 c137 | **ancestor** filesystem and capacity facts |

**Prohibited for HF-15:** any `findmnt`, `df` or `stat` with
`/var/lib/rp11-capture` as an operand; any listing of `/var/lib`; any other
path.

### 11.4 Absent-parent scan (carried from R2)

No H-0G `df` or `findmnt` command in this file names the absent parent. The
R3 handback (§5) records the re-run of that scan over this file.

### 11.5 Exit contract

`H-0G PASS` requires all of:

* every command of §11.2 and §11.3 run, with the outcome its definition
  permits;
* G-15a: `ENOENT` for both calls — **this is the PASS outcome for the parent**;
* G-15b: `/var/lib` a non-symlink directory equal to A-9;
* G-15c and G-15d: exit 0, with the anchor columns equal to A-10 and c137;
* every anchor A-1 … A-10 equal.

Terminal `HARD STOP` cases, each with the evidence closed and nothing
repaired:

| Condition | Terminal state |
|---|---|
| a FI-1 input missing or malformed | `HARD STOP: missing fixed input ⟨name⟩` (before any connection) |
| G-15a finds the parent **present** | record its `lstat`/xattr names only (no listing, no `findmnt`/`df` on it), then `HARD STOP: capture-root parent present before CPP` |
| G-15a raises anything other than `ENOENT` | `HARD STOP: capture-root parent unobservable (errno N)` |
| `/var/lib` absent, not a directory, or a symlink | `HARD STOP: capture-root ancestor invalid` |
| G-15c or G-15d non-zero | `HARD STOP: ancestor filesystem facts unavailable` |
| any anchor differs | `HARD STOP: composition anchor changed` → full fresh H-0 (D-6) |

Composition (§10.2) is a reviewer act after Codex's review of H-0G. The executor
never claims a composed `H-0 PASS`.

### 11.6 Prohibitions

§4.4.1's list, plus: no access to any R path (`/var/tmp/p5-r5-rp11-*`,
`/var/tmp/p5-r5-fresh-*`, the agent-client bootstrap evidence paths); **no
access of any kind to `/opt/freedom-blades/platform`, including `stat`
(D-7)**; no retrieval, checkout or repository path (H-0G is repository-free);
no privilege; no `/etc/polkit-1/rules.d` access beyond R5's `unreadable`; no
CL-21i path checks; no client search; no installation, package operation,
cleanup, retry, H-1/H-2, activation, commit or push.

---

## 12. Disposable-Test lifecycle (approved policy; proposed sequence)

### 12.1 Approved policy, recorded

Peter Duscha approved, through the R2 authority:

1. Test is disposable. Obsolete workspaces, run-specific checkouts and
   retained evidence should not accumulate indefinitely.
2. **No current object is deleted because this policy is recorded.**
3. The R1 … R5 retained paths and the current normal workspace remain
   untouched until the cumulative remediation is independently accepted and
   every evidence dependency is either closed or explicitly abandoned by Peter.
4. After that gate, a separately authorized bounded cleanup may remove only an
   exact enumerated path list whose identity, retention disposition and
   non-dependency have been reviewed. No glob, recursive broad root,
   discovery-and-delete loop or inferred path is acceptable.
5. Cleanup never targets `/`, `/var/tmp`, `/opt`, `/opt/freedom-blades`, a
   workspace root by implication, credentials, application/player data or an
   unreviewed path. Each target is checked against the approved literal list
   immediately before deletion; a mismatch is a hard stop.
6. After accepted cleanup, `/opt/freedom-blades/platform` is recreated as the
   normal clean Test workspace through a separately authorized
   synchronization or anonymous pinned-retrieval assignment, and verified
   before ordinary test use.
7. The normal workspace may be used for ordinary disposable-server testing but
   is never substituted for a fresh RP-11 checkout where independent pinned
   provenance is required.
8. Every future run-specific checkout or evidence path receives an explicit
   retention disposition at its review gate and a later exact-path cleanup
   authority when no longer needed.

### 12.2 Candidate object classes (from repository records only; no host inspection)

Paths below are those **named by durable repository records**. Whether each
was actually created is established only from its own record; where a record
does not establish it, the cleanup-enumeration slice (CE, §12.3) says so, and
the cleanup act records `absent` without searching.

*(R3)* "Evidence dependency" in this table means a dependency on the **host
bytes** at the path, not on the durable repository record that describes or
authenticates them (§12.7). A class closes only as RD-2 states.

| Class | Objects (as named by records) | Evidence dependency today | Closes at |
|---|---|---|---|
| C-W normal workspace | `/opt/freedom-blades/platform` | R3's accepted `HARD STOP` observed it dirty; D-7 preserves it | Peter's explicit closure of the R3 observation after LC-1 |
| C-H0 R5 | `/var/tmp/p5-r5-rp11-h0-20261006-02-evidence`, `/var/tmp/p5-r5-rp11-h0-20261006-02-checkout` | **live**: the composed H-0 (§10) cites R5's evidence. *(R3)* Whether H-0G's composition review or any later review or recovery needs R5's host bytes, rather than its durable handback, is stated explicitly at LC-2 (RD-2) and is not presumed | Codex review and Peter acceptance of the H-0G composition (OH-S1 composed), or Peter's explicit abandonment of R5 in favour of a full fresh H-0 |
| C-H0 R4 | `/var/tmp/p5-r5-rp11-h0-20261006-01-evidence`, `/var/tmp/p5-r5-rp11-h0-20261006-01-checkout` (R4 handback: closed evidence; checkout created by c015) | consumed `HARD STOP`, accepted by its review | Peter's explicit disposition after LC-1 |
| C-H0 R3 | `/var/tmp/p5-r5-rp11-h0-20261005-04-h0-evidence` | consumed `HARD STOP`, accepted; its returned text was malformed | same |
| C-H0 earlier | `/var/tmp/p5-r5-rp11-h0-20261005-01-h0-evidence`, `-02-h0-evidence` (first H-0 and R1); `-03-h0-evidence` (R2, withdrawn unused) | consumed or never used; creation not established by a repository record reviewed here | CE determines from the records; Peter's disposition |
| C-AC agent-client bootstrap evidence | `/var/tmp/p5-agent-client-bootstrap-20261005-01-evidence`, `-02-remediation-evidence`, `-03-handback-repair-evidence` | consumed; the repair return was recorded without clean acceptance of its reporting | Peter's explicit disposition |
| C-RB fresh-rebuild R4/R5 | `/var/tmp/p5-r5-fresh-20261003T234834Z-4fc93046-*` and `/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-*` (each suffix individually: `checkout`, `index`, `cache`, `root`, `work`, `evidence`, `pytest` as recorded) | §4.5.3: "only Peter's separate cleanup decision"; the D9/I-7 chain for image `04218ed2…` cites the accepted record. Route 1 supersedes the image only after OH-S4p/OH-S5 are accepted | Peter's decision after OH-S4p and OH-S5 acceptance |
| **excluded** | `/opt/freedom-blades/runtime` (`venv-web`), `/opt/freedom-blades/agent-tools`, `/home/ubuntu` and every dot-directory in it, PostgreSQL data and roles, `/var/lib/rp11-capture` and anything under it, every §4.2.3 path, `/var/lib/freedom-blades*`, `/var/lib/fb-evidence-p5-0` | not obsolete workspaces or evidence | not part of this lifecycle; any change needs its own decision |

The glob-like forms in the C-RB row are **record shorthand only**. CE must
expand each into exact literal paths from the records; no cleanup list may
contain a pattern.

### 12.3 Gates and sequence

| Gate | What happens | Authority | Must close before |
|---|---|---|---|
| LC-0 (now) | policy recorded; nothing deleted; no cleanup or recreation authority exists | R2 authority (documentation only) | — |
| LC-1 | **independent Codex acceptance of this cumulative R3 remediation** (which supersedes R2), then Peter's acceptance | Codex; Peter | any cleanup prompt, recreation, H-0G or later slice may be **prepared** |
| LC-2 | *(R3)* explicit closure of **every dependency on the class's host bytes** (RD-2), or Peter's explicit abandonment of that evidence: for C-H0 R5 the closing event is the **accepted H-0G composition review** together with its statement that no later review or recovery needs R5's host bytes (or Peter's abandonment of R5); for C-RB it is OH-S4p/OH-S5 acceptance with the same statement; for the rest, Peter's explicit disposition. A digest in a durable handback closes nothing (RD-1) | Codex review where a review closes it; Peter | CE may list that class |
| LC-3 | **CE, cleanup enumeration**: a repository-only slice that produces the exact literal list. For each entry: the absolute path; its class; the record that created it and whether that record establishes creation; expected type, owner, group and, where the record holds it, `(dev, ino)` (e.g. R5 c013: evidence directory `(2049, 1766009)`; R4 c013: `(2049, 1765916)`); its retention disposition; the closed dependency (LC-2); and *(R3)* its host-byte dependency statement with the record that closed it, or Peter's abandonment record (RD-2, RD-3) | its own repository-only authority | the cleanup prompt is written |
| LC-4 | independent review of CE's list; Peter approves the literal list | Codex; Peter | the cleanup act |
| LC-5 | **bounded cleanup act** on `oracle-test` under its own authority and work ID, removing only the approved literals (§12.4) | Peter's separate authority | recreation |
| LC-6 | review of the cleanup handback (per-target before/after records, mismatches, absences) | Codex; Peter | recreation |
| LC-7 | **workspace recreation** (§12.5) under its own authority, then its review | Peter; Codex | ordinary test use of W |

H-0G does not depend on LC-2 … LC-7 and may proceed after LC-1 under its own
authority, because it touches none of these objects. The R5 class cannot be
cleaned before H-0G's composition is reviewed, because R5 is a composition
input.

### 12.4 Constraints on the later cleanup act (design only; no command is written here)

1. **Literal list only.** Every target is an absolute path byte-equal to an
   entry of the approved list. No glob, brace, variable, pattern, `find`,
   discovery loop, parent-of or inferred path. A path not on the list is never
   touched, even if it looks related.
2. **Forbidden targets**, refused even if listed: `/`, `/var`, `/var/tmp`,
   `/var/lib`, `/opt`, `/opt/freedom-blades`, `/opt/freedom-blades/runtime`,
   `/opt/freedom-blades/agent-tools`, `/home`, `/home/ubuntu`, `/etc`, `/usr`,
   `/run`, `/tmp`, `/var/lib/rp11-capture` and anything under it, every §4.2.3
   path, `/var/lib/freedom-blades*`, `/var/lib/fb-evidence-p5-0`, PostgreSQL
   data directories, any credential file (including SSH, model-provider and
   Git credential material), and application or player data.
   `/opt/freedom-blades/platform` may be removed **only** as its own literal
   list entry under class C-W, never by implication or as the parent or
   container of another entry.
3. **Allowed parents.** A retained run path must be a **direct child** of
   `/var/tmp` whose name matches its record exactly. C-W must be exactly
   `/opt/freedom-blades/platform`.
4. **Immediately before each deletion**, for that target only: `lstat` (no
   follow) of the path and of every ancestor component; the target is not a
   symlink; no ancestor is a symlink; the target is not a mount point
   (`/proc/self/mountinfo`); type, owner, group and, where listed, `(dev, ino)`
   equal the approved entry. **Any mismatch is `HARD STOP`**: that target and
   every later target are left untouched. An `ENOENT` target is recorded
   `absent` and skipped, with no search.
5. **Removal scope.** Removing an approved directory entry removes that
   directory and its own contents only, without following symlinks and
   without crossing into another filesystem (`st_dev`). Nothing above the
   literal path is ever removed or modified (question 17).
6. **Privilege.** Unprivileged as `ubuntu` wherever the recorded owner is
   `ubuntu`. A root-owned entry (if CE finds one, such as a root-owned
   journal) needs an explicit per-entry privilege grant in the cleanup
   authority.
7. **Records.** Per target: the list entry, the pre-deletion observation, the
   action, and a post-deletion `lstat` (`ENOENT`). The cleanup evidence
   directory is fresh, exclusive and never itself a target.
8. *(R3, replacing R2's item 8)* **Preservation.** Manifests and digests in
   durable handbacks authenticate or describe retained bytes; they do **not**
   reproduce them. A digest's presence in a handback makes no path
   cleanup-eligible. Eligibility follows only from RD-2 (§12.7). A path whose
   bytes any pending or foreseeable review or recovery needs stays retained
   unless a separately authorized preservation or export step has succeeded
   and has been accepted (RD-4). This proposal writes no cleanup or export
   command and creates no authority for either.

### 12.5 Recreating the normal workspace (LC-7)

* **Method (Peter's choice under its own authority):** (a) anonymous pinned
  retrieval on `oracle-test` from the canonical public URL, recommended because
  it yields recorded provenance without using the production workspace host;
  or (b) the documented secret-excluding synchronization of
  disposable-test-server.md §3.2. Option (b) uses the workspace host as a
  source, which OH-D-1 prohibits **for RP-11**; it is admissible only for
  ordinary non-RP-11 testing and only if Peter authorizes it.
* **Verification before ordinary test use:** the path is exactly
  `/opt/freedom-blades/platform`, a directory and not a symlink or mount
  point; owner `ubuntu:ubuntu` throughout; no regular file or directory group-
  or world-writable *(R3: symlink permission bits are not evaluated, and the
  tracked `venv` symlink is expected, §8.6.1)*;
  the commit and branch policy Peter names (for example detached at a pinned
  commit, or a named branch at a named commit); `git status --porcelain=v1
  --untracked-files=all` empty; no remote other than the canonical public
  HTTPS URL, and no credential helper or credential-bearing configuration;
  no `.env` or other secret present unless separately provided under its own
  authority.
* **Status after recreation:** W is the normal Test workspace for ordinary
  disposable-server testing. It is still **not** an RP-11 source (§8.1); RP-11
  slices continue to use F.

### 12.6 Future retention (every new path)

Each future H-0G, CE, cleanup, rebuild, H-1, drill, H-2, activation or pass
assignment names, for each path it creates: its class (F, evidence, record);
its retention disposition at the review gate (`retain as evidence until
⟨gate⟩` or `eligible for exact-path cleanup after ⟨gate⟩`); and the gate that
closes its dependency. *(R3)* The disposition also states whether that gate,
or any later review or recovery, needs the path's **host bytes** rather than
only its durable record (RD-2). A path without a disposition is not accepted
at review. Capture roots and `/var/lib/rp11-capture` are never cleanup-eligible
under this policy (K-13); their later removal needs Peter's explicit decision.

### 12.7 Retained bytes and cleanup eligibility *(R3)*

R2's §12.4 item 8 justified "no preservation copy" by saying durable handbacks
"reproduce the retained bytes' manifests and digests". That reasoning is
withdrawn. A manifest or digest lets a reviewer **authenticate** bytes that are
still available, or **describe** them; it cannot **reproduce** them. Some
handbacks also transcribe retained text — R5's Appendices A and B, for
example — but no repository record has been verified as a complete
byte-for-byte reproduction of any retained path, and this proposal does not
rely on transcription.

* **RD-1 A digest is not closure.** No retained path becomes
  cleanup-eligible because its digest, manifest or inventory appears in a
  durable handback or review.
* **RD-2 Eligibility.** A retained path becomes eligible for CE enumeration
  only when every dependency on its **host bytes** is explicitly closed by a
  recorded review or decision that names the path (or its class) and states
  that no pending or foreseeable review or recovery needs those bytes, **or**
  when Peter explicitly abandons that evidence in a recorded decision.
* **RD-3 Sequence.** Eligibility under RD-2 is followed, unchanged, by CE
  enumeration (LC-3), independent review of CE's list and Peter's literal-list
  approval (LC-4), and a separately authorized cleanup (LC-5). RD-2 never
  substitutes for any of them.
* **RD-4 Bytes still needed.** If a future review or recovery requires the
  retained bytes rather than only the durable record, the path remains
  retained unless a separately authorized preservation or export step
  succeeds and its result is accepted at review. Only then may RD-2 be
  satisfied for the original path, and the preserved copy receives its own
  retention disposition (§12.6).
* **RD-5 Unknown is not closed.** Where a closing review or decision does not
  state whether host bytes are still needed, the dependency is treated as
  open.

This section, like the rest of §12, writes no executable cleanup or export
command and creates no cleanup authority.

---

## 13. Successor slices (§4.7.4, *R2*, *R3*)

These rows replace or add to the D3-R6 rows of the same name. **Every slice
still needs its own authority; none is requested or created here.**

| Order | Slice | Scope | Gate |
|---|---|---|---|
| OH-S0 | as D3-R6, plus D-1 … D-7 (decided) and acceptance of this cumulative R3 amendment | decision | Codex re-review of R3 (LC-1), then Peter |
| OH-S1 | **H-0 composed** = R5 + H-0G (§10, §11), under FI-1 … FI-5 *(R2)*; repository-free | read-only, unprivileged | Codex review of H-0G and the composition |
| OH-S2 | as D3-R6, plus PO-12/AS-8 and PO-19 for 3.14, the PT-8 capability, PO-17 against the new image, and **CL-21i** | documentation, U-10 | Codex, then Peter; refuted PO-12/PO-19 → Route 3 review |
| OH-S3 | as D3-R6, plus the capture-root parent, template and CPP record (§4.6), and the D-7 restatement of A0-02, A1-S1/A1-S2 and the synchronization text (§8.4) | documentation | Codex re-review of the draft (A-1) |
| **OH-S4p** | interpreter retarget (§6.5 item 2), Route 1 | repository only | Codex review per slice, with a security-focused review |
| OH-S4 | as D3-R6, plus CK-0 … CK-11 implementation and tests (including symlink-root substitution, extra config key, hook, gitlink, replace ref, alternates, ignored file and non-`ubuntu` owner cases), *(R3)* CK-9's G/GX/L table, NFW and SC-1 … SC-8 with the §8.6.7 tests, the TR-10 `entry-source-not-verifiable` refusal, the `baseline` `source_checkout` split and its R3 fields (§8.4), and RP-11 code tests under CPython 3.14 | repository only | as before |
| OH-S5 | as before, with the new image digest and its own F under CK and SC (Class T, §8.6.5) | build as `ubuntu` | as before |
| OH-S8 | H-1 with **P-0p** (and the §4.1.1 *(R3)* role wording), its own F under CK, installation bytes read through NFW | as before | as before |
| **CPP** | capture-parent provisioning with the R2 preflight and postcondition (§4.4), after H-1 PASS and before the first A-2 | privileged, one directory | Codex review; Peter acceptance |
| OH-S8b | as D3-R6, with its own F if it reads repository bytes | as before | as before |
| OH-S9 | as D3-R6, with AP-0/AM-0 *(R2)* (§4.5, §6.7, §7), and one F per activation chain pinned in A-2 (§8.3) | outside this amendment | — |
| **CE (new)** | cleanup enumeration (§12.3 LC-3) | repository only | Codex review; Peter approves the literal list |
| **TC (new)** | bounded Test cleanup (§12.4) | host, exact literals only | Codex review of the handback; Peter |
| **WR (new)** | workspace recreation (§12.5) | host | Codex review; Peter |

---

## 14. Remaining prerequisites

Before **H-0G** may be prepared: LC-1 (this proposal accepted); a fresh work
ID, evidence path and topology authority.

Before **OH-S2** completes: H-0G composition accepted (the citations bind the
H-0G versions); Peter's U-9 restatement.

Before **OH-S4p/OH-S5**: OH-S2's PO-12/PO-19 not refuted; OH-S4p reviewed.
*(R3)* Before **OH-S5** additionally: OH-S4's RP-11 code tests under CPython
3.14 (§6.5 item 3) accepted, or their gap stated in OH-S4's handback and
accepted at its review.

Before **H-1 (OH-S8)**: OH-S2, OH-S4, OH-S4p, OH-S5 and OH-S7 accepted; the PO-11
(f)(i) directory list accepted for P-0p.

Before **CPP**: H-1 PASS accepted; the composed H-0 (for G-15b/G-15c
comparison).

Before any **A-2**: CPP accepted; CL-21i accepted (D-5); the D-3b equality
values fixed by the accepted citations.

Before **CE/TC/WR**: LC-1 and the LC-2 closure for each class listed.

The `disposable-test-server.md` restriction banner still names the consumed R5
restriction. Updating it is outside this assignment's three authorized
pointers and is left to the controller.

---

## 15. Questions for independent Codex re-review

*(R3)* Every question asks whether a completed rule in this proposal is
sufficient. None asks the reviewer to supply an allowlist, security rule,
normative value or design decision; R2's questions that did (former 2, 3, 8,
10, 11, 13 and 14) are answered in the text, and former question 13 is
withdrawn.

1. **HF-15 *(R2)*.** Do G-15a … G-15d and the §11.5 exit contract pass on the
   expected `ENOENT` state and fail closed on every other state, including a
   parent present before CPP?
2. **Ancestor determination.** Is observing only the literal's own
   components, nearest first, with `/var/lib` the single candidate and `/`
   and `/var` relied on from R5 c105, sufficient?
3. **CPP postcondition.** Do `st_dev` equality plus the `mountinfo`
   mount-point check suffice to prove "non-mount directory on the same
   filesystem"?
4. **Anchors A-9/A-10.** Are the anchors sufficient, with `df` capacity
   recorded but not anchored?
5. **D-7 objects.** Is the W/F/R distinction complete, and does any accepted
   text still read `/opt/freedom-blades/platform` as an RP-11 source?
6. **CR and CK.** Are CR-1 … CR-4 *(R3)* and CK-0 … CK-11 *(R3)* at least as
   strong as R5's accepted controls and R2's contract everywhere?
7. **CK-9 *(R3)* (R2-F1).** Does the closed table G-1 … G-14, with its
   required/optional split, the GX-1 … GX-12 rejections and L-1 … L-5, fail
   closed on every mechanism R2-F1 and the R3 prompt list, and is the
   reasoning for choosing form (2) over form (1) sound?
8. **CK-3 and SC *(R3)* (R2-F2).** Do CK-3, NFW and SC-1 … SC-8 together
   prevent every dereference of `venv`, or of any other symlink, by every
   consumer traced in §8.6.5, and is SC-6's stated residual for Class T tools
   acceptable?
9. **Reconciliation.** Does any source-consuming path in the accepted design,
   the operational draft or this proposal remain untraced by §8.6.5?
10. **`baseline` split.** Does moving `repository_root` into a per-slice
    `source_checkout`, with the R3 fields, keep H-2's byte-equality sound
    while H-1 and the pass use different checkouts?
11. **P-0p.** Is the §4.1.1 *(R3)* role wording sufficient to make P-0p's
    privileged read-only `lstat` set consistent with the accepted design?
12. **HF-20 split.** Is CL-21i's "empty list is an accepted result" wording
    safe?
13. **Route 1 completeness.** Is the carried Role A–D inventory complete, and
    is one OH-S4p slice with a security-focused review sufficient?
14. **Test-version ordering.** Is §14's requirement — OH-S4's CPython 3.14
    RP-11 tests, or their accepted stated gap, before OH-S5 — sufficient?
15. **HF-18.** Is the per-slice preflight strict enough to forbid installation
    and search, including for a symlinked client path?
16. **Activation-chain checkout.** Is the §8.3 note's argument sufficient for
    one F to serve H-2 through `DEACT` without violating "a retained checkout
    is never reused"?
17. **Cleanup removal scope.** Is "an approved directory and its own contents,
    no-follow, one filesystem" consistent with the policy's prohibition of a
    "recursive broad root"?
18. **Retained bytes *(R3)* (R2-F3).** Do §12.4 item 8 *(R3)* and RD-1 …
    RD-5 remove every reliance on digests as reproduction, and is LC-2's
    closing event for R5 sufficient?

---

## 16. No change to any accepted baseline, authority or gate

This proposal changes no accepted baseline, design text, decision (other than
recording D-1 … D-7 and the lifecycle policy as the R2 authority directed),
authority, gate, finding or disposition. R2 remains unaccepted. R5 remains
consumed and its `H-0 PASS` not accepted. No H-0G, CPP, cleanup enumeration,
cleanup, export, workspace recreation, OH-S2, OH-S4p or later slice is
authorized. No object on `oracle-test` is deleted, modified or inspected by
this proposal or by the policy it records. Every effect described above takes
effect only after Codex's independent re-review and Peter's recorded
acceptance, and each slice still requires its own authority.
