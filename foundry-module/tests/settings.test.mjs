/**
 * The confidentiality boundary for the submission credential.
 *
 * Security review S-B-1: a `scope: "world"` setting's value is delivered to
 * *every* connecting client. `settings.js` records the Foundry 14.365 source
 * that establishes it — `dist/packages/world.mjs` builds each user's world
 * payload with an unfiltered `db.Setting.dump()`, and the client's
 * `game.settings.storage.get("world")` **is** that delivered collection.
 *
 * So the property under test is not "an ordinary user cannot write the setting"
 * and not "an ordinary user cannot see the button". Both were true before and
 * neither prevented anything. It is: **no reusable credential is in any Foundry
 * state at all.** The fake `game` below models the delivery honestly — whatever
 * is registered or written is readable by every client — so a test that reads
 * it as an ordinary player is reading exactly what a real one would receive.
 */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import {
  DEFAULT_SUPPORTED,
  MODULE_ID,
  SETTINGS,
  readSettings,
  registerSettings,
} from "../scripts/settings.js";

/** Anything whose *name* suggests it could hold a secret. */
const SECRET_SHAPED = /credential|secret|token|password|bearer|apikey|api[-_]?key|auth/i;

/** A synthetic credential. Never a real one — it is invented for this file. */
const SYNTHETIC_CREDENTIAL = "foundry-the-guild.0123456789012345678901234567890123456789";

/**
 * A `game.settings` that models Foundry's real delivery: one world-scoped store,
 * whose entire contents reach every client regardless of role.
 */
function fakeGame() {
  const registered = new Map();
  const values = new Map();
  return {
    settings: {
      register(namespace, key, config) {
        registered.set(`${namespace}.${key}`, config);
        values.set(`${namespace}.${key}`, config.default);
      },
      set(namespace, key, value) {
        values.set(`${namespace}.${key}`, value);
      },
      get(namespace, key) {
        return values.get(`${namespace}.${key}`);
      },
    },
    /** Every Setting document a joining client is vended. */
    vendedToEveryClient() {
      return Object.fromEntries(values);
    },
    registeredSettings() {
      return registered;
    },
  };
}

test("no setting whose name could hold a secret is registered", () => {
  const game = fakeGame();
  registerSettings(game);

  for (const key of game.registeredSettings().keys()) {
    assert.equal(
      SECRET_SHAPED.test(key),
      false,
      `${key} is registered as a Foundry setting. A world setting's value is ` +
        "delivered to every client, so it is not a place a credential may live."
    );
  }
  for (const key of Object.values(SETTINGS)) {
    assert.equal(SECRET_SHAPED.test(key), false, `SETTINGS.${key} is secret-shaped`);
  }
});

test("the exact set of settings is the four non-secret ones", () => {
  const game = fakeGame();
  registerSettings(game);

  assert.deepEqual(
    [...game.registeredSettings().keys()].sort(),
    [
      `${MODULE_ID}.submissionEndpoint`,
      `${MODULE_ID}.supportedCoreVersion`,
      `${MODULE_ID}.supportedSystemVersion`,
      `${MODULE_ID}.supportedWorldId`,
    ]
  );
});

test("what every client is vended contains no credential", () => {
  const game = fakeGame();
  registerSettings(game);

  // What an ordinary player's browser holds after joining.
  const delivered = JSON.stringify(game.vendedToEveryClient());

  assert.equal(delivered.includes(SYNTHETIC_CREDENTIAL), false);
  assert.equal(
    /credential|secret|token|password/i.test(delivered),
    false,
    `an ordinary client is vended: ${delivered}`
  );
});

test("readSettings returns no credential for any caller to pick up", () => {
  const game = fakeGame();
  registerSettings(game);
  game.settings.set(MODULE_ID, SETTINGS.endpoint, "https://freedom.example/api");

  const settings = readSettings(game);

  assert.deepEqual(Object.keys(settings).sort(), ["endpoint", "supported"]);
  assert.equal("credential" in settings, false);
  assert.equal(JSON.stringify(settings).includes(SYNTHETIC_CREDENTIAL), false);
  assert.equal(settings.supported.worldId, DEFAULT_SUPPORTED.worldId);
});

test("registering settings writes nothing secret-shaped through the settings API", () => {
  const game = fakeGame();
  const writes = [];
  const set = game.settings.set.bind(game.settings);
  game.settings.set = (namespace, key, value) => {
    writes.push([key, value]);
    return set(namespace, key, value);
  };

  registerSettings(game);

  assert.deepEqual(writes, []);
});

test("no module source persists a credential through any Foundry storage API", () => {
  // The regression guard proper. A future change that puts the secret back into
  // world state has to go through one of these APIs, and this fails when it does.
  const sources = ["settings.js", "main.js", "transport.js", "workflow.js"].map(
    (name) => [
      name,
      readFileSync(
        fileURLToPath(new URL(`../scripts/${name}`, import.meta.url)),
        "utf8"
      ),
    ]
  );

  const forbidden = [
    /settings\.register\([^)]*(credential|secret|token|password)/i,
    /settings\.set\([^)]*(credential|secret|token|password)/i,
    /localStorage/i,
    /sessionStorage/i,
    /setFlag\(/i,
  ];

  for (const [name, source] of sources) {
    // Comments explain *why* the credential is not stored, and naming the APIs
    // is the point of them; only executable code is scanned.
    const code = source
      .replace(/\/\*[\s\S]*?\*\//g, "")
      .replace(/^\s*\/\/.*$/gm, "");
    for (const pattern of forbidden) {
      assert.equal(
        pattern.test(code),
        false,
        `${name} matches ${pattern}: the submission credential must not be ` +
          "persisted in any state a Foundry client can read."
      );
    }
  }
});
