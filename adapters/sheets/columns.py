"""A1 column-letter arithmetic. One definition, importable without Discord.

`col_to_index` used to live in `helpers/utils.py`, which imports `discord` at
module scope. That made every consumer of a four-line pure function about
spreadsheet column letters require Pycord to be installed — including
`adapters/sheets/character_import.py`, and therefore including any operator
command that reads a Sheet layout. Temporary C-04 runs from its separate
Google-enabled operator environment, not the portal virtualenv; neither
environment needs Discord merely to interpret an A1 column.

The definition is here rather than duplicated: A1 addressing is Sheets-adapter
knowledge, this is the adapter, and `helpers/utils.py` re-exports the same object
so the bot's existing callers are unchanged.
"""
from __future__ import annotations


def col_to_index(col: str) -> int:
    """`"A"` → 0, `"D"` → 3, `"AL"` → 37. Base-26 with no zero digit."""
    index = 0
    for char in col.upper():
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


__all__ = ["col_to_index"]
