# P3.4 Step 3 remediation independent review

Date: 2026-08-20

Status: **CLOSED BY REMEDIATION 02 AND PETER'S STEP 3 ACCEPTANCE**

Implementer: Gemini

Independent reviewer: Codex

Acceptance and release authority: Peter Duscha

## Scope

Codex independently reviewed Gemini's completed bounded Step 3 remediation
against:

- the released Step 3 shell prompt;
- the authorized Step 3 remediation prompt;
- the Step 1 immutable template baseline;
- the resulting two-file remediation allowlist; and
- the required visual-freeze, static-integrity, focused, supporting, combined,
  compilation, and diff checks.

This review does not accept Step 3 or release Step 4.

## Correctly remediated findings

1. `base.html` no longer contains the unsupported `head_extra` extension block.
2. The test module contains an explicit accepted SHA-256 mapping for all 23
   Step 1 page/fragment templates and enforces exact set and byte-digest
   equality.
3. The immutable header, footer, CSS, manifest, HTMX, emblem, and Step 2 test
   files retained their required digests.
4. The implementation remained within the two-file remediation allowlist.

## Remaining blocking findings

### B1 — ordinary inline event handlers pass the corpus validator

`validate_template_security_rules` rejects `hx-on:` but does not reject ordinary
HTML event-handler attributes such as `onclick`, `onerror`, or `onload`. The
reviewer passed this synthetic input through the production helper:

```html
<button onclick="alert(1)">x</button>
```

The helper returned successfully (`INLINE_HANDLER_ACCEPTED`). Therefore the
positive corpus guard and its falsification do not enforce the released Step 3
prohibition on inline event handlers.

### B2 — CSS manifest falsification is independent of the tampered bytes

`validate_manifest_integrity(manifest_path, static_dir)` ignores its
`static_dir` argument and resolves every manifest target through repository
`ROOT`. The falsification creates a temporary mutated CSS file but then supplies
an independently invalid all-zero digest whose path resolves to the unchanged
production CSS. The check would fail even if the temporary CSS were never
mutated, so it does not prove tampered-byte detection.

The manifest helper is also not invoked by a positive production-integrity test
in the Step 3 module. This violates the remediation requirement that the same
helper govern the positive and negative assertion.

## Verification evidence

All commands completed with exit code 0:

| Check | Result |
|---|---|
| Visual freeze manifest | 14 files OK |
| Static asset integrity manifest | 3 files OK |
| Focused Step 3 suite | 30 passed |
| Supporting non-database suite | 69 passed, 64 deselected-by-runtime skips because `TEST_DATABASE_URL` is absent |
| Combined required suite | 99 passed, 64 database-dependent skips |
| Python compilation | passed |
| `git diff --check` | passed |

Passing execution does not close B1 or B2 because the affected tests do not
exercise the required adverse conditions correctly.

## Digest evidence after Gemini remediation

| File | SHA-256 |
|---|---|
| `adapters/web/templates/base.html` | `3048bd5bb561dfc5f26bfbf30353f7ddd474d804ebe65c2c5349a1b2f5566585` |
| `tests/web/test_p3_4_shell_and_components.py` | `b195c5f11b0fd1084a0ffa2f2b7095820c0ef6be37d73376339e54b50823835f` |

## Verdict

This was the intermediate verdict. Gemini's authorized remediation 02 closed
B1 and B2; Codex independently re-reviewed the result with no findings, and
Peter accepted Step 3 on 2026-08-20. See
`phase-3-p3-4-step-03-review-and-acceptance.md`. Step 4 remains unreleased.
