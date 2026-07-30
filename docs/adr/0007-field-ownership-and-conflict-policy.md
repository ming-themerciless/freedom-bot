# ADR 0007 — Field ownership and conflict policy

Status: **Accepted** — approved by the maintainer 2026-07-30. That satisfies the
Phase 0 acceptance criterion *"maintainer approves architecture ADRs"* (plan §12).
The independent Codex review required by plan §16.4 approved Phase 0 on
2026-07-30, and the maintainer accepted the milestone. This ADR is the contract
Phase 1 will be reviewed against.

Date: 2026-07-29

## Context

Three systems will hold overlapping character data: the Google Sheet (current
authority), Foundry `The Guild` (where players maintain their own sheets), and
PostgreSQL (the future authority). Plan §6.1 requires a field-ownership matrix
before writes are enabled; plan §6.2 forbids silent bidirectional
last-write-wins.

Plan §20 lists field ownership among the ADRs to write. The matrix itself is
[rules/field-ownership.md](../rules/field-ownership.md); this ADR records the
*policy* — how ownership is decided, enforced and changed.

## Decision

### Every synced field has exactly one recorded owner

The classes are plan §6.1's: Foundry-owned, Database-owned, Council-approved
shared, Derived, Display-only, plus External mapping for identity linkage.

A field with no recorded owner is **Database-owned by default and never
overwritten by an import.** An unlisted field is an unanalysed field, and the
safe failure mode for an unanalysed field is to leave it alone.

### Ownership is data, not code

Field ownership lives in a versioned table the Council can inspect, and every
`sync_difference` records the owner that applied at detection time. A rule that
only exists as an `if` statement in an adapter cannot be audited, and cannot
explain why a past decision was made the way it was.

### The conflict record

Per plan §6.2, every detected difference records external value, internal value,
field owner, external record and version, internal version, detection time,
proposed action, conflict state, and resolution with approver.

### Resolution by class

| Owner | On difference |
|---|---|
| Foundry-owned | May refresh automatically **only after** the mapping and validation rules for that field are approved. Until then: record, do not apply |
| Database-owned | **Never** overwritten by an import. Record a warning; the Council may push the platform value outward once outbound sync exists |
| Council-approved shared | Generate an approval proposal. Nothing applies without approval |
| Derived | Recalculate from authoritative inputs. A difference means an input differs — resolve the input, not the derived value |
| Display-only | Refresh freely |
| External mapping | Council action only; never inferred |

### Three prohibitions

1. **No silent last-write-wins**, in either direction, for any field, ever.
2. **No import writes a live character record.** Imports write
   `sync_snapshots` and `sync_differences`. Applying a difference is a separate,
   approved, audited action.
3. **No automatic advancement.** Level, badge, mission count and any reward are
   never changed by a sync (`.agents/AGENTS.md`, plan §3 principle 4).

### Changing an ownership decision

An ownership change is a Council decision, recorded as a new version of the
matrix row with an effective date. Existing `sync_differences` keep the owner
that applied when they were detected — history is not retroactively reinterpreted.

### Enforcement point

Ownership is enforced in the **application service** that applies a difference,
not in the adapter that fetched it and not in the domain. The adapter cannot know
the policy; the domain must not know that Foundry exists.

This means an ownership violation is testable with a fake repository and no
external system, which is what makes plan §12 Phase 7's *"database-owned values
are not overwritten"* an automated check rather than a review promise.

## Consequences

**Positive.**

- The Council can see and change the policy without a code change.
- Every applied difference is attributable to a person, a policy version and a
  moment in time.
- The default-deny posture means an overlooked field fails safe.

**Negative.**

- More Council work: shared fields generate proposals, and there will be many of
  them early on because Foundry currency and platform currency diverge constantly
  by design.
- A migration is needed whenever a field's ownership changes, plus the versioned
  history rows.
- Read-only-first means players see differences they cannot resolve themselves.

**The main risk this creates.** If proposal volume is high enough, the Council
will be tempted to bulk-approve, which defeats the purpose. Phase 3's
reconciliation view should therefore group differences by field and by cause, and
Phase 6 should support an explicit, audited bulk decision rather than forcing
either one-by-one review or an unrecorded shortcut.

## Alternatives considered

**Foundry authoritative for everything mechanical.** Rejected: players edit their
own Foundry sheets (rules §6 p.14 says so explicitly), so this would let any
player mint gold, grant themselves a level or add a tool proficiency — directly
contradicting the no-automatic-advancement invariant.

**Platform authoritative for everything.** Rejected: the platform has no ability
scores, no class features and no inventory detail, and Foundry is where the
character actually exists at the table.

**Timestamp-based last-write-wins.** Rejected outright by plan §6.2. It is also
unworkable here: Foundry timestamps reflect when a player last edited their own
sheet, which carries no authority over a Council-approved settlement.

**Manual reconciliation with no automation.** This is the status quo, and it is
what the platform exists to replace. Rejected — but note that read-only Phase 7
is deliberately close to it, by design, until ownership is settled.
