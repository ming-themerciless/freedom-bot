# Phase 2 I-03 third remediation — Codex security-focused re-review

Date: 2026-08-05

Scope: final-target publication, preservation of filesystem-root anchoring, and
preservation of S-B-1 credential confidentiality and S-I-1 CORS restrictions in
the uncommitted working tree at `c8a3da9` plus working-tree changes.

This report is separate from the implementation re-review and is a
recommendation, not approval. No Foundry module was installed and no Foundry
world storage or player data was accessed.

## Result

**The final-target publication defect is resolved. Root anchoring, S-B-1, and
S-I-1 remain preserved. I found no new Blocking or Important security finding
in this remediation.**

## Final-target publication

Publication performs one anchored `linkat` operation through `os.link`. The
destination is create-only: an existing regular file, symlink, directory, or
other entry produces `EEXIST`; none is followed, removed, or overwritten. The
subsequent validation opens the existing name relative to the anchored root
with `O_NOFOLLOW`, checks the opened descriptor, and hashes bytes read from that
same descriptor.

No reviewed sequence lets cleanup delete the final target. `_discard` returns
before `unlink` unless its argument has the internal `.incoming-` prefix, and
the checksum naming grammar cannot have that prefix. A failed cleanup may leave
a private temporary hard link, as documented in the implementation report, but
does not broaden access or threaten the final entry.

The startup probe tests the relevant filesystem behaviour at the configured
root. `publication_unsettled` is bounded and fail-closed if an `EEXIST` entry
repeatedly disappears before validation.

## Root anchoring

Temporary creation, artifact opens, publication, temporary unlink, presence
checks, and directory sync all use the held root descriptor. Root validation is
performed with `fstat` on that descriptor. The configured-path comparison only
detects divergence and grants no access. `TrustedAncestors` remains a startup
pathname check; its optional ceiling is injectable only in code and production
composition defaults to the unbounded walk.

The deliberately pathname-based constructor checks and root creation do not
reintroduce the reviewed post-validation redirection: the root is subsequently
opened with `O_DIRECTORY | O_NOFOLLOW`, validated through its descriptor, and
all artifact operations are anchored to it.

## S-B-1 and S-I-1 preservation

The Foundry module still takes the bearer credential from the submission dialog
for that request and does not register or write it to Foundry settings,
`localStorage`, `sessionStorage`, flags, documents, journals, notifications, or
receipts. Transport uses it only in the Authorization header and specifies
`credentials: "omit"`.

CORS remains fail-closed and exact: configured origins are normalized and
matched as complete origins; wildcards, `null`, paths, userinfo, and non-loopback
HTTP are refused; preflight is limited to the submission route, POST, and the
four client headers; and no credential-sharing header is emitted. The module's
81 tests and the Python HTTP/composition suites passed.

## Residual evidence

Operations §8.1 (observation from a live second Foundry client) and §8.2 (a real
browser-origin preflight) remain unperformed and require Peter. Automated source
and contract tests support the construction but do not replace those supervised
checks. The documented cross-account and multi-process experiments likewise
remain residual evidence, not claims made by this review.

## Recommendation

Recommend closure of the final-target publication security finding after the
Acceptance Authority considers this report and the separate implementation
review. Phase 2 remains open for the outstanding supervised and operational
evidence; this review does not approve or close the gate.
