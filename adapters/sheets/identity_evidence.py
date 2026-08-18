"""Sheet layout for M-2's two source ranges: `Characters C` and `Players A/B/D`.

The A1 ranges, the column positions and the header names live here and nowhere
else, because that is the rule for the Sheets adapter: application code is handed
typed rows and never learns what a column letter is.

Two ranges, and only two. `Characters` is read for column **C** alone — the
*Player Name* that is the join key (sheet inventory F-S1) — and the player tab for
**A**, **B** and **D**: the player's name, that player's **Discord name** and the
`Active DM` flag. Nothing here reads a game-state column, because the only
Sheet-era migration in Phase 3 is the identity linkage evidence (delivery plan §4,
migration contract §9), and nothing here writes: the reader is a values reader with
one method, obtained from `read_only.build_values_reader`, and there is no
`batch_update` anywhere in the module or in the tool that drives it.

## Positions are checked, not assumed

`Characters` reuses `character_import.rows_from_values`, so the same layout guard
the Phase 2 importer runs protects this run: an inserted column moves every field
at once, and reading column C from a shifted Sheet would attribute one player's
name to another character. The player tab gets the same treatment against its own
column map. A layout that has moved is a refusal naming the column, never a run
that quietly resolves the wrong thing.

## Uniqueness of the player name is decided elsewhere, deliberately

`player_rows` refuses a row that carries data without a *Player Name*, and skips a
wholly blank spacer. It does **not** decide whether two rows name the same person:
that comparison is `domain/names.py`'s NFC-normalised, case-folded `identity_key`,
which is the resolver's rule, and migration contract §7.3 forbids a second
implementation of *"are these the same name?"* — a second copy would be wrong in
the direction of linking two people. So this adapter supplies rows and positions,
and `application/web/identity_evidence.py` refuses the whole run when two of them
share one key (§7.3.1). The absence of the check here is the design, and this
paragraph is where a reader looking for it finds out where it went.

## `Active DM` is parsed and then not used for anything

It is recorded on the proposal because §7.1 calls it reconciliation evidence, and
it is read by no capability decision anywhere in this package (OD-18). Parsing it
strictly is still worth doing: a cell nobody can interpret is a cell whose meaning
somebody has changed, and finding that out costs one comparison.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from adapters.sheets.character_import import (
    FIRST_DATA_ROW as CHARACTER_FIRST_DATA_ROW,
    SheetLayoutError,
    rows_from_values,
)
from adapters.sheets.columns import col_to_index

#: `Characters C`. The join key, and the only column of that tab M-2 reads.
CHARACTER_PLAYER_NAME_HEADER = "Player Name"

#: The default tab and range for the character side, matching the Phase 2
#: importer's so both tools read one layout.
CHARACTER_TAB = "Characters"
CHARACTER_RANGE = "A1:AL150"

#: There is deliberately **no `PLAYER_TAB` constant**, and the reason is not that
#: the name is unknown. Peter Duscha confirmed the one-time legacy tab as `Players`
#: on 2026-08-17 (`C-P3.2-B`), and `docs/discovery/sheet-inventory.md` §2.1 records
#: it. A constant here would take that one-time *migration input* and make it
#: enduring command configuration, which is what `C-P3.2-B` rejected: the failure
#: mode it guards against is a run that silently reads whatever tab the default
#: names and attributes one player's Discord name to another character. C-04 takes
#: `--player-tab` as a **required** argument instead, so the operator states the
#: tab every time (migration contract §7.7). `Players A/B/D` in the contract is the
#: *columns*; the tab's name is the operator's argument.
PLAYER_RANGE = "A1:H400"

#: Sheet inventory §2.1, by position as well as by name.
PLAYER_COLUMNS = {
    "Player Name": "A",
    "Discord Name": "B",
    "Active DM": "D",
}

#: The player tab has one header row; data starts at row 2. (`Characters` has
#: two, which is why it has its own constant.)
PLAYER_FIRST_DATA_ROW = 2

#: Accepted spellings of `Active DM`. Blank is `false` — an unset flag is not a
#: malformed one — and anything else is a refusal naming the row, because a cell
#: nobody can interpret means the column's meaning has changed.
_TRUE_TOKENS = frozenset({"1", "true", "yes", "y", "x"})
_FALSE_TOKENS = frozenset({"", "0", "false", "no", "n"})


@dataclass(frozen=True, slots=True)
class CharacterEvidenceRow:
    """One `Characters` row's position and its column C. Nothing else."""

    row_number: int
    player_name: str


@dataclass(frozen=True, slots=True)
class PlayerEvidenceRow:
    """One player-tab row: A, B and D, as read."""

    row_number: int
    player_name: str
    discord_name: str | None
    active_dm: bool


def _cell(row, header: str) -> str:
    value = row.get(header, "")
    return "" if value is None else str(value).strip()


def character_rows(values: Sequence[Sequence[Any]]) -> tuple[CharacterEvidenceRow, ...]:
    """`Characters` rows that carry a non-blank column C, with their positions.

    A blank column C is **not** a source row: §7.4 defines `source_characters` as
    *"rows in Characters with a non-blank column C"*, so a character nobody has
    named a player for contributes nothing to the arithmetic rather than
    contributing an `unresolved` proposal. It is not evidence of anything — the
    Sheet is simply silent — and the Phase 2 importer already reports it as
    `owner_unresolved`.
    """
    rows = rows_from_values(values, first_data_row=CHARACTER_FIRST_DATA_ROW)
    return tuple(
        CharacterEvidenceRow(
            row_number=CHARACTER_FIRST_DATA_ROW + offset,
            player_name=_cell(row, CHARACTER_PLAYER_NAME_HEADER),
        )
        for offset, row in enumerate(rows)
        if _cell(row, CHARACTER_PLAYER_NAME_HEADER)
    )


def player_rows(values: Sequence[Sequence[Any]]) -> tuple[PlayerEvidenceRow, ...]:
    """The player tab's A/B/D, positionally validated, with `Active DM` parsed."""
    if not values:
        raise SheetLayoutError("The player range returned no rows at all.")

    headers = [str(header).strip() for header in values[0]]
    for name, column in PLAYER_COLUMNS.items():
        index = col_to_index(column)
        if index >= len(headers) or headers[index] != name:
            found = headers[index] if index < len(headers) else "nothing"
            raise SheetLayoutError(
                f"Expected player-tab column {column} to be {name!r}, found "
                f"{found!r}. The Sheet layout changed; re-check the column map "
                "before running the identity-evidence migration."
            )

    parsed: list[PlayerEvidenceRow] = []
    for offset, row in enumerate(values[PLAYER_FIRST_DATA_ROW - 1 :]):
        row_number = PLAYER_FIRST_DATA_ROW + offset
        cells = {
            header: "" if index >= len(row) or row[index] is None else str(row[index])
            for index, header in enumerate(headers)
        }
        player_name = _cell(cells, "Player Name")
        if not player_name:
            # A wholly blank row is a spacer. §7.4 counts `source_players` as
            # "rows in the player tab", and a spacer is not one of those either:
            # it names nobody, so it can neither be joined to nor counted as a
            # person the migration failed to resolve.
            if not any(_cell(cells, header) for header in headers):
                continue
            raise SheetLayoutError(
                f"Player-tab row {row_number} has data but no Player Name, so no "
                "character row can be joined to it. Fix the row and re-run."
            )
        discord_name = _cell(cells, "Discord Name")
        parsed.append(
            PlayerEvidenceRow(
                row_number=row_number,
                player_name=player_name,
                discord_name=discord_name or None,
                active_dm=_active_dm(_cell(cells, "Active DM"), row_number=row_number),
            )
        )
    return tuple(parsed)


def _active_dm(value: str, *, row_number: int) -> bool:
    folded = value.casefold()
    if folded in _TRUE_TOKENS:
        return True
    if folded in _FALSE_TOKENS:
        return False
    raise SheetLayoutError(
        f"Player-tab row {row_number}: Active DM must be 1/0, true/false, yes/no "
        f"or blank, not {value!r}."
    )


__all__ = [
    "CHARACTER_FIRST_DATA_ROW",
    "CHARACTER_PLAYER_NAME_HEADER",
    "CHARACTER_RANGE",
    "CHARACTER_TAB",
    "CharacterEvidenceRow",
    "PLAYER_COLUMNS",
    "PLAYER_FIRST_DATA_ROW",
    "PLAYER_RANGE",
    "PlayerEvidenceRow",
    "SheetLayoutError",
    "character_rows",
    "player_rows",
]
