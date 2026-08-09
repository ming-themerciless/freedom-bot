"""Regression controls for the lost-pin operational reconciliation."""

from pathlib import Path


GUIDE = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "operations"
    / "foundry-snapshot-submission.md"
)


def _lost_pin_procedure() -> str:
    text = GUIDE.read_text(encoding="utf-8")
    return text.split(
        "#### Lost-pin reconciliation after an accidental reload", maxsplit=1
    )[1].split("Downloading is a fallback delivery channel", maxsplit=1)[0]


def test_lost_pin_reconciliation_spans_the_whole_unresolved_episode():
    """Same-key retries are silent, so the window includes the first attempt."""
    procedure = _lost_pin_procedure()
    normalized = " ".join(procedure.split())

    assert "FROM audit_events AS a" in procedure
    assert "JOIN foundry_snapshots AS s ON s.checksum = a.entity_id" in procedure
    assert "a.action = 'snapshot_submission.accepted'" in procedure
    assert "a.payload->>'world_id' = 'the-guild'" in procedure
    assert "a.occurred_at >=" in procedure
    assert "a.occurred_at <=" in procedure
    assert "s.received_at >=" not in procedure
    assert "s.received_at <=" not in procedure
    assert "a.payload->>'duplicate' AS duplicate" in procedure
    assert "whole unresolved delivery episode" in normalized
    assert "from the first submission" in normalized
    assert "same idempotency key" in normalized
    assert "without writing a new audit event" in normalized
    assert "`duplicate = false`" in normalized


def test_lost_pin_miss_requires_the_duplicate_safe_query_to_be_repeated():
    procedure = _lost_pin_procedure()

    miss_rule = " ".join(
        procedure.split("- No row,", maxsplit=1)[1]
        .split("- More than one row", maxsplit=1)[0]
        .split()
    )
    assert "whole-episode audit-event query has been repeated once" in miss_rule
    assert "accepted pending snapshot during that episode" in miss_rule
    assert "Only then may the operator authorize" in miss_rule
