# Unresolved Decisions

**Current static-launcher disposition, 2026-10-01.** Peter Duscha accepted the
D2-R2 design after independent Codex review and decided LD-9 option (i): Codex
must independently decode the actual `.text` at D9-2 using its own decoder or
byte-by-byte manual derivation prepared without reading XD's table. Exercising
XD alone is not sufficient. `R4-D2-R1-1` is Closed as remediated at the design
level. LD-7 and LD-8 remain decided as recorded. PO-9 and PO-14 remain open;
no implementation or operational authority exists, and a separate M-14/I-7
assignment is required.
[Acceptance and LD-9 decision](../review/project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md).

**Current R3 disposition, 2026-09-29.** Peter Duscha accepted the bounded
`PosixFilesystem.create_file`/`openat` descriptor-release remediation after
independent review with no finding. Manifest version 26 and digest
`526dd446…` are accepted review inputs only. RP-11 remains unwired and unmet;
C-11 and the exact pinned launcher environment remain unresolved.
[Acceptance record](../review/project-review-2026-09-29-p5-r5-rp11-i1-r3-r3-posix-post-open-release-acceptance.md).

**Current RP-11 alignment disposition, 2026-09-29.** Peter Duscha accepted
Codex's independent review of the corrected Option-1 documentation alignment.
`RP11-I1-2`, `RP11-I1-R2-1` and `RP11-I1-R1-1` are Closed as superseded by the
accepted I1-R3 retained-alias design. This accepts no RP-11 implementation or
operational authority; RP-11 remains unwired and unmet.
[Acceptance record](../review/project-review-2026-09-29-p5-r5-rp11-option-1-alignment-acceptance.md).

**Current RP-11 disposition, 2026-09-28.** Peter Duscha accepted Option 1 for
the recorded unadmitted staging/final pair: metadata-only verification of the
two fixed names sharing one regular-file inode at link count two, with no third
name, no content read or digest and no admission. `RP11-I1-R3-1` is Closed by
that decision; `RP11-I1-R3-2` and `RP11-I1-R3-3` are Closed as remediated after
Codex's independent R2 review. Historical proposal and review text below that
calls the policy pending is superseded. RP-11 itself remains unwired and unmet,
and no operational authority or package-gate change follows.
[Decision record](../review/project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md).

**Current MD-4 disposition, 2026-09-23.** Peter Duscha explicitly accepted
`R-5.0-10` through `R-5.0-16` as active residual risks on their stated terms.
`R-5.0-12` through `R-5.0-16` now enter the current RAID register. Recovery
rehearsals for `R-5.0-11`, `R-5.0-14` and `R-5.0-16` remain mandatory
evidence. Historical text below that calls these risks pending or unaccepted is
superseded by this explicit decision.

**Current governance disposition, 2026-09-02.** Peter Duscha approved **OD-64
Option A**, **OD-65 Option B** and **OD-66 Option A / J-1** in all accountable
roles. **OD-62 remains Open** with G-A recorded only as a provisional direction
pending P5.0-R5 operational evidence and independent review. The older review
notes below that say OD-64 through OD-66 remain Open are retained as historical
state and are superseded on those three decisions. The approvals do not
authorize implementation and do not silently accept R-5.0-12 through
R-5.0-16.

**Phase 4 post-gate correction note, 2026-08-31.** P4-PG1 through P4-PG3
are Closed; P4-PG4 and P4-PG5 require one final bounded correction and Codex
re-review before Phase 5 preparation resumes. **No decision is created, closed
or changed by this work.** The defects have one safe implementation answer each
inside accepted Phase 4 policy, so they do not belong in the decision register.
OD-62 through OD-66 and Package 5.0's `not ready` state remain unchanged.

**Superseded as the active work item — Package 5.0 security review and
remediation R11, 2026-08-31.**

The §9.2
security pass ran and returned **changes requested with no readiness
recommendation**: **P5.0-SR1 (Blocking)** — the deployment integrity check can be
skipped silently, because both sides of its comparison come from the live
deployed bytes and no step refuses when the comparison against the reviewed
commit is omitted — and **P5.0-SR2 (Important)** — the operating-system identity
contract contradicted the journal group contract about `freedomjournal`.
**Revision 12 of the package plan and the logical schema remediates both and
claims neither closed. It decides no option and closes no decision.**

**OD-62 through OD-66 remain Open and must not be ruled from revision 12.** Two
of them change content and neither changes state. **OD-65's scope is extended**
by the reviewed-source provenance objects — a `root:root 0700` bare Git object
store, an out-of-band approved-revision record and a per-component provenance
record, all three new host objects, one a governance artifact needing a custody
procedure — and by the **canonical identity and group membership table**
provisioning must create in a stated order; its option set grows to four, and the
implementer's recorded assessment is that the new **option C**, which takes
everything except the provenance objects, **leaves P5.0-SR1 unremediated**.
**OD-66 gains option A-3** — a cryptographically signed approved-revision record
verified against a root-held keyring, which would narrow residual **R-5.0-15** —
**priced and deliberately not adopted**, on the same reasoning as option A-2.

**Nothing is closed and nothing is authorized.** P5.0-R5 remains Blocking
pending authorized operational evidence; P5.0-R1 and P5.0-R4 remain open;
P5.0-R2 remains closed; A-5.0-3, A-5.0-4 and A-5.0-5 remain unconfirmed and
A-5.0-5 is widened again; host check **C-1** remains not completed and **C-3**
and **C-4** not run; Package 5.0 remains `not ready`; and implementation,
migration, deployment, cutover and Package 5.1+ remain unauthorized. **An
independent security re-review of revision 12 is required.**

**Superseded — revision 11 independent re-review, 2026-08-31.** Codex identified no new
Blocking or Important design finding and considers R10-A through R10-C
materially addressed on paper. This decides no option and closes no decision.
OD-62 through OD-66 remain Open; P5.0-R5 remains Blocking pending authorized
operational evidence; Package 5.0 remains `not ready`; and implementation
remains unauthorized. **The Security Reviewer was named on 2026-08-31 — Codex —
closing OD-61; that assignment approves no option and closes no finding, and the
security recommendation itself is still outstanding.** The active
handover routes the next action to the accountable maintainers and reviewers,
not to implementation.

Status: Phase 0 deliverable. Sixteen of the 36 entries that existed then were
closed by maintainer answers on 2026-07-29 and 2026-07-30, including every
question that blocked Phase 1 or the architecture gate. Further entries have been
raised since; the list now runs **OD-01 to OD-66**, and every identifier is
unique. The remainder are marked with when they must be settled. The independent
Codex re-review approved Phase 0 on 2026-07-30, the maintainer accepted the
milestone, and the gate is closed.

Current delivery note (2026-08-28): the Phase 3 authentication, authorization
and web-security gate is approved and Phase 4 implementation is authorized.
The open decisions below retain their package-specific deadlines; Phase 4
authorization does not decide a later Phase 5 rule or cutover question early.

**Package 5.0 review note, updated 2026-08-31 for revision 12.** **Revision 12 is
the response to the security review's two findings, and it makes no policy
choice.** It adds a fail-closed reviewed-source provenance contract (package plan
§2.12.5a) binding deployment and generation registration to an **immutable
reviewed Git object** held in a root-owned bare store and to an **out-of-band
approval record**, with a **`NOT NULL` foreign key** to a new seventh table so an
unprovenanced generation cannot be registered and activation cannot be reached;
and it makes package plan §2.12.2 the **single canonical primary/supplementary
membership table**, withdrawing the isolation sentence that had been false since
revision 6. **The estimate rises to PERT 47.6 and the security review to 4.5–5.5
reviewer-days over twelve surfaces**, both decomposed. **Two residuals are
proposed and neither is accepted** — R-5.0-15 and R-5.0-16 — and **no finding is
claimed closed.** The provenance design's honest limit is stated rather than
argued around: **root remains inside the trust boundary**, and the signed
alternative is OD-66 option A-3, raised and **not adopted**. **No option is
adopted, and OD-62 through OD-66 remain Open and must not be ruled from revision
12.** Package 5.0 remains not ready, implementation is unauthorized, and **an
independent security re-review of revision 12 is required**.

**Superseded Package 5.0 review note, 2026-08-31.** **Revision 11 is the R10
response, submitted the same day, and it makes no policy choice.** It replaces
the E1–E8 launch recipes with a **`capsh(1)`** construction — `setpriv(1)` from
util-linux 2.39.3 rejects the securebit revision 10 used, and does not document
the option ordering every declared mask depends on — states exact UID, GID,
supplementary groups, permitted, effective, inheritable, ambient and bounding
masks **and securebits** for all eight identities with a complete invocation
each, and adds a mask-versus-recipe comparison that also records a third
recipe/mask disagreement the review did not name. Dependent evidence is
revalidated and **one control pair is redesigned**: `E6` replaces `E2` as the
isolating positive control in `JNL-50` case 7 and `JNL-49` case 11. **No case,
identifier, estimate, authority, falsification row, risk or schema object
changes**, and two stale copies of superseded wording in the logical schema are
corrected. **The `capsh` choice is an evidence-harness mechanism inside
unconfirmed assumption A-5.0-5** — it installs nothing, sets no file capability,
creates no set-user-ID artifact and changes no production tool — and it is routed
to the **Security Reviewer**, not raised as a decision here. **No option is
adopted, and OD-62 through OD-66 remain Open and must not be ruled from revision
11.** The Security Reviewer remains unnamed, Package 5.0 remains not ready,
implementation is unauthorized, and **an independent re-review of revision 11 is
required**.

**Superseded Package 5.0 review note, 2026-08-31.** Revision 10 was independently
re-reviewed and returned **changes requested**. R9-A and R9-B are materially
improved, but R9-C's E2–E6 launch recipes use a `setpriv` securebit the named
util-linux tool rejects, E8's recipe does not create its declared empty bounding
set, and E7 omits complete masks. Remediation R10 is documentation/design only
and makes no policy choice. **OD-62 through OD-66 remain Open and must not be
ruled from revision 10.** Package 5.0 remains not ready and implementation is
unauthorized.

**Superseded Package 5.0 review note, 2026-08-30.** Revision 9 was independently
re-reviewed and required documentation/design remediation R9. Its deployment-
digest, cleanup-state and forged-host-identity corrections were materially
addressed, but its authority model omitted the owner-or-`CAP_FOWNER` prerequisite
for `FS_IOC_SETFLAGS` and contradicted itself about whether A3 confers A2.
**Revision 10 is the R9 response, submitted the same day.** It redesigns the
authority register into **eleven** primitives — `A1` the `CAP_LINUX_IMMUTABLE`
half of `FS_IOC_SETFLAGS`, `A10` and `A11` its owner-or-`CAP_FOWNER` half over the
`freedomsheet`-owned journal and over the root-owned seal and archive — separates
the independence of those primitives from the fact that real holders bundle them,
and rewrites the executable evidence under identities with complete capability
sets. **Every corrected combination makes an alteration harder to construct**, so
no option's cost or benefit moves and **no option is adopted**. **OD-62 through
OD-66 remain Open and must not be ruled from revision 10.** Package 5.0 remains
not ready and implementation is unauthorized.

Phase 0 acceptance criterion: *"unresolved ownership questions are listed
explicitly"* (plan §12).

Most decisions below were reached during Phase 0 discovery, and none of them
**can be made by an agent**, because each one changes rules, data authority,
authorization, privacy, production behaviour or migration strategy — the exact
categories `.agents/AGENTS.md` requires an agent to stop for.

**Identifier note, 2026-08-01.** The music decision was recorded as a second
"OD-38" while OD-38 already meant *Initial authority during Sheet migration*.
The music decision is now **[OD-40](#od-40--music-platform-work--closed-2026-07-31-amended-2026-07-31)**;
[OD-38](#od-38--initial-authority-during-sheet-migration--closed-2026-07-31)
keeps its original meaning. Review documents written before that date may still
show the old number and are accurate records of what they said at the time.

## How to use this list

Each entry states the question, why it is open, what it blocks, and — where there
is one — a recommendation with its reasoning. Maintainers should record the
decision inline (or accept the recommendation), and the decisions in plan §17 must
be settled **before Phase 1 completes**.

| Urgency | Meaning |
|---|---|
| **Blocking now** | Phase 1 cannot start or finish without it |
| **Blocking Phase 2** | Import work cannot begin |
| **Blocking Phase 3+** | Needed later, but decide early if convenient |

---

## A. Google Sheet structure

### OD-01 — Are there other tabs? · **CLOSED 2026-07-30**

**There is a player-level tab, and it is in scope.** The maintainer:

> *"Only players and characters are relevant because last session, is DM, last time
> DMed, and campaigns are player based not character based."*

**Migration scope is therefore two tabs: `Characters` and the player tab.** Anything
else in the document is out of scope.

**This is a structural finding, not just a scope answer.** The sheet already
separates *player-level* facts from *character-level* facts, and the platform's
schema should mirror that split rather than flattening it:

| Level | Facts | Platform home |
|---|---|---|
| **Player** | last session, is DM, last time DMed, campaigns | `players` / platform users |
| **Character** | the 38 columns of `Characters` | `characters` |
| **Join** | `Characters` column **C** (Player Name) | `character_access` |

Three consequences:

1. **Column C is the foreign key**, not merely a helpful hint. The two tabs are
   already a normalised two-table model joined on player name, which is much closer
   to the target schema than Phase 0 assumed.
2. **`is DM` is authorization data that already exists.** Plan §4.1 needs a DM
   capability and [OD-18](#od-18--discord-guild-council-and-dm-role-snowflakes--closed-2026-07-31)
   asks which Discord roles grant it. There is an existing answer in the sheet to
   reconcile against — a per-player flag maintained by the people who actually know.
   It is *evidence*, not authorization: effective privilege still resolves from
   Discord role IDs server-side per
   [ADR 0004](../adr/0004-discord-oauth2-authentication.md).
3. **`campaigns` being player-based** matters for the mission/attendance model in
   Phases 6–8. A player belongs to campaigns; a character is played within them. The
   plan's mission records should attach campaign membership at the player level.

**Column headers supplied 2026-07-30 — the Sheet side of discovery is complete.**

`Player Name`, `Discord Name`, `Last date played`, `Active DM`, `Last date DMed`,
`Latest date to DM`, `Campaign Counter`, `No shows`. Full analysis in
[sheet-inventory.md §2.1](sheet-inventory.md#21-the-player-tab); three findings:

- **F-S5 — the Discord link already exists.** `Characters.C → player.A → player.B`
  completes `character → player → Discord`. It is a *username*, not a snowflake, so it
  seeds a Council-verified matching pass rather than granting authorization.
- **F-S6 — *Last date played* and *No shows* are recorded at both levels.** Probably
  player-level aggregates of the character rows, but that is an inference; the importer
  should compute the aggregate, compare, and report disagreement rather than trust
  either side.
- **F-S7 — *"Latest date to DM"* is a deadline with no rule behind it.** Nothing in the
  rule catalogue covers a DM rotation obligation. Either a hand-kept Council convention
  or a missing rule. Worth confirming before Phase 6.

*Import scope settled:* shop inventory, Moradinium accounting and mission logs are
confirmed out of scope.

*Closed.*

### OD-36 — What happens to the sheet macros at cutover? · **CLOSED 2026-07-31**

Raised 2026-07-30 by the answer to OD-07. **Two** timed Apps Script macros write to
the sheet: `+1` week to `J` weekly, and Frank's interest on `AC`. A third, the
living-cost→downtime grant, exists but is **switched off** — the bot does it.

They are **not in this repository**, not version-controlled, and will keep writing
throughout any verification or dual-run period.

Two problems to settle:

1. ~~**Overlap with the bot today.**~~ **Resolved 2026-07-30: the downtime macro is
   not active.** The bot alone grants the `+5` days (`models/lifestyle.py:62`), so
   downtime is **not** being granted twice. That was the one live-economy risk in this
   entry and it is closed.

   **Two macros remain active:** the weekly `+1` to `J` (living cost owed) and
   Frank's interest on `AC`.
2. **Cutover.** Either disable the macros and reimplement the accrual in the
   platform as a scheduled, audited, idempotent job — the accrual is a rule (§5
   p.12, §5.6 p.14) and belongs in the domain — or leave them running and record
   `J` and `AC` as **macro-owned** in the field-ownership matrix for the duration,
   with the platform reading and never writing them.

*Recommendation:* reimplement in the platform, because a Bastion turn or a week of
living cost must not be applied twice under retry (`.agents/AGENTS.md`), and a
timed spreadsheet script has no idempotency key. But **do not disable anything
before** the platform's equivalent is running and reconciled — the accrual is what
the whole living-cost economy rests on.

*Also worth a look while deciding:* whether the macro source is backed up
anywhere. It is currently a single point of failure holding live game rules.

**Maintainer decision, 2026-07-31:** reimplement both active macros—the weekly
living-cost accrual in column J and Frank's interest accrual in column AC—as
scheduled, deterministic, audited and idempotent platform jobs. Each Sheet macro
remains running and authoritative until its corresponding platform job is
implemented, tested, dry-run/reconciled against the Sheet, and approved for
cutover. At that per-macro cutover, disable the Sheet macro before enabling the
platform writer. The two writers must never operate concurrently after cutover.
Retain the Sheet and rollback procedure during the verification window.

**Maintainer amendment, 2026-08-02:** this supersedes the earlier requirement to
disable the Living Cost Sheet macro before enabling the platform job. After the
approved Living Cost authority cutover, PostgreSQL is the sole authority and no
database-backed path reads, reconciles or imports Sheet column J. The old Sheet
macro may be disabled as operational cleanup, but its continued execution
against the retired Sheet cannot affect PostgreSQL and is no longer a
dual-writer correctness risk. The platform schedule uses fixed IANA timezone
`Europe/Berlin`, initially Sunday at
04:00; only a currently authorized Platform Administrator may change its weekday
or local time. Inactive characters do not accrue. Following a schedule change,
the first occurrence under the new weekday/time is explicitly non-accruing and
the next weekly occurrence is the first that increments Living Cost. Eligibility
is evaluated from effective-dated active status at the nominal occurrence, not
from status when a delayed catch-up happens. Platform accrual history begins at
the authority-cutover instant; no earlier periods are synthesized. A schedule
change is refused until every overdue or failed period has been recovered and
the backlog is empty.

### OD-02 — What do the unmapped columns hold? · ~~Blocking Phase 2~~ **CLOSED**

**Answered by the maintainer 2026-07-30.** All eleven identified; the full 38-column
map with real headers is
[sheet-inventory.md §3](sheet-inventory.md#3-column-map--characters).

| Col | Holds | Consequence |
|---|---|---|
| B | Character Name (long) | Display attribute |
| **C** | **Player Name** | **The player↔character link already exists** — seed for `character_access` (F-S1) |
| O | Aristocratic lifestyle flag | As guessed — the §5.5 p.13 lock-out marker |
| U | Weekly Expenses | Reconcile against the computed lifestyle cost |
| AD | Background | Character detail |
| **AE–AH** | **Classes/Subclasses, Race/Species, Abilities, Feats/ASIs** | **Dual-recorded with Foundry** — a contested group the matrix did not have (F-S4) |
| AI, AJ | Special Notes, Mounts | Free text |

Two of these change design rather than merely filling a gap:

- **C** means Phase 3 seeds character access from existing data rather than from
  nothing. It is a *name*, not a snowflake, and one name per character where the
  invariant allows several users — so it is evidence for an audited linking pass,
  never authorization in itself.
- **AG (abilities)** means the platform can compute the Learning/Earning roll
  modifier from data it holds, replacing a number the player currently types in,
  **without waiting for the Foundry connector.**

*Closed.*

### OD-07 — Does any bot-written column contain a formula? · ~~Blocking Phase 2~~ **CLOSED**

**Answered by the maintainer 2026-07-30: there are no formulas in the sheet.**

Phase 0's hypotheses — badge, level, living weeks, downtime and Frank's interest as
formula candidates — were all wrong. **Phase 2 is a migration, not a repair.** The
bot's 26-cell whole-row write has never destroyed a formula, because there were
none to destroy.

**But the accrual is real, and it runs as timed Apps Script macros:** `+1` week to
`J` every week; `+5` downtime days when living cost is paid (the bot does this now);
and Frank's interest on `AC`. The weekly `+1` to `J` had never been documented
anywhere before this answer.

That makes the sheet a **three-writer system** — bot, Council, macros — where every
prior concurrency statement assumed two. It also gives the whole-row-write hazard an
automated trigger: a save writes `J` from its load-time value, so an accrual that
fires inside a command's read→write window is silently reverted.

Full analysis in
[sheet-inventory.md §4](sheet-inventory.md#4-formulas-and-macros). The remaining
decision is what happens to the macros at cutover — **[OD-36](#od-36--what-happens-to-the-sheet-macros-at-cutover--closed-2026-07-31)**.

*Closed, and it is the good outcome.*

### OD-08 — Downtime smallest unit and rounding · **CLOSED 2026-07-30**

**Maintainer ruling:** *"Crafting days are rounded to one digit after the dot."*

That answers the question directly. Standard-item crafting computes
`base_price / dt_div` (rules §6.5.2.3 p.22), producing arbitrary fractions —
`7/25 = 0.28`, `100/75 = 1.3333…`. Those are charged as **0.3** and **1.3**.

**Consequence: ADR 0005's eighth-days is withdrawn.** It was derived only from the
table constants and could not represent a tenth at all — the commonest crafting
path. The unit is now **thousandth-days** (`downtime_millis`), which represents every
relevant value exactly:

| Unit | `0.1` computed | `0.25` master common | `0.125` master cantrip brew |
|---|---|---|---|
| eighth-day *(withdrawn)* | ✗ | ✓ | ✓ |
| tenth-day | ✓ | ✗ | ✗ |
| **thousandth-day** | **✓** `100` | **✓** `250` | **✓** `125` |

Note that the code performs **no rounding at all today** — `dt_cost` stays a raw
float throughout `helpers/craft_calculator.py`. Applying the ruling is a small
behaviour change belonging to the Phase 5 `/craft` migration, not to Phase 0 or 1.

**Fully closed 2026-07-30.** Asked whether the fixed constants `0.25` and `0.125` are
charged exactly or rounded, the maintainer answered:

> *"Make the number exact. Maybe round after three digits, that should be enough."*

- **Table constants are exact** — `0.25` = `250` millis, `0.125` = `125` millis. No
  master-tier cost changes; the PDF is preserved verbatim.
- **Computed costs round to three decimals** — `100/75 = 1.3333…` charges `1.333`.

This supersedes the earlier *"one digit after the dot"*, which was given before the
computed/constant distinction had been put to the maintainer. The newer answer is the
specific one and the better outcome: **rounding to three decimals is rounding to the
nearest whole `downtime_millis`**, so the rule and the storage unit coincide — no second
rounding step between domain and database, and no value the rule can produce that the
unit cannot hold exactly.

*Closed.* [ADR 0005](../adr/0005-identifier-and-quantity-representation.md) is amended
and accepted.

---

## B. Rules corrections

**Resolved 2026-07-29.** The maintainer confirmed all five mismatches and ruled
that the PDF is the leading rules document. RC-02, RC-03, RC-04, RC-06 and the
CRP half of RC-09 are implemented; see
[rule-catalogue.md](../rules/rule-catalogue.md#summary-of-mismatches).

A follow-up ruling on the same day closed OD-11, OD-27 and OD-29 entirely and
settled the historical question on OD-10. **No community announcement is
required** — the maintainer assessed that neither corrected payout rule was ever
triggered in practice (see OD-10 and OD-11).

What remains open in this section is the untracked tribute item (OD-28), the
**legacy untagged CRP policy the RC-09 gate exposed (OD-34)**, and the per-command
questions OD-03, OD-04, OD-05 and OD-09.

### OD-10 — RC-02: natural-20 earning bonus is 50%, should be 20% · Blocking Phase 5.4

`models/resource.py:139` computes `Money(base_gold * 150)` = +50%. Rules §6.6
p.28 specify +20% (`* 120`). Over-pays 33.6 GP per natural 20 on the top band.

**Corrected: the code now applies +20%.**

**Resolved — no reconciliation, no announcement.** The maintainer assessed that a
natural 20 on `/work` has almost certainly never occurred, because the command
sees very little use. No player's recorded state is affected.

*Residual uncertainty, recorded honestly:* this is a judgement about usage rather
than a verified fact. The roll channel (`ROLL_CHANNEL_ID`) does receive every
roll, but `roll_dice()` emits an identical message format for `/work`, `/learn`,
`/mine` and `/sale`, so its history cannot cleanly attribute a natural 20 to
`/work`. If certainty is ever wanted, it would have to come from the sheet's
revision history instead.

### OD-11 — RC-04: special facilities, levels 5–8, aristocratic · Blocking Phase 5.9 / 10

`models/bastion.py:23` has `2`; rules §7.1 p.29 give `3`. One cell of thirteen
disagrees; every other cell matches. Under-charges maintenance by 5 GP per
accrued week.

**Corrected: the code now uses `3`.** The unrecognised-lifestyle default was
also changed from `1` to `0`, since the rules grant no allowance below a
comfortable lifestyle.

**Resolved — no historical impact.** The maintainer confirms that no character
has ever held an aristocratic lifestyle below level 9, so the incorrect cell was
never reached. The correction is forward-looking only and needs no announcement.

*Closed.*

### OD-26 — RC-06: masterpiece rarity unconstrained · Blocking Phase 5.6

Rules §6.3.3.1 p.17 specify *"a rare item of your choice"*. The code accepts any
rarity a Master may craft, and legendary interacts with the legendary
roll-progression branch in an undefined way.

**Corrected: `is_masterpiece` now requires `rarity == "rare"`**, which also
rejects the previously undefined legendary combination.

*Nothing further required.*

### OD-27 — RC-03: no 140% sale floor · Blocking Phase 5.7

Rules §4.2.1 p.12: *"The base selling percentage starts at the minimum of 140 %."*
A negative Persuasion total previously sold below 140%.

**Corrected: 140% is now a hard floor.** The haggling contribution is clamped to
`>= 0` before the 180% cap. Both PDF worked examples (p.11 and p.12) reproduce
exactly and are covered by tests.

*Nothing further required.*

### OD-28 — RC-09: Master rank prerequisite not enforced · Blocking Phase 5.5

Rules §6.3.3.1 p.17 require 100 CRP in the tool **and** crafting a free uncommon
item for the master before lessons begin. Neither is enforced; the Council catches
it manually.

**Partly corrected: the 100-CRP gate is now enforced** when a Master project
starts. Projects already under way are not retroactively blocked.

*Still open:* the tribute item (craft an uncommon item and give it to the master
free of charge) is **not** enforced, because nothing in the sheet records that it
happened. Enforcing it needs new persistent state, which belongs to the Phase 5
`/learn` migration rather than to a rule correction.

*Decide:* does the tribute item stay a Council check, or should Phase 5 add state
to track it?

### OD-34 — Legacy untagged CRP and the 100-CRP Master gate · **RULED 2026-07-30**

**Maintainer ruling:** *"We will decide on any CRP not connected to a tool once in
the beginning. Actually I don't think this is an actual real issue."*

**Related ruling, 2026-07-30 — both column W formats are acceptable.** *"I have no
issue with Tool: CRP format, we have both. It will be all right as everyone can see
it and we got no complaints."* So `7.5 (Brewer)` and `Brewer: 7.5` coexist by design;
the parser reads both, and which one a save writes back is a **cosmetic** choice, not
a correctness one.

**This ruling covers the format, not the loss.** The two are separable and only the
first is cosmetic: before the 2026-07-30 fix, a `/craft` did not merely rewrite the
notation, it **dropped every other tool's balance and reset the crafted tool to the
new award alone** (`7.5 (Brewer), 2.5 (Calligrapher)` → `Brewer: 2.5`). That is
invisible to a reader who does not remember the prior value, which is consistent with
no complaints having been raised. The parser fix stops it; what was already
overwritten is only recoverable from Sheets version history.

Recorded as **option (a), lightweight**: untagged CRP is resolved **once, by hand,
at import** rather than by a code policy. Current behaviour stays as-is until then.

The ruling is well-founded, and the 2026-07-30 format finding is why: the canonical
form of column W is **per-tool** (`7.5 (Brewer)`), so the untagged `general` bucket
only arises from a bare number with no tool at all. It is a rare legacy shape, not
the normal case — which is exactly what makes a one-time manual assignment the
proportionate answer instead of a migration project.

**Consequently unchanged:** the `general` fallback in `get_tool_crp()`
(`models/skills.py`) stays, `test_untagged_legacy_total_counts_for_any_tool` stays,
and the Phase 2 importer must surface any bare-number cell in its report for the
one-time assignment.

**One consequence of the ruling, recorded 2026-07-30 while fixing the Codex re-review
findings:** the `general` bucket counts for a tool only while it is the **sole** entry,
so the first per-tool award a legacy character earns shadows their untagged total —
`120` plus a 2.5 Smith award reads 2.5 at the gate, not 122.5. That is a direct
consequence of resolving untagged CRP by hand rather than in code, and it makes the
import assignment time-sensitive for any character still holding a bare number. It is
pinned by `test_an_award_beside_an_untagged_legacy_total_shadows_it`, which records it
as the ruling's consequence rather than as intended behaviour. The `Painter`-style abbreviation problem in
[OD-06](#od-06--tool-identity--resolved-2026-07-30-residual-free-text-validation) is the
*sharper* version of this concern and is still open.

*Closed as a policy question. Retained below for the reasoning and for the import
report requirement.*

---

Original write-up, 2026-07-29. **This was an ambiguity, not a recommendation — the
code embodied one reading of the rules and it might have been the wrong one.**

**The rule.** §6.3.3.1 p.17: a master takes a student on once they have
accumulated 100 crafting reputation points **with that tool**. CRP is per-tool by
rule.

**The data.** Column W has two historical encodings
([sheet-inventory.md §3.2](sheet-inventory.md#32-column-w--crafting-reputation-points-crp)).
A per-tool list (`Smith: 40, Alchemist: 12.5`) parses into `crp_dict` keyed by
tool. But a **bare number** — the older encoding, written before per-tool
tracking existed — parses into the single untagged bucket
`crp_dict = {"general": n}`. That bucket carries no record of which tool earned it.

**What the code currently does.** `Skills.get_tool_crp()` (`models/skills.py:232`)
returns an exact per-tool match if one exists. Failing that, if `crp_dict` is
*exactly* `["general"]`, it returns the untagged total **for whichever tool was
asked about** (`models/skills.py:241`). So a character whose sheet reads `120`
satisfies the 100-CRP Master prerequisite for **any** tool — including one they
have demonstrably never used. Once any per-tool key exists alongside `general`,
the fallback stops applying (`test_untagged_total_is_ignored_once_tools_are_tracked_separately`).

**Why it may be wrong.** It grants a Master prerequisite the rule ties to a
specific tool, on evidence that does not identify a tool. It is permissive in the
one direction the rules are strict about, and §6.3.3.1 permits one Master rank
*for life* — so an incorrectly granted Master rank is not correctable by a later
ruling.

**Why it was written that way.** It preserves existing production behaviour for
characters whose reputation predates per-tool tracking. Removing it without a
migration would silently revoke a prerequisite those characters may legitimately
hold, mid-project, with no notice.

**The maintainer must choose. Options, with what each costs:**

| Option | Behaviour | Cost |
|---|---|---|
| **(a) Council assignment** | Untagged CRP counts for **no** tool. The Council migrates each legacy balance to a named tool as an audited action; `get_tool_crp()` drops the fallback | Correct by the rule, and auditable. Needs a Council pass over every legacy row **before** the gate is safe to enforce strictly, and blocks affected players until then |
| **(b) Grandfather** | Untagged CRP counts as today, but only for characters holding it **at a recorded cutoff date**; anything written afterwards must be per-tool | Nobody is blocked. Requires a cutoff and per-character state to record it, and still permits one wrong-tool Master grant per legacy character |
| **(c) Interim Council review** | Untagged CRP never auto-satisfies the gate; the command refuses and directs the player to the Council, which rules case by case | No migration project, no wrong grant. Manual work per case, and a worse player experience |
| **(d) Status quo** | Keep the current fallback as a documented, accepted deviation | Zero work. Accepts that a legacy balance can satisfy the gate for an unrelated tool |

*Also decide, whichever option is chosen:* whether the RC-09 gate belongs at
**project start** (current behaviour, which deliberately lets pre-existing
under-qualified Master projects finish) or on **every roll**.

*Resolved above by the 2026-07-30 ruling: option (a), applied by hand once at
import.* `get_tool_crp()` and
`test_untagged_legacy_total_counts_for_any_tool` are unchanged.

### OD-29 — RC-07: CRP suppressed once any tool is mastered · Blocking Phase 5.6

`ext/commands/craft.py:84` awards zero CRP if the character holds a Master rank in
**any** tool. The rules track CRP per tool and say nothing about this. Commit
`3f41a2e` suggests it was deliberate.

**Resolved 2026-07-29 — the current behaviour is correct.** The maintainer's
reasoning:

> The PDF says you can be master in one tool only, so gaining more CRP doesn't
> make sense.

This derives from the rules rather than overriding them. §6.3.3.1 p.17 gives CRP
one purpose — a master contacts you at 100 points in a tool — and limits a
character to one Master rank for life. Once that rank is held, further CRP can
never be spent, so tracking it would be meaningless.

The rationale is now recorded in `helpers/craft_calculator.py` and
`ext/commands/craft.py`, and locked in by tests that warn against "fixing" it
from the CRP table alone.

*Closed.*

### OD-03 — Is downtime granted by paying LC? · Blocking Phase 5.3 — **mostly answered**

`models/lifestyle.py:62` grants `weeks * 5` downtime when LC is paid. Rules §6
p.14 say DT is awarded every Sunday by the Guild Council, independently.

**Answered 2026-07-30.** The maintainer: *"Every week every Character has to pay
living cost. When they are paid, 5 days of Downtime are added (this is actually now
done by the Bot)."* So downtime **is** granted by paying, the current code is
correct, and the weekly `+1` to column `J` is what tracks weeks owed.

*One thing left to confirm:* there is also a **macro** that grants the `+5`
(see [OD-36](#od-36--what-happens-to-the-sheet-macros-at-cutover--closed-2026-07-31)).
If both the macro and the bot are active, downtime may be granted twice for the
same week. **Worth checking before anything else in this list** — it would be a live
economy bug, not a migration concern.

### OD-04 — Frank the Money Lender · Blocking Phase 5.3 — **partly answered**

Rules §5.6 p.14 define 20% weekly interest and collection above 500 GP.
`Actor.debt` and column `AC` exist and are entirely unused **by the bot**.

**Answered 2026-07-30:** column AC is *Frank*, and interest **is** applied today —
by a timed macro, not a formula and not the bot. So the debt economy is live; only
the bot is unaware of it.

*Still to decide:* whether the platform takes over the interest accrual (see
[OD-36](#od-36--what-happens-to-the-sheet-macros-at-cutover--closed-2026-07-31))
and whether it enforces the 500 GP collection threshold.

### OD-05 — Do fancy meals cost 5% downtime too? · Blocking Phase 5.6

Rules §6.5.4.1 p.26: a fancy meal *"costs just 5% of a regular consumable to
craft"*. The code applies 5% to GP only. Genuinely ambiguous.

### OD-06 — Tool identity · **RESOLVED 2026-07-30** (residual: free-text validation)

`_clean_tool_name()` reduces a tool to its first word with the possessive
stripped, so `Painter's Supplies` → `Painter`. Is the canonical identity the full
tool name or the short code?

*Recommendation:* a controlled vocabulary of short codes
([ADR 0005](../adr/0005-identifier-and-quantity-representation.md)), with the full
name as a display label. The current heuristic collides on any two tools sharing a
first word.

**Answered 2026-07-30, and the answer is a clean rule.** The maintainer:

> *"Y is the tool, W, X is the artisan (e.g. Weaver's Tools - Weaver)."*

So the sheet deliberately uses **two vocabularies**, one per column group:

| Column | Vocabulary | Example |
|---|---|---|
| **Y** Tool Proficiencies | the **tool** | `Weaver's Tools` |
| **W** CRP, **X** Crafting Skills | the **artisan** | `Weaver` |

`_clean_tool_name()` is therefore not a lossy heuristic that happens to work — it is
**the documented bridge between the two vocabularies**, converting a tool name to
its artisan. Verified across all 22 `TOOL_CHOICES`: `Alchemist`, `Brewer`,
`Calligrapher`, `Carpenter`, `Cartographer`, `Cobbler`, `Cook`, `Glassblower`,
`Herbalism`, `Jeweler`, `Leatherworker`, `Mason`, `Painter`, `Poisoner`, `Potter`,
`Smith`, `Tinker`, `Weaver`, `Woodcarver`, `Disguise`, `Forgery`, `Thieves` — every
one is the correct artisan for its tool.

The earlier `(Calligraph)` alarm was shorthand in chat, not a sheet value: the
artisan for `Calligrapher's Supplies` is `Calligrapher`, and that matches.

**Resolution for the schema.** Identity is the **artisan code**; the tool name is a
display label attached to it. One `tools` vocabulary table with both, keyed on the
artisan code, and column Y normalises into it on import. This is what
[ADR 0005](../adr/0005-identifier-and-quantity-representation.md) means by
*"controlled vocabulary keyed by a tool code"* — now with the two names distinguished
rather than conflated.

**What stays open, and it is smaller than it was.** W, X and Y remain free text, so
a genuine typo or a non-canonical artisan still resolves to **0.0 silently**, and the
RC-09 Master gate reads that value. The import must therefore reject an unrecognised
artisan and report the row rather than defaulting — not guess. Current behaviour is
pinned by `test_an_abbreviated_tool_name_silently_resolves_to_zero`, which is
retained as a description of the hazard. It must **not** be "fixed" with prefix
matching: that would silently merge `Painter`/`Potter`-style collisions instead of
failing loudly.

**Applied 2026-07-30 (Codex re-review, *Important*).** Writes now use the same bridge
as reads: `Skills.add_tool_crp()` resolves the artisan with `_clean_tool_name()`, so a
CRP award lands on the existing entry rather than adding a second spelling of the same
artisan, and duplicate spellings already in a cell are folded into one. This closes the
*write* half of the identity question; the residual above is about unrecognised
free-text values, which remains an import-validation problem.

**Boundary confirmed 2026-07-30 (second Codex re-review, *Blocking* — F-S3c).**
Duplicate CRP entries that differ **only in case** are now summed at read time, since
case is not an identity question. The bridge is deliberately **not** applied at read
time: it collapses a name to its first word, so merging on it would silently commit a
free-text cell to that collapse — including for an unrecognised artisan, which the
residual above says must fail loudly at import rather than be guessed. `Smith` beside
`Smith's Tools` therefore still reads as two entries and is folded only when
`add_tool_crp()` awards CRP for that tool. See
[sheet-inventory.md §3.2 F-S3c](sheet-inventory.md#32-column-w--crafting-reputation-points-crp).

### OD-09 — Disguise and forgery kit learning cost · Blocking Phase 5.5

Rules §6.3.3.4 p.18: the NPC *"will agree on a price with you"*. The code
defaults to 10 GP. Is 10 GP the intended default, or should the override be
mandatory for these two?

---

## C. Data ownership

### OD-13 — Contested field groups · **CLOSED 2026-07-31**

Four groups need explicit ownership rulings. Full analysis in
[field-ownership.md](../rules/field-ownership.md).

| Group | Question | Recommendation |
|---|---|---|
| ~~**Electrum**~~ | ~~Foundry has `ep`; the Sheet and the rules do not~~ | **CLOSED 2026-07-30.** The maintainer confirms no actor holds electrum and the game does not use it, so all three systems agree. A nonzero `ep` is an **anomaly**: warn and refuse, never convert. Note also that **`Electrum` is a badge tier name** (rules §3 p.8–9) — a `Electrum` in Sheet column **E** is a badge, not currency, and the two must never be conflated by a name match |
| **Notable items** | Automated Foundry↔Sheet matching, or Council linking? | Council linking. Fuzzy name matching fails worst on the high-value items where a mistake matters most |
| **Languages** | Which code table; who owns additions? | Platform code table seeded from the `/learn` dropdown plus rules §6.3.1 p.16; Council owns additions |
| **Weapon proficiencies / masteries** | Platform-granted or Foundry-recorded? | Platform-granted — rules §6.3.2 p.16 make them a downtime purchase |

**Maintainer decision, 2026-07-31:** notable inventory, languages, and weapon
proficiencies/masteries are **Council-approved shared**. A Guild Council member
imports the Foundry representation; the import creates reviewable proposals and
nothing changes authoritative platform state without Council approval. Notable
items use Council linking rather than automatic fuzzy matching. Languages use
the platform code table with Council-controlled additions. Self-approval follows
OD-32 and is explicitly auditable.

### OD-15 — Who owns character level? · **CLOSED 2026-07-30**

Plan §6.1 puts level under Foundry. Rules §3.1 p.9–10 derive it from cumulative
mission count, and rules §2.1.1 p.3–4 plus `.agents/AGENTS.md` require Council
approval with **no automatic advancement**.

If Foundry owns level, a player editing their own Foundry sheet grants themselves
a level and the platform imports it. If the platform owns level, the two disagree
whenever a player levels in Foundry before approval.

**Maintainer decision:** **Council-approved shared.** The platform computes the eligible
level from mission count; Foundry reports the actual level; a mismatch becomes an
approval proposal. Satisfies the invariant without pretending Foundry is not where
levelling happens.

### OD-16 — Should `/info` remain unrestricted? · Blocking Phase 3

`/info` has no channel restriction and no authorization, and replies
non-ephemerally. Any guild member can read any character's full financial state
from any channel.

*Decide:* leave open (a deliberate transparency choice), make ephemeral, or scope
to linked characters plus Council.

**Closed 2026-08-12 — maintainer ruling.** `/info` is scoped to characters linked
to the authenticated user, with Guild Council permitted to inspect any character,
and its Discord response is ephemeral. It is not a public financial-transparency
surface. Server-side object authorization remains mandatory; hiding a character
in a selector is not authorization. Peter Duscha accepted this recommended policy
when releasing Phase 3 readiness planning.

### OD-17 — How long may the bot remain unauthorized? · Blocking Phase 3 planning · **ESCALATED 2026-07-31**

Phase 3 gives the **web app** authorization. The bot keeps its current
no-ownership-check behaviour until each command is migrated in Phase 5.

*Decide:* is that acceptable for the Phase 3–5 window, or should a
`character_access` check be back-ported to the bot as soon as the table exists?

*Recommendation:* back-port as soon as `character_access` is populated. It is a
small change at the cog boundary, and it closes the largest live authorization
gap months earlier than Phase 5 would.

**Escalated by the Codex project review of the Phase 2 submission, 2026-07-31.**
The review classifies the gap as a serious, live authorization risk rather than
merely scheduled work: `/info`, `/trade`, `/sale`, `/craft`, `/xchange`, `/lc`,
`/learn`, `/mine`, `/work` and `/bastion` all accept an arbitrary character name
and act on it, and a channel restriction is not authorization.

**Maintainer ruling, 2026-08-01 — which gate this belongs to.** OD-17 is a real
authorization risk and it stays open. It must be resolved **before Phase 3
planning, and before any affected legacy bot mutation is migrated or cut over.**
It is **not** a Phase 2 import blocker:

- the exposure is in the legacy Discord command surface and predates Phase 2;
- the Phase 2 importer neither introduced nor widened it. It writes no
  `character_access` row, no `discord_users` row and no authorization state at
  all, and no Discord command calls any code it added;
- the approved Phase 2 review gate is *data integrity and migration safety* for
  import/reconciliation (plan §12), and this finding is outside it.

Treating it as a Phase 2 blocker created a sequencing deadlock: the containment
options below all depend on identity links that only Phase 3 can create, so
Phase 2 could never be approved and Phase 3 could never start. **Nothing about
this ruling reduces the risk or declares it fixed** — it records which gate the
decision belongs to.

**Why an agent cannot close it, precisely.** There is nothing to authorize
*against*. `character_access` exists as a table with a schema, no rows, and no
writer. The only Sheet-side link is column C, a free-text **player name** —
`F-S1` and [OD-13](#c-data-ownership) both record that it seeds a
Council-verified pass and is not itself authorization. Building a
name-to-Discord mapping in the bot would be exactly the insecure shortcut this
document exists to prevent, and Phase 3 is where verified links are created.

**Containment options while that remains true**, with what each costs in
production. Recorded here because the choice is a production-behaviour decision:

| Option | Change | Consequence |
|---|---|---|
| **(a) Document and accept** | None in code. The gap is recorded as a known, accepted risk until Phase 3 | Zero disruption. Any guild member can continue to move any character's money. This is the status quo, made explicit |
| **(b) Ephemeral reads** | `/info` replies ephemerally instead of publicly | Stops one member reading another's finances into a shared channel. Costs the current transparency, which may be deliberate — that is [OD-16](#od-16--should-info-remain-unrestricted--blocking-phase-3). Does not touch mutations |
| **(c) Council-only mutations** | Gate the nine mutating commands on the Council role snowflake from [OD-18](#od-18--discord-guild-council-and-dm-role-snowflakes--closed-2026-07-31) | Closes the mutation gap immediately and completely. Also stops every ordinary player using `/work`, `/craft`, `/lc` and the rest — the bot's entire day-to-day purpose — until Phase 3 links exist. Implementable today |
| **(d) Disable the highest-risk commands** | `/trade` and `/sale` only, per [OD-39](#od-39--unauthenticated-economy-mutations-through-trade-and-sale--raised-2026-07-31) | Closes the currency-creation path, leaves downtime commands working. Trades and sales revert to whatever manual process preceded the bot |
| **(e) Announce, don't block** | Every mutation posts a non-ephemeral record naming the acting Discord user and the character | No authorization, but the Council can see who did what. Detective rather than preventive; needs no identity link because it records the *caller*, which Discord already supplies |

*Recommendation:* **(e) now, (c) at the moment `character_access` has rows**, and
(b) folded into whatever OD-16 decides. (e) is the only option that reduces risk
without either breaking play or asserting an identity link the platform does not
have; it makes an abuse attributable and visible on the day it happens rather
than at the next audit. It is a genuine change to production behaviour and is
therefore not made without this decision.

*Needed from:* a maintainer, before Phase 3 planning and before any affected
legacy bot mutation is migrated or cut over. Not required to approve Phase 2.

**Closed 2026-08-12 — maintainer ruling.** Adopt the staged recommendation:

1. while verified `character_access` links are not yet populated, every legacy
   bot mutation posts a non-ephemeral attribution naming the acting Discord user,
   character and action; this is a detective interim control and is not described
   as authorization; and
2. the attribution control remains in force through the Phase 3 gate; immediately
   after Phase 3 acceptance, the first post-acceptance deployment back-ports the
   active `character_access` check to every affected legacy command boundary
   (with the separately approved Council capability where applicable). No later
   phase feature deployment and no affected Phase 5 mutation cutover may precede
   that deployment.

Peter Duscha accepted the recommendation when releasing Phase 3 readiness
planning and fixed the transition at **after Phase 3 acceptance** on 2026-08-12.
The Phase 3 plan must prepare the back-port, its command matrix and its tests so
the first post-acceptance deployment can enforce it without an open-ended
intermediate state.

### OD-39 — Unauthenticated economy mutations through `/trade` and `/sale` · **RAISED 2026-07-31**

Raised by the Codex project review of the Phase 2 submission. Distinct from
OD-17 because it is about **what evidence a value must have**, not only about
who may act.

**What the code does today.** Both are documented existing behaviour with a
rule behind them, so neither is a defect to be fixed by an agent:

- `/trade` with `Shop` or `Store` on one side loads and writes only the other
  side. Selling to the shop therefore **creates currency** and buying from it
  destroys currency. That is what an NPC vendor is, and §4.1 p.10 and §4.2 p.11
  describe the guild shop and player-to-player deals as manual arrangements the
  bot merely records.
- `/sale` takes the item name, crafting cost, material value, quantity and
  Persuasion modifier from the caller. It verifies none of them: not that the
  character owns or crafted the item, not that the cost is the item's real
  crafting cost, not that the Persuasion modifier is the character's. §4.1/§4.2
  define the *percentage*, not the provenance of the inputs.

So the bot is a **recording instrument for a Council-supervised process**, and
its inputs are trusted because the people typing them are. The review's finding
is that the platform is becoming the authority, and an authority cannot trust
its inputs the way a shared spreadsheet could.

**The classification the platform needs, and only a maintainer can give.** For
each value: may a player supply it, must it come from authoritative character or
game state, or does it need Council approval?

| Value | Could come from | Question for the maintainer |
|---|---|---|
| `/sale` item | caller, or inventory | Must a sale name an item the character actually holds? Column AA records *notable* items only, so most sold goods are not recorded anywhere |
| `/sale` crafting cost | caller, or the `/craft` that produced it | Should a sale be linked to a crafting record, so the cost is the one the rules computed rather than one typed in? |
| `/sale` material value | caller | Same question, and it is added to the price directly |
| `/sale` quantity | caller | Is an upper bound wanted? There is no rule for one, and the current command accepts any positive integer |
| `/sale` Persuasion modifier | caller, or ability scores + proficiency | Sheet column **AG** now holds abilities ([OD-02](#od-02--what-do-the-unmapped-columns-hold--blocking-phase-2-closed)), so the platform *can* compute this without waiting for Foundry |
| `/sale` point of sale | caller, gated on a role **name** | `your own shop` adds **20 percentage points** to the sale price. It is the one authorization check either command makes, and it matches `r.name.lower() == "shop owner"` on the caller's roles. A role name is presentation (plan §4.1, `.agents/AGENTS.md`), and renaming the role silently removes or grants the bonus. The snowflake [OD-18](#od-18--discord-guild-council-and-dm-role-snowflakes--closed-2026-07-31) asked for is **still outstanding**; until it exists this cannot be moved to a stable ID |
| `/trade` shop side | caller | Should crediting a character from `Shop` require Council approval, or a Shop Owner role, or stay open? |
| `/trade` counterparty | caller | Should the *other* character's owner have to confirm? Today one player can move another's money in both directions |

**What was changed here, and what was not.** Only input validation that needs no
ruling: `/sale` now refuses a non-finite cost, which previously passed the
`< 0` check and failed obscurely inside the money arithmetic. Nothing about
provenance, approval or authorization was changed, because every one of those is
a rule or policy decision.

*Fail-closed containment available today, if wanted before the classification
exists:* refuse `/trade` where either side is `Shop`/`Store` unless the caller
holds the Council role, which stops unbacked currency creation while leaving
player-to-player trades working. This would visibly change production
behaviour for the shop workflow and is not applied without a decision.

**Maintainer ruling, 2026-08-01 — which gate this belongs to.** OD-39 is a real
game-policy and data-provenance decision and it stays open. It must be resolved
**before Phase 5.7 (`/sale`) and Phase 5.8 (`/trade`)**. It is **not** a Phase 2
import blocker:

- both behaviours are existing, rule-backed production behaviour that predates
  Phase 2;
- the Phase 2 importer neither introduced nor worsened them. It imports identity
  only — display name, long name, level and the active flag — and touches no
  currency, no inventory and no sale or trade path;
- the approved Phase 2 review gate is *data integrity and migration safety* for
  import/reconciliation (plan §12), and the provenance of `/sale` and `/trade`
  inputs is outside it.

The one Phase 2-era change to `/sale` — refusing a non-finite `cost` — is input
validation that needs no ruling and is unaffected. **This ruling does not fix or
reduce the risk**; it records when the classification table below must be
answered.

*Needed from:* a maintainer, before Phase 5.7 (`/sale`) and Phase 5.8
(`/trade`). Not required to approve Phase 2.

---

## D. Foundry

**Resolved 2026-07-30.** Maintainer answers closed OD-12 and OD-14 and the
electrum half of OD-13. **OD-30 remains the only open Foundry item**, and it is the
last thing gating the Foundry half of Phase 2.

### OD-12 — Which Foundry instance is authoritative? · ~~Blocking Phase 2 and 7~~ **CLOSED**

Phase 0 reported that three instances (ports 30001–30003) each held a world
directory named `the-guild`, and concluded that a maintainer had to declare one
authoritative or risk importing a stale parallel copy of every character.

**The premise was wrong.** The maintainer clarified that the game *The Guild* is
shared: `/home/foundry/shared/worlds` is bind-mounted onto each instance's
`foundrydata/Data/worlds`, so all three see the same directory. Verified — all
three paths to `the-guild` resolve to **inode 4388511 on device 64769**, and
`/etc/fstab` declares the binds.

**Resolution: there is nothing to choose.** One world, three front doors. No
stale-copy risk exists. The consequences are recorded in
[foundry-mapping.md §3](foundry-mapping.md#3-topology-one-shared-world-behind-three-instances)
and [ADR 0006](../adr/0006-foundry-integration-boundary.md), and they simplify the
design:

- `external_worlds` keys on **world ID**, not (instance, world ID) — composing the
  instance in would split one world into three phantom identities and generate
  spurious differences between them.
- The instance is **connection configuration**, repointable without touching world
  or actor identity.
- **One** service principal, not three.

*Also confirmed:* the Actor folder is `Characters (active)` and there are no
sub-folders.

*New operational constraint, not a decision.* LevelDB takes an exclusive lock, so
only one instance can host `the-guild` at a time; a second launch fails cleanly
rather than corrupting anything (local ext4, so the lock is effective). The
connector must therefore be repointable by configuration and must not assume port
30001. Recorded as topology **F-2a**.

*Closed.*

### OD-14 — Supported Foundry and dnd5e version range · ~~Blocking Phase 7~~ **CLOSED**

Verified baseline: core `14.365`, system `dnd5e` `5.3.3`, system compatibility
`minimum 13.347 / verified 14`. Observed 2026-07-30: all three instances run that
same tuple, but the Foundry binary and the `systems/` tree are **per-instance**
(`/home/foundry/dist/foundryN/`), so they are independently upgradable against the
one shared world.

**Resolved 2026-07-30; superseded 2026-08-27 by controlled baseline v1.6.** The
connector remains single-deployment and non-distributed, but Peter Duscha
explicitly authorized scoped compatibility ranges after the 14.365 → 14.367
operational upgrade and EX-11 review:

| Aspect | Policy |
|---|---|
| Supported deployment | World ID `the-guild` and system ID `dnd5e` match exactly; Foundry core must be numeric `14.x`; dnd5e must be numeric `5.3.x`. Reference versions remain configuration-supplied, not hard-coded policy |
| On mismatch | **Fail closed**, with a diagnostic naming observed and accepted series. No degrading, guessing or partial import |
| On upgrade | An in-range build/patch may proceed through the normal validation path. A Foundry generation change, dnd5e minor/major change, identity change or malformed version stops synchronization pending a new controlled decision |
| Backwards compatibility | None owed — there is no third-party consumer |

*Operational obligation:* every deployed upgrade still receives a real export,
preview and safe diagnostics check. Structural parsing is not evidence that all
semantics are unchanged. An out-of-range upgrade requires validation and a
controlled policy update before synchronization resumes.

*Closed.*

### OD-30 — Foundry actor export validating the field paths · **CLOSED 2026-07-30**

**Satisfied.** The maintainer supplied two real Actor exports — a level-9 Paladin (128
items) and a level-14 Sorceress (364 items). Every path in
[foundry-mapping.md §4.2](foundry-mapping.md#42-character-mechanics--verified-against-two-real-actors)
was checked against both. Most held; **five corrections** resulted:

| # | Finding |
|---|---|
| **F-F1** | A manual export carries `"_id": null` — the real ID survives only in the filename. Mappings must come from the module/API, never from an export |
| **F-F2** | Derived values are **absent**, not merely derived: `abilities.*.mod`, `hp.max`, `ac.flat`, `attributes.prof`, `details.level`. The platform computes the ability modifier itself |
| **F-F3** | `system.tools` is keyed by **artisan name** — the same vocabulary as Sheet columns W/X. The tool code table is shared with Foundry, not translated. Three aliases needed (`disg`, `scrolls`, instruments) |
| **F-F4** | **Bastions *are* modelled in Foundry**, richly — `system.bastion` plus `facility` items with type, subtype, size and order. This reverses a §4.3 claim and creates a contested group the matrix did not have |
| **F-F5** | An actor is **1.1–3.3 MB of JSON** with no embedded images — real item volume. Phase 7's snapshot endpoint needs megabyte-scale request limits |

Two further traps worth naming, both of the match-by-name variety:

- **"Experience" means different things on each side.** Sheet column G is a *mission
  count*; Foundry's `details.xp.value` is D&D XP (48 000 / 140 000). Never reconcile
  them.
- **Class, race and subclass names are customised** (`name: "Sorceress"` /
  `identifier: "sorcerer"`). Map on `system.identifier`.

*Closed.* The committed fixture is hand-written to match the verified shape; neither
export is committed.

**Recommended route — a purpose-built throwaway actor, involving no player data at
all.** Create a new actor in a scratch world on the same system version, populate
only what the platform reads, and export that. Full field list and the anonymised
fallback route in
[foundry-mapping.md §7.1](foundry-mapping.md#71-the-remaining-item-and-the-cheapest-safe-way-to-get-it).

Worth including a nonzero `system.currency.ep` even though the game uses no
electrum, so the importer's anomaly-warning path has a fixture.

*Needed from:* a maintainer.

---

## E. Authorization and policy

### OD-18 — Discord guild, Council and DM role snowflakes · **CLOSED 2026-07-31**

Plan §17 requires these as configuration. Which roles grant DM capability?

**Maintainer decision, 2026-07-31:**

- Freedom Blades guild: `1052698198180892733`;
- Guild Council role: `1052702392728178688`; and
- Dungeon Master role, the sole Discord role granting DM capability initially:
  `1124406915783475241`.

These are stable authorization identifiers. The guild and protected Server
Administrator role are bootstrap configuration; capability mappings such as
Council and DM are stored by the platform and managed through the
administrator-only website workflow. The Sheet's `Active DM` flag remains
reconciliation evidence only and never grants effective authorization.

**Authorization administration clarification, 2026-07-31:** individual users'
guild membership and Discord role assignments are managed on the Discord server,
not by the Freedom Blades website. The website stores only the mapping from
stable Discord role IDs to platform capabilities. Only the Server Administrator
may manage those mappings.

**Outstanding residue of an otherwise closed decision.** `/sale` currently matches
the role **name** `shop owner`, and that match is worth 20 percentage points on
the sale price. That role's snowflake is still needed, and until it is supplied
the one authorization check in `/sale` is made against presentation data that
anyone who can rename a role can change. Tracked as a row in
[OD-39](#od-39--unauthenticated-economy-mutations-through-trade-and-sale--raised-2026-07-31).

### OD-24 — Platform Administrator scope · **CLOSED 2026-07-31**

Plan §4.1: the administrator role *"must not silently imply game-policy
authority"*.

*Decide:* may an administrator act with Council capability in a break-glass case?
If so, how is it audited and announced?

**Maintainer decision, 2026-07-31:** Discord role
`1124405581298552933` is the Server Administrator role. It currently has one
holder, but authorization is role-based and must not be tied to that person's
user ID. Individual membership and role assignment are administered in Discord;
the website does not grant or revoke Discord roles. The website manages only the
mapping from Discord role IDs to platform capabilities, and only the Server
Administrator may change those mappings.

The Server Administrator mapping is protected bootstrap configuration: a
Council user cannot edit it, and ordinary mapping changes cannot revoke,
replace, demote or otherwise lock out the administrator. Discord server
ownership remains an external emergency-recovery path, not the normal
authorization mechanism.

This ruling protects administrative continuity; it does not silently make the
Server Administrator a Guild Council game-policy actor. Game-policy capability
continues to come from the separately configured Council role.

### OD-31 — Ordinary-user website mutations · **CLOSED 2026-07-31**

Plan §4.3 and `.agents/AGENTS.md`: ordinary users initially get a **read-only**
website. Confirm this holds for the initial release, and name any narrow action to
be delegated later.

**Maintainer decision, 2026-07-31:** confirmed. Ordinary users receive a
read-only website initially. Website mutations require Guild Council; no narrow
ordinary-user mutation is delegated for the initial release.

### OD-37 — Character ownership and Council reach · **CLOSED 2026-07-30**

Raised at the Phase 1 review gate as O-1: plan §4.2 lists `owner` and `co_owner`
without saying whether a character may have more than one `owner`.

**Maintainer decision, 2026-07-30:**

> *"A character has exactly one owner. However, the Guild Council members can
> access and modify all characters. Modifications should be logged."*

Consequences implemented in Phase 1:

1. **At most one active `owner` per character** is a database constraint —
   `uq_character_access_one_active_owner`. `co_owner`, `delegate` and `viewer`
   remain unlimited.
2. **"Exactly" also means at least one, which is *not* a table constraint.**
   PostgreSQL cannot require a row in another table without a deferred trigger,
   and the Phase 2 importer must be able to create a character before Council
   has resolved who owns it — the same reason `characters.level` is nullable. So
   *at most one* is enforced by the database, and *at least one* is an
   application invariant that the Phase 2 reconciliation report must list as an
   exception. This is the one part of the ruling the schema cannot hold.
3. **Council reach is role-derived, not a `character_access` row.** Council
   members are not granted access rows for every character; their capability
   comes from holding the configured Council role snowflake, resolved through
   `discord_membership_roles` (OD-18 supplies the snowflake). `guild_council` is
   therefore deliberately *not* an `access_kind`.
4. **`audit_events.actor_capability` records the authority a mutation was made
   under**, so a Council modification of a character the actor does not own is
   distinguishable in the audit from an owner editing their own. Plan §4.3
   already required *"the acting Discord user and current authorization
   context"*; this ruling is what makes the second half concrete.

Enforcing the Council's *reach* — that holding the role grants read and write on
every character — is Phase 3 authorization work, not Phase 1. Phase 1 provides
the role snapshot table it will read and the audit column it must write.

### OD-32 — Mission approval and self-approval · **CLOSED 2026-07-31**

Plan §17. Also: are there thresholds requiring a second approver?

**Maintainer decision, 2026-07-31:** a DM prepares and submits a mission and its
settlement; Guild Council approves and applies it. A Guild Council member may
approve their own draft. Self-approval must be recorded explicitly in the audit
history and must be searchable/reviewable by the other Council members. There is
no mandatory second-approver threshold in the initial release.

### OD-33 — Event and announcement channel mappings · **CLOSED 2026-07-31**

Plan §17. The rules name `#goodies-confirmation` (§2.1.2 p.4), `#downtime` (§6
p.14), `#announcements` (§6 p.14), `#trading` (§4.1 p.10),
`#offers-player-services` (§4.2 p.11), `#bastion-turns` (§7.2 p.30),
`#keep-it-rolling` (§7.2 p.30), `#characters-and-bastions` (§7.3 p.30) and
`#lifestyle-work-and.mining` (§6.4 p.18). Snowflakes are needed for each the
platform will use.

**Maintainer decision, 2026-07-31:**

- server announcements: `1054441748874657852`;
- mission channel: `1052700525444997130`; and
- Discord Scheduled Events are guild-level objects and have no channel mapping.

The mission channel constrains mission-related bot commands and notifications;
it is not an Event location. Other legacy command-channel IDs remain separate
configuration and are not inferred from these values.

### OD-38 — Initial authority during Sheet migration · **CLOSED 2026-07-31**

Plan §17 requires an explicit source of truth while Sheets are being retired.

**Maintainer decision, 2026-07-31:** Google Sheets remain authoritative until an
explicitly approved, per-feature cutover. Before each cutover PostgreSQL imports
and reconciles the applicable data. The platform does not enter an indefinite
dual-write mode; authority changes only at the approved cutover gate, with the
documented rollback path retained for the verification period.

---

## F. Operations

### OD-19 — Production domain for the web application · **CLOSED 2026-07-31**

Caddy currently serves `foundry1..3.rpgworld.org`.

**Maintainer decision, 2026-07-31:** the production hostname is
`freedom-blades.rpgworld.org`, and Caddy is the accepted reverse proxy (it
already fronts Foundry). This exact HTTPS origin is used when configuring web
security and Discord OAuth redirect URIs; a wildcard origin is not used.

### OD-20 — Same host as Foundry, or separate? · **CLOSED 2026-07-31**

This host already runs three Foundry instances plus the live bot.

**Maintainer decision, 2026-07-31:** the platform is co-located on this host and
served as `freedom-blades.rpgworld.org` through the existing Caddy reverse proxy.
It retains separate systemd services, loopback application ports, credentials,
database roles and environment files.

### OD-21 — PostgreSQL deployment and backup method · **CLOSED 2026-07-30**

**Maintainer decision:** PostgreSQL 16 is installed from the Ubuntu package and
managed as a host systemd service. It binds to loopback. Migrations use a
separate owner role; applications use restricted roles. Backup target,
retention and off-host copy remain operational configuration that must be
settled before production data is stored.

### OD-22 — Staging on this host or its own? · **CLOSED 2026-07-30**

**Maintainer decision:** staging shares this host to avoid renting a second
server. The accepted risk is mitigated by hard separation: a separate database
and login role, separate service accounts and environment files, distinct
loopback ports, a staging-only Discord application/guild, a non-production
Foundry world, and no shared credentials. Staging never receives a production
backup and must not be configured with a production endpoint.

### OD-23 — Retention periods · **CLOSED 2026-07-31**

Plan §9.4 and §17: OAuth tokens, sessions, attendance records, audit events and
reports.

**Maintainer decision, 2026-07-31:** raw attendance intervals are retained for
90 days after mission settlement; the confirmed mission roster and mission
reports are retained; audit and settlement history are retained indefinitely in
normal operation; OAuth tokens and sessions are retained only as long as they
are operationally necessary and are revoked/removed when no longer needed.

### OD-25 — Are Foundry ports firewalled? · Non-blocking, but check now

The three instances bind to `*:30001-30003`, not loopback, while Caddy proxies
them from `127.0.0.1`. Unless a host firewall blocks those ports, the instances
are reachable directly, bypassing Caddy's TLS.

*This is the only item in this document that may be a live security exposure and
is worth checking independently of the platform work.*

---

## G. Schema and identifiers

### OD-35 — How import idempotency is achieved · **RULED 2026-07-30**

**Maintainer ruling:** *"Take just the database ID the character gets when you fill in
the character table. You also have to write the UUID from foundry in there."*

Recorded as **option (a)**: the ID is assigned when the row is created, never derived
from anything outside the database. ADR 0003 is amended accordingly and is **no longer
blocked**; see *Identifier assignment and import idempotency* there.

**On the second half of the ruling — storing the Foundry ID — agreed, with one
structural note.** The Foundry actor ID is recorded against the character, exactly as
asked. It lives in a one-row-per-link mapping table rather than a bare column on
`characters`, for three reasons that all show up in practice:

1. A character has **more than one** external identity — a Foundry actor *and* a sheet
   row — and both need the same treatment.
2. A Foundry world rebuild **invalidates every actor `_id`**
   ([foundry-mapping.md §4.1](foundry-mapping.md#41-identity-and-mapping-keys)).
   Re-linking then replaces a mapping row instead of editing the character, and the
   old link stays visible in history.
3. Linking is a **Council action that must be auditable** — who linked it, when, and
   the name/class/level fingerprint at the time
   ([ADR 0006](../adr/0006-foundry-integration-boundary.md)).

From the outside this is the same thing: look up a character, see its Foundry actor.
The difference only shows when a link changes.

**One factual correction:** the Foundry actor `_id` is a **16-character alphanumeric
string** (e.g. `TESTACTOR000001`), not a UUID. It affects the column type — a short
`TEXT`, not `uuid` — so it is worth stating precisely. The platform's own
`characters.id` is the UUID.

*Closed. Original write-up retained below for the reasoning.*

---

Raised by Codex review of Phase 0, 2026-07-29. **ADR 0003 was internally
inconsistent on this point and could not be approved as written.**

**The inconsistency.** ADR 0003's schema conventions require primary keys to be
*"UUID (`uuid7` preferred for index locality; `uuid4` acceptable), generated by the
application"* — both of which are **random**, so the same input produces a
different ID on every run. But ADR 0003's *Alternatives considered* rejects
`bigserial` on the grounds that *"import idempotency … is much simpler when the
importer can compute an ID deterministically before writing"* — which a random
UUID cannot do. Both statements cannot hold. The consequences section repeats the
random-UUID reading; §7 of `sheet-inventory.md` and §4.1 of `foundry-mapping.md`
both assume the mapping-table reading.

**The requirement both readings serve.** Plan §12 Phase 2: *"repeated imports do
not create duplicates."* Re-running an import must find the row it created last
time.

**The maintainer must choose. Options:**

| Option | Mechanism | Assessment |
|---|---|---|
| **(a) Random UUID + unique external mapping key** | `characters.id` is `uuid7`/`uuid4`. Idempotency comes from a `UNIQUE` constraint on the mapping table — `sheet_row_mappings(sheet_tab, row_index)` and `external_actor_mappings(instance, world_id, external_actor_id)`. The importer looks up the mapping, reuses the stored `characters.id` if present, generates a new one and inserts the mapping if not, in one transaction | **Recommended.** Idempotency becomes a database constraint rather than a property of a hash function. It survives a change of external key (a Foundry world rebuild invalidates every `_id`, per foundry-mapping §4.1) because the platform ID is independent of it. It also keeps IDs unguessable, which matters once they appear in web URLs |
| **(b) Deterministic UUIDv5** | `characters.id = uuid5(namespace, external_key)`. No lookup needed — the ID *is* the function of the source | Simpler importer. But the ID is then permanently welded to an external key that is **not stable**: a Foundry world rebuild or a Sheet row reorder changes the key and therefore the identity, which is exactly what stable IDs exist to prevent. A row imported from two sources gets two different IDs and must be merged. IDs also become guessable from a known character name or row number |
| **(c) Mapping table plus a deterministic ID** | Both | Redundant. The constraint already guarantees uniqueness; the determinism adds a second source of truth that can disagree with the first |

*Note:* under (a) the ID is generated by the application before the `INSERT` and
persisted — so it is still *"generated by the application, not the database"* as
ADR 0003 requires. Random and application-generated are compatible; random and
*deterministic* are not. That is the whole of the confusion.

*Updated on the ruling, 2026-07-30:* ADR 0003 (conventions, new *Identifier
assignment* section, alternatives), ADR 0005 (Identifiers table), and this entry. The
`sheet_row_mappings` and `external_actor_mappings` shapes in
[sheet-inventory.md §7](sheet-inventory.md#7-implications-for-the-phase-1-schema) and
[foundry-mapping.md §4.1](foundry-mapping.md#41-identity-and-mapping-keys) already
matched option (a) and needed no change.

---

### OD-41 — Phase 2 representation of database-managed current state · **CLOSED 2026-08-02**

**Raised by** the I-02 implementation, which could not proceed without taking a
position and therefore records the position rather than assuming it.

**The question.** Phase 2 must let one Council member correct *every*
database-managed current-state field, and must test every one. Those fields have
no Phase 4/5 domain tables yet, and plan §7.3 says not to create every future
table in the first migration. What representation should Phase 2 use?

**What was implemented, pending a ruling.** A **profile-driven store**:
`character_state_values` for standard and protected fields,
`character_balances` plus append-only `character_transactions` for compensating
ones, with the versioned field profile supplying the key set, the value type and
the correction mode. The four fields that are already `characters` columns keep
those columns. See [ADR 0008](../adr/0008-profile-driven-character-state.md),
status **Proposed**.

**Why it needs a maintainer.** It is a schema-identity decision. It trades a
typed column's database-level constraints for application-level validation
against the profile, and it defers normalization to the Phase 5 package that
owns each field group. Both costs are stated in the ADR; neither is hidden.

**The alternative.** Normalize each field group now — `wallet_balances`,
`resource_transactions`, `character_proficiencies`, `lifestyle_states`,
`bastions`, `character_items` and the rest — ahead of the rule decisions and use
cases those packages carry. That is the design the platform ends up with; the
objection is only to designing it now, against a guess.

**Ruling by Peter Duscha, 2026-08-02:** reject ADR 0008. Phase 2 imports
immutable snapshots, character identity and mappings and produces reconciliation
evidence, but does not migrate Sheet-era state. Each field group migrates once
into the typed model introduced by its owning package. The legacy path remains
authoritative until that package's approved cutover; no dual writes are allowed.
Controlled baseline v1.1 records the impact and acceptance criteria.

**Downtime consequence:** `character.downtime_progress` (Sheet column V) is not
corrected as opaque text in Phase 2. Its migration waits for the typed learning
and crafting project models in their owning packages.

---

### OD-42 — Character display-name identity policy · **CLOSED 2026-08-02**

**Raised by** I-05, the residual of I-01. The mapped-name normalization
correction was accepted on 2026-08-02, but `characters.display_name` carries no
database uniqueness rule, so the shared comparison policy in `domain/names.py`
is enforced by the importer alone. Recording the position rather than assuming
one is the point of this entry: the replacement Phase 2 plan needs a decided
answer before another writer touches that column.

**The question.** May two characters share a display name, and what must a
name-based lookup do when it finds more than one candidate?

**What the accepted record already establishes.** Three of the four parts are
not open at all:

- names are not identities — `.agents/AGENTS.md` § *Domain* (*"Use stable IDs
  for actors and records. Display names are mutable and are not identities"*)
  and plan §3 principle 6;
- display labels never serve as keys — plan §7.3.1 (*"Reference identities use
  stable internal IDs; display labels are mutable and never serve as foreign
  keys"*);
- a mapping is never established by name — [ADR 0006](../adr/0006-foundry-integration-boundary.md)
  § *Mapping is Council-established, never inferred* (*"Never by name matching"*),
  carried forward intact by its 2026-08-02 amendment.

Plan §12 Phase 2 also lists *duplicate display name* among the scenarios the
import must **report**, which presupposes that duplicates can occur.

**What is genuinely open**, and therefore what this ruling adds: whether a
duplicate is *permitted to persist* in PostgreSQL, and what a legacy name-based
candidate lookup does when it finds several. The accepted record does not settle
either, and silence has been read in two incompatible ways — as licence to add a
unique constraint, and as licence to pick the first candidate.

**Ruling by Peter Duscha, Acceptance Authority, 2026-08-02:** accepted as
recommended.

> *Display names are not unique identities. Multiple characters may share a
> display name. Stable character IDs and external Actor IDs provide identity.
> Any legacy name-based candidate lookup fails closed when more than one
> candidate exists.*

The Data Owner recommendation and the Acceptance Authority approval are the same
person under the solo-maintainer operating model (plan §0.3). **I-05 is closed
by this ruling.** No unique display-name constraint is added.

**Consequences.**

- No unique index or constraint is added to `characters.display_name`. A
  uniqueness rule would make a legitimate in-world situation — two characters
  called *Grim* — an import failure and a data-repair task.
- The reconciliation candidate lookup must return **all** candidates rather than
  one, and refuse the run when it finds more than one; the current single-value
  claim lookup collapses duplicates and is a defect under this ruling.
- Two Actors sharing a display name under distinct external IDs remain two
  create candidates, and an unmapped Actor whose name is already claimed remains
  a blocking issue requiring a deliberate Council mapping.
- I-05 closes. R-01's residual narrows to the legacy bot's own comparison.

**Alternative rejected.** A unique display-name constraint plus a stored
identity key. It would enforce the comparison in the database, which is the
attraction, but it forbids a situation the game permits and converts a display
concern into an identity constraint — the exact confusion the rest of the
accepted record removes.

**Authority.** Data Owner recommendation, Acceptance Authority approval, per
plan §17 (field/data ownership). Recorded 2026-08-02 with the acceptance of
[`../review/phase-2-v1.5-remediation-plan.md`](../review/phase-2-v1.5-remediation-plan.md).

### OD-43 — Discord-independent administration and provider portability · **CLOSED 2026-08-13; DESIGN ACCEPTED AT P3.G0**

**Ruling by Peter Duscha, Product Owner and Acceptance Authority, 2026-08-13.**
The Server Administrator must retain an independent access route if Discord
authentication is unavailable. The account and authorization model must also
permit a controlled replacement of Discord as the community login provider.
Discord remains the initial provider, but it must not become the permanent
identity key for sessions, character ownership or audit attribution.

**Required security boundary.** Emergency authentication grants Platform
Administrator capability only. It does not grant Council authority and cannot
by itself approve an import or change game policy. A future replacement provider
must link through immutable provider identifiers and a controlled migration;
display names, usernames and email addresses never establish identity
equivalence automatically.

**Implementation design accepted at P3.G0.** ADR 0010 and the accepted Phase 3
contracts implement stable internal platform accounts, separately linked
`(provider, subject)` identities, pre-enrolled WebAuthn credentials and a
host-local hashed single-use recovery grant. It deliberately does not add a
permanent local password or choose an ordinary-member replacement provider in
advance. The accepted remediation also replaces the Discord-only audit constraint
and makes emergency-derived administrator authority continuity-scoped through
mapping provenance until full-scope ratification. P3.1 implements the accepted
design; its named database evidence remains prospective until executed.

**Why the split is deliberate.** The availability and portability requirements
are decided product requirements. Credential mechanics, recovery lifetime,
session limits and migration mechanics are security architecture. Peter accepted
that architecture at P3.G0 on 2026-08-13 after independent architecture and
security-focused re-review.

**Authority.** Product Owner for required behaviour; Acceptance Authority for
the phase gate; Security Reviewer recommendation required for the implementation
contract.

### OD-44 — OAuth completion binding across provider I/O · **CLOSED 2026-08-14**

**Ruling by Peter Duscha, Product Owner, Security Reviewer and Acceptance
Authority, 2026-08-14.** Adopt the durable one-way completion binding in
[`../review/phase-3-p3-1-sm-01-completion-binding-decision.md`](../review/phase-3-p3-1-sm-01-completion-binding-decision.md).
A Discord OAuth session carries a unique, non-null
`sessions.oauth_transaction_id` referencing a consumed transaction. Completion
atomically claims `oauth_transactions.completion_claimed_at`, creates the
session and writes the success audit in one transaction after provider I/O.

There is no reverse `oauth_transactions.session_id`: the session foreign key is
the single authoritative relationship, avoiding a redundant cyclic value. The
accepted outcome is exactly one session from one consumed browser-bound OAuth
transaction without holding a database transaction across Discord I/O. A new
revision 0009 and the named PostgreSQL, rollback, concurrency and mutation
evidence are required before P3.G1 can close.

**Implementation recorded 2026-08-14** (change-log C-P3.1-E,
[`../review/phase-3-p3-1-od-44-remediation-submission.md`](../review/phase-3-p3-1-od-44-remediation-submission.md)).
Migration 0009 adds both columns, the `RESTRICT` foreign key, the unique index
and the check constraint; `complete()` takes the transaction id and claims it
atomically as the first statement of the provider-I/O-free transaction. One
reading of the ruling is declared for confirmation rather than assumed: the
unique index is scoped `WHERE rotated_from_session_id IS NULL`, because a
table-wide `UNIQUE` together with the ruled check constraint would make N-08
privilege rotation of a Discord OAuth session impossible. Independent
implementation re-review and a distinct security-focused pass remain outstanding;
this ruling is not thereby accepted as delivered.

**Second ruling, 2026-08-14** (decision record §8, change-log C-P3.1-F,
[`../review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md`](../review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md)).
Peter approves the declared partial index
`UNIQUE (oauth_transaction_id) WHERE rotated_from_session_id IS NULL` as the
authoritative interpretation of OD-44, **conditionally on rotation integrity**:
one successor per predecessor; a rotation's account, authentication method and
OAuth binding equal to its predecessor's; only a live, unrotated predecessor
rotatable; insertion and revocation atomic; concurrent rotations deterministic;
no arbitrary session labellable a rotation; and break-glass rotations unbound to
OAuth transactions.

The same ruling covers Codex's re-review finding that the completion claim did
not bind the **provider**: the claim now compares `provider_key` on the row it is
claiming, and the expected key is derived from an indivisible verified provider
result rather than from route ordering. Implemented 2026-08-14 in migration 0009
and the OAuth, session and provider boundaries. Codex independent implementation
re-review and a distinct security-focused pass remain required; OD-44's closure
stands, P3.G1 does not.

### OD-45 — TC-BG-05 HTTP evidence gate allocation · **CLOSED 2026-08-14**

**Ruling by Peter Duscha, Product Owner and Acceptance Authority, 2026-08-14.**
Adopt Option 1 in
[`../review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md`](../review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md).
P3.G1 retains TC-BG-05a, TC-BG-05d and the service/database portions of
TC-BG-05b/c/e. The direct-HTTP portions move to P3.2 and are mandatory blocking
evidence at P3.G2 against the real R-33, R-34 and R-38 routes.

This changes evidence timing only. It is not a waiver, does not accept the HTTP
boundary at P3.G1, and does not authorize test-only substitutes or early P3.2
implementation.

### OD-46 — Where the Sheet-era identity link is written · **CLOSED 2026-08-17**

**Ruling by Peter Duscha, Maintainer, Product Sponsor and Acceptance Authority,
2026-08-17**, recorded in full as change-log entry
[`C-P3.2-A`](../project-management/change-log.md) and implemented in the corrected
[`phase-3-identity-migration-contract.md`](../contracts/phase-3-identity-migration-contract.md)
§7.2–§7.7.

Three accepted passages placed the `character_access` write at the Council
confirmation and one — §7.2 of the migration contract — placed it in a later
`C-05 --apply` step. **Immediate activation is authoritative.** A Guild Council
confirmation at R-29 creates the link:

1. R-29 creates the real `character_access` row atomically with the proposal's
   confirmed transition and both audit events, through the same
   `CharacterAccessService.grant()` R-25 uses, attributed to the confirming
   Council member's **live** server-side authorization resolution. Any failure in
   that set rolls all of it back.
2. **C-05 is withdrawn.** There is no later materialization step, no apply state
   and no apply command; the identifier is retired rather than reused. An unused
   apply phase is not retained merely because it was implemented.
3. R-30 remains a rejection only and can never create a link.
4. **C-04 remains a temporary migration/import utility** that reads the legacy
   Google Sheet because some current character/player data still lives there. It
   writes proposals and evidence only, never a `character_access` row, and never
   writes to Google.
5. **Google Sheets is legacy migration input**, not an ongoing platform component,
   operational database or portal dependency. The Google client libraries stay out
   of the web application environment; C-04 runs in a separate, temporary operator
   environment holding those libraries and a read-only credential.
6. Imported data is verified in PostgreSQL. The legacy access is retained only for
   the approved verification/rollback window and is then retired.
7. C-04 must be told the real player-tab name explicitly. An unverified tab name
   is not operational truth, so `--player-tab` is required rather than defaulted.

**Operational input confirmed later on 2026-08-17.** Peter Duscha confirmed that
the one-time C-04 source tab is named **`Players`** (change-log entry
`C-P3.2-B`). The command still requires `--player-tab Players`: keeping the input
explicit prevents a temporary migration fact from becoming a permanent portal
default or Google dependency. This confirmation closes the operational input
question; it does not approve P3.G2.

**Consequential defect ruling, same date.** Duplicate player names in the legacy
player tab (`Ada` / `ADA`) must fail closed. Nothing may choose a row by Sheet
order, and nothing may grant access from such evidence. Migration contract §7.3.1
records the resolution: the whole C-04 run is refused, so no partial run is
written and no control total can conceal the duplicate.

P3.G2 is **not** approved by this ruling and remains open pending independent and
security-focused re-review and explicit maintainer acceptance.

### OD-47 — Two active Discord identities on one platform account · **DEFERRED 2026-08-17**

**Ruling by Peter Duscha, 2026-08-17** (change-log entry `C-P3.2-A`). Whether one
human may hold two simultaneously active Discord identities on one platform
account remains an open product question, and it is deliberately deferred rather
than settled to unblock P3.2.

The current behaviour is **fail-closed and is retained**: when an account holds two
active identities for one provider, the capability resolution refuses rather than
picking one, because which Discord account's roles decide a person's capability is
exactly the question an arbitrary tiebreak must not settle (the same rule OD-42
applies to candidate people, applied to one person's provider identities). No
uniqueness constraint is added and none is removed by this deferral.

Revisit when a second ordinary provider or an account-merge flow is proposed.

### OD-48 — Does Phase 4 add a physical ledger table? · **CLOSED 2026-08-28**

**Ruling by Peter Duscha, Data Owner, Product Owner and Acceptance Authority,
2026-08-28**, on the recommendation in
[`../review/phase-4-package-plan.md`](../review/phase-4-package-plan.md) §5
(P4-D1). **Phase 4 adds no migration and no physical ledger table.**

The ledger is defined in `domain/` with a repository protocol in `application/`
owned by its consumer, and an in-memory reference adapter exercised by contract
tests. Durable idempotent command execution reuses the **existing**
`idempotency_keys` table under a Phase-4-owned scope, so retry, conflicting
reuse and concurrent callers are still proved against real PostgreSQL.

**Rationale.** `../project-management/data-migration-register.md` assigns
`wallet.balance_copper` (Characters P–S), `wallet.moradinium` (T) and
`wallet.debt_copper` (AC) to package **5.2**, `downtime.thousandth_days` (I) to
**5.5** and `lifestyle.living_cost_weeks` (J) to **5.3**, and states that no row
may have two write-authoritative targets. A Phase 4 balances or wallet table
would pre-empt that ownership, and the Phase 4 handover independently forbids
inventing a generic character-state store or a Phase 5 feature schema.

**Affected requirements.** Implementation-plan §12 Phase 4 deliverable
"transaction ledger"; §13.2's migration-failure row; the handover's conditional
requirement for PostgreSQL constraint, append-only and runtime-role evidence.

**Consequence, stated so the gate is not surprised.** Phase 4 produces **no
new** constraint, append-only-trigger or runtime-role evidence for a ledger
table, because it creates none. That evidence is owed by package **5.0** or
**5.2** when the physical ledger lands. The mandatory logical-schema artifact
and its independent review are **not** triggered by Phase 4; they are triggered
the moment a material schema addition is proposed, and the package plan's stop
condition 1 enforces that.

### OD-49 — The downtime unit in the shared domain · **CLOSED 2026-08-28**

**Ruling by Peter Duscha, Product Owner and Data Owner, 2026-08-28**, on
[`../review/phase-4-package-plan.md`](../review/phase-4-package-plan.md) §5
(P4-D2). The domain `Downtime` value object holds an **integer count of
thousandth-days** and refuses anything else — no rounding, no coercion.

Under final OD-52, Phase 4 creates no Sheet read adapter. **`/info` continues to
render exactly the text it renders today** through its untouched legacy path.
Package 5.5 owns conversion and explicit invalid-value handling when it migrates
column I and adds the real character-page consumer.

**Rationale.** The unit is already settled: OD-08 fixed downtime at three
decimals, which coincides exactly with the thousandth-day, and the migration
register names the typed target `downtime.thousandth_days`. The live code
disagrees — `models/resource.py:18` loads the value through
`safe_number(..., default=0.0)` into a Python `float`, and `helpers/utils.py:6`
silently coerces an unparseable cell to a default, which `.agents/AGENTS.md`
forbids at a boundary. Refusal belongs in the domain object; surfacing that
refusal to a player is a **behaviour change**, and preserved visible behaviour is
a Phase 4 gate criterion. Rounding was rejected outright: it is the
`safe_number` defect carried into the new layer.

**Affected requirements.** Phase 4 deliverable "money and resource value
objects" and its "explicit smallest unit and accepted rounding policy"; the
characterization requirement that `/info` output is unchanged. Package **5.5**
owns what to do about an invalid stored value when it migrates column I; Phase
4 decides the domain unit but does not read the Sheet through a new boundary.

### OD-50 — Denomination counters are a Sheet representation, not a domain concept · **CLOSED 2026-08-28**

**Ruling by Peter Duscha, Product Owner and Data Owner, 2026-08-28**, on
[`../review/phase-4-package-plan.md`](../review/phase-4-package-plan.md) §5
(P4-D3). `domain/` models money as **integer copper only**. The Sheet's four
independent denomination counters remain a **legacy persistence and presentation
detail**, carried on the read model, explicitly labelled, with no domain meaning.

`/info` renders from the as-stored counters and is byte-identical to today. The
copper total travels alongside for comparison and arithmetic. **Nothing
normalizes a character's coins as a side effect of a read.**

**Rationale.** A wallet holding `10 sp` and one holding `1 gp` are the same
100 cp but print differently (`models/resource.py:41` prints each denomination
only when strictly positive), so the visible output is **not derivable** from a
copper total and normalizing on read would silently change `/info` for many
characters. Modelling denominations in the domain was rejected because package
5.2's typed target is a single integer-copper balance, so the concept would be
built in order to be discarded.

**Affected requirements.** Phase 4 acceptance criterion "money uses integer
copper"; the characterization requirement that command output is unchanged;
package **5.2**, which owns the eventual normalization of Characters P–S into
one balance and must record its own control totals when it does.

### OD-51 — The float-money defects in `/sale` and `/lc` · **CLOSED 2026-08-28**

**Ruling by Peter Duscha, Product Owner, 2026-08-28**, on
[`../review/phase-4-package-plan.md`](../review/phase-4-package-plan.md) §5
(P4-D4). **Characterize, do not correct.**

Phase 4 adds tests recording exactly what these paths do today, each naming the
defect and its owning package in its docstring, and changes no line of either.

**The defect.** `Resource.sale` (`models/resource.py:166`) computes
`earnings = crafting_cost * earnings_percent` in binary floating point and
converts through `to_currency` (`helpers/utils.py:29`);
`Lifestyle.pay_for_weeks` (`models/lifestyle.py:52`) does the same with
`extra_expenses_sp / 10.0`. Both contradict the product invariant that money is
never calculated or persisted as a binary float.

**Why it is deferred rather than fixed.** The *rules* are verified correct —
RC-01 and RC-03 are recorded as Implemented ✓ / Corrected ✓ and reproduce both
PDF worked examples — so the defect is the arithmetic type, not the rule. Both
are **mutation** paths, and Phase 4 is explicitly excluded from changing a live
mutation. Correcting them here would be a Phase 5 behaviour change made under a
Phase 4 authorization.

**Owners.** Package **5.7** owns `/sale`; package **5.3** owns `/lc`. Each
inherits the characterization test and must convert the path to integer copper
when it migrates, with its own evidence that the corrected arithmetic still
reproduces the PDF worked examples.

**Affected requirements.** Phase 4's characterization deliverable; risk R-P4-2,
which exists so these tests are not later mistaken for accepted policy.

### OD-52 — The Phase 4 query and `/info` boundary · **CLOSED 2026-08-28; FINAL AMENDMENT 2026-08-29**

**Original ruling by Peter Duscha, Product Owner, 2026-08-28**, on
[`../review/phase-4-package-plan.md`](../review/phase-4-package-plan.md) §5
(P4-D5): `/info` would call one application query and only the money/resource
block would be typed.

The query returns typed `Money`, `Moradinium` and `Downtime` for the resource
block. Name, level, badge, lifestyle and Bastion pass through as presentation
values the temporary Sheet adapter read, explicitly labelled as owned by
packages **5.1**, **5.3** and **5.9**. `/info`'s rendered output is unchanged.

**Why the query is not shaped like `/info`'s summary.** `/info` is a Discord
command and its summary is Discord presentation. The platform has no consumer
for that shape and cannot acquire one in Phase 4: the portal's
`CharacterDetailView` renders every money field as `MigrationDeferred` — a type
with **no value field at all**, so a legacy field cannot be shown as though the
platform knew it — under a mandatory Phase 3 test. Until package 5.2 migrates
the wallet, the portal has no wallet to show. A full typed summary read model
would therefore have exactly one consumer, be shaped by Discord's rendering, and
cut across four packages' typed ownership.

**First amendment by Peter Duscha, Product Owner and Acceptance Authority,
2026-08-28.** `/info` would remain unchanged while Phase 4 built a
production-shaped temporary Sheet adapter for a typed money/resource query.

**Final amendment by Peter Duscha, Product Owner and Acceptance Authority,
2026-08-29.** Do not build that adapter-only compromise. A query without a real
production caller violates the project's real-consumer design rule and would
create transitional code likely to be discarded. Phase 4 creates neither an
`/info` rewrite nor a temporary Sheet-backed wallet query/adapter. Its
application-boundary evidence comes from the ledger and durable idempotent
command-execution work, whose protocols have concrete Phase 4 consumers.

The finished platform does not need an `/info` slash-command equivalent:
authenticated players inspect linked characters on its character pages.
Package **5.2** introduces the typed wallet query and production adapter when
that page can consume them. Package **5.1** owns any transitional database-backed
`/info` migration required to keep the Freedom bot supported through cutover.

**Affected requirements.** The Phase 4 real-command and temporary-adapter
deliverables are removed. Existing `/info` characterization remains regression
evidence. No Phase 5 implementation, order change, authority move or gate is
approved by this ruling.

**Recorded observation, not a proposal.** `/info` performs no authorization
beyond guild membership, so any guild member can read any character's wallet.
Phase 4 is explicitly forbidden from changing authorization and no longer
touches the command. Risk **R-P4-3** remains with package **5.1** if it migrates
the command during the transition; its gate already covers read-path
authorization.

### OD-54 — Package 5.0 persists the migration-authority control plane · **CLOSED 2026-08-29**

Peter Duscha accepted Codex's recommendation that Package 5.0 persist its own
authority control plane and use an authority revision as the durable effect in
the effect/receipt/audit transaction. Acceptance is conditional on remediation
and independent re-review of P5.0-R1 and P5.0-R2; it authorizes design revision,
not implementation.

### OD-55 — Comparison telemetry implementation begins in Package 5.1 · **CLOSED 2026-08-29**

Package 5.0 defines the common comparison-telemetry contract only. Package 5.1
owns the table, write path and independently reviewed schema with its first real
shadow consumer. Synthetic use in 5.0 is not a sufficient production consumer.

### OD-56 — Character identity in comparison telemetry · **CLOSED 2026-08-29**

An internal character UUID may be stored when Package 5.1 implements telemetry,
with restricted access and approved retention. Telemetry stores no name,
Discord identity, compared value, exception text or arbitrary payload. The
Security Reviewer confirms the implementation at the applicable gate.

### OD-57 — Package 5 migration/cutover numeric controls · **CLOSED 2026-08-29**

Peter approved N5.0-1 through N5.0-8 as proposed in the Package 5.0 plan, with
one clarification: fewer than 30 compared operations requires a separately
approved package-specific numeric threshold and rationale before shadowing
begins; it cannot be improvised as a gate exception.

### OD-58 — The durable ledger table belongs to Package 5.2 · **CLOSED 2026-08-29**

Package 5.2 owns the durable wallet/ledger schema and its first production
consumer. Package 5.0 creates no ledger table and does not close R-P4-4.

### OD-59 — Package 5.0 authority changes are host-local · **CLOSED 2026-08-29**

Authority changes use a host-local operator command executed by a named,
currently authorized Platform Administrator against a validated database
target, with preview/apply fencing, idempotency and safe output. Package 5.0
adds no web route or Discord command for this mutation.

### OD-60 — No new service-principal scope in Package 5.0 · **CLOSED 2026-08-29**

Package 5.0 has no non-human authority-change caller and adds no service-
principal scope. The decision is revisited only by a package with a concrete
consumer, initially Package 5.3's scheduled writer.

### OD-61 — Package 5.0 review roles · **CLOSED 2026-08-31**

Peter designated Claude as implementer and working Technical Lead, and Codex as
Independent Reviewer and independent logical-schema reviewer. The Security
Reviewer remains unnamed, so Package 5.0 remains not ready. Codex's first design
review returned Blocking findings P5.0-R1 and P5.0-R2 and Important finding
P5.0-R3; the last was closed by replacing the corrupted handoff.

**Re-review update, 2026-08-29.** Codex closed P5.0-R2, kept P5.0-R1 Blocking
and raised Blocking P5.0-R4 for forgeable shared-role lease and acknowledgement
evidence. The Security Reviewer remains unnamed and implementation remains
unauthorized.

**Remediation R2 update, 2026-08-29.** Claude submitted revision 3 of both
design artifacts and a handback document. It **claims neither Blocking finding
closed**; Codex independent re-review is requested. The Security Reviewer's scope
has grown — a new database principal, the relocation of the Google
service-account credential out of the Freedom bot, and a procedure that changes a
production Drive permission at each cutover — and the estimate for that review
rises to 1.0–1.5 reviewer-days. The Security Reviewer is still unnamed and the
package is still not ready.

**Remediation R2 independent re-review, 2026-08-29.** Codex kept P5.0-R1 and
P5.0-R4 Blocking and requested remediation R3. The proposed Google boundary
does not prove completion of a request accepted before permission revocation;
measured propagation and a fixed settle interval cannot manufacture a
contractual barrier. The coordinator principal is not yet bound to a named,
dedicated OS account, exact peer mapping and host privilege boundary that prove
no service process can authenticate as it. P5.0-R2 remains closed, OD-55 remains
preserved, the Security Reviewer remains unnamed and implementation remains
unauthorized.

**Remediation R3 submitted, 2026-08-29.** Revision 4 of the package plan and the
logical schema, plus
`docs/review/phase-5-0-remediation-r3-handback.md`. It **claims neither Blocking
finding closed.** For **P5.0-R4** it supplies the missing boundary: a dedicated
`freedomcoord` OS identity, exact `pg_hba.conf` ordering and a single
`pg_ident.conf` map, a `sudoers` execution boundary, a root-owned deployment path
outside the group-writable repository tree, and a per-identity denial-evidence
plan. For **P5.0-R1** it takes the second route the handoff permits: after
tracing thirteen candidate barriers against the published Google surface it
concludes that **no accepted-request completion barrier exists**, states the
invariant that cannot be guaranteed, states the six weaker guarantees that can be,
and returns a newly priced choice as OD-62 reframed a third time. **OD-65 is
raised** for the host changes the boundary needs outside the coordinator. The
estimate rises to PERT 29.2 implementer-days and the Security Reviewer's scope
grows again, to 1.5–2.5 reviewer-days. The Security Reviewer is still unnamed and
the package is still not ready.

**Independent re-review of revision 4, 2026-08-29.** Changes requested and
remediation R4 required. P5.0-R1 remains Blocking and P5.0-R5 is raised
Blocking: the dispatch journal is specified under volatile `/run`, while its
append-only property was inferred from the unrelated ext4 filesystem under
`/opt`; reboot, replacement, missing or corrupt state can therefore falsely
appear clear. The plan also contradicts itself by denying dependency on journal
completeness while requiring `dispatch_journal_clear` for activation. OD-62
must not be ruled until R4 makes this control fail closed. P5.0-R4's identity
design substantially answers the design finding, but OD-64, OD-65, the named
Security Reviewer and operational evidence remain open. P5.0-R2 remains closed.

**Remediation R4 submitted, 2026-08-29.** Revision 5 of the package plan and the
logical schema, plus `docs/review/phase-5-0-remediation-r4-handback.md`. It
**claims no finding closed.**

**Revision 5 independent re-review, 2026-08-29.** Changes requested;
**P5.0-R5 remains Blocking** and remediation R5 is required. The revised path
answers the original volatility problem, but the proposed trust root cannot be
instantiated: the genesis record hash depends on the seal digest while the seal
contains the genesis record digest. The writer is denied read access to the seal
it must validate. The capability probe's ordinary permissions mask whether
`FS_APPEND_FL` caused each refusal, and destructive probes against the live
journal are unsafe if the flag is absent. `CHECK (append_only_verified)` also
validates only an asserted Boolean and cannot establish that a host probe ran.
OD-62 and OD-66 remain Open pending an acyclic, executable and independently
reviewed revision. Implementation remains unauthorized.

For **P5.0-R5** the journal's storage and lifecycle are replaced rather than
patched. `/run` was read on this host and is `tmpfs`; `/`, `/var`, `/var/lib` and
`/opt/freedom-blades` are one ext4 filesystem on `/dev/vda1`, so the journal moves
to **`/var/lib/freedom-sheet-writer/journal/`** — durable, and established by
reading `/proc/mounts` rather than by inference. The containing directory is
**root-owned and not writable by the writer**, so it can neither unlink, rename,
replace nor create there; `chattr +a` becomes a second, independent layer and is
**probed at provisioning and at every writer start**, with a generation whose
probe failed unable to be registered at all. A `chattr +i` **seal**, a genesis
record inside the journal and a **registered generation** in a new sixth table
must all agree, so a new or reset journal is never indistinguishable from a valid
empty history — and creating one first requires **sealing and archiving the
history it replaces**. **Twenty-one conditions all fail closed**, covering every
state the handoff enumerated and six more. A **privileged `freedom-journal-admin`**,
run as root under its own `sudoers` drop-in, owns seal, rotate, repair,
archive-verify and a `dispose` gated on retention, plan §15.1's gate and a Data
Owner approval, so **the writer cannot erase or replace evidence it authored** and
clearing is a named audited command rather than an ambient capability.

**The completeness contradiction is resolved by withdrawing the false statement,
not the control.** Revision 4's *"nothing in the fence depends on the journal
being complete"* is withdrawn; `dispatch_journal_clear` is kept; and the single
direction of the dependency is stated — the journal can **refuse** an activation
the other four methods would permit and can **never permit** one they would
refuse. What is left outside it is named as risk **R-5.0-10**. Dropping the method
instead is offered as **OD-66 option J-3** rather than taken.

For **P5.0-R1** nothing changes and nothing is claimed: **a durable journal is not
a barrier and is not offered as one**, and R-5.0-8 is not narrowed by a single
case. For **P5.0-R4** the boundary is unchanged apart from two added denial rows,
and **no operational evidence is claimed passed**.

**OD-66 is raised**, OD-63 is extended to nine controls, the estimate rises to
PERT 35.5 implementer-days, new risks **R-5.0-10** and **R-5.0-11** and new
assumption **A-5.0-5** are recorded, and the Security Reviewer's scope grows again
to 2.0–3.0 reviewer-days. The Security Reviewer is still unnamed and the package
is still not ready.

**Revision 6 independently re-reviewed, 2026-08-30; remediation R6 required.**
P5.0-R5 remains Blocking. Algorithm C embeds probe stages 1–3 while the schema
claims the immutable digest covers all four stages, including the later
deployment-time sandbox check. F-1 also overclaims writer-only protection of
the seal because V-W does not authenticate `BND.sealed_at`. `JNL-32` must be
corrected so absent `+a` refuses at W9 with no startup append. The active handoff
contains the documentation-only remediation instructions. No OD option is
approved or preferred by this review; OD-62 through OD-66 retain their prior
owners and decision status.

**Remediation R5 submitted, 2026-08-30.** Revision 6 of the package plan and the
logical schema, plus `docs/review/phase-5-0-remediation-r5-handback.md`. It
**claims no finding closed.** All four revision-5 defects are conceded. The
cryptographic construction becomes **acyclic**: a seal body is written and hashed
before the journal file exists, the genesis record is *derived* from that body and
anchored on `seal_body_digest`, the binding section is appended once the genesis
record and its inode exist, and the finished seal's digest is a **leaf** that
nothing else hashes — with numbered creation and verification algorithms and eight
falsification cases. The writer is given the **minimum read-only** access to the
seal it is required to validate, through a new system group `freedomjournal`,
while `…/journal` tightens from `0751` to `0750` so *other* loses even traverse;
the writer still cannot modify, replace, rotate, seal, archive or dispose of
evidence. The capability probe moves into a **disposable arena** with a control
stage that must pass before any refusal is attributed to `FS_APPEND_FL`, expected
`errno`s that separate discretionary permissions, a read-only mount, the systemd
sandbox and append-only enforcement, non-destructive startup checks and a
privileged cleanup. And `CHECK (append_only_verified)` is **withdrawn** — a
Boolean constraint cannot observe a host — replaced by an attested, re-derivable
probe report and an explicit statement of what PostgreSQL enforces versus merely
records.

**No new decision is raised by R5**, and OD-62 and OD-66 are **not decided**;
their impacts are recorded above and in the entries below. OD-65 gains a fourth
item, the third system group. The fail-closed conditions grow to **twenty-five**
and the evidence band to **forty-one** cases, the estimate rises to PERT 37.7
implementer-days, and the Security Reviewer's scope grows to **2.5–3.5**
reviewer-days over an eleven-element surface. **No implementation was performed
and no implementation suite was run.** The Security Reviewer is still unnamed and
the package is still not ready.

**Revision 7 independently re-reviewed, 2026-08-30; remediation R7 required.**
P5.0-R5 remains Blocking. C0 requires the probe result before C1 produces it;
S4-2 lacks a positive DAC control for the exact path whose `EROFS` is attributed
to systemd; and the attacker-class matrix assigns cases beyond each class's
defined capabilities. No OD option is approved or preferred by this review;
OD-62 through OD-66 retain their prior owners and status.

**Remediation R6 submitted, 2026-08-30.** Revision 7 of the package plan and the
logical schema, plus `docs/review/phase-5-0-remediation-r6-handback.md`. It
**claims no finding closed.** All four revision-6 defects are conceded. The
capability probe's **sandbox stage moves from deployment to provisioning**,
inside the same `verify-capability` invocation and **before** the probe report is
built, with named cases `S4-1 … S4-3`, the deployed unit's directive set captured
and hashed, and invalidation reusing the rule that already exists — a
redeployment forces a rotation — so the sealed digest covers the four stages it
names. The re-review's alternative, a second typed artifact for deployment
evidence, is **priced and rejected in the same table** on its own requirement:
outside the immutable seal, with no database available to it, the writer cannot
authenticate a deployment-time file at all. The seal's **binding section loses
`sealed_at` and its own format field**, keeping exactly the three values the
writer's V-W algorithm recomputes or compares, with its structure fixed by a
`binding_format_version` carried in the chain-authenticated seal body; a complete
binding-field authentication table is added; **F-1 splits into F-1a** — refused
by the writer with no database — **and F-1b** — a `CAP_LINUX_IMMUTABLE` rewrite
of the seal *and* the journal's record 0, which **only the registered row
refuses** — with two attacker classes stated and **F-9 … F-12** added.
**`chattr +i` is not offered as the answer.** And `JNL-32` becomes **`JNL-32a`**
and **`JNL-32b`**, the second expecting a refusal at **W9** with `SW-J06` before
**W17**, no write-mode journal open and byte-for-byte unchanged evidence.

**No new decision is raised by R6**, and OD-62 through OD-66 are **not decided**.
The lifecycle question the handoff put was a choice of *where* evidence lives
inside **OD-66 option A**, which is already open, so it is recorded there as an
amended option-A content rather than adopted. **OD-66's option A changes in two
places and no others**; options B, C and D, the owners, the authorities and the
retention rule are unchanged, **OD-63 stays at nine controls**, and OD-62,
OD-64 and OD-65 are untouched. The evidence band grows to **forty-five
identifiers and forty-eight cases**, falsification rows to **twelve**, the
estimate to PERT **38.2** implementer-days and the stop conditions by **10h**;
the fail-closed conditions stay at **twenty-five**, the refusal codes stay
`SW-J01 … SW-J25`, and **no schema object changes at all**, because `sealed_at`
was never a database column. The Security Reviewer's scope gains one element —
the transient `systemd-run` unit the probe's stage 4 starts as root at
provisioning — without a change to the 2.5–3.5 reviewer-day estimate.
**No implementation was performed, no host was read or written, no `systemd-run`,
`chattr` or `setpriv` was run, no probe arena was created, and no implementation
suite was run.** The Security Reviewer is still unnamed and the package is still
not ready.

**Remediation R7 submitted, 2026-08-30.** Revision 8 of the package plan and the
logical schema, plus `docs/review/phase-5-0-remediation-r7-handback.md`. It
**claims no finding closed.** All three Blocking defects and the one Important
governance defect are conceded. **Algorithm C is renumbered `C0 … C13`**: `C0`
checks only preconditions that exist before the probe runs and reads no probe
result; `C1` remains the single invocation of the probe stages and the single
creation point of the report; and a new **`C2`** validates pass state, report
completeness, deployment-digest equality and cleanup success **before any
persistent artifact exists**, so a refusal at `C0`, `C1` or `C2` leaves no
journal, seal, symlink or registration row. A **value-dependency table** states
where every consumed value is produced, validated and first used. **Stage 4 gains
an exact target and a positive control**: `…/probe-ro/s4-2.target`, in a second
transient directory on the same mount, inside `ProtectSystem=strict`'s read-only
tree and outside the substituted `ReadWritePaths=`, with new case **`S4-0`**
proving open, append, `fsync`, `rename` and `unlink` permitted by DAC on that
exact file under the writer's uid **outside any unit**; only then is `EROFS`
accepted, `EACCES` is **`inconclusive`**, and a sandboxed success is a **failed**
stage. And the **two-class attacker model is withdrawn** for an **eight-capability
register** — seal write, journal-directory write, journal-content rewrite,
archive write, deployment-path write, host identity/restoration, coordinator
execution, and PostgreSQL row mutation or insertion — with each falsification row
giving its **minimum capability**, whether that capability also reaches the
**detector**, the refusing actor, the exact step and code, and the **residual when
it reaches both**. **F-2 is corrected to `K3`**, **F-7 is corrected in the
opposite direction** because `/etc/machine-id` is root-writable, and
not-constructible pairings are marked with the control that makes them so.

**No new decision is raised by R7**, and OD-62 through OD-66 are **not decided**.
None of the three corrections introduces a governed choice: two change no host
artifact at all, and the third adds one transient directory to a probe **OD-66
option A** already carries. **OD-66's option A changes in three places and no
others**; options B, C and D, the owners, the authorities and the retention rule
are unchanged, **OD-63 stays at nine controls**, and OD-62, OD-64 and OD-65 are
untouched. The evidence band grows to **fifty identifiers and seventy-four
cases**; the falsification-row count is **corrected from a stated twelve to the
thirteen actually listed**; the estimate rises to PERT **39.5** implementer-days
and the remediation allowance to **11.5**; stop conditions **10i**, **10j** and
**10k** are added; the fail-closed conditions stay at **twenty-five**, the
refusal codes stay `SW-J01 … SW-J25`, V-W stays at eighteen steps, and **no
schema object changes at all**. **A new residual, R-5.0-12**, records the one
combination this design does **not** refuse — host root holding
`CAP_LINUX_IMMUTABLE` **and** a PostgreSQL superuser, which writes both copies
the coordinator compares — as an acceptance question under OD-66 rather than as a
control. The Security Reviewer's scope gains one element, the `…/probe-ro`
directory, and two questions, without a change to the 2.5–3.5 reviewer-day
estimate. **No implementation was performed, no host was read or written, no
`systemd-run`, `chattr` or `setpriv` was run, neither a probe arena nor
`…/probe-ro` was created, and no implementation suite was run.** The Security
Reviewer is still unnamed and the package is still not ready.

**Remediation R10 submitted, 2026-08-31.** Revision 11 of the package plan and
the logical schema, plus `docs/review/phase-5-0-remediation-r10-handback.md`. It
**claims no finding closed.** The defects are conceded before their replacements
are presented, in package plan §2.13.1 rows **25–28**.

**The executable-identity launch mechanism is replaced.** `setpriv(1)` from
util-linux 2.39.3 documents `keep_caps` as *"not allowed"* because `execve`
clears it, so revision 10's E2–E6 recipes exited **127** before any identity
existed; the same page states that the kernel does not permit capabilities to be
**added** to a bounding set, which those five recipes also requested — a third
disagreement the re-review did not name and the mechanical mask-versus-recipe
comparison found. E8 declared an empty bounding set and dropped nothing; E7 wrote
dashes for inheritable and ambient. §2.13.5c is rebuilt on **`capsh(1)`**, whose
manual documents that it acts on its arguments *"in the order they are
provided"* — which `setpriv(1)` does not, and on which every declared mask
depends — with a **seven-step construction** naming the kernel rule behind each
step, exact UID, GID, supplementary-group list, `CapPrm`, `CapEff`, `CapInh`,
`CapAmb`, `CapBnd` **and securebits** for `E1 … E8`, a complete invocation each,
and a comparison table deriving every declared cell from its command line. **No
invocation asks any tool to add to a bounding set**, and the prerequisite that
the launching bounding set already holds every needed capability is stated and
asserted. **Dependent evidence is revalidated**: `JNL-50` case 7 and `JNL-49`
case 11 take **E6** — which differs from E4 by `CAP_FOWNER` alone — as the
isolating positive control instead of **E2**, which differs in uid, groups and
two capabilities and is retained as corroborating; `JNL-50` case 4 gains a second
control form; and two stale copies of superseded wording in the logical schema
are corrected.

**No new decision number and no new option is raised by R10**, and OD-62 through
OD-66 are **not decided**. **OD-66's options do not move at all**: R10 corrects
how the evidence harness constructs identities, not any artifact, authority,
column, refusal code, retention rule or cost of option A, and **option A-2
remains unchanged and not adopted**. **The `capsh` choice is an evidence-harness
mechanism inside unconfirmed assumption A-5.0-5, not a decision**: it installs
nothing, sets no file capability, creates no set-user-ID artifact, adds no
`sudoers` rule, unit, group, account or directory, and changes no production
tool. It is routed to the **Security Reviewer** in package plan §9.2 with the
declined alternatives named. **Every count and estimate is unchanged, with the
reason stated rather than recalculated**: fifty identifiers and **eighty-eight**
cases, **thirteen** falsification rows, **eleven** authorities, **fifteen**
manipulation rows, twenty-five fail-closed conditions, `SW-J01 … SW-J25`, V-W at
eighteen steps, PERT **40.9** implementer-days, remediation allowance **11.9**,
security review **3.5–4.5** reviewer-days, and **no schema object changes at
all**. **R-5.0-12, R-5.0-13 and R-5.0-14 are unchanged and no RAID row is added
or closed**; §7.1 gains row **28** and stop condition **10n** is added for the
recurrence class; **A-5.0-5 is widened and remains unconfirmed**. **No
implementation was performed and no host was written**; the host was **read**
non-mutatingly for the tool contract (package plan §8.1 **H-6**), and no
`systemd-run`, `chattr`, `setpriv` or `capsh` execution altered any credential,
no probe arena, `…/probe-ro` or `fbprobe` identity was created, and no
implementation suite was run. The Security Reviewer is still unnamed and the
package is still not ready. **The independent re-review required at submission
completed on 2026-08-31 with no new Blocking or Important design finding; it
closed R10 only and decided none of OD-62 through OD-66.**

**Superseded — remediation R9 submitted, 2026-08-30.** Revision 10 of the package plan and the
logical schema, plus `docs/review/phase-5-0-remediation-r9-handback.md`. It
**claims no finding closed.** The Blocking defect is conceded before its
replacement is presented, in package plan §2.13.1 rows **22–24**.
**The inode-flag authority model is corrected**: `FS_IOC_SETFLAGS` requires the
caller's effective UID to equal the inode's owner **or** `CAP_FOWNER`, **in
addition to** `CAP_LINUX_IMMUTABLE` for `FS_IMMUTABLE_FL`/`FS_APPEND_FL`, and
`CAP_DAC_OVERRIDE` is **not** a substitute for the owner check. §2.13.5c states
the kernel's checks in a table of their own before the register that encodes
them; **A1** is narrowed to the capability half alone; **A10** (owner
authorization over the `freedomsheet`-owned journal, which the writer holds **by
owning the file**) and **A11** (owner authorization over the root-owned seal and
archive, held only by uid 0 or a `CAP_FOWNER` holder) are added as separate rows;
and the register grows from nine authorities to **eleven**. **Eleven of the
thirteen falsification rows gain a prerequisite** — F-1a, F-4, F-5 and
F-8 … F-12 gain `A11`, F-1b gains `A10` and `A11`, F-2 and F-5 gain `A10` — and
**every one of those changes makes the alteration harder to construct**, so no
refusal is strengthened, no risk is narrowed and no guarantee moves. **The A3/A2
contradiction is removed** by separating what an authority *is* from who can
*hold* it: the register keeps the independence claim for the primitives, a new
**holder table** carries the bundling, and every row's detector reach is assessed
against the smallest identity that can really hold its combination — which
**narrows** the bounded claim to **F-2, F-3 and F-6**. **The executable evidence
contract is rewritten**: eight identities `E1 … E8` with effective UID, GID,
supplementary groups and complete permitted, effective, inheritable, ambient and
bounding capability sets, full `setpriv` invocations **including securebits**
because ambient shorthand builds no such set, and `JNL-49`/`JNL-50` at **twelve
cases each**, every negative flag case running with all other prerequisites
satisfied and carrying a **positive control that succeeds**. **No privileged case
is claimed to have run**, and **A-5.0-5 is corrected rather than carried
forward** — the revision-9 capability-only archive case was not constructible —
and remains **unconfirmed**.

**No new decision number and no new option is raised by R9**, and OD-62 through
OD-66 are **not decided**. **OD-66's option A does not change at all**: R9
corrects the description of a kernel check option A already depended on, so no
artifact, authority, column, refusal code or cost moves. **Option A-2 is
preserved unchanged and remains not adopted**; options **B**, **C** and **D**,
the owners, the authorities and the retention rule are unchanged; **OD-63 stays
at nine controls**; and OD-62, OD-64 and OD-65 are untouched. The R8-A
deployment-digest lifecycle, the R8-B cleanup state machine and the R8-D
withdrawal of F-7's detector are **preserved unchanged in substance**. The
evidence band grows to **eighty-eight cases across the same fifty identifiers —
no identifier is added**; §2.13.4's manipulation matrix grows from thirteen rows
to **fifteen**; the falsification-row count **stays at thirteen**; the estimate
rises to PERT **40.9** implementer-days with the remediation allowance unchanged
at **11.9**; stop condition **10m** is added and **10k** extended; the fail-closed
conditions stay at **twenty-five**, the refusal codes stay `SW-J01 … SW-J25`, V-W
stays at eighteen steps, and **no schema object changes at all**. **R-5.0-12's
authority set is corrected to a larger one**, R-5.0-13 and R-5.0-14 are
unchanged, and **no RAID row is added or closed**; §7.1 gains row **27** for the
recurrence class. The Security Reviewer's estimate rises to **3.5–4.5**
reviewer-days with two added questions and the surface count unchanged at eleven.
**No implementation was performed, no host was read or written, no `systemd-run`,
`chattr` or `setpriv` was run, no probe arena, `…/probe-ro` or `fbprobe` identity
was created, and no implementation suite was run.** The Security Reviewer is still
unnamed and the package is still not ready.

**Superseded — remediation R8 submitted, 2026-08-30.** Revision 9 of the package plan and the
logical schema, plus `docs/review/phase-5-0-remediation-r8-handback.md`. It
**claims no finding closed.** All four Blocking inconsistencies are conceded.
**The deployment digest is now computed and validated against the deployment**:
new §2.13.2c names who computes `deployment_manifest_digest()`, the exact bytes
it covers — every deployed file with its path, mode, uid, gid and content digest,
plus the unit file **and its `.service.d/` drop-ins** — and when it becomes final;
Algorithm C **`C0` computes it and refuses unless the operator's supplied value
equals it**, discarding the supplied string, so `C1` consumes a value checked
against the deployed bytes rather than against a copy of itself, and **`C2`**
keeps a consistency check **and recomputes** to catch a deployment changed since
`C0`. The universal *produced < validated ≤ consumed* claim is **withdrawn** for
five invariants **I-1 … I-5** separating pre-consumption validation of external
inputs from post-production consistency checking of internal values. **Cleanup
failure now has one outcome**: new §2.13.2b is a three-state machine in which
*"no generation artifact"* is unconditional and *"no transient residue"* is
conditional on cleanup success, and the next invocation has **one** behaviour —
`verify-capability` and `C0` **refuse for operator recovery** — revision 8's
automatic clean-and-reuse step being **withdrawn**. **The eight-capability
register is withdrawn** for **nine independently constructible authorities**
separating flag control from discretionary access — `CAP_LINUX_IMMUTABLE` clears
a flag and confers **no** DAC — with each falsification row stating its minimum
**combination**; **F-2 becomes `A1 + A2`**, **F-4 becomes `A1 + A4`** and **F-5
becomes `A1 + A3`**. And **F-7's refusal is withdrawn**: a forged matching
`/etc/machine-id` is seen by neither **W10** nor **C-d**, because the registered
row carries the same value the seal does, so the case becomes residual
**R-5.0-13** with the independent operational evidence that remains named.

**No new decision number is raised by R8**, and OD-62 through OD-66 are **not
decided**. **OD-66's option A changes in two places and no others** — the
deployment digest's computation point, and the cleanup contract, which *removes*
a code path — and neither adds an artifact, an authority, a column or a refusal
code. **A new option A-2 is raised inside OD-66 and is deliberately not
adopted**: option A **plus an independent authenticated host-bound value**, a
TPM-sealed or coordinator-signed host token, which is the only thing that would
make **F-7** a refusal instead of a residual. It **would** add a seal field, a
**V-W** step, a coordinator comparison, a refusal code, a §2.13.6 condition and a
database column, and its principal price is that a **legitimate restore onto
replacement hardware fails closed**. Because it changes the design surface it is
routed to the Acceptance Authority under §0.2 rather than adopted by the
implementer. Options **B**, **C** and **D**, the owners, the authorities and the
retention rule are unchanged, **OD-63 stays at nine controls**, and OD-62, OD-64
and OD-65 are untouched. The evidence band grows to **eighty-four cases across the
same fifty identifiers — no identifier is added**; the falsification-row count
**stays at thirteen**; the estimate rises to PERT **40.4** implementer-days and
the remediation allowance to **11.9**; stop condition **10l** is added, **10b**,
**10f** and **10h** are extended and **10j** is re-worded; the fail-closed
conditions stay at **twenty-five**, the refusal codes stay `SW-J01 … SW-J25`, V-W
stays at eighteen steps, and **no schema object changes at all**. **Two new
residuals** are recorded as acceptance questions under OD-66 rather than as
controls: **R-5.0-13**, the forged matching host identity that nothing here
detects, and **R-5.0-14**, the writer-writable transient directory a failed
cleanup leaves until an operator acts. The Security Reviewer's estimate rises to
**3.0–4.0 reviewer-days** with **no added surface** and two added questions.
**No implementation was performed, no host was read or written, no `systemd-run`,
`chattr` or `setpriv` was run, neither a probe arena nor `…/probe-ro` was
created, and no implementation suite was run.** The Security Reviewer is still
unnamed and the package is still not ready.

**Security Reviewer named — decision by Peter Duscha, 2026-08-31. OD-61 is now
CLOSED.** **Codex is the Package 5.0 Security Reviewer**, in addition to its
existing Independent Reviewer and independent logical-schema reviewer roles. The
role is compatible with implementation-plan §0.3, which bars a reviewer from
approving their own implementation: Codex did not implement Package 5.0. This is
a role assignment only.

**What this decision does not do.** It does not approve an option, close a
finding, confirm an assumption or make the package ready. P5.0-R5 remains
**Blocking**, P5.0-R1 and P5.0-R4 remain open, OD-62 through OD-66 remain
**Open**, A-5.0-3, A-5.0-4 and A-5.0-5 remain unconfirmed, and Package 5.0
remains `not ready`. Implementation, migration, deployment, cutover and Package
5.1+ remain unauthorized.

**Two conditions attach to the assignment.** First, the security review must be a
**distinct security-focused pass**, not folded into a design re-review, as
package plan §9.2 requires; a design re-review that found no Blocking finding is
not a security recommendation. Second, Codex holding both roles means the
Independent Reviewer's design judgement and the Security Reviewer's judgement are
no longer independent of each other; that concentration is accepted knowingly by
the Acceptance Authority and is recorded here rather than left implicit.

**What the reviewer must now receive**, per the handover: revision 11 of
`docs/review/phase-5-0-package-plan.md` and
`docs/review/phase-5-0-logical-schema.md`, the threat and authority model
(package plan §2.13.5c), the open decisions OD-62 … OD-66, and the full
3.5–4.5 reviewer-day scope in package plan §9.2. The briefing pack is
`docs/review/phase-5-0-security-review-brief.md`.

**Consequence for the other decisions.** OD-64, OD-65 and OD-66 are owned *on the
Security Reviewer's review* and remain unrulable until that recommendation
exists. OD-63 carries no Security Reviewer dependency and may be ruled
independently. OD-62 is the risk acceptance the other four price and should be
ruled last.

### OD-62 — The Package 5.0 cutover boundary for the Google Sheet · **OPEN — G-A CONFIRMED IN PRINCIPLE 2026-09-22; BINDING RULING GATED ON P5.0-R5**

**Current direction, 2026-09-22.** Peter Duscha selects G-A in principle and
accepts its late-Google-apply residual in principle because the user base is
small and the cutover time is known and supervised. The choice is not yet
binding: the existing prerequisite remains independent acceptance that
P5.0-R5's enumeration control is fail-closed. Post-cutover Sheet retention is
separate. Plan §15.1 permits retaining the Sheet and rollback path during a
numeric verification window but prohibits dual writes; any updated copy would
have to be a separately reviewed one-way PostgreSQL-to-Sheet diagnostic
projection with no authority.

**Post-cutover retention decision, 2026-09-22.** The source Sheet will be
frozen read-only and retained for four weeks with its export, connector,
credential and documented rollback path. PostgreSQL is the sole authority;
there will be no dual writes and no live diagnostic projection. Retirement
requires the completed four-week verification gate and explicit approval.

**Provisional direction recorded 2026-09-02 — not a ruling.** Peter Duscha
selected G-A as the intended option, but expressly deferred the binding risk
acceptance until P5.0-R5's operational evidence and independent review are
complete. OD-62 remains Open, and this direction neither authorizes WP-4b nor
accepts R-5.0-8.

**Raised 2026-08-29** by the Package 5.0 design remediation (D5.0-9), in response
to Codex Blocking finding P5.0-R1.

**Reframed by remediation R2, 2026-08-29.** The original question — *may Freedom-
bot mutations take a bounded 25-second availability dependency on PostgreSQL?* —
was priced around a leased self-fencing design that does **not** close P5.0-R1,
because a process paused after admission can resume after activation and write
Sheets. Answering it either way would buy nothing, so **the leased options are
withdrawn** and are retained below only as decision history. They must not be
revived.

**What the remediation established, and what is therefore not in question.**

Every PostgreSQL-authoritative write is fenced by a trigger evaluated **inside
the writing transaction**, so a paused-and-resumed process commits nothing. That
half needs no decision: it costs nothing, has no timing behaviour and has no
alternative worth comparing.

The Google Sheet is the half that does. It is not transactional and its API
offers no conditional write — no ETag, no `If-Match`, no revision id, no
compare-and-swap — so the only enforceable controls are that **the writer does
not exist** and that **its access is gone**. Both have costs, and this decision
is about which costs are accepted.

**The question.** Which enforceable boundary is adopted?

- **Option A (recommended).** Isolate the Sheet writer in its own systemd unit,
  `freedom-sheet-writer`; at each fenced transition revoke the service account's
  Drive **write** permission on the spreadsheet, stop the unit, observe
  termination three ways (unit inactive, cgroup empty, host scan clear), run the
  owning package's import or replay, activate, restart the writer, restore the
  permission.
  *Costs:* a fourth systemd unit holding the Google credential; a Sheet-mutation
  outage for the fence window at each cutover and rollback; a production Drive-
  permission change at each cutover.
  *Benefits:* two independent controls with disjoint residuals; the bot stays
  online serving reads, `/info` and every non-mutating command; and **no standing
  PostgreSQL availability dependency for legacy mutations at all**, which the
  leased design would have introduced.
- **Option B.** The same, but stop the whole `freedom-bot` unit instead of a
  separate writer.
  *Costs:* a full bot outage — not merely refused mutations — at every one of
  roughly forty cutovers and at every rollback; the production access change
  remains.
  *Benefits:* no fourth unit, no IPC boundary, a materially smaller change to a
  live service.
- **Option C.** Isolation and termination only, with no Google access change.
  *Costs:* the out-of-systemd duplicate and the already-dispatched call remain
  open. The implementer's assessment is that this **does not close P5.0-R1**, and
  it is listed so the reviewer can disagree with that assessment rather than have
  it hidden.
  *Benefits:* no production access change.
- **Option D.** None of them, and P5.0-R1 stays open. Package 5.0 delivers the
  database-side fence — complete for PostgreSQL writes on its own — plus
  detection for the Sheet, and the first cutover waits for an accepted boundary.

**Why an agent could not decide the revision-3 framing.** `.agents/AGENTS.md`
forbids weakening, disabling or degrading the Freedom bot **and** forbids
production credential and access changes without approval. Every option touched
one of those rules. It was a production-availability, topology and external-access
choice.

**Coupled to OD-63.** Option A's second control depends on how fast a Drive
permission change propagates, which Google does not contractually specify.
Package 5.0 work package WP-13 measures it against a **disposable** spreadsheet
and a **disposable** service account before N5.0-18 is fixed. If those disposable
resources are unavailable (assumption A-5.0-3, unconfirmed) the measurement
cannot be made, the Google-side control cannot be relied on, and the option set
narrows to B or D.

**Independent-review constraint added 2026-08-29.** WP-13 measurement may
inform an operational timeout, but cannot close P5.0-R1: Google publishes no
maximum propagation or accepted-request completion guarantee. Before Peter can
rule Option A or B an enforceable boundary, remediation R3 must identify an
externally verifiable barrier proving that every request accepted before
revocation is reflected before the final import, or reframe the choices around
the conclusion that this API cannot provide that guarantee.

---

**Reframed a third time by remediation R3, 2026-08-29. This is the current
question; the two framings above are decision history and are retained below.**

Remediation R3 took the second route the constraint permits. Thirteen candidate
barriers were traced against the published Sheets v4 and Drive v3 surface — the
`batchUpdate` response, an operation identifier, an idempotency token, a
conditional write, `files.version`, `revisions.list`, the Activity API, push
notifications, a marker write, protected ranges, a file copy, Apps Script
`flush()`, and waiting — and each either reduces to a quiet period, rests on an
unpublished implementation property, is documented as unreliable, or does not
exist. **The conclusion is that the published Google APIs cannot supply the
barrier**, and the implementer claims P5.0-R1 no more closed than before.

> **The invariant that cannot be guaranteed.** *Every
> `spreadsheets.values.batchUpdate` request Google accepted before the fence
> began is durably reflected in the spreadsheet before the final import reads
> it.*

**The weaker guarantee that is achievable**, and is what the design now offers:
the writer is **drained before it is killed**, so every request that completed
normally has an observed response; a **durable, sealed, generation-bound,
hash-chained** dispatch journal makes anything outstanding **enumerable**; a
non-empty unresolved set — **or any unknown journal state** — **refuses the
activation**; a late apply **cannot reach PostgreSQL**; and two post-import
re-reads **detect** it inside the verification window.

**Corrected by remediation R4, 2026-08-29.** The journal is a completeness aid,
not a proof — a writer whose *dispatch path itself* was replaced can omit an
entry, which is risk **R-5.0-10**. The earlier sentence *"nothing in the fence
depends on it"* is **withdrawn as false**, because `dispatch_journal_clear` is one
of five required fence methods. The journal **can refuse** an activation the other
four would permit and **can never permit** one they would refuse; an incomplete
journal therefore removes a refusal rather than manufacturing a permission.
Revision 4 additionally placed this file on volatile `/run`, where a reboot
produced an *empty* unresolved set and so a *permitted* cutover; remediation R4
moves it to durable, root-owned storage with a sealed and registered generation.
**None of that is a barrier**, and the residual below is unchanged.

**Impacts recorded by remediation R5, 2026-08-30 — this decision is not made
here.** Revision 5's journal could not actually be built: its seal and its
genesis record each hashed the other. Revision 6 replaces that with an acyclic
order (package plan §2.13.5a), gives the writer the **minimum read-only** access
to the seal it is required to validate, makes the append-only capability probe
attributable rather than assumed, and **withdraws** the claim that a database
`CHECK` proved a host probe had run. The effect on this decision is confined to
three things. **Cost:** option G-A gains a **third system group**,
`freedomjournal`, at provisioning, and a **disposable probe arena** that must not
outlive provisioning; against that, `…/journal` tightens from `0751` to `0750`,
so `discordbot` and `freedomweb` lose directory traverse they had in revision 5.
**Failure behaviour:** the fail-closed conditions grow from twenty-one to
**twenty-five**, so the bounded-outage cost named in **R-5.0-11** grows with
them. **Authority, topology and retention are unchanged**: the same owners, the
same `/var/lib/freedom-sheet-writer` hierarchy, the same N5.0-23. **The residual
is unchanged and is not narrowed by a single case**, and none of revision 6 is a
barrier or may be described as one.

**The residual, in one sentence.** *A request Google accepted, whose response
never reached the writer, and which Google applies after the final import has
read the Sheet, is not prevented and cannot be proved absent.*

**The question is therefore no longer which fence, but what is accepted in place
of one.**

- **Option G-A (recommended).** The drain-first boundary above, with the isolated
  writer, the explicit request timeout, the journal, the access revocation and
  the two divergence re-reads. *Costs:* a fourth systemd unit and a fifth OS
  identity; a Sheet-mutation outage per fence window; a production Drive-permission
  change per cutover; an `fsync` on the legacy mutation path; an operator
  adjudication step; **a third system group and a disposable probe arena at
  provisioning** (remediation R5); **and the residual, accepted explicitly.**
- **Option G-B.** Pre-cutover write-path retirement — deploy a build without the
  migrating unit's Sheet write path, refuse those mutations for an accepted
  period, then import. Stronger *in kind*, because the in-flight set is empty by
  deployment rather than by timing. *Costs:* a mutation outage measured in days,
  roughly forty times. **Variant G-B′** does it once for the whole bot.
- **Option G-C.** Accept a measured quiet period as the boundary. **This is what
  the re-review rejected**; it is listed so the residual can be accepted knowingly
  rather than relabelled, and it is not recommended.
- **Option G-D.** Cut no Sheet-authoritative unit over. Package 5.0 still delivers
  the PostgreSQL fence — complete on its own — the isolated writer, the journal,
  the access control, the detection and the monitoring, and the first
  Sheet-authoritative cutover waits for an accepted authority design. *Costs:*
  Phase 5's field cutovers do not proceed; shadow comparison and the platform
  build continue.

**Why an agent cannot decide this, and why the reason has changed.**
`.agents/AGENTS.md` still gates bot degradation and production access changes.
The stronger reason is that G-A, G-B and G-C all require **someone to accept an
unprovable residual on the authoritative store of a live community's game
state**. That is a risk acceptance under implementation-plan §0.2 and §0.3 and
belongs to the **Acceptance Authority**. An implementer who took it would be
deciding the project's tolerance for silent data loss.

**Owner:** **Acceptance Authority and Product Owner**, with the Operations Owner
and the Security Reviewer.
**Required by:** before Package 5.0 WP-4b. The barrier search is
`docs/review/phase-5-0-package-plan.md` §2.10.1, the conclusion §2.10.2, the
achievable guarantees §2.10.3, the seven required cases §2.10.4 and the priced
options §2.10.5. The boundary of every claim the design makes is
`docs/review/phase-5-0-logical-schema.md` §2.8.

---

**Decision history — the withdrawn revision-2 framing.** Retained so the record
shows what was considered and why it was not approvable, and not to be revived:

> Closing P5.0-R1 requires a fence that acts at request time rather than at
> process start. The recommended design leases authority from PostgreSQL and
> refuses to admit a mutation once the lease has less than a clock-skew allowance
> plus one operation budget of headroom left. **Does the Freedom bot's mutation
> path take a bounded availability dependency on PostgreSQL — proposed grace 25
> seconds — after which mutations are refused with a typed retriable error?**
> Option A: yes. Option B: no, stop the bot for each cutover instead. Option C:
> neither, and P5.0-R1 cannot be closed.
>
> **Why it was withdrawn:** a process suspended between its headroom check and
> its external write, and resumed after the lease horizon, still emits one legacy
> Sheet write. The invariant rested on probability rather than on a boundary.

### OD-63 — Package 5.0 fencing numeric controls · **CLOSED 2026-09-02 — OPTION 1**

**Ruling, 2026-09-02.** Peter Duscha approved Option 1 as Operations Owner,
Product Owner, Data Owner for N5.0-23, and Acceptance Authority. All nine values
below are accepted. N5.0-18 is accepted only with its attached status:
**120 seconds — an operational margin, not a barrier**. A-5.0-3 remains
unconfirmed; a later WP-13 measurement may inform a re-ruling but cannot turn a
measured distribution into a maximum. This ruling closes no risk, adopts no
other option, and authorizes no implementation, migration, deployment or
cutover.

**Raised 2026-08-29** by the Package 5.0 design remediation (D5.0-10).

OD-57 accepted N5.0-1 … N5.0-8, which are unchanged.

**Reduced by remediation R2, 2026-08-29.** Revision 2 proposed seven controls,
six of which existed only to make a lease work. **N5.0-9 (lease time-to-live),
N5.0-10 (renewal interval), N5.0-11 (clock-skew allowance), N5.0-12
(admitted-operation budget), N5.0-13 (quiesce acknowledgement expectation) and
N5.0-15 (the fence's share of a cutover window) are withdrawn**, and with them
the derived 25-second Freedom-bot grace period. A withdrawn number is recorded as
withdrawn with its reason and is never silently reused.

**Extended from four to six by remediation R3, and from six to nine by
remediation R4, 2026-08-29.** Two of the original four were described as bounds
they cannot be, and R3's barrier search (OD-62) shows why; R4 adds three numbers
for the dispatch journal's storage lifecycle, which revision 4 had none of. Nine
controls now remain to be ruled, proposed with reasoning in
`docs/review/phase-5-0-package-plan.md` §8.3:

| Ref | Threshold | Proposed | State |
|---|---|---|---|
| N5.0-14 | Activation deadline after `effective_at` | **24 hours** | unchanged |
| N5.0-16 | Maximum age of a quiescence observation at activation | **15 minutes** | unchanged |
| N5.0-17 | The Sheet writer's **drain timeout** — how long it is given after `SIGTERM` to refuse new work, finish outstanding calls and record their outcomes, before the `SIGKILL` escalation. It is the unit's `TimeoutStopSec` | **45 seconds**, and it must exceed N5.0-19 with margin | **reframed.** It was described as a settle interval bounding a call already dispatched to Google. It cannot bound that; nothing can. What it can bound is our own client's wait for its own response |
| N5.0-18 | The **post-revocation margin** before the final import reads the Sheet | **120 seconds — an operational margin, not a barrier** | **reframed.** Google publishes no propagation guarantee, so no value of this number bounds anything, and the register must carry that sentence beside it. A measured distribution is not a maximum |
| **N5.0-19** | The Sheets client's explicit per-request timeout | **30 seconds** | **new.** `connectors/sheets.py` sets none today, so the in-flight window is unbounded by anything the repository states. N5.0-17 cannot be chosen until this exists |
| **N5.0-20** | Maximum unresolved dispatch-journal entries permitted at activation | **zero** | **new.** A control rather than a tolerance: one unresolved entry refuses the cutover and is adjudicated by a human. Any non-zero value would silently decide that some unknown writes are acceptable — which is exactly the decision OD-62 puts to the Acceptance Authority explicitly |
| **N5.0-21** | Minimum free space on the journal filesystem below which the writer refuses to dispatch | **1 GiB** | **new, remediation R4.** The volume holds 135 GiB free today and a journal record is a few hundred bytes, so the floor costs nothing. Its job is to make disk-full a refusal **before** the Google call rather than an `ENOSPC` discovered after it. A value of zero would mean *dispatch first, journal if you can*, which is the failure direction the control exists to prevent |
| **N5.0-22** | Maximum current-journal size before a privileged rotation is required | **64 MiB** | **new, remediation R4.** At roughly 400 bytes per record and two records per Sheet write, that is on the order of 80 000 writes — far beyond this bot's traffic for the whole of Phase 5. It exists so the file cannot grow without a decision and so that chain re-reads stay bounded. Exceeding it is an operational signal, not a refusal to dispatch |
| **N5.0-23** | Retention of a sealed, archived journal generation before disposal may run | **until plan §15.1's Sheet-retirement gate closes, and in no case less than 365 days** | **new, remediation R4, and the only number in this register owned by the Data Owner.** It is the record of what the platform wrote to a live community's Sheet and of what was outstanding at each fence. A shorter period would allow a generation to be destroyed inside a verification window that might still need it |

**N5.0-18 may be re-ruled after WP-13 measures it**, but the coupling to
OD-62 is weaker than it was: an unmeasured margin no longer removes a control,
because the margin was never one. **WP-13 is demoted accordingly** — it informs a
number and closes nothing.

**Owner:** Operations Owner and Product Owner; **N5.0-23 additionally the Data
Owner**, because it governs when evidence may be destroyed. **Required by:**
before Package 5.0 WP-1 completes.

### OD-64 — The Package 5.0 authority-plane database principal · **CLOSED 2026-09-02 — OPTION A**

**Decision.** Peter Duscha approved Option A in the Product Owner, Operations
Owner and Acceptance Authority roles. Package 5.0 will introduce
`freedom_migration_coordinator` together with the dedicated `freedomcoord` OS
identity, ordered peer/HBA and identity mapping, the narrow `sudoers` boundary,
the pinned wrapper and the root-owned reviewed deployment path. This closes the
design choice; the specified operational denial evidence is still required for
readiness and P5.0-R4 disposition.

**Raised 2026-08-29** by the Package 5.0 design remediation R2 (D5.0-11), in
response to Codex Blocking finding P5.0-R4.

**The finding.** All application processes share one restricted runtime role. In
revision 2 that role could update every authority lease and insert
acknowledgements for any instance, so a defective or compromised process could
forge another process's quiescence proof and make the activation trigger accept
false evidence. *"Each process, its own row only"* was an application convention
the grants contradicted.

**What the remediation does about it, and what still needs a ruling.** The
remediation removes self-attested proof entirely: both runtime-written tables are
withdrawn, no application process authors any authority proof for any instance
including its own, and quiescence evidence is *observed* by a supervisor — systemd
state, an empty cgroup, a clear host scan, Google's own response to a permission
change — rather than reported by the process being fenced. Row-level security with
per-role principals was compared and rejected as the primary control: `current_user`
is a role, not a process instance, so it stops cross-process forgery and does
nothing about a process forging its own proof, which is the case that matters.

That leaves one question, and it is a security and credential-topology question
rather than a design preference.

**Independent-review constraint added 2026-08-29.** PostgreSQL-role separation
alone does not establish peer-authentication isolation. Remediation R3 must name
a dedicated coordinator OS account distinct from every service account; specify
the exact `pg_hba.conf` and, if used, `pg_ident.conf` mapping; define the
sudo/polkit execution boundary and operator-code/configuration ownership; and
require denial tests for every runtime OS identity. Until then, the assertion
that no service can authenticate as `freedom_migration_coordinator` is unproved
and P5.0-R4 remains Blocking.

**The question.** Is `freedom_migration_coordinator` introduced?

- **Option A (recommended).** A distinct PostgreSQL role, **peer**-authenticated
  over the Unix-domain socket by the host account that runs
  `python -m tools.migration_authority`, holding `SELECT, INSERT` on the three
  append-only authority tables and nothing else — while the shared runtime role
  holds `SELECT` on four of the five Package 5.0 tables and **nothing at all** on
  the quiescence-evidence table.
  *Cost:* one new database role and one `pg_hba.conf` line; a security and
  operations impact assessment.
  *Benefit:* no application process can write any authority row, so the forgery
  class is **unconstructable** rather than defended; and **there is no new secret
  to distribute or rotate**, because peer authentication makes the secret host
  access, which the break-glass custody document already governs.
- **Option B.** Use the existing schema-owner credential for the coordinator.
  *Cost:* the operator command runs with DDL rights it does not need, and the
  append-only triggers become the only thing between an operator typo and the
  schema.
  *Benefit:* no new role at all.
- **Option C.** Keep one shared principal and rely on the application to restrict
  who writes. **This is the P5.0-R4 finding.** Listed for completeness and not
  recommended.

**Why an agent cannot decide this.** It is a database-role and credential-topology
change. `.agents/AGENTS.md` requires a maintainer decision for authorization and
migration/rollback strategy changes, and the handoff requires an impact
assessment and the named Security Reviewer's review for any new database
credential, role topology, security-definer function or RLS policy.

**It does not change the accepted production topology.** OD-20, OD-21 and OD-22
stand: same host, loopback, separate roles and environment files, no shared
credential. If a preferred solution *would* change the accepted topology or
credential contract, work stops and Peter's ruling is requested before it is
treated as binding.

> **Corrected by remediation R3, 2026-08-29.** The paragraph above was true of the
> database role considered alone and is **not** true of the control. A
> peer-authenticated role isolates nothing until the operating-system identity it
> trusts is named, and naming it requires an OS account, a `sudoers` drop-in, a
> `pg_ident` map and a deployment path outside the repository. **This decision
> does change the accepted topology**, which is why it is extended below and why
> OD-65 is raised. OD-20/21/22's substance still stands; the claim of *no change*
> does not.

---

**Extended by remediation R3, 2026-08-29. This is the current question.**

The re-review's point is that the earlier question was incomplete: peer
authentication trusts an **operating-system** identity, and revision 3 never said
which one. A role any local process can authenticate as is not isolated; it is
renamed. **Approving the database role without the host boundary would approve a
control that does not exist**, so the decision now covers both halves.

Remediation R3 supplies the missing specification —
`docs/review/phase-5-0-package-plan.md` §2.12 and
`docs/review/phase-5-0-logical-schema.md` §4.3:

- a dedicated **`freedomcoord`** OS user and group, distinct from `discordbot`,
  `freedomweb`, the proposed `freedomsheet` and `foundry`, in no group any of them
  holds, with no password, no login shell, no home directory and no SSH key;
- `pg_hba.conf` lines placed **above** any broader rule — one `peer` line with
  `map=freedom_coord` for the production database, then `local all … reject` and
  three `host`/`hostssl`/`hostnossl` rejects written out so a later broad rule
  cannot silently expose the role;
- a single `pg_ident.conf` line, no regular expression, no wildcard;
- the role created `PASSWORD NULL`, so password authentication can never succeed
  and a leaked `.pgpass` is worthless;
- a `sudoers` drop-in (`root:root 0440`) naming **`foundry` only**, with
  `env_reset`, `!setenv`, `secure_path`, `log_output`, **no `NOPASSWD`**, and one
  fixed absolute executable — a root-owned wrapper rather than `python -m …`; and
- a root-owned deployment path `/opt/freedom-blades/coordinator`, **outside the
  repository**, with digest verification at deploy.

**The last item exists because of an observed host fact, not a hypothesis.**
`/opt/freedom-blades/platform` is `drwxrwsr-x foundry:discordbot` with
group-writable files, and `freedomweb` is a member of group `discordbot` (read
2026-08-29). **The bot, web and worker processes can today rewrite every module in
the repository, including `tools/` and `migrations/`.** A coordinator running
`python -m tools.migration_authority` from that tree would execute code a
compromised service process can choose.

**The question.** Is `freedom_migration_coordinator` introduced **together with**
that host boundary?

- **Option A (recommended).** The role and the dedicated `freedomcoord` identity,
  the peer map, the `sudoers` boundary and the root-owned deployment path.
  *Cost:* one OS account, one `sudoers` file, two PostgreSQL configuration lines
  and a reload, one deployment path. *Benefit:* four independent layers must all
  hold before a connection succeeds; no secret exists to steal; every claim is
  testable one runtime identity at a time.
- **Option B.** The role, but mapped to the existing `foundry` operator account.
  *Cost:* no separation between the maintainer's general-purpose account and the
  authority principal. It still needs the root-owned deployment path. *Benefit:*
  no new OS account.
- **Option C.** The schema-owner credential — the revision-3 Option B, which
  inherits every problem of Option B and adds DDL rights.
- **Option D.** One shared principal. **This is the P5.0-R4 finding.**

**This does change the accepted topology**, unlike the revision-3 framing, which
is why it is raised rather than adopted. **The two checks the implementer could
not run** — enumerating `/etc/sudoers.d/` and a host-wide setuid audit — are the
Security Reviewer's to complete, and are recorded as not run rather than assumed
clear.

**Owner:** Product Owner and Operations Owner, on the Security Reviewer's review.
**Required by:** before Package 5.0 WP-2 **and WP-14**. The option comparison is
`docs/review/phase-5-0-package-plan.md` §2.11 and §2.12.8; the identity,
authentication, grant and evidence model is
`docs/review/phase-5-0-logical-schema.md` §4.3.

### OD-65 — The host changes the Package 5.0 boundary requires outside the coordinator · **CLOSED 2026-09-02 — OPTION B**

**Decision.** Peter Duscha approved Option B in the Operations Owner, Product
Owner and Acceptance Authority roles. Adopt the dedicated `freedomsheet`
identity and credential relocation, live bot hardening, reviewed-source
provenance objects, and canonical identity/group membership controls. Defer the
existing group-writable worktree correction to a separately planned maintenance
change. The approved Package 5.0 deployment path must read no executable input
from that worktree. Operational verification remains required for readiness.

**Raised 2026-08-29** by Package 5.0 design remediation R3 (D5.0-12).

Three changes that the §2.12 boundary depends on, that are **not** about the
coordinator principal, and that each touch a live service. They are separate from
OD-64 because they have a different owner and a different blast radius, and
because two of them are pre-existing conditions the design would otherwise be
silently relying on.

1. **A dedicated `freedomsheet` OS identity for `freedom-sheet-writer`, and the
   Google service-account credential relocated to
   `/etc/freedom-blades/sheet-writer.env` (`root:freedomsheet`, `0640`).** The
   writer must not run as `discordbot`, which has a login shell and group write
   access to the whole repository. *A credential relocation; needs the Security
   Reviewer.*
2. **Hardening directives added to `freedom-bot.service.tmpl`** —
   `NoNewPrivileges=true`, `PrivateTmp=true`, `ProtectSystem=strict`,
   `ProtectHome=true` — closing Phase 0 topology finding **F-3**, still open.
   Every *"a service cannot gain privileges"* argument is weaker for the bot than
   for web and worker until this is done. *A change to a live unit; needs the
   Operations Owner.*
3. **A ruling on the group-writable repository tree.**
   `/opt/freedom-blades/platform` is group-writable by `discordbot` and
   `freedomweb` is in that group, so all three service processes can rewrite every
   module including `migrations/` and `.git`. Package 5.0 **works around** this
   with the root-owned deployment path rather than fixing it, because fixing it
   would change how the maintainer edits and deploys the repository — wider than
   this package. *The workaround is sufficient for the coordinator and does not
   make the condition acceptable.*
4. **A third system group, `freedomjournal`** (added by remediation R5,
   2026-08-30). It holds exactly `freedomcoord` and `freedomsheet`, carries **no
   database privilege** and owns no service. It exists so the writer can *read* the
   journal seal that revision 6 requires it to validate, while
   `/var/lib/freedom-sheet-writer/journal` tightens from `0751` to
   `root:freedomjournal 0750` and the seal is `root:freedomjournal 0440`. **The
   net effect is narrower than revision 5**, which left *other* with directory
   traverse: `discordbot` and `freedomweb` lose it. A world-readable `0444` seal
   was considered and rejected for that reason. *An operating-system change;
   needs the Operations Owner.*

- **Option A (recommended).** All four.
- **Option B.** Items 1, 2 and 4; item 3 deferred to a separate maintenance change.
  The condition persists and the deployment-path workaround carries the whole
  weight.
- **Option C.** None; the writer runs as `discordbot` on an unhardened unit. **The
  implementer's assessment is that the §2.12.6 argument does not hold under this
  option**, and it is listed so that assessment can be disagreed with rather than
  hidden. Under option C item 4 is also absent, so the writer cannot read the
  seal and the revision-6 validation contract does not hold either.

**Owner:** Operations Owner and Product Owner, on the Security Reviewer's review.
**Required by:** before Package 5.0 WP-4b and WP-14. Statement and pricing:
`docs/review/phase-5-0-package-plan.md` §5.3 and §2.12.1.

### OD-66 — The dispatch journal's durable storage, generation lifecycle and evidence-disposal authority · **CLOSED 2026-09-02 — OPTION A / J-1**

**Decision.** Peter Duscha approved Option A / J-1 in the Operations Owner,
Data Owner and Acceptance Authority roles: durable root-owned storage, sealed
and PostgreSQL-registered generations, the independently revocable privileged
journal lifecycle, reviewed-source provenance, and the accepted N5.0-23
retention/disposal rule. Options A-2 and A-3 are not adopted. This approval does
not silently accept R-5.0-12 through R-5.0-16; they retain their required
explicit dispositions. P5.0-R5 remains Blocking until the operational evidence
is produced and independently reviewed.

**Raised 2026-08-29** by Package 5.0 design remediation R4 (D5.0-13), in response
to Codex Blocking finding P5.0-R5.

**The finding.** Revision 4 specified the dispatch journal in a single table row:
a `fsync`-ed, `chattr +a` file at `/run/freedom-sheet-writer/dispatch.journal`.
Two facts about this host defeat it. `/run` is a **separate volatile `tmpfs`
mount** — read from `/proc/mounts` — so a reboot empties the file. And the
`chattr +a` claim was **inferred** from `/opt/freedom-blades` being ext4, a
different path, and a filesystem type is in any case not a runtime capability
test. Because an *empty* unresolved set is the answer that lets the coordinator
record `dispatch_journal_clear`, a lost, replaced or reset journal turned unknown
history into a **permitted** cutover: the failure direction inverted from safe to
unsafe exactly where it mattered.

**What the remediation does about it.** Package plan §2.13 replaces the row with a
contract in eleven subsections (**sixteen after revision 6**) — the storage decision and the five candidates it
rejects, the hierarchy with an owner, group, mode, filesystem and authority for
every artifact, the manipulation matrix with an expected `errno` per attempt, the
sealed and registered generation, a twenty-one-condition fail-closed state table
(**twenty-five after revision 6**),
the privileged lifecycle, the record format and evidence band, the completeness
statement, the separation from the Google residual, and the priced options.
Logical schema §3.7 adds the sixth table, §3.5 three evidence columns, §3.4 a
fifth activation-trigger condition and §2.9 the completeness statement.

**Re-stated again by remediation R8, 2026-08-30. Still not decided, and still
not recommended into effect.** The revision-8 re-review found four internal
inconsistencies: the supplied deployment digest was consumed at `C1` and its
equality checked at `C2` against the probe's copy of that same string, so the
check was both late and vacuous; `JNL-47` and `JNL-48(d)` required one injected
cleanup failure to leave two mutually exclusive residue states, and the next
invocation was given both a self-cleaning and a refusing path; the capability
register credited `CAP_LINUX_IMMUTABLE` **alone** with archive and journal writes
that Unix DAC refuses it; and **F-7** claimed a coordinator refusal for a forged
matching `/etc/machine-id` although the registered row carries the same value.
**Revision 9 corrects all four**, and what is on offer for a ruling is the
revision-9 contract. **Option A's content changes in exactly two places**, and
both are corrections rather than new capabilities:

- **where the deployment digest is computed and checked.** New §2.13.2c names the
  computor, the exact manifest — every deployed file with its path, mode, uid,
  gid and content digest, plus the unit file **and its `.service.d/` drop-ins** —
  and the instant it becomes final. **`C0` computes it and refuses unless the
  operator's supplied value equals it**, and the supplied string is then
  discarded; **`C2`** keeps a consistency check against the report and
  **recomputes the manifest** to catch a deployment changed since `C0`. The
  universal ordering claim is replaced by invariants **I-1 … I-5**. **This adds a
  specification and a computation, and no host artifact, authority, digest,
  storage location, invalidation rule, column or refusal code whatever.**
- **what a failed cleanup leaves.** New §2.13.2b is one three-state machine:
  probe-stage failure with cleanup succeeding leaves **no residue and no
  artifact**; cleanup failure leaves **no artifact** and **the exact residue,
  reported by absolute path**; success proceeds. **“No generation artifact” is
  unconditional; “no transient residue” is conditional on cleanup success.** For
  the next invocation the design now specifies **one** behaviour — both privileged
  commands **refuse for operator recovery** — and revision 8's automatic
  clean-and-reuse step is **withdrawn**. **This removes a code path from option A
  and adds an operator procedure to the operations document.** Its cost is
  **R-5.0-14**: a writer-writable transient directory persists, and generation
  creation is blocked, until an operator acts.

**And one thing this option should now be ruled on knowingly.** The threat model
is rewritten as **nine independently constructible authorities**, separating flag
control from discretionary access, and that rewrite makes a limit explicit that
revision 8 had described as a refusal: **an actor holding root on whichever host
the tree is read on can rewrite `/etc/machine-id` to the recorded value, after
which neither the writer nor the coordinator refuses**, because every copy of
that fact — the seal, the file and the registered row — carries the same value.
That is residual **R-5.0-13**, and it is an acceptance question rather than a
control.

- **New option A-2, raised by R8-D and deliberately not adopted.** Option A
  **plus an independent authenticated host-bound value** — a TPM-sealed key whose
  public half the seal carries, or a coordinator-signed host token held
  `root:root 0400` outside the journal tree — provisioned once per host by the
  Operations Owner before the first `init-generation`, rotated by forcing a
  rotation exactly as a redeployment already does, and verified by a new **V-W**
  step and a new coordinator comparison. **It would make F-7 a refusal instead of
  a residual.** Its cost is a new secret with a custody model, a hardware or
  credential dependency, a seal field, a refusal code beyond `SW-J25`, a
  §2.13.6 condition, a column in `sheet_writer_journal_generations`, at least
  three new `TC-5.0-JNL` cases — and, the price that matters, **a legitimate
  restore onto replacement hardware that fails closed**: a TPM-sealed value cannot
  be restored at all and a token must be re-issued, so disaster recovery gains a
  manual, authority-bearing step in a design whose whole purpose is that evidence
  survives a restore. **Because it changes the design surface it is the Acceptance
  Authority's under §0.2, on the Security Reviewer's and the Operations Owner's
  advice, and the implementer does not adopt it.**

**Everything else about this decision is again unchanged**: the four elements
below, their **authority, topology and retention**, options **J-1 … J-4**, the
owners, and N5.0-23. **No new decision number is raised, the numeric register
stays at nine, and no schema object changes.** The estimate moves to PERT
**40.4** implementer-days, the evidence band to **eighty-four cases across fifty
identifiers**, the falsification rows **stay at thirteen**, and the
security-review estimate rises to **3.0–4.0 reviewer-days** with **no added
surface**.

**Re-stated by remediation R7, 2026-08-30. Retained. Still not decided, and still
not recommended into effect.** The revision-7 re-review found that each of
revision 7's own corrections reproduced, one level down, the defect it was
correcting: **Algorithm C step `C0` consumed a probe result step `C1` had not yet
produced**, so the construction had no executable order; **Stage 4 case `S4-2`
attributed `EROFS` to the systemd sandbox without proving its exact target
writable outside it**; and **the attacker classes claimed reach their
capabilities could not construct**, with `F-2` assigned class 1 while conceding
it needs class 2. **Revision 8 corrects all three**, and what is on offer for a
ruling is the revision-8 contract. **Option A's content changes in exactly three
places**, and all three are corrections rather than new capabilities:

- **the order in which a generation is created.** Algorithm C is renumbered
  **`C0 … C13`**: `C0` keeps only preconditions observable before the probe runs,
  `C1` remains the single probe invocation and the single creation point of the
  report, and a new **`C2`** validates pass state, report completeness,
  deployment-digest equality and cleanup success **before any persistent artifact
  exists**. A value-dependency table makes *produced < validated ≤ consumed*
  checkable per value. **This adds a step number and no host artifact, authority,
  digest, storage location, invalidation rule or refusal code whatever.**
- **Stage 4's target.** The exact target is named — `…/probe-ro/s4-2.target`, in a
  **second transient directory** `root:freedomsheet 0770` on the same mount,
  inside `ProtectSystem=strict`'s read-only tree and **outside** the substituted
  `ReadWritePaths=` — and a new case **`S4-0`** proves it writable, appendable,
  `fsync`-able, renamable and unlinkable by `freedomsheet` **outside any unit**
  before any `EROFS` is interpreted. **The cost to this option is one transient
  directory, created and destroyed inside `verify-capability` and removed in the
  same `finally`**; it is added to the same security-review surface as the arena,
  with its own reviewer question. `EACCES` under the sandbox becomes
  **`inconclusive`** and a sandboxed success becomes a **failed** stage.
- **the threat model.** The two attacker classes are withdrawn for an
  **eight-capability register**, with each falsification row stating its minimum
  capability, whether that capability also reaches the detector, the refusing
  actor, the exact step and code, and the residual when it reaches both. **This
  adds no mechanism at all**, and it makes one thing explicit that this decision
  should be ruled on knowingly: **an attacker holding host root *and* PostgreSQL
  superuser authority writes both copies the design compares, and no check here
  refuses that** — recorded as residual **R-5.0-12**, detected by `sudo
  log_output`, journald, `audit_events` and offline backups, and not prevented.

**Everything else about this decision is again unchanged**: the four elements
below, their **authority, topology and retention**, options **J-1 … J-4**, the
owners, and N5.0-23. **No new decision number is raised, the numeric register
stays at nine, and no schema object changes.** The estimate moves to PERT
**39.5** implementer-days and the evidence band to **fifty identifiers and
seventy-four cases**; the falsification-row count is corrected to **thirteen**;
the fail-closed conditions stay at **twenty-five**.

**Re-stated by remediation R6, 2026-08-30. Retained.** The revision-6 re-review found that the corrected
contract described three of its own artifacts more strongly than it built them:
the immutable probe report was said to cover four stages while Algorithm C sealed
three, the fourth running later at deployment; falsification case F-1 claimed the
writer refuses every seal-byte alteration without PostgreSQL, although
`BND.sealed_at` passed every V-W step; and `JNL-32` expected a `startup` record in
a branch W9 refuses before W17. **Revision 7 corrects all three**, and what is on
offer for a ruling is the corrected contract, not the revision-6 one. **Option
A's content changes in exactly two places**, and both are corrections rather than
new capabilities:

- **where the probe's sandbox stage runs.** It moves from deployment to
  **provisioning**, inside the same `verify-capability` invocation and **before**
  the report is built, so the sealed digest covers the four stages it names. The
  cost of that is a **transient `systemd-run` unit started as root** at
  provisioning, carrying the deployed writer unit's hardening directives with
  `ReadWritePaths=` redirected to the disposable arena, and a requirement that the
  writer's unit file be **deployed** before a generation can be created. The
  benefit is that **no second evidence artifact, digest, authority, storage
  location, invalidation rule, column or refusal code exists**: invalidation
  reuses the rotation a redeployment already forces. The alternative — a second
  typed artifact for deployment evidence — is priced and rejected in package plan
  §2.13.2a on its own requirement, that the writer cannot authenticate such a file
  without PostgreSQL. **This is a design choice inside this option, made in the
  open and recorded here rather than adopted.**
- **what the seal's binding section contains.** It loses `sealed_at` and its own
  format field, keeping exactly the three values the writer's **V-W** algorithm
  recomputes or compares, with its structure fixed by a `binding_format_version`
  carried in the chain-authenticated seal body. **The consequence for this
  decision is that option J-2 is worse than revision 6 made it look**: the
  registered row is now identified as the **only** artifact that refuses a
  `CAP_LINUX_IMMUTABLE` rewrite of the seal *and* the journal's record 0
  (falsification case **F-1b**), so dropping the PostgreSQL registration drops
  the only cover for that case.

**Everything else about this decision is unchanged**: the four elements below,
their **authority, topology and retention**, options **J-1 … J-4**, the owners,
and the retention rule N5.0-23. **No new decision number is raised, the numeric
register stays at nine, and no schema object changes.** The estimate moves to
PERT **38.2** implementer-days and the evidence band to **forty-five identifiers
and forty-eight cases**; the fail-closed conditions stay at **twenty-five**.

**Re-stated by remediation R5, 2026-08-30. Retained.** The revision-5
re-review found that the contract above, as written, could not be built or
operated: the seal hashed the genesis record while the genesis record hashed the
seal; the writer was required to validate a seal the permission hierarchy denied
it; the capability probe ran under permissions that would make every negative
case fail even with append-only support absent, and its startup form attacked
live evidence; and a `CHECK (append_only_verified)` was credited with proving a
host probe had run. **Revision 6 corrects all four**, and what is on offer for a
ruling is the corrected contract, not the revision-5 one. The four elements
below are otherwise unchanged in **authority, topology and retention**; what
changes is stated inside each.

Four things need a ruling **together**, because approving some without the others
would approve a control that does not hold:

1. **The storage.** `/var/lib/freedom-sheet-writer` on the verified ext4 root
   volume, root-owned throughout, with the writer holding **no write permission on
   the directory containing its own journal** — so it cannot unlink, rename, link,
   create or replace anything there, with `chattr +a` as a second, independent
   layer that is **probed rather than inferred**. Deliberately **not** systemd's
   `StateDirectory=`, which creates the directory owned by the unit's `User=` and
   would hand the writer the very authority the control removes. **Revision 6
   changes two modes and adds one group.** `…/journal` becomes
   `root:freedomjournal 0750` and the seal `root:freedomjournal 0440`, with
   `freedomsheet` the group's only member, so the writer can **read** the seal it
   is required to validate and *other* loses the traverse it had at `0751`. The
   probe moves into a **disposable arena** the tested identity can ordinarily
   write, which is what makes each expected refusal attributable to
   `FS_APPEND_FL` rather than to file permissions, and which is destroyed by a
   privileged cleanup that exits non-zero on residue. **The writer still cannot
   modify, replace, rotate, seal, archive or dispose of anything.**
2. **The generation and its registration.** A `chattr +i` seal on disk, a genesis
   record inside the journal, and a registered row in PostgreSQL that must all
   agree — so the activation trigger can refuse **stale and cross-generation**
   evidence, which revision 4 could not, and so a new or reset journal is never a
   valid empty history. **The writer still opens no database connection**, so the
   Freedom bot's legacy mutation path gains no PostgreSQL dependency. **Revision 6
   makes the construction acyclic** — a seal body is written and hashed before the
   journal exists, the genesis record is *derived* from that body, and the
   finished seal's digest is a leaf that nothing else hashes — and **withdraws the
   claim that PostgreSQL proves the capability probe ran**. The registered row now
   carries an attested, re-derivable probe report, and the refusal of a generation
   whose probe failed happens **on the host**, in `init-generation`, not in a
   database `CHECK`.
3. **The privileged lifecycle.** `freedom-journal-admin`, run as **root** under a
   second `sudoers` drop-in kept separate from the coordinator's, so the two
   authorities are revoked independently. It owns `verify-capability`,
   `init-generation`, `seal`, `rotate`, `repair`, `archive-verify` and `dispose`.
4. **The retention and disposal rule.** N5.0-23, and a `dispose` that refuses
   without plan §15.1's gate and a **Data Owner approval reference**. *This is the
   part that is genuinely the Data Owner's*: it decides when a record of what the
   platform wrote to a live community's Sheet may be destroyed.

**The question.** Which journal contract is adopted?

- **Option J-1 (recommended).** All four above. *Costs:* a sixth table, a fifth
  application command, a second privileged tool and `sudoers` entry, a root-owned
  state hierarchy, **a third system group** and a **disposable probe arena** at
  provisioning, and **the refusal cost of N5.0-21** — a full or failing journal
  filesystem stops Sheet mutations until an operator acts (risk **R-5.0-11**,
  which revision 6 grows from twenty-one to **twenty-five** fail-closed
  conditions). *Benefits:* every unknown state refuses; a reset cannot look empty;
  the writer cannot erase what it authored; the enumeration survives a reboot;
  and, after revision 6, the whole chain is **constructible in a stated order and
  independently re-derivable** by a verifier that holds only the seal and the
  journal.
- **Option J-2.** Durable storage and the seal, **without** the PostgreSQL
  registration and without the sixth table. *Cost:* the stale- and
  cross-generation checks then exist **only** in the coordinator command,
  contradicting the reason this package already gave for duplicating the fence
  test in the database. **Marginally less bad after revision 6**, because more of
  the check — the acyclic derivation, the inode binding, the deployment digest and
  the host identity — is verifiable from the on-disk artifacts alone; still not
  recommended, because nothing then refuses a *stale* generation at activation.
- **Option J-3.** **Drop `dispatch_journal_clear` and the journal entirely.**
  *Benefit:* the contradiction disappears, four fence methods remain, and neither
  the sixth table, the second tool nor R-5.0-11 exists. *Cost:* **nothing refuses
  a cutover when a request is *known* to be outstanding** — the case P5.0-R1 is
  actually about — and two of the six achievable guarantees are withdrawn. **This
  is the honest alternative to revision 4's contradiction and it is listed so the
  choice is Peter's rather than the implementer's**, with the implementer's
  assessment that it is not recommended stated so it can be disagreed with.
- **Option J-4.** Keep revision 4's `/run` journal. **This is the P5.0-R5
  finding.** Listed for completeness, not recommended.

**Why an agent does not decide this.** Two of the four elements change the
accepted production topology — a root-owned durable state hierarchy and a second
`sudoers` rule that runs as root — which `.agents/AGENTS.md` gates. The fourth
decides when evidence may be destroyed, which is a data decision. And option J-3
would trade a control away, which is a risk acceptance rather than a design
preference.

**Owner:** Operations Owner and **Data Owner**, on the Security Reviewer's review.
**Required by:** before Package 5.0 WP-4b and WP-15. The full contract is
`docs/review/phase-5-0-package-plan.md` §2.13; the option pricing is §2.13.11 and
§5.3; the schema consequence is
`docs/review/phase-5-0-logical-schema.md` §3.7, §3.5, §3.4 and §2.9. The
revision-6 corrections are package plan §2.13.2a, §2.13.3, §2.13.5a, §2.13.5b,
§2.13.5c and §2.13.8a, and logical schema §3.7 and §3.7.1.

**Coupled to OD-62.** The R4 and R5 handoffs record that the Google residual decision
**must not be taken until this control is accurately stated and fail closed**. It
is not, however, a *substitute* for OD-62: a durable journal is not a barrier, and
`docs/review/phase-5-0-package-plan.md` §2.13.10 exists so no later reader can
mistake it for one.

## H. Product scope

### OD-53 — The Freedom bot is retired at the end of the migration · **CLOSED 2026-08-28**

**Decision by Peter Duscha, Product Sponsor, Product Owner and Acceptance
Authority, 2026-08-28**, stated directly: *"I'd say we don't need `/info`
anymore when the freedom-blades platform is running… like the whole bot. That is
basically what the platform is all about: To get the google sheet and the bot
out and make the experience for the player better."* and, on the sequencing,
*"Obviously, we discontinue the bot only after everyone went over to the
platform. But in the end, yes, the bot will be deleted because it's not needed
anymore."*

**The ruling.** The Freedom bot is deleted once the platform is **fully
functional**, and not before. The platform must provide every player-facing
behavior the bot provides, so that a player needs no manual step beyond the
Council confirmations the rules require.

**Clarified by Peter Duscha, 2026-08-28**, on reviewing the first record of this
decision: *"I said, the bot are not to be deleted…as long as the platform is not
fully functional."* The first amendment anchored the prohibition to deletion
*"as part of the website or database migration"*, which is a vaguer and weaker
condition than the one given. The prohibition is now bound to the platform's
functionality in `.agents/AGENTS.md` and §15.2, extended to cover **disabling or
degrading** the bot and not only deleting it, and *fully functional* is given an
explicit four-part definition rather than left to judgement.

**What this changed.** `.agents/AGENTS.md` direction item 8 previously retained
Discord for "optional lightweight commands" and the working agreement stated
that the bot "must not be deleted". Baseline **v1.7** amends both: the
prohibition is narrowed to *"must not be deleted as part of the website or
database migration"*, which is what it was actually protecting, and a new
direction item 9 records the retirement. The staged retirement contract and its
terminal gate are implementation-plan **§15.2**.

**What this did not change.** Most of the intent was already approved and needed
no amendment: §15.1 retires Google Sheets, Phase 5.1–5.9 migrates every command's
automation with 5.10 cutting the behaviors over, Phase 6 provides the Council
approval centre, and Phases 8–11 automate missions, attendance, reports,
rewards, Bastions and facilities. The endpoint where a player does everything on
the platform was already the plan.

**Discord and the Freedom bot are two different things.** Confirmed by Peter
Duscha, 2026-08-28: *"Discord and the Freedom Bot (discord bot) are two very
different things. The discord server is the basis for the whole project."*
Discord is the community's server and the foundation of the platform; the
Freedom bot is this repository's Python/Pycord application, a client of Discord.
This decision retires the client and nothing else. `.agents/AGENTS.md` now opens
its product direction with a terminology block stating the distinction, and the
loose uses of "Discord bot" in the working agreement and the implementation plan
were corrected to "Freedom bot" so no future reader can act on the wrong one.

**Discord is not retired with the bot.** Discord OAuth remains the platform's
authentication, and Discord remains the source of guild membership, role
verification, events, notifications and voice-state attendance evidence.
Whatever Discord-side presence those require afterwards is a narrow,
platform-owned adapter owned by the package that needs it. **Recorded
consequence for Phase 8:** voice-state join/leave requires a live gateway
connection, so "no bot" must not be read as "no gateway process" until the
attendance package decides how attendance evidence is collected. That is an
impact to size, not an objection to the decision.

**Affected requirements.** `.agents/AGENTS.md` product direction and the
non-deletion rule; implementation-plan §12.0 dependency map, §15 (retitled
*Legacy runtime retirement*), new §15.2; the Phase 8 attendance package's
sizing; §18/§19 remain accurate as written.

**Phase 4 consequence, as finally amended by OD-52.** Neither `/info` nor a
temporary wallet query/Sheet adapter is Phase 4 work. The finished platform
replaces the user need with character pages, and package 5.2 supplies their
typed wallet query and adapter. Bot retirement still waits for every underlying
player-facing behavior and owning package gate, not for preservation of the
slash-command interface itself.



### OD-40 — Music platform work · **CLOSED 2026-07-31, AMENDED 2026-07-31**

*Recorded as a duplicate "OD-38" until 2026-08-01; renumbered because OD-38 was
already* Initial authority during Sheet migration.

**Maintainer decision:** remove music from the implementation completely. Music
is not a platform feature and it is **not deferred** to a later phase. Its bot
commands, runtime path, dependencies, configuration, credential examples and
deployment templates are removed. No platform acceptance criterion depends on
music, and no later phase reintroduces it.

**State in the repository, verified 2026-08-01** (read-only verification; no live
service was inspected or altered):

| Surface | State |
|---|---|
| `music.py` | deleted |
| Runtime attachment in `main.py` | removed; `EXTENSIONS` holds eleven required extensions and no music entry |
| Music commands | none registered |
| Dependencies | `yt-dlp` removed from `requirements.txt`; no Wavelink dependency is or was declared |
| Configuration | no `ENABLE_MUSIC`, `LAVALINK_*` or `YTDLP_*` in `config.py`, `.env.example` or `repoize.sh` |
| Deployment templates | `infra/systemd/lavalink.service.tmpl` and `infra/lavalink/application.yml.tmpl` deleted |
| Cookie fixture | `yt-cookies.txt.example` deleted |
| Tests | no music-specific test exists |

Two residues are **outside the repository's tracked content** and were
deliberately left alone:

- `infra/lavalink/` remains as an empty directory in the working tree. Git does
  not track empty directories, so it does not exist in the repository; deleting
  it locally is optional tidying.
- `yt-cookies.txt` still exists in the working tree and is excluded by
  `.gitignore`. It is a credential-shaped file: it was not read, printed or
  modified, and whether to delete it from the host is an operator decision.

Repository removal is **not** authorization to stop or reconfigure any live
Lavalink process. That is live-service administration and belongs to a
maintainer.

---

## Summary by urgency

**Resolved 2026-07-29 (rule corrections):** OD-10, OD-11, OD-26, OD-27 and OD-29
are closed. OD-28 is partly closed — the 100-CRP gate is implemented; the
untracked tribute item remains.

**Resolved 2026-07-30 (Foundry answers):** **OD-12** closed — its premise was
wrong; one shared bind-mounted world, not three copies. **OD-14** closed — pin to
the deployed (core, system) tuple and fail closed. The **electrum** group of
OD-13 closed — the game does not use electrum, and `Electrum` in Sheet column E is
a *badge tier*, not currency. The `Characters (active)` folder name is confirmed;
one character (Xirla) is in the sheet but not that folder, so sheet↔Foundry is not
1:1.

**Resolved 2026-07-30 (Sheet answers):** **OD-02** closed — all eleven unmapped
columns identified, with two design consequences (column **C** is the player link;
**AE–AH** duplicate Foundry's character mechanics). **OD-07** closed — *there are no
formulas*, so Phase 2 is a migration rather than a repair; but three timed macros
write to the sheet, which is a previously unknown third writer. **OD-34** ruled —
untagged CRP is resolved by hand once at import. **OD-03** and **OD-04** mostly
answered. **Opened: OD-36** (macro fate at cutover). **Escalated: OD-06** — tool-name
abbreviations have a live false-refusal path.

**Found while verifying those answers:** column W's real format was not the one the
parser understood, and `/craft` was overwriting per-tool CRP with a single tool on
every craft. Fixed, with seven regression tests — see
[phase-0-handoff.md §4.6](phase-0-handoff.md#46-column-w-was-silently-destroying-crp-data-on-every-craft--fixed).

**Resolved during Phase 1:** OD-15, OD-21, OD-22.
*(OD-08 and OD-35 are ruled; ADRs 0003 and 0005 were amended and accepted.)*

**Blocking live behaviour today:** none outstanding. OD-34 is ruled, the column W
data loss is fixed, and the downtime double-grant risk was disproved (the macro is
off).

**Blocking Phase 2:** none. No decision blocks the import work, and — per the
maintainer ruling of 2026-08-01 recorded at OD-17 and OD-39 — neither of those
entries gates the Phase 2 review either. Phase 2 approval depends on the Phase 2
acceptance criteria in plan §12 and on the correction of actual
import/reconciliation findings. **OD-17 and OD-39 remain open, real and
unfixed**; they are listed under Phase 3 and Phase 5 below because that is where
they must be answered, not because they have shrunk.
*(OD-36 closed 2026-07-31.)*
*(OD-01, OD-02, OD-06, OD-07, OD-12 and OD-30 closed.)*

**Blocking Phase 3:** OD-16 and OD-17. OD-17 must also be answered before any
affected legacy bot mutation is migrated or cut over.
*(OD-18, OD-19, OD-20, OD-23, OD-24 and OD-31 closed 2026-07-31.)*

**Raised by the Codex project review of Phase 2, 2026-07-31:** **OD-17
escalated** from "decide the schedule" to "decide the interim containment", with
five options priced; and **OD-39** opened on the provenance of `/trade` and
`/sale` inputs. Neither can be settled by an agent: one asserts an identity link
the platform does not yet have, the other is game policy. Both were scoped to
their correct future gates on 2026-08-01 — Phase 3 planning and the affected
command migrations for OD-17, Phase 5.7/5.8 for OD-39 — after the Phase 2
classification was found to create a sequencing deadlock.

**Blocking Phase 5 (per command):** OD-03, OD-04, OD-05, OD-09, **OD-39 before
5.7 `/sale` and 5.8 `/trade`**, plus the tribute item remainder of OD-28 and the
gate-boundary half of OD-34.

**Blocking Phase 6–8:** none from the plan §17 decision log.
*(OD-32 and OD-33 closed 2026-07-31.)*

**Blocking write-enablement:** none from field ownership.
*(OD-13 closed 2026-07-31; the approved workflow still requires proposals and
Council approval.)*
*(OD-14 closed.)*

**Blocking the Phase 2 gate:** no open OD entry. OD-41 closed 2026-08-02 by
rejecting the generic store and adopting package-owned typed migrations; OD-42
closed 2026-08-02 by ruling that display names are not unique identities and
that ambiguous name-based candidate lookup fails closed.

**Blocking Phase 3 P3.G0:** OD-43's product requirement is ruled; its proposed
credential, account, migration and recovery design must be accepted or amended
through the P3.0 ADR before P3.1 starts.

**Check independently:** OD-25.

**Added by the Codex review of 2026-07-29:** OD-34 (legacy untagged CRP policy)
and OD-35 (import idempotency and ID generation). This is historical context:
both were subsequently ruled by the maintainer, as recorded below.

**Resolved 2026-07-30 (third round):** **OD-35** ruled — the ID is assigned at row
creation, never derived; ADR 0003 amended and unblocked. **OD-30** closed — two real
Foundry actors verified the field mapping, producing five corrections (F-F1–F-F5),
including the discovery that **Foundry models Bastions natively** and that the tool
vocabularies already agree.

**Resolved 2026-07-30 (second round):** **OD-01** — scope is `Characters` plus a
player-level tab; everything else is out of scope. **OD-06** — the sheet uses two
vocabularies (Y = tool, W/X = artisan) and `_clean_tool_name()` is the documented
bridge between them. **OD-08** — the initial one-decimal answer showed that
eighth-days were unsuitable; the later, more specific ruling below settled on
three decimals. **OD-03/OD-36** — the
downtime macro is off, so there is no double grant. The column W format question is
closed as cosmetic.

**Resolved 2026-07-30 (fourth round):** **all seven ADRs accepted**, satisfying the
Phase 0 acceptance criterion for ADR approval (the gate itself also needs the Codex
review, subsequently approved). **OD-01** closed — player tab columns supplied, and they contain the Discord link
(F-S5). **OD-08** closed — table constants exact, computed values rounded to three
decimals, which coincides exactly with the thousandth-day unit. **Bastion ownership**
settled as complementary rather than contested, with partial Foundry coverage binding on
the design.

**No open decision blocks Phase 1 from starting.** The Phase 0 review gate is
closed: the independent Codex re-review approved the architecture and data
handling, and the maintainer accepted the milestone on 2026-07-30.

What remains, in the order it will be needed:

| When | Decisions |
|---|---|
| Early Phase 1 | **Closed 2026-07-30:** OD-15 (Council-approved shared level), OD-21 (host-managed PostgreSQL 16), OD-22 (same-host staging with strict separation) |
| Phase 2 | No open OD entry; approval rests on controlled baseline v1.1 §12 acceptance criteria and remediation/re-review of the import implementation. Still carry forward F-S6 aggregate disagreements and F-S7's unruled deadline rather than treating either as authoritative policy |
| Phase 3 | OD-16 and OD-17; the §17 authorization parameters closed 2026-07-31. OD-17 is also required before any affected legacy bot mutation is migrated or cut over |
| Write-enablement | Ownership settled by OD-13; implementation still requires the approved proposal and Council-approval controls |
| Package 5.0 | **OD-62** (**reframed a third time 2026-08-29** — no barrier exists, so what is accepted in place of one; a **risk acceptance**, before WP-4b, and **not to be decided until the Independent Reviewer accepts that the enumeration control is fail-closed**), **OD-63** (**extended to nine** numeric controls 2026-08-29, before WP-1 completes), **OD-64** (**extended** to the authority-plane principal **and** its dedicated OS identity and host boundary, before WP-2 and WP-14), **OD-65** (the `freedomsheet` identity and credential relocation, live-unit hardening, the group-writable repository tree, and — **extended 2026-08-30** — a third system group `freedomjournal`; before WP-4b and WP-14) and **OD-66** (**new 2026-08-29, option A re-stated 2026-08-30** — the dispatch journal's durable storage, its **acyclic** sealed and registered generation, privileged lifecycle and evidence-disposal authority; before WP-4b and WP-15). OD-61 is **closed 2026-08-31**: Codex is named Security Reviewer, and OD-64, OD-65 and OD-66 remain unrulable until that review returns a recommendation |
| Phase 5–8 | OD-03, OD-04, OD-05, OD-09, **OD-39 before 5.7 `/sale` and 5.8 `/trade`**, and OD-28 tribute item; OD-32 and OD-33 closed 2026-07-31 |
