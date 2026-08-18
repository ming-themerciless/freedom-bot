# Phase 3 identity migration contract

Status: **Accepted 2026-08-13 at P3.G0.** No migration was executed by P3.0;
implementation and database evidence belong to P3.1/P3.2.

Remediated in this revision: stage A performs the `audit_events` **constraint
swap** and treats the three append-only tables on their own evidence rather than
symmetrically; its downgrade restores the legacy constraint `NOT VALID` and names
what a downgrade costs; control totals T7 and T8 are added; and §8 gains the
break-glass attribution property the design has to deliver.

**Amended 2026-08-17 by change-log entry C-P3.2-A (Peter Duscha, Acceptance
Authority).** §7.2 previously described a three-step M-2 pipeline whose third
step, `C-05 --apply`, materialized confirmed proposals into `character_access`.
That contradicted §7.5 of this document, §5.1 of the route-authorization contract
and TC-MIG-09/TC-MIG-11/TC-MIG-13 of the test traceability, all of which place the
write at the Council confirmation. The maintainer resolved the contradiction in
favour of **immediate activation**: a Guild Council confirmation at R-29 creates
the `character_access` row atomically with its audit events, and there is no
later materialization step. C-05 is withdrawn from this contract and from the
command register. §7.2, §7.3, §7.4 and §7.5 below are the corrected text.

**No migration is written in P3.0.** This is the design the P3.1 and P3.2
revisions will be reviewed against. Package: P3.0 · Owner: Claude · Implemented
by P3.1 (stages A–C, §3) and P3.2 (the Sheet-era evidence migration, §7).

Tables are defined in
[`phase-3-logical-schema.md`](phase-3-logical-schema.md). Numbers are `N-nn` from
[`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md).

## 1. Two migrations, deliberately separated

They are often spoken of as one and must not be built as one.

| | **M-1: Discord reference migration** | **M-2: Sheet-era identity evidence** |
|---|---|---|
| Question it answers | "Which platform account does this existing Discord-keyed row belong to?" | "Which Discord human does this Sheet row's *Player Name* refer to?" |
| Source | PostgreSQL rows written by Phases 1–2 | `Characters C`, `Players A/B/D` in Google Sheets |
| Determinism | **Total.** Every Discord id maps to exactly one account, computed | **Partial.** Names are evidence; several rows resolve to nothing |
| Human decision | None | **One Council confirmation per proposed link** |
| Package | P3.1 | P3.2 |
| Reversible | Yes, until stage D | Yes: reject a proposal, revoke a link |

Building them together would let a name-derived guess flow into an
authorization-bearing column under cover of a deterministic backfill. That is the
exact failure delivery plan §9.4 forbids.

## 2. Current state, counted

The migration's arithmetic starts from what actually exists. As of this package,
the tables holding Discord references are:

| Table | Column | Role |
|---|---|---|
| `discord_users` | `id` | The population being migrated |
| `discord_guild_memberships` | `discord_user_id` | Discord fact — **stays** |
| `discord_membership_roles` | `discord_user_id` | Discord fact — **stays** |
| `character_access` | `discord_user_id`, `granted_by_discord_user_id` | Authorization-bearing — **migrates** |
| `audit_events` | `actor_discord_user_id` | Append-only attribution — **not rewritten** (schema §6) |
| `snapshot_imports` | `actor_discord_user_id` | Append-only — **not rewritten** |
| `foundry_snapshots` | `received_by_discord_user_id` | Append-only — **not rewritten** |

**The production database currently holds no `character_access` rows and no
`discord_users` rows** — Phase 2 applied nothing to production, and rehearsal B
verified `characters` 0, `external_actor_mappings` 0, `snapshot_imports` 0 in the
test database before teardown. P3.0 has not inspected production data and must
not: the migration is therefore designed to be correct for a **non-empty**
database and to be trivially correct for an empty one. Its control totals are
computed at run time, never assumed.

## 3. M-1: staged Discord reference migration

Four stages, each its own Alembic revision, each reversible on its own.

### Stage A — additive, no behaviour change

Creates: `platform_accounts`, `external_identities`, `oauth_token_grants`,
`sessions`, `oauth_transactions`, `webauthn_credentials`, `recovery_grants`,
`auth_rate_limits`. Adds nullable `platform_account_id` /
`granted_by_account_id` to `character_access`; adds the nullable attribution
columns to the three append-only tables and performs the **constraint swap** on
`audit_events` (schema §6.3, §6.4).

The three append-only tables are not treated alike, because they are not alike
(schema §6.2.1):

| Table | Stage A does | Because |
|---|---|---|
| `audit_events` | add `actor_platform_account_id` + FK; **add** `ck_audit_events_human_action_has_an_attribution` `NOT VALID`; **drop** `ck_audit_events_human_action_has_an_actor` — in that order, in one transaction | The legacy check forbids a Discord-independent human event, which is precisely what break-glass writes. Without the swap, the emergency login itself fails, because SM-03 commits the session and its audit event together |
| `snapshot_imports` | add `actor_account_id` + FK; **add** `ck_snapshot_imports_import_has_an_attribution` `NOT VALID` | No attribution rule exists on this table today. The new check is a strengthening for new rows, never validated against history |
| `foundry_snapshots` | add `received_by_account_id` + FK only | No attribution rule exists and none is added: a supervised-bootstrap row that names no human is legitimate (migration 0004) |

The same revision changes `application/audit.py`'s `UNATTENDED_CAPABILITIES`
guard to accept an account id, because it enforces a copy of the constraint in
Python and would otherwise refuse the write before SQL ever saw it (schema
§6.1.1). Migration and guard move together or not at all; TC-AUD-11 asserts both
halves.

**No row is read, updated or deleted at any point.** `ADD COLUMN` without a
default, `ADD CONSTRAINT … NOT VALID` and `DROP CONSTRAINT` are catalogue
operations; row triggers do not fire for DDL, so the `audit_events_append_only`
trigger from migration 0002 is neither dropped, disabled nor evaded. The
replacement check is implied by the constraint it replaces (`A ⟹ X ∨ A`), so its
truth over history is a proof rather than a scan.

Backfill, in the same revision, deterministic and idempotent:

```text
for each row in discord_users:
    account := platform_accounts row, id = uuid4(), status = 'active'
    external_identities row: (provider_key='discord', subject=<id as text>,
                              platform_account_id=account.id, state='active',
                              linked_at = discord_users.created_at)
update character_access set platform_account_id = account of discord_user_id,
                            granted_by_account_id = account of granted_by_...
```

Idempotency: the backfill selects `discord_users` that have no
`external_identities` row for `('discord', id)`. Re-running inserts nothing.
Re-running after a partial failure completes the remainder. This is the same
"idempotency from mapping constraints" rule ADR 0003 already sets.

**Downgrade:** restore `ck_audit_events_human_action_has_an_actor` **`NOT
VALID`**, drop the two new checks, then drop the new columns and tables. The
`character_access` rows still carry their original `discord_user_id`, untouched.

The legacy check comes back `NOT VALID` deliberately: by downgrade time the table
may hold account-attributed rows, and a validating `ADD CONSTRAINT` would scan,
find them and fail, leaving the downgrade half-applied. `NOT VALID` restores the
rule without asserting a history that is no longer true (schema §6.3).

One thing **is** lost on downgrade, and the revision docstring must say so where
an operator will read it: dropping `actor_platform_account_id` discards the
attribution of any audit event written by a break-glass session after the
upgrade. The event itself survives with its capability, action, payload and
correlation id; its actor becomes unresolvable. That is a data consequence of the
downgrade, not a defect in it, and it is the reason §5 requires a pre-stage dump.

**Control totals, checked inside the migration's own transaction and refused if
they disagree:**

| Total | Rule |
|---|---|
| T1 | `count(platform_accounts)` = `count(discord_users)` + pre-existing accounts |
| T2 | `count(external_identities WHERE provider_key='discord')` = `count(discord_users)` |
| T3 | `count(DISTINCT subject)` = `count(external_identities WHERE provider_key='discord')` |
| T4 | `count(character_access WHERE platform_account_id IS NULL)` = 0 |
| T5 | `count(character_access WHERE granted_by_account_id IS NULL)` = 0 |
| T6 | For every `character_access` row: the account resolved from `platform_account_id` has an active Discord identity whose subject equals the row's `discord_user_id` |
| T7 | `count(audit_events)` before the revision = `count(audit_events)` after it, and `max(occurred_at)` is unchanged. The swap must not have touched history, and this is the cheapest statement of that |
| T8 | The check-constraint inventory of `audit_events`, `snapshot_imports` and `foundry_snapshots` after the revision equals the inventory in schema §6.2.1 exactly — no missing constraint, no surviving legacy one, nothing extra |

T6 is the one that matters for the mapping. It is a full-table equality between
the old key and the new key, and it is the evidence that the migration mapped
rather than guessed. T7 and T8 are the ones that matter for the constraint swap:
the first says history is the same size it was, the second says the rule set is
exactly the one that was reviewed.

### Stage B — constraints

Sets both new `character_access` columns `NOT NULL`; adds the account-keyed FKs;
creates the account-keyed partial unique indexes **alongside** the existing
Discord-keyed ones (schema §7).

Both invariant sets are enforced simultaneously. If the mapping were wrong, an
insert would violate one of the two, loudly, before any user saw a wrong
authorization. **Downgrade:** drop the new indexes and constraints; the old ones
never stopped working.

### Stage C — application cutover

No schema change. The application begins reading and writing
`platform_account_id` exclusively. `discord_user_id` becomes a read-only shadow
maintained by a database trigger, so the legacy invariants keep protecting rows
written by the new code path.

**Guard for the point of no return** (§4): the trigger refuses an insert whose
account has no active Discord identity. Until stage D, every
authorization-bearing row must be expressible both ways. Break-glass accounts
never receive `character_access` (N-12), so this refuses nothing legitimate.

**Downgrade:** revert the application. The shadow column is current, because the
trigger kept it current.

### Stage D — drop the legacy columns

A **separate, later decision**, not part of P3.2's delivery, and not taken until
the verification period in §6 has passed. Drops `character_access.discord_user_id`,
`granted_by_discord_user_id`, the trigger and the legacy indexes.

**Downgrade past stage D is recovery, not rollback.** See §5.

## 4. The point after which rollback becomes recovery

Stated precisely, because "reversible" is otherwise a claim rather than a fact.

| Position | Reversal | Cost |
|---|---|---|
| Before stage A completes | `alembic downgrade` | None |
| After A, before B | `alembic downgrade` | None; new tables discarded |
| After B, before C | `alembic downgrade` | None |
| After C, before D | Revert the application and downgrade | Sessions created after cutover are lost — users log in again. `character_access` rows written after cutover survive, because the trigger maintained the shadow column |
| **After D** | **Not a rollback.** The Discord key no longer exists in the table and cannot be recomputed from it — only from `external_identities`, which the downgrade would also drop | **Restore from backup, then replay.** See §5 |

Stage D is therefore the point of no return, and it is deliberately placed after
a verification period rather than inside the migration package that creates the
need for it.

## 5. Backup, restore and rehearsal

Preconditions, all of which must be evidenced before **each** stage runs against
a non-disposable database:

1. A `pg_dump` taken immediately before the stage, restore-tested per plan §14.3
   — *restore-tested, not merely reported successful* (topology §6).
2. The full sequence rehearsed end to end on the disposable `freedom_test`
   database with synthetic data: upgrade → control totals → downgrade →
   upgrade again, proving idempotency and reversibility in one run
   (`infra/postgresql/backup-restore-drill.sh` is the existing harness).
3. The bot is unaffected: stages A–C add columns and tables the bot does not
   read. Stage D touches a table the bot does not read either (`character_access`
   is not consulted by any current command — that is OD-17's open gap, and this
   migration neither widens nor closes it).

Recovery from a failed stage: the stage runs in one transaction and either commits
or leaves nothing. A failure between stages leaves a consistent database at the
previous stage. The documented recovery is *restore the pre-stage dump* only if a
downgrade itself fails, which for stages A–C means only DDL failure.

## 6. Verification period before stage D

Stage D is authorized only when all of the following hold and are recorded:

- 30 days of production operation after stage C with no identity-related incident;
- zero rows where the shadow column and the resolved account disagree, checked by
  a scheduled read-only query;
- every acceptance test in the P3.G1/P3.G2 sets green on the current build;
- one restore-tested backup that predates stage D;
- Data Owner and Operations Owner sign-off, per plan §0.3.

That list is the definition of *"the point after which rollback becomes
recovery"* being crossed deliberately.

## 7. M-2: Sheet-era identity evidence

### 7.1 What the evidence is, and what it is worth

`Characters C` (*Player Name*) joins to the player tab's column A; column B holds
that player's **Discord name** (sheet inventory F-S5). The chain
`character → player → Discord` therefore exists in the spreadsheet already. Two
facts limit it to evidence, both already recorded:

- it is a **username, not a snowflake**, and usernames change (F-S5);
- it is **one Discord name per player**, while the product invariant allows several
  authorized users per character.

`Players D` (*Active DM*) is reconciliation evidence only and never grants
capability (OD-18, migration register). Display names are not identities (OD-42).

### 7.2 The pipeline

Two steps, and the second is the one that authorizes.

```text
C-04 --dry-run                          Council (R-28/R-29/R-30)
──────────────────                      ────────────────────────
read-only Sheet boundary          ──▶   review one proposal at a time
writes identity_link_proposals          confirm: creates the character_access row
writes NO character_access               and both audit events in one transaction,
nothing is resolved by row order         through the same service R-25 uses
                                        reject: decision + audit, and no link
                                        nothing auto-confirms, nothing in bulk
```

Nothing in this pipeline can create an authorization row without a named Council
member having confirmed that specific proposal, under a **live** server-side
resolution of that member's Council capability taken on the confirming request.
C-04 resolves; the confirmation does not resolve again — it links to the subject
C-04 recorded and R-28 displayed, and refuses if that subject is absent.

**There is no deferred apply step.** A confirmation is the activation: the
proposal's `confirmed` transition, the `character_access` row, the character's
optimistic version bump, the `character_access.granted` audit event and the
`identity_migration.confirmed` audit event commit together or not at all. A
confirmed proposal therefore never denotes an instruction someone still has to
carry out, and R-28 never has to distinguish "decided" from "materialized",
because they are the same moment.

Google Sheets is **legacy migration input** to C-04 and nothing else: not an
operational data store, not a portal dependency, and not a participant in the
Council decision. C-04 is a temporary operator utility, run from a separate
environment that carries the read-only Google client libraries and credentials
(§7.7); the portal runtime and the normal PostgreSQL-backed operation of the
platform require neither.

### 7.3 Resolution rules

| Situation | `resolution` | Confirmable |
|---|---|---|
| Exactly one guild member's username matches the sheet's Discord name, case-folded and NFC-normalized | `proposed` | yes — a Council member still confirms |
| More than one member matches | `ambiguous` | **no**. Every candidate is listed; none is chosen |
| No member matches | `unresolved` | no |
| The sheet cell is blank | `unresolved` | no |
| The character already has an active access row for that account | `already_linked` | n/a — counted, not proposed |

The refusal to choose among candidates is the same rule
`application/foundry/reconciliation.py` already applies to Actor mapping
(*"an ambiguous candidate lookup fails closed"*), applied to people instead of
Actors. Comparison uses the existing shared policy in `domain/names.py` rather
than a second implementation — a second copy of a name-comparison rule is a
second place for it to be wrong.

#### 7.3.1 The join key must be unique, and the run refuses when it is not

*Added 2026-08-17 by C-P3.2-A, in response to an independent-review defect.*

The table above resolves a character through its *Player Name*. That join is only
meaningful if the player tab names each player once. Two rows whose player names
are equal under the same NFC-normalized, case-folded comparison the resolver uses
— `Ada` and `ADA` — are **two claims to one key**, and if they carry different
Discord names the platform cannot tell which person a character's *Player Name*
refers to. Choosing between them by Sheet order is not a tie-break, it is a name
deciding an identity by an accident of layout, which is exactly what OD-42 and
N-16 forbid.

So the run **refuses**, before anything is written:

| Situation | Outcome |
|---|---|
| Two or more player-tab rows share one normalized *Player Name* key | The whole C-04 run is refused. No run row, no proposal, no candidate and no `character_access` row is written, and no control total is reported — there is nothing partial to hide a duplicate in |

The refusal names the number of colliding keys and the number of rows involved,
and no name, cell or Discord identity: an operator's terminal is not the place for
the personal data the player tab holds. The remedy is operational and belongs to
the person who owns the spreadsheet — resolve the duplicate in the legacy Sheet,
then re-run C-04. Nothing in this workflow writes to Google, so the platform does
not resolve it for them.

The alternative considered and rejected was to persist each affected character as
non-confirmable evidence. It fails closed too, but it lets a source-integrity
defect appear in the control totals as an ordinary ambiguity, and §7.4's balance
would then be reported over a player set the run had silently decided was
self-consistent. A refusal states the problem where it is.

The uniqueness rule lives with the resolver rather than in the Sheets adapter,
because it is the same normalization the resolution rules use, and §7.3 forbids a
second implementation of *"are these the same name?"*. The adapter supplies rows
and positions; it does not decide identity.

**Nothing in this pipeline consults `Active DM`, and nothing derives capability
from any Sheet value.** Capability comes from Discord role snowflakes resolved
server-side (OD-18).

### 7.4 Control totals

C-04 emits, and R-28 displays (VM-10), a reconciliation that must balance:

```text
source_characters        = rows in Characters with a non-blank column C
source_players           = rows in the player tab
already_linked           + proposed + ambiguous + unresolved  =  source_characters
confirmed + confirmed_revoked + rejected + outstanding        =  proposed + ambiguous + unresolved
```

Every source row lands in exactly one bucket. An unbalanced report is a refusal to
proceed, not a warning — the plan's success measure is *"no identity discrepancy
is silently accepted"* (§0.5).

`confirmed` counts proposals that are **active links**, because under §7.2 a
confirmation is the activation. There is no fourth decision state between
`confirmed` and an existing `character_access` row, and R-28 shows none.

`confirmed_revoked` counts confirmations whose `character_access` row Council has
since revoked through R-26 (*added 2026-08-17 by C-P3.2-C, in response to an
independent-review defect*). §7.5 has always made that revocation supported and
§7.4 has always defined `confirmed` as active links; what was missing was the
bucket the revoked one moves into. Without it the second balance loses a proposal
every time Council corrects a link, and the only balanced reading left is the
false one the defect produced — counting a revoked grant as an active confirmed
link and telling a Council member on R-28 that it *"is active now"*.

The revoked confirmation is **counted, not re-decided**. Its `resolution` stays
`confirmed`, it is never rewritten to `rejected`, never returned to `outstanding`,
and it keeps its decider, its reason, its `granted_access_id` and both audit
events: the compensating-action model of §7.5, applied to the report as well as to
the row. Activation is determined from that exact `granted_access_id` joined to
`character_access.active`, and never inferred from another active link on the same
character or account.

### 7.5 Idempotency, atomicity, reversibility

- **Idempotent.** A second dry run over unchanged sources produces the same
  proposal set, keyed `(run_id, character_id)`; a character that an earlier run's
  confirmation has already linked is counted `already_linked` by the next run and
  proposed again to nobody. Confirming a proposal twice is refused, not applied
  twice: the decision transition is a conditional update, so a double submission
  and two concurrent Council confirmations produce **one** durable authorization
  and **one** of each audit effect, and the loser is told the state moved. A newer
  C-04 run also supersedes every older run for decisions: older evidence remains
  durable and readable, but R-29/R-30 refuse it. The decision update independently
  requires the proposal to belong to the latest run, so a newer run committed
  during a confirmation rolls the entire grant back.
- **Atomic.** One confirmation writes one `character_access` row and its audit
  events in one transaction (plan §6.5, *atomic apply*). An audit failure, a
  proposal-transition failure, a grant failure or a commit failure rolls the whole
  confirmation back: no link, no decision, no version bump, no audit.
- **Reversible.** A wrong link is revoked through R-26, leaving the historical row
  and its reason — the compensating-action model, not deletion. The proposal that
  created it stays `confirmed` and R-28 reports the revocation rather than
  concealing or undoing it: the confirmed row renders `confirmed-and-revoked` and
  moves from `confirmed` to `confirmed_revoked` in §7.4's totals (C-P3.2-C).
- **No Sheet mutation, ever.** C-04 uses the existing read-only Sheet boundary
  (`adapters/sheets/read_only.py`, and the separate read-only service account
  documented in `.env.example`). Rollback to the legacy linkage workflow requires
  nothing to be undone in Google Sheets, because nothing was done to it.

### 7.6 Unresolved records

Unresolved and ambiguous proposals **persist as explicit records**. They are not
deleted at the end of a run, not retried automatically, and not resolved by a
later run choosing differently. They appear in VM-10 with their evidence and their
totals until a Council member acts on them. That is delivery plan §9.4's *"ambiguous
or unverified links remain unresolved and grant no access"* made durable rather
than transient.

## 7.7 Google is temporary, and lives outside the platform runtime

*Added 2026-08-17 by C-P3.2-A.*

C-04 is a **migration/import utility with an end date**, not a component. The
constraints on it are:

1. **Read-only, and only the identity-evidence columns.** `Characters C` and
   `Players A/B/D`, through `adapters/sheets/read_only.py`. No game-state column
   is read (§9), and there is no write path in the reader, the adapter or the
   command.
2. **No Google dependency in the platform runtime.** `google-api-python-client`
   and `google-auth` are **not** in `requirements-web.txt` or its lock file, and
   the portal, the Discord bot and every PostgreSQL-backed runtime path start and
   run without them. `read_only.py` imports them lazily and refuses with a typed
   operator-facing message when they are absent.
3. **A separate, temporary operator environment.** The operator runs C-04 from an
   environment provisioned for the migration window with those two libraries and
   the read-only service-account credential. It is not the portal virtualenv, it
   is not deployed, and it is torn down at retirement.
4. **Verify in PostgreSQL, then retire.** After a run, the imported evidence is
   verified in the database (control totals, per-character resolutions, candidate
   sets). The legacy Google access is retained only for the approved
   verification/rollback window recorded with the gate, and is then retired:
   credential revoked, service account removed, operator environment destroyed.
   `.agents/AGENTS.md` already requires the Sheets credentials to be removed after
   Sheets is retired; this is the P3.2 half of that.
5. **The tab name is supplied, never assumed.** Peter Duscha confirmed on
   2026-08-17 that the one-time migration source tab is **`Players`**
   (`C-P3.2-B`), and the Sheet inventory §2.1 records it. C-04 still takes
   `--player-tab` as a **required** argument, and `C-P3.2-B` rejected restoring a
   code default: a default would turn one-time migration input into enduring
   runtime configuration and remove the explicit wrong-tab guard, and a run that
   silently reads whichever tab the default names is how one player's Discord name
   is attributed to another character. The recorded name is operational input to
   the invocation `--player-tab Players`, not portal configuration.

## 8. Historical audit readability after migration

Three properties must hold together, and §6.3 of the schema contract is what makes
them hold:

1. an audit event written before the migration still names its actor;
2. an audit event written after it names an account;
3. both render identically in VM-18, through the `COALESCE` resolution.

Retiring a Discord identity later does not break (1), because retirement keeps the
row. Deleting a `discord_users` row would break it — which is why every FK to that
table is already `ON DELETE RESTRICT` and why this package adds no path to delete
one.

A fourth property was added by remediation and belongs with them:

4. **an audit event written by a break-glass session names an account and no
   Discord user, and is legal.** That is what the constraint swap buys, and it is
   the difference between an emergency-administration design that works during a
   Discord outage and one that only reads as though it does. TC-BG-15 exercises
   the whole path with the provider faulted: session insert and audit insert
   commit in the same transaction, with `actor_discord_user_id` null.

## 9. What this contract explicitly does not do

- It does not migrate any character **game-state** field. Every Sheet-era
  game-state row belongs to a Phase 5 package (migration register), and the only
  Sheet-era migration in Phase 3 is the identity linkage evidence (delivery plan
  §4).
- It does not back-port `character_access` checks to the Discord bot. That is
  OD-17, owned by Phase 5, and this package neither closes nor widens it.
- It does not retire Google Sheets, touch the Sheets adapter, or alter any
  credential.
- It does not write a migration file. P3.1 and P3.2 do, after P3.G0.

## 10. Traceability

| Requirement | Source | Test |
|---|---|---|
| Every existing Discord user, access link and audit reference accounted for | delivery plan §9.3 | TC-MIG-01, TC-MIG-02 |
| Dry-runnable, idempotent, transactional, reversible before cutover | delivery plan §9.3; plan §14.3 | TC-MIG-03, TC-MIG-04, TC-MIG-06 |
| Exact source/target control totals | delivery plan §9.3; plan §0.5 | TC-MIG-02, TC-MIG-08 |
| No name/email establishes equivalence | delivery plan §9.4; N-16; OD-42 | TC-ID-05, TC-MIG-09 |
| Ambiguous stays unresolved and grants nothing | delivery plan §9.4 | TC-MIG-10 |
| A duplicate player-name key refuses the whole run | §7.3.1; plan §0.5 | TC-MIG-17 |
| Council confirms every proposed link, and the confirmation is the activation | delivery plan §5 P3.2; §7.2 | TC-MIG-11 |
| Google stays out of the platform runtime | §7.7; C-P3.2-A | TC-MIG-18 |
| Historical attribution survives retirement | delivery plan §9.5 | TC-AUD-05 |
| Backup/restore rehearsal | plan §14.3; topology §6 | TC-MIG-07 |
| Rollback boundary is explicit | P3.0 prompt §3 | §4 of this document; TC-MIG-12 |
