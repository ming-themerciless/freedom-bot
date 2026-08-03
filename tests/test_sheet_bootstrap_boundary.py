"""The Sheet's remaining role, and the fences around it.

Controlled baseline v1.1 removed Sheet-era migration from Phase 2 entirely, and
ruling D-3 of 2026-08-02 reverted `tools/import_sheet_characters.py` to its
accepted I-01 state and recorded it as **dormant**: its four identity fields are
allocated to package 5.1, which owns their migration.

So the tests here are no longer about fencing a bootstrap. They are about the
boundary that survives it, and each one still earns its place:

- no platform path writes Google Sheets;
- the read-only scope stays the narrowest that serves the reader;
- the live bot's connector is untouched and still read/write, because the bot
  still needs it; and
- no platform module imports that connector, and the domain layer imports no
  infrastructure at all.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


# -- never writes the Sheet ----------------------------------------------------


def test_no_import_path_calls_batch_update():
    # Checked as a *call*, not as a word: the modules describe the restriction
    # in prose, and a prose mention is not a write.
    for module in (
        "tools/import_sheet_characters.py",
        "adapters/sheets/read_only.py",
        "adapters/sheets/character_import.py",
        "application/sheet_import.py",
    ):
        body = (ROOT / module).read_text(encoding="utf-8")
        assert "batch_update(" not in body, module


def test_the_read_only_scope_is_the_narrowest_that_serves_the_reader():
    from adapters.sheets.read_only import READ_ONLY_SCOPES

    assert READ_ONLY_SCOPES == (
        "https://www.googleapis.com/auth/spreadsheets.readonly",
    )


# -- the legacy bot connector is untouched -------------------------------------


def test_the_legacy_sheets_connector_still_exposes_read_and_write():
    from connectors import sheets

    assert hasattr(sheets, "get_values")
    assert hasattr(sheets, "batch_update")


def test_no_phase_2_module_imports_the_legacy_connector_except_the_fallback():
    """The bot's connector is a bot dependency, not a platform one.

    The single permitted use is `adapters/sheets/read_only.py`'s documented
    fallback, which reads through the bot's existing credential when no
    read-only service account is configured.
    """
    offenders = []
    for path in sorted(ROOT.glob("application/**/*.py")) + sorted(
        ROOT.glob("domain/**/*.py")
    ):
        body = path.read_text(encoding="utf-8")
        if "connectors.sheets" in body or "from connectors import" in body:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def test_the_domain_layer_imports_no_infrastructure():
    for path in sorted(ROOT.glob("domain/**/*.py")):
        body = path.read_text(encoding="utf-8")
        for forbidden in (
            "import sqlalchemy",
            "from sqlalchemy",
            "import discord",
            "import googleapiclient",
            "from google",
            "import requests",
        ):
            assert forbidden not in body, f"{path.name} imports {forbidden}"
