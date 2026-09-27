# Claude remediation handback — C-P5.0-LAB-I3-R7-R1, documentation reconciliation of the independent R7 stopped-pass review — 2026-09-20

Author: Claude (implementing agent for C-P5.0-LAB-I3-R7-R1).
Authorization: **C-P5.0-LAB-I3-R7-R1**, one bounded
**repository-documentation-only** remediation. Returned for **independent Codex
technical, security and evidence re-review**. Codex remains the Independent
Technical, Security and Evidence Reviewer.

**No command of any kind was issued to `oracle-test` by this remediation**, and
none had been issued by the R7 pass it corrects. No SSH, synchronization, host
inspection, `sudo`, verifier invocation, controlled write or database access
occurred. The three protected `/tmp` evidence files — `/tmp/fb-i3-root.out`,
`/tmp/fb-i3-root.err` and `/tmp/fb-i3-r6-filelist.txt` — were not read, stat'ed,
deleted, truncated, overwritten, moved, modified or reused. No source, test,
hook, manifest, generated artifact, migration, schema or configuration file was
changed.

**Nothing here closes a finding.** PR-20260920-LAB-I3-R7-R1-1 and
PR-20260920-LAB-I3-R7-R1-2 are recorded **Open, Important**.
PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 are **untouched** and remain
**Open, Blocking**. I3 is not closed, no digest is approved, V7 is not
initialized, V8 and V10 are not performed, `plan.is_executable` is unchanged at
`False`, Package 5.0 is not advanced and `--execute` is not authorized.

---

## 0. Erratum — C-P5.0-LAB-I3-R7-R2, 2026-09-20 — the completed working-tree count was understated

*Added by the bounded, repository-documentation-only C-P5.0-LAB-I3-R7-R2
remediation. It corrects one count in §5 of this handback and records one new
finding. It changes no substantive result of the R7-R1 remediation: the two
withdrawn claims stay withdrawn, the retained hashes stay retained, the §12
omission stays an uncured operational-process deviation, the identity claim
stays limited to the measured 50-file review-input set, the controlled-place
count stays seven, both R6 findings stay Open and Blocking, and I3 stays
unconfirmed.*

**PR-20260920-LAB-I3-R7-R2-1 — the R7-R1 handback understates its completed
working-tree count — Open, Important.** *Raised by Codex's independent
re-review of this handback.*

§2 of this handback correctly records **85 paths — 34 modified and 51
untracked** as the state at the **start** of the R7-R1 remediation. §5 then
reported "85 paths" for `git status` **before and after**, while §4 of the same
handback identifies this handback as a newly created untracked file. Both
statements cannot be true: creating a new untracked file raises the count.
Codex's independent re-review observed **86 paths — 34 modified and 52
untracked** after the R7-R1 remediation completed.

The historical progression is therefore:

| Point in the record | Paths | Modified | Untracked |
|---|---|---|---|
| R7 stopped-pass handback, as recorded | 84 | 34 | 50 |
| Start of the R7-R1 remediation, after the stopped-pass handback existed (§2, correct as written) | 85 | 34 | 51 |
| Completion of the R7-R1 remediation, after this handback was created (§5, corrected below) | 86 | 34 | 52 |

§2 is **not** amended: its 85-path figure is the correct starting observation
and rewriting it as 86 would falsify the record. §5's row is corrected in place
to distinguish the starting state from the completed state.

**A working-tree path count is not an execution digest.** It is a bookkeeping
observation about this repository checkout, and this correction neither adds
nor withdraws operational evidence of any kind.

**Not closed.** PR-20260920-LAB-I3-R7-R2-1 is recorded **Open, Important**;
only independent Codex re-review may close it. This erratum does not close
PR-20260920-LAB-I3-R7-R1-1 or PR-20260920-LAB-I3-R7-R1-2, whose formal
disposition remains Codex's.
[R7-R2 remediation handback](phase-5-0-reserved-laboratory-i3-r7-r2-count-remediation-handback.md).

## 1. Governing context read before editing

Read completely and in full before any file was changed:

* `.agents/AGENTS.md`, in full;
* the implementation-plan **reading map** and **§§0, 12 (including the Phase 5
  work-package table and the Package 5.0 row), 13, 14, 16, 17 and 20**,
  including the §20 Package 5.0 action pointers;
* the **active handover**, including the C-P5.0-LAB-I3-R7-R1 assignment, its
  absolute operational restriction and the R7 state banner;
* the current **disposable-server restriction banner** and its standing
  prohibitions;
* the **authorized R7 prompt**, including its governing-context section (which
  is where the §12 requirement sits) and its guard-refusal and artifact rules;
* the **R7 stopped-pass handback** in full; and
* the current **status, RAID, decision and change registers**.

§12 is listed here because the finding under remediation is precisely its
omission from the operational pass's inventory. **Reading it now repairs the
documentation record only. It does not make the R7 operational pass
retroactively compliant, and it is not offered as doing so.**

## 2. Git status at the start of this remediation

| Property | Value |
|---|---|
| Branch | `docs/platform-plan` |
| `HEAD` | `2fb1d6fd88013752d53af76fc97b4db07fc31181` |
| Working tree | 85 paths — 34 modified, 51 untracked |

The R7 stopped-pass handback recorded 84 paths (34 modified, 50 untracked); the
one added untracked path is that handback itself. Unrelated, earlier-pass and
reviewer-authored changes were preserved. No file outside the table in §4 was
touched.

## 3. The findings, and exactly how each was addressed

### 3.1 PR-20260920-LAB-I3-R7-R1-1 — required Phase 5 context was skipped — Open, Important

*Attributed to Codex's independent review of the stopped-pass handback.*

**The finding.** The authorized R7 prompt's governing-context section required
implementation-plan **§12 (Package 5.0)** to be read before acting. The
implementation plan's reading map states that skipping a required section **is a
defect**. The stopped-pass handback's §2.1 inventory is exhaustive by intent and
omits §12.

**How it was addressed.** Recorded as an **operator process deviation on the
operational pass** in the handback's §0 erratum, in the §2.1 marked correction,
in the RAID register as its own **Open, Important** item, and in the handover,
§20, restriction banner, status and change-log summaries.

**What was deliberately not done.** §2.1's inventory was **not** amended to list
§12. §12 was not read during the operational pass, and editing the inventory
would have falsified the record of what that pass actually read. Every summary
states in terms that the later remediation does not cure the deviation.

**Not closed.** Only independent Codex re-review may close it.

### 3.2 PR-20260920-LAB-I3-R7-R1-2 — workspace identity exceeded the measured evidence — Open, Important

*Attributed to Codex's independent review of the stopped-pass handback.*

**The finding.** The reported aggregate covers exactly **50 files** — the 47
`review_manifest.COVERED_SOURCES` entries, the two generated artifacts and
runner contract r6. It covers neither the complete workspace nor every path the
repository-wide §3.2 synchronization would have transferred.

**The two claims withdrawn**, verbatim as they were returned:

| Location | Withdrawn claim |
|---|---|
| §2 introduction | "the read-only repository identity work that establishes what a synchronization **would have carried**" |
| §2.3 | "The **workspace tree** is therefore byte-for-byte the accepted manifest-version-17 tree." |

**What replaced them.** The §2 introduction now scopes the work to "the 50-file
review-input set defined in §2.3". §2.3's conclusion now states only what was
measured: **these 50 review-input files are byte-for-byte the corresponding
files of the accepted manifest-version-17 review-input set**, saying nothing
about the rest of the workspace or about the other paths a repository-wide §3.2
synchronization would have transferred. The original §2.3 sentence is struck
through in place and marked withdrawn rather than deleted; §2.3's heading
changed from "Source-tree identity" to "Review-input-set identity".

**Retained exactly as returned**, and confirmed present after editing:

| Retained | Value |
|---|---|
| `MANIFEST_VERSION` | 17 |
| `COVERED_SOURCES` count | 47 |
| Reproduced review-input digest | `c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26` |
| 50-file aggregate | `4d829dc6b2f3279cd2f660b0c02b5ee17bf40d8982dffa4fa46c82b6e1cfa12d` |
| All five artifact and spot digests | unchanged |
| Interpreter | local `python3` 3.12.3 |
| No-target-side-comparison statement | retained and repeated in the erratum |

**No digest was recomputed by this remediation.** The recorded hashes are the
operational pass's measurement, preserved as returned. The only read-only
inspection performed here was a count check confirming
`len(review_manifest.COVERED_SOURCES) == 47` and `MANIFEST_VERSION == 17`,
which is the arithmetic behind "50". No artifact was regenerated, and no file
was written by that check.

**Not closed.** Only independent Codex re-review may close it.

### 3.3 Controlled-place count — Optional, corrected in place

"all five controlled places" was inaccurate against its own enumeration. It now
reads **seven documents**: the active handover, implementation-plan §20, the
disposable-server restriction banner, and the status, RAID, decision and change
registers. The enumeration itself is unchanged.

## 4. Files changed, and the exact correction in each

All documentation. No source, test, hook, manifest, generated artifact,
migration, schema or configuration change; **no rollback step is required**, and
reverting any file restores the prior text exactly.

| File | Exact correction |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-i3-r7-stopped-pass-handback.md` | New dated **§0 erratum** recording both findings Open, Important, attributed to Codex, and stating what the erratum does not do. Marked in-place corrections at **§2** (withdraws "would have carried"), **§2.1** (records the §12 omission as an uncured process deviation; corrects "five" to "seven") and **§2.3** (heading narrowed; whole-tree claim struck through and replaced by the measured 50-file statement). New marked bullet in **§6**. Historical account, denial text, command text, timestamps, hashes and the no-host-command statement preserved |
| `docs/review/phase-5-0-reserved-laboratory-i3-r7-r1-erratum-remediation-handback.md` | This handback (new) |
| `docs/review/Handover information` | New top state block recording the returned remediation, both findings Open/Important, the withdrawn claims and the retained evidence, with the handback pointer; the R7-R1 assignment beneath it marked **superseded as the active assignment and retained unaltered** |
| `docs/implementation-plan.md` | §20 new current action pointer (independent re-review of C-P5.0-LAB-I3-R7-R1); the prior current action marked superseded **as a pointer only**, with its maintainer decision expressly still open |
| `docs/operations/disposable-test-server.md` | New current restriction banner: nothing was issued to the host, both findings recorded, the narrowed 50-file scope stated, and **every existing prohibition restated as in force**; prior banner marked superseded with its prohibitions unchanged |
| `docs/project-management/status.md` | New current status with the same narrowed scope and open decision; prior status marked superseded, its account unchanged and its decision still open |
| `docs/project-management/raid-register.md` | Two new **Open, Important** items, `PR-20260920-LAB-I3-R7-R1-1` and `PR-20260920-LAB-I3-R7-R1-2`, attributed to Codex; dated update appended to `LAB-I3-R7-STOP-1` recording Codex's recommendation **separately from Peter's undecided decision** |
| `docs/project-management/decision-register.md` | Restated open decision at the top: the R7 disposition is **unchanged, open and Peter's alone**; Codex's recommendation recorded in a separate, expressly non-decisional paragraph; the original statement retained in full beneath it |
| `docs/project-management/change-log.md` | New append-only row `C-P5.0-LAB-I3-R7-R1` superseding the **evidence wording** of `C-P5.0-LAB-I3-R7-H1`; the earlier row is retained and annotated, not rewritten. No scope, schedule or risk baseline change |

## 5. Checks run, and checks not run

| Check | Result |
|---|---|
| `git diff --check` | **clean** — no whitespace or conflict-marker error |
| `git status` before this remediation | ~~85 paths; the only additions are this handback and the edits in §4; no unrelated change disturbed~~ **Corrected by the §0 erratum (PR-20260920-LAB-I3-R7-R2-1).** Before: **85 paths — 34 modified, 51 untracked**, as recorded in §2 |
| `git status` after this remediation | **86 paths — 34 modified, 52 untracked.** The one added untracked path is this handback itself; the remaining §4 entries are edits to already-modified tracked files. No unrelated or earlier-pass change was disturbed |
| `COVERED_SOURCES` count / manifest version, read-only in-process | **47** and **17**, matching the handback's figures and the arithmetic behind the 50-file set |
| Cross-document consistency of the narrowed claim | the seven controlled documents and the handback agree on the 50-file scope, the two withdrawn claims and the retained hashes |
| Finding-state consistency | both new findings Open/Important in handback and RAID; both R6 findings still Open/Blocking and unedited |
| Decision-openness check | no document asserts the R7 disposition as decided; Codex's recommendation is labelled a recommendation in every place it appears |

| Not run | Why |
|---|---|
| `tests/phase_5_0_evidence`, web and bot suites, on either host | not required for a documentation-only remediation and not authorized. **No suite figure is offered for this remediation, and none is claimed.** No figure from another tree is cited |
| guard tests `python3 .claude/hooks/test_guards.py` | no hook was changed |
| formatter, linter, type checker, `compileall` | no source file was changed |
| any artifact regeneration or digest recomputation | the recorded hashes are the operational pass's measurement and are preserved as returned, not re-measured |
| every action on `oracle-test` — SSH, synchronization, inspection, `sudo`, verifier invocation, controlled write, database access, `/tmp` evidence access | **prohibited by the active restriction**; none attempted |
| V7 initialization, V8, V10, provisioning, preflight, `--execute` | explicitly excluded; not performed |

## 6. Resulting state

* **PR-20260920-LAB-I3-R7-R1-1 — Open, Important.** Addressed by erratum and
  recorded in RAID; **not closed**.
* **PR-20260920-LAB-I3-R7-R1-2 — Open, Important.** Addressed by erratum, the
  narrowed claim and reconciliation of the seven controlled documents; **not
  closed**.
* **PR-20260920-LAB-I3-R7-R2-1 — Open, Important.** *Added by the §0 erratum.*
  Raised by Codex's independent re-review of this handback: §5 understated the
  completed working-tree count. Corrected in §5 to distinguish the 85-path
  starting state from the **86-path completed state (34 modified, 52
  untracked)**; **not closed**.
* **PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 — Open, Blocking**,
  untouched and unaltered by this remediation.
* **I3 remains unconfirmed and not closed.** This remediation produced no
  operational evidence of any kind.
* **`oracle-test` is in exactly the state the R6 record and the restriction
  banner describe**, because nothing was issued to it. The operator observed
  nothing on the host and asserts nothing about it beyond that it was not
  contacted.
* V7 remains excluded. V8 and V10 remain unperformed. `plan.is_executable` is
  `False` and was not touched. `reservation.REAL_EXECUTION_REFUSAL` is
  untouched. Package 5.0 remains **not ready**. LAB-SECRETS-1 remains Open, Low.
  LAB-V6-P2 remains deferred.
* `c358ea8b…` remains **review input only** — not approval, not an I3
  confirmation, and never authority for `--execute`.

## 7. The unresolved maintainer decision

**Whether the R7 stop consumes C-P5.0-LAB-I3-R7 is undecided and is Peter
Duscha's decision.** This remediation did not make it, narrow it or prejudge it.

Recorded **separately** from that decision: Codex **recommends** treating
C-P5.0-LAB-I3-R7 as consumed and requiring fresh authority for any future
operational pass. Under implementation-plan §0.3 an Independent Reviewer
recommends and Peter records the decision. **The operator has not converted that
recommendation into a maintainer decision or into operational authority, and no
host authority exists on its strength.**

The secondary question recorded under RAID `LAB-I3-R7-STOP-1` also remains open:
whether a future R7-equivalent prompt must state in terms how an operator
handles a harness-level permission denial that is not a repository-guard
refusal.

## 8. Stop point and proposed reviewer focus

**The operator stops here for independent Codex technical, security and evidence
re-review**, and takes no further action on this authority.

Proposed reviewer focus:

1. **The erratum's preservation discipline** — whether the historical account,
   exact denial text, command text, timestamps, hashes and the no-host-command
   statement survive intact, and whether marking corrections in place rather
   than editing the original text is the right treatment for each of the three.
2. **PR-20260920-LAB-I3-R7-R1-1's framing** — whether recording the §12 omission
   as an uncured operator process deviation, and deliberately **not** adding §12
   to the pass's inventory, is correct, or whether any wording still implies
   retroactive compliance.
3. **The narrowed identity claim** — whether "these 50 review-input files are
   byte-for-byte the corresponding files of the accepted manifest-version-17
   review-input set" is now exactly coextensive with what was measured, in the
   handback and in each of the seven controlled documents, with no residual
   whole-workspace or would-have-transferred implication.
4. **Decision openness** — whether every document keeps Peter's R7 disposition
   genuinely open and keeps Codex's recommendation visibly separate from it,
   with no place where the recommendation reads as authority.
5. **Scope discipline** — whether the change set is genuinely documentation
   only, whether the two R6 Blocking findings are demonstrably unaltered, and
   whether any unrelated or earlier-pass working-tree change was disturbed.
6. **The change-log treatment** — whether superseding the `C-P5.0-LAB-I3-R7-H1`
   evidence wording by a new append-only row, rather than editing that row,
   satisfies §0.2's append-only correction rule.
