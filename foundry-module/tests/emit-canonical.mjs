/**
 * Encode arbitrary documents through the exporter's real canonical encoder.
 *
 * Companion to `emit-golden.mjs`. That script emits one whole *bundle*, which
 * is the right shape for proving the two implementations agree about a
 * submission; this one takes documents chosen by the caller, which is the only
 * way to reach contract corners a bundle never contains — object keys at the
 * ECMAScript array-index boundary, above all.
 *
 * That boundary is why this exists. Finding I-1 (change-log C-12) was a
 * cross-language disagreement about which numeric-looking keys JavaScript
 * hoists, and the committed fixture could not see it because its integer-like
 * keys are all small class levels. A test that can choose its own keys can.
 *
 * Usage:
 *
 *     echo '[{"a":1},{"b":2}]' | node tests/emit-canonical.mjs
 *
 * stdin is one JSON array of documents. stdout is `canonicalBytes` of each, in
 * order. Every canonical document is exactly one line — `serialise` emits no
 * whitespace and `JSON.stringify` escapes every newline inside a string — so
 * the trailing LF each one already carries separates them unambiguously.
 *
 * A **refusal** exits `1` and writes `{"code":…,"index":…}` to stderr, so a
 * caller can assert which refusal the exporter raised rather than pattern-match
 * a stack trace. Only the code and the document's position are reported; the
 * message may name a path, and stderr is not the place to carry one.
 *
 * Nothing here reads Foundry, the network, the clock or the filesystem beyond
 * stdin, and every document is supplied by the caller.
 */
import { CanonicalError, canonicalBytes } from "../scripts/canonical.js";

const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);

const documents = JSON.parse(Buffer.concat(chunks).toString("utf-8"));
if (!Array.isArray(documents)) {
  throw new TypeError("stdin must be a JSON array of documents.");
}

documents.forEach((document, index) => {
  try {
    process.stdout.write(canonicalBytes(document));
  } catch (error) {
    if (error instanceof CanonicalError) {
      process.stderr.write(`${JSON.stringify({ code: error.code, index })}\n`);
      process.exit(1);
    }
    throw error;
  }
});
