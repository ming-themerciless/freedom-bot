# Claude handback — C-P5.0-R5-OP1-R2 capture-durability remediation — 2026-09-27

Author: Claude, under the assignment in `docs/review/Handover information`
(2026-09-27) and its controlling prompt,
[`phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-claude-prompt.md).
The controlling defect list is Codex's
[R1 re-review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r1.md),
finding **OP1-R1-1**. Codex remains the Independent Reviewer and did not take
part in this pass.

**Repository-only; documentation only; requirements only.** No command was
issued to `oracle-test` or to any other host. No SSH, synchronization,
inspection, `sudo`, database access, provisioning, verifier, suite, evidence
band, controlled write, reboot or `--execute` occurred. RP-11 was not designed
or implemented, and no capture record was created or durability sequence
tested. No source, test, hook, manifest, generated evidence, migration, schema,
infrastructure or configuration was changed. The protected `/tmp` artifacts
were not accessed. No secrets scan was run. No guard or tool refused a call.
Nothing was committed or pushed, and nothing was restored from `HEAD`.

**Nothing here authorizes either pass, accepts the prompt, claims RP-11 is
satisfied, closes P5.0-R5, binds OD-62 G-A, sets `plan.is_executable=True` or
declares Package 5.0 ready.**

---

## 1. Outcome

The authorization draft was amended in place and is returned for Codex's
independent review. It remains visibly **draft, unaccepted and unauthorized**,
and **neither pass is executable**.

| Artifact | SHA-256 |
|---|---|
| Draft as re-reviewed by Codex (R1 re-review) | `7a73d3da474562eb098548cd44270c9d1f39adecb3ab073a6ed02409295ffe61` (verified before editing) |
| [R2-amended draft](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md), as returned | `308e788cfd4267308f7fc551d53db3a17cdaabebe870d7f4c4b5e2dad7eadc7e` (1086 → 1204 lines) |
| Original Codex review, **unchanged** | `bc5d7954506ac8d04ad4425c23d06123c5ad633eb8e4dcd055f23791896171a2` |
| Codex R1 re-review, **unchanged** | `71b70fb8f5f4898f8d69cc10df91e48b8b55fbc131879c42acc0b18f9f1a592b` |
| Original drafting handback, **unchanged** | `e7db948d4f61938b02d6c8115fd0a1ffcccdbfc5d61115f34dcb0ede6ae24a1b` |
| R1 remediation assignment, **unchanged** | `66e32e9fb6f513787c58a4735e2489961a7054cbbbe6c5afe8f4b4ad50c1b890` |
| R1 remediation handback, **unchanged** | `43f38b508d2803d4e0e93d83252f5bba438639b05eea901c680e9daf28d69382` |
| R2 assignment, **unchanged** | `b1dfd97559ab11f35e470d6b839073f10dd07aa5a2f3b8440be6915b03712f04` |

**The central result.** RP-11 now requires a complete crash-consistent
publication contract for all three kinds of primary capture evidence: the two
stream files, each per-act record (including its directory entry), and the
pass-level capture index (creation, advance and finalization). Any failed file
or directory barrier is an `inconclusive` stop, is not retried, and is never
repaired. The draft names the required semantics only. **RP-11 remains absent
and unmet**, and choosing interfaces and proving they work stays with RP-11's
later implementation and review.

## 2. Exact changes — OP1-R1-1

### 2.1 Stream files (assignment §3.1)

* **C-2 amended.** Each stream file is created exclusively under a name unique
  to its `capture_seq` and never reused. A stream is **complete** only when
  three things hold: the client process has ended, the channel has reached
  end-of-file, and the file is **closed to further writing**. No record is
  written for publication until both streams are complete and have passed
  their file and directory barriers. The separate-stream rule, the
  no-truncation rule and the declared-maximum rule are unchanged.
* **C-3 amended.** A stream digest is **published** in a record only after
  that stream file's file barrier (P-2) and directory barrier (P-3) have
  succeeded. An empty stream is still a file and passes the same barriers.
* **§9.5.1 P-2 and P-3 (new).** Each completed stream file receives a file
  barrier. Then each directory holding a stream file of the act receives a
  directory barrier. This covers the stream files' **directory entries**, not
  only their bytes, so a surviving record cannot point at a lost stream entry.
* **Failure.** C-10 now covers a stream that cannot be closed and any failed
  stream barrier. Either makes the act `inconclusive` and stops the pass under
  §11.2, which consumes it. §9.5.1 adds that a stream file whose P-2 or P-3
  barrier failed is never bound by a record.
* **Preserved.** C-6 (location), C-7 (ownership and mode), C-8 (retention) and
  C-9 (redaction) keep their requirements; C-7 and C-8 are only extended to the
  new files.

### 2.2 Per-act records and directory entries (assignment §3.2)

* **§9.5.1 (new): the publication sequence P-1 … P-8**, each step only after
  the previous one has succeeded:
  1. execute and capture;
  2. complete, close and file-synchronize both streams;
  3. directory barrier on the stream files' directory;
  4. compute the digests;
  5. write the complete record under a temporary name in its publication
     directory;
  6. file barrier on the record;
  7. atomic publication by rename;
  8. directory barrier on the containing directory.

  Then the index is advanced (X-2), and only then may the next act begin.
  This is the order the assignment fixes.
* **Required semantics defined without interfaces:** *file barrier*,
  *directory barrier*, *temporary name* and *atomic publication*. Atomic
  publication **never replaces an existing entry**. An existing final name is
  a capture failure, not an overwrite.
* **C-5 amended.** The record binds the **exact names and SHA-256 digests of
  its two already-durable stream files**. "At most one published record" per
  act. The old *"written durably (written, flushed and atomically renamed)"*
  is replaced: a record is durable **only when P-1 … P-8 have all succeeded**.
  A record written, flushed and renamed whose file or directory barrier did
  not succeed is expressly **not** durable and not evidence.
* **C-10 amended.**
  * Any failed or unconfirmed barrier is an `inconclusive` stop. This covers
    the file and directory barriers on stream files, records, index states,
    the capture root and subdirectories.
  * A failed barrier is **not retried**, and a later successful
    synchronization does not cure it.
  * The act is never rewritten, repaired, completed, renamed into place or
    reissued, and no record is published for it.
  * An uncaptured possible host act is still reported as a host act without
    admissible evidence.
* **C-7 amended.** Stream files, records and index states are never modified,
  truncated, appended to, renamed or replaced after publication, and published
  names are never reused. A file that reached its final name before a barrier
  failed is **unadmitted**.
* **C-6 amended.** Creating the capture root and any subdirectory is made
  durable by a directory barrier on its containing directory before the
  genesis index state is published.

### 2.3 Capture index (assignment §3.3)

* **§9.5.2 (new).** The index is a **chain of separate, immutable index
  states**, each published by the same temporary name → file barrier → atomic
  publication → directory barrier sequence. No published record, and no
  earlier state, is modified to maintain it. Each state carries:
  * `pass_id`, the capture root and `PIN.capture_tool_sha256`;
  * its state number and the SHA-256 of the state it follows;
  * a status, `open` or `final`;
  * the complete, gap-free, strictly increasing list of
    `(capture_seq, record name, record SHA-256)`. This preserves C-5's and
    C-12's sequence and ordered-digest requirements.
* **X-1 create.** After A0-08's check and **before the first host command**,
  the mechanism creates the capture root exclusively and publishes the
  genesis state *I*-0. A failure is an `inconclusive` stop before any host
  act. A0-08 and the A0/B0/B1 stop row in §11.2 now say this too.
* **X-2 advance.** After act *n*'s P-8, the mechanism publishes *I*-*n*. The
  next act waits for *I*-*n*'s directory barrier. A record is **admitted**
  only once a durable open state lists it. If *I*-*n* cannot be published
  durably, record *n* is not admitted and the pass stops.
* **X-3 finalize.** Exactly one final state *F* is published on completion
  **or on any stop**. *F* carries:
  * the records of the last durable open state and that state's digest;
  * a terminal status and stop reason;
  * the names of the unadmitted files.

  It issues no host command and is not a retry. **The finalization point is
  the successful directory barrier after *F*'s publication**, after which
  nothing further is created. **The handback's capture index SHA-256 is the
  SHA-256 of *F*.**
* **X-4 validity.** *F* must be durable and unique, with an intact chain to
  *I*-0. It must be gap-free and equal to the last durable open state. Every
  listed record and every bound stream must exist with its digest. Every
  published record must be either listed or named as unadmitted. **A missing,
  stale, non-durable or internally inconsistent final index state is an
  `inconclusive` stop.** No row of that pass is then a measured fact, and *F*
  is never written or reconstructed afterwards — not from the transcript,
  from memory, from intermediate states or by hand.

### 2.4 Interruption and unadmitted files (new C-15, §9.5.3)

* A crash, power loss or restart of the **repository host**, or termination of
  the mechanism, is a capture failure that ends the pass. The pass is not
  resumed and no further host command is issued. If *F* was not finalized, X-4
  applies.
* The **B6 reboot of `oracle-test` is expressly not** such an interruption.
  Every B6 command, including B6.4, completes P-1 … P-8 and X-2 before the
  next command. This addresses the review's point that durability is material
  to the mandatory reboot band.
* **Unadmitted files** are retained unmodified, reported by name and never
  completed, renamed, deleted, adopted or used as evidence. They are temporary
  files, unbound streams, unadmitted records and index states outside *F*'s
  chain.
* After a stop the capture root is **read-only**: names are listed and digests
  re-derived for the handback and the review. Nothing is repaired.

### 2.5 Dependent statements reconciled (assignment §3.4)

| Location | Change |
|---|---|
| Header | R1 re-review and R2 amendment recorded. The draft is stated to be unreviewed, unaccepted and unauthorized. The Pass A bullet says RP-11 includes the crash-consistent sequence |
| §4.1 A-1 | a review of `7a73d3da…` is added to the reviews that are not the required acceptance |
| §4.3 | the pins are stated as re-derived by neither R1 nor R2. `PIN.prompt_sha256` lists `9bd4f5b5…` and `7a73d3da…` as superseded |
| §4.4 RP-11 | adds the crash-consistent publication contract (C-13, C-14) and the barrier-failure stop. States that interface choice and proof belong to RP-11's implementation and review, and that the draft does not claim RP-11 is satisfied |
| §4.5 `MI.capture_root` | must lie on a filesystem whose file and directory synchronization semantics RP-11's review has accepted |
| §6.1 A0-08 | the admission step now ends with X-1. No host command is issued before X-1 succeeds |
| §6.2 preamble | each capture is published through §9.5.1/§9.5.2 before the next command |
| §9.1 | the primary-evidence row covers index states, and admission is tied to barriers plus the final index. Unadmitted files are retained |
| §9.3 | fields come only from a durably published record listed in the durable final index state |
| §9.4 | review inputs are the final index state, its digest, every earlier state and the unadmitted files |
| §9.5 preamble; C-2, C-3, C-5 … C-8, C-10, C-12 | as §2.1–§2.3 above. New rows C-13, C-14 and C-15 |
| §9.5.1 – §9.5.3 | new subsections, as §2.2–§2.4 above |
| §10 item 9 | covers streams, records, index states and unadmitted files. No completion or renaming, and no reconstruction of *F* |
| §11.2 "every band" row | lists every barrier failure, a replacing publication, a missed index advance and a repository-host interruption. The pass is finalized under X-3 unless the mechanism itself was interrupted. An invalid *F* makes the capture evidence `inconclusive` |
| §11.2 A0/B0/B1 row | adds the case where the genesis state is not durably published |
| §11.3 | adds failed durability barriers to what is never retried |
| §14 template §2 | now states the final index state's name, the capture index SHA-256 of *F*, its terminal status, X-4 validity, the index-state range, the admitted-record count and the unadmitted files |

### 2.6 Controls deliberately not changed (assignment §4)

These were confirmed by diffing the draft against the `7a73d3da…` bytes, which
had been kept aside before editing. Every hunk lies in the locations listed in
§2.5. The unchanged items are:

* The original findings' dispositions:
  * OP1-R1: RP-1 and RP-10, §4.7, and A1-C as corroborative only;
  * OP1-R2: row 40 as feasibility, RP-12 and B4b;
  * OP1-R3: RP-11 absent, and the transcript is not evidence.
* The MD-1 … MD-6 table and the controlling-state paragraph, byte for byte.
* The §8 matrix, including JNL-40(b)'s exclusion.
* B5's RR-11, RR-14 and RR-16, and B6's steps. Only a §9.5.3 statement about
  B6 was added.
* RP-1 … RP-10 and RP-12, and A-6.

P5.0-R5 remains Blocking, OD-62 G-A conditional, `plan.is_executable=False`,
and Package 5.0 not ready.

## 3. Unresolved prerequisites after this remediation

| Blocker | State |
|---|---|
| **RP-11** | **Unmet.** Its requirements now include C-13 … C-15. A separately assigned implementation pass must choose the interfaces and show that they deliver file barriers, directory barriers and non-replacing atomic publication on the filesystem holding `⟨MI.capture_root⟩`. It must also meet C-1 … C-12, including C-11 guard compatibility for §5, and then be independently reviewed and pinned (`PIN.capture_tool_sha256`) |
| RP-1 … RP-10, RP-12 | unchanged and unmet, as the R1 handback §3 records |
| A-6 / MD-5 | unmet: no independent acceptance record |
| `MI.pinned_commit`, `MI.pinned_commit_B`, `MI.capture_root`, `MI.run_record_path`, `MI.target_fact_statement` and the other §4.5 inputs | unsupplied. `MI.capture_root` now also needs an accepted filesystem |

Questions for Codex and the maintainer. Each arises from the correction, and
none is decided here:

1. **One capture root per pass.** C-6 requires the capture root to be absent
   before a pass, C-14 fixes one index per pass, and B0 repeats A0-08. So
   Pass A and Pass B need different capture roots. §4.5 has a single
   `MI.capture_root` input, and the draft already carried this ambiguity at
   `7a73d3da…`. This pass did not change it because OP1-R1-1 does not reach
   it. Should the input become per pass?
2. **Is X-4 strict enough, or too strict?** An invalid or missing *F* makes no
   row of the pass a measured fact, even where earlier records and open states
   are individually durable. This follows the assignment's "not reconstructed"
   rule. Codex may prefer a narrower consequence.
3. **Filesystem acceptance.** The added `MI.capture_root` condition makes the
   filesystem's synchronization semantics part of RP-11's review. It names
   no filesystem and no mount option.
4. **Digest source.** P-4 does not say whether the digest is computed from the
   bytes as written or re-read after the barrier. That is an implementation
   choice left to RP-11.

## 4. Files read

* `CLAUDE.md`; `.agents/AGENTS.md`, completely.
* `docs/implementation-plan.md`:
  * the reading map;
  * §0, §13, §14, §16 and §20;
  * the Phase 5 package table and its package-gate text.
* `docs/review/Handover information` (current).
* `docs/operations/disposable-test-server.md`: the first restriction banners.
* The R2 assignment and the Codex R1 re-review, both completely.
* The authorization draft at `7a73d3da…`, completely.
* The R1 remediation handback and the R1 remediation assignment.
* The original Codex review, completely.
* `docs/project-management/status.md`: its current section.

## 5. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | amended in place (§2). Untracked before and after |
| `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r2-durability-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | active assignment marked returned for Codex review, with pointers |
| `docs/project-management/status.md` | current status records the return |
| `docs/implementation-plan.md` | §20 current action points to the amended draft, the assignment, this handback and the required Codex review |
| `docs/operations/disposable-test-server.md` | the first restriction banner records the return and that no host action occurred |

Not changed:

* the original Codex review, the R1 re-review, the drafting handback, the R1
  assignment, the R1 handback and the R2 assignment;
* the RAID, decision and change registers;
* any source, test, hook, manifest, generated artifact, migration, schema or
  configuration.

## 6. Validation performed

Repository-local documentation checks only, as assignment §6 lists.

1. **Term search.** The amended draft was searched for every occurrence of
   `durab`, `flush`, `synchron`, `atomic`, `renam`, `capture index`,
   `inconclusive` and `capture failure`. Each hit was read in context.
   * **Order.** Every statement of the publication order agrees with P-1 …
     P-8 and X-1 … X-3: RP-11, C-2, C-3, C-5, C-13, C-14, §6.2, A0-08,
     §9.1, §9.3 and §11.2.
   * **Failure semantics.** Every statement agrees with C-10, X-4 and C-15:
     C-5, C-7, §9.5.1's closing paragraph, X-1, X-2, §10 item 9, §11.2 and
     §11.3.
   * **Unrelated hits.** The remaining hits concern the §5 synchronization,
     the harness's own `release durable`, the `oracle-test` B6.1c `sync`,
     and RP-5/MD-3's reboot durability. They are outside this finding and
     unchanged.
   * **Fixes.** Two inconsistencies found by this search were corrected
     before return:
     * §11.2 said the pass "is finalized under X-3" even after a
       repository-host interruption. It now excepts that case.
     * X-1 did not say what follows when the genesis state is not durable.
       It now says no final state can then satisfy X-4, and none is
       constructed.
   * **Stale text.** The old C-5 phrase *"written durably (written, flushed
     and atomically renamed)"* no longer occurs.
2. **Coverage.** Each item appears in the contract:

   | Item | Where |
   |---|---|
   | stream files | C-2, C-3, P-2, P-3 |
   | per-act records | C-5, P-5 … P-7 |
   | containing-directory barriers | P-3, P-8, C-6, and the X-sequence publication rule |
   | capture index creation, advance and finalization | X-1, X-2, X-3 |
   | final index validity and digest | X-3, X-4, C-12, §14 |
3. **Relative links.** Every new link resolves (§6.1).
4. **`git diff --check`**, limited to the changed documentation files (§6.1).
5. **Scoped diff inspection**, and a survey of the pre-existing worktree (§8).

### 6.1 Results

These checks were run after every edit to the six changed files, with this
handback's §6.1 and §8 still holding placeholders. Filling them in added no
link and no trailing whitespace.

* **Links.** A read-only script resolved every relative Markdown link against
  its file's directory, excluding URLs and in-page anchors. Every file had
  **0 missing**:

  | File | Relative links |
  |---|---|
  | the draft | 15 |
  | this handback | 3 |
  | `Handover information` | 12 |
  | `status.md` | 13 |
  | `implementation-plan.md` | 128 |
  | `disposable-test-server.md` | 63 |

* **Tracked files.** `git diff --check` limited to the four tracked files
  printed nothing and exited 0.
* **Untracked files.** `git diff --no-index --check /dev/null <file>` printed
  nothing for the draft or for this handback. Its exit status is not relied
  on, because `--no-index` returns 1 whenever the files differ. A direct
  search found 0 lines with trailing whitespace or tab characters in either
  file.
* **Scoped diff.** The draft was compared with the `7a73d3da…` copy set
  aside before editing. It has 21 hunks, 32 lines removed and 150 added, all
  in the locations of §2.5. For each tracked file, only the hunks this pass
  added differ from a copy taken before editing:
  * `Handover information`: the title, the new returned block, the consumed
    heading and the next-handoff paragraph;
  * `status.md`: the title and the returned paragraph;
  * the plan: the new §20 current action, with the prior action relabelled
    *Superseded*;
  * `disposable-test-server.md`: the new first banner.

## 7. Checks not run, and why

* **Anything on `oracle-test`.** Prohibited; no command in the draft was
  executed.
* **Test suites, the harness dry run and the A0-06 classifier tests.** This
  was a documentation-only assignment, and the assignment says not to run
  suites.
* **Any trial of the durability sequence, and any capture record.** Both are
  prohibited. The sequence is a requirement for RP-11's later implementation
  and review, and it is unproven here.
* **Re-derivation of the §4.3 pins.** They were unchanged, and §4.3 says so.
* **A secrets scan.** Prohibited.
* **`python3 .claude/hooks/test_guards.py`.** No guard was changed.
* **Formatter, linter and type checker.** No code was changed.

## 8. Git status relevant to this assignment

* **Branch and `HEAD`.** Branch `docs/platform-plan`; `HEAD`
  `2fb1d6fd88013752d53af76fc97b4db07fc31181`, unchanged.
* **Porcelain entries.** 147 before this pass and 148 after. The only
  difference is this new untracked handback.
* **Changed files.**
  * The draft was untracked before and remains untracked.
  * `Handover information`, `status.md`, `implementation-plan.md` and
    `disposable-test-server.md` were already modified by earlier uncommitted
    work, and now also carry this pass's hunks.
* **Untouched.** No other path was touched. No pre-existing change was
  reverted, restored, staged or committed.

## 9. Security, data-authority and operational implications

* **Security.** The change only narrows the draft. It adds stop conditions and
  forbids retrying a failed barrier, replacing a published name, and
  reconstructing a final index. It adds no host path, no privilege and no
  target-side file. C-6's *no file on `oracle-test`* and C-11's guard rule are
  unchanged.
* **Data authority.** No change.
* **Rollback and recovery.** §10 item 9 now covers index states and unadmitted
  files. Nothing else changed.
* **Reboot.** MD-3's B6 is unchanged. §9.5.3 states that the `oracle-test`
  reboot does not interrupt capture on the repository host.

## 10. Proposed Codex review focus

1. Does P-1 … P-8 close the gap OP1-R1-1 identified? In particular:
   * the stream entries' directory barrier (P-3) before the record exists;
   * the non-replacing atomic publication.
2. Is the index-state chain (X-1 … X-4) sound? Is the finalization point
   unambiguous, and are the X-2 admission rule and the X-4 consequence
   correct?
3. C-10 and C-15: are the no-retry and no-cure rules for failed barriers, and
   the treatment of unadmitted files, correctly stated?
4. Is the text neutral about implementation throughout? It should name
   semantics, not interfaces, commands or a language.
5. The four questions in §3, especially whether each pass needs its own
   capture root.

Claude has stopped. The next action is Codex's independent review of the
exact R2-amended bytes. Only a later explicit maintainer decision may accept or
authorize any operational pass.
