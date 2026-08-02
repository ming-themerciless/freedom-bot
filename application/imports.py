from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from domain.names import DisplayName


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

    @property
    def name(self) -> DisplayName:
        """The row's name under the platform's one comparison rule."""
        return DisplayName(self.display_name)


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


@dataclass(frozen=True, slots=True)
class SheetRowMapping:
    """A Sheet row is an import key, never an identity (ADR 0005).

    The mapping is what makes re-import idempotent: the row resolves to a
    `character_id` the platform generated, so a Sheet reorder or a renamed
    character cannot mint a second character.
    """

    character_id: UUID
    sheet_tab: str
    row_index: int

    def __post_init__(self) -> None:
        if not self.sheet_tab.strip():
            raise ValueError("A Sheet tab name is required.")
        if self.row_index <= 0:
            raise ValueError("Sheet row indexes start at 1.")


class SheetImportAction(Enum):
    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    #: Planned but refused: the row needs a human decision before it can import.
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class SheetImportEntry:
    row_number: int
    display_name: str
    action: SheetImportAction
    #: `None` only for a blocked row. For a created row in a dry run the id is
    #: provisional — the rehearsal is rolled back, and applying generates a new one.
    character_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class SheetCharacterImportOutcome:
    """What one import run did, or would have done.

    `applied` is the only statement about the database. A dry run and a blocked
    run both leave it `False`, and both are otherwise identical rehearsals: the
    same reads, writes and constraints, ending in a rollback.
    """

    sheet_tab: str
    entries: tuple[SheetImportEntry, ...]
    issues: tuple[ImportIssue, ...]
    correlation_id: UUID
    dry_run: bool
    applied: bool

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

    def count(self, action: SheetImportAction) -> int:
        return sum(entry.action is action for entry in self.entries)
