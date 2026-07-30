import pytest

from models.skills import Skills


def _skills(crp_dict=None, crafting=None, tool_proficiencies=None):
    skills = Skills()
    skills.crp_dict = dict(crp_dict or {})
    skills.crafting = dict(crafting or {})
    skills.tool_proficiencies = dict(tool_proficiencies or {})
    return skills


def _loaded(crp_cell="", skills_cell="", proficiencies_cell=""):
    """Build a Skills the way the Sheets adapter does, from raw cell text."""
    cells = {
        "crp": crp_cell,
        "skills": skills_cell,
        "proficiencies": proficiencies_cell,
        "languages": "",
        "downtime_progress": "-",
    }
    skills = Skills()
    skills.load_from_sheet_data(lambda key: cells.get(key, ""))
    return skills


# --- Column W parsing, canonical "amount (Tool)" form ---
#
# Regression tests for the data-loss defect found 2026-07-30: the parser only
# understood "Brewer: 7.5", so the live sheet's "7.5 (Brewer)" produced an empty
# crp_dict. A subsequent /craft then wrote a single-tool cell back over it,
# discarding every other tool's reputation. Maintainer-confirmed canonical form.


def test_canonical_paired_form_populates_every_tool():
    skills = _loaded("7.5 (Brewer), 2.5 (Calligrapher)")

    assert skills.crp_dict == {"brewer": 7.5, "calligrapher": 2.5}
    assert skills.get_tool_crp("Brewer's Supplies") == 7.5
    assert skills.get_tool_crp("Calligrapher's Supplies") == 2.5


def test_an_abbreviated_tool_name_silently_resolves_to_zero():
    """Documents current behaviour, which is a hazard rather than a feature.

    Lookup cleans a name to its first word ('Calligrapher's Supplies' ->
    'Calligrapher'), so a sheet cell abbreviated to '(Calligraph)' does not
    match and yields 0.0 with no warning. Since the RC-09 Master gate reads this
    value, an abbreviation is enough to refuse a qualified character. Tool
    identity is OD-06; do not 'fix' this with prefix matching, which would make
    Painter/Potter-style collisions silent instead.
    """
    skills = _loaded("120 (Calligraph)")

    assert skills.crp_dict == {"calligraph": 120}
    assert skills.get_tool_crp("Calligrapher's Supplies") == 0.0


def test_canonical_paired_form_accepts_comma_decimals():
    """A comma is both the decimal mark and the list separator; don't split on it."""
    skills = _loaded("7,5 (Brewer), 2,5 (Calligraph)")

    assert skills.crp_dict == {"brewer": 7.5, "calligraph": 2.5}


def test_legacy_colon_form_is_still_understood():
    skills = _loaded("Brewer: 7.5, Calligraph: 2.5")

    assert skills.crp_dict == {"brewer": 7.5, "calligraph": 2.5}


def test_mastered_marker_yields_no_running_total():
    """Rules 6.3.3.1 (PDF p.17): one Master rank for life, so CRP stops mattering."""
    skills = _loaded("Master")

    assert skills.crp == "Master"
    assert skills.crp_dict == {}


def test_award_preserves_other_tools_and_the_sheet_format():
    """The exact production sequence that was losing data."""
    skills = _loaded("7.5 (Brewer), 2.5 (Calligraph)")

    # ext/commands/craft.py awards 2.5 CRP in Brewer.
    skills.add_tool_crp("Brewer's Supplies", 2.5)

    written = skills.get_sheet_data()["crp"]

    assert "(Calligraph)" in written, "other tools must survive the write"
    assert "10 (Brewer)" in written, "the award must accumulate, not replace"
    assert ":" not in written, "must not rewrite the sheet's canonical form"


# --- Column W parsing is all-or-nothing ---
#
# Regression tests for the defect found in the Codex Phase 0 re-review: the pair
# pattern was applied with findall(), which keeps whatever fragments happen to
# match and silently ignores the rest. "7.5 (Brewer), BROKEN" therefore parsed as
# {"brewer": 7.5}, and the next /craft rewrote the whole cell from that dict --
# dropping "BROKEN" permanently. A cell is now read as a per-tool list only when
# everything outside the matched fragments is a separator.


def test_a_fully_valid_canonical_multi_tool_cell_is_accepted_whole():
    skills = _loaded("62.5 (Alchemist), 5 (Smith), 2.5 (Brewer)")

    assert skills.crp_dict == {"alchemist": 62.5, "smith": 5, "brewer": 2.5}
    assert skills.crp_unparsed is False


def test_comma_decimal_notation_is_accepted_throughout_the_cell():
    """The comma is both the decimal mark and the list separator."""
    skills = _loaded("7,5 (Brewer), 2,5 (Calligrapher), 10 (Smith)")

    assert skills.crp_dict == {"brewer": 7.5, "calligrapher": 2.5, "smith": 10}
    assert skills.crp_unparsed is False


def test_malformed_text_after_a_valid_pair_yields_no_partial_parse():
    skills = _loaded("7.5 (Brewer), BROKEN")

    assert skills.crp_dict == {}, "a partial parse is what overwrote the cell"
    assert skills.crp_unparsed is True
    assert skills.crp == "7.5 (Brewer), BROKEN", "the raw value must be preserved"


def test_malformed_text_between_valid_pairs_yields_no_partial_parse():
    skills = _loaded("7.5 (Brewer), BROKEN, 2.5 (Smith)")

    assert skills.crp_dict == {}
    assert skills.crp_unparsed is True
    assert skills.crp == "7.5 (Brewer), BROKEN, 2.5 (Smith)"


def test_a_malformed_legacy_fragment_yields_no_partial_parse():
    skills = _loaded("Brewer: 7.5, BROKEN")

    assert skills.crp_dict == {}
    assert skills.crp_unparsed is True
    assert skills.crp == "Brewer: 7.5, BROKEN"


def test_malformed_input_cannot_be_rewritten_as_a_truncated_valid_cell():
    """The data-loss path end to end: read, award, save."""
    skills = _loaded("7.5 (Brewer), BROKEN")

    assert skills.can_record_tool_crp() is False
    with pytest.raises(ValueError, match="reconciled"):
        skills.add_tool_crp("Brewer's Supplies", 2.5)

    # Even if a caller marks the cell modified by hand, column W is omitted from
    # the write set, so the adapter leaves the stored value alone.
    skills.crp_modified = True
    assert "crp" not in skills.get_sheet_data()


def test_an_unreadable_cell_is_surfaced_rather_than_shown_as_a_number():
    skills = _loaded("7.5 (Brewer), BROKEN")

    summary = skills.get_summary()

    assert "7.5 (Brewer), BROKEN" in summary
    assert "unreadable" in summary


def test_junk_in_column_w_is_treated_as_unreadable_too():
    """The 'anything else' row of the sheet-inventory table, now pinned read-only."""
    skills = _loaded("n/a")

    assert skills.crp_dict == {}
    assert skills.crp_unparsed is True
    assert skills.can_record_tool_crp() is False


def test_both_notations_may_appear_in_one_cell():
    """Both encodings coexist in the live sheet (OD-34), so a mixed cell is read."""
    skills = _loaded("7.5 (Brewer), Smith: 2.5")

    assert skills.crp_dict == {"brewer": 7.5, "smith": 2.5}
    assert skills.crp_unparsed is False


def test_a_bare_total_is_still_read_as_the_untagged_legacy_bucket():
    skills = _loaded("12.5")

    assert skills.crp_dict == {"general": 12.5}
    assert skills.crp_unparsed is False


# --- Column W parsing consolidates duplicate entries ---
#
# Regression tests for the third Codex Phase 0 re-review finding: _parse_crp_cell()
# lowercased each tool name and assigned it straight into the dictionary, so a
# second entry naming the same tool overwrote the first. "2.5 (Smith), 2.5 (SMITH)"
# read as {"smith": 2.5}, and the next /craft rewrote the whole cell from that
# dict -- discarding 2.5 CRP permanently. Duplicates are now summed at read time,
# under the first spelling seen and in its position.


def test_identical_duplicate_names_are_summed_not_overwritten():
    skills = _loaded("2.5 (Smith), 2.5 (Smith)")

    assert skills.crp_dict == {"smith": 5}
    assert skills.get_tool_crp("Smith's Tools") == 5.0
    assert skills.crp_unparsed is False


def test_case_variant_duplicate_names_are_summed_not_overwritten():
    """The reported reproduction: the second entry used to replace the first."""
    skills = _loaded("2.5 (Smith), 2.5 (SMITH)")

    assert skills.crp_dict == {"smith": 5}
    assert skills.get_tool_crp("Smith's Tools") == 5.0


def test_duplicate_names_in_legacy_notation_are_summed():
    skills = _loaded("Smith: 2.5, SMITH: 2.5")

    assert skills.crp_dict == {"smith": 5}
    assert skills.crp_unparsed is False


def test_duplicates_across_mixed_notations_are_summed():
    """Both encodings coexist in the live sheet (OD-34), including for one tool."""
    skills = _loaded("2.5 (Smith), Smith: 2.5")

    assert skills.crp_dict == {"smith": 5}
    assert skills.crp_unparsed is False


def test_duplicate_entries_with_comma_decimals_are_summed():
    skills = _loaded("2,5 (Smith), 2,5 (SMITH)")

    assert skills.crp_dict == {"smith": 5}


def test_consolidation_keeps_the_first_spelling_and_its_position():
    """Deterministic order: the first occurrence fixes both the key and its place."""
    skills = _loaded("7.5 (Brewer), 2.5 (Smith), 2.5 (BREWER)")

    assert skills.crp_dict == {"brewer": 10, "smith": 2.5}
    assert list(skills.crp_dict) == ["brewer", "smith"]
    assert skills.get_summary() == "**Crafting Reputation:** Brewer: 10, Smith: 2.5"


def test_the_full_duplicate_read_award_and_save_path_loses_nothing():
    """The reported defect end to end: 2.5 + 2.5 stored, +2.5 awarded, 7.5 saved."""
    skills = _loaded("2.5 (Smith), 2.5 (SMITH)")

    assert skills.add_tool_crp("Smith's Tools", 2.5) == 7.5

    written = skills.get_sheet_data()["crp"]
    assert written == "7.5 (Smith)"
    assert written.count("(") == 1, "one entry per tool"
    assert skills.get_tool_crp("Smith's Tools") == 7.5


def test_duplicate_entries_alone_do_not_rewrite_the_cell():
    """Consolidation is a read-time repair; it never triggers a write by itself."""
    skills = _loaded("2.5 (Smith), 2.5 (SMITH)")

    assert skills.crp_modified is False
    assert "crp" not in skills.get_sheet_data()
    assert skills.crp == "2.5 (Smith), 2.5 (SMITH)", "the raw value is untouched"


def test_distinct_tools_are_never_consolidated():
    """Painter/Potter-style near-misses must stay apart, not merge."""
    skills = _loaded("2.5 (Painter), 5 (Potter), 7.5 (Smith)")

    assert skills.crp_dict == {"painter": 2.5, "potter": 5, "smith": 7.5}


def test_equivalent_spellings_are_not_merged_at_read_time():
    """The read-time key is the literal name; only add_tool_crp() applies
    _clean_tool_name()'s tool-to-artisan bridge.

    Deliberate boundary. The bridge collapses a name to its first word, so merging
    on it at read time would silently commit a free-text cell to that collapse --
    including for a non-canonical artisan nobody has validated, which OD-06 rules
    must fail loudly at import rather than be guessed. 'Smith' and "Smith's Tools"
    are still folded into one entry the moment CRP is awarded for that tool -- see
    test_duplicate_spellings_already_in_the_cell_are_folded_into_one.
    """
    skills = _loaded("2.5 (Smith's tools), 2.5 (Smith)")

    assert skills.crp_dict == {"smith's tools": 2.5, "smith": 2.5}
    assert skills.crp_unparsed is False


def test_a_duplicate_beside_malformed_text_is_still_fail_closed():
    """Consolidation must not rescue a cell that is not understood in full."""
    skills = _loaded("2.5 (Smith), 2.5 (SMITH), BROKEN")

    assert skills.crp_dict == {}
    assert skills.crp_unparsed is True
    assert skills.crp == "2.5 (Smith), 2.5 (SMITH), BROKEN"
    assert skills.can_record_tool_crp() is False


@pytest.mark.parametrize(
    "cell",
    [
        "9" * 400 + " (Smith)",                      # one fragment overflows
        "Smith: " + "9" * 400,                       # ... in legacy notation too
        "9" * 308 + " (Smith), " + "9" * 308 + " (SMITH)",  # only the sum overflows
    ],
)
def test_a_value_too_large_to_represent_is_unreadable_rather_than_infinite(cell):
    """float() overflows such a literal to inf; inf must never enter crp_dict.

    Fail-closed, like any other value the parser cannot represent: the raw cell is
    preserved and column W is pinned read-only, rather than a total of `inf` being
    written back over it.
    """
    skills = _loaded(cell)

    assert skills.crp_dict == {}
    assert skills.crp_unparsed is True
    assert skills.crp == cell
    assert skills.can_record_tool_crp() is False


# --- add_tool_crp: one identity per tool ---
#
# Regression tests for the second Codex Phase 0 re-review finding: /craft wrote
# actor.skills.crp_dict[tool_clean] directly, which disagreed with the normalised
# lookup in get_tool_crp(). "2.5 (Smith's Tools)" plus an award therefore became
# "2.5 (Smith's tools), 2.5 (Smith)", and the Master gate read only half of it.


def test_award_accumulates_on_an_existing_short_key():
    skills = _skills(crp_dict={"smith": 2.5})

    assert skills.add_tool_crp("Smith's Tools", 2.5) == 5
    assert skills.crp_dict == {"smith": 5}
    assert skills.crp_modified is True


def test_award_accumulates_on_an_existing_full_tool_key():
    skills = _skills(crp_dict={"smith's tools": 2.5})

    assert skills.add_tool_crp("Smith's Tools", 2.5) == 5
    assert skills.crp_dict == {"smith's tools": 5}
    assert skills.get_tool_crp("Smith's Tools") == 5.0


def test_award_accumulates_regardless_of_capitalisation():
    skills = _skills(crp_dict={"Smith's Tools": 2.5})

    assert skills.add_tool_crp("smith", 2.5) == 5
    assert skills.crp_dict == {"Smith's Tools": 5}, "the stored spelling is kept"


def test_award_accumulates_on_the_canonical_parsed_sheet_representation():
    """The reported case, from sheet cell to sheet cell."""
    skills = _loaded("2.5 (Smith's Tools)")

    assert skills.add_tool_crp("Smith's Tools", 2.5) == 5

    written = skills.get_sheet_data()["crp"]
    assert written == "5 (Smith's tools)"
    assert written.count("(") == 1, "no second identity for the same tool"
    assert skills.get_tool_crp("Smith's Tools") == 5.0


def test_award_does_not_disturb_other_tools():
    skills = _loaded("7.5 (Brewer), 62.5 (Alchemist)")

    skills.add_tool_crp("Brewer's Supplies", 2.5)

    assert skills.crp_dict == {"brewer": 10, "alchemist": 62.5}


def test_duplicate_spellings_already_in_the_cell_are_folded_into_one():
    """Rows the old code already damaged are consolidated, not extended."""
    skills = _loaded("2.5 (Smith's tools), 2.5 (Smith)")

    assert skills.add_tool_crp("Smith's Tools", 2.5) == 7.5
    assert skills.crp_dict == {"smith's tools": 7.5}
    assert skills.get_sheet_data()["crp"] == "7.5 (Smith's tools)"


def test_a_first_award_creates_the_cleaned_tool_key():
    skills = _loaded("62.5 (Alchemist)")

    assert skills.add_tool_crp("Smith's Tools", 2.5) == 2.5
    assert skills.crp_dict == {"alchemist": 62.5, "smith": 2.5}


def test_fractional_awards_stay_exact_and_serialise_without_a_decimal_tail():
    skills = _loaded("7.5 (Brewer)")

    assert skills.add_tool_crp("Brewer's Supplies", 2.5) == 10
    assert skills.get_sheet_data()["crp"] == "10 (Brewer)"


def test_a_zero_award_changes_nothing():
    skills = _loaded("7.5 (Brewer)")

    assert skills.add_tool_crp("Brewer's Supplies", 0) == 7.5
    assert skills.crp_modified is False, "no reason to rewrite the cell"


@pytest.mark.parametrize("amount", ["lots", None, float("nan"), float("inf"), -2.5])
def test_a_non_numeric_or_impossible_award_is_refused(amount):
    skills = _skills(crp_dict={"smith": 2.5})

    with pytest.raises(ValueError):
        skills.add_tool_crp("Smith's Tools", amount)

    assert skills.crp_dict == {"smith": 2.5}
    assert skills.crp_modified is False


def test_an_unreadable_stored_value_is_refused_rather_than_replaced():
    skills = _skills(crp_dict={"smith": "lots"})

    with pytest.raises(ValueError, match="not a number"):
        skills.add_tool_crp("Smith's Tools", 2.5)

    assert skills.crp_dict == {"smith": "lots"}, "the stored value must survive"
    assert skills.crp_modified is False


def test_a_mastered_cell_is_never_replaced_by_a_per_tool_total():
    """Rules 6.3.3.1 (PDF p.17) / OD-29: one Master rank for life."""
    skills = _loaded("Master")

    assert skills.can_record_tool_crp() is False
    with pytest.raises(ValueError, match="reconciled"):
        skills.add_tool_crp("Smith's Tools", 2.5)

    assert skills.crp == "Master"
    assert skills.crp_modified is False


def test_an_award_beside_an_untagged_legacy_total_shadows_it():
    """Documents current behaviour, which OD-34 resolves by hand at import.

    The untagged 'general' bucket only counts for a tool while it is the *only*
    entry, so the first per-tool award stops a legacy total from satisfying the
    Master gate. Ruled 2026-07-30: untagged CRP is assigned to a tool once, by
    hand, at import -- not by a code policy here.
    """
    skills = _loaded("120")

    skills.add_tool_crp("Smith's Tools", 2.5)

    assert skills.crp_dict == {"general": 120, "smith": 2.5}
    assert skills.get_tool_crp("Smith's Tools") == 2.5
    assert skills.get_tool_crp("Jeweler's Tools") == 0.0


def test_a_qualified_master_candidate_is_not_blocked_by_the_gate():
    """The RC-09 gate must read the real sheet format, or it refuses everyone."""
    skills = _loaded("150 (Brewer)", skills_cell="Expert Brewer")

    assert skills.get_tool_crp("Brewer") >= Skills.MASTER_CRP_REQUIREMENT


class _StubActor:
    """Minimal stand-in for Actor; learn_proficiency only needs these."""

    def __init__(self, skills):
        self.name = "Test Smith A"
        self.skills = skills
        self.resources = _StubResources()


class _StubResources:
    def __init__(self):
        self.downtime = 60
        self.gold = 10000

    def validate_downtime(self, downtime):
        if downtime < 5 or downtime % 5 != 0:
            raise ValueError("Downtime must be spent in increments of five days.")

    def deduct(self, gold=0, **_):
        self.gold -= gold


# --- get_tool_crp ---


def test_tool_crp_matches_on_the_cleaned_tool_name():
    skills = _skills(crp_dict={"smith": 62.5})

    assert skills.get_tool_crp("Smith's Tools") == 62.5
    assert skills.get_tool_crp("smith") == 62.5


def test_tool_crp_is_zero_for_an_untracked_tool():
    skills = _skills(crp_dict={"smith": 100})

    assert skills.get_tool_crp("Jeweler's Tools") == 0.0


def test_untagged_legacy_total_counts_for_any_tool():
    """Sheets predating per-tool tracking hold a single untagged number."""
    skills = _skills(crp_dict={"general": 120})

    assert skills.get_tool_crp("Smith's Tools") == 120.0


def test_untagged_total_is_ignored_once_tools_are_tracked_separately():
    skills = _skills(crp_dict={"general": 120, "smith": 10})

    assert skills.get_tool_crp("Jeweler's Tools") == 0.0


# --- Master rank prerequisite, homebrew rules 6.3.3.1 (PDF p.17) ---


def test_master_requires_one_hundred_crp_with_that_tool():
    skills = _skills(
        crp_dict={"smith": 40},
        crafting={"Smith": "expert"},
    )
    actor = _StubActor(skills)

    with pytest.raises(ValueError, match="100 crafting reputation points"):
        skills.learn_proficiency(
            actor=actor, bot=None, ability_modifier=3, downtime=5,
            tool="Smith's Tools",
        )

    assert skills.downtime_progress == {}
    assert actor.resources.downtime == 60


def test_master_project_starts_once_the_reputation_threshold_is_met(monkeypatch):
    monkeypatch.setattr(
        "helpers.utils.roll_dice", lambda *a, **k: ([10], 13)
    )
    skills = _skills(
        crp_dict={"smith": 100},
        crafting={"Smith": "expert"},
    )
    actor = _StubActor(skills)

    _, spent_dt, spent_gp, name, level = skills.learn_proficiency(
        actor=actor, bot=None, ability_modifier=3, downtime=5,
        tool="Smith's Tools",
    )

    assert level == "master"
    assert name == "Smith"
    assert spent_dt == 5
    assert spent_gp == 100  # 100gp per Master lesson


def test_reputation_gate_does_not_block_lower_ranks(monkeypatch):
    monkeypatch.setattr(
        "helpers.utils.roll_dice", lambda *a, **k: ([10], 13)
    )
    skills = _skills(crp_dict={}, crafting={"Smith": "journeyman"})
    actor = _StubActor(skills)

    _, _, spent_gp, _, level = skills.learn_proficiency(
        actor=actor, bot=None, ability_modifier=3, downtime=5,
        tool="Smith's Tools",
    )

    assert level == "expert"
    assert spent_gp == 25  # 25gp per Expert lesson


def test_an_existing_master_tool_blocks_a_second_one_before_the_crp_check():
    """The one-Master limit is the accurate reason, so it must win the message."""
    skills = _skills(
        crp_dict={"jeweler": 500},
        crafting={"Smith": "master", "Jeweler": "expert"},
    )
    actor = _StubActor(skills)

    with pytest.raises(ValueError, match="only become a Master in one"):
        skills.learn_proficiency(
            actor=actor, bot=None, ability_modifier=3, downtime=5,
            tool="Jeweler's Tools",
        )


def test_in_progress_master_project_is_not_retroactively_blocked(monkeypatch):
    """The gate applies when a project starts, not to one already under way."""
    monkeypatch.setattr(
        "helpers.utils.roll_dice", lambda *a, **k: ([10], 13)
    )
    skills = _skills(crp_dict={"smith": 40}, crafting={"Smith": "expert"})
    skills.downtime_progress = {
        "smith": {
            "percent": 55.0,
            "level": "master",
            "orig_level": "master",
            "name": "Smith",
            "raw": "55% (master) Smith",
        }
    }
    actor = _StubActor(skills)

    rolls, _, _, _, level = skills.learn_proficiency(
        actor=actor, bot=None, ability_modifier=3, downtime=5,
        tool="Smith's Tools",
    )

    assert level == "master"
    assert rolls[0]["new_percent"] == 68.0


def test_other_master_tool_lookup_ignores_the_target_itself():
    skills = _skills(crafting={"Smith": "master"})

    assert skills._find_other_master_tool("Smith's Tools") is None
    assert skills._find_other_master_tool("Jeweler's Tools") == "Smith"
