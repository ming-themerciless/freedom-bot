# Rehearsal A findings — 2026-08-09

Source run: [`phase-2-supervised-rehearsal-2026-08-09.md`](phase-2-supervised-rehearsal-2026-08-09.md)
Observed by: Claude, with Peter Duscha supervising the browser half
Decision authority: Peter Duscha

Four findings. None was reachable from a synthetic fixture, and none was
produced by a test — each came from real data or a real browser. Numbered
`RA-*` so they do not collide with the `CL*` review series.

---

## RA-1 — the field profile is not exhaustive against the real world — **gate-relevant**

The preview of a 35-Actor real export produced **35 `unknown_snapshot_path`
warnings**. Profile `2026-08-03.1` does not classify:

- `system.favorites`
- `system.favorites[].id`, `.sort`, `.type`
- `system.source.book`, `.custom`, `.license`, `.page`, `.revision`, `.rules`

Behaviour is correct and fails closed: the paths are reported, never written,
and the run had 0 errors. But Phase 2 acceptance requires that the profile
"is exhaustive, versioned, reviewed by a maintainer and contains no unclassified
supported field", and that "every supported snapshot path and database field has
exactly one applicable profile/correction classification". Against the real
world, it does not.

These are almost certainly snapshot-only presentation and provenance fields
rather than anything the platform should own, so the likely resolution is an
explicit snapshot-only classification rather than new owned state. That is a
profile decision, not an implementation change.

**Disposition: CLASSIFIED, 2026-08-09.** All ten paths are now
`SNAPSHOT_ONLY` in profile **`2026-08-09.1`**: `system.favorites.*`,
`system.favorites[].*` (client presentation) and `system.source.*` (publisher
provenance). None gained an owning package, because none will ever become
platform state. `docs/rules/field-ownership.md` moved with the module — the
doc-sync test refused the change until it did — and fourteen tests pin the
observed paths and both favourites prefixes.

**Still outstanding:** the *maintainer review* of the profile, which Phase 2
acceptance has always required and which has never been recorded for any
version. The classification above is a proposal accepted by the Data Owner on
2026-08-09; the formal review record is a separate gate item.

## RA-2 — `canonical_encoding` cannot be true for any real world — **contract decision**

The submitted artifact was reported non-canonical. Investigated rather than
assumed: the bytes and the server's canonical form are the **same length**, with
identical non-ASCII counts and no escape differences. The sole divergence is key
order, in 54 objects, all of one shape:

```
.actors[].items[].system.advancement.<id>.configuration.scale
key order in the artifact: ["1", "4", "10"]
key order the server expects: ["1", "10", "4"]
```

These are dnd5e scale-value advancements keyed by class level. **JavaScript
orders integer-like object keys numerically and ahead of string keys** — an
ECMAScript property-order rule, not a module choice. `Object.keys()` returns
`["1","4","10"]` however the exporter sorts. `application/foundry/parser.py`
canonicalises with Python `sort_keys=True`, which is lexicographic.

So `canonical_encoding` is false for any world containing a class with a scale
advancement reaching level 10 — in practice, all of them. No amount of sorting in
the module can fix it.

**What is not affected:** two exports of an unchanged world still produce
identical bytes, because JS ordering is deterministic. Checksum-based duplicate
detection and snapshot identity are unaffected, and this rehearsal demonstrated
both. The warning text in `application/foundry/reconciliation.py` — "two exports
of an unchanged world will not compare equal until the exporter canonicalises its
output" — **misstates the consequence** and should be corrected whichever way the
contract goes.

**Disposition: RULED AND CLOSED, 2026-08-09.** Peter Duscha adopted ECMAScript
own-property order as the contract's canonical order — change-log **C-10**.
`docs/rules/foundry-export-contract.md` §1 and new §1.0 carry the rule,
`canonical_bytes` implements it, four parser tests pin it, and the misstated
warning text is corrected.

The mechanism was confirmed against the shipped module rather than inferred:
`canonical.js` sorts the key array to `["1","10","4"]` exactly as the old
contract demanded, then rebuilds an object, and the engine reorders it to
`["1","4","10"]` on insertion; the serialiser then walks `Object.keys`
deliberately unsorted. **The exporter always conformed to the rule the contract
should have stated**, so the module is unchanged and keeps version `1.0.5`.

One follow-up, deliberately not done today: the comment table in
`foundry-module/scripts/canonical.js:15` still describes the old rule. Editing
it would change the bytes of an installed, rehearsed build for a comment, which
CL3-I-2 is a reason not to do casually. It should ride along with the next
module change that bumps the version.

## RA-3 — a `401` on a large upload surfaces as `network_failure` — **diagnostic quality, bounded**

An authentication failure was observed end to end: the service answered `401`
before reading the 9.8 MB body and closed the connection while the client was
still uploading. The client therefore never received the `401` and reported a
lost connection. The operator-visible message was:

> The submission could not reach the Freedom Blades server. Nothing was
> confirmed. Submitting the same export again is safe.

That is true about arrival and useless as a diagnosis: the credential was
simply wrong, and every retry pins and fails identically. §9 already anticipates
the shape — "an empty or rotated credential … says nothing about whether the
earlier attempt arrived" — so the model is right; the operator's experience is
poor.

**Scope, stated rather than generalised:** observed against
`tools/snapshot_api.py`, which is `wsgiref.simple_server` and which the
operations guide already declares is not the production server. A production
WSGI server that drains the request body would likely deliver the `401` cleanly.
This finding should be **re-tested against the Phase 3 `freedom-web` process**
before any conclusion is drawn about production behaviour.

**Disposition:** track against Phase 3 hosting. If it reproduces there, the fix
is server-side body draining on an early reject, not a module change.

## RA-4 — a step 10 fault injector must not fault the preflight — **procedure**

The first attempt at step 10 failed to test what step 10 tests. The one-shot
injector dropped the **first** request after arming, and in a browser that is the
CORS preflight — so the `POST` was never sent, nothing was delivered, and the run
exercised the *miss* branch. The procedure warns against exactly this outcome
("stopping the service before submission is not this test, because that can
exercise only the miss branch") but not against this cause.

Corrected by faulting `POST` only, after which the step ran as intended and was
verified: preflight delivered, `POST` committed upstream, response dropped.

**Disposition:** whoever re-runs step 10 needs this. Add a sentence to §6 step 10
saying the fault must apply to the `POST` and never to the preflight, since the
browser's first request after arming is always `OPTIONS`. The injector itself is
deliberately not committed — it is rehearsal scaffolding, not product.

---

## RA-5 — the accepted performance threshold was calibrated against unrepresentative data — **gate-relevant**

Added after Rehearsal B, 2026-08-09.

Rehearsal B previewed the 32-Actor active folder in **9.566 s**, against the
5-second preview threshold accepted in change-log **C-9**. The run was otherwise
perfect: 0 errors, 0 warnings, all 32 Actors accounted for.

The threshold is the problem, not the run:

| | Synthetic benchmark (C-9) | Rehearsal B (real) |
|---|---|---|
| Artifact | 1,090,981 B / 500 Actors | 16,287,185 B / 32 Actors |
| Bytes per Actor | 2,182 | **508,975 — 233×** |
| Preview | 794 ms | 9,566 ms |
| **Throughput** | **728 ms/MB** | **587 ms/MB** |

Per megabyte the real run is *faster* than the benchmark. The implementation
scales with bytes, as anyone would expect of a parser, and the threshold was
expressed in Actor count against a corpus of 2 KB Actors.

What makes this more than an oversight: **the project already knew.** Discovery
finding F-F5 (`docs/discovery/foundry-mapping.md:159`) records "an actor is
1.1–3.3 MB of JSON … it is genuine item volume". The benchmark contradicted an
established finding about the data, and the accepted threshold inherited that
error. A 500-Actor artifact of real Actors would be roughly 250 MB, not 1 MB.

**Consequence for the gate:** C-9's thresholds cannot be used as an acceptance
criterion in their current form. A run that satisfies every correctness
criterion breaches them, and a run against 500 synthetic Actors would pass them
while being 15× smaller than a real 32-Actor folder.

**Disposition: RULED AND CLOSED, 2026-08-09** — change-log **C-11**, amending
C-9. The threshold was kept, not scrapped, and restated in the unit that
survives a change of corpus:

1. The gate criterion is **throughput ≤ 1,200 ms/MB**, measured from the slowest
   sample. Enforced and reported by `tests/benchmark_snapshot_500.py`
   (`THROUGHPUT_LIMIT_MS_PER_MB`, `throughput_gate`), with four tests pinning
   the unit, the breach reporting, and the use of the slowest sample rather than
   the median.
2. C-9's 5-second figures are retained as synthetic smoke-test context and are
   **no longer gate criteria**. They are not deleted — they remain the record of
   what that corpus measured.
3. The absolute 9.566 s became a **Phase 3 architecture input**: the Council
   preview route cannot be a synchronous HTTP handler. Recorded in the plan's
   Phase 3 planning note.

Waiving the breach case by case was considered and rejected: it converts a
threshold into a formality.

---

## Not findings, recorded because they were verified

- The module never wrote to Foundry: Actor, Item and Folder counts and the
  shared compendium were unchanged across two submissions, a refused submission
  and a dropped-response duplicate.
- A refused submission wrote exactly one `snapshot_submission.refused` audit
  event and created no snapshot row and no artifact.
- An unauthenticated submission wrote **no** audit event, there being no
  authenticated principal to attribute one to.
- Preview took 4.92 s against the accepted 5-second threshold for a 35-Actor
  export. The threshold was set from a synthetic 500-Actor benchmark; a real
  35-Actor export using 98% of it is worth knowing before Rehearsal B, which
  covers a larger folder.
