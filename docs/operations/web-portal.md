# Operating the Freedom Blades web portal (Phase 3 P3.1–P3.3)

Status: P3.1–P3.3 implementation document, extended by P3.3 with the
reconciliation worker (§7). **Nothing here has been deployed.** The portal has no
Caddy site block and no staging environment yet; those belong to P3.5 and the
separate deployment gate. `infra/systemd/freedom-worker.service.tmpl` is a
template, not an installed unit. What this document
records is how to configure, migrate, start and recover the portal on a host
where an operator already has authority — which is exactly the audience the
emergency commands are written for.

Read alongside:

- [`database-development.md`](database-development.md) — the disposable-database
  guards every command here inherits;
- [`topology.md`](topology.md) — where the process sits;
- [`../contracts/phase-3-configuration-and-dependency-contract.md`](../contracts/phase-3-configuration-and-dependency-contract.md)
  — the variables and the fifteen startup refusals;
- [`../adr/0010-provider-neutral-identity-and-emergency-administration.md`](../adr/0010-provider-neutral-identity-and-emergency-administration.md)
  — why emergency access is shaped the way it is.

## 1. The portal has its own virtualenv

```bash
python3 -m venv /opt/discord-bots/venv-web
/opt/discord-bots/venv-web/bin/pip install -r requirements-web.txt
```

`./venv-web` is a symlink to it. The Discord bot's virtualenv is **not** touched:
a shared one would couple the bot's dependency set to the portal's, and the bot
is a live service.

`requirements-web.lock` is the resolved set, committed at each Phase 3 package
gate so a deployment is reproducible and a review can see exactly what changed.

Development dependencies (`pytest`, `pytest-asyncio`, `beautifulsoup4`) are in
`requirements-web-dev.txt` and are not installed on a production host.

## 2. Configuration

Copy the `# ==== Freedom Blades web portal (Phase 3 P3.1) ====` block from
`.env.example` into the portal's **own** environment file. The bot reads no
`WEB_*` or `WORKER_*` variable, and the portal reads none of the bot's.

Four secrets must be generated, and all four must differ:

```bash
openssl rand -base64 32   # WEB_SECRET_KEY_CSRF
openssl rand -base64 32   # WEB_SECRET_KEY_CURSOR
openssl rand -base64 32   # WEB_SECRET_KEY_CLIENT_DIGEST
openssl rand -base64 32   # the material for WEB_TOKEN_ENCRYPTION_KEYS, as `1:<key>`
```

Key separation is what stops a CSRF token being a valid pagination cursor, and
either being usable as encryption key material. Startup refuses a missing key, a
key under 32 bytes, and any two keys that are equal.

### 2.1 Startup refuses rather than warns

The process raises a typed `ConfigurationError` listing **every** problem it
found, names the variables, and never prints a value. An operator fixing four
variables learns about all four in one attempt.

S-01 to S-11 are decided from the environment alone. S-12, S-14 and S-15 need a
resource — the filesystem, the database, the credential store — and run once at
startup after configuration is built:

| Refusal | What it catches |
|---|---|
| S-12 | `WORKER_ARTIFACT_ROOT` fails the existing Phase 2 store checks |
| S-14 | The database's Alembic revision is not this build's head |
| S-15 | Production, and the protected administrator has fewer than two enabled WebAuthn credentials |

**S-15 is a warning outside production**, because the credentials are hardware
and a development host has none. It is reported rather than swallowed: the
warning is on the composition, and `/healthz` reports the same condition.

### 2.2 Encryption key rotation

Add a key, switch the active version, re-encrypt in the background, remove the
old key:

```text
WEB_TOKEN_ENCRYPTION_KEYS=2:<new>,1:<old>
WEB_TOKEN_ENCRYPTION_ACTIVE_VERSION=2
```

The active key encrypts new rows; **every** configured key decrypts. There is no
moment at which a stored token cannot be read. Removing a key whose ciphertexts
still exist makes them unreadable, which is why the old key stays until the
re-encryption is done.

## 3. Migrations

P3.1 adds four revisions. The first three are the stages of the identity
migration in
[`../contracts/phase-3-identity-migration-contract.md`](../contracts/phase-3-identity-migration-contract.md);
the fourth is OD-44's completion binding, added on 2026-08-14 after Peter's
ruling:

| Revision | Stage | What it does | Reversal |
|---|---|---|---|
| `0006` | A | Creates the identity, credential, session and rate-limit tables; adds nullable account columns; performs the `audit_events` constraint swap; backfills one account and one Discord identity per `discord_users` row; checks control totals T1–T8 | `alembic downgrade 0005` |
| `0007` | B | Makes the account columns `NOT NULL` and creates the account-keyed unique indexes **alongside** the Discord-keyed ones | `alembic downgrade 0006` |
| `0008` | C | Makes `character_access.discord_user_id` a trigger-maintained read-only shadow | `alembic downgrade 0007` |
| `0009` | — | Adds `oauth_transactions.completion_claimed_at` and `sessions.oauth_transaction_id` with its foreign key, unique index and check constraint (OD-44), **and** the rotation-integrity objects added on 2026-08-14 under OD-44 §8: a unique index on `rotated_from_session_id` where not null, two composite rotation foreign keys and the two unique keys they reference | `alembic downgrade 0008`, at the cost in §3.5 |

Revisions 0006–0008 were **not** edited to add the binding. A revision that has
been submitted for review is a revision somebody has read.

Stage D — dropping the legacy Discord columns — is **not** in this package. It is
a separate, later decision after the verification period in the migration
contract §6, and it is the point after which rollback becomes recovery.

### 3.1 Revision 0006 requires two variables and has no defaults

```bash
APP_ENVIRONMENT=development \
DATABASE_URL='postgresql+psycopg:///freedom_dev' \
WEB_DISCORD_GUILD_ID=<guild snowflake> \
WEB_BOOTSTRAP_ADMIN_ROLE_ID=<administrator role snowflake> \
  ./venv/bin/alembic upgrade head
```

The revision inserts the **protected administrator role-capability mapping** and
refuses to run without both snowflakes. There is deliberately no default: a
default would be a production identifier compiled into source, and skipping the
insert would leave the portal with no anchor for administrator capability.

That mapping cannot afterwards be revoked, edited, demoted or shadowed — by the
application, by an ordinary administrator, or by the schema owner. A trigger
refuses every one of those, which is what makes administrator lockout
unreachable through the application (OD-24, ADR 0010 D10).

### 3.2 What the control totals refuse

Stage A checks eight totals **inside its own transaction** and aborts if any
disagrees, so a disagreement rolls the whole stage back and leaves the database
exactly where it started. The two worth knowing by name:

- **T6** is a full-table equality between the old key and the new one: every
  `character_access` row must resolve to an account whose active Discord
  identity *is* that row's own Discord user. It is the evidence that the
  migration mapped rather than guessed.
- **T7/T8** are about the constraint swap: history is the same size it was, and
  the check-constraint inventory of the three append-only tables is exactly the
  reviewed one — so a later migration cannot quietly reintroduce a Discord-only
  attribution rule.

### 3.2a Exactly which existing rows revision 0006 reads and writes

Recorded 2026-08-14, because an earlier handoff summarised this as "no historical
row is read, updated or deleted" and that sentence is false. An operator planning
a maintenance window needs the accurate version:

| Existing table | What 0006 does to it |
|---|---|
| `discord_users` | **Read.** The backfill selects every row that has no `('discord', id)` identity yet, and derives one account and one external identity from each. Not modified |
| `character_access` | **Read and updated.** Every row's `platform_account_id` and `granted_by_account_id` are set from the identity table, resolved through `discord_user_id` and `granted_by_discord_user_id`. Nothing else on the row changes, and no row is inserted or deleted |
| `audit_events` | **Not rewritten.** It gains a nullable column and its attribution check constraint is swapped. Both are catalogue operations |
| `snapshot_imports` | **Not rewritten.** A nullable column and a strengthened `NOT VALID` constraint |
| `foundry_snapshots` | **Not rewritten.** A nullable column and its foreign key; no constraint change |

The append-only claim is about the last three rows of that table and is correct:
`ADD COLUMN` without a default, `ADD CONSTRAINT … NOT VALID` and
`DROP CONSTRAINT` are catalogue-only, and PostgreSQL row triggers do not fire for
DDL — so migration 0002's append-only trigger is neither dropped, disabled nor
evaded. It is never reached.

The `character_access` update is intentional and is the whole point of stage A:
authorization-bearing rows must carry account attribution before stage B can make
those columns `NOT NULL`. Control total T6 is what proves the update mapped
rather than guessed.

The `xmin` evidence proves the **seeded append-only rows** were not rewritten
across the constraint swap. It does not prove — and was never capable of proving
— that the migration read or wrote no historical data anywhere. Those are
different claims, and only the first one is evidenced.

### 3.3 What a downgrade of 0006 costs

Stated here because an operator will read this before running it.

The downgrade restores the legacy `ck_audit_events_human_action_has_an_actor`
constraint **`NOT VALID`**. That is deliberate: by then the table may hold
account-attributed rows the legacy rule is false of, and a validating
`ADD CONSTRAINT` would scan, find them and fail, leaving the downgrade
half-applied.

**Dropping `actor_platform_account_id` discards the attribution of every audit
event written by a break-glass session after the upgrade.** The events survive
with their capability, action, payload and correlation id; their actor becomes
unresolvable. That is a data consequence of the downgrade, not a defect in it,
and it is why a restore-tested `pg_dump` is required before each stage runs
against a database whose history matters.

### 3.4 Runtime grants

After migrating, apply `infra/postgresql/runtime-grants.sql.tmpl` as the schema
owner. The Phase 3 tables are in three bands, and the boundaries are the design:

- **`SELECT, INSERT`** — `role_capability_mapping_events` joins the append-only
  set. The service whose behaviour it records must not be able to edit it.
- **`SELECT, INSERT, UPDATE`** — accounts, identities, sessions, transactions,
  credentials, grants and mappings. **No `DELETE`**: an account is closed and an
  identity retired rather than removed, because audit attribution resolves
  through them after a provider is retired.
- **`SELECT, INSERT, UPDATE, DELETE`** — `oauth_token_grants` (N-11 requires the
  stored provider tokens to be *deleted*, and that privacy control outranks the
  forensic value of the row), `auth_rate_limits` and `webauthn_challenges`.

### 3.5 Revision 0009: the precondition, and what a rollback costs

Stated here because an operator will meet the refusal before they meet the
explanation.

**Upgrading refuses while any `discord_oauth` session row exists.** Such a row
cannot be bound: the transaction that produced it was never recorded, so there is
no value to put in the new column, and the check constraint validates existing
rows. The revision counts them first and refuses with the count and the remedy
rather than letting `ADD CONSTRAINT` fail on a message that names a constraint:

```text
Revision 0009 refused: N Discord OAuth session row(s) predate the completion
binding and cannot be bound … End those logins and re-run:
DELETE FROM sessions WHERE auth_method = 'discord_oauth';
```

Run that statement as the schema owner — the runtime role has no `DELETE` on
`sessions` by design (§3.4) — and re-run the upgrade. The people affected sign in
again. **No history is lost:** a login is recorded by the append-only
`auth.login.succeeded` audit event, not by the session row.

**Revoking is not sufficient.** The constraint is evaluated over every row, and a
revoked row is still a row. `tools/session_revoke.py` therefore does not prepare
a database for this revision.

**Downgrading costs the same thing on the way back.** `alembic downgrade 0008`
drops both columns; every session row survives and keeps working, because the
table returns to exactly its pre-0009 shape. What is destroyed is the record of
which transaction produced which session and every `completion_claimed_at`
timestamp, and nothing reconstructs them — so re-upgrading meets the precondition
above and refuses until those sessions are deleted. Plan a rollback past 0009 as
"every Discord OAuth user signs in again", and take the usual restore-tested
`pg_dump` first.

**A second precondition, added 2026-08-14.** The revision also refuses if the
database already holds a rotation chain the new keys cannot describe — a session
with more than one successor, or a rotation whose account or authentication method
differs from its predecessor's. Neither can be produced by `SessionService`, and
neither is expected to exist, but `ADD CONSTRAINT` validates existing rows, so the
revision counts them first and refuses with the count and the remedy:

```text
Revision 0009 refused: N session rotation(s) disagree with their predecessor's
account or authentication method and M session(s) have more than one successor …
End the affected logins and re-run:
DELETE FROM sessions WHERE rotated_from_session_id IS NOT NULL;
```

That statement ends the affected logins — those people sign in again — and loses
no history, for the same reason as above: rotations are recorded in the
append-only audit trail, not in the session row. Run it as the schema owner.

The downgrade drops these objects with the rest of 0009. Their loss costs nothing
extra beyond what §3.5 already states: they constrain shape rather than carry
data, so a re-upgrade needs only the two preconditions satisfied.

The sequence is rehearsed end to end, both refusals included, by
`tests/test_oauth_completion_binding_migration.py`.

**Grants are unchanged.** 0009 adds columns to `sessions` and
`oauth_transactions`, both already in the `SELECT, INSERT, UPDATE` band, and
creates no new table. `infra/postgresql/runtime-grants.sql.tmpl` needs no edit
and none was made.

### 3.6 Migration 0013 rollback boundary

Added 2026-08-18 by the migration-rollback remediation, and **the part of this
document to read before planning any rollback of P3.3**.

> **Downgrade below revision 0013 is refused while any retained
> reconciliation job records a committed import effect. It becomes
> available only when no such job exists; in normal operation that means
> either no apply has committed, or every completed committed-effect job
> and its result has been removed by the approved N-24 retention process
> and no committed-but-unpublished job remains.**

**Corrected 2026-08-18 by the second migration-rollback remediation.** The
earlier wording — "available until the first apply commits an import effect, and
refused afterwards" — claimed a permanent historical fact the guard does not
record. The guard counts **retained** rows, and N-24 retention removes a
completed terminal job and its result once the retention conditions are met,
while preserving the immutable `snapshot_imports` receipt and the append-only
audit history. Once no committed-effect job survives there is nothing a
downgrade could destroy and nothing the re-upgrade's
`effect_result_accompanies_the_fence` could refuse, so the boundary truthfully
reopens.

Four states an operator must distinguish:

| The database holds | Downgrade below 0013 |
|---|---|
| a **retained completed** committed-effect job | **Refused.** Its `effect_result` is still there to destroy, and the re-upgrade would refuse on the row |
| a **retained committed-but-unpublished** job | **Refused**, and this is the population a downgrade would hurt worst: `effect_result` is the only record of what the publication owes. Retention can never remove it — it is `running`, not terminal, so no age makes it eligible |
| approved retention has removed **all** completed job/result presentation records, import and audit history preserved | **Available**, and genuinely reversible: proved by `…approved_retention_reopens_the_boundary_and_the_round_trip_is_exact` |
| an unused database that never committed an effect | **Available**, as it always was |

**Retention is not a rollback bypass and must not be used as one.** Deleting job
history by hand, shortening the retention period, or running the sweep early to
clear a refusal are all outside the supported procedure; eligibility, the
operator command, its audit event and the 30-day period are unchanged. The
normal operator response to a refusal remains publication of recoverable
outstanding effects and roll-forward recovery.

**The decision is taken under a lock.** `downgrade()` acquires `LOCK TABLE
reconciliation_jobs IN ACCESS EXCLUSIVE MODE` before it counts and holds it until
the migration transaction ends, so a worker transaction already applying an
import must finish before the count sees the database, and one starting later
waits until the migration is done. Both directions are regression-tested against
real PostgreSQL by observing the lock itself:
`…a_downgrade_started_during_an_in_flight_effect_refuses_after_it_commits` proves
the lock is taken **before** the count;
`…a_fence_writer_starting_under_the_held_lock_cannot_commit_until_it_ends` proves
that a writer beginning after the lock is **granted** cannot commit until the
migration transaction ends; and
`…a_fence_writer_arriving_behind_a_pending_lock_request_cannot_overtake_it`
covers the separate queue-fairness property. The generated offline (`--sql`)
script takes
the same lock inside the same `BEGIN … COMMIT` frame, before the guard and
through the drops. Stopping the workers first is still required (below); the lock
is the backstop for the operator who misses that step or whose process is still
draining.

**Status: this boundary is a proposal awaiting Peter/Acceptance Authority
ratification.** What is already implemented is the refusal — 0013 will not
destroy a payload nothing can truthfully reconstruct — because that is the safe
behaviour under any policy. What needs ratification is the operational
consequence: that while a committed effect is retained, rolling P3.3 back is
*application* rollback or roll-forward, not schema downgrade. See the submission
§14 and change-log `C-P3.3-D`.

#### Why the boundary exists

The commit fence writes `reconciliation_jobs.effect_result` — the run's bounded
summary and its blocked create-candidate list — **inside the transaction that
commits the import effect**, alongside `effect_committed_at`. `0013`'s check
constraint `effect_result_accompanies_the_fence` makes the pair inseparable.

`downgrade 0012` drops `effect_result` and deliberately keeps
`effect_committed_at`, which belongs to 0012. Two things then follow, and the
second is the one that closes the door:

1. a committed effect whose result was never published **can never be
   published**: `snapshot_imports` holds the import's immutable receipt, but not
   the blocked-entry list, the `{code, severity, count}` issue counts (the
   receipt keeps bare `issue_codes`), `would_create`, `would_update` or
   `selected_folder_path`, and no truthful value can be invented for them; and
2. **the database can never return to head.** Every truthfully completed apply is
   now a row with a committed effect and no payload, which is exactly what
   `upgrade 0013` refuses on. The remedies that would clear it — deleting
   committed job history, clearing the fence, or manufacturing a result — are all
   forbidden by `.agents/AGENTS.md` and by the P3.3 contract.

So `downgrade()` counts both populations **before it changes anything** and
refuses:

```text
Refusing to downgrade revision 0013: 3 retained reconciliation job(s) record a
committed import effect (2 completed, 1 committed but unpublished). … NOTHING HAS
BEEN CHANGED: the database is still at 0013, complete and usable. Schema rollback
below 0013 is refused while any retained job records a committed effect - roll
forward at 0013 instead. It becomes available again only when no such job
survives, which in normal operation means the approved N-24 retention process has
removed every completed committed-effect job and its result and no
committed-but-unpublished job remains; deleting job history by hand, or
shortening retention to clear this refusal, is not a supported rollback route.
```

The two counts are reported separately because they cost differently. A
`completed` job loses only the ability to return to head. A committed-but-
unpublished one loses that **and** its publication.

`alembic downgrade base` is a downgrade too, and is refused on the same terms.

#### Preflight

Run as the schema owner, before scheduling any downgrade:

```sql
SELECT count(*) FILTER (WHERE state = 'completed')  AS completed_effects,
       count(*) FILTER (WHERE state <> 'completed') AS unpublished_effects
  FROM reconciliation_jobs
 WHERE effect_committed_at IS NOT NULL;
```

Both zero: `downgrade 0012` is available and is genuinely reversible — proved
with realistic rows by
`tests/web/test_migration_0013_rollback_boundary.py::…succeeds_below_the_boundary…`.
Either non-zero: the downgrade will refuse, and the procedure below applies
instead.

Offline (`--sql`) generation carries the same guard as an executable `DO` block
rather than a comment, and it is emitted before the first `DROP`. A generated
downgrade script applied top to bottom therefore stops on the server that runs
it, exactly as an online downgrade would. Do not edit that block out.

#### Worker shutdown and version order

`WORKER_ENABLED` selects the worker process (§7). The compatibility of each
application version with each schema revision is:

| Schema | Application/worker version | Supported? |
|---|---|---|
| `0013` | P3.3 remediated (current head) | **Yes.** The only supported production pair |
| `0012` | P3.3 remediated | **No.** The fence writes `effect_result`; every apply aborts with an undefined-column error and commits nothing. Previews are unaffected, but do not run it |
| `0013` | pre-0013 (0012-era) | **No, but safe-failing.** The old fence writes `effect_committed_at` without a payload, so `effect_result_accompanies_the_fence` aborts the import transaction — no effect commits and no partial state exists. The old reaper and cancellation statements abort on `committed_effect_is_never_denied` the same way. Read paths are unaffected. Acceptable only as the brief interval of a roll-forward deployment |
| `0012` | pre-0013 (0012-era) | The pre-remediation baseline. Supported only as the state a database is in before it has ever reached 0013 |

Consequences for ordering:

- **Roll forward** (`0012 -> 0013`): migrate first, then deploy the new code. The
  old worker cannot corrupt anything at `0013` — it can only fail to commit —
  which is why this order is safe and is the one to use.
- **Roll back** (`0013 -> 0012`), only while the preflight above returns two
  zeros: **stop every worker first** (`systemctl stop freedom-worker`), confirm
  no lease is live, then `alembic downgrade 0012`, then deploy the 0012-era
  code. A remediated worker left running against `0012` would fail every apply.
- Never run a downgrade with a worker running. The refusal is a backstop, not a
  substitute for stopping the process: a worker that commits an effect between
  the preflight and the downgrade turns a supported rollback into a refused one.

#### Recovery procedure when the downgrade is refused

1. **Do not force it.** There is no override flag, and adding one would be adding
   a way to strand the database. `DROP`ping the column by hand has the same
   consequence and no record.
2. **Publish what is outstanding.** If the refusal names any
   *committed but unpublished* effects, start (or leave running) a worker at
   `0013`: `WorkerRuntime.recover()` publishes each one from the two durable rows
   on the reaper's interval (§7.3), consuming no attempt and re-running nothing.
   This does **not** make the downgrade available: the job becomes `completed`
   and is still retained, and a retained completed committed-effect job refuses
   the downgrade exactly as an unpublished one does. What it does is clear the
   population that would have been unrecoverable, move those jobs into the only
   population approved N-24 retention can ever remove, and it is what an operator
   wants done regardless. The boundary reopens when — and only when — retention
   has removed those jobs and their results on its normal schedule. **Do not
   shorten the retention period, run the sweep early, or delete rows by hand to
   reach that point**; none of those is a supported rollback technique.
3. **Roll forward.** Fix at `0013` with a new revision. `docs/implementation-plan.md`
   §14.3 is explicit: applied migrations are never edited; roll forward or write a
   documented recovery migration.
4. **Application rollback, if the problem is the code rather than the schema.**
   Revision `0013` adds one nullable column and two check constraints; nothing
   else in P3.3's read paths depends on it. There is no supported code version
   that runs against `0013` (see the table above), so an application rollback
   past this point requires a recovery migration that gives the older code a
   schema it can write — which is a change requiring maintainer approval, not an
   operator action at 03:00.
5. **Restore, only as a decision that is taken and recorded.** Restoring the
   pre-migration `pg_dump` discards every import applied since it was taken. That
   is a data-loss decision for the Acceptance Authority, not a rollback step.

#### If a *re-upgrade* is refused

`upgrade 0013` refuses on a `0012` database holding a job that records a
committed effect. The message distinguishes the two ways to hold one:

- **the database never reached 0013** — the payload was never written because the
  column did not exist. In a disposable development database, `TRUNCATE` the
  reconciliation tables and re-run. In any database whose history matters, stop
  and ask a maintainer;
- **the database was at 0013 and was taken below it by something other than
  `downgrade()`** — the payload existed and was destroyed. Nothing may
  reconstruct it, and neither clearing `effect_committed_at` nor deleting the
  jobs is permitted. Restore the pre-downgrade backup and roll forward.

#### Retry and crash behaviour

Both directions run inside a single transaction (`migrations/env.py` wraps
`run_migrations()` in `context.begin_transaction()`, and PostgreSQL's DDL is
transactional). A refusal, a crash, a lost connection or a cancelled command
therefore leaves either the **complete** pre-migration schema and data or the
**complete** post-migration schema and data, never half of either — including
`alembic_version`, which moves only on commit. Both commands are safe to re-run
after any failure; a refusal in particular writes nothing, so retrying it costs
nothing and changes nothing until the preflight condition changes.
`tests/web/test_migration_0013_rollback_boundary.py` asserts this in both
directions by injecting a failure part-way through each.

## 4. Emergency access

Everything in this section is **host-local**. There is no HTTP route that issues
a grant or enrols a credential, and that absence is the control: the recovery
path requires existing host authority and cannot be reached from the internet,
even by someone holding a stolen break-glass session.

### 4.1 Before the portal is exposed: enrol two credentials

Migration 0006 inserts the protected *mapping*. The protected **account** is
created by the first enrollment, and until then break-glass has no account to
authenticate. This ordering hazard is why S-15 exists.

```bash
WEB_DATABASE_URL='postgresql+psycopg:///freedom_dev' WEB_ENVIRONMENT=development \
  ./venv-web/bin/python -m tools.webauthn_enrollment enroll \
    --operator "Peter Duscha" --nickname "yubikey-1" \
    --credential-id <base64url> --public-key <base64url COSE key>
```

The registration ceremony itself happens in a browser; this command takes its
result. What is stored is a public key and a counter — **no attestation object,
no private key, no PIN and no biometric material**, none of which ever leaves the
authenticator.

**Enrol at least two.** `retire` refuses to take the account below two, and
production startup refuses below two, because losing every key is unrecoverable
through the application by design. The alternative — a permanent local password —
is a standing credential that exists when nobody is using it, and ADR 0010
rejected it.

```bash
./venv-web/bin/python -m tools.webauthn_enrollment list --operator "…"
./venv-web/bin/python -m tools.webauthn_enrollment retire \
  --operator "…" --credential <record uuid> --reason "…"
```

### 4.2 Last resort: a recovery grant

When every enrolled credential is lost:

```bash
./venv-web/bin/python -m tools.emergency_recovery issue \
  --operator "Peter Duscha" --reason "all passkeys lost in the office move"
```

The token is printed **once**, to the terminal, and stored only as a SHA-256
hash. It is in no row, no log line and no audit payload; the audit record names
the grant's *record id* instead. If the output is lost, the grant is lost —
issue another, which invalidates the first in the same transaction.

It is single use, purpose-bound to emergency login, and valid for ten minutes.

**The residual, stated rather than hidden:** for those ten minutes the token is a
bearer credential. If the operator's terminal or clipboard is compromised in that
window, it is usable. The compensating controls are the ten-minute expiry, single
use, the one-live-grant rule, and an audit record the operator can compare
against their own action.

```bash
./venv-web/bin/python -m tools.emergency_recovery revoke \
  --operator "…" --reason "the terminal was shared"
```

### 4.3 What a break-glass session can and cannot do

It resolves to exactly `{platform_administrator}`, whatever Discord roles the
same human holds. Never Council, never character ownership, never import-apply
authority. It is fifteen minutes idle, sixty absolute, with no extension.

**Fifteen minutes idle means fifteen minutes** (corrected 2026-08-15). Activity
refreshes the idle window by fifteen minutes at a time, not sixty: the operator
who leaves an emergency session alone for a quarter of an hour has to
authenticate again, and no amount of activity carries the session past sixty
minutes from the login. Plan emergency work in that unit. Until this correction
the idle refresh applied the ordinary sixty-minute window to break-glass
sessions, so an emergency session could in principle idle for its whole absolute
lifetime; no P3.1 route reached that code, so the operational effect is a
tightening of documented behaviour rather than a change to behaviour any operator
has observed.

**Amended later the same day.** The first correction was made in the session
*service* only. The repository beneath it still accepted a refresh duration as an
argument, checked only that the authentication method named alongside matched the
row, and would therefore still give a break-glass session the sixty-minute window
if asked for it with the row's own method. The duration is no longer an argument
anywhere: the refresh takes a session id and an instant, and the window is chosen
from configured policy by the method stored on the row.

**Amended a third time, still the same day.** Removing the two arguments moved
the same authority one layer down. The policy object the repository is built with
was itself constructible from an arbitrary method-to-duration mapping, so a
composition that built one giving *every* method sixty minutes would have handed
break-glass rows the ordinary window again — every stated invariant of that
mapping (it names each method once, it names them all, all its windows are
positive) is satisfied by exactly the mapping that is wrong. That object now has
no public constructor: it is built from validated configuration only, and which
methods count as emergency methods is decided inside it rather than supplied.
One such policy is built when the portal starts and the same object is used by
the session service and by the database layer, instead of each deriving its own.

**Amended a fourth time, still the same day, and this one changed the shape
rather than adding another lock.** Three ways past the third correction were
found. The settings object the policy was built from validated nothing of its
own, so a sixty-minute emergency window written directly into it was accepted and
faithfully applied. The database statement was generated by *iterating* the
policy object, so an ordinary subclass could hand the statement one set of windows
while every reported value stayed correct. And the session service still took a
policy of its own beside the database layer's, so nothing but care stopped the two
from disagreeing. The policy object is now gone entirely: the settings type
refuses its own out-of-range values whoever builds it, the database layer derives
its bounds from those settings and owns them, the session service reads that same
object rather than being handed one, and which authentication methods count as
emergency methods is a written-out list — a future method that nobody has
classified stops the portal at startup instead of quietly receiving a window.

The operator-visible rule is unchanged throughout and now holds at every layer —
**fifteen minutes, and sixty from the login, whatever calls it, and whatever a
future caller is built with**. The two numbers still come from
`WEB_EMERGENCY_SESSION_IDLE_MINUTES` and `WEB_EMERGENCY_SESSION_ABSOLUTE_MINUTES`
and are still capped at 15 and 60; nothing in any of these corrections changes a
configurable value, a variable name, a schema object or a deployment step. The
only operator-visible difference is that a configuration file naming a value
above an accepted cap is refused at startup as it always was, and is now refused
by the settings themselves as well.

Within that, it may perform exactly **two** role-capability operations: create a
mapping whose capability is `platform_administrator`, and revoke a non-protected
mapping whose capability is `platform_administrator`. Everything else is refused
`emergency_scope_refused`, before any row is read or written, and the refusal is
recorded with the attempted capability.

A mapping created that way is marked `emergency_continuity`, and **administrator
authority held only through such mappings is itself continuity-scoped** — through
an ordinary Discord login as well. The way out is ratification by a full-scope
administrator on an ordinary-provider session (route R-38, delivered by P3.2).

That is a *persistence* gain and it is recorded as a residual risk rather than
described away: a break-glass session can leave durable administrator continuity
behind it. That is exactly what the recovery case requires.

### 4.3a When a session refuses to continue

Two operations continue an existing session: the **idle refresh** on an ordinary
request, and the **rotation** that N-08 performs when a privilege change is
detected. Each is a single conditional database statement, and each can refuse.

A refusal means the session is no longer live — revoked, past its idle bound, or
past its absolute bound — or, for a rotation, that it is not the session the
caller believed it was. The correct response is always the same, and it is the
opposite of a retry:

> **End the session.** Clear the cookie, treat the request as unauthenticated,
> and send the person back through login. Never retry the operation as though
> still authenticated, and never fall back to serving the request.

Operationally this is not an error condition to investigate. It is what an
expired session looks like from the inside, and a person meeting it should simply
sign in again. A *burst* of refusals against one account is worth attention —
that is the shape of a stolen cookie being replayed after the session it came
from ended — and the `auth.session.revoked` audit events are where to look.

**Nothing is written by a refusal.** A refused refresh or rotation leaves the
session row exactly as it was: no `last_seen_at`, no expiry change, no revocation,
no successor row and no success audit event. An operator reading the table after
a refusal sees the state that existed before it.

**Neither operation can extend a session's absolute lifetime.** The absolute bound
is written once, when the session is created, and no refresh or rotation writes it
again. Twelve hours from a Discord login (N-07) and sixty minutes from a
break-glass login (N-15) are therefore the real ceilings, whatever the person does
in between. A session that must end sooner is ended with
`tools/session_revoke.py`, not by waiting for an expiry.

**Current reach.** As of P3.1 no HTTP route calls the idle refresh — the portal's
request path does not yet exist — so this section describes a contract the P3.2
request handling must meet rather than behaviour running in production today.
Rotation is reachable through privilege-change detection.

### 4.4 After a suspected compromise

```bash
./venv-web/bin/python -m tools.session_revoke \
  --protected-admin --operator "…" --reason "suspected compromise"
```

Revocation is server-side and immediate: sessions are database rows and
resolution filters on `revoked_at` on every request, so there is no cache for a
revoked session to slip through. The stored provider tokens go with them.

## 5. The kill switch

Three layers, weakest first, **all of which leave the Discord bot and Foundry
running**:

```bash
./venv-web/bin/python -m tools.portal_kill_switch on  --operator "…" --reason "…"
./venv-web/bin/python -m tools.portal_kill_switch status
./venv-web/bin/python -m tools.portal_kill_switch off --operator "…" --reason "…"
```

Layer 1 is the file above: every route except `/healthz` and `/static/*` answers
`503` with a static maintenance body, effective within one second, because the
file is `stat`-ed at most once per second per process.

Health stays up deliberately. It is on the loopback bind, is not published by
Caddy, and is what an operator watches while recovering.

`/static/*` stays up deliberately too, **added 2026-08-19** by the accepted D-03
correction. The maintenance body, the login page and the safe error page are the
pages a person sees while the portal is disabled, and serving them unstyled makes
the incident look worse than it is. It is a narrow exemption: the static mount is
unauthenticated, reads no database, opens no transaction and reaches no
application service, so nothing the switch exists to stop is reachable through it.
Every `/v1/*` route is refused exactly as before, and the host check still applies
to an asset — a request under an unknown `Host` is `400` whether the switch is on
or off. See §9.

Layer 2 is `systemctl stop freedom-web`; layer 3 is removing the Caddy site
block. Neither exists yet — the deployment work is after the Phase 3 gate.

## 6. Health

`GET /healthz` on the loopback bind returns check names and pass/fail, and
nothing else: no connection string, no host, no credential, no player count, no
identity, no queue contents.

```json
{"status": "ok",
 "checks": {"database": true, "migrations": true, "artifact_store": true,
            "worker_heartbeat": true, "expired_leases": true,
            "identity_provider": true, "kill_switch": true},
 "version": "phase-3-p3.1", "environment": "production"}
```

`environment` is included on purpose: the single most useful thing a monitor can
tell you is that production is running production configuration.

`worker_heartbeat` and `expired_leases` were reported as `true` with nothing
behind them in P3.1, because the worker did not exist. **P3.3 makes them real**,
and what each one actually observes is worth knowing before it wakes somebody:

| Check | Observes | Fails when |
|---|---|---|
| `worker_heartbeat` | the age of the oldest `queued` job | something has been waiting longer than one lease plus one reaper interval (60 + 15 s), i.e. **nothing is draining the queue** |
| `expired_leases` | the age of the oldest expired lease still `running` | the same bound is exceeded, i.e. **the reaper is not running** |

Two limits, stated rather than implied:

- **An empty queue reports `ok`.** A worker with nothing to do writes nothing, so
  this check cannot tell an idle worker from an absent one when there is no work.
  A monitor that needs that distinction watches `systemctl is-active
  freedom-worker`, which is the thing that actually knows.
- **The tolerance is generous on purpose.** These answer "nothing is draining the
  queue" and "the reaper is not running" — not "the worker is healthy". A job
  legitimately takes ten seconds; a job waiting seventy-five has nobody.

Both are numbers only. No job id, no requester, no checksum, no queue contents:
a health endpoint that named the work in flight would disclose who is importing
what to anything that can reach the loopback port.

## 7. The reconciliation worker

`freedom-worker` claims and executes durable preview and apply jobs. It is a
**separate process** — not a thread in the portal — for three measured reasons
recorded in the operational contract §3: the work holds the GIL for its whole
~9.6 seconds, its peak memory is per-job and unmeasured, and a web deploy should
be quick while a worker holding a 60-second lease should drain.

```bash
./venv-web/bin/python -m tools.freedom_worker            # the service
./venv-web/bin/python -m tools.freedom_worker --once     # one tick, then exit
./venv-web/bin/python -m tools.freedom_worker --reap-only  # reap and publish committed effects, claim nothing
```

It runs the **same code from the same virtualenv** as `freedom-web` and reads the
same variables. The two differ by `WORKER_ENABLED`, and each process refuses the
other's value (S-11, both directions).

**Corrected 2026-08-25 (F5).** This paragraph used to offer two ways to arrange
that: "two environment files identical but for that line, or one file plus
`Environment=WORKER_ENABLED=true` on the worker unit." **The second one cannot
work**, and a staging deployment built on it left the worker crash-looping on S-11
from the day the unit was installed until the day someone read the journal.

The reason is a systemd precedence rule. `systemd.exec(5)`, on `EnvironmentFile=`:

> Settings from these files override settings made with `Environment=`.

The one shared file is also `freedom-web`'s, so it sets `WORKER_ENABLED=false`.
An `Environment=WORKER_ENABLED=true` line on the worker unit is read first and
then **overwritten** by the file, and the worker refuses itself with S-11 on every
start. The unit reads as though it is configured correctly, which is what made
this expensive to see: `systemctl show` reports both settings, and nothing in the
unit says which one wins.

Use one of these instead:

1. **Two complete environment files**, one per unit, identical but for that line.
2. **The shared file plus a small second file listed after it** on the worker
   unit — the arrangement `infra/systemd/freedom-worker.service.tmpl` now carries.
   The second file holds `WORKER_ENABLED=true` and nothing secret. Order is
   load-bearing: *"If the same variable is set twice from these files, the files
   will be read in the order they are specified and the later setting will override
   the earlier setting."*

Whichever is used, verify it rather than assume it: `systemctl is-active
freedom-worker` after a start, because `/healthz`'s `worker_heartbeat` **will not
tell you** — it reports whether the queue is draining, and an empty queue drains
trivially whether or not any worker exists — see the `/healthz` check table
above, where `worker_heartbeat` is *the age of the oldest queued job*.

`infra/systemd/freedom-worker.service.tmpl` is the unit, and the three numbers in
it each have a reason written beside them.

The worker exposes **no listener at all**. It is reached by nothing; it reaches
PostgreSQL over the loopback socket and the restricted artifact store on disk,
and nothing else. It makes no Discord call and no Google call.

### 7.1 Starting and stopping

`SIGTERM` asks the loop to stop. The current attempt finishes or is abandoned at
its next heartbeat, and **an abandoned attempt is recoverable rather than
failed**: the job returns to `queued` while an attempt remains. `TimeoutStopSec`
is 30 seconds — deliberately below the 60-second lease, so a restarting process
never holds a claim it can no longer heartbeat.

Stopping the worker is safe at any moment. Nothing is lost: a claimed job's lease
expires, the reaper requeues it, and the durable effect of an apply is fenced by
`uq_snapshot_imports_applied_input` and `snapshot_imports.request_key` rather
than by the job's state. An apply that had already committed when the process
died is found by the retry and returned as a duplicate.

### 7.2 The kill switch reaches the worker too

Layer 1 (§5) engages the worker as well as the portal: it **claims no new work**
and abandons the current attempt at its next heartbeat. One operator action
closes both processes, and neither the Discord bot nor Foundry is affected.

### 7.3 When a job is stuck

| Symptom | What it means | What to do |
|---|---|---|
| `expired_leases` failing | the reaper is not running | check `systemctl is-active freedom-worker`; `--reap-only` runs one reaper pass **and one effect-publication pass** without claiming work |
| `worker_heartbeat` failing, queue non-empty | nothing is claiming | as above |
| A job `failed` with `attempts_exhausted` | three claims expired without completing | the job's audit event names the last `lease_owner`; that is the process that stopped answering |
| A job `failed` with `parse_refused` | the artifact is malformed **for this deployment** | deterministic — it will not succeed on a retry; the snapshot needs re-exporting |
| A job `failed` with `artifact_unavailable` | the store cannot read the checksum | check `WORKER_ARTIFACT_ROOT` and `/healthz`'s `artifact_store` |
| A preview `stale` with `folder_changed` | an administrator selected a different folder | produce a new preview; this is the control working |
| A cancellation answered `409` with `already_applied` on a `running` apply | the apply's effect committed before the cancellation reached the row | the import is durable and the job completes; read the receipt. `reconciliation_jobs.effect_committed_at` is when it committed. **No cancellation was recorded**: the refusal writes no audit event and does not set `cancel_requested_at` |
| `/healthz` reporting a worker with an **outstanding attempt** | a job's execution thread did not stop when the worker stopped watching it, so the worker is claiming nothing (N-41) | nothing is at risk — the commit fence makes that thread unable to commit — but the worker is idle. Restart `freedom-worker`; the job is recovered within `N-23 + N-44`, and a stalled worker still reaps and still publishes committed effects, because `tick` does both before it consults its own state |
| A job `completed` whose audit event carries `recovered: true` | the effect committed and the process that ran it died before publishing the result; the platform published it from the payload the commit fence made durable (**RR-16, closed 2026-08-18**) | nothing to do. The receipt is the receipt, the counts are the import's own, and the event names the `lease_owner` that stopped answering — that is the process to look at in the journal. A job `failed` with `attempts_exhausted` over a committed effect is no longer representable: migration 0013's `committed_effect_is_never_denied` refuses the row |
| A job `running` with an expired lease that neither reaps nor completes | its effect committed and the recovery publication is failing; `expired_lease_age_seconds` climbs past `N-23 + N-44` and keeps climbing | the import is durable and is **never** written `failed` — that is the design, not a stall to force through. Read the worker journal for the exception; it names the job and which durable half could not be read. Do not move the job by hand: read `snapshot_imports` for the receipt and escalate |

There is no "unstick" command and there is deliberately no way to move a job
between states by hand: `reconciliation_jobs` holds check constraints that make
the invalid states unrepresentable, and a statement that tried would be refused
by PostgreSQL rather than quietly succeed.

### 7.4 Retention (N-24)

Job and result **presentation records** are removed 30 days after the job reaches
a terminal state. `snapshot_imports`, `audit_events` and `foundry_snapshots` are
append-only and are **never** touched: a sweep that has run its course removes
the working papers and leaves the decision.

```bash
./venv-web/bin/python -m tools.job_retention --report
./venv-web/bin/python -m tools.job_retention --apply --operator "…"
```

It runs **as the schema owner**, not as the runtime role, and that is a control:
the runtime role holds no `DELETE` on `reconciliation_jobs`, because a web
process or a worker that could delete a job could delete the record of a refused
apply. `--report` is the default; `--apply` requires a named operator and is
recorded as an audited act carrying a count and that name — never a job id, a
checksum or a requester.

`--limit` bounds one pass (default 500, maximum 10 000) and is refused before a
connection is opened if it is zero, negative or above that maximum. A backlog is
several bounded sweeps, never one long transaction; a sweep that has caught up
removes zero and is safe to repeat.

**What a sweep removes and what it retains** (corrected 2026-08-18):

- a terminal job more than 30 days past its `finished_at`, together with its
  result row if it has one — and *only* if that result has also passed its own
  `expires_at`;
- a `failed` or `cancelled` job that never produced a result, on its terminal
  age alone. Before the correction these were invisible to every sweep and
  accumulated indefinitely;
- **nothing** that a retained job still needs: an apply names the preview it was
  confirmed from with `ON DELETE RESTRICT`, so a preview whose apply is younger
  than the retention age stays, and the whole graph above it stays with it.

The output distinguishes the two numbers. `N terminal job(s) past their N-24
retention` is what was *considered*; `Removed M job(s)` is what actually went;
and a `Retained` line names the difference, which is the answer to "why did it
not remove everything it just counted".

## 8. Running the tests

Two commands, because the portal's dependencies live in the portal's virtualenv
and the bot's virtualenv is a live production environment this package does not
add a web framework to:

```bash
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv/bin/python -m pytest
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv-web/bin/python -m pytest tests/web
```

The first command does not collect `tests/web` — a `pytest_ignore_collect` hook
refuses to descend into it when FastAPI is not importable, so an absent
dependency is a skipped directory rather than a collection error.

Both use the same disposable-database guards as every other database test, and
`TEST_DATABASE_URL` must name the local `freedom_test` socket. A URL that is not
the disposable test database **fails** the run rather than skipping it.

## 9. Static assets (M-01)

**Added 2026-08-19** by the accepted D-03 backend-contract correction
(change-log `C-P3.4-A`, item D-03-1). The contract is route contract §1.2 and
operational contract §4.4; what an operator needs is short.

`freedom-web` serves `/static/*` itself, out of `adapters/web/static/` inside the
deployed package. There is **no** configuration for it: no environment variable
for the root, none for the cache policy. Both are properties of the code, so
there is no operator-supplied path for a mistake to point somewhere else.

| Question | Answer |
|---|---|
| Does Caddy need a `file_server` or a `root` directive? | **No.** `/static/*` is proxied like every other path. Adding one would move the CSP and `nosniff` off the application, which owns every header but HSTS |
| Do assets deploy separately? | **No.** They ship with the application, in the same unit of deployment. No bucket, no sync step, no CDN — the accepted CSP (N-26) permits no remote origin |
| Do they need backup? | **No.** The root holds no state and no operator data. It is restored by redeploying |
| Do asset requests appear in the audit log? | **No.** They are unauthenticated reads of public files |
| Are they available during maintenance? | **Yes**, deliberately — see §5 |
| Is the surface authenticated? | **No.** `GET` and `HEAD` only, no session, no capability, no CSRF token. The host check (N-01) still applies |

**The root is currently empty**, holding one zero-byte `.gitkeep`. That file
exists because the framework refuses to start against a missing static directory
— which is the behaviour worth keeping, since the alternative is a mis-deployed
portal that starts normally and answers `404` to every asset. Production CSS,
vendored HTMX and the emblem are **P3.4's** work and are not in the tree.

If a deployment ever answers `404` for an asset that is present on disk, check
the name against the accepted grammar before anything else: a leading dot, a
space, a semicolon or a non-ASCII character in any path segment is refused by
design, and the refusal is deliberately indistinguishable from a missing file.
