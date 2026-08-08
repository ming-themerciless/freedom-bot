# Freedom Blades — Snapshot Submission (Foundry v14 module)

Submits an immutable, read-only snapshot of **one Actor folder** to the Freedom
Blades platform over HTTPS.

Operations, installation, configuration, credential rotation and the two
maintainer-run rehearsals are documented in
[`docs/operations/foundry-snapshot-submission.md`](../docs/operations/foundry-snapshot-submission.md).
The artifact's format is
[`docs/rules/foundry-export-contract.md`](../docs/rules/foundry-export-contract.md).

## What it does, and what it never does

| Does | Never does |
|---|---|
| reads world Actors through `game.actors` | reads LevelDB, world storage or a compendium |
| reads folders through `game.folders` | reads the `Actors (shared)` compendium |
| builds and validates the whole bundle locally | creates, updates or deletes any Foundry document |
| computes SHA-256 over the exact bytes | writes to the filesystem, except the fallback download |
| uploads those exact bytes over HTTPS | applies anything to the platform |
| offers a browser download of the same bytes | displays or logs Actor names, mechanics or raw JSON |

A submission creates a **pending** artifact. Applying it is a separate,
explicitly confirmed action by a currently authorized Guild Council member.

## The credential is entered per submission and stored nowhere

**There is no credential setting, and there must never be one.** A Foundry
world setting's *value* is delivered to every client that joins the world,
whatever its role: the server builds each user's world payload with an
unfiltered `db.Setting.dump()` (`dist/packages/world.mjs`), and the client's
`game.settings.storage.get("world")` is that delivered collection. `config:
false` only keeps a value out of the settings *form*, and `SETTINGS_MODIFY`
governs **writes**. Neither is a read boundary, and Foundry 14.365 offers no
setting option that is one — `client` scope is browser `localStorage`, and
`world` and `user` scope are both Setting documents vended by the same
unfiltered dump.

So the submitting GM enters the credential in the submission dialog, once per
submission. It lives in one local variable for the duration of one `fetch` and
is never written to a setting, `localStorage`, a flag, a document, a
notification, a log or a receipt. `tests/settings.test.mjs` fails if that ever
changes.

Keep the credential in a password manager. Rotation, revocation and the
consequence of a compromised GM device are in the operations document §5.3.

## Authority

A Foundry GM role is the authority to *read* every Actor in this world. It is
**not** proof of Discord Guild Council membership, and the module never claims
otherwise. Three authorities stay separate:

| Authority | May |
|---|---|
| Foundry GM | read and submit the selected folder |
| the submit-only service principal | upload a snapshot, and nothing else |
| a Guild Council member | preview and, separately, apply |

## Layout

| File | Foundry? | Purpose |
|---|---|---|
| `scripts/canonical.js` | no | canonical JSON encoding (contract §1) |
| `scripts/bundle.js` | no | bundle assembly and every structural bound |
| `scripts/transport.js` | no | SHA-256, HTTPS upload, idempotency key |
| `scripts/workflow.js` | no | the order the steps happen in |
| `scripts/world-source.js` | **yes** | the only file that reads Foundry (implements boundary projection `projectFoundryData` for optional `undefined` properties) |
| `scripts/settings.js` | **yes** | world-scoped configuration — endpoint and version tuple, **never a secret** |
| `scripts/main.js` | **yes** | the Actor Directory button, the dialog and the per-submission credential prompt |

Everything marked *no* is pure and tested without a running Foundry instance.

## Tests

```bash
cd foundry-module && node --test "tests/*.test.mjs"
```

No npm, no install step, no bundler and no dependency. `package.json` exists
only to declare `"type": "module"` so Node parses the same `.js` files Foundry
loads; it has no dependencies and no lockfile.

`tests/emit-golden.mjs` is run by `tests/test_exporter_contract.py` on the Python
side: it emits a synthetic bundle through the exporter's *real* serialization
path so the Manager's real parser can consume it. That is the control against
the two implementations drifting apart.

The Actor Directory button, the dialog and the download fallback need a running
Foundry client and are covered by the manual smoke test in the operations
document, not by an automated test.

## Foundry APIs used

Every one was verified against the installed Foundry **14.365.0** application
source rather than from memory; the table is in the header comment of
`scripts/world-source.js` and `scripts/main.js`, naming the file each was found
in. No private underscored internal is used where a public API exists.
