/**
 * A synthetic Foundry world, shaped like the real one and holding nothing real.
 *
 * Synthetic **by construction** (`docs/discovery/fixture-strategy.md` §1): every
 * id, name and value here was invented for the test suite. No real Actor, real
 * export or real world data is used, and none is ever committed.
 *
 * The fake `game` implements only the surface `world-source.js` reads, which is
 * also a check on that surface: adding a Foundry API to the exporter means
 * adding it here, which is the moment to ask whether the new API is a supported
 * public one.
 */

export const ROOT_FOLDER_ID = "rootQwErTyUiOpAs";
export const ACTIVE_FOLDER_ID = "actvQwErTyUiOpAs";
export const INACTIVE_FOLDER_ID = "inacQwErTyUiOpAs";
export const NESTED_FOLDER_ID = "nestQwErTyUiOpAs";

export const FIRST_ACTOR_ID = "5tYuIoPaSdFgHj6K";
export const SECOND_ACTOR_ID = "9kQpZ2mNbVcXsAe1";
export const THIRD_ACTOR_ID = "3fTgYhUjIkOlPq7W";
export const NESTED_ACTOR_ID = "7hJkLmNpQrStUvWx";

export const SUPPORTED = Object.freeze({
  worldId: "the-guild",
  coreVersion: "14.367",
  systemId: "dnd5e",
  systemVersion: "5.3.3",
});

class FakeFolder {
  constructor({ id, name, parent = null, type = "Actor" }) {
    this.id = id;
    this.name = name;
    this.type = type;
    this.folder = parent;
  }
}

class FakeActor {
  /**
   * @param {object} options
   * @param {boolean} [options.owned]  Whether the current user has OWNER on it.
   * @param {object|null} [options.sourceOverride]  Replaces what `toObject()` returns.
   */
  constructor({ id, name, folder, owned = true, sourceOverride = undefined, extra = {} }) {
    this.id = id;
    this.name = name;
    this.folder = folder;
    this._owned = owned;
    this._sourceOverride = sourceOverride;
    this._extra = extra;
  }

  testUserPermission(_user, permission) {
    return permission === "OWNER" ? this._owned : true;
  }

  toObject() {
    if (this._sourceOverride !== undefined) return this._sourceOverride;
    return {
      _id: this.id,
      name: this.name,
      img: "worlds/the-guild/assets/synthetic.webp",
      // Present in a real `toObject()` and deliberately dropped by the exporter,
      // so a test can prove they never reach the bundle.
      ownership: { default: 0, xY7SyntheticUser: 3 },
      _stats: { systemId: "dnd5e", lastModifiedBy: "xY7SyntheticUser" },
      flags: { "some-module": { note: "invented" } },
      folder: this.folder?.id ?? null,
      sort: 100000,
      type: "character",
      prototypeToken: { name: this.name },
      system: {
        abilities: {
          str: { value: 16 },
          dex: { value: 8 },
          cha: { value: 20 },
        },
        attributes: { hp: { value: 61, max: null, temp: 5 } },
        details: { xp: { value: 48000 } },
        traits: { languages: { value: ["common"], custom: "Common Sign Language" } },
      },
      items: [
        { type: "class", name: "Oathsworn", system: { identifier: "paladin", levels: 9 } },
        { type: "feat", name: "Synthetic Alertness", system: {} },
      ],
      ...this._extra,
    };
  }
}

/**
 * @param {object} [options]
 * @returns {object} A fake `game` sufficient for `world-source.js`.
 */
export function fakeGame(options = {}) {
  const {
    worldId = SUPPORTED.worldId,
    coreVersion = SUPPORTED.coreVersion,
    systemId = SUPPORTED.systemId,
    systemVersion = SUPPORTED.systemVersion,
    isGM = true,
    actorOverrides = {},
    extraActors = [],
    cyclicFolders = false,
  } = options;

  const root = new FakeFolder({ id: ROOT_FOLDER_ID, name: "Characters" });
  const active = new FakeFolder({
    id: ACTIVE_FOLDER_ID,
    name: "Characters (active)",
    parent: root,
  });
  // Deliberately the same *name* under a different parent, to prove that folder
  // identity is (id, path) and never the name alone.
  const inactive = new FakeFolder({
    id: INACTIVE_FOLDER_ID,
    name: "Characters (active)",
    parent: null,
  });
  const nested = new FakeFolder({
    id: NESTED_FOLDER_ID,
    name: "Retired",
    parent: active,
  });

  if (cyclicFolders) {
    root.folder = nested;
  }

  const actors = [
    new FakeActor({
      id: FIRST_ACTOR_ID,
      name: "Testcharacter Brightlantern",
      folder: active,
      ...(actorOverrides[FIRST_ACTOR_ID] ?? {}),
    }),
    new FakeActor({
      id: SECOND_ACTOR_ID,
      name: "Invented Ashgrove",
      folder: active,
      ...(actorOverrides[SECOND_ACTOR_ID] ?? {}),
    }),
    new FakeActor({
      id: THIRD_ACTOR_ID,
      name: "Fictional Stonewhistle",
      folder: inactive,
      ...(actorOverrides[THIRD_ACTOR_ID] ?? {}),
    }),
    // Inside a sub-folder of the selected folder: out of scope, and a test
    // proves it does not appear.
    new FakeActor({
      id: NESTED_ACTOR_ID,
      name: "Archived Nobody",
      folder: nested,
      ...(actorOverrides[NESTED_ACTOR_ID] ?? {}),
    }),
    ...extraActors,
  ];

  return {
    world: { id: worldId, title: "The Guild" },
    version: coreVersion,
    system: { id: systemId, version: systemVersion },
    user: { id: "xY7SyntheticUser", isGM },
    actors,
    folders: [root, active, inactive, nested],
    modules: { get: () => ({ version: "1.0.2" }) },
  };
}

/** A `crypto` with `subtle.digest`, which Node supplies natively. */
export const nodeCrypto = globalThis.crypto;

/**
 * A `fetch` double that records the request and answers with a fixed response.
 *
 * @param {object} response
 * @param {number} [status]
 */
export function fakeFetch(response, status = 201) {
  const calls = [];
  const impl = async (url, init) => {
    calls.push({ url, init });
    return {
      ok: status >= 200 && status < 300,
      status,
      json: async () => response,
    };
  };
  impl.calls = calls;
  return impl;
}
