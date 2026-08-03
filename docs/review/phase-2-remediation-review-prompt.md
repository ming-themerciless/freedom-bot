# Independent review request — Phase 2 remediation (packages R1–R4)

Prepared for: **Codex, as Independent Reviewer**
Prepared by: Claude, working Technical Lead and implementer of this work
Requested by: Peter Duscha, Acceptance Authority
Date: 2026-08-03
Commit under review: **`ba42467`** on branch `docs/platform-plan` (not pushed)

---

## 1. Your role, and its limits

You are the **Independent Reviewer** required by implementation plan §16.4 for
*import/reconciliation*. Plan §0.3 makes this a mandatory checkpoint: a reviewer
who did not implement the work is required, and if none is available the package
stays `deferred`.

You are also asked for a **separate, separately reported security-focused pass**
covering authorization, artifact handling, audit content and runtime grants
(ruling D-5, 2026-08-02). Please keep the two reports distinct rather than
merging them — a security concern absorbed into a general review is easy to lose.

**You recommend; you do not approve.** Peter Duscha records the gate decision.
Do not implement fixes: report findings and let the implementer address them,
so that the re-review has something independent to check.

Classify every finding per plan §16.4:

- **Blocking** — security, data loss, authorization, rule correctness,
  migration, atomicity or production reliability;
- **Important** — material maintainability, testing, performance or operational
  weakness;
- **Optional** — improvement that does not block the milestone.

Blocking findings must be fixed and re-reviewed before dependent work starts.

## 2. What this work was, in one paragraph

ADR 0008 proposed a profile-driven key/value store so Phase 2 could correct
every database-managed character field. The Acceptance Authority **rejected** it
on 2026-08-02 (OD-41, controlled baseline v1.1/v1.5): Phase 2 does not migrate
Sheet-era state, and each field group migrates once into the typed model its
owning package introduces. This work removes that store and everything built on
it, while preserving immutable snapshot ingestion, character identity, external
Actor mappings, deterministic reconciliation, provenance and audit — and adds
`legacy_authority_deferred` reporting in place of comparisons the platform has
no authority to make.

## 3. What to read

**Governing, in this order:**

1. `.agents/AGENTS.md`
2. `docs/implementation-plan.md` §§6.1–6.5, §7.3, §12 Phase 2, §13.3, §16.4
3. `docs/review/phase-2-v1.5-remediation-plan.md` — the accepted plan this
   implements, including thresholds T-1…T-12 in §8
4. `docs/review/phase-2-remediation-submission.md` — the evidence record, with
   traceability in §5 and exact commands in §6
5. `docs/discovery/open-decisions.md` OD-41 and **OD-42**
6. `docs/adr/0006-foundry-integration-boundary.md` (accepted) and
   `docs/adr/0008-profile-driven-character-state.md` (rejected, retained)

**Superseded, for context only — do not review against these:**
`docs/review/phase-2-package-plan.md`, `docs/review/phase-2-i-02-submission.md`.

**Code:** `git show --stat ba42467`, then `domain/field_profile.py`,
`domain/foundry_profile.py`, `application/foundry/reconciliation.py`,
`application/foundry/import_service.py`,
`migrations/versions/0002_foundry_snapshot_and_identity.py`,
`infra/postgresql/runtime-grants.sql.tmpl`.

## 4. Constraints on your review

- **Do not read the maintainer-authorized exports** at
  `/opt/discord-bots/foundry-actor-exports`. The supervised rehearsal is a
  separate maintainer action and has not happened.
- **Do not access Foundry's live storage** at
  `/home/foundry/shared/worlds/the-guild/data/actors`. Direct LevelDB reads are
  prohibited in every phase.
- Destructive database work belongs on the disposable `freedom_test` only.
  Note that `freedom_dev` exists and is currently empty; do not drill it.
- Nothing is pushed. Do not push.

## 5. Where I think this is weakest — please start here

These are my own judgement calls and known soft spots. I would rather you spend
your time here than rediscover them.

### 5.1 `character.display_name` is the only field with database authority

Every other profile field is `legacy_authority_deferred`. I classified this one
as `database_authority` because **the import writes it itself** at character
creation from the Actor name, so comparing a later snapshot against it is a
comparison against a value from the same source rather than a fabricated one.

The counter-argument, which I did not take: `data-migration-register.md`
allocates `character.display_name` (Characters column A) to package **5.1** and
marks it `Legacy`, so arguably it should be deferred like the rest, with rename
detection reported some other way.

Two sources write one column, and 5.1 will have to resolve that. **Is my
classification right, and if so is the report's rename semantics right?** Note
the direction inverts here: Foundry is where players rename, so a difference
means the *platform* record is stale, not that the Foundry Actor is out of date.

### 5.2 The profile shrank from 30 fields to 13

Fields with no snapshot path — Moradinium, living-cost weeks, no-shows, artisan
ranks, downtime progress and 16 others — were removed from the profile entirely,
because they existed in it only to be correctable. They are governed by the
migration register instead, and `field-ownership.md` §5 accounts for them.

Plan §12 Phase 2 requires the profile to be *"exhaustive… contains no
unclassified supported field"*. I read exhaustive as **over supported snapshot
paths**, which I believe still holds. **Please confirm that reading**, and that
nothing became unreviewable by leaving the profile.

### 5.3 A deferred row reports presence, not the value

`DeferredField` carries `snapshot_has_value: bool` and an unavailability reason
— never what Foundry holds. Rationale: nothing in Phase 2 can act on the value,
and omitting it keeps Actor field data out of the reconciliation summary and the
audit record built from it.

I hit a contradiction between my own documents here (the plan said "presence",
an earlier draft of `field-ownership.md` said "what Foundry holds") and resolved
toward presence. **Is that the right call, or does it make the report too thin
for a Council member to act on?**

### 5.4 The preview binding — is there a third defect?

Two defects were found here during I-02 and fixed. I then changed the binding's
shape again: it now covers checksum, world id, folder id, **folder path**,
profile version, **exporter schema**, aggregate versions and request key, with
`differences()` generated from a field→description table so an unreported bound
input fails a test.

What I convinced myself of, and would like checked independently:

- a **new mapping** appearing between preview and apply changes
  `aggregate_versions`, so it is caught;
- a **deleted character** produces a dangling mapping, so `report.blocked`
  catches it;
- a **new colliding display name** created between preview and apply is *not*
  visible in `aggregate_versions` (the new character is unmapped), and is caught
  only because `report.blocked` is recomputed at apply. **That is a different
  mechanism from the binding — please verify the reasoning holds.**
- `BundleLimits` and the supported deployment tuple are constructor state, not
  bound. A change to either makes `parse()` refuse at apply rather than
  producing a stale-preview result. **Is refusal-instead-of-staleness correct
  here?**

### 5.5 `_DATABASE_VALUES` raises at runtime

`application/foundry/reconciliation.py` holds a one-entry table mapping a
comparable field to a reader, and raises `LookupError` if a field claims
database authority with no reader. That is a runtime failure in reconciliation.
**Should it instead be a profile-construction invariant**, so the condition is
impossible rather than merely detected?

### 5.6 My guards matched prose four times

Four separate tests I wrote scanned raw text and flagged documentation that
*explained* what had been removed. Each is now AST-based or scoped. The pattern
is worth a sweep: **is any remaining guard still too loose — or worse, too tight
in a way that produces false confidence?**

Specifically, `tests/test_rejected_scope_absent.py` uses `ast.unparse` to strip
docstrings. A table name assembled by string concatenation would evade it.
Whether that matters is your call.

### 5.7 The audit-payload allowlist may be circular

`test_the_audit_payload_contains_only_allowlisted_keys` asserts the payload
contains only allowlisted keys — but I built the allowlist from what the code
currently emits. **Please check it reads as policy rather than as a description
of current behaviour**, and that nothing in it should not be there.

### 5.8 Migration 0002 was replaced in place

Rather than corrected by a follow-on migration. Justification: it was never
committed and existed only in the disposable database, so plan §14.3's "applied
migrations are never edited" did not attach. **Please confirm that reasoning**,
and that `docs/operations/foundry-snapshot-import.md` §8's guidance — recreate
rather than migrate any database built from the old revision — is sufficient.

## 6. What the evidence covers, and what it does not

**Covered, and re-runnable:**

- 1431 tests against PostgreSQL, **no skips**;
- live restricted-role denial: all 12 combinations of `UPDATE`/`DELETE`/
  `TRUNCATE` × four append-only tables refused with SQLSTATE `42501`, with the
  grants template applied by the test fixture itself;
- `upgrade → downgrade → upgrade` plus `alembic check`;
- backup → drop schema → restore → inventory comparison → idempotent rerun;
- injected failure at each of five write points, proving no partial commit.

**Not covered, and not claimed:**

- the supervised real-export rehearsal and the Data Owner attestation;
- the §9.4 operational windows (rehearsal window, observation period,
  preview/apply runtime budget), which are unset;
- formatter, linter and type checker — none is configured in this repository.

**Two operator errors during R4** are recorded in submission §8.1: the
disposable database was dropped without confirming it could be recreated, and
the backup drill was first run against `freedom_dev` (which was empty, so
nothing was destroyed). Both were mine. Please judge whether they indicate
anything about the procedures themselves rather than only about their operator.

## 7. Specific questions for the security pass

1. Is there **any** path — service API, repository, CLI, migration, profile
   classification — by which a snapshot value can reach a character game-state
   field? The claim is that there is none.
2. Does the reconciliation report or the audit payload leak Actor field data?
   The deferred row is designed not to; the summary carries counts, field keys
   and owning packages.
3. Is current-role authorization genuinely resolved **at apply** rather than
   carried from the preview, and does Platform Administrator alone confer
   nothing?
4. Do the rewritten runtime grants leave any append-only table mutable? A grant
   on a dropped table is harmless; a missing `REVOKE` on a retained one is not.
5. Does a refusal disclose what it would have changed, or leak artifact content,
   a traceback or a connection string?
6. Are the inherited artifact bounds (64 MiB, depth 64, ≤500 Actors, ≤64
   folders, 1–8 selected, ≤4000 items/Actor) still enforced before parsing?

## 8. What to produce

- a findings list, each classified Blocking / Important / Optional, with file
  and line;
- a separate security-pass report;
- an explicit answer on each of §5.1–5.8 and §7.1–7.6, even where the answer is
  "no concern"; and
- a recommendation to the Acceptance Authority: proceed to the supervised
  rehearsal, or remediate first.

Please do not recommend closing the Phase 2 gate. The rehearsal, the attestation
and the §9.4 windows are outstanding regardless of your findings, and the gate
decision is Peter's to record.
