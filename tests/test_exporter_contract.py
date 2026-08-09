"""The cross-language contract: the exporter's real output, the Manager's real parser.

The Foundry module and the Manager are two implementations of one contract in
two languages. Each has its own tests, and each can be entirely self-consistent
while disagreeing with the other — which is the failure this file exists to
prevent, and the only kind that no single-language test can see.

So this is not a golden *file*. A committed golden artifact is a third
implementation: it is right on the day it is written and silently stale
afterwards, because nothing regenerates it. Instead the exporter's actual
serialization path is executed, and the bytes it produces are handed to
`ingest_bytes` and `parse_snapshot` — the same two functions a real submission
goes through.

The bundle is synthetic and is built by `foundry-module/tests/fixtures.mjs`.
Nothing here writes a file, and no real Actor data is involved.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from application.foundry.artifact import ingest_bytes
from application.foundry.parser import canonical_bytes, parse_snapshot
from domain.foundry import EXPORT_SCHEMA, OBSERVED_DEPLOYMENT

MODULE = Path(__file__).resolve().parents[1] / "foundry-module"
EMITTER = MODULE / "tests" / "emit-golden.mjs"

#: The folder ids the exporter's synthetic world uses. Kept here rather than
#: imported, because importing them would mean parsing JavaScript from Python;
#: `test_the_fixture_ids_match` asserts they are still the fixture's.
ACTIVE_FOLDER_ID = "actvQwErTyUiOpAs"
ROOT_FOLDER_ID = "rootQwErTyUiOpAs"
FIRST_ACTOR_ID = "5tYuIoPaSdFgHj6K"
SECOND_ACTOR_ID = "9kQpZ2mNbVcXsAe1"
NESTED_ACTOR_ID = "7hJkLmNpQrStUvWx"


def node() -> str:
    executable = shutil.which("node")
    if executable is None:
        pytest.skip(
            "node is not available, so the exporter's serialization path cannot "
            "be executed. This test is the only check that the JavaScript "
            "exporter and the Python parser agree; a run without it has not "
            "verified that."
        )
    return executable


@pytest.fixture(scope="module")
def emitted() -> bytes:
    result = subprocess.run(
        [
            node(),
            str(EMITTER),
            OBSERVED_DEPLOYMENT.world_id,
            OBSERVED_DEPLOYMENT.core_version,
            OBSERVED_DEPLOYMENT.system_id,
            OBSERVED_DEPLOYMENT.system_version,
            ACTIVE_FOLDER_ID,
        ],
        cwd=MODULE,
        capture_output=True,
        check=True,
    )
    return result.stdout


def test_the_exporter_s_output_is_accepted_by_the_real_parser(emitted):
    artifact = ingest_bytes(emitted)

    snapshot = parse_snapshot(artifact, deployment=OBSERVED_DEPLOYMENT)

    assert snapshot.schema_version == 1
    assert snapshot.exporter.id == "freedom-blades-export"
    assert snapshot.world.world_id == OBSERVED_DEPLOYMENT.world_id
    assert snapshot.world.core_version == OBSERVED_DEPLOYMENT.core_version
    assert snapshot.world.system_version == OBSERVED_DEPLOYMENT.system_version
    assert snapshot.selected_folder_ids == (ACTIVE_FOLDER_ID,)


def test_the_parser_agrees_the_exporter_s_encoding_is_canonical(emitted):
    """The exporter's obligation, checked by the Manager's own definition of it."""
    artifact = ingest_bytes(emitted)
    snapshot = parse_snapshot(artifact, deployment=OBSERVED_DEPLOYMENT)

    assert snapshot.canonical_encoding is True
    # …and directly: the Python canonical encoder produces the same bytes.
    assert canonical_bytes(json.loads(emitted.decode("utf-8"))) == emitted


def test_the_full_ancestor_path_survives_the_round_trip(emitted):
    snapshot = parse_snapshot(ingest_bytes(emitted), deployment=OBSERVED_DEPLOYMENT)

    assert snapshot.folder_path(ACTIVE_FOLDER_ID) == (
        "/actors/Characters/Characters (active)"
    )
    assert ROOT_FOLDER_ID in snapshot.folders


def test_real_actor_ids_survive_and_out_of_scope_actors_do_not(emitted):
    snapshot = parse_snapshot(ingest_bytes(emitted), deployment=OBSERVED_DEPLOYMENT)

    identifiers = {str(actor.actor_id) for actor in snapshot.actors}
    assert identifiers == {FIRST_ACTOR_ID, SECOND_ACTOR_ID}
    # In a sub-folder of the selection, so out of scope.
    assert NESTED_ACTOR_ID not in identifiers


def test_the_embedded_item_shape_is_the_one_the_parser_classifies(emitted):
    snapshot = parse_snapshot(ingest_bytes(emitted), deployment=OBSERVED_DEPLOYMENT)

    first = next(
        actor for actor in snapshot.actors if str(actor.actor_id) == FIRST_ACTOR_ID
    )
    assert first.item_types() == ("class", "feat")


def test_the_exporter_emits_no_key_the_contract_forbids(emitted):
    document = json.loads(emitted.decode("utf-8"))

    assert document["schema"] == EXPORT_SCHEMA
    assert set(document) == {
        "schema",
        "schemaVersion",
        "exporter",
        "exportedAt",
        "world",
        "selectedFolderIds",
        "folders",
        "actors",
    }
    for actor in document["actors"]:
        assert set(actor) <= {"id", "folderId", "name", "img", "system", "items"}
    rendered = emitted.decode("utf-8")
    for forbidden in ("ownership", "_stats", "prototypeToken", "xY7SyntheticUser"):
        assert forbidden not in rendered


def test_a_changed_byte_is_a_different_snapshot(emitted):
    tampered = emitted.replace(b'"levels":9', b'"levels":8', 1)
    assert tampered != emitted

    assert ingest_bytes(tampered).checksum != ingest_bytes(emitted).checksum


def test_a_bundle_from_another_deployment_is_refused_by_the_parser():
    """The tuple check holds across the boundary as well as inside the module.

    `bundle.test.mjs` proves the exporter refuses a world it was not configured
    for. This proves the other half: a bundle that *was* legitimately exported
    from a different deployment is refused by the Manager rather than imported.
    """
    result = subprocess.run(
        [node(), str(EMITTER), "another-world", "13.999", "dnd5e", "5.3.3"],
        cwd=MODULE,
        capture_output=True,
    )
    assert result.returncode == 0
    with pytest.raises(Exception) as refusal:
        parse_snapshot(
            ingest_bytes(result.stdout), deployment=OBSERVED_DEPLOYMENT
        )
    assert getattr(refusal.value, "code", None) == "unsupported_deployment"


def test_the_fixture_ids_match_the_javascript_fixture():
    """Guards the ids duplicated at the top of this file against drift."""
    source = (MODULE / "tests" / "fixtures.mjs").read_text(encoding="utf-8")
    for name, value in (
        ("ACTIVE_FOLDER_ID", ACTIVE_FOLDER_ID),
        ("ROOT_FOLDER_ID", ROOT_FOLDER_ID),
        ("FIRST_ACTOR_ID", FIRST_ACTOR_ID),
        ("SECOND_ACTOR_ID", SECOND_ACTOR_ID),
        ("NESTED_ACTOR_ID", NESTED_ACTOR_ID),
    ):
        assert f'{name} = "{value}"' in source


def test_both_module_manifests_declare_one_version():
    """`exporter.version` reaches checksum-bearing audit history.

    `main.js` feeds `module.json`'s version into the bundle, so it lands in
    `foundry_snapshots.exporter_version`. Two builds sharing a version — or the
    two manifests disagreeing — makes that history unable to say which module
    produced a row, so the pair is pinned rather than kept in step by hand.
    """
    module = json.loads((MODULE / "module.json").read_text(encoding="utf-8"))
    package = json.loads((MODULE / "package.json").read_text(encoding="utf-8"))

    assert module["version"] == package["version"]
    assert module["id"] == package["name"]


def test_the_module_carries_no_dependency_lockfile_or_build_step():
    manifest = json.loads((MODULE / "package.json").read_text(encoding="utf-8"))

    assert "dependencies" not in manifest
    assert "devDependencies" not in manifest
    assert manifest["type"] == "module"
    assert not (MODULE / "package-lock.json").exists()
    assert not (MODULE / "node_modules").exists()
