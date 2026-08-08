# Phase 2 supervised Foundry rehearsal — 2026-08-06

Status: IN PROGRESS — no gate decision recorded

Data Owner and supervising maintainer: Peter Duscha
Target database: `freedom_test` only
Foundry origin: `https://foundry1.rpgworld.org`
Foundry world ID: `the-guild`
Module ID and version: `freedom-blades-export` 1.0.0 initially; 1.0.1 during
the remediated rerun; 1.0.2 is prepared locally but has not been installed or
rehearsed
Field-profile version: `2026-08-03.1`

This record contains only operational outcomes, stable identifiers, counts and
checksums. It must not contain a credential, Actor name, mechanic, raw snapshot,
downloaded JSON, authorization header, database dump or browser-console output.

## A. Preconditions and server-half smoke test

- [x] Working-tree changes preserved.
- [x] Module installed, discovered and enabled only on Foundry 1.
- [x] GM dialog opened and deployment tuple matched the target world.
- [x] `freedom_test` confirmed at migration `0004` with zero snapshot, import,
      character, audit and idempotency rows before the rehearsal.
- [x] Synthetic smoke test: first submission HTTP `201`.
- [x] Synthetic smoke test: duplicate submission HTTP `200`, `duplicate: true`,
      and the same snapshot ID.
- [x] Exactly one `<SHA-256>.json` artifact with mode `0600`.
- [x] No `.incoming-*` artifact remains.
- [x] Submission alone created zero characters and zero imports.
- [x] Smoke-test state removed and empty baseline restored.

Safe note: two initial startup attempts failed closed before accepting a
request. The first temporary artifact directory was absent; the second used an
untrusted temporary-directory ancestry. Both attempts ran their cleanup and
left the disposable database empty. No Foundry data was submitted.

Successful smoke-test result: first HTTP `201`; duplicate HTTP `200` with
`duplicate: true` and the same snapshot ID; one `0600` artifact; no incoming
leftover; database counts during submission were characters `0`, imports `0`,
snapshots `1`. Immediate cleanup restored all recorded disposable tables and
the artifact root to zero entries.

## B. Inactive-folder transport rehearsal

- [x] Folder selected: `Characters (inactive)` or another explicitly approved
      non-live Actor folder.
- Stable folder ID: `9tMjaPtScBEmWuVd`
- Direct Actor count: 35
- Downloaded artifact SHA-256:
  `c058ba593f899e5110f5a7d9d850741db1afac32fefc5fc086e47447bfb5363e`
- [x] Download fallback completed without a credential using remediated module
      version `1.0.1`; the file remains only on the maintainer's Mac and was not
      opened, uploaded or committed.
- [x] Empty credential refused locally with `missing_credential`; the rehearsal
      endpoint was stopped and no database or artifact state was created.
- [x] Synthetic credential submission returned HTTP `201` and a sanitized
      receipt after one locally corrected/reissued credential; the refused
      credential attempt returned HTTP `401` and created no state.
- [x] Receipt contained count 35 and checksum
      `6359abd5a670fa903c7d6d3b8c7ecdd547fad7a2a2f3da3a4f01c2bbdc85261a`,
      and no Actor data.
- [ ] Duplicate unchanged submission reported the same snapshot already held.
      **FAIL:** repeated UI submissions rebuilt the bundle with a new
      `exportedAt` value, producing a new checksum and HTTP `201` each time.
      Six pending snapshots were recorded before the endpoint was stopped:
      five for the 35-Actor inactive folder and one for the 32-Actor active
      folder. Imports, characters and external mappings remained zero.
- [ ] Download, receipt, stored artifact and database checksums agreed.
- [ ] Preview succeeded against `freedom_test` within the accepted 5-second
      threshold.
- [ ] Foundry Actor, Item, Folder and `Actors (shared)` compendium counts did not
      change.

Earlier attempt: **FAIL — remediated in 1.0.1.** The download fallback initially
failed closed with `undefined_value` before producing an artifact. A real dnd5e 5.3.3
embedded Item contained an optional property whose JavaScript value was
`undefined`; canonical JSON deliberately refuses that value rather than
silently dropping it. No Actor name, mechanic or raw value is recorded here.
The synthetic fixtures did not model this real document shape. No download or
submission occurred, and no disposable database or artifact state was created.

*Undefined-value remediation status (2026-08-06)*: Module version `1.0.1` implements pure
boundary projection (`projectFoundryData`) in `world-source.js`. Optional
`undefined` object properties are skipped while constructing a new projected
result (source object and properties are unchanged), while array `undefined`
elements and canonical encoder inputs continue to refuse fail-closed. Prior
remediations established dynamic key redaction, `MAX_DEPTH = 64` bounds, a
testable non-overridable `dispatchWorkflow` dispatcher, fixed-prose error
messages, and non-mutation documentation. The fourth remediation replaced the
module-private mutable `Set` with a private `Object.freeze([...])` string array
allowlist (`SAFE_STRUCTURAL_KEYS`) queried via `.includes()`, ensuring
immutability by construction. Node test suite (`101 passed`) and Python suites
verified clean. That remediation was installed and allowed the later download
and submissions recorded above.

Current result: **FAIL — prepared-snapshot lifecycle remediation completed locally; independent review required.** Repeated unchanged submissions in version 1.0.1 used different `exportedAt` values, checksums and idempotency keys, creating six pending snapshots. Local version `1.0.2` has been fully remediated with a bounded `PreparedSnapshotState`, canonical content fingerprinting, transition-level failure disposition classification (`local_refusal`, `definitive_refusal`, `retry_same_key`, `delivery_indeterminate`), generation-based compare-and-set protection against stale overlapping completions, and 106 passed node tests. Version 1.0.2 has not been installed or rehearsed on the server. No preview may use the real pending snapshots from this failed run; the disposable server and database state were removed.

## C. Credential-confidentiality observation

- [x] Credential field was masked, empty and not pre-filled when reopened.
- GM Freedom Blades secret-shaped settings count: 0
- Ordinary player received secret: false
- [ ] Synthetic credential revoked after the browser checks.

Result: PENDING

## D. Real-browser origin observation

- Allowed origin: `https://foundry1.rpgworld.org`
- [x] Allowed preflight returned HTTP `204` with the exact allowed origin.
- [x] Following POST succeeded with HTTP `201` and produced a receipt.
- [ ] Removed-origin preflight was refused and no successful POST occurred.
- [ ] Allowed origin restored only for the remainder of the supervised session.

Result: PENDING

## E. Active-folder Phase 2 gate preview

- [x] Target reconfirmed as `freedom_test` for submission; preview remains
      pending.
- Stable folder ID: `smob5eya6XVBAuIb`
- Direct Actor count: 32
- Snapshot SHA-256:
  `1a39c3edb38006f8ac07e116e48f228d850f77e03714ee0b7a2d57f8c5fd9931`
- Exporter version: `1.0.1`
- Preview runtime: PENDING
- Mapped count/stable IDs: PENDING
- Create-candidate count/stable IDs: PENDING
- Explicitly unresolved count/stable IDs and safe reasons: PENDING
- [ ] Disposition counts total exactly the selected-folder Actor count.
- [ ] Zero unexplained identity discrepancies.
- [ ] Preview created no character, mapping or game-state changes.
- [ ] No raw artifact, Actor data, credential or unsafe report entered Git.

Result: PENDING

The active-folder snapshot was submitted unintentionally while attempting the
duplicate check. This is safe pending-only evidence: the endpoint cannot apply
an import, and immediate database verification showed zero imports, characters
and external mappings. It must not be previewed until the duplicate-submission
defect is resolved or explicitly dispositioned.

## F. Immediate verification and cleanup

- [x] Endpoint stopped.
- [x] Synthetic credential revoked by stopping the only process configured with
      its digest.
- [x] `freedom_test` returned to migration head with no rehearsal rows.
- [x] Disposable server artifacts absent. The fallback download recorded in
      section B remains only on the maintainer's Mac under the stated handling
      restriction.
- [ ] No unexpected `.incoming-*` entry.
- [ ] Git hygiene and `git diff --check` clean for rehearsal-generated data.

Overall rehearsal result: **FAIL — the `undefined_value` defect was remediated,
but duplicate prepared-snapshot lifecycle handling remains under remediation.
Version 1.0.2 requires correction and independent review before installation or
a complete rehearsal rerun. No Phase 2 gate decision is recorded.**
