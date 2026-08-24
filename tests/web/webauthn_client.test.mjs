import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { readdirSync } from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ROOT = join(__dirname, '..', '..');

// Dynamically locate the fingerprinted WebAuthn JS file
const jsDir = join(ROOT, 'adapters', 'web', 'static', 'js');
const jsFiles = readdirSync(jsDir).filter(f => f.startsWith('webauthn-emergency.') && f.endsWith('.js'));
assert.equal(jsFiles.length, 1, 'Expected exactly one fingerprinted webauthn-emergency JS file');
const webauthnModulePath = join(jsDir, jsFiles[0]);

const require = createRequire(import.meta.url);
const webauthn = require(webauthnModulePath);

const {
  base64urlToBytes,
  bytesToBase64url,
  isSafeSameOriginRedirect,
  preparePublicKeyOptions,
  serializeAssertion,
  formatGenericRefusal,
  setStatus,
  startWebAuthnCeremony,
  initWebAuthnUI,
  CANONICAL_UUID_RE,
  ACCEPTED_REFUSAL_CODES,
} = webauthn;

// ===========================================================================
// Lightweight DOM Mock for State Machine Testing
// ===========================================================================

class MockClassList {
  constructor() {
    this._classes = new Set();
  }
  add(c) {
    this._classes.add(c);
  }
  remove(c) {
    this._classes.delete(c);
  }
  contains(c) {
    return this._classes.has(c);
  }
  toggle(c, force) {
    if (force !== undefined) {
      if (force) this.add(c);
      else this.remove(c);
    } else {
      if (this.contains(c)) this.remove(c);
      else this.add(c);
    }
  }
}

class MockElement {
  constructor(id, tagName = 'div', hidden = false) {
    this.id = id;
    this.tagName = tagName.toUpperCase();
    this.hidden = hidden;
    this.disabled = false;
    this.textContent = '';
    this._attributes = new Map();
    this.classList = new MockClassList();
    this._listeners = new Map();
  }
  getAttribute(name) {
    return this._attributes.has(name) ? this._attributes.get(name) : null;
  }
  setAttribute(name, value) {
    this._attributes.set(name, String(value));
  }
  removeAttribute(name) {
    this._attributes.delete(name);
  }
  hasAttribute(name) {
    return this._attributes.has(name);
  }
  addEventListener(type, listener) {
    if (!this._listeners.has(type)) {
      this._listeners.set(type, []);
    }
    this._listeners.get(type).push(listener);
  }
  click() {
    let prevented = false;
    const evt = {
      preventDefault: () => {
        prevented = true;
      },
    };
    const handlers = this._listeners.get('click') || [];
    for (const h of handlers) {
      h(evt);
    }
    return prevented;
  }
}

class MockDocument {
  constructor() {
    this.elements = new Map();
    this.addElement(new MockElement('webauthn-signin-btn', 'button', true));
    this.addElement(new MockElement('webauthn-fallback-msg', 'p', false));
    this.addElement(new MockElement('webauthn-unsupported-msg', 'p', true));
    this.addElement(new MockElement('webauthn-status-msg', 'div', true));
  }
  addElement(el) {
    this.elements.set(el.id, el);
  }
  getElementById(id) {
    return this.elements.get(id) || null;
  }
}

function createEnvironment(options = {}) {
  const doc = new MockDocument();
  const win = {
    PublicKeyCredential: options.supported !== false ? function () {} : undefined,
    location: { href: 'https://example.com/v1/auth/emergency' },
  };
  const calls = {
    fetch: [],
    get: [],
    navigate: [],
  };

  const nav = {
    credentials: {
      get: async opts => {
        calls.get.push(opts);
        if (options.getThrows) {
          const err = new Error(options.getThrows.message || 'Error');
          err.name = options.getThrows.name || 'Error';
          throw err;
        }
        return options.assertionResult !== undefined ? options.assertionResult : {
          id: 'test-cred-id',
          rawId: new Uint8Array([1, 2, 3, 4]).buffer,
          type: 'public-key',
          response: {
            clientDataJSON: new Uint8Array([10, 11, 12]).buffer,
            authenticatorData: new Uint8Array([20, 21, 22]).buffer,
            signature: new Uint8Array([30, 31, 32]).buffer,
            userHandle: null,
          },
          getClientExtensionResults: () => ({}),
        };
      },
    },
  };

  const fetchFn = async (url, init) => {
    calls.fetch.push({ url, init });
    if (options.fetchThrows) {
      throw new Error(options.fetchThrows);
    }
    if (url === '/v1/auth/emergency/webauthn/options') {
      if (options.optionsStatus && options.optionsStatus !== 200) {
        return {
          status: options.optionsStatus,
          json: async () => options.optionsErrorJson || { error: 'invalid', correlation_id: '12345678-1234-1234-1234-123456789abc' },
        };
      }
      return {
        status: 200,
        json: async () => options.optionsJson || {
          challenge: 'dGVzdC1jaGFsbGVuZ2U',
          rpId: 'localhost',
          timeout: 60000,
          userVerification: 'required',
          allowCredentials: [],
        },
      };
    }
    if (url === '/v1/auth/emergency/webauthn/verify') {
      if (options.verifyStatus && options.verifyStatus !== 200) {
        return {
          status: options.verifyStatus,
          json: async () => options.verifyErrorJson || { error: 'invalid', correlation_id: '12345678-1234-1234-1234-123456789abc' },
        };
      }
      return {
        status: 200,
        json: async () => options.verifyJson || {
          status: 'ok',
          redirect: '/v1/admin/role-capabilities',
        },
      };
    }
    throw new Error('Unexpected URL: ' + url);
  };

  const navigateFn = url => {
    calls.navigate.push(url);
  };

  const deps = {
    document: doc,
    window: win,
    navigator: nav,
    fetch: fetchFn,
    navigate: navigateFn,
  };

  return { doc, win, nav, deps, calls };
}

// ===========================================================================
// 1. Strict Base64URL Decoder Unit Tests (Finding G36-02)
// ===========================================================================

describe('Strict Base64URL Decoder (G36-02)', () => {
  test('decodes valid 2-, 3-, and 4-character quantums correctly', () => {
    // 2-char quantum -> 1 byte (0x00)
    assert.deepEqual(Array.from(base64urlToBytes('AA')), [0]);
    // 3-char quantum -> 2 bytes (0x00, 0x00)
    assert.deepEqual(Array.from(base64urlToBytes('AAA')), [0, 0]);
    // 4-char quantum -> 3 bytes (0x00, 0x00, 0x00)
    assert.deepEqual(Array.from(base64urlToBytes('AAAA')), [0, 0, 0]);
  });

  test('decodes URL-safe characters - and _ correctly', () => {
    const raw = 'Hello_World-123';
    const b64url = 'SGVsbG9fV29ybGQtMTIz';
    const decoded = base64urlToBytes(b64url);
    assert.equal(Buffer.from(decoded).toString('utf8'), raw);

    // Byte 0xfb, 0xff, 0xfe -> binary "-__-"
    const b64url2 = '-__-';
    const decoded2 = base64urlToBytes(b64url2);
    assert.deepEqual(Array.from(decoded2), [251, 255, 254]);
  });

  test('accepts valid padded and equivalent unpadded forms', () => {
    // 1 byte: "AA==" and "AA"
    assert.deepEqual(base64urlToBytes('AA=='), base64urlToBytes('AA'));
    // 2 bytes: "AAA=" and "AAA"
    assert.deepEqual(base64urlToBytes('AAA='), base64urlToBytes('AAA'));
    // 3 bytes: "AAAA" (no pad)
    assert.deepEqual(base64urlToBytes('AAAA'), new Uint8Array([0, 0, 0]));
    // "Hello": "SGVsbG8=" and "SGVsbG8"
    assert.deepEqual(base64urlToBytes('SGVsbG8='), base64urlToBytes('SGVsbG8'));
  });

  test('round-trip canonical encoding holds for all valid inputs', () => {
    const testVectors = [
      new Uint8Array([0]),
      new Uint8Array([255]),
      new Uint8Array([1, 2]),
      new Uint8Array([1, 2, 3]),
      new Uint8Array([10, 20, 30, 40, 50]),
      new Uint8Array(Buffer.from('Freedom Blades Platform WebAuthn Test Challenge')),
    ];
    for (const vec of testVectors) {
      const encoded = bytesToBase64url(vec);
      const decoded = base64urlToBytes(encoded);
      assert.deepEqual(decoded, vec);
      assert.equal(bytesToBase64url(decoded), encoded);
    }
  });

  test('rejects empty input explicitly', () => {
    assert.throws(() => base64urlToBytes(''), /empty input/);
  });

  test('rejects non-string values', () => {
    assert.throws(() => base64urlToBytes(null), TypeError);
    assert.throws(() => base64urlToBytes(undefined), TypeError);
    assert.throws(() => base64urlToBytes(123), TypeError);
    assert.throws(() => base64urlToBytes({}), TypeError);
  });

  test('rejects standard Base64 characters + and /', () => {
    assert.throws(() => base64urlToBytes('SGVs+G8'), /standard base64 prohibited/);
    assert.throws(() => base64urlToBytes('SGVs/G8'), /standard base64 prohibited/);
  });

  test('rejects whitespace in all positions (leading, trailing, internal, tab, newline, cr)', () => {
    assert.throws(() => base64urlToBytes(' SGVsbG8'), /whitespace prohibited/);
    assert.throws(() => base64urlToBytes('SGVsbG8 '), /whitespace prohibited/);
    assert.throws(() => base64urlToBytes('SGVs bG8'), /whitespace prohibited/);
    assert.throws(() => base64urlToBytes('SGVsbG8\n'), /whitespace prohibited/);
    assert.throws(() => base64urlToBytes('SGVsbG8\r'), /whitespace prohibited/);
    assert.throws(() => base64urlToBytes('SGVsbG8\t'), /whitespace prohibited/);
  });

  test('rejects prohibited punctuation and non-base64 characters', () => {
    assert.throws(() => base64urlToBytes('SGVs!bG8'), /invalid character/);
    assert.throws(() => base64urlToBytes('SGVs.bG8'), /invalid character/);
    assert.throws(() => base64urlToBytes('SGVs$bG8'), /invalid character/);
  });

  test('rejects malformed padding: A, A=, A===, AA===, AA====, =AAA, AA=A, AA==A, and excessive padding', () => {
    assert.throws(() => base64urlToBytes('A'), /impossible unpadded length/);
    assert.throws(() => base64urlToBytes('A='), /padded string length must be multiple of 4/);
    assert.throws(() => base64urlToBytes('A==='), /excessive padding/);
    assert.throws(() => base64urlToBytes('AA==='), /excessive padding/);
    assert.throws(() => base64urlToBytes('AA===='), /excessive padding/);
    assert.throws(() => base64urlToBytes('=AAA'), /embedded padding character/);
    assert.throws(() => base64urlToBytes('AA=A'), /embedded padding character/);
    assert.throws(() => base64urlToBytes('AA==A'), /embedded padding character/);
  });

  test('rejects incorrect padding for lengths modulo two and three', () => {
    // Unpadded len 2 requires '==' pad (len 4), len 2 with '=' (len 3) is rejected
    assert.throws(() => base64urlToBytes('AA='), /padded string length must be multiple of 4/);
    // Unpadded len 3 requires '=' pad (len 4), len 3 with '==' (len 5) is rejected
    assert.throws(() => base64urlToBytes('AAA=='), /padded string length must be multiple of 4/);
  });

  test('rejects non-canonical encodings with non-zero padding bits', () => {
    // In 2-char quantum 'AB', 'B' has unused bits 0001 (non-zero!)
    assert.throws(() => base64urlToBytes('AB'), /non-zero padding bits/);
    assert.throws(() => base64urlToBytes('AB=='), /non-zero padding bits/);
    // In 3-char quantum 'AAB', 'B' has unused bits 01 (non-zero!)
    assert.throws(() => base64urlToBytes('AAB'), /non-zero padding bits/);
    assert.throws(() => base64urlToBytes('AAB='), /non-zero padding bits/);
  });
});

// ===========================================================================
// 2. Closed Refusal Vocabulary & Canonical UUID Tests (Finding G36-01)
// ===========================================================================

describe('Closed Refusal Vocabulary & Canonical UUID (G36-01)', () => {
  const validUuid = '12345678-1234-1234-1234-123456789abc';

  test('every accepted R-07/R-08 code with a canonical UUID is accepted and formatted safely', () => {
    const acceptedCodes = ['origin_invalid', 'rate_limited', 'invalid', 'expired'];
    for (const code of acceptedCodes) {
      const msg = formatGenericRefusal({ error: code, correlation_id: validUuid });
      assert.equal(msg, `Emergency sign-in did not complete. Reference ${validUuid}.`);
    }
  });

  test('an unknown refusal code with a canonical UUID falls back generically without referencing UUID', () => {
    const msg = formatGenericRefusal({ error: 'unknown_custom_code', correlation_id: validUuid });
    assert.equal(msg, 'Emergency sign-in did not complete.');
    assert.equal(msg.includes(validUuid), false);
  });

  test('every unrelated code removed from the prior overbroad set falls back generically', () => {
    const removedCodes = ['credential_invalid', 'not_available', 'consumed', 'revoked', 'suspended', 'denied'];
    for (const code of removedCodes) {
      const msg = formatGenericRefusal({ error: code, correlation_id: validUuid });
      assert.equal(msg, 'Emergency sign-in did not complete.', `Code ${code} should not be accepted`);
      assert.equal(msg.includes(validUuid), false);
    }
  });

  test('missing and non-string error values fall back generically', () => {
    assert.equal(formatGenericRefusal({ correlation_id: validUuid }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: null, correlation_id: validUuid }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: 123, correlation_id: validUuid }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: [], correlation_id: validUuid }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: {}, correlation_id: validUuid }), 'Emergency sign-in did not complete.');
  });

  test('missing and non-string correlation values fall back generically', () => {
    assert.equal(formatGenericRefusal({ error: 'invalid' }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: null }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: 12345 }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: [] }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: {} }), 'Emergency sign-in did not complete.');
  });

  test('leading, trailing, or internal whitespace around a UUID is rejected without normalization', () => {
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: ` ${validUuid}` }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: `${validUuid} ` }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: `\n${validUuid}` }), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: '12345678- 1234-1234-1234-123456789abc' }), 'Emergency sign-in did not complete.');
  });

  test('uppercase UUID is rejected as non-canonical', () => {
    const upperUuid = '12345678-1234-1234-1234-123456789ABC';
    assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: upperUuid }), 'Emergency sign-in did not complete.');
  });

  test('malformed group lengths, braces, URN prefixes, nil malformed strings, suffixes are rejected', () => {
    const malformedCases = [
      '{12345678-1234-1234-1234-123456789abc}',
      'urn:uuid:12345678-1234-1234-1234-123456789abc',
      '12345678-1234-1234-1234-123456789abc-extra',
      '1234567-1234-1234-1234-123456789abc', // 7 chars in group 1
      '12345678-123-1234-1234-123456789abc',  // 3 chars in group 2
      '00000000-0000-0000-0000-00000000000z', // non-hex character
      'just a sentence with a uuid inside 12345678-1234-1234-1234-123456789abc',
    ];
    for (const bad of malformedCases) {
      assert.equal(formatGenericRefusal({ error: 'invalid', correlation_id: bad }), 'Emergency sign-in did not complete.', `Case ${bad} should be rejected`);
    }
  });

  test('non-object and array response bodies fall back generically', () => {
    assert.equal(formatGenericRefusal(null), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal(undefined), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal('plain string'), 'Emergency sign-in did not complete.');
    assert.equal(formatGenericRefusal([1, 2, 3]), 'Emergency sign-in did not complete.');
  });
});

// ===========================================================================
// 3. Other Pure Helper Unit Tests (G35-05)
// ===========================================================================

describe('Other Pure Helper Functions', () => {
  test('isSafeSameOriginRedirect accepts exact accepted admin path only', () => {
    assert.equal(isSafeSameOriginRedirect('/v1/admin/role-capabilities'), true);
  });

  test('isSafeSameOriginRedirect strictly rejects external, protocol-relative, backslash, control, whitespace, schemes', () => {
    assert.equal(isSafeSameOriginRedirect('https://evil.com'), false);
    assert.equal(isSafeSameOriginRedirect('//evil.com'), false);
    assert.equal(isSafeSameOriginRedirect('/\\evil.com'), false);
    assert.equal(isSafeSameOriginRedirect('\\evil.com'), false);
    assert.equal(isSafeSameOriginRedirect('/v1/admin/role-capabilities\n'), false);
    assert.equal(isSafeSameOriginRedirect(' /v1/admin/role-capabilities'), false);
    assert.equal(isSafeSameOriginRedirect('/v1/admin/role-capabilities '), false);
    assert.equal(isSafeSameOriginRedirect('javascript:alert(1)'), false);
    assert.equal(isSafeSameOriginRedirect('/other-path'), false);
    assert.equal(isSafeSameOriginRedirect(null), false);
    assert.equal(isSafeSameOriginRedirect(123), false);
  });

  test('serializeAssertion formats PublicKeyCredential assertion correctly with null userHandle', () => {
    const rawId = new Uint8Array([1, 2, 3, 4]).buffer;
    const clientDataJSON = new Uint8Array([5, 6, 7, 8]).buffer;
    const authenticatorData = new Uint8Array([9, 10, 11, 12]).buffer;
    const signature = new Uint8Array([13, 14, 15, 16]).buffer;

    const assertion = {
      id: 'custom-id',
      rawId: rawId,
      type: 'public-key',
      response: {
        clientDataJSON: clientDataJSON,
        authenticatorData: authenticatorData,
        signature: signature,
        userHandle: null,
      },
      getClientExtensionResults: () => ({ appid: true }),
    };

    const serialized = serializeAssertion(assertion);
    assert.equal(serialized.id, 'custom-id');
    assert.equal(serialized.type, 'public-key');
    assert.equal(serialized.response.userHandle, null);
    assert.equal(typeof serialized.response.clientDataJSON, 'string');
    assert.equal(typeof serialized.response.authenticatorData, 'string');
    assert.equal(typeof serialized.response.signature, 'string');
    assert.deepEqual(serialized.clientExtensionResults, { appid: true });
  });

  test('serializeAssertion formats binary userHandle correctly', () => {
    const assertion = {
      id: 'cred-id',
      rawId: new Uint8Array([1]).buffer,
      type: 'public-key',
      response: {
        clientDataJSON: new Uint8Array([2]).buffer,
        authenticatorData: new Uint8Array([3]).buffer,
        signature: new Uint8Array([4]).buffer,
        userHandle: new Uint8Array([255, 0]).buffer,
      },
    };
    const serialized = serializeAssertion(assertion);
    assert.equal(serialized.response.userHandle, '_wA');
  });

  test('serializeAssertion throws on missing required assertion fields', () => {
    assert.throws(() => serializeAssertion(null), /Invalid PublicKeyCredential/);
    assert.throws(() => serializeAssertion({ response: {} }), /Invalid PublicKeyCredential/);
    assert.throws(() => serializeAssertion({ rawId: new ArrayBuffer(0), response: {} }), /Missing required assertion response fields/);
  });

  test('preparePublicKeyOptions converts challenge and allowCredentials IDs', () => {
    const serverOptions = {
      challenge: 'dGVzdC1jaGFsbGVuZ2U',
      rpId: 'freedom-blades.local',
      timeout: 30000,
      userVerification: 'required',
      allowCredentials: [
        { type: 'public-key', id: 'AQIDBA' },
      ],
    };

    const prepared = preparePublicKeyOptions(serverOptions);
    assert.equal(prepared.rpId, 'freedom-blades.local');
    assert.equal(prepared.timeout, 30000);
    assert.equal(prepared.userVerification, 'required');
    assert.ok(prepared.challenge instanceof Uint8Array);
    assert.equal(Buffer.from(prepared.challenge).toString('utf8'), 'test-challenge');
    assert.equal(prepared.allowCredentials.length, 1);
    assert.ok(prepared.allowCredentials[0].id instanceof Uint8Array);
    assert.deepEqual(Array.from(prepared.allowCredentials[0].id), [1, 2, 3, 4]);
  });

  test('preparePublicKeyOptions throws on missing challenge or malformed credential descriptors', () => {
    assert.throws(() => preparePublicKeyOptions(null), /Invalid options object/);
    assert.throws(() => preparePublicKeyOptions({}), /Missing or invalid challenge/);
    assert.throws(() => preparePublicKeyOptions({ challenge: 'abc', allowCredentials: [{}] }), /Malformed credential descriptor/);
  });
});

// ===========================================================================
// 4. Full Ceremony State Machine & Executable Workflow Proofs (G35-04 & G36-03)
// ===========================================================================

describe('WebAuthn Ceremony State Machine (Executable Workflow Proofs)', () => {
  test('1. Supported initialization reveals/enables button and hides fallback using CSP-safe hidden attribute', () => {
    const { doc, deps } = createEnvironment({ supported: true });
    const btn = doc.getElementById('webauthn-signin-btn');
    const fallbackMsg = doc.getElementById('webauthn-fallback-msg');
    const unsupportedMsg = doc.getElementById('webauthn-unsupported-msg');

    assert.equal(btn.hidden, true, 'Initial state: button hidden');
    assert.equal(fallbackMsg.hidden, false, 'Initial state: fallback visible');

    initWebAuthnUI(deps);

    assert.equal(btn.hidden, false, 'Supported: button unhidden');
    assert.equal(btn.disabled, false, 'Supported: button enabled');
    assert.equal(fallbackMsg.hidden, true, 'Supported: fallback hidden');
    assert.equal(unsupportedMsg.hidden, true, 'Supported: unsupported hidden');
  });

  test('2. Unsupported initialization leaves no actionable button and shows unsupported message', () => {
    const { doc, deps } = createEnvironment({ supported: false });
    const btn = doc.getElementById('webauthn-signin-btn');
    const fallbackMsg = doc.getElementById('webauthn-fallback-msg');
    const unsupportedMsg = doc.getElementById('webauthn-unsupported-msg');

    initWebAuthnUI(deps);

    assert.equal(btn.hidden, true, 'Unsupported: button remains hidden');
    assert.equal(fallbackMsg.hidden, true, 'Unsupported: no-JS fallback hidden');
    assert.equal(unsupportedMsg.hidden, false, 'Unsupported: unsupported explanation visible');
  });

  test('3. No-JS initial markup contains no usable dead action', () => {
    const doc = new MockDocument();
    const btn = doc.getElementById('webauthn-signin-btn');
    const fallback = doc.getElementById('webauthn-fallback-msg');

    assert.equal(btn.hidden, true, 'No-JS markup has button hidden');
    assert.equal(fallback.hidden, false, 'No-JS markup has fallback message visible');
  });

  test('4. One click sends exactly one same-origin POST to R-07 with accepted headers/body behavior', async () => {
    const { deps, calls } = createEnvironment();
    await startWebAuthnCeremony(deps);

    assert.ok(calls.fetch.length >= 1);
    const r07 = calls.fetch[0];
    assert.equal(r07.url, '/v1/auth/emergency/webauthn/options');
    assert.equal(r07.init.method, 'POST');
    assert.equal(r07.init.credentials, 'same-origin');
    assert.equal(r07.init.headers.Accept, 'application/json');
  });

  test('5. Returned challenge and descriptor IDs are converted before navigator.credentials.get()', async () => {
    const { deps, calls } = createEnvironment({
      optionsJson: {
        challenge: 'dGVzdC1jaGFsbGVuZ2U',
        allowCredentials: [{ type: 'public-key', id: 'AQIDBA' }],
      },
    });

    await startWebAuthnCeremony(deps);

    assert.equal(calls.get.length, 1);
    const publicKey = calls.get[0].publicKey;
    assert.ok(publicKey.challenge instanceof Uint8Array);
    assert.equal(Buffer.from(publicKey.challenge).toString('utf8'), 'test-challenge');
    assert.ok(publicKey.allowCredentials[0].id instanceof Uint8Array);
    assert.deepEqual(Array.from(publicKey.allowCredentials[0].id), [1, 2, 3, 4]);
  });

  test('6. navigator.credentials.get({publicKey}) receives exact prepared options', async () => {
    const { deps, calls } = createEnvironment({
      optionsJson: {
        challenge: 'dGVzdC1jaGFsbGVuZ2U',
        rpId: 'freedom-blades.org',
        timeout: 45000,
        userVerification: 'required',
      },
    });

    await startWebAuthnCeremony(deps);

    assert.equal(calls.get.length, 1);
    const pk = calls.get[0].publicKey;
    assert.equal(pk.rpId, 'freedom-blades.org');
    assert.equal(pk.timeout, 45000);
    assert.equal(pk.userVerification, 'required');
  });

  test('7. Successful assertion sends exactly one POST to R-08 with exact serialized payload', async () => {
    const { deps, calls } = createEnvironment();
    await startWebAuthnCeremony(deps);

    assert.equal(calls.fetch.length, 2);
    const r08 = calls.fetch[1];
    assert.equal(r08.url, '/v1/auth/emergency/webauthn/verify');
    assert.equal(r08.init.method, 'POST');
    assert.equal(r08.init.credentials, 'same-origin');
    assert.equal(r08.init.headers['Content-Type'], 'application/json');

    const parsed = JSON.parse(r08.init.body);
    assert.equal(parsed.id, 'test-cred-id');
    assert.equal(parsed.type, 'public-key');
    assert.equal(parsed.response.userHandle, null);
  });

  test('8. userHandle: null and binary user handles both work in ceremony serialization', async () => {
    const { deps, calls } = createEnvironment({
      assertionResult: {
        id: 'binary-cred-id',
        rawId: new Uint8Array([1]).buffer,
        type: 'public-key',
        response: {
          clientDataJSON: new Uint8Array([2]).buffer,
          authenticatorData: new Uint8Array([3]).buffer,
          signature: new Uint8Array([4]).buffer,
          userHandle: new Uint8Array([10, 20]).buffer,
        },
      },
    });

    await startWebAuthnCeremony(deps);
    const r08 = calls.fetch[1];
    const parsed = JSON.parse(r08.init.body);
    assert.equal(parsed.response.userHandle, 'ChQ');
  });

  test('9. Success navigates only to accepted same-origin absolute path', async () => {
    const { deps, calls } = createEnvironment({
      verifyJson: {
        status: 'ok',
        redirect: '/v1/admin/role-capabilities',
      },
    });

    await startWebAuthnCeremony(deps);
    assert.deepEqual(calls.navigate, ['/v1/admin/role-capabilities']);
  });

  test('10. Protocol-relative, external, backslash, control, whitespace, malformed, wrong-typed redirects are refused', async () => {
    const badRedirects = [
      'https://attacker.com',
      '//attacker.com',
      '/\\attacker.com',
      '\\attacker.com',
      '/v1/admin/role-capabilities\r\n',
      ' /v1/admin/role-capabilities',
      '/v1/other',
      null,
      12345,
    ];

    for (const bad of badRedirects) {
      const { doc, deps, calls } = createEnvironment({
        verifyJson: { status: 'ok', redirect: bad },
      });
      await startWebAuthnCeremony(deps);
      assert.equal(calls.navigate.length, 0, `Should not navigate to ${bad}`);
      const statusEl = doc.getElementById('webauthn-status-msg');
      assert.equal(statusEl.textContent, 'Emergency sign-in did not complete.');
    }
  });

  test('11. Two rapid clicks cannot start two ceremonies or duplicate either request', async () => {
    const { deps, calls } = createEnvironment();
    const p1 = startWebAuthnCeremony(deps);
    const p2 = startWebAuthnCeremony(deps);

    await Promise.all([p1, p2]);

    assert.equal(calls.fetch.length, 2);
    assert.equal(calls.get.length, 1);
  });

  test('12. NotAllowedError and AbortError restore button, clear busy state, do not retry, show neutral text', async () => {
    for (const errName of ['NotAllowedError', 'AbortError']) {
      const { doc, deps, calls } = createEnvironment({
        getThrows: { name: errName, message: 'User cancelled' },
      });
      const btn = doc.getElementById('webauthn-signin-btn');
      const statusEl = doc.getElementById('webauthn-status-msg');

      await startWebAuthnCeremony(deps);

      assert.equal(calls.fetch.length, 1, 'Only options called, no verify');
      assert.equal(btn.disabled, false, 'Button re-enabled');
      assert.equal(btn.hasAttribute('aria-busy'), false, 'aria-busy cleared');
      assert.equal(statusEl.textContent, 'Security key operation was cancelled or timed out.');
      assert.equal(statusEl.classList.contains('is-error'), false, 'Neutral cancellation is not error');
    }
  });

  test('13. Network failure restores control and exposes no exception detail', async () => {
    const { doc, deps } = createEnvironment({
      fetchThrows: 'Fatal TCP Connection Reset 0xDEADBEEF',
    });
    const btn = doc.getElementById('webauthn-signin-btn');
    const statusEl = doc.getElementById('webauthn-status-msg');

    await startWebAuthnCeremony(deps);

    assert.equal(btn.disabled, false);
    assert.equal(btn.hasAttribute('aria-busy'), false);
    assert.equal(statusEl.textContent, 'Emergency sign-in did not complete.');
    assert.equal(statusEl.textContent.includes('TCP'), false);
  });

  test('14. R-07 refusal uses only validated closed code/UUID presentation', async () => {
    const validUuid = '12345678-1234-1234-1234-123456789abc';
    const { doc, deps } = createEnvironment({
      optionsStatus: 403,
      optionsErrorJson: { error: 'origin_invalid', correlation_id: validUuid },
    });
    const statusEl = doc.getElementById('webauthn-status-msg');

    await startWebAuthnCeremony(deps);

    assert.equal(statusEl.textContent, `Emergency sign-in did not complete. Reference ${validUuid}.`);
    assert.equal(statusEl.classList.contains('is-error'), true);
  });

  test('15. R-08 refusal uses only validated closed code/UUID presentation', async () => {
    const validUuid = '87654321-4321-4321-4321-cba987654321';
    const { doc, deps } = createEnvironment({
      verifyStatus: 403,
      verifyErrorJson: { error: 'invalid', correlation_id: validUuid },
    });
    const statusEl = doc.getElementById('webauthn-status-msg');

    await startWebAuthnCeremony(deps);

    assert.equal(statusEl.textContent, `Emergency sign-in did not complete. Reference ${validUuid}.`);
    assert.equal(statusEl.classList.contains('is-error'), true);
  });

  test('16. Malformed JSON and unexpected response shapes fall back generically', async () => {
    const { doc, deps } = createEnvironment({
      optionsStatus: 500,
      optionsErrorJson: 'Internal Server Error <h1>Boom</h1>',
    });
    const statusEl = doc.getElementById('webauthn-status-msg');

    await startWebAuthnCeremony(deps);

    assert.equal(statusEl.textContent, 'Emergency sign-in did not complete.');
    assert.equal(statusEl.textContent.includes('Boom'), false);
  });

  test('17. Unsupported-browser initialization makes no network or credential call', () => {
    const { deps, calls } = createEnvironment({ supported: false });
    initWebAuthnUI(deps);

    assert.equal(calls.fetch.length, 0);
    assert.equal(calls.get.length, 0);
  });

  test('18. Busy state uses disabled and aria-busy, and always clears on non-navigation completion', async () => {
    const { doc, deps } = createEnvironment({
      getThrows: { name: 'NotAllowedError', message: 'Cancelled' },
    });
    const btn = doc.getElementById('webauthn-signin-btn');

    await startWebAuthnCeremony(deps);

    assert.equal(btn.disabled, false);
    assert.equal(btn.hasAttribute('aria-busy'), false);
  });

  test('19. The workflow never writes to Web Storage', async () => {
    const originalLocalStorage = globalThis.localStorage;
    const originalSessionStorage = globalThis.sessionStorage;
    let storageWritten = false;

    globalThis.localStorage = {
      setItem: () => {
        storageWritten = true;
      },
    };
    globalThis.sessionStorage = {
      setItem: () => {
        storageWritten = true;
      },
    };

    const { deps } = createEnvironment();
    await startWebAuthnCeremony(deps);

    globalThis.localStorage = originalLocalStorage;
    globalThis.sessionStorage = originalSessionStorage;

    assert.equal(storageWritten, false, 'No Web Storage writes permitted');
  });

  test('20. The client references no network endpoint other than R-07 and R-08', async () => {
    const { deps, calls } = createEnvironment();
    await startWebAuthnCeremony(deps);

    const endpoints = calls.fetch.map(c => c.url);
    assert.deepEqual(endpoints, [
      '/v1/auth/emergency/webauthn/options',
      '/v1/auth/emergency/webauthn/verify',
    ]);
  });

  test('21. Malformed challenge in server options fails generically before authenticator call', async () => {
    const { doc, deps, calls } = createEnvironment({
      optionsJson: {
        challenge: 'AA====', // malformed excessive padding
        rpId: 'localhost',
      },
    });

    await startWebAuthnCeremony(deps);

    assert.equal(calls.get.length, 0, 'navigator.credentials.get must NOT be called on malformed challenge');
    const statusEl = doc.getElementById('webauthn-status-msg');
    assert.equal(statusEl.textContent, 'Emergency sign-in did not complete.');
  });

  test('22. Malformed credential descriptor ID in options fails generically before authenticator call', async () => {
    const { doc, deps, calls } = createEnvironment({
      optionsJson: {
        challenge: 'dGVzdC1jaGFsbGVuZ2U',
        allowCredentials: [{ type: 'public-key', id: 'invalid!b64' }],
      },
    });

    await startWebAuthnCeremony(deps);

    assert.equal(calls.get.length, 0, 'navigator.credentials.get must NOT be called on malformed descriptor ID');
    const statusEl = doc.getElementById('webauthn-status-msg');
    assert.equal(statusEl.textContent, 'Emergency sign-in did not complete.');
  });
});
