# P3.G1 — test clock authority in `tests/web/test_canonical_settings_graph.py`

**Date:** 2026-08-16 (fourth P3.G1 remediation of the day) · **Package:** P3.G1
· **Author:** working Technical Lead (Claude) · **Corrects:**
`phase-3-p3-g1-request-authority-and-lifecycle-remediation-submission.md` §9 and
the corresponding status, change-log and RAID statements.

**Status: submitted for fresh independent implementation review and a distinct
security-focused review. Nothing here is accepted. P3.G1, RAID I-09 and RAID I-10
remain open. P3.2 and P3.3 have not been started.**

Scope is one test module. **No production file was changed.** No accepted value,
route, schema, migration, dependency, deployment value, provider/engine authority,
lifecycle behaviour or visual asset changed.

> **Amended 2026-08-16 (fifth remediation of the day), by independent
> implementation re-review.** §3.1 claimed the absence of module-level datetimes
> was "asked of the AST". No such evidence existed. **§10 is that correction**: the
> missing AST regression was added rather than the claim withdrawn, and §11
> replaces §9 as this document's closing status. §3.1 carries an inline note; §4,
> §5, §6 and §7 are added to by §10 and are otherwise unchanged.

> **Amended again 2026-08-16 (sixth remediation of the day), by independent
> implementation re-review of §10.** The AST detector §10 added did not enforce the
> invariant §10.2 states: it skipped every lambda body, so an immediately invoked
> lambda captured a clock at import and was reported clean. **§12 is that
> correction**, and §13 replaces §11 as this document's closing status. §10.2's
> walked/not-walked table and §10.6's limits are superseded by §12 where they
> disagree; the earlier text is left in place and marked, not rewritten.

> **Amended a third time 2026-08-16 (seventh remediation of the day), by
> independent implementation re-review of §12.** §12's rule was right and its
> recognition of that rule was incomplete: `_invoked_lambda()` knew only
> `ast.Lambda` and a chain of `ast.Call`, so a lambda invoked through a named
> expression — `NOW = (reader := lambda: datetime.now(timezone.utc))()` — ran its
> body at import and was reported clean. **§14 is that correction**, and §15
> replaces §13 as this document's closing status. §12.2's implementation
> paragraph and §12.7's limits are superseded **in part** by §14 where they
> disagree; the earlier text is left in place and marked, not rewritten.

---

## 1. The finding, and why the previous correction was not one

The independent re-review found that

```python
NOW = datetime.now(timezone.utc).replace(microsecond=0)
```

is not a deterministic clock. It is captured **at module import**, while the rows
these cases write have their `created_at` stamped later by something else. The
change from a literal date to an import-time timestamp moved the failure from "at
noon on the day it was written" to "whenever more than N-04's ten minutes elapse
between import and execution" — collection, an earlier case, a debugger pause or a
slow CI worker are each enough. Two clock authorities remained, and the module's
result still depended on elapsed wall time.

That is the correct reading, and the previous submission's §9 claim that the
constant made the arithmetic deterministic was wrong. It is corrected here rather
than defended.

---

## 2. Timestamp-ownership trace, for every `NOW` use

Traced before choosing a correction, because the smallest honest fix depends on
who actually owns each timestamp. There were eleven `NOW` occurrences in five
cases, and every one of them was either an injected `now=` argument or arithmetic
against it. **None** of them was a value compared to a database-stamped column,
which is why the module could pass at all — and also why the two-clock defect was
invisible to every assertion it made.

| Persisted column | Who stamps it | Where |
|---|---|---|
| `oauth_transactions.created_at` | the **application**: `adapters/web/repositories.py::utcnow()`, read while the INSERT is built | `OAuthTransactionRepository.create()`, `created_at=utcnow()` (`adapters/web/repositories.py:802`) |
| `oauth_transactions.expires_at` | the **caller's injected clock**: `now + oauth_transaction_minutes` | `OAuthLoginService.start()` (`application/web/oauth.py:217`) |
| `webauthn_challenges.created_at` | **PostgreSQL**: the column is not supplied, so `server_default=func.now()` — the *transaction* timestamp — applies | `WebAuthnRepository.issue_challenge()` (`adapters/web/repositories.py:1143`); column at `adapters/database/tables.py:920` |
| `webauthn_challenges.expires_at` | the **caller's injected clock**: `now + oauth_transaction_minutes` | `BreakGlassService.begin_assertion()` (`application/web/breakglass.py:156`) |

The constraints that compare them are
`ck_oauth_transactions_expiry_after_creation` and
`ck_webauthn_challenges_expiry_after_creation` (`adapters/database/tables.py:854`
and `:924`; migration `0006_platform_identity_stage_a.py:610` and `:698`).

So a case that injected a *third* instant — one captured neither by the repository
nor by the database — had two clocks in one row, and the row's legality was the
difference between them. Per case:

| Case | Row written | Clock authority for `created_at` |
|---|---|---|
| `test_an_oauth_transaction_expires_on_the_canonical_lifetime_not_a_later_answer` | `oauth_transactions` | application `utcnow()` |
| `test_a_webauthn_challenge_expires_on_the_canonical_lifetime` | `webauthn_challenges` | PostgreSQL `now()` |
| `test_the_relying_party_a_challenge_is_scoped_to_is_the_canonical_one` | `webauthn_challenges` | PostgreSQL `now()` |
| `test_the_composition_snapshots_the_nested_settings_object_exactly_once` | `oauth_transactions` | application `utcnow()` |
| `test_a_sealed_verifier_uses_the_canonical_active_encryption_version` | `oauth_transactions` (insert), then an UPDATE-only consumption | application `utcnow()` |

### 2.1 Is this a production defect? No — and the reasoning is recorded, not assumed

The handover requires a stop-and-document rather than a silent broadening if the
trace reveals a production clock-authority defect. It does not, and the argument is:

1. In production the only callers of `OAuthLoginService.start()` and
   `BreakGlassService.begin_assertion()` are the routes and `tools/`, and each
   passes `now=utcnow()` read from the *same process clock* the repository reads
   microseconds later (`adapters/web/app.py:878`, `:909`, `:958`). `expires_at` is
   therefore `created_at + 10 minutes` to within the duration of one statement, and
   the constraint cannot be reached.
2. The failure needs an injected instant that is **unrelated** to the process
   clock. Only a test supplies one.

Two observations are nevertheless handed to the reviewer rather than acted on,
because acting on either would be a production redesign this task does not
authorise:

- **`OAuthTransactionRepository.create()` re-reads the clock** instead of deriving
  `created_at` from the `now` the service already used for `expires_at`. It is not
  observable as a defect today, for the reason above, but it *is* the same
  "two readings, one operation" shape RAID I-09/I-10 track, and `.agents/AGENTS.md`
  asks for injected clocks in time-dependent behaviour.
- **The two tables' `created_at` come from different machines' clocks in
  principle** — one from the application process, one from the database server.
  They are the same host today (OD-21/OD-22), so no skew exists; a future split
  would make `expiry_after_creation` sensitive to it.

Neither is changed here. Both are review questions in §8.

---

## 3. The correction

One file: `tests/web/test_canonical_settings_graph.py` (untracked, part of the
uncommitted P3.G1 work). The change is confined to the module's clock and to the
five cases that inject one.

**`NOW` is deleted.** In its place, `OperationClock` — a function-scoped fixture,
`operation_clock` — makes the operation and the rows it writes share **one**
clock, by taking the reading from the authority that will stamp `created_at`:

```python
@contextmanager
def begin(self):
    with self._engine.begin() as connection:
        reading = connection.execute(select(func.now())).scalar_one()
        now = reading.astimezone(timezone.utc)
        self._monkeypatch.setattr(repositories_module, "utcnow", lambda: now)
        self._readings.append(now)
        yield connection, now
```

- For the **database-stamped** row this is exact by construction: PostgreSQL's
  `now()` is `transaction_timestamp()`, fixed for the transaction, so the value
  read here *is* the value the `server_default` will write. Verified directly, to
  the microsecond, before the fixture was written.
- For the **application-stamped** row the repository's `utcnow` is bound to that
  same instant for the test. Bound rather than read: reading it would produce a
  third instant, which is the defect in miniature. `monkeypatch` undoes it at the
  end of the test.

What this is **not**: no later constant, no extended lifetime, no timestamp
captured at module or session scope, no safety margin, no reordering, no weakened
or removed constraint, no sleep, and no reliance on the suite finishing quickly.
The instant is read inside the transaction under test, so elapsed time before the
test is arithmetically irrelevant rather than merely unlikely to matter.

Each of the five cases now reads `with operation_clock.begin() as (connection, now):`
and injects `now`. Every original assertion is preserved verbatim with `NOW`
replaced by `now`:

- N-04's accepted `oauth_transaction_minutes` is still read from `settings` and
  still asserted exactly (`started.expires_at == now + timedelta(minutes=accepted)`,
  and the same value read back off the stored row);
- N-06's derived idle bound, the relying-party scoping, the single-snapshot
  identity assertions and the encryption-version round trip are untouched;
- every `lie.lying_reads == 0` and read-phase assertion is untouched;
- PostgreSQL is still the database under test, still with both check constraints
  live, and no repository, service or table is faked.

One consumption in `test_a_sealed_verifier_uses_the_canonical_active_encryption_version`
still opens an ordinary transaction: it writes no row of its own and only needs an
instant inside the transaction's accepted window, so it uses `now + 1 second` as
before.

### 3.1 Remaining module-level datetimes

> **Corrected 2026-08-16 (fifth remediation of the day), by independent
> implementation re-review.** As first written, this section said the absence was
> "asked of the AST rather than of a reader". **That was false when it was
> written.** The module did not import `ast`, no case parsed it, and nothing but a
> reader had asked anything. The paragraph also said "no module-level statement
> mentions `datetime`, `timedelta`, `timezone`", which is wrong on its face: line
> 70 is `from datetime import datetime, timedelta, timezone`. The absence was real
> and the `OperationClock` correction was unaffected, but the *evidence* claimed
> for it did not exist. §10 records what was done about it. The text below is the
> corrected claim, not the original.

**There are none, and a case now says so.** The only module-level assignment in
the file is `pytestmark = pytest.mark.database`; `datetime`, `timedelta` and
`timezone` are imported at module scope and used only inside functions. Nothing
executed while the module is imported reads or constructs an instant, so nothing
at module scope participates in persisted timestamp ordering.

That is asserted by `test_this_module_captures_no_instant_while_it_is_imported`
(§0.1, added by the correction in §10), which parses this module and fails if any
code that runs at import — a module-level statement, a class body, a decorator, or
a function's default argument — reads or constructs a datetime or clock value.
Imports, declarations, `pytestmark`, module-level `timedelta` durations and all
function-scoped datetime arithmetic including `OperationClock` itself remain
accepted. No unrelated cleanup was done.

---

## 4. The regressions, and what makes them discriminate

Both are in the same module, in a new §0 beside the clock they are about.

**`test_persisted_rows_carry_one_clock_from_creation_to_expiry`** writes both
affected tables in one operation, reads both rows back on a second connection, and
asks the only question that separates one clock from two:

```python
assert expires_at - created_at == lifetime
```

Under the import-time model this cannot hold. `created_at` is stamped when the
INSERT runs; `expires_at` was derived from an instant captured at module import;
the difference is `lifetime - elapsed`, and *elapsed* is never zero, because
import, collection and every earlier case happen in between. The case therefore
fails against the old model for the defect's own reason, and it asserts nothing
about how fast the suite runs. It also pins the accepted value —
`assert accepted == 10, "N-04's accepted lifetime, carried exactly and unchanged"` —
so it cannot be made to pass by extending a lifetime.

**`test_an_instant_captured_before_the_operation_is_refused_by_the_database`**
covers the handover's fourth requirement — that an *arbitrary* delay between
import/collection and execution cannot produce an illegal row — from the other
side, and without a sleep. It injects an instant a year before the operation
while leaving `utcnow` deliberately unbound, and asserts PostgreSQL raises
`IntegrityError` naming `expiry_after_creation` for **both** tables. A year and
eleven minutes are the same row to that constraint, and eleven minutes is one
minute past N-04; injecting the stale instant *is* what elapsed time does, so no
sleep and no timing assertion is needed. It is also the proof that the constraint
is live and unmocked, which is what makes the coherent-clock case above a result
rather than a convention.

Requirement 5 is satisfied by construction: nothing extends a lifetime, nothing
suppresses or drops a constraint, nothing replaces PostgreSQL with a fake, and the
accepted N-04 value is asserted in both directions (exactly carried when the clock
is coherent; refused by the database when it is not).

---

## 5. Mandatory falsification

The module was copied and digested first
(`sha256 d8ad755ef5daf8d630b76b08b3e43078f0f8de840340b3b6aaf1cfdff15e36eb`), then
mutated by a recorded script and restored from the copy.

**The mutation** reverses exactly the thing under test: `OperationClock.begin()`
yields a module-import-time constant instead of the transaction's reading, and
binds nothing.

```python
_IMPORT_TIME_NOW = datetime.now(timezone.utc).replace(microsecond=0)  # [- timedelta(minutes=11)]

    @contextmanager
    def begin(self):
        with self._engine.begin() as connection:
            now = _IMPORT_TIME_NOW
            self._readings.append(now)
            yield connection, now
```

### M1 — the import-time model, with no simulated delay

```
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv-web/bin/python -m pytest \
  tests/web/test_canonical_settings_graph.py -q \
  -k "one_clock or instant_captured_before or ..."
→ 1 failed, 1 passed, 56 deselected
```

```
FAILED test_persisted_rows_carry_one_clock_from_creation_to_expiry
E  AssertionError: oauth_transactions.created_at must be the operation's own
   instant. It is 2026-08-16 15:56:01.996194+00:00 and the operation's clock read
   2026-08-16 15:56:00+00:00, so the row was stamped by a clock the expiry was
   not derived from
```

The 1.996 seconds are module import and collection alone — the discriminator sees
the two clocks with no delay engineered at all.

### M2 — the same model with the operation clock deliberately advanced

The import instant is placed 11 minutes before execution, which is exactly what an
11-minute delay between import and the test produces, and is one minute past
N-04's lifetime. Run over the **whole** module:

```
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv-web/bin/python -m pytest \
  tests/web/test_canonical_settings_graph.py -q
→ 6 failed, 52 passed
```

```
E  sqlalchemy.exc.IntegrityError: (psycopg.errors.CheckViolation) new row for
   relation "oauth_transactions" violates check constraint
   "ck_oauth_transactions_expiry_after_creation"
   ... 'created_at': datetime.datetime(2026, 8, 16, 15, 56, 15, 655058, ...),
       'expires_at': datetime.datetime(2026, 8, 16, 15, 55, 13, ...)
```

Failing: the new discriminator plus all five previously-`NOW`-using cases —
`test_an_oauth_transaction_expires_on_the_canonical_lifetime_not_a_later_answer`,
`test_a_webauthn_challenge_expires_on_the_canonical_lifetime`,
`test_the_relying_party_a_challenge_is_scoped_to_is_the_canonical_one`,
`test_the_composition_snapshots_the_nested_settings_object_exactly_once` and
`test_a_sealed_verifier_uses_the_canonical_active_encryption_version`. That is the
original 12:00-UTC failure mode reproduced on demand, and it is the failure the
import-time model postponed rather than removed. `expires_at` is 15:55:13 —
stale module-import time plus ten minutes — against a `created_at` of 15:56:15.

`test_an_instant_captured_before_the_operation_is_refused_by_the_database` passed
under both mutations, correctly: it takes no clock fixture, because it is about
the constraint rather than about the harness.

### Restoration

```
cp scratchpad/original.py tests/web/test_canonical_settings_graph.py
sha256sum -c original.sha256 → tests/web/test_canonical_settings_graph.py: OK
cmp original.py tests/web/test_canonical_settings_graph.py → identical
grep -c _IMPORT_TIME_NOW … → 0
```

Byte-for-byte, verified by digest **and** by `cmp`. No other file was touched
during the falsification, and no unrelated work was overwritten.

---

## 6. Verification

Both suites share the guarded disposable `freedom_test` database and were run
**serially**; running them concurrently produces spurious failures.

| # | Command | Result |
|---|---|---|
| 1 | `TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv-web/bin/python -m pytest tests/web/test_canonical_settings_graph.py -q -k "one_clock or instant_captured_before or an_oauth_transaction_expires or a_webauthn_challenge_expires or relying_party or snapshots_the_nested or sealed_verifier"` | **7 passed**, 0 failed, **0 skipped**, 51 deselected |
| 2 | `… -m pytest tests/web/test_canonical_settings_graph.py -q` | **58 passed**, 0 failed, **0 skipped**, 2 warnings (56 before this work; +2 new cases) |
| 3 | `… -m pytest tests/web/test_canonical_settings_graph.py tests/web/test_request_authority_and_lifecycle.py -q` (TC-STRUCT-08/10/11) | **89 passed**, 0 failed, **0 skipped**, 6 warnings |
| 4 | `… -m pytest tests/web -q -k "provider or oauth or break or glass or security or settings or numeric or struct or composition or startup or lifecycle or authority"` | **567 passed**, 129 deselected, 0 failed, **0 skipped** |
| 5 | `… -m pytest tests/web -q` (complete portal suite, `../venv-web/bin/python`) | **696 passed**, 0 failed, **0 skipped**, 20 warnings (694 before; +2) |
| 6 | `TEST_DATABASE_URL=… ../venv/bin/python -m pytest -q` (complete repository/bot suite) | **2260 passed**, 0 failed, **0 skipped**, 1 warning |
| 7 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv/bin/alembic check` | **`No new upgrade operations detected.`** with the one pre-existing unrelated `SAWarning` from `migrations/env.py:133` |
| 8 | `../venv/bin/python -m compileall -q adapters application tests` and the same under `../venv-web/bin/python` | Both clean |
| 9 | Formatter / linter / type checker | **None configured** — re-verified by inspection, not assumed: no `pyproject.toml`, `setup.cfg`, `.ruff.toml`, `ruff.toml`, `.flake8`, `mypy.ini`, `tox.ini`, `.pylintrc` or pre-commit configuration exists, and neither virtualenv contains `ruff`, `mypy`, `flake8`, `black`, `isort`, `pylint` or `pyright` |
| 10 | `git diff --check` | Clean |
| 11 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14/14 OK**, 0 failed |
| 12 | `git status --short` / `git diff --stat` audit | See §7 |

**No result above is a skip, and no guarded infrastructure was missing.** The 20
portal warnings and the 1 bot warning are the pre-existing `httpx`
per-request-cookies and `audioop` deprecations; neither count changed. Mutation
testing beyond the two recorded falsification runs was not performed and is not
claimed; no mutation tool is configured.

Selected coverage in row 4 includes the provider, composition, startup, shutdown,
refusal, partial-construction, settings-construction, OAuth, WebAuthn, break-glass
and security-control cases the handover names; rows 3 and 5 contain them in full.

---

## 7. Final status and diff audit

**Files this remediation changed — one:**

| File | Kind |
|---|---|
| `tests/web/test_canonical_settings_graph.py` | tests (untracked; existing uncommitted work) |

Documentation updated after the code and evidence agreed:
`docs/contracts/phase-3-test-traceability.md` (TC-STRUCT-08 amended by addition),
`docs/project-management/status.md`, `change-log.md` (new entry C-P3.1-Q),
`raid-register.md` (I-10 clause appended), this submission (new), and a dated
correction appended to §9 of the request-authority submission.

Confirmed **unchanged**:

- **Production code.** No file under `adapters/`, `application/`, `domain/`,
  `helpers/`, `models/`, `ext/`, `tools/` or `migrations/` was modified. `git
  status` lists exactly the modifications and untracked files it listed before
  this work, with no additions beyond the new submission document.
- **Accepted values.** N-04 is unchanged and is now additionally pinned by an
  assertion. No numeric register value, policy value, refusal identifier or
  accepted default moved.
- **Routes, schema, migrations, deployment.** None changed; `alembic check`
  reports no new upgrade operations; no `infra/systemd/` unit touched.
- **Dependencies.** `requirements-web.txt`, `requirements-web-dev.txt`,
  `requirements.txt` and `requirements-dev.txt` untouched. The correction uses
  `sqlalchemy.func`, `contextlib.contextmanager` and pytest's own `monkeypatch` —
  all already in use in this suite. No new package, no `freezegun`, no
  `time-machine`.
- **Environment variables and `.env.example`.** Nothing added, renamed or removed.
- **Lifecycle and request authority.** `RequestAuthority`, the lifespan-hosted
  resource checks, `aclose()` ownership and the write-once slots are untouched.
- **Provider and engine authority.** No parameter, hook or ownership rule changed;
  `tests/web/composition_harness.py` remains the single substitution path.
- **Visual freeze.** 14/14 manifest entries verify.
- **Secrets and data.** No `.env`, credential, token, database password, OAuth
  secret, key material, raw provider response or player datum was read, printed,
  copied or included. Only synthetic settings and the guarded disposable
  `freedom_test` database over the Unix-domain socket were used. No production,
  shared, TCP-forwarded or unverified database was contacted.
- **Unrelated user work.** Every other uncommitted modification and untracked file
  in the worktree is preserved. No destructive Git command was used; nothing was
  staged, committed, stashed, checked out, reset or cleaned.

---

## 8. Honest remaining gaps and review focus

1. **The correction is scoped to one module.** Other portal test modules use their
   own `utcnow()` helper (`tests/web/conftest.py`) and seed rows with a locally
   consistent `now`, which is coherent; they were **not** audited case by case,
   because the handover scopes this task to the affected module and forbids
   unrelated cleanup. A reviewer who wants that sweep should ask for it as its own
   task.
2. **`OAuthTransactionRepository.create()` re-reads the clock** rather than
   deriving `created_at` from the operation's `now` (§2.1). Not changed, not
   observable as a production defect, and offered as a question: is a single
   injected clock per operation worth a small production change here, or is the
   repository's own reading the intended contract?
3. **Two `created_at` authorities across two tables** — application clock for
   `oauth_transactions`, database clock for `webauthn_challenges` (§2.1). Harmless
   on one host; a review question if the database is ever moved off it.
4. **`monkeypatch` on `repositories.utcnow`** is a test seam over a production
   module-level function. It is the narrowest seam available without changing
   production, and it is undone per test — but the reviewer should confirm they
   accept a bound clock over an injected one for this evidence.
5. **The suite still cannot detect a *skewed* database clock**, only a stale
   injected one. Nothing in scope claims otherwise.

**Implementation review** is asked to confirm: that the ownership trace in §2 is
complete and correct; that binding the transaction's own timestamp is the smallest
honest correction rather than a broadening; that the two regressions discriminate
for the stated reason and not incidentally; and that no assertion's policy meaning
changed.

**Security review** is asked to confirm: that no lifetime, window, constraint or
accepted value was relaxed to make these cases pass; that both expiry constraints
remain exercised against real PostgreSQL; and that nothing in the new code or the
falsification recorded a secret, a credential or a real player datum.

---

## 9. Status

**P3.G1 remains OPEN. RAID I-09 remains OPEN. RAID I-10 remains OPEN.**

All changes remain **unstaged and uncommitted**. Nothing in this submission is
accepted; it requires a fresh independent implementation review, a distinct
security-focused review and the maintainer's acceptance decision before any
dependent work continues. P3.2 and P3.3 have not been started and must not be.

---

## 10. Correction 2026-08-16 (fifth): the missing AST regression, added

**Dated correction, appended after the sections above were submitted.** It
supersedes §3.1's original wording and adds to §4, §5, §6 and §7. Everything else
in this document stands.

### 10.1 The independent-review finding

Fresh independent implementation review of the work above found that §3.1 said the
absence of module-level datetimes was "asked of the AST", and that the handoff
summary said the same thing in the words "asserted over the AST". **No such
evidence existed.** `tests/web/test_canonical_settings_graph.py` did not import
`ast`; no case in it parsed the module or inspected module-scope statements; and
therefore a module-import clock could have been reintroduced without failing
anything. The finding is accepted in full. It is the same shape as the defect the
document itself is about — a property established by reading and then described as
established by a check — and it is recorded here rather than quietly repaired.

The reviewer also confirmed that the source really does delete `NOW` and that the
`OperationClock` correction is technically coherent. The defect was in the
evidence, not in the fix.

### 10.2 What was done: the regression was added, not the claim withdrawn

Resolution 1 of the two the handover offers. A robust invariant could be stated,
so it was stated rather than the claim retracted. Two cases were added to
`tests/web/test_canonical_settings_graph.py` in a new §0.1, beside the clock they
guard. **No production file changed, and no other file's behaviour changed.**

**The invariant.** *No code that runs while this module is imported may read or
construct an instant.*

**The detector.** `import_time_clock_offenders(source, *, where)` parses the module
with `ast` and walks only the positions the interpreter executes at import time.
Its scope is a decision, and is listed in the class docstring rather than left
implicit:

| Position | Walked? | Why |
|---|---|---|
| Module-level statements | yes | this is where both deleted constants lived |
| Class bodies | yes | a class body is import-time code; a field default that captures an instant is the same staleness |
| Decorator expressions | yes | evaluated at import — `@pytest.mark.parametrize(..., [datetime.utcnow()])` is a capture |
| Default arguments of declared functions and lambdas | yes | evaluated at import, and the classic accidental capture |
| Function, method and lambda **bodies** | **no** | they run when a case calls them, which is when the operation's clock should be read — *the lambda half of this row is superseded by §12: an invoked lambda's body does run at import and is now walked* |
| `import` / `from … import` | **no** | importing `datetime` is not reading a clock, and this module must go on importing it |
| Annotations | **no** | `from __future__ import annotations` is in force, so an annotation is a string and evaluates nothing |

A finding is a reference to one of fifteen names in `INSTANT_SOURCES` — `now`,
`utcnow`, `utcfromtimestamp`, `today`, `fromtimestamp`, `fromisoformat`,
`combine`, `datetime`, `date`, `time`, `time_ns`, `monotonic`, `monotonic_ns`,
`perf_counter`, `clock` — matched as a bare name or as the last component of a
dotted reference, so `datetime.now(...)`, `dt.datetime.utcnow()`, PostgreSQL's
`func.now()` and a bare `utcnow()` are one finding each. A bare attribute
reference counts, so the alias `_clock = datetime.now` is caught at the alias
rather than one line later at the call.

**`timedelta` and `timezone` are deliberately not findings.** A duration and a
fixed UTC offset are not instants. Rejecting them would have been the "brittle or
misleading detector" the handover warns about: the guard would have said something
other than what it means, and would have forbidden a module-level
`LIFETIME = timedelta(minutes=10)` that carries no staleness at all.

**The cases.**

- `test_this_module_captures_no_instant_while_it_is_imported` — TC-STRUCT-08. Reads
  this module's own source and asserts the offender list is empty.
- `test_the_import_time_clock_guard_reports_both_forms_and_no_others` — the
  detector's own falsification, run on every suite execution rather than only once
  by hand (§10.3 records the one-off mutations of the real module as well).

### 10.3 Falsification — the detector proved, not merely run

Baseline before any mutation:
`sha256 084482e7facc0b5ca7de1c81484b39762a03345094eb55a073c9389d3ab91349`,
copied to the session scratchpad. Every mutation was applied to
`tests/web/test_canonical_settings_graph.py` alone, by a recorded script, and
restored from that copy before the next.

Each run was:

```
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv-web/bin/python -m pytest \
  tests/web/test_canonical_settings_graph.py -q \
  -k "captures_no_instant or import_time_clock_guard"
```

| # | Mutation applied to the real module | Result | Detector's report |
|---|---|---|---|
| M-AST-1 | `NOW = datetime.now(timezone.utc).replace(microsecond=0)` inserted after `pytestmark` (line 120) — **the exact expression the handover names**, and the one that was actually deleted | **1 failed, 1 passed**, 58 deselected | `test_canonical_settings_graph.py:120 datetime.now` |
| M-AST-2 | `NOW = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)` in the same place — the **fixed module-scope constructor** the handover also requires covered, and the form that preceded M-AST-1 in this module's history | **1 failed, 1 passed**, 58 deselected | `test_canonical_settings_graph.py:120 datetime` |
| M-AST-3 | `def lying(instance, lie: Lie, _at=datetime.now(timezone.utc)):` (line 614) — a capture in a **default argument**, which a detector that only read the module's statement list would miss | **1 failed, 1 passed**, 58 deselected | `test_canonical_settings_graph.py:614 datetime.now` |

The observed failure in each case, verbatim in form:

```
E  AssertionError: an instant is captured while this module is imported, which is
   the defect the clock remediation removed:
   ['test_canonical_settings_graph.py:120 datetime.now']
```

`test_the_import_time_clock_guard_reports_both_forms_and_no_others` passed under
all three mutations, correctly: it exercises the detector against synthetic
sources and is not about the state of this file.

**The accepted side, proved rather than assumed.** The committed case asserts an
empty offender list against four synthetic sources covering everything the module
legitimately does, and the run on the unmutated module is itself the proof for the
real thing:

| Construct | Result |
|---|---|
| `from datetime import datetime, timedelta, timezone` and every other import | accepted |
| `pytestmark = pytest.mark.database` | accepted |
| Class, function, async-function and fixture declarations | accepted |
| Module-level `LIFETIME = timedelta(minutes=10)` (a duration, not an instant) | accepted |
| `OperationClock.begin()`'s `select(func.now())` and `reading.astimezone(timezone.utc)` — method bodies | accepted |
| Function-scoped `now + timedelta(minutes=accepted)` and `datetime.now(timezone.utc)` inside a case | accepted |
| Capture in a class body, a decorator, or a default argument | **rejected** |
| `_clock = datetime.now` (alias without a call) | **rejected** |

**AST semantics, not text.** The clean module contains **7** literal occurrences of
`datetime.now(timezone.utc)` (`grep -c`) — in this section's explanatory comments,
in docstrings, and inside the synthetic source strings the falsification case
feeds the detector. A `grep`-based guard would report all 7 against a module that
is correct. The AST guard reports none, and reports the one on line 120 the moment
it becomes executable code.

**Restoration.**

```
cp scratchpad/ast-original.py tests/web/test_canonical_settings_graph.py
sha256sum -c ast-original.sha256 → tests/web/test_canonical_settings_graph.py: OK
cmp ast-original.py tests/web/test_canonical_settings_graph.py → identical
grep -c "^NOW = \|_at=datetime" → 0
```

Byte-for-byte, verified by digest **and** by `cmp`. No other file was touched
during the falsification; `git status --short` lists exactly the entries it listed
before this correction, with no additions.

### 10.4 Verification for this correction

Narrow first, then the evidence this correction affects. Interpreters are the
contractually selected `../venv-web/bin/python` (portal) and `../venv/bin/python`
(bot). The two suites share the guarded disposable `freedom_test` database over the
Unix-domain socket and were run **serially**; no production, shared, TCP-forwarded
or unverified database was contacted.

| # | Command | Result |
|---|---|---|
| 1 | `… -m pytest tests/web/test_canonical_settings_graph.py -q -k "captures_no_instant or import_time_clock_guard"` | **2 passed**, 0 failed, **0 skipped**, 58 deselected |
| 2 | `… -q -k "captures_no_instant or import_time_clock_guard or one_clock or instant_captured_before"` | **4 passed**, 0 failed, **0 skipped**, 56 deselected |
| 3 | `… -m pytest tests/web/test_canonical_settings_graph.py -q -rs` (whole module) | **60 passed**, 0 failed, **0 skipped**, 2 warnings (58 before this correction; +2 new cases) |
| 4 | `… -m pytest tests/web/test_canonical_settings_graph.py tests/web/test_request_authority_and_lifecycle.py -q -rs` (TC-STRUCT-08/10/11) | **91 passed**, 0 failed, **0 skipped**, 6 warnings (89 before; +2) |
| 5 | `… -m pytest tests/web -q -rs -k "provider or oauth or break or glass or security or settings or numeric or struct or composition or startup or lifecycle or authority or webauthn or clock"` — the PostgreSQL-backed OAuth and WebAuthn clock regressions among them | **575 passed**, 0 failed, **0 skipped**, 123 deselected, 19 warnings |
| 6 | `… -m pytest tests/web -q -rs` (complete portal suite) | **698 passed**, 0 failed, **0 skipped**, 20 warnings (696 before; +2) |
| 7 | `TEST_DATABASE_URL=… ../venv/bin/python -m pytest -q -rs` (complete repository/bot suite) | **2260 passed**, 0 failed, **0 skipped**, 1 warning — unchanged |
| 8 | `git diff --check` | Clean |
| 9 | `../venv-web/bin/python -m compileall -q tests/web/test_canonical_settings_graph.py` and the same under `../venv/bin/python` | Both clean |
| 10 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 OK, 0 FAILED** |
| 11 | `git status --porcelain=v1` | Identical to before this correction — 17 modified, 8 untracked, no new entry |

**Every run above was executed with `-rs`, and every one reported zero skipped.**
No guarded infrastructure was missing and no result is a skip. Warning counts are
unchanged in kind and number apart from the two the new cases do not add: the
portal's 20 `httpx` per-request-cookie deprecations and the bot's 1 `audioop`
deprecation are the pre-existing ones.

`alembic check` was **not** re-run for this correction and is not re-claimed here:
no schema, migration, table or model was touched, and §6 row 7 records its result
for the work this corrects. Mutation testing beyond M-AST-1/2/3 was not performed
and is not claimed; no mutation tool is configured. **No formatter, linter or type
checker is configured** — the §6 row 9 inspection stands and was not re-run.

### 10.5 Nothing was weakened

Re-confirmed after this correction, by inspection of the diff and by the runs
above:

- **`OperationClock` is unchanged.** Same class, same function-scoped fixture, same
  `select(func.now())` reading inside the operation's transaction, same
  `monkeypatch` binding of `repositories.utcnow`. The correction adds a guard
  beside it and does not touch it.
- **N-04's accepted lifetime is unchanged**, and still pinned by
  `assert accepted == 10` in `test_persisted_rows_carry_one_clock_from_creation_to_expiry`.
  No lifetime was extended, no window widened, no margin added, no sleep
  introduced.
- **Both live PostgreSQL constraints are unchanged and still exercised.**
  `ck_oauth_transactions_expiry_after_creation` and
  `ck_webauthn_challenges_expiry_after_creation` are still asserted by
  `test_an_instant_captured_before_the_operation_is_refused_by_the_database`
  against the real guarded database; nothing is suppressed, dropped, deferred or
  faked, and PostgreSQL was not replaced by a fake anywhere.
- **No production code changed.** Nothing under `adapters/`, `application/`,
  `domain/`, `helpers/`, `models/`, `ext/`, `tools/` or `migrations/` was modified.
  No route, schema, migration, dependency, provider/engine authority, request
  authority, lifecycle behaviour, deployment topology, environment variable or
  `.env.example` entry changed. No new package: the guard uses the standard
  library's `ast`.
- **Secrets and data.** No `.env`, credential, token, key material, raw provider
  response or player datum was read, printed, copied or included. The synthetic
  sources in the falsification case are hand-written strings containing no
  configuration value.
- **Unrelated user work is preserved.** Nothing was staged, committed, stashed,
  reset, checked out or cleaned, and no destructive Git command was used.

### 10.6 Honest remaining gaps in this correction

1. **The detector is name-based, and indirection can still evade it.**
   `NOW = _read_the_clock()`, where `_read_the_clock` is defined elsewhere in the
   module or imported under a name not in `INSTANT_SOURCES`, is a capture the guard
   does not see. Both forms that have actually occurred here — and the alias form
   one step from them — are caught, and closing the general case would need either
   a whole-name-resolution pass or a blanket ban on every module-level binding.
   The second was considered and rejected as brittle: it would reject a future
   harmless constant and would state an invariant broader than the one claimed.
   This is stated as a limit rather than papered over.
2. **The guard is scoped to this one module.** Other portal test modules are not
   parsed. That is the handover's scope, not a judgement that they are clean; a
   sweep should be asked for as its own task.
3. **`date` and `time` are common words.** Matched only in import-executed
   positions, so the false-positive surface is small, but a future module-level
   `time = ...` binding unrelated to clocks would be reported. It would be a true
   report of a confusing name, but it is not a clock defect.
4. **The three §8 gaps from the work this corrects are unchanged and still open** —
   the single-module scope of the clock correction, `OAuthTransactionRepository`
   re-reading the clock, the two `created_at` authorities, the `monkeypatch` seam,
   and the suite's inability to detect a *skewed* database clock.

### 10.7 What review is asked to confirm about this correction

**Implementation review:** that the invariant in §10.2 is the one §3.1 now claims
and no more; that the walked/not-walked table is the right boundary for
"import-time"; that excluding `timedelta`, `timezone` and annotations is correct
rather than convenient; and that M-AST-1/2/3 prove the detector rather than
exercise it.

**Security review:** that no lifetime, window, constraint or accepted value was
relaxed by this correction; that both expiry constraints remain exercised against
real PostgreSQL; and that neither the new code nor the falsification recorded a
secret, a credential or a real player datum.

---

## 11. Status after the fifth correction

*(Superseded as this document's closing status by §13. The paragraph below is left
as written.)*

**P3.G1 remains OPEN. RAID I-09 remains OPEN. RAID I-10 remains OPEN.**

Nothing is accepted and no gate is closed. All changes — this correction's two
test cases and every earlier uncommitted P3.G1 modification — remain **unstaged
and uncommitted**. This document requires a fresh independent implementation
review, a distinct security-focused review and the maintainer's acceptance
decision before any dependent work continues. P3.2 and P3.3 have not been started
and must not be.

---

## 12. Correction 2026-08-16 (sixth): the detector did not enforce its own invariant

**Dated correction, appended after §10 was submitted.** It supersedes the lambda
half of §10.2's walked/not-walked table and adds to §10.3, §10.4 and §10.6.
Everything else in this document, including §10's account of *why* the AST
regression exists, stands unchanged.

### 12.1 The independent-review finding

Fresh independent implementation re-review read the detector rather than the claim
made for it, and found the claim wider than the code. §10.2 states the invariant as

> *No code that runs while this module is imported may read or construct an
> instant.*

while `_ImportTimeClocks.visit_Lambda()` was

```python
def visit_Lambda(self, node: ast.Lambda) -> None:
    self._defaults(node.args)
```

— it visited the defaults and returned, so **every** lambda body was skipped
unconditionally. The minimal reproducer:

```python
from datetime import datetime, timezone

NOW = (lambda: datetime.now(timezone.utc))()
```

`NOW` is a stale instant captured at import — precisely the defect this whole
document exists to remove — and the detector reported it clean. §10.2's stated
reason for excluding lambda bodies ("they run when a case calls them") is true of a
lambda that is stored, returned or passed, and false of one invoked where it is
written. Nothing calls this lambda later; the call is right there in the same
expression.

**The finding is accepted in full.** It is the same shape as everything else this
document records, one level further in: not a claim about a control this time, but
a control whose declared scope exceeded its actual scope. `OperationClock`, N-04's
lifetime, both expiry constraints and the module's real freedom from import-time
clocks were never affected — the module contains no such lambda, before or after —
but a diff that added one would have passed.

### 12.2 The resolution taken, and why

The handover offers two resolutions and prefers correcting the detector, because
the missed construct is directly recognisable from the AST. It is recognisable, so
that is what was done: **the detector now enforces the invariant, and the invariant
is not narrowed**.

Parentheses leave no trace in the AST. `(lambda: ...)()` is exactly a `Call` whose
`func` **is** the `Lambda` — there is no other way to spell an immediately invoked
lambda — so the construct is decidable syntactically, with no name resolution and
no call graph. The rule is therefore stated as **when the body runs**, not as what
the node is:

| Lambda position | Body walked? | Why |
|---|---|---|
| `(lambda: …)()` — the callable of a call | **yes** | it is invoked where it is written, so the body runs whenever the enclosing expression is evaluated, and at module scope that is during the import |
| `(lambda: lambda: …)()()` — curried, fully applied | **yes** | the outer call yields the inner lambda and the second call runs it, both inside the same import-time expression |
| `(lambda: lambda: …)()` — curried, applied once | **no** | the module stores a callable; whoever calls it later decides when a clock is read |
| `f = lambda: …` — stored | **no** | unchanged; the body runs when its holder calls it |
| `sorted(rows, key=lambda …)` — passed | **no** | unchanged; same reason |
| Lambda **defaults**, in every case above | **yes** | unchanged; a default is evaluated when the lambda object is created, which at module scope is at import |

Implemented as one new `visit_Call` and one pure helper, `_invoked_lambda`, which
answers "the lambda this callable position runs, when the source says so" and
answers nothing else. `visit_Call` walks a call the way `generic_visit` already
did — callable, then arguments, then keywords, in that order — and adds only the
invoked body; when the callable *is* the lambda it takes over the defaults so that
`visit_Lambda` is not also reached and nothing is reported twice. Reporting stays
deterministic and in traversal order, and the source-line and reference
diagnostics are unchanged.

**Everything else is untouched, deliberately.** Function and method bodies,
decorators, class bodies, default arguments, imports, annotations, `timedelta`,
`timezone` and the fifteen-name `INSTANT_SOURCES` set are exactly as §10.2
describes them. No interprocedural analysis was added, and no blanket ban on
module-level bindings was introduced — both were named by the handover as things
not to do, and both were avoided.

### 12.3 Falsification — before and after, and the negative control

Baseline before any mutation:
`sha256 0fe654e45bcad1a8a3babad0d690b8c285d610bbdac7b30785e0c81a4896e8be`, copied
to the session scratchpad. Every mutation was applied to
`tests/web/test_canonical_settings_graph.py` alone, inserted immediately after
`pytestmark` (line 119), and restored from that copy before the next.

Each run was:

```
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv-web/bin/python -m pytest \
  tests/web/test_canonical_settings_graph.py -q -rs \
  -k "captures_no_instant or import_time_clock_guard"
```

| # | Mutation applied to the real module | Result | Detector's report |
|---|---|---|---|
| M-AST-4 | `NOW = (lambda: datetime.now(timezone.utc))()` — **the handover's reproducer, verbatim** | **1 failed, 2 passed**, 58 deselected | `test_canonical_settings_graph.py:119 datetime.now` |
| M-AST-5 | `NOW = (lambda: lambda: datetime.now(timezone.utc))()()` — curried and fully applied, the nested form §12.2 includes | **1 failed, 2 passed**, 58 deselected | `test_canonical_settings_graph.py:119 datetime.now` |
| M-AST-6 | `make_now = lambda: datetime.now(timezone.utc)  # stored, not invoked` — the **negative control** | **3 passed**, 58 deselected | *(none, correctly)* |

M-AST-6 is the half that matters as much as the first two: it proves the
correction did not close the gap by widening the net until everything is a
finding. A lambda that is stored rather than invoked reads no clock at import, and
the detector still says so.

**The detector before and after, on the same inputs.** The pre-correction
behaviour is recorded rather than described. Reconstructed by subclassing the
committed detector and disabling only the new method
(`visit_Call = ast.NodeVisitor.generic_visit`), which is exactly what it was:

| Source | Pre-correction detector | Corrected detector |
|---|---|---|
| The handover's reproducer | `[]` — the false negative, reproduced | `[(3, 'datetime.now')]` |
| The mutated real module (M-AST-4) | `[]` | `[(119, 'datetime.now')]` |
| The **clean** real module | `[]` | `[]` |

The last row is the one that shows the correction introduced no false positive:
the real module reports nothing under either detector, so nothing this module
legitimately does became a finding.

**One honest note on the committed case.** The first draft of its stored-lambda
example bound the lambda to the name `clock`, and the case failed:
`synthetic.py:4 clock`. That is a **true** report of the detector's documented
name-based rule — `clock` is one of the fifteen names in `INSTANT_SOURCES`, and a
module-level binding of it is reported wherever it appears — and it is §10.6's
third declared limit arriving in practice. The synthetic was renamed to
`read_now`; the detector was not changed to accommodate it.

**Restoration.**

```
cp scratchpad/lambda-original.py tests/web/test_canonical_settings_graph.py
sha256sum -c lambda-original.sha256 → lambda-original.py: OK
sha256sum tests/web/test_canonical_settings_graph.py
  → 0fe654e45bcad1a8a3babad0d690b8c285d610bbdac7b30785e0c81a4896e8be
cmp scratchpad/lambda-original.py tests/web/test_canonical_settings_graph.py → identical
grep -c "^NOW = \|^make_now = " → 0
```

Byte-for-byte, verified by digest **and** by `cmp`. No other file was touched
during the falsification; `git status --porcelain=v1` lists exactly the 17 modified
and 8 untracked entries it listed before this correction, with no additions.

### 12.4 The committed case

`test_the_import_time_clock_guard_reads_an_invoked_lambda_body` is added beside
the two §10 cases, and runs on every execution of the suite rather than only once
by hand. It asserts, on synthetic sources:

1. the handover's reproducer is reported at its `datetime.now` line;
2. the curried, fully applied form is reported;
3. the curried form applied **once** — a stored callable — is not;
4. a stored lambda and a lambda passed as an argument are not;
5. defaults are reported for a stored lambda and for an invoked one alike; and
6. an ordinary call's callable, arguments and keywords are still walked exactly as
   before, each reported once and in source order.

(6) exists because `visit_Call` is new: every call in the module now passes through
it, so the unchanged behaviour is asserted rather than assumed.

### 12.5 Verification for this correction

Narrow first, then in proportion to the change. Interpreters are the contractually
selected `../venv-web/bin/python` (portal) and `../venv/bin/python` (bot). The two
suites share the guarded disposable `freedom_test` database over the Unix-domain
socket and were run **serially**; no production, shared, TCP-forwarded or
unverified database was contacted.

| # | Command | Result |
|---|---|---|
| 1 | `… -m pytest tests/web/test_canonical_settings_graph.py -q -rs -k "captures_no_instant or import_time_clock_guard"` | **3 passed**, 0 failed, **0 skipped**, 58 deselected |
| 2 | `… -m pytest tests/web/test_canonical_settings_graph.py -q -rs` (whole module) | **61 passed**, 0 failed, **0 skipped**, 2 warnings (60 before this correction; +1 new case) |
| 3 | `… -m pytest tests/web/test_canonical_settings_graph.py tests/web/test_request_authority_and_lifecycle.py -q -rs` (TC-STRUCT-08/10/11) | **92 passed**, 0 failed, **0 skipped**, 6 warnings (91 before; +1) |
| 4 | `… -m pytest tests/web -q -rs` (complete portal suite) | **699 passed**, 0 failed, **0 skipped**, 20 warnings (698 before; +1) |
| 5 | `TEST_DATABASE_URL=… ../venv/bin/python -m pytest -q -rs` (complete repository/bot suite) | **2260 passed**, 0 failed, **0 skipped**, 1 warning — unchanged |
| 6 | `git diff --check` | Clean |
| 7 | `../venv-web/bin/python -m compileall -q …` and the same under `../venv/bin/python` | Both clean |
| 8 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 OK, 0 FAILED** |
| 9 | `git status --porcelain=v1` | 17 modified, 8 untracked — identical to before this correction |

**Every run above was executed with `-rs`, and every one reported zero skipped.**
No guarded infrastructure was missing and no result is a skip. Warning counts are
unchanged in kind and number: the portal's 20 `httpx` per-request-cookie
deprecations and the bot's 1 `audioop` deprecation are the pre-existing ones.

**Not run, and not claimed.** The `-k "provider or oauth or break or glass or …"`
selection of §10.4 row 5 was not repeated separately — the complete portal suite
(row 4) is a superset of it and was run. `alembic check` was **not** re-run: no
schema, migration, table or model was touched, and §6 row 7 records its result for
the work this corrects. **No formatter, linter or type checker is configured** —
the §6 row 9 inspection stands and was not re-run. Mutation testing beyond
M-AST-4/5/6 was not performed; no mutation tool is configured.

### 12.6 Nothing was weakened

Re-confirmed by inspection of the diff and by the runs above:

- **The invariant was not narrowed.** The alternative resolution the handover
  permits — declaring invoked lambda bodies out of scope and saying so in the test
  comments, TC-STRUCT-08, this submission, the change log, the RAID amendment and
  the status entry — was **not** taken. The claim "any code that runs at import"
  stands and is now enforced for this construct.
- **No previously accepted example became a finding.** The four accepted synthetic
  sources of §10 and the clean real module all still report nothing, and the clean
  module reports nothing under the pre-correction detector too (§12.3).
- **`OperationClock` is unchanged**, same class, same function-scoped fixture, same
  `select(func.now())` reading inside the operation's transaction, same
  `monkeypatch` binding of `repositories.utcnow`.
- **N-04's accepted lifetime is unchanged** and still pinned by `assert accepted ==
  10`. No lifetime extended, no window widened, no margin added, no sleep
  introduced.
- **Both live PostgreSQL constraints are unchanged and still exercised.**
  `ck_oauth_transactions_expiry_after_creation` and
  `ck_webauthn_challenges_expiry_after_creation` are still asserted against the real
  guarded database; nothing is suppressed, dropped, deferred or faked.
- **No production code changed.** Nothing under `adapters/`, `application/`,
  `domain/`, `helpers/`, `models/`, `ext/`, `tools/` or `migrations/` was modified.
  No route, schema, migration, dependency, provider/engine authority, request
  authority, lifecycle behaviour, deployment topology, environment variable or
  `.env.example` entry changed. No new package: `ast` is the standard library.
- **Secrets and data.** No `.env`, credential, token, key material, raw provider
  response or player datum was read, printed, copied or included. The synthetic
  sources are hand-written strings containing no configuration value.
- **Unrelated user work is preserved.** Nothing was staged, committed, stashed,
  reset, checked out or cleaned, and no destructive Git command was used.

### 12.7 Remaining declared limits

1. **The detector is name-based** (§10.6 limit 1, unchanged and restated).
   `NOW = _read_the_clock()`, where the helper is named outside `INSTANT_SOURCES`,
   is not seen. This correction does not narrow that gap and does not claim to:
   an *indirectly named helper call* remains outside the guard.
2. **Invocation is recognised syntactically, not by resolution.** `f = lambda:
   datetime.now(timezone.utc)` on one line and `NOW = f()` on the next is two
   statements whose connection is a name binding, and resolving it is the
   interprocedural analysis the handover excludes. It is the same limit as (1)
   wearing a lambda's clothes, and it is stated rather than implied. What the guard
   covers is the construct that is decidable from the AST alone: the lambda that is
   invoked where it is written.
3. **The guard is scoped to this one module** (§10.6 limit 2, unchanged). Other
   portal test modules are not parsed; a sweep should be asked for as its own task.
4. **`date` and `time` are common words** (§10.6 limit 3, unchanged) — and §12.3
   records `clock` behaving exactly that way in practice.
5. **The §8 gaps from the work this corrects are unchanged and still open.**

### 12.8 What review is asked to confirm about this correction

**Implementation review:** that "invoked where it is written" is the correct
boundary for a lambda body, and that the curried form belongs inside it for the
same reason rather than by accident; that the stored, returned and passed cases are
the right other side of that line; that `visit_Call` walks an ordinary call exactly
as `generic_visit` did and reports no position twice; that M-AST-6 and the clean
module runs are adequate evidence of no over-broadening; and that §12.7's limits are
the true remaining ones.

**Security review:** that no lifetime, window, constraint or accepted value was
relaxed by this correction; that both expiry constraints remain exercised against
real PostgreSQL; and that neither the new case nor the falsification recorded a
secret, a credential or a real player datum.

---

## 13. Status after the sixth correction

*(Superseded in part by §15. The sixth correction's account of the lambda rule
stands; its claim that the rule was fully recognised by the code does not — see
§14.)*

**P3.G1 remains OPEN. RAID I-09 remains OPEN. RAID I-10 remains OPEN.**

Nothing is accepted, and nothing here is an acceptance of itself: this correction
was written by the same working Technical Lead whose detector the finding is
against, and it is remediation evidence for a fresh independent review, not a gate
decision. All changes — this correction's detector fix and third test case, §10's
two cases and every earlier uncommitted P3.G1 modification — remain **unstaged and
uncommitted**. A fresh independent implementation review, a distinct
security-focused review and the maintainer's acceptance decision are required
before any dependent work continues. **P3.2 and P3.3 have not been started and must
not be.**

---

## 14. Correction 2026-08-16 (seventh): the lambda rule was right, its recognition was not

**Dated correction, appended after §12 was submitted.** It supersedes **in part**
§12.2's implementation paragraph and §12.7's limits 2 and 5. Everything else in
this document — including §12's account of *why* an invoked lambda's body is
import-time code, which this correction does not revisit but extends — stands
unchanged. Nothing here is an acceptance of anything: it is remediation evidence
written by the same working Technical Lead whose detector the finding is against.

### 14.1 The independent-review finding

§12 stated the rule as *when the body runs*, and stated its recognition as
syntactic — §12.2, verbatim:

> the construct is decidable syntactically, with no name resolution and no call
> graph

Fresh independent implementation re-review took that rule at its word and found
two spellings it does not reach. `_invoked_lambda()` recognised an `ast.Lambda`
or the supported chain of `ast.Call` nodes, and nothing else — so it did not
unwrap an `ast.NamedExpr`:

```python
from datetime import datetime, timezone

NOW = (reader := lambda: datetime.now(timezone.utc))()
```

```python
from datetime import datetime, timezone

NOW = (factory := lambda: lambda: datetime.now(timezone.utc))()()
```

Both were reported **clean**. Both bodies execute during the import — confirmed
by executing the two sources rather than by reading the grammar: they bind `NOW`
to `datetime.datetime(2026, 8, 16, 17, 53, 49, 529981, tzinfo=…)` and
`…530038` respectively, instants captured at import and stale from that moment
on. And both are lambdas invoked where they are written, so recognising either
requires nothing to be resolved.

**The finding is accepted in full.** It is not a new shape; it is §12's shape one
turn further in. §12 corrected a control whose *declared scope* exceeded its
actual scope, and in doing so asserted a *recognition property* — "no name
resolution is needed for this construct" — that its own code did not deliver.
This is I-10 again: the claim was checked against the constructs that had already
been raised, not against the constructs it claimed to cover.

As before, nothing about the module's real state was wrong. It contains no such
lambda, before or after, and `OperationClock` was never affected. A diff that
added one would have passed.

### 14.2 Why a named expression is a wrapper and not the excluded name resolution

This is the distinction the correction turns on, so it is argued rather than
asserted.

`(reader := L)` is an **expression** whose value is `L`. It evaluates `L` once,
binds the result to `reader` as a side effect, and answers *that same object* as
its own value. In `(reader := L)()` the call's callable is that value. There is no
step between producing the lambda and calling it, and no question about what the
callable is that the enclosing expression does not itself answer. The AST says so
directly: `Call(func=NamedExpr(target=Name('reader'), value=Lambda(...)))`. The
`Lambda` is a child of the callable position.

`f = lambda: ...` on one line and `NOW = f()` on the next is a different fact.
There the callable position holds a `Name`, and deciding what it holds means
knowing which binding of `f` is live at that statement — whether it was rebound,
deleted, shadowed, or conditionally assigned. That is data flow across
statements, and it is the interprocedural analysis the handover excludes and §12.7
limit 2 declares. It remains excluded, and case 6 of the new test asserts it
(§14.4).

The two are not on a spectrum: one is a child node of the call, the other is a
question about program history. The correction crosses no part of that gap.

**The boundary is exact, and is not "the first wrapper we found".** `ast.NamedExpr`
is the *only* expression in the grammar that yields its single operand, evaluated
at that point, with neither a selection nor a lookup:

| Callable expression | Unwrapped? | Why |
|---|---|---|
| `ast.NamedExpr` — `(f := L)()` | **yes** | one operand, evaluated here, answered unchanged; the binding is a side effect |
| `ast.IfExp` — `(f if flag else g)()` | **no** | a **selection**: the source does not say which body runs, and reporting one would report a body that may not execute — **superseded in part by §16: this row is true of `if flag` and false of `if True`/`if False`, which name their own branch and are now unwrapped** |
| `ast.BoolOp` — `(f or g)()` | **no** | the same selection, spelled shorter, and additionally conditional on a value |
| `ast.Await` — `(await x)()` | **no** | not a wrapper at all: it yields the awaited *result*, and a lambda is not awaitable. It cannot occur at this module's import scope |
| `ast.Name`, `ast.Attribute`, `ast.Subscript`, a container element, an argument | **no** | reaching the lambda means resolving where a **separately stored** value came from — the excluded analysis |

`ast.Starred` cannot appear in a callable position, and parentheses leave no node
at all. The list is therefore closed, and the two "no" rows that are *not* name
resolution — `IfExp` and `BoolOp` — are declared as limits in §14.7 rather than
left for the next reviewer to find. They were considered and deliberately not
implemented: handling a selection would mean answering "which body runs" with
"either", which `_invoked_lambda()`'s contract cannot express without becoming a
set-valued analysis, and the handover is explicit that this task is not to be
broadened into a general static analyzer.

### 14.3 The corrected traversal, exactly

Three lines of behaviour change, all inside the pure helper:

```python
if isinstance(callable_expression, ast.NamedExpr):
    return _invoked_lambda(callable_expression.value)
```

placed before the existing `ast.Lambda` and `ast.Call` branches, so it composes
with both: a walrus around a direct lambda, a walrus around a curried lambda, and
a walrus nested in another walrus are all answered by the same recursion.

**Unwrapping decides one thing only: whether a body runs.** It removes nothing
from the walk, and `visit_Call` is unchanged in structure. The callable position
of `(reader := L)()` is not an `ast.Lambda`, so it takes the existing "walk the
callable as ordinary import-time code" branch, which visits the `NamedExpr` in
full — its **target** first, as a `Name`, and then the `Lambda`, which reaches
`visit_Lambda` for its **defaults**. Only then is the invoked body visited, once.
So:

| Construct | Reported | Why |
|---|---|---|
| `NOW = (reader := lambda: datetime.now(timezone.utc))()` | `datetime.now` | the body runs at import |
| `NOW = (factory := lambda: lambda: datetime.now(...))()()` | `datetime.now` | fully applied; the second call runs the inner body |
| `NOW = (now := lambda: datetime.utcnow())()` | `now`, then `datetime.utcnow` | the **target** is import-time code like any other, and `now` is one of `INSTANT_SOURCES`; the unwrapping took nothing away |
| `NOW = (clock := datetime.now)()` | `clock`, then `datetime.now` | no lambda is invented where there is none; walked exactly as before |
| `held = (keep := lambda _at=datetime.now(...): _at)` | `datetime.now` | defaults run when the lambda object is created |
| `make_clock = (factory := lambda: lambda: …)()` | *(none)* | applied once: the module stores a callable |
| `read_now = (reader := lambda: …)` | *(none)* | bound, never called |
| `if (stamp := datetime.now(...)) is not None:` | `datetime.now` | a walrus outside a callable position is untouched by any of this |

Every position §12 walked is still walked, in the same order, once each; the
source-line and reference diagnostics are unchanged; and no position is reported
twice. Function and method bodies, decorators, class bodies, imports,
annotations, `timedelta`, `timezone` and the fifteen-name `INSTANT_SOURCES` set
are exactly as §10.2 and §12.2 describe them.

### 14.4 The committed case

`test_the_import_time_clock_guard_sees_through_a_named_expression` is added beside
the three existing guard cases and runs on every execution of the suite. Its eight
sections are the table above, plus the two controls that say what the correction is
not:

1. **both reproducers, verbatim**, asserted as one mapping so that a regression
   reports both rather than stopping at the first;
2. the named-expression **target** still reported, and reported first;
3. a walrus whose value is not a lambda, walked exactly as before;
4. defaults through a walrus, invoked and bound alike;
5. the curried form applied **once**, and a walrus never called — both silent;
6. **negative control** — `read_now = lambda: …` then `NOW = read_now()` is
   **not** reported. This construct does capture an instant at import and the
   guard does not see it. It is asserted here so the declared limit is where the
   code says it is, and it is what distinguishes this correction from the
   forbidden name resolution: case 1 is decidable from one expression, this is
   not;
7. **boundary control** — a selection `((lambda: datetime.now(…)) if flag else
   (lambda: None))()` is **not** reported, for the reason in §14.2. Declared as a
   limit in §14.7, not claimed as correct coverage; and
8. a named expression outside a callable position, unchanged.

### 14.5 Falsification — before and after, and against the real module

Baseline before any mutation: the module as §12 left it,
`sha256 0fe654e45bcad1a8a3babad0d690b8c285d610bbdac7b30785e0c81a4896e8be` —
identical to §12.3's recorded digest, so the starting point is verifiably the
submitted sixth correction and nothing else. After this correction the module is
`sha256 d2f52dbb842a771c168f100b5b8d46700e4154a74252944959004b6d6f31203a`, copied
to the session scratchpad and used to restore it after every mutation.

**The new case fails against the pre-correction detector, for the finding's own
reason.** Run with the new test present and only the three-line helper branch
removed:

```
TEST_DATABASE_URL='postgresql+psycopg:///freedom_test' ../venv-web/bin/python -m pytest \
  tests/web/test_canonical_settings_graph.py -q -rs \
  -k "captures_no_instant or import_time_clock_guard"
→ 1 failed, 3 passed, 58 deselected
E  AssertionError: assert {'curried': [], 'direct': []} == {'curried': [...], 'direct': [...]}
E    Differing items:
E    {'direct': []}  != {'direct': ['synthetic.py:3 datetime.now']}
E    {'curried': []} != {'curried': ['synthetic.py:3 datetime.now']}
```

Both reproducers reported clean — the false negative, reproduced, and not some
other failure standing in for it.

**The detector before and after, on the same inputs.** The pre-correction
behaviour is recorded rather than described. Reconstructed by rebinding the
module's `_invoked_lambda` to the version without the `ast.NamedExpr` branch and
nothing else, which is exactly what it was; `visit_Call` resolves the helper
through the module global, so the rebinding is the whole difference, and the real
helper is restored and re-asserted after each row.

| Source | Pre-correction detector | Corrected detector |
|---|---|---|
| The direct reproducer | `[]` — the false negative, reproduced | `['x.py:3 datetime.now']` |
| The curried reproducer | `[]` — likewise | `['x.py:3 datetime.now']` |
| Stored, then called by name (negative control) | `[]` | `[]` — unchanged, as declared |
| The real module mutated with the direct reproducer | `[]` | `['x.py:119 datetime.now']` |
| The real module mutated with the curried reproducer | `[]` | `['x.py:119 datetime.now']` |
| The real module mutated with the negative control | `[]` | `[]` |
| The **clean** real module | `[]` | `[]` |

The last row is the one that shows no false positive was introduced: the real
module reports nothing under either detector, so nothing this module legitimately
does became a finding.

**Mutations of the real module.** Each was inserted immediately after `pytestmark`
(line 118), run, then restored from the digested copy before the next.

| # | Mutation applied to the real module | Result | Detector's report |
|---|---|---|---|
| M-AST-7 | `NOW = (reader := lambda: datetime.now(timezone.utc))()` — **the finding's direct reproducer, verbatim** | **1 failed, 3 passed**, 58 deselected | `test_canonical_settings_graph.py:119 datetime.now` |
| M-AST-8 | `NOW = (factory := lambda: lambda: datetime.now(timezone.utc))()()` — **the curried reproducer, verbatim** | **1 failed, 3 passed**, 58 deselected | `test_canonical_settings_graph.py:119 datetime.now` |
| M-AST-9 | `read_now = lambda: datetime.now(timezone.utc)` then `NOW = read_now()` — the **negative control** | **4 passed**, 58 deselected | *(none — the declared limit, behaving as declared)* |

M-AST-9 is the half that keeps the correction honest in the other direction. It is
a real import-time capture that the guard does not report, and the run proves the
fix did not close the gap by widening the net until every lambda is a finding —
and equally proves the limit is real rather than rhetorical.

**Restoration.**

```
cp scratchpad/walrus-corrected.py tests/web/test_canonical_settings_graph.py
sha256sum -c walrus-corrected.sha256 → walrus-corrected.py: OK
sha256sum tests/web/test_canonical_settings_graph.py
  → d2f52dbb842a771c168f100b5b8d46700e4154a74252944959004b6d6f31203a
cmp scratchpad/walrus-corrected.py tests/web/test_canonical_settings_graph.py → identical
grep -c "^NOW = \|^read_now = " → 0
```

Byte-for-byte after every mutation, verified by digest **and** by `cmp`. No other
file was touched during the falsification; `git status --porcelain=v1` lists
exactly the 17 modified and 8 untracked entries it listed before this correction.

### 14.6 Verification for this correction

Narrow first, then in proportion to the change. Interpreters are the contractually
selected `../venv-web/bin/python` (portal) and `../venv/bin/python` (bot), both
CPython 3.12.3. The two suites share the guarded disposable `freedom_test`
database over the Unix-domain socket and were run **serially**; no production,
shared, TCP-forwarded or unverified database was contacted.

| # | Command | Result |
|---|---|---|
| 1 | `… -m pytest tests/web/test_canonical_settings_graph.py -q -rs -k "captures_no_instant or import_time_clock_guard"` | **4 passed**, 0 failed, **0 skipped**, 58 deselected (3 before this correction; +1 new case) |
| 2 | `… -m pytest tests/web/test_canonical_settings_graph.py -q -rs` (whole module) | **62 passed**, 0 failed, **0 skipped**, 2 warnings (61 before; +1) |
| 3 | `… -m pytest tests/web/test_canonical_settings_graph.py tests/web/test_request_authority_and_lifecycle.py -q -rs` (TC-STRUCT-08/10/11) | **93 passed**, 0 failed, **0 skipped**, 6 warnings (92 before; +1) |
| 4 | `… -m pytest tests/web -q -rs` (complete portal suite) | **700 passed**, 0 failed, **0 skipped**, 20 warnings (699 before; +1) |
| 5 | `TEST_DATABASE_URL=… ../venv/bin/python -m pytest -q -rs` (complete repository/bot suite) | **2260 passed**, 0 failed, **0 skipped**, 1 warning — unchanged |
| 6 | `git diff --check` | Clean |
| 7 | `../venv-web/bin/python -m compileall -q tests/web/test_canonical_settings_graph.py` and the same under `../venv/bin/python` | Both clean |
| 8 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 OK, 0 FAILED** |
| 9 | `git status --porcelain=v1` | 17 modified, 8 untracked — identical to before this correction |

**Every run above was executed with `-rs`, and every one reported zero skipped.**
No guarded infrastructure was missing and no result is a skip. Warning counts are
unchanged in kind and number: the portal's 20 `httpx` per-request-cookie
deprecations and the bot's 1 `audioop` deprecation are the pre-existing ones.

**Not run, and not claimed.** `alembic check` was **not** re-run: no schema,
migration, table or model was touched, and §6 row 7 records its result for the work
this corrects. **No formatter, linter or type checker is configured** — the §6 row 9
inspection stands and was not re-run. The `-k "provider or oauth or break or glass
or …"` selection of §10.4 row 5 was not repeated separately; the complete portal
suite (row 4) is a superset of it and was run. Mutation testing beyond M-AST-7/8/9
and the reconstructed before/after table was not performed; no mutation tool is
configured. No other test module was parsed by the guard, and no sweep of the wider
test tree was attempted (§14.7 limit 4).

### 14.7 Nothing was weakened, and the limits that remain

Re-confirmed by inspection of the diff and by the runs above:

- **The invariant was not narrowed.** The alternative the handover forbids —
  declaring named-expression lambdas out of scope — was not taken. "Any code that
  runs at import" stands, and is now enforced for this construct too.
- **No previously accepted example became a finding.** Every synthetic source of
  §10 and §12 still reports exactly what it reported, and the clean real module
  reports nothing under both the pre-correction and the corrected detector.
- **`OperationClock` is unchanged** — same class, same function-scoped fixture,
  same `select(func.now())` reading inside the operation's transaction, same
  `monkeypatch` binding of `repositories.utcnow`.
- **N-04's accepted lifetime is unchanged** and still pinned by `assert accepted ==
  10`. No lifetime extended, no window widened, no margin added, no sleep
  introduced.
- **Both live PostgreSQL constraints are unchanged and still exercised.**
  `ck_oauth_transactions_expiry_after_creation` and
  `ck_webauthn_challenges_expiry_after_creation` are still asserted against the
  real guarded database; nothing is suppressed, dropped, deferred or faked.
- **No production code changed.** Nothing under `adapters/`, `application/`,
  `domain/`, `helpers/`, `models/`, `ext/`, `tools/` or `migrations/` was modified.
  No route, schema, migration, dependency, configuration variable, `.env.example`
  entry, provider/engine authority, request authority, lifecycle behaviour,
  deployment topology or runtime grant changed. No new package: `ast` is the
  standard library, and `ast.NamedExpr` has existed since Python 3.8.
- **Secrets and data.** No `.env`, credential, token, key material, raw provider
  response or player datum was read, printed, copied or included. The synthetic
  sources are hand-written strings containing no configuration value.
- **Unrelated user work is preserved.** Nothing was staged, committed, stashed,
  reset, checked out or cleaned, and no destructive Git command was used.

**The remaining limits, stated rather than implied.** (1) and (2) supersede §12.7
limits 1 and 2 in wording only; (3) is new and is a *consequence* of this
correction's boundary, disclosed here rather than left for the next review.

1. **The detector is name-based** (§10.6 limit 1, §12.7 limit 1, unchanged).
   `NOW = _read_the_clock()`, where the helper is named outside the fifteen-name
   `INSTANT_SOURCES` set, is not seen. This correction narrows nothing there.
2. **Invocation is recognised syntactically, not by resolution** (§12.7 limit 2,
   restated with its true edge). What the guard covers is a lambda whose invocation
   is decidable from the enclosing expression: written in the callable position, or
   named there by a walrus, directly or curried. What it does not cover is a lambda
   bound in one statement and called through its name in another — `f = lambda:
   datetime.now(...)`, then `NOW = f()`. That is a live false negative, asserted as
   case 6 of the new test so it cannot be mistaken for coverage, and closing it
   means the data-flow analysis the handover excludes.
3. **A selection in a callable position is not unwrapped** (new). **Superseded in
   part by §16.7 limit 3:** this was stated for every selection and holds only for
   a condition that is not an exact boolean literal. `if True` and `if False` are
   decidable from the one node, needed neither data flow nor a set-valued
   analysis, and are now unwrapped. The text below is left as it was written.
   `((lambda:
   datetime.now(...)) if flag else (lambda: None))()` executes one of two bodies at
   import and is not reported, because the source does not say which. It is
   asserted as case 7 of the new test for the same reason as (2). Closing it would
   mean `_invoked_lambda()` answering with a *set* of possible bodies, which is a
   different contract and a broader analysis than this task allows; it is offered
   as a candidate for a separately scoped task rather than smuggled in here.
4. **The guard is scoped to this one module** (§10.6 limit 2, §12.7 limit 3,
   unchanged). Other portal test modules are not parsed; a sweep should be asked
   for as its own task.
5. **`date`, `time` and `clock` are common words** (§10.6 limit 3, §12.7 limit 4,
   unchanged) — §12.3 records `clock` behaving exactly that way in practice, and
   case 3 of the new test records it again.
6. **The §8 gaps from the work this corrects are unchanged and still open.**

### 14.8 What review is asked to confirm about this correction

**Implementation review:** that an `ast.NamedExpr` in a callable position is a
directly evaluated wrapper and not the separately stored name §12.7 declares out of
scope, and that §14.2's table closes the set of wrappers rather than opening one;
that the unwrapping takes nothing out of the ordinary walk — in particular that a
named-expression target and a lambda's defaults are still reported, once each and
in source order; that cases 6 and 7 are the correct other side of the line and
their limits are honestly stated rather than quietly blessed; that M-AST-9 and the
clean-module rows are adequate evidence of no over-broadening; and that §14.7's
limits are the true remaining ones.

**Security review:** that no lifetime, window, constraint or accepted value was
relaxed by this correction; that both expiry constraints remain exercised against
real PostgreSQL; that no production file, dependency, configuration value,
migration or schema changed; and that neither the new case nor the falsification
recorded a secret, a credential or a real player datum.

---

## 15. Status after the seventh correction

**Superseded in part by §17.** This section was the document's closing status when
it was written; §17 replaces it. The status it records — P3.G1, I-09 and I-10 open,
nothing accepted, nothing staged — is unchanged by the eighth correction. The text
below is left as it was written.

**P3.G1 remains OPEN. RAID I-09 remains OPEN. RAID I-10 remains OPEN.**

This section replaces §13 as the document's closing status; §13 is left in place
and marked superseded in part.

Nothing is accepted, and nothing here is an acceptance of itself: this correction
was written by the same working Technical Lead whose detector the finding is
against, and it is remediation evidence for a fresh independent review, not a gate
decision. All changes — this correction's three-line helper branch and fourth test
case, §12's correction, §10's two cases and every earlier uncommitted P3.G1
modification — remain **unstaged and uncommitted**. A fresh independent
implementation review, a distinct security-focused review and the maintainer's
acceptance decision are required before any dependent work continues. **P3.2 and
P3.3 have not been started and must not be.**

---

## 16. Correction 2026-08-16 (eighth): a literal conditional is decidable, and was not decided

**Dated correction, appended after §14 was submitted.** It supersedes **in part**
§14.2's `ast.IfExp` table row, §14.4's description of case 7, and §14.7 limit 3.
Everything else in this document stands unchanged, including §14's account of why
an `ast.NamedExpr` is a wrapper rather than a name — which this correction does
not revisit but extends. Nothing here is an acceptance of anything: it is
remediation evidence written by the same working Technical Lead whose detector the
finding is against.

### 16.1 The independent-review finding

§14 looked through `ast.NamedExpr` correctly. The boundary it claimed beside that
unwrapping is false. §14.2's table said of `ast.IfExp`:

> a **selection**: the source does not say which body runs, and reporting one
> would report a body that may not execute

and §14.7 limit 3 said closing it "would mean `_invoked_lambda()` answering with a
*set* of possible bodies, which is a different contract and a broader analysis
than this task allows". Both statements are true of `if flag`. Neither is true
when the condition is an AST literal:

```python
from datetime import datetime, timezone

NOW = ((lambda: datetime.now(timezone.utc)) if True else (lambda: None))()
```

This captures an instant at import. The source and the AST say **exactly** which
lambda runs: `IfExp(test=Constant(True), …)` names its own branch. No name is
resolved, no stored value is looked up, and no set of possible bodies is needed —
there is one body, written where it stands, exactly as in the forms §12 and §14
already cover.

The detector returned `[]`, because `_invoked_lambda()` did not handle `ast.IfExp`
at all. And the existing negative control used `PREFER_UTC` — a **name** — as its
test, so it exercised only the decidable half of the claim while the claim was
made for every selection.

**The finding is accepted in full**, in both its halves: the guard did not enforce
its stated import-time invariant, and the seventh submission presented an open
boundary as an exact one. This is I-10's shape once more — a claim about a
control's reach, checked against the construct that had been raised (`if flag`)
rather than the construct the claim covered (every `ast.IfExp`).

As before, nothing about the module's real state was wrong. It contains no such
conditional, before or after, and `OperationClock` was never affected.

**Confirmed by execution, not by reading the grammar.** Both reproducers were run:

```
executed literal-True  reproducer -> NOW = datetime(2026, 8, 16, 18, 51, 44, 151297, tzinfo=utc)
executed literal-False reproducer -> NOW = datetime(2026, 8, 16, 18, 51, 44, 151355)
```

### 16.2 Why an exact boolean literal makes the branch syntactically decidable

`A if True else B` evaluates `A` and never evaluates `B`; `A if False else B` does
the reverse. The test *is* the answer and it is written in the callable position
itself, so the selection is decidable from that one node — the same property that
makes `(lambda: ...)()` and `(reader := lambda: ...)()` decidable. `_invoked_lambda()`
still answers with **one** body or none; its contract is unchanged and no
set-valued analysis was introduced.

**The boundary is identity, not truthiness.** `test.value is True` is deliberately
an identity check on an `ast.Constant`. `1`, `1.0`, `'yes'`, `(0,)` and `None` are
all constants with a settled truth value and **none** of them is unwrapped;
neither is a name, a comparison, a `not`, or an `ast.BoolOp`. Deciding those is
constant folding, symbol resolution or control-flow analysis, all of which the
handover excludes and none of which is attempted. Every one of them answers `None`
and leaves the conditional exactly where it was.

**The corrected `ast.IfExp` row**, superseding §14.2's:

| Callable expression | Unwrapped? | Why |
|---|---|---|
| `ast.IfExp` with `test=Constant(True/False)` | **yes** | the source names the branch that runs; one body, decidable from this node |
| `ast.IfExp` with any other test | **no** | the source genuinely does not say which body runs |
| `ast.BoolOp` — `(f or g)()` | **no** | unchanged: a selection conditional on a *value*, not on a literal |

### 16.3 The corrected traversal, exactly

Two behaviour changes, both local and AST-syntactic.

1. A pure `_literal_selection(conditional)` answering `conditional.body` when the
   test is `Constant(True)`, `conditional.orelse` when it is `Constant(False)`, and
   `None` otherwise; `_invoked_lambda()` recurses through it, so a literal
   selection composes with the lambda, call and named-expression chain already
   supported rather than being special-cased beside it.
2. A `visit_IfExp` on the visitor. **The test always runs and is always walked.**
   The branches are walked as Python evaluates them: both when the test is not an
   exact boolean literal (either may run, and the guard errs towards reporting),
   the selected one alone when it is. The order for every conditional that was
   already walked is unchanged — test, then body, then orelse.

The second half is required by the first. The unselected expression is never
evaluated, so no lambda object is built from it and **no default of one runs**; a
capture written there is never made, and reporting it would be a finding against
code that does not execute. This is the one place where the corrected detector
reports *less* than its predecessor, it is disclosed rather than left to be found
(§16.5, row 3), and it narrows no invariant: the invariant is about instants that
*are* captured during the import.

| Construct | Reported | Why |
|---|---|---|
| `NOW = ((lambda: datetime.now(…)) if True else (lambda: None))()` | `datetime.now` | the selected body runs at import |
| `NOW = ((lambda: None) if False else (lambda: datetime.utcnow()))()` | `datetime.utcnow` | likewise, through `orelse` |
| clock in **each** branch, `if True` | the `body` clock only | one branch runs; the other is not evaluated |
| `((lambda _at=datetime.now(…): _at) if False else …)()` | *(none)* | the dead branch builds no lambda, so its defaults never run |
| `((lambda _at=datetime.utcnow(): _at) if True else …)()` | `datetime.utcnow` | the selected branch's defaults do run |
| `((lambda: datetime.now(…)) if datetime.utcnow() else …)()` | `datetime.utcnow` only | the test is walked; a non-literal test unwraps nothing |
| `((lambda: lambda: datetime.now(…)) if True else …)()()` | `datetime.now` | composes with the curried chain |
| `((reader := lambda: datetime.now(…)) if True else …)()` | `datetime.now` | composes with §14's named expression |
| `((lambda: datetime.now(…)) if PREFER_UTC else …)()` | *(none)* | **the preserved control**: a name is not a literal |

Every position §14 walked is still walked, once each; diagnostics, source lines and
references are unchanged; and no position is reported twice.

### 16.4 The committed case

`test_the_import_time_clock_guard_selects_a_literal_conditional_branch` is added
beside the four existing guard cases and runs on every execution of the suite. Its
seven sections are: both reproducers asserted as one mapping; a clock in **each**
selectable branch under `True` and under `False`; the dead branch proved dead at
the one position where it would otherwise still report — a lambda's defaults —
with its live counterpart beside it; a clock in the **condition**, showing normal
evaluation still visible; the curried and walrus compositions; the limit as seven
non-literal tests plus an `ast.BoolOp`, each asserted silent; and a literal
selection outside a callable position.

§14.4's case 7 is **preserved unchanged in behaviour** and its comment corrected:
it reports nothing because its test is a *name*, not because every selection is
undecidable.

### 16.5 Falsification — before and after, and against the real module

Baseline before any change: `sha256 d2f52dbb842a771c168f100b5b8d46700e4154a74252944959004b6d6f31203a`,
identical to §14.5's recorded digest, so the starting point is verifiably the
seventh correction and nothing else. After this correction the module is
`sha256 785c7d40de0720f717cf8ba7d54aeff012ef398981b6bcfa4c6c20c26518f5e7`, copied
to the session scratchpad and used to restore it after every mutation.

**The new case fails against the pre-correction detector, for the finding's own
reason.** Run with the new test present and only the `_literal_selection` branch
removed from the helper:

```
1 failed, 4 passed, 58 deselected
E  AssertionError: assert {'false': [], 'true': []} == {'false': [...], 'true': [...]}
E    {'true': []}  != {'true': ['synthetic.py:3 datetime.now']}
E    {'false': []} != {'false': ['synthetic.py:3 datetime.utcnow']}
```

Both reproducers reported clean — the false negative, reproduced, and not some
other failure standing in for it.

**The detector before and after, on the same inputs.** The pre-correction
behaviour is recorded rather than described, by loading the §14 module's own
top-level detector definitions beside the corrected ones and running both.

| Source | Pre-correction detector | Corrected detector |
|---|---|---|
| the literal-`True` reproducer | `[]` — the false negative, reproduced | `['x.py:3 datetime.now']` |
| the literal-`False` reproducer | `[]` — likewise | `['x.py:3 datetime.utcnow']` |
| a dead branch's lambda defaults | `['x.py:3 datetime.now']` | `[]` — **the one row that reports less**; the expression is never evaluated, so the capture is never made |
| name-conditioned selection (control) | `[]` | `[]` — unchanged, as declared |
| truthy constant `if 1` (control) | `[]` | `[]` — identity, not truthiness |
| the **clean** real module | `[]` | `[]` |

The last row shows no false positive was introduced; the third is the honest
converse and is the only behaviour this correction removes.

**Mutations of the real module.** Each was inserted immediately after `pytestmark`
(line 118), run, then restored from the digested copy before the next.

| # | Mutation applied to the real module | Result | Detector's report |
|---|---|---|---|
| M-AST-10 | `NOW = ((lambda: datetime.now(timezone.utc)) if True else (lambda: None))()` — **the finding's reproducer, verbatim** | **1 failed, 4 passed**, 58 deselected | `test_canonical_settings_graph.py:119 datetime.now` |
| M-AST-11 | `NOW = ((lambda: None) if False else (lambda: datetime.utcnow()))()` — the literal-`False` positive | **1 failed, 4 passed**, 58 deselected | `test_canonical_settings_graph.py:119 datetime.utcnow` |
| M-AST-12 | the existing name-conditioned selection — the **dynamic boundary control** | **5 passed**, 58 deselected | *(none — the declared limit, behaving as declared)* |

M-AST-11 carries independent corroboration that the mutated module really executed
a clock during its import: CPython emitted `DeprecationWarning: datetime.datetime.utcnow()
is deprecated` **at line 119** during collection, which is the interpreter, not
this guard, reporting the capture.

M-AST-12 is the half that keeps the correction honest in the other direction: a
real import-time capture the guard does not report, proving the fix did not widen
the net until every conditional is a finding, and that the remaining limit is real
rather than rhetorical.

**Restoration.**

```
cp scratchpad/corrected.py tests/web/test_canonical_settings_graph.py
sha256sum -c corrected.sha256 → corrected.py: OK
sha256sum tests/web/test_canonical_settings_graph.py
  → 785c7d40de0720f717cf8ba7d54aeff012ef398981b6bcfa4c6c20c26518f5e7
cmp scratchpad/corrected.py tests/web/test_canonical_settings_graph.py → identical
```

Byte-for-byte after every mutation, verified by digest **and** by `cmp`. No other
file was touched during the falsification.

### 16.6 Verification for this correction

Narrow first, then in proportion to the change. Interpreters are the contractually
selected `../venv-web/bin/python` (portal) and `../venv/bin/python` (bot), both
CPython 3.12.3. The two suites share the guarded disposable `freedom_test`
database over the Unix-domain socket and were run **serially**; no production,
shared, TCP-forwarded or unverified database was contacted.

| # | Command | Result |
|---|---|---|
| 1 | `… -m pytest tests/web/test_canonical_settings_graph.py -q -rs -k "captures_no_instant or import_time_clock_guard"` | **5 passed**, 0 failed, **0 skipped**, 58 deselected (4 before; +1 new case) |
| 2 | `… -m pytest tests/web/test_canonical_settings_graph.py -q -rs` (whole module) | **63 passed**, 0 failed, **0 skipped**, 2 warnings (62 before; +1) |
| 3 | `… -m pytest tests/web/test_canonical_settings_graph.py tests/web/test_request_authority_and_lifecycle.py -q -rs` (TC-STRUCT-08/10/11) | **94 passed**, 0 failed, **0 skipped**, 6 warnings (93 before; +1) |
| 4 | `… -m pytest tests/web -q -rs` (complete portal suite) | **701 passed**, 0 failed, **0 skipped**, 20 warnings (700 before; +1) |
| 5 | `TEST_DATABASE_URL=… ../venv/bin/python -m pytest -q -rs` (complete repository/bot suite) | **2260 passed**, 0 failed, **0 skipped**, 1 warning — unchanged |
| 6 | `git diff --check` | Clean |
| 7 | `compileall` under `../venv-web/bin/python` **and** `../venv/bin/python` | Both clean |
| 8 | `sha256sum -c docs/review/phase-3-visual-freeze-manifest.sha256` | **14 OK, 0 FAILED** |
| 9 | `git status --porcelain=v1` | 17 modified, 8 untracked — identical to before this correction |

**Every run above was executed with `-rs`, and every one reported zero skipped.**
Warning counts are unchanged in kind and number: the portal's 20 `httpx`
per-request-cookie deprecations and the bot's 1 `audioop` deprecation are the
pre-existing ones.

**Not run, and not claimed.** `alembic check` was **not** re-run: no schema,
migration, table or model was touched, and §6 row 7 records its result for the work
this corrects. **No formatter, linter or type checker is configured** — the §6 row 9
inspection stands and was not re-run. Mutation testing beyond M-AST-10/11/12 and
the recorded before/after table was not performed; no mutation tool is configured.
No other test module was parsed by the guard, and no sweep of the wider test tree
was attempted (§14.7 limit 4, unchanged).

### 16.7 Nothing was weakened, and the limits that remain

- **The invariant was not narrowed.** The alternative the handover forbids —
  declaring literal conditionals out of scope — was not taken. "Any code that runs
  at import" stands, and is now enforced for this construct too.
- **No previously accepted example became a finding.** Every synthetic source of
  §10, §12 and §14 still reports exactly what it reported, and the clean real
  module reports nothing under both the pre-correction and the corrected detector.
- **One construct now reports less, disclosed above** (§16.3, §16.5 row 3): a
  capture written in a branch the source proves dead. It is not an instant the
  import captures, because the expression is not evaluated.
- **`OperationClock` is unchanged**; **N-04's accepted lifetime is unchanged** and
  still pinned by `assert accepted == 10`; **both live PostgreSQL expiry
  constraints are unchanged and still exercised** against the real guarded
  database. No lifetime extended, no window widened, no sleep introduced.
- **No production code changed.** Nothing under `adapters/`, `application/`,
  `domain/`, `helpers/`, `models/`, `ext/`, `tools/` or `migrations/` was modified.
  No route, schema, migration, dependency, configuration variable, `.env.example`
  entry, provider/engine authority, lifecycle behaviour or runtime grant changed.
  No new package: `ast` is the standard library.
- **Secrets and data.** No `.env`, credential, token, key material or player datum
  was read, printed or included. The synthetic sources are hand-written strings.
- **Unrelated user work is preserved.** Nothing was staged, committed, stashed,
  reset, checked out or cleaned.

**The remaining limits.** (1), (2), (4) and (5) are §14.7's, unchanged. (3) is
**superseded and narrowed**:

1. **The detector is name-based** — `NOW = _read_the_clock()` is not seen.
2. **Invocation is recognised syntactically, not by resolution** — a lambda bound
   in one statement and called through its name in another is a live false
   negative, asserted as a case.
3. **A selection is unwrapped only when its test is an exact boolean literal**
   (supersedes §14.7 limit 3, which claimed no selection could be). What remains
   outside is a selection whose condition is a name, a comparison, a boolean
   operator, or a constant that is merely truthy — `((lambda: datetime.now(…)) if
   flag else (lambda: None))()` executes one of two bodies at import and is not
   reported, because the source does not say which. Asserted as cases 6 and the
   preserved case 7. Closing *that* would need the data-flow or set-valued
   analysis this task excludes; closing the literal case did not.
4. **The guard is scoped to this one module.**
5. **`date`, `time` and `clock` are common words.**
6. **The §8 gaps from the work this corrects are unchanged and still open.**

### 16.8 What review is asked to confirm about this correction

**Implementation review:** that an exact boolean literal makes the selected branch
decidable from the one node, and that `test.value is True/False` is the right
boundary rather than truthiness or constant folding; that `visit_IfExp` walks the
test always and the dead branch never, and that the resulting single behaviour
*removal* is correct rather than a narrowed invariant; that findings remain
deterministic, source ordered and duplicate-free; that the preserved case 7 is now
described accurately; and that §16.7 limit 3 is the true remaining one.

**Security review:** that no lifetime, window, constraint or accepted value was
relaxed; that both expiry constraints remain exercised against real PostgreSQL;
that no production file, dependency, configuration value, migration or schema
changed; and that neither the new case nor the falsification recorded a secret, a
credential or a real player datum.

---

## 17. Status after the eighth correction

**P3.G1 remains OPEN. RAID I-09 remains OPEN. RAID I-10 remains OPEN.**

This section replaces §15 as the document's closing status; §15 is left in place
and marked superseded in part.

Nothing is accepted, and nothing here is an acceptance of itself: this correction
was written by the same working Technical Lead whose detector the finding is
against, and it is remediation evidence for a fresh independent review, not a gate
decision. All changes remain **unstaged and uncommitted**. A fresh independent
implementation review, a distinct security-focused review and the maintainer's
acceptance decision are required before any dependent work continues. **P3.2 and
P3.3 have not been started and must not be.**
