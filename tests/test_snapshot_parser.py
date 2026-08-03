"""Parser refusals: shape, deployment, folder graph and Actor identity.

Everything here happens before a state-change transaction is opened, so every
refusal is a run that could not have partially committed.
"""
from __future__ import annotations

from copy import deepcopy

import pytest

from application.foundry.artifact import SnapshotRejected, ingest_bytes
from application.foundry.parser import BundleLimits, canonical_bytes, parse_snapshot
from domain.foundry import OBSERVED_DEPLOYMENT, SupportedDeployment
from tests import foundry_fixtures as fx


def parse(document, *, deployment=OBSERVED_DEPLOYMENT, limits=None):
    artifact = ingest_bytes(fx.encode(document))
    return parse_snapshot(artifact, deployment=deployment, limits=limits)


def refusal(document, **kwargs) -> SnapshotRejected:
    with pytest.raises(SnapshotRejected) as raised:
        parse(document, **kwargs)
    return raised.value


# -- the happy path ------------------------------------------------------------


def test_a_contract_shaped_bundle_parses():
    snapshot = parse(fx.bundle())

    assert snapshot.schema_version == 1
    assert snapshot.exporter.describe() == "freedom-blades-export 1.0.0"
    assert snapshot.world.world_id == "the-guild"
    assert snapshot.exported_at.tzinfo is not None
    assert [str(a.actor_id) for a in snapshot.actors] == [fx.FIRST_ACTOR_ID]


def test_folder_identity_is_the_id_together_with_the_displayed_path():
    snapshot = parse(fx.bundle())

    identity = snapshot.folder_identity(fx.ACTIVE_FOLDER_ID)

    assert str(identity.folder_id) == fx.ACTIVE_FOLDER_ID
    assert identity.path == "/actors/Characters/Characters (active)"
    assert fx.ACTIVE_FOLDER_ID in identity.describe()


def test_two_folders_may_share_a_name_and_stay_distinct():
    document = fx.bundle(
        folders=(
            fx.folder(fx.ROOT_FOLDER_ID, "Characters"),
            fx.folder(fx.ACTIVE_FOLDER_ID, "Active", fx.ROOT_FOLDER_ID),
            fx.folder(fx.ARCHIVE_FOLDER_ID, "Active"),
        ),
        selected_folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID),
    )

    snapshot = parse(document)

    assert snapshot.folder_path(fx.ACTIVE_FOLDER_ID) == "/actors/Characters/Active"
    assert snapshot.folder_path(fx.ARCHIVE_FOLDER_ID) == "/actors/Active"


def test_selectable_folders_are_a_bounded_set_the_manager_chooses_from():
    document = fx.bundle(
        folders=(
            fx.folder(fx.ROOT_FOLDER_ID, "Characters"),
            fx.folder(fx.ACTIVE_FOLDER_ID, "Characters (active)", fx.ROOT_FOLDER_ID),
            fx.folder(fx.ARCHIVE_FOLDER_ID, "Characters (retired)", fx.ROOT_FOLDER_ID),
        ),
        selected_folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ARCHIVE_FOLDER_ID),
        actors=(fx.actor(), fx.actor(fx.SECOND_ACTOR_ID, folder_id=fx.ARCHIVE_FOLDER_ID)),
    )

    snapshot = parse(document)

    assert [identity.path for identity in snapshot.selectable_folders()] == [
        "/actors/Characters/Characters (retired)",
        "/actors/Characters/Characters (active)",
    ]
    assert len(snapshot.actors_in(fx.ACTIVE_FOLDER_ID)) == 1
    assert len(snapshot.actors_in(fx.ARCHIVE_FOLDER_ID)) == 1


def test_an_unselected_folder_cannot_be_imported_from():
    snapshot = parse(fx.bundle())

    with pytest.raises(SnapshotRejected) as raised:
        snapshot.actors_in(fx.ROOT_FOLDER_ID)

    assert raised.value.code == "folder_not_selected"


def test_canonical_encoding_is_reported_but_never_enforced():
    document = fx.bundle()
    canonical = parse(document)
    assert canonical.canonical_encoding is True

    # A bundle written without the canonical separators is still a valid
    # snapshot; it simply has its own identity and a preview warning.
    import json

    loose = json.dumps(document, indent=2).encode("utf-8")
    snapshot = parse_snapshot(
        ingest_bytes(loose), deployment=OBSERVED_DEPLOYMENT
    )

    assert snapshot.canonical_encoding is False
    assert canonical_bytes(document) != loose


# -- shape ---------------------------------------------------------------------


def test_a_non_object_top_level_is_refused():
    assert (
        parse_or_code(b"[1, 2, 3]\n") == "unexpected_top_level"
    )


def parse_or_code(raw: bytes) -> str:
    with pytest.raises(SnapshotRejected) as raised:
        parse_snapshot(ingest_bytes(raw), deployment=OBSERVED_DEPLOYMENT)
    return raised.value.code


def test_invalid_json_is_refused_without_quoting_the_document():
    with pytest.raises(SnapshotRejected) as raised:
        parse_snapshot(
            ingest_bytes(b'{"schema": "x" "oops": 1}'),
            deployment=OBSERVED_DEPLOYMENT,
        )

    assert raised.value.code == "malformed_json"
    assert "oops" not in str(raised.value)


@pytest.mark.parametrize(
    "key",
    ["schema", "schemaVersion", "exporter", "exportedAt", "world", "folders", "actors", "selectedFolderIds"],
)
def test_every_top_level_key_is_required(key):
    assert refusal(fx.without(fx.bundle(), key)).code == "missing_top_level_key"


def test_an_unknown_top_level_key_is_refused_not_ignored():
    # Contract §3: the bundle carries actors and folders and nothing else, so a
    # smuggled collection fails closed rather than being skipped.
    document = fx.with_key(fx.bundle(), "journal", [{"name": "Council notes"}])

    error = refusal(document)

    assert error.code == "unknown_top_level_key"
    assert "journal" in str(error)


def test_a_foreign_schema_is_refused():
    assert refusal(fx.with_key(fx.bundle(), "schema", "other")).code == "unsupported_schema"


@pytest.mark.parametrize("version", [0, 2, 99])
def test_an_unsupported_exporter_schema_version_fails_closed(version):
    error = refusal(fx.bundle(schema_version=version))

    assert error.code == "unsupported_schema_version"
    assert str(version) in str(error)
    assert "1" in str(error)


def test_a_non_integer_schema_version_is_refused():
    assert refusal(fx.bundle(schema_version="1")).code == "unsupported_schema_version"


@pytest.mark.parametrize(
    "exporter",
    [{"id": "", "version": "1.0.0"}, {"id": "x"}, {"id": "x", "version": "!!"}, "1.0.0"],
)
def test_a_malformed_exporter_block_is_refused(exporter):
    assert refusal(fx.bundle(exporter=exporter)).code == "malformed_exporter"


@pytest.mark.parametrize(
    "value", ["yesterday", "2026-08-02T09:15:00", "", 12345]
)
def test_a_malformed_export_timestamp_is_refused(value):
    assert refusal(fx.bundle(exported_at=value)).code == "malformed_timestamp"


# -- deployment ----------------------------------------------------------------


def test_the_wrong_world_is_refused_and_names_both_values():
    document = fx.bundle()
    document["world"]["id"] = "some-other-world"

    error = refusal(document)

    assert error.code == "unsupported_deployment"
    assert "some-other-world" in str(error)
    assert "the-guild" in str(error)


@pytest.mark.parametrize(
    ("key", "value"),
    [("coreVersion", "15.1"), ("systemId", "pf2e"), ("systemVersion", "5.4.0")],
)
def test_the_version_tuple_is_validated_as_a_tuple(key, value):
    document = fx.bundle()
    document["world"][key] = value

    error = refusal(document)

    assert error.code == "unsupported_deployment"
    assert value in str(error)


def test_every_deployment_difference_is_named_individually():
    document = fx.bundle()
    document["world"]["coreVersion"] = "15.1"
    document["world"]["systemVersion"] = "6.0.0"

    message = str(refusal(document))

    assert "15.1" in message and "6.0.0" in message


def test_a_reconfigured_deployment_accepts_its_own_tuple():
    deployment = SupportedDeployment(
        world_id="the-guild",
        core_version="15.1",
        system_id="dnd5e",
        system_version="6.0.0",
    )
    document = fx.bundle()
    document["world"]["coreVersion"] = "15.1"
    document["world"]["systemVersion"] = "6.0.0"

    snapshot = parse(document, deployment=deployment)

    assert snapshot.world.version_tuple == ("15.1", "dnd5e", "6.0.0")


@pytest.mark.parametrize("key", sorted({"id", "title", "coreVersion", "systemId", "systemVersion"}))
def test_a_missing_world_key_is_refused(key):
    document = fx.bundle()
    document["world"].pop(key)

    assert refusal(document).code == "malformed_world"


def test_an_extra_world_key_is_refused():
    document = fx.bundle()
    document["world"]["instanceUrl"] = "https://foundry1.rpgworld.org"

    assert refusal(document).code == "malformed_world"


# -- folder graph --------------------------------------------------------------


def test_a_duplicate_folder_id_is_ambiguous_and_refused():
    document = fx.bundle(
        folders=(
            fx.folder(fx.ACTIVE_FOLDER_ID, "Characters (active)"),
            fx.folder(fx.ACTIVE_FOLDER_ID, "Characters (also active)"),
        )
    )

    assert refusal(document).code == "duplicate_folder_id"


def test_a_missing_parent_folder_is_refused_because_the_path_is_unpresentable():
    document = fx.bundle(
        folders=(fx.folder(fx.ACTIVE_FOLDER_ID, "Characters (active)", fx.ROOT_FOLDER_ID),)
    )

    assert refusal(document).code == "unknown_parent_folder"


def test_a_folder_cycle_is_refused():
    document = fx.bundle(
        folders=(
            fx.folder(fx.ACTIVE_FOLDER_ID, "A", fx.ROOT_FOLDER_ID),
            fx.folder(fx.ROOT_FOLDER_ID, "B", fx.ACTIVE_FOLDER_ID),
        )
    )

    assert refusal(document).code == "folder_cycle"


def test_a_malformed_folder_id_is_refused():
    document = fx.bundle(folders=(fx.folder("short", "Characters (active)"),))

    assert refusal(document).code == "malformed_folder_id"


def test_an_empty_selection_is_refused():
    document = fx.bundle(selected_folder_ids=())

    assert refusal(document).code == "empty_selection"


def test_a_selection_naming_an_absent_folder_is_refused():
    document = fx.bundle(selected_folder_ids=(fx.ARCHIVE_FOLDER_ID,))

    assert refusal(document).code == "unknown_selected_folder"


def test_a_duplicated_selection_entry_is_refused():
    document = fx.bundle(selected_folder_ids=(fx.ACTIVE_FOLDER_ID, fx.ACTIVE_FOLDER_ID))

    assert refusal(document).code == "duplicate_selected_folder"


def test_the_selected_folder_set_is_bounded():
    folders = tuple(
        fx.folder(f"fold{index:012d}", f"Folder {index}") for index in range(9)
    )
    document = fx.bundle(
        folders=folders,
        selected_folder_ids=tuple(entry["id"] for entry in folders),
        actors=(),
    )

    assert refusal(document).code == "too_many_selected_folders"


def test_the_folder_count_is_bounded():
    folders = tuple(
        fx.folder(f"fold{index:012d}", f"Folder {index}") for index in range(9)
    )
    document = fx.bundle(
        folders=folders,
        selected_folder_ids=(folders[0]["id"],),
        actors=(),
    )

    error = refusal(document, limits=BundleLimits(max_folders=4))

    assert error.code == "too_many_folders"


# -- Actor identity ------------------------------------------------------------


def test_a_null_actor_id_is_refused_and_explains_the_per_actor_export_trap():
    document = fx.bundle(actors=(fx.actor(),))
    document["actors"][0]["id"] = None

    error = refusal(document)

    assert error.code == "missing_actor_id"
    assert "_id" in str(error)


@pytest.mark.parametrize("value", ["short", "way-too-long-for-a-document-id", "!!!!!!!!!!!!!!!!"])
def test_a_malformed_actor_id_is_refused(value):
    document = fx.bundle(actors=(fx.actor(),))
    document["actors"][0]["id"] = value

    assert refusal(document).code == "malformed_actor_id"


def test_a_duplicate_actor_id_is_ambiguous_and_refused():
    document = fx.bundle(actors=(fx.actor(), fx.actor(name="Another Testcharacter")))

    error = refusal(document)

    assert error.code == "duplicate_actor_id"


def test_two_actors_may_share_a_display_name_under_distinct_ids():
    document = fx.bundle(
        actors=(
            fx.actor(fx.FIRST_ACTOR_ID, name="Testcharacter"),
            fx.actor(fx.SECOND_ACTOR_ID, name="Testcharacter"),
        )
    )

    snapshot = parse(document)

    assert len(snapshot.actors) == 2


def test_an_actor_outside_the_exported_selection_is_refused():
    document = fx.bundle(
        folders=(
            fx.folder(fx.ACTIVE_FOLDER_ID, "Characters (active)"),
            fx.folder(fx.ARCHIVE_FOLDER_ID, "Characters (retired)"),
        ),
        selected_folder_ids=(fx.ACTIVE_FOLDER_ID,),
        actors=(fx.actor(folder_id=fx.ARCHIVE_FOLDER_ID),),
    )

    assert refusal(document).code == "actor_outside_selection"


def test_an_unknown_actor_key_is_refused_so_ownership_cannot_be_smuggled_in():
    document = fx.bundle(actors=(fx.actor(),))
    document["actors"][0]["ownership"] = {"default": 0, "abc": 3}

    error = refusal(document)

    assert error.code == "unknown_actor_key"
    assert "ownership" in str(error)


@pytest.mark.parametrize("key", ["name", "system", "items", "folderId"])
def test_a_missing_actor_key_is_refused(key):
    document = fx.bundle(actors=(fx.actor(),))
    document["actors"][0].pop(key)

    assert refusal(document).code == "malformed_actor"


def test_an_untyped_embedded_item_is_refused():
    broken = deepcopy(fx.actor())
    broken["items"].append({"name": "Mystery", "system": {}})
    document = fx.bundle(actors=(broken,))

    error = refusal(document)

    assert error.code == "malformed_actor"
    assert "document type" in str(error)


def test_the_actor_count_is_bounded():
    actors = tuple(
        fx.actor(f"actor{index:011d}", name=f"Testcharacter {index}")
        for index in range(6)
    )
    document = fx.bundle(actors=actors)

    assert refusal(document, limits=BundleLimits(max_actors=3)).code == "too_many_actors"


def test_the_embedded_item_count_is_bounded():
    crowded = deepcopy(fx.actor())
    crowded["items"].extend(
        {"type": "loot", "name": f"Pebble {index}", "system": {}} for index in range(50)
    )
    document = fx.bundle(actors=(crowded,))

    error = refusal(document, limits=BundleLimits(max_items_per_actor=10))

    assert error.code == "too_many_items"


def test_item_types_are_reported_for_diagnostics():
    snapshot = parse(fx.bundle())

    assert "class" in snapshot.actors[0].item_types()
