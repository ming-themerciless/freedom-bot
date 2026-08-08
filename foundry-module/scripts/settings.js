/**
 * Module configuration: the endpoint and the supported deployment tuple.
 *
 * **No credential is registered here, and none may be.** Security review S-B-1
 * found the previous arrangement — the full reusable bearer secret in a
 * `scope: "world"`, `config: false` setting — to be a confidentiality defect. It
 * is, and the Foundry source establishes exactly why.
 *
 * ## What Foundry 14.365 actually does with a setting
 *
 * Read from the installed application source on this host, not inferred:
 *
 * | Question | Answer | Where |
 * |---|---|---|
 * | Who may create or update a Setting? | a user holding `SETTINGS_MODIFY`; the server enforces it | `common/documents/setting.mjs`, `BaseSetting.canUserCreate` / `#canModify` |
 * | Which clients receive a world-scoped Setting's **value**? | **every connecting client**, whatever its role | `dist/packages/world.mjs`: the per-user world payload does `db.Setting.dump().then(s => data.settings = s)` |
 * | Does `dump()` filter by user or permission? | **no** — it takes a sort option and nothing else | `dist/database/backend/server-document.mjs`, `static async dump({sort})` |
 * | Does the client filter? | no; `game.settings.storage.get("world")` *is* that delivered collection, and `getSetting(key, user)` is an in-memory lookup over it | `client/game.mjs:67`, `client/documents/collections/world-settings.mjs` |
 * | Is there a supported option giving read confidentiality? | **no.** `SETTING_SCOPES` is `client` (browser `localStorage`), `world` and `user` — and `world` and `user` are both Setting documents, both vended by the same unfiltered `dump()` | `common/constants.mjs`, `client/helpers/client-settings.mjs` |
 *
 * So `SETTINGS_MODIFY` is a **write** control, `config: false` only keeps a
 * value out of the settings *form*, and neither is a read boundary. A secret in
 * a world setting is a secret handed to every browser that joins the world.
 * There is no supported setting option that fixes this, so the fix is not a
 * different setting.
 *
 * ## Where the credential lives instead
 *
 * Nowhere persistent. The submitting GM enters it in the submission dialog,
 * once per submission; it exists in one local variable for the duration of that
 * `fetch` and is never written to a setting, `localStorage`, a flag, a journal
 * entry, a notification, a log or a receipt. `docs/operations/foundry-snapshot-submission.md`
 * §4 documents the operator workflow and the rotation consequence.
 *
 * `tests/settings.test.mjs` is the regression guard: it fails if any setting is
 * ever registered whose name could hold a secret, and if `readSettings` ever
 * returns one.
 *
 * ## Why the remaining settings are still `scope: "world"`
 *
 * They are not secrets — an endpoint URL and a version tuple — and for them the
 * world scope is the right one for the reason the old comment gave and which
 * still holds: write permission is enforced **on the server**, so an ordinary
 * player cannot repoint the endpoint. A `client`-scoped endpoint would live in
 * each browser's `localStorage`, where the player it belongs to could edit it
 * freely. `config: false` keeps them out of the settings sheet because an
 * administrator sets them from the documented console command.
 */

export const MODULE_ID = "freedom-blades-export";

export const SETTINGS = Object.freeze({
  endpoint: "submissionEndpoint",
  supportedCore: "supportedCoreVersion",
  supportedSystem: "supportedSystemVersion",
  supportedWorld: "supportedWorldId",
});

/**
 * The deployment the platform is configured to accept.
 *
 * Held in settings rather than hard-coded so that a validated Foundry or system
 * upgrade is a configuration change on both sides, matching OD-14 and ADR 0006:
 * the connector serves one deployment, and an upgrade deliberately stops
 * submission until the new tuple is validated.
 */
export const DEFAULT_SUPPORTED = Object.freeze({
  worldId: "the-guild",
  coreVersion: "14.365",
  systemId: "dnd5e",
  systemVersion: "5.3.3",
});

/**
 * @param {object} game
 */
export function registerSettings(game) {
  const register = (key, type, initial) =>
    game.settings.register(MODULE_ID, key, {
      scope: "world",
      config: false,
      type,
      default: initial,
    });

  register(SETTINGS.endpoint, String, "");
  register(SETTINGS.supportedWorld, String, DEFAULT_SUPPORTED.worldId);
  register(SETTINGS.supportedCore, String, DEFAULT_SUPPORTED.coreVersion);
  register(SETTINGS.supportedSystem, String, DEFAULT_SUPPORTED.systemVersion);
}

/**
 * Read the module's configuration. There is deliberately no credential in it.
 *
 * @param {object} game
 * @returns {{endpoint: string, supported: object}}
 */
export function readSettings(game) {
  return {
    endpoint: String(game.settings.get(MODULE_ID, SETTINGS.endpoint) ?? "").trim(),
    supported: {
      worldId: String(game.settings.get(MODULE_ID, SETTINGS.supportedWorld) ?? ""),
      coreVersion: String(game.settings.get(MODULE_ID, SETTINGS.supportedCore) ?? ""),
      systemId: DEFAULT_SUPPORTED.systemId,
      systemVersion: String(
        game.settings.get(MODULE_ID, SETTINGS.supportedSystem) ?? ""
      ),
    },
  };
}
