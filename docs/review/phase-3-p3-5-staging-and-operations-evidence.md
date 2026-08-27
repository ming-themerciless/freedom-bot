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
| SP-18 | Real-device inspection | TC-UI-08 | **Not Run** |
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

**Not remediated here.** It is a change to the proxy configuration and to the
production template, it interacts with the `includeSubDomains` question the
contract explicitly reserves for the Operations Owner, and setting HSTS on a test
hostname pins that name to HTTPS in every visiting browser for the `max-age`.
**Raised for the Operations Owner and for Codex.**

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
the same shape as N-15, which was withdrawn earlier the same day for the same
reason, and raising it would repeat that error. Recorded so a reviewer can see the
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
