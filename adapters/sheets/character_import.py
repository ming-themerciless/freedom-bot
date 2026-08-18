from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from application.imports import (
    ImportIssue,
    ImportIssueSeverity,
    SheetCharacterCandidate,
    SheetCharacterImportReport,
)
from adapters.sheets.columns import col_to_index
from domain.names import DisplayName

#: The identity columns this importer reads, at the positions
#: `docs/discovery/sheet-inventory.md` §3 records. The position is checked as
#: well as the name: an inserted column would otherwise move every field
#: silently, and the importer would write one character's data onto another.
IDENTITY_COLUMNS = {
    "Character Name (short)": "A",
    "Character Name (long)": "B",
    "Player Name": "C",
    "Character Level": "F",
    "Active": "AL",
}

#: Rows 1 and 2 of the Characters tab are both headers; data starts at row 3.
FIRST_DATA_ROW = 3


class SheetLayoutError(ValueError):
    """The Sheet is not shaped the way the importer was written to read."""


def rows_from_values(
    values: Sequence[Sequence[object]], *, first_data_row: int = FIRST_DATA_ROW
) -> list[dict[str, str]]:
    """Turn a raw `Characters!A1:AL…` read into header-keyed rows.

    The returned list is positional: index 0 is `first_data_row`, and a blank
    row keeps its place rather than being dropped, because a row's position is
    its import key. Short rows — Google omits trailing empty cells — are padded
    rather than treated as malformed.
    """
    if not values:
        raise SheetLayoutError("The Characters range returned no rows at all.")

    headers = [str(header).strip() for header in values[0]]
    for name, column in IDENTITY_COLUMNS.items():
        index = col_to_index(column)
        if index >= len(headers) or headers[index] != name:
            found = headers[index] if index < len(headers) else "nothing"
            raise SheetLayoutError(
                f"Expected column {column} to be {name!r}, found {found!r}. "
                "The Sheet layout changed; re-check the column map before importing."
            )

    header_rows = first_data_row - 1
    return [
        {
            header: "" if index >= len(row) or row[index] is None else str(row[index])
            for index, header in enumerate(headers)
        }
        for row in values[header_rows:]
    ]


def _value(row: Mapping[str, object], field: str) -> str:
    value = row.get(field, "")
    return "" if value is None else str(value).strip()


def _parse_optional_level(
    value: str, *, row_number: int, issues: list[ImportIssue]
) -> int | None:
    if not value:
        return None
    try:
        level = int(value)
    except ValueError:
        issues.append(
            ImportIssue(
                row_number=row_number,
                field="Character Level",
                code="invalid_integer",
                message=f"Character Level must be a whole number, not {value!r}.",
            )
        )
        return None
    if not 1 <= level <= 20:
        issues.append(
            ImportIssue(
                row_number=row_number,
                field="Character Level",
                code="out_of_range",
                message="Character Level must be between 1 and 20.",
            )
        )
        return None
    return level


def _parse_active(
    value: str, *, row_number: int, issues: list[ImportIssue]
) -> bool | None:
    if value in {"1", "true", "TRUE"}:
        return True
    if value in {"0", "false", "FALSE"}:
        return False
    issues.append(
        ImportIssue(
            row_number=row_number,
            field="Active",
            code="invalid_boolean",
            message=f"Active must be 1/0 or true/false, not {value!r}.",
        )
    )
    return None


def parse_character_rows(
    rows: Iterable[Mapping[str, object]], *, first_row_number: int = 3
) -> SheetCharacterImportReport:
    """Validate Sheet character identities without writing or coercing data.

    The live Characters range begins at row 3. Invalid rows are reported with
    their Sheet row and field and are excluded from candidates. Display names
    are compared through `domain/names.py`, the one rule the platform claims
    identities under, so two rows the importer could not later tell apart are
    reported here; a duplicate is never resolved by first-match-wins.
    """
    candidates: list[SheetCharacterCandidate] = []
    issues: list[ImportIssue] = []
    seen_names: dict[str, int] = {}

    for offset, row in enumerate(rows):
        row_number = first_row_number + offset
        # A wholly empty row is a spacer, not a malformed character. It is
        # skipped without an issue, and `row_number` still advances, because a
        # row's position is what the import mapping is keyed on.
        if not any(_value(row, field) for field in row):
            continue
        row_errors_before = len(issues)
        display_name = _value(row, "Character Name (short)")
        if not display_name:
            issues.append(
                ImportIssue(
                    row_number=row_number,
                    field="Character Name (short)",
                    code="required",
                    message="Character Name (short) is required.",
                )
            )
        else:
            # The same key the platform claims identities under, so two rows the
            # importer would later find indistinguishable are refused here,
            # inside the run, with the row numbers still to hand.
            normalized_name = DisplayName(display_name).identity_key
            earlier_row = seen_names.get(normalized_name)
            if earlier_row is not None:
                issues.append(
                    ImportIssue(
                        row_number=row_number,
                        field="Character Name (short)",
                        code="duplicate",
                        message=(
                            f"Character name duplicates Sheet row {earlier_row} "
                            "case-insensitively."
                        ),
                    )
                )
            else:
                seen_names[normalized_name] = row_number

        level = _parse_optional_level(
            _value(row, "Character Level"),
            row_number=row_number,
            issues=issues,
        )
        active = _parse_active(
            _value(row, "Active"), row_number=row_number, issues=issues
        )
        player_name = _value(row, "Player Name") or None
        if player_name is None:
            issues.append(
                ImportIssue(
                    row_number=row_number,
                    field="Player Name",
                    code="owner_unresolved",
                    message="No Sheet player is available for Council reconciliation.",
                    severity=ImportIssueSeverity.WARNING,
                )
            )

        row_has_error = any(
            issue.row_number == row_number
            and issue.severity is ImportIssueSeverity.ERROR
            for issue in issues[row_errors_before:]
        )
        if row_has_error or active is None:
            continue

        candidates.append(
            SheetCharacterCandidate(
                row_number=row_number,
                display_name=display_name,
                long_name=_value(row, "Character Name (long)") or None,
                player_name=player_name,
                level=level,
                active=active,
            )
        )

    return SheetCharacterImportReport(
        candidates=tuple(candidates), issues=tuple(issues)
    )
