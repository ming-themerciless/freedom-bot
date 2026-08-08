/**
 * Hashing and sending the validated bytes. Pure apart from `crypto` and `fetch`,
 * both of which are injected so the whole module is testable under `node --test`.
 *
 * ## One producer of bytes, three consumers
 *
 * `encodeBundle` produces a `Uint8Array`. It is hashed here, uploaded here, and
 * handed to the download fallback unchanged. Nothing re-encodes it on the way
 * out: a re-encoded document is a different artifact whatever it looks like, and
 * the checksum the operator reads on screen would then belong to bytes the
 * server never saw.
 *
 * ## Retries cannot create a second pending artifact
 *
 * The `Idempotency-Key` is derived from the checksum, so it is the same on
 * every attempt at the same export. The server binds that key to the bytes it
 * was first spent on: a retry returns the original receipt, and the same key
 * presented with different bytes is refused rather than answered. A network
 * failure after the server committed therefore resolves correctly on retry
 * instead of producing two artifacts.
 *
 * ## HTTPS is required
 *
 * Anything else is refused before a request is made, with one deliberate
 * exception for `http://127.0.0.1` and `http://localhost` so a maintainer can
 * rehearse against a loopback endpoint on the same host. That exception cannot
 * reach the network, which is what makes it safe to have.
 *
 * ## The credential is a parameter, never a lookup
 *
 * `submitSnapshot` takes the credential as an argument and never reads one from
 * `game.settings` or anywhere else. That was already true, and security review
 * S-B-1 is why it now matters: there is no stored credential to read. The
 * caller (`main.js`) obtains it from the operator for the duration of one
 * submission. Nothing here logs it, echoes it, or puts it anywhere but the
 * `Authorization` header of the one request it was given for.
 *
 * ## The request is cross-origin, and the server has to permit it
 *
 * These four headers are not CORS-safelisted, so the browser sends an
 * unauthenticated `OPTIONS` preflight first and will not send this POST unless
 * the server answers it. `adapters/http/cors.py` answers it for an allowlisted
 * origin only. Nothing changes on this side — `credentials: "omit"` stays,
 * because adding cookie authority to a bearer endpoint would widen who can
 * drive it — but a `network_failure` reported from a browser whose origin is
 * not on the server's allowlist is a *configuration* failure, and
 * `docs/operations/foundry-snapshot-submission.md` §5.4 says how to read it.
 */

export class TransportError extends Error {
  /**
   * @param {string} code
   * @param {string} message
   * @param {object} [options]
   * @param {"pre_dispatch"|"post_dispatch"} [options.stage="pre_dispatch"]
   * @param {number} [options.status]
   */
  constructor(code, message, { stage = "pre_dispatch", status } = {}) {
    super(message);
    this.name = "TransportError";
    this.code = code;
    this.stage = stage;
    this.status = status;
  }
}

/** How long a submission may take before it is abandoned. */
export const DEFAULT_TIMEOUT_MS = 120_000;

/**
 * SHA-256 of exactly these bytes, as lower-case hex.
 *
 * @param {Uint8Array} bytes
 * @param {Crypto} cryptoImpl
 * @returns {Promise<string>}
 */
export async function sha256Hex(bytes, cryptoImpl) {
  const digest = await cryptoImpl.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

/**
 * Refuse an endpoint that is not HTTPS, before anything is sent to it.
 *
 * @param {string} endpoint
 * @returns {URL}
 */
export function requireSecureEndpoint(endpoint) {
  let url;
  try {
    url = new URL(endpoint);
  } catch {
    throw new TransportError(
      "invalid_endpoint",
      "The configured submission endpoint is not a valid URL. Ask an operator " +
        "to correct the module setting.",
      { stage: "pre_dispatch" }
    );
  }
  const loopback = url.hostname === "127.0.0.1" || url.hostname === "localhost" || url.hostname === "[::1]";
  if (url.protocol !== "https:" && !(url.protocol === "http:" && loopback)) {
    throw new TransportError(
      "insecure_endpoint",
      "The submission endpoint must use HTTPS. A snapshot carries every " +
        "exported Actor's mechanics and is never sent in clear text.",
      { stage: "pre_dispatch" }
    );
  }
  return url;
}

/**
 * The idempotency key for one export. Derived, never random.
 *
 * A random key would make every retry a *new* submission, which is the one
 * thing the key exists to prevent.
 *
 * @param {string} checksum
 * @returns {string}
 */
export function idempotencyKeyFor(checksum) {
  return `foundry-module:${checksum}`;
}

/**
 * Submit the bytes. Resolves to the server's receipt, or throws a `TransportError`.
 *
 * @param {object} options
 * @param {Uint8Array} options.bytes
 * @param {string} options.checksum
 * @param {string} options.endpoint
 * @param {string} options.credential
 * @param {typeof fetch} options.fetchImpl
 * @param {number} [options.timeoutMs]
 * @returns {Promise<{status: number, receipt: object}>}
 */
export async function submitSnapshot({
  bytes,
  checksum,
  endpoint,
  credential,
  fetchImpl,
  timeoutMs = DEFAULT_TIMEOUT_MS,
}) {
  const url = requireSecureEndpoint(endpoint);
  if (typeof credential !== "string" || credential.trim() === "") {
    throw new TransportError(
      "missing_credential",
      "No submission credential was entered. Enter the one issued for this " +
        "world in the submission dialog; it is deliberately not stored in " +
        "Foundry, because a stored one would be readable by every user in the " +
        "world.",
      { stage: "pre_dispatch" }
    );
  }

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let response;
  try {
    response = await fetchImpl(url.toString(), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${credential.trim()}`,
        "Content-Type": "application/json",
        "Idempotency-Key": idempotencyKeyFor(checksum),
        "X-Snapshot-SHA256": checksum,
      },
      body: bytes,
      signal: controller.signal,
      // The credential is a bearer token in a header; no cookie should ever be
      // attached to this request, and no response cookie should be kept.
      credentials: "omit",
      cache: "no-store",
      redirect: "error",
    });
  } catch (error) {
    // The cause is deliberately not surfaced: a `fetch` failure message can
    // carry the resolved address and the TLS error detail, and neither belongs
    // in a Foundry notification.
    throw new TransportError(
      error?.name === "AbortError" ? "timeout" : "network_failure",
      error?.name === "AbortError"
        ? "The submission timed out. Nothing was confirmed. Submitting again " +
          "with the same export is safe: a retry cannot create a second " +
          "snapshot."
        : "The submission could not reach the Freedom Blades server. Nothing " +
          "was confirmed. Submitting the same export again is safe.",
      { stage: "post_dispatch" }
    );
  } finally {
    clearTimeout(timer);
  }

  let receipt;
  try {
    receipt = await response.json();
  } catch {
    throw new TransportError(
      "malformed_response",
      `The server answered ${response.status} with something that is not a ` +
        "receipt. Ask an operator to check the service log.",
      { stage: "post_dispatch", status: response.status }
    );
  }

  if (!response.ok) {
    const code = receipt?.error?.code ?? "submission_refused";
    throw new TransportError(
      code,
      "The Freedom Blades server refused the submission. Ask an operator to " +
        "check the service log using the error code shown here.",
      {
        stage: "post_dispatch",
        status: response.status,
      }
    );
  }
  return { status: response.status, receipt };
}
