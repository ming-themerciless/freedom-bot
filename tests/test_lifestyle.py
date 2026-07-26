import pytest

from models.lifestyle import Lifestyle
from models.resource import Resource


def test_lifestyle_payment_deducts_exact_expenses_and_grants_downtime():
    lifestyle = Lifestyle("modest")
    lifestyle.living_weeks = 2
    resources = Resource(gold=20, downtime=55)

    weekly_cost, expenses = lifestyle.pay_for_weeks(
        resources,
        weeks=1,
        extra_expenses_sp=3.5,
    )

    assert weekly_cost == 7
    assert expenses == (0, 3, 5)
    assert (resources.gold, resources.silver, resources.copper) == (12, 6, 5)
    assert resources.downtime == 60
    assert lifestyle.living_weeks == 1


def test_failed_lifestyle_payment_preserves_weeks_and_resources():
    lifestyle = Lifestyle("aristocratic")
    lifestyle.living_weeks = 1
    resources = Resource(gold=10, downtime=5)

    with pytest.raises(ValueError, match="Not enough currency"):
        lifestyle.pay_for_weeks(resources, weeks=1)

    assert lifestyle.living_weeks == 1
    assert resources.gold == 10
    assert resources.downtime == 5


def test_final_paid_week_unlocks_owned_bastion_turn():
    lifestyle = Lifestyle("wretched")
    lifestyle.living_weeks = 1
    lifestyle.bastion.bastion_flag = 1
    resources = Resource()

    lifestyle.pay_for_weeks(resources, weeks=1)

    assert lifestyle.bastion.turn_available_flag == 1
