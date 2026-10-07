# Handback — R5 H-0 remediation: complete checkout contract, symlink-safe source consumption and retained-evidence rationale (R3)

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR3-20261006-05`

Date: 2026-10-06

Executor: Claude Code, in `/opt/freedom-blades/platform` (local read-only
repository inspection plus the authorized documentation writes)

Prompt:
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-claude-prompt.md),
SHA-256 `752e227e2221369547240ae5c088eb5b251b87f5ef4a9a42f67f041d121bd196`,
8944 bytes. Recomputed before any work; equal to the authority's pin.

Authority:
[`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-authority.md)
(SHA-256 `d589cbc16cfe1aac07026eaa473a3c9169567c4a1a9dcf48dc502f1b78d61833`)

Findings remediated:
[`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-findings.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-findings.md)

Deliverable:
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md)

## 1. Terminal state: `R3 REMEDIATION READY FOR REVIEW`

The cumulative R3 proposal and this handback are written, and the three
authorized current-state pointers are updated. R2-F1, R2-F2 and R2-F3 are
resolved in the proposal itself; no review question asks the reviewer to
supply an allowlist, security rule, normative value or design decision. R2
remains unaccepted, and everything in R3 is proposed text awaiting independent
Codex re-review. No host, network, retained-path, credential or secret access
occurred, and no cleanup, export, test, build or other host action was
performed.

## 2. Findings mapped to R3 sections

| Finding | R3 sections | Resolution |
|---|---|---|
| **R2-F1 (Blocking)** CK-9 not an executable closed contract | §0 item 1; §3.2; §8.2 CK-9 *(R3)* row; **§8.5** (8.5.1 choice of form, 8.5.2 G-1 … G-14, 8.5.3 GX-1 … GX-12 and L-1 … L-5, 8.5.4 outcomes and evidence); §8.6.7 tests; §15 (former question 13 withdrawn) | Form (2) chosen and justified: no durable accepted record lists the `.git` produced by the CR sequence (R5 never listed it), so an exact observed allowlist is unavailable without forbidden host access. The contract is still closed: every path under `.git` must match exactly one G row derived from the accepted CR sequence (R5 c015 … c020) and Git's layout for it; required rows are only those the observed results imply; optional rows are admitted only within exact constraints and are not claims of observation; anything else is `HARD STOP`. GX rows name every mechanism the prompt lists (remotes and config via CK-5/GX-8, includes, credential, URL-rewrite, transport, filter, hook, fsmonitor, maintenance, active hooks, gitlinks and submodule state, replace refs, grafts, alternates, worktree indirection, `commondir`, object borrowing, path and file types). L-1 … L-5 prove Git locates exactly `⟨F⟩/.git` with no environment indirection. PASS and `HARD STOP` outcomes and the bounded `ck9.tsv` evidence are exact |
| **R2-F2 (Blocking)** CK-3 claims an escaping-symlink control it does not perform | §0 item 2; §3.2; §8.1 note; §8.2 CK-3, CK-7, CK-10, CK-11 *(R3)*; §8.3 consumer column and chain note; §8.4 IA-12, §4.1.4, TR-2, TR-10, `source_checkout`, H-1, H-2, A-2, `ACT`, A0-02, A1-S1, A1-S2 *(R3)*; **§8.6** (8.6.1 pinned-tree facts, 8.6.2 classification, 8.6.3 NFW, 8.6.4 SC-1 … SC-8, 8.6.5 consumer trace, 8.6.6 interpreter clarification, 8.6.7 tests); §12.5; §13 | (1) inventory is `lstat`-only and never dereferences; (2) every worktree symlink must be a mode-`120000` tree entry and its `readlink` text must equal the pinned blob bytes; (3) absolute and lexically escaping targets are recorded **checkout-escaping and non-consumable**, and inventory no longer claims to reject them; (4) every consumed path is in the slice's CS, has no symlink component, and terminates in an `ubuntu:ubuntu`, non-group/world-writable, `nlink` 1 regular file whose bytes equal the accepted digest; (5) SC-3 forbids any RP-11 command from opening, executing, hashing as source, importing, traversing through or otherwise dereferencing a symlink; (6) attempted consumption is a pre-use `HARD STOP` (SC-7). The tracked `venv` symlink (link text `/opt/freedom-blades/runtime/venv-bot`, 36 bytes) is reconciled, not banned. Interpreters invoked by fixed host path are stated not to be consumption through `venv` (§8.6.6). Also corrected: R2's CK-3 would have misread every symlink's `0777` permission bits, and R2's CK-10 "R5 c026 pattern" used `sha256sum`, which follows symlinks |
| **R2-F3 (Important)** digests do not reproduce retained bytes | §0 item 3; §3.2; §12.2 note and C-H0 R5 row; §12.3 LC-2, LC-3; **§12.4 item 8 *(R3)***; §12.6; **§12.7 RD-1 … RD-5**; §15 question 18 | The reproduction rationale is withdrawn. Manifests and digests authenticate or describe but do not reproduce; a digest in a handback makes nothing cleanup-eligible; eligibility requires explicit closure of every host-byte dependency or Peter's explicit abandonment, followed by the unchanged CE, review, literal-list approval and separately authorized cleanup; a path whose bytes a future review or recovery needs stays retained unless a separately authorized preservation or export succeeds and is accepted. No executable cleanup or export command is written and no cleanup authority is created |

Preserved unchanged in substance (verified by a per-section comparison with R2,
§5): §4 HF-15 and CPP, §5 HF-18, §6 Route 1, §9 FI-1 … FI-5, §10 R5 disposition
and anchors A-1 … A-10. §7 changes only by the resolved P-0p role wording; §11
only by two R2→R3 self-references; §14 only by the stated OH-S5 test-ordering
prerequisite. D-1 … D-7 and the lifecycle policy are recorded exactly as the
R2 authority decided them.

Three carried R2 review questions also asked for a design decision. R3
answers each in the proposal instead: the §4.1.1 H-1 role wording for P-0p
(§7.1), one F per activation chain with its argument (§8.3 note), and
OH-S4's CPython 3.14 test evidence, or an accepted stated gap, before OH-S5
(§14). R3 also carries R5's exact CR options, which R2 had transcribed
incompletely (`advice.detachedHead=false`, `init.defaultBranch=h0-unborn`,
`timeout 900`; §3.2, §8.2).

## 3. Files changed

**Created by this assignment:**

| File | SHA-256 | Bytes |
|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md` | see §9 (final) | see §9 |
| `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-handback.md` | this file (digest not self-reported) | — |

**Updated by this assignment** — pointer edits only, applied on top of
pre-existing uncommitted edits, which were preserved:

| File | Before | After | Change |
|---|---|---|---|
| `docs/review/Handover information` | `68c9397a76f32344709b8dc06cb55171e946a5d1a54c270f8e6ffbd7baba60f7` | see §9 | heading "R3 remediation authorized" → "R3 remediation returned for review"; one terminal-state paragraph; "Active R3 Claude prompt" relabelled "Consumed"; R3 proposal and handback links |
| `docs/project-management/status.md` | `a722a62ea09fa9351cbbae552d887b0c8b93884f55331dca380b0594af5725e1` | see §9 | the same three changes in the current-status section |
| `docs/implementation-plan.md` | `39f72198f379fac3b33ccf3784d90e013fc205b8ebea988c06b92a3e594218c9` | see §9 | the same three changes, in §20 only |

Unchanged, recomputed at the end (§9): the R2 proposal, R2 handback, DR1
proposal and handback, the R2 findings, the R3 prompt and authority, the
accepted one-host design, `.agents/AGENTS.md` and `disposable-test-server.md`.
No source, test, infrastructure, manifest, change-log, decision-register or
archive file was touched. No migration, configuration or deployment change,
commit or push.

## 4. Pre-existing worktree changes, reported separately

Captured with `git status --short` before any edit (50 lines) and preserved:

- **Modified (11):** `.agents/AGENTS.md`;
  `docs/implementation-plan-archive/README.md`; `docs/implementation-plan.md`;
  `docs/operations/disposable-test-server-archive/README.md`;
  `docs/operations/disposable-test-server.md`;
  `docs/project-management/change-log.md`;
  `docs/project-management/decision-register.md`;
  `docs/project-management/status-archive/README.md`;
  `docs/project-management/status.md`; `docs/review/Handover information`;
  `docs/review/handover-archive/README.md`. Three of these are this
  assignment's pointer files (§3); their earlier uncommitted content was kept.
- **Untracked (39):** the four `*-through-2026-10-04-d3-r6-acceptance.md`
  snapshots and the R1 … R5, DR1, R2, R3 and agent-client prompts,
  authorities, handbacks and reviews, including this assignment's prompt and
  authority and the R2 findings.

The final `git status --short`, compared with the start snapshot, differs only
by the two new files (§9).

## 5. Commands and checks run, with exact results

All commands were local and read-only, except the authorized writes.

| Check | Command (summary) | Result |
|---|---|---|
| prompt pin | `sha256sum`, `wc -c` on the prompt | `752e227e…bd196`, 8944 bytes: **equal** to the authority |
| start snapshot | `git status --short` to a scratch file; `sha256sum` of the three pointer files and every source in proposal §1 | 50 lines; digests in §3 "Before" and proposal §1. R2 proposal `04a4abb4…ce105` equals R2 handback's report; DR1, C11 and operational-draft digests equal R2 §1 |
| required reading | `cat`/`sed`/`Read` of every item in the prompt's list (proposal §1) | done; no remote or retained path read |
| accepted CR sequence | `sed` of R5 Appendix B records c013 … c027 | exact environment, `-c` options (including `advice.detachedHead=false` and, for `init`, `init.defaultBranch=h0-unborn`), `timeout 900`, outputs; c025's four config keys; no `.git` listing in any record |
| pinned-tree facts | `git cat-file -t`, `git ls-tree -r --full-tree 46d1c35a…ef2ef`, `git cat-file -s/-p` of blob `0550fe8b…f4601` in the controller's object store | `commit`; 1324 entries: 1271 `100644`, 52 `100755`, 1 `120000` (`venv`), 0 `160000`; no `.gitmodules` or `.gitattributes`; one root `.gitignore`; `venv` link text `/opt/freedom-blades/runtime/venv-bot`, 36 bytes, no trailing newline, SHA-256 `7e566c75…ef08` |
| relative `venv` use | `git grep` of the pinned commit, `infra` and `tools`, for `venv` not part of `runtime/venv-*`; and of every `*.py` for `import venv`/`from venv` | one match only, a comment in `tools/phase_5_0_evidence/case_runtime.py:147` describing "a normal CPython venv" generically, not a path; **no** Python import of `venv` |
| design wording | `grep` of the accepted design for the §4.1.1 H-1 row, TR-2, TR-10, IA-12, `repository_root`, the `ACT` A-2 read; of C11 for C-6 and its failure rows; of the operational draft for A0-02, A1-S1, A1-S2 | texts cited in proposal §7.1, §8.4, §8.6.5 confirmed |
| construction | `cp` of the R2 proposal to the R3 path, then Python splices replacing §0 … §3, §8 and §15 … §16, and exact single-occurrence replacements elsewhere (each asserted to match once) | all replacements matched exactly once |
| preservation | Python per-section comparison of R2 and R3 | §4, §5, §6, §9, §10 **identical**; §7, §11, §14 differ only by the edits listed in §2 (confirmed with `diff`) |
| whitespace | `git diff --check` | exit 0, no output |
| whitespace, new files | `git diff --no-index --check /dev/null ⟨file⟩` | exit 1 with no error lines (files differ; no whitespace errors), for the proposal and this handback |
| unresolved phrase | `grep -i` for `to be fixed by review`, `fixed by review`, `to be decided`, `TBD`, reviewer-choose wording; plus a scan of every normative `\| CK-n ` row | 4 matches, all R3's quotations of R2's defect (§0, §3.2) or §15's statement that no question asks for a rule; **0** normative CK rows contain it |
| slice trace | Python parse of the §8.3 matrix and the §8.6.5 consumer table | every source-consuming slice (OH-S4/OH-S4p Test run, OH-S5, OH-S8, OH-S8b, the activation chain) has its own F, a consumer class and the matrix sentence binding it to CK-10 and SC-1 … SC-8; every one of the 12 consumers is bound to NFW or to T-1 … T-6 (A0-02's row was tightened to name T-1 … T-6 after the first run reported it unbound); CK-10 names NFW and SC-2 |
| mode-`120000` claim | `grep -n 120000` | every occurrence is the R2 quotation, a pinned-tree fact, CK-3's correspondence rule, SC-2, or §8.6.2's explicit statement "Mode `120000` alone prevents nothing" |
| reproduction claim | `grep -n -i reproduc` | every occurrence is a quotation of R2's defect, a negation, or the unrelated Role D "reproducibility" of test interpreters |
| absent-parent scan (carried) | Python scan of every inline code span containing `findmnt` or `df` | **0** in HF-15 (§4.3) or H-0G (§11); the four spans naming `/var/lib/rp11-capture` are §3.1's quotation of DR1's defect (2) and CPP's postcondition (2), which runs only after the parent exists — the same result as R2 |
| scope scan | `grep` for `rm`, `rmdir`, `-delete`, `rmtree`, `unlink(`, `shutil`; `ssh`, `scp`, `rsync`, `sudo `; `hereby`, `is authorized`, `authorizes`, `push`; `password`, `token`, `secret`, private-key material | deletion: only the policy phrase "discovery-and-delete loop" and the quoted draft term `rsync --delete` being withdrawn; privilege: the quoted Role A `sudo -n` literal, P-0p's `sudo -n` text and the quoted and amended §4.1.1 role wording; authority: only negations and "only if Peter authorizes it" for recreation option (b); push: the H-0G prohibition list; secrets: only "password database" (HF-03), "none of them secret", and the recreation rule that no secret is present. **No executable cleanup or export command, no grant of authority, no network action, no secret or player data** |

Final link, whitespace and status checks: §9.

## 6. Checks not run

- No application test suite, formatter, linter, type checker or build: the
  assignment is documentation-only and forbids them.
- No network, no `oracle-test` access, no access to any retained path
  (`/var/tmp/p5-r5-rp11-*`, `/var/tmp/p5-r5-fresh-*`, agent-client evidence)
  and no access to `/opt/freedom-blades/platform` on `oracle-test`. Every host
  fact is cited from durable repository handbacks.
- No upstream Git source or documentation was read. CK-9's derivation of the
  `.git` layout from the CR sequence (no template residue after `--template=`,
  no ref written by a fetch by object ID without a destination, `logs/HEAD`
  under `core.logallrefupdates`, files back-end and SHA-1 without
  `extensions.*`) is stated as the basis of the closed table, not as an
  observation; that is why entries the procedure may or may not create are
  optional rows and an unlisted entry fails closed. The first CK-9 run will be
  the first durable observation of the layout.
- NFW and SC are specified, not implemented or exercised; OH-S4 implements
  and tests them (proposal §8.6.7).
- Whether each record-named retained path in proposal §12.2 exists was not
  determined; that remains CE's task.
- No Markdown renderer was run.

## 7. Security implications

- **CK-9.** A planted alternates file, replace ref, graft, hook, include,
  worktree link, `commondir`, gitfile, reftable or lock state, or any entry
  Git's accepted procedure does not produce, now stops the slice
  deterministically, and Git's self-location is proven. The trade-off is
  stated: an unforeseen benign Git incidental also stops the slice and needs a
  reviewed amendment.
- **Symlinks.** The repository's one symlink can no longer be followed by any
  RP-11 consumer that reads bytes itself: NFW refuses symlinks at every
  component. Tool consumers (Git, the rebuild, pytest, the harness dry run,
  the client) are bounded by pre-use verification, fixed host executables,
  explicit roots, a static read-set review, no writes into F and a post-run
  re-check. The residual — tools are not confined at the system-call level —
  is stated (SC-6) and rests on F's `ubuntu`-only `0700` ownership, which is
  the accepted OH-D-6 authority boundary.
- **Retention.** Cleanup can no longer be justified by the presence of a
  digest. Unknown dependency is treated as open (RD-5).
- **Carried.** HF-15, HF-18, Route 1, P-0p/AM-0, CL-21i, FI-1 … FI-5 and the
  cleanup constraints are unchanged in substance.

## 8. Remaining decisions and next gate

Decided by Peter (recorded, unchanged): D-1 … D-7 and the lifecycle policy.
Still required, each later: Codex re-review and Peter's acceptance of the
cumulative R3 proposal (LC-1); Peter's U-9 restatement for
`/usr/bin/python3.14`; separate authorities for H-0G, OH-S2, OH-S4p, OH-S5,
H-1, CPP, CE, TC and WR; per-class host-byte dependency closures (LC-2,
RD-2); the sufficiency questions of proposal §15.

The `disposable-test-server.md` restriction banner still names the consumed R5
restriction; updating it was outside this assignment's three pointers and is
left to the controller.

**Next gate:** independent Codex re-review of the R3 proposal and this
handback, then Peter's recorded decision. Proposed reviewer focus: CK-9's
closed table and form-(2) reasoning (question 7); CK-3, NFW and SC-1 … SC-8
against every consumer, including SC-6's residual (questions 8, 9); the
`source_checkout` fields (10); RD-1 … RD-5 and LC-2 for R5 (18); and the three
carried questions now answered in text (11, 14, 16).

## 9. Final verification

Run after this handback was first written; only this section was edited
afterwards, and it changes no link.

| Check | Result |
|---|---|
| R3 proposal | SHA-256 `13310416888709e5756d8ed6be8aa61c29c30b4737617c407a1dae9e360f2fa1`, 131058 bytes |
| `Handover information` after | `917f0050efc274b0cd4d640b2479ef207da64fbe93e90dde530f1e8914d646f2` |
| `status.md` after | `6a866b7a21c06c1504edebb7a40afc1d1d53769a18504e23310aad0d132c0e89` |
| `implementation-plan.md` after | `1d95393d418a1fdb3ce16fbf67d8c57b531b807923f53c24ddfc2ccdd08d0189` |
| unchanged sources | R2 proposal `04a4abb4…b11ce105`, R2 handback `6c256a18…bdfc7d47`, DR1 proposal `403b2bc1…57582d60`, DR1 handback `0a42d926…398f3509`, R2 findings `70582c3c…0e53eda5`, R3 prompt `752e227e…121bd196`, R3 authority `d589cbc1…78d61833`, accepted design `a752a4b8…7e615d02`, `.agents/AGENTS.md` `28ce54ef…c7c84ad2`, `disposable-test-server.md` `6c6ea256…67ba47a1`: **all equal** to their start values |
| repository-relative links | proposal 6, this handback 4, `Handover information` 35, `status.md` 30, `implementation-plan.md` 30: **0 missing** |
| `git diff --check` | exit 0, no output |
| `git diff --no-index --check /dev/null ⟨file⟩` | proposal and this handback: exit 1 with no error lines (differs; no whitespace errors) |
| `git status --short` against the start snapshot | only the two new files added |

R3 remediation awaits independent Codex review; no host cleanup, H-0G, OH-S2 or later slice is authorized.
