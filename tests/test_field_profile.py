"""The field profile is exhaustive, versioned and fails closed.

The tests here are deliberately **table-driven off the profile itself**, so a
new field cannot be added without a classification, an extractor and — when it
is deferred — an accountable owning package. Adding a row and running the suite
is how you find out what else the row obliges you to do.

The load-bearing property after the 2026-08-02 rejection of ADR 0008 is
negative: **there is no writable classification and no correction mode.** A
snapshot value has no route into a character game-state field, and several tests
below exist to keep it that way rather than to describe behaviour.
"""
from __future__ import annotations

import pytest

from application.foundry.extraction import (
    SnapshotActorView,
    iter_missing_extractors,
    registered_extractors,
    registered_roll_inputs,
)
from domain.field_profile import (
    DifferenceDirection,
    FieldAuthority,
    FieldProfile,
    FieldProfileError,
    ProfileField,
    SnapshotField,
    SnapshotMode,
    UnknownPath,
    iter_actor_paths,
)
from domain.foundry_profile import PROFILE, PROFILE_VERSION
from domain.snapshot_values import Comparison
from tests import foundry_fixtures as fx

PROFILE_FIELDS = sorted(PROFILE.fields)
SNAPSHOT_RULES = sorted(PROFILE.snapshot_fields, key=lambda rule: rule.path)
DEFERRED = sorted(PROFILE.deferred_fields(), key=lambda entry: entry.key)


def view(actor=None) -> SnapshotActorView:
    from application.foundry.artifact import ingest_bytes
    from application.foundry.parser import parse_snapshot
    from domain.foundry import OBSERVED_DEPLOYMENT

    document = fx.bundle(actors=(actor or fx.actor(),))
    snapshot = parse_snapshot(
        ingest_bytes(fx.encode(document)), deployment=OBSERVED_DEPLOYMENT
    )
    return SnapshotActorView(snapshot.actors[0], PROFILE)


# -- exhaustiveness ------------------------------------------------------------


def test_the_profile_is_versioned():
    assert PROFILE.version == PROFILE_VERSION
    assert PROFILE.version.strip()


@pytest.mark.parametrize("rule", SNAPSHOT_RULES, ids=lambda rule: rule.path)
def test_every_snapshot_path_has_exactly_one_mode(rule: SnapshotField):
    resolved = PROFILE.classify(rule.prefix if rule.is_prefix else rule.path)

    assert resolved is not None
    assert isinstance(resolved.mode, SnapshotMode)


@pytest.mark.parametrize("key", PROFILE_FIELDS)
def test_every_field_has_exactly_one_authority_and_cites_a_source(key: str):
    profile_field = PROFILE.profile_field(key)

    assert isinstance(profile_field.authority, FieldAuthority)
    assert profile_field.source, f"{key} cites no rule or discovery source"


def test_the_fixture_actor_has_no_unclassified_path():
    # The exhaustiveness claim, checked rather than asserted in prose: every
    # canonical leaf of a contract-shaped Actor resolves to a rule.
    assert view().unknown_paths() == ()


def test_a_new_supported_schema_field_fails_closed():
    extended = fx.actor()
    extended["system"]["synthetics"] = {"newRuleInput": 3}

    unknown = view(extended).unknown_paths()

    assert unknown == (UnknownPath(path="system.synthetics.newRuleInput"),)
    assert PROFILE.classify("system.synthetics.newRuleInput") is None


def test_a_new_item_document_type_fails_closed():
    extended = fx.actor()
    extended["items"].append(
        {"type": "vehicle", "name": "Invented Cart", "system": {"speed": 10}}
    )

    paths = {entry.path for entry in view(extended).unknown_paths()}

    assert paths == {
        "items[type=vehicle].name",
        "items[type=vehicle].system.speed",
        "items[type=vehicle].type",
    }


def test_an_unknown_path_classifies_as_nothing_at_all():
    for path in ("system.newthing", "items[type=vehicle].name", "totally.made.up"):
        assert PROFILE.classify(path) is None


def test_the_unknown_path_report_is_bounded():
    extended = fx.actor()
    extended["system"]["synthetics"] = {f"k{index}": index for index in range(40)}

    assert len(view(extended).unknown_paths(limit=5)) == 5


def test_an_empty_subtree_is_still_a_classified_leaf():
    paths = set(iter_actor_paths({"system": {"traits": {"languages": {}}}}))

    assert paths == {"system.traits.languages"}
    assert PROFILE.classify("system.traits.languages") is not None


# -- deferred authority --------------------------------------------------------


def test_almost_every_field_is_deferred_and_display_name_is_the_exception():
    """The shape of the remediated profile, stated once as a whole.

    If this test starts failing because a field gained database authority, that
    is a migration/cutover event and belongs to the owning package's gate — not
    to a profile edit.
    """
    assert [entry.key for entry in PROFILE.comparable_fields()] == [
        "character.display_name"
    ]
    assert len(DEFERRED) == len(PROFILE.fields) - 1


@pytest.mark.parametrize("profile_field", DEFERRED, ids=lambda entry: entry.key)
def test_every_deferred_field_names_an_owning_package(profile_field: ProfileField):
    assert profile_field.owning_package, (
        f"{profile_field.key} defers its authority without naming who will "
        "migrate it, which leaves the field orphaned"
    )


@pytest.mark.parametrize("profile_field", DEFERRED, ids=lambda entry: entry.key)
def test_a_deferred_field_cannot_be_compared(profile_field: ProfileField):
    """Asking for a comparison raises rather than answering.

    Returning `NOT_COMPARABLE` would be one `if` away from being read as "no
    difference found", which is the fabrication the deferred classification
    exists to prevent. Absence of authority is not agreement.
    """
    assert profile_field.comparison is Comparison.NOT_COMPARABLE

    with pytest.raises(FieldProfileError, match="legacy_authority_deferred"):
        PROFILE.comparison_for(profile_field.key)


def test_the_refusal_names_the_package_that_will_migrate_the_field():
    with pytest.raises(FieldProfileError, match="5.2"):
        PROFILE.comparison_for("wallet.balance_copper")


def test_the_one_comparable_field_answers_with_a_real_rule():
    assert (
        PROFILE.comparison_for("character.display_name")
        is Comparison.NORMALIZED_TEXT
    )


# -- B-2: a comparable field must state which record a difference makes stale --


def test_a_field_with_database_authority_must_declare_its_difference_direction():
    """No default, because the default would be a guess about authorship.

    The rejected shape is the one that shipped: authority implied "the platform
    is right, update Foundry", which for a Foundry-authored field is an
    instruction to undo a legitimate change.
    """
    with pytest.raises(FieldProfileError, match="which record a difference makes stale"):
        ProfileField(
            key="character.something_new",
            label="Something a later package migrates",
            authority=FieldAuthority.DATABASE,
            comparison=Comparison.NORMALIZED_TEXT,
        )


def test_a_deferred_field_may_not_declare_a_difference_direction():
    with pytest.raises(FieldProfileError, match="difference makes stale"):
        ProfileField(
            key="character.something_deferred",
            label="Deferred",
            authority=FieldAuthority.LEGACY_DEFERRED,
            owning_package="5.1",
            difference_direction=DifferenceDirection.FOUNDRY_OUT_OF_DATE,
        )


def test_the_display_name_difference_makes_the_platform_record_stale():
    display_name = PROFILE.profile_field("character.display_name")

    assert (
        display_name.difference_direction
        is DifferenceDirection.PLATFORM_DISPLAY_NAME_STALE
    )
    assert not display_name.stales(DifferenceDirection.FOUNDRY_OUT_OF_DATE)


@pytest.mark.parametrize("direction", list(DifferenceDirection))
def test_every_direction_names_the_issue_code_it_is_reported_under(direction):
    """One fact, not two kept in step by hand."""
    assert direction.value in {"foundry_out_of_date", "platform_display_name_stale"}


def test_level_is_reported_but_never_comparable():
    """No automatic advancement, held by construction rather than by policy."""
    level = PROFILE.profile_field("character.level")

    assert level.is_deferred
    assert level.owning_package == "5.1"
    with pytest.raises(FieldProfileError):
        PROFILE.comparison_for("character.level")


def test_missions_are_never_reconciled_against_foundry_experience():
    """Sheet column G is a mission count; Foundry XP is D&D experience."""
    assert "missions.count" not in PROFILE.fields
    assert PROFILE.classify("system.details.xp.value").mode is SnapshotMode.IGNORED


# -- the absence of a write surface --------------------------------------------


def test_the_profile_exposes_no_correction_or_writable_classification():
    """ADR 0008's vocabulary must not come back through the API.

    Checked by name because that is how it would return: someone reintroducing
    a `correction_mode` attribute or a `snapshot_correctable_fields()` helper
    would be reintroducing the rejected design, whatever they called the commit.
    """
    for banned in (
        "correction_mode",
        "snapshot_correctable_fields",
        "is_writable_from_snapshot",
        "sheet_era_fields",
        "unresolved_fields",
        "database_field",
        "database_fields",
    ):
        assert not hasattr(PROFILE, banned), (
            f"FieldProfile exposes {banned!r}, which belongs to the rejected "
            "ADR 0008 design"
        )

    sample = PROFILE.profile_field("character.level")
    for banned in ("correction_mode", "storage", "value_kind", "subject_label"):
        assert not hasattr(sample, banned), (
            f"ProfileField exposes {banned!r}, which belongs to the rejected "
            "ADR 0008 design"
        )

    assert not hasattr(SnapshotMode, "COUNCIL_CORRECTABLE")
    assert not hasattr(SnapshotMode, "COMPARE")


def test_snapshot_only_inputs_cannot_be_selected_for_database_write():
    """A roll input is readable and has nowhere to be written to."""
    for name, rule in PROFILE.roll_inputs().items():
        assert rule.mode is SnapshotMode.SNAPSHOT_ONLY, name
        assert rule.profile_field is None, name


def test_no_snapshot_only_or_ignored_path_names_a_field():
    for rule in PROFILE.snapshot_fields:
        if rule.mode is not SnapshotMode.REPORTED:
            assert rule.profile_field is None, rule.path


# -- extractor coverage --------------------------------------------------------


def test_every_declared_roll_input_has_an_extractor():
    assert set(PROFILE.roll_inputs()) <= registered_roll_inputs()


def test_every_reported_field_has_an_extractor():
    assert list(iter_missing_extractors(PROFILE)) == []


def test_no_extractor_exists_for_a_field_the_profile_does_not_report():
    reported = {entry.key for entry in PROFILE.reported_fields()}

    assert registered_extractors() == reported


# -- construction invariants ---------------------------------------------------


def deferred_field(key="x.y", **kwargs) -> ProfileField:
    defaults = dict(
        key=key,
        label=key,
        authority=FieldAuthority.LEGACY_DEFERRED,
        owning_package="5.1",
        source="test",
    )
    defaults.update(kwargs)
    return ProfileField(**defaults)


def database_field(key="x.y", **kwargs) -> ProfileField:
    defaults = dict(
        key=key,
        label=key,
        authority=FieldAuthority.DATABASE,
        comparison=Comparison.EXACT_TEXT,
        source="test",
    )
    defaults.update(kwargs)
    return ProfileField(**defaults)


def profile_with(field: ProfileField, rule: SnapshotField) -> FieldProfile:
    return FieldProfile(
        version="t", fields={field.key: field}, snapshot_fields=(rule,)
    )


def test_a_deferred_field_must_name_its_owning_package():
    with pytest.raises(FieldProfileError, match="migration package"):
        deferred_field(owning_package=None)


def test_a_deferred_field_may_not_declare_a_comparison_rule():
    with pytest.raises(FieldProfileError, match="fabricated verdict"):
        deferred_field(comparison=Comparison.EXACT_TEXT)


def test_a_database_authority_field_may_not_name_a_migration_package():
    with pytest.raises(FieldProfileError, match="cannot be both"):
        database_field(owning_package="5.1")


def test_a_database_authority_field_needs_a_comparison_rule():
    with pytest.raises(FieldProfileError, match="no comparison rule"):
        database_field(comparison=Comparison.NOT_COMPARABLE)


def test_a_reported_path_must_name_an_existing_field():
    with pytest.raises(FieldProfileError, match="unknown profile field"):
        FieldProfile(
            version="t",
            fields={},
            snapshot_fields=(
                SnapshotField(
                    path="a", mode=SnapshotMode.REPORTED, profile_field="missing"
                ),
            ),
        )


def test_a_reported_path_must_name_some_field():
    with pytest.raises(FieldProfileError, match="names no profile field"):
        FieldProfile(
            version="t",
            fields={},
            snapshot_fields=(SnapshotField(path="a", mode=SnapshotMode.REPORTED),),
        )


def test_an_ignored_path_may_not_name_a_field():
    with pytest.raises(FieldProfileError, match="must name no"):
        profile_with(
            deferred_field(),
            SnapshotField(
                path="a", mode=SnapshotMode.IGNORED, profile_field="x.y"
            ),
        )


def test_a_snapshot_only_path_may_not_name_a_field():
    with pytest.raises(FieldProfileError, match="must name no"):
        profile_with(
            deferred_field(),
            SnapshotField(
                path="a", mode=SnapshotMode.SNAPSHOT_ONLY, profile_field="x.y"
            ),
        )


def test_an_ignored_path_cannot_be_a_roll_input():
    with pytest.raises(FieldProfileError, match="cannot be a roll input"):
        FieldProfile(
            version="t",
            fields={},
            snapshot_fields=(
                SnapshotField(path="a", mode=SnapshotMode.IGNORED, roll_input="r"),
            ),
        )


def test_a_field_no_snapshot_path_feeds_is_refused():
    """An unreachable field would drop silently out of every report."""
    with pytest.raises(FieldProfileError, match="no snapshot path feeds it"):
        FieldProfile(
            version="t",
            fields={"x.y": deferred_field()},
            snapshot_fields=(SnapshotField(path="a", mode=SnapshotMode.IGNORED),),
        )


def test_a_path_cannot_be_classified_twice():
    with pytest.raises(FieldProfileError, match="classified twice"):
        FieldProfile(
            version="t",
            fields={},
            snapshot_fields=(
                SnapshotField(path="a", mode=SnapshotMode.IGNORED),
                SnapshotField(path="a", mode=SnapshotMode.SNAPSHOT_ONLY),
            ),
        )


def test_a_profile_requires_a_version():
    with pytest.raises(FieldProfileError, match="requires a version"):
        FieldProfile(version="  ", fields={}, snapshot_fields=())


def test_an_unknown_field_is_refused_by_name():
    with pytest.raises(FieldProfileError, match="not a field in profile"):
        PROFILE.profile_field("character.invented")


def test_exact_rules_beat_prefix_rules_and_longer_prefixes_win():
    assert (
        PROFILE.classify("items[type=equipment].system.rarity").mode
        is SnapshotMode.REPORTED
    )
    assert (
        PROFILE.classify("items[type=equipment].system.description.value").mode
        is SnapshotMode.SNAPSHOT_ONLY
    )
    assert (
        PROFILE.classify("system.traits.languages.value").mode
        is SnapshotMode.REPORTED
    )
    assert PROFILE.classify("system.traits.size").mode is SnapshotMode.SNAPSHOT_ONLY


#: The exact paths a real 35-Actor export carried that profile `2026-08-03.1`
#: could not classify (finding RA-1, Rehearsal A, 2026-08-09). Written out
#: rather than generated, because the point of the test is that *these observed
#: paths* are covered — a generated list would drift with the profile it guards.
RA1_OBSERVED_PATHS = (
    "system.favorites",
    "system.favorites[].id",
    "system.favorites[].sort",
    "system.favorites[].type",
    "system.source.book",
    "system.source.custom",
    "system.source.license",
    "system.source.page",
    "system.source.revision",
    "system.source.rules",
)


@pytest.mark.parametrize("path", RA1_OBSERVED_PATHS)
def test_the_paths_a_real_export_carried_are_classified(path: str):
    """RA-1: the profile was not exhaustive against real data until 2026-08-09."""
    rule = PROFILE.classify(path)

    assert rule is not None, f"{path} is unclassified; classify returns fail-closed None"
    assert rule.mode is SnapshotMode.SNAPSHOT_ONLY
    assert rule.profile_field is None, (
        f"{path} feeds a profile field, so it would be reported and compared; "
        "presentation and provenance metadata must not become owned state"
    )


def test_favourites_needs_both_rules_because_of_the_array_spelling():
    """A `system.favorites.*` prefix does not reach `system.favorites[].id`.

    The next character after the prefix is `[`, not `.`, so `classify` would
    answer `None`. This is the mistake RA-1 is easiest to re-introduce by
    "tidying" the two rules into one.
    """
    prefixes = {
        rule.prefix for rule in PROFILE.snapshot_fields if rule.is_prefix
    }

    assert "system.favorites" in prefixes
    assert "system.favorites[]" in prefixes


def test_the_alias_table_is_explicit_and_leaves_unknown_keys_alone():
    assert PROFILE.alias("disg") == "disguise"
    assert PROFILE.alias("scrolls") == "scroll"
    assert PROFILE.alias("weaver") == "weaver"
