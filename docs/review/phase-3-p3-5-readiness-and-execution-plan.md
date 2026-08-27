# P3.5 readiness and execution plan — Phase integration and authentication/security gate package

**Prepared:** 2026-08-23 by Claude, P3.5 backend/integration Technical Lead

**Status:** **SG-1 approved by Peter Duscha on 2026-08-23**, together with the
P-2 browser decision. Repository-scoped execution (EX-1…EX-9) is released. **SG-2
and SG-3 remain unapproved**: no staging mutation, no credential ceremony and no
external action is authorized by this document.

**Baselines:** `docs/implementation-plan.md` v1.5 · `docs/review/phase-3-delivery-plan.md`
(accepted 2026-08-13) §§5 P3.5, 6, 7, 10, 11, 13 · `docs/contracts/phase-3-test-traceability.md`
§§16, 17, 20 · `docs/review/phase-3-p3-4-step-13-final-independent-reviews-and-acceptance.md`

**Predecessor:** P3.4 and Step 13 accepted by Peter Duscha on 2026-08-23; stop
gate P3.G4 closed; P3.5 released for planning and gate-evidence work.

---

## 0. What this document is, and what it is not

This is the **first-run readiness audit and execution plan** required by the P3.5
handover. It was produced from a **read-only** inspection of the repository and
this host, plus the safe local checks recorded in §5. It changes no application
code, no schema, no configuration and no RAID disposition.

It is **not** a claim that any staging, browser, device, assistive-technology,
performance or operational check has been performed. Every such row below is
`Planned` or `Blocked`, and §13 states exactly what would make each one closable.

**Nothing in this plan authorizes itself.** Stop gate SG-1 (§12.2) is Peter's
approval of this document; SG-2 and SG-3 are separate authorizations for host
mutation and for the credential ceremony.

### 0.1 Where each required plan item lives

| Required item | Section |
|---|---|
| 1. Scope and exclusions | §1 |
| 2. Owners | §2 |
| 3. Estimate, confidence and contingency reconciled with the accepted 3/5/8-day range | §3 |
| 4. Environment and dependency readiness matrix | §4 |
| 5. Peter's authority and participation checkpoints | §16 |
| 6. Requirement-to-test/evidence matrix with literal commands or named manual procedures | §7 (with §5 for what was actually run today, and §6.2 for the procedure IDs) |
| 7. Staging topology, isolation and secret-redaction checklist | §8.1–§8.3 |
| 8. Backup, restore, rollback and recovery design | §8.4 |
| 9. Browser, device and accessibility plan | §10 |
| 10. Performance and resource plan | §11 |
| 11. Artifacts, stop gates and acceptance criteria | §12 |
| 12. Exact closure criteria for I-06, A-05, A-06 and R-23 | §13 |


### 0.2 Decisions recorded since issue

| Checkpoint | Decision | Date | Effect |
|---|---|---|---|
| **P-1 — SG-1** | **Approved.** | 2026-08-23 | Releases EX-1…EX-9, repository-scoped only. Closes no RAID item and authorizes no host action. |
| **P-2 — browser** | **Approved as recommended: Peter's own workstation browser**, against the staging loopback. | 2026-08-23 | **No headless-browser dependency is added to this repository.** TC-UI-01/02, TC-SEC-07's browser half and the WebAuthn registration ceremony are performed by a person driving a real browser, and each result records browser/OS/viewport/zoom/AT identity (§10.3). |
| **D-a — staging address** | **Real hostname with TLS**, `WEB_ENVIRONMENT=staging`, **access restricted to the Operations Owner's addresses**, staging site block in its own imported Caddy file. | 2026-08-23 | Settled largely by the code: outside development, `config.py` requires an **https** public origin and refuses `WEB_COOKIE_SECURE=false` (S-03), so a loopback-http staging environment could only run marked `development` and would forfeit the environment-marker and fail-closed evidence SP-08 exists to produce. Restriction answers the residual exposure risk — Certificate Transparency publishes any issued hostname within minutes, so obscurity is not a control. |
| **D-b — A-05 target** | ~~Two ceremonies against two hostnames.~~ **Superseded the same day by D-h.** | 2026-08-23 | Overtaken by the decision to test on the production hostname. |
| **D-c — names and ports** | Database `freedom_staging`; separate owner role and separate restricted login role; portal on `127.0.0.1:8001`, reachable only through the proxy. | 2026-08-23 | Technical convention; decided by the Technical Lead rather than referred to the Sponsor. |
| **D-d — service account** | A **dedicated system user for the portal and worker**, separate from the bot's `discordbot` account, holding group read on the repository and the web virtualenv. | 2026-08-23 | The portal should not run as the account that owns the bot's files and environment. Reversible if it complicates the deployment. |
| **D-e — break-glass credential type** | **Platform passkeys, not purchased hardware.** Two independent WebAuthn credentials — e.g. a phone passkey and a laptop/password-manager passkey. | 2026-08-23 | N-60 requires user verification and permits `attestation: none`; a platform authenticator satisfies both. The accepted contract says "at least two pre-enrolled WebAuthn/passkey credentials", never "hardware tokens". No purchase is required and no accepted control is weakened. |
| **D-f — TC-UI-09 screen-reader traversal** | **Accepted as permanently Not Run for Phase 3**, with the production-readiness consequence stated in the submission. | 2026-08-23 | The Operations Owner confirms no current community member is known to rely on assistive technology, and knowingly accepts the residual. **R-23 stays active**; the row is never reclassified as passed. |
| **D-g — Operations Owner availability** | Most evenings, approximately 30 minutes per session. | 2026-08-23 | Procedures must be decomposable into ~30-minute units; no step may assume a continuous multi-hour window. |
| **D-h — test address** | ~~Test on the production hostname.~~ **Refused by the application and superseded by D-j.** Originally: test on `freedom-blades.rpgworld.org`, with a **separate disposable database** and a **separate Discord application and test guild** behind it, access restricted to the Operations Owner until the gate passes. Supersedes the `staging.` sub-domain proposal. | 2026-08-23 | The environment separations the plan actually requires (§8.2) are database, Discord identity, secrets and data — **not hostname**. Testing on the production name makes every TLS, cookie, header, CSP and OAuth-redirect observation exactly what ships, matches the accepted N-01/N-02 origin and redirect contract literally, and **eliminates F-8's relying-party trap**. Nothing is served at that address today and it is unannounced. |
| **D-i — Cloudflare mode** | ~~DNS-only ("grey cloud").~~ **Corrected the same day to proxied ("orange") in both testing and production** (F-10). | 2026-08-23 | Proxied mode puts Cloudflare's address in the right-most `X-Forwarded-For` entry, which is the one N-34 trusts, so the per-address authentication limiter (N-30/N-31) would count every visitor as one. **The correction:** the host's TLS is a Cloudflare **Origin CA** wildcard, trusted by Cloudflare and by nothing else, so a DNS-only record would fail in every browser. Proxied is therefore mandatory, and the true-visitor-address rewrite is a *testing* requirement, not a go-live one. It is implemented in `infra/caddy/freedom-blades-portal.caddy.tmpl`. |
| **D-j — test address, corrected** | **`freedom-blades-test.rpgworld.org`** with `WEB_ENVIRONMENT=staging`. Production keeps `freedom-blades.rpgworld.org` with `WEB_ENVIRONMENT=production`. | 2026-08-23 | **D-h was not a free choice: S-02 refuses it.** A non-production process claiming the accepted production origin (N-01) is refused at startup, because it would receive production cookies and OAuth callbacks — verified by observing the refusal, not by reading the rule. One label under `rpgworld.org`, so the existing `*.rpgworld.org` origin certificate covers it with no new certificate. **Cost:** F-8 returns in its original form — passkeys enrolled at the test address are bound to that relying-party identifier and cannot authenticate against production, so go-live needs a second ten-minute browser ceremony rather than a copy-paste. A-05's criterion 2a stands as written. |
| **D-k — `/v1` URL prefix** | **Retained unchanged.** | 2026-08-23 | Questioned by the Acceptance Authority on first use and resolved in favour of the accepted contract. The prefix is not cosmetic: `/v1/*` is the browser boundary (cookie sessions, CSRF, HTML) and `/api/v1/*` the machine boundary (service principals, no cookies), so the path states which authentication model applies — and the deployed Foundry module 1.0.7 has its submission path compiled in. Changing it would touch 22 routes across 66 files **and reopen P3.0–P3.4**, whose route inventory is accepted gate evidence. R-04 `/auth/discord/callback` remains the one deliberate exception, fixed by N-02 because it is registered at the provider. |
| **D-l — real Foundry data in staging** | **Approved by Peter Duscha, Data Owner.** A real `the-guild` Actor folder may be submitted to `freedom_staging` as a **supervised operational input** for TC-PERF-01/02 and TC-OPS-03. The Operations Owner noted the payload is character-sheet data only, and offered either the active or an inactive-characters folder, expressing no preference. | 2026-08-25 | **Resolves the §8.2 / §17 conflict recorded as inventory finding N-4.** §8.2's "synthetic snapshot artifacts only" is superseded **for the named performance and end-to-end procedures only**; it stands unchanged everywhere else. The Rehearsal A/B discipline binds: never committed, no Actor name, payload or warning text in any artifact, artifact shredded and staging import tables truncated at teardown. **Technical Lead's decision on which folder, taken under the §2 audience rule:** `Characters (active)` is the primary, because it is the folder the traceability contract names and the only one carrying a real baseline (32 Actors, 16,287,185 bytes, preview 9.566 s, Rehearsal B). The inactive folder is submitted **as well** only if its Actor count exceeds 32, in which case it is a free second real data point closer to the N-20 bound; its count is read from the folder-selection dialog during M-7a, not requested separately. |
| **D-m — TC-PERF-02 repeat runs** | **Option (b), as recommended.** One **real**-folder apply, reported honestly as **n = 1**, plus two **bounded-synthetic** applies for repeatability. | 2026-08-25 | **Resolves inventory finding N-2.** §11.2's "three runs" cannot be satisfied against one input: `uq_snapshot_imports_applied_input` and `snapshot_imports.request_key` make runs 2 and 3 return the already-committed effect as a duplicate — the fence working as designed. The real measurement is therefore single-sample and **must be reported as single-sample**, never as a median of three. Variance is carried by the synthetic pair, whose shape is stated with the measurement so a reviewer can judge it (§11.4). |
| **D-n — A-05 criterion 4** | ~~Split approved by Peter Duscha, accountable Security Reviewer.~~ **The 4b half was superseded on 2026-08-26 by D-o**, after Codex Blocking finding B-1; 4a stands. Recorded unaltered below because it is the decision as taken. Criterion 4 becomes **4a** (startup and `/healthz` observed below and at the N-13 threshold under `WEB_ENVIRONMENT=staging`, on a disposable database with synthetic credential records) and **4b** (S-15's production refusal, **moved to the deployment gate**, not an A-05 closure criterion). | 2026-08-25 | **Resolves the criterion-4 circularity carried unresolved since the 2026-08-24 addendum §8 item 6.** Verified in code rather than assumed: `WebEnvironment.is_production` is `PRODUCTION` alone (`config.py:431`) and S-15 refuses only in production (`startup.py:205-212`), so no staging-marked process can observe the refusal; and `WEB_ENVIRONMENT=production` is itself refused on this host by S-02/S-05/S-07 before the lifespan runs. A-05 gates exposure, so a criterion satisfiable only after exposure can never close. **Full text, rationale, non-effects and the reversal procedure are in §13.2 criterion 4, amended by addition with the original wording struck through rather than deleted.** N-13 is unchanged; nothing is waived; 4b is owed at the deployment gate. |
| **D-o — A-05 criterion 4, corrected** | **Supersedes D-n's 4b half after Codex Blocking finding B-1.** **4b stays an A-05 closure criterion**, discharged by the new guarded exercise **SP-27**; the deployment-gate check becomes **4c**, defence in depth and never a substitute. 4a is unchanged. **Implemented, and CONFIRMED by Peter Duscha as Security Reviewer on 2026-08-26.** | 2026-08-26 | **D-n rested on a false premise: it treated "production-marked" and "publicly exposed" as the same event.** They are not — `run_resource_checks` is a plain function (`application/web/startup.py:80`), so S-15's production branch is reachable with **no listener, no bind and no route**, and S-02/S-05/S-07 make such an exercise more controlled rather than public. D-n therefore **weakened a security precondition** while appearing to resolve a circularity that did not exist, and left operational contract §7 item 10 contradicting item 9. Corrected in §13.2 criterion 4, with §7 items 9 and 10 now reconciled explicitly. Full account in change-log **C-P3.5-U**. |
| **P-3 — SG-2** | **GRANTED by Peter Duscha, Operations Owner.** | 2026-08-26 | Releases SP-01…SP-06, SP-08…SP-19, SP-28 and plan-SP-23 — every remaining I-06 procedure. Granted together with a specific authorization to **deploy the reviewed N-7 fix by service restart** and re-run **SP-12** over a fresh journal interval, and to run **SP-27** as written. Requested in `phase-3-p3-5-authority-request-2026-08-26.md`. |
| **P-4 — SG-3 extension** | **GRANTED by Peter Duscha, Operations Owner**, with his presence for every assigned step. | 2026-08-26 | The 2026-08-24 SG-3 grant and its ceremony (SP-07, SP-20…SP-22) stand and are not repeated. This extension covers only **M-1b** (criterion 4a) and **M-1c/SP-27** (criterion 4b), both on disposable databases with **synthetic** credential records. No real credential is manipulated. |
| **P-5 — second N-7/N-13 deployment** | **AUTHORIZED by Peter Duscha, Operations Owner**, choosing option A. | 2026-08-26 | Deploys the **N-13** remediation — the keyed client-address pseudonym — by a second service restart, followed by a second fresh-interval **SP-12** re-run. **Distinct from C-P3.5-V item 4**, which authorized only the *reviewed* N-7 fix; this code has **not** been seen by Codex, and that was stated when the option was put. Chosen over deferral because the nine remaining sittings would otherwise write many more prohibited plaintext addresses into the journal before the fix landed. **Rollback limitation recorded rather than glossed:** the only saved rollback is the **pre-N-7** build, so restoring it would reinstate the credential leak; the primary recovery path is therefore forward, supported by a clean import under the runtime interpreter and 68 passing regression tests. |
| **D-s — the two performance latency bounds** | **Accepted as proposed by Peter Duscha, Acceptance Authority.** `/healthz` p95 ≤ 500 ms and max ≤ 2000 ms; job-status poll p95 ≤ 1000 ms and max ≤ 3000 ms, both while a preview is running. | 2026-08-26 | §11.3 requires every bound to be stated before the run it judges. Three of the five are accepted policy (N-47, N-45, C-11's throughput) and were cited; **these two had no accepted figure anywhere**. They are **tripwires for a design assumption, not speed targets**: the worker is a separate process at N-41 concurrency 1, so a preview should barely touch the portal, and a miss would mean it *is* blocking — an architectural problem. **Accepted with the explicit condition that a miss is investigated, never relaxed.** Applied to `tools/snapshot_perf_harness.py`, which now prints them as `ACCEPTED`; the test asserting they were `proposed` was rewritten so the guard that flags an unaccepted bound survives. Change-log **C-P3.5-W**. |
| **D-r — the staging gate-off window** | **Option 1, approved by Peter Duscha, Operations Owner.** A **tightly bounded** window with the Caddy `basic_auth` gate removed, covering M-5, M-6 and the M-7 block, the gate restored immediately afterwards, **both times recorded**. | 2026-08-26 | **Resolves finding N-14.** The deployed site file already required it — a `401` in front of the application is not the response the accepted contract describes, and TC-SEC-07 must observe the application's own answers (`infra/caddy/freedom-blades-test.caddy:24-26`). Without it, M-5's early-response case would have recorded **Caddy's** answer as the application's, and a mid-flight challenge could have corrupted the M-7b apply or the M-7c measurement. **What is accepted:** for the window's duration the staging build is reachable by anyone who knows the hostname, which Certificate Transparency published at issuance — so the gate's removal is a real, if brief, exposure of an unreviewed build. **What still protects it:** the application's own controls, which are the ones under test — Discord OAuth, guild and role verification, CSRF, origin and host checks, the authentication limiter, and the kill switch. Options 2 (an address allowlist, rejected originally because the responsive checks need a laptop **and** a phone on mobile data) and 3 (keep the gate, record TC-SEC-07's browser half `Not Run`) were declined. Recorded as procedure **SP-29**. |
| **D-p — A-05 criterion 4a, made executable** | **Option 1, approved by Peter Duscha as Security Reviewer.** The threshold observation is taken under the **`development`** marker on the disposable `freedom_dev` with synthetic credentials, not under `staging`. | 2026-08-26 | **Resolves finding N-10.** The criterion as written could not be satisfied: `DatabaseSettings` binds each environment to exactly one database name (`adapters/database/config.py:66`), so a staging-marked process must target `freedom_staging` — the deployed database holding the protected account's two **real** credentials, which the same criterion forbids manipulating. Observed refusing (**S-01**), not inferred. **Nothing is weakened:** S-15 branches on `settings.environment.is_production` alone (`startup.py:205-212`), so `development` and `staging` take the **identical** path, and the live `environment: staging` marker is already evidenced by `/healthz` on the deployed portal (O-2). **What the option gives up, recorded rather than glossed:** no observation of the threshold under the staging marker itself, and no running portal answering `/healthz` with `break_glass_credentials:false`. Options 2 (a throwaway second PostgreSQL cluster) and 3 (temporarily disabling a real credential — excluded by the criterion's own text) were declined. Change-log **C-P3.5-V**. |
| **D-q — SP-10's instrument** | **Route A, approved by Peter Duscha as Operations Owner.** `backup-restore-drill.sh` accepts `freedom_staging` behind two independent, non-default signals. | 2026-08-26 | **Resolves finding N-11.** The script refused any target but `freedom_dev`/`freedom_test` **by design**, so SP-10 — TC-OPS-02's staging half — had no instrument. Route A keeps the automatic before/after inventory comparison that makes TC-OPS-02 a *verified* restore rather than a successful dump (plan §14.3: "restore tests, not merely backup success messages"). **It does weaken a stated invariant**, and is fenced accordingly: `FREEDOM_DRILL_ALLOW_STAGING=1` **and** `FREEDOM_DRILL_STAGING_CONFIRM=freedom_staging`, neither a default, with a loud banner; **production keeps no override at all**. Applied 2026-08-26 with three falsifying tests. Route B (a manual procedure, no test) was declined. Change-log **C-P3.5-V**. |

---

## 1. Scope and exclusions

### 1.1 In scope for P3.5

| # | Deliverable | Delivery-plan source |
|---|---|---|
| D-1 | Remediation and re-review of every blocking/important finding raised against Phase 3 | §5 P3.5 |
| D-2 | Final requirements-to-evidence traceability across P3.0–P3.4 | §5, §11 |
| D-3 | Narrow suites during work; full suites before submission, against disposable PostgreSQL, with every skip explained | §5, plan §13.3 |
| D-4 | Available formatter/linter/type/migration/compile checks, or an explicit unavailability statement | plan §13.3 |
| D-5 | Isolated-staging OAuth, member-read, Council-link, folder-selection, preview, confirm and audit-search flows | §5, TC-OPS-03 |
| D-6 | Security headers, host/origin, CORS/CSRF, revocation and object-substitution evidence, including the browser half of TC-SEC-07 | §11, TC-SEC-05/07 |
| D-7 | Deployment, health, monitoring, backup, restore, rollback and recovery rehearsals | TC-OPS-01…05 |
| D-8 | Representative resource/performance evidence for I-06 and A-06 | TC-PERF-01…03 |
| D-9 | Browser, responsive, zoom, keyboard and assistive-technology evidence for R-23 | TC-UI-01/02, TC-UI-08/09 |
| D-10 | Operational A-05 establishment and its evidence | RAID A-05 |
| D-11 | A final submission **requesting** the Phase 3 gate decision | §5, §13 |

### 1.2 Explicitly out of scope

- Production deployment, public exposure and any DNS, firewall or public proxy change.
- Any change to Phase 3 authentication, authorization, persistence, route or
  view-model contracts. A necessary cross-contract change stops for Codex review
  and Peter's decision (delivery plan §5 P3.4/P3.5).
- New product features, new routes, ordinary-member mutation, character
  game-state correction, Phase 4 work of any kind.
- Sheet retirement, Foundry writes, live LevelDB access.
- Real player data, production backups, production Discord/Sheets/Foundry/PostgreSQL contact.
- Self-acceptance of P3.5 or closure of the Phase 3 gate.

### 1.3 Boundary this plan will not cross without a separate authorization

Public staging exposure · real-host DNS/proxy/firewall/systemd/provider mutation ·
creation or change of real Discord applications, guilds, roles or secrets ·
reading, printing, copying or committing secrets or `.env` · real WebAuthn
enrollment without Peter present · contact with live Discord, Sheets, Foundry or
production PostgreSQL · production backups or real player data in staging ·
closing I-06, A-05, A-06 or R-23 on local or simulated evidence.

---

## 2. Owners

| Stream | Owner | Boundary |
|---|---|---|
| Backend/integration implementation, traceability, evidence assembly, submission | **Claude** (working Technical Lead) | Repository-scoped; cannot approve its own work, cannot mutate the host |
| Verified frontend-only remediation, if a finding arises | **Gemini** | Accepted contracts only; a cross-boundary need returns to Claude |
| Independent implementation review **and** a distinct security-focused review | **Codex** | Two separate passes; did not implement P3.5 |
| Operational, security, accessibility and host actions; the A-05 ceremony; real-device check; every authorization | **Peter Duscha** (Sponsor, Acceptance/Operations/Data Owner, accountable Security and Accessibility Reviewer) | Sole decider of the Phase 3 gate |

**Audience rule for every operator-facing artifact (recorded 2026-08-23).** The
Operations Owner is the accountable decision-maker and **is not a programmer or a
web engineer**. Every procedure written for him — SP-01…SP-23, the enrollment
ceremony, the accessibility checks — must be literal and click-by-click, must
state what to type or press and what he should expect to see, and must never
require him to interpret a configuration file, a stack trace or a protocol term.
Where a step needs judgement he cannot be expected to have, the Technical Lead
decides it and records the decision rather than referring it. The formal
traceability, contract and review artifacts remain written for Codex and are not
his to read.

Peter is **accountable and participating**, not merely approving: SP-01…SP-05,
SP-07, SP-18 and SP-19 (§6.2) cannot be performed by Claude at all.

---

## 3. Estimate, confidence and contingency

### 3.1 Reconciliation with the accepted 3/5/8-day P3.5 range

The delivery plan §6 accepted **3 / 5 / 8 focused days** for "P3.5
integration/gate evidence". That range is retained unchanged for the
**implementer** stream, and is decomposed here so the reconciliation is checkable:

| Stream | Owner | Optimistic | Likely | Pessimistic |
|---|---:|---:|---:|---:|
| S1 — repository-scoped integration, final traceability, full suites, all available checks, migration rehearsal | Claude | 1.0 | 1.5 | 2.5 |
| S2 — staging build **preparation**: procedures, service/proxy templates, configuration contract, redaction checklist | Claude | 0.5 | 1.0 | 2.0 |
| S3 — staging **execution support** and evidence capture, under Peter's authorization and participation | Claude | 0.5 | 1.0 | 2.0 |
| S4 — submission, review response and remediation | Claude | 1.0 | 1.5 | 1.5 |
| **Claude total** | | **3.0** | **5.0** | **8.0** |

**This matches the accepted range exactly.** No rebaselining is proposed.

### 3.2 Effort this plan adds that the accepted range never contained

The accepted range is *implementer focused effort*. It does not include, and
never included, the accountable owner's own work:

| Accountable stream | Owner | Optimistic | Likely | Pessimistic |
|---|---:|---:|---:|---:|
| Staging host build: DB/roles, secrets, Discord app/guild, service units, proxy boundary | Peter | 0.5 | 1.0 | 2.0 |
| A-05 ceremony: account establishment, two WebAuthn enrollments, retirement refusal, emergency login, recovery grant | Peter | 0.25 | 0.5 | 1.0 |
| TC-UI-08 real-device check | Peter | 0.1 | 0.25 | 0.5 |
| TC-UI-09 screen-reader traversal | Peter or a qualified person | **unavailable** | 0.5 | 1.0 |
| Review reading and gate decision | Peter | 0.25 | 0.5 | 1.0 |
| Verified frontend remediation, **contingent** | Gemini | 0.0 | 0.5 | 2.0 |
| Two independent review passes | Codex | 0.5 | 1.0 | 2.0 |

### 3.3 Confidence

- **Claude's 3/5/8 range: Medium-low** — the same confidence the plan recorded.
  S1 and S4 are well understood; S2/S3 depend on a host that has never run this
  service.
- **End-to-end P3.5 completion: Low.** Six of the deliverables (D-5…D-10) are
  gated on actions that have **never been performed on any host** and that Claude
  cannot perform. The dominant uncertainty is availability and authorization, not
  implementation difficulty.
- **Calendar: none promised.** Per delivery plan §6, no calendar date is
  committed until Peter records availability windows.

### 3.4 Contingency

Delivery plan §6 reserves **30% of each package's likely implementation effort**
for review and remediation, already inside the pessimistic figure. For P3.5 that
is **1.5 focused days**, held explicitly against:

1. blocking or important findings from either Codex pass;
2. a staging observation that contradicts a documented contract (for example a
   proxy/application limit mismatch at TC-LIM-02, or a TC-PERF-01 measurement
   above N-47's 1 GiB guard); and
3. re-running the full evidence set after any remediation.

**Contingency is not permission to compress evidence.** A blocking finding
returns through its stop gate.

---

## 4. Environment and dependency readiness matrix

Observed on this host on 2026-08-23. "Observed" means a command was run and its
output read; nothing here is inferred from documentation.

| # | Item | Required state | Observed 2026-08-23 | Readiness |
|---|---|---|---|---|
| E-1 | Python | 3.12 in both virtualenvs | `venv-web` 3.12.3; `venv` 3.12.3 | **Ready** |
| E-2 | Node.js | present for the Foundry module suite | v24.19.0; 155 tests pass | **Ready** |
| E-3 | PostgreSQL server | running, loopback | 16.15, socket `/var/run/postgresql`, accepting connections | **Ready** |
| E-4 | Disposable test DB | guarded `freedom_test` | exists; both suites pass against it | **Ready** |
| E-5 | Development DB | `freedom_dev` | exists | **Ready** |
| E-6 | Restricted runtime role | non-login restricted role for grant tests | `freedom_runtime_test` exists (`rolcanlogin = f`) | **Ready** |
| E-7 | Alembic head consistency | single linear head | single head `0013`; 13 revisions; `alembic branches` empty | **Ready** |
| E-8 | Backup/restore drill script | disposable-only, socket-pinned | `infra/postgresql/backup-restore-drill.sh` present; refuses anything but `freedom_dev`/`freedom_test`, refuses TCP and inherited libpq configuration | **Ready for D-7's disposable half** |
| E-9 | Formatter / linter / type checker | configured, or explicitly unavailable | **None configured.** No `pyproject.toml`, `setup.cfg`, `tox.ini`, `.ruff.toml`, `.flake8`, `mypy.ini`, `.pre-commit-config.yaml`; no `ruff`/`black`/`isort`/`mypy`/`flake8`/`pyright` binary in either virtualenv | **Unavailable — recorded, never reported as passed** |
| E-10 | Worker/web systemd units on this host | present for staging | **Absent.** `freedom-bot.service` is the only Freedom unit loaded; `infra/systemd/` ships `freedom-bot.service.tmpl` and `freedom-worker.service.tmpl` only | **Blocked** |
| E-11 | `freedom-web` service template | a unit template exists to deploy from | **Absent — no `freedom-web.service.tmpl` exists in the repository at all.** This is a real gap in D-7/TC-OPS-04, and S2 must author it | **Gap; owned by S2** |
| E-12 | Proxy site block for the portal | a Caddy staging site block | **Absent.** Caddy runs (Foundry), and no repository artifact defines a portal site block or its body limits (N-55) | **Gap; owned by S2, applied only by Peter** |
| E-13 | Staging database and role | `freedom_staging` + separate login role | **Absent.** Cluster holds `freedom_dev`, `freedom_test`, `postgres` and templates only; roles are `foundry`, `freedom_runtime_test`, `postgres` | **Blocked — SP-01** |
| E-14 | Staging Discord application/guild/roles | separate application, guild, role IDs, secrets | **Not observable from here and must not be created by Claude.** No repository evidence that any staging Discord identity exists | **Blocked — SP-03, Peter only** |
| E-15 | Artifact store and kill-switch paths | `/srv/freedom/snapshots`, `/srv/freedom/web` | `/srv/freedom` exists, owned `root:root`, **empty** | **Blocked — SP-01/SP-04** |
| E-16 | Browser engine and automation | a browser plus a driver, for TC-UI-01/02 and TC-SEC-07's browser half | **Absent.** No `chromium`, `chrome` or `firefox` binary on PATH; no `playwright`/`selenium` in either virtualenv (63 packages in `venv-web`, none of them a browser driver) | **Blocked — needs a deliberate dependency decision (§9.4)** |
| E-17 | Real device for TC-UI-08 | Peter's own hardware | Not available to Claude by construction | **Blocked — SP-18, Peter only** |
| E-18 | Screen reader and a qualified operator for TC-UI-09 | assistive technology plus a person to drive it | No evidence any capacity exists; inherited `not tested` from the visual baseline | **Blocked — SP-19; may legitimately stay Not Run (§13.4)** |
| E-19 | Protected administrator account and WebAuthn credentials | account exists; ≥2 enabled credentials | **Never established on any host.** The mechanism exists (`tools/webauthn_enrollment`, S-15 startup refusal, `/healthz` shortfall) and has never been exercised with a real authenticator | **Blocked — SP-07, A-05, Peter only** |
| E-20 | Host capacity for representative load | headroom beside three Foundry instances, the bot and PostgreSQL | 6 CPUs; **7 GiB RAM with ~2 GiB available**; 138 GiB free disk | **Constraint, not a blocker — see §11.3** |

**The single dominant readiness fact:** everything Claude can do locally is
ready and green; everything that closes I-06, A-05, A-06 and R-23 requires a host
that does not yet have a staging environment, a browser, an authenticator or a
protected account.

---

## 5. Safe local checks actually performed on 2026-08-23

Read-only or disposable-database only. Literal commands and literal results.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2168 passed, 80 skipped, 1063 warnings in 124.22s** (exit 0) |
| 2 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test /opt/discord-bots/freedom-bot/venv/bin/python -m pytest -q -rs tests/test_*.py` | **2294 passed, 1 warning in 134.59s** (exit 0) |
| 3 | `node --test "foundry-module/tests/*.test.mjs"` | **155 pass, 0 fail, 0 skipped** in 207.76 ms |
| 4 | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **3/3 OK** |
| 5 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 6 | `/opt/discord-bots/venv-web/bin/python -m compileall -q adapters application domain tests` | clean, exit 0 |
| 7 | `/opt/discord-bots/freedom-bot/venv/bin/python -m compileall -q adapters application domain tests` | clean, exit 0 |
| 8 | `git diff --check` | clean, exit 0 |
| 9 | `DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/alembic heads` / `history` / `branches` | single head **`0013`**; linear `base → 0001 → … → 0013`; **no branches** |
| 10 | `git status --porcelain` | empty — the worktree was clean before and after this audit |

**The two suites were run sequentially, never concurrently.** They share the one
disposable `freedom_test` database; running them at the same time produces dozens
of false failures. Every later P3.5 run must preserve that ordering.

### 5.1 Every skip, warning and unavailable check, explained

| Class | Count | Explanation |
|---|---:|---|
| Skips, `tests/web/test_p3_2_matrix.py:155` | 54 | Deliberate: the permitted cells of the authorization matrix are asserted by the per-route success cases, so the matrix parameterization skips them rather than duplicating them. Denial cells are **not** skipped. |
| Skips, `tests/web/test_p3_3_matrix.py:198` | 26 | Same construction for the P3.3 matrix. |
| Warnings, web suite | 1063 | Overwhelmingly HTTPX `DeprecationWarning: Setting per-request cookies=<...> is being deprecated` from the test harness. Not a behavior or security failure; identical in class to the 99 warnings Codex recorded at Step 13. |
| Warnings, bot suite | 1 | `audioop` deprecation from `discord/player.py` under Python 3.12. Third-party; music is removed under OD-40 and no platform code imports it. |
| Formatter | — | **Not configured. Not run. Not passed.** |
| Linter | — | **Not configured. Not run. Not passed.** |
| Type checker | — | **Not configured. Not run. Not passed.** |
| Migration upgrade/downgrade/upgrade rehearsal | — | **Not run in this read-only audit.** It writes to a database and belongs to S1 under SG-1 (§6.1, EX-3). |

The absence of a formatter, linter and type checker is a **standing repository
condition**, consistent with what the P3.3 submission recorded. P3.5 must not
introduce one as a drive-by change; if Peter wants one, it is a scoped decision
with its own diff.

---

## 6. Execution sequence

### 6.1 Repository-scoped work (Claude; released by SG-1)

| Step | Work | Produces | Depends on |
|---|---|---|---|
| EX-1 | Assemble the final requirements-to-evidence traceability across P3.0–P3.4, expanding every delivery-plan §11 row and every implementation-plan §12 mandatory test to exact node IDs and exact staging procedure IDs | `phase-3-p3-5-test-and-evidence-traceability.md` | SG-1 |
| EX-2 | Reconcile the **TC-UI label discrepancy** recorded in §14, F-1, without weakening any accepted row | traceability doc + a finding entry | EX-1 |
| EX-3 | Migration rehearsal on a guarded disposable database: `upgrade head` → `downgrade` across the P3.3 boundary → `upgrade head`, with the runtime-grant template applied and re-verified | staging/ops evidence doc §migrations | SG-1 |
| EX-4 | Backup → checksum → destroy → restore → inventory comparison via `infra/postgresql/backup-restore-drill.sh` against `freedom_test` | TC-OPS-02 **disposable half** | EX-3 |
| EX-5 | Author the missing deployment and ceremony artifacts: `infra/systemd/freedom-web.service.tmpl`, a staging worker override, a **documented** Caddy staging site block including the N-55 body limits and the `OPTIONS`/CORS rule, and the **WebAuthn registration reference page** that `tools/webauthn_enrollment.py` already tells operators to use and that does not exist (F-7) | operations doc updates | SG-1 |
| EX-6 | Author the staging runbook: literal, ordered, redaction-safe procedures SP-01…SP-23 | `phase-3-p3-5-staging-and-operations-evidence.md` (procedures, results empty) | EX-5 |
| EX-7 | Author the accessibility and browser plan with its exact viewport/zoom/AT record fields | `phase-3-p3-5-accessibility-and-browser-evidence.md` (plan, results empty) | SG-1 |
| EX-8 | Build the synthetic representative load fixtures for TC-PERF-01…03 — realistically shaped, bounded, **never real Actor payloads** | fixtures + method note | SG-1 |
| EX-9 | Full suites, all available checks, manifests, `git diff --check`, and the complete skip/warning explanation | submission §validation | after EX-1…EX-8 |

**EX-1…EX-9 mutate nothing outside the repository and the disposable database.**

### 6.2 Staging procedures (authored by Claude; executed only with Peter, under SG-2/SG-3)

| ID | Procedure | Closes | Who executes |
|---|---|---|---|
| SP-01 | Create `freedom_staging` database, owner role and separate restricted login role; apply `runtime-grants.sql.tmpl`; create `/srv/freedom/{snapshots,web}` with `0700` | prerequisite | Peter |
| SP-02 | Generate staging secrets independently (CSRF, cursor, client-digest, token-encryption keys); place a `0600` environment file **outside** the repository | prerequisite | Peter |
| SP-03 | Create/confirm a **separate** staging Discord application, guild and role IDs; record identifiers only, never secrets | prerequisite | Peter |
| SP-04 | Install `freedom-web-staging` and `freedom-worker-staging` units on loopback `127.0.0.1:8001`, `WORKER_ENABLED` differing between them | prerequisite | Peter |
| SP-05 | Add the staging Caddy site block behind the accepted proxy boundary, with matched body limits | prerequisite | Peter |
| SP-06 | `alembic upgrade head` against staging; re-apply runtime grants; verify head `0013` | prerequisite | Peter + Claude |
| SP-07 | **A-05 ceremony** — §9 | A-05 | Peter (Claude assists) |
| SP-08 | Observe every startup refusal (S-11 both directions, S-15, environment markers) refusing on the **deployed** configuration | TC-OPS-04 | Peter + Claude |
| SP-09 | Kill switch: engage layer 1, confirm every route except `/healthz` and `/static/*` answers 503, confirm the bot and Foundry are unaffected, release | TC-OPS-01 | Peter + Claude |
| SP-10 | Backup, restore, rollback and rerun rehearsal on the staging database | TC-OPS-02 staging half | Peter + Claude |
| SP-11 | End-to-end browser flow: OAuth login → member read → Council link change → folder selection → preview → confirm → audit search | TC-OPS-03 | Peter (browser) |
| SP-12 | Review monitoring/log output for identity, character or token data | TC-OPS-05 | Peter + Claude |
| SP-13 | Assert the deployed Caddy limit and the application limit are **equal**, on both the general and snapshot routes | TC-LIM-02 | Peter + Claude |
| SP-14 | Browser-observed security headers and CSP on normal, early and error responses | TC-SEC-07 browser half | Peter (browser) |
| SP-15 | Representative measurements: 64 MiB refusal, 32-Actor-class preview and apply, worker peak RSS vs N-47 | TC-PERF-01/02 | Peter + Claude |
| SP-16 | `/healthz` and a status poll answered **during** a running preview | TC-PERF-03 | Peter + Claude |
| SP-17 | Worker restart, lease expiry, lost response, reaper recovery and apply-idempotency under the deployed configuration | I-06, A-06 | Peter + Claude |
| SP-18 | Real-device responsive and 200% zoom inspection at 320/768/1280 | TC-UI-08 | Peter only |
| SP-19 | Screen-reader traversal of login, My Characters, character detail, reconciliation and audit | TC-UI-09 | Qualified operator only |
| SP-20 | Emergency login with Discord simulated unavailable | A-05 | Peter |
| SP-21 | Recovery grant: issue host-locally, use once, prove replay and expiry refusal — **without recording the token** | A-05 | Peter |
| SP-22 | Break-glass boundary: prove `{platform_administrator}` only; prove Council, character and import-apply routes refuse | A-05, TC-BG-05a…e re-observation | Peter + Claude |
| SP-23 | Browser-observed rendering at 320 / 768 / 1280 CSS pixels and 200% zoom/reflow; keyboard-only traversal, focus order, skip links, HTMX-enhanced and JavaScript-disabled paths, real-engine contrast and reduced motion | TC-UI-01/02, R-23 | Peter (browser) |

### 6.3 Review and decision

| Step | Work | Owner |
|---|---|---|
| EX-10 | Final submission requesting — never making — the Phase 3 gate decision | Claude |
| EX-11 | Independent implementation review | Codex |
| EX-12 | Distinct security-focused review | Codex |
| EX-13 | Remediation of any blocking/important finding, then re-review | Claude / Gemini |
| EX-14 | **Phase 3 gate decision** | Peter, alone |

---

## 7. Requirement-to-test/evidence matrix

Literal commands where a command exists; a named procedure ID where a human acts.
Full expansion to exact node IDs is EX-1's deliverable; this is the plan-level map
and it drops no delivery-plan §11 row.

### 7.1 Rows already carried by automated evidence (to be re-run and re-cited, not re-argued)

| Delivery-plan §11 requirement | Evidence class | Literal command |
|---|---|---|
| Unauthenticated denial; non-member/member/Council/administrator matrix; object substitution; stable role IDs; break-glass boundary; CSRF/origin/host/cookie/redirects; body/content-type/filename limits; escaping; correlation UUID; import staleness/idempotency/double-click/two-browser; append-only audit and restricted-role denial; absence of character-game-state routes; CSP and security headers on normal and error responses; no-JS essential flows; asset integrity and traversal refusal | automated, real PostgreSQL | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test /opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` |
| Domain, rules, repository and Foundry-contract behavior | automated | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test /opt/discord-bots/freedom-bot/venv/bin/python -m pytest -q -rs tests/test_*.py` |
| Foundry module read-only boundary | automated | `node --test "foundry-module/tests/*.test.mjs"` |
| Production asset integrity | manifest | `sha256sum -c adapters/web/static/asset-integrity.sha256` |
| Visual freeze integrity | manifest | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` |
| Bytecode compilation | compile | `… -m compileall -q adapters application domain tests` (both virtualenvs) |
| Whitespace/conflict markers | diff | `git diff --check` |
| Migration consistency | alembic | `DATABASE_URL=… ./venv-web/bin/alembic heads` (single head `0013`), `history`, `branches` |
| Migration apply/downgrade/upgrade and recovery | disposable rehearsal | EX-3 (`upgrade head` → `downgrade` → `upgrade head`) |
| Backup/restore/rollback, disposable half | disposable rehearsal | `infra/postgresql/backup-restore-drill.sh freedom_test <workdir>` |

### 7.2 Rows that **only** staging can carry

| Requirement | Test | Procedure | Status today |
|---|---|---|---|
| Proxy/application limit parity | TC-LIM-02 | SP-13 | **Not Run** |
| Security headers observed by a real browser engine | TC-SEC-07 browser half | SP-14 | **Not Run** |
| Kill switch on a deployed portal | TC-OPS-01 | SP-09 | **Not Run** |
| Backup/restore/rollback on staging | TC-OPS-02 staging half | SP-10 | **Not Run** |
| Staging end-to-end flow | TC-OPS-03 | SP-11 | **Not Run** |
| Deployed startup refusals | TC-OPS-04 | SP-08 | **Not Run** |
| Monitoring output carries no identity/character/token data | TC-OPS-05 | SP-12 | **Not Run** |
| Worker peak RSS vs N-47's 1 GiB guard | TC-PERF-01 | SP-15 | **Not Run — never measured** |
| Real-folder apply measured end to end | TC-PERF-02 | SP-15 | **Not Run — never measured at all (RR-06)** |
| `/healthz` and status poll under a running preview | TC-PERF-03 | SP-16 | **Not Run** |
| Browser rendering at 320/768/1280 and 200% reflow, keyboard traversal and reduced motion | TC-UI-01/02 | SP-23 | **Not Run — no browser on this host** |
| Real-device inspection | TC-UI-08 | SP-18 | **Not Run — Peter's hardware** |
| Screen-reader traversal | TC-UI-09 | SP-19 | **Not Run — no capacity identified** |

### 7.3 Status vocabulary, used strictly

`Planned` — scheduled, not started. `Blocked` — a named prerequisite is missing.
`Not Run` — required, and no evidence exists. `Failed` — executed, did not meet
its criterion. `Passed` — executed at its **required evidence level** and met its
criterion. **A `Passed` is never written from a lower evidence level than the
accepted row demands.**

---

## 8. Staging topology, isolation and secret redaction

### 8.1 Topology

Per `docs/operations/topology.md` §3 and OD-22, staging **shares this host**.
The separations are therefore enforcement requirements, not recommendations.

```text
   (no public DNS, no public exposure under this plan)
                      │
                      ▼
             Caddy — staging site block, loopback upstream only
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
 freedom-web-staging        freedom-worker-staging
   127.0.0.1:8001              no listener at all
        │                           │
        └──────────┬────────────────┘
                   ▼
   PostgreSQL  freedom_staging + separate restricted role
               loopback socket only
```

### 8.2 Non-negotiable separations (verified before any flow is exercised)

| Resource | Requirement | Verification |
|---|---|---|
| Database | Separate **database and role**, not a schema in production | SP-01; `\l` and `\du` inspection recorded without credentials |
| Discord | Separate application, guild and role IDs; separate secrets | SP-03; identifiers recorded, secrets never |
| Google Sheets | Not exercised. If it ever were, a copy and a separate service account | asserted in the evidence doc |
| Foundry | Never `the-guild`. Synthetic snapshot artifacts only | SP-15 fixtures |
| Secrets | Independently generated; **no value shared with production** | SP-02 |
| Data | Synthetic or anonymized only; **never a production backup** | stated per procedure |
| Environment markers | `WEB_ENVIRONMENT=staging`; fail-closed cross-environment validation observed refusing | SP-08 |
| Exposure | Loopback bind behind the accepted proxy boundary; no public DNS | SP-04/SP-05 |

### 8.3 Secret-redaction checklist, applied to every artifact before it is written

1. No `.env` or environment-file content, in whole or in part.
2. No token, client secret, encryption key, password, cookie value, session
   identifier, CSRF token or recovery grant token — **including in a "redacted"
   form that preserves length or prefix**.
3. No WebAuthn credential material: no attestation object, no public-key blob,
   no counter value tied to a real credential. Record **record UUIDs and
   nicknames only**.
4. No Discord user IDs, usernames, global names or avatars of real people beyond
   Peter's own explicitly authorized staging identity; no player data at all.
5. No database URL containing a user, password or host; name the database only.
6. No raw snapshot bytes, Actor payloads, Actor names or warning text from any
   real export.
7. Screenshots: synthetic data only, and reviewed pixel-by-pixel for a leaked
   token in an address bar, a session cookie in devtools, or a real name.
8. Logs pasted as evidence are re-read line by line before pasting, not grepped
   for a denylist.
9. Every command shown in an artifact is shown with placeholders where a secret
   would otherwise appear, and the placeholder is obviously a placeholder.
10. `git diff --check` plus a manual diff read before any commit; no `.env`,
    artifact, snapshot or backup file is ever staged.

---

### 8.4 Backup, restore, rollback and recovery design

Four distinct obligations, deliberately separated because they fail differently.

| # | Obligation | Design | Evidence |
|---|---|---|---|
| B-1 | **Backup** | `pg_dump` of the staging database to a working directory on this host, immediately checksummed. Encryption, retention and the off-host copy are production concerns owned by OD-21 and the deployment gate, and staging holds no real data | SP-10 |
| B-2 | **Restore** | Restore into the same disposable target, then compare the **table and row inventory** before and after — a restore that reports success without an inventory comparison proves nothing (plan §14.3) | SP-10; disposable half already exercisable by `infra/postgresql/backup-restore-drill.sh freedom_test <workdir>` (EX-4) |
| B-3 | **Rollback** | Schema rollback is Alembic's, not the backup's: `upgrade head` → `downgrade` across the P3.3 boundary → `upgrade head`, with the runtime-grant template re-applied and re-verified afterwards. Revision `0013`'s documented rollback boundary and `0006`'s and `0009`'s documented rollback costs (`web-portal.md` §§3.3, 3.5, 3.6) are read **before** the rehearsal and the observed behavior compared against them | EX-3 on `freedom_test`; SP-10 on staging |
| B-4 | **Recovery** | Operational, not schema: worker SIGTERM mid-attempt, lease expiry, reaper requeue, lost response, and a retry that finds the already-committed effect and returns it as a duplicate. The invariant proved is **exactly one durable effect**, and the fence that carries it is `uq_snapshot_imports_applied_input` plus `snapshot_imports.request_key`, not the job's state | SP-17 |

Two rules that hold throughout:

- **A restore is never performed into production, and staging is never restored
  from a production backup.** The drill script already refuses anything but
  `freedom_dev` and `freedom_test`, refuses TCP targets and refuses inherited
  libpq configuration; the staging procedure inherits the same discipline
  explicitly rather than by assumption.
- **A pre-migration backup is taken before every rehearsed migration**, including
  on staging, so a failed downgrade is recoverable without re-creating the
  environment.

---

## 9. A-05: the Peter-participated host ceremony

**Not authorized by this plan.** It requires SG-3.

### 9.1 Ordering (the hazard S-15 exists for)

Migration `0006` inserts the protected *mapping*; the protected **account** is
created by the **first enrollment**. Until that enrollment happens, break-glass
has no account to authenticate, so the emergency route exists but cannot be used —
which is exactly today's condition, and exactly why A-05 is open.

### 9.2 Steps

| # | Step | Evidence recorded | Never recorded |
|---|---|---|---|
| A-1 | Establish the protected Server Administrator account through `python -m tools.webauthn_enrollment enroll` on the target host | host, environment, UTC timestamp, operator name, credential **nickname** and record UUID | credential id/public key bytes, PIN, biometric, attestation |
| A-2 | Enroll a **second, independent** authenticator | same | same |
| A-3 | Prove retirement below two is refused: `… retire …` on the second credential | the exact refusal message and exit status | — |
| A-4 | Prove production-class startup refuses below two (S-15) and that `/healthz` reports the shortfall | the refusal, the health body | — |
| A-5 | Prove startup and `/healthz` readiness **after** two credentials exist | the health body | — |
| A-6 | Emergency login with Discord simulated unavailable (SP-20) | outcome, correlation ID, audit record identity | session cookie value |
| A-7 | Prove break-glass resolves to `{platform_administrator}` **only** — Council, character and import-apply routes refuse (SP-22, N-65/N-67) | each refusal code and body | — |
| A-8 | Verify limiter, audit, correlation, session expiry (15 min idle / 60 min absolute) and logout/revocation | observed behavior | — |
| A-9 | Recovery grant: `python -m tools.emergency_recovery issue`, use once, then prove replay and 10-minute expiry refusal (SP-21) | grant **record id**, audit rows, refusals | **the token itself — never, in any form** |
| A-10 | Document custody, replacement, loss and recovery | procedure text | credential material |

### 9.3 Boundaries Claude holds

Claude does **not** choose Peter's authenticators, does not touch a credential,
does not expose a recovery token, and **cannot close A-05 with a mocked
authenticator**. A mock proves the code path; A-05 is an assumption about the
world, and only a real enrollment on the real target host validates it.

### 9.4 The browser-engine question, stated rather than assumed

The WebAuthn registration ceremony happens in a browser, and this host has no
browser engine (E-16). Two of P3.5's obligations therefore depend on a decision
Peter has not yet been asked for:

- **A-05** needs a browser to *perform* the registration ceremony whose result
  `tools.webauthn_enrollment` consumes.
- **TC-UI-01/02 and TC-SEC-07's browser half** need a browser to *observe*
  rendering and headers.

**Decided 2026-08-23 (P-2): Peter's own workstation browser**, against the staging
loopback via an authorized tunnel or a session on the host. **No headless browser
and no driver are added to this repository**, which keeps the delivery plan's
no-frontend-toolchain exclusion intact and adds no dependency to review.

Two consequences follow directly from that choice, and both change what the
ceremony must do rather than merely how it is driven — see F-7 and F-8 in §14.

---

## 10. Browser, device and accessibility plan (R-23, TC-UI-01/02, TC-UI-08, TC-UI-09)

### 10.1 The precondition, stated first

There is **no browser engine on this host** (E-16), no real device available to
Claude (E-17) and no identified screen-reader capacity (E-18). Every row below is
therefore `Not Run` today, and the first decision is P-2 (§9.4): whether the
browser is Peter's own workstation browser against the staging loopback — the
recommendation, because it adds no repository dependency — or a deliberately
added headless engine and driver.

### 10.2 What is covered, and by which procedure

| Coverage | Procedure | Accepted row |
|---|---|---|
| Keyboard-only operation of every workflow; no keyboard traps; visible **and** logical focus order; skip links reach the right landmark | SP-23 | TC-UI-03, R-23 |
| Semantics: landmarks, heading order, form labels, accessible descriptions, table headers and captions | SP-23, with the existing parsed-DOM tests re-cited under their contract IDs | TC-UI-03, TC-UI-05 |
| Denied, empty, loading, stale, validation and system-error states, each rendered from a **real view model** rather than a mock | SP-23 | TC-UI-05 |
| HTMX-enhanced paths **and** the same workflows with JavaScript disabled in the browser | SP-23 | TC-UI-05, F-SEC no-JS rows |
| 320, 768 and 1280 CSS-pixel viewports; no horizontal body overflow | SP-23 | TC-UI-01 |
| 200% zoom and reflow: no content or function lost | SP-23 | TC-UI-02 |
| Real-engine contrast (not only the static token calculation) and `prefers-reduced-motion` with focus indicators preserved | SP-23 | TC-UI-04, TC-UI-07 |
| Real-device inspection on Peter's own hardware | SP-18 | TC-UI-08 |
| Screen-reader traversal of login, My Characters, character detail, reconciliation and audit | SP-19 | TC-UI-09 |

### 10.3 What every result must record

Browser name and version · operating system and version · exact viewport in CSS
pixels · zoom level · assistive technology name and version where used · device
model where applicable · UTC timestamp · the staging build identity · the exact
workflow exercised · the observed outcome.

A result missing its browser/OS/viewport/zoom/AT identity is not evidence for an
accepted row, because the row's evidence level is defined by those facts.

### 10.4 Screenshot and privacy rule

Screenshots use **synthetic data only** and are reviewed individually before
inclusion — for a token in an address bar, a session cookie in an open devtools
panel, or a real person's name or avatar. No screenshot of a real player's data
is taken, and none is taken from any environment other than staging.

### 10.5 The honest-outcome rule

If real-device or screen-reader review remains unavailable, TC-UI-08 and/or
TC-UI-09 **stay Not Run**, R-23 stays active, and §13.4's production-readiness
consequence is stated in the submission. An automated pass, a source review or a
static contrast calculation is **never** promoted to satisfy them.

---

## 11. Performance and resource plan (A-06, TC-PERF-01…03)

### 11.1 What is being tested

A-06 asserts PostgreSQL is an acceptable substrate for **both** the durable job
queue **and** the cross-process rate limiter, so no second datastore is needed.
Half of it has automated evidence (`test_the_limiter_counts_across_processes`,
two engines sharing one database enforcing one budget). The other half —
behavior under representative operation — is unmeasured.

### 11.2 Measurements

| Measure | Method | Compared against |
|---|---|---|
| Preview duration, 32-Actor-class synthetic folder | wall clock inside the worker attempt, three runs, median and worst | the measured 9.566 s real-folder baseline |
| **Apply duration, end to end** | wall clock across the apply transaction, three runs | **no baseline exists — this is the first measurement (RR-06)** |
| Worker peak RSS | sampled RSS of the worker process across an attempt | **N-47's 1 GiB `MemoryMax` guard** |
| Portal responsiveness under load | `/healthz` and a status poll issued **during** a running preview | a stated bound, recorded before the run, not after |
| DB pool behavior | connections and wait time under N-53 (`pool_size=5`, overflow 5, timeout 5 s) | no pool timeout under representative load |
| Cross-process limiter | the deployed web and worker processes sharing one budget | one budget, not two |
| Lease heartbeat and commit fence | heartbeat ≤ 20 s inside a 60 s lease (N-23); the effect fence holds | no duplicate effect |
| Recovery after interruption | SIGTERM mid-attempt; lease expiry; reaper requeue; retry returns the committed effect as a duplicate | exactly one durable effect |
| 64 MiB refusal | a body over the accepted snapshot bound refused at both proxy and application | matched limits (N-20/N-55) |

### 11.3 The host constraint, recorded before the measurement rather than after

This host has 6 CPUs and **7 GiB of RAM with roughly 2 GiB available**, shared
with three Foundry instances, the live Discord bot, PostgreSQL and Caddy. A
worker attempt bounded by a 1 GiB `MemoryMax` therefore sits inside a fairly
narrow margin. Two consequences, stated now so the result cannot be rationalized
later:

1. Measurements are taken with the live bot and Foundry **running**, because that
   is the real condition (RAID R-24), and the observed load is recorded alongside.
2. If peak RSS approaches or exceeds N-47, that is a **finding**, not a reason to
   raise N-47. Changing an accepted numeric policy follows delivery-plan §7
   change control and security review.

### 11.4 Data rule

Realistically **shaped**, bounded, synthetic fixtures. Never a real Actor
payload, never a production backup, never real player data. The 500-Actor
synthetic benchmark's known weakness — synthetic Actors ~233× smaller than real
ones (RA-5) — is why the fixtures are shaped to real size distributions, and the
shaping method is recorded with the measurement so a reviewer can judge it.

---

## 12. Artifacts, stop gates and acceptance criteria

### 12.1 Artifacts

| # | Artifact | Written when |
|---|---|---|
| 1 | `docs/review/phase-3-p3-5-readiness-and-execution-plan.md` | **this document — now** |
| 2 | `docs/review/phase-3-p3-5-test-and-evidence-traceability.md` | EX-1 |
| 3 | `docs/review/phase-3-p3-5-staging-and-operations-evidence.md` | EX-6 (procedures), completed during SP-01…SP-17 |
| 4 | `docs/review/phase-3-p3-5-accessibility-and-browser-evidence.md` | EX-7 (plan), completed during SP-18, SP-19 and SP-23 |
| 5 | `docs/review/phase-3-p3-5-submission.md` | EX-10 |
| 6 | Narrowly required operations-document updates (`web-portal.md`, `topology.md`) plus the missing `infra/systemd/freedom-web.service.tmpl` and the documented staging site block | EX-5 |
| 7 | Status, change log and **evidence-backed** RAID dispositions | now (planning) and at each evidence change |

**No artifact is pre-created with passing evidence.** Artifacts 3 and 4 are
written with their procedures and empty result columns, and filled only by an
execution that actually happened.

### 12.2 Stop gates

| Gate | Condition | Releases |
|---|---|---|
| **SG-1** | Peter approves this plan | EX-1…EX-9, repository-scoped only |
| **SG-2** | Peter authorizes the staging build and participates | SP-01…SP-06, SP-08…SP-19, SP-23 |
| **SG-3** | Peter authorizes and is present for the credential ceremony | SP-07, SP-20…SP-22 |
| **SG-4** | Submission complete and honest | Codex's two review passes |
| **Phase 3 gate** | Peter's decision, after both reviews | **Peter alone** |

Claude stops at each gate. A staging or credential action taken without its gate
would invalidate the evidence it produced.

### 12.3 Acceptance criteria for P3.5 itself

1. Every delivery-plan §11 row and every implementation-plan §12 Phase 3
   mandatory test maps to an exact node ID or an exact procedure ID, with a
   status from §7.3, and no row is dropped.
2. Full suites and every available check are run and reported with literal
   commands and literal results, every skip and warning explained.
3. Unavailable checks are recorded as **unavailable**, never as passed.
4. Staging facts are recorded with exact timestamps, versions, environment
   identity, commands and outputs — and without secrets or unnecessary identity
   data.
5. I-06, A-05, A-06 and R-23 each carry an explicit disposition with the evidence
   that supports it, or an explicit statement that it remains open and what the
   production-readiness consequence is.
6. Blocking findings (security, authorization, identity, atomicity, data
   integrity, recovery, reliability) are zero, or remediated and re-reviewed.
7. Both Codex passes are requested and completed.
8. The submission **requests** the gate decision and does not make it.

---

## 13. Exact closure criteria for I-06, A-05, A-06 and R-23

### 13.1 I-06 — staging/browser/device evidence

**Closable only when all of the following hold:**

1. A **named, deployed** staging build exists — dated, with recorded environment
   identity and build identity — on separate DB/roles, separate web identity,
   separate Discord application/guild and independently generated credentials,
   bound to loopback behind the accepted proxy boundary, using synthetic or
   anonymized data only.
2. **TC-LIM-02** passes at configuration + supervised level (SP-13).
3. **TC-SEC-07's browser half** passes, observed by a real browser engine (SP-14).
4. **TC-OPS-01…05** each pass at their required level (SP-09…SP-12, SP-08).
5. **TC-PERF-01…03** each produce a real measurement against a stated bound
   (SP-15, SP-16), including the apply that **has never been measured**.
6. Environment markers and fail-closed cross-environment validation are observed
   refusing (SP-08).
7. Worker restart, lease expiry, lost response and recovery are observed (SP-17).
8. Backup, restore, rollback and rerun evidence exists for staging (SP-10).
9. Every result records exact timestamps, versions, environment identity,
   commands and outputs, with no secrets and no unnecessary identity data.
10. The **Operations Owner and the required reviewers accept it.**

**Not closable on:** undeployed configuration, local ASGI tests, written
procedures, or a green automated suite. Any of the ten unmet ⇒ I-06 stays open
and continues to block staging/production exposure and the production-readiness
decision.

### 13.2 A-05 — protected administrator account and credentials

**Closable only when all of the following hold:**

1. The protected Server Administrator account exists **on the intended target
   host**, established through supported host-local tooling.
2. **At least two independent, enabled** WebAuthn/passkey credentials are enrolled
   for it, confirmed through the protected operator/startup check.
2a. Each credential was created by a browser ceremony whose **relying-party
   identifier is the intended target host's own hostname** (N-60), and at least
   one of them has been **used to authenticate successfully against the
   production database**, not only against the disposable test database.
   **Revised 2026-08-23 under D-h:** because testing now runs on the production
   hostname, the credentials are already relying-party-correct, so the go-live
   step is re-registering the same credential id and public key — both public
   values, neither a secret — into the production database with
   `tools.webauthn_enrollment enroll`. No second browser ceremony is required.
   This is safe because `breakglass.py:276` rejects a non-advancing signature
   counter **only when the authenticator supplies one**, and a re-registered
   record starts at zero. A-05 still does not close until a real login against
   the production database has succeeded (F-8).
3. Retirement below two is **observed being refused**.
4. ~~Startup and `/healthz` readiness behavior is observed both below and at the
   threshold.~~ **Superseded 2026-08-25 by decision D-n (change-log C-P3.5-T),
   approved by Peter Duscha as accountable Security Reviewer.** The original
   wording is retained above, struck through rather than deleted, so a reviewer
   can see exactly what changed. It is replaced by 4a and 4b:

4a. **Startup behaviour and `/healthz` readiness are observed both below and at
   the N-13 threshold under `WEB_ENVIRONMENT=staging`**, on the deployed build,
   capturing the S-15 **warning** and the accepted C2-1 `break_glass_credentials`
   boolean. Executed against a **disposable** database with **synthetic**
   credential records: the protected account's real credentials are never
   manipulated, because `retire` refuses below two (N-13, criterion 3) and the
   only other route would be a database-owner action against Peter's own
   credentials, which the P3.5 handover forbids.

4b. **S-15's production-class refusal is observed before exposure**, in the
   guarded exercise defined as **SP-27** below. **This remains an A-05 closure
   criterion.**

   **Corrected 2026-08-26 after Codex interim finding B-1 (change-log
   C-P3.5-U).** The version approved on 2026-08-25 moved this evidence out of
   A-05 to the deployment gate, on the argument that S-15's refusal needs
   production configuration and A-05 gates public exposure. **That argument was
   wrong, and the error is worth naming precisely: it treated "production-marked"
   and "publicly exposed" as the same event.** They are not. A production-marked
   process can be exercised with no listener at all, against a guarded disposable
   database. S-02, S-05 and S-07 requiring the accepted production identity make
   such an exercise **more** controlled, not public. Moving the only observation
   of S-15 past A-05 would therefore have **weakened a security precondition**
   while appearing to resolve a circularity that did not exist.

   **SP-27 — the guarded pre-exposure exercise.** Owner: Peter (authorizes and
   supervises) with Claude. Estimated 20 minutes. **No socket is ever opened.**

   1. Create a **disposable** `freedom_production` database — the name
      `EXPECTED_DATABASES` requires for this environment — migrate it to head,
      and seed a protected administrator account holding **fewer than two**
      enabled credentials, using **synthetic** credential records. **It is never
      a copy of, and never restored from, any real data.**
   2. Block outbound egress for the exercising account with the single
      `iptables` OUTPUT rule already proven by SP-25, so no live Discord contact
      is possible even accidentally.
   3. Build production-marked settings — the accepted production origin, redirect
      URI and guild ID are **identifiers, not secrets**; the client secret is a
      syntactically valid placeholder, never the real one — and call
      **`run_resource_checks(settings, engine)` directly**
      (`application/web/startup.py:80`). **This is the whole reason the exercise
      is safe: `run_resource_checks` is a plain function, so S-15 is reached
      without uvicorn, without a bind, and without a route. There is no listener
      to expose, so no public traffic can reach it and no production cookie or
      OAuth callback can be delivered to it.**
   4. Record the literal `ConfigurationProblem` naming **S-15**.
   5. Seed the second synthetic credential and repeat, recording that the check
      now passes.
   6. **Teardown:** drop the database, remove the egress rule, delete the
      temporary environment file. Record each as done.

   **Never recorded:** credential material, the real client secret, any real
   account, or any value from a live production system.

4c. **A deployment-gate re-observation is retained as defence in depth**, at
   `docs/contracts/phase-3-operational-contract.md` §7 **item 10**. It is an
   *addition* to 4b, **never a replacement for it**: A-05 does not close on a
   promise that something will be checked later.

   **How to reverse 4a/4b/4c.** Restore the struck-through wording above and
   A-05 returns to a single criterion 4 requiring both observations, which is
   substantively what 4a and 4b now require together. No evidence collected under
   4a or 4b is invalidated by that reversal.

5. Emergency login succeeds with Discord simulated unavailable.
6. Break-glass is proven to grant **Platform Administrator only** — never
   Council, character ownership or import-apply authority, by implication or by
   route.
7. Limiter, audit, correlation, session expiry and logout/revocation are verified.
8. The host-local hashed, single-use, ten-minute recovery grant is exercised —
   issued, used once, replay refused, expiry refused — **with the token never
   recorded anywhere**.
9. Custody, replacement, loss and recovery are documented without credential
   material.
10. The **Security Reviewer confirms break-glass readiness**, and the Operations
    Owner records host, environment and date.

**Not closable on:** a mocked authenticator, a test fixture, a passing unit test,
or an enrollment on any host that is not the intended target.

### 13.3 A-06 — PostgreSQL as job-queue and limiter substrate

**Closable only when:**

1. The measurements in §11.2 are taken under **representative staging
   conditions**, with the co-located bot and Foundry running and the observed
   load recorded.
2. Preview and apply durations, worker peak RSS against N-47, portal
   responsiveness, DB pool behavior, cross-process limiter behavior, and lease
   heartbeat/commit-fence behavior all meet their stated bounds — with the bound
   stated **before** the run.
3. Recovery after worker interruption and lease expiry produces **exactly one**
   durable effect.
4. Every input is realistically shaped, bounded synthetic data.
5. If any measure misses its bound, A-06 does **not** close: the finding is
   recorded and the numeric policy change (if any) goes through delivery-plan §7
   change control and security review.

### 13.4 R-23 — accessibility residual

**Closable only when, in isolated staging:**

1. Keyboard-only operation, absence of traps, visible and logical focus order,
   and skip links are verified.
2. Semantics, headings, labels, descriptions and tables are verified.
3. Denied, empty, loading, stale, validation and error states are each verified
   from a real view model.
4. HTMX-enhanced **and** JavaScript-disabled paths are verified.
5. 320 / 768 / 1280 CSS-pixel viewports and 200% zoom/reflow are verified
   (TC-UI-01/02 via SP-23; TC-UI-08 via SP-18).
6. Real-engine contrast and reduced motion are verified.
7. Screen-reader traversal is documented (TC-UI-09).
8. Browser, OS, viewport, zoom, AT and versions are recorded for every result,
   and every screenshot uses synthetic data.

**The honest alternative, and it is a legitimate outcome:** if real-device or
screen-reader review remains unavailable, TC-UI-08 and/or TC-UI-09 **stay Not
Run**, R-23 **stays active**, and the submission states the production-readiness
consequence plainly — that the portal would be exposed without direct evidence
that a screen-reader user can complete its essential workflows, which is an
accessibility risk Peter would be accepting knowingly rather than one that was
tested away. R-23 is not closed by automation, and P3.4's acceptance did not
close it.

---

## 14. Findings and observations from this audit

| ID | Observation | Class | Disposition |
|---|---|---|---|
| **F-1** | The P3.4 submission's accessibility matrix **renumbers** the TC-UI rows relative to the accepted `phase-3-test-traceability.md` §16. The accepted contract defines TC-UI-03 as keyboard reachability with a visible focus indicator, TC-UI-04 as `prefers-reduced-motion`, TC-UI-05 as the empty/loading/stale/denied/validation/system-error states, TC-UI-06 as prototype isolation and TC-UI-07 as WCAG **2.2** AA contrast. The submission labels them semantic landmarks, contrast (as "WCAG 2.1 AA"), form-label associations, focus/reduced-motion and no-JavaScript respectively. The **tests are named for the contract's numbering** — the submission's "TC-UI-04" row cites `test_tc_ui_07_wcag_contrast_matrix`, and its "TC-UI-06" row cites `test_tc_ui_04_prefers_reduced_motion_media_query` — so the code is right and the citation labels drift. Two accepted rows consequently have **no citation under their own ID** in that matrix: TC-UI-03 (keyboard reachability/focus) and TC-UI-05 (the six state renderings), even though passing tests for both exist | **Important — traceability.** Not a security or behavior defect; nothing is broken, and no accepted row is weakened. It matters because a gate package that cited a passing test against the wrong accepted row would be misreporting | EX-2 rebuilds the TC-UI mapping in the P3.5 traceability document strictly against the **accepted contract's** numbering, locates the existing evidence for TC-UI-03 and TC-UI-05 under their own IDs, records the misalignment openly rather than silently repairing it, and changes no accepted contract row. Flagged for Codex |
| **F-2** | `infra/systemd/freedom-web.service.tmpl` **does not exist**. The repository ships bot and worker unit templates only, and TC-OPS-04 requires observing startup refusals on a deployed configuration | **Important — gap in D-7** | EX-5 authors it. Applied to the host only under SG-2, by Peter |
| **F-3** | No repository artifact defines the portal's Caddy site block or its body limits, yet TC-LIM-02 asserts proxy/application **parity** from the deployed configuration | **Important — gap in D-6/D-7** | EX-5 documents it, including the N-55 limits and the `OPTIONS`/no-proxy-CORS rule |
| **F-4** | No browser engine and no browser automation exist on this host, so TC-UI-01/02 and TC-SEC-07's browser half cannot be executed here as things stand | **Blocking for those rows only** | §9.4 — Peter's decision between his own workstation browser (recommended, no new dependency) and a deliberate headless-browser dependency |
| **F-5** | `/srv/freedom` exists but is empty and `root`-owned; the artifact store and kill-switch paths do not exist | Operational prerequisite | SP-01/SP-04 |
| **F-6** | The two pytest suites share the single disposable `freedom_test` database and must never run concurrently | Method constraint | Recorded in §5; binding on every later P3.5 run |
| **F-7** | `tools/webauthn_enrollment.py`'s own docstring directs the operator to perform the registration ceremony "with the reference page in `docs/operations/`". **No such page exists.** There is therefore no supported way to obtain the base64url credential id and COSE public key the `enroll` subcommand requires, and A-05's ceremony has no starting point | **Important — blocks the A-05 ceremony**, not a defect in the mechanism | EX-5 authors the page: a single self-contained local HTML file that runs `navigator.credentials.create()`, shows the two base64url values for copying, stores nothing and transmits nothing. Repository-scoped, released by SG-1 |
| **F-9** | `freedom-blades.rpgworld.org` is **already live** and currently serves `design-prototype/` as a static site from the existing Caddy block. The delivery plan requires the production frontend to adapt the visual language **without serving** `design-prototype/`, and TC-UI-06 asserts exactly that | Pre-existing condition, not a defect introduced here | The portal's site block replaces it at cutover. Recorded so the replacement is a deliberate step with a stated consequence — the prototype preview at that URL disappears — rather than a surprise |
| **F-10** | The host's TLS is a **Cloudflare Origin CA** wildcard for `*.rpgworld.org` (valid to 2040), which is trusted by Cloudflare and by no public browser. **This reverses D-i:** the DNS record must stay **proxied**, and a DNS-only record would produce a certificate error for every visitor. The consequence is immediate, not deferred: with Cloudflare in front, the right-most `X-Forwarded-For` entry — the one N-34 trusts — is Cloudflare's address, so the N-30/N-31 authentication limiter would treat **every visitor on the internet as one source** and its ten-starts-per-ten-minutes budget would be shared globally | **Important — would have produced a real availability and rate-limiting defect** | Corrected in D-i. `infra/caddy/freedom-blades-portal.caddy.tmpl` sets `X-Forwarded-For` from `CF-Connecting-IP` so the application still sees exactly one hop. **Residual:** a request reaching the origin port directly could spoof that header; the operator-address restriction is the interim control and restricting the origin to Cloudflare's published ranges is a deployment-gate item |
| **F-11** | `/etc/ssl/rpgworld/cloudflare.key` — the origin private key shared by all four sites including the live Foundry instances — is mode `-rw-r--r--`, **world-readable**. Any local account on this host can read it and present itself to Cloudflare as this origin | **Important — host security, pre-existing and outside this package's scope to fix** | Reported to the Operations Owner with the one-line remedy (`chmod 600`, `chown root:root`). **The file was not read**; the finding comes from directory metadata alone. Not remediable by the Technical Lead, who holds no root authority on this host |
| **F-12** | The existing `freedom-blades.rpgworld.org` Caddy block injects its own `Content-Security-Policy`, `X-Frame-Options`, `Referrer-Policy` and others. The portal sets its own (N-26) and **deliberately omits `X-Frame-Options`** in favour of `frame-ancestors 'none'`. Two `Content-Security-Policy` headers are both enforced by browsers, so the proxy's policy would silently intersect with the application's and break pages P3.4's tests certify as working | **Important — would have broken the portal and contradicted TC-SEC-05** | The new site block adds **no** security header at all and says why. Header ownership sits entirely with the application, which is what makes TC-SEC-05 and TC-SEC-07 mean the same thing |
| **F-15** | **The passkey break-glass login cannot be completed in a browser.** `emergency.html` renders the security-key section as a heading and the sentence "Present an enrolled security key." — **no button, no form, no script hook** — and `adapters/web/static/` ships exactly three files: the stylesheet, the emblem and vendored HTMX. There is **no application JavaScript at all**, and `navigator.credentials.get()` cannot be driven by HTMX. Routes R-07 (`POST /v1/auth/emergency/webauthn/options`) and R-08 (`.../verify`) exist and are service-tested, and nothing in the browser can call them. Observed by opening the page with two real credentials enrolled: the only usable control is the recovery-token form | **Blocking — authentication capability.** The delivery plan's P3.1 deliverable is a break-glass login using "pre-enrolled WebAuthn/passkey credentials **for normal break-glass use**", with the host-local recovery grant as the last resort for when every passkey is lost. As shipped, the last resort is the *only* resort, and the two enrolled credentials cannot be used at all | Route to **Gemini** as the frontend owner per delivery plan §5 P3.5, or to Claude if the Acceptance Authority prefers. The fix is frontend-only and crosses no contract: a small same-origin script driving the two accepted routes, a control in the template, and the new asset added to `asset-integrity.sha256`. CSP already permits `script-src 'self'`; TC-SEC-10's no-inline-script rule is satisfied by a served file. **A-05 cannot close until a passkey login actually succeeds**, so this blocks exposure |
| **F-16** | Nothing in the suite asserts that a human can *complete* break-glass login. P3.1 proves R-07/R-08 by posting synthesized payloads; P3.4 proves the template renders, escapes and carries no inline script. Both pass with the browser half absent. This is the same shape as F-14: the first defect that only appears when a person opens the page | **Important — coverage.** It is the direct cause of F-15 surviving two gates | The P3.5 traceability must record that TC-BG-02's browser half is **Not Run**, alongside TC-SEC-07's, rather than inheriting a pass from the service-level cases. Raised for Codex |
| **F-18** | **A password verifier was committed to a repository artifact.** `infra/caddy/freedom-blades-test.caddy` carried a concrete bcrypt Basic Auth verifier, authored by this package. Verified rather than assumed: the file is untracked on every branch, but a harness checkpoint commit (`refs/claude/checkpoint-e3e17315`) snapshotted it, so **it did enter Git history** — on no branch and no remote-tracking ref, and `refs/claude/*` is not pushed by `git push` | **Blocking — credential material (Codex C35-01).** Local-only reach, but read during review, so the password is spent regardless | Removed; the gate is now a host-local fragment imported fail-closed. Rotation script written; **rotation is a required Operations Owner action**. Structural tests over every repository Caddy artifact, falsified. Full account in the C35 remediation handoff |
| **F-19** | **`/healthz` was publishable through the proxy.** The catch-all `handle` proxied it, while the accepted operational contract puts health on the loopback bind and states it is not published by Caddy | **Blocking — perimeter (Codex C35-02).** An unauthenticated reader of check results learns the deployment's internal state | The health refusal is now the first handle block, covering all three path forms, answering `404` rather than `403`. Ordering proved in the adapted configuration — health at route index 2, proxy at index 9 — and asserted by a falsified test. **The host is still unchanged**; correcting it is a separate authorized action |
| **F-17** | **The navigation is static and signed-out.** `base.html` always includes `includes/header.html`, which renders the same three links — Characters, Emergency Access, **Login** — to every caller on every page, with no conditional on session state. Consequences observed on the deployed portal: a signed-in user is shown "Login"; **`grep -rln logout` across the whole template corpus returns nothing, so there is no way to sign out through the interface**; and there is no link to the administration, Council, reconciliation or audit surfaces, so the entire privileged surface is reachable only by typing a URL | **Important — usability and session hygiene.** No authorization boundary is weakened: every route still authorizes server-side. But a portal with no logout control fails the "logout and revocation" expectation a reviewer will look for at the gate, and an administrator who cannot reach the administration page cannot administer | Frontend-only; add to Gemini's scope alongside F-15, or commission separately. Requires the header to reflect the caller's capabilities, which VM-01/VM-05 already carry. **Confirm with Peter whether P3.4 was ever asked for a capability-aware header** before classifying it as a defect rather than a second scope gap |
| **F-13** | `build_health_view` calls `settings.kill_switch_file.exists()` unguarded. `Path.exists()` raises `PermissionError` rather than returning `False` when the process cannot traverse the containing directory, so a mis-permissioned kill-switch directory turns `/healthz` into a `500` instead of a health report saying `kill_switch: false`. Observed directly: the endpoint returned the safe error page with a correlation ID | **Minor — robustness.** The safe-error boundary behaved correctly and leaked nothing; the health checks around it are unaffected when permissions are right | Raised for Codex, **not fixed under this plan** — `application/web/startup.py` is accepted P3.1/P3.3 surface. The observation is worth its own line because a health endpoint that fails closed on a permissions fault is least useful exactly when an operator most needs it |
| **F-8** | `enroll` accepts the credential id and public key **without recording or validating the relying-party identifier the ceremony used**, while authentication verifies `expected_rp_id` against the running service's `WEB_WEBAUTHN_RP_ID` — and `config.py` requires that RP ID to equal the public origin's own host. A credential created at `http://127.0.0.1:8001` is therefore stored happily and **can never authenticate** against `freedom-blades.rpgworld.org`, with nothing at enrollment time saying so. The failure surfaces only at the moment somebody is locked out and reaching for it | **Important — operator-safety gap.** Not exploitable: the strictness that causes it (RP ID must equal the portal's own host, N-60/S-09) is a control worth keeping | Two parts. Procedurally, §13.2's criterion 2a now requires the ceremony's RP ID to match the intended target host and requires one **successful authentication** before A-05 closes. Structurally, the gap is raised for Codex: the ceremony's RP ID is knowable at enroll time and could be recorded and checked. **No behavior change is made under this plan** — it would touch an accepted P3.1 contract surface and belongs to Peter's decision after review |

**No blocking security, authorization, identity, atomicity, data-integrity,
recovery or reliability finding was identified in this read-only audit.** That
statement is scoped to what a read-only audit plus the local suites can show; it
is not a substitute for Codex's two independent passes.

---

## 15. RAID dispositions

**No RAID disposition is changed by this document.** Today's evidence — a green
local suite, a clean worktree, a single linear migration head — does not change
what I-06, A-05, A-06 or R-23 assert, and a disposition must move on evidence
rather than on activity. Their current statuses remain correct as written:

- **I-06 — Open.** Blocks staging/production exposure and production-readiness acceptance.
- **A-05 — Open.** No credential has been enrolled on any host; the emergency route exists but cannot be used.
- **A-06 — Open.** The limiter half has automated evidence; the representative-operation half does not.
- **R-23 — Active accepted residual.** TC-UI-01/02, TC-UI-08 and TC-UI-09 remain Not Run.

Each will move only when §13's criteria are met, with the evidence cited.

---

## 16. Peter's authority and participation checkpoints

| # | Checkpoint | What is being asked | Blocking? |
|---|---|---|---|
| **P-1** | Approve this plan (**SG-1**) | Release EX-1…EX-9, repository-scoped only | **Done — approved 2026-08-23** |
| **P-2** | Decide the browser question (§9.4) | Workstation browser vs. a headless-browser dependency | **Done — workstation browser, 2026-08-23** |
| **P-3** | Authorize and participate in the staging build (**SG-2**) | SP-01…SP-06: DB/roles, secrets, Discord app/guild, units, proxy, migration | Blocks all of I-06 |
| **P-4** | Authorize and participate in the credential ceremony (**SG-3**) | SP-07, SP-20…SP-22 | Blocks A-05 |
| **P-5** | Perform the real-device check | SP-18 / TC-UI-08 | Blocks that row of R-23 |
| **P-6** | Decide screen-reader capacity | SP-19 / TC-UI-09, or an explicit "remains Not Run" | Blocks that row of R-23 |
| **P-7** | Record availability windows | Turns the effort estimate into a forecast | Blocks any calendar commitment |
| **P-8** | Gate decision (EX-14) | After both Codex passes | **Peter alone** |

---

## 17. The next bounded execution step

**Requested now:** P-1 (approve this plan) and P-2 (the browser decision).

**On P-1 alone, and nothing more:** EX-1 (final traceability), EX-2 (F-1
reconciliation) and EX-3/EX-4 (migration and backup/restore rehearsals against
the guarded disposable database). These mutate nothing outside the repository and
`freedom_test`, produce no staging claim, and close no RAID item.

Everything else waits for SG-2 or SG-3.

---

## 18. Frontend code-review disposition and next session — 2026-08-24

The readiness facts in §§4 and 14 describe the state observed when this plan was
written. Subsequent P3.5 work supplied the missing browser WebAuthn client and
server-owned shell, and Codex accepted their repository implementation on
2026-08-24 after two remediation rounds. The accepted client has strict
R-07/R-08 refusal/UUID validation, strict Base64URL decoding, exact safe redirect
handling, duplicate-activation protection, truthful no-JavaScript behavior and
durable workflow tests.

This does **not** change the evidence-level blockers identified here:

- TC-UI-01/02 are still Not Run in a real browser;
- TC-BG-02's browser/physical-authenticator path is still Not Run;
- A-05 still requires two successful real-credential assertions against the
  intended origin/RP ID and Security Reviewer confirmation;
- R-23 stays active and the Phase 3 gate stays open.

Peter stated that the supervised work must occur in a few hours. The controlled
procedure and evidence schema are now recorded in
`phase-3-p3-5-frontend-code-acceptance-and-supervised-session-plan.md`. That
statement records intent and near-term sequencing only; it is not a Passed,
Scheduled-with-guarantee or acceptance claim.
