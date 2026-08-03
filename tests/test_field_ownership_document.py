"""`docs/rules/field-ownership.md` and the profile cannot drift apart.

A prose ownership matrix that disagrees with the code is worse than none: it is
what a reviewer reads while approving the thing it no longer describes. So the
document is checked against the profile rather than trusted.

The owning-package column is checked a second way, against the controlled
migration manifest, because a deferred field naming a package that does not
exist would claim an accountable owner that nobody is.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from domain.foundry_profile import PROFILE

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "rules" / "field-ownership.md"
MIGRATION_MANIFEST = (
    ROOT / "docs" / "project-management" / "data-migration-manifest.json"
)

#: A profile-field key as it appears in a document cell: `` `a.b` ``.
_FIELD_KEY = re.compile(r"`([a-z_]+\.[a-z_]+)`")


def document() -> str:
    return DOCUMENT.read_text(encoding="utf-8")


def documented_keys() -> set[str]:
    return set(_FIELD_KEY.findall(document()))


def manifest_packages() -> set[str]:
    return set(json.loads(MIGRATION_MANIFEST.read_text(encoding="utf-8"))["valid_packages"])


def row_for(key: str) -> str | None:
    return next(
        (
            line
            for line in document().splitlines()
            if f"`{key}`" in line and line.lstrip().startswith("|")
        ),
        None,
    )


def test_the_document_records_the_running_profile_version():
    assert PROFILE.version in document(), (
        "the document names a different profile version than the module"
    )


@pytest.mark.parametrize("key", sorted(PROFILE.fields), ids=lambda value: value)
def test_every_profile_field_appears_in_the_document(key: str):
    assert key in documented_keys(), (
        f"{key} is in the profile but nowhere in field-ownership.md, so no "
        "maintainer has approved its classification"
    )


@pytest.mark.parametrize(
    "profile_field",
    sorted(PROFILE.deferred_fields(), key=lambda entry: entry.key),
    ids=lambda entry: entry.key,
)
def test_every_deferred_field_documents_its_owning_package(profile_field):
    row = row_for(profile_field.key)

    assert row is not None, f"{profile_field.key} has no table row in the document"
    assert profile_field.owning_package in row, (
        f"{profile_field.key} is owned by package {profile_field.owning_package} "
        f"in the profile, but its documented row does not say so: {row.strip()}"
    )


@pytest.mark.parametrize(
    "profile_field",
    sorted(PROFILE.deferred_fields(), key=lambda entry: entry.key),
    ids=lambda entry: entry.key,
)
def test_every_owning_package_exists_in_the_migration_manifest(profile_field):
    """A deferred field must name a package the controlled manifest knows.

    This is the join between the profile and the migration register. Without it
    a typo would produce a report naming an accountable owner who does not
    exist, which reads as accountability and is not.
    """
    assert profile_field.owning_package in manifest_packages(), (
        f"{profile_field.key} names package {profile_field.owning_package!r}, "
        f"which is not one of the manifest's valid packages"
    )


#: §0's change table names the removed vocabulary deliberately, to say it is
#: gone. That is history and must stay readable; everything after it describes
#: current behaviour and must not mention a correction mode at all.
_CHANGE_TABLE = re.compile(
    r"^### What changed at profile version.*?(?=^## 1\.)", re.MULTILINE | re.DOTALL
)


def test_the_document_does_not_advertise_a_correction_or_writable_mode():
    """The rejected vocabulary must not survive as current-behaviour prose.

    A document still describing a correction allowlist would be read as
    permission by the next implementer, whatever the code does. The §0 change
    table is exempt: naming what was removed is how a reader learns it was.
    """
    body = _CHANGE_TABLE.sub("", document()).lower()

    for phrase in (
        "council-correctable",
        "correction allowlist",
        "compensating correction",
        "protected correction",
    ):
        assert phrase not in body, (
            f"field-ownership.md still describes {phrase!r} outside its change "
            "table; ADR 0008 was rejected and Phase 2 has no correction surface"
        )


def test_the_document_separates_target_ownership_from_current_authority():
    body = document()

    assert "Target ownership and current authority are different questions" in body
    assert "legacy_authority_deferred" in body


def test_fields_with_no_snapshot_path_are_named_as_register_governed():
    """The fields dropped from the profile must still be accounted for.

    They left the profile because no snapshot path feeds them, not because they
    stopped mattering. §5 is where a reader finds out where they went.
    """
    body = document()

    for key in (
        "wallet.moradinium",
        "missions.count",
        "lifestyle.living_cost_weeks",
        "character.downtime_progress",
    ):
        assert f"`{key}`" in body, (
            f"{key} left the profile and is not accounted for in the document"
        )

    assert "governed solely by the controlled migration register" in body.replace(
        "\n", " "
    )
