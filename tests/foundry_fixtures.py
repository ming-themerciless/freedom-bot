"""Synthetic Foundry export bundles, built to the contract.

Synthetic **by construction**, not anonymised after the fact
(`docs/discovery/fixture-strategy.md` §1): every name, id, score and item here
was invented for the test suite. No value is derived from a real Actor, and no
real Council snapshot is ever committed.

The shape follows `docs/rules/foundry-export-contract.md` and the paths verified
in `docs/discovery/foundry-mapping.md` §4.2 — including the awkward ones, which
are the point of having a fixture at all: an absent `hp.max`, an `ac` that is a
custom formula string, a class whose display name differs from its
`system.identifier`, and a `custom` language string.
"""
from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from domain.foundry import OBSERVED_DEPLOYMENT

ACTIVE_FOLDER_ID = "smob5eya6XVBAuIb"
ARCHIVE_FOLDER_ID = "arch5eya6XVBAuIb"
ROOT_FOLDER_ID = "root5eya6XVBAuIb"

FIRST_ACTOR_ID = "52ywI3ttEcgf9iBv"
SECOND_ACTOR_ID = "9kQpZ2mNbVcXsAe1"
THIRD_ACTOR_ID = "3fTgYhUjIkOlPq7W"


def folder(folder_id: str, name: str, parent_id: str | None = None) -> dict[str, Any]:
    return {"id": folder_id, "name": name, "parentId": parent_id}


def item(document_type: str, name: str, **system: Any) -> dict[str, Any]:
    return {"type": document_type, "name": name, "system": system}


def magic_item(
    name: str,
    *,
    rarity: str = "rare",
    identifier: str | None = "synthetic-band",
    book: str | None = "FBH",
) -> dict[str, Any]:
    system: dict[str, Any] = {"rarity": rarity, "quantity": 1}
    if identifier is not None:
        system["identifier"] = identifier
    if book is not None:
        system["source"] = {"book": book}
    return {"type": "equipment", "name": name, "system": system}


def actor(
    actor_id: str = FIRST_ACTOR_ID,
    *,
    name: str = "Testcharacter Brightlantern",
    folder_id: str = ACTIVE_FOLDER_ID,
    abilities: dict[str, int] | None = None,
    level: int = 9,
    class_identifier: str = "paladin",
    class_name: str = "Oathsworn",
    subclass_identifier: str = "oath-of-redemption",
    race: str = "Synthetic Human",
    background: str = "Entertainer",
    feats: tuple[str, ...] = ("Synthetic Alertness",),
    currency: dict[str, int] | None = None,
    tools: dict[str, int] | None = None,
    languages: tuple[str, ...] = ("common", "elvish"),
    custom_languages: str = "Common Sign Language",
    weapon_proficiencies: tuple[str, ...] = ("simple", "martial"),
    skills: dict[str, int] | None = None,
    magic_items: tuple[dict[str, Any], ...] | None = None,
    extra_items: tuple[dict[str, Any], ...] = (),
) -> dict[str, Any]:
    abilities = abilities or {
        "str": 16,
        "dex": 8,
        "con": 14,
        "int": 10,
        "wis": 12,
        "cha": 20,
    }
    currency = currency or {"pp": 1, "gp": 23, "sp": 4, "cp": 5, "ep": 0}
    tools = tools or {"smith": 1, "alchemist": 2, "disg": 1, "scrolls": 1}
    skills = skills or {"acr": 0, "ath": 1, "prc": 2}
    magic_items = (
        magic_items
        if magic_items is not None
        else (magic_item("Band of Synthetic Focus"),)
    )

    return {
        "id": actor_id,
        "folderId": folder_id,
        "name": name,
        "img": "worlds/the-guild/assets/synthetic.webp",
        "system": {
            "abilities": {
                ability: {"value": score} for ability, score in abilities.items()
            },
            "attributes": {
                # `hp.max` is deliberately null and `ac.flat` deliberately
                # absent: both are computed by Foundry at runtime and are
                # missing from a real export (foundry-mapping F-F2).
                "hp": {"value": 61, "max": None, "temp": 5},
                "ac": {
                    "calc": "custom",
                    "formula": "@attributes.ac.armor + @abilities.cha.mod",
                },
                "movement": {"walk": 30, "fly": 0, "units": "ft"},
                "senses": {"darkvision": 60, "units": "ft"},
                "init": {"ability": "dex", "bonus": ""},
            },
            "bastion": {
                "name": "Synthetic Watchtower",
                "description": "<p>Invented for the test suite.</p>",
            },
            "bonuses": {"mwak": {"attack": "", "damage": ""}},
            "currency": dict(currency),
            "details": {
                "biography": {"value": "<p>Synthetic.</p>"},
                "xp": {"value": 48000},
                "alignment": "Neutral Good",
            },
            "resources": {"primary": {"value": 0, "max": 0}},
            "skills": {key: {"value": value} for key, value in skills.items()},
            "spells": {"spell1": {"value": 4, "max": 4}},
            "tools": {key: {"value": value} for key, value in tools.items()},
            "traits": {
                "languages": {"value": list(languages), "custom": custom_languages},
                "weaponProf": {"value": list(weapon_proficiencies), "custom": ""},
                "armorProf": {"value": ["hvy"], "custom": ""},
                "dr": {"value": ["fire"], "custom": ""},
                "di": {"value": [], "custom": ""},
                "dv": {"value": [], "custom": ""},
                "ci": {"value": ["charmed"], "custom": ""},
                "size": "med",
            },
        },
        "items": [
            item("race", race),
            item("class", class_name, identifier=class_identifier, levels=level),
            item("subclass", "Vow of Invented Mercy", identifier=subclass_identifier),
            item("background", background),
            *(item("feat", feat_name) for feat_name in feats),
            *magic_items,
            {
                "type": "equipment",
                "name": "Travelling Cloak",
                "system": {"rarity": "common", "quantity": 1},
            },
            {
                "type": "facility",
                "name": "Synthetic Scriptorium",
                "system": {
                    "type": {"value": "special", "subtype": "scriptorium"},
                    "size": "roomy",
                    "order": "craft",
                },
            },
            {"type": "spell", "name": "Invented Light", "system": {"level": 0}},
            *extra_items,
        ],
    }


def bundle(
    *,
    actors: tuple[dict[str, Any], ...] | None = None,
    folders: tuple[dict[str, Any], ...] | None = None,
    selected_folder_ids: tuple[str, ...] = (ACTIVE_FOLDER_ID,),
    world: dict[str, Any] | None = None,
    schema_version: int = 1,
    exported_at: str = "2026-08-02T09:15:00Z",
    exporter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": "freedom-blades.foundry-export",
        "schemaVersion": schema_version,
        "exporter": exporter or {"id": "freedom-blades-export", "version": "1.0.2"},
        "exportedAt": exported_at,
        "world": world
        or {
            "id": OBSERVED_DEPLOYMENT.world_id,
            "title": "The Guild",
            "coreVersion": OBSERVED_DEPLOYMENT.core_version,
            "systemId": OBSERVED_DEPLOYMENT.system_id,
            "systemVersion": OBSERVED_DEPLOYMENT.system_version,
        },
        "selectedFolderIds": list(selected_folder_ids),
        "folders": list(
            folders
            or (
                folder(ROOT_FOLDER_ID, "Characters"),
                folder(ACTIVE_FOLDER_ID, "Characters (active)", ROOT_FOLDER_ID),
            )
        ),
        "actors": list(actors if actors is not None else (actor(),)),
    }


def encode(document: dict[str, Any]) -> bytes:
    """Encode a bundle exactly as the contract's canonical rules require."""
    text = json.dumps(
        document,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return (text + "\n").encode("utf-8")


def tamper(payload: bytes, *, find: bytes, replace: bytes) -> bytes:
    """Change bytes in an encoded bundle, to prove the checksum notices."""
    if find not in payload:
        raise AssertionError(f"{find!r} is not present in the encoded bundle.")
    return payload.replace(find, replace, 1)


def without(document: dict[str, Any], key: str) -> dict[str, Any]:
    copy = deepcopy(document)
    copy.pop(key)
    return copy


def with_key(document: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    copy = deepcopy(document)
    copy[key] = value
    return copy
