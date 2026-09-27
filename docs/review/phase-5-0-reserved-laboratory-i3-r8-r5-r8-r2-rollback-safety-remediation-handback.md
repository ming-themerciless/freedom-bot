# Claude remediation handback — C-P5.0-LAB-I3-R8-R5; the R8-R2 rollback instruction withdrawn as unsafe — 2026-09-22

Author: Claude (implementing agent for C-P5.0-LAB-I3-R8-R5).
Authorization: the bounded **repository-only** assignment recorded at the head
of `docs/review/Handover information`, accepted by Peter Duscha and explicitly
assigned to Claude on 2026-09-22. Codex remains the Independent Technical,
Security and Evidence Reviewer and did not perform this remediation.

**No command of any kind was issued to `oracle-test`.** There was no SSH, no
synchronization, no host inspection, no verifier invocation, no suite, no
database access, and no read, `stat` or change of the three protected `/tmp`
evidence artifacts. No source, test, hook, manifest, generated artifact,
migration, schema or configuration file was changed. **No secrets scan was run
and no command expected to engage a secrets guard was issued.** No guard, hook
or rule was altered, and **no guard or tool refused any call during this pass**.
**No destructive Git command was run, attempted or recommended**, and **no file
was reverted, deleted or restored**.

**Nothing is closed by this pass.** **LAB-I3-R8-R2-ROLLBACK-1 remains Open,
Important** for independent Codex re-review. The five findings Peter Duscha
closed on 2026-09-22 — LAB-I3-R8-R3-ROLLBACK-1, LAB-I3-R8-R3-WORDING-1,
LAB-I3-R8-R2-GUARD-1, LAB-I3-R8-R2-COUNT-1 and LAB-I3-R8-AGGREGATE-1 — stand
exactly as decided; this pass neither disposes of nor reopens any of them.
PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**.
I3 remains performed but unconfirmed and not closed. V7 remains excluded, V8
and V10 remain unperformed, `plan.is_executable=False`, and Package 5.0 remains
**not ready**.

---

## 1. The finding addressed

### 1.1 LAB-I3-R8-R2-ROLLBACK-1 — Important, unsafe rollback instruction, Open

The R8-R2 handback §8.1 read:

> To revert: `git checkout --` the eight modified documents and delete the one
> added handback, … That restores the exact pre-remediation state, which was 92
> paths with `git diff --check` clean.

This is the same defect R8-R4 corrected in R8-R3, and R8-R4's §6 scope
observation had already reported it without editing it. The repository bears
the finding out. The measured basis is in §6.

**The count was wrong as well as the command.** R8-R2 §5 lists **nine** edited
documents plus the one new handback. §8.1's "eight" matched neither figure.

**None of the nine was created by R8-R2.** Every one already carried
earlier-pass, uncommitted work before R8-R2 began. **Seven** are tracked and
modified. `git checkout --` restores a tracked file's `HEAD` version, and in the
committed version of each of those seven the strings `LAB-I3-R8`, `R8-R1` and
`R8-R2` occur **zero** times. Against `HEAD` (`2fb1d6f`) the seven stood at
**+8,659 / −18 lines** when this pass began. The command would therefore
discard the **entire uncommitted R8 evidence chain**, not only R8-R2's hunks.
That chain now includes R8-R3, R8-R4 and Peter Duscha's 2026-09-22 dispositions
as well as R8 through R8-R2, and every other uncommitted change in those files
would go with it.

**Two of the nine are untracked.** The R8 and R8-R1 handbacks are untracked
files. `git checkout --` does not restore an untracked path; Git reports that
the pathspec did not match any file known to it. Their pre-R8-R2 bytes have
**no Git baseline at all**. This pass did not run the command, so it makes no
claim about whether Git would abort the whole invocation or act on the
remaining paths. Neither outcome is the pre-R8-R2 state.

**The file R8-R2 added is no longer R8-R2's alone.** Before this pass it already
carried R8-R3's dated erratum and R8-R3's in-place corrections to §1, §6, §6.1,
§7, §8.1, §10 and §11, which is nine references to R8-R3 or R8-R4. Those
corrections record the procedural violation and the count correction that the
maintainer's 2026-09-22 dispositions rest on. Deleting the file would erase
them, so **deletion is not an R8-R2-only reversal either**. R8-R4 could call the
deletion of its own added file unambiguous, but that does not carry over to
R8-R2's file.

**The exact-restoration claim was therefore unsupported.** The command cannot
reconstruct the pre-R8-R2 working tree. The instruction and the claim are
**withdrawn**.

## 2. What was done

This pass made documentation corrections only. Each is a **dated erratum** or a
**clearly marked in-place correction**, and every withdrawn sentence stays
visible instead of being rewritten away.

**A second dated erratum was added at the head of the R8-R2 handback.** It
records the finding, its measured basis and the four reasons above. It gives the
explicit instructions **do not run that command, and do not delete this
handback as a rollback step**, and it states that it changes no measured value
or evidence claim and disposes of nothing.

**R8-R2 §8.1's rollback paragraph was replaced under a marked correction.** The
withdrawn text is quoted in place. The replacement separates four things:

* **what is true:** the changes are documentation only, nothing is committed,
  and no host or migration state is involved;
* **what rollback is available:** only the R8-R2-specific hunks and its one
  added file, through a **reviewed, remediation-specific reverse patch or
  equivalent exact reconstruction preserving every pre-existing change**, and
  never a checkout, restore, reset, whole-file deletion or whole-file
  restoration;
* **why even that is no longer mechanical:** later passes have annotated and
  quoted R8-R2's text, the maintainer's dispositions rest on it, and the added
  file carries later errata; and
* **what is not available:** the exact pre-R8-R2 bytes.

It states plainly that **no exact automated rollback can be offered or claimed**
and that **any** rollback of R8-R2 **requires maintainer coordination**.

**R8-R2 §5 was annotated, not altered.** Its rows remain correct as a record of
what was changed. A dated note records the count and tracking state they never
stated and §8.1 misstated: nine documents, seven tracked, two untracked, all
already carrying earlier-pass work.

**R8-R2 §8.2 item 1 was corrected by an appended note.** Its "should be reverted
per §8.1" pointed at the withdrawn instruction. The note states that it confers
no authority to run it, and that any reversal is governed by the corrected §8.1.
The original sentence is unaltered.

**R8-R2 §11 received a dated update** recording the new finding as Open.

**The controlled documentation was reconciled only as far as recording this
finding requires:** the handover, plan §20, the restriction banner and the four
project-management registers.

## 3. The line this remediation does not cross

* **The withdrawn `git checkout --` command was not executed**, in whole or in
  part, on any path.
* **No file was reverted, deleted, restored or moved.** The R8-R2 handback was
  corrected in place, not deleted.
* **No reverse patch was manufactured**, whether from assumptions or otherwise,
  and none is proposed. Constructing one is maintainer-coordinated work.
* **No destructive Git command was run, attempted or recommended.** Every Git
  command used was read-only; §6 lists them.
* **No secrets scan was run**, and no command expected to engage a secrets guard
  was issued. The consistency checks in §6 were plain `grep` and `awk` searches
  for finding IDs, withdrawn phrases, R8-chain strings and hash prefixes, over
  `docs/` only.
* **No guard, hook, `.claude/settings.json` entry or rule was read for
  modification, altered or proposed for alteration.**
* **No guard or tool refused any call during this pass.** Had one refused, the
  pass would have stopped immediately with no altered attempt, and the refusal
  would be reported here.
* **No protected artifact content was added, inspected or inferred.** This
  handback refers to the three protected `/tmp` artifacts and their restriction.
  It states nothing about their contents.
* **No measurement of the R8 evidence was made or claimed.** The measurements in
  §6 are of this repository's own Git state, made to establish whether the
  withdrawn rollback instruction was safe. None of them touches an aggregate, a
  digest or any recorded value.
* **The repository-wide cleanup was not broadened into.** Older handbacks with
  `git checkout --` guidance of the same shape were not edited (§6, scope
  observations).
* **This pass closes nothing.**

## 4. Files changed

| File | Tracking | Change |
|---|---|---|
| `docs/review/phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md` | untracked | second dated erratum at the head; **§8.1 rollback paragraph withdrawn and replaced** under a marked correction, with the withdrawn text quoted in place; **§5 annotated** with the count and tracking state; **§8.2 item 1** given a correcting note; **§11** dated update. No other section altered |
| `docs/review/phase-5-0-reserved-laboratory-i3-r8-r5-r8-r2-rollback-safety-remediation-handback.md` | untracked, **new** | this handback |
| `docs/review/Handover information` | tracked | the R8-R5 assignment block marked consumed, with its text unaltered; new active state block; the R8-R4 state block retitled superseded, with a forward-pointing note |
| `docs/implementation-plan.md` | tracked | new §20 current action; the prior action retained as superseded, with a note |
| `docs/operations/disposable-test-server.md` | tracked | banner note: no host command, no secrets scan, nothing reverted, restriction unchanged |
| `docs/project-management/status.md` | tracked | new current status; prior status retained as superseded, with a note |
| `docs/project-management/raid-register.md` | tracked | **LAB-I3-R8-R2-ROLLBACK-1** entry added — Open, Important. There was previously no dedicated entry, only a mention in the dispositions header |
| `docs/project-management/decision-register.md` | tracked | new pending decision on what, if anything, to roll back from R8-R2 |
| `docs/project-management/change-log.md` | tracked | new append-only row **C-P5.0-LAB-I3-R8-R5**, superseding the R8-R2 row's §8.1 rollback guidance |

**Migrations added: none.** No source, test, hook, manifest, generated artifact,
migration, schema or configuration file appears in that list, and none was
changed. Seven of the nine paths are tracked and modified, and two are
untracked. The tracking state is stated because assuming it is what produced
this finding.

## 5. Requirements addressed

1. **Reading and preservation.** I read `.agents/AGENTS.md` completely. I also
   read the implementation-plan reading map and §§0, 12 (including the Package
   5.0 row and the Phase 5 package rules), 13, 16, 17 and 20; this handover's
   active prompt, the maintainer decisions and the prior state blocks; the
   disposable-server restriction banner; the R8, R8-R1, R8-R2, R8-R3 and R8-R4
   handbacks; the 2026-09-22 decision record; and the status, RAID, decision and
   change registers. I inspected `git status` before and after. **Every
   unrelated and earlier-pass change was preserved**; none was touched,
   reclassified or reverted.
2. **Scope verified; the rollback section corrected.** The exact scope and
   tracking state of the documents in R8-R2 §5 were verified read-only (§6)
   without changing any of them for that purpose. The correction was made by
   dated erratum plus a marked in-place correction. Both the `git checkout --`
   instruction and the exact-restoration claim are **withdrawn**. The command
   was **not executed**, the handback was **not deleted**, **no file was
   reverted**, and **no reverse patch was manufactured**.
3. **Truthful rollback guidance stated.** Only the R8-R2-specific hunks and the
   file R8-R2 added may be reversed, through a reviewed remediation-specific
   reverse patch or equivalent exact reconstruction preserving every
   pre-existing change. The exact pre-R8-R2 bytes are **not** independently
   available, and the correction **says so plainly** and **requires maintainer
   coordination** instead of claiming exact automated rollback.
4. **Controlled documentation reconciled only as needed.** The nine paths in §4
   were reconciled by dated erratum, marked correction or forward-pointing
   supersession note wherever historical text must stay visible. **No
   operational evidence was rewritten, no project rule altered, no measured
   value changed, and no R8-chain evidence claim strengthened.** The pass was
   not broadened into a repository-wide rollback-guidance cleanup.
5. **This dated handback.** **LAB-I3-R8-R2-ROLLBACK-1 is left Open,
   Important** for Codex re-review. No other finding, I3 or package gate is
   closed or disposed of.

## 6. Checks run

**Interpreter and host.** Local `python3` 3.12.3 in the repository workspace
`/opt/freedom-blades/platform`, used only for one heredoc `python3 -` script.
That script inserted one table row into `docs/project-management/change-log.md`
after asserting the two neighbouring lines it expected. This was **not** the
`oracle-test` interpreter, and **no host was contacted**. All other edits were
exact string replacements in documentation files.

**Exact commands.** All were read-only except that one insertion:

* `git rev-parse --short HEAD` and `git branch --show-current`;
* `git status --porcelain`, counted with `wc -l` and `grep -c`;
* `git status --porcelain -- <path>` for each of the ten paths in R8-R2 §5;
* `git diff --check`;
* `git diff --numstat -- <path>` for the seven tracked documents, before and
  after;
* `git show HEAD:<path> | grep -c` for `R8`, `LAB-I3-R8`, `R8-R1` and `R8-R2`
  in each of those seven;
* `git stash list`, `git stash show --name-only stash@{0}` and
  `git log -1 --format` on that stash ref;
* `find docs -name '*.bak' -o -name '*.orig' -o -name '*~'`;
* `grep -n`/`grep -rn`/`grep -rno` searches over `docs/` for the finding ID,
  the withdrawn phrases, `checkout`, R8-chain strings and six hash prefixes; and
* `sed -n` and `awk` ranges over the documents read.

| Check | Result |
|---|---|
| `git diff --check` | clean, before and after |
| Working-tree path count, before and after | **96 paths — 34 modified, 62 untracked** before; **97 paths — 34 modified, 63 untracked** after. The one added path is this handback. No path changed classification |
| Tracking state of the ten paths in R8-R2 §5 | **seven tracked and modified**; **three untracked**: the R8 and R8-R1 handbacks, which R8-R2 edited, and the R8-R2 handback, which R8-R2 added. §5 lists **nine** edited documents, not the "eight" §8.1 named |
| Divergence of the seven tracked documents from `HEAD` (`2fb1d6f`) before this pass | **+8,659 / −18 lines**: handover 4,685/0, plan 696/7, restriction banner 725/4, status 905/6, RAID 937/1, decision register 669/0, change log 42/0 |
| R8-chain content at `HEAD` in those seven | `LAB-I3-R8`, `R8-R1` and `R8-R2` match on **zero** lines of each committed version. In the working tree before this pass, `R8-R2` matched on 5–46 lines per document and `R8-R3`/`R8-R4` on 3–50 lines. That is later-pass content a checkout would also erase. `grep -c` counts matching lines |
| Later-pass content in the file R8-R2 added | **9** lines referencing R8-R3 or R8-R4 before this pass. Deletion would erase them |
| Independent availability of the pre-R8-R2 bytes | **none found.** There is no `.bak`, `.orig` or `~` file under `docs/`. The one stash, `stash@{0}` ("On main: temp before rebase", 2025-09-15), touches `.env.example`, `music.py` and `requirements.txt`, is unrelated, and was inspected read-only by name listing only |
| No committed line removed by this pass | deletions against `HEAD` are **unchanged** in all seven tracked documents after the pass: 0, 7, 4, 6, 1, 0, 0. Additions rose by 73, 35, 15, 37, 41, 26 and 1 lines respectively |
| Withdrawn-instruction sweep in the R8-R2 handback | every remaining occurrence of `git checkout --`, "eight modified documents", "exact pre-remediation state" and "reverted per §8.1" is inside the new erratum, quoted as withdrawn text, or part of a prohibition or correcting note. **None stands as live guidance.** The "92 paths" in §8's table is R8-R2's historical measurement and stands |
| Spread of the R8-R2 instruction into controlled summaries | `checkout` searched in the handover, plan, banner and four registers. **None** carried R8-R2's rollback guidance, so only the R8-R2 handback needed the withdrawal |
| Finding-ID spelling and state | `LAB-I3-R8-R2-ROLLBACK-1` occurs in nine documents with no variant spelling. **No occurrence is on a line stating it Closed**; every touched document states Open, Important |
| Preserved-evidence check in the R8-R2 handback | the lines carrying `c358ea8b`, `4d829dc6`, `f4120970`, `ce275fd3`, `66855575` and `206e40b2` all lie outside the regions this pass added. No measured value is in any added text except the Git-state figures this pass measured itself |
| Historical-record check | no R6 or R8-chain operational observation was edited. Every correction is an added erratum, an added note, a quoted-and-withdrawn passage or a forward-pointing supersession note |
| Cross-document link targets | this handback's filename is linked from `docs/review/`, `docs/project-management/`, `docs/operations/` and `docs/implementation-plan.md` at the relative depth each uses. Resolution was checked after this file was written |

**Scope observations.** These are reported, not acted on, and they are not a
claim that nothing else exists:

* **Older handbacks.** R8-R4 §6 reported live `git checkout --` rollback
  guidance in six older handbacks outside the R8 chain. This pass did **not**
  re-sweep or edit them, because the assignment limits it to this finding. They
  remain as R8-R4 described them.
* **R8-R3 §8.2 item 1** still says "reverted per §8.1". That now points at
  R8-R3's already-corrected §8.1, not at live unsafe guidance. It was not
  edited.
* **Precision of an R8-R4 measurement statement.** R8-R4's handback and the
  documents recording its finding — the R8-R3 handback's erratum, the R8-R4
  handover state block, superseded plan §20 and status blocks, the R8-R3 RAID
  entry and the R8-R4 change-log row — say that `R8`, `R8-R1` and `R8-R2` occur
  zero times at `HEAD`. For the R8-chain
  strings R8-R4 actually counted (`R8-R1`, `R8-R2`, `LAB-I3-R8`) that holds, and
  this pass reproduced it. Bare `R8` does occur at `HEAD`, inside unrelated
  older designations such as `R8-A`, `R8-B` and `R8-D`; for example, the
  committed `status.md` has 21 such lines. The conclusion is unaffected. The
  wording belongs to closed findings and was **not** edited. This pass cites
  the specific strings.
* **Change-log table structure.** The maintainer-recorded row
  C-P5.0-LAB-I3-R8-D1 sits **between the header row and the `|---|` delimiter
  row**. In GitHub-flavoured Markdown that stops the table rendering as a table.
  This pass inserted its own row directly **below** the delimiter, so it adds
  nothing to the problem, and it did **not** move the maintainer's row. The
  repair is for the maintainer.

**No guard or tool refused any call during this pass**, so there is no refusal
to report under the assignment's stop rule.

## 7. Checks not run, and why

| Not run | Why |
|---|---|
| **Any secret-indicator scan of this or any diff** | **Deliberately not run.** The assignment forbids a secrets scan or any command expected to engage a secrets guard. Reviewing this diff for secrets by scan is recorded as **not run**, not as passed. What is established instead, without any scan: `git status` and `git diff --numstat` show the change set is documentation only, and every added line is prose about the R8 evidence chain and this repository's Git state, read in full while writing it. That is not a substitute check |
| Both pytest suites and the Node contract tests | Out of scope. This remediation is documentation only, changes no source, test or artifact, and the assignment authorizes no suite. **No suite figure is offered, cited or claimed** |
| Any command on `oracle-test` | **Expressly prohibited.** No host action of any kind is authorized |
| Any measurement of either aggregate or of any recorded digest | Not required by the finding and not performed. **No measurement of the R8 evidence** is made or claimed |
| Execution of the withdrawn `git checkout --` command, or of any revert, reset, restore, deletion or reverse patch | **Expressly prohibited, and the subject of the finding.** Consequently Git's behaviour on the mixed tracked/untracked path list is stated from Git's documented pathspec rule, not observed |
| A docs-wide re-sweep of older handbacks' rollback guidance | Outside the assignment's bounded scope. See the §6 scope observations |
| Formatter, linter, type checker | No code changed |
| `python3 .claude/hooks/test_guards.py` | **Not run and not applicable.** No guard or hook was changed |

## 8. Repository state

| | |
|---|---|
| Branch / `HEAD` | `docs/platform-plan` / `2fb1d6f` |
| Working tree before this remediation | **96 paths — 34 modified, 62 untracked**; `git diff --check` clean. The difference from R8-R4's recorded 95 is the maintainer's untracked decision record `project-review-2026-09-22-r8-r4-acceptance-and-r8-dispositions.md` |
| Working tree after this remediation | **97 paths — 34 modified, 63 untracked**; `git diff --check` clean. The one added path is this handback |

Unrelated and earlier-pass working-tree changes were inspected and
**preserved**; none was touched, reclassified or reverted. No commit, push,
rebase, amend, reset, checkout, restore or history rewrite was performed or
attempted.

## 8.1 Security, configuration, deployment and rollback

**Security implications.** No authentication, authorization, privacy, migration
or production path is touched. **No credential or protected artifact was read,
inspected, `stat`ed, written, moved, modified or reused, and no secret value,
credential, connection string or key was disclosed.** This handback *refers* to
the three protected `/tmp` evidence artifacts and to the restriction governing
them, as any record of a restricted pass must. **Referring to a restriction is
not access to what it protects.** No artifact content is stated, inspected or
inferred anywhere in this document. **No secrets scan was run and no command
expected to engage a secrets guard was issued.**

The correction *weakens* a claim in an evidence document by withdrawing an
unsafe instruction and an unsupported restoration claim. It strengthens no
claim, relaxes no control and advances no state. Its security relevance is
operational safety: live guidance that would have destroyed the uncommitted
evidence record no longer stands.

**Configuration and deployment changes: none.** No configuration file,
environment contract, `.env.example` entry, migration, schema or deployment unit
is in the change set. Nothing needs to be deployed.

**Rollback and recovery.** Every change this pass made is documentation in the
working tree and **nothing is committed**. No data migration, no recovery
procedure, no configuration and no host state is involved.

The following is stated with the care the finding demands and is **not** an
exact automated restoration:

* **The one file this pass added** is this handback. It carries no other pass's
  content, so deleting it removes only R8-R5 bytes. On its own, however, that
  would leave the links to it in the eight other documents dangling, so it is
  **not a complete rollback**.
* **The eight other documents this pass edited already carried earlier-pass,
  uncommitted work**, including the entire R8 chain and the maintainer's
  dispositions. **`git checkout --`, `git restore`, `git reset`, deletion of a
  whole file and any other whole-file restoration must not be used on them.**
  Seven are tracked, and their `HEAD` versions predate the whole R8 chain. One,
  the R8-R2 handback, is untracked and has no Git baseline at all.
* Reversing this pass's edits to those eight therefore requires a **reviewed,
  remediation-specific reverse patch or an equivalent exact reconstruction that
  preserves every pre-existing change**. **The exact pre-R8-R5 bytes are not
  independently available** in this repository: not at `HEAD`, not in any
  stash, snapshot or backup, and not at all for the untracked file. **This pass
  took no pre-pass snapshot.** **No exact automated rollback is offered or
  claimed.** Any such reversal **requires maintainer coordination**: Peter
  Duscha decides what is reversed, and the patch is constructed and reviewed
  against this pass's changes, not assumed.
* What makes a reviewed reverse patch feasible is that this pass's edits are
  additive prose in identifiable regions. Deletions against `HEAD` are unchanged
  in every tracked file (§6). The regions are:
  * in the R8-R2 handback, the second erratum block, the §5 note, the §8.1
    rollback correction, the §8.2 item 1 note and the §11 update;
  * in the handover, one "consumed" note, one new state block and one retitled
    and annotated heading;
  * in plan §20, one new current action and a retitled, annotated prior action;
  * one banner paragraph;
  * in the status register, one new status and a retitled, annotated prior one;
  * one new RAID entry, one new decision-register entry and one change-log row.

  Being able to list the regions does not make a blind restoration safe.

**Requirements proposed but not implemented: none.** The assignment's five items
are all implemented. Nothing was deferred. No follow-up work is proposed beyond
the independent re-review and any maintainer rollback decision.

## 8.2 Assumptions, stated as assumptions

1. **Authority.** The prompt at the head of `docs/review/Handover information`
   carries an explicit acceptance and assignment line above its retained draft
   banner, and the maintainer instructed the operator in session to implement
   it. The operator treated the two together as the required acceptance and
   assignment. The prompt's closing sentence says LAB-I3-R8-R2-GUARD-1 "remains
   Open, Blocking". The later maintainer note in the same block says that
   sentence is superseded by the 2026-09-22 closure, and the operator followed
   the maintainer note. That finding was neither reopened nor re-disposed here.
2. **What "the R8-R2-specific hunks" denotes.** The corrected rollback statement
   refers to them without enumerating them. Enumerating them exactly would
   require reconstructing the pre-R8-R2 tree, which is the very thing that is
   not independently available. It would also require separating them from the
   R8-R3, R8-R4 and R8-R5 annotations now interleaved with them. That is
   maintainer-coordinated work, not an output of this pass.
3. **Scope of "the controlled documentation needed".** The operator read this as
   the nine paths in §4 and no further. The R8 and R8-R1 handbacks were **not**
   edited, because the finding does not concern their text. Neither were the
   R8-R3 and R8-R4 handbacks, which concern closed findings.
4. **Treatment.** Historical text was retained and annotated, and withdrawn text
   quoted in place, following the repository's erratum-not-rewrite convention
   that the assignment's item 4 directs. Two headings, in the handover and the
   status register, were retitled from "Active"/"Current" to "Superseded", as
   the R8-R2 through R8-R4 passes did.

## 9. Remaining uncertainty

1. **Whether anything should be rolled back from R8-R2 at all** is undecided and
   is Peter Duscha's decision. This pass records that no exact automated
   rollback exists. It does not propose, construct or recommend a reversal.
2. **The exact pre-R8-R2 and pre-R8-R5 bytes are unrecoverable from this
   repository.** That is stated as fact. An exact reconstruction would need a
   source this repository does not contain.
3. **Git's behaviour on the withdrawn command's mixed path list**, meaning
   whether it would abort entirely or act on the tracked paths, is not observed,
   because running it is prohibited. The finding does not depend on it, since
   neither outcome is the pre-R8-R2 state.
4. **Older handbacks outside the R8 chain** still carry `git checkout --`
   guidance of the same shape, as R8-R4 reported. Whether
   LAB-I3-R8-R2-ROLLBACK-1 generalizes to them is for Codex and Peter Duscha.
5. The **cause of the historical aggregate divergence and the R6 calculation**
   remain unknown, as accepted in the 2026-09-22 dispositions, and are untouched
   here.
6. Neither aggregate is approval. A digest is review input, never an I3
   confirmation and never authority for `--execute`.

## 10. Proposed independent reviewer focus

1. **Whether the R8-R2 rollback instruction is now unambiguously withdrawn**
   everywhere it appears, and whether any residue survives as live guidance,
   including through §8.2 item 1's cross-reference.
2. **Whether the replacement rollback statement is truthful for this tree.** In
   particular, check the added point that deleting the R8-R2 handback is no
   longer an R8-R2-only step because it carries R8-R3's errata.
3. **Whether this handback's own §8.1 avoids the defect it corrects.** It is
   written to the same standard it imposes, and that should be checked rather
   than assumed. Check especially the claim that deleting this handback alone is
   not a complete rollback.
4. **Whether the measured basis in §6 supports the finding as stated.** The
   points to check are the nine-not-eight count, the seven-tracked/two-untracked
   split, the +8,659 / −18 divergence, the zero R8-chain strings at `HEAD`, the
   later-pass content in the R8-R2 handback, and the absence of any independent
   snapshot.
5. **Whether erratum and marked correction is the right treatment**, and whether
   any historical operational statement was rewritten rather than annotated.
6. **That nothing was reverted, deleted or restored**, that no destructive Git
   command was run or recommended, that no reverse patch was manufactured, and
   that §7 reports the secrets scan as not run.
7. **The four scope observations in §6.** None was acted on. The bare-`R8`
   precision point and the change-log delimiter placement may warrant
   maintainer attention.

## 11. Disposition

**C-P5.0-LAB-I3-R8-R5 is consumed by this handback.** The authority ends here
and reached nothing outside the repository.

**LAB-I3-R8-R2-ROLLBACK-1 remains Open, Important**, for independent Codex
re-review, and the operator closes nothing. The five findings closed on
2026-09-22 stand as decided. PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2
remain **Open, Blocking**. I3 remains **performed but unconfirmed and not
closed**, and its closure remains Peter Duscha's decision. V7 remains excluded
and absent, V8 and V10 remain unperformed, `plan.is_executable=False`, Package
5.0 remains **not ready**, LAB-SECRETS-1 remains Open, Low, and LAB-V6-P2
remains deferred.

**No action on `oracle-test` is authorized.**
**Next step: independent Codex technical, security and evidence re-review, and
Peter Duscha's decision on whether any R8-R2 rollback is wanted.**
