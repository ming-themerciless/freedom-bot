# Claude remediation handback — C-P5.0-LAB-I3-R7-R2, correction of the R7-R1 working-tree count — 2026-09-20

Author: Claude (implementing agent for C-P5.0-LAB-I3-R7-R2).
Authorization: **C-P5.0-LAB-I3-R7-R2**, one bounded
**repository-documentation-only** remediation. Returned for **independent Codex
technical, security and evidence re-review**. Codex remains the Independent
Technical, Security and Evidence Reviewer.

**No command of any kind was issued to `oracle-test` by this remediation**, and
none had been issued by the R7-R1 remediation or the R7 pass before it. No SSH,
synchronization, host inspection, `sudo`, verifier invocation, controlled write
or database access occurred. The three protected `/tmp` evidence files —
`/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and `/tmp/fb-i3-r6-filelist.txt` —
were not read, stat'ed, deleted, truncated, overwritten, moved, modified or
reused. No source, test, hook, manifest, generated artifact, migration, schema
or configuration file was changed.

**Nothing here closes a finding.** PR-20260920-LAB-I3-R7-R2-1 is recorded
**Open, Important**. PR-20260920-LAB-I3-R7-R1-1 and PR-20260920-LAB-I3-R7-R1-2
remain **Open, Important** and are **not closed by this remediation** — their
formal disposition is Codex's. PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 are **untouched** and remain **Open, Blocking**. I3 is
not closed, no digest is approved, V7 is not initialized, V8 and V10 are not
performed, `plan.is_executable` is unchanged at `False`, Package 5.0 is not
advanced and `--execute` is not authorized.

---

## 1. Governing context read before editing

Read completely and in full before any file was changed:

* `.agents/AGENTS.md`, in full;
* the implementation-plan **reading map** and **§§0, 12 (including the Phase 5
  work-package table and the Package 5.0 row), 13, 14, 16, 17 and 20**;
* the **active handover**, including the C-P5.0-LAB-I3-R7-R2 assignment, its
  absolute operational restriction and the returned R7-R1 state block;
* the current **disposable-server restriction banner** and its standing
  prohibitions;
* the **authorized R7 prompt**, the **R7 stopped-pass handback** and the
  **R7-R1 remediation handback** under correction; and
* the current **status, RAID, decision and change registers**.

§12 including Package 5.0 was read here, as the assignment requires. As in
R7-R1, **that repairs the documentation record only and does not make the R7
operational pass retroactively compliant**;
PR-20260920-LAB-I3-R7-R1-1 remains an uncured operational-process deviation.

## 2. Git status before this remediation

| Property | Value |
|---|---|
| Branch | `docs/platform-plan` |
| `HEAD` | `2fb1d6fd88013752d53af76fc97b4db07fc31181` |
| Working tree | **86 paths — 34 modified, 52 untracked** |

This starting figure is the state Codex's independent re-review observed after
the R7-R1 remediation completed, and it is the figure whose absence from that
remediation's §5 is the finding under correction. Unrelated, earlier-pass and
reviewer-authored changes were preserved; no file outside the table in §4 was
touched, and none was reclassified.

## 3. The finding, and exactly how it was addressed

### PR-20260920-LAB-I3-R7-R2-1 — the R7-R1 handback understates its completed working-tree count — Open, Important

*Attributed to Codex's independent re-review of the R7-R1 remediation
handback.*

**The finding.** The R7-R1 handback's §2 correctly records **85 paths — 34
modified, 51 untracked** at the **start** of that remediation. Its §5 then
reported `git status` as "85 paths" **before and after**, while §4 of the same
handback identifies the handback itself as a newly created untracked file.
Those two statements cannot both be true: creating a new untracked file raises
the count by one. Codex's re-review observed **86 paths — 34 modified, 52
untracked** after completion.

**The exact correction.** §5's single before-and-after row is replaced by two
rows:

| | Recorded before | Recorded now |
|---|---|---|
| Before the R7-R1 remediation | "85 paths" (shared row) | **85 paths — 34 modified, 51 untracked**, struck-through prior text retained and marked corrected |
| After the R7-R1 remediation | "85 paths" (same shared row) | **86 paths — 34 modified, 52 untracked**, the one added untracked path being the R7-R1 handback itself |

**What was deliberately not done.** §2 was **not** amended. Its 85-path figure
is the correct starting observation, and rewriting it as 86 would falsify the
record of what that remediation actually began from. The prior §5 text is struck
through in place and marked corrected rather than deleted.

**The historical progression now recorded**, consistently across the corrected
handback, the RAID register and the five other controlled documents:

| Point in the record | Paths | Modified | Untracked |
|---|---|---|---|
| R7 stopped-pass handback, as recorded | 84 | 34 | 50 |
| Start of R7-R1, after the stopped-pass handback existed | 85 | 34 | 51 |
| Completion of R7-R1, after its own handback was created | 86 | 34 | 52 |

**A working-tree path count is not an execution digest.** It is a bookkeeping
observation about this repository checkout. Every document touched here states
that in terms, and this correction adds and withdraws no operational evidence
of any kind.

**No substantive R7-R1 result was altered.** The §12 omission remains an uncured
operational-process deviation; the identity claim remains limited to the
measured **50-file review-input set**; the two withdrawn claims stay withdrawn;
manifest version **17**, `COVERED_SOURCES` **47**, digest `c358ea8b…`, aggregate
`4d829dc6…` and the statement that **no target-side comparison exists** stay
retained; the controlled-place count stays **seven**.

**Not closed.** Only independent Codex re-review may close it.

## 4. Files changed, and the exact correction in each

All documentation. No source, test, hook, manifest, generated artifact,
migration, schema or configuration change; **no rollback step is required**, and
reverting any file restores the prior text exactly.

| File | Exact correction |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-i3-r7-r1-erratum-remediation-handback.md` | New dated **§0 erratum** recording PR-20260920-LAB-I3-R7-R2-1 Open, Important, attributed to Codex, with the 84 → 85 → 86 progression, the statement that a path count is not an execution digest, and an explicit note that §2 is not amended. **§5**'s single before-and-after row replaced by two rows: before **85 (34/51)**, prior text struck through and marked corrected; after **86 (34/52)**. New **§6** bullet for the finding. §2 and every substantive result unchanged |
| `docs/review/phase-5-0-reserved-laboratory-i3-r7-r2-count-remediation-handback.md` | This handback (new, untracked) |
| `docs/review/Handover information` | New top state block recording the returned R7-R2 correction with this handback's pointer; the R7-R2 prompt beneath it marked **performed and superseded as the active assignment, retained unaltered**; the prior R7-R1 state block left in place and marked superseded as the current state only |
| `docs/implementation-plan.md` | §20 new current action pointer (independent re-review of C-P5.0-LAB-I3-R7-R2); the prior current action marked superseded **as a pointer only**, with its substantive account and its maintainer decision expressly not superseded |
| `docs/operations/disposable-test-server.md` | New current restriction banner: nothing was issued to the host, the corrected count recorded, the count expressly identified as a repository bookkeeping figure that says nothing about the host, and **every existing prohibition restated as in force**; prior banner marked superseded with its prohibitions unchanged |
| `docs/project-management/status.md` | New current status carrying the correction, the unchanged substantive results and the open decision; prior status marked superseded, its account unchanged and its decision still open |
| `docs/project-management/raid-register.md` | New **Open, Important** item `PR-20260920-LAB-I3-R7-R2-1`, attributed to Codex's independent re-review, recording the progression and the not-an-execution-digest point. Existing R7-R1 and R6 items untouched |
| `docs/project-management/decision-register.md` | Restated open decision at the top: the R7 disposition is **unchanged, open and Peter's alone**, and a bookkeeping count correction neither makes nor narrows it; Codex's recommendation recorded in a separate, expressly non-decisional paragraph; the previous restatement and the original statement retained in full beneath it |
| `docs/project-management/change-log.md` | New append-only row `C-P5.0-LAB-I3-R7-R2` superseding the **working-tree status evidence** of `C-P5.0-LAB-I3-R7-R1`; that earlier row is retained and annotated, not rewritten, and its substantive results are stated as standing. No scope, schedule or risk baseline change |

## 5. Git status after this remediation

| Property | Value |
|---|---|
| Working tree | **87 paths — 34 modified, 53 untracked** |

**Accounting for the change, as the assignment requires.** The starting count was
**86**. Eight of the nine files in §4 were already-modified tracked files and
remain counted once each, so editing them moves no count. The ninth, **this
R7-R2 handback, is a new untracked path**, so the completed count is **86 + 1 =
87 — 34 modified, 53 untracked**. No concurrent workspace change was observed,
and no other explanation is offered or needed. The modified count is unchanged
at 34 because no new tracked file was modified and none was reverted.

The progression across the three passes is therefore **84 → 85 → 86 → 87**, each
step being that pass's own handback becoming a new untracked path.

## 6. Checks run, and checks not run

| Check | Result |
|---|---|
| `git diff --check` | **clean** — no whitespace or conflict-marker error |
| `git status --porcelain` before editing | **86 paths — 34 modified, 52 untracked**, recorded in §2 and matching Codex's re-review observation |
| `git status --porcelain` after editing | **87 paths — 34 modified, 53 untracked**, reconciled in §5 against the starting count plus this handback |
| Count-arithmetic check of the corrected figures | 84 + 1 = 85, 85 + 1 = 86, 86 + 1 = 87; modified stays 34 at every step; untracked 50 → 51 → 52 → 53 |
| R7-R1 §2 preservation check | §2 still reads **85 paths — 34 modified, 51 untracked**; not rewritten as 86 |
| Cross-document consistency of the corrected count | the corrected handback, the RAID register and the five other controlled documents agree on 84 → 85 → 86 and on 86 = 34 + 52 |
| Substantive-result preservation check | the 50-file scope, the two withdrawn claims, manifest version 17, `COVERED_SOURCES` 47, `c358ea8b…`, `4d829dc6…`, the no-target-side-comparison statement and the seven controlled places are unchanged wherever they appear |
| Finding-state consistency | PR-20260920-LAB-I3-R7-R2-1 Open/Important in handback and RAID; both R7-R1 findings still Open/Important and not closed; both R6 findings still Open/Blocking and unedited |
| Decision-openness check | no document asserts the R7 disposition as decided; Codex's recommendation is labelled a recommendation in every place it appears |
| Execution-digest confusion check | every document touched states that a working-tree path count is a bookkeeping observation and not an execution digest |

| Not run | Why |
|---|---|
| `tests/phase_5_0_evidence`, web and bot suites, on either host | not required for a documentation-only remediation and not authorized by this prompt. **No suite figure is offered for this remediation, and none is claimed.** No figure from another tree is cited |
| guard tests `python3 .claude/hooks/test_guards.py` | no hook was changed |
| formatter, linter, type checker, `compileall` | no source file was changed |
| any artifact regeneration or digest recomputation | the recorded hashes are the operational pass's measurement, preserved as returned and not re-measured. No read of `review_manifest` was needed for this correction |
| every action on `oracle-test` — SSH, synchronization, inspection, `sudo`, verifier invocation, controlled write, database access, `/tmp` evidence access | **prohibited by the active restriction**; none attempted |
| V7 initialization, V8, V10, provisioning, preflight, `--execute` | explicitly excluded; not performed |

## 7. Resulting finding states

* **PR-20260920-LAB-I3-R7-R2-1 — Open, Important.** Addressed by the §0 erratum
  and the §5 correction in the R7-R1 handback and recorded in RAID; **not
  closed**.
* **PR-20260920-LAB-I3-R7-R1-1 — Open, Important**, unchanged. The §12 omission
  remains an uncured operational-process deviation; **not closed here**, and its
  formal disposition is Codex's.
* **PR-20260920-LAB-I3-R7-R1-2 — Open, Important**, unchanged. The identity
  claim remains limited to the measured 50-file review-input set; **not closed
  here**, and its formal disposition is Codex's.
* **PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 — Open, Blocking**,
  untouched and unaltered.
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

## 8. The unresolved maintainer decision

**Whether the R7 stop consumes C-P5.0-LAB-I3-R7 is undecided and is Peter
Duscha's decision.** This remediation did not make it, narrow it or prejudge it,
and a corrected path count bears on it not at all.

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

## 9. Stop point and proposed reviewer focus

**The operator stops here for independent Codex technical, security and evidence
re-review**, and takes no further action on this authority.

Proposed reviewer focus:

1. **The corrected counts themselves** — whether 85 (34/51) as the R7-R1
   starting state, 86 (34/52) as its completed state and 87 (34/53) as this
   remediation's completed state are each correct and mutually consistent, and
   whether §5's reconciliation of 86 + this handback = 87 is sound.
2. **§2 preservation** — whether the R7-R1 handback's 85-path starting
   observation survives unrewritten, and whether striking through §5's prior
   text rather than deleting it is the right treatment.
3. **Substantive non-interference** — whether any substantive R7-R1 result was
   altered: the 50-file scope, the withdrawn claims, the retained hashes and
   manifest version, the uncured §12 deviation and the seven controlled places.
4. **Finding discipline** — whether PR-20260920-LAB-I3-R7-R1-1 and
   PR-20260920-LAB-I3-R7-R1-2 are genuinely left open with their disposition
   reserved to Codex, and whether the two R6 Blocking findings are demonstrably
   unaltered.
5. **Decision openness** — whether every document keeps Peter's R7 disposition
   genuinely open and keeps Codex's recommendation visibly separate from it,
   with no place where the recommendation reads as authority.
6. **The not-an-execution-digest framing** — whether any wording anywhere could
   still be read as offering a working-tree path count as operational or
   execution evidence.
7. **Scope discipline** — whether the change set is genuinely documentation
   only, and whether any unrelated or earlier-pass working-tree change was
   disturbed or reclassified.
8. **The change-log treatment** — whether superseding the `C-P5.0-LAB-I3-R7-R1`
   working-tree status evidence by a new append-only row, rather than editing
   that row, satisfies §0.2's append-only correction rule.
