"""Phase 4 WP-2 — the command envelope, its refusals and its receipts.

The envelope is the boundary every state-changing request crosses, so what it
*refuses* to be built from matters as much as what it carries. These tests pin
both, plus the two properties the durable idempotency path rests on: a receipt
round-trips through its stored payload unchanged, and a receipt that cannot be
read back is never invented.
"""
from __future__ import annotations

import dataclasses
import json
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from application.audit import AuditSource
from application.commands import (
    CommandCaller,
    CommandEnvelope,
    CommandReceipt,
    ExpectedVersion,
    InvalidEnvelopeError,
    StoredReceiptUnreadable,
)
from application.idempotency import (
    KEY_MAX_LENGTH,
    IdempotencyKeyError,
    IdempotencyRecord,
    IdempotencyStatus,
    validate_key,
)

COUNCIL_USER = 4200000000000000001


def caller() -> CommandCaller:
    return CommandCaller(AuditSource.DISCORD, discord_user_id=COUNCIL_USER)


def envelope(**overrides) -> CommandEnvelope:
    fields = {
        "caller": caller(),
        "idempotency_key": "interaction-1",
        "correlation_id": uuid4(),
    }
    fields.update(overrides)
    return CommandEnvelope(**fields)


# --- the caller is an identity, never a privilege -----------------------------


def test_a_caller_names_one_identity():
    person = CommandCaller(AuditSource.WEB, discord_user_id=COUNCIL_USER)
    service = CommandCaller(AuditSource.FOUNDRY, principal_id="foundry-module")

    assert person.is_human is True
    assert service.is_human is False


def test_a_caller_naming_two_identities_is_refused():
    """A request claiming to be two callers is not one this platform records."""
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(
            AuditSource.DISCORD,
            discord_user_id=COUNCIL_USER,
            principal_id="foundry-module",
        )

    assert refusal.value.code == "invalid_caller"


def test_a_caller_naming_no_identity_is_refused():
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.DISCORD)

    assert refusal.value.code == "invalid_caller"


@pytest.mark.parametrize("snowflake", [0, -1, -COUNCIL_USER])
def test_a_caller_requires_a_positive_snowflake(snowflake):
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.DISCORD, discord_user_id=snowflake)

    assert refusal.value.code == "invalid_caller"


# --- P4-PG1 · a Discord identity is an actual positive integer ----------------
#
# Post-gate finding, 2026-08-31. `discord_user_id <= 0` is a comparison, not a
# type check, so it let two malformed identities past the boundary: `True`,
# because `bool` is an `int` subclass, arrived as Discord user 1; and anything
# not orderable against `0` — `"123"`, a `Decimal` — either raised a raw
# `TypeError` out of the constructor or, where the comparison happened to work,
# was accepted as a snowflake it is not. The constructor is the application
# boundary for this value, so it refuses through the typed vocabulary instead.
# Nothing here coerces: a string of digits is a refusal, not an integer.


@pytest.mark.parametrize("snowflake", [1, 42, COUNCIL_USER])
def test_an_actual_positive_snowflake_remains_accepted(snowflake):
    accepted = CommandCaller(AuditSource.DISCORD, discord_user_id=snowflake)

    assert accepted.discord_user_id == snowflake
    assert accepted.is_human is True


@pytest.mark.parametrize("flag", [True, False])
def test_a_boolean_discord_id_is_refused(flag):
    """`isinstance(True, int)` is `True`, so a flag was read as Discord user 1."""
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.DISCORD, discord_user_id=flag)

    assert refusal.value.code == "invalid_caller"


@pytest.mark.parametrize(
    "value",
    [
        "123",
        str(COUNCIL_USER),
        1.0,
        float(COUNCIL_USER),
        Decimal("123"),
        b"123",
        [COUNCIL_USER],
        (COUNCIL_USER,),
    ],
)
def test_a_non_integer_discord_id_is_refused_not_raised_through(value):
    """The refusal is the documented one, never the comparison's own error.

    An adapter branches on `code`. A raw `TypeError` escaping the constructor is
    not a code it can branch on, and a value the comparison happens to accept —
    `1.0`, `Decimal("123")` — is a snowflake this platform never issued.
    """
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.DISCORD, discord_user_id=value)

    assert refusal.value.code == "invalid_caller"


def test_a_numeric_string_discord_id_is_not_silently_coerced():
    """Refused, rather than read as the integer it looks like.

    `.agents/AGENTS.md`: validate at boundaries, do not silently coerce invalid
    data. Accepting `"4200000000000000001"` here would make the identity the
    audit trail attributes a mutation to depend on the adapter's typing.
    """
    with pytest.raises(InvalidEnvelopeError):
        CommandCaller(AuditSource.DISCORD, discord_user_id=str(COUNCIL_USER))


@pytest.mark.parametrize("blank", ["", "   ", "\t"])
def test_a_blank_service_principal_is_refused(blank):
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.FOUNDRY, principal_id=blank)

    assert refusal.value.code == "invalid_caller"


# --- P4-PG3 · a service-principal identity is proved to be text before stripping
#
# Post-gate finding, 2026-08-31. Reported out of the P4-PG1/P4-PG2 correction
# rather than absorbed into it, and corrected here on its own authority. It is
# P4-PG2's mistake one constructor away: `principal_id.strip()` ran before
# anything established that `principal_id` was a string, so
# `CommandCaller(..., principal_id=123)` left this constructor as a raw
# `AttributeError` instead of the documented `invalid_caller`, and
# `b"principal"` — which does have a `.strip()` of its own — was *accepted* as
# an identity that the `str` lookup in `LedgerPrincipalPort.current_principal()`
# can never match.
#
# The type is established first; the existing nonblank rule is unchanged, and
# nothing is coerced with `str(...)` or decoded. This validates the *shape* of
# the identifier and nothing more: whether it resolves, and to what, remains the
# port's answer at execution.


@pytest.mark.parametrize(
    "identifier", ["foundry-module", "import-worker", "bot", " padded "]
)
def test_a_nonblank_string_principal_id_remains_accepted(identifier):
    accepted = CommandCaller(AuditSource.FOUNDRY, principal_id=identifier)

    assert accepted.principal_id == identifier
    assert accepted.is_human is False


def test_an_accepted_principal_id_is_carried_verbatim():
    """Nothing normalises it: the envelope carries exactly what arrived."""
    identifier = "foundry-module"

    accepted = CommandCaller(AuditSource.FOUNDRY, principal_id=identifier)

    assert accepted.principal_id is identifier


@pytest.mark.parametrize("blank", ["", "   ", "\t", "\n"])
def test_a_blank_string_principal_id_remains_refused(blank):
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.FOUNDRY, principal_id=blank)

    assert refusal.value.code == "invalid_caller"


@pytest.mark.parametrize(
    "identifier",
    [
        1,
        0,
        123,
        True,
        False,
        1.0,
        Decimal("1"),
        b"principal",
        ["principal"],
        ("principal",),
        uuid4(),
    ],
)
def test_a_non_string_principal_id_is_refused_not_raised_through(identifier):
    """The refusal is the documented one, never `AttributeError`.

    An adapter branches on `code`. A driver-level `AttributeError` escaping the
    constructor is not a code it can branch on, and this constructor is the
    application boundary for the value.
    """
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.FOUNDRY, principal_id=identifier)

    assert refusal.value.code == "invalid_caller"


def test_a_bytes_principal_id_is_refused_although_it_has_a_strip():
    """The acceptance half of this finding, named on its own.

    `b"principal"` satisfied the old nonblank test because `bytes` has
    `.strip()`. It could never be the `str` identity
    `LedgerPrincipalPort.current_principal()` is handed, so it was an identity
    that resolves to nothing, admitted at construction.
    """
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.FOUNDRY, principal_id=b"principal")

    assert refusal.value.code == "invalid_caller"


@pytest.mark.parametrize("identifier", [b"foundry-module", 123, 1.0, True])
def test_a_malformed_principal_id_is_never_converted_or_decoded(identifier):
    """Refused, rather than read as the text it could be turned into.

    `.agents/AGENTS.md`: validate at boundaries, do not silently coerce invalid
    data. `str(b"foundry-module")` is `"b'foundry-module'"` and
    `b"foundry-module".decode()` is a different identity from the one the
    request carried; either would make the principal an audit row attributes a
    mutation to depend on the adapter's typing. The refusal names the offending
    *type* and never the offending value, so a malformed identity cannot be
    echoed into a log, an audit row or an adapter's reply.
    """
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller(AuditSource.FOUNDRY, principal_id=identifier)

    assert refusal.value.code == "invalid_caller"
    assert str(identifier) not in str(refusal.value)
    assert type(identifier).__name__ in str(refusal.value)


@pytest.mark.parametrize(
    "identifier", ["Foundry-Module", "foundry module", "x" * 200, "prïncipal"]
)
def test_the_envelope_does_not_impose_the_configured_principal_vocabulary(identifier):
    """Shape, not existence — the boundary this correction must not move.

    `application/service_principals.validate_principal_id` is the closed
    vocabulary a *configured* principal satisfies, and
    `LedgerPrincipalPort.current_principal()` decides whether an identifier
    resolves at all. Enforcing either here would answer an authorization
    question inside the envelope, which is the mistake finding P4-R2 records.
    An unconfigured identifier is refused at execution by the port, not admitted
    as authority.
    """
    accepted = CommandCaller(AuditSource.FOUNDRY, principal_id=identifier)

    assert accepted.principal_id == identifier
    assert accepted.is_human is False


def test_a_caller_names_its_surface_as_an_audit_source():
    """`"discord"` is a string somebody typed; `AuditSource.DISCORD` is a value."""
    with pytest.raises(InvalidEnvelopeError) as refusal:
        CommandCaller("discord", discord_user_id=COUNCIL_USER)

    assert refusal.value.code == "invalid_caller"


def test_the_envelope_carries_no_resolved_privilege():
    """The design decision, asserted rather than left to a docstring.

    `application/authorization.py` rule 2: permission is re-resolved at the
    moment the work is done. An envelope field carrying `guild_council` would
    let a caller present a privilege it held a minute ago — or never held, since
    the envelope is built from the request.
    """
    fields = set(CommandEnvelope.__dataclass_fields__) | set(
        CommandCaller.__dataclass_fields__
    )

    assert not fields & {
        "guild_council",
        "guild_member",
        "platform_administrator",
        "capability",
        "authorized",
    }


# --- the idempotency key ------------------------------------------------------


@pytest.mark.parametrize("blank", ["", "   ", "\n"])
def test_a_blank_idempotency_key_is_refused(blank):
    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope(idempotency_key=blank)

    assert refusal.value.code == "invalid_request_key"


def test_an_over_long_idempotency_key_is_refused():
    """Refused where it can be explained, rather than truncated by the column."""
    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope(idempotency_key="k" * (KEY_MAX_LENGTH + 1))

    assert refusal.value.code == "invalid_request_key"


def test_a_key_at_the_column_limit_is_accepted():
    assert envelope(idempotency_key="k" * KEY_MAX_LENGTH)


@pytest.mark.parametrize("key", ["with\nnewline", "with\x00null", "bell\x07"])
def test_a_control_character_in_a_key_is_refused(key):
    """It is recorded verbatim in append-only history and must stay renderable."""
    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope(idempotency_key=key)

    assert refusal.value.code == "invalid_request_key"


def test_the_key_refusal_keeps_the_published_idempotency_code():
    """One exception type for an adapter to translate; the code is unchanged.

    `application/idempotency.py` already publishes `invalid_request_key`, and an
    adapter that branches on it must not have to know whether the refusal came
    from the envelope or from the key validator.
    """
    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope(idempotency_key="")

    assert refusal.value.code == "invalid_request_key"
    assert isinstance(refusal.value, ValueError)


# --- P4-PG4 · an idempotency key is proved to be text before it is stripped ---
#
# `validate_key()` opened `if not key.strip():` before anything established that
# `key` was text, so every non-string left it as a raw `AttributeError` or
# `TypeError`. `CommandEnvelope.__post_init__` catches only `IdempotencyKeyError`,
# so its documented `InvalidEnvelopeError(code="invalid_request_key")` contract
# was bypassed at the one value that makes a retry recognisable as a retry.
#
# The validator is shared. Its three production callers are `CommandEnvelope`
# (below), `IdempotencyRecord` (below) and the Foundry submission boundary
# (`tests/test_snapshot_submission.py`), and each is covered where it lives.

#: The malformed shapes the finding names. Synthetic, and deliberately including
#: `bytes` — which has a `.strip()` of its own and therefore passed the blank
#: rule — and `None`, which is the shape an absent stored column arrives as.
MALFORMED_KEYS = [
    1,
    0,
    123,
    True,
    False,
    1.0,
    Decimal("1"),
    None,
    b"interaction-1",
    ["interaction-1"],
    ("interaction-1",),
    uuid4(),
]


@pytest.mark.parametrize("key", ["interaction-1", "k", " padded ", "k" * KEY_MAX_LENGTH])
def test_a_valid_key_is_accepted_and_returned_verbatim(key):
    """Nothing is normalized: the value returned is the value supplied."""
    assert validate_key(key) is key


@pytest.mark.parametrize("blank", ["", "   ", "\t", "\n"])
def test_a_blank_key_keeps_its_published_refusal(blank):
    with pytest.raises(IdempotencyKeyError) as refusal:
        validate_key(blank)

    assert refusal.value.code == "invalid_request_key"


def test_an_over_long_key_keeps_its_published_refusal():
    with pytest.raises(IdempotencyKeyError) as refusal:
        validate_key("k" * (KEY_MAX_LENGTH + 1))

    assert refusal.value.code == "invalid_request_key"


@pytest.mark.parametrize("key", ["with\nnewline", "with\x00null", "bell\x07", "\x7f"])
def test_a_control_character_key_keeps_its_published_refusal(key):
    with pytest.raises(IdempotencyKeyError) as refusal:
        validate_key(key)

    assert refusal.value.code == "invalid_request_key"


@pytest.mark.parametrize("key", MALFORMED_KEYS)
def test_a_non_string_key_is_refused_not_raised_through(key):
    """The escape half: a driver-level error is not a code an adapter branches on."""
    with pytest.raises(IdempotencyKeyError) as refusal:
        validate_key(key)

    assert refusal.value.code == "invalid_request_key"


def test_a_bytes_key_is_refused_although_it_has_a_strip():
    """The acceptance half.

    `b"interaction-1".strip()` is truthy and `len()` works, so it passed the
    blank and length rules and only failed inside the control-character scan, as
    an unrelated `TypeError`. It can never match the `str` a previous attempt
    stored, so admitting it would spend a fresh key on every retry.
    """
    with pytest.raises(IdempotencyKeyError) as refusal:
        validate_key(b"interaction-1")

    assert refusal.value.code == "invalid_request_key"


@pytest.mark.parametrize("key", [b"interaction-1", 123, 1.0, True])
def test_a_malformed_key_is_never_coerced_or_decoded(key):
    """Refused, never `str(...)`-ed, decoded, normalized or truncated.

    The message names the offending *type* and never the offending value, so a
    caller-supplied key cannot be echoed into a log line, an append-only row or
    an adapter's reply.
    """
    with pytest.raises(IdempotencyKeyError) as refusal:
        validate_key(key)

    message = str(refusal.value)
    assert type(key).__name__ in message
    assert str(key) not in message
    if isinstance(key, bytes):
        assert key.decode() not in message


@pytest.mark.parametrize("key", MALFORMED_KEYS)
def test_a_malformed_key_reaches_the_envelope_as_a_typed_refusal(key):
    """The contract the finding is about: never a raw exception at the boundary."""
    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope(idempotency_key=key)

    assert refusal.value.code == "invalid_request_key"


def test_an_envelope_still_carries_an_accepted_key_verbatim():
    assert envelope(idempotency_key=" padded ").idempotency_key == " padded "


def record(**overrides) -> IdempotencyRecord:
    fields = {
        "scope": "ledger.post_transaction",
        "key": "interaction-1",
        "request_hash": bytes(32),
        "status": IdempotencyStatus.STARTED,
    }
    fields.update(overrides)
    return IdempotencyRecord(**fields)


@pytest.mark.parametrize("key", MALFORMED_KEYS)
def test_an_idempotency_record_refuses_a_malformed_key(key):
    """The second production caller, refusing through the shared validator."""
    with pytest.raises(IdempotencyKeyError) as refusal:
        record(key=key)

    assert refusal.value.code == "invalid_request_key"


@pytest.mark.parametrize("key", ["interaction-1", " padded "])
def test_an_idempotency_record_still_accepts_a_valid_key(key):
    assert record(key=key).key == key


@pytest.mark.parametrize("blank", ["", "   "])
def test_an_idempotency_record_still_refuses_a_blank_key(blank):
    with pytest.raises(IdempotencyKeyError) as refusal:
        record(key=blank)

    assert refusal.value.code == "invalid_request_key"


# --- correlation --------------------------------------------------------------


@pytest.mark.parametrize("value", ["not-a-uuid", 1, None, str(uuid4())])
def test_a_correlation_id_must_be_a_uuid(value):
    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope(correlation_id=value)

    assert refusal.value.code == "invalid_correlation_id"


# --- the expected version -----------------------------------------------------


def test_an_expected_version_names_the_aggregate_it_constrains():
    book = uuid4()
    expected = ExpectedVersion("ledger_book", book, 3)

    assert expected.describes("ledger_book", book) is True
    assert expected.describes("character", book) is False
    assert expected.describes("ledger_book", uuid4()) is False


def test_a_zero_expected_version_is_a_value_not_an_absence():
    """A caller's first posting legitimately expects version 0."""
    assert ExpectedVersion("ledger_book", uuid4(), 0).version == 0


def test_a_negative_expected_version_is_refused():
    with pytest.raises(InvalidEnvelopeError) as refusal:
        ExpectedVersion("ledger_book", uuid4(), -1)

    assert refusal.value.code == "invalid_expected_version"


def test_a_boolean_expected_version_is_refused():
    """`isinstance(True, int)` is `True`, so a flag would be read as version 1."""
    with pytest.raises(InvalidEnvelopeError) as refusal:
        ExpectedVersion("ledger_book", uuid4(), True)

    assert refusal.value.code == "invalid_expected_version"


@pytest.mark.parametrize("version", [1.0, "1", None])
def test_a_non_integer_expected_version_is_refused(version):
    with pytest.raises(InvalidEnvelopeError) as refusal:
        ExpectedVersion("ledger_book", uuid4(), version)

    assert refusal.value.code == "invalid_expected_version"


def test_an_aggregate_is_identified_by_a_uuid():
    with pytest.raises(InvalidEnvelopeError) as refusal:
        ExpectedVersion("ledger_book", "Brightlantern", 0)

    assert refusal.value.code == "invalid_expected_version"


@pytest.mark.parametrize("blank", ["", "   "])
def test_an_expected_version_requires_an_aggregate_type(blank):
    with pytest.raises(InvalidEnvelopeError) as refusal:
        ExpectedVersion(blank, uuid4(), 0)

    assert refusal.value.code == "invalid_expected_version"


# --- P4-PG2 · the aggregate type is proved to be text before it is stripped ---
#
# Post-gate finding, 2026-08-31. `aggregate_type.strip()` ran before anything
# established that `aggregate_type` was a string, so `ExpectedVersion(1, ...)`
# left the constructor as a raw `AttributeError` rather than the documented
# `invalid_expected_version`, and `b"ledger_book"` — which does have `.strip()`
# — was accepted as an aggregate name that can never equal the `str` any
# `describes()` call passes. The type is established first; the existing
# nonblank rule is unchanged, and nothing is coerced with `str(...)`.


@pytest.mark.parametrize("aggregate_type", ["ledger_book", "character", " book "])
def test_a_nonblank_string_aggregate_type_remains_accepted(aggregate_type):
    accepted = ExpectedVersion(aggregate_type, uuid4(), 0)

    assert accepted.aggregate_type == aggregate_type


@pytest.mark.parametrize("blank", ["", "   ", "\t", "\n"])
def test_a_blank_string_aggregate_type_remains_refused(blank):
    with pytest.raises(InvalidEnvelopeError) as refusal:
        ExpectedVersion(blank, uuid4(), 0)

    assert refusal.value.code == "invalid_expected_version"


@pytest.mark.parametrize(
    "aggregate_type",
    [1, 0, True, False, None, 1.0, b"ledger_book", ["ledger_book"], uuid4()],
)
def test_a_non_string_aggregate_type_is_refused_not_raised_through(aggregate_type):
    """The refusal is the documented one, never `AttributeError`.

    A precondition that does not name its aggregate in the same type
    `describes()` compares against is one an executor checks against the wrong
    thing — and the failure mode is a stale write that reported success.
    """
    with pytest.raises(InvalidEnvelopeError) as refusal:
        ExpectedVersion(aggregate_type, uuid4(), 0)

    assert refusal.value.code == "invalid_expected_version"


def test_a_bytes_aggregate_type_could_never_match_the_type_it_names():
    """Why bytes is a refusal and not a near-miss.

    `describes()` is handed a `str` by every caller, so `b"ledger_book"` would
    compare unequal to `"ledger_book"` forever: a precondition that can never be
    satisfied, accepted at construction.
    """
    with pytest.raises(InvalidEnvelopeError) as refusal:
        ExpectedVersion(b"ledger_book", uuid4(), 0)

    assert refusal.value.code == "invalid_expected_version"


def test_a_bare_integer_expected_version_is_refused_on_the_envelope():
    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope(expected_version=3)

    assert refusal.value.code == "invalid_expected_version"


def test_requiring_a_missing_expected_version_refuses_the_command():
    book = uuid4()

    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope().require_expected_version("ledger_book", book)

    assert refusal.value.code == "missing_expected_version"


def test_requiring_a_version_of_a_different_aggregate_refuses_the_command():
    """The failure this catches is a stale write that reported success."""
    other = uuid4()
    request = envelope(expected_version=ExpectedVersion("ledger_book", other, 2))

    with pytest.raises(InvalidEnvelopeError) as refusal:
        request.require_expected_version("ledger_book", uuid4())

    assert refusal.value.code == "invalid_expected_version"


def test_requiring_a_version_of_a_different_aggregate_type_refuses_the_command():
    book = uuid4()
    request = envelope(expected_version=ExpectedVersion("character", book, 2))

    with pytest.raises(InvalidEnvelopeError) as refusal:
        request.require_expected_version("ledger_book", book)

    assert refusal.value.code == "invalid_expected_version"


def test_a_matching_expected_version_is_returned():
    book = uuid4()
    expected = ExpectedVersion("ledger_book", book, 7)

    assert envelope(expected_version=expected).require_expected_version(
        "ledger_book", book
    ) is expected


# --- the envelope itself ------------------------------------------------------


def test_an_envelope_requires_a_command_caller():
    with pytest.raises(InvalidEnvelopeError) as refusal:
        envelope(caller=COUNCIL_USER)

    assert refusal.value.code == "invalid_caller"


def test_an_envelope_is_immutable():
    """A use case cannot be handed one request and act on another."""
    request = envelope()

    with pytest.raises(dataclasses.FrozenInstanceError):
        request.idempotency_key = "something-else"


def test_an_envelope_exposes_no_framework_object():
    """The dependency-direction rule, at this boundary specifically.

    No Discord interaction, no HTTP request, no A1 range, no ORM row, no SQL.
    The envelope's whole field list is checked rather than a sample, so a field
    added later is covered by this test without anyone remembering to extend it.
    """
    request = envelope(expected_version=ExpectedVersion("ledger_book", uuid4(), 0))

    permitted = (CommandCaller, ExpectedVersion, str, UUID, type(None))
    for name in CommandEnvelope.__dataclass_fields__:
        assert isinstance(getattr(request, name), permitted), name


# --- receipts -----------------------------------------------------------------


def receipt(**overrides) -> CommandReceipt:
    fields = {
        "command": "ledger.post_transaction",
        "correlation_id": uuid4(),
        "version": 1,
        "facts": {"transaction_id": str(uuid4()), "entry_count": 2},
    }
    fields.update(overrides)
    return CommandReceipt(**fields)


def test_a_receipt_round_trips_through_its_stored_payload():
    """The property the whole retry path rests on.

    The payload is what goes into `idempotency_keys.response`; a retry is
    answered from it. If the round trip lost or changed a field, a retry would
    quietly return a different answer from the original call.
    """
    original = receipt()

    restored = CommandReceipt.from_payload(original.as_payload(), duplicate=True)

    assert restored.command == original.command
    assert restored.correlation_id == original.correlation_id
    assert restored.version == original.version
    assert restored.facts == original.facts


def test_the_replay_flag_is_not_stored():
    """`duplicate` describes *this call*, not the operation.

    Storing it would make the first caller's own receipt claim to be a replay of
    itself the moment it was read back.
    """
    assert "duplicate" not in receipt().as_payload()


def test_a_replayed_receipt_says_it_is_a_replay():
    restored = CommandReceipt.from_payload(receipt().as_payload(), duplicate=True)

    assert restored.duplicate is True


def test_a_receipt_payload_is_json_serializable():
    payload = receipt().as_payload()

    assert json.loads(json.dumps(payload)) == payload


def test_a_receipt_fact_cannot_hold_a_float():
    """A receipt is the last place a binary float should enter the platform."""
    with pytest.raises(ValueError):
        receipt(facts={"earnings": 12.5})


@pytest.mark.parametrize(
    "value", [{"nested": 1}, [1, 2], uuid4(), b"bytes", (1, 2)]
)
def test_a_receipt_fact_cannot_hold_a_value_that_would_not_round_trip(value):
    with pytest.raises(ValueError):
        receipt(facts={"thing": value})


def test_a_receipt_fact_key_must_be_text():
    with pytest.raises(ValueError):
        receipt(facts={1: "one"})


def test_receipt_facts_are_frozen_against_the_caller():
    """A caller keeping its dictionary cannot alter what the receipt says."""
    facts = {"transaction_id": "a"}
    written = receipt(facts=facts)

    facts["transaction_id"] = "b"

    assert written.facts["transaction_id"] == "a"
    with pytest.raises(TypeError):
        written.facts["transaction_id"] = "c"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"command": "x"},
        {"command": "x", "correlation_id": "not-a-uuid", "version": 1},
        {"command": "x", "correlation_id": str(uuid4())},
        {"command": "x", "correlation_id": str(uuid4()), "version": "one"},
    ],
)
def test_an_unreadable_stored_receipt_is_never_invented(payload):
    """The key is spent, so the effect may have happened.

    Answering with a reconstruction would state facts nothing recorded, and
    re-executing could duplicate an effect. Both are refused; the caller is told
    the result is unavailable.
    """
    with pytest.raises(StoredReceiptUnreadable):
        CommandReceipt.from_payload(payload, duplicate=True)


def test_a_receipt_requires_a_command_name():
    with pytest.raises(ValueError):
        receipt(command="  ")


def test_a_receipt_version_is_a_whole_number():
    with pytest.raises(ValueError):
        receipt(version=True)


# --- P4-PG5 · a receipt's command name is proved to be text before stripping ---
#
# `CommandReceipt.__post_init__` opened `if not self.command.strip():` before
# anything established that `command` was text. Direct construction leaked an
# `AttributeError`, and `bytes` was accepted. The consequence is on the *replay*
# path: `from_payload()` deliberately converts a bad stored row into
# `StoredReceiptUnreadable`, and `AttributeError` is in neither of its caught
# tuples — so a spent key whose stored command is malformed escaped the typed
# refusal entirely, against a key whose effect may already have committed.
#
# The correction is at the source, in the constructor, and it raises `ValueError`
# — the vocabulary this constructor already uses for every other malformed field,
# and the one `from_payload()` already catches. Widening the catch list instead
# would leave direct construction leaking and `bytes` accepted.

#: The malformed shapes the finding names, in the forms a stored row can hold.
MALFORMED_COMMANDS = [
    1,
    0,
    123,
    True,
    False,
    1.0,
    Decimal("1"),
    None,
    b"ledger.post_transaction",
    ["ledger.post_transaction"],
    ("ledger.post_transaction",),
    uuid4(),
]


@pytest.mark.parametrize(
    "command", ["ledger.post_transaction", "x", " ledger.post_transaction "]
)
def test_a_valid_command_name_is_accepted_and_round_trips_unchanged(command):
    """Accepted verbatim, and unchanged by the stored round trip."""
    written = receipt(command=command)

    assert written.command == command
    assert written.as_payload()["command"] == command
    assert (
        CommandReceipt.from_payload(written.as_payload(), duplicate=True).command
        == command
    )


@pytest.mark.parametrize("blank", ["", "   ", "\t", "\n"])
def test_a_blank_command_name_remains_refused(blank):
    with pytest.raises(ValueError):
        receipt(command=blank)


@pytest.mark.parametrize("command", MALFORMED_COMMANDS)
def test_a_non_string_command_name_is_refused_with_a_value_error(command):
    """`ValueError`, never `AttributeError`.

    `AttributeError` is not a `ValueError`, so this test fails on the escaping
    driver-level error as well as on acceptance.
    """
    with pytest.raises(ValueError) as refusal:
        receipt(command=command)

    assert type(refusal.value) is ValueError


def test_a_bytes_command_name_is_refused_although_it_has_a_strip():
    """`b"...".strip()` is truthy, so it satisfied the nonblank rule and was
    accepted as a command name no `str` comparison could ever match."""
    with pytest.raises(ValueError):
        receipt(command=b"ledger.post_transaction")


@pytest.mark.parametrize("command", [b"ledger.post_transaction", 123, 1.0, True])
def test_a_malformed_command_name_is_never_coerced_or_decoded(command):
    with pytest.raises(ValueError) as refusal:
        receipt(command=command)

    message = str(refusal.value)
    assert type(command).__name__ in message
    assert str(command) not in message
    if isinstance(command, bytes):
        assert command.decode() not in message


@pytest.mark.parametrize("command", MALFORMED_COMMANDS)
def test_a_malformed_stored_command_becomes_an_unreadable_receipt(command):
    """The contract the finding is about.

    The key is spent, so the effect may already have committed. An unreadable
    receipt is neither re-executed nor invented; it is the typed
    `StoredReceiptUnreadable` its caller converts to `original_result_unavailable`.
    """
    payload = {
        "command": command,
        "correlation_id": str(uuid4()),
        "version": 1,
        "facts": {},
    }

    with pytest.raises(StoredReceiptUnreadable):
        CommandReceipt.from_payload(payload, duplicate=True)


def test_a_stored_bytes_command_is_neither_accepted_nor_decoded():
    payload = {
        "command": b"ledger.post_transaction",
        "correlation_id": str(uuid4()),
        "version": 1,
        "facts": {},
    }

    with pytest.raises(StoredReceiptUnreadable) as refusal:
        CommandReceipt.from_payload(payload, duplicate=True)

    assert "ledger.post_transaction" not in str(refusal.value)
