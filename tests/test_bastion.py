import pytest

from models.bastion import Bastion, get_level_group
from models.resource import Resource


# Homebrew rules 7.1 (PDF p.29-30): maximum special facilities by level band
# and lifestyle. Wretched and modest cannot sustain a bastion at any level.
EXPECTED_LIMITS = [
    (4, "comfortable", 0),
    (4, "wealthy", 0),
    (4, "aristocratic", 0),
    (5, "comfortable", 1),
    (5, "wealthy", 2),
    (5, "aristocratic", 3),
    (8, "aristocratic", 3),
    (9, "comfortable", 2),
    (9, "wealthy", 4),
    (9, "aristocratic", 5),
    (13, "comfortable", 3),
    (13, "wealthy", 5),
    (13, "aristocratic", 6),
    (17, "comfortable", 4),
    (17, "wealthy", 6),
    (20, "aristocratic", 7),
]


@pytest.mark.parametrize("level, lifestyle, expected", EXPECTED_LIMITS)
def test_special_facility_limits_match_the_rules_table(level, lifestyle, expected):
    bastion = Bastion(lifestyle_type=lifestyle)

    assert bastion.get_max_special_facilities(level) == expected


@pytest.mark.parametrize("lifestyle", ["wretched", "modest"])
@pytest.mark.parametrize("level", [1, 5, 9, 13, 17, 20])
def test_lifestyles_below_comfortable_allow_no_special_facilities(lifestyle, level):
    bastion = Bastion(lifestyle_type=lifestyle)

    assert bastion.get_max_special_facilities(level) == 0


def test_unrecognised_lifestyle_grants_no_allowance():
    """An unparseable lifestyle cell is a data error, not an allowance."""
    bastion = Bastion(lifestyle_type="gilded")

    assert bastion.get_max_special_facilities(10) == 0


@pytest.mark.parametrize(
    "level, expected",
    [(1, (1, 4)), (4, (1, 4)), (5, (5, 8)), (12, (9, 12)), (16, (13, 16)), (20, (17, 20))],
)
def test_level_groups(level, expected):
    assert get_level_group(level) == expected


def test_maintenance_charges_five_gold_per_facility_week():
    """Homebrew rules 5.3-5.5 (PDF p.13): 5gp per special facility per week."""
    bastion = Bastion(lifestyle_type="aristocratic")
    bastion.bastion_flag = 1
    bastion.turn_available_flag = 1
    bastion.weeks_of_maintenance = 2
    resources = Resource(gold=100)

    cost = bastion.maintain_bastion(resources, level=6)

    # Levels 5-8 aristocratic allows 3 special facilities: 2 weeks * 3 * 5gp.
    assert cost == 30
    assert resources.gold == 70
    assert bastion.weeks_of_maintenance == 0
    assert bastion.turn_available_flag == 0


def test_maintenance_requires_an_available_turn():
    bastion = Bastion(lifestyle_type="wealthy")
    bastion.bastion_flag = 1
    bastion.turn_available_flag = 0
    bastion.weeks_of_maintenance = 1
    resources = Resource(gold=100)

    with pytest.raises(ValueError, match="No bastion turn"):
        bastion.maintain_bastion(resources, level=10)

    assert resources.gold == 100


def test_maintenance_requires_an_owned_bastion():
    bastion = Bastion(lifestyle_type="wealthy")
    resources = Resource(gold=100)

    with pytest.raises(ValueError, match="No bastion"):
        bastion.maintain_bastion(resources, level=10)


def test_insufficient_gold_leaves_bastion_state_untouched():
    bastion = Bastion(lifestyle_type="aristocratic")
    bastion.bastion_flag = 1
    bastion.turn_available_flag = 1
    bastion.weeks_of_maintenance = 4
    resources = Resource(gold=5)

    with pytest.raises(ValueError, match="Not enough currency"):
        bastion.maintain_bastion(resources, level=20)

    assert resources.gold == 5
    assert bastion.weeks_of_maintenance == 4
    assert bastion.turn_available_flag == 1
