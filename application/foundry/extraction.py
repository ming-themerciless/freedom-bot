"""Read the profile-classified values out of one exported Actor.

Every extractor answers with either a value or an `Unavailable` carrying the
reason. There is no third path: an extractor never returns a zero, an empty set
or "no proficiency" to stand in for something it could not read. That rule is
what makes plan §6.5's *snapshot-backed calculations* invariant enforceable —
"calculations never silently substitute zero, no proficiency or an older
unreported value" is only true if the layer underneath refuses to invent one.

The extractors are also where the two documented **identity** rules live:

- a class or subclass is read from `system.identifier`, never from `name`,
  because class display names are player-customised (`"Sorceress"` /
  `"sorcerer"`);
- a magic item is identified by source plus upstream identifier, or by an
  explicitly reviewed alias, and never by its displayed name.

Ambiguity is `Unavailable`, not a first-match. Two `race` items or two
`background` items on one Actor mean the platform cannot say which is the
character's, and picking one would write a guess into a protected field.
"""
from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass

from application.foundry.parser import SnapshotActor
from domain.field_profile import FieldProfile
from domain.foundry_profile import PHYSICAL_ITEM_TYPES
from domain.snapshot_values import ABILITIES, ItemIdentity, ItemSet, Unavailable
from models.money import Money

#: Rarities `dnd5e` uses for items the platform treats as magic/homebrew-managed.
#: `common` and an absent rarity are mundane and stay snapshot-only evidence.
MAGIC_RARITIES = frozenset(
    {"uncommon", "rare", "veryrare", "very rare", "legendary", "artifact"}
)


@dataclass(frozen=True, slots=True)
class SnapshotValue:
    """One extracted value, or the reason there is not one."""

    value: object

    @property
    def is_available(self) -> bool:
        return not isinstance(self.value, Unavailable)


def _items(actor: SnapshotActor) -> Sequence[Mapping[str, object]]:
    items = actor.document.get("items")
    return items if isinstance(items, Sequence) else ()


def _items_of_type(actor: SnapshotActor, document_type: str) -> list[Mapping[str, object]]:
    return [
        item
        for item in _items(actor)
        if isinstance(item, Mapping) and item.get("type") == document_type
    ]


def _system(actor: SnapshotActor) -> Mapping[str, object]:
    system = actor.document.get("system")
    return system if isinstance(system, Mapping) else {}


def _nested(root: Mapping[str, object], *path: str) -> object | None:
    current: object = root
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def _exactly_one(
    candidates: Sequence[Mapping[str, object]], *, what: str
) -> Mapping[str, object] | Unavailable:
    if not candidates:
        return Unavailable(f"the Actor carries no {what} item")
    if len(candidates) > 1:
        return Unavailable(
            f"the Actor carries {len(candidates)} {what} items, so which one is "
            "the character's cannot be decided here"
        )
    return candidates[0]


class SnapshotActorView:
    """Profile-aware access to one Actor's classified values.

    Constructed per Actor per reconciliation run. It holds no state beyond the
    Actor and the profile, so two views of the same Actor answer identically —
    which is what makes a reconciliation report deterministic.
    """

    __slots__ = ("_actor", "_profile")

    def __init__(self, actor: SnapshotActor, profile: FieldProfile) -> None:
        self._actor = actor
        self._profile = profile

    @property
    def actor(self) -> SnapshotActor:
        return self._actor

    def unknown_paths(self, *, limit: int = 50):
        return self._profile.unknown_paths(self._actor.document, limit=limit)

    def value_for(self, profile_field: str) -> object:
        """The snapshot's representation of `profile_field`, or `Unavailable`.

        This is *what Foundry says*, and nothing more. For a deferred field it
        is report-only evidence: the platform holds no accepted typed value to
        set it beside, so a caller may render it but may never compare it. The
        refusal lives in `FieldProfile.comparison_for`, which raises for a
        deferred field rather than handing back a comparison rule.
        """
        extractor = _EXTRACTORS.get(profile_field)
        if extractor is None:
            return Unavailable(
                f"profile {self._profile.version} defines no snapshot extractor "
                f"for {profile_field}"
            )
        return extractor(self._actor, self._profile)

    def roll_input(self, name: str) -> object:
        """A snapshot-only input, or `Unavailable` with the reason.

        Snapshot-only inputs are readable and never writable: there is no
        counterpart to this method that sets one.
        """
        extractor = _ROLL_INPUTS.get(name)
        if extractor is None:
            return Unavailable(
                f"profile {self._profile.version} exposes no roll input "
                f"named {name!r}"
            )
        return extractor(self._actor, self._profile)


# -- database-field extractors ------------------------------------------------


def _display_name(actor: SnapshotActor, profile: FieldProfile) -> object:
    return actor.name


def _race(actor: SnapshotActor, profile: FieldProfile) -> object:
    item = _exactly_one(_items_of_type(actor, "race"), what="race")
    if isinstance(item, Unavailable):
        return item
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        return Unavailable("the race item has no usable name")
    return name


def _class_identifier(actor: SnapshotActor, profile: FieldProfile) -> object:
    classes = _items_of_type(actor, "class")
    if not classes:
        return Unavailable("the Actor carries no class item")
    if len(classes) > 1:
        # Multiclassing is representable in Foundry and is not yet modelled by
        # the platform's single class field. Reporting it as unable-to-compare
        # is honest; collapsing it to the first class would be a silent choice.
        return Unavailable(
            f"the Actor is multiclassed across {len(classes)} classes, which "
            "the platform's single class field cannot represent"
        )
    identifier = _nested(classes[0], "system", "identifier")
    if not isinstance(identifier, str) or not identifier.strip():
        return Unavailable(
            "the class item carries no `system.identifier`; a class is never "
            "identified by its player-customised display name"
        )
    return identifier


def _subclass_identifier(actor: SnapshotActor, profile: FieldProfile) -> object:
    item = _exactly_one(_items_of_type(actor, "subclass"), what="subclass")
    if isinstance(item, Unavailable):
        return item
    identifier = _nested(item, "system", "identifier")
    if not isinstance(identifier, str) or not identifier.strip():
        return Unavailable("the subclass item carries no `system.identifier`")
    return identifier


def _background(actor: SnapshotActor, profile: FieldProfile) -> object:
    item = _exactly_one(_items_of_type(actor, "background"), what="background")
    if isinstance(item, Unavailable):
        return item
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        return Unavailable("the background item has no usable name")
    return name


def _level(actor: SnapshotActor, profile: FieldProfile) -> object:
    classes = _items_of_type(actor, "class")
    if not classes:
        return Unavailable("the Actor carries no class item, so it has no level")
    total = 0
    for item in classes:
        levels = _nested(item, "system", "levels")
        if isinstance(levels, bool) or not isinstance(levels, int) or levels <= 0:
            return Unavailable(
                "a class item carries no positive `system.levels`, so the "
                "character level cannot be summed"
            )
        total += levels
    return total


def _ability_scores(actor: SnapshotActor, profile: FieldProfile) -> object:
    abilities = _nested(_system(actor), "abilities")
    if not isinstance(abilities, Mapping):
        return Unavailable("the Actor carries no `system.abilities`")
    scores: dict[str, int] = {}
    for ability in ABILITIES:
        value = _nested(abilities, ability, "value")
        if isinstance(value, bool) or not isinstance(value, int):
            return Unavailable(
                f"`system.abilities.{ability}.value` is missing or not a whole "
                "number"
            )
        scores[ability] = value
    return scores


def _feats(actor: SnapshotActor, profile: FieldProfile) -> object:
    names = [
        item.get("name")
        for item in _items_of_type(actor, "feat")
    ]
    if any(not isinstance(name, str) or not name.strip() for name in names):
        return Unavailable("a feat item has no usable name")
    return frozenset(profile.alias(str(name)) for name in names)


def _tools(actor: SnapshotActor, profile: FieldProfile) -> object:
    tools = _nested(_system(actor), "tools")
    if tools is None:
        return Unavailable("the Actor carries no `system.tools`")
    if not isinstance(tools, Mapping):
        return Unavailable("`system.tools` is not an object")
    held: set[str] = set()
    for key, entry in tools.items():
        value = entry.get("value") if isinstance(entry, Mapping) else entry
        if isinstance(value, bool) or not isinstance(value, int):
            return Unavailable(
                f"`system.tools.{key}` carries no numeric proficiency level"
            )
        if value > 0:
            held.add(profile.alias(str(key)))
    return frozenset(held)


def _trait_set(actor: SnapshotActor, profile: FieldProfile, trait: str) -> object:
    node = _nested(_system(actor), "traits", trait)
    if node is None:
        return Unavailable(f"the Actor carries no `system.traits.{trait}`")
    if not isinstance(node, Mapping):
        return Unavailable(f"`system.traits.{trait}` is not an object")

    values = node.get("value", ())
    if isinstance(values, str) or not isinstance(values, (list, tuple, set, frozenset)):
        return Unavailable(f"`system.traits.{trait}.value` is not a list")
    tokens = {profile.alias(str(entry)) for entry in values}

    custom = node.get("custom", "")
    if custom:
        if not isinstance(custom, str):
            return Unavailable(f"`system.traits.{trait}.custom` is not a string")
        # `dnd5e` stores custom entries as a `;`-separated string. Homebrew
        # languages such as Common Sign Language and Druidic arrive this way.
        tokens.update(
            profile.alias(part.strip())
            for part in custom.split(";")
            if part.strip()
        )
    return frozenset(tokens)


def _languages(actor: SnapshotActor, profile: FieldProfile) -> object:
    return _trait_set(actor, profile, "languages")


def _weapon_proficiencies(actor: SnapshotActor, profile: FieldProfile) -> object:
    return _trait_set(actor, profile, "weaponProf")


def _balance_copper(actor: SnapshotActor, profile: FieldProfile) -> object:
    currency = _nested(_system(actor), "currency")
    if not isinstance(currency, Mapping):
        return Unavailable("the Actor carries no `system.currency`")
    amounts: dict[str, int] = {}
    for denomination in ("pp", "gp", "sp", "cp", "ep"):
        value = currency.get(denomination, 0)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            return Unavailable(
                f"`system.currency.{denomination}` is missing or not a "
                "non-negative whole number"
            )
        amounts[denomination] = value
    if amounts["ep"]:
        # Electrum is unused in the game and has no Sheet column or rule. A
        # nonzero value is an anomaly: warn and refuse to convert, never fold it
        # in at 5 sp (foundry-mapping §4.4).
        return Unavailable(
            f"the Actor holds {amounts['ep']} electrum, which the game does not "
            "use. Electrum is never converted; resolve the anomaly in Foundry"
        )
    return Money.from_denominations(
        platinum=amounts["pp"],
        gold=amounts["gp"],
        silver=amounts["sp"],
        copper=amounts["cp"],
    ).copper


def _magic_items(actor: SnapshotActor, profile: FieldProfile) -> object:
    identities: list[ItemIdentity] = []
    for item in _items(actor):
        if not isinstance(item, Mapping):
            continue
        if item.get("type") not in PHYSICAL_ITEM_TYPES:
            continue
        system = item.get("system")
        if not isinstance(system, Mapping):
            continue
        rarity = system.get("rarity")
        if not isinstance(rarity, str) or rarity.strip().casefold() not in MAGIC_RARITIES:
            continue

        name = item.get("name")
        display = name if isinstance(name, str) else ""
        source = _nested(system, "source", "book")
        identifier = system.get("identifier")
        alias = profile.aliases.get(f"item:{identifier}") if isinstance(identifier, str) else None
        identities.append(
            ItemIdentity(
                source=source if isinstance(source, str) and source.strip() else None,
                upstream_id=(
                    identifier
                    if isinstance(identifier, str) and identifier.strip()
                    else None
                ),
                alias=alias,
                display_name=display,
            )
        )
    return ItemSet.of(identities)


_EXTRACTORS = {
    "character.display_name": _display_name,
    "character.race": _race,
    "character.class": _class_identifier,
    "character.subclass": _subclass_identifier,
    "character.background": _background,
    "character.level": _level,
    "character.ability_scores": _ability_scores,
    "character.feats": _feats,
    "proficiencies.tools": _tools,
    "proficiencies.languages": _languages,
    "proficiencies.special_weapons": _weapon_proficiencies,
    "wallet.balance_copper": _balance_copper,
    "inventory.magic_items": _magic_items,
}


# -- snapshot-only roll inputs -------------------------------------------------


def _skill_proficiencies(actor: SnapshotActor, profile: FieldProfile) -> object:
    skills = _nested(_system(actor), "skills")
    if not isinstance(skills, Mapping):
        return Unavailable("the Actor carries no `system.skills`")
    levels: dict[str, int] = {}
    for key, entry in skills.items():
        value = entry.get("value") if isinstance(entry, Mapping) else entry
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 2:
            return Unavailable(
                f"`system.skills.{key}.value` is missing or is not 0, 1 or 2"
            )
        levels[str(key)] = value
    return dict(sorted(levels.items()))


def _movement(actor: SnapshotActor, profile: FieldProfile) -> object:
    movement = _nested(_system(actor), "attributes", "movement")
    if not isinstance(movement, Mapping):
        return Unavailable("the Actor carries no `system.attributes.movement`")
    return {str(key): movement[key] for key in sorted(str(k) for k in movement)}


def _senses(actor: SnapshotActor, profile: FieldProfile) -> object:
    senses = _nested(_system(actor), "attributes", "senses")
    if not isinstance(senses, Mapping):
        return Unavailable("the Actor carries no `system.attributes.senses`")
    return {str(key): senses[key] for key in sorted(str(k) for k in senses)}


def _resistances(actor: SnapshotActor, profile: FieldProfile) -> object:
    return _trait_set(actor, profile, "dr")


def _immunities(actor: SnapshotActor, profile: FieldProfile) -> object:
    return _trait_set(actor, profile, "di")


def _vulnerabilities(actor: SnapshotActor, profile: FieldProfile) -> object:
    return _trait_set(actor, profile, "dv")


def _condition_immunities(actor: SnapshotActor, profile: FieldProfile) -> object:
    return _trait_set(actor, profile, "ci")


def _bastion_description(actor: SnapshotActor, profile: FieldProfile) -> object:
    bastion = _nested(_system(actor), "bastion")
    if not isinstance(bastion, Mapping):
        return Unavailable("the Actor carries no `system.bastion`")
    name = bastion.get("name")
    return name if isinstance(name, str) else Unavailable("the Bastion has no name")


def _bastion_facilities(actor: SnapshotActor, profile: FieldProfile) -> object:
    """Facilities as *observed*, never as a count that defaults to zero.

    Coverage is partial — not every player records facilities — so absence is
    not evidence of absence. The caller receives what was observed together with
    the fact that it was observed; nothing here turns an empty list into a
    finding.
    """
    facilities: list[Mapping[str, object]] = []
    for item in _items_of_type(actor, "facility"):
        name = item.get("name")
        subtype = _nested(item, "system", "type", "subtype")
        size = _nested(item, "system", "size")
        facilities.append(
            {
                "name": name if isinstance(name, str) else "",
                "subtype": subtype if isinstance(subtype, str) else None,
                "size": size if isinstance(size, str) else None,
            }
        )
    return tuple(sorted(facilities, key=lambda entry: str(entry["name"])))


_ROLL_INPUTS = {
    "skill_proficiencies": _skill_proficiencies,
    "movement": _movement,
    "senses": _senses,
    "damage_resistances": _resistances,
    "damage_immunities": _immunities,
    "damage_vulnerabilities": _vulnerabilities,
    "condition_immunities": _condition_immunities,
    "bastion_description": _bastion_description,
    "bastion_facilities": _bastion_facilities,
}


def registered_extractors() -> frozenset[str]:
    """Profile fields with a snapshot extractor. Used by the profile tests."""
    return frozenset(_EXTRACTORS)


def registered_roll_inputs() -> frozenset[str]:
    return frozenset(_ROLL_INPUTS)


def iter_missing_extractors(profile: FieldProfile) -> Iterator[str]:
    """Reported fields the extraction layer cannot read.

    A profile row a snapshot path feeds but no extractor can read would report
    `Unavailable` for every Actor for ever, silently — and for a deferred field
    that is worse than useless, because the whole point of the deferred row is
    to show what Foundry holds while the platform holds nothing. This turns the
    omission into a test failure.
    """
    for profile_field in profile.reported_fields():
        if profile_field.key not in _EXTRACTORS:
            yield profile_field.key
