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

test("object keys are sorted by code point at every depth", () => {
  const bytes = canonicalBytes({ b: { d: 1, c: 2 }, a: 3 });
  assert.equal(decode(bytes), '{"a":3,"b":{"c":2,"d":1}}\n');
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

test("null, booleans and nested empties round-trip exactly", () => {
  assert.equal(
    decode(canonicalBytes({ a: null, b: true, c: false, d: {}, e: [] })),
    '{"a":null,"b":true,"c":false,"d":{},"e":[]}\n'
  );
});
