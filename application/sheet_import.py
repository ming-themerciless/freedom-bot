"""The Sheet character identity import use case (implementation plan, Phase 2).

Every row either resolves to exactly one character through its stored
`sheet_row_mappings` key, or is reported for a human to resolve. The importer
writes no game state — identity, level and the active flag only — and it does
not create `character_access`: who owns a character is a Council decision
(OD-13, OD-37), not something a Sheet name column can settle.

The hard case is a **mapped semantic name change**: a row whose stored character
is recorded under a different name. It can be an in-place rename, or it can be a
row that moved out from under its mapping while the character who used to sit
there was renamed in the same edit. Those two readings are *observationally
identical*. Permute two mapped rows and give both displaced characters fresh,
otherwise-unused names, and the import is byte-for-byte what two ordinary
renames produce — no row is added, none removed, none malformed, no mapping
dangles, neither old name appears anywhere else, and neither new name collides.
A Sheet row carries no stable source identity, so no row-count, index or name
evidence can separate the readings. An earlier revision of this module believed
a set of six run-level signals could; that claim was false, and committing the
wrong reading writes one character's identity onto another with nothing
afterwards to notice.

So a semantic mapped-name change is never applied automatically. It is reported
(`mapped_name_change`, or the more specific `row_identity_shift` /
`name_collision` where the run says which), and the whole run stops until a
deliberate mapping/identity reconciliation is made outside this importer. What
stays automatic is everything that needs no identity guess: creating an unmapped
row whose name nobody claims, updating long name, level and the active flag
while the display name is unchanged, and a change of capitalisation alone, which
is identity-neutral — but which is still looked up against every other
character before it is written, because a re-cased name can be taken.

*Which* changes count as capitalisation alone is not this module's decision to
make locally. `domain/names.py` holds the single comparison rule the parser,
this service and both repositories use. Deciding it here with `casefold()` while
the platform looked names up with `lower()` is exactly how `Test Straße` was
once accepted as a re-capitalisation of `Test STRASSE`, skipping the collision
lookup and committing two characters under one display name.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from uuid import UUID, uuid4

from application.audit import ActorCapability, AuditEvent, AuditSource
from application.imports import (
    ImportIssue,
    ImportIssueSeverity,
    SheetCharacterCandidate,
    SheetCharacterImportOutcome,
    SheetCharacterImportReport,
    SheetImportAction,
    SheetImportEntry,
    SheetRowMapping,
)
from application.repositories import UnitOfWork
from domain.identity import Character

#: `entity_type` for audit rows this importer writes.
CHARACTER_ENTITY = "character"

CREATE_ACTION = "sheet_import.character.created"
UPDATE_ACTION = "sheet_import.character.updated"

#: The field every issue about a row's identity is reported against.
NAME_FIELD = "Character Name (short)"


@dataclass(frozen=True, slots=True)
class _Resolution:
    """One candidate row, resolved against the platform, before any decision.

    Every row is resolved before any is decided so that a refusal can name what
    the rest of the run shows: where else a mapped character now appears, or who
    already holds the name a row is claiming. That does not decide whether a
    name change is genuine — nothing in the run can — but it turns a bare
    refusal into an instruction.
    """

    candidate: SheetCharacterCandidate
    #: The character this row's mapping points at, if the row is mapped.
    character_id: UUID | None
    #: That character as it stands now. `None` with a `character_id` set means
    #: the mapping is dangling.
    current: Character | None
    #: Characters already claiming the candidate's name, under the one identity
    #: key in `domain/names.py`. Looked up for every creation and every spelling
    #: change, including a change of capitalisation alone; a row whose name is
    #: character-for-character what is stored claims nothing new and costs no
    #: extra query.
    same_named: tuple[Character, ...]

    @property
    def row_number(self) -> int:
        return self.candidate.row_number

    @property
    def is_creation(self) -> bool:
        return self.character_id is None

    @property
    def is_dangling(self) -> bool:
        return self.character_id is not None and self.current is None

    @property
    def is_spelling_change(self) -> bool:
        """The mapped row's name is not character-for-character what is stored.

        Every one of these is looked up against the other characters before
        anything is written, whether or not it turns out to be identity-neutral:
        a re-capitalised name can still be a name somebody else holds.
        """
        return self.current is not None and not self.candidate.name.is_exactly(
            self.current.name
        )

    @property
    def is_semantic_name_change(self) -> bool:
        """The mapped character is recorded under a *different* name.

        A change of capitalisation alone is not one: the re-cased name claims
        the same identity under `domain/names.py`, so it denotes the same
        character and cannot be a moved row for that same reason. Nothing wider
        than capitalisation qualifies — `Test Straße` to `Test STRASSE` replaces
        one letter with two and is a semantic change.
        """
        return self.current is not None and self.candidate.name.is_semantic_change_from(
            self.current.name
        )

    def other_holder(self) -> Character | None:
        """A *different* character already claiming this row's name, if any."""
        for character in self.same_named:
            if character.id != self.character_id:
                return character
        return None


class SheetCharacterImportService:
    """Import Sheet character identities idempotently, or explain why not.

    One run is one transaction. It is committed only when the caller asked to
    apply it *and* nothing in the run needs a human decision, so a run can
    never half-import: the acceptance criterion is that import failure cannot
    partially commit.

    A dry run is the same rehearsal with a rollback at the end — the same
    reads, the same writes, the same database constraints — so a dry run that
    reports clean is evidence about this schema, not about a model of it.

    Rows are resolved one query at a time rather than batched. That is a
    deliberate choice for an operator tool that runs occasionally over a few
    hundred rows on a local socket: per-row queries keep each decision, and the
    issue it reports, readable next to the row that caused it. If the import
    ever becomes a request path or the Sheet grows by an order of magnitude,
    pre-loading the tab's mappings and characters is the change to make — and,
    with it, storing and indexing the identity key `domain/names.py` defines,
    which is the threshold `SqlAlchemyCharacterRepository.find_by_display_name`
    records.
    """

    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
        *,
        correlation_ids: Callable[[], UUID] = uuid4,
        character_ids: Callable[[], UUID] = uuid4,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._correlation_ids = correlation_ids
        self._character_ids = character_ids

    def run(
        self,
        report: SheetCharacterImportReport,
        *,
        sheet_tab: str,
        dry_run: bool = True,
    ) -> SheetCharacterImportOutcome:
        correlation_id = self._correlation_ids()
        entries: list[SheetImportEntry] = []
        # The parse issues travel with the outcome: a caller reading only the
        # outcome must still see the malformed rows that never became candidates.
        issues: list[ImportIssue] = list(report.issues)

        rows_by_name = _rows_by_name(report)

        with self._unit_of_work_factory() as unit_of_work:
            resolutions = [
                self._resolve(unit_of_work, candidate, sheet_tab=sheet_tab)
                for candidate in report.candidates
            ]
            absent = self._absent_from_source(
                unit_of_work, report, sheet_tab=sheet_tab, resolutions=resolutions
            )

            for resolution in resolutions:
                entries.append(
                    self._import_row(
                        unit_of_work,
                        resolution,
                        sheet_tab=sheet_tab,
                        correlation_id=correlation_id,
                        issues=issues,
                        rows_by_name=rows_by_name,
                    )
                )
            issues.extend(absent)

            blocked = any(
                issue.severity is ImportIssueSeverity.ERROR for issue in issues
            )
            applied = not dry_run and not blocked
            if applied:
                unit_of_work.commit()
            else:
                # Every character, mapping and audit row this run wrote goes
                # with it: the transaction is the unit, not the row.
                unit_of_work.rollback()

        return SheetCharacterImportOutcome(
            sheet_tab=sheet_tab,
            entries=tuple(entries),
            issues=tuple(issues),
            correlation_id=correlation_id,
            dry_run=dry_run,
            applied=applied,
        )

    def _resolve(
        self,
        unit_of_work: UnitOfWork,
        candidate: SheetCharacterCandidate,
        *,
        sheet_tab: str,
    ) -> _Resolution:
        character_id = unit_of_work.sheet_row_mappings.get_character_id(
            sheet_tab, candidate.row_number
        )
        current = (
            unit_of_work.characters.get(character_id)
            if character_id is not None
            else None
        )
        resolved = _Resolution(
            candidate=candidate,
            character_id=character_id,
            current=current,
            same_named=(),
        )
        # A row that is about to claim a name — a new character, or a mapped one
        # whose spelling changed at all — can collide with an existing holder.
        # A row whose name is character-for-character what is stored claims
        # nothing new, so it costs no query. Every other spelling change is
        # looked up, *including* a change of capitalisation alone: that change
        # is identity-neutral with respect to its own character and says nothing
        # about whether another character already holds the re-cased name.
        if not (resolved.is_creation or resolved.is_spelling_change):
            return resolved
        return replace(
            resolved,
            same_named=tuple(
                unit_of_work.characters.find_by_display_name(candidate.display_name)
            ),
        )

    def _import_row(
        self,
        unit_of_work: UnitOfWork,
        resolution: _Resolution,
        *,
        sheet_tab: str,
        correlation_id: UUID,
        issues: list[ImportIssue],
        rows_by_name: dict[str, int],
    ) -> SheetImportEntry:
        if resolution.is_dangling:
            return self._block(
                resolution,
                issues,
                code="dangling_mapping",
                message=(
                    f"Sheet row {resolution.row_number} maps to character "
                    f"{resolution.character_id}, which no longer exists."
                ),
            )
        if resolution.is_creation:
            return self._create(
                unit_of_work,
                resolution,
                sheet_tab=sheet_tab,
                correlation_id=correlation_id,
                issues=issues,
            )
        return self._update(
            unit_of_work,
            resolution,
            sheet_tab=sheet_tab,
            correlation_id=correlation_id,
            issues=issues,
            rows_by_name=rows_by_name,
        )

    def _create(
        self,
        unit_of_work: UnitOfWork,
        resolution: _Resolution,
        *,
        sheet_tab: str,
        correlation_id: UUID,
        issues: list[ImportIssue],
    ) -> SheetImportEntry:
        candidate = resolution.candidate
        # An unmapped row carrying a name the platform already holds is the
        # signature of a moved or re-typed Sheet row. Creating a second
        # character would duplicate a player silently, and re-keying the
        # existing mapping would be a guess — two characters could have swapped
        # rows. Report it and let a maintainer say which.
        existing = resolution.other_holder()
        if existing is not None:
            return self._block(
                resolution,
                issues,
                code="unmapped_name_collision",
                message=(
                    f"{candidate.display_name!r} is not mapped to Sheet row "
                    f"{candidate.row_number} but already exists as character "
                    f"{existing.id}. Resolve the mapping before importing."
                ),
            )

        character = Character(
            id=self._character_ids(),
            display_name=candidate.display_name,
            long_name=candidate.long_name,
            level=candidate.level,
            active=candidate.active,
        )
        unit_of_work.characters.add(character)
        unit_of_work.sheet_row_mappings.add(
            SheetRowMapping(
                character_id=character.id,
                sheet_tab=sheet_tab,
                row_index=candidate.row_number,
            )
        )
        unit_of_work.audit.record(
            self._audit_event(
                CREATE_ACTION,
                character.id,
                correlation_id=correlation_id,
                payload={
                    "sheet_tab": sheet_tab,
                    "row_index": candidate.row_number,
                    "display_name": character.display_name,
                },
            )
        )
        return SheetImportEntry(
            row_number=candidate.row_number,
            display_name=candidate.display_name,
            action=SheetImportAction.CREATED,
            character_id=character.id,
        )

    def _update(
        self,
        unit_of_work: UnitOfWork,
        resolution: _Resolution,
        *,
        sheet_tab: str,
        correlation_id: UUID,
        issues: list[ImportIssue],
        rows_by_name: dict[str, int],
    ) -> SheetImportEntry:
        candidate = resolution.candidate
        current = resolution.current
        assert current is not None  # guaranteed by _import_row
        character_id = resolution.character_id
        assert character_id is not None

        if resolution.is_semantic_name_change:
            code, message = self._name_change_refusal(
                resolution, rows_by_name=rows_by_name
            )
            return self._block(
                resolution, issues, code=code, message=message,
                character_id=character_id,
            )

        # What is left is either the same name exactly, or a change of
        # capitalisation alone. The second is identity-neutral for *this*
        # character and still has to be looked up: another character may
        # already claim the name it is being re-cased into, and writing it
        # would leave two characters answering to one name.
        if resolution.is_spelling_change:
            holder = resolution.other_holder()
            if holder is not None:
                return self._block(
                    resolution,
                    issues,
                    code="name_collision",
                    message=(
                        f"Sheet row {candidate.row_number} would re-spell "
                        f"character {character_id} as "
                        f"{candidate.display_name!r}, which character "
                        f"{holder.id} already claims. Resolve the duplicate "
                        "before importing."
                    ),
                    character_id=character_id,
                )

        desired = replace(
            current,
            display_name=candidate.display_name,
            long_name=candidate.long_name,
            level=candidate.level,
            active=candidate.active,
        )
        if desired == current:
            return SheetImportEntry(
                row_number=candidate.row_number,
                display_name=candidate.display_name,
                action=SheetImportAction.UNCHANGED,
                character_id=character_id,
            )

        unit_of_work.characters.save(desired, expected_version=current.version)
        unit_of_work.audit.record(
            self._audit_event(
                UPDATE_ACTION,
                character_id,
                correlation_id=correlation_id,
                payload={
                    "sheet_tab": sheet_tab,
                    "row_index": candidate.row_number,
                    "changes": _changed_fields(current, desired),
                },
            )
        )
        return SheetImportEntry(
            row_number=candidate.row_number,
            display_name=candidate.display_name,
            action=SheetImportAction.UPDATED,
            character_id=character_id,
        )

    def _name_change_refusal(
        self,
        resolution: _Resolution,
        *,
        rows_by_name: dict[str, int],
    ) -> tuple[str, str]:
        """Why this name change is refused, in the most specific terms available.

        Every semantic mapped-name change is refused; the run only decides *how
        it is explained*. Where the run shows the mapped character at another row
        or the new name already taken, the operator is told that, because it says
        what to fix. Where it shows neither, the refusal is the general one:
        applying the change would commit one of two readings of an input that
        cannot distinguish them.
        """
        current = resolution.current
        assert current is not None
        candidate = resolution.candidate

        # The mapped character is *also* listed somewhere else in this import.
        # The rows have moved under the mappings — which is what inserting or
        # deleting a Sheet row does to every row below it — and this run can say
        # exactly where, which is more use to an operator than the general
        # refusal below.
        elsewhere = rows_by_name.get(current.name.identity_key)
        if elsewhere is not None and elsewhere != candidate.row_number:
            return (
                "row_identity_shift",
                f"Sheet row {candidate.row_number} maps to "
                f"{current.display_name!r}, which this import lists at row "
                f"{elsewhere}. The rows appear to have moved; re-key the "
                "mapping deliberately before importing.",
            )

        # The name this row is claiming already belongs to somebody else.
        # Renaming into it would leave two characters answering to one name.
        holder = resolution.other_holder()
        if holder is not None:
            return (
                "name_collision",
                f"Sheet row {candidate.row_number} would rename character "
                f"{resolution.character_id} to {candidate.display_name!r}, which "
                f"character {holder.id} already uses. Resolve the duplicate "
                "before importing.",
            )

        # Nothing else in the run explains the change, which is exactly the case
        # that cannot be decided: a permutation of mapped rows in which every
        # displaced character is also renamed to a fresh name produces this same
        # input, and so does an ordinary rename. A false refusal costs a human a
        # reconciliation; committing the wrong reading costs a character its
        # identity, silently and permanently.
        return (
            "mapped_name_change",
            f"Sheet row {candidate.row_number} maps to "
            f"{current.display_name!r} but now reads "
            f"{candidate.display_name!r}. A mapped name change is not applied "
            "automatically: it cannot be told apart from a row that moved under "
            "its mapping while the character it displaced was renamed. "
            "Reconcile the mapping and the identity deliberately, then import "
            "again.",
        )

    def _block(
        self,
        resolution: _Resolution,
        issues: list[ImportIssue],
        *,
        code: str,
        message: str,
        character_id: UUID | None = None,
    ) -> SheetImportEntry:
        issues.append(
            ImportIssue(
                row_number=resolution.row_number,
                field=NAME_FIELD,
                code=code,
                message=message,
            )
        )
        return SheetImportEntry(
            row_number=resolution.row_number,
            display_name=resolution.candidate.display_name,
            action=SheetImportAction.BLOCKED,
            character_id=character_id,
        )

    def _absent_from_source(
        self,
        unit_of_work: UnitOfWork,
        report: SheetCharacterImportReport,
        *,
        sheet_tab: str,
        resolutions: list[_Resolution],
    ) -> list[ImportIssue]:
        """Report mapped rows this run did not see.

        A character missing from the source is never deactivated or deleted
        here — the row may simply have failed validation, and the platform does
        not treat an absent Sheet row as an instruction. It is a warning for
        Council reconciliation, and a signal that rows may have moved.
        """
        covered = {resolution.row_number for resolution in resolutions}
        covered.update(issue.row_number for issue in report.issues)
        return [
            ImportIssue(
                row_number=mapping.row_index,
                field=NAME_FIELD,
                code="absent_from_source",
                message=(
                    f"Character {mapping.character_id} is mapped to Sheet row "
                    f"{mapping.row_index}, which this import did not contain."
                ),
                severity=ImportIssueSeverity.WARNING,
            )
            for mapping in unit_of_work.sheet_row_mappings.list_for_tab(sheet_tab)
            if mapping.row_index not in covered
        ]

    def _audit_event(
        self,
        action: str,
        character_id: UUID,
        *,
        correlation_id: UUID,
        payload: dict[str, object],
    ) -> AuditEvent:
        return AuditEvent(
            action=action,
            entity_type=CHARACTER_ENTITY,
            entity_id=str(character_id),
            source=AuditSource.IMPORT,
            # No Discord user acts here. The operator who started the import is
            # accountable for the run; the writer of each row is the platform.
            actor_capability=ActorCapability.SYSTEM,
            correlation_id=correlation_id,
            payload=payload,
        )


def _rows_by_name(report: SheetCharacterImportReport) -> dict[str, int]:
    """Where each candidate name sits in this import, under the shared rule.

    Keyed on `DisplayName.identity_key`, which is what the parser rejects
    duplicates by, so one row per key is exact rather than last-wins.
    """
    return {
        candidate.name.identity_key: candidate.row_number
        for candidate in report.candidates
    }


def _changed_fields(current: Character, desired: Character) -> dict[str, object]:
    return {
        field: {"from": getattr(current, field), "to": getattr(desired, field)}
        for field in ("display_name", "long_name", "level", "active")
        if getattr(current, field) != getattr(desired, field)
    }
