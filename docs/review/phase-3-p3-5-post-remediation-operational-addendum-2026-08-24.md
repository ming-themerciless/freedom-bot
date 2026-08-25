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

**Not executed.** It requires a live break-glass session established by a human
at a browser with a platform authenticator, on a process whose identity has been
verified after restart. Neither precondition is satisfiable from a shell, and
Step 2 is not done. A-05 criterion 6 remains incomplete.

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

**Not executed.** Criteria 3, 4, 9 and 10 all require the Operations Owner, a
browser, an authenticator or a designated Security Reviewer. Criterion 4 in
particular takes the credential count below its safe threshold under a bounded
procedure and must not be attempted unsupervised.

The proportionate staging re-observations the handover lists are likewise
deferred; each needs the restarted process. One of them is cheap and worth
scheduling first, because it is the restart's own acceptance test: with the
portal's Discord service account faulted, `/healthz` must report
`identity_provider: false`, `status: degraded` and HTTP **503**. On today's stale
process it reports `true` and 200 throughout an outage, which is S-4 exactly.

---

## 6. Handover Step 6 — I-06 prerequisite: why the worker is inactive

**Diagnosed. Activation requires the Operations Owner.**

`freedom-worker.service` is **installed and correct but was never started**:

```text
$ systemctl show freedom-worker.service -p UnitFileState -p ActiveState \
    -p SubState -p Result -p ExecMainStatus -p ExecMainStartTimestamp -p NRestarts
  UnitFileState=disabled
  ActiveState=inactive
  SubState=dead
  Result=success
  ExecMainStatus=0
  ExecMainStartTimestamp=
  NRestarts=0
```

`Result=success` with `NRestarts=0` and an **empty** `ExecMainStartTimestamp`
means this is not a crash, not a restart loop and not a failed dependency: the
main process has never run. `UnitFileState=disabled` means it will not start at
boot either. The installed unit file matches
`infra/systemd/freedom-worker.service.tmpl` with the placeholders filled and one
appended `[Service] Environment=WORKER_ENABLED=true` stanza, which is the
documented difference between the worker and the portal.

`journalctl -u freedom-worker.service` returned no entries, but the review
account is in neither `adm` nor `systemd-journal`, so **that particular output is
not evidence of anything** — the `systemctl show` fields above are, and they are
sufficient.

Activation (`sudo systemctl enable --now freedom-worker.service`) needs the same
password grant Step 2 does. S-2 therefore remains open as an operational item,
not a code defect.

Restating the handover's warning because it is the trap this diagnosis invites:
`worker_heartbeat: true` alongside a dead unit — visible in §2.1's `/healthz`
output above — is **documented behavior**. That check asks whether the queue is
draining, not whether the unit is alive. An empty queue drains trivially. Use
systemd for unit liveness.

---

## 7. State after this addendum

| Item | State |
|---|---|
| Reviewed repository package | **Committed** as `0bef692…` and **deployed**, process identity verified (§2) |
| Serial verification set | **Re-run and green**, figures in §1.2 |
| N-32a | Accepted 2026-08-24; no configuration change needed to deploy it (§2.3) |
| S-5, S-6 | Closed in the repository by Codex re-review |
| S-4, S-7, S-9 | Repository remediation accepted and now **running**; deployed *behavioural* observation still outstanding (§5) |
| S-1 | **Satisfied for this deployment** — restarted 2026-08-25T05:08:56Z; PID 3785672 postdates commit `0bef692…` by 6h32m, proven in §2.2. The control stays live for every future deployment |
| S-2 | **Open** — worker installed, never started, disabled at boot |
| F3 / SP-22 R-41, R-46 | **Open** |
| F4 evidence hygiene | Grant UUIDs recorded; **exact session end and authenticator description outstanding** |
| A-05, I-06, A-06 | **Open** |
| R-23 | **Active** |
| Phase 3 gate | **Open** |
| Public exposure, Phase 4 | **Unauthorized** |

## 8. What is needed next, and from whom

1. ~~Restart `freedom-web.service`~~ — **done 2026-08-25T05:08:56Z** (§2).
2. **Operations Owner** — enable and verify `freedom-worker.service` (§6),
   unblocking I-06's worker procedures.
3. **Operations Owner** — supply the exact session-end timestamp and a truthful
   authenticator description, or confirm the latter stays `Not Recorded` (§4.2,
   §4.3).
4. **Supervised session** — SP-22's R-41 and R-46 denials, and A-05 criteria 3
   and 4, on the restarted and identity-verified process. This is now the
   critical path.
5. **Security Reviewer** — the A-05 readiness recommendation, only once the
   evidence and dispositions above are complete.
6. **Peter Duscha, Acceptance Authority** — any A-05 disposition or gate
   decision, separately and last.

No credential, assertion, challenge, cookie, token, token hash, CSRF value,
public key, raw IP address or unnecessary identity datum was read or recorded in
producing this addendum. No production service, production database, authenticator or
external account was mutated. The one staging state change is the
`freedom-web.service` restart in §2, performed by the Operations Owner.
