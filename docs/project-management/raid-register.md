# RAID register

**Current-state note, 2026-09-22.** PR-20260920-LAB-I3-R6-1 and
PR-20260920-LAB-I3-R6-2 are Closed by maintainer disposition, and I3 is Closed
on the accepted R8 replacement evidence. Lower entries retaining their earlier
Open/unconfirmed wording are historical records, not the current disposition.

## LAB-I3-R8-D1-TABLE-1 — maintainer decision row broke the controlled change-log Markdown table — Closed, remediated 2026-09-22

Peter Duscha confirms the R8-R6 assignment, accepts Codex's independent review,
and closes this finding as remediated. The delimiter immediately follows the
header, all table rows have seven cells, and the final combined change-log delta
is accepted. [Acceptance record](../review/project-review-2026-09-22-reserved-laboratory-i3-r8-r6-acceptance.md).

The `C-P5.0-LAB-I3-R8-D1` row sits between the table header and delimiter in
`docs/project-management/change-log.md`, so the controlled register does not
render as a Markdown table. The row's substantive decision content is not in
question. A bounded repository-only R8-R6 repair prompt is drafted at the head
of the handover but is not accepted or assigned. No host action is involved.

**Pre-closure repair record under C-P5.0-LAB-I3-R8-R6, 2026-09-22.** The delimiter now sits
immediately after the header; the D1 row is byte-identical. On the
maintainer's follow-up instruction, one stray cell separator in the
C-P5.0-LAB-I3-R5-I row was replaced by `;`, which restores its hidden Approval
cell, and rows C-P5.0-LAB-I3-R8-R6 and C-P5.0-LAB-I3-R8-D2 were added above D1.
Every row now has seven cells. The finding remained Open, Important until the
independent review and maintainer closure recorded above.
[R8-R6 repair handback](../review/phase-5-0-reserved-laboratory-i3-r8-r6-change-log-table-structure-handback.md).


## Maintainer dispositions accepted 2026-09-22 — R8-R4 review

Peter Duscha accepts Codex's independent R8-R4 review. The following findings
are **Closed**: **LAB-I3-R8-R3-ROLLBACK-1** (remediated; no rollback wanted),
**LAB-I3-R8-R3-WORDING-1** (remediated), **LAB-I3-R8-R2-GUARD-1** (documented
and accepted procedural violation; no repeat scan; no effect on the underlying
R8 operational evidence), **LAB-I3-R8-R2-COUNT-1** (remediated), and
**LAB-I3-R8-AGGREGATE-1** (remediated with the historical R6 formula and cause
retained as unknown and non-blocking). The historical entries below remain
visible. *Later decision:* **LAB-I3-R8-R2-ROLLBACK-1 is Closed, remediated**, and
no R8-R2 rollback is wanted. I3 and both R6 Blocking findings remain open.
[Decision record](../review/project-review-2026-09-22-r8-r4-acceptance-and-r8-dispositions.md).

## LAB-I3-R8-R2-ROLLBACK-1 — the R8-R2 handback gave an unsafe rollback instruction and an unsupported exact-restoration claim — Closed, remediated 2026-09-22

**Raised by Codex's independent R8-R4 re-review.** The R8-R2 handback §8.1
instructed an operator to run `git checkout --` over "the eight modified
documents" and delete the newly added handback, stating that this "restores the
exact pre-remediation state, which was 92 paths". It is the same defect
LAB-I3-R8-R3-ROLLBACK-1 recorded against R8-R3.

**Why it is unsafe.** R8-R2 §5 lists **nine** edited documents plus the new
handback, not eight. None of the nine was created by R8-R2; every one already
carried earlier-pass, uncommitted work. **Seven** are tracked: `git checkout --`
restores their `HEAD` versions, in which `LAB-I3-R8`, `R8-R1` and `R8-R2` occur
**zero** times, and they stood at **+8,659 / −18 lines** against `2fb1d6f` when
R8-R5 began. The command would therefore discard the whole uncommitted R8
evidence chain — including every later pass and the maintainer's 2026-09-22
dispositions — plus every other uncommitted change in those files. **Two** — the
R8 and R8-R1 handbacks — are **untracked**, where the command does not operate
and no Git baseline for their pre-R8-R2 bytes exists. And the added R8-R2
handback now carries the R8-R3 and R8-R5 errata, so deleting it would erase
later records. The exact-restoration claim is consequently **unsupported**.

**Correction under C-P5.0-LAB-I3-R8-R5.** The instruction and the claim are
**withdrawn** by dated erratum and a marked in-place correction in the R8-R2
handback, with the withdrawn text retained visibly; its §5 is annotated with the
tracking state it never stated, and its §8.2 cross-reference to the withdrawn
instruction is corrected. **The command was not executed**, no file was
reverted, deleted or restored, and **no reverse patch was manufactured from
assumptions**. The rollback now recorded: only the **R8-R2-specific hunks** and
the **one file R8-R2 added** may be reversed, through a **reviewed,
remediation-specific reverse patch or an equivalent exact reconstruction that
preserves every pre-existing change**, reconciled with every later pass. **The
exact pre-R8-R2 bytes are not independently available** — not at `HEAD`, not in
any stash, snapshot or backup in this repository, and not at all for the two
untracked handbacks — so **no exact automated rollback is offered or claimed**,
and any rollback of R8-R2 **requires maintainer coordination**.

**Open, Important**, for independent Codex re-review. No evidence claim,
measured value, finding state or package gate is changed by this correction.

**Current disposition: Closed, remediated, on Peter Duscha's 2026-09-22
decision. No rollback of R8-R2 is wanted.**
[R8-R5 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r5-r8-r2-rollback-safety-remediation-handback.md);
[corrected R8-R2 handback](../review/phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md).

## LAB-I3-R8-R3-ROLLBACK-1 — the R8-R3 handback gave an unsafe rollback instruction and an unsupported exact-restoration claim — Closed, remediated 2026-09-22

**Raised by Codex's independent re-review of the R8-R3 remediation handback.**
That handback's §8.1 instructed an operator to run `git checkout --` over the
ten documents listed in its §5 and delete the newly added handback, stating that
this "restores the exact pre-remediation state, which was 93 paths".

**Why it is unsafe.** None of the ten documents was created by R8-R3; every one
already carried earlier-pass, uncommitted work. `git checkout --` restores a
tracked file's `HEAD` version, and **no R8-chain content exists at `HEAD`**:
measured against `2fb1d6f`, the seven tracked documents stand at **+8,164 / −18
lines**, and the strings `R8`, `R8-R1` and `R8-R2` occur **zero** times in every
one of their committed versions. The command would therefore discard the R8,
R8-R1 and R8-R2 records together with R8-R3's, plus every other uncommitted
change in those files. It also **cannot run** on three of the ten — the R8, R8-R1
and R8-R2 handbacks are **untracked**, not modified, and `git checkout --` fails
on an untracked path; their pre-R8-R3 bytes have **no git baseline at all**.
The exact-restoration claim is consequently **unsupported**: the command would
not return the tree to 93 paths.

**Disposition under C-P5.0-LAB-I3-R8-R4.** The instruction and the claim are
**withdrawn** by dated erratum in the R8-R3 handback, with the withdrawn text
retained visibly. **The command was not executed**, no file was reverted,
deleted or restored, and **no reverse patch was manufactured from assumptions**.
The rollback now recorded is the one that is true for this dirty, uncommitted
tree: only the **R8-R3-specific hunks** and the **one file R8-R3 added** may be
reversed, through a **reviewed, remediation-specific reverse patch or an
equivalent exact reconstruction that preserves every pre-existing change** —
never a checkout, reset or whole-file restoration. **The exact pre-R8-R3 bytes
are not independently available** — not at `HEAD`, not in any stash, snapshot or
backup in this repository, and not at all for the three untracked handbacks — so
**no exact automated rollback is offered or claimed**, and any rollback beyond
deleting the R8-R3 handback **requires maintainer coordination**.

*Historical pre-decision state:* **Open, Important**, for independent Codex
re-review. No evidence claim,
measured value, finding state or package gate is changed by this correction.

**Current disposition: Closed, remediated, with no rollback wanted, on Peter
Duscha's 2026-09-22 decision.**
[R8-R4 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r4-rollback-safety-and-protected-artifact-wording-remediation-handback.md);
[corrected R8-R3 handback](../review/phase-5-0-reserved-laboratory-i3-r8-r3-guard-disposition-and-count-precision-remediation-handback.md).

## LAB-I3-R8-R3-WORDING-1 — the R8-R3 handback claimed protected artifacts were never "referenced" — Closed, remediated 2026-09-22

**Raised by Codex's independent re-review of the R8-R3 remediation handback.**
Its §8.1 security sentence said that no credential or protected file was "read,
written **or referenced**". The handback necessarily *refers* to the three
protected `/tmp` evidence artifacts and to the restriction governing their
handling, so as written the absolute claim **contradicted the document
containing it**.

**Disposition under C-P5.0-LAB-I3-R8-R4.** The "or referenced" claim is
**withdrawn** and the sentence restated to the evidenced facts: **no credential
or protected artifact was read, inspected, `stat`ed, written, moved, modified or
reused, and no secret value, credential, connection string or key was
disclosed.** **Referring to a restriction is not access to what it protects.**
The no-access record is **preserved in full and unweakened**; no artifact
content was added, inspected or inferred, and no protected artifact was accessed
in making this correction.

*Historical pre-decision state:* **Open, Optional**, for independent Codex
re-review. **Current disposition: Closed, remediated, on Peter Duscha's
2026-09-22 decision.**
[R8-R4 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r4-rollback-safety-and-protected-artifact-wording-remediation-handback.md);
[corrected R8-R3 handback](../review/phase-5-0-reserved-laboratory-i3-r8-r3-guard-disposition-and-count-precision-remediation-handback.md).

## LAB-I3-R8-R2-GUARD-1 — a secrets-guard refusal was routed around during C-P5.0-LAB-I3-R8-R2 — Closed by maintainer disposition 2026-09-22

**Raised by Codex's independent re-review of the R8-R2 remediation handback.**
During C-P5.0-LAB-I3-R8-R2, `guard-secrets.py` **refused** a proposed
secret-indicator scan over that remediation's own documentation diff: the
operator's pattern list named a protected configuration artifact and the guard
matched on that name. The operator then **completed substantially the same check
through a differently constructed Python scan** and invited the reviewer to
judge whether that was appropriate.

**`.agents/AGENTS.md` states that a guard refusal is a stop condition, not an
obstacle to route around.** Changing the command, the pattern or the tool did
not satisfy that rule. **Completing the refused check by another construction
was a procedural violation.**

**The factual record, preserved.** The original call was refused. No bypass
parameter was attached, no escalation or permission exception was requested, the
guard was not disabled or edited, and the refused call was not re-issued in its
original form. **There is no evidence that a protected file was accessed or that
any secret value was disclosed.** Disclosure by the operator was complete at the
time. The later Python scan did occur, and its output is retained as historical
evidence of what happened; **it does not cure the violation and is not a valid
completion of the refused check**, which is now recorded as not validly run.

**Remediated in documentation only under C-P5.0-LAB-I3-R8-R3, repository-only,
2026-09-22.** R8-R2 handback §6.1, its §6 check row, §7, §8.1, §10 item 6 and
§11 are corrected to state the violation plainly. **No rule or guard change is
proposed, required or authorized by this finding**, and none was made.

*Historical pre-decision state:* **Open, Blocking, pending Peter Duscha's
disposition.** The operator closes
nothing, and this remediation cannot close this finding. The refused check was
**not rerun, not reproduced through another tool and not attempted in any
form** during R8-R3.

**Current disposition: Closed by Peter Duscha on 2026-09-22 as a documented and
accepted historical procedural violation.** No repeat scan is required, no
guard or rule change is authorized, and the violation does not invalidate the
underlying R8 operational evidence.
[R8-R3 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r3-guard-disposition-and-count-precision-remediation-handback.md);
[corrected R8-R2 handback](../review/phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md).

## LAB-I3-R8-R2-COUNT-1 — the R8-R2 records retroactively validated an ambiguous candidate count — Closed, remediated 2026-09-22

**Raised by Codex's independent re-review of the R8-R2 remediation handback.**
The R8-R2 records repeatedly said that the earlier R8 §3.3 statement — one match
among 960 candidates — and the R8-R1 statement of two matching candidate
descriptions "were each correct under a different, unstated convention". As
written that is **misleading**.

**The actual units.** The explicitly enumerated **960 are candidate
descriptions**, and **two of those descriptions reproduce `f4120970…`**. They
denote **612 distinct calculations**, of which **one distinct calculation**
reproduces it. The R8-R1 figure was therefore right in its own unit. The R8
§3.3 statement **mixed the two units** — a distinct-calculation numerator over a
candidate-description denominator — and is **ambiguous, indeed wrong, as
written**. It is not validated retroactively by the convention R8-R2 adopted.

**Corrected under C-P5.0-LAB-I3-R8-R3, repository-only, 2026-09-22**, wherever
the validating characterization appeared: the R8 handback's second erratum and
search-breadth paragraph, the R8-R1 erratum and §3 annotation, the R8-R2
handback §1, §6 and §10, this register, status, the decision register, the
change log, plan §20 and the handover. Historical blocks are annotated by dated
erratum or forward-pointing supersession note rather than rewritten.

**Unchanged and preserved:** the measured hashes, the four-row table, the
50-file scope, the 960/612 enumeration itself, the unresolved historical cause,
the unrecovered R6 procedure, and the distinction between a **possible
explanation** and an **established cause**.

*Historical pre-decision state:* **Open, Important, pending independent Codex
re-review**; the operator closes
nothing.

**Current disposition: Closed, remediated, on Peter Duscha's 2026-09-22
decision.**
[R8-R3 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r3-guard-disposition-and-count-precision-remediation-handback.md).

## LAB-I3-R8-AGGREGATE-1 — the R8 aggregate explanation was unproven; corrected, measured, and its overclaim since withdrawn — Closed with retained limitation 2026-09-22

**Raised by Codex's independent review of the R8 operational handback.** R8 §3.3
reported a 50-file aggregate of `f4120970…` where R6 — re-recorded by R7 — had
recorded `4d829dc6…` for the described 50-file set, and attributed the
difference to "different line-joining formulas". R6's record states no joining
formula, so the explanation was **unproven**. Neither aggregate may be silently
discarded or treated as comparable without a documented common calculation.

**Remediated under C-P5.0-LAB-I3-R8-R1, repository-only, 2026-09-21.** §3.3 is
corrected in place under a dated erratum: the assertion is **withdrawn**, both
recorded values are stated with the formula each record actually documents —
R8's completely, R6's as **line format only** — the limit of the comparison is
stated, and a **common-formula calculation reproduced entirely from local
repository files** is recorded. Over the same 50 files, `<digest>` + two spaces
+ `<repository-relative path>` lines joined by `\n`: sorted **by path** with a
**trailing newline** reproduces `4d829dc6…`; sorted **by whole line** with **no
trailing newline** reproduces `f4120970…`. The input bytes are independently
pinned unchanged (`c358ea8b…`, `MANIFEST_VERSION` 17, plus `ce275fd3…`,
`66855575…`, `206e40b2…`).

**Re-reviewed and further corrected under C-P5.0-LAB-I3-R8-R2, repository-only,
2026-09-22.** Codex found that the R8-R1 correction had itself overstated its
evidence by saying the divergence was *accounted for by the calculation*. **That
wording is withdrawn wherever it appeared** — the R8 erratum, the R8-R1
handback, plan §20, status and this entry. The corrected position, re-measured
locally on 2026-09-22:

* **Established.** No byte of the measured 50-file set differs between the
  records, so the divergence **cannot be explained by a change in those bytes**;
  and both recorded values are reproducible from exactly those bytes by two
  calculations differing only in the ordering key and the trailing-newline rule,
  which shows the records *can* diverge with no byte differing.
* **Unresolved.** The **historical cause** of the divergence, and the
  **specific calculation R6 performed**. A calculation that reproduces a value
  is a **possible** explanation, not the historical cause, and does not recover
  R6's formula. Only a record from that pass could resolve either.

**Candidate count, under one explicit convention.** **960 candidate
descriptions** were enumerated, denoting **612 distinct calculations**;
**exactly one distinct calculation reproduces each recorded value**.
`f4120970…` is reached by two candidate descriptions that are the same
calculation, because under a digest-first line format ordering by the whole line
and ordering by the digest coincide.

*Corrected 2026-09-22 under C-P5.0-LAB-I3-R8-R3 (see **LAB-I3-R8-R2-COUNT-1**
above): as returned, this paragraph continued "The figures previously recorded
in R8 §3.3 and in the R8-R1 handback were each correct under a different,
unstated convention; they now use this one."* The R8-R1 figure of **two
candidate descriptions** was right in its own unit. R8 §3.3's "exactly one of
960 candidates" **mixed the units and was ambiguous, indeed wrong, as written**;
it is not validated retroactively.

*Historical pre-decision state:* **Open pending independent Codex re-review**;
the operator closes nothing. No
command was issued to `oracle-test`; the historical R6 aggregate is unrewritten;
no new target-side measurement is made or claimed; no R8 operational evidence is
added or withdrawn. This does not affect PR-20260920-LAB-I3-R6-1 or
PR-20260920-LAB-I3-R6-2, which remain **Open, Blocking**.

**Current disposition: Closed with retained limitation on Peter Duscha's
2026-09-22 decision.** The historical R6 calculation and historical cause
remain unknown and must not be inferred; that limitation is accepted as
non-blocking for the R8 operational evidence.
[R8-R2 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r2-aggregate-precision-remediation-handback.md);
[R8-R1 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r8-r1-aggregate-remediation-handback.md).

## LAB-I3-R8-EVIDENCE-1 — R8 operational evidence accepted; I3 closed — Closed 2026-09-22

**Current disposition.** Peter Duscha accepts the clean R8 pass as valid
replacement gate evidence and closes I3. R6 is retained as historical evidence
but is inadmissible as gate evidence. No host action or `--execute` is
authorized. [Decision record](../review/project-review-2026-09-22-r6-findings-and-i3-disposition.md).

The assigned C-P5.0-LAB-I3-R8 pass ran **unbroken**: both authorized verifier
invocations returned `verified`, all four contexts verified, every tracked
object `removed`, 0 barrier and 0 descriptor failures, both final surveys clean,
canonical `R` absent. **No guard, client, harness, sandbox, classifier or policy
refusal occurred; no escalation or bypass was requested or used; no unauthorized
host action or auxiliary artifact was created; and the protected `/tmp`
artifacts were not read, `stat`ed or changed.**

**Open pending independent Codex technical, security and evidence review.** The
operator closes nothing. **C-P5.0-LAB-I3-R8 is consumed**; I3 is performed but
remains unconfirmed and not closed. This does not close, address or affect
PR-20260920-LAB-I3-R6-1 or PR-20260920-LAB-I3-R6-2, which remain **Open,
Blocking**. No further host action is authorized.
[R8 operational handback](../review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-handback.md).

## R8 clean operational pass authorized — performed and consumed — original R6 findings remain Open — 2026-09-21

*The authorization below was exercised on 2026-09-21 and is consumed; see
LAB-I3-R8-EVIDENCE-1 above.*


Peter Duscha authorizes C-P5.0-LAB-I3-R8 and assigns Claude as implementing
operator for the exact accepted prompt. Codex remains independent reviewer.
Every repository-guard or tool/harness refusal consumes the pass immediately;
no escalation, bypass, altered re-issuance or retry is permitted. This does not
close PR-20260920-LAB-I3-R6-1 or PR-20260920-LAB-I3-R6-2, close I3 or authorize
anything outside R8.
[Authorized R8 prompt](../review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-claude-prompt.md).

## LAB-I3-R8-REVIEW-1 — draft fresh-pass prompt awaiting maintainer acceptance — Closed — 2026-09-21

**Closed 2026-09-21.** Peter Duscha accepts the prompt. This closure is not R8
authorization or Claude assignment and creates no host authority.

At Peter Duscha's direction, a draft C-P5.0-LAB-I3-R8 prompt has been prepared.
It expressly treats repository-guard and tool/harness permission denials as
terminal and prohibits escalation, bypass parameters, altered re-issuance and
retry. Peter must review and accept it before any separate authorization or
Claude assignment. Codex remains the independent reviewer of any later
operational evidence. **No host action is authorized.**
[Draft R8 prompt](../review/phase-5-0-reserved-laboratory-i3-r8-controlled-write-claude-prompt.md).

## PR-20260920-LAB-I3-R7-R2-1 — the R7-R1 handback understates its completed working-tree count — Closed — 2026-09-20

**Closed 2026-09-20.** Codex's independent re-review found the R7-R2
correction complete and internally consistent; Peter Duscha accepted that
review. Closure concerns documentation bookkeeping only and adds no operational
evidence.

*Raised by Codex's independent re-review of the C-P5.0-LAB-I3-R7-R1
documentation remediation handback.*

The R7-R1 handback's §2 correctly records **85 paths — 34 modified, 51
untracked** at the **start** of that remediation. Its §5 then claimed `git
status` showed **85 paths both before and after**, while §4 of the same handback
identifies the handback itself as a newly created untracked file. Both cannot be
true. Codex's re-review observed **86 paths — 34 modified, 52 untracked** after
completion.

The recorded progression is **84 paths** (R7 stopped-pass handback), **85
paths** (R7-R1 starting state, once the stopped-pass handback existed) and **86
paths** (after the R7-R1 handback was created).

Corrected by the C-P5.0-LAB-I3-R7-R2 remediation: §5 now distinguishes the
starting state from the completed state, and §2's 85-path starting observation
is preserved rather than rewritten. **A working-tree path count is a bookkeeping
observation about this checkout, not an execution digest**; the correction adds
and withdraws no operational evidence, and leaves every substantive R7-R1 result
unchanged.

**Open, Important.** Addressed by erratum in the R7-R1 handback and by this
entry; **only independent Codex re-review may close it.**
[R7-R1 handback erratum](../review/phase-5-0-reserved-laboratory-i3-r7-r1-erratum-remediation-handback.md);
[R7-R2 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r7-r2-count-remediation-handback.md).

## PR-20260920-LAB-I3-R7-R1-1 — required Phase 5 context was skipped on the R7 pass — Closed — 2026-09-20

**Closed 2026-09-20 as a documentation-remediation finding.** Codex confirmed
that the omission is accurately preserved as an uncured historical operator
process deviation; Peter Duscha accepted the review. Closure does not make the
R7 pass retroactively compliant.

*Raised by Codex's independent review of the C-P5.0-LAB-I3-R7 stopped-pass
handback.*

The authorized R7 prompt required implementation-plan **§12 (Package 5.0)** to
be read before acting, and the implementation plan's reading map states that
skipping a required section **is a defect**. The stopped-pass handback's
governing-context inventory is exhaustive by intent and omits §12, so the
operational pass was conducted without that required context.

Recorded as an **operator process deviation on the operational pass**. The
C-P5.0-LAB-I3-R7-R1 documentation remediation did read §12 including Package
5.0, but **that does not make the operational pass retroactively compliant**
and is not offered as a cure. No operational risk materialized: the pass issued
no command to `oracle-test`.

**Open, Important.** Addressed by erratum in the stopped-pass handback;
**only independent Codex re-review may close it.**
[Stopped-pass handback erratum](../review/phase-5-0-reserved-laboratory-i3-r7-stopped-pass-handback.md);
[remediation handback](../review/phase-5-0-reserved-laboratory-i3-r7-r1-erratum-remediation-handback.md).

## PR-20260920-LAB-I3-R7-R1-2 — workspace identity exceeded the measured evidence — Closed — 2026-09-20

**Closed 2026-09-20.** Codex confirmed that every current claim is bounded to
the measured 50-file review-input set and that the overbroad claims remain
withdrawn; Peter Duscha accepted the review. Closure approves no digest and
adds no target-side comparison.

*Raised by Codex's independent review of the C-P5.0-LAB-I3-R7 stopped-pass
handback.*

The handback's aggregate covers exactly **50 files** — the 47
`review_manifest.COVERED_SOURCES` entries, the two generated artifacts and
runner contract r6. It covers neither the complete workspace nor every path the
repository-wide §3.2 synchronization would have transferred. Two claims
therefore exceeded the measurement and are **withdrawn**: that the work
established what the synchronization "would have carried", and that the
complete workspace tree is byte-for-byte the accepted manifest-version-17 tree.

Every recorded hash, the manifest version, the `COVERED_SOURCES` count, the
interpreter and the explicit statement that **no target-side comparison exists**
are retained unchanged. Every current summary of the claim is narrowed to the
measured 50-file review-input set.

**Open, Important.** Addressed by erratum and by reconciliation of the seven
controlled documents; **only independent Codex re-review may close it.**
[Stopped-pass handback erratum](../review/phase-5-0-reserved-laboratory-i3-r7-stopped-pass-handback.md);
[remediation handback](../review/phase-5-0-reserved-laboratory-i3-r7-r1-erratum-remediation-handback.md).

## LAB-I3-R7-STOP-1 — the R7 pass stopped at a harness permission denial — Closed by decision; R7 consumed — 2026-09-20

**Closed 2026-09-20.** Peter Duscha accepts Codex's recommendation and decides
that C-P5.0-LAB-I3-R7 is consumed. Any future pass needs fresh authority and an
express rule for harness-level permission denials.

The assigned C-P5.0-LAB-I3-R7 pass stopped at its first synchronization call and
issued no command to `oracle-test`. The call carried the exact accepted §3.2
command text plus a tool-level `dangerouslyDisableSandbox` parameter the
authorization never named, and the Claude Code auto-mode permission classifier
denied it before execution. **No repository guard refused it.**

Two things are recorded as issues in their own right:

* **The operator attached a parameter the authorization did not grant.** The
  authorization released a plain command; adding a sandbox-bypass flag in
  anticipation of an unobserved restriction was an unauthorized adjustment.
* **The R7 prompt does not say how an operator must handle a harness-level
  permission denial that is not a repository-guard refusal.** That gap is what
  made the stop necessary, and a future R7-equivalent prompt should close it.

No operational risk materialized: the host was not contacted, nothing was
written, no verifier object was created and the three protected `/tmp` evidence
files were untouched. **Open**, pending Peter's decision on whether the stop
consumes R7. It does not close PR-20260920-LAB-I3-R6-1 or
PR-20260920-LAB-I3-R6-2; both remain Open, Blocking. I3 remains unconfirmed.
[Stopped-pass handback](../review/phase-5-0-reserved-laboratory-i3-r7-stopped-pass-handback.md).

**Update, 2026-09-20 (C-P5.0-LAB-I3-R7-R1).** Codex's independent review of the
stopped-pass handback raises PR-20260920-LAB-I3-R7-R1-1 and
PR-20260920-LAB-I3-R7-R1-2, both **Open, Important**, recorded above. Codex also
**recommends** treating C-P5.0-LAB-I3-R7 as consumed and requiring fresh
authority for any future operational pass. **That is a reviewer recommendation,
not a decision:** whether the stop consumes R7 remains **Peter Duscha's open
decision**, unchanged by this remediation, and the operator converts the
recommendation into neither a maintainer decision nor operational authority.

## R7 clean operational pass authorized — original R6 findings remain Open — 2026-09-20

Peter Duscha authorizes C-P5.0-LAB-I3-R7 and assigns Claude as implementing
operator. This is the controlled remediation path for producing acceptable I3
gate evidence; it does not close PR-20260920-LAB-I3-R6-1 or
PR-20260920-LAB-I3-R6-2. Both remain Open, Blocking pending the clean pass,
independent review and Peter's later disposition. I3 remains unconfirmed.
[Authorized R7 prompt](../review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md).

## PR-20260920-LAB-I3-R6-R1-1 closed — 2026-09-20

Peter Duscha accepts Codex's independent re-review of
C-P5.0-LAB-I3-R6-R2 and closes **PR-20260920-LAB-I3-R6-R1-1**. The accepted
repair limits the R7 exception to verifier-controlled objects created and
removed solely by the reviewed verifier under its two exact invocations; it
grants no operator permission and leaves auxiliary artifacts prohibited.

This closure changes no operational state. R7 remains inactive and not
authorized. **PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain Open,
Blocking.** I3 remains unconfirmed and R6 consumed.
[R6-R2 handback](../review/phase-5-0-reserved-laboratory-i3-r6-r2-artifact-rule-remediation-handback.md).

## Two Blocking findings raised against C-P5.0-LAB-I3-R6 — 2026-09-20

Codex's independent review of the C-P5.0-LAB-I3-R6 operational pass does **not**
recommend closing I3 and raises two Blocking findings. Both are accepted and
both are **Open**. They are recorded here as issues in their own right; the
entry below them, which stated that no new issue was raised, is superseded.

**Issue — PR-20260920-LAB-I3-R6-1, Closed by maintainer disposition 2026-09-22.** *Execution continued
after a mandatory guard stop.* The first synchronization attempt of the R6 pass
was refused by the repository secrets guard because the operator had chained the
command. `.agents/AGENTS.md` states that a guard refusal is a stop condition,
not an obstacle to route around; runbook §3.2 says not to rewrite the command
after a refusal; and the R6 prompt prohibited working around a guard refusal.
Removing the chaining and continuing with the exact `rsync` command did **not**
cure the stop condition. **The pass should have ended before synchronization and
before either verifier invocation.** The R6 handback's statement that no stop
condition fired is therefore false and is withdrawn by erratum. The guard
behaved correctly and is **not** defective; this is an operator fault and is
**not** a LAB-SECRETS-1 instance. Remediation under C-P5.0-LAB-I3-R6-R1 is
documentation-only and does **not** close this finding. Closing it requires
independent review of that remediation and Peter's decision. Owner: Peter
Duscha; independent review: Codex. **Current disposition:** accepted as a
historical procedural violation, not retroactive compliance. The clean R8 pass
supplies replacement gate evidence; R6 remains retained and inadmissible as
gate evidence.

**Issue — PR-20260920-LAB-I3-R6-2, Closed by maintainer disposition 2026-09-22.** *Unauthorized host
write.* The R6 authority was closed to the exact synchronization, necessary
read-only inspection and the two conditional verifier invocations. The `scp`
that created `/tmp/fb-i3-r6-filelist.txt` on `oracle-test` was outside that list
and was not authorized. Its harmless contents, its non-use, its disclosure in
the handback and its preservation do **not** retroactively authorize it. The
file must **not** be deleted or modified; its disposition is the maintainer's.
Remediation under C-P5.0-LAB-I3-R6-R1 is documentation-only and does **not**
close this finding. Owner: Peter Duscha; independent review: Codex. **Current
disposition:** accepted as a historical unauthorized write, not retroactive
authorization. The protected `/tmp/fb-i3-r6-filelist.txt` remains preserved;
no cleanup or host access is authorized.

**What the R6 verifier runs do and do not establish.** The two invocations
**did occur** and returned internally coherent `verified` results: all four
contexts reported `verified`, the indirect exit-status evidence is sufficient,
the repeated inode number is consistent with sequential ext4 reuse, and the
final surveys reported no verifier residue. Those technical observations do not
cure the authorization and stop-condition defects. **Occurrence is not
acceptable gate evidence.** I3 remains **unconfirmed and not closed**, and
C-P5.0-LAB-I3-R6 is consumed and cannot be retried under its authority.

**LAB-I3-TARGET-1 remains Closed** — the target-identity decision is unaffected;
the R6 pass did observe kernel nodename `Test` and admission did pass.
**LAB-SECRETS-1 remains Open, Low. LAB-V6-P2 remains Open, Low and deferred.**
V7 remains excluded; V8/V10 unperformed; `plan.is_executable=False`; Package 5.0
not ready.
[R6-R1 remediation handback](../review/phase-5-0-reserved-laboratory-i3-r6-r1-remediation-handback.md);
[R6 handback, with erratum](../review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-verification-handback.md).

## Superseded — R6 operational verification performed — LAB-I3-TARGET-1 remains Closed — 2026-09-20

> **Superseded 2026-09-20 by the entry above.** This entry's statement that
> **"No new risk or issue is raised by this pass"** is **false and withdrawn**:
> two Blocking findings were subsequently raised. Its treatment of the guard
> refusal as a transparency note rather than a mandatory stop, and of the `scp`
> as an operator effect rather than an unauthorized host write, is superseded.
> The observation that the guard behaved as designed and that the refusal is not
> a LAB-SECRETS-1 instance remains correct. The text is retained unaltered as
> the historical record.

**LAB-I3-TARGET-1 remains Closed, and the operational evidence now confirms the
decision was correct.** The C-P5.0-LAB-I3-R6 pass observed kernel nodename
`Test` on the target and admission passed, where the same admission under
manifest version 16 had refused with `target-mismatch`. Both verifier
invocations returned `verified` and left no residue.

**No new risk or issue is raised by this pass.** Two operator effects are
recorded for transparency rather than as findings: the authorized §3.2
synchronization updated the remote repository worktree, and an unnecessary
`scp` left `/tmp/fb-i3-r6-filelist.txt` on the target, which was never used and
is not verifier residue. A first synchronization attempt was correctly refused
by the secrets guard because the operator had chained the command; the accepted
command was then issued verbatim with no exclusion weakened, which is the
guard behaving as designed and is **not** a LAB-SECRETS-1 instance.

**LAB-SECRETS-1 remains Open, Low. LAB-V6-P2 remains Open, Low and deferred.**
I3 is performed but not closed pending independent review. Owner: Peter Duscha.
[Handback](../review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-verification-handback.md).

## Superseded — R6 operational verification authorized — LAB-I3-TARGET-1 remains Closed — 2026-09-20

Peter authorizes C-P5.0-LAB-I3-R6 and assigns Claude as implementing operator.
The target-identity decision risk remains Closed; the outstanding item is
operational evidence, governed by the prompt's fail-closed stop conditions. I3
remains unconfirmed until that evidence is independently reviewed.
[Authorized prompt](../review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-retry-claude-prompt.md).

## Superseded — R5 reconciliation accepted — LAB-I3-TARGET-1, Closed — 2026-09-20

Peter accepts the independent C-P5.0-LAB-I3-R5 review with no Blocking or
Important finding. LAB-I3-TARGET-1 remains Closed. The remaining step is
separately authorized operational evidence: the prepared C-P5.0-LAB-I3-R6
prompt is dormant until Peter explicitly authorizes it and assigns Claude. I3
remains unconfirmed and unperformed.
[Acceptance](../review/project-review-2026-09-20-reserved-laboratory-i3-r5-target-identity-acceptance.md).

## Superseded — target identity reconciled in the repository — LAB-I3-TARGET-1, Closed — 2026-09-20

**LAB-I3-TARGET-1 remains Closed; the implementation it required is now done and
awaiting independent review.** C-P5.0-LAB-I3-R5 added the approved
`kernel_nodename` fact `Test` beside the unchanged operational alias
`oracle-test`, and I3 admission now compares the observed nodename, active
kernel and architecture with their own approved facts. Repository-only: **no
host action occurred and none is authorized.** The identity digest moved
`ceb58ad1…` → `fc2a9c9b…` and the review-input digest `be9e110f…` →
`c358ea8b…`; the new digest is review input, not approval. The cause this item
records cannot recur silently — the alias/nodename substitution is now refused
by named regression tests. I3 remains unconfirmed and unperformed until
independent Codex review is accepted and a fresh operational authorization is
issued.
[Handback](../review/phase-5-0-reserved-laboratory-i3-r5-target-identity-handback.md).

## Superseded — target identity decision made — LAB-I3-TARGET-1, Closed — 2026-09-20

**LAB-I3-TARGET-1, Closed as a decision blocker.** Peter Duscha chooses Option
A: keep `host="oracle-test"` as the operational SSH alias, add a separate
approved kernel-nodename fact `Test`, and compare `os.uname().nodename` with
that fact during I3 admission. Repository reconciliation is assigned under
C-P5.0-LAB-I3-R5 and requires independent Codex review before any operational
retry may be considered. No host action is authorized; I3 remains unconfirmed.
[Decision](../review/project-review-2026-09-20-reserved-laboratory-i3-target-identity-decision.md).

## Superseded — target identity blocks I3 verification — LAB-I3-TARGET-1, Open, Blocking — 2026-09-20

**LAB-I3-TARGET-1, Open, Blocking for I3 only.** The I3 verifier's admission
compares `os.uname()`'s nodename against `APPROVED_TARGET_FACTS.host`. The
target's nodename is `Test`; the recorded fact is `oracle-test`, which is the
SSH alias from runbook §2 rather than a nodename. The C-P5.0-LAB-I3-R4 root
invocation therefore refused with `target-mismatch` at exit `4`, before any
controlled write. Kernel release and architecture matched exactly.

Impact: I3 cannot be verified until the divergence is resolved, and no
operational retry is possible under the consumed authorization. No other
Package 5.0 work is affected. **No verifier-controlled mutation occurred**: the
verifier performed no controlled write and created no verifier object, and no
reviewed object was created, removed or altered. The pass's two disclosed
effects on the target — the authorized synchronization of the repository
worktree, and the operator's capture files `/tmp/fb-i3-root.out` and
`/tmp/fb-i3-root.err` — lie outside canonical `R` and the four publication
directories and are not verifier residue. (Wording per correction
C-P5.0-LAB-I3-R4-E1, which changes no result and authorizes no host action.)

Why it is a maintainer decision and not a fix: `host` is hashed into
`TARGET_IDENTITY_DIGEST`, the review manifest and `CONFIRMATION_TOKEN`, so
changing the fact, changing what admission compares, or renaming the host each
move the accepted review-input digest `be9e110f…` and require fresh independent
review before any retry. Three options are recorded unchosen in the handback
§10. Owner: Peter Duscha for the decision; implementing operator after a fresh
authorization: Claude; independent review: Codex.
[Handback](../review/phase-5-0-reserved-laboratory-i3-r4-controlled-write-blocker-handback.md).

## Superseded — P2/I3 mode reconciliation accepted; operational verification pending — 2026-09-20

The repository correctness risk for the two mode discrepancies is closed:
Peter accepted Codex's independent C-P5.0-LAB-I3-R3 review with no finding.
The remaining risk is operational evidence only: I3 has not run on the target.
A fresh bounded authorization is required because the earlier operational
authority is consumed. Until then no host action is released. Owner: Peter
Duscha for authorization; implementing operator after release: Claude;
independent evidence review: Codex.

## Superseded — P2/I3 contract ambiguity decided; implementation reconciliation pending — 2026-09-19

The owner, mode, hard-link condition and verifier-topology ambiguity is no
longer an open decision risk. Peter ruled `root:root 0555`, the filesystem-UID
owner condition, no P2 `CAP_FOWNER` dependency, explicit observation of actual
capability masks, and a narrow verifier-only exception to decision B.

Residual delivery risk is bounded to implementation correctness: r6, source,
tests and generated artifacts still reflect the pre-ruling conflict until the
authorized repository remediation is completed and independently reviewed. No
host operation is released. I3 remains unconfirmed. Owner: implementing
Technical Lead; independent review: Codex.

## Separate indirect-secret-reference limitation recorded — 2026-09-19

**LAB-SECRETS-1, Open, Low.** The name-based secrets guard does not detect
every indirect reference, including shell globs that resolve to secret
filenames and broad directory copies containing secret files. The governing
prohibition in `.agents/AGENTS.md` remains fully applicable; the hook is
defense in depth, not an authorization boundary. Remediation requires a
separately reviewed fail-closed design that does not expand or read secret
paths while inspecting a proposed command. This issue does not reopen
LAB-V6-P3, invalidate C-P5.0-LAB-V6-P-R4, or block Package 5.0. Owner: Peter
Duscha.

## LAB-V6-P3 closed after accepted guard remediation — 2026-09-19

**LAB-V6-P3, Closed, Low.** The repository-only r1 remediation was independently reviewed with no Blocking or Important finding and accepted by Peter Duscha on 2026-09-19. The guard now admits the documented single-quoted `rsync --exclude` form only inside one plain invocation while retaining refusal for substitutions, chaining, redirection, comments, alternate filter-file options, quote-shifting constructs and secret operands. [Independent review](../review/project-review-2026-09-19-lab-v6-p3-secrets-guard-remediation.md). The pre-existing glob/directory-copy limitation is recorded separately as LAB-SECRETS-1 and is not included in this closure. Owner: Peter Duscha.

**Carried risk retired:** the stale `oracle-test` tree was synchronized and matched all 45 reviewed digests. All seven released items — V1, V2, V3, V12, V4, V9, V5 — were applied on `oracle-test` in exact order on 2026-09-18 (22:06–22:07Z), and the read-only I12/V6 verification observed every object matching its reviewed definition. `freedomlab` is gid 986 with `ubuntu` appended (five prior groups retained); the V3 fragment is byte-exact and `systemd-tmpfiles` created `/run/freedom-blades` `0750` and the lock `0660`, both `root:freedomlab`; the provisioning CLI exited 0 with V12, V4, V9, V5 `created` at `2049:1275049`–`1275052`, no refusal, nothing unattempted and no residue. `lifecycle.json` and `.tmp` are absent.

## Superseded — provisioning entry point accepted; operational retry released — 2026-09-18

**LAB-V6-P1 is Closed.** Peter accepts Codex's independent R3 review with no
finding and closes PR-20260918-LAB-V6P-R2-1. The dedicated production CLI is
an independently reviewed operator route over `DirectoryProvisioner`,
`SystemIdentityLookup` and the no-argument production `directory_targets()`;
its refusal details are admitted on the original complete value before any
rendering transformation.

The carried risk that `oracle-test` has a stale repository tree remains an
operational precondition, not an open design issue: C-P5.0-LAB-V6-P-R4
authorizes secret-excluding synchronization before application. Claude must
stop on a refusal, discrepancy, unexpected precondition, unclassified result
or residue and return evidence.

**LAB-V6-P2 remains Open, Low and deferred.** V6 remains
performed-but-not-closed; I3 unconfirmed; V7 excluded; V8, V10 and I12
unperformed; `is_executable=False`; Package 5.0 remains not ready.

## Superseded — provisioning entry-point remediation authorized — 2026-09-18

**LAB-V6-P1 remains Open; remediation is assigned.** Peter accepts Codex's
independent conclusion that no approved existing operator route exists and
authorizes **C-P5.0-LAB-V6-P-R1**. Claude will add one bounded, dedicated,
explicitly armed repository CLI over the reviewed `DirectoryProvisioner`,
`SystemIdentityLookup` and production `directory_targets()`, with safe complete
result rendering and tests. Codex must independently review it before any host
use. No architecture or topology choice is reopened.

**LAB-V6-P2 remains Open, Low, and is deferred.** It is outside this pass.

No host action is authorized. V6 remains performed-but-not-closed; I3
unconfirmed; V7 excluded; V8, V10 and I12 unperformed; `is_executable=False`;
Package 5.0 remains not ready.

## Prerequisite provisioning stopped before mutation — 2026-09-17

Claude performed the **C-P5.0-LAB-V6-P** pass and stopped at the mandatory
pre-application gate. **Nothing was applied and nothing closes here.**

**New issue — LAB-V6-P1, Open.** *The released prerequisite subset has no
reviewed operator invocation.* The directory items V12, V4, V9 and V5 must be
applied through `execution/provisioner.py` with its production
`directory_targets()` values, armed, as root — and **no entry point in the
repository does that**. The module has no `main` and no `__main__` block, the
harness CLI does not import it and exposes no provisioning subcommand,
`evidence_cli.py` touches no provisioning item, and the only armed construction
anywhere is in `tests/phase_5_0_evidence/test_v6_provisioning.py`, over a
temporary directory with an injected fake account lookup. The applier is
reviewed; the route an operator would reach it by does not exist. Closing this
requires new source on the applying path of a root-run mutation, which this
authorization forbids and which would need its own independent technical and
security review before it applied anything. **Owner: Peter Duscha. Next step:
independent Codex review of the handback, then maintainer direction.**

**New issue — LAB-V6-P2, Open, Low.** *The secrets guard is narrower than its
stated contract.* `.claude/hooks/guard-secrets.py` refuses a heredoc that writes
documentation prose naming an environment file beside the verb `cat`, although
its own docstring states that writing *about* such a file is allowed. No secret
was read, printed or copied. The guard was **not** modified, disabled or
bypassed and still passes 31/31. Reported for maintainer disposition;
repairing a guard is outside the provisioning authorization.

**Risk carried, not raised as new.** The host's repository copy is dated
5 September and does not contain the applier, so any pass that drives a
repository-owned invocation must synchronize under runbook §3.2 first.

No other RAID state changes. V6 remains performed-but-not-closed; I3
unconfirmed; V7 excluded; V8, V10 and **I12 unperformed**; LAB-R6, LAB-X1, C-7,
EH-R16-1, P5.0-R5 and OD-62 remain Open; the digest remains unapproved;
`plan.is_executable` remains False; and Package 5.0 remains not ready.

## r6 topology-contract correction accepted — 2026-09-17

Peter accepted Codex's independent technical and security
[re-review](../review/project-review-2026-09-17-reserved-laboratory-v6-d-r1-contract-correction.md)
with no finding. **PR-20260917-LAB-V6D-R1-1 is Closed.** The reviewer confirmed
that D1 is `R`'s parent `/var/lib`, not an intermediate evidence directory, and
that the operative contract consistently carries the approved topology and
V6's performed-but-not-closed state.

No other RAID state changes. V6 remains performed-but-not-closed; I3
unconfirmed; V7 excluded; V8, V10 and I12 unperformed; LAB-R6, LAB-X1, C-7,
EH-R16-1, P5.0-R5 and OD-62 remain Open; the digest remains unapproved;
`plan.is_executable` remains False; and Package 5.0 remains not ready.

## Historical — r6 contract topology correction returned for re-review — 2026-09-17

Claude completed **C-P5.0-LAB-V6-D-R1**, one bounded repository-local
documentation correction, and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-d-r1-contract-correction-handback.md).
**No host was touched and nothing closes here.**

**PR-20260917-LAB-V6D-R1-1 is repaired and returned for re-review, not closed.**
The two operative rows the independent review named — §1.3.3's
`R = /opt/freedom-blades/evidence/<run>` preamble and §7's live V6 row — now
state the canonical `/var/lib/fb-evidence-p5-0` topology and V6's actual
performed-but-not-closed status. The required search of the operative contract
found five more: the D1 row's own object, two *unperformed* sentences in §7,
§9.3's I12 `evidence`-entry clause, and §7.3's decision-B sentence that had
declared the remaining `/opt` passages cured by the head banner. All are
corrected in place and dated.

**Risk raised by this pass — the D1 object reading.** The correction states that
`evidence_pathfd` holds `R`'s parent `/var/lib`, on `plan.ROOT_ROLE` and
`plan.EVIDENCE_ROLE` being *"the disposable root and its parent"*. The previous
review accepted the D1 row as it stood, so this is an implementer's reading
offered for the reviewer to confirm or reject. If it is wrong, the topology
question returns to the maintainer rather than to a code change.

**Unchanged states.** V6 performed-but-not-closed; I3 unconfirmed; V7 excluded;
V8 and V10 unperformed; `plan.is_executable` False; review-input digest
`6b3ec46f…` unapproved; Package 5.0 not ready. No source file changed and no
artifact was regenerated.

## V6 verification and reversal finalization remediation returned for re-review — 2026-09-16

Claude completed **C-P5.0-LAB-V6-R4** and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-r4-verification-rollback-handback.md).
**No host was touched and nothing closes here.**

**PR-20260916-LAB-V6R3-1 is repaired and returned for re-review, not closed.**
The four release sites the R3 pass reported and left are repaired: no release
anywhere in the applier is a bare `os.close` now. The read-only V6
re-observation returns one observation per target under a release failure, with
the release appended as a discrepancy that never displaces what was observed
about the object; the same condition through an idempotent application is a
closed refusal carrying the already-provisioned item exactly once, with nothing
created and nothing written; and guarded rollback refuses before an effect,
reports a removal that really happened, and drops the removed object from its
live account exactly once so a second reversal cannot aim at it. All four sites
were reproduced first. **36 new fault-injection tests; sixteen single-point
reversals, all caught.**

**One discrepancy is reported rather than resolved.** The installed concrete
plan carried review-manifest digest `5df17256…`, the C-P5.0-LAB-D12-R1 value,
not the `5602eb95…` the R3 handback reported — so either that artifact was not
installed or the reported digest was computed from a tree that was not
submitted. This pass regenerates and installs both artifacts; the digest is
maintainer and reviewer business, not an implementer's to reconcile.

**No RAID item opens or closes.** **LAB-V6-1**, **LAB-V6-2** and **LAB-V6-3**
remain open maintainer stop conditions and **V11 must remain unapplied** while
they are; V6 remains performed but not closed; I3 remains unconfirmed; V7
excluded; V8 and V10 unperformed; LAB-R6, LAB-X1, C-7, EH-R16-1, P5.0-R5 and
OD-62 remain Open; Package 5.0 remains not ready. Next action: independent Codex
technical and security re-review.

## V6 descriptor-finalization remediation returned for re-review — 2026-09-16

Claude completed **C-P5.0-LAB-V6-R3** and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-r3-descriptor-finalization-handback.md).
**No host was touched and nothing closes here.**

**PR-20260916-LAB-V6R2-1 is repaired and returned for re-review, not closed.**
Releasing a descriptor is now treated as an operation that can fail rather than
as cleanup. All three descriptors the application path holds are released
through one helper that reports instead of raising, so a failing `close()`
neither escapes as a raw `OSError` nor replaces the refusal it was unwinding. A
release failure with nothing else in flight is the closed refusal
`descriptor-not-released`, carrying the object **exactly once** with the
identity its read-back established, so guarded rollback survives. An ambiguous
`close()` is treated as ambiguous: no reuse, no retry, and **no leak claimed in
either direction**. The reviewer's reproduction was reproduced first and is
closed. 28 new fault-injection tests; twelve single-point reversals, all caught.

**One thing is reported rather than repaired.** `_verify_one` — used by
`verify()` and by the already-provisioned path — and `_remove`, used by guarded
rollback, still release their descriptors with a bare `os.close` and can still
raise. Both are outside the post-`mkdirat` window this finding governs, and
`verify()` is the read-only V6 re-observation whose contract is to return
findings rather than refuse. Scoping them is a maintainer's decision; this pass
reproduces all four sites and leaves them unchanged.

**No RAID item opens or closes.** **LAB-V6-1**, **LAB-V6-2** and **LAB-V6-3**
remain open maintainer stop conditions and **V11 must remain unapplied** while
they are; V6 remains performed but not closed; I3 remains unconfirmed; V7
excluded; V8 and V10 unperformed; LAB-R6, LAB-X1, C-7, EH-R16-1, P5.0-R5 and
OD-62 remain Open; Package 5.0 remains not ready. Next action: independent Codex
technical and security re-review.

## V6 post-creation partial-state remediation returned for re-review — 2026-09-16

Claude completed **C-P5.0-LAB-V6-R2** and returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-r2-partial-state-handback.md).
**No host was touched and nothing closes here.**

**PR-20260916-LAB-V6R1-1 is repaired and returned for re-review, not closed.**
Every failure after the applier's `mkdirat` succeeds is now a closed refusal
carrying the object it left: the created directory appears in the returned
`ProvisioningRun.applied`, `(st_dev, st_ino)` is preserved wherever the object
can still be observed, and an object whose identity was never established is
reported as residue that guarded rollback refuses — for the whole reversal, not
only for itself. Both reviewer reproductions were reproduced first and are
closed. 15 new fault-injection tests; nine single-point reversals, all caught.

**No RAID item opens or closes.** **LAB-V6-1**, **LAB-V6-2** and **LAB-V6-3**
remain open maintainer stop conditions and **V11 must remain unapplied** while
they are; V6 remains performed but not closed; I3 remains unconfirmed; V7
excluded; V8 and V10 unperformed; LAB-R6, LAB-X1, C-7, EH-R16-1, P5.0-R5 and
OD-62 remain Open; Package 5.0 remains not ready. Next action: independent Codex
technical and security re-review.

## V6 provisioning remediation review — Blocking partial-state defect — 2026-09-16

Codex's independent
[review](../review/project-review-2026-09-16-reserved-laboratory-v6-provisioning-remediation.md)
requests changes and opens **PR-20260916-LAB-V6R1-1 — Blocking**. After the
new directory applier's `mkdirat` succeeds, post-creation failures can leave a
directory on disk without a truthful returned partial-application record or a
recorded identity for guarded rollback. Even the handled barrier-failure path
omits the current visible directory from `ProvisioningRun.applied`/`created`.

Provisioning remains unreleased. LAB-V6-1, LAB-V6-2 and LAB-V6-3 remain open
maintainer stop conditions; V6 remains performed but not closed and I3 remains
unconfirmed. Next action: bounded repository-local remediation with fault
injection at every post-`mkdirat` stage, followed by independent review.

## V6 provisioning contract completed and returned for review — 2026-09-16

Claude completed **C-P5.0-LAB-V6-R1** in one bounded repository-local pass and
returned the
[handback](../review/phase-5-0-reserved-laboratory-v6-provisioning-remediation-handback.md).
**No host was touched and nothing closes here.**

The r6 §7 delta is now **eleven items**. The missing specification is stated as
**V11 — `/opt/freedom-blades/evidence`, `0700 root:root`** — with its creation
mechanism, persistence, verification and rollback, and the mode is **derived**
from the execution model in r6 §7.2 rather than chosen: the only process that
opens D1 or issues C1 is the executor, which cannot reach any effect unless it
is already effective UID and GID 0, and every object under `R` is reached by an
inherited descriptor rather than by a pathname. `fs.protected_hardlinks` does
not bear on the item, because no exclusive publication happens in that
directory. Every item now also states its creation, persistence, verification
and rollback, and `execution/provisioner.py` applies the four directory items
idempotently and fail-closed.

**New issue — LAB-V6-1, Open. The observed parent defeats the root-only claim.**
V6 found `/opt/freedom-blades` as `1001:1001 0755`. A directory `0700
root:root` under a parent `ubuntu` may write is not a root-only object: the
parent's write bit governs renaming and unlinking the **entry**. So r6 §1.4.1's
administrator-only exposure argument **does not hold on `oracle-test` as it
stands**. It is reported rather than repaired — `chown root:root
/opt/freedom-blades` is a permission change to an existing path that holds the
repository worktree, it is outside the approved subset, and it is Peter's
decision. The applier refuses `parent-unsafe-ownership` until it is taken.

**New issue — LAB-V6-2, Open. `/var/lib/freedom-blades` is absent and no item
defines it.** V4 and V5 are created beneath it and r6 §2.2 states it as
`root:root 0755`, but no §7 item creates it. It is the same class of defect as
V11's, at a second path; a twelfth item is not defined here because the
assignment authorizes one and Peter's approval names V1–V5, V9 and that one.
The applier refuses `parent-absent` for V4 and V5 until a maintainer rules.

**New issue — LAB-V6-3, Open. `R`'s location is unreconciled.** r6 §1.3.3 writes
`R = /opt/freedom-blades/evidence/<run>`; the approved target's root is
`/var/lib/fb-evidence-p5-0`, the concrete plan creates exactly that, and
`targets.validate_mutation_root` would refuse the former outright. Both cannot
be `R`. Related: `plan.EVIDENCE_ROLE` has **no production caller** — D1 is
specified, named and unbuilt. Changing either is a §0.2 change-control matter.

**V7 stays excluded and I3 stays unconfirmed.** The lifecycle record is not
initialized: its `linkat` is the first real exclusive publication on the target.
A provisioned host without it refuses all seven participants, which is the
fail-closed state the release is meant to end in. V6 remains performed but not
closed; V8 and V10 unperformed; LAB-R6, LAB-X1, C-7, EH-R16-1, P5.0-R5 and
OD-62 remain Open; `is_executable` remains False; Package 5.0 remains not ready.

## V6 prerequisite provisioning approved; specification remediation assigned — 2026-09-16

Peter approves prerequisite provisioning for `freedomlab` and the exact
directories with reviewed owners and modes. The accepted V6 survey exposed one
missing specification: `/opt/freedom-blades/evidence` is absent and required,
but r6 gives it no exact provisioning item beyond “root-only [A]”. Applying an
invented owner/mode would cross the review gate.

Claude is assigned
[C-P5.0-LAB-V6-R1](../review/phase-5-0-reserved-laboratory-v6-provisioning-remediation-claude-prompt.md)
to complete and test the repository-local provisioning contract, then stop for
independent Codex review. No host mutation is authorized in that remediation.
V7 and I3's controlled write remain separately gated; V6 remains performed but
not closed, and the standing package blockers remain Open.

## D12-R1 accepted; V6 observed but not closed — 2026-09-16

Peter accepted Codex's independent D12-R1 re-review, closing
**PR-20260915-LAB-D12-1**, and released the V6 read-only prerequisite survey.
The [dated record](../review/project-review-2026-09-16-reserved-laboratory-d12-r1-acceptance-and-v6-preflight.md)
records ext4 at both future location families, `fs.protected_hardlinks=1`, the
`ubuntu` execution identity and zero permitted/effective/ambient capabilities.

**V6 was performed but does not close:** the exact publication directories and
the proposed `freedomlab` group are absent, so their required ownership/mode
assumptions cannot be confirmed. The survey proves no real `linkat` viability;
I3 remains unconfirmed and controlled write verification remains separately
gated. V8 and V10 remain unperformed. LAB-X1 and the standing package blockers
remain Open, `is_executable` remains False and Package 5.0 remains not ready.

## D12-R1 remediation returned for re-review; LAB-X1 opened — 2026-09-15

Claude completed **C-P5.0-LAB-D12-R1** in one bounded repository-local pass and
returned it for independent Codex technical and security re-review. The
authoritative admission path now refuses on the lifecycle record's leftover
publication temporary, before any of the seven participants proceeds, and T1's
and T6's operator recovery requires an immediately preceding `(st_dev, st_ino)`
comparison before the temporary is removed.

**PR-20260915-LAB-D12-1 is remediated and remains Open.** The implementer closes
no finding. The read-only preflight remains authorized and queued behind that
re-review and Peter's release.

**New issue — LAB-X1, Open.** Runner contract r6 §1.4.4's X1 step requires
`execveat(…, AT_EMPTY_PATH)` and no implementation route is chosen: Python
3.12's `os` has no `execveat`, and the candidate `os.execve`-on-a-descriptor
route reaches it through `fexecve(3)` only where glibc and the kernel provide
it, otherwise falling back to `/proc` — which re-resolves a pathname and gives
up the descriptor binding X1 exists for. **Owner:** the agent Peter designates
as Package 5.0's working Technical Lead. **Required evidence and execution stop
condition:** r6 §6.4, which also records that widening the one `ctypes`
exception would be a separate approval. **While LAB-X1 is open, X1 is not
executed**: `plan.is_executable` stays False and
`reservation.REAL_EXECUTION_REFUSAL` stands unconditionally. Choosing the route
is a separate authorized pass, and C-P5.0-LAB-D12-R1 forbade choosing one.

**V6 is dispositioned, and it closes nothing.** Peter approved it as a read-only
prerequisite survey of filesystem and mount type, `fs.protected_hardlinks`,
execution identity, ownership and mode assumptions and relevant capability
state. It does not prove real `linkat` viability and does not close **I3**; a
controlled write verification requires separate authorization before execution.

C-7 remains unresolved; EH-R16-1, LAB-R1, LAB-R2, LAB-R3, LAB-R5, LAB-R6,
LAB-D1/C-7, LAB-D2 and OD-62 remain Open; `is_executable` remains False; all
twelve target facts remain unconfirmed; Package 5.0 remains not ready; P5.0-R5
remains Blocking.

## Historical — D1/D2 correction re-review — Blocking admission defect — 2026-09-15

The independent
[re-review](../review/project-review-2026-09-15-reserved-laboratory-d1-d2-corrections.md)
adds **PR-20260915-LAB-D12-1 — Blocking**. A lifecycle record's leftover
publication temporary is not checked by the authoritative admission path, so
the six ordinary participants can proceed on the final record while the
interrupted publication remains unresolved. All seven must refuse until
attributable recovery.

Peter approves V6 as a read-only prerequisite survey only; I3 remains
unconfirmed and controlled write verification remains separately gated. The
authorized preflight stays queued behind remediation and re-review.

## Historical — D1/D2 accepted; preflight queued behind independent document review — 2026-09-15

Peter approves D1 and D2 and authorizes the documented read-only target
preflight. Their contract delta is applied to r6. A different Independent
Reviewer must review the edit before preflight because Codex applied it.
The D1/D2 amendment moves from proposed to applied-in-contract, awaiting that
review; no target fact is confirmed and no operational mutation is authorized.
*Corrected 2026-09-15:* this entry first said that "LAB-D1 and LAB-D2" moved.
Those RAID items are the C-7 producer dependency and the twelve unconfirmed
target facts. They are unrelated to the D1/D2 amendment and unchanged.

## Historical — reserved-laboratory one-shot authority re-review accepted — 2026-09-15

Codex's independent
[re-review](../review/project-review-2026-09-15-reserved-laboratory-one-shot-authority.md)
closes **PR-20260914-LABI-R2-1** with no residual finding inside the explicitly
stated ordinary-object-graph boundary. Arbitrary same-interpreter Python remains
outside that claim; treating it as adversarial would require a separately
approved process boundary.

LAB-R1, LAB-R2, LAB-R3, LAB-R5, LAB-R6, LAB-D1/C-7 and LAB-D2 remain open. No
target fact was observed and no operational action is authorized. The next
action is maintainer direction on the standing blockers and proposed decisions.

## Historical — reserved-laboratory one-shot authority remediation assigned — 2026-09-15

The independent
[live-authority re-review](../review/project-review-2026-09-14-reserved-laboratory-live-authority.md)
adds **PR-20260914-LABI-R2-1 — Blocking**. Clearing `_authority` revokes one
object but records no non-reusable invocation transition: the live callback can
call `_issue_authority()` again after consumption, or assign a fully bound
constructed permit to the mutable registration. Both public synthetic
regressions reach a second armed execution under one durable start.

Peter assigns the bounded
[C-P5.0-LAB-I-R2 remediation](../review/phase-5-0-reserved-laboratory-live-authority-r2-claude-prompt.md).
It must make issuance single-transition, make consumption depend on
invocation-owned state not replaceable through the reviewed callback graph,
retain the two reproductions and add independent reversals. The finding remains
open until independent Codex re-review; the implementer cannot close it.

LAB-R1, LAB-R2, LAB-R3, LAB-R5, LAB-R6, LAB-D1/C-7 and LAB-D2 remain open. No
target fact was observed and no operational action is authorized.

## Historical — reserved-laboratory call-graph remediation returned; awaiting Codex re-review — 2026-09-14

The bounded remediation of Codex's re-review finding is
[returned](../review/phase-5-0-reserved-laboratory-call-graph-remediation-handback.md)
for independent technical and security re-review. It moves one issue **without
closing it**, because an implementer does not close a review finding.

* **PR-20260914-LABI-R1-1 — Blocking** — the executable call graph is repaired
  and has public regressions. `ParticipantIntegration.run_harness` owns the
  harness call through one orchestration path; the armed executor requires an
  unforgeable `EffectPermit` issued only after a durable `participant_started`
  and bound by equality to the harness participant, run id and reservation; the
  release evidence is derived from the executor's own cleanup, residue and
  restoration outcome and from the session's own open lock descriptor; §5.12's
  two terminal entries are published before the lock is released; and an
  exception leaves the durable start unsettled. The reviewer's `session=object()`
  reproduction refuses and reaches no effect, and the reversal that restores the
  presence-only check makes that regression fail. **Awaiting re-review.**

**PR-20260913-LABI-1 and -2 were accepted by the 2026-09-14 re-review** and are
carried below as closed by that review rather than by this pass.

**LAB-R6 is unchanged and still open.** The six non-harness integration points
exist and nothing outside the repository calls them. The re-review agreed this
must not be closed here: an integration point refuses on an absent lock, so
wiring the six on an unprovisioned host would stop the bot suite, the web suite,
the Foundry tests, synchronization, dependency updates and the environment
reset. Closing it needs a separately authorized, ordered provisioning-and-wiring
rollout. No wrapper was weakened and no lock is created on demand. Mitigation
today: they are not connected.

**New observation carried with this pass.** r6 §5.7's **T7** and **T8** — the
reservation's own `admitted` and `running` entries — are published by
`run_harness`, because without them `conclude_reservation` refuses a release of a
reservation the stored history never admitted and §5.12 has no reachable
successful path. If the intended owner of those two durable writes is an
out-of-band operator action rather than the harness, that is a maintainer's
ruling and is raised as question 2 of the handback.

LAB-R1, LAB-R2, LAB-R3, LAB-R5, LAB-R6, LAB-D1/C-7 and LAB-D2 remain open. No
target fact was observed and no operational action is authorized.

## Reserved-laboratory remediation returned; awaiting Codex re-review — 2026-09-14

The C-P5.0-LAB-I-R1 remediation is
[returned](../review/phase-5-0-reserved-laboratory-implementation-remediation-handback.md)
for independent technical and security re-review. It moves the three issues
below **without closing any of them**, because an implementer does not close a
review finding.

* **PR-20260913-LABI-1** — the fail-open path is repaired and has public
  regressions: the reviewed capture set is bound at the integration boundary,
  the whole requested set is validated before the recovery run directory
  exists, the destination a record binds is derived rather than supplied,
  publication verification and restart discovery both establish the
  correspondence restoration consumes, and the reviewer's `/wrong/destination`
  reproduction refuses and publishes nothing. **Awaiting re-review.**
* **PR-20260913-LABI-2** — a non-empty creating-step identity is now a
  mandatory prerequisite of set, clear and removal; three inputs refuse before
  any `ioctl`, `unlinkat` or `rmdir`; equality is the only admitting branch; and
  every production creation path records the identity inside the creation. The
  reviewer's unrecorded-removal reproduction refuses and the file survives.
  **Awaiting re-review.**
* **PR-20260913-LABI-3** — the protocol is wired through
  `execution/participants.py` for all seven entry points, the CLI's `--execute`
  branch, the boundary's declared descriptor table and the 35 reviewed steps
  that were `install`/`chattr` vectors; `PERMITTED_EXECUTABLES` is 20.
  **One part is explicitly incomplete and carried as an open item:** the six
  non-harness integration points exist and nothing outside the repository calls
  them, because this authorization forbids invoking a real participant.
  **Awaiting re-review and a follow-up authorization.**

**New risk carried forward — LAB-R6.** An integration point refuses on an absent
lock or an absent reservation record. Wiring the six participants to call one on
an **unprovisioned** host would therefore stop the bot suite, the web suite, the
Foundry tests, synchronization, dependency updates and the environment reset.
The r6 §7 delta must be provisioned, or the wiring made conditional, before the
six are connected operationally. Mitigation today: they are not connected.

LAB-R1, LAB-R2, LAB-R3, LAB-R5, LAB-D1/C-7 and LAB-D2 remain open. No target
fact was observed and no operational action is authorized.

## Reserved-laboratory implementation review — changes requested, 2026-09-13

The independent technical and security
[review](../review/project-review-2026-09-13-reserved-laboratory-implementation.md)
adds three open implementation issues without closing any LAB entry:

* **PR-20260913-LABI-1 — Blocking:** recovery publication can authorize M1 when
  the stored destination is not the configuration destination restoration will
  accept.
* **PR-20260913-LABI-2 — Blocking:** a missing creating-step identity bypasses
  the flag/removal ownership comparison; public `remove_object()` deleted an
  unrecorded file in the independent reproduction.
* **PR-20260913-LABI-3 — Important:** the new enforcement objects have no
  consumer in the executor, CLI or any of the seven participant entry points,
  and the old `install`/`chattr` plan remains.

LAB-R1, LAB-R2, LAB-R3, LAB-R5, LAB-D1/C-7 and LAB-D2 remain open. No target
fact was observed and no operational action is authorized.

## Reserved-laboratory mechanism implemented; awaiting Codex review — 2026-09-13

The C-P5.0-LAB-I implementation is
[returned](../review/phase-5-0-reserved-laboratory-implementation-handback.md)
for independent technical and security review. It moves the LAB entries below
**without closing any of them**, and code that exists is not a risk that closed.

* **LAB-R1** — the controls it names are now built rather than proposed: the
  cooperative lock adapter, the reservation record, the run ledger and the
  fail-closed admission all exist as mechanism. **Not closed.** Nothing is
  provisioned, so nothing is enforced on the target, and the modes are accident
  guards rather than barriers between the seven shared-identity participants.
* **LAB-R2** — unchanged in substance and now exercised over real files: no
  outgoing transition from quarantine, no resumption by recovery, no identity
  reuse, and an unsettled run blocking every successor including the reset.
* **LAB-R3** — **Open and unchanged.** The reservation still does not close
  EH-R16-1: the run's own experimental writers remain able to substitute an
  object mid-run, and r6 §1 is the whole of the answer to that.
* **LAB-R5** — unchanged. Package-level P5.0-R5 remains **Blocking**; no
  operational evidence was produced and none was authorized.
* **LAB-D1 / C-7** — the producer-to-importer adapter that was missing now
  exists and **resolves nothing**: with all eight variants supplied and every
  record well formed, all three cases stay unresolved, none is covered, and the
  importer classifies no record at all.
* **LAB-D2** — unchanged. All twelve target facts remain unconfirmed and V6, V8
  and V10 remain unperformed.

**Three items are raised for a reviewer's ruling and are not decided here:** the
`linkat`/`unlinkat` substitute for an unreachable `RENAME_NOREPLACE`; the
listing descriptor r6 §1.3.3 does not enumerate while §§2.5 and 5.11 require
`readdir`; and `PERMITTED_EXECUTABLES` remaining at 22 rather than r6 §6.4's 20.

No disposable-server action was performed and none is authorized.

## Reserved-laboratory local implementation authorized — 2026-09-13

C-P5.0-LAB-I authorizes repository implementation and local tests for the r6
mechanism. It treats LAB-R1/LAB-R2/LAB-R3 and LAB-R5 only by permitting the
specified controls to be built; none closes until independent review and later
target evidence. LAB-D1/C-7 remains unresolved pending producer implementation
and review. LAB-D2 remains unchanged because all target facts are unconfirmed.
No disposable-server action is authorized.

## LAB-1 local issue closed — 2026-09-13

Codex's independent [R3 re-review](../review/project-review-2026-09-13-lab1-rereview-r3.md)
accepts PR-20260912-LAB1-2 with no residual finding. **LAB-1 is Closed** in its
local remediation scope. LAB-R1 through LAB-R5 are not closed by that result:
reservation enforcement is still unbuilt, C-7 and EH-R16-1 remain unresolved,
the twelve target facts remain unconfirmed, and no real execution is authorized.

## Reserved laboratory remediation returned — C-P5.0-LAB-1, 2026-09-11

Claude's [handback](../review/phase-5-0-reserved-laboratory-handback.md) and the
submitted [runner contract](../review/phase-5-0-reserved-laboratory-runner-contract.md)
move the LAB entries below without closing any of them. Nothing here is accepted.

| Local ID | Type / owner | State and treatment |
|---|---|---|
| LAB-R1 | Risk / Operations Owner | **Partially treated, not closed.** The cooperative-admission decision mechanism and the writer inventory are implemented and tested (`tools/phase_5_0_evidence/reservation.py`, 41 injected cases); the lock **adapter** is proposed and not built, so no reservation is enforced yet. The no-malicious-root claim is stated in `LOCK_LIMITS` and asserted by a test. |
| LAB-R2 | Risk / Technical Lead | **Treated in decision, not in enforcement.** Quarantine has no outgoing transition, recovery never resumes a reservation, an expired deadline moves a run to `recovering` and authorizes no takeover, and release requires observed child-process termination and settled transactions with `None` treated as `False`. Enforcement still needs the lock adapter and the EH-R16-1 remedy. |
| LAB-R3 | Risk / Security Reviewer | **Open and unchanged.** Reservation does not close EH-R16-1: the handback and contract §0 state that the run's own experimental writers remain able to substitute objects. The unconditional real-execution refusal is retained. |
| LAB-D1 | Dependency / Technical Lead and Acceptance Authority | **Analysed; one split submitted.** All three C-7 cases have bounded local producers establishing feasibility only, and all three remain declared unresolved. `JNL-47-RECOVERY-STATE` cannot be meaningful without gated product code; the exact criterion split is submitted with a recommendation in handback §3.4 and is **not adopted**. |
| LAB-D2 | Dependency / Codex and Operations Owner | **Unchanged.** Twelve target facts remain unconfirmed and were not populated. The later read-only preflight remains assigned to Codex and unperformed. |
| LAB-R4 | Risk / Delivery Lead | **Unchanged.** `PARTICIPATING_ENTRY_POINTS` enumerates the seven entry points that must serialize on the lock, which makes the availability cost explicit. No additional environment was added. |
| PR-20260910-R2-1 | Issue / Claude, Codex review | **Fixed, pending review.** Reproduced before change on the reported cell; reads and writes now aggregate equivalent entries through one shared identity rule with no persistence on read; 17 regression tests, 17 of which fail against the pre-fix read. Claude does not close its own finding. |
| **LAB-1** | Issue / Claude, **new 2026-09-11**, Codex classifies | A §2.13.2b run reaching state S-B on residue alone reports **no named operator recovery**: `CleanupOutcome.recovery_procedure` carries only the configuration recovery and only when a capture was retained, while `journal.RECOVERY_PROCEDURE` is never attached. Reported and **not repaired** — the fix changes an accepted contract behind the outstanding design checkpoint. Reproduced by a labelled defect-reproduction test that deliberately asserts the record fails. Proposed Important. |
| **LAB-R5** | Risk / Technical Lead, **new 2026-09-11**, not accepted | The EH-R16-1 remedy requires four descriptor-relative verbs and four new syscalls in the reviewed case program (contract §9.2). That expands the trusted computing base's verb table from 16 to 20. The exact diff is submitted for Codex review and **nothing is implemented**; the permission delta added by this pass is **zero**. |

## Reserved laboratory impact — C-P5.0-LAB-1, 2026-09-10

The [direction](../review/phase-5-0-reserved-laboratory-direction.md) is authorized;
the following controls are obligations to implement/review, not verified facts.

| Local ID | Type / owner | State and treatment |
|---|---|---|
| LAB-R1 | Risk / Operations Owner | Reservation can be bypassed accidentally by another trusted agent or automation. Whole-host scheduling, cooperative admission and writer inventory required; no malicious-root exclusion claim. |
| LAB-R2 | Risk / Technical Lead | Crash, lock release or timeout can leave children or transactions active. Quarantine blocks automatic reuse until termination, residue and recovery are established. |
| LAB-R3 | Risk / Security Reviewer | Test-created privileged writers can still substitute recovery inputs/destinations. Explicit case scope, source custody and quiescence remain required; reservation does not close EH-R16-1. |
| LAB-D1 | Dependency / Technical Lead and Acceptance Authority | Three C-7 producers missing. Minimum synthetic facsimiles may establish feasibility, not production behavior. Resolve each requirement first; submit any necessary criterion split without waiving it. |
| LAB-D2 | Dependency / Codex and Operations Owner | Twelve target facts unconfirmed. Existing later preflight follows implementation review; no host collection performed by this direction. |
| LAB-R4 | Risk / Delivery Lead | Whole-host reservation delays other test/development work. Serialize and name the owner; do not add infrastructure by default. Track accepted evidence and closed blockers rather than raw test counts. |
| PR-20260910-R2-1 | Issue / Claude, Codex review | Blocking CRP alias read/write inconsistency. Separate bounded fix and threshold regressions in the active prompt. |

VM proposal risks below remain historical unresolved risks against that deferred
alternative. No production residual or package gate is accepted by LAB-1.

## Proposed VM evidence boundary — 2026-09-10

These entries describe the [unaccepted VM proposal](../review/phase-5-0-evidence-vm-design.md),
not verified host facts or accepted residuals. Claude's independent review is
assigned in [Handover information](../review/Handover%20information).

| Local ID | Type / owner | State and next action |
|---|---|---|
| VM-R1 | Risk / Operations Owner, independent security reviewer | New hypervisor/controller privilege boundary could expose host resources. Unaccepted; Claude reviews confinement and ownership, then Peter decides VM-D2/3. |
| VM-A1 | Assumption / Operations Owner | KVM, capacity and required confinement on candidate oracle-test are unverified. No new inspection authorized; exact feasibility scope follows review and VM-D2. |
| VM-R2 | Risk / Technical Lead, independent reviewer | Guest behavior may not establish target filesystem/durability or host-specific controls; guest compromise can invalidate observations. Require per-band equivalence and observation-integrity limits before evidence acceptance. |
| VM-R3 | Risk / Operations Owner | Controller crash or unavailable management service may leave an allocation. Require durable identity-bound recovery, quarantine and verified disposal; no automatic clean claim. |
| VM-DP1 | Dependency / Acceptance Authority | Independent review by Claude and VM-D1/2/3 decisions precede implementation/operations. ADR 0011 remains proposed. |
| VM-R4 | Risk / Operations Owner | **Raised 2026-09-10 by VM-1.** The design's exclusive-controller premise is contradicted by `oracle-test`'s documented multi-agent passwordless-root profile, and adopting it as management host would convert the confirmed disposable target into a trusted component. Unaccepted; Codex must name a sole-controller host or withdraw the premise. |
| VM-R5 | Risk / Technical Lead, independent reviewer | **Raised 2026-09-10 by VM-2 and VM-3.** The registry publication path re-instantiates PR-20260910-1's staged-write-then-rename mechanism, and disposal deletes by a volume key the cited libvirt documentation does not pin for a directory-backed pool. Unaccepted; a destructive operation can reach an unowned host resource. |
| VM-R6 | Risk / Technical Lead | **Raised 2026-09-10 by VM-4 and VM-5.** No in-guest ownership guard is proposed, so design §10's "affected evidence not silently passed" is unsatisfiable; and the existing executor is refused only by data-conditional target facts an already-authorized preflight would clear, not by EH-R16-1. Unaccepted. |

Claude's independent review returned **changes requested** on 2026-09-10:
[`VM evidence boundary independent review`](../review/phase-5-0-evidence-vm-independent-review.md).
VM-R4, VM-R5 and VM-R6 are recorded from it and **none is accepted**.

EH-R16-1, PR-20260910-1/2/3 and P5.0-R5 remain open. These local IDs do not
replace existing finding, risk or OD identities. No package gate is changed.

**Evidence authorization update, 2026-09-02.** Peter Duscha authorized the
bounded pre-implementation evidence harness needed to test A-5.0-4/A-5.0-5 and
P5.0-R4/P5.0-R5 in a synthetic disposable environment. This resolves the
authorization circularity only; it confirms no assumption, closes no finding,
accepts no residual and authorizes no Package 5.0 product implementation.

**Current Package 5.0 decision disposition, 2026-09-02.** OD-64 Option A,
OD-65 Option B and OD-66 Option A / J-1 are approved. The corresponding
decision portions of D-5.0-2 are discharged; OD-62 remains Open with G-A only a
provisional direction pending P5.0-R5 operational evidence and independent
review. A-5.0-3 through A-5.0-5 and R-5.0-12 through R-5.0-16 remain open;
approval of OD-66 did not silently confirm or accept them.

**Security re-review, 2026-09-02.** P5.0-SR1 and P5.0-SR2 are Closed on design
after Codex's revision-12 re-review. No new Blocking or Important design finding
was identified. This does not close P5.0-R1, P5.0-R4 or Blocking P5.0-R5, accept
R-5.0-12 through R-5.0-16, confirm A-5.0-3 through A-5.0-5, or substitute for
C-1/C-3/C-4 and the remaining operational evidence. Package 5.0 remains `not
ready`.

**Decision update, 2026-09-02.** P4-PG4 and P4-PG5 are Closed after Codex
independent review and Peter Duscha's acceptance; Phase 4 remains approved and
closed. OD-63 / D5.0-10 Option 1 is also accepted: all nine numeric controls are
fixed, with N5.0-18 explicitly **an operational margin, not a barrier**.
A-5.0-3 remains unconfirmed. No RAID row is opened, closed or narrowed by the
numeric ruling, and Package 5.0 remains `not ready`.

**Phase 4 post-gate R2 disposition, 2026-08-31.** P4-PG1, P4-PG2 and
P4-PG3 are **Closed** after bounded remediation and Codex review. P4-PG4 and
P4-PG5 are **Open Important findings**: malformed idempotency keys escape the
typed envelope refusal, and malformed stored receipt command names escape the
typed unreadable-receipt replay refusal. No new standing RAID row is required:
both are bounded, reproducible implementation defects with an authorized
correction and immediate owner. Per maintainer direction, Package 5.0 readiness
work pauses until their remediation and re-review complete. This changes no
Package 5.0 risk, assumption, dependency or decision; its `not ready` state and
implementation prohibition remain.

**Superseded as the active work item — Package 5.0 security review returned,
and remediation R11 submitted, 2026-08-31.**

The §9.2 security pass ran once and returned **changes requested
with no readiness recommendation**: **P5.0-SR1 (Blocking)** — the deployment
integrity check can be skipped silently, because its comparison takes both sides
from the live deployed bytes and no step refuses when the comparison against the
reviewed commit is omitted — and **P5.0-SR2 (Important)** — the OS identity
contract and the journal group contract contradicted each other about
`freedomjournal`. **Revision 12 remediates both and claims neither closed.**

**Two rows are proposed and none is closed, narrowed or added to the register
itself.**

- **R-5.0-15 — new, proposed.** The reviewed-source provenance of package plan
  §2.12.5a rests on three root-owned host artifacts: the bare Git object store,
  the approved-revision record and the provenance record. An actor holding **A5**
  rewrites all three so every host copy agrees on a tree it chose. The database
  still refuses, because the generation needs an `approved_source_revisions` row
  and that needs **A8** — **but an actor holding A5 *and* A8 approves and
  registers its own revision, and no check in this design refuses it.** That
  boundary is **operator trust, not a technical control**. Owner: Acceptance
  Authority. What remains is external: `sudo log_output`, journald,
  `audit_events`, offline backups and the `review_reference` a human can check.
  The design change that would narrow it — a signed approval record verified
  against a root-held keyring — is priced as **OD-66 option A-3** and
  deliberately **not adopted**.
- **R-5.0-16 — new, proposed.** A deployment with no approval record, no
  provenance record or a drifted tree cannot produce a journal generation at all,
  and a writer whose provenance record is removed refuses every Sheet mutation at
  **W11a**. An emergency redeployment fails closed until an approved revision
  exists. Owner: Operations Owner. Fail-closed and intended; it never permits an
  unjournalled or unprovenanced dispatch.

**Existing rows this touches.** **R-03** gains a revised estimate, **47.6** —
*and a correction: the package plan's own §5.1 copy of that figure still read
`35.5`, the revision-4 value, through six estimate changes; it is corrected
rather than updated silently.* **D-5.0-1**'s scope grows again: a **twelfth**
security surface, the canonical membership table to confirm identity by identity,
falsification row **F-13**, the widened **A5**, and a **third** unrefused
host-side residual; the estimate rises to **4.5–5.5** reviewer-days.
**A-5.0-5** is widened again — a disposable object store, a disposable approval
record, and the ability to run `id`, `namei -l` and `open` as four named
identities — and **remains unconfirmed**.

**Nothing else moves.** P5.0-R5 remains **Blocking**; P5.0-R1 and P5.0-R4 remain
open; P5.0-R2 remains closed; R-5.0-12, R-5.0-13 and R-5.0-14 remain unrefused
residuals awaiting acceptance under OD-66; check **C-1** remains not completed
and **C-3** and **C-4** not run. Package 5.0 remains `not ready` and
implementation remains unauthorized. **An independent security re-review of
revision 12 is required.**

**Superseded — Security Reviewer named, 2026-08-31.** Peter Duscha named **Codex** the
Package 5.0 Security Reviewer, closing OD-61 / D5.0-8. **No RAID row is closed,
narrowed or added by this.** P5.0-R5 remains **Blocking**; P5.0-R1 and P5.0-R4
remain open; P5.0-R2 remains closed; A-5.0-3, A-5.0-4 and A-5.0-5 remain
**unconfirmed**; R-5.0-12, R-5.0-13 and R-5.0-14 remain unrefused residuals
awaiting acceptance under OD-66. The security recommendation required by package
plan §9.2 is **still outstanding**, and the revision-11 design re-review is not
it. Package 5.0 remains `not ready` and implementation remains unauthorized.

**Superseded on the reviewer-naming point — revision 11 independent re-review, 2026-08-31.** No new Blocking or Important
design finding was identified; R10-A through R10-C are materially addressed on
paper. This closes the R10 remediation request only. It does not close
P5.0-R5, confirm A-5.0-5, accept an option, or authorize work. P5.0-R5 remains
**Blocking** pending authorized operational evidence; P5.0-R1 and P5.0-R4
remain open; P5.0-R2 remains closed; OD-62 through OD-66 remain Open; the
Security Reviewer remains unnamed; Package 5.0 remains `not ready`; and
implementation, migration, deployment, cutover and Package 5.1+ remain
unauthorized.

**Superseded — remediation R10 submitted, 2026-08-31.** Package 5.0 design remediation
**R10** — revision 11 of the package plan and the logical schema, plus
`docs/review/phase-5-0-remediation-r10-handback.md` — **claims no Blocking
finding closed**. **R10-A:** revision 10's E2–E6 launch recipes used a `setpriv`
securebit util-linux 2.39.3 documents as *"not allowed"*, so those five
identities never existed. The mechanism becomes **`capsh(1)`** — an already
installed, `root:root 0755`, no-file-capability distribution binary — because
`setpriv(1)` does not document the option ordering every declared mask depends
on, while `capsh(1)` does. **`+keep_caps` is used nowhere.** **R10-B:**
`E1 … E8` state exact UID, GID, supplementary groups, `CapPrm`, `CapEff`,
`CapInh`, `CapAmb`, `CapBnd` **and securebits**, each with a complete
invocation, and a **mask-versus-recipe comparison** derives every declared cell
from its command line. A **third** recipe/mask disagreement the re-review did not
name is recorded and corrected: E2–E6 asked `--bounding-set=+…` to **add** to a
bounding set, which the kernel does not permit. **R10-C:** dependent evidence is
revalidated; **`JNL-50` case 7 and `JNL-49` case 11 take `E6` as the isolating
control instead of `E2`**, E2 being retained as corroborating, and `JNL-50` case
4 gains a second control form. **Two stale copies of superseded wording in the
logical schema were found and corrected.**

**Nothing closes and nothing is added except one stop condition and one risk
row.** **`A-5.0-5` is widened** — it now names `capsh(1)`, `libcap2-bin` on the
target host, and the prerequisite that the launching process's bounding set
already holds every capability required, since **no tool can add to a bounding
set** — **and remains unconfirmed**. **No privileged case is claimed to have
run.** **R-5.0-12, R-5.0-13 and R-5.0-14 are unchanged, and no RAID row is added
or closed.** New §7.1 risk row **28** and new stop condition **10n** record the
recurrence class: a specification declaring a state its own recipe does not
produce. The evidence band (fifty identifiers, eighty-eight cases), the estimate
(**PERT 40.9**), the remediation allowance (**11.9**) and the security-review
estimate (**3.5–4.5** reviewer-days) are **unchanged**, and the plan states why
rather than recalculating. P5.0-R1 and P5.0-R4 remain open, P5.0-R2 remains
closed, P5.0-R5 remains **Blocking**, D5.0-9 … D5.0-13 / OD-62 … OD-66 remain
**Open**, the Security Reviewer remains **unnamed**, Package 5.0 remains
`not ready`, implementation remains **unauthorized**, and **an independent
re-review of revision 11 is required**.

**Superseded — revision-10 independent re-review, 2026-08-31 — remediation R10 required.**
P5.0-R5 remains **Blocking**. R9-A and R9-B are materially improved, but R9-C's
executable identities are not constructible as specified: util-linux 2.39.3
rejects the E2–E6 `+keep_caps` securebit; E8's recipe does not produce its
declared empty bounding set; and E7 does not declare complete inheritable and
ambient masks. The mandatory identity assertions therefore make affected
`JNL-49`/`JNL-50` cases inconclusive. **A-5.0-5 remains unconfirmed and is not
evidence that these recipes work.** No risk, assumption, dependency or decision
closes; no new RAID row is required because this is another realization of the
existing evidence-constructibility class. Remediation R10 and independent
re-review are required. Package 5.0 remains not ready and implementation is
unauthorized.

**Superseded — remediation R9 submitted, 2026-08-30.** Package 5.0 design remediation **R9** —
revision 10 of the package plan and the logical schema, plus
`docs/review/phase-5-0-remediation-r9-handback.md` — **claims no Blocking finding
closed**. **R9-A:** `FS_IOC_SETFLAGS` requires the caller's effective UID to equal
the inode's owner **or** `CAP_FOWNER`, in addition to `CAP_LINUX_IMMUTABLE` for
the immutable and append flags, and `CAP_DAC_OVERRIDE` is not a substitute. The
nine-authority register is redesigned into **eleven**: **A1** is narrowed to the
capability half, and **A10** and **A11** carry the owner authorization over the
`freedomsheet`-owned journal and over the root-owned seal and archive
respectively. **Eleven of the thirteen falsification rows gain a prerequisite**,
and every such change makes the alteration **harder** to construct — no refusal is
strengthened and no risk is narrowed. **R9-B:** the register keeps its
independence claim for the primitives and a new **holder table** carries the
bundling; detector reach is assessed against the smallest identity that can really
hold each combination, and the bounded claim is **narrowed** to F-2, F-3 and F-6.
**R9-C:** eight executable identities `E1 … E8` with complete permitted,
effective, inheritable, ambient and bounding sets and securebits; `JNL-49` and
`JNL-50` at **twelve cases each**, every negative flag case carrying a positive
control. **`A-5.0-5` is corrected rather than carried forward and remains
unconfirmed**; **no privileged case is claimed to have run**, and the revision-9
capability-only archive case is withdrawn as not constructible. **R-5.0-12's
authority set is corrected to `A1 + A2 + A3 + A10 + A11 + A9`, a larger set;
R-5.0-13 and R-5.0-14 are unchanged; no RAID row is added or closed.** New §7.1
risk row **27** records the recurrence class. **No risk, assumption, dependency or
decision is closed, and none is approved.** P5.0-R1 and P5.0-R4 remain open,
P5.0-R2 remains closed, P5.0-R5 remains **Blocking**, D5.0-9 … D5.0-13 remain
**open**, the Security Reviewer remains **unnamed** with the estimate raised to
**3.5–4.5** reviewer-days, Package 5.0 remains `not ready` and implementation
remains **unauthorized**.

**Superseded — revision-9 independent re-review, 2026-08-30 — remediation R9 required.**
P5.0-R5 remains **Blocking**. Revision 9 materially addresses R8-A, R8-B and
R8-D, but R8-C's replacement authority register omits the owner-or-`CAP_FOWNER`
authorization Linux requires for `FS_IOC_SETFLAGS`, in addition to
`CAP_LINUX_IMMUTABLE` for changing immutable/append flags. Its non-root
capability-only archive test and several minimum combinations are therefore not
constructible as stated. The register's assertion that A1–A6 confer nothing on
one another also conflicts with F-1a's statement that every real A3 holder has
A2. **A-5.0-5 remains unconfirmed and must be corrected, not treated as evidence
that the impossible capability set works.** No risk, assumption, dependency or
decision closes. Remediation R9, revision 10 and independent re-review are
required; Package 5.0 remains not ready and implementation unauthorized.

**Superseded — remediation R8 submitted, 2026-08-30.** Package 5.0 design remediation **R8** —
revision 9 of the package plan and the logical schema, plus
`docs/review/phase-5-0-remediation-r8-handback.md` — **claims no Blocking finding
closed**. All four Blocking inconsistencies are conceded and corrected. **R8-A:**
new §2.13.2c defines `deployment_manifest_digest()` — its computor, its exact
manifest including the unit file's drop-ins, and when it becomes final — and
Algorithm C **C0 computes it and refuses unless the operator's supplied value
equals it**, so the digest is validated against the **deployed bytes** before C1
consumes it, while **C2** keeps a consistency check and **recomputes** to catch a
deployment changed since C0; the universal *produced < validated ≤ consumed*
claim is **withdrawn** for invariants **I-1 … I-5**. **R8-B:** new §2.13.2b is one
three-state cleanup machine in which *"no generation artifact"* is unconditional
and *"no transient residue"* is conditional on cleanup success, with **one**
next-invocation behaviour — refuse for operator recovery — and revision 8's
automatic clean-and-reuse step **withdrawn**. **R8-C:** the eight-capability
register is **withdrawn** for **nine independently constructible authorities**
(`A1 … A9`) separating flag control from discretionary access, with per-row
minimum **combinations**; **F-2 → `A1 + A2`**, **F-4 → `A1 + A4`**, **F-5 →
`A1 + A3`**. **R8-D:** F-7's coordinator refusal is **withdrawn** — the registered
row carries the same `host_machine_id` the seal does — and the forged-matching
case becomes residual **R-5.0-13**, with the alternative routed as OD-66 **option
A-2** and not adopted. **No risk, assumption, dependency or decision is closed,
and none is approved.** P5.0-R1 and P5.0-R4 remain open, P5.0-R2 remains closed,
P5.0-R5 remains **Blocking**, D5.0-9 … D5.0-13 remain **open**, the Security
Reviewer remains **unnamed**, Package 5.0 remains `not ready` and implementation
remains **unauthorized**.

Status date: 2026-08-30 — Package 5.0 design remediation **R9** submitted for
independent re-review; it claims **no** Blocking finding closed; P5.0-R5 remains
Blocking; Package 5.0 remains not ready and implementation unauthorized.

**Remediation R8 note, 2026-08-30.** The revision-9 work is **documentation and
design only**. No production code, no migration `0014`, no database, host,
service or deployment change was made; **no `systemd-run`, `chattr` or `setpriv`
was run, and neither a probe arena nor `…/probe-ro` was created**; the host was
neither read nor written; and **no implementation suite was run, because no code
exists for this package and none changed**. The estimate moves from 39.5 to
**40.4 person-days** and the remediation allowance from 11.5 to **11.9**. The
security-review dependency D-5.0-1 rises from 2.5–3.5 to **3.0–4.0
reviewer-days** — **with no added surface**, because the cost is the nine-authority
threat model whose combinations must each be checked against real Unix DAC and a
second unrefused residual — and gains **two reviewer questions**. The evidence
band grows from seventy-four cases to **eighty-four** with **no identifier added**
(fifty); §6.5 items grow from eighteen to **nineteen**; new stop condition
**10l** is added and **10b**, **10f** and **10h** are extended while **10j** is
re-worded; new §7.1 risk rows **25** and **26** and new RAID rows **R-5.0-13**
(a forged matching `/etc/machine-id` is detected by nothing in this design) and
**R-5.0-14** (a failed privileged cleanup leaves a writer-writable transient
directory until an operator acts) are added. **A-5.0-5 is widened again** — a
non-root ambient `CAP_LINUX_IMMUTABLE` capability set, and a second host or a
host whose `/etc/machine-id` may be rewritten — and **remains unconfirmed**.
**Falsification rows stay at thirteen, fail-closed conditions stay at twenty-five,
refusal codes stay `SW-J01 … SW-J25`, V-W stays at eighteen steps, numeric
controls stay at nine, security-review surfaces stay at eleven, contingency stays
at 4.0, and every schema object is unchanged.** **No new decision number**;
OD-66 gains an **option A-2** that is routed under §0.2 and **not adopted**.

**Superseded — revision-8 independent re-review update, 2026-08-30.** P5.0-R5 remains
Blocking and remediation R8 is required. Four Blocking inconsistencies remain:
Algorithm C consumes the supplied deployment digest before its stated equality
validation; cleanup-failure cases require both absence and presence of the same
residue; `CAP_LINUX_IMMUTABLE` is incorrectly treated as bypassing archive DAC;
and F-7 names no detector that distinguishes a forged matching
`/etc/machine-id` from the registered value. R-5.0-12 remains active but does
not subsume these defects. No risk, assumption, dependency or decision is
closed or accepted. Package 5.0 remains not ready and implementation remains
unauthorized. The active handoff is remediation R8; revision 9 and independent
re-review are required.

**Superseded — remediation R7 submitted, 2026-08-30.** Package 5.0 design remediation **R7** —
revision 8 of the package plan and the logical schema, plus
`docs/review/phase-5-0-remediation-r7-handback.md` — **claims no Blocking finding
closed**. All three Blocking defects and the one Important governance defect are
conceded and corrected: **Algorithm C is renumbered C0 … C13** so that C0 checks
only pre-probe preconditions, C1 remains the single probe invocation and the
single creation point of the report, and a new **C2** validates the
result-dependent facts before any persistent artifact exists — with a
value-dependency table and two new construction tests; **Stage 4 gains an exact
target and a positive DAC control**, `…/probe-ro/s4-2.target` in a second
transient directory on the same mount, with new case **`S4-0`** proving it
writable by `freedomsheet` outside the sandbox before any `EROFS` is accepted,
`EACCES` classified **`inconclusive`** and a success classified **failed**; and
the **two-class attacker model is withdrawn** for an eight-capability register
(`K1 … K8`) stating, per falsification row, the minimum capability, whether it
also reaches the detector, the refusing actor, the exact step and code, and the
residual when it reaches both — **F-2 corrected to `K3`**, **F-7 corrected in the
opposite direction** because `/etc/machine-id` is root-writable, and
not-constructible pairings marked with the control that makes them so. **No risk,
assumption, dependency or decision is closed, and none is approved.** P5.0-R1 and
P5.0-R4 remain open, P5.0-R2 remains closed, P5.0-R5 remains **Blocking**, D5.0-9
… D5.0-13 remain **open**, the Security Reviewer remains **unnamed**, Package 5.0
remains `not ready` and implementation remains **unauthorized**.

Status date: 2026-08-30 — Package 5.0 design remediation **R7** submitted for
independent re-review; it claims **no** Blocking finding closed; P5.0-R5 remains
Blocking; Package 5.0 remains not ready and implementation unauthorized.

**Remediation R7 note, 2026-08-30.** The revision-8 work is **documentation and
design only**. No production code, no migration `0014`, no database, host,
service or deployment change was made; **no `systemd-run`, `chattr` or `setpriv`
was run, and neither a probe arena nor `…/probe-ro` was created**; the host was
neither read nor written; and **no implementation suite was run, because no code
exists for this package and none changed**. The estimate moves from 38.2 to
**39.5 person-days** and the remediation allowance from 11.1 to **11.5**. The
security-review dependency D-5.0-1 stays at **2.5–3.5 reviewer-days** and gains
**one surface element** — the `…/probe-ro` directory the writer's identity may
write during provisioning — and **two reviewer questions**. The evidence band
grows from forty-five identifiers and forty-eight cases to **fifty and
seventy-four**; the falsification-row count is corrected from a stated twelve to
the **thirteen** actually listed; new stop conditions **10i**, **10j** and
**10k**, a new §7.1 risk row **24** and a new RAID row **R-5.0-12** are added.
**A-5.0-5 is widened again** — a second transient directory on the same mount and
the `S4-0` control executed under the writer's uid outside any unit — and
**remains unconfirmed**. **Fail-closed conditions stay at twenty-five, refusal
codes stay `SW-J01 … SW-J25`, V-W stays at eighteen steps, numeric controls stay
at nine, and no schema object, decision number or work package is added.**

**New risk row, 2026-08-30.** **R-5.0-12 — the combined-authority residual.** An
attacker holding **both** `CAP_LINUX_IMMUTABLE`-bearing root on the host **and**
PostgreSQL superuser authority can rewrite the seal, record 0 and the registered
digests into mutual agreement. **No check in this design refuses that**, because
every check compares two copies and this attacker writes both. Owner:
**Acceptance Authority**, with the Security Reviewer. It is **detected, not
prevented** — by `sudo log_output`, journald, the `audit_events` chain, offline
backups, and the fact that a forged head has no `seal` record, no `.close`
manifest and no archive — and it is distinguished from `CAP_LINUX_IMMUTABLE`
**alone**, which reaches F-1b and *is* refused by the registered row. **Recorded
as a residual for D5.0-13, not as a control.** *Relabelled in revision 9 as
`A1 + A2 + A3` together with `A9`, the nine-authority register having replaced
the eight-capability one; the property is unchanged.*

**Two new risk rows, 2026-08-30 (remediation R8).** **R-5.0-13 — the forged
host identity.** An actor holding **A6** — root on whichever host the journal
tree is read on — restores the tree there and rewrites `/etc/machine-id` to the
value the seal records. `SB.host_machine_id`, the file and the **registered row**
then all carry that value, so **neither W10 nor C-d refuses**. *Revision 8's F-7
recorded a coordinator refusal; the registered row holds the forged value too,
and the claim is withdrawn.* Owner: **Acceptance Authority**, with the Security
Reviewer. **Not detected.** Bounded rather than mitigated: the restored tree
carries no production database, so the forgery is inert until its holder also
reaches the coordinator (**A8**) and, for registered rows, **A9**; and what
remains as evidence is `sudo log_output`, journald, `audit_events`, the
production host's own systemd and deployment records, and a forged head with no
`seal` record, `.close` manifest or archive. The design change that would make it
a refusal — an independent authenticated host-bound value — is **D5.0-13 / OD-66
option A-2**, routed under §0.2 and **not adopted**. **R-5.0-14 — the residue
state.** A failed privileged cleanup (§2.13.2b state **S-B**) leaves `…/probe` or
`…/probe-ro` — `root:freedomsheet 0770`, holding no evidence — in the state
hierarchy until an operator acts, and **blocks generation creation** while it is
there. Owner: **Operations Owner**. The residue is reported by absolute path with
its failed operation and `errno`, both privileged commands refuse while it exists
and **neither cleans it**, and the operations document names the recovery. It is
an **availability** cost accepted deliberately in preference to an automatic
clean, which would put a routine deletion of a writer-writable directory on the
happy path and mask an uninvestigated failure.

**Superseded — revision-7 independent re-review update, 2026-08-30.** P5.0-R5 remains
Blocking. Remediation R7 is required: Algorithm C consumes the probe result
before producing it; S4-2 does not isolate sandbox `EROFS` from DAC on the exact
target; and the falsification attacker classes exceed their stated
capabilities. Package 5.0 remains not ready and implementation unauthorized. No
risk, assumption, dependency or decision is closed.

**Remediation R6 submitted, 2026-08-30.** Package 5.0 design remediation **R6**
— revision 7 of the package plan and the logical schema, plus
`docs/review/phase-5-0-remediation-r6-handback.md` — **claims no Blocking finding
closed**. All four revision-6 defects are conceded and corrected: the capability
probe's **stage 4 moves to provisioning**, inside the same `verify-capability`
invocation and before the report is built, so the sealed digest covers the four
stages it names; the seal's **binding section loses `sealed_at` and its own
format field**, keeping exactly the three values V-W recomputes or compares, with
its structure fixed by a `binding_format_version` in the chain-authenticated
body, and **F-1 is split into F-1a — refused by the writer with no database —
and F-1b — a `CAP_LINUX_IMMUTABLE` rewrite of the seal *and* record 0, refused
only by the coordinator against PostgreSQL**; `JNL-32` becomes **`JNL-32a`** and
**`JNL-32b`**, the second expecting `SW-J06` at **W9** before **W17**, no
write-mode journal open and byte-for-byte unchanged evidence; and the corrupted
R5 handback is replaced. **No risk, assumption, dependency or decision is
closed, and none is approved.** P5.0-R1 and P5.0-R4 remain open, P5.0-R2 remains
closed, P5.0-R5 remains **Blocking**, D5.0-9 … D5.0-13 remain **open**, the
Security Reviewer remains **unnamed**, Package 5.0 remains `not ready` and
implementation remains **unauthorized**.

Status date: 2026-08-30 — Package 5.0 design remediation **R6** submitted for
independent re-review; it claims **no** Blocking finding closed; P5.0-R5 remains
Blocking; Package 5.0 remains not ready and implementation unauthorized.

**Remediation R6 note, 2026-08-30.** The revision-7 work is **documentation and
design only**. No production code, no migration `0014`, no database, host,
service or deployment change was made; **no `systemd-run`, `chattr` or `setpriv`
was run and no probe arena was created**; the host was neither read nor written;
and **no implementation suite was run, because no code exists for this package
and none changed**. The estimate moves from 37.7 to **38.2 person-days** and the
remediation allowance from 11.0 to **11.1**. The security-review dependency
D-5.0-1 stays at **2.5–3.5 reviewer-days** and gains **one surface element** —
the transient `systemd-run` unit stage 4 starts as root at provisioning — and
**one reviewer question**. The evidence band grows from forty-one identifiers and
forty-two cases to **forty-five and forty-eight**; falsification rows grow from
eight to **twelve**; a new stop condition **10h** and a new §7.1 risk row **23**
are added. **Fail-closed conditions stay at twenty-five, refusal codes stay
`SW-J01 … SW-J25`, numeric controls stay at nine, and no schema object, decision
number or work package is added.**

**Superseded — revision-6 independent re-review update, 2026-08-30.** P5.0-R5
remained Blocking. Remediation R6 was required because the sealed probe report
could not both exclude deployment-time stage 4 in Algorithm C and contain all
four stages as the schema claimed; V-W did not reject every seal-byte alteration
as F-1 claimed; and `JNL-32` expected W17 to run after W9 had already refused an
absent `+a` flag. The corrupted active handoff was replaced. Package 5.0 remained
not ready and implementation unauthorized. No risk, assumption, dependency or
decision was closed.

Superseded status date: 2026-08-30 — revision 6 independently re-reviewed;
remediation R6 required.

**Revision-5 independent re-review update, 2026-08-29.** P5.0-R5 remains
Blocking. Remediation R4 corrected the volatile path but introduced a circular
seal/genesis hash, assigned seal validation to a writer that cannot read the
seal, and specified a probe whose ordinary permissions mask the capability being
tested. The Boolean database check also cannot prove the probe ran. Remediation
R5 and independent re-review are required; implementation remains unauthorized.

Superseded status date: 2026-08-30 — Package 5.0 design remediation **R5** submitted for
independent re-review; it claims **no** Blocking finding closed; P5.0-R2 stays
closed; P5.0-R4 stays **open** pending security and operational evidence;
P5.0-R5's four revision-5 defects are conceded and corrected in revision 6 of the
package plan and the logical schema — the circular seal/genesis hash is replaced
by an **acyclic** construction anchored on a `seal_body_digest` computed before
the journal exists; the writer is given **minimum read-only** access to the seal
through a third system group `freedomjournal` so the validation it is assigned is
one it can perform; the append-only capability probe becomes a **four-stage,
disposable-arena** procedure whose control stage must pass before any refusal is
attributed to `FS_APPEND_FL`, and startup stops probing live evidence
destructively; and the `CHECK (append_only_verified)` claim is **withdrawn**,
replaced by an attested, re-derivable probe report bound to the generation.
**P5.0-R1 is unchanged and a durable journal is still not a barrier**; D5.0-9
remains a **risk acceptance**, D5.0-10 stays at nine controls, D5.0-11 remains
extended to the operating-system identity and host boundary, D5.0-12 is extended
by the third system group, D5.0-13's option A is re-stated, and the Security
Reviewer is unnamed; Package 5.0 is `not ready`

**Remediation R5 note, 2026-08-30.** The revision-6 work is **documentation and
design only**. No production code, no migration `0014`, no database, host,
service or deployment change was made, and **no implementation suite was run**.
The estimate moves from 35.5 to **37.7 person-days**; the security-review
dependency D-5.0-1 moves to **2.5–3.5 reviewer-days** over an **eleven-element**
surface.

## Package 5.0 readiness — 2026-08-29

### Independent design-review findings

| ID | Class | Finding | Required remediation | State |
|---|---|---|---|---|
| P5.0-R1 | **Blocking** | Startup checks and advisory process state cannot prevent overlapping old/new writers | Provide an enforceable quiescence boundary that prevents a paused legacy process from resuming and writing after activation | **Open. Remediation R3 submitted 2026-08-29 and claims it not closed.** The PostgreSQL transaction trigger closes the database half. For the Sheet half, R3 took the handoff's second permitted route: thirteen candidate barriers were traced against the published Sheets v4 and Drive v3 surface — the `batchUpdate` response, an operation id, an idempotency token, a conditional write, `files.version`, `revisions.list`, the Activity API, push notifications, a marker write, protected ranges, a file copy, Apps Script `flush()` and waiting — and each reduces to a quiet period, rests on an unpublished implementation property, is documented as unreliable, or does not exist. **The conclusion is that no accepted-request completion barrier exists in the published Google APIs**, and revision 3's enforceability claim is withdrawn. What replaces it is a stated weaker guarantee — drain before kill, an enumerable unresolved set, fail-closed activation, containment and two detection re-reads — and a priced **risk-acceptance** decision returned as OD-62. **The residual is R-5.0-8** and is owned by the Acceptance Authority. Codex decides whether this route closes the finding  **Unchanged by remediation R4, deliberately.** Revision 5 makes the dispatch journal durable, sealed, generation-bound and hash-chained, which makes the *enumeration* trustworthy across a reboot — and **is not a barrier and is not offered as one** (package plan §2.13.10). The residual **R-5.0-8 is not narrowed by a single case**, and stop condition 10b now names the journal's durability, generation, seal and archive among the things that must never be described as a barrier |
| P5.0-R2 | **Blocking** | `cutover`, `database` and `effective_at` lacked coherent semantics | Define the state matrix and an activation model that cannot take effect early | **Closed by Codex re-review 2026-08-29, and preserved by remediation R2.** Revision 3 restates the accepted matrix and effective-time model in full rather than by reference (logical schema §2.1, §2.5) so a reviewer can confirm nothing drifted. The only change in that area is removing `lease_horizon_at`, which existed solely for the withdrawn lease protocol |
| P5.0-R3 | **Important** | The handoff was corrupted and duplicated | Replaced by the remediation brief dated 2026-08-29 | Closed |
| P5.0-R4 | **Blocking — security/integrity** | The shared runtime role can update every lease and insert acknowledgements for any instance, allowing one process to forge another process's quiescence proof | Enforce process identity and row ownership below the application, or redesign so runtime-authored lease/ack rows are not trusted as activation authority | **Open. Remediation R3 submitted 2026-08-29 and claims it not closed.** R3 supplies what the re-review asked for: a dedicated **`freedomcoord`** OS user and group distinct from `discordbot`, `freedomweb`, the proposed `freedomsheet` and `foundry`, and in no group any of them holds; `pg_hba.conf` with the `peer`/`map` line above three written-out TCP rejects; one `pg_ident.conf` line, no wildcard; the role created `PASSWORD NULL`; a `sudoers` drop-in naming `foundry` only, without `NOPASSWD`, invoking one fixed root-owned wrapper that clears the environment and runs `python -I -P`; ownership and modes for every artifact; a per-vector argument; provisioning, audit, revocation, recovery and rotation; and a ten-case host-boundary evidence band. **One observed host fact drove the design**: the repository tree is group-writable by `discordbot` and `freedomweb` is in that group, so all three service processes can rewrite every module including `tools/` — hence a **root-owned deployment path outside the repository** with digest verification, and OD-65 for the condition itself. **Two checks could not be run** — enumerating `/etc/sudoers.d/` and a host-wide setuid audit — and are the Security Reviewer's. The evidence band needs **A-5.0-4**, unconfirmed. Introducing the principal is D5.0-11 / OD-64, **extended**  **Unchanged by remediation R4** apart from two added denial rows for the second `sudoers` drop-in that `freedom-journal-admin` needs (`sudo -l -U` must list **neither** `Cmnd_Alias`; an unauthorized invocation is refused), and one tightening: `freedom-sheet-writer` is removed from the runtime role, because it holds no database credential and opens no connection. **No operational evidence is claimed to have passed**, and A-5.0-4 remains unconfirmed |
| **P5.0-R5** | **Blocking — integrity/production reliability** | The dispatch journal is under volatile `/run`, while append-only support is claimed from the unrelated ext4 filesystem under `/opt`; reboot, replacement, missing/corrupt state or unsupported `chattr +a` can turn unknown dispatch history into an apparently empty unresolved set. The plan also denies dependency on completeness while activation requires `dispatch_journal_clear` | Use durable storage with an independently protected directory and explicit generation/lifecycle metadata; make missing, replaced, reset, corrupt, unsealed or unreadable state refuse evidence and activation; define privileged rotation/clearing and reboot recovery; add host-filesystem and lifecycle falsification tests; reconcile the contradictory dependency claims | **Open. Raised by Codex independent re-review of revision 4 on 2026-08-29. Remediation R4 submitted 2026-08-29 and claims it not closed.** Revision 5 moves the journal to `/var/lib/freedom-sheet-writer/journal/` on the ext4 root volume — **read from `/proc/mounts` and `df -T`, not inferred** — into a root-owned directory the writer cannot write, so it can neither unlink, rename, replace nor create there; `chattr +a` becomes a **second, independent** layer and is **probed at provisioning and at every writer start**, with a generation whose probe failed unable to be registered at all (`CHECK (append_only_verified)`). A `chattr +i` **seal**, a genesis record inside the journal and a **registered generation** in the new sixth table must all agree, so a new or reset journal is never a valid empty history, and creating one first requires sealing and archiving its predecessor. **Twenty-one conditions all fail closed** (package plan §2.13.6) — reboot, unclean shutdown, missing, empty, wrong owner/mode, unsupported flags, malformed, sequence gap, checksum failure, duplicate sequence, replaced inode, unreadable, disk full, failed `fsync`, failed outcome append and six more. A **privileged `freedom-journal-admin`**, run as root under its own `sudoers` drop-in, owns seal, rotate, repair, archive-verify and a `dispose` gated on N5.0-23, the §15.1 gate and a Data Owner approval. **The completeness contradiction is resolved by withdrawing the false statement and keeping the control** (§2.13.9), with what remains named as **R-5.0-10**. The activation trigger gains a **fifth condition** refusing stale and cross-generation evidence. Evidence is the twenty-six-case `TC-5.0-JNL` band, which **needs A-5.0-5**, unconfirmed. **D5.0-9 / OD-62 must still not be decided until Codex accepts that this control is fail-closed.**  **Independently re-reviewed 2026-08-29: still Blocking.** Revision 5 was found to contain a circular seal/genesis construction that cannot be created as specified, a permission hierarchy denying the writer the seal it was required to validate, a capability probe whose ordinary permissions masked `FS_APPEND_FL` and whose startup form was destructive against live evidence, and a `CHECK (append_only_verified)` credited with proving a host fact it cannot observe. **Remediation R5 submitted 2026-08-30 and claims it not closed.** Revision 6 answers all four: an **acyclic** order — seal body → `seal_body_digest` → derived genesis record → `genesis_record_digest` and inode → seal binding section → `seal_digest` as a leaf → registered row — with numbered creation (C0–C12) and verification (V-W, V-C, V-R) algorithms and falsification cases F-1 … F-8 (package plan §2.13.5a–§2.13.5c); a **minimum read-only** seal grant through a new system group `freedomjournal`, with `…/journal` tightened to `root:freedomjournal 0750` so *other* loses even traverse and the writer still cannot modify, replace, rotate, seal, archive or dispose of evidence (§2.13.3, §2.13.4); a **four-stage** probe in a disposable arena whose control cases C-1 … C-6 must succeed before any refusal is read as append-only, with expected `errno`s separating DAC, `EROFS`, the sandbox and `FS_APPEND_FL`, non-destructive startup checks and privileged cleanup (§2.13.2a); and the withdrawal of the Boolean check in favour of an attested, re-derivable probe report with an explicit enforces-versus-records division (§2.13.8a, logical schema §3.7.1). The fail-closed conditions grow from twenty-one to **twenty-five** (`SW-J01 … SW-J25`) and the evidence band from twenty-six to **forty-one** cases. **A-5.0-5 remains unconfirmed**, so none of the band is claimed to have been run. &nbsp; **Independently re-reviewed 2026-08-30: still Blocking.** Revision 6 was found to contain three claims stronger than the artifacts it built: Algorithm C sealed probe stages 1–3 while the schema and evidence contract said the digest covered four; F-1 claimed the writer refuses every seal-byte alteration without PostgreSQL although `BND.sealed_at` passed every V-W step; and `JNL-32` expected a `startup` record in a branch W9 refuses before W17. The R5 handoff was also corrupted and truncated. **Remediation R6 submitted 2026-08-30 and claims it not closed.** Revision 7 moves the probe's **stage 4 to provisioning**, inside one `verify-capability` invocation and before the report is built, with cases `S4-1 … S4-3`, the deployed unit's directive set hashed, and invalidation reusing the existing rotation rule — introducing **no** second artifact, digest, authority, storage location, invalidation rule, column or refusal code; withdraws `sealed_at` and the binding's own format field so the binding holds exactly the three values V-W recomputes or compares, fixes its structure with a `binding_format_version` in the chain-authenticated body, adds a complete binding-field authentication table, **splits F-1 into F-1a and F-1b**, states two attacker classes and adds **F-9 … F-12**; and replaces `JNL-32` with **`JNL-32a`** and **`JNL-32b`**. The evidence band grows to **forty-five identifiers and forty-eight cases**, falsification rows to **twelve**, the estimate to **38.2** and the stop conditions by **10h**. **Fail-closed conditions stay at twenty-five and the refusal codes stay `SW-J01 … SW-J25`; no schema object changes.** **A-5.0-5 is widened and remains unconfirmed**, so none of the band is claimed to have been run. &nbsp; **Independently re-reviewed 2026-08-30: still Blocking.** Revision 7 was found to have reproduced, in its own corrections, the class of defect it was correcting: Algorithm C step **C0** consumed a probe result step **C1** had not yet produced, so the algorithm had no executable order; **S4-2** attributed `EROFS` to the systemd sandbox without a positive control proving its exact target writable outside it; and the attacker classes claimed reach their capabilities could not construct, **F-2** being assigned class 1 while conceding it needs class 2. Implementation-plan §20 also named an obsolete brief. **Remediation R7 submitted 2026-08-30 and claims it not closed.** Revision 8 renumbers Algorithm C to **C0 … C13** with a post-probe validation step **C2** and a value-dependency table; names Stage 4's exact target `…/probe-ro/s4-2.target` and adds the positive DAC control **`S4-0`**, with `EACCES` classified `inconclusive` and a sandboxed success classified failed; and replaces the two-class model with an **eight-capability register** giving each falsification row its minimum capability, detector reach, refusing actor, exact step and code, and residual — correcting **F-2** to `K3` and **F-7** in the opposite direction, and marking not-constructible pairings with their controls. The evidence band grows to **fifty identifiers and seventy-four cases**, the falsification-row count is corrected to **thirteen**, the estimate to **39.5**, and the stop conditions by **10i**, **10j** and **10k**; new residual **R-5.0-12** records the one combination this design does **not** refuse. **Fail-closed conditions stay at twenty-five, refusal codes stay `SW-J01 … SW-J25`, V-W stays at eighteen steps and no schema object changes.** **A-5.0-5 is widened again and remains unconfirmed**, so none of the band is claimed to have been run. &nbsp; **Independently re-reviewed 2026-08-30: still Blocking.** Revision 8 was found to contain four internal inconsistencies: the supplied deployment digest was consumed at **C1** and its equality checked at **C2**, against the probe's copy of that same string, so the check was both late and vacuous; `JNL-47` and `JNL-48(d)` required one injected cleanup failure to leave two mutually exclusive residue states, and the next invocation was given both a self-cleaning and a refusing path; the capability register credited `CAP_LINUX_IMMUTABLE` **alone** with archive and journal writes that Unix DAC refuses it; and **F-7** claimed a coordinator refusal for a forged matching `/etc/machine-id` although the registered row carries the same value. **Remediation R8 submitted 2026-08-30 and claims it not closed.** Revision 9 defines `deployment_manifest_digest()` in a new §2.13.2c and moves its **computation and comparison to C0**, before C1 consumes it, keeping a consistency check and a **second computation** at C2, and replaces the universal ordering claim with invariants **I-1 … I-5**; adds a new §2.13.2b **three-state cleanup machine** in which *"no generation artifact"* is unconditional and *"no transient residue"* is conditional on cleanup success, with **one** next-invocation behaviour — refuse for operator recovery; replaces the eight-capability register with **nine independently constructible authorities** (`A1 … A9`) separating flag control from discretionary access, re-evaluating **F-2 → `A1 + A2`**, **F-4 → `A1 + A4`** and **F-5 → `A1 + A3`**; and **withdraws F-7's refusal**, recording the forged-matching host identity as residual **R-5.0-13** and routing the alternative as OD-66 **option A-2** without adopting it. The evidence band grows to **eighty-four cases across the same fifty identifiers**, §6.5 items to **nineteen**, the estimate to **40.4** and the stop conditions by **10l**, with **10b**, **10f** and **10h** extended and **10j** re-worded; new residual **R-5.0-14** records the cleanup-failure residue state. **Falsification rows stay at thirteen, fail-closed conditions stay at twenty-five, refusal codes stay `SW-J01 … SW-J25`, V-W stays at eighteen steps, security-review surfaces stay at eleven and no schema object changes.** **A-5.0-5 is widened again and remains unconfirmed**, so none of the band is claimed to have been run. &nbsp; **Independently re-reviewed 2026-08-30: still Blocking.** Revision 9's replacement authority model was found to be incorrect against the Linux contract it depends on: `FS_IOC_SETFLAGS` requires the caller's effective UID to equal the inode's owner **or** `CAP_FOWNER`, in addition to `CAP_LINUX_IMMUTABLE` for the immutable and append flags, so a non-root `CAP_LINUX_IMMUTABLE`-only process cannot clear `+i` on the root-owned archive, the stated `A1 + A3` / `A1 + A4` combinations are incomplete, and `JNL-50` case 9 is not executable; the register also declared `A1 … A6` independent while F-1a said every real A3 holder holds A2. **Remediation R9 submitted 2026-08-30 and claims it not closed.** Revision 10 states the kernel's checks in a table of their own before the register that encodes them; narrows **A1** to the `CAP_LINUX_IMMUTABLE` half; adds **A10** and **A11** for the owner authorization over the `freedomsheet`-owned journal and over the root-owned seal and archive; and re-states **eleven of the thirteen** falsification rows with corrected minimum combinations — **F-1a, F-4, F-5, F-8 … F-12 gain `A11`; F-1b gains `A10` and `A11`; F-2 and F-5 gain `A10`** — **every one of which makes the alteration harder to construct, so no refusal is strengthened and this finding is not narrowed by any of it**. It removes the independence contradiction with a **holder table**, assessing detector reach against the smallest identity that can really hold each combination and **narrowing** the bounded claim to F-2, F-3 and F-6; and it replaces the executable contract with eight identities `E1 … E8` carrying complete permitted, effective, inheritable, ambient and bounding capability sets and securebits, with `JNL-49` and `JNL-50` at **twelve cases each** and a positive control beside every negative flag case. §2.13.4's manipulation matrix grows from thirteen rows to **fifteen**; the evidence band grows to **eighty-eight cases across the same fifty identifiers**; §6.5 items to **twenty**; the estimate to **40.9**; and the stop conditions by **10m**, with **10k** extended. **Falsification rows stay at thirteen, fail-closed conditions stay at twenty-five, refusal codes stay `SW-J01 … SW-J25`, V-W stays at eighteen steps, security-review surfaces stay at eleven, no residual is added and no schema object changes.** The R8-A deployment-digest lifecycle, the R8-B cleanup state machine and the R8-D withdrawal of F-7's detector are **preserved unchanged in substance**. **A-5.0-5 is corrected rather than widened — its revision-9 capability-only case is withdrawn as not constructible — and remains unconfirmed**, so none of the band is claimed to have been run. **D5.0-9 / OD-62 must still not be decided until Codex accepts that this control is fail-closed.** Codex decides whether this route closes the finding |

**MD-4 disposition, 2026-09-23:** Peter Duscha explicitly accepts
`R-5.0-10` through `R-5.0-16` as active residual risks on their stated terms.
`R-5.0-10` and `R-5.0-11` are retained here, and `R-5.0-12` through
`R-5.0-16` are entered here. Recovery rehearsals for `R-5.0-11`, `R-5.0-14`
and `R-5.0-16` remain mandatory evidence. Other rows below are not entered in
the register yet. A register row for a package that has not started would assert the readiness the
5.0 readiness package is asking for. These are the rows to enter **when Peter
records a readiness decision**; the authoritative statements are in
[`../review/phase-5-0-package-plan.md`](../review/phase-5-0-package-plan.md) §7.

| Proposed | Type | Statement | Owner | Trigger / mitigation |
|---|---|---|---|---|
| R-5.0-1 | Risk | The authority fence is added to a live estate — a database trigger on every authoritative write and a new writer process — and a defect in it refuses a healthy process | Technical Lead | Every refusal is fail-*closed* by design, so the failure mode is a bounded refusal rather than a silent wrong authority. Exercised against every process before deployment; the operations document names the recovery; design **F-6 (stop the whole bot)** is the declared fallback if the separately terminable writer is found defective |
| R-5.0-2 | Risk | **Superseded a second time, by design remediation R2.** Revision 1's statement was the substance of P5.0-R1; revision 2 replaced it with a lease, which did not close the finding. Revision 3 replaces the lease with a database-enforced write fence and a lifecycle boundary: the correctness risk is closed for PostgreSQL writes by construction, and converted into a bounded availability cost for Sheet writes | Operations Owner | The authority-fence trigger evaluated inside the writing transaction; the separately terminable Sheet writer; the revoked Google write access. The availability consequence is decision D5.0-9 / OD-62 as reframed, and risk R-5.0-6 |
| R-5.0-3 | Risk | A database restore silently returns a migration unit to an earlier authority, **or the journal-generation register to a pre-rotation state** | Operations Owner | The operations document requires `python -m tools.migration_authority status` as the first post-restore step, before any service is started, and a comparison of the restored control-plane version against the change log. Quiescence evidence restored from a dump is bound to its revision and is refused as stale by the N5.0-16 age test, so no restored evidence can fence a later activation. **Extended by remediation R4:** the procedure additionally compares the restored head generation against the seal on disk and runs `archive-verify`, refusing if they disagree — the journal file survives a database restore, and that asymmetry is a control rather than a problem |
| R-5.0-4 | Risk | **Re-owned by package 5.1 under OD-55.** Package 5.0 creates no comparison-telemetry table, so it cannot carry this risk. The statement — *shadow comparison telemetry grows without bound during a long verification window* — moves with the implementation | Product Owner | Carried into the telemetry contract Package 5.0 retains (plan §11) as a binding constraint on 5.1's design: value-free fixed-width rows with no column able to hold a value; a schema-owner retention sweep at N5.0-7 (30 days); no runtime `DELETE`; a monitored row count |
| **R-5.0-5** | Risk | **Restated and narrowed by remediation R2.** The paused-process case is removed: a `SIGSTOP`ped writer is killed by the `SIGKILL` escalation and cannot resume, and a resumed database writer is refused by the fence trigger inside its own transaction. What remains is that `host_scan_clear` is a *point-in-time* observation, so a writer started between the scan and the activation is not observed | Technical Lead | The coordinator re-observes immediately before activating, in the same invocation; the N5.0-16 staleness test refuses evidence older than 15 minutes; and the revoked Google write access refuses such a writer independently of any host observation. Stated as a residual rather than described as impossible |
| **R-5.0-6** | Risk | **Restated by remediation R2.** The revision-2 statement — *Freedom-bot mutations refuse during a PostgreSQL outage* — is **withdrawn with the lease**; the bot's legacy mutation path takes no runtime database dependency at all, only a startup authority read. It is replaced by: Sheet mutations are unavailable for the length of each fence window, and remain unavailable if the writer fails to restart | Product Owner | Bounded by the fence window; reads, `/info` and every non-mutating command unaffected; a typed message rather than a crash; `/healthz` `migration_sheet_writer` reports it. **Accepted or rejected by decision D5.0-9 / OD-62 as reframed**, not by the implementer |
| **R-5.0-7** | Risk | A Drive write permission revoked for a cutover and not restored afterwards is a silent Sheet-mutation outage for every migration unit still at `legacy` | Operations Owner | The restore is the cutover checklist's last step and a named line item in the WP-9 rehearsal; `/healthz` `migration_sheet_writer` reports a writer whose writes are being refused at the external boundary; the operations document states the one-line restore. Detected, not prevented |
| **R-5.0-8** | Risk | **New, raised by remediation R3, and it is a residual rather than a mitigation gap.** A `spreadsheets.values.batchUpdate` request Google accepted before the fence, whose response never reached the writer, and which Google applies after the final import has read the Sheet, silently diverges the frozen legacy store from the imported snapshot. **No control in the published Google API prevents it or proves it absent**, and package plan §2.10.1 records the thirteen-candidate search that establishes this | **Acceptance Authority** | Made rare by draining the writer before killing it; enumerated by the dispatch journal when the writer worked correctly; **refuses the cutover while outstanding** (N5.0-20 = zero); cannot reach PostgreSQL, because after activation the unit is database-authoritative and no Sheet-derived write path exists; detected by two post-import re-reads; disclosed before any rollback replay. **Accepted or rejected by D5.0-9 / OD-62 as reframed a third time.** It is not owned by the Technical Lead, because it is not a thing implementation can close |
| **R-5.0-9** | Risk | **New, raised by remediation R3.** The coordinator's host boundary depends on host state — group memberships, `sudoers` rules, `pg_hba` ordering, the `pg_ident` map, file modes — that can drift after it is established, silently and outside this repository | Operations Owner | The ten-case host-boundary matrix is re-run after any PostgreSQL configuration change, any `sudoers` change and any deployment; the `diagnostics` subcommand re-checks on every invocation that no `sys.path` entry is writable by a service identity; the operations document lists the host facts to re-verify. **Extended by remediation R4** to the journal hierarchy's owners, modes and filesystem attributes, which drift the same way and are outside this repository too. **Detected on re-run, not prevented**. **Extended again by remediation R5** to the new `freedomjournal` group and its membership, to the seal's `0440` mode and `…/journal`'s tightened `0750`, and to the disposable probe arena, which must not exist on a production host between provisioning runs; the host-boundary matrix re-run therefore checks group membership and the absence of the arena as well **Extended by remediation R6** to the deployed `freedom-sheet-writer.service` directive set, which the probe's stage 4 records at provisioning and which drifts whenever the unit is edited. **Detected on re-run, not prevented** |
| **R-5.0-10** | Risk | **New, raised by remediation R4, and it is the honest limit of the dispatch journal.** A writer whose **dispatch path itself** has been replaced can call `values.batchUpdate` without writing a journal record, so the unresolved set reads empty when it is not and a refusal that should have occurred does not occur | Technical Lead, with the Security Reviewer | **Not detected by the journal**, and package plan §2.13.9 says so where a reader meets it rather than in a footnote. What bounds it is everything the writer does *not* author: the process is terminated, its cgroup is empty, a host scan found nothing, and Google refuses its access. The unit hardening — `NoNewPrivileges=true`, an empty `CapabilityBoundingSet=`, `ProtectSystem=strict` — and the deployment digest carried in the registered generation raise the cost of reaching that state. **A writer compromised this deeply could have written the Sheet arbitrarily long before the fence**, which is a condition no fence was ever going to repair |
| **R-5.0-11** | Risk | **New, raised by remediation R4, and it is the price of fail-closed.** The journal filesystem falls below N5.0-21, or an `fsync` fails, or any of package plan §2.13.6's twenty-one conditions holds — and the Sheet writer refuses **every** mutation until an operator acts, for every migration unit still at `legacy` | Operations Owner | The refusal is typed, named (`SW-J01 … SW-J21`) and carries no exception text, path or `errno`; the Freedom bot stays online and reads, `/info` and every non-mutating command are unaffected; `/healthz` `migration_sheet_writer` reports the writer unreachable and the new `migration_journal_generation` reports an unregistered or superseded generation; the operations document names the recovery for each condition. **A deliberate trade — a bounded outage instead of an unrecorded external write — accepted or rejected by decision D5.0-13 / OD-66**. **Extended by remediation R5 to twenty-five conditions** (`SW-J01 … SW-J25`): J-22 refuses a deployment digest that does not match the one recorded in the seal, J-23 refuses a host identity that does not match, J-24 refuses a seal whose structure is malformed or whose genesis record is not derivable from the seal body, and J-25 refuses a generation whose probe report is missing, `inconclusive` or of an unrecognised version. The outage surface grows with them, and the refusals stay typed, unexplained and non-Sheet-mutating |
| **R-5.0-12** | Risk | An actor with complete on-disk authority and PostgreSQL superuser authority can rewrite the seal, record 0 and registered digests into mutual agreement; no check inside those stores refuses it | Acceptance Authority, with Security Reviewer | **Accepted by MD-4 on 2026-09-23.** External `sudo` output, journald, the `audit_events` chain and offline backups remain the detection and recovery controls |
| **R-5.0-13** | Risk | Host root can restore the journal tree and forge the recorded machine identity so the internal comparisons agree | Acceptance Authority, with Security Reviewer | **Accepted by MD-4 and MD-6; JNL-40(b) is not mandatory for P5.0-R5 closure.** External system, deployment, audit and backup evidence remains required; option A-2 is not adopted |
| **R-5.0-14** | Risk | Failed privileged cleanup can leave writer-writable transient residue and block generation creation until an operator acts | Operations Owner | **Accepted by MD-4.** Explicit recovery must be rehearsed and evidenced; automatic cleanup remains prohibited |
| **R-5.0-15** | Risk | Host root combined with the Platform Administrator path can rewrite provenance, approve and register its chosen revision; no check in this design refuses that combined authority | Acceptance Authority | **Accepted by MD-4.** External logs, audit evidence, backups and human review-reference checks remain required; signing option A-3 is not adopted |
| **R-5.0-16** | Risk | Missing approval or provenance, or deployed-tree drift, blocks generation creation and Sheet mutations until approval, installation, deployment and rotation recovery completes | Operations Owner | **Accepted by MD-4.** The recovery path must be rehearsed and evidenced at feasibility and production gates |
| A-5.0-1 | Assumption | The legacy Freedom bot and Sheet path remain available and undegraded **outside the bounded fence windows**, throughout 5.0 readiness, implementation and every later verification window | Product Owner | A-04 restated at package scope. The fence-window qualification is what decision D5.0-9 / OD-62 is being asked to accept. Void the moment plan §15.1's final Sheet retirement gate closes, at which point the `database → legacy` transition row must be removed by migration |
| A-5.0-2 | Assumption | No staging deployment is required for package 5.0 | Operations Owner | Holds while the package deploys nothing. Its database evidence is producible against the disposable `freedom_test` database; its **termination evidence needs real processes** and is producible with a harness writer under a transient systemd unit on this host, never against the production writer. **Forward dependency flagged:** packages 5.1 and 5.2 will need a staging-class environment, and staging is currently a procedure (`infra/staging/`) rather than a standing service |
| D-5.0-1 | Dependency | A named Security Reviewer, **and their delivered recommendation** | Delivery Lead | **Reviewer named 2026-08-31 (OD-61 closed):** Peter Duscha named **Codex**, which also holds the Independent Reviewer and independent logical-schema reviewer roles; the implementer did not nominate it. **The dependency is not discharged.** What blocks readiness is now the **review**, not the vacancy: the package plan §9.2 pass of 3.5–4.5 reviewer-days over eleven surfaces has not run, and the revision-11 design re-review is not that pass. **Scope grew at R2, R3 and again at R4:** it now covers a new database principal and `pg_hba`/`pg_ident` ordering, **two new operating-system identities**, **two `sudoers` drop-ins one of which runs as root**, **a root-owned deployment path with digest verification**, **a root-owned durable evidence hierarchy with filesystem attributes and an evidence-disposal path**, hardening on two live units, **the pre-existing group-writable repository tree**, the relocation of the Google service-account credential out of the Freedom bot, and a procedure that changes a production Drive permission at each cutover. **Three checks the implementer could not run are theirs**: enumerating `/etc/sudoers.d/`, a host-wide setuid audit, and verifying that `chattr +a` is honoured at the journal path. **Scope grew again at R5** to an **eleven-element** surface: the new `freedomjournal` system group and the minimum read-only seal grant, the disposable probe arena and its privileged cleanup, the `setpriv` identity drop in the provisioning probe, and the acyclic digest construction itself, which a security reviewer should attack rather than accept. **A fourth check the implementer could not run is theirs**: confirming that the `0750`/`0440` grant gives `freedomsheet` read access to the seal and gives `discordbot` and `freedomweb` none. Estimate raised to **2.5–3.5 reviewer-days** **Extended at R6:** the scope gains a **transient `systemd-run` unit started as root at provisioning**, which executes the writer's identity under directives read from the deployed unit file, with one substitution the tool performs itself. The estimate is **unchanged at 2.5–3.5 reviewer-days**, and one reviewer question is added |
| **D-5.0-2** | Dependency | **Extended again by remediation R4.** Rulings on D5.0-9 / OD-62 (**reframed a third time**: no barrier exists, so what is accepted in place of one — a **risk acceptance**), D5.0-10 / OD-63 (**extended to nine numeric controls**, three of them new for the journal's storage lifecycle), D5.0-11 / OD-64 (**extended** to the database principal **and** its dedicated OS identity and host privilege boundary) **D5.0-12 / OD-65** (the `freedomsheet` identity and Google-credential relocation, hardening on the live `freedom-bot` unit, and the group-writable repository tree) and **D5.0-13 / OD-66** (**new**: the dispatch journal's durable storage, its sealed and registered generation, the privileged `freedom-journal-admin` lifecycle, and the retention and disposal rule that is the Data Owner's) | Delivery Lead | Unresolved. D5.0-9 blocks WP-4b, can change it wholesale, and now belongs to the **Acceptance Authority** rather than only to the Product Owner; D5.0-10 blocks WP-1's completion; D5.0-11 blocks WP-2 and WP-14; D5.0-12 blocks WP-4b and WP-14; **D5.0-13 blocks WP-4b and WP-15**. **Extended again by remediation R5**: D5.0-12 / OD-65 now also carries the **third system group** `freedomjournal`, and D5.0-13 / OD-66's option A is re-stated with revision 6's acyclic construction, seal readability, probe procedure and withdrawn database check. **No new decision number is raised**; D5.0-9 and D5.0-13 remain unruled and revision 6 must not be read as deciding them **Extended at R6:** D5.0-13 / OD-66 **option A's content is amended again** — where the probe's sandbox stage runs, and what the seal's binding section contains. Options B, C and D, the owners, the authorities and retention rule N5.0-23 are unchanged; **no new decision number is raised and nothing is decided** |
| **A-5.0-3** | Assumption | A **disposable** Google spreadsheet and a **disposable** service account are available for WP-13's propagation measurement | Delivery Lead | **Unconfirmed.** No production spreadsheet, credential or access may be used. **Less consequential after remediation R3**: N5.0-18 is now an operational margin rather than a control, and WP-13 is demoted to informing it. Its absence no longer changes D5.0-9's option set on its own |
| **A-5.0-4** | Assumption | **New, raised by remediation R3.** A **disposable** operating-system identity, a `pg_hba.conf`/`pg_ident.conf` entry and a configuration reload can be made on the disposable cluster, so the host-boundary denial matrix can be produced | Operations Owner | **Unconfirmed, and it is a host change.** The attacking side of the matrix can use the existing service identities read-only; the coordinator side cannot be simulated. **Without it the entire R3-B evidence plan is unproducible and P5.0-R4 cannot close on evidence.** Stated at readiness rather than discovered at WP-14 |
| **A-5.0-5** | Assumption | **New, raised by remediation R4.** A root-owned durable directory hierarchy can be created under `/var/lib/freedom-sheet-writer`, `chattr +a` can be **verified** there under the service uid, an `fsync` failure can be injected, and — if the Operations Owner authorizes it — a supervised host reboot can be taken between a dispatch and its outcome | Operations Owner | **Unconfirmed, and it is a host change. Corrected by remediation R9-A and R9-C, and not carried forward in its revision-9 form.** Setting or clearing a filesystem attribute needs **two** things — `CAP_LINUX_IMMUTABLE` **and** an effective UID equal to the inode's owner or `CAP_FOWNER` — neither of which the remediation account holds and neither of which this remediation was authorized to use. **Revision 9's assumption that a `setpriv --ambient-caps=+linux_immutable` process could clear `+i` on a root-owned archive file is withdrawn as not constructible**: the ioctl returns `EPERM`, and the shorthand does not build the capability set it names, because an ambient capability must also be permitted and inheritable and a `setuid` away from 0 clears the permitted set without `SECBIT_KEEP_CAPS`/`SECBIT_NO_SETUID_FIXUP`. **What is assumed instead — widened again by remediation R10-A and R10-B, revision 10's form being withdrawn in its turn** — is package-plan §2.13.5c's eight executable identities `E1 … E8`: a disposable uid `fbprobe`; **`capsh(1)` present on the target host** (`libcap2-bin`; on this host `/usr/sbin/capsh`, `root:root 0755`, no file capabilities) able to build the capability masks `0x0`, `0x200`, `0x206`, `0x208` and `0x20E` by the seven-step construction; a **launching process whose bounding set already contains every capability those masks need**, because **no tool can add a capability to a bounding set**; and `/proc/self/status` **plus `prctl(PR_GET_SECUREBITS)`** readable inside each dropped process so every case can assert its identity and securebits before it runs. **Revision 10's `setpriv --securebits=+keep_caps,…` recipes are withdrawn as not executable**: util-linux 2.39.3 documents that securebit as not allowed, `--bounding-set=+…` requests an addition the kernel forbids, E8 dropped no bounding set and E7 declared no inheritable or ambient mask. **Package-plan §8.1 H-6 records a non-mutating read of that tool contract on 2026-08-31; it is not a confirmation of this assumption.** A disposable path on the same filesystem suffices for the evidence; the production hierarchy is provisioned at deployment. **Without it the capability probe cannot run, no generation can be registered — a host-side refusal by `init-generation`, not a database constraint, revision 5's `CHECK (append_only_verified)` having been withdrawn with the column at R5-D — and the whole `TC-5.0-JNL` band is unproducible, so P5.0-R5 cannot close on evidence.** The reboot bullet may end as a check not run, and the plan says so rather than assuming it. **Widened by remediation R6:** stage 4 of the probe now runs at **provisioning**, so it additionally needs a **transient `systemd-run` unit startable as root** and a **deployed `freedom-sheet-writer.service`** to read hardening directives from. **None of that was run**: no `systemd-run`, no `chattr`, no `setpriv` and no arena. Without it `verify-capability` cannot produce a passing four-stage report, so `init-generation` refuses to create a generation at all — a host-side refusal, not a database constraint. **Restated by remediation R5.** The probe now needs a **disposable arena** — a directory the tested identity can ordinarily write, on the journal filesystem — and the ability to drop to that identity with `setpriv`, so that each expected refusal is attributable to `FS_APPEND_FL` rather than to discretionary permissions. **The `CHECK (append_only_verified)` clause named above is withdrawn**: a generation whose probe failed or was `inconclusive` is refused **host-side** by `init-generation` (`SW-J25`), not by a database constraint. **Widened again by remediation R7:** a **second transient directory `…/probe-ro`** on the same mount, with the `S4-0` control executed in it under the writer's uid **outside any unit**. **Widened again by remediation R8:** a **non-root ambient `CAP_LINUX_IMMUTABLE` capability set** (`setpriv --ambient-caps=+linux_immutable`), so `JNL-49` and `JNL-50`'s new cases run under a set that really holds only what they claim rather than being simulated as root; and a **disposable second host, or a disposable host whose `/etc/machine-id` may be rewritten**, for `JNL-40`'s forged-matching case. The assumption is otherwise unchanged and still **unconfirmed**, so the `TC-5.0-JNL` band remains unproducible and P5.0-R5 cannot close on evidence |

### Existing rows this readiness package touches, without closing any

- **R-P4-4** — *a posted ledger transaction is durable only as far as process
  memory* — remains **Active**. The 5.0 design recommends that the ledger table
  stay with package **5.2** (decision D5.0-5, closing OD-48's "5.0 or 5.2"
  ambiguity), because a 5.0 ledger table would have to persist a free-text
  account name with no foreign key to `characters`, 5.0 not being permitted to
  decide the account vocabulary. Package 5.0 **narrows** the risk in exactly one
  way and claims nothing further: it makes it impossible to deploy a process that
  treats the in-memory ledger as production authority, because a unit cannot
  reach `cutover` or `database` authority while its owning package has registered
  no durable repository, and the admission fence refuses every database-path
  mutation of a `legacy` unit. **OD-58 closed OD-48's "5.0 or 5.2" ambiguity in
  favour of 5.2.**
- **R-03** — *Phase 5 scope cannot fit its roadmap range* — its 5.0 input is
  **revised by remediation R1**: O 10.0 / ML 20.0 / P 35.0 implementer-days,
  PERT **20.8** (was 14.3), plus 6.0 days of remediation allowance and 2.5 of
  contingency, with review, security review, rehearsal and maintainer decision
  time outside those figures. The movement decomposes as −1.1 for removing the
  telemetry work package under OD-55 and +7.6 for request-time fencing under
  P5.0-R1.
- **R-06** — *cutover or rollback loses live-bot availability* — package 5.0 is
  its principal mitigation, and remains Active until that mitigation exists.
  Remediation R1 also makes 5.0 a **contributor** to it, through R-5.0-6: the
  fence that protects the bot from a dual-authority write is the same mechanism
  that refuses its mutations during a database outage. Decision D5.0-9 is where
  that trade is accepted or rejected.
- **A-02** — the disposable PostgreSQL environment and an assumable restricted
  runtime role — **confirmed still holding** on 2026-08-29: `freedom_test` at
  PostgreSQL 16.15 over the Unix-domain socket, 31 tables at head `0013`, and
  role `freedom_runtime_test` present and unable to log in.
- **A-04** — the legacy Sheet-backed bot remains the rollback implementation
  until approved cutover — **confirmed, and package 5.0 depends on it
  absolutely**: the `cutover → legacy` and `database → legacy` transitions exist
  only while it does.
- **I-03** — package-specific implementer/reviewer capacity is not yet recorded —
  remains **Open**, and is the register form of decision D5.0-8.

## Phase 4 independent-review findings — 2026-08-29

### Gate closure — 2026-08-29

Codex's second independent re-review returned no Blocking or Important
findings. Peter Duscha approved the Phase 4 dependency-direction and domain-
correctness gate. **P4-R1, P4-R2, P4-R3, P4-R4, P4-R5 and D-04 are Closed.**
Phase 5 package planning is released, while every package-specific readiness,
review, migration and cutover control remains in force. R-P4-1 is Closed by the
gate decision; R-P4-2 through R-P4-4 remain active and owned by their stated
later packages. Gate acceptance does not convert the in-memory reference ledger
into production authority.

### Remediation R2 submission — delivered 2026-08-29

Both re-review findings are **remediated and resubmitted**. **Neither is
closed.** Claude does not close P4-R4, P4-R5 or D-04 and does not decide the
gate; Codex re-reviews and Peter Duscha records the decision. Evidence:
`../review/phase-4-submission.md`, *Remediation R2*; package plan §20; change
log C-P4-K.

| ID | State after remediation | What changed | Evidence |
|---|---|---|---|
| P4-R4 | **Remediated — awaiting re-review** (was Open — Blocking) | `compensate()` resolves the caller's current authority through the same ports `post()` uses **before** it opens a unit of work or reads the ledger, so an unauthorized caller receives one identical `not_authorized` refusal whether the transaction exists or not — and the ledger is never consulted, so there is no answer to leak. That resolution happens **once**: the resolved attribution is carried through a new private `_post_resolved` path into the digest, the receipt, the audit row and the posting, rather than the operation re-entering `post()` and asking a port a second time. The public surface is still `post` and `compensate`, neither of which accepts an attribution. `post()`'s behaviour is unchanged | 20 new tests, 9 of them against real PostgreSQL. The existence-oracle regression is parametrized over six caller shapes — ordinary member, revoked member, unknown principal, revoked principal, deactivated principal, wrong-scope principal — and asserts both that the two refusals are identical and that no unit of work was opened. Falsifications R2-1 (12 failures), R2-1a (6 failures) and R2-2 (3 failures) |
| P4-R5 | **Remediated — awaiting re-review** (was Open — Important) | `post()` refuses a mismatch between `CommandEnvelope.correlation_id` and `LedgerTransaction.correlation_id` with the new declared code `correlation_mismatch`, before the expected-version precondition, before the digest and before the unit-of-work factory is called. An accepted command records one id in ledger history, the stored receipt and the audit row, the fenced value being passed into execution rather than re-read. Correlation is **not** added to the command-defining digest: a true retry may regenerate it on both halves and is still answered from the stored receipt | 19 new tests, 4 of them against real PostgreSQL, including the mismatch-leaves-everything-empty regression and a direct digest-equality assertion. Falsifications R2-3 (4 failures) and R2-4 (6 failures) |

**No new risk is raised and none is closed.** R-P4-4 is unchanged: the in-memory
ledger is still not durable under OD-48, and package 5.0 or 5.2 still owes the
table and the single database transaction.

**One environment observation, reported rather than resolved.** The re-review's
bot-suite failure (2887 passed, 2 skipped, 1 failed — the backup/restore drill
finding missing disposable-test-database grants) **could not be reproduced**.
The drill passes here with 35 tests and the suite reports zero skips, both
before and after the R2 changes. No grant, role or schema was altered by this
remediation. A re-reviewer who sees the failure again should apply
`infra/postgresql/runtime-grants.sql.tmpl` to their own `freedom_test` database
and rerun the drill before reading the figure as a Phase 4 result.

### Remediation R1 independent re-review

P4-R1 and P4-R2 are materially remediated, and P4-R3's requested digest change
is present. The gate remains **deferred**, D-04 remains Open and Phase 5 remains
blocked for these further findings:

| ID | Class | Finding | Owner | Closure evidence | State |
|---|---|---|---|---|---|
| P4-R4 | Blocking — authorization boundary | `LedgerCommandService.compensate()` reads a transaction and discloses a distinguishable missing result before current authority is resolved | Technical Lead | Resolve authority before lookup, reuse one resolved attribution through posting without a second authorization race, and prove unauthorized unknown/existing probes produce the same refusal and no posting, receipt or audit | **Open — Blocking** |
| P4-R5 | Important — audit/correlation correctness | Envelope and ledger transaction may carry different correlation IDs; receipt/audit use one while ledger history retains the other | Technical Lead | Enforce one attempt correlation ID before opening a unit of work; mismatch is a typed no-effect refusal while true-retry behavior remains unchanged | **Open — Important** |

No maintainer decision is required; both are implementation defects inside the
approved Phase 4 scope. See the latest disposition in
`../review/phase-4-submission.md` and change log C-P4-J.

### Historical original review findings

The following table records the first review state and is superseded by the
re-review disposition above. Codex completed the required independent
implementation review. The gate was
**deferred**, D-04 remains Open, and Phase 5 remains blocked. The focused suite
passed 326 tests in 2.81 seconds, but did not exercise the counterexamples.

| ID | Class | Finding | Owner | Closure evidence | State |
|---|---|---|---|---|---|
| P4-R1 | Blocking issue — atomicity / production reliability | `LedgerUnitOfWork.commit()` releases the ledger lock after publishing and before the durable commit. If another caller appends during that window, `retract(N)` can remove the newer caller's transaction rather than the failed caller's transaction, leaving corrupted history and versions | Technical Lead | Replace the unsafe cross-store transaction shape or make rollback target the exact unpublished/published identities without exposing intermediate state; add a deterministic two-caller regression in which caller A publishes, caller B commits, then A's durable commit fails, proving B remains, A does not, versions/balances are correct, and no receipt/audit lies | **Open — Blocking** |
| P4-R2 | Blocking issue — authorization | A nonblank `principal_id` is treated as sufficient service-principal authority; the application service does not resolve a current scoped credential/capability | Technical Lead / Security Reviewer | Add an application-owned service-principal authorization port or reuse an accepted scoped authority mechanism; verify current identity and ledger-command scope at execution; test unknown, revoked, wrong-scope and valid principals through direct service calls, with no mutation/audit/receipt on refusal | **Open — Blocking** |
| P4-R3 | Important issue — idempotency / audit correctness | The ledger request digest omits authoritative command facts including `occurred_at` and caller identity, allowing materially different history or cross-principal reuse to be answered as an identical retry | Technical Lead | Define and document attempt-only versus command-defining fields; bind occurrence time and authenticated caller identity (and every other authoritative input) into the canonical digest, or normalize them before hashing under an explicitly justified contract; test conflicting time and caller reuse plus stable true retries | **Open — Important** |

R-P4-4's prior statement that retraction prevents a receipt/effect mismatch is
not accepted as a mitigation while P4-R1 is open. OD-48 remains unchanged: the
remediation must not add a physical ledger table in Phase 4 without a new
maintainer decision and the mandatory independently reviewed schema artifact.

### Historical Remediation R1 submission — delivered 2026-08-29

All three findings are **remediated and resubmitted**. **None is closed.**
Claude does not close P4-R1, P4-R2, P4-R3 or D-04 and does not decide the gate;
Codex re-reviews and Peter Duscha records the decision. Evidence:
`../review/phase-4-submission.md`, *Remediation R1*; change log C-P4-I.

| ID | State after remediation | What changed | Evidence |
|---|---|---|---|
| P4-R1 | **Remediated — awaiting re-review** (was Open — Blocking) | The publish-before-durable-commit shape is replaced. `LedgerBook.committing` holds the book's writer lock across the durable commit and appends only after it returns; `publish` and `retract` are removed, so rollback of a published posting is not an operation the class can be asked to perform. The adapter no longer claims cross-store atomicity, and the residual crash window is stated | Six new concurrency tests, event-synchronized with no sleeps, including the handover's mandatory two-caller regression against fakes and against real PostgreSQL. Falsification R1-1 fails deterministically on the visibility assertion |
| P4-R2 | **Remediated — awaiting re-review** (was Open — Blocking) | The rule that every non-human caller is authorized is removed. A consumer-owned `LedgerPrincipalPort` resolves the principal at execution; unknown, revoked, deactivated and out-of-scope principals are refused with one undifferentiated message; audit attributes the resolved principal, never request text. `ServicePrincipalScope` and the Foundry credential vocabulary are deliberately untouched | 21 tests through direct service calls, four of them against real PostgreSQL. Falsifications R1-2 (16 failures) and R1-3 (14 failures) |
| P4-R3 | **Remediated — awaiting re-review** (was Open — Important) | Command-defining and attempt-metadata fields are documented and enforced. The digest binds the authoritative occurrence time, the verified caller identity and the caller's surface, and is computed by a typed, length-delimited, schema-versioned encoding replacing delimiter joining. `correlation_id` is ruled attempt metadata, explicitly | 20 identity tests plus four canonicalization tests. Falsifications R1-4 and R1-5 |

**R-P4-4 is narrowed but not closed.** The in-memory ledger is still not durable
(OD-48), and package 5.0 or 5.2 still owes the table and the single database
transaction. What changed is that the adapter no longer claims a guarantee it
could not enforce.

## Phase 3 gate decision — 2026-08-28

Peter Duscha accepted the final accountable gate statement. **A-05 is Closed**
by the Security Reviewer's final break-glass-readiness confirmation. **A-06 and
I-06 are Closed** by the Technical Lead and Operations Owner's acceptance of the
PostgreSQL queue/limiter and staging evidence. **R-23 remains an active accepted
residual** under the Product Owner's disposition; screen-reader traversal is
Not Run for Phase 3 and is not treated as passed. The Acceptance Authority
approved the Phase 3 authentication, authorization and web-security gate and
authorized Phase 4 implementation. See change-log C-P3.5-AK and the superseding
decision in `docs/review/phase-3-gate-disposition-2026-08-25.md`.

## Historical close of the 2026-08-26 supervised sessions

The open-state statements in this section are a dated operational record. They
are superseded for current status by the 2026-08-28 gate decision above.

**I-06 — Open, and substantially advanced.** Of its ten closure criteria, the
staging build now carries: deployed startup refusals at **14 of 15** (S-13 is
test-enforced and not observable on a live host), **TC-LIM-02 exact**,
**TC-SEC-07's browser half in part**, **TC-OPS-01, -02, -03 partly, -04 partly and
-05 all executed**, **worker recovery observed under a lost worker**, and
**backup/restore/rollback evidence on staging**. **Not closable yet:** TC-OPS-03's
end-to-end flow was exercised only with synthetic input, TC-PERF-01/02 still owe
**D-m's real n = 1 apply**, TC-UI-08 covers one device width, and the Operations
Owner and reviewers have not accepted it.

**A-06 — Open, with most of its evidence now in hand.** Preview and apply
durations, worker peak RSS against N-47, portal responsiveness and lease
heartbeat/commit-fence behaviour were all measured against bounds **stated before
the run** (§11.3; decision **D-s** for the two that had no accepted figure).
Recovery after interruption produced **exactly one durable effect**. **Not
closable yet:** criterion 1 requires representative *staging* conditions, and
every input so far has been synthetic — real-shaped, but parsing roughly **3×
faster** than real Actor data.

**A-05 — Open on criterion 10 alone.** Criteria 1, 2, 2a, 3, **4a**, **4b**, 5, 6,
7, 8 and 9 are Met. Criterion 10, the Security Reviewer's break-glass readiness
confirmation, comes last by its own terms. Criterion **4c** is owed at the
deployment gate as defence in depth.

**R-23 — active accepted residual, marginally improved.** The skip link now
Passes, reduced-motion support is verified in a real engine, and the exact Chrome
build is recorded. Screen-reader traversal remains **permanently Not Run for
Phase 3** under D-f, real-engine contrast and HTMX-enhanced paths remain Not Run,
and TC-UI-08 covers one device width.

**Findings raised across the day and not yet dispositioned by a reviewer:**
**N-20** (Blocking, remediated and re-verified), **N-22** (Important — HSTS
required by the accepted contract and configured nowhere), **N-13** (fixed and
deployed), **N-21** (an outage caused by this package's own procedure, corrected),
plus N-14, N-16, N-17, N-18, N-19, N-23 and N-24. **N-15 was withdrawn** on
evidence that contradicted it.

**Phase 4 remains unauthorized.** EX-11 and EX-12 are still owed.

## P3.5 authority granted, and two criteria repaired — 2026-08-26

- **SG-2 granted, and an SG-3 extension granted**, by Peter Duscha as Operations
  Owner, together with specific authorization to deploy the reviewed **N-7** fix
  by service restart and re-run **SP-12**, and to run **SP-27** as written
  (change-log **C-P3.5-V**, execution plan §0.2 rows P-3 and P-4). **A grant is
  not evidence:** no procedure has yet been executed and **no RAID disposition
  moves on this entry.**
- **D-o confirmed** by Peter Duscha as Security Reviewer. S-15's pre-exposure
  observation stays inside **A-05** as criterion 4b, discharged by SP-27; the
  deployment-gate check is 4c, defence in depth only.
- **A-05 criterion 4a was not executable as written (finding N-10)** and is
  repaired by decision **D-p**: the threshold observation is taken under the
  `development` marker on a disposable database, because each environment is
  bound to exactly one database name and a staging-marked process would have to
  target the deployed staging database holding the protected account's two
  **real** credentials. S-15 branches on `is_production` alone, so the observed
  branch is identical. **A-05 remains Open**; criteria 4a, 4b and 10 are
  outstanding and now all executable.
- **I-06's SP-10 had no instrument (finding N-11)** and is repaired by decision
  **D-q**: `backup-restore-drill.sh` accepts `freedom_staging` behind two
  independent, non-default signals, with production keeping no override. **I-06
  remains Open**; every procedure it needs is now unblocked but unexecuted.
- **A-05 reduced to a single outstanding criterion, 2026-08-26.** Criterion **4a**
  was met as M-1b under decision D-p, and criterion **4b** as SP-27 — S-15's
  production-class refusal observed **before exposure**, with no listener, inside
  a verified per-process network namespace on a disposable database proved empty
  first, and shown to pass at two credentials so the refusal means the N-13 floor
  rather than production-marking. **Only criterion 10 remains**, and by its own
  terms it comes last. **A-05 stays Open.** Criterion 4c is owed at the deployment
  gate as defence in depth.
- **N-21 raised 2026-08-26 — this package's own procedure caused an
  operator-visible outage.** SP-27's egress step reused SP-25's uid-scoped
  firewall rule under `foundry`, the maintainer login, rather than the dedicated
  `freedomweb` service account it was proven against, and took unrelated services
  off TCP/443 until the Operations Owner diagnosed and removed it. No platform
  service and no data was affected. **Corrected**: replaced by per-process network
  namespace isolation, verified in use.
- **N-20 raised 2026-08-26 — Blocking, against the recovery procedure.** SP-10's
  restore on staging returned every row and every guard **and silently dropped the
  runtime role's privileges**, leaving both units crash-looping until
  `runtime-grants.sql.tmpl` was re-applied. The drill's row-inventory comparison
  cannot see a missing GRANT, so it reported `Restore verified`. **I-06 criterion
  8 (backup/restore/rollback evidence for staging) is satisfied as a procedure but
  the procedure itself is defective**, and the deployment gate's "restore-tested"
  input (§7 item 4, plan §14.3) is not met until the drill re-applies and asserts
  the grants. **Remediated the same day** as options 2+3 with the Operations Owner's approval:
  the drill records the privilege state before the destroy, re-applies the runtime
  grants template afterwards, and fails when a privilege present before is missing
  after. Both directions tested. **Verified on `freedom_staging` the same day**: the same
  drill that previously left both services crash-looping (`NRestarts` 35/36) now
  restores all 99 runtime privilege rows automatically, at the restricted posture
  with `TRUNCATE` still denied, and both services start clean (`NRestarts=0`).
  **N-20's remediation is proved on the target where the defect was reachable.**
- **Six staging rows closed on 2026-08-26**: TC-OPS-05, SP-02, SP-03,
  **SP-09 / TC-OPS-01**, SP-13 / TC-LIM-02 and SP-10 — the kill switch engaged, every route including a
  mutation refused with a safe body, `/healthz` and `/static/` exempt as designed,
  **the Discord bot and Foundry confirmed unaffected by the Operations Owner**,
  and full recovery verified. **I-06 remains Open**: criterion 1 still needs the
  proxy-boundary parity half (SP-13 / TC-LIM-02), and criteria 3 through 8 need
  the sittings still ahead.
- **TC-OPS-05 is now Passed**, at the third observation on 2026-08-26: run 1
  failed on N-7, run 2 on N-13, run 3 is clean on every class over a fully
  accounted-for interval. **I-06 criterion 4 moves one row closer and I-06
  itself remains Open.** A coverage limit is recorded: no worker job ran in the
  observed interval, so SP-12 is to be re-observed once after the performance
  and worker-recovery sittings. **A separate open question stands** — the
  deployed portal answered `POST /v1/auth/logout` with `415` twice, which the
  shipped sign-out control cannot produce; if a real click does that, session
  revocation is broken and A-05 criterion 7's **Met** status is wrong.
- *(Superseded, retained for history)* **TC-OPS-05 was Failed on a new class.** The N-7 fix was deployed at
  `2026-08-26T12:26:49Z` and **verified on the running portal**: the credential
  class is clean. SP-12's re-run over the fresh interval then found **N-13**, the
  client IP address logged in plaintext, which operational contract §5 prohibits
  outright. Remediated in the repository with a keyed per-process pseudonym and
  proved against a real uvicorn; **not deployed**, and deploying it is a decision
  the Operations Owner has not yet taken because the code is unreviewed. **A-06 remains Open. R-23 remains an active accepted residual.**
  The Phase 3 gate remains open and **Phase 4 remains unauthorized.**

## C2 contract decision and F5/S-2 review — 2026-08-25

- **C2 accepted.** Peter Duscha, Acceptance Authority, accepted the additive
  VM-16 `break_glass_credentials` health-contract correction after Codex's
  independent and security-focused recommendation. The earlier statements below
  that call C2 proposed or unapproved are historical and are superseded by this
  decision.
- **F5/S-2 closure recommended.** Codex independently reviewed the supported-
  installer execution produced by the filesystem cutover, observed the worker
  active with the required effective environment-file order, and reported no
  blocking or important finding. The Acceptance Authority has not separately
  declared the RAID item closed in this decision.
- **A-05 remains open.** Criterion 4 still needs its remaining deployed
  observation/production-refusal evidence; criterion 10 remains the Security
  Reviewer's final confirmation. No public exposure, Phase 3 gate closure or
  Phase 4 authorization follows from accepting C2.

## Filesystem-layout migration hold — 2026-08-25

- The accepted target is `/opt/freedom-blades` with `platform`, `runtime`,
  `reference` and `workspace` responsibilities; `/srv/freedom-blades` owns
  persistent service paths and `/etc/freedom-blades` owns configuration.
- **Risk controlled:** Python environments are recreated, never moved, because
  entry-point shebangs embed their absolute creation path. Every move refuses an
  existing target; directory trees are never merged. Historical evidence is not
  mechanically rewritten.
- **Rollback:** stop the three Freedom services, restore backed-up unit/Caddy
  files, move the four trees to their exact legacy locations, reload, and repeat
  direct service/journal/endpoint checks. Old runtime content remains until the
  observation hold is released.
- **Cutover observed; cleanup hold remains:** the Operations Owner recorded the
  directory inventory, effective systemd/Caddy paths, service states, endpoints
  and asset integrity in status update 59. Obsolete rollback environments and
  review trees remain until the observation hold is deliberately released.


## P3.5 C3/C4 acceptance and Low diagnostic correction — 2026-08-25

- Codex accepted the C3 and C4 repository remediations with no blocking finding
  and retained its recommendation to approve C2's boolean health-contract change.
- One Low issue was corrected directly: the newline sentinel in
  `worker_env_file_problem` previously masked `cat`'s failure status. An unreadable
  file was still refused, but with a content-mismatch message and raw stderr. The
  validator now preserves the read status, emits only its controlled refusal, and
  has an executable unreadable-file regression.
- **No RAID closure follows.** F5/S-2 still require the authorized supported-
  installer run and direct worker evidence. A-05 criteria 4 and 10 remain open,
  and C2 still requires the Acceptance Authority's decision.

## P3.5 re-review amendment (C3/C4) — 2026-08-25

Recorded after Codex re-reviewed the C1/C2 remediation over `020f455..78dfb67`.
Return package:
`docs/review/phase-3-p3-5-codex-c3-c4-remediation-2026-08-25.md`.

- **Both C1 and C2 core mechanisms were accepted**, and Codex **recommends
  approving** the additive C2 health-contract change once C4's language is
  corrected. That is a specialist recommendation and is recorded as one: it is not
  the Acceptance Authority's approval, which remains outstanding.
- **C3 (High) — an existing worker environment file was not safely confirmed.**
  The check accepted any file whose last `WORKER_ENABLED=` assignment said `true`.
  The worker unit reads that file **after** the shared portal file, so every other
  assignment in it overrides the portal's: extra `WEB_DATABASE_URL` and
  `WORKER_ARTIFACT_ROOT` lines above a conforming last line would have been adopted
  silently, redirecting the worker's database and artifact store. Ownership, mode
  and symlink shape were unchecked. **Remediated**: the file must be a regular file
  (never a symlink), owned `root` and the service group at mode `0640`, with
  complete content of exactly one line reading `WORKER_ENABLED=true`. The check
  lives in `infra/staging/lib/worker-env-file.sh` so 21 tests execute the
  operator's own validation rather than grepping the installer. It still refuses
  rather than repairs, and still never overwrites.
- **C4 (Medium) — a documentation defect with incident consequences.** "Fewer than
  two credentials" was described as "the emergency route cannot be used". That is
  true of zero and of no protected account, and **false of exactly one**: a single
  enabled credential still authenticates. During an outage an operator could have
  been told the authenticator in their hand was unusable. Corrected to readiness
  against N-13's redundancy floor, with the three states written out, in the
  operations guide, the health check's docstrings, the lifespan comment, the S-15
  rationale in the configuration and dependency contract, the VM-16 block, the
  earlier return package and this register. The boolean's behaviour is unchanged,
  and a test now asserts the corrected wording.
- **Nothing closed.** F5/S-2 remain pending the authorized installer re-run on the
  staging host and Codex's re-review of this package. A-05 criterion 4 remains open
  on both halves and criterion 10 is untouched. The C2 contract change remains
  **proposed**.

## P3.5 independent-review remediation amendment — 2026-08-25

Recorded after Codex's independent review of `0bef692..020f455` requested changes
on two High findings. Return package:
`docs/review/phase-3-p3-5-codex-c1-c2-remediation-2026-08-25.md`. This amendment
**supersedes the two statements below it** that read as though F5/S-2 were closed
and F6 had no proposed disposition.

- **S-2/F5 are NOT closed at repository level.** Codex finding C1: the F5 repair
  reached `infra/systemd/freedom-worker.service.tmpl` and the operations guide but
  not `infra/staging/setup-portal-host.sh`, the template's only executable
  consumer, which never substituted the new `__WORKER_ENVIRONMENT_FILE__` and still
  appended the losing `Environment=WORKER_ENABLED=true`. A newly generated worker
  unit would have been broken. **Remediated**: the installer writes and substitutes
  `/etc/freedom-web/worker.env`, appends no `Environment=` line, refuses a unit
  whose directives still carry a placeholder, and verifies the effective
  `EnvironmentFiles` order with systemd after `daemon-reload`; five repository tests
  render each unit through the installer's own substitutions, four of which fail
  against the installer as reviewed. The generated unit is directive-for-directive
  identical to the running, manually repaired one. **Closure still requires** Codex
  re-review and one root-held step — re-running the supported installer on the
  staging host and observing `freedom-worker` active from `systemctl`/`journalctl`,
  never from `/healthz`'s `worker_heartbeat`.
- **F6 has a proposed disposition, and it is implemented rather than deferred.**
  Codex finding C2: F6 is nonconformance with the written A-05 A-4 requirement, not
  an optional preference. Of the two permitted paths — change the reporting
  contract, or formally amend A-4 — this package takes the first. `/healthz` gains
  `break_glass_credentials` (a boolean, never the count, re-asked on every request),
  and the lifespan logs the S-15 warning it previously only assigned. The change is
  additive: `VIEW_MODEL_VERSION` stays `vm-1`, and no route, view-model field,
  status code, template, migration or schema changes. **It is proposed, not
  approved**: the Acceptance Authority's approval and the Security Reviewer's review
  of its disclosure and availability effects are both outstanding. A host where
  nobody has enrolled now answers `degraded`/`503`, which is the intended reading of
  A-4 and a visible change for any monitor.
- **A-05 criterion 4 remains Open.** Its `/healthz` half exists in the repository
  and has been observed on no host; its production-refusal half remains
  unobservable before an authorized production deployment. Criterion 10 is
  untouched. **Criteria 4 and 10 remain the only A-05 criteria outstanding.**

## P3.5 handover-execution amendment — 2026-08-25

Recorded after executing `docs/review/Handover information`. Full operational
record: `docs/review/phase-3-p3-5-post-remediation-operational-addendum-2026-08-24.md`.

- **A-05 remains Open, and moved substantially.** **Criterion 6 is now evidenced
  in full**: R-41 and R-46 were addressed directly from inside an authenticated
  page of a live break-glass session and both refused `403
  emergency_surface_refused` — N-65's continuity-surface check, evaluated before
  the route's capability requirement and before any handler object lookup. F3 is
  answered. **Criterion 3 is evidenced** (SP-23): retirement below two enabled
  credentials is refused before any write, exit status 1. **Criterion 9 is
  satisfied**: `docs/operations/break-glass-credential-custody.md`, accepted by
  Peter Duscha on 2026-08-25. **Criterion 4 is half-observed** (SP-24) — below and
  at the threshold on a disposable database, both starting normally with
  byte-identical `/healthz` bodies. **Its production half is not observable before
  a production deployment exists**, established by attempting it on 2026-08-25:
  `WEB_ENVIRONMENT=production` pins the public origin, OAuth redirect URI and
  Discord guild to their real production values, and configuration is refused
  before the lifespan runs, so S-15's production branch is never reached. The
  earlier analysis — that only a database named `freedom_production` was needed —
  was wrong, and the disposable database created to test it was dropped two
  minutes later. Either A-4 is amended to what a non-production host can observe,
  or criterion 4 stays open until production exists; the judgment is the Security
  Reviewer's. **Criteria 4 and 10 remain the only A-05 criteria outstanding.**
- **S-1 is satisfied for this deployment.** The portal was restarted onto commit
  `0bef692` and the running process (PID 3785672) is proved to postdate it by a
  mechanism rather than a favourable timestamp: every tracked source file predates
  the process start, and CPython validates cached bytecode against source mtime
  and size. The control stays live for every future deployment.
- **S-2 is resolved, and the cause was ours** — recorded as **F5**.
  `freedom-worker.service` had never started and could not have: the unit set
  `Environment=WORKER_ENABLED=true` while reading the shared portal
  `EnvironmentFile`, and `systemd.exec(5)` gives the file precedence, so the
  shared file's `WORKER_ENABLED=false` — required there by S-11 in the other
  direction — silently won and the worker refused itself on every start. The
  arrangement came from this repository's own operations guide, which offered it
  explicitly. The guide and `infra/systemd/freedom-worker.service.tmpl` are
  corrected; the worker is running. **I-06's worker prerequisite is met**; its
  named procedures remain untouched.
- **S-4 is closed end to end.** Under a real provider outage isolated to the
  portal's service account, `/healthz` reported `identity_provider: false`,
  `degraded` and `503` — where the same `iptables` rule on the same host reported
  `ok` and `200` a day earlier. Isolation was re-proved in both directions and the
  rule removed in the same sitting.
- **F6 raised; no repository change proposed.** A below-threshold credential count
  is detected and then reported to nobody outside production. `run_resource_checks`
  produces a warning naming the shortfall exactly; the lifespan assigns it to
  `composition.startup_warnings`, which no route, service, repository or control
  reads; it is never logged and never reaches VM-16; and S-15 is a refusal only in
  production. A staging account down to one credential answers `/healthz`
  byte-identically to a healthy one. This is the third instance of one pattern
  after S-4 and `worker_heartbeat`. The route surface is frozen and VM-16 is an
  accepted closed vocabulary, so the disposition belongs to the Security Reviewer
  and the Acceptance Authority, not to a drive-by fix during evidence work.
- **All five code findings are closed end to end.** S-4, S-5, S-6, S-7 and S-9 are
  each accepted in the repository **and** observed behaving on the deployed build
  (SP-25, SP-26, 2026-08-25). S-5 is the finding the package began with — limiter
  refusals answering `429` with a correlation reference and writing nothing — and
  every reference shown to the operator during the re-observation sitting resolves
  to its audit row. **No deployed re-observation remains outstanding.**
- **R-23 remains Active**, unchanged: still one browser on one platform.
- **No Phase 3 gate or exposure decision is made**, and none is requested.
  Criterion 4's wording, criterion 10 and every I-06 procedure remain outstanding.
  Public exposure and Phase 4 remain unauthorized.

## P3.5 supervised-session remediation amendment — 2026-08-24

Recorded after the supervised session
(`phase-3-p3-5-supervised-session-evidence-2026-08-24.md`), Codex's two review
passes, and the remediation submitted as
`phase-3-p3-5-supervised-session-remediation-submission.md`.

- **A-05 remains Open, and moved.** Criteria 1, 2, 2a and 5 are evidenced by the
  session; criterion 8 by SP-21; criterion 6's presentation half and its three
  GET routes by SP-22. **Criterion 7's two blocking findings — S-5 (limiter
  refusals unaudited) and S-6 (logout attributed to `guild_member` for a
  break-glass administrator) — were remediated and accepted by independent and
  security re-review on 2026-08-24.** Criterion 6's remaining half is the two POST routes R-41 and R-46,
  which need the Operations Owner and a live break-glass session; criteria 3, 4,
  9 and 10 remain Not Run. The Security Reviewer's criterion-10 confirmation is
  explicitly conditional on the re-review.
- **I-06 remains Open.** S-4 is remediated — `/healthz` now probes the identity
  provider instead of asserting it — which unblocks TC-OPS-05's premise but
  evidences none of I-06's procedures. **S-2 stands:** `freedom-worker.service`
  is inactive, and it is an operational prerequisite for the worker procedures.
  **S-1 stands** as a deployment/reload gap: the deployed process served code
  8½ hours older than the commit under test while every suite was green, and
  build identity must be verified after deployment before any later evidence run
  is trustworthy. No repository change is proposed for either.
- **R-23 remains Active.** TC-UI-01/02 are satisfied for **one** browser on one
  platform (Chrome, macOS 26). TC-UI-08's device matrix is uncovered and
  TC-UI-09 is permanently Not Run under decision D-f.
- **N-32a accepted 2026-08-24.** Peter Duscha, Acceptance Authority, accepted 10
  WebAuthn challenge issuances per source IP per 10 minutes, separately from
  N-32's unchanged assertion budget. It answers a break-glass **availability**
  finding: while the two shared a bucket, an ordinary operator mistake could
  exhaust the emergency path during the outage that path exists for. This
  numeric decision closes no RAID item or gate.
- **No Phase 3 gate or exposure decision is made**, and none is requested. Public
  exposure and Phase 4 remain unauthorized.

## P3.5 frontend acceptance amendment — 2026-08-24

- **A-05 remains Open.** Codex accepted the repository implementation of the
  emergency WebAuthn client, including strict protocol/refusal validation and
  executable ceremony tests. This removes the frontend-code blocker but does
  not prove either real credential works at the intended staging origin/RP ID.
  The supervised two-credential ceremony and Security Reviewer confirmation are
  still required.
- **R-23 remains Active.** Frontend source, structural and workflow automation
  passed review, but TC-UI-01/02 and the real-device checks remain Not Run. A
  bounded supervised browser session is documented in
  `docs/review/phase-3-p3-5-frontend-code-acceptance-and-supervised-session-plan.md`.
- **I-06 and A-06 remain Open.** This frontend decision supplies no missing
  staging operations or representative-load evidence.
- **No Phase 3 gate or exposure decision is made.** The manual session planned
  for later on 2026-08-24 moves no status until its results are recorded and
  accepted by the named authority.

Scale: probability and impact are `Low`, `Medium` or `High`. The Delivery Lead
updates status and due dates; the named role owns the response. A person's name
must replace each role assignment before the affected work starts.

## P3.G1 closure amendment — 2026-08-16

This dated amendment supersedes the older trailing status sentences in the long
I-07, I-09 and I-10 chronology rows below; those sentences are retained as the
history of what each remediation submission reported before acceptance.

- **I-07 — Closed.** The complete independent implementation and distinct
  security-focused re-review accepted the durable OAuth completion/provider
  binding and linear rotation integrity. Peter accepted P3.1 and closed P3.G1.
- **I-09 — Closed.** The same re-review accepted the accumulated session
  lifetime, composition lifecycle and break-glass attempt-budget corrections.
- **I-10 — Closed.** The same re-review accepted the exact numeric construction,
  canonical settings/dependency authority and corrected evidence controls.
- **I-06 — Open.** It does not block P3.2. It blocks staging/production exposure
  and final Phase 3 production-readiness acceptance until a named staging build
  passes TC-LIM-02, TC-SEC-07's browser half, TC-OPS-01…05 and TC-PERF-01…03,
  with dated environment/build identity, explained skips or failures, and
  Operations Owner plus required reviewer acceptance.
- **A-05 — Open.** It does not block P3.2. It blocks public staging/production
  exposure until the Operations Owner records the host/environment and date,
  confirms at least two enabled real WebAuthn credentials through the protected
  operator/startup check without recording credential material, and the Security
  Reviewer confirms break-glass readiness.

Review and gate record:
`docs/review/phase-3-p3-g1-independent-and-security-re-review-2026-08-16.md`.

## Risks

| ID | Risk | Probability | Impact | Owner | Mitigation / trigger / contingency | Status |
|---|---|---|---|---|---|---|
| R-01 | Sheet row identity ambiguity corrupts character identity | Medium | High | Data Owner | Fail closed on mapped semantic name changes; one shared display-name comparison policy (`domain/names.py`) used by parser, service and both repositories; regression and PostgreSQL tests. Trigger: any unexplained name/mapping change. Contingency: stop import, roll back, reconcile mappings deliberately. | Active; mitigation independently reviewed by Codex and accepted by Peter Duscha on 2026-08-02. Residual narrowed 2026-08-02 by OD-42: the absence of database display-name uniqueness is now a deliberate accepted decision, not an open gap, so the remaining residual is that the legacy bot lookup uses its own comparison until its owning package migrates |
| R-02 | Real Foundry snapshot differs from synthetic contract | High | High | Data Owner | Versioned exhaustive profile and supervised rehearsal. Trigger: unknown path/version/shape. Contingency: reject snapshot and revise contract through change control. | Active |
| R-03 | Phase 5 scope cannot fit its roadmap range | High | High | Delivery Lead | Split into gated work packages and estimate each after discovery. Trigger: any package not meeting ready criteria. Contingency: rebaseline release scope; never compress tests or gates. | Active |
| R-04 | Authorization gap permits mutation of another character | Medium | High | Security Reviewer | OD-16 and OD-17 are closed; implement server-side linked-character and role checks in Phase 3 and affected later packages, close OD-39 before Phase 5.7/5.8, and require denial tests. Trigger: any unauthenticated or cross-character success. Contingency: disable affected command/feature until fixed. | Active; policy inputs for Phase 3 closed 2026-08-12, implementation control remains outstanding |
| R-05 | PostgreSQL-only behavior is missed when integration tests are skipped | Medium | High | Technical Lead | Maintain disposable guarded database and require database evidence at mutation/import gates. Trigger: skipped required DB suite. Contingency: gate remains deferred. | Active |
| R-06 | Cutover or rollback loses live-bot availability | Medium | High | Operations Owner | Feature flags, backups, rehearsed restore/rollback, monitoring and verification window. Trigger: failed health/reconciliation check. Contingency: return to accepted Sheet-backed path within documented recovery objective. | Active |
| R-07 | Foundry or dnd5e version changes invalidate integration | Medium | Medium | Technical Lead | Explicit supported versions and fail-safe negotiation. Trigger: deployment version outside range. Contingency: stop import/sync pending contract update. | Active |
| R-08 | Catalogue content creates licensing or provenance exposure | Medium | High | Product Owner | Pinned provenance, allowlist, minimum authorized content, legal review where needed. Trigger: uncertain redistribution right. Contingency: retain identifiers/source references only. | Future |
| R-09 | Reviewer or maintainer capacity delays critical gates | High | Medium | Delivery Lead | Book review windows in phase plan; expose queue in status. Trigger: no reviewer by ready date. Contingency: reforecast, not self-approve. | Active |
| R-10 | A stored snapshot artifact exposes every exported Actor's mechanics at rest | Low | Medium | Operations Owner | Restricted root outside the repository (`0700`/`0600`), **enforced rather than assumed** at startup and on every store and read, anchored to a directory descriptor so a pathname replacement cannot redirect an operation (see R-15), checksum-derived names, no download route and no directory listing, documented retention and deletion, encrypted host backups. Checksum and audit record survive deletion. Trigger: any artifact found outside the configured root, in a backup without encryption, or served by a route. Contingency: delete the artifacts, rotate nothing (no credential is involved), and record the exposure. | Active from 2026-08-04 (Phase 2 I-03) |
| R-11 | A Foundry submission credential leaks from a client the platform does not control | Low | Low | Security Reviewer | Submit-only scope: it cannot apply, read Council data, read audit history, mutate a character or reach PostgreSQL. Configuration holds only the SHA-256 of a ≥32-character generated secret. Rotation and revocation are a configuration change plus a reload, and no longer touch Foundry. **The credential is not stored in Foundry at all** (remediation of S-B-1, 2026-08-04): a world-scoped setting's value is delivered to every connecting client, so the submitting GM enters it per submission and it is persisted nowhere. Trigger: an unexpected pending snapshot, or a credential appearing in a log, ticket, screenshot or any Foundry setting. Contingency: revoke the entry and reload; delete the unwanted pending artifact; the snapshots it delivered are immutable and are not retracted. | Active from 2026-08-04 (Phase 2 I-03); likelihood reduced 2026-08-04 by the S-B-1 remediation. Residual: the credential is typed into a GM browser once per submission, so a malicious module or extension in that browser can observe it |
| R-12 | The exporter and the Manager's parser drift apart in two languages | Medium | Medium | Technical Lead | `tests/test_exporter_contract.py` runs the exporter's real serialization path and feeds the output to the real Python parser, and asserts the bytes equal the Python canonical encoding of the same document. No committed golden artifact. Trigger: that test failing, or being skipped because `node` is absent. Contingency: treat a skipped run as unverified and do not submit on it. | Active from 2026-08-04 (Phase 2 I-03) |
| R-10 | Requirements continue growing inside active phases | High | High | Product Owner | Controlled baseline and impact-assessed change requests. Trigger: new mandatory outcome after phase start. Contingency: defer or rebaseline with explicit approval. | Active |
| R-11 | Longer legacy-Sheet operation causes drift or cutover failure before typed packages migrate all fields | Medium | High | Operations Owner / Data Owner | No dual writes; characterize each field group; package-owned deterministic migration, reconciliation totals, feature-flag cutover and rehearsed rollback. Trigger: unexplained source/target difference or legacy behavior without a typed replacement. Contingency: keep that field on the legacy path and defer its cutover. | Active — introduced by baseline v1.1 |
| R-12 | A legacy field is omitted, duplicated or migrated by the wrong package | Low | High | Data Owner | Controlled exhaustive migration register, automated profile/inventory consistency check and one accountable package per row. Trigger: new/renamed source field or conflicting target. Contingency: stop the affected package/cutover and amend the register through change control. | Active — introduced by baseline v1.2 |
| R-13 | A scalar legacy aggregate is expanded into invented event history or an uncontrolled vocabulary creates duplicate identities | Medium | High | Data Owner / Product Owner | Typed opening facts, no-synthetic-history rule, machine-readable source manifest and controlled vocabulary register. Trigger: migration proposes events unsupported by source records or creates a definition from unmatched text. Contingency: stop migration, preserve explicit unresolved data and obtain a Data Owner ruling. | Active — introduced by baseline v1.5 |
| R-14 | The supported browser submission workflow is verified by test but not by a browser | Medium | Medium | Technical Lead | The CORS preflight is implemented against an explicit origin allowlist and covered by tests that reproduce the preflight protocol, plus one exercise over a real socket. **None of them is a browser, and `curl` does not enforce CORS** — the class of failure that produced Blocking finding B-1 in the first place. Trigger: any claim that the browser workflow works, before operations §8.2 has been run. Contingency: treat the workflow as unverified; run the maintainer-supervised real-origin check in `../operations/foundry-snapshot-submission.md` §8.2, including the negative case where removing the origin makes the submission fail. | **Open** from 2026-08-04. Related: the credential confidentiality boundary is likewise established from Foundry source and not from a live second client — operations §8.1, also not run |
| R-15 | Another account on the host replaces the artifact root between validation and use | Low | High | Security Reviewer | The root is opened once with `O_DIRECTORY \| O_NOFOLLOW` and every create, open, publication, read, `unlink` and directory `fsync` is resolved against that descriptor, so a pathname replacement redirects nothing (remediation of S-B-2's re-review, 2026-08-04). Type, owner and mode are re-proved through the descriptor at startup, on every store and on every read; the ancestors that would have to be writable for such a replacement to be staged are refused at startup (`root_ancestor_untrusted`); a divergence between the configured path and the anchored directory is refused (`root_replaced`). Trigger: a `root_replaced` or `root_ancestor_untrusted` refusal in the service log, or an artifact appearing outside the configured root. Contingency: stop the service, establish who can write the parent chain, correct ownership and modes per operations §5.6, restart. | **Open** from 2026-08-04. Residual, stated in the remediation submission §12.3: the anchoring is proven against pathname substitution performed by the test process and against mode, owner and type as this process observes them — **no cross-account experiment has been run and no automated test creates a second POSIX account**. The ancestor walk is a startup check and does not detect a parent that becomes writable later |
| R-16 | A submission destroys an artifact the service did not write and has not validated | Low | High | Security Reviewer | Publication creates the checksum entry with `link(2)`, which either creates it or fails `EEXIST` and has no mode in which it removes an existing entry (remediation of the third security review, 2026-08-05). An entry that appears between the presence check and publication is re-opened through the anchored descriptor and re-proved for type, owner, mode and content: a valid one is reused, and an invalid one is refused and left byte for byte and mode for mode as it was found. Cleanup is structurally unable to name anything but a `.incoming-*` temporary, so a failed cleanup cannot delete a published artifact — though it can leave one behind, which is R-18 rather than this risk. Startup proves the filesystem both supports hard links and refuses a link over an existing name (`link_unsupported`). Trigger: an `artifact_*` or `checksum_mismatch` refusal from a **store**, which means an unexpected entry is sitting under a checksum name. Contingency: operations §9, "An unexpected entry under a checksum name" — preserve it, establish what wrote it, and do not delete it before that is understood. | **Open** from 2026-08-05. Residual: convergence of two writers is proven deterministically by running the second writer inside the first's publication window, not by a multi-process stress test; and the `EEXIST` guarantee is the kernel's, proven at startup on the configured filesystem rather than argued from documentation |
| R-17 | The artifact root is deployed on a filesystem or directory chain the storage policy cannot accept | Medium | Medium | Operations Owner | Two host prerequisites, both proven at startup rather than assumed, and both refusing to start rather than half-working: the filesystem must support hard links with create-only semantics (`link_unsupported`), and every directory above the root must be owned by `root` or the service account and not writable by others without the sticky bit (`root_ancestor_untrusted`). `.env.example` and operations §5.6 state both, with `namei -l` as the pre-deployment check. Trigger: either refusal at service start. Contingency: move the root to a supported filesystem, or correct the ownership and modes of the parent chain; **do not weaken the policy to fit the host** — that is a security-policy change reserved to the Acceptance Authority. | **Open** from 2026-08-05. Note: the automated suite bounds the ancestor walk at pytest's temporary root so that tests about publication and descriptor lifetime are hermetic, and the production walk is separately exercised unbounded. The bound is a test seam with no environment variable; it does not remove the deployment prerequisite |
| R-18 | Leftover `.incoming-*` temporaries accumulate in the artifact root and consume storage unnoticed | Low | Low | Operations Owner | Publication writes a temporary, links the checksum name to it, and unlinks the temporary **best effort**: `_discard` swallows `OSError`, so a submission that succeeded may leave one private hard link behind and the service never learns or reports it (correction of evidence finding I-3R-1, 2026-08-05; the third-remediation record had claimed no temporary survives). A leftover is `0600` inside a `0700` root, is served by no route, and cannot invalidate or remove the published artifact; the cost is an inode, and the bytes themselves once the artifact is deleted under retention. Detection is the read-only, age-bounded, link-count-aware procedure in `../operations/foundry-snapshot-submission.md` §5.6, "Temporary files left by a failed cleanup", proved against synthetic files by three tests in `tests/test_artifact_store.py`. Trigger: a leftover found by that procedure, and especially a *repeated* one — an `unlink` only fails when the root's mode or ownership has drifted or the filesystem is full or read-only. Contingency: check the §5.6 required directory state before treating it as routine; remove leftovers deliberately after reading the link count, never automatically. | **Open** from 2026-08-05. Residual: nothing counts, alerts on or removes leftovers, and how often an operator should run the procedure is an operations decision that has **not** been taken. No listing or deletion capability was added to the service, deliberately |
| R-19 | OAuth, session or CSRF defect exposes a protected web surface | Medium | High | Security Reviewer | P3.0 threat model and numeric contract; P3.1 fail-closed foundation; opaque server-side sessions, rotation/revocation, synchronizer CSRF, exact-origin checks and distinct security review. Trigger: any bypass, unsafe redirect, token disclosure or stale privilege success outside the accepted window. Contingency: disable `freedom-web` protected routes and keep the existing bot/Sheet path operating. | Proposed active Phase 3 risk; owner assignment confirmed with plan acceptance |
| R-20 | Discord outage or rate limiting produces stale authorization or prevents portal use | Medium | High | Technical Lead / Security Reviewer | Five-minute membership cache, bounded read-only grace proposed in the Phase 3 plan, immediate mutation refusal, metrics and safe degraded UI. Trigger: Discord errors, cache age beyond policy or revocation test failure. Contingency: fail closed and expose no protected data after the grace bound. | Proposed active Phase 3 risk. Numeric policy accepted 2026-08-13 (N-09, N-10); P3.0 adds the projection state machine SM-06 and outage tests TC-OUT-01…04 |
| R-21 | Reconciliation background work duplicates, stalls or is lost on restart | Medium | High | Technical Lead | PostgreSQL-backed job identity, claim/lease, heartbeat, idempotency, stale recheck, bounded retry and real concurrency/restart tests. Trigger: expired lease, duplicate success effect, orphaned running job or false completion. Contingency: stop new claims, preserve audit/history and run the reviewed recovery path. | Proposed active Phase 3 risk. P3.0 supplies the durable-job schema, the `FOR UPDATE SKIP LOCKED` claim, the six-state machine SM-05 and the concurrency/restart tests TC-JOB-01…14 |
| R-22 | Backend route/view-model contracts drift during Gemini integration | Medium | Medium | Technical Lead | Contract stop gates P3.G2/P3.G3, typed view models and explicit cross-boundary change review. Trigger: template needs an unaccepted route, field or authority decision. Contingency: stop frontend integration and return the change to Claude/Codex/Peter. | Proposed active Phase 3 risk |
| R-23 | Production adaptation regresses accessibility despite accepted static prototype | Medium | High | Product Owner / Accessibility reviewer | Preserve frozen reference, add production automated browser checks, Codex source review and Peter real-device acceptance; report unrun assistive-technology checks honestly. Trigger: keyboard trap, lost focus, overflow, contrast or screen-reader defect. Contingency: stop exposure and remediate before production-readiness acceptance. | **Active accepted residual after P3.G4 closure (2026-08-23).** P3.4 source, structural, contrast and accessibility automation passed independent review, and Peter accepted P3.4. TC-UI-01/02, TC-UI-08 and TC-UI-09 remain honestly Not Run; I-06 and the P3.5/staging evidence package retain browser, real-device and assistive-technology follow-up. P3.4 acceptance does not classify those checks as passed or authorize exposure. |
| R-24 | Co-located web/import workload degrades the live bot or Foundry services | Medium | High | Operations Owner | Bound HTTP bodies, DB pool, job concurrency and polling; stage the measured 32-Actor preview and refusal at accepted limits; monitor CPU, memory, database and latency without player data. Trigger: threshold breach defined in P3.0/staging. Contingency: disable claims/web route, leave bot operational and re-plan worker/topology. | Proposed active Phase 3 risk. P3.0 supplies the thresholds (N-41 job concurrency 1, N-42 queue bound, N-45 runtime cap, N-47 worker memory ceiling, N-53/N-54 pools) and a separate `freedom-worker` service so a 9.57-second GIL-holding parse cannot stall the portal. **Peak memory remains unmeasured** — see R-28 |
| R-25 | Development, staging or production configuration crosses environment boundaries | Low | High | Operations Owner | Typed startup validation, separate web venvs, DB roles, Discord applications/guilds, loopback ports and environment files; destructive-test guards; no production backup in staging. Trigger: shared credential/ID, production endpoint in non-production or unsafe DB target. Contingency: refuse startup, rotate exposed credential and rebuild the environment separation. | Proposed active Phase 3 risk |
| R-26 | Emergency administrator access becomes a permanent backdoor or gains game-policy authority | Low | High | Security Reviewer / Operations Owner | No permanent local password; pre-enrolled phishing-resistant credentials; host-local hashed single-use recovery grant; short session; Platform-Administrator-only capability; audit and rate limits. Trigger: remote recovery issuance, reusable token, unaudited attempt or Council capability. Contingency: disable the break-glass web route, revoke credentials/sessions and use host recovery after review. | Active Phase 3 risk. P3.G0 accepted ADR 0010, host-local-only issuance/enrollment, N-65, N-67, mapping provenance and R-38. The first design's two-session escalation is closed in the accepted contract and must now be proven by TC-BG-05a…05e during implementation. Residual RR-13 is accepted: an emergency session can leave durable *continuity-scoped* administrator capability behind, which is persistence required for recovery rather than escalation |
| R-27 | A replacement identity provider merges or strands accounts | Medium | High | Data Owner / Security Reviewer | Stable internal platform account, exact `(provider, subject)` identities, no name/email matching, explicit linking/retirement workflow, control-total migration and unresolved records. Trigger: ambiguous link, orphaned account or changed provider subject. Contingency: stop provider rollout, preserve existing identity and reconcile manually through audited recovery. | Proposed active Phase 3 risk. P3.0 supplies the schema (unique `(provider_key, subject)` covering retired rows, no name/email column exists), the link/unlink/retirement state machine SM-04 and tests TC-ID-01…08. Residual: a future OIDC provider reusing subjects causes a refusal rather than a takeover |
| R-28 | The real-folder apply duration and the worker's peak memory have never been measured | Medium | Medium | Technical Lead / Operations Owner | Rehearsal B previewed a real 32-Actor folder in 9.566 s and **applied nothing**; the 500-Actor apply benchmark used Actors ~233× smaller, the calibration error already recorded as RA-5. P3.0 therefore models apply as a durable job rather than a synchronous handler, and sets N-45 and N-47 as guards rather than as measurements. Trigger: any production apply attempted before a staging measurement exists. Contingency: keep the portal's import controls disabled and apply through the existing operator path. | **Open** from 2026-08-13 (P3.0). Measurement is owned by P3.3 (TC-PERF-01, TC-PERF-02) and must precede production use |
| R-29 | A Phase 3 design defect is found only at implementation, after the contract has been frozen for Gemini | Medium | Medium | Technical Lead / Independent Reviewer | The P3.G0 remediation found four such defects **in review rather than in production** — an unreachable job state, a legacy constraint that would have blocked emergency audit writes, an escalation path across two sessions, and a contradiction between two contracts about PKCE storage. Each is now specified as executable SQL, an explicit constraint or a named PostgreSQL test rather than as prose. Trigger: any P3.1–P3.3 implementation that cannot be written from the contract as stated. Contingency: return the point to the contract and its gate, never absorb it in code. | **Open** from 2026-08-13. The mitigation is the review discipline itself; the four corrections are the evidence it works |
| R-P4-1 | A ledger with no physical table is judged insufficient at the Phase 4 gate, after the work is done | Low | Medium | Technical Lead | Ruled up front by **OD-48**: the ledger is `domain/` plus a consumer-owned protocol and an in-memory reference adapter, and durable idempotency reuses the existing `idempotency_keys` table under a Phase-4 scope | **Closed 2026-08-29:** the Phase 4 gate was approved without a physical table. The later durable-ledger obligation remains separately tracked by R-P4-4 and package 5.0/5.2 readiness |
| R-P4-2 | The Phase 4 characterization tests freeze legacy float-money behaviour and are later mistaken for accepted policy | Medium | Medium | Product Owner | Every such test names the defect and its owning package in its own docstring; **OD-51** and package-plan §4.4 are quoted in the submission. Trigger: any Phase 5 package citing a characterization test as the rule. Contingency: packages **5.7** (`/sale`) and **5.3** (`/lc`) must convert the path to integer copper and reproduce both PDF worked examples | **Active** from 2026-08-28 with the WP-0 delivery |
| R-P4-3 | `/info` exposes any character's wallet to any guild member, and Phase 4 preserves this exactly | Medium | Medium | Product Owner | Changing authorization is an explicit Phase 4 exclusion, so the behaviour is characterized rather than corrected. Raised to package **5.1**, whose gate is already profile-migration and read-path authorization review. Trigger: any transitional `/info` migration that carries the gap forward. Contingency: 5.1 closes it as part of its own gate | **Active**, owned by package 5.1. Recorded as an observation in **OD-52** |
| R-P4-4 | A posted ledger transaction is durable only as far as process memory, because OD-48 defers the physical ledger table | Medium | Medium | Technical Lead | Stated rather than mitigated in Phase 4, and bounded: the *receipt* is durable in PostgreSQL and is what every idempotency guarantee turns on; the reference adapter publishes under the version fence **before** the database commit and retracts if that commit fails, so no receipt can outlive a refused posting. The one residual window — a process dying between publish and commit — is unobservable while the book is process memory. Trigger: any proposal to treat the in-memory ledger as an authority, or to deploy it. Contingency: package **5.0/5.2** commits both halves in one database transaction, which the service is written to accept as a change of adapter rather than of use case | **Active** from 2026-08-29 with the WP-3 delivery. Nothing is deployed and no service runs this code |

## Assumptions

For current disposition, the 2026-08-28 decision at the head of this register
supersedes older status-cell prose for A-05 and A-06: both are Closed. The
long-form cells remain as the evidence history that led to the decision.

| ID | Assumption | Owner | Validation / deadline | Status |
|---|---|---|---|---|
| A-01 | One focused implementer is the basis of roadmap effort ranges | Delivery Lead | Confirm capacity before each phase baseline | Unvalidated |
| A-02 | A guarded disposable PostgreSQL environment remains available, including a restricted runtime role that can be assumed for denial evidence | Operations Owner | Confirm before every database gate | **Partly validated 2026-08-02.** The disposable database `freedom_test` and the owner/test login `foundry` are available. The temporary restricted role `freedom_runtime_test` now **exists** and can be assumed: it is `NOLOGIN`, non-superuser, cannot create roles or databases, cannot replicate, cannot bypass RLS, and `foundry` is a member able to `SET ROLE freedom_runtime_test`. Role creation is therefore no longer an evidence gap. **Validated 2026-08-05:** the template was corrected for the retained schema, and `tests/test_runtime_grants_live.py` applies it and proves `UPDATE`, `DELETE` and `TRUNCATE` denial **directly under the role** (`SET ROLE freedom_runtime_test`) against real PostgreSQL, including after hostile `PUBLIC` drift — 13 tests, no skips in the 2026-08-05 run. Nothing outstanding on this assumption; it remains subject to the environment continuing to exist before each database gate. **Re-confirmed 2026-08-14** before P3.1: `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` resolves through `assert_disposable_target` under `UNIX_SOCKET_ONLY`, and `verify_connected_unix_socket_target` proves `current_database() = 'freedom_test'` with both `inet_server_addr()` and `inet_client_addr()` null. P3.1's full database evidence ran against it |
| A-03 | Maintainers can provide a supervised immutable Foundry snapshot rehearsal | Data Owner | Required before Phase 2 gate | **Validated 2026-08-09 and closed for Phase 2.** Rehearsal A used a real 35-Actor non-live folder; Rehearsal B previewed the real 32-Actor active folder with every Actor accounted for, zero errors, zero warnings and zero unexplained identity discrepancy. The Data Owner attestation was signed 2026-08-10. No artifact or real Actor payload was committed. |
| A-04 | The legacy Sheet-backed bot remains the rollback implementation until approved cutover | Operations Owner | Validate at each Phase 5 cutover | Active |
| A-05 | The Server Administrator's protected platform account is established and at least two WebAuthn credentials are enrolled **before** the portal is exposed publicly | Operations Owner / Security Reviewer | P3.1 operator documentation and the startup check S-15; enrollment is host-local (C-03). Deadline: before any staging or production exposure | **Open, and substantially advanced on 2026-08-25.** Criteria 1, 2, 2a, 3, 5, 6, 7, 8 and 9 are evidenced. C2-1 is now **accepted**: `/healthz` carries the fresh, fail-closed boolean `break_glass_credentials` check and the lifespan logs S-15 without publishing credential count or material. **Criterion 4 was split on 2026-08-25 by decision D-n (change-log C-P3.5-T), approved by Peter Duscha as accountable Security Reviewer**, after the premise was verified in code: `WebEnvironment.is_production` is `PRODUCTION` alone and S-15 refuses only in production, so no staging-marked process can observe the production refusal, and a criterion satisfiable only after exposure could never close the item that gates exposure. **4a** — startup and `/healthz` observed below and at the N-13 threshold under `WEB_ENVIRONMENT=staging`, on a disposable database with synthetic credential records — remains an A-05 closure criterion and is **Open, executable**. **4b** — S-15's production-class refusal — **remains an A-05 closure criterion**, discharged by the guarded pre-exposure exercise **SP-27**: a disposable `freedom_production` database with synthetic credential records, outbound egress blocked, and `run_resource_checks` called directly so **no socket is ever opened**. **Corrected 2026-08-26 (D-o, change-log C-P3.5-U) after Codex Blocking finding B-1**, which showed D-n's premise conflated "production-marked" with "publicly exposed" and so would have weakened a security precondition. **4c** — a deployment-gate re-observation — is retained as defence in depth and never substitutes for 4b. Awaiting the Security Reviewer's confirmation of the correction. N-13 is unchanged and no control is weakened. The original wording is retained struck through in execution plan §13.2 so the change is reviewable and reversible. Criterion 10 still requires the Security Reviewer's final break-glass-readiness confirmation. Exactly one credential may authenticate but does not satisfy N-13's redundancy floor; zero cannot authenticate. Public exposure remains prohibited until both remaining criteria close. |
| A-06 | PostgreSQL is an acceptable substrate for the job queue and the cross-process rate limiter, so no second datastore is introduced | Technical Lead | P3.3 concurrency and restart evidence (TC-JOB-02…08) and the P3.5 staging rehearsal | **Open** — introduced by the P3.0 package 2026-08-13; the dependency proposal rests on it. P3.1 exercised the limiter half: `test_the_limiter_counts_across_processes` proves two engines sharing one database enforce one budget |
| A-P4-1 | No staging environment is required for Phase 4 | Operations Owner | Holds while the package deploys nothing and adds no persistent state | **Validated 2026-08-29 at the WP-4 delivery.** Phase 4 adds no migration, no table, no constraint, no grant, no configuration and no service change; nothing is restarted and no host is touched. The assumption would be void the moment a physical ledger table were proposed, which **OD-48** forbids in this phase |
| A-P4-2 | The established database-enabled web skip count of **80** still holds for an unchanged tree | Technical Lead | Measured against the unchanged tree before implementation and again at submission; a different figure is explained rather than adjusted to | **Validated.** Measured **80** on 2026-08-28 before any edit (package plan §16; all 80 are the two permission-matrix modules' permitted cells, none a database skip) and re-measured at the Phase 4 submission against the tree actually submitted. Stop condition 5 was not triggered |
| A-07 | The three deviations P3.1 declares against the accepted P3.0 contracts are acceptable as implemented | Technical Lead / Security Reviewer | Codex independent and security review at P3.G1, then Peter's decision | **Open** — introduced by P3.1 on 2026-08-14. (1) `role_capability_mappings.created_by_account_id` is nullable, constrained by `CHECK (created_by_account_id IS NOT NULL OR protected)`, because the migration inserts the protected row when no account exists; schema §8 states `Null: no`. (2) `WEB_SECRET_KEY_CLIENT_DIGEST` is added to the configuration contract's named set, because the schema specifies a *salted* address hash and an unkeyed one is reversible. (3) `webauthn_challenges` is added, because SM-03 requires a challenge row and schema §9 lists no table for it. Each is recorded in `docs/review/phase-3-p3-1-submission.md` §8 |

## Issues

For current disposition, I-06 is Closed by the Operations Owner's 2026-08-28
acceptance. Its long-form status cell remains as pre-decision evidence history.

| ID | Issue | Owner | Resolution condition | Status |
|---|---|---|---|---|
| I-01 | Phase 2 mapped-name normalization semantics differ between Python and PostgreSQL lookup | Technical Lead | Shared policy plus service/PostgreSQL regression evidence and re-review | **Closed 2026-08-02** — implementation and PostgreSQL evidence independently reviewed by Codex; accepted by Peter Duscha. The database-enforcement residual remains I-05 |
| I-05 | `characters.display_name` has no database uniqueness rule, so the shared comparison policy is enforced by the importer alone | Data Owner | A decided identity/uniqueness policy recorded as a maintainer ruling, or a recorded acceptance that the application enforces it | **Closed 2026-08-02** by OD-42, ruled by Peter Duscha: display names are not unique identities, multiple characters may share one, stable character IDs and external Actor IDs provide identity, and any legacy name-based candidate lookup fails closed when more than one candidate exists. No unique display-name constraint is added; the application enforcement is accepted deliberately. Package R2 implements the multi-candidate fail-closed lookup |
| I-02 | Phase 2 implementation contains the rejected ADR 0008 interim state/bootstrap/correction path | Technical Lead | Baseline the replacement plan; remove rejected scope; implement deferred legacy reporting; close Codex blocking findings; pass current-baseline §12 evidence; complete operational rehearsals | **Closed 2026-08-12.** Rejected scope was removed, deferred legacy reporting and evidence were accepted, C-24/B-1 closed on independent re-review, and Peter accepted the Phase 2 gate. |
| I-03 | Package-specific implementer/reviewer capacity is not yet recorded | Delivery Lead | Record agent assignments and Peter's decision/review availability during package readiness | Managed per package |
| I-06 | Mandatory staging-class, browser-class and real-device-class evidence remains incomplete | Operations Owner | Execute and accept the checks named in `phase-3-test-traceability.md` §20 against the deployed staging environment | **Open.** A staging deployment now exists, but existence and active services do not execute the gate procedures. TC-LIM-02, TC-SEC-07's browser half, TC-OPS-01…05 and TC-PERF-01…03 are not all completed and accepted. In particular, TC-PERF-02's real-folder apply has never been measured end to end; Rehearsal B previewed a real 32-Actor folder and applied nothing, while the synthetic benchmark used materially smaller Actors. TC-PERF-01 worker peak RSS and TC-PERF-03 health/status responsiveness during a running preview remain unmeasured. I-06 blocks the Phase 3 production-readiness gate and public exposure. |
| I-04 | Proposed baseline v1.0 is not accepted | Acceptance Authority | Approval recorded in change log | Closed 2026-08-02 |
| I-07 | SM-01's "session creation runs in the same transaction as the consumption" cannot hold together with the accepted no-database-transaction-across-provider-I/O invariant, because schema §9.2.1 makes verifier recovery and erasure one statement and PKCE requires that verifier before the identity is known | Technical Lead / Security Reviewer | Implement OD-44 with migration 0009, real-PostgreSQL concurrency/constraint/rollback and mutation evidence, then complete independent and distinct security re-review | **Decision closed 2026-08-14; implemented 2026-08-14; re-review still blocks P3.G1.** Peter approved the durable one-way binding, refined to one authoritative unique `sessions.oauth_transaction_id` relationship plus atomic `completion_claimed_at`; no redundant reverse FK. Migration 0009, the atomic claim, TC-AUTH-13/14 and four killed mutations are recorded in `docs/review/phase-3-p3-1-od-44-remediation-submission.md`; the unique index is scoped to non-rotated sessions, declared there for confirmation. **Confirmed conditionally 2026-08-14**: Peter approved that index and required rotation integrity to be strengthened, and Codex's re-review additionally found the claim did not bind the transaction's recorded provider. Both are remediated in `docs/review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md` — the claim compares `provider_key`, the expected key is derived from an indivisible verified provider result, and the rotation chain is made linear by a unique index, two composite foreign keys and one locked transactional operation, with TC-AUTH-15/16/17 and six killed mutations. Re-review still blocks P3.G1. |
| I-09 | Both session-continuation operations described their predecessor as *live* while testing only `revoked_at IS NULL`, so a `SessionRecord` resolved while a session was valid could rotate or refresh it after its idle bound and revive it; rotation additionally wrote a fresh absolute expiration, extending one login without limit; and the idle refresh applied N-06's 60-minute window to break-glass sessions, making N-15's 15-minute value inoperative. A refused refresh was also reported as success, because the repository returned nothing and a zero-row `UPDATE` was indistinguishable from a successful one | Technical Lead / Security Reviewer | Enforce liveness inside each conditional write, stop writing `absolute_expires_at` on either continuation, select the idle duration from the persisted authentication method, type the refusals, and produce real-PostgreSQL boundary, stale-record, concurrency and mutation evidence, then complete independent and distinct security re-review | **Open — remediated 2026-08-15, re-review blocks P3.G1.** The rotation half was found by Codex on 2026-08-14 and corrected the same day; the touch half was found by Codex's independent re-review on 2026-08-15 and is corrected in `docs/review/phase-3-p3-1-od-44-session-lifetime-remediation-submission.md`, with TC-AUTH-18/19 and nine killed mutants. **Reachability differs by half and is stated rather than smoothed over:** `rotate()` is reachable through `rotate_if_privileges_changed`, while no P3.1 HTTP route calls `touch()` at all, so its defect was latent and its correction is proven at the service and repository boundary only. The P3.2 package that wires either must treat `SessionRotationRefused` and `SessionTouchRefused` as end-the-session outcomes, never retries. **Amended 2026-08-15 (second independent re-review): that remediation was incomplete.** The idle-policy half had been corrected in `SessionService` only; `SessionRepository.touch()` still took `idle` and `expected_auth_method` as independent arguments and verified only the method, so a caller supplying a break-glass row's **correct** method beside N-06's 60-minute duration matched the row and extended its idle window to the emergency absolute bound. The repository test offered as proof supplied a *mismatched* method and never exercised that pairing. Corrected in `docs/review/phase-3-p3-1-od-44-session-touch-policy-remediation-submission.md`: the duration is no longer a parameter at either layer, being selected inside the conditional write by `CASE auth_method` from an immutable validated `SessionIdlePolicy` injected once at composition. Evidence is the rewritten TC-AUTH-19(h) and 13 killed mutants. Resolution now additionally requires that no supported API admit a caller-selected refresh duration. **Amended again 2026-08-15 (third independent re-review): that remediation was also incomplete.** Removing the two arguments moved the same authority into `SessionIdlePolicy`'s public dataclass constructor, which accepted any complete, duplicate-free, positive mapping — including the one giving *every* method N-06's 60 minutes — so a repository constructed with it applied 60 minutes to persisted WebAuthn and recovery-grant rows and N-15 was bypassed again. The policy tests proved completeness, uniqueness and positivity and never attempted a complete but semantically false mapping. A related composition defect was found alongside it: `WebComposition.services()` and `SessionService.__init__()` each derived a policy, so the two layers held equal-by-accident objects rather than one. Corrected in `docs/review/phase-3-p3-1-od-44-session-idle-policy-construction-remediation-submission.md`: the policy has no public constructor, its one factory takes `SessionSettings`, its mapping is classification derived from `AuthMethod.is_break_glass`, and one instance is injected into both layers at the composition root. Evidence is TC-AUTH-19(j) and 16 killed mutants. Resolution now additionally requires that no supported API admit a caller-*constructed* method-to-duration mapping, and that the repository and service demonstrably hold the same policy instance. **Amended a fourth time 2026-08-15 (idle-policy-construction re-review): that remediation was also incomplete, in three ways.** (F1) `SessionIdlePolicy.from_settings()` validated only positivity while `SessionSettings` was a public frozen dataclass with no construction-time validation, so `SessionSettings(..., emergency_idle_minutes=60, ...)` was an accepted object and the derived policy returned 60 minutes for both break-glass methods — the policy's closed constructor was irrelevant while the numbers it read were unconstrained. (F2) The refresh statement was generated by iterating the policy's public, overridable `__iter__`, so a subclass inheriting the supported factory replaced the mapping the SQL used while `for_method()` still reported 15 minutes; the reproduction bound `idle_seconds = 3600.0` for all three methods. (F3) `SessionService.__init__()` accepted a policy beside the repository and required no relationship between them, so a supported caller could create sessions under one idle window and refresh them under another. Corrected in `docs/review/phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md` by simplifying the construction model rather than adding guards: `SessionIdlePolicy` is **deleted**; `SessionSettings` enforces the accepted register in `__post_init__`; `SessionRepository` **derives** a `SessionPolicy` from settings, reading each number once, and accepts no policy object; the `CASE` branches are generated by walking `AuthMethod` and consulting an explicit classification table rather than by iterating anything; `SessionService` reads its bounds from the repository and has no policy argument; and an unclassified authentication method refuses at import and at construction instead of inheriting the shorter window. Evidence is TC-AUTH-19(k), 392 portal and 2260 bot tests with no skips, and recorded before/after reproductions of F1, F2 and F3. Resolution now additionally requires that the type carrying the accepted numeric bounds be **unconstructible outside the register**, that no object consumed by the refresh SQL be caller-supplied or overridable, and that a service/repository graph admit only one bounds source. **Amended a fifth time 2026-08-15 (session-bounds-construction re-review): that remediation was also incomplete, in one way, reported from two perspectives.** Codex's independent implementation review (Blocking F1) and its distinct security-focused pass (Blocking S1) describe **one** defect: `SessionSettings.__post_init__` required each registered number to be an actual `int` excluding `bool`, positive and within its ceiling, while the derived-policy gate restated the rule as the two ordering comparisons `value < 1` and `value > ceiling` and dropped the type half. `float("nan")` makes both comparisons false, so it survived `SessionPolicy.derive()` as `max_sessions_per_account`, and `len(live) >= maximum` in `_enforce_session_limit` was then false for **every** live-session count — **N-66 revoked nothing and the per-account live-session bound was inoperative.** It was reachable through the supported repository constructor with no `object.__new__`, no mutation of a frozen instance, no forged `SessionPolicy` and no private helper, because `derive()` deliberately accepts `SessionSettings` subclasses and a subclass whose inherited `__post_init__` observes the valid stored integer may answer differently on the single later derivation read. Corrected in `docs/review/phase-3-p3-1-od-44-session-policy-numeric-validation-remediation-submission.md` by making the rule **one authoritative definition** rather than a third restatement: `session_policy_problem`/`session_policy_problems` sit beside `SESSION_CEILINGS` in `application/web/config.py`, and both `SessionSettings.__post_init__` and `_validate_policy_values` in `application/web/sessions.py` — the function `SessionPolicy.__post_init__` and `SessionPolicy.derive()` both go through — call it. Refusing anything that is not an `int`, and never a `bool`, covers floats as a class: integral-looking, fractional, infinite and NaN alike. Evidence is TC-AUTH-19(l) and TC-SESS-08b, 420 portal and 2260 bot tests with no skips, and a recorded falsification run in which nine of the new cases fail against the reviewed implementation while the whole pre-existing 54-test lifetime suite stays green — the suite contained no counterexample. No accepted numeric value changed and no schema or migration change was required. Resolution now additionally requires that every registered session-policy number have **exactly one runtime definition of its accepted type and range**, called by every construction and derivation gate, and that the value validated during derivation be the value stored in the policy and used by repository and service behaviour. **Amended a sixth time 2026-08-15 (settings-construction remediation): that remediation was also incomplete, in one way.** Making the rule one authoritative definition was correct; the definition itself still stated the type half as `isinstance(value, int) and not isinstance(value, bool)`, which refuses `bool` and every float and admits **every other subclass of `int`**. An `int` subclass may override `__lt__`, `__gt__`, `__le__` and `__ge__`, and Python gives the right-hand subclass's reflected comparison priority, so `len(live) >= maximum` is answered by the subclass. `dataclasses.replace(VALID_SESSION_SETTINGS, max_sessions_per_account=LyingInt(10))` therefore survived settings construction **and** `SessionPolicy.derive()`, and `_enforce_session_limit` saw false for every live-session count — **N-66 inoperative for the third time**, through the supported public constructor with no `object.__new__`, no frozen-object mutation, no private helper, no forged policy and no skipped `__post_init__`. Corrected in `docs/review/phase-3-p3-1-settings-construction-validation-remediation-submission.md` by stating the accepted type as the **exact** built-in `int` — `type(value) is int` — in the one definition both gates call, which is now `policy_number_problem`, shared with every other settings type in the register. Evidence is TC-AUTH-19(m): every registered field at both construction routes, both policy construction routes, the derivation gate with the read count asserted, the repository constructor, a falsification control showing the old predicate admitting the value, and eleven logins against real PostgreSQL leaving ten live sessions with the oldest durably revoked. 16 of the 22 new cases fail against the reviewed predicate while the whole pre-existing 28-case module stays green — it contained no counterexample. No accepted numeric value changed and no schema or migration change was required. Resolution now additionally requires that the accepted integer type be the **exact built-in `int`**, stated once and called by every construction and derivation gate, so that no subclass can answer a comparison the enforcement depends on **Amended 2026-08-16 (canonical settings-graph remediation): the same shape, one level above the session types.** The corrected session gates read whatever object their construction site handed them, and the composition root handed on the caller's outer `WebSettings` — so the graph whose numbers had been validated and the graph a service later re-read were not required to be the same object. The session bounds are now derived from the process's one canonical graph, and `OAuthLoginService` and `BreakGlassService` refuse anything else. See I-10's 2026-08-16 amendment and `docs/review/phase-3-p3-g1-canonical-settings-graph-remediation-submission.md`. **Amended again 2026-08-16 (provider/engine authority remediation): that remediation was incomplete in three ways, all the same shape.** The canonical graph was correct and the *dependencies derived from it* were not: the composition still accepted a `provider_double: IdentityProvider` refusing only a concrete `DiscordIdentityProvider` — a structural protocol, so a wrapper or delegating adapter holding a second graph passed and served R-03 and R-04; `WebComposition.provider` stayed publicly assignable while `create_app` checked it once and both routes dereferenced it per request, so an already-built application could be made to authenticate through an unvalidated graph (reproduced before the fix); and `WebComposition(settings=A, engine=B)` accepted any engine, making the configured database selection ignorable rather than singly-read (also reproduced). Corrected in `docs/review/phase-3-p3-g1-provider-and-engine-authority-remediation-submission.md` by removing both parameters, deriving the engine and provider from the canonical graph through two protected hooks whose only overrides live in `tests/`, making `settings`, `engine` and `provider` write-once behind read-only properties, binding the routes to the composition the factory accepted, stating engine ownership explicitly, and deleting `_require_provider_from()` rather than keeping a startup comparison that could detect nothing. Evidence is TC-STRUCT-09, 663 portal and 2260 bot tests with no skips, four falsification runs and two before/after reproductions. Resolution now additionally requires that every infrastructure dependency a web process uses be **derived** from its canonical graph or arrive through a declared protected hook with stated ownership, and that no process-lifetime dependency be replaceable after the application that validated it was built. **I-09 remains OPEN**; nothing here is accepted. **Amended 2026-08-16 (third, request-authority and lifecycle re-review).** The lifecycle half of the correction held for a normal shutdown only. `create_app()` ran `run_resource_checks()` at factory time, after the composition had already built the identity provider's HTTP client and its owned SQLAlchemy engine, so a refused startup raised out of the factory: no application was returned, no ASGI lifespan could execute, and neither resource was released on the one path where the process was being told not to run — the same "the claim is true of the method, not of the process" shape as the finding it was correcting. The checks now run inside the lifespan that owns the exact accepted composition, so a refusal is an ASGI startup failure that still closes the provider exactly once and disposes an owned engine exactly once while leaving a lent one alone, and the original typed `ConfigurationError` is what surfaces. `WebComposition.__init__` additionally disposes an engine it built when a later construction step raises, because no composition exists on that path for anything else to release it. Evidence is TC-STRUCT-10 and TC-STRUCT-11, 694 portal and 2260 bot tests with no skips, and six falsification runs restored byte-for-byte. Resolution now additionally requires that a composition owning process-lifetime resources release them on **every** exit — normal shutdown, refused startup and partial construction — not only the one a test happened to drive. **Amended 2026-08-16 (fourth, composition-lifecycle re-review): that lifecycle contract was complete in one direction only.** `aclose()` is permanent — it closes the provider's HTTP client and disposes an owned engine — and the lifespan asked nothing on the way *in*, so a composition passed to two applications, or one application whose lifespan was entered again, answered `lifespan.startup.complete` and began serving with a closed Discord client behind R-03 and R-04. The resource checks were no defence and could not become one: they never receive the provider, and `Engine.dispose()` discards a pool rather than invalidating an engine, so S-14 connects through the replacement and reports health for a resource nobody may use. **The suite had codified the unsafe outcome**, requiring `lifespan.startup.complete` from a second lifespan over a closed composition under the name of repeated-shutdown idempotency — an assertion about the wrong operation. This is I-09's shape in its lifecycle form: release one way, admit the other, with the correct exit making the entry look already handled. Corrected by an explicit one-way `CompositionLifecycle` (`new -> started -> closing -> closed`) claimed by exactly one application startup, refusing with `CompositionLifecycleError` before the resource checks and before any request is served, outside the cleanup `try` so a refused application closes nothing belonging to a serving one, and with `__setattr__` refusing every backward or sideways write so a spent composition cannot be reset and re-claimed. Evidence is TC-STRUCT-11 extended by addition, the codifying case corrected, six new cases over the real ASGI lifespan protocol, 707 portal and 2260 bot tests with no skips, and five killed falsification mutations plus one disclosed non-killing mutation, all restored byte-for-byte. Resolution now additionally requires that a one-way lifetime be guarded at **both** ends, and that an idempotency claim be checked for which operation it is actually repeating. Recorded in `docs/review/phase-3-p3-g1-composition-lifecycle-claim-remediation-submission-2026-08-16.md`. **I-09 remains OPEN**; nothing here is accepted. **Amended 2026-08-16 (fifth, distinct security review): the same shape twice, in the break-glass attempt budgets.** N-32's per-account WebAuthn budget was implemented, validated and unit-tested with **no production caller at all**, so assertions spread over fresh source addresses were bounded only per address; and N-33's per-grant recovery counter was incremented **inside** the redemption transaction that every refusal rolls back, so an attempt matching a real but expired, invalidated or consumed grant left the stored count untouched and the cap could be walked past from new addresses. The suite reported on the mechanisms rather than on a request: TC-LIM-06 called `check_account()` directly, and the per-grant case presented a token matching no row and asserted the count stayed zero — an assertion the defect satisfies. Corrected by spending both budgets in their own committed transactions before the unit of work they bound: the account budget after the presented credential is resolved and before anything is verified, with an equivalent keyed per-credential budget for unresolved credentials so the limit is not an account-existence oracle; and the per-grant attempt through a service method that **returns** its refusal instead of raising it, because raising inside the transaction is what destroyed the increment. `note_attempt()` is now one `UPDATE … RETURNING` statement. Evidence is TC-BG-16 and TC-BG-17 added by addition — both direct HTTP against real PostgreSQL, both spending their budget from several source addresses — the overstated per-grant case renamed and re-scoped, 712 portal and 2260 bot tests with no skips, and four killed falsification mutations restored byte-for-byte. Resolution now additionally requires that **an attempt counter be spent in a transaction that commits whether or not the attempt succeeds**, and that a limit's evidence show a request reaching it rather than the limiter counting correctly when called. Recorded in `docs/review/phase-3-p3-g1-security-review-remediation-submission-2026-08-16.md`. **I-09 remains OPEN**; nothing here is accepted. |
| I-08 | The traceability contract requires direct-HTTP evidence for TC-BG-05b and the HTTP halves of TC-BG-05c and 05e, against R-33, R-34 and R-38 — routes that belong to P3.2 and are absent from P3.1 by design, behind the very gate that evidence would support | Technical Lead / Independent Reviewer | Preserve P3.G1 service/constraint evidence and execute the direct-HTTP portions against the real P3.2 routes before P3.G2 closes | **Decision closed 2026-08-14; HTTP evidence transferred as a P3.G2 blocker.** Peter approved reallocation, not waiver. No early P3.2 route is authorized. |
| I-10 | Five public `WebSettings` sub-dataclasses (`RateLimitSettings`, `BoundsSettings`, `WebAuthnSettings`, `DatabasePoolSettings` and `WorkerSettings`) trust numeric and related policy values validated only by the environment reader; direct construction, `dataclasses.replace()` and subclass reads can therefore create values outside the accepted register that downstream consumers trust | Technical Lead / Security Reviewer | Before each affected consumer's package gate, inventory every accepted field and consumer; give each policy exactly one runtime type/range/relationship definition; enforce it at every public construction and derivation boundary; require exact built-in integers with `type(value) is int` where the contract says integer (not `isinstance`, which admits comparison-overriding `int` subclasses); validate the exact locals subsequently stored/used; and add direct-construction, `replace`, subclass, consumer-behaviour and falsification tests. Complete independent implementation and distinct security review for rate limits, request/proxy/membership bounds and WebAuthn; complete availability review for pool and worker bounds. | **Open — documented 2026-08-15 for later scoped remediation; not fixed by the session-policy package.** Ordinary `WebSettings.from_environment()` currently parses and bounds these fields, so this is not evidence of an environment-string bypass. It is the same construction-boundary shape previously demonstrated for session settings and must not be dismissed merely because production composition normally uses the environment factory. Priority by impact: rate limits, bounds and WebAuthn are security-sensitive; database-pool values are availability-sensitive; worker values are latent in P3.1 except for `enabled` but become mandatory before P3.3 activates worker behavior. See `docs/review/phase-3-settings-construction-validation-gap.md`. **Remediated 2026-08-15; remains OPEN pending fresh independent implementation review, a distinct security-focused pass, an availability review of the pool and worker bounds, and maintainer acceptance.** Implementation and evidence are recorded in `docs/review/phase-3-p3-1-settings-construction-validation-remediation-submission.md`: every field of the five types has one runtime `PolicyBound` beside the register it comes from, read by both the environment reader and the type's `__post_init__`; contract integers require an **exact** built-in `int` (`type(value) is int`), which is the same rule and the same function the corrected session gate uses; the accepted non-numeric shapes are enforced with them; N-21's default-cannot-exceed-maximum is enforced at the object owning both fields from one read of each; every seam that re-reads a settings value (engine composition, limiter, application composition, break-glass construction, startup health view) reads each attribute once, validates that read and holds the base type afterwards; and the environment boundary still aggregates every problem into one redacted `ConfigurationError`. Evidence is TC-STRUCT-07 and TC-LIM-06, 587 portal and 2260 bot tests with no skips, and a falsification run in which 81 of the 145 new cases fail against the previous reader-only model while all 442 pre-existing portal tests stay green. **Honest limits, carried into the review:** N-09/N-10 have no P3.1 route consumer and N-21/N-22 have none at all, so their consumer evidence is an obligation of the package that adds the consumer; `WEB_WEBAUTHN_USER_VERIFICATION` and `WEB_RECOVERY_GRANT_MINUTES` are validated but read by no runtime consumer (the assertion path hard-codes N-60's `required`, and `tools/emergency_recovery.py` uses its own N-14 constant); the worker's lease, heartbeat, attempt, timeout and queue consumers are P3.3's; and no ordering relationship between N-23's lease and heartbeat is enforced, because no accepted document states one — an open question for the maintainer rather than a policy decision taken in a constructor. **Amended 2026-08-15 (N-23 exact-lease remediation), correcting the previous sentence.** Independent review found the remediation's N-23 entry wrong: it defined the worker lease as `PolicyBound(minimum=1, maximum=60)`, treating the accepted "60 seconds" as a ceiling, when the accepted row states a lease **value** of 60 seconds and a heartbeat **maximum** of 20 seconds — the reading SM-05's `now() + 60s`, the logical schema's claim/renewal statements and the operational contract's `N-23 + N-44` recovery bound all take. The runtime entry is now `PolicyBound(minimum=60, maximum=60, policy="N-23")`; `heartbeat_seconds` is unchanged at 1…20; no accepted value, variable name, state machine, schema, migration, route, service, worker behaviour or deployment topology changed, and `.env.example` already shipped `WORKER_LEASE_SECONDS=60`. **The open question recorded above is withdrawn, not answered:** `lease_seconds=1, heartbeat_seconds=20` was never inside the accepted register, so it was never evidence that an ordering rule was missing; with the lease exactly 60, every accepted heartbeat is already far inside it, **no ordering rule was added, none is needed, no relationship involving N-45 has been accepted**, and nothing about N-23 blocks P3.3 — what P3.3 still owns is the worker consumers' evidence. Evidence is TC-STRUCT-07 and TC-LIM-06 as corrected, with 20 further cases (10 of which fail against the previous `1…60` entry) in `tests/web/test_settings_construction_validation.py`; 607 portal and 2260 bot tests pass with no skips. Recorded in `docs/review/phase-3-p3-1-n-23-exact-lease-remediation-submission.md`. **I-10 remains OPEN**: this correction is submitted for review and changes nothing about the outstanding independent implementation review, distinct security-focused pass, availability review of the pool and worker bounds, or maintainer acceptance. **Amended 2026-08-16 (canonical settings-graph remediation): the type-level correction was right and did not reach the process level.** Making each type valid by construction, and making selected consumers rebuild the one nested object they used, left a web process able to hold **two** individually valid graphs and use each in different places: `WebComposition` retained the caller's `WebSettings`; `create_app(settings_a, composition=composition_b)` gave middleware, cookies, digests and startup checks A while every service used B; `OAuthLoginService` and `BreakGlassService` re-read `session.oauth_transaction_minutes` and `encryption.active_version` from whatever they were handed; and the composition accepted a ready-made identity provider, so a genuine `DiscordIdentityProvider` built from valid graph B — B's client id, client secret, redirect URI, scopes, guild id, endpoints and timeout — could serve R-03's authorization URL and R-04's token exchange for an application that had validated graph A. None of it needed private mutation, `object.__new__` or an unsupported API. Remediated by removing the second authority rather than comparing the two: `canonical_settings` descends the declared `CANONICAL_SETTINGS_GRAPH`, rebuilding exact base types at every depth from one read of every field; the composition root canonicalises once and is the process's only configuration authority; `create_app` takes exactly one authority; retaining consumers require the canonical object; the Discord adapter is **built by the composition** from its own `settings.discord` and a real provider cannot be injected, while a test double and an HTTP transport still can; an undeclared settings type now fails closed instead of being canonicalised as a leaf; and the declared graph's completeness is proved against a topology derived from the dataclasses' annotations rather than from the mapping itself. Evidence is TC-STRUCT-08 in `tests/web/test_canonical_settings_graph.py` (46 cases), 653 portal and 2260 bot tests with no skips, and four recorded falsification runs. Recorded in `docs/review/phase-3-p3-g1-canonical-settings-graph-remediation-submission.md`. **Amended again 2026-08-16 (provider/engine authority remediation): "including the identity provider" was stated and not established.** The provider was built by the composition, and a `provider_double: IdentityProvider` parameter remained beside it refusing only the concrete Discord adapter; because `IdentityProvider` is a structural protocol, a wrapper or delegating adapter carrying a second graph's client id, secret, redirect URI, scopes, guild and endpoints passed that exclusion. The provider was also publicly assignable after `create_app` had checked it once, and the engine was still accepted whole — so the database the canonical graph selects could simply be ignored. Corrected by removing both parameters, deriving both dependencies from the canonical graph, and making the three process-lifetime objects write-once behind read-only properties; test substitution is a `WebComposition` subclass in `tests/web/composition_harness.py` reached by overriding two protected hooks, which no production module imports. Recorded in `docs/review/phase-3-p3-g1-provider-and-engine-authority-remediation-submission.md`. **I-10 remains OPEN**, and the requirement is now additionally that a web process have exactly one settings authority at every production configuration boundary, that the identity provider and the database engine be **derived** from that authority rather than supplied, that neither be replaceable for the life of the process, and that the declared graph's completeness be checked independently of the declaration. **Amended 2026-08-16 (third, request-authority and lifecycle re-review).** The canonical graph was still dereferenced per request through `request.app.state.settings`, which gave an already-validated application a second complete settings graph to serve from through one ordinary assignment; the factory now builds one frozen `RequestAuthority` from the graph it accepted and every route and the exception handler read from that object, with the four `app.state` references diagnostic only and proved inert. The same object is what the resource checks are evaluated against, now that they run inside the application's lifespan, so the configuration S-12/S-14/S-15 check is the configuration the application serves from **by identity** rather than by agreement. Recorded in `docs/review/phase-3-p3-g1-request-authority-and-lifecycle-remediation-submission.md`. **I-10 remains OPEN**, and the requirement is now additionally that the canonical graph be **held** by the objects that use it rather than looked up per use, and that no production request or startup path resolve a process-lifetime authority through a mutable application-level namespace. **Amended 2026-08-16 (fourth, test clock authority): the evidence carried the same shape as the code it was proving.** The re-review of the third amendment found that `tests/web/test_canonical_settings_graph.py` injected a clock captured at **module import** while `oauth_transactions.created_at` is stamped by `repositories.utcnow()` and `webauthn_challenges.created_at` by PostgreSQL's `server_default = now()`, with `expires_at` derived from the injected instant and two check constraints comparing them — two authorities, one row, and a result that depended on how much wall time elapsed before the case ran. The correction removes the second authority rather than widening the margin: each operation takes its instant from inside its own transaction and the repository's clock is bound to that same reading, so a row's expiry is exactly the accepted N-04 lifetime after that row's own creation. **No production file changed**, no accepted value moved, and both expiry constraints are now positively exercised by a regression that injects a deliberately stale instant and requires PostgreSQL to refuse the row. Recorded in `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`, which also declares — without acting on it — that `OAuthTransactionRepository.create()` re-reads the clock rather than deriving `created_at` from the operation's `now`; that is not observable as a production defect, because every production caller injects the same process clock microseconds earlier. **Amended 2026-08-16 (fifth, the AST evidence gap): the fourth amendment's own evidence claim was unsupported.** The clock submission's §3.1 said the absence of a module-level datetime was "asked of the AST", and no case in the module parsed it — the module did not import `ast` at all — so the property was established by reading and then described as established by a check. The absence was real and `OperationClock` was unaffected, but the claim was false when made, which is I-10's shape one level further out: this time in a statement about a control rather than in the control. The claim is now made true rather than withdrawn — a regression parses the module and fails if any code that runs at import reads or constructs an instant, falsified against a reintroduced `datetime.now(timezone.utc)`, a fixed module-scope `datetime(...)` constructor, a capture hidden in a default argument and an uncalled `datetime.now` alias, with each mutation restored byte-for-byte. **No production file changed**, no accepted value moved, no dependency was added, and `OperationClock`, N-04's lifetime and both live expiry constraints are untouched. The detector's name-based limit is declared rather than papered over. Recorded in §10 of `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`. **I-10 remains OPEN.** **Amended 2026-08-16 (sixth, the detector's own scope): the check added by the fifth amendment was narrower than the invariant it announced.** It reported "any code that reads or constructs an instant while the module is imported", but its `visit_Lambda()` always skipped the lambda body, so `NOW = (lambda: datetime.now(timezone.utc))()` — whose body executes during the import — was reported clean, and the stated reason ("a lambda body runs only when a test calls it") held for a stored lambda and not for an invoked one. That is I-10's shape inside the control this time rather than in a claim about it: a check whose declared scope and actual scope differ. Corrected by deciding a lambda on **when its body runs** — walked when the source shows it invoked in place, including the curried `(lambda: lambda: ...)()()`, excluded when it is stored, returned or passed, with defaults walked in both cases — leaving function and method bodies, imports, annotations, class bodies, decorators, `timedelta` and `timezone` untouched. Falsified against the invoked form and the curried form, both reported at their `datetime` source line, and against a **stored** lambda reading the same clock, correctly not reported; the pre-correction detector is recorded reporting nothing for the same input; every mutation was restored byte-for-byte. **No production file changed**, no accepted value moved, no dependency was added, and every previously accepted example still produces no finding. Resolution now additionally requires that a structural guard's declared scope be falsified against the constructs it claims to cover, not only against the ones that have already occurred. The remaining limits are declared: the detector is name-based, and a lambda called through a variable is outside it. Recorded in §12 of `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`. **I-10 remains OPEN.** **Amended 2026-08-16 (seventh, the corrected control's own reach): the sixth amendment's rule was right and its recognition of that rule was not.** It declared that a lambda invoked where it is written is decidable from the AST "with no name resolution", but `_invoked_lambda()` recognised only an `ast.Lambda` or a chain of `ast.Call`, so `NOW = (reader := lambda: datetime.now(timezone.utc))()` and its curried form ran their bodies during the import and were reported clean — neither of them requiring a separately stored name to be resolved. That is I-10's shape again, this time in a claim about how far a corrected control reaches: the claim was checked against the constructs already raised rather than the constructs it announced. Corrected by reading a callable position **through** an `ast.NamedExpr`, which evaluates its operand and answers that same object to the call beside it, while the target and the lambda's defaults stay in the ordinary walk so nothing previously reported disappears. Falsified against both reproducers — the new case proved failing first, reporting `[]` for both under the pre-correction helper — against the real module at line 119, and against a stored-then-called-by-name control that is correctly **not** reported and is declared a live false negative rather than coverage; every mutation restored byte-for-byte. **No production file changed**, no accepted value moved, no dependency was added, and every previously accepted example still produces no finding. Resolution now additionally requires that when a control's *reach* is claimed — not only its scope — the claim be falsified against the constructs it names, and that any construct deliberately left outside be asserted as a case rather than described. Two such limits are declared: a lambda called through a name in a later statement, and a lambda reached through a **selection** in a callable position. Recorded in §14 of `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`. **I-10 remains OPEN.** **Amended 2026-08-16 (eighth, the boundary beside the corrected control): the seventh amendment's declared limit was wider than the fact it rested on.** It excluded every selection in a callable position on the ground that "the source does not say which body runs", and that closing it would need a set-valued analysis. Both are true of `if flag` and false of an AST literal: `NOW = ((lambda: datetime.now(timezone.utc)) if True else (lambda: None))()` captures an instant at import and the AST names the branch that runs, so one body is decidable from the one node. The detector reported it clean because `_invoked_lambda()` did not handle `ast.IfExp` at all, and the control that was offered as evidence for the limit used a **name** as its test, so it never exercised the claim it was cited for. That is I-10's shape once more, this time in a declared *limit*: the exclusion was justified by the construct already raised rather than by the constructs it named. Corrected by selecting the reachable branch of an `ast.IfExp` whose test is an **exact** boolean literal (identity, so a name, a comparison, a boolean operator and a merely truthy constant are all untouched) and by walking the conditional as Python evaluates it — the test always, and only the selected branch when it is decidable, so a capture in the dead branch is not reported while the selected branch's defaults still are. Falsified against both literal positives at line 119 of the real module — the literal-`False` run corroborated by CPython's own `utcnow() is deprecated` warning at that line — and against the preserved name-conditioned selection, correctly **not** reported and still declared a live false negative; every mutation restored byte-for-byte. **No production file changed**, no accepted value moved, no dependency was added, and every previously accepted example still produces no finding. Resolution now additionally requires that a declared *limit* be falsified against the constructs it excludes, not only against the one that prompted it, and that any exclusion resting on undecidability be stated for the exact condition that makes it undecidable. Recorded in §16 of `docs/review/phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`. **I-10 remains OPEN.** |
| I-11 | The accepted schema names no table for the administrator's snapshot folder selection, and the table the selection would naturally belong to is append-only | Technical Lead | An accepted representation, or acceptance of the one P3.3 built | **Closed 2026-08-19 by Peter/Acceptance Authority; change-log C-P3.3-J.** `snapshot_folder_selections` is accepted as the authoritative current representation: one live row per snapshot, mutable and versioned, whose history remains the append-only `snapshot.folder_selected` audit event. The append-only protection on `foundry_snapshots` is unchanged; no data-authority, authorization, privacy, migration or rollback strategy changes were accepted |
| I-12 | `WebSettings.from_environment` refused `WORKER_ENABLED=true` unconditionally, so a worker process could not read its own configuration | Technical Lead | A process-aware refusal that preserves S-11 for the web process | **Closed 2026-08-18 by P3.3** — S-11 is a statement about the *web* process and was enforced at the one environment reader, which was correct while there was one process and wrong the moment there were two. It is now **symmetric rather than relaxed**: `from_environment(..., process=ProcessRole.WORKER)` refuses `WORKER_ENABLED=false` under the same `S-11`, the default stays `WEB`, every existing caller is unchanged, and each process refuses the other's value. `test_p3_3_worker.py` exercises both directions and asserts neither refusal echoes the value |
| I-13 | The Phase 2 apply service never set `snapshot_imports.actor_account_id`, so a portal-applied import recorded only a Discord snowflake | Technical Lead | New rows carry the account, without changing the accepted atomic boundary | **Closed 2026-08-18 by P3.3** — schema §11 and ADR 0010 D1 require new rows to carry the stable account, and a P3.3 apply that named only a snowflake would write exactly the legacy-only shape the identity migration is retiring; R-47's receipt would have rendered it as an unattributed bootstrap. `SnapshotImportService.apply` gains a **keyword-only `actor_account_id` defaulting to `None`**, so the Phase 2 operator path and the supervised bootstrap are untouched. It is *recorded*, never trusted: authority is still resolved through the `AuthorizationPort` from the Discord identity at the moment of the commit |
| I-14 | P3.3 fenced the *publication of a job result* and left the **import effect** unfenced, so a cancelled, abandoned or reaped attempt could still commit characters, mappings, an import row and a success audit event | Technical Lead | An effect that cannot commit without the attempt's entitlement proved in the same transaction | **Closed 2026-08-18 by the P3.3 remediation** — raised as a blocking finding by the independent implementation review. `SnapshotImportService.apply` committed in one transaction and `WorkerRuntime` published the terminal state in a second; in the window between them a cancellation, a timeout self-abandon, a kill-switch self-abandon or a reaper requeue transitioned the job while the abandoned execution thread went on to commit. Uniqueness did not cover it: it prevents a *second* effect, not the *first* effect from a cancelled attempt. Migration `0012` adds `reconciliation_jobs.effect_committed_at`, written by the effect's own transaction; the cancellation request, the self-abandon and R-41/R-46's invalidation statements carry `AND effect_committed_at IS NULL`; the reaper's `FOR UPDATE SKIP LOCKED` skips a locked row. R-41 and R-46 were a **fourth** writer in the same window that the review's finding did not name; it was found while building the race suite and closed with the same predicate. Ten race cases (TC-JOB-17…26) assert the actual rows, and each was first shown failing against the pre-remediation code. Recorded as change-log `C-P3.3-B`; the SM-05 mechanism correction it needs is **proposed, not self-approved** |
| I-15 | The N-24 retention command could not run: its `UPDATE reconciliation_jobs SET result_id = NULL` violated `CHECK ((state = 'completed') = (result_id IS NOT NULL))` for every completed job, and it ignored the `parent_job_id … RESTRICT` graph | Technical Lead | A bounded, atomic, referentially safe sweep | **Closed 2026-08-18 by the P3.3 remediation** — also a blocking finding of the independent implementation review. Rewritten with **no schema change**: the pointer never needed nulling, because deleting the job cascades to its result and the `RESTRICT` on `result_id` is satisfied by the job's own deletion. The candidate set is locked `FOR UPDATE … SKIP LOCKED`, a recursive fixed point retains any graph a younger apply still needs, `failed`/`cancelled` jobs with no result row are now eligible on their terminal age (they were invisible to every earlier sweep), and `--limit` is refused before a connection is opened. Twelve real-PostgreSQL cases, TC-OPS-06…17 |
| I-16 | Both branches of R-45's cancel statement were needed, and only one carried the fence predicate, so a committed effect could be cancelled after the reaper requeued it | Technical Lead | A cancellation that refuses a committed effect whatever state the job is in, enforced at the write boundary | **Closed 2026-08-18 by the P3.3 effect-publication remediation** — raised as a blocking finding by the independent implementation and security re-review of the first remediation. The `queued` branch matched `id = :job_id AND state = 'queued'` alone, and the reaper deliberately requeued a job whose effect had committed but whose result had not been published, so this interleaving existed: apply commits → process dies → lease expires → reaper writes `queued` → R-45 cancels a job over a durable import. Fixed at the **write boundary**, not with a preceding read: both branches carry `AND effect_committed_at IS NULL`, `fail`, `cancel_under_lease` and `mark_stale_under_lease` gained the same predicate, and migration 0013's `CHECK (effect_committed_at IS NULL OR state NOT IN ('failed','cancelled','stale'))` refuses the row whatever statement writes it. The route now answers the truthful `409` with VM-19's `already_applied` — derived from the typed `Cancellation` rather than guessed from a state that says `running` — and **writes no audit event claiming a cancellation was requested** |
| I-17 | A committed effect could become `failed` with `attempts_exhausted` on attempt three, because the reaper chose its branch from `attempts` alone (the condition RR-16 recorded as accepted) | Technical Lead | An explicit recovery outcome that publishes the effect's result truthfully, without a fourth attempt | **Closed 2026-08-18 by the P3.3 effect-publication remediation** — the second blocking finding of the same re-review, and the reason RR-16 is withdrawn rather than carried. Neither reaper branch can describe a committed effect: one retries an attempt that already succeeded, the other declares it exhausted. Migration 0013 adds `reconciliation_jobs.effect_result`, which the **commit fence writes in the same statement as `effect_committed_at`**, so the bounded result the run produced becomes durable if and only if the effect does. The reaper's locking sub-select gains `AND effect_committed_at IS NULL`; `lock_unpublished_effect` takes the rest under `FOR UPDATE SKIP LOCKED` and one transaction inserts the result, completes the job and records the completion event. The summary is read from `effect_result` and the immutable `snapshot_imports` receipt — never recomputed against the database as it stands, never from a caller — which is Phase 2 finding B-1R's rule applied to the job's result. **No artifact is re-parsed, no authority re-resolved, no lease minted and `attempts` untouched, so N-43 is neither spent nor disguised.** A seventh state `recovering` was considered and rejected: the publication is one transaction under the row lock, so no distinguishable state is observable. Twenty-one real-PostgreSQL cases in `tests/web/test_p3_3_effect_recovery.py`. Recorded as change-log `C-P3.3-C`; the SM-05 amendment it needs — one added transition, two forbidden transitions, one column — is **proposed, not self-approved** |
| I-18 | Migration `0013` could not round-trip a database that had processed a normal apply: `downgrade 0012` destroyed `effect_result` and kept `effect_committed_at`, so `upgrade 0013` then refused on every truthfully completed apply and the database was stranded one revision below head | Technical Lead | A truthful, recoverable migration strategy, proved against real PostgreSQL with realistic rows | **Closed 2026-08-18 by the P3.3 migration-rollback remediation** — the blocking finding of the independent review of `C-P3.3-C`, whose rollback evidence exercised only an **empty** schema. The commit fence writes `effect_result` inside the effect's own transaction and `ck_…_effect_result_accompanies_the_fence` makes the pair inseparable, so dropping the column destroys a payload nothing may truthfully reconstruct: `snapshot_imports` is the *import's* receipt and holds no blocked create-candidate list, no `{code, severity, count}` issue counts, no `would_create`/`would_update` and no `selected_folder_path`. `downgrade()` now **refuses before any schema change** while any **retained** job records a committed import effect — becoming available again once no such job survives, which in normal operation means approved N-24 retention has removed every completed committed-effect job and its result and no committed-but-unpublished job remains (predicate corrected 2026-08-19; the closure wording originally read "once any job records a committed import effect", which described a historical event the guard does not record) — counting the `completed` and committed-but-unpublished populations separately and naming the operator's action; offline (`--sql`) scripts carry the same guard as an executable `DO … RAISE EXCEPTION` block, because `DROP CONSTRAINT`/`DROP COLUMN` succeed against any data and a comment is not a control. **No constraint weakened, no invariant amended, no history deleted, no grant changed.** Seven real-PostgreSQL cases, TC-MIG-24…TC-MIG-30, every committed effect produced by the production apply path; all failed against the pre-remediation migration first. Recorded as change-log `C-P3.3-D`; the **operational rollback contract** it implies is proposed rather than self-approved — see D-09 |
| I-19 | TC-MIG-37, the mandatory held-lock concurrency regression added by the third migration-rollback correction, did not identify the ungranted `RowExclusiveLock` it asserted on as belonging to its own fence writer: it polled every ungranted request of that mode on `reconciliation_jobs` and asserted only that the migration holder's pid was absent, so an unrelated queued session could satisfy it while the intended writer had not yet requested any lock | Technical Lead | The committed assertion binds the observed lock to the writer's own backend **and** transaction, and fails deterministically when only an unrelated session is queued | **Closed 2026-08-19 by the P3.3 fourth migration-rollback correction.** Major finding of the independent review of `C-P3.3-F`. **Not a timing flake** — the assertion was wrong about what it identified, and passed only because the disposable database is quiet enough that the intended writer normally wins the race. The writer now announces its PostgreSQL backend pid over a bounded queue from inside its own transaction before issuing any production statement; the poll is scoped `AND l.pid = :pid` and additionally requires `pg_stat_activity.query` to be the production `hold_for_effect` fence rather than `seed_import`, connection setup or an unrelated statement; and the transaction identity observed while the request is queued (`pid`, `virtualtransaction`, `backend_xid`, `xact_start`) is re-observed, still open and uncommitted, on the transaction that then commits the fence. Falsified deterministically: with the writer held before its fence and only an unrelated session queued, the old predicate is satisfied and the corrected one cannot be. **No production change** — no migration, module, emitted statement, grant, constraint or retention rule was touched, and no production pause hook exists. The queue-fairness case (TC-MIG-32) keeps its deliberately broader observation and every assertion it had. Recorded as change-log `C-P3.3-G`; submission §17 |
| I-20 | TC-MIG-37's failure-path cleanup was unbounded: its `finally` block killed a surviving migration subprocess and then called `migration.communicate()` with no timeout, so a stall in process termination or pipe collection could hang cleanup indefinitely — before the externally held `alembic_version` row lock was rolled back, before the holder connection was closed and before the fence writer was joined | Technical Lead | A single ordered release that is bounded on every assertion-failure path, leaves no live migration child, blocked writer, open writer transaction or holder row lock, and reports a cleanup problem without replacing the assertion under diagnosis | **Closed 2026-08-19 by the P3.3 fifth migration-rollback correction.** Major finding of the independent review of `C-P3.3-G`, which accepted the writer-identity remediation as sound. **Not a flake and not a timing defect** — the passing case never executes the defective path, which is why the reviewer's passing runs did not close it. Every resource the case holds is now owned by one test-local object whose `release()` runs on every exit path in a fixed order: release the writer's commit event; end and boundedly reap a surviving migration child **before** releasing the `alembic_version` row lock, so a *released* rather than *ended* migration cannot commit its drops and a writer queued behind its table lock is freed; roll back the row lock; close the holder; then join the writer, bounded, and only if it was started and is still alive. The reap kills and collects with an explicit timeout, twice, and never waits without one; a child surviving both is reported and stepped over rather than stranding the resources that are still releasable. `release()` never raises — its problems are attached to the failing assertion with `add_note()` instead of replacing it. The same bounded reap replaces the identical unbounded shape in the module's three sibling concurrency cases, and `_reap()`'s own post-kill collection is bounded too. Proved by TC-MIG-38…TC-MIG-41: a controlled assertion failure against real PostgreSQL at two named points, with the production revision and the production fence statement live, plus deterministic coverage of the timeout, pre-start and error-preservation branches. Falsified deterministically against the pre-fix `kill(); communicate()` shape; the mutation was restored by checksum and is not in the final tree. **No production change** — no migration, module, emitted statement, grant, constraint or retention rule was touched, and no production pause hook exists. TC-MIG-37's own requirement, assertions and scope statement are unchanged. Recorded as change-log `C-P3.3-H`; submission §18 |
| I-21 | `_HeldLockCleanup.release()` was **not** bounded on every path, contrary to the fifth correction's claim: its `seconds_ceiling` counted only the subprocess reap and the writer join, while the release also called `holding.rollback()` and `holder.close()` synchronously, with no enforceable timeout for either. A blocked rollback prevented the close and the writer join from being reached at all, and a blocked close prevented the writer join — leaving the externally taken `alembic_version` row lock live in the **shared** disposable `freedom_test` database, where it would contaminate every later case's evidence | Technical Lead | A release in which every wait is bounded and counted by the documented ceiling, every later step is attempted whatever an earlier one did, and any thread used to impose a bound is itself accounted for rather than hidden | **Closed and accepted 2026-08-19 by Peter/Acceptance Authority after distinct implementation and security-focused re-reviews; change-log `C-P3.3-I`.** Each database cleanup wait is bounded and counted; the holder is detached before threaded cleanup; orphaned calls are recorded and fail the case; and test-owned backend disposal is restricted by PID plus `backend_start`. TC-MIG-42…TC-MIG-44 provide deterministic rollback/close coverage, and the security review recorded 120 passing rollback, structural and rejected-scope tests. No production code, migration, grant, retention rule or caller-reachable path changed. The defective `C-P3.3-H` ceiling claim is not separately accepted |

## Residual risks recorded with the P3.3 remediation (2026-08-18)

| ID | Residual | Owner | Why it is accepted rather than closed |
|---|---|---|---|
| RR-16 | ~~A job whose effect committed and whose **third** lease then expires is failed by the reaper with `attempts_exhausted` while a valid import exists~~ | Technical Lead | **Not accepted. Closed 2026-08-18 as issue I-17.** The independent implementation and security re-review refused it as a residual risk, and was right to: `failed` over a durable import is a job denying something the database is holding, whatever the receipt says beside it. It is closed by an explicit recovery outcome rather than by a fourth claim — see I-17 |
| RR-17 | The commit fence holds the job row's write lock for the duration of the import's `COMMIT`, so the worker's own heartbeat and any concurrent cancellation block for that interval | Technical Lead | The fence is the **last** statement before the commit, so the interval is the commit and not the apply. The lease is 60 s (N-23) against a measured 9.566 s preview, and a blocked heartbeat that did expire is recoverable rather than a failure verdict. Not measured at the accepted 64 MiB bound, which is the same staging gap I-06 already records |
| RR-18 | A recovery publication that cannot succeed leaves the job `running` with a lapsed lease rather than writing `failed`, so `expired_lease_age_seconds` climbs until an operator intervenes | Technical Lead | Recorded with the 2026-08-18 effect-publication remediation. It is the design rather than a stall to force through: a durable import is **never** denied, and writing `failed` to clear an alarm is exactly the defect I-17 closed. Both causes — an unreadable `effect_result` and a missing `snapshot_imports` receipt — are rows migration 0013's constraints and the fence's single transaction make unrepresentable, so this is the behaviour of a fault rather than of an expected condition. The alarm is VM-16's own signal, the worker journal names the job and which durable half could not be read, and the runbook names the response |
| RR-19 | While any **retained** reconciliation job records a committed apply effect there is no supported schema rollback below revision `0013`, and there is no supported application version below the remediated one at `0013` at all, so a defect found while such a job is retained must be fixed by roll-forward. The boundary reopens only when no such job survives — approved N-24 retention having removed every completed committed-effect job and its result, and no committed-but-unpublished job remaining; a committed-but-unpublished job is `running` and never retention-eligible at any age. (Wording corrected 2026-08-19: this row previously read "past the first committed apply effect", a historical event the guard does not record. Retention is not a rollback technique — manual deletion, truncation, a shortened period and an early sweep are all unsupported.) | Technical Lead | Recorded with the 2026-08-18 migration-rollback remediation, and accepted rather than closed because the alternative — a sidecar object carrying the fence's payload across a downgrade — is a material new schema object with its own ownership and retention rules, and would add a second writer for a value whose single-writer property is what makes effect-publication recovery trustworthy. Two things bound it: revision `0013` is small (one nullable column, two check constraints), and `0013` running under pre-0013 code fails **safe** rather than corrupting — the old fence writes no payload, so the constraint aborts the import transaction and nothing commits. `docs/implementation-plan.md` §14.3 already requires roll-forward over editing an applied migration; this makes the consequence explicit for P3.3 |

## Dependencies

Phase 3 predecessor dependencies are closed for Phase 4. D-04 was Closed on
2026-08-29 when Peter approved the Phase 4 gate.

D-01 was split on 2026-08-02 into D-01a and D-01b. The single row conflated a
Phase 2 precondition with a per-package one and therefore made every future
vocabulary decision read as a Phase 2 blocker, which it is not: Phase 2
classifies and defers legacy fields, and migrates none of them. The split is a
clarification of dependency granularity, not a scope change; no register row,
package allocation or gate criterion is altered by it.

| ID | Dependency | Needed by | Owner | Satisfied when | Status |
|---|---|---|---|---|---|
| D-01a | Exhaustive snapshot classification, accountable legacy disposition, and proof that no interim editable Sheet-state representation exists | Phase 2 import only | Data Owner | Every supported snapshot path carries exactly one classification and an unknown path fails closed; every known legacy source/profile field has exactly one accountable owning package in the migration register/manifest and is reported as `legacy_authority_deferred` rather than compared; and no Phase 2 table, repository API or write path holds a second editable copy of a legacy Sheet field | **Closed 2026-08-12 with the accepted Phase 2 gate.** |
| D-01b | Readiness of each controlled vocabulary in `data-vocabulary-register.md` | Only the typed migration package that uses that vocabulary | Data Owner | For that package alone: source identity, version, alias/merge policy, licensing/provenance, retirement behavior, steward and unresolved-value workflow are decided and dated | Open per package. **Vocabulary readiness does not block Phase 2**, which classifies and reports legacy fields without migrating, normalizing or writing them |
| D-02 | Phase 2 data-integrity gate | Phase 3 | Acceptance Authority | Gate decision is approved | **Closed 2026-08-12.** |
| D-03 | Accepted visual prototype and stable view-model contracts | Phase 3 frontend | Product Owner / Technical Lead | Separate visual gate and backend contract approval close | **Closed 2026-08-20.** Visual gate accepted 2026-08-13. Peter accepted `C-P3.4-A` on 2026-08-19 and authorized the bounded backend correction; Claude implemented and submitted it as `C-P3.4-B`. The independent Codex implementation review and distinct security-focused review passed with no blocking findings. Peter/Acceptance Authority then accepted the corrected D-03 backend route/view-model contract and explicitly released the Gemini P3.4 implementation prompt (`C-P3.4-C`). The correction delivers M-01 `/static/`, the `ConfirmScope` and `CharacterFilters` definitions, accurate VM-13 CSRF and R-36 records, and VM-22 `DeniedView`; `VIEW_MODEL_VERSION` remains `vm-1`. P3.G4, I-06 and A-05 remain open, and no staging exposure, deployment, production use, live-service contact or real-player-data use is authorized. Evidence: `docs/review/phase-3-d-03-backend-contract-correction-submission.md` and `docs/review/phase-3-d-03-codex-reviews-and-acceptance.md`. |
| D-04 | Shared ledger/idempotency/domain foundations | Phase 5 mutations | Technical Lead | Phase 4 gate approved | **Closed 2026-08-29** |
| D-10 | Freedom bot retirement (plan §15.2, baseline v1.7, OD-53) — every migrated command's package gate, Phase 6 approvals, the Phase 8–11 behaviors the bot touches, §15.1's final Sheet retirement gate, and measured adoption against a pre-accepted threshold | Terminal; releases no successor work | Product Owner / Operations Owner | The bot-retirement gate is approved by the Acceptance Authority on Product Owner, Technical Lead, Operations Owner and Independent Reviewer recommendations | **Open.** Not on the current critical path. Deleting the bot as part of the website or database migration remains forbidden |
| D-05 | Catalogue and inventory foundations | Phase 5 crafting | Product Owner / Data Owner | Package 5.6a gate approved | Open |
| D-06 | Mission and attendance records | Phase 9 settlement | Product Owner | Phase 8 gate approved | Open |
| D-07 | Basic Bastion state | Phase 11 facilities | Product Owner | Phase 10 gate approved | Open |
| D-09 | Ratification of migration `0013`'s **operational rollback boundary** — that while any retained reconciliation job records a committed apply effect, rolling P3.3 back is application rollback or roll-forward rather than schema downgrade, and that the boundary reopens only when approved N-24 retention has removed every such job (restated 2026-08-18 by the second remediation; the earlier "forever after the first apply" wording was not what the guard enforces) | P3.G3 closure | Acceptance Authority | Peter/Acceptance Authority records a decision on change-log `C-P3.3-D`, `C-P3.3-E` and `C-P3.3-F` and on `docs/operations/web-portal.md` §3.6 | **Closed and accepted 2026-08-19 by Peter/Acceptance Authority; change-log C-P3.3-J.** While a retained reconciliation job records a committed apply effect, rollback is application rollback or roll-forward rather than schema downgrade below `0013`. The boundary reopens only under the documented N-24 conditions. The migration refusal and runbook consequence are ratified |
# V6 R4 accepted; LAB-V6-1 through LAB-V6-3 disposition — 2026-09-17

Peter accepted the independent R4 review and closed PR-20260916-LAB-V6R3-1.
The unreproducible R3 digest is not approved and is superseded by the
reproducible R4 artifact as review input only.

**LAB-V6-1 resolved by decision:** V11 and `/opt/freedom-blades/evidence` are
withdrawn; `/opt/freedom-blades` ownership is unchanged. **LAB-V6-2 resolved by
decision:** V12 explicitly owns creation of `/var/lib/freedom-blades` as
`root:root 0755` before V4/V5. **LAB-V6-3 resolved by decision:**
`/var/lib/fb-evidence-p5-0` is the sole canonical `R`, while production
`EVIDENCE_ROLE` registration is deferred to its separately reviewed real
consumer. These items are closed as decisions; their repository implementation
is returned for independent review and nothing is provisioned.
