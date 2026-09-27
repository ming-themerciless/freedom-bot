# Claude handback — C-P5.0-R5-OP1-R5 unadmitted-file retention remediation — 2026-09-27

Author: Claude, under the assignment in `docs/review/Handover information`
(2026-09-27) and its controlling prompt,
[`phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-claude-prompt.md`](phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-claude-prompt.md).
The controlling defect list is Codex's
[R4 review](project-review-2026-09-27-p5-r5-operational-evidence-prompt-r4.md),
finding **OP1-R4-1**. Codex remains the Independent Reviewer and did not take
part in this pass.

**Repository-only; documentation only; requirements only.** No command was
issued to `oracle-test` or to any other host. No SSH, synchronization,
inspection, `sudo`, database access, provisioning, verifier, suite, evidence
band, controlled write, reboot or `--execute` occurred. RP-11 was not designed
or implemented. No capture root, record, enumeration or durability sequence
was created, inspected or tested. No source, test, hook, manifest, generated
evidence, migration, schema, infrastructure or configuration was changed. The
protected `/tmp` artifacts were not accessed. No secrets scan was run. No
guard or tool refused a call. Nothing was committed or pushed, and nothing was
restored from `HEAD`.

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
| Draft as reviewed by Codex (R4 review) | `20fa2ce07b391d430569df0e513d687859a1032cfc37bc4c6c0e4dda883b486b` (verified before editing) |
| [R5-amended draft](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md), as returned | `5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3` (1326 → 1360 lines) |
| Original Codex review, **unchanged** | `bc5d7954506ac8d04ad4425c23d06123c5ad633eb8e4dcd055f23791896171a2` |
| Codex R1 re-review, **unchanged** | `71b70fb8f5f4898f8d69cc10df91e48b8b55fbc131879c42acc0b18f9f1a592b` |
| Codex R2 review, **unchanged** | `9722adbfee3e7c553ad9356d28f1bee1b6c7ddf5def623aad6482bf2c6f89d12` |
| Codex R3 review, **unchanged** | `0fd7ffa0bd5dc3337cd3217eec50fc359351995ceaa2c4e9e4a76c0283f0893c` |
| Codex R4 review, **unchanged** | `b72784626c1080260f2548f65612477acb3c914728d063113dddfa0329320a70` |
| Original drafting handback, **unchanged** | `e7db948d4f61938b02d6c8115fd0a1ffcccdbfc5d61115f34dcb0ede6ae24a1b` |
| R1 remediation assignment, **unchanged** | `66e32e9fb6f513787c58a4735e2489961a7054cbbbe6c5afe8f4b4ad50c1b890` |
| R1 remediation handback, **unchanged** | `43f38b508d2803d4e0e93d83252f5bba438639b05eea901c680e9daf28d69382` |
| R2 assignment, **unchanged** | `b1dfd97559ab11f35e470d6b839073f10dd07aa5a2f3b8440be6915b03712f04` |
| R2 handback, **unchanged** | `c191a83cc18d6d922635bbfc965a0dd4b39f5c1593ebfb1af764743401e174c1` |
| R3 assignment, **unchanged** | `dee11c9e6425821552bfc2a2148905c80cc472b074e06a6f4a6d834c9177e36a` |
| R3 handback, **unchanged** | `08acd634bc53b4b29e4199a7da6f5164fd480dd3161d86d0e0d6ab5f33d7d829` |
| R4 assignment, **unchanged** | `3bf3e9d2de73d5d28f915c0ae0c2dcb9830b6c4751017c9502265f87b292144c` |
| R4 handback, **unchanged** | `0e387f9a7fb3b0e74e5c2052c77a59e0d46080dbe387e3d9ad356734c4aa9d8e` |
| R5 assignment, **unchanged** | `a3557db01957deaccd57d36ea5eb59f2cbd41a5e5664342f20ea357af4590c3c` |

The earlier digests equal those in the R4 handback's §1 and the R4 review's
header.

**The central result.** B0-RA now has a fifth condition: **bidirectional
retained-name agreement**. It compares one complete recursive enumeration of
Pass A's root with the set of names Pass A's final state *F* accounts for.

* Every observed name must be accounted for.
* Every accounted name, including every unadmitted name, must be present at
  its exact relative name with its expected object type.

Either non-empty set difference, or any type mismatch, duplicate, alias, escape
from the root or incomplete comparison, is a fail-closed B0 stop before B0-08.

The draft now states the evidentiary limit explicitly. For an unadmitted file,
B0-RA verifies presence, relative name and object type only. It never claims
the file's bytes or metadata are unchanged.

The draft names required semantics only. **RP-11 remains absent and unmet.**

## 2. Exact changes — OP1-R4-1

### 2.1 B0-RA (§7.1)

Conditions (1) to (3) are unchanged. Condition (4) keeps X-4's re-application
to the chain, the admitted records and the bound stream files. Its former last
clause, "every name under the root is accounted for", moves into a new,
stronger condition (5).

**Condition (5) — bidirectional retained-name agreement.**

* **Set *O*, observed.** One complete, recursive enumeration of every name
  under the root, at every depth and not only the root's immediate entries.
  Each name is recorded with its observed object type.
* **Set *R*, accounted.** Formed from *F* and the fixed rules of §9.5.2. Each
  name has its expected object type:
  * *F* itself, each state of *F*'s chain, each listed per-act record and each
    stream file a listed record binds — each a regular file;
  * each subdirectory *F* records the mechanism as having created (C-6) — a
    directory;
  * each object *F* records as unadmitted — at the relative name and object
    type *F* records for it.

  Each accounted name belongs to exactly one category.
* **Observed to recorded.** Every name in *O* is in *R* with the same object
  type.
* **Recorded to observed.** Every name in *R*, including every unadmitted
  name, is in *O* at that exact relative name with its expected object type.
* **Comparison.** Names are compared exactly, in one fixed representation that
  RP-11 defines. No normalization is applied that the comparison did not
  declare.

**Stop conditions.** Each of the following is a fail-closed B0 stop:

* a recorded name absent from *O*, including an absent unadmitted name;
* an observed name not in *R*;
* an object-type mismatch;
* a duplicate or ambiguous name: one accounted for twice or in two
  categories, or two entries the fixed representation cannot tell apart;
* a path alias: a second name for an accounted object, or a symbolic link;
* a name that resolves outside the root;
* an object type that no category expects;
* inability to complete the enumeration or either direction of the
  comparison.

On any of these stops:

* B0-08 does not run;
* no `MI.capture_root_B` is created and no X-1 is performed;
* no Pass B host command is issued;
* nothing under either root is written;
* the check is not retried.

**Evidentiary limit.** This is a new paragraph in B0-RA.

* Conditions (3) and (4) re-derive digests, so they establish the bytes of
  index states, listed records and bound stream files.
* For unadmitted objects and recorded subdirectories, condition (5)
  establishes presence at the recorded relative name with the recorded type
  **only**.
* B0-RA does **not** establish that an unadmitted object's bytes or metadata
  are unchanged.
* No unadmitted object is digested, admitted or used as evidence by the check.

**Other B0-RA changes.**

* The permitted acts now read "list names **and object types**, read bytes and
  re-derive digests".
* A sentence states that the check "runs once and is never retried".
* The *Expected* cell now reads "all **five** conditions hold".

The §7.1 introduction now says that B0-RA checks what the handback **and
Pass A's final state** recorded, within B0-RA's evidentiary limit for
unadmitted files.

### 2.2 The minimal *F* amendment (§3.2 of the assignment)

**What *F* recorded before this change.** X-3 had *F* carry "the names of
every unadmitted file it knows of". Nothing required that name to be relative
to the root. Nothing recorded the object's type. Nothing recorded the
subdirectories the mechanism may create under C-6. Without those fields,
B0-RA would have had to infer them. The following amendments close that gap:

| Location | Change |
|---|---|
| X-3 | *F* records the relative name of every subdirectory the mechanism created under the capture root (C-6), and every unadmitted file it knows of, each by its **exact relative name under the capture root and its object type**. Both are recorded as stated facts and not left to be inferred. *F* records no content digest for an unadmitted file, and none is computed for it later |
| §9.5 preamble | every name a record or index state carries, and every name a handback reports for that pass's capture, is the object's exact relative name under that pass's capture root |
| C-5 | a record binds the exact **relative** names (under the pass's capture root) and digests of its stream files |
| §9.5.2 preamble | an index state is named by a fixed rule **from its state number**; its record list carries each record's **relative** name |

**No content digest was added for an unadmitted file.** The publication
contract does not support one. C-7 says a file whose barrier failed is never
afterwards published. C-8 now says such a file is never digested afterwards to
make it evidence.

### 2.3 Other dependent references

| Location | Change |
|---|---|
| Header | records the R4 review of `20fa2ce0…` and this R5 amendment, and states that the R5 bytes are unreviewed. The Pass B summary adds bidirectional name agreement |
| §4.1 A-1 | adds the R4 review of `20fa2ce0…` to the reviews that are not the required acceptance |
| §4.3 | records that R5 also did not re-derive the pins, and adds `20fa2ce0…` to the superseded prompt digests |
| §4.4 RP-11 | the retention check must also perform the complete recursive, bidirectional name and type comparison. For unadmitted objects it establishes presence, relative name and type only, never unchanged bytes or metadata. The proof obligation reserved to RP-11 now also covers safe relative-name resolution and detecting duplicate or ambiguous names, path aliases, traversal outside the root and unexpected object types |
| §9.1 primary-evidence row | unadmitted files are reported by exact relative name and object type. B0-RA verifies their presence, name and type, not their content |
| §9.4 | B0-RA's result covers five conditions, including each direction of the condition-5 comparison and every name in either set difference (or `none`). For an unadmitted object it is evidence of presence, relative name and type only |
| C-8 | retention of unadmitted files is kept. B0-RA's summary adds the bidirectional comparison, so an absent unadmitted file stops Pass B as an absent record does. It states that retention of an unadmitted file is **required**, but only its presence, relative name and type are **verified**. Its content is unverified, and it is never digested afterwards to make it evidence |
| C-12 | each handback also states the mechanism-created subdirectories, and every unadmitted file by exact relative name and object type, as its final state records them |
| X-4 | the closing B0-RA sentence now describes the bidirectional comparison. It states that neither X-4 nor B0-RA establishes an unadmitted file's content |
| §9.5.3 *Unadmitted files* | recorded in *F* and reported by exact relative name and object type. Such a file is never digested to make it evidence. B0-RA later verifies its presence, name and type, not its content |
| §10 item 9 | unadmitted files are retained "as records of the failure, never as admitted evidence". Previously they were grouped with stream files, records and index states as "evidence". B0-RA's read includes the bidirectional name and type check. On failure, no absent or mistyped name is re-created or replaced |
| §11.2 A0/B0/B1 row | the B0-RA failure list now names each condition-5 failure. The earlier one-directional "name not accounted for" is replaced |
| §11.3 | a failed or incomplete enumeration or name-set comparison is never retried |
| §14 template | the Pass B B0-RA line now records bidirectional agreement, with both set differences stated (`none` when passed). A stopped check lists each offending name. The line states that the check verifies presence, name and type of unadmitted files, not their content. The Pass A line records that B0-RA compares the root with every relative name and type *F* records. There is a new line for mechanism-created subdirectories. The *Unadmitted files* line takes exact relative names and object types, and states that their content is not digested or verified and that they are not evidence |
| Final draft reminder | B0-RA must also have verified bidirectional name agreement |

## 3. Controls deliberately not changed

The draft was diffed against the `20fa2ce0…` bytes, which were copied aside
before editing. There are 26 hunks, all in the locations listed in §2. A
read-only script confirmed that the following are **byte-identical** to the
reviewed bytes:

* C-1 … C-4, C-6, C-7, C-9 … C-11, C-13 … C-15;
* X-1, X-2 and P-1 … P-8;
* the B0-08 row;
* the MD-1 … MD-6 table;
* §4.7, §6 (Pass A), §7.2 … §7.7, the §8 matrix, §9.5.1, and §12 … §13;
* the five steps of the §9.5.3 stop transition, and its closing paragraph on
  Pass B.

As a result:

* **OP1-R3-1's other parts are preserved.** Conditions (1) to (3) of B0-RA
  are unchanged. Condition (4) still covers the chain, admitted records and
  bound streams. Barrier success is still inherited from the digest-pinned
  handback.
* **OP1-R2-1 is preserved.**
  * The roots stay distinct, and neither lies within the other.
  * Each root has one genesis state, chain, final state and handback binding.
  * C-6, C-14 and B0-08 are unchanged.
* **OP1-R2-2 is preserved.**
  * The ordered stop transition is unchanged.
  * No X-3 attempt is made after an interruption or without a durable *I*-0.
  * X-3 still creates only *F*. It now records more fields in *F*, but
    performs no new write.
* **B0-RA's placement is preserved.** It still runs after the B0 repeats and
  before B0-08, Pass B's X-1 and every Pass B host command. It stays
  non-mutating and one-shot.
* OP1-R1, OP1-R2, OP1-R3 and OP1-R1-1 remain resolved as before.

The controlling state is unchanged:

* P5.0-R5 remains Blocking;
* OD-62 G-A remains conditional;
* `plan.is_executable=False`;
* Package 5.0 remains not ready.

RP-1 … RP-12, A-6 and every other unresolved prerequisite remain fail-closed.
Pass A observations are still never RP-1 inputs. Row 40 is not deferred. B6
and RR-11/RR-14/RR-16 are unchanged. JNL-40(b) stays excluded. The client
transcript remains non-evidence, raw streams remain separately retained, and
published evidence remains immutable.

## 4. Unresolved prerequisites after this remediation

| Blocker | State |
|---|---|
| **RP-11** | **Unmet.** It now also owes the recursive, bidirectional comparison. A separately assigned implementation pass must choose the interfaces, the fixed name representation, and the method for resolving paths and detecting duplicates, aliases, escapes and unexpected types. It must prove those choices on the accepted filesystem, including that the check changes nothing. The mechanism must then be independently reviewed and pinned |
| `MI.pass_a_handback` | unsupplied. No Pass A handback exists |
| RP-1 … RP-10, RP-12 | unchanged and unmet |
| A-6 / MD-5 | unmet: no independent acceptance record |
| `MI.pinned_commit`, `MI.pinned_commit_B`, `MI.capture_root_A`, `MI.capture_root_B`, `MI.run_record_path`, `MI.target_fact_statement` and the other §4.5 inputs | unsupplied |

Points for Codex and the maintainer. Each arises from the correction, and none
is decided here:

1. **Directories are a sixth accounted category.** The assignment lists five
   categories. C-6 permits the mechanism to create subdirectories under the
   root, and a complete recursive enumeration will observe them. Without a
   category for them, any subdirectory would stop Pass B. The draft therefore
   has *F* record each mechanism-created subdirectory by relative name, with
   the expected type directory. Presence and type are verified; nothing more
   is claimed. Codex should confirm this addition. The alternative is to
   forbid subdirectories under C-6, which would change a control this
   assignment preserves.
2. **Chain-state names come from the fixed naming rule.** *F* carries its
   predecessor's digest and each state carries its own number. The draft
   takes each chain state's relative name from §9.5.2's fixed naming rule
   applied to that number. It does not add a recorded predecessor name. Codex
   may prefer each state to carry its predecessor's relative name explicitly.
3. **A recorded unadmitted name that never existed stops Pass B.** Suppose
   the mechanism records an unadmitted temporary name whose creation failed
   before any entry existed. The recorded-to-observed direction then fails.
   This fails closed. RP-11 should record as unadmitted only entries it knows
   to exist. The draft does not state this.
4. **Strict accounting is kept.** An unadmitted name counts only if *F*
   records it (R4 point 3). The Pass A handback's own list is reported, but
   is not a source for *R*.
5. **Metadata of admitted objects.** B0-RA's digests establish bytes. They do
   not establish owner, mode (C-7's `0600`/`0700`) or timestamps, for
   admitted objects or for unadmitted ones. The draft now says this for
   unadmitted objects. It did not add a metadata claim or a check for
   admitted objects, because the assignment does not ask for one.
6. **Pass A's own X-4 is unchanged.** Its condition that "every published
   record under the pass's capture root is either listed in *F* or named in
   it as unadmitted" was not made bidirectional. The bidirectional comparison
   is a B0-RA requirement only.
7. **Enumeration at one moment.** The comparison is over one enumeration. A
   change made while the enumeration runs, or after it, is not addressed
   beyond the existing "moment of the check" limit. The assignment excludes a
   monitor. How RP-11 detects an inconsistent enumeration is part of its proof
   obligation. An enumeration RP-11 cannot show to be complete is an
   incomplete comparison, and therefore a stop.

## 5. Validation performed

Only repository-local documentation checks were run, as assignment §6 lists.

1. **Complete term searches.** The amended draft was searched for every term
   the assignment names: `unadmitted`, `accounted`, `every name`, `B0-RA`,
   `retained`, `X-4`, `relative name`, `object type` and `content`. Every hit
   was read in context.
   * `unadmitted` (38 occurrences), `accounted`, `every name`, `relative
     name` and `object type`: every hit is in a location listed in §2, or is
     unchanged text consistent with it.
   * **`content`**: the hits outside §2 are A-5, RP-6, A1-33, §7.5's "minimum
     content", C-9 and §12's "digests, not contents". None of them concerns
     capture retention.
   * **`B0-RA`, `X-4`, `retained`**: the hits outside §2 are unchanged
     R4 text on ordering, read-only use and generic retention. They are
     consistent with the correction.
   * **Stale phrasing.** Searches for `four conditions` (1 hit: S4-3's
     unrelated "four conditions" in §4.3), `all four`, `names of every`,
     `reported by name` and `are evidence` show that no stale B0-RA or
     unadmitted phrasing remains.
2. **Set-difference model.** Each direction was traced to the text that
   stops Pass B before B0-08:

   | Case | Where it stops |
   |---|---|
   | *O* ∖ *R* non-empty (an unexpected name) | B0-RA *Expected*: "an observed name not in *R*"; §11.2 row |
   | *R* ∖ *O* non-empty (for example, a deleted unadmitted file) | B0-RA *Expected*: "a recorded name absent from *O* (including an absent unadmitted name)"; §11.2 row; C-8 |
   | same name, wrong type | B0-RA *Expected*; §11.2 row |

   Each case leads to no B0-08, no `_B`, no X-1 and no host command.
   §9.5.3's unchanged closing paragraph confirms there is no X-3 attempt.
3. **Recursive relative names and types are consistent** across RP-11, B0-RA,
   the §9.5 preamble, C-5, C-8, C-12, §9.5.2, X-3, X-4, §9.5.3, §9.1, §9.4,
   §10, §11.2 and §14.
4. **No content-integrity claim for undigested unadmitted objects.** Every
   location that describes B0-RA's effect on unadmitted objects limits it to
   presence, name and type. The locations that say they are retained
   "unmodified" state C-8's requirement, not a verified property. §10 item 9
   no longer calls them "evidence". X-3, C-8 and §9.5.3 forbid digesting them
   later to make them evidence.
5. **Non-mutating, one-shot and ordered.** B0-RA's permitted acts are listing
   names and types, reading and digesting. It "runs once and is never
   retried", and §11.3 repeats this. The §7.1 order, the X-1 text and the
   B0-08 row are unchanged.
6. **OP1-R2-1, OP1-R2-2 and the rest of OP1-R3-1** were checked by the
   byte-identity check in §3.
7. **Relative links** resolve (§5.1).
8. **`git diff --check`**, limited to the changed documentation files (§5.1).
9. **Scoped diff inspection**, and a survey of the pre-existing worktree
   (§5.1, §8).

### 5.1 Results

* **Links.** A read-only script resolved every relative Markdown link against
  its file's directory, after percent-decoding, excluding URLs and in-page
  anchors. Every file has **0 missing**. Before decoding, the pre-existing
  `Handover%20information` links appear missing; they resolve once decoded.
* **Whitespace.**
  * **Tracked files.** `git diff --check`, limited to the four tracked
    files, printed nothing and exited 0.
  * **Untracked files.** A direct search found 0 lines with trailing
    whitespace or tab characters in the draft and in this handback.
* **Scoped diff.** Each file was compared with a copy taken before editing.
* **Durable records.** Every earlier durable record in §1 was hashed after
  editing and matches.

| File | Relative links | Hunks | Lines removed | Lines added | Content |
|---|---|---|---|---|---|
| the draft | 24 | 26 | 36 | 70 | only the locations in §2 |
| this handback | 3 | — | — | new | — |
| `Handover information` | 31 | 5 | 6 | 38 | title, returned block, R5 assignment heading marked consumed, next handoff |
| `status.md` | 25 | 5 | 4 | 21 | title, the R5 paragraph and a returned paragraph, gate steps 1–2 |
| `implementation-plan.md` | 152 | 1 | 1 | 22 | §20's new current action; the prior action relabelled *Superseded* |
| `disposable-test-server.md` | 79 | 1 | 0 | 17 | the new first banner |

## 6. Files read

* `CLAUDE.md`, and `.agents/AGENTS.md` completely.
* `docs/implementation-plan.md`:
  * the reading map;
  * §0, §13, §14, §16 and §20;
  * Phase 5 with its Package 5.0 table.
* `docs/review/Handover information`, current.
* `docs/operations/disposable-test-server.md`, its first restriction
  banners.
* The R5 assignment and the Codex R4 review, both completely.
* The authorization draft at `20fa2ce0…`, completely.
* The R4 handback, completely.
* `docs/project-management/status.md`, its current section and gate
  sequence.

## 7. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | amended in place (§2). Untracked before and after |
| `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r5-unadmitted-retention-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | the title; a new returned block; the R5 assignment heading marked consumed; the next-handoff paragraph |
| `docs/project-management/status.md` | the title; the R5 assignment paragraph set to past tense; a returned paragraph; gate-sequence steps 1 and 2 |
| `docs/implementation-plan.md` | §20: a new current action pointing to the amended draft, this handback, the assignment and the R4 review. The prior action is relabelled *Superseded* |
| `docs/operations/disposable-test-server.md` | a new first restriction banner recording the return and that no host action occurred |

Not changed:

* every earlier Codex review, assignment and handback (§1 digests);
* the RAID, decision and change registers;
* any source, test, hook, manifest, generated artifact, migration, schema or
  configuration.

Consumed blocks in `Handover information` were not moved to a dated archive
snapshot. Earlier passes did not move them either, and this assignment does
not ask for it.

## 8. Git status relevant to this assignment

* **Branch and `HEAD`.** Branch `docs/platform-plan`; `HEAD`
  `2fb1d6fd88013752d53af76fc97b4db07fc31181`, unchanged.
* **Porcelain entries.** 156 before this pass and 157 after. The only new
  entry is this untracked handback. Nothing is staged.
* **Changed files.**
  * The draft and the R5 assignment were untracked before this pass. Both are
    still untracked, and the assignment was not edited.
  * `Handover information`, `status.md`, `implementation-plan.md` and
    `disposable-test-server.md` were already modified by earlier uncommitted
    work. They now also carry this pass's hunks.
* **Untouched.** No other path was touched. No pre-existing change was
  reverted, restored, staged or committed.

## 9. Checks not run, and why

* **Anything on `oracle-test` or another host.** Prohibited. No command in
  the draft was executed.
* **Test suites, the harness dry run and the A0-06 classifier tests.** This
  was a documentation-only assignment, and the assignment says not to run
  suites.
* **Creating, inspecting or testing a capture root, an enumeration, a
  retention check or a durability sequence.** Prohibited. These are
  requirements for RP-11's later implementation and review, and are unproven
  here.
* **Re-derivation of the §4.3 pins.** They were unchanged, and §4.3 says so.
* **A secrets scan.** Prohibited.
* **`python3 .claude/hooks/test_guards.py`.** No guard was changed.
* **Formatter, linter and type checker.** No code was changed.

## 10. Security, data-authority and operational implications

* **Evidence integrity.** The change only narrows the draft. Deleting,
  renaming or retyping any name that Pass A's final state accounts for now
  stops Pass B, provided it happens before B0-RA. This includes unadmitted
  files and mechanism-created subdirectories. So does adding an unexpected
  name.
* **No new access.** The change adds no host path, no privilege, no
  target-side file and no write. B0-RA's access to Pass A's root is still
  read-only.
* **Residual.** Two limits remain, and the draft states both:
  * the content and metadata of unadmitted files are not verified;
  * a change after B0-RA is not detected.
* **Data authority.** No change.
* **Rollback and recovery.** A failed B0-RA is never repaired, and no absent
  or mistyped name is re-created.

## 11. Proposed Codex review focus

1. Does condition 5 establish both directions over a complete recursive
   relative-name set, with object types? Does every failure named by OP1-R4-1
   stop Pass B before B0-08?
2. Does any clause still claim, or imply, unchanged content for an undigested
   unadmitted object, or treat one as admitted evidence?
3. Is the minimal *F* amendment (§2.2) sufficient, so that *R* is formed
   without inference? In particular, see point 1 (directories) and point 2
   (chain-state names) of §4.
4. Implementation neutrality. The text should name semantics and detection
   obligations only, with no API, language or command.
5. Are OP1-R2-1, OP1-R2-2 and the rest of OP1-R3-1 preserved?

Claude has stopped. The next action is Codex's independent review of the
exact R5-amended bytes. Only a later explicit maintainer decision may accept or
authorize any operational pass.
