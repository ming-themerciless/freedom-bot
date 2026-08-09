"""The Freedom Blades field profile, version `2026-08-09.1`.

This module is **data**: the one place that says, for every supported snapshot
path, what the platform does with it, and for every field a path feeds, what the
platform is entitled to claim about that field today.
`docs/rules/field-ownership.md` is its prose counterpart and must be changed
with it.

The version string is stored on every preview, import, comparison and
calculation. Editing any row below is a profile change: it must bump the
version, and doing so makes every outstanding preview stale.

## What changed at `2026-08-09.1`

Rehearsal A on 2026-08-09 previewed a real 35-Actor export and found ten paths
this profile did not classify — finding RA-1. `classify` answered `None` for
each, which is the fail-closed answer and meant they were reported and never
written; but Phase 2 acceptance requires the profile to be *exhaustive* against
supported data, and it was not.

Three subtree rules close that gap, all `SNAPSHOT_ONLY`:

- `system.favorites.*` and `system.favorites[].*` — the character sheet's
  favourites bar. Presentation state belonging to the Foundry client. It is not
  game state, the platform will never own it, and no roll consumes it.
- `system.source.*` — the Actor's sourcebook provenance (`book`, `custom`,
  `license`, `page`, `revision`, `rules`). Reference metadata about where a
  statblock came from; the platform records provenance by snapshot checksum, not
  by publisher citation.

Two rules are needed for favourites rather than one because a path under an
array element is spelled `system.favorites[].id`, and a `system.favorites.*`
prefix does not match it — the character after the prefix is `[`, not `.`.

These are subtree rules, so a *new* path appearing under either subtree is
classified rather than failing closed. That is the same trade the profile
already makes for `system.attributes.*` and mundane inventory, and it is
acceptable for the same reason: neither subtree can become owned state without a
profile change, because `SNAPSHOT_ONLY` has no writable classification to
promote to.

## What changed at `2026-08-03.1`

ADR 0008 was rejected on 2026-08-02 and controlled baseline v1.1/v1.5 removed
Sheet-era migration from Phase 2. Three consequences are visible here:

1. **There is no correction mode, and no writable classification.** The former
   `council-correctable` snapshot mode and the standard/protected/compensating
   correction modes are gone. Phase 2 imports identity, mappings and provenance;
   it corrects nothing. Each field group becomes correctable when the typed
   package that owns it passes its migration/cutover gate.
2. **Almost every field is `legacy_authority_deferred`** and names the package
   accountable for migrating it, from
   `docs/project-management/data-migration-register.md`. A deferred field is
   reported, never compared: the platform holds no accepted typed value for it,
   so "matches" and "differs" are both claims it has not earned.
3. **Only fields a snapshot path actually feeds appear here.** The previous
   profile also carried fields with no Foundry representation — Moradinium,
   living-cost weeks, no-shows and the rest — because they were correctable.
   With correction gone they have no snapshot boundary to classify, and the
   controlled migration register is their sole governing record. Removing them
   from the profile removes the only place they could have been mistaken for
   something Phase 2 acts on.

## The one field with database authority

`character.display_name` is the exception, and deliberately so: the snapshot
import **writes it itself** when it creates a character, from the Actor's name.
Comparing a later snapshot against a value the platform wrote from the same
source is a real comparison, not a fabricated one. Its Sheet-era migration is
still owned by package 5.1 — the Sheet's column A and this column are different
sources for the same column, which is a tension the 5.1 migration resolves, not
Phase 2.

Note the direction: for a rename, **Foundry is where players rename**, so a
difference means the platform's display record is stale, not that the Foundry
Actor is out of date. Phase 2 reports it and changes nothing; identity is the
external Actor ID and is unaffected either way (OD-42).
"""
from __future__ import annotations

from domain.field_profile import (
    DifferenceDirection,
    FieldAuthority,
    FieldProfile,
    ProfileField,
    SnapshotField,
    SnapshotMode,
)
from domain.snapshot_values import Comparison

PROFILE_VERSION = "2026-08-09.1"

#: Embedded item types carrying physical possessions. Magic items are the subset
#: of these whose `system.rarity` is a real rarity; everything else in the
#: subtree is a snapshot-only mundane-inventory input.
PHYSICAL_ITEM_TYPES = (
    "consumable",
    "container",
    "equipment",
    "loot",
    "tool",
    "weapon",
)

#: Foundry vocabulary bridges, from `foundry-mapping.md` §4.6. Explicit and
#: reviewed: an unlisted Foundry key is reported as itself rather than guessed
#: at, because a wrong bridge silently rewrites a proficiency list.
ALIASES = {
    "disg": "disguise",
    "scrolls": "scroll",
}


def _deferred(
    key: str,
    label: str,
    *,
    owning_package: str,
    legacy_source: str,
    source: str,
) -> ProfileField:
    """A field whose accepted authority is still the legacy path.

    Every one of these is reported with its owning package and compared against
    nothing. The helper exists so that adding a deferred field cannot
    accidentally omit the package: the argument is required.
    """
    return ProfileField(
        key=key,
        label=label,
        authority=FieldAuthority.LEGACY_DEFERRED,
        owning_package=owning_package,
        legacy_source=legacy_source,
        source=source,
    )


def _fields() -> dict[str, ProfileField]:
    rows = (
        # -- the one field Phase 2 itself writes ------------------------------
        ProfileField(
            key="character.display_name",
            label="Character name (short)",
            authority=FieldAuthority.DATABASE,
            comparison=Comparison.NORMALIZED_TEXT,
            # Players rename in Foundry. The platform's copy was written from an
            # earlier Actor name, so a difference makes the *platform* record
            # stale — never the Foundry Actor. Declared here so the
            # reconciliation reads the direction off the field rather than
            # assuming one from the authority.
            difference_direction=DifferenceDirection.PLATFORM_DISPLAY_NAME_STALE,
            source=(
                "Written by the snapshot import at character creation from the "
                "Actor name. A later difference is a rename notice: the platform "
                "display record is stale, Foundry is not out of date, and "
                "identity is unaffected (OD-42, ADR 0006)."
            ),
        ),
        # -- identity and progression: deferred to package 5.1 -----------------
        _deferred(
            "character.race",
            "Race / species",
            owning_package="5.1",
            legacy_source="Characters AF",
            source="sheet-inventory F-S4; foundry-mapping §4.2",
        ),
        _deferred(
            "character.class",
            "Class",
            owning_package="5.1",
            # `system.identifier`, never `name`: class display names are
            # player-customised (`name: "Sorceress"` / `identifier: "sorcerer"`).
            legacy_source="Characters AE",
            source="foundry-mapping §4.2 — read the identifier, never the name",
        ),
        _deferred(
            "character.subclass",
            "Subclass",
            owning_package="5.1",
            legacy_source="Characters AE",
            source="foundry-mapping §4.2",
        ),
        _deferred(
            "character.background",
            "Background",
            owning_package="5.1",
            legacy_source="Characters AD",
            source="sheet-inventory §3; foundry-mapping §4.2",
        ),
        _deferred(
            "character.ability_scores",
            "Ability scores",
            owning_package="5.1",
            legacy_source="Characters AG",
            source="rules §6.2 p.15 (Learning Roll); sheet-inventory F-S4",
        ),
        _deferred(
            "character.feats",
            "Feats and ASIs",
            owning_package="5.1",
            legacy_source="Characters AH",
            source="sheet-inventory F-S4",
        ),
        _deferred(
            "character.level",
            "Character level",
            owning_package="5.1",
            legacy_source="Characters F",
            source=(
                "plan §6.1; rules §3 p.8–9. Reported only. Phase 2 cannot adopt "
                "a Foundry level, which is what keeps 'no automatic advancement' "
                "true by construction rather than by policy."
            ),
        ),
        # -- proficiencies: deferred to package 5.1 ----------------------------
        _deferred(
            "proficiencies.tools",
            "Tool proficiencies",
            owning_package="5.1",
            legacy_source="Characters Y",
            source=(
                "sheet-inventory §3.1; foundry-mapping §4.6. `dnd5e` records two "
                "proficiency levels against Freedom Blades' three ranks, so the "
                "vocabularies are lossy in both directions; 5.1 owns the mapping."
            ),
        ),
        _deferred(
            "proficiencies.languages",
            "Languages",
            owning_package="5.1",
            legacy_source="Characters Z",
            source="plan §6.1; foundry-mapping §4.4",
        ),
        _deferred(
            "proficiencies.special_weapons",
            "Special weapon proficiencies",
            owning_package="5.1",
            legacy_source="no direct column",
            source=(
                "rules §6.3.2 p.16; foundry-mapping §4.2. The register records "
                "no Sheet column: 5.1 may populate it only from an approved "
                "source, never by inference."
            ),
        ),
        # -- economy: deferred to package 5.2 ----------------------------------
        _deferred(
            "wallet.balance_copper",
            "Coin balance (integer copper)",
            owning_package="5.2",
            legacy_source="Characters P–S",
            source=(
                "plan §6.1, §7.7; ADR 0005. Player-editable in the Foundry "
                "client, so it can never be authoritative for money. Electrum is "
                "unused in the game: a nonzero `ep` is an anomaly to report, "
                "never to convert."
            ),
        ),
        # -- inventory: deferred to package 5.6a -------------------------------
        _deferred(
            "inventory.magic_items",
            "Magic and homebrew-managed items",
            owning_package="5.6a",
            legacy_source="Characters AA",
            source=(
                "plan §6.1, §7.4. Most items carry no stable catalogue identity "
                "until the 5.6a catalogue exists, which is a further reason "
                "Phase 2 reports presence rather than agreement."
            ),
        ),
    )
    return {row.key: row for row in rows}


def _snapshot_fields() -> tuple[SnapshotField, ...]:
    rules: list[SnapshotField] = [
        # -- structural identity ---------------------------------------------
        SnapshotField(
            path="id",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note=(
                "The Actor's real Foundry `_id`. Consumed by the parser and "
                "stored as an external mapping; never character state, and "
                "never matched by name."
            ),
        ),
        SnapshotField(
            path="folderId",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note="Folder membership, resolved against the bundle's folder graph.",
        ),
        SnapshotField(
            path="img",
            mode=SnapshotMode.IGNORED,
            note="Portrait path. Display-only; the platform stores no copy.",
        ),
        # -- identity and progression ----------------------------------------
        SnapshotField(
            path="name",
            mode=SnapshotMode.REPORTED,
            profile_field="character.display_name",
            note=(
                "Written at character creation; compared thereafter. Foundry is "
                "where players rename, and a rename is never an identity change."
            ),
        ),
        SnapshotField(
            path="items[type=race].name",
            mode=SnapshotMode.REPORTED,
            profile_field="character.race",
        ),
        SnapshotField(
            path="items[type=race].*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note="Race item mechanics; the platform stores no copy.",
        ),
        SnapshotField(
            path="items[type=class].system.identifier",
            mode=SnapshotMode.REPORTED,
            profile_field="character.class",
            note="Stable identifier. Class `name` is player-customised.",
        ),
        SnapshotField(
            path="items[type=class].system.levels",
            mode=SnapshotMode.REPORTED,
            profile_field="character.level",
            note="Character level is the sum of class levels. Reported only.",
        ),
        SnapshotField(
            path="items[type=class].*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
        ),
        SnapshotField(
            path="items[type=subclass].system.identifier",
            mode=SnapshotMode.REPORTED,
            profile_field="character.subclass",
        ),
        SnapshotField(
            path="items[type=subclass].*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
        ),
        SnapshotField(
            path="items[type=background].name",
            mode=SnapshotMode.REPORTED,
            profile_field="character.background",
        ),
        SnapshotField(
            path="items[type=background].*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
        ),
        SnapshotField(
            path="items[type=feat].name",
            mode=SnapshotMode.REPORTED,
            profile_field="character.feats",
        ),
        SnapshotField(
            path="items[type=feat].*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
        ),
        SnapshotField(
            path="system.abilities.*",
            mode=SnapshotMode.REPORTED,
            profile_field="character.ability_scores",
            note=(
                "`.value` only. `.mod` is absent from an export and is computed "
                "by the platform (foundry-mapping F-F2)."
            ),
        ),
        # -- reported proficiencies and economy -------------------------------
        SnapshotField(
            path="system.tools.*",
            mode=SnapshotMode.REPORTED,
            profile_field="proficiencies.tools",
        ),
        SnapshotField(
            path="system.traits.languages.*",
            mode=SnapshotMode.REPORTED,
            profile_field="proficiencies.languages",
        ),
        SnapshotField(
            path="system.traits.weaponProf.*",
            mode=SnapshotMode.REPORTED,
            profile_field="proficiencies.special_weapons",
        ),
        SnapshotField(
            path="system.currency.*",
            mode=SnapshotMode.REPORTED,
            profile_field="wallet.balance_copper",
        ),
        # -- snapshot-only mechanics ------------------------------------------
        SnapshotField(
            path="system.skills.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="skill_proficiencies",
            note="0 none, 1 proficient, 2 expertise. A roll input, never stored.",
        ),
        SnapshotField(
            path="system.attributes.movement.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="movement",
        ),
        SnapshotField(
            path="system.attributes.senses.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="senses",
        ),
        SnapshotField(
            path="system.attributes.hp.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note="`hp.max` is absent from an export and is computed at runtime.",
        ),
        SnapshotField(
            path="system.attributes.ac.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note="May be a custom formula string rather than a number (F-F2).",
        ),
        SnapshotField(
            path="system.attributes.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note="Remaining Actor attributes: display and DM reference.",
        ),
        # RA-1: found by previewing a real export, not by a fixture. Two rules,
        # because `system.favorites[].id` does not match a `system.favorites.*`
        # prefix — the next character is `[`, not `.`.
        SnapshotField(
            path="system.favorites.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note="Character sheet favourites bar: Foundry client presentation.",
        ),
        SnapshotField(
            path="system.favorites[].*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note="Favourite entries (`id`, `sort`, `type`): presentation only.",
        ),
        SnapshotField(
            path="system.source.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note=(
                "Sourcebook provenance for the Actor. The platform records "
                "provenance by snapshot checksum, not by publisher citation."
            ),
        ),
        SnapshotField(
            path="system.traits.dr.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="damage_resistances",
        ),
        SnapshotField(
            path="system.traits.di.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="damage_immunities",
        ),
        SnapshotField(
            path="system.traits.dv.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="damage_vulnerabilities",
        ),
        SnapshotField(
            path="system.traits.ci.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="condition_immunities",
        ),
        SnapshotField(
            path="system.traits.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            note="Remaining traits, including armour proficiency and size.",
        ),
        SnapshotField(
            path="system.resources.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
        ),
        SnapshotField(
            path="system.bastion.*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="bastion_description",
            note=(
                "Native `dnd5e` Bastion name and description. Evidence only: the "
                "Sheet-era Bastion economy stays on the legacy path under 5.9."
            ),
        ),
        SnapshotField(
            path="items[type=facility].*",
            mode=SnapshotMode.SNAPSHOT_ONLY,
            roll_input="bastion_facilities",
            note=(
                "Partial coverage: not every player records facilities. Absence "
                "is not evidence of absence, and no import may contradict "
                "Bastion state on the strength of an empty list."
            ),
        ),
        # -- ignored ----------------------------------------------------------
        SnapshotField(
            path="system.details.*",
            mode=SnapshotMode.IGNORED,
            note=(
                "Biography, appearance and D&D XP. `system.details.xp.value` is "
                "standard D&D experience and is NOT the Sheet's mission count; "
                "reconciling them by name is the mistake this row prevents."
            ),
        ),
        SnapshotField(
            path="system.spells.*",
            mode=SnapshotMode.IGNORED,
            note="Spell slots. No platform rule depends on them.",
        ),
        SnapshotField(
            path="system.bonuses.*",
            mode=SnapshotMode.IGNORED,
        ),
        SnapshotField(
            path="items[type=spell].*",
            mode=SnapshotMode.IGNORED,
        ),
    ]

    for item_type in PHYSICAL_ITEM_TYPES:
        # A magic item is a physical item carrying a real rarity. The three
        # paths below are what identity and rarity are read from; everything
        # else in the subtree is snapshot-only mundane inventory.
        rules.extend(
            (
                SnapshotField(
                    path=f"items[type={item_type}].system.rarity",
                    mode=SnapshotMode.REPORTED,
                    profile_field="inventory.magic_items",
                ),
                SnapshotField(
                    path=f"items[type={item_type}].system.identifier",
                    mode=SnapshotMode.REPORTED,
                    profile_field="inventory.magic_items",
                ),
                SnapshotField(
                    path=f"items[type={item_type}].system.source.*",
                    mode=SnapshotMode.REPORTED,
                    profile_field="inventory.magic_items",
                ),
                SnapshotField(
                    path=f"items[type={item_type}].*",
                    mode=SnapshotMode.SNAPSHOT_ONLY,
                    roll_input=None,
                    note="Mundane inventory: read-only evidence.",
                ),
            )
        )

    return tuple(rules)


PROFILE = FieldProfile(
    version=PROFILE_VERSION,
    fields=_fields(),
    snapshot_fields=_snapshot_fields(),
    aliases=ALIASES,
)
