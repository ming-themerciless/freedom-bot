# P3.G1 — the composition lifecycle is explicit, one-way, and claimed once

**Date:** 2026-08-16 (fifth P3.G1 remediation of the day) · **Package:** P3.G1 ·
**Author:** working Technical Lead (Claude) · **Corrects:**
`docs/review/Handover information` — the Claude independent re-review of the
P3.G1 remediation, dated 2026-08-16, which returned *changes requested* on one
`[Important]` finding.

**Status: submitted for fresh independent implementation review and a distinct
security-focused review. Nothing here is accepted. P3.G1, RAID I-09 and RAID I-10
remain open. P3.2 and P3.3 have not been started.**

Scope is two production files and one test module. **No accepted numeric value,
environment variable, route, view model, schema, migration, dependency,
deployment value, runtime grant, provider/engine authority or visual asset
changed.** `.env.example` is unchanged. The change is a lifecycle state machine on
`WebComposition` and one call to it from the ASGI lifespan.

---

## 1. The finding

Quoted from the re-review, in full, because the correction is judged against it
rather than against a paraphrase:

> `WebComposition.aclose()` permanently closes the provider and, for a production
> composition, disposes the owned engine (`adapters/web/composition.py:499-559`).
> However, the lifespan performs no live/closed-state check before running startup
> checks and yielding (`adapters/web/app.py:292-308`). A composition can therefore
> be passed to two applications, or the same application's lifespan can be entered
> again: the second startup reports success and may begin serving while its Discord
> HTTP client is already closed. With `run_startup_checks=False` this is immediate;
> with checks enabled the disposed SQLAlchemy engine can create a replacement pool,
> so the resource checks do not prove that the closed provider is usable.
>
> The regression suite currently codifies the unsafe result. In
> `tests/web/test_request_authority_and_lifecycle.py:984-996`, the first lifespan
> closes the shared composition and the second lifespan is required to answer
> `lifespan.startup.complete`. That is not repeated *shutdown* idempotency; it is a
> new startup after shutdown. The portal can then accept requests until an OAuth
> route reaches the closed provider and fails.

Both halves are accepted without qualification. The second is the more serious of
the two: the suite did not merely miss the defect, it required it.

### 1.1 Why this is the same shape RAID I-09 tracks

Every P3.G1 finding so far has been *validate one thing, then use another*. This
one is its lifecycle twin: **release one way, admit the other**. `aclose()` was
correct, guarded, idempotent, and wired to the ASGI lifecycle by the previous
remediation — all of which was about the way *out*. Nothing was ever asked on the
way *in*. A resource whose lifetime is one-way needs a check at both ends, and
having the exit right is exactly what makes the entry look already handled.

### 1.2 Why the resource checks were never going to catch it

The re-review states this and it is worth making mechanical, because it decides
where the correction has to go.

| | What the check would see |
|---|---|
| Closed provider | Nothing. S-12/S-14/S-15 never touch the identity provider; `run_resource_checks(settings, engine)` does not receive it. |
| Disposed engine | A healthy database. `Engine.dispose()` does not invalidate the engine — it discards the pool and lets the next checkout build a replacement. S-14 opens a fresh connection through that replacement and reads the Alembic revision successfully. |

So a startup on a spent composition would have *passed* its checks and then
served requests against a closed `httpx.AsyncClient`. A check that reports health
for a resource nobody may use is worse than no check, which is why the refusal is
a state transition on the way in rather than an additional assertion inside the
checks.

---

## 2. The correction

### 2.1 `adapters/web/composition.py` — an explicit one-way lifecycle

`CompositionLifecycle` is a four-state enum, `NEW -> STARTED -> CLOSING ->
CLOSED`, exactly as the finding asked for. The member values are integers because
they are the **order** and nothing else: the machine is one-way, so monotonicity
is one comparison rather than a table of permitted pairs that a fifth state would
have to be remembered in.

| State | Meaning | `claim_for_startup()` | `aclose()` |
|---|---|---|---|
| `NEW` | Constructed; unclaimed, nothing closed | accepted → `STARTED` | runs cleanup |
| `STARTED` | One lifespan holds it and will close it | **refused** | runs cleanup |
| `CLOSING` | `aclose()` has begun, not finished | **refused** | no-op |
| `CLOSED` | Provider closed, owned engine disposed | **refused** | no-op |

`CLOSING` and `CLOSED` answer every guard identically and are still kept distinct,
because a stalled or failed shutdown is a different thing for an operator to read
than a finished one, and collapsing them would have `aclose()` report a completion
it had not reached.

Three concrete changes:

1. **`_cleanup_started: bool` is replaced by `_lifecycle: CompositionLifecycle`.**
   The boolean answered "has cleanup begun". It could not answer "may this be
   started", which is the question that was never asked. One attribute now answers
   both, so the two cannot disagree.
2. **`claim_for_startup()`** is the only transition out of `NEW`. It raises
   `CompositionLifecycleError` from every other state and **releases nothing** —
   see §2.3.
3. **`__setattr__` refuses any non-forward write to `_lifecycle`.** The write-once
   rule cannot apply to an attribute that exists in order to move, so monotonicity
   replaces it: `STARTED` cannot be wound back to `NEW`, and a `CLOSED`
   composition cannot be reopened and re-claimed with its provider closed and its
   engine disposed. Without this the state would be a lever rather than a record —
   the same reasoning that made `settings`, `engine` and `provider` write-once.

`aclose()` keeps its documented contract unchanged. It still performs cleanup **at
most once**, still moves its state before the first `await` (so an overlapping
call from another task cannot pass the guard), still disposes an owned engine in a
`finally` even when closing the provider raises, still re-raises that failure, and
still leaves a lent engine alone. What is new is one sentence of doctrine: that
idempotency is for a repeated or overlapping **cleanup**, and is not a licence to
start again.

A nested `finally` now sets `CLOSED` even when `dispose()` itself raises. That
changes nothing any guard reads — both `CLOSING` and `CLOSED` refuse a claim and
make `aclose()` a no-op — and it stops the object reporting an in-flight shutdown
for a process that has stopped.

### 2.2 `adapters/web/app.py` — the claim is the lifespan's first statement

```python
composition.claim_for_startup()
try:
    if run_startup_checks:
        composition.startup_warnings = await run_in_threadpool(...)
    yield
except BaseException as failure:
    ...
```

Two placement decisions, and both are load-bearing:

* **Before the resource checks**, because §1.2 shows the checks cannot detect the
  condition and would otherwise report a healthy portal on the way to serving
  requests against a closed client. A refusal here is an ordinary ASGI startup
  failure: the application answers `lifespan.startup.failed`, never
  `lifespan.startup.complete`, and a server that receives that stops instead of
  binding a socket — which is what "serves no request" means at this layer.
* **Outside the cleanup `try`**, which is the half that would do real damage if it
  were wrong. A composition this application was *refused* is not this
  application's to clean up. In `STARTED` the claimant that already holds it is
  still serving requests through that provider and that engine, and closing them
  from a second application's failed startup would turn a caller's mistake into an
  outage. In `CLOSING`/`CLOSED` there is nothing left to release.

`create_app()` is deliberately **not** changed to refuse a second application. The
factory opens nothing and closes nothing, so there is no resource a second call
can endanger; the constraint belongs where the resources are actually used. Its
docstring now says so.

### 2.3 What a refusal does not do

Stated separately because it is the property most easily lost in a later edit:

* it closes no provider;
* it disposes no engine, owned or lent;
* it does not move the claimant's state; and
* it names no configured value — `CompositionLifecycleError` carries a state name
  and a rule, and no URL, key, secret, host or client id.

### 2.4 Why `RuntimeError` and not `SettingsAuthorityError`

Nothing is wrong with the configuration. The graph, the provider and the engine
are the ones this process validated. What is wrong is *when*. Raising the
settings-authority type would have made a lifecycle fault indistinguishable from a
two-graph fault for any caller catching it, and `SettingsAuthorityError` is a
`TypeError`, which a lifecycle refusal is not.

---

## 3. The regression suite, corrected first

### 3.1 The case that codified the defect

`test_the_stated_idempotency_rule_holds_under_a_repeated_shutdown` tried three
shutdown paths against one composition: a completed lifespan, **a second lifespan
over the same composition**, and a direct `aclose()`. The middle one asserted

```python
assert repeated[-1]["type"] == "lifespan.shutdown.complete", (
    "a repeated shutdown is a clean no-op, not a failure"
)
```

which required the second application to have **started**. The case is now two
paths — the completed lifespan and the direct `aclose()` — and carries a note
saying why the third was removed and where the opposite assertion now lives. The
property it was written for (cleanup runs at most once) is unchanged and still
proved.

### 3.2 New section §3.1 — six cases

| Case | What it establishes |
|---|---|
| `test_a_second_application_cannot_start_on_a_closed_composition` | The direct replacement. Two applications, one composition: the first completes a lifespan, the second answers `lifespan.startup.failed` with `CompositionLifecycleError` and never `lifespan.startup.complete`; provider closes and engine disposals stay at exactly one **after** the refusal as well as before it. |
| `test_the_same_application_cannot_start_twice` | The finding's other half. Its own case because a claim implemented on the `FastAPI` object rather than on the composition would pass the case above and fail this one. |
| `test_a_second_startup_is_refused_while_the_first_is_still_serving` | The live case. The refusal happens *inside* the first lifespan; the running application's provider is proved untouched, the state is still `STARTED`, and R-03 is then driven through the real client and answers `303` from the same provider. Cleanup happens once, on the claimant's own exit. |
| `test_a_refused_claim_runs_no_resource_check` | Ordering, by counting calls: one for the allowed startup, none for the refused one. |
| `test_a_refused_claim_names_no_configured_value` | The refusal over all three channels a startup failure reaches — the exception, its whole chained context, and the `lifespan.startup.failed` traceback — against the database URL, the Discord client secret, the CSRF key and the client-digest key. |
| `test_a_composition_discarded_without_starting_still_closes` | `NEW -> CLOSING -> CLOSED`. A composition may be released before it ever serves, and is then refused a startup like any other. |

`test_a_composition_cannot_be_relieved_of_its_cleanup_guard` is extended to the
new attribute: it asserts `STARTED` inside the lifespan and `CLOSED` after, and
that every one of the four states is refused as a write once the composition is
spent.

Every case drives the **real** ASGI lifespan through `tests/web/lifespan.py`.
`httpx.ASGITransport` never opens a `lifespan` scope, so a case that assumed
otherwise would pass with no lifespan installed at all — the mistake the previous
remediation's finding 2 was about.

---

## 4. Mandatory falsification

Five mutations. Each was applied to the real production file, run, and reverted;
after every revert both files were verified against a pre-recorded
`sha256sum` manifest **and** by `cmp` against byte copies taken before the first
mutation.

| # | Mutation | Result |
|---|---|---|
| M0 | `composition.claim_for_startup()` removed from the lifespan | **7 failed, 2 passed** (of the 9 selected) — the defect reproduced exactly |
| M1 | Claim moved **after** the resource checks (and thus inside the `try`) | **2 failed, 35 passed** — `..._runs_no_resource_check` and `..._while_the_first_is_still_serving` |
| M2 | Claim kept first but moved **inside** the cleanup `try` | **1 failed, 36 passed** — `..._while_the_first_is_still_serving`: the live claimant's provider was closed by the second application's failed startup |
| M3 | The forward-only `_lifecycle` guard removed from `__setattr__` | **1 failed, 36 passed** — `..._cannot_be_relieved_of_its_cleanup_guard` |
| M4 | `claim_for_startup()` made a pure no-op (guard and state write both removed) | **7 failed, 30 passed** |

**A sixth mutation killed nothing, and it is reported rather than omitted.** It
replaced only the *refusal* inside `claim_for_startup()` (`if self._lifecycle is
not CompositionLifecycle.NEW:` → `if False:`), leaving the `STARTED` write in
place: **37 passed**. That is not a gap in the tests — it is the
monotonic `__setattr__` guard catching the second `STARTED -> STARTED` write and
raising `CompositionLifecycleError` from the other direction. The two mechanisms
cover each other, which is why M4 removes both to isolate the claim's own
contribution. Recorded because a reader who runs that single mutation and sees a
green suite deserves the explanation rather than a suspicion.

M1 and M2 are the two placement mistakes a later edit is most likely to make, and
M2 is the one that would cause an outage rather than a leak.

---

## 5. Verification

All commands were run from `/opt/discord-bots/freedom-bot` against the guarded
disposable PostgreSQL database `freedom_test` over its local Unix-domain socket.
The two suites share that database, so they were run **serially**; running them
concurrently produces dozens of false failures.

| Command | Result |
|---|---|
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/python -m pytest -q -rs tests/web` | **707 passed**, 20 deprecation warnings, **0 skipped** |
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv-web/bin/python -m pytest -q -rs tests/web/test_request_authority_and_lifecycle.py` | **37 passed**, 0 skipped |
| `TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q -rs` | **2260 passed**, 1 warning, **0 skipped** |
| `./venv-web/bin/python -m compileall -q adapters application tests/web tests/web_fixtures.py` | clean |
| `git diff --check` | clean |
| `sha256sum -c` / `cmp` after every mutation | both files OK, byte-for-byte |

Every run used `-rs`, so "0 skipped" is asserted from the report rather than
assumed.

### 5.1 Not run, and not claimed

* **`alembic check`** — no schema, migration, table or model was touched.
* **Formatter, linter, type checker** — none is configured in this repository;
  C-P3.1-Q's manual inspection stands and was not repeated.
* **Staging-class checks** — no staging environment exists (an open Phase 3
  condition).
* **Mutation testing beyond the five recorded runs.**
* **The visual-freeze manifest** — no frozen asset was touched.

---

## 6. Diff audit

Three files changed by this remediation:

* `adapters/web/composition.py` — `CompositionLifecycle`, `CompositionLifecycleError`,
  the `_lifecycle` slot replacing `_cleanup_started`, `claim_for_startup()`, the
  `lifecycle` property, the `__setattr__` monotonicity guard, and `aclose()`'s
  state transitions. No service, repository, envelope, engine, provider or
  settings behaviour changed.
* `adapters/web/app.py` — one call, plus docstrings on `_portal_lifespan` and
  `create_app`. No route, middleware, handler, cookie, digest or check changed.
* `tests/web/test_request_authority_and_lifecycle.py` — the corrected case, the
  new §3.1, and the extended attribute case.

Documentation: `docs/contracts/phase-3-test-traceability.md` (TC-STRUCT-11 amended
**by addition**), `docs/contracts/phase-3-configuration-and-dependency-contract.md`
(a new appended subsection beside the startup-refusal one, because this refusal
fails ASGI startup in the same place and an operator will look for it there),
`docs/project-management/change-log.md` (C-P3.1-W),
`docs/project-management/raid-register.md` (I-09 amended),
`docs/project-management/status.md` (ninth update, appended), and this file.

No production file outside `adapters/web/` was read from or written to. No secret,
credential, real player datum, production identifier or `.env` value appears in
any changed file.

---

## 7. Honest remaining gaps, and where a reviewer should push

1. **This is a single-process rule.** `claim_for_startup()` makes one composition
   serve one application in one Python process. It says nothing about two
   *processes* — two uvicorn workers each build their own composition, which is
   correct and intended, and each will hold its own pool. N-53's pool arithmetic is
   per-process and unchanged by this work, but a reviewer sizing PostgreSQL for a
   multi-worker deployment should not read this document as a statement about it.
2. **The claim is not a lock.** It is a check-and-set with no `await` between the
   test and the write, which makes it safe against concurrent lifespans on one
   event loop — the only concurrency an ASGI application has here. It is **not**
   thread-safe, and it is not claimed to be. Two threads entering two lifespans
   over one composition simultaneously is not a shape this process produces; if a
   later package produces one, this needs a lock.
3. **`CLOSING` is barely observable.** It exists only for the duration of the
   provider's `aclose()`, and no test asserts it directly — there is no suspension
   point a case could reliably observe it from without instrumenting the provider.
   The states either side of it are asserted. A reviewer may reasonably ask whether
   a three-state machine would have been enough; the answer given in §2.1 is that
   the distinction is for the operator, not for a guard.
4. **The suite codified the defect for a day.** The previous remediation's §3
   passed its own review with a case that required the unsafe outcome. The
   correction here removes that case, but the general lesson — that an assertion
   about *idempotency* must be checked for which operation it is actually
   repeating — is not something a test can enforce, and is offered to the review
   rather than closed.

**Requested of the implementation review:** confirm that a state transition on the
way in is the right correction rather than a check inside `run_resource_checks`;
that the claim belongs outside the cleanup `try`; that monotonic `_lifecycle` is
the right analogue of the write-once rule for an attribute that must move; and
that `NEW -> CLOSING` (closing an unclaimed composition) is correct rather than an
omission.

**Requested of the security review:** confirm that no lifetime, window, constraint
or accepted value was relaxed; that a refused claim releases nothing belonging to a
serving application; that `CompositionLifecycleError` and the
`lifespan.startup.failed` traceback carry no configured value; and that a refused
startup remains incapable of serving a request.

---

## 8. Status

**Submitted, not accepted.** P3.G1, RAID I-09 and RAID I-10 remain open. P3.2 and
P3.3 have not been started. No deployment, OAuth registration, production database
change, Foundry mutation or Google Sheet mutation is authorized by this document.
