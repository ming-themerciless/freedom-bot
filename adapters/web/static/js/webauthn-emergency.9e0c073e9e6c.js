/**
 * Freedom Blades — Emergency Break-Glass WebAuthn Client (F-15)
 *
 * Implements browser-side ceremony for Server Administrator emergency access:
 * 1. Requests assertion options from POST /v1/auth/emergency/webauthn/options
 * 2. Prepares binary challenge/credentials and invokes navigator.credentials.get()
 * 3. Serializes assertion response into standard Base64URL JSON
 * 4. Submits payload to POST /v1/auth/emergency/webauthn/verify
 * 5. Validates same-origin redirect and navigates on success
 * 6. Handles cancellations, generic error formatting, and correlation IDs securely
 *
 * Invariants:
 * - Zero inline scripts, zero eval, zero external dependencies.
 * - Zero inline styles, zero inline style mutation (uses [hidden] and CSS classes).
 * - Progressive enhancement: no-JS view renders no dead button; JS unhides on support.
 * - VM-04 non-enumeration: never leaks account or credential existence.
 * - Closed refusal vocabulary & strict UUID format validation for correlation IDs.
 */

(function (root, factory) {
  if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.FreedomBladesWebAuthn = factory();
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  var CANONICAL_UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

  var ACCEPTED_REFUSAL_CODES = {
    'origin_invalid': true,
    'rate_limited': true,
    'invalid': true,
    'expired': true
  };

  var B64_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
  var CHAR_MAP = {};
  for (var idx = 0; idx < B64_CHARS.length; idx++) {
    CHAR_MAP[B64_CHARS.charAt(idx)] = idx;
  }

  /**
   * Strict RFC 4648 §5 Base64URL decoder.
   * Validates alphabet, length, padding structure, and canonical bit alignment.
   */
  function base64urlToBytes(b64url) {
    if (typeof b64url !== 'string') {
      throw new TypeError('Expected string for base64url decoding');
    }
    if (b64url.length === 0) {
      throw new Error('Invalid base64url string: empty input');
    }
    if (/[\s]/.test(b64url)) {
      throw new Error('Invalid base64url string: whitespace prohibited');
    }
    if (b64url.indexOf('+') !== -1 || b64url.indexOf('/') !== -1) {
      throw new Error('Invalid base64url string: standard base64 prohibited');
    }
    if (!/^[A-Za-z0-9\-_=]+$/.test(b64url)) {
      throw new Error('Invalid base64url string: invalid character');
    }

    var padIndex = b64url.indexOf('=');
    var padCount = 0;
    if (padIndex !== -1) {
      for (var i = padIndex; i < b64url.length; i++) {
        if (b64url.charAt(i) !== '=') {
          throw new Error('Invalid base64url string: embedded padding character');
        }
        padCount++;
      }
      if (padCount > 2) {
        throw new Error('Invalid base64url string: excessive padding');
      }
      if (b64url.length % 4 !== 0) {
        throw new Error('Invalid base64url string: padded string length must be multiple of 4');
      }
      if (padCount === 1 && (b64url.length - 1) % 4 !== 3) {
        throw new Error('Invalid base64url string: invalid single padding position');
      }
      if (padCount === 2 && (b64url.length - 2) % 4 !== 2) {
        throw new Error('Invalid base64url string: invalid double padding position');
      }
    }

    var unpadded = b64url.substring(0, b64url.length - padCount);
    var unpaddedMod = unpadded.length % 4;
    if (unpaddedMod === 1) {
      throw new Error('Invalid base64url string: impossible unpadded length');
    }

    var byteCount = Math.floor((unpadded.length * 6) / 8);
    var bytes = new Uint8Array(byteCount);
    var byteIdx = 0;
    var quantum = 0;
    var bits = 0;

    for (var k = 0; k < unpadded.length; k++) {
      var charVal = CHAR_MAP[unpadded.charAt(k)];
      if (charVal === undefined) {
        throw new Error('Invalid base64url character');
      }
      quantum = (quantum << 6) | charVal;
      bits += 6;
      if (bits >= 8) {
        bits -= 8;
        bytes[byteIdx++] = (quantum >>> bits) & 0xff;
      }
    }

    if (bits > 0) {
      var unusedMask = (1 << bits) - 1;
      if ((quantum & unusedMask) !== 0) {
        throw new Error('Invalid base64url string: non-zero padding bits');
      }
    }

    return bytes;
  }

  /**
   * Pure unpadded Base64URL encoder (RFC 4648 §5).
   */
  function bytesToBase64url(bufferOrView) {
    if (!bufferOrView) {
      throw new TypeError('Expected ArrayBuffer or TypedArray for base64url encoding');
    }

    var bytes;
    if (bufferOrView instanceof Uint8Array) {
      bytes = bufferOrView;
    } else if (bufferOrView instanceof ArrayBuffer) {
      bytes = new Uint8Array(bufferOrView);
    } else if (ArrayBuffer.isView(bufferOrView)) {
      bytes = new Uint8Array(bufferOrView.buffer, bufferOrView.byteOffset, bufferOrView.byteLength);
    } else {
      throw new TypeError('Expected ArrayBuffer or TypedArray for base64url encoding');
    }

    var result = '';
    var len = bytes.length;
    var i = 0;

    for (; i + 2 < len; i += 3) {
      var n = (bytes[i] << 16) | (bytes[i + 1] << 8) | bytes[i + 2];
      result +=
        B64_CHARS.charAt((n >>> 18) & 63) +
        B64_CHARS.charAt((n >>> 12) & 63) +
        B64_CHARS.charAt((n >>> 6) & 63) +
        B64_CHARS.charAt(n & 63);
    }

    if (i < len) {
      if (len - i === 1) {
        var n1 = bytes[i] << 16;
        result +=
          B64_CHARS.charAt((n1 >>> 18) & 63) +
          B64_CHARS.charAt((n1 >>> 12) & 63);
      } else if (len - i === 2) {
        var n2 = (bytes[i] << 16) | (bytes[i + 1] << 8);
        result +=
          B64_CHARS.charAt((n2 >>> 18) & 63) +
          B64_CHARS.charAt((n2 >>> 12) & 63) +
          B64_CHARS.charAt((n2 >>> 6) & 63);
      }
    }

    return result;
  }

  /**
   * Strict validator for safe same-origin redirects.
   * Rejects protocol-relative //, schemes, whitespace, control characters, backslashes.
   */
  function isSafeSameOriginRedirect(url) {
    if (typeof url !== 'string' || !url) {
      return false;
    }
    if (url.trim() !== url) {
      return false;
    }
    if (url.length > 2048) {
      return false;
    }
    if (!url.startsWith('/')) {
      return false;
    }
    if (url.startsWith('//') || url.startsWith('/\\')) {
      return false;
    }
    if (/[\\\x00-\x1f\x7f]/.test(url)) {
      return false;
    }
    if (url.indexOf(':') !== -1) {
      return false;
    }
    return url === '/v1/admin/role-capabilities';
  }

  /**
   * Prepares server options JSON for navigator.credentials.get({ publicKey }).
   */
  function preparePublicKeyOptions(serverOptions) {
    if (!serverOptions || typeof serverOptions !== 'object') {
      throw new Error('Invalid options object from server');
    }
    if (!serverOptions.challenge || typeof serverOptions.challenge !== 'string') {
      throw new Error('Missing or invalid challenge in options');
    }

    var publicKey = {
      challenge: base64urlToBytes(serverOptions.challenge)
    };

    if (serverOptions.rpId && typeof serverOptions.rpId === 'string') {
      publicKey.rpId = serverOptions.rpId;
    }
    if (typeof serverOptions.timeout === 'number') {
      publicKey.timeout = serverOptions.timeout;
    }
    if (serverOptions.userVerification && typeof serverOptions.userVerification === 'string') {
      publicKey.userVerification = serverOptions.userVerification;
    }

    if (Array.isArray(serverOptions.allowCredentials)) {
      publicKey.allowCredentials = serverOptions.allowCredentials.map(function (cred) {
        if (!cred || !cred.id || typeof cred.id !== 'string') {
          throw new Error('Malformed credential descriptor in allowCredentials');
        }
        return {
          type: cred.type || 'public-key',
          id: base64urlToBytes(cred.id),
          transports: Array.isArray(cred.transports) ? cred.transports : undefined
        };
      });
    }

    return publicKey;
  }

  /**
   * Serializes a PublicKeyCredential assertion into standard Base64URL JSON.
   */
  function serializeAssertion(assertion) {
    if (!assertion || !assertion.rawId || !assertion.response) {
      throw new Error('Invalid PublicKeyCredential assertion structure');
    }
    var res = assertion.response;
    if (!res.clientDataJSON || !res.authenticatorData || !res.signature) {
      throw new Error('Missing required assertion response fields');
    }

    var userHandleB64 = null;
    if (res.userHandle) {
      userHandleB64 = bytesToBase64url(res.userHandle);
    }

    var extensions = {};
    if (typeof assertion.getClientExtensionResults === 'function') {
      try {
        extensions = assertion.getClientExtensionResults() || {};
      } catch (e) {
        extensions = {};
      }
    }

    return {
      id: assertion.id || bytesToBase64url(assertion.rawId),
      rawId: bytesToBase64url(assertion.rawId),
      type: assertion.type || 'public-key',
      response: {
        clientDataJSON: bytesToBase64url(res.clientDataJSON),
        authenticatorData: bytesToBase64url(res.authenticatorData),
        signature: bytesToBase64url(res.signature),
        userHandle: userHandleB64
      },
      clientExtensionResults: extensions
    };
  }

  /**
   * Formats safe refusal presentation with validated closed code and UUID.
   * G36-01: strictly checks non-array object, error in ACCEPTED_REFUSAL_CODES,
   * and correlation_id matching canonical UUID format without normalization.
   */
  function formatGenericRefusal(data) {
    var base = 'Emergency sign-in did not complete.';
    if (
      !data ||
      typeof data !== 'object' ||
      Array.isArray(data) ||
      typeof data.error !== 'string' ||
      !Object.prototype.hasOwnProperty.call(ACCEPTED_REFUSAL_CODES, data.error) ||
      typeof data.correlation_id !== 'string' ||
      !CANONICAL_UUID_RE.test(data.correlation_id)
    ) {
      return base;
    }
    return base + ' Reference ' + data.correlation_id + '.';
  }

  /**
   * Sets text content and status class without inline style mutation.
   */
  function setStatus(doc, message, isError) {
    var el = doc.getElementById('webauthn-status-msg');
    if (!el) return;
    if (!message) {
      el.textContent = '';
      el.hidden = true;
      if (el.classList) {
        el.classList.remove('is-error', 'is-info');
      }
      return;
    }
    el.textContent = message;
    if (el.classList) {
      el.classList.remove('is-error', 'is-info');
      el.classList.add(isError ? 'is-error' : 'is-info');
    }
    el.hidden = false;
  }

  var isCeremonyBusy = false;

  /**
   * Drives the complete WebAuthn ceremony state machine.
   */
  async function startWebAuthnCeremony(deps) {
    var d = deps || {};
    var doc = d.document || (typeof document !== 'undefined' ? document : null);
    var win = d.window || (typeof window !== 'undefined' ? window : null);
    var nav = d.navigator || (typeof navigator !== 'undefined' ? navigator : null);
    var fetchFn = d.fetch || (typeof fetch === 'function' ? fetch : null);
    var navigateFn = d.navigate || function (url) {
      if (win && win.location) {
        win.location.href = url;
      }
    };

    if (!doc || !fetchFn || !nav || !nav.credentials || typeof nav.credentials.get !== 'function') {
      return;
    }

    if (isCeremonyBusy) {
      return;
    }

    var btn = doc.getElementById('webauthn-signin-btn');
    isCeremonyBusy = true;
    if (btn) {
      btn.disabled = true;
      btn.setAttribute('aria-busy', 'true');
    }
    setStatus(doc, '', false);

    var navigated = false;

    try {
      var optionsRes = await fetchFn('/v1/auth/emergency/webauthn/options', {
        method: 'POST',
        headers: {
          'Accept': 'application/json'
        },
        credentials: 'same-origin'
      });

      if (!optionsRes || optionsRes.status !== 200) {
        var errData = null;
        try {
          errData = await optionsRes.json();
        } catch (e) {
          errData = null;
        }
        setStatus(doc, formatGenericRefusal(errData), true);
        return;
      }

      var serverOptions = await optionsRes.json();
      var publicKeyOptions = preparePublicKeyOptions(serverOptions);

      var assertion = await nav.credentials.get({ publicKey: publicKeyOptions });
      if (!assertion) {
        setStatus(doc, 'Emergency sign-in did not complete.', true);
        return;
      }

      var payload = serializeAssertion(assertion);

      var verifyRes = await fetchFn('/v1/auth/emergency/webauthn/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'same-origin',
        body: JSON.stringify(payload)
      });

      if (!verifyRes || verifyRes.status !== 200) {
        var verifyErr = null;
        try {
          verifyErr = await verifyRes.json();
        } catch (e) {
          verifyErr = null;
        }
        setStatus(doc, formatGenericRefusal(verifyErr), true);
        return;
      }

      var verifyData = await verifyRes.json();
      if (verifyData && verifyData.status === 'ok' && isSafeSameOriginRedirect(verifyData.redirect)) {
        navigated = true;
        navigateFn(verifyData.redirect);
        return;
      }

      setStatus(doc, 'Emergency sign-in did not complete.', true);
    } catch (err) {
      if (err && (err.name === 'NotAllowedError' || err.name === 'AbortError')) {
        setStatus(doc, 'Security key operation was cancelled or timed out.', false);
      } else {
        setStatus(doc, 'Emergency sign-in did not complete.', true);
      }
    } finally {
      isCeremonyBusy = false;
      if (!navigated && btn) {
        btn.disabled = false;
        btn.removeAttribute('aria-busy');
      }
    }
  }

  /**
   * Initializes the emergency access WebAuthn UI progressively.
   */
  function initWebAuthnUI(deps) {
    var d = deps || {};
    var doc = d.document || (typeof document !== 'undefined' ? document : null);
    var win = d.window || (typeof window !== 'undefined' ? window : null);
    var nav = d.navigator || (typeof navigator !== 'undefined' ? navigator : null);
    if (!doc) return;

    var btn = doc.getElementById('webauthn-signin-btn');
    var fallbackMsg = doc.getElementById('webauthn-fallback-msg');
    var unsupportedMsg = doc.getElementById('webauthn-unsupported-msg');

    if (!btn) return;

    var isSupported = !!(
      win &&
      win.PublicKeyCredential &&
      nav &&
      nav.credentials &&
      typeof nav.credentials.get === 'function'
    );

    if (isSupported) {
      if (fallbackMsg) fallbackMsg.hidden = true;
      if (unsupportedMsg) unsupportedMsg.hidden = true;
      btn.hidden = false;
      btn.disabled = false;
      btn.removeAttribute('aria-busy');
      btn.addEventListener('click', function (e) {
        if (e && typeof e.preventDefault === 'function') {
          e.preventDefault();
        }
        startWebAuthnCeremony(deps);
      });
    } else {
      btn.hidden = true;
      if (fallbackMsg) fallbackMsg.hidden = true;
      if (unsupportedMsg) unsupportedMsg.hidden = false;
    }
  }

  // Auto-initialize when loaded in browser DOM
  if (typeof document !== 'undefined' && typeof window !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        initWebAuthnUI();
      });
    } else {
      initWebAuthnUI();
    }
  }

  return {
    base64urlToBytes: base64urlToBytes,
    bytesToBase64url: bytesToBase64url,
    isSafeSameOriginRedirect: isSafeSameOriginRedirect,
    preparePublicKeyOptions: preparePublicKeyOptions,
    serializeAssertion: serializeAssertion,
    formatGenericRefusal: formatGenericRefusal,
    setStatus: setStatus,
    startWebAuthnCeremony: startWebAuthnCeremony,
    initWebAuthnUI: initWebAuthnUI,
    CANONICAL_UUID_RE: CANONICAL_UUID_RE,
    ACCEPTED_REFUSAL_CODES: ACCEPTED_REFUSAL_CODES
  };
});
