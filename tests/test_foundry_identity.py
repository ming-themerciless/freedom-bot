"""Snapshot identity value objects: an identity is never a name."""
from __future__ import annotations

import hashlib

import pytest

from domain.foundry import (
    OBSERVED_DEPLOYMENT,
    FolderIdentity,
    FoundryActorId,
    FoundryFolderId,
    InvalidIdentityError,
    SnapshotChecksum,
    SupportedDeployment,
    WorldIdentity,
)


def test_a_checksum_is_the_sha256_of_the_bytes():
    checksum = SnapshotChecksum.of(b"synthetic")

    assert checksum.hex_digest == hashlib.sha256(b"synthetic").hexdigest()
    assert str(checksum) == checksum.hex_digest
    assert checksum.short == checksum.hex_digest[:12]


@pytest.mark.parametrize(
    "value", ["", "abc", "Z" * 64, "0" * 63, "0" * 65, "A" * 64]
)
def test_a_checksum_must_be_64_lowercase_hex_characters(value):
    with pytest.raises(InvalidIdentityError):
        SnapshotChecksum(value)


def test_checksums_compare_by_value():
    assert SnapshotChecksum.of(b"a") == SnapshotChecksum.of(b"a")
    assert SnapshotChecksum.of(b"a") != SnapshotChecksum.of(b"b")


@pytest.mark.parametrize(
    "value",
    ["", "short", "5tYuIoPaSdFgHj6", "5tYuIoPaSdFgHj6KK", "5tYuIoPaSdFgHj6-", None],
)
def test_a_document_id_must_be_16_alphanumeric_characters(value):
    with pytest.raises(InvalidIdentityError):
        FoundryActorId(str(value))


def test_a_document_id_refusal_explains_the_per_actor_export_trap():
    with pytest.raises(InvalidIdentityError) as raised:
        FoundryActorId("null")

    assert "_id" in str(raised.value)


def test_actor_and_folder_ids_are_different_identities():
    # Structurally identical, semantically distinct: a folder id must never
    # compare equal to an actor id that happens to share its characters.
    assert FoundryActorId("5tYuIoPaSdFgHj6K") != FoundryFolderId("5tYuIoPaSdFgHj6K")
    assert FoundryActorId("5tYuIoPaSdFgHj6K") == FoundryActorId("5tYuIoPaSdFgHj6K")


def test_a_folder_identity_carries_its_path_as_well_as_its_id():
    identity = FolderIdentity(
        folder_id=FoundryFolderId("actvQwErTyUiOpAs"),
        path="/actors/Characters/Characters (active)",
    )

    assert "actvQwErTyUiOpAs" in identity.describe()
    assert "Characters (active)" in identity.describe()


def test_a_folder_path_must_be_absolute():
    with pytest.raises(InvalidIdentityError):
        FolderIdentity(folder_id=FoundryFolderId("actvQwErTyUiOpAs"), path="Characters")


def test_two_folders_sharing_a_name_are_different_identities():
    left = FolderIdentity(FoundryFolderId("aaaaQwErTyUiOpAs"), "/actors/A/Active")
    right = FolderIdentity(FoundryFolderId("bbbbQwErTyUiOpAs"), "/actors/B/Active")

    assert left != right


def world(**overrides) -> WorldIdentity:
    values = {
        "world_id": "the-guild",
        "title": "The Guild",
        "core_version": "14.365",
        "system_id": "dnd5e",
        "system_version": "5.3.3",
    }
    values.update(overrides)
    return WorldIdentity(**values)


def test_the_observed_deployment_accepts_its_own_world():
    assert OBSERVED_DEPLOYMENT.mismatches(world()) == ()


@pytest.mark.parametrize(
    ("override", "expected"),
    [
        ({"world_id": "other"}, "world id"),
        ({"core_version": "15.0"}, "Foundry core"),
        ({"system_id": "pf2e"}, "game system"),
        ({"system_version": "5.4.0"}, "system version"),
    ],
)
def test_every_deployment_difference_is_named_individually(override, expected):
    differences = OBSERVED_DEPLOYMENT.mismatches(world(**override))

    assert len(differences) == 1
    assert expected in differences[0]


def test_several_differences_are_all_reported():
    differences = OBSERVED_DEPLOYMENT.mismatches(
        world(core_version="15.0", system_version="6.0.0")
    )

    assert len(differences) == 2


def test_compatibility_is_keyed_on_the_tuple_not_on_one_member():
    assert world().version_tuple == ("14.365", "dnd5e", "5.3.3")


def test_the_deployment_is_configuration_not_a_constant():
    other = SupportedDeployment(
        world_id="scratch", core_version="14.365", system_id="dnd5e", system_version="5.3.3"
    )

    assert other.mismatches(world(world_id="scratch")) == ()


@pytest.mark.parametrize(
    "override",
    [{"world_id": " "}, {"core_version": ""}, {"system_id": ""}, {"system_version": " "}],
)
def test_a_world_identity_requires_its_parts(override):
    with pytest.raises(InvalidIdentityError):
        world(**override)


def test_a_world_describes_itself_without_an_instance():
    # ADR 0006: the world is the identity, the instance is a transport endpoint.
    description = world().describe()

    assert "the-guild" in description
    assert "foundry1" not in description
    assert "30001" not in description
