"""Parser refusals: shape, deployment, folder graph and Actor identity.

Everything here happens before a state-change transaction is opened, so every
refusal is a run that could not have partially committed.
"""
from __future__ import annotations

import unicodedata
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
    assert snapshot.exporter.describe() == "freedom-blades-export 1.0.2"
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

    # The order is the folder *id* sort, not the path sort: `selectable_folders`
    # promises a stable order and takes it from `sorted(selected_folder_ids)`.
    # ACTIVE's id sorts before ARCHIVE's, so it is listed first.
    assert [identity.path for identity in snapshot.selectable_folders()] == [
        "/actors/Characters/Characters (active)",
        "/actors/Characters/Characters (retired)",
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


def test_canonical_order_is_ecmascript_own_property_order():
    """RA-2: array-index keys sort numerically, ahead of every string key.

    Found by previewing a real export, not by a fixture. dnd5e keys scale-value
    advancements by class level, so a real Actor carries `{"1":…,"4":…,"10":…}`.
    A browser exporter emits those numerically however it sorts, because
    `Object.keys` hoists array-index keys — so a lexicographic canonical form
    (`"1","10","4"`) was one no conforming exporter could ever produce.
    """
    encoded = canonical_bytes({"scale": {"10": "c", "4": "b", "1": "a"}})

    assert encoded == b'{"scale":{"1":"a","4":"b","10":"c"}}\n'


def test_the_hoisted_range_ends_at_the_ecmascript_array_index_bound():
    """C-12: only array indices are hoisted, and they end at `2**32 - 2`.

    C-10 wrote the bound as `2**53 - 1`, which is the *integer index* — a
    `String.prototype`/typed-array concept ordinary object enumeration never
    consults. The consequence was a cross-language disagreement (finding I-1),
    not merely a wrong word: the exporter treats `"5000000000"` as an ordinary
    string key and emits it after `"10000000000"`, and this verifier sorted it
    numerically and put it first, so a conforming export would have been
    reported non-canonical.

    `tests/test_exporter_contract.py` asserts the shipped module agrees with
    every line below; this pins the verifier's own half.
    """
    assert canonical_bytes(
        {"4294967295": "b", "4294967294": "a", "7": "small"}
    ) == b'{"7":"small","4294967294":"a","4294967295":"b"}\n'

    # The pair from the finding: numerically 5e9 < 1e10, by code point "1…" < "5…".
    assert (
        canonical_bytes({"5000000000": "five", "10000000000": "ten"})
        == b'{"10000000000":"ten","5000000000":"five"}\n'
    )

    # The old bound's own values are ordinary string keys under the new one.
    assert canonical_bytes(
        {"9007199254740992": "b", "9007199254740991": "a", "11": "small"}
    ) == b'{"11":"small","9007199254740991":"a","9007199254740992":"b"}\n'


def test_only_canonical_integer_keys_count_as_array_indices():
    """`"01"`, `"-1"`, `"1.0"` and `" 1"` are string keys in JavaScript too."""
    encoded = canonical_bytes(
        {"2": "idx", "10": "idx", "01": "str", "-1": "str", "1.0": "str", "b": "str"}
    ).decode()

    assert encoded.index('"2"') < encoded.index('"10"')          # numeric, not "10" < "2"
    assert encoded.index('"10"') < encoded.index('"-1"')         # indices before names
    assert encoded.index('"-1"') < encoded.index('"01"') < encoded.index('"1.0"')
    assert encoded.index('"1.0"') < encoded.index('"b"')


def test_the_verifier_refuses_an_nfc_key_collision():
    """Closed defect — `docs/review/phase-2-canonical-nfc-key-collision.md`.

    The verifier used to emit a document carrying the same key twice, which is
    not a canonical form of anything, while the exporter silently dropped one of
    the two values. Both halves were fixed together in change-log C-16, exporter
    `1.0.6`.

    Refusal rather than a merge: the two source keys are different properties of
    a Foundry document, and no rule in this repository says which one an
    operator meant.

    The two keys are written as escapes rather than as literal characters: they
    are indistinguishable on screen, and a test whose point is that they differ
    should not depend on an editor preserving that.
    """
    composed = "\u00e9"  # LATIN SMALL LETTER E WITH ACUTE
    decomposed = "e\u0301"  # e + COMBINING ACUTE ACCENT
    assert composed != decomposed
    assert unicodedata.normalize("NFC", decomposed) == composed

    for document in (
        {composed: "first", decomposed: "second"},
        {decomposed: "first", composed: "second"},
    ):
        assert len(document) == 2
        with pytest.raises(SnapshotRejected) as refused:
            canonical_bytes(document)
        assert refused.value.code == "nfc_key_collision"


def test_a_collision_refusal_names_its_path_and_never_a_value():
    """A refusal message may say where, never what — as everywhere else here."""
    composed = "\u00e9"
    decomposed = "e\u0301"

    with pytest.raises(SnapshotRejected) as refused:
        canonical_bytes({"flags": {"world": {composed: "a", decomposed: "b"}}})

    message = str(refused.value)
    assert "$.flags.world" in message
    assert "'a'" not in message and "'b'" not in message


def test_one_non_nfc_key_is_normalised_rather_than_refused():
    """Only a collision is ambiguous; a lone decomposed key has one NFC form.

    The order matters as much as the form: `"e" + U+0301` sorts before `"z"` by
    code point and `U+00E9` sorts after it, so an implementation that sorted the
    pre-NFC form would emit these two keys the other way round.
    """
    decomposed = "e\u0301"

    assert canonical_bytes({decomposed: 1, "z": 2}) == '{"z":2,"\u00e9":1}\n'.encode()


def test_string_values_are_normalised_to_nfc_like_the_exporter_s():
    """§1 normalises every string, not only keys — C-16.

    Without this the verifier reproduced a decomposed value verbatim and
    reported the artifact canonical, when the only supported exporter would have
    emitted the composed form and therefore different bytes.
    """
    assert canonical_bytes({"name": "Ame\u0301lie"}) == b'{"name":"Am\xc3\xa9lie"}\n'


def test_an_artifact_whose_keys_collide_under_nfc_is_refused_with_its_checksum():
    """The refusal reaches `parse_snapshot`, and carries the bytes it refused.

    Canonicalisation is otherwise only *reported*. A collision is the exception,
    because such a document has no canonical form and no conforming exporter can
    have produced it: `canonical.js` refuses it before any bytes exist.
    """
    colliding = fx.actor()
    colliding["system"]["tools"] = {
        "\u00e9": {"value": 1},
        "e\u0301": {"value": 2},
    }
    artifact = ingest_bytes(fx.encode(fx.bundle(actors=(colliding,))))

    with pytest.raises(SnapshotRejected) as refused:
        parse_snapshot(artifact, deployment=OBSERVED_DEPLOYMENT)

    assert refused.value.code == "nfc_key_collision"
    # Refused artifacts are auditable against the exact bytes, like every other
    # refusal in the parser.
    assert refused.value.checksum == artifact.checksum


#: `Number::toString` as the exporter emits it, against what `json.dumps` used
#: to emit for the same value — C-17. The right-hand column is the whole defect:
#: every row where the two differ was a conforming export reported
#: non-canonical.
#:
#: `tests/test_exporter_contract.py` asserts the shipped module agrees with each
#: of these; this pins the verifier's own half, as C-12's pair of tests does for
#: key order.
ECMASCRIPT_NUMBERS = [
    # value, canonical text, what `json.dumps` wrote before C-17
    (0.0, "0", "0.0"),
    (-0.0, "0", "-0.0"),
    (1.0, "1", "1.0"),
    (1.5, "1.5", "1.5"),
    (100.0, "100", "100.0"),
    (0.0001, "0.0001", "0.0001"),
    (1e-5, "0.00001", "1e-05"),
    (1e-6, "0.000001", "1e-06"),
    (1e-7, "1e-7", "1e-07"),
    (1e-100, "1e-100", "1e-100"),
    (5e-324, "5e-324", "5e-324"),
    (1e15, "1000000000000000", "1000000000000000.0"),
    (1e16, "10000000000000000", "1e+16"),
    (1e20, "100000000000000000000", "1e+20"),
    (1e21, "1e+21", "1e+21"),
    (1.7976931348623157e308, "1.7976931348623157e+308", "1.7976931348623157e+308"),
    (0.30000000000000004, "0.30000000000000004", "0.30000000000000004"),
    (-1e-7, "-1e-7", "-1e-07"),
    (-1e21, "-1e+21", "-1e+21"),
    (123.456, "123.456", "123.456"),
]


@pytest.mark.parametrize(("value", "expected", "python"), ECMASCRIPT_NUMBERS)
def test_numbers_are_encoded_as_ecmascript_writes_them(value, expected, python):
    """C-17: `json.dumps` is a different function from `JSON.stringify`.

    Python switches to exponent notation at `1e16` and below `1e-4`, ECMAScript
    at `1e21` and below `1e-6`, and Python pads the exponent to two digits. The
    third column records what this encoder used to produce, so the rows that
    were wrong stay visible.
    """
    import json

    assert json.dumps(value) == python  # the old behaviour, for the record
    assert canonical_bytes({"n": value}) == f'{{"n":{expected}}}\n'.encode()


def test_an_integer_literal_is_the_double_the_exporter_would_have_read():
    """`json.loads` keeps an integer exactly; JavaScript has only doubles.

    Re-encoding from Python's `int` would report an artifact canonical against
    bytes no exporter could have produced, because a browser cannot hold
    `9007199254740993` in the first place.
    """
    assert canonical_bytes({"n": 10**20}) == b'{"n":100000000000000000000}\n'
    assert canonical_bytes({"n": 10**21}) == b'{"n":1e+21}\n'
    assert canonical_bytes({"n": 2**53 + 1}) == b'{"n":9007199254740992}\n'


def test_negative_zero_has_the_canonical_form_zero_and_is_not_refused():
    """The exporter refuses to *produce* one; reading one is a different act.

    By the time a document reaches this verifier the sign is already gone from
    JSON — `-0` and `0` are one literal apart and one value. It therefore has a
    canonical form, and an artifact spelling it the other way is reported
    non-canonical like any other, rather than refused as an NFC collision or an
    infinity is.
    """
    assert canonical_bytes({"n": -0.0}) == b'{"n":0}\n'


def test_a_number_outside_the_double_range_is_refused_with_its_checksum():
    """The second document that has no canonical form at all.

    `1e999` reads as an infinity in both languages, JSON cannot express one, and
    every encoding available — `null`, a clamp, the digits again — is a
    different value. The exporter refuses it (`non_finite_number`) before any
    bytes exist; this is the Manager's half. Before C-17 the same artifact
    raised `ValueError` out of `json.dumps` and was not a refusal at all.
    """
    actor = fx.actor()
    actor["system"]["placeholder"] = "REPLACE"
    artifact = ingest_bytes(
        fx.tamper(
            fx.encode(fx.bundle(actors=(actor,))),
            find=b'"REPLACE"',
            replace=b"1e999",
        )
    )

    with pytest.raises(SnapshotRejected) as refused:
        parse_snapshot(artifact, deployment=OBSERVED_DEPLOYMENT)

    assert refused.value.code == "non_finite_number"
    assert refused.value.checksum == artifact.checksum
    assert "$.actors" in str(refused.value)


def test_an_exporter_shaped_number_is_reported_canonical_and_python_s_is_not():
    """The end-to-end shape of C-17, on the flag itself rather than the encoder.

    Both artifacts hold the same double. The first spells it as the exporter
    does and is canonical; the second spells it as `json.dumps` did, and is the
    artifact this Manager used to call canonical while calling the real one
    non-canonical.
    """
    actor = fx.actor()
    actor["system"]["placeholder"] = "REPLACE"
    encoded = fx.encode(fx.bundle(actors=(actor,)))

    def flag(literal: bytes) -> bool:
        artifact = ingest_bytes(fx.tamper(encoded, find=b'"REPLACE"', replace=literal))
        return parse_snapshot(
            artifact, deployment=OBSERVED_DEPLOYMENT
        ).canonical_encoding

    assert flag(b"1e-7") is True
    assert flag(b"1e-07") is False


def test_canonical_ordering_recurses_through_lists_and_objects():
    """The generator bug this guards against encoded every object as `{}`."""
    encoded = canonical_bytes(
        {"outer": [{"10": {"z": 1, "a": 2}, "2": {}}], "a": {"b": {"c": 1}}}
    ).decode()

    assert encoded == '{"a":{"b":{"c":1}},"outer":[{"2":{},"10":{"a":2,"z":1}}]}\n'


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
