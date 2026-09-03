# Decision register

**Current decision update, 2026-09-02.** Peter Duscha approved **D5.0-11 /
OD-64 Option A**, **D5.0-12 / OD-65 Option B**, and **D5.0-13 / OD-66 Option
A / J-1** in all accountable roles. The dedicated coordinator boundary, the
isolated Sheet-writer and provenance controls (with correction of the
group-writable worktree deferred to a separate maintenance change), and the
full durable sealed/registered journal contract are now binding Package 5.0
inputs. OD-66's approval does not by itself accept R-5.0-12 through R-5.0-16;
their explicit dispositions and the operational evidence remain outstanding.
Peter recorded **G-A as the provisional direction for D5.0-9 / OD-62**, but
expressly deferred its binding ruling until P5.0-R5's operational evidence and
independent review are complete. OD-62 therefore remains Open. Package 5.0
remains `not ready`, and implementation remains unauthorized.

**Security-review dependency update, 2026-09-02.** Codex delivered the
revision-12 Security Reviewer recommendation and closed P5.0-SR1/SR2 on design.
D5.0-11 / OD-64, D5.0-12 / OD-65 and D5.0-13 / OD-66 are now rulable by their
accountable owners; none is ruled by the review. D5.0-9 / OD-62 remains last.
Operational evidence and P5.0-R5 still block readiness and implementation.

**Current decision update, 2026-09-02.** Peter Duscha accepted Codex's closure
recommendation for P4-PG4 and P4-PG5; Phase 4 remains approved and closed.
Peter also approved **D5.0-10 / OD-63 Option 1** in every accountable role. The
nine numeric controls are accepted, with N5.0-18 fixed at **120 seconds — an
operational margin, not a barrier**. The older open D5.0-10 row below is
superseded by this decision and retained as decision history. D5.0-11 through
D5.0-13 were subsequently approved as recorded in the current update above;
D5.0-9 remains Open. Package 5.0 remains `not ready`.

**Phase 4 post-gate correction note, 2026-08-31. No decision is required or
made.** P4-PG1 through P4-PG3 are Closed; P4-PG4 and P4-PG5 have a bounded
implementation remediation and Codex re-review before Phase 5 preparation
resumes. The correction changes no architecture, authority, schema, migration,
deployment, data ownership, phase order or release boundary. D5.0-9 through
D5.0-13 / OD-62 through OD-66 remain Open and unchanged.

**Superseded as the active work item — Security remediation R11 submitted,
2026-08-31. No decision is made by it.**

The Package 5.0 security review returned **P5.0-SR1 (Blocking)** and **P5.0-SR2
(Important)** with no readiness recommendation; revision 12 of the package plan
and the logical schema remediates both and **claims neither closed**.
**D5.0-9 through D5.0-13 / OD-62 through OD-66 remain Open and must not be ruled
from revision 12.** No decision number is added and **no option is adopted**.

Two decision entries change **content**, and neither changes state:

- **D5.0-12 / OD-65's scope is extended** by the reviewed-source provenance
  objects — a `root:root 0700` bare Git object store, an out-of-band
  approved-revision record and a per-component provenance record, all three new
  host objects, one of them a governance artifact needing a custody procedure —
  and by the **canonical identity and group membership table** provisioning must
  create in a stated order and re-verify after any account, group or deployment
  change. Its option set grows from three to four: **option C** now names taking
  everything *except* the provenance objects, and the implementer's assessment,
  recorded so it can be disagreed with, is that **option C leaves P5.0-SR1
  unremediated**.
- **D5.0-13 / OD-66 gains option A-3**, a cryptographically signed
  approved-revision record verified against a root-held keyring, which would
  narrow residual **R-5.0-15** to its A5-only case. **It is priced and
  deliberately not adopted**, on the same reasoning as option A-2: a signing key
  is a governance change with its own custody, rotation, revocation and
  availability failure modes, and it is the Acceptance Authority's to make.
  Option A's **cost** also grows by a seventh table, four columns and three
  fail-closed conditions.

**Everything else holds.** Options A, A-2, B, C and D of OD-66 are unchanged word
for word; no numeric control is added or moved; no vocabulary widens except the
new closed two-value `component`; and no schema object is *adopted* — the seventh
table and the four columns are **proposed**, like every object in the logical
schema, and remain so until the schema gate closes. Package 5.0 remains `not
ready` and implementation remains unauthorized.

**Superseded — Security Reviewer named, 2026-08-31.** Peter Duscha named **Codex** the
Package 5.0 Security Reviewer, closing **D5.0-8 / OD-61**. **This is the only
decision closed by it.** D5.0-9 through D5.0-13 / OD-62 through OD-66 remain
**Open**; no option is adopted; no finding closes; A-5.0-3, A-5.0-4 and A-5.0-5
remain unconfirmed. Package 5.0 remains `not ready` and implementation remains
unauthorized. **D5.0-11, D5.0-12 and D5.0-13 are owned *on the Security
Reviewer's review* and stay unrulable until that recommendation exists;
D5.0-10 carries no such dependency and is rulable now** — its unsigned
change-control package is `docs/review/phase-5-0-od-63-ruling-draft.md`.
**D5.0-9 is ruled last**, being the risk acceptance the other four price.

**Superseded on the reviewer-naming point — revision 11 independent re-review, 2026-08-31.** R10-A through R10-C are
materially addressed on paper, with no new Blocking or Important design
finding. This review decides nothing: D5.0-9 through D5.0-13 / OD-62 through
OD-66 remain **Open**, no option is adopted, and the Security Reviewer remains
unnamed. Package 5.0 remains `not ready` and implementation remains
unauthorized. The active handover routes these decisions to their accountable
owners before any implementation brief may be issued.

**Superseded — remediation R10 submitted, 2026-08-31.** D5.0-9 / OD-62 through D5.0-13 /
OD-66 remain **Open** and **must not be ruled from revision 11**. Revision 11 of
the package plan and the logical schema is **documentation and design only**, it
**claims no finding closed**, and it **raises no new decision number and no new
option**. **No option, risk, decision or schema object is adopted or closed by
R10.**

**D5.0-13 / OD-66's options do not move at all.** R10 corrects how the *evidence
harness* constructs the identities that test option A's threat model — a
`capsh(1)` launch procedure replacing `setpriv` recipes the named tool rejects —
and touches no artifact, authority, column, refusal code, retention rule or cost
of option A. **Option A-2** (an independent authenticated host-bound value)
remains unchanged and **not adopted**; options **B**, **C** and **D** are
unchanged.

**The `capsh` choice is not a decision this register records, and is deliberately
not raised as one.** It is an evidence-harness mechanism inside assumption
**A-5.0-5**, which is unconfirmed: it installs nothing, sets no file capability,
creates no set-user-ID artifact, adds no `sudoers` rule, unit, group, account or
directory beyond the disposable `fbprobe` identity revision 10 already carried,
and changes no production tool — `verify-capability`, `freedom-journal-admin`,
`migration-authority` and the writer are untouched. It is routed to the
**Security Reviewer** in package plan §9.2 as a question, with the declined
alternatives named. **If the Acceptance Authority judges that an evidence
mechanism belongs in this register, that is a ruling to make rather than one this
submission has made.**

**Nothing else that feeds a ruling has moved.** The threat model stays at eleven
authorities and thirteen falsification rows; the evidence band stays at fifty
identifiers and eighty-eight cases; the Security Reviewer's estimate stays at
**3.5–4.5** reviewer-days; the PERT estimate stays at **40.9**; and assumption
**A-5.0-5** is widened to name the new mechanism and its prerequisites and
**remains unconfirmed**. The Security Reviewer remains **unnamed**; Package 5.0
remains `not ready`; implementation is **unauthorized**; and **an independent
re-review of revision 11 is required**.

**Superseded — revision-10 independent re-review, 2026-08-31.** D5.0-9 / OD-62 through
D5.0-13 / OD-66 remain **Open** and must not be ruled from revision 10. The
review requests remediation R10 solely because the documented E-identity launch
recipes and declared capability masks do not agree with the named `setpriv`
contract. It adds no decision, option, artifact, authority, column, refusal code
or accepted cost. Option A and option A-2 remain unchanged and unadopted; the
Security Reviewer remains unnamed; Package 5.0 remains `not ready`; implementation
is unauthorized.

**Superseded — remediation R9 submitted, 2026-08-30.** D5.0-9 / OD-62 through D5.0-13 / OD-66
remain **Open** and **must not be ruled from revision 10**. Revision 10 of the
package plan and the logical schema is **documentation and design only**, it
**claims no finding closed**, and it **raises no new decision number and no new
option**. **D5.0-13 / OD-66 option A's content does not change**: R9 corrects the
*description* of a Linux permission check that option A's design already depended
on — `FS_IOC_SETFLAGS` needs the caller to own the inode or hold `CAP_FOWNER` as
well as `CAP_LINUX_IMMUTABLE` — so no artifact, authority, column, refusal code or
cost of option A moves. **Option A-2** (an independent authenticated host-bound
value) is preserved unchanged and remains **not adopted**; options **B**, **C**
and **D** are unchanged. What does change is input to the ruling rather than part
of it: the threat model that prices option A grows from nine authorities to
**eleven**, eleven of thirteen falsification rows gain a prerequisite that makes
each alteration **harder** to construct, the Security Reviewer's estimate rises to
**3.5–4.5** reviewer-days, assumption **A-5.0-5** is corrected and remains
unconfirmed, and the PERT estimate rises to **40.9**. The Security Reviewer
remains unnamed; Package 5.0 remains `not ready`; implementation is unauthorized.

**Superseded — revision-9 independent re-review, 2026-08-30 — remediation R9 required.**
D5.0-9 / OD-62 through D5.0-13 / OD-66 remain **Open** and must not be ruled
from revision 9. The review accepts none of revision 9 as authority and adds no
decision: its authority model omits the owner-or-`CAP_FOWNER` prerequisite for
`FS_IOC_SETFLAGS` and contradicts itself about whether A3 confers A2. Revision
10 must correct the model and evidence under remediation R9. The Security
Reviewer remains unnamed; Package 5.0 remains `not ready`; implementation is
unauthorized.

**Superseded — remediation R8 submitted, 2026-08-30.** D5.0-9 / OD-62 through D5.0-13 / OD-66
remain **Open** and **must not be ruled from revision 9**. Revision 9 of the
package plan and the logical schema is **documentation and design only**, it
**claims no finding closed**, and it **raises no new decision number**.
**D5.0-13 / OD-66 option A's content changes in two places** — the deployment
digest becomes a value `init-generation` **computes at C0 and compares against
the deployed manifest** before anything consumes it (new §2.13.2c), and the
transient probe directories acquire an explicit **three-state cleanup contract**
whose failed-cleanup state **refuses and reports rather than cleaning**, which
**removes** a code path revision 8 had. Neither adds an artifact, an authority, a
column or a refusal code. **A new option A-2 is raised inside D5.0-13**: option A
**plus an independent authenticated host-bound value** — a TPM-sealed or
coordinator-signed host token — which is the only thing that would make
package-plan **F-7** a refusal instead of residual **R-5.0-13**. It **would** add
a seal field, a V-W step, a coordinator comparison, a refusal code, a §2.13.6
condition and a database column, and its principal price is that a **legitimate
restore onto replacement hardware fails closed**. Because it changes the design
surface it is **routed to the Acceptance Authority under §0.2 and is not
adopted**; revision 9 takes option A with the residual stated instead. **Options
B, C and D, the owners, the authorities and retention rule N5.0-23 are unchanged.
D5.0-9, D5.0-10, D5.0-11 and D5.0-12 are untouched, and no numeric control is
added.** The Security Reviewer remains **unnamed**; the security-review estimate
rises to **3.0–4.0 reviewer-days** with **no added surface**, and the reviewer
inherits a **second** unrefused residual, **R-5.0-13**, alongside R-5.0-12 and
the new operator-recovery state **R-5.0-14**. The entries below record impacts,
not approvals.

Status date: 2026-08-30 (Package 5.0 design remediation **R8** submitted for
independent re-review; it claims no finding closed; all Package 5.0 open
decisions retain their prior owners and status; no option approved.)

**Superseded — revision-8 independent re-review update, 2026-08-30.** D5.0-9 / OD-62 through
D5.0-13 / OD-66 remain **Open** and must not be ruled from revision 8. Four
Blocking internal inconsistencies remain in Algorithm C's value ordering, the
cleanup-failure evidence, the K3/K4 DAC boundary and F-7's claimed host-identity
detector. They require remediation R8 and revision 9; they close no decision and
authorize no implementation. The Security Reviewer remains unnamed and Package
5.0 remains `not ready`.

**Superseded — remediation R7 submitted, 2026-08-30.** D5.0-9 / OD-62 through D5.0-13 / OD-66
remain **Open** and **must not be ruled from revision 8**. Revision 8 of the
package plan and the logical schema is **documentation and design only**, it
**claims no finding closed**, and it **raises no new decision number**: none of
the three Blocking corrections introduces a governed choice. **D5.0-13 / OD-66
option A's content changes in three places** — the generation construction gains a
**post-probe validation step** (**C2**) so it can be executed in the order it
states; Stage 4 gains a **second transient directory `…/probe-ro`** and the
positive DAC control **`S4-0`**; and the threat model becomes an **eight-capability
register** in place of two attacker classes. The first and third add no host
artifact at all; the second adds one transient directory to a probe option A
already carries. **All three are corrections to claims, not new capabilities**,
and they are recorded there rather than adopted. **Options B, C and D, the
owners, the authorities and retention rule N5.0-23 are unchanged. D5.0-9,
D5.0-10, D5.0-11 and D5.0-12 are untouched, and no numeric control is added.**
The Security Reviewer remains **unnamed** and gains one surface element
(`…/probe-ro`) and the new residual **R-5.0-12** — the combination of host root
and PostgreSQL superuser authority, which **no check in this design refuses** and
which is recorded for the Acceptance Authority under D5.0-13 rather than
mitigated. The entries below record impacts, not approvals.

Status date: 2026-08-30 (Package 5.0 design remediation **R7** submitted for
independent re-review; it claims no finding closed; all Package 5.0 open
decisions retain their prior owners and status; no option approved.)

**Superseded — revision-7 independent re-review update, 2026-08-30.** D5.0-9 / OD-62 through
D5.0-13 / OD-66 retain their prior owners and remain Open. Revision 7 cannot be
used to rule them because its creation order, sandbox-attribution evidence and
attacker-capability model remain internally inconsistent. Remediation R7 and
another independent re-review are required before readiness, implementation or
any ruling.

**Remediation R6 submitted, 2026-08-30.** D5.0-9 / OD-62 through D5.0-13 /
OD-66 remain **Open** and **must not be ruled from revision 7**. Revision 7 of
the package plan and the logical schema is **documentation and design only**, it
**claims no finding closed**, and it **raises no new decision number**: the
probe-evidence lifecycle question the R6 handoff put — bind the sandbox stage
into the immutable report, or split it into a second typed artifact — was a
choice of *where* evidence lives inside **D5.0-13 / OD-66 option A**, which is
already open, so it is recorded there as an amended option-A content and is
**not** adopted. **D5.0-13 / OD-66 option A's content changes in two places** —
the probe's sandbox stage moves to provisioning, inside the sealed report, and
the seal's binding section holds three authenticated fields instead of five, two
of which no verifier read — and both are corrections to revision-6 claims rather
than new capabilities. **Options B, C and D, the owners, the authorities and
retention rule N5.0-23 are unchanged.** **D5.0-9, D5.0-10, D5.0-11 and D5.0-12
are untouched, and no numeric control is added.** The Security Reviewer remains
unnamed and gains one surface element. The entries below record impacts, not
approvals.

Status date: 2026-08-30 (Package 5.0 design remediation **R6** submitted for
independent re-review; it claims no finding closed; all Package 5.0 open
decisions retain their prior owners and status; no option approved.

**Superseded — revision-6 independent re-review update, 2026-08-30.** D5.0-9 /
OD-62 and D5.0-13 / OD-66 remained Open and were not to be ruled from revision
6. P5.0-R5 remained Blocking: the immutable probe-report lifecycle contradicted
the later deployment-time sandbox stage, and V-W did not support F-1's claim
that every seal-byte alteration is refused without PostgreSQL. `JNL-32` also
contradicted the W9/W17 order.

Superseded status date: 2026-08-30 (revision 6 independently re-reviewed;
remediation R6 required; all Package 5.0 open decisions retain their prior owners and status;
no option approved. Earlier status history follows. Phase 4 gate approved;
Peter Duscha ruled Package 5.0
decisions D5.0-1 through D5.0-7 and partially resolved D5.0-8; Codex closed
P5.0-R2 on remediation-R1 re-review, kept P5.0-R1 Blocking and raised Blocking
P5.0-R4; remediation R2 was re-reviewed on 2026-08-29 and both findings stayed
Blocking; design remediation R3 was independently re-reviewed on 2026-08-29,
P5.0-R1 stayed Blocking and new Blocking finding P5.0-R5 was raised; **design
remediation R4 was submitted on 2026-08-29 and claims no finding closed**;
revision 5 was independently re-reviewed on 2026-08-29 and P5.0-R5 stayed
Blocking; **design remediation R5 was submitted on 2026-08-30 and likewise claims
no finding closed**; revision 6 was independently re-reviewed on 2026-08-30 and
P5.0-R5 stayed Blocking; **design remediation R6 was submitted on 2026-08-30 and
likewise claims no finding closed**. D5.0-9 remains reframed a third time and is a **risk
acceptance**, D5.0-10 is **extended to nine controls**, D5.0-11 remains extended
to the operating-system identity and host boundary, **D5.0-12 is extended by a
third system group** `freedomjournal`, **D5.0-13's option A is re-stated** for
revision 6 — the dispatch journal's durable storage, generation lifecycle and
evidence-disposal authority — and the Security Reviewer remains unnamed)

**Remediation R5 note, 2026-08-30.** Revision 6 of the package plan and the
logical schema is **documentation and design only**. It raises **no new decision
number**. D5.0-9 / OD-62 and D5.0-13 / OD-66 remain Open and **must not be ruled
from revision 6**; the entries below record impacts, not approvals.

## Package 5.0 decisions — ruled 2026-08-29

Raised by the package 5.0 readiness and design submission and ruled by Peter
Duscha on Codex's independent recommendation. Full statements,
options and reasoning are in
[`../review/phase-5-0-package-plan.md`](../review/phase-5-0-package-plan.md) §5.2;
the schema consequences are in
[`../review/phase-5-0-logical-schema.md`](../review/phase-5-0-logical-schema.md).
Each accepted ruling is recorded in
[`../discovery/open-decisions.md`](../discovery/open-decisions.md) with an OD
number while retaining its local `D5.0-n` traceability reference.

**Current-row override, 2026-09-02:** the historical rows below that label
D5.0-11, D5.0-12 or D5.0-13 Open are superseded by the current decision update
at the top of this register. They are Closed as OD-64 A, OD-65 B and OD-66
A/J-1 respectively. D5.0-9 / OD-62 remains Open; G-A is provisional only.

| Decision | Status | Question | Accountable role | Required before | Ruling |
|---|---|---|---|---|---|
| D5.0-1 / OD-54 | **Closed** | Persist a Package 5.0 control plane | Product Owner / Acceptance Authority | before implementation | **Yes.** P5.0-R2 is closed; P5.0-R1 and P5.0-R4 must close before schema acceptance. Remediation R2 reduces the control plane from six tables to **five** by withdrawing the lease and acknowledgement tables |
| D5.0-2 / OD-55 | **Closed** | Placement of comparison telemetry | Product Owner | before implementation | **Package 5.1** creates the table and write path with its first real shadow consumer; 5.0 delivers the common contract only |
| D5.0-3 / OD-56 | **Closed** | `character_id` in comparison telemetry | Data Owner | Package 5.1 schema | Permitted as an internal UUID only, with restricted access, approved retention, and no names, Discord IDs, values, exception text or arbitrary payloads; Security Reviewer confirmation remains required at that package's gate |
| D5.0-4 / OD-57 | **Closed** | Numeric cutover controls | Product Owner / Operations Owner | contract completion | Approved as proposed, except that fewer than 30 comparisons requires a separately approved package-specific threshold before shadowing begins |
| D5.0-5 / OD-58 | **Closed** | Durable ledger ownership | Data Owner / Acceptance Authority | Package 5.2 readiness | The durable ledger table belongs to **5.2** |
| D5.0-6 / OD-59 | **Closed** | Authority-change surface | Product Owner | Package 5.0 implementation | Host-local Platform-Administrator operator command only; no web or Discord mutation surface |
| D5.0-7 / OD-60 | **Closed** | Non-human scope | Product Owner | Package 5.0 implementation | No new service-principal scope in 5.0; reconsider only with a concrete consumer, initially 5.3 |
| D5.0-8 / OD-61 | **Closed 2026-08-31** | Named roles | Delivery Lead / Acceptance Authority | readiness | Claude designated implementer/working Technical Lead; Codex designated Independent Reviewer, logical-schema reviewer and — **named by Peter Duscha 2026-08-31** — **Security Reviewer**. Compatible with §0.3 because Codex did not implement the package; the resulting concentration of design and security judgement in one reviewer is accepted knowingly. **The assignment approves no option and closes no finding**, and the distinct §9.2 security pass (3.5–4.5 reviewer-days, eleven surfaces) is still outstanding |
| **D5.0-9 / OD-62** | **Open — reframed a third time 2026-08-29; blocks WP-4b and must await R4** | **No barrier exists, so what is accepted in place of one?** G-A the drain-first boundary with an enumerable unresolved set, fail-closed activation, containment and detection; G-B pre-cutover write-path retirement; G-C an acknowledged quiet period; or G-D no Sheet-authoritative cutover at all | **Acceptance Authority** and Product Owner, with the Operations Owner and the Security Reviewer | before Package 5.0 WP-4b, and only after P5.0-R5 is remediated and re-reviewed | **Not ruled.** Remediation R3 traced thirteen candidate barriers against the published Sheets v4 and Drive v3 surface and concludes **none proves that a request Google accepted before the fence is reflected before the final import reads**. Revision 3's enforceability claim is withdrawn. **This is now a risk acceptance, not a cost choice**: G-A, G-B and G-C each require accepting an unprovable residual on the authoritative store of a live community's game state. Revision-4 re-review additionally found that G-A's journal can falsely appear clear because it is on volatile `/run` and its lifecycle is unspecified. **Remediation R4, submitted 2026-08-29, rebuilds that control** — durable root-owned storage on a filesystem that was read rather than inferred, a sealed and registered generation, a hash chain, twenty-one fail-closed conditions and a privileged lifecycle — and states plainly that **none of it is a barrier and R-5.0-8 is not narrowed by a single case**. **Peter must still not decide among the options until the Independent Reviewer accepts that the enumeration control is fail-closed.** Both earlier framings are withdrawn and retained as decision history. **Remediation R5, 2026-08-30, records impacts and decides nothing.** Revision 6 makes G-A's enumeration control *creatable* — the revision-5 seal could not be built as specified — and makes its evidence attributable rather than asserted, but it changes **no cost, topology, authority, retention or failure behaviour** in a way that favours one option over another, and **it is still not a barrier**. The residual **R-5.0-8 is not narrowed by a single case**. Peter must still not decide until the Independent Reviewer accepts that the control is fail-closed |
| **D5.0-10 / OD-63** | **Open — extended to nine 2026-08-29; blocks WP-1 completion** | N5.0-14, N5.0-16, N5.0-17, N5.0-18, N5.0-19 and N5.0-20 carry forward unchanged from revision 4; **N5.0-21 new** (minimum free space on the journal filesystem below which the writer refuses to dispatch, 1 GiB); **N5.0-22 new** (maximum current-journal size before a privileged rotation, 64 MiB); **N5.0-23 new** (retention of a sealed archived generation — until plan §15.1's gate and not less than 365 days) | Operations Owner / Product Owner | before Package 5.0 WP-1 completes | **Not ruled.** N5.0-9 … N5.0-13 and N5.0-15 remain withdrawn with the lease. Two of the four revision-3 controls were described as bounds they cannot be, and were reframed rather than re-valued. **WP-13 is demoted**: it informs N5.0-18's margin and closes nothing, so the coupling to D5.0-9 is weaker than it was. **Remediation R4 adds three storage-lifecycle numbers.** N5.0-23 is the only number in the register whose owner is the **Data Owner**, because it decides when a record of what the platform wrote to a live community's Sheet may be destroyed. **Unchanged by remediation R5**, which adds no numeric control: the probe version, the arena and the retry behaviour are all design constants, not operator-set thresholds. **Unchanged again by remediation R6**, which likewise adds none: the probe's stage ordering, its `systemd-run` substitution and the seal binding's field set are design constants. The count stays at **nine** |
| **D5.0-11 / OD-64** | **Open — extended 2026-08-29; blocks WP-2 and WP-14** | Is `freedom_migration_coordinator` introduced **together with** the dedicated `freedomcoord` operating-system identity, the `pg_hba.conf` ordering, the single `pg_ident.conf` map, the `sudoers` execution boundary and the root-owned deployment path? | Product Owner / Operations Owner, on the Security Reviewer's review | before Package 5.0 WP-2 and WP-14 | **Not ruled.** Remediation R3 supplies the specification the re-review required. **Approving the role without the host boundary would approve a control that does not exist**, so the two halves are one decision. Unlike the revision-3 framing this **does** change the accepted topology, which is why it is raised rather than adopted. Option D remains the original P5.0-R4 finding |
| **D5.0-12 / OD-65** | **Open — new 2026-08-29; blocks WP-4b and WP-14** | The host changes the boundary requires outside the coordinator: a dedicated `freedomsheet` identity with the Google credential relocated to it; hardening directives on the live `freedom-bot` unit (Phase 0 finding F-3); and a ruling on the group-writable repository tree that lets every service identity edit every module | Operations Owner / Product Owner, on the Security Reviewer's review | before Package 5.0 WP-4b and WP-14 | **Not ruled.** Two of the three are pre-existing conditions the design would otherwise rely on silently. Package 5.0 **works around** the repository permissions with a root-owned deployment path rather than fixing them, because fixing them is wider than this package; the workaround is sufficient for the coordinator and does not make the condition acceptable. **Extended by remediation R5** to a **third system group**, `freedomjournal`, holding exactly `freedomcoord` and `freedomsheet` and carrying **no database privilege**. It exists so the writer can *read* the seal it is required to validate while `…/journal` tightens from `0751` to `root:freedomjournal 0750` — so the net effect is a **narrower** grant than revision 5 had: `discordbot` and `freedomweb` lose even directory traverse. A world-readable `0444` seal was considered and rejected for exactly that reason. The group is an operating-system change and is the Operations Owner's to approve |
| **D5.0-13 / OD-66** | **Open — new 2026-08-29; blocks WP-4b and WP-15** | The dispatch journal's durable storage, generation lifecycle and evidence-disposal authority — four things ruled together: the root-owned hierarchy at `/var/lib/freedom-sheet-writer`, deliberately **not** systemd's `StateDirectory=`, which would make the writer own the directory holding its own evidence; the sealed generation and its PostgreSQL registration in a **sixth table**, without which the activation trigger cannot refuse stale or cross-generation evidence; the privileged `freedom-journal-admin` lifecycle under a **second `sudoers` drop-in that runs as root**; and the retention and disposal rule N5.0-23 | Operations Owner and **Data Owner**, on the Security Reviewer's review | before Package 5.0 WP-4b and WP-15 | **Not ruled.** Raised by design remediation R4 in response to Blocking finding P5.0-R5. Options **J-1** (the full contract, recommended), **J-2** (durable storage without the PostgreSQL registration, so the stale-evidence check exists only in the coordinator command), **J-3** (**drop `dispatch_journal_clear` and the journal entirely** — the honest alternative to revision 4's contradiction, which removes the only control that refuses a cutover when a request is *known* outstanding, and is Peter's to take rather than the implementer's), and **J-4** (keep the `/run` journal, which is the finding). **Option A carries a named cost, R-5.0-11**: a full or failing journal filesystem stops Sheet mutations until an operator acts. **Option A is re-stated by remediation R5 and is what would be ruled on**: the acyclic seal-body/genesis/seal-digest construction, the minimum read-only seal grant through `freedomjournal`, the four-stage disposable-arena capability probe with privileged cleanup, and an attested probe report in place of the **withdrawn** `CHECK (append_only_verified)`. J-1 remains recommended and J-2 is now marginally less bad than it was, because more of the check is derivable on the host; J-3 and J-4 are unchanged. R-5.0-11 grows with the fail-closed conditions, from twenty-one to **twenty-five**. **Option A's content is amended again by remediation R6, in two places and no others, and is again what would be ruled on**: the capability probe's **sandbox stage moves from deployment to provisioning**, inside the same `verify-capability` invocation and before the report is sealed — which adds a transient `systemd-run` unit started **as root** and a requirement that the writer's unit file be deployed, and removes a deployment-time step — and the seal's **binding section holds three authenticated fields instead of five**, `sealed_at` and the binding's own format field being withdrawn because no verifier read either. **Both are corrections to revision-6 claims, not new capabilities.** J-1 remains recommended; **J-2 is worse than revision 6 made it look**, because the registered row is now identified as the only artifact that refuses a privileged rewrite of the seal *and* the journal's record 0 (falsification case F-1b); J-3 and J-4 are unchanged, as are the owners, the authorities and N5.0-23. The Security Reviewer's scope gains the transient root-started unit, without a change to the 2.5–3.5 reviewer-day estimate. **Option A's content is amended again by remediation R7**, in two places: Stage 4 gains an **exact target `…/probe-ro/s4-2.target` in a second transient directory** and the **positive DAC control `S4-0`**, and the construction gains a **post-probe validation step C2**. **And again by remediation R8**, in two places and no others: the deployment digest becomes a value **computed at C0 and compared against the deployed manifest** before anything consumes it (§2.13.2c), and the transient directories acquire a **three-state cleanup contract** whose failed-cleanup state **refuses and reports rather than cleaning** — which **removes** a code path rather than adding one. **Neither R8 movement adds an artifact, an authority, a column or a refusal code.** **A new option A-2 is raised by remediation R8 and is what R8-D routes rather than adopts**: option A **plus an independent authenticated host-bound value** — a TPM-sealed or coordinator-signed host token — which is the only thing that would make falsification row **F-7** a refusal instead of residual **R-5.0-13**. It **would** add a seal field, a **V-W** step, a coordinator comparison, a refusal code beyond `SW-J25`, a §2.13.6 condition and a column in `sheet_writer_journal_generations`, and its principal price is that a **legitimate restore onto replacement hardware fails closed** in a design whose purpose is that evidence survives a restore. Because it changes the design surface it is the Acceptance Authority's under §0.2, on the Security Reviewer's and the Operations Owner's advice; **the implementer does not adopt it.** J-1 remains recommended; J-2, J-3 and J-4, the owners, the authorities and N5.0-23 are unchanged. The Security Reviewer's estimate rises to **3.0–4.0 reviewer-days** with **no added surface**, because the threat model is now nine authorities whose combinations must each be checked against real Unix DAC and there are now **two** unrefused residuals. **No new decision number is raised. Still not ruled** |

**Package 5.0 remains `not ready`.** D5.0-1 through D5.0-7 are closed. D5.0-8
remains open only for the Security Reviewer. Codex's remediation-R1 re-review
closed P5.0-R2, kept P5.0-R1 Blocking and raised Blocking P5.0-R4; the
remediation-R2 re-review kept both Blocking; the remediation-R3 re-review kept
P5.0-R1 Blocking and raised Blocking P5.0-R5. **Design remediation R4 was
submitted on 2026-08-29 and claims no finding closed** — for P5.0-R5 it replaces
the dispatch journal's storage, identity, integrity format, failure states and
privileged lifecycle and resolves the completeness contradiction by withdrawing
the false statement rather than the control; for P5.0-R4 it leaves the boundary
unchanged and claims no operational evidence passed; for P5.0-R1's Sheet half it
repeats that no barrier exists in the published Google APIs and returns a priced
decision. **The revision-5 re-review on 2026-08-29 kept P5.0-R5 Blocking**, on
four grounds: a circular seal/genesis construction, a writer denied the seal it
was told to validate, a capability probe that could not distinguish append-only
enforcement from ordinary permissions, and a Boolean database check credited with
proving a host fact. **Design remediation R5 was submitted on 2026-08-30 and
likewise claims no finding closed**; revision 6 corrects all four, and **P5.0-R4
stays open** pending security and operational evidence while P5.0-R2 stays
closed. **D5.0-9, D5.0-10, D5.0-11, D5.0-12 and D5.0-13 are open, each blocking
a work package.** Assumption A-5.0-3 (disposable Google resources) is
unconfirmed; **A-5.0-4 — a disposable operating-system identity and a `pg_hba`
reload — is unconfirmed and without it the whole R3-B evidence plan is
unproducible**; and **A-5.0-5 — a root-owned durable journal hierarchy, a
disposable probe arena, a `setpriv` identity drop and a *verified* `chattr +a` —
is unconfirmed and without it no capability probe can run, no generation can be
initialised and P5.0-R5 cannot close on evidence.**

**One open item cannot be resolved by a further design pass.** The barrier
P5.0-R1's Sheet half asks for does not exist in the published Google APIs, and
making the dispatch journal durable does not create one. What closes that half is
Peter's ruling on D5.0-9, or the Independent Reviewer evidencing a published
mechanism the search missed.

**One open item is genuinely the Data Owner's.** N5.0-23, inside D5.0-13, decides
when a sealed record of what the platform wrote to a live community's Sheet may be
destroyed. It is the first number in this package whose owner is not the
Operations Owner or the Product Owner.

The authoritative decision text is
[`docs/discovery/open-decisions.md`](../discovery/open-decisions.md). This file is
the management index: it identifies what remains actionable, who owns it and
which milestone it blocks. It does not restate or supersede a ruling.

| Decision | Status | Accountable role | Required before | Management action |
|---|---|---|---|---|
| OD-03 | Partly answered | Product Owner | Phase 5.3 | Close remaining downtime/living-cost behavior before package readiness |
| OD-04 | Partly answered | Product Owner | Phase 5.3 and Frank-interest job | Define remaining lender behavior and acceptance examples |
| OD-05 | Open | Product Owner | Phase 5.6 crafting | Rule whether fancy meals incur the downtime percentage |
| OD-09 | Open | Product Owner | Phase 5.5 learning | Set disguise/forgery learning cost policy |
| OD-16 | **Closed 2026-08-12** | Product Owner / Security Reviewer | Phase 3 | `/info` is ephemeral and limited to linked characters plus Guild Council |
| OD-17 | **Closed 2026-08-12** | Product Owner / Security Reviewer | Phase 3 planning | Attribute legacy mutations through the Phase 3 gate; the first post-acceptance deployment requires verified `character_access` and precedes every later feature deployment |
| OD-25 | Verification open | Operations Owner | Production readiness | Verify Foundry network exposure and record evidence |
| OD-28 | Partly implemented | Product Owner | Phase 5.5 | Define auditable tribute-item mechanism |
| OD-39 | Open | Product Owner / Security Reviewer | Phase 5.7/5.8 cutover | Close unauthenticated trade/sale mutation policy and interim control |
| OD-41 | **Closed 2026-08-02** | Product Owner / Acceptance Authority | Phase 2 remediation | ADR 0008 rejected; the controlled migration register assigns every Sheet-era field, including `character.downtime_progress`, to one typed owning package |
| OD-42 | **Closed 2026-08-02** | Data Owner / Acceptance Authority | Phase 2 remediation plan approval | Ruled: display names are not unique identities; multiple characters may share one; stable character IDs and external Actor IDs provide identity; any legacy name-based candidate lookup fails closed when more than one candidate exists. **No unique display-name constraint is added.** Closes I-05. Package R2 corrects the single-value claim lookup to return every candidate and refuse on more than one |
| OD-43 | **Closed 2026-08-13; design accepted at P3.G0** | Product Owner / Security Reviewer / Acceptance Authority | Phase 3 P3.G0 | Peter accepted [ADR 0010](../adr/0010-provider-neutral-identity-and-emergency-administration.md) and the complete remediated P3.0 baseline after Codex architecture/security re-review. Acceptance includes corrected N-43, widened N-65, new N-67, account-aware audit attribution, mapping provenance and R-38. P3.1 is authorized subject to its disposable-PostgreSQL readiness condition. |
| OD-44 | **Closed 2026-08-14** | Product Owner / Security Reviewer / Acceptance Authority | Phase 3 P3.G1 | Peter approved the durable one-way OAuth completion binding in the [I-07 decision](../review/phase-3-p3-1-sm-01-completion-binding-decision.md): a unique, required `sessions.oauth_transaction_id` for Discord OAuth plus an atomic `completion_claimed_at` claim in the provider-I/O-free session transaction. No reverse `oauth_transactions.session_id` is added. **Implemented 2026-08-14** as migration 0009 with the required PostgreSQL concurrency, constraint, rollback and mutation evidence; the unique index is scoped to non-rotated sessions so N-08 rotation remains possible, declared for confirmation in `../review/phase-3-p3-1-od-44-remediation-submission.md`. **Confirmed 2026-08-14** (decision record §8): Peter approves that scoped index as the authoritative interpretation, conditionally on rotation integrity — one successor per predecessor, a rotation's account, authentication method and OAuth binding equal to its predecessor's, only a live unrotated predecessor rotatable, atomic insert-and-revoke, deterministic concurrent rotation, no arbitrary session labellable a rotation, and break-glass rotations unbound. The same ruling covers the re-review finding that the claim did not bind the provider. Implemented 2026-08-14 in migration 0009 and the OAuth, session and provider boundaries; see `../review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md`. Independent and distinct security re-review remain required. |
| OD-45 | **Closed 2026-08-14** | Product Owner / Acceptance Authority | Phase 3 P3.G1/P3.G2 | Peter approved the [I-08 allocation](../review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md): service/constraint portions remain at P3.G1; direct-HTTP portions of TC-BG-05b/c/e are mandatory blocking evidence at P3.G2 against the real P3.2 routes. This is not a waiver and does not authorize early P3.2 work. |
| OD-46 | **Closed 2026-08-17; operational input confirmed** | Product Owner / Acceptance Authority | Phase 3 P3.G2 | Peter resolved the controlled-contract contradiction over where the Sheet-era identity link is written, in favour of **immediate activation**: an R-29 Guild Council confirmation creates the `character_access` row atomically with its audit events, and command **C-05 is withdrawn**. The same ruling records Google Sheets as temporary legacy migration input with no platform-runtime dependency, requires C-04's player-tab name to be supplied explicitly, and requires the duplicate-player-name defect to fail closed by refusing the whole C-04 run. Peter subsequently confirmed the one-time tab name as **`Players`**; `--player-tab Players` remains required and is not portal configuration. See [C-P3.2-A and C-P3.2-B](change-log.md) and the corrected contract text in `../contracts/phase-3-identity-migration-contract.md` §7.2–§7.7. **Extended 2026-08-17 by [C-P3.2-C](change-log.md):** the independent implementation review found that R-28 read a proposal's historical `confirmed` resolution as proof the link was still active, so a link revoked through R-26 was reported as active and counted as one. Peter ruled that §7.4's *"`confirmed` counts active links"* sentence stands and a **balanced `confirmed_revoked` bucket** is added beside it, with VM-10 reporting each confirmation's own link state from the exact `granted_access_id`. The confirmation itself is never rewritten and no decision state is added. **P3.G2 is not approved by any of these rulings** and remains open pending independent and security-focused re-review. |
| OD-47 | **Deferred 2026-08-17** | Product Owner / Security Reviewer | after Phase 3 | Whether one platform account may hold two active Discord identities. Retained deliberately under C-P3.2-A: the current behaviour fails closed (`AmbiguousProviderIdentity` answers `503` rather than guessing whose roles decide the account's capability), and that is the safe state to defer in. No schema constraint is added and none is removed. |

**OD-44 addendum, 2026-08-15 (no decision changed).** The OD-44 ruling's condition
that "only a live unrotated predecessor" may be rotated is recorded here as having
required two corrections to be true of the implementation, both now made and
neither yet re-reviewed: the rotation liveness predicates on 2026-08-14, and the
same class in the idle refresh on 2026-08-15, which additionally applied N-06's
idle window to break-glass sessions. The clarified reading of N-07, N-08 and N-15
that follows from the ruling is recorded in the numeric policy register; **no
accepted numeric value changed**, so this is an addendum and not a change request
under that register's §5. See
`../review/phase-3-p3-1-od-44-session-lifetime-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

**OD-44 addendum continued, 2026-08-15 later the same day (no decision changed).**
Codex's independent implementation and security re-reviews of that submission
returned one blocking finding: the idle-policy correction had been made in the
session service while the repository API still accepted a refresh duration and an
authentication method as independent arguments, so N-15's 15-minute window could
still be bypassed by a caller naming a break-glass row's true method beside N-06's
duration. The correction removes the duration from the API at both layers and
selects it inside the atomic statement from the persisted `auth_method`, using an
immutable validated policy injected once at the composition root. **No accepted
numeric value changed and no decision changed**; N-06 and N-15 keep their values and
configuration remains their source. This also reverses one alternative recorded as
rejected in change record C-P3.1-G — "deriving the idle duration inside the
repository" — on the ground that the objection was to adapter-owned *constants*,
not to configuration-owned policy consumed by the adapter. See
`../review/phase-3-p3-1-od-44-session-touch-policy-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

**OD-44 addendum continued, 2026-08-15, third entry of that day (no decision
changed).** Codex's independent re-review of the preceding submission returned one
blocking finding, and it is the same authority in a third position rather than a
new one. Removing `idle` and `expected_auth_method` from the repository API had
moved the method-to-duration pairing into `SessionIdlePolicy`'s public dataclass
constructor: a complete, duplicate-free, positive mapping assigning N-06's
60-minute window to *every* method satisfied every invariant that constructor
validated, so a repository built with it selected 60 minutes for persisted
WebAuthn and recovery-grant rows and N-15's 15-minute limit was bypassed again, up
to the 60-minute emergency absolute bound. Two statements in the preceding
submission — that no supported API could pair a method with another policy's
duration, and that policy was built once and injected — were false; the second was
false of the composition as well, since `SessionService` derived its own policy
while `WebComposition.services()` derived another for the repository. The
correction closes construction rather than adding a predicate: the policy has no
public constructor, its only factory takes `SessionSettings`, the mapping is
derived internally from `AuthMethod.is_break_glass`, and one instance is built at
the composition root and injected into both the repository and the service.
**No accepted numeric value changed and no decision changed**; N-06 and N-15 keep
their values, `SessionSettings` remains their sole source, and every pair of
values the configuration contract accepts — including an ordinary window shorter
than the emergency one — maps by method classification. No schema change and no
migration edit was required. See
`../review/phase-3-p3-1-od-44-session-idle-policy-construction-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

**OD-44 addendum continued, 2026-08-15, fourth entry of that day (no decision
changed).** Codex's independent re-review of the preceding submission returned
three counterexamples that survived it, and their combined lesson is recorded here
because it changed the *shape* of the implementation rather than a decision. (F1)
`from_settings()` validated only positivity while `SessionSettings` was a public
frozen dataclass with no construction-time validation, so an out-of-register
settings object was accepted and the derived policy gave both break-glass methods
sixty minutes; closing the policy's constructor was beside the point while the
numbers it read were unconstrained. (F2) The refresh SQL was generated by
iterating the policy's public, overridable `__iter__`, so a subclass inheriting
the supported factory replaced the mapping the database used while the
service-facing method still reported fifteen minutes — ordinary Python
subclassing, which the preceding submission wrongly characterised as out-of-scope
forgery. (F3) `SessionService` accepted a policy beside the repository and
required no relationship between them, so correct production wiring was a
convention rather than an invariant. The correction removes the extensible
boundary instead of guarding it: `SessionIdlePolicy` is deleted, `SessionSettings`
enforces the accepted register in its own constructor, `SessionRepository` derives
and owns the bounds, `SessionService` reads the repository's, and which window a
method receives is an explicit classification table that refuses an unclassified
method at startup rather than defaulting it. **No accepted numeric value changed,
no decision changed, no configuration variable was renamed and no deployment value
moved**; N-04, N-06, N-07, N-15 and N-66 keep their values and `SessionSettings`
remains their sole source, now validated at every construction rather than only at
environment load. No schema change and no migration edit was required. See
`../review/phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

**OD-44 addendum continued, 2026-08-15, fifth entry of that day (no decision
changed).** Codex's independent re-review of the preceding submission returned
**one** blocking counterexample, described from two perspectives — F1 in the
implementation review and S1 in the distinct security-focused pass. It is recorded
here because it is a lesson about where an accepted policy is *defined*, not about
what it says. `SESSION_CEILINGS` had given both enforcement gates the same bounds
and left each to state independently what a value of these fields may **be**:
`SessionSettings.__post_init__` required an actual `int`, never a `bool`, positive
and within its ceiling, while the derived-policy gate restated the rule as the two
ordering comparisons `value < 1` and `value > ceiling`. Two ordering comparisons
are not a whole-number rule — `float("nan")` makes both false — so a non-finite
`max_sessions_per_account` survived `SessionPolicy.derive()` and
`len(live) >= maximum` was false for every live-session count, leaving **N-66
inoperative**. The route was ordinary: `derive()` accepts `SessionSettings`
subclasses deliberately, so a subclass whose inherited `__post_init__` observes
the valid stored integer can answer differently on the single later derivation
read. The correction makes the rule **one runtime definition** rather than a third
restatement: `session_policy_problem`/`session_policy_problems` live beside
`SESSION_CEILINGS` in `application/web/config.py`, and both gates call them; the
accepted type is recorded in the numeric policy register as `int` and never
`bool`, with floats refused as a class. **No accepted numeric value changed and no
decision changed**; N-04, N-06, N-07, N-15 and N-66 keep their values and their
sole source. No schema change and no migration edit was required. See
`../review/phase-3-p3-1-od-44-session-policy-numeric-validation-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

## Baseline v1.7 — Freedom bot retirement, 2026-08-28

| OD | Decision | Ruling | Affects |
|---|---|---|---|
| OD-53 | Is the Freedom bot retained after the platform is complete? | **No.** The bot is deleted at the end of the migration, once the platform provides every player-facing behavior it provides and a player needs no manual step beyond required Council confirmations. Discord itself is **not** retired: OAuth authentication, guild/role verification, events, notifications and voice-state attendance evidence remain | `.agents/AGENTS.md` direction and non-deletion rule; plan §12.0 and new §15.2 with a terminal gate; Phase 8 must size the gateway presence attendance needs. **Phase 4 unaffected** |

## Phase 4 decisions ruled 2026-08-28

| OD | Decision | Ruling | Affects |
|---|---|---|---|
| OD-48 | Does Phase 4 add a physical ledger table? | **No.** Ledger in `domain/` plus a consumer-owned protocol and an in-memory reference adapter; durable idempotency reuses the existing `idempotency_keys` table under a Phase-4 scope. No migration, so the mandatory logical-schema artifact is not triggered | Phase 4 "transaction ledger"; the conditional PostgreSQL constraint/append-only/runtime-role evidence is reallocated to package 5.0 or 5.2 |
| OD-49 | The downtime unit in the shared domain | **Integer thousandth-days**, refusing anything else; Phase 4 leaves `/info`'s legacy rendering unchanged and creates no read adapter | Phase 4 value object; package 5.5 owns Sheet conversion, invalid-value handling and the real character-page consumer when it migrates Characters column I |
| OD-51 | The float-money defects in `/sale` and `/lc` | **Characterize, do not correct.** Tests record today's behaviour and name the defect and its owning package; no line of either path changes. The rules are verified correct — the defect is the arithmetic type | Phase 4 characterization and risk R-P4-2; packages **5.7** and **5.3** inherit the fix and must reproduce the PDF worked examples in integer copper |
| OD-50 | Are the Sheet's denomination counters a domain concept? | **No.** `domain/` models money as integer copper only; the four counters stay a labelled legacy representation and nothing normalizes a character's coins on read | Phase 4 "money uses integer copper" and the unchanged-output characterization; package 5.2 owns the eventual normalization of Characters P–S |
| OD-52 | The Phase 4 query boundary and `/info` | **Final amendment 2026-08-29: Phase 4 creates neither an `/info` rewrite nor an unconsumed temporary Sheet query/adapter.** The platform replaces `/info` with character pages. Package 5.2 introduces the wallet query and production adapter with that page as its real consumer; package 5.1 owns any transitional bot migration. | Phase 4 evidence comes from ledger/idempotent command execution; package 5.2 wallet read path; risk R-P4-3 remains with 5.1 if it migrates the command |

Recorded as change-log `C-P4-C` through final amendment `C-P4-F`; full rationale in
[`../discovery/open-decisions.md`](../discovery/open-decisions.md) and
[`../review/phase-4-package-plan.md`](../review/phase-4-package-plan.md) §5.
These rulings released the Phase 4 work that was subsequently delivered,
independently reviewed and approved on 2026-08-29 (change-log C-P4-L). P4-R1
through P4-R5 and D-04 are Closed. Phase 5.0 is the next package selected for
readiness planning; no Phase 5 implementation or cutover is authorized by this
decision index.

All other OD entries marked closed or ruled remain decisions, not open actions.
The Delivery Lead reviews this index before baselining every phase. A decision is
closed only when the authoritative OD entry records the ruling, date, rationale
and affected requirements; an implementation does not silently make policy.
