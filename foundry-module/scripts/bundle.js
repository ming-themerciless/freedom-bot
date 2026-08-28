/**
 * Building and validating an export bundle from plain data. Pure: no Foundry,
 * no DOM, no network.
 *
 * This is the half of the exporter that can be tested without a running Foundry
 * instance, and it is where every rule in
 * `docs/rules/foundry-export-contract.md` §2 is enforced. `world-source.js`
 * reads Foundry and produces the plain input; this module decides whether that
 * input is a legal bundle and turns it into bytes.
 *
 * The split matters for one specific reason: **the exporter must not be able to
 * emit something the Manager would refuse.** Every bound below is the Manager's
 * bound, checked here so that a refusal happens in front of the operator who
 * can fix it, before any Actor byte leaves the client.
 *
 * ## Scope: direct children of the selected folder
 *
 * Contract §2.6 requires every Actor's `folderId` to be one of
 * `selectedFolderIds`. With one selected folder that admits exactly one reading:
 * the Actors whose `folderId` *is* that folder. A recursive walk would produce
 * Actors sitting in sub-folders, whose `folderId` would not be in the selection,
 * and the Manager's parser refuses those with `actor_outside_selection`.
 *
 * So the scope is direct membership, and sub-folders are **reported** rather
 * than silently ignored: `describeSelection` returns their count so the
 * confirmation dialog can say "this folder has 2 sub-folders, whose Actors are
 * not included". An operator seeing an unexpected number is the control here.
 */

import { CanonicalError, canonicalBytes } from "./canonical.js";

export const SCHEMA = "freedom-blades.foundry-export";
export const SCHEMA_VERSION = 1;
export const EXPORTER_ID = "freedom-blades-export";

/** Contract §1 and §2.5. Each is the Manager's own limit. */
export const LIMITS = Object.freeze({
  maxBytes: 64 * 1024 * 1024,
  maxActors: 500,
  maxFolders: 64,
  maxSelectedFolders: 8,
  maxItemsPerActor: 4000,
});

/** Contract §2.6: a Foundry document id is 16 alphanumeric characters. */
const DOCUMENT_ID = /^[A-Za-z0-9]{16}$/;

/**
 * The only Actor keys the contract admits. `img` is optional; the Manager
 * accepts it and nothing else beyond these.
 *
 * Everything absent from this list is absent on purpose — `ownership`, `_stats`,
 * `flags`, `prototypeToken`, `folder`, `sort`, `type`, `effects`. Contract §3
 * forbids ownership grants and user ids, and the Manager refuses an unknown
 * Actor key outright.
 */
export const ACTOR_KEYS = Object.freeze([
  "id",
  "folderId",
  "name",
  "img",
  "system",
  "items",
]);

export class BundleError extends Error {
  constructor(code, message) {
    super(message);
    this.name = "BundleError";
    this.code = code;
  }
}

/**
 * The leading `components` of a dotted version, or `null` if it is malformed.
 *
 * **Every** component is validated, not only the compared prefix: `14.x` and
 * `5.3.3-beta` would otherwise pass because their tails are never read, and a
 * prerelease game system is exactly the case that should stop and ask.
 *
 * `null` never equals anything, including another `null`, so an unreadable
 * version on either side is a mismatch. Fail closed.
 *
 * **This must stay identical to `SupportedDeployment._series` in
 * `domain/foundry.py`.** The module refuses before assembling a bundle and the
 * server refuses on submission; two different rules would mean an export the
 * module allowed and the server rejected, or worse the reverse.
 */
function versionSeries(value, components) {
  const parts = String(value).split(".");
  if (parts.length < components) return null;
  if (!parts.every((part) => /^\d+$/.test(part))) return null;
  return parts.slice(0, components).join(".");
}

/** Foundry core ranges over the generation; the game system over major.minor. */
const CORE_COMPONENTS = 1;
const SYSTEM_COMPONENTS = 2;

/**
 * Validate the deployment tuple before anything else happens.
 *
 * Fails **before Actor bytes are read**, let alone sent: an unsupported Foundry
 * or system version means the Manager would refuse the bundle anyway, and there
 * is no reason to have assembled every active character's mechanics first.
 *
 * **Not exact equality (OD-14 controlled baseline v1.6).** World and system ids
 * match exactly; Foundry core is compared over its generation and dnd5e over
 * major.minor; malformed or out-of-range versions fail closed. An in-range build
 * therefore proceeds — and still owes the operational export-and-preview check,
 * because parsing a shape is not evidence that semantics are unchanged.
 *
 * @param {{id: string, title: string, coreVersion: string, systemId: string, systemVersion: string}} world
 * @param {{worldId: string, coreVersion: string, systemId: string, systemVersion: string}} supported
 */
export function assertSupportedDeployment(world, supported) {
  const differences = [];
  if (world.id !== supported.worldId) {
    differences.push(`world ${world.id} (expected ${supported.worldId})`);
  }
  const coreSeen = versionSeries(world.coreVersion, CORE_COMPONENTS);
  const coreWant = versionSeries(supported.coreVersion, CORE_COMPONENTS);
  if (coreSeen === null || coreWant === null || coreSeen !== coreWant) {
    differences.push(
      `Foundry ${world.coreVersion} (expected the ` +
        `${coreWant === null ? supported.coreVersion : `${coreWant}.x`} series)`
    );
  }
  if (world.systemId !== supported.systemId) {
    differences.push(`system ${world.systemId} (expected ${supported.systemId})`);
  }
  const sysSeen = versionSeries(world.systemVersion, SYSTEM_COMPONENTS);
  const sysWant = versionSeries(supported.systemVersion, SYSTEM_COMPONENTS);
  if (sysSeen === null || sysWant === null || sysSeen !== sysWant) {
    differences.push(
      `system version ${world.systemVersion} (expected the ` +
        `${sysWant === null ? supported.systemVersion : `${sysWant}.x`} series)`
    );
  }
  if (differences.length > 0) {
    throw new BundleError(
      "unsupported_deployment",
      `This deployment is not the one the Freedom Blades platform is ` +
        `configured for: ${differences.join("; ")}. Nothing was exported. A ` +
        `Foundry or system upgrade deliberately stops submission until the ` +
        `platform's supported version is updated.`
    );
  }
}

/**
 * Resolve one selected folder into itself plus every ancestor.
 *
 * The Manager needs the ancestors to present a full path such as
 * `/actors/Characters/Characters (active)` without asking Foundry anything, and
 * refuses a bundle whose `parentId` names a folder it does not carry.
 *
 * @param {string} folderId
 * @param {Map<string, {id: string, name: string, parentId: string|null}>} folders
 * @returns {Array<{id: string, name: string, parentId: string|null}>}
 */
export function withAncestors(folderId, folders) {
  const chain = [];
  const seen = new Set();
  let current = folderId;
  while (current !== null && current !== undefined) {
    if (seen.has(current)) {
      throw new BundleError(
        "folder_cycle",
        "The folder graph contains a cycle, so no path can be presented for it."
      );
    }
    seen.add(current);
    const folder = folders.get(current);
    if (folder === undefined) {
      throw new BundleError(
        "unknown_parent_folder",
        `Folder ${current} is missing from this world's folder list, so the ` +
          "selected folder's full path cannot be built."
      );
    }
    chain.push(folder);
    current = folder.parentId ?? null;
  }
  return chain;
}

/**
 * The displayed path of a folder, matching what the Manager builds from ids.
 *
 * @param {string} folderId
 * @param {Map<string, {id: string, name: string, parentId: string|null}>} folders
 * @returns {string}
 */
export function folderPath(folderId, folders) {
  const chain = withAncestors(folderId, folders);
  return `/actors/${chain.map((folder) => folder.name).reverse().join("/")}`;
}

/**
 * Assemble a bundle document from validated plain inputs.
 *
 * @param {object} input
 * @param {string} input.exporterVersion
 * @param {string} input.exportedAt      RFC 3339 UTC, ending `Z`.
 * @param {object} input.world
 * @param {string} input.selectedFolderId
 * @param {Map<string, {id: string, name: string, parentId: string|null}>} input.folders
 * @param {Array<object>} input.actors   Already reduced to the accepted keys.
 * @returns {object}
 */
export function buildBundle({
  exporterVersion,
  exportedAt,
  world,
  selectedFolderId,
  folders,
  actors,
}) {
  const chain = withAncestors(selectedFolderId, folders);
  const bundleFolders = chain
    .map((folder) => ({
      id: folder.id,
      name: folder.name,
      parentId: folder.parentId ?? null,
    }))
    // Contract §1: `folders` ascending by id. Sorted here rather than left to
    // the canonical encoder, because array order is not something key sorting
    // touches.
    .sort((left, right) => (left.id < right.id ? -1 : left.id > right.id ? 1 : 0));

  const bundleActors = [...actors].sort((left, right) =>
    left.id < right.id ? -1 : left.id > right.id ? 1 : 0
  );

  return {
    schema: SCHEMA,
    schemaVersion: SCHEMA_VERSION,
    exporter: { id: EXPORTER_ID, version: exporterVersion },
    exportedAt,
    world: {
      id: world.id,
      title: world.title,
      coreVersion: world.coreVersion,
      systemId: world.systemId,
      systemVersion: world.systemVersion,
    },
    selectedFolderIds: [selectedFolderId],
    folders: bundleFolders,
    actors: bundleActors,
  };
}

/**
 * Every structural rule the Manager applies, applied here first.
 *
 * Ambiguity is a refusal, not a warning, for the same reason it is in the
 * Manager: the only way past a duplicate id is to guess which record was meant,
 * and the record being guessed at is a character.
 *
 * @param {object} bundle
 */
export function validateBundle(bundle) {
  const selected = bundle.selectedFolderIds;
  if (!Array.isArray(selected) || selected.length === 0) {
    throw new BundleError(
      "empty_selection",
      "No folder was selected, so there is nothing to export."
    );
  }
  if (selected.length > LIMITS.maxSelectedFolders) {
    throw new BundleError(
      "too_many_selected_folders",
      `${selected.length} folders were selected, over the ` +
        `${LIMITS.maxSelectedFolders} the contract allows.`
    );
  }

  const folderIds = new Set();
  for (const folder of bundle.folders) {
    if (!DOCUMENT_ID.test(folder.id)) {
      throw new BundleError(
        "malformed_folder_id",
        "A folder carries an id that is not a 16-character Foundry id."
      );
    }
    if (folderIds.has(folder.id)) {
      throw new BundleError(
        "duplicate_folder_id",
        `Folder id ${folder.id} appears more than once.`
      );
    }
    folderIds.add(folder.id);
    if (typeof folder.name !== "string" || folder.name.trim() === "") {
      throw new BundleError(
        "malformed_folders",
        `Folder ${folder.id} has no usable name.`
      );
    }
  }
  if (bundle.folders.length > LIMITS.maxFolders) {
    throw new BundleError(
      "too_many_folders",
      `The bundle carries ${bundle.folders.length} folders, over the ` +
        `${LIMITS.maxFolders} the contract allows.`
    );
  }
  for (const folder of bundle.folders) {
    if (folder.parentId !== null && !folderIds.has(folder.parentId)) {
      throw new BundleError(
        "unknown_parent_folder",
        `Folder ${folder.id} names a parent the bundle does not contain.`
      );
    }
  }
  for (const identifier of selected) {
    if (!folderIds.has(identifier)) {
      throw new BundleError(
        "unknown_selected_folder",
        `Selected folder ${identifier} is not present in the folder list.`
      );
    }
  }

  if (bundle.actors.length > LIMITS.maxActors) {
    throw new BundleError(
      "too_many_actors",
      `The selection holds ${bundle.actors.length} Actors, over the ` +
        `${LIMITS.maxActors} the contract allows.`
    );
  }

  const selectedSet = new Set(selected);
  const actorIds = new Set();
  for (const actor of bundle.actors) {
    if (typeof actor.id !== "string" || !DOCUMENT_ID.test(actor.id)) {
      throw new BundleError(
        "malformed_actor_id",
        "An Actor carries a missing or malformed id. An Actor is never " +
          "identified by its name, so it cannot be exported without one."
      );
    }
    if (actorIds.has(actor.id)) {
      throw new BundleError(
        "duplicate_actor_id",
        `Actor id ${actor.id} appears more than once.`
      );
    }
    actorIds.add(actor.id);
    if (!selectedSet.has(actor.folderId)) {
      throw new BundleError(
        "actor_outside_selection",
        `Actor ${actor.id} sits outside the selected folder.`
      );
    }
    if (typeof actor.name !== "string" || actor.name.trim() === "") {
      throw new BundleError(
        "malformed_actor",
        `Actor ${actor.id} has no usable name.`
      );
    }
    if (actor.system === null || typeof actor.system !== "object" || Array.isArray(actor.system)) {
      throw new BundleError(
        "malformed_actor",
        `Actor ${actor.id} has no system object.`
      );
    }
    if (!Array.isArray(actor.items)) {
      throw new BundleError(
        "malformed_actor",
        `Actor ${actor.id} has no items array.`
      );
    }
    if (actor.items.length > LIMITS.maxItemsPerActor) {
      throw new BundleError(
        "too_many_items",
        `Actor ${actor.id} carries ${actor.items.length} embedded items, over ` +
          `the ${LIMITS.maxItemsPerActor} limit.`
      );
    }
    for (const item of actor.items) {
      if (item === null || typeof item !== "object" || Array.isArray(item)) {
        throw new BundleError(
          "malformed_actor",
          `Actor ${actor.id} carries an item that is not an object.`
        );
      }
      if (typeof item.type !== "string" || item.type.trim() === "") {
        throw new BundleError(
          "malformed_actor",
          `Actor ${actor.id} carries an item with no document type. An ` +
            "unclassified item is never read."
        );
      }
    }
    const unknown = Object.keys(actor).filter((key) => !ACTOR_KEYS.includes(key));
    if (unknown.length > 0) {
      throw new BundleError(
        "unknown_actor_key",
        `Actor ${actor.id} carries key(s) the contract does not permit: ` +
          `${unknown.sort().join(", ")}.`
      );
    }
  }
}

/**
 * Validate and encode. The single producer of the bytes that are hashed, sent
 * and downloaded — so those three can never disagree.
 *
 * @param {object} bundle
 * @returns {Uint8Array}
 */
export function encodeBundle(bundle) {
  validateBundle(bundle);
  let bytes;
  try {
    bytes = canonicalBytes(bundle);
  } catch (error) {
    if (error instanceof CanonicalError) {
      throw new BundleError(error.code, error.message);
    }
    throw error;
  }
  if (bytes.byteLength > LIMITS.maxBytes) {
    throw new BundleError(
      "artifact_too_large",
      `The bundle is ${bytes.byteLength} bytes, over the ` +
        `${LIMITS.maxBytes}-byte limit. Nothing was sent.`
    );
  }
  return bytes;
}
