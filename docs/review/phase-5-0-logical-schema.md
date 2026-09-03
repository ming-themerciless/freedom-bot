# Package 5.0 — logical schema and schema decision table

Status: **Proposed, revision 12 (remediation R11), answering security-review
findings P5.0-SR1 and P5.0-SR2. Awaiting independent security re-review. Not
accepted, not implemented, and no migration is written.**
This artifact exists to be independently reviewed
*before* any migration or production code, as the Phase 5.0 handover and
implementation-plan §7.3.1 require. Nothing below is authority until Peter
Duscha records the architecture/schema gate decision on the Independent
Reviewer's and the Data Owner's recommendation.

**Security review of revision 11, 2026-08-31: changes requested; no readiness
recommendation.** Two findings. **P5.0-SR1 — Blocking** — the deployment
integrity check can be skipped silently: it compares a digest of the live
deployed bytes with a caller-supplied copy of that value, which is consistency
after deployment and not provenance from the reviewed commit, and no step refuses
when it is omitted. **P5.0-SR2 — Important** — the operating-system identity
contract contradicted the journal group contract. **Unlike R6 … R10, this
remediation has schema-visible consequences**: revision 12 adds a **seventh
table, `approved_source_revisions`** (§3.8), **four columns** on
`sheet_writer_journal_generations` including a **`NOT NULL` foreign key** to it
(§3.7), the grants and append-only trigger that follow, and three corrected
passages in §4.3.2. The finding's *"prevents activation"* requirement is
discharged **structurally**: a generation whose reviewed source was never
approved cannot be inserted, and §3.4's activation trigger requires a registered
generation. **Nothing is claimed closed**, and an independent security re-review
of revision 12 is required.

**Independent re-review of revision 11, 2026-08-31: R10-A through R10-C are
materially addressed on paper.** No new Blocking or Important schema/design
finding was identified. This closes the R10 remediation request only; it does
not accept this schema, close P5.0-R5, confirm A-5.0-5, or authorize migration
or implementation. P5.0-R5 remains Blocking pending authorized operational
evidence, and the package remains `not ready` while its decisions, Security
Reviewer and other readiness conditions remain open.

**Independent re-review of revision 10, 2026-08-31: changes requested;
P5.0-R5 remains Blocking.** R9-A and R9-B are materially improved, but the
R9-C executable-identity contract is not constructible as written. The E2–E6
`setpriv` recipes name the unsupported securebit `keep_caps`; E8 declares an
empty bounding set without requesting one; and E7 omits explicit inheritable
and ambient masks. The affected `JNL-49`/`JNL-50` evidence would be
inconclusive at its mandatory identity assertion. This is a host/evidence
contract defect and changes no schema object or schema guarantee. Remediation
R10 and another independent re-review are required before any migration or
implementation.

**Independent re-review of revision 9, 2026-08-30: changes requested; P5.0-R5
remains Blocking.** The R8 deployment-digest, cleanup-state and forged-host-
identity corrections are materially addressed, but the authority model omits
the owner-or-`CAP_FOWNER` prerequisite for `FS_IOC_SETFLAGS`. Consequently its
root-owned seal/archive falsification combinations and `CAP_LINUX_IMMUTABLE`-
only evidence are not executable as written, and the A1–A6 independence claim
contradicts F-1a's A3-implies-A2 qualification. These are host-design and
evidence-contract defects rather than accepted schema changes. Revision 10 and
remediation R9 are required; no migration or implementation is authorized.

**Revision 11 is remediation R10, and the findings are conceded.** The
schema-visible consequences are stated in *What changed in revision 11* below and
are **nil**: **no column, constraint, index, trigger, sequence, command, table or
vocabulary changes, and no schema guarantee moves.** The defect is entirely
host-side and narrower than R9's: revision 10's authority model was right, and
the **commands that were supposed to put a process in front of the kernel checks
it describes did not run**. `setpriv(1)` from util-linux 2.39.3 rejects the
securebit `keep_caps`; the same manual page states that the kernel does not
permit capabilities to be **added** to a bounding set, which `E2 … E6` asked for;
`E8` declared an empty bounding set and dropped nothing; and `E7` wrote dashes
where complete inheritable and ambient masks were required. The companion
rebuilds `E1 … E8` on **`capsh(1)`**, whose manual documents that it acts on its
arguments *"in the order they are provided"*, and carries a
**mask-versus-recipe comparison** so that every declared mask is derived from its
invocation.

**Nothing in this artifact consumed the broken recipes**, which is why the
schema-visible consequence is nil rather than small: the recipes are an evidence
*construction* detail, and this document references the identities only through
§9's evidence mapping and §4.3.8's Band 3, both of which name **which** identity
executes a case and never **how** it is built. Those references are corrected in
wording so that no reader is sent to a withdrawn recipe. **The property this
artifact rests on is unchanged**: **`A9`, PostgreSQL mutation authority, is held
by no principal in this design.** **Claude claims no finding closed**, no option,
risk, decision or schema object is adopted or closed by R10, and **no migration
may be written before an independent re-review of revision 11**.

**Revision 10 was remediation R9, and the finding was conceded. Retained as history; revision 11 is the current artifact.** The schema-visible
consequences are stated in *What changed in revision 10* below and are, again
deliberately, small: **no column, constraint, index, trigger, sequence, command,
table or vocabulary changes.** The defect is host-side and is a **wrong model of a
Linux permission check**: `FS_IOC_SETFLAGS` requires the caller's effective UID to
match the inode's owner **or** `CAP_FOWNER`, in addition to `CAP_LINUX_IMMUTABLE`
for the immutable and append flags, and revision 9's authority register recorded
only the second half. Two statements in **this** artifact consumed the incorrect
register and are corrected: §3.7's *What this table uniquely can do* named the
F-1b combination as `A1 + A2 + A3`, and §3.7.1's seal-integrity row and §9's
threat-model row described a nine-authority register. **The register is now
eleven authorities**, with `A10` and `A11` carrying the owner authorization, and
**eleven of thirteen falsification rows gain a prerequisite** — every one of which
makes the alteration **harder** to construct, so **no schema guarantee moves**.
The property this artifact rests on is unchanged and is re-stated with its new
label intact: **`A9`, PostgreSQL mutation authority, is held by no principal in
this design.** **Claude claims no finding closed**, and no migration may be
written before re-review.

**Independent re-review of revision 8, 2026-08-30: changes requested; P5.0-R5
remains Blocking.** Revision 8 consumes the supplied deployment digest before
its stated equality validation; gives cleanup failure mutually exclusive
residue outcomes; treats `CAP_LINUX_IMMUTABLE` alone as archive write authority
despite DAC; and claims the registered row detects a forged matching
`/etc/machine-id` although it contains the same value. These are host-design and
evidence-contract defects, not accepted schema changes.

**Revision 9 was remediation R8, and all four findings were conceded. Retained as history; revision 10 is the current artifact.** The
schema-visible consequences are stated in *What changed in revision 9* below and
are, again deliberately, small: **no column, constraint, index, trigger,
sequence, command, table or vocabulary changes.** All four Blocking defects are
host-side — a validation's source and position, a cleanup contract's outcome
count, a capability model that credited flag control with discretionary access,
and a detector that compares two copies of one recorded value — and none of them
adds or removes a schema object. **Two of the four correct claims this artifact
itself made**: §3.7's `host_machine_id` rule said a journal restored onto another
host *"is refused"*, which is untrue when `/etc/machine-id` there is rewritten to
the recorded value; and §3.7's `writer_deployment_digest` note described a value
whose validation, in the companion, compared it against a copy of itself.
**Claude claims no finding closed**, and no migration may be written before
re-review.

**Independent re-review of revision 7, 2026-08-30: changes requested; P5.0-R5
remains Blocking.** Algorithm C checks a probe result at C0 before C1 creates it;
S4-2 lacks a positive DAC control for its exact target; and the attacker classes
do not match the capabilities required by their falsification rows. These
host-side defects invalidate evidence claims traced into this schema even though
they add no schema object. Remediation R7 and another independent re-review are
required. No migration or implementation is authorized.

**Independent re-review of revision 6, 2026-08-30: changes requested; P5.0-R5
remains Blocking.** The schema said `append_only_probe_digest` covers all four
probe stages, but package-plan Algorithm C embedded only stages 1–3 and ran stage
4 later at deployment. The claimed immutable evidence therefore could not have
the documented contents or lifecycle. The package plan also overclaimed
writer-only seal falsification: V-W did not authenticate `BND.sealed_at`, so
changing only that binding field was not refused without PostgreSQL. `JNL-32` was
internally inconsistent, because W9 must refuse an absent `FS_APPEND_FL` before
W17 can append a startup record. The active handoff was also corrupted and
truncated.

**Revision 8 was remediation R7, and all four of its findings were conceded**
(retained below). The
schema-visible consequences are stated in *What changed in revision 8* below and
are, again deliberately, small: **no column, constraint, index, trigger,
sequence, command, table or vocabulary changes.** All three Blocking defects are
host-side — an algorithm's step order, a probe case's target, and a threat
model's classification axis — and none of them adds or removes a schema object.
What changes here is that §3.7's column notes, §3.7.1's enforce-versus-record
division, §4.3.8's evidence bands and §9's traceability rows now describe
artifacts that exist as described **and can be produced in the order the package
plan states**. **Claude claims no finding closed**, and no migration may be
written before re-review.

**Revision 7 is remediation R6, and all four of its findings were conceded**
(retained below). Its schema-visible consequences were likewise none: `sealed_at`
was never a database column, and the probe's stage placement is a host-side
lifecycle question.

**Independent re-review of revision 5, 2026-08-29: P5.0-R5 remained
Blocking.** The seal contained `genesis_record_digest` while the genesis record
hashed `seal_digest`, so the registered generation could not be constructed. The
package plan also denied the writer read access to the seal it must validate and
specified a capability probe whose ordinary permissions masked append-only
enforcement. `CHECK (append_only_verified)` proved only that the coordinator
supplied `true`; it could not prove a host probe occurred. **Revision 6 is
remediation R5**, and the four corrections land here as follows: the construction
becomes acyclic (package plan §2.13.5a), the seal becomes readable by the writer
through a third system group (§2.13.3), the probe becomes valid and
non-destructive (§2.13.2a), and **`append_only_verified` and its `CHECK` are
withdrawn from §3.7** and replaced by a probe-report digest, version and timestamp
whose semantics are stated in new **§3.7.1**. **Claude claims no finding closed**,
and no migration may be written before re-review.

**Independent re-review of revision 4, 2026-08-29: changes requested.** P5.0-R1
remains Blocking and **P5.0-R5** is raised Blocking. The journal was placed under
`/run`, a separate volatile `tmpfs` filesystem on the reviewed host, while
`chattr +a` support was inferred from `/opt/freedom-blades` being ext4. Reboot,
replacement, missing or corrupt state could therefore turn unknown history into
an apparently empty unresolved set. The text also denied dependency on journal
completeness while the activation trigger required `dispatch_journal_clear`.
P5.0-R4's identity design substantially answers its design finding; its
operational evidence and the governing decisions remain open. P5.0-R2 remains
closed.

**Revision 6 is remediation R5, and its schema consequences are narrower than
revision 5's but not editorial.** Three of the four R5 findings are host-side and
land in package plan §2.13; the fourth, **R5-D**, is a schema finding and lands
here. What changes in this artifact:

- **`append_only_verified BOOLEAN CHECK (append_only_verified)` is withdrawn**
  from `sheet_writer_journal_generations` (§3.7), together with every sentence
  that described it as making the capability probe *"enforced by a constraint
  rather than by a procedure step somebody could skip"*. A `CHECK` on a supplied
  Boolean constrains the supplied value; it cannot observe a host;
- **four columns replace it**: `seal_body_digest`, `append_only_probe_version`
  (a closed vocabulary), `append_only_probe_digest` and `append_only_probe_at`
  (§3.7). The probe report itself lives inside the `chattr +i` seal, so the
  registered digest is an attestation **bound to a re-derivable artifact**;
- **new §3.7.1** states, line by line, **what PostgreSQL enforces and what it
  merely records**, names the authenticated actor and the immutable fields, and
  states what actually establishes that the probe ran;
- **§3.7's `genesis_record_digest` and `seal_digest` gain their construction
  order** — the genesis record is anchored to `seal_body_digest`, not to
  `seal_digest`, and `seal_digest` is a leaf no on-disk artifact contains
  (package plan §2.13.5a);
- **§4.3.8 Band 3 is corrected**: without A-5.0-5 no generation can be *created*,
  because `init-generation` refuses — a host-side refusal, not a database one.

**The activation trigger's fifth condition (§3.4), the three journal columns on
`migration_quiescence_evidence` (§3.5), the fifth command, the fifth idempotency
scope and the fifth audit action are unchanged.** So is the table count: **six**.

**Retained from revision 5**, whose schema consequences were real rather than
editorial. The journal's storage, identity, integrity format, failure states and
privileged lifecycle are specified in **package plan §2.13**. What landed *here*
was:

- **a sixth table, `sheet_writer_journal_generations`** (§3.7) — an append-only,
  single-linear-chain register of journal generations, so the activation trigger
  can refuse **stale, cross-generation and unregistered** journal evidence.
  Revision 4 could not refuse those, because the database did not know a
  generation existed;
- **three new columns on `migration_quiescence_evidence`** (§3.5) binding a
  `dispatch_journal_clear` row to the generation, the last sequence and the head
  digest it was observed against;
- **a fifth condition on the activation trigger** (§3.4), and a **fifth command**,
  `RegisterJournalGeneration` (§0.3);
- **§2.9, new**, which states exactly what journal completeness is trusted to
  establish and **withdraws revision 4's claim that nothing depends on it**.

**Claude claims no finding closed.** P5.0-R1's Sheet half is unchanged and still
open; **a durable journal is not a barrier and is not offered as one** (§2.9,
package plan §2.13.10), and revision 6 narrows it by no cases at all. P5.0-R4's
operational evidence is not claimed passed. P5.0-R2 remains closed, and OD-55 and
OD-58 remain preserved.

Date: 2026-08-30 · Package: 5.0 — Migration and cutover harness

Prepared by: Claude, implementer and working Technical Lead (designated, OD-61)

Reviewed by the author against: implementation plan §7, §7.3, §7.3.1, §7.6,
§7.7, §9.3, §12.0, Phase 5, §13.2, §13.3, §14, §15.1; ADR 0003; ADR 0005;
`.agents/AGENTS.md` (*Database migration*, *Product invariants*, *Configuration
and secrets*); `docs/contracts/phase-3-logical-schema.md`; the live schema of
`freedom_test`; `infra/postgresql/runtime-grants.sql.tmpl`;
`infra/systemd/freedom-bot.service.tmpl`, `freedom-web.service.tmpl`,
`freedom-worker.service.tmpl`; `connectors/sheets.py`; `config.py`;
`tools/web_operator.py`;
`migrations/versions/0002_foundry_snapshot_and_identity.py` and `0013`; and
`docs/project-management/data-migration-manifest.json`.

Companion document: [`phase-5-0-package-plan.md`](phase-5-0-package-plan.md).
The package plan owns scope, estimate, risk, the fencing option comparison and
the gates; this document owns the physical-design proposal alone.

> **No implementation or environment change occurred.** No production code, no
> migration `0014`, no table, no configuration or environment change, no
> credential, database role or Google access change, no operating-system account
> **or group**, **no directory, file, file mode or filesystem attribute**, no
> deployment, no service restart, no data mutation, no Sheet access, no authority
> cutover, no Package 5.1+ work. `/var/lib/freedom-sheet-writer` does not exist on
> this host and was not created; `freedomjournal` is a proposed group that does not
> exist. **No Git repository, bare object store, approval record or provenance
> record was created, fetched, written or signed anywhere**, and no `git` command
> that writes was run. The changed files are documents and registers.

## What changed in revision 12, and why

The Package 5.0 security review returned **changes requested** on 2026-08-31 with
two findings. **This is the first remediation since R5 with schema-visible
consequences**, and they are stated before anything else so that a reader is not
told *"nil"* five times and then handed a table.

| Input | Revision 11 | Revision 12 |
|---|---|---|
| **P5.0-SR1** — *Blocking; the deployment integrity check can be skipped silently* | `writer_deployment_digest` was the only provenance the schema carried, and it is a digest of the deployed bytes compared with a caller-supplied copy of itself. **The schema had no representation of a reviewed commit at all** | **New §3.8, `approved_source_revisions`** — the seventh table — holding the `component`, `source_commit`, `source_tree_id`, `source_manifest_digest`, `review_reference`, approver and approval time of each revision a review approved, append-only, `SELECT, INSERT` for the coordinator and **nothing for the runtime role**. **§3.7 gains four columns**: `source_commit`, `source_tree_id`, `source_manifest_digest` and `approved_source_revision_id`, the last a **`NOT NULL` foreign key** with `RESTRICT`, plus a **composite foreign key** so the registered copies cannot disagree with the approved row. **That is the whole of the "prevents activation" requirement**: a generation whose reviewed source was never approved cannot be inserted, and §3.4's activation trigger requires a registered generation, so no procedure step is load-bearing |
| **P5.0-SR2** — *Important; the OS identity contract contradicts the journal group contract* | §4.3.2's prose said `freedomcoord` has *"no supplementary groups"* while its own table gave it `freedomjournal`, mirroring the package plan's contradiction | **§4.3.2 corrected and demoted to a citation.** The prose sentence is **withdrawn**; the membership table becomes a pointer to package plan **§2.12.2**, which is now the single canonical primary/supplementary membership table; and the sentence *"distinct from every service identity and in no group any of them holds"* is replaced by the three claims that are actually true. **No authentication or authorization matrix moves** — the group carries no database privilege, which §4.3.5 already said |
| Table count | six | **seven.** `approved_source_revisions` (§3.8) |
| Columns on `sheet_writer_journal_generations` | as revision 6 left them | **four added**, one of them a `NOT NULL` FK. **None is withdrawn and none changes type** |
| Constraints | as revision 6 left them | **five added** — the two foreign keys, a composite uniqueness target on §3.8, a lowercase-hex check on the three new digest/object columns, and §3.8's own uniqueness pair. **None is withdrawn** |
| Triggers, sequences, commands, vocabularies | five trigger conditions, two sequences, five commands, `jnl-probe-1` | **Unchanged**, except that `reject_history_mutation` is installed on the seventh table too. **No new command**: `RegisterJournalGeneration` gains a lookup, not a sibling. **No closed vocabulary widens**; `component` is a new closed vocabulary of two values |
| Authority register and falsification rows | eleven authorities, thirteen rows | **Eleven authorities**, with **`A5` widened** to the three root-owned provenance artifacts; **fourteen rows**, **F-13** added — the deployment substitution, refused by this schema's foreign key and by nothing else once the host copies agree |
| Evidence band | fifty identifiers, eighty-eight cases | **fifty-three identifiers, one hundred and fourteen cases.** `JNL-46` 5 → 9; new `JNL-51` (eight), `JNL-52` (eight), `JNL-53` (six) |
| Fail-closed conditions | twenty-five, `SW-J01 … SW-J25` | **twenty-eight, `SW-J01 … SW-J28`**, plus the deploy step's own `DEP-01 … DEP-09`, which belongs to neither actor and is not in §2.13.6 |
| Residuals | R-5.0-12, R-5.0-13, R-5.0-14 | **plus R-5.0-15** — the approval record's integrity is root ownership, so **A5** rewrites every host copy and **A5 + A8** also registers the revision it approved. **This table refuses the A5-only case and not the A5 + A8 case**, exactly as §3.7 already refuses F-1b and not F-1b-plus-superuser — and **R-5.0-16**, the availability cost of refusing an unprovenanced deployment |
| **The preserved corrections** | — | **§0.1, §0.2, §2.1, §2.2B, §2.4, §2.5, §3.7.1 and the R8-A/R8-B/R8-D and R9-A/R9-B corrections are preserved unchanged in substance.** §3.7 is **extended**, not rewritten; no existing column, constraint or claim is weakened |
| **P5.0-R1**, **P5.0-R4**, **P5.0-R5** | open / open / Blocking | **Unchanged.** No operational evidence is claimed passed and **P5.0-R5 remains Blocking** |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged** |
| Decisions | D5.0-9 … D5.0-13 / OD-62 … OD-66 open | **All still Open, and none is adopted, closed or added by R11.** OD-65's scope is extended and OD-66 gains an unadopted **option A-3** |

---

## What changed in revision 11, and why — retained

Revision 10 was returned **changes requested** on 2026-08-31 with P5.0-R5 still
Blocking: R9-A's and R9-B's corrections were accepted as materially improved, but
R9-C's executable-identity recipes do not construct the identities they declare.
**It is not a schema-object defect, and it is not even a schema-claim defect**:
revision 11 adds, removes and alters **no** column, constraint, index, trigger,
sequence, command, table or closed vocabulary, and **no statement in this artifact
consumed a launch recipe**. What changes here is wording in two places that name
the identities, so that no reader is directed to a withdrawn construction.

| Input | Revision 10 | Revision 11 |
|---|---|---|
| **R10-A** — *the launch recipes were not valid for the tool they named* | **E2 … E6** were built with `setpriv --securebits=+keep_caps,+no_setuid_fixup …` | **Host-side, package plan §2.13.5c, rewritten.** util-linux 2.39.3's `setpriv(1)` documents `keep_caps` as *"not allowed"* because `execve` clears it, so those five commands exit **127** before any identity exists. The mechanism becomes **`capsh(1)`** (libcap 2.66, `/usr/sbin/capsh`, `root:root 0755`, **no file capabilities**, already installed), whose manual documents that it acts on its arguments *"in the order they are provided"* — which `setpriv(1)` does not, and on which every declared mask depends. A **seven-step construction** is stated with the kernel rule each step relies on, and `+keep_caps` is used nowhere. **No schema trace at all**: this artifact never named a construction |
| **R10-B** — *three identities declared masks their recipes did not produce* | **E8** declared `CapBnd=0x0` and dropped nothing; **E7** wrote dashes for inheritable and ambient; and — found by the mechanical comparison, not by the re-review — **E2 … E6** asked `--bounding-set=+…` to **add** to a bounding set, which the same manual page says the kernel does not permit | **Host-side, package plan §2.13.5c.** `E1 … E8` now carry exact effective UID, GID, the exact supplementary-group list, exact `CapPrm`/`CapEff`/`CapInh`/`CapAmb`/`CapBnd` **and securebits**, each with a complete invocation, and a **mask-versus-recipe comparison table** derives every declared cell from its command line. E7's masks are read from the host and labelled environment-dependent. **No schema trace**: §4.3.8 Band 3 counts cases, not identities |
| **R10-C** — *revalidate the dependent evidence* | `JNL-50` case 7 and `JNL-49` case 11 named **E2** as the positive control for an **E4** refusal | **Host-side, package plan §2.13.8.** The isolating control becomes **E6**, which differs from E4 by `CAP_FOWNER` alone; E2 is retained as a **corroborating** control by the ownership route. `JNL-50` case 4 gains a second control form — hold the identity fixed, vary the inode's owner. **The case counts do not move.** Its schema trace is §4.3.8 Band 3 and §9's threat-model row, corrected in wording only. **`A-5.0-5` is widened and remains unconfirmed; no privileged case is claimed to have run** |
| Falsification-row count | thirteen | **Unchanged at thirteen** — F-1a, F-1b and F-2 … F-12. R10 touched no row |
| Authority register | eleven (`A1 … A11`) | **Unchanged at eleven.** Every label, meaning and holder row is carried forward verbatim in substance, so every reference in this artifact remains valid |
| Table count, columns, constraints, triggers, evidence columns, commands, vocabularies | six tables, five trigger conditions, three journal evidence columns, five commands, `jnl-probe-1` | **Unchanged, every one.** Revision 11 has no schema-adjacent movement whatever |
| Evidence band | fifty identifiers, eighty-eight cases | **Unchanged: fifty identifiers, eighty-eight cases.** `JNL-49` twelve, `JNL-50` twelve. **No identifier and no case is added, removed or renumbered**, because R10 corrects how an identity is built and which identity is the control — not which cases exist |
| **The preserved corrections** | — | **§2.13.2b's cleanup state machine, §2.13.2c's deployment digest, F-7's withdrawn detector and revision 10's R9-A/R9-B authority corrections are preserved unchanged in substance**, as the R10 brief requires. **No corrected identity produced a conflict with any of them**, so nothing was stopped and reported under the brief's conflict clause |
| **P5.0-R1**, **P5.0-R4** | unchanged | **Unchanged.** §2.2B and §2.8 stand; §4.3's boundary and evidence plan stand; no operational evidence is claimed passed |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged.** §2.1's matrix, §2.5's effective-time model, no telemetry table and no ledger table |
| Decisions | D5.0-9 … D5.0-13 / OD-62 … OD-66 open | **All still Open, and none is adopted, closed or added by R10.** The Security Reviewer remains **unnamed** *(named on 2026-08-31, after this revision was written — see the status block)* |

---

## What changed in revision 10, and why — retained

Revision 9 was returned **changes requested** on 2026-08-30 with P5.0-R5 still
Blocking: its replacement authority model omits half of a kernel permission
check. **It is not a schema-object defect**, and revision 10 adds, removes and
alters **no** column, constraint, index, trigger, sequence, command, table or
closed vocabulary.

| Input | Revision 9 | Revision 10 |
|---|---|---|
| **R9-A** — *the inode-flag authority model omitted the owner check* | **A1** was given as *"flag control"* with minimum holder `CAP_LINUX_IMMUTABLE`, and every root-owned-inode combination was written as `A1 + A3` or `A1 + A4` | **Host-side, package plan §2.13.5c, redesigned.** `FS_IOC_SETFLAGS` requires effective UID equal to the inode's owner **or `CAP_FOWNER`**, *in addition to* `CAP_LINUX_IMMUTABLE` for `FS_IMMUTABLE_FL`/`FS_APPEND_FL`; `CAP_DAC_OVERRIDE` is not a substitute. **A1** is narrowed to the special-bit half; **A10** (owner authorization over the `freedomsheet`-owned journal) and **A11** (owner authorization over the root-owned seal and archive) become separate rows; the register grows to **eleven** authorities and **eleven of thirteen falsification rows gain a prerequisite**. Its schema trace is §3.7's *What this table uniquely can do*, where the F-1b combination becomes **`A1 + A2 + A3 + A10 + A11`**, and §9's threat-model row. **Every change makes an alteration harder to construct, so no claim this table makes is weakened and none is strengthened** |
| **R9-B** — *the register asserted independence and reasoned from implication* | *"A1 … A6 confer nothing on each other"*, and, under F-1a, *"every real holder of A3 also holds A2"* | **Host-side, package plan §2.13.5c.** The register keeps the independence claim **for the primitives**; a new **holder table** states which identities on this host bundle which rows; and every falsification row is assessed against its minimum combination **and** against the smallest identity that can actually hold it. Its schema trace is §3.7: **F-1b is still refused here and nowhere else**, and that is unaffected, because it rests on **`A9` being held by nobody** rather than on any statement about which host authorities imply which |
| **R9-C** — *the executable evidence asserted a result the kernel does not produce* | `JNL-50` case 9 had a non-root `CAP_LINUX_IMMUTABLE`-only identity clear `+i` *"successfully"*; `--ambient-caps` shorthand was treated as a capability-set specification | **Host-side, package plan §2.13.5c and §2.13.8.** Eight executable identities **E1 … E8** with complete permitted/effective/inheritable/ambient/bounding sets and securebits; `JNL-49` and `JNL-50` at **twelve cases each**, every negative flag case carrying a positive control. Its schema trace is §4.3.8 Band 3's case counts and §9's threat-model row. **`A-5.0-5` is corrected and remains unconfirmed; no privileged case is claimed to have run** |
| Falsification-row count | thirteen | **Unchanged at thirteen** — F-1a, F-1b and F-2 … F-12 |
| Authority register | nine (`A1 … A9`) | **eleven** (`A1 … A11`). **`A2` … `A9` keep their labels and meanings**, so every reference in this artifact remains valid; `A1` is narrowed and `A10`/`A11` are added |
| Table count, columns, constraints, triggers, evidence columns, commands, vocabularies | six tables, five trigger conditions, three journal evidence columns, five commands, `jnl-probe-1` | **Unchanged, every one.** Revision 10 has no schema-adjacent movement at all: `jnl-probe-1` denotes the same four-stage procedure, and the corrected register describes the host's permission model rather than anything the database records |
| Evidence band | fifty identifiers, eighty-four cases | **Fifty identifiers, eighty-eight cases** — **no identifier added** (§4.3.8 Band 3, package plan §2.13.8) |
| **The preserved R8 corrections** | — | **§2.13.2b's cleanup state machine, §2.13.2c's deployment digest and F-7's withdrawn detector are preserved unchanged in substance**, as the R9 brief requires. §3.7's bounded `host_machine_id` rule, §3.7.1's host-identity row and §9's forged-host row are carried forward **unchanged** |
| **P5.0-R1**, **P5.0-R4** | unchanged | **Unchanged.** §2.2B and §2.8 stand; §4.3's boundary and evidence plan stand; no operational evidence is claimed passed |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged.** §2.1's matrix, §2.5's effective-time model, no telemetry table and no ledger table |

---

## What changed in revision 9, and why — retained

Revision 8 was returned **changes requested** on 2026-08-30 with P5.0-R5 still
Blocking: four Blocking internal inconsistencies. **None of the four is a
schema-object defect**, and revision 9 adds, removes and alters **no** column,
constraint, index, trigger, sequence, command, table or closed vocabulary. What
was wrong was again what this artifact and its companion *said about* artifacts
that live on the host — where a validation happens and what it compares against,
how many states one cleanup failure may leave, what a Linux capability confers,
and whether a comparison between two copies of one value can detect a forgery of
that value — and that is what changes.

| Input | Revision 8 | Revision 9 |
|---|---|---|
| **R8-A** — *the deployment digest was consumed before it was validated* | package-plan **C1** passed the operator-supplied `writer_deployment_digest` to the probe, which copied it into the report; **C2** then compared the report's copy with the supplied value — a comparison that passes for any string, made after the step that consumed it | **Host-side, package plan §2.13.2c and §2.13.5a.** A named `deployment_manifest_digest()` is defined — its computor, its exact manifest (every deployed file with path, mode, uid, gid and content digest, plus the unit file **and its drop-ins**), and when it becomes final. **C0 computes it and refuses unless the supplied value equals it**, so the sealed digest is validated against the **deployed bytes**; **C2** keeps a consistency check and **recomputes** to catch a deployment changed since C0. The universal ordering claim is replaced by invariants **I-1 … I-5**. Its schema trace is §3.7's `writer_deployment_digest` note, which now says what the column's value is computed from and where it is validated, and §9's ordered-construction row. **No column, constraint or command changes** |
| **R8-B** — *cleanup failure required two mutually exclusive states* | `JNL-47` asserted no residue after a cleanup failure while `JNL-48(d)` required the planted residue to remain and make the next `C0` refuse | **Host-side, package plan §2.13.2b.** One state machine with three states, in which **“no generation artifact” is unconditional and “no transient residue” is conditional on cleanup success**, and **one** next-invocation behaviour — refuse for operator recovery, never clean or reuse. Its schema trace is the database half of the claim: **`JNL-47` asserts, in all six of its cases, that no row is inserted into `sheet_writer_journal_generations`**, which is unaffected by which residue state the host is in. §4.3.8 Band 3 and §9 carry it |
| **R8-C** — *`CAP_LINUX_IMMUTABLE` was treated as bypassing DAC* | the register gave `K3` and `K4` as capability-only holdings, so a non-root holder was credited with archive and journal writes it cannot perform | **Host-side, package plan §2.13.5c, rewritten again.** **Nine independently constructible authorities** (`A1 … A9`) with a per-row **minimum combination**: flag control is separated from DAC, and the journal, the seal, the archive, the deployment path, host identity, full root, coordinator insertion and PostgreSQL mutation are separate rows. **F-2, F-4 and F-5 each change.** Its schema trace is direct and load-bearing and is **unchanged in substance**: **`A9`, PostgreSQL mutation authority, is held by no principal in this design**, which is what `reject_history_mutation` and the revoked `UPDATE`/`DELETE`/`TRUNCATE` grants of §4.3 establish — the label moves from `K8` to `A9` and the property does not move at all. **F-1b is still refused here and nowhere else** |
| **R8-D** — *F-7 named a host-identity detector that does not exist* | the falsification matrix recorded the coordinator as refusing a forged matching `/etc/machine-id` *"against the registered row — which is not on the restored tree"* | **Corrected here as well as host-side, because the claim was this artifact's too.** §3.7's `host_machine_id` rule said *"A journal restored onto another host is refused"*. **The registered row carries the same value the seal does**, so when `/etc/machine-id` is rewritten to it, **W10 passes and C-d has nothing to disagree with**. The rule is bounded to the **unforged** case, §3.7.1 gains the enforce/record row for it, §9 gains a row, and the outcome is package-plan residual **R-5.0-13**. The alternative — an independent authenticated host-bound value, which **would** add a column to this table — is routed as **D5.0-13 / OD-66 option A-2** and is **not adopted** |
| Falsification-row count | thirteen | **Unchanged at thirteen** — F-1a, F-1b and F-2 … F-12. R8-C re-evaluates rows and R8-D reclassifies one outcome |
| Table count, columns, constraints, triggers, evidence columns, commands, vocabularies | six tables, five trigger conditions, three journal evidence columns, five commands, `jnl-probe-1` | **Unchanged, every one.** Revision 9's only schema-adjacent movement is that `jnl-probe-1` now denotes a four-stage procedure whose deployment digest is **validated against the deployed manifest before the probe consumes it** and whose cleanup has **three named outcomes**. That is a change to the procedure the closed vocabulary names, not to the vocabulary |
| Evidence band | fifty identifiers, seventy-four cases | **Fifty identifiers, eighty-four cases** — **no identifier added** (§4.3.8 Band 3, package plan §2.13.8) |
| **P5.0-R1**, **P5.0-R4** | unchanged | **Unchanged.** §2.2B and §2.8 stand; §4.3's boundary and evidence plan stand; no operational evidence is claimed passed |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged.** §2.1's matrix, §2.5's effective-time model, no telemetry table and no ledger table |

---

## What changed in revision 8, and why — retained

Revision 7 was returned **changes requested** on 2026-08-30 with P5.0-R5 still
Blocking: three Blocking design defects and one Important governance defect.
**None of the four is a schema-object defect**, and revision 8 adds, removes and
alters **no** column, constraint, index, trigger, sequence, command, table or
closed vocabulary. What was wrong was again what this artifact and its companion
*said about* artifacts that live on the host — the order in which they are
created, the target one probe case runs against, and the axis on which the threat
model is classified — and that is what changes.

| Input | Revision 7 | Revision 8 |
|---|---|---|
| **R7-A** — *Algorithm C had no executable order* | package-plan step **C0** refused unless `verify-capability` had already passed all four stages with a matching report, and step **C1** was the step that ran them and built it | **Host-side, package plan §2.13.5a.** **C0** keeps only pre-probe preconditions; **C1** is the single probe invocation and the single creation point of the report; a new **C2** validates pass state, report completeness, deployment-digest equality and cleanup success **before any persistent artifact exists**; the algorithm is renumbered **C0 … C13** and gains a value-dependency table. Its schema trace is §3.7's `append_only_probe_digest` and `seal_body_digest` notes — the report those columns describe is now produced, validated and sealed in a stated order — §3.7.1 and §9, which gain the ordered-construction evidence rows `JNL-46` and `JNL-47`. **No column, constraint or command changes**, and the registration step (**C13**, formerly C12) is unmoved in everything but its number |
| **R7-B** — *S4-2 attributed `EROFS` without a positive control* | the case appended to an unnamed path *"outside `ReadWritePaths=`"* and accepted `EROFS`, without proving the path writable by `freedomsheet` outside the sandbox | **Host-side, package plan §2.13.2a.** The exact target is `…/probe-ro/s4-2.target` in a second transient directory on the same mount; new case **`S4-0`** proves open, append, `fsync`, `rename` and `unlink` are permitted by DAC on it outside any unit; `EACCES` under the sandbox is **`inconclusive`** and a success is a **failed** stage. Stage 4's cases become **`S4-0 … S4-3`**, which this artifact carries in §3.7's `append_only_probe_digest` note, in §3.7.1's sandbox row and in §4.3.8 Band 3. **`append_only_probe_version` still reads `jnl-probe-1`**: what that value denotes gains a control case, which is a change to the procedure the closed vocabulary names, not to the vocabulary |
| **R7-C** — *the attacker classes exceeded their capabilities* | class 1 could not clear `FS_APPEND_FL` yet was said to reach every falsification row but one; **F-2** was assigned class 1 while conceding it needs class 2 | **Host-side, package plan §2.13.5c, rewritten.** The two-class model is withdrawn for an **eight-capability register** (`K1 … K8`) with a per-row minimum capability, detector reach, refusing actor, exact step and code, and residual. Its schema trace is direct and load-bearing: **`K8`'s mutation half is held by no principal in this design**, which is what `reject_history_mutation` and the revoked `UPDATE`/`DELETE`/`TRUNCATE` grants of §4.3 establish — see §3.7's *What this table uniquely can do* and §3.7.1. **F-1b is still refused here and nowhere else**, and revision 8 adds the boundary above it: an attacker holding **both** `K1 + K3` **and** `K8`-mutation writes both copies, which **no check in this design refuses** — package-plan risk **R-5.0-12** |
| **R7-D** | implementation-plan §20 named an obsolete brief | corrected by the reviewer and **preserved**; this artifact, the package plan, the handback and the five registers all name **R7** as the active cycle and revision 8 as the response |
| Falsification-row count | the package plan's WP-8 and §6.5 item 16 described §2.13.5c as *"twelve falsification rows"* while listing thirteen | **Corrected to thirteen** — F-1a, F-1b and F-2 … F-12 — in the package plan; §9 below cites the corrected count |
| Table count, columns, constraints, triggers, evidence columns, commands, vocabularies | six tables, five trigger conditions, three journal evidence columns, five commands, `jnl-probe-1` | **Unchanged, every one.** Revision 8's only schema-adjacent movement is that `jnl-probe-1` now denotes a four-stage procedure **whose fourth stage carries a positive control** and whose report is produced before it is validated and sealed |
| Evidence band | forty-five identifiers, forty-eight cases | **fifty identifiers, seventy-four cases** (§4.3.8 Band 3, package plan §2.13.8) |
| **P5.0-R1**, **P5.0-R4** | unchanged | **Unchanged.** §2.2B and §2.8 stand; §4.3's boundary and evidence plan stand; no operational evidence is claimed passed |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged.** §2.1's matrix, §2.5's effective-time model, no telemetry table and no ledger table |

---

## What changed in revision 7, and why — retained

Revision 6 was returned **changes requested** on 2026-08-30 with P5.0-R5 still
Blocking: two Blocking defects and two Important documentation defects. **None
of the four is a schema-object defect**, and revision 7 adds, removes and alters
**no** column, constraint, index, trigger, sequence, command, table or closed
vocabulary. What was wrong here was what this artifact *said about* artifacts that
live on the host, and that is what changes.

| Input | Revision 6 | Revision 7 |
|---|---|---|
| **R6-A** — *the probe report's lifecycle* | §3.7 said `append_only_probe_digest` covers the probe's **four stages**, while package-plan Algorithm C step **C1** built the report from stages **1–3** and stage 4 ran later, at deployment. A digest was described as covering bytes it did not contain | **Host-side, package plan §2.13.2a.** Stage 4 moves to **provisioning**, inside the same `verify-capability` invocation and **before** the report is built, so the sentence is true by construction. Its schema trace is §3.7's `append_only_probe_digest` note — which now names the four stages **and** their cases `C-1 … C-6`, `P-1 … P-9`, `M-1 … M-2`, `S4-1 … S4-3` — §3.7.1, which gains a row saying the database enforces **nothing whatever** about the sandbox, and §4.3.8 Band 3. **No column is added for the sandbox evidence, deliberately**: it is inside the same report, under the same digest, invalidated by the same rotation rule |
| **R6-B** — *the whole-seal falsification claim* | package plan **F-1** claimed the writer refuses any seal-byte alteration without PostgreSQL; `BND.sealed_at` was authenticated by no **V-W** step | **Host-side, package plan §2.13.5a–c.** The binding section loses `sealed_at` and its own format field and keeps exactly the three values V-W recomputes or compares; its structure is fixed by a `binding_format_version` in the chain-authenticated body; **F-1** splits into **F-1a** (the writer refuses, no database) and **F-1b** (a `CAP_LINUX_IMMUTABLE` holder rewriting seal *and* record 0, which **only the coordinator refuses, against this table**). Its schema trace is §3.7's `seal_digest` and `genesis_record_digest` notes and §9: **`sealed_at` was never a column here**, so nothing in §3.7 changes shape — but the registered row is now, explicitly, the **only** artifact that refuses **F-1b**, and §3.7's *"What this table cannot do"* paragraph is joined by what it uniquely **can** |
| **R6-C** — *`JNL-32` contradicted W9* | §9 cited a syscall trace of a *"full writer start"* that leaves the journal unchanged *"including with `+a` absent"* | **Corrected here.** §9's row and §4.3.8 Band 3 now name **`JNL-32a`** (successful start, `+a` present, exactly one appended `startup` record) and **`JNL-32b`** (`+a` absent, refusal at **W9** with `SW-J06` before W17, no write-mode journal open, nothing appended, evidence byte-for-byte unchanged) |
| **R6-D**, **R6-E** | — | Handback `phase-5-0-remediation-r6-handback.md`; the package plan's cross-reference defects are corrected there and in §2.13.2a/§2.13.5a. Nothing in this artifact depended on them |
| Table count, columns, constraints, triggers, evidence columns, commands, vocabularies | six tables, five trigger conditions, three journal evidence columns, five commands, `jnl-probe-1` | **Unchanged, every one.** Revision 7's only schema-adjacent movement is `append_only_probe_version`'s *meaning*: `jnl-probe-1` now denotes a four-stage procedure whose stages all run before the report is built. **That is a change to the procedure the vocabulary names, not to the vocabulary**, and it is why the value is a closed vocabulary in the first place — a later procedure gets a new value and a visible migration |
| Evidence band | forty-one identifiers | **forty-five identifiers, forty-eight cases** (§4.3.8 Band 3, package plan §2.13.8) |
| **P5.0-R1**, **P5.0-R4** | unchanged | **Unchanged.** §2.2B and §2.8 stand; §4.3's boundary and evidence plan stand; no operational evidence is claimed passed |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged.** §2.1's matrix, §2.5's effective-time model, no telemetry table and no ledger table |

---

## What changed in revision 6, and why — retained

Revision 5 was returned **changes requested** on 2026-08-29 with P5.0-R5 still
Blocking. Three of the four findings are host-side; one is this artifact's.

| Input | Revision 5 | Revision 6 |
|---|---|---|
| **R5-D** — *the database-evidence claim* | `append_only_verified BOOLEAN NOT NULL CHECK (append_only_verified)`, described as making the probe *"enforced by a constraint rather than by a procedure step somebody could skip"* | **The column and its `CHECK` are withdrawn.** `seal_body_digest`, `append_only_probe_version`, `append_only_probe_digest` and `append_only_probe_at` replace them (§3.7), and **new §3.7.1** states what PostgreSQL enforces, what it merely records, who the authenticated actor is, which fields are immutable, and what actually establishes that the probe ran — the seal, `sudo log_output`, journald, `audit_events` and `archive-verify`. **The writer still opens no database connection** |
| **R5-A** — *the circular construction* | the seal carried `genesis_record_digest` while the genesis record hashed `seal_digest` | **Host-side, package plan §2.13.5a.** Its schema trace is in §3.7: the registered row now carries `seal_body_digest` as well, the column notes name the construction order, and `genesis_record_digest` is documented as **derived from the seal body**, so a reader of the table can see why it is registrable |
| **R5-B** — *permissions versus validation duties* | the seal was `root:freedomcoord 0440` and the writer was required to validate it | **Host-side, package plan §2.13.3.** Its schema trace is §4.3.2, which gains the proposed `freedomjournal` group, and §4.3.5, whose authentication matrix is **unchanged** — the writer still holds no database credential and can authenticate as no principal |
| **R5-C** — *the capability probe* | a `root:root 0600` probe file in a directory the writer cannot write, re-run destructively against the live journal at every start | **Host-side, package plan §2.13.2a.** Its schema trace is §4.3.8 Band 3 and §3.7.1: the probe's *result* reaches the database as a digest of a report held in the seal, and the database is not the thing that enforces it |
| Table count, trigger, evidence columns, commands | six tables, five trigger conditions, three journal evidence columns, five commands | **Unchanged.** Revision 6 adds no table, no trigger condition, no evidence column and no command |
| **P5.0-R1**, **P5.0-R4** | unchanged | **Unchanged.** §2.2B and §2.8 stand; §4.3's boundary and evidence plan stand; no operational evidence is claimed passed |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged.** §2.1's matrix, §2.5's effective-time model, no telemetry table and no ledger table |

---

## What changed in revision 5, and why — retained

Revision 4 was returned **changes requested** on 2026-08-29. P5.0-R1 stayed
Blocking and P5.0-R5 was raised.

| Input | Revision 4 | Revision 5 |
|---|---|---|
| **P5.0-R5** — the journal's storage | a `fsync`-ed, `chattr +a` file at `/run/freedom-sheet-writer/dispatch.journal`, described in one table row, with the append-only capability inferred from a different path's filesystem type | **A contract, in package plan §2.13.** Durable ext4 storage under a root-owned `/var/lib/freedom-sheet-writer` hierarchy that the writer may traverse and never write; a probed — not inferred — append-only capability; a `chattr +i` **generation seal**; a hash-chained, sequence-numbered record format; **twenty-one conditions that all refuse**; and a privileged seal/rotate/archive/retain/dispose lifecycle the writer cannot perform |
| **P5.0-R5** — the schema consequence | none. Revision 4 stated that no table was added | **A sixth table, `sheet_writer_journal_generations`** (§3.7); **three journal columns** on the evidence table (§3.5); a **fifth activation-trigger condition** (§3.4); a **fifth command** (§0.3). A trigger cannot refuse stale or cross-generation evidence that the database has never heard of, and refusing exactly that is what the finding requires |
| **P5.0-R5** — the completeness contradiction | *"nothing in the fence depends on the journal being complete"*, while `dispatch_journal_clear` was one of five **required** fence methods | **New §2.9.** The sentence is **withdrawn as false**; the method is **kept**. §2.9 states what completeness is trusted to establish, the single direction in which activation depends on it — it can refuse, never permit — and the residual that is left outside it, **R-5.0-8's new sibling R-5.0-10** |
| **P5.0-R1** | no barrier; a stated weaker guarantee and a priced decision | **Unchanged, and deliberately so.** §2.2B and §2.8 stand. A durable journal makes the *enumeration* trustworthy and says nothing about what Google has applied, which §2.9 and package plan §2.13.10 both state so no reader assembles the opposite |
| **P5.0-R4** | the dedicated `freedomcoord` identity, the peer map, the host boundary and the denial matrix | **Unchanged**, apart from two rows added to §4.3.8 Band 2 for the second `sudoers` drop-in that `freedom-journal-admin` needs. **No operational evidence is claimed passed** |
| Table count | five | **six.** The property revision 4 was protecting is preserved and restated: **the writer still never opens a database connection**, so the Freedom bot's legacy mutation path still takes no PostgreSQL availability dependency. Only the coordinator touches the new table, at provisioning, rotation and observation, all human-run |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged.** §2.1's matrix, §2.5's effective-time model, no telemetry table and no ledger table |

---

## What changed in revision 4, and why — retained

Revision 3 was returned **changes requested** on 2026-08-29. Both open Blocking
findings stayed open.

| Input | Revision 3 | Revision 4 |
|---|---|---|
| **P5.0-R1** — the Sheet half | Termination plus Google-side write-access revocation, presented together as an **enforceable** boundary | **The enforceability claim is withdrawn.** §2.2B now names the invariant that cannot be guaranteed — *every request Google accepted before the fence is reflected before the final import reads* — records that no barrier for it was found in the published API (package plan §2.10.1, thirteen candidates), and replaces the claim with six stated weaker guarantees. The **ordering changes**: drain, then terminate, then revoke. The writer gains an explicit request timeout and a host-local dispatch journal, so the unresolved set is **enumerable** and a non-empty set **refuses the activation**. New §2.8 states the boundary of the claim in one place |
| **P5.0-R4** | A peer-authenticated `freedom_migration_coordinator` role, with no operating-system identity named | **§4.3 is rewritten and roughly trebled.** It names the dedicated `freedomcoord` OS user and group, gives the exact `pg_hba.conf` line ordering and the single `pg_ident.conf` map entry, states the four independent layers a connection must pass, gives ownership and modes for every deployed artifact, answers each attack vector one at a time, and specifies provisioning, audit, revocation, recovery and rotation. The host-boundary evidence plan is new and **needs a disposable OS identity and a `pg_hba` reload** (assumption A-5.0-4, unconfirmed) |
| Consequence | five tables | **still five tables. Revision 4 adds no table**, and the dispatch journal is deliberately a **host file, not a PostgreSQL row**, so the legacy mutation path gains no database dependency — the property revision 3 won by withdrawing the lease is not given back. `fence_method` gains a fifth value, `dispatch_journal_clear` |
| **P5.0-R2**, **OD-55**, **OD-58** | preserved | **Preserved unchanged.** §2.1's matrix, §2.5's effective-time model, no telemetry table and no ledger table |

*(Revision 4's "still five tables, revision 4 adds no table" row is superseded by
revision 5's table above, for the reason stated there.)*

---

## What changed in revision 3, and why — retained

Revision 2 was returned **changes requested** on 2026-08-29. P5.0-R2 is closed
and is preserved unchanged below. P5.0-R1 stayed Blocking and P5.0-R4 was raised.

| Input | Revision 2 | Revision 3 |
|---|---|---|
| **P5.0-R1** — enforceable external-writer quiescence | A PostgreSQL **lease** with request-time admission, a headroom rule and a positive drain acknowledgement. A process paused after admission and resumed after the horizon could still emit one Sheet write, so the invariant rested on probability | **Replaced by a lifecycle boundary.** The fence is now a property of *the store being written*, not of the process's clock. PostgreSQL-authoritative writes are fenced **inside the transaction** by the current activated disposition — a transactional store can be fenced perfectly. The Google Sheet cannot, so its writer is fenced by **termination**, verified at the cgroup level, plus **Google-side write-access revocation** on the spreadsheet. Killing a process fences a `SIGSTOP`ped one; an ACL evaluated by Google fences a request that escaped every local check. §2.2, §2.3, §2.7 |
| **P5.0-R4** — database-enforced proof ownership | `migration_authority_leases` (shared-role `UPDATE` on every row) and `migration_quiesce_acknowledgements` (shared-role `INSERT` for any instance). Own-row ownership was an application convention the grants contradicted | **Both tables are withdrawn.** No runtime process authors any authority proof at all, for any instance including its own. Quiescence evidence is **observed** and recorded by a privileged coordinator principal that no application process can authenticate as. Self-attestation is removed rather than secured, because a compromised process's claim about itself is worthless under any grant model. §2.4, §3.5, §4.3 |
| Consequence | six tables; leases, acknowledgements, seven timing controls, a monotonic-clock model | **five tables**; no lease, no acknowledgement, no headroom rule, no clock injection. N5.0-9 … N5.0-13 and N5.0-15 are **withdrawn**; four new controls replace them (package plan §8.3) |
| **P5.0-R2** — state and effective-time semantics | Closed by the re-review | **Preserved unchanged.** §2.1's matrix, authority transfer at `shadow → cutover`, `database` as accepted completion, authorization separate from activation, authority read only from an activated disposition, and `effective_at` as the earliest permitted activation instant all stand exactly as accepted |
| **OD-55** | Applied | **Preserved.** No comparison-telemetry table, column, write path or schema in this package; the contract stays prose in package plan §11 and package 5.1 owns the implementation |
| **OD-58** | Applied | **Preserved.** No ledger table; R-P4-4 stays open and owned by 5.2 |

The table count falls from six to five and the estimate rises anyway (package
plan §4), because what left the schema moved into a live service's topology.

---

## 0. The questions this artifact must answer first

### 0.1 The durable ledger table is package 5.2's — **closed by OD-58**

Package 5.0 designs no ledger table. Plan §12.0 already allocates the typed
wallet/ledger schema to 5.2; a 5.0 ledger table would have to persist a
free-text `account_name` with no foreign key to `characters`, because 5.0 may
not decide the account vocabulary; 5.0 has no mutation consumer for it; and a
generic book/account table created before any typed aggregate exists is close to
the generic character-state store the handover bans. **R-P4-4 is not closed by
this package** (§0.3).

### 0.2 What package 5.0 persists, and its real 5.0 consumers

Package 5.0 persists **its own control plane**: which authority owns each
migration unit right now, how that authority has changed, what was *observed*
about the external writer before an authority change took effect, and — new in
revision 5 — **which durable dispatch journal that observation was made against**,
and — new in revision 12 — **which reviewed source the program that wrote that
journal was built from, and who approved it.**
**Seven tables**, in §3 — six through revision 11, and
`approved_source_revisions` added in revision 12 (§3.8).

| Consumer | What it is | Why it is real, not speculative |
|---|---|---|
| **The database authority fence** | A `BEFORE` trigger, installed by each owning package's migration on each table it makes database-authoritative, that refuses a write whose unit is not at `cutover` or `database` | Live from day one on package 5.0's own control-plane tables and, from 5.1 onward, on every migrated aggregate. With every unit seeded `legacy` its first job is to make *"no process may write PostgreSQL for any unit"* an enforced property of the database rather than a convention of the code |
| **The startup authority read and capability refusal** | Production code in the bot, web and worker: each reads the authority map at start and refuses to start if any unit's authority names a store it holds no repository for | It is what makes a half-deployed estate fail closed instead of running split |
| **The separately terminable Sheet writer** | `freedom-sheet-writer`, the one process that holds the Google credential and issues `values.batchUpdate`; it is drained, then terminated, and it appends to the **durable, sealed, generation-bound** dispatch journal the coordinator reads | The Freedom bot's entire Sheet **write** surface is one function today (`connectors/sheets.py:31`, called from `models/actor.py:230` and `models/trade.py:66`), so the boundary already exists in the code and this makes it a process boundary. **It never opens a database connection**, which is why the journal is a host file and only its *generation* is a table |
| **`AuthorizeAuthorityChange`, `ActivateAuthorityChange`, `AbandonAuthorityRevision`, `RecordQuiescenceEvidence`, `RegisterJournalGeneration`** | The audited, idempotent, optimistically fenced application commands. **The fifth is new in revision 5** | The only writers of the authority chain, the evidence table and the generation register. The authorization revision is the durable domain effect that proves the transaction boundary (§0.3) |
| **The coordinator command** | `migration-authority preview\|authorize\|observe\|activate\|abandon\|status\|diagnostics\|register-journal-generation`, host-local, on the accepted `tools/web_operator.py` pattern, invoked through `sudo` as the dedicated `freedomcoord` OS identity and connecting as a principal no application process can authenticate as (§4.3) | The only way a human changes authority (OD-59), **the only writer of quiescence evidence** (§2.4) and **the only writer of the generation register** (§3.7) |
| **The deployment step** *(new in revision 12)* | The root-run Algorithm **D** of package plan §2.12.5a, which installs the writer and the coordinator | It is the only writer of the provenance record, and the reason `approved_source_revisions` exists: without a row here, `RegisterJournalGeneration` cannot insert a generation, so **an unreviewed deployment cannot reach activation**. That is security-review finding **P5.0-SR1**'s required fail-closed binding, and it is a foreign key rather than a procedure |
| **The privileged journal tool** | `freedom-journal-admin`, run as `root` under its own `sudoers` drop-in — `verify-capability`, `init-generation`, `seal`, `rotate`, `repair`, `archive-verify`, `dispose` (package plan §2.13.7) | **New in revision 5.** It writes nothing to the database; it produces the on-disk generation the coordinator then registers, and it is the only thing that may seal or dispose of a journal. **The writer cannot invoke it**, which is what makes "the writer cannot erase evidence it authored" a permission fact |
| **`/healthz` and the monitoring surface** | **Four** named checks plus the bounded queries behind them | The numeric thresholds in package plan §8 are read from these tables and from nowhere else. The fourth check reads **only** the generation register, because the web identity has no access to the journal itself (package plan §8.4) |

### 0.3 How the first mutation stays atomic, without the in-memory ledger

`AuthorizeAuthorityChange` commits three things in one PostgreSQL transaction
through one `SqlAlchemyUnitOfWork`:

1. the durable domain effect — one `migration_authority_revisions` row;
2. the idempotency receipt — one `idempotency_keys` row under the 5.0-owned
   scope `migration.authorize_authority`; and
3. the success audit — one `audit_events` row.

`ActivateAuthorityChange`, `AbandonAuthorityRevision`, `RecordQuiescenceEvidence`
and — new in revision 5 — **`RegisterJournalGeneration`** do the same with a
`migration_authority_dispositions`, `migration_quiescence_evidence` or
`sheet_writer_journal_generations` row as their effect, under their own scopes.
Every mandatory evidence item is therefore exercised against a real durable
effect: constraints reject invalid, duplicate and stale writes; the restricted
runtime role cannot write any of these tables **at all**; injected effect, audit
and commit failures leave no partial state and no false success; identical retries
return the original receipt; conflicting key reuse refuses; two concurrent callers
produce one durable effect. None of that is asserted against a fake.

**`RegisterJournalGeneration` is a control-plane write, not a mutation path.** It
runs once per journal generation — at provisioning and at each rotation — from the
human-run coordinator command, after `freedom-journal-admin` has created and
sealed the generation on disk. **No Sheet write, and no Freedom-bot command, ever
causes it to run.**

**What 5.0 does not close is R-P4-4.** The ledger posting is still durable only
as far as process memory, because no ledger table exists. Package 5.0 narrows the
risk in exactly one way and claims nothing further: a unit cannot reach `cutover`
or `database` authority while its owning package has registered no durable
repository, and the database authority fence refuses every database-path mutation
of a `legacy` unit. R-P4-4 remains **Active and owned by package 5.2**.

---

## 1. Conventions inherited, not reinvented

| Convention | Source | Applied here |
|---|---|---|
| UUID primary keys, application-generated at insert, never derived from external data | ADR 0003, OD-35 | all **seven** tables |
| `TIMESTAMPTZ`, UTC, timezone-aware in Python | ADR 0003 | every time column |
| Enumerations as `VARCHAR` + `CHECK`, or a lookup table — never PostgreSQL `ENUM` | ADR 0003 | `authority`, `disposition`, `fence_method`, `fenced_writer`, **`filesystem_type`**, and the `migration_authority_transitions` lookup |
| Foreign keys always declared with explicit `ON DELETE` | ADR 0003 | all; every one is `RESTRICT` (§4) |
| `NOT NULL` by default; a nullable column states its reason | ADR 0003 | **thirteen** nullable columns, each with a reason in §3 — seven in the tables revisions 2–4 designed and six added by revision 5. *(Revisions 2–4 said "five" here; the count had drifted and is corrected rather than carried forward.)* Five of the new six are **biconditionally `CHECK`ed** against another column, so their nullability is exact rather than optional |
| Append-only history enforced by the `reject_history_mutation` trigger from migration 0002, **and** by withheld grants | `migrations/versions/0002_foundry_snapshot_and_identity.py:185`, `runtime-grants.sql.tmpl` | `migration_authority_revisions`, `migration_authority_dispositions`, `migration_quiescence_evidence`, **`sheet_writer_journal_generations`** |
| `REVOKE ALL PRIVILEGES … FROM PUBLIC` before granting, for every new table | finding O-1, `runtime-grants.sql.tmpl` | all six |
| One use case, one transaction, opened by the application service | ADR 0003 | each of the five commands |
| Idempotency is `(scope, key)` unique plus a schema-versioned canonical `request_hash` | `application/idempotency.py` | **five** 5.0 scopes (§3.6) |
| Money in integer copper; divisible quantities in an integer smallest unit | ADR 0005, plan §7.7 | **no quantity column exists in this package** (§5) |
| Downgrade refuses rather than destroying committed effects | migration `0013`, dependency D-09 | §6 |

**No new migration tooling.** Alembic, one additive revision `0014`.

**Revision 2 broke one convention; revisions 3, 4 and 5 do not.** Revision 2
introduced a mutable `migration_authority_leases` table renewed by `UPDATE` under
a shared role — the surface P5.0-R4 found. It is withdrawn. **Every table in this
package is append-only or seed-only**, and no application process holds `INSERT`,
`UPDATE` or `DELETE` on any of them. **Revision 5's sixth table keeps that
property deliberately**: superseding a journal generation is the successor's own
row, never an `UPDATE` of the predecessor, which is why §3.7 reuses the revision
chain's shape rather than adding a `superseded_at` column somebody would have to
write to.

---

## 2. The model, before the tables

### 2.1 The authority-state matrix — P5.0-R2, closed and preserved

**Unchanged from revision 2, which the Independent Reviewer accepted.** It is
restated in full rather than referenced, because the re-review closed it on this
text and a reviewer must be able to confirm nothing drifted.

The four states are the accepted vocabulary; this package adds none. For each
state the matrix states which store is read-authoritative, which may accept
writes, whether comparison reads occur, the condition of the legacy path, the
valid process configuration, and the transitions and prerequisites permitted.

| | `legacy` | `shadow` | `cutover` | `database` |
|---|---|---|---|---|
| **Read-authoritative store** | Google Sheet / Freedom-bot model | Google Sheet / Freedom-bot model | **PostgreSQL** | **PostgreSQL** |
| **May accept writes** | Sheet only | Sheet only | PostgreSQL only | PostgreSQL only |
| **Second store written?** | **no** | **no** | **no** | **no** |
| **Comparison reads** | none | **yes** — the database answer is computed and compared on each read, then discarded | **none** — the legacy store is frozen from the activation instant, so a comparison against it would measure elapsed time, not correctness | none |
| **Legacy path** | active and authoritative | active and authoritative | **quiesced** — not written by any process; retained unchanged as the rollback source | **rollback-only** — retained under plan §15.1 stage 9, never written, increasingly stale |
| **Valid process configuration** | no per-unit authority setting exists in any process; every process reads authority from the activated dispositions. A process is valid for this unit if it can serve the legacy path | as `legacy`, **and** the process must hold a registered database read repository for the unit, or it may not perform the comparison | the process must hold a registered durable database repository for the unit, and the Sheet writer must hold no write access to it | as `cutover` |
| **Permitted transitions out** | `→ shadow` | `→ cutover`, `→ legacy` | `→ database`, `→ legacy` | `→ legacy` (while the legacy path exists) |
| **Operational prerequisites for entering** | seeded genesis | the owning package's import is idempotent, dry-runnable and reconciled; a database read repository exists | N5.0-1 shadow period, N5.0-2 compared operations, N5.0-3 mismatch condition; a durable write repository; a **declared and evidenced rollback data path** (§2.6); a quiesced final import | the N5.0-4 verification window elapsed with no open N5.0-5 trigger; the Operations Owner accepts |

> **Authority transfers at `shadow → cutover`.** `cutover → database` transfers
> nothing: it closes the bounded verification window, retires the *planned*
> rollback, and accepts the unit. `database → legacy` remains legal while the
> legacy path exists, but it is an exceptional supervised recovery rather than a
> planned option.

**No dual writes, at any moment, in any state.** The matrix's *"second store
written?"* row is `no` in all four columns. `shadow` compares a computed database
answer against the authoritative legacy answer and discards it; the database copy
is refreshed only by the owning package's supervised, idempotent import. That is
why the final import happens **inside** the `shadow → cutover` quiesce window,
when nothing can be writing either store (§2.3).

### 2.2 The fence is a property of the store, not of the process — P5.0-R1

This is the correction. Revisions 1 and 2 both looked for **one** mechanism that
would fence every writer, and both therefore reached for the weakest common
denominator: a process-side check, first at startup and then on a clock. The
finding's counterexample — a process paused after its last check and resumed
after activation — defeats every process-side check by construction, because a
process-side check is a statement about the past.

The two stores this platform writes are not alike, and they do not need the same
mechanism.

| | PostgreSQL | Google Sheet |
|---|---|---|
| Transactional | yes | no |
| Can the target refuse a stale write at the moment it arrives? | **yes** — a trigger inside the writing transaction reads the current authority | **no** — Sheets API v4 has no precondition, ETag, revision id or compare-and-swap on `values.update`, `values.batchUpdate` or `spreadsheets.batchUpdate` (§2.7) |
| Therefore the fence is | **inside the write**, and needs no clock, no lease and no process cooperation | **outside the write**: the writer must not exist, and its access must be gone |

So the design splits:

**A. Every PostgreSQL-authoritative write is fenced inside its own transaction.**
An owning package that makes a table database-authoritative installs a `BEFORE
INSERT OR UPDATE OR DELETE` trigger on it that reads the unit's current activated
disposition and refuses unless it is `cutover` or `database`. The check and the
write are the same transaction, so there is no window between them. A process
paused for a week and resumed commits nothing: its transaction re-evaluates the
authority at commit time, in the database, against the row that is current then.
The runtime role has `SELECT` only on dispositions (§4.3), so no application
process can lie to the trigger.

*What this replaces:* the entire admission/headroom/lease apparatus for database
writes. There is nothing to admit, because the store refuses on its own.

**B. The Google Sheet has no fence, and revision 4 says so.**

This is where revision 3 was wrong, and the correction matters more than the
mechanism. Revision 3 offered termination plus revoked access and called the pair
*enforceable*. Neither control says anything about a request **Google has already
accepted**: terminating a client does not undo work a server has taken on, and no
published statement makes revocation cancel an accepted request. The property the
final import actually needs is exactly about that request.

> **I-SHEET-COMPLETE.** Every `spreadsheets.values.batchUpdate` request Google
> accepted before the fence began is durably reflected in the spreadsheet before
> the final import reads it.
>
> **This invariant cannot be guaranteed with the published Google APIs.**
> Package plan §2.10.1 searched thirteen candidate barriers — the response
> itself, an operation id, an idempotency token, a conditional write, Drive
> `files.version`, `revisions.list`, the Activity API, push notifications, a
> marker write, protected ranges, a file copy, Apps Script `flush()`, and waiting
> — and every one either reduces to a quiet period, rests on an unpublished
> implementation property, is documented as unreliable, or does not exist.

What the design does instead, and each part's limit:

1. **The writer is drained before it is killed.** `SIGTERM` puts
   `freedom-sheet-writer` into refuse-new-work mode; it waits up to N5.0-17 for
   outstanding calls to return, and records each outcome. **A received response is
   the only affirmative evidence that exists**, so the design's first job is to
   maximise how many requests have one. `SIGKILL` escalation remains the backstop,
   and it still defeats a `SIGSTOP`ped process — `SIGKILL` is not blockable and is
   delivered to a stopped process — so pausing is not an escape.
2. **The unresolved set is enumerable, and survives a reboot.** The writer
   appends to a **durable, sealed, generation-bound, hash-chained** journal
   **before** each dispatch and again on each response, `fsync`-ing each. After
   termination the coordinator computes *dispatched with no recorded outcome*.
   **This is a completeness aid, not a proof** — §2.9 states exactly what it is
   trusted for and what it is not. **Revision 4's claim that nothing in the design
   depends on the journal being complete is withdrawn as false**, because
   `dispatch_journal_clear` is a required fence method; §2.9 replaces it with the
   one direction in which activation does depend on it. The journal is a **host
   file and not a table**, deliberately: a PostgreSQL write before every Sheet
   write would reintroduce the standing database dependency on the legacy mutation
   path that withdrawing the lease removed. **Its *generation* is a table**
   (§3.7), because that is written once per journal by a human and never on the
   mutation path.
3. **The activation is fail-closed on that set, and on the journal's own
   state.** `dispatch_journal_clear` is a required fence method for a fenced
   transition, and the coordinator records it only when the journal validates
   against its seal, its inode, its chain and its **registered generation**, *and*
   the unresolved set is empty (N5.0-20 fixes the permitted size at zero). A
   non-empty set refuses the cutover and is adjudicated entry by entry. **A
   missing, empty, unsealed, unregistered, superseded, replaced, truncated,
   corrupt or unreadable journal also refuses** — package plan §2.13.6 lists
   twenty-five conditions and **no row of it resolves to "continue"**. Revision 4
   placed this file on volatile `tmpfs`, where a reboot produced an *empty*
   unresolved set and therefore a *permitted* cutover; that is finding P5.0-R5 and
   package plan §2.13.2 is where it is fixed.
4. **Termination is still verified as an empty-set proof**: the unit reports
   `inactive`/`dead`, its `cgroup.procs` is empty, and a host-wide scan finds no
   other process running the writer entry point. The first two are conclusive for
   anything systemd started; the third looks for an out-of-systemd duplicate and
   is point-in-time (R-5.0-5).
5. **Write access is revoked, after the drain rather than before it.** The bot
   authenticates as one service account scoped to `spreadsheets` against one
   `GUILD_SHEET_ID` (`config.py`, `connectors/sheets.py:8`), and its write access
   is a Drive permission on that file. Revoking it refuses **new** requests —
   a duplicate, a restarted writer, a stray call — at Google rather than at us.
   **Revision 4 demotes this from *fence* to *access bound*** and removes
   revision 3's claim that it captures an accepted request. Revoking *before* the
   drain would be worse, not better: it converts *completed and known* into
   *failed and unknown*, and no published statement makes `values.batchUpdate`
   atomic across its `data` entries.
6. **A late apply is contained and detected, not prevented.** After activation the
   unit is PostgreSQL-authoritative and no Sheet-derived write path exists, so
   nothing that happens on the Sheet afterwards can reach the database. Two
   re-reads of the fenced ranges — at import + N5.0-18 and at the end of the
   N5.0-4 window — compare against the imported snapshot and report any
   divergence, and a `→ legacy` replay must not run until that report exists.

Nothing above depends on a clock or on the writer behaving correctly after it has
lost authority. **What it does depend on is an accepted residual**, stated in
§2.8 and returned to the Acceptance Authority as D5.0-9 / OD-62.

**What is deliberately gone.** No lease. No renewal interval. No clock-skew
allowance. No admitted-operation budget. No headroom rule. No monotonic-clock
model. No acknowledgement. No `fence_protocol_version` handshake. Each of those
existed to make a time-bounded approximation of a boundary that is now an event,
and each was a place the design could be wrong.

**The cost, stated at the top rather than in a footnote.** Every available
option costs one of three things, and the package cannot avoid all three:

- a **bounded Freedom-bot mutation outage** at every cutover and every rollback
  (all options; scoped to mutations under the isolated writer, whole-bot without
  it);
- a **topology change** — a fourth systemd unit holding the Google credential
  (the isolated writer); or
- a **production Google access change** — a Drive permission edited at cutover
  and restored after (the ACL fence).

`.agents/AGENTS.md` forbids degrading the Freedom bot and forbids production
credential changes without approval. All three costs touch those rules — and
revision 4 adds a fourth cost that is not a cost of a mechanism at all: **an
accepted, unprovable residual on the legacy store.** The choice is raised as
decision **D5.0-9 / OD-62, reframed a third time** in package plan §5.3 rather
than taken by the implementer; **D5.0-11 / OD-64** covers the database principal
and its operating-system identity; and **D5.0-12 / OD-65** covers the host
changes the boundary needs outside the coordinator itself.

### 2.3 The quiesced apply protocol

An authority change is **three** operations — authorize, observe, activate — and
the fence lives between the first and the last.

```text
  ┌── AUTHORIZE ─────────────────────────────────────────────────────────┐
  │ coordinator previews against disposition D (the current authority)   │
  │ AuthorizeAuthorityChange writes ONE revision row:                    │
  │   previous_disposition_id = D          ← UNIQUE: one pending at once │
  │   from_authority           = D.resulting_authority                   │
  │   proposed_authority       = the target                              │
  │   epoch                    = D.epoch + 1                             │
  │   effective_at             ≥ created_at   ← earliest legal activation│
  │   activation_deadline_at   = effective_at + N5.0-14                  │
  │ + idempotency receipt + audit row, one transaction                   │
  │ NOTHING HAS CHANGED YET. The current authority is still D.           │
  └──────────────────────────────────────────────────────────────────────┘
                                   │
  ┌── FENCE (operator actions; nothing is self-attested) ────────────────┐
  │ only for transitions the reference table marks                       │
  │ requires_external_writer_fence:                                      │
  │   1. systemctl stop freedom-sheet-writer  — SIGTERM drains first,    │
  │        up to N5.0-17, then SIGKILL escalates    ← ORDER CHANGED, R3  │
  │   2. revoke the service account's write permission on the Sheet,     │
  │        and read the effective role back                              │
  │        → evidence 'external_write_access_revoked'                    │
  │   3. observe unit inactive/dead   → evidence 'unit_inactive'         │
  │   4. observe cgroup.procs empty   → evidence 'cgroup_empty'          │
  │   5. host-wide scan finds no writer entry point                      │
  │                                   → evidence 'host_scan_clear'       │
  │   6. validate the dispatch journal against its SEAL, its inode, its  │
  │        hash chain and its REGISTERED GENERATION; the unresolved set  │
  │        must be EMPTY       → evidence 'dispatch_journal_clear',      │
  │        carrying the generation id, last sequence and head digest     │
  │        a non-empty set, OR any of the 21 conditions in plan §2.13.6, │
  │        records nothing and refuses (N5.0-20)          ← REWRITTEN R4 │
  │   7. wait N5.0-18, the post-revocation margin.                       │
  │        THIS IS RISK REDUCTION, NOT A BARRIER — no wait proves that   │
  │        a request Google already accepted has been applied (§2.2B)    │
  │ each observation is INSERTed by the COORDINATOR principal, which no  │
  │ application process can authenticate as — proved by a dedicated OS   │
  │ identity and an exact peer map, §4.3. Nothing the fenced writer      │
  │ says is recorded, because nothing it says is worth anything.         │
  │ PostgreSQL-authoritative writes need no step here at all: their      │
  │ fence is inside their own transaction.                               │
  └──────────────────────────────────────────────────────────────────────┘
                                   │
  ┌── (owning package's work, inside the window) ────────────────────────┐
  │ shadow → cutover : the final idempotent import + control totals      │
  │ cutover → legacy : the supervised replay/export back to the Sheet    │
  │ both run while NEITHER store can be written by any service           │
  └──────────────────────────────────────────────────────────────────────┘
                                   │
  ┌── ACTIVATE ──────────────────────────────────────────────────────────┐
  │ ActivateAuthorityChange writes ONE disposition row, 'activated',     │
  │ + receipt + audit, one transaction. A BEFORE INSERT trigger refuses  │
  │ unless ALL of:                                                       │
  │   now() ≥ revision.effective_at                                      │
  │   now() ≤ revision.activation_deadline_at                            │
  │   if the transition requires an external-writer fence: one           │
  │     coordinator-recorded evidence row of EVERY required method,      │
  │     each observed after revision.created_at and no more than         │
  │     N5.0-16 before now()                                             │
  │   and the dispatch_journal_clear row names the CURRENT registered    │
  │     generation, with no later generation registered since it was     │
  │     observed                                          ← NEW IN R4    │
  │ THE AUTHORITY CHANGES HERE, and nowhere else.                        │
  └──────────────────────────────────────────────────────────────────────┘
                                   │
  ┌── RESTART, then DETECT ──────────────────────────────────────────────┐
  │ start freedom-sheet-writer on a build that reads the new authority   │
  │ and holds no legacy write path for the moved unit; restore the       │
  │ Drive permission only when no unit it guards is at cutover/database; │
  │ then RE-READ the fenced ranges and compare against the imported      │
  │ snapshot — once now, once at the end of the N5.0-4 window. A         │
  │ difference is a late apply or a human edit. It is DETECTED here      │
  │ because it could not be PREVENTED earlier (§2.2B, §2.8)              │
  └──────────────────────────────────────────────────────────────────────┘
```

**A revision that is never activated is abandoned**, not deleted: an `abandoned`
disposition records the unchanged authority and frees the chain, so a mistaken
authorization costs one appended row and no outage.

**Rollback uses exactly the same protocol.** `cutover → legacy` and
`database → legacy` are ordinary transitions: authorize, fence, replay, activate,
restart. There is no second mechanism and no emergency path that skips the fence.
N5.0-6's sixty minutes is the deadline to *decide* a rollback; the replay's
duration is the owning package's number and is the length of the writer outage.

### 2.4 Quiescence evidence is observed, never attested — P5.0-R4

The finding is that *"each process, its own row only"* was an application
convention the grants contradicted. Revision 3 does not secure that convention.
It removes the thing the convention was protecting.

**No application process writes any authority proof, for any instance, including
itself.** The runtime role holds no `INSERT`, `UPDATE` or `DELETE` on any of the
seven tables (§4.3). There is nothing for a compromised bot, web or worker process
to forge, because there is no row it is permitted to write.

The reason is stronger than a grant argument. Row-level security binding a write
to `current_user` would stop `freedom_web` forging `freedom_bot`'s drain proof.
It would not stop `freedom_bot` forging its **own** — and a process that has been
compromised, or is simply defective, is exactly the process whose claim about
itself is worthless. Self-attested quiescence is unsound at any privilege level,
so it is withdrawn rather than protected.

What replaces it is evidence about the writer, gathered by something else:

| Evidence | What is observed | Who observes it | Can the fenced writer influence it? |
|---|---|---|---|
| `external_write_access_revoked` | Google's own response to the Drive permission change, and the resulting effective role on the file | the coordinator, through the Drive API | **No.** It is Google's answer about Google's ACL |
| `unit_inactive` | `systemctl show freedom-sheet-writer -p ActiveState,SubState` | the coordinator, through systemd | **No.** systemd is the writer's supervisor, not its peer |
| `cgroup_empty` | the unit's `cgroup.procs` is empty | the coordinator, on the host | **No.** A process cannot remove itself from its own cgroup while it exists |
| `host_scan_clear` | no process anywhere on the host runs the writer entry point | the coordinator, on the host | **No**, though it is a point-in-time observation — see the residual below |
| **`dispatch_journal_clear`** | the writer's journal **validates** — seal, inode, hash chain, sequence, registered generation — **and** holds no entry that was dispatched without a recorded outcome | the coordinator, reading a **durable** file in a root-owned directory the writer may read and traverse and **never write**, protected additionally by `chattr +a`, against a `chattr +i` seal whose genesis digest the reader **derives** rather than trusts, and a registered generation (package plan §2.13, §2.13.5a) | **Partly, and this one is different from the other four and must not be read as equal to them.** The writer authors the *records*, so a writer whose dispatch path has been replaced can omit one — **R-5.0-10**. It is not evidence *about* the writer gathered by something else; it is the writer's own record, made durable before the act it records, on storage it cannot erase, in a format it cannot silently rewrite. It is **flagged here rather than in a footnote** because P5.0-R4's whole point is that a fenced process's word is worth nothing. **It can only refuse a cutover, never permit one the other four would refuse** — but it *is* required, so an absent, invalid or unknown journal refuses too. §2.9 states that dependency exactly; **revision 4's *"nothing else in the fence depends on it"* is withdrawn as false** |

The **coordinator** is a distinct SQL principal, `freedom_migration_coordinator`,
authenticated by peer over the Unix-domain socket by the host account that runs
the operator command, exactly as the accepted `tools/web_operator.py` pattern
authenticates today. It is the only principal with `INSERT` on
`migration_authority_revisions`, `migration_authority_dispositions` and
`migration_quiescence_evidence`. No service unit's environment file contains its
credential, and it cannot log in over TCP. **Introducing it is a database-role
and credential-topology change**, so it is raised as decision **D5.0-11 / OD-64**
with an impact assessment, and it requires the named Security Reviewer.

**Residual, stated and not mitigated away.** The trigger can prove that evidence
of every required kind was recorded, recently, after the revision was authorized.
It cannot prove the writer is *still* absent at the instant of the `INSERT`. Three
controls bound that window and none of them pretends to close it by itself: the
coordinator re-observes immediately before activating, in the same command
invocation; the trigger refuses evidence older than N5.0-16; and the Drive
permission is still revoked, so a writer restarted inside the window is refused
by Google even though the host observation has gone stale. It is risk
**R-5.0-5** in package plan §7.4.

**A second residual, new in revision 4 and larger.** Four of the five evidence
kinds establish that *no writer exists and none may write*. **None of them
establishes that no request Google already accepted is still outstanding**, and
§2.2B records that nothing in the published API does. That is **R-5.0-8**, it is
owned by the Acceptance Authority rather than by the Technical Lead, and §2.8
states its exact boundary.

**A third residual, new in revision 5 and narrower.** The fifth evidence kind is
the one the writer authors, and §2.9 states the limit of what that can be trusted
for: **a writer whose dispatch path has itself been replaced can call Google
without journalling at all.** No record it authors bounds that. It is
**R-5.0-10**, it is not mitigated away, and what bounds it instead is the four
kinds the writer does *not* author — the process is terminated, its cgroup is
empty, a host scan found nothing, and Google refuses its access.

### 2.5 Effective time — how a pending revision stays pending

**Unchanged from revision 2, which the Independent Reviewer accepted.**

**Authority is never read from the revision table.** A revision is an
*authorization*; a disposition is its *outcome*; only dispositions carry
authority:

```sql
-- The one query. There is no other way to obtain a unit's authority.
SELECT d.resulting_authority, d.epoch, d.control_plane_version
  FROM migration_authority_dispositions d
 WHERE d.unit_id = :unit_id
 ORDER BY d.epoch DESC
 LIMIT 1;
```

and for the whole estate at startup, one bounded statement over ~40 units:

```sql
SELECT DISTINCT ON (d.unit_id) d.unit_id, d.resulting_authority, d.epoch
  FROM migration_authority_dispositions d
 ORDER BY d.unit_id, d.epoch DESC;
```

`effective_at` is **the earliest instant at which this revision may be
activated**, enforced by the activation trigger. Nothing becomes true by the
passage of time. A cutover may still be authorized in advance for a quiet hour;
it takes effect when an operator activates it inside that window, not while
everybody is asleep.

Three properties follow:

- **a future revision cannot become current early**, because becoming current
  requires an `INSERT` that only the coordinator command performs and that the
  trigger refuses before `effective_at`;
- **there are never two current heads**, because `(unit_id, epoch)` is UNIQUE on
  dispositions and the read is `ORDER BY epoch DESC LIMIT 1` over a totally
  ordered column, not an anti-join over a graph; and
- **a revision that is never activated expires** at `activation_deadline_at` and
  can then only receive an `abandoned` disposition.

The database authority fence in §2.2A reads exactly this query, inside the
writing transaction. That is the whole of the PostgreSQL-side fence.

### 2.6 The rollback data path — a precondition, not an afterthought

**Unchanged from revision 2.** Because no state dual-writes, the legacy store is
frozen at the instant a unit enters `cutover` and diverges from PostgreSQL for as
long as the unit stays there. A rollback therefore has to *move data*:

> **A unit may not enter `cutover` unless its owning package has declared, and
> evidenced against the disposable database, a rollback data path that restores
> the legacy store from the frozen snapshot plus the PostgreSQL changes made
> since activation, within the window the Operations Owner accepts.**

Package 5.0 states the requirement and tests it against its own synthetic unit.
It does not implement any unit's replay: each migrating package owns its own,
under its own gate. N5.0-4's fourteen days is the bound on how much divergence a
rollback ever has to replay.

The replay itself writes the Sheet, so it runs **while the Sheet writer is
terminated and its access is restored only for the replay's own credential** —
the coordinator's, not the bot's. That is stated here because it is the one place
in the design where a Sheet write is intended during a fence, and a reviewer
should see it named rather than discover it.

### 2.7 The options P5.0-R1 requires, compared

The full comparison is **package plan §2.10** — the thirteen-candidate barrier
search (§2.10.1), the conclusion (§2.10.2), the six achievable guarantees
(§2.10.3), the seven cases the handoff enumerates (§2.10.4), the four priced
options (§2.10.5) and the retained revision-3 host-side comparison (§2.10.6). The
schema-relevant conclusions are:

- **Sheets API v4 offers no conditional-write mechanism.** `values.update`,
  `values.batchUpdate` and `spreadsheets.batchUpdate` accept no ETag, `If-Match`,
  revision id or expected-value precondition; Drive v3 exposes revision *history*
  but no write precondition for Sheets content. The only Google-side enforcement
  point that exists is **authorization**, which is why the ACL fence is the
  option and a "Google conditional write" is not. This is stated as *no such
  mechanism was found in the published API surface*; if the reviewer knows of
  one, it should be evidenced rather than assumed on either side.
- **Credential rotation is rejected as the mechanism.** Disabling or rotating the
  service-account key removes reads as well as writes, so it is a whole-bot
  outage; and an already-minted OAuth access token remains valid for its
  remaining lifetime, so key rotation is not a prompt fence at all. The Drive
  permission, evaluated per request, is.
- **No completion barrier exists in the published surface.** Beyond the absent
  conditional write, there is no operation identifier, idempotency token,
  read-your-writes guarantee, ordering guarantee, flush or drain method by which
  a client can establish that a request Google accepted has been applied. Drive
  `files.version`, `revisions.list`, the Activity API and push notifications
  describe applied state or are documented as best-effort, so each can only ever
  support a quiet-period argument. **This is the schema-relevant conclusion**,
  because it is why `dispatch_journal_clear` exists and why it is described as an
  enumeration rather than a proof.
- **The recommended sequence is: isolate the writer, drain it, terminate it,
  revoke its write access, observe all five, check the journal, wait the margin,
  import, activate, restart, restore, then re-read twice.** The declared fallback,
  if the isolated writer unit is judged too invasive for the live bot, is to stop
  the whole `freedom-bot` unit instead — same properties, larger outage.

### 2.8 The boundary of what this artifact claims

Stated once, in one place, so that no later reader has to assemble it from six
sections and no future revision can quietly widen it.

| | Statement |
|---|---|
| **Guaranteed, by PostgreSQL** | No process may write a PostgreSQL-authoritative table for a unit whose current activated disposition is not `cutover` or `database`. The check and the write are one transaction, so no pause, delay, stale snapshot or restart defeats it. **This is unconditional** |
| **Guaranteed, by the database** | Authority is read only from an activated disposition; a pending revision is authority for nothing; there are never two current heads; an authority change commits with its receipt and its audit row or not at all; no application principal may write any authority row |
| **Guaranteed, by the host** | At activation, no process systemd started is running the writer, its cgroup is empty, and a host scan at that instant found no other. Each is an observation by a supervisor, recorded by a principal the fenced process cannot authenticate as |
| **Guaranteed, by the filesystem and the kernel** | **New in revision 5; corrected in revision 6.** The writer cannot unlink, rename, replace or truncate its own journal, cannot **alter** its seal, cannot reach the archive at all, and cannot clear the append-only attribute — because the containing directory is root-owned and not writable by it, the file carries `chattr +a`, the seal carries `chattr +i` at mode `0440`, the archive excludes it, and its unit's capability bounding set is empty. **It *can* read the seal, deliberately**: revision 5 denied that read while requiring the writer to validate the seal at start, which was remediation R5-B (package plan §2.13.3). Package plan §2.13.4 gives the expected `errno` for each attempt |
| **Guaranteed, by Google** | After the revocation has taken effect, a **new** write from the service account is refused |
| **Bounded and enumerated, not guaranteed** | The set of requests the writer dispatched without recording an outcome. It is empty in the normal case, it **survives a reboot**, it refuses the activation when it is not empty **or when the journal's state is unknown**, and it is complete only if the writer executed its own dispatch path. §2.9 states that condition exactly |
| **NOT guaranteed, and stated rather than implied** | **New in revision 5.** That the journal is complete against a writer whose *dispatch path* was replaced. **R-5.0-10** |
| **NOT guaranteed, and no design in this package makes it so** | **I-SHEET-COMPLETE.** A `values.batchUpdate` request Google accepted before the fence, whose response never reached the writer, and which Google applies after the final import has read the Sheet, is **not prevented and cannot be proved absent** |
| **Consequence of the last row, contained** | Such a write cannot reach PostgreSQL — after activation the unit is database-authoritative and no Sheet-derived write path exists — so its effect is a divergence between the frozen legacy store and the imported snapshot |
| **Consequence of the last row, detected** | Both post-import re-reads compare the fenced ranges against the imported snapshot, and any `→ legacy` replay is blocked until that comparison has been produced and read |
| **Whose decision the residual is** | The **Acceptance Authority's**, through D5.0-9 / OD-62. It is not the Technical Lead's, because it is not a thing implementation can close |

### 2.9 What journal completeness is trusted to establish — new in revision 5

P5.0-R5's second half is that revision 4 said *"nothing in the fence depends on
the journal being complete"* while making `dispatch_journal_clear` one of five
**required** fence methods. Those two statements cannot both be true.

> **Withdrawn.** *"Nothing in the fence depends on the journal being complete"*
> — §2.4 and package plan §2.10.3 W-2, revision 4. **It is false, and it is
> withdrawn rather than defended.**

**The method is kept and the sentence goes**, not the other way round. Package
plan §2.13.9 gives the full argument and §2.13.11 prices the alternative as
**D5.0-13 / OD-66 option C**; what belongs in the schema is this:

| | Statement |
|---|---|
| **What completeness is trusted to establish** | *For a writer that executed its own dispatch path, the set of requests dispatched without a recorded outcome is the set the coordinator enumerates.* It is trusted against crash, `SIGKILL`, power loss, reboot, unclean shutdown, disk-full, `fsync` failure, partial writes and defects elsewhere in the writer — because each of those is a condition that **refuses** rather than under-reports |
| **The one direction activation depends on it** | The journal **can refuse** an activation the other four methods would permit — a non-empty unresolved set, or any unknown journal state. It **can never permit** one they would refuse, because all five methods are required and a clear journal is necessary and not sufficient |
| **Therefore what an incomplete journal costs** | **a refusal that should have occurred does not occur.** It never manufactures a permission. That is the direction in which the design is weakened |
| **What bounds that weakening** | durable storage, a directory the writer cannot write, an append-only file, an immutable seal, a hash chain, a monotonic sequence, a registered generation, and every unknown state treated as a refusal — package plan §2.13 |
| **What remains outside it** | **a writer whose dispatch path was itself replaced can dispatch without journalling.** No record it authors bounds that. **R-5.0-10** |
| **What bounds *that*** | not the journal, and the design does not pretend otherwise. The writer is dead, its cgroup is empty, a host scan found nothing, and Google refuses its access — the four evidence kinds it does not author. A writer compromised deeply enough to bypass its own journal could have written the Sheet arbitrarily long before the fence, which is a condition no fence was ever going to repair |
| **What none of it establishes** | **I-SHEET-COMPLETE.** §2.8's sixth row is unchanged. A durable, sealed, chained, registered journal is a better record of what *this client* did; it observes nothing whatever about what *Google* has applied |

**Why this is in the schema artifact at all.** The activation trigger's fifth
condition (§3.4) and the evidence table's three journal columns (§3.5) exist
*because* of the dependency stated above. A reviewer reading those columns should
find the reason for them here, and should find the limit stated in the same place
as the mechanism.

---

## 3. Table designs

### 3.0 Entity-relationship diagram

```text
   migration_authority_transitions
   (from_authority, to_authority)          reference vocabulary, seeded by the
    requires_external_writer_fence         migration, SELECT-only at runtime
              ▲
              │ FK (from_authority, proposed_authority)
              │      … an illegal transition is refused by the database
              │
 migration_units                  migration_authority_revisions        (append-only)
 ────────────────                 ──────────────────────────────
 id             UUID PK           id                       UUID PK
 unit_key       UNIQUE  ◄──1:N──  unit_id                  FK RESTRICT
 owning_package CHECK             epoch                    BIGINT   ─┐
 manifest_source    (nullable)    previous_disposition_id  FK, UNIQUE ├─ the fence
 description                      previous_epoch           (nullable)─┘
 registered_at                    from_authority           (nullable) CHECK
        │                         proposed_authority       CHECK
        │                         effective_at             ≥ created_at
        │                         activation_deadline_at   > effective_at
        │                         verification_until       (nullable)
        │                         reason · gate_reference
        │                         authorized_by_platform_account_id  FK ──► platform_accounts
        │                         correlation_id · created_at
        │                            │ 1:0..1              │ 1:N
        │                            ▼                     ▼
        │              migration_authority_dispositions   migration_quiescence_evidence
        │              ────────────────────────────────   ─────────────────────────────
        └──1:N──────── unit_id            FK RESTRICT      id            UUID PK
                       revision_id        FK, UNIQUE       revision_id   FK RESTRICT
                       epoch              UNIQUE(unit,ep)  fenced_writer CHECK
                       disposition        CHECK            fence_method  CHECK
                       resulting_authority  proved in-row  observation   CHECK ('clear')
                       control_plane_version BIGINT UNIQUE observed_detail VARCHAR
                       decided_at · correlation_id         observed_at
                       decided_by_platform_account_id      observed_by_platform_account_id
                               ▲                           correlation_id
                               │                           journal_generation_id  FK ─┐
                               │  ← the ONLY source of     journal_last_sequence     │
                               │    "current authority"    journal_head_digest       │
                               │                                  ▲                  │
                               │                                  │  ← the ONLY      │
                               │                                  │    input to the  │
                               └──────────────────────────────────┘    activation    │
                                                                       trigger's     │
                                                                       fence test    │
                                                                                     │
   sheet_writer_journal_generations                    (append-only)  ◄──────────────┘
   ────────────────────────────────                     NEW IN REVISION 5
   id                        UUID PK
   generation_seq            BIGINT UNIQUE   ─┐
   predecessor_generation_id FK self, UNIQUE  ├─ one linear chain, one head
   predecessor_seq           (nullable)      ─┘   … the same shape as the
   predecessor_close_digest  (nullable)           revision chain above
   fenced_writer             CHECK
   journal_path · journal_device · journal_inode   UNIQUE(device, inode)
   seal_body_digest ──► the genesis record's prev_hash anchor   (rev 6)
   genesis_record_digest ──► DERIVED from the seal body, not trusted
   seal_digest ──► a LEAF: no on-disk artifact contains it
   host_machine_id · writer_unit · writer_deployment_digest
   filesystem_type           CHECK IN ('ext4')  ← a tmpfs journal cannot
                                                  even be registered
   append_only_probe_version CHECK IN ('jnl-probe-1')          (rev 6)
   append_only_probe_digest  ──► digest of the probe report    (rev 6)
   append_only_probe_at      CHECK (<= created_at)             (rev 6)
     … the report itself lives inside the +i seal. These columns
       RECORD an attestation; they do not PROVE a probe ran (§3.7.1).
       Revision 5's append_only_verified CHECK(TRUE) is WITHDRAWN.
       rev 7: the report covers ALL FOUR probe stages, because all
       four now run before it is built. No column is added for the
       sandbox stage, and none changes shape.
     … rev 7: these three digest columns are the ONLY artifact that
       refuses a CAP_LINUX_IMMUTABLE rewrite of the seal AND record 0
       (package plan F-1b). The writer refuses every other case
       from disk alone, with no database.
   source_commit · source_tree_id · source_manifest_digest    (rev 12)
   approved_source_revision_id  FK RESTRICT, NOT NULL ────────►┐  (rev 12)
     … the fail-closed half of P5.0-SR1: a generation whose      │
       reviewed source was never approved CANNOT BE INSERTED,    │
       and the activation trigger requires a registered          │
       generation, so activation is unreachable without it.      │
   created_at · correlation_id                                   │
   registered_by_platform_account_id  FK ──► platform_accounts   │
                                                                 │
   approved_source_revisions                    (append-only)  ◄─┘
   ─────────────────────────                     NEW IN REVISION 12
   id                     UUID PK
   component              CHECK IN ('sheet_writer','coordinator')
   source_commit          CHAR(40)  ─┐ UNIQUE (component, source_commit)
   source_tree_id         CHAR(40)   ├─ the immutable Git objects a
   source_manifest_digest CHAR(64)  ─┘  review approved; the SHA-256
                                        is what a SHA-1 collision does
                                        not preserve (plan §2.12.5a)
   review_reference       VARCHAR(200)   ← the governance fact; this
                                           table does not verify it
   approved_at · created_at · correlation_id
   approved_by_platform_account_id  FK ──► platform_accounts
     … UNIQUE (id, source_commit, source_tree_id, source_manifest_digest)
       is the target of the generation table's composite FK, so the
       registered copies cannot disagree with the approved row.
     … There is NO withdrawal column. Superseding an approved revision
       means approving another; a generation binds to exactly one.

  Every one of these seven tables:  runtime role has SELECT or nothing.
  INSERT belongs to freedom_migration_coordinator alone (§4.3).
  No table in this package is writable by freedom-bot, freedom-web,
  freedom-worker or freedom-sheet-writer, under any grant.
  freedom-sheet-writer holds NO database connection at all.

 Reused unchanged, with no schema change of any kind:
     idempotency_keys   ── one row per accepted command, five 5.0 scopes;
                           admission_id stays NULL, which the existing
                           submission_names_its_admission check permits
     audit_events       ── one row per accepted command, append-only
     platform_accounts  ── the authorizing / activating / observing /
                           registering Platform Administrator
```

### 3.1 `migration_units` — the controlled unit vocabulary

**Unchanged from revision 2.** Ownership: package 5.0 owns the table. **The
vocabulary it holds is owned by the Data Owner** and its source of truth is
`docs/project-management/data-migration-manifest.json`; the migration seeds the
rows and a test asserts the two agree. The application cannot register a unit —
the runtime role has `SELECT` only. No code path can invent a migration unit and
then claim authority over it.

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | `UUID` | no | PK, application-generated |
| `unit_key` | `VARCHAR(120)` | no | **UNIQUE.** A stable token: a manifest `profile_target` (`wallet.balance_copper`) or a registered behavior unit (`lifestyle.living_cost_accrual`). `CHECK` not blank, printable |
| `owning_package` | `VARCHAR(16)` | no | `CHECK` against the closed list `5.1, 5.2, 5.3, 5.4, 5.5, 5.6a, 5.6b, 5.7, 5.8, 5.9, 5.10, Phase 8` |
| `manifest_source` | `VARCHAR(60)` | **yes** | **Reason for nullability:** a field unit names its Sheet source (`Characters P-S`); a *behavior* unit — the Living Cost accrual job — has no single column and must not be given a fabricated one |
| `description` | `VARCHAR(200)` | no | `CHECK` not blank |
| `registered_at` | `TIMESTAMPTZ` | no | `DEFAULT now()` |

**Immutable in practice, mutable by migration.** Adding a later package's units
is a migration, reviewed like any other. Rows are never deleted: every foreign
key into this table is `RESTRICT`.

**A unit is not a field profile.** It deliberately does not duplicate the
register's typed target, transformation rule or reconciliation rule.

### 3.2 `migration_authority_transitions` — the legal-transition vocabulary

Seeded by the migration, `SELECT` only at runtime. The transition rule is data,
so an illegal transition is refused by a foreign key rather than by a predicate
somebody has to remember to write.

**One column is new in revision 3:** `requires_external_writer_fence BOOLEAN NOT
NULL`. Which transitions need the Sheet writer terminated is a property of the
transition, not a judgement the coordinator command makes at runtime, and the
activation trigger reads it. Putting it in the reference table means adding a
transition later cannot silently omit its fence.

| from | to | fence? | Meaning under the §2.1 matrix |
|---|---|---|---|
| `legacy` | `shadow` | **no** | begin comparison reads; the legacy store stays read- and write-authoritative, so no writer changes and nothing must stop |
| `shadow` | `legacy` | **no** | abandon the comparison; nothing was ever authoritative but legacy |
| `shadow` | `cutover` | **yes** | **authority transfers.** The Sheet writer must be gone and its write access revoked before the final import runs and before activation |
| `cutover` | `database` | **no** | the verification window closed with no open trigger; PostgreSQL is already the only writer, so no external writer changes state |
| `cutover` | `legacy` | **yes** | rollback inside the verification window: the writer must be absent while PostgreSQL's changes are replayed to the Sheet |
| `database` | `legacy` | **yes** | exceptional supervised recovery over a longer divergence. Legal only while the legacy path exists |

Four absences are deliberate. `legacy → cutover` and `legacy → database` do not
exist, so no unit reaches database authority without a shadow period.
`shadow → database` does not exist, so no unit skips its verification window.
`database → shadow` and `cutover → shadow` do not exist, because re-entering
comparison after PostgreSQL has been authoritative would compare a live store
against a frozen one and call the difference a defect.

**`database → legacy` has an end date.** Once plan §15.1's final Sheet retirement
gate closes there is no legacy path to roll back to, and the row must be removed
by a migration at that point. Until then it is what makes A-04 true.

### 3.3 `migration_authority_revisions` — the append-only authorization chain

Ownership: package 5.0. Writer: `AuthorizeAuthorityChange`, running as
`freedom_migration_coordinator` in the host-local operator command's process, and
nothing else. **The runtime role has `SELECT` only** (§4.3).

**Changed from revision 2:** `lease_horizon_at` is **removed**. There are no
leases, so there is no horizon.

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | `UUID` | no | PK |
| `unit_id` | `UUID` | no | FK → `migration_units(id)` `ON DELETE RESTRICT` |
| `epoch` | `BIGINT` | no | `CHECK (epoch >= 0)`. UNIQUE `(unit_id, epoch)`. Genesis is 0 |
| `previous_disposition_id` | `UUID` | **yes** | **UNIQUE.** FK → `migration_authority_dispositions(id)` `RESTRICT`. **Reason for nullability:** the genesis revision of a unit has no predecessor. Exactly one genesis per unit is a partial unique index. This column **is** the optimistic fence: one pending or decided successor per disposition, ever |
| `previous_epoch` | `BIGINT` | **yes** | **Reason for nullability:** genesis has none. The composite FK `(previous_disposition_id, previous_epoch) → dispositions(id, epoch)` plus `CHECK (epoch = previous_epoch + 1)` makes the chain's arithmetic provable rather than asserted |
| `from_authority` | `VARCHAR(10)` | **yes** | **Reason for nullability:** genesis has no predecessor authority. Composite FK `(previous_disposition_id, from_authority) → dispositions(id, resulting_authority)` makes it provably equal to the authority actually in force when this was authorized |
| `proposed_authority` | `VARCHAR(10)` | no | `CHECK IN ('legacy','shadow','cutover','database')` |
| `effective_at` | `TIMESTAMPTZ` | no | `CHECK (effective_at >= created_at)`. **The earliest instant this revision may be activated** (§2.5) |
| `activation_deadline_at` | `TIMESTAMPTZ` | no | `CHECK (activation_deadline_at > effective_at)`. After it, only an `abandoned` disposition is possible |
| `verification_until` | `TIMESTAMPTZ` | **yes** | The end of the bounded verification window. **Reason for nullability:** only a revision proposing `cutover` has one. `CHECK ((proposed_authority = 'cutover') = (verification_until IS NOT NULL))` and `CHECK (verification_until IS NULL OR verification_until > effective_at)` |
| `reason` | `VARCHAR(200)` | no | `CHECK` not blank. Recorded verbatim in append-only history |
| `gate_reference` | `VARCHAR(120)` | no | `CHECK` not blank. The change-log or gate record that authorized this change (`C-P5.x-n`). The application cannot verify the reference is genuine; what it guarantees is that no authority change exists without one |
| `authorized_by_platform_account_id` | `UUID` | no | FK → `platform_accounts(id)` `RESTRICT`. The Platform Administrator resolved **at execution**, never taken from the request |
| `correlation_id` | `UUID` | no | One identity for the attempt; the same value reaches the receipt and the audit row (P4-R5's rule) |
| `created_at` | `TIMESTAMPTZ` | no | `DEFAULT now()` |

**Constraints, in full.**

| Name | Kind | What it makes impossible |
|---|---|---|
| `pk_migration_authority_revisions` | PK `(id)` | — |
| `uq_…_unit_epoch` | UNIQUE `(unit_id, epoch)` | two authorizations at one chain position |
| `uq_…_id_unit` | UNIQUE `(id, unit_id)` | target of the disposition's composite unit FK |
| `uq_…_id_epoch` | UNIQUE `(id, epoch)` | target of the disposition's composite epoch FK |
| `uq_…_id_proposed` / `uq_…_id_from` | UNIQUE `(id, proposed_authority)`, `(id, from_authority)` | targets of the disposition's outcome FKs, which is what lets `resulting_authority` be proved in-row |
| `uq_…_previous_disposition` | UNIQUE `(previous_disposition_id)` | **two successors to one authority state** — a forked history, a stale apply, a concurrent double cutover, or a second pending revision while one is open |
| `uq_…_one_genesis` | partial UNIQUE `(unit_id) WHERE previous_disposition_id IS NULL` | a second chain for one unit |
| `fk_…_previous_same_unit` | FK `(previous_disposition_id, unit_id)` → `dispositions(id, unit_id)` | chaining onto another unit's history |
| `fk_…_previous_epoch` | FK `(previous_disposition_id, previous_epoch)` → `dispositions(id, epoch)` | a predecessor epoch that is not the predecessor's |
| `ck_…_epoch_succeeds` | `CHECK (previous_epoch IS NULL AND epoch = 0) OR (epoch = previous_epoch + 1)` | a gap or a repeat in the chain |
| `fk_…_previous_authority` | FK `(previous_disposition_id, from_authority)` → `dispositions(id, resulting_authority)` | authorizing against an authority that was not in force |
| `fk_…_transition_legal` | FK `(from_authority, proposed_authority)` → `migration_authority_transitions` | an illegal transition, e.g. `legacy → database`, `shadow → database`, `database → shadow` |
| `ck_…_genesis_is_legacy` | `CHECK (previous_disposition_id IS NOT NULL OR proposed_authority = 'legacy')` | a unit whose recorded history begins anywhere but `legacy`. Needed because the transition FK has a NULL component at genesis |
| `ck_…_previous_triple` | `CHECK ((previous_disposition_id IS NULL) = (from_authority IS NULL) AND (previous_disposition_id IS NULL) = (previous_epoch IS NULL))` | half a predecessor |
| `ck_…_no_backdating` | `CHECK (effective_at >= created_at)` | a change recorded as having been effective before it was authorized |
| `ck_…_deadline_after_effective` | `CHECK (activation_deadline_at > effective_at)` | a revision that expires before it may be activated |
| `ck_…_verification_window` | the two `verification_until` checks above | a `cutover` with no bounded verification window, or one ending before it starts |
| trigger `…_append_only` | `BEFORE UPDATE OR DELETE`, `reject_history_mutation` (migration 0002) | rewriting or erasing an authorization, **including by the schema owner** |

### 3.4 `migration_authority_dispositions` — what actually took effect

Ownership: package 5.0. Writers: `ActivateAuthorityChange` and
`AbandonAuthorityRevision` as `freedom_migration_coordinator`, plus the
migration's genesis seed. **This table is the only source of a unit's authority**
(§2.5). Append-only. **Unchanged from revision 2 except for the activation
trigger's fourth condition.**

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | `UUID` | no | PK |
| `revision_id` | `UUID` | no | **UNIQUE.** FK → `migration_authority_revisions(id)` `RESTRICT`. One outcome per authorization |
| `unit_id` | `UUID` | no | FK, and composite FK `(revision_id, unit_id)` → `revisions(id, unit_id)` so it cannot disagree with the revision |
| `epoch` | `BIGINT` | no | **UNIQUE `(unit_id, epoch)`.** Composite FK `(revision_id, epoch)` → `revisions(id, epoch)`. This pair is what makes the `ORDER BY epoch DESC LIMIT 1` read total and unambiguous |
| `disposition` | `VARCHAR(10)` | no | `CHECK IN ('activated','abandoned')` |
| `proposed_authority` | `VARCHAR(10)` | no | carried from the revision by FK `(revision_id, proposed_authority)`; present only so the next column can be proved in-row |
| `from_authority` | `VARCHAR(10)` | **yes** | carried by FK `(revision_id, from_authority)`. **Reason for nullability:** the genesis revision has none |
| `resulting_authority` | `VARCHAR(10)` | no | `CHECK (resulting_authority = CASE disposition WHEN 'activated' THEN proposed_authority ELSE from_authority END)`. An abandoned revision leaves the authority exactly where it was, and the database proves it rather than trusting the writer |
| `control_plane_version` | `BIGINT` | no | **UNIQUE**, from a sequence. A single global monotone version of the whole authority map |
| `decided_at` | `TIMESTAMPTZ` | no | `DEFAULT now()` |
| `decided_by_platform_account_id` | `UUID` | **yes** | FK → `platform_accounts(id)` `RESTRICT`. **Reason for nullability:** the genesis disposition is written by the migration, not by a person |
| `correlation_id` | `UUID` | no | as §3.3 |

**Constraints and the activation trigger.**

| Name | Kind | What it makes impossible |
|---|---|---|
| `uq_…_revision` | UNIQUE `(revision_id)` | two outcomes for one authorization; also the concurrency fence — two concurrent activations, one wins |
| `uq_…_unit_epoch` | UNIQUE `(unit_id, epoch)` | two current heads at one chain position |
| `uq_…_control_plane_version` | UNIQUE | an ambiguous global version |
| `uq_…_id_unit`, `uq_…_id_epoch`, `uq_…_id_resulting` | UNIQUE | targets of the revision's composite predecessor FKs |
| `ck_…_resulting_authority` | the `CASE` check above | an outcome that does not follow from its disposition |
| `ck_…_genesis_activated` | `CHECK (from_authority IS NOT NULL OR disposition = 'activated')` | an abandoned genesis, which would leave a unit with no authority at all |
| trigger `…_append_only` | `BEFORE UPDATE OR DELETE`, `reject_history_mutation` | rewriting or erasing what took effect |
| trigger `…_activation_is_fenced` | `BEFORE INSERT`, new in `0014` | **the finding's core control** — see below |

The activation trigger refuses an `INSERT` with `disposition = 'activated'`
unless every one of these holds, evaluated against the **database's** `now()`:

1. `now() >= revision.effective_at` — no early activation (§2.5);
2. `now() <= revision.activation_deadline_at` — no activation of a revision
   everybody has forgotten;
3. the predecessor disposition exists and is the unit's current head — implied by
   `uq_…_unit_epoch` plus the revision's chain FKs, and re-asserted here so the
   refusal names the reason; and
4. **if `migration_authority_transitions.requires_external_writer_fence` is true
   for `(from_authority, proposed_authority)`**, then for **every** required
   fence method there exists a `migration_quiescence_evidence` row for this
   revision with `observation = 'clear'`, `observed_at > revision.created_at` and
   `observed_at >= now() - N5.0-16`; and
5. **new in revision 5** — the `dispatch_journal_clear` row's
   `journal_generation_id` is the **current head** of the
   `sheet_writer_journal_generations` chain for that `fenced_writer` (no row names
   it as a predecessor), **and** no generation has been registered with
   `created_at > evidence.observed_at`.

Condition 4 replaces revision 2's lease/acknowledgement test. The difference that
matters: the rows it reads were written by a principal the fenced writer cannot
authenticate as, and they record what a supervisor observed rather than what a
process claimed about itself.

**Condition 5 is P5.0-R5's control in the database.** Without it, a
`dispatch_journal_clear` row remains satisfying after the journal it described has
been rotated, reset, restored or replaced — which is the handoff's *"reboot,
restore, or deployment rollback cannot reuse stale clear evidence"*. Its two
clauses answer two different cases: the head test refuses evidence about a
**superseded** journal, and the `created_at` test refuses evidence taken **before**
a rotation that has happened since. Neither can be satisfied by anything the
writer does, because the writer cannot register a generation.

Putting conditions 4 and 5 in the database duplicates checks the coordinator
command also makes, which is a cost worth naming: they must be tested against each
other, and WP-8 does exactly that. The reason to pay it is that the coordinator
command is not the only conceivable writer of this table over the platform's
life, and an activation without a fence proof — or against a journal that no
longer exists — is precisely the condition P5.0-R1 and P5.0-R5 say must be
impossible.

An `abandoned` disposition is refused only if the revision already has one; it is
legal at any time before activation, because abandoning changes nothing and
therefore needs no fence.

### 3.5 `migration_quiescence_evidence` — the observed fence record

**New in revision 3; it replaced `migration_authority_leases` and
`migration_quiesce_acknowledgements`, both withdrawn. Revision 4 changes one
column's vocabulary and renames what this table is called in prose: it is a
record of what was observed, not a *proof* of quiescence,** because §2.8 records
that one of the things a reader would want it to prove cannot be proved.

Ownership: package 5.0. Writer: `RecordQuiescenceEvidence`, running as
`freedom_migration_coordinator` in the host-local operator command's process, and
nothing else. Append-only. **No application process holds any privilege on this
table** — not `INSERT`, not `UPDATE`, not `DELETE`, not `SELECT`.

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | `UUID` | no | PK |
| `revision_id` | `UUID` | no | FK → `revisions(id)` `RESTRICT`. Evidence is bound to the authorization it fences; it cannot be reused for a later one |
| `fenced_writer` | `VARCHAR(40)` | no | `CHECK IN ('sheet_writer')`. The closed vocabulary of external writers this platform has. It is a `CHECK` and not free text because an unrecognised writer name in an evidence row would silently satisfy nothing while looking like proof |
| `fence_method` | `VARCHAR(40)` | no | `CHECK IN ('external_write_access_revoked','unit_inactive','cgroup_empty','host_scan_clear','dispatch_journal_clear')`. **`dispatch_journal_clear` is new in revision 4** and is the one value whose underlying observation the fenced writer authors (§2.4). It is in the same closed vocabulary because the trigger must require it; it is not equal in strength to the other four, and §2.4 says so at the point a reader meets it |
| `observation` | `VARCHAR(10)` | no | `CHECK (observation = 'clear')`. The column exists so the claim is explicit; the constraint exists so a *negative* observation cannot be recorded as proof. An observation that is not clear is a refusal in the coordinator command and a line in its output, never a row here |
| `observed_detail` | `VARCHAR(200)` | no | `CHECK` not blank. What was actually seen, in a form an auditor can re-derive: the unit's `ActiveState`/`SubState`, the cgroup path and its process count, the scan's pattern and match count, or the Drive permission id and its resulting role. **No credential material, no token, no service-account key, no player data** — the same rule `audit_events` payloads follow |
| `observed_at` | `TIMESTAMPTZ` | no | `DEFAULT now()`. The database's clock, not the observer's |
| `observed_by_platform_account_id` | `UUID` | no | FK → `platform_accounts(id)` `RESTRICT`. The Platform Administrator resolved at execution |
| `correlation_id` | `UUID` | no | as §3.3 |
| **`journal_generation_id`** | `UUID` | **yes** | **New in revision 5.** FK → `sheet_writer_journal_generations(id)` `RESTRICT`. **Reason for nullability:** only a `dispatch_journal_clear` row has one, and the biconditional `CHECK` below makes the nullability exact rather than optional |
| **`journal_last_sequence`** | `BIGINT` | **yes** | **New.** The `seq` of the last record the coordinator read. `CHECK (journal_last_sequence IS NULL OR journal_last_sequence >= 0)`. It is what makes *"this observation was of that much journal"* checkable after the fact |
| **`journal_head_digest`** | `CHAR(64)` | **yes** | **New.** The `record_hash` of that last record, lowercase hex. Together with the sequence it pins the exact content the observation was made against, so a later append is visible to an auditor |

**Constraints.**

| Name | Kind | What it makes impossible |
|---|---|---|
| `pk_migration_quiescence_evidence` | PK `(id)` | — |
| `uq_…_revision_writer_method` | UNIQUE `(revision_id, fenced_writer, fence_method)` | two rows claiming the same observation for one revision, so a retry is idempotent by constraint rather than by convention |
| `ck_…_observation_clear` | `CHECK (observation = 'clear')` | recording a failed observation as proof |
| `ck_…_detail_not_blank` | `CHECK (btrim(observed_detail) <> '')` | evidence with nothing in it |
| `ck_…_observed_after_authorization` | enforced by the recording trigger, which compares `observed_at > revision.created_at` | reusing an observation taken before the revision existed |
| **`ck_…_journal_columns_iff_journal_method`** | `CHECK ((fence_method = 'dispatch_journal_clear') = (journal_generation_id IS NOT NULL))`, and the same equivalence for `journal_last_sequence` and `journal_head_digest` | **new in revision 5** — a journal observation with no journal identity, or a *non*-journal observation carrying one. The binding is structural rather than a rule the coordinator has to remember |
| **`ck_…_journal_head_digest_hex`** | `CHECK (journal_head_digest IS NULL OR journal_head_digest ~ '^[0-9a-f]{64}$')` | **new** — a digest that is not one |
| trigger `…_append_only` | `BEFORE UPDATE OR DELETE`, `reject_history_mutation` | revising or withdrawing evidence, **including by the schema owner** |

**Which methods are required.** For `fenced_writer = 'sheet_writer'`, all
**five**: `external_write_access_revoked`, `unit_inactive`, `cgroup_empty`,
`host_scan_clear` and `dispatch_journal_clear`. The set is a constant in migration
`0014` and is read by both the trigger and the coordinator command from one place,
so the two cannot disagree about what a complete fence is.

**What a complete set does and does not mean.** It means: no writer systemd
started is running, its cgroup is empty, a host scan at that instant found no
other, Google will refuse a new write from the service account, and **a journal
that validated against its seal, its inode, its hash chain and its currently
registered generation** recorded no dispatch without an outcome. **It does not
mean the Sheet's final state is established** — §2.8's sixth row — and it does not
mean the journal is complete against a writer whose dispatch path was replaced —
§2.9. The distinction is recorded here, in the table's own section, because this
table is where a future reader will look for the strongest claim the package
makes, and the strongest claim is narrower than the table's name suggests.

**Growth.** At most five rows per fenced authority change, and fenced changes are
roughly one per unit per cutover and rollback — tens of rows for the whole of
Phase 5. Retention: **indefinite**. It is the record that a cutover was fenced,
and it is the smallest table in the package.

### 3.6 Reused without change

| Table | Use | Change |
|---|---|---|
| `idempotency_keys` | one receipt per accepted command under scopes `migration.authorize_authority`, `migration.activate_authority`, `migration.abandon_revision`, `migration.record_quiescence_evidence` and **`migration.register_journal_generation`**; `admission_id` NULL | **none.** The existing `submission_names_its_admission` check already permits a NULL admission for every scope but the Foundry submission's, and the existing `(scope, key)` unique index is the fence |
| `audit_events` | one row per accepted command — `migration.authority_authorized`, `migration.authority_activated`, `migration.revision_abandoned`, `migration.quiescence_observed` and **`migration.journal_generation_registered`** — with `actor_platform_account_id` set, `actor_capability = 'platform_administrator'`, `AuditSource.SYSTEM`, and a payload of unit key, from/to authority, epoch, effective instant, gate reference; for the evidence command the writer and method; and for the generation command the generation sequence, writer unit, filesystem type and digests. No player data, no credential material, no path outside the fixed hierarchy | **none to the schema.** The payload keys must be added to the audit projection's classified set in `application/web/audit_search.py`, which the `test_every_payload_key_this_repository_writes_is_classified` regression already enforces. That is a code change |
| `platform_accounts` | the authorizing, activating, observing **and registering** administrator | **none** |

`characters` is **not referenced by this package at all**: the only foreign key to
it was `shadow_comparisons.character_id`, which OD-55 moves to package 5.1.

**Two additions in revision 5**, neither a schema change: a fifth idempotency
scope `migration.register_journal_generation`, and a fifth audit action
`migration.journal_generation_registered`, whose payload keys — the generation
sequence, the writer unit, the filesystem type and the digests — must be added to
the classified set in `application/web/audit_search.py`. **No cell value, no path
outside the fixed hierarchy, no credential material and no player data** appear in
that payload, and the existing
`test_every_payload_key_this_repository_writes_is_classified` regression enforces
the classification.

### 3.7 `sheet_writer_journal_generations` — the registered journal identity

**New in revision 5, and it is the schema half of the P5.0-R5 remediation.**

Ownership: package 5.0. Writer: `RegisterJournalGeneration`, running as
`freedom_migration_coordinator` in the host-local operator command's process, and
nothing else. Append-only. **No application process holds any privilege on this
table** — not `INSERT`, not `UPDATE`, not `DELETE`, not `SELECT` — and
`freedom-sheet-writer` holds no database connection at all.

**Why it exists, in one sentence.** The activation trigger must be able to refuse
journal evidence that describes a journal which has since been rotated, reset,
restored or replaced, and **a trigger cannot refuse what the database has never
heard of.**

**Why it is not the journal.** It registers a journal's *identity* — created once
per generation, by a human, at provisioning and rotation. **The per-dispatch
records stay a host file** (package plan §2.13.2 S-4), so the Freedom bot's
legacy mutation path takes no PostgreSQL availability dependency, which is the
property withdrawing the lease bought and revision 5 does not give back.

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | `UUID` | no | PK, application-generated |
| `generation_seq` | `BIGINT` | no | **UNIQUE.** `CHECK (generation_seq >= 1)`, from the `sheet_writer_journal_generation_seq` sequence. The first generation is 1 |
| `fenced_writer` | `VARCHAR(40)` | no | `CHECK IN ('sheet_writer')` — the **same closed vocabulary** as `migration_quiescence_evidence.fenced_writer`, deliberately, so the two cannot drift |
| `predecessor_generation_id` | `UUID` | **yes** | **UNIQUE.** FK → `sheet_writer_journal_generations(id)` `RESTRICT`. **Reason for nullability:** the first generation has no predecessor. **This column is the chain fence**, exactly as `previous_disposition_id` is in §3.3: one successor per generation, ever |
| `predecessor_seq` | `BIGINT` | **yes** | Composite FK `(predecessor_generation_id, predecessor_seq)` → `(id, generation_seq)` plus `CHECK` below, so the chain arithmetic is provable rather than asserted |
| `predecessor_close_digest` | `CHAR(64)` | **yes** | SHA-256 of the predecessor's `.close` manifest. **Reason for nullability:** the first generation has none. **This is the "cannot create a new generation while the previous is unsealed" rule expressed as a constraint**: a `.close` manifest exists only after `freedom-journal-admin seal` |
| `journal_path` | `VARCHAR(200)` | no | absolute. `CHECK (journal_path LIKE '/var/lib/freedom-sheet-writer/journal/%')` and not blank. The prefix is a `CHECK` and not a convention because P5.0-R5 was, in part, a path |
| `journal_device` | `BIGINT` | no | `st_dev` of the journal file at registration |
| `journal_inode` | `BIGINT` | no | `st_ino`. **UNIQUE `(journal_device, journal_inode)`**, so a recycled inode cannot be registered twice |
| `seal_body_digest` | `CHAR(64)` | no | **New in revision 6.** SHA-256 over the canonical **seal body** — the part of the seal fixed *before* the journal file exists (package plan §2.13.5a step C2). It is the anchor the genesis record's `prev_hash` carries, so registering it lets an auditor re-derive the chain root without re-reading the seal. `CHECK` lowercase hex |
| `genesis_record_digest` | `CHAR(64)` | no | the `record_hash` of the journal's record 0. **Derived**, not merely observed: record 0's whole content is a pure function of the seal body, so any holder of the seal recomputes this rather than trusting it — which is what makes the construction acyclic (package plan §2.13.5a step C3). `CHECK` lowercase hex. **An empty file has no genesis record and therefore cannot be registered** |
| `seal_digest` | `CHAR(64)` | no | SHA-256 over the exact bytes of the finished `chattr +i` seal file — body **and** binding section, and, after revision 7, **nothing else**: the file's length is exactly `len(SB) + len(BND)`, so a trailing byte is detectable. It is a **leaf**: no on-disk artifact contains it, every reader recomputes it, and nothing upstream depends on it. *Revision 5 made the genesis record hash this value, which was the cycle.* **Revision 7 gives this column a second, load-bearing job**: the seal's binding section holds three fields, all of which the writer authenticates from disk, so the one falsification the **writer** cannot refuse — an attacker holding package plan §2.13.5c's **`A1 + A2 + A3`**, rewriting the seal body *and* the journal's record 0 consistently — is refused **here and nowhere else** (**F-1b**). **Revision 8 states the boundary above that too, relabelled in revision 9**: an attacker holding `A1 + A2 + A3` **and** `A9` — a PostgreSQL superuser — writes this column as well, and **no check in this design refuses that** (package plan risk **R-5.0-12**). It is recorded as a residual, not described as a refusal |
| `host_machine_id` | `CHAR(32)` | no | `/etc/machine-id`. `CHECK` lowercase hex. A journal restored onto another host is refused — **and revision 9 bounds that sentence, which was this artifact's own share of remediation R8-D.** It holds for an **unforged** restore: the writer refuses at **W10** with `SW-J23` and the coordinator at **C-d** with `J-16`. It does **not** hold when an actor holding package-plan §2.13.5c's **`A6`** rewrites `/etc/machine-id` on the restoring host **to this recorded value** — the seal, the file and **this column** then all carry the same value, so neither comparison has anything to disagree with. **This column stores a copy of the fact; it is not an independent attestation of it**, and no comparison between two copies of one recorded value can detect a forgery of what it records. That outcome is package-plan residual **R-5.0-13**; the design change that would make it a refusal — an independent authenticated host-bound value, which **would** add a column here — is routed as **D5.0-13 / OD-66 option A-2** and is not adopted |
| `writer_unit` | `VARCHAR(80)` | no | `CHECK (btrim(writer_unit) <> '')`. `freedom-sheet-writer.service` |
| `writer_deployment_digest` | `CHAR(64)` | no | SHA-256 over the deployed writer's file manifest — **`deployment_manifest_digest()`, specified in package plan §2.13.2c and new in revision 9**: every deployed file with its path, mode, uid, gid and content digest, plus the unit file **and its `.service.d/` drop-ins**, canonically encoded and sorted. **This is the handoff's "bound to the writer deployment"**: redeploying the writer requires a new generation, so a rollback cannot silently reuse the old journal's clear evidence. **Revision 9 also fixes where the value is validated** (**R8-A**): root **computes** it at Algorithm C **C0** and refuses unless the operator's supplied value equals it, so what reaches this column has been checked against the **deployed bytes** before any step consumed it; **C2** recomputes it to catch a deployment changed between C0 and the probe, and the writer recomputes it at **W11**. *Revision 8 passed the supplied string to the probe at C1 and then compared it at C2 with the probe's copy of that same string, which is a tautology* |
| `source_commit` | `CHAR(40)` | no | **New in revision 12; this is the schema half of remediation R11-A.** The Git commit object id of the reviewed source the deployed writer was built from. `CHECK` lowercase hex. **It is a name, not a binding**: Git object ids are SHA-1, and the binding this column participates in is the SHA-256 `source_manifest_digest` beside it |
| `source_tree_id` | `CHAR(40)` | no | **New in revision 12.** The commit's root tree object id, recorded so an auditor can address the tree without re-reading the commit. `CHECK` lowercase hex |
| `source_manifest_digest` | `CHAR(64)` | no | **New in revision 12.** SHA-256 over `source_manifest_digest()` — package plan §2.12.5a: every deployed region-S artifact with its deployed name, its source path inside the reviewed tree, its entry class and its content digest, canonically encoded and sorted. **This is the value that makes the provenance independent of SHA-1**, because a substituted object that collided under SHA-1 has different content bytes and therefore a different value here. It is computed at **D3** from Git object bytes, recomputed at **C0** from the deployed bytes, sealed into `SB`, and recomputed by the writer at **W11a**. `CHECK` lowercase hex |
| `approved_source_revision_id` | `UUID` | **no** | **New in revision 12, and it is the fail-closed half of P5.0-SR1.** FK → `approved_source_revisions(id)` `RESTRICT`, **`NOT NULL`**. **A generation whose reviewed source has no approved revision cannot be inserted**, by any principal including the schema owner, and §3.4's activation trigger requires a registered generation — so an unprovenanced deployment cannot reach activation, and the refusal is a constraint rather than a step in `RegisterJournalGeneration` that somebody could remove. *Compare `append_only_verified`, withdrawn in revision 6: that column asked the database to believe a supplied Boolean about the host. **This column asks the database only about its own rows**, which §3.7.1 says is the one thing it can enforce* |
| `filesystem_type` | `VARCHAR(20)` | no | `CHECK IN ('ext4')`. **A closed vocabulary, so a journal on `tmpfs` cannot be registered at all.** Widening it is a schema migration and a review, which is the correct cost for a decision that P5.0-R5 shows is load-bearing |
| ~~`append_only_verified`~~ | ~~`BOOLEAN`~~ | — | **Withdrawn in revision 6, and this is remediation R5-D.** It was `CHECK (append_only_verified)`, described as making the capability probe *"enforced by a constraint rather than by a procedure step somebody could skip"*. **That was false.** A `CHECK` on a supplied Boolean constrains the supplied value to `true`; it proves that the coordinator supplied `true`, and it cannot observe a host. The re-review is correct and the column goes with the claim. §3.7.1 states what replaces it |
| `append_only_probe_version` | `VARCHAR(20)` | no | **New in revision 6.** `CHECK (append_only_probe_version IN ('jnl-probe-1'))` — a **closed vocabulary**, so a report produced by an unknown or superseded probe procedure cannot be registered, and widening it is a visible schema migration. The writer refuses a version its build does not support (package plan row **J-25**). **Revision 7 changes what `jnl-probe-1` denotes** — a four-stage procedure whose four stages all run before the report is built — **and not the vocabulary**, which is exactly the movement a closed vocabulary is meant to make visible: a later procedure takes a new value and a migration |
| `append_only_probe_digest` | `CHAR(64)` | no | **New in revision 6; its subject corrected in revision 7; its case list extended in revision 8.** SHA-256 over the canonical **probe report** of package plan §2.13.2a — **all four stages** and every one of their cases, `C-1 … C-6` (control), `P-1 … P-9` (append-only), `M-1 … M-2` (storage) and **`S4-0 … S4-3`** (systemd sandbox, `S4-0` being the positive DAC control revision 8 adds for `S4-2`), each with its expected and observed result. *Revision 6 said four stages while Algorithm C sealed three; revision 7 moves stage 4 to provisioning so the report contains what this column is said to cover, rather than re-wording the column* (**R6-A**). *Revision 8 makes the report's production, validation and sealing an executable order — created once at Algorithm C **C1**, validated at **C2**, written to disk only at **C9** — so the digest this column carries is computed over bytes that existed and were validated before any generation artifact did* (**R7-A**). The report itself is **inside the seal body**, hence covered by `seal_body_digest`, anchored by the genesis record and sealed under `chattr +i`. `CHECK` lowercase hex. **This column records an attestation bound to a re-derivable artifact. It does not prove the probe ran** — §3.7.1 |
| `append_only_probe_at` | `TIMESTAMPTZ` | no | **New in revision 6.** When the probe was executed. `CHECK (append_only_probe_at <= created_at)`, because a generation cannot be registered against a probe that had not happened when the seal was written |
| `created_at` | `TIMESTAMPTZ` | no | `DEFAULT now()`. The database's clock. It is what the activation trigger's condition 5 compares evidence against |
| `registered_by_platform_account_id` | `UUID` | no | FK → `platform_accounts(id)` `RESTRICT`. The Platform Administrator resolved **at execution** |
| `correlation_id` | `UUID` | no | as §3.3 |

**Constraints, in full.**

| Name | Kind | What it makes impossible |
|---|---|---|
| `pk_sheet_writer_journal_generations` | PK `(id)` | — |
| `uq_…_generation_seq` | UNIQUE `(generation_seq)` | two generations at one chain position |
| `uq_…_id_seq` | UNIQUE `(id, generation_seq)` | target of the composite predecessor FK |
| `uq_…_predecessor` | UNIQUE `(predecessor_generation_id)` | **two successors to one generation** — a forked journal history, which is what "reset it and start again" would look like |
| `uq_…_first_generation` | partial UNIQUE `(fenced_writer) WHERE predecessor_generation_id IS NULL` | **a second chain for one writer.** With the previous row this makes the chain linear, so *"the current generation"* is the unique row nothing names as predecessor — the same proof shape §2.5 uses for authority, and no mutable head pointer |
| `uq_…_device_inode` | UNIQUE `(journal_device, journal_inode)` | registering the same inode twice |
| `fk_…_predecessor_seq` | FK `(predecessor_generation_id, predecessor_seq)` → `(id, generation_seq)` | a predecessor sequence that is not the predecessor's |
| `ck_…_seq_succeeds` | `CHECK ((predecessor_generation_id IS NULL AND generation_seq = 1) OR (generation_seq = predecessor_seq + 1))` | a gap or a repeat in the chain |
| `ck_…_predecessor_triple` | `CHECK ((predecessor_generation_id IS NULL) = (predecessor_seq IS NULL) AND (predecessor_generation_id IS NULL) = (predecessor_close_digest IS NULL))` | half a predecessor — in particular a successor registered against a predecessor that was never sealed |
| `ck_…_digests_hex` | `CHECK` lowercase-hex on `seal_body_digest`, `genesis_record_digest`, `seal_digest`, `predecessor_close_digest`, `writer_deployment_digest`, `append_only_probe_digest`, `host_machine_id` **and, from revision 12, `source_commit`, `source_tree_id` and `source_manifest_digest`** | a digest or object-id column holding something that is not one |
| `fk_…_approved_source_revision` | FK `(approved_source_revision_id)` → `approved_source_revisions(id)` `RESTRICT`, **`NOT NULL`** | **registering a generation against a reviewed source no review approved.** With §2.3's registered-generation precondition, this is what makes an unprovenanced deployment unable to reach activation |
| `fk_…_source_revision_values` | composite FK `(approved_source_revision_id, source_commit, source_tree_id, source_manifest_digest)` → `approved_source_revisions(id, source_commit, source_tree_id, source_manifest_digest)` | **the generation's three recorded provenance values disagreeing with the approved row they name.** Without it a caller could name a valid approved revision and record different digests beside it, and `C-d` would then compare the seal against values nothing had checked. It is the same shape as `fk_…_predecessor_seq`, and for the same reason: the arithmetic is provable rather than asserted |
| `ck_…_digests_distinct` | `CHECK (seal_body_digest <> seal_digest AND genesis_record_digest <> seal_body_digest AND genesis_record_digest <> seal_digest)` | **the three artifacts being conflated**, which is the shape of the revision-5 defect. It is a **smoke check and nothing more** — three distinct SHA-256 values differ anyway — and it is included, and labelled, so that a future edit collapsing the body and the file into one value fails loudly instead of silently reintroducing the cycle |
| `ck_…_journal_path_prefix` | `CHECK (journal_path LIKE '/var/lib/freedom-sheet-writer/journal/%')` | registering a journal outside the reviewed hierarchy |
| `ck_…_filesystem_type` | `CHECK (filesystem_type IN ('ext4'))` | **registering a journal on a volatile filesystem** |
| ~~`ck_…_append_only_verified`~~ | ~~`CHECK (append_only_verified)`~~ | **Withdrawn in revision 6 with its column.** It made nothing impossible: it constrained a value the coordinator supplied |
| `ck_…_probe_version` | `CHECK (append_only_probe_version IN ('jnl-probe-1'))` | registering a report from an unknown or superseded probe procedure |
| `ck_…_probe_not_after_created` | `CHECK (append_only_probe_at <= created_at)` | registering against a probe that had not yet happened |
| `ck_…_inode_positive` | `CHECK (journal_inode > 0 AND journal_device > 0)` | a placeholder identity |
| trigger `…_append_only` | `BEFORE UPDATE OR DELETE`, `reject_history_mutation` | rewriting or erasing a generation record, **including by the schema owner**. Supersession is the successor's own row, **never an `UPDATE`** — so the package's "no mutable table anywhere" property (§5) is preserved |

**Growth.** One row per journal generation: one at provisioning, one per rotation.
Rotation is required by N5.0-22 (size) and by each writer redeployment — on the
order of tens of rows for the whole of Phase 5. Retention: **indefinite**. It is
the index of the evidence archive, and deleting a row would orphan the file it
names.

**What this table cannot do**, stated where a reader meets it: it does not make
the journal complete (§2.9), it does not observe Google (§2.8), it does not prove
that a host-side probe ran (§3.7.1), **it does not attest the host — new in
revision 9, and it is the correction R8-D forces here: `host_machine_id` is a
*copy* of `/etc/machine-id`, so an actor able to write that file on the host
where the tree is read makes the row agree rather than disagree (package-plan
**F-7**, residual **R-5.0-13**)** — **it does not prove that the deployed program was built from a reviewed source
— new in revision 12: `source_commit`, `source_tree_id` and
`source_manifest_digest` are *copies* of values root computed from Git objects at
package plan **D3** and **C0**, and what this table adds is not verification but
a `NOT NULL` foreign key to §3.8, so a generation with no approved revision
cannot exist** — and it does not prove that the file on disk
*today* still matches the row — that is the coordinator's `observe`, which
re-reads the seal, re-derives the genesis record, re-checks the inode and the
chain at the moment it records evidence, and which is why the evidence row carries
the head digest as well as the generation id.

**What this table uniquely can do — new in revision 7, and it is the schema half
of remediation R6-B.** Every other falsification of the on-disk evidence is
refused by the **writer**, from the seal and the journal alone, with no database
reachable: an altered seal body no longer derives record 0, an altered binding
field no longer matches `fstat` or the derived genesis digest, an altered probe
report no longer matches its digest, a wrong host or a wrong deployment no longer
matches the body. **One falsification is not**: an actor holding package plan
§2.13.5c's **`A1`** (the `CAP_LINUX_IMMUTABLE` half of `FS_IOC_SETFLAGS`)
together with **`A10`** and **`A11`** (the owner-or-`CAP_FOWNER` half, over the
`freedomsheet`-owned journal and over the root-owned seal respectively),
**`A3`** (DAC on `…/journal` and the seal) and **`A2`** (DAC on the journal file)
can rewrite the seal body **and** record 0 so that they agree, and restore both
attributes. *Revision 8 gave this as `K1 + K3` and credited `CAP_LINUX_IMMUTABLE`
with the discretionary access it does not confer; revision 9 stated it as
`A1 + A2 + A3` and omitted the owner authorization `FS_IOC_SETFLAGS` also
requires; revision 10 states the complete combination, which on this host means
uid 0 or a non-root identity carrying `CAP_LINUX_IMMUTABLE`, `CAP_FOWNER`,
`CAP_DAC_OVERRIDE` and `CAP_DAC_READ_SEARCH` — package-plan identity **E6**.* Nothing confined to that host distinguishes
the result from a genuine generation, because every artifact and every attribute
the writer reads is below the privilege that produced it. **The registered row is
the one copy of those digests that actor did not write**, and the coordinator's
comparison at `observe` (package plan **C-b**, **C-d**) is where it is refused.
Revision 6 claimed the writer refused *every* seal-byte alteration without a
database; it did not, and revision 7 stated the boundary here rather than leaving
it to the package plan alone.

**And the boundary above that, new in revision 8; relabelled in revision 9;
its host half corrected in revision 10.**
This table refuses **F-1b** because **`A9`** — `UPDATE`, `DELETE`, `TRUNCATE` on
an append-only chain, or direct datafile mutation — is held by **no principal
this design defines**: it is revoked from every
role including the schema owner and refused by `reject_history_mutation`, so
changing a registered digest requires a PostgreSQL **superuser** or direct
datafile access. An attacker who holds **`A1 + A2 + A3 + A10 + A11` and that superuser** writes
both copies the coordinator compares, and **no check in this design refuses
them**. *Revision 9 wrote the host half as `A1 + A2 + A3`; the corrected set is
**larger**, which makes the combination harder to assemble and changes nothing
about what this table refuses.* That is package-plan risk **R-5.0-12**, and it is recorded as a residual
for the Acceptance Authority rather than described as a refusal. What remains is
external to both stores: `sudo`'s `log_output`, journald, the `audit_events`
chain, offline backups, and the fact that a forged head has no `seal` record, no
`.close` manifest and no archive behind it.

### 3.7.1 What PostgreSQL enforces, and what it merely records — **new in revision 6; this is remediation R5-D**

Revision 5 said `CHECK (append_only_verified)` made the capability probe
*"enforced by a constraint rather than by a procedure step somebody could skip"*.
The re-review's objection is exact: **a `CHECK` on a Boolean column constrains a
supplied value.** It proves the row's author supplied `true`. It cannot observe a
host, cannot know whether `verify-capability` ran, and cannot distinguish a probe
that passed from a coordinator that typed the word. The claim is withdrawn and so
is the column.

**The authenticated actor.** A row is inserted only by
`RegisterJournalGeneration`, connecting as `freedom_migration_coordinator`,
authenticated by PostgreSQL's `peer` method as the dedicated `freedomcoord`
operating-system identity and reachable only through the `sudo` wrapper (§4.3.2,
§4.3.3). The row names `registered_by_platform_account_id`, a real
`platform_accounts` row resolved **at execution**. **No application principal holds
any privilege on this table at any level** (§4.3.4), and the writer the row is
*about* holds no database credential at all.

**The immutable fields.** All of them. `UPDATE`, `DELETE` and `TRUNCATE` are
revoked from every principal **and** refused by `reject_history_mutation`,
including for the schema owner (§4.3.4). Supersession is the successor's own row,
never an `UPDATE`. Outside the database the same act leaves an `idempotency_keys`
receipt and an `audit_events` row in the **same transaction**, and `sudo`'s
`log_output` and journald record the invocation independently.

**The binding to the exact generation, filesystem and probe version.** The probe
report names its procedure version, the filesystem type and the `st_dev` the probe
actually tested; `init-generation` refuses unless the journal file it creates has
that same `st_dev` (package plan §2.13.5a step **C7**, renumbered from C6 by
remediation R7-A); the report is then inside that
generation's seal body, which is inside that generation's genesis anchor. So a
probe report cannot be moved to another generation, another filesystem or another
probe version without breaking a digest that three independent readers recompute —
the writer at **W4**, the coordinator at **C-d**, and `archive-verify` at every
restore.

| | PostgreSQL **enforces** | PostgreSQL **merely records** |
|---|---|---|
| Shape | lowercase-hex digests, non-blank text, `append_only_probe_at <= created_at`, and closed vocabularies for `filesystem_type`, `fenced_writer` and `append_only_probe_version` | that the values describe the files that exist on disk **now** |
| Structure | one linear chain — unique `generation_seq`, unique predecessor, one first generation per fenced writer, `generation_seq = predecessor_seq + 1`, the composite FK to the predecessor, one registration per `(journal_device, journal_inode)`, and an all-or-nothing predecessor triple | that the predecessor was genuinely sealed on disk. The `.close` digest is re-read and compared by the coordinator **on the host** (package plan Algorithm **V-R**); the constraint only enforces that *a* value was supplied |
| History | append-only against every principal, including the schema owner | — |
| Authority | that the inserting principal is the coordinator, peer-authenticated as `freedomcoord`, naming a real platform account | that the human behind that account ran the probe honestly |
| Fencing | that a `dispatch_journal_clear` evidence row names the **current head** and predates no later registration (§3.4 condition 5) | — |
| The probe | **nothing whatever about whether it ran.** It enforces that a well-formed digest, a supported version and a non-future timestamp were supplied | that `verify-capability` produced *this* report at *this* time — an attestation whose falsity is **detectable**, because the report is inside the `chattr +i` seal and every reader recomputes its digest |
| The systemd sandbox (**new in revision 7; extended in revision 8**) | **nothing whatever.** No column names a unit, a directive or a mount, and none is proposed | that the probe's stage 4 observed the deployed writer unit's directives at provisioning, and — from revision 8 — that **`S4-0` proved the exact `S4-2` target writable by `freedomsheet` outside the sandbox before any `EROFS` was interpreted**. A database column could not have distinguished those two states, which is precisely why none is proposed. It is inside the same report, under the same digest, and invalidated by the same rule — a redeployment forces a rotation (package plan **J-22**, **F-6**) — which is why no second artifact, column, authority or invalidation rule exists for it |
| Host identity (**new in revision 9; this is remediation R8-D**) | **nothing whatever.** `CHECK` constrains `host_machine_id` to 32 lowercase hex characters. **No constraint can observe which host a value was read from**, and this column is a copy of that value rather than an attestation bound to the host | that the machine-id read at Algorithm C **C3** was this one. Against an **unforged** restore that is enough: the writer refuses at **W10** and the coordinator at **C-d**. Against an actor holding **`A6`**, who rewrites `/etc/machine-id` on the restoring host to this value, it records nothing anyone can disagree with, and **neither W10 nor C-d refuses** — package-plan residual **R-5.0-13**. *Revision 8's F-7 described a C-d refusal here; it is withdrawn.* A column that **could** distinguish the two — a TPM-sealed or coordinator-signed host binding — is **D5.0-13 / OD-66 option A-2**, routed under §0.2 and not adopted |
| Seal integrity against a privileged rewrite (**new in revision 7; bounded in revision 8**) | **that the registered digests cannot be changed by any principal this design defines** — `UPDATE`, `DELETE` and `TRUNCATE` are revoked from every principal and refused by `reject_history_mutation`, including for the schema owner. In package plan §2.13.5c's register that is **`A9`, PostgreSQL mutation authority, held by nobody** (`K8`'s mutation half in revision 8's withdrawn register; **the label is unchanged by revision 10's redesign, which adds `A10` and `A11` and leaves every other row's meaning alone**); changing these rows requires a PostgreSQL **superuser** or direct datafile access | nothing about the file. This is the **one** falsification the writer cannot refuse from disk (**F-1b**), so the comparison the coordinator makes against these immutable columns is the only thing that refuses it — **and it stops refusing when the attacker also holds the superuser**, which revision 8 records as residual **R-5.0-12** rather than describing as a refusal |

**Why this is stronger than the withdrawn `CHECK`, and why it is still not a
proof.** Stronger, because a false attestation is now **detectable** rather than
merely unprovable: package plan `JNL-41` alters the probe report and both the
writer and the coordinator refuse. Not a proof, because **no database constraint
can observe a host**, and this design no longer says one does. What establishes
that the probe ran is the on-disk seal, the `sudo log_output` transcript, the
journald entry, the `audit_events` row and `archive-verify` — four records, three
of them outside PostgreSQL, and the operations document names all four.

**What a reviewer should check here.** That no sentence anywhere in this artifact
or the package plan still credits a constraint with observing a host; that
`append_only_probe_digest` is described as an attestation everywhere it appears;
that the four host-side records above are named in the operations document
rather than assumed; **new in revision 8**, that **no negative capability case
anywhere is interpreted without a positive control on its exact target**, and
that **no threat class is stated by which detector fires rather than by what an
attacker must hold**; **new in revision 10**, that **no operation is described by
fewer kernel prerequisites than it has** — for `FS_IOC_SETFLAGS` that is
traversal, open, **owner-or-`CAP_FOWNER`** and `CAP_LINUX_IMMUTABLE` — and that
**no negative capability case is interpreted without a positive control on the
exact privilege under test**, which is package-plan stop condition **10m**; and — **new in revision 7** — that **no digest anywhere is
described as covering an artifact, a stage or a byte range outside the bytes it is
computed over**, which was the R6-A defect and is now package-plan stop condition
**10h**.

---

### 3.8 `approved_source_revisions` — the reviewed source a deployment may carry. **New in revision 12; this is remediation R11-A**

**Why it exists, in one sentence.** The security review found that the deployment
integrity check compared a digest of the deployed bytes with a caller-supplied
copy of that same value, so **nothing anywhere in this design named the reviewed
commit** — and a database cannot refuse a provenance it has never heard of, for
exactly the reason §3.7 gives about generations.

Ownership: package 5.0. Writer: `migration-authority`, running as
`freedom_migration_coordinator` in the host-local operator command's process, and
nothing else. **Append-only.** **No application process holds any privilege on
this table** — not `INSERT`, not `UPDATE`, not `DELETE`, not `SELECT`.

**Why it is not the approval.** It records that a named human, at a named time,
approved a named immutable Git object for a named component, and it names the
review document. **It does not verify that the review happened**, and it cannot:
that is a governance fact carried by `review_reference` and by the change log.
What it does is make the fact **durable, attributable and referenceable by a
foreign key**, so that a generation can be structurally unable to exist without
one.

| Column | Type | Null | Rule |
|---|---|---|---|
| `id` | `UUID` | no | PK, application-generated |
| `component` | `VARCHAR(40)` | no | `CHECK IN ('sheet_writer', 'coordinator')` — a **closed vocabulary**, the same discipline `fenced_writer` follows. A third deployed component is a migration and a review |
| `source_commit` | `CHAR(40)` | no | the reviewed Git commit object id. `CHECK` lowercase hex. **UNIQUE `(component, source_commit)`**, so one commit is approved at most once per component and a second approval is a visible conflict rather than a silent duplicate |
| `source_tree_id` | `CHAR(40)` | no | the commit's root tree object id. `CHECK` lowercase hex |
| `source_manifest_digest` | `CHAR(64)` | no | SHA-256 over package plan §2.12.5a's `source_manifest_digest()` for that tree. **UNIQUE `(component, source_manifest_digest)`** — two different commits with byte-identical deployed content are the same deployment, and approving both would let a generation name one while the deployment matched the other. `CHECK` lowercase hex |
| `review_reference` | `VARCHAR(200)` | no | the review artifact that approved it — a document path and revision. `CHECK (btrim(review_reference) <> '')`. **It is a pointer, not a proof**, and this table asserts nothing about what it points at |
| `approved_by_platform_account_id` | `UUID` | no | FK → `platform_accounts(id)` `RESTRICT`. The Platform Administrator resolved **at execution**, exactly as §3.7's `registered_by_platform_account_id` is |
| `approved_at` | `TIMESTAMPTZ` | no | when the approval was given. `CHECK (approved_at <= created_at)`, because a revision cannot be registered against an approval that had not happened |
| `created_at` | `TIMESTAMPTZ` | no | `DEFAULT now()`. The database's clock |
| `correlation_id` | `UUID` | no | as §3.3 |

**Constraints, in full.**

| Name | Kind | What it makes impossible |
|---|---|---|
| `pk_approved_source_revisions` | PK `(id)` | — |
| `uq_…_component_commit` | UNIQUE `(component, source_commit)` | approving one commit twice for one component |
| `uq_…_component_manifest` | UNIQUE `(component, source_manifest_digest)` | two approvals whose deployed content is byte-identical, which would let a generation and a deployment agree with **different** approved rows |
| `uq_…_id_values` | UNIQUE `(id, source_commit, source_tree_id, source_manifest_digest)` | target of §3.7's composite foreign key. It exists **only** to be that target, and it is labelled so, on the `uq_…_id_seq` precedent |
| `ck_…_component` | `CHECK (component IN ('sheet_writer','coordinator'))` | a deployment component this package does not define |
| `ck_…_hex` | `CHECK` lowercase-hex on `source_commit`, `source_tree_id`, `source_manifest_digest` | an object-id or digest column holding something that is not one |
| `ck_…_review_reference_present` | `CHECK (btrim(review_reference) <> '')` | an approval with no traceable review |
| `ck_…_approved_not_after_created` | `CHECK (approved_at <= created_at)` | recording an approval that had not happened when the row was written |
| trigger `…_append_only` | `BEFORE UPDATE OR DELETE`, `reject_history_mutation` | **rewriting or erasing an approval, including by the schema owner.** There is no withdrawal column and no `revoked_at`: superseding an approval means approving another revision, and a generation binds to exactly one |

**Why there is no withdrawal, stated because a reviewer will ask.** A withdrawal
flag would have to be `UPDATE`-able, which `reject_history_mutation` refuses on
every table in this package, or it would need a second append-only table and a
"latest row wins" read — the mutable-head shape §3.7 deliberately avoids.
Neither is worth it here, because **withdrawal cannot un-deploy anything**: a
generation already registered against a revision stays registered, and what
actually stops a bad revision from being used again is that the next deployment
needs a new approval record on the host and a new generation. A revocation
capability that only affects future rows is a change-log entry, not a column.
**Its absence is a residual, not an oversight**, and it is named in the package
plan's **R-5.0-15**.

**Growth.** One row per approved deployment of each component — on the order of
tens of rows for the whole of Phase 5. Retention: **indefinite**. It is the index
of what was ever authorized to run, and §3.7's `RESTRICT` foreign key would
refuse to let a row be deleted while a generation names it in any case.

**What this table cannot do**, stated where a reader meets it, on the §3.7
precedent:

- **It does not verify a review happened.** `review_reference` is a pointer.
- **It does not verify that the commit exists**, that it is reachable, or that
  its tree hashes to `source_manifest_digest`. Those are host facts, checked by
  root at package plan **D3** and **C0** against Git object bytes; **§3.7.1's
  division applies here unchanged** — this table records an attestation and
  enforces relationships between its own rows.
- **It does not refuse an actor who holds both host and coordinator authority.**
  An actor holding **A5** rewrites the approval record, the object store and the
  provenance record on the host; if it also holds **A8** it inserts the matching
  row here and every comparison agrees. That is **R-5.0-15**, and it is the same
  shape as §3.7's **R-5.0-12**: this table is the copy the *host-only* attacker
  did not write, and nothing more.
- **What it uniquely can do** is refuse the **A5-only** attacker — the one who
  substitutes the deployment and every host artifact that describes it — because
  the row it needs is in a database whose `INSERT` privilege belongs to one
  peer-authenticated principal reachable only through the `sudoers` rule
  (§4.3.1, §4.3.3). **That is the whole of F-13's refusal**, and it is claimed no
  more widely.

## 4. Schema decision table

Reading key as in `docs/contracts/phase-3-logical-schema.md` §11: *Writer* is the
only component permitted to insert; *Retention* is the deletion rule. **The
`Runtime role` column is new in revision 3** and is the direct answer to P5.0-R4.

| Table | Owner pkg | PK | Key FKs | Uniqueness | Writer | Runtime role holds | Reader | Delete policy | Retention | PII |
|---|---|---|---|---|---|---|---|---|---|---|
| `migration_units` | 5.0 | UUID | — | `unit_key` | migration only (seed) | **`SELECT`** | the authority fence, coordinator command, monitoring | never; every FK is `RESTRICT` | indefinite | none |
| `migration_authority_transitions` | 5.0 | `(from_authority, to_authority)` | — | PK | migration only (seed) | **`SELECT`** | the revision transition FK, the activation trigger | by migration, when §15.1 removes the legacy path | indefinite | none |
| `migration_authority_revisions` | 5.0 | UUID | unit `RESTRICT`, disposition `RESTRICT` ×3, account `RESTRICT`, transitions `RESTRICT` | `(unit_id, epoch)`; `previous_disposition_id`; one genesis per unit; `(id, unit_id)`, `(id, epoch)`, `(id, proposed_authority)`, `(id, from_authority)` | `AuthorizeAuthorityChange`, as `freedom_migration_coordinator` | **`SELECT`** | monitoring, admin audit views | **append-only, never** | indefinite | authorizing account |
| `migration_authority_dispositions` | 5.0 | UUID | revision `RESTRICT` ×4, unit `RESTRICT`, account `RESTRICT` | `revision_id`; `(unit_id, epoch)`; `control_plane_version`; `(id, unit_id)`, `(id, epoch)`, `(id, resulting_authority)` | `ActivateAuthorityChange`, `AbandonAuthorityRevision`, as `freedom_migration_coordinator`, plus the genesis seed | **`SELECT`** | **every authority read and every authority-fence trigger in the platform**; monitoring | **append-only, never** | indefinite | deciding account |
| `migration_quiescence_evidence` | 5.0 | UUID | revision `RESTRICT`, account `RESTRICT`, **generation `RESTRICT`** | `(revision_id, fenced_writer, fence_method)` | `RecordQuiescenceEvidence`, as `freedom_migration_coordinator`, authenticated by peer as the dedicated `freedomcoord` OS identity (§4.3.2) | **nothing at all** | the activation trigger, the coordinator command, monitoring | **append-only, never** | indefinite — it is the record that a cutover was fenced | observing account |
| **`sheet_writer_journal_generations`** | 5.0 | UUID | predecessor self `RESTRICT` ×2, account `RESTRICT`, **approved source revision `RESTRICT` ×2, one of them `NOT NULL`** *(rev 12)* | `generation_seq`; `predecessor_generation_id`; one first generation per writer; `(journal_device, journal_inode)`; `(id, generation_seq)` | `RegisterJournalGeneration`, as `freedom_migration_coordinator` | **nothing at all** | the activation trigger's condition 5, the coordinator command, the `migration_journal_generation` health check | **append-only, never**; supersession is the successor's own row | indefinite — it is the index of the evidence archive | registering account |
| **`approved_source_revisions`** *(new in revision 12)* | 5.0 | UUID | approving account `RESTRICT` | `(component, source_commit)`; `(component, source_manifest_digest)`; `(id, source_commit, source_tree_id, source_manifest_digest)` | the coordinator, at approval | **nothing at all** | `RegisterJournalGeneration`'s lookup, and §3.7's two foreign keys | **append-only, never**; there is no withdrawal column, and superseding means approving another revision | indefinite — it is the index of what was ever authorized to run, and §3.7's `RESTRICT` would refuse a delete in any case | approving account |
| `idempotency_keys` | existing | existing | existing | existing | the coordinator under its **five** 5.0 scopes; runtime services under theirs | existing | replay | existing | none | none |
| `audit_events` | existing | existing | existing | existing | the coordinator; runtime services | existing (`SELECT, INSERT`) | Council/admin | **append-only, never** | indefinite (OD-23) | actor |

### 4.1 Cardinalities and stable identities

| Relationship | Cardinality | Identity |
|---|---|---|
| `migration_units` → revisions | 1 : N, N ≥ 1 after seeding | unit identity is `unit_key`, stable and controlled by the manifest; the UUID is the foreign key |
| revision → disposition | 1 : 0..1 | a revision without a disposition is *pending* and is authority for nothing |
| revision → quiescence evidence | 1 : 0..5 | one row per `(fenced_writer, fence_method)`; a fenced transition needs all five before it may activate, **and the `dispatch_journal_clear` row must additionally name the current registered generation** (§3.4 condition 5) |
| disposition → successor revision | 1 : 0..1, forming one linear chain per unit | `(unit_id, epoch)` is the chain's coordinate; there is no version integer and no mutable head pointer |
| **generation → successor generation** | 1 : 0..1, forming **one linear chain per fenced writer** | `generation_seq` is the chain's coordinate. The current generation is the unique row nothing names as its predecessor — **the same shape as the authority chain, and for the same reason**: no mutable head pointer means no `UPDATE` and no lost update |
| **generation → quiescence evidence** | 1 : N | one `dispatch_journal_clear` row per fenced revision observed against that generation. `RESTRICT` on delete, so a generation naming an archived journal cannot be removed while evidence cites it |
| `platform_accounts` → revisions, dispositions, evidence, **generations** | 1 : N | the stable platform account (ADR 0010 D1), never a Discord snowflake |

### 4.2 Expected access patterns and bounded pagination

| Query | Caller | Frequency | Index | Bound |
|---|---|---|---|---|
| The whole authority map | every process, at start | once per process start | `DISTINCT ON (unit_id) … ORDER BY unit_id, epoch DESC` on `uq_dispositions_unit_epoch` | whole table; ~40 units, one row each at seeding, and one more per authority change ever |
| One unit's current authority | **the authority-fence trigger, inside every authoritative write transaction** | per authoritative write | same index, `LIMIT 1` | 1 row. This is the highest-frequency query in the package and the reason the read is a single indexed lookup rather than a join |
| Any pending revision | coordinator `status`, monitoring | per monitoring interval | `LEFT JOIN … WHERE d.id IS NULL` over `uq_revisions_unit_epoch` | at most one per unit by `uq_…_previous_disposition` |
| Evidence for a revision | the activation trigger, `status` | per activation | `(revision_id, fenced_writer, fence_method)` | at most five rows |
| **The current journal generation** | the activation trigger's condition 5, the coordinator's `observe` and `register`, the `migration_journal_generation` check | per activation, per observation, per monitoring interval | `uq_…_predecessor` anti-join, or `ORDER BY generation_seq DESC LIMIT 1` on `uq_…_generation_seq` | **1 row.** Tens of rows in the table for the whole of Phase 5 |
| One unit's full chain | coordinator `status`, gate evidence | rare | `(unit_id, epoch DESC)` | explicit `LIMIT`, newest first |

No query in this package returns an unbounded history, and the largest table is
bounded by *authority changes ever made* — tens of rows for the whole of Phase 5.
Plan §7.7 and the `.agents/AGENTS.md` pagination rule are satisfied by
construction. **Revision 2's once-per-ten-seconds-per-process renewal query is
gone with the lease**, which also removes a standing three-process write load
against PostgreSQL.

### 4.3 Principals, identities, grants and the host boundary — P5.0-R4

Revision 2 had one application principal and asked the schema to believe an
application convention. Revision 3 separated authority-plane writes from the
application and named a peer-authenticated role. **Revision 3's gap, which the
re-review found, is that peer authentication trusts an *operating-system*
identity and revision 3 never said which one.** A role that any local process can
authenticate as is not isolated; it is renamed. This section closes that, and it
is the part of the artifact that grew.

Package plan §2.12 carries the deployment detail, the wrapper, the threat-vector
table and the lifecycle procedures. This section carries what the schema itself
must be true of: the principals, the identities they bind to, the authentication
layers, the grants, and the evidence.

#### 4.3.1 Three database principals

| Principal | Exists today? | Authenticated how | May do what, on the **seven** 5.0 tables |
|---|---|---|---|
| schema owner (migration role) | **yes** | host-local, by the deployment | DDL and the migration's own seed. Defeated by the append-only triggers for `UPDATE`/`DELETE`, exactly as it is for `audit_events` today |
| `__APP_ROLE__` — the restricted runtime role shared by `freedom-bot`, `freedom-web` and `freedom-worker` | **yes** | password/socket credential in each service's environment file | **`SELECT` on four tables, nothing on the other three** *(two before revision 12 added `approved_source_revisions`)*. No `INSERT`, `UPDATE`, `DELETE` or `TRUNCATE` anywhere in this package. **Revision 5 removes `freedom-sheet-writer` from this row**: the writer holds **no database credential and opens no connection at all**, which is what keeps the legacy mutation path free of a PostgreSQL dependency (§0.2) |
| **`freedom_migration_coordinator`** | **no — proposed, D5.0-11 / OD-64** | **peer** authentication over the Unix-domain socket, **by the dedicated `freedomcoord` operating-system account and by no other** (§4.3.2). No password, no TCP login, no service unit references it | `SELECT, INSERT` on revisions, dispositions, quiescence evidence, **journal generations** and — **new in revision 12** — **approved source revisions**; `SELECT` on units and transitions; `SELECT, INSERT` on `idempotency_keys` and `audit_events` for its own receipts. No `UPDATE`, no `DELETE`, no `TRUNCATE`, anywhere |

#### 4.3.2 The operating-system identity the peer method trusts — **corrected in revision 12; this is remediation R11-B**

**The defect, conceded before its replacement.** Revisions 6 through 11 said here
that `freedomcoord` has *"no supplementary groups"* and is *"in no group any
service identity holds"* — **and then listed `freedomjournal` for it, and for
`freedomsheet`, in the table two lines below.** Both halves could not be true, and
the same contradiction ran through package plan §2.12.2 and §2.13.3. That is
security-review finding **P5.0-SR2**. The prose sentence is **withdrawn**, and
this subsection **states no membership of its own**.

**`freedomcoord` : `freedomcoord`** — a system account created for this purpose
and used for nothing else. No password, no login shell (`/usr/sbin/nologin`), no
home directory and no SSH key.

**The canonical membership table is package plan §2.12.2**, and it is the only
place primary and supplementary groups are stated for any identity in this
package. This artifact **cites** it. The rows below are reproduced for the
reader's convenience with a pointer, and **if they ever disagree with §2.12.2,
§2.12.2 is correct and this is a defect** under package-plan stop condition
**10p**.

| OS identity | Runs | Primary + supplementary groups — **per package plan §2.12.2** |
|---|---|---|
| **`freedomcoord`** *(proposed)* | `migration-authority`, through `sudo` only | `freedomcoord` + `freedomjournal` |
| **`freedomsheet`** *(proposed, D5.0-12)* | `freedom-sheet-writer` | `freedomsheet` + `freedomjournal` |
| `discordbot` | `freedom-bot` | `discordbot` + none |
| `freedomweb` | `freedom-web`, `freedom-worker` | `freedomweb` + `discordbot` |
| `foundry` | the maintainer's interactive account | `foundry` + `sudo`, `users` |

**What replaces the withdrawn sentence, in the terms this artifact cares about.**
`freedomcoord` and `freedomsheet` **do** share one group, `freedomjournal`. Its
grant is `r-x` on `…/journal` and `r--` on the seal, and **it carries no database
privilege of any kind** — which is not a mitigation but a fact about what the
group is: `pg_hba`, `pg_ident` and `SO_PEERCRED` resolve a database principal
from a **system user**, never from a group, so no membership can move a cell in
§4.3.5's authentication matrix. The three claims that replace the sentence, and
their evidence, are stated in package plan §2.12.2 and tested by `JNL-52`.

`freedomweb`'s membership of `discordbot` and the repository's group writability
are why the coordinator's code is deployed outside the repository tree (package
plan §2.12.5, observation H-1). They are recorded here because they are the
reason for a schema-adjacent design choice, not because this package changes them.
**Revision 12 narrows what that choice rests on**: no step of the deployment
algorithm reads the worktree at all (package plan §2.12.5a, `JNL-51` case (h)).

**The `freedomjournal` group, new in revision 6 and proposed rather than
adopted.** Remediation R5-B requires the writer to be able to read the generation
seal it is required to validate. A third system group — **whose membership is
stated in package plan §2.12.2 and nowhere else** — grants that read while
**tightening** the rest:
`…/journal` moves from `0751` to `root:freedomjournal 0750`, so `discordbot`,
`freedomweb` and every other local identity lose even the traverse revision 5
gave them (package plan §2.13.3). **It changes nothing in this artifact's
authentication or authorization matrices** — the group grants filesystem access
and no database privilege whatever — and it is a host-topology change, so it joins
**D5.0-12 / OD-65**'s scope and **D5.0-13 / OD-66** option A's cost. It is not
adopted here.

#### 4.3.3 The four layers a coordinator connection must pass

`pg_hba.conf`, placed **above** any broader `local all all …` line — PostgreSQL
takes the **first** matching rule, so ordering is the control:

```
# TYPE       DATABASE        USER                            ADDRESS  METHOD  OPTIONS
local        __PROD_DB__     freedom_migration_coordinator            peer    map=freedom_coord
local        all             freedom_migration_coordinator            reject
host         all             freedom_migration_coordinator   all      reject
hostssl      all             freedom_migration_coordinator   all      reject
hostnossl    all             freedom_migration_coordinator   all      reject
```

`pg_ident.conf` — one line, no regular expression, no wildcard:

```
# MAPNAME        SYSTEM-USERNAME    PG-USERNAME
freedom_coord    freedomcoord       freedom_migration_coordinator
```

The role:

```sql
CREATE ROLE freedom_migration_coordinator
    LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
    NOINHERIT NOREPLICATION NOBYPASSRLS
    PASSWORD NULL
    CONNECTION LIMIT 2;
REVOKE CONNECT ON DATABASE __PROD_DB__ FROM PUBLIC;
GRANT  CONNECT ON DATABASE __PROD_DB__ TO freedom_migration_coordinator;
```

Four independent things must all hold, and each fails in a different layer:

1. the **kernel** reports the connecting peer's uid as `freedomcoord`
   (`SO_PEERCRED`), which a process cannot forge;
2. **`pg_ident`** translates that system user to this role, and lists no other;
3. the first matching **`pg_hba`** rule is the `peer` line, requiring `local`
   transport and the production database — every other combination hits a
   `reject`, written out rather than left to the absence of a permissive line, so
   that a later broad `host all all scram-sha-256` cannot silently expose it; and
4. **`PASSWORD NULL`** means password authentication can never succeed for this
   role, so a leaked `.pgpass`, `PGPASSWORD` or environment file is worthless.

**The socket path is not one of the layers, and that is deliberate.**
`/var/run/postgresql` is `drwxrwsr-x postgres:postgres` (observation H-3), so
every local identity can reach it. A private socket directory with a restricted
mode was considered and is **not proposed**: it would add an operational failure
mode and would not add a layer, because the map already decides who the peer may
become.

#### 4.3.4 Grants

**To add to `infra/postgresql/runtime-grants.sql.tmpl`**, with the
`REVOKE ALL PRIVILEGES … FROM PUBLIC` normalisation finding O-1 requires, for all
**six** new tables — *five in revision 11; `approved_source_revisions` is added in
revision 12*:

| Grant | Tables | Why |
|---|---|---|
| `SELECT` only, to `__APP_ROLE__` | `migration_units`, `migration_authority_transitions` | the application reads the vocabulary and the legal transitions; it may not invent a unit or legalise a transition |
| `SELECT` only, to `__APP_ROLE__` | `migration_authority_revisions`, `migration_authority_dispositions` | every process must be able to read the authority it is serving, and the authority-fence trigger reads dispositions inside the writing transaction. **No process may change any unit's authority at all**, not even by defect (OD-59) |
| **nothing**, to `__APP_ROLE__` | `migration_quiescence_evidence`, **`sheet_writer_journal_generations`**, **`approved_source_revisions`** | **this is the P5.0-R4 database control, extended in revision 5.** A process that cannot write the evidence table cannot record a fence observation for itself or for anyone else; a process that cannot write the generation table cannot register a journal, supersede one, or make a stale observation look current. Neither has any reason to be *read* by the application either: the trigger reads them, and the trigger runs as the definer |
| `SELECT, INSERT` to `freedom_migration_coordinator`; `REVOKE UPDATE, DELETE, TRUNCATE` | `migration_authority_revisions`, `migration_authority_dispositions`, `migration_quiescence_evidence`, **`sheet_writer_journal_generations`**, **`approved_source_revisions`** | the coordinator appends and never revises. Even the principal that writes history cannot rewrite it |
| `SELECT` to `freedom_migration_coordinator` | `migration_units`, `migration_authority_transitions` | it reads the vocabulary it validates against; it cannot extend either |
| unchanged | `alembic_version` beyond the existing `SELECT` | — |

The `reject_history_mutation` trigger is additionally installed on
`migration_authority_revisions`, `migration_authority_dispositions`,
`migration_quiescence_evidence`, **`sheet_writer_journal_generations`** and —
**new in revision 12** — **`approved_source_revisions`**, so all **five**
append-only tables are protected against the **schema owner** as well as every
other principal — the same double control migration 0002 applies to
`audit_events`. **An approval, once recorded, cannot be edited or erased**, which
is what makes §3.7's foreign key mean something: a row that could be rewritten
would let a registered generation's provenance change after the fact.

**One grant that is deliberately absent.** `freedom-sheet-writer` receives **no
database grant of any kind, and no credential**, because it opens no connection.
Revision 4's §4.3.1 listed it as a holder of `__APP_ROLE__`; revision 5 removes
it, which is a small tightening and is stated rather than left as a silent edit.

#### 4.3.5 The complete per-principal and per-OS-identity matrix

The handoff requires this as one artifact rather than as a set of statements. It
is the schema's answer to *"who can do what, and what stops them"*.

**Authentication — can this OS identity become this database principal?**

| OS identity | schema owner | `__APP_ROLE__` | `freedom_migration_coordinator` |
|---|---|---|---|
| `root` | yes (deployment) | yes, trivially — it can read any file | **yes, trivially** — it can `setuid` to `freedomcoord`. Root is above every boundary in this design and no control here pretends otherwise |
| `foundry` (maintainer, in `sudo`) | yes, by deployment | yes, by reading an environment file | **only through the `sudoers` rule**, which runs the fixed wrapper as `freedomcoord`. `foundry` is in `sudo` and can therefore reach root, so this is a boundary against **mistake and against service compromise**, not against the maintainer |
| `discordbot` | no | yes — it holds the credential | **no.** Layers 1 and 2 |
| `freedomweb` | no | yes — it holds the credential | **no.** Layers 1 and 2 |
| `freedomsheet` *(proposed)* | no | **no — corrected in revision 5, and unchanged in revision 6.** It holds **no** database credential and its unit's environment file contains none. **The `freedomjournal` group revision 6 adds is a filesystem group and carries no database privilege of any kind** | **no.** Layers 1 and 2 |
| `freedomcoord` *(proposed)* | no | no — it holds no environment file | **yes, over the local socket to one database only.** Refused over TCP by layer 3 and refused by password by layer 4 |
| any other local uid | no | no | **no.** Layer 2 lists exactly one system user |

**Authorization — what may each database principal do on the seven tables?**

| Table | schema owner | `__APP_ROLE__` | `freedom_migration_coordinator` |
|---|---|---|---|
| `migration_units` | DDL + seed | `SELECT` | `SELECT` |
| `migration_authority_transitions` | DDL + seed | `SELECT` | `SELECT` |
| `migration_authority_revisions` | DDL + seed; `UPDATE`/`DELETE` **refused by trigger** | `SELECT` | `SELECT, INSERT`; `UPDATE`/`DELETE`/`TRUNCATE` revoked **and** trigger-refused |
| `migration_authority_dispositions` | DDL + seed; `UPDATE`/`DELETE` **refused by trigger** | `SELECT` | `SELECT, INSERT`; same |
| `migration_quiescence_evidence` | DDL; `UPDATE`/`DELETE` **refused by trigger** | **nothing** | `SELECT, INSERT`; same |
| **`sheet_writer_journal_generations`** | DDL; `UPDATE`/`DELETE` **refused by trigger** | **nothing** | `SELECT, INSERT`; same |
| **`approved_source_revisions`** *(new in revision 12)* | DDL; `UPDATE`/`DELETE` **refused by trigger** | **nothing** | `SELECT, INSERT`; same |

**The two tables together are the claim.** A forged fence observation requires
both an OS identity the map accepts *and* a grant on the evidence table. No
service identity has either, and no application principal has the second at any
privilege level.

**Revision 5 adds a second, parallel claim.** Making a *stale* journal observation
look current requires registering or superseding a generation, which requires the
same OS identity and a grant on `sheet_writer_journal_generations`. **No service
identity has either**, and the writer — the process the journal is about — has no
database access at all.

**Revision 12 adds a third, and it is the schema half of P5.0-SR1.** Making an
**unreviewed deployment** usable requires a row in `approved_source_revisions`,
because §3.7's foreign key is `NOT NULL`. That row needs the same OS identity and
a grant no service identity holds — and, crucially, **it is the one copy of the
provenance that lives outside the host the deployment is on**, so an actor who has
rewritten the approval record, the object store and the provenance record still
has nothing to register against. **The claim stops exactly there**: an actor who
holds the coordinator's `sudo` path as well inserts the row and every comparison
agrees, which is **R-5.0-15** and is recorded, not refused.

**The `freedomjournal` membership does not appear in either matrix, and revision
12 says why explicitly.** It is a filesystem group. `pg_hba`, `pg_ident` and
`SO_PEERCRED` decide a database principal from a **system user**, never from a
group, so the group that §4.3.2 records cannot move a cell in the authentication
table. That was true in revision 6 and is restated here because revision 11's
§4.3.2 denied the group existed at all, which is security-review finding
**P5.0-SR2**.

#### 4.3.6 Why not row-level security with per-role principals

It was compared (package plan §2.11) and rejected as the *primary* control, on
one argument: RLS binds a row to `current_user`, and `current_user` is a **role**,
not a process instance. It would stop `freedom_web` recording `freedom_bot`'s
observation, and it would not stop `freedom_bot` recording its own — which is the
case that matters, because the process being fenced is exactly the one whose
self-report is worthless. Removing self-attestation is a stronger control than
authenticating it, and it costs three fewer credentials to provision and rotate.
What survives from that option is its *conclusion about grants*: the runtime role
gets nothing on the authority plane, which §4.3.4 implements without any new
runtime role.

#### 4.3.7 Credential provisioning, rotation and revocation

The coordinator has **no credential to distribute.** Peer authentication means
PostgreSQL trusts the operating-system account, so the secret is host access,
which `docs/operations/break-glass-credential-custody.md` already governs — and
that document already states that *"anyone with host shell access and sudo"* is
the trust boundary, which is the same boundary this design uses rather than a new
one.

| Event | What actually changes | Who |
|---|---|---|
| **Provision** | create the OS user and group; create the role; apply the grants; add the two configuration lines; `SELECT pg_reload_conf()` — a **reload**, not a restart; run the §4.3.8 matrix before first use | root and the database superuser |
| **Rotate** | there is no secret, so rotation is *which OS account maps to the role*: add the new `pg_ident` line, reload, prove the new account authenticates and the old is refused, remove the old line, reload, re-prove. Both intermediate states are testable | Operations Owner, recorded in the change log |
| **Revoke** | any one of: remove the operator from the `sudoers` drop-in; `ALTER ROLE … NOLOGIN`; remove the `pg_ident` line and reload. **Each is fail-closed**: revocation can only prevent cutovers, never enable one, because activation requires an `INSERT` no other principal may make | Operations Owner |
| **Recover** | a broken mapping means no cutover can be activated. Restoring it is a root and superuser action on two configuration lines, and **no service process can perform it** — which is the property that makes the failure direction safe | Operations Owner |
| **Audit** | three independent records that must agree: `sudo`'s `log_output` and journald entry naming the invoking uid; PostgreSQL's connection log naming the authenticated role; the `audit_events` row naming the platform account. **PostgreSQL `log_connections` was not verified on this host** and the operations document must set and verify it rather than assume it | Operations Owner |

No environment file, `.env`, service unit or secret store gains an entry. That is
the main reason this option is recommended over per-process roles, which would add
three passwords to three environment files and three rotations to the operations
calendar.

#### 4.3.8 Required evidence, against PostgreSQL and the host, not a fake

Two bands. The first exists in revision 3 and is unchanged; the second is new and
is what P5.0-R4's re-review asked for.

**Band 1 — database authorization.**

- direct `INSERT`/`UPDATE`/`DELETE`/`TRUNCATE` attempts by `freedom_runtime_test`
  against all **six** tables, each refused;
- a direct `INSERT` into `migration_quiescence_evidence` **and into
  `sheet_writer_journal_generations`** by the runtime role, each refused for want
  of any privilege;
- `UPDATE`/`DELETE` by the schema owner against the **four** append-only tables,
  refused by the triggers;
- an activation attempted with evidence rows inserted by any principal other than
  the coordinator, which **cannot be constructed at all** and is recorded as
  *unconstructable* with the grant proof that makes it so; and
- `has_table_privilege` assertions after seeding hostile `GRANT … TO PUBLIC`
  statements, in the shape `tests/test_runtime_grants_live.py` already uses.

**Band 2 — host and authentication boundary. New in revision 4.**

| # | Evidence | Assertion |
|---|---|---|
| 1 | each runtime OS identity attempts a peer connection as the coordinator role | `discordbot`, `freedomweb`, `freedomsheet` and `foundry` each refused; the refusal is PostgreSQL's, and the message is captured |
| 2 | the dedicated identity connects over the intended Unix socket | accepted, and `SELECT current_user` returns the coordinator role |
| 3 | the dedicated identity attempts TCP | refused by `pg_hba`, **with and without** a password supplied, and against a second database |
| 4 | `sudo -l -U <identity>` for each service identity | lists nothing |
| 5 | an unauthorized `sudo` invocation of the wrapper | refused |
| 6 | each service identity attempts to write the root-owned deployment path | `EACCES` |
| 7 | `PYTHONPATH`, `PYTHONHOME` and `PGSERVICE` supplied across the `sudo` boundary | absent from the process's recorded environment and from its `sys.path` |
| 8 | a shadowing module planted in the invocation directory | not imported; `sys.path[0]` is not the cwd |
| 9 | **the positive invariant** — the effective `sys.path` recorded by `diagnostics` | **no entry on it is writable by `discordbot`, `freedomweb` or `freedomsheet`**, computed under each uid rather than reasoned about |
| 10 | a `pg_ident` rotation | the new account authenticates and the old is refused, in both intermediate states |
| **11** | **new in revision 5** — `sudo -l -U <identity>` for each service identity | lists **neither** `Cmnd_Alias`: not `FREEDOM_MIGRATION_AUTHORITY` and not `FREEDOM_JOURNAL_ADMIN` |
| **12** | **new in revision 5** — an unauthorized invocation of `freedom-journal-admin`, under each service identity | refused by `sudo`, and the attempt appears in `log_output` |

**Band 3 — the journal's storage, integrity and lifecycle. New in revision 5,
extended in revision 6, and again in revisions 7, 8, 9 and 10; unchanged in
count by revision 11**, and it is
the P5.0-R5 evidence. The full `TC-5.0-JNL` band — **fifty identifiers and
eighty-eight cases**, because `JNL-02`, `JNL-32`, `JNL-34` and `JNL-40` each carry
two and `JNL-46`, `JNL-47`, `JNL-48`, `JNL-49` and `JNL-50` carry five, six,
four, twelve and twelve — is
**package plan §2.13.8**, mapped one test per bullet of the R4 handoff's
falsification plan plus one per defect the R5, R6, R7, R8 and R9 handoffs name.
**Revision 11 adds no identifier and no case**, and the total is unchanged at
fifty and eighty-eight. Its corrections are to how an identity is **constructed**
— package plan §2.13.5c's `capsh(1)` procedure replacing `setpriv` recipes that
util-linux 2.39.3 rejects — and to **which identity serves as a positive
control** in `JNL-50` case 7 and `JNL-49` case 11, where **E6** replaces **E2** as
the isolating control. **No case changed its expected syscall, result or
`errno`**, none is schema-relevant, and there is accordingly no arithmetic to
show. **Revision 10 adds four cases and no identifier**, all four in `JNL-49` and
`JNL-50` and none of them schema-relevant: they are the owner-authorization
isolating controls and their positive counterparts, which run against the
filesystem and open no database connection. **Revision 9 added ten cases and no
identifier.** Four of its cases are
schema-relevant and are named here because a reviewer of this artifact should
expect them: **`JNL-36`** alters the **registered digests** and asserts that
`reject_history_mutation` refuses the `UPDATE` outright, that no other principal
can `INSERT` a competing row, and that a disagreeing row is refused at comparison;
**`JNL-41`** alters the **probe report** and asserts that a row *can* be inserted
carrying a well-formed but false `append_only_probe_digest` — **which is exactly
what §3.7.1 says the database cannot prevent** — and that both the writer and the
coordinator then refuse it; **`JNL-31`** asserts the construction order the
`seal_body_digest`, `genesis_record_digest` and `seal_digest` columns record; and
**`JNL-34b`, new in revision 7**, rewrites the seal body **and** record 0
consistently under `CAP_LINUX_IMMUTABLE`, asserts that the **writer completes V-W
without refusing** — the limit is asserted, not omitted — and asserts that the
**coordinator** then refuses it against these columns. That last case is the
evidence for §3.7's *"What this table uniquely can do"*, and it is the reason a
reviewer should not read the registered digests as merely redundant with the
seal. **`JNL-29`** additionally asserts that the sealed probe report contains
**all four stages** and that `append_only_probe_digest` is computed over exactly
those bytes (**R6-A**), and **`JNL-32a`/`JNL-32b`** assert the writer's two
startup branches — `+a` present, exactly one appended `startup` record; `+a`
absent, refusal at **W9** before **W17**, nothing appended, evidence byte-for-byte
unchanged (**R6-C**).

**Three of revision 8's five new identifiers are schema-relevant, and a reviewer
of this artifact should expect them too.** **`JNL-47`** — **six cases in revision
9**, four probe-stage failures with cleanup succeeding and **two** cleanup
failures with deterministic residue — asserts in **every** case that **no row is
inserted into `sheet_writer_journal_generations`**. That is the database-visible
half of package plan **C2**, and it is the half that is **unconditional**:
whichever of §2.13.2b's states the host is left in, the database is untouched.
*Revision 8 asserted "no residue" in the cleanup case as though that were
unconditional too, which contradicted `JNL-48(d)`; the database assertion was
never the problem and does not change* (**R7-A**, **R8-B**). **`JNL-49`** — **twelve cases since revision 10** — case 6 inserts a **wholly forged,
self-consistent generation** under an attacker holding
`A1 + A2 + A3 + A10 + A11 + A8` and
asserts that the partial unique index and the predecessor foreign key still admit
only one unsuperseded head and one successor per generation, so a forgery is
visible as a head with no `seal` record, no `.close` manifest and no archive;
**case 7 asserts the limit this design does not refuse** — the same attacker also
holding **`A9`** — which is residual **R-5.0-12** and not a refusal; and **case 3,
rewritten in revision 9, asserts that the coordinator does *not* refuse a
forged matching `/etc/machine-id`**, because this table's `host_machine_id`
carries the same value (**R8-D**, residual **R-5.0-13**). *Revision 8's case 3
asserted a C-d refusal with `J-16`; it is withdrawn.* **`JNL-50`** — **twelve cases
since revision 10** — executes the not-constructible cells under their real
identities and capability sets, including `freedomcoord` attempting
`UPDATE`/`DELETE` on this table, `freedomsheet` asserted to open **no database
connection at all**, and a **non-root process holding `CAP_LINUX_IMMUTABLE` *and
`CAP_FOWNER`*** clearing `+i` on an archived file and then receiving `EACCES` —
the executed proof that flag control confers no DAC (**R7-C**, **R8-C**).
**Corrected in revision 11**: this sentence still described that identity as
holding `CAP_LINUX_IMMUTABLE` *"and nothing else"*, which is revision 9's
non-constructible form — without the owner half the `FS_IOC_SETFLAGS` returns
`EPERM` and the open is never reached. The package plan corrected the case in
revision 10 as `JNL-49` case 12 under identity **E5**; this copy was not
corrected with it (**R9-A**, **R10-C**). What is otherwise schema-relevant is the band's five
activation cases:
activation attempted with **missing**, **stale**, **cross-generation**,
**corrupt** and **incomplete** journal evidence, each refused by the activation
trigger's conditions 4 and 5 (§3.4), each asserting the named refusal reason, and
each executed by direct statement against real PostgreSQL rather than through the
service.

**Band 4 — reviewed-source provenance and the canonical membership. New in
revision 12; this is remediation R11.** Its host half is package plan §2.12.5a
and §2.12.2, and only two things in it are schema evidence, both of them about
this artifact's own constraints.

**The `NOT NULL` foreign key must be proved to refuse, by direct statement, under
both writing principals.** `JNL-51` case (g) and `JNL-53` issue an `INSERT` into
`sheet_writer_journal_generations` naming a `source_commit`, `source_tree_id` and
`source_manifest_digest` for which no `approved_source_revisions` row exists —
first through `RegisterJournalGeneration`, where **`V-R` refuses with `J-28`
before any statement is issued**, and then as **direct SQL** under
`freedom_migration_coordinator` **and** under the schema owner, where the foreign
key refuses it. The second half is the one that matters: it is what makes the
control survive a coordinator whose code was altered, and it is the same proof
shape §3.7.1 requires for every claim that a constraint rather than a procedure
does the refusing. **A companion case asserts the composite foreign key**: a row
naming a valid approved revision but carrying different digests beside it is
refused, so `C-d` never compares the seal against values nothing checked.

**The append-only trigger must be proved on the seventh table.**
`UPDATE` and `DELETE` on `approved_source_revisions` are refused for
`freedom_migration_coordinator` **and for the schema owner**, by
`reject_history_mutation`, which extends §6.2's matrix from four append-only
tables to five and is asserted there rather than assumed from the trigger's
existence elsewhere.

**Everything else in Band 4 is host evidence and is not this artifact's**:
Algorithm **D**'s nine refusals, the Git-object-derived trusted manifest, the
closed two-region partition, the omission test, the syscall trace showing the
worktree is never read, and `JNL-52`'s eight `id`/`namei -l`/`open` cases. **None
of it has been run**, and **`freedomcoord`, `freedomsheet`, `freedomjournal` and
`fbprobe` do not exist on this host**, so `JNL-52` — which is the security
review's check **C-4** — is specified and unexecuted, exactly as Band 3 is.

**Band 2 needs real operating-system identities and a real `pg_hba` reload**,
which the disposable database alone does not supply. The attacking side can use
the existing service identities read-only; the coordinator side cannot be
simulated. It is **assumption A-5.0-4, unconfirmed**, and without it P5.0-R4
cannot be closed on evidence. That is stated here rather than discovered at
implementation time.

**Band 3 needs a root-owned durable directory hierarchy, a disposable probe arena
owned by the writer's identity, and a *verified* `chattr +a` exercised under that
identity**, plus — **new in revision 7** — **a transient `systemd-run` unit
startable as root at provisioning and a deployed `freedom-sheet-writer.service`
unit file to read hardening directives from**, so §2.13.2a stage 4 can run before
the probe report is built; plus — **new in revision 8** — **a second transient
directory `…/probe-ro` on the same mount, with the `S4-0` control executed in it
under the writer's uid outside any unit**; plus — **new in revision 9, corrected in revision 10 and corrected again in
revision 11** — **the eight
executable identities `E1 … E8` of package plan §2.13.5c**: a disposable uid
`fbprobe`; **`capsh(1)` present on the target host** (`libcap2-bin`; on this host
`/usr/sbin/capsh`, `root:root 0755`, no file capabilities) and able to build the
complete permitted/effective/inheritable/ambient/bounding masks `0x0`, `0x200`,
`0x206`, `0x208` and `0x20E`; a **launching bounding set that already contains**
every capability those masks need, since no tool can add to a bounding set; and
`/proc/self/status` plus `prctl(PR_GET_SECUREBITS)` readable inside each dropped
process, so every case asserts its identity **and its securebits** before it runs
— *revision 9 assumed `setpriv --ambient-caps=+linux_immutable` alone, which
builds no such set, because an ambient capability must also be permitted and
inheritable, and which in any case could not have produced the asserted result on
a **root-owned** inode; **revision 10 replaced it with
`setpriv --securebits=+keep_caps,…` recipes that util-linux 2.39.3 rejects and
that declared bounding sets they did not produce.** Both forms are withdrawn
rather than carried forward* — and a disposable
second host, or a disposable host whose `/etc/machine-id` may be rewritten, for
`JNL-40`'s forged-matching case; plus
fault injection for a `fsync` failure and — for one bullet — a supervised host
reboot. It is **assumption
A-5.0-5, unconfirmed**; revisions 7, 8 and 9 widen it, **revision 10 corrects
it and revision 11 corrects and widens it again. It has never been confirmed, and
package plan §8.1 H-6 — a non-mutating read of the tool contract on 2026-08-31 —
is not a confirmation of it.** **Revision 6
corrects what its absence costs**: without it `verify-capability` cannot produce a
passing probe report, so `init-generation` **refuses to create a generation at
all** — a host-side refusal by the privileged tool. Revision 5's *"no generation
can be registered at all, because `append_only_verified` is `CHECK`ed true"* is
**withdrawn with the column** (§3.7.1); the database records the consequence, it
does not cause it. **P5.0-R5 therefore cannot be closed on evidence without
A-5.0-5**, and that is stated here for the same reason.

---

## 5. Representation rules — what this package does and does not represent

| Rule (plan §7.7, §7.3.1, ADR 0005) | Application here |
|---|---|
| Currency in integer copper | **no money column exists in this package.** The control plane records who is authoritative, never an amount. The first integer-copper column is package 5.2's |
| Divisible resources in an integer smallest unit | same — none exists here |
| No binary floats for persisted quantities | vacuously satisfied. The only numeric columns are `epoch`, `control_plane_version` and — new in revision 5 — `generation_seq`, `predecessor_seq`, `journal_device`, `journal_inode` and `journal_last_sequence`, **all integers**. No size, duration or free-space figure is persisted anywhere: N5.0-21, N5.0-22 and N5.0-23 are contract numbers the writer and the tools read from configuration, never columns. Revision 2's `fence_protocol_version` and `in_flight_operations` are gone with the tables that held them |
| Discord snowflakes as `BIGINT` | none stored; attribution is by `platform_accounts.id` (ADR 0010 D1) |
| Optimistic concurrency on mutable aggregates | **there is no mutable table in this package at all**, and revision 5 preserves that: journal generations supersede by the successor's own row and never by `UPDATE`. The precondition is `previous_disposition_id`, or `predecessor_generation_id`, enforced by a unique constraint, so the check is atomic with the write and has no read-then-write window. Revision 2's one mutable table is withdrawn |
| No JSON, array, delimited text or generic key/value as operational authority | **satisfied, and it is the load-bearing claim of this artifact.** Every operational fact is a typed column with a `CHECK` or a foreign key. `observed_detail` is a bounded human-readable `VARCHAR` and is deliberately **not** operational authority: the trigger tests the row's existence, its `fence_method` and — new in revision 5 — its `journal_generation_id`, never its text. **The journal's own records are not in the database at all**, so nothing here parses a serialized structure to make a decision |
| Normalized records over Sheet-era serialized strings | no Sheet value is migrated by this package (§7) |
| Personal data minimisation | **no player-identifying column exists in this package.** Revision 1's only one was `shadow_comparisons.character_id`, which OD-55 moves to 5.1 and OD-56 governs there. `observed_detail` is `CHECK`ed not-blank and bounded, and the coordinator command is forbidden to write credential material or player data into it — asserted by a test over the recorded values, on the `audit_events` payload-classification precedent. **Revision 5's new columns are all digests, integers, a unit name, a machine id and a fixed-prefix path**: none can hold a name, a balance, a cell value or a credential, and `journal_path`'s `LIKE` constraint means it cannot even hold an arbitrary path |

---

## 6. Migration, upgrade, downgrade, backup, restore and retry

**One additive Alembic revision `0014`.** It creates **seven** tables — *six
through revision 11; `approved_source_revisions` is added in revision 12* — seeds
`migration_authority_transitions` (now including
`requires_external_writer_fence`) and `migration_units`, inserts one genesis
`legacy` revision **and its activated disposition** per unit, creates the
`control_plane_version` **and `sheet_writer_journal_generation_seq`** sequences,
installs the **five** append-only triggers, the activation trigger and the
evidence-recording trigger, creates the `freedom_migration_coordinator` role if
D5.0-11 approves it, and applies the grant changes.

**`approved_source_revisions` is created empty and is not seeded, for the same
reason `sheet_writer_journal_generations` is not.** An approval is a fact about a
human decision on a named immutable Git object; seeding one would be the
migration approving a revision, which is exactly the shape of defect
security-review finding **P5.0-SR1** identifies — a control whose trusted side
was manufactured by the thing it is supposed to constrain. Until the first
approval is recorded by a Platform Administrator, **no journal generation can be
registered at all**, because §3.7's foreign key is `NOT NULL`, and therefore no
fenced transition can be activated. **That is the correct starting state**, and
it is a stricter one than revision 11's: revision 11 started with a registrable
generation and no provenance requirement.

**`sheet_writer_journal_generations` is created empty and is not seeded.** A
generation is a fact about a file that exists on a host, so the migration must not
invent one: seeding a row would be exactly the *"a new journal that looks like a
valid empty history"* failure P5.0-R5 names, moved into the schema. Until the
first generation is registered by a human after `freedom-journal-admin
init-generation`, the `migration_journal_generation` health check fails and no
fenced transition can be activated. **That is the correct starting state** — every
unit is at `legacy`, no fenced transition is due, and the estate refuses rather
than assumes.

**The seed is derived, not typed by hand.** Unit rows come from
`data-migration-manifest.json`'s `profile_targets` plus the explicitly registered
behavior units. A test asserts the seeded set equals the manifest's set, so a
manifest change not reflected here fails the suite rather than silently leaving a
field ungoverned.

**Genesis is seeded as an activated disposition, not a bare revision.** If it
were not, every unit would start *pending* and the whole platform would have no
authority for anything — a fail-closed state, but a useless one. The seed writes
both rows, with `decided_by_platform_account_id` NULL, which is the one case §3.4
permits. Genesis is `legacy → legacy` and is not a fenced transition, so it needs
no evidence.

**Downgrade.** Drops the **seven** tables, the **two** sequences and the triggers,
and reverses the grants. It is genuinely reversible **only while every unit is
still at its genesis disposition**; once any unit has moved, a downgrade destroys
authority history that plan §7.6 requires to be append-only. **A registered
journal generation does not by itself block the downgrade** — no unit has moved —
and the on-disk journal, seal and archive survive it untouched, which is the
correct direction: the evidence outlives the schema that indexed it, and
re-registering a generation after a re-upgrade is a supported operator step. The migration therefore
refuses to downgrade when any unit has more than one disposition, and says so in
its own docstring rather than pretending to be reversible — the boundary
migration `0013` established (`_refuse_a_downgrade_that_cannot_be_undone`,
`migrations/versions/0013_effect_publication_recovery.py:341`) and the same
disposition dependency D-09 records. Rolling a *cutover* back is a new `→ legacy`
revision, never a schema downgrade.

**Required migration evidence.**

| Evidence | Shape |
|---|---|
| applies to an empty disposable database | `alembic upgrade head` from zero |
| applies to a database holding the previous revision's fixtures | upgrade over the current head with seeded Phase 1–3 data |
| `upgrade → downgrade → upgrade` round trip | at genesis state; and the refusal path once a unit has moved |
| restored-backup rerun | `infra/postgresql/backup-restore-drill.sh` against `freedom_test`, then the migration and the full suite again |
| idempotent rerun of the seed | reseeding an already-seeded database changes nothing and adds no duplicate unit, revision or disposition |
| source-to-target control totals | manifest `profile_targets` + registered behavior units **=** `migration_units` rows **=** genesis revisions **=** activated genesis dispositions, asserted as four equal counts. This is the only control total this package has, because it migrates no legacy data |
| **the generation table applies empty and stays empty** | after `upgrade head`, `SELECT count(*) FROM sheet_writer_journal_generations` is **0**, the `migration_journal_generation` health check **fails**, and an attempted activation of a fenced transition is **refused**. A migration that seeded a generation would recreate P5.0-R5 inside the schema, so the assertion is that it did not |

**Restore is a special case, and it is the one the operations document opens
with.** A restore can return the control plane to an earlier
`control_plane_version` — which means returning a unit to an earlier authority
while the estate believes otherwise. **Three** controls: quiescence evidence
restored from a dump is bound to its revision and is refused as stale by the
N5.0-16 age test, so no restored evidence can fence a later activation; **a
restore can also return the generation register to a state before a rotation, so
the operations procedure additionally requires the coordinator to compare the
restored head generation against the seal on disk and to run `archive-verify`,
refusing if they disagree** — the file survives a database restore, and that
asymmetry is a control rather than a problem; and the procedure requires
`python -m tools.migration_authority status` **before any service is started**,
comparing the restored control-plane version against the last one recorded in the
change log. This is risk R-5.0-3, extended in revision 5.

**Retry behaviour.** Each of the **five** commands is one transaction: effect,
receipt and audit commit together or not at all. A retry with the same
idempotency key returns the stored receipt without writing a second row. A retry
with a *new* key against an already-superseded predecessor is refused by
`uq_…_previous_disposition`, which is the stale-apply case. A re-recorded
*observation* is refused by `(revision_id, fenced_writer, fence_method)` UNIQUE
and treated as success by the coordinator, because the observation it makes is
already recorded. A re-registered *generation* is refused by
`uq_…_predecessor` — the chain admits one successor — and by
`uq_…_device_inode`, so registering the same journal twice is impossible even
under a fresh idempotency key.

---

## 7. Failure modes this design must survive, and how

Every row the handoff's evidence plan names, answered rather than asserted. The
option comparison behind these answers is package plan §2.10.

| Case | What happens | Residual |
|---|---|---|
| **A process paused after its final admission check and resumed after activation** | **This is the counterexample that defeated revision 2, and it is now defeated in both directions.** *Database path:* the resumed transaction's authority-fence trigger reads the current disposition and refuses; a pause changes nothing because the check is inside the write. *Sheet path:* there is no resumption — a `SIGSTOP`ped process is killed by the `SIGKILL` escalation `systemctl stop` performs, and a process that has been killed cannot resume. Even a hypothetical survivor is refused by Google, because its write access was revoked before termination | none for the database path. For the Sheet path, only the `host_scan_clear` staleness window in §2.4, which the revoked ACL covers |
| **An out-of-systemd duplicate legacy writer** | Not covered by the unit stop or the cgroup check, and this is stated rather than hidden: those observe what systemd started. It is covered by `host_scan_clear`, which scans every process on the host for the writer entry point, and — independently and continuously — by the revoked Drive permission, which refuses a duplicate's writes at Google regardless of how it was started | a duplicate started *after* the scan. It writes nothing, because its access is revoked. **R-5.0-5** |
| **A request already at the irreversible external-call boundary** | **Rewritten in revision 4. The revision-3 answer in this row was wrong and is withdrawn**: it asserted that a call dispatched and accepted before revocation *"lands before the fence … and is captured by the final import"*, and nothing establishes that. A `values.batchUpdate` already dispatched cannot be recalled, and no published API fact says when Google applies it (§2.2B). What the design does instead: the writer is **drained first**, so in the normal case the response arrives and the request is *known* complete; the journal makes anything outstanding **enumerable**; a non-empty unresolved set **refuses the activation** (N5.0-20); the ACL bounds anything dispatched afterwards; and two post-import re-reads **detect** a late apply | **The residual, R-5.0-8.** A request accepted before the fence whose response was lost and which Google applies after the final import is not prevented and cannot be proved absent. It cannot reach PostgreSQL, and it is detected within the verification window. **Accepted or rejected by D5.0-9 / OD-62**, not mitigated away here |
| **One runtime process attempting to update, release or fence another process's lease** | **Unconstructable: there is no lease table.** The evidence is recorded by a principal no service can authenticate as, and no service holds any privilege on the evidence table | none |
| **One runtime process attempting to acknowledge for another process** | **Unconstructable: there is no acknowledgement table**, and no process attests anything about itself either | none |
| **Direct SQL under every proposed database principal** | §4.3's evidence list: the runtime role refused on all **six** tables, the schema owner refused on the **four** append-only tables by trigger, the coordinator refused `UPDATE`/`DELETE`/`TRUNCATE` everywhere, and `freedom-sheet-writer` asserted to hold no credential at all | none |
| **Activation with forged, missing, stale or cross-instance proof** | *Forged:* unconstructable — no principal but the coordinator may insert evidence, and no service **OS identity** can authenticate as the coordinator (§4.3.3, §4.3.5). *Missing:* the trigger refuses when any of the **five** required methods has no row. *Stale:* the trigger refuses evidence older than N5.0-16 or predating `revision.created_at`. *Cross-revision:* evidence is bound to `revision_id` by foreign key | none in the database. The residuals are operational and are §2.4's two |
| **A compromised writer omits a dispatch-journal entry** | The unresolved set looks empty when it is not, so `dispatch_journal_clear` is recorded when it should not be. **The other four fence methods are unaffected**, because the writer authors none of them, and the activation still requires all five | **Stated, not mitigated. R-5.0-10.** The journal is a completeness aid and §2.4 and §2.9 say so where a reader meets it. A writer whose *dispatch path* was replaced is outside what any record it authors can bound; what bounds it is that the process is dead and its access is revoked |
| **The journal is lost, replaced, reset, truncated or corrupted, and an unknown history reads as an empty unresolved set** | **This is P5.0-R5, and revision 4's answer to it was "the file is on `/run` and has `chattr +a`", which was wrong twice.** Revision 5: the file is on **durable ext4** in a **root-owned directory the writer cannot write**, so it cannot be unlinked, renamed or replaced; the attribute is **probed, not inferred**; a `chattr +i` **seal** names the genesis record, so an empty file is *invalid* rather than *clean*; a **hash chain and a sequence** make truncation, splicing and rewriting detectable; and the **registered generation** lets the activation trigger refuse evidence about a journal that has since been rotated or restored. **Package plan §2.13.6 enumerates twenty-one conditions and no row of it resolves to "continue"** | **none for the enumerated conditions**, which all refuse on both the writer's side and the coordinator's. The residual that remains is **R-5.0-10**, above, and it is a different failure — a writer that never journalled, not a journal that was lost |
| **A journal generation is rotated, restored or rolled back after clear evidence was recorded** | The activation trigger's **condition 5** (§3.4) refuses: the evidence's `journal_generation_id` must be the current chain head, and no generation may have been registered since the evidence was observed. The chain's `uq_…_predecessor` and its partial unique index make "current head" a single unambiguous row rather than a query somebody has to write correctly | none in the database. Operationally, the coordinator re-observes immediately before activating, which is the same control §2.4's first residual already relies on |
| **The journal filesystem fills, or an `fsync` fails** | The writer refuses to dispatch below N5.0-21 and for the life of the process after a failed `fsync` (package plan §2.13.6 **J-13**, **J-14**). **It never dispatches a request it could not durably record first** | **R-5.0-11:** Sheet mutations are unavailable until an operator acts. A bounded outage in exchange for never making an unrecorded external write — the same trade §7's *failed restart* row already makes |
| **The host boundary drifts after provisioning** | A group membership, a `sudoers` rule, a `pg_hba` ordering, a `pg_ident` line or a file mode changes outside this repository, and the §4.3.5 matrix silently stops holding | **R-5.0-9.** The §4.3.8 Band 2 matrix is re-run after any PostgreSQL configuration change, any `sudoers` change and any deployment, and `diagnostics` re-checks the `sys.path` invariant on every invocation. **Detected on re-run, not prevented** |
| **All three services** | `freedom-web` and `freedom-worker` write PostgreSQL and are fenced inside their transactions. `freedom-bot` writes both; its database path is fenced the same way and its Sheet path moves to `freedom-sheet-writer`. A service that is not running writes nothing | none. A role that is down is an outage, not a split |
| **Failed shutdown of the writer** | `systemctl stop` escalates to `SIGKILL`; if the unit still reports active or the cgroup is non-empty, the coordinator **records no evidence and refuses to proceed**. The activation trigger then refuses too, because the required methods have no rows | a unit stuck in `deactivating` with an unkillable process — a kernel-level `D` state. The coordinator refuses, the cutover does not happen, and that is the correct outcome |
| **Failed restart after activation** | The writer stays down: mutations of every unit it served are unavailable until it starts. No dual write is possible, because the new authority is PostgreSQL and the old writer does not exist | a bounded outage, which is the intended failure direction |
| **Rollback** | The same authorize → fence → replay → activate → restart protocol, in reverse. No emergency path skips the fence. The replay writes the Sheet under the *coordinator's* access, not the bot's | the replay's duration is the unit's mutation outage. Bounded by N5.0-4's divergence |
| **Operator death mid-cutover** | The revision stays pending; nothing has changed authority. At `activation_deadline_at` it can only be abandoned. The writer is down and its access revoked, so the failure is an outage with no integrity consequence, and `/healthz` reports both the pending revision and the missing writer | the outage lasts until a human notices. Monitoring is the control, and it is why `migration_authority_pending` is one of the three checks |
| **Supervised recovery after a restore** | `status` before any service starts (§6); restored evidence is stale by construction and fences nothing; the operator reconciles the restored control-plane version against the change log | a restore to a point before a cutover, undetected. **R-5.0-3** |
| **The database is unreachable** | *Database writes* fail, as they do today. *Sheet writes* are **unaffected** — this is the change from revision 2, and it is worth stating plainly: with the lease withdrawn, the Freedom bot's legacy mutation path takes **no** availability dependency on PostgreSQL at all. The startup authority read is the only database interaction it gains, and a process that cannot perform it refuses to start rather than starting under an unknown authority | a bot that cannot reach PostgreSQL at start does not start. That is a startup dependency, not a runtime one, and it is smaller than revision 2's |
| **Clock disagreement** | Every instant that matters — `created_at`, `observed_at`, `effective_at`, `activation_deadline_at`, the trigger's comparisons — is the *database's* `now()`. No process measures elapsed time for any fencing decision, so there is no monotonic-clock model to get wrong and nothing to inject in a test | none. Revision 2's whole clock-injection evidence band is withdrawn as unnecessary |

---

## 8. What this artifact deliberately does not design

- **The ledger table** — package 5.2, under its own schema artifact (OD-58).
- **Comparison telemetry** — package 5.1, under its own schema artifact (OD-55).
  Package 5.0 writes the common contract as prose (package plan §11).
- **`wallet_balances`, `resource_transactions`, and any character-state table** —
  their owning packages, per the migration register.
- **The account vocabulary** — package 5.2. Nothing here names an account.
- **Any Sheet-era field** — none is migrated, and no column here can hold one.
- **Any per-unit import, comparison or replay implementation** — each migrating
  package owns its own, against the §2.6 contract.
- **The authority-fence trigger on any aggregate table** — package 5.0 supplies
  the trigger function and installs it on nothing but its own tables and one
  synthetic test unit. Each owning package installs it on the tables it makes
  authoritative, in its own migration, under its own review.
- **A generic migration framework** — no migration job table, no step/stage
  machinery, no reconciliation store, no preview store.
- **A schedule, a job queue or a timer** — package 5.3 owns the Living Cost
  schedule tables, and `reconciliation_jobs` is not extended here.
- **A web route or a Discord command** — the only human surface is the host-local
  coordinator command (OD-59).
- **The `freedom-sheet-writer` unit's internals** — its systemd unit file, its OS
  identity, its hardening directives, its IPC boundary, its drain behaviour, its
  request timeout and its failure semantics are package plan §2.10, §2.12, §2.13.3,
  WP-4b and D5.0-12, and they are not schema. This artifact records only what the
  evidence table observes about it.
- **The dispatch journal's storage, record format, integrity, failure states,
  rotation, archival, retention and disposal** — package plan **§2.13** in full.
  The per-dispatch records remain deliberately **a host file and not a table**:
  putting them in PostgreSQL would give the legacy mutation path a database
  dependency that withdrawing the lease removed, and revision 5 does not give that
  back. **What revision 5 does add here is the journal's *identity*** — §3.7 —
  because the activation trigger must be able to refuse evidence about a journal
  that has been rotated, reset or replaced, and it cannot refuse what the database
  has never heard of. **That distinction is the whole of the schema's involvement
  in P5.0-R5**: the generation is registered once per journal by a human; the
  records are never written to the database at all.
- **A barrier for I-SHEET-COMPLETE.** Package plan §2.10.2 concludes none exists
  in the published Google APIs, so this artifact designs none. §2.8 states the
  boundary of what is claimed instead. **A schema cannot supply a property an
  external service does not expose**, and a table that looked as though it did
  would be worse than none.

---

## 9. Traceability

| Design element | Requirement | Planned evidence |
|---|---|---|
| Append-only revision, disposition, evidence **and journal-generation** chains | plan §7.6, `.agents/AGENTS.md` correction-not-erasure | runtime-role, coordinator and schema-owner `UPDATE`/`DELETE`/`TRUNCATE` refusals against PostgreSQL, on all **four** append-only tables |
| One current authority per unit | P5.0-R1 | `(unit_id, epoch)` UNIQUE exercised by a concurrent double-activation test; and the §2.5 read proved to be the only path by a repository-level test |
| **A pending revision is never authority** | P5.0-R2 (closed; regression-guarded) | a revision authorized with `effective_at` in the future, then every authority read asserted to return the predecessor; and an activation attempt before `effective_at` refused by the trigger |
| **A stale database write is refused inside its own transaction** | P5.0-R1 | a transaction opened while a unit is at `cutover`, held past an activation of `cutover → legacy`, then committed — refused by the authority-fence trigger. Run against PostgreSQL with two connections and a barrier, not mocked |
| **Termination fences a paused writer** | P5.0-R1, handoff evidence item 1 | a test-harness writer process `SIGSTOP`ped mid-operation, then stopped through its unit; the cgroup asserted empty; `SIGCONT` proved impossible because the process is gone; the coordinator's evidence rows asserted present |
| **An out-of-systemd duplicate is detected and cannot write** | handoff evidence item 2 | a second writer started outside systemd; `host_scan_clear` refuses; and, separately, a revoked-access simulation asserts its write is refused at the boundary |
| **A request at the irreversible boundary** | handoff evidence item 3 | **Rewritten in revision 4**, because the revision-3 test asserted a property §2.2B says cannot be established. Four assertions replace it: a journal entry present after a `SIGKILL` between the `fsync` and the dispatch; a drained writer completing an outstanding call and recording its outcome; a killed writer leaving an **unresolved** entry, the coordinator refusing `dispatch_journal_clear`, and the activation refused; and a call dispatched after revocation refused at the API boundary. **No test asserts that a dispatched call has completed** |
| **A late apply is detected** | §2.2B item 6, R-5.0-8 | the fenced ranges mutated out-of-band after the final import in a harness; both re-reads report the divergence; a `→ legacy` replay refused until the report exists |
| **The dispatch journal is durable, protected and tamper-evident** | **P5.0-R5 items 1, 2 and 4** | package plan §2.13.8's `TC-5.0-JNL-01`, `04 … 13`, `16 … 18`: the journal path proved to be on a non-`tmpfs`, block-backed filesystem; `+a` and the **fifteen** manipulation attempts each failing with the expected `errno` under package-plan identity **E1**, including the two flag rows revision 10 adds — `chattr -i` on the seal and on an archived file; each of the nine named bad states refusing on both the writer's and the coordinator's side; disk-full, `fsync` failure and outcome-append failure preventing a dispatch or leaving an unresolved entry, **with the Sheets client asserted never called** |
| **A new or reset journal is never a valid empty history** | **P5.0-R5 item 3** | `JNL-02a/b`, `JNL-03`, `JNL-19`: an unresolved entry surviving a kill and — supervised — a reboot; a restart appending rather than creating; `init-generation` refused while a predecessor is unsealed; the successor's `predecessor_close_digest` required by `ck_…_predecessor_triple`; a second chain head refused by the partial unique index; **and the migration asserted to seed no generation at all** (§6) |
| **Activation refuses stale, cross-generation and unregistered journal evidence** | **P5.0-R5 items 3 and 4** | `JNL-21`, `JNL-22 … 26`: a generation registered after the evidence → refused by condition 5's `created_at` clause; evidence naming a superseded generation → refused by its head clause; missing, corrupt and incomplete evidence → refused by condition 4. All by direct statement against real PostgreSQL |
| **The journal's privileged lifecycle cannot be performed by the writer** | **P5.0-R5 item 5** | `JNL-13` and `JNL-19`: `seal`, `rotate`, `clear` and `dispose` all require `root` through a `sudoers` alias the writer identity does not hold; the archive is `chattr +i` and unreadable to `freedomsheet`; `dispose` refused without N5.0-23, plan §15.1's gate, a Data Owner reference and a passing `archive-verify` |
| **The generation construction is acyclic and its digests are derivable** | **P5.0-R5, R5-A** | package plan §2.13.5a's Algorithm C and `JNL-31`: an independent implementation re-derives the genesis record from the seal body alone, byte for byte, and the seal body is asserted to contain none of `genesis_record_digest`, `journal_device`, `journal_inode` or `seal_digest`. The registered `seal_body_digest`, `genesis_record_digest` and `seal_digest` columns (§3.7) are what the test compares against |
| **The writer can perform every check it is required to perform** | **P5.0-R5, R5-B** | package plan §2.13.5b's Algorithm **V-W** and `JNL-33`: the whole eighteen-step startup validation — **unchanged by revision 8**, which renumbers Algorithm C and not V-W — completes using only the read the `freedomjournal` group grants, and every write attempt against the seal, the archive and the journal directory is refused with its expected `errno` |
| **Every field of the seal a reader trusts is a field the writer authenticates** | **P5.0-R5, R6-B** | package plan §2.13.5b's binding table and `JNL-42 … 45`: the binding section holds exactly `genesis_record_digest`, `journal_device` and `journal_inode`, and each is altered **independently** and refused at a named step — **W5**, **W7**, **W7**; a `sealed_at` field planted in the binding is refused at **W3** because the binding's length is fixed by a `binding_format_version` carried in the chain-authenticated body. **The same planted seal is asserted to have passed revision 6's V-W**, which is the regression the case exists to prevent |
| **The one falsification the writer cannot refuse is stated, not omitted** | **P5.0-R5, R6-B**, §3.7 | `JNL-34a` and `JNL-34b`: an altered seal body alone is refused by the writer at **W13**, with no database reachable; the seal body **and** record 0 rewritten consistently under **`A1 + A2 + A3 + A10 + A11`** — the `CAP_LINUX_IMMUTABLE` half of `FS_IOC_SETFLAGS`, its owner-or-`CAP_FOWNER` half over both the `freedomsheet`-owned journal and the root-owned seal, and DAC on the journal file and on `…/journal` and its seal, which revision 9 separated for flag control and DAC and **revision 10 completes with the owner authorization** — is asserted **not** to be refused by V-W, and to be refused by the coordinator at **C-b/C-d** against `sheet_writer_journal_generations`. This is the only row in this table whose evidence is a **negative** about the writer, and it is here because revision 6 claimed the positive |
| **The capability probe's refusals are attributable, and startup destroys nothing** | **P5.0-R5, R5-C; corrected by R6-C** | package plan §2.13.2a and `JNL-27 … 30`: the control stage must pass before any refusal is interpreted, and `EACCES`, `EROFS`, `EPERM` and `ENOTTY` are each produced deliberately and classified. Startup is proved by **two branches with opposite expectations**: **`JNL-32a`** — with `+a` **present**, a start that reaches **W18** performs no destructive operation against the journal, seal or archive and appends **exactly one** `startup` record; **`JNL-32b`** — with `+a` **absent**, the start refuses at **W9** with `SW-J06` **before W17**, opens the journal for writing not at all, appends **nothing**, and leaves the journal, seal and archive **byte-for-byte unchanged**. *Revision 6 asserted a single trace that left the file unchanged "except for the startup record" even with `+a` absent, which W9 makes unreachable* |
| **No digest is credited with covering bytes it does not contain** | **P5.0-R5, R6-A**, §3.7 | `JNL-29`: the probe report `verify-capability` returns is asserted to contain **all four stages** — `C-1 … C-6`, `P-1 … P-9`, `M-1 … M-2`, `S4-0 … S4-3` — before any generation is created, and `append_only_probe_digest` is asserted to be computed over exactly those bytes. Stage 4's transient unit is asserted to carry the deployed unit's directives with the single recorded `ReadWritePaths=` substitution, and a directive-set mismatch is asserted to yield **`inconclusive`** rather than a pass |
| **The generation construction can be executed in the order it states, and every external input is validated against a source that is not itself** | **P5.0-R5, R7-A, R8-A**, §3.7 | package plan §2.13.5a's Algorithm **C0 … C13**, its value table with an **I-2/I-3/I-5 class per row**, §2.13.2c's `deployment_manifest_digest()`, and `JNL-46`'s **five** cases: an independent harness walks the algorithm in order and asserts invariants **I-1 … I-5** — **C0 reading no probe result**, **C1 the only creation point of the report**, and the digest function returning identical bytes at its three call sites — and four cases refuse a **malformed** supplied digest, a **wrong** supplied digest, a **deployment changed between C0 and the probe** and a **report whose field differs from the validated input**, each before **C5** and each leaving **no row in `sheet_writer_journal_generations`**. *Revision 7's C0 required a probe report C1 had not yet built; revision 8 consumed the supplied digest at C1 and compared it at C2 against the probe's copy of that same string* |
| **One injected failure leaves one state, and the database is untouched in all of them** | **P5.0-R5, R8-B**, §3.7 | package plan §2.13.2b's three-state machine and `JNL-47`'s **six** cases — four probe-stage failures with cleanup succeeding, and **two** cleanup failures with deterministic residue. Every case asserts **no row in `sheet_writer_journal_generations`**, which is unconditional; the residue assertion differs by state, which is the correction. The cleanup cases additionally assert the exit code, the residue reported by absolute path, the **next run refusing at C0 without cleaning it**, and the operator recovery that clears it. *Revision 8's `JNL-47` asserted no residue after a cleanup failure while `JNL-48(d)` required it to remain* |
| **A forged matching host identity is recorded as a residual, not as a refusal** | **P5.0-R5, R8-D**, §3.7, §3.7.1 | package plan **F-7**, `JNL-40`'s **two** cases and `JNL-49` case 3: with `/etc/machine-id` left alone, the writer refuses at **W10** with `SW-J23` and the coordinator at **C-d** with `J-16`; with it **rewritten to the recorded value** and the device and inode preserved, **W10 is asserted to pass and C-d is asserted not to refuse on `host_machine_id`**, because this table stores a **copy** of that value rather than an attestation of it. **No case may assert a C-d refusal without naming the field whose inherent mismatch the threat proves.** The outcome is residual **R-5.0-13**; the column that would change it is **OD-66 option A-2**, not adopted |
| **Every negative capability case has a positive control on its exact target** | **P5.0-R5, R7-B** | package plan §2.13.2a and `JNL-48`: Stage 1's six control cases for Stage 2, and **`S4-0`** for **`S4-2`** — open, append, `fsync`, `rename` and `unlink` proved permitted by DAC on the exact `…/probe-ro/s4-2.target` under the writer's uid **outside any unit**, before any `EROFS` is interpreted. The four outcomes are produced and distinguished: positive DAC success outside the sandbox, `EACCES` from DAC (**`inconclusive`**), `EROFS` from the systemd read-only bind (**pass**), and cleanup failure or residue (non-zero exit, and `init-generation` refusing at **C0**) |
| **The threat model states the authorities an attacker must hold, separates flag control from discretionary access, and names every kernel prerequisite** | **P5.0-R5, R7-C, R8-C, R9-A, R9-B, R9-C**, §3.7, §3.7.1 | package plan §2.13.5c's **eleven-authority** register — `A1` the `CAP_LINUX_IMMUTABLE` half of `FS_IOC_SETFLAGS`, **`A10`** and **`A11`** its owner-or-`CAP_FOWNER` half over the `freedomsheet`-owned journal and the root-owned seal and archive, and `A2 … A9` the discretionary, host, coordinator and database rows — its **holder table**, its **executable-identity table** `E1 … E8` with complete permitted/effective/inheritable/ambient/bounding sets, and `JNL-49`/`JNL-50` at **twelve cases each**: **thirteen** falsification rows, each naming its minimum **combination**, whether that combination also reaches the detector, the refusing actor, the exact step and code, and the residual when it reaches both; one case per feasible combination, including the combined-authority residuals; and one executed assertion per **not-constructible** cell, with the control that makes it so. **Every new case is executed under an identity and capability set that really holds only what the row claims** — including identity **E5**, `CAP_LINUX_IMMUTABLE` **and `CAP_FOWNER`** in `freedomcoord`, which clears `+i` on an archived file and then receives `EACCES` on the open, which is the executed proof that flag control confers no DAC. **Corrected in revision 11**: this cell previously described that identity as *"`CAP_LINUX_IMMUTABLE`-only"*, which is revision 9's non-constructible form — a `CAP_LINUX_IMMUTABLE`-only non-root process receives `EPERM` from the ioctl and never reaches the open. The package plan corrected the case in revision 10; **this sentence was not corrected with it, and is corrected here**. The schema half is unchanged in substance and relabelled: **`A9`, PostgreSQL mutation authority, is held by no principal here** — `reject_history_mutation` and the revoked grants — and **`A1 + A2 + A3 + A10 + A11` plus a PostgreSQL superuser (`A9`) is a residual this design does not refuse** (**R-5.0-12**) — **also corrected in revision 11**, the set having been widened by R9-A and this copy of it left behind. *Revision 8's register credited `CAP_LINUX_IMMUTABLE` alone with archive and journal writes* |
| **Every kernel prerequisite is named, and every negative capability case is isolated with a positive control** | **P5.0-R5, R9-A, R9-C**, §3.7, §3.7.1 | package plan §2.13.5c's kernel-requirements table, stated **before** the register that encodes it, and `JNL-50` cases 3, 6 and 7 with their positive controls: identity **E4** — `CAP_LINUX_IMMUTABLE`, `CAP_DAC_OVERRIDE` and `CAP_DAC_READ_SEARCH`, **no `CAP_FOWNER`** — **opens** the root-owned archived file successfully and is asserted to receive **`EPERM`** from `FS_IOC_SETFLAGS`, while **E6**, differing only by `CAP_FOWNER`, issues the identical call and **succeeds**; and **E1** is asserted to receive `EPERM` clearing `FS_APPEND_FL` on its **own** inode, where the owner half is satisfied by ownership, with **E2** as its control — the two differing by `CAP_LINUX_IMMUTABLE` and nothing else. **Corrected in revision 11 (R10-C):** case 7's isolating control is **E6**, not E2 — E6 differs from E4 by `CAP_FOWNER` alone, where E2 differs in uid, groups and two capabilities — and E2 is retained as a **corroborating** control demonstrating the ownership route to the same check. `JNL-50` case 4 gains the second control form the package plan defines: hold the identity fixed and vary the **inode's owner**. Every case asserts `Uid`, `Gid`, `Groups`, `CapPrm`, `CapEff`, `CapInh`, `CapAmb` and `CapBnd` from `/proc/self/status`, **and its securebits from `prctl(PR_GET_SECUREBITS)`**, **before** the operation under test, and an unasserted identity yields **`inconclusive`**. **Nothing in this row is schema evidence** — it is named here because §3.7's *What this table uniquely can do* and §3.7.1's seal-integrity row both consume the corrected combinations, and a reviewer of this artifact should be able to check what they now rest on. **All of it depends on package-plan assumption A-5.0-5, which is unconfirmed** |
| **Every executable identity is constructible by a recipe whose result is derivable from the named tool's documentation** | **P5.0-R5, R10-A, R10-B**, §4.3.8 | package plan §2.13.5c's **seven-step `capsh(1)` construction** and its **mask-versus-recipe comparison**: each of `E1 … E8` states exact effective UID, GID, supplementary-group list, `CapPrm`, `CapEff`, `CapInh`, `CapAmb`, `CapBnd` **and securebits**, and each declared value is derived option by option from a complete invocation. **No tool is asked to add a capability to a bounding set** — `capsh` has no such option — and the launching process's bounding set is asserted to already hold every capability required, an absence yielding **`inconclusive`**. *Revision 10's `setpriv --securebits=+keep_caps,…` recipes are withdrawn: util-linux 2.39.3 rejects that securebit, `--bounding-set=+…` requests an addition the kernel forbids, E8 dropped no bounding set and E7 stated no inheritable or ambient mask.* **Nothing in this row is schema evidence**, and **none of it has been run**: it depends on package-plan assumption **A-5.0-5**, which is unconfirmed |
| **No database constraint is credited with proving a host fact** | **P5.0-R5, R5-D**, §3.7.1 | `JNL-41` and the §3.7.1 division: a row **can** be inserted carrying a well-formed but false `append_only_probe_digest`, and the writer (**W4**) and the coordinator (**C-d**) both refuse it against the seal. The withdrawn `CHECK (append_only_verified)` is asserted **absent** from migration `0014` |
| **What completeness is and is not trusted for** | **P5.0-R5 item 6**, §2.9 | not a test but a stated boundary, and the thing tests must not contradict: no test asserts the journal is complete against a writer whose dispatch path was replaced, and **the review should reject any evidence artifact that claims it is** |
| **Cross-instance proof forgery is unconstructable** | P5.0-R4, handoff evidence items 4 and 5 | `freedom_runtime_test` attempting `INSERT` on `migration_quiescence_evidence` — refused for want of privilege — plus a grant assertion proving no application role holds any privilege on it |
| **Direct SQL under every proposed principal** | P5.0-R4, handoff evidence item 6 | the §4.3 matrix, each cell exercised against PostgreSQL |
| **Activation with forged, missing, stale and cross-revision proof** | P5.0-R4, handoff evidence item 7 | four trigger-refusal tests, each asserting the named refusal reason |
| **Failed shutdown, failed restart and rollback** | handoff evidence item 8 | a unit stop that leaves the cgroup non-empty → coordinator refuses and records nothing → activation refused; a restart that fails → outage asserted, no authority change; a full `cutover → legacy` rehearsal |
| **The fence prevents the write, rather than noticing it** | handoff evidence item 9 | **Met for the database path** by the held-transaction refusal above — the write never commits. **Not met for the Sheet path**, and revision 4 records that rather than substituting a weaker test: what is proved there is the absence of a process, a refusal at the API boundary after revocation, a refused activation while the unresolved set is non-empty, and a detected divergence. §2.8 states the boundary |
| **No service OS identity can authenticate as the coordinator** | P5.0-R4, R3-B | §4.3.8 Band 2: peer attempts under `discordbot`, `freedomweb`, `freedomsheet` and `foundry`, each refused by PostgreSQL; the dedicated identity accepted on the socket and refused over TCP with and without a password. **Requires A-5.0-4** |
| **No service OS identity can change the code the coordinator runs** | P5.0-R4, R3-B | §4.3.8 Band 2 items 6–9: `EACCES` writing the root-owned deployment path under each service identity; `PYTHONPATH` stripped across the `sudo` boundary; a planted shadowing module not imported; and the positive invariant — **no `sys.path` entry writable by any service identity** |
| **The OS-to-database mapping can be rotated and revoked** | R3-B, §4.3.7 | a `pg_ident` rotation exercised in both intermediate states; `ALTER ROLE … NOLOGIN` asserted to refuse activation and never to permit one |
| Stale or concurrent authorization refused | plan §13.2 *stale optimistic version* | two authorizations against one disposition; one commits, one is refused by `uq_…_previous_disposition` |
| Illegal transition refused | the §2.1 matrix | `legacy → database`, `shadow → database` and `database → shadow` inserts refused by the transition FK, against PostgreSQL |
| A fenced transition cannot activate unfenced | §3.2, §3.4 | `shadow → cutover` activated with four of five evidence methods → refused, once for each omitted method; with all five **and a current registered generation** → succeeds; with all five but a **superseded** generation → refused by condition 5; `legacy → shadow` with none → succeeds, because its reference row requires no fence |
| No application process can register or supersede a journal generation | §3.7, §4.3.4 | `freedom_runtime_test` `INSERT` into `sheet_writer_journal_generations` refused for want of privilege; `has_table_privilege` asserting no application role holds anything on it; and the writer asserted to hold **no database credential at all** |
| No backdating; deadline honoured | plan §12's schedule-revision rule | `effective_at < created_at` refused; activation after `activation_deadline_at` refused; abandonment then permitted |
| Bounded verification window | handover *"bounded verification-window template"* | a `cutover` revision without `verification_until` refused; a `database` revision *with* one refused |
| Abandonment leaves authority unchanged | §3.4 | abandon a pending `shadow` revision; assert the unit still reads `legacy`; assert a new revision may then be authorized |
| Effect + receipt + audit are one transaction | handover, plan §13.3 | injected failures at each of the three writes, for each of the **five** commands; no partial effect, no false success |
| Retry returns the original receipt | plan §13.2 *duplicate Discord interaction* | same key, same content, three attempts, one revision |
| Conflicting key reuse refuses | Phase 4 contract | same key, different content → `idempotency_key_conflict` |
| No application process can change authority or forge a fence | §4.3 | `freedom_runtime_test` `INSERT` into revisions, dispositions and evidence, all refused |
| Grants are what the template says | finding O-1 | `has_table_privilege` after hostile `GRANT … TO PUBLIC` |
| Seed equals the manifest | plan §15.1 control totals | four equal counts |
| `observed_detail` carries no secret or player data | §5, `audit_events` precedent | a test over every value the coordinator command can write, asserting the allowlist |
| **A deployment carrying authority is bound to an immutable reviewed Git object, and omitting the binding refuses** | **P5.0-SR1**, §3.7, §3.8 | This artifact's half is **structural and is the whole of the "prevents activation" requirement**: `sheet_writer_journal_generations.approved_source_revision_id` is **`NOT NULL`** with a `RESTRICT` foreign key to §3.8, a composite foreign key ties the generation's three recorded provenance values to the approved row, and `reject_history_mutation` is installed on §3.8 — so **a generation whose reviewed source no review approved cannot be inserted by any principal including the schema owner**, and §3.4's activation trigger requires a registered generation. Proved by direct statement under both writing principals in `JNL-51` case (g) and `JNL-53`, not through the service. The host half — the approved-revision record, the `0700 root:root` bare Git object store addressed by object id with **no ref resolved anywhere**, the trusted manifest recomputed from Git object bytes, the closed two-region partition, Algorithm **D**'s nine refusals, the `PVR` record whose **absence refuses at C0**, the writer's **W11a**, and the syscall trace showing the deployment reads no path in the group-writable worktree — is package plan §2.12.5a and `JNL-51`, and **none of it has been run.** **The limit is stated rather than argued around**: an actor holding **A5** rewrites every host copy and one holding **A5 + A8** also inserts the row here, which is residual **R-5.0-15** and is refused by nothing in this design |
| **Every operating-system identity's group membership is stated once, and this artifact states none of its own** | **P5.0-SR2**, §4.3.2, §4.3.5 | §4.3.2's *"no supplementary groups"* sentence is **withdrawn** — it contradicted its own table from revision 6 onward — and its membership table becomes a **citation** of package plan §2.12.2, which is now canonical, with a stated rule that a disagreement makes this artifact wrong. §4.3.5 states explicitly that **no membership can move a cell in the authentication matrix**, because `pg_hba`, `pg_ident` and `SO_PEERCRED` resolve a database principal from a system **user** and never from a group — so the correction changes no schema guarantee, which is why it is recorded here rather than as a constraint. The evidence is `JNL-52`'s eight positive and negative `id`, `namei -l` and `open` cases for `freedomsheet`, `freedomcoord`, `discordbot` and `freedomweb`, which is the security review's check **C-4**; **it has not been run, and none of the four proposed identities or the group exists on this host** |

---

## 10. The decisions this artifact does not make

| Ref | Question | State |
|---|---|---|
| D5.0-1 / OD-54 | Does package 5.0 persist a control plane? | **Closed** — yes, conditional on remediation and re-review |
| D5.0-2 / OD-55 | Where does comparison telemetry live? | **Closed** — package 5.1 |
| D5.0-3 / OD-56 | May telemetry record `character_id`? | **Closed** — internal UUID only, at 5.1's gate |
| D5.0-4 / OD-57 | The numeric controls N5.0-1 … N5.0-8 | **Closed** — accepted |
| D5.0-5 / OD-58 | Is the ledger table 5.2's? | **Closed** — yes |
| D5.0-6 / OD-59 | The authority-change surface | **Closed** — host-local operator command only |
| D5.0-7 / OD-60 | A non-human scope? | **Closed** — none in 5.0. Unchanged by revisions 3 and 4: the coordinator is a *database* principal, reached by a *human* through `sudo`, for a human-run command. It is not a service principal, and `application/service_principals.py` is untouched |
| D5.0-8 / OD-61 | Named reviewers | **Closed 2026-08-31** — Codex is Independent Reviewer, logical-schema reviewer and Security Reviewer. **The security review itself is outstanding**: its first pass, 2026-08-31, returned changes requested with no recommendation (P5.0-SR1 Blocking, P5.0-SR2 Important), and revision 12 remediates both and claims neither closed. *Revision 11's wording, retained for the record:* Security Reviewer unnamed; this artifact cannot be accepted until the schema review recommends acceptance. **Revision 7 added one element to the Security Reviewer's scope** — the transient `systemd-run` unit stage 4 starts as root at provisioning — and **revision 8 adds a second**: the `…/probe-ro` directory the writer's identity may write during provisioning, plus the combined-authority residual **R-5.0-12**. Neither changed the estimate. **Revision 9 adds no surface and does raise the estimate, to 3.0–4.0 reviewer-days**, because the threat model is now nine authorities whose combinations must each be checked against real Unix DAC and there are now two unrefused residuals — **R-5.0-12** and the new **R-5.0-13** — plus the operator-recovery residue state **R-5.0-14** |
| **D5.0-9 / OD-62** | **Reframed a third time by revision 4; unchanged in substance by revision 6.** No barrier for I-SHEET-COMPLETE exists in the published Google APIs (package plan §2.10.2), so the question is no longer *which fence* but **what is accepted in place of one**: the drain-first boundary with an enumerable unresolved set and detection (G-A), pre-cutover write-path retirement (G-B), an acknowledged quiet period (G-C), or no Sheet-authoritative cutover at all (G-D) | **Open. Blocks WP-4b.** Both earlier framings are withdrawn. **It is now a risk acceptance and belongs to the Acceptance Authority**, because §2.8's sixth row is what is being accepted. **Revision 6 records two impacts without deciding it**: G-A's enumeration control was found not implementable and is replaced, so the R4 precondition — that the Independent Reviewer accept the control as fail-closed — still stands and is still unmet; and four new refusal conditions widen G-A's availability cost under R-5.0-11 (package plan §5.3) |
| **D5.0-10 / OD-63** | **Extended to nine by revision 5; unchanged by revision 6, which adds no numeric control.** N5.0-14, N5.0-16, N5.0-17, N5.0-18, N5.0-19 and N5.0-20 carry forward unchanged from revision 4; **N5.0-21 (journal free-space floor), N5.0-22 (rotation size ceiling) and N5.0-23 (archive retention) are new**, the last owned by the **Data Owner** because it decides when evidence may be destroyed | **Open. Blocks WP-1's completion** |
| **D5.0-11 / OD-64** | **Extended by revision 4; unchanged by revision 6.** Is `freedom_migration_coordinator` introduced *together with* the dedicated `freedomcoord` OS identity, the `pg_hba` ordering, the `pg_ident` map, the `sudoers` boundary and the root-owned deployment path (§4.3.2–§4.3.5)? Approving the role without the host boundary would approve a control that does not exist | **Open. Blocks WP-2 and WP-14.** A database-role, credential and **host**-topology change requiring an impact assessment and the named Security Reviewer's review |
| **D5.0-12 / OD-65** | **Extended again by revision 12** with the reviewed-source provenance objects — a `0700 root:root` bare Git object store, an out-of-band approved-revision record and a per-component provenance record, all three new host objects, one of them a governance artifact needing a custody procedure — and with the **canonical membership table** §2.12.2 now specifies, which provisioning must create in a stated order and re-verify after any account, group or deployment change. Otherwise: the host changes the boundary needs outside the coordinator: a dedicated `freedomsheet` identity with the Google credential relocated to it; hardening directives on the live `freedom-bot` unit (Phase 0 finding F-3); and a ruling on the group-writable repository tree that lets service identities edit every module. **Extended by revision 6** with a third system group, `freedomjournal`, holding exactly `freedomcoord` and `freedomsheet`, which is what lets the writer read the seal it is required to validate while removing every other identity's traverse of `…/journal` (§4.3.2) | **Open. Blocks WP-4b and WP-14.** Package plan §5.3 prices three options |
| **D5.0-13 / OD-66** | **Amended by revision 12:** option A's cost gains the **seventh table** `approved_source_revisions` (§3.8), the **four provenance columns** on §3.7 including a `NOT NULL` foreign key, and the three fail-closed conditions `J-26 … J-28`; and a new **option A-3** — a cryptographically signed approval record verified against a root-held keyring, which would close **R-5.0-15**'s A5-only half — is **raised and not adopted**, on the same reasoning as A-2. **No option is chosen here.** Otherwise: **new in revision 5, and it is what P5.0-R5 forces.** Four things ruled together: the **durable root-owned storage** at `/var/lib/freedom-sheet-writer`, deliberately not systemd's `StateDirectory=`; the **sealed generation and its PostgreSQL registration** (§3.7), without which the activation trigger cannot refuse stale or cross-generation evidence; the **privileged `freedom-journal-admin` lifecycle** under a second `sudoers` drop-in that runs as root; and the **retention and disposal rule** N5.0-23, which is the Data Owner's. Options J-1 … J-4 in package plan §2.13.11, including **J-3: drop `dispatch_journal_clear` and the journal entirely**, which is the honest alternative to revision 4's contradiction and is Peter's to take rather than the implementer's. **Option A's content changed in revision 6, again in revision 7 and again in revision 8, and is re-stated rather than carried forward unread**: at revision 6, an acyclic construction in place of one that could not be built, a seal the writer may read through a third system group, a probe whose refusals are attributable and whose startup path is non-destructive, and a registration that **records** an attestation in place of a `CHECK` credited with proving one (§3.7.1); at revision 7, the probe's **sandbox stage moves to provisioning**, inside the sealed report — which adds a transient `systemd-run` unit started as root and a deployed-unit precondition, and removes a deployment-time step — and the seal's **binding section holds three authenticated fields instead of five, two of which no verifier read**; at revision 8, the generation construction gains a **post-probe validation step** so it can be executed in the order it states, Stage 4 gains a **second transient directory `…/probe-ro` and the positive DAC control `S4-0`**, and the threat model becomes an **eight-capability register** whose combined-authority residual **R-5.0-12** is recorded rather than refused; and at revision 9, the deployment digest becomes a **computed value validated at C0 against the deployed manifest** before anything consumes it (§2.13.2c), the transient directories acquire a **three-state cleanup contract** whose failed-cleanup state **refuses and reports rather than cleaning**, and the threat model becomes **nine independently constructible authorities** with per-row minimum combinations; **and at revision 10, option A's content does not change at all** — R9 corrects the *description* of a Linux permission check option A already depended on, so the register becomes **eleven** authorities (`A1` the `CAP_LINUX_IMMUTABLE` half of `FS_IOC_SETFLAGS`, `A10` and `A11` its owner-or-`CAP_FOWNER` half) and eleven of thirteen falsification rows gain a prerequisite, **every one of which makes the alteration harder to construct**. **All seven movements are corrections to claims, not new capabilities**; the revision-9 ones add a specification and remove a code path, the revision-10 ones add neither, and none of them adds an artifact, authority, column or refusal code. **A new option A-2 is raised inside this decision by revision 9** — option A **plus an independent authenticated host-bound value**, the only thing that would make package-plan **F-7** a refusal instead of residual **R-5.0-13**. It **would** add a seal field, a **V-W** step, a coordinator comparison, a refusal code, a §2.13.6 condition and a column here, and its principal price is that a **legitimate restore onto replacement hardware fails closed**. It is **routed under §0.2 and not adopted**. Its other options, owners and retention rule are unchanged | **Open. Blocks WP-4b and WP-15.** A production-topology, privileged-tooling and evidence-retention decision requiring the named Security Reviewer's review and the Data Owner's ruling on retention |
