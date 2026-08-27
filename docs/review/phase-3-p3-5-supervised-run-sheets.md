# P3.5 supervised run sheets — C-7 and C-9

**Date:** 2026-08-26 · **Author:** Claude, P3.5 working Technical Lead ·
**Status:** **Prepared. Nothing here has been executed, and nothing here
authorizes its own execution.** Every sitting waits on the grant named in its
own header, requested in `phase-3-p3-5-authority-request-2026-08-26.md`.

**Audience rule (execution plan §2):** these sheets say what to type and what to
expect. No step asks the reader to interpret a configuration file, decide a
protocol question, or judge whether an output is close enough.

**Results do not live here.** Each sitting names where its evidence is written —
`phase-3-p3-5-staging-and-operations-evidence.md` for operations rows,
`phase-3-p3-5-accessibility-and-browser-evidence.md` for browser and device rows.
This document is the instrument, not the record.

---

## 0. Standing rules for every sitting

1. **Staging only.** Nothing is run against production, and no production
   backup or real player datum is used beyond D-l's named exception.
2. **No secret is ever displayed, pasted, echoed or recorded** — not a key, a
   token, a token hash, a cookie, a CSRF value, a public key or a COSE blob.
   Where a step needs a value out of `/etc/freedom-blades/portal.env`, it reads
   **one named non-secret line** and says so.
3. **Every command is prefixed by nothing you have to guess.** `sudo` means run
   it as root; anything else runs as the ordinary account.
4. **If a step's expected result does not appear, stop the sitting.** Do not
   improvise a repair. The stop conditions are the execution plan's §8.3 and the
   inventory's §8.3; the sitting-specific ones are repeated in each sheet.
5. **Record the literal output**, not a summary of it. A result that reads
   "worked as expected" is not evidence.
6. **The clock matters.** Start each sitting with `date -u` and record it, so a
   journal interval can be bounded afterwards.

**The three identities used below**

| Name | What it is |
|---|---|
| `freedom-web.service` | the portal process |
| `freedom-worker.service` | the job worker |
| `/opt/freedom-blades/runtime/venv-web/bin/python` | the portal's interpreter |

---

## 1. SP-28 — supervised snapshot transport into staging (C-7)

**New procedure ID.** The execution plan defines SP-01…SP-23; SP-24…SP-26 were
added by the 2026-08-24/25 evidence; SP-27 by decision D-o. This is **SP-28**.
(The plan's SP-23 and the evidence's SP-23 are two different procedures — finding
N-1 — which is why no existing number is reused here.)

**Why it exists:** finding **N-3**. The deployed portal has no snapshot
submission route, and TC-OPS-03, TC-PERF-01 and TC-PERF-02 all need a snapshot
inside `freedom_staging` before they can begin. Nothing accepted for Phase 3 ever
promised a portal submission route; this is a gap in the *procedure*, not a defect.

**Authorized input (D-l):** the real `the-guild` `Characters (active)` folder, as
a supervised operational input, under the Rehearsal A/B discipline. The inactive
folder is submitted **as well** only if its Actor count exceeds 32, read from the
folder-selection dialog during this sitting.

### 1.1 Two routes, and the one I recommend

| | **Route A — module submits over HTTPS** | **Route B — module downloads, host submits on loopback** |
|---|---|---|
| Path | Foundry module → browser preflight → Caddy → loopback endpoint | Foundry module's download fallback → file copied to the host → `curl` to the loopback endpoint |
| Needs a **temporary Caddy route** | **Yes** — deployed proxy mutation, reverted at teardown | **No** |
| Also evidences | the cross-origin preflight and `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` behaviour | nothing extra |
| Risk | a proxy change on the host that serves the staging portal, added and reverted inside a 30-minute sitting | a file passes through the operator's workstation and must be shredded there too |

**Recommended: Route B.** The snapshot is a *prerequisite* for TC-OPS-03 and
TC-PERF-01/02, none of which asserts anything about the submission transport. The
browser-origin behaviour Route A would additionally show is covered by the
maintainer-supervised check in `foundry-snapshot-submission.md` §8.2 and by
automated origin tests; buying it here costs a proxy mutation on the host that is
serving the evidence. **What Route B does not evidence, stated plainly:** the
cross-origin submission path is not exercised in this package, and the submission
receipt the module shows is not observed.

The rest of this sheet is Route B. If Peter prefers Route A, the Caddy step is
added and reverted under SG-2 and I write it separately.

### 1.2 Steps

**Who:** Peter drives Foundry and the copy; Claude drives the loopback endpoint.
**Duration:** ~30 minutes. **Grant:** SG-2.

1. `date -u` — record the start.
2. **Peter, in Foundry:** open the Actor Directory, press *Submit Freedom Blades
   Snapshot*, select `Characters (active)`. **Read out and record: the folder's
   full path, its stable ID and its Actor count.** Then read the **inactive**
   folder's Actor count from the same dialog and record it — that number decides
   whether a second submission happens at all (D-l).
3. **Peter:** choose the module's **download** action rather than submit. The
   module builds and validates the bundle locally and produces the same
   checksummed bytes it would have posted.
4. **Peter:** copy the file to the host, into `/srv/freedom-blades/snapshots`
   is **wrong** — that directory is the artifact store the endpoint writes, not a
   drop box. Copy it to a path only he can read, e.g.
   `scp <file> <host>:/tmp/sp28-<date>.json`, then
   `sudo chown freedomweb:freedomweb /tmp/sp28-<date>.json && sudo chmod 600 /tmp/sp28-<date>.json`.
5. **Peter:** generate a submit-only credential for this sitting and its SHA-256
   digest, following `foundry-snapshot-submission.md` §5.2. **The secret is never
   written down, pasted into chat, or recorded in any artifact.** Only the
   principal *id* is recorded.
6. **Claude, with Peter watching:** start the loopback submission endpoint
   against staging. It binds `127.0.0.1` and refuses anything else.

   ```bash
   FREEDOM_SNAPSHOT_ARTIFACT_ROOT=/srv/freedom-blades/snapshots \
   FREEDOM_SNAPSHOT_PRINCIPALS='<principal-id>|foundry:snapshot:submit|<sha256-digest>' \
   APP_ENVIRONMENT=staging DATABASE_URL='postgresql+psycopg:///freedom_staging' \
     /opt/freedom-blades/runtime/venv-web/bin/python -m tools.snapshot_api --port 8757
   ```

   **Expect** the banner naming the artifact root, the principal id, no browser
   origins, and the accepted deployment `the-guild · Foundry 14.365 · dnd5e
   5.3.3`. **`FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` is deliberately unset:** no
   browser submits here, and an unset origin list means no browser can.
7. **Peter:** POST the bytes on loopback, supplying the credential from step 5
   through the documented header. **Expect** a receipt carrying the snapshot id,
   the checksum and the Actor count — and **compare that checksum with the one
   the module displayed in step 3.** They must be identical; if they are not,
   stop, because the bytes changed in transit.
8. Record: the snapshot id, the checksum, the Actor count, the byte size, the
   wall-clock time of the POST, `date -u`. **Record no Actor name, no payload,
   and no warning text.**
9. Stop the endpoint with Ctrl-C.

### 1.3 Teardown — mandatory, and part of this procedure rather than a follow-up

Run at the end of **M-7d**, after the last measurement that needs the snapshot,
and record each line as done:

1. `shred -u /tmp/sp28-<date>.json` on the host, and the same on Peter's
   workstation for the downloaded copy.
2. Remove the stored artifact from `/srv/freedom-blades/snapshots` under the
   retention rule in `foundry-snapshot-submission.md` §5.6.
3. Truncate the staging import tables — the D-l condition, and an Operations
   Owner action on staging only.
4. Retire the submit-only principal from the endpoint configuration; it existed
   only for this sitting.
5. `date -u`, and record the teardown as complete.

**Stop conditions:** a checksum mismatch at step 7; any Actor name or payload
that would have to be written into an artifact; the endpoint refusing to start
(read the refusal, record it, stop — it names a fixed reason and never a path).

---

## 2. M-1a — deploy the N-7 fix and re-run SP-12 (TC-OPS-05)

**Grant:** the Operations Owner's authorization in §4 of the authority request.
**Duration:** ~25 minutes. **Peter restarts; Claude reads.**

**Why a restart is the whole deployment:** the unit's `WorkingDirectory` is
`/opt/freedom-blades/platform`, so the fixed source is already on disk; the unit
file is unchanged by the fix; the running process started
`2026-08-25T22:46:33Z`, before the fix was written.

1. `date -u` — record. This timestamp bounds the fresh journal interval.
2. **Take the rollback in hand before making the change:**
   `git -C /opt/freedom-blades/platform show HEAD:tools/portal_server.py > /tmp/portal_server.pre-n7.py`
   Record that it was taken. This is the code running today.
3. `sudo systemctl restart freedom-web.service`
4. `systemctl is-active freedom-web.service` — **expect** `active`.
5. `curl -s -H 'Host: freedom-blades-test.rpgworld.org' http://127.0.0.1:8001/healthz`
   — **expect** `"status":"ok"` and `"environment":"staging"`. Record the whole body.
6. **Peter, in a browser:** complete one ordinary Discord login against the
   staging portal, so a fresh `/auth/discord/callback` line exists to inspect.
7. **SP-12 re-run, over the fresh interval only:**
   `sudo journalctl -u freedom-web.service -u freedom-worker.service --since "<the time from step 1>"`
   Reduce it exactly as the first run did: strip the syslog prefix, normalise
   UUIDs and integers to placeholders, group with counts, and **confirm the counts
   sum back to the line total** — that is what makes it complete coverage rather
   than a denylist scan.
8. **The one line that decides the row.** Find the callback access line.
   **Expect:**
   `"GET /auth/discord/callback?<redacted> HTTP/1.1" 303 See Other`
   Method, path, HTTP version and status survive; nothing after the `?` does.
9. Re-check every class the first run checked: human or character names, Discord
   usernames or IDs, character identifiers beyond opaque UUIDs, tokens or
   credentials. **Record each as found or not found.**
10. `date -u` — record the end.

**Rollback trigger:** `/healthz` does not return `status: ok` within 30 seconds
of step 3, or the access log stops emitting entirely.
**Rollback:** `sudo cp /tmp/portal_server.pre-n7.py /opt/freedom-blades/platform/tools/portal_server.py`
then `sudo systemctl restart freedom-web.service`, and record that the fix was
withdrawn.

**Evidence destination:** `phase-3-p3-5-staging-and-operations-evidence.md` §5.2,
as a **new dated subsection**. The original failure stays exactly as written;
this is recorded beside it, never over it.

**TC-OPS-05 moves to `Passed` only if step 8 and step 9 both hold.** Any leak of
any class leaves it `Failed`.

---

## 3. M-1 — prerequisite attestation (SP-02, SP-03)

**Grant:** SG-2. **Duration:** ~25 minutes. **Peter states; Claude records.**

Neither row can be closed by inspection, and neither should be: they are
statements the Operations Owner makes.

1. `date -u`.
2. **SP-02.** Peter states, in his own words, that the staging secrets were
   generated independently and that **no secret value is shared with production**,
   and that the environment file is `0600` and outside the repository.
   `sudo stat -c '%a %U:%G %n' /etc/freedom-blades/portal.env` — **expect**
   `600` and a root-owned or `freedomweb`-owned file. **The file is not opened.**
3. **SP-03.** Peter reads out the staging Discord **application id, guild id and
   role ids** — identifiers only, never a secret — and states whether each is
   separate from the production value. Record the identifiers and the statement.
4. `date -u`.

**Stop condition:** any step that would require reading, displaying or copying a
secret value. Stop before it.

**Evidence destination:** staging evidence §3, rows SP-02 and SP-03, with the
attestation quoted and attributed.

---

## 4. M-2 — kill switch (SP-09, TC-OPS-01)

**Grant:** SG-2. **Duration:** ~25 minutes.

**Precondition:** the bot and Foundry must be **running**, or "unaffected" means
nothing.

1. `date -u`. `systemctl is-active freedom-bot freedom-web freedom-worker` —
   record all three.
2. Read the switch's path — **one non-secret line**, a filesystem path:
   `sudo grep -h '^WEB_KILL_SWITCH_FILE=' /etc/freedom-blades/portal.env`
3. **`date -u`, then engage as root** (N-17: bound the window at both ends by an
   observation rather than by inference). **Root, not `freedomweb`** — the switch
   directory is `root:freedomweb` with no group write, so the portal's own account
   cannot create the file, and an earlier draft of this sheet was wrong about that:
   ```bash
   sudo env WEB_KILL_SWITCH_FILE=<path from step 2> \
     PYTHONPATH=/opt/freedom-blades/platform \
     /opt/freedom-blades/runtime/venv-web/bin/python -m tools.portal_kill_switch \
     on --operator "Peter Duscha" --reason "SP-09 / TC-OPS-01"
   ```
   Then `date -u` again.
4. Within a second or two, confirm the perimeter is closed. **Expect `503` from
   every route except the two exceptions:**
   ```bash
   curl -s -o /dev/null -w '%{http_code} /v1/characters\n' -H 'Host: freedom-blades-test.rpgworld.org' http://127.0.0.1:8001/v1/characters
   curl -s -o /dev/null -w '%{http_code} /v1/auth/emergency\n' -H 'Host: freedom-blades-test.rpgworld.org' http://127.0.0.1:8001/v1/auth/emergency
   curl -s -o /dev/null -w '%{http_code} /healthz\n' -H 'Host: freedom-blades-test.rpgworld.org' http://127.0.0.1:8001/healthz
   curl -s -o /dev/null -w '%{http_code} /static/css\n' -H 'Host: freedom-blades-test.rpgworld.org' http://127.0.0.1:8001/static/css/freedom-blades.3f877d00a8f9.css
   ```
   **Expect** `503`, `503`, **`503`**, `200`.

   **`/healthz` answers `503`, and that is correct.** It carries a `kill_switch`
   check of its own, so an engaged switch makes it report `status: degraded`. The
   criterion is that the switch must not **refuse** it, and it does not — the
   response is health's own verdict, told apart from the middleware's by its
   `application/json` content type and its **absence** of `Retry-After`. **Read
   the body, not the status code:** expect `kill_switch: false` with every other
   check `true`. An earlier draft of this sheet expected `200` and was wrong.
5. **The half that makes TC-OPS-01 worth running:** confirm the **bot and Foundry
   are unaffected.** `systemctl is-active freedom-bot` — expect `active`. Peter
   confirms in Discord that the bot still answers, and that Foundry still loads.
   Record both as observed, not assumed.
6. **`date -u`, then release** — same command with `off` and a reason — then
   `date -u` again. Re-run step 4: **expect** `200` or a redirect from the routes
   that were `503`, and `/healthz` back to `status: ok` with `kill_switch: true`.
7. `date -u`.

**Rollback trigger:** routes still answer `503` after the release.
**Rollback:** `sudo systemctl restart freedom-web.service`; if they are still
`503`, the switch file survived — remove it as `freedomweb` and restart again.

**Evidence destination:** staging evidence §3, row SP-09.

---

## 5. M-3 — deployed startup refusals and limit parity (SP-08, SP-13)

**Grant:** SG-2. **Duration:** ~30 minutes. **The riskiest sitting: every step
leaves the portal down until the value is restored.**

**Before anything:** `sudo cp /etc/freedom-blades/portal.env /etc/freedom-blades/portal.env.pre-sp08`
and record that the copy exists. This is the rollback, and there is no other.

### 5.1 SP-08 — the refusals, on the deployed configuration

**Method B, adopted 2026-08-26.** Twelve edit-restart cycles means twelve
outages with one backup between the sitting and a portal that will not come back.
Instead: **one** real restart-to-failure proves the systemd chain, and every other
refusal is observed with `tools.startup_refusal_probe`, which calls the same
`WebSettings.from_environment` the deployed process calls at startup, against the
same environment file, with one variable overridden — no socket, no service
touched, no downtime. The probe's output is value-free by construction.

> **N-18 — `systemctl restart` returning `0` does NOT mean the configuration was
> accepted.** systemd reports that it *started* the unit; the process evaluates
> its configuration milliseconds later and exits. `systemctl status` read
> immediately afterwards shows `active (running)` on a service that is
> crash-looping. **Check `systemctl show -p NRestarts` or the journal, a few
> seconds later.** An earlier draft of this sheet said to read `status`, and
> following it literally would have recorded a refusal as a non-refusal.

> **N-19 — do not trust `. /etc/freedom-blades/portal.env`.** The file is a
> systemd `EnvironmentFile`, not a shell script: an unquoted multi-word value
> (`WEB_WEBAUTHN_RP_NAME`) makes bash treat the second word as a command and drop
> the variable silently. Harmless for the checks below, but never assume a
> sourced environment is complete.

| # | Change exactly this | Expect |
|---|---|---|
| S-01 | `WEB_ENVIRONMENT=production` | refusal naming **S-01** (database is `freedom_staging`, not `freedom_production`). It will collect **S-03/S-05/S-07** in the same message — record the whole list; the collection is itself the accepted behaviour |
| S-02 | `WEB_PUBLIC_ORIGIN=https://freedom-blades.rpgworld.org` (environment left `staging`) | refusal naming **S-02** |
| S-03 | `WEB_PUBLIC_ORIGIN=http://freedom-blades-test.rpgworld.org` | refusal naming **S-03** (non-`https` origin) |
| S-04 | `WEB_ALLOWED_HOSTS=*` | refusal naming **S-04** |
| S-05 | `WEB_DISCORD_REDIRECT_URI=https://example.invalid/auth/discord/callback` | refusal naming **S-05** |
| S-06 | `WEB_DISCORD_SCOPES=identify` | refusal naming **S-06** |
| S-07 | covered by the S-01 run above | recorded there |
| S-08 | set `WEB_SECRET_KEY_CURSOR` equal to `WEB_SECRET_KEY_CSRF` — **copy the variable name, never read the value aloud** | refusal naming **S-08** |
| S-09 | `WEB_WEBAUTHN_RP_ID=rpgworld.org` | refusal naming **S-09** |
| S-10 | `WEB_SESSION_IDLE_MINUTES=90` | refusal naming **S-10** |
| S-11 | `WORKER_ENABLED=true` in the **web** unit's file | refusal naming **S-11**. The worker direction was already observed refusing 58 times during the F5 incident; record that as the other half |
| S-12 | in the **worker** unit's file, point `WORKER_ARTIFACT_ROOT` at a group-readable directory | refusal naming **S-12** |
| S-13 | **not demonstrated here.** It is enforced by a test, and making the bot's `config.py` importable would be a deployment mutation with no path back inside this sitting | record as *covered by test, not by deployed demonstration* |
| S-14 | **deferred to M-4**, immediately after the pre-migration backup, where a downgrade is already being taken and is recoverable | recorded there |
| S-15 | **SP-27, in M-1c** | recorded there |

**After the last row:** restore the file
(`sudo cp /etc/freedom-blades/portal.env.pre-sp08 /etc/freedom-blades/portal.env`),
restart, and confirm `/healthz` returns `status: ok` **before the sitting ends.**

### 5.2 SP-13 — proxy and application limit parity (TC-LIM-02)

1. Peter reads the **deployed** Caddy configuration and records the body limits
   on the browser routes and on the submission route.
2. Compare with the application's own limits: 1 MiB on browser routes, 64 MiB on
   the submission route (N-55, N-20). Record both numbers side by side.
3. **The assertion is equality.** Record it as met or not met; a mismatch is a
   finding, not something to reconcile by editing one side during the sitting.

**Stop condition:** the restored configuration does not bring the portal back.
**Rollback:** restore from `portal.env.pre-sp08`; if that fails, engage the kill
switch (M-2) and stop. A portal that is down is recoverable; a half-configured
portal serving requests is not.

**Evidence destination:** staging evidence §3, rows SP-08 and SP-13.

---

## 6. M-1b — A-05 criterion 4a (the credential threshold, below and at it)

**Grant:** the SG-3 extension. **Duration:** ~15 minutes. **Peter authorizes and
watches; Claude runs.**

**Finding N-10 is decided: option 1** (decision **D-p**, change-log
**C-P3.5-V**), approved by Peter Duscha as Security Reviewer on 2026-08-26. The
observation is taken on the **disposable `freedom_dev`**, marked `development`.
S-15 branches on `is_production` alone, so this is the identical branch a
staging-marked process would take. What it does **not** cover is recorded at the
end of this sheet, not glossed.

**Nothing here touches a real credential.** The harness refuses outright if the
database holds a credential it did not create.

1. `date -u`.
2. Clear any residue from the 2026-08-25 observation, which used a different
   operator label:
   `psql -d freedom_dev -c "SELECT count(*), created_by_operator FROM webauthn_credentials GROUP BY 2"`
   Record what is there. Peter authorizes its removal, or the sitting moves to a
   database with none.
3. **Below the threshold** — seed one synthetic credential and observe:
   ```bash
   /opt/freedom-blades/runtime/venv-web/bin/python -m tools.breakglass_observation \
     --environment development seed --credentials 1
   /opt/freedom-blades/runtime/venv-web/bin/python -m tools.breakglass_observation \
     --environment development check
   ```
   **Expect** `enabled creds 1`, `outcome passed`, and a warning line naming
   **S-15** and "at least 2".
4. **At the threshold** — seed the second and repeat `check`. **Expect**
   `enabled creds 2` and `no warnings`.
5. **The health half.** With the deployed portal untouched, record the live
   `/healthz` body from M-1a step 5: it already carries
   `"break_glass_credentials":true` and `"environment":"staging"` under the
   accepted C2-1 contract. Note in the record that the boolean's *false* state is
   evidenced by the S-15 warning in step 3 and not by a second portal process.
6. **Clean down:**
   `... --environment development clear` — **expect** `cleared`. Then
   `psql -d freedom_dev -c "SELECT count(*) FROM webauthn_credentials"` — expect `0`.
7. `date -u`.

**What this does not cover, and must be recorded as not covered:** the threshold
behaviour observed *under the staging marker itself*, and a running portal
process answering `/healthz` with `break_glass_credentials:false`. See N-10.

**Evidence destination:** staging evidence, new A-05 criterion 4a subsection.

---

## 7. M-1c — SP-27, A-05 criterion 4b (the pre-exposure S-15 refusal)

**Grant:** the SG-3 extension **and** the SP-27 authorization. **Duration:**
~20 minutes. **Peter authorizes, creates the database and supervises.**

**No socket is ever opened.** `run_resource_checks` is a plain function, so the
production branch is reached with no uvicorn, no bind and no route.

1. `date -u`.
2. **Isolate the exercise in its own network namespace** — **not** a uid-scoped
   `iptables` rule. **Finding N-21:** an earlier version of this step retargeted
   SP-25's rule from `freedomweb` to `foundry` and took every unrelated service
   under uid 1000 off the network, because SP-25's rule was safe only by virtue of
   naming a dedicated single-purpose account.

   ```bash
   sudo unshare -n runuser -u foundry -- bash -c '
     curl -s -o /dev/null -w "egress: %{http_code}\n" --max-time 5 https://discord.com/ ;
     psql -d postgres -tAc "select '"'"'socket: '"'"'||current_database()"'
   ```

   **Expect `egress: 000` (or a connect failure) and `socket: postgres`.** That
   pair is the precondition for everything below: the namespace must have no
   network **and** a working database socket. **If either half does not hold,
   stop** — do not fall back to a firewall rule.

   *The isolation is defence in depth regardless: `run_resource_checks` touches
   the filesystem, the database socket and a credential query, and makes no
   network call. It affects exactly one process and ends when that process does,
   so there is nothing to leave behind.*
3. **Peter:** create the disposable database and migrate it.
   ```bash
   sudo -u postgres createdb freedom_production
   APP_ENVIRONMENT=production DATABASE_URL='postgresql+psycopg:///freedom_production' \
     /opt/freedom-blades/runtime/venv-web/bin/alembic upgrade head
   ```
   **Expect** head `0013`.
4. **Prove the guard before trusting the exercise.** Run the check with no
   acknowledgement:
   ```bash
   /opt/freedom-blades/runtime/venv-web/bin/python -m tools.breakglass_observation \
     --environment production check
   ```
   **Expect** a refusal demanding `--acknowledge-disposable`. Record it: a guard
   that has never fired is a guard nobody has tested.
5. **Below the threshold** — seed **one** synthetic credential, then check:
   ```bash
   /opt/freedom-blades/runtime/venv-web/bin/python -m tools.breakglass_observation \
     --environment production --acknowledge-disposable seed --credentials 1
   /opt/freedom-blades/runtime/venv-web/bin/python -m tools.breakglass_observation \
     --environment production --acknowledge-disposable check
   ```
   **Expect** `listener none — run_resource_checks called directly`,
   `outcome refused`, and a line naming **S-15**. **Record it literally.**
   *This is criterion 4b's evidence.*
6. **At the threshold** — seed the second and repeat. **Expect** `outcome passed`.
   This is the falsification: it shows the refusal was the threshold and not
   production-marking by itself.
7. **Teardown, all of it, each line recorded as done:**
   ```bash
   sudo -u postgres dropdb freedom_production
   ```
   and any temporary environment file is deleted. **No firewall rule to remove** —
   the namespace ended with the process. Confirm `psql -l` no longer lists
   `freedom_production`.
8. `date -u`.

**Never recorded:** credential material, the real client secret, any real
account, or any value from a live production system. The production origin,
redirect URI and guild id used are the accepted **identifiers** already in
`application/web/config.py`, where they exist so the platform can refuse an
impostor.

**Stop condition:** the guard in step 4 does **not** fire; the database is not
empty when the harness inspects it; or any step would need a real secret.

**Evidence destination:** staging evidence §3, row SP-27.

---

## 8. M-4 — backup, restore and rollback on staging (SP-10, TC-OPS-02 staging half)

**Grant:** SG-2, granted 2026-08-26. **The C-8 decision is taken: route A**
(decision **D-q**, change-log **C-P3.5-V**), and it is **applied** — the drill
script now accepts `freedom_staging` behind `FREEDOM_DRILL_ALLOW_STAGING=1` **and**
`FREEDOM_DRILL_STAGING_CONFIRM=freedom_staging`, both required, with production
keeping no override. Step 4 below therefore runs the drill:

```bash
FREEDOM_DRILL_ALLOW_STAGING=1 FREEDOM_DRILL_STAGING_CONFIRM=freedom_staging \
  ./infra/postgresql/backup-restore-drill.sh freedom_staging <workdir>
```

**Expect the banner first**, then the round trip and the inventory comparison.

**Duration:** ~30 minutes. **Peter acts as Operations Owner throughout.**

1. `date -u`. Record the pre-state:
   `psql -d freedom_staging -tAc "select version_num from alembic_version"` and a
   row census over the boundary-relevant tables.
2. **Pre-migration backup, before anything else.**
   `pg_dump -Fc -d freedom_staging -f <workdir>/pre-sp10.dump`, then
   `sha256sum` it. Record the byte size and the digest. **This is the only thing
   standing between this sitting and a lost staging database.**
3. **S-14, deferred here from M-3.** Stop the portal, downgrade one revision,
   start the portal, and read the refusal:
   ```bash
   sudo systemctl stop freedom-web.service
   # downgrade one step, as Operations Owner
   sudo systemctl start freedom-web.service
   sudo journalctl -u freedom-web.service -n 20 --no-pager
   ```
   **Expect** a refusal naming **S-14** and the two revisions. Then upgrade back
   to head and confirm the portal starts.
4. **The rollback rehearsal proper:** run the drill (route A) or the written
   procedure (route B) — backup, checksum, destroy, restore, and a **table-and-row
   inventory comparison before and after**. Record the comparison, table by table.
5. **The check the disposable rehearsal proved worth making:** after the restore,
   confirm an append-only guard is back by attempting a refused delete:
   `psql -d freedom_staging -c "DELETE FROM foundry_snapshots"` — **expect the
   append-only refusal**. A restore that returns rows but not guards would pass a
   row-count comparison and still be a failure.
6. `date -u`.

**Rollback trigger:** the downgrade fails, or the schema is inconsistent after
step 3 or 4. **Rollback:** restore from the step-2 dump. **Do not attempt a
forward repair inside the sitting.**

**Evidence destination:** staging evidence §3, row SP-10, and the S-14 row of §3
SP-08.

---

## 9. M-5 — browser observations (SP-14, plan-SP-23 remainder)

**Grant:** SG-2. **Duration:** ~30 minutes. **Peter drives his own browser.**
**Read-only: no rollback is needed.**

> **PRECONDITION — SP-29's gate-off window must be open (finding N-14, decision
> D-r).** The staging site imports a Caddy `basic_auth` fragment, and the site
> file itself states that the gate "must be gone before the final security-header
> evidence run": a `401` in front of the application is not the response the
> accepted contract describes, and the **early-response** case below would
> otherwise observe **Caddy's** answer rather than the application's. **This
> sitting cannot produce valid TC-SEC-07 evidence while the gate is in place.**
> Peter approved a tightly bounded window on 2026-08-26; run §12A below to open
> it, and close it in the same session.

**Record for every result:** browser name and **exact build number** (the 2026-08-24
session recorded the browser but not the build), operating system and version,
viewport width in CSS pixels, zoom level, and whether an assistive technology was
running.

1. `date -u`.
2. **SP-14 — headers and CSP, observed by a real browser engine**, on three
   response classes:
   - a **normal** page — `/v1/characters` while signed in;
   - an **early** response — one refused before a handler runs, e.g. a request
     with a wrong `Host`;
   - an **error** response — a `404` or a denial page.
   For each, open the developer tools' network panel and record the literal
   `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`,
   `Referrer-Policy` and frame-ancestors values.
3. **The specific TC-SEC-07 assertion:** complete a Discord login and confirm the
   OAuth redirect completes **under `form-action 'self'`**, because a `GET` start
   is a navigation rather than a form submission. Record that the login completed
   and that no CSP violation appeared in the console.
4. **plan-SP-23 remainder**, each recorded separately:
   - **skip links** — press Tab from a cold page load; confirm the skip link
     appears, and that activating it moves focus to the **main landmark**;
   - **HTMX-enhanced paths** — exercise at least one enhanced interaction and
     confirm it updates in place without a full reload;
   - **`prefers-reduced-motion`** — enable it in the OS, reload, confirm
     animation is suppressed;
   - **real-engine contrast** — use the developer tools' contrast inspector on
     body text, a muted label, a badge and a disabled control; record the ratios.
5. `date -u`.

**Screenshots:** synthetic data only, reviewed individually before being written
anywhere. If a real name would appear, do not take the screenshot.

**Evidence destination:** `phase-3-p3-5-accessibility-and-browser-evidence.md`,
under the accepted TC-UI numbering, plus staging evidence §3 row SP-14.

---

## 10. M-6 — real device (SP-18, TC-UI-08)

**Grant:** SG-2. **Duration:** ~15 minutes. Can ride along with M-5.

1. `date -u`. Record **device model, OS version and browser build**.
2. Load the portal on the real device. At each of **320**, **768** and **1280**
   CSS pixels, and again at **200% zoom**, confirm for every one of the seven
   views: no horizontal scrolling, no clipped control, no overlapping text, and
   every primary action reachable.
3. Record each view at each width as pass or fail. **A fail is a finding, not a
   note.**
4. `date -u`.

**Evidence destination:** accessibility evidence, TC-UI-08.

---

## 11. M-7b — end-to-end flow (SP-11, TC-OPS-03)

**Grant:** SG-2. **Precondition: SP-28 completed.** **Duration:** ~30 minutes.
**Peter drives the browser throughout.**

> **Note the gate (N-14).** If the Caddy `basic_auth` gate is still in place, let
> the browser accept it **before** starting the flow. A challenge arriving
> mid-`POST` makes the browser retry without its body, which the application
> answers `415` — that is what produced the two unexplained `415`s on
> `/v1/auth/logout` on 2026-08-26 (§5.7 of the staging evidence). Inside an apply
> it would corrupt the run rather than merely confuse it.

1. `date -u`.
2. **OAuth login** as an ordinary member. Record that the member landing page
   renders.
2a. **Sign out once, deliberately, and record the status code.** Two minutes, and
   it settles the question §5.7 left open: the shipped control is a plain form, so
   a click with the gate already accepted must not return `415`. Then sign back
   in to continue.
3. **Member read** — open My Characters and one character detail. Record that
   both render and that nothing offers a mutation.
4. **Council link change** — as a Council member, change one character link.
   Record the before and after, and the audit correlation id shown.
5. **Folder selection** — as Platform Administrator, select the folder. Record
   the folder path, stable id and Actor count the confirmation displays.
6. **Preview** — start it. Record the wall-clock duration and the job id.
   *(M-7c measures this properly; here it only has to complete.)*
7. **Confirm** — apply. **Record the checksum, world, selected folder, Actor
   count, mappings and warnings the confirmation displays**, which is the
   accepted acceptance criterion for this screen. Record the counts, not the
   Actor names.
8. **Audit search** — find the import and the link change by correlation id.
   Confirm both are present and that no control offers to edit or delete them.
9. `date -u`.

**Stop condition:** any screen offering a character-game-state mutation. That
would contradict an accepted Phase 3 criterion and is a Blocking finding.

**Evidence destination:** staging evidence §3, row SP-11.

---

## 12A. SP-29 — the bounded gate-off window (decision D-r)

**Grant:** SG-2 plus decision **D-r**. **Owner:** Peter, at the console.
**Covers:** M-5, M-6, M-7a, M-7b, M-7c, M-7d — and nothing else.

**Do M-2 first.** The kill switch is the emergency stop for this window, and
proving it works *before* removing the outer protection is the right order rather
than the convenient one. If anything unexpected appears while the gate is off,
engaging layer 1 closes every route except `/healthz` and `/static/*` within a
second.

**What is accepted for the duration:** the staging build is reachable by anyone
who knows the hostname, and Certificate Transparency published that hostname at
issuance. **What still protects it:** the application's own controls — Discord
OAuth, guild and role verification, CSRF, origin and host checks, the
authentication limiter and the kill switch. Those are the controls under test,
which is the point.

### 12A.1 Opening the window

1. `date -u` — **record it. This timestamp opens the window.**
2. Confirm the kill switch is available and released: `/healthz` reports
   `kill_switch: true`.
3. Comment out or remove the `import /etc/caddy/freedom-blades-test.gate` line in
   the staging site file.
4. `sudo caddy validate --config <caddyfile>` — **expect valid.** The import
   fails *closed*, so a mistake here refuses the whole configuration rather than
   serving the site unprotected; a validation failure is the intended behaviour
   and not a fault.
5. Reload Caddy. Confirm from a browser that the site answers **without** a
   password prompt, and that `/v1/characters` still redirects an unauthenticated
   visitor to login — the application's own boundary, now the only one.
6. Record: the exact time, the change made, and that step 5 was observed.

### 12A.2 Closing it — in the same session, not the next one

1. Restore the `import` line.
2. `sudo caddy validate` — expect valid. Reload.
3. Confirm from a browser that the password prompt is **back**.
4. `date -u` — **record it. This timestamp closes the window**, and the pair is
   the evidence that it was bounded.

**Stop condition:** if the window would have to stay open past the end of the
session — an interruption, a sitting overrunning, anything at all — **close it
first and reopen it next time.** An unbounded window is a different decision from
the one that was approved.

---

## 12. M-7c and M-7d — performance and worker recovery

**Grant:** SG-2. **Precondition: SP-28 completed, and the bounds record printed
and pasted into the evidence document *before* any run.**

### 12.1 Before the first measurement

```bash
/opt/freedom-blades/runtime/venv-web/bin/python -m tools.snapshot_perf_harness bounds
```

Paste the output into the evidence document **now**. Two of the five bounds are
marked `PROPOSED` and need Peter's acceptance before they judge anything.

**Generate the synthetic fixtures** (never committed, written outside the
repository, `0600`):

```bash
/opt/freedom-blades/runtime/venv-web/bin/python -m tests.perf_snapshot_fixtures \
  --profile folder-32 --out /tmp/perf-folder-32.json
/opt/freedom-blades/runtime/venv-web/bin/python -m tests.perf_snapshot_fixtures \
  --profile bound --out /tmp/perf-bound.json
/opt/freedom-blades/runtime/venv-web/bin/python -m tests.perf_snapshot_fixtures \
  --profile over-bound --out /tmp/perf-over-bound.json
```

### 12.2 M-7c — SP-15 and SP-16 (~30 minutes)

1. `date -u`. Record the observed load: the bot and Foundry **must be running**,
   because that is the real condition (R-24).
2. **The 64 MiB refusal (TC-PERF-01's boundary half).** Submit
   `/tmp/perf-over-bound.json` to the loopback endpoint. **Expect** a refusal
   naming the byte bound, with nothing stored.
3. **Reset the worker's peak, then run the real preview:**
   ```bash
   sudo /opt/freedom-blades/runtime/venv-web/bin/python -m tools.snapshot_perf_harness \
     memory --unit freedom-worker.service --reset-peak
   ```
   Record whether the reset succeeded; if it did not, the figure is the process
   lifetime peak, which is an upper bound and must be labelled as one.
4. Start the **real-folder preview** from SP-28's snapshot. **While it runs**, in
   a second terminal:
   ```bash
   /opt/freedom-blades/runtime/venv-web/bin/python -m tools.snapshot_perf_harness \
     poll --url http://127.0.0.1:8001/healthz \
     --host-header freedom-blades-test.rpgworld.org --seconds 30
   ```
   and Peter watches the **job-status poll in his browser**, recording its
   observed latency — the harness deliberately does not touch a session cookie.
   *(That pair is SP-16 / TC-PERF-03.)*
5. When the preview completes, read the peak:
   `... memory --unit freedom-worker.service`. Record `peak rss bytes`,
   `fraction of N-47` and `within N-47`.
6. **The apply, measured end to end — the measurement that has never been taken
   (RR-06).** Time it from confirmation to committed effect. Record it as
   **n = 1**, never as a median (D-m).
7. Repeat steps 3–6 for `/tmp/perf-folder-32.json` and `/tmp/perf-bound.json` —
   the two **synthetic** runs that carry repeatability. Report the real figure
   and the synthetic figures separately, and say which is which.
8. `date -u`.

**Stop condition:** worker peak RSS approaches or exceeds N-47's 1 GiB. **That is
a finding, not a reason to raise N-47.** Record it with the bound as written
before the run, stop, and route the numeric question through delivery-plan §7.

### 12.3 M-7d — SP-17 worker recovery, then teardown (~25 minutes)

1. `date -u`.
2. Start an apply, and **while the worker holds the lease**, Peter authorizes
   `sudo systemctl kill -s SIGTERM freedom-worker.service`.
3. Observe, and record each: the lease expiring; the reaper returning the job to
   `queued`; the attempt count incrementing; the retry completing.
4. **The property that matters:** confirm **exactly one** durable effect.
   Re-submit the same input and confirm it returns the **already-committed effect
   as a duplicate** — the fence working, not a second apply.
5. **If two durable effects appear, stop immediately.** That is a Blocking
   finding, not a retryable step.
6. **SP-28 teardown, §1.3, all five lines.** Record each as done.
7. `date -u`.

**Evidence destination:** staging evidence §3, rows SP-15, SP-16, SP-17, and the
SP-28 teardown confirmation.

---

## 13. Findings raised while preparing these sheets

| ID | Finding | Class | Disposition |
|---|---|---|---|
| **N-9** | The SG-3 record is not uniform: `status.md` says "SG-3 remains ungranted" while the 2026-08-24 supervised-session evidence §7 records it **approved that day**, with SP-07/SP-20/SP-21/SP-22 executed and Passed | **Minor — record accuracy.** No evidence affected; no procedure ran without authority | Raised in the authority request §9. The request asks for an *extension*, not a fresh grant. Historical entries left as written; a dated current-state correction follows Peter's answer |
| **N-10** *(decided — D-p)* | **A-05 criterion 4a is not executable as written.** It requires the observation "under `WEB_ENVIRONMENT=staging`" **and** "on a **disposable** database". `DatabaseSettings` binds each environment to exactly one database name (`adapters/database/config.py:66`), so a staging-marked process must target `freedom_staging` — the deployed staging database holding the protected account's **two real credentials**, the records the same criterion forbids manipulating. Verified by observing the refusal, not by reading the rule: a staging-marked build against `freedom_dev` is refused by **S-01** | **Important — criterion wording.** The same shape as Codex finding B-1: two halves of one criterion that cannot both hold. **Nothing is broken in the platform**; the defect is in the criterion | **Decided 2026-08-26 as option 1** by Peter Duscha, Security Reviewer, recorded as **D-p**. The three options were: **(1)** accept the observation under the `development` marker on disposable `freedom_dev` — the S-15 branch is `is_production` or not, so `development` and `staging` take the identical path, and the live staging `environment` marker is already evidenced by `/healthz` (O-2). *My recommendation; no host mutation.* **(2)** stand up a throwaway second PostgreSQL cluster holding a disposable `freedom_staging`, which satisfies the wording literally and costs a cluster. **(3)** temporarily disable one of the real credentials on deployed staging — **excluded by the criterion's own text**, and I do not recommend it. **The harness continues to refuse `staging` outright, which under option 1 is now the correct behaviour rather than a hold** |
| **N-11** *(decided — D-q)* | **SP-10 has no instrument.** `infra/postgresql/backup-restore-drill.sh` refuses any target but `freedom_dev`/`freedom_test` by design, and its header states that as a safety property | **Important — prerequisite gap** | `phase-3-p3-5-c8-staging-drill-guard-proposal.md`: a reviewable two-signal guard extension with three falsifying tests. **Decided 2026-08-26 as route A** by Peter Duscha, Operations Owner, recorded as **D-q**, and **applied** the same day with its three tests. Bot suite after the change: **2420 passed** |

| **N-12** | **Two unexplained tests, and four test files the tracked tree cannot agree about.** The bot suite collects **2379** tests today from the 65 pre-existing files, while the 2026-08-26 verification record states **2377 passed**. No tracked test file has been modified since that run. Separately and certainly: **four tracked test files are `0600` in the working tree while Git records `100644`** — `tests/test_filesystem_layout.py` (added by the 2026-08-25 cutover, and exactly 2 tests), `tests/test_snapshot_api.py`, `tests/test_snapshot_recovery_documentation.py` and `tests/web/test_identity_migration_settings.py` | **Minor — evidence hygiene.** No test fails and no coverage is missing; every one of them passes when the owning account runs the suite. It matters because a suite whose file set depends on **who runs it** produces counts a reviewer cannot reproduce, which is the same class of defect as N-6 | **Reported, not silently repaired.** The mode drift is almost certainly collateral from the cutover's `mv` under a restrictive umask, and `chmod 644` on the four files would restore exactly what Git already records — but it is a change to files this package did not author, so it is offered rather than taken. **I cannot account for the 2-test difference** from the tracked tree and do not assert which figure is wrong; today's count is recorded as a new dated observation beside the earlier one, and the earlier record is left as written. Flagged for Codex |

---

## 14. What these sheets do not do

- They execute nothing and authorize nothing.
- They close no RAID item and request no gate decision.
- They convert no `Not Run` into `Passed`, and no partial observation into a pass.
- They start no Phase 4 work.
