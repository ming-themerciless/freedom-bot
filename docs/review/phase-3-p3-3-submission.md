# Phase 3 P3.3 submission — snapshot jobs, import control and audit search

Date: 2026-08-18 · Package: P3.3 · Implementer: Claude (Technical Lead role)

**Status: re-submitted after a second remediation.** P3.3 has **not** been
accepted, stop gate **P3.G3 is open**, and P3.4 has not started. **Sections 1–11
below are the original submission and are preserved unchanged, including the
findings the review overturned.** Section 12, dated 2026-08-18, records the
remediation of the two blocking defects the first independent review raised; read
it against sections 5 and 10, whose claims it corrects. **Section 13, also dated
2026-08-18, records the remediation of the two blocking defects the independent
implementation and security re-review then raised against section 12** — and it
withdraws RR-16, which section 12 recorded as an accepted residual risk and the
re-review refused as one. Nothing was committed, pushed or deployed. No live
Google, Discord, Foundry or production service was contacted, and no real player,
Actor, guild or credential data appears anywhere in this package.

Starting authority: P3.G2 was accepted on 2026-08-18 by change-log entry
`C-P3.2-D`, at commit `c318231`, on branch `docs/platform-plan`. That decision
authorized P3.3 to begin and accepted no later gate. The pre-existing worktree
stash `stash@{0}: On main: temp before rebase` was preserved and never inspected,
applied, dropped or modified.

---

## 1. Findings and contract issues encountered, and their decisions

Four things could not be implemented from the accepted contracts without either
a silent choice or a contradiction. Each is recorded here, in change-log entry
`C-P3.3-A`, and in the RAID register — as decisions a reviewer meets, not as
diffs a reviewer discovers.

### F-1 (blocking on design) — the accepted schema names no home for the folder selection

R-41 sets a **changeable** Actor folder per snapshot, R-40 renders it as
`SnapshotRow.selected_folder`, and R-42 refuses `folder_unselected` without one.
So the selection must be durable and mutable. But:

- `foundry_snapshots` is **append-only**. Schema §11.2 grants the runtime role
  `SELECT, INSERT` on it, and migration 0002's trigger refuses `UPDATE` and
  `DELETE` **for the schema owner too**. A column there cannot be changed.
- Schema §10 defines only `reconciliation_jobs` and `reconciliation_job_results`.
- Schema §11's decision table names no table for the selection.

**Alternatives rejected.** Storing it on `foundry_snapshots` requires weakening
the append-only trigger, which is a security control protecting three tables.
Deriving the current selection by folding the append-only
`snapshot.folder_selected` audit events would make an audit log the source of
operational state, which is the separation the plan maintains everywhere else —
and would make every R-40 page load a fold over history that grows forever.

**Decision.** `snapshot_folder_selections`: one live row per snapshot, mutable,
versioned, unique on `snapshot_id`, written by R-41 alone. Its *history* remains
the append-only `snapshot.folder_selected` audit event the route contract already
requires, so nothing is lost by the row being mutable.

This follows the precedent P3.2 set and P3.G2 accepted: migration 0010 added
`identity_migration_runs` and `identity_link_proposal_candidates`, two tables
§11 does not name, because the accepted behaviour required a representation the
decision table had not spelled out — and recorded the addition in its submission.

**Nothing about data authority, authorization, privacy, migration or rollback
changes.** The selection is not authorization-bearing, holds no personal data
beyond the administrator's account id, and takes the runtime-grant band §11.2
gives every table whose row is changed in place.

**This is the one decision in the package that wants a maintainer's word**
(RAID I-11). If Peter prefers a different representation, the change is contained:
one table, one repository, one service method.

### F-2 — SM-05's forbidden-transition table and R-41 cannot both be read literally

SM-05 forbids *"any terminal state → any other state"*, naming its mechanism as
"the application's single-statement guards on `state IN ('queued','running')`".
Route contract §6.1 requires the opposite for one case, in as many words: R-41
transitions **every completed-but-unconfirmed preview** to `stale`.

**Decision.** The specific requirement governs, with the boundary drawn exactly
where the two agree:

- a **`completed` preview no apply names** is not a record of anything that
  happened. It is an offer to confirm, and `stale` is what withdrawing that offer
  is called. A preview writes only its own result row, so nothing durable is
  rewritten;
- a **`completed` apply**, and a preview an apply already names, are never
  touched. An apply that completed has committed an import.

The `parent_job_id` clause expresses "unconfirmed", and it is **one**
implementation shared by `mark_stale` and `invalidate_for_snapshot` rather than
two that agree today: R-41's folder change and R-46's N-46 expiry withdraw the
same kind of offer for different reasons.

One consequence, followed rather than worked around: `CHECK ((state =
'completed') = (result_id IS NOT NULL))` means a `stale` job cannot name a
result. The transition therefore clears `result_id` — and the result row itself
is untouched and still reachable from its own `job_id`, which is how a Council
member still sees what a just-invalidated preview said. `JobStatusView` reads the
result from that side for exactly this reason.

### F-3 — S-11 made the worker unable to read its own configuration

`WebSettings.from_environment` refused `WORKER_ENABLED=true` unconditionally.
That was correct while there was one process and wrong the moment there were two:
the worker reads the same variables from the same environment.

**Decision.** The rule is **not relaxed; it is made symmetric**, and its subject
is stated rather than assumed. `from_environment(..., process=ProcessRole.WORKER)`
refuses `WORKER_ENABLED=false` under the same `S-11`. The default is `WEB`, so
every existing caller — `create_app`, the operator commands, the suites — keeps
the behaviour it had, and nothing a web factory passes can change which rule
applies to it. `WorkerComposition` refuses a web graph independently, so a valid
web graph cannot become a worker by being handed to one. (RAID I-12, closed.)

### F-4 — an applied import recorded only a Discord snowflake

Schema §11 and ADR 0010 D1 require new rows to carry the stable platform account.
The Phase 2 apply service set only `actor_discord_user_id`, so a portal-applied
import would have written exactly the legacy-only shape the identity migration is
retiring — and R-47's receipt would have rendered it as an unattributed
bootstrap.

**Decision.** `SnapshotImportService.apply` gains a **keyword-only
`actor_account_id` defaulting to `None`**, threaded to both record-construction
sites. The Phase 2 operator path and the supervised bootstrap are untouched:
neither has an account, and the first predates them. It is *recorded*, never
*trusted* — authority is still resolved through the `AuthorizationPort` from the
Discord identity at the moment of the commit, and passing an account confers
nothing. (RAID I-13, closed.)

### Two defects the new tests found in this package's own code

Recorded because a submission that only listed contract issues would be
describing a package nobody had tried to break.

1. **The reaper reported the lease owner it had just cleared.** `RETURNING`
   yields the row *after* the update, so `lease_owner` was `NULL` by the time the
   terminal audit event named it — and that name is the only thing an operator
   has to find the process that stopped answering. The statement is now a
   three-CTE form that captures the owner in the locking select and joins it
   back; `FOR UPDATE SKIP LOCKED` is unmoved.
2. **A crash-after-commit apply reported a false `stale`.** Re-executing an
   attempt whose effect had already committed re-previewed against a database
   that now contained the characters the first attempt created, so the scope
   fingerprint differed and the job reported `aggregate_version_changed` — a job
   saying its scope moved when what moved it was itself, and a Council member
   told nothing was applied when something was. SM-05 states the rule the other
   way, and the fix follows it: a **spent request key** goes straight to the
   import service, which resolves the duplicate from the row the first attempt
   wrote.

Both were reproduced by cases added before the fix and observed failing.

---

## 2. Delivered and explicitly deferred scope

### Delivered

| Area | What |
|---|---|
| Routes | Exactly R-40…R-49, in `adapters/web/import_routes.py`, with the §6.2 matrix as a `GUARDS` table and the contract's per-route body bounds |
| Retirement | `GET /api/v1/foundry/snapshots/{checksum}/preview` **removed** (route contract §1.1), including its constructor parameters — not left answering `503` |
| Schema | Migration `0011`: `snapshot_folder_selections`, `reconciliation_jobs`, `reconciliation_job_results`; reversible; metadata parity proved by `alembic check` |
| Grants | Schema §11.2's bands for all three, plus PUBLIC normalisation, asserted as **effective** privileges |
| Job model | SM-05's six states as **check constraints**; `FOR UPDATE SKIP LOCKED` claiming; per-claim fencing tokens; the two-branch reaper; the self-abandon that shares it; request-key idempotency; N-42 admission |
| Worker | `application/worker/` and `adapters/worker/`, a separate `freedom-worker` process (`tools/freedom_worker.py`) and its systemd unit |
| Audit search | R-48/R-49 with cursor pagination, N-63 filter bounds, and an **allowlisted** payload projection |
| View models | VM-14, VM-15, VM-17, VM-18 — `vm-1` is now complete; `DEFERRED_VIEW_MODELS` is empty |
| Templates | Six minimal contract templates; no `\|safe`, no `hx-on:`, no inline script or style, nothing imported from `design-prototype/` |
| Operations | Worker runbook, retention procedure (`tools/job_retention.py`), the two health signals P3.1 left as placeholders, `.env.example` |

### Explicitly deferred, and by whom

- **Production frontend integration** is P3.4's. These templates exist so the
  contracts can be *tested* — status codes, headers, escaping, the absence of
  controls — and for no other purpose.
- **Deployment** is P3.5's. `freedom-worker.service.tmpl` is a template; no unit
  is installed, no Caddy block exists, and no staging environment exists.
- **Every staging-class measurement** — see §9. Not deferred quietly: named,
  with an owner and a prerequisite.
- **Character game-state correction** remains absent by design. No route, no
  service, no column. `TC-STRUCT-04` and the closed inventory both hold.

---

## 3. Route, authorization and transaction mapping

| Route | Requirement | Continuity (N-65) | Body | Transactions |
|---|---|---|---|---|
| R-40 `GET /v1/council/snapshots` | Council **or** administrator | refused | – | one read |
| R-41 `POST …/{snapshot_id}/folder` | Administrator only | refused | 4 KiB | **one**: selection + invalidation + audit |
| R-42 `POST …/preview-jobs` | Council only | refused | 4 KiB | one: admission + insert + audit |
| R-43 `GET /v1/council/jobs/{job_id}` | Council only | refused | – | one read |
| R-44 `GET …/{job_id}/status` | Council only | refused | – | one read, **no audit** |
| R-45 `POST …/{job_id}/cancel` | Council only | refused | 4 KiB | one: cancel + audit |
| R-46 `POST …/{job_id}/apply` | Council only | refused | 8 KiB | one: checks + insert + audit |
| R-47 `GET /v1/council/imports/{import_id}` | Council **or** administrator | refused | – | one read |
| R-48 `GET /v1/audit` | Council, administrator **or** break-glass | **permitted** | – | one read |
| R-49 `GET /v1/audit/results` | as R-48 | **permitted** | – | one read |

The preamble performs the contract's steps in the contract's order — session,
origin, content type, **this route's body bound**, CSRF, capability resolution
including any provider refresh, capability decision — and object authorization
happens inside the transaction that reads the object. A forged synchronizer token
is refused before the platform makes a single network call.

`Requirement.AUDIT_READ` exists because R-48/R-49 admit `BG`, and a break-glass
session holds `platform_administrator` with **no membership projection at all** —
`COUNCIL_OR_ADMINISTRATOR` would refuse it on the membership test.

**Separation of duties, both directions, asserted:** an administrator alone
cannot preview or apply; Council alone cannot select a folder; a combined caller
acts under `guild_council`, asserted on the durable row rather than the response.

---

## 4. Schema, migration, grants and rollback

Migration `0011`, descending from `0010`. Every SM-05 rule expressible as a check
constraint is one, because the runtime role holds `UPDATE` on
`reconciliation_jobs` and a rule living only in Python is one direct statement
away from being false:

- `completed` ⟺ a durable result — delivery plan §8.7 as a constraint;
- terminal ⟺ `finished_at`; `failed` ⟺ a code; `stale` ⟺ a reason;
- `running` ⟺ holding a lease, in **both** directions;
- `attempts BETWEEN 0 AND 3`, and **`state <> 'queued' OR attempts < 3`** — the
  constraint whose absence let a job strand. The stranded state is
  unrepresentable, not merely avoided.

`uq_reconciliation_jobs_one_live_apply` stops the second of two concurrent
applies from *starting*; the durable effect was already fenced by
`uq_snapshot_imports_applied_input` and `snapshot_imports.request_key`.

The job↔result foreign-key cycle is created with `use_alter` and dropped in the
opposite order. The alternative — dropping `result_id` and joining from the
result side — would make the durable-commit constraint inexpressible.

**Rollback evidence.** `tests/web/test_migration_0011_round_trip.py`: upgrade →
downgrade → upgrade against real PostgreSQL, with the **catalogue** compared each
way (columns, constraints, indexes); the three tables absent after the downgrade
and every pre-existing table still present; no orphaned constraint or index; and
append-only history seeded before the revision **unchanged by both directions,
compared by `xmin`** — not merely by value, which an `UPDATE … SET x = x` would
satisfy. The chain is asserted linear and `0011` the only head.

**Grants.** `snapshot_folder_selections` and `reconciliation_jobs` are
`SELECT, INSERT, UPDATE`; `reconciliation_job_results` adds `DELETE`. **No
`DELETE` on the jobs**, deliberately: N-24's sweep is an operator action run as
the schema owner, and a runtime role that could delete a job could delete the
record of a refused apply. All fourteen (table, privilege) pairs are asserted
through `has_table_privilege` after applying the real template.

---

## 5. Job state machine, idempotency, concurrency, crash/restart, cancellation

**The scope fingerprint is written in two phases**, and the phase is part of the
value rather than a nullable column. A preview cannot know its aggregate versions
at enqueue — finding out requires the parse that is the ten seconds the request
must not spend — so it is enqueued with the aggregate component `unobserved` and
**rewritten by the worker in the same transaction as the result**, so a
`completed` preview can never carry the unobserved scope. An apply **inherits**
the parent's completed fingerprint and never rewrites it, because that scope is
what the confirmation means. The worker recomputes and compares: one equality
comparison, exactly as schema §10.1 specifies.

**Idempotency is not invented here.** The request key is a **digest** —
`(kind, checksum, folder, profile version, account, nonce)` — never the caller's
text, because an apply's key is written verbatim into the one column finding S-1
established must not become an arbitrary text channel. The durable effect is
fenced by constraints that already existed and were already tested.

**Concurrency evidence is deterministic**, driven with explicit barriers over two
real connections rather than raced and hoped over: two workers claiming; two
reapers over jobs at `attempts` 1, 2 and 3; two concurrent live applies; a cancel
racing a completion; a self-abandon racing the reaper **in both orders**.

**Leases are never slept for.** `expire_lease` moves `lease_expires_at` into the
past, so the *real* reaper statement runs against a real expired lease. Shortening
the lease would also be testing a configuration nobody runs — and N-23's lease is
an exact 60 that `WorkerSettings` refuses to let be anything else.

**Fencing is per claim, not per worker.** `lease_owner` is `{instance}:{token}`
with fresh random hex each claim, so the same process cannot satisfy its own
expired lease after the reaper requeued the job and it reclaimed. Asserted.

**Cancellation.** `queued` cancels immediately; `running` records a request and is
observed at the next heartbeat; a committed apply matches zero rows and answers
`409` with the receipt. The claim predicate excludes a job whose cancellation was
requested, so a requeued attempt does not restart work somebody asked to stop.

**Crash and restart.** The hardest ordering is covered: the effect commits, the
publication does not, the lease expires, the reaper requeues, a worker finishes —
**exactly one** import, one character, and the second run reporting `duplicate`.

---

## 6. Disclosure, privacy and audit

**Artifact text never reaches a response, and escaping is not what stops it.**
Issue *messages* are dropped where the durable record is **built**, folded into
`{code, severity, count}` triples, so the dangerous string is never stored to be
rendered. The only Actor name that crosses the boundary is a blocked
create-candidate's: Council-only, capped at 50 entries, and bounded at 120
characters **where it is stored**, so the untruncated value is not sitting in the
database for the next reader either.

**The audit projection renders a key only if it recognizes it.** A denylist would
be safe only for the keys somebody remembered; an unrecognized key renders as a
redacted marker with **no value at all**. A regression parses every
`AuditEvent(payload={…})` literal in the repository and requires each key to be
classified — which is what caught nine P3.1/P3.2 keys the projection would
otherwise have silently withheld from a Council member reading history.

**Append-only holds at three independent levels**: no application method exists
(asserted over the AST), the runtime role has no grant, and migration 0002's
trigger refuses `UPDATE`/`DELETE` for the schema owner too — including an update
touching only the column migration 0006 added.

**No artifact is reachable from anywhere.** Six plausible paths answer `404`
**issued as Council**, the caller most entitled; and the rendered pages carry
neither the artifact's bytes nor the store's own reference to it.

**Polling writes no audit event**, asserted by counting rows across ten polls.

---

## 7. Test traceability

The full row-by-row map is `docs/contracts/phase-3-test-traceability.md` §21,
added by this package **by addition only** — no accepted row is rewritten.

| Module | Passed | Carries |
|---|---|---|
| `test_p3_3_matrix.py` | 62 (+26 intentional skips) | TC-OBJ-01/05/06, TC-CAP-01/02/07/09, TC-SESS-03/06, TC-AUD-01 |
| `test_p3_3_success_cells.py` | 28 | the 26 permitted matrix cells, plus the no-audit-on-poll property |
| `test_p3_3_jobs.py` | 27 | TC-JOB-01/02/03/05/06/07/08/09/10/11/12/13/15/16 |
| `test_p3_3_audit_search.py` | 42 | TC-AUD-02…08, and the runtime-grant bands |
| `test_p3_3_worker.py` | 20 | TC-JOB-04, the apply path, TC-LIM-06's P3.3 obligation, S-11/S-12 |
| `test_p3_3_disclosure_and_bounds.py` | 39 | TC-SEC-09/13, TC-JOB-14, TC-LIM-01/03/04/05, TC-OUT-01…04, TC-VM-04 |
| `test_migration_0011_round_trip.py` | 4 | migration, rollback and history-integrity evidence |
| **P3.3 slice total** | **222 passed, 26 skipped** | |

The 26 skips are the matrix's `✓` cells, skipped deliberately because "permitted"
is not one status — a permitted `GET` is `200` and a permitted mutation is `303`
— and each is asserted by name in `test_p3_3_success_cells.py`. **No database
test was skipped.**

For each confirmed defect, the smallest failing case was added first and observed
failing before the fix.

---

## 8. Commands, results, skips and warnings

Run serially against the guarded disposable `freedom_test`, because that database
is shared by both suites and running them concurrently manufactures failures.

| # | Command | Result |
|---|---|---|
| 1 | targeted reproductions before remediation | reaper: `lease_owner` returned `None`; crash-after-commit: outcome `stale` — both failed their new assertions |
| 2 | P3.3 slice (seven modules) | **222 passed, 26 skipped** |
| 3 | `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest -q tests/web` | **1342 passed, 80 skipped**, 475 pre-existing HTTPX warnings |
| 4 | `TEST_DATABASE_URL=… ./venv/bin/python -m pytest -q tests --ignore=tests/web` | **2289 passed**, 1 pre-existing `audioop` deprecation |
| 5 | `python -m compileall application adapters tools migrations tests` | exit 0 |
| 6 | `alembic check` against head | "No new upgrade operations detected" |
| 7 | `alembic downgrade 0010 && alembic upgrade head` | both clean; asserted by module 7 above |
| 8 | `git diff --check` | clean |
| 9 | migration-chain inspection | `0001…0011`, linear, single head |
| 10 | secret and unsafe-log scan over the new modules | no finding; every hit is a CSRF, cursor or preview **parameter name** |

Baselines for comparison: P3.2 closed at **1103 passed / 54 skipped** (portal) and
**2272 passed** (bot). The portal grew by 239 passing tests and 26 intentional
skips; the bot suite grew by 17.

**No configured formatter, linter or type checker exists in this repository.**
`requirements-dev.txt` and `requirements-web-dev.txt` contain `pytest`,
`pytest-asyncio` and `beautifulsoup4` and nothing else; there is no `ruff`,
`flake8`, `mypy`, `pyproject.toml`, `setup.cfg` or pre-commit configuration.
Reported as absent rather than as passing. Adding one is a deliberate change that
would reformat files across the repository and is not smuggled into this package.

**Every skip is accounted for**: 54 P3.2 matrix cells and 26 P3.3 matrix cells,
all intentional and all covered by the per-route success suites. There is no
unexplained skip.

---

## 9. Staging and manual evidence that remains outstanding

**None of this is claimed, simulated or estimated.** I-06 remains open and is
widened by this package.

| Check | What it needs | Owner |
|---|---|---|
| **TC-PERF-02** — measure a **real-folder apply** end to end | a named staging build, a real snapshot, supervision | Operations Owner |
| **TC-PERF-01** — worker peak resident memory, real folder and N-20 worst case, against N-47 | same | Operations Owner |
| **TC-PERF-03** — the portal answers `/healthz` and a status poll under a running preview | same | Operations Owner |
| **TC-LIM-02** — Caddy/application body-limit parity from deployed configuration | a deployed proxy | Operations Owner |
| **TC-SEC-07** browser half | a real browser under the accepted CSP | Operations Owner |
| **TC-OPS-01…05** | supervised rehearsals, some needing staging | Operations Owner |

TC-PERF-02 deserves emphasis: **a real-folder apply has never been measured at
all.** Rehearsal B previewed a real 32-Actor folder in 9.566 s and applied
nothing; the 500-Actor benchmark's 1.31 s apply used synthetic Actors ~233×
smaller than real ones (RA-5). P3.3 delivers the durable job model that
measurement needs. **No number in this package is a real-folder apply**, and
N-47's 1 GiB memory ceiling is a guard rather than a measurement.

**A-05 also remains open.** No public staging or production exposure is
authorized until the protected administrator account and two real WebAuthn
credentials are established and attested by Operations.

I-06, A-05, A-06, R-21 and R-28 are **not** closed by this package.

---

## 10. Deployment, configuration, worker, recovery and rollback triggers

**Configuration.** `freedom-web` and `freedom-worker` run the same code from the
same virtualenv and read the same variables, differing by `WORKER_ENABLED` — and
each refuses the other's value. In practice: two environment files identical but
for that line, or one plus `Environment=WORKER_ENABLED=true` on the worker unit.
`WORKER_ARTIFACT_ROOT` is **required** on the worker.

**Deployment order.**

1. Back up the database (the existing drill).
2. `alembic upgrade head` — `0011` only.
3. Apply `infra/postgresql/runtime-grants.sql.tmpl` as the schema owner.
4. Restart `freedom-web`. **The portal is fully functional with no worker**: jobs
   queue and Council members see `queued`. Nothing breaks; work waits.
5. Install and start `freedom-worker`.

**Recovery.** Stopping the worker is safe at any moment. A claimed job's lease
expires, the reaper requeues it, and an apply's durable effect is fenced by the
import's own unique constraints rather than by the job's state — an apply that
had committed when the process died is found by the retry and returned as a
duplicate. `TimeoutStopSec=30` is deliberately below the 60-second lease.

**Monitoring.** `/healthz` reports `worker_heartbeat` (the oldest `queued` age)
and `expired_leases` (the oldest expired lease), both against `N-23 + N-44`, both
numbers only. Two limits are documented rather than implied: an empty queue
reports `ok`, so these cannot tell an idle worker from an absent one when there
is no work; and the tolerance is generous because they answer "nothing is
draining the queue", not "the worker is healthy".

**Retention.** `python -m tools.job_retention --report` then `--apply --operator`,
as the schema owner. It removes presentation records only; `snapshot_imports`,
`audit_events` and `foundry_snapshots` are never touched.

**Rollback.** `alembic downgrade 0010` and revert the code. The downgrade is
round-trip tested and provably leaves append-only history byte-identical. Rollback
triggers: any duplicate durable effect; any job reaching `completed` without a
result; any artifact-derived text in a response; any audit row observed changing;
any apply committing without current Council authority; `expired_leases` failing
with the worker running.

---

## 11. Residual risks and recommendation

| # | Residual | Assessment |
|---|---|---|
| RR-P3.3-1 | **The heartbeat can be delayed by one GIL-holding call.** `json.loads` on a multi-megabyte artifact does not release the GIL, so the heartbeat thread cannot run during it | The lease is ~6× the whole measured 9.566 s preview and the parse's `json.loads` is a fraction of that, so the delay is comfortably inside it **at the observed scale**. At the accepted 64 MiB bound it has never been measured. The failure mode is an expired lease, which is **recoverable** (N-23) and not a failure verdict, and the durable effect is fenced by constraints regardless. Staging measurement folded into TC-PERF-01/02 |
| RR-P3.3-2 | **The worker refuses an apply whose membership projection is older than N-09** | Deliberate and **stricter than the web path**. A mutation gets no N-10 grace, and the worker performs no provider I/O. In practice the R-46 request refreshed the projection moments earlier, so a job claimed within the poll interval finds it fresh. The visible consequence is that a job that waits out five minutes in a full queue is refused rather than committed on a stale reading of somebody's roles |
| RR-P3.3-3 | **A folder path is unknown until something has previewed** | `foundry_snapshots` records folder **ids** only; a path lives in the artifact, and reading it costs the ~9.6 s R-40 must not spend. `FolderChoice.path_observed` says so rather than a path being invented, and the template renders an unobserved folder as an identifier. Additive optional field, permitted by view-model contract §1 rule 5 |
| RR-P3.3-4 | **The folder-selection representation is not an accepted contract element** | RAID I-11, above. Contained: one table, one repository, one service method |
| RR-14 (inherited) | A job may be failed by a process that never executed it | Unchanged and stated where it shows: the reaper's terminal audit event names the job's **lease history** and `reaped_by`, rather than pretending the reaper did the work |

### Recommendation

**Submit P3.3 for independent implementation review and a distinct
security-focused review.** I recommend the reviews concentrate on:

1. **F-1** — the folder-selection table. It is the one place this package
   extended the accepted schema, and it wants a maintainer's word.
2. **F-2** — the `completed → stale` boundary, and whether the line drawn between
   an unconfirmed preview and a committed apply is the right one.
3. **The apply path's authorization at the commit**, including the stricter
   N-09 freshness rule the worker applies (RR-P3.3-2).
4. **The audit payload allowlist** — a projection that fails closed on
   disclosure but can silently withhold a fact, which is the failure mode the
   completeness regression exists to catch.

---

P3.3 is **submitted**. It is not accepted; **P3.G3 is open**; P3.4 has not
started. Nothing was committed, pushed or deployed. No live service or production
data was touched, Google Sheets was never contacted, and the unrelated worktree
stash was preserved untouched.

---

# 12. Remediation — 2026-08-18 (independent implementation re-review)

Date: 2026-08-18 · Implementer: Claude (Technical Lead role) · HEAD unchanged at
`c318231`, everything uncommitted, the pre-existing stash never inspected,
applied, dropped or modified.

The independent implementation review of the submission above raised **two
blocking defects**. Both are fixed here, both are covered by deterministic
regression tests that were **first shown failing against the pre-remediation
implementation**, and neither is closed by weakening a control. Nothing in
sections 1–11 has been deleted; where this section contradicts an earlier claim,
this section is the correct one and says so explicitly.

## 12.1 Blocker 1 — the import effect was fenced by nothing

### 12.1.1 The defect, reproduced

Section 5 claimed that a committed apply cannot be cancelled, on SM-05's
authority, and SM-05 named the mechanism as *"the apply's commit sets
`state='completed'`; the cancel statement filters `state IN ('queued','running')`
and matches zero rows"*.

**That mechanism did not exist.** The apply's effect and the job's completion
were two transactions:

```text
    T1  SnapshotImportService.apply
          → characters, external_actor_mappings, snapshot_imports,
            snapshot_import.applied audit event                       COMMIT
                 ←── the window: the job is still `running` here ──→
    T2  WorkerRuntime._publish_result
          → reconciliation_job_results row + state = 'completed'      COMMIT
```

Inside that window every one of these produced a job whose stated outcome was
false:

| What happened in the window | What the job said | What was actually true |
|---|---|---|
| R-45 cancellation observed at a heartbeat | `cancelled` | the import committed |
| N-45 timeout self-abandon | `queued` (or `failed` at the cap) | the import committed |
| Kill-switch self-abandon | `queued` / `failed` | the import committed |
| Lease expiry and reaper requeue, original thread still running | `queued`, then a second attempt | the first attempt's import committed |

`application/worker/execution.py::_apply` checked a Python cancellation event
before calling `apply`, and the whole of `apply` — the re-parse, the
reconciliation, the character creation, the import row, the audit event — came
after that check. `application/worker/runtime.py::_run` made it worse by
*returning* from the loop on lease loss, on cancellation after a single
`join(timeout=heartbeat)`, on timeout and on the kill switch, in every case
leaving a live daemon thread the process had stopped watching.

**Uniqueness does not close this.** `uq_snapshot_imports_applied_input` and
`snapshot_imports.request_key` prevent a **second** effect. They do not prevent
the **first** effect from an attempt that has already been cancelled.

Reproduction, against the pre-remediation code, on real PostgreSQL:

```text
FAILED tests/web/test_p3_3_effect_fence.py::…cancellation_after_the_last_python_check_leaves_no_effect
    AssertionError: a cancelled attempt commits nothing
    {'applied_audit': 1} != {'applied_audit': 0}
    {'characters': 1}    != {'characters': 0}
    {'imports': 1}       != {'imports': 0}
    {'mappings': 1}      != {'mappings': 0}

FAILED tests/web/test_p3_3_effect_fence.py::…self_abandon_in_the_commit_window_leaves_no_effect[timeout-requeues]
    AssertionError: an abandoned attempt commits nothing

FAILED tests/web/test_p3_3_effect_fence.py::…reaped_lease_and_a_new_claim_stop_the_old_token_writing_anything
    AssertionError: a stale token commits nothing
```

### 12.1.2 The serialization design

**One column, three predicates, and PostgreSQL's row lock as the referee.**

Migration `0012` adds `reconciliation_jobs.effect_committed_at TIMESTAMPTZ`, with
`CHECK ((kind = 'apply') OR (effect_committed_at IS NULL))`. It is a **successor
migration**, not an edit of `0011`: `0011` has been applied to development and
disposable test databases, `.agents/AGENTS.md` forbids editing an applied
migration, and a revision edited in place cannot produce round-trip evidence.

`application/worker/fence.py::JobLeaseFence` issues one statement, on the **same
session as the effect**, as the last statement before that session commits:

```sql
UPDATE reconciliation_jobs SET effect_committed_at = :now, version = version + 1
WHERE id = :job_id
  AND lease_owner = :owner            -- (2) this exact per-claim token,
                                      --     which also covers (4) abandon/reap,
                                      --     both of which clear it, and
                                      --     (5) supersession, since a claim
                                      --     mints a fresh token
  AND state = 'running'               -- (1)
  AND cancel_requested_at IS NULL     -- (3)
  AND effect_committed_at IS NULL;    -- single use
```

Zero rows raises `FenceLost`, the unit of work rolls back, and **no character,
mapping, import row or success audit event survives**. `FenceLost` is
deliberately not an `ImportRefused`: a refusal is recorded as an attempted import
in its own transaction, and writing one here would be writing exactly the durable
effect the fence exists to prevent.

It is an `UPDATE` rather than a `SELECT … FOR UPDATE` plus a check because the
row's write lock **is** the serialization, and because a committed effect has to
leave a durable mark a later cancellation can see:

| Competing writer | Statement change | Why exactly one side wins |
|---|---|---|
| Cancellation request (R-45) | `+ AND effect_committed_at IS NULL` on the `running` branch of `request_cancel` | Blocks on the fence's lock, then re-evaluates its predicate under `READ COMMITTED`. Effect first → zero rows → `409` with the receipt. Cancel first → the fence sees `cancel_requested_at` → zero rows → the effect rolls back |
| Worker self-abandon (N-45 cap, kill switch) | `+ AND effect_committed_at IS NULL` on `abandon` | Same two outcomes. When the abandon loses it now returns `Abandonment(state=None, effect_committed=True)` instead of a bare `None`, because "the reaper got there first" and "my effect committed" need opposite responses |
| Reaper | none | `FOR UPDATE SKIP LOCKED` in its sub-select already skips a locked row. It reaps on its next pass if the effect rolled back |
| A newer claim | none | The claim mints a **fresh** `{instance}:{token}`, so the old attempt's `lease_owner = :owner` matches nothing — including when the *same instance* reclaims |
| R-41's folder change and R-46's N-46 expiry | `+ AND effect_committed_at IS NULL` on `mark_stale` and `invalidate_for_snapshot` | **A fourth writer the review's finding did not name**, found while building the race suite. Both transition *live* jobs, so a `running` apply is in their reach. Invalidation first → the fence's `state = 'running'` fails → nothing commits. Effect first → `stale` cannot describe an apply whose import is durable, and the predicate refuses it. This is the same argument the repository already applied to a `completed` apply, moved to the instant the effect became durable |

The isolation level is pinned at `READ COMMITTED` by
`adapters/database/unit_of_work.py`, which is what makes "blocks, then
re-evaluates its own predicate" a property of the transaction rather than of the
cluster's configuration.

**`effect_committed_at` is never cleared, including by the reaper's requeue.**
SM-05's process-restart recovery requires a requeued attempt to reach the import
service, find its spent request key and return the original import as a
duplicate. That path returns before the fence, and clearing the column would
erase the only record on the job that the effect exists (case 6 asserts both).

### 12.1.3 The thread the runtime cannot kill

The fence makes correctness independent of the thread: an orphan cannot commit.
That is not the same as pretending it ended, which is what the previous `_run`
did. `WorkerRuntime` now:

- keeps every attempt as an `_Attempt` and, when it stops watching one whose
  thread is still alive, records it as **outstanding**;
- **claims nothing** while an outstanding attempt is alive, returning
  `Tick(outcome="attempt_outstanding")` — N-41 enforced against the thread that
  is actually running rather than against the job the worker stopped watching;
- exposes `outstanding_attempts()` — a **method, not a property**, because it
  prunes the dead threads as it answers and a mutating property would be exactly
  the surprising access this project's design rules keep out of properties;
- reports `outstanding_report()` as `(job id, lease owner, why)` for the
  operator, with no checksum, requester or artifact-derived value.
  `tools/freedom_worker.py` logs it once when the condition starts and once when
  it clears — a stalled worker that printed a line per poll would bury the
  reason it stalled;
- on a self-abandon that lost to a committed effect, keeps the lease alive for
  `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` heartbeats and publishes the result
  the thread owes. **This is not "wait forever":** when the grace elapses the job
  is left `running`, the reaper requeues it within `N-23 + N-44`, and the retry
  recovers the same import as a duplicate. The bound costs a delay and never an
  effect.
- when the fence is what lost, the runtime writes **no verdict** except its own
  outstanding cancellation, which `cancel_under_lease` matches only while this
  worker still holds the lease on a `running` job.

Process isolation was considered and is **not** implemented. It would be the
stronger enforcement of N-45, and it is a topology change (N-40's process model,
the systemd unit, the pool, the artifact-store descriptor) that this remediation
is not authorized to make. What is implemented instead is stated honestly: the
worker stops taking work and says so, and the platform recovers the job through
the reaper, which needs nothing from the stalled worker.

### 12.1.4 What the fence deliberately did **not** change

- Council authorization is still re-resolved through the `AuthorizationPort` at
  the apply, before the transaction opens.
- The scope-fingerprint re-check is still the one equality comparison inside the
  attempt.
- Import, mapping and success-audit atomicity is unchanged: the fence is one more
  statement in that same transaction.
- Phase 2's operator path and the supervised bootstrap pass no fence and are
  bit-for-bit unaffected: `commit_fence` is keyword-only and defaults to `None`.
- No accepted numeric value, job state or transition changes.

### 12.1.5 The seven mandatory races

All in `tests/web/test_p3_3_effect_fence.py`, all against real PostgreSQL, all
asserting the **rows** (`snapshot_imports`, `characters`,
`external_actor_mappings`, and the `snapshot_import.applied` audit event) as well
as the job's final state. No case sleeps.

Determinism comes from `WorkerComposition.executor(fences=…)`: the cases wrap
**the production `JobLeaseFence`** in a barrier that runs a callback immediately
before or immediately after the real fence statement — inside the import's own
transaction, either side of the row lock. The competing writer is then the
production statement the runtime or the route would have issued, on its own
connection.

| # | Handover requirement | Case | Result |
|---|---|---|---|
| 1 | Cancellation wins after the final cooperative check, before the import commit | `…cancellation_after_the_last_python_check_leaves_no_effect` | no import/character/mapping/audit row; job `cancelled`; `effect_committed_at` still `NULL`; no result row |
| 2 | Timeout self-abandon wins in that window | `…self_abandon_in_the_commit_window…[timeout-requeues]` | no effect; job `queued`; lease released |
| 3 | Kill-switch self-abandon wins in that window | `…self_abandon_in_the_commit_window…[kill-switch-at-the-last-attempt-fails]` | no effect; job `failed` with `attempts_exhausted` |
| 4 | Lease expiry + reaper + a new claim while the original thread continues | `…reaped_lease_and_a_new_claim_stop_the_old_token_writing_anything` | no effect; the successor's token owns the job |
| 5 | Apply commit wins immediately before cancellation | `…apply_that_commits_first_refuses_the_cancellation_that_follows` | one import; job `completed`; `request_cancel` returns `COMPLETED` and `cancel_requested_at` stays `NULL` |
| 6 | Crash after import commit, before result publication | `…crash_between_the_effect_and_the_result_recovers_one_import` | one import through requeue and retry; `duplicate: true`; `effect_committed_at` survives the requeue |
| 7 | The same worker instance reclaiming with a new token | `…same_instance_reclaiming_cannot_make_its_old_attempt_valid` | no effect; the token, not the instance, is the fence |
| — | *(beyond the handover's seven)* R-41's invalidation wins the window | `…invalidation_in_the_commit_window_leaves_no_effect` | no effect; job `stale` |
| — | *(beyond the handover's seven)* an apply whose effect committed cannot be made `stale` by R-41 or R-46 | `…apply_whose_effect_committed_can_no_longer_be_made_stale` | both statements refuse it while withdrawing an ordinary live job in the same transaction |

Cases 2 and 3 issue the **same repository statement** the runtime's timeout
branch and kill-switch branch both issue; what differs between those two branches
is the reason string and, through `attempts`, which branch of the two-branch
update fires — so both branches are covered rather than one twice. This is stated
because it is the one place the race suite exercises the statement rather than
the `if` that selects it.

Case 5's assertion does not depend on the competing thread being observed to
block: if it arrives after the commit instead, `effect_committed_at IS NOT NULL`
refuses it just the same. Exactly one outcome is reachable either way, which is
what makes it deterministic rather than timing-dependent.

Two further cases cover the runtime's own bookkeeping (TC-JOB-24): a worker whose
thread outlived the attempt, and the `attempt_outstanding` refusal itself.

**On the last two cases, and why one of them is not a barrier race.** R-41 and
R-46 were a *fourth* writer in the fence's window — cancellation, self-abandon
and the reaper were the three the finding named. TC-JOB-25 drives the
invalidation-wins direction through the barrier, deterministically. The
effect-wins direction was **first written as a barrier race and then rewritten**,
because that race passed against the missing predicate: whether the runtime's
result publication or the administrator's invalidation reaches the row first
after the fence releases the lock is a scheduling detail, and the case passed on
the scheduling rather than on the control. TC-JOB-26 instead reaches the window's
own state through the production claim and the production fence, and asserts that
**this row cannot be made `stale` at all** — by either statement — while an
ordinary live job in the same transaction still is. Removing the predicate fails
it with `AssertionError: R-46 cannot withdraw an apply that applied`. This is
recorded because the first version of the case was evidence of nothing, and a
reviewer should be able to see that it was replaced rather than kept.

## 12.2 Blocker 2 — N-24's retention sweep could not run

### 12.2.1 The defect, reproduced

`tools/job_retention.py` released the job's result pointer before deleting:

```sql
UPDATE reconciliation_jobs SET result_id = NULL WHERE id = ANY(:ids)
```

Migration `0011` enforces `CHECK ((state = 'completed') = (result_id IS NOT
NULL))`, so that statement is refused for **every completed job** — which is most
of what a sweep removes. Driving the pre-remediation command against one eligible
completed preview on real PostgreSQL:

```text
sqlalchemy.exc.IntegrityError: (psycopg.errors.CheckViolation)
new row for relation "reconciliation_jobs" violates check constraint
"ck_reconciliation_jobs_completed_has_a_result"
[SQL: UPDATE reconciliation_jobs SET result_id = NULL WHERE id = ANY(%(ids)s)]
```

Two further defects in the same file:

- deleting an expired preview could violate
  `fk_reconciliation_jobs_parent_job_id_reconciliation_jobs … RESTRICT` while its
  apply child was still retained, aborting a sweep where the correct answer was
  "that graph is not eligible yet";
- the candidate query **inner**-joined `reconciliation_job_results`, so `failed`
  and `cancelled` jobs that never produced a result were invisible to every sweep
  ever run and would accumulate indefinitely.

`--limit` was also unvalidated: `--limit 0` reported success having swept
nothing, and an arbitrarily large value made one sweep one long transaction.

### 12.2.2 The retention design

**No schema change, and none was needed.** The foreign-key cycle needs no
breaking: deleting the job cascades to its result through
`fk_reconciliation_job_results_job_id_reconciliation_jobs … ON DELETE CASCADE`,
and the `RESTRICT` on `reconciliation_jobs.result_id` is satisfied because the
only row that referenced that result is the job being deleted in the same
statement. That is asserted by TC-OPS-06 rather than argued.

`RetentionSweep` is one object with two operations, and `main` is a thin argument
parser around it — so the tests exercise the production transaction rather than a
re-implementation of it.

**Eligibility**, stated once and applied once:

- terminal state (`completed`, `stale`, `failed`, `cancelled`);
- `finished_at` more than N-24's 30 days ago; **and**
- if the job has a result row, that row's own `expires_at` has passed.

The join is a `LEFT JOIN`, which is what makes a result-less `failed` or
`cancelled` job eligible on its terminal age alone. The two age conditions are
both applied because they can disagree — a result's expiry runs from when it was
*produced*, the job's from when it became *terminal* — and TC-OPS-10 exercises
exactly that disagreement.

**Concurrency safety and referential safety are the same lock.** The candidate
set is taken `FOR UPDATE OF j SKIP LOCKED`, which makes two concurrent sweeps
take disjoint sets, and — because inserting an apply child takes a `KEY SHARE`
lock on its parent row, which conflicts with `FOR UPDATE` — makes it impossible
for a new child to appear beneath a locked candidate between the check and the
delete.

**The retained-graph rule is a fixed point, not one pass.** A single `NOT EXISTS`
would be correct only for a two-level graph; the `WITH RECURSIVE blocked` term
grows upward from any candidate having a child nobody is deleting, through the
parents of blocked candidates, until it stops changing. A candidate is deleted
only if it is not blocked.

**The audit event is in the same transaction and can veto it.** TC-OPS-16 injects
a real `BEFORE INSERT` trigger on `audit_events` and asserts every deletion rolls
back — proving the property in PostgreSQL rather than in a patched Python object.
The payload carries `removed`, `considered` and the operator's name, and never a
job id, a checksum or a requester.

**`--limit` is validated before a connection exists.** `validated_limit` refuses
anything below 1 or above `MAX_LIMIT = 10 000` with a sentence an operator can
act on and exit code `4`. TC-OPS-17 replaces `create_engine` with something that
fails loudly, so a refusal that happened *after* connecting would fail the case
rather than pass it.

**Report mode writes nothing and locks nothing.** It runs the same predicate
without `FOR UPDATE`, because a report that blocked the enqueue path while
somebody read a count would be a report with a cost.

### 12.2.3 The twelve mandatory retention cases

All in `tests/web/test_p3_3_job_retention.py`, all against real PostgreSQL, all
driving `RetentionSweep` (the production transaction) or `main` (the command).

| # | Handover requirement | Case |
|---|---|---|
| 1 | Expired completed preview and result | `…expired_completed_preview_and_its_result_are_removed` |
| 2 | Expired completed apply and result, immutable import receipt survives | `…expired_completed_apply_goes_while_its_import_receipt_stays` |
| 3 | Stale preview whose result is linked from the result side | `…stale_preview_whose_result_is_linked_from_the_result_side_is_removed` |
| 4 | Failed/cancelled terminal jobs with and without result rows | `…failed_and_cancelled_jobs_follow_the_documented_age_policy` (4 parameterisations), plus `…result_has_not_expired_is_retained…` and `…queued_or_running_job_is_never_removed` |
| 5 | Expired preview with unexpired apply child: graph retained | `…expired_preview_with_an_unexpired_apply_child_is_retained` |
| 6 | Both eligible: graph removed with no FK/check failure | `…wholly_eligible_graph_is_removed_without_a_constraint_failure` |
| 7 | Mixed eligible and ineligible graphs under the limit | `…mixed_graphs_under_one_limit_remove_only_the_removable_ones`, plus `…limit_bounds_one_pass_and_the_next_pass_finishes_it` |
| 8 | Report mode performs no writes | `…report_mode_counts_and_writes_nothing` and `…report_mode_through_the_command_writes_nothing` |
| 9 | Injected audit failure rolls back every deletion | `…audit_failure_rolls_back_every_deletion` |
| 10 | Immutable rows unchanged except the sweep event | `…immutable_tables_are_untouched_but_for_the_sweeps_own_event` |
| 11 | A repeated apply is safe and removes zero | `…repeated_sweep_is_safe_and_removes_zero` |
| 12 | Zero, negative and excessive `--limit` refused before connection or mutation | `…nonsensical_limit_is_refused_before_a_connection_exists` (5 values), `…validator_names_what_is_wrong`, `…sensible_limit_is_accepted`, `…apply_without_an_operator_is_refused` |

## 12.3 Reproducing the failures against the pre-remediation implementation

The three control edits and the previous `tools/job_retention.py` were reinstated
in place, the new suites were run, and the remediated files were restored from a
byte-identical backup. What was reinstated:

1. `commit_fence.hold(unit_of_work)` in `_apply_within_transaction` replaced by
   `pass`;
2. `AND effect_committed_at IS NULL` removed from `request_cancel`'s `running`
   statement;
3. the same predicate removed from `abandon`;
4. `tick`'s outstanding-attempt refusal disabled;
5. `tools/job_retention.py` replaced with the submitted version.

```text
34 failed, 8 passed in 34.05s
```

Every one of the **nine** fence cases failed. Of the 30 retention cases, 25
failed; the remaining five are the ones that pass trivially against a stub —
`validated_limit`, `LimitRefused`, `RetentionSweep` and `MAX_LIMIT` **do not
exist** in the submitted file, so against the genuine pre-remediation module the
suite does not import at all and every case in it is a collection error. Stubs
were added for those four names purely so the *other* 25 cases could run and be
seen failing; that is stated here rather than presented as a clean result. The
three migration `0012` round-trip cases passed because the migration itself was
not reverted — they are new evidence for a new revision, not a regression against
old behaviour.

The remediated files were restored and the same command re-run:

```text
42 passed in 3.82s
```

## 12.4 Commands run, and their results

Both virtualenvs, in the documented environments, run **serially** — the
disposable `freedom_test` database is shared, and running the two suites
concurrently produces dozens of spurious failures.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_p3_3_effect_fence.py tests/web/test_p3_3_job_retention.py tests/web/test_migration_0012_round_trip.py -q` | **44 passed** |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_p3_3_worker.py tests/web/test_p3_3_jobs.py -q` | **47 passed** |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_p3_2_runtime_grants_and_bounds.py tests/web/test_migration_0011_round_trip.py tests/web/test_migration_0012_round_trip.py -q` | **40 passed** |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web -q` | **1386 passed, 80 skipped** (76 s). The 80 skips are the two permission-matrix modules' permitted cells, asserted by the per-route success cases |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest -q` | **2291 passed** (138 s) |
| `DATABASE_URL=… APP_ENVIRONMENT=test alembic downgrade base` then `upgrade head` | Round trip against real PostgreSQL. `downgrade base` refuses at revision `0006` without `WEB_DISCORD_GUILD_ID` / `WEB_BOOTSTRAP_ADMIN_ROLE_ID`, which is that revision's own designed refusal; the suite's `run_alembic` supplies them, and `test_migration_0012_round_trip.py` runs the full `upgrade → downgrade → upgrade` through it |
| Metadata parity: `alembic.autogenerate.compare_metadata` against `adapters/database/tables.py` | **0 differences**, and 0 reconciliation-related differences |
| Effective grants | `tests/test_runtime_grants.py` + `tests/web/test_p3_2_runtime_grants_and_bounds.py` — **passed**. No grant changed: the runtime role already held `UPDATE` on `reconciliation_jobs` (the fence's statement) and still holds **no `DELETE`** |
| `git diff --check` | clean, no output |
| Formatter / linter / type checker | **absent, and reported as absent rather than claimed.** `requirements-dev.txt` and `requirements-web-dev.txt` pin `pytest`, `pytest-asyncio` and the driver only; there is no `black`, `ruff`, `flake8` or `mypy` in either virtualenv and no configuration for one in `pytest.ini`, `alembic.ini` or any `pyproject.toml`/`setup.cfg` (neither file exists). `./venv-web/bin/python -m compileall` on every changed file succeeds. Introducing a formatter or type checker would be a drive-by dependency change this remediation is not authorized to make |

## 12.5 Diff inspection

Reviewed for secrets, real data, unrelated edits and weakened contracts:

- **No secret, credential, token, real Discord snowflake, real guild id, real
  Actor name or production identifier** appears in any changed file. `.env`,
  `yt-cookies.txt` and every credential file were never read, printed or
  modified. The new fixtures are the synthetic Phase 2 bundles the P3.3 suites
  already use.
- **No unrelated edit.** The changed files are: migration `0012`;
  `adapters/database/tables.py`, `repositories.py`, `unit_of_work.py`;
  `application/repositories.py`; `application/foundry/import_service.py`;
  `application/web/jobs.py`; `application/worker/{execution,fence,runtime}.py`;
  `adapters/web/repositories.py`; `adapters/worker/composition.py`;
  `tools/{job_retention,freedom_worker}.py`; six test modules (three new, three
  amended); and the contract, operations and project-management documents this
  section names.
- **No contract weakened.** Every change adds a predicate or a constraint. The
  three assertions that changed in existing tests are shape changes forced by
  `abandon` returning a typed `Abandonment` instead of a bare string, plus the
  `owner=` argument the executor now requires; `test_migration_0011_round_trip`
  stops asserting that `0011` is the *head* and instead asserts a single head and
  its place in the chain, because `0012` is a successor.
- **No test relaxed or removed.** The suite grew by 44 cases.

## 12.6 What remains open, and what is not mine to close

**Two decisions are Peter's, and are deliberately untouched here:**

1. **RAID I-11** — the reviewer recommends accepting
   `snapshot_folder_selections`. Peter must record the schema decision.
2. **R-41 versus SM-05** — a precise controlled-contract amendment for the
   completed-unconfirmed-preview → `stale` exception is still owed. The
   submission's "the specific requirement governs" rationale is **not** an
   amendment to the baseline and is not claimed as one.

**One amendment is proposed here, not self-approved.** SM-05's "cancelling a
committed apply" mechanism cell described something the code did not do; it is
corrected to name the fence, and two forbidden-transition rows are added. No
state, no transition and no accepted numeric value changes. Change-log entry
`C-P3.3-B`.

**Two new derived constants**, neither an accepted register number, both listed
for ratification: `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` and the retention
sweep's `MAX_LIMIT = 10 000`.

**Two new residual risks**, RAID `RR-16` and `RR-17`, recorded rather than argued
away — the exhausted-attempts job over a committed effect, and the row lock the
fence holds across the import's `COMMIT`.

**Staging gaps are unchanged and still open.** TC-PERF-01/02/03, TC-LIM-02,
TC-SEC-07's browser half and TC-OPS-01…05 remain unrun because staging does not
exist (RAID I-06). In particular **the fence has never been measured under a
real-folder apply**: RR-17's lock interval is the import's `COMMIT`, which no
measurement in this package covers. A-05 is unchanged.

---

P3.3 remains **submitted, not accepted**. **P3.G3 is open** pending an
independent implementation re-review, a distinct security-focused re-review, and
Peter's two decisions. P3.4 has not started. HEAD is `c318231`, every change is
uncommitted, and the pre-existing stash was never inspected, applied, dropped or
modified.

---

# 13. Second remediation — a committed effect is never denied, and is always published

Date: 2026-08-18 · Implementer: Claude (Technical Lead role) · **Status:
submitted, not accepted.**

Two blocking defects, found by the independent implementation and security
re-review of section 12. Both are the same mistake in two places: **a job's state
chosen without asking whether its import effect is already durable.** Section 12
closed that question for every writer that could *deny* the effect during the
commit window. It did not close it for the two writers that act *after* the
window, when the process that committed the effect is gone.

Section 12's §12.6 recorded one of them as residual risk **RR-16** and accepted
it. The reviewer refused that acceptance, and was right to: `failed` over a
durable import is a job denying something the database is still holding, whatever
the receipt says beside it. **RR-16 is withdrawn, not carried** — it is RAID
**I-17, closed**.

## 13.1 Blocker 1 — a committed effect could be cancelled after reaping

### 13.1.1 The defect, and its exact interleaving

`ReconciliationJobRepository.request_cancel` has two statements. Section 12 put
`AND effect_committed_at IS NULL` on the second — the `running` branch — and not
on the first:

```sql
UPDATE reconciliation_jobs SET state = 'cancelled', … WHERE id = :job_id AND state = 'queued'
```

The `queued` branch was believed unreachable for a committed effect. It was not,
because the reaper deliberately produced exactly that row:

```text
    T1  apply commits import, characters, mappings, applied audit event
        and effect_committed_at                                          COMMIT
    ✗   the process dies before publishing the job result
    T2  the lease expires; the reaper's requeue branch writes state = 'queued'
    T3  R-45 matches `state = 'queued'`                       → cancelled
        …over an import that is still in the database
```

That violates SM-05 and R-45's stated invariant.

**A second, quieter defect in the same path.** Even where `request_cancel`
*refused*, the application did not. `ReconciliationJobService.cancel` returned the
refusal as an ordinary outcome, recorded
`reconciliation.job_cancel_requested` in the append-only log, and the route
answered `303`. So the history said a Council member's cancellation request had
been accepted for a job whose state never changed. The route contract §6.1 and
VM-19 already required the opposite — `409` with `already_applied` — and neither
happened.

### 13.1.2 The fix, at the write boundary

- **Both branches** of `request_cancel` carry `AND effect_committed_at IS NULL`.
- `fail`, `cancel_under_lease` and `mark_stale_under_lease` — the three statements
  that write a terminal verdict under a live lease — carry it too. `abandon`,
  `mark_stale` and `invalidate_for_snapshot` already did.
- **Migration 0013 adds the invariant itself**:
  `CHECK (effect_committed_at IS NULL OR state NOT IN ('failed','cancelled','stale'))`,
  named `committed_effect_is_never_denied`. Each of those states asserts that
  *nothing was applied*; none can describe an apply whose import is durable. The
  predicates make each statement **refuse** (zero rows, a worker exits quietly);
  the constraint makes the row **impossible**, including for direct runtime-role
  SQL and for a statement a future change forgets the predicate in.
- `request_cancel` answers a typed `Cancellation` — `state`, `effect_committed`,
  `observed_state` — on the precedent `Abandonment` set in section 12.
  `JobState.COMPLETED` was doing double duty as "the job completed" and as "this
  matched nothing, for one of four reasons".
- `ReconciliationJobService.cancel` **raises** `CancellationRefused` when the
  statement matched nothing, so **no audit event is written** and the route
  answers `409`. The conflict word comes from the refusal, not from the job's
  state: a `running` apply whose effect committed reads `running`, which
  `_cancel_conflict` would have rendered `stale_version`; the truth is
  `already_applied`.

The reaper no longer requeues a committed effect either (§13.2), so the
interleaving above is gone at its source as well. The predicate is on both
branches anyway, because *"every cancellation statement refuses a committed
effect"* is a property a reader can check in one place, and *"no other statement
can produce that row"* is one they would have to reconstruct from four.

## 13.2 Blocker 2 — a committed effect could become `failed` on attempt three

### 13.2.1 The defect

`reap()` selected every expired `running` job and chose from `attempts <
max_attempts` alone:

```text
    attempts = 3, effect committed, process dead before publication
    → failed, failure_code = 'attempts_exhausted'
```

The existing crash-recovery coverage exercised attempt one, where the reaper
requeued and a **re-execution** reached the import service, found the spent
request key and published the original import as a duplicate. At the cap there is
no attempt to spend, and N-43 and `queued_can_be_claimed` forbid a fourth.

**The requeue-and-re-execute answer was wrong below the cap too**, which is why
the fix applies at every attempt count. A re-execution re-parses the artifact and
re-resolves Council authority, so it can return `Stale(AUTHORIZATION_CHANGED)`,
`Stale(FOLDER_CHANGED)` or `Failed(ARTIFACT_UNAVAILABLE)` — verdicts that say
nothing about the import that already committed, and that
`mark_stale_under_lease` and `fail` would have written over it.

### 13.2.2 The design: publish, do not re-run

**The publication is made durable where the effect is.** The commit fence's
`UPDATE` now writes one more column in the same statement:

```sql
UPDATE reconciliation_jobs SET
    effect_committed_at = :now,
    effect_result       = :result,      -- ← added
    version = version + 1
WHERE id = :job_id AND lease_owner = :owner AND state = 'running'
  AND cancel_requested_at IS NULL AND effect_committed_at IS NULL;
```

`effect_result` is the bounded summary and blocked-entry list the run produced —
the same value the result row holds, minus the five keys only the committed
import can answer for. `JobExecutor._apply` builds it from the preview it already
has, *before* calling the import service, and hands it to the fence.
`CHECK ((effect_committed_at IS NULL) = (effect_result IS NULL))` makes "the fence
writes both" a fact rather than a convention: an effect whose publication cannot
be reconstructed from durable data is an unrepresentable row.

**The reaper declines the row; recovery takes it.**

| | |
|---|---|
| `reap()` | `+ AND effect_committed_at IS NULL` in the locking sub-select. An expired lease over a committed effect is not an expiry |
| `lock_unpublished_effect()` | `SELECT * … WHERE state = 'running' AND effect_committed_at IS NOT NULL AND lease_expires_at < now() ORDER BY effect_committed_at FOR UPDATE SKIP LOCKED LIMIT 1` |
| `complete_recovered_effect()` | `running → completed`, with `effect_committed_at IS NOT NULL` and the held row lock as the entitlement in place of the lease, whose owner is gone |
| `WorkerRuntime.recover()` | One transaction per job, up to `EFFECT_RECOVERY_LIMIT = 20`, run from `tick` on the reaper's interval |

Each of the handover's design questions, answered:

| Question | Answer |
|---|---|
| How the reaper distinguishes an ordinary expiry | `effect_committed_at IS NULL` in its locking sub-select. One predicate, in the statement, not in Python |
| How publication is reconstructed after the process and the in-memory `Executed` are gone | From two rows the **effect's own transaction** wrote: `reconciliation_jobs.effect_result` and the immutable `snapshot_imports` receipt named by the job's `request_key` |
| How the summary is authoritative | Every value is read from those two rows. Nothing is recomputed against the database as it stands (which would describe the moment *after* the effect — Phase 2 finding B-1R's exact mistake), nothing comes from a caller, and no cache is consulted. The five merged keys — `import_id`, `duplicate`, `created_count`, `updated_count`, `warning_count` — are the receipt's own columns |
| How insertion, completion and the audit event stay atomic | They are one transaction, opened by `lock_unpublished_effect`'s `FOR UPDATE` and closed by the audit event. TC-JOB-35 injects a real committed `BEFORE INSERT` trigger on `audit_events` and requires PostgreSQL to take the result row and the state change down with it |
| How two racers cannot double-publish | `SKIP LOCKED`. The second finds nothing to do and writes nothing, rather than blocking and inserting a second result. TC-JOB-34 proves it with a held lock **and** with two real runtimes racing |
| How cancellation, invalidation, N-46, self-abandonment and the ordinary reaper branches are excluded | Every one carries `AND effect_committed_at IS NULL`, and `committed_effect_is_never_denied` refuses the row regardless. TC-JOB-29 drives all four **before and after** lease expiry |
| How N-43 holds, and is not disguised | Recovery mints no lease, touches no `attempts`, parses no artifact, resolves no authority and calls no import service. The claim statement is unchanged. A publication of a result the effect already produced is not an execution |
| What happens if the recovery transaction itself crashes | Everything rolls back together. The job is still `running` with `effect_committed_at` set and `result_id NULL` — which is precisely what `lock_unpublished_effect` looks for — so the next pass repeats it. **The predicate is the idempotency**; there is no flag to set and none to forget |

**The result is truthful about what it is.** `duplicate: false`, because this
job's own first and only effect wrote this import and there was no second attempt
to be a duplicate of; `recovered: true`, because what was recovered is the
*publication*. The completion audit event carries the same marker, the reason
`effect_committed_unpublished`, the job's `attempts` and the lease that stopped
answering — so an operator can tell a job the worker finished from a job the
platform finished for it. The Council member's screen is unchanged: VM-15 is not
amended and no view model gains a field.

### 13.2.3 What was considered and rejected

| Rejected | Why |
|---|---|
| A fourth claim | N-43 forbids it, and the accepted cap is not this remediation's to widen |
| Relaxing `queued_can_be_claimed` so a committed effect could requeue at the cap | A job that could never be claimed, counted against N-42's five-job queue bound forever |
| Clearing `effect_committed_at` | It is the only durable record on the job that the effect exists |
| A seventh state, `recovering` | The publication is one transaction under the row lock, so no distinguishable state is ever observable. N-27's six states are an accepted register value an internal convenience must not spend |
| Re-previewing at recovery time to rebuild the summary | It would reconcile against a database that now contains the characters the effect created, so the counts would describe a different moment from the import id beside them. That is B-1R |
| Writing `issue_counts: []` and calling the summary bounded-but-thin | It would have been a *minimal* summary, which the handover forbids. Storing the payload at fence time removes the need to decide what to leave out |
| Leaving the intermediate state as `queued` to match the handover's wording | The handover asks the reaper to move the job "into its recovery state". Under this design the recovery state is the one the crash already left — `running`, lease lapsed, no result — and the reaper's job is to **decline** to move it. This is called out because it is a deliberate deviation from the handover's description, not an oversight |

### 13.2.4 What happens if recovery itself cannot succeed — RR-18

A publication that raises leaves the job `running` with a lapsed lease. **It is
never written `failed`.** `expired_lease_age_seconds` (VM-16) climbs and the
operational runbook names the symptom, the cause and the response. Both causes —
an unreadable `effect_result` and a missing receipt — are rows migration 0013's
constraints and the fence's single transaction make unrepresentable, so this is
the behaviour of a fault rather than of an expected condition. Recorded as
**RR-18** rather than argued away.

## 13.3 Every production statement and constraint changed

| File | Change |
|---|---|
| `migrations/versions/0013_effect_publication_recovery.py` | **New.** `effect_result JSONB`; `CHECK ((effect_committed_at IS NULL) = (effect_result IS NULL))`; `CHECK (effect_committed_at IS NULL OR state NOT IN ('failed','cancelled','stale'))`. `upgrade()` refuses, *before adding anything*, a database holding a pre-0013 committed effect, naming the count and the remedy; offline (`--sql`) mode emits the same explanation as a script comment, on revision 0009's precedent |
| `adapters/database/tables.py` | The column and both constraints, in the metadata. Parity re-verified |
| `adapters/database/repositories.py` | `hold_for_effect(..., result)` — required, not defaulted — writing `effect_result` in the fence's own statement, bound as `JSONB` through `bindparams` rather than a `::jsonb` cast |
| `adapters/web/repositories.py` | `request_cancel`: predicate on the `queued` branch; typed `Cancellation`. `reap`: `AND effect_committed_at IS NULL` in the locking sub-select. `fail`, `cancel_under_lease`, `mark_stale_under_lease`: the same predicate. **New:** `lock_unpublished_effect`, `complete_recovered_effect` |
| `application/worker/fence.py` | `PendingEffectResult`; `JobLeaseFence` requires it |
| `application/worker/execution.py` | `_apply` builds the payload before the apply and hands it to the fence; the published summary is the same document plus the outcome keys |
| `application/worker/recovery.py` | **New.** `recovered_result`, `recovery_payload`, `EffectPublicationUnavailable`, `RECOVERED_KEY` |
| `application/worker/runtime.py` | `recover()`, `_recover_one()`, `EFFECT_RECOVERY_LIMIT`, `Tick.recovered`; `completion_payload` is public and takes a summary, so the live and recovered publications build one payload from one function |
| `application/repositories.py` | The `hold_for_effect` protocol |
| `application/web/jobs.py` | `Cancellation`, `CancellationRefused`, `_terminal_conflict`; `cancel` raises instead of auditing a refusal |
| `adapters/web/import_routes.py` | `_cancel_conflict` reads the refusal's own word before falling back to the state |
| `adapters/worker/composition.py`, `tools/freedom_worker.py` | The fence factory's signature; `--reap-only` also publishes; one journal line per recovered job (job id only, N-25) |

**No grant changed.** The runtime role already holds `SELECT`, `INSERT` and
`UPDATE` on `reconciliation_jobs` and `reconciliation_job_results` and still holds
**no `DELETE`**. `SELECT … FOR UPDATE` requires the `UPDATE` privilege the role
already has. `tests/test_runtime_grants.py` and
`tests/web/test_p3_2_runtime_grants_and_bounds.py` pass unchanged.

## 13.4 Migration and rollback

> **Superseded 2026-08-18 by §14.** The final paragraph of this section was
> wrong, the independent review rejected it, and §14 is the correction. It is
> left standing rather than edited away because a submission that quietly
> replaced a claim a reviewer acted on would be harder to audit, not easier. Read
> §14 for the rollback contract that actually holds. What remains true here is
> the first paragraph and the mechanics it describes.

`0013` is a **successor** to `0012`; neither `0011` nor `0012` was edited.
`downgrade()` drops the two constraints and the column, in reverse order, and
nothing else — `0012`'s column and constraint are `0012`'s to remove.
`test_migration_0013_round_trip.py` runs `upgrade → downgrade → upgrade` against
real PostgreSQL, compares the catalogue fingerprint either side, compares
append-only history on `xmin` so an `UPDATE … SET x = x` would show, and asserts
that the downgrade leaves `effect_committed_at` and
`only_an_apply_commits_an_effect` in place. **That module seeds only
`audit_events`; every reconciliation table is empty throughout, so it is
empty-schema evidence and nothing more** (§14.5).

~~Dropping `effect_result` loses no fact that is not also in `snapshot_imports`.
What a downgrade costs is the ability to publish a result for an effect that
commits while the schema is down-level — the same position `0012` was in.~~
**Both sentences are false. See §14.1.**

## 13.5 Reproducing the failures against the defective statements

The remediated files were backed up, the following control edits reinstated, the
suites run, and the files then restored **byte-for-byte** (`md5sum` verified):

1. `AND effect_committed_at IS NULL` removed from `reap`'s locking sub-select;
2. the same predicate removed from `request_cancel`'s `queued` branch;
3. `WorkerRuntime.recover()` neutered and `tick` stopped calling it;
4. `cancel()` restored to auditing the refusal and returning it;
5. migration `0013`'s `committed_effect_is_never_denied` not created (the
   database was rebuilt through the fixture's own
   `downgrade base` → `upgrade head`, so the constraint was absent rather than
   dropped by hand).

```text
tests/web/test_p3_3_effect_recovery.py          16 failed, 5 passed
tests/web/test_p3_3_effect_fence.py             1 failed  (TC-JOB-22)
tests/web/test_p3_3_worker.py                   1 failed  (TC-JOB-04's crash ordering)
```

The failures are for the intended reasons, not incidental:

```text
AssertionError: the reaper does not touch a committed effect
    assert [UUID('3125…')] == []
AssertionError: the exhaustion branch does not fire
    assert [UUID('b7ed…')] == []
AssertionError: assert True is False
  + where True = Cancellation(state=<JobState.CANCELLED>, effect_committed=False,
                              observed_state=<JobState.CANCELLED>).accepted
Failed: DID NOT RAISE <class 'sqlalchemy.exc.IntegrityError'>   (the constraint)
```

**The five that passed are the controls, and they are named rather than counted:**
`…ordinary_queued_job_is_still_cancelled_outright`,
`…expired_lease_with_no_committed_effect_is_still_reaped`,
`…live_lease_is_left_to_the_worker_that_holds_it`,
`…ordinary_job_still_reaches_every_terminal_state` and
`…committed_effect_cannot_be_recorded_without_its_publication`. Each asserts
behaviour this remediation must **not** change, so a control that failed here
would mean the remediation had narrowed something. The last one passes because
control edit 5 removed only the other constraint.

After restoring, the same commands were re-run: **120 passed**.

## 13.6 Commands run, and their exact results

Both virtualenvs run **serially**: the disposable `freedom_test` database is
shared, and running the two suites concurrently produces dozens of spurious
failures.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_p3_3_effect_recovery.py -q` | **21 passed** |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_p3_3_effect_recovery.py tests/web/test_p3_3_effect_fence.py tests/web/test_p3_3_worker.py tests/web/test_p3_3_jobs.py tests/web/test_p3_3_job_retention.py tests/web/test_migration_0011_round_trip.py tests/web/test_migration_0012_round_trip.py tests/web/test_migration_0013_round_trip.py -q` | **120 passed** |
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web -q` | **1411 passed, 80 skipped** (82 s). The 80 skips are the two permission-matrix modules' permitted cells, asserted by the per-route success cases |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest -q` | **2293 passed** (135 s) |
| `DATABASE_URL=… APP_ENVIRONMENT=test alembic downgrade base` then `upgrade head` | Full round trip against real PostgreSQL, `0001 → 0013` and back. `downgrade base` needs `WEB_DISCORD_GUILD_ID`/`WEB_BOOTSTRAP_ADMIN_ROLE_ID` for revision 0006's own designed refusal; they were supplied as the suite's `run_alembic` supplies them |
| Metadata parity: `alembic.autogenerate.compare_metadata` against `adapters/database/tables.py`, after a clean `downgrade base` → `upgrade head` | **0 differences** |
| Effective runtime grants — `tests/test_runtime_grants.py`, `tests/web/test_p3_2_runtime_grants_and_bounds.py` | **10 passed** and **33 passed**. No grant changed |
| `./venv-web/bin/python -m compileall` on every changed Python file | **succeeds** |
| `git diff --check` | **clean, no output** |
| Formatter / linter / type checker | **absent, and reported as absent rather than claimed.** There is no `black`, `ruff`, `flake8`, `mypy`, `pyright` or `isort` executable in either virtualenv, and no `pyproject.toml`, `setup.cfg`, `.flake8` or `.ruff.toml` exists. `requirements-dev.txt` and `requirements-web-dev.txt` pin `pytest`, `pytest-asyncio`, `beautifulsoup4` and the driver only. Introducing one would be a drive-by dependency change this remediation is not authorized to make |

**PostgreSQL race evidence is present, not skipped.** Every case above ran against
a real local `freedom_test` database; nothing in this section rests on a run with
`TEST_DATABASE_URL` unset.

## 13.7 Diff inspection

- **No secret, credential, token, real Discord snowflake, real guild id, real
  Actor name or production identifier** appears in any changed file. `.env`,
  `yt-cookies.txt` and every credential file were never read, printed or modified.
  The only snowflakes anywhere are the synthetic `9000000000000000xx` values
  `tests/web_fixtures.py` has always used.
- **No unrelated edit.** The changed files are exactly those listed in §13.3, plus
  the controlled documents named in §13.8 and five test modules (two new, three
  amended).
- **No contract weakened.** Every production change adds a predicate, a
  constraint, or a statement that refuses. Nothing is relaxed.
- **No test relaxed or removed.** The suite grew by 25 cases. Three existing
  assertions changed shape, each because the design changed and each stated in the
  case's own docstring: `request_cancel` answers a typed `Cancellation`
  (TC-JOB-11's race case), and TC-JOB-22 and TC-JOB-04's crash ordering now assert
  `running` + `recover()` where they asserted `queued` + a re-executed duplicate.
  `test_migration_0012_round_trip` stops asserting that `0012` is the *head* and
  asserts a single head and its place in the chain, exactly as
  `test_migration_0011_round_trip` already did, and its constraint case now sets
  `effect_result` too so that the constraint it names is the only one the
  statement can violate.
- **The pre-existing stash** `stash@{0}: On main: temp before rebase` was never
  inspected, applied, dropped or modified. Nothing was committed, pushed or
  deployed. No live Discord, Google, Foundry or production service was contacted.

## 13.8 Controlled documents updated

| Document | Change |
|---|---|
| `docs/contracts/phase-3-logical-schema.md` | `effect_result`; both check constraints; `effect_committed_at`'s note corrected — it is never cleared, and it is what routes an expired lease to publication |
| `docs/contracts/phase-3-state-machines.md` | SM-05: one added transition (`running → completed` by the recovery pass), three added forbidden transitions, the corrected "cancelling a committed apply" mechanism, the new "Effect-publication recovery" subsection, and RR-16 replaced by the design that closes it |
| `docs/contracts/phase-3-test-traceability.md` | §21.4b — TC-JOB-27…37 and TC-MIG-23; TC-JOB-22's claim corrected |
| `docs/operations/web-portal.md` | The recovered-publication symptom, the never-denied guarantee, the stalled-recovery symptom, `--reap-only`'s second half, and the corrected `409` row |
| `docs/project-management/change-log.md` | `C-P3.3-C` |
| `docs/project-management/raid-register.md` | I-16 and I-17 opened and closed; **RR-16 withdrawn**; RR-18 added |
| `docs/project-management/status.md` | Fourteenth update |

## 13.9 Security implications

- **The invariant moved from application predicates to the database.** Before,
  "a committed effect is never denied" was eleven statements a reader had to
  audit. It is now a check constraint, and the statements are defence in depth.
  A runtime-role connection at `psql` cannot write the row.
- **The append-only log stopped saying something untrue.** A refused cancellation
  wrote `reconciliation.job_cancel_requested`; it no longer writes anything.
- **`effect_result` widens no disclosure boundary.** It is the *same bounded
  value* the result row already holds — counts, closed-vocabulary issue codes, the
  checksum, the folder identity, and at most 50 blocked entries with one
  120-character display name each. It is reachable by no route: the only reader is
  `recovery.recovered_result`, and what a Council member sees is the result row,
  as before. No Actor field value, no artifact text and no raw bytes enter it.
- **The recovery publication is not a caller-reachable path.** No route, no form
  and no parameter reaches it. It runs in the worker process, on the reaper's
  interval, and takes nothing but the row it locked.
- **Nothing new is logged.** One journal line per recovered job, carrying the job
  id only (N-25). The completion audit payload carries the same counts and codes
  the ordinary one does, plus the recovery marker and the lease owner — an
  instance name and a random token, never a credential or a requester.
- **The recovery transaction cannot be starved into a denial.** The one outcome it
  will not produce is a terminal state that denies the effect: a failing
  publication retries forever and alarms, rather than resolving to `failed`.

## 13.10 What remains open, and what is not mine to close

**Peter's two decisions are unchanged and untouched here:** RAID **I-11**
(`snapshot_folder_selections`) and the **R-41 versus SM-05** controlled amendment
for the completed-unconfirmed-preview → `stale` exception. Neither is resolved by
this remediation and neither was reached for.

**One amendment is proposed, not self-approved**, and it is larger than section
12's: SM-05 gains one transition, three forbidden transitions, one column and two
constraints. **No state is added and no accepted numeric value changes.**
Change-log `C-P3.3-C`.

**One new derived constant, not an accepted register number**, listed for
ratification: `EFFECT_RECOVERY_LIMIT = 20`. Section 12's two —
`EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` and the retention sweep's
`MAX_LIMIT = 10 000` — are unchanged and still await the same ratification.

**Residual risks:** RR-16 **withdrawn and closed**; RR-17 **unchanged** (the fence
still holds the row's write lock across the import's `COMMIT`, and now writes one
bounded JSONB value in the same statement — no extra round trip and no extra
lock); **RR-18 new** (a recovery publication that cannot succeed alarms rather
than denying the effect).

**Staging gaps are unchanged and still open.** TC-PERF-01/02/03, TC-LIM-02,
TC-SEC-07's browser half and TC-OPS-01…05 remain unrun because staging does not
exist (RAID I-06). The fence has still never been measured under a real-folder
apply, and the JSONB write this remediation adds to it has not been measured
either — it is bounded by the same 50-entry cap the result row is, but that is an
argument and not a measurement. A-05 is unchanged.

## 13.11 What is requested

**An independent implementation re-review and a separate security-focused
re-review**, of this section and of the code it describes.

**P3.G3 is not closed and is not claimed closed.** It remains open until both
blocking findings are accepted as fixed, the PostgreSQL evidence above is
independently re-run, the SM-05 amendment and the three derived constants are
ratified, and Peter's two outstanding decisions are recorded. P3.4 has not
started. HEAD is `c318231`, every change is uncommitted, and the pre-existing
stash was never inspected, applied, dropped or modified.

---

# 14. Third remediation — migration 0013 could not round-trip after normal use

Date: 2026-08-18. One blocking defect, raised by the independent review of the
P3.3 effect-publication remediation (§13). Scope is this slice only: **P3.G3
remains open and P3.4 has not begun.**

## 14.1 The defect, and its exact interleaving

§13.4 claimed that dropping `effect_result` "loses no fact that is not also in
`snapshot_imports`", and that the only cost of a downgrade was the inability to
publish an effect committed while the schema was down-level. Both halves were
wrong, and the second one much more seriously than the first.

Reproduced end to end against real PostgreSQL, through the production apply path
— a real preview, a real apply, a real fence, a real receipt (transcript in
§14.7.1):

```text
STEP 1  at 0013, a truthfully completed apply
        state                = completed
        effect_committed_at  = 2026-08-18 20:39:04.190691+00:00
        effect_result keys   = ['blocked_entries', 'summary']
        result_id            = aec5ae34-01a5-4fd8-a52f-b2723cb15d5f
        receipts             = 1
STEP 2  alembic downgrade 0012
        exit code            = 0 (no refusal)
        effect_result column = 0 (destroyed)
        effect_committed_at  = 2026-08-18 20:39:04.190691+00:00 (kept)
STEP 3  alembic upgrade 0013
        exit code            = 1
        RuntimeError: 1 reconciliation job(s) recorded a committed effect before
        this revision added `effect_result`, so they carry no durable publication
        payload and cannot satisfy
        `ck_reconciliation_jobs_effect_result_accompanies_the_fence`. …
STEP 4  the database is stranded at 0012
```

The interleaving, stated once:

1. at `0013` the commit fence writes `effect_committed_at` **and**
   `effect_result` in one statement, inside the transaction that commits the
   import effect. `ck_…_effect_result_accompanies_the_fence` makes the pair
   inseparable;
2. `downgrade 0012` drops `effect_result` and deliberately keeps
   `effect_committed_at` — that column belongs to `0012`, and removing it would
   be `0012`'s downgrade doing `0013`'s work;
3. `upgrade 0013` runs `_refuse_rows_this_revision_cannot_describe()`, which
   counts **every** row with `effect_committed_at IS NOT NULL`;
4. a truthfully completed apply is in that count. Its state does not narrow it
   and nothing else about it does either: the payload the constraint requires was
   destroyed in step 2; and
5. the re-upgrade refuses. **The database cannot return to head**, and every
   remedy that would clear the refusal is one this platform forbids — deleting
   committed job or import history, clearing the fence, or manufacturing a result.

The evidence §13.4 offered was `test_migration_0013_round_trip.py`, which seeds
three `audit_events` rows and nothing else. Every reconciliation table is empty
for the whole of its round trip, so it proved the statements were structurally
reversible and proved nothing whatever about a database that had done work. That
module's docstring now says so in its first paragraph.

**What is actually lost.** `snapshot_imports` is the immutable receipt of the
*import*; `effect_result` is the durable publication of the *run*. They are
different documents, and the second is not derivable from the first:

| Value | In `effect_result` | In `snapshot_imports` |
|---|---|---|
| `blocked_entries` — up to 50 blocked create-candidates, one bounded display name and candidate character ids each | yes | **no** |
| `issue_counts` — `{code, severity, count}` triples | yes | only bare `issue_codes` |
| `would_create`, `would_update` | yes | no (the receipt has committed `created_count`/`updated_count`, which answer a different question) |
| `selected_folder_path` — the administrator's R-41 selection as the run saw it | yes | no (`folder_path` is the artifact's) |
| checksum, folder identity, profile version, actor/mapped/unmapped/blocked/absent/error/warning counts | yes | yes |

For a **completed** job the published `reconciliation_job_results` row happens to
hold a superset of the payload, so the fact is not lost — but it is not the
fence's own write either, and reconstructing `effect_result` from it on
re-upgrade would be a migration inventing a durable value with a defined single
writer. That is not done. For a **committed-but-unpublished** job there is no
superset anywhere: `effect_result` is the only row that holds it.

## 14.2 The chosen design

> **SUPERSEDED FINDING — do not read as current.** What this section originally
> said was: *"Schema downgrade below revision `0013` is available until the first
> apply commits an import effect, and refused afterwards."* That is a claim about
> a historical event. The guard records no such event and this schema holds none,
> and the second remediation's independent review was right to reject it.
>
> **The corrected rule, which is what the code enforces and what the rest of this
> document states:**
>
> > Downgrade below 0013 is refused while any **retained** reconciliation job
> > records a committed effect. It becomes available only when no such job
> > exists; in normal operation that means either no apply has committed, or
> > every completed committed-effect job and its result has been removed by the
> > approved N-24 retention process and no committed-but-unpublished job
> > remains.
>
> See §16.1 for the four database states this admits, and
> `docs/operations/web-portal.md` §3.6 for the operational contract.

`downgrade()` counts the **retained** committed effects **before it changes
anything** and raises. Nothing is dropped, `alembic_version` does not move, and the database is
left at `0013`, complete and usable.

Two populations are counted and named separately, because a downgrade costs them
different things and the operator's next action depends on which they hold:

- **`state = 'completed'`** — the publication already happened. What a downgrade
  would take is the ability to return to head, which is enough on its own.
- **anything else** (in practice `running` with a lapsed lease) — the effect is
  durable and unpublished. A downgrade would take the publication *and* the
  return to head. `queued` is included by `state <> 'completed'` deliberately: no
  production statement requeues a committed effect any more, but the column is
  still representable there, and a row the guard did not count would be a row a
  downgrade silently broke.

Offline (`--sql`) mode gets the same guard as an executable `DO … RAISE
EXCEPTION` block, emitted **before** the first `DROP`. The upgrade can afford a
comment there — its two `ADD CONSTRAINT` statements validate every existing row
and refuse on their own — but `DROP CONSTRAINT`/`DROP COLUMN` succeed against any
data at all, so a comment would have been the only protection, and a comment is
not a control.

### Why not the alternatives

- **Weaken `effect_result_accompanies_the_fence`** so a `completed` job need not
  carry a payload. Rejected: it is the constraint that makes "an effect whose
  publication cannot be reconstructed from durable data is unrepresentable" a
  fact rather than a convention, and the handover forbids changing the
  effect-publication invariant.
- **Narrow the upgrade guard** to unpublished effects only. Rejected for the same
  reason, and it would leave `completed` rows violating the constraint it is
  guarding.
- **Reconstruct `effect_result` on re-upgrade** from `reconciliation_job_results`.
  Rejected: it is only available for the completed population; the result row is
  a superset written by the publication rather than the fence's own write, so the
  reconstruction would be a migration writing a durable fact it did not witness;
  and it would answer for the instant the migration ran rather than the instant
  the effect committed, which is precisely the mistake Phase 2 finding B-1R
  exists to prevent.
- **A sidecar table or a JSONB stash carried across the downgrade.** This is the
  one design that could make a data-bearing downgrade genuinely reversible, and
  it is a **material new schema object with its own ownership and retention
  rules**. The handover requires that to be presented for maintainer approval
  before implementation, so it is presented here as a rejected-for-now option and
  not built. Its cost, for the record: a new table the runtime role must not
  read, a retention rule for a payload whose job may since have been swept by
  N-24, and a second writer for a value whose single-writer property is what
  makes the recovery path trustworthy.
- **Clear `effect_committed_at`, delete the jobs, or truncate.** Forbidden by the
  handover and by `.agents/AGENTS.md`; each destroys the record of something that
  happened.

### What this does not change

No constraint is weakened, no invariant is amended, no state is added, no grant
changes, and no application or worker statement is touched. The whole production
change is one guard function in one revision file. `alembic check` reports no
metadata difference, because there is no metadata difference to report.

## 14.3 Answers to the handover's required design questions

> **Corrected 2026-08-19 (third correction).** These answers were written
> against the superseded "first apply" wording. Each one below now states the
> retained-row predicate; nothing else about them changed.

**Is downgrade of `0013` supported while a retained job records a committed
effect?** No. It is refused before any schema change. It is supported again once
no such job survives — see the four states in §16.1.

**If it remains supported, how is the information for a re-upgrade preserved?**
Where it is supported, there is nothing to preserve: the downgrade is available
exactly when no retained job holds an `effect_result`, so no such value exists to
carry across. Where a retained job does hold one, the answer is the refusal, not
a preservation mechanism.

**How is an unpublished committed effect handled during downgrade?** It is not:
the downgrade refuses, so no unpublished effect ever faces a schema without the
recovery column. The operator is told to let the worker publish it at `0013`
first (which is worth doing regardless). That clears the population that would
have been unrecoverable and moves the job to `completed`; the downgrade is still
refused while that completed job is **retained**, and becomes available when
approved N-24 retention has removed it and its result. Publication therefore does
reopen the boundary, but only through retention and never immediately — and
shortening or hand-running retention to reach that point is not a supported
rollback route.

**How do completed and committed-but-unpublished jobs differ?** They are counted
apart in the refusal (§14.2). Completed loses only the return to head;
unpublished loses the publication as well.

**How does re-upgrade reconstruct authoritative facts?** It reconstructs nothing.
No truthful reconstruction exists (§14.1), so the guard refuses and says which of
the two ways the database came to hold such a row — never reached `0013`, or was
taken below it by something other than `downgrade()` — because the two need
different answers.

**How are bounded result fields absent from `snapshot_imports` preserved?** By
refusing before they are lost. The table in §14.1 enumerates them.

**The exact operational rollback boundary.** Not an event: a **condition on
retained rows**. `alembic downgrade 0012` is supported, and genuinely reversible
with realistic rows, whenever no retained reconciliation job records a committed
effect — which includes a database that has never applied and a database whose
completed committed-effect jobs and results have all been removed by approved
N-24 retention. While such a job is retained, rollback is application
roll-forward, or a restore that is a data-loss decision for the Acceptance
Authority. A committed-but-unpublished job is never retention-eligible at any
age, so it refuses the downgrade until it is published.

**Code rollback compatibility.** `docs/operations/web-portal.md` §3.6 carries the
matrix. In short: `0013` + remediated code is the only supported production pair;
`0012` + remediated code fails every apply (undefined column) and must not be
run; `0013` + pre-0013 code fails safe — the old fence writes no payload, so
`effect_result_accompanies_the_fence` aborts the import transaction and nothing
commits — which is why **roll-forward order is migrate-then-deploy**, and why
rollback order is **stop every worker, confirm the preflight, downgrade, then
deploy the older code**.

**Retry and crash behaviour.** Both directions run in one transaction
(`migrations/env.py` wraps `run_migrations()` in `context.begin_transaction()`;
PostgreSQL's DDL is transactional). A refusal, a crash or a cancelled command
leaves the complete pre-migration or the complete post-migration schema and data,
never half of either, `alembic_version` included. Both commands are safe to
re-run; a refusal writes nothing at all.

**What an operator does when a precondition refuses.** `docs/operations/web-portal.md`
§3.6, "Recovery procedure when the downgrade is refused" and "If a *re-upgrade*
is refused".

## 14.4 The policy this remediation does **not** self-approve

The refusal is implemented. The operational contract it implies — that past the
retained committed effect, rolling P3.3 back is application rollback or roll-forward
rather than schema downgrade — is a **proposal awaiting Peter/Acceptance
Authority ratification**, recorded as change-log `C-P3.3-D` and RAID **D-09**.

Refusing to destroy a payload nothing may truthfully reconstruct is correct under
either policy, which is why it is implemented now rather than held. What is being
asked for is ratification of the *consequence*, not of the refusal.

The sidecar design that would make a data-bearing downgrade genuinely reversible
is presented in §14.2 and **not built**, because it is a material new schema
object with new ownership and retention rules.

## 14.5 Evidence, classified

The classification is the point of this table: §13.4's error was citing the first
row as though it were the second.

| Class | What it is | Where |
|---|---|---|
| **Empty-schema round trip** | `upgrade → downgrade → upgrade` with every reconciliation table empty. Proves the statements are structurally reversible and rebuild an identical catalogue. Proves nothing about a populated database | `tests/web/test_migration_0013_round_trip.py` (docstring now says exactly this) |
| **Data-bearing downgrade, below the boundary** | A database with completed previews, durable results, a refused import receipt, a failed apply and append-only audit history — and no committed effect — round-trips and every durable row is unchanged, `xmin` included | `…rollback_boundary.py::…succeeds_below_the_boundary_with_realistic_rows` |
| **Data-bearing downgrade, above the boundary** | Refused before any schema change, with both counts and the operator's action; the database is left at `0013`, complete, with every durable row untouched by `xmin`, and still able to publish the effect it holds | `…rollback_boundary.py::…refuses_a_published_committed_effect`, `…refuses_a_committed_but_unpublished_effect`, `…names_both_populations_separately`, `…leaves_history_untouched_and_the_database_usable` |
| **Application roll-forward / rollback recovery** | Documented, not tested here: it is a deployment procedure, and this repository has no staging (RAID I-06) | `docs/operations/web-portal.md` §3.6 |
| **Implemented behaviour** | The downgrade guard, its offline `DO` block, and the corrected upgrade-guard message | `migrations/versions/0013_effect_publication_recovery.py` |
| **Awaiting ratification** | The rollback-boundary operational contract (`C-P3.3-D`, RAID D-09). The §13 items — the SM-05 amendment, `EFFECT_RECOVERY_LIMIT`, `EFFECT_PUBLICATION_GRACE_HEARTBEATS`, the sweep's `MAX_LIMIT` — are unchanged and still awaiting the same ratification | this section, change-log, RAID |

**No claim is made that dropping `effect_result` loses no necessary fact.** The
opposite is now asserted, and tested. **P3.G3 is not claimed closed.**

## 14.6 Every production change

| File | Change |
|---|---|
| `migrations/versions/0013_effect_publication_recovery.py` | **New** `_refuse_a_downgrade_that_cannot_be_undone()`, called by `downgrade()` before its first `DROP`; **new** `OFFLINE_DOWNGRADE_GUARD`, an executable `DO … RAISE EXCEPTION` block for `--sql` mode; the `unpublishable` branch of the upgrade guard now distinguishes a database that never reached `0013` from one taken below it, and stops recommending `TRUNCATE` to the second; the module docstring's reversibility claim corrected |
| `tests/conftest.py` | `migrated_database` empties the disposable database's two reconciliation tables before `downgrade base`, applying the refusal's own documented remedy. Without it, one interrupted run would make every later session fail at the fixture — the refusal is deliberately unconditional, and `downgrade base` is a downgrade |

**No schema object, constraint, grant, application statement, worker statement or
contract value changed.** `alembic check` is unchanged and still reports no
difference; `infra/postgresql/runtime-grants.sql.tmpl` was not touched.

## 14.7 Verification

Both virtualenvs run **serially**: the disposable `freedom_test` database is
shared, and running the two suites concurrently produces dozens of spurious
failures.

### 14.7.1 The pre-fix failure, recorded

The new module was written and run **before** the migration was changed.

```text
$ TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
    ./venv-web/bin/python -m pytest tests/web/test_migration_0013_rollback_boundary.py -q
8 failed, 1 passed in 4.11s
```

The first failure is the finding itself, and the rest are its consequence:

```text
test_the_downgrade_refuses_a_published_committed_effect
    Failed: DID NOT RAISE <class 'subprocess.CalledProcessError'>
        — `alembic downgrade 0012` succeeded on a database holding a truthfully
          completed apply, its receipt and its durable result.

test_the_downgrade_refuses_a_committed_but_unpublished_effect
test_the_refusal_names_both_populations_separately
test_the_refusal_leaves_history_untouched_and_the_database_usable
test_the_downgrade_and_re_upgrade_succeed_below_the_boundary_with_realistic_rows
    psycopg.errors.UndefinedColumn: column "effect_result" does not exist
        — the database left at 0012 by that successful downgrade, which is
          exactly the stranded state the finding describes.

test_an_interrupted_downgrade_leaves_the_complete_pre_migration_schema
    psycopg.errors.UndefinedObject: constraint
    "ck_reconciliation_jobs_effect_result_accompanies_the_fence" … does not exist

test_the_offline_downgrade_script_carries_the_same_guard
    AssertionError: 'RAISE EXCEPTION' not in <the generated script>
        — the offline downgrade had no guard at all, only DROP statements.

test_the_operations_document_records_the_rollback_boundary
    AssertionError: 'Migration 0013 rollback boundary' not in the runbook
```

The one that passed is `…an_interrupted_upgrade_leaves_the_complete_pre_migration_schema_and_rows`,
which exercises the **upgrade** guard's denying-state branch — behaviour this
remediation must not change, so a control that failed here would have meant the
remediation had narrowed something.

The interleaving itself was also reproduced end to end through the production
apply path, and is the transcript quoted in §14.1: `downgrade 0012` exit code
`0`, `effect_result` destroyed, `effect_committed_at` kept, `upgrade 0013` exit
code `1`, database stranded at `0012`.

### 14.7.2 After the fix

> **Historical — the result of the §14 tree, not of the current one.** These
> counts were exact when taken and are kept unrewritten. The evidence for the
> **final** tree is §16.4; do not cite this table as current.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=… ./venv-web/bin/python -m pytest tests/web/test_migration_0013_rollback_boundary.py -q` | **9 passed** |
| `… -m pytest tests/web/test_migration_0013_rollback_boundary.py tests/web/test_migration_0011_round_trip.py tests/web/test_migration_0012_round_trip.py tests/web/test_migration_0013_round_trip.py -q` | **20 passed** (10.86 s) — migrations `0011`, `0012` and `0013` round trips against real PostgreSQL |
| `… -m pytest tests/web/test_p3_3_jobs.py tests/web/test_p3_3_worker.py tests/web/test_p3_3_effect_fence.py tests/web/test_p3_3_effect_recovery.py tests/web/test_p3_3_job_retention.py -q` | **109 passed** — every P3.3 job, worker, effect-fence, effect-recovery and retention test |
| `… -m pytest tests/web -q` | **1420 passed, 80 skipped** (84.29 s). The 80 skips are the two permission-matrix modules' permitted cells, asserted by the per-route success cases. The count is +9 on §13's 1411, which is exactly this remediation's new module |
| `TEST_DATABASE_URL=… ./venv/bin/python -m pytest -q` | **2293 passed** (135.86 s) — the full bot suite, unchanged |
| `… -m pytest tests/test_database_postgresql.py::test_migration_matches_table_metadata tests/test_database_postgresql.py::test_migrations_apply_to_empty_postgresql_and_downgrade tests/test_runtime_grants.py tests/web/test_p3_2_runtime_grants_and_bounds.py -q` | **45 passed** — metadata parity (`alembic check`), the empty-database `base ↔ head` round trip, and the effective runtime-grant tests. **No grant changed** |
| `alembic downgrade base` then `upgrade head` then `alembic check`, against real PostgreSQL | Full `0001 → 0013` round trip; `check` reports **"No new upgrade operations detected."**; the database ends at `0013` |
| `alembic downgrade 0013:0012 --sql`, script then applied with `psql -v ON_ERROR_STOP=1` against a database **below** the boundary | `BEGIN / DO / ALTER TABLE ×3 / UPDATE 1 / COMMIT` — the guard runs and passes, and the script is valid SQL |
| the same guard block, run inside a transaction against a database holding one committed unpublished effect | `ERROR: Refusing to downgrade revision 0013: 1 reconciliation job(s) record a committed import effect (0 completed, 1 committed but unpublished). …` then `ROLLBACK`. **The offline path refuses for real, not only in the generated text** |
| `./venv-web/bin/python -m compileall` on every changed Python file | **succeeds** |
| `git diff --check` | **clean, no output** |
| Formatter / linter / type checker | **absent, and reported as absent rather than claimed.** Re-verified for this remediation: there is no `black`, `ruff`, `flake8`, `mypy`, `pyright` or `isort` executable in either virtualenv, and no `pyproject.toml`, `setup.cfg`, `.flake8` or `.ruff.toml` exists. Introducing one would be a drive-by dependency change this remediation is not authorized to make |

**PostgreSQL evidence is present, not skipped.** Every case above ran against the
real local `freedom_test` database over its Unix-domain socket, through the
suite's own `assert_disposable_target` / `verify_connected_unix_socket_target`
guards. Nothing in this section rests on a run with `TEST_DATABASE_URL` unset,
and no test in the new module is skippable without it — the module is
`pytest.mark.database` and its fixtures resolve the disposable URL or fail.

**Checks that could not be run:** the staging-class ones, unchanged and still
open (RAID I-06). TC-PERF-01/02/03, TC-LIM-02, TC-SEC-07's browser half and
TC-OPS-01…05 remain unrun because staging does not exist. In particular, **the
rollback procedure in `docs/operations/web-portal.md` §3.6 has not been rehearsed
against a staging deployment** — the migration's half of it is tested here, but
the worker-shutdown and version-ordering half is documented rather than
exercised. A-05 is unchanged.

### 14.7.3 Diff inspection

- **No secret, credential, token, real Discord snowflake, real guild id, real
  Actor name or production identifier** appears in any changed file. `.env`,
  `yt-cookies.txt` and every credential file were never read, printed or
  modified. The only snowflakes anywhere are the synthetic
  `9000000000000000xx` values `tests/web_fixtures.py` has always used, and the
  only Actor data is the synthetic Phase 2 bundle.
- **No unrelated edit.** The files this remediation changed are exactly:
  `migrations/versions/0013_effect_publication_recovery.py`, `tests/conftest.py`,
  `tests/web/test_migration_0013_round_trip.py` (docstring only),
  the new `tests/web/test_migration_0013_rollback_boundary.py`, and the eight
  controlled documents listed in §14.8. Every other modified file in
  `git status` was already modified by §12 and §13 and was not touched here.
- **No contract weakened and no test relaxed or removed.** The only production
  change adds a refusal. `test_migration_0013_round_trip.py` keeps all four of
  its cases and all of its assertions; what changed is its docstring, which now
  states the scope the review found being over-read.
- **No log line added**, no new audit event, no new route, no new parameter and
  no new configuration variable.
- **The pre-existing stash** `stash@{0}: On main: temp before rebase` was never
  inspected, applied, dropped or modified. Nothing was committed, pushed or
  deployed. No live Discord, Google, Foundry or production service was contacted,
  and no real Actor, player, guild or credential data was used.

### 14.7.4 Security, integrity and runtime-role implications

- **A destructive DDL path that ran silently now refuses.** `downgrade 0012` on a
  database with committed effects previously succeeded and left the database
  unable to return to head. It now stops before the first `DROP`. That is a
  strengthening; nothing was relaxed to achieve it.
- **The offline path is no longer weaker than the online one.** A generated
  `--sql` downgrade script previously carried no guard at all. It now carries the
  same two counts as an executable block that raises on the server that runs it.
- **Refusals report counts, never rows.** No job id, request key, account,
  requester, Actor name or artifact content appears in either message (N-25).
- **No grant, role or privilege changed.** The guard runs as whoever runs Alembic
  — the schema owner — and reads `reconciliation_jobs`, which that role already
  reads. The runtime role is untouched and still holds no `DELETE` on
  `reconciliation_jobs`; `tests/test_runtime_grants.py` and
  `tests/web/test_p3_2_runtime_grants_and_bounds.py` pass unchanged.
- **The disposable-database reset in `tests/conftest.py` is test-only and
  guarded.** It runs inside the session fixture that already validates the target
  is the local disposable `freedom_test` over a Unix-domain socket, immediately
  before `alembic downgrade base` drops every table anyway. It is unreachable
  from the application, and nothing in `application/`, `adapters/` or `tools/`
  can perform it.
- **No new caller-reachable path exists.** No route, form, parameter or command
  reaches the new code; it runs only inside `alembic downgrade`.

## 14.8 Controlled documents updated

| Document | Change |
|---|---|
| `docs/review/phase-3-p3-3-submission.md` | §13.4 marked superseded, with the false sentences struck rather than deleted; this §14 added |
| `docs/operations/web-portal.md` | **New §3.6, "Migration 0013 rollback boundary"** — the boundary, its ratification status, the preflight query, the schema/application compatibility matrix, worker shutdown and version ordering, the recovery procedure when a downgrade is refused, what to do when a *re-upgrade* is refused, and retry/crash behaviour |
| `docs/contracts/phase-3-logical-schema.md` | `effect_result_accompanies_the_fence` gains its **migration precondition**: the constraint is also what a downgrade must not leave unsatisfiable, and `0013`'s `downgrade()` refuses while any **retained** job records a committed effect (wording corrected 2026-08-19; see §16.1) |
| `docs/contracts/phase-3-state-machines.md` | SM-05's effect-publication-recovery subsection gains the paragraph on why a schema downgrade cannot pass through the `running → completed` recovery transition, and why the answer is a refusal rather than a state-machine change. **No transition, state or exception is added** |
| `docs/contracts/phase-3-test-traceability.md` | **New §21.4c**, TC-MIG-24…TC-MIG-30; TC-MIG-23's scope corrected to empty-schema evidence; header amendment note |
| `docs/project-management/change-log.md` | **`C-P3.3-D`** |
| `docs/project-management/raid-register.md` | **I-18** opened and closed; **RR-19** recorded; **D-09** opened |
| `docs/project-management/status.md` | Fifteenth update |

## 14.9 What remains open, and what is not mine to close

**Peter's decisions are unchanged and untouched here:** RAID **I-11**
(`snapshot_folder_selections`) and the **R-41 versus SM-05** controlled amendment.
Neither is resolved by this remediation and neither was reached for.

**One new decision is requested:** RAID **D-09** — ratification of the
operational rollback boundary (change-log `C-P3.3-D`). It was deliberately not
self-approved. The refusal is implemented; the operational consequence is
proposed.

**One design is presented and not built:** the sidecar object that would make a
data-bearing downgrade genuinely reversible (§14.2). It is a material new schema
object with new ownership and retention rules, so it is presented for maintainer
approval rather than implemented.

**The §13 items are unchanged and still awaiting the same ratification:** the
SM-05 amendment of `C-P3.3-C`, `EFFECT_RECOVERY_LIMIT = 20`,
`EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` and the retention sweep's
`MAX_LIMIT = 10 000`.

**Residual risks:** RR-16 remains withdrawn; RR-17 and RR-18 are unchanged;
**RR-19 is new** — while a committed effect is retained there is no supported schema
rollback and no supported application version below the remediated one, so a
defect found after the first production apply must be fixed by roll-forward.

**Staging gaps are unchanged and still open** (RAID I-06), and §14.7.2 names the
one this remediation adds to the list: the operational half of §3.6 — worker
shutdown, version ordering, and a rehearsed restore — is documented rather than
exercised, because staging does not exist.

## 14.10 What is requested

**An independent implementation re-review and a separate security-focused
re-review**, of this section and of the code it describes.

**P3.G3 is not closed and is not claimed closed.** It remains open until this
migration finding is accepted as fixed, the PostgreSQL evidence above is
independently re-run, D-09 is recorded, and the outstanding maintainer decisions
from §13 are recorded. **P3.4 has not started.** HEAD is `c318231`, every change
is uncommitted, and the pre-existing stash was never inspected, applied, dropped
or modified.


---

## 15. Second migration-rollback remediation (2026-08-18)

The second independent re-review of §14 found one blocking concurrency defect
(F1) and two major contract/evidence defects (F2, F3). All three are fixed here.
**P3.G3 remains open.**

### 15.1 F1 — the downgrade precondition raced the worker

**The unsafe interleaving.** `_refuse_a_downgrade_that_cannot_be_undone()` ran an
ordinary `SELECT`, returned on a zero count, and only then let the first `ALTER
TABLE` queue for its DDL lock:

1. a worker transaction is applying an import and has not committed its fence;
2. the guard's `SELECT` runs under its own MVCC snapshot and sees zero;
3. the worker commits `effect_committed_at` **and** `effect_result`;
4. the first `ALTER TABLE` is granted its lock *after* that commit;
5. `effect_result` is dropped; and
6. the database holds an unpublishable, un-re-upgradeable committed effect.

**The lock ordering that now prevents it.** `LOCK TABLE reconciliation_jobs IN
ACCESS EXCLUSIVE MODE` is issued on Alembic's own connection **before** the
snapshot the count uses, and is released only when the migration transaction
commits or rolls back:

```text
acquire ACCESS EXCLUSIVE  →  count  →  refuse or drop all three  →  COMMIT/ROLLBACK
```

**Mode, conflicts, wait and deadlock behaviour.** `ACCESS EXCLUSIVE` conflicts
with every PostgreSQL lock mode, so it excludes `ROW EXCLUSIVE`
(`INSERT`/`UPDATE`/`DELETE`, and therefore the commit fence's `UPDATE`), `ROW
SHARE` (`SELECT … FOR UPDATE`) and everything else able to create or change a
committed-effect row. A writer already in flight holds `ROW EXCLUSIVE` until it
ends, so the `LOCK TABLE` waits for it and the count therefore sees its committed
row; a writer arriving later conflicts with the lock — and, while it is still
pending, with the *request*, because PostgreSQL queues a conflicting requester
behind an existing waiter — so it cannot commit a fence until the migration
finishes. It is also the mode the three `ALTER TABLE` statements require anyway,
so it adds no concurrency cost and removes the lock **upgrade** the previous
shape performed silently, which is the classic deadlock pair. No `lock_timeout`
is set: an operator wants the migration to wait for a draining worker, and the
deadlock detector still resolves a genuine cycle. Advisory locks were rejected —
workers take none. Transaction lifetime is one Alembic transaction.

**Online and offline both hold the lock through the drops.** `migrations/env.py`
runs the offline migration inside `context.begin_transaction()`, and PostgreSQL's
dialect is transactional, so the generated script is framed `BEGIN; … COMMIT;`
with the lock taken immediately after `BEGIN` and every `DROP` inside it. This is
asserted positionally rather than by keyword — one `BEGIN;`, one `COMMIT;`, and
no transaction control between the lock and the last drop — and executed with
`psql` against the disposable database in a concurrency case.

### 15.2 F2 — the retention-aware boundary

The exact predicate the guard enforces, now stated everywhere it was misstated:

> **Downgrade below 0013 is refused while any retained reconciliation job records
> a committed effect. It becomes available only when no such job exists; in
> normal operation that means either no apply has committed, or every completed
> committed-effect job and its result has been removed by the approved N-24
> retention process and no committed-but-unpublished job remains.**

Retained and retired jobs differ because what a downgrade destroys is a
*surviving* `effect_result`. Once N-24 has removed the completed job and its
result, there is nothing for the drop to take and nothing for the re-upgrade's
`effect_result_accompanies_the_fence` to refuse. The immutable `snapshot_imports`
receipt and the append-only audit history that retention preserves obstruct
neither direction — no constraint in this revision reads them and no column of
theirs is added or dropped — proved by driving `0013 → 0012 → 0013` after a real
retention sweep and comparing the catalogue and every surviving row on `xmin`.

Retention never removes a running job, so a committed-but-unpublished effect
blocks the downgrade at any age; that is asserted with a sweep run ten years into
the future. Manual deletion and early or shortened retention are named in the
runbook as unsupported rollback routes. **No permanent marker, sidecar,
tombstone, new retention rule or other schema object was added**, and no
eligibility, audit or operator control was changed: the migration's DDL is
unchanged and `tools/job_retention.py` is untouched by this remediation. The
operational consequence remains a proposal awaiting Peter/Acceptance Authority
ratification (RAID **D-09**, change-log **C-P3.3-E**).

### 15.3 F3 — hermetic fixtures

`tests/web/conftest.py` gained one session-scoped `bounded_ancestors` fixture
(`TrustedAncestors(ceiling=tmp_path_factory.getbasetemp())`), and
`tests/web/p3_3_fixtures.py` one `open_artifact_store()` that injects it and
**asserts the ceiling really is an ancestor of the artifact root**, so a bad
fixture cannot silently fall back to walking `/`. The worker, effect-fence and
effect-recovery suites — and the `WorkerComposition` each builds — now use it.
Production validation is unchanged: `FilesystemArtifactStore(...).ancestors.ceiling`
is still `None` by default, asserted by a control case in the rollback module and
by `tests/test_artifact_store.py`.

### 15.4 Pre-fix and post-fix evidence, separately

The two defects have **separate** before/after evidence; neither is presented as
the other's red phase.

**Fixture portability, pre-fix** (`TMPDIR=/opt/discord-bots/tmp-review`, whose
`/opt/discord-bots` is group-writable without the sticky bit):

```text
TMPDIR=/opt/discord-bots/tmp-review TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
./venv-web/bin/python -m pytest -q \
tests/web/test_migration_0013_rollback_boundary.py \
tests/web/test_migration_0013_round_trip.py -rs

6 passed, 7 errors        (all seven ArtifactStorageError root_ancestor_untrusted in setup)
```

**Fixture portability, post-fix**, same command: `13 passed`. The three P3.3
suites under the same `TMPDIR`: `52 passed`.

**Concurrency, pre-fix** — the new regression run against the guard with only its
`LOCK TABLE` statement removed:

```text
E  AssertionError: the migration was not waiting at the guard's lock but at
   'ALTER TABLE reconciliation_jobs DROP CONSTRAINT
    ck_reconciliation_jobs_committed_effect_is_never_denied'
   — which is the pre-fix interleaving: the count has already run under its own
   snapshot and only the DDL is queued behind the worker

1 failed, 10 deselected
```

**Post-fix:** `tests/web/test_migration_0013_rollback_boundary.py` — **17 passed**.

**Full runs** (all with `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'`):

> **SUPERSEDED, and it was wrong.** The 2026-08-19 independent review found this
> table internally impossible: it reports **17 passed** for the rollback module
> alone and **15 passed** for that module *plus*
> `test_migration_0013_round_trip.py`, and a superset cannot be smaller. Earlier
> results had been combined with later test additions and presented as current
> exact evidence. **Every row below is withdrawn as current evidence.** The
> rerun, exact, internally consistent final-tree results are §16.4; the pre-fix
> results above this banner are genuine historical results of the §15 tree and
> are kept as such.

| Command | Result (withdrawn — see §16.4) |
|---|---|
| `pytest -q tests/web/test_migration_0013_rollback_boundary.py` | 17 passed |
| `pytest -q tests/web/test_migration_0013_rollback_boundary.py tests/web/test_migration_0013_round_trip.py` | 15 passed |
| `pytest -q tests/web/test_p3_3_worker.py tests/web/test_p3_3_effect_fence.py tests/web/test_p3_3_effect_recovery.py` | 52 passed |
| `./venv-web/bin/python -m pytest -q tests/web` | 1428 passed, 80 skipped |
| `./venv/bin/python -m pytest -q tests` | 2293 passed |
| `pytest -q tests/test_database_postgresql.py -k migration_matches_table_metadata` (`alembic check`) | 1 passed |
| `pytest -q tests/web/test_p3_2_runtime_grants_and_bounds.py tests/test_migration_safety.py` | 69 passed |
| `python -m compileall` on every changed Python file | clean |
| `git diff --check` | clean |

**Checks not run:** no formatter, linter or type checker is installed or
configured in this repository — `requirements-dev.txt` carries only `pytest` and
`pytest-asyncio`, and there is no `pyproject.toml`, `setup.cfg` or `.flake8`.

### 15.5 Compatibility, security and residual risk

No production code changed: the diff is the migration's guard, three test suites,
two test-support modules and the controlled documents. Application/worker/schema
compatibility and the operational shutdown order in
`docs/operations/web-portal.md` §3.6 are unchanged — stop every worker, confirm
no lease is live, run the preflight, then downgrade. Security: the lock is taken
by the schema owner running a migration, not by any runtime role; the restricted
runtime role gains nothing and still holds no `DELETE` on `reconciliation_jobs`.
Availability: the downgrade now waits for a draining worker instead of racing it
(RR-24), which is visible in `pg_locks`/`pg_stat_activity`. Integrity: the window
in which a committed effect could be silently destroyed is closed.

**Outstanding:** Peter/Acceptance Authority ratification of the retention-aware
operational boundary (D-09, C-P3.3-E). **Requested:** another independent
implementation re-review and a separate security-focused re-review. P3.G3 is
**not** closed.

---

## 16. Third migration-rollback correction (2026-08-19)

The independent review of §15 found **three major defects and no new blocking
defect**. All three are corrected here. **No production code, schema object,
constraint, grant, application statement or worker statement changed**: the
migration's DDL, its guard and the SQL it emits are byte-for-byte what §15 left.
The diff is one new test case, one renamed and re-scoped test case, two
test-cleanup corrections, and controlled-document wording.

**P3.G3 remains open. P3.4 has not begun.** HEAD is `c318231`, every change is
uncommitted, and the pre-existing stash `stash@{0}: On main: temp before rebase`
was never inspected, applied, dropped or modified.

### 16.1 The rollback predicate, and the four database states

This is the rule. It is what `migrations/versions/0013_effect_publication_recovery.py`
enforces, and every normative statement in every controlled document now says it:

> **Downgrade below 0013 is refused while any *retained* reconciliation job
> records a committed effect. It becomes available only when no such job exists;
> in normal operation that means either no apply has committed, or every
> completed committed-effect job and its result has been removed by the approved
> N-24 retention process and no committed-but-unpublished job remains.**

It is a condition on **rows that survive**, not a record of an event. The guard
counts surviving rows because surviving rows are exactly what a `DROP COLUMN` can
destroy; nothing in this schema records "an apply once committed", and no marker,
sidecar or tombstone was added to make such a record exist.

The four states it admits, and the case that drives each:

| # | The database holds | Downgrade below 0013 | Driven by |
|---|---|---|---|
| 1 | an unused database that **never committed an effect** | **Available**, and genuinely reversible with realistic rows | `…succeeds_below_the_boundary_with_realistic_rows` (TC-MIG-28) |
| 2 | a **retained completed** committed-effect job | **Refused** before any schema change. Its `effect_result` is still there to destroy, and the re-upgrade would refuse on the row | `…refuses_a_published_committed_effect` (TC-MIG-24) |
| 3 | a **retained committed-but-unpublished** job | **Refused**, and **retention cannot remove it at any age** — it is `running`, never terminal, so it is never eligible. This is the population a downgrade would hurt worst: `effect_result` is the only record of what the publication owes | `…refuses_a_committed_but_unpublished_effect` (TC-MIG-25), `…an_unpublished_effect_blocks_the_downgrade_at_any_age` (TC-MIG-36), asserted with a sweep ten years in the future |
| 4 | approved **N-24 retention removed every completed job/result presentation row**, while `snapshot_imports` and the append-only audit history are preserved | **Available again**, provided no unpublished committed-effect job survives; `0013 → 0012 → 0013` is exact, catalogue and every surviving row compared on `xmin` | `…approved_retention_reopens_the_boundary_and_the_round_trip_is_exact` (TC-MIG-35) |

**Publication does not by itself reopen the boundary.** Publishing an outstanding
effect moves a job from state 3 to state 2 — which is the right thing to do, and
the only route into the population retention can ever remove — but a retained
completed job refuses the downgrade exactly as an unpublished one does. The
boundary reopens through retention on its normal schedule and no other way.

**Retention is not a rollback technique.** Manual deletion, truncation of
production history, a shortened retention period and an early sweep are named as
unsupported in `docs/operations/web-portal.md` §3.6 and in the refusal message
itself. N-24's eligibility rule, 30-day age, operator command and audit event are
unchanged by this correction, and `tools/job_retention.py` was not touched. The
`TRUNCATE`-and-retry remedy the migration offers is scoped, in the message and in
the runbook, to **a disposable development database with no history worth
keeping**. The disposable-test reset in `tests/conftest.py` is unchanged, is
reachable from no application code, and runs only inside the session fixture that
has already proved the target is the local disposable `freedom_test` over a
Unix-domain socket.

**The policy remains a proposal.** Ratification of the operational consequence is
RAID **D-09**, change-log `C-P3.3-D`, `C-P3.3-E` and the new `C-P3.3-F`. It is not
self-approved here and **P3.G3 is not claimed closed**.

### 16.2 F1 — every corrected stale statement, by document

The predicate had been corrected in the migration and in the runbook headline by
§15, and left standing as present-tense prose elsewhere. A superseded block in one
section does not cure contradictory prose in later answers, evidence tables,
status records or contracts, and a reader must not have to infer that a later
section silently overrides an earlier one. Every occurrence below was searched for
by the handover's own list of variants — `first committed effect`, `first apply`,
`once any committed effect exists`, `after a committed effect`, `forever`,
`permanent`, and claims that publication cannot reopen the boundary.

| Document | Location | Was | Now |
|---|---|---|---|
| `docs/review/phase-3-p3-3-submission.md` | §14.2 opening block | A broken-markup strikethrough pointing at another document for the corrected rule | An unmistakably labelled **SUPERSEDED FINDING**, quoting the dead wording, immediately followed by the corrected predicate in full and a pointer to §16.1. The sentence after it now says `downgrade()` counts the **retained** committed effects |
| " | §14.3, "Is downgrade supported…" | "after a committed effect exists?** No." | Asks the retained-job question and answers it with the predicate plus a pointer to the four states |
| " | §14.3, "how is the information preserved?" | "Not applicable — it is not supported" | States where it *is* supported there is nothing to preserve, because availability and the absence of a surviving `effect_result` are the same condition |
| " | §14.3, "How is an unpublished committed effect handled?" | "does not make the downgrade available, because the committed effect is still recorded" | Publication moves the job into the only retention-eligible population; the boundary reopens through approved retention and never immediately, and shortening or hand-running retention is not a supported route |
| " | §14.3, "The exact operational rollback boundary" | "The first commit of an apply effect at revision `0013`. Before it… After it…" | "Not an event: a **condition on retained rows**", with both directions and the never-eligible unpublished case |
| " | §14.8 controlled-document table | "the constraint is also what closes schema rollback, and `0013`'s `downgrade()` refuses once any committed effect exists" | "what a downgrade must not leave unsatisfiable", refusing while any **retained** job records one |
| `docs/operations/web-portal.md` | §3.6, the quoted refusal | Quoted a message text the migration no longer raises: "not available once an apply has committed an effect" | Quotes the message the migration actually raises, retained-row predicate and unsupported-route sentence included |
| " | §3.6, recovery step 2 | "This does not make the downgrade available — the committed effects are still recorded" | Explains that publication moves the job to `completed` and still refuses, that retention is what reopens the boundary, and that shortening the period, sweeping early or deleting rows by hand are **not** supported |
| " | §3.6, "The decision is taken under a lock" | Named no evidence | Names all three concurrency cases and says which condition each one holds |
| `docs/contracts/phase-3-logical-schema.md` | `committed_effect_is_never_denied`, migration precondition | "This constraint is also what closes schema rollback… refuses… once any reconciliation job records a committed import effect" | The retained-row predicate in full, with the never-eligible unpublished case, the retention-is-not-a-technique sentence, and a labelled note that the old wording is dead |
| `docs/contracts/phase-3-state-machines.md` | SM-05, effect-publication recovery | "refuses before any schema change **once any** reconciliation job records a committed import effect… rollback is simply not available past that point" | "while any *retained*…", with how each population leaves the refusing state, and the correction dated |
| `docs/contracts/phase-3-test-traceability.md` | TC-MIG-32 | Named and described for the held-lock condition | Re-scoped to lock-queue fairness with an explicit "makes **no** claim about a granted lock", and pointed at TC-MIG-37 |
| " | §21.4c, header amendment note, pre-fix evidence note | — | TC-MIG-37 added; the 2026-08-19 amendment note added; TC-MIG-32's separate pre-fix evidence recorded; TC-MIG-37's scope limits stated |
| `docs/project-management/change-log.md` | `C-P3.3-D`, "Contract amendment sought" | "Past the first committed apply effect…" | The retained-row predicate, with a dated inline correction note pointing at `C-P3.3-E` and `C-P3.3-F` |
| " | new `C-P3.3-F` | — | The whole correction, its three findings, the alternatives rejected for each, and the explicit "nothing is accepted" |
| `docs/project-management/raid-register.md` | `I-18` closure text | "refuses before any schema change **once any job records** a committed import effect" | The retained-row predicate with the reopening condition and a dated note that the closure wording was corrected |
| " | `RR-19` | "Past the first committed apply effect there is no supported schema rollback…" | "While any **retained** reconciliation job records a committed apply effect…", with the reopening condition, the never-eligible unpublished case, and retention named as not a rollback technique |
| " | `D-09` | Named only `C-P3.3-D` | Names `C-P3.3-D`, `C-P3.3-E` and `C-P3.3-F` |
| `docs/project-management/status.md` | fifteenth update, contract-amendment bullet | "past the first committed apply effect" | The retained-row predicate with the reopening condition and a dated correction note |
| " | header and new seventeenth update | — | Status date 2026-08-19; the seventeenth update records F1, F2 and F3 |
| `migrations/versions/0013_effect_publication_recovery.py` | module docstring, `DOWNGRADE_LOCK` note, `OFFLINE_DOWNGRADE_GUARD`, `_refuse_a_downgrade_that_cannot_be_undone`, both refusal messages | Already corrected by §15 | **Unchanged — verified, not assumed.** Every normative sentence in the revision already states the retained-row predicate, names both populations, says retention can never remove a `running` job, and names hand-deletion and shortened retention as unsupported. The only "first apply" text in the file is inside a paragraph explicitly labelled as the wording the second remediation *corrected* |
| `tests/web/test_migration_0013_rollback_boundary.py` | module docstring | "schema downgrade below 0013 is refused… **once any** reconciliation job records a committed import effect", and "rollback past the first apply is application rollback/roll-forward" | The predicate in full, the four states with the case that drives each, an explicit note that the old wording is superseded, and the retention-is-not-a-technique sentence |
| " | `…succeeds_below_the_boundary_with_realistic_rows` docstring | "The boundary is the first committed effect, not the first row." | "State 1: rows are not the boundary; a *retained committed effect* is." |
| " | the case table | "downgrade **is** supported until the first committed effect" | "while no retained job records a committed effect"; the table also gained rows for the retention, concurrency and queue-fairness cases, which it had never listed |

**Nothing was added to make the old wording true.** No permanent marker, sidecar,
tombstone, retention-policy change or schema object was introduced — see §16.5.

### 16.3 F2 — the held-lock condition, proved from a granted lock

**What the existing case actually proved.** In
`…a_fence_writer_arriving_after_the_lock_cannot_commit_until_it_finishes`, an
ordinary reader held `ACCESS SHARE`, so the migration's `LOCK TABLE … ACCESS
EXCLUSIVE` was **never granted**; a later fence writer queued behind that pending
request; releasing the reader let the migration reach its refusal first. That is
PostgreSQL lock-queue fairness — *a later requester cannot overtake an existing
waiter* — and it is a real property the guard depends on. It is **not** the
condition the name claimed, and its own docstring said the migration was
ungranted while later prose said it "holds the decision". The two were being
presented as one.

**What was done about it.** The case is **kept**, **renamed**
`test_a_fence_writer_arriving_behind_a_pending_lock_request_cannot_overtake_it`,
and its docstring rewritten to state the queue-fairness property, to say
explicitly that the migration's request is ungranted throughout, and to point at
the new case for the other condition. Traceability follows: **TC-MIG-32 is
re-scoped** and now says it makes no claim about a granted lock.

**The new regression.**
`test_a_fence_writer_starting_under_the_held_lock_cannot_commit_until_it_ends`
(**TC-MIG-37**) establishes all six required conditions from observable database
state, in order, with no sleep used as proof and no unbounded wait — every wait is
a bounded poll (60 s ceiling, 50 ms interval) of `pg_locks`/`pg_stat_activity`
scoped to `reconciliation_jobs`, and a poll that times out fails with what it last
saw.

**The coordination, exactly.** The revision has no point at which it can be
observed holding its lock, and must not grow one: a production pause hook is
forbidden, and a revision carrying one is not the program a deployment runs. So
the hold is taken **from PostgreSQL, outside Alembic**. Alembic updates its own
`alembic_version` row *inside the migration transaction*, after the revision body
has run, so one `SELECT version_num FROM alembic_version FOR UPDATE` held by the
test stops the production child exactly there:

```text
  test:       BEGIN; SELECT … FROM alembic_version FOR UPDATE     (row held)
  migration:  LOCK TABLE reconciliation_jobs IN ACCESS EXCLUSIVE MODE   <- GRANTED, held
              count -> (0, 0) -> DROP CONSTRAINT ×2, DROP COLUMN
              UPDATE alembic_version SET version_num='0012' …      <- waits here
              (COMMIT never reached)
  test:       observe the granted lock          (condition 1, 2)
  writer:     start; production hold_for_effect UPDATE             <- ROW EXCLUSIVE, ungranted
  test:       observe the queued writer, re-observe the same holder (condition 3, 4)
  test:       pg_cancel_backend(migration pid)  -> ROLLBACK        (condition 5)
  writer:     proceeds and commits the fence                       (condition 6)
```

The database is deliberately **below the boundary** when the guard counts, so the
downgrade proceeds past its refusal into the drops and reaches the hold point. The
migration finishes by **rollback**, which is the same finish its own refusal
produces and which is what leaves the schema intact for the writer to commit
against; the three dropped objects being restored is asserted, not assumed.

**Nothing production-side changes.** No file under `migrations/`, `application/`,
`adapters/`, `domain/` or `tools/` is touched by this case. The revision is the
production revision, run through the suite's guarded `start_alembic` subprocess
exactly as `run_alembic` runs a deployment; the emitted SQL is unchanged; the
writer is the production `SqlAlchemyReconciliationJobLeaseRepository.hold_for_effect`
statement for an apply job it has really claimed, beside the `snapshot_imports`
receipt the recovery path reads. `CREATE EVENT TRIGGER` was considered as the
alternative hold and rejected: it requires superuser, and the test role
deliberately is not one (`usesuper = f`).

**Amended 2026-08-19 by the fourth correction (§17). The transcript below is
illustrative, not the evidence.** The independent review of this section found
that what the transcript shows — OBSERVED-2 being *the intended writer's* backend
executing *the fence* — is not what the committed assertions enforced. The case
polled every ungranted `RowExclusiveLock` on `reconciliation_jobs` and asserted
only that the migration's pid was absent, so an unrelated queued session could
satisfy it while the intended writer had not yet requested its lock. **That is a
defect in the assertion, not a flake**; on a quiet database the intended writer
normally wins the race, which is why it passed. §17 replaces the assertions with
ones that bind the observation to the writer's own backend and transaction, and
those committed assertions — not the removed `print()` calls — are now the primary
evidence for conditions 3 and 4. The transcript is retained below because it
records what a real run looked like, and it is labelled accordingly.

**The observed PostgreSQL lock states**, from an instrumented run of this exact
case (three `print()` calls, since removed; the file was restored byte-for-byte
and the module rerun — see §16.4):

```text
OBSERVED-1  the granted lock, before the writer exists
  pid                 995462
  granted             True
  virtualtransaction  5/48623
  wait_event_type     Lock
  state               active
  xact_start          2026-08-19 00:28:35.972437+00:00
  query               UPDATE alembic_version SET version_num='0012'
                      WHERE alembic_version.version_num = '0013'

OBSERVED-2  the writer, started only after OBSERVED-1, ungranted
  pid                 995461      (≠ 995462: a different backend)
  mode                RowExclusiveLock, NOT granted
  wait_event_type     Lock
  query               UPDATE reconciliation_jobs SET
                          effect_committed_at = $1,
                          effect_result = $2::JSONB,
                          version = version + 1
                      WHERE id = $3 AND lease_owner = $4
                        AND state = 'running'
                        AND cancel_requested_at IS NULL
                        AND effect_committed_at IS NULL
                                          -- the production commit fence, verbatim

OBSERVED-3  re-observed while the writer waits: identical holder
  pid 995462 | virtualtransaction 5/48623 | xact_start 2026-08-19 00:28:35.972437+00:00
              -- same backend, same transaction: no COMMIT or other boundary
                 released the lock between OBSERVED-1 and OBSERVED-2

OBSERVED-4  after the migration transaction ends
  migration exit code  1   (QueryCanceled -> ROLLBACK)
  fence outcome        {'held': True}   -- committed only afterwards
```

After the run: `alembic_version` is `0013`, all three revision objects are back,
the catalogue fingerprint equals the pre-run fingerprint, `committed_effects()` is
`(0, 1)` — the late fence, which the migration provably never counted — and
`effect_result` holds the payload the fence wrote.

**Scope stated exactly, so this case is not read for more than it is.** It does
**not** bind the granted lock to the guard's own `LOCK TABLE`: by the hold point
the three `ALTER TABLE` statements have run and each requires `ACCESS EXCLUSIVE`
on its own. Verified rather than assumed — with `connection.execute(sa.text(DOWNGRADE_LOCK))`
removed from `_refuse_a_downgrade_that_cannot_be_undone()`, this case still
passes, while the two cases that *do* hold the lock's placement fail:

```text
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest -q \
  tests/web/test_migration_0013_rollback_boundary.py \
  -k "in_flight_effect or under_the_held_lock or behind_a_pending_lock" -rf

FAILED …::test_a_downgrade_started_during_an_in_flight_effect_refuses_after_it_commits
FAILED …::test_a_fence_writer_arriving_behind_a_pending_lock_request_cannot_overtake_it
2 failed, 1 passed, 15 deselected in 64.01s
```

The revision was restored byte-for-byte immediately afterwards
(`sha256 9ca19bca0423217f0f3057b41bdcbb4667d3f0fc40d298138380dbbd76cc9cc1`), and
every count in §16.4 was taken after that restoration. That the lock is taken
**before the count** is TC-MIG-31's claim, and TC-MIG-31 is one of the two cases
that fail above.

**Cleanup.** Both concurrency cases release every connection, thread and process
on every path. Two cleanup defects found while running the falsification are
fixed: each `finally` now joins the writer thread only `if writer.is_alive()`,
because an assertion failing before `writer.start()` previously raised
`RuntimeError: cannot join thread before it is started` from the cleanup and hid
the real failure — which is exactly what happened in the falsification run above.
The new case kills the migration child **before** releasing the `alembic_version`
row, because a migration *released* rather than *ended* would commit the drops the
assertions assume were undone. `head_restored` returns the disposable database to
head however the case ended.

**Also retained and rerun**, as required, all against the final tree (§16.4): the
in-flight-writer versus online-downgrade regression (TC-MIG-31), offline-script
transaction framing and its concurrency execution (TC-MIG-33, TC-MIG-34),
retention reopening and unpublished-effect blocking (TC-MIG-35, TC-MIG-36), and
fixture portability below a deliberately untrusted parent (TC-MIG-36's third case
plus the production-default control).

### 16.4 F3 — exact final-tree evidence

§15.4 reported **17 passed** for the rollback module alone and **15 passed** for
that module plus `test_migration_0013_round_trip.py`. Both cannot describe one
tree: a superset cannot be smaller. Historical results had been combined with
later test additions and presented as current exact evidence. Every required
command below was rerun against the final corrected tree, and each row carries its
literal invocation and its exact count. **Nothing is derived, no earlier count is
reused, and no partial run is reported as a full one.**

All commands were run from `/opt/discord-bots/freedom-bot` with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported, **serially** —
the disposable `freedom_test` database is shared by both virtualenvs and running
the suites concurrently produces dozens of spurious failures.

| # | Command | Exact result |
|---|---|---|
| 1 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -rs` | **18 passed** in 15.12s — the concurrency, offline-SQL, retention-boundary and fixture-portability regressions all live here. **No skips**; the module is `pytest.mark.database` and its fixtures resolve the disposable URL or fail |
| 2 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py tests/web/test_migration_0013_round_trip.py -rs` | **22 passed** in 17.33s (18 + 4) |
| 3 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0011_round_trip.py tests/web/test_migration_0012_round_trip.py tests/web/test_migration_0013_round_trip.py tests/web/test_migration_0013_rollback_boundary.py -rs` | **29 passed** in 20.06s — all `0011`, `0012` and `0013` migration tests |
| 3a | the four modules individually, so the arithmetic above is checkable | `0011`: **4 passed**; `0012`: **3 passed**; `0013` round trip: **4 passed**; `0013` rollback boundary: **18 passed**. 4 + 3 + 4 + 18 = **29** |
| 4 | `./venv-web/bin/python -m pytest -q tests/web/test_p3_3_jobs.py tests/web/test_p3_3_worker.py tests/web/test_p3_3_effect_fence.py tests/web/test_p3_3_effect_recovery.py tests/web/test_p3_3_job_retention.py -rs` | **109 passed** in 7.33s — every P3.3 jobs, worker, effect-fence, effect-recovery and retention test |
| 5 | `./venv-web/bin/python -m pytest -q tests/web` | **1429 passed, 80 skipped** in 92.61s. The 80 skips are the two permission-matrix modules' permitted cells (54 + 26), which the per-route success cases assert; the reason strings are printed by the run. **+1 on §15's 1428**, which is exactly TC-MIG-37 |
| 6 | `./venv/bin/python -m pytest -q` | **2293 passed** in 133.23s — the full bot suite, unchanged |
| 7 | `./venv-web/bin/python -m pytest -q tests/test_database_postgresql.py::test_migration_matches_table_metadata tests/test_database_postgresql.py::test_migrations_apply_to_empty_postgresql_and_downgrade tests/test_runtime_grants.py tests/web/test_p3_2_runtime_grants_and_bounds.py tests/test_migration_safety.py` | **81 passed** in 5.39s — metadata parity (`alembic check`), the empty-database `base ↔ head` round trip, the effective runtime-grant tests and the migration-safety tests. **No grant changed** |
| 8 | `alembic downgrade base`, then `alembic upgrade head`, then `alembic check`, against the disposable database through the suite's own guarded environment | `downgrade base` rc **0**; `upgrade head` rc **0**; `check` rc **0**, output **"No new upgrade operations detected."**; `SELECT version_num FROM alembic_version` = **`0013`** |
| 9 | `alembic downgrade 0013:0012 --sql` | rc **0**. Statement order in the generated script: `BEGIN;` → `LOCK TABLE reconciliation_jobs IN ACCESS EXCLUSIVE MODE;` → `DO $rollback_boundary$ … RAISE EXCEPTION …` → `DROP CONSTRAINT ck_…_committed_effect_is_never_denied` → `DROP CONSTRAINT ck_…_effect_result_accompanies_the_fence` → `DROP COLUMN effect_result` → `COMMIT;`. `RAISE EXCEPTION` present. The positional assertions and the `psql` execution of this script are cases 33 and 34 inside command 1 |
| 10 | `./venv-web/bin/python -m compileall -q` on **every changed Python file** (54 files: `git diff --name-only` plus `git ls-files --others --exclude-standard`, filtered to `*.py`) | rc **0**, no output |
| 11 | `git diff --check` | rc **0**, **no output** |
| 12 | Formatter / linter / type checker | **None is installed or configured, and that is reported rather than claimed as a pass.** Re-verified for this correction: no `black`, `ruff`, `flake8`, `mypy`, `pyright`, `isort` or `pylint` executable exists in `./venv/bin` or `./venv-web/bin`, and there is no `pyproject.toml`, `setup.cfg`, `.flake8`, `.ruff.toml` or `tox.ini`. `requirements-dev.txt` carries only `pytest` and `pytest-asyncio`. Introducing one would be a drive-by dependency change this correction is not authorized to make |

**Historical results are kept separate and labelled.** §14.7.1's pre-fix
transcript (**8 failed, 1 passed**), §15.4's fixture-portability before/after
(**6 passed, 7 errors** → **13 passed**) and §15.4's concurrency pre-fix failure
are results of earlier trees and are **not** rewritten as though rerun. §15.4's
own post-fix table is superseded by the table above; the two counts it reported
for overlapping selections were the defect. The one falsification run performed
for this correction is in §16.3 and is labelled as such.

**PostgreSQL evidence is present, not skipped.** Every case above ran against the
real local `freedom_test` database over its Unix-domain socket, through the
suite's `assert_disposable_target` / `verify_connected_unix_socket_target` guards.
No result in this section rests on a run with `TEST_DATABASE_URL` unset, none is a
fixture setup failure, and no PostgreSQL concurrency test was skipped.

**Order of operations, stated so the "after the final edit" rule is checkable.**
The last edit to any file in this correction was a one-line tightening of an
assertion message in
`test_a_fence_writer_starting_under_the_held_lock_cannot_commit_until_it_ends`
(`granted["pid"] not in {queued pids}` rather than a list comparison). **Commands
1–7 and 10–11 were rerun after that edit**, and after every controlled-document
edit including this section, and produced exactly the counts in the table above.
Commands 8, 9 and 12 do not depend on the test tree and were run after the last
migration and documentation edit. `docs/operations/web-portal.md` is the only
documentation file any test opens, and it was edited before every run reported
here.

### 16.5 Diff inspection, and what was **not** added

- **No permanent marker, sidecar, tombstone, retention-policy change, production
  pause hook or hidden schema object was added.** The migration's DDL is unchanged
  and `alembic check` reports no metadata difference (command 8). `tools/job_retention.py`
  was not touched, and N-24's eligibility rule, 30-day age, operator command and
  audit event are unchanged.
- **No production file changed at all.** The diff of this correction is:
  `tests/web/test_migration_0013_rollback_boundary.py` (one new case, one renamed
  and re-documented case, two `finally`-block corrections, module docstring),
  `docs/operations/web-portal.md`, `docs/contracts/phase-3-logical-schema.md`,
  `docs/contracts/phase-3-state-machines.md`,
  `docs/contracts/phase-3-test-traceability.md`,
  `docs/project-management/change-log.md`,
  `docs/project-management/raid-register.md`,
  `docs/project-management/status.md` and this submission. Every other modified or
  untracked file in `git status` was already modified by §12–§15 and was not
  touched here.
- **No contract weakened and no test relaxed or removed.** The queue-fairness case
  keeps every assertion it had; what changed is its name and its documentation.
  `FilesystemArtifactStore`'s production default `ancestors.ceiling is None` is
  unchanged and still asserted by the control case; the online/offline downgrade
  guard and the artifact-store fixture remediation are untouched.
- **No secret, credential, token, real Discord snowflake, real guild id, real
  Actor name or production identifier** appears in any changed file. `.env`,
  `yt-cookies.txt` and every credential file were never read, printed or modified.
  The only snowflakes are the synthetic `9000000000000000xx` values and the only
  Actor data is the synthetic Phase 2 bundle. The observed transcript in §16.3
  contains backend pids and a virtual transaction id from the local disposable
  database and no data of any kind.
- **No log line, audit event, route, parameter or configuration variable added.**
- **`0011` and `0012` were not edited**, and neither was any other applied
  migration. `0013` — the still-unaccepted, uncommitted work already in this
  review slice — was edited only for the falsification in §16.3 and restored
  byte-for-byte, verified by checksum.
- **The pre-existing stash** `stash@{0}: On main: temp before rebase` was never
  inspected, applied, dropped or modified. Nothing was committed, pushed or
  deployed. No live Discord, Google, Foundry or production service was contacted,
  and no real Actor, player, guild or credential data was used.

### 16.6 Security, integrity, availability, runtime-role and deployment order

Unchanged from §15.5, because no production behaviour changed. Restated so the
security reviewer does not have to infer it:

- **Security.** No new caller-reachable path exists; nothing added here runs
  outside `pytest` and `alembic`. The lock is taken by the schema owner running a
  migration, never by a runtime role. Refusals still report counts, never rows
  (N-25). `pg_cancel_backend` is used only by the test, against a backend of its
  own role, in the disposable database; it appears in no production module.
- **Integrity.** The window in which a committed effect could be silently
  destroyed remains closed, and is now covered from both directions: the lock is
  taken before the count (TC-MIG-31), and a writer starting under the held lock
  cannot commit until the migration transaction ends (TC-MIG-37).
- **Availability.** Unchanged: the downgrade waits for a draining worker rather
  than racing it (**RR-24**), visible in `pg_locks`/`pg_stat_activity`. No
  `lock_timeout` is set and none was added.
- **Runtime role.** Untouched. It still holds no `DELETE` on
  `reconciliation_jobs`; `tests/test_runtime_grants.py` and
  `tests/web/test_p3_2_runtime_grants_and_bounds.py` pass unchanged (command 7),
  and `infra/postgresql/runtime-grants.sql.tmpl` was not edited.
- **Deployment order.** Unchanged and still `docs/operations/web-portal.md` §3.6:
  roll forward is **migrate then deploy**; roll back is **stop every worker,
  confirm no lease is live, run the preflight, downgrade, then deploy the older
  code**, and only while the preflight returns two zeros.

### 16.7 Checks unavailable or skipped, and why

- **Formatter, linter and type checker:** none installed or configured (command
  12). Reported as absent, not as passing.
- **Staging-class checks remain unrun** (RAID **I-06**, unchanged):
  TC-PERF-01/02/03, TC-LIM-02, TC-SEC-07's browser half and TC-OPS-01…05. In
  particular the **operational half of §3.6 — worker shutdown, version ordering
  and a rehearsed restore — is documented rather than exercised**, because staging
  does not exist. **A-05 is unchanged.**
- **The 80 skips in command 5** are the permission-matrix modules' permitted
  cells, asserted by the per-route success cases. They are the same 80 as in §15
  and are not concurrency or database skips.
- **No PostgreSQL concurrency test was skipped**, no command was run with
  `TEST_DATABASE_URL` unset, and no fixture setup failed.

### 16.8 Residual risks and the decision that is not mine

**The rollback policy remains a proposal.** Ratification of the retention-aware
operational boundary is RAID **D-09** and change-log `C-P3.3-D` / `C-P3.3-E` /
`C-P3.3-F`. It is **not** self-approved here, and **P3.G3 is not claimed closed**.

**Residual risks:** RR-16 remains withdrawn; RR-17 and RR-18 are unchanged;
**RR-19 is restated** to the retained-row predicate rather than "past the first
apply"; **RR-24** (the downgrade waits for a draining worker) is unchanged.

**Peter's decisions are unchanged and untouched:** RAID **I-11**
(`snapshot_folder_selections`) and the **R-41 versus SM-05** controlled amendment.
The §13 items — the SM-05 amendment of `C-P3.3-C`, `EFFECT_RECOVERY_LIMIT = 20`,
`EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` and the sweep's `MAX_LIMIT = 10 000` —
are unchanged and still awaiting the same ratification.

**One limitation is stated rather than smoothed over.** TC-MIG-37 holds the
migration after its lock is granted by locking Alembic's own `alembic_version`
row. That is a real hold on the real migration transaction and it changes no
production code, but it necessarily observes the lock *after* the revision body
has run, so it cannot and does not bind the granted lock to the guard's own
`LOCK TABLE` statement (§16.3). Holding the production revision between the lock
grant and the count, with no production hook, is not achievable in this
environment: the only PostgreSQL-native hold point in that interval would be a
DDL event trigger, and `CREATE EVENT TRIGGER` requires superuser, which the test
role deliberately is not. The lock's placement before the count is therefore
proved by TC-MIG-31, which fails against a guard with the statement removed, and
the two claims are kept apart on purpose.

### 16.9 What is requested

**An independent implementation re-review and a separate security-focused
re-review**, of this section and of the code and documents it describes.

**P3.G3 is not closed and is not claimed closed.** It remains open until these
three findings are accepted as corrected, the PostgreSQL evidence in §16.4 is
independently rerun, the retention-aware rollback policy is ratified and recorded
(**D-09**), the outstanding maintainer decisions from §13 and §14 are recorded,
and this correction passes both re-reviews. **P3.4 has not started.**

## 17. Fourth migration-rollback correction (2026-08-19)

The independent review of the third correction (§16) confirmed the
controlled-document correction (F1) and the exact rollback-module count (F3), and
recorded that the rollback module passed against disposable PostgreSQL:

```text
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
./venv-web/bin/python -m pytest -q \
tests/web/test_migration_0013_rollback_boundary.py -rs

18 passed in 15.71s
```

**That result is historical and it closes nothing.** It was taken against a test
whose identity assertion was ambiguous, and a passing run of an
identity-ambiguous test is not closing evidence. Every count in §17.5 was taken
after the correction below.

One major finding was open. It is fixed here, and nothing else in this slice is
touched: P3.G3 remains open and P3.4 has not begun.

### 17.1 F1 — TC-MIG-37 did not identify its ungranted lock as the test writer

**The finding, stated as the reviewer stated it.** `_ungranted(engine,
"RowExclusiveLock")` returns *every* ungranted `RowExclusiveLock` request on
`reconciliation_jobs`. After starting the fence writer, TC-MIG-37 accepted the
first non-empty result and asserted only that the migration lock-holder's pid was
absent from it. It never proved that any returned row belonged to the writer
thread's database connection or transaction. An unrelated session queued for the
same lock therefore satisfied the poll while the intended writer had not yet
requested its lock at all — it could still have been awaiting scheduling, opening
its connection, inside `seed_import()`, or anywhere before the production fence
statement. The surviving `writer.is_alive()` and `fence == {}` assertions do not
close that gap: both are true of a thread that has not reached the fence.

**This is not a timing flake and is not recorded as one.** The assertion was
wrong about *what it identified*, not about *when it ran*. That it passed is
explained by the disposable database being quiet, so the intended writer normally
won the race — which is exactly why a passing run was not evidence. The
requirement it contradicted is the mandatory one that `pg_locks` /
`pg_stat_activity` polling be scoped to the relevant relation **and** to the
process/transaction, so that an unrelated lock cannot satisfy the assertion.
§16.3's instrumented transcript showed the intended fence query; the committed
regression did not enforce the identity that transcript displayed.

**No production defect is implied and none was found.** The exclusion property
itself holds; what was missing was proof that the excluded transaction was the
one the case claims to exclude. `migrations/versions/0013_effect_publication_recovery.py`
is unchanged, as are `0011`, `0012` and `migrations/env.py`.

### 17.2 The correction — the writer names itself, and every later observation is bound to it

**How the writer's identity is obtained.** The writer is a thread owned by this
test module, so the seam is entirely test-side. Inside its own transaction, and
**before any production statement**, it executes `SELECT pg_backend_pid()` and
publishes the result on a bounded `queue.Queue(maxsize=1)`; the controlling test
takes it with `announced.get(timeout=LOCK_WAIT_SECONDS)` and fails with what the
writer reported if it never arrives. The pid is therefore the backend that will
issue the fence, read from the connection that will commit it — not a value taken
before the transaction existed, and not inferred from ordering.

Transaction identity is PostgreSQL-native and is read, not assumed:

```python
def _transaction_identity(row: dict) -> tuple:
    return (row["pid"], row["virtualtransaction"], row["backend_xid"], row["xact_start"])
```

`backend_xid` is real rather than `NULL` because the same transaction has already
inserted its `snapshot_imports` receipt, so the tuple carries a true xid as well
as the virtual transaction and the transaction start time.

**The two identities are distinct throughout, and are never conflated.**

| | The migration holder | The fence writer |
|---|---|---|
| Probe | `_holding_after_the_grant()` | `_the_writers_queued_fence()` / `_the_writers_open_fence_transaction()` |
| Bound by | holding a **granted** `AccessExclusiveLock` on `reconciliation_jobs` while itself blocked (`wait_event_type = 'Lock'`) on the `alembic_version` row this test holds — the only backend that can be | the pid it announced from inside its own transaction |
| Statement proved | `UPDATE alembic_version …` | the production `hold_for_effect` `UPDATE` |
| Variable in the case | `granted` | `writer_pid`, `queued`, `still_open` |
| Identity re-checked | `_lock_identity` — pid, `virtualtransaction`, `xact_start` unchanged while the writer waits | `_transaction_identity` — pid, `virtualtransaction`, `backend_xid`, `xact_start` identical between the queued request and the open, uncommitted fence transaction |

**The exact predicates.** Both writer probes share one projection, so the two
observations that are compared are literally the same columns:

```sql
SELECT l.pid, l.granted, l.virtualtransaction, a.query, a.wait_event_type,
       a.state, a.xact_start, a.backend_xid
FROM pg_locks l JOIN pg_stat_activity a ON a.pid = l.pid
WHERE l.locktype = 'relation'
  AND l.relation = 'reconciliation_jobs'::regclass
  AND l.mode = 'RowExclusiveLock'
  AND l.pid = :pid                    -- the announced writer backend, and no other
  AND NOT l.granted                   -- `_the_writers_queued_fence`
--  AND l.granted                     -- `_the_writers_open_fence_transaction`
```

and in Python, over that result:

| Probe | Additional condition | What it excludes |
|---|---|---|
| both | `_is_the_fence_statement(row["query"])` | a backend in `seed_import()`, in connection setup, or in any other statement |
| both | exactly one matching row, else `None` | an ambiguous match |
| `_the_writers_queued_fence` | `wait_event_type == 'Lock'` and `backend_xid is not None` | a backend not actually waiting on a lock, or one with no transaction of its own |
| `_the_writers_open_fence_transaction` | `state == 'idle in transaction'` | a backend still executing, or one that has already committed |

The `:pid` bind is what closes the finding: **a queued request from any other
backend cannot satisfy the poll**, because no other backend's row is returned.
The migration holder is additionally and separately excluded by an explicit
`assert writer_pid != granted["pid"]`.

**Statement shape, not statement text.** `_is_the_fence_statement()` normalises
whitespace and requires every token of

```text
UPDATE reconciliation_jobs SET | effect_committed_at = | effect_result =
version = version + 1 | AND effect_committed_at IS NULL
```

while requiring that `snapshot_imports` is **absent**. No token depends on how a
placeholder is spelled — the repository writes `:now`, SQLAlchemy renders
`%(now)s`, psycopg sends `$1`, and none of those is part of the production
contract. Every token that is matched **is** part of it: the table the effect
writes, the two columns it makes durable, the optimistic-concurrency bump, and
the once-only predicate that makes the fence a fence.

**The eight conditions, and where each is established.**

| # | Required | In the case |
|---|---|---|
| 1 | the downgrade transaction holds a **granted** `AccessExclusiveLock` | `granted = _await(_holding_after_the_grant(...))`; `assert granted["granted"] is True` |
| 2 | the writer opens only after that grant, and announces its backend pid by a bounded, deterministic mechanism | `writer.start()` after step 1; `announced.get(timeout=LOCK_WAIT_SECONDS)`, failing with the writer's own report if empty |
| 3 | the writer executes the production fence path and requests `RowExclusiveLock` | the thread runs `seed_import()` then `SqlAlchemyReconciliationJobLeaseRepository.hold_for_effect()` for a job it really claimed |
| 4 | the ungranted row has **exactly** the writer's pid | `_the_writers_queued_fence(engine, pid=writer_pid)`, `AND l.pid = :pid`; plus `assert queued["pid"] == writer_pid and queued["granted"] is False` |
| 5 | `pg_stat_activity` for that pid is the fence, not `seed_import` or setup | `_is_the_fence_statement()` inside the probe and again as an explicit assertion on `queued["query"]` |
| 6 | writer transaction identity recorded and re-observed | `waiting_transaction = _transaction_identity(queued)`, later `assert _transaction_identity(still_open) == waiting_transaction` — pid, `virtualtransaction`, `backend_xid` and `xact_start`, not thread liveness |
| 7 | while that request is ungranted, the same migration backend and transaction still hold the granted lock and the fence has not committed | `_lock_identity(still_held) == _lock_identity(granted)`; `migration.poll() is None`; `assert fence == {}` |
| 8 | after the migration transaction ends, that same writer transaction proceeds and commits | `fence_executed.wait(...)` → re-observation → `may_commit.set()` → `fence["committed"] is True`, `committed_effects() == (0, 1)`, `effect_committed_at IS NOT NULL`, `effect_result == FENCE_PAYLOAD` |

**How condition 6 is made observable.** The writer sets `fence_executed` after
`hold_for_effect()` returns and then blocks on `may_commit.wait(timeout=…)`
*inside* its transaction, before `COMMIT`. That interval is where the controlling
test re-reads `pg_locks`/`pg_stat_activity` for the same pid and finds the same
`virtualtransaction`, the same `backend_xid` and the same `xact_start`, now
holding the lock granted and `idle in transaction` with the fence as its last
statement. The transaction is then released and commits. **Both waits are
bounded, both are events rather than sleeps, and neither is in production code**
— the pause is in this module's own thread, between production calls, not a
production pause hook. No production module, revision statement or emitted SQL is
changed.

**`_ungranted()` is untouched and the queue-fairness case is not weakened.** A
narrowly named helper was added rather than a filter bolted onto the shared one,
so `…arriving_behind_a_pending_lock_request_cannot_overtake_it` (TC-MIG-32) keeps
every assertion and the deliberately broad observation its own property needs —
there, *that someone is queued* is the condition, and identity is not. What
`_ungranted()` gained is a docstring saying so, and saying that any case needing
identity must use `_the_writers_queued_fence()` instead.

**Docstrings and messages name the identity being proved.** The case's docstring
lists the eight conditions above and states, in its own words, that "two distinct
backends are named throughout and never conflated". Each assertion message says
which one it is about — for example the queued poll fails with `backend <pid> —
the fence writer, and no other session — to hold an ungranted ROW EXCLUSIVE
request on reconciliation_jobs while pg_stat_activity shows it executing the
production hold_for_effect fence`.

**Cleanup is bounded and total on every path.** `finally` now sets `may_commit`
**first and unconditionally**, so a failure anywhere above cannot leave the writer
parked in an open transaction until its own bound expires; then it kills the
migration child **before** releasing the `alembic_version` row, which both
prevents a *released* migration from committing its drops and unblocks a writer
still queued behind the migration's lock, so no failure path leaves the writer
waiting on a surviving lock holder; then it rolls back and closes the holder; and
it joins the writer only `if writer.is_alive()`, so a failure before
`writer.start()` raises the real assertion rather than `RuntimeError: cannot join
thread before it is started`. The timeout on the queued-fence poll is re-raised
with the writer's own reported state appended, so a writer that failed early
reports its error instead of an opaque timeout. `head_restored` returns the
disposable database to head however the case ended.

### 17.3 The falsification, and its exact failure

**What had to be shown:** that the corrected identity assertion fails when only an
unrelated queued `RowExclusiveLock` exists and the intended writer has not reached
the fence — and that the *old* broad predicate is satisfied in that same state.
Deterministically, not by scheduler luck.

**The mutation** (five edits to `tests/web/test_migration_0013_rollback_boundary.py`,
none to production, none weakening a guard):

1. a `unrelated_only = threading.Event()` added beside the existing events;
2. in the writer thread, immediately after it announces its pid and **before**
   `seed_import()`, `assert unrelated_only.wait(timeout=LOCK_WAIT_SECONDS)` — so
   the intended writer has provably requested no lock on `reconciliation_jobs`;
3. after the pid handshake, a second connection queues the same mode on the same
   relation from an unrelated session — `LOCK TABLE reconciliation_jobs IN ROW
   EXCLUSIVE MODE` — and the **old** predicate `_ungranted(engine,
   "RowExclusiveLock")` is polled and printed;
4. the corrected poll's ceiling lowered to `seconds=10.0` so the failure is
   prompt; and
5. `unrelated_only.set()` and the stranger's join/rollback/close added to
   `finally`.

**The result**, with `-s` so the printed observation is visible:

```text
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest -q \
  tests/web/test_migration_0013_rollback_boundary.py -k under_the_held_lock -rf -s

FALSIFICATION: old predicate `_ungranted(engine, 'RowExclusiveLock')` SATISFIED by
pids [1013135]; migration holder is 1013133; intended fence writer is 1013131,
which is held before its fence and appears: False

E   AssertionError: timed out after 10s waiting for backend 1013131 — the fence
    writer, and no other session — to hold an ungranted ROW EXCLUSIVE request on
    reconciliation_jobs while pg_stat_activity shows it executing the production
    hold_for_effect fence; last saw None; the writer reported {}

FAILED tests/web/test_migration_0013_rollback_boundary.py::test_a_fence_writer_starting_under_the_held_lock_cannot_commit_until_it_ends
1 failed, 17 deselected in 12.44s
```

**Read exactly.** Three distinct backends: the migration holder `1013133`, an
unrelated session `1013135`, and the intended fence writer `1013131`. The old
broad predicate was **satisfied** — by `1013135` — and its only identity
assertion, that the holder's pid is absent, **still held**, because `1013133` is
not `1013135`. The intended writer does not appear (`appears: False`). The
corrected predicate could not be satisfied and the case failed on it. That is the
gap the finding described, reproduced deterministically: the mutation removes
scheduler luck by holding the writer on an event rather than hoping it is slow.

**Restoration, immediately afterwards.** The final tree had been checksummed
before the mutation; the file was restored from that snapshot and the checksum
re-verified:

```text
sha256sum -c → tests/web/test_migration_0013_rollback_boundary.py: OK
              (ea89f462a4d4a681a0936149bdc765f7793f2b43cac761c567cb14d05fa1bfd4)
grep -c FALSIFICATION tests/web/test_migration_0013_rollback_boundary.py → 0
```

**The mutation is not in the final tree**, no production or test guard was
weakened to create it, and every count in §17.5 was taken after the restoration.

### 17.4 Every file changed by this fourth correction

| File | Change |
|---|---|
| `tests/web/test_migration_0013_rollback_boundary.py` | `import queue`; `_ungranted()`'s docstring states that it is deliberately broad and unusable for identity claims; new `FENCE_STATEMENT_SHAPE`, `RECEIPT_TABLE`, `_is_the_fence_statement()`, `_transaction_identity()`, `_WRITER_COLUMNS`, `_the_writers_queued_fence()` and `_the_writers_open_fence_transaction()`; TC-MIG-37's body and docstring rewritten around the pid handshake, the identity-bound polls, the pre-commit re-observation and the unconditional release in `finally` |
| `docs/contracts/phase-3-test-traceability.md` | a dated fourth-correction amendment note; TC-MIG-37's row states the identity now enforced; the regression note records what the corrected assertion is additionally a regression for |
| `docs/review/phase-3-p3-3-submission.md` | §16.3 amended so its transcript is labelled illustrative and the committed assertions are named as the evidence; this §17 added |
| `docs/project-management/status.md` | eighteenth update |
| `docs/project-management/change-log.md` | `C-P3.3-G` |
| `docs/project-management/raid-register.md` | `I-19` recorded and closed |

**No other file was touched.** In particular: no file under `migrations/`,
`application/`, `adapters/`, `domain/`, `tools/`, `infra/` or `models/`; no other
test module; and `docs/operations/web-portal.md`, `docs/contracts/phase-3-logical-schema.md`
and `docs/contracts/phase-3-state-machines.md` are unchanged, because this
finding and its evidence change none of their present claims. Every other
modified or untracked path in `git status` was already modified by §12–§16 and
was not touched here. The pre-existing stash `stash@{0}: On main: temp before
rebase` was never inspected, applied, dropped or modified. Nothing was committed,
pushed or deployed; no live Discord, Google, Foundry or production service was
contacted; and no real Actor, player, guild or credential data was used.

### 17.5 Final-tree evidence

All commands were run from `/opt/discord-bots/freedom-bot` with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported, **serially** —
the disposable `freedom_test` database is shared by both virtualenvs and running
the suites concurrently produces dozens of spurious failures. Every count below is
the literal result of the run named, taken **after the last edit to any file in
this correction**. Nothing is derived and no earlier count is reused.

| # | Command | Exact result |
|---|---|---|
| 1 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k under_the_held_lock -rs` | **1 passed, 17 deselected** in 2.37s — TC-MIG-37 alone |
| 2 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k "in_flight_effect or under_the_held_lock or behind_a_pending_lock" -rs` | **3 passed, 15 deselected** in 4.38s — the held-lock, pending-lock queue-fairness and in-flight-writer concurrency selections together |
| 3 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -rs` | **18 passed** in 15.47s. **No skips**; the module is `pytest.mark.database` and its fixtures resolve the disposable URL or fail |
| 4 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py tests/web/test_migration_0013_round_trip.py -rs` | **22 passed** in 17.49s (18 + 4) |
| 5 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0011_round_trip.py tests/web/test_migration_0012_round_trip.py tests/web/test_migration_0013_round_trip.py tests/web/test_migration_0013_rollback_boundary.py -rs` | **29 passed** in 19.90s — all `0011`, `0012` and `0013` migration tests (4 + 3 + 4 + 18) |
| 6 | `./venv-web/bin/python -m pytest -q tests/web/test_p3_3_jobs.py tests/web/test_p3_3_worker.py tests/web/test_p3_3_effect_fence.py tests/web/test_p3_3_effect_recovery.py tests/web/test_p3_3_job_retention.py -rs` | **109 passed** in 7.30s — every P3.3 jobs, worker, effect-fence, effect-recovery and retention test |
| 7 | `./venv-web/bin/python -m pytest -q tests/web` | **1429 passed, 80 skipped** in 93.41s. The 80 skips are the two permission-matrix modules' permitted cells (54 + 26), which the per-route success cases assert; unchanged from §16 |
| 8 | `./venv/bin/python -m pytest -q` | **2293 passed** in 137.81s — the full bot suite, unchanged |
| 9 | `./venv-web/bin/python -m pytest -q tests/test_database_postgresql.py::test_migration_matches_table_metadata tests/test_database_postgresql.py::test_migrations_apply_to_empty_postgresql_and_downgrade tests/test_runtime_grants.py tests/web/test_p3_2_runtime_grants_and_bounds.py tests/test_migration_safety.py -rs` | **81 passed** in 5.40s — metadata parity, the empty-database `base ↔ head` round trip, the effective runtime-grant tests and the migration-safety tests. **No grant changed** |
| 10 | `alembic downgrade base`, `alembic upgrade head`, `alembic check`, through the suite's own guarded environment | rc **0**, rc **0**, rc **0** with output **"No new upgrade operations detected."**; `SELECT version_num FROM alembic_version` = **`0013`** |
| 11 | `alembic downgrade 0013:0012 --sql` | rc **0**. Emitted order: `BEGIN;` → `LOCK TABLE reconciliation_jobs IN ACCESS EXCLUSIVE MODE;` → `DO $rollback_boundary$ … RAISE EXCEPTION …` → `DROP CONSTRAINT ck_…_committed_effect_is_never_denied` → `DROP CONSTRAINT ck_…_effect_result_accompanies_the_fence` → `DROP COLUMN effect_result` → `UPDATE alembic_version SET version_num='0012' …` → `COMMIT;`. `RAISE EXCEPTION` present. The positional assertions and the `psql` execution of this script are TC-MIG-33 and TC-MIG-34, inside command 3 |
| 12 | `./venv-web/bin/python -m compileall -q` on **every changed Python file** (54 files: `git diff --name-only` plus `git ls-files --others --exclude-standard`, filtered to `*.py`) | rc **0**, no output |
| 13 | `git diff --check` | rc **0**, **no output** |
| 14 | Formatter / linter / type checker | **None is installed or configured, and that is reported rather than claimed as a pass.** Re-verified for this correction: no `black`, `ruff`, `flake8`, `mypy`, `pyright`, `isort` or `pylint` executable exists in `./venv/bin` or `./venv-web/bin`, and there is no `pyproject.toml`, `setup.cfg`, `.flake8`, `.ruff.toml` or `tox.ini`. `requirements-dev.txt` carries only `pytest` and `pytest-asyncio`. Introducing one would be a drive-by dependency change this correction is not authorized to make |

**Manual diff review.** No secret, credential, token, real Discord snowflake, real
guild id, real Actor name or production identifier appears in any file changed by
this correction. `.env`, `yt-cookies.txt` and every credential file were never
read, printed or modified. No unsafe log line was added — the correction adds no
logging at all, and the only `print()` calls written in this slice were in the
falsification mutation, which is not in the final tree. No unrelated file was
edited. No test was relaxed, skipped, deleted or given a weaker assertion: TC-MIG-37
gained assertions and lost none, and TC-MIG-32 is untouched. The backend pids in
§17.3 are ephemeral process ids from the local disposable database and are not
data of any kind.

**Order of operations, stated so the "after the final edit" rule is checkable.**
The last edits in this correction were the controlled documents — this submission
section, the test-traceability register, the status record, the change log and the
RAID register — all made after the final edit to
`tests/web/test_migration_0013_rollback_boundary.py`. `docs/operations/web-portal.md`
is the only documentation file any test opens and it is **unchanged** here, so no
test result depends on a document edited in this correction; commands 1–9 and
12–13 were nevertheless rerun after the last of those edits and produced exactly
the counts above. Commands 10, 11 and 14 do not depend on the test tree.

**Historical results are kept separate and labelled.** The `18 passed in 15.71s`
quoted at the head of this section is the reviewer's pre-fix run and is **not**
closing evidence. §14.7.1's pre-fix transcript, §15.4's before/after results,
§16.3's `LOCK TABLE`-removed falsification and §16.4's table are results of earlier
trees and are not rewritten as though rerun. No result in this section rests on a
run with `TEST_DATABASE_URL` unset, none is a fixture setup failure, and no
PostgreSQL concurrency test was skipped.

### 17.6 What was **not** added

- **No marker, sidecar, tombstone, retention-policy change, production pause hook
  or hidden schema object.** The pause this case needs is a `threading.Event` in
  this test module's own writer thread, between production calls; no production
  module has, or gained, a hook.
- **No production SQL change and no production change of any kind.** The
  migration's DDL and emitted SQL are byte-for-byte what §16 left, and `alembic
  check` reports no metadata difference (command 10). `0011` and `0012` were not
  edited, and neither was `0013` — this finding required a test-evidence
  correction, not a migration change, and no failing production regression
  suggested otherwise.
- **No manual deletion, truncation, shortened retention or early retention** was
  introduced as a rollback technique. `tools/job_retention.py` was not touched and
  N-24's eligibility rule, 30-day age, operator command and audit event are
  unchanged.
- **No weakening** of authorization, audit append-only behaviour, effect fencing,
  result publication, recovery, runtime grants or schema constraints. The upfront
  online `ACCESS EXCLUSIVE` lock and count-after-grant ordering, the offline
  `BEGIN` → lock → count/refusal → drops → `COMMIT` ordering, the retention-aware
  retained-row predicate and all four documented database states are preserved and
  still covered by commands 3 and 5.
- **`FilesystemArtifactStore`'s production default `ancestors.ceiling is None`** is
  unchanged and still asserted by its control case; the ordinary P3.3 tests still
  use the explicit bounded test seam.

### 17.7 Security, integrity, availability, runtime-role and deployment order

Unchanged from §16.6, because no production behaviour changed. Restated so the
security reviewer does not have to infer it:

- **Security.** No new caller-reachable path exists; nothing added here runs
  outside `pytest`. The two new probes read only `pg_locks`, `pg_stat_activity` and
  `pg_class`, never `reconciliation_jobs`, and they run as the test role against
  the disposable database. `pg_backend_pid()` is called by the test's own
  connection about itself. `pg_cancel_backend` is unchanged, still used only by the
  test against a backend of its own role, and appears in no production module.
  Refusals still report counts, never rows (N-25).
- **Integrity.** The window in which a committed effect could be silently
  destroyed remains closed, and the evidence for one half of it is now stronger
  rather than weaker: the lock is taken before the count (TC-MIG-31), and a writer
  starting under the held lock cannot commit until the migration transaction ends
  — now proved of *that writer's own transaction* (TC-MIG-37).
- **Availability.** Unchanged: the downgrade waits for a draining worker rather
  than racing it (**RR-24**), visible in `pg_locks`/`pg_stat_activity`. No
  `lock_timeout` is set and none was added.
- **Runtime role.** Untouched. It still holds no `DELETE` on
  `reconciliation_jobs`; `tests/test_runtime_grants.py` and
  `tests/web/test_p3_2_runtime_grants_and_bounds.py` pass unchanged (command 9),
  and `infra/postgresql/runtime-grants.sql.tmpl` was not edited.
- **Deployment order.** Unchanged and still `docs/operations/web-portal.md` §3.6:
  roll forward is **migrate then deploy**; roll back is **stop every worker,
  confirm no lease is live, run the preflight, downgrade, then deploy the older
  code**, and only while the preflight returns two zeros.

### 17.8 Open decisions and residual risks — all retained

Nothing below is closed, reinterpreted or self-approved by this correction.

- **The retention-aware rollback policy remains a proposal awaiting
  Peter/Acceptance Authority ratification.** RAID **D-09**, change-log
  `C-P3.3-D` / `C-P3.3-E` / `C-P3.3-F`. **P3.G3 is not claimed closed.**
- **Peter's other decisions are unchanged and untouched:** RAID **I-11**
  (`snapshot_folder_selections`) and the **R-41 versus SM-05** controlled
  amendment.
- **The §13 items are unchanged and still awaiting the same ratification:** the
  SM-05 amendment of `C-P3.3-C`, `EFFECT_RECOVERY_LIMIT = 20`,
  `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` and the sweep's `MAX_LIMIT = 10 000`.
- **Residual risks unchanged:** RR-16 remains withdrawn; RR-17 and RR-18 are
  unchanged; RR-19 stands as restated to the retained-row predicate; RR-24 is
  unchanged.
- **I-06 and A-05 are unchanged and still open.** Staging-class checks remain
  unrun — TC-PERF-01/02/03, TC-LIM-02, TC-SEC-07's browser half and
  TC-OPS-01…05 — and the operational half of §3.6 is documented rather than
  exercised, because staging does not exist.
- **§16.8's stated limitation of TC-MIG-37 is unchanged and is not narrowed by
  this correction.** The case still observes the granted lock *after* the revision
  body has run, so it does not bind that lock to the guard's own `LOCK TABLE`; the
  lock's placement before the count remains TC-MIG-31's claim. What this
  correction changes is *whose* transaction the exclusion is proved of, not which
  statement took the lock.

### 17.9 What is requested

**Another independent implementation re-review, and a separate security-focused
re-review**, of this section and of the code and documents it describes.

**P3.G3 remains open and is not claimed closed.** It remains open until this
finding is accepted as corrected, the PostgreSQL identity evidence in §17.5 is
independently rerun, the retention-aware rollback policy is ratified and recorded
(**D-09**), the outstanding maintainer decisions from §13, §14 and §16 are
recorded, and this correction passes both re-reviews. **P3.4 has not started.**

## 18. Fifth migration-rollback correction (2026-08-19)

The independent review of the fourth correction (§17) **accepted the
writer-identity remediation as sound**. It recorded that the observed request is
restricted to the announced writer PID, matched to the production
`hold_for_effect` statement, and tied through `pid`, `virtualtransaction`,
`backend_xid` and `xact_start` to the transaction that later commits, and that
the falsification checksum recorded in §17.3 matches the current file. That
result stands and is not reopened here.

The reviewer also reran the tree against disposable PostgreSQL:

```text
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
./venv-web/bin/python -m pytest -q \
tests/web/test_migration_0013_rollback_boundary.py -k under_the_held_lock -rs

1 passed, 17 deselected in 2.57s

TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' \
./venv-web/bin/python -m pytest -q \
tests/web/test_migration_0013_rollback_boundary.py -rs

18 passed in 16.30s
```

**Both results are historical and neither closes the finding below.** They are
runs of the **happy path**, and the defect is on the failure path — the path a
passing case never executes. That is the whole reason a passing run was not
evidence here, and every count in §18.5 was taken after the correction.

One major finding was open. It is fixed here, and nothing else in this slice is
touched: P3.G3 remains open and P3.4 has not begun.

### 18.1 F1 — TC-MIG-37 had an unbounded subprocess reap on failure

**The finding, stated as the reviewer stated it.** In
`test_a_fence_writer_starting_under_the_held_lock_cannot_commit_until_it_ends`,
the `finally` block killed a surviving migration subprocess and then called
`migration.communicate()` **without a timeout**:

```python
if migration is not None and migration.poll() is None:
    migration.kill()
    migration.communicate()      # <- unbounded
```

If process termination or pipe collection stalled, cleanup could hang
indefinitely *before* it rolled back `holding`, closed `holder`, or finished
joining the writer. This contradicts the mandatory requirement that cleanup
remain bounded and release every connection, transaction, thread and process on
every assertion-failure path, and it contradicts the case's own claim that its
waits are bounded.

**Classified as an unbounded failure-path cleanup defect, not a flake and not a
timing defect.** Nothing about it depends on the scheduler. The path simply is
not reachable from a passing run: `migration.poll()` is not `None` by the time a
successful TC-MIG-37 reaches its `finally`, because step (6) already reaped the
child with `_reap()`. Only a failure between `start_alembic()` and that reap
enters the branch at all — which is exactly the condition under which a hang is
least acceptable, because the suite is already trying to report a defect.

**Two further instances of the same defect were found while fixing it, and are
recorded rather than left.** `_reap()` itself — the *success*-path helper — ended
its timeout branch with `process.kill()` followed by an unbounded
`process.communicate()`, so the fix would have moved the hang rather than removed
it. And the three sibling concurrency cases in the same module
(`…in_flight_effect…`, `…behind_a_pending_lock_request…`, and the offline `psql`
applier) carried the identical `kill(); communicate()` shape in their own
`finally` blocks. All are corrected here; see §18.2 and §18.6. This is stated
explicitly because it is a **deliberate, minimal extension** of the finding's
literal scope — the same two-line substitution at each site, no restructuring of
those cases — and the reviewer may reject that part without affecting the
correction to TC-MIG-37.

**No production defect is implied and none was found.**
`migrations/versions/0013_effect_publication_recovery.py` is unchanged, as are
`0011`, `0012` and `migrations/env.py`. This is a test cleanup and evidence
correction.

### 18.2 The correction — one owner, one ordered release, every bound explicit

Every resource TC-MIG-37 holds is now owned by a small test-local object,
`_HeldLockCleanup`, whose single `release()` runs on **every** exit path through
the `_released()` context manager. There is no `finally` block in the case any
more, and no second place where a resource can be released.

**The order, and why each step is where it is.**

| # | Step | Why here |
|---|---|---|
| 1 | `may_commit.set()` — release the writer's commit event | Unconditional and **first**, so a failure anywhere cannot leave the writer parked inside an open transaction until its own `LOCK_WAIT_SECONDS` bound expires. It costs nothing on the paths that already released it |
| 2 | End and **boundedly reap** a surviving migration child | **Before** the `alembic_version` row lock is released. Order, not preference: a migration *released* rather than *ended* would go on to commit the drops the case asserts were undone. Ending it also drops its `ACCESS EXCLUSIVE` lock, which is what unblocks a writer still queued behind it — so no failure path leaves the writer waiting on a lock holder that outlives the test |
| 3 | `holding.rollback()` — release the row lock | Two steps rather than one with step 4, so a rollback that raises cannot leak the connection |
| 4 | `holder.close()` | — |
| 5 | `writer.join(timeout=…)`, **only if it was started and is still alive** | An unconditional join would raise `cannot join thread before it is started` out of a failure that happened before `writer.start()`, and hide it |

Every step runs even when an earlier one failed, and every step is bounded.

**The bounded reap.** `_bounded_reap()` replaces the unbounded call:

```python
for _attempt in (1, 2):
    try:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=seconds)
    except subprocess.TimeoutExpired:
        continue
    except Exception as error:
        return f"collecting the migration {name} raised {error!r}"
    return None
return (f"the migration {name} was neither killed nor collected within "
        f"{2 * seconds:.0f}s; its locks and connection may survive this test")
```

Three properties, each deliberate:

- **it never waits without a bound**, including after the kill — `2 * seconds`
  is the whole of it, with `CLEANUP_REAP_SECONDS = 5.0`;
- **it never raises.** Cleanup runs while an assertion is already failing, and a
  helper that raised there would substitute a report about the cleanup for the
  failure under diagnosis. It returns `None`, or a description of what was left
  behind; and
- **`kill()` rather than `terminate()`, and that is a safety property.**
  `SIGKILL` cannot run a signal handler, so a migration ended this way provably
  cannot issue the `COMMIT` that would make its drops durable. `SIGTERM` gives
  the child that opportunity, however unlikely. The handover's "terminate and
  boundedly reap" is satisfied by an unconditional kill; the substitution would
  weaken the very property the surrounding assertions rest on, so it was not
  made.

A child that survives both bounded collections is **reported and stepped over**
rather than aborting the release. That is a deliberate trade: a process beyond
the reach of two `SIGKILL`s is beyond the test's reach either way, while the row
lock, the holder connection and the writer transaction are not — and requirement
5 forbids leaving *those* behind. The problem is reported, so the state is never
silently accepted.

`_reap()`, the success-path helper, is bounded in the same way: its post-kill
collection now carries `timeout=CLEANUP_REAP_SECONDS` and raises a distinct
`AssertionError` if even that does not complete. Its contract is otherwise
unchanged — it still returns `(returncode, stdout, stderr)` and still fails the
case rather than reporting, because a child that outlives the wait *is* a failure
of a case that is otherwise passing.

**How the original assertion stays diagnosable.** `_released()` is a context
manager, not a `finally` block:

```python
try:
    yield cleanup
except BaseException as primary:
    for problem in cleanup.release():
        primary.add_note(f"cleanup also failed: {problem}")
    raise
problems = cleanup.release()
assert not problems, "the case passed but its cleanup did not: " + "; ".join(problems)
```

On the failing path the **original exception is re-raised unchanged** and each
cleanup problem is attached to it with `add_note()`, so pytest reports the
assertion that actually failed and, underneath it, whatever cleanup could not
release. On the passing path there is no failure to preserve, so an unreported
cleanup problem becomes the failure — bounded, total cleanup is part of what
these cases claim.

**Explicit bounds, all far below the production-test ceiling.**

```python
CLEANUP_REAP_SECONDS = 5.0        # per bounded collection; the reap costs at most 2 x
CLEANUP_JOIN_SECONDS = 15.0       # the bounded writer join
CLEANUP_SETTLE_SECONDS = 15.0     # how long PostgreSQL is given to tear down a killed backend
```

`cleanup.seconds_ceiling` is `2 * reap + join` — **25 s** with the defaults, and
the regression asserts the measured elapsed time against it. Nothing here is
allowed to *approach* the 60-second `LOCK_WAIT_SECONDS` ceiling, let alone a
hang.

### 18.3 The regression: bounded, total, and driven from a controlled failure

Four new cases, TC-MIG-38…TC-MIG-41. They are about TC-MIG-37's **cleanup**, not
its property, and they are cited for nothing else.

**TC-MIG-38 — real PostgreSQL, a controlled assertion failure, two failure
points.** `test_the_held_lock_cleanup_is_bounded_and_total_when_the_case_fails`
rebuilds TC-MIG-37's scenario exactly: the `alembic_version` row held from
outside Alembic, the production `alembic downgrade 0012` running until it holds a
**granted** `AccessExclusiveLock` on `reconciliation_jobs` while blocked on that
row, and a fence-capable writer that announces its own backend pid from inside
its own transaction and then issues the production `hold_for_effect` statement
behind that lock, observed through `_the_writers_queued_fence()`. Nothing is
stubbed; the production revision and the production fence statement drive it.

Then an assertion fails, deliberately, at a named point, and the **cleanup** is
what is measured — from the instant of failure:

| Required | Asserted as |
|---|---|
| returns within an explicit bound | `elapsed < cleanup.seconds_ceiling` **and** `elapsed < CLEANUP_SETTLE_SECONDS`, measured with `time.monotonic()` from the moment the controlled failure is raised |
| reaps the migration process | `migration.poll() is not None` and `migration.returncode is not None` |
| releases the writer thread and its transaction | `not writer.is_alive()`; the writer's own report shows the fence held **and committed**, so its transaction resolved rather than being abandoned |
| releases the holder transaction/connection | `holding.is_active is False`, `holder.closed is True` |
| leaves no matching PostgreSQL lock or activity | a bounded poll of `pg_locks`/`pg_stat_activity` until **all three** counts are zero: `AccessExclusiveLock`/`RowExclusiveLock` on `reconciliation_jobs`, open transactions for the writer's backend, and surviving migration backends |
| the primary failure survives | `pytest.raises` catches the controlled `AssertionError`, and `raised.value.__notes__ == []` — cleanup had nothing to attach |
| the killed migration did not commit its drops | `alembic_version` is still `0013`, the three dropped objects are back, and the catalogue fingerprint equals the pre-failure one |
| the collection carried a **bound** | `None not in migration.collected_with` and `migration.collected_with == [CLEANUP_REAP_SECONDS]`, recorded on the real child by `_RecordingChild` |

The two parameters are the two shapes cleanup has to handle:

- **`while the writer is queued`** — the migration child is **alive** and holds
  the table lock, and the writer is blocked behind it. This is the finding's own
  path: cleanup must end and collect that child, and doing so is also what frees
  the writer; and
- **`after the fence executed`** — the migration transaction has already ended
  (cancelled, and deliberately **not** reaped by the test, so cleanup still has
  to collect the child) and the writer is parked inside an open, uncommitted
  fence transaction. Nothing but the release can get it out.

Which of the two shapes cleanup faces is **asserted, not assumed**: the first
parameter checks `migration.poll() is None` immediately before the controlled
failure, and the second waits for the cancelled child to exit first.

Neither depends on scheduler luck: every step waits on an observable database
state or a `threading.Event`, and the failure is injected at a point the test
reaches deterministically. Neither hangs for the 60-second ceiling; the whole
module now runs in ~19 s.

**How a real case can falsify an unbounded call at all — `_RecordingChild`.** A
real Alembic child killed with `SIGKILL` is collected immediately, so the pre-fix
`kill(); communicate()` shape returns at once: every assertion above about
elapsed time, about the child being reaped, and about surviving locks still
passes against it. The defect is not "cleanup was slow"; it is "cleanup asked for
a collection it could not bound", which is a property of the **call**. So the
child `start_alembic()` returns is wrapped in `_RecordingChild`, which delegates
`poll`, `kill`, `terminate`, `communicate`, `pid` and `returncode` to the real
process — the real Alembic revision runs, the real signal is sent — and records
the `timeout` each collection carried and how often the child was killed. Nothing
is replaced and nothing is simulated; the wrapper adds observation only. With it,
TC-MIG-38 fails deterministically against the pre-fix shape in **both**
parameters (§18.4).

**TC-MIG-39 — the branch a real child cannot be made to take.** A genuinely hung
Alembic child cannot be produced on demand, and a regression that hung for real
would hang the suite instead of reporting. `_UnreapableProcess` is a fake that
never dies, records **the timeout it was collected with**, and stands in for
"forever" with `STAND_IN_FOR_FOREVER = 3.0` seconds. Against it, cleanup is shown
to collect the child **with a timeout, twice, and never once without one**
(`assert None not in process.collected_with`), to return well inside its ceiling,
to **report** the stuck child rather than swallow it, and to still complete every
other step — writer released and joined, row lock rolled back, holder closed. The
last point is the one the trade in §18.2 rests on. The handover permits this
seam — distinct from `_RecordingChild`, which replaces nothing — and the real
PostgreSQL concurrency case (TC-MIG-38, and TC-MIG-37 itself) still drives the
production revision and the production fence statement. TC-MIG-38 falsifies the
defect in its own right; TC-MIG-39 exists for the branch a real child cannot be
made to take.

**TC-MIG-40 — the earliest paths.** A failure before the migration child exists
and before `writer.start()` — the same shape as a failure before the pid
announcement — still releases the commit event, rolls back the row lock and
closes the holder, does not join an unstarted thread, and reports no problem it
does not have.

**TC-MIG-41 — requirement 3, asserted directly.** With a cleanup that cannot
release its child, an assertion raised inside `_released()` surfaces **unchanged**
and the cleanup problem appears as a note on it; the resources that *could* be
released still were. The mirror case proves the passing path turns an unreported
cleanup problem into a failure.

**Every path enumerated in the handover's requirement 4, and where it is
covered.**

| Path | Covered by |
|---|---|
| failure before `writer.start()` | TC-MIG-40 |
| failure before PID announcement | TC-MIG-40 (identical shape: no child, unstarted thread) |
| failure while the writer is queued | TC-MIG-38, parameter `while the writer is queued` — real PostgreSQL, migration child alive |
| failure after the fence executes but before commit release | TC-MIG-38, parameter `after the fence executed` |
| a migration child that will not die | TC-MIG-39 |
| a cleanup error alongside a primary failure | TC-MIG-41 |

### 18.4 The falsification, and its exact failure

**What had to be shown:** that the pre-fix unbounded form is caught by the
regression, deterministically, and without hanging.

**The mutation** — one edit to `tests/web/test_migration_0013_rollback_boundary.py`,
replacing `_bounded_reap()`'s body with the shape the finding describes:

```python
# MUTATION: the pre-fix unbounded shape, restored deliberately.
if process is not None and process.poll() is None:
    process.kill()
    process.communicate()
return None
```

**The result:**

```text
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest -q \
  tests/web/test_migration_0013_rollback_boundary.py -k "cleanup" -rf

E       AssertionError: cleanup collected the real migration child with no timeout — that
        is the pre-fix unbounded shape: [None]
E       assert None not in [None]
E        +  where [None] = <_RecordingChild object at 0x7d09f33c9e80>.collected_with

E       AssertionError: the real migration child was not collected exactly once with the
        bounded reap's own timeout: []. An empty record means cleanup skipped an
        already-exited child instead of collecting its pipes
E       assert [] == [5.0]

E       AssertionError: cleanup collected the migration child with no timeout — that is
        the pre-fix unbounded shape: [None]
E       assert None not in [None]
E        +  where [None] = <_UnreapableProcess object at 0x7d09f2fa44a0>.collected_with

E       AssertionError: []
E       assert False
E        +  where False = any(<generator ...>)   # no cleanup problem was reported at all

FAILED …::test_the_held_lock_cleanup_is_bounded_and_total_when_the_case_fails[while the writer is queued]
FAILED …::test_the_held_lock_cleanup_is_bounded_and_total_when_the_case_fails[after the fence executed]
FAILED …::test_the_held_lock_cleanup_is_bounded_when_the_migration_child_will_not_die
FAILED …::test_a_cleanup_problem_is_reported_without_replacing_the_failure_under_diagnosis
4 failed, 1 passed, 18 deselected in 9.46s
```

**Read exactly.** Four cases fail, and the two that matter most are the **real
PostgreSQL** ones — the production Alembic revision, the production
`hold_for_effect` fence, a real child, a real `SIGKILL`. They fail for the two
distinct reasons the pre-fix shape produces:

- **`while the writer is queued`** — the surviving child was collected with
  `timeout=None`, recorded at the call. That is the defect itself, not a proxy
  for it; and
- **`after the fence executed`** — the child had already exited, so the pre-fix
  branch (`if poll() is None`) skipped it entirely and its pipes were never
  collected: `[] == [5.0]` fails. The bounded reap collects an exited child too,
  which is a second, smaller defect of the pre-fix shape that this parameter
  exposes.

TC-MIG-39 fails on the same recorded `timeout=None` against a child that never
dies, and would have failed independently on its elapsed bound (`elapsed < 2.0`
against a fake standing in for "forever" with 3.0 s) and on the problem a bounded
reap reports and an unbounded one cannot. TC-MIG-41 fails because there was no
cleanup problem to attach to the assertion under diagnosis.

The one case that still passes is TC-MIG-40, correctly: it has no migration child
at all, so the mutation cannot reach it.

The run took **9.46 s** and did not hang. That is deliberate on both sides: the
real cases assert on the *call* rather than on elapsed time, because a real hung
child cannot be produced on demand, and the fake stands in for "forever" with a
3.0 s ceiling, because a regression that hangs is not a regression.

**Restoration, immediately afterwards.** The final tree had been checksummed
before the mutation; the file was restored from that snapshot and the checksum
re-verified:

```text
sha256sum -c → tests/web/test_migration_0013_rollback_boundary.py: OK
              (9cbc1a73d4f4b5cf0ad9c161ff80e7752bd775f27dfaf6088f5e043f38d7b558)
grep -c MUTATION tests/web/test_migration_0013_rollback_boundary.py → 0
```

**The mutation is not in the final tree**, no production or test guard was
weakened to create it, and every count in §18.5 was taken after the restoration.

### 18.5 Final-tree evidence

All commands were run from `/opt/discord-bots/freedom-bot` with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported, **serially** —
the disposable `freedom_test` database is shared by both virtualenvs and running
the suites concurrently produces dozens of spurious failures. Every count below is
the literal result of the run named, taken **after the last edit to any file in
this correction**. Nothing is derived and no earlier count is reused.

**What is claimed here is the pass/skip/fail count.** The wall-clock durations are
reproduced from the same run for context and vary by a few percent between runs on
this host; a duration that differs slightly on re-execution is not a discrepancy,
and no count below depends on one.

| # | Command | Exact result |
|---|---|---|
| 1 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k "cleanup" -rs` | **5 passed, 18 deselected** in 4.76s — the new bounded-cleanup regression alone (TC-MIG-38 ×2 parameters, TC-MIG-39, TC-MIG-40, TC-MIG-41) |
| 2 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k under_the_held_lock -rs` | **1 passed, 22 deselected** in 2.24s — TC-MIG-37 alone |
| 3 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k "in_flight_effect or under_the_held_lock or behind_a_pending_lock" -rs` | **3 passed, 20 deselected** in 4.11s — the held-lock, pending-lock queue-fairness and in-flight-writer concurrency selections together |
| 4 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -rs` | **23 passed** in 19.18s (18 + 5 new). **No skips**; the module is `pytest.mark.database` and its fixtures resolve the disposable URL or fail |
| 5 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py tests/web/test_migration_0013_round_trip.py -rs` | **27 passed** in 21.20s (23 + 4) |
| 6 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0011_round_trip.py tests/web/test_migration_0012_round_trip.py tests/web/test_migration_0013_round_trip.py tests/web/test_migration_0013_rollback_boundary.py -rs` | **34 passed** in 23.67s — all `0011`, `0012` and `0013` migration tests (4 + 3 + 4 + 23) |
| 7 | `./venv-web/bin/python -m pytest -q tests/web/test_p3_3_jobs.py tests/web/test_p3_3_worker.py tests/web/test_p3_3_effect_fence.py tests/web/test_p3_3_effect_recovery.py tests/web/test_p3_3_job_retention.py -rs` | **109 passed, 20 warnings** in 7.49s — every P3.3 jobs, worker, effect-fence, effect-recovery and retention test. The 20 warnings are pre-existing `httpx` per-request-cookie `DeprecationWarning`s from `test_p3_3_jobs.py` (19) and `test_p3_3_effect_recovery.py` (1); nothing in this correction adds or removes a warning |
| 8 | `./venv-web/bin/python -m pytest -q tests/web` | **1434 passed, 80 skipped** in 99.56s. The 80 skips are the two permission-matrix modules' permitted cells (54 + 26), which the per-route success cases assert; unchanged from §17. The pass count is §17's 1429 plus the 5 new cases |
| 9 | `./venv/bin/python -m pytest -q` | **2293 passed** in 138.67s — the full bot suite, unchanged |
| 10 | `./venv-web/bin/python -m pytest -q tests/test_database_postgresql.py::test_migration_matches_table_metadata tests/test_database_postgresql.py::test_migrations_apply_to_empty_postgresql_and_downgrade tests/test_runtime_grants.py tests/web/test_p3_2_runtime_grants_and_bounds.py tests/test_migration_safety.py -rs` | **81 passed** in 5.76s — metadata parity, the empty-database `base ↔ head` round trip, the effective runtime-grant tests and the migration-safety tests. **No grant changed** |
| 11 | `alembic downgrade base`, `alembic upgrade head`, `alembic check`, through the suite's own guarded environment | rc **0**, rc **0**, rc **0** with output **"No new upgrade operations detected."**; `SELECT version_num FROM alembic_version` = **`0013`** |
| 12 | `alembic downgrade 0013:0012 --sql` | rc **0**. Emitted order: `BEGIN;` → `LOCK TABLE reconciliation_jobs IN ACCESS EXCLUSIVE MODE;` → `DO $rollback_boundary$ … RAISE EXCEPTION …` → `DROP CONSTRAINT ck_…_committed_effect_is_never_denied` → `DROP CONSTRAINT ck_…_effect_result_accompanies_the_fence` → `DROP COLUMN effect_result` → `UPDATE alembic_version SET version_num='0012' …` → `COMMIT;`. `RAISE EXCEPTION` present. The positional assertions and the `psql` **execution** of this script are TC-MIG-33 and TC-MIG-34, inside command 4 |
| 13 | `./venv-web/bin/python -m compileall -q` on **every changed Python file** (54 files: `git diff --name-only` plus `git ls-files --others --exclude-standard`, filtered to `*.py`) | rc **0**, no output |
| 14 | `git diff --check` | rc **0**, **no output** |
| 15 | Formatter / linter / type checker | **None is installed or configured, and that is reported rather than claimed as a pass.** Re-verified for this correction: no `black`, `ruff`, `flake8`, `mypy`, `pyright`, `isort` or `pylint` executable exists in `./venv/bin` or `./venv-web/bin`, and there is no `pyproject.toml`, `setup.cfg`, `.flake8`, `.ruff.toml` or `tox.ini`. `requirements-dev.txt` carries only `pytest` and `pytest-asyncio`. Introducing one would be a drive-by dependency change this correction is not authorized to make |

**Manual diff review.** No secret, credential, token, real Discord snowflake, real
guild id, real Actor name or production identifier appears in any file changed by
this correction. `.env`, `yt-cookies.txt` and every credential file were never
read, printed or modified. No unsafe log line was added — the correction adds no
logging at all, and no `print()` call exists anywhere in it, including in the
falsification mutation, which asserted on recorded state instead. No unrelated
file was edited. No test was relaxed, skipped, deleted or given a weaker
assertion: TC-MIG-37 keeps every assertion §17 gave it and loses none, TC-MIG-32
is untouched, and the module gained five cases. The one object address in §18.4 is
a `repr()` of a local Python fake and is not data of any kind.

**Order of operations, stated so the "after the final edit" rule is checkable.**
The last edits in this correction were the controlled documents — this submission
section, the test-traceability register, the status record, the change log and the
RAID register — all made after the final edit to
`tests/web/test_migration_0013_rollback_boundary.py`. `docs/operations/web-portal.md`
is the only documentation file any test opens (TC-MIG-30) and it is **unchanged**
here, so no test result depends on a document edited in this correction; commands
1–10 and 13–14 were nevertheless rerun after the last of those edits and produced
exactly the counts above. Commands 11, 12 and 15 do not depend on the test tree.

**Historical results are kept separate and labelled.** The `1 passed, 17
deselected in 2.57s` and `18 passed in 16.30s` quoted at the head of this section
are the reviewer's pre-fix runs and are **not** closing evidence: they are runs of
the happy path, and this finding is on the failure path. §14.7.1's pre-fix
transcript, §15.4's before/after results, §16.3's `LOCK TABLE`-removed
falsification and §17.3's and §17.5's results are results of earlier trees and are
not rewritten as though rerun. No result in this section rests on a run with
`TEST_DATABASE_URL` unset, none is a fixture setup failure, and no PostgreSQL
concurrency test was skipped.

### 18.6 Every file changed by this fifth correction

| File | Change |
|---|---|
| `tests/web/test_migration_0013_rollback_boundary.py` | `import contextlib`; new `CLEANUP_REAP_SECONDS`, `CLEANUP_JOIN_SECONDS`, `CLEANUP_SETTLE_SECONDS`, `CLEANUP_WRITER_OWNER`, `CONTROLLED_FAILURE`; `_reap()`'s post-kill collection bounded; new `_bounded_reap()`, `_HeldLockCleanup`, `_released()`, `_job_table_residue()`, `_await_quiet()`, `_RecordingChild`, `_UnreapableProcess`, `_FakeTransaction`, `_FakeConnection`, `_parked_writer()`; TC-MIG-37's `finally` block replaced by `with _released(cleanup)` and its docstring extended with the bounded-cleanup paragraph; the identical unbounded `kill(); communicate()` shape in the three sibling concurrency cases replaced by `_bounded_reap()` with its result asserted; four new cases (TC-MIG-38…TC-MIG-41) |
| `docs/contracts/phase-3-test-traceability.md` | a dated fifth-correction amendment note; TC-MIG-38…TC-MIG-41 rows in §21.4c; a scope note stating exactly what they are and are not cited for. **TC-MIG-37's row is unchanged** |
| `docs/review/phase-3-p3-3-submission.md` | this §18 added. §17 is unchanged |
| `docs/project-management/status.md` | nineteenth update |
| `docs/project-management/change-log.md` | `C-P3.3-H` |
| `docs/project-management/raid-register.md` | `I-20` recorded and closed |

**No other file was touched.** In particular: no file under `migrations/`,
`application/`, `adapters/`, `domain/`, `tools/`, `infra/` or `models/`; no other
test module; and `docs/operations/web-portal.md`,
`docs/contracts/phase-3-logical-schema.md` and
`docs/contracts/phase-3-state-machines.md` are unchanged, because this finding and
its evidence change none of their present claims. Every other modified or
untracked path in `git status` was already modified by §12–§17 and was not touched
here. The pre-existing stash `stash@{0}: On main: temp before rebase` was never
inspected, applied, dropped or modified. Nothing was committed, pushed or
deployed; no live Discord, Google, Foundry or production service was contacted;
and no real Actor, player, guild or credential data was used.

### 18.7 What was **not** changed

Stated as the handover requires it, so the reviewer does not have to infer it.

- **No identity assertion.** TC-MIG-37's writer PID filtering, its fence-statement
  shape match, and its comparison of `pid`, `virtualtransaction`, `backend_xid`
  and `xact_start` across the queued and pre-commit observations are byte-for-byte
  what §17 left. The `finally` block was replaced; the assertions above it were
  not.
- **No queue-fairness assertion.** TC-MIG-32 keeps every assertion and its
  deliberately broad `_ungranted()` observation. The only edit inside it is the
  bounded reap in its `finally`, whose result is asserted rather than discarded.
- **No migration.** `0011`, `0012`, `0013` and `migrations/env.py` are unedited.
  The DDL and emitted SQL are byte-for-byte what §17 left and `alembic check`
  reports no metadata difference (commands 11 and 12).
- **No production statement, and no production change of any kind.** Nothing added
  here runs outside `pytest`.
- **No production pause hook.** The only pause is a `threading.Event` in this test
  module's own writer thread, between production calls, exactly as in §17.
- **No marker, sidecar, tombstone, retention-policy change or hidden schema
  object.** `tools/job_retention.py` was not touched and N-24's eligibility rule,
  30-day age, operator command and audit event are unchanged.
- **No manual deletion, truncation, shortened retention or early retention** was
  introduced as a rollback technique.
- **No weakening** of authorization, audit append-only behaviour, effect fencing,
  result publication, recovery, runtime grants or schema constraints. The upfront
  online `ACCESS EXCLUSIVE` lock and count-after-grant ordering, the offline
  `BEGIN` → lock → count/refusal → drops → `COMMIT` ordering, the retention-aware
  retained-row predicate and all four documented database states are preserved and
  still covered by commands 4 and 6.
- **`FilesystemArtifactStore`'s production default `ancestors.ceiling is None`** is
  unchanged and still asserted by its control case; the ordinary P3.3 tests still
  use the explicit bounded test seam. The two new real-PostgreSQL parameters run
  under the same fixtures as TC-MIG-37 and change nothing about it.
- **N-24 eligibility, age, audit and operator controls** are unchanged.

### 18.8 Security, integrity, availability, runtime-role and deployment order

Unchanged from §17.7, because no production behaviour changed. Restated so the
security reviewer does not have to infer it:

- **Security.** No new caller-reachable path exists; nothing added here runs
  outside `pytest`. `_job_table_residue()` reads only `pg_locks` and
  `pg_stat_activity` — never `reconciliation_jobs` — and runs as the test role
  against the disposable database. The only signals sent are `SIGKILL` to a test's
  own Alembic child. `pg_cancel_backend` is unchanged, still used only by tests
  against a backend of their own role, and appears in no production module. The
  new fakes are local Python objects with no I/O. Refusals still report counts,
  never rows (N-25).
- **Integrity.** Unchanged, and the evidence around it is stronger rather than
  weaker: a failing concurrency case can no longer strand a live migration child
  holding `ACCESS EXCLUSIVE` on `reconciliation_jobs`, a writer blocked behind it,
  an open writer transaction, or the holder's `alembic_version` row lock — any of
  which could have corrupted the *next* test's evidence in a shared disposable
  database. The window in which a committed effect could be silently destroyed
  remains closed.
- **Availability.** Unchanged: the downgrade waits for a draining worker rather
  than racing it (**RR-24**), visible in `pg_locks`/`pg_stat_activity`. No
  `lock_timeout` is set and none was added; the new bounds are test-side only.
- **Runtime role.** Untouched. It still holds no `DELETE` on
  `reconciliation_jobs`; `tests/test_runtime_grants.py` and
  `tests/web/test_p3_2_runtime_grants_and_bounds.py` pass unchanged (command 10),
  and `infra/postgresql/runtime-grants.sql.tmpl` was not edited.
- **Deployment order.** Unchanged and still `docs/operations/web-portal.md` §3.6:
  roll forward is **migrate then deploy**; roll back is **stop every worker,
  confirm no lease is live, run the preflight, downgrade, then deploy the older
  code**, and only while the preflight returns two zeros.

### 18.9 Open decisions and residual risks — all retained

Nothing below is closed, reinterpreted or self-approved by this correction.

- **The retention-aware rollback policy remains a proposal awaiting
  Peter/Acceptance Authority ratification.** RAID **D-09**, change-log
  `C-P3.3-D` / `C-P3.3-E` / `C-P3.3-F` / `C-P3.3-G` / `C-P3.3-H`. **P3.G3 is not
  claimed closed and the rollback policy is not self-approved.**
- **The fourth correction's writer-identity result is retained as accepted
  sound**, exactly as the reviewer recorded it. §17 is unchanged.
- **Peter's other decisions are unchanged and untouched:** RAID **I-11**
  (`snapshot_folder_selections`) and the **R-41 versus SM-05** controlled
  amendment.
- **The §13 items are unchanged and still awaiting the same ratification:** the
  SM-05 amendment of `C-P3.3-C`, `EFFECT_RECOVERY_LIMIT = 20`,
  `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` and the sweep's `MAX_LIMIT = 10 000`.
- **Residual risks unchanged:** RR-16 remains withdrawn; RR-17 and RR-18 are
  unchanged; RR-19 stands as restated to the retained-row predicate; RR-24 is
  unchanged.
- **I-06 and A-05 are unchanged and still open.** Staging-class checks remain
  unrun — TC-PERF-01/02/03, TC-LIM-02, TC-SEC-07's browser half and
  TC-OPS-01…05 — and the operational half of §3.6 is documented rather than
  exercised, because staging does not exist.
- **§16.8's stated limitation of TC-MIG-37 is unchanged and is not narrowed by
  this correction.** The case still observes the granted lock *after* the revision
  body has run, so it does not bind that lock to the guard's own `LOCK TABLE`; the
  lock's placement before the count remains TC-MIG-31's claim. This correction
  changed the case's **cleanup**, not its property.

### 18.10 What is requested

**Another independent implementation re-review, and a separate security-focused
re-review**, of this section and of the code and documents it describes.

**One decision inside this slice has already been taken.** Asserting the bounded
collection **at the call** (§18.3, `_RecordingChild`) was put to the maintainer
and **endorsed on 2026-08-19**. The reason it needed a decision: a real Alembic
child killed with `SIGKILL` is collected immediately, so an unbounded
`communicate()` returns at once and no assertion about elapsed time, reaping or
residual locks can distinguish the two shapes — an earlier draft of this
correction therefore could not falsify the defect from the real PostgreSQL case at
all and rested the falsification on TC-MIG-39's fake alone. The maintainer
accepted that recording what cleanup asks of the real child asserts something
about *how* cleanup is implemented, and concurred that it is the better option
against the alternative of conceding that the real case cannot falsify this defect.
This is a **design concurrence on one evidence technique**, not a gate approval:
it ratifies nothing else in §18, P3.G3 remains open, and the independent reviewer
is explicitly free to disagree on the merits and say so.

**Whether to formalise the concurrence is deliberately still open and is a
decision for after the review.** It is recorded here, in the review handover, and
in the "Technical Lead and specialist reviews" line of change-log `C-P3.3-H`, and
**not** as a numbered RAID decision or its own change-log decision entry — on its
own it is an evidence technique inside one test module rather than a plan,
architecture or contract change, and formalising it now would blur it against the
outstanding ratifications (**D-09** and the §13, §14, §16 and §17 items). The
reviewers are asked to say whether they think it should become a recorded
decision — for instance if it sets a precedent for how P3.3's concurrency and
cleanup evidence is written, if it constrains future corrections, or if it should
be reversed. The maintainer will then decide whether to formalise it, leave it as
a concurrence, or withdraw it.

Two further things are offered for the reviewer's judgement rather than presented
as settled:

1. the **deliberate extension** in §18.1 — bounding `_reap()`'s own post-kill
   collection and the identical unbounded shape in the module's three sibling
   concurrency cases. It is the same two-line substitution at each site with no
   restructuring, and it can be rejected without affecting the correction to
   TC-MIG-37;
2. the **trade in §18.2** — a migration child that survives two bounded
   `SIGKILL` collections is reported and stepped over rather than aborting the
   release, so that the row lock, the holder connection and the writer
   transaction are still released.

**P3.G3 remains open and is not claimed closed.** It remains open until this
finding is accepted as corrected, the failure-path evidence in §18.5 is
independently rerun, the retention-aware rollback policy is ratified and recorded
(**D-09**), the outstanding maintainer decisions from §13, §14, §16 and §17 are
recorded, and this correction passes both re-reviews. **P3.4 has not started.**

## 19. Sixth migration-rollback correction (2026-08-19)

The independent review of the fifth correction (§18) **did not accept it**. It
recorded that the subprocess collection and the writer join were bounded as
claimed, and that the claim built on top of them — that
`_HeldLockCleanup.release()` is bounded on **every** path — is false.

**Both re-reviews of §18 remain outstanding as re-reviews of this section
instead. `C-P3.3-H` is unaccepted, P3.G3 is open and P3.4 has not begun.**

### 19.1 F1 — the 25-second ceiling omitted the two database calls

**The finding, stated as the reviewer stated it.** `seconds_ceiling` counted

```text
2 × subprocess reap timeout + writer join timeout
```

and nothing else. Yet `release()` also called

```python
self._holding.rollback()
self._holder.close()
```

Both are synchronous SQLAlchemy/psycopg operations with no enforceable timeout.
**Catching an exception does not bound an operation that never returns** — it
describes one that ended. If the rollback blocked, `close()` and the writer join
were never reached. If the close blocked, the writer join was never reached. The
documented 25 seconds therefore described a release that could not be shown to
end at all.

**Why the fifth correction's own evidence did not falsify either path.** Two
reasons, and they are the same two the fifth correction's finding had:

- **TC-MIG-38 runs against healthy PostgreSQL.** A `rollback()` and a `close()`
  on a healthy local connection return in microseconds, so every elapsed-time,
  residue and "holder closed" assertion passes against the unbounded shape
  exactly as it does against a bounded one. A regression that only measures a
  healthy database cannot see this defect at all; and
- **`_FakeTransaction` and `_FakeConnection` return instantly.** They were
  written to stand in for a database, not for a database that has stopped
  answering, so TC-MIG-39…TC-MIG-41 never entered the branch either.

**This is the same class of defect as the fifth correction's original finding.**
An unbounded cleanup step prevents later resources from being released. In this
module that is not an abstract risk: the resource the rollback holds is the
externally taken `alembic_version` row lock, and `freedom_test` is a **shared**
disposable database. A cleanup that never reaches the rollback leaves that lock
live and contaminates the next case's evidence.

**No production defect is implied and none was found.**
`migrations/versions/0013_effect_publication_recovery.py` is unchanged, as are
`0011`, `0012` and `migrations/env.py`. This is a test-cleanup and
review-evidence correction, as §18 was.

### 19.2 The correction — bound the wait, own the connection, dispose of the backend

Nothing can force SQLAlchemy or psycopg to return. What a test *can* control is
**how long it waits**, and **who owns the object while it waits**. Both are
addressed, and the second matters as much as the first: a bound imposed by
handing a call to a thread is worthless — worse than worthless — if the thread is
then hidden, or if the resource it is still holding is handed to somebody else.

**1. Every database call is made by a thread of its own, and the *wait* is
bounded.** `_bounded_call(what, action, seconds)` starts a daemon thread, joins
it with `seconds`, and returns `(problem, orphan)`:

```python
owner = threading.Thread(target=run, name=f"held-lock cleanup: {what}", daemon=True)
owner.start()
owner.join(timeout=seconds)
if owner.is_alive():
    return (f"{what} did not return within {seconds:.0f}s; …", owner)
```

The orphan is **returned, not swallowed**: the release records it in
`orphaned_threads`, reports it as a problem, and never touches what it owns
again.

**2. The holder is detached from its pool at construction**, while only the
calling thread can possibly be inside it:

```python
self.pool_detached, self._detach_problem = self._detach_the_holder()
```

`Connection.detach()` is pure pool bookkeeping — no round trip, nothing that can
block — and after it, closing the connection closes the DBAPI connection outright
instead of returning it. This is what makes "never return a connection to the
pool while another thread may still operate on it" hold on **every** path rather
than only on the paths that noticed a problem. It is done at construction, not at
the moment a problem is detected, because by then it is too late to do it safely.

**3. A blocked call's object is never touched again — and an independent disposal
is attempted in its place.** If the rollback does not return, closing the same
connection from the release would race the thread still inside it. So the close
step reports that it deliberately did not, and the next step disposes of the
resource that actually matters — the **backend**, from a *different* connection:

```sql
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE pid = :pid AND backend_start = :backend_start
```

`backend_start` is matched beside the pid because PostgreSQL reuses process ids
and a disposal that named a pid alone could end an innocent backend. Both
together name one backend and only one — the one this test opened, recorded by
`_backend_identity()` before anything could block. Terminating it releases the
`alembic_version` row lock into the shared database, which is the whole point,
and it also causes the stuck client call to return so its thread can end. The
disposal's own connection is detached before use, so if *it* is the call that
blocks, the thread left owning it owns nothing the pool can hand to anybody else.

**4. The order, and the guarantee that every later step is attempted.**

| # | Step | Bound | Why here |
|---|---|---|---|
| 1 | `may_commit.set()` — release the writer's commit event | none needed | Unconditional and **first**, so a failure anywhere cannot leave the writer parked in an open transaction until its own `LOCK_WAIT_SECONDS` expires |
| 2 | End and boundedly reap a surviving migration child | `2 × CLEANUP_REAP_SECONDS` | **Before** the row lock is released: a migration *released* rather than *ended* would commit the drops the case asserts were undone, and ending it unblocks a writer queued behind its table lock. Unchanged from §18 |
| 3 | Roll back the `alembic_version` row lock | `CLEANUP_DATABASE_SECONDS` | **New bound.** On its own thread |
| 4 | Close the holder connection | `CLEANUP_DATABASE_SECONDS` | **New bound.** A separate step, so a rollback that raises cannot leak the connection and one that never returns cannot stop this being attempted. If step 3 orphaned the connection this step reports that it deliberately did not touch it |
| 5 | Dispose of the holder's backend independently | `CLEANUP_DISPOSE_SECONDS` | **New step.** Attempted when and only when step 3 or 4 did not return. Nothing to dispose of when both completed — terminating a backend that is already closing would report a leak the cleanup does not have |
| 6 | `writer.join(...)`, only if started and alive | `CLEANUP_JOIN_SECONDS` | Unchanged from §18 |

`release()` enters each step through one wrapper that records it in
`attempted` **before** calling it, so "every later step was attempted" is read
from the object rather than from the source:

```python
def step(what: str, action) -> None:
    self.attempted.append(what)
    try:
        problem = action()
    except BaseException as error:
        problems.append(f"cleanup step {what!r} raised {error!r}")
    else:
        if problem:
            problems.append(problem)
```

Every case that drives a release asserts `cleanup.attempted == CLEANUP_STEPS` —
all six, in order — on blocked and unblocked paths alike.

**5. The orphan accounting, stated as a trade rather than as a success.** A
thread left inside a call that never returns is a cost, not a clean result, and
this correction does not pretend otherwise:

- it is a **daemon**, so it cannot keep the pytest process alive at the end of
  the session — no hidden live non-daemon thread;
- it is **recorded** on `orphaned_threads` and **reported** as a problem, which on
  a failing path becomes a note on the assertion under diagnosis and on a passing
  path fails the case — no silent daemon thread;
- what it owns is **detached from the pool**, so it is not a usable pooled
  connection and cannot reach another case; and
- nothing else touches that object, so no connection is returned to the pool, or
  operated on, while that thread may still be inside it.

If a maintainer prefers to abort the release rather than continue past an
orphaned connection, that is a decision to record; the reasoning for continuing
is the same as §18's for an unreapable child — the writer thread, its transaction
and the migration child are still releasable, and requirement 5 forbids leaving
*those* behind because one other thing is stuck.

### 19.3 The complete worst-case timing calculation

```python
CLEANUP_REAP_SECONDS     = 5.0    # per bounded collection; the reap costs at most 2 ×
CLEANUP_DATABASE_SECONDS = 5.0    # per database call: the rollback, and the close
CLEANUP_DISPOSE_SECONDS  = 5.0    # the independent server-side disposal
CLEANUP_JOIN_SECONDS     = 15.0   # the bounded writer join
```

```python
@property
def seconds_ceiling(self) -> float:
    return (
        2 * self._reap_seconds        # step 2
        + 2 * self._database_seconds  # steps 3 and 4
        + self._dispose_seconds       # step 5
        + self._join_seconds          # step 6
    )
```

| Bounded wait | Worst case |
|---|---|
| step 2 — first bounded collection | 5.0 s |
| step 2 — second bounded collection, after `SIGKILL` | 5.0 s |
| step 3 — bounded rollback | 5.0 s |
| step 4 — bounded close | 5.0 s |
| step 5 — bounded independent disposal | 5.0 s |
| step 6 — bounded writer join | 15.0 s |
| **`seconds_ceiling`** | **40.0 s** |

Step 1 performs no wait. Steps 3 and 4 are both counted because both can consume
their bound on the same run — a rollback that returns at 4.9 s followed by a close
that never returns. Step 5 is counted even though it runs only after a step did
not return, because `seconds_ceiling` is a **worst case**, not a typical case.
40.0 s is below the 60-second `LOCK_WAIT_SECONDS` production-test ceiling, and
the measured healthy-path release is a fraction of a second.

**The calculation, the documentation and the tests agree**, which the fifth
correction's did not: `seconds_ceiling` is the value TC-MIG-38, TC-MIG-39,
TC-MIG-42 and TC-MIG-43 assert their measured elapsed time against, and the
per-step bounds in the table above are the constructor's own parameters.

### 19.4 The two regressions, and the falsification

**TC-MIG-42 — the rollback does not return.**
`test_the_held_lock_cleanup_is_bounded_when_the_row_lock_rollback_never_returns`.
**TC-MIG-43 — the close does not return.**
`test_the_held_lock_cleanup_is_bounded_when_closing_the_holder_never_returns`.
**TC-MIG-44 — the passing-path mirror**, parametrized over both calls.

Each of the first two proves, **without waiting for the stand-in's full
"forever" period**:

| Required | Asserted as |
|---|---|
| `release()` returns within its complete documented ceiling | `elapsed < cleanup.seconds_ceiling` **and** `elapsed < _BlockingCall.STAND_IN_FOR_FOREVER` (3.0 s), measured across the whole `_released()` block |
| the blocked step is reported | a note matching `"rolling back the alembic_version row lock did not return"` / `"closing the holder connection did not return"` |
| every later step was attempted | `cleanup.attempted == CLEANUP_STEPS` — all six, in order |
| the writer's commit event was set and its bounded join was attempted | `may_commit.is_set()`, and the parked stand-in writer is `not writer.is_alive()` — it was released *by* the cleanup and joined *by* the cleanup |
| the primary assertion remains the exception under diagnosis | `pytest.raises` catches `CONTROLLED_FAILURE`; the cleanup problems are `__notes__` on it, not in its place |
| a blocked call's object is not touched again | `holder.closed is False` on the rollback-blocked path, and the deliberate "not closed" report as a note |
| the independent disposal is attempted in its place | `disposal.calls == 1`, and it was called on a thread that is not the calling thread |
| the helper thread is accounted for | exactly one orphan; it is not the calling thread; `orphan.daemon is True`; it is the thread that entered the blocked call; `cleanup.holder_orphaned is True`; `cleanup.pool_detached is True` |
| the regression leaks nothing of its own | the stand-in is released and every orphan is joined and asserted dead before the case ends |

TC-MIG-43 additionally asserts `holding.rolled_back is True` and
`holder.entered.is_set()`, so what blocked is provably the **close** and not
something inherited from the step before it.

**Why deterministic stand-ins, and not healthy PostgreSQL.** Neither branch can
be produced on demand from a healthy local database — which is exactly why the
fifth correction's evidence did not falsify them — and a regression that blocked
for real would hang the suite instead of reporting. `_BlockingTransaction` and
`_BlockingConnection` block precisely where the real calls would, record the
thread they were called on, and stand in for "forever" with 3.0 s. The real
PostgreSQL controlled-failure case is **retained unchanged and rerun**
(TC-MIG-38, §19.6 command 3), and it is **not** claimed to prove behaviour under a
failed database connection; it proves the healthy-path release is bounded and
total, and that the collection carried a bound at the call.

**Asserted at the call, not only at the clock.** Each case asserts, first, that
the call was **not made on the calling thread**:

```python
assert holding.called_on and holding.called_on[0] is not threading.current_thread(), (
    "the rollback was made on the calling thread; that is the pre-fix shape, "
    "in which no bound on it is possible at all"
)
```

This is the same technique `_RecordingChild` applies to the subprocess
collection, for the same reason: a bound is a property of the **call**, and a
timing assertion can only see a call that happened to be slow on that run.

#### The mutation run

Three mutations, each restored before the next. **No production file was touched
by any of them and no guard was weakened to create them.**

**Mutation A — an unbounded direct `rollback()`, the rejected fifth-correction
shape:**

```python
def _roll_back(self) -> str | None:
    if self._holding is None or not self._holding.is_active:
        return None
    # MUTATION: the rejected fifth-correction shape, restored deliberately.
    self._holding.rollback()
    return None
```

```text
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ./venv-web/bin/python -m pytest -q \
  tests/web/test_migration_0013_rollback_boundary.py -k "cleanup" -rf

E       AssertionError: the rollback was made on the calling thread; that is the pre-fix
        shape, in which no bound on it is possible at all
E       assert ([<_MainThread(MainThread, started …)>] and <_MainThread(MainThread, started …)>
        is not <_MainThread(MainThread, started …)>)
E        +  where [<_MainThread(MainThread, started …)>] = <…._BlockingTransaction object>.called_on

E       Failed: DID NOT RAISE <class 'AssertionError'>

FAILED …::test_the_held_lock_cleanup_is_bounded_when_the_row_lock_rollback_never_returns
FAILED …::test_a_blocked_database_cleanup_call_fails_the_case_that_otherwise_passed[rollback]
2 failed, 7 passed, 18 deselected in 11.31s
```

**Mutation B — an unbounded direct `close()`:**

```text
E       AssertionError: the close was made on the calling thread; that is the pre-fix
        shape, in which no bound on it is possible at all
E        +  where [<_MainThread(MainThread, started …)>] = <…._BlockingConnection object>.called_on

E       Failed: DID NOT RAISE <class 'AssertionError'>

FAILED …::test_the_held_lock_cleanup_is_bounded_when_closing_the_holder_never_returns
FAILED …::test_a_blocked_database_cleanup_call_fails_the_case_that_otherwise_passed[close]
2 failed, 7 passed, 18 deselected in 11.54s
```

**Read exactly.** Each mutation fails **exactly** the two cases written for its
path, and passes the other seven — TC-MIG-38's two parameters, TC-MIG-39,
TC-MIG-40, TC-MIG-41 and the other path's two cases — which is what a targeted
regression should do and is itself evidence that the new cases test what they
claim to and not something incidental. `DID NOT RAISE` is TC-MIG-44: with an
unbounded call there is no cleanup problem, so the passing path no longer fails.
Neither run hung: 11.31 s and 11.54 s, because the stand-in ends after 3.0 s.

**Mutation C — the fifth correction's falsification, retained and rerun.**
`_bounded_reap()`'s body replaced by the pre-fix `kill(); communicate()` shape:

```text
E       AssertionError: cleanup collected the real migration child with no timeout — that
        is the pre-fix unbounded shape: [None]
E       AssertionError: the real migration child was not collected exactly once with the
        bounded reap's own timeout: []
E       AssertionError: cleanup collected the migration child with no timeout — that is
        the pre-fix unbounded shape: [None]
E       assert False   # no cleanup problem was reported at all

FAILED …::test_the_held_lock_cleanup_is_bounded_and_total_when_the_case_fails[while the writer is queued]
FAILED …::test_the_held_lock_cleanup_is_bounded_and_total_when_the_case_fails[after the fence executed]
FAILED …::test_the_held_lock_cleanup_is_bounded_when_the_migration_child_will_not_die
FAILED …::test_a_cleanup_problem_is_reported_without_replacing_the_failure_under_diagnosis
4 failed, 5 passed, 18 deselected in 10.52s
```

The same four cases fail, for the same reasons, as in §18.4 — so the
subprocess-reap falsification is not weakened by this correction's redesign.
TC-MIG-40 and the four new cases correctly still pass: none has a migration child
the mutation can reach.

**Restoration, immediately afterwards.** The final tree was checksummed before
the first mutation; the file was restored from that snapshot after each and the
checksum re-verified after the last:

```text
sha256sum -c → tests/web/test_migration_0013_rollback_boundary.py: OK
              (0d0456e71c9af4f41d3c18aec6164cd97b6b91006e95a3af3ab6bea35e1fab31)
grep -c MUTATION tests/web/test_migration_0013_rollback_boundary.py → 0
```

**No mutation is in the final tree**, and every count in §19.6 was taken after
the restoration.

### 19.5 Every file changed by this sixth correction, with before/after SHA-256

Because every P3.3 iteration is uncommitted, Git alone does not prove
per-correction provenance and is not offered as doing so. The before value for
`tests/web/test_migration_0013_rollback_boundary.py` is the value §18.4 recorded
as its restoration checksum, which is the fifth correction's final tree.

| File | Before | After |
|---|---|---|
| `tests/web/test_migration_0013_rollback_boundary.py` | `9cbc1a73d4f4b5cf0ad9c161ff80e7752bd775f27dfaf6088f5e043f38d7b558` | `0d0456e71c9af4f41d3c18aec6164cd97b6b91006e95a3af3ab6bea35e1fab31` |
| `docs/contracts/phase-3-test-traceability.md` | `c02e7243bfddd1d2479cabe3eef46811dd5654d3f41a987c7ee7f973f71ba1d2` | `c5442287a8646e2645899260124f2f53cc7c843be56cf73668bf2ad577162fa0` |
| `docs/review/phase-3-p3-3-submission.md` | `e71085037059de953b0d1d2cac8f89f0d06f1c24bf7e263a234959c01689a77e` | **cannot be embedded in itself** — see the note under this table |
| `docs/project-management/status.md` | `57e128d61adb5f5591c5c001fb7c54df1f549a04483b55a246a4319fe2699d06` | `13a4f1b66387162303021798d56db5692d3f396e6a4c8fffb6caf1f56f91efe2` |
| `docs/project-management/change-log.md` | `702cdfd1209ae1ce444e75f7195c8b6fb1215fd32bfae18e6505be039bf3e505` | `130d8470cee4893286d5cf0c6b5f8b4c4695b75bd3389e09ef5a36ab91c56f23` |
| `docs/project-management/raid-register.md` | `6512d97c0bddb13e03b1e85043a99b229aa6fa45be66438e1ffb07bc57a7dfaa` | `73e89eed4d0fea04b47bf33ee93c75686b63010c144ed23340e57404176895d4` |


**Why one cell says what it says.** A file cannot contain its own SHA-256: writing
the value into this table changes the value. This section is the last edit in the
correction, so its after-value is quoted in the handoff message that accompanies
this submission and is reproducible with `sha256sum
docs/review/phase-3-p3-3-submission.md` against the delivered tree. The other five
after-values above were taken after the final edit to each of those files, and
none of them is edited again by this correction.

**The exact edited regions of the test module**, so the reviewer does not have to
diff to find them:

| Region | Change |
|---|---|
| the cleanup-ceiling constants | `CLEANUP_DATABASE_SECONDS` and `CLEANUP_DISPOSE_SECONDS` added beside the existing `CLEANUP_REAP_SECONDS`/`CLEANUP_JOIN_SECONDS`/`CLEANUP_SETTLE_SECONDS`; none of the existing values changed |
| after `_bounded_reap()` | new `_bounded_call()`, `_backend_identity()`, `_backend_disposal()` |
| `_HeldLockCleanup` | docstring records the sixth finding; constructor gains `database_seconds`, `dispose_seconds`, `dispose`, and the `attempted` / `orphaned_threads` / `holder_orphaned` / `pool_detached` records; new `_detach_the_holder()`; `seconds_ceiling` now counts all six waits; `release()`'s `step()` records `attempted`; `_roll_back()` and `_close_the_holder()` bounded; new `_dispose_of_the_backend()` step; `_join_the_writer()` records a writer it could not join. **`_released()` is unchanged** |
| TC-MIG-37 | `_backend_identity(holder)` taken before the case begins and `dispose=_backend_disposal(...)` passed to the cleanup; docstring's cleanup paragraph extended. **No assertion added, removed or altered** |
| TC-MIG-38 | the same two-line construction change, plus **added** assertions on `attempted`, `orphaned_threads`, `holder_orphaned` and `pool_detached`. No existing assertion changed |
| `_FakeConnection` | gains `detach()`; nothing else changed |
| after TC-MIG-41 | new `_BlockingCall`, `_BlockingTransaction`, `_BlockingConnection`, `_RecordingDisposal`, `CLEANUP_STEPS`, the four `BLOCKED_*` bounds, `_blocked_cleanup()`, `_assert_the_orphan_was_accounted_for()`, `_assert_the_orphan_ends()`, and TC-MIG-42…TC-MIG-44 |

**No other file was touched**, and no additional file needed to be. In
particular: no file under `migrations/`, `application/`, `adapters/`, `domain/`,
`tools/`, `infra/` or `models/`; no other test module; and
`docs/operations/web-portal.md`, `docs/contracts/phase-3-logical-schema.md` and
`docs/contracts/phase-3-state-machines.md` are unchanged, because this finding
and its evidence change none of their present claims. Every other modified or
untracked path in `git status` was already modified by §12–§18 and was not touched
here. The pre-existing stash `stash@{0}: On main: temp before rebase` was never
inspected, applied, dropped or modified. Nothing was committed, pushed or
deployed; no live Discord, Google, Foundry or production service was contacted;
and no real Actor, player, guild or credential data was used.

### 19.6 Final-tree evidence

All commands were run from `/opt/discord-bots/freedom-bot` with
`TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'` exported, **serially** —
the disposable `freedom_test` database is shared by both virtualenvs and running
the suites concurrently produces dozens of spurious failures. Every count below is
the literal result of the run named, taken **after the last edit to any file in
this correction**. Nothing is derived and no earlier count is reused. Wall-clock
durations are reproduced for context and vary by a few percent between runs on
this host; no count depends on one.

| # | Command | Exact result |
|---|---|---|
| 1 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k "never_returns or otherwise_passed" -rs` | **4 passed, 23 deselected** in 1.37s — the new rollback-blocked and close-blocked cases and both mirror parameters (TC-MIG-42, TC-MIG-43, TC-MIG-44 ×2) |
| 2 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k "cleanup" -rs` | **9 passed, 18 deselected** in 5.69s — every cleanup case in the module (TC-MIG-38 ×2, TC-MIG-39…TC-MIG-41, TC-MIG-42, TC-MIG-43, TC-MIG-44 ×2) |
| 3 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k under_the_held_lock -rs` | **1 passed, 26 deselected** in 2.24s — TC-MIG-37 alone |
| 4 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -k "in_flight_effect or under_the_held_lock or behind_a_pending_lock" -rs` | **3 passed, 24 deselected** in 4.04s — the three concurrency selections named in the fifth handover |
| 5 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0013_rollback_boundary.py -rs` | **27 passed** in 19.94s (23 + 4 new). **No skips**; the module is `pytest.mark.database` and its fixtures resolve the disposable URL or fail |
| 6 | `./venv-web/bin/python -m pytest -q tests/web/test_migration_0011_round_trip.py tests/web/test_migration_0012_round_trip.py tests/web/test_migration_0013_round_trip.py tests/web/test_migration_0013_rollback_boundary.py -rs` | **38 passed** in 24.87s — all `0011`, `0012` and `0013` migration tests (4 + 3 + 4 + 27) |
| 7 | `./venv-web/bin/python -m pytest -q tests/web/test_p3_3_jobs.py tests/web/test_p3_3_worker.py tests/web/test_p3_3_effect_fence.py tests/web/test_p3_3_effect_recovery.py tests/web/test_p3_3_job_retention.py -rs` | **109 passed, 20 warnings** in 7.09s — every P3.3 jobs, worker, effect-fence, effect-recovery and retention test. The 20 warnings are the same pre-existing `httpx` per-request-cookie `DeprecationWarning`s §18.5 recorded; nothing here adds or removes a warning |
| 8 | `./venv-web/bin/python -m pytest -q tests/web` | **1438 passed, 80 skipped** in 97.22s. The 80 skips are the two permission-matrix modules' permitted cells (54 + 26), which the per-route success cases assert; unchanged from §18. The pass count is §18's 1434 plus the 4 new cases |
| 9 | `./venv/bin/python -m pytest -q` | **2293 passed** in 137.67s — the full bot suite, unchanged |
| 10 | `./venv-web/bin/python -m pytest -q tests/test_database_postgresql.py::test_migration_matches_table_metadata tests/test_database_postgresql.py::test_migrations_apply_to_empty_postgresql_and_downgrade tests/test_runtime_grants.py tests/web/test_p3_2_runtime_grants_and_bounds.py tests/test_migration_safety.py -rs` | **81 passed** in 5.72s — metadata parity, the empty-database `base ↔ head` round trip, the effective runtime-grant tests and the migration-safety tests. **No grant changed** |
| 11 | `alembic downgrade base`, `alembic upgrade head`, `alembic check`, through the suite's own guarded environment | rc **0**, rc **0**, rc **0** with output **"No new upgrade operations detected."**; `SELECT version_num FROM alembic_version` = **`0013`** |
| 12 | `alembic downgrade 0013:0012 --sql` | rc **0**. Emitted order, by byte offset: `BEGIN;` (1314) → `LOCK TABLE reconciliation_jobs IN ACCESS EXCLUSIVE MODE` (2661) → `RAISE EXCEPTION` (3122) → `DROP CONSTRAINT ck_…_committed_effect_is_never_denied` (3966) → `DROP CONSTRAINT ck_…_effect_result_accompanies_the_fence` (4072) → `DROP COLUMN effect_result` (4165) → `UPDATE alembic_version SET version_num='0012'` (4193) → `COMMIT;` (4284). Strictly increasing, so the documented order holds. The positional assertions and the `psql` **execution** of this script are TC-MIG-33 and TC-MIG-34, inside command 5 |
| 13 | `./venv-web/bin/python -m compileall -q` on **every changed Python file** (54 files: `git diff --name-only` plus `git ls-files --others --exclude-standard`, filtered to `*.py`) | rc **0**, no output |
| 14 | `git diff --check` | rc **0**, **no output** |
| 15 | Formatter / linter / type checker | **None is installed or configured, and that is reported rather than claimed as a pass.** Re-verified for this correction: no `black`, `ruff`, `flake8`, `mypy`, `pyright`, `isort` or `pylint` executable exists in `./venv/bin` or `./venv-web/bin`, and there is no `pyproject.toml`, `setup.cfg`, `.flake8`, `.ruff.toml` or `tox.ini`. `requirements-dev.txt` carries only `pytest` and `pytest-asyncio`. Introducing one would be a drive-by dependency change this correction is not authorized to make |

**A passing count is not closing evidence for a non-returning cleanup path, and
is not offered as such.** The closing evidence for this finding is §19.4's
deterministic stand-ins and its three mutation runs, plus the code review the
reviewers are asked for. Commands 1–15 exist to show that nothing else broke.

**Manual diff review.** No secret, credential, token, real Discord snowflake, real
guild id, real Actor name or production identifier appears in any file changed by
this correction. `.env`, `yt-cookies.txt` and every credential file were never
read, printed or modified. No unsafe log line was added — the correction adds no
logging at all, and no `print()` call exists anywhere in it, including in the
three mutations, which asserted on recorded state instead. No unrelated file was
edited. No test was relaxed, skipped, deleted or given a weaker assertion:
TC-MIG-37 keeps every assertion §17 and §18 gave it, TC-MIG-38 gained four
assertions and lost none, TC-MIG-39…TC-MIG-41 are unchanged, TC-MIG-32 is
untouched, and the module gained four cases. The `_MainThread` reprs in §19.4 are
`repr()`s of a local Python thread object and are not data of any kind.

**Order of operations, stated so the "after the final edit" rule is checkable.**
The last edits in this correction were the controlled documents — this submission
section, the test-traceability register, the status record, the change log and the
RAID register — all made after the final edit to
`tests/web/test_migration_0013_rollback_boundary.py`.
`docs/operations/web-portal.md` is the only documentation file any test opens
(TC-MIG-30) and it is **unchanged** here, so no test result depends on a document
edited in this correction; commands 1–10 and 13–14 were nevertheless rerun after
the last of those edits and produced exactly the counts above. Commands 11, 12 and
15 do not depend on the test tree.

**Historical results are kept separate and labelled.** §18.5's counts are results
of the fifth-correction tree and are not rewritten as though rerun, and §18.4's
falsification transcript is retained as the fifth correction's, with its rerun
against *this* tree recorded separately as Mutation C above. §14.7.1, §15.4,
§16.3, §17.3 and §17.5 are likewise results of earlier trees. No result in this
section rests on a run with `TEST_DATABASE_URL` unset, none is a fixture setup
failure, and no PostgreSQL concurrency test was skipped.

### 19.7 What was **not** changed

- **No production code of any kind.** Nothing added here runs outside `pytest`.
- **No migration.** `0011`, `0012`, `0013` and `migrations/env.py` are unedited
  and byte-for-byte what the fifth correction left, verified by SHA-256 against
  the pre-correction tree, and `alembic check` reports no metadata difference
  (commands 11 and 12).
- **No identity assertion.** TC-MIG-37's writer PID filtering, fence-statement
  shape match, writer PID assertion, and comparison of `pid`,
  `virtualtransaction`, `backend_xid` and `xact_start` across the queued and
  pre-commit observations are byte-for-byte what §17 left.
- **No queue-fairness assertion.** TC-MIG-32 keeps every assertion and its
  deliberately broad `_ungranted()` observation, and was not edited at all here.
- **The fifth correction's own decisions are kept, as the handover directs:**
  `SIGKILL` rather than `SIGTERM` for the test-owned Alembic child; migration
  collection **before** the externally held `alembic_version` row lock is
  released; reporting and stepping over an unreapable child; the bounded-reap
  substitutions in the three sibling concurrency cases and in `_reap()`; and
  `_RecordingChild` as the observation technique for the real child.
- **No production pause hook, timeout policy, migration or schema object,
  marker, sidecar, tombstone, retention change, runtime grant or
  caller-reachable path.** The only pauses are `threading.Event`s in this test
  module's own threads, between production calls.
- **No socket timeout was added and none is claimed.** A `connect_timeout` or a
  statement timeout would not be active for `rollback()` or `close()`, and
  presenting one as a bound on them would be the disguised failure the handover
  names. The bound here is on the **wait**, and the ownership consequences of
  that are stated in §19.2 rather than glossed over.
- **`_job_table_residue()` remains catalogue-only** — `pg_locks` and
  `pg_stat_activity`, never `reconciliation_jobs`.
- **No weakening** of authorization, audit append-only behaviour, effect fencing,
  result publication, recovery, runtime grants or schema constraints. The upfront
  online `ACCESS EXCLUSIVE` lock and count-after-grant ordering, the offline
  `BEGIN` → lock → count/refusal → drops → `COMMIT` ordering, the retention-aware
  retained-row predicate and all four documented database states are preserved and
  still covered by commands 5 and 6.
- **N-24 eligibility, age, audit and operator controls are unchanged**, rollback
  policy and deployment order are unchanged, and `tools/job_retention.py` was not
  touched.
- **`docs/operations/web-portal.md` is unchanged by this correction.**
- **`FilesystemArtifactStore`'s production default `ancestors.ceiling is None`**
  is unchanged and still asserted by its control case.

### 19.8 Security, integrity, availability and shared-database isolation

- **Security.** No new caller-reachable path exists; nothing added here runs
  outside `pytest`. The new helpers read only `pg_stat_activity` — never
  `reconciliation_jobs` — and run as the test role against the disposable
  database. **One new signal path is added and it is test-scoped:**
  `_backend_disposal()` calls `pg_terminate_backend()` on a backend **this test
  opened**, identified by pid *and* `backend_start` so a reused pid cannot be
  hit, and only when that test's own bounded rollback or close did not return. It
  appears in no production module, is never reachable from an HTTP route, a
  worker or a migration, and is a strictly narrower target than the existing
  test-scoped `pg_cancel_backend`, which is unchanged. Refusals still report
  counts, never rows (N-25). No secret, credential, token or real identifier is
  introduced, and the correction adds no logging and no `print()`.
- **Integrity.** Unchanged, and its *evidence* is stronger rather than weaker. The
  window in which a committed effect could be silently destroyed remains closed;
  no production statement, constraint or grant moved. What changed is that a
  failing concurrency case can no longer be stopped, before it releases anything,
  by a database call that does not return.
- **Availability.** Unchanged: the downgrade waits for a draining worker rather
  than racing it (**RR-24**), visible in `pg_locks`/`pg_stat_activity`. No
  `lock_timeout` is set and none was added; every new bound is test-side, and
  none of them is a production timeout policy.
- **Shared-database isolation — the reason this finding mattered.** `freedom_test`
  is shared by both virtualenvs and by every case in sequence. Before this
  correction, a failing TC-MIG-37 whose `rollback()` did not return would have
  held the externally taken `alembic_version` row lock indefinitely, and every
  later migration case would have queued behind it or timed out against it, so a
  single stuck cleanup could have produced a page of unrelated failures whose real
  cause was invisible. Now: the wait is bounded; the lock is released by the
  bounded rollback on the ordinary path and by the independent
  `pg_terminate_backend()` on the blocked path; the connection is detached from
  the pool at construction, so no orphaned thread can leave a live connection for
  a later case to draw; and if anything is nevertheless left behind it is named in
  the failure report instead of being inherited silently. TC-MIG-38's
  `_await_quiet()` residue poll — no `ACCESS EXCLUSIVE`/`ROW EXCLUSIVE` lock on
  `reconciliation_jobs`, no open writer transaction, no surviving migration
  backend — is retained and rerun (command 2).
- **Runtime role.** Untouched. It still holds no `DELETE` on
  `reconciliation_jobs`; `tests/test_runtime_grants.py` and
  `tests/web/test_p3_2_runtime_grants_and_bounds.py` pass unchanged (command 10),
  and `infra/postgresql/runtime-grants.sql.tmpl` was not edited.
- **Deployment order.** Unchanged and still `docs/operations/web-portal.md` §3.6:
  roll forward is **migrate then deploy**; roll back is **stop every worker,
  confirm no lease is live, run the preflight, downgrade, then deploy the older
  code**, and only while the preflight returns two zeros.

### 19.9 `_RecordingChild` remains an informal concurrence

Peter's direction, recorded here as the handover instructs and **not** elevated
into a project-wide contract: `_RecordingChild` stays an **informal technical
concurrence**. It is **not** given a numbered RAID decision and **not** given its
own change-log decision entry. Its existing localized documentation — its
docstring in the test module, §18.3, and the "Technical Lead and specialist
reviews" line of change-log `C-P3.3-H` — is sufficient. The question §18.10 left
open for the reviewers is therefore **answered by the maintainer and closed as a
concurrence**; the reviewers remain free to disagree on the technique's merits and
say so, but they are not being asked to decide whether to formalise it.

The same technique is used by TC-MIG-42 and TC-MIG-43 for the two database calls
(`called_on` rather than `collected_with`) on the same footing, and likewise
without a numbered decision.

### 19.10 Open decisions and residual risks — all retained

Nothing below is closed, reinterpreted or self-approved by this correction.

- **The retention-aware rollback policy remains a proposal awaiting
  Peter/Acceptance Authority ratification.** RAID **D-09**, change-log
  `C-P3.3-D` / `C-P3.3-E` / `C-P3.3-F` / `C-P3.3-G` / `C-P3.3-H` /
  `C-P3.3-I`. **P3.G3 is not claimed closed and the rollback policy is not
  self-approved.**
- **`C-P3.3-H` is not accepted.** The fifth correction's redesign stands only as
  far as this correction confirms it: its bounded reap, its ordering and its
  `add_note()` behaviour are retained and rerun, and its ceiling claim is
  corrected here.
- **The fourth correction's writer-identity result is retained as accepted
  sound**, exactly as the reviewer recorded it. §17 is unchanged.
- **Peter's other decisions are unchanged and untouched:** RAID **I-11**
  (`snapshot_folder_selections`) and the **R-41 versus SM-05** controlled
  amendment.
- **The §13 items are unchanged and still awaiting the same ratification:** the
  SM-05 amendment of `C-P3.3-C`, `EFFECT_RECOVERY_LIMIT = 20`,
  `EFFECT_PUBLICATION_GRACE_HEARTBEATS = 3` and the sweep's `MAX_LIMIT = 10 000`.
- **Residual risks unchanged:** RR-16 remains withdrawn; RR-17 and RR-18 are
  unchanged; RR-19 stands as restated to the retained-row predicate; RR-24 is
  unchanged.
- **I-06 and A-05 are unchanged and still open.** Staging-class checks remain
  unrun — TC-PERF-01/02/03, TC-LIM-02, TC-SEC-07's browser half and
  TC-OPS-01…05 — and the operational half of §3.6 is documented rather than
  exercised, because staging does not exist.
- **§16.8's stated limitation of TC-MIG-37 is unchanged and is not narrowed by
  this correction.** The case still observes the granted lock *after* the revision
  body has run, so it does not bind that lock to the guard's own `LOCK TABLE`; the
  lock's placement before the count remains TC-MIG-31's claim. This correction
  changed the case's **cleanup**, not its property.

### 19.11 What is requested

**An independent implementation re-review, and a separate security-focused
re-review**, of this section and of the code and documents it describes. **Do not
merge them.**

Two things are offered for the reviewer's judgement rather than presented as
settled:

1. **the ownership model.** Bounding a call by moving it to a thread means that a
   call which never returns leaves that thread alive. This correction makes that
   cost explicit — daemon, recorded, reported, owning only a detached connection,
   never touched again — rather than hiding it, and disposes of the server-side
   backend independently so the resource that matters is released anyway. If the
   reviewer or Peter judges that a materially different resource-ownership model
   is required — for example a dedicated engine per held-lock case, or aborting
   the release instead of continuing past an orphaned connection — that is a
   decision to record, and this section is the place it is being raised rather
   than assumed; and
2. **the independent disposal itself.** `pg_terminate_backend()` on a test's own
   backend is a new, test-scoped signal path. It is narrower than the existing
   `pg_cancel_backend` usage and is guarded by pid *and* `backend_start`, but it
   is new, and the security reviewer is asked to say whether they accept it.

**P3.G3 remains open and is not claimed closed.** It remains open until this
finding is accepted as corrected, the evidence in §19.4 and §19.6 is
independently rerun, the retention-aware rollback policy is ratified and recorded
(**D-09**), the outstanding maintainer decisions from §13, §14, §16, §17 and §18
are recorded, and this correction passes both re-reviews. **P3.4 has not
started.**

### 19.12 Acceptance Authority update — 2026-08-19

Peter/Acceptance Authority subsequently accepted D-09, I-11, the narrow
R-41/SM-05 completed-unconfirmed-preview → `stale` exception, the §13
effect-publication recovery amendment, and its three derived limits: 20, 3 and
10,000. The decision is recorded as change-log `C-P3.3-J`; the historical review
record above is intentionally not rewritten.

This resolves the named maintainer decisions. It does **not** accept
`C-P3.3-I`, does not substitute for the distinct security-focused review, does
not close P3.G3, and does not authorize P3.4.

### 19.13 Security review and correction acceptance — 2026-08-19

The distinct security-focused review found no blocking or major security
finding. Its report is
`docs/review/phase-3-p3-3-sixth-correction-security-review.md`; verification was
120 passing rollback-boundary, structural-guard and rejected-scope tests against
the disposable database.

Peter/Acceptance Authority accepted `C-P3.3-I` on 2026-08-19. This accepts the
sixth correction, not the defective fifth-correction ceiling claim. P3.G3 remains
open for a separate explicit gate decision, and P3.4 is not yet authorized.

### 19.14 Gate decision — 2026-08-19

Peter/Acceptance Authority accepted P3.3, closed **P3.G3**, and authorized
**P3.4** to begin. The decision is recorded as change-log `C-P3.3-K`.

This is development authorization, not deployment authorization. I-06 and A-05
remain open and continue to block public staging or production exposure; D-03
continues to govern later Gemini production integration.
