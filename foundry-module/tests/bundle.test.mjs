import test from "node:test";
import assert from "node:assert/strict";

import {
  ACTOR_KEYS,
  BundleError,
  LIMITS,
  assertSupportedDeployment,
  buildBundle,
  encodeBundle,
  folderPath,
  validateBundle,
  withAncestors,
} from "../scripts/bundle.js";
import {
  ACTIVE_FOLDER_ID,
  FIRST_ACTOR_ID,
  NESTED_FOLDER_ID,
  ROOT_FOLDER_ID,
  SECOND_ACTOR_ID,
  SUPPORTED,
} from "./fixtures.mjs";

const folders = () =>
  new Map([
    [ROOT_FOLDER_ID, { id: ROOT_FOLDER_ID, name: "Characters", parentId: null }],
    [
      ACTIVE_FOLDER_ID,
      { id: ACTIVE_FOLDER_ID, name: "Characters (active)", parentId: ROOT_FOLDER_ID },
    ],
    [
      NESTED_FOLDER_ID,
      { id: NESTED_FOLDER_ID, name: "Retired", parentId: ACTIVE_FOLDER_ID },
    ],
  ]);

const actor = (id, overrides = {}) => ({
  id,
  folderId: ACTIVE_FOLDER_ID,
  name: `Synthetic ${id}`,
  system: { abilities: { str: { value: 10 } } },
  items: [{ type: "class", name: "Oathsworn", system: {} }],
  ...overrides,
});

const build = (actors = [actor(FIRST_ACTOR_ID)], selected = ACTIVE_FOLDER_ID) =>
  buildBundle({
    exporterVersion: "1.0.2",
    exportedAt: "2026-08-04T09:15:00Z",
    world: {
      id: SUPPORTED.worldId,
      title: "The Guild",
      coreVersion: SUPPORTED.coreVersion,
      systemId: SUPPORTED.systemId,
      systemVersion: SUPPORTED.systemVersion,
    },
    selectedFolderId: selected,
    folders: folders(),
    actors,
  });

test("an unsupported deployment tuple is refused, naming each difference", () => {
  const world = {
    id: "another-world",
    title: "Other",
    coreVersion: "13.999",
    systemId: "dnd5e",
    systemVersion: "5.0.0",
  };
  assert.throws(
    () => assertSupportedDeployment(world, SUPPORTED),
    (error) => {
      assert.ok(error instanceof BundleError);
      assert.equal(error.code, "unsupported_deployment");
      assert.match(error.message, /another-world/);
      assert.match(error.message, /13\.999/);
      assert.match(error.message, /5\.0\.0/);
      return true;
    }
  );
});

test("the supported tuple is accepted", () => {
  assert.doesNotThrow(() =>
    assertSupportedDeployment(
      {
        id: SUPPORTED.worldId,
        title: "The Guild",
        coreVersion: SUPPORTED.coreVersion,
        systemId: SUPPORTED.systemId,
        systemVersion: SUPPORTED.systemVersion,
      },
      SUPPORTED
    )
  );
});

test("the selected folder carries every ancestor, so a full path can be built", () => {
  const chain = withAncestors(NESTED_FOLDER_ID, folders());
  assert.deepEqual(
    chain.map((entry) => entry.id),
    [NESTED_FOLDER_ID, ACTIVE_FOLDER_ID, ROOT_FOLDER_ID]
  );
  assert.equal(
    folderPath(NESTED_FOLDER_ID, folders()),
    "/actors/Characters/Characters (active)/Retired"
  );
});

test("a missing ancestor is refused rather than producing a partial path", () => {
  const orphaned = new Map([
    [ACTIVE_FOLDER_ID, { id: ACTIVE_FOLDER_ID, name: "Active", parentId: "miss5eya6XVBAuIb" }],
  ]);
  assert.throws(
    () => withAncestors(ACTIVE_FOLDER_ID, orphaned),
    (error) => error.code === "unknown_parent_folder"
  );
});

test("a parent cycle is refused", () => {
  const cyclic = new Map([
    [ROOT_FOLDER_ID, { id: ROOT_FOLDER_ID, name: "Root", parentId: ACTIVE_FOLDER_ID }],
    [ACTIVE_FOLDER_ID, { id: ACTIVE_FOLDER_ID, name: "Active", parentId: ROOT_FOLDER_ID }],
  ]);
  assert.throws(
    () => withAncestors(ACTIVE_FOLDER_ID, cyclic),
    (error) => error.code === "folder_cycle"
  );
});

test("the bundle has exactly the contract's top-level keys", () => {
  assert.deepEqual(Object.keys(build()).sort(), [
    "actors",
    "exportedAt",
    "exporter",
    "folders",
    "schema",
    "schemaVersion",
    "selectedFolderIds",
    "world",
  ]);
});

test("folders and actors are sorted ascending by id", () => {
  const bundle = build([actor(SECOND_ACTOR_ID), actor(FIRST_ACTOR_ID)]);
  const ids = bundle.actors.map((entry) => entry.id);
  assert.deepEqual(ids, [...ids].sort());
  const folderIds = bundle.folders.map((entry) => entry.id);
  assert.deepEqual(folderIds, [...folderIds].sort());
});

test("only the selected folder is in selectedFolderIds", () => {
  assert.deepEqual(build().selectedFolderIds, [ACTIVE_FOLDER_ID]);
});

test("a duplicate Actor id is a refusal, never a choice between two records", () => {
  assert.throws(
    () => validateBundle(build([actor(FIRST_ACTOR_ID), actor(FIRST_ACTOR_ID)])),
    (error) => error.code === "duplicate_actor_id"
  );
});

test("a missing or malformed Actor id is refused", () => {
  for (const identifier of [undefined, null, "", "short", "notsixteen-chars!!"]) {
    assert.throws(
      () => validateBundle(build([actor(identifier)])),
      (error) => error.code === "malformed_actor_id"
    );
  }
});

test("an Actor outside the selected folder is refused", () => {
  assert.throws(
    () => validateBundle(build([actor(FIRST_ACTOR_ID, { folderId: NESTED_FOLDER_ID })])),
    (error) => error.code === "actor_outside_selection"
  );
});

test("an Actor key the contract does not permit is refused", () => {
  assert.throws(
    () => validateBundle(build([actor(FIRST_ACTOR_ID, { ownership: { default: 3 } })])),
    (error) => {
      assert.equal(error.code, "unknown_actor_key");
      assert.match(error.message, /ownership/);
      return true;
    }
  );
});

test("the accepted Actor key set is exactly the contract's", () => {
  assert.deepEqual([...ACTOR_KEYS].sort(), [
    "folderId",
    "id",
    "img",
    "items",
    "name",
    "system",
  ]);
});

test("an item without a document type is refused", () => {
  assert.throws(
    () =>
      validateBundle(
        build([actor(FIRST_ACTOR_ID, { items: [{ name: "Untyped", system: {} }] })])
      ),
    (error) => error.code === "malformed_actor"
  );
});

test("an accepted embedded item shape passes", () => {
  assert.doesNotThrow(() =>
    validateBundle(
      build([
        actor(FIRST_ACTOR_ID, {
          items: [
            { type: "class", name: "Oathsworn", system: { levels: 9 } },
            { type: "equipment", name: "Band of Focus", system: { rarity: "rare" } },
          ],
        }),
      ])
    )
  );
});

test("each structural bound is enforced before transmission", () => {
  const many = Array.from({ length: LIMITS.maxActors + 1 }, (_, index) =>
    actor(`aaaaaaaaaaaaaa${String(index).padStart(2, "0")}`.slice(-16))
  );
  assert.throws(
    () => validateBundle(build(many)),
    (error) => error.code === "too_many_actors"
  );

  const overloaded = actor(FIRST_ACTOR_ID, {
    items: Array.from({ length: LIMITS.maxItemsPerActor + 1 }, () => ({
      type: "feat",
      name: "x",
      system: {},
    })),
  });
  assert.throws(
    () => validateBundle(build([overloaded])),
    (error) => error.code === "too_many_items"
  );
});

test("an empty selection is refused", () => {
  const bundle = build();
  bundle.selectedFolderIds = [];
  assert.throws(
    () => validateBundle(bundle),
    (error) => error.code === "empty_selection"
  );
});

test("a selected folder absent from the folder list is refused", () => {
  const bundle = build();
  bundle.selectedFolderIds = ["miss5eya6XVBAuIb"];
  assert.throws(
    () => validateBundle(bundle),
    (error) => error.code === "unknown_selected_folder"
  );
});

test("an empty folder produces a valid bundle with no Actors", () => {
  const bytes = encodeBundle(build([]));
  const parsed = JSON.parse(new TextDecoder().decode(bytes));
  assert.deepEqual(parsed.actors, []);
  assert.deepEqual(parsed.selectedFolderIds, [ACTIVE_FOLDER_ID]);
});

test("an invalid JSON-domain value inside an Actor is refused, not coerced", () => {
  assert.throws(
    () => encodeBundle(build([actor(FIRST_ACTOR_ID, { system: { hp: Number.NaN } })])),
    (error) => error instanceof BundleError && error.code === "non_finite_number"
  );
});

test("a cyclic Actor document is refused", () => {
  const system = { abilities: {} };
  system.self = system;
  assert.throws(
    () => encodeBundle(build([actor(FIRST_ACTOR_ID, { system })])),
    (error) => error instanceof BundleError && error.code === "cycle"
  );
});

test("encodeBundle produces canonical bytes the contract describes", () => {
  const text = new TextDecoder().decode(encodeBundle(build()));
  assert.equal(text.endsWith("\n"), true);
  assert.equal(text.includes(", "), false);
  assert.match(text, /^\{"actors":/);
  // Top-level keys emitted in code-point order.
  const order = [...text.matchAll(/"(actors|exportedAt|exporter|folders|schema|schemaVersion|selectedFolderIds|world)":/g)].map(
    (match) => match[1]
  );
  assert.deepEqual(order.slice(0, 8), [
    "actors",
    "exportedAt",
    "exporter",
    "folders",
    "schema",
    "schemaVersion",
    "selectedFolderIds",
    "world",
  ]);
});
