# Phase 4 — post-gate remediation R3 · idempotency-key and stored-receipt type boundaries · handback

**Date:** 2026-08-31
**Implementing agent and working Technical Lead:** Claude
**Independent Reviewer:** Codex
**Authorizing prompt:** [`Handover information`](Handover%20information) — "Claude implementation handover — Phase 4 post-gate remediation R3"
**Preceding corrections:** [`phase-4-post-gate-remediation-handback.md`](phase-4-post-gate-remediation-handback.md) (R1 — P4-PG1, P4-PG2) and [`phase-4-post-gate-remediation-r2-handback.md`](phase-4-post-gate-remediation-r2-handback.md) (R2 — P4-PG3)
**Independent review being answered:** [`phase-4-post-gate-r2-independent-review.md`](phase-4-post-gate-r2-independent-review.md)

## Status and authority

**Phase 4 remains approved.** Peter Duscha accepted the Phase 4
dependency-direction and domain-correctness gate on 2026-08-29 and this document
does not disturb that decision. This is the **final bounded post-gate
correction** the R2 independent review required, covering exactly two Important
findings: **P4-PG4** and **P4-PG5**. It reopens no Phase 4 architecture and no
accepted ledger, authorization, idempotency, concurrency, audit or correlation
decision.

**P4-PG1, P4-PG2 and P4-PG3 are Closed and are preserved.** Their
implementations and tests are unchanged; evidence that all three still pass on
this tree is below.

**Neither finding is closed here.** P4-PG4 and P4-PG5 remain Open pending
Codex's independent disposition. Any governance consequence is the maintainer's
decision.

**Package 5.0 is untouched and remains `not ready`.** This correction delivers
no Package 5.0 implementation, no migration `0014`, no host, database,
deployment, cutover or production change, and no Package 5.1+ work. P5.0-SR1,
P5.0-SR2, P5.0-R5, OD-62 through OD-66 and the required operational evidence are
exactly where they stood. No controlled status, change, RAID, decision or
roadmap document was updated.

---

## The two findings, conceded precisely

### P4-PG4 — a malformed idempotency key escaped the typed envelope boundary

`application/idempotency.py`'s shared validator opened on the value:

```python
def validate_key(key: str) -> str:
    if not key.strip():
```

Nothing had established that `key` was text, and the finding has the same two
halves the P4-PG1…PG3 class had.

**The escape half.** Every non-string lacking `.strip()` left the validator as a
raw `AttributeError`. `CommandEnvelope.__post_init__` catches only
`IdempotencyKeyError`, so its documented
`InvalidEnvelopeError(code="invalid_request_key")` contract was bypassed
entirely; the Foundry submission boundary's `SubmissionRefused` translation was
bypassed for the same reason. An adapter branches on `code`. A driver-level
`AttributeError` is not a code it can branch on.

**The acceptance half.** `bytes` has a `.strip()` and a `len()` of its own, so
`b"interaction-1"` satisfied the blank rule and the length rule and failed only
inside the control-character scan — as an unrelated `TypeError`
(`'<' not supported between instances of 'int' and 'str'`, because iterating
`bytes` yields integers). Both observed forms are in the pre-fix output below.

**Why this value in particular.** The idempotency key is what makes a retry
recognisable as a retry. A key that is not `str` can never match the `str` a
previous attempt stored, so a caller whose adapter typed it wrongly would — if
the escaping error were ever handled generically upstream — spend a *new* key on
every retry. That is the duplicate execution the mechanism exists to prevent.

### P4-PG5 — a malformed stored receipt command escaped `StoredReceiptUnreadable`

`application/commands.py`, `CommandReceipt.__post_init__`, opened the same way:

```python
def __post_init__(self) -> None:
    if not self.command.strip():
```

Direct construction leaked `AttributeError`; `bytes` was **accepted** as a
command name no `str` comparison could ever match.

The consequence is on the **replay path**, and that is what makes it more than
constructor tidiness. `CommandReceipt.from_payload()` reads `payload["command"]`
out of `idempotency_keys.response` and deliberately converts a bad stored row
into the typed `StoredReceiptUnreadable`:

```python
except (KeyError, TypeError, ValueError) as error:
    raise StoredReceiptUnreadable(str(error)) from None
```

`AttributeError` is in neither tuple. A spent key whose stored `command` is not
a string therefore escaped that contract against a key **whose effect may
already have committed** — and the `bytes` case did something worse than escape:
`application/ledger.py`'s `_replay_record` returned a `CommandReceipt` naming
`b"ledger.post_transaction"` as a successful replay. Both are proved
end-to-end through `LedgerCommandService` in the pre-fix output below.

---

## The caller inventory, and a correction to the R2 handback

The R2 handback stated that `validate_key` "is also shared with
`application.snapshots.SnapshotImportRecord`". **That statement is false, and it
is corrected here.** `SnapshotImportRecord.__post_init__` **does not call
`validate_key`**: it implements the same three rules independently and raises
plain `ValueError`, as `application/snapshots.py:176-195` shows. Nothing in this
correction touches it, exactly as the prompt requires.

`rg` over every production directory, verbatim:

```
$ rg -n --no-heading "validate_key" application/ adapters/ domain/ web/ ext/ models/ helpers/ tools/
application/commands.py:64:from application.idempotency import IdempotencyKeyError, validate_key
application/commands.py:259:            validate_key(self.idempotency_key)
application/idempotency.py:77:        validate_key(self.key)
application/idempotency.py:88:def validate_key(key: str) -> str:
application/foundry/submission.py:71:    validate_key,
application/foundry/submission.py:495:            validate_key(request_key)
```

**Three production callers, and all three are covered by regressions:**

| # | Caller | Translation | Regressions live in |
|---|---|---|---|
| 1 | `CommandEnvelope.__post_init__` (`application/commands.py:259`) | `IdempotencyKeyError` → `InvalidEnvelopeError(code="invalid_request_key")` | `tests/test_p4_commands.py` |
| 2 | `IdempotencyRecord.__post_init__` (`application/idempotency.py:77`) | none — the typed error propagates | `tests/test_p4_commands.py` |
| 3 | `SnapshotSubmissionService._submit` (`application/foundry/submission.py:495`) | `IdempotencyKeyError` → `SubmissionRefused(error.code, …)` | `tests/test_snapshot_submission.py` |

Callers 1 and 3 already translate `IdempotencyKeyError` correctly, so **neither
translation site needed changing**: correcting the shared validator was
sufficient for both, and that is why `application/commands.py` changes only for
P4-PG5.

---

## Regression-first sequence, as executed

### 1–2. Tests added first, and their exact pre-fix failure

All regressions were written and run against the **unchanged** production tree.

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_commands.py
# 71 failed, 146 passed in 0.74s

/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_ledger_service.py
# 7 failed, 116 passed in 0.33s

/opt/discord-bots/venv/bin/python -m pytest -q tests/test_snapshot_submission.py
# 10 failed, 66 passed in 0.48s
```

**88 pre-fix failures**, grouped by test (`sed 's/\[.*//' | sort | uniq -c`):

```
P4-PG4
  12 tests/test_p4_commands.py::test_a_non_string_key_is_refused_not_raised_through
  12 tests/test_p4_commands.py::test_a_malformed_key_reaches_the_envelope_as_a_typed_refusal
  12 tests/test_p4_commands.py::test_an_idempotency_record_refuses_a_malformed_key
   4 tests/test_p4_commands.py::test_a_malformed_key_is_never_coerced_or_decoded
   1 tests/test_p4_commands.py::test_a_bytes_key_is_refused_although_it_has_a_strip
  10 tests/test_snapshot_submission.py::test_a_malformed_request_key_keeps_the_documented_refusal

P4-PG5
  12 tests/test_p4_commands.py::test_a_non_string_command_name_is_refused_with_a_value_error
  12 tests/test_p4_commands.py::test_a_malformed_stored_command_becomes_an_unreadable_receipt
   4 tests/test_p4_commands.py::test_a_malformed_command_name_is_never_coerced_or_decoded
   1 tests/test_p4_commands.py::test_a_bytes_command_name_is_refused_although_it_has_a_strip
   1 tests/test_p4_commands.py::test_a_stored_bytes_command_is_neither_accepted_nor_decoded
   7 tests/test_p4_ledger_service.py::test_a_spent_key_with_a_malformed_stored_command_is_never_re_executed
```

The distinct pre-fix errors, verbatim (`grep -E '^E ' | sort -u`):

```
E       AttributeError: 'NoneType' object has no attribute 'strip'
E       AttributeError: 'UUID' object has no attribute 'strip'
E       AttributeError: 'bool' object has no attribute 'strip'
E       AttributeError: 'decimal.Decimal' object has no attribute 'strip'
E       AttributeError: 'float' object has no attribute 'strip'
E       AttributeError: 'int' object has no attribute 'strip'
E       AttributeError: 'list' object has no attribute 'strip'
E       AttributeError: 'tuple' object has no attribute 'strip'
E       Failed: DID NOT RAISE <class 'ValueError'>
E       Failed: DID NOT RAISE <class 'application.commands.StoredReceiptUnreadable'>
E       Failed: DID NOT RAISE <class 'application.ledger.LedgerRefused'>
E   TypeError: '<' not supported between instances of 'int' and 'str'
```

Reading the two halves of each finding out of that output precisely:

- **The exception-escape case.** The eight `AttributeError` lines are the
  escapes. They occur at `application/idempotency.py:99` (P4-PG4) and
  `application/commands.py:331` (P4-PG5) on the pre-fix tree.
- **The bytes-acceptance case, P4-PG4.** The single `TypeError: '<' not
  supported between instances of 'int' and 'str'` is `b"interaction-1"` passing
  the blank and length rules and failing inside the control-character scan as an
  untyped error.
- **The bytes-acceptance case, P4-PG5.** The `DID NOT RAISE` lines are bytes
  being *accepted*, not merely mistyped: `ValueError` for direct construction,
  `StoredReceiptUnreadable` for `from_payload()`, and — the one that matters
  most — `LedgerRefused` for the full application-service replay. The captured
  frame reads:

  ```
  _ test_a_spent_key_with_a_malformed_stored_command_is_never_re_executed[ledger.post_transaction] _
  command = b'ledger.post_transaction'
  ...
  >       with pytest.raises(LedgerRefused) as refusal:
  E       Failed: DID NOT RAISE <class 'application.ledger.LedgerRefused'>
  ```

  That is a spent ledger key answering a caller with a receipt naming a command
  in bytes, instead of `original_result_unavailable`.

**The guard tests passed pre-fix, which is the point.** The valid-value,
blank-value, over-length, control-character, verbatim-return and
valid-submission tests pass identically before and after: they pin behaviour
this correction must **not** change. `test_a_valid_request_key_still_submits_
and_is_stored_verbatim` in particular passed on the unchanged tree.

### 3. Production corrections

Two files, one added block each. Both establish type before the existing value
rules and change nothing else.

**`application/idempotency.py`, `validate_key()`:**

```python
    if not isinstance(key, str):
        raise IdempotencyKeyError(
            "invalid_request_key",
            f"A request key is text, not {type(key).__name__}.",
        )
    if not key.strip():
        ...
```

**`application/commands.py`, `CommandReceipt.__post_init__()`:**

```python
        if not isinstance(self.command, str):
            raise ValueError(
                "A command receipt names its command in text, not by "
                f"{type(self.command).__name__}."
            )
        if not self.command.strip():
            ...
```

Each is preceded by the explanatory comment the module's existing style uses.
The full comments are in the files; their substance is stated in the *findings*
section above.

**`ValueError` for P4-PG5, deliberately, and not `AttributeError` in the catch
list.** The prompt forbids merely widening the catch tuple, and the reason
matters: widening it would leave direct construction leaking and `bytes`
accepted, and would make `from_payload()` swallow an `AttributeError` from
*anywhere* under it. Raising `ValueError` at the source matches the
constructor's existing vocabulary for every other malformed field
(`correlation_id`, `version`, fact keys, fact values), and `from_payload()`
already catches it. `from_payload()` itself was not modified.

**Proof each production file gained exactly one block and nothing else.** Both
files are edited by a single anchored exact-string insertion, so every other
byte is unchanged by construction. That is verified rather than asserted:
removing the one added block from each file reproduces its pre-edit SHA-256
exactly.

| File | Pre-edit SHA-256 | Block removed → reproduces it |
|---|---|---|
| `application/idempotency.py` | `f1f9fa551b5e6f95952dafed79c7d86403b85b2a37d9b6e273b1aff8bfef7db7` | **True** |
| `application/commands.py` | `9cf45020b4969aea7ce00b451b49f8faf57366d61fc76dd718a282acc40cbc36` | **True** |

### 4–6. Verification, diff review, return

Recorded below. This document is the return; neither finding is declared closed.

---

## Files changed, and why

| File | Change | Why |
|---|---|---|
| `application/idempotency.py` | `validate_key()`: an `isinstance(key, str)` check before the existing blank rule, plus its comment | The minimum correction to P4-PG4, at the shared validator all three callers reach |
| `application/commands.py` | `CommandReceipt.__post_init__`: an `isinstance(self.command, str)` check before the existing nonblank rule, plus its comment | The minimum correction to P4-PG5, at the source rather than at the catch list |
| `tests/test_p4_commands.py` | +96 tests in two new sections, `# --- P4-PG4 · …` and `# --- P4-PG5 · …`; the `application.idempotency` import widened to four more names | The owning file for the envelope's idempotency-key boundary and for command/receipt construction |
| `tests/test_p4_ledger_service.py` | +1 parametrized test (7 cases) beside the existing unreadable-receipt regressions | The owning file for ledger replay behaviour through the application service |
| `tests/test_snapshot_submission.py` | +2 tests (11 cases) beside the existing `test_an_unusable_request_key_is_refused` | The owning file for the third `validate_key` consumer, the Foundry submission boundary |
| `docs/review/phase-4-post-gate-remediation-r3-handback.md` | This document | The handback the prompt requires |

**No other production, test or documentation file was changed.** The expected
production scope in the prompt was exactly the two production files; no third
production file became necessary and no widening was requested.

**No new test file and no new abstraction was created.** Each area went to the
smallest existing owner: the shared validator and command/receipt construction
to `tests/test_p4_commands.py` (which already owns the envelope's whole
`# --- the idempotency key` section and already imported `KEY_MAX_LENGTH` from
`application/idempotency.py`), the Foundry consumer to
`tests/test_snapshot_submission.py`, and ledger replay to
`tests/test_p4_ledger_service.py`.

**The `application/idempotency.py` diff against `HEAD` is larger than this
correction**, and that must not be misread: it also carries the R1 remediation's
`canonical_request_hash` work, which is pre-existing uncommitted Phase 4 code
this session did not touch. The checksum proof above is what bounds *this*
correction's contribution to that file.

**No test-guard declaration was needed.** `application/idempotency.py` and
`application/commands.py` are both already enumerated in
`PERMITTED_PHASE_4_PRODUCTION` in `tests/web/test_p3_4_static_assets.py`, so the
P3.4 scope guard passes unchanged and that file was not edited.

---

## The exact validation and replay behaviour after correction

Probed directly against the corrected tree, not inferred from reading.

### `validate_key()`

```
123                -> IdempotencyKeyError('invalid_request_key'): A request key is text, not int.
True               -> IdempotencyKeyError('invalid_request_key'): A request key is text, not bool.
1.0                -> IdempotencyKeyError('invalid_request_key'): A request key is text, not float.
None               -> IdempotencyKeyError('invalid_request_key'): A request key is text, not NoneType.
b'interaction-1'   -> IdempotencyKeyError('invalid_request_key'): A request key is text, not bytes.
['k']              -> IdempotencyKeyError('invalid_request_key'): A request key is text, not list.
('k',)             -> IdempotencyKeyError('invalid_request_key'): A request key is text, not tuple.
Decimal('1')       -> IdempotencyKeyError('invalid_request_key'): A request key is text, not Decimal.
UUID(...)          -> IdempotencyKeyError('invalid_request_key'): A request key is text, not UUID.
'interaction-1'    -> returned verbatim: interaction-1
```

The rules in order, rules 2–4 **unchanged**:

1. **New.** `key` must be a `str` → else `IdempotencyKeyError("invalid_request_key")`.
   No `str(...)` coercion, no `bytes` decoding, no normalization, no truncation.
2. `key.strip()` must be nonblank → `invalid_request_key`. *(Unchanged, message byte-identical.)*
3. `len(key) <= KEY_MAX_LENGTH` → `invalid_request_key`. *(Unchanged.)*
4. No control character or `\x7f` → `invalid_request_key`. *(Unchanged.)*
5. The key is returned **verbatim**; `" padded "` is still accepted and still
   returned unmodified.

### The three callers

```
CommandEnvelope(idempotency_key=123)              -> InvalidEnvelopeError('invalid_request_key'): A request key is text, not int.
CommandEnvelope(idempotency_key=None)             -> InvalidEnvelopeError('invalid_request_key'): A request key is text, not NoneType.
CommandEnvelope(idempotency_key=b'interaction-1') -> InvalidEnvelopeError('invalid_request_key'): A request key is text, not bytes.

IdempotencyRecord(key=123)                        -> IdempotencyKeyError('invalid_request_key'): A request key is text, not int.
IdempotencyRecord(key=b'k')                       -> IdempotencyKeyError('invalid_request_key'): A request key is text, not bytes.

SnapshotSubmissionService.submit(request_key=…)   -> SubmissionRefused('invalid_request_key'), snapshots and idempotency rows both empty
```

Never a raw exception at any of the three, and the code is the pre-existing
published one at each: no new refusal code was introduced anywhere.

### `CommandReceipt` construction and replay

```
CommandReceipt(command=123)                        -> ValueError: A command receipt names its command in text, not by int.
CommandReceipt(command=True)                       -> ValueError: … not by bool.
CommandReceipt(command=None)                       -> ValueError: … not by NoneType.
CommandReceipt(command=b'ledger.post_transaction') -> ValueError: … not by bytes.
CommandReceipt(command=['x'])                      -> ValueError: … not by list.

from_payload({"command": 123, …})                  -> StoredReceiptUnreadable: A command receipt names its command in text, not by int.
from_payload({"command": None, …})                 -> StoredReceiptUnreadable: … not by NoneType.
from_payload({"command": b'ledger.post_transaction', …}) -> StoredReceiptUnreadable: … not by bytes.
```

The rules in order:

1. **New.** `command` must be a `str` → else `ValueError`. No coercion, no
   decoding, no normalization.
2. `command.strip()` must be nonblank → `ValueError`. *(Unchanged, message
   byte-identical.)*
3. `from_payload()` consequently converts every malformed stored command into
   `StoredReceiptUnreadable` through its **existing, unmodified** catch tuple.
4. The receipt payload schema and the accepted command names are unchanged. A
   valid name round-trips verbatim, including `" ledger.post_transaction "`.

### The replay contract, end to end

`test_a_spent_key_with_a_malformed_stored_command_is_never_re_executed` posts a
command, replaces the stored `idempotency_keys.response` with one whose
`command` is malformed, and retries the same request. For each of the seven
malformed shapes it asserts, on the corrected tree:

- `LedgerRefused(code="original_result_unavailable")` — the existing refusal,
  through `_replay_record`'s existing `except StoredReceiptUnreadable`;
- `len(harness.transactions()) == 1` — **no second transaction posted**;
- `harness.audit_actions() == [TRANSACTION_POSTED]` — **no new audit effect**;
- `len(harness.receipts()) == 1` and the stored `response` is still the exact
  corrupted mapping — **the stored receipt is not replaced**, and no receipt is
  invented for it.

No refusal message names the offending value, so a malformed stored row cannot
be echoed into a log line, an append-only row or a caller's reply.

---

## Mandatory synthetic coverage, item by item

Every value below is synthetic. No real key, principal, credential or player
datum appears.

### P4-PG4

| Required | Test | Cases |
|---|---|---|
| valid nonblank string keys accepted and returned verbatim | `test_a_valid_key_is_accepted_and_returned_verbatim` (identity check with `is`) | `"interaction-1"`, `"k"`, `" padded "`, `"k" * KEY_MAX_LENGTH` |
| blank strings retain `invalid_request_key` | `test_a_blank_key_keeps_its_published_refusal` | `""`, `"   "`, `"\t"`, `"\n"` |
| overlong strings retain `invalid_request_key` | `test_an_over_long_key_keeps_its_published_refusal` | `KEY_MAX_LENGTH + 1` |
| control characters retain `invalid_request_key` | `test_a_control_character_key_keeps_its_published_refusal` | `"with\nnewline"`, `"with\x00null"`, `"bell\x07"`, `"\x7f"` |
| integers, booleans, floats, `None`, bytes, lists, tuples refused by `validate_key()` with `IdempotencyKeyError("invalid_request_key")` | `test_a_non_string_key_is_refused_not_raised_through` | `1`, `0`, `123`, `True`, `False`, `1.0`, `Decimal("1")`, `None`, `b"interaction-1"`, `["interaction-1"]`, `("interaction-1",)`, `uuid4()` |
| — the bytes case specifically, which previously passed the blank and length rules | `test_a_bytes_key_is_refused_although_it_has_a_strip` | `b"interaction-1"` |
| the same values reach `CommandEnvelope` as `InvalidEnvelopeError("invalid_request_key")`, never a raw exception | `test_a_malformed_key_reaches_the_envelope_as_a_typed_refusal` | the same 12 |
| malformed keys are neither coerced nor decoded | `test_a_malformed_key_is_never_coerced_or_decoded` | `b"interaction-1"`, `123`, `1.0`, `True` |
| `IdempotencyRecord` refuses malformed keys through the shared validator | `test_an_idempotency_record_refuses_a_malformed_key` | the same 12 |
| — and still accepts and still refuses what it did | `test_an_idempotency_record_still_accepts_a_valid_key`, `…_still_refuses_a_blank_key` | `"interaction-1"`, `" padded "`; `""`, `"   "` |
| the Foundry submission boundary retains its documented safe refusal | `test_a_malformed_request_key_keeps_the_documented_refusal` | `1`, `0`, `123`, `True`, `False`, `1.0`, `None`, `b"foundry-module:test-key"`, `["k"]`, `("k",)` |
| — and its valid behaviour | `test_a_valid_request_key_still_submits_and_is_stored_verbatim` | `KEY` |
| — accepted envelopes still carry the key verbatim | `test_an_envelope_still_carries_an_accepted_key_verbatim` | `" padded "` |

### P4-PG5

| Required | Test | Cases |
|---|---|---|
| valid nonblank command names accepted and round-trip unchanged | `test_a_valid_command_name_is_accepted_and_round_trips_unchanged` (asserts the field, `as_payload()` and `from_payload()`) | `"ledger.post_transaction"`, `"x"`, `" ledger.post_transaction "` |
| blank strings remain refused with `ValueError` | `test_a_blank_command_name_remains_refused` (+ pre-existing `test_a_receipt_requires_a_command_name`) | `""`, `"   "`, `"\t"`, `"\n"` |
| integers, booleans, floats, `None`, bytes, lists, tuples refused with `ValueError`, never `AttributeError` | `test_a_non_string_command_name_is_refused_with_a_value_error` | `1`, `0`, `123`, `True`, `False`, `1.0`, `Decimal("1")`, `None`, `b"ledger.post_transaction"`, `["…"]`, `("…",)`, `uuid4()` |
| — the bytes case, previously accepted | `test_a_bytes_command_name_is_refused_although_it_has_a_strip` | `b"ledger.post_transaction"` |
| `from_payload()` converts each malformed stored command into `StoredReceiptUnreadable` | `test_a_malformed_stored_command_becomes_an_unreadable_receipt` | the same 12 |
| bytes are neither accepted nor decoded | `test_a_stored_bytes_command_is_neither_accepted_nor_decoded`, `test_a_malformed_command_name_is_never_coerced_or_decoded` | `b"ledger.post_transaction"`, `123`, `1.0`, `True` |
| an unreadable stored ledger receipt returns `original_result_unavailable` with no posting, audit event, idempotency replacement or retry execution | `test_a_spent_key_with_a_malformed_stored_command_is_never_re_executed` | `123`, `True`, `1.0`, `None`, `b"ledger.post_transaction"`, `["x"]`, `("x",)` |

Each refusal test asserts through `pytest.raises`, and each type assertion is
strict where it needs to be: `test_a_non_string_command_name_is_refused_with_a_
value_error` asserts `type(refusal.value) is ValueError`, and because
`AttributeError` is not a `ValueError` these tests fail on an escaping
driver-level error as well as on acceptance — which is how all 88 failed before
the fix.

The no-coercion tests assert that the refusal message contains the offending
**type name** and does **not** contain `str(value)`, and for bytes that it does
not contain `value.decode()` either. `str(b"interaction-1")` is
`"b'interaction-1'"` and `b"interaction-1".decode()` is a *different* identity;
neither appears anywhere. That is both the no-coercion proof and the safe-message
proof.

---

## P4-PG1, P4-PG2 and P4-PG3 remain passing, unchanged

No R1 or R2 test was edited, renamed, re-parametrized or deleted. Both new
sections were inserted at anchors — between the existing `# --- the idempotency
key` and `# --- correlation` sections, and at the end of the file — so every
earlier test is byte-unchanged.

```sh
/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_commands.py \
  -k "snowflake or boolean_discord or non_integer_discord or \
      numeric_string_discord or aggregate_type"
# 37 passed, 180 deselected in 0.06s          (P4-PG1 + P4-PG2; R2 recorded 37)

/opt/discord-bots/venv/bin/python -m pytest -q tests/test_p4_commands.py \
  -k "principal_id or service_principal or principal"
# 32 passed, 185 deselected in 0.06s          (P4-PG3)
```

The 37 is the same 37 the R2 handback enumerates, collected in the same file
order.

**The test arithmetic corroborates that nothing was removed or renamed.**

| File | R2 tree | This tree | Delta | Accounted for by |
|---|---|---|---|---|
| `tests/test_p4_commands.py` | 121 | **217** | +96 | 59 P4-PG4 cases + 37 P4-PG5 cases |
| `tests/test_p4_ledger_service.py` | 116 | **123** | +7 | the 7 replay cases |
| `tests/test_snapshot_submission.py` | 65 | **76** | +11 | 10 malformed-key cases + 1 valid-key guard |
| Focused Phase 4 set (7 files) | 534 | **637** | +103 | 96 + 7 |
| Bot suite | 2989 | **3103** | +114 | 96 + 7 + 11 |

`tests/test_snapshot_submission.py` is the one changed test file that is
**tracked**, so its inventory is checkable against `HEAD` directly:

```sh
diff <(git show HEAD:tests/test_snapshot_submission.py | grep -o "^def test_[a-z_0-9]*") \
     <(grep -o "^def test_[a-z_0-9]*" tests/test_snapshot_submission.py)
# 14a15,16
# > def test_a_malformed_request_key_keeps_the_documented_refusal
# > def test_a_valid_request_key_still_submits_and_is_stored_verbatim
```

Two added, none removed, none renamed.

---

## Verification

Repository-prescribed interpreters, exported test database URL, suites run
**serially** because the Python suites share one disposable database (finding
F-6).

```sh
export TEST_DATABASE_URL='postgresql+psycopg:///freedom_test'
```

**Focused — the files the correction touches**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/test_p4_commands.py tests/test_p4_ledger_service.py \
  tests/test_snapshot_submission.py
# 416 passed in 0.46s
```

Individually, as the prompt asks for the narrow files owning the other callers
and ledger replay to be named with their exact results:

| File | Result | What it owns here |
|---|---|---|
| `tests/test_p4_commands.py` | **217 passed in 0.13s** | `validate_key`, `IdempotencyRecord`, `CommandEnvelope`, `CommandReceipt` construction and `from_payload` |
| `tests/test_p4_ledger_service.py` | **123 passed in 0.13s** | ledger replay through `LedgerCommandService` |
| `tests/test_snapshot_submission.py` | **76 passed in 0.27s** | the Foundry submission `validate_key` consumer |

**Focused — every Phase 4 test file**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q \
  tests/test_p4_domain_quantities.py tests/test_p4_commands.py \
  tests/test_p4_ledger_domain.py tests/test_p4_ledger_service.py \
  tests/test_p4_idempotent_execution.py tests/test_p4_characterization.py \
  tests/test_p4_domain_isolation.py
# 637 passed, 1 warning in 4.80s
```

**Full suites, against the R3 tree**

```sh
/opt/discord-bots/venv/bin/python -m pytest -q -rs tests/test_*.py
# 3103 passed, 1 warning in 143.40s (0:02:23)

/opt/discord-bots/venv-web/bin/python -m pytest -q -rs tests/web
# 2824 passed, 80 skipped, 1137 warnings in 137.09s (0:02:17)

node --test "foundry-module/tests/"*.test.mjs
# tests 171 · suites 0 · pass 171 · fail 0 · cancelled 0 · skipped 0 · todo 0
```

**Skips.** The bot suite reported **zero** skips. The web skip count is
**exactly 80**, as required, and `-rs` accounts for every one:

```
SKIPPED [54] tests/web/test_p3_2_matrix.py:155: permitted cells are asserted by the per-route success cases
SKIPPED [26] tests/web/test_p3_3_matrix.py:198: permitted cells are asserted by the per-route success cases
```

Both are the expected permission-matrix cell skips with their documented
reasons. **Neither is a database skip**, so `TEST_DATABASE_URL` was genuinely in
effect and the failure mode `.agents/AGENTS.md` warns about — roughly 1141
passed / 1362 skipped, exit 0 — did not occur.

**Warnings.** The bot suite's single warning is the pre-existing `audioop`
`DeprecationWarning` from the installed `discord.py` under Python 3.12,
unrelated to this correction. The web suite's 1137 warnings are the established
pre-existing figure, unchanged from R2.

**Every figure above was produced against the R3 tree in this session.** The R2
figures (bot 2989, web 2824/80, Foundry 171) are quoted only as the arithmetic
baseline above and are not reused as R3 evidence.

**Compile and whitespace**

```sh
/opt/discord-bots/venv/bin/python -m compileall -q \
  application/idempotency.py application/commands.py      # exit 0
/opt/discord-bots/venv-web/bin/python -m compileall -q \
  application/idempotency.py application/commands.py      # exit 0
git diff --check                                           # exit 0, clean
```

`git diff --check` inspects only tracked files, and two of the five changed
files (`application/commands.py`, `tests/test_p4_commands.py`,
`tests/test_p4_ledger_service.py` — three, in fact) are **untracked** because
Phase 4's work is uncommitted. All five were therefore checked directly:
`grep -cP '[ \t]+$'` reported **0** trailing-whitespace lines and `grep -cP '\t'`
reported **0** tab characters in each.

---

## Checks not run, and why

| Check | Status |
|---|---|
| Formatter | **Not configured** in this repository. Not run, not claimed, and not introduced by this correction. |
| Linter | **Not configured.** Same. |
| Type checker | **Not configured.** Same. |
| Migration consistency / Alembic | **Not applicable.** No migration exists in or is touched by this correction; OD-48 is unchanged. |
| Database or integration behaviour beyond the suites above | Not separately exercised. Both defects are in pure in-memory validation with no persistence path of their own; `tests/test_p4_idempotent_execution.py` (real PostgreSQL) ran in full inside the focused Phase 4 set and the bot suite and is green. |
| A new PostgreSQL-level replay regression | **Not added, deliberately.** The prompt asks for an *application-service* regression and for the smallest existing owners. The existing PostgreSQL analogue `test_a_corrupted_stored_receipt_fails_closed_without_re_executing` covers the same refusal against the real stored row with a string command and still passes. Codex may reasonably ask for the malformed-type form against PostgreSQL as well; it was not added on my own authority. |
| Deployment, staging or production verification | **Not run and not authorized.** No staging environment exists. |
| Falsification mutations | **Not requested by this prompt** and not performed. The regression-first evidence above — 88 tests failing on the unchanged tree with their verbatim errors, and passing after — is the equivalent evidence for a correction of this size. |

---

## Diff review

- **Scope / unrelated changes.** `git status --short` held **52** entries before
  this session and holds **53** after the code change; the single new entry is
  `tests/test_snapshot_submission.py`, which was previously unmodified. It
  becomes 54 with this handback, which is this document and nothing else. Every
  other maintainer-owned and agent-owned uncommitted change is untouched:
  nothing was reset, reverted, reformatted or rewritten, and no adjacent cleanup
  was performed. `sha256sum -c` against checksums taken before the first edit
  reports a mismatch for exactly the five intended files and nothing else.
- **Controlled documents.** `.agents/AGENTS.md`, `docs/implementation-plan.md`,
  `docs/discovery/`, `docs/project-management/` and
  `docs/review/Handover information` were **read only**. Their mtimes all
  predate this session's first edit (23:12:53 UTC); the handover's is
  `2026-08-31 22:52:16` and its SHA-256 is
  `21aeb18e7eeb870a546f65b7fc5a1e5f65056bbfdab54fc85cf12034cf39d18b`. No status,
  change-log, RAID, decision or roadmap document was updated, as the prompt
  requires.
- **Secrets.** None added. Both changed production files and all three changed
  test files were grepped for token, secret, password, credential, API-key,
  connection-string, `DISCORD_` and `OAUTH` patterns; the only matches are the
  pre-existing `discord_user_id` **field name** and `TEST_DATABASE_URL` in
  commands quoted in documentation. No credential, database URL or
  service-account material appears.
- **Real data.** None. Every value is synthetic. `"interaction-1"`,
  `"ledger.post_transaction"`, `"foundry-module:test-key"` and
  `COUNCIL_USER = 4200000000000000001` are the files' pre-existing synthetic
  fixtures; the new malformed values are type fixtures, not identities.
- **Unsafe logging.** None. Neither change logs anything. Both new refusal
  messages name only `type(value).__name__` and never the offending value, so a
  caller-supplied idempotency key — which may be attacker-controlled — and a
  malformed stored receipt row cannot reach a log line, an append-only audit row
  or a user-facing reply. Tests assert this directly in both directions.
- **Authorization, resolution and persistence.** Unchanged. No hashing, digest
  schema, key storage, idempotency scope, database schema, ledger behaviour,
  authorization, audit, migration, dependency, framework, adapter, route or
  command was touched. `canonical_request_hash`, `request_hash`,
  `request_key_digest`, `LedgerPrincipalPort`, `validate_principal_id`,
  `LedgerScope`, the authorization ports, audit attribution and the receipt
  payload schema are all untouched.
- **Behavioural surface.** The only externally visible changes are that inputs
  which previously raised `AttributeError` or `TypeError` now raise the
  documented typed refusal, and that `bytes` is now refused instead of accepted
  at both boundaries. **No previously accepted valid input is refused**, and no
  refusal code, message or vocabulary was added or altered for any input that
  was already refused.

---

## Confirmations

- **No Package 5 work.** No Package 5.0 plan, schema, brief, finding, decision,
  risk or readiness state was created, read into, or updated. Package 5.0
  remains `not ready`; P5.0-SR1, P5.0-SR2, P5.0-R5 and OD-62 through OD-66 are
  unchanged, and implementation, migration `0014`, deployment, cutover and
  Package 5.1+ remain unauthorized.
- **No external-state mutation.** No host account, group, file, permission,
  service, timer, database, credential or `git` write occurred. Nothing outside
  this repository working tree was touched. No commit, branch or tag was created.
- **No Discord, Sheets, Foundry or production database contact.** The new tests
  are in-process constructor, service and fake-store tests over synthetic values;
  the suites run against the disposable `freedom_test` database only.
- **No migration** was added, edited or applied.
- **The Freedom bot's production behaviour is unchanged.** No cog, command,
  model, helper or Sheets connector was touched; `/info` is untouched.
- **R1 and R2 are preserved.** P4-PG1, P4-PG2 and P4-PG3 corrections and tests
  are unchanged and passing; no adjustment to any of them was necessary.
- **The Phase 4 acceptance decision is unchanged.** P4-PG4 and P4-PG5 are not
  closed here, and nothing in this correction releases Package 5.

---

## Residual and unexpected findings

Reported rather than absorbed, in line with the prompt's instruction to report
any further concrete defect separately. **None was fixed.**

### 1. `IdempotencyRecord.scope` — the same class, explicitly out of scope

The prompt names this and forbids broadening into it. It is reported concretely
rather than by inspection; probed read-only against the **corrected** tree:

```
scope=123        -> AttributeError: 'int' object has no attribute 'strip'
scope=None       -> AttributeError: 'NoneType' object has no attribute 'strip'
scope=b'ledger'  -> ACCEPTED
```

Both halves of the class, unchanged. Its practical reach is narrower than the
key's: `scope` is a module-level constant at every production call site
(`LEDGER_SCOPE`, `SUBMISSION_SCOPE`), never caller-supplied — which is presumably
why the prompt excludes it. Codex's disposition.

### 2. `SnapshotImportRecord.request_key` — independently implemented, out of scope

`application/snapshots.py:176` opens `if not self.request_key.strip():` with the
same shape, raising plain `ValueError`. It does **not** go through
`validate_key`, so this correction does not reach it and the prompt forbids
broadening into it. It is a Phase 2/3-owned path with its own accepted evidence.
Codex's disposition.

### 3. The wider `.strip()`-before-type inventory in `application/`

For completeness rather than as a claim: `rg '\.strip\(\)' application/` shows
the same textual shape at, among others, `application/audit.py:163-167`
(`AuditEvent.action`, `entity_type`, `entity_id`), `application/authorization.py:103`,
`application/imports.py:75`, and `application/snapshots.py:232-249`. **I did not
probe these and make no claim about any of them** — several may be unreachable
with a non-string, and each belongs to an accepted phase with its own evidence.
They are named so that Codex can decide whether the class warrants a separate
review item, not asserted as defects.

### 4. `request_key_digest()` coerces before the validator runs — context, not a defect

`application/foundry/submission.py:463` computes
`request_key_digest(request_key)` **before** `_submit()` calls `validate_key`,
and that function f-string-interpolates the key. A malformed key's `str()`
therefore reaches a SHA-256 input on the refusal path. I judge this **not** a
defect and did not change it: the digest is one-way, the key text is never
stored, the refusal still happens, and the behaviour is identical for the blank,
overlong and control-character keys the boundary has always refused. Recorded so
that the reviewer sees it was looked at rather than missed.

### 5. Where the defect class now stands in the two corrected modules

| Value | Boundary | State |
|---|---|---|
| `CommandCaller.discord_user_id` | envelope | corrected (P4-PG1, R1) |
| `ExpectedVersion.aggregate_type` | envelope | corrected (P4-PG2, R1) |
| `CommandCaller.principal_id` | envelope | corrected (P4-PG3, R2) |
| `CommandEnvelope.idempotency_key` / `validate_key()` | shared validator | **corrected here (P4-PG4)** |
| `CommandReceipt.command` | receipt / replay | **corrected here (P4-PG5)** |
| `IdempotencyRecord.scope` | idempotency record | open, out of scope — item 1 above |

That is the whole of the class in `application/commands.py` and
`application/idempotency.py`. Every other value in both modules is
`isinstance`-first.

### 6. Context, not a finding: current reach

No adapter is yet wired to `CommandEnvelope`, `CommandReceipt` or
`LedgerCommandService`; they are constructed only by Phase 4's own tests and
services. **The Foundry submission boundary is the exception** — `validate_key`
has a live production consumer there — so P4-PG4 was, unlike P4-PG1…PG3, not
purely latent. That is a statement about today's reach, not an argument about
severity; Package 5.0 wires the first real adapter to the command envelope,
which is exactly when a latent boundary defect stops being latent.

Nothing in this work suggested a materially broader defect in the Phase 4
ledger, authorization, idempotency, concurrency or audit **mechanisms**. P4-PG4
and P4-PG5 are input-validation escapes at their boundaries, not faults in the
durable idempotency or attribution design.

---

## Request for independent re-review

Codex is asked to independently re-review **P4-PG4** and **P4-PG5** against this
tree and to supply the disposition. Suggested focus:

1. that `validate_key()` establishes `str` before every value rule and refuses
   every non-`str` through the pre-existing `invalid_request_key` code —
   **without** `str(...)` coercion, `bytes` decoding, normalization or
   truncation — and that the blank, maximum-length and control-character rules
   and their messages are unchanged;
2. that all **three** production callers are correct and covered, and that the
   caller inventory above — including the correction of R2's false
   `SnapshotImportRecord` statement — is accurate;
3. that `CommandReceipt` raises `ValueError` at the source rather than
   `from_payload()` widening its catch list, and that `from_payload()` itself,
   the receipt payload schema and the accepted command names are unchanged;
4. that the ledger replay regression proves what it claims — the existing
   `original_result_unavailable`, no second posting, no new audit effect, the
   stored receipt neither replaced nor invented — for the bytes case as well as
   the exception cases;
5. that the regressions genuinely fail on the pre-fix tree rather than being
   assertions written around the new code; the exact commands, counts and
   verbatim errors are recorded above;
6. that P4-PG1, P4-PG2 and P4-PG3 corrections and tests are byte-unchanged and
   still passing, and that the test arithmetic (121 → 217, 116 → 123, 65 → 76,
   2989 → 3103) accounts for every added case with nothing removed; and
7. the residuals above — in particular whether `IdempotencyRecord.scope`, the
   independently implemented `SnapshotImportRecord.request_key`, and the wider
   unprobed `.strip()` inventory warrant their own bounded item, and whether the
   PostgreSQL-level form of the replay regression should be added.

**Neither finding is closed by this document.** If both are accepted with no
further Blocking or Important Phase 4 finding, the maintainer's requested Phase 4
cleanup is complete and work returns to Package 5.0 readiness and security work
at exactly its existing `not ready` state.
