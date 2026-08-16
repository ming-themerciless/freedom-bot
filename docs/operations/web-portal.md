# Operating the Freedom Blades web portal (Phase 3 P3.1)

Status: P3.1 implementation document. **Nothing here has been deployed.** The
portal has no systemd unit, no Caddy site block and no staging environment yet;
those belong to P3.5 and the separate deployment gate. What this document
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

Layer 1 is the file above: every route except `/healthz` answers `503` with a
static maintenance body, effective within one second, because the file is
`stat`-ed at most once per second per process.

Health stays up deliberately. It is on the loopback bind, is not published by
Caddy, and is what an operator watches while recovering.

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

`worker_heartbeat` and `expired_leases` are reported as `true` in P3.1 with
nothing behind them: the worker and its lease reaper are P3.3's, and reporting
them as failing would be a false alarm about something that does not exist while
reporting them as passing would be a claim nothing supports. The names are in
the accepted VM-16 vocabulary so P3.3 can make them real without a contract
change.

## 7. Running the tests

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
