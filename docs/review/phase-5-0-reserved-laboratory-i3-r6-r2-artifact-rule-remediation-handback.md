# Claude remediation handback — the R7 host-side-artifact contradiction corrected; R7 still NOT authorized — 2026-09-20

Authorization: **C-P5.0-LAB-I3-R6-R2**, one bounded **repository-documentation-
only** remediation. Claude is the implementing agent. Codex remains the
Independent Technical, Security and Evidence Reviewer and must re-review this
remediation.

**State: PR-20260920-LAB-I3-R6-R1-1 is remediated but NOT closed.** It awaits
independent Codex re-review and Peter Duscha's decision. The draft
`C-P5.0-LAB-I3-R7` prompt remains **DRAFT, INACTIVE and NOT AUTHORIZED**;
correcting it conferred no permission of any kind and created no host authority.
**PR-20260920-LAB-I3-R6-1 and PR-20260920-LAB-I3-R6-2 remain Open, Blocking**
and are untouched by this pass. I3 remains **unconfirmed and not closed**.

No host action was taken and none is authorized. No SSH, synchronization,
inspection of `oracle-test`, `sudo`, `/tmp` access, controlled write, verifier
invocation, harness run, generated vector or database access occurred.

---

## 1. The finding, and its disposition

### PR-20260920-LAB-I3-R6-R1-1 — the R7 host-side-artifact prohibition contradicts the controlled-write invocations it would authorize

**Disposition: ACCEPTED IN FULL. Remediated in the draft prompt and in every
current summary of it. NOT closed.**

The finding is correct and is not disputed. The draft's "No host-side artifacts"
section prohibited creating or writing **any file on the target** except files
written by the repository synchronization. Two sections later the same draft
authorizes two exact verifier invocations, and those invocations necessarily
create, publish, observe and remove filesystem objects of their own — that
creation and removal *is* the behavior under verification. An operator who
issued the two authorized commands would violate the absolute prohibition; an
operator who honored the prohibition literally could not issue them. The two
instructions could not both be satisfied.

Three things are stated because the assignment requires precision about them:

* **This is a prompt defect, not a verifier defect.** The verifier's object
  creation and removal was independently reviewed and is unchanged. Nothing here
  alters `tools/phase_5_0_evidence/execution/i3_verifier.py`, its CLI, its
  descriptors or its tests; no source, test, tool, manifest, generated artifact,
  migration, schema, configuration or hook file was changed by this pass.
* **It is not authority to execute the prompt.** Correcting a draft does not
  activate it. `C-P5.0-LAB-I3-R7` has still not been authorized and no
  implementing operator has been assigned.
* **It discharges neither R6 finding.** PR-20260920-LAB-I3-R6-1 and
  PR-20260920-LAB-I3-R6-2 remain Open and Blocking, unchanged and unclosed.

## 2. The rule, exactly before and exactly after

### 2.1 Before — `phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md`, section "No host-side artifacts"

> **Prohibited outright: `scp`, `sftp`, `rsync` of any file other than the
> synchronization above, remote temporary files, and every other host-side
> artifact.** Specifically, do not create, copy or write any file on the target
> other than what the authorized synchronization writes into
> `/opt/freedom-blades/platform`, and do not create a file list, a capture file,
> an output redirection, a shell wrapper, a script, a scratch file or a `/tmp`
> object of any kind.

The contradiction is the phrase *"do not create, copy or write **any file on the
target** other than what the authorized synchronization writes"*, read against
the verifier invocations authorized under "Authorized verifier invocations, if
authorized".

### 2.2 After — section renamed "No host-side artifacts beyond the reviewed verifier-controlled objects"

The prohibition is retained in full against every operator-created or auxiliary
artifact, with its scope stated as *operator-created* rather than absolute:

> **Prohibited outright: `scp`, `sftp`, `rsync` of any file other than the
> synchronization above, operator-created remote temporary files, and every
> other auxiliary host-side artifact.** Specifically, do not create, copy or
> write any file or directory on the target other than (a) what the authorized
> synchronization writes into `/opt/freedom-blades/platform` and (b) the
> reviewed verifier-controlled objects defined immediately below; and do not
> create a file list, a capture file, an output redirection, a shell wrapper, a
> script, a scratch file or a `/tmp` object of any kind.

A new subsection, **"The one narrow exemption — the reviewed verifier-controlled
objects"**, then defines the exemption exhaustively and closes it:

> The two exact verifier invocations authorized below necessarily create,
> publish, observe and remove filesystem objects of their own. That is the
> behavior under verification, it is what the separately armed and independently
> reviewed verifier implementation does, and an operator cannot both issue those
> two commands and prevent those objects from existing. The prohibition above
> therefore does not reach, **and reaches nothing beyond**:
>
> * the temporary exclusively-created payload file
>   `.fb-i3-verify-<nonce>-staged` and the published hard link
>   `.fb-i3-verify-<nonce>-linked`, in each of the four reviewed publication
>   directories — V4 for T1, V5 for §2.3.3, temporary canonical `R/bin` for P2,
>   and V9 for T6; and
> * in the P2 context only, the temporary canonical root
>   `/var/lib/fb-evidence-p5-0` and its `bin` subdirectory, created and removed
>   within that context.
>
> Nothing else on the host is exempt, and the exemption is not an operational
> authority. In particular it:
>
> 1. **confers no operator permission over these objects.** It does not permit
>    an operator to create, rename, replace, edit, move, copy, preserve, repair
>    or remove any verifier object manually, by any command, before, during or
>    after either invocation. **All verifier-object creation and cleanup must
>    occur solely inside the reviewed verifier implementation, under the two
>    exact invocations below.** The operator issues those two commands and
>    touches nothing they create or leave behind;
> 2. **does not widen either invocation.** No flag may be added, no ad hoc
>    wrapper used and no verifier object invoked directly, exactly as stated
>    below; and
> 3. **does not excuse residue or a cleanup failure.** A cleanup failure, a
>    surviving verifier name or a non-clean final survey remains a stop
>    condition to be recorded and reported, never tidied up, repaired or
>    retried.

### 2.3 Why the exemption is no wider than the reviewed verifier-controlled objects

The exemption is bounded on four independent axes, and an object must satisfy
all four to fall inside it:

1. **By name.** Only `.fb-i3-verify-<nonce>-staged` and
   `.fb-i3-verify-<nonce>-linked` — the pair `verifier_names()` derives from one
   nonce, matching `_NAME_SHAPE`
   (`\A\.fb-i3-verify-[0-9a-f]{32}-(?:staged|linked)\Z`) — plus P2's canonical
   root and its `bin` subdirectory. No other name on the host is exempt.
2. **By location.** Only the four reviewed publication directories named in the
   draft's own objective — V4 for T1, V5 for §2.3.3, temporary canonical `R/bin`
   for P2, V9 for T6 — and, for the canonical pair, the reviewed state parent.
   Nothing under `/tmp`, nothing under `/opt/freedom-blades/platform`, nothing
   elsewhere under `/var/lib`.
3. **By creator.** Only objects created **inside the reviewed verifier
   implementation**, under the two exact invocations already specified. The
   exemption is written as a statement about what the verifier does, not as a
   permission granted to the operator, and it says so in terms: the operator may
   not create, rename, replace, edit, move, copy, preserve, repair or remove any
   of them manually, by any command, at any time.
4. **By lifetime.** Each object is created and removed within its own context of
   the same invocation. Residue is not exempted; it remains a stop condition, and
   manual cleanup remains prohibited.

Consequently **no `scp`, `sftp`, additional `rsync`, remote file list, capture
file, output redirection, shell wrapper, script, scratch file or `/tmp` object
falls inside the exemption** — none of them is created by the verifier, and each
is named as prohibited in the retained sentence. The unauthorized write that
produced `/tmp/fb-i3-r6-filelist.txt` under R6, which is the conduct
PR-20260920-LAB-I3-R6-2 records, would be prohibited by the corrected rule
exactly as it was by the original. The correction removes a contradiction; it
removes no prohibition.

### 2.4 Why the revised rule is internally executable

Under the corrected wording an operator can comply with every instruction in the
draft simultaneously: issue the exact §3.2 `rsync`, perform read-only
prerequisite inspection, issue the two exact verifier commands, and create
nothing else. The objects the verifier creates are no longer described as a
violation of the prompt that orders the commands creating them, and the operator
still has no permission to touch any of them. The two previously irreconcilable
instructions are now one rule with one closed exception.

## 3. Every file and passage changed

Three files. No other file in the repository was modified by this pass.

### 3.1 `docs/review/phase-5-0-reserved-laboratory-i3-r7-controlled-write-claude-prompt.md`

| Passage | Change |
|---|---|
| Section heading "No host-side artifacts" | Renamed "**No host-side artifacts beyond the reviewed verifier-controlled objects**" |
| Prohibition sentence | "remote temporary files, and every other host-side artifact" → "**operator-created** remote temporary files, and every other **auxiliary** host-side artifact"; "any file on the target other than what the authorized synchronization writes" → "any file **or directory** on the target other than **(a)** what the authorized synchronization writes into `/opt/freedom-blades/platform` **and (b) the reviewed verifier-controlled objects defined immediately below**". The enumerated bans — file list, capture file, output redirection, shell wrapper, script, scratch file, `/tmp` object of any kind — are retained verbatim |
| New subsection "The one narrow exemption — the reviewed verifier-controlled objects" | Added. Defines the exempt objects exhaustively and states the three limits quoted at §2.2 above |
| `COVERED_SOURCES` / transcript paragraph | Unchanged, retained in place |
| Historical-evidence block for `/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err`, `/tmp/fb-i3-r6-filelist.txt` | **Unchanged.** Preservation, the ban on reading contents, and the statement that tidying up the third file is not permitted all stand exactly as written |
| Required handback | "whether any host-side artifact was created" → "whether any host-side artifact **outside the reviewed verifier-controlled exemption** was created, with confirmation that every verifier object was created and removed solely inside the verifier under the two exact invocations and that the operator touched none of them" |

Everything else in the draft is untouched: the ⛔ NOT AUTHORIZED banner and
closing reminder, "Why this draft exists", the objective and four contexts, the
governing-context reading list, the guard-refusal stop section, the exact §3.2
`rsync` command and its first-attempt rule, the four numbered preparation items
with manifest version 17 and digest `c358ea8b…`, the prerequisite list, the two
exact verifier invocations and their conditional order, the stop conditions, the
claim limits, and the closing restrictions and stop point.

### 3.2 `docs/review/phase-5-0-reserved-laboratory-i3-r6-r1-remediation-handback.md`

| Passage | Change |
|---|---|
| Head of document | New erratum note pointing to §11, naming PR-20260920-LAB-I3-R6-R1-1, stating that §4's third item is corrected in place and that the R7 draft remains NOT AUTHORIZED and both R6 findings Open, Blocking |
| §4, third item ("What the draft tightens") | Corrected in place and marked with a dated parenthetical: the prohibition is restated as reaching every operator-created or auxiliary artifact, the one narrow exemption is summarized with its three limits, and the parenthetical records that the item previously stated the prohibition absolutely as reaching "any file on the target" |
| New §11, "Erratum — the R7 host-side-artifact rule, corrected under C-P5.0-LAB-I3-R6-R2" | Added. States the finding, accepts it, records the before and after wording, lists what the correction left unchanged, and records the finding as remediated but not closed |

**Nothing in that handback was erased.** No historical command, timestamp,
digest, verifier output or operator effect was rewritten. The single in-place
edit is to a summary of a draft document that this pass changed, and the erratum
records verbatim what it summarized before.

### 3.3 `docs/review/Handover information`

The returned remediation state and this handback's pointer are placed at the top
of the active handover, superseding the C-P5.0-LAB-I3-R6-R2 assignment without
erasing it. The assignment and every earlier prompt and handback banner remain
in the file, in order, unaltered.

## 4. Other current summaries of the R7 artifact rule — traced, and why they are not changed

Every occurrence of the rule in the repository was traced before editing
(`grep -rn "host-side artifact"` across `docs/`, plus a check of each controlled
document that mentions R7). Beyond the three files above:

| Location | Wording | Disposition |
|---|---|---|
| `docs/review/Handover information`, R6-R1 handback banner | "prohibits `scp`, remote temporary files and every other host-side artifact" | **Not rewritten.** It does not carry the absolute "any file on the target" formulation, so it does not repeat the contradiction. It is a returned, retained handback banner; the new top entry supersedes it explicitly |
| `docs/review/Handover information`, retained C-P5.0-LAB-I3-R6-R1 prompt, assignment item 6 | "prohibit `scp`, remote temporary files and every other host-side artifact" | **Not rewritten.** A retained historical assignment record, and likewise free of the absolute formulation. Rewriting it would normalize wording in a historical record for no substantive reason |
| `docs/project-management/status.md`, `decision-register.md`, `raid-register.md`, `change-log.md`, `docs/implementation-plan.md` §20, `docs/operations/disposable-test-server.md` | Each describes the R7 prompt only as draft, inactive and not authorized; none summarizes its artifact rule | **No change needed.** Nothing in them repeats the contradictory wording, and this documentation-only correction changes no state they record |

No register entry, status banner, §20 action or disposable-server restriction was
altered, because this pass changed no state: the findings, the authorization, the
host restriction and the resulting state are all exactly as those documents
already record them.

## 5. Confirmation — R7 remains inactive; no host authority was created

* The draft retains its fenced **⛔ NOT AUTHORIZED — THIS DOCUMENT IS NOT
  AUTHORITY** block immediately under the title, "DRAFT, NOT AUTHORIZED" in the
  title itself, and the closing reminder in the same terms. None of the three was
  weakened, and all three were re-read after editing.
* `C-P5.0-LAB-I3-R7` has **not** been authorized and **no** implementing operator
  has been assigned. A pass requires Peter Duscha's later explicit authorization
  naming that identifier and operator, recorded in the handover, §20, the
  disposable-server restriction and the registers, after independent Codex
  re-review.
* **The exemption is not authority.** It describes what the reviewed verifier
  does inside two commands that are themselves unauthorized. It grants the
  operator nothing, and it exists inside a document that grants nothing.
* The operational scope of the draft is unchanged: the exact §3.2
  synchronization, necessary read-only prerequisite inspection and the two exact
  verifier invocations, and nothing else.
* Nothing in this pass approved a digest, initialized V7, changed
  `plan.is_executable`, advanced Package 5.0 or authorized `--execute`.

## 6. Scope actually exercised, and the restrictions observed

Repository documentation only. The following were **not** done, each because
this authorization forbids it: SSH; synchronization; any inspection of
`oracle-test`; `sudo`; reading, deleting or modifying any `/tmp` evidence
artifact; any controlled write; either verifier invocation; any participant or
evidence-harness run; any generated vector; any database access; V7
initialization; V8 or V10; any real boundary or materializer; and `--execute`.

`git status` was inspected first. Every unrelated, earlier-pass and
reviewer-authored change in the working tree was preserved; the three files in
§3 are the only ones this pass touched. No secret file was read, printed, copied
or modified, and no guard refusal occurred during this pass. The I3 verifier
source was read **read-only in the repository**, to state the exempt object
names and layout accurately.

## 7. Checks run

| Check | Result |
|---|---|
| `git status --short` before editing | Inspected; unrelated and earlier-pass changes identified and preserved |
| `git diff --check` | **Clean — no whitespace errors, no output** |
| Trace of every current summary of the R7 artifact rule | Complete; dispositions in §4 |
| Re-read of the corrected draft's NOT-AUTHORIZED banner, title and closing reminder | All three intact |
| Re-read of the draft's `/tmp` historical-evidence block | Unchanged, character for character |

## 8. Checks not run, and why

| Not run | Why |
|---|---|
| Python, web, bot, Foundry and database suites | Not required for this documentation-only remediation, and the assignment states so expressly. **No figure from an earlier tree is asserted as evidence for this pass.** No source, test, tool, manifest, generated artifact, migration, schema, configuration or hook file was changed, so no suite result could change |
| `python3 .claude/hooks/test_guards.py` | No hook was changed by this pass |
| Formatter, linter, type checker | No Python file was changed by this pass |
| Any check on `oracle-test` — synchronization, prerequisite inspection, residue survey, `/tmp` metadata | Forbidden by this pass's restrictions: no SSH, no synchronization, no host inspection, no `sudo`, no `/tmp` access |
| Either verifier invocation, harness run, generated vector, real boundary, materializer, V7, V8, V10, `--execute` | Explicitly excluded; not performed |

## 9. Resulting state — precisely

* **PR-20260920-LAB-I3-R6-R1-1: remediated, NOT closed.** Awaiting independent
  Codex re-review and Peter's decision.
* **PR-20260920-LAB-I3-R6-1: Open, Blocking. Not closed, not changed.**
* **PR-20260920-LAB-I3-R6-2: Open, Blocking. Not closed, not changed.**
* **`C-P5.0-LAB-I3-R7` remains DRAFT, INACTIVE and NOT AUTHORIZED.** Correcting
  it conferred no permission and created no host authority.
* **I3 remains unconfirmed and not closed.** C-P5.0-LAB-I3-R6 remains consumed
  and cannot be retried under its authority.
* `/tmp/fb-i3-root.out`, `/tmp/fb-i3-root.err` and `/tmp/fb-i3-r6-filelist.txt`
  must not be read, deleted, truncated, overwritten, moved, modified or reused;
  the disposition of the third is the maintainer's alone.
* V7 remains excluded; V8 and V10 remain unperformed; `plan.is_executable` is
  `False` and was not touched; Package 5.0 remains **not ready**; LAB-SECRETS-1
  remains Open, Low; LAB-V6-P2 remains deferred; LAB-I3-TARGET-1 remains Closed.
* `c358ea8b…` remains **review input only** — no approval, no I3 confirmation,
  never authority for `--execute`.

## 10. Stop point and proposed reviewer focus

**Stopping here for independent Codex re-review.** Nothing further is claimed and
nothing further will be done under this authorization.

Proposed reviewer focus:

1. **§2.2 and the corrected draft section** — whether the exemption is genuinely
   no wider than the objects the two exact invocations necessarily create, and
   whether any operator-created artifact could be argued into it.
2. **§2.3's four axes** — whether name, location, creator and lifetime together
   close the exemption, and whether the "creator" axis is stated firmly enough
   that no manual touch of a verifier object could be read as permitted.
3. **§2.4** — whether the draft is now executable end to end without a
   contradiction remaining anywhere in it.
4. **§3.1's unchanged column** — whether the synchronization command, guard-stop
   rule, prerequisites, verifier commands and order, evidence requirements, stop
   conditions, claim limits and scope exclusions are in fact unchanged, and
   whether the `/tmp` protections survived intact.
5. **§4** — whether leaving the two retained handover summaries unrewritten is
   right, or whether either should also be superseded in place.
