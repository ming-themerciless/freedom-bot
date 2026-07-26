from models import resource as resource_module
from models.resource import Resource


def test_natural_twenty_earnings_preserve_half_gold(monkeypatch):
    monkeypatch.setattr(resource_module, "roll_dice", lambda *args, **kwargs: ([20], 20))
    resources = Resource(downtime=5)

    rolls = resources.earn_money(bot=None, downtime=5)

    assert rolls == [(20, 20, 42.0)]
    assert resources.gold == 42
    assert resources.silver == 0
    assert resources.downtime == 0


def test_natural_twenty_preserves_fractional_coin(monkeypatch):
    monkeypatch.setattr(resource_module, "roll_dice", lambda *args, **kwargs: ([20], 10))
    resources = Resource(downtime=5)

    resources.earn_money(bot=None, downtime=5)

    assert resources.gold == 10
    assert resources.silver == 5
    assert resources.copper == 0
