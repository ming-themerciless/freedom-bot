# Security-focused review — Phase 2 I-03

Reviewer: Codex, Security Reviewer
Date: 2026-08-04
State reviewed: uncommitted working tree on `docs/platform-plan`, `HEAD` at `c8a3da9`

## Recommendation

**Do not issue a real module credential or proceed to either supervised
rehearsal.** Two confidentiality/control findings are Blocking and require an
independent security re-review. This is a recommendation only; Peter Duscha
records the decision.

## Findings

### S-B-1 — Blocking — The bearer credential is stored in client-readable world configuration

The full reusable bearer credential is stored as a Foundry world setting
(`foundry-module/scripts/settings.js:51-64`) and is retrieved through the client
`game.settings.get` API (`settings.js:71-85`). `config: false` only keeps it out
of Foundry's settings form, and the implementation's cited Foundry control is
write authorization (`SETTINGS_MODIFY`); neither is a confidentiality boundary
for a value delivered to browser clients. `main.js` conditionally hides the
button from non-GMs, but client-side UI gating does not prevent a connected user
or browser extension from reading client state.

Impact: a bearer secret intended for a GM-operated submitter can be exposed to
other clients of the world. The credential is submit-only, so compromise cannot
apply game state, but it can submit attacker-crafted valid pending artifacts,
consume restricted storage and database/audit capacity, and create misleading
provenance under the configured principal. A bearer credential knowingly placed
outside a demonstrated confidentiality boundary is an authentication defect and
is Blocking under plan §16.4.

Required remediation: do not persist the reusable secret in a setting exposed to
ordinary browser clients. Establish and document a server-side or otherwise
GM-confidential credential delivery/storage mechanism, or replace the design
with short-lived/restricted proof that does not distribute a reusable bearer to
all clients. Add a real Foundry authorization/confidentiality check demonstrating
which roles can retrieve the value; write permission tests are insufficient.
Rotate any credential used during development or rehearsal after remediation.

### S-B-2 — Blocking — Existing artifact roots and files are accepted without enforcing confidentiality

`_ensure_root()` calls `mkdir(mode=0o700, exist_ok=True)` but never checks or
corrects the mode of an existing directory
(`adapters/artifacts/filesystem.py:190-194`). Likewise, when a checksum-named
target already exists, the store verifies only its content and accepts it without
checking that it is a regular, service-owned `0600` file
(`filesystem.py:112-117`, `196-202`). The permission test creates a fresh
temporary root, so it cannot catch either case.

Impact: startup and submission can succeed while the configured root is
traversable/listable by other accounts, or while a pre-existing artifact
containing every exported Actor's mechanics is readable by them. This violates
the package's restricted-storage guarantee and is a confidentiality defect.

Required remediation: fail closed at startup/store time unless the root and
every accepted existing target have the required ownership, type and restrictive
mode (or deliberately repair them under a documented safe ownership policy).
Use no-follow/stat checks appropriate to the supported platform. Add tests for a
pre-existing permissive root, permissive target, non-regular target and symlink.

### S-I-1 — Important — Browser CORS policy is absent and its eventual security boundary is unspecified

The direct module call is cross-origin browser `fetch` with authorization and
custom headers, yet the API has no preflight implementation or allowed-origin
policy (`adapters/http/wsgi.py:85-96`, `165-170`). This currently breaks the
workflow (implementation finding B-1). A rushed fix can also broaden who may
drive the bearer-bearing browser request.

Required remediation: name the exact trusted Foundry origin(s), return a bounded
preflight response only for the submission route/method/headers, and test denied
origins as well as allowed ones. Keep `credentials: "omit"`; do not reflect
arbitrary origins and do not add cookie authority to this endpoint.

## Security conclusions without findings

- SHA-256 is acceptable for a genuinely random, high-entropy machine secret;
  this is not a human password. The minimum length is checked at issuance and
  presentation, and digest comparison is constant-time.
- `<id>.<secret>` is unambiguous because service-principal IDs exclude `.`.
- Uniform authentication errors are appropriate. Authentication attempts should
  be rate-limited and monitored at the proxy; permitting anonymous callers to
  append permanent audit rows would be worse.
- The adapter checks authentication and declared size before reading the body,
  requires `Content-Length`, and does not read beyond it.
- Audit payloads use closed fields and digest the idempotency key; I found no
  path, raw artifact, Actor value, or credential written into the new audit
  payloads.
- Temporary files are created `0600`, written and verified before atomic rename.
  No partial file is published under the checksum name.
- Folder names are inserted with DOM `textContent`; I found no HTML injection
  path in the dialog construction.
- HTTPS enforcement and the literal `localhost`/`127.0.0.1` HTTP exception are
  appropriately narrow for the documented same-host rehearsal.

## Verification boundary

I inspected repository source only. I did not access prohibited Foundry world
storage, LevelDB, or compendium data; did not run either rehearsal; and did not
commit or push.
