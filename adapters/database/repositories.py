from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from application.audit import AuditEvent
from application.errors import ConcurrencyConflictError
from application.imports import SheetRowMapping
from domain.identity import Character, DiscordUser
from domain.names import DisplayName

from .mappers import character_from_row, discord_user_from_row, sheet_row_mapping_from_row
from .tables import audit_events, characters, discord_users, sheet_row_mappings


class SqlAlchemyCharacterRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, character: Character) -> None:
        self._session.execute(
            insert(characters).values(
                id=character.id,
                display_name=character.display_name,
                long_name=character.long_name,
                level=character.level,
                active=character.active,
                version=character.version,
            )
        )

    def get(self, character_id: UUID) -> Character | None:
        row = self._session.execute(
            select(characters).where(characters.c.id == character_id)
        ).mappings().one_or_none()
        return character_from_row(row) if row else None

    def save(self, character: Character, *, expected_version: int) -> Character:
        next_version = expected_version + 1
        result = self._session.execute(
            update(characters)
            .where(
                characters.c.id == character.id,
                characters.c.version == expected_version,
            )
            .values(
                display_name=character.display_name,
                long_name=character.long_name,
                level=character.level,
                active=character.active,
                version=next_version,
            )
        )
        if result.rowcount != 1:
            raise ConcurrencyConflictError(
                f"Character {character.id} was changed by another transaction."
            )
        return Character(
            id=character.id,
            display_name=character.display_name,
            long_name=character.long_name,
            level=character.level,
            active=character.active,
            version=next_version,
        )

    def find_by_display_name(self, display_name: str) -> tuple[Character, ...]:
        """Compared in Python, on `domain/names.py`, over the whole table.

        The protocol's comparison is NFC-normalised full case folding. SQL
        `lower()` is **not** that comparison and must not be presented as it:
        PostgreSQL's `lower()` leaves `ß` alone, so `Test Straße` and
        `Test STRASSE` compare equal in Python and unequal in the database. A
        `WHERE` clause that narrowed the scan by `lower()` would therefore
        *skip* real matches, and the caller would be told a claimed name is
        free. There is no cheaper predicate that is safe in that direction:
        anything the database can evaluate today is narrower than the fold, and
        a narrower filter is the defect, not an optimisation.

        So this reads the characters and compares them here. The cost is one
        sequential scan and one `DisplayName` fold per row per call, and the
        importer calls it once per created or re-spelled row — quadratic in the
        size of the table across a run. That is deliberate and bounded: the
        bootstrap population is the live Sheet's roughly 150 characters, on a
        Unix socket, in an operator tool that runs occasionally.

        **The threshold at which this must change**: when `characters` passes
        roughly 2,000 rows, or when any request path — the Phase 3 portal, a
        Discord command — starts calling this, the fix is a schema one. Store
        the fold beside the name as a generated column, index it, and add the
        uniqueness rule that would let the database refuse a duplicate outright
        (§11 item 8 of the Phase 2 submission). That is a migration and a
        decided uniqueness policy, which is more than this correction is scoped
        to make.
        """
        wanted = DisplayName(display_name)
        rows = self._session.execute(
            select(characters).order_by(characters.c.created_at, characters.c.id)
        ).mappings().all()
        return tuple(
            character
            for character in (character_from_row(row) for row in rows)
            if character.name.claims_same_identity_as(wanted)
        )


class SqlAlchemyDiscordUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: DiscordUser) -> None:
        self._session.execute(
            insert(discord_users).values(
                id=user.discord_id,
                username=user.username,
                global_name=user.global_name,
            )
        )

    def get(self, discord_id: int) -> DiscordUser | None:
        row = self._session.execute(
            select(discord_users).where(discord_users.c.id == discord_id)
        ).mappings().one_or_none()
        return discord_user_from_row(row) if row else None


class SqlAlchemySheetRowMappingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, mapping: SheetRowMapping) -> None:
        self._session.execute(
            insert(sheet_row_mappings).values(
                id=uuid4(),
                character_id=mapping.character_id,
                sheet_tab=mapping.sheet_tab,
                row_index=mapping.row_index,
            )
        )

    def get_character_id(self, sheet_tab: str, row_index: int) -> UUID | None:
        return self._session.execute(
            select(sheet_row_mappings.c.character_id).where(
                sheet_row_mappings.c.sheet_tab == sheet_tab,
                sheet_row_mappings.c.row_index == row_index,
            )
        ).scalar_one_or_none()

    def list_for_tab(self, sheet_tab: str) -> tuple[SheetRowMapping, ...]:
        rows = self._session.execute(
            select(sheet_row_mappings)
            .where(sheet_row_mappings.c.sheet_tab == sheet_tab)
            .order_by(sheet_row_mappings.c.row_index)
        ).mappings().all()
        return tuple(sheet_row_mapping_from_row(row) for row in rows)


class SqlAlchemyAuditRepository:
    """Append-only. The runtime role holds `SELECT, INSERT` and nothing else."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def record(self, event: AuditEvent) -> None:
        self._session.execute(
            insert(audit_events).values(
                id=event.id,
                actor_discord_user_id=event.actor_discord_user_id,
                actor_capability=event.actor_capability.value,
                action=event.action,
                entity_type=event.entity_type,
                entity_id=event.entity_id,
                source=event.source.value,
                correlation_id=event.correlation_id,
                # The event holds a deeply frozen payload; JSON serialization
                # needs plain dicts and lists, so it is converted back here at
                # the persistence boundary rather than stored mutable.
                payload=event.json_payload(),
            )
        )
