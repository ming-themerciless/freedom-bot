# Phase 3 operational contract — topology, boundaries, monitoring and recovery

Status: **Accepted 2026-08-13 at P3.G0.** Deployment and operational evidence
remain assigned to later packages and gates.

**Nothing is deployed, started, configured or verified by this document.** It
states what P3.1–P3.5 must build and what the deployment gate must check. Package:
P3.0 · Owner: Claude · Numbers are `N-nn` from
[`phase-3-numeric-policy-register.md`](phase-3-numeric-policy-register.md).

Revised 2026-08-13 by the P3.0 remediation: §5 adds the reaper-liveness,
unratified-mapping and mapping-refusal signals, and §6 adds the matching recovery
procedures. No topology, perimeter or worker conclusion changed.

## 1. Evidence discipline for this document

The P3.0 prompt is explicit: *"Do not claim the current firewall or staging
environment is configured unless verified by separately authorized evidence."*

| Claim | Status here |
|---|---|
| Caddy fronts this host and terminates TLS | **Observed** in topology §1 (process/socket inspection, 2026-07-31) |
| PostgreSQL 16 is loopback-bound with a restricted runtime role | **Observed** in Phase 1/2 and exercised in Phase 2 tests |
| The artifact store's ownership/mode invariants are enforced at startup | **Implemented and tested** in Phase 2 (R-15, R-16, R-17) |
| Ports 30001–30003 are firewalled | **UNVERIFIED.** OD-25 is open. This document makes no claim either way |
| A staging environment exists | **It does not.** Delivery plan §10 records staging as open |
| `freedom-web` / `freedom-worker` services exist | **They do not.** No unit file, no venv, no service |
| Peak worker memory and real apply duration | **Unmeasured** (RR-05, RR-06) |

Everything below marked *proposed* is a design for P3.1–P3.5 to build and for the
deployment gate (plan §14.2) to verify.

## 2. Topology per environment

### 2.1 Development (proposed)

```text
developer shell
   ├── freedom-web        127.0.0.1:8000   uvicorn --reload, WORKER_ENABLED=false
   ├── freedom-worker     no listener      WORKER_ENABLED=true
   └── PostgreSQL         freedom_dev      unix socket, developer role
```

Separate virtualenv (`venv-web`), synthetic configuration, staging Discord
application, non-production Foundry fixtures. No TLS, no Caddy, `WEB_COOKIE_SECURE`
false — which is why the `__Host-` cookie prefix is conditional (config contract
§2.2) and why S-03 refuses that combination anywhere else.

### 2.2 Disposable PostgreSQL for tests

`freedom_test`, guarded by the existing `adapters/database/safety.py` policy and
the `database` pytest marker. The integration tests drop every table, which is why
`.env.example` already requires it to differ from `DATABASE_URL`.

**Open condition, carried from the delivery plan §10:** `TEST_DATABASE_URL` was
not configured in the 2026-08-13 reconciliation session and must be re-confirmed
before P3.1 — without recording any credential.

### 2.3 Staging (proposed; does not exist)

```text
Caddy (staging site block)
   ├── freedom-web-staging     127.0.0.1:8001
   ├── freedom-worker-staging  no listener
   └── PostgreSQL              freedom_staging, separate login role
```

Separate database, login role, environment file, loopback port, systemd units,
Discord application and guild, and a non-production Foundry world (OD-22).
**Staging never receives a production database backup**, and a staging process
configured with a production endpoint is a startup refusal (S-02, S-07).

### 2.4 Production (proposed; does not exist)

```text
                   Internet
                      │ 443
        ┌─────────────▼──────────────┐
        │  Caddy                     │  TLS, HSTS, exact host N-01,
        │  freedom-blades.rpgworld…  │  body limits N-55, security headers
        └──────┬─────────────┬───────┘
               │             └───────────────┐
    ┌──────────▼─────────┐        ┌──────────▼──────────┐
    │ freedom-web        │        │ foundry1..3          │  unchanged
    │ 127.0.0.1:8000     │        │ (existing services)  │
    └──────────┬─────────┘        └──────────────────────┘
               │ claims jobs via PostgreSQL
    ┌──────────▼─────────┐        ┌──────────────────────┐
    │ freedom-worker     │        │ freedom-bot          │  unchanged
    │ no listener        │        │ (existing service)   │
    └──────────┬─────────┘        └──────────────────────┘
               │
    ┌──────────▼──────────────────────────────────────────┐
    │ PostgreSQL 16, 127.0.0.1:5432, restricted role      │
    └─────────────────────────────────────────────────────┘
```

Five systemd services on one host (OD-20), each with its own unit, virtualenv,
environment file, database login role and loopback port. The bot and Foundry are
**not** modified by Phase 3 and do not depend on the portal.

## 3. Why a separate worker process — the finding the delivery plan asked for

Delivery plan §5 P3.3: *"A separate long-running worker is introduced only if P3.0
shows that a durable database-claimed job executed by `freedom-web` cannot meet
bounded recovery and operational requirements."*

**P3.0's finding: it cannot.** Three reasons, in order of weight.

1. **The work holds the GIL for the whole of its ~9.6 seconds.** The parser uses
   `json.loads` plus pure-Python NFC normalization and canonical-key ordering
   (`application/foundry/parser.py`). Neither releases the GIL. Offloading to a
   thread inside `freedom-web` therefore does not free the event loop: it stalls
   every other request, including the N-22 status polls that exist to report the
   job's progress and the `/healthz` check that monitoring uses to decide the
   process is alive. A design in which watching a job prevents the job from being
   watched is not a design.
2. **Peak memory is per-job and unmeasured.** A 16.3 MB artifact becomes a Python
   object graph several times larger; the accepted upload bound is 64 MiB (N-20).
   Bounding that with `MemoryMax` on a dedicated unit (N-47) protects the bot,
   three Foundry worlds and PostgreSQL on the shared host (RAID R-24). The same
   ceiling on `freedom-web` would kill the portal instead of the job.
3. **Deploy and restart semantics differ.** A web deploy should be quick and
   frequent; a worker holding a 60-second lease (N-23) should drain. Separating
   them lets `freedom-web` restart in seconds without abandoning an attempt, and
   lets the worker's graceful shutdown exceed the lease without delaying the
   portal.

The queue itself stays in PostgreSQL, so this introduces a **process**, not a
technology: no broker, no second datastore, no new dependency (config contract
§1.4). Both processes run the same code from the same virtualenv, differing only
by `WORKER_ENABLED` — and S-11 refuses the mistake of setting it wrongly.

**This is a decision for Peter at P3.G0**, because it adds a service to the
accepted topology. If Peter prefers to defer the worker, the honest fallback is
that the portal stalls for ~10 seconds per preview and per apply, which is
observable to every concurrent user and to monitoring.

## 4. Public perimeter

### 4.1 Caddy

| Requirement | Value |
|---|---|
| Site block | Exactly `freedom-blades.rpgworld.org` (N-01). No wildcard (OD-19) |
| Unknown hosts | Not matched by the block, therefore refused at the proxy; the application refuses again (route contract §2.1) |
| TLS | Existing Cloudflare origin certificates, as for the Foundry hosts |
| HSTS | `max-age` at least one year, `includeSubDomains` only after the Operations Owner confirms no sibling host would break |
| Request body | N-55: 1 MiB for `/v1/*`, 64 MiB only on the existing submission route |
| Timeouts | Read/write bounded; the submission route keeps its accepted longer budget |
| Headers | Adds HSTS; the application owns CSP and the rest (route contract §7.2) so there is one authority per header |
| `/healthz` | **Not proxied.** It stays loopback-only (N-50) |
| CORS | Caddy adds **no** CORS header. The submission route's exact-origin allowlist is owned by the application (`adapters/http/cors.py`), unchanged |

The Rehearsal B teardown lesson is recorded as a procedure, not a footnote: a
temporary Caddy route added for a rehearsal was reverted from a backup captured
*after* the route was added, so the first revert was a no-op and the route stayed
live for about two hours. **Any temporary route must be reverted by removing the
block explicitly and verified with a live request, not by restoring a backup whose
capture time is unverified.**

### 4.2 Private ports

| Service | Bind | Public |
|---|---|---|
| `freedom-web` | `127.0.0.1:8000` | no — via Caddy only |
| `freedom-worker` | no listener at all | no |
| PostgreSQL | `127.0.0.1:5432` | no |
| Foundry ×3 | `*:30001-30003` | **UNVERIFIED — OD-25 is open** |

OD-25 is an Operations Owner verification that predates and outlives Phase 3.
Phase 3 does not depend on it, does not claim it, and does not change it. It is
restated because a shared host means the portal's security posture is bounded by
the host's.

### 4.3 Operator kill switch

Three layers, weakest first, all of which leave the bot and Foundry running:

| Layer | Mechanism | Effect | Recovery |
|---|---|---|---|
| 1 | `WEB_KILL_SWITCH_FILE` present (C-06) | Every route except `/healthz` answers `503` with a static maintenance body; the worker stops claiming new jobs and finishes or abandons the current attempt at its next heartbeat | Remove the file (C-06 `off`); effective within N-56 |
| 2 | `systemctl stop freedom-web freedom-worker` | The processes are gone; Caddy answers `502` | `systemctl start` |
| 3 | Comment out the Caddy site block and reload | The hostname stops resolving to anything | Restore the block and verify with a live request (§4.1) |

Layer 1 is the intended control, because health and monitoring keep working and
an operator can see the system while it is disabled. **No layer touches
`freedom-bot`, PostgreSQL or Foundry** — that separation is the requirement
(delivery plan §9.11).

## 5. Monitoring without personal data

| Signal | Source | Contains |
|---|---|---|
| Liveness / readiness | `/healthz` (VM-16) | Check names, pass/fail, environment, version |
| Job queue depth, oldest queued age | Counts over `reconciliation_jobs` | Numbers only |
| Attempt duration, requeue count | Job timestamps | Numbers only |
| **Oldest expired lease still `running`** | `max(now() - lease_expires_at) WHERE state = 'running' AND lease_expires_at < now()` | Number only. This is the reaper's liveness signal: the corrected N-43 makes the reaper the only writer of the expiry transition, so a stalled reaper is the one way a job can sit unterminated (SM-05). It should never exceed `N-23 + N-44` |
| **Unratified emergency-provenance mappings** | Count over `role_capability_mappings WHERE provenance = 'emergency_continuity'` | Number only. A mapping created during an outage that is still unratified after the outage is an operational item, not a permanent state (schema §8.1) |
| **Mapping refusals by code** | Counts over `role_capability_mapping_events WHERE outcome = 'refused'` | Code and count, never the role or the actor. A rising `emergency_scope_refused` count is what an attempted escalation looks like from the outside |
| Auth refusal counts by category | Counters over audit actions | Category and count, **never** the identity |
| Rate-limit trips | `auth_rate_limits` | Bucket **hash** and count |
| Session count | `sessions` | Number only |
| Worker memory, CPU | systemd/host | Process-level |
| Database pool saturation | SQLAlchemy pool | Numbers only |

Prohibited in every metric, log line and dashboard: Discord snowflakes, usernames,
character names, Actor content, checksums of artifacts a viewer is not authorized
to know about, tokens, grants, session identifiers, and IP addresses in plaintext
(plan §9.4; existing `adapters/safe_logging.py` discipline).

Alert thresholds are deliberately **not** set here (numeric register §4): they
depend on measured staging behaviour, and inventing them now would produce numbers
nobody has evidence for.

## 6. Backup, restore and recovery

Inherited from plan §14.3 and OD-21; Phase 3 adds new tables, not a new posture.

| Item | Rule |
|---|---|
| Backup scope | The whole `freedom_production` database. Sessions and rate limits are included because excluding them is more complex than restoring them |
| Restore testing | **Restore-tested, not reported successful** (topology §6). The existing `infra/postgresql/backup-restore-drill.sh` is the harness |
| Before each migration stage | A restore-tested dump immediately before, per migration contract §5 |
| Artifact store | Follows the existing Phase 2 retention procedure (change-log C-8, ≤ 30 days) and encrypted host backups |
| Secrets | Never in the database backup. Environment files are backed up separately by the Operations Owner |
| What a restore loses | Sessions (users log in again) and in-flight jobs (requeued or re-requested). Neither is a durable domain effect |

Recovery procedures P3.1–P3.3 must document:

| Situation | Procedure |
|---|---|
| Administrator locked out of Discord | WebAuthn break-glass (R-08). No operator action needed |
| Every passkey lost | C-01 issues a 10-minute grant on the host; R-09 consumes it; enroll new credentials with C-03 immediately |
| Suspected session compromise | C-07 revokes the account's sessions; audit shows what the session did |
| Suspected recovery-grant compromise | C-02 invalidates; C-07 revokes; audit shows whether it was consumed |
| Worker wedged | Stop the unit; the lease expires within N-23 and the reaper requeues it, or fails it with `attempts_exhausted` if this was the third attempt (SM-05). **Never** delete a job row to "unstick" it, and never `UPDATE` its state by hand: the corrected reaper reaches every expired lease, so a job that looks stuck means the reaper is not running |
| Reaper not running | The `oldest expired lease` signal above rises without bound. Restart `freedom-worker`; jobs resume from wherever they were, because every state is a durable row. No job is lost and none is duplicated — the durable effect is fenced by `uq_snapshot_imports_applied_input`, not by job state |
| Emergency mapping left unratified after the outage | A full-scope administrator ratifies it through R-38, or revokes it. Until then the authority it confers is continuity-scoped and cannot reach Council or import routes (schema §8.1) |
| Queue flooded | Kill switch layer 1 stops new claims; the queue drains or is cancelled per job (R-45) |
| Portal degrading the host | Kill switch layer 1 or 2. Bot and Foundry keep running |
| Bad deploy | `systemctl stop`, redeploy the previous revision, restart. No schema downgrade unless the deploy included a migration |
| Migration must be reversed | Migration contract §4's stage table; after stage D it is restore-and-replay, not a downgrade |

## 7. Deployment gate inputs Phase 3 owes

Plan §14.2's ten steps apply. Phase 3 must supply, before any production
deployment (which is itself behind a separate gate):

1. `freedom-web` and `freedom-worker` unit files, with `MemoryMax`, restart policy,
   `NoNewPrivileges`, `ProtectSystem`, `PrivateTmp` and a dedicated service account;
2. the Caddy site block, reviewed against §4.1;
3. the restricted database role's grants, matching schema §11.2;
4. a restore-tested backup;
5. staging evidence for the two unmeasured quantities (RR-05, RR-06);
6. the rollback procedure exercised, not merely written;
7. the kill switch exercised, including verification that the bot and Foundry are
   unaffected;
8. monitoring in place with no personal data; and
9. the environment-separation checks (S-01…S-15) demonstrated failing on
   deliberately wrong configuration.

Item 9 is worth its place: a startup refusal that has never been observed refusing
is an assumption.

## 8. Traceability

| Element | Source |
|---|---|
| Co-located host, separate services and roles | OD-20, OD-22, topology §1 |
| Public hostname and exact origin | OD-19; N-01 |
| Loopback-only application and database ports | plan §9.3; topology §4 |
| Kill switch without stopping bot or Foundry | delivery plan §9.11 |
| Monitoring without personal data | plan §9.4; §0.5 |
| Restore-tested backups | plan §14.3; topology §6 |
| Worker justification required from P3.0 | delivery plan §5 P3.3 |
| No claim about firewall or staging | P3.0 prompt §6; OD-25; delivery plan §10 |
