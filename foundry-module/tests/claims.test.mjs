import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

/**
 * What the module is allowed to tell the submitting GM about the server.
 *
 * Implementation review I-1. The server writes the artifact before it commits
 * the database transaction, so a submission that fails — a timeout, a dropped
 * connection, a 503, an unexpected 500 — may well have left correct bytes on the
 * server's disk. The module is the *least* able of anything in this system to
 * know: it saw a network failure and nothing else.
 *
 * So a reassurance such as "nothing was stored" would be a claim the client
 * cannot make, shown to the one person who acts on it. What it may say is what
 * a retry guarantees: the submission was not recorded or confirmed, and
 * resubmitting the same export cannot create a second snapshot, because the
 * server addresses artifacts by content.
 *
 * These read the source rather than driving the dialog, because the dialog
 * needs a live Foundry client. The Python suite's
 * `tests/test_storage_claim_vocabulary.py` applies the same rule to every file
 * in this module and to the server's own messages.
 */

const read = (name) =>
  readFileSync(fileURLToPath(new URL(`../scripts/${name}`, import.meta.url)), "utf8");

/** Executable code only: an explanation of the old defect is not a claim. */
const withoutComments = (source) =>
  source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/[^\n]*/g, "");

const PROHIBITED = /nothing\s+(?:was|is|has been)\s+(?:stored|saved|persisted)/i;

test("no module message tells the GM that nothing was stored", () => {
  for (const name of ["main.js", "transport.js", "workflow.js", "settings.js"]) {
    assert.equal(
      PROHIBITED.test(withoutComments(read(name))),
      false,
      `${name} claims nothing was stored, which a browser client cannot know`
    );
  }
});

test("a failed submission tells the GM what a retry actually guarantees", () => {
  const main = read("main.js");
  assert.match(main, /Nothing was recorded or confirmed/);
  assert.match(main, /a retry cannot create a second snapshot/);
});

test("a transport failure says the same thing, in the same vocabulary", () => {
  const transport = withoutComments(read("transport.js"));
  // Both branches: a timeout and an unreachable server are indistinguishable
  // from a server that stored the bytes and could not record them.
  assert.match(transport, /The submission timed out\. Nothing was confirmed\./);
  assert.match(
    transport,
    /could not reach the Freedom Blades server\. Nothing\s*"?\s*\+?\s*"?was confirmed\./
  );
});
