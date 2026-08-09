/** Pure construction of bounded operator-facing failure notifications. */

const RELOAD_WARNING =
  " Do not reload or close this page while delivery is unconfirmed: " +
  "the exact retry state exists only for this page load.";

/**
 * @param {object} options
 * @param {string} options.title
 * @param {boolean} options.known
 * @param {string} [options.code]
 * @param {string} [options.message]
 * @param {string} options.reassurance
 * @param {boolean} options.retryPinned
 */
export function failureNotification({
  title,
  known,
  code,
  message,
  reassurance,
  retryPinned,
}) {
  const base = known
    ? `${title} [${code}]: ${message}`
    : `${title}: the snapshot could not be completed. ${reassurance}`;
  return base + (retryPinned ? RELOAD_WARNING : "");
}
