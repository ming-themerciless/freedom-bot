# Independent review request — the complete Phase 2 gate package

Prepared: 2026-08-10
Requested by: Peter Duscha, Acceptance Authority
Implementer of the work under review: Claude
Reviewer: Codex, as Independent Reviewer
Repository state: branch `docs/platform-plan`, through commit `9dfe676` plus the
records added with this request

## What is being asked

Recommend whether the Phase 2 data-integrity, identity and migration-safety gate
may close. This is the review the plan requires as §13.3 operational evidence —
"independent review closure of every blocking security, identity, atomicity,
migration and recovery finding" — not a courtesy pass over a finished thing.

**Nothing in this package has been independently reviewed.** That is the reason
for the request and the first thing to weigh.

## Outcome, and the re-review this request now needs — 2026-08-10

**Answered 2026-08-09** by Codex in [`Handover information`](Handover%20information):
**do not close the Phase 2 gate.** Two findings, both against the two questions
this request ranked first and third:

| Finding | Question | Severity | Disposition |
|---|---|---|---|
| **B-1** — lost-pin reconciliation can still produce a false miss | 1 | Blocking | **open.** Remediated four times: C-13, C-14, C-15, and now **C-18** |
| **I-1** — C-10's ECMAScript key boundary is wrong | 3 | Important | **closed** by the re-review, change-log C-12 |

**B-1 has been through two re-reviews and is still open.** C-13's S-B inferred the
endpoint's accept order from the client's issuance order. C-14's S-B.1 then read
`caddy_http_requests_in_flight` as evidence that the proxy held nothing, which
Caddy's documentation does not support — it counts the requests *currently being
handled*, not an accepted connection whose request has not entered the handler,
and not body bytes still arriving. **C-15 withdraws both the probe and the gauge**
and settles an episode by a state instead of an observation: the endpoint is
stopped, and stays stopped until the outcome is recorded. A new step 4 re-queries
after the fresh submission so that a residual is detected rather than assumed
away. §5.4 drops the metrics requirement, replaces it with "no upstream retry
window", and — separately from B-1 — corrects the deprecated nested
`servers { metrics }` snippet to the current global form.

Question 7 — "is anything claimed that was not done?" — found its third case:
CL3-B-1 was recorded as closed and was not, and Rehearsal A's record claimed a
closure by observation that its step 10 could not have made. Both are corrected.

**It has since found three more, all self-reported and all corrected below**, which
is worth weighing when judging how much this package's prose should be trusted
without checking: step 4 expected a `404` from the retired path and gets an empty
`200`; the `5.4 s` shutdown figure was a rig measurement being read as a
production one, and the first attempt to measure production measured an
already-stopped service; and the `exporter.version`/`1.0.5` claim rested on
process restarts when the registry reloads at world launch. Each was found by
carrying out what the document said rather than by re-reading it.

Codex accepted questions 2, 4, 5 and 6, and the declared Phase 3 disposition of
RA-3. RA-4 is now written into §6 step 10.

**Added 2026-08-10, after the re-review of C-15:** on the reviewer's finding that
holding the NFC key-collision regression tests as `todo`/`xfail` left the release
vulnerable, and on maintainer instruction, that defect is now **fixed in both
implementations** — change-log **C-16**, contract **§1.2**, new refusal code
`nfc_key_collision`, exporter **`1.0.6`**. The module bytes therefore change,
which is also the version bump the `canonical.js` comment correction was being
carried against; that comment is corrected in the same build. **`1.0.6` was
installed on `foundry1` and `foundry3` on 2026-08-10** — since **superseded by
`1.0.7`**, installed the same day, and the "neither has been restarted" caveat
written here is corrected in the C-17 paragraph below;
Rehearsals A and B remain evidence about `1.0.5`, the build they ran on. The reviewer's second point is also addressed: the advertised
`npm test` script ran `node --test tests/`, which fails under Node 24 with
`MODULE_NOT_FOUND`, and is now `node --test tests/*.test.mjs`.

Everything is in
[`phase-2-b-1-settlement-remediation.md`](phase-2-b-1-settlement-remediation.md).

> **Superseded by the fourth remediation, recorded at the end of this section.**
> The five questions below were asked about C-15's rule, which the re-review held
> open; they are left unedited as the record of what was asked. S-A.1 and S-A.2
> survive into the current rule, S-A.3 is withdrawn and inverted, and question 1's
> premise — that "an unserved port accepts nothing" settles the episode — is
> exactly what the re-review found to be true and insufficient.

**What was requested was an independent re-review of B-1's third remediation.**
I-1 is closed and is not resubmitted. The third remediation was written after the
re-review that found the second one insufficient, by the implementer, and carries
no review of any kind. The specific questions:

1. **Does S-A close B-1?** The whole argument is that every commit on this path
   begins with an accept and an unserved port accepts nothing, so a query run while
   the endpoint is down is the complete truth about the episode. Is there a way for
   a request of the episode to commit after that query — in particular across the
   restart in step 4, given §5.4's "no upstream retry window" requirement? Is
   S-A.3's `502`/`503` check worth what it claims, or is it decoration on S-A.2?
2. **Is stopping the endpoint an acceptable price?** It is deliberately the only
   condition, so every lost-pin episode where the process is still running now
   requires maintainer-authorized downtime. Is that the right trade for Phase 2, and
   is the Phase 3 improvement — settling without a stop — recorded firmly enough not
   to be lost?
3. **Is the automated evidence what it says it is?**
   `tests/test_snapshot_recovery_settlement.py` claims that a submission connected,
   fully sent and waiting unaccepted at the endpoint commits nothing when the
   endpoint stops, against a real `wsgiref.simple_server`. Its negative control —
   serving the queue instead of stopping — is described in the remediation record
   but **not committed**: take that on the record's word or reproduce it.
4. **Is *Unsettled* reachable in practice**, or is it a branch an operator under
   time pressure will quietly classify as a miss? Unchanged from the last request,
   and still the part no test can hold.
5. **Are the operator-side claims sound where they are unobserved?** Nothing in
   S-A has been run against a live Caddy: that a stopped upstream yields `502`/`503`
   rather than a held request is read from configuration and documentation.

**Added 2026-08-10, after the review of the C-16 package**, which returned one
Blocking finding: the Manager's canonical encoder used `json.dumps`, whose float
formatting is a different function from `JSON.stringify`'s, so a conforming
export carrying `1e20` or `1e-7` was reported non-canonical. Fixed as change-log
**C-17**, contract **§1.3**: the verifier now implements `Number::toString`,
reads every literal as the double the exporter would have, and refuses a literal
outside the double range under the exporter's own code `non_finite_number`.
Eleven boundary documents plus a forty-value precision spread are asserted
through the shipped module and the real verifier in
`tests/test_exporter_contract.py`, which is the coverage gap the finding named.

**The exporter's output is unchanged byte for byte** — `canonical.js` always
delegated numbers to `JSON.stringify` — and the module is **`1.0.7`** solely
because the new refusal code joins the client's bounded `SERVER_ARTIFACT_CODES`
list. **`1.0.7` was installed on `foundry1` and `foundry3` on 2026-08-10 23:24:18
UTC** ([record](phase-2-module-1.0.7-install-2026-08-10.md)); exactly two files
differ from `1.0.6` and `canonical.js` is not one of them. No rehearsal evidence
changes: Rehearsals A and B remain evidence about `1.0.5`.

**A claim this request previously made is corrected there, and it is a question 7
case found by carrying it out.** This document said neither instance had been
restarted and that `exporter.version` "could still be stamped `1.0.5`". The
processes had not been restarted — but `exporter.version` is read from
`game.modules.get(MODULE_ID)?.version`, the **server's package registry**, which
reloads when a **world is launched**, not when a process starts. Both instances
launched worlds at 20:55 on 2026-08-10, six minutes after `1.0.6` went in, so the
stamp was `1.0.6` from that moment. Both launched again at 23:40, after `1.0.7`,
so the registry now holds `1.0.7` and the "no export until restarted" blocker is
cleared. No export has been taken, so no artifact has been observed carrying
`1.0.7`, and that is not claimed. C-17 also records one deliberate asymmetry for review: `-0` is refused
by the exporter and encoded as `0` by the Manager, because producing a `-0` and
reading a document in which the sign has already been lost to JSON are different
acts.

**Added 2026-08-10, after the re-review of C-15**, which held B-1 open for the
fourth time and is the reason this package is being returned again. The finding:
stopping only the upstream endpoint does not settle a request Caddy holds that has
not made its **first** upstream connection. Such a request connects after the
restart; "no upstream retry window" addresses retries after a *failed* attempt, not
a first attempt that has not happened. Step 4 detected the resulting duplicate but
did not prevent the false miss from authorizing it. The reviewer asked for either a
procedure that terminates or positively drains the complete ingress path, or an
application-level mechanism that rejects pre-settlement requests after restart.

**The maintainer ruled for the first**, and it is implemented as change-log
**C-18**: settlement is now S-A (the endpoint is not running) **plus S-I** (the
proxy in front of it is terminated — no process, no listener on `:80`/`:443` in
either protocol, nothing that will restart it, and the public name answering from
no origin) plus S-D (all of it stays down until the outcome is recorded). C-15's
S-A.3 is **withdrawn and inverted**: a `502` from Caddy means Caddy is running.
Step 4 gains the prevention half — the episode's route is **replaced by an explicit
`respond 410`**, for a reason found by running it, and the endpoint returns behind a
single-use `/recovery/<nonce>/…` path, so a request held by a hop
this host cannot terminate carries a dead address. The application-level mechanism
stays where §9 already had it, as the Phase 3 improvement. Everything is in
[`phase-2-b-1-settlement-remediation.md`](phase-2-b-1-settlement-remediation.md),
§ "B-1, fourth remediation".

**What is now requested is an independent re-review of B-1's fourth remediation.**
It was written after the re-review that found the third insufficient, by the
implementer, and carries no review of any kind. The specific questions:

1. **Does terminating the ingress close B-1?** The argument is that a request
   which has not reached the endpoint exists only inside the proxy, so a proxy
   process that does not exist cannot be holding one. Is there a place on this path
   a request can survive both — a kernel socket buffer, a socket-activated unit, a
   connection handed off during shutdown — and be delivered after the restart?
2. **Is the route retirement sound, and is it enough for the hops we cannot
   terminate?** Cloudflare fronts the public name and cannot be stopped from this
   host. The claim is that whatever it does with a held request, the request
   addresses a path that no longer routes to the application, so it cannot commit.
   Does `uri strip_prefix` behave as step 4 assumes, and is there a way the retired
   path still reaches the endpoint — a fall-through handler, a cached route, a
   normalisation that strips the nonce?
3. **Is host-wide downtime the right trade for Phase 2?** Every service Caddy
   fronts, all three Foundry instances included, is down for the duration of a
   reconciliation. C-15 rejected this cost and the maintainer has now accepted it.
   Is the Phase 3 improvement recorded firmly enough not to be lost?
4. **Is the automated evidence what it says it is?** The two new tests are each
   other's control: one reproduces the false miss with only the endpoint stopped,
   the other is the same episode with the proxy terminated. Both are committed.
   Deleting the terminate call from the second makes it fail — reproduce that
   rather than taking it on the record's word.
5. **Is *Unsettled* reachable in practice?** Unchanged from the last request, and
   now harder: step 1 is seven recorded conditions across two processes plus the
   database check.
6. **Are the operator-side claims sound where they are still unobserved?** Much
   narrower than it was. **The finding itself was reproduced** against a real Caddy
   2.10.2 on an isolated rig: a request the proxy had accepted with no upstream
   connection made survived the endpoint stop and was answered `201` after the
   restart, while the same episode with the proxy terminated delivered nothing.
   **S-I was then exercised against the production Caddy** in authorized windows,
   with one request held open on the origin's own listener: listeners gone in
   0.5 ms, process gone at 4.3 s, held connection closed with nothing delivered,
   `521` from Cloudflare on both paths, `Restart=no`. Running it found three things
   the record had wrong or missing — the retired path answers an empty `200` rather
   than `404` unless the block is *replaced* rather than deleted; S-I.2 passes
   while S-I.1 still fails, by 4.3 seconds on production; and the stop delay tracks
   what the proxy is holding, so an idle-host rehearsal shows a 4 ms stop and
   teaches the wrong expectation. All corrected. **Still unobserved:** step 4's
   retirement against production, which needs a route that does not exist there,
   and an operator following the steps. Please weigh whether the reproduction is
   the right shape of evidence, and whether anything in it proves less than the
   record now claims.

The original request below is left unedited as the record of what was asked.

## Why independence matters unusually much here

On 2026-08-09 Claude acted as both reviewer and implementer, on the maintainer's
explicit instruction, to end a review cycle that had stopped producing value.
Concretely, Claude:

- raised findings CL3-B-1, CL3-I-1, CL3-I-2, CL3-O-1…O-3 **and then implemented
  the fixes for I-1, I-2 and O-1**;
- raised RA-1, RA-2, RA-3, RA-4, RA-5 during the rehearsals **and implemented or
  drafted the disposition of RA-1, RA-2 and RA-5**;
- chose the field classifications, the canonical ordering rule, the throughput
  unit and the 1,200 ms/MB limit — every one a judgement nobody has checked.

The maintainer authorised this and it is recorded in each affected document.
It is still a departure from §17, and the correct remedy is this review rather
than a note.

## Scope

Everything from commit `e1749db` onward, plus the standing Phase 2 package.

| Area | Where |
|---|---|
| CL3 remediation | `phase-2-i-03-cl3-remediation.md`, commit `e1749db` |
| Rehearsal A + findings | `phase-2-supervised-rehearsal-2026-08-09.md`, `phase-2-rehearsal-a-findings-2026-08-09.md`, commit `e2f0a4d` |
| RA-1 / RA-2 closures | commit `281dbec` — `domain/foundry_profile.py`, `application/foundry/parser.py`, `docs/rules/*` |
| Rehearsal B + attestation + RA-5 | commit `e54e5c0` — `phase-2-supervised-rehearsal-b-2026-08-09.md`, `phase-2-data-owner-attestation-2026-08-09.md` |
| Change-log C-10, C-11 | `docs/project-management/change-log.md` |
| Profile review, owner recommendations | `phase-2-field-profile-maintainer-review-2026-08-10.md`, `phase-2-owner-recommendations-2026-08-10.md` |

## Specific questions, in priority order

1. **Is CL3-B-1 genuinely closed?** The §9 window rule now spans the whole
   unresolved episode, and Rehearsal A step 10 observed the hit branch against
   real data. Does any reachable sequence still produce a false miss and
   authorise a second export?
2. **Is the RA-1 classification right?** Ten paths became `SNAPSHOT_ONLY` with
   no owning package, on the argument that favourites and sourcebook provenance
   will never be platform state. Should any of them instead be
   `legacy_authority_deferred` with a named package?
3. **Is C-10's canonical order correct and complete?** Integer-index keys
   ascending, then string keys by code point. Check the array-index definition
   against ECMAScript, and check `canonical_bytes` against the module's
   `canonical.js` for any case where the two still disagree.
4. **Is C-11's throughput criterion sound?** 1,200 ms/MB from the slowest
   sample, replacing wall-clock seconds. Is the limit defensible, and does
   measuring the slowest sample rather than the median hold under a noisy host?
5. **Is the attestation adequate §13.3 evidence?** Note the honest weakness
   recorded in its §2: every Actor is a create-candidate because the database was
   empty, so no identity conflict *could* arise. Does that satisfy "accounting
   for every Actor" as the plan intends, or does the gate need a reconciliation
   against a populated database?
6. **Is the field-profile review adequate?** Its own record states it was a
   blanket acceptance, resting on two rehearsals returning zero unclassified
   paths rather than a field-by-field session.
7. **Is anything claimed that was not done?** This package's history includes
   two prior evidence-accuracy findings (I-1, I-3R-1) where a document asserted
   more than the code delivered. Please look for a third.

## Known open items, declared rather than found

- **RA-3** — a `401` on a large upload surfaces as `network_failure`. Bounded to
  the `wsgiref` rehearsal launcher; referred to Phase 3, not fixed.
- **RA-4** — a step 10 fault injector must fault the `POST`, never the
  preflight. Procedure note; the operations guide does not yet say so.
- ~~**CL3-O-1's sibling in the module**~~ — closed. The `canonical.js` header
  comment described the pre-C-10 key-order rule and was left unedited to avoid
  changing an installed, rehearsed build's bytes for a comment. C-16 is that
  version bump, and the comment is corrected in `1.0.6`.
- ~~**NFC key collision in the canonical encoder**~~ — **fixed 2026-08-10**,
  change-log **C-16**, exporter `1.0.6`. Two distinct object keys sharing an NFC
  form collapsed in the exporter and one value was silently dropped; the verifier
  did not normalise keys at all and emitted the same key twice. Both halves now
  refuse with `nfc_key_collision`, the verifier also normalises string values,
  and the `xfail`/`todo` holds are gone:
  [`phase-2-canonical-nfc-key-collision.md`](phase-2-canonical-nfc-key-collision.md).
  Reachability against real Foundry data was never demonstrated and is still not
  claimed. `1.0.6` was **installed on `foundry1` and `foundry3` on 2026-08-10**,
  recorded in
  [`phase-2-module-1.0.6-install-2026-08-10.md`](phase-2-module-1.0.6-install-2026-08-10.md).
  ~~**New open item: neither instance has been restarted, so no supervised export
  may be taken until they are** — before that, `exporter.version` could still be
  stamped `1.0.5`.~~ **Closed and corrected 2026-08-10.** `1.0.7` superseded
  `1.0.6` on both instances at 23:24 UTC, and both worlds were launched at 23:40,
  which is what reloads the package registry `exporter.version` is read from. The
  claim struck through was also wrong when written: both instances launched worlds
  at 20:55, six minutes after `1.0.6` went in, so the stamp was `1.0.6` from then
  and a process restart was never what governed it.
- **Caddy** — closed. The temporary public route was reverted 2026-08-09 22:38
  UTC, on the second attempt: the first restored a backup that had itself been
  captured after the route was added. Verified — no `via: 1.1 Caddy` and no body
  from that hostname. A Cloudflare DNS record still resolves it to an empty edge
  `200` with no origin behind it.
- The **fixture-guard test** recommended by
  `phase-2-i-03-fixture-identity-correction.md` remains untracked work.

## Evidence boundary

- Rehearsals A and B ran against real Actor data in the live `the-guild` world,
  writing only to the disposable `freedom_test`. No character, mapping or import
  row was ever created. Both artifacts and both credentials were shredded.
- The 208 skipped tests are database-backed and skip without
  `TEST_DATABASE_URL`; that is the same posture as every prior review.
- Storage guarantees remain proven against same-process substitution, not a
  cross-account or multi-process experiment. Neither is a gate requirement.
- **Rehearsal A satisfies no gate criterion.** Rehearsal B and its attestation
  are two items of §13.3 evidence, not the gate.

## Verification

Re-run 2026-08-10 after C-18:

```text
./venv/bin/python -m pytest -q               → 1886 passed, 208 skipped
(cd foundry-module && npm test)              → 155 passed, 0 todo
node --check foundry-module/scripts/*.js     → 8 files
git diff --check                             → clean
```

No expected failure remains: the strict `xfail` that held the NFC defect open is
gone, as is the node `todo`. The 208 skips are database-backed and skip without
`TEST_DATABASE_URL`, unchanged. Earlier runs of this package reported 1,784, then
1,815, then 1,832 passing; the growth is C-15's, C-16's, C-17's and C-18's own
tests. C-18 adds four and rewrites six, and changes no JavaScript.

## What a clean review would release

The Acceptance Authority's gate decision, and nothing else. Phase 3 additionally
requires an accepted §12.1 visual direction, a named security reviewer distinct
from the implementer, and OD-16 and OD-17 closed — none of which this package
touches.
