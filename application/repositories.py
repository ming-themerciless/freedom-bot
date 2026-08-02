from __future__ import annotations

from typing import Protocol
from uuid import UUID

from application.audit import AuditEvent
from application.imports import SheetRowMapping
from domain.identity import Character, DiscordUser


class CharacterRepository(Protocol):
    def add(self, character: Character) -> None: ...

    def get(self, character_id: UUID) -> Character | None: ...

    def save(self, character: Character, *, expected_version: int) -> Character: ...

    def find_by_display_name(self, display_name: str) -> tuple[Character, ...]:
        """Every character claiming the same identity as `display_name`.

        The comparison is `DisplayName.claims_same_identity_as` — NFC-normalised
        full case folding — and every implementation must answer for the whole
        of that domain, not for the part a particular database collation happens
        to agree with. A narrower implementation would silently reintroduce the
        Phase 2 normalisation defect: a name the caller believes is free while
        the platform already holds it.

        This returns a tuple rather than one character because display names
        carry no uniqueness constraint: two matches are a reconciliation
        finding for the caller to report, not an error to raise here.
        """
        ...


class DiscordUserRepository(Protocol):
    def add(self, user: DiscordUser) -> None: ...

    def get(self, discord_id: int) -> DiscordUser | None: ...


class SheetRowMappingRepository(Protocol):
    def add(self, mapping: SheetRowMapping) -> None: ...

    def get_character_id(self, sheet_tab: str, row_index: int) -> UUID | None: ...

    def list_for_tab(self, sheet_tab: str) -> tuple[SheetRowMapping, ...]: ...


class AuditRepository(Protocol):
    def record(self, event: AuditEvent) -> None:
        """Append one event. There is deliberately no update or delete."""
        ...


class UnitOfWork(Protocol):
    characters: CharacterRepository
    discord_users: DiscordUserRepository
    sheet_row_mappings: SheetRowMappingRepository
    audit: AuditRepository

    def __enter__(self) -> UnitOfWork: ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
