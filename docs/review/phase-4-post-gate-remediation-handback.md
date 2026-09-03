# Phase 4 — post-gate constructor-validation remediation · handback

**Date:** 2026-08-31
**Implementing agent and working Technical Lead:** Claude
**Independent Reviewer:** Codex
**Authorizing prompt:** [`phase-4-post-gate-remediation-prompt.md`](phase-4-post-gate-remediation-prompt.md)

## Status

**Phase 4 remains approved.** Peter Duscha accepted the Phase 4 dependency-
direction and domain-correctness gate on 2026-08-29, and this document does not
disturb that decision. This is a **narrow post-gate correction** to two
constructor-validation defects Codex found in a later repository review. It
reopens no Phase 4 architecture, and no accepted ledger, authorization,
idempotency, concurrency, audit or correlation decision.

**Package 5.0 remains `not ready`.** This correction authorizes and delivers no
Package 5.0 implementation, no migration `0014`, no deployment, cutover,
production or host change, and no Package 5.1+ work. After independent
re-review and acceptance, work resumes from the existing Package 5.0 handover
under its unchanged readiness conditions.

**Neither finding is closed here.** P4-PG1 and P4-PG2 remain Open pending
Codex's independent disposition. Any governance consequence is the maintainer's
decision.

---

## The two defects, conceded

Both are the same mistake in two places: a constructor that is the application
boundary for a value **acted on that value before establishing its type**.

### P4-PG1 — malformed Discord identity accepted, or escaping the typed boundary

`CommandCaller.__post_init__` read:

```python
if self.discord_user_id is not None and self.discord_user_id <= 0:
    raise InvalidEnvelopeError(
        "invalid_caller", "Discord IDs must be positive snowflakes."
    )
```

`x <= 0` is a comparison, not a check, and it had two wrong outcomes:

- **`True` was accepted as Discord user ID 1.** `bool` is an `int` subclass, so
  `True <= 0` is `False` and construction succeeded. `CommandCaller(...,
  discord_user_id=True).discord_user_id` was `True`, and `is_human` was `True`.
  (`False` was refused, but only incidentally — as the integer `0`, by the
  magnitude rule, not because a flag is not an identity.)
- **A value not orderable against `0` raised a raw `TypeError`** out of the
  constructor rather than the documented
  `InvalidEnvelopeError(code="invalid_caller")` — for example `"123"`:
  `TypeError: '<=' not supported between instances of 'str' and 'int'`. An
  adapter branches on `code`; a driver-level `TypeError` is not something it can
  branch on.
- A third, unstated consequence of the same line: values that *are* orderable
  against `0` but are not integers — `1.0`, `Decimal("123")` — passed the check
  and were accepted as snowflakes. These are covered by the same corrected rule.

### P4-PG2 — malformed expected-version aggregate type escaping the typed boundary

`ExpectedVersion.__post_init__` read:

```python
if not self.aggregate_type.strip():
    raise InvalidEnvelopeError(
        "invalid_expected_version",
        "An expected version must name the aggregate type it constrains.",
    )
```

`.strip()` was called before anything proved `aggregate_type` was a string:

- `ExpectedVersion(1, uuid4(), 0)` raised `AttributeError: 'int' object has no
  attribute 'strip'` rather than
  `InvalidEnvelopeError(code="invalid_expected_version")`. Same for `True`,
  `None`, `1.0`, a `list` and a `UUID`.
- `b"ledger_book"` — which *does* have `.strip()` — was **accepted**. It can
  never equal the `str` that every `describes()` caller passes, so it was a
  precondition that could never be satisfied, admitted at construction. The
  failure mode `ExpectedVersion` exists to prevent is a stale write that
  reported success.

---

## Required sequence, as executed

### 1. Regression tests added first, and their pre-fix failure

Tests were added to `tests/test_p4_commands.py` and run against the **unchanged**
`application/commands.py`:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_commands.py
```

Result: **20 failed, 72 passed in 0.21s.**

```
FAILED tests/test_p4_commands.py::test_a_boolean_discord_id_is_refused[True]
FAILED tests/test_p4_commands.py::test_a_non_integer_discord_id_is_refused_not_raised_through[123_0]
FAILED tests/test_p4_commands.py::test_a_non_integer_discord_id_is_refused_not_raised_through[4200000000000000001]
FAILED tests/test_p4_commands.py::test_a_non_integer_discord_id_is_refused_not_raised_through[1.0]
FAILED tests/test_p4_commands.py::test_a_non_integer_discord_id_is_refused_not_raised_through[4.2e+18]
FAILED tests/test_p4_commands.py::test_a_non_integer_discord_id_is_refused_not_raised_through[value4]
FAILED tests/test_p4_commands.py::test_a_non_integer_discord_id_is_refused_not_raised_through[123_1]
FAILED tests/test_p4_commands.py::test_a_non_integer_discord_id_is_refused_not_raised_through[value6]
FAILED tests/test_p4_commands.py::test_a_non_integer_discord_id_is_refused_not_raised_through[value7]
FAILED tests/test_p4_commands.py::test_a_numeric_string_discord_id_is_not_silently_coerced
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[1]
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[0]
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[True]
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[False]
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[None]
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[1.0]
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[ledger_book]
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[aggregate_type7]
FAILED tests/test_p4_commands.py::test_a_non_string_aggregate_type_is_refused_not_raised_through[aggregate_type8]
FAILED tests/test_p4_commands.py::test_a_bytes_aggregate_type_could_never_match_the_type_it_names
```

The distinct pre-fix errors, verbatim:

```
E       Failed: DID NOT RAISE <class 'application.commands.InvalidEnvelopeError'>
E       TypeError: '<=' not supported between instances of 'str' and 'int'
E       TypeError: '<=' not supported between instances of 'bytes' and 'int'
E       TypeError: '<=' not supported between instances of 'list' and 'int'
E       TypeError: '<=' not supported between instances of 'tuple' and 'int'
E       AttributeError: 'int' object has no attribute 'strip'
E       AttributeError: 'bool' object has no attribute 'strip'
E       AttributeError: 'NoneType' object has no attribute 'strip'
E       AttributeError: 'float' object has no attribute 'strip'
E       AttributeError: 'list' object has no attribute 'strip'
E       AttributeError: 'UUID' object has no attribute 'strip'
```

`DID NOT RAISE` is the acceptance half of each finding — `True` as Discord user
1, and `b"ledger_book"` as an aggregate name. The `TypeError`/`AttributeError`
lines are the escape half.

Two pre-fix outcomes are worth naming precisely, because they are the finding
rather than noise:

- `test_a_boolean_discord_id_is_refused[False]` **passed** before the fix, since
  `False` was caught as `0`. Only `[True]` failed. After the fix both are
  refused as booleans.
- `test_a_non_integer_discord_id_is_refused_not_raised_through[1.0]` and
  `[value4]` (`Decimal("123")`) failed as `DID NOT RAISE`, not as `TypeError`:
  those values were silently *accepted* as snowflakes.

### 2. Production correction

`application/commands.py`, two constructors, type established before the
existing rule is applied. Nothing is coerced.

`CommandCaller.__post_init__`:

```python
if self.discord_user_id is not None:
    if isinstance(self.discord_user_id, bool) or not isinstance(
        self.discord_user_id, int
    ):
        raise InvalidEnvelopeError(
            "invalid_caller",
            "A Discord user is identified by a snowflake integer, not "
            f"by {type(self.discord_user_id).__name__}.",
        )
    if self.discord_user_id <= 0:
        raise InvalidEnvelopeError(
            "invalid_caller", "Discord IDs must be positive snowflakes."
        )
```

`ExpectedVersion.__post_init__`:

```python
if not isinstance(self.aggregate_type, str):
    raise InvalidEnvelopeError(
        "invalid_expected_version",
        "An aggregate type is named in text, not by "
        f"{type(self.aggregate_type).__name__}.",
    )
if not self.aggregate_type.strip():
    raise InvalidEnvelopeError(
        "invalid_expected_version",
        "An expected version must name the aggregate type it constrains.",
    )
```

The `bool`-before-`int` shape is the one `ExpectedVersion.version` already used
in this same module; the correction makes the two consistent rather than
inventing a mechanism.

### 3–4. Focused and full verification

Recorded in *Verification* below.

### 5. Diff review

Recorded in *Diff review* below.

### 6. Returned to Codex

This document is the return. Neither finding is declared closed.

---

## Files changed, and why each was necessary

| File | Change | Why |
|---|---|---|
| `application/commands.py` | Two constructors: a type check before the existing magnitude/nonblank rule | The minimum correction to P4-PG1 and P4-PG2. Both constructors are the application boundary for the value they validate. |
| `tests/test_p4_commands.py` | +31 tests, and `from decimal import Decimal` | The mandatory regression coverage. `Decimal` is the representative non-integer that the old comparison *accepted* rather than raised on. |

**No other production or test file was changed.** The expected scope in the
prompt was exactly these two files, and no third file was necessary. Both files
are untracked in the working tree (Phase 4 work is uncommitted), so they carry
no diff against `HEAD`; they were edited by targeted string replacement, not
rewritten.

## The exact validation rules after the correction

**`CommandCaller`** — unchanged order, one rule inserted:

1. `source` must be an `AuditSource` → else `invalid_caller`.
2. Exactly one of `discord_user_id` / `principal_id` is non-`None` → else
   `invalid_caller`.
3. **New.** If `discord_user_id` is not `None`, it must be an `int` and must not
   be a `bool` → else `invalid_caller`. No coercion: `"123"`, `1.0`,
   `Decimal("123")`, `b"123"`, a `list` and a `tuple` are refusals, not
   conversions.
4. `discord_user_id <= 0` → `invalid_caller`. Now reached only for an actual
   integer, so it can no longer raise `TypeError`.
5. `principal_id` must not be blank → `invalid_caller`. **Unchanged** (see
   *Residual finding*).

**`ExpectedVersion`** — unchanged order, one rule inserted:

1. **New.** `aggregate_type` must be a `str` → else `invalid_expected_version`.
   No `str(...)` coercion.
2. `aggregate_type.strip()` must be nonblank → `invalid_expected_version`.
   **Unchanged**, and now reached only for an actual string.
3. `aggregate_id` must be a `UUID` → `invalid_expected_version`. Unchanged.
4. `version` must be an `int` and not a `bool` → `invalid_expected_version`.
   Unchanged.
5. `version` must not be negative → `invalid_expected_version`. Unchanged.

Accepted-value semantics are unchanged: a positive integer snowflake is still
accepted, `0` and negatives are still refused, a nonblank string aggregate type
is still accepted (including one with surrounding whitespace, which is stored
verbatim as before), expected-version semantics and the accepted aggregate name
are untouched.

## Regression coverage delivered

Every item the prompt required, table-driven, synthetic values only:

| Required | Test | Cases |
|---|---|---|
| positive integer snowflake still accepted | `test_an_actual_positive_snowflake_remains_accepted` | `1`, `42`, `4200000000000000001` |
| `0` and negatives still refused `invalid_caller` | `test_a_caller_requires_a_positive_snowflake` (pre-existing) | `0`, `-1`, `-4200000000000000001` |
| `True` and `False` refused `invalid_caller` | `test_a_boolean_discord_id_is_refused` | `True`, `False` |
| non-integer IDs incl. numeric string and float refused `invalid_caller`, not `TypeError` | `test_a_non_integer_discord_id_is_refused_not_raised_through` | `"123"`, `"4200000000000000001"`, `1.0`, `4.2e+18`, `Decimal("123")`, `b"123"`, `list`, `tuple` |
| numeric string not silently coerced | `test_a_numeric_string_discord_id_is_not_silently_coerced` | `"4200000000000000001"` |
| nonblank string `aggregate_type` still accepted | `test_a_nonblank_string_aggregate_type_remains_accepted` | `"ledger_book"`, `"character"`, `" book "` |
| blank aggregate types still refused `invalid_expected_version` | `test_a_blank_string_aggregate_type_remains_refused` (+ pre-existing `test_an_expected_version_requires_an_aggregate_type`) | `""`, `"   "`, `"\t"`, `"\n"` |
| non-string aggregate types incl. int and bool refused `invalid_expected_version`, not `AttributeError` | `test_a_non_string_aggregate_type_is_refused_not_raised_through` | `1`, `0`, `True`, `False`, `None`, `1.0`, `b"ledger_book"`, `list`, `UUID` |
| bytes cannot masquerade as an aggregate name | `test_a_bytes_aggregate_type_could_never_match_the_type_it_names` | `b"ledger_book"` |

Each refusal test asserts `refusal.value.code`, and each is written as
`pytest.raises(InvalidEnvelopeError)`. Because `TypeError` and `AttributeError`
are not subclasses of `InvalidEnvelopeError` (a `ValueError`), these tests fail
on an escaping driver-level error as well as on acceptance — which is exactly
how they failed before the fix.

`tests/test_p4_commands.py` goes from 61 to 92 tests (+31), which is the whole
of the bot suite's `2929 → 2960` delta.

## Verification

Repository-prescribed interpreters, exported database URL, suites run
**serially** because the Python suites share one disposable database.

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
```

**Focused — the corrected file's own suite**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_commands.py
# 92 passed in 0.07s
```

**Focused — every Phase 4 test file**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/test_p4_domain_quantities.py tests/test_p4_commands.py \
  tests/test_p4_ledger_domain.py tests/test_p4_ledger_service.py \
  tests/test_p4_idempotent_execution.py tests/test_p4_characterization.py \
  tests/test_p4_domain_isolation.py
# 505 passed, 1 warning in 4.54s
```

**Full suites, against the corrected tree**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
# 2960 passed, 1 warning in 143.25s (0:02:23)

/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
# 2824 passed, 80 skipped, 1137 warnings in 136.99s (0:02:16)

node --test "foundry-module/tests/"*.test.mjs
# tests 171 · pass 171 · fail 0 · cancelled 0 · skipped 0 · todo 0
```

The web skip count is **exactly 80**, as required. `-rs` reason summary:

```
SKIPPED [54] tests/web/test_p3_2_matrix.py:155: permitted cells are asserted by the per-route success cases
SKIPPED [26] tests/web/test_p3_3_matrix.py:198: permitted cells are asserted by the per-route success cases
```

Both are the expected matrix-cell skips; neither is a database-marked skip, so
`TEST_DATABASE_URL` was in fact in effect. The bot suite reported **zero**
skips.

**Compile and whitespace**

```sh
/opt/discord-bots/venv/bin/python -m compileall -q \
  application/commands.py tests/test_p4_commands.py      # exit 0
/opt/discord-bots/venv-web/bin/python -m compileall -q \
  application/commands.py tests/test_p4_commands.py      # exit 0
git diff --check                                          # exit 0, clean
```

Every figure above was produced against the corrected tree in this session. The
prompt's pre-remediation baseline is **not** reproduced here as evidence.
Comparing only for the reviewer's convenience: bot `2929 → 2960` is the +31 new
tests and nothing else; web `2824 passed / 80 skipped` and Foundry `171 passed`
are unchanged, as a correction confined to two constructors should leave them.

## Checks not run, and why

| Check | Status |
|---|---|
| Formatter | **Not configured** in this repository. Not run, and not introduced by this correction. |
| Linter | **Not configured.** Same. |
| Type checker | **Not configured.** Same. |
| Migration consistency | **Not applicable.** No migration exists in or is touched by this correction. |
| Database/integration behaviour beyond the suites above | Not separately exercised. Both defects are in pure in-memory constructors with no persistence path; the full PostgreSQL-backed suites above cover the rest of the tree. |
| Deployment, staging or production verification | **Not run and not authorized.** |

`git diff --check` is reported as run and clean. It is worth stating what it did
*not* cover: both changed files are **untracked**, so they are outside its
inspection. Trailing whitespace and tab characters in the two files were
therefore checked directly — `grep -nP '[ \t]+$'` matched nothing in either
file, and both contain zero tab characters.

## Diff review

- **Unrelated changes:** none. `git status --short` listed 48 entries before
  this correction and the same 48 after the code change — no file added, removed
  or newly modified by the fix. It lists 49 once this handback document is
  written, which is that document and nothing else. Every other maintainer-owned
  and agent-owned uncommitted change is untouched; nothing was reset, reverted,
  reformatted or rewritten.
- **Secrets:** none added. No token, credential, database URL, OAuth secret or
  service-account material appears in either changed file.
- **Real player data:** none. Every test value is synthetic. `COUNCIL_USER =
  4200000000000000001` is the pre-existing synthetic constant in this file, not
  a production Discord ID, and no production Discord ID was added.
- **Unsafe logging:** none. Neither change logs anything. The two new refusal
  messages name only a **type name** (`type(x).__name__`) and never the
  offending value, so a malformed identity cannot be echoed into a log, an audit
  row or a Discord response.
- **Identity resolution and authorization:** unchanged. This correction
  validates the *shape* of an id, which — as the `CommandCaller` docstring
  already states — proves nothing about whether it exists or what it may do.
  `AuthorizationPort` and `LedgerPrincipalPort` resolution is untouched.

## Confirmations

- **No Package 5 work.** No Package 5.0 design, finding, decision, risk or
  readiness state was updated. Package 5.0 remains `not ready`.
- **`docs/review/Handover information` was not changed.** It remains the active
  Package 5.0 handover. Its file timestamp (`2026-08-31T10:22:07`) predates both
  edits in this session (`20:41:41` and `20:42:09`).
- **No migration** was added, edited or applied. Migration `0014` was not
  created.
- **No deployment, host, service, account, group, permission, database or
  credential mutation** occurred. Nothing outside the repository working tree
  was touched.
- **No Discord, Sheets, Foundry or production database contact.** The tests are
  in-process constructor tests over synthetic values; the suites run against the
  disposable `freedom_test` database only.
- **No dependency, framework, adapter, route or command was added.**
- **No ledger domain or ledger service change; no authorization port,
  service-principal scope or audit attribution change; no idempotency hashing or
  receipt schema change.**
- **The Phase 4 acceptance decision is unchanged**, no finding is closed here,
  and nothing in this correction releases Package 5.

## Residual finding — reported, not absorbed

**P4-PG3 (proposed, Important) — `CommandCaller.principal_id` has the identical
defect class, one line below the P4-PG1 fix, and was deliberately left alone.**

`CommandCaller.__post_init__` still ends:

```python
if self.principal_id is not None and not self.principal_id.strip():
```

This is P4-PG2's mistake — `.strip()` before the type is established — applied
to the service-principal identity. Observed on the corrected tree:

```
principal_id=123          -> AttributeError
principal_id=1.0          -> AttributeError
principal_id=True         -> AttributeError
principal_id=b'p'         -> ACCEPTED
```

So a malformed service-principal id still escapes as a raw `AttributeError`
instead of `invalid_caller`, and `b'p'` is still accepted as a principal id that
no `LedgerPrincipalPort` string lookup can match.

**It was not fixed, and that is deliberate.** The authorizing prompt scopes this
correction to P4-PG1 and P4-PG2 and instructs: "Do not clean up adjacent
validation code that is not required by P4-PG1 or P4-PG2", and to report rather
than absorb a further boundary defect. Fixing it would also touch the
service-principal identity path, which the prompt places out of scope. It is
raised here for Codex's disposition and the maintainer's decision on whether it
warrants its own bounded correction.

Its practical exposure today is the same as P4-PG1's and P4-PG2's: no adapter is
yet wired to this envelope — `CommandCaller` and `ExpectedVersion` are
constructed only by Phase 4's own tests and services — so all three are latent
boundary defects rather than live production faults. That is a statement about
current reach, not an argument for leaving any of them.

No other unexpected finding arose. Nothing in this work suggested a materially
broader defect in the Phase 4 ledger, authorization, idempotency, concurrency or
audit mechanisms.

## Request for independent re-review

Codex is asked to independently re-review **P4-PG1** and **P4-PG2** against the
corrected tree, and to supply the disposition. Suggested focus:

1. that the corrected `CommandCaller` rule accepts exactly the positive integer
   snowflakes and refuses `bool` and every non-`int`, **without coercion**;
2. that the corrected `ExpectedVersion` rule establishes `str` before
   `.strip()`, **without `str(...)` coercion**, and leaves the nonblank rule,
   the accepted aggregate name and expected-version semantics unchanged;
3. that the regression tests genuinely fail on the pre-fix tree — the failing
   command and its exact output are recorded above — and are not merely
   assertions written around the new code;
4. that no accepted Phase 4 decision, contract or error code changed: the
   refusal codes are the pre-existing `invalid_caller` and
   `invalid_expected_version`, and no new code was published; and
5. the residual **P4-PG3** report above, for disposition on whether it needs its
   own bounded correction.

Neither finding is closed by this document. On acceptance, continuation returns
to the existing Package 5.0 readiness and security-remediation sequence exactly
where it stood.
