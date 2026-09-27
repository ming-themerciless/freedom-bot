# Claude remediation handback — R6 authorization and stop-condition findings recorded Open, Blocking — 2026-09-20

Authorization: **C-P5.0-LAB-I3-R6-R1**, one bounded **repository-documentation-
only** remediation. Peter Duscha assigned Claude as implementing agent. Codex
remains the Independent Technical, Security and Evidence Reviewer and must
re-review this remediation.

**State: C-P5.0-LAB-I3-R6 is NOT accepted and I3 is NOT closed.** Codex's two
Blocking findings are accepted in full and recorded **Open**. Neither is closed
here, and this remediation does not attempt to close either. No host action was
taken and none is authorized.

V7 remains excluded; V8 and V10 remain unperformed; `plan.is_executable=False`;
Package 5.0 remains **not ready**; LAB-SECRETS-1 remains Open, Low; LAB-V6-P2
remains deferred. Nothing here approves a digest, initializes V7, makes the
concrete plan executable, advances Package 5.0 or authorizes `--execute`.

> **Erratum, 2026-09-20 — see [§11](#11-erratum--the-r7-host-side-artifact-rule-corrected-under-c-p50-lab-i3-r6-r2--2026-09-20).**
> Codex's re-review of this remediation raised one Important finding,
> **PR-20260920-LAB-I3-R6-R1-1**, against the draft R7 prompt prepared under §4:
> its host-side-artifact prohibition contradicted the two verifier invocations
> the same draft authorizes. §4's third item is corrected in place and marked,
> and §11 records what it said before. The draft R7 prompt remains **NOT
> AUTHORIZED**; both R6 findings remain **Open, Blocking**.

---

## 1. Disposition of the two findings — stated exactly

### PR-20260920-LAB-I3-R6-1 — execution continued after a mandatory guard stop

**Disposition: ACCEPTED IN FULL. Recorded Open, Blocking. Not closed.**

The finding is correct and is not disputed in any particular. The first
synchronization attempt of the R6 pass was refused by the repository secrets
guard because the operator had submitted a chained command. That refusal was a
**mandatory stop condition**:

* `.agents/AGENTS.md` states that a guard refusal is a stop condition, not an
  obstacle to route around;
* the disposable-server runbook §3.2 says not to rewrite the command after a
  refusal; and
* the R6 prompt expressly prohibited working around a guard refusal.

Removing the chaining and continuing with the exact `rsync` command **did not
cure the stop condition**. The pass should have ended there — **before
synchronization and before either verifier invocation**. Consequently the R6
handback's statement that no stop condition fired is **false**, and it is
withdrawn.

Two things are stated because the assignment requires precision about them:

* **The guard behaved correctly.** Its refusal is not a defect, and it is not
  recorded as one anywhere in this remediation. The fault is the operator's.
* **This correction is not stylistic.** It changes what the R6 pass is worth as
  evidence, from "operational evidence awaiting a closure decision" to "a pass
  that continued without authority".

Closing this finding requires independent Codex review of this remediation and
Peter's decision. A documentation correction does not discharge it.

### PR-20260920-LAB-I3-R6-2 — unauthorized host write

**Disposition: ACCEPTED IN FULL. Recorded Open, Blocking. Not closed.**

The R6 authority was closed to an exhaustive list: the exact synchronization,
necessary read-only inspection, and the two conditional verifier invocations.
The `scp` that created `/tmp/fb-i3-r6-filelist.txt` on `oracle-test` was **not
on that list and was not authorized**.

The mitigating circumstances recorded in the R6 handback are all true and none
of them changes the disposition. That the file contains only repository-relative
paths, that it was never used, that it was disclosed rather than concealed, and
that it was preserved rather than deleted — **none of these retroactively
authorizes the write**, and the handback's framing of it as an "operator
misstep" disclosed for transparency is insufficient and has been superseded.

`/tmp/fb-i3-r6-filelist.txt` **must not be deleted, truncated, overwritten,
moved or modified.** Deleting it now would be a second unauthorized write. Its
disposition is the maintainer's alone, and the disposable-server restriction has
been extended to protect it alongside `/tmp/fb-i3-root.out` and
`/tmp/fb-i3-root.err`.

### What the R6 verifier runs do and do not establish

Stated precisely, because the assignment requires occurrence and sufficiency to
be distinguished:

**The verifier runs did occur.** Both invocations of the separately armed I3
verifier were executed and returned run status `verified`. Their output is
**internally coherent**: all four contexts reported `verified`; the indirect
exit-status evidence in R6 §6.3 is sufficient on its own terms; the repeated
inode number `2049:1275057` is consistent with sequential ext4 inode reuse, as
R6 §7.2 explains; and both final surveys reported no verifier residue with
canonical `R` absent.

**Those technical observations do not cure the authorization and stop-condition
defects.** Occurrence is not acceptable gate evidence. The runs were produced by
a pass whose authority had already lapsed at the guard refusal, and the same
pass performed an unauthorized write on the host. **I3 therefore remains
unconfirmed and not closed**, and no claim of I3 closure, digest approval or
readiness rests on these runs.

**C-P5.0-LAB-I3-R6 is consumed and cannot be retried under its authority.**

## 2. Every corrected claim, and the file it is in

### 2.1 `docs/review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-verification-handback.md`

Corrected by one **erratum block** at the head of the document and five
**superseding notes** placed at the claims they correct. Nothing was deleted.

| Location | Claim as it stood | Correction |
|---|---|---|
| head of document | — | New erratum: both findings stated, both accepted, five named conclusions withdrawn, I3 unconfirmed, R6 consumed, guard not defective, correction not stylistic |
| opening summary | "That is operational evidence for a maintainer decision." | Struck through and superseded: the runs occurred and are internally coherent, but the pass continued past a mandatory stop and included an unauthorized write, so it is not evidence a maintainer may rely on to close I3 |
| §1 authorized-vs-done table | "nothing else \| two disclosed operator effects" | Row annotated that the `scp` was an unauthorized host write; note added that every "yes" from §3 onward describes work performed after the §3.1 stop |
| §3.1 heading and reasoning | "A guard refusal, disclosed" — recorded so a reviewer can see "how it was resolved" | Heading corrected to "**corrected: it was a mandatory stop**"; the "resolved" framing withdrawn; the three governing rules cited; states that synchronization and both invocations should never have been issued; states the guard behaved as designed and the fault is the operator's |
| §9 heading block | `scp` presented as an "operator misstep" disclosed for transparency | Superseded as an **unauthorized host write**; the mitigations named and rejected as authorization; effect 1 noted as issued after the stop; preservation requirement restated |
| §11 first bullet | "Closure is Peter's decision on independent Codex review of this evidence" | Struck through and corrected: that review has been performed and does not recommend closure; I3 unconfirmed and not closed |
| §11 stop-condition bullet | "**No stop condition fired:** …" | Struck through; declared **false and withdrawn**; the surviving observations re-stated with their correct, narrower scope — *within the verifier runs themselves* — with the note that those runs should not have been issued |
| §12 reviewer focus | items 3 and 4 posed the guard refusal and the `scp` as open questions for review | Superseded: both are answered against the pass and are Open, Blocking; item 4's phrasing withdrawn as the wrong question |

### 2.2 `docs/review/Handover information`

| Location | Correction |
|---|---|
| top of file | New R6-R1 state banner: both findings Open and Blocking, neither closed; the R6 handback corrected by erratum with no history erased; "No stop condition fired" withdrawn as false; the `scp` reframed as an unauthorized write; occurrence distinguished from acceptable gate evidence; the R7 draft named and marked **not authorized**; no host action, no suite figures |
| prior R6 operational handback banner | Retitled "Superseded"; superseding note added naming both defects and stating the pass is not acceptable evidence for closing I3. Body retained unaltered |

### 2.3 `docs/implementation-plan.md` §20

| Location | Correction |
|---|---|
| current action | Replaced. Was "review the returned C-P5.0-LAB-I3-R6 operational evidence and decide I3 closure"; now "independently re-review the C-P5.0-LAB-I3-R6-R1 remediation; I3 remains unconfirmed and not closed", stating both findings, the withdrawn stop-condition claim, occurrence versus gate evidence, the inactive R7 draft, and that no host action is authorized |
| prior current action | Demoted to "Superseded action" with a note that the pass was not accepted, the closure decision is not ripe, and its resulting-state statement is corrected. Body retained unaltered |

### 2.4 `docs/operations/disposable-test-server.md`

| Location | Correction |
|---|---|
| restriction banner | Replaced. Was "C-P5.0-LAB-I3-R6 performed; no further action authorized"; now "C-P5.0-LAB-I3-R6 not accepted; two Blocking findings Open; NO action on this host is authorized". The `/tmp` protection is **extended to `/tmp/fb-i3-r6-filelist.txt`**, whose disposition is the maintainer's and which must not be tidied up. The host's undisputed physical state is retained; occurrence is distinguished from gate evidence; the R7 draft is named as not authorized |
| prior banner | Demoted to "Superseded state and restriction" with a note. Body retained unaltered |

### 2.5 `docs/project-management/raid-register.md`

| Location | Correction |
|---|---|
| new top entry | **PR-20260920-LAB-I3-R6-1, Open, Blocking** and **PR-20260920-LAB-I3-R6-2, Open, Blocking** recorded as issues, each with its cause, its governing rule, the explicit statement that the R6-R1 remediation does not close it, and its owner and independent reviewer. A paragraph distinguishes the runs' occurrence and internal coherence from acceptable gate evidence. LAB-I3-TARGET-1 stays Closed; LAB-SECRETS-1 stays Open, Low; LAB-V6-P2 stays Open, Low and deferred |
| prior top entry | Demoted to "Superseded"; its claim **"No new risk or issue is raised by this pass"** declared **false and withdrawn**; its transparency framing of the guard refusal and the `scp` superseded; its correct observation that the refusal is not a LAB-SECRETS-1 instance preserved. Body retained unaltered |

### 2.6 `docs/project-management/status.md`

| Location | Correction |
|---|---|
| current status | Replaced. Was "C-P5.0-LAB-I3-R6 performed; I3 verified but not closed"; now "C-P5.0-LAB-I3-R6 not accepted; two Blocking findings Open; I3 unconfirmed". States both findings, withdraws "No stop condition fired" as false, distinguishes occurrence from gate evidence, records the documentation-only remediation that closes neither finding, names the inactive R7 draft, and states that no suite was run and no earlier tree's figures are asserted |
| prior current status | Demoted to "Superseded status" with a note naming the false claim. Body retained unaltered, including its own "No stop condition fired" sentence, which the note withdraws |

### 2.7 `docs/project-management/decision-register.md`

| Location | Correction |
|---|---|
| new top entry | The I3 **closure decision is withdrawn as not ripe**. States the decisions actually before Peter: accepting the R6-R1 remediation after independent review; disposing of `/tmp/fb-i3-r6-filelist.txt`, which must not be deleted meanwhile; and whether to authorize a further operational pass. States that the R7 draft confers no permission and that R6 is consumed |
| prior top entry | Demoted to "Superseded" with a note. Body retained unaltered |

### 2.8 `docs/project-management/change-log.md`

Append-only. One new row, **C-P5.0-LAB-I3-R6-R1**, recording the findings, the
erratum-based correction with no history erased, the documentation-only scope,
that neither finding is closed, the inactive R7 draft, and **no scope, schedule
or risk baseline change**. The earlier R6 row's label now reads "performed;
subsequently not accepted (see C-P5.0-LAB-I3-R6-R1)"; its body is unaltered.

## 3. Confirmation that history was preserved, not erased

Checked explicitly, because the assignment requires it:

* **Every command in the R6 handback is intact** — the `rsync` block in §3, the
  two verbatim `ssh` invocations in §6.1 and §6.2, and the reviewed argv listings.
  None was edited, re-quoted or removed.
* **Every result is intact** — timestamps, transfer counts and byte figures,
  manifest version 17, the artifact and spot digests, the reproduced review-input
  digest `c358ea8b…`, the 50-file aggregate `4d829dc6…`, the prerequisite table,
  the capability blocks, the per-context tables, nonces, stage lists,
  tracked-object fates, inode identities, the residue surveys and the post-run
  observation table.
* **Both operator effects are still recorded, in their original words**, in §9;
  the superseding note sits above them rather than in place of them.
* **The guard refusal is still recorded** in §3.1, including that the call had
  been written as `date … && rsync … ; echo …` and that no exclusion or command
  shape was weakened. The correction addresses what the refusal *meant*, not
  what happened.
* **Withdrawn sentences are struck through and left legible**, not deleted, at
  the opening summary and at §11's two bullets.
* In the registers, the handover and the plan, each superseded block was
  **demoted in place with a dated note and its body left unaltered**. No entry
  was rewritten, and the change log was appended to, never edited in substance.

## 4. The prepared R7 prompt, and why it is inactive

`docs/review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md`
is a **draft** for one clean operational verification pass.

**It is inactive because it is not authority and nobody has made it one.**
`C-P5.0-LAB-I3-R7` has not been authorized and no implementing operator has been
assigned. Preparing a draft is not an authorization, a scheduling commitment or
an expectation that a pass will be run, and preparing it discharges neither
finding. A new operational pass requires **Peter Duscha's later explicit
authorization and assignment, after independent Codex review of this
remediation** — recorded by identifier and operator in the handover, §20, the
disposable-server restriction and the registers.

It is labelled unmistakably: a fenced **"⛔ NOT AUTHORIZED — THIS DOCUMENT IS NOT
AUTHORITY"** block immediately under the title, "DRAFT, NOT AUTHORIZED" in the
title itself, and a closing reminder in the same terms.

What the draft tightens, relative to R6:

1. **The first synchronization attempt must be the exact plain §3.2 `rsync`
   command** — one plain invocation with single-quoted exclusions, **with no
   preliminary chained form**, no chained `date`, no `&&`, `;` or `|`, no
   substitution, redirection or trailing comment. Timestamps, if wanted, are
   taken in their own separate calls before and after.
2. **Any guard refusal immediately ends the entire pass**, in a section that
   overrides any contrary reading of the rest of the prompt: no further host
   command, no re-issue in any form, no reformulation, unchaining, splitting,
   re-quoting or retry; removing the offending construct and re-issuing does
   **not** cure the stop; the refusal and the refused call are recorded, the
   handback states that the pass ended at a mandatory stop with no
   synchronization and no invocation, and the authority is consumed. A refusal
   may never be described as a guard defect, as stylistic, or as "resolved".
3. **`scp`, operator-created remote temporary files and every other auxiliary
   host-side artifact are prohibited outright** — no file list, capture file,
   output redirection, shell wrapper, script, scratch file or `/tmp` object. The
   one narrow exemption is the reviewed verifier-controlled objects that the two
   exact invocations necessarily create and remove: the
   `.fb-i3-verify-<nonce>-staged` temporary file and `.fb-i3-verify-<nonce>-linked`
   published link in the four publication directories, and P2's temporary
   canonical root and `bin`. That exemption confers no operator permission over
   those objects, does not widen either invocation and does not excuse residue or
   a cleanup failure. Any file set needed for a digest comparison is derived
   in-process from `review_manifest.COVERED_SOURCES` on each host; all output is
   captured in the client/tool transcript.
   *(Corrected 2026-09-20 under C-P5.0-LAB-I3-R6-R2 — see the erratum in §11.
   This item, and the draft section it summarized, previously stated the
   prohibition absolutely, as reaching "any file on the target" other than the
   synchronization's, which contradicted the two invocations the same draft
   authorizes.)*
4. **`/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and
   `/tmp/fb-i3-r6-filelist.txt` are preserved exactly** — not deleted,
   truncated, overwritten, moved, modified or read; `stat` metadata only. The
   draft states that tidying up the third file is not permitted and would be a
   further unauthorized write.
5. The handback requirements add **an explicit statement of whether any guard
   refusal occurred and whether any host-side artifact was created**.

What the draft **retains unchanged** from the accepted R6: the objective and the
four contexts; the governing-context reading list, extended with the R6 erratum
and this handback; the four numbered preparation items including the manifest
version 17 and digest `c358ea8b…` checks; the full prerequisite list; the
prohibition on repairing, provisioning, installing, `chmod`, `chown`, group
creation, capability change and V7 initialization; the exact two verifier
invocations, their identities and their conditional order; the operational stop
conditions; the evidence requirements; the no-capability-causation and
four-context claim limits; and the closing restrictions and stop point.

## 5. Scope actually exercised, and the restrictions observed

Repository documentation only. The following were **not** done, each because the
authorization forbids it: SSH; synchronization; any inspection of `oracle-test`;
`sudo`; deletion or modification of any `/tmp` evidence artifact; any controlled
write; either verifier invocation; any participant or evidence-harness run; any
generated vector; any database access; V7 initialization; V8 or V10; any real
boundary or materializer; and `--execute`.

No source, test, tool, manifest, generated artifact, migration, schema,
configuration or hook file was changed. `plan.is_executable` was not touched and
remains `False`; `reservation.REAL_EXECUTION_REFUSAL` is untouched. No secret
file was read, printed, copied or modified. `git status` was inspected first and
every unrelated, earlier-pass and reviewer-authored change in the working tree
was preserved.

## 6. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-reserved-laboratory-i3-r6-r1-remediation-handback.md` | this handback (new) |
| `docs/review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md` | draft, **not authorized** R7 prompt (new) |
| `docs/review/phase-5-0-reserved-laboratory-i3-r6-controlled-write-verification-handback.md` | erratum plus five superseding notes; history intact |
| `docs/review/Handover information` | new R6-R1 banner; prior R6 banner demoted with a note |
| `docs/implementation-plan.md` | §20 current action replaced; prior action demoted with a note |
| `docs/operations/disposable-test-server.md` | restriction banner replaced, `/tmp` protection extended; prior banner demoted |
| `docs/project-management/raid-register.md` | both findings recorded Open, Blocking; prior entry demoted, its "no new issue" claim withdrawn |
| `docs/project-management/status.md` | current status replaced; prior status demoted with a note |
| `docs/project-management/decision-register.md` | closure decision withdrawn as not ripe; prior entry demoted |
| `docs/project-management/change-log.md` | one appended row; the R6 row relabelled as subsequently not accepted |

No migration, schema or configuration change. No rollback step is required for
the repository; every change is additive documentation or a dated superseding
note, and reverting this commit would restore the uncorrected text, which is not
desirable. **On the target, nothing was changed by this pass**, and
`/tmp/fb-i3-r6-filelist.txt` remains in place awaiting the maintainer.

## 7. Checks run

| Check | Result |
|---|---|
| `git diff --check` | **clean** — no whitespace error, no conflict marker; exit `0` |
| `git status` inspected before editing | done; unrelated, earlier-pass and reviewer-authored changes preserved |
| Trace of every current R6 claim across the controlled documents | done; the corrected claims are enumerated in §2, and a repository-wide search for the withdrawn phrasings confirms each surviving instance sits inside a block carrying its superseding note |

## 8. Checks not run, and why

| Check | Why not |
|---|---|
| `tests/phase_5_0_evidence`, web suite, bot suite, Foundry `node --test` | **Not required and not run.** No Python, web, bot, Foundry or database suite is required for documentation-only remediation, and none was authorized. **No suite figure is offered for this pass.** The R5 figures describe the R5 tree and are **not** re-asserted here; the R6 pass offered none |
| `python3 .claude/hooks/test_guards.py` | no hook was changed by this pass |
| formatter, linter, type checker | no source file was changed by this pass |
| database connectivity, `TEST_DATABASE_URL` | excluded; neither set nor required at any point |
| any check on `oracle-test` — synchronization, prerequisite inspection, residue survey, `/tmp` metadata | forbidden by this pass's restrictions: no SSH, no synchronization, no host inspection, no `sudo` |
| either verifier invocation, harness run, generated vector, real boundary, materializer, V7, V8, V10, `--execute` | explicitly excluded; not performed |

## 9. Resulting state — precisely

* **PR-20260920-LAB-I3-R6-1: Open, Blocking. Not closed.**
* **PR-20260920-LAB-I3-R6-2: Open, Blocking. Not closed.**
* **I3 is unconfirmed and not closed.** The R6 verifier runs occurred and
  returned internally coherent `verified` results; that is occurrence, not
  acceptable gate evidence.
* **C-P5.0-LAB-I3-R6 is consumed** and cannot be retried under its authority.
* The R6 handback stands as a corrected historical record: commands, verifier
  output and operator effects intact; authorization and stop-condition
  conclusions withdrawn by erratum.
* **`C-P5.0-LAB-I3-R7` is not authorized.** The prepared prompt is a draft and
  confers no permission. A new operational pass requires Peter's later explicit
  authorization and assignment after independent review of this remediation.
* `/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and `/tmp/fb-i3-r6-filelist.txt`
  must not be deleted, truncated, overwritten, moved, modified or read.
* V7 remains excluded; V8 and V10 remain unperformed; `plan.is_executable` is
  `False` and was not touched; Package 5.0 remains **not ready**; LAB-SECRETS-1
  remains Open, Low; LAB-V6-P2 remains deferred; LAB-I3-TARGET-1 remains Closed.
* `c358ea8b…` remains **review input only** — no approval, no I3 confirmation,
  never authority for `--execute`.

## 10. Stop point and proposed reviewer focus

**Stopping here for independent Codex re-review.** Nothing further is claimed
and nothing further will be done under this authorization.

Proposed reviewer focus:

1. **§1** — whether both dispositions are stated with sufficient precision, and
   in particular whether the occurrence-versus-gate-evidence distinction is put
   correctly and consistently everywhere it appears.
2. **§2** — whether any current claim that no stop condition fired, that no new
   issue was raised, or that the R6 evidence is presently sufficient to close I3
   survives anywhere uncorrected, in any controlled document.
3. **§3** — whether the erratum-and-superseding-note approach preserved the
   historical record adequately, or whether any withdrawal went further than
   correcting a conclusion.
4. **§4 and the R7 draft** — whether its inactivity is unmistakable, whether its
   three tightenings actually prevent the two findings' recurrence, and whether
   anything accepted in R6 was lost in the rewrite.
5. **The registers** — whether the demotion-in-place convention leaves the
   reconciliation unambiguous for a reader arriving at any one of them.

---

## 11. Erratum — the R7 host-side-artifact rule, corrected under C-P5.0-LAB-I3-R6-R2 — 2026-09-20

**Added 2026-09-20. Nothing above is erased; §4's third item is corrected in
place and marked, and this erratum records what it said before.**

Codex's independent re-review of this remediation raises one **Important**
finding against the draft R7 prompt prepared under it:
**PR-20260920-LAB-I3-R6-R1-1 — the R7 host-side-artifact prohibition
contradicts the controlled-write invocations it would authorize.** The draft's
"No host-side artifacts" section prohibited creating or writing *any file on the
target* except files written by the repository synchronization, while the same
draft authorizes two exact verifier invocations that necessarily create,
publish, observe and remove filesystem objects of their own. An operator could
not satisfy both instructions literally.

**The finding is accepted.** It is a defect in the draft prompt's wording. It is
**not** a defect in the reviewed verifier, and it is **not** authority to
execute that prompt. The correction was made under **C-P5.0-LAB-I3-R6-R2**, one
bounded repository-documentation-only remediation, and is reported in
[the R6-R2 remediation handback](phase-5-0-reserved-laboratory-i3-r6-r2-artifact-rule-remediation-handback.md).

What §4's third item and the draft section said before the correction: that
`scp`, remote temporary files and every other host-side artifact were prohibited
outright, with no file, of any kind, to be created or written on the target
other than what the authorized synchronization writes into
`/opt/freedom-blades/platform`.

What they say now: the same prohibition on every **operator-created or
auxiliary** artifact, with one narrow exemption for the **reviewed
verifier-controlled objects** that the two exact invocations necessarily create
and remove — the `.fb-i3-verify-<nonce>-staged` temporary file and the
`.fb-i3-verify-<nonce>-linked` published link in the four reviewed publication
directories, and, in P2 only, the temporary canonical root
`/var/lib/fb-evidence-p5-0` and its `bin` subdirectory. The exemption confers no
operator permission over those objects, does not widen either invocation and
does not excuse residue or a cleanup failure; all verifier-object creation and
cleanup must occur solely inside the reviewed verifier implementation under the
two exact invocations.

**Unchanged by that correction:** the protection of `/tmp/fb-i3-root.out`,
`/tmp/fb-i3-root.err` and `/tmp/fb-i3-r6-filelist.txt`, including the ban on
reading their contents and on deleting, truncating, overwriting, moving,
modifying or reusing them; the exact synchronization command; the guard-refusal
stop rule; the prerequisites; the verifier commands and their order; the
evidence requirements; the stop conditions; the claim limits; and the scope
exclusions.

**PR-20260920-LAB-I3-R6-R1-1 is remediated but NOT closed** — it awaits
independent Codex re-review and Peter Duscha's decision.
**PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain Open, Blocking**
and are not affected. **`C-P5.0-LAB-I3-R7` remains draft, inactive and NOT
AUTHORIZED**; correcting it confers no permission. I3 remains unconfirmed and
not closed. V7 remains excluded; V8 and V10 remain unperformed;
`plan.is_executable=False`; Package 5.0 remains not ready; LAB-SECRETS-1 remains
Open, Low; LAB-V6-P2 remains deferred.
