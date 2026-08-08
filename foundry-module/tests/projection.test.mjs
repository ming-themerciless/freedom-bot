import test from "node:test";
import assert from "node:assert/strict";

import { projectFoundryData, SourceError, safeKeySegment } from "../scripts/world-source.js";
import { canonicalBytes, normalise, CanonicalError, MAX_DEPTH } from "../scripts/canonical.js";
import { buildBundle } from "../scripts/bundle.js";

test("synthetic nested object with optional undefined property omits that property", () => {
  const source = {
    _id: "itm0000000000001",
    name: "Synthetic Item",
    type: "feat",
    system: {
      advancement: {
        plH3fE1UazZ2j5k3: {
          title: "Synthetic Advancement",
          classRestriction: undefined,
          value: { option: "a" },
        },
      },
    },
  };

  const projected = projectFoundryData(source, "$");

  // Input object must not be mutated
  assert.equal(source.system.advancement.plH3fE1UazZ2j5k3.classRestriction, undefined);
  assert.equal("classRestriction" in source.system.advancement.plH3fE1UazZ2j5k3, true);

  // Projected object must omit classRestriction key
  assert.equal("classRestriction" in projected.system.advancement.plH3fE1UazZ2j5k3, false);
  assert.equal(projected.system.advancement.plH3fE1UazZ2j5k3.title, "Synthetic Advancement");
  assert.equal(projected.system.advancement.plH3fE1UazZ2j5k3.value.option, "a");
});

test("siblings with falsey primitives (null, false, 0, '') are retained exactly", () => {
  const source = {
    nullVal: null,
    boolVal: false,
    zeroVal: 0,
    emptyStr: "",
    undefVal: undefined,
  };

  const projected = projectFoundryData(source, "$");

  assert.equal(projected.nullVal, null);
  assert.equal(projected.boolVal, false);
  assert.equal(projected.zeroVal, 0);
  assert.equal(projected.emptyStr, "");
  assert.equal("undefVal" in projected, false);
  assert.deepEqual(Object.keys(projected).sort(), ["boolVal", "emptyStr", "nullVal", "zeroVal"]);
});

test("nested objects and objects inside arrays are projected recursively", () => {
  const source = {
    items: [
      {
        id: "i1",
        opt: undefined,
        active: true,
      },
    ],
  };

  const projected = projectFoundryData(source, "$");

  assert.equal(Array.isArray(projected.items), true);
  assert.equal(projected.items.length, 1);
  assert.equal("opt" in projected.items[0], false);
  assert.equal(projected.items[0].active, true);
});

test("undefined array element error path redacts dynamic IDs, names and UUIDs", () => {
  const syntheticDynamicId = "AbCdEf1234567890";
  const syntheticName = "SyntheticItemName";
  const syntheticUuid = "550e8400-e29b-41d4-a716-446655440000";

  const source = {
    system: {
      advancement: {
        [syntheticDynamicId]: {
          [syntheticName]: {
            [syntheticUuid]: ["valid", undefined],
          },
        },
      },
    },
  };

  assert.throws(
    () => projectFoundryData(source, "$actors[0]"),
    (err) => {
      assert.equal(err instanceof SourceError, true);
      assert.equal(err.code, "undefined_array_element");

      // Dynamic key strings must never appear in the error message
      assert.equal(err.message.includes(syntheticDynamicId), false);
      assert.equal(err.message.includes(syntheticName), false);
      assert.equal(err.message.includes(syntheticUuid), false);

      // Safe static structural keys and ordinal placeholders must appear
      assert.equal(err.message.includes("$actors[0].system.advancement.{key:0}.{key:0}.{key:0}[1]"), true);
      return true;
    }
  );
});

test("unsupported type and cycle errors use safe path formatting", () => {
  const dynamicKey = "SecretKeyName123";
  const funcObj = {
    system: {
      [dynamicKey]: () => {},
    },
  };

  assert.throws(
    () => projectFoundryData(funcObj, "$actors[0]"),
    (err) => {
      assert.equal(err instanceof SourceError, true);
      assert.equal(err.code, "unsupported_type");
      assert.equal(err.message.includes(dynamicKey), false);
      assert.equal(err.message.includes("$actors[0].system.{key:0}"), true);
      return true;
    }
  );

  const cycleObj = { system: {} };
  cycleObj.system.self = cycleObj;

  assert.throws(
    () => projectFoundryData(cycleObj, "$actors[0]"),
    (err) => {
      assert.equal(err instanceof SourceError, true);
      assert.equal(err.code, "cycle_detected");
      assert.equal(err.message.includes("$actors[0].system.{key:0}"), true);
      return true;
    }
  );
});

test("safeKeySegment preserves repository structural keys and redacts dynamic keys as ordinals", () => {
  assert.equal(safeKeySegment("system", 0), ".system");
  assert.equal(safeKeySegment("items", 1), ".items");
  assert.equal(safeKeySegment("advancement", 2), ".advancement");
  assert.equal(safeKeySegment("AbCdEf1234567890", 0), ".{key:0}");
  assert.equal(safeKeySegment("CustomAdvancementName", 3), ".{key:3}");
});

test("world-source.js does not export the safe-key policy", async () => {
  const worldSource = await import("../scripts/world-source.js");
  assert.equal("SAFE_STRUCTURAL_KEYS" in worldSource, false);
  for (const exportedKey of Object.keys(worldSource)) {
    const val = worldSource[exportedKey];
    assert.equal(val instanceof Set, false);
    assert.equal(val instanceof Map, false);
  }

  const { readFileSync } = await import("node:fs");
  const sourceCode = readFileSync(new URL("../scripts/world-source.js", import.meta.url), "utf-8");
  assert.match(sourceCode, /const\s+SAFE_STRUCTURAL_KEYS\s*=\s*Object\.freeze\(\s*\[/);
  assert.equal(/const\s+SAFE_STRUCTURAL_KEYS\s*=\s*new\s+(Set|Map)/.test(sourceCode), false);
});

test("depth boundary of 64 levels succeeds and level 65 refuses with excessive_depth", () => {
  // Construct 64-level nested object structure (root container + 63 inner containers)
  let level64 = { value: "leaf" };
  for (let i = 0; i < 63; i++) {
    level64 = { inner: level64 };
  }
  const projected64 = projectFoundryData(level64, "$");
  assert.equal(projected64 !== undefined, true);

  // Construct 65-level nested object structure
  let level65 = { value: "deep" };
  for (let i = 0; i < 64; i++) {
    level65 = { inner: level65 };
  }

  assert.throws(
    () => projectFoundryData(level65, "$"),
    (err) => {
      assert.equal(err instanceof SourceError, true);
      assert.equal(err.code, "excessive_depth");
      assert.equal(err.message.includes("exceeds maximum allowed limit of 64"), true);
      return true;
    }
  );
});

test("10,000-level synthetic input refuses with excessive_depth and never throws RangeError", () => {
  let deep10k = { leaf: true };
  for (let i = 0; i < 10000; i++) {
    deep10k = { sub: deep10k };
  }

  assert.throws(
    () => projectFoundryData(deep10k, "$"),
    (err) => {
      assert.equal(err instanceof SourceError, true);
      assert.equal(err.code, "excessive_depth");
      return true;
    }
  );
});

test("array and object structures share consistent depth semantics", () => {
  // 65-deep array nesting
  let deepArray = ["leaf"];
  for (let i = 0; i < 64; i++) {
    deepArray = [deepArray];
  }

  assert.throws(
    () => projectFoundryData(deepArray, "$"),
    (err) => {
      assert.equal(err instanceof SourceError, true);
      assert.equal(err.code, "excessive_depth");
      return true;
    }
  );
});

test("repeated non-ancestor sibling references are accepted while ancestor cycles refuse", () => {
  const sharedSibling = { active: true, name: "Shared" };
  const container = {
    first: sharedSibling,
    second: sharedSibling,
  };

  const projected = projectFoundryData(container, "$");
  assert.equal(projected.first.active, true);
  assert.equal(projected.second.active, true);
});

test("input objects are not mutated during projection", () => {
  const inner = { a: 1, b: undefined };
  const outer = { sub: inner };

  projectFoundryData(outer, "$");

  assert.equal("b" in inner, true);
  assert.equal(inner.b, undefined);
  assert.equal("sub" in outer, true);
});

test("canonicalisation independently refuses { a: undefined } as a fail-closed boundary", () => {
  const unprojectedWithUndefined = { a: undefined };

  assert.throws(
    () => normalise(unprojectedWithUndefined, "$"),
    (err) => {
      assert.equal(err instanceof CanonicalError, true);
      assert.equal(err.code, "undefined_value");
      return true;
    }
  );

  assert.throws(
    () => canonicalBytes(unprojectedWithUndefined),
    (err) => {
      assert.equal(err instanceof CanonicalError, true);
      assert.equal(err.code, "undefined_value");
      return true;
    }
  );
});

test("two projections of unchanged synthetic input produce identical bytes and checksum", () => {
  const actor1 = {
    id: "act0000000000001",
    folderId: "fld0000000000001",
    name: "Synthetic Hero",
    system: { level: 5, details: { title: "Champ", opt: undefined } },
    items: [{ id: "itm0000000000001", type: "feat", system: { restriction: undefined } }],
  };

  const proj1 = projectFoundryData(actor1, "$actors[0]");
  const proj2 = projectFoundryData(actor1, "$actors[0]");

  assert.deepEqual(proj1, proj2);

  const folders = new Map([["fld0000000000001", { id: "fld0000000000001", name: "Actors", parentId: null }]]);

  const bundle1 = buildBundle({
    exportedAt: "2026-08-06T00:00:00Z",
    exporterVersion: "1.0.2",
    world: { id: "w1", title: "W1", coreVersion: "14.365", systemId: "dnd5e", systemVersion: "5.3.3" },
    selectedFolderId: "fld0000000000001",
    folders,
    actors: [proj1],
  });

  const bundle2 = buildBundle({
    exportedAt: "2026-08-06T00:00:00Z",
    exporterVersion: "1.0.2",
    world: { id: "w1", title: "W1", coreVersion: "14.365", systemId: "dnd5e", systemVersion: "5.3.3" },
    selectedFolderId: "fld0000000000001",
    folders,
    actors: [proj2],
  });

  const bytes1 = canonicalBytes(bundle1);
  const bytes2 = canonicalBytes(bundle2);

  assert.deepEqual(bytes1, bytes2);
});
