"""The audit event's stated contract: what it records cannot change afterwards.

`AuditEvent` promises that a caller keeping its own reference to the payload
cannot alter what the audit says. Freezing only the outer mapping does not
deliver that for any payload this platform actually writes — the importer's
change record is `{"changes": {field: {"from": ..., "to": ...}}}`, two levels
deep — so the freeze is recursive and these tests are what hold it there.
"""
from __future__ import annotations

import json
from uuid import uuid4

import pytest

from application.audit import (
    ActorCapability,
    AuditEvent,
    AuditSource,
    UnsupportedAuditPayloadError,
)


def event(payload) -> AuditEvent:
    return AuditEvent(
        action="sheet_import.character.updated",
        entity_type="character",
        entity_id=str(uuid4()),
        source=AuditSource.IMPORT,
        actor_capability=ActorCapability.SYSTEM,
        correlation_id=uuid4(),
        payload=payload,
    )


def test_the_outer_payload_cannot_be_replaced_or_extended():
    recorded = event({"row_index": 3})

    with pytest.raises(TypeError):
        recorded.payload["row_index"] = 4  # type: ignore[index]


def test_a_nested_mapping_cannot_be_mutated_through_the_event():
    recorded = event({"changes": {"level": {"from": 4, "to": 5}}})

    with pytest.raises(TypeError):
        recorded.payload["changes"]["level"]["to"] = 20  # type: ignore[index]
    with pytest.raises(AttributeError):
        recorded.payload["changes"]["level"].clear()  # type: ignore[attr-defined]
    assert recorded.payload["changes"]["level"]["to"] == 5


def test_mutating_the_callers_dictionary_afterwards_does_not_change_the_record():
    changes = {"level": {"from": 4, "to": 5}}
    recorded = event({"changes": changes})

    changes["level"]["to"] = 20
    changes["display_name"] = {"from": "a", "to": "b"}

    assert recorded.payload["changes"]["level"]["to"] == 5
    assert "display_name" not in recorded.payload["changes"]


def test_a_nested_list_becomes_an_immutable_sequence():
    recorded = event({"rows": [3, 4, 5]})

    assert recorded.payload["rows"] == (3, 4, 5)
    with pytest.raises(AttributeError):
        recorded.payload["rows"].append(6)  # type: ignore[attr-defined]


def test_a_list_of_mappings_is_frozen_all_the_way_down():
    recorded = event({"rows": [{"row_index": 3, "name": "Test Smith A"}]})

    with pytest.raises(TypeError):
        recorded.payload["rows"][0]["name"] = "Test Smith B"  # type: ignore[index]


def test_a_value_an_audit_row_cannot_record_is_refused_at_construction():
    """Fail at the call site, not at the driver, and never by silent coercion."""
    with pytest.raises(UnsupportedAuditPayloadError):
        event({"rows": {3, 4}})
    with pytest.raises(UnsupportedAuditPayloadError):
        event({"blob": b"bytes"})
    with pytest.raises(UnsupportedAuditPayloadError):
        event({"when": object()})


def test_non_string_keys_are_refused_because_json_objects_have_none():
    with pytest.raises(UnsupportedAuditPayloadError):
        event({"rows": {3: "Test Smith A"}})


def test_the_payload_still_serializes_to_the_json_the_database_stores():
    recorded = event(
        {
            "sheet_tab": "Characters",
            "row_index": 3,
            "changes": {"level": {"from": None, "to": 5}, "active": {"from": True, "to": False}},
            "rows": [1, 2],
        }
    )

    serialized = json.dumps(recorded.json_payload())

    assert json.loads(serialized) == {
        "sheet_tab": "Characters",
        "row_index": 3,
        "changes": {
            "level": {"from": None, "to": 5},
            "active": {"from": True, "to": False},
        },
        # A frozen sequence round-trips as the JSON array it came from.
        "rows": [1, 2],
    }


def test_the_json_payload_is_a_copy_that_cannot_write_back_into_the_event():
    recorded = event({"changes": {"level": {"from": 4, "to": 5}}})

    plain = recorded.json_payload()
    plain["changes"]["level"]["to"] = 20

    assert recorded.payload["changes"]["level"]["to"] == 5


# --------------------------------------------------------------------------- #
# Non-finite numbers
#
# `NaN`, `inf` and `-inf` are Python floats, and `json.dumps` emits them happily
# as the bare tokens `NaN`, `Infinity` and `-Infinity`. None of the three is
# valid JSON, and PostgreSQL refuses each with `invalid input syntax for type
# json` when the driver hands it to a JSONB column — which fails not just the
# audit row but the whole transaction, and therefore the mutation the audit row
# was recording. They are refused where the payload is built instead.
# --------------------------------------------------------------------------- #

NON_FINITE = (float("nan"), float("inf"), float("-inf"))


@pytest.mark.parametrize("value", NON_FINITE)
def test_a_non_finite_number_is_refused_at_construction(value):
    with pytest.raises(UnsupportedAuditPayloadError) as refusal:
        event({"balance": value})

    assert "payload.balance" in str(refusal.value)


@pytest.mark.parametrize("value", NON_FINITE)
def test_a_non_finite_number_nested_in_a_mapping_is_refused(value):
    """The payload this platform writes is nested, so the check must be too."""
    with pytest.raises(UnsupportedAuditPayloadError) as refusal:
        event({"changes": {"balance": {"from": 10.5, "to": value}}})

    assert "payload.changes.balance.to" in str(refusal.value)


@pytest.mark.parametrize("value", NON_FINITE)
def test_a_non_finite_number_nested_in_a_sequence_is_refused(value):
    with pytest.raises(UnsupportedAuditPayloadError) as refusal:
        event({"amounts": [1.5, 2.5, value]})

    assert "payload.amounts[2]" in str(refusal.value)


@pytest.mark.parametrize("value", NON_FINITE)
def test_a_non_finite_number_inside_a_sequence_of_mappings_is_refused(value):
    with pytest.raises(UnsupportedAuditPayloadError) as refusal:
        event({"rows": [{"row_index": 3, "rate": value}]})

    assert "payload.rows[0].rate" in str(refusal.value)


def test_the_refusal_names_the_path_and_no_player_state():
    """A safe message: where the value is, not what the record contains."""
    with pytest.raises(UnsupportedAuditPayloadError) as refusal:
        event({"changes": {"gold": {"from": 12345, "to": float("nan")}}})

    message = str(refusal.value)
    assert "payload.changes.gold.to" in message
    assert "12345" not in message


def test_finite_numbers_and_every_other_supported_value_still_pass():
    """The check must reject only the three values that cannot be stored."""
    recorded = event(
        {
            "zero": 0.0,
            "negative_zero": -0.0,
            "fraction": 0.125,
            "large": 1e308,
            "small": 5e-324,
            "integer": 42,
            "negative": -7,
            "true": True,
            "false": False,
            "null": None,
            "text": "Test Smith A",
            "nested": {"amounts": [1.5, -2.5, 0.0], "count": 3},
        }
    )

    assert recorded.payload["fraction"] == 0.125
    assert recorded.payload["nested"]["amounts"] == (1.5, -2.5, 0.0)
    # And it is still the JSON the database stores.
    assert json.loads(json.dumps(recorded.json_payload()))["large"] == 1e308
