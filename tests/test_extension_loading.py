"""Startup fails closed when a required extension does not load.

`main.py` is not imported here: importing it reads `config`, which reads `.env`,
and no test in this repository may touch credentials. The loader is the unit
that decides, and `main.EXTENSIONS` is read out of the source with `ast`, the
same technique `tests/test_fixtures.py` uses for `Actor.COLUMNS`.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ext.loader import ExtensionLoadError, load_required_extensions

REPO_ROOT = Path(__file__).resolve().parent.parent


class FakeBot:
    """Records what was loaded, and fails for the extensions it is told to."""

    def __init__(self, failing: set[str] | None = None) -> None:
        self.loaded: list[str] = []
        self.failing = failing or set()

    def load_extension(self, name: str) -> None:
        if name in self.failing:
            raise ImportError(f"cannot import {name}")
        self.loaded.append(name)


def _main_extensions() -> list[str]:
    tree = ast.parse((REPO_ROOT / "main.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "EXTENSIONS"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("EXTENSIONS not found in main.py")


def test_every_extension_loads_when_none_fail():
    bot = FakeBot()

    loaded = load_required_extensions(bot, ["ext.error_handler", "ext.commands.info"])

    assert loaded == ["ext.error_handler", "ext.commands.info"]
    assert bot.loaded == loaded


def test_a_failing_extension_stops_startup_instead_of_being_logged_and_ignored():
    bot = FakeBot(failing={"ext.commands.trade"})

    with pytest.raises(ExtensionLoadError) as raised:
        load_required_extensions(
            bot, ["ext.error_handler", "ext.commands.trade", "ext.commands.sale"]
        )

    assert raised.value.extension == "ext.commands.trade"
    # Loading stops at the failure; nothing after it is half-registered.
    assert bot.loaded == ["ext.error_handler"]


def test_a_failing_error_handler_stops_startup():
    """The safety extension specifically: without it, raw errors reach Discord."""
    bot = FakeBot(failing={"ext.error_handler"})

    with pytest.raises(ExtensionLoadError):
        load_required_extensions(bot, ["ext.error_handler", "ext.commands.info"])

    assert bot.loaded == []


def test_the_error_handler_is_among_the_required_extensions():
    assert "ext.error_handler" in _main_extensions()


def test_the_extension_load_error_names_the_extension_and_not_the_cause():
    """The operator log gets the traceback; the message stays short and specific."""
    error = ExtensionLoadError("ext.commands.craft")

    assert "ext.commands.craft" in str(error)
    assert "Refusing to start" in str(error)
