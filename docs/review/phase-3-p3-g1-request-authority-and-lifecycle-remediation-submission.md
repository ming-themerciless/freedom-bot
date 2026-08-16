# P3.G1 — request authority and lifecycle remediation (submission)

**Date:** 2026-08-16 · **Package:** Phase 3 P3.1, under stop gate **P3.G1** ·
**Author:** Claude (working Technical Lead) · **Status:** *submitted for a fresh
independent implementation review and a distinct security-focused review.*

**This is an implementation submission, not an acceptance.** P3.G1, RAID I-09 and
RAID I-10 remain **open**. P3.2 and P3.3 have not been started. No test result
below closes a gate.

It corrects the one blocking finding left outstanding by the fresh independent
re-review of the provider/engine authority remediation
(`phase-3-p3-g1-provider-and-engine-authority-remediation-submission.md`), and
records the two structural corrections already present in the worktree, which it
preserves.

---

## 1. What was wrong

### 1.1 The outstanding blocking finding — a factory-time startup refusal leaked resources

`create_app()` constructed or accepted a `WebComposition`, called
`run_resource_checks()`, and only **afterwards** constructed the `FastAPI`
application and installed its lifespan:

```text
create_app()
  ├─ WebComposition(settings=…)        ← builds httpx.AsyncClient + owned Engine (N-53 pool)
  ├─ require_canonical_web_settings()
  ├─ run_resource_checks()             ← S-12 / S-14 / S-15 — may raise ConfigurationError
  └─ FastAPI(lifespan=_portal_lifespan(composition))   ← never reached on a refusal
```

On the production construction path both process-lifetime resources exist by the
time the checks run. A refusal propagated out of the factory, so **no application
was returned, no ASGI lifespan could ever execute, and `WebComposition.aclose()`
had no caller** — on the one path where the process was being told not to run.
The provider's HTTP client and the SQLAlchemy engine with its N-53 pool were both
left open.

This is the lifecycle-ownership claim itself, not a cosmetic edge case: a
composition that owns process-lifetime resources must release them on **every**
failed startup path as well as on a normal shutdown. It is also the same shape as
the finding it followed — a property established for one path (normal shutdown)
and then described as general.

### 1.2 A partial-construction leak found by the required audit

`WebComposition.__init__` built an owned engine and then took two further steps
that can raise on inputs the environment boundary accepts:

- `Envelope(self._settings.encryption)` — validates the token-encryption key
  register; and
- `self._require_no_second_discord_authority(self._build_provider(...))` —
  constructs a real `httpx.AsyncClient` and then applies the no-second-Discord-
  authority requirement.

On either refusal **no composition existed**, so nothing — not a caller, not a
lifespan — could ever release the engine that had already been built.

---

## 2. What changed

Two production files. No route, schema, migration, dependency, environment
variable, accepted value, deployment value or visual asset changed.

### 2.1 `adapters/web/app.py`

| Change | Effect |
|---|---|
| `run_resource_checks()` removed from `create_app()` | The factory no longer decides whether the portal may start. Returning is not a passed check. |
| `_portal_lifespan(composition, authority, *, run_startup_checks)` | The checks run **inside** the lifespan, before `lifespan.startup.complete`, closing over the exact accepted composition and the same canonical graph object every route reads. |
| Checks cross the seam through `run_in_threadpool` | S-14 and S-15 open connections and query. In the factory this was synchronous code on a synchronous path; on a lifespan it would block the loop that must answer the startup message, which `.agents/AGENTS.md` forbids. Adds no dependency — `starlette.concurrency` is already the module's seam. |
| `except BaseException` / `_attach_cleanup_failure` / `raise`, with `await composition.aclose()` on the success path | Cleanup runs on the refusal path as well as normal shutdown, and a cleanup failure that occurs *while a refusal is unwinding* is attached beneath the refusal rather than replacing it. |

The target shape in the handover is followed with one deliberate adaptation:
`try/finally` is written as `except … / raise` plus a success-path call, because
`finally` would let a cleanup failure **replace** the `ConfigurationError` the
handover requires to be the surfaced startup failure.

### 2.2 `adapters/web/composition.py`

The two steps after the engine is recorded are wrapped, and an **owned** engine is
disposed before the constructor re-raises. `Engine.dispose()` is synchronous, so
this invents no asynchronous cleanup a synchronous constructor cannot await.

**A provider that was constructed and then rejected is deliberately not closed
there.** Its `aclose()` is a coroutine and `__init__` has no running loop it may
safely await on; inventing one would be a worse defect than the leak. That path is
reachable only from a `WebComposition` subclass whose `_build_provider` returns a
`DiscordIdentityProvider` configured from a second graph, which exists nowhere in
`adapters/`, `application/`, `domain/` or `tools/`. The limit is recorded in the
code rather than papered over.

### 2.3 Deterministic exception behaviour when both halves fail

Required by the handover, chosen and documented rather than left to Python's
default:

> **The startup refusal stays at the head of the exception. A cleanup failure
> raised while it unwinds is attached to the tail of its `__context__` chain.**

Python's default would surface the wrong one — an exception raised inside an
`except` block replaces the exception being handled — so a provider whose
transport failed to shut down would have hidden the `ConfigurationError` that
refused the boot. Attaching at the **tail** preserves any context the refusal
already carried; the `seen` set prevents a cycle; the back-reference Python
already set on the cleanup failure is cleared first for the same reason, and loses
nothing because the refusal is the exception it is being attached beneath. Both
appear in one traceback and neither is dropped. Nothing is rendered, formatted or
logged: `aclose()` states that it adds no settings value, database URL or provider
configuration to what it re-raises.

**The constructor's rule is deliberately different and is stated as such.** There,
a `dispose()` that itself failed would surface with the construction failure
chained as its `__context__` — both visible, honest, and unconstrained, because no
object escapes that path either way and there is no ASGI startup contract to keep
a particular exception at the head of.

---

## 3. Inventory: every former production `app.state` access

From the committed baseline (`git show HEAD:adapters/web/app.py`). The
request-authority correction is preserved work; it is inventoried here because the
submission is required to account for it.

### 3.1 Writes — kept, as diagnostics

| Baseline line | Access | Now |
|---|---|---|
| 119 | `app.state.composition = composition` | kept |
| 120 | `app.state.settings = settings` | kept |
| 121 | `app.state.templates = Jinja2Templates(...)` | kept (built into a local first) |
| 125 | `app.state.templates.env.autoescape = True` | now set on the local before publication |
| 132 | `app.state.address_policy = ClientAddressPolicy(...)` | kept (built into `authority` first) |

All four references remain so an operator and the suite can read them. Replacing
any of them changes what is *reported* and nothing that serves a request or runs a
startup check — asserted, not conventional (§5, properties R-1…R-8 and S-6).

### 3.2 Reads — all removed

| Baseline line | Access | Read by | Governed |
|---|---|---|---|
| 155 | `request.app.state.composition` | `_composition(request)` | which provider R-03/R-04 use; which engine every transaction opens on |
| 159 | `request.app.state.settings` | `_settings(request)` | accepted `Origin`, CSRF key, session and login cookie names/attributes, digest keys, health view |
| 163 | `request.app.state.address_policy` | `_client_digest(request)` | which address the client digest is over |
| 170 | `request.app.state.address_policy` | `_client_address(request)` | which address the rate-limit bucket is keyed by |
| 237 | `app.state.settings` | `_register_routes` opening | the graph the routes closed over |
| 762 | `request.app.state.templates` | `_render(request, …)` | the escaping policy of every HTML response (TC-SEC-08) |

Call sites those helpers had in the baseline: `_settings` 6, `_client_address` 4,
`_client_digest` 4, `_origin_is_ours` 3, `_render` 3, `_user_agent_digest` 2.

**Current production count of `app.state` reads across `adapters/`,
`application/`, `domain/`, `helpers/` and `tools/`: zero**, asserted over the AST
by `test_no_production_module_reads_app_state` (TC-STRUCT-10), whose detector is
itself falsified against a reintroduced read, against writes alone, and against a
read inside the factory.

---

## 4. The four lifecycle paths

| Path | Who runs cleanup | Owned engine | Lent engine | Provider |
|---|---|---|---|---|
| **Normal shutdown** | the lifespan's success-path `aclose()` | disposed exactly once | never disposed | closed exactly once |
| **Refused startup** (S-12/S-14/S-15) | the lifespan's `except` branch, before re-raising | disposed exactly once | never disposed | closed exactly once |
| **Lifespan body raised** | the same `except` branch | disposed exactly once | never disposed | closed exactly once |
| **Partial construction** | `WebComposition.__init__` before re-raising | disposed exactly once | never disposed | not closed — no loop to await on (§2.2) |

Repeated and overlapping calls are the composition's own at-most-once guard, set
before the first `await`; nothing on the new path changes it.

---

## 5. Test map — property to named test

All in `tests/web/test_request_authority_and_lifecycle.py` unless stated. Every
lifecycle case drives the **real** ASGI lifespan protocol through
`tests/web/lifespan.py`, because `httpx.ASGITransport` never opens a `lifespan`
scope and a case that assumed otherwise would pass with no lifespan installed.

### 5.1 The remaining finding — required properties 1…7

| # | Required property | Test |
|---|---|---|
| 1 | A refusal produces `lifespan.startup.failed` and surfaces the original typed error | `test_a_refused_resource_check_fails_asgi_startup_with_the_original_error` |
| 2 | The provider the accepted composition holds is closed exactly once | `test_a_refused_startup_closes_the_provider_exactly_once` |
| 3 | A production-owned engine is disposed exactly once | `test_a_refused_startup_disposes_a_production_owned_engine_exactly_once` |
| 4 | A lent test engine is not disposed even when startup is refused | `test_a_refused_startup_never_disposes_a_lent_engine` |
| 5 | No request can be served after the refused startup | `test_no_request_is_served_after_a_refused_startup` |
| 6 | Replacing all diagnostic `app.state` references cannot redirect the startup checks or cleanup | `test_replacing_the_state_references_cannot_redirect_checks_or_cleanup` |
| 7 | No secret in failure messages, chained exceptions, logs or ASGI protocol messages | `test_a_refused_startup_transmits_no_secret_anywhere` |

Property 5 is asserted where requests actually belong. `application_lifespan`'s
body runs between `lifespan.startup.complete` and `lifespan.shutdown`; on a
refusal the context manager raises without ever entering it, and the message
sequence contains `lifespan.startup.failed` and no `…complete`. A server that
receives that message stops rather than binding a socket — asserting instead that
a later HTTP request 404s would assert about a situation no server produces.

Property 7 reads all four channels: the surfaced exception, its **whole chained
context** (cycle-safe walk), the `lifespan.startup.failed` message's formatted
traceback — the one place on this path where source text crosses a protocol
boundary — and everything captured at `DEBUG` from every logger. Checked against
the database URL, the Discord client secret, the CSRF key and the client-digest
key.

### 5.2 Supporting cases added

| Claim | Test |
|---|---|
| A provider close that fails while a refusal unwinds does not replace it, and the transport failure stays reachable in the chain | `test_a_failing_provider_close_does_not_replace_the_startup_refusal` |
| The success path still records `startup_warnings`, from the accepted graph and engine **by identity** | `test_a_completed_startup_still_records_its_warnings_from_the_accepted_graph` |
| The factory runs no resource check; the checks run exactly once, in the lifespan | `test_the_factory_no_longer_decides_whether_the_portal_may_start` |
| A constructor that fails after building an owned engine disposes it | `test_a_constructor_that_fails_after_building_an_engine_disposes_it` |
| A constructor that fails holding a **lent** engine does not dispose it | `test_a_constructor_that_fails_never_disposes_a_lent_engine` |

### 5.3 Retained and rerun

`TC-STRUCT-10` (§1–§2 of the module, 11 cases) and `TC-STRUCT-11` (§3, 7 cases)
are retained unchanged and rerun. **TC-STRUCT-11's stated coverage in
`docs/contracts/phase-3-test-traceability.md` is updated** to say explicitly that
it covers failed-startup cleanup and partial construction, not merely normal
shutdown.

One retained case required a change, and it is a change of *where* the assertion
is made rather than of what it asserts:
`tests/web/test_canonical_settings_graph.py::test_the_application_checks_repositories_and_lifecycle_use_one_engine`
asserted that `create_app()` had run the checks. It now asserts that the factory
ran **none**, and makes the original identity assertions — the accepted graph
object and the accepted engine object — inside the lifespan where they now happen.

### 5.4 Test-infrastructure change

`tests/web/lifespan.py` gains `refused_startup()` and `RefusedStartup`, and its
existing `application_lifespan` is refactored onto a shared private
`_LifespanDriver`. The refusal path has no body to wrap, and property 7 needs to
read the `lifespan.startup.failed` message, which the context-manager form raises
past. Both helpers drive the **same** protocol implementation, so there is one
copy of the ASGI conversation rather than two that could drift. No new dependency:
`starlette.testclient`, `requests` and `asgi-lifespan` are still absent
(contract §1.3).

---

## 6. Falsification — six mutations, each reverted byte-for-byte

Baseline checksums taken before the first mutation and re-verified with
`sha256sum -c` after each restoration. **Every restoration verified OK.**

```text
765434a557d342b03c547f875c4a5e7ed043ca237b936317f87d034c6a368f23  adapters/web/app.py
bde5b2128ebfd601f102f24081dd2396228418b6263487fb3ea9557938a2b293  adapters/web/composition.py
```

| # | Mutation | Result | Restored |
|---|---|---|---|
| 1 | Reintroduce `_settings(request)` reading `request.app.state.settings`, used by `origin_is_ours` | **2 failed** — `test_the_accepted_origin_is_still_graph_as_after_the_replacement` (graph B's origin accepted) and `test_no_production_module_reads_app_state` (TC-STRUCT-10 AST guard) | ✔ both checksums OK |
| 2 | Resolve the lifespan's composition through `_app.state.composition` at **startup** | **1 failed** — `test_replacing_the_state_references_cannot_redirect_checks_or_cleanup`: the checks were handed the intruder's engine | ✔ OK |
| 2b | Resolve it through `_app.state.composition` at **cleanup** time | **2 failed** — `test_replacing_the_state_composition_cannot_redirect_cleanup` and `…cannot_redirect_checks_or_cleanup`: the original provider was never closed | ✔ OK |
| 3 | Omit lifespan cleanup entirely | **7 failed** — all four normal-shutdown cases, the idempotency case, and both refused-startup resource cases | ✔ OK |
| 4 | Remove `aclose()`'s `try/finally`, so a failing provider close skips engine disposal | **2 failed** — `test_a_failing_provider_close_still_disposes_the_owned_engine` and `test_a_failing_provider_close_does_not_replace_the_startup_refusal` | ✔ OK |
| 5 | Move `run_resource_checks()` back in front of the `FastAPI`/lifespan construction | **10 failed** — all six required-property cases, the both-fail case, the warnings case, `test_the_factory_no_longer_decides_whether_the_portal_may_start`, and the canonical-graph identity case | ✔ OK |
| 6 | Remove the constructor's owned-engine disposal | **1 failed** — `test_a_constructor_that_fails_after_building_an_engine_disposes_it` | ✔ OK |

Mutation 2 is recorded in both variants because the handover names "resolve
shutdown composition through `app.state`" and the two placements are caught by
different regressions. Each mutation failed the intended test for the intended
reason; none produced a collateral failure elsewhere in the selected sets.

---

## 7. Verification

Both suites share the guarded disposable `freedom_test` database and were run
**serially**; running them concurrently produces spurious failures.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv-web/bin/python -m pytest tests/web/test_request_authority_and_lifecycle.py -q` | **31 passed**, 0 failed, 0 skipped, 4 warnings |
| 2 | `… -m pytest tests/web/test_canonical_settings_graph.py -q` | **56 passed**, 0 failed, 0 skipped, 2 warnings |
| 3 | `… -m pytest tests/web -q -k "provider or oauth or break or glass or security or settings or numeric or struct or composition or startup or lifecycle or authority"` | **565 passed**, 129 deselected, 0 failed, 0 skipped |
| 4 | `… -m pytest tests/web -q` (complete portal suite) | **694 passed**, 0 failed, **0 skipped**, 20 warnings |
| 5 | `TEST_DATABASE_URL=… ../venv/bin/python -m pytest -q` (complete repository/bot suite) | **2260 passed**, 0 failed, **0 skipped**, 1 warning |
| 6 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv/bin/alembic check` | **`No new upgrade operations detected.`** One pre-existing `SAWarning` from `migrations/env.py:133`, unrelated and unchanged |
| 7 | `../venv/bin/python -m compileall -q adapters application tests` and the same under `../venv-web/bin/python` | Both clean |
| 8 | Formatter / linter / type checker | **None configured** — re-verified, not assumed: no `pyproject.toml`, `setup.cfg`, `.ruff.toml`, `.flake8`, `mypy.ini`, `tox.ini` or pre-commit configuration exists, and neither virtualenv contains `ruff`, `mypy`, `flake8`, `black`, `isort` or `pyright` |
| 9 | `git diff --check` | Clean |
| 10 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK** |
| 11 | `git status` / `git diff --stat` audit | See §8 |

The 20 portal warnings and the 1 bot warning are the pre-existing `httpx`
per-request-cookies deprecation and the `audioop` deprecation respectively; both
predate this work and neither count changed.

**No result above is a skip, and no guarded infrastructure was missing.**
Mutation testing was not run and is not claimed; no mutation tool is configured.

---

## 8. Final status and diff audit

Files this remediation changed:

| File | Kind |
|---|---|
| `adapters/web/app.py` | production |
| `adapters/web/composition.py` | production |
| `tests/web/lifespan.py` | test infrastructure |
| `tests/web/test_request_authority_and_lifecycle.py` | tests |
| `tests/web/test_canonical_settings_graph.py` | tests (one case relocated, one constant corrected — §9) |
| `docs/contracts/phase-3-test-traceability.md` | contract, by addition |
| `docs/contracts/phase-3-configuration-and-dependency-contract.md` | contract, dated correction appended |
| `docs/project-management/status.md`, `change-log.md`, `raid-register.md` | project management, appended |

Confirmed **unchanged**:

- **Accepted values.** No numeric register value, no policy value, no refusal
  identifier and no accepted default moved. §2.3's refusal set is unchanged in
  content; only where three of them are *evaluated* changed, and that is recorded
  in the configuration/dependency contract.
- **Environment variables and `.env.example`.** No variable added, renamed or
  removed. `.env.example` is untouched.
- **Dependencies.** `requirements-web.txt` and `requirements-web-dev.txt` are
  untouched. `run_in_threadpool` comes from `starlette.concurrency`, already the
  module's seam. No `starlette.testclient`, `requests` or `asgi-lifespan`.
- **Routes.** `ROUTE_INVENTORY` and `DEFERRED_ROUTES` are unchanged; TC-STRUCT-01
  passes.
- **Schema, migrations and deployment topology.** No migration file, table,
  constraint, `infra/systemd/` unit or deployment value changed. `alembic check`
  reports no new upgrade operations.
- **Provider and engine authority.** No parameter, hook or ownership rule changed.
  `settings`, `engine` and `provider` remain write-once behind read-only
  properties; `EngineHandle` still states ownership; `tests/web/composition_harness.py`
  remains the single substitution path and is imported by no production module.
- **Visual freeze.** 14/14 manifest entries verify.
- **Secrets.** No `.env`, credential, token, player datum, database password,
  OAuth secret or key material was read, printed, copied or included. Only
  synthetic settings and the guarded disposable database were used. No production,
  shared or TCP-forwarded database was contacted.
- **Unrelated user work.** All other uncommitted modifications and untracked files
  in the worktree are preserved. No destructive Git command was used; nothing was
  staged, committed, stashed, checked out or reset.

---

## 9. A defect found in the work being verified — declared, not folded in

While running the required sweep, five database cases in
`tests/web/test_canonical_settings_graph.py` — the previous remediation's own
uncommitted evidence — were found **failing**, and they fail on a wall clock
rather than on anything this work touched.

The module pinned its injected clock to a literal
`NOW = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)`. The repositories stamp
`created_at` from the real clock, `expires_at` is derived from `NOW`, and
`ck_oauth_transactions_expiry_after_creation` and
`ck_webauthn_challenges_expiry_after_creation` refuse a row that expires before it
was created. From 12:00 UTC on the day the module was written, every case that
inserted a row with that clock raised `IntegrityError`.

`NOW` is now anchored to the run's own clock, truncated to the second so the
arithmetic the comment asks for stays exact. **No assertion, no accepted value and
no other line changed**, and all eleven `NOW` uses are injected-clock arguments or
arithmetic against it — none compares against a database-stamped `created_at`.

It is corrected rather than reported-and-left because the mandated verification
sweep cannot produce complete evidence past a failing suite, and reported here
rather than folded silently into §2 because it is **not** part of this
remediation's scope and belongs to the review of the package that introduced it. A
suite that expires at a wall-clock time is a control that stops working without
announcing it, and the reviewer may wish to look for the same pattern elsewhere.

### Correction appended 2026-08-16 — the paragraph above was wrong

Independent re-review found that the replacement was not a fix. Read the two
preceding paragraphs as the record of what was believed at the time, not as a
current statement.

`NOW = datetime.now(timezone.utc).replace(microsecond=0)` is captured at **module
import**, while `created_at` is stamped later by something else — by
`adapters.web.repositories.utcnow()` for `oauth_transactions`, and by PostgreSQL's
`server_default=func.now()` for `webauthn_challenges`. The module therefore still
had **two clock authorities** and still depended on elapsed wall time: the failure
was postponed from "noon on the day it was written" to "whenever more than N-04's
ten minutes elapse between import and execution", which collection, an earlier
case, a debugger pause or a slow worker can each produce.

Two claims made above are withdrawn:

- **"anchored to the run's own clock … the arithmetic the comment asks for stays
  exact"** — the arithmetic was exact against an instant nothing else in the
  operation shared, which is the defect rather than its correction; and
- **"all eleven `NOW` uses are injected-clock arguments or arithmetic against it —
  none compares against a database-stamped `created_at`"** — factually true, and
  the wrong reassurance. It is precisely because nothing compared the two that no
  assertion could see the second clock; the database's check constraints saw it.

The constant is now removed entirely. Each affected operation takes its instant
from inside its own transaction, and the correction, its two regressions, its
falsification and its full evidence sweep are recorded in
[`phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md`](phase-3-p3-g1-test-clock-authority-remediation-submission-2026-08-16.md).

The verification totals in §7 above (694 portal / 2260 bot) were correct when run
and are **superseded** by that submission's sweep (696 portal / 2260 bot); the
"full evidence complete" reading of §7 does not survive this finding, because the
suite it was measured on carried a control that would stop working on its own.
P3.G1, RAID I-09 and RAID I-10 remain open.

---

## 10. Questions for the two reviews

**Implementation review** is asked to confirm:

1. that no production request or startup path resolves a process-lifetime
   authority through `app.state`, and that the AST guard's scope is right;
2. that running S-12/S-14/S-15 inside the lifespan preserves every property §2.3
   promises of them — in particular that a refused portal cannot serve a request
   and that the supervisor still observes a non-zero exit;
3. that `run_in_threadpool` is the correct seam for the checks, and that no
   database work was left on the event loop; and
4. that the constructor's engine disposal is the smallest correct fix, and that
   declining to close a constructed-then-rejected provider is the right call
   rather than a gap.

**Security review** is asked to confirm:

1. that a refused startup transmits no configured secret through the surfaced
   exception, its chained context, the `lifespan.startup.failed` traceback or the
   logs;
2. that keeping the refusal at the head of the exception while attaching a cleanup
   failure beneath it hides neither failure and creates no channel for one to
   carry data from the other; and
3. that the diagnostic `app.state` references cannot produce a reporting/behaviour
   divergence that would mislead an operator during an incident.

---

## 11. Status

**P3.G1 remains OPEN. RAID I-09 remains OPEN. RAID I-10 remains OPEN.**

Nothing in this submission is accepted. It requires a fresh independent
implementation review and a distinct security-focused review before any dependent
work continues. P3.2 and P3.3 have not been started and must not be.
