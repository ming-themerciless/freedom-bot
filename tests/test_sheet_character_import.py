from __future__ import annotations

import csv
from pathlib import Path

import pytest

from adapters.sheets.character_import import (
    IDENTITY_COLUMNS,
    SheetLayoutError,
    parse_character_rows,
    rows_from_values,
)
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


def fixture_headers() -> list[str]:
    with FIXTURE.open(newline="", encoding="utf-8") as handle:
        return next(csv.reader(handle))


def values_from_fixture(*data_rows: list[str]) -> list[list[str]]:
    """A raw `get_values` shape: header row, second header row, then data."""
    headers = fixture_headers()
    return [headers, [""] * len(headers), *data_rows]


def data_row(**fields: str) -> list[str]:
    headers = fixture_headers()
    row = [""] * len(headers)
    for name, value in fields.items():
        row[headers.index(name)] = value
    return row


def test_raw_values_become_header_keyed_rows():
    values = values_from_fixture(
        data_row(**{"Character Name (short)": "Test Smith A", "Character Level": "4", "Active": "1"})
    )

    rows = rows_from_values(values)

    assert len(rows) == 1
    assert rows[0]["Character Name (short)"] == "Test Smith A"
    assert rows[0]["Character Level"] == "4"


def test_a_short_row_is_padded_rather_than_treated_as_malformed():
    """Google omits trailing empty cells, so a valid row can arrive short."""
    values = values_from_fixture(["Test Smith A"])

    report = parse_character_rows(rows_from_values(values))

    assert report.has_errors  # Active is blank, which is still not a boolean
    assert {issue.field for issue in report.issues} == {"Active", "Player Name"}


def test_a_blank_spacer_row_is_skipped_without_shifting_the_rows_below_it():
    values = values_from_fixture(
        data_row(**{"Character Name (short)": "Test Smith A", "Character Level": "4", "Active": "1", "Player Name": "testplayer01"}),
        [],
        data_row(**{"Character Name (short)": "Test Smith B", "Character Level": "5", "Active": "1", "Player Name": "testplayer02"}),
    )

    report = parse_character_rows(rows_from_values(values))

    assert not report.has_errors
    # Row 4 was blank and produced nothing, and row 5 kept its own number.
    assert [(c.row_number, c.display_name) for c in report.candidates] == [
        (3, "Test Smith A"),
        (5, "Test Smith B"),
    ]


def test_an_unexpected_column_layout_refuses_to_import_anything():
    headers = fixture_headers()
    headers.insert(1, "Newly Inserted Column")

    with pytest.raises(SheetLayoutError, match="Character Name \\(long\\)"):
        rows_from_values([headers, [""] * len(headers), ["Test Smith A"]])


def test_an_empty_read_is_refused_rather_than_reported_as_no_characters():
    with pytest.raises(SheetLayoutError):
        rows_from_values([])


def test_the_identity_columns_match_the_verified_fixture_headers():
    headers = fixture_headers()

    for name, column in IDENTITY_COLUMNS.items():
        index = 0
        for character in column:
            index = index * 26 + (ord(character) - ord("A") + 1)
        assert headers[index - 1] == name
