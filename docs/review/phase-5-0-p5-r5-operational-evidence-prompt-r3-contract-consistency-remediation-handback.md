# Claude handback — C-P5.0-R5-OP1-R3 capture-contract consistency remediation — 2026-09-27

Author: Claude, under the assignment in `docs/review/Handover information`
(2026-09-27) and its controlling prompt,
[`phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-claude-prompt.md).
The controlling defect list is Codex's
[R2 review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r2.md),
findings **OP1-R2-1** and **OP1-R2-2**. Codex remains the Independent Reviewer
and did not take part in this pass.

**Repository-only; documentation only; requirements only.** No command was
issued to `oracle-test` or to any other host. No SSH, synchronization,
inspection, `sudo`, database access, provisioning, verifier, suite, evidence
band, controlled write, reboot or `--execute` occurred. RP-11 was not designed
or implemented. No capture root or record was created, and no durability
sequence was tested. No source, test, hook, manifest, generated evidence,
migration, schema, infrastructure or configuration was changed. The protected
`/tmp` artifacts were not accessed. No secrets scan was run. No guard or tool
refused a call. Nothing was committed or pushed, and nothing was restored from
`HEAD`.

**Nothing here authorizes either pass, accepts the draft, claims RP-11 is
satisfied, closes P5.0-R5, binds OD-62 G-A, sets `plan.is_executable=True` or
declares Package 5.0 ready.**

---

## 1. Outcome

The authorization draft was amended in place and is returned for Codex's
independent review. It remains visibly **draft, unaccepted and unauthorized**,
and **neither pass is executable**.

| Artifact | SHA-256 |
|---|---|
| Draft as reviewed by Codex (R2 review) | `308e788cfd4267308f7fc551d53db3a17cdaabebe870d7f4c4b5e2dad7eadc7e` (verified before editing) |
| [R3-amended draft](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md), as returned | `026edf43935fb8a837911d66f467596e5ebfe31a4da1135e576f0c03a4dd69f7` (1204 → 1289 lines) |
| Original Codex review, **unchanged** | `bc5d7954506ac8d04ad4425c23d06123c5ad633eb8e4dcd055f23791896171a2` |
| Codex R1 re-review, **unchanged** | `71b70fb8f5f4898f8d69cc10df91e48b8b55fbc131879c42acc0b18f9f1a592b` |
| Codex R2 review, **unchanged** | `9722adbfee3e7c553ad9356d28f1bee1b6c7ddf5def623aad6482bf2c6f89d12` |
| Original drafting handback, **unchanged** | `e7db948d4f61938b02d6c8115fd0a1ffcccdbfc5d61115f34dcb0ede6ae24a1b` |
| R1 remediation assignment, **unchanged** | `66e32e9fb6f513787c58a4735e2489961a7054cbbbe6c5afe8f4b4ad50c1b890` |
| R1 remediation handback, **unchanged** | `43f38b508d2803d4e0e93d83252f5bba438639b05eea901c680e9daf28d69382` |
| R2 assignment, **unchanged** | `b1dfd97559ab11f35e470d6b839073f10dd07aa5a2f3b8440be6915b03712f04` |
| R2 handback, **unchanged** | `c191a83cc18d6d922635bbfc965a0dd4b39f5c1593ebfb1af764743401e174c1` |
| R3 assignment, **unchanged** | `dee11c9e6425821552bfc2a2148905c80cc472b074e06a6f4a6d834c9177e36a` |

**The central result.**

* **OP1-R2-1.** Each pass now has its own capture root, genesis state, index
  chain, final state and handback binding. Pass B's admission no longer
  requires Pass A's retained root to be absent.
* **OP1-R2-2.** Stop, X-3 finalization and the read-only state now follow one
  order, stated once in §9.5.3. Every dependent clause refers to it.

The draft names required semantics only. **RP-11 remains absent and unmet.**

## 2. Exact changes — OP1-R2-1, distinct retained capture roots

### 2.1 The inputs (§4.5)

The single `MI.capture_root` row is replaced by two rows.

* **`MI.capture_root_A`** is Pass A's own root. It keeps every earlier
  condition:
  * absent before Pass A;
  * outside the Git worktree and `/tmp`;
  * on a filesystem RP-11's review has accepted;
  * created exclusively in Pass A's X-1, with its own genesis state and index
    chain.

  After Pass A it is **retained, unmodified and unused**. It is never removed,
  renamed, reused or modified to make `MI.capture_root_B` absent. Used by:
  A0-08 and Pass A's X-1, every A1 host command, and Pass A's X-2 … X-4 and
  handback. It is **never used by Pass B**.
* **`MI.capture_root_B`** is Pass B's own root. It must **differ from**
  `MI.capture_root_A`, and neither may lie within the other. It
  **independently** meets every condition stated for `_A`. It is never
  derived from Pass A's root, created inside it, or made available by
  changing it. Used by: B0-08 and Pass B's X-1, every B1 … B7 host command,
  and Pass B's X-2 … X-4 and handback.

Both remain **typed blockers**; neither value is supplied.

### 2.2 Admission

* **A0-08** now checks and creates `⟨MI.capture_root_A⟩` and publishes Pass
  A's genesis state there.
* **B0** no longer repeats A0-08 textually with Pass A's value. It repeats
  A0-01 … A0-07 and A0-09, and adds **B0-08**, the Pass B equivalent of A0-08:
  * the capture tool digest check;
  * `_B` differs from `_A`, and neither lies within the other;
  * `_B` does not yet exist;
  * then X-1 creates `_B` exclusively and publishes Pass B's own genesis state
    there.

  Nothing under `_A` is written, moved, renamed or removed, and `_A` is not
  used.
* **B1** states that its commands are captured under `⟨MI.capture_root_B⟩`.
* **§11.2 A0/B0/B1 row.**
  * A0-08's failure case names `_A`.
  * A new B0-08 failure case covers `_B` present, equal to `_A`, within it or
    containing it, and a Pass B genesis state that was not durably published.
  * A new stop covers any act that would write, move, rename or remove
    anything under `_A` to admit Pass B.

### 2.3 Capture contract (§9.5)

| Location | Change |
|---|---|
| §9.5 preamble | defines **the pass's capture root**: `_A` for every act of Pass A, `_B` for every act of Pass B. States that each pass has exactly one root, genesis state, index chain, final state and handback binding, and that nothing of one pass is written, listed or chained under the other's root. The filesystem obligation now refers to each pass's root |
| C-6 | rewritten as **one distinct root per pass**. The roots are distinct, neither lies within the other, and each independently meets the location, `/tmp`, worktree, accepted-filesystem and absent-before-its-own-pass conditions. Each is created exclusively in its own pass's X-1 (A0-08 or B0-08) with its own directory barriers. Pass A's root is never removed, renamed, reused or modified to make Pass B's root absent. The common-parent clause is described after this table |
| C-8 | adds that `_A` and everything under it stay retained, unmodified and unused while Pass B is admitted and executed, and that Pass B's admission never depends on changing it |
| C-12 | each handback states **its own** root and the outcome of its X-3 attempt. A Pass B row is never bound to a record under Pass A's root, or the reverse |
| C-14 | one index per pass, under that pass's own root. Pass B's chain begins at its own genesis state and never continues, reuses or references Pass A's chain. There is no shared index |
| §9.5.2 preamble | "each pass has its own capture index". Each state carries the pass's own root |
| X-1 | acts after the pass's admission check (A0-08 or B0-08) and before the pass's first host command, on the pass's root |
| X-4 | the chain must be intact back to **the same pass's** *I*-0. The "every published record" condition applies to the pass's own root |
| §9.5.3 | unadmitted files are those under the pass's own root. A closing paragraph states that Pass B's stop transition acts only on `_B`, and that Pass A's root, already read-only, is never written, even by Pass B's X-3 attempt |

**Common parent (C-6).** The draft names no common parent directory. If the
two roots share one:

* it already exists;
* the mechanism and the operator never create it, clean it up or write to it,
  apart from each root's own entry in it;
* it holds no capture file itself;
* each root is still created separately and exclusively, and is
  independently durable.

This adds no collision risk and no cleanup requirement.

### 2.4 Other dependent references

| Location | Change |
|---|---|
| Header, Pass A summary | names `MI.capture_root_A` as Pass A's own root |
| Header, Pass B summary | Pass B also needs its own `MI.capture_root_B`, distinct from Pass A's retained root |
| §4.4 RP-11 | "a fixed repository-host location outside the worktree" becomes a fixed, **pass-specific** capture root, `_A` for Pass A and `_B` for Pass B, distinct and each with its own index chain. "A pass-level capture index" becomes "one capture index per pass, under that pass's own capture root" |
| §9.1 primary-evidence row | location is the pass's own root, `_A` or `_B`, each with its own genesis state, chain and final state. Retention adds that Pass A's root stays retained, unmodified and unused throughout Pass B and is never removed, renamed, reused or modified to make Pass B's root absent |
| §9.4 | review inputs are given **for each pass separately**: its root, its X-3 outcome, its final state and digest, its own chain and its retained files |
| §10 item 9 | neither root is rolled back or cleaned up, and `_A` is never removed, renamed, reused or modified to admit Pass B |
| §12 | output is captured under the pass's own root, `_A` or `_B` |
| §14 template | "Capture root" is the pass's own root. The Pass B handback also states that Pass A's root was not used, written, moved, renamed or removed |
| Final draft reminder | Pass A needs `MI.capture_root_A`. Pass B needs its own distinct `MI.capture_root_B` |

After the change, the draft contains **no bare `MI.capture_root`** (§6, check 1).

## 3. Exact changes — OP1-R2-2, one ordered stop transition

### 3.1 The transition (§9.5.3)

The unqualified bullet *"After a stop, read-only only … No file there is
written, moved or removed"* is removed. Its operator rule is kept as step 4 of
a new **stop transition**. That transition applies, in order, to every stop: a
§11.1 refusal, a §11.2 stop or a C-10 capture failure.

1. **Stop further commands.** Command execution stops immediately. No host
   command is issued, retried or reissued after the stop, not even a read-only
   one. The failed act is not completed, repaired or re-run.
2. **One local X-3 finalization attempt, only where possible.** This happens
   only if the capture mechanism and the repository host both remain available
   and the pass has a durable *I*-0. The attempt:
   * is the **only** write permitted under the pass's root after the failure
     or refusal;
   * creates only *F*;
   * alters no stream file, per-act record, earlier index state or unadmitted
     file;
   * issues no host command, and is neither a retry nor a repair.
3. **One outcome.**
   * The attempt **succeeds** at the X-3 finalization point: the successful
     directory barrier after *F*'s atomic publication.
   * It **fails** at the first step that does not succeed. That includes a
     failed or unconfirmed barrier, and an interruption during the attempt.
   * A failed attempt, including a failed finalization barrier, is not retried
     or cured. The resulting final state is not repaired, completed or
     reconstructed, and X-4 decides admissibility.
4. **Read-only state.** The root becomes read-only when the attempt reaches
   either outcome. After that the operator may only list names and re-derive
   digests.
5. **No attempt after an interruption.** If the capture mechanism or the
   repository host was interrupted, no X-3 attempt is possible, before or
   after recovery. The root is read-only from the interruption, and X-4
   applies directly.

A pass that **completes** follows steps 2 to 4 in the same way. The text
keeps four terms apart:

* **stopping further commands** (step 1);
* **the local X-3 finalization attempt** (step 2);
* **the finalization point**, which is success (step 3);
* **the read-only state**, after the attempt or after an interruption (steps 4
  and 5).

### 3.2 Dependent clauses

| Location | Change |
|---|---|
| C-10 | *"The only further act the mechanism performs is the finalization of §9.5.2 X-3"* is replaced by a statement that the §9.5.3 transition applies **in its order**. Commands stop at once, and no host command is issued, retried or reissued. If the mechanism and repository host remain available, the only permitted write is one X-3 attempt, which records the stop. The root is read-only once that attempt reaches its outcome, or at once after an interruption |
| C-15 | no X-3 attempt is made after recovery, and X-4 applies directly |
| X-1 | with no durable *I*-0 there is no chain to finalize and **no X-3 attempt is made**. The existing "none is constructed" rule is kept |
| X-3 | now **"Finalize — one attempt"**. It makes exactly one attempt where §9.5.3 permits one. After a stop it is the only permitted write. It creates nothing but *F* and does not write, rename, move or remove any stream file, per-act record, earlier index state or unadmitted file. Reaching the finalization point is success; any failed step is failure, which is not retried or cured. The root becomes read-only at either outcome. No attempt is made after an interruption. *"After it, nothing further is created"* is replaced by the read-only rule, which covers both outcomes. The handback digest rule is unchanged |
| X-4 | adds: *"A failed X-3 attempt is not repeated, and the resulting final state is not repaired or completed."* The never-reconstructed rule is unchanged |
| §9.5.3 interruption bullet | no X-3 attempt, including after recovery. The root is read-only from the interruption, and X-4 applies directly |
| §9.5.3 unadmitted files | adds "a file left by a failed X-3 attempt" |
| §10 item 9 | after a stop, the mechanism's one X-3 attempt is the only write, and the root is read-only once it reaches its outcome |
| §11.1 | the X-3 attempt is not a host command and not a retry; it follows the §9.5.3 transition. *"No further host command"* is unchanged |
| §11.2 "every band" row | *"the pass is finalized under X-3"* is replaced by the transition in order: no further host command; one X-3 attempt as the only write where the mechanism and host remain; the root read-only once the attempt succeeds or fails; after an interruption, no attempt and X-4 directly |
| §11.3 | a failed X-3 finalization attempt is added to what is never retried |
| §14 template | adds the X-3 outcome line (`succeeded at the finalization point`, `failed at <step>`, or `not made: <interruption \| no durable I-0>`). The final state name and digest may be `none` |

### 3.3 Header, admission and pin bookkeeping

These are the same kind of updates the R2 pass made:

* **Header.** Records the R2 review and this R3 amendment, and states that the
  R3 bytes are unreviewed, unaccepted and unauthorized.
* **§4.1 A-1.** Adds the R2 review of `308e788c…` to the reviews that are not
  the required acceptance.
* **§4.3.** Records that R3 also did not re-derive the pins, and lists
  `308e788c…` among the superseded prompt digests.

## 4. Controls deliberately not changed

The draft was diffed against the `308e788c…` bytes, which were kept aside
before editing. It has 33 hunks, all in the locations listed in §2 and §3.
Unchanged:

* the resolved dispositions of OP1-R1 (RP-1/RP-10, §4.7, A1-C corroborative
  only), OP1-R2 (row 40 as feasibility, RP-12, B4b), OP1-R3 (RP-11 absent, the
  transcript is not evidence) and OP1-R1-1 (P-1 … P-8, X-2, C-2, C-3, C-5,
  C-7, C-13);
* the MD-1 … MD-6 table and the controlling-state paragraph, byte for byte;
* the §8 matrix, including JNL-40(b)'s exclusion;
* B5's RR-11, RR-14 and RR-16, and B6's steps;
* RP-1 … RP-10 and RP-12, A-6, and every other unresolved prerequisite;
* P-1 … P-8, X-2, and C-1 … C-5, C-7, C-9, C-11 and C-13, with no text
  change.

X-1, X-3, X-4, C-6, C-8, C-10, C-12, C-14 and C-15 changed only as §2 and §3
state.

P5.0-R5 remains Blocking, OD-62 G-A conditional, `plan.is_executable=False`,
and Package 5.0 not ready.

## 5. Unresolved prerequisites after this remediation

| Blocker | State |
|---|---|
| **RP-11** | **Unmet.** Its requirements now include pass-specific roots and the §9.5.3 stop transition, besides C-1 … C-15. A separately assigned implementation pass must choose the interfaces and prove them. That proof covers both roots' filesystems, the exclusive creation of `_B` without touching `_A`, and a single, non-repeating X-3 attempt. The mechanism must then be independently reviewed and pinned (`PIN.capture_tool_sha256`) |
| RP-1 … RP-10, RP-12 | unchanged and unmet |
| A-6 / MD-5 | unmet: no independent acceptance record |
| `MI.pinned_commit`, `MI.pinned_commit_B`, **`MI.capture_root_A`**, **`MI.capture_root_B`**, `MI.run_record_path`, `MI.target_fact_statement` and the other §4.5 inputs | unsupplied |

Points for Codex and the maintainer. Each arises from the correction, and none
is decided here:

1. **X-1 failure yields no X-3 attempt.** The assignment's rule 3 permits one
   X-3 attempt "if the capture mechanism and repository host remain
   available". The R2 X-1 already said that, without a durable *I*-0, no final
   state can satisfy X-4 and none is constructed. To keep those two rules
   consistent, the draft now adds the durable *I*-0 as a condition for the
   attempt. Without it there is no chain to finalize, so no attempt is made
   and the root, if created, is read-only from that failure. This is a
   narrowing, not a new write. Codex should confirm it is the intended
   reading.
2. **B0-08 is a new step identifier.** The assignment requires B0 to perform
   the equivalent of A0-08 against `_B`, not a textual repeat. Giving it its
   own id lets §11.2, C-6 and X-1 name it. No other step id changed.
3. **"Neither lies within the other."** This is required so that creating
   `_B` cannot modify `_A`, and so that `_A`'s X-4 "every published record
   under the root" condition cannot see Pass B's files. The comparison method
   is not specified; it belongs to RP-11.
4. **B0 does not inspect Pass A's root.** B0-08 compares paths and checks that
   `_B` is absent. It does not read, list or verify `_A`'s contents. The R2
   review and the assignment require only that `_A` be retained, unmodified
   and unused. If Codex wants a read-only retention check of `_A` at Pass B
   admission, that is an addition this pass did not make.
5. **When `_B` is supplied.** §4.5 still says maintainer inputs are supplied
   in the A-2 authorization. This pass does not decide whether `_B` must be
   named with `_A` or may come in a later Pass B authorization. B0-08 enforces
   distinctness either way.

## 6. Validation performed

Repository-local documentation checks only, as assignment §6 lists. The
results are in §6.1.

1. **Term search.** The amended draft was searched for every occurrence of
   `capture_root`, `capture root`, `A0-08`, `B0`, `stop`, `finaliz`,
   `read-only`, `C-10`, `X-3`, `X-4` and `interruption`, and each hit was read
   in context.
2. **Per-pass uniqueness.** Each pass has exactly one of each of the
   following, with no retention conflict:

   | Item | Pass A | Pass B |
   |---|---|---|
   | root | `_A` (§4.5, C-6) | `_B` (§4.5, C-6) |
   | genesis state | X-1 after A0-08 | X-1 after B0-08 |
   | index chain | C-14, X-2 | C-14, X-2, never continuing A's |
   | final state | X-3 | X-3, acting only on `_B` |
   | handback binding | C-12, §14 | C-12, §14, plus the statement that `_A` was untouched |

   Retention: C-8, §9.1 and §10 item 9 keep `_A` unmodified and unused through
   Pass B. No clause requires `_A` to be absent, removed or reused.
3. **Stop transition.**
   * X-3 is the sole permitted post-stop write in C-10, X-3, §9.5.3 step 2,
     §10 item 9 and the §11.2 every-band row.
   * The read-only state begins at the attempt's one success-or-failure
     outcome (X-3, step 4), or at the interruption (step 5, C-15).
   * The draft no longer contains *"After a stop, read-only only"*, *"The only
     further act"*, *"After it, nothing further is created"* or *"the pass is
     finalized under X-3"*.
4. **Relative links.** Every new link resolves.
5. **`git diff --check`**, limited to the changed documentation files.
6. **Scoped diff inspection**, and a survey of the pre-existing worktree
   (§9).

### 6.1 Results

* **Term search.**
  * **Roots.** The draft has 0 occurrences of bare `MI.capture_root`. Every
    `capture_root` hit is `_A` or `_B` and sits on the correct pass. Every
    generic "capture root" hit is either defined as the pass's own root
    (§9.5 preamble) or names both.
  * **A0-08 and B0.** Every `A0-08` hit refers to Pass A. Every `B0` hit that
    concerns the capture root refers to B0-08 or `_B`: §4.5, B0-08, C-6, X-1
    and the §11.2 A0/B0/B1 row. The other `B0` hits are unaffected: band
    names in the header, §0 and the §7.1 heading, the MD-5 row, §4.3, the
    `MI.pinned_commit_B` row, and the §8 introduction and row 34/36.
  * **Stop terms.** Every `finaliz`, `X-3`, `X-4`, `C-10` and `interrupt` hit
    agrees with the §9.5.3 order.
  * **Unrelated hits.** The other `read-only` hits describe the target host,
    not the capture root. They cover pass and band titles, AUTH-READ and
    AUTH-DBREAD, the drafting pin check, RP-5 and RP-12, the A1/B1/B4b
    surveys, §10 item 8, §11.1's "not even a read-only one", B6.5 in §11.3,
    and §13.1. The other `stop` hits are band stop conditions. Both groups
    are outside this finding and unchanged.
  * **Fixes.** Two local wording problems found by the search were corrected
    before return:
    * step 3 at first spoke only of a failed finalization *barrier*; it now
      covers any failed step of the attempt;
    * C-8's new sentence had made the following *"They are never committed"*
      ambiguous, so it was moved to the end of the cell.
* **Links.** A read-only script resolved every relative Markdown link against
  its file's directory, excluding URLs and in-page anchors. Every file had
  **0 missing**:

  | File | Relative links |
  |---|---|
  | the draft | 18 |
  | this handback | 3 |
  | `Handover information` | 19 |
  | `status.md` | 17 |
  | `implementation-plan.md` | 136 |
  | `disposable-test-server.md` | 69 |

  The new links are the draft's links to the R2 review, the R3 assignment and
  this handback, and the pointer files' links to the same records. All
  resolve.
* **`git diff --check`.**
  * **Tracked files.** Limited to the four tracked files, it printed nothing
    and exited 0.
  * **Untracked files.** `git diff --no-index --check /dev/null <file>`
    printed nothing for the draft or for this handback. Its exit status is not
    relied on, because `--no-index` returns 1 whenever the files differ. A
    direct search found 0 lines with trailing whitespace or tab characters in
    either file.
* **Scoped diff.** Each file was compared with a copy taken before editing:

  | File | Hunks | Lines removed | Lines added | Content |
  |---|---|---|---|---|
  | the draft | 33 | 59 | 144 | only the locations in §2 and §3 |
  | `Handover information` | 5 | 6 | 43 | title, returned block, consumed heading, next handoff |
  | `status.md` | 3 | 3 | 23 | title, returned paragraph, gate steps 1–2 |
  | `implementation-plan.md` | 1 | 1 | 24 | §20's new current action, prior action relabelled |
  | `disposable-test-server.md` | 1 | 0 | 15 | the new first banner |

  The nine earlier durable records in §1 were re-hashed after editing, and
  each matches its pre-edit digest.

## 7. Files read

* `CLAUDE.md`, and `.agents/AGENTS.md` completely.
* `docs/implementation-plan.md`: the reading map; §0, §13, §14, §16 and §20;
  and Phase 5 with its Package 5.0 table and acceptance criteria.
* `docs/review/Handover information`, current.
* `docs/operations/disposable-test-server.md`, its first restriction banners.
* The R3 assignment and the Codex R2 review, both completely.
* The authorization draft at `308e788c…`, completely.
* The R2 handback and the R2 assignment.
* The Codex R1 re-review and the original Codex review, completely.
* `docs/project-management/status.md`, its current section.

## 8. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | amended in place (§2, §3). Untracked before and after |
| `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r3-contract-consistency-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | title; a new returned block; the R3 assignment heading marked consumed; the next-handoff paragraph |
| `docs/project-management/status.md` | title; a returned paragraph; gate-sequence steps 1 and 2 |
| `docs/implementation-plan.md` | §20: a new current action pointing to the amended draft, this handback, the assignment and the R2 review. The prior action is relabelled *Superseded* |
| `docs/operations/disposable-test-server.md` | a new first restriction banner recording the return and that no host action occurred |

Not changed:

* every earlier Codex review, assignment and handback (§1 digests);
* the RAID, decision and change registers;
* any source, test, hook, manifest, generated artifact, migration, schema or
  configuration.

## 9. Git status relevant to this assignment

* **Branch and `HEAD`.** Branch `docs/platform-plan`; `HEAD`
  `2fb1d6fd88013752d53af76fc97b4db07fc31181`, unchanged.
* **Porcelain entries.** 150 before this pass and 151 after. The only new
  entry is this untracked handback. Nothing is staged.
* **Changed files.**
  * The draft was untracked before and remains untracked.
  * `Handover information`, `status.md`, `implementation-plan.md` and
    `disposable-test-server.md` were already modified by earlier uncommitted
    work, and now also carry this pass's hunks (§6.1).
* **Untouched.** No other path was touched. No pre-existing change was
  reverted, restored, staged or committed.

## 10. Checks not run, and why

* **Anything on `oracle-test`.** Prohibited. No command in the draft was
  executed.
* **Test suites, the harness dry run and the A0-06 classifier tests.** This
  was a documentation-only assignment, and the assignment says not to run
  suites.
* **Creating a capture root or record, or any trial of the stop transition.**
  Prohibited. Both are requirements for RP-11's later implementation and
  review, and are unproven here.
* **Re-derivation of the §4.3 pins.** They were unchanged, and §4.3 says so.
* **A secrets scan.** Prohibited.
* **`python3 .claude/hooks/test_guards.py`.** No guard was changed.
* **Formatter, linter and type checker.** No code was changed.

## 11. Security, data-authority and operational implications

* **Security.** The change only narrows the draft:
  * it removes an impossible admission condition;
  * it adds a Pass B stop on any act that would touch Pass A's root;
  * it limits the post-stop write to one non-repeating local attempt.

  It adds no host path, no privilege and no target-side file. C-6's *no file
  on `oracle-test`* and C-11's guard rule are unchanged.
* **Data authority.** No change.
* **Rollback and recovery.** §10 item 9 now states that neither capture root
  is rolled back or cleaned up.
* **Reboot.** MD-3's B6 is unchanged. The §9.5.3 statement that the
  `oracle-test` reboot is not a repository-host interruption is unchanged.

## 12. Proposed Codex review focus

1. OP1-R2-1:
   * Are `_A` and `_B` unambiguous everywhere?
   * Can B0-08 now be satisfied after a successful Pass A without touching
     `_A`?
   * Does the common-parent clause avoid collision and cleanup?
2. OP1-R2-2:
   * Is there now exactly one order: stop, one X-3 attempt, one outcome,
     read-only?
   * Does any remaining clause still require or forbid a write
     inconsistently?
3. The X-1 → no-attempt narrowing (§5 point 1).
4. Whether B0 should additionally verify, read-only, that `_A` is retained
   (§5 point 4).
5. Implementation neutrality. The text should name semantics only, with no
   interface, command or language.

Claude has stopped. The next action is Codex's independent review of the
exact R3-amended bytes. Only a later explicit maintainer decision may accept or
authorize any operational pass.
