# P3.5 staging and operations evidence

**Artifact 3 of `phase-3-p3-5-readiness-and-execution-plan.md` §12.1**, created by
**EX-6**. **Opened:** 2026-08-25 by Claude, P3.5 working Technical Lead.

**Repository:** `/opt/freedom-blades/platform` · **Branch:** `docs/platform-plan`
· **Commit at opening:** `0e3929a`

> **The rule this document is written under.** Every result row is either filled
> by a check that **actually ran**, with its literal command and literal output,
> or it says **Not Run** and stays that way. **No row is pre-filled with a
> passing result.** A `Passed` is never written from a lower evidence level than
> the accepted row demands (execution plan §7.3).

**Nothing here closes I-06, A-05, A-06 or R-23, and nothing here requests a gate
decision.**

---

## 1. What is filled in so far

| Section | Procedures | State |
|---|---|---|
| §2 — disposable-database rehearsals | EX-3, EX-4 | **Executed 2026-08-25/26. Results below.** |
| §3 — staging procedures | SP-01…SP-06, SP-08…SP-19, SP-23 | **Not Run.** Awaiting SG-2 |
| §4 — verification set | full suites and available checks | **Executed 2026-08-26. Results below.** |

---

## 2. Disposable-database rehearsals (EX-3, EX-4) — executed

Released by SG-1. Target: the guarded disposable `freedom_test` **only**. No
staging or production database was contacted, and no service was mutated.

### 2.1 The documented expectations, read **before** the rehearsal

Execution plan §8.4 B-3 requires the documented rollback costs to be read first
and the observed behaviour compared against them. They were, and they are quoted
here so the comparison is checkable rather than asserted.

From `docs/operations/web-portal.md` §3.6, the four states an operator must
distinguish:

| The database holds | Documented outcome of a downgrade below 0013 |
|---|---|
| a **retained completed** committed-effect job | **Refused** |
| a **retained committed-but-unpublished** job | **Refused** — "the population a downgrade would hurt worst" |
| approved retention has removed all completed job/result records | **Available** |
| an unused database that never committed an effect | **Available** |

From §3.3, a downgrade of `0006` discards break-glass audit attribution; from
§3.5, `0009` refuses to upgrade while any `discord_oauth` session row exists.
**Neither was reached by this rehearsal**, whose downgrade floor was `0010`
(§2.3) — recorded so no reader credits this rehearsal with evidence it did not
produce.

### 2.2 Pre-state, and the pre-migration backup

Execution plan §8.4: "A pre-migration backup is taken before every rehearsed
migration." It was.

| # | Command | Result |
|---|---|---|
| 1 | `date -u` | rehearsal opened **2026-08-25T23:48:47Z** |
| 2 | `APP_ENVIRONMENT=test DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/alembic current` | `0013 (head)` |
| 3 | `psql -d freedom_test` row census over the boundary-relevant tables | `reconciliation_jobs` 0 · jobs with committed effect 0 · `sessions` 0 · `audit_events` 0 · `snapshot_imports` 0 |
| 4 | `pg_dump -Fc -d freedom_test -f <workdir>/pre-rehearsal.dump` | 124,464 bytes, SHA-256 `31de2d9c1b6e8a17…` |
| 5 | table count, `information_schema.tables` where `table_schema='public'` | **31** |

**Stated expectation, from §2.1 row four:** an unused database that never
committed an effect ⇒ downgrade below 0013 **Available**.

### 2.3 EX-3 — migration rollback rehearsal across the P3.3 boundary

| # | Step | Literal result |
|---|---|---|
| 1 | `alembic downgrade 0010` | Ran `0013 → 0012 → 0011 → 0010`, **exit 0**. Tables 31 → **28**; `to_regclass('public.reconciliation_jobs')` → null |
| 2 | `alembic upgrade head` | Ran `0010 → 0011 → 0012 → 0013`, **exit 0**; `alembic current` → `0013 (head)`; tables **31** |
| 3 | Schema round-trip comparison, `pg_dump -s` before vs. after | **Identical.** 986 schema lines compared, **0 differences**. The only raw diff was `pg_dump`'s own per-invocation `\restrict`/`\unrestrict` nonce, which differs per dump by construction and is not schema |

**Observed = documented.** The `Available` branch behaved as §3.6's fourth row
states, and the round trip is exact.

### 2.4 EX-3 (continued) — the **refusal** branch, observed on a real database

The more valuable half, and the one an operator actually meets. A **synthetic**
committed-but-unpublished apply job was seeded — §3.6's second row, the case the
document calls the worst-hurt population — and the downgrade attempted.

**No real Actor payload, no real account and no real snapshot was involved.** The
seed was three synthetic rows: one `platform_accounts` row, one `foundry_snapshots`
row whose checksum is a repeating `ab` pattern satisfying the SHA-256-hex check
constraint, and one `reconciliation_jobs` row in state `running` with
`effect_committed_at` and `effect_result` set.

| # | Step | Literal result |
|---|---|---|
| 1 | `alembic downgrade 0012` with one committed-but-unpublished effect | **Refused. Exit status 1.** `RuntimeError: Refusing to downgrade revision 0013: 1 retained reconciliation job(s) record a committed import effect (0 completed, 1 committed but unpublished). … NOTHING HAS BEEN CHANGED: the database is still at 0013, complete and usable. …` — matching `web-portal.md` §3.6's quoted text |
| 2 | State after the refusal | `alembic current` → **`0013 (head)`**; tables **31**; `effect_result` column **present**; the job row **intact** |
| 3 | Remove the synthetic rows, then `alembic downgrade 0012` | **Exit 0**, landed at `0012` — the boundary **reopens**, as §3.6's third and fourth rows state |
| 4 | `alembic upgrade head` | **Exit 0**, `0013 (head)` |
| 5 | Schema vs. the §2.2 pre-state | **Identical, 0 differences, 986 lines** |

**Two properties are evidenced here that a unit test cannot supply:** the guard
refuses on **real PostgreSQL** under Alembic's own transaction, and it **fails
closed** — the refusal left the database complete, usable and at head, exactly as
its message claims.

**An incidental control was also observed refusing.** `DELETE FROM
foundry_snapshots` was refused by the append-only trigger:
`ERROR: append-only table foundry_snapshots: DELETE is refused. History is
corrected by appending a compensating record, never by editing it.` The synthetic
rows were therefore removed with `TRUNCATE`, which the migration's own refusal
message names as the supported disposable-database route.

### 2.5 EX-3 (continued) — runtime grants re-applied and re-verified

Required by EX-3: "with the runtime-grant template applied and re-verified".

| # | Step | Literal result |
|---|---|---|
| 1 | `sed 's/__APP_ROLE__/freedom_runtime_test/g' infra/postgresql/runtime-grants.sql.tmpl \| psql -d freedom_test -v ON_ERROR_STOP=1 -f -` | **exit 0** |
| 2 | `pytest -q tests/test_runtime_grants.py` | **11 passed** |

### 2.6 EX-4 — backup, checksum, destroy, restore, inventory comparison

**TC-OPS-02, disposable half.**

**Method note that matters.** An empty database makes a restore comparison prove
nothing — every count is zero before and after. Representative **synthetic** rows
were therefore seeded across four tables first, including the append-only
`foundry_snapshots`, so the comparison has something to fail on.

| # | Step | Literal result |
|---|---|---|
| 1 | Seed | `platform_accounts` 2 · `foundry_snapshots` 1 · `reconciliation_jobs` 1 (completed, with a result) · `reconciliation_job_results` 1 |
| 2 | `./infra/postgresql/backup-restore-drill.sh freedom_test <workdir>` | **exit 0** · `Restore verified for freedom_test` · opened **2026-08-25T23:53:55Z** |
| 3 | Artefacts written | `freedom_test.dump` 131,746 bytes · `freedom_test.dump.sha256` (`b5b4db791b8c65d0…`) · `inventory-before.txt` · `inventory-after.txt` |
| 4 | The drill's own destroy step | dropped the `public` schema, cascading to every Phase 2/3 table **and to the append-only trigger functions** `reject_history_mutation()`, `reject_admission_reversal()`, `protect_platform_admin_account()`, `reject_protected_mapping_change()`, `reject_second_protected_mapping()`, `enforce_mapping_provenance_transition()` |
| 5 | **Inventory comparison, before vs. after** | **Identical across all 31 tables.** The four seeded tables round-tripped with their exact counts: `platform_accounts=2`, `foundry_snapshots=1`, `reconciliation_jobs=1`, `reconciliation_job_results=1` |
| 6 | **Did the restore bring the protections back?** Verified rather than assumed: `DELETE FROM foundry_snapshots` after the restore | **Refused** by the restored append-only trigger, same message as §2.4. A restore that returns the rows but not the guards would pass a row-count comparison and still be a failure; it did not happen |

### 2.7 State left behind

`freedom_test` was returned to its pre-rehearsal condition: **`0013 (head)`**, 31
tables, **0 rows** across every base table. Verified by a census over
`information_schema.tables`. Both later suite runs (§4) ran against it green.

---

## 3. Staging procedures — Not Run

**None of the following has been executed. SG-2 is not granted.** They are listed
with their result columns deliberately empty; each is filled only by an execution
that actually happened.

| ID | Procedure | Closes | Result |
|---|---|---|---|
| SP-01 | Staging database, owner role, restricted login role, runtime grants, artifact paths | prerequisite | **Not Run** as a procedure — outcome partially evidenced by read-only observation; see the evidence inventory §2.1, including deviation **N-5** |
| SP-02 | Independently generated staging secrets outside the repository | prerequisite | **Passed 2026-08-26** — attested by the Operations Owner; files root-owned, not world-readable, outside the repository. Deviation **N-15**: `0640`, not the specified `0600`. See §5A |
| SP-03 | Separate staging Discord application, guild and role IDs | prerequisite | **Passed 2026-08-26** — identifiers recorded; guild proved distinct from `PRODUCTION_GUILD_ID`; snowflake creation times corroborate a purpose-built test server. See §5A |
| SP-04 | `freedom-web` and `freedom-worker` on loopback, `WORKER_ENABLED` differing | prerequisite | **Passed** — Codex independent observation, `phase-3-p3-5-f5-s2-operational-re-review-2026-08-25.md` |
| SP-05 | Staging Caddy site block with matched body limits | prerequisite | **Not Run** |
| SP-06 | `alembic upgrade head` on staging; grants; head `0013` | prerequisite | **Not Run** as a procedure — head `0013` observed read-only |
| SP-08 | Every startup refusal observed on the **deployed** configuration | TC-OPS-04 | **Partly executed 2026-08-26 — 11 of 15.** S-01…S-11 observed (S-02, S-05 and S-11 in both directions); **S-11 proved on the deployed unit** with systemd's own restart counter. **S-14 also observed on the deployed unit in M-4 (§5D).** **S-12 attempted three times and Not Run** — every failure was a setup error, none the portal's. S-13 test-enforced, S-15 owed by SP-27. **12 of 15; TC-OPS-04 not complete.** See §5C and §5D |
| SP-09 | Kill switch engage / verify / release | TC-OPS-01 | **Passed 2026-08-26** — every route 503 including a mutation, `/static/` and `/healthz` exempt as designed, bot and Foundry confirmed unaffected by the Operations Owner, full recovery verified. See §5B |
| SP-10 | Backup, restore, rollback rehearsal on **staging** | TC-OPS-02 staging half | **Passed as a procedure 2026-08-26** — backup verified listable, destroy, restore, inventory and guard checks all executed. **Raised Blocking finding N-20:** the restore silently drops the runtime role's privileges and both units crash-looped until the grants were re-applied. See §5D |
| SP-11 | End-to-end flow through preview, confirm and audit search | TC-OPS-03 | **Not Run** — needs the §5 transport step first |
| SP-12 | Monitoring/log output review | TC-OPS-05 | **Passed 2026-08-26**, at the third observation. Run 1 failed on **N-7** (§5.2); run 2, after the N-7 deployment, failed on **N-13** (§5.4); run 3, after the N-13 deployment, is clean on every class (§5.5). Coverage limit recorded: no worker job ran in the observed interval |
| SP-13 | Deployed proxy and application limit parity | TC-LIM-02 | **Passed 2026-08-26** — `WEB_MAX_REQUEST_BYTES=1048576` against Caddy `max_size 1MiB`: exact. Snapshot half: no such route on either side, by accepted design; flagged for Codex. See §5C |
| SP-14 | Browser-observed headers and CSP, normal / early / error | TC-SEC-07 browser half | **Passed in part 2026-08-26** — CSP identical on normal and error, early refusal observed at the origin, OAuth redirect confirmed under `form-action 'self'` in Chrome 151. Raised **N-22** (HSTS absent) and **N-23** (HTMX CSP violation). See §5I |
| SP-15 | 64 MiB refusal, preview and apply, worker peak RSS vs N-47 | TC-PERF-01/02 | **Synthetic halves executed 2026-08-26.** Refusal observed at the boundary; peak RSS **184.5 MiB** (realistic corpus) and **482.3 MiB** (N-20 ceiling), both inside N-47; applies 6.2 s and 27.0 s at 384/405 ms/MB. **D-m's real n=1 run still owed.** See §5J |
| SP-16 | `/healthz` and status poll during a running preview | TC-PERF-03 | **Passed 2026-08-26** against bounds accepted beforehand (**D-s**). 984 samples, zero non-200, every p95 ≤ 51 ms. One 1,561 ms maximum recorded as a signal. Browser-side poll not separately timed. See §5J |
| SP-17 | Worker restart, lease expiry, lost response, reaper recovery | I-06, A-06 | **Passed 2026-08-26** — SIGKILL mid-parse, `attempts` 1→2, systemd restart, lease expiry, reaper requeue, retry completed, **exactly one outcome and no partial state**. See §5J |
| **SP-27** | **Guarded pre-exposure S-15 observation** — disposable `freedom_production` with **synthetic** credentials, outbound egress blocked, `run_resource_checks` called **directly so no socket is ever opened**, then full teardown | **A-05 criterion 4b** | **Passed 2026-08-26** — S-15 observed refusing under the production marker with **no listener**, and passing at two credentials, inside a verified network namespace on a disposable database proved empty first. Added by decision **D-o** after Codex Blocking finding B-1. See §5G |
| SP-18 | Real-device inspection | TC-UI-08 | **Passed 2026-08-26/27** — iPhone 15 / iOS 26.6 and iPad A16 / iPadOS 26.6.1, every view, resized and zoomed, no defect. Bands covered by form factor rather than measured CSS pixels. See the accessibility evidence §2.2 |
| SP-19 | Screen-reader traversal | TC-UI-09 | **Not Run — permanently for Phase 3 under decision D-f.** R-23 stays active |
| SP-23 *(plan sense)* | Browser rendering, keyboard, skip links, HTMX, no-JS, contrast, reduced motion | TC-UI-01/02, R-23 | **Passed in part** 2026-08-24 — see the evidence inventory §2.2 and **finding N-1**, the SP-23 identifier collision |

---

## 4. Verification set — executed 2026-08-26

Re-run 2026-08-26 after the second I-1 remediation: **web 2398 passed / 80
skipped**, every other row unchanged. The web count moved because that
remediation added 32 tests; see §5.2.

Run **serially**, never concurrently, per finding F-6: both suites share the one
disposable `freedom_test` database.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test <review venv>/bin/python -m pytest -q -rs tests/web` | **2339 passed, 80 skipped, 1137 warnings** in 139.75 s |
| 2 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test <bot review venv>/bin/python -m pytest -q -rs tests/test_*.py` | **2377 passed, 1 warning** in 136.82 s |
| 3 | `node --test "foundry-module/tests/*.test.mjs"` | **155 pass, 0 fail, 0 skipped** in 214 ms |
| 4 | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **4/4 OK** |
| 5 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 6 | `python -m compileall -q adapters application domain tests`, both environments | clean, exit 0 |
| 7 | `git diff --check` | clean |
| 8 | `alembic heads` / `branches` | single head **`0013`**; **no branches** |
| 9 | `tests/test_runtime_grants.py` | **11 passed** |

### 4.1 Every skip, warning and unavailable check, explained

| Class | Count | Explanation |
|---|---:|---|
| Skips, `tests/web/test_p3_2_matrix.py:155` | 54 | Deliberate: the permitted cells of the authorization matrix are asserted by the per-route success cases. **Denial cells are not skipped.** |
| Skips, `tests/web/test_p3_3_matrix.py:198` | 26 | Same construction for the P3.3 matrix |
| Warnings, web suite | 1137 | Overwhelmingly HTTPX `DeprecationWarning: Setting per-request cookies=<…> is being deprecated`, from the test harness. Not a behaviour or security failure |
| Warnings, bot suite | 1 | `audioop` deprecation from `discord/player.py` under Python 3.12. Third-party; music is removed under OD-40 and no platform code imports it |
| Formatter | — | **Not configured. Not run. Not passed.** Standing repository condition (E-9) |
| Linter | — | **Not configured. Not run. Not passed.** |
| Type checker | — | **Not configured. Not run. Not passed.** |

**Suite totals moved** from the 2026-08-23 audit's 2168/2294: the web suite is now
2339 and the bot suite 2377, reflecting the tests added by the P3.5 frontend,
supervised-session and C1–C4 remediation packages.

### 4.2 Re-run after the C-5…C-12 preparation — 2026-08-26, later the same day

The earlier §4 table is left exactly as written. This is a **second, later run**
on the same date, after the preparation harnesses and their tests were added.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test <bot review venv>/bin/python -m pytest -q -rs tests/test_*.py` | **2417 passed, 1 warning** in 137.32 s |
| 2 | `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test <review venv>/bin/python -m pytest -q -rs tests/web` | **2398 passed, 80 skipped, 1137 warnings** in 135.23 s — **unchanged**, as expected: this package added no web test |
| 3 | `node --test "foundry-module/tests/*.test.mjs"` | **155 pass, 0 fail, 0 skipped** in 221 ms |
| 4 | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **4/4 OK** |
| 5 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 6 | `python -m compileall -q adapters application domain tests tools`, both environments | clean, exit 0 |
| 7 | `git diff --check` | clean |
| 8 | `alembic heads` / `branches` | single head **`0013`**; **no branches** |

Run **serially** (finding F-6). Formatter, linter and type checker remain
**not configured / not run / not passed** (E-9).

**The bot suite moved 2377 → 2417, and 38 of those 40 are this package's:**
`test_perf_snapshot_fixtures.py` 12, `test_snapshot_perf_harness.py` 11,
`test_breakglass_observation.py` 15. **The remaining 2 are not accounted for** —
the 65 pre-existing files collect 2379 today and no tracked test file has been
modified since the earlier run. Recorded as finding **N-12** rather than
reconciled; the earlier figure is left as written and neither is asserted to be
the wrong one.


### 4.3 Verification set re-run at the close of 2026-08-26

After the day's supervised sessions and the code they produced. Run **serially**
(finding F-6); the earlier §4 and §4.2 tables are left as written.

| # | Command | Result |
|---|---|---|
| 1 | `<bot review venv>/bin/python -m pytest -q -rs tests/test_*.py` | **2424 passed, 1 warning** in 137.39 s |
| 2 | `<review venv>/bin/python -m pytest -q -rs tests/web` | **2415 passed, 80 skipped, 1137 warnings** in 131.62 s |
| 3 | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **4/4 OK** |
| 4 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 5 | `python -m compileall -q adapters application domain tests tools`, both environments | clean |
| 6 | `git diff --check` | clean |
| 7 | `alembic heads` | single head **`0013`** |

**Counts moved** from 2417/2398 at the start of the day to **2424/2415**, reflecting
the tests added by the N-13 access-log remediation, the N-20 drill remediation,
the startup-refusal probe and the performance harness. Skips are unchanged at 80
and explained in §4.1. **Formatter, linter and type checker remain not configured,
not run, not passed** (E-9).

**The visual freeze and asset manifests still verify**, which matters this
evening: finding **N-23** proposes a `base.html` change, and nothing has been
applied to the frozen assets.

---

## 5. Finding raised by this execution

### N-6 — stale bytecode from the filesystem cutover named a directory that no longer exists

**Class: Important — evidence hygiene. Corrected.**

**What was observed.** The first post-rehearsal run of the web suite reported **6
failures**, all of the same shape —
`test_structural_*_fixture_cleans_after_yield`, failing with
`OSError: could not get source code` from `inspect.getsource`. The suite also
displayed every test path as `../../discord-bots/freedom-bot/tests/web/…`, a
directory that **does not exist**: `ls -ld /opt/discord-bots/freedom-bot` →
`No such file or directory`.

**Root cause.** The 2026-08-25 filesystem cutover moved the repository by
**same-host rename**. `mv` preserves mtime and size, which are exactly the two
values CPython uses to decide whether a cached `.pyc` is still valid. The caches
were therefore accepted as current while their compiled code objects still
carried the pre-cutover `co_filename`. Verified rather than inferred: **163
`.pyc` files under `tests/` contained the literal string
`/opt/discord-bots/freedom-bot`.**

**Why it matters beyond six tests.** Anything that reads source through a code
object — `inspect.getsource`, and every traceback path in a failure report —
pointed at a tree that is gone. Evidence collected from this host between the
cutover and this correction could therefore cite file paths that no reviewer can
resolve. The six failures were **not** product defects, and a reader who took
them at face value would have been misled in both directions.

**Correction.** All 24 `__pycache__` directories were removed. They are
regenerable, untracked and `.gitignore`d — confirmed with `git check-ignore`
before deleting, and `git status` was unchanged afterwards. The suite then ran
**2339 passed, 0 failed**, with paths displaying correctly as `tests/web/…`.

**Consequence for the record.** No repository source, test or document was
changed by this correction. Earlier suite figures taken from this host after the
cutover are not invalidated — the tests themselves executed — but any **file path
or traceback** quoted from such a run should be read as naming the pre-cutover
tree. Raised for Codex.

---

## 5.2 SP-12 / TC-OPS-05 — executed 2026-08-26. **Failed.**

**Operator:** Peter Duscha, at his own console with elevated access. **Method:**
`journalctl -u freedom-web.service -u freedom-worker.service --since "2026-08-24"`,
**5535 lines**, reduced to distinct message shapes by stripping the syslog prefix
and normalising UUIDs and integers to placeholders, then grouped with counts.

**Why the reduction is complete coverage and not a denylist scan.** The counts sum
back to 5535, so nothing was sampled or dropped, and the normalisation collapses
only what repeats. A name, a character or a token does **not** repeat, so it
survives as its own line and becomes *more* visible rather than less. The method
was validated against seeded test data before use: a planted character name
survived the reduction intact.

### The result

| Class sought | Found? |
|---|---|
| Human or character names | **None** |
| Discord usernames or user IDs | **None** |
| Character identifiers beyond opaque UUIDs | **None** |
| **Tokens or credentials** | **YES — see N-7** |

### N-7 — the OAuth authorization code and state are written to the journal in clear text

**Class: Important — security / operational disclosure. TC-OPS-05 fails on this
row alone; every other class is clean.**

**What was observed.** Three access-log lines of the form:

```text
"GET /auth/discord/callback?code=<AUTHORIZATION CODE>&state=<STATE> HTTP/1.1" 303 See Other
```

The literal values are **deliberately not transcribed into this document, in any
form, including a truncated one** (§8.3 rule 2).

**Mechanism, verified rather than inferred.** The deployed unit starts uvicorn
with no `--no-access-log` and no custom log configuration —
`ExecStart=… -m uvicorn tools.portal_server:application --factory --host 127.0.0.1
--port 8001 --timeout-keep-alive 5 --no-server-header --proxy-headers
--forwarded-allow-ips 127.0.0.1`. Uvicorn's default access logger writes the whole
request line, **query string included**, to stdout, which systemd captures. R-04
`/auth/discord/callback` is the one route that receives credentials as query
parameters, because that is how the OAuth provider redirects. **The application's
own logging is not at fault:** it writes exactly two kinds of line — startup
warnings naming variables never values, and failure lines carrying a correlation
UUID and a path — and neither carries a secret.

**Severity, stated honestly in both directions.**

*Why it is not an emergency:* the codes observed are **spent** — each line ends
`303 See Other`, the completed exchange. A Discord authorization code is
single-use and short-lived, and this flow is **PKCE-bound**, so a code alone
cannot be exchanged without the verifier, which never appears in a URL. The
journal is readable only by `root` and members of `adm` / `systemd-journal`;
confirmed by observation that an unprivileged account sees nothing. **No client
secret, session cookie, CSRF token, recovery grant or WebAuthn material appears
anywhere in the 5535 lines. No credential rotation is indicated.**

*Why it is nonetheless a real finding:* TC-OPS-05's criterion is that monitoring
output contains **no** token data, not that the tokens it contains are hard to
use. A privileged local reader — or anyone receiving an exported journal, a
support bundle or a log shipped off-host — obtains authorization codes and the
state values that bind the OAuth transaction. **The same configuration would do
the same in production**, where the window between the log write and the code's
consumption is the same but the population with journal access, and the value of
what the code buys, are both larger.

**Why it survived four gates.** P3.1 proved the OAuth flow; P3.4 proved the
rendering; neither looked at what the deployed process *writes*. This is the same
shape as findings F-15 and F-16 — the defect that only appears when somebody looks
at the running system. It is the first thing SP-12 has ever been run against, and
it found it on the first run.

**Remediated in the repository, 2026-08-26. Not yet deployed.**

`tools/portal_server.py` — the operator entry point the unit file names — installs
a `logging.Filter` on `uvicorn.access` that replaces the query string with the
marker `?<redacted>`. The route stays identifiable; the credential does not
survive.

Three design points, each of which a reviewer should be able to challenge:

1. **Why not `--no-access-log`.** It fixes the disclosure by destroying the
   operational visibility an operator needs during an incident. Wrong trade.
2. **Why the entry point and not the unit or a `--log-config` file.**
   `uvicorn.config.Config` calls `configure_logging()` in `__init__`, **before**
   `load()` imports the factory — verified by reading the installed uvicorn
   0.32.1, not assumed — so a filter added at import time is installed after
   `dictConfig` has run and is not wiped by it. **The unit file is unchanged**,
   which means this needs a service restart rather than SG-2's unit surgery, and
   the redaction cannot be deployed without the code that requires it.
3. **Why the whole query string rather than an allowlist of safe keys.** An
   allowlist is a control somebody must maintain; the day a route gains a
   parameter carrying a token, an allowlist nobody updated leaks it and nothing
   fails. Dropping the whole string fails safe. The `?failure=…&correlation=…`
   diagnostics that were being read out of access lines remain available from the
   application's own correlation logging and from the audit table.

**Evidence, at two levels.**

`tests/web/test_n7_access_log_redaction.py` — **59 tests, all passing** (20 at the
first review, 27 after finding I-1's first remediation, 59 after its re-review),
written against uvicorn's real record shape rather than a paraphrase of it, and
including:

- a **falsification** test asserting the leak *is* reproduced without the filter,
  so a filter that silently stopped matching could not leave this file green;
- the redaction itself, over the OAuth target and over five other query shapes,
  because there is no allowlist to trust;
- **fail-closed behaviour for every unrecognised record shape**, each one first
  shown to leak unfiltered and then shown not to — the pass-through this file
  originally asserted was finding I-1, and is described below;
- proof the filter **never drops** a record; and
- proof that **`application()` installs it** — available is not installed, and
  without this the redaction could be deleted from the entry point with the rest
  of the file still green.

**And end to end against a real running uvicorn**, on a throwaway port with a
trivial ASGI app, because what is under test is the server's logger rather than
the portal:

```text
WITHOUT the filter:  "GET /auth/discord/callback?code=<SYNTHETIC>&state=<SYNTHETIC> HTTP/1.1" 303
WITH the filter:     "GET /auth/discord/callback?<redacted> HTTP/1.1" 303
```

The synthetic code and state are absent from the second line and the path is
preserved. **The leak was reproduced before it was fixed**, so the fix is shown to
address the observed defect rather than an assumed one.

**Hardened 2026-08-26 after Codex interim finding I-1 (Important).**

The first version redacted only uvicorn 0.32.1's exact five-tuple and passed every
other record shape through **untouched** — and its tests *enshrined* that
pass-through. Codex identified the failure mode precisely: a uvicorn upgrade or a
logging-configuration change could restore credential disclosure **while every
shape-independent test stayed green**. A security control whose tests pass after
it has stopped working is worse than no control, because it is believed.

Two changes, and the first one was found by a test rather than reasoned about:

1. **The precise branch is now gated on the format *contract*, not the record
   *shape*.** Gating on shape was itself unsafe: a future uvicorn prepending a
   field would still present a tuple with a string at index 2, so the filter would
   confidently redact the wrong argument while the credential sailed past in the
   next one. **That is not hypothetical — the test written for I-1 caught exactly
   it, and the fix was made because the test failed.** The branch now requires
   `record.msg` to equal the pinned `ACCESS_LOG_FORMAT` and the argument count to
   be exactly five.
2. **Anything else fails closed** — but the first attempt at this half was itself
   wrong, and is corrected below. It scrubbed tuple arguments, mapping values and
   `record.msg`, and **claimed that made every unrecognised record safe**.

**Tests: 20 → 27**, adding five shapes that must each fail closed (target at an
unexpected index, extra leading fields, mapping arguments, a pre-formatted message
with no arguments at all), a check that the test's and the implementation's format
constants are the **same string** so they cannot drift apart, and a pin on
uvicorn's own access-log call in **both** the httptools and h11 protocol
implementations — so a version bump that moves the contract fails CI instead of
degrading silently in a journal.

**Corrected again 2026-08-26 after Codex re-reviewed I-1 and reproduced the leak.**

The fallback above was still open, and its docstring said otherwise. Codex ran the
filter over `record.args = ["/auth/discord/callback?code=…"]` — a **list**, which is
neither a tuple nor a mapping — and the credential rendered intact. Reproduced
here before changing anything, and two further shapes go past the one Codex named:
a `set`, and **an object carrying the target only in its `__str__`**.

That third shape is why the fix is not "add `list` beside `tuple`". **The set of
objects that can render a query string is not enumerable**, so every enumeration is
a claim that will silently become false — the same failure mode as the
pass-through, one container later.

**The fallback no longer inspects structure at all.** It renders the record itself,
redacts the rendered *text*, and stores the result as `record.msg` with
`record.args = None`. Whatever the arguments were, they are characters by the time
the redaction runs, and the guarantee is a property of the output that can be
stated in one line: **no character after the first `?` survives.** A record that
cannot be rendered at all becomes a fixed placeholder carrying the exception's
*type name* and nothing else from the record — which also closes a second defect,
because a malformed record used to carry its `TypeError` into whichever handler
formatted it. An attached traceback or stack is redacted the same way, so the
guarantee covers everything a formatter appends rather than only the message.

**The pinned path is untouched:** uvicorn 0.32.1's five-argument access line still
has only its request target redacted, so client, method, HTTP version and status
code reach the journal intact. Every ordinary access record takes that path, which
is what makes the aggressive fallback affordable.

**Tests: 27 → 59.** Six leaking shapes, each asserted **twice** — once unfiltered to
reproduce the leak, once filtered to prevent it — plus the output guarantee
asserted directly, unrenderable records, idempotent re-filtering, the arity
boundary on the pinned format, and attached traceback and stack redaction. Every
assertion is made against the fully rendered `LogRecord.getMessage()` rather than
against mutated arguments. The live end-to-end proof was re-run against the
corrected filter and still passes.

**What remains.** The staging portal still runs the pre-fix code, so
**TC-OPS-05 stays `Failed` until the fix is deployed and SP-12 is re-run against a
fresh journal.** Deployment is a service restart under the Operations Owner's
authority. Raised for Codex as a security finding with its remediation attached.

### 5.4 SP-12 re-run after the N-7 deployment — 2026-08-26. **The token class is clean. TC-OPS-05 still fails, on a different class.**

**The 2026-08-26 first run in §5.2 is left exactly as written.** This is the
post-deployment re-observation it called for.

**Deployment.** Authorized by Peter Duscha, Operations Owner (change-log
**C-P3.5-V** item 4). `sudo systemctl restart freedom-web.service` at
**2026-08-26T12:26:49Z**, new main PID 296069, previous process active since
2026-08-25T22:46:33Z. The unit file was not touched. Rollback copy
`git show HEAD:tools/portal_server.py` taken **before** the restart and verified
to contain **no** filter, so the rollback really was the pre-fix code.

| Check | Result |
|---|---|
| `systemctl is-active` web / worker / bot | `active` · `active` · `active` |
| `/healthz` | `{"status":"ok", … all eight checks true …,"environment":"staging"}` — inside the 30 s rollback trigger |
| Rollback trigger | **did not fire** |

**Journal interval:** fresh, bounded at the restart —
`--since "2026-08-26 12:26:49"`. Operator: Peter Duscha, elevated access.
**21 lines**, reduced to distinct shapes with counts; **the counts sum back to
21**, so this is complete coverage rather than a sample.

| Class sought | Found? |
|---|---|
| Human or character names | **None** |
| Discord usernames or user IDs | **None** |
| Character identifiers beyond opaque UUIDs | **None** |
| **Tokens or credentials** | **None — N-7 is fixed on the deployed build** |
| **Client IP addresses in plaintext** | **YES — see N-13** |

**The N-7 line, observed on the deployed portal:**

```text
"GET /auth/discord/callback?<redacted> HTTP/1.1" 303 See Other
```

Method, path, protocol and status survive; nothing after the `?` does. **The
observed defect is fixed on the running system**, which is what the first run
could not say.

### N-13 — the deployed access log records the client IP address in plaintext

**Class: Important — privacy / operational disclosure. TC-OPS-05 fails on this
row alone; every other class is clean.**

**What was observed.** Every access line carries the client address before the
request, in the form `<addr>:<port>`. The literal value is **deliberately not
transcribed into this document in any form**, per execution plan §8.3 rule
"no raw address".

**Why this is a defect and not a judgement call.** The accepted operational
contract **§5** states, of every metric, log line and dashboard:

> Prohibited in every metric, log line and dashboard: Discord snowflakes,
> usernames, character names, Actor content, checksums of artifacts a viewer is
> not authorized to know about, tokens, grants, session identifiers, and **IP
> addresses in plaintext** (plan §9.4; existing `adapters/safe_logging.py`
> discipline).

**And it is the true visitor's address, not the proxy's.** The unit runs uvicorn
with `--proxy-headers --forwarded-allow-ips 127.0.0.1`, so the forwarded address
is what gets logged. On the same line as an OAuth callback, that records *which
address authenticated when*.

**Owning the cause.** The N-7 filter authored on 2026-08-26 **deliberately
preserved** the client field, and its own docstring presented that as a virtue:
"the client, method, HTTP version and status code reach the log untouched". That
was written without checking it against operational contract §5, which prohibits
it. The N-7 remediation fixed one prohibited class and left another in place
while describing the result as safe for operators to read.

**Severity, stated honestly in both directions.** *Not an emergency:* the journal
is readable only by `root` and `adm`/`systemd-journal`; the addresses are those
of the Operations Owner and the staging testers, not a community population; no
token, cookie, session identifier or credential appears. *A real finding
nonetheless:* the criterion and the contract are explicit, the same configuration
would behave identically in production, and there the population and the
sensitivity are both larger.

**Remediated in the repository 2026-08-26. Not yet deployed.**

The same `uvicorn.access` filter now replaces the client field with a
**keyed** pseudonym, `client-<8 hex>`:

- **Keyed, not a bare digest.** An unkeyed hash of an IPv4 address is not
  pseudonymisation: 2^32 candidates is seconds of compute. The key is
  `secrets.token_bytes(16)`, generated per process and never logged or persisted.
- **What it keeps.** Two lines from the same client in one process lifetime share
  a pseudonym, so an operator can still correlate a session during an incident.
  A restart re-randomises the key, so nothing correlates across restarts and
  nothing on disk can be joined to anything else. **This is the pattern the
  operational contract already accepts** for rate-limit trips, which it records
  as a bucket hash rather than an address.
- **The pinned path is exact**; the fallback path scrubs IP literals from the
  rendered text by finding candidates and validating each with `ipaddress`,
  which is **best-effort by construction** and is documented as such — a pattern
  alone would have rewritten every `12:34:56` timestamp in a traceback.

  > **Superseded 2026-08-28 by N-29; this bullet is left as written.** A
  > best-effort control cannot satisfy §5's prohibition, which has no
  > exceptions, and this bullet stated both facts in one sentence without
  > drawing the conclusion. Codex drew it. The fallback no longer scrubs text
  > at all: an unfamiliar record is withheld whole. See §5Q.

**Evidence, at two levels. Tests: 59 → 68.** Nine added, each falsified first —
the leak reproduced without the filter, then shown prevented: plaintext address
absent, method/path/version/status intact, same client to same pseudonym,
different clients to different pseudonyms, the pseudonym shown **not** to be a
bare digest, the fallback path, an IPv6 literal, a timestamp shown **not** to be
mistaken for an address, and re-filtering shown not to hash the hash.

**Two existing tests were amended, and the amendment is the honest kind:** both
asserted that the pinned path left the client field untouched, which is the
behaviour N-13 changes. They now assert the stronger property — exactly two
fields redacted, three provably unchanged — rather than being deleted.

**And end to end against a real running uvicorn**, on a throwaway port with a
trivial ASGI app:

```text
WITHOUT the filter:  <addr>:<port> - "GET /auth/discord/callback?code=<SYNTHETIC>&state=<SYNTHETIC> HTTP/1.1" 200
WITH the filter:     client-<8 hex> - "GET /auth/discord/callback?<redacted> HTTP/1.1" 200
```

**What remains.** The deployed portal still runs the address-leaking build.
**TC-OPS-05 stays `Failed`** until this is deployed and SP-12 is re-run over a
second fresh interval. Deployment is another service restart under the Operations
Owner's authority — and it deploys code **Codex has not reviewed**, which the
2026-08-26 N-7 deployment did not. Raised for Codex as a security finding with
its remediation attached.

### 5.5 SP-12 second re-run after the N-13 deployment — 2026-08-26. **TC-OPS-05 PASSES.**

**§§5.2 and 5.4 are left exactly as written.** This is the third observation in
the sequence and the first one that meets the criterion.

**Deployment.** Authorized by Peter Duscha, Operations Owner, as **P-5**
(execution plan §0.2) — explicitly distinct from the earlier authorization,
because this code has not been reviewed by Codex. `sudo systemctl restart
freedom-web.service`; new main PID **328111**; observed working at
**2026-08-26T14:17:47Z**.

**Journal interval:** fresh, bounded at the restart. Operator: Peter Duscha,
elevated access. **22 lines**, reduced to distinct shapes with counts. **The
counts sum back to 22** (one shape at 2, twenty at 1), so this is complete
coverage of the interval rather than a sample.

| Class sought | Found? |
|---|---|
| Human or character names | **None** |
| Discord usernames or user IDs | **None** |
| Character identifiers beyond opaque UUIDs | **None** — no UUID appears at all |
| Tokens or credentials | **None** |
| Client IP addresses in plaintext | **None** |

**The line that carried both defects, now carrying neither:**

```text
client-34b16d41 - "GET /auth/discord/callback?<redacted> HTTP/1.1" 303 See Other
```

Method, path, protocol and status survive. The credential does not. The address
does not. **And the pseudonym did the job it was kept for:** every access line in
the interval carries the *same* `client-…` value, so an operator reading this
window can still see it was one client throughout — which is the entire reason
the field was pseudonymised rather than deleted.

**TC-OPS-05: `Failed` → `Passed`**, at its required supervised evidence level, on
the deployed staging build, with exact commands, a bounded interval and complete
coverage.

**The coverage limit, stated rather than left implicit.** This interval contains
one browser session — visit, login redirect, OAuth callback, member read, logout
attempts — plus startup and shutdown. **The worker processed no job in it**, so
worker output *during* a real preview and apply is not yet observed. Those flows
arrive with M-7c and M-7d, and **SP-12 should be re-observed once after them**
before the gate package is submitted. That is a recommendation about completeness,
not a defect: the criterion as written is met by this run.

### 5.6 Two observations from the same output

| Observation | Assessment |
|---|---|
| `Uvicorn running on http://127.0.0.1:8001` at startup carries a literal address | **Not a finding, and recorded so a reviewer can disagree.** Operational contract §5 prohibits "IP addresses in plaintext", and the purpose it serves (plan §9.4, `adapters/safe_logging.py`) is personal and identifying data. This is the process's **own loopback bind**, which identifies nobody, is fixed by N-50, and is already stated in the unit file and the operational contract. It is emitted by uvicorn's startup message, not the access logger, so the N-13 filter does not reach it. **Deliberately not redacted:** an operator reading a startup line needs to know what the process bound to |
| **`POST /v1/auth/logout` answered `415 Unsupported Media Type` twice, and `401` once** | **Explained the same day by the Operations Owner's account; see §5.7. Not a sign-out defect, and not yet positively proved either.** The original assessment is retained below because it is what the evidence alone supported. **Open question — not resolved, and not a conclusion.** The handler's order is: no session cookie → `401`; bad origin → `403`; content type not `application/x-www-form-urlencoded` → `415` (`adapters/web/app.py:1002-1018`). So two POSTs arrived **with** a session cookie and a valid origin, carrying some other content type. **That cannot come from the sign-out control as shipped:** `templates/includes/header.html:39` is a plain `<form method="post">` with a hidden CSRF field, no JavaScript touches the route, and there is no `hx-boost` on it — a browser submitting it sends form encoding. **Why it matters enough to chase:** if a real sign-out click returns `415`, session revocation is broken on the deployed build, which is security-relevant and touches A-05 criterion 7, currently recorded **Met** from the 2026-08-24 session. **Possible benign explanations** — a stale tab from an older build, a browser extension, or a hand-made request — are equally consistent with the counts, and counts alone cannot distinguish them. **Referred to the Operations Owner for what he actually did, and to SP-11/M-7b to exercise sign-out deliberately and record the status code.** Raised for Codex |

### 5.7 The logout `415`s, explained — and a sitting it would have invalidated

**The Operations Owner's account, recorded verbatim in substance:** he was
prompted for *"a password for the user peter"*, the password he supplied was
wrong, he reloaded completely, landed back on the Discord sign-in page, and from
there everything worked.

**That prompt is the proxy gate, not the application.** The staging site imports
`/etc/caddy/freedom-blades-test.gate`, a Caddy `basic_auth` fragment whose
username is literally `peter` (`infra/caddy/freedom-blades-test.gate.example`).
**The platform has no password authentication at all** — N-13 forbids a permanent
local password, and break-glass is WebAuthn plus a host-local recovery grant — so
a password prompt could only ever have come from in front of the application.

**The mechanism that produces `415`, stated as a hypothesis rather than a
conclusion.** A `basic_auth` challenge arriving mid-flight interrupts the form
`POST`. The browser's re-issued request keeps the cookies and the origin — which
is why it reaches the handler's third check rather than its first or second — but
arrives **without the form body**, so no `Content-Type` header is declared and
`_form_content_type_is_supported` refuses it with `415`
(`adapters/web/app.py:1015`). Two retries, two `415`s. The single `401` is a later
`POST` with no session cookie, consistent with the complete reload he describes.

**What this does and does not establish.** It removes the reason to suspect the
sign-out control: the shipped control is a plain form with a hidden CSRF field and
nothing enhances it, and the account explains every observed status without it
being at fault. **It does not positively prove sign-out works on this build.** The
decisive check is one deliberate sign-out click with the gate credential already
accepted, reading the status code — two minutes, and it belongs in **SP-11 /
M-7b** regardless. **A-05 criterion 7's `Met` status is left as it stands**, on
the 2026-08-24 evidence, and is re-confirmed there.

### N-14 — the proxy gate makes TC-SEC-07's evidence run impossible as scheduled

**Class: Important — evidence validity and sequencing. Found by chasing the
`415`, not by reading the plan.**

The deployed staging site file says so itself, in a comment written when the gate
was introduced (`infra/caddy/freedom-blades-test.caddy:24-26`):

> **This gate must be gone before the final security-header evidence run**: a 401
> in front of the application is not the response the accepted contract
> describes, and TC-SEC-07 must observe the application's own answers.

**The run sheets did not account for it.** M-5 (SP-14, the browser-observed
security headers and CSP on normal, early and error responses) would have been
performed with a `basic_auth` challenge in front of every route, and the "early
response" case in particular would have observed **Caddy's 401**, not the
application's. That evidence would have looked complete and been wrong — the same
failure class as citing a passing test against the wrong contract row (F-1).

**A second consequence, for the higher-stakes sittings.** The same mid-flight
challenge can interrupt **any** form `POST`, including the Council import
**apply** confirmation in M-7b and the measured apply in M-7c. There it would not
merely produce a confusing `415`: it would corrupt a measurement or make a
successful apply look like a failure.

**What is needed, and it is a decision rather than a task.** Removing the gate
changes the staging site's exposure — Certificate Transparency published the
hostname within minutes of issuance, which is the reason the gate exists
(`freedom-blades-test.caddy:18-22`). Options, for the Operations Owner:

1. **A tightly bounded gate-off window** covering M-5 and the M-7 sittings, with
   the gate restored immediately afterwards and both changes recorded with
   timestamps. *Recommended:* it is the smallest exposure that yields valid
   evidence, and it is the sequence the site file already anticipates.
2. **Swap the password gate for an address allowlist** for the duration. The site
   file records why an allowlist was rejected originally — the responsive checks
   need a laptop **and** a phone on mobile data — so this trades one operator
   burden for another and would complicate M-6.
3. **Accept the gate and record TC-SEC-07's browser half as `Not Run`.** Honest,
   and it leaves an I-06 criterion open.

**Practical note on the password itself.** `infra/staging/rotate-test-gate.sh`
generates a new verifier and **prints the password once** to the operator's
terminal, writing it nowhere. That is the supported way to recover a credential
nobody has to hand. No credential material is read, printed or recorded by this
package.

## 5A. M-1 — SP-02 and SP-03, executed 2026-08-26

**Grant:** SG-2 (change-log C-P3.5-V item 2). **Operator:** Peter Duscha at his
own console with elevated access; Claude recorded. **No host state was changed
and neither environment file was opened.**

### SP-02 — independently generated staging secrets, outside the repository. **Passed, with deviation N-15.**

| Check | Result |
|---|---|
| `sudo stat -c '%a %U:%G %n' /etc/freedom-blades/portal.env /etc/freedom-blades/worker.env` | `640 root:freedomweb` for **both** |
| Outside the repository | **Yes** — both under `/etc/freedom-blades/`, and the repository is `/opt/freedom-blades/platform` |
| Not world-readable | **Yes** — no `other` bits |
| Root-owned | **Yes** |
| **Operations Owner's attestation** | **"Yes"** — the staging secrets share **no value** with production and were generated independently. This is a statement he makes, not a file anyone reads: it cannot be established by inspection and must not be |

**The files were not opened by this procedure.** Only their metadata was read, and
separately four identifier lines for SP-03 by an expression anchored to exact
variable names, which cannot match `WEB_DISCORD_CLIENT_SECRET`.

### N-15 — the environment files are `0640`, where SP-02 specifies `0600`

**Class: Minor — deviation from the written procedure. Recorded rather than
repaired.**

Execution plan §6.2 SP-02 says "place a `0600` environment file **outside** the
repository". The deployed files are `0640 root:freedomweb`, so the `freedomweb`
**group** can read them.

**Why the security-relevant properties still hold:** the files are root-owned, not
world-readable, and outside the repository — which is what the procedure exists to
establish.

**Why the group bit is nonetheless unnecessary:** systemd reads `EnvironmentFile`
**as root**, before dropping to `User=freedomweb`, so the service does not need
group read to start. `0600 root:root` would work.

**Why it is close to harmless anyway, stated so the finding is not inflated:** the
only accounts that gain by the group bit are ones already running as
`freedomweb` — and such a process can read its own `/proc/self/environ`, which
holds the same values. The bit widens the surface from "processes that already
hold these secrets" to "any process that account runs".

**Disposition — downgraded 2026-08-26, later the same day, on new evidence.**
The recommendation to tighten to `0600` is **withdrawn as unnecessary**. The
containing directory `/etc/freedom-blades` is **`750 root:root`**, and
`freedomweb` is not in group `root`, so the service account **cannot traverse the
directory and cannot open either file** — the group-read bit on the files is
unreachable. systemd reads the `EnvironmentFile` as root before dropping
privileges, which is why the service works regardless.

**How this was established, and it was not by inspection:** an attempt to run the
worker's own entry point as `freedomweb` with the environment files sourced
produced *"WEB_DISCORD_GUILD_ID: is required and was not set"* for most of the
configuration — the sourcing had silently failed because the account cannot reach
the files. The directory mode was then read and confirmed.

**N-15 therefore stands as a deviation from SP-02's literal wording (`0640`, not
`0600`) with no security consequence**, because the directory already enforces
what the file mode was meant to. No change is recommended. Recorded rather than
deleted, because the original assessment was published in this document and a
reader should see it corrected rather than silently revised.

### SP-03 — separate staging Discord application, guild and role. **Passed.**

Identifiers only. No secret was read, and none appears here.

| Variable | Value | Assessment |
|---|---|---|
| `WEB_DISCORD_CLIENT_ID` | `1541101102571724890` | A separate application. **Cannot be checked against a recorded production value, because the repository records none** — there is no `PRODUCTION_CLIENT_ID` constant, since S-07 checks only for an `.env.example` placeholder in production. **This half rests on the Operations Owner's attestation**, and is recorded as resting on it |
| `WEB_DISCORD_GUILD_ID` | `1541104273872392273` | **Not the production guild** (`PRODUCTION_GUILD_ID = 1052698198180892733`, `config.py:64`). Independently enforced: S-07 refuses a non-production process configured with the production guild, so the portal running at all already implied this — now it is recorded explicitly rather than inferred |
| `WEB_BOOTSTRAP_ADMIN_ROLE_ID` | `1541113163578216468` | A role in the staging guild |
| `WEB_DISCORD_REDIRECT_URI` | `https://freedom-blades-test.rpgworld.org/auth/discord/callback` | The **staging** origin (decision D-j), not production. S-05 independently requires it to share the public origin |

**Operations Owner's statement:** *"Yes, we specifically created that Discord
server for testing purposes."*

**And the identifiers corroborate the statement independently.** A Discord
snowflake carries its own creation time in its high bits, so these four values
date themselves:

| Identifier | Created |
|---|---|
| Production guild `1052698198180892733` | **2022-12-14T21:26:48Z** |
| Staging application `1541101102571724890` | **2026-08-23T15:05:35Z** |
| Staging guild `1541104273872392273` | **2026-08-23T15:18:11Z** |
| Staging admin role `1541113163578216468` | **2026-08-23T15:53:30Z** |

The three staging identifiers were created **within 48 minutes of one another**,
on **2026-08-23** — the day SG-1 and the staging-address decisions were taken —
and **3 years 8 months after** the production guild. That is consistent with a
test server created for this purpose and inconsistent with a reused production
object. **This is corroboration, not proof of the secret's separation**, which
remains an attestation.

**What SP-02 and SP-03 close, and what they do not.** Both feed **I-06 closure
criterion 1**, which also needs the separate database and roles (SP-01, evidenced
with deviation **N-5**), the separate web identity (SP-04, **Passed**), the
migration head (SP-06, evidenced), and the loopback bind behind the accepted proxy
boundary — whose *parity* half is **SP-13 / TC-LIM-02** and is still **Not Run**.
**I-06 remains Open.**

## 5B. M-2 — SP-09 / TC-OPS-01, executed 2026-08-26. **Passed.**

**Grant:** SG-2. **Operator:** Peter Duscha engaged and released as root; Claude
ran the loopback observations. **Sitting opened 2026-08-26T15:28:37Z; portal
verified recovered 2026-08-26T15:47:33Z.**

**Layer 1 only**, the file-based switch (operational contract §4.3). The switch
file is `/srv/freedom-blades/web/kill-switch`, in a directory owned
`root:freedomweb` with no group write — so engaging and releasing are **root**
actions, which is what the directory mode enforces rather than merely documents.

### While engaged

| Observation | Result |
|---|---|
| `/v1/characters`, `/v1/login`, `/v1/council/audit`, `/` | **503** |
| `POST /v1/auth/logout` — a mutation route, with a valid form content type | **503**. The switch closes mutations, not merely reads |
| Response shape on a blocked route | `text/plain`, `Retry-After: 300`, `Cache-Control: no-store`, and the full security header set: `content-security-policy` (N-26 in full), `x-content-type-options: nosniff`, `referrer-policy: same-origin` |
| Maintenance body, in full | *"The Freedom Blades portal is temporarily unavailable for maintenance. The Discord bot is unaffected."* — **no exception detail, no internal path, no identity** |
| `/static/css/…` | **200**, `text/css`, serving normally |
| `/healthz` | **Reachable**, `application/json`, `status: degraded`, `kill_switch: false`, the seven other checks **all `true`** |
| `freedom-worker.service`, `freedom-bot.service` | both **active** throughout |
| **Discord bot answering a command** | **Confirmed by the Operations Owner** |
| **Foundry loading** | **Confirmed by the Operations Owner** |

**The last two rows are the ones TC-OPS-01 exists for.** A switch that closes the
web perimeter *and* the community's bot would be an outage, not a kill switch. The
loopback observations alone could never have shown that, which is why the
criterion names them.

### After release

| Route | Result |
|---|---|
| `/healthz` | **200**, `status: ok`, `kill_switch: true`, all eight checks true |
| `/v1/login` | **200** |
| `/v1/characters` (unauthenticated) | **303** to login — the application's own boundary, back in force |
| `/`, `/static/css/…` | **303**, **200** |

**Recovery is complete and was verified, not assumed.**

### A correction to this package's own run sheet, not to the portal

The run sheet said to expect **200** from `/healthz` while engaged. That
expectation was **wrong**. `/healthz` carries a `kill_switch` check of its own, so
an engaged switch makes it report `status: degraded` and answer **503** — with a
JSON body naming the cause. The accepted criterion is that the switch must not
**refuse** `/healthz`, and it does not: the response is the health route's own
verdict, distinguishable from the middleware's by its `application/json`
content type and its absence of `Retry-After`.

**That distinction is worth more than the criterion asks for.** A monitor polling
this endpoint is told *"deliberately in maintenance"* rather than *"host is
gone"*, which is exactly what keeping health up during an incident is for. The
run sheet is corrected; nothing in the portal is.

### N-16 — the tool's success message understates what stays up

**Class: Minor — operator-facing message accuracy. Not a behaviour defect.**

`tools/portal_kill_switch.py` prints *"Every portal route except /healthz now
answers 503 within one second."* **Two prefixes stay up, not one:** `/static/` was
added by the accepted D-03 correction (item D-03-1), so the maintenance body, the
login page and the safe error page keep their presentation while the portal is
disabled. The middleware docstring and the route contract both say so; only this
message does not.

**Why it is worth fixing rather than shrugging at:** an operator reading it during
an incident would expect the login page to come back unstyled, and could mistake
correct behaviour for a second fault at exactly the moment they are least able to
investigate calmly. One line. Offered to the Operations Owner; **not changed
unilaterally**, because it is outside this package's authorized change scope.

### N-17 — the engage timestamp was not captured

**Class: Minor — evidence hygiene. Recorded for the next run of this procedure.**

The tool writes the exact engage time *into the switch file*, and the release
deletes the file — so the precise moment the switch was engaged is not recoverable
after the fact. This sitting is bounded by its recorded start (`15:28:37Z`) and
its verified recovery (`15:47:33Z`), which is sufficient for the criterion but
looser than every other timestamp in this document.

**Correction applied to the run sheet:** `date -u` immediately before and after
**each** of engage and release, so the window is bounded at both ends by an
observation rather than by inference.

## 5C. M-3 — SP-08 and SP-13, executed 2026-08-26

**Grant:** SG-2. **Operator:** Peter Duscha at the console; Claude designed the
method and verified recovery. **Opened 16:13:45Z.** Rollback taken first:
`/etc/freedom-blades/portal.env.pre-sp08`, `cp -a`, confirmed present before any
change.

### The method, and why it is not the one the run sheet first described

The sheet called for twelve edit-restart-read-restore cycles on the live service:
twelve deliberate outages with a single backup between the sitting and a portal
that will not come back. **Method B was adopted instead**, with the Operations
Owner's agreement:

1. **One real restart-to-failure** on the deployed unit, proving the whole chain
   — the environment file, systemd, the unit and the supervisor's handling of a
   non-zero exit.
2. **Every other refusal** through `tools.startup_refusal_probe`, which calls
   **the same `WebSettings.from_environment` the deployed process calls at
   startup**, under the same interpreter, against the same environment file, with
   exactly one variable overridden. No socket, no service touched, no downtime.

**The evidence level, stated rather than implied.** For the probe-observed
refusals this is evidence at the *configuration* layer: this build, this
configuration, this refusal. It is **not** evidence that systemd behaves
correctly when a refusal happens — that chain is proved once, by S-11 below, and
nothing here claims the probe covers it.

**Why the probe output is safe to quote.** `ConfigurationError` is value-free by
construction, and the probe prints that error and nothing else — it never prints,
iterates or summarises the environment it read, which matters because that
environment holds every secret the portal has. The property is falsified in
`tests/web/test_startup_refusal_probe.py`: a distinctive secret is handed in and
asserted not to come back out.

### SP-08 / TC-OPS-04 — refusals observed

| Refusal | Observed | How |
|---|---|---|
| **S-01** | ✅ | production marker against the staging database — *"must name the production database (freedom_production) … not 'freedom_staging'"* |
| **S-02** | ✅ **both directions** | production-marked with a non-production origin (*"must be exactly the accepted production origin (N-01) in production"*), **and** non-production claiming the production origin (*"would receive production cookies and OAuth callbacks"*). The full N-01 fence, not half of it |
| **S-03** | ✅ | `WEB_COOKIE_SECURE=false` outside development |
| **S-04** | ✅ | wildcard host, and the omitted-own-host case in the same run |
| **S-05** | ✅ **both directions** | a foreign redirect not sharing the public origin, **and** the production requirement that it be exactly N-02 |
| **S-06** | ✅ | scope creep beyond N-03 |
| **S-07** | ✅ | production process pointed at the staging guild — *"would authorize the wrong community"* |
| **S-08** | ✅ | **using the real key values**: `WEB_SECRET_KEY_CURSOR` set to the deployed `WEB_SECRET_KEY_CSRF`. The refusal names both variables and prints neither. A real-value test with zero disclosure |
| **S-09** | ✅ | registrable-domain RP id, plus the allowed-host-suffix and WebAuthn-origin cases |
| **S-10** | ✅ | `WEB_SESSION_IDLE_MINUTES=90` — *"may tighten an accepted policy and never loosen it"* |
| **S-11 web** | ✅ **on the deployed unit** | see below |
| **S-11 worker** | ✅ | probe, `--role worker` — *"a worker started with it false would claim no job while appearing to run"* |
| **S-12** | ❌ **Not Run** | Not a configuration check: it needs the artifact filesystem through `run_resource_checks`. Scheduled with M-4, where a database connection is already in play |
| **S-13** | ➖ **not observable here** | A module-graph property enforced by a test. Making the bot's `config.py` importable would be a deployment mutation with no path back inside a sitting |
| **S-14** | ⏭ **deferred to M-4** | Needs an Alembic mismatch, which M-4 creates deliberately **with a pre-migration backup in hand** |
| **S-15** | ⏭ **SP-27, in M-1c** | Needs a production-marked process and a credential query |

**Eleven of fifteen observed; one of those on the deployed unit end to end.**
TC-OPS-04 is **not yet complete** and is recorded as such.

### S-11 on the deployed unit — and the run-sheet defect it exposed

`WORKER_ENABLED=true` was written into the deployed `portal.env` and the service
restarted. The journal shows the refusal, repeatedly:

```text
application.web.config.ConfigurationError: The web portal refuses to start: 1 configuration problem(s).
  - [S-11] WORKER_ENABLED: must be false in the web process. …
freedom-web.service: Failed with result 'exit-code'.
freedom-web.service: Scheduled restart job, restart counter is at 1.
```

…through restart counter 5 and beyond, until the file was restored from the
backup. Final state: `NRestarts=8`, then recovery at **16:31:22Z**, PID 369521,
`/healthz` `status: ok` with all eight checks true. **Verified, not assumed.**

**N-18 — `systemctl restart` returning 0 is not evidence the configuration was
accepted.** *Class: Important — run-sheet defect in this package, corrected.* The
sheet said to restart and read `systemctl status`. Done literally, that showed
`Active: active (running) since … 8ms ago` and an exit status of `0` — because
systemd had successfully *started* the unit, milliseconds before the process
evaluated its configuration and exited. **An operator following the sheet would
have concluded S-11 did not fire while the service was crash-looping.** The check
is `NRestarts`, or the journal, taken a few seconds later. Corrected in the run
sheet.

### SP-13 / TC-LIM-02 — proxy and application limit parity

| Side | Value |
|---|---|
| Application, deployed | `WEB_MAX_REQUEST_BYTES=1048576` |
| Caddy, deployed | `request_body { max_size 1MiB }` |

**1 MiB = 1048576 bytes. The parity assertion holds exactly**, and the deployed
Caddy file carries a comment naming this very test as its reader.

**The snapshot route, and why its absence is not a gap.** TC-LIM-02's wording
names "both the general and the snapshot route". **There is no 64 MiB block on
either side, and that is the accepted design, not an omission**: the route
contract §1.2 admits exactly one mount in this process (the static assets), so no
route served here may exceed the general bound. The production template states
this explicitly and fences the future change — *"If a later package mounts it,
this file and N-55 change together or the parity assertion fails."* **Proxy and
application therefore agree about the snapshot route as well: neither has one.**

**Flagged for Codex** rather than quietly resolved, because the accepted row names
two routes and only one exists in this deployment. The alternative reading — that
the row cannot close until a submission route is deployed — would make TC-LIM-02
un-closable in Phase 3, since nothing accepted for Phase 3 promised that route
(finding **N-3**).

**SP-13 / TC-LIM-02: Passed**, with the snapshot half recorded above.

### N-19 — the deployed environment file is not shell-sourceable

**Class: Minor — operational hazard, found by using it.** Sourcing
`/etc/freedom-blades/portal.env` into bash produced
`line 43: Blades: command not found`: the file holds `WEB_WEBAUTHN_RP_NAME` with
an unquoted multi-word value. systemd's `EnvironmentFile` parser handles that
correctly; `.` in a shell does not — it treats the value's first word as an
assignment prefix and the second as a command, so **the variable is silently
absent from the resulting environment**.

**It did not affect this sitting's results:** `WEB_WEBAUTHN_RP_NAME` is a display
string the configuration layer does not require, and had any *required* variable
been dropped, every probe run would have reported `is required and was not set`.
None did.

**Why it is still worth recording:** any operator procedure that sources this file
— including the one in this package — silently loses that variable, and a future
file could put a required value on such a line. **Two fixes, neither taken
unilaterally:** quote the value in the environment file, or teach the probe to
parse `EnvironmentFile` the way systemd does rather than relying on the shell.
The second is the more durable and is offered to the Operations Owner.

## 5D. M-4 — SP-10, S-14 and the finding that justifies the whole procedure

**Grant:** SG-2, with **D-q** route A applied. **Opened 17:18:58Z.** Operator:
Peter Duscha stopped and started the units; Claude ran the database work and the
verification. **Both services were stopped first** — the portal's pooled
connections would block a schema drop, and the worker must not touch a
half-restored schema. Verified before proceeding: both `inactive`, **zero
connections** to `freedom_staging`, `freedom-bot` untouched and `active`
throughout.

### Pre-state, and a backup that was checked rather than assumed

| # | Step | Result |
|---|---|---|
| 1 | Revision | `0013` |
| 2 | Census | `platform_accounts=2` · `webauthn_credentials=4` · `sessions=19` · `audit_events=49` · `discord_users=1` · jobs/imports/snapshots `0` |
| 3 | Tables | **31** |
| 4 | `pg_dump -Fc` → `pre-sp10.dump` | 143,986 bytes, mode `0600`, SHA-256 recorded |
| 5 | **`pg_restore -l` on the dump** | **241 archive entries listed** — the backup is a *readable archive*, not merely a file that exists. §14.3's "restore-tested, not reported successful", applied to the backup before anything depended on it |

**This database holds real data** — the Operations Owner's two enrolled passkeys,
his Discord identity and 49 audit rows. The consequence of a failed restore was
put to him before the destructive step: A-05 criteria 1, 2, 2a, 3, 5, 6, 7 and 8
would lose their evidence base and need a fresh SG-3 ceremony. He accepted it
against the three mitigations (this dump, the drill's own dump, and the identical
drill already exercised on `freedom_test`).

### S-14 on the deployed unit

`alembic downgrade -1` took staging to `0012` and dropped `effect_result`. The
portal was started and refused, repeatedly:

```text
[S-14] WEB_DATABASE_URL: is at Alembic revision '0012' but this build's
migrations end at '0013'. A process serving a schema it was not built for is a
data-integrity risk.
freedom-web.service: Failed with result 'exit-code'.
```

`alembic upgrade head` returned it to `0013`. **Census after the round trip:
identical** — `2 / 4 / 19 / 49`, 31 tables. The credentials survived the
downgrade/upgrade pair.

### SP-10 — the drill

`FREEDOM_DRILL_ALLOW_STAGING=1 FREEDOM_DRILL_STAGING_CONFIRM=freedom_staging
./infra/postgresql/backup-restore-drill.sh freedom_staging <workdir>` — **exit 0**,
`Restore verified for freedom_staging`. The destroy step cascaded through all 31
tables and **six trigger functions**.

**Verified independently, because the script's own verdict is not evidence:**

| Check | Result |
|---|---|
| Revision | `0013` |
| Census vs pre-state | **identical** — `2 / 4 / 19 / 49 / 1` |
| Tables | **31** |
| Guard functions restored | **6 / 6** |
| User triggers restored | **10** |
| **Append-only still refuses** | `ERROR: append-only table audit_events: DELETE is refused. History is corrected by appending a compensating record, never by editing it.` |

The last row was run inside a transaction that was **rolled back**, so the answer
was obtained without risking a row either way. A restore that returned the rows
but not the guards would pass a row-count comparison and still be a failure.

### N-20 — the restore silently drops the runtime role's privileges

**Class: Blocking for I-06 and for the deployment gate — recovery correctness.
Found by SP-10, which is what SP-10 is for.**

**What was observed.** Both units were started after the successful restore and
**both crash-looped**, to `NRestarts=35` and `36`, until the cause was found. The
cause was not the data:

| | Before the drill | After the restore |
|---|---|---|
| `sessions` privileges | `foundry=arwdDxt`, **`freedomweb=arw`** | `foundry=…` **only** |
| `public` schema ACL | populated | **`(none)`** |

**The row inventory was perfect and the platform could not read its own
database.**

**The mechanism, named precisely** (`backup-restore-drill.sh:246`):

```bash
RESTORE_COMMAND=(pg_restore --dbname="${DATABASE}" --no-owner --no-privileges
                 --single-transaction --exit-on-error "${DUMP}")
```

**`--no-privileges` instructs `pg_restore` to skip every `GRANT` and `REVOKE` in
the archive.** The dump is not at fault and the backup is not incomplete: the
ACLs are in the archive, and the restore is told to discard them. `--no-owner`
compounds it — restored objects belong to whoever ran the drill rather than to
their recorded owner.

**So the defect is sharper than "a row count cannot see a missing GRANT".** It is
that **the drill deliberately discards exactly the state its verification cannot
see.** Those two decisions are individually defensible and jointly produce a
restore that reports success on a database the application cannot use.

**Why the flags are there, and why the defect survived.** `--no-owner
--no-privileges` is the portable choice: it lets a dump restore into a cluster
whose roles differ, without failing on a `GRANT` naming a role that does not
exist there. With `--exit-on-error`, an unknown role would otherwise abort the
whole restore. On the disposable `freedom_dev` and `freedom_test` targets the
drill was written for, **only the owner ever connects**, so nothing depends on a
second role's privileges and the discarded ACLs are never missed.
`freedom_staging` is the first target with a genuinely restricted runtime role —
which is why this is the first run that could have exposed it.

**And EX-3 on `freedom_test` re-applied `runtime-grants.sql.tmpl` as a separate
later step**, so even there the gap was covered by the next thing in the sequence
rather than exposed by it. Two procedures in the right order can hide a defect
that either one alone would show.

**Why it matters beyond staging.** Plan §14.3 requires "restore tests, not merely
backup success messages", and this is precisely the failure that distinguishes
the two. In production the sequence would be: an incident, a restore, a report of
success, and a portal that stays down — an outage *after* the recovery, at the
moment an operator has least capacity to diagnose it. The remedy is a single
documented command, and **nothing in the procedure says to run it and nothing in
the drill checks for it.**

**Recovery, applied within the granted authority and verified.**
`sed 's/__APP_ROLE__/freedomweb/g' infra/postgresql/runtime-grants.sql.tmpl |
psql -d freedom_staging -v ON_ERROR_STOP=1 -f -` → exit 0. Then:

- `sessions` privileges: **`freedomweb=INSERT,SELECT,UPDATE`** restored;
- `has_table_privilege('freedomweb','sessions','TRUNCATE')` → **false**, so the
  restricted posture is restored and not widened;
- both units **`active`**, `SubState=running`, `/healthz` `status: ok` with all
  eight checks true, at **17:29:18Z**.

**Recommended remediation, for the Operations Owner and Codex — not applied
here.**

| Option | What it does | Assessment |
|---|---|---|
| **1. Drop `--no-privileges`** | ACLs restore from the archive | **Insufficient alone, and it can make things worse.** With `--exit-on-error`, a `GRANT` naming a role absent from the target cluster aborts the entire restore — turning a recoverable state into a failed one, during an incident |
| **2. Re-apply `runtime-grants.sql.tmpl` as a final step** | Restores the grant state deterministically, from the template that is already the single source of truth | Correct, but a step that must be remembered is exactly what failed here |
| **3. Extend the verification to assert the runtime role's privileges** | The comparison stops being blind to what the restore discards | Correct, and it is the half that makes any of the others durable |
| **2 + 3 — recommended** | Re-apply, then assert | The template already exists, `tests/test_runtime_grants.py` already encodes what correct looks like, and the drill gains a check that fails **loudly** instead of a report that succeeds quietly |

**The argument for including 3 regardless of which fix is chosen:** the failure
mode here was not that somebody forgot a step — it was that **nothing was looking
at the thing that broke.** A remediation that adds a step but no assertion leaves
the drill able to report success on a broken restore for some *other* reason
nobody has thought of yet.

**SP-10 / TC-OPS-02 staging half: Passed as a procedure — backup, destroy,
restore, inventory and guard verification all executed and verified — with N-20
recorded as a Blocking finding against the recovery procedure it exercised.**

### N-20 remediated — 2026-08-26, option 2 + 3 approved by the Operations Owner

**Applied to `infra/postgresql/backup-restore-drill.sh`.** The restore flags are
**unchanged**: reverting `--no-privileges` would trade a recoverable state for a
restore that aborts mid-incident on a `GRANT` naming an absent role. Instead the
drill now handles the privilege state deliberately and then proves it.

| Step | What it does |
|---|---|
| **3b** | Records the privilege inventory before the destroy — table grants **and** schema ACLs, because the staging failure left `public` with no ACL at all and a table-only inventory would have missed it. Detects the runtime role as *the non-owner, non-PUBLIC grantee holding table grants*, **derived rather than configured**, so no per-database mapping can fall out of step |
| **5b** | Re-applies `runtime-grants.sql.tmpl` for that role, from the template that is already the single source of truth. Skipped, with a message, when no runtime role held grants. **Fails closed** if the template is unreadable |
| **6b** | Compares the privilege inventory and **fails** when an entry present before is absent after |
| — | Refuses outright when **more than one** non-owner role holds grants, because which role the template should name would be a guess |

**A defect in the first version of this fix, found by running it.** Step 6b
originally required the two inventories to be *identical*. That is wrong: step 5b
re-applies the canonical template to every table, so a database whose grants had
drifted legitimately ends with **more** entries than it started with, and exact
equality fails the drill for having repaired something. It surfaced immediately —
an existing, unrelated test began failing. **The check now asserts loss, not
difference**, which is the property N-20 is actually about.

**Both directions tested, in `tests/test_database_backup_restore.py`:**

- `test_the_drill_leaves_the_runtime_roles_privileges_intact` — the drill exits 0,
  names the detected role, and the privilege count is unchanged;
- `test_the_drill_fails_when_the_privilege_state_is_not_restored` — the drill is
  copied beside its own template with step 5b removed, reproducing exactly the
  pre-N-20 behaviour, and **must** now fail with *"privileges present before the
  drill are missing after it"*.

**The second test is the one that matters**, and it earned its place: an earlier
attempt at it passed *vacuously*, because a previous broken run had already
stripped the grants, so there was nothing left to lose. The test now asserts its
own precondition — that the runtime role holds privileges before it starts —
rather than trusting the database to be in the state it expects.

**Verified against a live database, not only in tests:** with step 5b removed the
drill exits **1** with the new message; with it, `freedom_test`'s 99 runtime
privilege rows survive the round trip. Suite: **35 passed** in that file.

**Not yet re-run against `freedom_staging`.** The remediation is proved on the
disposable database; **SP-10 should be repeated once on staging** to observe the
fixed drill restoring the runtime grants there, since staging is the only target
with a genuinely restricted runtime role and therefore the only one where the
original defect was reachable.

## 5O. Deployment of the three undeployed remediations — executed 2026-08-27

**Authorized by Peter Duscha on 2026-08-27**, after the EX-11 handoff's
implementation tasks were completed. Submission §7 listed three remediations as
**repository-only**; this section records their deployment. It records a
deployment, not an acceptance: neither the Phase 3 gate nor any finding is closed
by it.

### 5O.1 HSTS (N-22) — deployed 22:06 UTC

`/etc/caddy/freedom-blades-test.caddy` was replaced with
`infra/caddy/freedom-blades-test.caddy`, a **one-directive delta** confirmed by
`diff` beforehand. Backup taken to
`/etc/caddy/freedom-blades-test.caddy.before-hsts-20260827T220639Z` (4891 bytes).

**Byte-identity held at deployment, was briefly broken, and was restored at
23:06 UTC.** The `includeSubDomains` comment correction below changed the
repository file by 27 comment lines; it was copied to `/etc/caddy` the same
evening and `caddy validate` returned `Valid configuration`. `diff` of the
deployed file against `infra/caddy/freedom-blades-test.caddy` is now **empty**.

Caddy was **not reloaded** for that copy and did not need to be — the change is
comments only. `NRestarts=0` and `ExecMainStartTimestamp=2026-08-25 22:27:12 UTC`
are unchanged, and the header was re-confirmed on the wire afterwards at both the
origin (`server: Caddy`) and the edge, still `max-age=31536000`.

`caddy validate --config /etc/caddy/Caddyfile` → `Valid configuration`, with the
expected OCSP-stapling warning for the Cloudflare Origin CA certificate (it
carries no issuer URL) and the five already-loaded certificates. Applied with
`systemctl reload caddy`.

**Captured twice, deliberately.** Through the Cloudflare edge — the path a real
visitor takes — and again at the origin with `--resolve …:443:127.0.0.1`:

| Capture | `server:` | `strict-transport-security:` |
|---|---|---|
| Cloudflare edge | `cloudflare` | `max-age=31536000` |
| Caddy origin | `Caddy` | `max-age=31536000` |

**The second capture is the one that proves the claim.** Cloudflare has its own
HSTS feature, so an edge capture alone cannot distinguish a header this platform
emits from one the edge added. `server: Caddy` settles it.

The value is exactly the accepted one: `max-age=31536000`, **no
`includeSubDomains`**, **no `preload`**.

**The reload was confirmed by effect, not by exit code** (N-18). `systemctl show
caddy` reports `ActiveState=active`, `NRestarts=0` and
`ExecMainStartTimestamp=2026-08-25 22:27:12 UTC` — the process did not restart,
so this was a genuine in-place configuration reload, and the header on the wire
is the evidence it took effect.

**Both captures are `HTTP/2 401`**, because the site-wide test gate is still in
place. That is expected and is not a defect: HSTS is a transport statement and is
asserted on every path. The gate must still be removed before the final
TC-SEC-07 evidence run, per the Caddy file's own comment.

**Scope limit.** `infra/caddy/freedom-blades-portal.caddy.tmpl` carries an
identical HSTS line and **was not deployed and could not be**: no
`freedom-blades-portal` file exists under `/etc/caddy`, because that hostname
does not exist yet. The production block's HSTS is verified by inspection and by
nothing else.

**The recorded reason for omitting `includeSubDomains` was wrong, and is
corrected 2026-08-27.** Both Caddy files, and the test that enforces the
omission, said the directive was reserved because it "would cover the sibling
Foundry hosts under the same registrable domain". **It would not.**
`includeSubDomains` binds the sending host and names *beneath* it
(RFC 6797 §6.1.2), so `foundry1.rpgworld.org` and its two peers are **siblings of
the portal names, not subdomains of them, and are unaffected either way**. The
`/etc/caddy/Caddyfile` was checked: every block serves a third-level name and
**no block serves the apex `rpgworld.org`**, which is the only place the sibling
reasoning could ever have applied.

**The decision is unchanged and the omission stands**, on a reason that holds: no
name exists beneath either portal host, so the directive buys nothing today while
committing every future name under it to HTTPS-only for the whole `max-age`,
before anything is known about what those names will serve. The contract's
reservation of the directive to the Operations Owner is a governance rule and is
untouched.

Corrected in `infra/caddy/freedom-blades-test.caddy`,
`infra/caddy/freedom-blades-portal.caddy.tmpl` and the docstring and failure
message of `test_hsts_does_not_claim_subdomains_or_preload`. **No assertion and
no directive changed** — the test still requires the directive's absence, and a
comments-stripped diff of the Caddy file against the deployed copy is empty.

**Two canonical statements still carry the wrong premise and were NOT amended**,
because amending an accepted contract is not this package's to do:
`docs/contracts/phase-3-operational-contract.md` §4.1's HSTS row
(*"`includeSubDomains` only after the Operations Owner confirms no sibling host
would break"*) is the origin of the framing, and §5G's decision table repeats it.
The **rule** each states is still workable — the reservation is a governance
requirement and the Operations Owner can simply confirm that no sibling can break
because siblings are not covered — but the technical premise inside it is false
and has now propagated to four places. **Recommended for amendment at the gate.**

**One observation, not a finding, and pre-existing.** The same site block carries
`header -Server`, and the origin 401 nonetheless answers `server: Caddy` — one
header directive taking effect where another does not. The only change to that
file was the HSTS block (confirmed by `diff` against the backup), so this is not
caused by the deployment. It does not currently reach the internet, because the
edge substitutes `server: cloudflare`. It could not be diagnosed further: the
gate returns 401 on every path, including `/healthz` and `/enrol`, so no non-error
response is observable without the gate credential, which was not read.
**Recheck when the gate is removed** — that is simultaneously the first moment a
200 exists to test against and the moment the edge stops being the only thing
covering it.

### 5O.2 Foundry module 1.0.9 — deployed to **three** instances

**Scope changed from the handoff, on the Acceptance Authority's explicit
instruction.** The handoff named foundry1 and foundry3. Peter directed
installation on **foundry1, foundry2 and foundry3**. Recorded here because it is
a deviation from the written procedure, decided by the authority entitled to
decide it — not absorbed silently.

**foundry2 had never carried this module at all.** Established by counting
directory entries before the change: foundry1 and foundry3 held 58 modules,
foundry2 held 57, and `freedom-blades-export` was absent from both of foundry2's
paths. So this is a **first installation** there, not an upgrade. The consequence
is worth stating: one shared world is bind-mounted into all three instances and
only one may host it at a time (ADR 0006), so an instance without the module
cannot export the world it may be asked to serve. Installing it on all three
removes that asymmetry.

**Topology confirmed rather than assumed.** `/home/foundry/dist/foundryN/modules`
and `/home/foundry/foundryN/foundrydata/Data/modules` are **the same directory** —
identical inodes (1329612, 1329621, 1329626) — so each instance takes one write,
not two. An earlier `find` had suggested otherwise; it had simply not followed
the mount.

**Rollback prepared before writing.** The installed 1.0.8 was snapshotted to
`/home/foundry/foundry{1,3}/module-rollbacks/freedom-blades-export-1.0.8-2026-08-27/`,
alongside the pre-existing 1.0.7 packages (both instances) and 1.0.0 (foundry1).
foundry2 had nothing to snapshot; its rollback is removal of the directory.

**What 1.0.9 actually changes over the installed 1.0.8** — established by `diff`,
not by the version number. Three files:

| File | Change |
|---|---|
| `module.json` | `"version": "1.0.8"` → `"1.0.9"`. The `compatibility` block is unchanged: `minimum 14`, `verified 14.367`, `maximum 14` |
| `scripts/bundle.js` | **The behavioural change.** The installed 1.0.8 contains **no** range logic — zero occurrences of `versionSeries`/`CORE_COMPONENTS` — and compares exact strings. 1.0.9 carries C-P3.5-Z's scoped ranges |
| `scripts/settings.js` | The reference-deployment comment corrected to state that the tuple is a reference, not a boundary |

There is **no build step** (`package.json` declares one does not exist), so the
deployed set is `module.json`, `scripts/` and `styles/` — `tests/`,
`package.json` and `README.md` are not deployed.

**Verified after the write**, on all three and on both paths of each:

- `diff -r` of the installed tree against `foundry-module/` (excluding the three
  non-deployed items): **matches the repository exactly**, on foundry1, foundry2
  and foundry3;
- `module.json` reports `"version": "1.0.9"` at **both** the `dist/` and the
  `foundrydata/Data/` path of each instance — six manifests;
- `scripts/bundle.js` contains the range logic on all three (6 occurrences each,
  against 0 before);
- **file modes are identical across all three instances** — the same digest over
  `stat`ted modes on each. `diff -r` compares content and not permissions, so
  this was checked separately rather than assumed from it. One asymmetry was
  found and corrected: the freshly created foundry2 directories lacked the setgid
  bit that foundry1 and foundry3 carry, and were normalized to `2775`. Foundry
  runs as `foundry` (PM2, PID 1114) and every file is owned `foundry:foundry`, so
  `scripts/notifications.js` at `0600` — pre-existing on foundry1 and foundry3,
  and part of N-12's mode drift — is readable by the process on all three.

**What this does not claim.** Foundry runs under `pm2-foundry.service` and the
running processes were **not restarted** — that would interrupt live sessions and
was not authorized. The **on-disk** installed version is 1.0.9 on all three; each
instance will load it at its next restart or world reload. No export, preview or
compatibility check was run, so **deployment task 4 remains outstanding** and
nothing here is evidence that 1.0.9 behaves correctly against real data.

### 5O.3 `MemoryMax=2G` (N-47) — deployed 22:43 UTC

The deployed unit is a **filled-in copy** of
`infra/systemd/freedom-worker.service.tmpl` — its `EnvironmentFile` lines point
at `/etc/freedom-blades/*.env` — so the template must **not** be copied over it.
The change is therefore surgical: the `MemoryMax` directive and the two comment
blocks that still described the ceiling as unmeasured.

Confirmed before applying: there is **no** `/etc/systemd/system/freedom-worker.service.d/`
drop-in directory, so the unit file is the single source of the property and
nothing can override it. `systemd-analyze verify` on the prepared unit returns
**rc 0 with no warnings**, and a directive-only diff (comments stripped) shows
**exactly one** changed line, `MemoryMax=1G` → `MemoryMax=2G`.

Pre-change state, for the comparison the readiness procedure requires:
`MemoryMax=1073741824`, `ActiveState=active`, `SubState=running`, `NRestarts=0`,
`ExecMainStartTimestamp=2026-08-27 12:01:00 UTC`. `/healthz` reports all eight
checks true, `environment: staging`.

**Applied**: backup to
`/etc/systemd/system/freedom-worker.service.before-n47-2g-20260827T224337Z`
(4539 bytes), then the prepared unit, then `systemctl daemon-reload` and
`systemctl restart freedom-worker`.

**Confirmed at three levels, because two of them can agree and still be wrong.**
N-18's lesson is that a zero exit code is not evidence the configuration was
accepted; the corrected procedure reads the *effective* property. This run reads
one level further, to the kernel:

| Level | Reading |
|---|---|
| Unit file on disk | `MemoryMax=2G` (line 89) |
| systemd effective property | `MemoryMax=2147483648` |
| **Kernel cgroup** — `/sys/fs/cgroup/system.slice/freedom-worker.service/memory.max` | **`2147483648`** |

The third row is the one that matters: it is the limit the kernel will actually
enforce, and it is the only reading that cannot be a systemd bookkeeping artifact.
2147483648 bytes = 2 GiB exactly.

**The restart genuinely happened**, and was not a no-op that left the old process
running with the old limit: `ExecMainStartTimestamp` moved from
`12:01:00` to `22:43:58 UTC` and `ExecMainPID` is `1009046`. The observation was
taken after a deliberate pause, not in the milliseconds after the command
returned, which is precisely the error N-18 recorded.

**`NRestarts=0` after a restart is correct, not a contradiction.** It counts
*automatic* restarts under `Restart=on-failure`; a manual `systemctl restart` does
not increment it. Zero therefore says what is wanted here: the new process came up
and has not crash-looped.

**Post-change health.** `/healthz` reports all eight checks true, including
`worker_heartbeat: true` — so the platform can see the *new* process, not merely
that systemd started something. `freedom-worker`, `freedom-web`, `caddy` and
`pm2-foundry` are all `active`. Idle memory usage immediately after the restart
was 50,536,448 bytes (~48 MiB), against the 302 MiB measured peak and the 2 GiB
guard.

**The deployed unit is byte-identical to the reviewed, prepared file** (`diff`),
so the comment corrections landed with the directive and the deployed unit no
longer describes the ceiling as unmeasured.

**One stale line remains in the deployed unit and is not corrected here.** Its
file header still reads *"its peak memory is per-job and unmeasured"* — the same
claim task 2 corrected in `infra/systemd/freedom-worker.service.tmpl`. The
surgical edit covered the ceiling block and the directive and not the header. It
is a comment with no runtime effect, and correcting it needs a `daemon-reload`
but **no restart**. Recorded rather than quietly left: the deployed unit and the
repository template disagree by one paragraph until it is applied.

### 5O.4 What this deployment does not close

Three remediations are deployed; **deployment task 4 is not done**. No real
export, preview or compatibility check has been run against 1.0.9, so nothing
here is evidence that the scoped version ranges behave correctly on real data —
only that the code implementing them is installed. It remains blocked until an
instance restarts and loads the new module.

No finding is closed by this section, and no gate decision is implied by it.

## 5P. Codex EX-11/EX-12 re-review — N-29 and N-30 raised 2026-08-28

Codex independently re-ran the submitted verification set and reviewed the
C-P3.5-AB implementation and deployment evidence. EX-11 and EX-12 were both
withheld on two findings:

- **N-29, Blocking:** the unfamiliar-record access-log fallback remains
  best-effort. Synthetic input with an IPv4 address adjacent to a word character
  survives unchanged, contrary to operational contract §5's prohibition on
  plaintext IP addresses in every log line. The unfamiliar path must fail closed
  as a whole rather than preserve arbitrary rendered input after regex-based
  discovery.
- **N-30, Important:** the P3.4 scope guard watches `adapters/`, `application/`
  and `domain/`, but not `tools/`. The behavioral change to
  `tools/portal_server.py` passed undeclared, reproducing N-27's failure class.

The real export/preview against a running process that has loaded module 1.0.9
also remains outstanding. No live service or implementation was changed by the
review. Full independent results: bot **2447 passed**; web **2452 passed, 80
skipped**; module **171 passed**; assets **4/4**; visual freeze **14/14**; clean
`git diff --check`. Remediation instructions are in the 2026-08-28 overwritten
reviewer handoff. Peter alone decides the gate; Phase 4 remains unauthorized.

## 5Q. N-29 and N-30 remediated — 2026-08-28

**Nothing in this section is deployed, and it closes no finding.** It records
repository remediation and its verification, for the two re-reviews the handoff
requests. Peter alone decides the Phase 3 gate.

### 5Q.1 N-29 — the unfamiliar access-log record now fails closed as a whole

**Reproduced first, against the tree as submitted.** `_scrub_addresses()`
anchored its candidate pattern on `\b` at both ends, so an address adjacent to a
word character was never a candidate at all. Six synthetic documentation-range
inputs (RFC 5737 / RFC 3849), and what the submitted build did with each:

```text
peer=203.0.113.7suffix   ->  peer=203.0.113.7suffix        # unchanged
203.0.113.7_tail         ->  203.0.113.7_tail              # unchanged
a203.0.113.7             ->  a203.0.113.7                  # unchanged
x2001:db8::1y            ->  x2001:db8::1y                 # unchanged
peer=203.0.113.7         ->  peer=client-<8 hex>           # the only shape it caught
[2001:db8::1]zz          ->  [client-<8 hex>]zz            # caught, because of the brackets
```

The finding is not that the pattern was wrong. It is that **a pattern is the
wrong instrument**: whatever its edges are, some rendering of some object falls
outside them, and §5's prohibition has no edges to match against.

**What the correction does.** `RedactAccessLogQueryString` now has two paths and
the second one emits nothing that came from the record.

| | Pinned uvicorn 0.32.1 access line | Every other record |
|---|---|---|
| Recognised by | format string identical to `ACCESS_LOG_FORMAT`, five-tuple, each argument of the pinned type **and within a stated bound**, no `exc_info`, no `exc_text`, no `stack_info` | anything else |
| Client | keyed per-process pseudonym (N-13, unchanged) | — |
| Query string | dropped at the first `?` (N-7, unchanged) | — |
| Request path | address literals replaced by a rule **closed over its input** | — |
| Method, protocol, status | retained, each validated against what uvicorn can produce | — |
| Result | one access line, still useful to an operator | `<uvicorn.access record withheld: <reason>>` and nothing else |
| `args`, `exc_info`, `exc_text`, `stack_info` | none present, by definition of the gate | all four cleared |

**What safe diagnostic value remains on the withheld path.** One reason, drawn
from a closed set of six literals in this repository — `unpinned-format-string`,
`unpinned-argument-shape`, `unpinned-argument-type`, `unpinned-argument-value`,
`unpinned-request-target`, `attached-exception-or-stack`. None is derived from a
value, a type name, a length or a count, so none is a channel for caller
material. The reason names which term of the pinned contract stopped holding,
which is the fact an operator or a reviewer actually needs when uvicorn's
contract moves — and it is more than the previous design gave, which was the
exception's type name only when rendering had failed.

**What it costs.** An unfamiliar record loses everything else. `uvicorn.access`
emits the pinned access line and nothing else, so in practice nothing an operator
reads day to day changes; a withheld line is itself the signal that something
moved. **This is not free and is not claimed to be:** if a future uvicorn changes
its access format, the portal's access log degrades to a stream of markers until
the pin is updated, and `test_the_pinned_uvicorn_access_contract_still_holds`
is what is meant to say so in CI before that happens in a journal.

**Two things narrowed on the retained path at the same time, for one reason.** A
branch that claims to know which argument is which has to check:

1. **every pinned field is bounded** — the method against an RFC 9110 token, the
   protocol against `[0-9](\.[0-9])?`, the status against 100–599 (and `bool`
   rejected, because `True` is an `int`), the path against printable ASCII with a
   2048-character ceiling, the client field against a 128-character ceiling. A
   record carrying anything else is withheld rather than trusted field by field.
   A consequence worth naming: **nothing on the retained path renders
   caller-supplied data**, because every retained field is already a `str` or an
   `int`. "An argument whose `__str__` raises" is no longer a case this path
   survives — it is a case this path cannot reach.
2. **the retained request path is scrubbed too.** An HTTP client chooses the
   path, so `GET /x203.0.113.7y` would otherwise have put a plaintext address in
   the access log through the branch the handoff keeps — the same finding, on the
   other branch. **This was found while writing the correction, not by the
   review.** The scrub is closed over its input: every IP literal is spelled
   entirely from hex digits, `:` and `.`, so every literal lies inside exactly
   one maximal run of those characters. A run with two or more colons may carry
   an IPv6 literal and is removed **whole**; a run with fewer cannot, so only
   IPv4 remains, and every start position and length is enumerated rather than
   trusted to one greedy scan. Two inputs show why the enumeration is not
   theoretical: `999.999.999.203.0.113.7` and `203.0.113.789` both hid a valid
   address from a single-pass reading.

**Falsification — recorded before the correction was applied.** The new tests
were written first and run against the submitted implementation:

| Run | Result |
|---|---|
| New N-29 tests vs. the **submitted** implementation | **68 failed, 73 passed** |
| … of which: an address in the request path survived | 17 |
| … a field outside the pinned bounds was trusted | 14 |
| … a fragment of an unfamiliar record survived | 11 |
| … the record was not replaced by repository-owned text | 11 |
| … an adjacent address survived an unfamiliar record | 8 |
| … attached exception, `exc_text` or stack text survived | 3 |
| … remaining (installation, rendering, falsification-of-falsification) | 4 |

**And falsified again after it, one element at a time.** Each defect was
reinstated in the corrected file, the file's suite re-run, and the file restored:

| Reinstated defect | Tests failing |
|---|---|
| the `\b`-anchored candidate pattern (N-29 itself) | **3** |
| unfamiliar records rendered and text-redacted again | **52** |
| `exc_info` / `exc_text` / `stack_info` no longer cleared | **5** |
| the retained request path no longer scrubbed | **19** |
| the per-field bounds dropped from the pinned branch | **8** |
| all restored | **238 passed** |

**Tests: 97 → 238 in this file**, 141 of them new. The new section covers every
case the handoff names: IPv4 adjacent to letters, digits, underscores and punctuation; IPv6
adjacent to text, bracketed, zone-identified, ported, uncompressed and
IPv4-mapped; addresses inside lists, sets, mappings, nested containers and a
custom `__str__`; credentials in message, argument and container forms; attached
exceptions, pre-rendered `exc_text` and stack text; malformed formatting and an
object whose `__str__` raises; proof that no fragment of arbitrary unfamiliar
input survives; proof that only the pinned format retains bounded
method/path/protocol/status; IPv4 and IPv6 same-address/different-port
correlation; and installation and pseudonym idempotency.

**Nine existing test functions — fifteen parametrised cases — were rewritten
rather than deleted**, each with its own docstring saying what it used to assert
and why that is no longer the property to hold. Three of them had asserted
behaviour the correction deliberately removes:
that a timestamp *survives* the fallback, that an attached exception's type stays
diagnosable, and that no character after the first `?` survives — the last being
a real guarantee that was simply not enough, because an address does not follow a
`?`.

### 5Q.2 N-30 — the scope guard watches `tools/`, and can now be shown to fail

**Reproduced first.** With `tools/portal_server.py` removed from the allowlist,
the guard reports it: `Unpermitted tools modification detected in working tree:
tools/portal_server.py`. That is the state N-30 found, and it passed silently
because `tools/` was not a watched prefix at all.

**What the correction does.**

1. **`tools/` is watched**, and the two entry points P3.5 genuinely changed are
   declared with their reasons: `tools/portal_server.py` (N-7 / N-13 / N-29) and
   `tools/snapshot_perf_harness.py` (N-28). `tools/breakglass_observation.py` and
   `tools/startup_refusal_probe.py` were assessed as the handoff required and are
   **not** declared: both are committed at `HEAD` and neither is modified in the
   working tree this guard reads, so declaring them would assert a change that is
   not there. No directory is allowed by prefix.
2. **The guard's decision became a function of a path.** It was a loop inside the
   test, so the only demonstration available was "the current working tree
   passes" — which shows that it ran, not that it can fail, and N-27 and N-30 are
   both cases where it ran and could not fail. `scope_violation(path)` can be
   handed a path that is not in the tree.
3. **Every production layer is now watched, not one per finding.** The guard was
   extended a layer at a time, each time after something had already passed
   through the gap. Every top-level directory in the repository is now either
   watched or named non-production, and a test fails on a directory that is in
   neither — so a new layer fails on the day it is created rather than at the
   third review to look for it.

**The widening is raised, not absorbed.** `infra/` and `foundry-module/` carry
accepted, deployed P3.5 changes (HSTS in C-P3.5-Y, module 1.0.9 and the OD-14
v1.6 ranges in C-P3.5-X/Z, `MemoryMax=2G` in C-P3.5-Z), and both are deployment
surfaces where an undeclared edit reaches production directly. Seven files are
declared there, file by file. **This is a deliberate expansion beyond the
handoff's `tools/`, and a reviewer should confirm it rather than inherit it.** It
adds no permission: every declared file is an already-reviewed change.

**Falsified four ways.**

| What was done | Result |
|---|---|
| an undeclared synthetic change written into a real `tools/` file | **caught**: `Unpermitted tools modification detected in working tree: tools/portal_kill_switch.py` |
| `tools/` removed from the watched prefixes (N-30 itself) | **4 failed** |
| the pre-2026-08-23 porcelain strip defect reinstated | **2 failed** |
| `tools/portal_server.py` left undeclared (N-30 as found) | **1 failed**, naming the file |
| all restored | **43 passed** |

The first row is the one the handoff asked for and the one the working tree
cannot give on its own: an undeclared path is rejected, and fifteen synthetic
paths across every watched layer are rejected in a test that does not read the
working tree at all.

### 5Q.3 Verification — full set, serial, database enabled

`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported. Run on the
deployed host, 2026-08-28, against the tree being submitted.

| # | Command | Result |
|---|---|---|
| 1 | `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **2447 passed**, 1 warning, 139.28 s |
| 2 | `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2625 passed, 80 skipped**, 1137 warnings, 133.89 s |
| 3 | `node --test "foundry-module/tests/*.test.mjs"` | **171 pass, 0 fail** |
| 4 | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **4/4 OK** |
| 5 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 6 | `python -m compileall -q adapters application domain tests tools`, both venvs | clean, rc 0 |
| 7 | `alembic heads` / `alembic branches` | single head **`0013`**, no branches |
| 8 | `git diff --check` | clean |

**The skip count is 80, not 1362.** Without the environment variable the web
suite reports roughly *1141 passed, 1362 skipped* in about twelve seconds and
still exits 0, having exercised almost no database behaviour at all.

The web figure moves **2452 → 2625**: 173 tests added across the two files,
141 in `test_n7_access_log_redaction.py` (97 → 238) and 32 in
`test_p3_4_static_assets.py` (11 → 43) — much of both is parametrisation, not
173 new ideas.

**Formatter, linter and type checker remain unconfigured** (E-9) and are **not**
claimed as passed.

### 5Q.4 What this section does not close

No deployment happened. The corrected `tools/portal_server.py` is **not** on the
running portal, so the deployed process still carries the submitted build and its
N-29 behaviour; reverting the repository change needs no service action. The four
outstanding operational items — loaded module 1.0.9 and the real export/preview,
the stale worker-unit header comment, the post-gate `Server` header and
TC-SEC-07 — are untouched and are listed in §5R.

No finding is closed here. No gate decision is implied. Phase 4 remains
unauthorized.

## 5R. The remaining operational evidence — not run, and why

Recorded here so the four outstanding items are in one place rather than spread
across the sections that raised them. **None was attempted**, and none is blocked
by anything in this repository.

| # | Item | Why it is not run |
|---|---|---|
| 1 | Prove the **running** Foundry process has loaded module 1.0.9 — not that the installed manifest reads 1.0.9 | Needs a restart or world reload on an instance, at a window Peter approves. Doing it otherwise interrupts a live session, which the handoff explicitly does not authorize |
| 2 | The authorized real export and preview compatibility check against 1.0.9: Actor counts, mappings, warnings and diagnostics against the prior baseline | Blocked by 1: an instance that has not loaded 1.0.9 cannot demonstrate its behaviour. No real artifact or player data would be committed |
| 3 | Correct the **stale deployed worker-unit header comment**; validate and `daemon-reload` | Touches a deployed unit file. Comment-only, so no restart is required — but it is a deployed-artifact change and is Peter's to authorize |
| 4 | Recheck the origin and edge `Server` header on a normal response and complete the final **TC-SEC-07** capture | Requires the staging gate to be removed under its existing procedure. The gate credential is not read for this task |

Items 1, 2 and 4 need a supervised window; item 3 needs authorization only.

## 5S. EX-11/EX-12 remediation re-review — N-31 raised 2026-08-28

Codex independently reviewed C-P3.5-AD without changing the tree or touching a
service. N-30's scope-guard remediation is satisfactory: `tools/` and the other
production layers are watched, declarations are file-specific, and synthetic
undeclared paths prove the guard can fail. The unfamiliar-record branch of N-29
also now has the required security shape: a record outside the exact pinned
contract is withheld whole and formatter-appended diagnostics are cleared.

The retained pinned branch still violates operational contract §5. The method
is caller-controlled; `_HTTP_METHOD` accepts the RFC-token characters `.` and
digits; and `_redact_pinned_access_line()` returns the method unchanged. The
following synthetic documentation-range reproduction passed the filter and
formatted as shown:

```text
input tuple: ("198.51.100.9:1", "203.0.113.7", "/healthz", "1.1", 200)
output: client-08c95168 - "203.0.113.7 /healthz HTTP/1.1" 200
```

The pseudonym value is process-key-dependent and is evidence only of client
redaction; the plaintext method is the defect. This is **N-31, Blocking**. The
fix must either scrub address material from every accepted method or withhold a
pinned record whose method carries it. It must preserve the exact query-string
removal, per-address client correlation, unfamiliar-record whole withholding,
bounded field validation, filter installation scope and idempotency. A fully
formatted pinned-record regression must be shown failing against C-P3.5-AD
before the correction and passing afterward. Tests should include the exact IPv4
case, IPv4 adjacent to other token characters, and token-valid hex/dot forms
that could conceal an address; do not weaken method validation to an ad hoc list
of common verbs unless the accepted Uvicorn/HTTP contract is deliberately
changed and reviewed.

Independent verification against the reviewed tree:

| Check | Result |
|---|---|
| Focused N-29/N-30 and related tests | **289 passed** |
| Bot suite, database enabled | **2447 passed**, 1 warning |
| Web suite, database enabled | **2625 passed, 80 skipped**, 1137 warnings |
| Foundry module | **171 passed** |
| Asset / visual-freeze manifests | **4/4 and 14/14 clean** |
| `compileall`, both required interpreters | clean |
| Alembic | single head `0013`, no branches |
| `git diff --check` | clean |

Formatter, linter and type checker remain unconfigured and are not claimed.
The four §5R operational items remain not run. EX-11 and EX-12 remain withheld;
no finding or gate closes on these results, and Phase 4 remains unauthorized.

## 5T. N-31 remediated — 2026-08-28

**Nothing in this section is deployed, and it closes no finding.** It records
repository remediation and its verification, for the two re-reviews the handoff
requests. Peter alone decides the Phase 3 gate.

### 5T.1 The behaviour before and after

**Reproduced first, against the tree as reviewed (C-P3.5-AD).** The reviewer's
exact tuple, and four further shapes written while establishing how wide the
defect was. Every line below is the *fully formatted* record, which is what
reaches a journal:

```text
("198.51.100.9:1", "203.0.113.7", "/healthz", "1.1", 200)
  -> client-23dbb48d - "203.0.113.7 /healthz HTTP/1.1" 200
("198.51.100.9:1", "X203.0.113.7Y", …)
  -> client-23dbb48d - "X203.0.113.7Y /healthz HTTP/1.1" 200
("198.51.100.9:1", "203.0.113.7-198.51.100.9", …)
  -> client-23dbb48d - "203.0.113.7-198.51.100.9 /healthz HTTP/1.1" 200
("198.51.100.9:1", "999.999.999.203.0.113.7", …)
  -> client-23dbb48d - "999.999.999.203.0.113.7 /healthz HTTP/1.1" 200
("198.51.100.9:1", "A.203.0.113.7", …)
  -> client-23dbb48d - "A.203.0.113.7 /healthz HTTP/1.1" 200
```

The `client-` value is the keyed per-process pseudonym and is evidence only that
the *client* field was redacted. The plaintext method is the defect, and it is
one plaintext address per line against operational contract §5, which has no
exceptions.

**After the correction, the same five inputs:**

```text
<uvicorn.access record withheld: address-bearing-method>
```

**What changed, precisely.** One check in
`RedactAccessLogQueryString._outside_the_pinned_contract`, one helper, and one
reason literal:

| | Before (C-P3.5-AD) | After |
|---|---|---|
| Method syntax | `_HTTP_METHOD`, an RFC 9110 token bounded at 32 characters | unchanged |
| Method content | not examined; returned to the formatter verbatim | a record whose method carries an IP literal is **withheld whole** |
| Reason literals | six | seven — `address-bearing-method` added |
| Everything else | — | unchanged |

### 5T.2 Why the method policy is complete over its accepted input

The claim is that no IP literal can reach the log through the method. It rests on
two facts and one reused rule.

1. **The method's accepted alphabet contains no `:`.** `_HTTP_METHOD` is
   ``[A-Za-z0-9!#$%&'*+.^_`|~-]{1,32}``. Every textual IPv6 literal contains at
   least two colons — that is what the separator means for a minimum of three
   fields, and `::` is two on its own — so **no IPv6 literal is expressible in a
   method at all**, in any form: compressed, uncompressed, bracketed,
   zone-identified or IPv4-mapped. This is asserted in
   `test_n31_no_ipv6_literal_is_expressible_in_the_method_alphabet` rather than
   argued.
2. **That leaves the IPv4 dotted quad**, whose detection in a bounded string is
   decidable by enumeration — at most nine lengths per start position, over at
   most 32 positions.
3. **The rule is not a new one.** `_scrub_addresses` is the rule N-29 accepted
   for the request path, and it already enumerates every start position and
   length rather than trusting one greedy scan. `_carries_address_material(text)`
   asks whether that rule *would change* `text`. The equivalence holds because
   neither replacement can reproduce its input: a pseudonym and
   `REDACTED_ADDRESS` both contain characters outside the address alphabet, so a
   replaced run always differs from the run that was there. **The detector
   therefore cannot drift from the scrubber**, and a reviewer has one rule to be
   convinced by rather than two.

**Checked, not only argued.**
`test_n31_detection_agrees_with_a_brute_force_reference_over_the_alphabet` puts
2,000 seeded pseudo-random token-valid methods through the filter and through an
independent brute force that offers *every* substring to `ipaddress.IPv4Address`,
and fails on a disagreement in either direction. A third of the cases embed a
real address at a random offset and a third embed a near miss
(`999.999.999.999`, `256.1.1.1`, `1.2.3`, `203.0.113`, `1.1.1.1.1`), so the check
catches over-refusal as well as disclosure — and the near misses are load-bearing:
without them the mutation in 5T.3 that matched the dotted-quad *shape* without
validating the octets agreed with the reference on every case generated.
`test_n31_every_offset_of_an_address_in_a_bounded_method_is_found` is exhaustive
over position for the 32-character bound.

**Withheld rather than scrubbed, and why.** The handoff offered both and preferred
withholding where scrubbing would leave ambiguous partial preservation. It would
here: `X203.0.113.7Y` becomes `X<pseudonym>Y`, keeping caller-chosen characters
around the removed span in a field that has no operational meaning left once it
carries an address. The request path is scrubbed instead of withheld because a
path with an address removed is still a route an operator can read; a method is
not. `test_n31_an_address_bearing_method_withholds_the_whole_record` pins the
choice, and mutation M3 below shows the tests distinguish the two options rather
than merely asserting the address is gone.

**What the rule does not claim.** It finds IP *literals*, which is what §5's
prohibition of plaintext addresses means and what N-29's accepted path already
covers. A method spelling an address in another encoding — the decimal form
`ipaddress.ip_address()` also accepts, say — is not a plaintext address and is
not detected. The boundary is stated rather than quietly widened, and it is the
same boundary the accepted request-path rule has.

**No method validation was weakened.** `_HTTP_METHOD` is unchanged; extension
methods remain valid. `VERSION-CONTROL`, `M-SEARCH`, `MKCALENDAR`, `PROPFIND`,
`QUERY`, `X-FREEDOM-BLADES`, `REPORT.V2`, `DEAD.BEEF`, `1.2.3`, `203.0.113` and
`999.999.999.999` all still reach the log unchanged — asserted in
`test_n31_an_ordinary_or_extension_method_still_reaches_the_log`.

### 5T.3 Falsification

**Written first, and run against C-P3.5-AD before the correction was applied.**

| Run | Result |
|---|---|
| The new N-31 tests vs. the **reviewed** implementation | **68 failed, 342 passed** |
| … of which: an address-bearing method reached the formatted line | 21 |
| … the record was not withheld | 21 |
| … withholding was not idempotent (nothing was withheld to be idempotent about) | 21 |
| … the reviewer's exact tuple was not withheld | 1 |
| … the seventh reason literal did not exist | 1 |
| … detection disagreed with the brute-force reference | 1 |
| … an address at some offset in a bounded method was missed | 1 |
| … the real-handler end-to-end case disclosed | 1 |

**No pre-existing test failed in that run.** The 342 passing include every N-29
and N-13 assertion, which is the direct evidence that the regression isolates
N-31 rather than re-testing what was already accepted.

**And falsified again after it, one element at a time.** Each defect was
reinstated in the corrected file, the file's suite re-run, and the file restored:

| Reinstated defect | Tests failing |
|---|---|
| **M1** — the method passed through unchanged again (N-31 itself) | **67** |
| **M2** — detection by one greedy unvalidated `_IPV4_LITERAL.search()` | **2** |
| **M3** — the method *scrubbed* instead of the record withheld | **46** |
| all restored | **410 passed** |

M1 is the mutation the handoff asks for: it leaves the reason literal and the
helper in place and removes only the check, so the 67 failures are exactly the
assertions that depend on the method being examined. M2 fails on
`999.999.999.999` — over-refusal caught by the operational-method case and by the
brute-force reference. M3 fails 46 because the tests pin the *choice* between the
handoff's two options, not merely the absence of the address.

**The scope guard was falsified against this edit too.** With
`tools/portal_server.py` removed from `PERMITTED_P3_5_PRODUCTION`, the guard
reports it — `Unpermitted tools modification detected in working tree:
tools/portal_server.py`, 2 failed — which is the direct evidence that the N-30
remediation is watching *this* change and not merely present. Restored: 43
passed. No new production file was opened: the only production file this
remediation touches is the one already declared, and its declaration comment now
names N-31 as a distinct change rather than letting the existing entry cover it
silently.

**Tests: 238 → 410 in this file**, 172 of them new, all in the N-31 section. No
existing test was modified, relaxed or deleted — the N-29 whole-withholding tests
are byte-for-byte as they were, and `test_n31_the_unfamiliar_record_contract_is_untouched`
restates their property inside the new section so a future edit to the method
rule that weakened the fallback would fail in both places.

### 5T.4 Verification — full set, serial, database enabled

`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported. Run on the
deployed host, 2026-08-28, against the tree being submitted.

| # | Command | Result |
|---|---|---|
| 1 | `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **2447 passed**, 1 warning, 141.57 s |
| 2 | `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2797 passed, 80 skipped**, 1137 warnings, 134.59 s |
| 3 | `node --test "foundry-module/tests/*.test.mjs"` | **171 pass, 0 fail** |
| 4 | Focused: the access-log and scope-guard files | **453 passed** (410 + 43) |
| 5 | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **4/4 OK** |
| 6 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 7 | `python -m compileall -q adapters application domain tests tools`, both venvs | clean, rc 0 |
| 8 | `alembic heads` / `alembic branches` | single head **`0013`**, no branches |
| 9 | `git diff --check` | clean |

**The skip count is 80, not 1362**, and the two skip reasons `-rs` prints are the
same two as before: 54 permitted cells in `test_p3_2_matrix.py` and 26 in
`test_p3_3_matrix.py`, each asserted by the per-route success cases instead.

The web figure moves **2625 → 2797**: 172 tests added, all of them in
`test_n7_access_log_redaction.py` (238 → 410). Much of that is parametrisation —
21 address-bearing methods and 21 operational methods across several
properties — not 172 new ideas.

**Formatter, linter and type checker remain unconfigured** (E-9) and are **not**
claimed as passed.

### 5T.5 What this section does not close

No deployment happened. The corrected `tools/portal_server.py` is **not** on the
running portal, so the deployed process still carries the submitted build and
both its N-29 and its N-31 behaviour; reverting the repository change needs no
service action. The four outstanding operational items in §5R are untouched and
were not attempted under this handoff.

No finding is closed here. No gate decision is implied. EX-11 and EX-12 are
requested again as distinct passes. Phase 4 remains unauthorized.

## 5U. N-31 re-review and N-32 test-evidence finding — 2026-08-28

The N-31 production correction is satisfactory. The method detector reuses the
accepted bounded address scrubber; IPv6 syntax cannot enter the allowed method
alphabet; the IPv4 path enumerates start positions and candidate lengths; and an
address-bearing method withholds the whole record. Ordinary and extension
methods, query removal, client correlation, unfamiliar-record withholding,
field bounds, idempotency and the N-30 scope guard remain intact. No further
production-code finding was identified.

The evidence rerun found **N-32, Important**, in two pre-existing test assertions.
The full database-enabled web suite first passed **2797 with 80 skips**. A later
fresh-process run of the exact access-log and scope-guard files then reported:

```text
2 failed, 451 passed
client: 203.0.113.999:54321
pseudonym: client-unknown-59990025
```

The failures are in
`test_an_unfamiliar_client_value_fails_safe_without_leaking_its_contents` and
`test_an_unfamiliar_client_value_does_not_reach_the_formatted_line`. Both split
the source on punctuation and assert that every fragment of length three or
greater is absent from the eight hexadecimal digest. Here the source fragment
`999` appears by chance inside `59990025`. A keyed digest is allowed to have that
hex substring; it did not preserve the source fragment, and the output contains
neither the complete client field nor a dotted plaintext address. Because the
pseudonym key is freshly generated per process, the assertion is probabilistic.

This finding does **not** reopen N-31 or identify a production disclosure. The
required correction is test-only:

- assert the exact bounded pseudonym form;
- assert absence of the complete original client value and complete plaintext
  IP literal in the fully formatted line;
- avoid absence claims about arbitrary short fragments inside a digest;
- reproduce the defect deterministically by fixing or monkeypatching the digest
  to contain `999`; and
- mutation-test the replacement assertion by returning the raw client/address,
  proving a real disclosure still fails.

Independent checks run against the reviewed tree:

| Check | Result |
|---|---|
| Bot suite, database enabled | **2447 passed**, 1 warning |
| Web suite, database enabled | **2797 passed, 80 skipped**, 1137 warnings |
| Foundry module | **171 passed** |
| Initial focused set including related checks | **461 passed** |
| Exact access-log + scope-guard rerun in a fresh process | **451 passed, 2 failed** — N-32 |
| Asset / visual-freeze manifests | **4/4 and 14/14 clean** |
| `compileall`, both interpreters | clean |
| Alembic | single head `0013`, no branches |
| `git diff --check` | clean |

Formatter, linter and type checker remain unconfigured and are not claimed. No
file or service was changed by the review. The four §5R operational items remain
outstanding. EX-11 and EX-12 remain withheld pending N-32 correction and renewed
verification; Peter alone decides the gate and Phase 4 remains unauthorized.

## 5V. N-32 remediated — 2026-08-28

**Test-only.** No production pseudonymization, access-log policy, route,
configuration or deployment artifact changed, no service was deployed or
restarted, and no production injection seam was added. N-31 remains satisfactory
and is not reopened; N-29 and N-30 are not reopened. Exactly one file changed:
`tests/web/test_n7_access_log_redaction.py`.

### 5V.1 What was wrong, and what it was not

`test_an_unfamiliar_client_value_fails_safe_without_leaking_its_contents` and
`test_an_unfamiliar_client_value_does_not_reach_the_formatted_line` split the
source client value on `.`, `:` and `/` and required every fragment of three
characters or more to be absent from the eight hexadecimal characters of the
keyed pseudonym.

`_CLIENT_PSEUDONYM_KEY` is `secrets.token_bytes(16)`, generated per process, so
the digest is a fresh random value on every run — and a random hex string may
contain any short hex substring. The rerun in §5U drew one that did:

```text
source:     203.0.113.999:54321
pseudonym:  client-unknown-59990025
collision:  999
result:     2 failed, 451 passed
```

**That is not a disclosure.** Neither the complete client field nor a dotted IP
literal survived; the source fragment `999` was not preserved, it recurred. The
tests had mistaken coincidental substring equality for source preservation, and
in doing so made the security evidence depend on a random key.

### 5V.2 The correction

Each unfamiliar client value is now a `_UnfamiliarClient` record carrying the
**complete** representations that must not survive it, and why it reaches the
fail-safe path at all:

| Client field | Forbidden, completely | Why it fails safe |
|---|---|---|
| `""` | — | uvicorn's own no-client case: `get_client_addr` returns `""` for a Unix socket or a lost peer |
| `/run/freedom-portal.sock` | the whole value | a socket path, not an address at all |
| `203.0.113.7:99999` | the whole value, `203.0.113.7` | a port outside the range |
| `203.0.113.7:not-a-port` | the whole value, `203.0.113.7` | a port that is not numeric |
| `203.0.113.999:54321` | the whole value, `203.0.113.999` | **N-32's own case**: no octet may exceed 255 |
| `host.example.invalid:54321` | the whole value, `host.example.invalid` | a hostname, which `--proxy-headers` can put here |
| `SYNTHETICcode…:54321` | the whole value, the credential | a credential-shaped value standing in for anything unexpected |

Against each, the two tests now assert:

1. the pseudonym is exactly `client-unknown-` plus eight lowercase hexadecimal
   characters;
2. no forbidden complete value occurs in the pseudonym;
3. no forbidden complete value occurs in the fully formatted line; and
4. the line is still an access line — the pseudonym in the client position, and
   `"GET /v1/characters HTTP/1.1" 200` intact — so a correction that emptied the
   record could not pass.

Property 3 of the handoff, every complete plaintext IP literal, is asserted
twice: by hand in the table, and mechanically by
`test_n32_every_complete_ipv4_literal_in_the_source_is_absent`, which offers
every substring of every length to `ipaddress.IPv4Address` with the dotted-quad
shape required explicitly — the same independent reference the N-31 tests use.
The mechanical check exists so that a value added to the table later cannot
silently skip the address check.

**Why this is deterministic where the old rule was not**, asserted rather than
assumed. A pseudonym is a fixed prefix plus hexadecimal characters, so the set of
characters one can contain is fixed and small.
`test_n32_no_forbidden_value_can_occur_inside_a_pseudonym` requires every
forbidden value to carry at least one character outside that set. Every one does
— a `.`, a `/`, a `-` or an uppercase letter. The old rule forbade fragments
drawn from `[0-9]` alone, every one of which is *inside* the set, which is
exactly how `999` got in.

The three parsing, prefix and correlation properties the module already held are
untouched: nothing in `tools/portal_server.py` was edited, and the digest length,
key generation, prefixes, client parsing, method handling, request-path handling
and production logging are all as C-P3.5-AF left them.

### 5V.3 The deterministic falsification

The regression does not wait for a lucky key. `_digest` is monkeypatched at its
boundary, from the test module, to return the eight characters the rerun
observed. Everything else — reading the port, failing to parse the host,
choosing the `client-unknown-` prefix, the filter, the formatter — runs as it
ships, and `monkeypatch` restores `_digest` at the end of each test.

| Test | Asserts | Result |
|---|---|---|
| `test_n32_falsification_the_old_fragment_rule_fails_on_a_safe_pseudonym` | the pinned digest yields exactly `client-unknown-59990025`, and the old rule raises `AssertionError` on it | **passes** — the defect reproduced deterministically |
| `test_n32_falsification_the_old_rule_fails_on_the_formatted_line_too` | the same, on the fully formatted line, which is the rerun's second failure | **passes** |
| `test_n32_the_corrected_rule_passes_on_that_same_pseudonym` | the corrected assertions hold for the exact value the old ones rejected | **passes** |

The pinned run, in full:

```text
client-unknown-59990025 - "GET /v1/characters HTTP/1.1" 200
```

Neither `203.0.113.999:54321` nor `203.0.113.999` appears in it.

### 5V.4 The mutation — a real disclosure still fails

`test_n32_a_raw_pass_through_still_fails_the_corrected_rule` replaces
`_pseudonymise_client` with three mutations and requires the corrected
assertions to raise:

| Mutation | Emits | Caught by |
|---|---|---|
| the raw client field | `203.0.113.999:54321` | the confidentiality assertion |
| the raw host address | `203.0.113.999` | the confidentiality assertion |
| the raw host address **wearing the pseudonym's prefix** | `client-unknown-203.0.113.999` | the confidentiality assertion |

The third is the one worth reading: it keeps the label, so a corrected rule that
had checked only the *form* would have passed it. All three fail on the
confidentiality assertion itself, not merely on the form check — confirmed
directly, with the failure message naming the complete value that survived.

The assertions the mutation is shown to fail are the same functions the two
rewritten tests call, held in one place (`_assert_the_pseudonym_is_safe`,
`_assert_the_access_line_is_safe`, `_assert_no_forbidden_value_survives`), so
what the mutation falsifies cannot drift from what the suite runs.

### 5V.5 How probabilistic the old rule actually was

A one-off measurement, run against this tree and recorded here as evidence
rather than added to the suite — nothing randomized was introduced into the
tests. Over **20,000 random keys × 7 client cases = 140,000 case-runs**, each
case exercised against both the pseudonym and the formatted line:

| Rule | Case-runs failed |
|---|---|
| the old fragment rule | **199 of 140,000 (0.142%)** |
| the corrected rule | **0** |

At 0.142% per case, a process running all seven cases fails the pair roughly
once in a hundred starts — which is why the full suite passed at §5U and the
focused rerun in a fresh process did not.

### 5V.6 Verification

The focused pair, three times, each as a **separate Python process**, to prove
the result no longer depends on the process-local key:

```sh
/opt/discord-bots/venv-web/bin/python -m pytest -q \
  tests/web/test_n7_access_log_redaction.py \
  tests/web/test_p3_4_static_assets.py
```

| Run | Result |
|---|---|
| 1 | **480 passed**, 0.60 s |
| 2 | **480 passed**, 0.69 s |
| 3 | **480 passed**, 0.61 s |

The module goes from **410 to 437 collected tests**; the pair from 453 to 480.
The pre-correction tree failed **2 of 453** in one such process.

Then serially, with PostgreSQL enabled
(`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`):

| # | Check | Result |
|---|---|---|
| 1 | `/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py` | **2447 passed**, 1 warning, 144.36 s |
| 2 | `/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web` | **2824 passed, 80 skipped**, 1137 warnings, 143.56 s |
| 3 | `node --test "foundry-module/tests/"*.test.mjs` | **171 pass, 0 fail** |
| 4 | `sha256sum -c adapters/web/static/asset-integrity.sha256` | **4/4 OK** |
| 5 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 6 | `compileall`, both interpreters | clean, rc 0 |
| 7 | `alembic heads` / `alembic branches` | single head **`0013`**, no branches |
| 8 | `git diff --check` | clean |

The web figure moves **2797 → 2824**, which is the 27 tests this correction
added. The skip count is still **80**, and `-rs` prints both reasons: 54
permitted cells in `test_p3_2_matrix.py` and 26 in `test_p3_3_matrix.py`, each
asserted by the per-route success cases.

**Not run, and recorded as unavailable rather than passed:** formatter, linter
and type checker remain unconfigured in this repository (standing condition
E-9). This correction did not introduce one as a drive-by change.

### 5V.7 What this does not claim

The four §5R operational items remain outstanding and were **not** executed
under this correction: proving a running Foundry process loaded module 1.0.9;
the authorized real export/preview compatibility check; the stale deployed
worker-unit header comment; and the final origin/edge `Server` header with
TC-SEC-07 after the staging gate is removed. Three remediations remain
undeployed (§7 of the submission). EX-11 and EX-12 are requested again. No
finding and no gate closes on implementation or green tests alone, and Phase 4
remains unauthorized.

## 5N. N-28 — the raise reached the policy and the unit, not the tool that measures against it

**Class: Important — a fifth instance of this package's own §5 pattern, and
the first one found *after* the pattern was written down.** Raised 2026-08-27.

C-P3.5-Z raised N-47 from 1 GiB to 2 GiB. The raise reached
`docs/contracts/phase-3-numeric-policy-register.md` and it reached
`infra/systemd/freedom-worker.service.tmpl`, which is where `MemoryMax` actually
takes effect. It did **not** reach `tools/snapshot_perf_harness.py`, the tool
whose entire job is to report a measured peak *against N-47*:

```
N47_MEMORY_MAX_BYTES = 1024 * 1024 * 1024        # the harness
MemoryMax=2G                                     # the unit that enforces it
```

**What made it silent is the test that was supposed to prevent it.**
`test_the_restated_constants_match_their_sources` pins the harness constants so
they "cannot drift apart" — and pins two of the three against a real source: the
throughput limit against `tests/benchmark_snapshot_500`, the soft warning against
the shipped worker constant. N-47 alone was pinned to a **literal**:

```python
assert N47_MEMORY_MAX_BYTES == 1024 * 1024 * 1024
```

A literal cannot detect drift from anything. It asserts that the harness still
agrees with *itself*, which it always will. So the suite stayed green while the
measuring instrument disagreed with the policy it measured against.

**Consequence, had it not been found.** The harness prints `fraction of N-47` and
warns above 75%. Against the stale 1 GiB divisor it overstates every future
reading by 2x and warns at 768 MiB — a real 1.1 GiB peak, comfortably inside the
accepted 2 GiB, would have been reported as **over the ceiling**. It would have
failed in the safe direction, which is why it could have survived a long time:
nobody investigates a bound that looks stricter than it is until a run trips it.

**It changes no measurement in this package.** TC-PERF-01's real figure is
**302.4 MiB**, inside both the old and the new bound, and the reported fraction
was against the value in force at the time.

**Remediated 2026-08-27.** The harness now carries `2 * 1024 * 1024 * 1024` with
the raise and its reason in the comment, and the two prose statements of the
ceiling follow it. The literal assertion is replaced by
`test_the_memory_ceiling_matches_the_shipped_worker_unit`, which parses
`MemoryMax=` out of the unit template and converts the suffix, so the unit file
is the single source and the next raise is either a one-place change or a failing
test.

**Falsified, not merely observed to pass.** With the unit set to `MemoryMax=1G`
the new test fails at its assertion; restored to `2G` it passes, and the file's
**14 tests pass**.

## 5M. N-27 — the scope guard does not watch `domain/`

**Class: Important — a gap in a control, found by the control working elsewhere.**
Raised 2026-08-27.

`tests/web/test_p3_4_static_assets.py::test_no_unrelated_production_files_modified`
is a scope guard from P3.4: it reads `git status` and fails when a production
file is modified without being declared. Its own convention is strict and good —
*"one entry per finding … so the guard names why each file was opened rather
than growing a general backend exemption."*

**It caught today's change to `application/worker/runtime.py`**, which is exactly
what it is for, and the change was declared with its reason.

**It did not catch today's change to `domain/foundry.py`** — the version
comparison rewritten from exact equality to scoped ranges (C-P3.5-Z). The guard
tests three prefixes:

```python
if path.startswith("adapters/web/templates/") …
if path.startswith("adapters/") …
if path.startswith("application/") …
```

**`domain/` is absent.** It is production code, and it is the layer holding the
rules — the place where an undeclared change matters most, not least. A
drive-by edit there is precisely what this guard exists to surface, and today one
passed it unnoticed.

**Remediated 2026-08-27**, authorized by Peter Duscha (*"Please do. Full
documentation for review included."*).

`domain/` is now a fourth watched prefix, and `domain/foundry.py` is declared in
the permitted set against **C-P3.5-Z** — using the same self-documenting
mechanism the guard already required of every other entry, so the reason a file
was opened travels with the permission.

**Falsified rather than assumed.** An undeclared change was made to a `domain/`
file and the guard observed failing:

```text
Failed: Unpermitted domain modification detected in working tree: domain/__init__.py
```

The change was reverted and the guard passes with only the declared modification
outstanding. **A guard that has never fired is a guard nobody has tested**, and
this one had never been able to fire on this layer at all.

### Why this one is worth a reviewer's attention

**The gap existed for the whole of P3.4 and P3.5 and was invisible by
construction.** A scope guard that does not watch a layer cannot report that it
is not watching it — it simply passes, which reads exactly like the layer being
clean. It surfaced only because the *same* guard fired correctly on
`application/worker/runtime.py` in the same session, which prompted the question
of what else it covered.

**Controls that fail silently are worse than absent ones**, because the passing
result is taken as evidence. That is the same shape as **N-22** (a contract
requiring HSTS, with no configuration and nothing checking), **N-45** (a
documented soft warning that was never emitted) and **F6** before them. Four
instances in this package of *a control described somewhere and implemented
nowhere*, each found by looking rather than by testing.

**Worth a reviewer asking:** how many others are there? Every one of the four was
found by accident, none by a check designed to find them.

## 5L. The real-folder run — D-m's n = 1, and the finding it produced

**2026-08-27, 11:37Z → 11:49Z.** Grant: SG-2 and **D-l**. The Operations Owner
exported from Foundry, drove the portal and every privileged action; Claude
submitted and measured. **Real Actor data, as a supervised operational input.**

**This closes RR-06** — the real-folder apply the threat model records as never
having been measured — and it was only possible after the version pin moved
(**N-25**, change-log **C-P3.5-X**).

### Transport (SP-28, route B) and integrity

| | |
|---|---|
| Module | **1.0.8**, installed on foundry1 and foundry3, 1.0.7 snapshotted to `module-rollbacks/` first |
| Folder | `/actors/Characters (active)`, stable ID `smob5eya6XVBAuIb`, **32 Actors** |
| Bytes | **16,374,947** — against Rehearsal B's 16,287,185, **+0.5% in 18 days** of real sheet growth |
| Checksum | The module displayed `673c753f9866…`; the **server computed the same independently**. The bytes are byte-for-byte what Foundry produced |
| Exporter recorded | `freedom-blades-export 1.0.8` — the new version reaches the provenance record |
| Canonical encoding | **True** |

**No temporary proxy route was opened**: route B used the module's download
fallback and a host-local POST to the loopback endpoint.

### The version bump, validated rather than argued

C-P3.5-X's risk assessment named a residual the parser cannot catch: a
**schema-valid semantic change**. This run is the evidence.

| | Rehearsal B, Foundry 14.365 | Today, Foundry 14.367 |
|---|---|---|
| Preview duration | 9,566 ms | **9,854 ms** |
| Throughput | 587 ms/MB | **602 ms/MB** |
| Actors | 32 | **32** |
| Warnings | — | **none** |

**Within 2.5% of the Phase 2 baseline**, with the same Actor count, the same
folder shape and a clean reconciliation summary (32 unmapped, 32 would-create, 0
would-update, 0 blocked, 0 absent). **14.367's export behaves like 14.365's on
this world**, which is what the pin change was resting on and no longer is.

### The measurements

| Measure | Real | Accepted bound |
|---|---|---|
| Preview | 9,854 ms = **602 ms/MB** | ≤ 1200 ms/MB ✅ |
| Apply | 19,927 ms = **1,217 ms/MB** | < 300 s cap, and under N-45's 30 s soft warning ✅ |
| Worker peak | **302.4 MiB** (29.5% of N-47) | ≤ 1 GiB ✅ |
| `/healthz` during both | n=263, median 52.5 ms, **p95 61.2 ms**, max 145.7 ms, **zero non-200** | p95 ≤ 500 ms, max ≤ 2000 ms ✅ |

Queue waits 77 ms and 752 ms. **One attempt each, one durable effect**:
`characters` **32**, `external_actor_mappings` **32**, `snapshot_imports` **1**,
audit 203 → **245**. The apply created exactly what the preview predicted.

**The worker was restarted before the run** so its `VmHWM` was a fresh 67.9 MiB
rather than the 482.3 MiB carried over from the previous night's synthetic job.
Without that the real peak could not have been attributed at all.

### N-26 — real Actor data costs about twice the memory of the synthetic fixture, and the extrapolation reaches N-47

**Class: Important — a numeric-policy question raised by measurement, not a
defect.**

| Corpus | Bytes | Peak | Job memory above baseline | Ratio to input |
|---|---|---|---|---|
| Synthetic `folder-32` | 16,287,681 | 184.5 MiB | ~116 MiB | **~7.5×** |
| **Real `Characters (active)`** | 16,374,947 | **302.4 MiB** | ~234 MiB | **~15×** |

**Near-identical byte counts, 64% more peak memory.** The cause is in the fixture
generator and was documented there before this run: its filler prose is
**lexically repetitive**, so CPython interns far fewer distinct string objects
than real character sheets produce. The fixture is structurally realistic —
hundreds of item documents per Actor — and materially cheaper per byte.

**Why it matters.** Extrapolating the *real* ratio to N-20's 64 MiB ceiling gives
roughly **1.0 GiB — at or just over N-47's 1 GiB guard**. The synthetic worst case
measured **482 MiB** and suggested comfortable headroom; **it understated the real
cost by half.**

**Stated honestly:** this is one real data point extrapolated four-fold, and peak
memory need not scale linearly — interning, allocator behaviour and GC timing all
cut both ways. **It is not a demonstration that N-47 is too low.** It is a
demonstration that **the synthetic measurement cannot be used to argue N-47 is
high enough**, which is what it would otherwise have been used for.

**A second extrapolation, for completeness:** a real preview at the N-20 ceiling
would take roughly 39 s, exceeding N-45's **30 s soft warning** — reportable
rather than a failure, and worth knowing before it appears in a journal.

**Not decided here.** Whether N-47 needs raising, whether N-20's ceiling should
fall, or whether the answer is simply that no such folder will ever exist, is a
numeric-policy question for the Acceptance Authority through delivery-plan §7
change control, with the Security Reviewer's view. **Raised for Codex with the
extrapolation shown so it can be challenged.**

### N-26 strengthened by a second real sample, and sharpened by the operator

**The inactive folder, 2026-08-27 12:01Z–12:05Z.** 34 Actors, 9,586,078 bytes —
**282 KB per Actor against the active folder's 512 KB**, so retired characters
are a genuinely different corpus rather than a near-duplicate.

| Corpus | Bytes | Job memory above baseline | Ratio | Preview | Apply |
|---|---|---|---|---|---|
| Synthetic `folder-32` | 16,287,681 | ~116 MiB | **~7.5×** | 192 ms/MB | 384 ms/MB |
| Real active (32) | 16,374,947 | ~234 MiB | **~15×** | 602 ms/MB | 1,217 ms/MB |
| Real inactive (34) | 9,586,078 | ~124 MiB | **~12.9×** | 559 ms/MB | 1,138 ms/MB |

**The ratio is stable in the 13–15× band across two real corpora of different
size and different per-Actor profile, and both are roughly double the synthetic
fixture's.** One extrapolated point has become two consistent ones.

Throughput is consistent to within 8% across the two, which is the more
reassuring half of the result.

### The Operations Owner's observation, which sharpens the extrapolation

> *"Time has more to do with the size of the characters. Seiri for example has
> hundreds of items and 3.4 MB in her character sheet alone."*

**One Actor is 3.4 MB — 21% of the entire active folder.** The 512 KB mean hides
a heavily skewed distribution, and three consequences follow:

1. **It explains the memory ratio.** Real cost is driven by *hundreds of distinct
   item documents per character*, each with its own strings. The synthetic
   fixture had comparable item counts but lexically repetitive text, so CPython
   interned what real data cannot.
2. **It reframes the N-20 ceiling.** 64 MiB is not "130 average characters" — it
   is roughly **19 Seiri-sized ones**. That is a far more reachable number than
   the mean suggests.
3. **It names the real growth vector.** The plan anticipates "the folder will
   grow"; this says growth is at least as much *characters accumulating items*
   as *more characters*. The active folder already grew 0.5% in the 18 days
   between Rehearsal B and this run.

**What the data still cannot separate:** whether peak memory tracks total bytes
or spikes on the largest single Actor. Both corpora are consistent with either.
Distinguishing them needs a deliberately skewed fixture — one Actor at several
megabytes against many small ones — which the current generator does not produce
and which is worth building **before** N-47 is argued either way.

### `absent_from_snapshot` — the mandatory scenario, observed on real data

The inactive-folder preview raised **`absent_from_snapshot` × 32**: the 32 active
characters already in the database are not in this snapshot's folder, and the
operator saw the warning framed in red.

**Applying created 34 and touched none of the 32.** `characters` 32 → **66**,
`external_actor_mappings` 32 → **66**, `snapshot_imports` 1 → **2**.

The code says why, and the operator's message says the same thing:

> *"A warning, never an instruction. The Actor may have been moved to another
> folder, or the export may simply be older than the character."*
> *"Nothing is deleted, deactivated or unmapped; a separate Council correction is
> required to change that state."*

**This is the design decision that matters most in the whole run.** A
reconciliation that read "absent from this folder" as "delete" would have
destroyed 32 live characters the moment somebody imported a different folder —
an entirely ordinary thing to do, done here by accident of sequencing. The
severity is `WARNING`, not `BLOCKED`, and `BLOCKED` is the class where "applying
commits nothing".

**Recorded as a live observation of the mandatory scenario for absent/renamed
Actor handling** (implementation plan §13.2), on real data, with the operator
seeing the warning and the system declining to act on it.

**What would settle it:** a real corpus at or near the ceiling. The community has
32 active and 34 inactive Actors, so **no such corpus exists today** — the
extrapolation cannot currently be replaced by a measurement, and that limitation
belongs in the submission.

### Teardown — D-l discharged in full, 2026-08-27 13:44Z

| Item | State |
|---|---|
| Staging import tables | `characters`, `external_actor_mappings`, `snapshot_imports`, `foundry_snapshots`, `reconciliation_jobs` all **0** |
| Stored artifacts | **shredded**, store empty |
| The Operations Owner's uploads | **shredded**, directory empty |
| Ephemeral submit credential | **shredded**; it existed only for this run |
| Admissions | generation 1 (`perf-synthetic`) and generation 2 (`real-folder`) both **closed** |
| Endpoint | `sp28-real` **stopped** |
| Services | web, worker and bot **active**; `/healthz` ok with no failing check |
| `audit_events` | **288, retained deliberately** — append-only history of what was imported and by whom, carrying no character content |

**No real Actor name, payload or warning text appears anywhere in this document**,
which is the condition D-l attaches to the allowance. The one character named in
this evidence is named by the Operations Owner in his own observation about sheet
size, and carries no game data.

**A teardown-order mistake, repeated and therefore worth naming twice.** The
import tables were truncated **before** the runbook's acceptance-event query was
run — exactly the sequencing error recorded as **N-24** on 2026-08-26, made again
a day later by the same author. The query joins `foundry_snapshots`, so after a
truncate it resolves nothing; the append-only events survive and answer the
question directly. **N-24's remediation should therefore change the teardown
procedure, not only the runbook**, because a note in a runbook has now failed to
prevent the same error twice.

## 5K. N-25 — the Foundry upgrade blocks the real-folder run, and the pin did its job

**Class: Important — a blocker for named gate evidence, and simultaneously a
passing observation of a mandatory scenario.** Raised 2026-08-27 at the first
attempt to export the real folder.

### What happened

The Operations Owner upgraded Foundry between sessions. The module refused to
export:

```text
Freedom Blades [unsupported_deployment]: This deployment is not the one the
Freedom Blades platform is configured for: Foundry 14.367 (expected 14.365).
Nothing was exported. A Foundry or system upgrade deliberately stops submission
until the platform's supported version is updated.
```

**Nothing was exported, and nothing reached the platform.**

### This is the control working, and it is evidence

Implementation plan §13.2 lists **"unsupported Foundry version"** among the
mandatory scenarios, and `.agents/AGENTS.md` requires that the connector
"negotiate or validate supported versions", treating the recorded baseline as
"an observed deployment baseline, not an eternal compatibility promise".

**That scenario has now been observed live, on a real upgrade, rather than
against a fixture.** The refusal is the module's own deliberate check — not
Foundry's `module.json` compatibility warning — it names both versions, states
that nothing was exported, and says why. An operator reading it knows exactly
what happened and what to do.

**Recorded as a pass for the mandatory scenario at the strongest available
evidence level: a real deployment, upgraded by its owner, refused in production
use.**

### And it blocks the run it was found by

`SupportedDeployment.mismatches` compares **exact strings** across world id, core
version, system id and system version (`domain/foundry.py:168-192`). `14.367` is
not `14.365`, so export stops.

**D-m's real n = 1 apply cannot proceed until the pin moves.** TC-PERF-01's real
32-Actor half and TC-PERF-02's real-folder apply — the measurement RR-06 records
as never taken — stay owed.

### What moving the pin would touch

| Location | What |
|---|---|
| `foundry-module/scripts/settings.js:69` | `coreVersion: "14.365"` — the module's own check, the one that fired |
| `foundry-module/module.json:8` | `"verified": "14.365"` |
| `domain/foundry.py:202` | `OBSERVED_DEPLOYMENT.core_version` — the server's default |
| `foundry-module/tests/fixtures.mjs`, and five Python test modules | fixture expectations |
| `.agents/AGENTS.md`, plan and contracts | the recorded observed baseline |

Plus a **module version bump and re-install** on the Foundry host, since the
deployed module is 1.0.7 and the check lives in it.

### The risk of moving it, assessed rather than assumed

**Bounded.** The pin gates whether an export is *attempted*; it does not replace
validation. The server's parser still checks schema version, canonical encoding,
exporter identity, folder graph, Actor identity uniqueness, item structure and
every N-20 limit. **A genuine schema change in 14.367 would surface as a parse
refusal, not as silent corruption.**

**But the pin exists precisely so that nobody assumes a patch release is
harmless**, and changing an accepted compatibility baseline to unblock a
measurement would be changing it for the wrong reason.

### Recorded for when the run does happen

From the module dialog before the refusal:

| | |
|---|---|
| `Characters (active)` stable ID | `smob5eya6XVBAuIb` |
| `Characters (active)` Actor count | **32** — matching Rehearsal B exactly |
| **Inactive folder Actor count** | **34** |

**34 exceeds 32, so under D-l the inactive folder is submitted as well** — the
Data Owner's allowance makes it a free second real data point, closer to the N-20
bound. That condition is now resolved and needs no further decision.

### Disposition

**Decided 2026-08-27 by Peter Duscha: *"Fully documented update and review
after."*** The pin was moved to `14.367` as a controlled change, recorded in full
as change-log **C-P3.5-X**, with **independent review made a condition of the
authorization**.

**What the change did and did not do:**

- **Moved:** the server's `OBSERVED_DEPLOYMENT`, the module's own check
  (`settings.js`, the one that fired), `module.json`'s `verified` field, the
  module version **1.0.7 → 1.0.8**, every test fixture carrying the version, and
  the recorded baseline in AGENTS.md, the implementation plan, topology and the
  submission operations document.
- **Deliberately not moved:** three provenance comments stating the module's APIs
  were "verified against the installed Foundry **14.365.0** application source".
  Those record what was actually read. **Rewriting them would fabricate
  verification nobody performed**, so the honest position is that the pin moved on
  the strength of the server-side parser rather than on a re-reading of Foundry's
  source.
- **`system_version` unchanged at 5.3.3**, evidenced rather than assumed:
  `mismatches()` names every differing field and the refusal named the core
  version alone.

**The residual risk, named for the reviewer:** parser validation catches a schema
change but **not** a schema-valid semantic change — a field that keeps its shape
and changes its meaning. Nobody has read 14.367's source or diffed a real export.
**The first real export under 14.367 is therefore also the first evidence**, and
its preview output — Actor counts, the mapped/unmapped split and the
`legacy_authority_deferred` warning count — should be compared against the
32-Actor baseline **before** it is applied.

**One design question was raised and deliberately left undecided:** the comparison
is exact-string, so every Foundry patch stops submission until a human decides.
Moving to a range would be a substantive decision about tolerable version drift
and would have been wrong to smuggle into a version bump. Raised for review as its
own question.

**Still blocking the real-folder run:** the deployed module is **1.0.7**, and the
check that refuses lives in it. **Foundry needs module 1.0.8 installed** before
any export can succeed. Until then TC-PERF-01's and TC-PERF-02's real halves
remain `Blocked`.

## 5J. SP-28, SP-15/16/17 — the synthetic performance and recovery run

**2026-08-26, 22:32Z → 23:31Z.** Grant: SG-2. The Operations Owner drove the
portal and every privileged action; Claude submitted fixtures and measured.
**Entirely synthetic** — no real Actor payload was used, so D-l's real-data
allowance was not drawn on and teardown was unconditional.

**Bounds printed and accepted before any measurement** (§11.3). The two latency
figures had no accepted source and were **accepted by Peter Duscha as Acceptance
Authority, decision D-s**, on the explicit understanding that a miss is
investigated, never relaxed.

### The corpus, and what it does and does not represent

| Fixture | Actors | Bytes | Represents |
|---|---|---|---|
| `folder-32` | 32 | 16,287,681 | **The operationally realistic case** — 496 bytes from Rehearsal B's real 16,287,185 |
| `bound` | 131 | 66,676,206 | **The N-20 ceiling, not a forecast** — 99.4% of the maximum permitted input |
| `over-bound` | 132 | 67,185,181 | The refusal, 76,317 bytes past the bound |

**The Operations Owner's point, recorded because it frames every number below:**
the real `Characters (active)` folder holds **32** Actors. The 131-Actor run
answers *"where is the wall?"*, not *"what will happen"*. The plan anticipates
growth — "a real Actor is roughly 0.5 MB of JSON and the folder will grow" — and
the answer is that it would need to roughly **quadruple** before memory became
interesting.

### Four refusals, each before the next stage could run

| Gate | Observed on the deployed staging path |
|---|---|
| Idempotency key | `400 missing_idempotency_key` in **1 ms** on a 67 MB request — **before the body** |
| Size (N-20) | `413 artifact_too_large`, **0.96 ms**: *"…over the 67108864-byte limit. **It was not read**"* |
| Admission | `403 admission_closed`: *"nothing can be recorded under it and nothing was"* |
| Duplicate content | Same bytes, new key → same `snapshot_id`, `duplicate: true`, **no second row** |

`foundry_snapshots` stayed at 0 through all four. **Unplanned TC-LIM / T-41
evidence on the deployed path, arguably worth more than the measurements it was
blocking.**

### TC-PERF-01 — worker peak resident memory, never previously measured

| Input | Peak `VmHWM` | Fraction of N-47 |
|---|---|---|
| 16.3 MB (realistic) | **184.5 MiB** | **17.9%** |
| 66.7 MB (N-20 ceiling) | **482.3 MiB** | **47.1%** |

Both inside the 1 GiB guard, the ceiling case with better than 2× headroom. Peak
scales at roughly **7× the input size** — the ratio to extrapolate from, rather
than either absolute figure.

### TC-PERF-02 — apply measured end to end

| Input | Queue wait | Run | Throughput |
|---|---|---|---|
| 16.3 MB — 32 creates | 370 ms | **6,249 ms** | 384 ms/MB |
| 66.7 MB — 99 creates + 32 updates | 841 ms | **27,015 ms** | 405 ms/MB |

Both far inside N-45's 300 s cap. **384 and 405 ms/MB across a 4× size difference
is D-m's repeatability pair**, and the linear scaling is the useful result. The
second apply exercised a path the first did not: **updates against records a
previous import created**. Durable effects matched the preview exactly —
`characters` 32 → **131**, mappings 32 → **131**, `snapshot_imports` 1 → **2**,
audit 100 → **202**.

**One figure that must not be quoted as a measurement.** The 66.7 MB *preview*
recorded 78,614 ms = 1179 ms/MB, just under the 1200 ms/MB bound. **It is not a
throughput measurement**: that is the run deliberately SIGKILLed for SP-17, and
most of its 79 seconds is lease-expiry wait. The clean preview figure is
**192 ms/MB at 16.3 MB**; a clean preview at the bound is still owed.

### TC-PERF-03 — the portal under a running job

| During | n | median | p95 | max |
|---|---|---|---|---|
| 16.3 MB preview | 219 | 32.7 ms | **38.4 ms** | 49.0 ms |
| 16.3 MB apply | 217 | 36.2 ms | **42.4 ms** | 116.7 ms |
| 66.7 MB preview + SIGKILL + recovery | 431 | 41.0 ms | **49.4 ms** | 131.3 ms |
| 66.7 MB apply | 117 | 45.1 ms | **51.2 ms** | **1,561.4 ms** |

**Zero non-200 responses across 984 samples**, including through a worker being
killed and restarted. Every p95 is an order of magnitude inside the accepted
500 ms.

**The last row is recorded as a signal, not a failure.** It passes the accepted
2000 ms maximum, but 1,561 ms is **30× the previous maximum**. During a
27-second transaction writing 131 characters, 131 mappings and 102 audit rows,
one health check took over a second — portal and worker contending on the
database. **This is the number that moves first under a larger apply**, and the
real-folder run should watch it.

### SP-17 — recovery from a lost worker

`SIGKILL` mid-parse of the 66.7 MB snapshot — **no graceful drain**, the lost
worker rather than a clean shutdown.

| Evidence | |
|---|---|
| Job attempts | **2** — first claim lost, second completed |
| `NRestarts` | **1** (`Restart=on-failure`, 5 s) |
| Wall clock | 79 s, spanning kill → restart → 60 s lease expiry → reaper requeue → retry |
| Final state | `completed`, no `failure_code`, no `stale_reason` |
| **Durable effects** | unchanged — the interruption created nothing, and a preview commits nothing |
| Portal | unaffected throughout |

**Exactly one outcome and no partial state**, which is the property the row exists
for.

### Teardown

Import tables truncated; all fixtures, the ephemeral credential and both stored
artifacts shredded (the store is empty); the admission **closed**; the transient
endpoint stopped. `audit_events` retained at 202 — **append-only by design**: the
history of what was imported survives the data being removed.

**The fence, verified after closure:** zero `snapshot_submission.accepted` events
after the close.

**The acceptance-event trail, which survived the truncate:**

```text
22:53:42  197ab2d4…  duplicate=false  generation=1
22:54:05  197ab2d4…  duplicate=true   generation=1
23:10:17  06971c12…  duplicate=false  generation=1
```

**Three events for four submissions, and that is correct** — the same-key retry
created no event at all, exactly as `foundry-snapshot-submission.md` describes.

### N-24 — the lost-pin runbook's query must run before teardown

**Class: Minor — procedure ordering. No consequence here; a real one in a real
recovery.**

`tools.submission_admission close` instructs the operator to *"Run the
acceptance-event query now."* That query joins `audit_events` to
`foundry_snapshots` on checksum — and this session had already truncated
`foundry_snapshots`, so the documented query returned **0 rows** while the
underlying append-only events were intact and answered the question when read
directly.

**Here it cost nothing.** In a genuine lost-pin recovery it would matter: the
query exists to resolve whether bytes were accepted before a closure, and
truncating first destroys its ability to do so. **The runbook should state that
the acceptance-event query runs before any import-table teardown**, and this
package's teardown order should say the same. Raised for Codex.

### An unprompted accessibility observation from the operator

Of the reconciliation job page: *"the text should be smaller as I can't really
read everything."* The cards are generously sized and content overflows at his
window width. **Not blocking, and not a contrast or semantics defect** — but it is
exactly what R-23 exists to collect, and it came from the person who will operate
the screen rather than from a checker.

### What this run does **not** establish

1. **D-m's real 32-Actor apply, reported as n = 1, is still owed.** Synthetic
   Actors parse roughly **3× faster** than real ones — Rehearsal B measured
   587 ms/MB against tonight's 192 ms/MB on an almost identical byte count —
   because the fixture's filler prose is lexically repetitive. **Tonight's timings
   are optimistic and must be cited as synthetic.**
2. A **clean** preview at the N-20 bound, uncontaminated by the SP-17 interruption.
3. TC-PERF-03b, the browser-side job-status poll latency, was not separately timed.

## 5I. SP-29 and M-5 — the gate-off window and the browser evidence

**Window opened 2026-08-26T21:24:46Z, closed 22:01:01Z — 36 minutes**, bounded at
both ends by a recorded observation, per decision **D-r**. Kill switch confirmed
available (`kill_switch: true`) before opening; **M-2 had already proved it
works**, which is why that sitting was resequenced ahead of this one.

| Step | Observation |
|---|---|
| Gate removed, `caddy validate` | **Valid configuration** — the import fails closed, so a mistake would have refused the whole config |
| Public `GET /` and `/v1/characters`, unauthenticated | **`303` both** — no `401`, and the application's own boundary redirecting to login as the only guard |
| Gate restored, `caddy validate`, reload | **Valid**, and public `GET /` → **`401`**. Prompt back |

### SP-14 / TC-SEC-07 — headers on three response classes

| Class | Result |
|---|---|
| **Normal** (`/v1/login`, 200, through the real proxy) | Full N-26 CSP verbatim, plus `cross-origin-opener-policy: same-origin`, `cross-origin-resource-policy: same-origin`, `permissions-policy: geolocation=(), camera=(), microphone=(), payment=()`, `referrer-policy: same-origin`, `x-content-type-options: nosniff` |
| **Early refusal** (wrong `Host`) | **`400 Bad Request` / `Unknown host.`** with the **same** CSP, `nosniff`, `referrer-policy` and `cache-control: no-store` — observed **at the origin**, because the public path returns **Cloudflare's `530`** and never reaches our boundary |
| **Error** (`404`) | **CSP identical to the normal response**, plus `nosniff` and `referrer-policy` |

**The CSP is byte-identical on normal and error responses**, which is the property
the row exists to assert.

**TC-SEC-07's specific assertion — the OAuth redirect under `form-action 'self'`
— is evidenced.** The Operations Owner completed a Discord login in Chrome
**151.0.7922.172 (arm64)** during the window, and the console showed **no
`form-action` violation**. A `GET`-initiated redirect is a navigation, not a form
submission, and the engine agrees.

**Evidence level, stated exactly.** Headers for the normal and error classes were
captured over the wire through the deployed proxy; the early-refusal class was
captured at the origin. **CSP enforcement in a real engine is separately
evidenced** — by the successful login and by finding **N-23** below, which is a
violation report the engine produced and acted on. What is *not* claimed is a
devtools capture of all three classes by the operator. **SP-14: Passed in part.**

### N-22 — HSTS is required by the accepted contract and is not configured

**Class: Important — a control named in the accepted contract that does not
exist in the deployed configuration or in the production template.**

Operational contract §4.1 assigns Caddy **exactly two jobs**:

> `| TLS | Existing Cloudflare origin certificates … |`
> `| HSTS | max-age at least one year, includeSubDomains only after the Operations Owner confirms no sibling host would break |`
> `| Headers | Adds HSTS; the application owns CSP and the rest … so there is one authority per header |`

**Observed on the wire: no `strict-transport-security` on any response** — normal,
error or otherwise. And the only `header` directive in **either** Caddy file is
`header -Server`: neither `infra/caddy/freedom-blades-test.caddy` nor the
production template `freedom-blades-portal.caddy.tmpl` sets HSTS.

**So one of Caddy's two assigned jobs is unimplemented, in staging and in the
template that production would be built from.** Cloudflare could add HSTS at its
edge if enabled there; empirically it is not present, and a control that depends
on an unrecorded dashboard setting is not the control the contract describes.

**Why it matters at the deployment gate rather than here:** without HSTS, a
first-time visitor who types `http://` can be intercepted before the redirect to
TLS. That is precisely the attack HSTS exists for, and the contract already
decided it should be prevented.

**Remediated in the repository 2026-08-27**, authorized by Peter Duscha
(*"Fine with me. Most important: full documentation for review"*). **Not yet
deployed** — `/etc/caddy` is root-owned and the change needs an operator reload.

**What was added**, to **both** the production template and the deployed test
site file:

```caddy
header Strict-Transport-Security "max-age=31536000"
```

| Choice | Reason |
|---|---|
| `max-age=31536000` | One year — the contract's floor, not a number invented here |
| **No `includeSubDomains`** | The contract reserves it until the Operations Owner confirms no sibling would break, and **the Foundry hosts are siblings** under `rpgworld.org` |
| **No `preload`** | A submission to a browser-vendor list, and close to irreversible |
| Set at the proxy, not the application | HSTS is a statement about the TLS connection, and TLS terminates at Caddy. The application answers on plain HTTP over loopback and cannot know whether the transport that reached the visitor was secure — a header it set would be a guess |

**The production template's own comment was the near-miss.** It read *"Security
headers: none here, deliberately … the application owns every one of them"* and
then listed **five** — CSP, Referrer-Policy, X-Content-Type-Options, COOP, CORP.
The reasoning was correct for those five and silently omitted the one the
application does **not** own. The heading now reads *"one here, and only one"*.

**On the test hostname this is a real commitment** and is recorded as such: every
browser that visits will refuse plain HTTP to that name for a year. Acceptable
because nothing is ever served there over HTTP, and it is the posture production
will carry.

**Five tests** in `tests/test_deployment_artifacts.py`, covering **both files by
name** — the existing parametrised checks glob `*.caddy` and `*.example`, so the
production `.tmpl` sat outside them, which is part of why this went unnoticed:
HSTS present with a `max-age` at or above the floor; **no `includeSubDomains` and
no `preload`** without a decision; and **the application still owns every other
header**, so this stays an exception rather than becoming a habit — two
`Content-Security-Policy` headers would silently intersect.

**Falsified rather than assumed:** the header was removed from one file and the
test observed failing with *"sets no Strict-Transport-Security header (N-22)"*,
then restored.

**Still owed:** the deployed `/etc/caddy` files need the same change and a reload,
and TC-SEC-07's header capture should then be re-run to observe HSTS on the wire.
Independent review is owed, as the authorization required.

### N-23 — HTMX triggers a CSP violation on every page that loads it

**Class: Minor — no functional impact. Found only because a real engine ran the
page.**

```text
htmx-2.0.10.min.js:1 Applying inline style violates the following Content Security
Policy directive 'style-src 'self''. … The action has been blocked.
```

**Mechanism:** HTMX 2.0.10 ships `includeIndicatorStyles: true` and injects an
inline `<style>` for `.htmx-indicator` at load. The accepted N-26 policy is
`style-src 'self'` with no nonce, so the engine blocks it. **The CSP is working
correctly; HTMX is doing something the policy forbids.**

**Impact: none functional.** No template uses `hx-indicator` — the three HTMX
templates (`audit_search`, `audit_results`, `job_status_fragment`) use only
`hx-get`, `hx-swap`, `hx-target`, `hx-trigger` and `hx-on` — and our stylesheet
defines no `.htmx-indicator` rules. HTMX is styling a feature the portal does not
use.

**Why it is still worth fixing:** a violation on every HTMX page load is console
noise that would **mask a genuine violation**, and the honest TC-SEC-07 record
must state that the deployed portal generates one in normal operation.

**Proposed remediation, not applied:** add
`<meta name="htmx-config" content='{"includeIndicatorStyles":false}'>` to
`base.html`. No inline script (which would violate `script-src`), no stylesheet
change, and **no touch to the frozen visual assets**. Raised for Codex.

### plan-SP-23 remainder — partly evidenced

| Item | Result |
|---|---|
| **Skip link** | **Passed.** `<a href="#main-content" class="skip-link">Skip to main content</a>` targeting `<main id="main-content">`, a genuine landmark (`base.html:13,15`). The operator observed it appear on `Tab` and activate, with the URL becoming `…#main-content`. No visible scroll is expected on a short page whose main content is already in view |
| **`prefers-reduced-motion`** | **Mechanism verified, effect imperceptible by design.** The stylesheet carries a correct `@media (prefers-reduced-motion: reduce)` block over `*, *::before, *::after`. The only motion in the entire stylesheet is **10 short hover transitions**; with the setting on they become instant, which is a change no operator would perceive. The operator reported no visible difference — consistent with correct behaviour, not with a defect |
| **HTMX-enhanced path exercised** | **Not Run** |
| **Real-engine contrast ratios** | **Not Run** |

### TC-UI-08 / M-6 — partly evidenced

**Real device: iPhone 15, iOS 26.6, Safari.** The Operations Owner checked every
view and exercised zoom, reporting no defect.

**Recorded as partial, because the row asks for 320 / 768 / 1280 CSS pixels** and a
phone offers only its own width (~393). **768 and 1280 are not covered.** An iPad
(portrait ≈ 820, landscape ≈ 1180) would cover the remaining bands on real
hardware, which is stronger evidence than a resized desktop window; the operator
has one and it is queued.

## 5H. SP-10 re-run on staging — N-20's fix verified where the defect was reachable

**2026-08-26, 21:00:54Z → 21:03:27Z.** Grant: SG-2 with **D-q** route A. Services
stopped by the Operations Owner; database work and verification by Claude.

**Why a second run was owed.** The N-20 remediation was proved on `freedom_test`,
where **only the owner ever connects** — so nothing there depends on a second
role's privileges and the original defect was never reachable. `freedom_staging`
is the one target with a genuinely restricted runtime role, and therefore the
only place the fix could be shown to matter.

### Preconditions

| | |
|---|---|
| Services | both `inactive`, **0 live connections** to `freedom_staging` |
| Independent backup | `pg_dump -Fc`, 145,300 bytes, mode `0600`, **`pg_restore -l` listed 243 entries** before anything depended on it |
| Runtime role baseline | **99 `freedomweb` privilege rows**; `INSERT,SELECT,UPDATE` on `sessions` |

### The drill

```text
3b. Recording the privilege inventory (N-20)
    Runtime role: freedomweb
4.  Destroying the schema to prove the restore, not the backup
5b. Re-applying the runtime grants the restore discarded (N-20)
    Applied runtime-grants.sql.tmpl for freedomweb
6b. Comparing the privilege inventory (N-20)
Restore verified for freedom_staging.                        EXIT 0
```

The runtime role was **detected, not configured** — no per-database mapping was
consulted, and none can therefore fall out of step.

### Verification — the comparison with M-4 is the point

| Check | M-4 (before the fix) | This run |
|---|---|---|
| `freedomweb` privilege rows | **0** | **99** |
| `sessions` privileges | none | **`INSERT,SELECT,UPDATE`** |
| `TRUNCATE` on `sessions` | — | **denied** — restored posture, not widened |
| Services after restore | **crash-looped to `NRestarts` 35 / 36** | **`NRestarts=0`, `running`** |
| Manual intervention needed | grants re-applied by hand | **none** |
| `/healthz` | unusable | `status: ok`, all eight checks true |

Data and guards unchanged: revision `0013`, 31 tables,
`platform_accounts=2 webauthn_credentials=4 sessions=19 audit_events=49`,
**6/6 guard functions**, and the append-only trigger observed **still refusing** a
`DELETE` inside a rolled-back transaction.

**The `NRestarts=0` row is the whole result.** The same drill, against the same
database, with the same data, differing only in the remediation — and the two
services start clean instead of crash-looping. N-20's fix is verified on the
target where the defect was reachable.

### Teardown

All seven artefacts `shred -u -n 3`, work directory removed, absence verified.
They held real credential public keys, real Discord identity and real audit
history; none of it is quoted anywhere in this document.

**SP-10 / TC-OPS-02 staging half: Passed, and now with a remediated procedure
rather than a defective one.**

## 5G. M-1c / SP-27 — A-05 criterion 4b, executed 2026-08-26. **Met.**

**Grant:** the SG-3 extension plus the specific SP-27 authorization (change-log
**C-P3.5-V** item 5). **Executed 20:20:03Z–20:20:04Z**, inside a network
namespace, by the Operations Owner at his own console. **No socket was opened at
any point.**

**This is the evidence decision D-o exists for.** Codex finding B-1 established
that a production-*marked* process is not a publicly *exposed* one:
`run_resource_checks` is a plain function (`application/web/startup.py:80`), so
S-15's production branch is reachable with no uvicorn, no bind and no route. That
claim is now an observation.

### Isolation — the corrected control, verified inside the namespace it protected

After finding **N-21**, the uid-scoped firewall rule was replaced by per-process
network namespace isolation. It was verified **twice**: once standalone before
the exercise, and again by the exercise's own first step, inside the namespace
that actually ran it.

| Check | Result |
|---|---|
| `curl https://discord.com/` inside the namespace | **`egress: 000`**, then `blocked` |
| `psql` over the Unix socket inside the namespace | **`socket: postgres`** — a network namespace does not affect Unix domain sockets |

**Blast radius: one process.** Nothing else on the host lost connectivity, and
there was no rule to remove afterwards — the isolation ended when the process did.

### Preconditions, checked rather than assumed

| | |
|---|---|
| Database | `freedom_production`, created disposable, **owned by `foundry`**, dropped at teardown |
| Revision | `0013`, 31 tables |
| **Empty of real data** | `audit_events=0 discord_users=0 sessions=0 platform_accounts=0 characters=0` |
| Migration identifiers | **Synthetic** — `900000000000000001` / `900000000000000002`. Revision 0006 requires `WEB_DISCORD_GUILD_ID` and `WEB_BOOTSTRAP_ADMIN_ROLE_ID` and deliberately has no defaults ("a default would be a production identifier in source"). Nothing in this exercise depends on their values — S-15 counts credentials on the protected account and never reads the guild — so **real production identifiers were deliberately kept out of a throwaway database** |

### The guard, made to fire before anything was seeded

```text
REFUSED: a production-marked exercise needs --acknowledge-disposable: the
operator's statement that this database was created for SP-27 and will be dropped
at teardown.                                                            exit=1
```

A guard that has never fired is a guard nobody has tested. It was fired first, on
purpose, against the real target.

### The observation

| Enabled credentials | Outcome |
|---|---|
| **1 — below the N-13 threshold** | **`outcome refused`**, `listener none — run_resource_checks called directly`:<br>`[S-15] (operator action): the protected administrator account has 1 enabled WebAuthn credential(s); N-13 requires at least 2.` |
| **2 — at the threshold** | **`outcome passed`**, `no warnings` |

**The second row is the falsification and it is why the first row means
something.** Had the check refused at both counts, the refusal would have been
about production-marking rather than about the threshold, and would have evidenced
nothing about N-13. It passed at two, so the refusal at one is the credential
floor being enforced.

### Teardown, verified independently

| Step | Result |
|---|---|
| `dropdb freedom_production` | **0 databases of that name remain**; `freedom_dev`, `freedom_staging`, `freedom_test` are the only `freedom*` databases |
| Firewall residue | **none by construction** — no rule was ever added |
| Egress outside the namespace | `discord.com → 200`, never affected |
| Credential material recorded | **none.** The synthetic credential id and public key were random bytes generated in-process; no real account, secret or value from any live system appears anywhere |

### One observation, not a finding

**The harness exits `0` on a refused outcome.** Section 3 shows `outcome refused`
followed by `exit=0`, because the tool reports what the check did rather than
judging it — a refusal is the *expected* result below the threshold, so a non-zero
exit would be wrong as often as it was right. **Recorded because a reader
skimming exit codes could misread `exit=0` as "no refusal".** The outcome line is
the result; the exit code is not.

### Disposition

**A-05 criterion 4b: Met**, before exposure, exactly as D-o requires. Criterion
**4c** — the deployment-gate re-observation at operational contract §7 item 10 —
remains owed at that gate, as defence in depth and never as a substitute.

**A-05 now stands at criteria 1, 2, 2a, 3, 4a, 4b, 5, 6, 7, 8 and 9 Met.
Criterion 10 — the Security Reviewer's break-glass readiness confirmation, which
comes last by its own terms — is the only one outstanding.**

## 5F. N-21 — this package's own procedure caused an operator-visible outage

**Class: Important — procedure defect in P3.5. Not a platform defect. Recorded
because it happened, and because the honest-outcome rule exists for exactly this.**

**Date:** 2026-08-26, rule inserted **18:02:40Z**. **Raised by:** the Operations
Owner, who diagnosed it independently and wrote an incident report before this
entry existed.

### What happened

SP-27's design calls for outbound egress to be blocked during the exercise, "with
the single `iptables` OUTPUT rule already proven by SP-25". The working Technical
Lead retargeted that rule from `freedomweb` to `foundry`, because `foundry` is the
account that runs the harness:

```bash
sudo iptables -I OUTPUT -m owner --uid-owner foundry -p tcp --dport 443 \
  -j REJECT --reject-with icmp-port-unreachable
```

**The result was an outage of unrelated services on the host.** `foundry` is uid
1000 — the maintainer's own login account, running PM2-managed services, developer
tooling and browser automation. The rule blocked **every** outbound HTTPS
connection made by any of them. An unrelated application failed with
`API Error: Connection refused`, and stayed broken until the Operations Owner
found the rule and removed it.

### Why the reasoning was wrong, stated precisely

**SP-25's rule was safe because of the account it named, not because of its
form.** `freedomweb` is a dedicated service account that runs the portal and
nothing else, so a uid-scoped block on it has a blast radius of exactly one
service — the one under test. `foundry` has no such property.

**The control was reused while the premise that made it safe was discarded**, and
the premise was never re-checked: a single `ps -u foundry` beforehand would have
shown PM2, `codex`, `claude` and browser tooling all running under that uid. It
was run *after* the incident report, not before the instruction.

### Impact and current state

| | |
|---|---|
| Blast radius | every process owned by uid 1000 |
| Platform services affected | **none** — the portal (`freedomweb`) and the bot (`discordbot`) run under different uids and were untouched |
| Data | **none touched.** No database, credential, artifact or configuration was altered by the rule |
| Resolution | the Operations Owner deleted the rule; outbound HTTPS verified restored (`discord.com → 200`) |
| Residue | a disposable `freedom_production` database was created during the attempt and **was dropped by the Operations Owner** during his own cleanup. Verified from this account: **0 databases of that name remain** |

### The correction

**The uid-scoped rule is withdrawn from SP-27 and replaced by per-process network
namespace isolation**, which affects exactly one process and cannot outlive it:

```bash
sudo unshare -n runuser -u foundry -- <command>
```

PostgreSQL remains reachable, because Unix domain sockets are not part of a
network namespace. Nothing else on the host loses connectivity, and there is no
rule left behind to forget — the isolation ends when the process does.

**This replacement has not been verified on this host**, because unprivileged user
namespaces are disabled here and the check needs root. **The revised SP-27
therefore verifies the isolation as its first step** — proving inside the
namespace that egress fails and the database socket works — before anything else
runs. A control that has not been observed working is an assumption, which is the
mistake this finding is about.

### What this does not change

**A-05 criterion 4b remains Open. SP-27 has not been executed**, and no part of it
was completed: no migration was applied, no synthetic credential was seeded, and
`run_resource_checks` was never called under a production marker.

### The lesson worth keeping

A safety control is safe because of its **scope**, not its shape. Reusing one that
was proven elsewhere requires re-establishing the property that made it safe in
the first place — here, "this uid runs only the thing under test" — rather than
copying the command and changing a parameter.

## 5E. M-1b — A-05 criterion 4a, executed 2026-08-26. **Met.**

**Grant:** the SG-3 extension, with Peter Duscha present. **Decision D-p:** taken
under the **`development`** marker on the disposable `freedom_dev`, because the
criterion's own wording is not executable (finding N-10). **17:58:32Z →
17:58:49Z.** No real credential was touched; the deployed portal was not
restarted or otherwise disturbed.

### Residue cleared first, and one thing learned by clearing it

`freedom_dev` held two synthetic credentials from the 2026-08-25 observation,
under a different operator label. The harness **refuses to touch a credential it
did not create**, so they were removed by explicit statement with the Operations
Owner's authorization rather than by bypassing that guard.

**The protected account itself could not be deleted:**

```text
ERROR: update or delete on table "platform_accounts" violates foreign key
constraint "fk_audit_events_actor_platform_account_id_platform_accounts"
```

**Not a defect — the append-only design working.** Audit history references the
account that acted, and history that could lose its actor by a later delete would
not be history. Recorded because it is the kind of refusal an operator meets
during a clean-down and should not mistake for a fault.

### The observation

| State | Enabled credentials | Result |
|---|---|---|
| **Below the N-13 threshold** | 1 | `outcome passed` with `warning refusal=S-15`: *"the protected administrator account has 1 enabled WebAuthn credential(s); N-13 requires at least 2."* |
| **At the threshold** | 2 | `outcome passed`, **`no warnings`** |

**`run_resource_checks` was called directly — no listener, no bind, no route**,
which is the same property decision D-o turns on for criterion 4b.

**The accepted C2-1 health contract, recorded live from the deployed portal at
the same moment:** `environment: staging`, `break_glass_credentials: true`,
`status: ok`.

### Cleaned down

`clear` removed the synthetic credentials and the marker table; `webauthn_credentials`
returned to **0** rows. The pre-existing protected account remains, held by the
audit foreign key above.

### What criterion 4a now rests on, and what it does not cover

**Met**: startup behaviour observed **below and at** the N-13 threshold, on a
disposable database with synthetic credential records, capturing the S-15 warning;
and the accepted `break_glass_credentials` boolean observed live on the deployed
build.

**Not covered, and recorded as not covered** (decision D-p accepted this
knowingly):

1. no observation of the threshold **under the `staging` marker itself** — S-15
   branches on `settings.environment.is_production` alone, so `development` and
   `staging` take the identical path, but that is an argument from the code, not
   an observation;
2. no running portal process observed answering `/healthz` with
   `break_glass_credentials: false`. The false state is evidenced by the S-15
   warning instead.

Option 2 of D-p — a throwaway second PostgreSQL cluster carrying a disposable
`freedom_staging` — would close both, and was declined as disproportionate.

**A-05 criterion 4a: Met. Criteria 4b (SP-27) and 10 remain outstanding.**

### S-12 — **Passed at the seventh attempt.** The six failures before it were all the observer's

The artifact-root refusal was **not** observed at the deployed level. For the
record, because the failures were instructive:

1. **Attempt 1** was invalidated by N-20 running underneath it: the worker was
   already crash-looping on missing database privileges, so its failure was not
   the artifact root and the filtered journal correctly matched no `S-12` line.
2. **Attempt 2** produced a reading from a journal window that predated the test.
3. **Attempt 3** ran the worker entry point as `freedomweb` with the environment
   files sourced — and the sourcing **silently failed**, because
   `/etc/freedom-blades` is `750 root:root` and the service account cannot
   traverse it. What refused was an empty configuration, not a bad artifact root.

**The check itself is proven to work**, at the code level, on the same host and
interpreter:

```text
/tmp/sp08-bad-artifact-root            REFUSED: root_permissive
```

That is *not* the deployed-level evidence TC-OPS-04 asks for, and **S-12 is
recorded as `Not Run`, not as passed by inference.** It is one `sed`, one restart
and one bounded journal read whenever the Operations Owner next has ten minutes.

**Attempts 4, 5 and 6, and the root cause of all of them.**

4. A path was used that **did not exist**. `FilesystemArtifactStore.ensure_ready`
   **creates** a missing root and accepts it — verified directly — so a
   non-existent path is a *valid* configuration and the worker was right to start.
5. The `sed` targeted `WORKER_ARTIFACT_ROOT` in **`worker.env`, where it has never
   existed**. The variable lives in `portal.env:73`; `worker.env` is a one-line
   override holding `WORKER_ENABLED=true` alone. Every `sed` matched nothing and
   changed nothing, silently. This was established only when the file was finally
   read, at the sixth attempt, rather than assumed.
6. With the override **appended to `worker.env`** and confirmed present in the
   running process's own environment
   (`/proc/<pid>/environ` → `WORKER_ARTIFACT_ROOT=/tmp/sp08-perm-root`), the
   worker reported `active` and the journal showed no refusal.

**Attempt 6 looked like a finding and is not one.** The observation method was
inadequate: `systemctl is-active` was read, and it reports `active` during the
window between an auto-restart and the next failure. **The discriminator is
`NRestarts`** — which is precisely what finding **N-18** in §5C records, written
earlier the same day by the same author, and then not applied here.

**What is established, and it points the other way:**

| Evidence | Result |
|---|---|
| `ensure_ready()` on `/tmp/sp08-perm-root`, this interpreter | **REFUSED: `root_permissive`** |
| The worker's own `build()` with that root, reproduced directly | **REFUSED: `ArtifactStorageError: root_permissive`** |
| Deployed unit's code path | identical — same `WorkingDirectory`, interpreter and module |

**So S-12 is very probably firing and was mis-observed.** It is recorded as
**Not Run** rather than as Passed *or* as a finding, because neither claim is
supported: the refusal was never seen, and the anomaly has an explanation more
likely than a defect.

**Attempt 7 — observed refusing, 2026-08-26 21:2x Z.** The worker's own entry
point was run **as `freedomweb`**, with the **deployed environment files** sourced
by root and the process then dropped to the service account, in the foreground
where an exception is visible rather than swallowed:

```text
  File "adapters/artifacts/filesystem.py", line 776, in _open_trusted_root
    _require_trusted_root(os.fstat(descriptor))
  File "adapters/artifacts/filesystem.py", line 1061, in _require_trusted_root
    raise ArtifactStorageError("root_not_owned", UNCHANGED)
application.artifacts.ArtifactStorageError: The snapshot artifact store could not
complete this operation (root_not_owned).
```

**`root_not_owned` is the correct refusal for this account:** the root is
`foundry`-owned and the worker runs as `freedomweb`, so the ownership check fires
before the mode check. The same root refuses as `root_permissive` when the owner
runs it — both branches of `_require_trusted_root` observed, from the two
accounts that make each one fire.

**Evidence level, stated exactly:** deployed code, deployed environment files,
deployed service account, deployed host — run at the entry point rather than
under systemd supervision. The systemd-supervised variant was attempted and
repeatedly mis-instrumented; **the refusal itself is not in doubt**, and S-11 and
S-14 already carry systemd-supervised observations in §5C and §5D.

**And the diagnosis of the six failures resolves cleanly.** Attempt 6 confirmed
the value in the running process's `/proc/<pid>/environ` but read `is-active`;
attempt 7 read `NRestarts` but never re-confirmed the value had landed.
**Neither attempt held both confirmations at once**, which is exactly how a
working refusal was mistaken first for a setup error and then for an anomaly.

**What would settle it, in one command:** append the override, restart, wait, then
read **`systemctl show -p NRestarts`** and the journal bounded to that restart —
not `is-active`.

**The lesson, and it is about the observer rather than the system:** six attempts
changed one parameter each time and re-ran, instead of establishing the facts —
which file holds the variable, what a missing directory does, what `active`
actually means. The first `grep` of the two environment files would have ended it
at attempt two. Recorded because a gate package's credibility rests on how its
evidence was obtained, not only on what it concluded.

**SP-08 stands at 13 of 15** *(updated after SP-27)*: S-01…S-11, S-14 and **S-15**
observed; S-11 and S-14 on the deployed unit, S-15 under the production marker in
SP-27. **S-12 observed refusing** at the deployed entry point under the service account.
**SP-08 therefore stands at 14 of 15**; S-13 is test-enforced and not observable
on a live host. **TC-OPS-04's remaining gap is S-13 alone.**

### Teardown — completed 2026-08-26

All six artefacts were shredded (`shred -u -n 3`) and the work directory removed,
with absence verified:

| Artefact | Size |
|---|---|
| `pre-sp10.dump` + `.sha256` | 143,986 bytes |
| `freedom_staging.dump` + `.sha256` (the drill's own) | 143,986 bytes |
| `inventory-before.txt`, `inventory-after.txt` | 700 bytes each |

The synthetic `/tmp/sp08-bad-artifact-root` was removed too; it never held data.

**An observation, checked and deliberately not raised as a finding.** The drill's
own dump was created `-rw-rw-r--` — the invoking account's umask — while the
`pre-sp10.dump` taken by hand was `0600`. That permissive file mode is
**unreachable**: `backup-restore-drill.sh:238` sets the work directory to `0700`
unconditionally, so no other account can traverse it to reach the file. This is
the same shape as N-15, whose **security consequence** was withdrawn earlier the
same day for the same reason — the finding itself stands as a deviation — and
raising this would repeat the error the withdrawal corrected. Recorded so a reviewer can see the
check was made rather than skipped.

**Completed 2026-08-26 by the Operations Owner.** The two environment-file
backups left by M-3 and M-4 —
`/etc/freedom-blades/portal.env.pre-sp08` and `worker.env.pre-sp08` — were
**duplicate copies of every secret the portal holds**. The directory is
`750 root:root`, so they were never exposed, but a spare copy of a secrets file
that outlives the procedure needing it is secrets sprawl. Both originals were
proven good by every service running healthy through the evening.

**Removed, and the result observed rather than assumed:** `/etc/freedom-blades/`
now contains `portal.env` and `worker.env` alone, and `worker.env` is back to its
original 20 bytes — confirming the S-12 override line was removed with it. **No
secret-bearing residue from this package remains on the host.**

### Superseded — outstanding teardown from this sitting

`/tmp/sp10-2026-08-26/` holds `pre-sp10.dump` and the drill's own artefacts. **They
contain real credential public keys, real Discord identity and real audit
history.** They are mode `0600`, outside the repository, and **must be shredded**
once today's sittings are finished. Retained until then deliberately, as the
rollback of last resort. **Recorded here so it cannot be forgotten.**

### 5.3 Three further observations from the same output, none of them findings

| Observation | Assessment |
|---|---|
| `WORKER_ARTIFACT_ROOT … root_unavailable` × 65, crash-looping the worker | **Historical, resolved.** A cutover-period failure mode **distinct from F5's `WORKER_ENABLED`**: the artifact root moved from `/srv/freedom` to `/srv/freedom-blades`. `/healthz` now reports `artifact_store: true` and the worker is active. Worth recording because the F5 account named only one worker failure mode and there were two |
| `jinja2.exceptions.UndefinedError: 'shell' is undefined` × 4 on `/v1/auth/emergency` | **Historical, already on record** as the S-1 incident (supervised-session evidence B-6): the deployed process predated the commit under test until the operator restarted it |
| Tracebacks naming `/opt/discord-bots/freedom-bot/...` | **Correct at the time.** These lines predate the 2026-08-25 cutover, so they name the path that was real when they were written. **Not** a further instance of N-6, which concerned caches that outlived the rename |

---

## 6. What this document does not claim

- It does **not** claim any staging procedure has been executed. Section 3 is
  empty on purpose.
- It does **not** close TC-OPS-02: §2.6 is the **disposable half**. The staging
  half is SP-10, and it is Not Run.
- It does **not** close I-06, A-05, A-06 or R-23.
- It does **not** request a gate decision.
- The rehearsals in §2 touched `freedom_test` only. No staging or production
  database, no service, no credential and no real Actor payload was involved, and
  no secret was read, printed or recorded.

## 5W. Worker parity and final TC-SEC-07 capture — 2026-08-28

**Authority and scope.** Peter Duscha authorized deployment of the reviewed
staging changes, correction of the deployed worker-unit header, and the bounded
gate-off/header procedure. He visually confirmed module 1.0.9 installed on all
three Foundry instances. That is installation evidence, not proof that each
running process loaded it. No real Actor export was handled here.

### Worker and portal deployment

- `systemd-analyze verify` returned 0, and the deployed worker unit matched the
  reviewed template after approved deployment substitution.
- The worker remained active without restart and effective `MemoryMax` was
  **2147483648** bytes.
- A database-enabled focused preflight passed **458 tests**.
- `freedom-web` restarted onto the current reviewed tree and passed Host-aware
  loopback health. The first immediate connection raced startup and refused; a
  bounded retry passed.

### Bounded window and captures

The gate was removed at **20:21:43Z** and restored at **20:23:15Z**, a
**92-second** window. Public unauthenticated `/` and `/v1/characters` returned
**303/303**, proving the application boundary was observed.

| Capture | Result |
|---|---|
| Edge normal `/v1/login` | 200; CSP; COOP/CORP; permissions; same-origin referrer; `nosniff`; `no-store`; HSTS `max-age=31536000`; `server: cloudflare` |
| Origin normal `/v1/login` | 200; the same application headers and HSTS; **no `Server` header** |
| Origin wrong-Host refusal | 400; CSP; `no-store`; `nosniff`; referrer; COOP/CORP and permissions; no unsafe detail |
| Edge missing route | 404; CSP byte-identical to normal; HSTS; application headers; `server: cloudflare` |

Only allowlisted status/security headers were retained in `/tmp`; cookies and
redirect locations were not captured. Peter completed and acknowledged the
browser step, whose explicit checks were successful Discord login with no
CSP/form-action violation and no HTMX indicator-style violation. No contrary
observation was reported.

The exit handler restored the exact gate-bearing site file, validated and
reloaded Caddy, and observed public **401**. Operational items 3 and 4 from §5R
are complete at the evidence level.

### Still outstanding

1. Installed module 1.0.9 is not proof each running Foundry process loaded it;
   record the running version after an approved restart/world reload or an
   equivalent process-owned observation.
2. After that proof, conduct the authorized real export/preview compatibility
   check without committing the artifact or Actor data.
3. Accountable A-05, A-06, I-06, R-23 and Phase 3 gate decisions remain
   deferred. Phase 4 remains unauthorized.

## 5X. Foundry 1.0.9 real active-folder compatibility — 2026-08-28

Peter observed the module-owned snapshot button in the running Foundry worlds,
which is running-load evidence rather than installed-manifest evidence. The
fresh export reported `freedom-blades-export 1.0.9`, Foundry 14.367, dnd5e
5.3.3, `/actors/Characters (active)`, 32 Actors and checksum
`fb14adf0a36ce3596aeb5b70627ec937d9411e475e7f00b0a24eca8bda543b47`.

The prior active baseline was exporter 1.0.8, 32 Actors and checksum
`673c753f9866d57a7a5a91559c2e1a1a76c070bc386d743c1c59bea012b9a155`.
The stable Actor-ID sets matched exactly. After excluding only `exportedAt` and
`exporter.version`, canonical content hashes also matched exactly. The
same 16,374,947-byte length was therefore an expected sign of unchanged world
state, not evidence that the old artifact had been reused.

A read-only staging reconciliation preview produced:

- field profile `2026-08-09.1`;
- actors 32;
- would create 32;
- already mapped, blocked and absent 0;
- errors 0 and warnings 0;
- exit code 0; and
- explicit `Rehearsal. Nothing was written.` result.

The 34-Actor inactive file and the earlier active file remained identifiable as
1.0.8 baselines. No apply was invoked, no raw Actor data was printed into this
record, and artifacts remained outside Git. This completes §5R items 1–2 at the
operational-evidence level. Final accountable decisions remain separate.
