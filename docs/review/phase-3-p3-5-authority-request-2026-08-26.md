# P3.5 authority request — Claude to Peter Duscha

**Date:** 2026-08-26 · **From:** Claude, P3.5 working Technical Lead ·
**To:** Peter Duscha — Security Reviewer, Operations Owner, Data Owner,
Acceptance Authority

**Repository:** `/opt/freedom-blades/platform` · **Branch:** `docs/platform-plan`
· **Head commit:** `0e3929a`, plus the working-tree P3.5 changes

**Prepared under** `docs/review/Handover information` (Codex → Claude, 2026-08-26)
**Step 1**, which requires one request covering every authority I cannot supply
myself.

**What this document is:** a request for eight decisions — six from the handover's
Step 1, plus two forced by defects found while preparing the sittings (§§5a, 5b). **What it is not:** a
gate decision, a claim that any procedure has run, an SG-2/SG-3 grant, a
deployment, a credential ceremony, permission to use production data, or the
start of Phase 4. Nothing below executes until its own authority is recorded.

---

## 0. The eight decisions, in one place

> **ANSWERED IN FULL on 2026-08-26 by Peter Duscha.** 1 confirm · 2 yes · 3 yes ·
> 4 yes · 5 yes · 6 today, excluding 20:30–22:30 MET · 7 option 1 · 8 route A.
> **The canonical record is change-log `C-P3.5-V` and the execution plan's §0.2
> checkpoint table**, not this document; the table below is left as it was asked
> so the request and its answers can be read against each other.

| # | Your role | Decision asked | What it unblocks | Your answer |
|---|---|---|---|---|
| **1** | Security Reviewer | **Confirm or reject D-o** and change-log **C-P3.5-U** | A-05 criterion 4b's definition; operational contract §7 items 9/10 | |
| **2** | Operations Owner | **Grant SG-2** for the staging build and the named procedures in §6 | Every remaining I-06 procedure — nine `Not Run` rows | |
| **3** | Operations Owner | **Grant an SG-3 extension** for the two remaining credential-touching procedures, and be present for each | A-05 criteria 4a and 4b | |
| **4** | Operations Owner | **Authorize deploying the reviewed N-7 fix** by service restart, and an **SP-12 re-run over a fresh journal interval** | TC-OPS-05, currently **Failed** | |
| **5** | Operations Owner + Security Reviewer | **Authorize SP-27** exactly as specified in §5 | A-05 criterion 4b | |
| **6** | Delivery Lead | **Confirm the window** in §6, or give the evenings you actually have | Turns effort into a forecast (checkpoint P-7) | |
| **7** | Security Reviewer | **Decide A-05 criterion 4a's disposition** (finding **N-10**) — the criterion is not executable as written | Sitting M-1b | |
| **8** | Operations Owner | **Choose route A or B for SP-10's instrument** (finding **N-11**, C-8 proposal) | Sitting M-4 | |

Decisions 2–5 are host actions. Decision 1 is a decision about wording that
**re-imposes** a control rather than relaxing one. If you reject decision 1, say
so plainly and I revert to D-n; you should know that Codex classified D-n's
premise as **Blocking**, so a reversion would need its own review answer.

---

## 1. Decision 1 — confirm or reject D-o (Security Reviewer)

**Record:** decision **D-o**, execution plan §0.2 and §13.2 criterion 4;
change-log **C-P3.5-U**; operational contract §7 items 9 and 10.

On 2026-08-25 you approved **D-n**, which moved S-15's production-refusal
evidence out of A-05 to the deployment gate. Codex's interim review found the
argument false: it treated *production-marked* and *publicly exposed* as the same
event. They are not. `run_resource_checks` is a plain function
(`application/web/startup.py:80`), so S-15's production branch is reachable with
**no listener, no bind and no route**.

**D-o corrects it:** 4b stays an A-05 closure criterion, discharged by the
guarded exercise **SP-27** (§5); 4c is a deployment-gate re-observation, defence
in depth only, never a substitute. 4a is unchanged. It is implemented in the
documents already, because it re-imposes a control — but it supersedes a decision
you recorded, so it is **not treated as decided until you confirm it**.

**Asked:** confirm D-o and C-P3.5-U, or reject with your reason.

---

## 2. Decision 2 — SG-2, the staging build and its procedures (Operations Owner)

SG-2 releases SP-01…SP-06, SP-08…SP-19 and plan-SP-23 — every remaining I-06
procedure. The environmental blockers the execution plan recorded are gone: the
staging build exists and is healthy, the worker is active, `freedom_staging` is
at head `0013` with a genuinely restricted runtime role, and a real browser has
already been driven against the deployed portal. **What is missing is execution
of the named procedures, not readiness for them.**

Three prerequisites are recorded as deviations rather than repaired silently:

- **N-5** — `freedom_staging` is owned by `foundry`, shared with `freedom_dev`
  and `freedom_test`, not by a dedicated staging owner role. The control that
  matters is intact: the runtime role `freedomweb` is separate and holds `arw`
  with no DDL. **My recommendation is to record the deviation and leave it.**
  Repairing it means `ALTER DATABASE OWNER`/`REASSIGN OWNED` against a live
  staging database, which is yours to authorize if you want it.
- **SP-01/SP-06** — the end state is right; nobody recorded reaching it. The
  sittings supply the dated execution record.
- **N-3** — the deployed portal exposes **no snapshot-submission route**, so
  TC-OPS-03 and TC-PERF-01/02 need the supervised transport step M-7a first.
  No route is added to the deployed proxy under this package.

**Asked:** grant SG-2 for the procedures listed in §6, and participate where §6
names you.

---

## 3. Decision 3 — SG-3 extension for the two remaining credential procedures

**Stated accurately, because the record is not uniform.** You granted **SG-3 on
2026-08-24** and the credential ceremony was executed in full that evening:
SP-07, SP-20, SP-21 and SP-22 are all Passed, two real passkeys authenticate
against `https://freedom-blades-test.rpgworld.org`, and A-05 criteria 1, 2, 2a,
3, 5, 6, 7, 8 and 9 are met. **I am not asking you to repeat any of that.**
(`status.md` currently says "SG-3 remains ungranted"; that wording is stale and
I flag it in §9 rather than editing it silently.)

Two credential-touching procedures remain, and **neither touches a real
credential**:

| Procedure | What it does | Credential material |
|---|---|---|
| **M-1b — A-05 criterion 4a** | A throwaway portal process on a spare port against the **disposable** `freedom_dev`, marked `WEB_ENVIRONMENT=staging`, observed below and at the N-13 threshold, capturing the S-15 **warning** and the `/healthz` `break_glass_credentials` boolean | **Synthetic records only.** Your real credentials are never manipulated — `retire` refuses below two (criterion 3), and the only other route would be a database-owner action against your own credentials, which the handover forbids |
| **M-1c — A-05 criterion 4b (SP-27)** | §5 below | **Synthetic records only** |

The deployed portal is untouched by both.

**Asked:** grant an SG-3 extension covering exactly M-1b and M-1c, and be present
for every step of each.

---

## 4. Decision 4 — deploy the reviewed N-7 fix and re-run SP-12

**Why this is owed.** SP-12 ran on 2026-08-26 and **TC-OPS-05 failed**: uvicorn's
default access log writes the OAuth authorization code and state to the journal
in clear text on `/auth/discord/callback`. The finding is **N-7**. The fix is in
`tools/portal_server.py`, has **59 regression tests** plus a live end-to-end
proof against a real uvicorn, and **passed Codex's focused re-review with no
remaining finding** after two rounds.

**The deployment is a service restart and nothing else**, and I can state exactly
why from the deployed unit:

- `WorkingDirectory=/opt/freedom-blades/platform` — the portal runs from **this
  working tree**, so the fixed source is already on disk;
- `ExecStart=… -m uvicorn tools.portal_server:application --factory …` — the unit
  file is **unchanged** by the fix, so no unit surgery and no SG-2 unit work;
- the running process started **2026-08-25T22:46:33Z**; the fix was written
  **2026-08-26T09:36:51Z**. The running process predates it.
- the only code file modified in the working tree is `tools/portal_server.py`;
  everything else uncommitted is documentation and one new test file.

**Then SP-12 is re-run over a fresh journal interval** — a `--since` bounded at
the restart, not the old window — and must show the callback line rendering as
`?<redacted>` with method, status and path intact.

**Rollback trigger:** `/healthz` does not return `status: ok` within 30 seconds
of the restart, or the access log stops emitting. **Rollback:** restore
`git show HEAD:tools/portal_server.py` over the file and restart; the pre-fix
process is what is running today, so the rollback state is the known-good state.

**Asked:** authorize the restart of `freedom-web.service` (root) and the SP-12
re-run. TC-OPS-05 stays `Failed` until that re-run passes.

---

## 5. Decision 5 — SP-27 in full, as the handover requires it stated

**Purpose:** observe S-15's production-class refusal **before exposure**,
discharging A-05 criterion 4b. **Owner:** you authorize and supervise; I drive.
**Duration:** 20 minutes. **No socket is ever opened.**

1. Create a **disposable** `freedom_production` database — the name
   `EXPECTED_DATABASES` requires for this environment — migrate it to head, and
   seed a protected administrator account holding **fewer than two** enabled
   credentials, using **synthetic** credential records. It is never a copy of,
   and never restored from, any real data.
2. **Block outbound egress** for the exercising account with the single
   `iptables` OUTPUT rule already proven by SP-25, so no live Discord contact is
   possible even accidentally.
3. Build production-marked settings — the accepted production origin, redirect
   URI and guild ID are **identifiers, not secrets**; the client secret is a
   syntactically valid **placeholder**, never the real one — and call
   **`run_resource_checks(settings, engine)` directly**
   (`application/web/startup.py:80`). This is what makes the exercise safe:
   `run_resource_checks` is a plain function, so S-15 is reached **without
   uvicorn, without a bind and without a route**. There is no listener to expose,
   so no public traffic can reach it and no production cookie or OAuth callback
   can be delivered to it.
4. Record the literal `ConfigurationProblem` naming **S-15**.
5. Seed the second synthetic credential and repeat, recording that the check now
   passes.
6. **Mandatory teardown:** drop the database, remove the egress rule, delete the
   temporary environment file. Each recorded as done.

**Never recorded:** credential material, the real client secret, any real
account, or any value from a live production system.

**Rollback trigger:** any step that would require a real secret, a real account,
a listener, or a live provider call. **Rollback:** run the §6 teardown
immediately and stop the sitting.

**Asked:** authorize SP-27 exactly as written.

---

## 5a. Decision 7 — A-05 criterion 4a is not executable as written (N-10)

**Found while building the harness for it, and it is the same shape as Codex's
B-1: two halves of one criterion that cannot both hold.**

Criterion 4a asks for the threshold observation **"under `WEB_ENVIRONMENT=staging`"**
and **"on a disposable database with synthetic credential records"**. Each
environment is bound to exactly one database name
(`adapters/database/config.py:66`), so a staging-marked process must target
`freedom_staging` — the deployed staging database holding your two **real**
credentials, the records the same criterion says must never be manipulated.
**Verified by observing the refusal, not by reading the rule:** a staging-marked
build pointed at `freedom_dev` is refused by **S-01**.

Three options. **My recommendation is (1).**

| | Option | Cost | What it gives up |
|---|---|---|---|
| **1 — recommended** | Take the observation under the **`development`** marker on disposable `freedom_dev`, with synthetic credentials | none; ~15 minutes, no host mutation | the marker string itself. S-15 branches on `is_production` alone, so `development` and `staging` take the **identical** path; and the live `environment: staging` marker is already evidenced by `/healthz` on the deployed portal |
| **2** | Stand up a throwaway **second PostgreSQL cluster** holding a disposable `freedom_staging` | a whole cluster, and a new moving part on the host | nothing — it satisfies the wording literally |
| **3** | Temporarily disable one of your **real** credentials on deployed staging | — | **excluded by the criterion's own text.** I do not recommend it and the harness refuses it |

**Asked:** choose 1, 2 or 3. Until you do, the harness refuses `staging` outright
and M-1b does not run.

---

## 5b. Decision 8 — SP-10 has no instrument (N-11)

`infra/postgresql/backup-restore-drill.sh` **refuses any target but
`freedom_dev` and `freedom_test`, by design**, and its header states that as a
safety property. SP-10 is TC-OPS-02's staging half, so it needs either that
refusal relaxed or a different instrument.

`phase-3-p3-5-c8-staging-drill-guard-proposal.md` sets out both routes in full,
with the proposed diff and three falsifying tests. In short:

- **Route A — extend the guard** behind two independent, non-default signals.
  Keeps the inventory comparison that makes TC-OPS-02 a *verified* restore rather
  than a successful dump. **Weakens a stated invariant**, which is why it is your
  decision and Codex's review, not mine.
- **Route B — a written manual procedure.** Changes no code and produces weaker
  evidence, with no falsifying test at all.

**My recommendation is A**, because plan §14.3 asks for "restore tests, not
merely backup success messages". **Nothing is applied until you choose**, and
M-4 cannot start before then.

---

## 6. Proposed window, and every procedure's owner, duration, rollback trigger and evidence destination

**Availability assumption (D-g):** most evenings, ~30 minutes. Every sitting below
fits one evening; none assumes a continuous multi-hour window. **Total attended
time ≈ 5 hours across twelve sittings.**

**Proposed window:** evenings of **2026-08-26 → 2026-09-03**, in the order below.
No date is committed until you record your availability (checkpoint P-7).

| # | Sitting | Procedures | Who acts | Duration | Rollback trigger → action | Evidence destination |
|---|---|---|---|---|---|---|
| **M-1a** | N-7 deploy and monitoring re-check | deploy + **SP-12** (TC-OPS-05) | You restart (root); I read the fresh journal | 25 min | `/healthz` not ok within 30 s, or access log silent → restore `git show HEAD:tools/portal_server.py`, restart | `phase-3-p3-5-staging-and-operations-evidence.md` §5.2, new dated subsection; TC-OPS-05 row |
| **M-1** | Prerequisite attestation | **SP-02**, **SP-03** | You attest that no staging secret shares a production value; you read out staging Discord application/guild/role **IDs** | 25 min | A secret value would have to be spoken or written → stop before it | same doc §3, rows SP-02/SP-03 |
| **M-2** | Kill switch | **SP-09** (TC-OPS-01) | You engage layer 1; we confirm every route `503` except `/healthz` and `/static/*`; you confirm bot and Foundry unaffected; you release | 25 min | Routes stay 503 after release → restart the portal; if still 503, stop and report | same doc §3, row SP-09 |
| **M-3** | Deployed refusals and limit parity | **SP-08** (TC-OPS-04), **SP-13** (TC-LIM-02) | You restart with each deliberately wrong value and read the refusal; you read the **deployed** Caddy limits | 30 min | Correct value does not bring the portal back → restore the pre-change copy of the environment file; if that fails, engage the kill switch and stop | same doc §3, rows SP-08/SP-13 |
| **M-1b** | A-05 criterion 4a *(needs decision 7)* | criterion 4a | You authorize; I run a throwaway portal on a spare port against disposable `freedom_dev`, synthetic credentials | 15 min | Anything would touch a real credential → stop. **Teardown:** kill the process, drop the synthetic rows | same doc, new §A-05 4a subsection; inventory §3 row 4 |
| **M-1c** | A-05 criterion 4b | **SP-27** (§5) | You authorize and supervise; I drive | 20 min | §5's trigger → §5 step 6 teardown, stop | same doc §3, row SP-27 |
| **M-4** | Backup, restore, rollback on staging *(needs decision 8)* | **SP-10** (TC-OPS-02 staging half) | You act as Operations Owner: pre-migration backup, `upgrade`→`downgrade`→`upgrade`, restore, inventory comparison | 30 min | Downgrade fails or leaves the schema inconsistent → restore from the pre-migration backup taken at the start. **No forward repair inside the sitting** | same doc §3, row SP-10 |
| **M-5** | Browser observations | **SP-14** (TC-SEC-07 browser half), plan-**SP-23** remainder | You drive your own browser: headers/CSP on normal, early and error responses; the OAuth redirect under `form-action 'self'`; skip links, HTMX paths, reduced motion, real-engine contrast; **record the exact Chrome build** | 30 min | Read-only; none. A screenshot would carry real data → redact at source, never afterwards | `phase-3-p3-5-accessibility-and-browser-evidence.md`; staging doc §3 row SP-14 |
| **M-6** | Real device | **SP-18** (TC-UI-08) | You inspect at 320/768/1280 and 200% on your own hardware; record device and OS | 15 min | Read-only; none | accessibility doc, TC-UI-08 row |
| **M-7a** | Snapshot transport | C-7's procedure (**N-3**) | You drive the Foundry side of a supervised submission of `Characters (active)` into `freedom_staging`; read out the inactive folder's Actor count from the selection dialog | 30 min | An Actor name, payload or warning text would enter an artifact → stop before writing it. **Teardown at M-7d:** shred the artifact, truncate the staging import tables | staging doc, new §transport section |
| **M-7b** | End-to-end flow | **SP-11** (TC-OPS-03) | You: OAuth login → member read → Council link change → folder selection → preview → confirm → audit search | 30 min | Any unexpected mutation outside the flow → stop, record, do not retry | staging doc §3, row SP-11 |
| **M-7c** | Performance | **SP-15** (TC-PERF-01/02), **SP-16** (TC-PERF-03) | You authorize; I measure and sample RSS with the bot and Foundry running | 30 min | Worker peak RSS approaches or exceeds N-47's 1 GiB → **that is a finding, not a reason to raise N-47**: record, stop, route the numeric change through delivery-plan §7 | staging doc §3, rows SP-15/SP-16. Apply reported **n = 1** real plus two synthetic (D-m) |
| **M-7d** | Worker recovery and teardown | **SP-17** (I-06, A-06) + D-l teardown | You authorize SIGTERM mid-attempt; we observe lease expiry, reaper requeue, lost response, and a retry returning the committed effect as a duplicate; then shred and truncate | 25 min | **Two durable effects appear** → stop immediately; that is a Blocking finding, not a retryable step | staging doc §3, row SP-17, plus a teardown confirmation line |
| **M-8** | A-05 close-out | criterion 10 | You confirm break-glass readiness, **last**, after everything above | 20 min | Any preceding criterion still open → criterion 10 is not asked | inventory §3 row 10; RAID A-05 |

**Standing conditions for every sitting** (execution plan §8.2, inventory §8.2):
staging only; loopback bind behind the accepted proxy boundary; no production
database, backup or real player data beyond D-l's named exception; no secret,
token, public key, COSE blob, cookie or CSRF value is read, printed, pasted or
committed; you are never asked to paste a credential into chat or a file; the bot
and Foundry stay running during the performance work; nothing under
`/opt/discord-bots` is deleted.

**Standing stop rule:** anything that would change architecture, authority,
privacy, data ownership, production behaviour, migration/rollback strategy or an
accepted numeric contract stops and comes back to you. An unavailable check stays
`Not Run` — **it keeps the gate open; it is not a waiver.**

---

## 7. What I have already done, with no further authority

**Complete as of 2026-08-26.** SG-1 released all of it; none of it mutated
staging, production, the proxy, a service or a credential. Every sitting below is
therefore spent observing rather than preparing:

| # | Preparation | Gates which sitting |
|---|---|---|
| **C-5** | Bounded synthetic fixtures shaped to the **real** size distribution — a 32-Actor-class folder at ~16 MB and a worst case at the N-20 64 MiB bound, generated at run time, never committed | M-7c |
| **C-6** | The RSS-sampling and wall-clock harness, and the **bounds written down in advance** for TC-PERF-03 and portal responsiveness | M-7c |
| **C-7** | The supervised snapshot-transport procedure, with teardown and shredding steps | M-7a |
| **C-8** | A proposed extension of the backup/restore drill's target guard to `freedom_staging`, as a reviewable diff with a falsifying test — **not applied** | M-4 |
| **C-9** | Click-by-click run sheets for every sitting above: what to type, what to expect, no configuration file or protocol term to interpret | all |
| **C-11** | The criterion-4a observation harness | M-1b |
| **C-12** | The SP-27 harness and its scripted teardown | M-1c |
| **C-10** | Full suites serially against the disposable database, every available check, `git diff --check`, every skip and warning explained — **last** | EX-10 |

---

## 8. What this request does not do

- It closes **no** RAID item. **I-06** and **A-06** remain Open, **A-05** Open at
  two criteria, **R-23** an active accepted residual.
- **TC-OPS-05 remains `Failed`.**
- It requests **no** gate decision, and no gate decision may be inferred from it.
- It starts **no** Phase 4 work. Phase 4 remains unauthorized until you record the
  Phase 3 gate decision after **EX-11** and **EX-12**, which are still owed.
- It converts **no** partial observation into a pass, and no `Not Run` into
  `Passed`.
- No secret, credential, token, public key, raw address or unnecessary identity
  datum was read or recorded in producing it.

---

## 9. Discrepancies I am flagging rather than editing

**N-9 — the SG-3 record is not uniform.** `docs/project-management/status.md`
states in several places that "SG-2 and SG-3 remain ungranted", while
`phase-3-p3-5-supervised-session-evidence-2026-08-24.md` §7 records SG-3
**approved by you on 2026-08-24**, and its named procedures SP-07, SP-20, SP-21
and SP-22 all executed and Passed that evening.

**Class: Minor — record accuracy. No evidence is affected**; every observation
stands and no procedure ran without authority. The correct reading is that SG-3
was granted and consumed, which is why §3 asks for an **extension** rather than a
fresh grant. I have not rewritten the status entries, because they are historical
statements; the correction belongs in a dated current-state update, which I will
add once you answer §0. Flagged for Codex.

**N-12 — two unexplained tests, and four files the tree cannot agree about.** The
65 pre-existing bot-suite files collect **2379** tests today, while the
2026-08-26 verification record states **2377 passed**; no tracked test file has
been modified since. Separately and certainly, **four tracked test files are
`0600` in the working tree while Git records `100644`** —
`tests/test_filesystem_layout.py`, `tests/test_snapshot_api.py`,
`tests/test_snapshot_recovery_documentation.py` and
`tests/web/test_identity_migration_settings.py`.

**Class: Minor — evidence hygiene.** Every one of them passes. It matters because
a suite whose file set depends on **who runs it** produces counts a reviewer
cannot reproduce. `chmod 644` on the four would restore exactly what Git already
records, but they are not this package's files, so it is offered rather than
taken. **I cannot account for the 2-test difference** and do not assert which
figure is wrong; today's count is recorded beside the earlier one in the staging
evidence §4.2. Flagged for Codex.
