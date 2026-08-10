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

from application.foundry.artifact import SnapshotRejected, ingest_bytes
from application.foundry.parser import canonical_bytes, parse_snapshot
from domain.foundry import EXPORT_SCHEMA, OBSERVED_DEPLOYMENT

MODULE = Path(__file__).resolve().parents[1] / "foundry-module"
EMITTER = MODULE / "tests" / "emit-golden.mjs"
#: Encodes caller-chosen documents through the same `canonicalBytes` the module
#: ships, which is how the array-index boundary below is reached at all.
CANONICAL_EMITTER = MODULE / "tests" / "emit-canonical.mjs"

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


#: The ECMAScript array-index boundary, as documents both implementations must
#: encode identically. Finding I-1 (change-log C-12): the contract and the
#: verifier called every canonical decimal in `[0, 2**53 - 1]` numerically
#: ordered, but ordinary object enumeration hoists only **array indices**, which
#: end at `2**32 - 2`. Anything larger is an ordinary string key and sorts by
#: code point.
#:
#: The committed bundle fixture cannot reach this: its integer-like keys are
#: dnd5e class levels, all one or two digits, and every one of them is an array
#: index under either rule. Only documents chosen for the boundary expose it,
#: which is why they are listed here rather than folded into the golden bundle.
#:
#: Each entry is `(name, document, expected canonical text)`. The expectation is
#: written out rather than derived, so that a change to *both* implementations at
#: once still has to argue with a third statement of the rule.
KEY_ORDER_BOUNDARY = [
    (
        "the smallest array index",
        {"0": "zero"},
        '{"0":"zero"}',
    ),
    (
        "array indices sort numerically, not by code point",
        {"10": "ten", "2": "two", "1": "one"},
        '{"1":"one","2":"two","10":"ten"}',
    ),
    (
        "the largest array index and the first key above it",
        {"4294967295": "not-an-index", "4294967294": "largest-index", "7": "small"},
        '{"7":"small","4294967294":"largest-index","4294967295":"not-an-index"}',
    ),
    (
        "above the boundary, numeric and code-point order disagree",
        # The exact disagreement finding I-1 reported. Numerically 5e9 < 1e10;
        # by code point "1…" < "5…". Both are ordinary string keys, so the
        # code-point order is the canonical one.
        {"5000000000": "five", "10000000000": "ten"},
        '{"10000000000":"ten","5000000000":"five"}',
    ),
    (
        "and the encoding does not depend on the order the keys arrived in",
        {"10000000000": "ten", "5000000000": "five"},
        '{"10000000000":"ten","5000000000":"five"}',
    ),
    (
        "the old bound's own values are ordinary string keys",
        {"9007199254740992": "b", "9007199254740991": "a", "11": "small"},
        '{"11":"small","9007199254740991":"a","9007199254740992":"b"}',
    ),
    (
        "noncanonical decimals are ordinary string keys",
        {"01": 1, "-1": 2, "1.0": 3, "1": 4, "0": 5, " 1": 6, "+1": 7, "1e2": 8},
        '{"0":5,"1":4," 1":6,"+1":7,"-1":2,"01":1,"1.0":3,"1e2":8}',
    ),
    (
        "the rule recurses through nested objects and arrays",
        {
            "b": {"10000000000": 1, "5000000000": 2, "7": 3, "4294967295": 4},
            "a": [{"20000000000": 1, "3000000000": 2}],
        },
        '{"a":[{"3000000000":2,"20000000000":1}],'
        '"b":{"7":3,"10000000000":1,"4294967295":4,"5000000000":2}}',
    ),
]


@pytest.fixture(scope="module")
def boundary_encodings() -> list[str]:
    """`canonicalBytes` of each boundary document, from the shipped module."""
    documents = [document for _, document, _ in KEY_ORDER_BOUNDARY]
    result = subprocess.run(
        [node(), str(CANONICAL_EMITTER)],
        cwd=MODULE,
        input=json.dumps(documents).encode("utf-8"),
        capture_output=True,
        check=True,
    )
    # Every canonical document is one line: no whitespace is emitted and every
    # newline inside a string is escaped, so the trailing LF is a safe separator.
    lines = result.stdout.decode("utf-8").split("\n")
    assert lines[-1] == "", "the exporter must end every document with one LF"
    return lines[:-1]


@pytest.mark.parametrize(
    ("name", "document", "expected"),
    KEY_ORDER_BOUNDARY,
    ids=[name for name, _, _ in KEY_ORDER_BOUNDARY],
)
def test_the_exporter_orders_keys_at_the_array_index_boundary_as_the_contract_says(
    name, document, expected, boundary_encodings
):
    index = [entry[0] for entry in KEY_ORDER_BOUNDARY].index(name)

    assert boundary_encodings[index] == expected


@pytest.mark.parametrize(
    ("name", "document", "expected"),
    KEY_ORDER_BOUNDARY,
    ids=[name for name, _, _ in KEY_ORDER_BOUNDARY],
)
def test_the_verifier_orders_keys_at_the_array_index_boundary_as_the_contract_says(
    name, document, expected
):
    assert canonical_bytes(document).decode("utf-8") == f"{expected}\n"


def test_exporter_and_verifier_agree_byte_for_byte_across_the_boundary(
    boundary_encodings,
):
    """The check neither single-language test can make.

    Both sides above are asserted against a written-out expectation, and this
    asserts they are the same bytes. It is the assertion that failed before
    C-12: the exporter emitted `{"10000000000":…,"5000000000":…}` and the
    verifier `{"5000000000":…,"10000000000":…}`, so `canonical_encoding` would
    have been reported false for a conforming export.
    """
    for (name, document, _), emitted in zip(
        KEY_ORDER_BOUNDARY, boundary_encodings, strict=True
    ):
        assert canonical_bytes(document).decode("utf-8") == f"{emitted}\n", name


#: Documents at the **NFC boundary**, which the two implementations must encode
#: identically for the same reason as the array-index boundary above: each was
#: self-consistent while disagreeing with the other.
#:
#: The defect (`docs/review/phase-2-canonical-nfc-key-collision.md`, change-log
#: C-16, exporter `1.0.6`): the exporter sorted keys by their pre-NFC form and
#: inserted them under their post-NFC form, and the verifier did not normalise
#: keys at all. Neither the golden bundle nor any earlier boundary document could
#: see it — every key in them is ASCII, for which NFC is the identity.
#:
#: Same shape as `KEY_ORDER_BOUNDARY`: `(name, document, expected canonical
#: text)`, written out rather than derived. Escapes rather than literal
#: characters throughout, because the two forms are indistinguishable on screen.
NFC_BOUNDARY = [
    (
        "a decomposed key is emitted in its composed form",
        {"e\u0301": 1},
        '{"\u00e9":1}',
    ),
    (
        "normalisation happens before the sort, not after",
        # "e" + U+0301 sorts before "z" by code point; U+00E9 sorts after it. An
        # implementation that sorted the source form emits these the other way.
        {"e\u0301": 1, "z": 2},
        '{"z":2,"\u00e9":1}',
    ),
    (
        "values are normalised as well as keys",
        {"name": "Ame\u0301lie"},
        '{"name":"Am\u00e9lie"}',
    ),
    (
        "an already-composed document is unchanged",
        {"\u00e9": "Am\u00e9lie"},
        '{"\u00e9":"Am\u00e9lie"}',
    ),
    (
        "normalisation recurses through nested objects and arrays",
        {"a": [{"e\u0301": ["Ame\u0301lie"]}]},
        '{"a":[{"\u00e9":["Am\u00e9lie"]}]}',
    ),
]

#: One document, refused by both implementations. `é` as U+00E9 and as
#: U+0065 U+0301 are two distinct properties of a Foundry document that share one
#: NFC form, so the canonical form cannot hold both — and no rule here says which
#: one an operator meant. The exporter used to let the second write overwrite the
#: first and emit a document short one value; the verifier used to emit the same
#: key twice, which is a canonical form of nothing.
NFC_COLLISION = {"\u00e9": "first", "e\u0301": "second"}


@pytest.fixture(scope="module")
def nfc_encodings() -> list[str]:
    """`canonicalBytes` of each NFC boundary document, from the shipped module."""
    documents = [document for _, document, _ in NFC_BOUNDARY]
    result = subprocess.run(
        [node(), str(CANONICAL_EMITTER)],
        cwd=MODULE,
        input=json.dumps(documents).encode("utf-8"),
        capture_output=True,
        check=True,
    )
    lines = result.stdout.decode("utf-8").split("\n")
    assert lines[-1] == "", "the exporter must end every document with one LF"
    return lines[:-1]


@pytest.mark.parametrize(
    ("name", "document", "expected"),
    NFC_BOUNDARY,
    ids=[name for name, _, _ in NFC_BOUNDARY],
)
def test_the_exporter_normalises_to_nfc_as_the_contract_says(
    name, document, expected, nfc_encodings
):
    index = [entry[0] for entry in NFC_BOUNDARY].index(name)

    assert nfc_encodings[index] == expected


@pytest.mark.parametrize(
    ("name", "document", "expected"),
    NFC_BOUNDARY,
    ids=[name for name, _, _ in NFC_BOUNDARY],
)
def test_the_verifier_normalises_to_nfc_as_the_contract_says(name, document, expected):
    assert canonical_bytes(document).decode("utf-8") == f"{expected}\n"


def test_exporter_and_verifier_agree_byte_for_byte_over_the_nfc_boundary(
    nfc_encodings,
):
    """The check neither single-language test can make — C-12's shape, C-16's bug.

    Before C-16 this failed on the first two entries: the exporter emitted the
    composed key but had sorted the decomposed one, and the verifier emitted the
    decomposed key unchanged, so a conforming export carrying any non-NFC key
    would have been reported non-canonical.
    """
    for (name, document, _), emitted in zip(
        NFC_BOUNDARY, nfc_encodings, strict=True
    ):
        assert canonical_bytes(document).decode("utf-8") == f"{emitted}\n", name


def test_both_implementations_refuse_an_nfc_key_collision_with_the_same_code():
    """A refusal is part of the contract, so the two must agree on it too.

    Neither may resolve the collision: the exporter drops nothing silently, and
    the verifier never invents a canonical form for a document that has none.
    """
    assert len(NFC_COLLISION) == 2

    refused = subprocess.run(
        [node(), str(CANONICAL_EMITTER)],
        cwd=MODULE,
        input=json.dumps([NFC_COLLISION]).encode("utf-8"),
        capture_output=True,
        check=False,
    )

    assert refused.returncode == 1, "the exporter emitted bytes for a collision"
    assert refused.stdout == b""
    assert json.loads(refused.stderr.decode("utf-8"))["code"] == "nfc_key_collision"

    with pytest.raises(SnapshotRejected) as rejection:
        canonical_bytes(NFC_COLLISION)

    assert rejection.value.code == "nfc_key_collision"


#: Documents at the **number boundary**, the third case of the shape above and
#: for the third time the same defect: each implementation was self-consistent
#: and the two disagreed.
#:
#: The defect (change-log **C-17**, 2026-08-10, verifier only): the Manager
#: encoded numbers with `json.dumps`, whose float formatting is a different
#: function from `JSON.stringify`'s. Python switches to exponent notation at
#: `1e16` and below `1e-4`; ECMAScript switches at `1e21` and below `1e-6`, and
#: does not pad the exponent to two digits. So a conforming export carrying
#: `1e20` or `1e-7` was reported non-canonical, and dnd5e carries fractional
#: values — `system.attributes.encumbrance` multipliers, spell scaling, currency
#: weight — so the flag was as reachable here as RA-2 made it for key order.
#:
#: Neither earlier boundary could see it: every number in the golden bundle and
#: in both boundary tables above is a small integer, which the two languages
#: format identically. Only numbers chosen for the thresholds expose it.
#:
#: Same shape as the tables above: `(name, document, expected canonical text)`,
#: written out rather than derived, so a change to both implementations at once
#: still has to argue with a third statement of the rule.
NUMBER_BOUNDARY = [
    (
        "an integral value carries no decimal point",
        # `json.dumps` writes a Python float as `1.0`; the exporter has one
        # number type and writes `1`. Nothing in the golden bundle is a float,
        # which is why nothing caught this.
        {"a": 1.0, "b": 0, "c": 0.0},
        '{"a":1,"b":0,"c":0}',
    ),
    (
        "the large threshold is 1e21, not Python's 1e16",
        {"a": 1e20, "b": 1e21},
        '{"a":100000000000000000000,"b":1e+21}',
    ),
    (
        "and it does not depend on the literal having been written as a float",
        # The same two values as integers. `json.loads` reads these as Python
        # `int`, and the contract's numbers are doubles, so both must encode
        # exactly as the pair above.
        {"a": 10**20, "b": 10**21},
        '{"a":100000000000000000000,"b":1e+21}',
    ),
    (
        "the small threshold is 1e-6, and the exponent is not zero-padded",
        # `json.dumps` emits `1e-06` and `1e-07` for these two.
        {"a": 1e-6, "b": 1e-7},
        '{"a":0.000001,"b":1e-7}',
    ),
    (
        "exponents of more than one digit, in both directions",
        {"a": 1e100, "b": 1e-100},
        '{"a":1e+100,"b":1e-100}',
    ),
    (
        "the ends of the double range",
        {"max": 1.7976931348623157e308, "min": 5e-324},
        '{"max":1.7976931348623157e+308,"min":5e-324}',
    ),
    (
        "the shortest round-tripping digits, not seventeen of them",
        {"a": 0.1, "b": 0.2, "c": 0.30000000000000004},
        '{"a":0.1,"b":0.2,"c":0.30000000000000004}',
    ),
    (
        "an integer literal past 2**53 is the double both languages read",
        # Python would carry `9007199254740993` exactly and re-emit it, which no
        # exporter can produce. Read as the double it is, the two keys hold the
        # same number and the artifact is correctly reported non-canonical.
        {"a": 9007199254740993, "b": 9007199254740992},
        '{"a":9007199254740992,"b":9007199254740992}',
    ),
    (
        "negatives take the sign and then the same rules",
        {"a": -1e-7, "b": -0.5, "c": -(10**21)},
        '{"a":-1e-7,"b":-0.5,"c":-1e+21}',
    ),
    (
        "where the decimal point falls, on both sides of it",
        {"a": 123.456, "b": 100.0, "c": 0.0001, "d": 0.00001},
        '{"a":123.456,"b":100,"c":0.0001,"d":0.00001}',
    ),
    (
        "the rule recurses through nested objects and arrays",
        {"a": [{"b": 1e-7}], "c": {"d": 1e21}},
        '{"a":[{"b":1e-7}],"c":{"d":1e+21}}',
    ),
]

#: One document both implementations must refuse, for the same reason as
#: `NFC_COLLISION`: it has no canonical form at all. `1e999` and a 401-digit
#: integer are both read as an infinity by `json.loads` and by `JSON.parse`,
#: JSON cannot express one, and every available encoding — `null`, the largest
#: double, the digits back again — is a different value. The exporter refuses to
#: emit it and the Manager refuses to accept it, under one code.
NON_FINITE = {"a": 10**401}

#: Refused by the exporter, *encoded* by the verifier — the one deliberate
#: asymmetry in this contract, and the reason it is written down here rather
#: than left to be discovered. `canonical.js` refuses to **produce** a `-0`
#: because the object it came from would no longer match the document it
#: emitted. The Manager only ever reads documents that already went through
#: JSON, where the sign is gone; `-0` has the canonical form `0`, so the
#: artifact is reported non-canonical like any other differently-encoded one.
NEGATIVE_ZERO = {"a": -0.0}


@pytest.fixture(scope="module")
def number_encodings() -> list[str]:
    """`canonicalBytes` of each number boundary document, from the shipped module."""
    documents = [document for _, document, _ in NUMBER_BOUNDARY]
    result = subprocess.run(
        [node(), str(CANONICAL_EMITTER)],
        cwd=MODULE,
        input=json.dumps(documents).encode("utf-8"),
        capture_output=True,
        check=True,
    )
    lines = result.stdout.decode("utf-8").split("\n")
    assert lines[-1] == "", "the exporter must end every document with one LF"
    return lines[:-1]


@pytest.mark.parametrize(
    ("name", "document", "expected"),
    NUMBER_BOUNDARY,
    ids=[name for name, _, _ in NUMBER_BOUNDARY],
)
def test_the_exporter_formats_numbers_as_the_contract_says(
    name, document, expected, number_encodings
):
    index = [entry[0] for entry in NUMBER_BOUNDARY].index(name)

    assert number_encodings[index] == expected


@pytest.mark.parametrize(
    ("name", "document", "expected"),
    NUMBER_BOUNDARY,
    ids=[name for name, _, _ in NUMBER_BOUNDARY],
)
def test_the_verifier_formats_numbers_as_the_contract_says(name, document, expected):
    assert canonical_bytes(document).decode("utf-8") == f"{expected}\n"


def test_exporter_and_verifier_agree_byte_for_byte_over_the_number_boundary(
    number_encodings,
):
    """The check neither single-language test can make — C-12's shape, C-17's bug.

    Before C-17 every entry below failed but the first zero and the plain
    integers: the exporter emitted `100000000000000000000` and `1e-7` where the
    verifier emitted `1e+20` and `1e-07`, so a conforming export carrying any
    number outside Python's own notation range was reported non-canonical.
    """
    for (name, document, _), emitted in zip(
        NUMBER_BOUNDARY, number_encodings, strict=True
    ):
        assert canonical_bytes(document).decode("utf-8") == f"{emitted}\n", name


#: Doubles chosen for breadth rather than for a written-out expectation: the
#: subnormals, the powers of ten either side of both notation thresholds, values
#: whose shortest representation needs all 17 digits, and a spread of ordinary
#: magnitudes. The table above pins the *rule*; this pins that the two languages
#: compute the same shortest round-tripping digits, which is the half of
#: `Number::toString` neither implementation writes itself.
PRECISION_SPREAD = [
    5e-324, 1e-323, 2.2250738585072014e-308, 2.225073858507201e-308,
    1e-100, 1e-21, 1e-7, 1e-6, 1e-5, 1e-4, 0.001, 0.1, 1 / 3, 0.5,
    0.1 + 0.2, 1.0, 1.5, 3.141592653589793, 2.718281828459045,
    99.99999999999999, 123.456, 1e15, 1e16, 1e17, 9007199254740991.0,
    9007199254740992.0, 4294967294.0, 4294967295.0, 1e20, 1e21, 1e22,
    6.02214076e23, 1.7976931348623157e308, 1.2345678901234567e300,
    -0.5, -1e-7, -1e21, -123.456, 1e-6 - 1e-22, 5.960464477539063e-8,
]


def test_the_two_implementations_agree_on_every_double_in_the_spread():
    """Precision, not thresholds: the same digits out of two shortest-repr engines.

    CPython and every JavaScript engine emit the shortest decimal that reads
    back as the same double, and pick the nearest when several are equally
    short. That agreement is assumed by `_shortest_decimal`, which reads its
    digits out of `repr`, so it is asserted rather than assumed here.
    """
    document = {f"{index:03d}": value for index, value in enumerate(PRECISION_SPREAD)}

    result = subprocess.run(
        [node(), str(CANONICAL_EMITTER)],
        cwd=MODULE,
        input=json.dumps([document]).encode("utf-8"),
        capture_output=True,
        check=True,
    )

    assert canonical_bytes(document) == result.stdout


def test_both_implementations_refuse_a_non_finite_number_with_the_same_code():
    """A refusal is part of the contract, so the two must agree on it too.

    The `nfc_key_collision` case, for numbers: a document with no canonical form
    is the one thing canonicalisation *enforces* rather than reports. Neither
    implementation may invent an encoding — `null`, a clamp to the largest
    double and the digits back again are three different values, and the one
    thing none of them is, is the number the artifact contained.
    """
    refused = subprocess.run(
        [node(), str(CANONICAL_EMITTER)],
        cwd=MODULE,
        input=json.dumps([NON_FINITE]).encode("utf-8"),
        capture_output=True,
        check=False,
    )

    assert refused.returncode == 1, "the exporter emitted bytes for an infinity"
    assert refused.stdout == b""
    assert json.loads(refused.stderr.decode("utf-8"))["code"] == "non_finite_number"

    with pytest.raises(SnapshotRejected) as rejection:
        canonical_bytes(NON_FINITE)

    assert rejection.value.code == "non_finite_number"


def test_negative_zero_is_refused_by_the_exporter_and_encoded_by_the_verifier():
    """The one place the two deliberately differ, asserted so it stays deliberate.

    Producing a `-0` and reading one are different acts. `canonical.js` reads
    live Foundry objects, where `-0` is a distinct value that its own output
    would not read back as, so it refuses. The Manager reads a document that has
    already been through JSON, where the sign did not survive: `-0` has the
    canonical form `0`, the artifact's bytes differ from it, and that is the
    ordinary non-canonical warning rather than a refusal.
    """
    refused = subprocess.run(
        [node(), str(CANONICAL_EMITTER)],
        cwd=MODULE,
        input=json.dumps([NEGATIVE_ZERO]).encode("utf-8"),
        capture_output=True,
        check=False,
    )

    assert refused.returncode == 1
    assert json.loads(refused.stderr.decode("utf-8"))["code"] == "negative_zero"

    assert canonical_bytes(NEGATIVE_ZERO) == b'{"a":0}\n'


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
