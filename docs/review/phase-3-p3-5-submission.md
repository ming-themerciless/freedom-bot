# P3.5 submission — Phase 3 gate evidence package

**Date:** 2026-08-27 · **Prepared by:** Claude, P3.5 working Technical Lead ·
**For:** Codex (EX-11 and EX-12) and Peter Duscha (Acceptance Authority)

**Repository:** `/opt/freedom-blades/platform` · **Branch:** `docs/platform-plan`
· **Last commit:** `bbbe977`, which carries the larger half of this package ·
**Working tree:** 34 modified and 4 new files, **uncommitted**, listed in §7a

> **This document requests the Phase 3 gate decision. It does not make it, and no
> gate decision may be inferred from it.** It also requests **EX-11** and
> **EX-12** as two distinct Codex passes. No prior focused review consumes
> either.
>
> **Phase 4 has not begun and remains unauthorized.**

---

## 1. What this package was asked to do

P3.5 is the Phase 3 integration and gate-evidence package: remediate every
blocking and important finding, assemble requirements-to-evidence traceability,
execute the staging and operational procedures that only a deployed system can
produce, and submit the result for two independent reviews and Peter's decision.

**The single most consequential thing in it:** the procedures were actually run
against a live system, and **most of what is worth reading below was found by
running them**, not by reading code.

---

## 2. Disposition of the four RAID items this package owns

| Item | Disposition | What remains |
|---|---|---|
| **A-05** — protected administrator and credentials | **Open on criterion 10 alone.** Criteria 1, 2, 2a, 3, **4a**, **4b**, 5, 6, 7, 8, 9 are Met | Criterion 10, the Security Reviewer's break-glass readiness confirmation, which comes last by its own terms. Criterion **4c** is owed at the deployment gate as defence in depth |
| **I-06** — staging/browser/device evidence | **Open, substantially evidenced.** TC-OPS-01…05 executed, TC-LIM-02 exact, TC-SEC-07's browser half in part, worker recovery observed, staging backup/restore/rollback done, **14 of 15 startup refusals observed** | S-13 is test-enforced and not observable on a live host; TC-OPS-03's end-to-end flow used synthetic input; three remediations are undeployed (§7); and the Operations Owner and reviewers have not accepted it |
| **A-06** — PostgreSQL as job-queue and limiter substrate | **Open, and now measurable rather than argued.** Preview, apply, worker peak memory, portal responsiveness and lease/fence behaviour all measured against bounds **stated before the run**; recovery produced exactly one durable effect | Criterion 1 asks for representative *staging* conditions; the co-located load was real but not deliberately shaped |
| **R-23** — accessibility residual | **Active accepted residual, thinner than it was.** TC-UI-01/02 passed, **TC-UI-08 passed across two real devices**, skip link passed, reduced motion verified | Screen-reader traversal **permanently Not Run for Phase 3** under D-f; real-engine contrast and HTMX-enhanced paths Not Run |

**Two threat-model residuals are closed by measurement:** **RR-05** (worker peak
memory, never measured) and **RR-06** (a real-folder apply, never measured).

---

## 3. What was executed, and where the evidence is

All procedure records are in
[`phase-3-p3-5-staging-and-operations-evidence.md`](phase-3-p3-5-staging-and-operations-evidence.md),
§§2 and 5A–5M. Accessibility and browser results are in
[`phase-3-p3-5-accessibility-and-browser-evidence.md`](phase-3-p3-5-accessibility-and-browser-evidence.md).

| Procedure | Outcome |
|---|---|
| SP-02, SP-03 — prerequisite attestations | **Passed.** Separation corroborated independently by Discord snowflake creation times |
| SP-08 / TC-OPS-04 — deployed startup refusals | **14 of 15.** S-02, S-05, S-11 in both directions; S-11 and S-14 proved under systemd with the restart counter climbing; S-15 under a production marker in SP-27. **S-13 test-enforced, not observable live** |
| SP-09 / TC-OPS-01 — kill switch | **Passed**, including the half that matters: the Discord bot and Foundry confirmed unaffected |
| SP-10 / TC-OPS-02 staging half | **Passed**, and it found Blocking finding **N-20** |
| SP-12 / TC-OPS-05 — monitoring output | **Passed at the third observation**, after **N-7** and **N-13** were both fixed and deployed |
| SP-13 / TC-LIM-02 — proxy/application parity | **Passed, exact** |
| SP-14 / TC-SEC-07 browser half | **Passed in part**; raised **N-22** and **N-23** |
| SP-15/16/17 — performance and recovery | **Passed** against bounds accepted beforehand (D-s) |
| SP-18 / TC-UI-08 | **Passed** across iPhone 15 and iPad A16 |
| SP-27 — A-05 criterion 4b | **Passed**: S-15's production refusal observed **before exposure**, no listener |
| SP-28 — snapshot transport | **Executed**, route B, no proxy mutation |
| SP-29 — bounded gate-off window | **Executed**, 36 minutes, both times recorded |
| SP-19 / TC-UI-09 — screen reader | **Not Run, permanently for Phase 3** (D-f) |

---

## 4. The measurements

Every bound was **stated before the run it judges** (§11.3). Three were existing
accepted policy (N-47, N-45, change-log C-11's throughput); two had no accepted
figure and were accepted by the Acceptance Authority as **D-s**.

| Measure | Real 32-Actor folder | Bound | |
|---|---|---|---|
| Preview | 9,854 ms = **602 ms/MB** | ≤ 1200 ms/MB | ✅ |
| Apply | **19,927 ms** | < 300 s cap | ✅ |
| Worker peak memory | **302.4 MiB** | ≤ N-47 | ✅ |
| `/healthz` during both | p95 **61.2 ms**, max 145.7 ms, **zero non-200** | p95 ≤ 500 ms | ✅ |

**Against the Phase 2 baseline:** Rehearsal B measured 587 ms/MB on 2026-08-09.
Today's 602 ms/MB is **within 2.5%** — across 18 days and a Foundry version
change.

**A second real sample** (the inactive folder, 34 Actors at 282 KB each against
the active folder's 512 KB) put throughput within 8% and the memory ratio in a
stable band.

**One figure is explicitly disqualified.** A 66.7 MB synthetic preview recorded
1179 ms/MB, just under the bound. It is **not** a throughput measurement: that is
the run deliberately SIGKILLed for SP-17, and most of its 79 seconds is
lease-expiry wait. It is recorded as unusable rather than quietly cited.

---

## 5. Findings

**27 findings, N-6 through N-32. Blocking: 3 (N-20 remediated and re-verified;
N-29 remediated; N-31 remediated under C-P3.5-AF and recommended resolved by
the next re-review). Important: 15 (N-30 remediated and
accepted by the 2026-08-28 re-review; **N-32 remediated under C-P3.5-AH**,
test-only). Minor: 9.** None is withdrawn; one
(**N-15**) had its *severity* withdrawn and stands as a deviation. N-29 and N-30
were raised by the 2026-08-28 EX-11/EX-12 re-review after C-P3.5-AB.

Each class below is the one recorded with the finding, not a re-grading for this
document.

| # | Class | Finding | State |
|---|---|---|---|
| **N-20** | **Blocking** | A restore returns every row and every guard and **silently drops the runtime role's privileges** — both services crash-looped after a "verified" restore | **Remediated** (the drill re-applies grants and asserts them, falsified) and **re-verified on staging**, where the same drill now leaves both services starting clean |
| **N-29** | **Blocking** | The unfamiliar-record access-log fallback still emits a plaintext IPv4 address when it is adjacent to other word characters, despite the contract prohibiting plaintext IP addresses in every log line | **Remediated in C-P3.5-AD; the unfamiliar-record branch was accepted as satisfactory on re-review.** The overall every-log-line boundary remains open under N-31 |
| **N-31** | **Blocking** | The retained pinned Uvicorn path preserves the caller-controlled HTTP method unchanged; the accepted token syntax permits `203.0.113.7`, so a fully formatted access line discloses that plaintext address | **Remediated in C-P3.5-AF, not closed.** A pinned record whose method carries an IP literal is withheld whole under a seventh repository-owned reason; `_HTTP_METHOD` is unchanged, so extension methods survive. Evidence §5T. **Not deployed**, and the correction closes nothing — EX-11 and EX-12 are requested again |
| **N-6** | Important | The cutover moved the repo by rename; `mv` preserves the mtime and size CPython validates bytecode by, so 163 `.pyc` files still named a tree that no longer exists. Six web tests failed with `OSError: could not get source code` | Corrected (caches cleared, nothing tracked changed). **Consequence: paths quoted from any pre-correction run on this host name a vanished tree** |
| **N-7** | Important | OAuth authorization code and state written to the journal in clear text | Fixed, **deployed**, re-observed |
| **N-10** | Important | **A-05 criterion 4a is not executable as written** — it requires a staging marker *and* a disposable database, and each environment binds to exactly one database name. Established by observing S-01 refuse, not by reading the rule | **Decided 2026-08-26 as option 1 (D-p)** by the Security Reviewer. Nothing in the platform is broken; the defect was in the criterion |
| **N-11** | Important | **SP-10 had no instrument** — the drill script refuses any target but `freedom_dev`/`freedom_test` by design | **Decided as route A (D-q)** and applied the same day with three falsifying tests |
| **N-13** | Important | The deployed access log records the client IP in plaintext, which operational contract §5 prohibits | The pinned Uvicorn path is fixed with a keyed per-process pseudonym and correlation normalization, but **N-29 keeps the overall every-log-line requirement open** |
| **N-14** | Important | Evidence validity and sequencing — found by chasing the discrepancy rather than by a check | Recorded; the sequencing rule is now written into the run sheets |
| **N-18** | Important | **`systemctl restart` returning 0 is not evidence the configuration was accepted.** Done literally, `status` showed `active (running) since … 8ms ago` — milliseconds before the process evaluates its config | Run-sheet defect in this package, **corrected** to read `NRestarts` |
| **N-21** | Important | **This package's own procedure caused an operator-visible outage** by retargeting a uid-scoped firewall rule onto the maintainer's login account | Corrected to per-process network-namespace isolation. **Not a platform defect.** Diagnosed by the Operations Owner |
| **N-22** | Important | HSTS required by the accepted contract, configured in **neither** Caddy file | Fixed in the repository; **undeployed** |
| **N-25** | Important | The Foundry upgrade blocked the real-folder run — **and the pin worked**, a live observation of a mandatory scenario | Resolved by C-P3.5-X; validated on real data |
| **N-26** | Important | Real Actor data costs **~13–15×** its input in peak memory where the synthetic fixture cost ~7.5×; extrapolated to N-20's ceiling this reached ~1 GiB | Raised; N-47 raised to 2 GiB (C-P3.5-Z). **The extrapolation is not a measurement** and says so |
| **N-27** | Important | The P3.4 scope guard watched `adapters/` and `application/` but **not `domain/`** | The `domain/` gap is fixed and falsified; **N-30 identifies the same unresolved class for `tools/`** |
| **N-28** | Important | C-P3.5-Z's N-47 raise reached the register and the systemd unit but **not the harness that measures against N-47** — and the test meant to prevent exactly that pinned the constant to a **literal**, so it could only confirm the harness still equalled itself | Fixed and falsified; the unit file is now the single source (C-P3.5-AA). **Changes no measurement in this package** |
| **N-30** | Important | The P3.4 scope guard still does not watch `tools/`, including `tools/portal_server.py`, the deployed portal entry point carrying the access-log confidentiality control | **Remediated in C-P3.5-AD and accepted as satisfactory on the 2026-08-28 re-review.** Production layers are enumerated, changes are declared file by file, and synthetic undeclared paths prove rejection |
| **N-32** | Important | Two unfamiliar-client tests assert that no three-character source fragment may coincidentally occur in an eight-hex-character keyed pseudonym, making their result depend on the random per-process key | **Remediated in C-P3.5-AH, not closed. Test-only.** The fragment rule is replaced by a per-case table of **complete** forbidden values, each carrying a character outside the pseudonym's own alphabet, so absence follows from the contract rather than the key. Falsified deterministically by pinning `_digest` to `59990025`, and mutation-tested against three raw pass-throughs including one wearing the pseudonym's prefix. Focused pair **480 passed** in each of three fresh processes; web **2797 → 2824**, skips still **80**. Nothing in `tools/portal_server.py` changed. Evidence §5V |
| **N-8** | Minor | Five accepted traceability rows carried no citation resolving in either direction | All five verified covered — citation gaps, not coverage gaps |
| **N-9** | Minor | The SG-3 record is not uniform between `status.md` and the supervised-session evidence | Raised, not silently corrected. No evidence affected; no procedure ran without authority |
| **N-12** | Minor | Two unexplained tests, and four tracked test files that are `0600` in the tree while Git records `100644` — a suite whose file set depends on **who runs it** | Reported, not repaired. **The 2-test difference is still unaccounted for** — see §9.6 |
| **N-15** | Minor | Environment files are `0640` where SP-02 specifies `0600` | **Stands as a deviation with no security consequence**: `/etc/freedom-blades` is `750 root:root`, so the group-read bit is unreachable. Established by a failed sourcing attempt, not by inspection. The original severity was withdrawn; the finding was not |
| **N-16** | Minor | An operator-facing message understates what happened | Recorded. Not a behaviour defect |
| **N-17** | Minor | A timestamp the procedure needed was not captured | Recorded for the next run of this procedure |
| **N-19** | Minor | An environment file is not shell-sourceable — an operational hazard found by using it | Recorded |
| **N-23** | Minor | HTMX triggers a CSP violation on every page that loads it | Fixed. Found only because a real engine ran the page |
| **N-24** | Minor | The lost-pin runbook's query must run **before** teardown | Recorded. **Its remediation must change the teardown procedure, not the runbook** — see §9.5 |

### The pattern worth a reviewer's attention

**Five controls in this package were stated in one place and absent from the
place that acts on them:** **N-22** (HSTS in the contract, in neither Caddy
file), **N-45** (a soft warning in the numeric register that nothing emitted),
**F6** (S-15's warning, computed and read by nothing), **N-27** (a scope guard
blind to a whole layer) and **N-28** (an accepted raise that never reached the
instrument measuring against it).

**Each was found by looking. None by a check designed to find them** — and two
had a check that was supposed to. N-27: a guard that does not watch a layer
cannot report that it is not watching; it simply passes, which reads exactly like
the layer being clean. N-28 is worse, because the guard existed and was
toothless: a constant pinned to a literal can only ever confirm that it still
equals itself. **N-28 was also found after this section was written**, which is
the most direct evidence available that the list is not complete.

**The question this package cannot answer, and puts to the reviewer: how many
others are there?**

**2026-08-28 re-review answer:** at least two more relevant omissions existed.
N-29 shows that the address scrubber's documented best-effort boundary conflicts
with the accepted every-log-line requirement. N-30 is a sixth silent-control
instance: the scope guard still omitted the `tools/` layer that contains the
portal's production entry point. EX-11 and EX-12 remain withheld.

**2026-08-28, later the same day — remediation applied, and the count moved
again.** N-29 and N-30 are corrected and falsified in the repository
(**C-P3.5-AD**, evidence §§5Q–5R); the table above is left as submitted and
neither finding is closed by the correction. Two further instances surfaced while
correcting them, both in the *retained* path rather than the fallback: the
pinned branch trusted the type and value of every field it kept, and the request
path — which an HTTP client chooses — was never scrubbed at all, so
`GET /x203.0.113.7y` disclosed an address through the branch this handoff keeps.
Both were found by writing the correction, **neither by the review and neither by
a check**. The question this section puts to the reviewer is therefore still
open, and its answer is still "at least two more".

**2026-08-28, later still — the count moved once more, and this time the review
found it.** N-31 is a *third* instance in the retained path: the branch bounded
every field it kept and scrubbed the one it knew was caller-controlled, and left
the method — equally caller-controlled — examined for syntax only. It is the same
mistake in a third place, and the honest reading is that "at least two more"
should have been "at least three", which nobody could have known by counting. The
correction under C-P3.5-AF therefore did not add a third special case: it reuses
the rule N-29's re-review already accepted, so the detector and the scrubber
cannot disagree, and the argument a reviewer has to check is one argument rather
than three. **The question stays open.**

**2026-08-28 remediation re-review:** N-30's correction is satisfactory and the
unfamiliar-record half of N-29 has the required fail-closed shape, but the
absolute confidentiality requirement still fails on the retained path. The
method is caller-controlled, is allowed to contain dots and digits, and is
preserved unchanged; method `203.0.113.7` reaches the formatted line. This is
Blocking **N-31**. EX-11 and EX-12 remain withheld, and no gate status changes.

---

## 5a. The 30 change-log entries this package wrote

Every entry is in `docs/project-management/change-log.md` under its identifier.
The alphabet is exhausted at `Z`; entries continue `AA`–`AC`. `P1` is an Acceptance
Authority decision recorded inside `P`'s window.

| Entry | Subject |
|---|---|
| **C-P3.5-A** | P3.5 planning opened; readiness audit complete; execution plan submitted for approval |
| **C-P3.5-B** | SG-1 approved; browser decision taken; two ceremony findings raised |
| **C-P3.5-C** | First deployed run: one blocking defect fixed, one routed to Gemini |
| **C-P3.5-D** | Codex withheld the Gemini prompt; C35 remediation partial |
| **C-P3.5-E** | R35 remediation partial; rotation script repaired |
| **C-P3.5-F** | Rotation transaction safety completed; shell contract still outstanding |
| **C-P3.5-G** | The server-owned shell contract is implemented |
| **C-P3.5-H** | Shell boundary defects and the rotation commit window closed |
| **C-P3.5-I** | Shell lifecycle completed on public and failure pages |
| **C-P3.5-J** | Public-shell failure boundary made typed |
| **C-P3.5-K** | Frontend repository remediation accepted; supervised evidence retained |
| **C-P3.5-L** | Supervised browser and authenticator session executed; SP-21 and SP-22 added; eight findings raised |
| **C-P3.5-M** | Codex review findings remediated: emergency refusal audit, logout attribution, limiter split, grant classification, provider probe |
| **C-P3.5-N** | Handover executed: deployment identity, criterion 6 and 3 observed, worker root-caused, S-4 closed end to end |
| **C-P3.5-O** | Codex C1/C2 remediation: the staging installer reproduces the F5 repair, and `/healthz` reports the credential shortfall |
| **C-P3.5-P** | Codex C3/C4 remediation: an existing worker file is confirmed completely, and readiness stops being described as usability |
| **C-P3.5-P1** | Acceptance Authority decision on C2-1 |
| **C-P3.5-Q** | prepare the product-owned filesystem layout |
| **C-P3.5-R** | product-owned filesystem cutover executed and verified |
| **C-P3.5-S** | Phase 3 closure request audited; gate remains open |
| **C-P3.5-T** | Three P3.5 decisions recorded: real Foundry data in staging, the TC-PERF-02 repeat-run method, and the A-05 criterion 4 split |
| **C-P3.5-U** | D-n corrected after Codex finding B-1: S-15's pre-exposure observation stays inside A-05 |
| **C-P3.5-V** | the P3.5 authority decisions of 2026-08-26, and the two criteria they had to repair first |
| **C-P3.5-W** | the 2026-08-26 evening decisions: the gate-off window and the performance bounds |
| **C-P3.5-X** | the supported Foundry core version moves 14.365 → 14.367 |
| **C-P3.5-Y** | HSTS added to the proxy configuration (finding N-22) |
| **C-P3.5-Z** | version compatibility ranges, N-47 raised, and N-45's soft warning built |
| **C-P3.5-AA** | N-47's raise carried into the harness that measures against it (finding N-28) |
| **C-P3.5-AB** | EX-11 implementation tasks and deployment of HSTS, module 1.0.9 and `MemoryMax=2G` |
| **C-P3.5-AC** | EX-11/EX-12 re-review raises Blocking N-29 and Important N-30; both recommendations withheld |
| **C-P3.5-AD** | N-29 and N-30 remediated in the repository and returned for review |
| **C-P3.5-AE** | Remediation re-review accepts N-30 but raises Blocking N-31 on the retained method field; both recommendations remain withheld |
| **C-P3.5-AF** | N-31 remediated: a pinned record whose method carries an address literal is withheld whole; both re-reviews requested again |
| **C-P3.5-AG** | N-31 production remediation accepted as satisfactory; Important N-32 raised on probabilistic short-fragment assertions in two access-log tests |

**A through S predate the handover** that made this package's author working
Technical Lead. **T through AB are its own.** C-P3.5-AC records the independent
re-review outcome. C-P3.5-AE records the next re-review: N-30 is satisfactory,
but N-31 keeps the confidentiality boundary and both recommendations open.
**C-P3.5-AF, 2026-08-28, is the remediation of N-31** — the entry count in this
section's heading is the count as submitted and is deliberately not re-cut with
every dated addendum below it.

**C-P3.5-AG records the next review outcome:** N-31's production behavior is
satisfactory. N-32 is confined to two nondeterministic assertions and does not
reopen the production confidentiality design. The recommendations remain
withheld until that evidence defect is corrected and the operational items run.

---

## 6. Verification

Run **serially** (finding F-6: both suites share one disposable database) on the
deployed host, 2026-08-27, **after** the N-28 correction, with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported.

**The environment variable is not decoration.** Without it the web suite reports
*1141 passed, 1362 skipped in 11.9 s* and still exits 0 — a green run that has
exercised almost no database behaviour at all. A reviewer reproducing these
figures should check the skip count first: **80, not 1362.**

| # | Command | Result |
|---|---|---|
| 1 | `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **2447 passed**, 1 warning, 141.46 s |
| 2 | `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2423 passed, 80 skipped**, 1137 warnings, 139.44 s |
| 3 | `node --test "foundry-module/tests/*.test.mjs"` | **171 pass, 0 fail** |
| 4 | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **4/4 OK** |
| 5 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 6 | `python -m compileall -q adapters application domain tests tools`, both venvs | clean, rc 0 |
| 7 | `alembic heads` / `alembic branches` | single head **`0013`**, no branches |
| 8 | `git diff --check` | clean |

> **Superseded for the web figure, 2026-08-28.** The table above is the run as
> submitted on 2026-08-27 and is left as it was. Three later remediations added
> tests to it: C-P3.5-AD (**2423 → 2625**, evidence §5Q.3), C-P3.5-AF
> (**2625 → 2797**, evidence §5T.4) and C-P3.5-AH (**2797 → 2824**, evidence
> §5V.6). The current tree's serial, database-enabled figures are bot **2447
> passed**, web **2824 passed, 80 skipped**, module **171 pass**, focused **480
> passed**, assets 4/4, freeze 14/14, both `compileall` checks clean, single
> Alembic head `0013`, clean `git diff --check`. Every other row above is
> unchanged, the skip count is still **80**, and formatter, linter and type
> checker are still unconfigured and still not claimed.
>
> **The focused figure moved for a reason worth stating.** It was **453** while
> the pair contained the two probabilistic N-32 assertions, and one fresh-process
> run of it failed **2 of 453** on a coincidental digest. It is **480** now, and
> was 480 in each of three separate processes, because the assertions no longer
> depend on the per-process key. See §5V.

The bot suite is **2447**, one higher than the 2446 recorded before this
correction: `test_the_memory_ceiling_matches_the_shipped_worker_unit` is new, and
the literal assertion it replaces lived inside an existing test rather than being
one of its own.

**The interpreters are not in the repository.** `./venv` and `./venv-web` are the
*runtime* environments and contain no pytest; the review environments are
`/opt/discord-bots/venv` and `/opt/discord-bots/venv-web`, a survival of the
pre-migration layout. A reviewer who runs `./venv-web/bin/python -m pytest` gets
`No module named pytest`, not a failure of this package.

**Every skip is explained**: 80 skips, all deliberate matrix cells asserted by
per-route success cases (§4.1 of the operations evidence), and both skip reasons
are printed by `-rs` in the run above. Warnings are overwhelmingly an HTTPX
deprecation raised by the test harness, not by application code.

**Checks not run, and they are recorded as unavailable rather than passed:**
**formatter, linter and type checker are not configured in this repository**
(standing condition E-9). P3.5 did not introduce one as a drive-by change.

---

## 7. Configuration and deployment changes — three are undeployed

> **Operational addendum, 2026-08-28 (C-P3.5-AI).** The deployed worker unit
> now matches the reviewed rendered template, validates, remains active without
> restart and enforces 2 GiB. HSTS was observed at origin and edge. The current
> portal tree, including accepted N-29/N-31 controls, was loaded by restart and
> passed health. The final 92-second TC-SEC-07 window observed the application
> boundary and safe headers, and the gate was restored with public 401. Peter
> visually confirmed module 1.0.9 installed on all three Foundry instances, but
> running-process version proof and the dependent real export/preview remain
> outstanding. The historical table below is retained as submitted; current
> evidence is §5W.

| Change | State |
|---|---|
| N-7 and N-13 access-log redaction | **Deployed** and re-observed |
| Foundry module **1.0.9** — version ranges | **Repository only.** 1.0.8 is installed on foundry1 and foundry3; 1.0.7 snapshotted to `module-rollbacks/` |
| **`MemoryMax=2G`** (N-47) | **Repository only.** The running worker still has 1G |
| **HSTS** in both Caddy files (N-22) | **Repository only.** `/etc/caddy` unchanged |

**Rollback for each is recorded in its change-log entry.** No migration was added
by P3.5; the schema is unchanged at `0013`.

### 7a. The uncommitted working tree

**34 modified**, **4 new**, all of it P3.5. Commit `bbbe977` carries
the earlier half — the run sheets, the evidence documents, the observation and
probe tools, and the N-7/N-13 portal fix. `docs/review/Handover information` is
the reviewer handoff and is **transient by design**: it will be overwritten once
read, and everything in it that matters is recorded elsewhere.

**Modified:**

- `.agents/AGENTS.md`
- `adapters/web/templates/base.html`
- `application/worker/runtime.py`
- `docs/contracts/phase-3-numeric-policy-register.md`
- `docs/implementation-plan.md`
- `docs/operations/foundry-snapshot-submission.md`
- `docs/operations/topology.md`
- `docs/project-management/change-log.md`
- `docs/project-management/status.md`
- `docs/review/Handover information`
- `docs/review/phase-3-p3-5-accessibility-and-browser-evidence.md`
- `docs/review/phase-3-p3-5-staging-and-operations-evidence.md`
- `domain/foundry.py`
- `foundry-module/module.json`
- `foundry-module/package.json`
- `foundry-module/scripts/bundle.js`
- `foundry-module/scripts/settings.js`
- `foundry-module/tests/fixtures.mjs`
- `foundry-module/tests/projection.test.mjs`
- `infra/caddy/freedom-blades-portal.caddy.tmpl`
- `infra/caddy/freedom-blades-test.caddy`
- `infra/systemd/freedom-worker.service.tmpl`
- `tests/fixtures/foundry_actor_anomalies.json`
- `tests/fixtures/foundry_actor_sample.json`
- `tests/test_deployment_artifacts.py`
- `tests/test_fixtures.py`
- `tests/test_foundry_identity.py`
- `tests/test_snapshot_api.py`
- `tests/test_snapshot_database.py`
- `tests/test_snapshot_perf_harness.py`
- `tests/test_submission_database.py`
- `tests/web/template_digests.py`
- `tests/web/test_p3_4_static_assets.py`
- `tools/snapshot_perf_harness.py`

**New:**

- `docs/review/phase-3-p3-5-submission.md`
- `foundry-module/tests/deployment-range.test.mjs`
- `tests/web/test_n23_htmx_csp_config.py`
- `tests/web/test_n45_soft_warning.py`

> **The counts above are the 2026-08-27 submission's and are left as they were.
> Observed 2026-08-28** against the current tree: **50 modified, 4 new**. The
> `New` list is unchanged. The `Modified` list does not carry the sixteen files
> below — fifteen of them opened by the N-29, N-30, N-31 and N-32 work that
> followed the submission, and by the documentation those findings required:
>
> - `application/worker/__init__.py`
> - `docs/adr/0006-foundry-integration-boundary.md`
> - `docs/adr/README.md`
> - `docs/contracts/phase-3-operational-contract.md`
> - `docs/contracts/phase-3-route-authorization-contract.md`
> - `docs/contracts/phase-3-test-traceability.md`
> - `docs/contracts/phase-3-threat-model.md`
> - `docs/discovery/foundry-mapping.md`
> - `docs/discovery/open-decisions.md`
> - `docs/project-management/README.md`
> - `docs/project-management/data-migration-manifest.json`
> - `docs/project-management/data-migration-register.md`
> - `docs/project-management/data-vocabulary-register.md`
> - `docs/rules/foundry-export-contract.md`
> - `tests/web/test_n7_access_log_redaction.py`
> - `tools/portal_server.py`
>
> **`tests/web/test_n7_access_log_redaction.py` is the only one C-P3.5-AH
> touched**, and it is the only file this correction changed at all. The other
> fifteen were already modified when it began and were left exactly as they
> were. This addendum records an observation about the tree; it repairs no
> figure and closes nothing.

---

## 8. Security and privacy

- **Two credential-disclosure defects found and fixed** by running the procedure
  that looks: N-7 and N-13. Both were in monitoring output, not in the
  application's own logging.
- **No secret, credential, token, public key, COSE blob, cookie or CSRF value**
  was read, printed, recorded or committed by this package.
- **Real Actor data** was used once, under **D-l**, as a supervised operational
  input. **No Actor name, payload or warning text appears in any artifact.**
  Teardown was verified: artifact store empty, uploads shredded, import tables
  truncated, admissions closed.
- **Screenshots are git-ignored** and were confirmed absent from the commit.
- **One outage was caused by this package's own procedure** — **N-21** — by
  reusing a uid-scoped firewall rule under an account running far more than the
  thing under test. Diagnosed by the Operations Owner, corrected to per-process
  network namespace isolation, and recorded in full.

---

## 9. Unresolved questions for the reviewer

1. **N-26.** Does the 13–15× real-data memory ratio, extrapolated to N-20's
   ceiling, justify the N-47 change — or does it argue for lowering N-20? The
   extrapolation is from two real points and cannot be replaced by a measurement,
   because **no corpus near the ceiling exists**. A deliberately skewed fixture
   would separate "tracks total bytes" from "spikes on the largest Actor"; it is
   not written.
2. **The version range.** C-P3.5-Z widened exact matching to Foundry generation
   and system major.minor. Is that the right split, and is fail-closed parsing of
   the untouched components sufficient?
3. **TC-LIM-02's snapshot half.** The row names two routes and only one exists in
   this deployment, by accepted design. Recorded as agreement rather than as a
   gap — the reviewer should confirm that reading.
4. **The five silent controls** (§5). Is there a systematic check worth adding,
   or is looking the only thing that finds them?
5. **N-24's remediation** should change the *teardown procedure*, not only the
   runbook: a note in a runbook failed to prevent the same error twice, on
   consecutive days, by the same author.
6. **N-12's two unexplained tests.** The bot suite collected 2379 tests from the
   65 pre-existing files where the 2026-08-26 record states 2377, with no
   tracked test file modified in between. **I cannot account for the
   difference and do not assert which figure is wrong.** Both are recorded as
   dated observations. The related mode drift — four tracked files `0600` in
   the tree where Git records `100644` — is offered, not taken, because they
   are files this package did not author. A suite whose file set depends on
   who runs it produces counts a reviewer cannot reproduce.

---

## 10. Proposed reviewer focus areas

**For EX-11 (implementation):** the N-20 remediation and its falsification; the
version-range comparison and the duplicated compatibility table across two
languages; the N-45 soft warning and the honesty of its test coverage; whether
the evidence documents distinguish *measured*, *extrapolated* and *attested*
consistently.

**For EX-12 (security):** N-13's keyed pseudonym and its fail-closed fallback;
SP-27's guarded production-marked exercise; the HSTS configuration and the
`includeSubDomains` reservation; N-21's blast radius and its correction; and
whether the five silent controls indicate a class of gap rather than five
accidents.

---

## 11. What this submission requests

1. **EX-11** — independent implementation review of the complete package.
2. **EX-12** — a **distinct** security-focused review.
3. Remediation and re-review of every Blocking finding they raise.
4. Presentation of the package and both recommendations to Peter Duscha.
5. **Peter's Phase 3 gate decision** — his alone — and, only if approved, the
   explicit release of Phase 4 implementation.

**This package does not approve its own work, does not treat any prior focused
review as EX-11 or EX-12, and infers no Phase 4 authority from tests,
deployment, staging or a review recommendation.**

---

## 12. Acceptance Authority decision — 2026-08-28

After the independent implementation and security reviews and completion of the
final operational evidence, Peter Duscha accepted the following statement:

> As Security Reviewer, I confirm final break-glass readiness and close A-05.
> As Technical Lead and Operations Owner, I accept the PostgreSQL queue/limiter
> and staging evidence and close A-06 and I-06. As Product Owner, I retain R-23
> as an active accepted accessibility residual with screen-reader traversal Not
> Run for Phase 3. As Acceptance Authority, I approve the Phase 3
> authentication, authorization, and web-security gate and authorize Phase 4
> implementation.

This is the requested gate decision: Phase 3 is approved and Phase 4
implementation is authorized. R-23 remains active and accepted; the Not Run
screen-reader check is neither waived into a pass nor erased from follow-up.
