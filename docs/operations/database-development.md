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
The drill's *other* `2` — the runtime-role refusal below — happens later, after
the dump; see that section for exactly what exists on disk when it does.

#### The runtime role the restore has to put back (finding DS-R8-1)

`pg_restore --no-privileges` discards every `GRANT` in the archive, so before it
destroys anything the drill asks which non-owner role holds table grants on
`public` and re-applies `runtime-grants.sql.tmpl` for that role afterwards. That
question has three answers and the drill decides which one it has **before**
step 4, while there is still nothing to recover:

- **no such role** — nothing is re-applied, and the drill says so. This is the
  ordinary case for a database only its owner ever connects to.
- **exactly one** — the name is used **exactly as the catalog holds it**, and it
  must be a *supported runtime role name*: lower case, no surrounding or
  embedded whitespace, no reserved key word, no special role spelling
  (`public`, `user`, `current_user`, `session_user`, …), no `pg_` prefix, at
  most 63 bytes. Anything else exits `2`. Both supported runtime roles —
  `freedom_runtime`, `freedom_runtime_test` — have that shape.

  **Why that is narrower than "a valid identifier" (finding PR-20260907-2).**
  The drill renders the name into a `sed` replacement and into **unquoted** SQL,
  and an unquoted identifier is not the string you typed:

  - PostgreSQL **down-cases** it, so a catalog role `MixedCase` becomes
    `mixedcase` in `GRANT … TO MixedCase` — a different role, or none at all.
    The grant restoration then fails after the destroy, or silently grants some
    other existing role. Upper case is refused for that reason.
  - Surrounding whitespace is **part of the catalog name**. The guard used to
    trim it before validating, so ` padded_role ` was repaired into a different
    identifier and then approved. Nothing is trimmed now; a name carrying
    whitespace is refused.
  - A **key word** is not an identifier at all. `GRANT … TO select` is a syntax
    error and `GRANT … TO public` grants to every role in the cluster, and both
    match the character syntax of an identifier.

  A catalog record that is entirely whitespace is a **record**, not an empty
  result: it is counted as one role and refused here, rather than taken as "no
  runtime role holds table grants" and silently restoring nothing.
- **more than one** — the drill exits `2` and names the roles it found, hex
  encoded. Which one the template should name is a decision for an operator, not
  a guess for a script, and the drill refuses it rather than rehearsing a restore
  it cannot finish.
- **unreadable** — the query failed, or its output was not the transport
  described below. The drill exits `2` with a fixed message and **does not** take
  this as "no runtime role": a report that cannot be read says nothing about how
  many roles there are, and restoring no table grants on that basis is finding
  N-20 with an extra step.

##### How the role names reach the script (finding PR-20260907-R2-1)

A PostgreSQL role name is a `name`, and a quoted one may contain **anything but
NUL** — including a newline. Until 2026-09-08 the drill read the catalog through
a command substitution and then split the result on newlines, and both halves of
that lose information a role name may carry:

- `$( )` strips **trailing** newlines, so a catalog role `freedom_runtime\n`
  arrived as `freedom_runtime` — a different role, which the guard approved and
  the rendered grant then named;
- a **leading** newline arrived as an empty first line and was skipped, so
  `\nfreedom_runtime` also arrived as `freedom_runtime`; and
- a role named `\n` disappeared entirely and was read as a zero-row result, so
  the drill restored no table grants and reported success.

No pattern applied after the split can recover a record boundary that has already
been deleted, so the **transport** is what changed. The query emits

```text
ROLE <the role name's UTF-8 bytes, hex encoded>   (one line per record)
END <the number of records>                       (exactly one, last)
```

A record is therefore pure `[0-9a-f]` and can contain no separator at all; the
count is stated by the server rather than inferred from how many lines survived;
and a **missing terminator is detectable**, which is what stops a truncated or
failed report from being read as "no runtime role". The script decodes the hex
back to the exact catalog bytes and applies the supported-role contract above to
**those bytes**. The encoding is transport. It validates nothing and widens
nothing: a quoted name is still refused, it is simply refused for what it
actually is.

**One byte cannot survive the decode, and it is refused rather than lost
(finding PR-20260908-R3-2).** A Bash string cannot hold a NUL, so an encoded
`00` did not arrive as a byte the supported-name guard could refuse — it
disappeared, and the shorter name that remained arrived already looking
supported. The report

```text
ROLE 66726565646f6d5f72756e74696d655f7465737400
END 1
```

is `freedom_runtime_test` followed by NUL, and the drill accepted it as
`freedom_runtime_test`, dropped the schema and rendered a grant for a role the
catalog does not hold. A PostgreSQL `name` is NUL terminated and cannot contain
one, so such a record is **malformed transport**, not a role identity, and the
drill now refuses the report — exit `2`, before the destroy, with the fixed
reason *"a role record carried a NUL byte"*. The check inspects whole byte
pairs: a plain search for `00` in the record text would misclassify `4004`,
which is `@` followed by `\x04` and carries no NUL at all.

The multiple-role refusal prints the transported form rather than the names,
for the same reason: a catalog name is arbitrary bytes and may carry control
characters or terminal escapes.

**Where these two refusals happen, stated precisely (finding DS-R8-2).** Both
are in step 3b. That is **after** step 1's `pg_dump`, step 2's checksum, the
creation of the work directory and the read-only inventories of steps 3, 3a and
3b, and **before** `DRILL_STAGE="destroy_attempted"`, `DROP SCHEMA` and the
restore. So a dump, its
`.sha256`, `inventory-before.txt` and `grants-before.txt` **may already exist in
the work directory** when the drill exits `2` here. What has not happened is the
destructive part: **no schema is dropped and nothing is restored, the database is
in exactly the state it was in before the drill started, and no recovery is
required.** Earlier wording said these refusals occurred *"before touching
anything"* and that *"nothing is dumped"*; that was true only of the
non-disposable-name refusal at gate 0a, and it is withdrawn.

The artifacts left behind are diagnostic, not a recovery obligation. They can be
deleted, or kept and re-used — the dump is a valid backup of the pre-drill state
— once the ambiguous or malformed runtime role has been resolved.

**Until 2026-09-06 the multiple-role refusal was unreachable**: the query result
was passed through `tr -d '[:space:]'` before being tested for a record
separator, so two roles arrived as one concatenated identifier and the drill
proceeded into the destructive cycle. Record boundaries are now preserved until
the count is known.

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

**Recovery depends on how far the drill got (finding PR-20260907-R2-2).** Until
2026-09-08 the banner printed the same full `pg_restore` for every failure after
the destroy, because it read a single "the schema was dropped" flag that stayed
set through the grants and both verifications. A failure in any of those happens
**after the data restore has committed**, and repeating that restore fails on the
objects that are already there instead of reaching the grant repair the operator
actually needs.

The script now records the last step that **succeeded** and prints the resume
point for that stage. The stage is stated in the banner's first paragraph; this
table says what each one means and where its procedure starts.

| Stage | What is known about the data | Where the printed procedure starts |
|---|---|---|
| `destroy_attempted` | the destroy ran and **did not report success**, so what the schema now holds is **not known** — it may be exactly as it was, and its transaction may still be open | a **step 0a** that establishes whether that transaction has ended, then a **step 0b** that establishes the schema's actual state; no mutation before either |
| `destroyed` | the destroy **reported success** and the data restore never started, so the database is **empty** | checksums, then the full restore |
| `restore_attempted` | the restore ran and did not report success, so **whether it committed is not known** — nor whether it has finished at all | a **step 0a** that establishes whether its transaction has ended, then a **step 0b** that establishes which it was; then the full restore, a skip to the grants, or a stop where those reports cannot decide |
| `restored` | the data restore **committed**; no grants are restored | the schema grants |
| `schema_grants_applied` | the data and the schema grants are restored; the runtime role holds **no table grants** — the N-20 state | the runtime grants |
| `grants_applied` | everything was applied and a **verification did not pass** | the verifications, and a grant re-application if they show loss |

**`destroy_attempted` and `destroyed` are two different statements, and the
difference is finding PR-20260908-R3-1.** Until 2026-09-08 the script recorded
`destroyed` *before* it issued `DROP SCHEMA`, on the reasoning that a failure
inside the destroy leaves an unknown state. But the `destroyed` banner does not
describe an unknown state — it asserts that the schema was dropped, that the
database is **empty**, and it directs a full restore. A command that was refused,
that never ran, or whose result was lost establishes none of that, and the
schema may be completely intact. The script now records *responsibility* before
the command (`destroy_attempted`: this drill may have destroyed something) and
*knowledge* only after it succeeds (`destroyed`: the schema is dropped,
recreated and empty). **A failed or uncertain destroy is never described as a
proven empty database, and its procedure prescribes no change to the database at
all until step 0 has established the state.**

**And what step 0 can establish is narrower than the first version of it
claimed.** That version read `pg_class` and the base-table inventory, and treated
`relations=0` as "the database held no objects". It does not follow: a function
lives in `pg_proc`, a standalone type in `pg_type`, and the row inventory sees
neither. The report now counts each schema-scoped catalog class separately, every
outcome below is written to hold for counts over those classes and for nothing
wider, and the one state the counts genuinely cannot resolve — every class zero
now *and* zero in the baseline — **stops for an operator instead of being called
empty**. The same correction applies to `restore_attempted`, whose step 0 read
the row inventory alone.

**And a report is an observation, not an outcome (finding PR-20260908-R5-1).**
Both of those step 0s classified the state from what the reports counted *at the
moment they ran*, without first establishing that the transaction this drill
started had ended. PostgreSQL 16 documents both halves of why that is not safe:
with
[`client_connection_check_interval=0`](https://www.postgresql.org/docs/16/runtime-config-connection.html#GUC-CLIENT-CONNECTION-CHECK-INTERVAL),
which is the default, the server detects a lost connection at its next socket
interaction rather than necessarily stopping the query when the client
disappears; and under
[Read Committed](https://www.postgresql.org/docs/16/transaction-iso.html) a
`SELECT` sees what was committed before the query began, not another
transaction's uncommitted work. So a schema holding one function, a DROP whose
client died, and a backend still running it produce `routines=1` and an empty
inventory — both matching their baselines — the operator is told no restore is
required, and the transaction then commits and the function is gone. The
dependent decision has the mirror image: zero counts are also what an
**uncommitted restore that is still running** looks like, because
`--single-transaction` publishes nothing until it commits, so "it rolled back,
run it again" would start a second restore beside one still in flight.

Both stages therefore ask **whether the transaction has ended** before they read
anything, and **every outcome below them is provisional until an operator has
answered that**. The drill does not answer it and does not try to: the process
that would leave the evidence behind is the one whose death defines the failure,
and `pg_stat_activity` shows every user that a session exists without
necessarily showing them the fields that would identify its work or its open
transaction. [PostgreSQL 16 restricts columns rather than
rows](https://www.postgresql.org/docs/16/monitoring-stats.html#MONITORING-STATS-VIEWS):
the existence of a session and its general properties, such as its session user
and database, are visible to all users, while in rows about another role's
session many columns are null unless the reader is a superuser, holds
`pg_read_all_stats`, or is a member of the role that owns the session. So an
operator can see that a session is there and still be unable to tell whether it
is this drill's or whether its transaction has ended. What the procedure
does instead is name what an operator must establish, name what does **not**
establish it, and refuse to classify the outcome — or to skip, repeat or resume
anything — until they have. **No stage terminates or cancels a backend**, which
would convert an unknown outcome into a rollback somebody chose.

Two further things are worth stating plainly. **`restore_attempted` is the other
genuinely uncertain outcome, and it too is reported as uncertain rather than
guessed at**: `--single-transaction --exit-on-error` rolls the whole restore back
on an ordinary error, which leaves the database empty, but a process that was
killed is not an ordinary error and the script cannot see the difference from the
outside. Its step 0 is the pair of reports that settles it, or says that they
cannot. And **no stage's procedure
contains a `DROP`, a `--clean` or any other destructive reset**: reaching a clean
retry after a committed-but-wrong restore destroys what is there, and that is an
operator decision the script does not make.

**Every artifact the procedure needs** is written **before** the destroy and
named by the `RECOVERY REQUIRED` banner:

| Artifact | What it carries | Why the recovery fails without it |
|---|---|---|
| `freedom_dev.dump` (+ `.sha256`) | tables, data, constraints, triggers | there is nothing to restore |
| `schema-grants.sql` (+ `.sha256`) | schema **ownership** and the schema ACL | `--no-owner --no-privileges` leaves `public` owned by whoever ran the restore — typically `postgres` or the migration role — and strips its explicit ACL, so `pg_database_owner` ownership and the `PUBLIC` grant state can both differ from the pre-drill state |
| `runtime-grants.sql` (+ `.sha256`) | the **runtime role's table grants**, already rendered for the exact role the pre-drill database granted | `pg_restore --no-privileges` discards every `GRANT` in the archive, so without it the application role holds **no table grants at all**: every row is present and the application cannot use its tables. That is finding **N-20**, and until finding **PR-20260907-1** this file did not exist and the printed procedure did not restore those grants |
| `grants-inventory.sql` | the same privilege query step 6b runs | the recovery could not be *verified*, only performed |
| `grants-before.txt` | the privilege state as it was before the drill | there would be nothing to compare the recovered state against |
| `inventory-query.sql` | the same table/row query step 3 and step 6 run | the **data** half of the recovery could not be verified either, and at `restore_attempted` there would be no way to find out whether the restore committed |
| `inventory-before.txt` | the table and row inventory as it was before the drill | there would be nothing to compare the restored rows against |
| `schema-state.sql` | the structural report — whether `public` exists, and how many objects it holds in each schema-scoped catalog class: `relations`, `base_tables`, `routines`, `types`, `extensions` and `other_objects` | at `destroy_attempted` there would be no way to tell an intact schema from an empty recreated one, and a row-count comparison cannot do it: on a database with no base tables both produce the same empty inventory |
| `schema-state-before.txt` | that report as it was before the destroy | the report of the current state would have nothing to be read against, and the baseline is what decides whether the counts can answer at all. Neither file establishes that the transaction whose outcome is in question has finished — that is step 0a, and an operator's to answer |

**Follow the steps for the stage the banner names.** Substitute the work
directory the banner names; `/var/tmp/drill` is used here as an example.

**Step 0a, at stages `destroy_attempted` and `restore_attempted`. Has the
server-side transaction ended?** Ask this **before** running any report, and
before choosing anything at all. The command failed, but that is a statement
about the drill's client, not about the server: the backend may still be running
the `DROP SCHEMA` this drill issued, and until it ends, no report describes a
final state.

**Until an operator has established that the transaction has ended, every
outcome in step 0b is provisional.** None of them may be acted on — not the
conclusion that no restore is required, not running a restore, and not resuming
at any later step.

| | |
|---|---|
| **What does not establish it** | the drill's client exiting or failing (with `client_connection_check_interval=0`, the default, the server does not necessarily stop a statement when its client disappears); elapsed time; running the reports twice and getting the same answer; the exit status the drill ended with |
| **What would** | that no backend is still running this drill's statement or holding its transaction open against the database. `pg_stat_activity` is where a backend that is still there is visible — its rows for this database, with `pid`, `backend_start`, `xact_start`, `state` and `query` |
| **How that observation fails** | a `pid` is not an identity on its own, because pids are reused — match `backend_start` with it. And PostgreSQL restricts columns here, not rows: [the existence of a session and its general properties, such as its session user and database, are visible to all users](https://www.postgresql.org/docs/16/monitoring-stats.html#MONITORING-STATS-VIEWS), while in rows about a session belonging to a role you are not a member of many columns are null unless you are a superuser or hold `pg_read_all_stats`. So the row may be there while the fields that would tell you what that session is running, and whether it still holds a transaction open, are not: **a null field, or being unable to associate a visible session with this drill, is not proof that this transaction has ended** |
| **Which direction is stable** | a backend that has ended cannot come back, so that answer stays true once you have it. "Still running" does not, so re-read it rather than assuming it stayed that way |
| **What not to do** | **do not terminate or cancel a backend to settle this.** Neither the drill nor this guide does that: it turns an unknown outcome into a rollback somebody chose, at the one moment nobody knows what the transaction was doing |
| **If it cannot be established** | **the outcome is unresolved.** Stop, change nothing, and resolve it with an operator |

Run step 0b **after** 0a has answered. A report taken while the transaction was
still open describes the state before it, not the state it leaves, so if you ran
the reports earlier, run them again.

**Step 0b, at stage `destroy_attempted` only.** Establish what the schema
actually holds *before* deciding anything. Both reports are read-only:

```bash
psql --dbname=freedom_dev -tAX -v ON_ERROR_STOP=1 \
     -f /var/tmp/drill/schema-state.sql >/var/tmp/drill/schema-state-after-recovery.txt
diff -u /var/tmp/drill/schema-state-before.txt /var/tmp/drill/schema-state-after-recovery.txt
psql --dbname=freedom_dev -tAX -v ON_ERROR_STOP=1 \
     -f /var/tmp/drill/inventory-query.sql >/var/tmp/drill/inventory-after-recovery.txt
diff -u /var/tmp/drill/inventory-before.txt /var/tmp/drill/inventory-after-recovery.txt
```

**What these reports observe, and what they do not.** The state report counts
how many objects `public` holds in each of six classes — `relations` (`pg_class`:
tables, views, materialized views, indexes, sequences, foreign and partitioned
tables), `base_tables` (the subset the row inventory can count), `routines`
(`pg_proc`), `types` (standalone entries in `pg_type`), `extensions`
(`pg_extension`) and `other_objects` (`pg_collation`, `pg_conversion`,
`pg_operator`, `pg_opclass`, `pg_opfamily`, the four `pg_ts_*` catalogs and
`pg_statistic_ext`). It does **not** say *which* objects those are — equal counts
are not an object-identity inventory — and it is **not** an exhaustive
enumeration of everything PostgreSQL can place in a schema. Every row of the
table below is a statement about those counts and about nothing wider.

The identity inventory that does exist is the archive itself:
`pg_restore --list /var/tmp/drill/freedom_dev.dump` names every object it holds,
needs no database and changes nothing. It is what an operator reads where the
counts cannot decide.

| What the reports say | What it means | What to do |
|---|---|---|
| either command failed | the state is **still not known**. A query that did not run is not evidence that the schema is empty | resolve the client or server problem and repeat step 0. Restore, drop and truncate nothing on the strength of a query that did not answer |
| `schema_present=false` | the schema is **absent** | neither a restore nor a grant can run into a schema that does not exist, and recreating one is a deliberate change this procedure does not make. Stop and resolve it with an operator |
| some count is non-zero and the whole state report matches the baseline, with the inventory matching too | **the destroy did not take effect** — provided step 0a established that its transaction has ended. If it did not, this is also exactly what an unfinished destroy looks like from another session, and the state is **unresolved**. A dropped and recreated `public` holds nothing at all, so objects still counted there were never dropped | **no data restore is required**, and none may be run — it aborts on the objects already there. This establishes that the schema was not dropped and recreated; being counts, it does not certify the objects one by one. Fix whatever refused the destroy; running the drill again afterwards is an ordinary run, not a recovery |
| every count is zero and the baseline recorded at least one object in any class | everything the baseline counted is gone: the schema was **dropped and recreated** — the `destroyed` state, again provided step 0a established that the transaction has ended, without which this is a snapshot of a database something may still be changing | continue with the full procedure below, once 0a has answered |
| every count is zero **and the baseline recorded zero in every class** | **these reports cannot resolve this state.** An intact schema and a dropped-and-recreated one produce exactly this pair of reports, and neither report establishes that the schema held nothing before the drill — they count the classes named above and no others | **this is not "there was nothing to lose".** Do not restore, drop or truncate on the strength of these counts. Stop and resolve it with an operator, reading `pg_restore --list` for what the database held before the destroy and the catalogs for what it holds now. Step 0a does not rescue this one: even a transaction known to have ended leaves these two reports identical here |
| anything else | the schema is in an **unexpected** state | neither restoring over it nor resetting it is safe, and this guide does not choose between them. Stop and resolve it with an operator |

**Why the rule is keyed on objects rather than on two reports matching**
(finding PR-20260908-R3-1, continued). Until this correction the report counted
`pg_class` relations and base tables only, and read `relations=0` as "the
database held no objects". `pg_class` describes *relations*; a function is
described by `pg_proc` and the row inventory does not see it either. A schema
holding only a function therefore reported
`schema_present=true|relations=0|base_tables=0` both before and after a destroy
that removed it: the diffs matched, and the guide said the schema was intact,
that nothing could have been lost, and that no restore was required. The
function was gone and the procedure skipped the restore that would have
recovered it. **Equal counts are not an object-identity inventory, and zero
counts over named classes are not evidence that a schema held nothing.**

**Step 0a, at stages `destroy_attempted` and `restore_attempted`. Has the
server-side transaction ended?** Ask this **before** running any report, and
before choosing anything at all. The command failed, but that is a statement
about the drill's client, not about the server: the backend may still be running
the restore this drill issued, and until it ends, no report describes a final
state. A restore that is still running has published nothing —
`--single-transaction` keeps every object it has loaded invisible to other
sessions until it commits — so **an unfinished restore looks exactly like a
rolled-back one from another session**, and running the restore again on that
reading starts a second restore beside one still in flight.

**Until an operator has established that the transaction has ended, every
outcome in step 0b is provisional.** None of them may be acted on — neither
running the restore again nor skipping it.

| | |
|---|---|
| **What does not establish it** | the drill's client exiting or failing (with `client_connection_check_interval=0`, the default, the server does not necessarily stop a statement when its client disappears); elapsed time; running the reports twice and getting the same answer; the exit status the drill ended with |
| **What would** | that no backend is still running this drill's statement or holding its transaction open against the database. `pg_stat_activity` is where a backend that is still there is visible — its rows for this database, with `pid`, `backend_start`, `xact_start`, `state` and `query` |
| **How that observation fails** | a `pid` is not an identity on its own, because pids are reused — match `backend_start` with it. And PostgreSQL restricts columns here, not rows: [the existence of a session and its general properties, such as its session user and database, are visible to all users](https://www.postgresql.org/docs/16/monitoring-stats.html#MONITORING-STATS-VIEWS), while in rows about a session belonging to a role you are not a member of many columns are null unless you are a superuser or hold `pg_read_all_stats`. So the row may be there while the fields that would tell you what that session is running, and whether it still holds a transaction open, are not: **a null field, or being unable to associate a visible session with this drill, is not proof that this transaction has ended** |
| **Which direction is stable** | a backend that has ended cannot come back, so that answer stays true once you have it. "Still running" does not, so re-read it rather than assuming it stayed that way |
| **What not to do** | **do not terminate or cancel a backend to settle this.** Neither the drill nor this guide does that: it turns an unknown outcome into a rollback somebody chose, at the one moment nobody knows what the transaction was doing |
| **If it cannot be established** | **the outcome is unresolved.** Stop, change nothing, and resolve it with an operator |

Run step 0b **after** 0a has answered. A report taken while the transaction was
still open describes the state before it, not the state it leaves, so if you ran
the reports earlier, run them again.

**Step 0b, at stage `restore_attempted` only.** Establish whether the restore
committed *before* deciding to run it again. Both reports are read-only:

```bash
psql --dbname=freedom_dev -tAX -v ON_ERROR_STOP=1 \
     -f /var/tmp/drill/schema-state.sql >/var/tmp/drill/schema-state-after-recovery.txt
diff -u /var/tmp/drill/schema-state-before.txt /var/tmp/drill/schema-state-after-recovery.txt
psql --dbname=freedom_dev -tAX -v ON_ERROR_STOP=1 \
     -f /var/tmp/drill/inventory-query.sql >/var/tmp/drill/inventory-after-recovery.txt
diff -u /var/tmp/drill/inventory-before.txt /var/tmp/drill/inventory-after-recovery.txt
```

**The row inventory alone cannot answer this question**, and until this
correction it was the only thing this step read. It counts base tables, so on a
database whose archive holds none — one holding only functions, say — a
rolled-back restore and a committed one both leave it matching
`inventory-before.txt`. "No differences" was then read as "the restore
committed" and the operator was told to skip the restore: the same unsupported
inference as at `destroy_attempted`, one stage later. The state report is read
first, and it is still only counts.

| What the reports say | What it means | What to do |
|---|---|---|
| either command failed | whether the restore committed is **still not known** | resolve the client or server problem and repeat step 0. Do not run the restore again on the strength of a query that did not answer |
| the baseline records zero in every class | these reports **cannot** tell a rolled-back restore from a committed one here, because both leave every count at zero | stop and resolve it with an operator, reading `pg_restore --list` for what the archive holds and the catalogs for what is there now |
| every count is zero, and the baseline recorded objects | none of what the archive holds is in the schema: the transaction **rolled back** — provided step 0a established that its transaction has ended. If it did not, an unfinished restore produces this same pair of reports and the state is **unresolved** | continue with the full procedure below, once 0a has answered |
| both diffs print nothing, and the baseline recorded objects | everything these reports count is back in the numbers the archive holds: the restore **committed** — once step 0a has established that its transaction has ended, without which no count here is a settled one | **skip the `pg_restore` line** — running it again over the existing objects fails instead of repairing anything — and continue at the schema grants |
| anything else | the restore is **partial** | neither resuming nor repeating it is safe without a deliberate decision |

**Stages `destroy_attempted`, `destroyed` and `restore_attempted` — the full
procedure.** At `destroy_attempted` it is run **only** once that stage's step 0
has established that the schema was dropped and recreated; at
`restore_attempted`, only once its step 0 has established that the restore did
not commit. In both cases that means 0a **and** 0b: the reports alone do not
establish either conclusion while the transaction may still be open:

```bash
sha256sum --check /var/tmp/drill/freedom_dev.dump.sha256
sha256sum --check /var/tmp/drill/schema-grants.sql.sha256
sha256sum --check /var/tmp/drill/runtime-grants.sql.sha256
pg_restore --dbname=freedom_dev --no-owner --no-privileges \
           --single-transaction --exit-on-error /var/tmp/drill/freedom_dev.dump
psql --dbname=freedom_dev -v ON_ERROR_STOP=1 -f /var/tmp/drill/schema-grants.sql
psql --dbname=freedom_dev -v ON_ERROR_STOP=1 -f /var/tmp/drill/runtime-grants.sql
```

**Stage `restored`** starts at the schema-grants checksum: the two `sha256sum`
lines for the grant files, then the two `psql` lines. **Stage
`schema_grants_applied`** starts at the runtime-grants checksum and its `psql`
line. **Stage `grants_applied`** starts at the verifications below, and re-applies
the two grant files only if the privilege comparison shows loss.

**In none of those stages is the `pg_restore` line run again.** The data restore
committed; repeating it aborts on the objects that are already there, and this
guide no longer prints it for them.

**Then verify — both halves, before calling the recovery complete.** These are
the same comparisons steps 6 and 6b make, which is why the drill writes both
queries out rather than keeping them inside itself:

```bash
psql --dbname=freedom_dev -tAX -v ON_ERROR_STOP=1 \
     -f /var/tmp/drill/grants-inventory.sql >/var/tmp/drill/grants-after-recovery.txt
comm -23 <(sort /var/tmp/drill/grants-before.txt) \
         <(sort /var/tmp/drill/grants-after-recovery.txt)
psql --dbname=freedom_dev -tAX -v ON_ERROR_STOP=1 \
     -f /var/tmp/drill/inventory-query.sql >/var/tmp/drill/inventory-after-recovery.txt
diff -u /var/tmp/drill/inventory-before.txt /var/tmp/drill/inventory-after-recovery.txt
```

Recovery is complete only when that prints nothing — both of them. Every line the
first prints is a privilege that existed before the drill and does not exist now;
every line the second prints is a table or a row count that does not match what
was dumped. **A restore command's exit status is not a substitute for either**,
which is the whole of finding N-20 and half of PR-20260907-R2-2.

**If the data inventory still differs after a restore that reported success**,
the restore itself is in question. Do not run it again over the objects that are
there: it fails on them. Reaching a clean retry means deliberately resetting the
schema, which destroys what the restore did put back — an operator decision, and
not part of this procedure.

**If no runtime role held table grants**, the drill says so — in step 3d, in the
banner, and by writing no `runtime-grants.sql` at all. Its checksum and its
`psql` line do not apply at any stage, and the schema grants are still required.
This is the ordinary case for a database only its owner ever connects to.

If the dump is also unusable — which can only be true at stages
`destroy_attempted`, `destroyed` and `restore_attempted`, because at every later
stage the data is already restored, and at `destroy_attempted` only after step 0
has established that the schema really was dropped, 0a included — the database
is disposable scratch state, so rebuild it from migrations instead.
That recreates the **schema**, not the data the dump held, and not the grants:

```bash
APP_ENVIRONMENT=development DATABASE_URL=<url> ./venv/bin/alembic upgrade head
psql --dbname=freedom_dev -v ON_ERROR_STOP=1 -f /var/tmp/drill/schema-grants.sql
psql --dbname=freedom_dev -v ON_ERROR_STOP=1 -f /var/tmp/drill/runtime-grants.sql
```

Re-running the drill is **not** a recovery step: it would dump the database in
whatever state the failure left it in and then destroy that state to prove a
restore of it.

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
