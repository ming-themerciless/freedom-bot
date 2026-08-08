# Gemini Step 4 — close and harden failure classification

Proceed only after Codex accepts Step 3. This step is limited to failure
classification integrity and its focused tests.

Review `TransportError`, `classifyFailureDisposition`, `submitSnapshot`, the
operations failure table, and current transition tests.

Required correction:

- Define the four permitted dispositions once:
  `local_refusal`, `definitive_refusal`, `retry_same_key`, and
  `delivery_indeterminate`.
- Do not accept an arbitrary string from `error.disposition` as authoritative.
- Ensure invalid, missing or mutated disposition metadata cannot turn an
  uncertain post-dispatch failure into state clearing.
- Unknown pre-dispatch failures may be local only when the implementation can
  establish that dispatch did not occur.
- Unknown post-dispatch failures must conservatively pin exact prepared state.
- Preserve the documented explicit handling of local endpoint/credential
  refusals, definitive 4xx responses, `request_key_conflict`, same-key server
  categories, HTTP 5xx, timeout, network failure and malformed responses.
- Avoid two divergent classification tables. Transport may attach facts while
  workflow applies one validated policy.
- Keep messages bounded and repository-owned; never expose a raw response,
  exception cause, endpoint, credential or Actor data.

Add focused tests for every permitted disposition, invalid strings, missing
metadata, unknown pre-dispatch and unknown post-dispatch errors, and mutation of
an error after construction. Drive the resulting lifecycle transition through
`executeWorkflow()` where state behavior matters.

Run the complete Node suite, syntax checks, `git diff --check`, and targeted
source scans for credential/error leakage. Do not update controlled project
status yet.

End with:

`Step 4 complete locally: failure classification is closed and conservative; awaiting Codex security and implementation review.`
