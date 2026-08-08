/**
 * The only file that reads Foundry. Everything it produces is plain data.
 *
 * Keeping the Foundry reads in one small module is what lets `bundle.js` and
 * `canonical.js` be tested with `node --test` and no Foundry instance at all,
 * and it is also the file to read when checking that this module touches
 * nothing it should not.
 *
 * ## Every API used here, and where it was verified
 *
 * Verified against the installed Foundry **14.365.0** application source on this
 * host, not from memory:
 *
 * | API | Verified in |
 * |---|---|
 * | `game.actors` | `client/game.mjs` — the world `Actors` collection |
 * | `game.folders` | `client/game.mjs` — the world `Folders` collection |
 * | `game.world.id`, `game.world.title` | `client/game.mjs`, `foundry.packages.World` |
 * | `game.version` | `client/game.mjs` — `get version()` returns `release.version` |
 * | `game.system.id`, `game.system.version` | `client/game.mjs` |
 * | `game.user.isGM` | `common/documents/user.mjs` |
 * | `Document#toObject()` | `common/abstract/document.mjs` |
 * | `Document#testUserPermission(user, "OWNER")` | `common/abstract/document.mjs` |
 * | `Folder#folder` (parent), `Folder#type` | `client/documents/folder.mjs` |
 *
 * No private underscored internal is used anywhere. In particular this module
 * does **not** read `worlds/…/data`, LevelDB, a compendium pack, the
 * `Actors (shared)` compendium, or the filesystem. `game.actors` is the live
 * world collection; a compendium copy may be stale and is explicitly not the
 * source.
 *
 * ## Read-only, structurally
 *
 * Nothing here calls `create`, `update`, `delete`, `createEmbeddedDocuments`,
 * `updateEmbeddedDocuments`, `deleteEmbeddedDocuments`, `importFromJSON`,
 * `exportToCompendium` or `game.settings.set`. `toObject()` returns a copy of
 * the document's source; reading it changes nothing.
 */

import { ACTOR_KEYS } from "./bundle.js";
import { MAX_DEPTH } from "./canonical.js";

export class SourceError extends Error {
  constructor(code, message) {
    super(message);
    this.name = "SourceError";
    this.code = code;
  }
}

/**
 * The deployment tuple this client is actually running.
 *
 * Read rather than assumed. The contract validates the tuple, and the whole
 * value of that check is lost if the exporter writes the expected values
 * instead of the observed ones.
 *
 * @param {object} game
 * @returns {{id: string, title: string, coreVersion: string, systemId: string, systemVersion: string}}
 */
export function readWorld(game) {
  const world = game?.world;
  const system = game?.system;
  if (!world?.id || !system?.id) {
    throw new SourceError(
      "world_unavailable",
      "The world or game system could not be read. Try again once Foundry has " +
        "finished loading."
    );
  }
  return {
    id: String(world.id),
    title: String(world.title ?? world.id),
    coreVersion: String(game.version),
    systemId: String(system.id),
    systemVersion: String(system.version),
  };
}

/**
 * Every world Actor folder, as plain records keyed by stable id.
 *
 * `Folder#folder` is the parent *document*; `parentId` is its id or `null` at
 * the root. Folder identity is (id, displayed path) — never the name, because
 * two folders may legitimately share a name under different parents.
 *
 * @param {object} game
 * @returns {Map<string, {id: string, name: string, parentId: string|null}>}
 */
export function readFolders(game) {
  const folders = new Map();
  for (const folder of game.folders ?? []) {
    if (folder.type !== "Actor") continue;
    folders.set(folder.id, {
      id: String(folder.id),
      name: String(folder.name),
      parentId: folder.folder ? String(folder.folder.id) : null,
    });
  }
  return folders;
}

/**
 * Selectable folders, each with its full path and its direct Actor count.
 *
 * The counts are what the confirmation dialog shows. `subfolders` is included
 * because the export scope is direct membership: an operator who expects a
 * recursive export needs to see that a folder has children whose Actors are not
 * included, rather than discover it from a count that looks low.
 *
 * @param {object} game
 * @returns {Array<{id: string, name: string, path: string, actors: number, subfolders: number}>}
 */
export function describeSelectableFolders(game) {
  const folders = readFolders(game);
  const actorCounts = new Map();
  for (const actor of game.actors ?? []) {
    const parent = actor.folder ? String(actor.folder.id) : null;
    if (parent === null) continue;
    actorCounts.set(parent, (actorCounts.get(parent) ?? 0) + 1);
  }
  const childCounts = new Map();
  for (const folder of folders.values()) {
    if (folder.parentId === null) continue;
    childCounts.set(folder.parentId, (childCounts.get(folder.parentId) ?? 0) + 1);
  }

  const described = [];
  for (const folder of folders.values()) {
    described.push({
      id: folder.id,
      name: folder.name,
      path: pathOf(folder.id, folders),
      actors: actorCounts.get(folder.id) ?? 0,
      subfolders: childCounts.get(folder.id) ?? 0,
    });
  }
  described.sort((left, right) => (left.path < right.path ? -1 : left.path > right.path ? 1 : 0));
  return described;
}

function pathOf(folderId, folders) {
  const names = [];
  const seen = new Set();
  let current = folderId;
  while (current !== null && current !== undefined) {
    if (seen.has(current)) return "/actors/(cycle)";
    seen.add(current);
    const folder = folders.get(current);
    if (folder === undefined) return "/actors/(unknown)";
    names.push(folder.name);
    current = folder.parentId;
  }
  return `/actors/${names.reverse().join("/")}`;
}

/**
 * Whether this user may export at all.
 *
 * A GM role is the *Foundry* authority to read every Actor in the world. It is
 * emphatically **not** proof of Discord Guild Council membership, and this
 * module never claims otherwise: submitting a snapshot creates a pending
 * artifact that a Council member must separately preview and confirm. The two
 * authorities are documented side by side in
 * `docs/operations/foundry-snapshot-submission.md`.
 *
 * @param {object} game
 * @returns {boolean}
 */
export function mayExport(game) {
  return game?.user?.isGM === true;
}

/**
 * The Actors directly inside `folderId`, reduced to the contract's keys.
 *
 * Two checks that are easy to leave out, and both are load-bearing:
 *
 * - **per-Actor permission.** `mayExport` establishes the role; this
 *   establishes that the role actually reaches *this* Actor. `testUserPermission`
 *   returns `OWNER` for a GM, so for a GM it passes — which is the point: the
 *   check is written against the document rather than against an assumption
 *   about what a GM can see, so it stays correct if the export is ever opened
 *   to a narrower role;
 * - **`_id` is present and real.** Contract §2.6 and ADR 0006's 2026-08-02
 *   amendment: a per-Actor Foundry export writes `"_id": null` and leaves the
 *   real id only in its filename. `toObject()` over `game.actors` carries the
 *   real one, and an Actor without it is refused rather than matched by name.
 *
 * @param {object} game
 * @param {string} folderId
 * @returns {Array<object>}
 */
export function readActors(game, folderId) {
  const user = game.user;
  const actors = [];
  for (const actor of game.actors ?? []) {
    const parent = actor.folder ? String(actor.folder.id) : null;
    if (parent !== folderId) continue;

    if (!actor.testUserPermission(user, "OWNER")) {
      throw new SourceError(
        "insufficient_permission",
        "This user does not have full access to every Actor in the selected " +
          "folder, so a complete snapshot cannot be taken. Nothing was sent."
      );
    }

    const source = actor.toObject();
    const identifier = source._id ?? actor.id;
    if (typeof identifier !== "string" || identifier === "") {
      throw new SourceError(
        "missing_actor_id",
        "An Actor in the selected folder has no stable Foundry id. It cannot " +
          "be exported, because an Actor is never identified by its name."
      );
    }

    const reduced = {
      id: String(identifier),
      folderId,
      name: String(source.name),
      system: source.system,
      items: Array.isArray(source.items) ? source.items : [],
    };
    if (typeof source.img === "string" && source.img !== "") {
      reduced.img = source.img;
    }
    // Belt and braces: build only the accepted keys above, then prove it. A
    // future edit that adds one would fail here rather than at the Manager.
    for (const key of Object.keys(reduced)) {
      if (!ACTOR_KEYS.includes(key)) {
        throw new SourceError(
          "unknown_actor_key",
          `The exporter produced an Actor key the contract does not permit: ${key}.`
        );
      }
    }

    const projected = projectFoundryData(reduced, `$actors[${actors.length}]`);
    actors.push(projected);
  }
  return actors;
}


/**
 * Closed allowlist of repository-authored static structural key names.
 * Keys in this allowlist are safe to include directly in error paths. Any key outside
 * this allowlist is represented by its zero-based Object.keys ordinal (e.g. `.{key:0}`).
 */
const SAFE_STRUCTURAL_KEYS = Object.freeze([
  "schema",
  "schemaVersion",
  "exporter",
  "exportedAt",
  "world",
  "selectedFolderId",
  "selectedFolderIds",
  "folders",
  "actors",
  "id",
  "folderId",
  "parentId",
  "name",
  "title",
  "coreVersion",
  "systemId",
  "systemVersion",
  "system",
  "items",
  "type",
  "img",
  "advancement",
  "details",
]);

/**
 * Safely format an object key path segment so dynamic document IDs, Item IDs,
 * advancement IDs, UUIDs or user data are never disclosed in error messages.
 *
 * @param {string} key
 * @param {number} ordinal
 * @returns {string}
 */
export function safeKeySegment(key, ordinal) {
  if (SAFE_STRUCTURAL_KEYS.includes(key)) {
    return `.${key}`;
  }
  return `.{key:${ordinal}}`;
}

/**
 * Pure projection at the Foundry source boundary between `Document#toObject()`
 * and bundle construction / canonical encoding.
 *
 * Semantic distinction (see docs/rules/foundry-export-contract.md):
 * - `undefined` as an optional object property at the Foundry API boundary is
 *   skipped while constructing a new projected result; the source object and its
 *   property are unchanged. This maps dnd5e's `initial: undefined` schema marker to
 *   JSON property absence without mutating the source Foundry object.
 * - `undefined` in an array or anywhere AFTER this boundary remains an exporter
 *   defect and causes a fail-closed refusal.
 *
 * @param {any} value
 * @param {string} [path="$"]
 * @param {Set<object>} [visited=new Set()]
 * @param {number} [depth=0]
 * @returns {any}
 */
export function projectFoundryData(value, path = "$", visited = new Set(), depth = 0) {
  if (value === null || typeof value === "boolean") {
    return value;
  }

  if (typeof value === "string") {
    return value.normalize("NFC");
  }

  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new SourceError(
        "unsupported_type",
        `Non-finite number at ${path} is refused.`
      );
    }
    if (Object.is(value, -0)) {
      throw new SourceError(
        "unsupported_type",
        `Negative zero at ${path} is refused.`
      );
    }
    return value;
  }

  if (typeof value !== "object") {
    throw new SourceError(
      "unsupported_type",
      `Value of type ${typeof value} at ${path} is refused.`
    );
  }

  const nextDepth = depth + 1;
  if (nextDepth > MAX_DEPTH) {
    throw new SourceError(
      "excessive_depth",
      `Nesting depth at ${path} exceeds maximum allowed limit of ${MAX_DEPTH}.`
    );
  }

  if (visited.has(value)) {
    throw new SourceError(
      "cycle_detected",
      `Circular reference detected at ${path}.`
    );
  }

  if (Array.isArray(value)) {
    const nextVisited = new Set(visited).add(value);
    const result = [];
    for (let i = 0; i < value.length; i++) {
      const item = value[i];
      const itemPath = `${path}[${i}]`;
      if (item === undefined) {
        throw new SourceError(
          "undefined_array_element",
          `Array element at ${itemPath} is undefined. JSON has no undefined, and array indexes cannot be omitted or converted.`
        );
      }
      result.push(projectFoundryData(item, itemPath, nextVisited, nextDepth));
    }
    return result;
  }

  const prototype = Object.getPrototypeOf(value);
  if (prototype !== Object.prototype && prototype !== null) {
    throw new SourceError(
      "unsupported_type",
      `Non-plain object instance at ${path} is refused.`
    );
  }

  const nextVisited = new Set(visited).add(value);
  const result = {};
  const keys = Object.keys(value);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];
    const propVal = value[key];
    const keyPath = `${path}${safeKeySegment(key, i)}`;
    if (propVal === undefined) {
      // The property is skipped while constructing a new projected result;
      // the source object and its property are unchanged.
      continue;
    }
    result[key.normalize("NFC")] = projectFoundryData(
      propVal,
      keyPath,
      nextVisited,
      nextDepth
    );
  }
  return result;
}
