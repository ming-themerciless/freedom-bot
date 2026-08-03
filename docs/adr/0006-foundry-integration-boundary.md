# ADR 0006 — Foundry integration boundary

Status: **Accepted, amended 2026-08-02.** Approved by the maintainer 2026-07-30,
which satisfies the Phase 0 acceptance criterion *"maintainer approves
architecture ADRs"* (plan §12). The independent Codex review required by plan
§16.4 approved Phase 0 on 2026-07-30, and the maintainer accepted the milestone.

**Amendment 2026-08-02** supersedes two parts of this ADR — the outright
rejection of offline snapshot import, and the claim that an Actor export cannot
carry a real `_id`. Everything else stands unchanged. The amendment is recorded
in [§ Amendment 2026-08-02](#amendment-2026-08-02--the-offline-snapshot-artifact)
below rather than by rewriting the original reasoning, because the reasoning was
sound for the artifact it was about.

Date: 2026-07-29

## Context

Plan §6.3 and §12 Phase 7 require a narrow, authenticated, versioned Foundry
integration. `.agents/AGENTS.md` forbids direct LevelDB reads or writes as the
production integration.

Phase 0 discovery ([foundry-mapping.md](../discovery/foundry-mapping.md)) confirmed
the deployment baseline from the manifests — world `the-guild`, title `The Guild`,
core `14.365`, system `dnd5e` `5.3.3` — and found one thing the plan did not
anticipate: **three Foundry instances run on this host**, on ports 30001–30003,
each exposing a world directory named `the-guild`. Phase 0 initially read that as
three separate worlds; the maintainer clarified on 2026-07-30 that
`/home/foundry/shared/worlds` is bind-mounted into all three, so it is **one world
with three front doors**. The decisions below reflect the corrected topology.

It also confirmed that all three world databases are held open by running
servers, which makes an offline snapshot read unsafe as well as unauthorized.

## Decision

### Foundry is an external client

It never receives a database credential, a database connection, or any secret
beyond its own scoped service-principal token. Data flows through a versioned
HTTPS API that this application exposes and the Foundry module consumes.

```text
Foundry module ──HTTPS──> /api/v1/foundry/* ──> application services ──> domain
     (client)              (this application)
```

The module is a client of the platform. The platform is never a client of
Foundry's internals.

### No LevelDB access in production, in either direction

Not for reads, not for writes, not "just for the import". The world stores are
live. An offline read-only snapshot is permitted **only** for
maintainer-authorized discovery (`.agents/AGENTS.md`) and never as a production
code path.

> **Unchanged by the 2026-08-02 amendment.** The Phase 2 snapshot artifact is
> produced *inside* Foundry through supported document APIs and handed to the
> Manager. Nothing in this repository opens a world directory, and no phase does.

### The world is the identity; the instance is a transport endpoint

*Revised 2026-07-30 on a maintainer answer, which corrected the topology this
section originally assumed.* Phase 0 reported three instances each holding a
`the-guild` world and concluded that an authoritative instance had to be chosen.
That was wrong: `/home/foundry/shared/worlds` is bind-mounted into all three
instances, so there is **one** world seen three times (verified by inode; see
[foundry-mapping.md §3](../discovery/foundry-mapping.md#3-topology-one-shared-world-behind-three-instances)).

Therefore:

- `external_worlds` keys on **world ID**, not (instance, world ID). There is no
  stale parallel copy to guard against, and composing the instance into the
  identity would falsely split one world into three.
- The instance is **connection configuration** — a base URL. It must be
  repointable without any change to world or actor identity, because LevelDB's
  exclusive lock means only one instance can host the world at a time and it need
  not always be the same one.
- **One service principal**, not three, because there is one world.

[OD-12](../discovery/open-decisions.md) is closed by this correction rather than
by a choice.

### Version compatibility is a tuple, and mismatch fails safely

Compatibility is keyed on **(core version, system version)** together. The
manifests give `core 14.365` with the system declaring `compatibility.verified:
"14"` and `minimum: "13.347"` — neither value alone identifies a supported
deployment.

Every request carries both versions and the API schema version. An unsupported
combination **fails the sync with a clear diagnostic**. It does not degrade, does
not guess, and does not partially import. Plan §12 Phase 7: *"unsupported
versions fail safely."*

**Supported range, decided 2026-07-30 ([OD-14](../discovery/open-decisions.md)):**
exactly the deployed tuple — core `14.365`, `dnd5e` `5.3.3` — held in
configuration rather than hard-coded. This connector serves **one deployment and
is not distributed**, so no backwards compatibility is owed. A Foundry or system
upgrade deliberately stops the sync until the new tuple is validated and the
configured value updated; that visible checkpoint is the feature. The per-instance
upgrade path makes this concrete: one instance can be upgraded against the shared
world while the others are not, so the connector can meet an unexpected tuple even
though the world itself never changed.

### One-way, read-only first

Phase 7 delivers **snapshots into the platform only**. No write to Foundry, for
any field, before Phase 7's review gate closes and
[field-ownership.md](../rules/field-ownership.md) has no UNRESOLVED rows.

An imported value lands in `sync_snapshots` and generates `sync_differences`. It
does not update a live character record. Applying a difference is a Council
action through the approval centre (plan §12 Phase 6).

### Idempotency

A snapshot is keyed on **(world ID, actor `_id`, content hash)** — *revised
2026-07-30; the instance is deliberately not part of the key.* Including it would
mean the same unchanged actor, submitted through a different front door to the same
shared world, counted as a new snapshot. Idempotency must hold across instances,
because there is only one world behind them.
Re-submitting an identical snapshot is a no-op that returns the original result.
Plan §12 Phase 7: *"duplicate snapshots are idempotent."*

The Foundry actor `_id` is a **mapping key, not an identity**. It does not survive
a world rebuild, so `external_actor_mappings` also stores a human-verifiable
fingerprint — name plus class and level at mapping time — to support re-linking
after one.

### Credentials

**One service principal for the Foundry connector** — revised 2026-07-30 from
"one per instance", since there is one shared world rather than three. It is
scoped to snapshot submission only, revocable, and rotatable without redeploying
the application. No administrator credential and no database secret is ever
shipped in a Foundry module — the module runs on clients the platform does not
control.

### Mapping is Council-established, never inferred

A Foundry actor is linked to a platform character by an explicit, audited Council
action. Never by name matching. Names are mutable display values, and the Sheet's
name-based lookup already demonstrates the failure mode.

This makes Council character-link management (plan §12 Phase 3) a hard
prerequisite for Phase 7 — which the plan's phase ordering already reflects.

## Amendment 2026-08-02 — the offline snapshot artifact

The maintainer ruled that **the Manager never reads live Foundry and never reads
Foundry LevelDB; a Guild Council member deliberately creates an offline snapshot
artifact**, and that Phase 2 imports from that artifact. Two statements in this
ADR conflict with that ruling and are superseded here.

### Superseded 1 — "no offline snapshot import"

The *Alternatives considered* section rejected **offline LevelDB snapshot
import**. That rejection stands, in full: the world databases are open, the
format is a Foundry internal, and `.agents/AGENTS.md` forbids it. It was
rejecting a *LevelDB read*.

What replaces it is a different artifact with none of those properties: a
**Council-produced export bundle**, built inside the Foundry client through
supported document APIs (`game.actors`, `game.folders`, `Document#toObject()`),
handed to the Manager as a file. No world directory is opened, no storage format
is depended on, and the act of exporting is a deliberate, attributable Council
action rather than a background read.

The bundle's contract is
[docs/rules/foundry-export-contract.md](../rules/foundry-export-contract.md). It
is versioned, deterministically encoded, content-addressed by SHA-256 computed
before parsing, and bounded in size, depth, folder count and Actor count.

### Superseded 2 — "an export has no `_id`, so mappings cannot come from one"

Phase 0's finding **F-F1** was that both maintainer-supplied Actor exports
carried `"_id": null`, with the real ID surviving only in the filename
(`fvtt-Actor-…-52ywI3ttEcgf9iBv.json`). This ADR concluded that *"mappings cannot
be established from exports"*.

That is true of Foundry's **per-Actor export**, and remains true. It is not true
of a bundle built through `Document#toObject()`, which carries the real `_id`.
The contract therefore **requires** every Actor to carry its real 16-character
Foundry `_id`, and refuses a missing, null, malformed or duplicated one as a
blocking issue. A hand-saved per-Actor export fails that check and is refused —
which is the correct outcome, because it is exactly the file whose identity is
only in its filename.

The conclusion F-F1 supported — **never establish a mapping by name matching** —
is unchanged and is enforced in code.

### What this amendment does **not** change

Every one of these is carried forward intact:

- **no LevelDB access**, for reads or writes, in any phase;
- **no Manager-initiated live Foundry access** — Phase 2 touches no network at
  all, and Phase 7's connector is still module-and-HTTPS only;
- **the world ID, not the instance, defines world identity** — the bundle
  carries no instance, host or port, for the reason §*The world is the identity*
  gives;
- **exact (core, system) version validation, failing closed** — the bundle
  carries both and the Manager compares the tuple against configuration;
- **stable platform character IDs independent of Foundry IDs** — `characters.id`
  stays a platform UUID and the Foundry `_id` stays a mapping key in
  `external_actor_mappings`;
- **no Foundry write-back in this phase**, for any field. A database-owned
  difference produces a warning that the Foundry Actor is out of date and should
  be updated manually;
- **mapping is Council-established, never inferred from a name.**

### New in this amendment

- **Content-addressed immutability.** The artifact's SHA-256, computed before
  parsing, is the snapshot identity. Preview, import, mapping, reconciliation,
  correction and audit all bind to it. One changed byte is a different snapshot.
- **A bounded folder set, selected in the Manager.** The bundle carries 1–8
  deliberately exported Actor folders plus the ancestors needed to present a
  path; a Platform Administrator selects one in Phase 3 and a Council member
  confirms the exact preview. The reasoning is in the contract, §2.5.
- **Folder identity is (stable folder ID, displayed path)**, never the name
  alone — the same rule this ADR already applies to Actor names, one level up.
- **Idempotency for the offline artifact** is keyed on
  (snapshot checksum, selected folder ID, field-profile version). The Phase 7
  key of (world ID, actor `_id`, content hash) is unchanged and belongs to the
  live connector; the two are different inputs and deliberately have different
  keys.

## Consequences

**Positive.**

- Foundry compromise or misconfiguration cannot corrupt platform state: the worst
  case is a rejected or quarantined snapshot.
- Version mismatches surface as diagnostics rather than as silently wrong
  imports.
- Keying identity on the world rather than the instance means the connector is
  unaffected by which instance happens to be hosting `the-guild`.

**Negative.**

- A Foundry module must be written, versioned and kept compatible across Foundry
  upgrades. That is real ongoing maintenance the project does not have today —
  though the single-deployment version policy above bounds it: the module is not
  distributed and owes no third party compatibility.
- Pinning to one (core, system) tuple means a Foundry upgrade **stops the sync
  until the pin is updated.** Deliberate, but it must be on the upgrade checklist
  or it will be discovered at the wrong moment.
- Read-only first means players see reconciliation differences they cannot fix
  from Foundry. That is intended — it is the Council's queue — but it needs
  explaining to the community.
- Bastion facility data in Foundry is **incompletely maintained** — not every player
  fills it in (maintainer, 2026-07-30). A Foundry snapshot is therefore evidence of
  what *is* recorded, never proof of what exists, and no rule check may treat an
  absent facility as an absent facility.

## Alternatives considered

**Offline LevelDB snapshot import.** Tempting: no module to write, no Foundry
API to learn. Rejected — forbidden by `.agents/AGENTS.md` for production, the
databases are open, and it would couple the platform to Foundry's internal
storage format across versions. **Still rejected after the 2026-08-02
amendment**, which permits a Council-produced *export bundle* and nothing else;
see that section for why the two are not the same artifact.

**Foundry REST API module from the ecosystem.** A general-purpose remote-access
module would grant far broader access than snapshot submission needs, and its
credential would be a standing key to the whole world. A purpose-built module
with one narrow capability is a much smaller thing to get wrong.

**Bidirectional sync from the start.** Rejected: `.agents/AGENTS.md` requires
field-level ownership rules and conflict resolution first, and
[field-ownership.md §10](../rules/field-ownership.md#10-unresolved-summary) still
has seven unresolved groups.

**Composing the instance into world identity.** This was the original decision,
made on the belief that three separate `the-guild` worlds existed. **Withdrawn
2026-07-30**: the world is bind-mounted and shared, so keying on
(instance, world ID) would split one world into three phantom identities and
generate spurious `sync_differences` between them. Recorded here rather than
deleted, because the reasoning was sound and only the premise was wrong — and
because it is a good illustration of why §7 of
[foundry-mapping.md](../discovery/foundry-mapping.md#7-what-a-maintainer-must-supply)
insists on maintainer-verified structure instead of agent inference.
