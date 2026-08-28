/**
 * Version compatibility, widened from exact equality 2026-08-27 (C-P3.5-Z).
 *
 * **This table is duplicated in `tests/test_foundry_identity.py` and the two
 * must agree.** The module refuses before assembling a bundle and the server
 * refuses on submission. Two different rules would mean an export the module
 * allowed and the server rejected — or, worse, one the module allowed and the
 * server accepted when it should not have.
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { assertSupportedDeployment } from "../scripts/bundle.js";

const SUPPORTED = Object.freeze({
  worldId: "the-guild",
  coreVersion: "14.367",
  systemId: "dnd5e",
  systemVersion: "5.3.3",
});

const world = (coreVersion, systemVersion) => ({
  id: SUPPORTED.worldId,
  title: "The Guild",
  coreVersion,
  systemId: SUPPORTED.systemId,
  systemVersion,
});

const TABLE = [
  ["14.367", "5.3.3", true, "the reference deployment itself"],
  ["14.365", "5.3.3", true, "an older build in the same generation"],
  ["14.999", "5.3.3", true, "a newer build in the same generation"],
  ["14", "5.3.3", true, "a generation with no build number"],
  ["14.367.2", "5.3.3", true, "a build with a third component"],
  ["15.1", "5.3.3", false, "the next Foundry generation"],
  ["13.999", "5.3.3", false, "the previous Foundry generation"],
  ["14.x", "5.3.3", false, "a core version that is not numeric"],
  ["14.367", "5.3", true, "a system version with no patch"],
  ["14.367", "5.3.9", true, "a later system patch"],
  ["14.367", "5.4.0", false, "the next system minor — where a schema may move"],
  ["14.367", "6.0.0", false, "the next system major"],
  ["14.367", "5", false, "a system version with no minor at all"],
  ["14.367", "5.3.3-beta", false, "a system prerelease"],
];

for (const [core, system, accepted, label] of TABLE) {
  test(`deployment ${core}/${system} is ${accepted ? "accepted" : "refused"} — ${label}`, () => {
    if (accepted) {
      assert.doesNotThrow(() => assertSupportedDeployment(world(core, system), SUPPORTED));
    } else {
      assert.throws(
        () => assertSupportedDeployment(world(core, system), SUPPORTED),
        (error) => error.code === "unsupported_deployment"
      );
    }
  });
}

test("a refusal names the accepted series rather than the reference version", () => {
  assert.throws(
    () => assertSupportedDeployment(world("15.1", "5.4.0"), SUPPORTED),
    (error) => {
      assert.match(error.message, /14\.x series/);
      assert.match(error.message, /5\.3\.x series/);
      return true;
    }
  );
});

test("identities are still matched exactly", () => {
  assert.throws(
    () =>
      assertSupportedDeployment(
        { ...world("14.367", "5.3.3"), id: "other-world", systemId: "pf2e" },
        SUPPORTED
      ),
    (error) => {
      assert.match(error.message, /world other-world/);
      assert.match(error.message, /system pf2e/);
      return true;
    }
  );
});
