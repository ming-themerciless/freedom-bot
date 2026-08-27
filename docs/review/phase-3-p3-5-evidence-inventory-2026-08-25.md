# P3.5 evidence inventory and session run sheet — 2026-08-25

**Prepared:** 2026-08-25 by Claude, P3.5 working Technical Lead

**Requested by:** `docs/review/Handover information` (Codex → Claude, 2026-08-25),
"First response requested from Claude", and
`docs/review/phase-3-gate-disposition-2026-08-25.md` §"Next executable package".

**Repository:** `/opt/freedom-blades/platform` · **Head commit:** `0e3929a`
· **Branch:** `docs/platform-plan`

**Baselines:** `docs/review/phase-3-p3-5-readiness-and-execution-plan.md` §§6.2,
7.2, 12, 13 (procedure and artifact IDs used here are that document's, unchanged)
· `docs/contracts/phase-3-test-traceability.md` §§13, 16, 17, 20
· `docs/review/phase-3-delivery-plan.md` §§5 P3.5, 11.

**Status of this document: an inventory, not evidence.** It closes nothing, moves
no RAID disposition, requests no gate decision and authorizes no host action. It
records what exists, what does not, and what it would take to finish. SG-2 and
SG-3 remain unrequested by this document.

---

## 0. Method, and the crediting rule applied

Every row below was decided by one of exactly three means, and the means is named:

- **Read** — a named existing artifact was read and its literal result taken.
- **Observed** — a read-only command was run on this host **today**, and its
  output is quoted. Nothing was mutated; no `.env`, secret, credential or
  environment file was read.
- **Absent** — the artifact or observation does not exist. Verified by looking,
  not inferred.

**The crediting rule the handover sets, applied strictly.** An existing
observation is credited as `Passed` only when it satisfies the *complete* named
evidence contract — timestamp, deployed build/environment identity, command or
procedure, literal result, owner and required review. Where an observation exists
but is partial, the row stays `Not Run` and the partial observation is recorded in
its own column so a reviewer can see exactly what is and is not there. **No
partial observation has been converted into a pass in this document.**

Status vocabulary is the execution plan's §7.3, used strictly: `Passed`,
`Failed`, `Blocked`, `Not Run`.

### 0.1 Read-only observations made today

| # | Command | Result |
|---|---|---|
| O-1 | `systemctl is-active freedom-bot freedom-web freedom-worker` | `active` · `active` · `active` |
| O-2 | `curl -s -H 'Host: freedom-blades-test.rpgworld.org' http://127.0.0.1:8001/healthz` | `{"status":"ok","checks":{"database":true,"migrations":true,"artifact_store":true,"worker_heartbeat":true,"expired_leases":true,"identity_provider":true,"kill_switch":true,"break_glass_credentials":true},"version":"phase-3-p3.1","environment":"staging"}` |
| O-3 | `psql -l` | `freedom_dev`, `freedom_staging`, `freedom_test`, `postgres`, templates |
| O-4 | `psql -d freedom_staging -c "select version_num from alembic_version"` | `0013` |
| O-5 | `psql -d postgres -c "select rolname, rolcanlogin, rolsuper, rolcreatedb from pg_roles …"` | `foundry` (login, no super, no createdb) · `freedom_runtime_test` (no login) · `freedomweb` (login, no super, no createdb) · `postgres` |
| O-6 | `psql -d freedom_staging -c "\dp sessions"` | `foundry=arwdDxt/foundry`, `freedomweb=arw/foundry` — the runtime role holds no DDL |
| O-7 | `ls -la /srv/freedom-blades/` | `snapshots` `drwx------ freedomweb:freedomweb` · `web` `drwxr-x--- root:freedomweb` |
| O-8 | `ls -la /opt/freedom-blades/reference/actor-exports/` | **two** Actor JSON files, 4.3 MB total |
| O-9 | `ls -la /etc/freedom-blades/` | `Permission denied` — correct, and the environment files were therefore not read |
| O-10 | `git status --porcelain` | `M "docs/review/Handover information"` only — the incoming handover itself |
| O-11 | Artifact existence check, `docs/review/` | Four of the five §12.1 artifacts are **Absent** — see §5 |

---

## 1. Headline

**Nine of the thirteen staging-only rows in the execution plan §7.2 remain `Not
Run`. Two are `Passed`. Two are `Passed in part` and therefore recorded as `Not
Run` against their full contract.** A-05 stands at eight of ten criteria
evidenced. A-06 has no representative-operation evidence at all. R-23 is
unchanged. Four of the five required P3.5 artifacts do not exist.

The dominant fact has changed since the execution plan was written, and changed in
the right direction: **every environmental blocker that plan recorded is now
gone.** A staging build exists and is healthy (O-1, O-2); the worker is active;
the database is at head `0013` with a genuinely restricted runtime role (O-4,
O-5, O-6); a real browser has been driven against the deployed portal; two real
passkeys authenticate. What remains is **execution of the named procedures**, not
readiness for them.

Against that, this inventory raises **five new findings** (§6), of which two are
`Important` and would change the design of the very next session if discovered
inside it rather than before it:

- **N-1** — the ID `SP-23` now means two different procedures in two accepted
  documents.
- **N-2** — TC-PERF-02's "three runs" cannot be performed against one input,
  because the commit fence makes runs 2 and 3 duplicates by design.
- **N-3** — the deployed portal has **no snapshot-submission route**, so TC-OPS-03
  and TC-PERF-01/02 have no way to get a snapshot into staging without a separate
  supervised transport step.
- **N-4** — the accepted documents **conflict** on whether a real Foundry folder
  may be used in staging. This is a Data Owner decision and I have not chosen it.
- **N-5** — `freedom_staging` is owned by `foundry`, shared with `freedom_dev` and
  `freedom_test`, rather than by a dedicated staging owner role as SP-01 specifies.

---

## 1A. Superseded by execution — 2026-08-26

**This inventory records the state on 2026-08-25 and is left as written.** A great
deal was executed the following day, and the authoritative record of what has now
been observed is
[`phase-3-p3-5-staging-and-operations-evidence.md`](phase-3-p3-5-staging-and-operations-evidence.md)
§§5A–5J, not the `Not Run` tables below.

**What changed on 2026-08-26**, so a reader is not misled by the tables that
follow:

| Row | Then | Now |
|---|---|---|
| SP-02, SP-03 | Not Run | **Passed** — attestations recorded, separation corroborated by Discord snowflake creation times |
| SP-08 / TC-OPS-04 | Not Run | **14 of 15 refusals observed.** Only S-13 remains, and it is test-enforced rather than observable on a live host |
| SP-09 / TC-OPS-01 | Not Run | **Passed** — bot and Foundry confirmed unaffected |
| SP-10 / TC-OPS-02 staging half | Not Run | **Passed**, and it found Blocking finding **N-20**, since remediated and re-verified |
| SP-12 / TC-OPS-05 | Failed (N-7) | **Passed** at the third observation, after N-7 and **N-13** were both fixed and deployed |
| SP-13 / TC-LIM-02 | Not Run | **Passed** — parity exact |
| SP-14 / TC-SEC-07 browser half | Not Run | **Passed in part**, raising **N-22** (HSTS absent) and **N-23** (a live CSP violation) |
| SP-15, SP-16, SP-17 | Not Run | **Synthetic halves passed.** Worker peak memory measured for the first time. **D-m's real n = 1 apply still owed** |
| SP-18 / TC-UI-08 | Not Run | **Partly** — real iPhone at its native width; 768 and 1280 not covered |
| SP-27 | Not Run | **Passed** — A-05 criterion **4b** met before exposure |
| A-05 | Open, two criteria | **Open on criterion 10 alone** |

**Still Open: I-06, A-06.** **R-23 remains an active accepted residual.** **Phase
4 remains unauthorized.**

---

## 2. I-06 — procedure-by-procedure inventory

### 2.1 Prerequisites (SP-01…SP-06), which feed I-06 closure criterion 1

| ID | Procedure | Status | Exact existing evidence | What is missing for the whole contract |
|---|---|---|---|---|
| SP-01 | Staging database, owner role, separate restricted login role, runtime grants, `/srv/…/{snapshots,web}` at `0700` | **Not Run** as a procedure; outcome **substantially evidenced** | Observed today: `freedom_staging` exists (O-3) at head `0013` (O-4); `freedomweb` is a separate login role holding `arw` and **no DDL** on `sessions` (O-5, O-6); `/srv/freedom-blades/snapshots` is `drwx------ freedomweb` and `/srv/freedom-blades/web` is `drwxr-x--- root:freedomweb` (O-7) | A **dedicated staging owner role** — the owner is `foundry`, shared with the disposable databases (**finding N-5**). No record that `runtime-grants.sql.tmpl` was the source of the observed grants rather than something equivalent. No dated execution record with an owner |
| SP-02 | Independently generated staging secrets in a `0600` file outside the repository | **Not Run** | The portal runs and answers (O-2), so *a* configuration exists. `/etc/freedom-blades/` is unreadable to this account (O-9) — which is the correct control | The Operations Owner's **attestation** that no secret value is shared with production. This cannot be evidenced by inspection and must not be: it is a statement Peter makes, not a file I read |
| SP-03 | Separate staging Discord application, guild and role IDs; identifiers only | **Not Run** | Ordinary `discord_oauth` sessions were created against the staging portal on 2026-08-24 (read: supervised-session evidence §1), so an application and guild are configured and working | No artifact records **which** application/guild/role IDs, nor that they are separate from production. Separation is the whole point of the procedure and is currently unevidenced |
| SP-04 | `freedom-web` and `freedom-worker` on loopback `127.0.0.1:8001`, `WORKER_ENABLED` differing | **Passed** | Read: `phase-3-p3-5-f5-s2-operational-re-review-2026-08-25.md` — Codex independently observed the active unit, `WorkingDirectory`, `ExecStart` and both `EnvironmentFiles` in the required order, with `systemd-analyze verify` passing. Observed today: portal answers on `127.0.0.1:8001` (O-2); all three units active (O-1) | — |
| SP-05 | Staging Caddy site block behind the accepted proxy boundary, matched body limits | **Not Run** | `infra/caddy/freedom-blades-portal.caddy.tmpl` exists and carries the N-55 limits and the health-refusal ordering (read; F-19 remediation). The site is reachable through the proxy password gate (read: supervised-session evidence §3) | The **deployed** configuration has not been compared against the application's limits. That comparison *is* TC-LIM-02 / SP-13, below |
| SP-06 | `alembic upgrade head` against staging; re-apply grants; verify head `0013` | **Not Run** as a procedure; head **evidenced** | Observed: `freedom_staging.alembic_version = 0013` (O-4) and the runtime role's grants are correctly restrictive (O-6) | A dated execution record. The end state is right; nobody recorded reaching it |

### 2.2 The evidence-bearing procedures (SP-08…SP-19, SP-23)

| ID | Procedure | Closes | Status | Exact existing evidence, and why it is not the whole contract |
|---|---|---|---|---|
| **SP-08** | Every startup refusal observed refusing on the **deployed** configuration — S-11 both directions, S-15, environment markers, cross-environment fail-closed | TC-OPS-04 | **Not Run** | **Two of the refusals have been observed on this host, neither as SP-08.** S-11's worker direction refused 58 times during the F5 incident (read: operational addendum §6.1) — a real deployed refusal, but observed as a *fault*, with no environment identity or owner recorded against TC-OPS-04. The S-02/S-05/S-07 production-identity refusals were observed on 2026-08-25 (read: addendum §5.2.1) against a **disposable** database, not the deployed configuration. S-15's production branch is shown **not observable before production exists** (addendum §5.2.1). The web-direction S-11 refusal, the environment markers and the cross-environment fail-closed check have no observation at all |
| **SP-09** | Kill switch: engage layer 1, confirm every route except `/healthz` and `/static/*` answers `503`, confirm bot and Foundry unaffected, release | TC-OPS-01 | **Not Run** | `/healthz` reports `kill_switch: true` today (O-2), i.e. the check is wired and the switch is **not** engaged. `tools/portal_kill_switch.py` exists and is unit-tested. **Nothing has ever engaged it on a deployed portal.** Engaging requires write access under `/srv/freedom-blades/web` (`root:freedomweb`, O-7), so it is a privileged action |
| **SP-10** | Backup, restore, rollback and rerun rehearsal on the staging database | TC-OPS-02 staging half | **Not Run** | `infra/postgresql/backup-restore-drill.sh` exists and **refuses any target but `freedom_dev`/`freedom_test`** (read). **Its disposable half (EX-4) was executed 2026-08-25/26** — backup, checksum, destroy, restore and a table-and-row inventory comparison over seeded synthetic rows, identical across all 31 tables, with the restored append-only trigger verified still refusing. **EX-3's migration rollback rehearsal was executed the same night**, including the 0013 boundary observed **refusing** on a real database and failing closed, and an exact 986-line schema round trip. Both are recorded in `phase-3-p3-5-staging-and-operations-evidence.md` §2. **The two halves are distinct and must not be conflated: TC-OPS-02's disposable half is evidenced by EX-3 and EX-4; its staging half — SP-10, this row — remains `Not Run`.** SP-10 additionally needs the drill script's target guard extended to `freedom_staging` under review (C-8), or an equivalent explicitly-guarded procedure, because the script refuses any target but `freedom_dev`/`freedom_test` by design. *(Corrected 2026-08-26 after Codex interim finding **I-2**: this row previously carried a stale sentence claiming EX-3 had never run, contradicting the same row's own account of it. The stale claim was residue from an earlier edit, not a second assessment.)* |
| **SP-11** | End-to-end: OAuth login → member read → Council link change → folder selection → preview → confirm → audit search | TC-OPS-03 | **Not Run** (unblocked 2026-08-25) | OAuth login and member read are evidenced incidentally (supervised-session §1, §3 — `/v1/characters` rendered at three widths under an ordinary Discord session). **Folder selection, preview, confirm and audit search have never been exercised on staging**, and cannot be until a snapshot exists in the staging artifact store. `/srv/freedom-blades/snapshots` is empty of any recorded artifact and the portal exposes **no submission route** (**finding N-3**) |
| **SP-12** | Review monitoring/log output for identity, character or token data | TC-OPS-05 | **Failed** 2026-08-26 | **Executed 2026-08-26** by the Operations Owner with elevated access, over 5535 journal lines reduced to distinct message shapes with counts summing back to 5535. **No name, character or Discord identity appears anywhere.** But the OAuth authorization code and state are written to the journal in clear text by uvicorn's default access log — **finding N-7**. TC-OPS-05's criterion is that monitoring output contains no token data, so the row **Fails** and I-06 criterion 4 cannot be met until it is remediated and re-observed |
| **SP-13** | Deployed Caddy limit and application limit asserted **equal**, on the general and the snapshot route | TC-LIM-02 | **Not Run** | The repository template carries the intended N-55 values (1 MiB browser routes, 64 MiB submission route) and TC-LIM-01/TC-LIM-06 prove the *application* side automatically. **The deployed proxy configuration has never been read and compared.** Parity is the whole assertion, and half of it is unobserved |
| **SP-14** | Browser-observed security headers and CSP on normal, early and error responses | TC-SEC-07 browser half | **Not Run** | The full N-26 CSP was captured from the deployed `/v1/auth/emergency` response on 2026-08-24 (read: supervised-session B-10) — but as a header read, not a real-browser-engine observation, and not on early or error responses, and TC-SEC-07's specific assertion (the OAuth redirect completing under `form-action 'self'` because a `GET` start is a navigation) was never observed in a browser. Ordinary Discord logins did complete in Chrome that day, which makes the assertion *very likely* true and **is not the same as having observed it** |
| **SP-15** | Representative measurements: 64 MiB refusal, 32-Actor-class preview and apply, worker peak RSS vs N-47 | TC-PERF-01, TC-PERF-02 | **Not Run** (unblocked 2026-08-25 by D-l/D-m) | **Nothing has been measured.** The only real-folder baseline is Phase 2 Rehearsal B (2026-08-09): 32 Actors, 16,287,185 bytes, preview 9.566 s, **preview only — `snapshot_imports` 0, nothing applied**, and the artifact was shredded at teardown. Peak RSS was not sampled then and never has been. N-4 and N-2 are now decided (D-l, D-m), so the remaining prerequisite is N-3's supervised transport step |
| **SP-16** | `/healthz` and a status poll answered **during** a running preview | TC-PERF-03 | **Not Run** (unblocked 2026-08-25) | No observation. Requires a running preview, so it sits behind SP-15's transport prerequisite. **No bound has been stated yet either** — §11.3 requires the bound be recorded *before* the run, and that has not been done. I own drafting it (§7) |
| **SP-17** | Worker restart, lease expiry, lost response, reaper recovery, apply idempotency under the **deployed** configuration | I-06, A-06 | **Not Run** | Every one of these is proved automatically against real PostgreSQL (TC-JOB-02…08, TC-JOB-13, TC-JOB-15/16), and the fence `uq_snapshot_imports_applied_input` is contract-tested. **None has been exercised on the deployed worker**, which has been running for less than a day and has never processed a job |
| **SP-18** | Real-device responsive and 200% zoom inspection at 320/768/1280 | TC-UI-08 | **Not Run** | Peter's own hardware; not available to me by construction. Unchanged |
| **SP-19** | Screen-reader traversal | TC-UI-09 | **Not Run — accepted as permanently Not Run for Phase 3** | Decision D-f (2026-08-23): the Operations Owner confirms no current community member is known to rely on assistive technology and knowingly accepts the residual. **R-23 stays active and this row is never reclassified as passed** |
| **SP-23** *(execution-plan sense)* | Browser-observed rendering at 320/768/1280 and 200% reflow; keyboard traversal, focus order, skip links, HTMX-enhanced and JavaScript-disabled paths, real-engine contrast, reduced motion | TC-UI-01/02, R-23 | **Passed in part; recorded `Not Run` against the full contract** | **Genuinely and well evidenced for the part that ran** (read: supervised-session §3, 2026-08-24, Chrome on macOS 26, deployed staging, operator Peter Duscha): all **seven** required views at 320/768/1280 and 200%; keyboard traversal with visible focus and a keyboard-actuated POST sign-out; a real scriptless browser confirming the truthful no-JavaScript state. **Missing from the contract:** skip links reaching the right landmark, HTMX-**enhanced** paths, `prefers-reduced-motion` in a real engine, real-engine contrast, and the exact Chrome build. One browser on one platform, which is why R-23 stays active regardless |

### 2.3 Rows that are complete

| Row | Status | Evidence |
|---|---|---|
| **TC-BG-02, browser/physical-authenticator half** | **Passed** 2026-08-24 | Read: supervised-session §4, A-3 and A-6. Two distinct enrolled platform passkeys each completed a real assertion in Chrome on macOS 26 against `https://freedom-blades-test.rpgworld.org`, **with the Discord provider genuinely unreachable to the portal** (an `iptables` OUTPUT rule on the portal account's uid, re-proved by the portal getting `000` while the bot under another uid got `200`), each landing exactly on `/v1/admin/role-capabilities`. This retires finding F-16 |
| **SP-21** (recovery grant), **SP-22** (break-glass boundary), **SP-24…SP-26** | **Passed** 2026-08-24/25 | Read: supervised-session §4 and operational addendum §§3, 5.1, 5.5, 5.6. Note the **ID collision at SP-23** — finding N-1 |

---

## 3. A-05 — the ten closure criteria reconciled against literal evidence

| # | Criterion | Status | Literal evidence, or what is missing |
|---|---|---|---|
| 1 | Protected account exists on the intended target host via supported host-local tooling | **Met** | Enrolled through `tools.webauthn_enrollment` on this host; confirmed by the protected operator check (supervised-session B-7: `Enabled credentials: 2 (minimum 2)`) |
| 2 | At least two independent, enabled WebAuthn credentials | **Met** | B-7, plus the A-6 evidence table. Nicknames only; no credential id, public key or COSE material was ever selected |
| 2a | Ceremony RP ID is the intended target host's own hostname, and one credential has authenticated successfully | **Met** | Both credentials completed real assertions against `https://freedom-blades-test.rpgworld.org` (§4 A-3, A-6). The binding was enforced by the authenticator, not asserted from configuration — which is stronger evidence, not weaker |
| 3 | Retirement below two is observed being refused | **Met** 2026-08-25 | Addendum §5.1: refused at `tools/webauthn_enrollment.py:212` **before any write**, exit status `1` (`EXIT_REFUSED`) captured from the shell, re-run and refused identically |
| 4 | ~~Startup and `/healthz` readiness observed both **below** and **at** the threshold~~ → split 2026-08-25 (D-n), **corrected 2026-08-26 (D-o)** | **4a and 4b both Open and executable · 4c is a deployment-gate re-observation** | The below/at pair was executed on the disposable `freedom_dev` (addendum §5.2): both states start normally with byte-identical health bodies under `WEB_ENVIRONMENT=development`. **The production-class half is shown not observable before production exists** (§5.2.1): `WEB_ENVIRONMENT=production` pins the real origin, redirect URI and guild in source, and configuration is refused *before* the lifespan evaluates S-15. C2-1 is now accepted and `break_glass_credentials: true` is live on the deployed portal (O-2) — **acceptance of the health contract is not execution evidence for this criterion**. **Corrected 2026-08-26 (D-o, change-log C-P3.5-U) after Codex Blocking finding B-1.** The 2026-08-25 split moved 4b out of A-05 on the premise that a production-marked process is a publicly exposed one. **It is not:** `run_resource_checks` is a plain function, so S-15's production branch is reachable with no listener, no bind and no route. **4b therefore stays an A-05 closure criterion**, discharged by the guarded exercise **SP-27**; **4c** is a deployment-gate re-observation, defence in depth only. Awaiting the Security Reviewer's confirmation |
| 5 | Emergency login succeeds with Discord simulated unavailable | **Met** | §4 A-2/A-3/A-6, under a genuine provider outage |
| 6 | Break-glass grants Platform Administrator **only** | **Met** | §4 A-4 (operator read the navigation unprompted, offered exactly Role capabilities / My account / Sign out) and SP-22, plus the deployed R-41/R-46 denials — both `403 emergency_surface_refused` **before handler object lookup** (addendum §3) |
| 7 | Limiter, audit, correlation, session expiry, logout/revocation verified | **Met** | SP-26 (addendum §5.6): S-5, S-6, S-7, S-9 all observed behaving on the deployed build; three correlation references shown to the operator, **all three resolve** to audit rows |
| 8 | Host-local recovery grant issued, used once, replay refused, expiry refused, token never recorded | **Met** | SP-21 (supervised-session §4). Grant **record ids** recorded; the token in no form |
| 9 | Custody, replacement, loss and recovery documented without credential material | **Met** 2026-08-25 | `docs/operations/break-glass-credential-custody.md`, **accepted by Peter Duscha** the same day. Acceptance is what closed it, not authorship |
| 4b | S-15's production-class refusal observed **before exposure** (SP-27) | **Met 2026-08-26** | Executed inside a verified network namespace on a disposable `freedom_production` proved empty first, with the acknowledgement guard fired deliberately before anything was seeded. Below the threshold `run_resource_checks` **refused** naming S-15 with `listener none`; at the threshold the same call **passed** — the falsification that makes the refusal mean the credential floor rather than production-marking. Teardown verified. See staging evidence §5G |
| 4a | Startup and `/healthz` observed below and at the N-13 threshold | **Met 2026-08-26** | Executed as M-1b under decision **D-p** on the disposable `freedom_dev`, marked `development`: below the threshold S-15 warns, at it the same call is clean; the live deployed `/healthz` shows `break_glass_credentials: true` under the accepted C2-1 contract. Two limits recorded rather than glossed — no observation under the `staging` marker itself, and no portal observed answering `break_glass_credentials: false`. See staging evidence §5E |
| 10 | **Security Reviewer confirms break-glass readiness** | **Not started — and correctly so** | By its own terms it comes last, after every preceding criterion and disposition is complete. Criterion 4 is the only thing in front of it |

**A-05 disposition: Open — but reduced to one criterion.** *(Updated 2026-08-26.)* Criteria 1, 2, 2a, 3, **4a**, **4b**, 5, 6, 7, 8 and 9 are Met. **Criterion 10 — the Security Reviewer's break-glass readiness confirmation — is the only one outstanding**, and by its own terms it comes last, after every preceding criterion and disposition is complete. Criterion **4c** remains owed at the deployment gate as defence in depth, never as a substitute for 4b.

### 3.1 Criterion 4 — split, approved 2026-08-25 (decision D-n)

**Recorded as decision D-n, change-log C-P3.5-T, approved by Peter Duscha as
accountable Security Reviewer on 2026-08-25.** The criterion's original wording is
retained **struck through rather than deleted** in execution plan §13.2, together
with the rationale, the explicit non-effects and a reversal procedure, so the
change is reviewable and can be undone later. What follows is the analysis that
supported it.

The addendum's §5.2.1 analysis is **confirmed correct** by direct reading today:
`WebEnvironment.is_production` is `PRODUCTION` alone
(`application/web/config.py:431`), and S-15 appends a `ConfigurationProblem` only
`if settings.environment.is_production`, otherwise a `StartupWarning`
(`application/web/startup.py:205-212`). **A staging-marked process cannot produce
S-15's refusal, however it is configured.** The production half of criterion 4 is
genuinely unobservable before production exists.

That creates a **circular dependency**, and naming it is the point: A-05 exists to
gate public exposure, so holding it open on evidence that requires production
configuration to exist means A-05 can never close before the thing it gates. That
is a defect in the criterion's wording, not a finding about the platform.

**Recommendation — split criterion 4 in two, and record both halves:**

| Half | Content | Observable? |
|---|---|---|
| **4a** | Startup behaviour and `/healthz` readiness observed **below** and **at** the N-13 threshold, under `WEB_ENVIRONMENT=staging`, on the deployed build, capturing the S-15 **warning** and the accepted C2-1 `break_glass_credentials` boolean | **Yes — and it is not yet on record.** What exists was taken under `WEB_ENVIRONMENT=development` on a disposable database *before* C2-1 was accepted, so it exercises neither the staging marker nor the accepted health contract |
| **4b** | S-15's production-class **refusal**, observed **before exposure** | **Yes — and this was the error.** `run_resource_checks` is a plain function, so the production branch is reachable with **no listener, no bind and no route**. Discharged by the guarded exercise **SP-27**; **stays an A-05 criterion** |
| **4c** | A deployment-gate **re-observation** | Retained as **defence in depth**, never a substitute for 4b |

**4a is worth re-taking and I can prepare it fully** (C-11): a throwaway portal
process on a spare port against the disposable `freedom_dev`, marked
`WEB_ENVIRONMENT=staging`, with **synthetic** credential records. Real credentials
are never touched — which is exactly why the disposable database was the right
call in §5.2 and remains so. It needs one authorization and about fifteen minutes.

**Applied 2026-08-25, then corrected 2026-08-26 after Codex Blocking finding
B-1.** The analysis above was **wrong in one load-bearing step**: it treated a
production-*marked* process as a publicly *exposed* one. Those are different
events, and the difference is the whole argument. A production-marked exercise can
run with no listener at all, so the circularity it claimed did not exist — and
moving 4b out of A-05 would have **weakened a security precondition** while
appearing to fix one.

**As corrected:** 4a and 4b are **both** A-05 closure criteria, 4b discharged by
the guarded exercise **SP-27** (§13.2); **4c** is a deployment-gate re-observation
retained as defence in depth. **N-13 is unchanged** and retirement below two is
still refused. The correction is recorded as **D-o** / **C-P3.5-U** and awaits the
Security Reviewer's confirmation, because it supersedes a decision he recorded.

---

## 4. A-06 and R-23

### 4.1 A-06 — PostgreSQL as job-queue and limiter substrate

**Status: Open. No representative-operation evidence exists.**

| §13.3 criterion | Status | Evidence |
|---|---|---|
| 1. Measurements under representative staging conditions, co-located bot and Foundry running, observed load recorded | **Not Run** | None |
| 2. Preview/apply durations, peak RSS vs N-47, portal responsiveness, DB pool, cross-process limiter, lease heartbeat/commit fence — each against a bound stated **before** the run | **Not Run** | The limiter half alone has automated evidence: `test_the_limiter_counts_across_processes`, two engines sharing one database enforcing one budget. **No bound has been stated for the others yet** |
| 3. Recovery after interruption produces **exactly one** durable effect | **Not Run** on the deployed worker | Fully proved automatically (TC-JOB-13/15/16, `uq_snapshot_imports_applied_input`). SP-17 is the deployed observation |
| 4. Every input realistically shaped, bounded synthetic data | **Not Run** — unblocked by D-l | The 500-Actor synthetic benchmark's known weakness stands: synthetic Actors ~233× smaller than real ones (RA-5) |
| 5. A missed bound does not close A-06 | — | Standing rule, acknowledged |

**Do not close A-06 without its staging concurrency/restart evidence.** The
handover says so explicitly, and nothing in this inventory tempts otherwise.

### 4.2 R-23 — accessibility residual

**Status: Active accepted residual. Unchanged by this inventory.**

| §13.4 criterion | Status |
|---|---|
| 1. Keyboard-only operation, no traps, visible and logical focus order, skip links | **Partly evidenced** — keyboard traversal and visible focus observed 2026-08-24 on the emergency view and the continuity shell; **skip-link landmark targeting and focus *order* across the full corpus are Not Run** |
| 2. Semantics, headings, labels, descriptions, tables | **Not Run in a browser** — parsed-DOM automation exists and is cited under its contract IDs; the accepted row's level is browser |
| 3. Denied, empty, loading, stale, validation, error states from a real view model | **Partly** — the denial/error view was observed at all widths; the other five states were not exercised individually |
| 4. HTMX-enhanced **and** JavaScript-disabled paths | **Half** — the scriptless path was observed in a real browser (U-5), which is the half that mattered most because F-15 lived there. **HTMX-enhanced paths were not exercised** |
| 5. 320/768/1280 and 200% zoom/reflow | **Passed for TC-UI-01/02** on one browser; **TC-UI-08 Not Run** |
| 6. Real-engine contrast and reduced motion | **Not Run** |
| 7. Screen-reader traversal | **Not Run — permanently, for Phase 3, under D-f** |
| 8. Browser/OS/viewport/zoom/AT recorded for every result | **Met for what ran**, except the exact Chrome build |

**The honest consequence, to be restated in the submission:** the portal would be
exposed without direct evidence that a screen-reader user can complete its
essential workflows. That is a risk Peter accepts knowingly under D-f; it is not
one that was tested away.

---

## 5. The five required P3.5 artifacts

| # | Artifact (§12.1) | State |
|---|---|---|
| 1 | `phase-3-p3-5-readiness-and-execution-plan.md` | **Present** |
| 2 | `phase-3-p3-5-test-and-evidence-traceability.md` (EX-1/EX-2) | **Created 2026-08-26.** 318 contract rows resolved mechanically in both directions; F-1 and N-1 reconciled |
| 3 | `phase-3-p3-5-staging-and-operations-evidence.md` (EX-6) | **Created 2026-08-25/26.** Procedures listed with empty result columns; the EX-3/EX-4 disposable rehearsals and the full verification set are filled in with real results |
| 4 | `phase-3-p3-5-accessibility-and-browser-evidence.md` (EX-7) | **Created 2026-08-26**, with the 2026-08-24 browser results under the accepted numbering and every unmet row recorded as unmet |
| 5 | `phase-3-p3-5-submission.md` (EX-10) | **Absent** |
| 6 | `infra/systemd/freedom-web.service.tmpl`, documented Caddy site block, WebAuthn registration page (EX-5) | **Present** — the unit template, `infra/caddy/freedom-blades-portal.caddy.tmpl`, and `infra/ceremony/passkey-registration.html`. F-2, F-3 and F-7 are discharged |

Artifacts 2–5 are mine and are repository-scoped. Their absence is the reason the
gate disposition lists "the complete P3.5 traceability, staging/operations
evidence, accessibility/browser evidence and final submission" as outstanding
independently of any procedure.

**EX-8's performance fixtures do not exist either.** `tests/benchmark_snapshot_500.py`
is the Phase 2 synthetic benchmark whose Actors are ~233× smaller than real ones —
the very weakness §11.4 requires the P3.5 fixtures to correct.

---

## 6. Findings raised by this inventory

| ID | Finding | Class | Disposition |
|---|---|---|---|
| **N-1** | **`SP-23` names two different procedures.** The execution plan §6.2 defines SP-23 as browser-observed rendering, keyboard traversal, skip links, HTMX, no-JS, contrast and reduced motion. The supervised-session evidence and the operational addendum use **SP-23 for "retirement below two enabled credentials is refused"** (A-05 criterion 3), and add SP-24, SP-25 and SP-26 beyond the plan's SP-01…SP-23 range. Meanwhile the execution plan's *actual* SP-23 content was executed on 2026-08-24 and recorded under the label "§4.2" rather than under its own ID | **Important — traceability.** Nothing is broken and no evidence is invalidated; every observation stands. But the handover forbids a parallel evidence structure, and a gate package in which one procedure ID resolves to two procedures would misreport | I have **not** renumbered anything, because renumbering accepted evidence records is worse than the collision. EX-1 will carry an explicit ID-reconciliation table: plan-SP-23 (browser) vs. evidence-SP-23 (retirement refusal), and will cite the 2026-08-24 browser work under **plan-SP-23**. Flagged for Codex |
| **N-2** *(decided — D-m)* | **TC-PERF-02's three-run method is not executable against one input.** §11.2 asks for apply duration over "three runs". The apply is fenced by `uq_snapshot_imports_applied_input` plus `snapshot_imports.request_key` — by design, run 2 and run 3 against the same snapshot return the already-committed effect as a **duplicate** and measure nothing. Discovering this inside a supervised sitting would waste the sitting | **Important — measurement design.** Not a defect; the fence working is the point | Three options, none of which I may choose alone because two touch data custody: (a) three **distinct** real folder submissions; (b) one real apply plus two bounded-synthetic applies, with the real one reported as n=1 and said so plainly; (c) truncate the staging import tables between runs — an Operations Owner action on staging only. **Decided 2026-08-25 as option (b)** by the Acceptance Authority, recorded as **D-m**: one real apply reported as **n = 1**, plus two bounded-synthetic applies. The real figure is reported as single-sample and never as a median of three |
| **N-3** | **The deployed portal exposes no snapshot-submission route.** The route inventory is R-02…R-49 plus the single M-01 `/static` mount; there is no `/api/v1/snapshots`. Phase 2 ingested snapshots through `tools.snapshot_api` — a `wsgiref` reference server bound to loopback, explicitly documented as "not the production server" — behind a temporary Caddy route that was reverted at teardown | **Important — prerequisite gap for TC-OPS-03 and TC-PERF-01/02.** Not a defect: nothing accepted for Phase 3 promised a portal submission route | SP-11 and SP-15 need a **supervised transport step** before them, following `docs/operations/foundry-snapshot-submission.md`, targeting `freedom_staging` and `/srv/freedom-blades/snapshots`. I will write it as a numbered procedure. It needs Peter for the Foundry side and for any proxy route; **no route is added to the deployed proxy under this package without SG-2** |
| **N-4** *(decided — D-l)* | **The accepted documents conflict on real Foundry data in staging.** Execution plan §8.2 says of Foundry: "**Never `the-guild`. Synthetic snapshot artifacts only**", and §11.4 says "never a real Actor payload". The traceability contract §17 requires TC-PERF-01 to measure "a **real** 32-Actor folder" and TC-PERF-02 to measure "a **real**-folder apply end to end", and the handover repeats that a synthetic Actor apply "is not evidence". §20 says only that real snapshots are never *committed as fixtures* | **Blocking for TC-PERF-01/02 until decided.** This is a data-ownership and privacy decision, and AGENTS.md requires me to stop rather than choose it | **Decided 2026-08-25 by the Data Owner, recorded as D-l:** a real `the-guild` folder may be used as a supervised operational input on `freedom_staging`, under the Rehearsal A/B discipline — never committed, no Actor name, payload or warning text in any artifact, artifact shredded and import tables truncated at teardown. §8.2's synthetic-only rule is superseded **for TC-PERF-01/02 and TC-OPS-03 only** and stands everywhere else. The Data Owner offered either the active or an inactive folder with no preference; **`Characters (active)` is the Technical Lead's choice**, because it is the folder the contract names and the only one with a real baseline (32 Actors, 16,287,185 bytes, 9.566 s). The inactive folder is submitted as well only if it holds more than 32 Actors |
| **N-5** | **`freedom_staging` is owned by `foundry`**, the same role that owns `freedom_dev` and `freedom_test`, rather than by a dedicated staging owner role as SP-01 specifies (O-3, O-5, O-6) | **Minor — separation of duties.** The security-relevant half is right: the **runtime** role `freedomweb` is separate, login-capable, and holds `arw` with no DDL. A shared *owner* is a weaker boundary than the procedure asks for, not an exposure | Record as a deviation in the staging evidence artifact rather than repair it silently. Repairing it means a `REASSIGN OWNED`/`ALTER DATABASE OWNER` against a live staging database and is Peter's to authorize if he wants it. **I recommend recording the deviation and leaving it**, because the control that matters is intact |

| **N-6** *(raised and corrected 2026-08-25/26)* | **Stale bytecode from the filesystem cutover named a directory that no longer exists.** The cutover moved the repository by same-host rename; `mv` preserves mtime and size, the two values CPython uses to decide a `.pyc` is current, so **163 cached `.pyc` files under `tests/` still carried `/opt/discord-bots/freedom-bot` as their `co_filename`** — a path that no longer exists. Six web-suite tests failed with `OSError: could not get source code`, and every displayed test path named the vanished tree | **Important — evidence hygiene.** The six failures were **not** product defects, and traceback and source paths in any run taken from this host between the cutover and the correction name a tree a reviewer cannot resolve | **Corrected.** All 24 `__pycache__` directories removed after confirming with `git check-ignore` that they are untracked and ignored; `git status` unchanged. The suite then ran **2339 passed, 0 failed** with correct paths. No source, test or document was changed. Recorded in full in `phase-3-p3-5-staging-and-operations-evidence.md` §5. Raised for Codex |

| **N-7** *(raised 2026-08-26 by SP-12)* | **The OAuth authorization code and state are written to the systemd journal in clear text.** Uvicorn is started with no `--no-access-log` and no log configuration, so its default access logger writes the whole request line including the query string. R-04 `/auth/discord/callback` is the one route that receives credentials as query parameters, because that is how the provider redirects. The application's own logging is clean — it writes only variable-naming startup warnings and correlation-plus-path failure lines | **Important — security / operational disclosure. TC-OPS-05 fails.** Not an emergency: the observed codes are spent, the flow is PKCE-bound so a code alone cannot be exchanged, and the journal is readable only by root and `adm`/`systemd-journal`. **No client secret, cookie, CSRF token, recovery grant or WebAuthn material appears; no rotation is indicated.** But the criterion is that monitoring carries **no** token data, and the same configuration would behave identically in production, where both the population with journal access and the value of a code are larger | **Remediated in the repository 2026-08-26, not yet deployed.** `tools/portal_server.py` installs a `uvicorn.access` filter replacing the query string with `?<redacted>`; the route stays identifiable, the credential does not survive. **The unit file is unchanged**, so deployment is a service restart rather than unit surgery. **59 regression tests** (20 at the first review; 27 after Codex finding I-1; 59 after Codex's re-review of I-1 reproduced a leak through a **list** of log-record arguments) including falsifications that reproduce each leak before preventing it, plus an end-to-end proof against a real running uvicorn. The fallback no longer inspects argument structure: an unrecognised record is rendered and its **text** redacted, so no character after the first `?` survives whatever container carried it. **TC-OPS-05 stays `Failed` until the fix is deployed and SP-12 re-run.** Full account in `phase-3-p3-5-staging-and-operations-evidence.md` §5.2 |

| **N-8** *(raised 2026-08-26 by EX-1)* | **Five accepted contract rows carry no citation that resolves in either direction** — TC-AUTH-17, TC-BG-19, TC-MIG-19, TC-MIG-21, TC-MIG-28. Found by resolving all 318 rows mechanically against the tests that actually exist | **Minor — traceability. No requirement is untested:** each of the five was chased individually and each has a passing test, generally named after its subject rather than its contract ID. The defect is that the contract cannot be verified end to end by anyone who does not already know where the tests are, which is the property a traceability contract exists to remove | Citations supplied in `phase-3-p3-5-test-and-evidence-traceability.md` §2.1. **The accepted contract is not edited**; folding them back into it is an Acceptance Authority decision after review |

**No blocking security, authorization, identity, atomicity, data-integrity,
recovery or reliability finding was identified by this inventory.** That statement
is scoped to a read-only inspection and the reading of existing artifacts. It is
not a substitute for Codex's two passes.

---

## 7. Preparation I will complete independently, before any sitting

All repository-scoped or disposable-database-scoped. Released by SG-1; none of it
mutates staging, production, the proxy, a service or a credential.

| # | Work | Produces | Blocked by |
|---|---|---|---|
| ~~**C-1**~~ **Done 2026-08-26** | EX-1/EX-2: the final requirements-to-evidence traceability across P3.0–P3.4, every delivery-plan §11 row and every implementation-plan §12 mandatory test expanded to exact node IDs and procedure IDs, **including the F-1 TC-UI relabelling and the N-1 SP-23 reconciliation** | Artifact 2 | — |
| ~~**C-2**~~ **Done 2026-08-26** | EX-6/EX-7: the staging/operations and accessibility/browser evidence artifacts, written with their procedures and **empty result columns**, pre-loaded with the evidence §2 and §3 already credit | Artifacts 3 and 4 | — |
| ~~**C-3**~~ **Done 2026-08-25/26** | EX-3: migration rehearsal on `freedom_test` — `upgrade head` → `downgrade` across the P3.3 boundary → `upgrade head`, runtime grants re-applied and re-verified, compared against `0013`'s documented rollback boundary and `0006`/`0009`'s documented costs | TC-OPS-02, disposable half | — |
| ~~**C-4**~~ **Done 2026-08-25/26** | EX-4: `infra/postgresql/backup-restore-drill.sh freedom_test <workdir>` — backup, checksum, destroy, restore, **table-and-row inventory comparison** | TC-OPS-02, disposable half | after C-3 |
| ~~**C-5**~~ **Done 2026-08-26** | EX-8: bounded synthetic fixtures **shaped to the real size distribution** — a 32-Actor-class folder at ~16 MB (Rehearsal B's real shape) and a worst case at the N-20 64 MiB bound. Generated at run time, never committed | TC-PERF-01/02 synthetic halves | `tests/perf_snapshot_fixtures.py` + 12 tests. Three profiles: `folder-32` (32 Actors, 16,287,681 bytes — within 496 bytes of Rehearsal B's real 16,287,185), `bound` (131 Actors, 66,676,206 bytes, 99.4% of N-20) and `over-bound` (67,185,181 bytes, for the refusal). **The byte bound binds long before N-20's 500-Actor bound** once Actors are real-sized, which is worth knowing before the sitting |
| ~~**C-6**~~ **Done 2026-08-26** | The RSS sampling and wall-clock measurement harness for SP-15/SP-16, and the **written-in-advance bounds** for TC-PERF-03 and for portal responsiveness, recorded **before** any run per §11.3 | SP-15, SP-16 method | `tools/snapshot_perf_harness.py` + 11 tests. Peak memory is read from the kernel's own `VmHWM` high-water mark rather than sampled, so no peak can fall between two samples. **Three of the five bounds are already accepted policy** (N-47, N-45, C-11's throughput) and are cited; the two latency bounds have **no accepted figure anywhere** and are marked `PROPOSED`, needing acceptance before the run they judge |
| ~~**C-7**~~ **Done 2026-08-26** | The supervised snapshot-transport procedure for N-3, targeting `freedom_staging`, with teardown and shredding steps | SP-11, SP-15 prerequisite | `phase-3-p3-5-supervised-run-sheets.md` §1, as new procedure **SP-28**. Two routes offered; **route B recommended** — the module's download fallback plus a host-local loopback POST, which needs **no proxy mutation**. What route B does not evidence is stated rather than left implicit |
| ~~**C-8**~~ **Done 2026-08-26** | A proposed extension of the drill script's target guard to `freedom_staging`, as a reviewable diff with its own falsifying test — **not applied** | SP-10 | `phase-3-p3-5-c8-staging-drill-guard-proposal.md`: a two-signal guard extension with three falsifying tests, **not applied**. Raised as finding **N-11** — the script refuses staging by design, so SP-10 has no instrument until Peter chooses route A or B |
| ~~**C-9**~~ **Done 2026-08-26** | The click-by-click run sheets for each sitting in §8, written to the §2 audience rule: literal, what to type, what to expect, no configuration file or protocol term to interpret | every sitting | `phase-3-p3-5-supervised-run-sheets.md` §§2–12, twelve sittings, including the literal per-refusal edit table for SP-08's S-01…S-15 |
| ~~**C-11**~~ **Done 2026-08-26, and it found a defect** | The criterion-4a observation harness: a throwaway `WEB_ENVIRONMENT=staging` portal process against disposable `freedom_dev` with synthetic credential records, below and at the N-13 threshold, capturing the startup warning and the `/healthz` `break_glass_credentials` boolean | A-05 criterion 4a | `tools/breakglass_observation.py` + 15 tests. **The criterion as written is not executable — finding N-10.** Each environment is bound to exactly one database name, so a staging-marked process must target `freedom_staging`, the deployed database holding the two **real** credentials the criterion forbids touching. Verified by observing S-01 refuse, not by reading the rule. The harness refuses `staging` outright and says why; the disposition is the Security Reviewer's |
| ~~**C-12**~~ **Done 2026-08-26** | The **SP-27** harness: production-marked settings from identifiers only, a guarded disposable `freedom_production` seeded with synthetic credentials, a direct `run_resource_checks` call, and a scripted teardown that drops the database and removes the egress rule | A-05 criterion 4b | Same module. The production branch is proved to fire in a test — below the threshold `run_resource_checks` refuses naming **S-15**, at it the same call passes, which is the falsification that shows the refusal is the threshold and not production-marking itself. **Guards falsified rather than asserted:** no acknowledgement, a non-empty database, a foreign credential and a database this harness did not prepare are each made to refuse |
| **C-10** | EX-9: full suites serially against the disposable database, all available checks, manifests, `git diff --check`, every skip and warning explained | submission §validation | last |

**Standing constraint (F-6):** the two pytest suites share the single disposable
`freedom_test` database and must never run concurrently.

**Standing condition (E-9):** no formatter, linter or type checker is configured
in this repository. That is recorded as **unavailable**, never as passed, and P3.5
does not introduce one as a drive-by change.

---

## 8. The smallest maintainer-attended sessions

Decomposed into ~30-minute units per decision D-g. **Each is a proposal; none is
scheduled and none is authorized.** SG-2 covers M-1…M-7; the A-05 remainder needs
no new SG-3 because the ceremony is done.

| # | Sitting | Procedures | Peter does | Attended | Preconditions |
|---|---|---|---|---|---|
| **M-1** | Prerequisite attestation and monitoring | SP-02, SP-03, SP-12 (TC-OPS-05) | States that staging secrets share no value with production; reads out the staging Discord application/guild/role **IDs**; runs the journal review with elevated access while I say what to look for | **~25 min** | None beyond his console |
| **M-2** | Kill switch | SP-09 (TC-OPS-01) | Engages layer 1, we confirm every route `503` except `/healthz` and `/static/*`, confirms the **bot and Foundry are unaffected**, releases | **~25 min** | Write access under `/srv/freedom-blades/web`. Bot and Foundry must be up so "unaffected" means something |
| **M-3** | Deployed refusals and limit parity | SP-08 (TC-OPS-04), SP-13 (TC-LIM-02) | Restarts the portal with each deliberately wrong value in turn and reads the refusal; reads the **deployed** Caddy limits so we compare them to the application's | **~30 min** | Portal restartable. **Each refusal leaves the portal down until the value is restored** — the stop condition below matters here |
| **M-4** | Backup, restore, rollback on staging | SP-10 (TC-OPS-02 staging half) | Acts as Operations Owner: pre-migration backup, `upgrade`→`downgrade`→`upgrade`, restore, inventory comparison | **~30 min** | C-3, C-4 and C-8 done first. **A pre-migration backup is taken before the rehearsed migration**, so a failed downgrade is recoverable |
| **M-5** | Browser observations | SP-14 (TC-SEC-07 browser half), plan-SP-23 remainder | Drives his own browser: headers/CSP on normal, early and error responses; the OAuth redirect under `form-action 'self'`; skip links, HTMX paths, reduced motion, real-engine contrast; **records the exact Chrome build this time** | **~30 min** | His workstation. Screenshots synthetic-only, reviewed individually |
| **M-6** | Real device | SP-18 (TC-UI-08) | Inspects at 320/768/1280 and 200% on his own hardware, records device model and OS | **~15 min** | His device. Can ride along with M-5 |
| **M-7a** | Snapshot transport | C-7's procedure | Foundry side of a supervised submission of `Characters (active)` into `freedom_staging`; reads out the inactive folder's Actor count from the selection dialog | **~30 min** | **Unblocked 2026-08-25 (D-l).** Needs C-7 and SG-2 |
| **M-7b** | End-to-end flow | SP-11 (TC-OPS-03) | OAuth login → member read → Council link change → folder selection → preview → confirm → audit search, in his browser | **~30 min** | M-7a |
| **M-7c** | Performance | SP-15 (TC-PERF-01/02), SP-16 (TC-PERF-03) | Authorizes; I drive the measurement and sample RSS while the bot and Foundry run | **~30 min** | M-7a; C-5, C-6; **bounds written down first**. Apply is n = 1 real plus two synthetic (D-m) |
| **M-7d** | Worker recovery | SP-17 | Authorizes SIGTERM mid-attempt; we observe lease expiry, reaper requeue, lost response and a retry returning the committed effect as a duplicate | **~25 min** | M-7a |
| **M-1b** | A-05 criterion 4a re-take | criterion 4a | Authorizes a **second, throwaway portal process** on a spare port against the disposable `freedom_dev`, marked `WEB_ENVIRONMENT=staging`, with synthetic credential records. No staging or production mutation; the deployed portal is untouched | **~15 min** | C-11. Real credentials are never touched — that is what makes it safe and what forced the disposable database in the first place |
| **M-1c** | A-05 criterion 4b — **SP-27** | criterion 4b | Authorizes and supervises the guarded pre-exposure exercise: disposable `freedom_production` with **synthetic** credentials, egress blocked, `run_resource_checks` called directly so **no socket is opened**, then full teardown | **~20 min** | C-12. No production service, no real data |
| **M-8** | A-05 close-out | criterion 10 | Confirms the D-o correction (§3.1); then, after everything above, the break-glass-readiness confirmation | **~20 min** | Everything else complete |

**Total attended time: roughly 4.5 hours across ten sittings**, of which
**M-7a…M-7d (about two hours) are blocked behind one decision** — N-4.

### 8.1 Proposed order

1. ~~**N-4 and N-2 decisions**~~ — **both taken 2026-08-25**, recorded as **D-l**
   and **D-m** in the execution plan §0.2. Nothing in the remaining work is
   blocked on a decision except A-05 criterion 4's wording (§3.1).
2. **C-1…C-6, C-8, C-9, C-11** — my independent preparation, in parallel.
3. **M-1, M-2, M-3** — cheapest, unblocked, and M-3 retires the largest single
   `Not Run` cluster (TC-OPS-04 plus TC-LIM-02).
4. **M-4** after C-3/C-4/C-8.
5. **M-5 + M-6** together, one evening at his workstation.
6. **M-7a → M-7b → M-7c → M-7d**, in that order. M-7a is a hard prerequisite for
   the other three. **M-1b** rides along with any of the earlier sittings.
7. **C-10** — full suites and all available checks, after the last remediation.
8. **EX-10** submission → **EX-11/EX-12** Codex's two passes → **EX-13**
   remediation and re-review → **M-8** → **EX-14**, Peter's gate decision, alone.

### 8.2 Environment and safety preconditions, standing for every sitting

- Staging only. `WEB_ENVIRONMENT=staging`, loopback bind, behind the accepted
  proxy boundary and the operator-address restriction.
- **No production database, no production backup, no real player data beyond what
  N-4 may authorize under Data Owner supervision.**
- No secret, credential, token, token hash, public key, COSE blob, cookie, CSRF
  value or raw address is read, printed, pasted or committed. Peter is never asked
  to paste a credential or secret into chat or a file.
- Every artifact passes the §8.3 ten-point redaction checklist before it is
  written, and `git diff --check` plus a manual diff read before any commit.
- The bot and Foundry stay running throughout the performance work, because that
  is the real condition (R-24), and the observed load is recorded alongside.
- The filesystem rollback/observation hold stands: **nothing under
  `/opt/discord-bots` is deleted** without a separate Operations Owner release.

### 8.3 Stop and rollback conditions

**Stop the sitting and report** if any of these occurs:

| Condition | Action |
|---|---|
| A deliberately-wrong-value restart (M-3) leaves the portal down and the correct value does not bring it back | Restore from the pre-change copy of the environment file; if that fails, engage the kill switch and stop. The portal being down is recoverable; a half-configured portal serving requests is not |
| The staging downgrade (M-4) fails or leaves the schema inconsistent | Restore from the pre-migration backup taken at the start of that sitting. Do not attempt a forward repair inside the sitting |
| Worker peak RSS approaches or exceeds N-47's 1 GiB | **That is a finding, not a reason to raise N-47.** Record it, stop, and route the numeric-policy question through delivery-plan §7 change control and security review |
| Any measurement misses a bound stated in advance | A-06 does **not** close. Record the miss with the bound as written before the run |
| Backup, restore, rollback or recovery does not meet its accepted result | Stop. This is an I-06 blocker and a gate-blocking outcome, not a retryable step |
| A real Actor name, payload, warning text or player datum would have to enter an artifact | Stop before writing it. Redact at source, not afterwards |
| A browser, device or credential precondition turns out to be unavailable | The row stays **Not Run**. **An unavailable check keeps the gate open; it is not a waiver** |
| Anything would require a change to architecture, authority, privacy, data ownership, production behavior, migration/rollback strategy or an accepted numeric contract | Stop and ask. I do not choose silently |

---

## 9. What this document does not do

- It closes **no** RAID item. I-06, A-05 and A-06 remain **Open**; R-23 remains
  **Active**.
- It requests **no** gate decision, and no gate decision may be inferred from it.
- It authorizes **no** staging mutation, no privileged action and no credential
  action. SG-2 and SG-3 are unrequested here.
- It starts **no** Phase 4 work of any kind.
- It converts **no** partial observation into a pass.

## 10. What is needed, and from whom

**Resolved 2026-08-25, and no longer outstanding:**

1. ~~**N-4, Data Owner** — real Foundry folder in staging.~~ **Approved**, recorded
   as **D-l**. `Characters (active)` is the primary folder; the inactive folder is
   submitted as well only if it holds more than 32 Actors.
2. ~~**N-2, Acceptance Authority** — TC-PERF-02 repeat runs.~~ **Option (b)**,
   recorded as **D-m**. The real apply is reported as **n = 1**.

**Still needed:**

3. **Peter, Operations Owner — SG-2.** Authorization for M-1…M-7: the staging
   build, kill-switch, deliberate-refusal, backup/rollback, browser, transport,
   end-to-end, performance and worker-recovery sittings. **This is now the only
   thing gating execution of every remaining I-06 procedure.**
4. **Peter — availability windows (P-7).** Turns §8's effort into a forecast. No
   calendar date is committed until he records them.
5. **Peter, Operations Owner — one bounded extra authorization** for M-1b: a
   throwaway portal process on a spare port against the disposable `freedom_dev`.
   No staging or production mutation; the deployed portal is untouched.
6. **Peter, Security Reviewer — confirm the D-o correction.** The 2026-08-25
   split (D-n) was corrected on 2026-08-26 after Codex Blocking finding B-1:
   4b **returns to A-05** rather than moving to the deployment gate. The
   correction **re-imposes** a control the earlier decision relaxed, so it is
   implemented rather than held — but it supersedes a decision he recorded and is
   not treated as decided until he confirms it. Change-log **C-P3.5-U**.
7. **Peter, Security Reviewer — A-05 criterion 10**, last, after everything else.
8. **Peter, Acceptance Authority — the Phase 3 gate**, after both Codex passes.
   Alone.

No secret, credential, token, public key, raw address or unnecessary identity
datum was read or recorded in producing this inventory. No service, database,
configuration or file outside this document was mutated.
