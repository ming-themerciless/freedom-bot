from __future__ import annotations

from collections.abc import Iterable, Mapping

from application.imports import (
    ImportIssue,
    ImportIssueSeverity,
    SheetCharacterCandidate,
    SheetCharacterImportReport,
)

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
    are compared case-insensitively because the current bot lookup is likewise
    case-insensitive; a duplicate is never resolved by first-match-wins.
    """
    candidates: list[SheetCharacterCandidate] = []
    issues: list[ImportIssue] = []
    seen_names: dict[str, int] = {}

    for offset, row in enumerate(rows):
        row_number = first_row_number + offset
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
            normalized_name = display_name.casefold()
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
