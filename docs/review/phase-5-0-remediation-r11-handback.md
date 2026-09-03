# Package 5.0 — security remediation R11 handback

Date: 2026-08-31 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer, independent
logical-schema reviewer and **Security Reviewer**, OD-61).

In response to: `docs/review/phase-5-0-security-review.md`, *Package 5.0 security
review — revision 11*, and the accompanying remediation instructions, which
**authorize documentation and design remediation only**. No production code,
migration `0014`, database, operating-system or host change, privileged probe,
Git write, service change, Google access, deployment, cutover or Package 5.1+
work is authorized, and none occurred.

> **Claude claims no finding closed.** P5.0-SR1 and P5.0-SR2 are closed by the
> Security Reviewer, not here. **P5.0-R5 remains Blocking**, P5.0-R1 and P5.0-R4
> remain open, OD-62 through OD-66 remain Open, and **Package 5.0 is not ready.**
>
> **The findings are conceded before any replacement is presented.** Both
> concessions are written into the documents themselves — package plan
> **§2.13.1 rows 29 and 30**, and again at the head of §2.12.5a and §2.12.2 —
> *before* the corrections are stated, so a reader meets the defect first.
>
> - **P5.0-SR1.** Revision 11 had one function, `deployment_manifest_digest()`,
>   and three consumers, and **every one of them computed or compared a digest of
>   the live deployed bytes**. The deploy step recorded that value, the operator
>   supplied it back, and `init-generation` **C0** compared it with a fresh
>   computation over the same bytes. **That is consistency after deployment, not
>   provenance from the reviewed commit.** No artifact, registration input or
>   activation precondition named a reviewed commit, and **no step refused when
>   the separate comparison against the commit was omitted** — so the omission
>   left no refusal and no durable trace. The re-review is right that this is
>   Blocking: **H-1** explicitly permits service identities to rewrite a source
>   tree, and the deployed program is root-owned and carries authority over the
>   authority plane and the journal evidence.
> - **P5.0-SR2.** §2.12.2 gave `freedomcoord` and `freedomsheet` the groups
>   *"its own only"* and asserted that `freedomcoord` *"is in no group any
>   service identity holds"*, while §2.13.3 created `freedomjournal` holding
>   exactly those two, and `E1` and `E2` were constructed with it. **The two
>   contracts cannot both be followed**: under the first the `0750` directory and
>   the `0440` seal are unreadable and the writer cannot perform the startup
>   validation §2.13.5b requires of it; under the second §2.12.6's identity
>   inventory is wrong. **The false sentence stood from revision 6 through
>   revision 11 — five revisions and three independent re-reviews.** The
>   logical schema carried the same contradiction in §4.3.2, in prose and in its
>   own table two lines apart.
>
> **Nothing was executed.** No host object was created: no account, no group, no
> directory, no Git repository or bare object store, no approval record, no
> provenance record, no file, mode or filesystem attribute. **No `git` command
> that writes was run**, no capability set, UID, GID or securebit was
> constructed, and **A-5.0-5 remains unconfirmed and is widened again**.
> **An independent security re-review of revision 12 is required.**

---

## 1. Instruction-by-instruction change table

| Instruction | Where it is answered | What it now says |
|---|---|---|
| **1 — remediate P5.0-SR1 by specifying a fail-closed binding between the deployed files and an immutable reviewed Git commit, not merely a digest computed from the live deployment** | package plan **§2.12.5a**, new; **§2.13.2c** extended; **§2.13.5a C0/C3**; **§2.13.5b W11a and V-R**; **§2.13.6 J-26 … J-28**; logical schema **§3.7**, **§3.8** | **Four facts from four sources must agree.** `APR`, a `root:root 0444` approved-revision record installed **out of band**, naming the commit, tree and source-manifest digest a review approved. `TM`, the trusted manifest **computed from Git object bytes** in a **bare** `root:root 0700` store, addressed **by object id**, with **no ref, branch, tag or `HEAD` resolved anywhere in the algorithm**. `SM`, the same manifest recomputed over the **live deployed bytes**. And `ASR`, a row in the new `approved_source_revisions` table — the one copy an actor with host authority alone did not write |
| **1 — include the deployment/registration contract** | package plan **§2.12.5a**, *Algorithm D* and *Where the provenance is then consumed* | **Algorithm D `D0 … D8`**, with its own refusal family `DEP-01 … DEP-09`, a **closed two-region partition** of the deployed root in which **any unaccounted file refuses**, a hash-pinned dependency region, ownership and modes taken from a **reviewed deployment map** that is itself inside the manifest, a **rollback to the predecessor** if `D7` or `D8` fails, and the provenance record `PVR` written **last** and **outside the deployed root**, so no digest covers a file containing its own value. The **registration** contract is `V-R`'s lookup plus a **`NOT NULL` foreign key**, and the plan says explicitly why the foreign key rather than the lookup is the control |
| **1 — a negative test proving that omission of provenance prevents activation** | package plan **§2.13.8**, **`JNL-51` case (g)**; §6.1 row 14; §6.5 item 21 | The provenance step is omitted — `D8` suppressed, or `PVR` deleted after a successful deployment. `init-generation` is asserted to **refuse at C0** with `J-26`; the probe is asserted **never to have run**; **no journal file, seal, `current` symlink, `.close` manifest or registration row exists**; and therefore **activation cannot succeed**, because §3.4's trigger requires a registered generation. The case then separately assembles a well-formed `PVR` and `APR` naming a commit with **no approved-revision row**, drives `init-generation` and `seal` to completion, and asserts that **`V-R` refuses with `J-28`** and that the identical `INSERT` **issued as direct SQL is refused by the foreign key under the coordinator role *and* under the schema owner** |
| **2 — one canonical primary/supplementary membership table, used consistently in provisioning, the holder model and E1–E8** | package plan **§2.12.2**, rewritten | §2.12.2 is now that table: primary group and **complete** supplementary list per identity, a **group → members inverse** stating what each membership grants and does not grant, and a rule that **no other passage states a membership**. §2.12.7's provisioning states the group creation and membership in order and asserts them before anything else runs; §2.13.3, §2.13.5c, §2.12.6, §2.13.7 and logical schema §4.3.2 **cite** it. **`E8` gains `freedomjournal`** so the identity named after the coordinator is the coordinator, and the identity table gains a column saying which provisioned identity each of `E1 … E8` corresponds to — **three correspond to none, and are labelled synthetic** |
| **2 — positive and negative `id`/`namei`/open evidence for `freedomsheet`, `freedomcoord`, `discordbot`, `freedomweb`** | package plan **§2.13.8**, new **`JNL-52`**, eight cases | Every case first asserts `getent group` against §2.12.2 **exactly**, and **an unexpected member fails the case**. Then a positive and a negative set per identity. `discordbot` and `freedomweb` each get a **traverse-to-parent positive control** — and `freedomweb` additionally a proof that its `discordbot` membership is real — so their denials are attributable to `…/journal`'s mode rather than to a path search or a broken identity. **These eight cases are the review's check `C-4`** |
| **3 — update the package plan** | throughout | §2.12.2, §2.12.5, **new §2.12.5a**, §2.12.6, §2.12.7, §2.13.1 rows 29–30, §2.13.2c, §2.13.3, §2.13.5a, §2.13.5b, §2.13.5c, §2.13.6, §2.13.7, §2.13.8, §1.2 deliverable 14, §3 WP-16 and seven amended work packages, §4, §5.1, §5.3, §6.1, §6.5, §7.1 rows 29–30, §7.4, §8.1, §9.2, §9.3 conditions 4/10o/10p, §9.4, §10 |
| **3 — update the logical schema where affected** | `phase-5-0-logical-schema.md` | **It is affected, unlike R6 … R10.** §0.2, §3.0's diagram, **§3.7** (four columns, two foreign keys, one extended check), **new §3.8**, §4.3.1, **§4.3.2** (the contradiction corrected and demoted to a citation), §4.3.4, §4.3.5, §4.3.8 **Band 4**, §5's inventory row, §6, §9 (two rows) and §10 |
| **3 — remediation handback** | this document | — |
| **3 — status / RAID records** | `docs/project-management/status.md`, `raid-register.md`, `decision-register.md`, `change-log.md`, `docs/discovery/open-decisions.md`, `docs/implementation-plan.md` §20 | Current entries added, previous entries demoted to superseded rather than rewritten. **Two RAID rows are proposed and none is closed**: **R-5.0-15** and **R-5.0-16** |
| **3 — security-review traceability** | `docs/review/phase-5-0-security-review-brief.md`; §9 of this document | The brief is updated to twelve surfaces, 4.5–5.5 reviewer-days, three residuals and the state carried into the re-review. **`phase-5-0-security-review.md` is not edited** — it is a received review artifact, and rewriting its conclusions would be the wrong move |
| **4 — do not make host changes, implement code, rule OD-62–OD-66, or claim Package 5.0 ready** | §7, §8 and §10 of this document | **None occurred.** No decision is ruled, no option adopted, no finding closed, no assumption confirmed. §9.4 still concludes `not ready` |
| **5 — return the remediation for Codex re-review** | §11 | Requested, and this submission does not pre-empt it |

---

## 2. Why P5.0-SR1 needed a contract and not a stronger sentence

The narrow reading of the finding is that an operations document said *"compare
the digests"* and no algorithm enforced it, so the fix is to move that sentence
into `C0`. **That would not have fixed it**, and the reason is worth stating,
because it is the same reason the R8-A defect needed a redesign rather than a
reordering.

`deployment_manifest_digest()` has exactly one input: the deployed bytes. A
comparison between two computations of it is a comparison between an artifact and
itself. Moving it into a precondition makes the check **mandatory** without making
it **meaningful** — it would refuse a deployment that changed underneath the
operator, which it already did, and it would still admit every set of bytes
whatever, including a tree a compromised service identity had authored through
**H-1**. **A control needs a trusted side that the untrusted side cannot
produce**, and revision 11 had nowhere to get one.

Three candidate trusted sides were considered, and two were rejected:

| Candidate | Why not |
|---|---|
| **The repository worktree at `/opt/freedom-blades/platform`** | It is group-writable by `discordbot`, and `freedomweb` is in that group (**H-1**). Its `.git` directory is writable too, so refs, objects and hooks are all attacker-influenceable. **A trusted side that the threat model says the attacker can write is not a trusted side** |
| **A ref, branch or tag in any store** | A ref is a mutable pointer. Resolving `refs/tags/v1.2.3` asks *"what does this name point at now"*, which is a question an attacker with write access to the store answers. **Revision 12 resolves nothing but object ids**, and says so as a property of the algorithm rather than as advice |
| **A commit object in a root-owned bare store, named by an out-of-band approval record** — *taken* | Content-addressed, so the object's bytes cannot change without changing its name; in a store that is `root:root 0700`, so no service identity can read or write it; and named by a record no step of the deploy path can write. This is the only candidate where **no arrow runs from the deployed bytes to the trusted side** |

**And one thing the candidate does not settle on its own: SHA-1.** A Git object
id is a SHA-1 digest and SHA-1 is not collision-resistant, so *"the commit id
matches"* is a weaker statement than it looks. `APR` therefore carries a
**SHA-256 `source_manifest_digest`** as well, and **D3** refuses unless the
manifest recomputed from the store's object bytes equals it. A substituted object
that collided under SHA-1 has different content bytes and a different SHA-256.
**This is stated in the design rather than assumed**, because a provenance design
that binds to "the commit" and never mentions SHA-1 has quietly assumed it.

**Two problems the contract had to solve that the finding does not name**, and
they are why §2.12.5a is longer than a comparison:

- **Git cannot express uid, gid or the full mode.** A manifest computed from a
  tree object cannot reproduce them, so a single function compared across both
  sides would fail on every correct deployment. Revision 12 defines a **second,
  projected** function, `deployed_source_manifest_digest()`, over the four facts
  both sides can produce, and checks ownership and modes **separately and
  exactly** against a deployment map that is itself inside the reviewed tree —
  so *which files are installed and who owns them* is a reviewed fact rather
  than a deploy-time argument.
- **A deployed root is not all reviewed source.** The interpreter and the
  third-party distributions are not in the repository. A whole-tree digest hides
  that; a source-only digest ignores it. Revision 12 **partitions the root into
  exactly two regions and closes the partition**: region **S** is bound to the
  reviewed tree, region **D** to a hash-pinned lock file that lives in region S,
  and **a file belonging to neither refuses** — at **D5** when deployed and again
  at **C0**. That is the failure a whole-tree digest cannot see: the reviewed
  files deployed correctly, *and one more*.

**What the contract deliberately does not claim** is set out in plan §2.12.5a and
§10, and the important one is this: **root is still inside the trust boundary.**
An actor holding **A5** rewrites the approval record, the object store and the
provenance record; if it also holds **A8** it registers the revision it approved.
That is **R-5.0-15**, it is recorded as a residual with its holder named, and the
design change that would narrow it — a signed approval record verified against a
root-held keyring — is priced as **OD-66 option A-3** and **not adopted**,
because introducing a signing key is a governance change with its own custody,
rotation, revocation and availability failure modes and is the Acceptance
Authority's to make.

---

## 3. Why P5.0-SR2 needed one table and not a corrected sentence

The finding could have been answered by editing four words in §2.12.2. **The
defect is not that one of five copies was wrong; it is that there were five
copies.** A membership stated in five places is four opportunities for the same
failure, and the failure mode here is specific and bad: two statements that both
read as contracts, that cannot both be followed, and whose consumers are in
different sections — a permission model in one place, a startup algorithm in
another — so neither's reader is looking at the other.

The evidence that a corrected sentence would not have been enough is that
**this exact defect survived five revisions and three independent re-reviews**,
including two that examined `E1 … E8` in detail and one that rewrote them
entirely. Nobody compared §2.12.2's table with §2.13.3's prose, because there was
no rule saying the comparison was owed.

So revision 12 makes it **structural**:

- **§2.12.2 is the only place a membership is stated.** Complete per-identity
  supplementary lists, and a per-group member list, so both directions are
  written and either can falsify the other.
- **Stop condition 10p** makes a membership stated elsewhere a defect **whether
  or not it is correct**, which is the only version of the rule that catches the
  next instance before it disagrees.
- **Every evidence identity must say which provisioned identity it corresponds
  to, or say that it corresponds to none.** `E3`, `E4`, `E5` and `E6` correspond
  to none. That is legitimate — a synthetic identity is how you isolate a kernel
  check — and it must be visible, because a synthetic identity mistaken for a
  real holder set is the same defect one level down.
- **The false claim is withdrawn, not repaired.** *"`freedomcoord` … is in no
  group any service identity holds"* is gone. What replaces it is three claims
  that are separately true and separately tested: the shared group is read-only
  over one directory and one file; `freedomcoord` holds no write bit anywhere in
  the hierarchy; and **no mechanism in this design decides who a process is from
  a group** — `SO_PEERCRED` reports a uid, `pg_ident` maps a system user, and the
  `sudoers` rule names `foundry` and targets `freedomcoord`.

**One correction follows from the table rather than from the finding.** `E8` was
`freedomcoord` with its own group only, which is not the identity §2.12.2
provisions. It now carries `freedomjournal` too, and its `capsh` invocation gains
the second `--groups` entry. **Every case naming E8 was rechecked and none
moves**: the added group grants `r-x` on `…/journal` and `r--` on the seal, which
§2.13.3 already says the reader has, and no case asserts E8 is denied a read.
`JNL-50` case 8 — the one case that turns on *absence* of `freedomjournal` — runs
under **E5** (`fbprobe`, in neither group) and is untouched.

---

## 4. What changed in the schema, which is what makes this remediation different

R6 through R10 each reported *nil* schema consequences. **R11 does not.**

| Object | Revision 11 | Revision 12 |
|---|---|---|
| Tables | six | **seven** — `approved_source_revisions` (§3.8) |
| Columns on `sheet_writer_journal_generations` | as revision 6 left them | **four added**: `source_commit`, `source_tree_id`, `source_manifest_digest`, `approved_source_revision_id` |
| Foreign keys | as revision 6 left them | **two added**, one **`NOT NULL` `RESTRICT`** and one **composite**, so the generation's recorded provenance cannot disagree with the approved row it names |
| Append-only triggers | four | **five** — `reject_history_mutation` on the seventh table |
| Closed vocabularies | `fenced_writer`, `filesystem_type`, `append_only_probe_version` | **plus `component`** (`sheet_writer`, `coordinator`) |
| Commands | five | **five.** `RegisterJournalGeneration` gains a lookup; no sibling command is added |
| Sequences, indexes on existing tables, the activation trigger's five conditions | unchanged | **unchanged** |

**The `NOT NULL` foreign key is the whole of the "prevents activation"
requirement**, and it is worth being precise about why it and not the `V-R`
lookup. A lookup is a step in a program: it can be removed, reordered or bypassed
by a caller who issues the `INSERT` directly. A `NOT NULL` foreign key is
evaluated by PostgreSQL on the statement that would create the row, for **every**
principal including the schema owner, and it cannot be satisfied without a row in
a table whose `INSERT` privilege belongs to one peer-authenticated principal
reachable only through the `sudoers` rule. Combined with §3.4's requirement of a
registered generation, **an unprovenanced deployment cannot reach activation**,
and no procedure step is load-bearing. `JNL-51` case (g) proves it by direct
statement under both writing principals, which is the proof shape §3.7.1 requires
whenever a constraint rather than a procedure is credited with a refusal.

**There is no withdrawal column, and its absence is a choice.** A `revoked_at`
would have to be `UPDATE`-able, which `reject_history_mutation` refuses on every
table here, or it would need a second append-only table and a latest-row-wins
read — the mutable-head shape §3.7 exists to avoid. And withdrawal cannot
un-deploy anything: a generation already registered stays registered. §3.8 says
so where a reader meets it.

---

## 5. Counts, estimates and effort — these move, and the arithmetic is shown

| Figure | Revision 11 | Revision 12 |
|---|---|---|
| Evidence identifiers | 50 | **53** |
| Evidence cases | 88 | **114** (`JNL-46` 5 → 9; new `JNL-51` 8, `JNL-52` 8, `JNL-53` 6) |
| Tables | 6 | **7** |
| Authorities | 11 | **11** — `A5` widened, no row added |
| Falsification rows | 13 | **14** — **F-13** added |
| §2.13.4 manipulation rows | 15 | **15** |
| Fail-closed conditions / writer refusal codes | 25 / `SW-J01 … SW-J25` | **28 / `SW-J01 … SW-J28`**, plus the deploy step's `DEP-01 … DEP-09` |
| Work packages | 15 (WP-5 withdrawn) | **16** — **WP-16**, the deployment contract |
| §1.2 deliverables | 13 | **14** |
| §6.5 evidence items | 20 | **22** |
| §9.2 security surfaces | 11 | **12** |
| Estimate | PERT 40.9 | **PERT 47.6** |
| Remediation allowance | 11.9 (0.30 × 39.8) | **13.9** (0.30 × 46.3) |
| Security review | 3.5–4.5 reviewer-days | **4.5–5.5** |
| Residuals | R-5.0-12, R-5.0-13, R-5.0-14 | **plus R-5.0-15, R-5.0-16** |

**The estimate rises because real, separately reviewable work is added**, and
§4 of the package plan decomposes it per package with both O/ML/P triples and
PERT deltas. `40.93 + 6.63 = 47.57`, which is the `285.4 / 6 = 47.6` the totals
row computes directly. **The two routes are both shown because they agree**;
nothing is rounded, absorbed or netted against the remediation allowance.

**One pre-existing stale figure was found and is corrected rather than updated
silently.** §5.1's R-03 row gave this package's estimate as **35.5** — the
revision-4 value, left behind through six estimate changes. It now reads 47.6,
with a note saying what it was and why the correction is called out: a stale
number in a scope-risk row is exactly what that risk exists to catch.

---

## 6. What changed elsewhere, and what deliberately did not

**Added.**

- **Stop condition 10o** — no integrity or supply-chain control may take its
  trusted side from the artifact it is checking, and omission of a provenance
  input must refuse rather than default. It extends **10j**'s I-2 from *"an
  independent source"* to *"a source outside the host the artifact is deployed
  on"*.
- **Stop condition 10p** — a membership stated anywhere but §2.12.2 is a defect
  whether or not it is correct.
- **Stop condition 4 is extended**: the gate now stops if the Security Reviewer
  is named but the recommendation is undelivered, or delivered with an open
  Blocking or Important finding. Revision 11 satisfied this condition by naming
  alone, and the gap it exists to guard was the review.
- **§7.1 rows 29 and 30** — the two recurrence classes.
- **RAID rows R-5.0-15 and R-5.0-16** — proposed, not entered.
- **OD-66 option A-3** — a signed approval record, priced and **not adopted**.

**Changed.**

- **`A5` is widened** to the three root-owned provenance artifacts. **Its holder
  set does not change** — they are `root:root` like the deployment path already
  was — which is why no twelfth authority is invented; inventing one would have
  implied a different holder set.
- **A-5.0-5 is widened again** and remains **unconfirmed**: it now also needs a
  disposable object store, a disposable approval record, and the ability to run
  `id`, `namei -l` and `open` as four named identities.
- **§9.4's role criterion flips to met and is replaced by a new one.** The
  Security Reviewer is named, so that row is satisfied; the **undelivered review**
  is now its own row, and it is **NOT met**. A named reviewer who has returned
  two findings is further from readiness than a vacancy, not closer, and the
  assessment says so.

**Preserved unchanged in substance.** §2.13.2b's cleanup state machine;
§2.13.2c's `deployment_manifest_digest()` contract, which is **extended** by the
source projection and the region partition and **not reopened**; F-7 and
R-5.0-13; the kernel-requirements table, the eleven-authority register, the
holder table and the thirteen inherited falsification rows; revision 11's
`capsh(1)` construction and its mask-versus-recipe comparison; §2.10's barrier
search; §2.1's authority-state matrix; OD-55 and OD-58. **No corrected artifact
produced a direct conflict with any of them**, so nothing was stopped and
reported under the brief's conflict clause.

---

## 7. Documentation checks, and their results

All non-mutating. **Nothing in this list created a host object, wrote to a Git
repository, changed a UID, GID, group, capability set, securebit, file, mode or
filesystem attribute, or executed a privileged helper.**

| Check | Result |
|---|---|
| **1 — every membership statement in `docs/` located and reconciled** | Searched for `freedomjournal`, `freedomcoord`, `freedomsheet`, `discordbot`, `freedomweb`, `fbprobe`, `getent group`, `--groups=` and `supplementary`. Every **live** statement now either is §2.12.2 or cites it; every other hit is inside a superseded block, a conceded-defect row or a review record that must retain its original wording. Results are in §9 |
| **2 — every consumer of `deployment_manifest_digest()` re-read against the new source projection** | Four call sites: the deploy step (**D7**), `init-generation` **C0** and **C2**, and the writer **W11**. **None of their contracts changes.** `deployed_source_manifest_digest()` is a **fourth** named function with its own three call sites, and `JNL-46` asserts the three-site identity for each function separately. **R8-A is preserved, not reopened** |
| **3 — acyclicity re-checked against stop condition 10g** | The four provenance fields enter the **seal body**, which is fixed before the journal file exists, so they are upstream of `seal_body_digest`, the genesis record and the binding — no new edge runs backwards. **`PVR` is outside the deployed root**, so `deployment_manifest_digest()` does not cover a file containing its own value. The §2.13.5a dependency graph gains a provenance fragment in which **no arrow runs from the deployed bytes to the trusted side**, and it is drawn rather than asserted |
| **4 — every `E1 … E8` reference rechecked after the E8 correction** | `JNL-49`, `JNL-50`, `JNL-13`, `JNL-33`, `JNL-35`, `JNL-38`, `JNL-48`, §2.13.2a, §2.13.5c's control pairs, logical schema §4.3.8 Band 3 and §9. **No expected result moves.** E8's added group grants reads §2.13.3 already attributes to the reader; `JNL-50` case 8, the only case turning on absence of `freedomjournal`, runs under **E5** and is untouched |
| **5 — arithmetic re-derived independently** | Per-package O/ML/P deltas sum to `3.2 / 6.5 / 10.6`; the totals row reads `23.1 / 46.3 / 77.1`; `285.4 / 6 = 47.5667`. Per-package PERT deltas sum to `6.633`; `40.933 + 6.633 = 47.567`. **The two routes agree.** Case arithmetic: `88 + 4 + 8 + 8 + 6 = 114`; identifiers `50 + 3 = 53` |
| **6 — Markdown whitespace, table-shape, heading-order and link checks** | `git diff --check` **clean**; no trailing whitespace and no tab characters in any changed document; every Markdown table has a consistent column count; heading order is monotone, the apparent exceptions being `#`-prefixed lines inside fenced `pg_hba`/`pg_ident` code blocks, which predate this remediation; every internal document reference resolves, the exceptions being `docs/contracts/phase-5-migration-and-cutover-contract.md` and `docs/operations/migration-cutover-and-rollback.md`, which are **§1.2 deliverables of this package** and correctly do not exist yet |
| **7 — implementation and privileged suites** | **Not run.** §8 below |

---

## 8. Checks run, checks not run, and their accountable owners

| Not run | Why |
|---|---|
| **Every `TC-5.0-JNL` case, including all of `JNL-51`, `JNL-52` and `JNL-53`** | **A-5.0-5 is unconfirmed.** The journal hierarchy, the object store, the approval record, the four proposed identities and the `freedomjournal` group **do not exist on this host**, and creating any of them is a host change this remediation is not authorized to make. **Owner: Operations Owner** |
| **Check `C-4`** — that the `0750`/`0440` grant gives `freedomsheet` read and gives `discordbot` and `freedomweb` none | the same authorization. **This is what `JNL-52` is for**, and specifying it is not running it. **Owner: Operations Owner**, on the Security Reviewer's brief |
| **Check `C-1`** — enumerate `/etc/sudoers.d/` | still not readable by the implementing account. **It remains a required pre-readiness condition and is the Security Reviewer's**, exactly as the review says |
| **Any Git operation that writes** — `git init`, `clone`, `fetch`, `archive`, `cat-file` against a store that does not exist | no such store exists, and creating one is a host change. **The `git` behaviour §2.12.5a relies on — object addressing, `--git-dir`, disabled discovery, no ref resolution — is argued from documented Git semantics and from nothing else, and this handback does not claim more** |
| **Any verification that Algorithm D runs**, that `DEP-01 … DEP-09` fire, or that a rollback restores a predecessor | the same authorization. **Owner: Operations Owner** |
| **The Python, web and Node suites** | no source file, test, migration, configuration or dependency changed. A green run would be a statement about a tree this remediation did not alter |
| **Formatter, linter and type checker** | **none is configured** in this repository (§8.1). Stated as not configured, never as passed |
| **The privileged probe, `verify-capability`, `init-generation`, `freedom-journal-admin`, `capsh`, `setpriv`, `systemd-run`, `chattr` and any `sudo` path** | unauthorized, and none of their code changed |

| Run | Result |
|---|---|
| Repository-wide searches for every membership, digest and identity form named in §7 | as tabulated in §9 |
| Independent re-derivation of every count, estimate and PERT figure | agrees, both routes, §7 check 5 |
| Markdown whitespace, table-shape, heading-order and link checks | §7 check 6 |
| Reading of the received security review, the package plan, the logical schema, `.agents/AGENTS.md` and `docs/implementation-plan.md` | — |

---

## 9. Stale-form search results, each hit classified

| Form | Hits | Classification |
|---|---|---|
| `its own only` / *"no supplementary groups"* as a claim about `freedomcoord` or `freedomsheet` | package plan §2.12.2; logical schema §4.3.2 | **Two live hits, both the P5.0-SR2 defect, both withdrawn.** The package plan's is replaced by the canonical table; the logical schema's prose sentence is deleted and its table demoted to a citation. **Both withdrawals are stated as withdrawals** |
| *"in no group any service identity holds"* | package plan §2.12.2 | **One live hit, withdrawn** and replaced by three separately testable claims |
| `freedomjournal` membership stated outside §2.12.2 | package plan §2.13.3, §2.13.5c, §2.12.7; logical schema §4.3.2, §4.3.5 | **Five live hits, all converted to citations.** §2.13.3 now says *"its membership is stated in §2.12.2 and nowhere else"*; §2.13.5c says every group name is taken from §2.12.2; §4.3.2 carries a reproduction with an explicit *"if these disagree, §2.12.2 is correct and this is a defect"* |
| `E8` with `freedomcoord` only | package plan §2.13.5c identity table and invocation table; R9 and R10 handbacks | **Two live hits corrected**; the handback copies are history and are left |
| *"the recorded SHA-256 of each deployed file … compared against that commit"* | package plan §2.12.5 | **One live hit, withdrawn** with the sentence quoted and the reason stated before §2.12.5a replaces it |
| `deployment_manifest_digest()` described as provenance | package plan §2.13.2c, §2.13.5a, §2.13.6 **J-22**, logical schema §3.7 | **Four live hits, all narrowed rather than deleted.** The function's contract is unchanged and preserved; what changes is that provenance is now a **different** function with a **different** trusted side, and **J-27** is added beside **J-22** precisely because the two check different things |
| `thirteen falsification rows` | package plan §2.13.5c heading and closing paragraph; logical schema §9 | **Corrected to fourteen** in live text; every other occurrence is inside a retained revision-10 or revision-11 change table and is history |
| `six tables` | logical schema §0.2, §3.0, §4.3.1, §4.3.5, §5, §6, §7 | **Six live hits corrected to seven**; the occurrences inside retained change tables are history |
| `fifty identifiers and eighty-eight cases` | package plan §2.13.8, §3 WP-8, §5.1 | **Corrected in live text**; retained inside the revision-10 and revision-11 change tables, where it is the historical figure |
| `3.5–4.5 reviewer-days`, `eleven surfaces` | package plan §4, §9.2, §7.4 D-5.0-1; brief | **Corrected in live text to 4.5–5.5 and twelve**; retained inside change tables and superseded register entries |
| `Security Reviewer: unnamed` | package plan header, §4 *Named roles*, §9.3 condition 4; registers | **All live hits corrected**, and **stop condition 4 is extended** rather than merely satisfied. Every remaining occurrence is inside a superseded block or a retained review quotation |
| `35.5` as this package's estimate | package plan §5.1, R-03 row | **One live hit, and it was stale before this remediation** — the revision-4 figure, carried through six estimate changes. **Corrected to 47.6 and reported here rather than absorbed** |

**One pre-existing stale statement, unrelated to either finding, was found by
this sweep and is corrected**: §5.1's R-03 estimate. It is reported rather than
silently fixed, because a correction that hides its own history is the class of
defect §2.13.1 has now recorded six times.

---

## 10. What the findings and decisions look like after this remediation

- **P5.0-SR1** — **remediated on paper; not closed.** The Security Reviewer
  decides. The design's own honest limit is **R-5.0-15**.
- **P5.0-SR2** — **remediated on paper; not closed.** Check **C-4** is
  specified as `JNL-52` and **has not been run**.
- **P5.0-R5** — **remains Blocking**, and is unchanged by this remediation.
- **P5.0-R1**, **P5.0-R4** — **remain open**, and nothing here touches them. No
  operational evidence is claimed passed.
- **P5.0-R2** — **remains closed.**
- **C-1** — still **not completed**. It is the reviewer's, and this remediation
  neither performs nor discharges it.
- **C-2** — completed by the review as an inventory, and **§8.1 still records the
  host-wide set-user-ID audit as not run by the implementer.**
- **C-3**, **C-4** — **not run by design**; both are operational evidence under
  A-5.0-5, and **C-4** now has a specified test.
- **R-5.0-12, R-5.0-13, R-5.0-14** — unchanged and **unaccepted**.
  **R-5.0-15, R-5.0-16** — **new, proposed, unaccepted.**
- **D5.0-9 … D5.0-13 / OD-62 … OD-66** — **all Open.** No decision number and no
  option is added; **OD-65's scope is extended** and **OD-66 gains an unadopted
  option A-3**. **Nothing here rules any of them.**
- **A-5.0-3, A-5.0-4, A-5.0-5** — **unconfirmed**; A-5.0-5 is widened again.
- **Package 5.0** — **`not ready`.** Implementation, migration `0014`,
  deployment, cutover and Package 5.1+ remain unauthorized.

---

## 11. Confirmation that no finding is claimed closed and no unauthorized action occurred

- **No finding is claimed closed**, and no assumption confirmed.
- **No decision is ruled.** OD-62 through OD-66 remain Open; no decision number
  and no option is added; **OD-66 option A-3 is raised and explicitly not
  adopted**.
- **Package 5.0 is not claimed ready**, and §9.4 concludes the opposite.
- **No implementation or environment change occurred.** No production code, no
  migration `0014`, no table, no database role, no operating-system account or
  group, no `pg_hba.conf`, `pg_ident.conf` or `sudoers` entry, no credential, no
  Google access change, no configuration or environment change, no directory,
  file, file mode or filesystem attribute, no deployment, no service restart, no
  `systemd-run`, `chattr`, `setpriv`, `capsh` or privileged probe, no data
  mutation, no Sheet access, no authority cutover, no Package 5.1+ work.
- **No host object named by §2.12.5a or §2.12.2 was created.**
  `/var/lib/freedom-sheet-writer`, `/opt/freedom-blades/coordinator`,
  `/opt/freedom-blades/sheet-writer`, the bare object store, the approved-revision
  record and the provenance record **do not exist on this host and were not
  created**; `freedomcoord`, `freedomsheet`, `freedomjournal` and `fbprobe`
  **do not exist and were not created**.
- **No Git repository was written.** No `init`, `clone`, `fetch`, `commit`,
  `tag`, `push` or object write of any kind was performed against any store, and
  **no signing key, keyring or signature exists or was created**.
- **The only changes are to documents**: the package plan, the logical schema,
  this handback, the security-review briefing pack, implementation-plan §20, and
  the five governance registers. **`docs/review/phase-5-0-security-review.md` is
  deliberately not edited** — it is a received review artifact.

---

## 12. What is requested next

1. **An independent security re-review of revision 12**, which this submission
   requires and does not pre-empt. The most useful disagreements would be: a
   route into the object store short of root; a gap in the SHA-1 argument; a
   window in `D0 … D8` where the deployed root is live and `PVR` is not; an
   ordering in which `C0`'s four-way comparison can be satisfied by an attacker
   who has not also reached the database; a mechanism in this design that **does**
   decide identity from a group; or a residual — **R-5.0-15** in particular —
   that is understated.
2. **The rest of the §9.2 pass**, which is outstanding in full at **4.5–5.5
   reviewer-days over twelve surfaces**. The revision-12 remediation is not that
   pass and must not be cited as one.
3. **Check `C-1`**, which remains the reviewer's and remains not completed.
4. **A ruling on whether `approved_source_revisions` and its approval procedure
   belong in the decision register in their own right.** This submission treats
   them as content of **D5.0-12 / OD-65** and **D5.0-13 / OD-66 option A**, and
   raises no new decision number. If the Acceptance Authority judges that a
   release-approval record with a custody procedure is a decision of its own,
   that is a ruling to make, not one made here.
5. **Nothing else.** No implementation, migration, host change, privileged probe,
   deployment, cutover or Package 5.1+ work is requested or authorized.
