# Operations — Foundry snapshot submission

Status: **Phase 2 I-03 working document, revised for the independent-review
remediation of 2026-08-04.** The procedures below are the deliverable. **No
rehearsal in §6 or §7 has been run**, and neither may be run without the
maintainer present. The maintainer-supervised checks in §8.1 and §8.2 have also
not been run, and the browser workflow is not verified from a real browser until
§8.2 is.

Related: [export contract](../rules/foundry-export-contract.md),
[ADR 0006](../adr/0006-foundry-integration-boundary.md),
[ADR 0009](../adr/0009-snapshot-submission-http-boundary.md),
[snapshot import](foundry-snapshot-import.md),
[topology](topology.md), [database development](database-development.md).

## 1. The supported workflow

```text
Authorized Foundry user opens the Actor Directory
  → presses "Submit Freedom Blades Snapshot"
  → selects one Actor folder, seeing its full path, stable ID and Actor count
  → enters the submit-only credential, which Foundry never stores (§4.1)
  → chooses Submit
  → the module builds and validates the whole bundle locally
  → the module computes SHA-256 over the exact UTF-8 bytes
  → the browser preflights the cross-origin POST; the server permits the
    configured Foundry origin and no other (§5.4)
  → the module POSTs those exact bytes over HTTPS
  → the server authenticates the submit-only service principal
  → the server independently validates size, checksum, canonical form and schema
  → the server stores the immutable artifact in restricted storage
  → the server records pending provenance and returns snapshot id, checksum, count
  → the module shows a bounded receipt with no Actor names or mechanics
  → a Guild Council member later previews it
  → a separate, explicit confirmation invokes the existing apply service
```

**No SSH. No server filesystem path. No manual file placement.**

Three things this is not:

- **`Export to Compendium` is not snapshot submission.** It writes a Foundry
  document. This module writes nothing to Foundry at all.
- **The `Actors (shared)` compendium is not the source.** It is a copy that may
  be stale. The module reads the live world through `game.actors`.
- **Browser download is a fallback, not the workflow.** It produces the same
  validated, checksummed bytes for the case where the endpoint is unreachable,
  and it exists for diagnosis. The normal path is direct submission.

Neither component reads Foundry LevelDB, world storage or a compendium file, in
this phase or any other.

## 2. Who may do what

Four authorities, and keeping them apart is the point.

| Authority | May | May not |
|---|---|---|
| Foundry GM | read and submit the selected folder | anything on the platform |
| the submit-only service principal | upload one snapshot | apply, read Council data, read audit history, mutate a character, reach PostgreSQL |
| a Guild Council member | preview a pending snapshot; separately, apply it | change a Foundry Actor |
| a Platform Administrator | operate the service, rotate credentials, manage retention | apply an import, unless they also hold Guild Council |

**A Foundry GM role is not proof of Discord Guild Council membership.** The
module says so in its dialog and this document says so here. A submission
creates a *pending* artifact and applies nothing.

A submission never applies anything. Apply remains a distinct action by a
currently authorized Council member, and the existing service re-checks the
snapshot checksum, world, folder id and path, profile version and every affected
aggregate version at the moment it commits.

## 3. Installing the module

1. Copy `foundry-module/` into the Foundry data path as
   `Data/modules/freedom-blades-export/`. There is no build step, no npm
   install and no bundler.
2. Enable it in the world's *Manage Modules*.
3. Configure it as in §4. The module is inert until an endpoint is set: without
   one, only the download fallback works. The credential is **not** configured —
   see §4.1.

Supported deployment: Foundry `14.365`, `dnd5e` `5.3.3`, world `the-guild`. The
module reads the tuple it is actually running and refuses to export if it does
not match the configured one. A Foundry or system upgrade therefore **stops
submission until the configured tuple is updated on both sides** — that visible
checkpoint is the feature (OD-14, ADR 0006).

**Rollback:** disable the module in *Manage Modules*, or delete its directory.
Neither affects any Foundry document, because the module never wrote one.
Snapshots already submitted are unaffected and remain pending.

## 4. Configuring the module

The four settings are world-scoped and are not rendered in the settings sheet.
Foundry enforces write permission on the server: a world setting requires
`SETTINGS_MODIFY`, which ordinary players do not hold. **None of them is a
secret** — see §4.1. Set them from a GM browser console:

```js
const M = "freedom-blades-export";
await game.settings.set(M, "submissionEndpoint", "https://<host>/api/v1/foundry/snapshots");
await game.settings.set(M, "supportedWorldId", "the-guild");
await game.settings.set(M, "supportedCoreVersion", "14.365");
await game.settings.set(M, "supportedSystemVersion", "5.3.3");
```

The endpoint must be HTTPS. Plain HTTP is refused before a request is made, with
one exception for `http://127.0.0.1` and `http://localhost` so a same-host
rehearsal is possible; that exception cannot reach the network.

### 4.1 The credential is not configuration

**There is no credential setting.** Security review S-B-1 found that storing the
reusable bearer as a world setting placed it outside any confidentiality
boundary, and the Foundry 14.365 application source establishes exactly why:

| Question | Answer | Source |
|---|---|---|
| Who may create or update a Setting? | a user holding `SETTINGS_MODIFY`; enforced on the server | `common/documents/setting.mjs` |
| Which clients receive a world-scoped Setting's **value**? | **every connecting client, whatever its role** | `dist/packages/world.mjs` builds each user's world payload with `db.Setting.dump()` |
| Does that dump filter by user or permission? | **no** — it takes a sort option and nothing else | `dist/database/backend/server-document.mjs` |
| Is there a setting option giving read confidentiality? | **no.** `client` scope is browser `localStorage`; `world` and `user` scope are both Setting documents vended by the same unfiltered dump | `common/constants.mjs`, `client/helpers/client-settings.mjs` |

`config: false` keeps a value out of the settings *form*. It is not a
confidentiality control, and hiding the submission button from non-GMs is
client-side UI gating that a connected user or a browser extension does not have
to respect.

**So the submitting GM enters the credential in the dialog, once per
submission.** The field is `type="password"` with `autocomplete="off"`; the
value lives in one local variable for the duration of one upload and is written
to no setting, no `localStorage`, no flag, no document, no notification, no log
and no receipt. `foundry-module/tests/settings.test.mjs` fails if that changes.

| Property | Value |
|---|---|
| Where the secret lives at rest | the operator's password manager, and the server's configuration as a **SHA-256 digest** |
| Who can retrieve it | the person who holds it. No Foundry user, module or client can read it out of world state, because it is not there |
| Lifetime in the browser | one submission. Cleared when `run()` returns |
| If a GM device or browser is compromised | treat the credential as exposed and rotate it (§5.3). Its authority is submit-only: an attacker can create unwanted **pending** artifacts and consume storage, and cannot apply anything, read Council data, mutate a character or reach PostgreSQL |
| If it is absent | the submission fails closed with `missing_credential` before any request is made. The download fallback still works and needs no credential |

**Any credential that was ever placed in a world setting must be treated as
exposed and rotated**, whether or not a non-GM was connected: it was delivered
to every client that joined the world while it was set. No credential has been
issued for this package (§5.2 has never been run outside a synthetic test), so
there is nothing outstanding to rotate today; this rule applies from the first
one issued.

Never put a real credential in a ticket, a chat message, a screenshot, a commit,
a log or this document.

## 5. Configuring the server

### 5.1 Environment

```bash
# Absolute directory, outside the repository, for the restricted artifact store.
# Required: there is no default, because every default would be a guess about
# which filesystem holds every exported Actor's mechanics. It must be a real
# path with no symlinked component, owned by the service account, granting
# nothing to group or other. See §5.6 — the service refuses to start otherwise.
FREEDOM_SNAPSHOT_ARTIFACT_ROOT=/srv/freedom/snapshots

# One entry per principal, ';'-separated:
#   <id>|<scope>[,<scope>]|<sha256 of the secret, hex>
# Configuration holds the DIGEST of the secret, never the secret.
FREEDOM_SNAPSHOT_PRINCIPALS='foundry-the-guild|foundry:snapshot:submit|<sha256 hex>'

# The browser origins permitted to submit, comma- or whitespace-separated. Exact
# origins only: no wildcard, no suffix match, no reflection of whatever arrived.
# Required for the supported browser workflow -- see §5.4.
FREEDOM_SNAPSHOT_ALLOWED_ORIGINS='https://foundry1.example.org,https://foundry2.example.org'
```

An absent or empty `FREEDOM_SNAPSHOT_PRINCIPALS` is a valid configuration: every
request then fails authentication, which is also how "revoke everything" is
spelled.

An absent or empty `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` is also valid and is the
default: **no browser origin may submit**, and every preflight is refused. A
non-browser caller — the §5.8 smoke test, the loopback rehearsal — sends no
`Origin` and is unaffected by it either way.

### 5.2 Issuing a credential

```bash
# Generate the secret. This value goes to the submitting GM's password manager
# and nowhere else — not into a Foundry setting, not into server configuration,
# not into a ticket, not into a log.
SECRET=$(./venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))')

# The digest is what the server configuration holds.
./venv/bin/python -c \
  'import sys; from adapters.http.credentials import secret_digest; print(secret_digest(sys.argv[1]))' \
  "$SECRET"
```

The presented credential is `<principal id>.<secret>`. A secret shorter than 32
characters is refused both at issue and at presentation.

**A credential is not enough on its own — it also needs an admission
generation.** Configuration decides which credentials authenticate; the
`submission_admissions` table decides which of them may still turn a submission
into a durable acceptance. A credential with no generation authenticates and is
then refused `403 admission_closed`, which is the correct state for a deployment
that has run migration 0005 and not yet opened one:

```bash
APP_ENVIRONMENT=production \
DATABASE_URL='postgresql+psycopg://__OWNER_ROLE__@/freedom_production' \
./venv/bin/python -m tools.submission_admission open \
  --principal foundry-the-guild \
  --operator 'A. Operator' \
  --reason 'Initial generation for the Phase 2 submission endpoint.'

# Confirm, and keep the output with the deployment record.
APP_ENVIRONMENT=production \
DATABASE_URL='postgresql+psycopg://__OWNER_ROLE__@/freedom_production' \
./venv/bin/python -m tools.submission_admission show
```

<a id="admission-tool-prerequisites"></a>

**Both halves of that environment are prerequisites, not decoration.**

- **`APP_ENVIRONMENT` selects which database name is permitted**, and it
  **defaults to `development`** exactly as it does for Alembic
  ([database-development.md](database-development.md)). A command that omits it
  can only ever reach `freedom_dev`; one that names `production` may only reach
  `freedom_production`. `DatabaseSettings` refuses any other pairing *before*
  connecting, so a mismatch costs a refusal (exit code 2) rather than a wrong
  database. Substitute the environment being operated: `freedom_staging` under
  `APP_ENVIRONMENT=staging`, `freedom_dev` under `development`.
- **`__OWNER_ROLE__` is the role that owns `submission_admissions`** — the
  migration/schema owner — and **not** the environment's restricted runtime login
  role (`freedom_production_app` and its siblings). That role holds `SELECT` on
  this table and nothing else, which is the control that keeps the fence
  enforced rather than advisory, so it cannot open or close a generation and the
  attempt is refused with exit code 4. Substitute the real role through the
  deployment's secret-safe templating, the way
  `infra/postgresql/runtime-grants.sql.tmpl` substitutes `__APP_ROLE__`. **Do not
  write a real role name, password or connection string into this file, a ticket
  or a log.** A socket URL with no password relies on peer or `scram` local
  authentication for that role; that is a deployment prerequisite, not something
  this command arranges.
- **The connection must be local.** The tool applies the `SOCKET_OR_LOOPBACK`
  policy, so a named remote host is refused. Use the Unix-domain socket form
  above.

**Exit codes.** Each failure is distinct. Codes 1 to 6 are reached with the
transaction rolled back, so each says that nothing was opened or closed. **Code 7
says the opposite: that nobody knows**, and the difference matters more than any
other line in this table.

| Code | Meaning | What the operator does |
|---|---|---|
| 0 | Succeeded | Record what came back |
| 1 | Refused before the database was touched | Fix the argument named in the message |
| 2 | Connection target refused by validation | Fix `APP_ENVIRONMENT`/`DATABASE_URL` |
| 3 | Database unreachable; nothing read or written | Check PostgreSQL and the socket |
| 4 | Insufficient privilege | Re-run as the schema owner, not the runtime role |
| 5 | `lock_timeout` | **Unsettled** — safe to retry; see §9 step 3 |
| 6 | Other database failure; the transaction did not commit | Escalate with the SQLSTATE |
| 7 | **Outcome unknown** — the connection was lost after the transaction began | **Unsettled.** Verify with `show` before anything else; see §5.2.1 |

#### 5.2.1 Exit code 7 — the outcome is unknown, and that is the answer

A connection can be lost while PostgreSQL is processing or acknowledging
`COMMIT`. The server may have committed the transition while this command heard
nothing back, and **no observation the client can make distinguishes those two
outcomes** — the same reasoning the fence itself rests on, met at the operator's
terminal instead of at the acceptance boundary. So the tool refuses to guess. It
does not say the generation was closed, and it does not say the fence is
unchanged.

Treat the episode as **Unsettled** and do this, in this order:

1. **Reconnect and run `show`.** It is a read, it settles nothing, and it is the
   only thing that answers the question.
2. **Confirm the transition against its append-only event.** Each transition
   writes one, and the admission row's correlation columns name it:

   ```sql
   SELECT admission.generation, admission.state, event.action, event.payload
     FROM submission_admissions AS admission
     JOIN audit_events AS event
       ON event.correlation_id = admission.closed_correlation_id
    WHERE admission.principal_id = 'foundry-the-guild';
   ```

   A closure that committed has both the `closed` state and one
   `snapshot_submission.admission_closed` row. One without the other is a
   finding to escalate, not something to work around.
3. **Then act on what you found.**

   | Command | `show` says | Do |
   |---|---|---|
   | `close` | closed | Nothing. The settlement happened; continue §9 from step 3's Hit/Miss decision |
   | `close` | still open | Run the same `close` again. It is idempotent, and a second close of a closed generation writes no second event |
   | `open` | the generation exists | Nothing. Use it; do **not** open another |
   | `open` | no generation for that principal | Run the same `open` again |

**Never authorize a fresh export on an unverified exit 7**, and never open a
second generation for a credential without checking first: a principal id holds
at most one admission for all time, so a blind retry of `open` is refused
permanently and spends nothing but time — while a blind assumption that a
`close` did not happen is what leads to two accepted artifacts for one episode.

**A principal id may hold at most one generation, ever.** That is enforced by a
unique constraint and it is the control that makes recovery sound: once a
generation is closed it can never be reopened, and the credential it belonged to
can never be admitted again. So a principal id is spent when its generation is
closed, and every reissue takes a new one. `foundry-the-guild`,
`foundry-the-guild-r1`, `foundry-the-guild-r2` is the convention. See §9 step 4.

### 5.3 Rotation and revocation

Both are a configuration change plus a service reload. No redeployment, no
migration and no database change.

| Action | Steps |
|---|---|
| **Rotate** | issue a new secret; add a second entry with a new principal id; reload; give the new credential to the submitting GM for their password manager; confirm a submission; remove the old entry; reload |
| **Revoke one** | remove that entry; reload |
| **Revoke everything** | set `FREEDOM_SNAPSHOT_PRINCIPALS=`; reload |

Rotation no longer touches Foundry at all: there is no setting to update
(§4.1), so the change is server configuration plus telling the holder. That is
also what makes revocation complete — the old secret exists in one person's
password manager and in no world's state, so removing the entry removes every
way to use it.

**Rotate whenever** the secret may have been seen: a GM device or browser
compromise, a screen share, a support session, an accidental paste into a chat
or a ticket, or a departure of the person holding it. Rotation is cheap by
design; treating it as routine is the intended posture.

Revocation takes effect for the running process at the reload, and the endpoint
answers `401` from that moment. Snapshots already submitted are unaffected: they
are immutable records, and revoking the credential that delivered one does not
retract it.

**Rotation opens a new generation; revocation should close the old one.** The
table above is about *authentication*, and it reaches only requests that have not
been authenticated yet. A request that authenticated before the reload and is
paused somewhere — in the browser's socket, inside Caddy, between two of its own
statements — is past that check and will still commit when it wakes. Closing its
admission generation is what reaches it:

| Action | Additionally |
|---|---|
| **Rotate** | `tools.submission_admission close` the old generation, then `open` one for the new principal id |
| **Revoke one** | `close` its generation. The credential is then refused twice over, and the second refusal reaches work already accepted |
| **Revoke everything** | `close` every open generation, then clear `FREEDOM_SNAPSHOT_PRINCIPALS` and reload |

Closing is the decisive half and it is cheap. Do it first: a closed generation
refuses a stranded request wherever it was paused, and a configuration reload
does not.

### 5.4 Proxy, body, time limits and browser origins — these must match

The application refuses a declared `Content-Length` above **64 MiB**, matching
the export contract. Every hop in front of it must allow at least that, or a
legitimate submission is cut off before the application can explain why.

Caddy already terminates TLS for this host (ADR 0002, [topology](topology.md)):

```caddyfile
handle /api/v1/foundry/snapshots {
    request_body {
        max_size 64MiB
    }
    reverse_proxy 127.0.0.1:8757 {
        transport http {
            read_timeout 180s
            write_timeout 60s
        }
    }
}
```

The module's own upload timeout is 120 s. Keep the proxy read timeout above it
so the client, not the proxy, is what gives up first — a proxy timeout produces
no receipt and no explanation.

**The ingress no longer has to be terminable, and §9 no longer depends on it.**
Nine versions of §9 settled a lost-pin episode by stopping the endpoint and
terminating the proxy in front of it, which required the path from a browser to
this application to be one proxy, on this host, under a supervisor the operator
could stop. §9 now settles an episode by **closing the submitting credential's
admission generation** — a transaction, not an outage — so a hop that cannot be
stopped from here is no longer a reason to revisit it. Keep the single-proxy
topology above regardless: it is what the rest of this document assumes and it
costs nothing. It is simply not load-bearing for recovery any more.

**No upstream retry window.** The block above sets none, and it must keep setting
none: `lb_try_duration`, or any hop that queues or retries a *refused dial*, turns
one submission into several deliveries, which is a real failure mode and a
confusing one to diagnose. It was never what made a miss safe — it governs a
retry after a *refused* attempt, and the request that defeated two earlier
versions of §9 had made no attempt at all — and it is not what makes one safe
now. A delivery that arrives after settlement is refused by the fence, whether it
is a retry, a first dial, or something a hop invented.

**Metrics are not required by anything in this document.** Caddy's
`caddy_http_requests_in_flight` gauge looks like evidence that the proxy is
holding nothing, and it is not: Caddy documents it as the requests *currently
being handled* ([metrics](https://caddyserver.com/docs/metrics)), which excludes
a connection it has accepted whose request has not entered the handler, and body
bytes still arriving on an established connection. An early version of §9 read it
and no longer does. Do not reintroduce it as settlement evidence — and note that
the same objection applies to every reading of that kind, which is why §9 reads
none of them.

If metrics are enabled for monitoring, use the current global option. The nested
`servers { metrics }` form still adapts on the installed Caddy 2.10.2, but
`caddy adapt` warns that it is removed in the next major version:

```caddyfile
{
    metrics
}
```

See [global options](https://caddyserver.com/docs/caddyfile/options#metrics).
Whatever is enabled, the admin API it is served from listens on loopback only by
default. Keep it that way: it is an administrative interface.

**Caddy must not add CORS headers of its own, and must pass `OPTIONS` through.**
The block above already does both — it proxies every method and injects no
header — and that is the required state, not an incidental one. The application
owns this policy, because it is the only component that knows which route,
method and header set are permitted. Two sources of `Access-Control-Allow-Origin`
on one response is a duplicated header, which browsers reject outright.

#### The browser preflight

The module submits with `Authorization`, `Content-Type: application/json`,
`Idempotency-Key` and `X-Snapshot-SHA256`. None is CORS-safelisted, so unless
Foundry and this application are served from **one origin** the browser first
sends an unauthenticated `OPTIONS` to this route and will not send the POST at
all unless it is answered. Review finding B-1 was that it was not.

`FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` names the exact Foundry origins that may do
this. Use the origin a browser actually sends — scheme and host, lower-case, with
the port only when it is not the scheme's default:

```bash
# Right: what the browser sends.
FREEDOM_SNAPSHOT_ALLOWED_ORIGINS='https://foundry1.example.org'

# Refused at startup, each with a message saying why:
#   'https://foundry1.example.org/'      -- a path; normalised, but write it without
#   '*'                                  -- a wildcard is not an allowlist
#   'null'                               -- an opaque origin must never be listable
#   'http://foundry1.example.org'        -- clear text, except for a loopback host
#   'https://user:pw@foundry1.example.org' -- userinfo is not part of an origin
```

What the endpoint then does:

| Request | Answer |
|---|---|
| `OPTIONS` from a listed origin, asking for `POST` and a subset of the four headers | `204`, with `Access-Control-Allow-Origin`, `-Allow-Methods: POST`, `-Allow-Headers` and `-Max-Age` |
| `OPTIONS` from an unlisted, malformed or `null` origin | `403 origin_not_allowed`, **no** permission header |
| `OPTIONS` asking for another method | `403 preflight_method_not_allowed` |
| `OPTIONS` asking for a fifth header | `403 preflight_header_not_allowed` |
| `POST` from a listed origin | processed; every response, including `401`, `400` and `500`, carries the permission so the browser can read it |
| `POST` from an unlisted origin | processed, with no permission header — the *browser* refuses it on the caller's machine. The access control on this endpoint is the bearer credential, not the origin |
| any request with no `Origin` | untouched. `curl`, the §5.8 smoke test and the loopback rehearsal are unaffected |

`Access-Control-Allow-Credentials` is never sent and no cookie authority is
added: the module sends `credentials: "omit"`, and a bearer-only endpoint is not
reachable by a page merely because a browser has a session somewhere.

**Symptom to recognise.** A browser-side submission that fails with
`network_failure` while `curl` from the same host succeeds is almost always this
origin not being on the allowlist. The browser reports it as an opaque network
error by design; the server log shows the `403 origin_not_allowed` preflight.

**Not yet verified from a real browser.** Every case above is covered by
automated tests that reproduce the preflight, and none of them is a browser.
`curl` cannot prove browser CORS. The real-origin check is §8's last item and
needs the maintainer present.

### 5.5 Running it

**There is no production server process in this package.** Phase 3 delivers
`freedom-web`; ADR 0009 records why. For a supervised rehearsal:

```bash
FREEDOM_SNAPSHOT_ARTIFACT_ROOT=/srv/freedom/snapshots \
FREEDOM_SNAPSHOT_PRINCIPALS='foundry-the-guild|foundry:snapshot:submit|<sha256>' \
FREEDOM_SNAPSHOT_ALLOWED_ORIGINS='https://foundry1.example.org' \
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/python -m tools.snapshot_api --port 8757
```

The launcher defaults to the controlled `the-guild` deployment pin. To rehearse
against a deliberately selected scratch world, add the complete rehearsal-only
tuple to the command above; a partial tuple refuses startup:

```bash
FREEDOM_SNAPSHOT_REHEARSAL_WORLD_ID='test' \
FREEDOM_SNAPSHOT_REHEARSAL_CORE_VERSION='14.365' \
FREEDOM_SNAPSHOT_REHEARSAL_SYSTEM_ID='dnd5e' \
FREEDOM_SNAPSHOT_REHEARSAL_SYSTEM_VERSION='5.3.3'
```

Use these variables only with this loopback rehearsal launcher and a disposable
database. They do not alter the production composition default, and the
launcher enforces that scope rather than trusting it: a complete, well-formed
tuple is **refused unless `APP_ENVIRONMENT=test`**, which in turn requires
`DATABASE_URL` to name the disposable `freedom_test` database. An unset
`APP_ENVIRONMENT` is refused for the same reason. Startup prints the effective
accepted tuple; compare it with the module dialog before submitting. Omitting
all four restores the controlled deployment pin, unconditionally and in every
environment.

It binds loopback only and refuses anything else. It prints the configured
principal *ids*, the artifact root, the permitted browser origins and the port —
never a secret, a digest or a database URL.

`FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` is needed only when the rehearsal is driven
from a **browser**. Omit it for the `curl` smoke test.

**It refuses to start** when the artifact root is not usable as restricted
storage — wrong owner, group- or other-readable, not a directory, reached
through a symlink, or on a filesystem that cannot `fsync` a directory. The
message names a fixed reason and never the path. §5.6 says what each requires.

The preview route is **disabled**: it needs the Phase 3 Discord-authenticated
boundary, which does not exist, so it answers `503
authentication_unavailable` rather than being served by something invented for
the purpose. **This is a blocker to production exposure of the preview route**,
and it is not a blocker to the submission endpoint.

### 5.6 Artifact storage, access and retention

| Record | Lifetime | Who may read it |
|---|---|---|
| checksum, provenance, counts, audit events | **permanent**, append-only | Guild Council and Platform Administrators |
| the raw artifact bytes | retained only while an operational need exists | Platform Administrators, on the host |

The store is created `0700` and each artifact `0600`, named for its own SHA-256,
never for anything a caller supplied. **No application route serves an artifact,
and there is no directory listing.** Audit visibility does not by itself grant
permission to download the document.

#### The required directory state, and what happens when it is wrong

Security review S-B-2 found, first, that the previous implementation set the mode
of a root it created and checked nothing about one that already existed, and
accepted an existing checksum-named target on content alone. The re-review found
that fixing the *checks* was not enough, because every one of them was made **by
pathname**: the root was `lstat`ed, and then the temporary file, the artifact
reads, the publication and the directory `fsync` each named that path again.
Anyone able to rename entries in a writable parent could substitute a different
directory in between, and each operation would follow the name to it.

**The root is now a file descriptor, not a path.** It is opened once with
`O_DIRECTORY | O_NOFOLLOW`, its type, owner and mode are proved through that
descriptor, and every later operation resolves its name *relative to it*. A
replacement of `/srv/freedom/snapshots` after the service starts therefore
redirects nothing: creation, publication, reads and the directory `fsync` all
continue to act on the directory that was approved.

The service also notices. Each store and each read compares the configured
pathname with the anchored directory and refuses `root_replaced` if they are no
longer the same directory — so a deliberate move is reported rather than
silently ignored. **Moving or replacing the artifact root requires restarting
the service**; that is the supported procedure, and the refusal is what tells
you it is needed.

The descriptor is held for the life of the service and released by
`Composition.dispose()` at shutdown. One descriptor, whatever the request rate;
nothing here is per-request, and a refused startup releases it before the process
exits.

#### Publication never overwrites an entry the service has not validated

The third security review found the remaining half of the same problem. Anchoring
fixed *which directory* the final entry was created in; it said nothing about
*how*. The implementation checked whether the checksum name was already this
artifact, then wrote a temporary file, then called `rename(2)` over the checksum
name. A rename replaces. Anything that appeared under that name in between — a
concurrent submission, a restored backup, an operator's copy, an intruder's file
— was removed and overwritten without anyone having looked at it.

**Publication is now `link(2)`, which creates the entry or fails `EEXIST`.**
There is no mode in which it removes what is already there, and the test and the
creation are one kernel operation, so there is no window between them.

| Situation | What happens |
|---|---|
| the checksum name is free | the link succeeds. Exactly one writer can win; the kernel serialises it |
| **another writer won** | `EEXIST`. The entry is re-opened through the anchored descriptor and re-proved completely — regular file, service-owned, no group/other permission, bytes hashing to the name. If it passes, **their** file is the artifact and this submission reuses it. Two submissions of identical bytes converge on one file |
| the entry is unsafe or mismatched | the submission is refused and the entry is left **byte for byte and mode for mode as it was found**. `checksum_mismatch`, `artifact_untrusted`, `artifact_permissive`, `artifact_not_owned`, `artifact_not_a_regular_file` all mean this. See §9 |

**Durability ordering.** Publication briefly leaves the bytes under two names —
the checksum name and the temporary. Removing the temporary is the *last*
directory-entry change publication makes, so it happens **before** the directory
`fsync`, and one sync makes the creation and the removal durable together.

**The removal is best effort, and this document does not claim it always
happens.** It can only ever name a `.incoming-*` file, so a cleanup failure can
never delete a published artifact and never invalidates one — a submission whose
cleanup fails still returns a receipt, and the artifact under the checksum name
is complete and correct. What it can do is leave a second, private hard link to
those same bytes in the root. Nothing serves it: the only name any route
resolves is the checksum one. It is `0600`, owned by the service account, inside
a `0700` root. But it consumes an inode and, once the checksum entry is deleted
under the retention rule below, a full copy of the bytes — so it is an operator
hygiene item, not a non-event. "Temporary files left by a failed cleanup" below
is how to find one.

**Filesystem requirement: hard links.** ext4, XFS, Btrfs, ZFS and tmpfs all
support them. FAT/exFAT and some network mounts do not, and neither can give this
store its guarantee. Startup proves it rather than assuming it — it links a probe
file, links it a second time, and requires the second attempt to fail — and
refuses `link_unsupported` if either fact does not hold. If you see that refusal,
the artifact root is on a filesystem this service cannot use; move it, do not
work around it.

`renameat2(RENAME_NOREPLACE)` would give the same guarantee in one syscall, but
Python exposes no wrapper for it, and a hand-rolled `ctypes` syscall stub in the
path that stores every exported Actor's mechanics is a worse trade than one extra
`unlink`. That is a recorded decision, not an oversight.

| Subject | Required | Refusal if not | When |
|---|---|---|---|
| the configured path | no symbolic-link component | startup: `is unusable: … symbolic link` | startup |
| every directory above the root | a directory owned by `root` or the service account, not writable by others unless sticky | `root_ancestor_untrusted` | startup |
| the platform | `O_NOFOLLOW`, `O_DIRECTORY` and descriptor-relative operations | `nofollow_unsupported`, `dir_fd_unsupported` | startup |
| the root's filesystem | hard links, and a link that refuses an existing name | `link_unsupported` | startup |
| the root | a directory, not a symlink | `root_not_a_directory`, `root_untrusted` | startup, every store, every read |
| the root | owned by the service account | `root_not_owned` | startup, every store, every read |
| the root | no permission granted to group or other | `root_permissive` | startup, every store, every read |
| the root | still the directory the configured path names | `root_replaced` | every store, every read |
| the root | reachable at all | `root_unavailable` | startup, every store |
| the root's filesystem | supports `fsync` on a directory | `durability_unconfirmed` | startup, every store |
| an artifact being written, read or reused | a regular file, not a symlink | `artifact_untrusted`, `artifact_not_a_regular_file` | every store, every read |
| an artifact | owned by the service account | `artifact_not_owned` | every store, every read |
| an artifact | no permission granted to group or other | `artifact_permissive` | every store, every read |
| an artifact | its bytes hash to its own name | `checksum_mismatch` | every store, every read |
| publication | settles, rather than repeatedly finding an entry that then vanishes | `publication_unsettled` | every store |

Every `artifact_*` and `checksum_mismatch` refusal above leaves the entry it
refused exactly where it was. The refusal message says so — "it has been left
exactly as it was found, so that it can be examined" — which is the wording to
look for when deciding whether an incident left something on the filesystem.

`publication_unsettled` is not reachable by any state this service can produce:
nothing here removes an artifact, so an entry cannot both exist and disappear
three times in one publication. It exists so that a filesystem that behaves that
way anyway produces a refusal rather than a request that never returns.

Three of these are deliberate decisions rather than omissions, and all three are
worth knowing about:

- **the ancestor walk happens only at startup.** A directory descriptor cannot
  observe what is above it, and re-walking the pathname on every request would
  add exactly the check-then-use window the anchoring removes. The walk
  establishes that the replacement could not have been staged in the first
  place; the descriptor makes it harmless if it is;
- **reads re-check the root as well as writes.** A store whose root has become
  readable by another account is no longer restricted storage, so a preview will
  refuse rather than keep serving every exported Actor's mechanics out of it
  while nobody has noticed;
- **an entry another writer published is reused, not replaced.** Content
  addressing is what makes that safe: their file and this submission's bytes hash
  to the same name, and the file is re-proved before it is accepted.

#### How the ancestor rule is tested, and what that costs

The rule above is the only one here whose answer depends on directories the
deployment does not own. The automated suite therefore runs it in two ways, and
the distinction matters if you are reading the evidence:

- **bounded**, for tests about publication, durability, anchoring and descriptor
  lifetime. The same rule, the same `os.lstat` calls, walking only the
  directories the test itself created; the host's `/` and temporary directory are
  out of scope. Without this, a host whose `/tmp` is owned by a third account
  fails those tests at the ancestor gate before they reach their own assertions
  — which is exactly what happened on the second review host, to thirty-two of
  them;
- **unbounded**, exercising the production walk against the real configured path,
  all the way to `/`. `test_the_production_walk_checks_the_real_configured_path`
  and `test_the_production_composition_walks_to_the_filesystem_root` do this, and
  the trusted, untrusted, sticky, writable, wrong-owner, symlinked, non-directory
  and absent cases are each tested directly against real directories.

The bound is a **test seam only**: there is no environment variable for it, and
`build_application` composed from configuration alone always walks to `/`. That
is asserted, not merely intended.

**A genuine environmental prerequisite remains, and it cannot be isolated away:**
the ancestor rule is a statement about the host, so the *deployment* must satisfy
it. `/srv` and `/srv/freedom` must be owned by `root` or by the service account.
A host whose `/` or `/tmp` is owned by a third account will refuse to start, and
that is the intended behaviour, not a test-environment problem.

**Nothing is repaired automatically.** The service does not `chmod` or `chown` a
path an operator configured — widening or narrowing it is an authority it was
never granted — so an unsafe state is a refusal and the operator fixes it:

```bash
sudo chown "$(id -un freedom):$(id -gn freedom)" /srv/freedom/snapshots
sudo chmod 0700 /srv/freedom/snapshots
sudo find /srv/freedom/snapshots -maxdepth 1 -type f -name '*.json' \
  -exec chmod 0600 {} +

# root_ancestor_untrusted: the directories *above* the store. Each must be owned
# by root or by the service account, and must not be writable by others unless
# it carries the sticky bit (which is why /tmp is acceptable and a shared
# 0777 parent is not).
namei -l /srv/freedom/snapshots
sudo chown root:root /srv /srv/freedom
sudo chmod 0755 /srv /srv/freedom
```

If a repair policy should ever become this process's job, that is a change to
this document and to the operations policy, not a code decision.

**What this does and does not establish.** The enforcement is against type,
owner, mode and directory identity as this process observes them, and against a
pathname substitution performed while the service is running. It is not a claim
of cross-account resistance proven by experiment: no automated test creates a
second POSIX account, and none should. The deployment requirement above — a
service-account-owned `0700` root whose ancestors only `root` and the service
account can write — is what the implementation assumes and what it refuses to
run without.

#### Retention and deletion

Deleting an artifact is an operator action against the filesystem, not an
application use case:

```bash
# Retain while a Council review may still need it; then delete deliberately.
rm /srv/freedom/snapshots/<checksum>.json
```

The checksum, provenance and audit record survive the deletion: the platform can
still say which snapshot a character came from without holding the document. A
preview of a deleted snapshot refuses with `snapshot_not_held`.

Include the store in the host's encrypted-backup treatment, and treat a backup
of it as holding every exported Actor's mechanics.

#### Database-unclaimed artifacts, and how to find them

The artifact is written **before** the database transaction commits, on purpose:
an orphaned file is recoverable and content-addressed, while a committed row
pointing at bytes that were never written is not. The consequence, accepted in
the package plan and restated by review finding I-1, is that a database failure,
a crash, or a refused directory-durability acknowledgement can leave a correct
artifact that no row references.

Such a file is harmless — no route serves it, and a retry of the same submission
re-uses it rather than writing a second — but it is real, and an operator should
be able to see it rather than infer it. This lists the checksums the filesystem
holds and the database does not:

```bash
# Every artifact the store holds, by checksum.
find /srv/freedom/snapshots -maxdepth 1 -type f -name '*.json' -printf '%f\n' \
  | sed 's/\.json$//' | sort > /tmp/held.txt

# Every checksum the database claims. Read-only.
psql -tAq freedom -c 'SELECT checksum FROM foundry_snapshots ORDER BY checksum;' \
  > /tmp/claimed.txt

# Held, but unclaimed.
comm -23 /tmp/held.txt /tmp/claimed.txt
```

**Report, do not delete.** Nothing in this platform removes them automatically,
and this procedure must not become a cron job that does. An unclaimed artifact is
evidence of a failure worth understanding — a database outage, a storage fault, a
crash — and deleting it before that is understood destroys the evidence. It also
cannot be assumed to be junk: a submission that failed durability acknowledgement
and is about to be retried needs exactly that file.

**Retention decision D-c, accepted by Peter Duscha on 2026-08-05:** retain a
database-unclaimed raw artifact for at most **30 days**, and delete it sooner
when the corresponding rehearsal, retry or incident is closed. Its checksum,
provenance and sanitized audit record remain permanently; the raw Actor payload
does not. Report and investigate before deleting—the maximum is not permission
to erase evidence while its incident remains open. Neither `/tmp` file above
contains an Actor value—both hold checksums only—but remove them when finished.

#### Temporary files left by a failed cleanup

A submission writes its bytes to a `.incoming-<pid>-<random>` file, publishes the
checksum entry as a **hard link** to it, and then unlinks the temporary. That
last step is best effort — the service swallows the error rather than failing a
submission whose artifact is already published and correct — so a store that
succeeded may leave one `.incoming-*` link behind, and so may a store that
failed, and so may the startup probe. The service never reports this, because it
never learns it.

Such a file is **not** an incident on its own and it is **not** an unserved
artifact: no route resolves any name but the checksum one. It is a storage cost.
Find them the same read-only way as unclaimed artifacts:

```bash
# Leftover temporaries older than an hour. The age bound matters: a
# `.incoming-*` file that is seconds old is probably a submission in flight, and
# removing it would break a live upload.
find /srv/freedom/snapshots -maxdepth 1 -type f -name '.incoming-*' -mmin +60 \
  -printf '%f\t%s bytes\t%TY-%Tm-%Td %TH:%TM\t%n links\n'
```

Read the `links` column before doing anything:

| Link count | What it is | Action |
|---|---|---|
| `2` or more | the bytes are also published under a checksum name; this is a success-path cleanup failure | the artifact is intact. Removing the temporary frees the inode and no bytes. Safe once you have confirmed the checksum entry exists |
| `1` | the bytes were never published, or the checksum entry has since been deleted under the retention rule | removing it frees the bytes. **Confirm with `sha256sum` first**: if its hash names an artifact the database still claims, it is a failure-path leftover of a submission that will be retried, and the retry writes its own temporary anyway |

Confirm before removing, rather than trusting the name:

```bash
# Is there a published artifact holding the other link? `%i` is the inode.
find /srv/freedom/snapshots -maxdepth 1 -type f -printf '%i\t%n\t%f\n' | sort -n

# What the leftover hashes to, and whether the database claims it. Read-only.
sha256sum /srv/freedom/snapshots/<the .incoming- name>
psql -tAq freedom -c "SELECT id, received_at FROM foundry_snapshots \
   WHERE checksum = '<that hash>';"
```

**The same rule as the unclaimed-artifact procedure applies: report, then remove
deliberately.** Nothing in the platform removes these automatically, this
procedure must not become a cron job that does, and the service is deliberately
given no listing or deletion capability of its own — it can create a temporary
and unlink one it created in the attempt that is running, and nothing else.
Repeated leftovers are a signal worth following: the unlink is failing, which
usually means the root's mode or ownership has drifted, or the filesystem is
full or read-only. Check the §5.6 required directory state before treating it as
routine.

`find` is used here rather than `ls`: the names begin with a dot, so a plain
`ls` does not show them, and `-maxdepth 1 -type f` keeps the procedure from
following anything into a directory that should not be there in the first place
(if one is, that is §9's "An unexpected entry under a checksum name" territory).

### 5.7 Monitoring, and what a log may say

Logs from this endpoint carry a fixed failure category and an exception *class
name* — never a message, a path, a credential, an artifact byte or an Actor
value (`adapters/safe_logging.py`). The rehearsal server's access log records
that a request happened and its status, and nothing else.

Operator-visible failure categories:

| Status | Code | Means |
|---|---|---|
| 401 | `unauthenticated` | credential absent, wrong or revoked |
| 403 | `out_of_scope` | the principal lacks `foundry:snapshot:submit` |
| 411/413 | `length_required`, `artifact_too_large` | body limits; check §5.4 |
| 400 | `artifact_rejected` (+ `artifact_code`) | the bundle broke a contract rule |
| 400 | `checksum_mismatch` | client and server hold different bytes |
| 409 | `request_key_conflict` | one key reused for a different export |
| 409 | `concurrent_submission` | a race was lost and unresolvable; retry the same key |
| 503 | `storage_unavailable`, `database_unavailable` | **nothing was recorded or confirmed**; retry the same key |
| 500 | `internal_error` | an unexpected defect; nothing was recorded or confirmed; retry the same key |
| 403 | `origin_not_allowed`, `preflight_method_not_allowed`, `preflight_header_not_allowed` | a browser preflight; see §5.4 |
| 503 | `authentication_unavailable` | the preview route, before Phase 3 |

`artifact_rejected` is the one to read carefully: its `artifact_code` is the
export-contract rule that failed, and the message names the limit or the key.

**"Nothing was recorded or confirmed" is deliberately not "nothing was
stored"** (review finding I-1). The artifact is written before the transaction
commits, so a `database_unavailable`, an `internal_error`, or a
`storage_unavailable` raised as `durability_unconfirmed` may leave a correct
content-addressed file behind. What every one of them does establish is that no
snapshot was recorded and that retrying the same `Idempotency-Key` is safe. §5.6
says how to find any file left behind, and §9 what to do about it.

The same applies to the `409`s, which is what the second re-review of I-1 found
still overstated. `request_key_conflict`, `original_result_unavailable` and
`concurrent_submission` are all raised *after* the artifact store has run, and
two of them can only occur when an **earlier** submission recorded something. So
they say what *this attempt* established and nothing else — this attempt
recorded nothing, the earlier submission's record is unchanged, and a retry
cannot create a second snapshot. Read them that way in an incident: a `409` is
not evidence that the store is empty, and it is not evidence that nothing at all
was recorded under that key.

Which storage refusals may leave bytes behind is a property of the refusal rather
than a sentence every refusal inherits. Three statements are possible, and the
message carries whichever one that path can prove:

| The refusal says | Means | What to do |
|---|---|---|
| "No artifact was published, and no artifact already held was changed or removed" | a pre-publication refusal: a bad root, a bad platform, a failed write | fix the named condition; there is nothing on the filesystem to investigate |
| "An entry was already present under that checksum and was refused; it has been left exactly as it was found" | **something is under a checksum name that should not be** | §9, "An unexpected entry under a checksum name". Do not delete it |
| "Publication under that checksum may or may not have completed, and its durability was not confirmed" | `durability_unconfirmed` only | retry the same key; the retry completes the guarantee against the same file |

The third re-review found the second I-1 defect one level down from the first:
the *default* — the sentence an unclassified reason inherits — still asserted
that nothing already held had been changed or removed, which the publication race
made false. A default may state what is structurally true of a content-addressed
store; it may not make a positive claim about what is on the filesystem. It no
longer does.

## 5.8 Smoke test — the server half, without Foundry

Two minutes, no Foundry, no real data. Do this **before** Rehearsal A: it proves
the endpoint, the credential, the artifact store and the database are wired up,
so a failure during the rehearsal is about Foundry rather than about the server.

```bash
cd /opt/discord-bots/freedom-bot
WORK=$(mktemp -d)

# A generated secret and the digest configuration holds.
SECRET=$(./venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))')
DIGEST=$(./venv/bin/python -c \
  'import sys; from adapters.http.credentials import secret_digest; print(secret_digest(sys.argv[1]))' \
  "$SECRET")

# A synthetic bundle from the committed test fixtures. No real Actor data.
./venv/bin/python -c "
from tests import foundry_fixtures as fx
open('$WORK/synthetic.json','wb').write(fx.encode(fx.bundle()))"

FREEDOM_SNAPSHOT_ARTIFACT_ROOT="$WORK/artifacts" \
FREEDOM_SNAPSHOT_PRINCIPALS="foundry-the-guild|foundry:snapshot:submit|$DIGEST" \
APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/python -m tools.snapshot_api --port 8757 &

CHECKSUM=$(sha256sum "$WORK/synthetic.json" | cut -d' ' -f1)
curl -sS -w '\nHTTP %{http_code}\n' -X POST http://127.0.0.1:8757/api/v1/foundry/snapshots \
  -H "Authorization: Bearer foundry-the-guild.$SECRET" \
  -H 'Content-Type: application/json' \
  -H "Idempotency-Key: foundry-module:$CHECKSUM" \
  -H "X-Snapshot-SHA256: $CHECKSUM" \
  --data-binary "@$WORK/synthetic.json"
```

Expect `HTTP 201` and a receipt. Run the same command again: `HTTP 200` with
`"duplicate":true`, the **same** `snapshot_id`, and still one artifact file.

`curl` sends no `Origin`, so this exercises the endpoint without touching the
browser-origin policy at all — which is exactly why it cannot substitute for the
real-browser check in §8. To see the preflight the browser will perform:

```bash
curl -sS -i -X OPTIONS http://127.0.0.1:8757/api/v1/foundry/snapshots \
  -H 'Origin: https://foundry1.example.org' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization,content-type,idempotency-key,x-snapshot-sha256'
```

With that origin in `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` expect `204` and an
`Access-Control-Allow-Origin` naming it; without it, `403 origin_not_allowed`
and no permission header. This still proves only that the server answers
correctly — no browser is enforcing anything here.

Then check the state and clean up:

```bash
ls -l "$WORK/artifacts"     # one file, 0600, named for its own SHA-256
psql -tA freedom_test -c \
  "SELECT received_via, submitted_by_principal FROM foundry_snapshots;"
psql -tA freedom_test -c \
  "SELECT (SELECT count(*) FROM characters), (SELECT count(*) FROM snapshot_imports);"
                            # both 0 — a submission applies nothing

kill %1
psql -q freedom_test -c \
  "TRUNCATE audit_events, foundry_snapshots, snapshot_imports, idempotency_keys CASCADE;"
rm -rf "$WORK"
```

`$SECRET` exists only in that shell. It is not written to a file, and the digest
is the only thing that ever goes into configuration.

## 6. Rehearsal A — inactive-folder transport rehearsal

**Not run.** Maintainer-supervised, against the disposable environment.

0. Run the §5.8 smoke test first, so that a failure here is about Foundry
   rather than about the server.
1. Configure the module for a **non-production** ingestion endpoint.
2. Select `Characters (inactive)`, or another explicitly chosen non-live folder.
3. Confirm the folder ID, full path, deployment tuple and Actor count in the
   dialog before pressing Submit.
4. Submit through the module.
5. Confirm the module's receipt checksum matches
   `SELECT checksum FROM foundry_snapshots ORDER BY received_at DESC LIMIT 1`
   and matches `sha256sum` of the downloaded fallback of the same export.
6. Preview against the disposable rehearsal database.
7. Optionally exercise apply — **only** in the disposable database.
8. Confirm Foundry is unchanged: Actor count, Item counts, folder structure and
   the `Actors (shared)` compendium.
9. Confirm nothing entered Git: `git status` shows no `.json` artifact, no dump,
   no log and no Actor content.
10. Without changing the selected folder or exportable world state after the
    successful submission in step 4, induce one unconfirmed **duplicate**
    delivery with a rehearsal-only proxy fault that forwards the complete POST
    to the service and drops or delays only the downstream response.

    **The injector must fault the POST, not the CORS preflight** (finding RA-4).
    A fault applied to the `OPTIONS` preflight stops the browser from sending
    the POST at all, so nothing reaches the service and the rehearsal can only
    reach the miss branch — while appearing to have exercised a lost response.
    Let the preflight through untouched and fault the POST's response only.

    The module must reuse the confirmed prepared bytes from step 4; do not
    discard or prepare a fresh export. Confirm from the sanitized upstream
    access record that the POST reached the service; stopping the service
    before submission is not this test, for the same reason. Record the first
    submission's UTC time and the last retry's UTC time, reload the Foundry page
    so its in-memory retry is lost, and execute the **Lost-pin reconciliation**
    in §9 — including step 1's closure, which is recorded with its evidence even
    when the outcome is the expected hit. Settlement is
    `tools.submission_admission close`, run **after** the faulted duplicate
    delivery and before the query. Nothing is stopped: the endpoint keeps serving,
    Caddy keeps serving, and the three Foundry instances stay up. Record the
    generation closed, the operator and the time. Then follow **step 4's hit
    branch** — a new credential and a new generation — and record both, because
    the GM's module cannot submit again until that has been done. An earlier
    version of this rehearsal stopped the endpoint and terminated Caddy here, and
    told the operator to expect host-wide downtime; that is withdrawn with the
    procedure that required it.
    The intended rehearsal outcome is
    one hit with `duplicate = false`: the original attempt's audit event resolves
    to the snapshot row. The same-key retry replays its receipt without writing
    another audit event. Do not make a fresh submission during this check. Record
    the sanitized conclusion, never the snapshot contents.

    **This step does not exercise the late-commit case.** Faulting the response
    means the request has already been served, so the acceptance event is
    committed before the operator queries — the hit branch. The sequence
    settlement exists for is the opposite one, where the query runs *before* a
    still-open transaction commits. It is covered by
    `tests/test_snapshot_recovery_settlement.py`, and inducing it against a live
    supervised rehearsal would mean holding a real transaction open by hand.
    Do not attempt it here.
11. Reset the disposable database and delete the raw artifact according to the
    recorded rehearsal decision.

This proves transport and integration. **It does not satisfy the Phase 2 gate.**

## 7. Rehearsal B — formal active-folder Phase 2 gate rehearsal

**Not run.** Maintainer-supervised, in the approved environment.

1. Select `Characters (active)`.
2. Submit, then run the reconciliation **preview only**.
3. Account for every stable external Actor ID as mapped, create-candidate or
   explicitly unresolved.
4. Resolve or explain every identity discrepancy. Zero unexplained discrepancies
   is the acceptance threshold (plan §12 Phase 2).
5. Store only the sanitized Data Owner attestation the implementation plan
   defines, under `docs/review/`.
6. Commit no artifact, no Actor name, no mechanics, no raw report and no
   unnecessary player or campaign data.

Inactive-folder evidence proves transport. It does not replace this.

## 8. Manual smoke test — the parts no automated test reaches

The dialog, the Actor Directory button and the browser download need a running
Foundry client. Everything beneath them is covered by
`foundry-module/tests/*.test.mjs` and the Python suite. Check by hand, once, per
module change:

- [ ] the button appears in the Actor Directory for a GM and **not** for a player;
- [ ] the dialog lists every Actor folder with its full path, stable ID, Actor
      count and, where applicable, the "sub-folders NOT included" note;
- [ ] the displayed deployment tuple matches the world;
- [ ] the credential field is present, masked, and empty every time the dialog
      opens — it must never be pre-filled, because nothing stores it;
- [ ] Cancel does nothing at all;
- [ ] Download JSON produces a file whose `sha256sum` equals the checksum shown,
      **without** a credential being entered;
- [ ] Submit with the field left empty refuses with `missing_credential` and
      makes no request;
- [ ] Submit produces a receipt naming an Actor count and a checksum, and **no**
      Actor name, mechanic or raw JSON;
- [ ] submitting the same export twice reports it as already held;
- [ ] with the endpoint stopped, Submit reports a network failure and says a
      retry is safe;
- [ ] Actor, Item and Folder counts in Foundry are unchanged throughout.

### 8.1 The credential confidentiality check — maintainer-supervised

Do this once, with a **synthetic** credential, in the disposable rehearsal
world. It is the observation the automated tests model but cannot make.

1. As a GM, open the dialog and submit with the synthetic credential.
2. In the GM console, confirm the credential was persisted nowhere:
   ```js
   (function () {
     var count = 0;
     var settings = game.settings.storage.get("world").contents;
     for (var i = 0; i < settings.length; i++) {
       var key = String(settings[i].key);
       if (
         key.startsWith("freedom-blades-export.") &&
         /credential|secret|token/i.test(key)
       ) count++;
     }
     return count;
   })(); // must be 0
   ```
3. Join the same world as an **ordinary player**, in a different browser profile,
   and in that player's console confirm the credential is nowhere in the client
   state they were vended:
   ```js
   JSON.stringify([...game.settings.storage.get("world")].map(s => s.value))
     .includes("<the synthetic secret>");   // must be false
   ```
   Step 3 is the point of the exercise. It is what the old design would have
   failed, and no write-permission or button-visibility test could have shown it.
4. Rotate the synthetic credential afterwards regardless of the outcome.

### 8.2 The browser-origin check — maintainer-supervised

**Not run.** `curl` does not enforce CORS, so no check in this document so far
has proven the supported browser workflow reaches the endpoint.

1. Put the rehearsal Foundry instance's exact origin in
   `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` and reload the service.
2. Submit from the Foundry browser client and confirm a receipt is shown.
3. In the browser's network panel, confirm an `OPTIONS` preceded the `POST` and
   returned `204` with `Access-Control-Allow-Origin` naming that origin.
4. Remove the origin from the allowlist, reload, and submit again: the module
   must report a network failure, and the server must log a refused preflight.
   That failure is what proves the allowlist is load-bearing rather than
   decorative.
5. Restore the allowlist.

Until this has been done and recorded, the browser workflow is verified by
automated preflight tests only.

## 9. Recovery

**Roll back first, restore second.**

1. **A refused submission needs no recovery.** It recorded nothing but one
   refused audit event. Fix the reported `artifact_code` and submit again; the
   refusal does not block the retry. A refusal reached before the bytes were
   stored — every `artifact_rejected`, `checksum_mismatch` and
   `invalid_request_key` — also wrote no file.
2. **An interrupted submission is safe to repeat.** The idempotency key is
   derived from the checksum, so the retry is a retry: same bytes and same key
   return the original receipt, and the artifact store is content-addressed, so
   nothing is duplicated. An artifact left by a crash between storing and
   committing is re-used harmlessly by that retry.
3. **`storage_unavailable` with reason `durability_unconfirmed` means the file
   may exist and was not acknowledged as durable.** The submission was refused
   and nothing was recorded. Retry the same key: the retry finds the file,
   re-verifies it and re-syncs the directory, which completes the guarantee the
   first attempt could not. If it keeps happening, the filesystem is the problem
   — check that the store is not on a mount that refuses directory `fsync`, and
   note that the service now refuses to start on such a filesystem rather than
   reporting success it cannot support.

   Every *other* `storage_unavailable` reason — `root_permissive`,
   `root_not_owned`, `root_replaced`, `root_ancestor_untrusted`,
   `artifact_permissive`, `checksum_mismatch` and the rest of the §5.6 table —
   refused before publishing anything and removed nothing. Fix the reported
   state and retry; nothing needs cleaning up **except** in the case below.

   `root_replaced` specifically means the configured path no longer names the
   directory the service anchored itself to at startup. Nothing was written to
   the directory now holding that name. Confirm with `stat` what is there,
   restore or accept the new directory, and **restart the service** so it
   anchors to it deliberately.

   `link_unsupported` means the artifact root is on a filesystem that cannot
   publish without overwriting. Move the root to ext4, XFS, Btrfs, ZFS or tmpfs.
   Do not work around it: publication's guarantee depends on it.

#### An unexpected entry under a checksum name

`checksum_mismatch`, `artifact_untrusted`, `artifact_permissive`,
`artifact_not_owned` and `artifact_not_a_regular_file` from a **store** mean the
service found something under a checksum name that it did not put there and would
not accept. It refused, and it left the entry exactly as it was.

**That is evidence. Do not delete it, do not `chmod` it, and do not let a retry
be the first thing that happens.** The submission cannot succeed until the entry
is dealt with, so there is no pressure to be quick.

```bash
# What is actually there. `--dereference` is deliberately absent: if it is a
# symlink, the link itself is the finding.
ls -ln /srv/freedom/snapshots/<checksum>.json
stat /srv/freedom/snapshots/<checksum>.json

# Is it the artifact its name claims? The service already decided it is not;
# this is what you show someone else.
sha256sum /srv/freedom/snapshots/<checksum>.json

# Does the database claim this checksum? Read-only.
psql -tAq freedom -c \
  "SELECT id, received_at, submitted_by_principal FROM foundry_snapshots \
   WHERE checksum = '<checksum>';"
```

Then, by what you found:

| What it is | Most likely | Action |
|---|---|---|
| a regular file, right mode and owner, wrong bytes | a partial restore, a truncated copy, a storage fault | preserve a copy outside the store, then decide with Peter whether to remove it. The submission can be retried once the name is free |
| a symlink | nothing in this platform creates one | **treat as a security incident.** Preserve it, establish who could write the directory, and check §5.6's ancestor requirement before restarting |
| a directory, socket or device | the same | as above |
| group- or other-readable | a backup or copy tool ran as another account, or the root's mode slipped | check the root's mode too; every exported Actor's mechanics may have been readable |
| owned by another account | as above, and more serious | as above |

Nothing in the platform will remove it for you. That is the point: an artifact
this service did not write is the only trace of whatever wrote it.

4. **`409 concurrent_submission`, `request_key_conflict` and
   `original_result_unavailable` need no filesystem action.** They tell you what
   this attempt did, not what the store contains. An artifact may be present,
   and a retry re-uses it. For `request_key_conflict`, use a new key for a
   genuinely new export; the record the key already earned is intact.
5. **An unwanted pending snapshot applies nothing.** Leave it, or delete the raw
   artifact under §5.6. Its provenance row and audit events are append-only and
   are not deleted — they are the evidence of what happened.
6. **A file with no database row** is expected after a failure at the wrong
   moment and is not by itself an incident. §5.6 says how to list them. Report,
   do not delete, and do not automate the deletion.

   **A leftover `.incoming-*` file is a different thing and needs no recovery.**
   Publication's temporary cleanup is best effort, so one can survive a
   successful store as well as a failed one. It is private, unservable and
   costs storage only; §5.6, "Temporary files left by a failed cleanup", is the
   read-only procedure. It becomes worth investigating when it *keeps*
   happening, because that means the unlink is failing — check the root's mode,
   its owner and the filesystem's free space and mount options.
7. **Database-level recovery** uses the documented restore in
   [database-development.md](database-development.md). Take a backup before
   running migrations.

### Migration

`0004_snapshot_submission_provenance` adds `received_via` and
`submitted_by_principal` to `foundry_snapshots`, with two check constraints
making them consistent. It is additive and reversible:

```bash
pg_dump --format=custom --file=/srv/backups/pre-0004.dump freedom_staging

APP_ENVIRONMENT=staging DATABASE_URL='postgresql+psycopg:///freedom_staging' \
  ./venv/bin/alembic upgrade head
```

`alembic downgrade 0003` reverses it. **Downgrading discards provenance** —
which artifacts arrived from a module and which principal presented them — so
take the backup: re-upgrading restores the columns but not their values.

No table is created or dropped, so `infra/postgresql/runtime-grants.sql.tmpl` is
unchanged and does not need reapplying.

### Foundry module client state

The module keeps one prepared snapshot entry. Preparing validated bytes marks
them `confirmed-reusable`; a timeout, network failure, malformed response, or
retryable server failure marks it `unconfirmed-retry-pinned`. A pinned entry is
never replaced by downloading JSON or by requesting a fresh preparation. The
operator must choose **Discard Pinned & Prepare New** to prepare and submit
current state, or **Discard Pinned & Download Selected** to prepare the chosen
folder without submitting. Either clears the entry before reading current world
state. Retrying the pinned submission resends the same bytes, checksum and
idempotency key.

Once delivery is pinned, a failed retry does not clear it: an empty or rotated
credential, an invalid endpoint, or a gateway `401`, `404`, or `405` says
nothing about whether the earlier attempt arrived. Only an explicit Discard
action, a successful receipt, or a positively identified
`request_key_conflict` ends that unresolved retry state.

The pin is deliberately held only in memory for the current Foundry page load;
the raw snapshot is not written to a client-readable Foundry setting or browser
storage. Do not reload or close the page while delivery is unconfirmed. A reload
loses the client retry material and is not covered by the same-key guarantee.
If it happens, stop rather than submitting current state under a new key and ask
the platform operator to perform the lost-pin reconciliation below. This is not
durable client recovery: it is a read-only check of whether the server recorded
the earlier request.

#### Lost-pin reconciliation after an accidental reload

The submitting GM gives the platform operator the exact `world_id` and a UTC
window spanning the whole unresolved delivery episode: from the first
submission of the pinned bytes through the last attempt before the reload. A
retry of pinned bytes uses the same idempotency key, so it replays the original
receipt without writing a new audit event; the first attempt's event is the
server-side evidence that the bytes arrived. Do not send Actor data or a
credential.

##### Step 1 — close the admission generation

**A client timeout is not evidence that the server stopped.** It establishes only
that the browser stopped waiting. The POST may still be inside the service:
parsing a bundle of up to 64 MiB, writing the artifact, or holding an open
transaction that has not yet committed. Reloading the page does not cancel it —
`wsgiref.simple_server` reads the request into the handler and runs it to
completion whether or not anyone is still listening.

So a query that returns no row establishes nothing on its own, and **repeating it
does not help**: two misses moments apart are two observations of the same
still-open transaction. Recording a miss on that basis authorizes a fresh export,
the fresh export mints a new checksum, the original request then commits, and the
Council is left with the second pending artifact this procedure exists to
prevent.

Before any query result may be interpreted, the operator must establish
**settlement**: that no request carrying the pinned bytes can commit after the
query has run.

**Settlement is one command.**

```bash
# Which generation is open, and for which credential.
APP_ENVIRONMENT=production \
DATABASE_URL='postgresql+psycopg://__OWNER_ROLE__@/freedom_production' \
./venv/bin/python -m tools.submission_admission show

# Close it. This is the settlement operation.
APP_ENVIRONMENT=production \
DATABASE_URL='postgresql+psycopg://__OWNER_ROLE__@/freedom_production' \
./venv/bin/python -m tools.submission_admission close \
  --principal foundry-the-guild \
  --operator 'A. Operator' \
  --reason 'Settling lost-pin episode <episode id>.'
```

`__OWNER_ROLE__` and `APP_ENVIRONMENT` are the prerequisites in
[§5.2](#admission-tool-prerequisites), and so are the exit codes: **exit 0 is the
only outcome that means the generation is closed.** Read it before interpreting
the message.

Record the generation, the operator, the reason and the time. Then, and only
then, run step 2's query.

###### Why this settles the question, when nine earlier versions did not

Every earlier version of this step tried to establish that nothing was still in
flight by **observing** something: an answer from a probe, Caddy's in-flight
gauge, a stopped endpoint, a terminated proxy, a restart-vector inventory, a
commit watermark, a `pg_locks` queue reading, a drain read taken after a lock was
released. Each was defeated the same way, and the last of them — C-23's drain
read — was defeated by this sequence:

1. the old request is accepted and pauses **before its first statement**;
2. settlement takes its lock, reads an empty queue and an unmoved watermark, and
   records a miss;
3. the drain transaction takes its lock, and *then* the paused request reaches
   its first conflicting `INSERT` and queues behind the drain;
4. the drain reading is taken before that writer can commit, so it matches;
5. the drain commits, the old writer commits immediately afterwards — and the
   miss has already authorized a fresh export with a different checksum.

**An observation of a resource cannot exclude work that has been accepted and has
not yet reached it.** That is not a defect in any particular reading; it is why no
reading can work. A request paused before its first statement is invisible to
every one of them, and it commits whenever it eventually wakes.

So settlement stops observing and **revokes**. Three facts make the closure
decisive, and none of them is a claim about timing:

- **The check is inside the request's own transaction.** Every submission reads
  its admission generation and, as the last statement before its commit, re-reads
  it. A request that was paused anywhere — in the browser's socket, inside Caddy,
  in the endpoint's accept queue, between two of its own statements — makes that
  check when it wakes, and refuses itself if the generation has closed. Where it
  was paused never enters into it.
- **The identity it is checked against travels in its own bytes.** A request is
  checked against the admission of the principal id in *its own* `Authorization`
  header, never against "whichever generation is open now". That distinction is
  the whole fence: a server-side "current generation" lookup would silently
  upgrade a request that had been paused before it, which is the same defect in a
  new place.
- **A credential holds at most one admission, ever.** `principal_id` is unique in
  `submission_admissions` for all time, so a closed generation cannot be
  succeeded by an open one for the same credential. Recovery issues a **new**
  credential and opens a generation naming that — see step 4. An old request
  cannot guess it, inherit it, or be upgraded into it, because it does not hold
  its secret.

And the closure cannot interleave with an acceptance, in either direction. An
acceptance writes a row whose foreign key references the admission, and checking
that key takes a row-level `KEY SHARE` lock on it; the closure takes `FOR UPDATE`
on the same row, plus the exclusive side of an advisory lock the submission
transaction holds shared. Those conflict, so:

- an acceptance already in flight **holds the closure off** until it commits, and
  settlement then reads a database that already contains it — a hit, with no miss
  to record; and
- an acceptance arriving during the closure **waits**, and then reads `closed` and
  rolls itself back.

`tests/test_submission_admission_postgresql.py` holds all of it against a real
PostgreSQL, using the real submission service and real transaction boundaries:
the paused-before-first-statement regression, the two other pause boundaries,
both lock orderings, retries on both sides of the closure, and the measured trap
that a plain `UPDATE` takes a lock that does *not* conflict — which is why
`tools.submission_admission` takes `FOR UPDATE` first.

###### What settlement no longer requires

**The endpoint stays up, and so does Caddy.** Settlement used to cost host-wide
downtime: it stopped the endpoint, terminated the proxy in front of it, held
both down through the query and the interpretation, and took the three Foundry
sites with them. None of that is needed now, and none of it is done. The fence
is a transaction, not an outage.

Withdrawn with it, and not to be reintroduced as an apparent simplification:
S-A's endpoint stop and its listener samples; S-I's ingress termination and its
restart-vector inventory; S-D.2's commit watermark comparison; S-D.3's
`LOCK TABLE … IN SHARE MODE`; S-D.4's `pg_locks` queue reading and drain read.
Each of them was an attempt to infer quiescence from an observation, each was
sound about what it measured, and not one of them could exclude a request that
had not yet arrived. They are not weakened here — they are **replaced**, by a
condition that does not depend on knowing what is in flight.

The requirement in §5.4 that the ingress be terminable is likewise no longer a
settlement dependency. Keep the configuration as documented; it is good practice
and it costs nothing. But §9 no longer rests on it, so adding a hop in front of
Caddy is no longer a reason to revisit this step.

###### Diagnostic readings — for understanding an episode, never for settling one

None of the following establishes anything, and no outcome below may cite one as
evidence. They are retained because an operator investigating an odd episode
wants them, and because deleting them would invite someone to re-derive them
badly.

```bash
# What the database is currently doing. A row here is something to understand,
# not a settlement condition: a request that has not reached the application has
# no backend to appear as.
psql -X -v ON_ERROR_STOP=1 freedom \
  -c "SELECT pid, usename, state, xact_start, query_start
      FROM pg_stat_activity
      WHERE datname = current_database()
        AND pid <> pg_backend_pid()
        AND state IN ('active', 'idle in transaction',
                      'idle in transaction (aborted)');"

# Whether the endpoint is listening, and whether Caddy is up. Read-only, and
# purely informational: settlement does not depend on either answer.
ss -ltnp 'sport = :8757' || true
systemctl is-active caddy || true

# Every refusal the fence has produced, which is how a closed generation looks
# from the server side when a stranded request finally arrives.
psql -X -v ON_ERROR_STOP=1 freedom \
  -c "SELECT occurred_at, payload->>'refusal_code' AS code,
             payload->>'admission_generation' AS generation
      FROM audit_events
      WHERE action = 'snapshot_submission.refused'
        AND payload->>'refusal_code' = 'admission_closed'
      ORDER BY occurred_at;"
```

That last one is worth reading in every episode. A row in it is the fence turning
a stranded request away — the event that, under every previous version of this
step, would have been a second pending artifact.

##### Step 2 — the whole-episode acceptance-event query

Run this read-only query using an account permitted to read `audit_events`
and `foundry_snapshots`:

```bash
psql -X -v ON_ERROR_STOP=1 freedom \
  -c "SELECT s.id, s.checksum, s.actor_count, s.received_at, s.received_via,
             a.correlation_id AS attempt_correlation_id,
             a.occurred_at AS attempt_occurred_at,
             a.payload->>'duplicate' AS duplicate,
             a.payload->>'admission_generation' AS admission_generation
      FROM audit_events AS a
      JOIN foundry_snapshots AS s ON s.checksum = a.entity_id
      WHERE a.action = 'snapshot_submission.accepted'
        AND a.entity_type = 'foundry_snapshot'
        AND a.source = 'foundry'
        AND a.payload->>'world_id' = 'the-guild'
        AND a.occurred_at >= '2026-08-08 19:00:00+00'::timestamptz
        AND a.occurred_at <= '2026-08-08 19:05:00+00'::timestamptz
      ORDER BY a.occurred_at;"
```

Replace all four example values: the database, world ID and both timestamps.
Set the timestamps from the known bounds of the whole unresolved episode; do
not widen them beyond those bounds merely to find a row. The time window
applies to the append-only event for the first submission of these pinned
bytes, not only to the last retry and not to the snapshot row's `received_at`.
The checksum join is deliberate: it resolves that acceptance event to the
all-time snapshot row. A module retry under the same key creates no new event;
`duplicate = false` on the original event is therefore the expected result. A
`duplicate = true` event is possible only when the same bytes arrived under a
different key. Do not replace the audit-event window with a
`foundry_snapshots.received_at` window.

`admission_generation` names the generation each acceptance was written under. It
is what makes step 1 checkable after the fact rather than taken on trust: no row
here may name the generation step 1 closed with a timestamp after that closure
committed, and if one ever does, the fence has failed and the episode is a defect
report rather than an incident.

##### Step 3 — interpret the result

Interpret the result as follows. Only the first two outcomes are conclusions;
the other two are incidents.

- **Hit** — exactly one row attributable to the attempt means the server already
  holds that pending snapshot. Record its `id`, checksum, `admission_generation`
  and receipt time in the restricted operational record, tell the GM not to
  submit again, and continue with the normal Council review of that row. **Then
  reopen submission on a new generation — step 4's hit branch**, because step 1
  closed the one the GM's module was using and nothing can be submitted until a
  new one exists.
- **Miss** — no row, **with step 1's closure committed and recorded**, means the
  server did not record an accepted pending snapshot during that episode, and
  cannot come to record one afterwards. The operator may authorize the GM to
  prepare and submit a fresh snapshot; step 4's miss branch applies to it.

  **There is no second reading to take, and no order to get right.** Earlier
  versions of this step required a watermark comparison, a lock queue reading,
  a drain read after a lock release, and the query repeated inside an open
  transaction — an order that was load-bearing precisely because each of those
  was a sample rather than a state. The closure is a state. Once it has
  committed, no request presenting that credential can produce an acceptance,
  whatever it is doing and wherever it is paused, so nothing about the timing of
  the query can make its answer stale.

  The one thing worth repeating is the query itself, and only for **operator
  error** — a mistyped world id, a window set from the wrong clock. It is not
  what makes the miss safe. The closure is.
- **Ambiguous** — more than one row, or any row that cannot be attributed to
  this attempt, means the result is unresolved. Stop; do not authorize a fresh
  submission. Correlate the fixed-category service/access logs and the rows'
  correlation IDs under the incident procedure before deciding which pending
  snapshot the Council should review. **Then take step 4's unresolved branch.**
  The incident stays open.
- **Unsettled** — step 1 could not be completed: `tools.submission_admission
  close` hit its `lock_timeout` and closed nothing (**exit code 5**); it could not
  reach the database (**3**), was refused for privilege (**4**) or failed some
  other way without committing (**6**); **it lost the connection after its
  transaction had begun, so whether the closure committed is unknown (7)**; it
  reported that the credential holds **no** admission at all (**1**), so there is
  no generation to close and the operator does not know what the endpoint has been
  accepting; or the operator does not know which generation the episode's module
  was using. This is **not** a miss and not a hit. Do not authorize a fresh
  export. Escalate to the maintainer.

  **Any non-zero exit is Unsettled**, and the episode stays open until an
  operator has established the state. For exit codes 1 to 6 that state is already
  known — every one of them is reached with the transaction rolled back, so
  nothing was closed and no failure message has to be weighed against the
  database. **Exit code 7 is the exception, and it is the one to read carefully**:
  the connection was lost after the transaction began, so PostgreSQL may have
  committed the closure without the command hearing that it did. Follow §5.2.1 —
  `show`, then the correlation join — before treating the generation as either
  open or closed. Verifying is cheap; assuming is what produces two accepted
  artifacts for one episode.

  **A `lock_timeout` is the good case, and it is worth recognising as such**
  (exit code 5). The
  closure waits only for an acceptance that is already committing, so a timeout
  means one was in flight. Wait, run `tools.submission_admission close` again,
  and then run step 2's query: the episode will almost always resolve as a
  **hit**, because the thing that blocked the closure is the acceptance the query
  is looking for.

  The way out of an unsettled episode is to establish which generation is open
  (`tools.submission_admission show`) and close it. That is the whole of it. No
  process needs stopping, the site stays up, and an episode that cannot be
  settled costs a delay rather than an outage.

No fresh submission is permitted from the reload until a settled hit or a settled
miss has been established and recorded. The checksum uniqueness constraint
prevents identical bytes from becoming two rows; the whole-episode
acceptance-event query detects the original accepted attempt even though later
same-key retries are silent replays; and the closed generation establishes that
there is no longer an attempt whose outcome the query cannot yet see. Together,
they prevent a new export with a new checksum from being submitted while the
earlier outcome is unknown.

##### Step 4 — reopen submission, on the terms the outcome chooses

**No episode takes the site down, and none of them ends with anything stopped.**
The endpoint and Caddy ran throughout: step 1 closed a generation rather than a
process. What step 4 does is decide **what may be submitted next, and under which
credential**, and record it.

Step 1 closed the generation the GM's module was using, so until a new one is
opened the endpoint answers every submission `403 admission_closed`. That is the
default state and it is the safe one. Every branch below either leaves it that
way deliberately or replaces it with a generation whose terms the operator chose.

| Step 3 said | What is opened | Fresh export |
|---|---|---|
| **Miss** | a new credential and a new generation, given to the GM | authorized |
| **Hit** | a new credential and a new generation, for later use | forbidden for this episode |
| **Ambiguous** or **Unsettled** | nothing; submission stays closed | forbidden |

**Why every branch issues a *new credential* rather than reopening the old
generation.** It cannot reopen it: `submission_admissions` moves `open` → `closed`
once, a trigger refuses the reverse and refuses `DELETE`, and `principal_id` is
unique for all time so the old credential can never hold a second generation. That
is deliberate and it is the control. A generation that could be reopened would be
indistinguishable afterwards from one that was never closed, and every settlement
record written against it would become unfalsifiable — and, more concretely, a
request stranded somewhere holding the old credential would find itself admitted
again, which is the defect this whole mechanism exists to remove.

###### After a settled miss — a new credential, then confirm the episode produced one artifact

Neither half is optional.

1. Confirm the settled miss is recorded, with the closed generation, the operator
   and the time.
2. Issue a new credential under a **new principal id** (§5.2). The id must not be
   one that has ever held an admission; `foundry-the-guild-r1`, `-r2` and so on
   are the convention. Add it to `FREEDOM_SNAPSHOT_PRINCIPALS`, remove the old
   entry, and reload.
3. Open a generation for it, and record what comes back:

   ```bash
   APP_ENVIRONMENT=production \
   DATABASE_URL='postgresql+psycopg://__OWNER_ROLE__@/freedom_production' \
   ./venv/bin/python -m tools.submission_admission open \
     --principal foundry-the-guild-r1 \
     --operator 'A. Operator' \
     --reason 'Recovery generation after settled miss, episode <episode id>.'
   ```

   Same prerequisites as [§5.2](#admission-tool-prerequisites). A non-zero exit
   means **no generation was opened**; the endpoint is still refusing every
   submission, which is the safe state, and the GM has nothing to submit under
   until this succeeds.

4. Give the new credential to the submitting GM for their password manager (§4.1
   — it goes into no Foundry setting and no server-side world state).
5. Let the GM prepare and submit the fresh export.
6. Run step 2's query again with the window widened to span the recovery itself:
   from the episode's first attempt through the fresh submission's receipt.

Expect exactly one acceptance event, and expect its checksum to be the fresh
submission's and its `admission_generation` to be the new one. That is the settled
miss confirmed by what happened next.

A **second** event whose checksum is not the fresh submission's means the
episode's original request committed after all, which the fence says cannot
happen: it would have had to pass a transactional check against a generation that
was already closed. Treat it as **ambiguous** — stop, do not let the Council
review both rows, and escalate to the maintainer as a **defect in the fence**
rather than an incident. The `admission_generation` on that second row is the
first thing to read: if it names the closed generation, the check did not run or
did not hold, and that is a code defect with a named regression test that should
have caught it.

**Retiring the route is no longer required, and this is a change from the previous
version.** It used to be the only thing standing between a stranded request and a
second artifact, because nothing on the server could refuse that request once it
arrived. Now something can: it presents the old credential, whose generation is
closed, and it is refused inside its own transaction. An operator who wants the
old address to stop answering may still retire it — the §5.4 `handle` block
replaced by `respond 410` — and it is reasonable hygiene for a noisy client. But
it is **hygiene, not a control**, and no outcome in step 3 depends on it.

###### After a settled hit — nothing new is authorized

The snapshot is already on the server and the Council is reviewing it. No fresh
export is authorized, so nothing the episode's stranded request can carry is a
second artifact: the only bytes it holds are the ones already recorded, those
bytes hash to a checksum that already exists, and the uniqueness constraint
refuses a second row for them.

Submission is nevertheless closed, because step 1 closed it. Reopen it when the
GM next needs to submit, by the same two steps as the miss branch — a new
credential (§5.2) and a new generation — and record both. There is no hurry: a
closed generation is a safe state, not a fault.

###### After an ambiguous or unsettled episode — leave submission closed

Open nothing. The endpoint answers `403 admission_closed` to every submission,
which is exactly the state an unresolved episode should leave behind, and it costs
no downtime to hold. Record that submission is closed, name the generation and the
episode, and hold the incident open with the site up.

Reopening is a maintainer decision made when the episode closes, and it takes the
same two steps as every other branch.

##### What settlement rests on, and when it stops holding

Settlement rests on four things. Not one of them is an argument about the
endpoint's concurrency, the proxy's internals, anyone's documented behaviour, or
what could still be in flight:

- **A submission checks its own credential's generation inside its own
  transaction, as the last thing before it commits.** So a request that was
  paused anywhere makes that check when it wakes. This is what none of the nine
  withdrawn conditions could do: they all had to establish something about a
  request they could not see, and this asks the request itself.
- **The identity it is checked against travels in the request's own bytes.** The
  principal id is in the `Authorization` header the client sent, fixed at the
  moment it was sent. Nothing resolves "which generation is open now", so nothing
  can silently upgrade an old request into a new generation.
- **A credential holds at most one admission, ever.** `principal_id` is unique in
  `submission_admissions` for all time, and the state moves `open` → `closed`
  once — a trigger refuses the reverse and refuses `DELETE`, for the schema owner
  too. So a closed generation stays closed, and recovery has to issue a new
  credential rather than reuse the old one.
- **Closure and acceptance cannot interleave.** The acceptance's foreign key into
  `submission_admissions` takes a row-level `KEY SHARE` lock; the closure takes
  `FOR UPDATE` on the same row, plus the exclusive side of an advisory lock the
  submission transaction holds shared. Those conflict in both directions, so one
  strictly precedes the other — an acceptance in flight holds the closure off and
  is then visible to the query, and an acceptance arriving during the closure
  waits and then refuses itself.

Two of those are properties of PostgreSQL rather than of this application, and
both are **measured** in `tests/test_submission_admission_postgresql.py` rather
than assumed — including the trap that a plain `UPDATE` of a non-key column takes
`FOR NO KEY UPDATE`, which does *not* conflict with `KEY SHARE`. A closure
written the obvious way would sail past a waiting acceptance and fence nothing
while reading exactly like a fence, which is why `tools.submission_admission`
takes `FOR UPDATE` first and why a test fails if that ever stops mattering.

**When it stops holding.** Three ways, each of which is a code or schema change
rather than an operational drift:

- the foreign key on `idempotency_keys.admission_id` is removed, or a new
  acceptance path is added that does not write that row;
- the admission check is moved out of the acceptance transaction, or resolved
  from anything other than the presented principal id; or
- a second admission is somehow opened for a credential whose first was closed,
  which the unique constraint currently makes impossible.

Each has a named regression test, and each was exercised as a deliberate mutation
before this procedure was accepted. See the C-24 change-log entry.

**What settlement no longer rests on**, because nine remediations died on it:
whether the endpoint is running, whether Caddy is running or would be restarted,
whether a hop in front of this host queues or discards a request when the origin
goes away, what `pg_stat_activity` shows, whether a commit watermark moved,
whether a lock queue was empty, and whether a drain read matched. None of them is
consulted. §5.4's requirement that the ingress be terminable is retained as good
practice and is no longer a settlement dependency, so a new hop in front of Caddy
is no longer a reason to revisit this procedure.

**The Phase 3 obligation the previous version recorded is discharged by this
one.** It read: "before `freedom-web` carries real traffic, add the mechanism
that lets recovery settle an episode **without** a stop … a pre-settlement
barrier the restarted application refuses requests against, or an equivalent.
That makes settlement a property the application states about itself rather than
one the operator assembles from process and socket state." That is what the
admission fence is. Settlement costs one transaction and no downtime, and it is
valid under a concurrent server for the same reason it is valid under this one:
nothing in it depends on how many requests are in flight.

**What remains unobserved.** No operator has yet followed this procedure end to
end on production, and no real Foundry client has yet met a `403
admission_closed`. The automated evidence is real PostgreSQL with the real
submission service; the operational rehearsal is step 10 of Rehearsal A and has
not been run against this version.

Downloading is a fallback delivery channel only. It does not confirm a server
submission and does not clear an existing pin. If the download itself fails,
no submission was attempted.
