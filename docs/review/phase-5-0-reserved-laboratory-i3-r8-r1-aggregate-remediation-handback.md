# Claude remediation handback — C-P5.0-LAB-I3-R8-R1; the R8 aggregate explanation, corrected and measured — 2026-09-21

Author: Claude (implementing agent for C-P5.0-LAB-I3-R8-R1).
Authorization: the bounded **repository-only** assignment recorded at the head
of `docs/review/Handover information`, accepted and assigned by Peter Duscha on
2026-09-21. Codex remains the Independent Technical, Security and Evidence
Reviewer and did not perform this remediation.

**No command of any kind was issued to `oracle-test`.** No SSH, no
synchronization, no host inspection, no verifier invocation, no suite, no
database access, and no read, `stat` or change of the three protected `/tmp`
evidence artifacts. No source, test, hook, manifest, generated artifact,
migration, schema or configuration file was changed. Nothing is closed:
**LAB-I3-R8-AGGREGATE-1 remains Open, Important**, PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**, I3 remains performed but
unconfirmed and not closed, V7 remains excluded, V8 and V10 remain unperformed,
`plan.is_executable=False`, and Package 5.0 remains **not ready**.

> **Erratum, 2026-09-22 — C-P5.0-LAB-I3-R8-R2, recording Codex's re-review of
> this handback under LAB-I3-R8-AGGREGATE-1 (still Open, Important).** Two
> corrections, both to this document's own claims; **no result of the
> remediation it reports is withdrawn**.
>
> 1. **The causal overclaim.** §4 said the divergence between the two records
>    is *accounted for* by the calculation, and §9 repeated it. It is not. The
>    reproduced calculation shows a **possible** explanation; it does not
>    establish the historical cause and does not recover R6's formula. The
>    cause is **unresolved**. §4, §9 and §10 are corrected below.
> 2. **The candidate count.** §3 reported that two candidate descriptions
>    reproduced `f4120970…` while R8 erratum §3.3 reported exactly one match
>    per value. §3 now counts under **one explicit convention** — distinct
>    calculations, with candidate descriptions reported separately — and R8
>    §3.3 is restated to match. *(Corrected 2026-09-22 under
>    C-P5.0-LAB-I3-R8-R3, LAB-I3-R8-R2-COUNT-1, Open, Important: as returned
>    this item said "Both figures were correct under different conventions and
>    neither said which it used." **§3's own figure of two candidate
>    descriptions was right in its unit**; R8 §3.3's "exactly one of 960
>    candidates" **mixed the two units and was ambiguous, indeed wrong, as
>    written**, and is not validated retroactively.)*
>
> The measured values are unchanged: the four-row table, `c358ea8b…`,
> `MANIFEST_VERSION` 17, and `ce275fd3…`, `66855575…`, `206e40b2…` all stand as
> recorded, and were re-measured on 2026-09-22 under C-P5.0-LAB-I3-R8-R2.
> [R8-R2 remediation handback](phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md).

---

## 1. The finding addressed

**LAB-I3-R8-AGGREGATE-1 — Important, evidence precision.** The R8 handback
reported a 50-file aggregate of `f4120970…` where R6 had recorded `4d829dc6…`
for the described 50-file set, and attributed the difference to *different
line-joining formulas*. Because R6's record does not state a joining formula,
that explanation was **unproven** — an offered cause standing where a measured
one was required. Neither aggregate may be silently discarded, and neither may
be treated as comparable to the other without a documented common calculation.

## 2. What was done

One correction, in one place, plus the register reconciliation that records it.

**R8 handback §3.3 is corrected in place, under a dated erratum.** The
withdrawn sentence is named and the reason for its withdrawal is stated; the
surrounding evidence is untouched. §3.3 now states:

1. **both recorded aggregate values**, each attributed to its record;
2. **the formula each record actually documents** — R8's completely (line
   format, ordering key, join, trailing-newline rule), R6's as **line format
   only**, with its ordering key, join separator and trailing-newline rule
   expressly recorded as *not stated*;
3. **the limit of the comparison** — that as returned the two numbers are not
   comparable, and neither confirms nor discards the other; and
4. **a common-formula calculation reproduced entirely from local repository
   files**, with its exact input set, ordering, line format and
   trailing-newline rule, and its result.

## 3. The calculation, stated so a reviewer can re-run it

Performed on 2026-09-21 in the repository workspace at branch
`docs/platform-plan`, `HEAD` `2fb1d6f`, with local `python3` 3.12.3. It reads
repository files and computes hashes; it invokes no part of the evidence harness
and touches nothing outside this checkout.

**Input set — 50 files.** The 47 `COVERED_SOURCES` entries, derived in-process
from `tools/phase_5_0_evidence/review_manifest.py` rather than from any list,
plus `docs/review/phase-5-0-evidence-harness-concrete-plan.md`,
`docs/review/phase-5-0-evidence-harness-review-manifest.json` and
`docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md`.

**Line format.** `<sha256-hex>` + two spaces + `<path>`, the path spelled
relative to the repository root exactly as `COVERED_SOURCES` spells it.

**Join and encoding.** A single `\n` between lines; the joined text encoded
UTF-8 (the input is ASCII) and hashed with SHA-256.

**The two rules varied.** The ordering key — the whole line, or the path — and
the trailing newline — present, or absent.

```python
lines = [f"{sha256_hex_of(path)}  {path}" for path in the_fifty_paths]
lines.sort(key=...)                      # whole line, or path
blob = "\n".join(lines) + ("\n" if trailing else "")
aggregate = sha256(blob.encode()).hexdigest()
```

**Result.**

| Ordering | Trailing newline | Aggregate | |
|---|---|---|---|
| sorted by path | present | `4d829dc6b2f3279cd2f660b0c02b5ee17bf40d8982dffa4fa46c82b6e1cfa12d` | **equals the R6/R7-recorded value** |
| sorted by path | absent | `1e9f7f5a4444d602b98bcec292360b7bdba93420eff6347b1cbba01b8808ed53` | — |
| sorted by whole line | present | `f88f2ac6321a8f6c8bc3df278f317703c90e40802bdd1f9c6dde4f4a9a168743` | — |
| sorted by whole line | absent | `f4120970ac7615b50944b1a2ab27fd689ab37782c282fe9680f7240cad52df36` | **equals the R8-recorded value** |

**Search breadth, so the two matches are not mistaken for luck — counted under
one explicit convention.** Two units are counted, and they are not the same:

* a **candidate description** is one point in the enumerated parameter space;
* a **distinct calculation** is one distinct byte string actually hashed. Two
  descriptions producing the same byte string are the same calculation.

**960 candidate descriptions** were enumerated — four path spellings
(repository-relative, `./`-prefixed, basename only, absolute) × eight line
formats (digest-first and path-first, each with two spaces, one space, a tab or
no separator between the fields) × three ordering keys (whole line, path,
digest) × five separators (`\n`, none, space, `\r\n`, NUL) × trailing separator
present or absent. They denote **612 distinct calculations**, which produced
612 distinct aggregate values.

**Exactly one distinct calculation reproduced each recorded value:**

| Recorded value | Candidate descriptions matching | Distinct calculations matching |
|---|---|---|
| `4d829dc6…` (R6/R7) | 1 | 1 |
| `f4120970…` (R8) | 2 | 1 |

The two descriptions reproducing `f4120970…` are the **same** calculation:
under the digest-first line format, ordering by the whole line and ordering by
the digest are the same ordering, because all 50 digests are distinct. Under
that same line format ordering by the path is a different ordering, so
`4d829dc6…` is reproduced by one description only. *(Annotated 2026-09-22 under
C-P5.0-LAB-I3-R8-R2; as returned this paragraph reported the
candidate-description counts without naming the convention, which read as a
disagreement with R8 §3.3. Further corrected 2026-09-22 under
C-P5.0-LAB-I3-R8-R3, LAB-I3-R8-R2-COUNT-1: the counts reported here were
**right in their unit** — two candidate descriptions for `f4120970…`, one for
`4d829dc6…`. The disagreement arose from R8 §3.3's "exactly one of 960
candidates", which mixed the units and was wrong as written.)*

**The input bytes are independently pinned as unchanged.** The review-input
digest reproduces as
`c358ea8b2298151f40bb16c7c5783e6fa195e959d5309decff7a3e9f143cca26` over the 47
covered sources, by the deterministic non-executing generation path
(`build_concrete_plan()` → `ReviewManifest.build(plan, read_covered_sources())`
→ `.digest()`), with `MANIFEST_VERSION` **17**. The three remaining files hash
to their individually recorded values: `ce275fd3…`, `66855575…` and
`206e40b2…`. So the 50 files this calculation read are byte-for-byte the 50
files the R6, R7 and R8 records describe.

## 4. What this establishes, and what it deliberately does not

*Corrected 2026-09-22 under C-P5.0-LAB-I3-R8-R2. As returned, this section said
the divergence was "accounted for by the calculation". It is not; that was an
overclaim, and the text below replaces it.*

**Established — the bytes.** No byte of the measured 50-file set differs
between the records. The review-input digest reproduces as `c358ea8b…` over the
47 covered sources at `MANIFEST_VERSION` 17, and the three remaining files hash
to their individually recorded `ce275fd3…`, `66855575…` and `206e40b2…`. The
divergence therefore **cannot be explained by a change in those bytes**.

**Established — a possibility.** Both recorded values are reproducible from
exactly those bytes by two calculations differing only in the ordering key and
the trailing-newline rule. This shows the two records *can* diverge with no
byte differing.

**Not established.** That this is what happened. A calculation that reproduces
a value is **a possible explanation, not the historical cause**. The cause of
the divergence is **unresolved**.

**Not established, and not inferred.** What calculation R6 actually executed.
R6's record documents no ordering key and no trailing-newline rule; a matching
value is not a retrieval of an undocumented formula and **does not recover R6's
formula**, and no such inference is drawn. The correction likewise does not
assert as fact that the two operators "used different formulas" — only that the
two **records document different calculations, one of them incompletely**. Both
the cause of the mismatch and the specific R6 calculation are **unresolved**,
and only a record from that pass could resolve either.

**Untouched.** The historical R6 aggregate and its surrounding record are not
rewritten, anywhere they appear. No new target-side measurement was made or
claimed. The R8 execution record, safe verifier output, timestamps, individual
hashes and source-to-target claims stand at their measured scope.

## 5. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-handback.md` | §3.3 corrected in place under a dated erratum; the unproven "different line-joining formulas" assertion withdrawn and replaced by the two documented formulas, the limit of the comparison, the reproduced common-formula calculation and the residual uncertainty |
| `docs/review/phase-5-0-reserved-laboratory-i3-r8-r1-aggregate-remediation-handback.md` | **new** — this handback |
| `docs/review/Handover information` | new active state block; the assignment block above it marked accepted, assigned and consumed |
| `docs/implementation-plan.md` | §20 current action replaced; the prior action retained as superseded |
| `docs/operations/disposable-test-server.md` | banner note recording that this remediation issued no host command and changed no restriction |
| `docs/project-management/status.md` | new current status; prior status retained as superseded |
| `docs/project-management/raid-register.md` | **LAB-I3-R8-AGGREGATE-1** recorded Open, Important |
| `docs/project-management/decision-register.md` | pending-decision entry noting the finding is outstanding and I3 closure remains undecided |
| `docs/project-management/change-log.md` | entry **C-P5.0-LAB-I3-R8-R1** |

No source, test, hook, manifest, generated artifact, migration, schema or
configuration file appears in that list, and none was changed.

## 6. Checks run

| Check | Result |
|---|---|
| `git diff --check` | clean, before and after |
| Aggregate reproduction, 960 candidate descriptions (612 distinct calculations) over the 50-file set | exactly one distinct calculation matched each recorded value; both are recorded in §3 |
| Review-input digest reproduction over the 47 covered sources | `c358ea8b…`, `MANIFEST_VERSION` 17, `COVERED_SOURCES` 47 |
| Individual digests of the three non-covered files | `ce275fd3…`, `66855575…`, `206e40b2…` — all equal to their recorded values |
| Cross-document consistency of the two aggregates and the finding ID | the R6/R7 value is unaltered wherever it appears; the finding ID is spelled identically in every document |

## 7. Checks not run, and why

| Not run | Why |
|---|---|
| Both pytest suites and the Node contract tests | Out of scope. This is a documentation-only remediation that changes no source, test or artifact, and the assignment authorizes no suite. **No suite figure is offered, cited or claimed.** |
| Any command on `oracle-test` | **Expressly prohibited.** No host action of any kind is authorized. |
| Any target-side re-measurement of either aggregate | Prohibited and unnecessary; the correction is a repository-only evidence-precision fix. |
| Any re-measurement of the R6 pass's own calculation | Impossible from the repository. R6's formula is not recorded, and no artifact of that calculation exists here. |
| Formatter, linter, type checker | No code changed. |

## 8. Repository state

| | |
|---|---|
| Branch / `HEAD` | `docs/platform-plan` / `2fb1d6f` |
| Working tree before this remediation | **91 paths — 34 modified, 57 untracked** |
| Working tree after this remediation | **92 paths — 34 modified, 58 untracked**; the one added path is this handback |
| `git diff --check` | clean, before and after |

Unrelated and earlier-pass working-tree changes were inspected and
**preserved**; none was touched, reclassified or reverted. No commit, push,
rebase, amend, reset or history rewrite was performed or attempted.

## 9. Remaining uncertainty

1. **The cause of the divergence and the specific R6 calculation are both
   unrecorded and unresolved**, and this remediation does not claim to have
   recovered either. A reproduced value is consistent with a formula; it is not
   proof that the formula was used, and it is not the historical cause.
   *(Corrected 2026-09-22 under C-P5.0-LAB-I3-R8-R2; as returned this item
   left the cause treated as accounted for.)*
2. **Neither aggregate is a target-side statement under a common formula.** The
   common-formula work is workspace-only. R8's target-side equality claim stands
   under R8's own formula and at its own 50-file scope.
3. The **50-file scope limit** from the closed PR-20260920-LAB-I3-R7-R1-2 is
   unchanged: no whole-tree byte-for-byte claim is made or implied.
4. Neither aggregate is approval. A digest is review input, never an I3
   confirmation and never authority for `--execute`.

## 10. Proposed independent reviewer focus

1. Whether §3.3 as corrected still **withdraws** the unproven cause rather than
   restating it in softer words — specifically that "the records document
   different calculations" is not read as "the operators used different
   formulas".
2. Whether the common-formula calculation is specified tightly enough to be
   re-run independently, and whether the enumeration is the right breadth to
   make the single `4d829dc6…` match meaningful.
3. *Answered by Codex's re-review and corrected under C-P5.0-LAB-I3-R8-R2: the
   cause itself must also remain unresolved, and now does.* Whether the
   corrected text holds that line without drifting back toward treating a
   reproduced value as the historical cause.
4. Whether any document still implies the two aggregates are comparable, or
   silently prefers one.
5. That no R8 operational evidence was weakened, strengthened or re-scoped, and
   that the historical R6 record is unrewritten.

## 11. Disposition

**C-P5.0-LAB-I3-R8-R1 is consumed by this handback.** The authority ends here
and reached nothing outside the repository.

**LAB-I3-R8-AGGREGATE-1 remains Open, Important**, for independent Codex
re-review; the operator closes nothing. PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 remain **Open, Blocking**. I3 remains **performed but
unconfirmed and not closed**, and its closure remains Peter Duscha's decision.
V7 remains excluded and absent; V8 and V10 remain unperformed;
`plan.is_executable=False`; Package 5.0 remains **not ready**; LAB-SECRETS-1
remains Open, Low; LAB-V6-P2 remains deferred.

**No action on `oracle-test` is authorized.**
**Next step: independent Codex technical, security and evidence re-review.**
