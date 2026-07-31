from __future__ import annotations

import csv
from pathlib import Path

from adapters.sheets.character_import import parse_character_rows
from application.imports import ImportIssueSeverity

FIXTURE = Path(__file__).parent / "fixtures" / "sheet_characters_sample.csv"


def fixture_rows() -> list[dict[str, str]]:
    with FIXTURE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return rows[1:]  # Sheet row 2 is the documented second header row.


def test_valid_identity_is_returned_as_a_typed_dry_run_candidate():
    report = parse_character_rows(
        [
            {
                "Character Name (short)": "Test Smith A",
                "Character Name (long)": "Test Smith Alpha",
                "Player Name": "testplayer01",
                "Character Level": "4",
                "Active": "1",
            }
        ]
    )

    assert not report.has_errors
    assert report.warning_count == 0
    candidate = report.candidates[0]
    assert candidate.row_number == 3
    assert candidate.display_name == "Test Smith A"
    assert candidate.long_name == "Test Smith Alpha"
    assert candidate.player_name == "testplayer01"
    assert candidate.level == 4
    assert candidate.active is True


def test_missing_player_is_a_reported_reconciliation_warning_not_an_owner_guess():
    report = parse_character_rows(
        [
            {
                "Character Name (short)": "Test Orphan A",
                "Character Level": "",
                "Active": "0",
            }
        ]
    )

    assert not report.has_errors
    assert report.warning_count == 1
    assert report.candidates[0].player_name is None
    assert report.issues[0].code == "owner_unresolved"
    assert report.issues[0].severity is ImportIssueSeverity.WARNING


def test_malformed_values_are_reported_by_sheet_row_and_field_without_coercion():
    report = parse_character_rows(
        [
            {
                "Character Name (short)": "Test Broken A",
                "Player Name": "testplayer01",
                "Character Level": "not-a-level",
                "Active": "maybe",
            }
        ],
        first_row_number=27,
    )

    assert report.has_errors
    assert report.error_count == 2
    assert report.candidates == ()
    assert {(issue.row_number, issue.field, issue.code) for issue in report.issues} == {
        (27, "Character Level", "invalid_integer"),
        (27, "Active", "invalid_boolean"),
    }


def test_case_insensitive_duplicates_are_reported_instead_of_first_match_wins():
    report = parse_character_rows(
        [
            {
                "Character Name (short)": "Test Smith A",
                "Player Name": "testplayer01",
                "Character Level": "4",
                "Active": "1",
            },
            {
                "Character Name (short)": "test smith a",
                "Player Name": "testplayer02",
                "Character Level": "4",
                "Active": "1",
            },
        ]
    )

    assert report.has_errors
    assert [candidate.row_number for candidate in report.candidates] == [3]
    duplicate = next(issue for issue in report.issues if issue.code == "duplicate")
    assert duplicate.row_number == 4
    assert "row 3" in duplicate.message


def test_verified_synthetic_fixture_produces_candidates_and_expected_anomalies():
    report = parse_character_rows(fixture_rows())

    names = {candidate.display_name for candidate in report.candidates}
    assert "Test Alchemist B" in names
    assert "Test Malformed Q" not in names
    # This slice validates identity fields only. Financial anomalies remain
    # candidates and will be rejected by the game-state import validator.
    assert "Test Negative R" in names
    assert "Test Duplicate P" in names
    assert "test smith a" not in names
    assert {issue.code for issue in report.issues} >= {
        "duplicate",
        "invalid_integer",
        "invalid_boolean",
    }
