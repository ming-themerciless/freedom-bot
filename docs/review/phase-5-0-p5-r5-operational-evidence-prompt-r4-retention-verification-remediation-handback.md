# Claude handback — C-P5.0-R5-OP1-R4 Pass A retention-verification remediation — 2026-09-27

Author: Claude, under the assignment in `docs/review/Handover information`
(2026-09-27) and its controlling prompt,
[`phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-claude-prompt.md).
The controlling defect list is Codex's
[R3 review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r3.md),
finding **OP1-R3-1**. Codex remains the Independent Reviewer and did not take
part in this pass.

**Repository-only; documentation only; requirements only.** No command was
issued to `oracle-test` or to any other host. No SSH, synchronization,
inspection, `sudo`, database access, provisioning, verifier, suite, evidence
band, controlled write, reboot or `--execute` occurred. RP-11 was not designed
or implemented. No capture root, record or durability sequence was created,
inspected or tested. No source, test, hook, manifest, generated evidence,
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
| Draft as reviewed by Codex (R3 review) | `026edf43935fb8a837911d66f467596e5ebfe31a4da1135e576f0c03a4dd69f7` (verified before editing) |
| [R4-amended draft](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md), as returned | `20fa2ce07b391d430569df0e513d687859a1032cfc37bc4c6c0e4dda883b486b` (1289 → 1326 lines) |
| Original Codex review, **unchanged** | `bc5d7954506ac8d04ad4425c23d06123c5ad633eb8e4dcd055f23791896171a2` |
| Codex R1 re-review, **unchanged** | `71b70fb8f5f4898f8d69cc10df91e48b8b55fbc131879c42acc0b18f9f1a592b` |
| Codex R2 review, **unchanged** | `9722adbfee3e7c553ad9356d28f1bee1b6c7ddf5def623aad6482bf2c6f89d12` |
| Codex R3 review, **unchanged** | `0fd7ffa0bd5dc3337cd3217eec50fc359351995ceaa2c4e9e4a76c0283f0893c` |
| Original drafting handback, **unchanged** | `e7db948d4f61938b02d6c8115fd0a1ffcccdbfc5d61115f34dcb0ede6ae24a1b` |
| R1 remediation assignment, **unchanged** | `66e32e9fb6f513787c58a4735e2489961a7054cbbbe6c5afe8f4b4ad50c1b890` |
| R1 remediation handback, **unchanged** | `43f38b508d2803d4e0e93d83252f5bba438639b05eea901c680e9daf28d69382` |
| R2 assignment, **unchanged** | `b1dfd97559ab11f35e470d6b839073f10dd07aa5a2f3b8440be6915b03712f04` |
| R2 handback, **unchanged** | `c191a83cc18d6d922635bbfc965a0dd4b39f5c1593ebfb1af764743401e174c1` |
| R3 assignment, **unchanged** | `dee11c9e6425821552bfc2a2148905c80cc472b074e06a6f4a6d834c9177e36a` |
| R3 handback, **unchanged** | `08acd634bc53b4b29e4199a7da6f5164fd480dd3161d86d0e0d6ab5f33d7d829` |
| R4 assignment, **unchanged** | `3bf3e9d2de73d5d28f915c0ae0c2dcb9830b6c4751017c9502265f87b292144c` |

The earlier digests equal those recorded in the R3 handback's §1.

**The central result.** Pass B now has a separately identified admission step,
**B0-RA**. It runs after the B0 repeats and before B0-08, and therefore before
X-1 creates `MI.capture_root_B` and before any Pass B host command. B0-RA is a
reviewed, **non-mutating** check that binds Pass A's retained root and final
index state to the Pass A handback and re-applies X-4 to the retained
evidence. Any failure is a fail-closed B0 stop.

The draft names required semantics only. **RP-11 remains absent and unmet.**

## 2. Exact changes — OP1-R3-1

### 2.1 The check (new B0-RA, §7.1)

The §7.1 introduction now fixes the order:

1. repeat A0-01 … A0-07 and A0-09;
2. **B0-RA**;
3. **B0-08**, only after B0-RA has succeeded.

B0-RA is `⟨RP-11.retention_check⟩`. It runs on the repository host, with no
host contact.

**Preconditions it checks.** B0-RA first:

* re-derives the SHA-256 of `⟨MI.pass_a_handback⟩` and requires it to equal
  the supplied digest; and
* requires that handback to record:
  * an X-3 outcome of *succeeded at the finalization point*;
  * X-4 validity *valid*;
  * a final index state name and capture index SHA-256 other than `none`.

**The four required conditions**, as the assignment lists them:

1. `⟨MI.capture_root_A⟩` is exactly, byte for byte, the root recorded in the
   Pass A handback.
2. That root exists, and the final index state the handback names (Pass A's
   *F*) exists under it under that name.
3. The SHA-256 re-derived over *F*'s bytes equals the handback's capture index
   SHA-256.
4. X-4 still succeeds for Pass A's retained evidence:
   * *F* is the only final state;
   * its chain is intact back to Pass A's *I*-0;
   * its record list is gap-free and equals the last durable open state's;
   * every listed record, and every stream file it binds, exists with its
     digest;
   * **every name under the root is accounted for by *F***: as *F* itself, a
     state of its chain, a listed record, a bound stream file, or a file *F*
     names as unadmitted.

**The barrier-success condition of X-4 is not re-observed.** It is a fact about
how Pass A published, not a property of the retained bytes. B0-RA takes it from
the Pass A handback's X-3 and X-4 lines. The draft says so explicitly rather
than claiming B0-RA re-verifies it.

**Permitted acts.** The check may only list names under `⟨MI.capture_root_A⟩`,
read bytes and re-derive digests.

**Forbidden acts.** It must not:

* write, move, rename, truncate, complete, repair, adopt, delete or change the
  permissions of the root or anything beneath it;
* create anything under it;
* use any of it as Pass B evidence;
* continue, copy or reuse Pass A's index chain.

**Result and stop.**

* B0-RA's result is recorded in the Pass B handback as an **admission result,
  not a Pass B capture record**, because no Pass B root exists yet.
* A failure is a **fail-closed B0 stop**. The failures are absence, a
  mismatch, an X-4 failure, an unaccounted name, or inability to complete the
  check. On a stop:
  * B0-08 does not run;
  * no `MI.capture_root_B` is created and no X-1 is performed;
  * no Pass B host command is issued;
  * nothing under either root is written;
  * the stop is not retried.

**Limit.** B0-RA establishes retention **at the moment of the check only**. It
does not monitor, protect or guarantee Pass A's root afterwards, and the draft
claims nothing about a later change.

B0-08 itself is unchanged except for two points. It now runs only after B0-RA
has succeeded. Its clause "Pass A's root is not used" now reads "nothing of
Pass A's root is used as Pass B evidence".

### 2.2 Inputs and RP-11 (§4.4, §4.5)

| Location | Change |
|---|---|
| §4.4 RP-11 | RP-11 must also provide `⟨RP-11.retention_check⟩` with the four conditions and the read-only limits above. The implementation-neutral sentence now also reserves to RP-11 the proof that the check changes nothing under `⟨MI.capture_root_A⟩`. The *Blocks* column adds **B0-RA** |
| §4.5 `MI.capture_root_A` | "retained, unmodified and unused" becomes "**retained and unmodified, and never used as Pass B evidence**". It adds that Pass B's only access is B0-RA's read-only retention check. The *Used by* column replaces "Never used by Pass B" with "B0-RA, read-only, as a retention check only. Never Pass B evidence" |
| §4.5 new `MI.pass_a_handback` | the repository path and SHA-256 of the Pass A handback, supplied in Pass B's A-2 authorization. From those exact bytes B0-RA takes the root, the final state's name, the capture index SHA-256, and the X-3 and X-4 lines. These are taken **as recorded, never re-typed, inferred or supplied by the operator**. The input is a typed blocker: no Pass A handback exists |
| §4.5 `MI.capture_root_B` | *Used by* now reads "B0-08, only after B0-RA has succeeded" |

### 2.3 Capture contract (§9.5)

| Location | Change |
|---|---|
| §9.5 preamble | Pass B's only access to Pass A's root is B0-RA's read-only verification: it lists names, reads bytes and re-derives digests, writes nothing and uses nothing as Pass B evidence. This reconciles the existing "nothing … listed … under the other pass's root" with a read-only listing |
| C-8 | "retained, unmodified and unused" becomes "retained and unmodified, and never used as Pass B evidence". Pass B's admission depends on B0-RA, which is summarized with its fail-closed rule and its moment-of-check limit |
| C-12 | each handback also states its X-4 validity, matching the §14 template. The Pass A handback states its root exactly, byte for byte, because B0-RA verifies against it. A Pass A handback with no admissible final state gives B0-RA nothing to verify, so Pass B is not admitted |
| X-1 | Pass B's admission check is "B0-RA's successful retention verification of Pass A's root and then B0-08" |
| X-4 | appends that B0-RA re-applies X-4 to Pass A's retained evidence. It is read-only, runs before Pass B's X-1, requires every name to be accounted for by *F*, and takes barrier success from the handback. It never writes, completes, repairs, adopts or reconstructs anything |
| §9.5.3 closing paragraph | a B0-RA stop precedes Pass B's X-1. There is no Pass B root, no *I*-0, no X-3 attempt, nothing to make read-only, and no host command |

C-6, C-7, C-10, C-14, C-15, X-2 and X-3 are **byte-identical** to the
reviewed bytes (§6.1).

### 2.4 Other dependent references

| Location | Change |
|---|---|
| Header | records the R3 review of `026edf43…` and this R4 amendment, and states that the R4 bytes are unreviewed. The Pass B summary adds B0-RA as an admission requirement, before `MI.capture_root_B` is created or any host command |
| §4.1 A-1 | adds the R3 review of `026edf43…` to the reviews that are not the required acceptance |
| §4.3 | records that R4 also did not re-derive the pins, and lists `026edf43…` among the superseded prompt digests |
| §9.1 primary-evidence row | "unused" becomes "never used as Pass B evidence". Adds that Pass B reads Pass A's root only in B0-RA, which must succeed before Pass B's root is created |
| §9.4 | for Pass B, the B0-RA result against the Pass A handback, with the outcome of each of its four conditions, is a review input |
| §10 item 9 | B0-RA only reads Pass A's root. If B0-RA fails, nothing is repaired, completed, restored or re-created; the failure is reported and Pass B does not start |
| §11.2 A0/B0/B1 row | new stop: *B0-RA not satisfied*, with each failure case listed, as a fail-closed stop before B0-08. New stop: *B0-08 attempted without a successful B0-RA*. The existing stop on acts under `_A` is widened to the full forbidden list (write, move, rename, truncate, complete, repair, adopt, delete or change permissions), including during B0-RA, and adds use as Pass B evidence |
| §11.3 | adds a failed or incomplete B0-RA to what is never retried |
| §14 template | Pass B's capture-root line allows "not created (stopped at B0-RA)". The Pass B line records the B0-RA outcome, marked as an admission result and not a measured fact, with its moment-of-check limit. It states that Pass A's root was read only by B0-RA and not written, moved, renamed or removed, nor used as Pass B evidence. A new Pass A line requires the root to be stated byte for byte, since it, the final state name and the digest are B0-RA's inputs. The X-3 line was reflowed only |
| Final draft reminder | Pass B additionally needs `MI.pass_a_handback` and a successful B0-RA |

After the change, the draft contains **no occurrence of "unused"** (§6.1).

## 3. Controls deliberately not changed

The draft was diffed against the `026edf43…` bytes, which were copied aside
before editing. There are 22 hunks, all in the locations listed in §2. A
read-only script confirmed that the following are **byte-identical** to the
reviewed bytes:

* the MD-1 … MD-6 table;
* §4.7, §6 (Pass A, including A0-08), §7.2 … §7.7, the §8 matrix, §9.5.1,
  and §12 … §13;
* the five steps of the §9.5.3 stop transition;
* C-1 … C-7, C-9 … C-11, C-13 … C-15, X-2 and X-3.

As a result:

* OP1-R1, OP1-R2, OP1-R3 and OP1-R1-1 remain resolved as before;
* **OP1-R2-1** is preserved. The two roots stay distinct, and neither lies
  within the other. Each has its own genesis state, chain, final state and
  handback binding. C-6 and C-14 are unchanged. B0-08's distinctness and
  absence checks are unchanged. Pass A's root is still never removed,
  renamed, reused or modified to admit Pass B;
* **OP1-R2-2** is preserved. §9.5.3's ordered transition is unchanged, as is
  the no-X-3 rule after an interruption or without a durable *I*-0. B0-RA
  adds no write and no X-3 attempt.

The controlling state is unchanged: P5.0-R5 remains Blocking, OD-62 G-A
conditional, `plan.is_executable=False`, and Package 5.0 not ready. RP-1 …
RP-12, A-6 and every other unresolved prerequisite remain fail-closed. Pass A
observations are still never RP-1 inputs. Row 40 is not deferred. B6 and
RR-11/RR-14/RR-16 are unchanged. JNL-40(b) stays excluded.

## 4. Unresolved prerequisites after this remediation

| Blocker | State |
|---|---|
| **RP-11** | **Unmet.** It now also owes `⟨RP-11.retention_check⟩`. A separately assigned implementation pass must choose its interface, language and filesystem-resolution method. It must also prove the check changes nothing under `_A` on the accepted filesystem. The mechanism must then be independently reviewed and pinned |
| **`MI.pass_a_handback`** | **new, unsupplied.** No Pass A handback exists, because Pass A has not run |
| RP-1 … RP-10, RP-12 | unchanged and unmet |
| A-6 / MD-5 | unmet: no independent acceptance record |
| `MI.pinned_commit`, `MI.pinned_commit_B`, `MI.capture_root_A`, `MI.capture_root_B`, `MI.run_record_path`, `MI.target_fact_statement` and the other §4.5 inputs | unsupplied |

Points for Codex and the maintainer. Each arises from the correction, and none
is decided here:

1. **Barrier success is inherited, not re-verified.** X-4's "its barriers
   succeeded" cannot be read from the retained bytes. B0-RA takes it from the
   Pass A handback's X-3 and X-4 lines. Codex should confirm that this reading
   of condition 4 is acceptable.
2. **Pass A handback preconditions.** The draft makes explicit that a Pass A
   handback recording a failed or absent X-3, an inconclusive X-4, or `none`
   for the final state or digest blocks Pass B. This follows from conditions 2
   and 3, which have nothing to check otherwise. It means an inconclusive Pass
   A capture cannot be followed by Pass B under this draft.
3. **"Accounted for by the final state" is strict.** An unadmitted name counts
   as accounted for only if *F* itself names it. A file the Pass A handback
   reports as unadmitted but that *F* does not name therefore stops Pass B.
   For example, X-3 names only the unadmitted files "it knows of". This
   follows the assignment's wording and fails closed. Codex may prefer the
   handback's unadmitted list to count as well.
4. **Presence of named unadmitted files is not checked.** C-8 retains
   unadmitted files, but the assignment's four conditions do not ask B0-RA to
   confirm that each file *F* names as unadmitted still exists. They have no
   recorded digest. This pass did not add that check.
5. **Read-time metadata.** Listing and reading can update access-time metadata
   on some filesystems. Whether that counts as modification under C-8, and how
   the check avoids it, is left to RP-11's proof of non-mutation. The draft
   names this proof obligation but does not choose a method.
6. **Where the B0-RA result lives.** It precedes Pass B's root, so it cannot
   be a Pass B capture record. The draft records it in the Pass B handback as
   an admission result, like the other B0 local checks. Codex should confirm
   that an uncaptured local admission result is acceptable here.
7. **`MI.pass_a_handback` is pinned by digest.** A later dated correction to
   the Pass A handback would change its digest, so the Pass B authorization
   must name the exact bytes relied on.

## 5. Validation performed

Only repository-local documentation checks were run, as assignment §6 lists.

1. **Complete term searches.** The amended draft was searched for
   `capture_root_A`, `retained`, `unmodified`, `unused`, `B0-08`, `X-4`,
   `final index` and `capture index SHA-256`, and also for the new `B0-RA` and
   `pass_a_handback`. Every hit was read in context.
   * **`unused`: 0 hits remain.** The three earlier hits (§4.5, §9.1 and C-8)
     are reconciled to "never used as Pass B evidence". The related "not
     used" wording in B0-08 and the §14 template is narrowed in the same
     way.
   * **`capture_root_A`, `B0-08`, `X-4`, `final index`, `capture index
     SHA-256`.** Every hit either concerns Pass A's own capture and is
     unchanged, or is one of the reconciled locations in §2.
   * **`retained`, `unmodified`.** The hits outside §2 describe other retained
     objects and are unchanged: the V-items, the PostgreSQL recovery captures,
     retained recovery inputs, and the generic C-8 and C-15 retention of each
     pass's evidence.
2. **Pass B admission order.** B0 runs, in order: the repeats, B0-RA, then
   B0-08 with X-1. The steps that state or depend on this order agree: §7.1,
   §4.5 `_B`, X-1, the §9.1 row and the §11.2 row. B0 issues no host command.
   Every host command follows X-1 (C-6, X-1, B0-08).
3. **Every failure mode stops fail-closed without modifying either root.** The
   failure modes are: handback digest mismatch; an unsuccessful X-3, invalid
   X-4 or `none` in the handback; a root mismatch; an absent root or final
   state; a digest mismatch; an X-4 failure; an unaccounted name; and
   incomplete verification. Each is listed in B0-RA's *Expected* cell and the
   §11.2 row. Each leads to: no B0-08, no `_B`, no X-1, no host command, and
   nothing written under either root. §9.5.3's closing paragraph confirms
   there is no X-3 attempt.
4. **Read-only use of Pass A's root, never as Pass B evidence.** This is
   stated in §4.5, the §9.5 preamble, C-8, X-4, B0-RA, B0-08, §9.1, §10 item 9,
   the §11.2 row and the §14 template. None of those locations permits a
   write, or use as Pass B evidence. C-12 and C-14 still forbid binding a Pass
   B row to Pass A's records or continuing Pass A's chain.
5. **OP1-R2-1 and OP1-R2-2 remain resolved.** See §3.
6. **Relative links** resolve (§5.1).
7. **`git diff --check`**, limited to the changed documentation files.
8. **Scoped diff inspection**, and a survey of the pre-existing worktree.

### 5.1 Results

* **Links.** A read-only script resolved every relative Markdown link against
  its file's directory, excluding URLs and in-page anchors. Every file has
  **0 missing**:

  | File | Relative links |
  |---|---|
  | the draft | 21 |
  | this handback | 3 |
  | `Handover information` | 25 |
  | `status.md` | 21 |
  | `implementation-plan.md` | 144 |
  | `disposable-test-server.md` | 74 |

  The new links point to the R3 review, the R4 assignment and this handback.
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
  | the draft | 22 | 29 | 66 | only the locations in §2 |
  | `Handover information` | 4 | 7 | 48 | title, returned block, R4 assignment heading marked consumed, next handoff |
  | `status.md` | 5 | 4 | 22 | title, the R4 paragraph and a returned paragraph, gate steps 1–2 |
  | `implementation-plan.md` | 1 | 1 | 22 | §20's new current action; the prior action relabelled *Superseded* |
  | `disposable-test-server.md` | 1 | 0 | 16 | the new first banner |

  Every earlier durable record in §1 was hashed after editing and matches.

## 6. Files read

* `CLAUDE.md`, and `.agents/AGENTS.md` completely.
* `docs/implementation-plan.md`: the reading map; §0, §13, §14, §16 and §20;
  and Phase 5 with its Package 5.0 table.
* `docs/review/Handover information`, current.
* `docs/operations/disposable-test-server.md`, its first restriction banners.
* The R4 assignment and the Codex R3 review, both completely.
* The authorization draft at `026edf43…`, completely.
* The R3 handback, completely, and the R3 assignment.
* The Codex R2 review, completely.
* `docs/project-management/status.md`, its current section and gate sequence.

## 7. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | amended in place (§2). Untracked before and after |
| `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | title; a new returned block; the R4 assignment heading marked consumed; the next-handoff paragraph |
| `docs/project-management/status.md` | title; the R4 assignment paragraph set to past tense; a returned paragraph; gate-sequence steps 1 and 2 |
| `docs/implementation-plan.md` | §20: a new current action pointing to the amended draft, this handback, the assignment and the R3 review. The prior action is relabelled *Superseded* |
| `docs/operations/disposable-test-server.md` | a new first restriction banner recording the return and that no host action occurred |

Not changed:

* every earlier Codex review, assignment and handback (§1 digests);
* the RAID, decision and change registers;
* any source, test, hook, manifest, generated artifact, migration, schema or
  configuration.

Consumed blocks in `Handover information` were not moved to a dated archive
snapshot. The R3 pass did not move them either, and the assignment did not
ask for it.

## 8. Git status relevant to this assignment

* **Branch and `HEAD`.** Branch `docs/platform-plan`; `HEAD`
  `2fb1d6fd88013752d53af76fc97b4db07fc31181`, unchanged.
* **Porcelain entries.** 153 before this pass and 154 after. The only new
  entry is this untracked handback. Nothing is staged.
* **Changed files.**
  * The draft and the R4 assignment were untracked before this pass. Both are
    still untracked, and the assignment was not edited.
  * `Handover information`, `status.md`, `implementation-plan.md` and
    `disposable-test-server.md` were already modified by earlier uncommitted
    work. They now also carry this pass's hunks (§5.1).
* **Untouched.** No other path was touched. No pre-existing change was
  reverted, restored, staged or committed.

## 9. Checks not run, and why

* **Anything on `oracle-test` or another host.** Prohibited. No command in
  the draft was executed.
* **Test suites, the harness dry run and the A0-06 classifier tests.** This
  was a documentation-only assignment, and the assignment says not to run
  suites.
* **Creating, inspecting or testing a capture root, record, retention check
  or durability sequence.** Prohibited. These are requirements for RP-11's
  later implementation and review, and are unproven here.
* **Re-derivation of the §4.3 pins.** They were unchanged, and §4.3 says so.
* **A secrets scan.** Prohibited.
* **`python3 .claude/hooks/test_guards.py`.** No guard was changed.
* **Formatter, linter and type checker.** No code was changed.

## 10. Security, data-authority and operational implications

* **Security and evidence integrity.** The change only narrows the draft:
  * Pass B can no longer be admitted after Pass A's retained evidence was
    removed or changed, provided the change happened before the check;
  * the only new access to Pass A's root is read-only;
  * the forbidden-act list for Pass A's root is widened.

  It adds no host path, no privilege, no target-side file and no write.
* **Residual.** Changes to Pass A's root after B0-RA are not detected by this
  draft, and the draft says so. The assignment excludes a continuous monitor
  and an immutability mechanism.
* **Data authority.** No change.
* **Rollback and recovery.** §10 item 9 adds that a failed B0-RA is never
  repaired. A retention failure is reported, and Pass B does not start.

## 11. Proposed Codex review focus

1. Do the four B0-RA conditions match OP1-R3-1 exactly? Does B0-RA precede
   `MI.capture_root_B` creation and every Pass B host command?
2. Does every failure mode stop fail-closed with nothing written under either
   root?
3. Is Pass A's root consistently read-only for Pass B, and never Pass B
   evidence? Does any remaining clause still say it is wholly unused, or
   permit more than listing, reading and digesting?
4. The seven points in §4, especially the inherited barrier-success condition
   (point 1) and the strict accounting rule (point 3).
5. Implementation neutrality. The text should name semantics only, with no
   interface, command or language.

Claude has stopped. The next action is Codex's independent review of the
exact R4-amended bytes. Only a later explicit maintainer decision may accept or
authorize any operational pass.
