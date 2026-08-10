import test from "node:test";
import assert from "node:assert/strict";

import {
  CanonicalError,
  MAX_DEPTH,
  assertDepth,
  canonicalBytes,
  compareCodePoints,
  normalise,
  serialise,
} from "../scripts/canonical.js";

const decode = (bytes) => new TextDecoder().decode(bytes);

test("non-index object keys are ordered by code point at every depth", () => {
  const bytes = canonicalBytes({ b: { d: 1, c: 2 }, a: 3 });
  assert.equal(decode(bytes), '{"a":3,"b":{"c":2,"d":1}}\n');
});

// The array-index boundary — contract §1.0, change-log C-12.
//
// `normalise` sorts the key array by code point and rebuilds an object; the
// engine then hoists the *array indices* on insertion. So the emitted order is
// ECMAScript own-property order, and the boundary that decides which keys get
// hoisted is `2**32 - 2`, not the `2**53 - 1` the contract used to name.
//
// These cases are mirrored in `tests/test_exporter_contract.py`, which asserts
// the Python verifier produces the same bytes. Neither suite alone can see a
// disagreement between the two languages, which is what finding I-1 was.

test("array-index keys are hoisted and ordered numerically", () => {
  assert.equal(
    decode(canonicalBytes({ "10": "ten", "2": "two", "1": "one" })),
    '{"1":"one","2":"two","10":"ten"}\n'
  );
});

test("the array-index range ends at 2**32 - 2", () => {
  assert.equal(
    decode(
      canonicalBytes({
        "4294967295": "not-an-index",
        "4294967294": "largest-index",
        "7": "small",
      })
    ),
    '{"7":"small","4294967294":"largest-index","4294967295":"not-an-index"}\n'
  );
});

test("above the boundary, keys sort by code point rather than numerically", () => {
  // Numerically 5e9 < 1e10; by code point "1…" < "5…". Both are ordinary string
  // keys here, so code point wins — this is the exact pair finding I-1 used.
  assert.equal(
    decode(canonicalBytes({ "5000000000": "five", "10000000000": "ten" })),
    '{"10000000000":"ten","5000000000":"five"}\n'
  );
});

test("insertion order does not change the encoding at the boundary", () => {
  assert.equal(
    decode(canonicalBytes({ "10000000000": "ten", "5000000000": "five" })),
    decode(canonicalBytes({ "5000000000": "five", "10000000000": "ten" }))
  );
});

test("the old 2**53 - 1 bound's own values are ordinary string keys", () => {
  assert.equal(
    decode(
      canonicalBytes({
        "9007199254740992": "b",
        "9007199254740991": "a",
        "11": "small",
      })
    ),
    '{"11":"small","9007199254740991":"a","9007199254740992":"b"}\n'
  );
});

test("noncanonical decimals are ordinary string keys", () => {
  assert.equal(
    decode(
      canonicalBytes({
        "01": 1,
        "-1": 2,
        "1.0": 3,
        "1": 4,
        "0": 5,
        " 1": 6,
        "+1": 7,
        "1e2": 8,
      })
    ),
    '{"0":5,"1":4," 1":6,"+1":7,"-1":2,"01":1,"1.0":3,"1e2":8}\n'
  );
});

test("the boundary rule recurses through nested objects and arrays", () => {
  assert.equal(
    decode(
      canonicalBytes({
        b: { "10000000000": 1, "5000000000": 2, "7": 3, "4294967295": 4 },
        a: [{ "20000000000": 1, "3000000000": 2 }],
      })
    ),
    '{"a":[{"3000000000":2,"20000000000":1}],' +
      '"b":{"7":3,"10000000000":1,"4294967295":4,"5000000000":2}}\n'
  );
});

test("sorting is by code point, not by UTF-16 code unit", () => {
  // U+1D400 (astral, surrogate pair starting \uD835) is greater than U+FFFD by
  // code point but *less* by naive `<` comparison of UTF-16 units.
  const astral = "\u{1D400}";
  const replacement = "�";

  // The trap, stated as an assertion: naive `<` compares UTF-16 code units, and
  // the astral character's first unit (\uD835) is *below* � — so `<` puts
  // them in the opposite order to the contract's code-point rule.
  assert.equal(astral < replacement, true);
  assert.equal(compareCodePoints(replacement, astral), -1);

  const text = decode(canonicalBytes({ [astral]: 1, [replacement]: 2 }));
  assert.ok(
    text.indexOf(JSON.stringify(replacement)) < text.indexOf(JSON.stringify(astral)),
    "U+FFFD must be emitted before U+1D400"
  );
});

test("separators are compact and there is exactly one trailing newline", () => {
  const text = decode(canonicalBytes({ a: [1, 2], b: "x" }));
  assert.equal(text, '{"a":[1,2],"b":"x"}\n');
  assert.equal(text.endsWith("\n"), true);
  assert.equal(text.endsWith("\n\n"), false);
  assert.equal(text.includes(", "), false);
  assert.equal(text.includes(": "), false);
});

test("output is UTF-8 without a byte-order mark", () => {
  const bytes = canonicalBytes({ "ä": "ö" });
  assert.notEqual(bytes[0], 0xef);
  assert.deepEqual(Array.from(bytes.slice(0, 1)), [0x7b]); // '{'
});

test("strings are normalised to NFC, in keys as well as values", () => {
  const decomposed = "Å"; // 'A' + combining ring above
  const composed = "Å"; // 'Å'
  const fromDecomposed = decode(canonicalBytes({ [decomposed]: decomposed }));
  const fromComposed = decode(canonicalBytes({ [composed]: composed }));
  assert.equal(fromDecomposed, fromComposed);
});

test("array order is preserved", () => {
  assert.equal(decode(canonicalBytes({ a: [3, 1, 2] })), '{"a":[3,1,2]}\n');
});

test("undefined is refused rather than dropped", () => {
  assert.throws(
    () => canonicalBytes({ a: undefined }),
    (error) => error instanceof CanonicalError && error.code === "undefined_value"
  );
});

test("functions, symbols and BigInt are refused", () => {
  for (const value of [() => 1, Symbol("x"), 1n]) {
    assert.throws(
      () => canonicalBytes({ a: value }),
      (error) => error instanceof CanonicalError && error.code === "unsupported_type"
    );
  }
});

test("NaN and the infinities are refused", () => {
  for (const value of [Number.NaN, Number.POSITIVE_INFINITY, Number.NEGATIVE_INFINITY]) {
    assert.throws(
      () => canonicalBytes({ a: value }),
      (error) => error instanceof CanonicalError && error.code === "non_finite_number"
    );
  }
});

test("negative zero is refused, because it does not survive a round trip", () => {
  assert.throws(
    () => canonicalBytes({ a: -0 }),
    (error) => error instanceof CanonicalError && error.code === "negative_zero"
  );
});

test("a reference cycle is refused rather than recursed into", () => {
  const cyclic = { a: 1 };
  cyclic.self = cyclic;
  assert.throws(
    () => canonicalBytes(cyclic),
    (error) => error instanceof CanonicalError && error.code === "cycle"
  );
});

test("a repeated sibling is not mistaken for a cycle", () => {
  const shared = { x: 1 };
  const text = decode(canonicalBytes({ a: shared, b: shared }));
  assert.equal(text, '{"a":{"x":1},"b":{"x":1}}\n');
});

test("a Date, Map or class instance is refused, not coerced", () => {
  for (const value of [new Date(0), new Map(), new Set(), /x/]) {
    assert.throws(
      () => canonicalBytes({ a: value }),
      (error) => error instanceof CanonicalError && error.code === "unsupported_object"
    );
  }
});

test("nesting past the depth bound is refused before transmission", () => {
  let deep = 1;
  for (let index = 0; index < MAX_DEPTH + 1; index += 1) deep = { deep };
  assert.throws(
    () => canonicalBytes(deep),
    (error) => error instanceof CanonicalError && error.code === "excessive_nesting"
  );
});

test("nesting exactly at the bound is accepted", () => {
  let deep = 1;
  for (let index = 0; index < MAX_DEPTH; index += 1) deep = { deep };
  assert.doesNotThrow(() => assertDepth(normalise(deep)));
});

test("serialise does not re-sort, so it cannot hide an unsorted normalise", () => {
  // Built directly, bypassing `normalise`, to prove `serialise` is faithful to
  // the key order it is given.
  assert.equal(serialise({ b: 1, a: 2 }), '{"b":1,"a":2}');
});

// Change-log C-17. The verifier encoded numbers with Python's `json.dumps`,
// which switches to exponent notation at different magnitudes than
// `Number::toString` and pads the exponent, so a conforming export carrying
// `1e20` or `1e-7` was reported non-canonical. Only the verifier was wrong —
// `serialise` delegates numbers to `JSON.stringify`, which is `Number::toString`
// exactly. This pins that delegation, so a hand-rolled formatter here would have
// to disagree with the contract in writing first.
test("numbers are Number::toString, at both notation thresholds", () => {
  const cases = [
    [1, "1"],
    [1.0, "1"],
    [-0.5, "-0.5"],
    [1e20, "100000000000000000000"],
    [1e21, "1e+21"],
    [1e-6, "0.000001"],
    [1e-7, "1e-7"],
    [5e-324, "5e-324"],
    [1.7976931348623157e308, "1.7976931348623157e+308"],
    [0.1 + 0.2, "0.30000000000000004"],
    [2 ** 53, "9007199254740992"],
  ];
  for (const [value, expected] of cases) {
    assert.equal(serialise(value), expected);
    assert.equal(decode(canonicalBytes({ n: value })), `{"n":${expected}}\n`);
  }
});

// Closed defect — docs/review/phase-2-canonical-nfc-key-collision.md, fixed in
// `1.0.6` (change-log C-16).
//
// `normalise` used to sort keys by their pre-NFC form and insert them under
// their post-NFC form, so two distinct keys sharing an NFC form wrote to the
// same property and one value was silently dropped — the one outcome this
// file's header says the contract exists to make impossible. It now refuses.
//
// The two keys are written as escapes rather than as literal characters: they
// are indistinguishable on screen, and a test whose point is that they differ
// should not depend on an editor preserving that.
const COMPOSED_E = "\u00e9"; // LATIN SMALL LETTER E WITH ACUTE
const DECOMPOSED_E = "e\u0301"; // e + COMBINING ACUTE ACCENT

test("an NFC key collision is refused rather than dropping a value", () => {
  assert.notEqual(COMPOSED_E, DECOMPOSED_E);
  assert.equal(DECOMPOSED_E.normalize("NFC"), COMPOSED_E);

  // Both insertion orders: which key survived was decided by the code-point
  // order of the pre-NFC forms, which is not a property of the data at all.
  for (const document of [
    { [COMPOSED_E]: "first", [DECOMPOSED_E]: "second" },
    { [DECOMPOSED_E]: "first", [COMPOSED_E]: "second" },
  ]) {
    assert.equal(Object.keys(document).length, 2);
    assert.throws(
      () => canonicalBytes(document),
      (error) =>
        error instanceof CanonicalError && error.code === "nfc_key_collision"
    );
  }
});

test("a nested collision names its path and never a value", () => {
  assert.throws(
    () =>
      canonicalBytes({
        flags: { world: { [COMPOSED_E]: "first", [DECOMPOSED_E]: "second" } },
      }),
    (error) => {
      assert.equal(error.code, "nfc_key_collision");
      assert.match(error.message, /\$\.flags\.world/);
      assert.equal(error.message.includes("first"), false);
      assert.equal(error.message.includes("second"), false);
      return true;
    }
  );
});

test("one non-NFC key is normalised rather than refused", () => {
  // Only a collision is ambiguous. A single decomposed key has exactly one NFC
  // form, so it is normalised like every other string in the document.
  assert.equal(
    decode(canonicalBytes({ [DECOMPOSED_E]: 1 })),
    `{"${COMPOSED_E}":1}\n`
  );
});

test("NFC normalisation happens before the keys are sorted", () => {
  // "e" + combining acute sorts before "z" by code point; U+00E9 sorts after.
  // Sorting the pre-NFC form would emit the collided key first, so this pins
  // the order the emitted document is actually in.
  assert.equal(
    decode(canonicalBytes({ [DECOMPOSED_E]: 1, z: 2 })),
    `{"z":2,"${COMPOSED_E}":1}\n`
  );
});

test("null, booleans and nested empties round-trip exactly", () => {
  assert.equal(
    decode(canonicalBytes({ a: null, b: true, c: false, d: {}, e: [] })),
    '{"a":null,"b":true,"c":false,"d":{},"e":[]}\n'
  );
});
