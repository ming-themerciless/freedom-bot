import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import {
  SourceError,
  describeSelectableFolders,
  mayExport,
  readActors,
  readFolders,
  readWorld,
} from "../scripts/world-source.js";
import {
  ACTIVE_FOLDER_ID,
  FIRST_ACTOR_ID,
  INACTIVE_FOLDER_ID,
  NESTED_ACTOR_ID,
  NESTED_FOLDER_ID,
  SECOND_ACTOR_ID,
  SUPPORTED,
  THIRD_ACTOR_ID,
  fakeGame,
} from "./fixtures.mjs";

test("the running deployment tuple is read, never assumed", () => {
  const game = fakeGame({ coreVersion: "14.999", systemVersion: "9.9.9" });
  assert.deepEqual(readWorld(game), {
    id: SUPPORTED.worldId,
    title: "The Guild",
    coreVersion: "14.999",
    systemId: "dnd5e",
    systemVersion: "9.9.9",
  });
});

test("only Actor folders are considered", () => {
  const game = fakeGame();
  game.folders.push({ id: "jrnlQwErTyUiOpAs", name: "Notes", type: "JournalEntry", folder: null });
  assert.equal(readFolders(game).has("jrnlQwErTyUiOpAs"), false);
});

test("selectable folders carry stable id, full path and direct Actor count", () => {
  const described = describeSelectableFolders(fakeGame());
  const active = described.find((entry) => entry.id === ACTIVE_FOLDER_ID);
  assert.equal(active.path, "/actors/Characters/Characters (active)");
  assert.equal(active.actors, 2);
  assert.equal(active.subfolders, 1);
});

test("two folders may share a name; identity is id plus path", () => {
  const described = describeSelectableFolders(fakeGame());
  const sameName = described.filter((entry) => entry.name === "Characters (active)");
  assert.equal(sameName.length, 2);
  assert.notEqual(sameName[0].id, sameName[1].id);
  assert.notEqual(sameName[0].path, sameName[1].path);
});

test("only a GM may export", () => {
  assert.equal(mayExport(fakeGame({ isGM: true })), true);
  assert.equal(mayExport(fakeGame({ isGM: false })), false);
  assert.equal(mayExport({}), false);
});

test("scope is direct membership: sub-folder Actors are excluded", () => {
  const actors = readActors(fakeGame(), ACTIVE_FOLDER_ID);
  const ids = actors.map((actor) => actor.id).sort();
  assert.deepEqual(ids, [FIRST_ACTOR_ID, SECOND_ACTOR_ID].sort());
  assert.equal(ids.includes(NESTED_ACTOR_ID), false);
  assert.equal(ids.includes(THIRD_ACTOR_ID), false);
});

test("a different folder yields a different set", () => {
  const actors = readActors(fakeGame(), INACTIVE_FOLDER_ID);
  assert.deepEqual(actors.map((actor) => actor.id), [THIRD_ACTOR_ID]);
});

test("the real world Actor id is preserved", () => {
  const [first] = readActors(fakeGame(), ACTIVE_FOLDER_ID);
  assert.equal(first.id, FIRST_ACTOR_ID);
});

test("a null _id falls back to the document's own id, never to a name", () => {
  // Exactly the shape of a hand-saved per-Actor Foundry export (F-F1).
  const game = fakeGame({
    actorOverrides: {
      [FIRST_ACTOR_ID]: {
        sourceOverride: { _id: null, name: "Testcharacter", system: {}, items: [] },
      },
    },
  });
  // `actor.id` is still present on the document, so the fallback resolves it —
  // which is the behaviour that matters: identity comes from the document, not
  // from a filename and never from a name.
  const [first] = readActors(game, ACTIVE_FOLDER_ID);
  assert.equal(first.id, FIRST_ACTOR_ID);
});

test("an Actor with no id at all is refused", () => {
  const game = fakeGame();
  game.actors[0].id = "";
  game.actors[0]._sourceOverride = { _id: null, name: "X", system: {}, items: [] };
  assert.throws(
    () => readActors(game, ACTIVE_FOLDER_ID),
    (error) => error instanceof SourceError && error.code === "missing_actor_id"
  );
});

test("insufficient permission on any selected Actor refuses the whole export", () => {
  const game = fakeGame({ actorOverrides: { [SECOND_ACTOR_ID]: { owned: false } } });
  assert.throws(
    () => readActors(game, ACTIVE_FOLDER_ID),
    (error) => error instanceof SourceError && error.code === "insufficient_permission"
  );
});

test("ownership, flags, _stats and other document metadata never reach the bundle", () => {
  const actors = readActors(fakeGame(), ACTIVE_FOLDER_ID);
  for (const actor of actors) {
    assert.deepEqual(Object.keys(actor).sort(), ["folderId", "id", "img", "items", "name", "system"]);
    assert.equal("ownership" in actor, false);
    assert.equal("_stats" in actor, false);
    assert.equal("flags" in actor, false);
    assert.equal("prototypeToken" in actor, false);
    assert.equal("sort" in actor, false);
    assert.equal(JSON.stringify(actors).includes("xY7SyntheticUser"), false);
  }
});

test("readActors projects optional undefined object properties at the source boundary", () => {
  const game = fakeGame();
  // Modify an actor's toObject() output to include optional undefined properties inside items
  const originalActor = game.actors[0];
  const origToObject = originalActor.toObject.bind(originalActor);
  originalActor.toObject = () => {
    const raw = origToObject();
    raw.items.push({
      _id: "itmAdvancement01",
      name: "Advancement Feat",
      type: "feat",
      system: {
        advancement: {
          step1: {
            title: "Option",
            classRestriction: undefined,
          },
        },
      },
    });
    return raw;
  };

  const actors = readActors(game, ACTIVE_FOLDER_ID);
  const projectedActor = actors[0];
  const advancementItem = projectedActor.items.find((i) => i._id === "itmAdvancement01");

  assert.equal(advancementItem !== undefined, true);
  assert.equal("classRestriction" in advancementItem.system.advancement.step1, false);
  assert.equal(advancementItem.system.advancement.step1.title, "Option");
});

test("no Foundry mutation API is invoked, and no forbidden source is read", () => {
  // A `game` whose every mutating entry point throws. If the exporter called
  // one, this test would fail rather than silently succeed against a double
  // that tolerated it.
  const game = fakeGame();
  const forbid = (name) => () => {
    throw new Error(`${name} must never be called`);
  };
  for (const collection of [game.actors, game.folders]) {
    collection.create = forbid("create");
    collection.updateAll = forbid("updateAll");
  }
  for (const actor of game.actors) {
    actor.update = forbid("update");
    actor.delete = forbid("delete");
    actor.createEmbeddedDocuments = forbid("createEmbeddedDocuments");
    actor.updateEmbeddedDocuments = forbid("updateEmbeddedDocuments");
    actor.deleteEmbeddedDocuments = forbid("deleteEmbeddedDocuments");
    actor.exportToCompendium = forbid("exportToCompendium");
    actor.importFromJSON = forbid("importFromJSON");
  }
  game.packs = new Proxy(
    {},
    {
      get: forbid("game.packs"),
    }
  );
  game.settings = { set: forbid("settings.set") };

  assert.doesNotThrow(() => readActors(game, ACTIVE_FOLDER_ID));
  assert.doesNotThrow(() => describeSelectableFolders(game));
});

test("no module source reads the filesystem, LevelDB or a compendium", () => {
  // A source-text check rather than a behavioural one, because "did not happen
  // in this test" is weaker than "cannot be written in this module".
  const forbidden = [
    /\bnode:fs\b/,
    /require\(\s*["']fs["']\s*\)/,
    /levelup|classic-level|leveldb/i,
    /game\.packs/,
    /CompendiumCollection/,
    /worlds\//,
  ];
  for (const name of [
    "canonical.js",
    "bundle.js",
    "world-source.js",
    "transport.js",
    "workflow.js",
    "main.js",
    "settings.js",
  ]) {
    const path = fileURLToPath(new URL(`../scripts/${name}`, import.meta.url));
    const source = readFileSync(path, "utf8");
    // Strip block comments so documentation that *names* a forbidden source in
    // order to forbid it does not fail the check on itself.
    const code = source.replace(/\/\*[\s\S]*?\*\//g, "").replace(/^\s*\/\/.*$/gm, "");
    for (const pattern of forbidden) {
      assert.equal(
        pattern.test(code),
        false,
        `${name} must not reference ${pattern}`
      );
    }
  }
});
