/**
 * Canonical JSON encoding, exactly as `docs/rules/foundry-export-contract.md` §1
 * defines it. Pure: nothing here touches Foundry, the DOM, the network or time.
 *
 * Canonicalisation is the exporter's obligation, not the Manager's. The Manager
 * identifies an artifact by the SHA-256 of the bytes it was given and never
 * re-serialises one, so if two exports of an unchanged world differ in byte
 * order they are simply two different snapshots. Getting this right here is what
 * makes "nothing changed" observable at all.
 *
 * The rules, and the failure each one prevents:
 *
 * | Rule | Without it |
 * |---|---|
 * | keys sorted by code point at every depth | key order follows insertion order, which follows whatever Foundry did last |
 * | `,` and `:` separators, no whitespace | pretty-printing changes every byte |
 * | NFC normalisation of every string | the same name typed two ways is two snapshots |
 * | one trailing LF, no BOM | the Manager refuses a BOM and pins the trailer |
 * | `folders` and `actors` sorted by id | collection iteration order is not a contract |
 *
 * `JSON.stringify` is deliberately **not** used for the document. Its
 * `replacer`/`space` options cannot express "sort at every depth", and — worse —
 * it silently drops `undefined`, functions and symbols from objects and turns
 * them into `null` inside arrays. A value quietly disappearing from an Actor
 * export is precisely the class of bug this contract exists to make impossible,
 * so every unsupported value is a refusal instead. `JSON.stringify` is still
 * used for individual strings and finite numbers, where it is exactly right.
 */

export class CanonicalError extends Error {
  /**
   * @param {string} code    A stable classification an operator can act on.
   * @param {string} message A sentence that names the path, never the value.
   */
  constructor(code, message) {
    super(message);
    this.name = "CanonicalError";
    this.code = code;
  }
}

/**
 * Compare two strings by Unicode code point, which is what the contract says.
 *
 * `String.prototype.localeCompare` is locale-dependent, and `<` compares UTF-16
 * code *units* — so an astral character (surrogate pair, `\uD800`–`\uDFFF`)
 * sorts before `�` under `<` but after it by code point. Foundry keys are
 * currently ASCII, which is exactly why this would never have been noticed.
 *
 * @param {string} left
 * @param {string} right
 * @returns {number}
 */
export function compareCodePoints(left, right) {
  const a = Array.from(left);
  const b = Array.from(right);
  const shared = Math.min(a.length, b.length);
  for (let index = 0; index < shared; index += 1) {
    const first = a[index].codePointAt(0);
    const second = b[index].codePointAt(0);
    if (first !== second) return first < second ? -1 : 1;
  }
  if (a.length === b.length) return 0;
  return a.length < b.length ? -1 : 1;
}

/**
 * Recursively normalise a JSON-domain value, or refuse it.
 *
 * Refuses `undefined`, functions, symbols, `BigInt`, `NaN`, the infinities,
 * negative zero, cycles and every host object. None of them is expressible in
 * JSON, and each of the alternatives — dropping, coercing, stringifying — would
 * change an Actor's exported data without saying so.
 *
 * `-0` is refused rather than normalised to `0`: it round-trips through
 * `JSON.parse` as `0`, so an exporter that emitted it would produce a document
 * that no longer matches the object it came from.
 *
 * @param {unknown} value
 * @param {string} path  Where we are, for the refusal message. Never a value.
 * @param {Set<object>} seen  Ancestors, for cycle detection.
 * @returns {unknown}
 */
export function normalise(value, path = "$", seen = new Set()) {
  if (value === null) return null;

  const type = typeof value;

  if (type === "string") return value.normalize("NFC");

  if (type === "number") {
    if (!Number.isFinite(value)) {
      throw new CanonicalError(
        "non_finite_number",
        `${path} is not a finite number. NaN and the infinities are not JSON.`
      );
    }
    if (Object.is(value, -0)) {
      throw new CanonicalError(
        "negative_zero",
        `${path} is negative zero, which does not survive a JSON round trip.`
      );
    }
    return value;
  }

  if (type === "boolean") return value;

  if (type === "undefined") {
    throw new CanonicalError(
      "undefined_value",
      `${path} is undefined. JSON has no undefined, and silently dropping it ` +
        "would remove exported data without saying so."
    );
  }

  if (type === "function" || type === "symbol" || type === "bigint") {
    throw new CanonicalError(
      "unsupported_type",
      `${path} is a ${type}, which cannot be represented in the export bundle.`
    );
  }

  if (Array.isArray(value)) {
    if (seen.has(value)) {
      throw new CanonicalError("cycle", `${path} is part of a reference cycle.`);
    }
    const nested = new Set(seen).add(value);
    return value.map((entry, index) =>
      normalise(entry, `${path}[${index}]`, nested)
    );
  }

  if (type === "object") {
    // A Date, Map, Set, RegExp or class instance is refused rather than coerced.
    // `toObject()` returns plain data; anything else here means something other
    // than document source data reached the bundle.
    const prototype = Object.getPrototypeOf(value);
    if (prototype !== Object.prototype && prototype !== null) {
      throw new CanonicalError(
        "unsupported_object",
        `${path} is not a plain object. Only document source data belongs in ` +
          "the bundle."
      );
    }
    if (seen.has(value)) {
      throw new CanonicalError("cycle", `${path} is part of a reference cycle.`);
    }
    const nested = new Set(seen).add(value);
    const result = {};
    for (const key of Object.keys(value).sort(compareCodePoints)) {
      result[key.normalize("NFC")] = normalise(
        value[key],
        `${path}.${key}`,
        nested
      );
    }
    return result;
  }

  throw new CanonicalError(
    "unsupported_type",
    `${path} holds a value the export bundle cannot represent.`
  );
}

/**
 * Serialise an already-normalised value with the contract's separators.
 *
 * Written out rather than delegated to `JSON.stringify` so that key order is
 * this function's own guarantee. Object keys are already sorted by `normalise`;
 * re-sorting here would hide a `normalise` that stopped doing it.
 *
 * @param {unknown} value
 * @returns {string}
 */
export function serialise(value) {
  if (value === null) return "null";
  const type = typeof value;
  if (type === "boolean") return value ? "true" : "false";
  if (type === "number") return JSON.stringify(value);
  if (type === "string") return JSON.stringify(value);
  if (Array.isArray(value)) {
    return `[${value.map(serialise).join(",")}]`;
  }
  const parts = [];
  for (const key of Object.keys(value)) {
    parts.push(`${JSON.stringify(key)}:${serialise(value[key])}`);
  }
  return `{${parts.join(",")}}`;
}

/**
 * The maximum nesting the contract permits, matched to the Manager's own bound.
 * Checked here so an over-deep document is refused before it is transmitted
 * rather than after.
 */
export const MAX_DEPTH = 64;

/**
 * @param {unknown} value
 * @param {number} depth
 * @param {string} path
 */
export function assertDepth(value, depth = 0, path = "$") {
  if (value === null || typeof value !== "object") return;
  const next = depth + 1;
  if (next > MAX_DEPTH) {
    throw new CanonicalError(
      "excessive_nesting",
      `${path} nests deeper than ${MAX_DEPTH} levels.`
    );
  }
  if (Array.isArray(value)) {
    value.forEach((entry, index) => assertDepth(entry, next, `${path}[${index}]`));
    return;
  }
  for (const key of Object.keys(value)) {
    assertDepth(value[key], next, `${path}.${key}`);
  }
}

/**
 * The exact bytes of one canonical document: UTF-8, no BOM, one trailing LF.
 *
 * These are the bytes that get hashed, the bytes that get uploaded and the bytes
 * a fallback download writes. There is exactly one producer of them, so the
 * three cannot disagree.
 *
 * @param {unknown} document
 * @returns {Uint8Array}
 */
export function canonicalBytes(document) {
  const normalised = normalise(document);
  assertDepth(normalised);
  const text = `${serialise(normalised)}\n`;
  return new TextEncoder().encode(text);
}
