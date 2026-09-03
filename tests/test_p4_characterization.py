"""Phase 4 WP-0 — characterization of the Sheet-era money and resource behaviour.

These tests pin **what the live bot does today**, before Phase 4 moves any of it
behind a shared application service. They are the reference the refactor is
measured against: if one of them fails after the refactor, the visible behaviour
changed, and that is a Phase 4 gate failure rather than a stale test.

**Several of these pin defects on purpose.** A characterization test is not an
endorsement. Where today's behaviour contradicts an accepted rule or invariant,
the test says so in its own docstring and names the decision record and the
package that owns the fix:

* **OD-49** — downtime is loaded as a Python ``float`` through ``safe_number``,
  while the accepted unit is the thousandth-day. A value with more precision
  than the unit is accepted silently, and an unparseable cell becomes ``0.0``.
  Phase 4's domain object refuses both; the *rendering* pinned here does not
  change, and package **5.5** owns column I's migration.
* **OD-50** — money is stored as four independent denomination counters, so two
  wallets holding the same value print differently. Phase 4 models money as
  integer copper and leaves these counters as a legacy representation; nothing
  normalizes them on read, which is what
  :func:`test_equal_value_wallets_print_differently` exists to guarantee.
* **OD-51** — ``Resource.sale`` and ``Lifestyle.pay_for_weeks`` compute money in
  binary floating point. Packages **5.7** and **5.3** own those fixes. Phase 4
  changes neither, and the existing coverage in ``tests/test_resource.py`` is
  their characterization.

``config`` and ``connectors.sheets`` are replaced in ``sys.modules`` for the
command tests, following ``tests/test_command_boundaries.py``: the real
``config`` reads ``.env``, and no test here may touch credentials or contact
Google.
"""
from __future__ import annotations

import asyncio
import sys
import types

import pytest

from helpers.renderers import render_actor_summary
from helpers.utils import safe_int, safe_number
from models.resource import Resource

GUILD_ID = 100000000000000003


# --------------------------------------------------------------------------- #
# 1. The visible output contract — what `/info` prints
# --------------------------------------------------------------------------- #


def test_summary_lists_only_strictly_positive_denominations():
    """Zero denominations are omitted, and the order is pp, gp, sp, cp."""
    resources = Resource(platinum=1, gold=2, silver=3, copper=4, moradinium=5)

    assert resources.get_summary() == (
        "**Money:** 1pp, 2gp, 3sp, 4cp\n"
        "**Moradinium:** 5"
    )


def test_a_negative_denomination_is_invisible_to_the_player():
    """A negative balance is *suppressed*, not shown and not refused.

    `get_summary` tests `> 0`, so a persisted negative gold balance simply does
    not appear. The player sees a wallet that omits it rather than a wallet that
    reports it. Pinned because Phase 4 must not change what is displayed; the
    typed domain object refuses to *construct* such a value, which is a
    different boundary.
    """
    resources = Resource(gold=-3, silver=2)

    assert resources.get_summary(include_moradinium=False) == "**Money:** 2sp"


def test_moradinium_is_unconditional_and_downtime_is_opt_in():
    resources = Resource(moradinium=0, downtime=10)

    assert resources.get_summary() == "**Moradinium:** 0"
    assert resources.get_summary(include_downtime=True) == (
        "**Moradinium:** 0\n"
        "**Downtime:** 10 days"
    )


def test_an_empty_wallet_renders_the_no_resources_sentinel():
    assert Resource().get_summary(include_moradinium=False) == "*No relevant resources.*"


def test_actor_summary_composition_and_the_conditional_bastion_line(actor_factory):
    """The exact `/info` body, with and without a Bastion.

    `render_actor_summary` delegates to `Actor.get_summary` whenever the object
    has one, so this pins both at once.
    """
    actor = actor_factory()

    assert render_actor_summary(actor) == (
        "**Name:** Testa Smith\n"
        "**Level:** 7\n"
        "**Badge:** Silver\n"
        "**Lifestyle:** Comfortable (Weeks open: 4)\n"
        "**Money:** 12gp, 3sp\n"
        "**Moradinium:** 2\n"
        "**Downtime:** 15.0 days"
    )
    assert render_actor_summary(actor) == actor.get_summary()

    actor.lifestyle.bastion.bastion_flag = 1
    actor.lifestyle.bastion.weeks_of_maintenance = 2

    assert render_actor_summary(actor) == (
        "**Name:** Testa Smith\n"
        "**Level:** 7\n"
        "**Badge:** Silver\n"
        "**Lifestyle:** Comfortable (Weeks open: 4)\n"
        "**Bastion:** Owned\n"
        "**Maintenance weeks open:** 2\n"
        "**Turn available:** False\n"
        "**Money:** 12gp, 3sp\n"
        "**Moradinium:** 2\n"
        "**Downtime:** 15.0 days"
    )


# --------------------------------------------------------------------------- #
# 2. OD-50 — the denomination counters are a representation, not a value
# --------------------------------------------------------------------------- #


def test_equal_value_wallets_print_differently():
    """**This is why OD-50 forbids normalizing coins on read.**

    Both wallets hold 100 copper. They print differently, so the visible output
    is *not derivable* from a copper total. Any Phase 4 change that canonicalizes
    denominations on the read path silently rewrites what many characters see,
    and this test is what catches it.
    """
    ten_silver = Resource(silver=10)
    one_gold = Resource(gold=1)

    assert ten_silver.get_summary(include_moradinium=False) == "**Money:** 10sp"
    assert one_gold.get_summary(include_moradinium=False) == "**Money:** 1gp"
    assert ten_silver.format_coins() == "10sp"
    assert one_gold.format_coins() == "1gp"


@pytest.mark.parametrize(
    ("wallet", "copper_total"),
    [
        (dict(silver=10), 100),
        (dict(gold=1), 100),
        (dict(copper=100), 100),
        (dict(platinum=1), 1000),
        (dict(gold=9, silver=9, copper=9), 999),
    ],
)
def test_the_copper_total_is_well_defined_even_though_the_rendering_is_not(
    wallet,
    copper_total,
):
    """The value Phase 4's `Money` will carry, independent of representation.

    `models/exchange.py` states the only conversion table the platform uses, and
    it agrees with `Money.from_denominations`. Pinned so that the typed copper
    total the new layer computes is checkable against today's counters.
    """
    resources = Resource(**wallet)
    total = (
        resources.platinum * 1000
        + resources.gold * 100
        + resources.silver * 10
        + resources.copper
    )

    assert total == copper_total


# --------------------------------------------------------------------------- #
# 3. OD-49 — the downtime unit, and silent coercion at the Sheet boundary
# --------------------------------------------------------------------------- #


def sheet_values(**overrides):
    """The `get_val` callable `load_from_sheet_data` expects."""
    values = {
        "downtime": "",
        "platinum": "",
        "gold": "",
        "silver": "",
        "copper": "",
        "moradinium": "",
    }
    values.update(overrides)
    return lambda key: values[key]


def test_downtime_is_loaded_as_a_float_and_rendered_as_one():
    """**Pins a defect.** OD-49; package 5.5 owns column I.

    The accepted unit is the thousandth-day, but the loader produces a Python
    `float`, so a whole number of days renders as `5.0 days` rather than
    `5 days`. Phase 4's typed quantity is an integer count of thousandth-days
    and refuses anything else — but the *rendering* pinned here must not change.
    """
    resources = Resource()
    resources.load_from_sheet_data(sheet_values(downtime="5"))

    assert resources.downtime == 5.0
    assert isinstance(resources.downtime, float)
    assert resources.get_summary(
        include_money=False,
        include_moradinium=False,
        include_downtime=True,
    ) == "**Downtime:** 5.0 days"


def test_downtime_beyond_the_accepted_unit_is_accepted_silently():
    """**Pins a defect.** OD-49.

    Four decimals is finer than the thousandth-day the platform accepts. Nothing
    refuses it, rounds it or reports it; it is simply carried. This is the value
    class the Phase 4 read model must mark as an invalid persisted value while
    still rendering what it renders today.
    """
    resources = Resource()
    resources.load_from_sheet_data(sheet_values(downtime="12.3456"))

    assert resources.downtime == 12.3456


def test_unparseable_persisted_values_become_defaults_without_a_report():
    """**Pins a defect.** `.agents/AGENTS.md` forbids silently coercing invalid
    persisted data; `safe_number`/`safe_int` do exactly that.

    A corrupt cell is indistinguishable from a genuinely empty one after the
    load. Phase 4 refuses these in the domain and marks them explicitly on the
    read model instead of inventing a zero.
    """
    resources = Resource()
    resources.load_from_sheet_data(sheet_values(downtime="not a number", platinum="x"))

    assert resources.downtime == 0.0
    assert resources.platinum == 0


@pytest.mark.parametrize(
    ("value", "expected"),
    [("3,5", 3.5), ("3.5", 3.5), ("", 0.0), (None, 0.0), ("  7 ", 7.0)],
)
def test_safe_number_accepts_a_comma_decimal_separator(value, expected):
    """The community's Sheet uses comma decimals; the loader normalizes them."""
    assert safe_number(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("7,9", 7), ("7.9", 7), ("", 0), (None, 0), (12, 12)],
)
def test_safe_int_truncates_rather_than_rounds(value, expected):
    """Truncation, not rounding: `7.9` becomes `7`. Pinned because a Phase 4
    conversion that rounds would change stored balances."""
    assert safe_int(value) == expected


# --------------------------------------------------------------------------- #
# 4. OD-52 — `/info`, the one command Phase 4 moves
# --------------------------------------------------------------------------- #


@pytest.fixture()
def info_command(monkeypatch):
    """Import the `/info` cog with configuration and Sheets stubbed."""
    config = types.ModuleType("config")
    config.GUILD_ID = GUILD_ID
    config.GUILD_IDS = [GUILD_ID]
    config.ROLL_CHANNEL_ID = 100000000000000004
    monkeypatch.setitem(sys.modules, "config", config)

    sheets = types.ModuleType("connectors.sheets")
    sheets.rows: list[list[object]] = []
    sheets.get_values = lambda *args, **kwargs: sheets.rows
    sheets.batch_update = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "connectors.sheets", sheets)

    from ext.commands import info

    return types.SimpleNamespace(module=info, sheets=sheets)


class FakeContext:
    """Just enough ApplicationContext to drive the `/info` callback."""

    def __init__(self) -> None:
        self.deferred = False
        self.followups: list[tuple[str, bool]] = []

    async def defer(self):
        self.deferred = True

    @property
    def followup(self):
        context = self

        class Followup:
            async def send(self, content, ephemeral=False):
                context.followups.append((content, ephemeral))

        return Followup()


class FakeBot:
    """A bot whose executor runs the callable inline, so tests stay synchronous."""

    def __init__(self) -> None:
        self.loop = self

    async def run_in_executor(self, _executor, function, *args):
        return function(*args)

    def get_channel(self, _id):
        return None


def sheet_row(**columns):
    """A `Characters` row built from `Actor.COLUMNS`, padded to column AL."""
    from helpers.utils import col_to_index
    from models.actor import Actor

    row = [""] * (col_to_index("AL") + 1)
    for field, value in columns.items():
        row[col_to_index(Actor.COLUMNS[field])] = value
    return row


def test_info_defers_then_sends_the_summary_non_ephemerally(info_command):
    """The whole visible contract of `/info`, end to end through the real loader.

    Deferred first, one follow-up, **not** ephemeral, and the body is exactly
    `render_actor_summary`. Every one of those is something Phase 4 must
    preserve: name, response timing, error safety and visible result.
    """
    info_command.sheets.rows = [
        sheet_row(
            name="Testa Smith",
            level=7,
            badge="Silver",
            lifestyle="comfortable",
            living_weeks=4,
            gold=12,
            silver=3,
            moradinium=2,
            downtime=15,
        )
    ]
    cog = info_command.module.Info(FakeBot())
    ctx = FakeContext()

    asyncio.run(info_command.module.Info.info.callback(cog, ctx, actor_name="Testa Smith"))

    assert ctx.deferred is True
    assert ctx.followups == [
        (
            "**Name:** Testa Smith\n"
            "**Level:** 7\n"
            "**Badge:** Silver\n"
            "**Lifestyle:** Comfortable (Weeks open: 4)\n"
            "**Money:** 12gp, 3sp\n"
            "**Moradinium:** 2\n"
            "**Downtime:** 15.0 days",
            False,
        )
    ]


def test_info_reports_an_unknown_character_ephemerally(info_command):
    info_command.sheets.rows = []
    cog = info_command.module.Info(FakeBot())
    ctx = FakeContext()

    asyncio.run(info_command.module.Info.info.callback(cog, ctx, actor_name="Nobody"))

    assert ctx.deferred is True
    assert ctx.followups == [
        ("Actor 'Nobody' could not be found in the records.", True)
    ]


def test_info_refuses_an_ambiguous_name_rather_than_guessing(info_command):
    """`AmbiguousActorError` is a `ValueError`, so `/info` reports it safely.

    Pinned because the refusal is a rule (OD-42: a display name is not an
    identity), and because the message names the rows, which the refactor must
    not turn into an internal-detail leak or a generic error.
    """
    info_command.sheets.rows = [
        sheet_row(name="Twin", level=1),
        sheet_row(name="Twin", level=2),
    ]
    cog = info_command.module.Info(FakeBot())
    ctx = FakeContext()

    asyncio.run(info_command.module.Info.info.callback(cog, ctx, actor_name="Twin"))

    message, ephemeral = ctx.followups[0]
    assert ephemeral is True
    assert "More than one character is recorded under 'Twin'" in message
    assert "rows 3, 4" in message


def test_info_matches_a_name_case_insensitively(info_command):
    info_command.sheets.rows = [sheet_row(name="Testa Smith", level=3, badge="Bronze")]
    cog = info_command.module.Info(FakeBot())
    ctx = FakeContext()

    asyncio.run(info_command.module.Info.info.callback(cog, ctx, actor_name="  testa smith  "))

    message, ephemeral = ctx.followups[0]
    assert ephemeral is False
    assert message.startswith("**Name:** Testa Smith\n**Level:** 3\n**Badge:** Bronze")


def test_info_writes_nothing(info_command, monkeypatch):
    """`/info` is read-only, and stays read-only after Phase 4.

    **Watching `batch_update` alone is not enough**, and this test originally
    made that mistake. `Actor.save_to_sheet` diffs against the cells it loaded
    and returns before calling `batch_update` when nothing changed — so a
    `save_to_sheet()` injected into `/info` reaches no Sheets API and a test
    watching only the API passes. Verified by deliberately injecting that call:
    the weaker assertion did not notice.

    So both are watched: every write *path* on the model, and the Sheets API
    itself. Either one being touched fails the test.
    """
    from models.actor import Actor

    invoked: list[str] = []
    monkeypatch.setattr(
        Actor, "save_to_sheet", lambda self: invoked.append("save_to_sheet")
    )
    monkeypatch.setattr(
        Actor, "sheet_updates", lambda self: invoked.append("sheet_updates") or []
    )
    monkeypatch.setattr(
        Actor, "verify_sheet_row", lambda self: invoked.append("verify_sheet_row")
    )
    info_command.sheets.batch_update = lambda *args, **kwargs: invoked.append(
        "batch_update"
    )
    info_command.sheets.rows = [sheet_row(name="Testa Smith", level=1)]
    cog = info_command.module.Info(FakeBot())
    ctx = FakeContext()

    asyncio.run(info_command.module.Info.info.callback(cog, ctx, actor_name="Testa Smith"))

    assert invoked == []
    assert len(ctx.followups) == 1


# --------------------------------------------------------------------------- #
# 5. Refusal behaviour the new layer must keep
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("downtime", [0, 3, 7, 61])
def test_validate_downtime_requires_five_day_increments(downtime):
    resources = Resource(downtime=100)

    with pytest.raises(ValueError):
        resources.validate_downtime(downtime)


def test_validate_downtime_reports_the_available_balance():
    resources = Resource(downtime=5)

    with pytest.raises(ValueError, match="Not enough downtime available: 5 days."):
        resources.validate_downtime(10)


def test_deduct_refuses_insufficient_moradinium_without_mutating():
    resources = Resource(gold=5, moradinium=1)

    with pytest.raises(ValueError, match="Not enough Moradinium to pay."):
        resources.deduct(moradinium=2)

    assert (resources.gold, resources.moradinium) == (5, 1)


def test_add_refuses_a_result_that_would_go_negative():
    resources = Resource(gold=1)

    with pytest.raises(ValueError, match="Resulting gold cannot be negative."):
        resources.add(gold=-2)

    assert resources.gold == 1


@pytest.fixture()
def actor_factory(monkeypatch):
    """An `Actor` populated without touching Sheets or configuration."""
    config = types.ModuleType("config")
    config.GUILD_ID = GUILD_ID
    config.GUILD_IDS = [GUILD_ID]
    config.ROLL_CHANNEL_ID = 100000000000000004
    monkeypatch.setitem(sys.modules, "config", config)

    def build():
        from models.actor import Actor

        actor = Actor("Testa Smith")
        actor.level = 7
        actor.badge = "Silver"
        actor.lifestyle.lifestyle_type = "comfortable"
        actor.lifestyle.living_weeks = 4
        actor.resources.gold = 12
        actor.resources.silver = 3
        actor.resources.moradinium = 2
        actor.resources.downtime = 15.0
        return actor

    return build
