# RP-11 I1-R3-R1 decision proposal — recorded unadmitted staging/final pairs

Proposal ID: `C-P5.0-R5-RP11-I1-R3-R1-D1`

Date: 2026-09-28

Prepared by: Claude, under
[`phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r1-retained-alias-review-remediation-claude-prompt.md) §2

State: **proposal for Peter Duscha's decision; repository-only; not an
acceptance record.** It records no decision. Finding **RP11-I1-R3-1 remains
Open, Blocking** until Peter records one.

## 1. Decision sought

Under the accepted I1-R3 direction, every record and index state is one inode
with two retained names: an exclusively created staging name and a final name
given by one non-replacing hard link. Only the next durable index state admits
the pair. A stop **after the final link and before that admission** leaves a
pair that *F* records as two unadmitted names sharing one inode at link count
two. Nothing may unlink, rename, repair, complete or adopt either name.

X-4 and B0-RA must treat that retained pair one way or the other. Two policies
are on the table:

1. **Permit metadata-only.** If *F* records both unadmitted names, X-4 and
   B0-RA permit them to share one inode **only** when both exact names are
   present as regular files, identify the same inode, each reports link count
   two, and no third name under the complete enumeration reaches that inode.
   Nothing is opened, read, digested, admitted or used as evidence, and no
   unchanged identity, content, owner, mode, size or digest is claimed.
2. **Refuse unadmitted aliases.** The alias exception remains limited to
   admitted objects. Any unadmitted pair sharing an inode makes X-4
   `inconclusive` and makes B0-RA stop fail-closed.

The I1-R3 handback reports an in-session answer choosing option 1 and says it
still needs confirmation as the decision of record. This proposal does not
infer that confirmation. The source currently implements option 1, and it
stays unchanged until Peter decides.

## 2. Where the two authorities differ

* The accepted
  [redesign proposal §4](phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md)
  permits "the one staging/final pair explicitly recorded for a **published**
  object". A pair verified after the link but not yet admitted has been
  published.
* The
  [I1-R3 assignment §4](phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-claude-prompt.md)
  permits "exactly the recorded staging/final pair for one **admitted**
  object". Under that reading, unadmitted names receive only the R5
  presence/name/type check. That check has no alias exception.

Option 1 follows the first reading and option 2 the second. Neither is a
drafting accident that one of them silently fixes, so the choice is Peter's.

## 3. When the difference matters

The policies differ only for a stop that happens **after a final link and
before the next durable state admits the pair**, when X-3 then succeeds. The
unwired implementation's own fault matrix
(`test_every_act_stage_fails_closed_once_with_the_correct_final_state`, 43
cases) shows how often that is. **Fifteen of the 43 act-stage storage
failures** leave such a pair and still reach a successful X-3:

| Failure | Unadmitted pair(s) *F* records |
|---|---|
| P-7 publish (error reported after the link); P-8 directory barrier, verify-pair, close | act *n*'s record |
| X-2 create, verify, write, verify-content, file barrier, publish (fail); X-2 create (error after the call) | act *n*'s record |
| X-2 directory barrier, verify-pair, close; X-2 publish (error after the link) | act *n*'s record **and** *I*-*n* |

Every other stop either leaves no pair (staging only, or stream files only) or
has no admissible *F* at all (X-3 failed or was interrupted). In those cases
X-4 is already `inconclusive` under both policies.

## 4. Comparison

| | Option 1 — permit metadata-only | Option 2 — refuse unadmitted aliases |
|---|---|---|
| **Fail-closed behaviour** | Permits exactly the one shape the mechanism leaves. Everything else stops: a lone member at link count two, divergent members, a third link inside or outside the root, a cross-object alias, a name in two pairs or categories, an unrecorded pair, a non-regular member, an absent member, and any incomplete or changing enumeration. §6 names the tests. | Stops on the one permitted shape as well. Its stop set is a strict superset of option 1's. |
| **Evidence meaning** | Unchanged from R5 for the pair. The pair is not evidence, is never opened, and has no established bytes or metadata. Admitted records, streams and states are verified exactly as under option 2. | The same admitted evidence would verify, but X-4 is `inconclusive` for the **whole pass**, including every act admitted before the stop. |
| **After a stopped Pass A** | Pass A's retained root stays verifiable. B0-RA can pass, and Pass B can proceed on an otherwise valid root, with the pair reported as bounded residue under the evidentiary limit. | Pass A's root can never pass B0-RA, because C-8 forbids removing the pair. The draft has no provision for a second Pass A. A repeat would need new authority and a new capture root, and would repeat Pass A's one target mutation, the §5 `rsync --delete`. |
| **Consistency with accepted R5 retention** | R5 establishes only presence, name and type for an unadmitted object, and never content. Option 1 keeps that and adds a stricter **metadata** condition: one inode, link count two, no third name. It reads nothing more. R5 had no alias exception because its rename route left no alias. The exception exists only because the accepted I1-R3 direction creates the alias. | Literal R5 alias rule, with the exception confined to admitted pairs. The price is that the accepted I1-R3 route turns an ordinary post-link storage failure into loss of the whole pass. |
| **Attack or confusion surface** | The unadmitted final name, for example `records/000002.json`, looks like a record. It is accounted as unadmitted, never read, and cannot satisfy `published-record-not-accounted` or X-4's record list. A hostile rewrite of its bytes is undetected, but R5 already accepts that limit for every unadmitted object. | No unadmitted inode is shared, so there is nothing to reason about for it. |
| **Implementation state** | Implemented and tested, unwired and unaccepted. | Not implemented. §7 lists what would change. |

## 5. Recommendation — option 1

Claude recommends **option 1, permit metadata-only**, for four reasons:

1. **It costs no evidentiary strength.** The pair is never evidence under
   either option. Option 1 permits only the exact state the mechanism itself
   leaves, and stops on every other shape. That includes shapes that R5's
   presence/type check alone would miss: a third link, and a lone member kept
   at link count two by an outside name.
2. **It avoids a disproportionate operational consequence.** Under option 2,
   about a third of the modelled post-launch storage failures would make a
   Pass A root, which the rules retain forever, permanently unusable for
   B0-RA. There is no recovery path short of a new, separately authorized
   Pass A that repeats the synchronization mutation. A failed close or a
   failed barrier after verification should not discard earlier acts that
   were admitted and verified.
3. **It matches the accepted design direction.** The redesign acceptance
   speaks of a *published* object's recorded pair, and it forbids cleanup. A
   policy that refuses the pair, while forbidding its removal, makes the
   route's own residue fatal.
4. **It is the tested state.** Choosing option 2 needs a further
   implementation and review cycle (§7). Choosing option 1 needs only the
   decision record and a docstring alignment (§8).

The residual risk of option 1 is the one R5 already accepts: an unadmitted
object's bytes are not established. Option 1 does not widen it.

## 6. Option 1 — requirements, source and tests as they stand

| Layer | Where | What it does |
|---|---|---|
| Requirements (proposed draft) | RP-11 row (e); §9.5.2 X-4; §7.1 B0-RA condition 5 | Admits the unadmitted-pair metadata rule. **Marked as awaiting a decision of record** by the I1-R3-R1 wording correction. |
| Pair representation | `capture_contract.accounted_objects` | Pairs two recorded unadmitted names that are one object's staging and final name (`role_of`), `partner` set and **no identity**. A name in two categories raises `duplicate-accounted-name`. |
| Store accounting | `CaptureRootStore.publish`, `_probe_regular`, `known_objects`, `publication_states` | A final name is known only after a successful link, or after a failed link whose no-follow `lstat` shows the bound inode. An `EEXIST` occupant is never recorded. |
| Final state | `CaptureSession._finalize_once` | *F*'s `unadmitted` is every known regular name that is not in the admitted chain, records or bound streams. |
| Enumeration | `_Verifier.enumerate` | Regular files only at link count one or two, with no more names than links. Otherwise `path-alias`. |
| Alias rule | `retention_check._aliases` | One name needs link count one. Two names need link count two **and** must be each other's recorded `partner` in *R*. Otherwise `path-alias`. Recorded partners that are both present on different inodes give `pair-divergent`. |
| Admitted pairs only | `_Verifier._admitted_pairs` | Identity, link count, owner and mode, for pairs that carry an identity. Unadmitted pairs never reach it. |
| No read | `read_admitted` is called only for *F*, its chain, listed records and bound streams | An unadmitted member is never opened. |

**Tests proving exactly one pair and no wider** (`test_rp11_retention.py`
unless stated). Every test marked † also asserts that neither unadmitted
member was opened:

| Required refusal or proof | Test(s) |
|---|---|
| the permitted shape, for four stop stages, nothing opened, tree unchanged, X-4 valid | `test_a_recorded_unadmitted_pair_is_retained_and_never_read` † |
| lone member at link count two, staging or final kept alive by an outside link | `test_a_lone_unadmitted_pair_member_at_link_count_two_stops` † (new, I1-R3-R1) |
| divergent members | `test_an_unadmitted_pair_whose_members_diverge_stops` † |
| third link outside / inside the root | `test_an_unadmitted_pair_with_a_third_link_stops`; `test_an_unadmitted_pair_with_a_third_link_inside_the_root_stops` † (new) |
| cross-object alias | `test_an_unadmitted_pair_member_aliasing_an_admitted_object_stops` † (new); `test_two_accounted_names_that_are_not_partners_may_not_share_an_inode`; `test_a_cross_object_alias_stops` |
| a name in two pairs or categories | `test_an_unadmitted_pair_recorded_twice_stops` † (new); `test_a_name_in_two_pairs_or_categories_stops` |
| an unrecorded pair | `test_an_unrecorded_published_pair_stops`; `test_an_unadmitted_staging_name_hard_linked_elsewhere_stops` |
| a non-regular member (directory, symbolic link) | `test_a_non_regular_unadmitted_pair_member_stops` † (new) |
| an absent member | `test_a_deleted_member_of_an_unadmitted_pair_stops` |
| incomplete enumeration | `test_an_incomplete_enumeration_of_a_pair_root_stops` (new) |
| changing enumeration or verification | `test_an_unadmitted_pair_changing_during_the_check_stops` † (new) |
| the mechanism's own X-4 and B0-RA accept each of the 15 pair-leaving stops | `test_rp11_capture.py::test_every_act_stage_fails_closed_once_with_the_correct_final_state` |

## 7. Option 2 — what a later decision implementation would change

This section is not implemented here.

* **Requirements (draft).**
  * Delete the unadmitted-pair sentence from B0-RA condition 5 and from X-4.
  * Narrow RP-11 row (e) to "an **admitted** object's recorded pair".
  * State under §9.5.3 and C-15 that a stop after a final link and before
    admission leaves X-4 `inconclusive` for the pass, and that B0-RA then
    stops.
  * State that no provision exists for a second Pass A.
* **Source.**
  * In `retention_check._aliases`, a two-name group must carry an identity
    (`AccountedObject.admitted_pair`). Otherwise it is `path-alias`.
  * Keep `pair-divergent` for recorded unadmitted partners on different inodes,
    so that option 2 is not weaker there.
  * Amend the module docstring bullet on the alias exception.
  * `capture_contract.accounted_objects` may keep pairing unadmitted names for
    the divergence check.
  * No change to `capture_store` or `capture_mechanism`: X-4 would simply
    return `inconclusive` through `verify_final_state`.
  * Three covered files change, so the manifest moves to version 24 and the
    artifacts are regenerated.
* **Tests.**
  * `test_every_act_stage_fails_closed_once_with_the_correct_final_state`: its
    15 pair-leaving cases expect X-4 `inconclusive` and a B0-RA stop.
  * `test_a_recorded_unadmitted_pair_is_retained_and_never_read` becomes a
    refusal test.
  * The `PassA` fixture asserts `x4_validity == "valid"`, and every test built
    on `_pair_root` or `stop_stage=` needs a fixture variant that does not.
  * Several expected reasons move to `path-alias`.
  * The no-read assertions stay.

## 8. Decision text

Peter may adopt either paragraph as written.

> **Accept option 1.** Peter Duscha decides, for finding RP11-I1-R3-1, that
> X-4 and B0-RA permit a staging/final pair that Pass A's final state *F*
> records as **unadmitted** to share one inode **only** when both recorded
> names are present as regular files, both identify the same inode, each
> reports link count two, and no third name under the complete enumeration
> reaches that inode; that nothing of such a pair is opened, read, digested,
> admitted or used as evidence; and that no unchanged identity, content, owner,
> mode, size or digest is claimed for it. Every other alias, divergence,
> absence, type or enumeration fault remains a fail-closed stop. This confirms
> the in-session answer reported in the I1-R3 handback as the decision of
> record. It accepts no draft bytes, implementation or manifest digest, and it
> closes no other finding.

> **Accept option 2.** Peter Duscha decides, for finding RP11-I1-R3-1, that the
> alias exception of X-4 and B0-RA is limited to the recorded staging/final
> pair of an **admitted** object; that any staging/final pair Pass A's final
> state *F* records as unadmitted and that shares an inode makes X-4
> `inconclusive` and makes B0-RA stop fail-closed; and that nothing is
> unlinked, renamed or repaired to avoid that outcome. This supersedes the
> in-session answer reported in the I1-R3 handback. A separately assigned
> implementation must amend the draft, `retention_check` and the tests listed
> in §7 of the decision proposal and return them for independent review. This
> decision accepts no draft bytes, implementation or manifest digest, and it
> closes no other finding.

Under **option 1**, a later assignment only needs to:

* record the decision;
* replace the "maintainer decision, 2026-09-28" note in
  `retention_check.py`'s docstring with a reference to the decision record,
  which is a covered-source byte change with a manifest version bump; and
* remove the "awaiting a decision of record" markers from the draft.

## 9. Authority and current state

This proposal authorizes nothing. It is not an acceptance record. It does not
change source semantics and it does not implement option 2. It creates no
host or operational authority.

* **RP11-I1-R3-1** remains Open, Blocking.
* RP11-I1-R3-2 and RP11-I1-R3-3 remain Open, Important.
* RP11-I1-R1-1, RP11-I1-R2-1 and RP11-I1-2 remain Open.
* RP-11 remains unmet, and neither pass is executable or authorized.
* P5.0-R5 remains Blocking and OD-62 G-A remains conditional.
* `plan.is_executable=False`, and Package 5.0 remains not ready.
