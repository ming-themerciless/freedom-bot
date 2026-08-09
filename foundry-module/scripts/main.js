/**
 * The Foundry entry point: one button, one dialog, and safe notifications.
 *
 * Everything with a decision in it lives in `workflow.js`, `bundle.js`,
 * `canonical.js`, `world-source.js` and `transport.js`, each of which is tested
 * with `node --test` and no Foundry. What is left here is the part that can only
 * be exercised by opening Foundry, and it is kept deliberately thin for exactly
 * that reason. The manual smoke test for it is documented in
 * `docs/operations/foundry-snapshot-submission.md` §6.
 *
 * ## The APIs used, verified against Foundry 14.365.0 on this host
 *
 * | API | Verified in |
 * |---|---|
 * | `Hooks.once("init")`, `Hooks.on("renderActorDirectory", …)` | `client/applications/api/application.mjs` dispatches `render{ClassName}` with `(application, element, context, options)` |
 * | `foundry.applications.api.DialogV2.wait` | `client/applications/api/dialog.mjs` |
 * | `foundry.utils.saveDataToFile(data, type, filename)` | `client/utils/helpers.mjs` |
 * | `ui.notifications.info/warn/error` | `client/ui.mjs` |
 * | `game.settings.register/get` | `client/helpers/client-settings.mjs` |
 *
 * ## What is never shown or logged
 *
 * No Actor name, no mechanic, no embedded item, no raw JSON, no credential and
 * no internal path reaches a notification, a dialog or the console. Folder
 * names and paths *are* shown — they are what the operator is choosing between,
 * and they describe the world's organisation rather than a character's state.
 * Every one of them is inserted as a text node rather than as HTML, so a folder
 * named `<img onerror=…>` is displayed, not executed.
 *
 * ## The credential is entered here and kept nowhere
 *
 * Security review S-B-1: a reusable bearer in a world setting is delivered to
 * every browser that joins the world (`settings.js` records the Foundry source
 * that establishes it). So the credential is not configuration at all. The
 * submitting GM types or pastes it into the dialog, it lives in one local
 * variable for the duration of one `fetch`, and `run` clears that variable
 * before it returns.
 *
 * It is never written to a setting, to `localStorage`, to a flag or to a
 * document; it is never rendered back into the dialog; and it never appears in
 * a notification, because `notifyFailure` shows only typed error codes and
 * messages this repository wrote. The input is `type="password"` and
 * `autocomplete="off"`, so it is not shown on screen and is not offered back by
 * the browser.
 *
 * The button remains hidden from non-GMs, but that is now only tidiness: the
 * authority to submit is the secret the person holds, which no amount of
 * client-side state inspection yields.
 */

import { BundleError } from "./bundle.js";
import { MODULE_ID, readSettings, registerSettings } from "./settings.js";
import { failureNotification } from "./notifications.js";
import { SourceError, describeSelectableFolders, mayExport } from "./world-source.js";
import { TransportError } from "./transport.js";
import {
  PreparedSnapshotState,
  WorkflowError,
  describeReceipt,
  executeWorkflow,
} from "./workflow.js";

const MODULE_TITLE = "Freedom Blades";
const snapshotState = new PreparedSnapshotState();
let submissionDialogOpen = false;

Hooks.once("init", () => {
  registerSettings(game);
});

Hooks.on("renderActorDirectory", (application, element) => {
  if (!mayExport(game)) return;
  const root = element instanceof HTMLElement ? element : application?.element;
  if (!root || root.querySelector(`.${MODULE_ID}-control`)) return;

  const button = document.createElement("button");
  button.type = "button";
  button.className = `${MODULE_ID}-control`;
  button.textContent = "Submit Freedom Blades Snapshot";
  button.addEventListener("click", () => {
    if (submissionDialogOpen) {
      ui.notifications.warn(
        `${MODULE_TITLE}: a snapshot workflow is already open. Finish or cancel it first.`
      );
      return;
    }
    void openSubmissionDialog();
  });

  const footer = root.querySelector(".directory-footer") ?? root;
  footer.append(button);
});

/**
 * Choose a folder, confirm the exact scope, then submit or download.
 */
async function openSubmissionDialog() {
  if (submissionDialogOpen) return;
  submissionDialogOpen = true;
  try {
    await openSubmissionDialogOnce();
  } finally {
    submissionDialogOpen = false;
  }
}

async function openSubmissionDialogOnce() {
  const folders = describeSelectableFolders(game);
  if (folders.length === 0) {
    ui.notifications.warn(
      `${MODULE_TITLE}: this world has no Actor folders, so there is nothing to submit.`
    );
    return;
  }

  const settings = readSettings(game);
  const hasPinned = snapshotState.hasPinnedRetry();
  const content = buildDialogContent(folders, settings, hasPinned);

  const buttons = [];
  if (hasPinned) {
    buttons.push(
      {
        action: "submit",
        label: "Retry Pinned Submission",
        icon: "fa-solid fa-rotate-right",
        default: true,
        callback: (event, button) => submissionChoice(button, false),
      },
      {
        action: "discard-and-submit",
        label: "Discard Pinned & Prepare New",
        icon: "fa-solid fa-trash-can",
        callback: (event, button) => submissionChoice(button, true),
      },
      {
        action: "discard-and-download",
        label: "Discard Pinned & Download Selected",
        icon: "fa-solid fa-file-arrow-down",
        callback: (event, button) => ({
          action: "download",
          folderId: button.form.elements.folderId.value,
          credential: "",
          discardPinned: true,
        }),
      }
    );
  } else {
    buttons.push({
      action: "submit",
      label: "Submit to Freedom Blades",
      icon: "fa-solid fa-cloud-arrow-up",
      default: true,
      callback: (event, button) => submissionChoice(button, false),
    });
  }

  buttons.push(
    {
      action: "download",
      label: "Download JSON (fallback)",
      icon: "fa-solid fa-download",
      callback: (event, button) => ({
        action: "download",
        folderId: button.form.elements.folderId.value,
        // The fallback writes a local file and reaches no network. It is
        // given no credential at all rather than one it would ignore.
        credential: "",
        discardPinned: false,
      }),
    },
    { action: "cancel", label: "Cancel", icon: "fa-solid fa-xmark" }
  );

  const choice = await foundry.applications.api.DialogV2.wait({
    window: { title: `${MODULE_TITLE} — Submit Snapshot` },
    content,
    buttons,
    rejectClose: false,
  });

  if (!choice || choice === "cancel" || choice.action === "cancel") return;
  try {
    await run(choice.action, choice.folderId, choice.credential, settings, {
      discardPinned: choice.discardPinned ?? false,
    });
  } finally {
    // The dialog's own DOM is gone by now, but the object the callback built is
    // still referenced here. Clearing it keeps the secret's lifetime as short
    // as this function rather than as long as whatever holds `choice`.
    choice.credential = "";
  }
}

/** Refuse an empty secret while the dialog still owns the form and its pin. */
function submissionChoice(button, discardPinned) {
  const credential = button.form.elements.submissionCredential.value;
  if (!credential.trim()) {
    ui.notifications.error(
      `${MODULE_TITLE} [missing_credential]: Enter the submission credential before submitting.`
    );
    return false;
  }
  return {
    action: "submit",
    folderId: button.form.elements.folderId.value,
    credential,
    discardPinned,
  };
}

/**
 * Build the dialog body as an element tree.
 *
 * Not a template string: folder names come from the world and would otherwise
 * be interpolated into HTML. `DialogV2` runs its `content` through
 * `cleanHTML`, which is a sanitiser rather than an escaper — building nodes and
 * setting `textContent` means nothing has to be sanitised in the first place.
 *
 * @param {Array<object>} folders
 * @param {object} settings
 * @param {boolean} [hasPinnedRetry=false]
 * @returns {HTMLDivElement}
 */
function buildDialogContent(folders, settings, hasPinnedRetry = false) {
  const container = document.createElement("div");

  const intro = document.createElement("p");
  intro.textContent =
    "Select one Actor folder. Its Actors are read from this world and sent as " +
    "an immutable snapshot. Nothing in Foundry is changed, and nothing is " +
    "applied until a Guild Council member reviews it.";
  container.append(intro);

  if (hasPinnedRetry) {
    const pinnedNote = document.createElement("p");
    pinnedNote.className = `${MODULE_ID}-warning`;
    pinnedNote.textContent =
      "An unconfirmed submission attempt is pinned. Submitting will resend the exact " +
      "unconfirmed payload. Download fallback also uses that payload. Choose an explicit " +
      "Discard action to abandon it and prepare the selected folder instead. Do not reload " +
      "this page while a delivery is unconfirmed: retry state exists only for this page load.";
    container.append(pinnedNote);
  }

  const label = document.createElement("label");
  label.textContent = "Actor folder";
  const select = document.createElement("select");
  select.name = "folderId";
  for (const folder of folders) {
    const option = document.createElement("option");
    option.value = folder.id;
    const suffix =
      folder.subfolders > 0
        ? ` — ${folder.actors} Actor(s), ${folder.subfolders} sub-folder(s) NOT included`
        : ` — ${folder.actors} Actor(s)`;
    option.textContent = `${folder.path} [${folder.id}]${suffix}`;
    select.append(option);
  }
  label.append(select);
  container.append(label);

  // The credential is asked for here rather than read from configuration,
  // because Foundry has no configuration a browser client cannot read
  // (`settings.js`). `type="password"` keeps it off the screen and out of any
  // screenshot; `autocomplete="off"` keeps the browser from storing and
  // re-offering it; and nothing ever writes the value back.
  const credentialLabel = document.createElement("label");
  credentialLabel.textContent = "Submission credential";
  const credentialInput = document.createElement("input");
  credentialInput.type = "password";
  credentialInput.name = "submissionCredential";
  credentialInput.autocomplete = "off";
  credentialInput.spellcheck = false;
  credentialInput.required = true;
  credentialInput.placeholder = "<principal id>.<secret>";
  credentialLabel.append(credentialInput);
  container.append(credentialLabel);

  const credentialNote = document.createElement("p");
  credentialNote.className = `${MODULE_ID}-credential-note`;
  credentialNote.textContent =
    "Entered once per submission and stored nowhere: Foundry has no setting " +
    "a browser client cannot read, so keeping it here would hand it to every " +
    "user in this world. Keep it in your password manager. Not needed for the " +
    "download fallback.";
  container.append(credentialNote);

  const deployment = document.createElement("p");
  deployment.className = `${MODULE_ID}-deployment`;
  deployment.textContent =
    `This world: ${game.world.id} · Foundry ${game.version} · ` +
    `${game.system.id} ${game.system.version}. ` +
    `Platform expects: ${settings.supported.worldId} · Foundry ` +
    `${settings.supported.coreVersion} · ${settings.supported.systemId} ` +
    `${settings.supported.systemVersion}.`;
  container.append(deployment);

  if (!settings.endpoint) {
    const warning = document.createElement("p");
    warning.className = `${MODULE_ID}-warning`;
    warning.textContent =
      "No submission endpoint is configured, so only the download fallback " +
      "will work. A Foundry administrator configures it.";
    container.append(warning);
  }

  return container;
}

/**
 * @param {"submit"|"download"} action
 * @param {string} folderId
 * @param {string} credential  Entered in the dialog; cleared before this returns.
 * @param {object} settings
 * @param {object} [options]
 * @param {boolean} [options.discardPinned=false]
 */
async function run(action, folderId, credential, settings, { discardPinned = false } = {}) {
  const version = game.modules.get(MODULE_ID)?.version ?? "0.0.0";
  try {
    const { prepared, receipt } = await executeWorkflow({
      game,
      crypto: globalThis.crypto,
      folderId,
      exporterVersion: version,
      supported: settings.supported,
      state: snapshotState,
      action,
      endpoint: settings.endpoint,
      credential,
      fetchImpl: globalThis.fetch.bind(globalThis),
      discardPinned,
      downloadPrepared: (p) => {
        foundry.utils.saveDataToFile(
          new TextDecoder().decode(p.bytes),
          "application/json",
          `${game.world.id}-${p.checksum.slice(0, 12)}.json`
        );
        ui.notifications.info(
          `${MODULE_TITLE}: downloaded ${p.actorCount} Actor(s) from ` +
            `${p.folderPath}, checksum ${p.checksum.slice(0, 12)}…. ` +
            "This is the fallback path; hand the file to an operator only if direct " +
            "submission is unavailable."
        );
      },
    });

    if (action === "submit") {
      ui.notifications.info(
        `${MODULE_TITLE}: ${describeReceipt(receipt, prepared.checksum)}`
      );
    }
  } catch (error) {
    const retryPinned = action === "submit" && snapshotState.hasPinnedRetry();
    notifyFailure(
      error,
      action === "download"
        ? "The download did not complete; no submission was attempted."
        : "Nothing was recorded or confirmed. Submitting the same export again is " +
          "safe: a retry cannot create a second snapshot.",
      retryPinned
    );
  } finally {
    // The last reference this function holds. Anything the browser still has is
    // the input element, which the dialog has already destroyed.
    credential = "";
  }
}

/**
 * Report a failure without letting an unexpected exception's text out.
 *
 * The typed errors carry messages this repository wrote, which name
 * limits, folder ids and rules and never quote Actor data. Anything else is an
 * unexpected exception whose message could be a browser or driver string, so it
 * is reported as a category only.
 *
 * @param {unknown} error
 * @param {string} reassurance
 * @param {boolean} [retryPinned=false]
 */
function notifyFailure(error, reassurance, retryPinned = false) {
  const known =
    error instanceof BundleError ||
    error instanceof SourceError ||
    error instanceof TransportError ||
    error instanceof WorkflowError;
  ui.notifications.error(
    failureNotification({
      title: MODULE_TITLE,
      known,
      code: known ? error.code : undefined,
      message: known ? error.message : undefined,
      reassurance,
      retryPinned,
    })
  );
}
