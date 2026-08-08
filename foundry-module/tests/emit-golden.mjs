/**
 * Emit one synthetic bundle through the exporter's real serialization path.
 *
 * Written for `tests/test_exporter_contract.py`, which runs this script and
 * feeds the bytes to the **real** Python artifact and parser path. That is the
 * anti-drift control: the exporter and the Manager are two implementations of
 * one contract in two languages, and the only way to know they agree is to make
 * one produce what the other consumes.
 *
 * It uses `prepareSnapshot` — the same function the Foundry button calls —
 * against the same synthetic fake world the `node --test` suite uses, so this is
 * not a second hand-written encoder that could quietly diverge from the one that
 * ships.
 *
 * Usage:
 *
 *     node tests/emit-golden.mjs <worldId> <coreVersion> <systemId> <systemVersion> [folderId]
 *
 * The deployment tuple is passed in rather than hard-coded so the Python test
 * can supply `domain.foundry.OBSERVED_DEPLOYMENT` and the two sides cannot
 * disagree about what "supported" means either.
 *
 * The bytes go to stdout, exactly as produced. Nothing is written to disk, and
 * every value in the document is synthetic.
 */

import { prepareSnapshot } from "../scripts/workflow.js";
import { ACTIVE_FOLDER_ID, fakeGame } from "./fixtures.mjs";

const [worldId, coreVersion, systemId, systemVersion, folderId = ACTIVE_FOLDER_ID] =
  process.argv.slice(2);

if (!worldId || !coreVersion || !systemId || !systemVersion) {
  process.stderr.write(
    "usage: emit-golden.mjs <worldId> <coreVersion> <systemId> <systemVersion> [folderId]\n"
  );
  process.exit(2);
}

const prepared = await prepareSnapshot({
  game: fakeGame({ worldId, coreVersion, systemId, systemVersion }),
  crypto: globalThis.crypto,
  folderId,
  exporterVersion: "1.0.2",
  supported: { worldId, coreVersion, systemId, systemVersion },
  now: () => new Date("2026-08-04T09:15:00Z"),
});

process.stdout.write(Buffer.from(prepared.bytes));
