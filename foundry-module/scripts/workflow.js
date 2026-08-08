/**
 * The submission workflow, with every dependency injected.
 *
 * `main.js` supplies the real `game`, `crypto` and `fetch` and renders the
 * result; this module decides what happens and in what order. That split is
 * what makes the order testable, and the order is the part with safety
 * properties in it:
 *
 * 1. **the deployment tuple is checked first** — before a single Actor is read,
 *    so an unsupported Foundry or system version never causes every active
 *    character's mechanics to be assembled in memory;
 * 2. **the whole artifact is built and validated before anything leaves** — a
 *    bundle that the Manager would refuse is refused here, in front of the
 *    operator, with nothing sent;
 * 3. **the checksum is taken over the exact bytes** that are then uploaded or
 *    downloaded, from the one encoder that produced them;
 * 4. **only then is the network touched.**
 *
 * ## What this never does
 *
 * No Foundry document is created, updated or deleted. No compendium is read or
 * written. No filesystem or world-storage path is opened. The only write of any
 * kind in the whole module is the browser download in the fallback path, which
 * writes to the operator's own machine.
 */

import { BundleError, assertSupportedDeployment, buildBundle, encodeBundle, folderPath } from "./bundle.js";
import { SourceError, readActors, readFolders, readWorld } from "./world-source.js";
import { TransportError, sha256Hex, submitSnapshot } from "./transport.js";

/**
 * Bounded single-entry prepared snapshot state machine.
 * Explicitly instantiated and owned by the caller (e.g. main.js entry point).
 */
export class PreparedSnapshotState {
  constructor() {
    this._entry = null;
    this._preparationSequence = 0;
    this._operation = null;
    this._activeOperations = new Set();
  }

  get generation() {
    return this._preparationSequence;
  }

  get operation() {
    return this._operation;
  }

  get status() {
    return this._entry ? this._entry.status : "empty";
  }

  get pinnedPrepared() {
    return this._entry?.status === "unconfirmed-retry-pinned"
      ? this._entry.prepared
      : null;
  }

  hasPinnedRetry() {
    return this._entry?.status === "unconfirmed-retry-pinned";
  }

  isReusable(folderId, contentFingerprint) {
    return (
      this._entry?.status === "confirmed-reusable" &&
      this._entry.folderId === folderId &&
      this._entry.contentFingerprint === contentFingerprint
    );
  }

  getReusablePrepared(folderId, contentFingerprint) {
    if (this.isReusable(folderId, contentFingerprint)) {
      return this._entry.prepared;
    }
    return null;
  }

  nextGeneration() {
    this._preparationSequence += 1;
    return this._preparationSequence;
  }

  startOperation() {
    // A fresh identity cannot wrap around and become equal to an ancient
    // in-flight operation. Only the current Symbol is retained, so this stays
    // constant-space without a counter or operation history.
    const token = Symbol("prepared-snapshot-operation");
    this._operation = token;
    this._activeOperations.add(token);
    return token;
  }

  /** Begin a standalone preparation without invalidating a live workflow. */
  startStandaloneOperation() {
    if (this._activeOperations.size > 0) return null;
    const token = Symbol("prepared-snapshot-operation");
    this._operation = token;
    return token;
  }

  finishOperation(operationToken) {
    if (operationToken) this._activeOperations.delete(operationToken);
  }

  setConfirmed(folderId, contentFingerprint, prepared, operationToken) {
    if (operationToken !== this._operation) {
      return false;
    }
    this._entry = {
      status: "confirmed-reusable",
      folderId,
      contentFingerprint,
      prepared,
    };
    return true;
  }

  setPinnedRetry(folderId, contentFingerprint, prepared, operationToken) {
    if (operationToken !== this._operation) {
      return false;
    }
    this._entry = {
      status: "unconfirmed-retry-pinned",
      folderId,
      contentFingerprint,
      prepared,
    };
    return true;
  }

  clear(operationToken) {
    if (operationToken !== this._operation) {
      return false;
    }
    this._entry = null;
    return true;
  }
}

/** The complete, immutable failure-policy vocabulary. */
export const FailureDisposition = Object.freeze({
  LOCAL_REFUSAL: "local_refusal",
  DEFINITIVE_REFUSAL: "definitive_refusal",
  RETRY_SAME_KEY: "retry_same_key",
  DELIVERY_INDETERMINATE: "delivery_indeterminate",
});

/**
 * Classify a failure from bounded transport facts, never caller-supplied
 * disposition metadata.
 *
 * @param {unknown} error
 * @returns {"local_refusal"|"definitive_refusal"|"retry_same_key"|"delivery_indeterminate"}
 */
export function classifyFailureDisposition(error) {
  if (
    error instanceof BundleError ||
    error instanceof SourceError ||
    error instanceof WorkflowError
  ) {
    return FailureDisposition.LOCAL_REFUSAL;
  }
  if (error instanceof TransportError) {
    if (
      error.code === "timeout" ||
      error.code === "network_failure" ||
      error.code === "malformed_response"
    ) {
      return FailureDisposition.DELIVERY_INDETERMINATE;
    }
    if (
      error.code === "missing_credential" ||
      error.code === "invalid_endpoint" ||
      error.code === "insecure_endpoint"
    ) {
      return FailureDisposition.LOCAL_REFUSAL;
    }
    if (typeof error.status === "number") {
      if (
        error.status >= 500 || error.code === "concurrent_submission"
      ) {
        return FailureDisposition.RETRY_SAME_KEY;
      }
      if (error.status >= 400 && error.status < 500) {
        return FailureDisposition.DEFINITIVE_REFUSAL;
      }
      return FailureDisposition.DELIVERY_INDETERMINATE;
    }
    if (error.stage === "post_dispatch") {
      return FailureDisposition.DELIVERY_INDETERMINATE;
    }
    return FailureDisposition.LOCAL_REFUSAL;
  }
  if (error?.stage === "post_dispatch") {
    return FailureDisposition.DELIVERY_INDETERMINATE;
  }
  return FailureDisposition.LOCAL_REFUSAL;
}

/**
 * Build and validate the artifact for one selected folder, without sending it.
 *
 * Returned separately from the submission so the UI can show the operator the
 * checksum, the Actor count and the byte size of the exact document that is
 * about to be sent — and so the download fallback can offer those same bytes.
 *
 * Reuses the exact previously prepared snapshot (including its exportedAt
 * timestamp, bytes, and SHA-256 checksum) if exportable data in the selected
 * folder is unchanged. If exportable content changes or a different folder is
 * selected, a new snapshot is prepared with a fresh RFC 3339 timestamp.
 *
 * @param {object} options
 * @param {object} options.game
 * @param {Crypto} options.crypto
 * @param {string} options.folderId
 * @param {string} options.exporterVersion
 * @param {object} options.supported
 * @param {PreparedSnapshotState} [options.state]
 * @param {() => Date} [options.now]
 * @param {boolean} [options.forceFresh]
 * @param {boolean} [options.discardPinned]
 * @param {symbol|null} [options.operationToken]
 * @returns {Promise<{bytes: Uint8Array, checksum: string, actorCount: number, folderPath: string, world: object, exportedAt: string, folderId: string, contentFingerprint: string, generation: number}>}
 */
export async function prepareSnapshot({
  game,
  crypto,
  folderId,
  exporterVersion,
  supported,
  state = null,
  now = () => new Date(),
  forceFresh = false,
  discardPinned = false,
  operationToken = null,
}) {
  // Standalone preparations and coordinated workflows use the same operation
  // authority. Starting before validation means an explicit discard remains
  // authoritative even if fresh preparation later fails.
  const standaloneOperation = state && !operationToken
    ? state.startStandaloneOperation()
    : null;
  const activeOperation = state
    ? operationToken ?? standaloneOperation
    : null;

  if (discardPinned && state) {
    state.clear(activeOperation);
  }

  // A pinned delivery can only be abandoned by the operator's explicit
  // discard. In particular, downloading it (or a caller asking for a fresh
  // preparation without discard authority) must not silently replace it.
  if (state && state.hasPinnedRetry()) {
    return state.pinnedPrepared;
  }

  const world = readWorld(game);
  assertSupportedDeployment(world, supported);

  const folders = readFolders(game);
  const actors = readActors(game, folderId);

  // Compute canonical content fingerprint over exportable data payload (excluding exportedAt)
  const fingerprintBundle = buildBundle({
    exporterVersion,
    exportedAt: "",
    world,
    selectedFolderId: folderId,
    folders,
    actors,
  });
  const fingerprintBytes = encodeBundle(fingerprintBundle);
  const contentFingerprint = await sha256Hex(fingerprintBytes, crypto);

  if (!forceFresh && state) {
    const reusable = state.getReusablePrepared(folderId, contentFingerprint);
    if (reusable) {
      return reusable;
    }
  }

  const generation = state ? state.nextGeneration() : 0;
  const exportedAt = `${now().toISOString().slice(0, 19)}Z`;
  const bundle = buildBundle({
    exporterVersion,
    exportedAt,
    world,
    selectedFolderId: folderId,
    folders,
    actors,
  });

  const bytes = encodeBundle(bundle);
  const checksum = await sha256Hex(bytes, crypto);
  const prepared = {
    bytes,
    checksum,
    actorCount: actors.length,
    folderPath: folderPath(folderId, folders),
    world,
    exportedAt,
    folderId,
    contentFingerprint,
    generation,
  };

  if (state && activeOperation) {
    state.setConfirmed(folderId, contentFingerprint, prepared, activeOperation);
  }

  if (standaloneOperation) state.finishOperation(standaloneOperation);

  return prepared;
}

export class WorkflowError extends Error {
  /**
   * @param {string} code    A stable classification an operator can act on.
   * @param {string} message A sentence explaining the refusal.
   */
  constructor(code, message) {
    super(message);
    this.name = "WorkflowError";
    this.code = code;
  }
}

/**
 * Pure dependency-injected workflow dispatcher.
 * Routes the single prepared snapshot instance to either download or submission
 * without re-encoding, cloning, or preparing a second time.
 *
 * @param {object} options
 * @param {object} options.prepared  The result of `prepareSnapshot`.
 * @param {"download"|"submit"|string} options.action
 * @param {(prepared: object) => Promise<any>|any} options.downloadPrepared
 * @param {(prepared: object) => Promise<any>|any} options.submitPrepared
 * @returns {Promise<any>}
 */
export async function dispatchWorkflow({
  prepared,
  action,
  downloadPrepared,
  submitPrepared,
}) {
  if (!prepared || !(prepared.bytes instanceof Uint8Array)) {
    throw new WorkflowError(
      "invalid_prepared_snapshot",
      "A valid prepared snapshot is required."
    );
  }
  if (action === "download") {
    return downloadPrepared(prepared);
  }
  if (action === "submit") {
    return submitPrepared(prepared);
  }
  throw new WorkflowError(
    "unsupported_action",
    "The requested workflow action is unsupported. Action must be 'download' or 'submit'."
  );
}

/**
 * Prepare and submit, returning the server's receipt.
 *
 * @param {object} options
 * @param {object} options.prepared  The result of `prepareSnapshot`.
 * @param {string} options.endpoint
 * @param {string} options.credential
 * @param {typeof fetch} options.fetchImpl
 * @param {number} [options.timeoutMs]
 * @returns {Promise<{status: number, receipt: object}>}
 */
export async function sendSnapshot({
  prepared,
  endpoint,
  credential,
  fetchImpl,
  timeoutMs,
}) {
  return submitSnapshot({
    bytes: prepared.bytes,
    checksum: prepared.checksum,
    endpoint,
    credential,
    fetchImpl,
    timeoutMs,
  });
}

/**
 * Dependency-injected workflow coordinator.
 * Executes prepare, dispatch, failure classification, and state transitions.
 *
 * @param {object} options
 * @param {object} options.game
 * @param {Crypto} options.crypto
 * @param {string} options.folderId
 * @param {string} options.exporterVersion
 * @param {object} options.supported
 * @param {PreparedSnapshotState} [options.state]
 * @param {"download"|"submit"} options.action
 * @param {string} [options.endpoint]
 * @param {string} [options.credential]
 * @param {typeof fetch} [options.fetchImpl]
 * @param {() => Date} [options.now]
 * @param {boolean} [options.forceFresh]
 * @param {boolean} [options.discardPinned]
 * @param {(prepared: object) => Promise<any>|any} [options.downloadPrepared]
 * @returns {Promise<{prepared: object, result?: any, status?: number, receipt?: object}>}
 */
export async function executeWorkflow({
  game,
  crypto,
  folderId,
  exporterVersion,
  supported,
  state = null,
  action,
  endpoint,
  credential,
  fetchImpl,
  now = () => new Date(),
  forceFresh = false,
  discardPinned = false,
  downloadPrepared,
}) {
  const opToken = state ? state.startOperation() : null;

  try {
    const prepared = await prepareSnapshot({
    game,
    crypto,
    folderId,
    exporterVersion,
    supported,
    state,
    now,
    forceFresh,
    discardPinned,
    operationToken: opToken,
    });

  if (action === "download") {
    let result;
    if (typeof downloadPrepared === "function") {
      result = await downloadPrepared(prepared);
    }
    // Downloading an unconfirmed payload is observational: it must remain
    // pinned until a retry confirms it or the operator explicitly discards it.
    if (state && state.pinnedPrepared !== prepared) {
      state.setConfirmed(
        prepared.folderId,
        prepared.contentFingerprint,
        prepared,
        opToken
      );
    }
    return { prepared, result };
  }

  if (action === "submit") {
    try {
      const { status, receipt } = await sendSnapshot({
        prepared,
        endpoint,
        credential,
        fetchImpl,
      });
      if (state) {
        state.setConfirmed(
          prepared.folderId,
          prepared.contentFingerprint,
          prepared,
          opToken
        );
      }
      return { prepared, status, receipt };
    } catch (error) {
      const disposition = classifyFailureDisposition(error);
      if (state) {
        if (
          disposition === FailureDisposition.RETRY_SAME_KEY ||
          disposition === FailureDisposition.DELIVERY_INDETERMINATE
        ) {
          state.setPinnedRetry(
            prepared.folderId,
            prepared.contentFingerprint,
            prepared,
            opToken
          );
        } else {
          state.clear(opToken);
        }
      }
    throw error;
    }
  }

  throw new WorkflowError(
    "unsupported_action",
    "The requested workflow action is unsupported. Action must be 'download' or 'submit'."
  );
  } finally {
    if (state) state.finishOperation(opToken);
  }
}

/**
 * The bounded receipt line shown to the operator.
 *
 * Deliberately built from the *server's* receipt rather than from what was
 * sent: the point of showing it is that the two ends agree, and echoing the
 * client's own numbers back would prove nothing. Actor names, mechanics, item
 * lists and raw JSON never appear.
 *
 * @param {object} receipt
 * @param {string} localChecksum
 * @returns {string}
 */
export function describeReceipt(receipt, localChecksum) {
  const agreed = receipt?.checksum === localChecksum;
  const state = receipt?.duplicate
    ? "already held (no second snapshot was created)"
    : "recorded as pending";
  const short = String(receipt?.checksum ?? "").slice(0, 12);
  return (
    `Snapshot ${state}. ${receipt?.actor_count ?? "?"} Actor(s), ` +
    `checksum ${short}…, ` +
    `${agreed ? "server and client checksums match" : "CHECKSUM DISAGREEMENT — tell an operator"}. ` +
    "A Guild Council member must review and apply it; nothing has been applied yet."
  );
}
