import test from "node:test";
import assert from "node:assert/strict";

import { BundleError } from "../scripts/bundle.js";
import { SourceError } from "../scripts/world-source.js";
import { TransportError, sha256Hex } from "../scripts/transport.js";
import {
  FailureDisposition,
  PreparedSnapshotState,
  WorkflowError,
  classifyFailureDisposition,
  describeReceipt,
  dispatchWorkflow,
  executeWorkflow,
  prepareSnapshot,
  sendSnapshot,
} from "../scripts/workflow.js";
import {
  ACTIVE_FOLDER_ID,
  FIRST_ACTOR_ID,
  INACTIVE_FOLDER_ID,
  SECOND_ACTOR_ID,
  SUPPORTED,
  fakeFetch,
  fakeGame,
  nodeCrypto,
} from "./fixtures.mjs";

const prepare = (
  game = fakeGame(),
  folderId = ACTIVE_FOLDER_ID,
  now = () => new Date("2026-08-04T09:15:00.123Z"),
  state = null,
  forceFresh = false,
  discardPinned = false
) =>
  prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
    forceFresh,
    discardPinned,
  });

test("a prepared snapshot describes the exact document it built", async () => {
  const prepared = await prepare();
  assert.equal(prepared.actorCount, 2);
  assert.equal(prepared.folderPath, "/actors/Characters/Characters (active)");
  assert.equal(prepared.checksum, await sha256Hex(prepared.bytes, nodeCrypto));

  const parsed = JSON.parse(new TextDecoder().decode(prepared.bytes));
  assert.equal(parsed.exportedAt, "2026-08-04T09:15:00Z");
  assert.deepEqual(
    parsed.actors.map((actor) => actor.id).sort(),
    [FIRST_ACTOR_ID, SECOND_ACTOR_ID].sort()
  );
});

test("dispatchWorkflow routes to downloadPrepared with strictEqual prepared object identity", async () => {
  const prepared = await prepare();
  let receivedObj = null;
  let submitCount = 0;

  const result = await dispatchWorkflow({
    prepared,
    action: "download",
    downloadPrepared: (p) => {
      receivedObj = p;
      return "downloaded";
    },
    submitPrepared: () => {
      submitCount++;
    },
  });

  assert.equal(result, "downloaded");
  assert.strictEqual(receivedObj, prepared);
  assert.equal(submitCount, 0);
});

test("dispatchWorkflow routes to submitPrepared with strictEqual prepared object identity", async () => {
  const prepared = await prepare();
  let receivedObj = null;
  let downloadCount = 0;

  const result = await dispatchWorkflow({
    prepared,
    action: "submit",
    downloadPrepared: () => {
      downloadCount++;
    },
    submitPrepared: (p) => {
      receivedObj = p;
      return "submitted";
    },
  });

  assert.equal(result, "submitted");
  assert.strictEqual(receivedObj, prepared);
  assert.equal(downloadCount, 0);
});

test("caller extra properties cannot replace or override top-level prepared snapshot", async () => {
  const genuinePrepared = await prepare();
  const fakeReplacement = { bytes: new Uint8Array([1, 2, 3]), checksum: "fake" };
  let receivedObj = null;

  await dispatchWorkflow({
    prepared: genuinePrepared,
    action: "submit",
    downloadPrepared: () => {},
    submitPrepared: (p) => {
      receivedObj = p;
    },
    submitOptions: { prepared: fakeReplacement },
    extraParam: { prepared: fakeReplacement },
  });

  assert.strictEqual(receivedObj, genuinePrepared);
  assert.notStrictEqual(receivedObj, fakeReplacement);
});

test("dispatchWorkflow refuses unsupported action with fixed-prose WorkflowError without echoing action input", async () => {
  const prepared = await prepare();
  const secretActionInput = "secret-token-action-123";
  let downloadCount = 0;
  let submitCount = 0;

  await assert.rejects(
    dispatchWorkflow({
      prepared,
      action: secretActionInput,
      downloadPrepared: () => {
        downloadCount++;
      },
      submitPrepared: () => {
        submitCount++;
      },
    }),
    (err) => {
      assert.equal(err instanceof WorkflowError, true);
      assert.equal(err.code, "unsupported_action");
      assert.equal(err.message, "The requested workflow action is unsupported. Action must be 'download' or 'submit'.");
      assert.equal(err.message.includes(secretActionInput), false);
      return true;
    }
  );

  assert.equal(downloadCount, 0);
  assert.equal(submitCount, 0);
});

test("dispatchWorkflow refuses missing or malformed prepared snapshot", async () => {
  await assert.rejects(
    dispatchWorkflow({
      prepared: null,
      action: "download",
      downloadPrepared: () => {},
      submitPrepared: () => {},
    }),
    (err) => {
      assert.equal(err instanceof WorkflowError, true);
      assert.equal(err.code, "invalid_prepared_snapshot");
      return true;
    }
  );
});

test("the deployment tuple is checked before any Actor is read", async () => {
  const game = fakeGame({ coreVersion: "13.999" });
  for (const actor of game.actors) {
    actor.toObject = () => {
      throw new Error("Actors must not be read for an unsupported deployment");
    };
  }
  await assert.rejects(
    prepare(game),
    (error) => error instanceof BundleError && error.code === "unsupported_deployment"
  );
});

test("the bytes hashed are the bytes sent", async () => {
  const prepared = await prepare();
  const fetchImpl = fakeFetch({
    status: "pending",
    checksum: prepared.checksum,
    actor_count: 2,
    duplicate: false,
  });
  await sendSnapshot({
    prepared,
    endpoint: "https://freedom.example/api/v1/foundry/snapshots",
    credential: "principal.0123456789012345678901234567890123456789",
    fetchImpl,
  });
  const [call] = fetchImpl.calls;
  assert.equal(call.init.body, prepared.bytes);
  assert.equal(call.init.headers["X-Snapshot-SHA256"], prepared.checksum);
  assert.equal(
    await sha256Hex(call.init.body, nodeCrypto),
    call.init.headers["X-Snapshot-SHA256"]
  );
});

test("preparing the same unchanged world twice at the same instant is byte-identical", async () => {
  const state = new PreparedSnapshotState();
  const first = await prepare(fakeGame(), ACTIVE_FOLDER_ID, undefined, state);
  const second = await prepare(fakeGame(), ACTIVE_FOLDER_ID, undefined, state);
  assert.deepEqual(Array.from(first.bytes), Array.from(second.bytes));
  assert.equal(first.checksum, second.checksum);
});

test("a receipt line reports agreement and carries no Actor data", async () => {
  const prepared = await prepare();
  const line = describeReceipt(
    { checksum: prepared.checksum, actor_count: 2, duplicate: false },
    prepared.checksum
  );
  assert.match(line, /recorded as pending/);
  assert.match(line, /checksums match/);
  assert.match(line, /nothing has been applied yet/);
  assert.equal(line.includes("Testcharacter"), false);
  assert.equal(line.includes("Brightlantern"), false);
});

test("a checksum disagreement is stated plainly rather than glossed over", () => {
  const line = describeReceipt(
    { checksum: "f".repeat(64), actor_count: 2, duplicate: false },
    "a".repeat(64)
  );
  assert.match(line, /CHECKSUM DISAGREEMENT/);
});

test("a duplicate receipt says no second snapshot was created", () => {
  const line = describeReceipt(
    { checksum: "a".repeat(64), actor_count: 2, duplicate: true },
    "a".repeat(64)
  );
  assert.match(line, /no second snapshot/);
});

test("an unreadable Actor stops the whole export, sending nothing", async () => {
  const game = fakeGame({ actorOverrides: { [SECOND_ACTOR_ID]: { owned: false } } });
  const fetchImpl = fakeFetch({});
  await assert.rejects(prepare(game), (error) => error.code === "insufficient_permission");
  assert.equal(fetchImpl.calls.length, 0);
});

test("two submissions of unchanged exportable state while clock advances reuse exact prepared bytes, checksum, and idempotency key", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  let time = "2026-08-06T22:00:00.000Z";
  const now = () => new Date(time);

  const first = await prepare(game, ACTIVE_FOLDER_ID, now, state);

  time = "2026-08-06T22:05:00.000Z";
  const second = await prepare(game, ACTIVE_FOLDER_ID, now, state);

  assert.strictEqual(first, second);
  assert.strictEqual(first.bytes, second.bytes);
  assert.equal(first.checksum, second.checksum);
  assert.equal(first.exportedAt, "2026-08-06T22:00:00Z");

  const fetchImpl = fakeFetch({
    status: "pending",
    checksum: first.checksum,
    actor_count: 2,
    duplicate: true,
  });

  const response = await sendSnapshot({
    prepared: second,
    endpoint: "https://freedom.example/api/v1/foundry/snapshots",
    credential: "principal.0123456789012345678901234567890123456789",
    fetchImpl,
  });

  assert.equal(response.receipt.duplicate, true);
  assert.equal(fetchImpl.calls[0].init.headers["X-Snapshot-SHA256"], first.checksum);
});

test("executeWorkflow transition: timeout, network_failure, and malformed_response pin exact prepared snapshot", async () => {
  for (const failureCase of [
    { name: "timeout", fetchImpl: () => Promise.reject({ name: "AbortError" }) },
    { name: "network_failure", fetchImpl: () => Promise.reject(new Error("Failed to fetch")) },
    {
      name: "malformed_response",
      fetchImpl: async () => ({
        ok: false,
        status: 502,
        json: async () => {
          throw new SyntaxError("Unexpected token <");
        },
      }),
    },
  ]) {
    const state = new PreparedSnapshotState();
    const game = fakeGame();

    await assert.rejects(
      executeWorkflow({
        game,
        crypto: nodeCrypto,
        folderId: ACTIVE_FOLDER_ID,
        exporterVersion: "1.0.2",
        supported: SUPPORTED,
        state,
        action: "submit",
        endpoint: "https://freedom.example/api/v1/foundry/snapshots",
        credential: "principal.0123456789012345678901234567890123456789",
        fetchImpl: failureCase.fetchImpl,
      }),
      (err) => err instanceof TransportError
    );

    assert.equal(state.status, "unconfirmed-retry-pinned", `Case ${failureCase.name} should pin retry`);
    assert.notEqual(state.pinnedPrepared, null);
  }
});

test("executeWorkflow transition: same-key server failures pin exact prepared snapshot", async () => {
  for (const code of [
    "concurrent_submission",
    "storage_unavailable",
    "database_unavailable",
    "internal_error",
    "authentication_unavailable",
  ]) {
    const state = new PreparedSnapshotState();
    const game = fakeGame();
    const status = code === "concurrent_submission" ? 409 : 503;

    await assert.rejects(
      executeWorkflow({
        game,
        crypto: nodeCrypto,
        folderId: ACTIVE_FOLDER_ID,
        exporterVersion: "1.0.2",
        supported: SUPPORTED,
        state,
        action: "submit",
        endpoint: "https://freedom.example/api/v1/foundry/snapshots",
        credential: "principal.0123456789012345678901234567890123456789",
        fetchImpl: fakeFetch({ error: { code, message: "Refused" } }, status),
      }),
      (err) => err instanceof TransportError && err.code === code
    );

    assert.equal(state.status, "unconfirmed-retry-pinned", `Code ${code} should pin retry`);
  }
});

test("executeWorkflow transition: local refusals and definitive server refusals clear state", async () => {
  for (const refusalCase of [
    { code: "missing_credential", credential: "" },
    { code: "insecure_endpoint", endpoint: "http://example.com/api" },
    { code: "request_key_conflict", fetchImpl: fakeFetch({ error: { code: "request_key_conflict", message: "Conflict" } }, 409) },
    { code: "unauthenticated", fetchImpl: fakeFetch({ error: { code: "unauthenticated", message: "Unauthorized" } }, 401) },
    { code: "out_of_scope", fetchImpl: fakeFetch({ error: { code: "out_of_scope", message: "Forbidden" } }, 403) },
    { code: "artifact_rejected", fetchImpl: fakeFetch({ error: { code: "artifact_rejected", message: "Rejected" } }, 400) },
  ]) {
    const state = new PreparedSnapshotState();
    const game = fakeGame();

    await assert.rejects(
      executeWorkflow({
        game,
        crypto: nodeCrypto,
        folderId: ACTIVE_FOLDER_ID,
        exporterVersion: "1.0.2",
        supported: SUPPORTED,
        state,
        action: "submit",
        endpoint: refusalCase.endpoint ?? "https://freedom.example/api/v1/foundry/snapshots",
        credential: refusalCase.credential ?? "principal.0123456789012345678901234567890123456789",
        fetchImpl: refusalCase.fetchImpl ?? fakeFetch({}),
      })
    );

    assert.equal(state.status, "empty", `Case ${refusalCase.code} should clear state`);
  }
});

test("failure classification has one closed four-value policy", () => {
  assert.equal(Object.isFrozen(FailureDisposition), true);
  assert.deepEqual(
    new Set(Object.values(FailureDisposition)),
    new Set([
      "local_refusal",
      "definitive_refusal",
      "retry_same_key",
      "delivery_indeterminate",
    ])
  );

  assert.equal(
    classifyFailureDisposition(new WorkflowError("local", "Local refusal.")),
    FailureDisposition.LOCAL_REFUSAL
  );
  assert.equal(
    classifyFailureDisposition(
      new TransportError("artifact_rejected", "Rejected.", {
        stage: "post_dispatch",
        status: 400,
      })
    ),
    FailureDisposition.DEFINITIVE_REFUSAL
  );
  assert.equal(
    classifyFailureDisposition(
      new TransportError("unknown_server_failure", "Unavailable.", {
        stage: "post_dispatch",
        status: 599,
      })
    ),
    FailureDisposition.RETRY_SAME_KEY
  );
  assert.equal(
    classifyFailureDisposition(
      new TransportError("unknown_delivery", "Unconfirmed.", {
        stage: "post_dispatch",
      })
    ),
    FailureDisposition.DELIVERY_INDETERMINATE
  );
});

test("arbitrary or mutated disposition metadata cannot clear an uncertain delivery", () => {
  const error = new TransportError("unknown_delivery", "Unconfirmed.", {
    stage: "post_dispatch",
  });

  error.disposition = "local_refusal";
  assert.equal(
    classifyFailureDisposition(error),
    FailureDisposition.DELIVERY_INDETERMINATE
  );

  error.disposition = "not-a-disposition";
  assert.equal(
    classifyFailureDisposition(error),
    FailureDisposition.DELIVERY_INDETERMINATE
  );

  assert.equal(
    classifyFailureDisposition({
      stage: "post_dispatch",
      disposition: "definitive_refusal",
    }),
    FailureDisposition.DELIVERY_INDETERMINATE
  );

  const bounded = new TransportError("unknown_delivery", "Unconfirmed.", {
    stage: "post_dispatch",
    status: 400,
  });
  bounded.stage = "pre_dispatch";
  assert.equal(
    classifyFailureDisposition(bounded),
    FailureDisposition.DEFINITIVE_REFUSAL
  );
});

test("status controls policy for server codes except concurrent submission", () => {
  for (const code of [
    "storage_unavailable",
    "database_unavailable",
    "internal_error",
    "authentication_unavailable",
  ]) {
    assert.equal(
      classifyFailureDisposition(new TransportError(code, "Refused.", {
        stage: "post_dispatch",
        status: 400,
      })),
      FailureDisposition.DEFINITIVE_REFUSAL
    );
  }
});

test("an unknown post-dispatch response pins exact prepared state conservatively", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();

  await assert.rejects(
    executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: "principal.0123456789012345678901234567890123456789",
      fetchImpl: fakeFetch(
        { error: { code: "unknown_redirect_response", message: "Unexpected response." } },
        302
      ),
    }),
    (error) =>
      error instanceof TransportError &&
      classifyFailureDisposition(error) === FailureDisposition.DELIVERY_INDETERMINATE
  );

  assert.equal(state.status, "unconfirmed-retry-pinned");
  assert.notEqual(state.pinnedPrepared, null);
});

test("timeout or network failure followed by retry resends exact prepared identity, bytes, checksum, timestamp and idempotency key", async () => {
  for (const failureCase of [
    { name: "network failure", err: new Error("Failed to fetch") },
    { name: "timeout AbortError", err: { name: "AbortError" } },
  ]) {
    const state = new PreparedSnapshotState();
    const game = fakeGame();
    let time = "2026-08-06T22:00:00.000Z";
    const now = () => new Date(time);

    const calls = [];
    let attemptCount = 0;
    const failingFetch = async (url, init) => {
      calls.push({ url, init });
      attemptCount++;
      if (attemptCount === 1) {
        throw failureCase.err;
      }
      return {
        ok: true,
        status: 201,
        json: async () => ({
          status: "pending",
          checksum: init.headers["X-Snapshot-SHA256"],
          actor_count: 2,
          duplicate: false,
        }),
      };
    };

    // Attempt 1: Failure (network error or timeout)
    await assert.rejects(
      executeWorkflow({
        game,
        crypto: nodeCrypto,
        folderId: ACTIVE_FOLDER_ID,
        exporterVersion: "1.0.2",
        supported: SUPPORTED,
        state,
        action: "submit",
        endpoint: "https://freedom.example/api/v1/foundry/snapshots",
        credential: "principal.0123456789012345678901234567890123456789",
        fetchImpl: failingFetch,
        now,
      }),
      (err) => err instanceof TransportError
    );

    assert.equal(state.status, "unconfirmed-retry-pinned", `Case ${failureCase.name} should pin state`);
    const pinned = state.pinnedPrepared;

    // Attempt 2: Retry with clock advanced
    time = "2026-08-06T22:05:00.000Z";
    const { prepared: retriedPrep, receipt } = await executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: "principal.0123456789012345678901234567890123456789",
      fetchImpl: failingFetch,
      now,
    });

    assert.equal(calls.length, 2);
    const [call1, call2] = calls;
    assert.strictEqual(call1.init.body, call2.init.body);
    assert.equal(call1.init.headers["X-Snapshot-SHA256"], call2.init.headers["X-Snapshot-SHA256"]);
    assert.equal(call1.init.headers["Idempotency-Key"], call2.init.headers["Idempotency-Key"]);

    assert.strictEqual(pinned, retriedPrep);
    assert.strictEqual(pinned.bytes, retriedPrep.bytes);
    assert.equal(pinned.checksum, retriedPrep.checksum);
    assert.equal(retriedPrep.exportedAt, "2026-08-06T22:00:00Z");
    assert.equal(receipt.checksum, pinned.checksum);
  }
});

test("changed world while an unconfirmed retry is pinned, followed by explicit operator discard and fresh preparation", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  let time = "2026-08-06T22:00:00.000Z";
  const now = () => new Date(time);

  const failingFetch = () => Promise.reject(new Error("Network disconnect"));

  await assert.rejects(
    executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: "principal.0123456789012345678901234567890123456789",
      fetchImpl: failingFetch,
      now,
    })
  );

  const initialPinned = state.pinnedPrepared;

  // World changes while retry is pinned
  const actorDoc = game.actors.find((a) => a.id === FIRST_ACTOR_ID);
  const origToObject = actorDoc.toObject.bind(actorDoc);
  actorDoc.toObject = () => {
    const obj = origToObject();
    obj.system.attributes = { hp: { value: 10, max: 45 } };
    return obj;
  };

  // Retry without discard returns pinned unconfirmed snapshot despite world change
  time = "2026-08-06T22:05:00.000Z";
  const prepPinned = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
    discardPinned: false,
  });

  assert.strictEqual(prepPinned, initialPinned);
  assert.equal(prepPinned.exportedAt, "2026-08-06T22:00:00Z");

  // Explicit operator discard clears pinned retry and prepares fresh state
  time = "2026-08-06T22:10:00.000Z";
  const prepFresh = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
    discardPinned: true,
  });

  assert.notStrictEqual(prepFresh, initialPinned);
  assert.notEqual(prepFresh.checksum, initialPinned.checksum);
  assert.equal(prepFresh.exportedAt, "2026-08-06T22:10:00Z");
  assert.equal(state.status, "confirmed-reusable");
});

test("meaningful Actor or embedded Item change invalidates reuse", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  let time = "2026-08-06T22:00:00.000Z";
  const now = () => new Date(time);

  const first = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  const actorDoc = game.actors.find((a) => a.id === FIRST_ACTOR_ID);
  const origToObject = actorDoc.toObject.bind(actorDoc);
  actorDoc.toObject = () => {
    const obj = origToObject();
    obj.system.attributes = { hp: { value: 45, max: 45 } };
    return obj;
  };

  time = "2026-08-06T22:10:00.000Z";
  const second = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  assert.notStrictEqual(first, second);
  assert.notEqual(first.checksum, second.checksum);
  assert.equal(second.exportedAt, "2026-08-06T22:10:00Z");
});

test("relevant Folder/export-scope change invalidates reuse", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  let time = "2026-08-06T22:00:00.000Z";
  const now = () => new Date(time);

  const first = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  const folderDoc = game.folders.find((f) => f.id === ACTIVE_FOLDER_ID);
  folderDoc.name = "Renamed Active Characters";

  time = "2026-08-06T22:15:00.000Z";
  const second = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  assert.notStrictEqual(first, second);
  assert.notEqual(first.checksum, second.checksum);
  assert.equal(second.exportedAt, "2026-08-06T22:15:00Z");
});

test("switching selected folders does not reuse the prior folder snapshot", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  let time = "2026-08-06T22:00:00.000Z";
  const now = () => new Date(time);

  const activePrep = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  time = "2026-08-06T22:02:00.000Z";
  const inactivePrep = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: INACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  assert.notStrictEqual(activePrep, inactivePrep);
  assert.notEqual(activePrep.checksum, inactivePrep.checksum);
  assert.notEqual(activePrep.folderPath, inactivePrep.folderPath);
});

test("download followed by submission reuses unchanged prepared bytes", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  let time = "2026-08-06T22:00:00.000Z";
  const now = () => new Date(time);

  const { prepared: downloadPrep } = await executeWorkflow({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    action: "download",
    now,
  });

  time = "2026-08-06T22:01:00.000Z";
  const fetchImpl = fakeFetch({
    status: "pending",
    checksum: downloadPrep.checksum,
    actor_count: 2,
    duplicate: false,
  });

  const { prepared: submitPrep } = await executeWorkflow({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    action: "submit",
    endpoint: "https://freedom.example/api/v1/foundry/snapshots",
    credential: "principal.0123456789012345678901234567890123456789",
    fetchImpl,
    now,
  });

  assert.strictEqual(downloadPrep, submitPrep);
  assert.strictEqual(downloadPrep.bytes, submitPrep.bytes);
  assert.equal(downloadPrep.checksum, submitPrep.checksum);
});

test("download while delivery is unconfirmed preserves the pinned retry", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  const failedFetch = async () => {
    throw new Error("delivery outcome unknown");
  };

  await assert.rejects(
    executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: "principal.0123456789012345678901234567890123456789",
      fetchImpl: failedFetch,
    }),
    (error) => error instanceof TransportError && error.code === "network_failure"
  );

  const pinned = state.pinnedPrepared;
  let downloaded;
  const result = await executeWorkflow({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    action: "download",
    forceFresh: true,
    discardPinned: false,
    downloadPrepared: (prepared) => {
      downloaded = prepared;
    },
  });

  assert.strictEqual(result.prepared, pinned);
  assert.strictEqual(downloaded, pinned);
  assert.equal(state.status, "unconfirmed-retry-pinned");
  assert.strictEqual(state.pinnedPrepared, pinned);
});

test("standalone preparation cannot take authority from an in-flight workflow", async () => {
  const state = new PreparedSnapshotState();
  const deferred = createDeferred();
  const game = fakeGame();
  const workflow = executeWorkflow({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    action: "submit",
    endpoint: "https://freedom.example/api/v1/foundry/snapshots",
    credential: "principal.0123456789012345678901234567890123456789",
    fetchImpl: async () => deferred.promise,
  });

  while (state.operation === null) await Promise.resolve();
  const standalone = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });
  assert.equal(state.operation !== null, true);

  deferred.resolve({
    ok: false,
    status: 503,
    json: async () => ({ error: { code: "storage_unavailable" } }),
  });
  await assert.rejects(workflow, (error) => error instanceof TransportError);
  assert.equal(state.status, "unconfirmed-retry-pinned");
  assert.notStrictEqual(state.pinnedPrepared, standalone);
  assert.equal(state.pinnedPrepared.checksum, standalone.checksum);
});

test("the cache remains strictly bounded to one entry through folder switches", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  let time = "2026-08-06T22:00:00.000Z";
  const now = () => new Date(time);

  const prepA1 = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  assert.equal(state.isReusable(ACTIVE_FOLDER_ID, prepA1.contentFingerprint), true);
  assert.strictEqual(state.getReusablePrepared(ACTIVE_FOLDER_ID, prepA1.contentFingerprint), prepA1);

  time = "2026-08-06T22:01:00.000Z";
  const prepB1 = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: INACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  assert.equal(state.isReusable(INACTIVE_FOLDER_ID, prepB1.contentFingerprint), true);
  assert.strictEqual(state.getReusablePrepared(INACTIVE_FOLDER_ID, prepB1.contentFingerprint), prepB1);
  assert.equal(state.isReusable(ACTIVE_FOLDER_ID, prepA1.contentFingerprint), false);
  assert.equal(state.getReusablePrepared(ACTIVE_FOLDER_ID, prepA1.contentFingerprint), null);

  time = "2026-08-06T22:02:00.000Z";
  const prepA2 = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
    now,
  });

  assert.notStrictEqual(prepA1, prepB1);
  assert.notStrictEqual(prepB1, prepA2);
  assert.notStrictEqual(prepA1, prepA2);
  assert.equal(prepA2.exportedAt, "2026-08-06T22:02:00Z");

  assert.equal(state.isReusable(INACTIVE_FOLDER_ID, prepB1.contentFingerprint), false);
  assert.equal(state.getReusablePrepared(INACTIVE_FOLDER_ID, prepB1.contentFingerprint), null);
});

test("credentials never enter prepared or cached state and are not retained by the test harness after submission", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();

  const prepared = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });

  assert.equal("credential" in prepared, false);
  assert.equal("submissionCredential" in prepared, false);

  let credentialInput = "principal.0123456789012345678901234567890123456789";
  assert.equal(JSON.stringify(prepared).includes(credentialInput), false);
  const fetchImpl = fakeFetch({
    status: "pending",
    checksum: prepared.checksum,
    actor_count: 2,
    duplicate: false,
  });

  try {
    await executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint: "https://freedom.example/api/v1/foundry/snapshots",
      credential: credentialInput,
      fetchImpl,
    });
  } finally {
    credentialInput = "";
  }

  assert.equal(credentialInput, "");
  assert.equal(JSON.stringify(state).includes("secret"), false);
});

test("state operation identity rejects stale completion and clear transitions", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();

  const prepA = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });
  const operationA = state.operation;

  const prepB = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: INACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });
  const operationB = state.operation;

  assert.equal(typeof operationA, "symbol");
  assert.equal(typeof operationB, "symbol");
  assert.notStrictEqual(operationA, operationB);
  assert.equal(state.status, "confirmed-reusable");

  const updatedStale = state.setPinnedRetry(
    prepA.folderId,
    prepA.contentFingerprint,
    prepA,
    operationA
  );
  assert.equal(updatedStale, false);
  assert.strictEqual(
    state.getReusablePrepared(INACTIVE_FOLDER_ID, prepB.contentFingerprint),
    prepB
  );

  const clearedStale = state.clear(operationA);
  assert.equal(clearedStale, false);
  assert.equal(state.status, "confirmed-reusable");
  assert.strictEqual(
    state.getReusablePrepared(INACTIVE_FOLDER_ID, prepB.contentFingerprint),
    prepB
  );
});

function createDeferred() {
  let resolve, reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

function withTimeout(promise, ms = 2000, label = "Operation") {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(new Error(`${label} timed out after ${ms}ms`)), ms);
    timer.unref?.();
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

test("executeWorkflow race 1: same payload - newer success completes before older definitive refusal", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  const endpoint = "https://freedom.example/api/v1/foundry/snapshots";
  const credential = "principal.0123456789012345678901234567890123456789";

  const prewarmed = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });

  assert.equal(state.status, "confirmed-reusable");
  assert.equal(prewarmed.generation, 1);

  const olderDeferred = createDeferred();
  const newerDeferred = createDeferred();
  const calls = [];

  const fetchOlder = async (url, init) => {
    calls.push({ id: "older", url, init });
    return olderDeferred.promise;
  };

  const fetchNewer = async (url, init) => {
    calls.push({ id: "newer", url, init });
    return newerDeferred.promise;
  };

  try {
    const olderPromise = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fetchOlder,
    });

    const newerPromise = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fetchNewer,
    });

    // Step 1: Newer successful submission completes
    newerDeferred.resolve({
      ok: true,
      status: 201,
      json: async () => ({
        status: "pending",
        checksum: prewarmed.checksum,
        actor_count: prewarmed.actorCount,
        duplicate: false,
      }),
    });

    const newerRes = await withTimeout(newerPromise, 2000, "Newer submission");
    assert.strictEqual(newerRes.prepared, prewarmed);
    assert.equal(newerRes.status, 201);
    assert.equal(state.status, "confirmed-reusable");

    // Step 2: Older definitive refusal completes
    olderDeferred.resolve({
      ok: false,
      status: 400,
      json: async () => ({ error: { code: "definitive_refusal", message: "Bad Request" } }),
    });

    await assert.rejects(
      withTimeout(olderPromise, 2000, "Older refusal"),
      (err) => err instanceof TransportError && err.status === 400
    );

    // Assertions: Success must remain reusable
    assert.equal(calls.length, 2);
    assert.strictEqual(calls[0].init.body, calls[1].init.body);
    assert.equal(calls[0].init.headers["X-Snapshot-SHA256"], prewarmed.checksum);
    assert.equal(calls[1].init.headers["X-Snapshot-SHA256"], prewarmed.checksum);
    assert.equal(calls[0].init.headers["Idempotency-Key"], calls[1].init.headers["Idempotency-Key"]);

    assert.equal(state.status, "confirmed-reusable");
    assert.strictEqual(
      state.getReusablePrepared(ACTIVE_FOLDER_ID, prewarmed.contentFingerprint),
      prewarmed
    );
  } finally {
    olderDeferred.resolve({ ok: false, status: 400, json: async () => ({}) });
    newerDeferred.resolve({ ok: true, status: 201, json: async () => ({}) });
  }
});

test("executeWorkflow race 2: same payload - newer success completes before older retryable failure", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  const endpoint = "https://freedom.example/api/v1/foundry/snapshots";
  const credential = "principal.0123456789012345678901234567890123456789";

  const prewarmed = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });

  assert.equal(state.status, "confirmed-reusable");
  assert.equal(prewarmed.generation, 1);

  const olderDeferred = createDeferred();
  const newerDeferred = createDeferred();
  const calls = [];

  const fetchOlder = async (url, init) => {
    calls.push({ id: "older", url, init });
    return olderDeferred.promise;
  };

  const fetchNewer = async (url, init) => {
    calls.push({ id: "newer", url, init });
    return newerDeferred.promise;
  };

  try {
    const olderPromise = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fetchOlder,
    });

    const newerPromise = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fetchNewer,
    });

    // Step 1: Newer success completes
    newerDeferred.resolve({
      ok: true,
      status: 201,
      json: async () => ({
        status: "pending",
        checksum: prewarmed.checksum,
        actor_count: prewarmed.actorCount,
        duplicate: false,
      }),
    });

    const newerRes = await withTimeout(newerPromise, 2000, "Newer submission");
    assert.strictEqual(newerRes.prepared, prewarmed);
    assert.equal(state.status, "confirmed-reusable");

    // Step 2: Older retryable/indeterminate failure completes
    olderDeferred.resolve({
      ok: false,
      status: 503,
      json: async () => ({ error: { code: "database_unavailable", message: "Service Unavailable" } }),
    });

    await assert.rejects(
      withTimeout(olderPromise, 2000, "Older failure"),
      (err) => err instanceof TransportError && err.status === 503
    );

    // Assertions: Stale failure must not repin over confirmed success
    assert.equal(calls.length, 2);
    assert.strictEqual(calls[0].init.body, calls[1].init.body);
    assert.equal(calls[0].init.headers["X-Snapshot-SHA256"], prewarmed.checksum);
    assert.equal(calls[1].init.headers["X-Snapshot-SHA256"], prewarmed.checksum);
    assert.equal(calls[0].init.headers["Idempotency-Key"], calls[1].init.headers["Idempotency-Key"]);

    assert.equal(state.status, "confirmed-reusable");
    assert.equal(state.hasPinnedRetry(), false);
    assert.strictEqual(
      state.getReusablePrepared(ACTIVE_FOLDER_ID, prewarmed.contentFingerprint),
      prewarmed
    );
  } finally {
    olderDeferred.resolve({ ok: false, status: 503, json: async () => ({}) });
    newerDeferred.resolve({ ok: true, status: 201, json: async () => ({}) });
  }
});

test("executeWorkflow race 3: same payload - newer pinned failure completes before older success", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  const endpoint = "https://freedom.example/api/v1/foundry/snapshots";
  const credential = "principal.0123456789012345678901234567890123456789";

  const prewarmed = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });

  assert.equal(state.status, "confirmed-reusable");
  assert.equal(prewarmed.generation, 1);

  const olderDeferred = createDeferred();
  const newerDeferred = createDeferred();
  const calls = [];

  const fetchOlder = async (url, init) => {
    calls.push({ id: "older", url, init });
    return olderDeferred.promise;
  };

  const fetchNewer = async (url, init) => {
    calls.push({ id: "newer", url, init });
    return newerDeferred.promise;
  };

  try {
    const olderPromise = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fetchOlder,
    });

    const newerPromise = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fetchNewer,
    });

    // Step 1: Newer pinned failure completes first
    newerDeferred.resolve({
      ok: false,
      status: 500,
      json: async () => ({ error: { code: "internal_error", message: "Server Error" } }),
    });

    await assert.rejects(
      withTimeout(newerPromise, 2000, "Newer failure"),
      (err) => err instanceof TransportError && err.status === 500
    );
    assert.equal(state.status, "unconfirmed-retry-pinned");
    assert.strictEqual(state.pinnedPrepared, prewarmed);

    // Step 2: Older success completes second
    olderDeferred.resolve({
      ok: true,
      status: 201,
      json: async () => ({
        status: "pending",
        checksum: prewarmed.checksum,
        actor_count: prewarmed.actorCount,
        duplicate: false,
      }),
    });

    const olderRes = await withTimeout(olderPromise, 2000, "Older success");
    assert.strictEqual(olderRes.prepared, prewarmed);

    // Assertions: Latest operation wins; older success must not overwrite newer pin
    assert.equal(calls.length, 2);
    assert.strictEqual(calls[0].init.body, calls[1].init.body);
    assert.equal(calls[0].init.headers["X-Snapshot-SHA256"], prewarmed.checksum);
    assert.equal(calls[1].init.headers["X-Snapshot-SHA256"], prewarmed.checksum);
    assert.equal(calls[0].init.headers["Idempotency-Key"], calls[1].init.headers["Idempotency-Key"]);

    assert.equal(state.status, "unconfirmed-retry-pinned");
    assert.equal(state.hasPinnedRetry(), true);
    assert.strictEqual(state.pinnedPrepared, prewarmed);
  } finally {
    olderDeferred.resolve({ ok: true, status: 201, json: async () => ({}) });
    newerDeferred.resolve({ ok: false, status: 500, json: async () => ({}) });
  }
});

test("executeWorkflow race 4: operator discards pinned retry while request in flight", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  const endpoint = "https://freedom.example/api/v1/foundry/snapshots";
  const credential = "principal.0123456789012345678901234567890123456789";

  const prewarmed = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });

  const initialFail = fakeFetch({ error: { code: "internal_error", message: "Server error" } }, 500);
  await assert.rejects(
    executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: initialFail,
    }),
    (err) => err instanceof TransportError
  );

  assert.equal(state.status, "unconfirmed-retry-pinned");
  const p1 = state.pinnedPrepared;
  assert.strictEqual(p1, prewarmed);

  const inFlightDeferred = createDeferred();
  const inFlightFetch = async () => inFlightDeferred.promise;
  const preparationDeferred = createDeferred();
  let digestCalls = 0;
  const gatedCrypto = {
    subtle: {
      digest: async (...args) => {
        digestCalls++;
        if (digestCalls === 1) await preparationDeferred.promise;
        return nodeCrypto.subtle.digest(...args);
      },
    },
  };

  try {
    const inFlightPromise = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: inFlightFetch,
    });

    // Drive the same discard-and-submit path used by main.js. Its first digest
    // is gated so the older request completes while preparation is in flight.
    const freshWorkflowPromise = executeWorkflow({
      game,
      crypto: gatedCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fakeFetch({
        status: "pending",
        checksum: p1.checksum,
        actor_count: p1.actorCount,
        duplicate: true,
      }),
      discardPinned: true,
    });

    // Older request completes while fresh prep is processing
    inFlightDeferred.resolve({
      ok: true,
      status: 201,
      json: async () => ({
        status: "pending",
        checksum: p1.checksum,
        actor_count: p1.actorCount,
        duplicate: false,
      }),
    });

    const inFlightRes = await withTimeout(inFlightPromise, 2000, "In-flight request");
    assert.strictEqual(inFlightRes.prepared, p1);

    // Before fresh prep finishes, the discarded attempt must not be restored to state
    assert.equal(state.status, "empty");
    assert.equal(
      state.getReusablePrepared(ACTIVE_FOLDER_ID, p1.contentFingerprint),
      null
    );

    preparationDeferred.resolve();
    const { prepared: freshPrep } = await withTimeout(
      freshWorkflowPromise,
      2000,
      "Fresh workflow"
    );
    assert.notStrictEqual(freshPrep, p1);
    assert.equal(freshPrep.folderId, ACTIVE_FOLDER_ID);
    assert.equal(freshPrep.checksum, p1.checksum);

    assert.equal(state.status, "confirmed-reusable");
    assert.strictEqual(
      state.getReusablePrepared(ACTIVE_FOLDER_ID, freshPrep.contentFingerprint),
      freshPrep
    );
    assert.notStrictEqual(
      state.getReusablePrepared(ACTIVE_FOLDER_ID, p1.contentFingerprint),
      p1
    );
    assert.equal(state.hasPinnedRetry(), false);
  } finally {
    inFlightDeferred.resolve({ ok: true, status: 201, json: async () => ({}) });
    preparationDeferred.resolve();
  }
});

test("executeWorkflow race 5: fresh preparation fails locally after discard while request in flight", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  const endpoint = "https://freedom.example/api/v1/foundry/snapshots";
  const credential = "principal.0123456789012345678901234567890123456789";

  const prewarmed = await prepareSnapshot({
    game,
    crypto: nodeCrypto,
    folderId: ACTIVE_FOLDER_ID,
    exporterVersion: "1.0.2",
    supported: SUPPORTED,
    state,
  });

  const initialFail = fakeFetch({ error: { code: "internal_error", message: "Server error" } }, 500);
  await assert.rejects(
    executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: initialFail,
    }),
    (err) => err instanceof TransportError
  );

  assert.equal(state.status, "unconfirmed-retry-pinned");
  const p1 = state.pinnedPrepared;
  assert.strictEqual(p1, prewarmed);

  const inFlightDeferred = createDeferred();
  const inFlightFetch = async () => inFlightDeferred.promise;

  try {
    const inFlightPromise = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: inFlightFetch,
    });

    const badGame = fakeGame({ actorOverrides: { [SECOND_ACTOR_ID]: { owned: false } } });

    await assert.rejects(
      executeWorkflow({
        game: badGame,
        crypto: nodeCrypto,
        folderId: ACTIVE_FOLDER_ID,
        exporterVersion: "1.0.2",
        supported: SUPPORTED,
        state,
        action: "submit",
        endpoint,
        credential,
        fetchImpl: fakeFetch({}),
        discardPinned: true,
      }),
      (err) => err instanceof SourceError && err.code === "insufficient_permission"
    );

    assert.equal(state.status, "empty");

    // In-flight request completes after fresh prep failed locally
    inFlightDeferred.resolve({
      ok: true,
      status: 201,
      json: async () => ({
        status: "pending",
        checksum: p1.checksum,
        actor_count: p1.actorCount,
        duplicate: false,
      }),
    });

    const inFlightRes = await withTimeout(inFlightPromise, 2000, "In-flight request");
    assert.strictEqual(inFlightRes.prepared, p1);

    // Older completion must not resurrect discarded state
    assert.equal(state.status, "empty");
    assert.equal(state.hasPinnedRetry(), false);
    assert.equal(
      state.getReusablePrepared(ACTIVE_FOLDER_ID, p1.contentFingerprint),
      null
    );
  } finally {
    inFlightDeferred.resolve({ ok: true, status: 201, json: async () => ({}) });
  }
});

test("executeWorkflow race 6: different prepared payloads overlap", async () => {
  const state = new PreparedSnapshotState();
  const game = fakeGame();
  const endpoint = "https://freedom.example/api/v1/foundry/snapshots";
  const credential = "principal.0123456789012345678901234567890123456789";

  const deferredA = createDeferred();
  const deferredB = createDeferred();

  const fetchA = async () => deferredA.promise;
  const fetchB = async () => deferredB.promise;

  try {
    const promiseA = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: ACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fetchA,
    });

    const promiseB = executeWorkflow({
      game,
      crypto: nodeCrypto,
      folderId: INACTIVE_FOLDER_ID,
      exporterVersion: "1.0.2",
      supported: SUPPORTED,
      state,
      action: "submit",
      endpoint,
      credential,
      fetchImpl: fetchB,
    });

    deferredB.resolve({
      ok: true,
      status: 201,
      json: async () => ({
        status: "pending",
        checksum: "checksumB",
        actor_count: 1,
        duplicate: false,
      }),
    });

    const resB = await withTimeout(promiseB, 2000, "Payload B");
    assert.equal(resB.prepared.folderId, INACTIVE_FOLDER_ID);
    assert.equal(resB.prepared.generation, 2);
    assert.equal(state.status, "confirmed-reusable");

    deferredA.resolve({
      ok: true,
      status: 201,
      json: async () => ({
        status: "pending",
        checksum: "checksumA",
        actor_count: 2,
        duplicate: false,
      }),
    });

    const resA = await withTimeout(promiseA, 2000, "Payload A");
    assert.equal(resA.prepared.folderId, ACTIVE_FOLDER_ID);
    assert.equal(resA.prepared.generation, 1);

    assert.equal(state.status, "confirmed-reusable");
    assert.strictEqual(
      state.getReusablePrepared(INACTIVE_FOLDER_ID, resB.prepared.contentFingerprint),
      resB.prepared
    );
    assert.equal(
      state.getReusablePrepared(ACTIVE_FOLDER_ID, resA.prepared.contentFingerprint),
      null
    );
  } finally {
    deferredA.resolve({ ok: true, status: 201, json: async () => ({}) });
    deferredB.resolve({ ok: true, status: 201, json: async () => ({}) });
  }
});
