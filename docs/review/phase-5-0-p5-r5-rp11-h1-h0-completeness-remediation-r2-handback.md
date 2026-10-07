# Handback — R5 H-0 remediation decisions, corrected HF-15 and disposable-Test lifecycle (R2)

Work ID: `C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR2-20261006-04`

Date: 2026-10-06

Executor: Claude Code, in `/opt/freedom-blades/platform` (local read-only
repository inspection plus the authorized documentation writes)

Prompt:
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-claude-prompt.md),
SHA-256 `c13d7177ba92bc7e24e2b19073e650d3f91f903a4279e5bbbbe2a3a9cf287169`,
11868 bytes. Recomputed before any work; equal to the authority's pin.

Authority:
[`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-authority.md)
(SHA-256 `f84d23306a9d4b1de2e5b6887ac9af6758d0e471566b4d297553555fc6ac1e16`)

Deliverable:
[`phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-proposal.md`](phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-proposal.md)

## 1. Terminal state: `R2 REMEDIATION READY FOR REVIEW`

The cumulative R2 proposal and this handback are written, and the three
authorized current-state pointers are updated. D-1 … D-7 and the lifecycle
policy are recorded as decided by the R2 authority. Every amendment, command
specification, gate and the cleanup/recreation sequence is proposed text,
unaccepted, awaiting independent Codex review. No host, network,
retained-path, credential or secret access occurred; no cleanup or other host
mutation was performed.

## 2. Requirements addressed

| Prompt item | Proposal section | Result |
|---|---|---|
| Record and apply D-1 … D-7 | §0 table, §2.1 traceability, §4 … §8 | Each decision is mapped to its amendment text and to the later gate that still applies. Decisions are stated as decided; prerequisites and review gates are preserved (§14) |
| 1. Correct HF-15 | §3, §4.3, §4.4, §11.3, §11.5 | (1) `lstat` and `listxattr` (no follow) on `/var/lib/rp11-capture`, `ENOENT` expected; (2) nearest existing ancestor from the literal's own components only, exactly `/var/lib`, no listing; (3) `findmnt --target /var/lib` and `df --output … -- /var/lib` in R5's exact c136/c137 forms, never against the absent path; (4) recorded explicitly as ancestor facts, not a stat of the parent; (5) CPP preflight and postcondition prove a non-symlink `ubuntu:ubuntu` `0700` directory with no xattr names, same `st_dev` as `/var/lib`, and no `mountinfo` mount point (closing the bind-mount case `st_dev` alone misses). The H-0G exit contract passes on `ENOENT` and lists each `HARD STOP` case. The defect is shown with R5's own records: c142 `findmnt` and c143 `df` both exited `1` on absent `/run/polkit-1` |
| 2. Apply D-7 completely | §8 | Three objects W/F/R defined. Fresh-checkout contract: retrieval CR-1 … CR-4 reuses R5's exact Git environment and `-c` controls (c014–c025); pre-use inventory CK-0 … CK-11 rejects root symlink substitution, unexpected owner/group, group/world-writable content, dirty/untracked/ignored content, a non-detached tree, commit mismatch, remotes, any config key beyond R5's four `core.*` keys, hooks, gitlinks, replace refs, grafts, alternates and unexpected `.git` entries; it adds CK-3/CK-9 and strengthens c022 with `--ignored`, weakening nothing. Normative amendments to HF-03, U-3, IA-12, §4.1.4, §4.1.5, TR-2, TR-10, `baseline.operator` (split into a per-slice `source_checkout`), A-2, §4.6.2 and the OH-S3 restatement scope. Slice matrix covers H-0G (repository-free) through the activation chain with work ID, freshness, retention and cleanup columns. States that R5 did not observe checkout ownership (its inventory covers its evidence directory; HF-03 says not observed) and that ownership is never inferred from creation by `ubuntu` |
| 3. Disposable-Test lifecycle | §12 | Policy recorded verbatim in substance (§12.1). Record-named candidate classes with their live dependency and closing gate (§12.2); gates LC-0 … LC-7 (§12.3); cleanup constraints: literal list only, forbidden targets, allowed parents, immediately-before identity check with `HARD STOP` on mismatch, removal scope, privilege, records (§12.4); recreation method and verification (§12.5); future retention (§12.6). **No executable cleanup command was written and no cleanup authority was created.** The review that must close before a cleanup prompt can enumerate targets is identified: LC-1 (independent acceptance of R2) for every class, and for R5's retained paths additionally the accepted H-0G composition review (or Peter's abandonment of R5) |
| 4. Preserve DR1 remediation | §4.1, §5, §6, §7, §9, §10, §13 | K-1 … K-15 and the candidate analysis, the HF-18 basis, the observed-facts table, the complete Role A–H inventory and the version-bound table are carried **verbatim** from DR1 by a scripted splice of DR1's unchanged lines (with five internal section references renumbered). P-0p/AM-0, HF-20/CL-21i, FI-1 … FI-5, R5 fact disposition, composition anchors (two added: A-9 `/var/lib` identity, A-10 its mount row), successor rows and the prohibition on treating a proposal or decision as execution authority are carried and updated |
| Required contents | §2, §4.2–§4.5, §5.2, §6, §7, §8.4, §9, §10.2, §11, §12, §14, §15 | decision traceability; exact normative amendments; corrected H-0G semantics; D-7 slice matrix; cleanup and recreation gates; complete R5 composition table; remaining prerequisites; 16 focused review questions |

## 3. Files changed

**Created by this assignment:**

| File | SHA-256 | Bytes |
|---|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-proposal.md` | `04a4abb4aa83c89b8e44479b1e56a12e423da9eb1967f8be0a9c85f9b11ce105` | 88131 |
| `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r2-handback.md` | this file (digest not self-reported) | — |

**Updated by this assignment** — pointer edits only, applied on top of
pre-existing uncommitted edits, which were preserved:

| File | Before | After | Change |
|---|---|---|---|
| `docs/review/Handover information` | `3de8ee58f4e24f53c7a51d8837758ad76485add6d05ec7092afe5065c9f41cc8` | `d58c735f3b864c9ca2fd67b7166f37bda58f74be3e73fa61ca7c81558100388a` | heading "R2 remediation authorized" → "R2 remediation returned for review"; one terminal-state paragraph; "R2 Claude prompt" relabelled "Consumed"; R2 proposal and handback links |
| `docs/project-management/status.md` | `a5289d83e8684ab203a26601f60f5f42c79642c2fd5f633260416673bd1137fe` | `e6033295d144c7ffa1ccc042e27681c9afc746e4359542773b9e86a23a7256b8` | the same three changes in the current-status section |
| `docs/implementation-plan.md` | `bf26df8b95d67a3a83649a47b4efb567493e18faf70959d3b9116072c29df849` | `04256bcd0fc83731b48e608aa20a877fdf866816b7911faf0c608c77fabdfd55` | the same three changes, in §20 only |

Unchanged, recomputed at the end: the DR1 proposal (`403b2bc1…7582d60`) and
handback (`0a42d926…f3509`); the accepted one-host design (`a752a4b8…7e615d02`);
`.agents/AGENTS.md` (`28ce54ef…7c84ad2`); `disposable-test-server.md`
(`6c6ea256…a47a1`). No source, test, infrastructure, manifest, change-log,
decision-register or archive file was touched. No migration, configuration or
deployment change, commit or push.

## 4. Pre-existing worktree changes, reported separately

Captured with `git status --porcelain=v1` before any edit (45 lines) and
preserved:

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
- **Untracked (34):** the four `*-through-2026-10-04-d3-r6-acceptance.md`
  snapshots and the R1 … R5, DR1, R2 and agent-client prompts, authorities,
  handbacks and reviews, including this assignment's prompt and authority.

The final `git status --porcelain=v1`, compared with the start snapshot,
differs only by the two new files.

## 5. Commands and checks run, with exact results

All commands were local and read-only, except the authorized writes.

| Check | Command (summary) | Result |
|---|---|---|
| prompt pin | `sha256sum`, `wc -c` on the prompt | `c13d7177…f287169`, 11868 bytes: **equal** to the authority |
| start snapshot | `git status --porcelain=v1` to a scratch file; `sha256sum` of the three pointer files | 45 lines; digests in §3 "Before" |
| required reading | `cat`/`sed`/`Read` of every item in the prompt's list (proposal §1) | done; no remote or retained path read |
| source digests | `sha256sum` of every DR1-cited source | all equal to DR1 §1, so DR1's line citations are still valid |
| anchor values | `grep`/`sed` of R5 Appendix B records c043, c046, c050, c052, c072, c096 and the c105 `/var/lib` row | values in proposal §10.2 confirmed, including `/var/lib` `root:root` `0755` `(2049, 97831)`, no xattr names |
| findmnt/df behaviour | `sed` of R5 c136, c137, c142, c143 | c142 `findmnt --target /run/polkit-1` exit 1, empty output; c143 `df … -- /run/polkit-1` exit 1, `No such file or directory` |
| DR1 splice | Python script substituting five DR1 line ranges into the template, then renaming four DR1-internal section references | all placeholders replaced; reference renames 1/1/1/1 |
| whitespace | `git diff --check` | exit 0, no output |
| whitespace, new proposal | `git diff --no-index --check /dev/null ⟨proposal⟩` | exit 1 with no error lines (files differ; no whitespace errors) |
| links | Python link extractor over the proposal, `Handover information`, `status.md`, `implementation-plan.md` and, after writing, this handback | before this handback existed the only missing target was this handback; final result in the row below |
| absent-parent scan | Python scan of every inline code span containing `findmnt` or `df` | in §4.3 and §11 (HF-15 and H-0G): **0** spans name `/var/lib/rp11-capture`; every such span names `/var/lib`. The four spans that name the parent are §3's quotation of DR1's defect (2) and CPP's postcondition (2), which runs only after the parent exists |
| Python 3.12 inventory | DR1's method: every `python3\.12|python ?3\.12|cpython ?3\.12|libpython3\.12|py3\.?12|cp312` line in the design, C11, D2, `launch.c`, `rp11_launch.py` and the manifest must be cited as `:line` in the proposal | **55 matches, 0 missing**. This check proves citation of each line number somewhere in the proposal, not semantic classification, which is carried from DR1 |
| decision carry-forward | `grep -c -F` per identifier on the proposal | D-1 9, D-1b 4, D-1c 5, D-2 9, D-3 4, D-3b 5, D-4 5, D-5 7, D-6 5, D-7 23; P-0p 12, AM-0 12, CL-21i 13, FI-1 13, Role A 8, OH-S4p 13, CK-0 6, CR-1 7, HF-03 12, IA-12 3, U-3 3, §4.1.4 3, OH-S3 7, OH-S5 10, LC-1 8, CPP 26 |
| scope scan | `grep` for `rm`, `rmdir`, `-delete`, `rmtree`, `unlink(`, `shutil`; `ssh`, `scp`, `rsync`, `sudo `; `hereby`, `is authorized`, `authorizes`; `push`; `password`, `token`, key material | deletion: only the policy phrase "discovery-and-delete loop" and the quoted draft term `rsync --delete` (being withdrawn). Remote/privilege: the quoted Role A `sudo -n` literals, P-0p's `sudo -n` text, and the same `rsync --delete` mention. Authority: only negations ("creates an authority or authorizes … nothing", "no … is authorized") and "only if Peter authorizes it" for recreation option (b). Push: the H-0G prohibition list. Secrets: only "password database" (HF-03 wording). **No executable cleanup command, no grant of authority, no secret or player data** |
| end snapshot | `git status --porcelain=v1` compared with the start | only the two new files added |

Final checks over all five files: see §9.

## 6. Checks not run

- No application test suite, formatter, linter, type checker or build: the
  assignment is documentation-only and forbids them.
- No network, no `oracle-test` access, no access to any retained path
  (`/var/tmp/p5-r5-rp11-*`, `/var/tmp/p5-r5-fresh-*`, agent-client evidence)
  and no access to `/opt/freedom-blades/platform` on `oracle-test`. Every host
  fact is cited from durable repository handbacks.
- No upstream source (CPython, glibc, systemd, polkit, util-linux, Git) was
  read. In particular, the `findmnt`/`df` behaviour is cited from R5's
  recorded c142/c143 results, not from source; the CK-9 `.git` entry set is a
  proposal to be fixed by review (question 13), not an observed fact.
- Whether each record-named retained path in proposal §12.2 actually exists
  was not determined; the proposal assigns that to the cleanup-enumeration
  slice CE.
- No Markdown renderer was run.

## 7. Security implications

- **HF-15.** The corrected procedure can no longer pass on a false premise:
  ancestor facts are labelled as such, and the parent's same-filesystem and
  non-mount properties are proved only at CPP, after creation, with a
  `mountinfo` check that closes the bind-mount gap of a pure `st_dev` test.
- **D-7.** The uncontrolled workspace leaves the RP-11 trust path entirely.
  Each source-consuming slice now verifies ownership, modes, Git state and
  configuration of its own checkout before use, so a planted hook, config
  key, replacement object, alternates file, ignored `.pyc` or symlinked root
  stops the slice. The `baseline` split keeps H-2's byte-equality meaningful
  across separate checkouts.
- **Lifecycle.** The cleanup design forbids broad roots and inference, refuses
  credential, runtime, agent-tool, PostgreSQL and capture paths even if
  listed, and stops on the first identity mismatch. No deletion can occur
  under this assignment or its policy record.
- **Carried.** HF-18 withdrawal does not weaken C-3, E-1 … E-3, S-8 or the
  polkit/CP/A-2 boundary; Route 1 still requires the launcher rebuild and
  D9 re-review; `unreadable` is never absence; no grant can be linked before
  CL-21i is accepted.

## 8. Remaining decisions and next gate

Decided by Peter (recorded): D-1, D-1b, D-1c, D-2, D-3, D-3b, D-4, D-5, D-6, D-7
and the lifecycle policy. Still required, each later: Codex review and Peter's
acceptance of R2 (LC-1); Peter's U-9 restatement for `/usr/bin/python3.14`;
separate authorities for H-0G, OH-S2, OH-S4p, OH-S5, H-1, CPP, CE, TC and WR;
per-class dependency closures (LC-2); the review questions of proposal §15.

The `disposable-test-server.md` restriction banner still names the consumed R5
restriction; updating it was outside this assignment's three pointers and is
left to the controller.

**Next gate:** independent Codex review of the R2 proposal and this handback,
then Peter's recorded decision. Proposed reviewer focus: HF-15 exit contract
and CPP postcondition (questions 1–4); the D-7 CK contract and `baseline`
split (5–7, 13, 14); the cleanup removal scope and R5's closing gate (15, 16);
and the carried DR1 items (8–12).

## 9. Final verification

Run after this handback was first written; only this section was edited
afterwards, and it changes no link:

| Check | Result |
|---|---|
| repository-relative links | proposal 4, this handback 3, `Handover information` 30, `status.md` 25, `implementation-plan.md` 25: **0 missing** |
| `git diff --check` | exit 0, no output |
| `git diff --no-index --check /dev/null ⟨this handback⟩` | exit 1 with no error lines (differs; no whitespace errors) |
| `git status --porcelain=v1` against the start snapshot | only the two new files added |

R2 remediation awaits independent Codex review; no host cleanup, H-0G, OH-S2 or later slice is authorized.
