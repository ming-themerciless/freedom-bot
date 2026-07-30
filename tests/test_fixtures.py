"""Validation of the Phase 0 synthetic fixtures.

The fixtures are a Phase 0 deliverable (plan section 12, "anonymized fixtures").
These tests are what makes them *validated* rather than merely present: they pin
the fixtures to the structural documentation verified on 2026-07-30
(docs/discovery/sheet-inventory.md section 3 and docs/discovery/foundry-mapping.md
section 4) and to the synthetic-by-construction rules in
docs/discovery/fixture-strategy.md.

`Actor.COLUMNS` is read out of the source with `ast` rather than imported,
because importing `models.actor` pulls in `connectors.sheets` and `config`, which
read `.env`. No test in this repository may touch credentials.
"""
from __future__ import annotations

import ast
import csv
import json
import re
from pathlib import Path

import pytest

from models.skills import Skills

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "tests" / "fixtures"

# The real Characters headers, supplied by the maintainer 2026-07-30 and recorded
# in docs/discovery/sheet-inventory.md section 3. Column letters run A..AL.
EXPECTED_SHEET_HEADERS = [
    "Character Name (short)",
    "Character Name (long)",
    "Player Name",
    "Inspiration Coin",
    "Badge",
    "Character Level",
    "Experience (Missions)",
    "Last Time Played",
    "Downtime (In days)",
    "Lifestyle Costs (In Weeks)",
    "Bastion flag",
    "Bastion maintenance (in weeks)",
    "Bastion turn flag",
    "Lifestyle",
    "Aristocratic lifestyle flag",
    "Platinum",
    "Gold",
    "Silver",
    "Copper",
    "Moradinium",
    "Weekly Expenses",
    "Downtime Progress",
    "CRP",
    "Crafting Skills",
    "Tool Proficiencies",
    "Languages",
    "Notable Items",
    "Masterpiece",
    "Frank",
    "Background",
    "Classes/Subclasses",
    "Race/Species",
    "Abilities (STR/DEX/CON/INT/WIS/CHA)",
    "Feats/ASIs",
    "Special Notes",
    "Mounts",
    "No shows",
    "Active",
]

# Header text the code's field key is expected to sit under, per sheet-inventory
# section 3. Only the columns Actor.COLUMNS maps are listed.
FIELD_KEY_HEADERS = {
    "name": "Character Name (short)",
    "inspiration": "Inspiration Coin",
    "badge": "Badge",
    "level": "Character Level",
    "missions": "Experience (Missions)",
    "last_played": "Last Time Played",
    "downtime": "Downtime (In days)",
    "living_weeks": "Lifestyle Costs (In Weeks)",
    "bastion_flag": "Bastion flag",
    "bastion_maintenance": "Bastion maintenance (in weeks)",
    "bastion_turn_flag": "Bastion turn flag",
    "lifestyle": "Lifestyle",
    "aristocratic_flag": "Aristocratic lifestyle flag",
    "platinum": "Platinum",
    "gold": "Gold",
    "silver": "Silver",
    "copper": "Copper",
    "moradinium": "Moradinium",
    "downtime_progress": "Downtime Progress",
    "crp": "CRP",
    "skills": "Crafting Skills",
    "proficiencies": "Tool Proficiencies",
    "languages": "Languages",
    "notable_items": "Notable Items",
    "masterpiece": "Masterpiece",
    "debt": "Frank",
    "no_shows": "No shows",
    "active_flag": "Active",
}


def _column_letter_to_index(letter: str) -> int:
    index = 0
    for char in letter.upper():
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def _actor_columns() -> dict[str, str]:
    """Read Actor.COLUMNS from source without importing config or the Sheets client."""
    tree = ast.parse((REPO_ROOT / "models" / "actor.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Actor":
            for statement in node.body:
                if isinstance(statement, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id == "COLUMNS"
                    for target in statement.targets
                ):
                    return ast.literal_eval(statement.value)
    raise AssertionError("Actor.COLUMNS not found in models/actor.py")


@pytest.fixture(scope="module")
def sheet_rows() -> list[list[str]]:
    with (FIXTURES / "sheet_characters_sample.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


@pytest.fixture(scope="module")
def sheet_characters(sheet_rows) -> list[dict[str, str]]:
    """Data rows keyed by header, skipping the two header rows the live sheet has."""
    header = sheet_rows[0]
    return [dict(zip(header, row)) for row in sheet_rows[2:]]


@pytest.fixture(scope="module")
def foundry_actor() -> dict:
    return json.loads((FIXTURES / "foundry_actor_sample.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def foundry_anomalies() -> dict:
    return json.loads((FIXTURES / "foundry_actor_anomalies.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Sheet fixture: structure
# --------------------------------------------------------------------------- #

def test_sheet_fixture_carries_the_verified_header_row(sheet_rows):
    assert sheet_rows[0] == EXPECTED_SHEET_HEADERS


def test_sheet_fixture_rows_are_all_38_columns_wide(sheet_rows):
    widths = {len(row) for row in sheet_rows}
    assert widths == {38}


def test_second_row_is_a_header_spacer_so_data_starts_where_the_bot_reads(sheet_rows):
    # The live read range is Characters!A3:AL150, so rows 1-2 are headers.
    assert sheet_rows[1][0].startswith("SYNTHETIC FIXTURE")
    assert all(cell == "" for cell in sheet_rows[1][1:])


def test_every_mapped_field_key_sits_under_its_real_header(sheet_rows):
    header = sheet_rows[0]
    for field_key, letter in _actor_columns().items():
        expected = FIELD_KEY_HEADERS[field_key]
        assert header[_column_letter_to_index(letter)] == expected, (
            f"{field_key} maps to column {letter}, which must be {expected!r}"
        )


def test_the_columns_the_bot_never_maps_are_still_populated(sheet_characters):
    """The ten unmapped columns are known since 2026-07-30 and Phase 2 imports them."""
    unmapped_headers = [
        "Character Name (long)",
        "Player Name",
        "Weekly Expenses",
        "Background",
        "Classes/Subclasses",
        "Race/Species",
        "Abilities (STR/DEX/CON/INT/WIS/CHA)",
        "Feats/ASIs",
        "Special Notes",
        "Mounts",
    ]
    for header in unmapped_headers:
        assert any(row[header].strip() for row in sheet_characters), (
            f"no fixture row exercises {header!r}"
        )


# --------------------------------------------------------------------------- #
# Sheet fixture: synthetic-by-construction rules (fixture-strategy sections 2-3)
# --------------------------------------------------------------------------- #

def test_every_character_name_uses_the_reserved_form(sheet_characters):
    for row in sheet_characters:
        assert row["Character Name (short)"].lower().startswith("test "), row

def test_every_player_name_uses_the_reserved_handle_form(sheet_characters):
    pattern = re.compile(r"^testplayer\d{2}$")
    for row in sheet_characters:
        value = row["Player Name"].strip()
        assert value == "" or pattern.match(value), value


@pytest.mark.parametrize(
    "fixture_name",
    ["sheet_characters_sample.csv", "foundry_actor_sample.json", "foundry_actor_anomalies.json"],
)
def test_no_fixture_contains_a_real_looking_snowflake(fixture_name):
    """Real Discord snowflakes are 1.1-1.5e18.

    The reserved ranges in fixture-strategy.md section 3 sit at 1e17-4e17, an order of
    magnitude below, so anything at or above 1e18 in a fixture is a finding.
    """
    text = (FIXTURES / fixture_name).read_text(encoding="utf-8")
    for candidate in re.findall(r"\d{15,20}", text):
        assert int(candidate) < 10**18, f"{candidate} in {fixture_name} looks like a real ID"


# --------------------------------------------------------------------------- #
# Sheet fixture: the column W formats, parsed by the real adapter code path
# --------------------------------------------------------------------------- #

def _load_crp(cell: str) -> Skills:
    skills = Skills()
    cells = {"crp": cell, "skills": "", "proficiencies": "", "languages": "", "downtime_progress": ""}
    skills.load_from_sheet_data(cells.get)
    return skills


def _crp_cell(sheet_characters, name: str) -> str:
    for row in sheet_characters:
        if row["Character Name (short)"] == name:
            return row["CRP"]
    raise AssertionError(f"fixture row {name!r} is missing")


def test_canonical_crp_form_parses_per_tool(sheet_characters):
    cell = _crp_cell(sheet_characters, "Test Alchemist B")
    assert cell == "62.5 (Alchemist), 5 (Smith)"
    assert _load_crp(cell).crp_dict == {"alchemist": 62.5, "smith": 5}


def test_canonical_crp_form_with_a_comma_decimal_parses(sheet_characters):
    cell = _crp_cell(sheet_characters, "Test Miner E")
    assert cell == "7,5 (Brewer)"
    assert _load_crp(cell).crp_dict == {"brewer": 7.5}


def test_legacy_colon_crp_form_is_still_covered(sheet_characters):
    # Both notations coexist in the live sheet by design (OD-34, 2026-07-30).
    cell = _crp_cell(sheet_characters, "Test Jeweler G")
    assert _load_crp(cell).crp_dict == {"jeweler": 92.5, "painter": 7.5}


def test_abbreviated_artisan_resolves_to_zero_and_the_fixture_records_it(sheet_characters):
    cell = _crp_cell(sheet_characters, "Test Scribe L")
    assert cell == "120 (Calligraph)"
    skills = _load_crp(cell)
    assert skills.crp_dict == {"calligraph": 120}
    # OD-06: the abbreviation matches no canonical artisan, silently (pinned, not fixed).
    assert skills.get_tool_crp("Calligrapher's Supplies") == 0.0


def test_untagged_legacy_total_is_covered(sheet_characters):
    skills = _load_crp(_crp_cell(sheet_characters, "Test Cook F"))
    assert skills.crp_dict == {"general": 12}


def test_mastered_tool_literal_is_covered(sheet_characters):
    skills = _load_crp(_crp_cell(sheet_characters, "Test Master H"))
    assert skills.crp == "Master"
    assert skills.crp_dict == {}


def test_unparseable_crp_cell_is_covered(sheet_characters):
    skills = _load_crp(_crp_cell(sheet_characters, "Test Malformed Q"))
    assert skills.crp_dict == {}


# --------------------------------------------------------------------------- #
# Foundry fixture: the shape verified against two real exports (F-F1 to F-F5)
# --------------------------------------------------------------------------- #

def test_export_shape_has_no_actor_id_in_the_document(foundry_actor):
    # F-F1: a manual export carries "_id": null; the real ID is only in the filename.
    assert foundry_actor["_id"] is None
    assert foundry_actor["_fixture_export_filename"].startswith("fvtt-Actor-")


def test_derived_values_are_absent_rather_than_precomputed(foundry_actor):
    system = foundry_actor["system"]
    # F-F2
    for ability in system["abilities"].values():
        assert set(ability) == {"value"}
    assert "prof" not in system["attributes"]
    assert system["attributes"]["hp"]["max"] is None
    assert system["attributes"]["ac"]["flat"] is None
    assert "level" not in system["details"]


def test_character_level_must_be_summed_from_class_items(foundry_actor):
    classes = [item for item in foundry_actor["items"] if item["type"] == "class"]
    assert classes
    assert sum(item["system"]["levels"] for item in classes) == 9
    for item in classes:
        assert item["system"]["identifier"], "map on identifier, never on the display name"


def test_tools_are_keyed_by_artisan_with_the_three_documented_aliases(foundry_actor):
    tools = foundry_actor["system"]["tools"]
    aliases = foundry_actor["_fixture_expected_mapping"]["tool_vocabulary"]
    assert "alchemist" in tools and "calligrapher" in tools  # F-F3: shared vocabulary
    for alias in ("scrolls", "disg", "lute"):
        assert alias in tools
        assert alias in aliases
    # value 2 is expertise; Freedom Blades has three ranks, so rank cannot round-trip.
    assert tools["alchemist"]["value"] == 2


def test_bastion_is_represented_natively(foundry_actor):
    # F-F4
    assert foundry_actor["system"]["bastion"]["name"]
    facilities = [item for item in foundry_actor["items"] if item["type"] == "facility"]
    assert len(facilities) >= 3
    subtypes = {item["system"]["type"]["subtype"] for item in facilities}
    assert "" in subtypes, "a homebrew facility with an empty subtype must be covered"
    assert {"basic", "special"} <= {item["system"]["type"]["value"] for item in facilities}


def test_no_actor_holds_electrum_in_the_normal_fixture(foundry_actor):
    assert foundry_actor["system"]["currency"]["ep"] == 0


def test_the_export_carries_no_foundry_user_identity(foundry_actor):
    assert foundry_actor["ownership"] == {"default": 0}
    assert foundry_actor["_stats"]["lastModifiedBy"] is None


def test_homebrew_and_rarity_coverage(foundry_actor):
    rarities = {
        item["system"].get("rarity")
        for item in foundry_actor["items"]
        if item["type"] in {"equipment", "weapon"}
    }
    assert {"rare", "common", "uncommon"} <= rarities


def test_expected_mapping_declares_a_reserved_actor_id(foundry_actor):
    mapping = foundry_actor["_fixture_expected_mapping"]
    assert re.fullmatch(r"TESTACTOR\d{6}", mapping["external_actor_id"])


# --------------------------------------------------------------------------- #
# Foundry anomaly fixture: the two cases that must fail rather than import
# --------------------------------------------------------------------------- #

def test_anomaly_fixture_holds_nonzero_electrum(foundry_anomalies):
    assert foundry_anomalies["system"]["currency"]["ep"] > 0


def test_anomaly_fixture_holds_an_unsupported_version_tuple(foundry_anomalies):
    stats = foundry_anomalies["_stats"]
    assert (stats["coreVersion"], stats["systemVersion"]) != ("14.365", "5.3.3")
