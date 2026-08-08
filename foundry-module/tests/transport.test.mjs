import test from "node:test";
import assert from "node:assert/strict";

import {
  TransportError,
  idempotencyKeyFor,
  requireSecureEndpoint,
  sha256Hex,
  submitSnapshot,
} from "../scripts/transport.js";
import { fakeFetch, nodeCrypto } from "./fixtures.mjs";

const BYTES = new TextEncoder().encode('{"a":1}\n');
const CREDENTIAL = "principal.0123456789012345678901234567890123456789";

test("the checksum is the SHA-256 of exactly the bytes given", async () => {
  const checksum = await sha256Hex(BYTES, nodeCrypto);
  // Independently derived: Node's own crypto over the same bytes.
  const { createHash } = await import("node:crypto");
  assert.equal(checksum, createHash("sha256").update(BYTES).digest("hex"));
});

test("a plain-HTTP endpoint is refused before anything is sent", () => {
  assert.throws(
    () => requireSecureEndpoint("http://freedom.example/api/v1/foundry/snapshots"),
    (error) => error instanceof TransportError && error.code === "insecure_endpoint"
  );
});

test("loopback HTTP is permitted, for a same-host rehearsal only", () => {
  assert.doesNotThrow(() => requireSecureEndpoint("http://127.0.0.1:8757/api/v1/foundry/snapshots"));
  assert.doesNotThrow(() => requireSecureEndpoint("http://localhost:8757/api/v1/foundry/snapshots"));
});

test("a malformed endpoint is refused", () => {
  assert.throws(
    () => requireSecureEndpoint("not a url"),
    (error) => error.code === "invalid_endpoint"
  );
});

test("the idempotency key is derived from the checksum, so a retry is a retry", () => {
  assert.equal(idempotencyKeyFor("abc"), idempotencyKeyFor("abc"));
  assert.notEqual(idempotencyKeyFor("abc"), idempotencyKeyFor("abd"));
});

test("a submission sends the exact bytes, the claimed digest and the derived key", async () => {
  const checksum = await sha256Hex(BYTES, nodeCrypto);
  const fetchImpl = fakeFetch({ status: "pending", checksum, actor_count: 2 });
  const { status, receipt } = await submitSnapshot({
    bytes: BYTES,
    checksum,
    endpoint: "https://freedom.example/api/v1/foundry/snapshots",
    credential: CREDENTIAL,
    fetchImpl,
  });

  assert.equal(status, 201);
  assert.equal(receipt.checksum, checksum);
  const [call] = fetchImpl.calls;
  assert.equal(call.init.method, "POST");
  assert.equal(call.init.body, BYTES);
  assert.equal(call.init.headers["X-Snapshot-SHA256"], checksum);
  assert.equal(call.init.headers["Idempotency-Key"], idempotencyKeyFor(checksum));
  assert.equal(call.init.headers.Authorization, `Bearer ${CREDENTIAL}`);
  assert.equal(call.init.headers["Content-Type"], "application/json");
  assert.equal(call.init.credentials, "omit");
  assert.equal(call.init.redirect, "error");
});

test("a missing credential is refused without a request being made", async () => {
  const fetchImpl = fakeFetch({});
  await assert.rejects(
    submitSnapshot({
      bytes: BYTES,
      checksum: "x",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: "   ",
      fetchImpl,
    }),
    (error) => error instanceof TransportError && error.code === "missing_credential"
  );
  assert.equal(fetchImpl.calls.length, 0);
});

test("a refusal surfaces its code but never the server-controlled message", async () => {
  const fetchImpl = fakeFetch(
    { error: { code: "unsupported_deployment", message: "SERVER CONTROLLED SECRET" } },
    400
  );
  await assert.rejects(
    submitSnapshot({
      bytes: BYTES,
      checksum: "x",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: CREDENTIAL,
      fetchImpl,
    }),
    (error) => {
      assert.equal(error.code, "unsupported_deployment");
      assert.equal(error.message.includes("SERVER CONTROLLED SECRET"), false);
      assert.match(error.message, /server refused the submission/i);
      return true;
    }
  );
});

test("a network failure is reported without leaking the underlying error text", async () => {
  const fetchImpl = async () => {
    throw new Error("connect ECONNREFUSED 203.0.113.7:443");
  };
  await assert.rejects(
    submitSnapshot({
      bytes: BYTES,
      checksum: "x",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: CREDENTIAL,
      fetchImpl,
    }),
    (error) => {
      assert.equal(error.code, "network_failure");
      assert.equal(error.message.includes("203.0.113.7"), false);
      assert.equal(error.message.includes("ECONNREFUSED"), false);
      assert.match(error.message, /again is safe/);
      return true;
    }
  );
});

test("a timeout aborts, and says a retry cannot create a second snapshot", async () => {
  const fetchImpl = (url, init) =>
    new Promise((resolve, reject) => {
      init.signal.addEventListener("abort", () => {
        const error = new Error("aborted");
        error.name = "AbortError";
        reject(error);
      });
    });
  await assert.rejects(
    submitSnapshot({
      bytes: BYTES,
      checksum: "x",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: CREDENTIAL,
      fetchImpl,
      timeoutMs: 5,
    }),
    (error) => {
      assert.equal(error.code, "timeout");
      assert.match(error.message, /cannot create a second snapshot/);
      return true;
    }
  );
});

test("a non-JSON response is reported as malformed rather than parsed loosely", async () => {
  const fetchImpl = async () => ({
    ok: false,
    status: 502,
    json: async () => {
      throw new Error("not json");
    },
  });
  await assert.rejects(
    submitSnapshot({
      bytes: BYTES,
      checksum: "x",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: CREDENTIAL,
      fetchImpl,
    }),
    (error) => error.code === "malformed_response"
  );
});
