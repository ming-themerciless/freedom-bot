# Maintainer review — field profile `2026-08-09.1`

Date: 2026-08-10 (Data Owner's local date; the evidence below is timestamped UTC
2026-08-09)
Reviewer: Peter Duscha, Data Owner
Subject: `domain/foundry_profile.py` and `docs/rules/field-ownership.md` at
profile version **`2026-08-09.1`**

Phase 2 acceptance requires that the field profile "is exhaustive, versioned,
**reviewed by a maintainer** and contains no unclassified supported field". The
first three were satisfiable by work; the fourth has never been recorded for any
version of this profile. This record supplies it.

## What was reviewed

- The complete classification in `domain/foundry_profile.py` at
  `2026-08-09.1`, and its prose counterpart `docs/rules/field-ownership.md`,
  which a test keeps in step with it.
- The distinction the profile is built on: **target ownership** versus **current
  authority**, and the consequence that almost every field is
  `legacy_authority_deferred` and names the package accountable for migrating
  it.
- The ten paths newly classified at this version (finding RA-1):
  `system.favorites`, `system.favorites[].{id,sort,type}` and
  `system.source.{book,custom,license,page,revision,rules}`, all
  `SNAPSHOT_ONLY` and owned by no package.

## Decision

**Accepted in full.** The classifications and package ownership are accepted as
they stand at `2026-08-09.1`. No field was disputed, no classification was
changed as a result of this review, and no correction is requested.

## The form this acceptance took, stated plainly

The Data Owner reviewed the change and accepted it as a whole, rather than
walking the matrix field by field in a recorded session. That is the honest
description and it is written here so that a later reader — or the Independent
Reviewer — can weigh it correctly rather than assume more than happened.

What gives the acceptance evidentiary weight is not the ceremony but two
independent observations from the same day, both against real data neither the
profile nor its author had seen:

- **Rehearsal A**, 35 Actors in a non-live folder, produced 35
  `unknown_snapshot_path` warnings against the *previous* version
  `2026-08-03.1`. That is what found RA-1 and produced the ten classifications.
- **Rehearsal B**, 32 Actors in `Characters (active)`, produced **zero**
  warnings against `2026-08-09.1` — a second real folder, containing Actors the
  first did not, with every path classified.

An exhaustiveness claim that survives two real folders it was not written
against is worth more than a line-by-line reading of a matrix, and it is the
evidence this acceptance rests on.

## What this does not do

- It does not close the Phase 2 gate, and no part of it should be read as a gate
  decision.
- It does not constitute the independent review required alongside it. The ten
  new classifications were proposed and implemented by Claude, who also raised
  RA-1; that work carries no independent review and goes to the Independent
  Reviewer with the rest of the Phase 2 evidence.
- It accepts `2026-08-09.1` only. Any later profile edit bumps the version and
  requires its own review, and makes every outstanding preview stale.
