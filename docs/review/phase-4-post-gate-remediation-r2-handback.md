# Phase 4 — post-gate remediation R2 · service-principal identifier boundary · handback

**Date:** 2026-08-31
**Implementing agent and working Technical Lead:** Claude
**Independent Reviewer:** Codex
**Authorizing prompt:** [`phase-4-post-gate-remediation-r2-prompt.md`](phase-4-post-gate-remediation-r2-prompt.md)
**Preceding correction:** [`phase-4-post-gate-remediation-handback.md`](phase-4-post-gate-remediation-handback.md) (R1 — P4-PG1, P4-PG2)

## Status

**Phase 4 remains approved.** Peter Duscha accepted the Phase 4
dependency-direction and domain-correctness gate on 2026-08-29, and this
document does not disturb that decision. This is a **narrow post-gate
correction** to one constructor-validation defect, **P4-PG3**, which Claude
reported out of R1 rather than absorbing into it and which Codex classified as
Important and authorized for this final bounded correction. It reopens no Phase
4 architecture and no accepted ledger, authorization, idempotency, concurrency,
audit or correlation decision.

**R1 is preserved.** P4-PG1's and P4-PG2's corrections and their tests are
unchanged. No adjustment to either was necessary, so none was made.

**Package 5.0 remains `not ready`.** This correction delivers no Package 5.0
implementation, no migration `0014`, no deployment, cutover, production or host
change, and no Package 5.1+ work.

**P4-PG3 is not closed here.** It remains Open pending Codex's independent
disposition. Any governance consequence is the maintainer's decision.

---

## P4-PG3, conceded in concrete Python terms

`CommandCaller.__post_init__` ended:

```python
if self.principal_id is not None and not self.principal_id.strip():
    raise InvalidEnvelopeError(
        "invalid_caller", "A service principal id may not be blank."
    )
```

This is P4-PG2's mistake one constructor away: `.strip()` was called on a value
nothing had established to be text. `CommandCaller` is the application boundary
for the service-principal identifier, and it had two wrong outcomes.

**The escape half.** Every non-string that lacks `.strip()` left the constructor
as a raw `AttributeError` rather than the documented
`InvalidEnvelopeError(code="invalid_caller")`. Observed on the R1-corrected
tree:

```
principal_id=123               -> AttributeError: 'int' object has no attribute 'strip'
principal_id=1.0               -> AttributeError: 'float' object has no attribute 'strip'
principal_id=True              -> AttributeError: 'bool' object has no attribute 'strip'
principal_id=Decimal("1")      -> AttributeError: 'decimal.Decimal' object has no attribute 'strip'
principal_id=["principal"]     -> AttributeError: 'list' object has no attribute 'strip'
principal_id=("principal",)    -> AttributeError: 'tuple' object has no attribute 'strip'
principal_id=uuid4()           -> AttributeError: 'UUID' object has no attribute 'strip'
```

An adapter branches on `code`. A driver-level `AttributeError` is not a code it
can branch on, so a malformed envelope surfaced as an unhandled internal error
instead of a typed refusal.

**The acceptance half.** `bytes` *has* a `.strip()`, so `b"principal"` satisfied
the nonblank rule and was **accepted** as a service-principal identity. It can
never be the `str` that `LedgerPrincipalPort.current_principal(principal_id:
str)` is declared to take and that `application/service_principals.
validate_principal_id` applies its set-membership rule to — so it was an
identity that resolves to nothing, admitted at construction, exactly as
`b"ledger_book"` was an aggregate name that could never match under P4-PG2.

**What this correction is and is not.** It validates the *shape* of the
envelope's identifier and nothing else. It grants no authority:
`LedgerCommandService` continues to resolve the current principal through
`LedgerPrincipalPort` at execution and to attribute the audit row to the
principal the **port** returned, never to the request's own `principal_id`.
That separation is finding P4-R2's rule and is untouched.

---

## Required sequence, as executed

### 1. Regression tests added first, and their pre-fix failure

29 tests were added to `tests/test_p4_commands.py` and run against the
**unchanged** R1-corrected `application/commands.py`:

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_commands.py
```

Result: **16 failed, 105 passed in 0.20s.**

```
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[1]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[0]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[123]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[True]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[False]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[1.0]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[identifier6]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[principal]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[identifier8]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[identifier9]
FAILED tests/test_p4_commands.py::test_a_non_string_principal_id_is_refused_not_raised_through[identifier10]
FAILED tests/test_p4_commands.py::test_a_bytes_principal_id_is_refused_although_it_has_a_strip
FAILED tests/test_p4_commands.py::test_a_malformed_principal_id_is_never_converted_or_decoded[foundry-module]
FAILED tests/test_p4_commands.py::test_a_malformed_principal_id_is_never_converted_or_decoded[123]
FAILED tests/test_p4_commands.py::test_a_malformed_principal_id_is_never_converted_or_decoded[1.0]
FAILED tests/test_p4_commands.py::test_a_malformed_principal_id_is_never_converted_or_decoded[True]
16 failed, 105 passed in 0.20s
```

The distinct pre-fix errors, verbatim (`grep -E '^E ' | sort -u`):

```
E       AttributeError: 'UUID' object has no attribute 'strip'
E       AttributeError: 'bool' object has no attribute 'strip'
E       AttributeError: 'decimal.Decimal' object has no attribute 'strip'
E       AttributeError: 'float' object has no attribute 'strip'
E       AttributeError: 'int' object has no attribute 'strip'
E       AttributeError: 'list' object has no attribute 'strip'
E       AttributeError: 'tuple' object has no attribute 'strip'
E       Failed: DID NOT RAISE <class 'application.commands.InvalidEnvelopeError'>
```

Reading the two halves of the finding out of that output precisely:

- The **three** `DID NOT RAISE` failures are exactly the three `bytes` cases —
  `[principal]` (`b"principal"`), `test_a_bytes_principal_id_is_refused_although_
  it_has_a_strip`, and `test_a_malformed_principal_id_is_never_converted_or_
  decoded[foundry-module]` (`b"foundry-module"`). That is the acceptance half:
  `bytes` was admitted as an identity.
- The remaining **13** failures are `AttributeError` escaping the constructor.
  That is the escape half.
- The pre-fix pass of `test_a_nonblank_string_principal_id_remains_accepted`,
  `test_an_accepted_principal_id_is_carried_verbatim`,
  `test_a_blank_string_principal_id_remains_refused` and
  `test_the_envelope_does_not_impose_the_configured_principal_vocabulary` is
  expected and is the point: those pin behavior this correction must **not**
  change, and they pass identically before and after.

### 2. Production correction

`application/commands.py`, `CommandCaller.__post_init__`, final clause only. The
type is established before the existing nonblank rule is applied; nothing is
coerced, decoded or normalized:

```python
if self.principal_id is not None:
    # Type before blankness, for the reason `ExpectedVersion` gives
    # about its own aggregate type: `.strip()` on a value never
    # established as text leaves this constructor as a raw
    # `AttributeError` an adapter cannot branch on, and `bytes` — which
    # has a `.strip()` of its own — would be admitted as an identity the
    # `str` lookup in `LedgerPrincipalPort.current_principal()` can
    # never match. Refused, never decoded and never coerced with
    # `str(...)`. Shape only: whether this identifier is configured, and
    # what it may do, stays the port's answer at execution.
    if not isinstance(self.principal_id, str):
        raise InvalidEnvelopeError(
            "invalid_caller",
            "A service principal is identified in text, not by "
            f"{type(self.principal_id).__name__}.",
        )
    if not self.principal_id.strip():
        raise InvalidEnvelopeError(
            "invalid_caller", "A service principal id may not be blank."
        )
```

This is the same shape the module already used twice — `ExpectedVersion.
aggregate_type` (P4-PG2) and `CommandCaller.discord_user_id` (P4-PG1) — rather
than a new mechanism. The refusal code is the pre-existing `invalid_caller`; no
new code was published, and the blank message is byte-identical to the one it
replaced.

### 3–4. Focused and full verification

Recorded in *Verification* below.

### 5. Diff review

Recorded in *Diff review* below.

### 6. Returned to Codex

This document is the return. P4-PG3 is not declared closed.

---

## Files changed, and why

| File | Change | Why |
|---|---|---|
| `application/commands.py` | `CommandCaller.__post_init__`: a `str` check before the existing nonblank rule, plus its explanatory comment | The minimum correction to P4-PG3. This constructor is the application boundary for the service-principal identifier. |
| `tests/test_p4_commands.py` | +29 tests in one new `# --- P4-PG3 · …` section | The mandatory regression coverage plus the guard tests that pin what must not change. |
| `docs/review/phase-4-post-gate-remediation-r2-handback.md` | This document | The handback the prompt requires. |

**No other production, test or documentation file was changed.** Scope was
exactly the prompt's expected scope; no third file became necessary and no
widening was requested.

Both changed files are **untracked** in the working tree (Phase 4 work is
uncommitted), so neither carries a diff against `HEAD`. Each was edited by a
single exact-string replacement at one anchor — the four-line `principal_id`
clause in `application/commands.py`, and the end of the existing
`test_a_blank_service_principal_is_refused` block in `tests/test_p4_commands.py`
— so every other byte of both files is unchanged by construction, including the
whole of R1's work.

## The exact validation rule after correction

`CommandCaller.__post_init__`, in order. Rules 1–4 are **unchanged from R1**;
rule 5 is the correction; rule 6 is R1's rule text, unchanged, now reached only
for an actual string:

1. `source` must be an `AuditSource` → else `invalid_caller`.
2. Exactly one of `discord_user_id` / `principal_id` is non-`None` → else
   `invalid_caller`.
3. If `discord_user_id` is not `None`, it must be an `int` and must not be a
   `bool` → else `invalid_caller`. *(P4-PG1, unchanged.)*
4. `discord_user_id <= 0` → `invalid_caller`. *(Unchanged.)*
5. **New.** If `principal_id` is not `None`, it must be a `str` → else
   `invalid_caller`. No coercion with `str(...)`, no `bytes` decoding, no
   normalization: `123`, `1.0`, `True`, `False`, `Decimal("1")`, `b"principal"`,
   a `list`, a `tuple` and a `UUID` are refusals, not conversions.
6. `principal_id.strip()` must be nonblank → `invalid_caller`. *(Unchanged.)*

**What the rule deliberately does not do.**

- It does not apply `application/service_principals.validate_principal_id`'s
  closed character vocabulary or its 64-character limit at the envelope. The
  prompt forbids it, and the reason is the one finding P4-R2 records: whether an
  identifier is *configured* is an authorization answer, and the port owns it.
  `"Foundry-Module"`, `"foundry module"`, `"x" * 200` and `"prïncipal"` are
  therefore still accepted **envelopes** and are refused at execution by
  `LedgerPrincipalPort.current_principal()` returning `None`. A pinned test
  asserts this.
- It does not normalize. `" padded "` is still accepted and still stored
  verbatim, exactly as before.
- It changes no authorization, resolution, scope, audit-attribution or
  idempotency-hashing behavior. `LedgerCommandService` still resolves the
  current principal at execution and still hashes and attributes the principal
  the port returned.

## Regression coverage delivered

Table-driven, synthetic values only. Every item the prompt required:

| Required | Test | Cases |
|---|---|---|
| a valid nonblank string principal ID remains accepted | `test_a_nonblank_string_principal_id_remains_accepted` | `"foundry-module"`, `"import-worker"`, `"bot"`, `" padded "` |
| blank strings remain refused with `invalid_caller` | `test_a_blank_string_principal_id_remains_refused` (+ pre-existing `test_a_blank_service_principal_is_refused`) | `""`, `"   "`, `"\t"`, `"\n"` |
| integers, booleans, floats, bytes, lists and tuples refused with `InvalidEnvelopeError(code="invalid_caller")`, not raw `AttributeError` | `test_a_non_string_principal_id_is_refused_not_raised_through` | `1`, `0`, `123`, `True`, `False`, `1.0`, `Decimal("1")`, `b"principal"`, `["principal"]`, `("principal",)`, `uuid4()` |
| a bytes value that previously passed because it had `.strip()` is refused | `test_a_bytes_principal_id_is_refused_although_it_has_a_strip` | `b"principal"` |
| malformed values are not silently converted or decoded | `test_a_malformed_principal_id_is_never_converted_or_decoded` | `b"foundry-module"`, `123`, `1.0`, `True` |
| — accepted values are not normalized either | `test_an_accepted_principal_id_is_carried_verbatim` | identity (`is`) check on `"foundry-module"` |
| — the envelope does not take over the port's question | `test_the_envelope_does_not_impose_the_configured_principal_vocabulary` | `"Foundry-Module"`, `"foundry module"`, `"x" * 200`, `"prïncipal"` |

Each refusal test asserts `refusal.value.code == "invalid_caller"` inside
`pytest.raises(InvalidEnvelopeError)`. Because `AttributeError` is not a
subclass of `InvalidEnvelopeError` (a `ValueError`), these tests fail on an
escaping driver-level error as well as on acceptance — which is how all 16
failed before the fix.

`test_a_malformed_principal_id_is_never_converted_or_decoded` additionally
asserts that the refusal message contains the offending **type name** and does
**not** contain `str(value)`. That is both the no-coercion proof
(`str(b"foundry-module")` is `"b'foundry-module'"` and
`b"foundry-module".decode()` is a *different* identity — neither appears
anywhere) and the safe-message proof: a malformed identity cannot be echoed into
a log, an audit row or an adapter's reply.

`tests/test_p4_commands.py` goes from 92 to 121 tests (+29), which is the whole
of the bot suite's `2960 → 2989` delta.

## P4-PG1 and P4-PG2 remain passing, unchanged

Neither R1 test was edited, renamed, re-parametrized or deleted; the insertion
was made at a single anchor between the P4-PG1 block and the pre-existing
audit-source test. All 37 R1-owned cases still collect and pass on the R2 tree:

```sh
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_commands.py \
  -k "snowflake or boolean_discord or non_integer_discord or \
      numeric_string_discord or aggregate_type"
# 37 passed, 84 deselected in 0.05s
```

Collected, in file order: `test_a_caller_requires_a_positive_snowflake[0|-1|
-4200000000000000001]`, `test_an_actual_positive_snowflake_remains_accepted[1|
42|4200000000000000001]`, `test_a_boolean_discord_id_is_refused[True|False]`,
`test_a_non_integer_discord_id_is_refused_not_raised_through` (8 cases),
`test_a_numeric_string_discord_id_is_not_silently_coerced`,
`test_an_expected_version_requires_an_aggregate_type` (2),
`test_a_nonblank_string_aggregate_type_remains_accepted` (3),
`test_a_blank_string_aggregate_type_remains_refused` (4),
`test_a_non_string_aggregate_type_is_refused_not_raised_through` (9),
`test_a_bytes_aggregate_type_could_never_match_the_type_it_names`, and
`test_requiring_a_version_of_a_different_aggregate_type_refuses_the_command`.

## Verification

Repository-prescribed interpreters, exported test database URL, suites run
**serially** because the Python suites share one disposable database.

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
```

**Focused — the corrected file's own suite**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_commands.py
# 121 passed in 0.09s
```

**Focused — every Phase 4 test file**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/test_p4_domain_quantities.py tests/test_p4_commands.py \
  tests/test_p4_ledger_domain.py tests/test_p4_ledger_service.py \
  tests/test_p4_idempotent_execution.py tests/test_p4_characterization.py \
  tests/test_p4_domain_isolation.py
# 534 passed, 1 warning in 4.28s
```

**Full suites, against the R2 tree**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
# 2989 passed, 1 warning in 145.14s (0:02:25)

/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
# 2824 passed, 80 skipped, 1137 warnings in 136.14s (0:02:16)

node --test "foundry-module/tests/"*.test.mjs
# tests 171 · suites 0 · pass 171 · fail 0 · cancelled 0 · skipped 0 · todo 0
```

The web skip count is **exactly 80**, as required. The `-rs` reasons, in full:

```
SKIPPED [54] tests/web/test_p3_2_matrix.py:155: permitted cells are asserted by the per-route success cases
SKIPPED [26] tests/web/test_p3_3_matrix.py:198: permitted cells are asserted by the per-route success cases
```

Both are the expected matrix-cell skips. Neither is a database-marked skip, so
`TEST_DATABASE_URL` was genuinely in effect — the failure mode
`.agents/AGENTS.md` warns about (roughly 1141 passed / 1362 skipped, exit 0)
did not occur. The bot suite reported **zero** skips. The one bot-suite warning
is the pre-existing `audioop` `DeprecationWarning` from the installed
`discord.py`, unrelated to this correction.

**Compile and whitespace**

```sh
/opt/discord-bots/venv/bin/python -m compileall -q \
  application/commands.py tests/test_p4_commands.py      # exit 0
/opt/discord-bots/venv-web/bin/python -m compileall -q \
  application/commands.py tests/test_p4_commands.py      # exit 0
git diff --check                                          # exit 0, clean
```

Every figure above was produced against the R2 tree in this session. R1's
submitted baseline is reproduced nowhere as new evidence. For the reviewer's
convenience only: bot `2960 → 2989` is the +29 new tests and nothing else; web
`2824 passed / 80 skipped` and Foundry `171 passed` are unchanged, as a
correction confined to one constructor clause should leave them.

## Checks not run, and why

| Check | Status |
|---|---|
| Formatter | **Not configured** in this repository. Not run, and not introduced by this correction. |
| Linter | **Not configured.** Same. |
| Type checker | **Not configured.** Same. |
| Migration consistency | **Not applicable.** No migration exists in or is touched by this correction. |
| Database or integration behavior beyond the suites above | Not separately exercised. The defect is in a pure in-memory constructor with no persistence path; the full PostgreSQL-backed suites above cover the rest of the tree. |
| Deployment, staging or production verification | **Not run and not authorized.** |

`git diff --check` is reported as run and clean, and what it did *not* cover is
worth stating: both changed files are **untracked**, so they are outside its
inspection. They were therefore checked directly — `grep -nP '[ \t]+$'` matched
nothing in either file, and `grep -cP '\t'` reported **0** tab characters in
each.

## Diff review

- **Scope / unrelated changes:** none. `git status --short` lists the **same 50
  entries** before and after the code change — no file added, removed or newly
  modified by the fix; it becomes 51 once this handback is written, which is
  this document and nothing else. Every other maintainer-owned and agent-owned
  uncommitted change is untouched. Nothing was reset, reverted, reformatted or
  rewritten. No adjacent cleanup was performed.
- **Secrets:** none added. A grep of both changed files for token, secret,
  password, credential, API-key, connection-string, `DISCORD_` and `OAUTH`
  patterns matched only the `discord_user_id` **field name** in pre-existing and
  new test lines. No credential, database URL or service-account material
  appears.
- **Real data:** none. Every value is synthetic. The new principal identifiers
  (`"foundry-module"`, `"import-worker"`, `"bot"`, `"principal"`) are shape
  fixtures, not configured production principals, and no real service-principal
  identifier, credential or production value was used. `COUNCIL_USER =
  4200000000000000001` is the file's pre-existing synthetic constant.
- **Unsafe logging:** none. The change logs nothing. The new refusal message
  names only `type(self.principal_id).__name__` and never the offending value,
  so a malformed identifier — which may be attacker-supplied — cannot reach a
  log line, an audit row or a user-facing reply. A test asserts this directly.
- **Authorization and resolution:** unchanged. This validates the *shape* of an
  identifier, which proves nothing about whether it exists or what it may do.
  `LedgerPrincipalPort`, `validate_principal_id`, `LedgerPrincipal`,
  `LedgerScope`, the authorization ports, audit attribution and idempotency
  hashing are all untouched.
- **Behavioral surface:** the only externally visible change is that inputs
  which previously raised `AttributeError` now raise
  `InvalidEnvelopeError("invalid_caller", …)`, and that `bytes` is now refused
  instead of accepted. No previously accepted **valid** envelope is refused.

## Confirmations

- **No Package 5 work.** No Package 5.0 plan, design, finding, decision, risk or
  readiness state was created or updated. Package 5.0 remains `not ready`.
- **`docs/review/Handover information` was not changed.** It remains the active
  Package 5.0 handover. Its mtime is unchanged at `2026-08-31T10:22:07`,
  predating both edits in this session (`21:20:31` and `21:21:03`), and its
  SHA-256 is
  `a2fa5a4265181609959abaf259616975089ccba0da11e7d3d5fdd0b423919992`.
- **No migration** was added, edited or applied. Migration `0014` was not
  created.
- **No deployment, host account, group, permission, service, database or
  credential mutation** occurred. Nothing outside this repository working tree
  was touched.
- **No Discord, Sheets, Foundry or production database contact.** The new tests
  are in-process constructor tests over synthetic values; the suites run against
  the disposable `freedom_test` database only.
- **No dependency, framework, adapter, route or command was added.**
- **No ledger domain or ledger service change.** No change to
  `validate_principal_id`, `LedgerPrincipal`, `LedgerPrincipalPort`,
  authorization ports, scopes or audit attribution. No change to idempotency
  hashing, receipt schemas, or command envelopes beyond this one validation.
- **The configured-principal character vocabulary was not imposed at the
  envelope boundary**, as the prompt requires. The port remains responsible for
  resolving whether an identifier exists and is authorized.
- **R1 preserved.** P4-PG1's and P4-PG2's corrections and tests are unchanged;
  no adjustment to either was necessary.
- **The Phase 4 acceptance decision is unchanged**, P4-PG3 is not closed here,
  and nothing in this correction releases Package 5.

## Unexpected and residual findings

### Reported, not absorbed: two further instances of the same defect class

Reviewing `application/commands.py` for a fourth instance of the class Codex
identified — a constructor acting on a value before establishing its type —
found **two more**, in the envelope's other two text fields. Neither is in this
prompt's scope, so **neither was fixed**. Both are reported here for Codex's
disposition, in line with the instruction to stop and report rather than absorb.

Both were observed on the R2 tree by direct construction, not inferred from
reading.

#### P4-PG4 (proposed, Important) — a malformed idempotency key escapes the envelope boundary

`CommandEnvelope.__post_init__` delegates to
`application/idempotency.validate_key`, which opens `if not key.strip():`
before anything establishes that `key` is text. Observed:

```
idempotency_key=123               -> AttributeError: 'int' object has no attribute 'strip'
idempotency_key=True              -> AttributeError: 'bool' object has no attribute 'strip'
idempotency_key=1.0               -> AttributeError: 'float' object has no attribute 'strip'
idempotency_key=None              -> AttributeError: 'NoneType' object has no attribute 'strip'
idempotency_key=['k']             -> AttributeError: 'list' object has no attribute 'strip'
idempotency_key=b'interaction-1'  -> TypeError: '<' not supported between instances of 'int' and 'str'
```

Every one escapes as a driver-level error rather than the documented
`InvalidEnvelopeError(code="invalid_request_key")` that
`CommandEnvelope.__post_init__` is written to re-raise — its
`except IdempotencyKeyError` never sees them. The `bytes` case is the same
acceptance-shaped hazard as P4-PG3's, one step later: `b"interaction-1".strip()`
is truthy and `len()` works, so it passes the blank and length rules and only
fails inside the control-character scan, as an unrelated `TypeError`.

This matters more than a type-name quibble because the idempotency key is the
value that makes a retry recognisable as one. A key that is not `str` cannot
match the `str` a previous attempt stored, so a caller whose adapter typed it
wrongly would, if the escaping error were ever handled generically upstream,
spend a *new* key on every retry — the duplicate-execution failure the
mechanism exists to prevent.

**Why it was not fixed here.** The rule lives in
`application/idempotency.py`, and this prompt confines production change to
`application/commands.py` and forbids changing "idempotency hashing, command
envelopes beyond this validation". `validate_key` is also shared with
`application.snapshots.SnapshotImportRecord`, so correcting it touches an
accepted Phase 2/3 path and needs its own authorization and evidence.

#### P4-PG5 (proposed, Important) — a stored receipt's command name bypasses `StoredReceiptUnreadable`

`CommandReceipt.__post_init__` opens `if not self.command.strip():` before
establishing that `command` is text. Observed at construction:

```
command=123                          -> AttributeError: 'int' object has no attribute 'strip'
command=True                         -> AttributeError: 'bool' object has no attribute 'strip'
command=1.0                          -> AttributeError: 'float' object has no attribute 'strip'
command=['x']                        -> AttributeError: 'list' object has no attribute 'strip'
command=b'ledger.post_transaction'   -> ACCEPTED as b'ledger.post_transaction'
```

The consequence is on the **replay path**, which is why this is more than the
constructor's own tidiness. `CommandReceipt.from_payload` reads
`payload["command"]` out of `idempotency_keys.response` and deliberately
converts a bad row into the typed `StoredReceiptUnreadable`:

```python
except (KeyError, TypeError, ValueError) as error:
    raise StoredReceiptUnreadable(str(error)) from None
```

`AttributeError` is in neither tuple, so a stored row whose `command` is not a
string escapes that contract entirely:

```
stored command=123    -> AttributeError: 'int' object has no attribute 'strip'   <-- ESCAPES
stored command=True   -> AttributeError: 'bool' object has no attribute 'strip'  <-- ESCAPES
stored command=None   -> AttributeError: 'NoneType' object has no attribute 'strip' <-- ESCAPES
stored command=['x']  -> AttributeError: 'list' object has no attribute 'strip'  <-- ESCAPES
```

`StoredReceiptUnreadable` exists precisely so that an unreadable receipt for a
**spent** key is neither re-executed nor invented. A raw `AttributeError` on
that path is an unhandled error where the module documents a typed one, and a
caller cannot distinguish it from any other internal failure — against a key
whose effect may already have committed. `test_an_unreadable_stored_receipt_is_
never_invented` does not cover it: every payload in its table has a string
`command`.

**Why it was not fixed here.** The prompt authorizes only P4-PG3 remediation,
scopes the production change to `CommandCaller`'s identifier validation, and
forbids changing receipt schemas. Correcting `CommandReceipt` also raises a
design question this correction has no authority to settle: whether the fix
should raise `ValueError` (matching the constructor's existing vocabulary, which
`from_payload` already catches) or the typed `InvalidEnvelopeError` used
elsewhere in the module.

#### Correction to an earlier statement in this document

An earlier draft of this handback asserted that the remaining `__post_init__`
checks in `application/commands.py` all establish type before use, and that
`CommandReceipt`'s checks raise `ValueError` by design. That was wrong on both
counts, as the probes above show, and it is corrected here rather than left to
stand. The checks that *are* type-safe are `ExpectedVersion.aggregate_id`,
`ExpectedVersion.version`, `CommandEnvelope.caller`,
`CommandEnvelope.correlation_id`, `CommandEnvelope.expected_version`,
`CommandReceipt.correlation_id`, `CommandReceipt.version` and both the key and
value checks on `CommandReceipt.facts` — all `isinstance`-first.

#### Where the class now stands

| Value | Boundary | State |
|---|---|---|
| `CommandCaller.discord_user_id` | envelope | corrected (P4-PG1, R1) |
| `ExpectedVersion.aggregate_type` | envelope | corrected (P4-PG2, R1) |
| `CommandCaller.principal_id` | envelope | corrected (P4-PG3, this document) |
| `CommandEnvelope.idempotency_key` | envelope | **open — P4-PG4 proposed** |
| `CommandReceipt.command` | receipt / replay | **open — P4-PG5 proposed** |

That is the whole of the class in `application/commands.py` and its one
delegated validator; no other value in the module is acted on before its type is
established. Codex is asked to dispose of P4-PG4 and P4-PG5 — including whether
they warrant one further bounded correction, or belong in Package 5.0's first
real adapter work, where these boundaries acquire their first non-test caller.

### Context, not findings

Two observations are recorded as context, because neither is a defect under the
accepted design:

1. **The envelope accepts identifiers no configured principal could have.**
   `"Foundry-Module"`, `"foundry module"`, a 200-character string and
   `"prïncipal"` are all valid *envelopes* after this correction. That is
   deliberate and prompt-mandated: shape is the envelope's question, existence
   and authority are the port's, and they are answered at execution.
   `LedgerPrincipalPort.current_principal()` returns `None` for every one of
   them, which is a refusal. Moving that check forward would put an
   authorization answer in an object built from the request — the P4-R2 mistake.
2. **Current reach is unchanged from R1's statement.** No adapter is yet wired
   to this envelope: `CommandCaller`, `CommandEnvelope` and `CommandReceipt` are
   constructed only by Phase 4's own tests and services, so P4-PG3 — and the two
   findings above — are latent boundary defects rather than live production
   faults. That is a statement about today's reach, not an argument that any of
   them does not need fixing: Package 5.0 wires the first real adapter to this
   boundary, which is exactly when a latent defect stops being latent.

Nothing in this work suggested a materially broader defect in the Phase 4
ledger, authorization, idempotency, concurrency or audit **mechanisms**
themselves. P4-PG4 and P4-PG5 are input-validation escapes at their boundaries,
not faults in the durable idempotency or attribution design.

## Request for independent re-review

Codex is asked to independently re-review **P4-PG3** against the R2 tree and to
supply the disposition. Suggested focus:

1. that the corrected `CommandCaller` clause establishes `str` before `.strip()`
   and refuses every non-`str` through the pre-existing `invalid_caller` code —
   **without** `str(...)` coercion, `bytes` decoding or normalization;
2. that the nonblank rule, its message and every accepted-value semantic are
   unchanged, including that `" padded "` is still accepted verbatim;
3. that the envelope did **not** take on the configured-principal character
   vocabulary, the length limit, or any part of the port's resolution or
   authorization question, and that `LedgerCommandService` still resolves and
   attributes through `LedgerPrincipalPort` at execution;
4. that the regression tests genuinely fail on the pre-fix R1 tree — the failing
   command and its exact output are recorded above — rather than being
   assertions written around the new code; and
5. that R1's P4-PG1 and P4-PG2 corrections and tests are byte-unchanged and
   still passing; and
6. the two further instances of the same defect class reported above —
   **P4-PG4** (`CommandEnvelope.idempotency_key`) and **P4-PG5**
   (`CommandReceipt.command`, escaping the `StoredReceiptUnreadable` contract on
   the replay path) — for disposition on whether either needs its own bounded
   correction. Neither was fixed here; both are outside this prompt's scope.

P4-PG3 is not closed by this document. If it is accepted with no further
Blocking or Important Phase 4 finding, the post-gate remediation is complete and
work returns to the existing Package 5.0 readiness and security-remediation
sequence exactly where it stood.
