# Claude remediation handback — C-P5.0-LAB-I3-R8-R4; the R8-R3 rollback instruction withdrawn as unsafe and its protected-artifact wording corrected — 2026-09-22

Author: Claude (implementing agent for C-P5.0-LAB-I3-R8-R4).
Authorization: the bounded **repository-only** assignment recorded at the head
of `docs/review/Handover information`, accepted by Peter Duscha and explicitly
assigned to Claude on 2026-09-22. Codex remains the Independent Technical,
Security and Evidence Reviewer and did not perform this remediation.

**No command of any kind was issued to `oracle-test`.** No SSH, no
synchronization, no host inspection, no verifier invocation, no suite, no
database access, and no read, `stat` or change of the three protected `/tmp`
evidence artifacts. No source, test, hook, manifest, generated artifact,
migration, schema or configuration file was changed. **No secrets scan was run
and no command expected to engage a secrets guard was issued.** No guard, hook
or rule was altered, and **no guard or tool refused any call during this pass**.
**No destructive Git command was run, attempted or recommended**, and **no file
was reverted, deleted or restored**.

**Nothing is closed.** **LAB-I3-R8-R3-ROLLBACK-1 is Open, Important** and
**LAB-I3-R8-R3-WORDING-1 is Open, Optional**, both for independent Codex
re-review. LAB-I3-R8-R2-GUARD-1 remains **Open, Blocking**, pending Peter
Duscha's disposition; LAB-I3-R8-R2-COUNT-1 remains Open, Important;
LAB-I3-R8-AGGREGATE-1 remains Open, Important; PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**; I3 remains performed but
unconfirmed and not closed; V7 remains excluded; V8 and V10 remain unperformed;
`plan.is_executable=False`; Package 5.0 remains **not ready**.

---

## 1. The findings addressed

### 1.1 LAB-I3-R8-R3-ROLLBACK-1 — Important, unsafe rollback instruction, Open

The R8-R3 handback §8.1 read:

> To revert: `git checkout --` the ten modified documents listed in §5 and
> delete the one added file … That restores the exact pre-remediation state,
> which was 93 paths with `git diff --check` clean.

Codex found that unsafe, and the repository bears the finding out completely.
The measured basis is in §6; the substance is this.

**The ten documents were not created by R8-R3.** Every one already carried
earlier-pass, uncommitted work — the R8, R8-R1 and R8-R2 records among it.
`git checkout --` restores a **tracked file's `HEAD` version**, which on these
files is a version predating the entire R8 chain. Measured against `HEAD`
(`2fb1d6f`), the seven tracked documents stand at **+8,164 / −18 lines**, and
the strings `R8`, `R8-R1` and `R8-R2` occur **zero times** in every one of their
committed versions. The command would therefore **discard the whole uncommitted
R8 evidence chain** along with R8-R3's own hunks, plus any other uncommitted
change in those files.

**Three of the ten are untracked, and the command does not operate on them at
all.** The R8, R8-R1 and R8-R2 handbacks are untracked files, not modified ones;
R8-R3 §5 described all ten as modified documents, which was imprecise.
`git checkout --` on an untracked path fails with `did not match any file(s)
known to git`. Their pre-R8-R3 bytes have **no git baseline whatsoever** and are
not recoverable from the repository.

**The exact-restoration claim was therefore unsupported.** The command cannot
reconstruct the pre-R8-R3 working tree, and would not return it to 93 paths; it
would produce a tree missing the uncommitted R8 evidence chain entirely. The
instruction and the claim are **withdrawn**.

### 1.2 LAB-I3-R8-R3-WORDING-1 — Optional, internally inconsistent security wording, Open

R8-R3 §8.1 said that no credential or protected file was "read, written **or
referenced**". The handback necessarily *refers* to the three protected `/tmp`
evidence artifacts and to the restriction governing their handling — any record
of a restricted pass must — so as written the absolute claim **contradicted the
document containing it**.

The supported fact is narrower and is unchanged: none was **read, inspected,
`stat`ed, written, moved, modified or reused**, and **no secret value,
credential, connection string or key was disclosed**. **Referring to a
restriction is not access to what it protects.** The "or referenced" claim is
**withdrawn**; the no-access record is preserved in full and is **not weakened**
by the correction.

## 2. What was done

Documentation correction only, by **dated erratum and clearly marked in-place
correction**, with every withdrawn sentence retained visibly rather than
rewritten away.

**A dated erratum was added at the head of the R8-R3 handback**, stating both
findings, the measured basis for the rollback finding, and that the correction
disposes of nothing else. It carries the explicit instruction **do not run that
command**.

**R8-R3 §8.1's rollback paragraph was replaced under a marked correction.** The
withdrawn text is quoted in place so the correction is visible. What replaces it
separates three things: what is true (documentation only, nothing committed, no
host or migration state involved); what rollback is actually available (only the
R8-R3-specific hunks and the one file R8-R3 added, by a **reviewed,
remediation-specific reverse patch or equivalent exact reconstruction preserving
every pre-existing change** — never a checkout, reset or whole-file
restoration); and what is **not** available (the exact pre-R8-R3 bytes, which do
not exist at `HEAD`, in any stash, snapshot or backup in this repository, or at
all for the three untracked handbacks). It states plainly that **no exact
automated rollback can be offered or claimed** and that any rollback beyond
deleting the R8-R3 handback **requires maintainer coordination**.

**R8-R3 §8.1's security sentence was restated** to the evidenced facts without
the absolute "or referenced" claim, and with the reason the distinction holds.

**R8-R3 §5's table was annotated, not altered.** Its rows remain correct as a
record of what was changed; a dated note records the tracking state they never
stated and that §8.1 had assumed — seven tracked, three untracked, all ten
already carrying earlier-pass work.

**The controlled documentation was reconciled only as far as recording these two
findings requires**: the handover, plan §20, the restriction banner and the four
project-management registers.

## 3. The line this remediation does not cross

Stated explicitly, because one finding is about exactly this kind of line.

* **The withdrawn `git checkout --` command was not executed**, in whole or in
  part, on any path.
* **No file was reverted, deleted, restored or moved.** The R8-R3 handback was
  not deleted; it was corrected in place.
* **No reverse patch was manufactured**, from assumptions or otherwise, and none
  is proposed here. Constructing one is maintainer-coordinated work.
* **No destructive Git command was run, attempted or recommended.** The Git
  commands used were read-only: `git status --porcelain`, `git diff --check`,
  `git diff --numstat`, `git show HEAD:<path>`, `git stash list`,
  `git stash show --name-only` and `git log -1` on the stash ref.
* **No secrets scan was run**, and no command expected to engage a secrets guard
  was issued. The consistency checks in §6 were plain `grep` searches for
  finding IDs and withdrawn phrases over `docs/` only.
* **No guard, hook, `.claude/settings.json` entry or rule was read for
  modification, altered or proposed for alteration.**
* **No guard or tool refused any call during this pass.** Had one, the pass would
  have stopped immediately with no altered attempt, and the refusal would be
  reported here.
* **No protected artifact content was added, inspected or inferred.** This
  handback refers to the three protected `/tmp` artifacts and their restriction;
  it states nothing about their contents.
* **No measurement of the R8 evidence was made or claimed.** The measurements in
  §6 are of this repository's own Git state, made to establish whether the
  withdrawn rollback instruction was safe. None touches an aggregate, a digest
  or any recorded value.
* **This remediation closes nothing** — not these two findings, not
  LAB-I3-R8-R2-GUARD-1, not LAB-I3-R8-R2-COUNT-1, not LAB-I3-R8-AGGREGATE-1, not
  either R6 Blocking finding, not I3 and not any package gate.

## 4. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-i3-r8-r3-guard-disposition-and-count-precision-remediation-handback.md` | dated erratum added at the head recording both findings and their measured basis; **§8.1 rollback paragraph withdrawn and replaced** under a marked correction, with the withdrawn text quoted in place; **§8.1 security sentence restated** without the "or referenced" claim; **§5 table annotated** with the tracking state it had assumed. No other section altered |
| `docs/review/phase-5-0-reserved-laboratory-i3-r8-r4-rollback-safety-and-protected-artifact-wording-remediation-handback.md` | **new** — this handback |
| `docs/review/Handover information` | the R8-R4 assignment block marked accepted, assigned and consumed; new active state block; the R8-R3 state block marked superseded with a forward-pointing note naming exactly what it corrects |
| `docs/implementation-plan.md` | §20 current action extended with both findings and the corrected rollback statement; its "Nothing is closed" list carries both |
| `docs/operations/disposable-test-server.md` | banner note recording that this remediation issued no host command, ran no secrets scan, reverted nothing and changed no restriction |
| `docs/project-management/status.md` | new current status; the prior status retained as superseded with a forward-pointing note |
| `docs/project-management/raid-register.md` | **LAB-I3-R8-R3-ROLLBACK-1** added — Open, Important; **LAB-I3-R8-R3-WORDING-1** added — Open, Optional |
| `docs/project-management/decision-register.md` | new pending decision on what, if anything, to roll back from R8-R3, recording that no exact automated rollback exists; the I3-disposition entry extended under a dated note to carry both new findings |
| `docs/project-management/change-log.md` | new append-only entry **C-P5.0-LAB-I3-R8-R4**, superseding the R8-R3 row's §8.1 rollback guidance and security claim |

**Migrations added: none.** No source, test, hook, manifest, generated artifact,
migration, schema or configuration file appears in that list, and none was
changed. Seven of these nine paths are tracked and modified; two — the R8-R3
handback and this one — are untracked. That distinction is stated because
assuming it is what produced LAB-I3-R8-R3-ROLLBACK-1.

## 5. Requirements addressed

The assignment's five numbered items, each with what was done.

1. **Reading and preservation.** `.agents/AGENTS.md` read completely; the
   implementation-plan reading map and §§0, 12 (Package 5.0 references), 13, 16,
   17 and 20; this handover; the disposable-server restriction banner; the R8,
   R8-R1, R8-R2 and R8-R3 handbacks; and the status, RAID, decision and change
   registers. `git status` inspected before and after. **Every unrelated and
   earlier-pass change was preserved**; none was touched, reclassified or
   reverted.
2. **The rollback section corrected.** By dated erratum plus a marked in-place
   correction. Both the `git checkout --` instruction and the exact-restoration
   claim are **withdrawn**. The command was **not executed**, the handback was
   **not deleted**, **no file was reverted**, and **no reverse patch was
   manufactured from assumptions**. A rollback truthful for this dirty,
   uncommitted tree is stated: R8-R3-specific hunks and its one added file only,
   by reviewed remediation-specific patch or equivalent exact reconstruction
   preserving every pre-existing change. The exact pre-R8-R3 bytes are **not**
   independently available, which is **said plainly**, and **maintainer
   coordination is required** in place of any claim of exact automated rollback.
3. **The security sentence corrected.** The "or referenced" claim is withdrawn;
   the record that no protected artifact was read, inspected, `stat`ed, written,
   moved, modified or reused and that no secret value was disclosed is preserved
   intact. **No artifact content was added, inspected or inferred.**
4. **Controlled documentation reconciled only as needed.** The nine files above,
   by dated erratum, marked correction or forward-pointing supersession note
   wherever historical text must stay visible. **No operational evidence was
   rewritten, no project rule altered, no measured value changed, and no
   R8/R8-R1/R8-R2/R8-R3 evidence claim strengthened.**
5. **This dated handback**, reporting requirements addressed, changed files,
   exact checks, Git status before and after, checks not run, security
   implications, truthful rollback guidance, remaining uncertainty and proposed
   reviewer focus. **LAB-I3-R8-R3-ROLLBACK-1 is left Open, Important** and
   **LAB-I3-R8-R3-WORDING-1 Open, Optional** for Codex re-review. Nothing else
   is closed or disposed of.

## 6. Checks run

**Interpreter and host.** Local `python3` 3.12.3 in the repository workspace
`/opt/freedom-blades/platform`, used only to insert one table row into
`docs/project-management/change-log.md`. **Not** the `oracle-test` interpreter;
**no host was contacted**. All other edits were exact string replacements in
documentation files.

The exact commands were: `git status --porcelain` with `wc -l` and `grep -c`
counts; `git status --porcelain -- <path>` for each of the ten documents named
in R8-R3 §5; `git diff --check`; `git diff --numstat -- <path>` for the seven
tracked documents; `git show HEAD:<path> | grep -c` for the strings `R8-R1`,
`R8-R2` and `LAB-I3-R8` in each of those seven; `git stash list`,
`git stash show --name-only stash@{0}` and `git log -1 --format` on that stash
ref; `find docs -name '*.bak' -o -name '*.orig' -o -name '*~'`; `sed -n` ranges
and `grep -n` searches over the documents read; and one heredoc `python3 -`
script performing a single insertion in the change log.

| Check | Result |
|---|---|
| `git diff --check` | clean, before and after |
| Working-tree path count, before and after | **94 paths — 34 modified, 60 untracked** before; **95 paths — 34 modified, 61 untracked** after. The one added path is this handback. No path changed classification: the eight documents this pass edited were already modified or already untracked before it began |
| Tracking state of the ten documents in R8-R3 §5 | **seven tracked and modified**; **three untracked** — the R8, R8-R1 and R8-R2 handbacks. Confirms the erratum's correction of §5's description |
| Divergence of the seven tracked documents from `HEAD` (`2fb1d6f`) | **+8,164 / −18 lines** in total: plan 641/7, restriction banner 697/4, status 820/6, RAID 863/1, decision register 610/0, change log 40/0, handover 4,493/0 |
| R8-chain content present at `HEAD` in those seven | **zero occurrences** of `R8`, `R8-R1` or `R8-R2` in every committed version. Establishes that `git checkout --` would erase the entire uncommitted R8 chain |
| Independent availability of the pre-R8-R3 bytes | **none found.** No `.bak`, `.orig` or `~` file under `docs/`; one stash only — `stash@{0}`, "On main: temp before rebase", dated 2025-09-15, touching `.env.example`, `music.py` and `requirements.txt`, unrelated to this work and inspected read-only |
| Withdrawn-wording sweep — `or referenced` across `docs/` | **within the R8-R3 handback and the documents recording this finding**, every occurrence is quoted and explicitly withdrawn; no unqualified occurrence remains. The sweep also found the phrase in two **older, unrelated** handbacks — `phase-5-0-reserved-laboratory-v6-p-r2-provisioning-safe-output-handback.md` §7 and `phase-5-0-gemini-readiness-analysis.md` — which this assignment does not cover and which were **not** edited. See the scope observation below |
| Withdrawn-instruction sweep — `git checkout --` across `docs/` | **within the R8-R3 handback and the documents recording this finding**, every occurrence is quoted as withdrawn and accompanied by an instruction not to run it; **none stands as live guidance**. The sweep also found live `git checkout --` rollback guidance in **seven older handbacks outside this assignment's scope**, which were **not** edited. See the scope observation below |
| Finding-ID spelling across all touched documents | `LAB-I3-R8-R3-ROLLBACK-1` and `LAB-I3-R8-R3-WORDING-1` spelled identically everywhere; severities stated identically (Important / Optional) and status `Open` everywhere |
| Cross-document link targets for this remediation | this handback's filename resolves from `docs/review/`, `docs/project-management/`, `docs/operations/` and `docs/implementation-plan.md` at the relative depth each uses |
| Preserved-evidence check | the measured hashes, the four-row table, the 960/612 enumeration, `c358ea8b…`, `MANIFEST_VERSION` 17, `COVERED_SOURCES` 47, `ce275fd3…`, `66855575…`, `206e40b2…`, the 50-file scope and the unresolved-cause and unrecovered-R6-procedure statements are unaltered wherever they appear |
| Historical-record check | no R6, R8, R8-R1, R8-R2 or R8-R3 operational observation was edited. Every correction is an added erratum, an added note, a quoted-and-withdrawn passage or a forward-pointing supersession note |
| Finding-state check | LAB-I3-R8-R2-GUARD-1, LAB-I3-R8-R2-COUNT-1, LAB-I3-R8-AGGREGATE-1, PR-20260920-LAB-I3-R6-1, PR-20260920-LAB-I3-R6-2, I3, V7, V8, V10, `plan.is_executable` and Package 5.0 readiness are stated identically to their pre-pass values in every document touched |

**Scope observation — not a claim that the sweep found nothing else.** The two
sweeps above are reported at the scope they actually cover, which is the R8-R3
handback and the documents recording this finding. Outside that scope they found
the same pattern elsewhere in `docs/review/`, and it is reported rather than
silently corrected or silently omitted:

* `phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md`
  §8.1 carries **the identical defect** — "To revert: `git checkout --` the eight
  modified documents and delete the one added handback … That restores the exact
  pre-remediation state, which was 92 paths". The same reasoning applies to it:
  those documents also carried earlier-pass uncommitted work.
* Six further handbacks — the reserved-laboratory implementation handback and its
  remediation, `d12-r1`, `v6-p-r1`, `v6-p-r3` and `v6-provisioning-remediation` —
  give `git checkout --` rollback instructions of the same shape, some already
  qualified by an exception clause, some not.

**None of these was edited.** The assignment's item 4 limits reconciliation to
the documentation needed to record *these two* findings, and correcting other
handbacks' rollback sections is outside it. Whether LAB-I3-R8-R3-ROLLBACK-1
generalizes to them is a question for Codex and Peter Duscha, raised in §9 and
§10 rather than acted on here.

**No guard or tool refused any call during this pass**, so there is no refusal to
report under the assignment's stop rule.

## 7. Checks not run, and why

| Not run | Why |
|---|---|
| **Any secret-indicator scan of this or any diff** | **Deliberately not run.** The assignment forbids running a secrets scan or issuing any command expected to engage a secrets guard. Reviewing this diff for secrets by scan is recorded as **not run**, not as passed. What is established instead, without any scan: the change set is documentation only, by `git status` and `git diff --numstat`, and every added line is prose about the R8 evidence chain, read in full while writing it. This mirrors R8-R3's treatment and is not a substitute check |
| Both pytest suites and the Node contract tests | Out of scope. Documentation-only remediation changing no source, test or artifact, and the assignment authorizes no suite. **No suite figure is offered, cited or claimed.** |
| Any command on `oracle-test` | **Expressly prohibited.** No host action of any kind is authorized |
| Any measurement or re-measurement of either aggregate, or of any recorded digest | Not required by either finding and not performed. This remediation makes **no measurement of the R8 evidence** and claims none |
| Execution of the withdrawn `git checkout --` command, or of any revert, reset, restore or reverse patch | **Expressly prohibited, and the subject of the finding.** Nothing was reverted. Whether anything should be is Peter Duscha's decision |
| Formatter, linter, type checker | No code changed |
| `python3 .claude/hooks/test_guards.py` | **Not run and not applicable.** No guard or hook was changed. Running it would assert guard behavior, which is not in question here and which this remediation is forbidden to alter |

## 8. Repository state

| | |
|---|---|
| Branch / `HEAD` | `docs/platform-plan` / `2fb1d6f` |
| Working tree before this remediation | **94 paths — 34 modified, 60 untracked**; `git diff --check` clean |
| Working tree after this remediation | **95 paths — 34 modified, 61 untracked**; `git diff --check` clean. The one added path is this handback |

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
them, as any record of a restricted pass must; **referring to a restriction is
not access to what it protects**, and no artifact content is stated, inspected
or inferred anywhere in this document. **No secrets scan was run and no command
expected to engage a secrets guard was issued.**

Both corrections *weaken* claims in an evidence document — one withdrawing an
unsafe instruction, one withdrawing an overreaching security claim. Neither
strengthens a claim, relaxes a control or advances a state. The security-process
matter recorded by the previous pass — the R8-R2 guard refusal that was routed
around — is **untouched by this pass**: **LAB-I3-R8-R2-GUARD-1 remains Open,
Blocking, pending Peter Duscha's disposition**.

**Configuration and deployment changes: none.** No configuration file,
environment contract, `.env.example` entry, migration, schema or deployment unit
is in the change set. Nothing needs to be deployed.

**Rollback and recovery.** Every change this pass made is documentation in the
working tree and **nothing is committed**. No data migration, no recovery
procedure, no configuration and no host state is involved.

Stated with the care the finding demands, and **not** as an exact automated
restoration:

* **The one file this pass added** — this handback — may be deleted. That is
  unambiguous, because this pass created it.
* **The eight documents this pass edited already carried earlier-pass,
  uncommitted work**, including the entire R8 chain. **`git checkout --`, `git
  restore`, `git reset` and any other whole-file restoration must not be used on
  them.** Seven are tracked, whose `HEAD` versions predate the whole R8 chain;
  one — the R8-R3 handback — is untracked and has no git baseline at all.
* Reversing this pass's edits to those eight therefore requires a **reviewed,
  remediation-specific reverse patch or an equivalent exact reconstruction that
  preserves every pre-existing change**. **The exact pre-R8-R4 bytes are not
  independently available** in this repository: not at `HEAD`, not in any stash,
  snapshot or backup, and not at all for the untracked file. **No exact
  automated rollback is offered or claimed**, and any such reversal **requires
  maintainer coordination** — Peter Duscha decides what is reversed, and the
  patch is constructed and reviewed against this pass's diff rather than
  assumed.
* This pass's edits are additive prose in identifiable regions — a new erratum
  block, a new state block, new register entries, a new change-log row and two
  marked corrections in R8-R3 §8.1 plus one note under its §5 — which is what
  makes a reviewed reverse patch feasible. It does not make a blind restoration
  safe.

**Requirements proposed but not implemented: none.** The assignment's five items
are all implemented. Nothing was deferred, and no follow-up work is proposed
beyond the independent re-review and the maintainer dispositions the assignment
requires.

## 8.2 Assumptions, stated as assumptions

1. **Authority.** The assignment block at the head of `docs/review/Handover
   information` carries an acceptance line — "Accepted by Peter Duscha and
   explicitly assigned to Claude on 2026-09-22" — **above** the draft banner it
   retains, and the maintainer instructed the operator in session to implement
   that block. The operator treated the two together as the acceptance and
   assignment the banner requires. **If that reading is wrong, this remediation
   was unauthorized and should be handled per §8.1 rather than reviewed.** The
   same question was raised as R8-R2 §8.2 item 1, R8-R2 §10 item 7 and R8-R3
   §8.2 item 1, and **remains undisposed across four consecutive passes**; this
   pass does not resolve it in its own favour.
2. **Scope of "the controlled documentation needed".** The assignment's item 4
   limits reconciliation to what recording these two findings requires. The
   operator read that as the nine documents in §4 — the R8-R3 handback carrying
   the defective section, this handback, the handover, plan §20, the restriction
   banner and the four project-management registers — and no further. The R8,
   R8-R1 and R8-R2 handbacks were **not** edited, because neither finding
   concerns them. If a document outside that set repeats the withdrawn rollback
   instruction or the "or referenced" claim, it was not found by the §6 sweeps
   and remains uncorrected.
3. **Erratum-and-correction treatment.** Historical text was retained and
   annotated, and withdrawn text quoted in place, rather than edited away, on
   the assumption that the repository's established erratum-not-rewrite
   convention governs — as the assignment's item 4 directs. A reviewer
   preferring a different arrangement would reach the same facts differently.
4. **What "the R8-R3-specific hunks" denotes.** The corrected rollback statement
   refers to them without enumerating them, because enumerating them exactly
   would require reconstructing the pre-R8-R3 tree, which is the very thing that
   is not independently available. Identifying them precisely is part of the
   maintainer-coordinated work, not an output of this pass.

## 9. Remaining uncertainty

1. **Whether anything should be rolled back from R8-R3 at all** is undecided and
   is Peter Duscha's. This pass records that no exact automated rollback exists;
   it does not propose, construct or recommend a reversal.
2. **The exact pre-R8-R3 and pre-R8-R4 bytes are unrecoverable from this
   repository.** Stated as fact, not as a problem this pass can solve. If an
   exact reconstruction is wanted, it needs a source this repository does not
   contain.
3. **The authority question in §8.2 item 1** is unresolved across four
   consecutive passes and compounds with each one. It is raised again here
   rather than allowed to lapse by repetition.
4. **The disposition of LAB-I3-R8-R2-GUARD-1 remains undecided** and is
   untouched by this pass.
5. **The cause of the aggregate divergence and the specific R6 calculation
   remain unrecorded and unresolved.** Unchanged by this pass, which recovers
   neither and claims neither.
6. The **50-file scope limit** from the closed PR-20260920-LAB-I3-R7-R1-2 is
   unchanged: no whole-tree byte-for-byte claim is made or implied.
7. Neither aggregate is approval. A digest is review input, never an I3
   confirmation and never authority for `--execute`.

## 10. Proposed independent reviewer focus

1. **Whether the withdrawn rollback instruction is now unambiguously withdrawn**
   everywhere it appears, and whether any residue of it survives as live
   guidance in any document rather than as quoted, withdrawn text.
2. **Whether the replacement rollback statement is truthful for this tree** —
   in particular whether "only the R8-R3-specific hunks and its one added file
   may be reversed, by reviewed patch or equivalent exact reconstruction, and
   the exact bytes are not independently available" is the correct statement, or
   whether a reviewer would draw the line differently.
3. **Whether this handback's own §8.1 rollback section avoids the defect it
   corrects.** It is written to the same standard it imposes; that is precisely
   what should be checked, not assumed.
4. **Whether the measured basis in §6 supports the finding as stated** — the
   seven-tracked/three-untracked split, the +8,164 / −18 divergence, the zero
   occurrences of R8-chain content at `HEAD`, and the absence of any independent
   snapshot.
5. **Whether the corrected security sentence states the evidenced facts without
   weakening the no-access record**, and whether dropping "or referenced" while
   adding the reason is the right correction or an over-correction.
6. **Whether erratum-and-marked-correction is the right treatment** for each
   document here, and whether any historical operational statement was rewritten
   rather than annotated.
7. **That nothing was reverted, deleted or restored**, that no destructive Git
   command was run or recommended, that no reverse patch was manufactured, and
   that §7 reports the secrets scan as not run rather than quietly satisfying it
   another way.
8. **That no measurement of the R8 evidence was made or claimed**, no evidence
   claim was strengthened, and no finding, gate or package state was advanced.
9. **The authority assumption in §8.2 item 1**, still undisposed after four
   passes.

## 11. Disposition

**C-P5.0-LAB-I3-R8-R4 is consumed by this handback.** The authority ends here
and reached nothing outside the repository.

**LAB-I3-R8-R3-ROLLBACK-1 remains Open, Important** and
**LAB-I3-R8-R3-WORDING-1 remains Open, Optional**, both for independent Codex
re-review. **LAB-I3-R8-R2-GUARD-1 remains Open, Blocking**, pending Peter
Duscha's disposition. **LAB-I3-R8-R2-COUNT-1 remains Open, Important.**
**LAB-I3-R8-AGGREGATE-1 remains Open, Important.** The operator closes nothing.
PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**.
I3 remains **performed but unconfirmed and not closed**, and its closure remains
Peter Duscha's decision. V7 remains excluded and absent; V8 and V10 remain
unperformed; `plan.is_executable=False`; Package 5.0 remains **not ready**;
LAB-SECRETS-1 remains Open, Low; LAB-V6-P2 remains deferred.

**No action on `oracle-test` is authorized.**
**Next step: independent Codex technical, security and evidence re-review, and
Peter Duscha's dispositions of the procedural violation and of any rollback.**
