import test from "node:test";
import assert from "node:assert/strict";

import { failureNotification } from "../scripts/notifications.js";

const base = {
  title: "Freedom Blades",
  reassurance: "Retry the same export.",
};

test("a newly pinned typed failure carries the reload warning behaviorally", () => {
  const message = failureNotification({
    ...base,
    known: true,
    code: "network_failure",
    message: "Nothing was confirmed.",
    retryPinned: true,
  });

  assert.match(message, /\[network_failure\]/);
  assert.match(message, /Do not reload or close this page/);
  assert.match(message, /exact retry state exists only for this page load/);
});

test("an unexpected pinned failure carries the same reload warning", () => {
  const message = failureNotification({
    ...base,
    known: false,
    retryPinned: true,
  });

  assert.match(message, /snapshot could not be completed/);
  assert.match(message, /Do not reload or close this page/);
});

test("a failure with no pin does not show the reload warning", () => {
  const message = failureNotification({
    ...base,
    known: true,
    code: "unauthenticated",
    message: "Refused.",
    retryPinned: false,
  });

  assert.doesNotMatch(message, /Do not reload/);
});
