"""Command-boundary tests for the behaviour this change altered.

Scope, deliberately: only `/sale` and `/trade`, and only the paths this work
touched — input validation, and what a caller is told when the Sheet write is
refused. There is no general command-test framework here and none is wanted;
each of these constructs the cog directly and calls its callback.

**What these tests cannot cover, and why.** There is no "unauthorized caller
denied" test, because there is nothing to deny with: no command in this
repository establishes whether the caller may act for the named character.
`character_access` exists as a table with no rows and no writer, and the
Discord→character identity link is Phase 3 work. A test asserting the current
behaviour would pin the gap rather than close it. It is reported as a blocking
finding in `docs/review/phase-2-submission.md` instead, with the test design the
eventual boundary needs.

`config` and `connectors.sheets` are both replaced in `sys.modules`: the real
`config` reads `.env`, and no test here may touch credentials.
"""
from __future__ import annotations

import asyncio
import sys
import types

import pytest

TRADE_CHANNEL_ID = 100000000000000001
DT_CHANNEL_ID = 100000000000000002
GUILD_ID = 100000000000000003


@pytest.fixture()
def command_modules(monkeypatch):
    """Import the sale and trade cogs with configuration and Sheets stubbed."""
    config = types.ModuleType("config")
    config.TRADE_CHANNEL_ID = TRADE_CHANNEL_ID
    config.DT_CHANNEL_ID = DT_CHANNEL_ID
    config.GUILD_ID = GUILD_ID
    config.GUILD_IDS = [GUILD_ID]
    config.ROLL_CHANNEL_ID = 100000000000000004
    monkeypatch.setitem(sys.modules, "config", config)

    sheets = types.ModuleType("connectors.sheets")
    sheets.get_values = lambda *args, **kwargs: []
    sheets.batch_update = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "connectors.sheets", sheets)

    from application.actor_locks import ActorLockManager
    from ext.commands import sale, trade

    # A fresh manager per test: an `asyncio.Lock` binds to the first loop that
    # awaits it, and each test here runs on its own `asyncio.run` loop.
    for module in (sale, trade):
        monkeypatch.setattr(module, "actor_locks", ActorLockManager())

    return types.SimpleNamespace(sale=sale, trade=trade, sheets=sheets)


class FakeResponse:
    def __init__(self) -> None:
        self._done = False

    def is_done(self) -> bool:
        return self._done


class FakeContext:
    """Just enough ApplicationContext to drive a command callback."""

    def __init__(self, channel_id: int) -> None:
        self.channel = types.SimpleNamespace(id=channel_id)
        self.author = types.SimpleNamespace(roles=[])
        self.interaction = types.SimpleNamespace(id=987654321)
        self.response = FakeResponse()
        self.replies: list[tuple[str, bool]] = []
        self.followups: list[tuple[str, bool]] = []
        self.deferred = False

    async def respond(self, content, ephemeral=False):
        self.replies.append((content, ephemeral))

    async def defer(self):
        self.deferred = True
        self.response._done = True

    @property
    def followup(self):
        context = self

        class Followup:
            async def send(self, content, ephemeral=False):
                context.followups.append((content, ephemeral))

        return Followup()

    def messages(self) -> list[str]:
        return [content for content, _ in self.replies + self.followups]


class FakeBot:
    """A bot whose executor runs the callable inline, so tests stay synchronous."""

    def __init__(self) -> None:
        self.loop = self

    async def run_in_executor(self, _executor, function, *args):
        return function(*args)

    def get_channel(self, _id):
        return None


def call(command, cog, ctx, **kwargs):
    """Invoke a slash command's callback on a fresh event loop.

    `asyncio.run` per test, and a fresh `ActorLockManager` wherever a command
    takes a lock, matching `tests/test_actor_locks.py`: an `asyncio.Lock` binds
    to the first loop that awaits it, so a module-level manager cannot be shared
    across loops.
    """
    return asyncio.run(command.callback(cog, ctx, **kwargs))


# --------------------------------------------------------------------------- #
# /sale input validation
# --------------------------------------------------------------------------- #


def sale_arguments(**overrides):
    arguments = {
        "actor_name": "Test Smith A",
        "item": "Test Trinket",
        "crafting_cost": 10.0,
        "point_of_sale": "general store",
        "quantity": 1,
        "persuasion_modifier": 0,
        "material": 0,
    }
    arguments.update(overrides)
    return arguments


def test_sale_outside_the_trade_channel_is_refused(command_modules):
    cog = command_modules.sale.Retail(FakeBot())
    ctx = FakeContext(channel_id=DT_CHANNEL_ID)

    call(command_modules.sale.Retail.retail, cog, ctx, **sale_arguments())

    assert ctx.replies and ctx.replies[0][1] is True
    assert not ctx.deferred


@pytest.mark.parametrize("cost", [float("inf"), float("-inf"), float("nan")])
def test_a_non_finite_cost_is_refused_before_any_money_is_calculated(
    command_modules, cost
):
    """`nan < 0` is False, so without this check they reached the money code."""
    cog = command_modules.sale.Retail(FakeBot())
    ctx = FakeContext(channel_id=TRADE_CHANNEL_ID)

    call(
        command_modules.sale.Retail.retail, cog, ctx, **sale_arguments(crafting_cost=cost)
    )

    assert ctx.messages() == ["Cost must be a finite number."]
    assert not ctx.deferred


@pytest.mark.parametrize(
    ("field", "value"),
    [("crafting_cost", -1.0), ("quantity", 0), ("quantity", -3), ("material", -5)],
)
def test_negative_and_zero_quantities_are_still_refused(
    command_modules, field, value
):
    cog = command_modules.sale.Retail(FakeBot())
    ctx = FakeContext(channel_id=TRADE_CHANNEL_ID)

    call(
        command_modules.sale.Retail.retail, cog, ctx, **sale_arguments(**{field: value})
    )

    assert ctx.messages()
    assert not ctx.deferred


# --------------------------------------------------------------------------- #
# A refused Sheet write is never reported as a completed sale
# --------------------------------------------------------------------------- #


def test_a_stale_row_refuses_the_sale_instead_of_reporting_success(
    command_modules, monkeypatch
):
    """The row moved under the character, so the write is refused.

    The caller must be told the sale did not happen. Reporting the rendered
    total while nothing was written would leave the player believing they hold
    money the Sheet does not show.
    """
    from models.actor import StaleSheetRowError

    class StaleActor:
        def __init__(self, name):
            self.name = name
            self.resources = _RecordingResources()

        def load_from_sheet(self):
            return None

        def save_to_sheet(self):
            raise StaleSheetRowError(
                "The records moved while this action was in progress, so nothing "
                "was changed. Please try again."
            )

    monkeypatch.setattr(command_modules.sale, "Actor", StaleActor)
    cog = command_modules.sale.Retail(FakeBot())
    ctx = FakeContext(channel_id=TRADE_CHANNEL_ID)

    call(command_modules.sale.Retail.retail, cog, ctx, **sale_arguments())

    messages = ctx.messages()
    assert any("moved while this action was in progress" in text for text in messages)
    assert not any("has sold items" in text for text in messages)
    # The refusal is ephemeral: it names a character and its records.
    assert all(ephemeral for _, ephemeral in ctx.followups)


class _RecordingResources:
    def sale(self, **kwargs):
        return "sold"

    def get_summary(self, **kwargs):
        return ""


# --------------------------------------------------------------------------- #
# /trade: the channel check is not an authorization check
# --------------------------------------------------------------------------- #


def test_trade_outside_the_trade_channel_is_refused(command_modules):
    cog = command_modules.trade.TradeCmd(FakeBot())
    ctx = FakeContext(channel_id=DT_CHANNEL_ID)

    call(
        command_modules.trade.TradeCmd.trade,
        cog,
        ctx,
        buyer_name="Shop",
        seller_name="Test Smith A",
        good="Goods",
        platinum=0,
        gold=100,
        silver=0,
        copper=0,
        moradinium=0,
    )

    assert ctx.replies and ctx.replies[0][1] is True
    assert not ctx.deferred


def test_trade_rejects_negative_currency_before_deferring(command_modules):
    cog = command_modules.trade.TradeCmd(FakeBot())
    ctx = FakeContext(channel_id=TRADE_CHANNEL_ID)

    call(
        command_modules.trade.TradeCmd.trade,
        cog,
        ctx,
        buyer_name="Test Smith A",
        seller_name="Test Smith B",
        good="Goods",
        platinum=0,
        gold=-1,
        silver=0,
        copper=0,
        moradinium=0,
    )

    assert ctx.messages() == [
        "Currency values (platinum, gold, silver, copper) cannot be negative."
    ]
    assert not ctx.deferred
