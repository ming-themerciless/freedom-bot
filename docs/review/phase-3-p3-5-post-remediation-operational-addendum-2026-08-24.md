# P3.5 post-remediation operational addendum — 2026-08-24

**Repository:** `/opt/discord-bots/freedom-bot`
**Branch:** `docs/platform-plan`
**Author:** Claude (working Technical Lead)
**Handover executed:** `docs/review/Handover information` (Codex, Independent Reviewer, 2026-08-24)
**Written:** 2026-08-24T22:41Z; **§2 completed** 2026-08-25T05:10Z after the
Operations Owner restarted the portal

This addendum records what was actually executed against the Codex handover, and
— just as importantly — what was **not**, and why. Every command below was run;
no result is reconstructed, estimated or generalised. Steps that could not run
say so and name the blocker rather than reporting a substitute.

**Nothing here closes A-05, I-06, A-06, R-23 or the Phase 3 gate.** No gate
decision is requested. Repository acceptance, deployed observation, specialist
recommendation and the Acceptance Authority's decision remain separate.

---

## 1. Handover Step 1 — the reviewed repository state is committed

**Complete.**

| Field | Value |
|---|---|
| Baseline before | `52ea1624bcde726abb9dc4349e104a0d1af910fa` |
| Commit recorded | **`0bef692acb095a3b0e61147490ecc2c147e81e9a`** |
| Commit time (UTC) | 2026-08-24T22:36:31Z |
| Files | 37 changed — 28 modified, 9 added |

The complete working tree described by the handover was committed as one
package: Claude's S-4/S-5/S-6/S-7/S-9 remediation, the four new regression
modules, Codex's original reviews, Codex's two re-reviews, the remediation
submission, and the N-32a approval records in the numeric-policy register,
change log, RAID register and status. No user or Codex work was amended,
rewritten or discarded. A-05 and I-06 are **not** closed by it.

### 1.1 Diff inspected before committing

The full diff and every untracked file were read in full — 4,301 lines. The
change set matches the accepted remediation and contains nothing else: no
unrelated refactor, no generated file, no formatting sweep.

A secret scan over the whole package (bot/OAuth tokens, client secrets,
passwords, API and private keys, credentialled PostgreSQL URLs, Discord webhook
URLs, Discord-token-shaped strings) returned **one** hit, and it is a false
positive: `tests/web/test_emergency_refusal_audit.py` asserts that the strings
`client_secret`, `client_id`, `scope` and `access_token` are **absent** from an
audit payload. `.env` is untracked and remains ignored by `.gitignore:14`; it
was not read, printed or modified.

### 1.2 Verification, run serially against the disposable database

The portal and bot suites share one disposable PostgreSQL database and were run
one after the other, never concurrently.

```text
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv-web/bin/python -m pytest -q tests/web
  2330 passed, 80 skipped, 1137 warnings in 128.95s (0:02:08)

$ ./venv/bin/python -m pytest -q tests
  2079 passed, 267 skipped, 1 warning in 13.46s

$ node --test tests/web/webauthn_client.test.mjs
  tests 50 | pass 50 | fail 0

$ sha256sum -c adapters/web/static/asset-integrity.sha256
  4/4 OK

$ git diff --check
  clean
```

The portal total and its 80 skips — the documented permitted caller-matrix cells,
54 from `test_p3_2_matrix.py` and 26 from `test_p3_3_matrix.py` — reproduce
Codex's independently obtained figures exactly.

A focused selection over the four new regression modules plus limiter/outage,
break-glass login, break-glass escalation, canonical settings, structural guards
and the frontend freeze guard gave **229 passed in 4.86s**. This is *not* Codex's
figure of 320 and is not offered as a reproduction of it: it is a differently
composed selection, and the full-suite figures above are the comparable evidence.

---

## 2. Handover Step 2 — deploy and prove process/build identity

**Complete.** The Operations Owner restarted `freedom-web.service` on
2026-08-25. The running process has been proven to postdate the deployed commit,
and S-1's operational control is satisfied **for this deployment**.

`freedom-web.service` runs from this repository directly
(`WorkingDirectory=/opt/discord-bots/freedom-bot`,
`ExecStart=…/venv-web/bin/python -m uvicorn tools.portal_server:application`), so
the reviewed commit reached the deployment path at commit time and the restart
was the whole of the deployment.

### 2.1 The identity record

| Field | Value |
|---|---|
| Unit | `freedom-web.service` (`/etc/systemd/system/freedom-web.service`) |
| Deployment (UTC) | **2026-08-24T22:36:31Z** — the commit itself; the unit serves this working tree |
| Restart (UTC) | **2026-08-25T05:08:56Z** (`ActiveEnterTimestamp`) |
| Main PID | **3785672** |
| Process start (UTC) | **2026-08-25 05:08:55Z** (`ps -o lstart`) |
| Commit deployed | **`0bef692acb095a3b0e61147490ecc2c147e81e9a`** (2026-08-24T22:36:31Z) |
| Repository HEAD | `9f62fcf042849f66fc07cc707d59f3d1c86e35e6` (2026-08-24T22:43:06Z, documentation only) |
| Active state | `active (running)`, `Result=success`, `NRestarts=0` |
| Previous process | PID 3436943, started 2026-08-24 08:36:54Z — the stale one, now replaced |

**The process postdates the deployed commit by 6h32m**, and postdates the
documentation-only HEAD as well. `NRestarts=0` means it has not crash-looped
since.

### 2.2 Why this is proof and not an assumption

The earlier S-1 failure was a process serving Python older than the commit under
test while templates were re-read from disk, so a timestamp comparison alone is
what has to be shown to be sound rather than merely favourable:

- Every tracked `.py` file in the repository has an mtime **no later than
  2026-08-24 22:12:44Z** (newest: `tests/web/test_p3_4_static_assets.py`; newest
  non-test: `application/web/errors.py` at 22:11:19Z).
- The process started **2026-08-25 05:08:55Z**, 6h56m after the last source edit.
- CPython reads source at import and validates cached bytecode against the
  source's mtime and size, so a `__pycache__` entry cannot serve stale code to a
  process that started after the edit.

There is therefore no mechanism by which this process could be running
pre-remediation Python. That is a stronger statement than "the timestamps look
right", and it is the statement S-1 asks for.

### 2.3 Corroboration: the S-4 probe is observably running

`identity_provider: true` cannot distinguish the removed literal from a probe
that succeeded, because Discord is up. Response time can, and does:

```text
/healthz              0.024, 0.016, 0.016, 0.018, 0.017 s
/v1/auth/emergency    0.002, 0.001, 0.001, 0.001, 0.001 s
```

Both endpoints do database work; only `/healthz` performs provider I/O. The
consistent **~15 ms** gap is a warm-keepalive HTTPS round trip to Discord on a
path that, in the previous build, made no network call at all and would have
answered in the same millisecond range as the page render.

This is corroboration, not the acceptance test. The definitive observation is
`/healthz` reporting `identity_provider: false`, `degraded` and HTTP 503 under a
deliberate provider outage, which is listed in §5 and needs the Operations Owner.

### 2.4 Post-restart checks, all passing

```text
$ curl -s -H 'Host: freedom-blades-test.rpgworld.org' http://127.0.0.1:8001/healthz
  {"status":"ok","checks":{"database":true,"migrations":true,"artifact_store":true,
   "worker_heartbeat":true,"expired_leases":true,"identity_provider":true,
   "kill_switch":true},"version":"phase-3-p3.1","environment":"staging"}
  http=200

$ curl -s -H 'Host: freedom-blades-test.rpgworld.org' http://127.0.0.1:8001/v1/auth/emergency
  http=200, 3136 bytes

$ sha256sum -c adapters/web/static/asset-integrity.sha256
  4/4 OK
```

`worker_heartbeat: true` beside a dead worker unit is documented behavior, not a
regression; see §6.

### 2.5 No configuration change was required, and none was made

`WEB_RATE_LIMIT_WEBAUTHN_CHALLENGES_PER_IP` is **new** in `.env.example`, so the
obvious deployment risk was that the portal would refuse to start against an
unchanged `/etc/freedom-web/portal.env`. It did not, as predicted before the
restart: `_Reader.registered_integer` returns `PolicyBound.default` for an unset
variable, and that default is derived from the bound rather than stored
separately, so the unset variable yields **10 per source IP per 10 minutes** —
precisely the N-32a value Peter accepted. The portal started clean and answers on
both endpoints above, which is the empirical confirmation.

`/etc/freedom-web/portal.env` was **not** read; it is not readable by the review
account, and nothing here needed it.

### 2.6 What this does and does not license

Browser observations may now rest on this process: its identity is verified and
recorded. It licenses nothing else. SP-22's R-41 and R-46 denials, A-05 criteria
3 and 4, and the staging re-observations in §5 all still have to be **performed**
before any of them can be recorded.

---

## 3. Handover Step 3 — SP-22 on deployed R-41 and R-46

**Complete. A-05 criterion 6 is now evidenced in full, and F3 is answered.**

Executed by the Operations Owner on 2026-08-25 from inside an authenticated page
of a live break-glass session, against the identity-verified process PID 3785672.

| Route | Path | Time (UTC) | Status | Refusal |
|---|---|---|---|---|
| R-41 | `POST /v1/admin/snapshots/{synthetic}/folder` | 05:22:31.435Z | **403** | `emergency_surface_refused` |
| R-46 | `POST /v1/council/jobs/{synthetic}/apply` | 05:22:31.608Z | **403** | `emergency_surface_refused` |

Both are passes. `emergency_surface_refused` is raised by the **first** statement
of `authorize()` (`application/web/access_control.py:318-319`) — N-65's
continuity-surface check, which the function evaluates *before* the route's
capability requirement, deliberately, so that a break-glass session on a Council
route is refused for being emergency-scoped rather than for lacking Council. The
handover asked for an authorization `403` from the continuity-scope capability
decision and this is it, refusing one step earlier than a capability-requirement
refusal would have.

`emergency_scope_refused` was the anticipated code and is **not** the correct one
here: it is raised deeper, by `require_full_administrator_scope()` and the
mapping-capability checks (`application/web/capabilities.py:476`, `:492`), which
N-65's surface check preempts on these two routes. The observed code is the more
specific of the two and the one the contract's ordering requires.

### 3.1 Method, and the two rules it had to satisfy

The 2026-08-24 session left these two routes unobserved for a stated reason: they
are POSTs taking an identifier, so they cannot be driven from a browser address
bar, and driving them from a shell would mean handling the operator's session
cookie, which A-8 forbids. Issuing them **from inside the already-authenticated
page** satisfies both at once — the browser attaches the HttpOnly cookie itself,
so it was never read, copied, printed or recorded, and the CSRF value was taken
from the hidden field the page had already rendered and was likewise never
recorded. Only route, UTC time, status and refusal code were captured, which is
exactly what the handover permits.

Path identifiers were synthetic well-formed UUIDs
(`00000000-0000-4000-8000-000000000001`) naming no real snapshot and no real job.
Bodies were minimal and form-encoded. No mutation was attempted and none occurred.

### 3.2 Why neither result is a false pass

The 2026-08-24 session recorded a near-miss on the GET half of SP-22: the first
attempt returned the Discord sign-in page for all three URLs, which is the
signature of *no session at all* rather than of a break-glass session being
refused. The same discipline applies here, and the preamble's fixed order
(`adapters/web/import_routes.py:150-230`) makes each early failure separately
observable:

| Failure mode | Observable | Seen? |
|---|---|---|
| No session | `401`, or `303` on a navigation route | no |
| Foreign origin | `403 origin_invalid` | no |
| Wrong content type | `415` | no |
| Missing length | `411` | no |
| Bad or absent CSRF | `403` with body exactly `{"error": "csrf_invalid"}` | no |
| **Continuity surface (step 5)** | **`403 emergency_surface_refused`** | **both routes** |

Only step 5 produces the observed code, so the requests demonstrably reached
authorization. And neither reached **object lookup**: a handler that had run would
have answered `snapshot_absent`, `job_absent` or `object_not_reachable` for an
identifier naming nothing, and neither did. That absence is criterion 6's actual
property — the route refuses before it looks the object up, so an emergency
administrator cannot use it to learn whether an identifier exists.

---

## 4. Handover Step 4 — evidence-record fields

**Two of three fields completed. One requires the Operations Owner.**
Updated file: `docs/review/phase-3-p3-5-supervised-session-evidence-2026-08-24.md`.

### 4.1 SP-21 grant record UUIDs — recorded

Read host-locally from the staging database with one read-only `SELECT` naming
`id`, `purpose`, `created_at`, `expires_at`, `consumed_at` and `invalidated_at`
**and no other column**. `token_hash` was not selected, is not derivable from an
id, and appears nowhere.

| Grant record ID | created_at (UTC) | expires_at (UTC) | consumed_at (UTC) | Role in SP-21 |
|---|---|---|---|---|
| `233b8199-2371-4ee6-88b9-a8e134bdd9a5` | 20:44:12.738527 | 20:54:12.738468 | 20:44:49.396104 | Redeemed, then **replayed** at 20:45:43Z |
| `b8437d11-2ae0-4ef9-83e4-02f5325736d9` | 20:47:07.711073 | 20:57:07.711019 | — | Left unused; **expired**, refused at 21:02:45Z |

Both rows match the audit timestamps already transcribed in the evidence
document to the second. That correspondence is what identifies them as SP-21's
two grants; they were not selected by assuming it. §9.2's A-9 row is satisfied
and no deviation needs approving.

### 4.2 Exact session end — still outstanding, lower bound raised

The evidence document recorded 21:02:45Z as an explicit lower bound. A read of
`audit_events` (`occurred_at`, `action`, `actor_capability`, and the
`auth_method` payload key only) shows four later rows on 2026-08-24:

```text
21:30:04.288396  auth.login.succeeded  guild_member  discord_oauth
21:30:07.716529  auth.logout           guild_member  discord_oauth
21:30:18.380136  auth.login.succeeded  guild_member  discord_oauth
21:30:43.196749  auth.logout           guild_member  discord_oauth
```

Two ordinary Discord logins and sign-outs, after the deliberate provider outage
was restored. The lower bound is therefore **21:30:43.196749Z**. Whether those
rows are the session's closing normal-login check or unrelated later use is not
something the audit stream states, so the field stays a lower bound. **Only the
Operations Owner can supply the exact end**, and it has not been invented.

### 4.3 Authenticator description — **Not Recorded**

Written as `Not Recorded`, per the handover, and a distinct row from the
credential nicknames. `puppetmaster`, `puppetphone`, `macbook` and `iphone` are
portal **credential-record nicknames**; the evidence document itself states they
are not what the platform passkey UI displays, so no authenticator model or
device class is inferred from them and none is written. The Operations Owner can
replace the row with a truthful non-sensitive description at any time.

### 4.4 Sanitization kept true

§5 and the §9.2 A-8 row were updated rather than left to age: A-8 previously said
the only UUID recorded was one correlation reference, which the two grant record
ids would have made false. Both now name exactly what is recorded and why each is
permitted, and §5 names the two reads added today and the columns they selected.

---

## 5. Handover Step 5 — remaining A-05 procedures

**Criterion 3 complete. Criterion 4 half-observed and blocked on one decision.
F6 raised. Criteria 9 and 10 not started.**

### 5.1 Criterion 3 — observed 2026-08-25

Recorded as SP-23 in the evidence document. The Operations Owner ran
`tools.webauthn_enrollment retire` against one of the two enabled credentials and
it refused:

```text
Refused: retiring this credential would leave 1, below the minimum of 2 (N-13).
Enroll a replacement first.
```

Refused at `tools/webauthn_enrollment.py:212`, **before any write**. Nothing was
retired; the account still holds two enabled credentials. §9.2's A-3 row also asks
for the exit status; it was **observed** as `1`, matching `EXIT_REFUSED`
(`tools/web_operator.py:32`), captured from the shell rather than cited from the
source. The command was re-run to capture it and refused identically, which also
shows the refusal is stable rather than a first-attempt artifact.

Note this is **not** the same fact §4 recorded on 2026-08-24. That observation was
that *presenting* a retired credential is refused at login — a dead credential
cannot be used. Criterion 3 is that a **live** credential cannot be made dead while
it is the second-to-last one. Both now exist.

### 5.2 Criterion 4 — executed on a disposable database; one half remains

Authorised by the Operations Owner on 2026-08-25 and executed the same day.
Recorded as **SP-24** in the evidence document.

Getting *below* the threshold is the whole difficulty, and SP-23 is why: the
application refuses to take itself there. `retire` is the only route to disabling
a credential, it has no `--force` and no override, and it refuses at two. The code
names the only remaining route — "database-owner action outside the application".
So the two options were direct action against Peter's real credentials, which the
handover forbids and which the N-13 floor exists to prevent, or a disposable
database. The second was taken.

**Target:** `freedom_dev` — empty and unused before this, with no schema and no
rows, on the same host. Migrated to head `0013`, seeded with a protected
administrator account and synthetic credential records. No real credential, no
authenticator, no staging data and no production data was involved. The staging
portal was untouched and stayed up throughout; the observations ran a second
process on port 8099.

| # | State | Environment | Startup | `/healthz` |
|---|---|---|---|---|
| 1 | 1 enabled credential (below) | `development` | starts normally | `200`, `status: ok`, all checks `true` |
| 2 | 2 enabled credentials (at) | `development` | starts normally | `200`, `status: ok`, all checks `true` |

The two health bodies are **byte-identical** and so are the two startup logs.

**Not Run: the production half.** §9.2's A-4 row asks for a *production-class*
startup **refusing** below two. `is_production` is true only for
`WEB_ENVIRONMENT=production`, and `adapters/database/config.py:14-19` pins each
environment to its own database name, so observing that refusal requires a
database literally named **`freedom_production`**. Creating one on the staging
host — even to drop it minutes later — is not a reviewer's call: it manufactures
the exact artifact the `EXPECTED_DATABASES` rail exists to keep distinct from
non-production, and a database with that name outliving its purpose is a hazard to
whoever meets it next. **The decision is put to the Operations Owner and the
Security Reviewer rather than taken.** Until it is, **criterion 4 remains open.**

### 5.3 F6 — the two-credential shortfall is detected and then reported to nobody

The previous revision of this addendum recorded that `/healthz` cannot report the
credential shortfall. Executing SP-24 showed the situation is **worse than that**,
and the correction is worth stating plainly: it is not that one channel is missing.
It is that **no channel exists at all** outside production.

The check runs and produces exactly the right words. Called against the
one-credential state with the settings the process builds:

```text
warnings returned : 1
  [S-15] the protected administrator account has 1 enabled WebAuthn credential(s);
         N-13 requires at least 2.
```

And then that warning goes nowhere:

- the lifespan assigns it to `composition.startup_warnings`
  (`adapters/web/app.py:470`);
- `adapters/web/composition.py:312` describes that attribute as "diagnostic output
  no route, service, repository or control reads", which is accurate — a
  repository-wide search finds **no reader outside `tests/`**;
- it is never logged, never printed to stdout or stderr, and never reaches VM-16;
- `build_health_view` has no credential check, and VM-16's vocabulary is closed;
- and S-15 is a refusal only in production.

The observed consequence, on a staging or development host: an administrator
account down to **one** credential starts normally, emits nothing anywhere, and
answers `/healthz` with `status: ok` and every check green — permanently, and
byte-identically to a healthy two-credential account. The only place the condition
is ever stated is the enrollment tool's own output at the moment of enrollment,
which is a transcript line in a terminal that has since scrolled away.

**This is the third instance of one pattern in this package**, which is why it is
raised as a finding rather than a note. S-4 was a health check that reported a
literal instead of asking. `worker_heartbeat` reported `true` through 58 crash
loops of a dead worker. F6 detects a condition correctly and discards it. In each
case an operator consults the endpoint built for the question and is told nothing
is wrong.

**No fix is proposed here.** The route surface is frozen, VM-16 is an accepted
closed vocabulary, and adding a check to it is a contract change that needs its own
decision — not a drive-by edit during evidence work. Recording the finding is the
work; deciding what to do about it is the Security Reviewer's and the Acceptance
Authority's.

### 5.3.1 Host state left behind by SP-24

Stated so it is not discovered later and mistaken for something real:

- `freedom_dev` now holds the schema at head `0013`, one **synthetic** protected
  administrator account and two **synthetic** credential records
  (`synthetic-one`, `synthetic-two`) whose credential id and public key are
  invented base64url text and correspond to no authenticator. It was empty before.
  Nothing points at this database; the staging portal uses `freedom_staging`.
- The synthetic environment file used for the observation is in the session
  scratch directory, not the repository, and contains freshly generated throwaway
  keys and no real secret.
- No process was left running; port 8099 is free.

### 5.3.2 An error made while setting SP-24 up, and its cost

`freedom_test` — the disposable database the portal suite runs against — was
dropped in the first setup attempt, before it was established that this account
cannot recreate one: `foundry` has `rolcreatedb = false`, and `createdb` failed
after the `dropdb` had already succeeded. The database is **gone and cannot be
restored without the Operations Owner**:

```text
sudo -u postgres createdb --owner=foundry freedom_test
```

That is the same form `infra/staging/setup-portal-host.sh:138` uses, and `foundry`
is the owner `freedom_dev` and `freedom_staging` already have.

**Restored 2026-08-25 by the Operations Owner**, with that command, and the
full verification set re-run serially to prove it:

```text
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv-web/bin/python -m pytest -q tests/web
  2330 passed, 80 skipped in 135.01s

$ ./venv/bin/python -m pytest -q tests
  2079 passed, 267 skipped in 14.57s

$ node --test tests/web/webauthn_client.test.mjs
  tests 50 | pass 50 | fail 0

$ sha256sum -c adapters/web/static/asset-integrity.sha256
  4/4 OK

$ git diff --check
  clean
```

**2330 / 80 reproduces §1.2 exactly**, which is what establishes the database is
genuinely restored rather than merely present: the suite builds its own schema, and
an incompletely restored target would not have produced the same totals and the
same 80 documented caller-matrix skips.

Consequences, stated fully and now closed:

- **The portal suite could not run while it was missing.** One commit
  (`46ed980`) was verified by the bot suite and inspection only, and says so in its
  own message rather than leaving the limitation implicit. The suite has since been
  re-run against it and the figures above are that re-run.
- **Nothing else was affected.** `freedom_test` is used by the test suite alone. The
  staging portal (`freedom_staging`), the worker, the staging data and every
  observation recorded in this addendum were untouched throughout — the §1.2 figures
  predate the incident and the figures above postdate the restoration, and they
  agree.
- **What it cost:** one command from the Operations Owner, and one commit that
  briefly stood on narrower verification than the standard this package holds
  itself to.

**The lesson worth keeping** is not "be careful with `dropdb`". It is that the
account doing this work can *destroy* a shared resource it cannot *recreate* —
`rolcreatedb = false` while `DROP DATABASE` on an owned database is permitted — so
an operation that looks symmetrical is not. Anything that drops a database from
this account should confirm it can rebuild it **before** removing it.

### 5.4 Criteria 9 and 10, and the staging re-observations

**Criterion 9 is drafted, 2026-08-25**, as
`docs/operations/break-glass-credential-custody.md`, and awaits the Operations
Owner's acceptance — which is what closes the criterion, not the writing of it. It
contains no credential material: no credential id, public key, COSE bytes, PIN,
biometric, recovery token or token hash.

It covers custody, replacement and rotation, loss in three degrees (one lost, one
possibly compromised, all lost) and the case where host access is lost too. Three
things in it come from what this package actually observed rather than from the
design:

- **The usability problem, given its own section with mitigations.** Portal
  nicknames are not what the platform passkey UI displays; on 2026-08-24 the
  operator selected a *retired* credential during a genuine rehearsal because his
  authenticator listed dead and live ones identically. The most effective
  mitigation is the one most often skipped — delete retired passkeys from the
  device when you retire them in the portal.
- **What a mistake costs**, as a table of the accepted budgets, including that a
  cancelled prompt no longer spends verification budget since S-7. The practical
  line an operator needs is *five real attempts per ten minutes from one location*.
- **The manual credential count**, because of F6. The document states plainly that
  nothing in the running system will tell you that you are down to one, and gives
  the `list` command and a cadence.

`docs/operations/web-portal.md` §4.1 now points at it.

**Criterion 10** is the designated Security Reviewer's confirmation, and by its
own terms comes only after every other criterion and disposition is complete.

The proportionate staging re-observations the handover lists still need the
Operations Owner. One is worth scheduling first because it is the acceptance test
for the S-4 remediation itself: with the portal's Discord service account faulted,
`/healthz` must report `identity_provider: false`, `status: degraded` and HTTP
**503**. §2.3 shows the probe is running; this would show it answering correctly
when the answer is "no".

---

## 6. Handover Step 6 — I-06 prerequisite: why the worker never started

**Root cause found, fixed and verified running on staging, 2026-08-25. Raised as
finding F5. S-2 is resolved.**

### 6.1 What was observed

`freedom-worker.service` was `disabled` and had **never** run — `Result=success`,
`NRestarts=0`, empty `ExecMainStartTimestamp`. Enabled and started by the
Operations Owner at 05:15Z, it did not come up: it crash-looped, reaching restart
counter 58 before being stopped. Every attempt failed identically:

```text
python[…]: The web portal refuses to start: 1 configuration problem(s).
           Variable names are given; values never are.
  - [S-11] WORKER_ENABLED: must be true in a freedom-worker process. It is the one
    variable that distinguishes this process from freedom-web, and a worker started
    with it false would claim no job while appearing to run.
systemd[1]: freedom-worker.service: Main process exited, code=exited, status=1/FAILURE
```

Exit `1` is `tools/freedom_worker.py`'s documented "configuration refused".

### 6.2 Root cause: a systemd precedence rule, and documentation that got it wrong

The installed unit **does** set the variable. `systemctl show` reports both:

```text
Environment=PYTHONUNBUFFERED=1 WORKER_ENABLED=true
EnvironmentFiles=/etc/freedom-web/portal.env (ignore_errors=no)
```

And the file wins. From this host's own `man systemd.exec`, on `EnvironmentFile=`:

> Settings from these files override settings made with `Environment=`.

`/etc/freedom-web/portal.env` is **also `freedom-web`'s** environment file, so it
necessarily sets `WORKER_ENABLED=false` — S-11 refuses a web process that claims
jobs, in the other direction. The worker unit's `Environment=WORKER_ENABLED=true`
is therefore read first and then overwritten by the shared file, and the worker
refuses itself with S-11 on every start, forever.

**The deployment was built on documented advice, and the advice was wrong.**
`docs/operations/web-portal.md` said, of the two processes: *"In practice: two
environment files identical but for that line, **or one file plus
`Environment=WORKER_ENABLED=true` on the worker unit**."* The second arrangement
cannot work for the reason above. This is not an operator error.

What made it expensive to see is that the unit reads as though it is configured
correctly. `systemctl show` reports both settings and nothing states which wins;
the only place the truth appears is the journal, which the review account cannot
read (§6.4).

### 6.3 The fix, and what remains to do

Two repository changes, both committed:

- `infra/systemd/freedom-worker.service.tmpl` now carries a **second**
  `EnvironmentFile=__WORKER_ENVIRONMENT_FILE__`, listed **after** the shared one,
  holding `WORKER_ENABLED=true` and nothing secret. Ordering is the mechanism:
  *"If the same variable is set twice from these files, the files will be read in
  the order they are specified and the later setting will override the earlier
  setting."* The reasoning is written into the unit beside it, so the next person
  to edit it cannot reintroduce the `Environment=` form without reading why it
  fails.
- `docs/operations/web-portal.md` no longer offers the arrangement that cannot
  work, states why, gives the two that do, and adds the verification step this
  incident shows is necessary: check `systemctl is-active freedom-worker`, because
  `/healthz`'s `worker_heartbeat` **will not** tell you.

### 6.3.1 Installed and verified on staging, 2026-08-25

The Operations Owner created `/etc/freedom-web/worker.env` (one line,
`WORKER_ENABLED=true`, `root:freedomweb`, mode `640`, nothing secret), installed
the corrected unit — the previous one kept as
`freedom-worker.service.bak-f5` — and reloaded and restarted.

| Field | Value |
|---|---|
| Active state | **`active (running)`** |
| Main PID | **3975305** |
| Process start (UTC) | **2026-08-25 17:42:56Z** |
| `ExecMainStartTimestamp` | 2026-08-25 17:42:57Z |
| `Result` | `success` |
| Resident size | ~69 MB, well under the `MemoryMax=1G` N-47 guard |

**`NRestarts=58` is the historical counter and is the useful number here, not a
concern.** It is the total since the unit was loaded and is not reset by a manual
restart; it stopped at 58 — the count the crash loop reached before the fix. Each
failed start died inside about a second against `RestartSec=5`, so a worker still
refusing itself would have pushed the counter well past 58 within the first
half-minute. It did not move, and the PID observed at 29 seconds of uptime is the
one systemd started. That is the verification: the counter's *stillness*, not its
value.

Verified with `systemctl is-active` and `systemctl show`, **not** with `/healthz`,
for the reason in §6.4.

### 6.4 Two things this incident demonstrates, beyond the fix itself

**`worker_heartbeat: true` beside a dead worker is documented behavior, and it
held throughout.** The check asks whether the queue is draining, not whether the
unit is alive, and an empty queue drains trivially. Across the entire crash-loop —
58 restarts — `/healthz` reported `status: ok` with `worker_heartbeat: true`. The
handover warned about exactly this trap and it is worth recording that the warning
was accurate in practice, not just in principle.

**A journal the reviewer cannot read is a real constraint on diagnosis, not a
formality.** §6 of the previous revision of this addendum correctly declined to
treat an empty `journalctl` as evidence, because the review account is in neither
`adm` nor `systemd-journal`. The `systemctl show` fields were enough to establish
*that* the worker had never run; they were not enough to establish *why*, and the
cause was one line in a log only the Operations Owner could fetch. Diagnosing this
class of failure will keep requiring a human until that access changes.

---

## 7. State after this addendum

| Item | State |
|---|---|
| Reviewed repository package | **Committed** as `0bef692…` and **deployed**, process identity verified (§2) |
| Serial verification set | **Re-run and green**, figures in §1.2 |
| N-32a | Accepted 2026-08-24; no configuration change needed to deploy it (§2.3) |
| S-5, S-6 | Closed in the repository by Codex re-review |
| S-4, S-7, S-9 | Repository remediation accepted and now **running**; deployed *behavioural* observation still outstanding (§5) |
| I-06 worker prerequisite | **Met 2026-08-25** (§6.3.1) |
| S-1 | **Satisfied for this deployment** — restarted 2026-08-25T05:08:56Z; PID 3785672 postdates commit `0bef692…` by 6h32m, proven in §2.2. The control stays live for every future deployment |
| S-2 | **Resolved 2026-08-25** — root-caused as F5, fixed in the repository, installed on staging, worker `active (running)` as PID 3975305 (§6.3.1) |
| F3 / SP-22 R-41, R-46 | **Closed by observation 2026-08-25** — both `403 emergency_surface_refused` before handler object lookup (§3) |
| F4 evidence hygiene | Grant UUIDs recorded; **exact session end and authenticator description outstanding** |
| A-05 | **Open** — criteria 3 and 6 complete; criterion 4 half-observed (SP-24); criterion 9 drafted and awaiting acceptance; 4, 9, 10 outstanding |
| I-06, A-06 | **Open** |
| R-23 | **Active** |
| Phase 3 gate | **Open** |
| Public exposure, Phase 4 | **Unauthorized** |

## 8. What is needed next, and from whom

1. ~~Restart `freedom-web.service`~~ — **done 2026-08-25T05:08:56Z** (§2).
2. ~~Install the F5 fix and verify the worker~~ — **done 2026-08-25T17:42:57Z**
   (§6.3.1). I-06's worker prerequisite is met; its named procedures (TC-OPS,
   TC-PERF, TC-LIM-02, the browser half of TC-SEC-07) remain to be executed.
3. **Operations Owner** — supply the exact session-end timestamp and a truthful
   authenticator description, or confirm the latter stays `Not Recorded` (§4.2,
   §4.3).
4. ~~SP-22's R-41 and R-46 denials~~ and ~~A-05 criterion 3~~ — **done
   2026-08-25** (§3, §5.1).
5. ~~Restore the test database~~ — **done 2026-08-25**; full verification set
   re-run and reproducing §1.2 exactly (§5.3.2).
6. **Decision needed** — whether a disposable database named `freedom_production`
   may be created and dropped on this host to observe criterion 4's remaining
   production-refusal half (§5.2). Not a reviewer's call to make alone.
7. **Security Reviewer** — finding **F6** (§5.3): a below-threshold credential
   count is detected and then reported to nobody outside production.
8. **Operations Owner + supervised session** — the §5.4 staging re-observations,
   starting with the provider-outage acceptance test for S-4.
9. **Security Reviewer** — the A-05 readiness recommendation, only once the
   evidence and dispositions above are complete.
10. **Peter Duscha, Acceptance Authority** — any A-05 disposition or gate
   decision, separately and last.

No credential, assertion, challenge, cookie, token, token hash, CSRF value,
public key, raw IP address or unnecessary identity datum was read or recorded in
producing this addendum. No production service, production database, authenticator or
external account was mutated. The one staging state change is the
`freedom-web.service` restart in §2, performed by the Operations Owner.
