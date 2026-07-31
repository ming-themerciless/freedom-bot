# Phase 1 database development and recovery

Status: Phase 1 working document. OD-21 selects host-managed PostgreSQL 16;
OD-22 places staging on this host with the strict separation below.

## Isolation

Development and test databases contain synthetic data only. They must use
separate database names and roles from production. `TEST_DATABASE_URL` must
point at a disposable PostgreSQL database; tests refuse to use `DATABASE_URL`.

The host uses separate databases and login roles:

| Environment | Database | Login role | Permitted data |
|---|---|---|---|
| Development | `freedom_dev` | `freedom_dev_app` | Synthetic only |
| Test | `freedom_test` | `freedom_test_app` | Disposable synthetic only |
| Staging | `freedom_staging` | `freedom_staging_app` | Staging fixtures/import rehearsals only |
| Production | `freedom_production` | `freedom_production_app` | Production |

Names are part of the safety boundary. An environment file whose database name
does not match its service environment must fail validation before connecting.
All four databases remain loopback-only, and every destructive or
schema-changing operation reaches them through the local Unix-domain socket
rather than TCP (see *Destructive and schema-changing work uses the Unix-domain
socket*). Sharing a host does not mean sharing a database, role, credential,
service account, or Foundry/Discord endpoint.

The runtime application role does not own the schema and cannot run migrations.
The migration role is used only during an explicit deployment step.

### How the boundary is enforced

`adapters/database/config.py` validates a URL before anything connects, and it
has two callers:

- `migrations/env.py` validates every Alembic invocation. `APP_ENVIRONMENT`
  selects the expected database and **defaults to `development`**, so a bare
  `alembic upgrade head` can only ever reach `freedom_dev`. Migrating any other
  environment is a deliberate act:

  ```bash
  APP_ENVIRONMENT=staging DATABASE_URL='postgresql+psycopg:///freedom_staging' \
    ./venv/bin/alembic upgrade head
  ```

- `tests/conftest.py` validates `TEST_DATABASE_URL` before the integration
  fixtures run, because those fixtures run `alembic downgrade base` and drop
  every table. A URL that is not the disposable test database, is not the local
  Unix-domain socket, or is equal to `DATABASE_URL` **fails the run** rather than
  skipping it.

#### Destructive and schema-changing work uses the Unix-domain socket

`ConnectionPolicy` in `adapters/database/safety.py` names two levels, and the
call site chooses:

| Policy | Accepts | What it proves |
|---|---|---|
| `UNIX_SOCKET_ONLY` | no host, or an absolute socket directory | the connection is a file on this host |
| `SOCKET_OR_LOOPBACK` | the above, plus `127.0.0.1`, `localhost`, `::1` | the target is not a named remote host — **nothing more** |

**Online migrations, the destructive test fixtures and the backup/restore drill
all require `UNIX_SOCKET_ONLY`.** `postgresql+psycopg://user@127.0.0.1/freedom_test`
is refused for those workflows, and so is a `PGHOST`/`PGHOSTADDR` that supplies a
loopback address to a hostless URL.

That is not because loopback is remote. It is because **a loopback address
cannot be distinguished from a tunnel**:

```text
ssh -L 5432:localhost:5432 elsewhere     # then connect to 127.0.0.1:5432 here
```

The session arrives at PostgreSQL on `elsewhere`, from sshd, over *that* host's
loopback interface. The server therefore reports loopback for both
`inet_server_addr()` and `inet_client_addr()`, `current_database()` answers with
whatever database name the URL asked for, and every check that inspects
addresses says "local". A connection pooler or any other TCP proxy has the same
shape. **Earlier revisions of this document and of the code claimed the address
check caught port forwarding. That claim was false and has been withdrawn.**

A Unix-domain socket is a file on this machine, so a TCP tunnel cannot present
one, and a server reached through one reports null addresses at both ends.

Residual, stated rather than hidden: a deliberately forwarded *socket*
(`ssh -L /tmp/s:/remote/s`) would still answer with null addresses. That is a
hand-built configuration on the operator's own host, not the ordinary
`ssh -L 5432:…` accident these guards exist to refuse, and no in-process check
can exclude it.

An ordinary *runtime* connection — one that creates and drops nothing — is
outside this rule and may use `SOCKET_OR_LOOPBACK`, which is what
`DatabaseSettings.from_mapping(..., policy=…)` is for. The default is the strict
policy, so a caller has to ask for the weaker one by name.

#### `PGHOSTADDR` overrides the socket URL — operators must unset it

**A socket URL is a socket only while `PGHOSTADDR` is unset.** libpq treats
`host` and `hostaddr` as two separate parameters, each with its own environment
default, and `hostaddr` is the one that decides where the connection goes:

| `hostaddr` | `host` | What libpq does |
|---|---|---|
| unset | unset | connects to the default Unix-domain socket directory |
| unset | `/var/run/postgresql` | connects to that socket directory |
| unset | `localhost` | resolves the name and connects over TCP |
| **set** | anything, including a socket directory | **connects over TCP to `hostaddr`**; `host` is kept only as a name for authentication |

So this configuration is a TCP connection to `127.0.0.1`, not a socket:

```bash
export PGHOSTADDR=127.0.0.1
DATABASE_URL='postgresql+psycopg:///freedom_test?host=/var/run/postgresql'
```

Setting `PGHOSTADDR` to a **remote** address is worse than a policy violation:
the migration or test role's credentials are offered to that server before
anything on this host can object. Every static guard therefore refuses the
combination *socket directory plus any host address* outright, under **every**
policy, before an engine is created or a connection is attempted:

- `alembic upgrade|downgrade` (online) — no engine is created;
- `alembic … --sql` (offline) — no script is emitted, not even the banner;
- `pytest` with `TEST_DATABASE_URL` — the run fails before any fixture;
- `backup-restore-drill.sh` — gate 0c refuses `PGHOSTADDR` outright, ahead of
  any `PGHOST` check, and exits `3` having created nothing.

**If a command refuses with "names the Unix-domain socket directory … and …
names the host address …", `unset PGHOSTADDR` and re-run.** Do not work around
it by removing `?host=` from the URL: that produces a TCP connection to the same
address, which the socket policy then refuses for the reason above. `PGHOSTADDR`
belongs to no documented Freedom Blades workflow; the topology in this document
is one loopback-only cluster per environment reached through its socket.

#### One target, or none: multi-host URLs are refused

A URL may name more than one server. libpq supports multi-host failover, and the
list can be spelled four ways — all of which are **refused**:

```text
?host=127.0.0.1&host=db.example.org     a repeated query parameter
?host=127.0.0.1,db.example.org          a comma-separated value
//127.0.0.1,db.example.org/freedom_dev  the same list in the URL authority
PGHOST=127.0.0.1,db.example.org         the same list in the environment
```

The same applies to a repeated or comma-separated `port`, to a repeated
`dbname`, and to a URL that names one component **twice with different values**
— `postgresql+psycopg://127.0.0.1/freedom_dev?host=db.example.org` connects to
`db.example.org`, not to `127.0.0.1`, so it is refused as undecidable. A
`?service=` parameter is refused for the same reason `PGSERVICE` is: it moves
the target definition outside this repository.

`?hostaddr=` is **not** treated as another spelling of the host. It is resolved
as its own component, with `PGHOSTADDR` as its default, and then applied ahead
of the host — see *`PGHOSTADDR` overrides the socket URL* above. A URL naming a
remote `hostaddr` beside a loopback `host` is still refused; what changed is
that it is refused because the *address* is remote, which is what libpq dials,
rather than because the pair looked ambiguous.

Two *local* hosts are refused as well. The policy is about how many targets a
URL names, not about which of them happen to be safe: the topology above is one
loopback-only cluster per environment, and no failover target is approved. If
one is ever needed, that is a maintainer decision and an ADR, not a relaxation
of this guard.

#### The URL is checked, and then the connection is checked

A URL is not a connection. A `localhost` remapped in `/etc/hosts`, an inherited
`PGHOST`, or a failover target that chose its second host can all put a session
on a server the URL never named. So both callers run a second, live check on the
**same connection** the work will use, before any DDL:

- `migrations/env.py` calls `verify_connected_unix_socket_target()` after
  `connect()` and before `context.run_migrations()`;
- `tests/conftest.py` calls it before the first `alembic downgrade base`.

It asks the server two things: `current_database()`, and whether
`inet_server_addr()` and `inet_client_addr()` are **both null** — a Unix-domain
socket. A mismatch on either half refuses. Loopback addresses are refused here
too, for the reason above: they are exactly what a forwarded port reports.

**The live check cannot replace the static one.** It runs on an established
connection, and establishing a connection is what sends the credentials. A
`PGHOSTADDR` pointing at a server outside this host would already have been
handed the migration role's password by the time the server could be asked
anything. That is why the socket/address contradiction is refused during
resolution, before an engine exists.

Alembic owns its own transaction. The verification query implicitly opens one on
the migration's connection, so `env.py` ends it with `connection.rollback()`
before `context.begin_transaction()`; without that the DDL would be discarded
when the connection closed and migrations would report success while changing
nothing. `test_online_migrations_run_against_a_verified_local_target` drives
head → base → head against real PostgreSQL to keep that honest.

#### Offline (`--sql`) migrations cannot be verified

`alembic upgrade head --sql` generates a script and **never connects**, so the
live check has no connection to interrogate. Offline mode therefore:

- runs the full static validation, exactly as online mode does — an
  unverifiable, remote, TCP, multi-host or wrong-environment `DATABASE_URL`
  produces no script at all; and
- prepends a warning to the generated script, as SQL comments, stating that
  nothing in it proves which server it will be applied to.

**The operator carries the target check for an offline script.** Before applying
one, confirm the target on the connection that will apply it:

```bash
psql --dbname=freedom_staging -c \
  'SELECT current_database(), inet_server_addr(), inet_client_addr();'
```

**Both addresses must be null** — that is a Unix-domain socket. Loopback
addresses are not sufficient; see the tunnel above. Take a backup first. Prefer
online `alembic upgrade head`, which verifies its own connection and refuses a
target it cannot prove. Offline mode is for review and for change-controlled
hand-off, not for routine deployment.

## Empty-database check

```bash
DATABASE_URL='postgresql+psycopg://migration_role@/freedom_dev' \
  ./venv/bin/alembic upgrade head
```

Then run the integration tests with a different disposable database:

```bash
TEST_DATABASE_URL='postgresql+psycopg://test_role@/freedom_test' \
  ./venv/bin/python -m pytest -m database
```

Both URLs name no host, which is the Unix-domain socket. An explicit
`?host=/var/run/postgresql` is equivalent — **provided `PGHOSTADDR` is unset**,
which is the one environment variable that silently converts either spelling to
TCP. A loopback URL such as
`postgresql+psycopg://test_role@127.0.0.1/freedom_test` is **refused** by both
commands — see *Destructive and schema-changing work uses the Unix-domain
socket* and *`PGHOSTADDR` overrides the socket URL*.

`alembic check` proves the committed migration and the mapped metadata have not
drifted apart. It runs in CI-equivalent form as
`tests/test_database_postgresql.py::test_migration_matches_table_metadata`, and
manually as:

```bash
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/alembic check
```

## Runtime role grants

After migrating, apply `infra/postgresql/runtime-grants.sql.tmpl` as the schema
owner, substituting `__APP_ROLE__` through the deployment's secret-safe
templating. The runtime role gets no `CREATE`, and only `SELECT, INSERT` on
`audit_events` — that grant is what makes the audit trail append-only in normal
operation. `tests/test_runtime_grants.py` keeps the template in step with the
schema, but the grants themselves are only exercised where a role can be
created; see the Phase 1 handoff for what that leaves unverified.

## Backup and recovery

Before any production migration:

1. stop writes or establish a documented consistent-snapshot boundary;
2. create a PostgreSQL custom-format backup with `pg_dump -Fc`;
3. copy the backup off-host and record its checksum;
4. restore it into an empty database with `pg_restore`;
5. run schema and reconciliation checks against the restored database;
6. only then apply the production migration.

### Development drill

`infra/postgresql/backup-restore-drill.sh` performs the whole round trip —
dump, checksum, destroy the schema, restore, and compare the table/row
inventory before and after — so what is verified is the *restore*, not that a
backup command exited zero (plan §14.3):

```bash
./infra/postgresql/backup-restore-drill.sh freedom_dev /var/tmp/drill
```

It refuses any database other than `freedom_dev` or `freedom_test`. Recovering
staging or production means restoring a verified off-host backup under the
procedure above, never running a drill script against live data.

#### What the drill validates before it destroys anything

A database *name* is not a database. libpq fills in the host, port and even the
database from `PGHOST`, `PGHOSTADDR`, `PGPORT`, `PGDATABASE` and a connection
service file, so `freedom_test` can be pointed at another server. The drill
therefore:

- refuses `PGSERVICE`, `PGSERVICEFILE`, `PGOPTIONS` and `PGDATABASE` outright;
- refuses `PGHOSTADDR` outright — an address is always a TCP connection, and it
  is checked **before** `PGHOST`, so naming the socket directory in `PGHOST`
  cannot rescue an inherited address
  (`test_the_drill_refuses_a_host_address_beside_a_socket_directory`);
- accepts `PGHOST` only as an **absolute Unix socket directory**, or unset, which
  is libpq's default socket directory. `localhost`, `127.0.0.1` and `::1` are
  refused, because a forwarded port cannot be distinguished from a local server;
- pins the validated connection — `PGHOST` as validated or absent, every
  redirecting variable removed — so the dump, the inventory, the drop and the
  restore cannot resolve differently from one another; and
- asks the server itself which database it landed in and requires
  `inet_server_addr()` and `inet_client_addr()` to be **both null**, proving a
  Unix-domain socket, before anything is dumped or dropped.

It exits `2` for a non-disposable name and `3` when the connection cannot be
proven safe, having touched nothing — the work directory is not even created.

If a drill exits `3`, unset the libpq variables it names and re-run over the
socket. Do not work around it by renaming the database, and do not re-add a
loopback `PGHOST`.

#### The in-place drill is not failure-atomic

**This is a known property, not a defect, and it needs an operator to know it.**
The drill dumps `freedom_dev`, then drops the `public` schema of that same
database, then restores into it. Between the drop and a successful restore the
database is **empty**. If the restore fails — a corrupt dump, a full disk, a
killed session — the database is left empty or partially restored and does not
recover on its own.

Nothing else is at risk: the drill only ever runs against a disposable database.
But the drill is *not* a safe way to prove a backup you cannot afford to lose.

**Recovery.** The dump and its checksum are kept, and the script prints
`RECOVERY REQUIRED` naming both. Restore from it:

```bash
sha256sum --check /var/tmp/drill/freedom_dev.dump.sha256
pg_restore --dbname=freedom_dev --no-owner --no-privileges \
           --single-transaction --exit-on-error /var/tmp/drill/freedom_dev.dump
```

If the dump is also unusable, the database is disposable scratch state — rebuild
it from migrations instead:

```bash
APP_ENVIRONMENT=development DATABASE_URL=<url> ./venv/bin/alembic upgrade head
```

Re-running the drill is **not** a recovery step: it would dump the empty
database and overwrite nothing useful.

A restore into a *separate* empty database would avoid this window entirely.
That variant has **not** been implemented or tested here, so it is not claimed.

## Downgrade and recovery strategy

`0001` has a tested `downgrade()`, and
`tests/test_database_postgresql.py::test_migrations_apply_to_empty_postgresql_and_downgrade`
drives empty → head → base → head against real PostgreSQL. That reversibility is
a **development** facility.

Once a database holds operational records the recovery path is different, and
deliberately so:

| Situation | Action |
|---|---|
| Development or test schema is wrong | `alembic downgrade base`, then `upgrade head` |
| Migration fails part-way | PostgreSQL runs DDL transactionally, so the failed migration rolls back; fix it forward and re-run |
| A released migration is wrong | Write a new, documented recovery migration. Never edit an applied migration (ADR 0003, plan §14.3) |
| Data loss or corruption | Restore the pre-migration `pg_dump -Fc` backup, verified by checksum, into an empty database |

`downgrade()` on a populated database drops tables and therefore destroys data.
It is not the production rollback procedure and must not be used as one.

## The authorization model this schema assumes

Settled by [OD-37](../discovery/open-decisions.md). Phase 1 stores the data;
Phase 3 enforces the rules.

**There are two independent paths to a character, not one.**

1. **A per-character link** — a row in `character_access`. A character has
   exactly one `owner`, plus any number of `co_owner`, `delegate` and `viewer`
   links. `uq_character_access_one_active_owner` enforces *at most* one active
   owner. Requiring *at least* one cannot be a table constraint: the Phase 2
   importer has to create a character before Council has resolved who owns it,
   which is the same reason `characters.level` is nullable. **The "exactly"
   half of the ruling is an application invariant, and Phase 2's reconciliation
   report must list every character that has no active owner.**

2. **A role** — Guild Council members may access and modify *every* character.
   That capability comes from holding the configured Council role snowflake,
   read from `discord_membership_roles`, and **never** from an access row.
   Council is deliberately absent from the `access_kind` vocabulary; a query
   that answers "may this user modify this character?" with
   `character_access` alone is wrong.

Ownership transfer is revoke-then-grant, not an update: the partial index covers
active rows only, so the outgoing owner's row survives with its `revoked_at` and
reason intact.

**Every modification is logged**, and `audit_events.actor_capability` records the
authority it was made under — `guild_council` for a Council override,
`character_owner` for an owner editing their own character. Without it the audit
cannot distinguish the two, which is the whole point of allowing Council to
reach every character. It is `NOT NULL`, and `service_principal` and `system` are
the only capabilities permitted to have no acting Discord user.

## Deviations from plan §7 worth a reviewer's attention

- Plan §7.1 names `discord_role_snapshots`. Phase 1 implements
  `discord_membership_roles`: the observed role IDs for a membership, cascading
  from `discord_guild_memberships`, whose `observed_at` carries the snapshot
  time. The name states what the row is rather than how it was obtained.
- Plan §7.1 also names `service_principals` and `sessions`, and §7.2 names
  `external_worlds`, `sync_runs`, `sync_snapshots`, `sync_differences` and
  `sync_resolutions`. None has a Phase 1 use case, domain model or test, so
  none is created — plan §7.3: *"Do not create every future table in the first
  migration."* `external_actor_mappings.world_id` is a plain identifier until
  `external_worlds` exists to reference.
