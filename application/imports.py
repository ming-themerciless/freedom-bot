from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ImportIssueSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True, slots=True)
class ImportIssue:
    row_number: int
    field: str
    code: str
    message: str
    severity: ImportIssueSeverity = ImportIssueSeverity.ERROR


@dataclass(frozen=True, slots=True)
class SheetCharacterCandidate:
    row_number: int
    display_name: str
    long_name: str | None
    player_name: str | None
    level: int | None
    active: bool


@dataclass(frozen=True, slots=True)
class SheetCharacterImportReport:
    candidates: tuple[SheetCharacterCandidate, ...]
    issues: tuple[ImportIssue, ...]

    @property
    def has_errors(self) -> bool:
        return any(issue.severity is ImportIssueSeverity.ERROR for issue in self.issues)

    @property
    def error_count(self) -> int:
        return sum(
            issue.severity is ImportIssueSeverity.ERROR for issue in self.issues
        )

    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity is ImportIssueSeverity.WARNING for issue in self.issues
        )
