"""In-memory doubles for the application-service tests.

The fake unit of work models the one behaviour those tests depend on that a
dictionary does not have: uncommitted work disappears. Each `with` block edits
a copy of the store and publishes it only on `commit()`, so a test can assert
that a dry run left nothing behind without needing PostgreSQL.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from uuid import UUID

from application.audit import AuditEvent
from application.errors import ConcurrencyConflictError
from application.imports import SheetRowMapping
from domain.identity import Character, DiscordUser
from domain.names import DisplayName


@dataclass
class FakeStore:
    """The committed state, shared by every unit of work built from it."""

    characters: dict[UUID, Character] = field(default_factory=dict)
    discord_users: dict[int, DiscordUser] = field(default_factory=dict)
    sheet_row_mappings: list[SheetRowMapping] = field(default_factory=list)
    audit_events: list[AuditEvent] = field(default_factory=list)

    def copy(self) -> FakeStore:
        return FakeStore(
            characters=dict(self.characters),
            discord_users=dict(self.discord_users),
            sheet_row_mappings=list(self.sheet_row_mappings),
            audit_events=list(self.audit_events),
        )


class FakeCharacterRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, character: Character) -> None:
        if character.id in self._store.characters:
            raise ValueError(f"Character {character.id} already exists.")
        self._store.characters[character.id] = character

    def get(self, character_id: UUID) -> Character | None:
        return self._store.characters.get(character_id)

    def save(self, character: Character, *, expected_version: int) -> Character:
        current = self._store.characters.get(character.id)
        if current is None or current.version != expected_version:
            raise ConcurrencyConflictError(
                f"Character {character.id} was changed by another transaction."
            )
        saved = replace(character, version=expected_version + 1)
        self._store.characters[character.id] = saved
        return saved

    def find_by_display_name(self, display_name: str) -> tuple[Character, ...]:
        """The same comparison the PostgreSQL repository makes, on the same rule.

        A fake that folded names differently from the adapter would let the
        application suite prove a decision the database would not reach — which
        is how the Phase 2 normalisation defect stayed invisible to it.
        """
        wanted = DisplayName(display_name)
        return tuple(
            character
            for character in self._store.characters.values()
            if character.name.claims_same_identity_as(wanted)
        )


class FakeDiscordUserRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, user: DiscordUser) -> None:
        self._store.discord_users[user.discord_id] = user

    def get(self, discord_id: int) -> DiscordUser | None:
        return self._store.discord_users.get(discord_id)


class FakeSheetRowMappingRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def add(self, mapping: SheetRowMapping) -> None:
        for existing in self._store.sheet_row_mappings:
            if (
                existing.sheet_tab == mapping.sheet_tab
                and existing.row_index == mapping.row_index
            ) or (
                existing.sheet_tab == mapping.sheet_tab
                and existing.character_id == mapping.character_id
            ):
                raise ValueError(
                    "sheet_row_mappings uniqueness violated for "
                    f"{mapping.sheet_tab}!{mapping.row_index}."
                )
        self._store.sheet_row_mappings.append(mapping)

    def get_character_id(self, sheet_tab: str, row_index: int) -> UUID | None:
        for mapping in self._store.sheet_row_mappings:
            if mapping.sheet_tab == sheet_tab and mapping.row_index == row_index:
                return mapping.character_id
        return None

    def list_for_tab(self, sheet_tab: str) -> tuple[SheetRowMapping, ...]:
        return tuple(
            sorted(
                (m for m in self._store.sheet_row_mappings if m.sheet_tab == sheet_tab),
                key=lambda mapping: mapping.row_index,
            )
        )


class FakeAuditRepository:
    def __init__(self, store: FakeStore) -> None:
        self._store = store

    def record(self, event: AuditEvent) -> None:
        self._store.audit_events.append(event)


class FakeUnitOfWork:
    """One `with` block, one transaction, exactly as the real one behaves."""

    def __init__(self, store: FakeStore) -> None:
        self._committed = store
        self._pending = store.copy()
        self.committed_count = 0
        self.rolled_back_count = 0

    def __enter__(self) -> FakeUnitOfWork:
        self._pending = self._committed.copy()
        self.characters = FakeCharacterRepository(self._pending)
        self.discord_users = FakeDiscordUserRepository(self._pending)
        self.sheet_row_mappings = FakeSheetRowMappingRepository(self._pending)
        self.audit = FakeAuditRepository(self._pending)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self._committed.characters = dict(self._pending.characters)
        self._committed.discord_users = dict(self._pending.discord_users)
        self._committed.sheet_row_mappings = list(self._pending.sheet_row_mappings)
        self._committed.audit_events = list(self._pending.audit_events)
        self.committed_count += 1

    def rollback(self) -> None:
        # Mutated in place rather than rebound: the repositories hold this
        # object, so rebinding would leave them writing to a discarded copy.
        restored = self._committed.copy()
        self._pending.characters = restored.characters
        self._pending.discord_users = restored.discord_users
        self._pending.sheet_row_mappings = restored.sheet_row_mappings
        self._pending.audit_events = restored.audit_events
        self.rolled_back_count += 1


def unit_of_work_factory(store: FakeStore):
    """A factory the service can call once per run, recording each unit."""
    units: list[FakeUnitOfWork] = []

    def factory() -> FakeUnitOfWork:
        unit = FakeUnitOfWork(store)
        units.append(unit)
        return unit

    factory.units = units  # type: ignore[attr-defined]
    return factory
