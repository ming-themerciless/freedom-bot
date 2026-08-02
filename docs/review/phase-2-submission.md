# Phase 2 — Review Submission (revision 7: one display-name comparison rule, shared by every layer)

Status: **The mapped-name normalization correction was independently reviewed
by Codex and accepted by Peter Duscha on 2026-08-02; I-01 is closed.** Every
finding raised within the approved Phase 2 review gate — *data integrity and
migration safety* for import/reconciliation (plan §12) — is fixed and covered by
regression tests, and §13 checks the slice against each of plan §12's acceptance
criteria. **This is not a claim that the complete plan §12 Phase 2 milestone is
finished**: the Foundry active-character snapshot importer, which §12 lists as a
Phase 2 deliverable, is not in this slice and remains an explicit maintainer
scope decision. The importer has also never run against a real Sheet. Both
reservations are recorded in §13 and are the maintainer's to weigh. Approval is
the reviewer's and the maintainer's to give; this document does not claim it.

Date: 2026-08-02 (revisions 6 and 7); 2026-08-01 (revisions 4 and 5); 2026-07-31
(revisions 1–3)

**Revision 7 closes the blocking normalization defect Codex raised against
revision 6** — issue **I-01** in
[`docs/project-management/raid-register.md`](../project-management/raid-register.md),
and item 2 of plan §20. Revision 6's case-only exemption folded with
`casefold()` while the repositories looked collisions up with `lower()`, so
`Test Straße` could import as `Test STRASSE`, be waved through as a
re-capitalisation, skip the collision lookup on the strength of that, and commit
two characters under one display name. There is now one comparison policy
(`domain/names.py`), every layer uses it, and every non-exact spelling change is
looked up before anything is written. §0.4 states the defect and the correction;
§2.14 is the fix; §7.0.2 is this session's verification. **This revision
implements the accepted identity policy; it does not amend it**, so there is no
change-log entry.

**Revision 6 fixed a blocking identity defect that revision 5 wrongly concluded
was not there.** A maintainer supplied the input that breaks it: permute two or
more mapped rows and rename every displaced character to a fresh, unused name,
and all six of revision 4's run-level signals stay false while the importer
commits each character's identity onto another. A mapped semantic name change is
now never applied automatically. §0.3 states the defect and the correction; §2.13
is the fix; §7.0 is this session's verification. Revision 5's conclusion that
*"no new identity hole"* existed is **incorrect and superseded** — see §0.3.

**Revision 5** changed no code. A later session re-ran every check in §7.1 for
itself rather than carrying the previous session's results forward, re-proved
rulings A and B end-to-end outside the test suite, and corrected three factual
slips in this document. Results and corrections are in **§7.0.1**; the slips are
listed in §0.2. Its identity conclusion did not survive revision 6.

This reports the same milestone slice — the **Sheet identity import**, plan
§16.4's *import/reconciliation* checkpoint — plus the correction passes carried
out under four maintainer rulings dated 2026-08-01 and the identity ruling of
2026-08-02.

Nothing is committed or pushed. The work sits on branch `docs/platform-plan` on
top of `bb104c8 Begin Phase 2 Sheet identity import`.

**Stop point.** This is the Phase 2 re-review handoff. No Phase 3 work, no part
of the plan §7.4 magic-item catalogue and no part of the Phase 5 Living Cost
scheduling requirements has been started — the last of those was read as
maintainer-owned plan text and left untouched — and none should be until this
submission is re-reviewed and the milestone accepted.

---

## 0.4 Revision 7 — two folds, one of them wrong for the job it had

**The defect (I-01, raised by Codex against revision 6).** Revision 6 kept one
mapped-name change automatic: a change of capitalisation alone. It decided that
with Python `casefold()` in `application/sheet_import.py`, and it *skipped the
collision lookup entirely* when the two folded names matched. The character
repositories — the fake and the PostgreSQL adapter — looked names up with
`lower()`.

`casefold()` is not "the same word, differently capitalised". It is full case
folding, and it expands `ß` into `ss`. So `Test Straße` and `Test STRASSE` fold
together under `casefold()` and apart under `lower()`, and the importer would:

1. hold `Test Straße` and `Test STRASSE` as two characters;
2. read the mapped `Test Straße` row as `Test STRASSE`;
3. classify that as a permitted capitalisation update;
4. skip the collision lookup because of step 3; and
5. commit two characters with the identical display name `Test STRASSE`, with no
   issue reported.

Reproduced against the uncorrected tree before anything was changed:

```text
applied= True
issues= []
names= ['Test STRASSE', 'Test STRASSE']
```

**Why it is not a one-line fold swap.** Making both sides `casefold()` would
make `Test Straße -> Test STRASSE` an automatic identity rewrite. Making both
sides `lower()` would let an unmapped `Test STRASSE` mint a second character
beside an existing `Test Straße`. The two questions are genuinely different
questions, and each wants a different width:

| Question | Used for | Fold | Errs |
|---|---|---|---|
| Is this the same name, exactly? | idempotence; no lookup needed | none | — |
| Is this the same word, re-capitalised? | may apply without a human | NFC + `lower()` | **narrow** — fewer changes apply unreviewed |
| Does another character claim this name? | collision lookup | NFC + `casefold()` | **wide** — more names count as taken |

Both errors land on *refuse*, which is the direction this importer has already
chosen everywhere else. NFC normalisation is applied before either fold so that
two canonically equivalent encodings of one name — a precomposed `é` and an `e`
with a combining acute — are one name; without it, creation could fork an
identity on how a name was typed.

**The containment is structural, not an assumption about Unicode.**
`DisplayName.differs_only_in_capitalization` is defined *through*
`claims_same_identity_as`, so nothing can be exempted from the identity refusal
that the collision key would not also see, whatever a future Unicode revision
does to some character. That is asserted directly, per case, in
`test_nothing_identity_neutral_escapes_the_collision_key`.

**The correction.**

1. One policy, `domain/names.py`, holding `DisplayName` and the three
   intention-revealing relations above. It is in `domain/` because it imports
   nothing but the standard library and answers a question about game identity,
   not about a Sheet or a database.
2. The Sheet parser, the import service, the fake repository and the PostgreSQL
   repository all compare through it. There is no remaining `casefold()` or
   `lower()` call anywhere on the importer's identity path.
3. **Every non-exact spelling change is looked up**, including a
   capitalisation-only one. A re-cased name can be a name somebody else holds;
   that is now `name_collision` rather than a silent second holder.
4. `Test Straße -> Test STRASSE` is a semantic mapped-name change and is refused
   as `mapped_name_change` when nothing more specific applies, exactly like any
   other rename.

**The cost, stated plainly.** `find_by_display_name` can no longer be a SQL
`WHERE`: PostgreSQL's `lower()` is narrower than the policy — confirmed on this
host, `lower('Test Straße') <> lower('Test STRASSE')` — and a narrower filter
*skips real matches*, which is the defect rather than an optimisation. The
adapter therefore reads `characters` and compares in Python: one sequential scan
per lookup, one lookup per created or re-spelled row. That is bounded and
deliberate for a bootstrap population of roughly 150 characters in an occasional
operator tool. The threshold at which it must become a stored, indexed identity
key plus a decided uniqueness rule — roughly 2,000 characters, or the first
request path that calls it — is recorded in the adapter docstring, in
`docs/operations/sheet-import.md` and at §11 item 8. That is a migration and a
policy decision, and this correction deliberately makes neither.

**What did not change.** Every issue code, outcome shape, transaction boundary,
audit action, exit code and idempotency guarantee. The one behavioural addition
is that `name_collision` can now be reported for a capitalisation-only change,
which is the blocking case the defect required.

**Corrections to earlier text in this document.**

| Superseded claim | Where it was | Correction |
|---|---|---|
| *"a re-cased name resolves to the same character under the importer's documented comparison rule"*, resting on `casefold()`/`lower()` | §0.3, "What is still automatic" | The two folds were not one rule. Rewritten in place; the guarantee now rests on `domain/names.py` |
| *"`Test Straße` … could be created twice rather than reported as a collision"* as an open question | §13.1, §11 item 8 | **It was worse than that**: on the mapped path it could commit two characters under one name. The comparison half is fixed; the database-uniqueness half of item 8 remains open |
| *"the exemption is internally consistent"* | §13.1 | False. `is_semantic_name_change` folded with `casefold()` while the collision lookup beside it folded with `lower()`, and the exemption *skipped* that lookup |
| §12 item 0(a), inviting a reviewer to attack the case-only exemption | §12 | **Answered, against the claim.** Codex attacked it and it fell. Replaced by §12 item 0 for revision 7 |

## 0.3 Revision 6 — the fresh-name permutation, and the correction of revision 5

**The defect.** Revision 4 decided a mapped-name change from six run-level
signals (`_RunStructure`): a parse error, a creation, an absent mapping, a
dangling mapping, a detected shift, or a name collision. If none of them was
true, it treated the change as an in-place rename and committed it. §12 item 1
of revision 4 invited a reviewer to attack the claim that those six *"cover
every way a row can move"*. Revision 5 attacked it, tried a pure row swap, found
`row_identity_shift` caught it, and concluded there was no new identity hole.
**That conclusion was wrong**, and it was wrong because it only tried the
permutation in which the moved characters keep their names.

Permute the rows **and** rename every displaced character to a fresh, unused
name:

| | Row 3 | Row 4 |
|---|---|---|
| Mapping says | character A, stored as `Test Smith A` | character B, stored as `Test Smith B` |
| The import reads | `Test Fresh X` | `Test Fresh Y` |

Every signal is false. No row was added, so no creation. None was removed, so no
absent mapping. Nothing is malformed, so no parse error. Both mappings resolve,
so nothing dangles. Neither *old* name appears anywhere in the import, so the
shift check finds nothing. Neither *new* name is held by anybody, so there is no
collision. Revision 4's importer therefore **committed** `Test Fresh X` onto
character A and `Test Fresh Y` onto character B — while the edit that produced
this input put `Test Fresh X` on character **B** and `Test Fresh Y` on character
**A**. Two players' identities are exchanged, the audit rows record two ordinary
renames, and nothing afterwards can tell. The same holds for a cycle of any
length.

**Why no seventh signal would help.** This is not a heuristic that missed a
case. The input is *observationally identical* to two legitimate in-place
renames: same rows, same count, same mappings, same absence of collisions, same
everything. A Sheet row has no stable source identity — only a position and a
name, and one edit can change both — so there is no function of the input that
separates the two readings. Any rule that commits one of them is a coin toss on
a player's identity. Revision 4's own trade — *"a false refusal costs a second
run; a wrong rename costs a character its identity"* — was stated correctly and
then applied to too small a set of inputs.

**The correction, fail-closed.** A semantic mapped-name change is now **never
applied automatically**. It is reported and the whole run stops:

| Reported | When |
|---|---|
| `row_identity_shift` | the mapped character's stored name is found at another row in the same import — the run shows the rows moved |
| `name_collision` | the name the row is claiming is already held by a different character |
| `mapped_name_change` | neither of the above: the general case, and the one that used to commit |

`_RunStructure`, `_structure_of` and `_is_shifted` are removed. They existed only
to decide whether a rename was safe, and no run-level view can decide that.

**What is still automatic**, because none of it requires guessing an identity:

- creating an unmapped row whose name the platform does not already hold;
- updating long name, level and the active flag while the short name is
  unchanged;
- a change of **capitalisation alone**. ~~The parser folds with `casefold()` and
  the platform's lookup folds with SQL `lower()`, so a re-cased name resolves to
  the same character under the importer's documented comparison rule~~
  **Corrected by revision 7 (§0.4): those were two different folds, and the gap
  between them was a blocking defect.** A re-cased name resolves to the same
  character under the single policy in `domain/names.py`, and cannot be a moved
  row for that same reason — but it is now looked up against every other
  character before it is applied, because the name it is being re-cased into can
  be taken.

**The cost, stated plainly.** A genuine rename now blocks with no in-platform
remedy, exactly as a moved row already did. The importer still has no re-key or
reconciliation command — building one is not in this task's scope, because
re-keying a mapping is precisely the guess this refusal exists to prevent and it
needs its own authorization and audit story. It is §11 item 5, and this change
makes it more pressing rather than less.

**Corrections to earlier text in this document.** Every claim below is
superseded, and each has been struck or rewritten where it appears:

| Superseded claim | Where it was | Correction |
|---|---|---|
| *"The importer never guesses"* as a standing property | `application/sheet_import.py` module docstring | Rewritten. It was true of every path except the one that mattered |
| *"these six signals cover every way a row can move under a mapping"* | §12 item 1, `_RunStructure` docstring | False. The fresh-name permutation moves rows with all six false |
| *"an unambiguous in-place rename is still applied"* | §2.2, `test_an_unambiguous_in_place_rename_is_still_applied` | Removed. There is no unambiguous mapped rename |
| *"No new hole"* in the identity row of §13.1 | §13.1 | **Incorrect.** The re-trace tried the name-preserving permutation only |
| `ambiguous_name_change` as a conditional refusal | §2.2, ops doc, tests | Replaced by `mapped_name_change`, which is unconditional |

## 0. Revision 4 — the maintainer rulings and what changed

The maintainer reviewed revision 3 and ruled on four matters. Two of them
corrected this document, and two of them are code defects it had not found.

| # | Matter | Ruling | What was done |
|---|---|---|---|
| A | Expected exceptions — credentials, database, transport — were still written to debug logs with tracebacks | Never log exception messages or tracebacks at **any** level | **Fixed.** `exc_info` removed from all six sites; a fixed category and the exception's class name are logged instead. 8 regression tests that turn DEBUG logging **on** and plant canaries inside the exceptions. §2.10 |
| B | A partial Google-library install could still escape as an `ImportError` traceback | Translate it into the same fixed dependency refusal and exit code | **Fixed**, with 3 regression tests. §2.11 |
| C | OD-17 and OD-39 were described as Phase 2 blockers, creating a sequencing deadlock | They are real risks at **Phase 3 planning / affected command migration** and **before Phase 5.7 and 5.8**, not Phase 2 import blockers | **Documentation corrected**, here and in `open-decisions.md`. The risks are *not* claimed fixed. §3 |
| D | "OD-38" named two different decisions | The music decision becomes **OD-40**; OD-38 keeps *Initial authority during Sheet migration* | **Renumbered**, references repaired, uniqueness of all forty identifiers checked. §2.12 |

**What revision 4 did not do**, because the rulings forbade it: no Phase 3 work,
no §7.4 catalogue scaffolding, no interim announcements, no Council-only
commands, no command disabling, no role-name authorization, no identity
inference, and no `character_access` population.

## 0.2 Revision 5 — what re-verification found

> **Corrected by revision 6.** The headline below — "no code defect" — was
> wrong. The re-trace of the *identity* path missed the fresh-name permutation
> and concluded there was no new hole; §0.3 has the case and §13.1 the corrected
> row. The rest of this section stands.

No code defect ~~was found~~ **was found, and one was there**. The rulings-A and
-B fixes hold under an independent end-to-end check (§7.0.1) and every §7.1
figure reproduced exactly. The re-trace of the import mapping, transaction,
audit, credential and failure paths found nothing, and revision 6 re-read those
five and agrees; the **identity** path is where it failed (§13.1).

Three factual slips in this document were corrected:

| Slip | Correction |
|---|---|
| §4 broke the 11 new tests down as "7 debug-logging canary, 3 client library, 1 helper" | It is **6** canary cases, **1** canary-is-really-there guard, 3 client library, 1 helper. The total of 11, and the 29 → 40 file count, were right |
| §2.10 said "all six sites converted", which reads as a claim about the tree | Six pre-existing sites were converted; ruling B then added a **seventh**. A reader counting `log_expected_failure` in the tree finds seven, and all seven are the safe form |
| §4's working-tree list omitted the maintainer-authored Phase 2 gap-closure prompt (now `docs/review/phase-2-i-02-prompt.md`) | Now listed as a maintainer-authored file that post-dates this document and is not part of this work |

One defect was found in a file this task does not touch: a **pre-existing broken
anchor** in `docs/review/phase-1-submission.md` pointing at OD-14. It predates
this work, it is in a historical Phase 1 record, and it was left alone rather
than edited (§7.0.1 command 9).

## 0.1 Revision 3, against the Codex re-review

| # | Re-review finding | Severity | State |
|---|---|---|---|
| 1 | Discord mutations remain unauthorized | Raised as Blocking | **Open, and not a Phase 2 gate item** under ruling C. Real risk, unfixed, unchanged by Phase 2. [OD-17](../discovery/open-decisions.md#od-17--how-long-may-the-bot-remain-unauthorized--blocking-phase-3-planning--escalated-2026-07-31). §3.1 |
| 2 | `/trade` and `/sale` permit currency creation from unauthoritative inputs | Raised as Blocking | **Open, and not a Phase 2 gate item** under ruling C. Real risk, unfixed, unchanged by Phase 2. [OD-39](../discovery/open-decisions.md#od-39--unauthenticated-economy-mutations-through-trade-and-sale--raised-2026-07-31). §3.2 |
| 3 | Malformed read-only credentials escape the CLI's safe failure handling | Important | **Fixed** in revision 3; **completed** in revision 4 by rulings A and B. §2.8, §2.10, §2.11 |
| 4 | Audit payload validation accepts non-finite floats | Important | **Fixed**, with 15 regression tests. §2.9 |

Findings 1 and 2 are the *same* two findings carried from the previous review.
Neither has been reduced by any revision, and this document does not claim
otherwise; ruling C changes only **which gate** they are answered at.

---

## 1. Summary against the original review findings

| # | Finding | Severity | State |
|---|---|---|---|
| 1 | Discord character authorization | Open risk, deferred to its correct gate | **Open on maintainer, outside the Phase 2 gate** — [OD-17](../discovery/open-decisions.md#od-17--how-long-may-the-bot-remain-unauthorized--blocking-phase-3-planning--escalated-2026-07-31). §3.1 |
| 2 | Resource creation through `/trade` and `/sale` | Open risk, deferred to its correct gate | **Partly fixed; the rest open on maintainer, outside the Phase 2 gate** — [OD-39](../discovery/open-decisions.md#od-39--unauthenticated-economy-mutations-through-trade-and-sale--raised-2026-07-31). §3.2 |
| 3 | Stale whole-row Sheet writes | Blocking | **Contained**, with the residue documented. §2.1 |
| 4 | Phase 2 importer identity corruption | Blocking | **Fixed in revision 7.** Revision 4's fix crossed identities on a fresh-name permutation (revision 6); revision 6's remaining case-only exemption then folded with `casefold()` while the lookup folded with `lower()`, committing two characters under one name. One shared comparison policy, and a collision lookup for every spelling change. §2.2, §2.13, §2.14 |
| 5 | Importer CLI failure handling | Important | **Fixed** in revision 2; **extended** in revision 3 by finding 3 above. §2.3, §2.8 |
| 6 | Command and authorization test coverage | Important | **Partly done**; the authorization half is blocked with finding 1. §2.4 |
| 7 | Critical extension startup | Important | **Fixed.** §2.5 |
| 8 | Sheet importer credential scope | Important | **Code boundary done**; the credential itself is a deployment step. §2.6 |
| 9 | Audit payload immutability | Important | **Fixed** in revision 2; **extended** in revision 3 by finding 4 above. §2.7, §2.9 |

---

## 2. Fixes completed

### 2.1 Finding 3 — stale whole-row Sheet writes

**What was wrong.** `Actor.load_from_sheet()` read a snapshot of the row;
`Actor.sheet_updates()` wrote **all 25 managed cells** back from that snapshot,
however long afterwards. Anything another writer changed in between was
silently reverted. There are three other writers, and OD-07 established that
two of them are automated and cannot be asked to wait: the weekly living-cost
macro on column **J**, and Frank's interest macro on column **AC**.

The window is not small. A `/craft` on a legendary project rolls dice, posts to
the roll channel and waits on Discord between the read and the write.

**Can the Sheets API do compare-and-set? No.** `spreadsheets.values.batchUpdate`
has no conditional-write, no ETag precondition and no row version. There is no
API-level construct that makes a read-modify-write atomic against another
writer. This is a property of the API, not of how it is being called, and it is
why the migration plan retires Sheets rather than hardening it. What follows is
therefore containment, not a fix, and it is sized to be consistent with §15's
staged retirement rather than to build a locking layer on a store that is being
removed.

**Three changes, each fail-closed.**

1. **Write only what changed.** `Actor` snapshots its managed cells at load
   time; `sheet_updates()` diffs against that snapshot and emits only the cells
   this command actually altered. A `/work` that earns money and spends
   downtime now writes four cells (I, Q, R, S) instead of twenty-five. A macro accrual on **J**, or a Council edit to the badge, is no
   longer in the write at all, so it cannot be reverted.

   This removes the entire class of lost updates where the two writers touched
   *different* fields — which, given the bot touches money and downtime while
   the macros touch weeks-owed and debt, is very nearly all of them. What
   remains is a genuinely contended single cell: two writers changing the same
   character's gold at the same instant. In-process locks cover that for one
   bot process; nothing covers two.

2. **Confirm the row before writing to it.** `row_index` is a *position*, and a
   position is not an identity: a row inserted above shifts every row below,
   and the snapshot then addresses a different character. `verify_sheet_row()`
   reads the single cell `Characters!A{row}` immediately before the write and
   refuses if the name no longer matches. That narrows the window from the
   whole command to one API call, and fails closed when it has already moved.
   `Trade.perform_trade()` confirms **both** rows before either is written,
   because the two sides go out as one `batch_update`.

   Cost: one extra single-cell read per mutating command. A command that
   changed nothing skips it entirely.

3. **Refuse a duplicate name instead of guessing.** `load_from_sheet()` matched
   the first row with the name and wrote to it. Two characters sharing a name
   meant an arbitrary choice followed by a mutation. It now raises
   `AmbiguousActorError` and names the rows.

**Regression tests** — `tests/test_actor_sheet_writes.py`, 14 tests, no
credentials and no network. The ones the finding asked for by name:

- `test_a_macro_accrual_during_the_command_survives_the_save` — column J is
  advanced by the macro mid-command and is neither written nor reverted;
- `test_a_council_edit_to_an_unrelated_field_survives_the_save` — badge and
  level are corrected mid-command and survive;
- `test_franks_interest_column_is_never_written` — column AC;
- `test_a_row_that_moved_under_the_actor_refuses_the_write`;
- `test_two_characters_sharing_a_name_are_refused_rather_than_guessed`;
- `test_a_trade_verifies_both_rows_before_writing_either`.

**What is still not covered, and honestly.**

| Case | State |
|---|---|
| Council edit / macro on a field the command did not touch | **Contained** — not written |
| Two bot commands, same character, same process | Contained by `actor_locks` (unchanged) |
| Two bot commands, same character, **two processes** | **Not contained.** No cross-process lock exists. Only one `freedom-bot` runs today; a second would reintroduce it |
| Council edit to the *same* field, inside the one-API-call window | **Not contained.** Requires CAS, which the API lacks |
| Row insert/delete during the window | Narrowed to one API call, fails closed |
| Character rename during the window | Fails closed — the name check refuses |
| Duplicate names | Refused at load |

**The smallest safe alternative for the residue, consistent with the plan:** it
is not a better Sheets lock, it is the per-feature cutover that OD-38 (initial
authority) and OD-36 (macros) already describe. Once a value's authority moves
to PostgreSQL, `SELECT … FOR UPDATE` and the existing `version` column give real
compare-and-set, and the Sheet becomes a projection. Building a lock service for
a store scheduled for retirement would be work thrown away.

### 2.2 Finding 4 — importer identity corruption (revision 4; **superseded by §2.13**)

> **This section describes revision 4's fix, which was incomplete.** It closed
> the two cases below and left a third — a permutation of mapped rows in which
> every displaced character is renamed to a fresh name — still committing the
> wrong identity. §2.13 is the current behaviour; this section is retained
> because the reasoning in it is what §2.13 corrects. The claims *"a mapped-name
> change is committed only in a run where none of them is true"* and *"a
> legitimate rename still works"* below are **no longer true of the code**.

**What was wrong.** `_update()` treated a mapped row whose name had changed as
an in-place rename unless the mapped character was found by name at another row
in the same import. Two edits defeat that check completely:

- **an inserted row plus a rename** — the displaced character is renamed, so its
  old name is not in the index and the check finds nothing;
- **an inserted row plus a malformed displaced row** — the displaced character
  failed validation, is not a candidate at all, and again is not in the index.

In the first case the run **commits**: the existing character is given the
newcomer's identity, and a second character is minted for the renamed one. That
is silent identity corruption, and nothing afterwards can detect it — the audit
row records a rename, which is what the importer believed it was doing.

**Revision 4's fix, and why its shape was not enough.** A rename and a shift are
*indistinguishable from the changed row alone*. No cleverer name heuristic fixes
that; a better heuristic just moves where it fails. Revision 4 accepted the first
half of that sentence and then made the decision from the whole run instead —
which is the same mistake one level up, because the *run* does not distinguish
them either.

Every candidate is resolved before any is decided (`_Resolution`, still true),
and revision 4 characterised the run by `_RunStructure`: whether it contained a
row that was added, a mapped row that was removed, a row that failed validation,
a dangling mapping, a detected shift, or a name collision. ~~A **mapped-name
change is committed only in a run where none of them is true.** Otherwise it is
`ambiguous_name_change` and the run stops.~~ **Superseded (§0.3).** All six are
false for a permutation whose displaced characters are renamed, and revision 4
committed it. `_RunStructure` and `ambiguous_name_change` no longer exist; every
semantic mapped-name change now blocks (§2.13).

Two narrower checks were added with it and both survive: a rename onto a name a
*different* character already holds is `name_collision`, and the pre-existing
`row_identity_shift` check is unchanged.

Revision 4 refused some genuine renames — renaming a character in the same
sitting as adding one was enough. Revision 6 refuses all of them. The trade is
the one stated in the review instruction and in the ops doc, applied to the full
set of inputs it always covered: a false refusal costs a second import run; a
wrong rename costs a character its identity, permanently and invisibly.

**Regression tests** added by revision 4, all of which fail against the
revision-3 implementation where the finding says they should. Names and expected
codes as revision 6 leaves them:

| Test | Case |
|---|---|
| `test_an_inserted_row_beside_a_rename_is_blocked_rather_than_committed` | inserted row + simultaneous rename |
| `test_a_rename_is_blocked_when_the_displaced_row_failed_validation` | displaced row malformed |
| `test_several_shifted_rows_with_one_renamed_are_all_blocked` | multiple shifted rows, one renamed |
| `test_a_rename_onto_a_name_another_character_holds_is_blocked` | rename into an existing name |
| ~~`test_an_unambiguous_in_place_rename_is_still_applied`~~ | **removed in revision 6** — there is no unambiguous mapped rename. Replaced by `test_a_single_mapped_name_change_is_reported_for_reconciliation` |
| `test_correcting_a_names_capitalisation_is_an_update_not_a_refusal` | case is not identity (renamed in revision 6) |
| `test_repeating_an_unchanged_import_is_never_refused` | unchanged repeat import (renamed in revision 6) |
| `test_a_blocked_run_rolls_back_characters_mappings_and_audit_events` | rollback covers all three |
| `test_a_failure_part_way_through_a_run_rolls_the_whole_run_back` | an exception mid-run rolls back |
| `test_a_refused_name_change_leaves_the_database_exactly_as_it_was` | the same, against real PostgreSQL (renamed in revision 6) |

The failure of the first four against the old behaviour was **verified, not
assumed**: the two new guards were temporarily neutered, the suite run, and the
file restored and confirmed byte-identical by `diff`. Result with the guards
removed: **4 failed, 21 passed**, and the four are exactly the four "must
block" cases. The rename-still-works and unchanged-repeat tests passed both
with and without the guards, which is the point of including them.

### 2.3 Finding 5 — importer CLI failure handling

Expected operational failures now become a short instruction and a defined exit
code instead of a traceback:

| Code | Meaning |
|---|---|
| 0 | clean |
| 1 | the run reported errors and wrote nothing |
| 2 | database target, Sheets credential or Sheet layout refused before importing |
| 3 | the Sheet could not be read |
| 4 | the database could not be reached or refused the work |
| 5 | a conflict — concurrent import, or a row edited mid-run |

Codes 3–5 print a fixed string. Not a redacted exception — a fixed string, so
there is no path by which a DSN, a service-account address, a SQL statement or
a Google error body reaches the terminal. The exception is attached to a
`logger.debug` call, which is silent under default logging (it is below
`logging.lastResort`'s WARNING threshold, so the traceback does not leak that
way either) and recoverable by an operator who configures logging.

Rollback is not conditional on any of this: `SqlAlchemyUnitOfWork.__exit__`
rolls back and closes on any exception leaving its block. `engine.dispose()` is
in a `finally`. Unexpected programming errors still propagate, per the
repository convention and the review's allowance.

Tests: `tests/test_import_cli.py`, 8 new. Each failure test asserts the exit
code *and* runs the whole of stdout and stderr through a regex for DSNs,
private-key headers, SQL statements and traceback frames.

### 2.4 Finding 6 — command and authorization test coverage

`tests/test_command_boundaries.py`, 11 tests, covering the behaviour this change
altered: channel refusal happens before `defer()`, non-finite and negative
inputs are refused, and **a refused Sheet write is not reported as a completed
sale** — the caller is told the sale did not happen, ephemerally.

No general command-test framework was built; each test constructs the cog and
calls its callback with a small fake context, on its own `asyncio.run` loop.
`config` and `connectors.sheets` are stubbed in `sys.modules`, because the real
`config` reads `.env`.

The **authorization half is absent on purpose** and is reported with finding 1.
There is no "unauthorized caller denied" test because there is nothing to deny
with; a test of the current behaviour would pin the gap rather than close it.
The test design the eventual boundary needs is in §3.1.

Also not covered: retries and concurrent duplicate mutations. Discord
interaction IDs are not used for idempotency anywhere in the bot yet — that is
Phase 5's `use the Discord interaction ID for idempotency` deliverable — so
there is no mechanism to test.

### 2.5 Finding 7 — critical extension startup

`main.py` logged a failed extension and started anyway. If the failed extension
was `ext.error_handler`, every unhandled command error fell back to Pycord's
default handling instead of the safe ephemeral message, and raw exception text
reached Discord.

`ext/loader.py` now raises `ExtensionLoadError` on the first failure and
`main()` returns a non-zero exit code without calling `bot.run()`. All eleven
entries in `EXTENSIONS` are required, including the error handler.

Music has been removed from the implementation under the amended
[OD-40](../discovery/open-decisions.md#od-40--music-platform-work--closed-2026-07-31-amended-2026-07-31)
ruling — recorded as a duplicate "OD-38" until 2026-08-01. It is **removed, not
deferred**: it is not part of extension loading and no platform phase reinstates
it. §2.12 records the verification.

### 2.6 Finding 8 — Sheet importer credential scope

`adapters/sheets/read_only.py` defines the one-method port the importer needs
and selects a `.../auth/spreadsheets.readonly` credential when
`SHEET_READONLY_SERVICE_ACCOUNT_JSON` is configured, falling back to the shared
read/write credential with a warning on stderr when it is not.

**The live bot's `connectors.sheets` is not touched**, and no credential was
read, created or modified. The narrow credential is a deployment step: a second
Google service account with Viewer on the spreadsheet. It is documented in
`docs/operations/sheet-import.md` and `.env.example`, both with placeholders
only.

Falling back rather than refusing is deliberate: refusing would block the import
for a reason the operator cannot fix from the command line.

### 2.7 Finding 9 — audit payload immutability

`AuditEvent` froze only the outer mapping, so the payload this platform actually
writes — `{"changes": {"level": {"from": 4, "to": 5}}}` — was mutable two levels
down.

The freeze is now recursive over JSON-like values: mappings become
`MappingProxyType`, sequences become tuples, scalars pass through, and anything
else (a `set`, `bytes`, a non-string key, an arbitrary object) is refused at
construction with `UnsupportedAuditPayloadError` rather than silently coerced or
left to fail at the driver.

JSON serialization is preserved by converting back at the persistence boundary:
`AuditEvent.json_payload()` returns plain dicts and lists, and
`SqlAlchemyAuditRepository.record()` calls it. Tests cover nested mutation
attempts (`tests/test_audit_events.py`, 9 tests) and a real JSONB round trip of
a nested payload (`tests/test_database_repositories.py`).

### 2.8 Re-review finding 3 — malformed credentials escaped the CLI

**What was wrong.** `adapters/sheets/read_only.py` translated only
`json.loads` failures into `SheetCredentialError`. Everything after that was
unguarded, so a `SHEET_READONLY_SERVICE_ACCOUNT_JSON` that *parsed* but was not
a usable service-account key reached the operator as a traceback instead of the
documented exit code 2. Verified against the installed libraries, the escaping
cases are:

| Configured value | What escaped |
|---|---|
| Valid JSON, but not an object (`[…]`, `"…"`, `5`) | `AttributeError`/`TypeError` from inside the Google library |
| Object missing `client_email`/`token_uri`/`private_key` | `google.auth.exceptions.MalformedError` |
| A field of the wrong JSON type | `google.auth.exceptions.InvalidValue` |
| A `private_key` that is not a key | `MalformedError`, or `binascii.Error` on a corrupt PEM body |
| Google libraries not installed with the variable set | `ImportError` |
| A transport failure while building the client | `OSError` and friends |

**Why the exception text may not be printed, concretely.** Google's own messages
quote the offending value back. A `private_key` field holding a JSON object
produces, verbatim:

```text
InvalidValue("{'a': 1} could not be converted to unicode")
```

A malformed but *real* key would be quoted the same way. So this is not a
theoretical leak: rendering the cause is a path from a credential file to a
terminal, a shell history and a CI log. Every message below is therefore a fixed
string, and the cause goes to `logger.debug`, which is silent under default
logging and available to an operator who turns it on. The same rule the
revision-2 CLI already followed, now applied one layer down.

**The fix.**

1. `_read_only_credentials()` is split out of `_build_read_only_reader()` so the
   credential half is reachable without a Google client. It validates that the
   parsed document is a JSON object, then translates `GoogleAuthError`,
   `ValueError` and `TypeError` from `Credentials.from_service_account_info()`
   into `SheetCredentialError` — `MalformedError` and `InvalidValue` are
   `ValueError` subclasses, a corrupt PEM surfaces as `binascii.Error`, also a
   `ValueError`, and an unexpected JSON type can reach the crypto layer as a
   `TypeError`. A missing Google library becomes a `SheetCredentialError` naming
   the dependency rather than an `ImportError`.
2. **Unexpected errors still propagate.** The `except` clauses are the shapes
   Google's construction is documented and observed to raise, around a single
   library call. A defect in this repository must not be reported to an operator
   as bad configuration, so nothing broader is caught.
3. The CLI additionally translates a *transport* failure while building the
   client — DNS, a proxy, the discovery document — into exit **3** ("the Sheet
   could not be read") rather than exit 2. A network blip is not a bad
   credential, and telling an operator to check their key would send them the
   wrong way.

**Regression tests** — `tests/test_import_cli.py`, 11 new. All credential data
is synthetic and non-secret: obviously fake strings, a `.invalid` service-account
address, no real account, and no network. Construction fails long before any
client is built or any request made.

| Test | Case |
|---|---|
| `…_is_refused_not_raised[invalid JSON]` | truncated document |
| `…_is_refused_not_raised[valid JSON that is not an object]` | a JSON array |
| `…_is_refused_not_raised[incomplete service account]` | valid JSON, valid shape, required fields missing |
| `…_is_refused_not_raised[unusable private key]` | complete document, `private_key` is not a key |
| `…_exits_misconfigured_and_says_nothing[×4]` | each of the four through `main()`: asserts exit **2**, `Sheet credential refused`, the leak regex over **both** stdout and stderr, and that none of `not-a-key`, `synthetic@`, `synthetic-test-project` or `BEGIN` appears |
| `…_really_does_reach_googles_construction` | guards the above from passing for the wrong reason if Google ever accepted the document |
| `…_missing_google_library_is_a_refusal…` | the variable set without the libraries installed |
| `…_transport_failure_building_the_client_is_reported_as_unreadable` | exit **3**, not 2, and no `Errno` in the output |

Both required cases from the instruction — invalid JSON, and valid JSON with an
invalid/incomplete service-account structure — are covered, each asserted for
both the exit code and safe output.

### 2.9 Re-review finding 4 — non-finite floats in audit payloads

**What was wrong.** `_freeze_payload()` accepted any `float`. `NaN`, `inf` and
`-inf` are floats, `json.dumps` emits them happily as the bare tokens `NaN`,
`Infinity` and `-Infinity`, and they survived `AuditEvent.json_payload()` intact.
PostgreSQL then refuses all three. Verified against the disposable database
rather than assumed:

```text
$ psql -d freedom_test -c "SELECT '{\"a\": NaN}'::jsonb;"
ERROR:  invalid input syntax for type json
DETAIL:  Token "NaN" is invalid.
```

The consequence is worse than a bad audit row. The audit write shares the
transaction with the change it describes, so the refusal fails **the whole
audited mutation** — and it fails at the driver, at commit, having already done
the work.

**The fix.** `_freeze_payload()` rejects a non-finite float wherever it appears,
which is recursive because that function already is: it descends mappings and
sequences to freeze them, so the check reaches a value nested inside either, at
any depth. It raises `UnsupportedAuditPayloadError` at `AuditEvent`
construction — the call site, with the payload path — rather than at the driver
hours of debugging later.

The refusal is deliberately narrow: only the three values PostgreSQL cannot
store. Finite floats, integers, booleans, strings, nulls, mappings and sequences
all pass exactly as before.

**Regression tests** — 14 in `tests/test_audit_events.py` and 1 in
`tests/test_database_repositories.py`:

| Test | Case |
|---|---|
| `…_refused_at_construction[nan/inf/-inf]` | each of the three at the top level |
| `…_nested_in_a_mapping_is_refused[×3]` | `payload.changes.balance.to` — the shape this platform actually writes |
| `…_nested_in_a_sequence_is_refused[×3]` | `payload.amounts[2]` |
| `…_inside_a_sequence_of_mappings_is_refused[×3]` | `payload.rows[0].rate` |
| `…_refusal_names_the_path_and_no_player_state` | the message identifies the path and does not quote the surrounding record |
| `…_finite_numbers_and_every_other_supported_value_still_pass` | `0.0`, `-0.0`, `0.125`, `1e308`, `5e-324`, integers, booleans, null, strings, nested |
| `…_finite_numbers_survive_the_jsonb_round_trip_at_every_depth` | **real PostgreSQL**: a finite nested payload stored and read back through the JSONB column |

The database test is the other half of the refusal: rejecting `NaN` is only
correct if finite values still store, so it round-trips floats nested in both a
mapping and a sequence. It uses ordinary magnitudes on purpose — JSONB stores a
number as `numeric`, so `1e308` comes back as the exact 308-digit integer rather
than the float that went in. That is a faithful JSON round trip rather than a
defect, but it is a different property, and it is noted in the test rather than
asserted around. **The test is not weakened when PostgreSQL is unavailable**: it
carries the existing `database` marker and the shared fixture *skips* the file
outright, so an unconfigured run cannot silently pass a database assertion.

### 2.10 Ruling A — expected exceptions were still reaching the logs

**What was wrong.** Revisions 2 and 3 kept the exception out of the *terminal*
and then attached it to a `logger.debug(..., exc_info=error)` call, on the
argument that DEBUG is silent by default. That argument does not hold:

- **Debug logging is still logging.** `logging.lastResort` suppressing DEBUG is
  a default, not a control. One `--log-level=DEBUG`, one
  `logging.basicConfig(level=DEBUG)` in any dependency, or one journald unit
  configured for debug, and the record is written to a file that outlives the
  run — a terminal scrollback, a CI job log, a log collector.
- **What the record contained was the whole exception.** `exc_info` renders the
  message *and* the traceback. Concretely: Google's `InvalidValue` quotes the
  offending credential field back verbatim; SQLAlchemy's `DatabaseError.__str__`
  renders the failing SQL statement, its bound parameters and the driver's
  message, which for a connection failure carries host, port, user and database.

So the six sites were a path from a service-account key or a DSN to a retained
log, and the operator-facing fixed strings in front of them did not close it.

**The fix.** `adapters/safe_logging.py` defines the whole logging vocabulary for
an expected failure: a fixed category chosen at the call site, and
`type(error).__name__`. Nothing else. The exception is never interpolated, never
serialized, and never passed as `exc_info`.

```text
expected failure category=database_unavailable exception_type=OperationalError
```

The class name is kept deliberately: it is an identifier in installed source
code rather than data derived from a credential, a database or a player, and it
is the part that actually distinguishes a `MalformedError` from an `InvalidValue`
from a `binascii.Error`. The cause still hangs off the exception through
`raise … from error`, where a debugger can reach it and no log can.

All six pre-existing sites converted — four in `tools/import_sheet_characters.py`
(`sheet_read_failed`, `import_conflict`, `database_unavailable`,
`sheets_client_unreachable`) and two in `adapters/sheets/read_only.py`
(`google_auth_library_missing`, `read_only_credential_refused`). Ruling B then
added a seventh (`google_client_library_missing`, §2.11), so a reader counting
`log_expected_failure` call sites in the tree finds **seven**, not six, and every
one of them is the safe form. Exception scopes and caught types are unchanged, so
an unexpected programming defect still propagates rather than being reported to
an operator as bad configuration.

**Regression tests** — 8 new in `tests/test_import_cli.py`: 6 canary tests over
the credential, database, conflict, sheet-read and transport paths, plus the two
named at the end of this section. Each canary test turns
logging **on**: root logger at `DEBUG`, with a real `logging.Formatter` (which is
what appends a traceback when a record carries `exc_info`) writing to a stream
the test reads, `caplog` at `DEBUG`, and `capsys` over stdout and stderr. Each
plants a **synthetic canary** inside the exception and asserts it appears on none
of the four surfaces, that no captured record carries `exc_info` or `exc_text`,
and — so the test cannot pass vacuously — that the safe category and class name
*were* recorded.

| Canary | Planted in |
|---|---|
| `CANARY-PRIVATE-KEY-MATERIAL-9f2a` | a `private_key` field Google quotes back verbatim |
| `canary-account@synthetic-canary-project.iam.invalid` | the service-account address |
| `postgresql+psycopg://canary_user:CANARY-DB-PASSWORD-3e11@…` | the DSN inside an `OperationalError`'s cause |
| `SELECT canary_column FROM canary_table WHERE id = 'CANARY-SQL-7c04'` | the statement inside `OperationalError` / `IntegrityError` |
| `canary-host-5b93.sheets.googleapis.invalid` | the transport `OSError` |

All of it is invented; no real credential, database, host or player value appears
in the file. `test_the_canary_credential_really_is_quoted_back_by_google` guards
the credential case from passing because the canary was never there in the first
place, and
`test_the_safe_diagnostic_records_the_category_and_class_and_nothing_else`
covers the helper directly.

The existing safe-output and exit-code assertions were not weakened: every one of
them still runs, and the new tests are additional surfaces over the same runs.

### 2.11 Ruling B — the Google *client* library was still unguarded

**What was wrong.** `_read_only_credentials()` translated a missing
`google-auth` into the documented dependency refusal, but
`_build_read_only_reader()` then imported `googleapiclient.discovery` **after**
it. `google-auth` and `google-api-python-client` are separate distributions, so
an environment can hold one without the other — a partial install, or a
requirements file applied in part. In that environment the credential half
succeeded and the next line raised a bare `ImportError`, which reached the
operator as a traceback instead of exit **2**.

**The fix.** The discovery import is wrapped and raises the same
`SheetCredentialError` with the same fixed `GOOGLE_LIBRARIES_MISSING_MESSAGE`,
so the operator sees the same sentence and the same exit code whichever half is
missing — the remedy is identical, and naming the half would be the only
difference. **Only the import statement is guarded**: nothing broader, so an
`ImportError` from this repository's own code still propagates as the defect it
is.

**Regression tests** — 3 new, none of which needs a service-account key or a
network. `_read_only_credentials` is replaced by a sentinel so the credential
half is out of the way, and `sys.modules["googleapiclient.discovery"]` is set to
`None`, which is how an uninstalled distribution fails.

| Test | Case |
|---|---|
| `…_missing_google_client_library_is_a_refusal_rather_than_an_import_error` | the adapter translates it |
| `…_missing_google_client_library_exits_misconfigured` | exit **2** through `main()`, the same fixed sentence, no leak |
| `…_client_library_guard_does_not_swallow_an_unrelated_import_error` | an `ImportError` from elsewhere still propagates — the guard is around one import, not the function |

### 2.12 Rulings C and D — documentation, and the music verification

**Ruling D — the duplicate identifier.** "OD-38" named two decisions: *Initial
authority during Sheet migration* and *Music platform work*. The music decision
is now **OD-40**, in a new *Product scope* section of `open-decisions.md`; OD-38
keeps its original meaning, which §2.1 of this document relies on. References
were repaired in `open-decisions.md`, `command-inventory.md`, `.agents/AGENTS.md`
and here. All forty identifiers were checked for uniqueness (§7.1 command 8), and
the in-document anchors now resolve — two that were already broken before this
task, at OD-18 and OD-36, were repaired with them.

Documents written before 2026-08-01 that say "OD-38" for music are accurate
records of what they said at the time and were left alone; §12 of the plan and
every current document say **removed, not deferred**.

**The music verification** was read-only. No live Lavalink process was inspected,
stopped or reconfigured — repository removal is not authorization for
live-service administration. Results are tabulated at
[OD-40](../discovery/open-decisions.md#od-40--music-platform-work--closed-2026-07-31-amended-2026-07-31):
no runtime attachment, no commands, no Wavelink or `yt-dlp` dependency, no
`ENABLE_MUSIC` / `LAVALINK_*` / `YTDLP_*` configuration, no Lavalink template, no
cookie fixture, no music-specific test. Two residues are outside the
repository's tracked content and were deliberately left: `infra/lavalink/` is an
empty working-tree directory that git does not track, and `yt-cookies.txt` is a
gitignored credential-shaped file that was **not read, printed or modified** and
whose deletion is an operator decision.

**Ruling C** is §3.

### 2.13 Revision 6 — a mapped semantic name change is never applied

**What was wrong** is stated in full in §0.3: revision 4's six run-level signals
are all false for a permutation of mapped rows whose displaced characters are
each renamed to a fresh name, so the importer committed each character's new
identity onto the wrong character. The input is observationally identical to two
in-place renames, so no additional signal can fix it.

**The fix.**

1. `_Resolution.is_name_change` became `is_semantic_name_change`, and a `True`
   answer now **always** blocks the row. There is no path from a mapped semantic
   name change to a write.
2. `_refuse_name_change`, which returned `None` for "commit it", became
   `_name_change_refusal`, which returns a code and a message unconditionally.
   The run-level view now only chooses **how the refusal is explained** —
   `row_identity_shift` where the mapped character is visible at another row,
   `name_collision` where the new name is taken, `mapped_name_change`
   otherwise — never whether to refuse.
3. `_RunStructure`, `_structure_of` and `_is_shifted` are deleted. Their only
   consumer was the decision that is gone, and leaving them would leave a
   false claim in the tree.
4. The module docstring, the `_Resolution` docstring and
   `docs/operations/sheet-import.md` are rewritten around the permutation
   argument rather than around "ambiguity".

Case-only corrections, non-identity updates, creations, idempotent repeats,
`absent_from_source` warnings, the all-or-nothing transaction, the audit
vocabulary and every exit code are unchanged. Nothing outside
`application/sheet_import.py` and its two test files changed in code.

**Regression tests** — `tests/test_sheet_import_service.py` (26 → 31) and
`tests/test_sheet_import_database.py` (6 → 7):

| Test | What it proves | File |
|---|---|---|
| `test_swapped_rows_with_fresh_names_are_blocked_rather_than_crossed` | the reported defect: two mapped rows swapped, both renamed fresh — blocked, neither display name changed, `sheet_row_mappings` identical, no audit row added | service |
| `test_a_three_row_cycle_with_fresh_names_is_blocked_atomically` | the same at length three, A→B→C→A, blocked on all three rows atomically | service |
| `test_a_single_mapped_name_change_is_reported_for_reconciliation` | one changed name in an otherwise spotless run is reported, not applied; the message names both the stored and the new name. Replaces `…_unambiguous_in_place_rename_is_still_applied` | service |
| `test_two_independent_looking_renames_are_blocked_with_no_structural_signal` | two changed rows that are *not* a permutation are blocked too, with every former signal false — asserted as `codes == {"mapped_name_change"}` | service |
| `test_a_renamed_row_never_mints_a_second_character_for_the_same_mapping` | a renamed mapped row is still not a second character; it blocks with the mapping intact | service |
| `test_correcting_a_names_capitalisation_is_an_update_not_a_refusal` | the case-only correction still imports, and a creation beside it still commits | service |
| `test_the_non_identity_fields_still_update_under_an_unchanged_name` | long name, level and active still update, and the audit payload records all three changes | service |
| `test_repeating_an_unchanged_import_is_never_refused` | an unchanged repeat is clean, idempotent and writes no audit noise | service |
| `test_the_dry_run_and_the_apply_reach_the_same_reconciliation_decision` | dry run and apply produce identical entries **and identical issues**, and neither commits | service |
| `test_a_blocked_run_rolls_back_characters_mappings_and_audit_events` | the fake unit-of-work rollback covers all three stores | service |
| `test_a_fresh_name_permutation_rolls_back_characters_mappings_and_audit` | **real PostgreSQL**: the permutation refused through the migrated schema, with the `(row_index, character_id, display_name, version)` join checked pairwise rather than by row count — a silent re-key would keep the counts identical — and no new `correlation_id` in `audit_events` | database |
| `test_a_refused_name_change_leaves_the_database_exactly_as_it_was` | the revision-4 case, retitled and re-coded for `mapped_name_change` | database |

**Proved to fail without the fix, not assumed.** The refusal was temporarily
neutralised: `_name_change_refusal`'s general branch was made to return `None`
and `_update` allowed to fall through when it did — the shift and collision
branches left in place, so what was removed is exactly "refuse a mapped name
change the run cannot otherwise explain". `tests/test_sheet_import_service.py`
then reported **9 failed, 22 passed**:

| Failing test | Why |
|---|---|
| `…_swapped_rows_with_fresh_names_are_blocked_rather_than_crossed` | the reported defect |
| `…_a_three_row_cycle_with_fresh_names_is_blocked_atomically` | the reported defect at length three |
| `…_a_single_mapped_name_change_is_reported_for_reconciliation` | the single rename commits again |
| `…_two_independent_looking_renames_are_blocked_with_no_structural_signal` | two changed rows commit again |
| `…_a_renamed_row_never_mints_a_second_character_for_the_same_mapping` | same, one mapped row |
| `…_the_dry_run_and_the_apply_reach_the_same_reconciliation_decision` | with the refusal gone there is no decision to agree on |
| `…_an_inserted_row_beside_a_rename_is_blocked_rather_than_committed` | revision 4 caught these three through `_RunStructure`, which revision 6 removes; with the general refusal neutralised as well, nothing catches them |
| `…_a_rename_is_blocked_when_the_displaced_row_failed_validation` | as above |
| `…_several_shifted_rows_with_one_renamed_are_all_blocked` | as above |

The neutralised importer was also run directly against the reported input, so
the evidence is the corruption itself rather than a test's expectation of it:

```text
applied: True issues: []
A (was Test Smith A, mapped row 3) -> Test Fresh X
B (was Test Smith B, mapped row 4) -> Test Fresh Y
```

The edit that produced that input renamed the character at row 3 — physically
**B** — to `Test Fresh X`. The run committed it onto **A**.

`application/sheet_import.py` was restored from a copy taken before the edit and
confirmed **byte-identical with `cmp`** (and by matching MD5), and the suite
re-run green: 31 passed. No other file was touched during the check, and no
working-tree change of the maintainer's was at risk. The only edit made to the
file *after* the proof was a four-line code comment above the
`row_identity_shift` branch — no executable line differs from the version the
proof ran against, and the suite was re-run green afterwards. §7.0 command 8.

### 2.14 Revision 7 — one comparison rule, and a lookup for every spelling change

**What was wrong** is stated in full in §0.4: two Unicode folds answering two
different questions, wired to the wrong questions, with the collision lookup
skipped whenever the wider fold said "capitalisation only".

**The fix.**

1. **`domain/names.py` is new**: `DisplayName`, an immutable value object over
   the raw name, with `is_exactly`, `differs_only_in_capitalization`,
   `claims_same_identity_as`/`identity_key` and `is_semantic_change_from`. It
   imports `unicodedata` and `dataclasses` and nothing else — no Sheet, no
   database, no configuration — so it sits in `domain/` beside `Character`.
2. `Character.name` and `SheetCharacterCandidate.name` expose a comparable name
   rather than bare text, so a caller reaching for `.display_name.casefold()`
   has to do so deliberately.
3. `application/sheet_import.py`: `_Resolution.is_semantic_name_change` is the
   policy's `is_semantic_change_from`; a new `_Resolution.is_spelling_change`
   drives the lookup decision; `_resolve` looks a name up for every creation and
   every non-exact mapped name, where it previously skipped the lookup on
   `casefold()` equality; `_update` blocks a capitalisation-only change with
   `name_collision` when another character claims the name; `_rows_by_name` keys
   on the identity key.
4. `adapters/sheets/character_import.py`: the parser's in-run duplicate check
   keys on the identity key rather than `casefold()` directly — the same key, now
   named and shared rather than re-derived.
5. `adapters/database/repositories.py`: `find_by_display_name` compares in
   Python over the `characters` rows instead of asserting a SQL `lower()`
   equivalence that does not hold. The cost and the threshold that would trigger
   a normalized/indexed schema are documented in the docstring.
6. `tests/fakes.py`: the fake repository uses the same policy, so the
   application suite can no longer prove a decision the database would not
   reach — which is how this defect stayed invisible to 600 passing tests.
7. `application/repositories.py`: the `CharacterRepository` protocol now states
   the comparison an implementation must answer for, and says why a narrower one
   is the defect.

Issue codes, outcome shapes, transaction boundaries, audit vocabulary, exit
codes and idempotency are unchanged. No migration, no dependency, no
configuration variable.

**Regression tests** — 9 added to `tests/test_sheet_import_service.py` (39
total), a new `tests/test_display_name_policy.py` (86 collected, table-driven),
a new shared table `tests/display_name_cases.py`, and 6 added to
`tests/test_sheet_import_database.py` (24 collected, real PostgreSQL).

| Test | What it proves | File |
|---|---|---|
| `…_sharp_s_expansion_never_commits_two_characters_under_one_name` | **the reported reproduction**: refused, both identities, both versions, the mapping and the audit log unchanged, two distinct display names still | service, **and database** |
| `…_a_sharp_s_expansion_is_a_semantic_name_change_not_a_capitalisation_fix` | `Test Straße -> Test STRASSE` alone is `mapped_name_change` | service |
| `…_an_unmapped_sharp_s_variant_never_mints_a_second_character` | creation uses the identity key: `unmapped_name_collision`, no second character, no mapping | service, **and database** |
| `…_a_capitalisation_only_change_onto_a_taken_name_is_a_collision` | the permitted change is still looked up: `name_collision`, nothing committed | service, **and database** |
| `…_a_capitalisation_only_change_applies_when_nobody_else_claims_the_name` | `Test Smith A -> TEST SMITH A` still applies, with the audit payload recording it | service |
| `…_an_exact_non_ascii_name_is_unchanged_and_idempotent` | an exact non-ASCII name is `unchanged` twice over, with no issue and no audit row | service |
| `…_the_dry_run_and_the_apply_agree_on_a_normalisation_refusal` | identical entries *and* identical issues; neither commits | service, **and database** |
| `…_a_valid_update_beside_a_normalisation_refusal_rolls_back_with_it` | a mixed run — real update, refusal, creation — rolls back characters, versions, mappings and audit together | service, **and database** |
| `test_the_policy_classifies_every_case_as_the_table_says` | the rule itself, over the shared 12-case table | policy |
| `test_the_three_relations_are_mutually_exclusive_and_exhaustive` | exactly one of exact / capitalisation-only / semantic holds, per case | policy |
| `test_nothing_identity_neutral_escapes_the_collision_key` | **the containment the correction rests on**: anything applied without a human is visible to the collision lookup | policy |
| `test_every_relation_is_symmetric` | which name is the stored one cannot change the answer | policy |
| `…_parser_reports_a_duplicate_exactly_when_the_names_claim_one_identity` | the parser agrees with the policy over the whole table | policy |
| `…_fake_repository_matches_exactly_when_the_names_claim_one_identity` | the fake agrees | policy |
| `…_import_service_decides_each_case_the_way_the_table_classifies_it` | the service agrees: unchanged / updated / blocked per relation | policy |
| `test_the_postgresql_repository_matches_the_shared_display_name_policy` | **the adapter agrees, against real PostgreSQL**, over the same table | database |

The table (`tests/display_name_cases.py`) covers ordinary ASCII case changes,
German sharp-s expansion and its capital `ẞ`, exact non-ASCII names, NFC/NFD
canonical equivalence, Turkish dotted/dotless `i`, and two plainly different
names.

**Proved to fail without the fix, not assumed.** Two separate proofs, because
the defect spans two layers:

1. **The application layer.** The nine service tests were written and run
   *before* any production file was edited: **6 failed, 33 passed**. The failures
   were `…_sharp_s_expansion_is_a_semantic_name_change_not_a_capitalisation_fix`,
   `…_sharp_s_expansion_never_commits_two_characters_under_one_name`,
   `…_an_unmapped_sharp_s_variant_never_mints_a_second_character`,
   `…_a_capitalisation_only_change_onto_a_taken_name_is_a_collision`,
   `…_the_dry_run_and_the_apply_agree_on_a_normalisation_refusal` and
   `…_a_valid_update_beside_a_normalisation_refusal_rolls_back_with_it`. The
   other three are guards that must pass either way. The standalone
   reproduction above was run first, against the untouched tree.
2. **The PostgreSQL layer.** With everything else corrected,
   `SqlAlchemyCharacterRepository.find_by_display_name` alone was reverted to the
   SQL `lower()` form and the database suites re-run: **4 failed, 40 passed** —
   the `sharp s expansion`, `sharp s expansion, lower` and
   `canonically equivalent` rows of the repository-policy test, and
   `…_an_unmapped_sharp_s_variant_creates_no_second_character_in_postgresql`.
   That is the evidence that a mocked or fake repository would not have given.
   The file was restored from a copy taken beforehand and confirmed
   **byte-identical by `cmp` and by MD5**, and the suites re-run green: 44
   passed. §7.0.2 commands 8 and 9.

Note which test did *not* fail in proof 2:
`…_a_sharp_s_expansion_never_commits_two_characters_under_one_name` passed with
the `lower()` adapter, because there the imported name is byte-identical to the
other character's stored name and SQL `lower()` finds it. The adapter's fold
matters when the *stored* name differs from the queried one by the fold — which
is exactly the unmapped-creation case that did fail. Both are needed; neither
alone covers the defect.

---

## 3. Findings outside the Phase 2 gate

**Both remain open, real and unfixed. Neither blocks the Phase 2 review gate.**

That second sentence is a maintainer ruling of 2026-08-01 (ruling C), not an
assessment by this document, and it is about *sequencing*, not severity:

- The approved Phase 2 gate is **data integrity and migration safety** for
  import/reconciliation (plan §12). Both findings are in the legacy Discord
  command surface, which is outside it.
- **Phase 2 neither introduced nor worsened either one.** The importer writes no
  `character_access` row, no `discord_users` row and no authorization state at
  all; it imports identity only — display name, long name, level, active flag —
  and touches no currency, no inventory and no sale or trade path. No Discord
  command calls any code Phase 2 added. The two Phase 2-era touches to the
  command surface both *reduce* exposure: `/sale` refuses a non-finite cost, and
  a refused Sheet write is reported as a failure rather than as a completed sale.
- Treating them as Phase 2 blockers created a **deadlock**. Every containment
  option for OD-17 depends on identity links that only Phase 3 creates, so
  Phase 2 could never be approved and Phase 3 could never start.

Their correct gates:

| Finding | Must be answered |
|---|---|
| **OD-17** — Discord character authorization | Before **Phase 3 planning**, and before any affected legacy bot mutation is migrated or cut over |
| **OD-39** — `/trade` and `/sale` input provenance | Before **Phase 5.7 `/sale`** and **Phase 5.8 `/trade`** |

**Phase 2 approval therefore rests on the plan §12 Phase 2 acceptance criteria
and on the correction of actual import/reconciliation findings** — not on these
two. Nothing above says either risk is smaller, contained or fixed: any guild
member can still act for any character today, and `/sale` still trusts
caller-supplied values. §6 records both as open exposures.

The re-review instruction was
explicit that they are not to be closed by an agent, and named the shortcuts
that must not be taken: display names, Discord usernames, role names, channel
membership or Sheet player names used as identity; `character_access` populated
from unverified Sheet data; commands silently made Council-only; commands
disabled; announcement behaviour added; shop or sale rules changed. **None of
those was done.** No production behaviour was changed in revision 3 or 4 at all —
the two files it touches are the Sheets import adapter and the audit value
object, neither of which any Discord command calls.

### 3.1 Finding 1 — Discord character authorization · **OPEN, Phase 3 gate**

**The exact blocker.** There is nothing to authorize against.

- `character_access` exists as a table with a schema, **no rows and no writer**.
  Phase 1 created it; Phase 2 deliberately does not populate it, because who
  owns a character is a Council decision (OD-13, OD-37).
- The only Sheet-side link is column **C**, a free-text *player name*. Finding
  F-S1 and OD-13 both record that it seeds a **Council-verified pass** and is
  not itself authorization. The player tab reaches a Discord *username*, which
  is mutable and is not a snowflake.
- Verified Discord identity links are Phase 3 (`Council character-link
  management`), behind the authentication review gate.

Building a name-to-Discord mapping in the bot would be exactly the insecure
shortcut the review instruction forbids and that `.agents/AGENTS.md` requires an
agent to stop for. Adopting the Sheet player name, the Discord username, a role
name or a channel as authorization would be the same thing wearing a different
hat.

**Containment options, their production consequences, and a recommendation** are
priced in [OD-17](../discovery/open-decisions.md#od-17--how-long-may-the-bot-remain-unauthorized--blocking-phase-3-planning--escalated-2026-07-31):
(a) document and accept, (b) ephemeral reads, (c) Council-only mutations,
(d) disable `/trade` and `/sale`, (e) attributable announcements.

**Recommended: (e) now, (c) the moment `character_access` has rows.** (e) is the
only option that reduces risk without either breaking day-to-day play or
asserting an identity link the platform does not have — it records the *caller*,
which Discord already supplies, making an abuse attributable and visible the day
it happens. (c) is implementable today (OD-18 supplied the Council snowflake on
2026-07-31) and closes the gap completely, but it would stop every ordinary
player using `/work`, `/craft` and `/lc`, which is the bot's entire purpose.

None of these was applied. Each changes production behaviour, which
`.agents/AGENTS.md` requires a maintainer to decide.

**Tests and design the eventual boundary needs.** So that the decision arrives
with the work sized:

*Design.* One application-level authorization service, called by the Discord
adapter and later by the web app — not a cog-by-cog check. It answers *may this
Discord user act for this character, under which capability?* from
`character_access` plus the Council role snapshot, returns a typed decision
carrying the capability for `audit_events.actor_capability`, and is the only
place either adapter asks. Character *selection* changes shape with it: a
player picks from their linked characters rather than typing a name, which
removes the arbitrary-name path rather than guarding it.

*Tests, all of which need the identity link to exist first:*

- an unlinked caller is denied for each mutating command, and the denial is
  ephemeral and names no other player's state;
- a linked owner is allowed, and the audit row records `character_owner`;
- a Council caller is allowed on a character they do not own, and the audit row
  records `guild_council` — the distinction OD-37 §4 requires;
- a revoked link denies on the *next* command, with no cached grace;
- the right channel plus no link is still denied, and the wrong channel plus a
  valid link is still denied, so neither check can be mistaken for the other;
- a delegate may do what a delegate may do and no more, once those capabilities
  are defined;
- `/info` follows whatever OD-16 rules, with a test per branch.

### 3.2 Finding 2 — resource creation through `/trade` and `/sale` · **PARTLY FIXED; the rest OPEN, Phase 5.7/5.8 gate**

**Traced, with the governing rules.** Both behaviours are existing, documented
and rule-backed, so neither is a defect an agent may unilaterally change:

- `/trade` with `Shop`/`Store` on one side loads and writes only the other side,
  so selling to the shop **creates** currency and buying **destroys** it. That is
  what an NPC vendor is. §4.1 p.10 and §4.2 p.11 describe the guild shop and
  player-to-player deals as manual arrangements the bot records.
- `/sale` computes a percentage the rules define exactly (§4.1 p.11, §4.1.1
  p.11, §4.2.1 p.11–12 — RC-01 and RC-03, both verified against the PDF's worked
  examples) over inputs the rules say nothing about. It does not check that the
  character owns or crafted the item, that the cost is the real crafting cost,
  or that the Persuasion modifier is the character's.

So the bot is a **recording instrument for a Council-supervised process**. The
inputs are trusted because the people typing them are — which was reasonable for
a shared spreadsheet and is not reasonable for an authority. The classification
the platform needs (player-suppliable / authoritative state / Council-approved)
is a game-policy ruling, tabulated value by value in
[OD-39](../discovery/open-decisions.md#od-39--unauthenticated-economy-mutations-through-trade-and-sale--raised-2026-07-31).

Worth noting for that decision: Sheet column **AG** now holds ability scores
(OD-02), so the platform can compute the Persuasion modifier itself without
waiting for the Foundry connector. That is the one input where the authoritative
source already exists.

**One detail added in revision 3, on re-checking the code against the
documentation.** `/sale` does make one authorization check, and it makes it with
presentation data: `point_of_sale="your own shop"` is worth **+20 percentage
points** on the sale price and is gated on `r.name.lower() == "shop owner"` over
the caller's roles. A role *name* is presentation (plan §4.1;
`.agents/AGENTS.md` requires stable role IDs), so renaming that Discord role
silently grants or removes the bonus. OD-18 already asked for that role's
snowflake and it has not been supplied; the request was buried in a decision
marked closed, so it is now a row in OD-39's table and flagged as outstanding at
OD-18. This is documentation of existing behaviour — the check was **not**
changed, because moving it to a snowflake needs the snowflake and changes who
can sell at the higher rate.

**What was fixed in revision 2** — only what needs no ruling. `/sale` refuses a
non-finite `cost`. `nan < 0` and `inf < 0` are both False, so the existing
non-negativity check passed them and they reached the money arithmetic, failing
inside `Decimal` as an unexplained error. This matches the check `/craft`
already applies. Four tests.

**Fail-closed containment available if wanted before the ruling:** refuse
`/trade` where either side is `Shop`/`Store` unless the caller holds the Council
role. This stops unbacked currency creation and leaves player-to-player trades
working. Not applied — it visibly changes the shop workflow in production.

---

## 4. Files changed

### Changed by revision 7 only

Twelve files: one new domain module, six code, three new or changed test files,
two documents. **No migration, no dependency, no configuration variable, no
Discord cog and no model was touched.**

```
domain/names.py                   NEW. DisplayName and the one comparison rule:
                                  exact, capitalisation-only, identity claim.
                                  Standard library only
domain/identity.py                Character.name exposes the comparable name
application/imports.py            SheetCharacterCandidate.name likewise
application/repositories.py       CharacterRepository.find_by_display_name states
                                  the comparison an implementation must answer
                                  for, and why a narrower one is the defect
application/sheet_import.py       is_semantic_name_change delegates to the policy;
                                  new is_spelling_change; _resolve looks a name up
                                  for every non-exact mapped name instead of
                                  skipping on casefold equality; _update blocks a
                                  capitalisation-only change onto a claimed name
                                  as name_collision; _rows_by_name keys on the
                                  identity key; module/class docstrings corrected
adapters/sheets/character_import.py  the parser's duplicate check keys on the
                                  shared identity key
adapters/database/repositories.py  find_by_display_name compares in Python on the
                                  policy instead of asserting a SQL lower()
                                  equivalence that does not hold; cost and the
                                  threshold for a normalized/indexed schema
                                  documented; the now-unused func import removed
tests/fakes.py                    the fake repository uses the same policy
tests/display_name_cases.py       NEW. The 12-case table every layer is checked
                                  against
tests/test_display_name_policy.py NEW. 86 collected: the rule, its containment
                                  property, and parser/fake/service agreement
tests/test_sheet_import_service.py   30 -> 39 collected. Nine added for the
                                  normalisation cases, the collision lookup on a
                                  capitalisation-only change, dry-run/apply
                                  agreement and mixed-run atomicity
tests/test_sheet_import_database.py   7 -> 24 collected (13 functions, one
                                  parametrised over the shared table):
                                  the repository-policy table against real
                                  PostgreSQL, the reproduction, the
                                  capitalisation collision, unmapped creation,
                                  the mixed-run rollback and dry-run/apply
                                  agreement
docs/operations/sheet-import.md   new "How two names are compared" section with
                                  the two folds, the worked examples and the
                                  scan/threshold note; duplicate and
                                  name_collision rows updated; the guarantees
                                  list gains "One comparison rule"
docs/review/phase-2-submission.md  this document, revision 7
```

Project records updated alongside:
`docs/project-management/status.md` and
`docs/project-management/raid-register.md` (I-01 and R-01).
`docs/project-management/change-log.md` is **not** updated: this correction
implements the accepted identity policy rather than amending the baseline.

### Changed by revision 6 only

Five files: one code, two tests, two documents. **No migration, no dependency,
no configuration variable, no Discord cog, no model and no adapter was touched.**

```
application/sheet_import.py       a semantic mapped-name change is never applied;
                                  _RunStructure, _structure_of and _is_shifted
                                  removed; is_name_change ->
                                  is_semantic_name_change; _refuse_name_change ->
                                  _name_change_refusal, now unconditional;
                                  ambiguous_name_change -> mapped_name_change;
                                  module and _Resolution docstrings rewritten
tests/test_sheet_import_service.py   26 -> 31 tests. Five added (fresh-name swap,
                                  three-row cycle, two independent renames,
                                  dry-run/apply agreement, non-identity fields);
                                  the "unambiguous rename is applied" test
                                  rewritten as "reported for reconciliation";
                                  three renamed for accuracy; three code
                                  assertions moved to mapped_name_change
tests/test_sheet_import_database.py   6 -> 7 tests. Adds the fresh-name
                                  permutation rollback against real PostgreSQL;
                                  the revision-4 case retitled and re-coded
docs/operations/sheet-import.md   the code table's ambiguous_name_change row
                                  replaced; "A rename versus a moved row"
                                  rewritten as "A renamed character is not
                                  imported automatically", with the permutation
                                  table and what still imports automatically
docs/review/phase-2-submission.md  this document, revision 6
```

### Changed by revision 4 only

Nine files. Two are code, one is a new module, one is a test file, and five are
documentation. **No Discord cog, no model, no migration, no dependency and no
configuration variable was touched by this revision.**

```
adapters/safe_logging.py        NEW. The whole logging vocabulary for an expected
                                failure: a fixed category and the exception class
                                name (ruling A)
adapters/sheets/read_only.py    exc_info removed from both sites; the
                                googleapiclient.discovery import translated into
                                the fixed dependency refusal (rulings A, B)
tools/import_sheet_characters.py  exc_info removed from all four sites; module
                                docstring corrected (ruling A)
tests/test_import_cli.py        + 11 tests (6 debug-logging canary cases, 1
                                canary-is-really-there guard, 3 client library,
                                1 helper); 29 -> 40 collected
docs/operations/sheet-import.md what the logs do and do not contain; the
                                dependency row covers either distribution
docs/discovery/open-decisions.md  music renumbered OD-38 -> OD-40 into a new
                                Product scope section; OD-17 and OD-39 scoped to
                                their correct gates; summary and urgency table
                                corrected; two pre-existing broken anchors fixed
docs/discovery/command-inventory.md  music reference renumbered and corrected to
                                "removed, not deferred"
.agents/AGENTS.md               repository map no longer lists music.py or
                                infra/lavalink/; adds application/, domain/,
                                adapters/, tools/; the test rule quoted by
                                fixture-strategy.md now matches its quotation
docs/review/phase-2-submission.md  this document
```

### Added (untracked), across all revisions

```
adapters/safe_logging.py                 safe diagnostic logging for expected failures
adapters/sheets/read_only.py             read-only Sheets port and credential selection
application/audit.py                     audit event, capability and source vocabulary
application/sheet_import.py              the import use case
ext/loader.py                            fail-closed extension loading
tools/__init__.py
tools/import_sheet_characters.py         operator entry point
tests/fakes.py                           in-memory unit of work and repositories
tests/test_sheet_import_service.py       31 tests, no database
tests/test_sheet_import_database.py       7 tests, real PostgreSQL
tests/test_import_cli.py                 40 tests
tests/test_audit_events.py               23 tests
tests/test_actor_sheet_writes.py         14 tests
tests/test_extension_loading.py           5 tests
tests/test_command_boundaries.py         11 tests
docs/operations/sheet-import.md          operator procedure and code table
docs/review/phase-2-submission.md        this document
```

The two import-test counts were collected from the tree in **this** session
(`pytest <file> --collect-only -q`: 31 and 7); the rest were collected during
revision 4 (§7.1 command 7) and are unchanged by revision 6, which touched no
other test file. Two counts in revision 3 were wrong and were corrected in
revision 4: `tests/test_import_cli.py` held 29, not 30, before that revision, and
`tests/test_extension_loading.py` holds **5** tests, not 6.

### Modified (tracked), across all revisions

```
main.py                                  fail-closed extension loading (finding 7)
models/actor.py                          changed-cell writes, row verification,
                                         duplicate-name refusal (finding 3)
models/trade.py                          verifies both rows before writing (finding 3)
ext/commands/sale.py                     non-finite cost refused (finding 2, partial)
application/imports.py                   + SheetRowMapping, SheetImportAction/Entry, outcome type
application/repositories.py              + SheetRowMappingRepository, AuditRepository,
                                           CharacterRepository.find_by_display_name
adapters/database/repositories.py        + the three implementations; audit payload
                                           serialized via json_payload() (finding 9)
adapters/database/mappers.py             + sheet_row_mapping_from_row
adapters/database/unit_of_work.py        + two repositories on the unit of work
adapters/sheets/character_import.py      + rows_from_values, layout check, blank-row skip
adapters/sheets/__init__.py              + exports
config.py                                music/Lavalink configuration removed (OD-40)
.env.example                             + optional SHEET_READONLY_SERVICE_ACCOUNT_JSON;
                                           music/Lavalink block removed (OD-40)
requirements.txt                         yt-dlp removed (OD-40)
repoize.sh, README.md                    music/Lavalink scaffolding removed (OD-40)
.agents/AGENTS.md                        repository map corrected (revision 4)
docs/implementation-plan.md              music excluded from the platform (OD-40);
                                         Phase 3 ownership; §7.4 catalogue design.
                                         Also holds the maintainer's Phase 5
                                         Living Cost scheduling requirements,
                                         which are NOT this work — see below
docs/discovery/open-decisions.md         OD-17 escalated, OD-39 raised, then both
                                         scoped; OD-40 renumbered (revision 4).
                                         Also holds the maintainer's OD-36
                                         amendment of 2026-08-02, which is NOT
                                         this work — see below
docs/discovery/command-inventory.md      music section removed (OD-40)
docs/discovery/fixture-strategy.md       Lavalink/YouTube references removed (OD-40)
docs/operations/topology.md              Lavalink service removed (OD-40)
tests/test_sheet_character_import.py     + 6 tests (11 total)
tests/test_database_repositories.py      + 9 tests (20 total)
```

Deleted under OD-40: `music.py`, `infra/systemd/lavalink.service.tmpl`,
`infra/lavalink/application.yml.tmpl`, `yt-cookies.txt.example`.

**Bot files touched, which the first submission could say were untouched:**
`main.py`, `models/actor.py`, `models/trade.py`, `ext/commands/sale.py` and
`config.py`. The first four are reviewed safety fixes under findings 2, 3 and 7;
`config.py` is the OD-40 removal. `connectors/`, `helpers/` and every other cog
are byte-identical.

**Also present in the working tree and not part of this work.** Listed so the
file list accounts for every path `git status --short` reports, as of revision 6:

| Path | State | Note |
|---|---|---|
| `docs/implementation-plan.md` — the Phase 5 Living Cost scheduling requirements | modified | **Maintainer-authored.** The scheduled Living Cost accrual job: PostgreSQL authority, Sunday 04:00 initially, fixed IANA `Europe/Berlin`, Platform-Administrator-only schedule changes, effective-dated eligibility, the durable non-accruing transition occurrence, backlog/catch-up rules and the Phase 5 acceptance criteria and mandatory tests. Read and left **byte-for-byte unchanged** by this work, which implements none of it |
| `docs/discovery/open-decisions.md` — OD-36's amendment of 2026-08-02 | modified | **Maintainer-authored**, and the OD-36 half of the same decision. Unchanged by this work |
| `docs/review/Handover information` | untracked | The maintainer's working exchange file, used in both directions. It carried the prompt for this correction pass and now holds this session's handoff summary; it is a scratch channel, not a record — this document is the record |
| `docs/review/phase-2-i-02-prompt.md` | later renamed and revised | The maintainer-authored successor prompt for I-02; not part of revision 7's implementation |
| `docs/review/Prompt-for-claude` | deleted | Deleted in the working tree by the maintainer, not by this work. No agent session removed it |
| `docs/Freedom Blades Token.png` | untracked | A binary asset |
| `tools/` | untracked | Contains `tools/__init__.py` and `tools/import_sheet_characters.py`, both listed above |

None of the maintainer-owned entries was created, modified or deleted by this
work.

---

## 5. Migrations

**None**, in revision 6 as in every revision before it. No column was added,
altered or dropped. `alembic check` reports `No new upgrade operations
detected.` (§7.0, command 9.)

---

## 6. Security implications

| Concern | Treatment |
|---|---|
| Sheet write access from the importer | Unchanged in effect — reads only — and now narrowed in principle: a `spreadsheets.readonly` credential is used when configured, and the shared one is announced when it is not (finding 8). |
| Sheet write access from the bot | **Reduced.** A command writes only the cells it changed, so a command cannot overwrite a field it did not touch, and refuses outright if its row moved (finding 3). |
| Which database gets written | Unchanged: `DatabaseSettings.from_mapping` with `ConnectionPolicy.SOCKET_OR_LOOPBACK`, and `APP_ENVIRONMENT` still constrains the permitted database name. |
| Operator output | **Improved again in revision 4.** Expected Google, SQLAlchemy, constraint, dependency and concurrency failures produce fixed strings and documented exit codes. No DSN, credential, SQL, Google body or traceback; asserted by regex over stdout **and** stderr in the tests. |
| **Operator logs** | **Closed in revision 4 (ruling A).** Revisions 2 and 3 kept the exception out of the terminal and then attached it to `logger.debug(exc_info=…)`, which put the credential fragment, DSN, SQL statement and full traceback into journald or a CI log for anybody running at DEBUG. At every level the record is now a fixed category and the exception's class name, nothing more. Proved by tests that turn DEBUG on and plant canaries inside the exceptions. §2.10 |
| Dependency failures | **Closed in revision 4 (ruling B).** A partial Google install — `google-auth` present, `google-api-python-client` absent — produced a bare `ImportError` traceback; it is now the same fixed refusal and exit **2** as the other half. §2.11 |
| Discord output | `/sale` reports a refused write ephemerally as a failure rather than rendering a total that was never saved. Startup can no longer proceed without the global error handler (finding 7). |
| Audit integrity | **Improved again in revision 3.** A payload cannot be altered after the event is constructed, at any depth; an unrecordable value is refused at the call site (finding 9); and a non-finite number can no longer reach the driver, where it would have failed the audited mutation itself (re-review 4). |
| Sale rate authorization | **Unchanged and now documented.** `/sale`'s +20-point "your own shop" rate is gated on a Discord role *name*, not a snowflake. Renaming the role changes who gets the better rate. OD-39 and OD-18. |
| **Character identity through import** | **Closed in revision 6.** Revision 4 could commit one character's new name onto another when mapped rows were permuted and every displaced character renamed to a fresh name — silent, unrecoverable identity corruption whose audit row read as an ordinary rename. A mapped semantic name change is now never applied automatically; the run is refused and rolled back in full. §0.3, §2.13 |
| Privilege escalation through import | Unchanged: the importer writes no `character_access` and no `discord_users` row. |
| **Character authorization** | **Unchanged and open.** Any guild member can still act for any character. This is the largest security exposure in the repository. Phase 2 neither introduced nor worsened it, and it is answered at the Phase 3 gate — finding 1, OD-17. |
| **Economy inputs** | **Unchanged and open.** `/trade` can still credit currency from `Shop`; `/sale` still trusts caller-supplied values. Phase 2 neither introduced nor worsened this, and it is answered before Phase 5.7 and 5.8 — finding 2, OD-39. |

| Music removal | No residual attack surface in the repository: no runtime path, dependency, credential example or deployment template (§2.12). `yt-cookies.txt` survives in the working tree as a gitignored credential-shaped file; it was **not read**, and removing it from the host is an operator decision. |

`.env`, credentials, live Sheets, Discord, Foundry and production databases were
not read or modified at any point. The only database written to was the
disposable `freedom_test`.

---

## 7. Commands run, and their exact results

From `/opt/discord-bots/freedom-bot` using the repository's `./venv`
(Python 3.12.3) against the disposable local database `freedom_test`
(PostgreSQL 16, Unix socket, owner `foundry`).

### 7.0.2 Revision 7 — run in this session, 2026-08-02

Nothing below is carried forward. Every figure is from this session, using the
repository `./venv` (Python 3.12.3) against the disposable local database
`freedom_test` (PostgreSQL 16.14, Unix socket, owner `foundry`), confirmed
present with `psql -lqt` before any database run and re-validated by
`tests/conftest.py`'s two-layer guard before `alembic downgrade base`.

| # | Command | Result |
|---|---|---|
| 1 | `./venv/bin/pytest tests/test_sheet_import_service.py -q` | **39 passed**, 1 warning |
| 2 | `./venv/bin/pytest tests/test_sheet_import_database.py -q` | **24 skipped**, 1 warning — no `TEST_DATABASE_URL`, so the fixture skips the file rather than letting a database assertion pass without a database |
| 3 | `./venv/bin/pytest tests/test_import_cli.py -q` | **40 passed**, 1 warning |
| 4 | `./venv/bin/pytest tests/test_display_name_policy.py -q` | **86 passed**, 1 warning |
| 5 | `./venv/bin/pytest -q` | **694 passed, 91 skipped**, 1 warning |
| 6 | `TEST_DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' ./venv/bin/pytest -q` | **785 passed, 0 skipped**, 1 warning |
| 7 | `./venv/bin/python -m compileall -q main.py config.py application adapters domain ext models tools` | exit **0**, no output |
| 8 | The nine service regression tests run against the untouched tree, before any production edit | **6 failed, 33 passed** — §2.14 proof 1 |
| 9 | `find_by_display_name` alone reverted to SQL `lower()`; `tests/test_sheet_import_database.py tests/test_database_repositories.py` re-run with PostgreSQL; the file restored | **4 failed, 40 passed** neutralised; restored file byte-identical by `cmp` and MD5; **44 passed** afterwards — §2.14 proof 2 |
| 10 | The standalone reproduction script, against the untouched tree | `applied= True`, `issues= []`, `names= ['Test STRASSE', 'Test STRASSE']`; re-run after the fix: `applied= False`, `issues= [('name_collision', 'error')]`, `names= ['Test STRASSE', 'Test Straße']` |
| 11 | `git diff --check` | clean, exit **0** |
| 12 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' ./venv/bin/alembic check` | `No new upgrade operations detected.` — this correction adds no schema drift |
| 13 | `psql -d freedom_test -Atc "SELECT lower('Test Straße') = lower('Test STRASSE')"` | `f` — the database's `lower()` really does disagree with the policy on this host (collation `C.UTF-8`, PostgreSQL 16.14). The adapter docstring's claim is measured, not assumed |
| 14 | `psql -lqt` | `freedom_test` and `freedom_dev` present on this host, both owned by `foundry`; no production or staging database was contacted |

The **one warning** in every pytest run is the pre-existing
`DeprecationWarning: 'audioop' is deprecated and slated for removal in Python
3.13`, raised by Pycord's `discord/player.py` at import. It is unrelated to this
work and unchanged by it.

**Test-count movement, measured rather than inferred, and a correction to
revision 6's figures.** Revision 7 adds 9 tests to
`tests/test_sheet_import_service.py`, 86 in the new
`tests/test_display_name_policy.py`, and 17 collected cases to
`tests/test_sheet_import_database.py` (7 → 24, the growth being partly
parametrisation). That is +95 without PostgreSQL and +112 with it. The measured
pre-change baseline was therefore **599 passed / 74 skipped** without
PostgreSQL, not the **600 / 74** revision 6 reported: `--collect-only` puts
`tests/test_sheet_import_service.py` at 30 before this session's additions, not
31. Revision 6 was one test out, in the same way it recorded revision 3 being
one out. The measured figure is stated here rather than carried forward, and the
discrepancy is in the count only — no test was removed by this work.

**No formatter, linter or type checker is configured**, re-verified in this
session: no `pyproject.toml`, `setup.cfg`, `.flake8`, `ruff.toml` or `mypy.ini`
exists; `requirements-dev.txt` adds only `pytest` on top of `requirements.txt`;
`pytest.ini` is test configuration, not a checker; and `black`, `ruff`,
`flake8`, `mypy`, `pyright`, `isort` and `pylint` are absent from the venv. None
was installed for this task. `compileall` is run instead, as the nearest
available check.

### 7.0 Revision 6 — run in the revision-6 session, 2026-08-02

Nothing below was carried forward at the time. Every figure is from that
session, against the
disposable local database `freedom_test` (owner `foundry`, Unix socket),
confirmed present with `psql -lqt` before any database run and re-validated by
`tests/conftest.py` twice more — statically against `TEST_DATABASE_URL` and
against the live connection — before `alembic downgrade base`.

| # | Command | Result |
|---|---|---|
| 1 | `./venv/bin/pytest tests/test_sheet_import_service.py -q` | **31 passed**, 1 warning |
| 2 | `./venv/bin/pytest tests/test_sheet_import_database.py -q` | **7 skipped**, 1 warning — no `TEST_DATABASE_URL`, so the fixture skips the file rather than letting a database assertion pass without a database |
| 3 | `./venv/bin/pytest tests/test_import_cli.py -q` | **40 passed**, 1 warning |
| 4 | `./venv/bin/pytest -q` | **600 passed, 74 skipped**, 1 warning |
| 5 | `TEST_DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' ./venv/bin/pytest -q` | **674 passed, 0 skipped**, 1 warning |
| 6 | `./venv/bin/python -m compileall -q main.py config.py application adapters domain ext models tools` | exit **0**, no output |
| 7 | `git diff --check` | clean, exit **0** |
| 8 | The refusal neutralised, `tests/test_sheet_import_service.py` re-run, the file restored | **9 failed, 22 passed** neutralised; restored file byte-identical by `cmp` and MD5; **31 passed** again afterwards. §2.13 |
| 9 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' ./venv/bin/alembic check` | `No new upgrade operations detected.` |
| 10 | `psql -lqt` | `freedom_test` and `freedom_dev` present on this host, both owned by `foundry`; no production or staging database was contacted |

The **one warning** in every pytest run is the pre-existing
`DeprecationWarning: 'audioop' is deprecated and slated for removal in Python
3.13`, raised by Pycord's `discord/player.py` at import. It is unrelated to this
work and unchanged by it.

**Test-count movement, measured rather than inferred.** The revision-5 figures
were 595 passed / 73 skipped without PostgreSQL and 668 with it. Revision 6 adds
**five** tests to `tests/test_sheet_import_service.py` (26 → 31) and **one** to
`tests/test_sheet_import_database.py` (6 → 7), and removes none — the
`…_unambiguous_in_place_rename…` test was rewritten in place rather than
deleted. 595 + 5 = 600, 73 + 1 = 74, and 668 + 6 = 674, which is what the runs
report.

**No formatter, linter or type checker is configured**, re-verified in this
session: no `pyproject.toml`, `setup.cfg`, `.flake8`, `ruff.toml` or `mypy.ini`
exists; `requirements-dev.txt` holds only `pytest`; and `black`, `ruff`,
`flake8`, `mypy`, `pyright`, `isort` and `pylint` are all absent from the venv.
None was installed. `compileall` is run instead, as the nearest available check.

### 7.0.1 Revision 5 — independent re-verification, 2026-08-01

A later session re-ran the checks below **itself** rather than carrying §7.1's
results forward, because a submission should not assert a check on the strength
of a previous session's word. Every figure in §7.1 was reproduced exactly.

| # | Command | Result |
|---|---|---|
| 1 | `pytest tests/test_import_cli.py tests/test_audit_events.py tests/test_extension_loading.py -q` | **68 passed**, 1 warning (pre-existing `audioop` deprecation from Pycord) |
| 2 | `pytest -q` | **595 passed, 73 skipped**, same warning |
| 3 | `TEST_DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' pytest -q` | **668 passed**, 0 skipped |
| 4 | `python -m compileall -q main.py config.py application adapters domain ext models tools` | exit **0** |
| 5 | `git diff --check` | clean, exit **0** |
| 6 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' alembic check` | `No new upgrade operations detected.` |
| 7 | `pytest <file> --collect-only -q` over every file in `tests/` | every per-file count in §4 confirmed |
| 8 | OD heading uniqueness over `open-decisions.md` | 40 OD headings, **no duplicate identifier**; OD-38 is *Initial authority*, OD-40 is *Music platform work* |
| 9 | Every `#od-…` link in every non-`venv` markdown file resolved against the headings of `open-decisions.md` | 26 links, **25 resolve**. The one that does not is in `docs/review/phase-1-submission.md` and points at OD-14; it is **pre-existing**, predates this work, and is in a historical Phase 1 record that this task does not rewrite. Every link in `open-decisions.md` and in this document resolves |
| 10 | Read-only music sweep (§2.12) repeated from scratch | No implementation surface remains. `music.py` absent; no `wavelink`/`lavalink`/`yt-dlp`/`ytdl`/`ENABLE_MUSIC`/`YTDLP_*` match in any `.py`, `.txt`, `.sh`, `.ini`, `.tmpl` or `.example` file; `main.EXTENSIONS` holds eleven non-music entries; `infra/` holds only `postgresql/` and `systemd/freedom-bot.service.tmpl`; no music test |
| 11 | Secret scan over the whole tracked diff | Two matches, both **placeholder templates** (`.env.example` and the plan's `SERVICE_ACCOUNT_JSON` example, whose key bodies are literally `ABC...` and `...`). No real key, DSN, token or webhook |

**Rulings A and B were also re-proved end-to-end, outside the test suite**, by
running the real CLI in a process with root logging forced to `DEBUG` and a
`logging.Formatter` attached — the configuration that renders a traceback when a
record carries `exc_info` — and capturing stdout, stderr and the log stream
separately. All credential material is synthetic and invented for the check.

| Scenario | Exit | Log record | Leak check |
|---|---|---|---|
| A synthetic service-account document whose `private_key` holds `VERIFY-CANARY-PRIVATE-KEY-4d7e`, with `verify-canary@synthetic-verify-project.iam.invalid` as the address | **2** | `expected failure category=read_only_credential_refused exception_type=Error` | No canary, no `BEGIN PRIVATE KEY`, no traceback on any of the three surfaces |
| An `OperationalError` carrying the DSN `postgresql+psycopg://canary_user:VERIFY-DB-PASSWORD-8c31@canary-host.invalid:5432/canary_db` and the statement `SELECT canary_col FROM canary_tbl WHERE id = 'VERIFY-SQL-2f90'` | **4** | `expected failure category=database_unavailable exception_type=OperationalError` | No DSN, no password, no SQL, no traceback |
| `google-auth` present, `googleapiclient.discovery` absent — the ruling B partial install | **2** | `expected failure category=google_client_library_missing exception_type=ModuleNotFoundError` | Fixed dependency sentence only; no `ImportError` traceback |

Each run printed the documented fixed operator string on stderr and nothing on
stdout, which is the same behaviour the suite asserts, reached by a different
route.

### 7.1 Revision 4 — run in the preceding session, 2026-08-01

Run with `/opt/discord-bots/venv/bin/pytest`, which is the same interpreter as
`./venv` (`freedom-bot/venv` is a symlink to `/opt/discord-bots/venv`).

| # | Command | Result |
|---|---|---|
| 1 | `pytest tests/test_import_cli.py tests/test_audit_events.py tests/test_extension_loading.py -q` | **68 passed**, 1 warning (pre-existing `audioop` deprecation from Pycord) |
| 2 | `pytest -q` | **595 passed, 73 skipped**, same warning |
| 3 | `TEST_DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' pytest -q` | **668 passed**, 0 skipped |
| 4 | `python -m compileall -q main.py config.py application adapters domain ext models tools` | exit **0** |
| 5 | `git diff --check` | clean, exit **0** |
| 6 | `APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' alembic check` | `No new upgrade operations detected.` |
| 7 | `pytest <file> --collect-only -q` over every file in `tests/` | the per-file counts in §4 |
| 8 | OD identifier uniqueness and in-document anchor resolution over `docs/discovery/open-decisions.md` | 40 headings, **no duplicate identifier**; every in-document `#od-…` link resolves |
| 9 | Read-only music sweep: `grep` for `music`, `lavalink`, `wavelink`, `yt-dlp`, `ytdl`, `ENABLE_MUSIC`, `LAVALINK_*`, `YTDLP_*` over every non-`venv`, non-`.git` file; `ls -R infra`; `main.py` `EXTENSIONS`; `requirements*.txt`; `tests/` | No implementation surface remains (§2.12). Matches survive only in `.gitignore`, historical Phase 0/1 review records, and the current documents that say music was *removed* |

**Test-count movement.** `pytest -q` was run against the unmodified tree at the
start of this task and reported **584 passed, 73 skipped** — not the 585 revision
3 claimed. That submission was one test out, and the measured figure is stated
here rather than carried forward. Revision 4 adds **11** tests, all in
`tests/test_import_cli.py` and none of them database-marked, giving 595 without
PostgreSQL and 668 with it. The corresponding revision-3 figure *with*
PostgreSQL, 657, is arithmetic from those two runs rather than a separate
measurement, and is labelled as such.

The PostgreSQL run used the documented disposable database `freedom_test`
(PostgreSQL 16, Unix socket, owner `foundry`), confirmed present with `psql -lqt`
before use. `.env` was not read and no credential was discovered to make it
available; the connection is peer authentication over the Unix socket. The
documented `test_role` still does not exist on this host.

### 7.2 Revision 4 regression tests, confirmed to fail without their fix

Both fixes were temporarily reverted to their pre-fix shape — `exc_info=` restored
at all six sites, the `googleapiclient.discovery` guard removed — the suite
re-run, and both files restored from copies and **confirmed byte-identical with
`cmp`**. The suite was re-run green afterwards.

| Fix removed | Result |
|---|---|
| `exc_info` restored and the client-library guard removed | **8 failed, 32 passed** — the **6** debug-logging canary tests (three parametrised database cases, plus sheet-read, transport and credential) and the **2** client-library tests |

The three tests that pass either way are named as such rather than counted as
evidence: `…_guard_does_not_swallow_an_unrelated_import_error` and
`…_canary_credential_really_is_quoted_back_by_google` are guards against the
others passing for the wrong reason, and
`…_safe_diagnostic_records_the_category_and_class_and_nothing_else` tests the new
helper, which does not exist in the pre-fix tree.

### 7.3 Revision 3 (carried, not re-run in full)

| # | Command | Result |
|---|---|---|
| 1 | `pytest tests/test_import_cli.py tests/test_audit_events.py -q` | **52 passed** |
| 2 | `psql -d freedom_test -c "SELECT '{\"a\": NaN}'::jsonb;"` and the `Infinity` form | `ERROR: invalid input syntax for type json` for both — the premise of re-review finding 4, verified rather than assumed |
| 3 | `python -m tools.import_sheet_characters --help` | usage printed; exit 0; no Google credentials and no database required |
| 4 | The CLI with a **synthetic** unusable service-account document | `Sheet credential refused: …`, exit **2**, no traceback, nothing of the document echoed |
| 5 | The CLI with truncated JSON in the same variable | `Sheet credential refused: …must be valid single-line JSON.`, exit **2** |
| 6 | Guards neutered in `application/sheet_import.py` and `adapters/sheets/read_only.py` | 4 and 6 failures respectively, exactly the "must block" cases; files restored byte-identical |

### 7.4 Revision 2 (carried, not re-run in full)

| # | Command | Result |
|---|---|---|
| 1 | `./venv/bin/python -m pytest -q` | **560 passed, 72 skipped**, 1 warning |
| 2 | `TEST_DATABASE_URL='postgresql+psycopg://foundry@/freedom_test' ./venv/bin/python -m pytest -q` | **632 passed** |
| 3 | Revision-1 baseline, same two commands | **499 passed, 70 skipped** / **569 passed** |
| 7 | `env -u DATABASE_URL APP_ENVIRONMENT=development ./venv/bin/python -m tools.import_sheet_characters` | `Database configuration refused: DATABASE_URL is required for development.`, exit **2**, before any Sheet read |

**The PostgreSQL target was validated before every database run.** `psql -lqt`
shows `freedom_test` on this host, owned by `foundry`, reachable over the Unix
socket, alongside `freedom_dev` — matching the documented disposable database.
`tests/conftest.py` re-validates it twice more, statically and against the live
connection, before running `alembic downgrade base`.

| Guard removed (revision 2) | Result |
|---|---|
| Both new guards in `application/sheet_import.py` (`rows_may_have_moved`, `name_collision`) | **4 failed, 21 passed** — exactly the four "must block" cases from finding 4. File restored and confirmed byte-identical by `diff`; suite re-run green |

The finding-3 tests were written against the new behaviour and were not run
against the old whole-row write, because the old code has no seam to disable —
`sheet_updates()` either diffs or it does not. Their value is as a lock on the
new behaviour rather than as a demonstration of the old.

---

## 8. Checks not run, and why

| Check | Why not |
|---|---|
| Formatter, linter, type checker | **None is configured or installed**, re-verified again in revision 6 (§7.0): no `pyproject.toml`, `setup.cfg`, `.flake8`, `ruff.toml` or `mypy.ini` exists, `requirements-dev.txt` contains only `pytest`, and `black`, `ruff`, `flake8`, `mypy`, `pyright`, `isort` and `pylint` are all absent from the venv. `compileall` is run instead as the nearest available check. No such dependency was installed for this task, per the task instruction. Still an open maintainer decision |
| The importer against the live Sheet | Requires the production service account; a maintainer decision, not an agent one. **The dry-run path has still never touched a real Sheet.** Largest evidence gap in this submission |
| The read-only credential path, **success** side | Building a *usable* credential needs a real service-account key, which no test here may use, so the `build()` call and the reader closure after it stay `pragma: no cover`. **Every failure side is now covered** — malformed credential (§2.8), missing `google-auth`, missing `google-api-python-client` (§2.11) — and the selection around it is tested with injected factories |
| The bot running with these changes | Not started, not deployed. `models/actor.py` and `main.py` changes are covered by tests but have not run against Discord or the live Sheet |
| `test_role` / `freedom_test_app` as documented | Those roles do not exist on this host. Re-checked in this session: `pg_roles` holds only `foundry` and `postgres` besides the built-in `pg_*` roles. Every database run used `foundry` over the Unix socket. Unchanged from revision 1 |
| Append-only enforcement of audit writes | The restricted runtime role cannot be created here, so `SELECT, INSERT`-only is asserted by template, not rehearsed |
| Concurrent imports | Two importers at once are still not tested. The database would reject the loser's duplicate mapping insert, and the CLI now translates that into exit 5 — but that path is tested with a synthesised `IntegrityError`, not real contention |
| Two bot processes writing one row | Not tested and **not contained**. See §2.1 |
| A real DEBUG-logging deployment | The canary tests in §2.10 configure a root handler in-process rather than exercising journald or a CI collector. What they prove is that no record *carries* the exception; how a given collector renders a record it never received is not a variable |
| Whether any live Lavalink process is still running | Deliberately not inspected. Repository removal is not authorization for live-service administration (§2.12) |
| Import of a 150-row Sheet | Largest exercised import is 4 rows |
| Any production, staging, Discord, Sheets, Foundry or live-PostgreSQL interaction | Forbidden. Only `freedom_test` was written, and the fixture truncates it after each test |

---

## 9. Configuration and deployment changes

**One new optional environment variable**, read only by the importer:

```bash
# Optional. A second service account holding only Viewer on the spreadsheet.
SHEET_READONLY_SERVICE_ACCOUNT_JSON='__MINIFIED_READONLY_SERVICE_ACCOUNT_JSON__'
```

Unset, the importer behaves exactly as before and says so on stderr.

**Configuration removed under OD-40**, and it must be removed from any deployed
`.env` too or it will simply sit there unread: `ENABLE_MUSIC`, `LAVALINK_HOST`,
`LAVALINK_PORT`, `LAVALINK_PASSWORD`, `YTDLP_COOKIES_FILE`. The `yt-dlp`
dependency is gone from `requirements.txt`; a redeploy that reinstalls
requirements will not remove it from an existing virtualenv, which is harmless
but worth knowing. **Stopping or disabling any live Lavalink service is a
separate operator decision that this work neither made nor authorized.**

No other configuration change, and no new service file.

**Deployment note for the bot changes.** `models/actor.py` and `main.py` change
live behaviour and need the usual §14.2 gate. Two operational consequences worth
naming before deploying:

1. **Startup now fails closed.** A deployment with a broken extension will
   refuse to start rather than run partially. That is the intent, and it means
   a bad deploy is visible immediately in the service status rather than as a
   missing command hours later.
2. **Each mutating command makes one extra single-cell Sheets read.** Well
   within quota at this scale, but it is a new API call on every `/work`,
   `/craft`, `/lc`, `/mine`, `/bastion`, `/sale`, `/learn`, `/xchange` and
   `/trade`.

---

## 10. Rollback and recovery

- **The importer.** Unchanged: a dry run and a blocked run commit nothing by
  construction; an applied run is undone by restoring the pre-run backup per
  `docs/operations/database-development.md`. The Sheet is untouched and remains
  authoritative, so re-importing after a restore is safe, and because the import
  is idempotent, re-running it is the normal recovery from any partial failure.
- **The bot changes.** Reverting `models/actor.py`, `models/trade.py`,
  `ext/commands/sale.py` and `main.py` restores the previous behaviour exactly.
  There is no data migration to undo: the changes alter which cells are written,
  not what any cell means. A row already written by the new code is
  indistinguishable from one written by the old.
- **The startup change.** If a required extension is broken in production and
  the bot must run without it, the correct action is to fix the extension, not
  to restart with it removed — but removing its entry from `EXTENSIONS` is a
  one-line, reviewable escape hatch if a maintainer decides the trade differently.
- **The revision-6 change carries no rollback risk of its own, and no data
  risk.** It only removes a path that wrote: an import that would have committed
  a mapped name change now refuses and rolls back. There is no schema change, no
  configuration change, no Discord-visible behaviour change and nothing written
  by the old code that needs undoing — a name already applied by an earlier
  revision stays applied, correctly or otherwise, and this change cannot tell
  which. **If an apply run has been performed against any real database, its
  renamed characters are worth checking by hand** against the Sheet before
  trusting them; no revision of this submission records an apply run against
  anything but the disposable `freedom_test`, which is truncated after every
  test. Reverting the three files restores the previous behaviour exactly, at
  the cost of reinstating the identity defect.
- **The revision-4 changes carry no rollback risk of their own.** They alter what
  is written to a log and which exception type a missing dependency produces.
  There is no state to undo, no schema change, no configuration change and no
  Discord-visible behaviour change; reverting the three touched files restores
  the previous behaviour exactly, at the cost of reinstating the disclosure.
- **The music removal.** Reverting it would mean restoring `music.py`, the two
  templates, the cookie example, the `yt-dlp` dependency and the `config.py`
  block from `bb104c8`. Under OD-40 that is not a rollback path anybody should
  take: music is removed, not deferred. It is recorded here only because a
  rollback section that omits a deletion is incomplete.

---

## 11. Open maintainer decisions

**None of these blocks the Phase 2 review gate.** That gate is *data integrity
and migration safety* for import/reconciliation, and every finding inside it is
fixed and tested. Each decision below is listed under the gate at which it must
actually be answered.

### Before Phase 3 planning, and before the affected commands are migrated or cut over

1. **OD-17 (escalated 2026-07-31, scoped 2026-08-01)** — interim authorization
   containment for the bot. Five options priced; recommendation (e) now, (c) once
   `character_access` has rows. The ruling needed is: *which containment, if any,
   applies before Phase 3, and what establishes a caller's identity when it
   does?* **This risk is open and unfixed.** Any guild member can act for any
   character today.
2. **OD-16** — should `/info` remain unrestricted, ephemeral, or scoped?

### Before Phase 5.7 (`/sale`) and Phase 5.8 (`/trade`)

3. **OD-39 (raised 2026-07-31, scoped 2026-08-01)** — provenance of `/trade` and
   `/sale` inputs: which values a player may supply, which must come from
   authoritative state, which need Council approval. The table is value-by-value
   and each row needs an answer. It also asks for the **Shop Owner role
   snowflake** OD-18 requested, so `/sale`'s +20-point rate can stop depending on
   a role *name*. **This risk is open and unfixed.**

### Import questions raised by this milestone, for the reviewer or the maintainer

None of these is a defect against the Phase 2 acceptance criteria; each is a
policy choice the criteria leave open, and the current behaviour is the
conservative one in every case.

4. **A character with no owner.** The importer creates characters with no
   `character_access` row and reports a missing player name as a *warning*.
   Should an unresolvable owner block the run instead?
5. **How is a moved row — or now a renamed one — corrected?** The importer
   refuses to re-key a mapping and nothing lets an operator do it deliberately.
   A `tools/` command, a Phase 3 Council action, or a documented manual `UPDATE`?
   **Revision 6 makes this the most pressing open question in this slice**: every
   genuine rename now stops for a human as well, and the human currently has no
   in-platform way to say "yes, this really is a rename of that character". This
   task deliberately did not build one — re-keying a mapping is precisely the
   guess the refusal exists to prevent, and it needs its own authorization,
   preview and audit design rather than a flag on an operator tool.
6. **Is all-or-nothing the right granularity?** One malformed row still prevents
   149 good ones from importing.
7. **Should the tool read `.env`?** It still does not.
8. **`characters.display_name` uniqueness.** ~~`unmapped_name_collision` uses SQL
   `lower()`; the parser uses Python `casefold()`.~~ **The comparison half is
   fixed in revision 7**: every importer layer now compares through
   `domain/names.py` (§0.4, §2.14). Two parts of this item remain open and are
   maintainer decisions, not defects:
   - **The database still enforces nothing.** `characters.display_name` has no
     uniqueness constraint, so the importer's refusal is the only thing
     preventing a duplicate, and a future writer that is not the importer could
     create one. A decided uniqueness rule would let PostgreSQL enforce it — as
     a stored, indexed identity key, because the comparison is not one SQL
     `lower()` can express. That is a migration plus a policy decision, and it
     is also what the adapter's documented performance threshold points at.
   - **`AmbiguousActorError` in the legacy bot uses a third comparison**
     (`str.lower()` on the Sheet value, `models/actor.py`). Revision 7
     deliberately did not touch it: it reads the live Sheet, it is not on the
     importer's path, and changing a live bot lookup is a behaviour change
     outside this correction's scope. It should adopt the same policy when that
     path is migrated.
9. **`test_role` does not exist on this host.** Which is wrong, the roles or the
   documentation?
10. **No formatter, linter or type checker is configured.** Deliberately not
    installed by this task. Worth a decision before Phase 3 doubles the code.

---

## 12. Recommended reviewer focus

**New in revision 4**, before the rest:

00a. **Is the exception *class name* safe to keep?** (`adapters/safe_logging.py`.)
     The argument is that a class name is an identifier in installed source code
     rather than data derived from a credential, a database or a player, and that
     it is the one part of an exception that distinguishes `MalformedError` from
     `InvalidValue` from `binascii.Error`. The counter-argument is that it is
     still information the exception chose to expose. If a reviewer disagrees,
     the fix is one line: log the category alone.

00b. **The `logger.exception` in `ext/loader.py` was left as it is**, and this is
     a judgement worth checking. It logs the traceback of a failed extension
     *import* — a programming or deployment defect, not an expected operator
     failure — and it is the only diagnostic available, because `main()` catches
     `ExtensionLoadError` and returns 1 rather than letting it propagate. It was
     traced for credential exposure: `connectors.sheets` builds its Google
     credential lazily in `_get_service()`, not at import, and `config.py`
     `sys.exit`s on a bad `SERVICE_ACCOUNT_JSON` before any extension loads, so
     the realistic failure there is a `SyntaxError` or `ImportError`. A reviewer
     who reads ruling A as covering every log line in the repository rather than
     the importer's expected-failure paths should say so.

00c. **One message for either missing Google distribution.** A partial install
     now produces the same sentence whichever half is absent, on the argument
     that the remedy is identical. If an operator would be better served by being
     told which package to install, that is a one-word change.

**New in revision 3:**

0a. **The breadth of the credential `except` clause** (`adapters/sheets/read_only.py`).
    It catches `GoogleAuthError`, `ValueError` and `TypeError` around one library
    call. `TypeError` is the debatable one: it is there because a JSON field of
    an unexpected type can reach the crypto layer, but it is also the shape a
    genuine defect would take. The counter-argument is that the try block holds a
    single call with two arguments this module constructs itself. Judge whether
    that is narrow enough, or whether `TypeError` should be dropped and the
    non-object case relied on instead.

0b. **Exit 2 versus exit 3 for a client-construction failure.** A credential that
    cannot be built is exit 2; a transport failure while building the client is
    exit 3. The split is a judgement about what an operator should go and check,
    not a rule from the plan. If it is wrong, an operator is sent to the wrong
    place at the worst time.

0c. **Refusing non-finite floats is a new constraint on every future audit
    writer** (`application/audit.py`). A caller computing a rate as `x / y` and
    passing the result into a payload now fails at construction where it
    previously reached the driver. That is the intended direction — fail early,
    at the call site, with a path — but it is a behaviour change for code not yet
    written, in the same family as the revision-2 constraint noted at item 6.

**New in revision 7**, and the first thing to read:

0. **Are the two folds assigned to the right questions, and is the wider one
   wide enough?** (`domain/names.py`.) The argument is in §0.4: the
   capitalisation exemption must be *narrower* than the collision key, because
   an over-wide exemption applies a rename without a human while an over-wide
   collision key only refuses. Three things worth attacking specifically:
   (a) whether NFC is the right normalisation, or whether NFKC — which would
   additionally fold a full-width `Ａ` onto `A` — is what a name claim should
   mean, noting that NFKC merges characters that are merely
   similar and so refuses more; (b) whether treating an NFC/NFD difference as
   identity-neutral and *applying* it is right, or whether it should be refused
   like any other spelling change, since it is not literally capitalisation;
   and (c) whether a locale-independent fold is correct for this community —
   `Test Işık -> Test IŞIK` is currently a `mapped_name_change`, and under a
   Turkish tailoring it would be a capitalisation fix. The importer applies no
   tailoring deliberately, because a locale-dependent identity rule would make
   the same import mean different things on different hosts.

0d. **Is the Python-side scan in `find_by_display_name` acceptable, and is the
    threshold right?** It is a sequential scan per lookup, once per created or
    re-spelled row. The argument is that the alternative — a SQL predicate — is
    *narrower than the comparison* and would skip real matches, which is the
    defect rather than a trade. The stated threshold is roughly 2,000 characters
    or the first request path that calls it. If a reviewer thinks either number
    or the "operator tool only" assumption is wrong, the answer is a migration
    that stores and indexes the identity key, and it should be scheduled rather
    than discovered.

**Carried from revision 6:**

0e. **Is fail-closed on every mapped name change the right trade?**
   (`application/sheet_import.py`, `_name_change_refusal`.) The argument is in
   §0.3: an in-place rename and a fresh-name permutation of mapped rows are
   *observationally identical*, so any rule that applies one applies the other,
   and the wrong reading crosses two players' identities silently. The cost is
   real and falls on ordinary use — a Council member renaming one character now
   stops the import, and nothing in the platform yet lets them say "yes, that is
   a rename" (§11 item 5). Two things worth attacking specifically: (a) whether
   the case-only exemption is genuinely identity-neutral, given that the parser
   folds with `casefold()` and the database lookup folds with `lower()` (§11 item
   8 — they differ for `ß`); and (b) whether `mapped_name_change` should be an
   error at all, or a *warning* that lets the rest of the run commit. It is an
   error deliberately, because the run is one transaction and a name change is
   the one edit that can be a disguised identity move — but that is a policy
   choice a maintainer may take differently.

Carried, in descending order of what would hurt most if wrong:

1. ~~**`_RunStructure` and `_refuse_name_change`.**~~ **Answered, against the
   claim.** Revision 4 asked a reviewer to attack "these six signals cover every
   way a row can move under a mapping", and offered a case it could not
   construct. The maintainer constructed one: permute the rows *and* rename every
   displaced character to a fresh name (§0.3). The signals are gone, and with
   them the claim. What replaces item 1 is item 0 above.
2. **`Actor.sheet_updates()` diffing against the load-time snapshot**
   (`models/actor.py`). If the snapshot is not exactly what a save would have
   written, a genuine change can be skipped. The snapshot is taken by calling
   the same `_managed_cells()` the save uses, immediately after load, which is
   the argument — but `Skills.get_sheet_data()` reserialises free text, and a
   value that does not round-trip through parse→serialise would appear changed
   on every save. That is the safe direction (an extra write, not a skipped
   one), but confirm it is the direction it fails in.
3. **`verify_sheet_row()` as a containment rather than a fix.** It closes the
   window to one API call; it does not close it. Is one extra Sheets read per
   mutation the right price, and is failing closed the right behaviour when the
   verification read itself fails?
4. **The blocked findings, §3.** Specifically whether the recommendation in
   OD-17 (attributable announcements now, Council-only mutations later) is the
   right interim, and whether OD-39's value-by-value table asks the right
   questions.
5. **`AmbiguousActorError` as a live behaviour change.** A character sharing a
   name with another now cannot use any command. That is fail-closed and
   correct, but if two such rows exist in the live Sheet today, those players
   are blocked from the moment this deploys. Worth checking the Sheet before
   deploying — the importer's `duplicate` code would find them.
6. **Recursive payload freezing refusing unsupported types.** `AuditEvent` now
   raises on a `set`, `bytes` or an arbitrary object. If any future caller
   passes a `datetime` or a `UUID` directly it will fail at construction rather
   than be coerced. Deliberate, but it is a constraint on every future audit
   writer.
7. **Carried from revision 1, still live:** the dry run writes and rolls back;
   all-or-nothing versus per-row commit; concurrency between two importers; the
   five-column layout guard; ~2N query shape; `tests/fakes.py` fidelity; the
   blank-row skip.

---

## 13. Repository state and status

Branch `docs/platform-plan`, **nothing committed, nothing pushed, no remote
touched** — in revision 7 as in revisions 1–6. No `git commit`, `git push`,
`git reset`, `git checkout`, `git restore` or `git stash` was run at any point.
All uncommitted work present at the start of each session was preserved,
including the maintainer's Phase 5 Living Cost scheduling requirements in
`docs/implementation-plan.md` and the OD-36 amendment of 2026-08-02, which this
work read and left unchanged. Nothing was discarded or overwritten, and no file
was deleted.

The files temporarily reverted to prove regression tests fail without their fix
— two in revision 4, one (`application/sheet_import.py`) in revision 6, one
(`adapters/database/repositories.py`) in revision 7 — were each restored from a
copy taken beforehand and confirmed byte-identical with `cmp`, and the suite
re-run green afterwards. Revision 7's application-layer proof needed no revert
at all: its nine service tests were written and run against the untouched tree
before any production file was edited.

`.env`, credentials, live Sheets, Discord, Foundry and production databases were
not read or modified. The only database written to was `freedom_test`, which is
disposable and is left migrated and empty of rows. No live Lavalink process was
inspected, stopped or reconfigured.

The former music implementation and its Lavalink deployment assets are removed
under [OD-40](../discovery/open-decisions.md#od-40--music-platform-work--closed-2026-07-31-amended-2026-07-31)
— **removed, not deferred**.

### Status

**Every finding raised within the approved Phase 2 review gate is fixed and
covered by regression tests** — including the identity defect revision 5 missed
and the normalization defect Codex raised against revision 6 (I-01).
**This is not a claim that the plan §12 Phase 2 milestone is complete**: the
criteria below are the subset that applies to the Sheet identity-import slice,
and the Foundry-snapshot deliverable that the rest of §12 is written around is
not in it. Against those criteria:

| Criterion | State |
|---|---|
| All active characters map or are explicitly unresolved | Met. Every row resolves through `sheet_row_mappings`, or is reported with a row number, a field and a code |
| Duplicates and malformed fields are reported | Met. `duplicate`, `unmapped_name_collision`, `name_collision`, `row_identity_shift`, `mapped_name_change`, `dangling_mapping`, `absent_from_source`, plus per-field parse issues. Every one of them decides "same name?" through the single policy in `domain/names.py`, proved against fakes *and* real PostgreSQL over one shared table (§2.14) |
| Repeated imports do not create duplicates | Met, and enforced by the database: `UNIQUE (sheet_tab, row_index)` and `UNIQUE (character_id, sheet_tab)`, not by importer convention |
| Import failure cannot partially commit | Met. One run is one transaction; any error rolls the whole run back, including valid rows. Covered against real PostgreSQL |
| Real data is not copied into tests | Met. Every fixture, credential and canary in this work is synthetic |
| Dry-runnable importer, no production writes | Met. The default is a dry run; the Sheet is opened read-only and `batch_update` is never called |
| Stable external mappings | Met. `characters.id` is application-generated and independent of any external key (OD-35 option (a)) |
| Validation and reconciliation reports | Met, with the reservation below |

**Three reservations this document will not paper over.**

1. **The Foundry active-character snapshot importer is not in this slice.** Plan
   §12 lists it as a Phase 2 deliverable. This submission covers the Sheet
   identity import only. Whether Phase 2 closes without it, or stays open for a
   second slice, is the maintainer's call and is the single largest scope
   question in front of this review. Nothing in revision 6 changes that: the
   milestone is **not** claimed finished.
2. **The importer has never run against a real Sheet.** That needs the production
   service account and is a maintainer decision, not an agent's. It remains the
   largest evidence gap here.
3. **A genuine rename now has no in-platform remedy.** Revision 6 refuses every
   mapped name change and the platform has no reconciliation or re-key command
   to answer with. That is a deliberate, fail-closed gap rather than a defect,
   but it is a real operational cost and it is §11 item 5.
4. **The database still does not enforce display-name uniqueness.** Revision 7
   makes every importer layer agree on one comparison, but `characters` carries
   no constraint, so the refusal is the application's alone. A writer that is
   not this importer could still create a duplicate. §11 item 8.
5. **Independent review completed.** Revision 7 was implemented by Claude and
   independently re-reviewed by Codex. Codex found no blocking or important
   implementation issue and reproduced the full PostgreSQL suite at 785 passed,
   0 skipped. Peter Duscha accepted the recommendation on 2026-08-02; **I-01 is
   closed**. This does not close the Phase 2 gate.

### 13.1 Revision 5 — the gate re-traced independently

The Phase 2 paths were re-traced against the approved gate — *data integrity and
migration safety for import/reconciliation* — without relying on the sections
above. **The identity row below was wrong**; it is retained with its correction
rather than quietly rewritten, because how the check missed the case is the
useful part.

| Path | What was checked | Finding |
|---|---|---|
| **Identity** | `_Resolution`, `_RunStructure`, `_refuse_name_change`, `_is_shifted`, `_rows_by_name` | ~~No new hole.~~ **INCORRECT — superseded by §0.3.** Revision 5 attacked the six-signal claim with a **pure row swap**, found `row_identity_shift` caught it because the moved characters kept their names, and stopped there. It did not try the swap *with* the displaced characters renamed, which is the case where every signal is false and the run commits crossed identities. One variant of an attack is not the attack. The signals no longer exist |
| **Mapping** | `sheet_row_mappings` insert/lookup, `UNIQUE (sheet_tab, row_index)` and `UNIQUE (character_id, sheet_tab)` | Mappings are keyed on position and never re-keyed silently; a duplicate insert becomes an `IntegrityError`, which the CLI translates to exit 5 |
| **Transaction** | `SqlAlchemyUnitOfWork.__enter__/__exit__/commit/rollback` against `SheetCharacterImportService.run` | One run is one session and one transaction. `commit()` is reached only when `applied` — not a dry run, and no ERROR issue. Any exception leaving the block rolls back before the session closes, and a failure *at* `COMMIT` is rolled back by PostgreSQL itself. No path commits part of a run |
| **Audit** | `SqlAlchemyAuditRepository.record`, `AuditEvent.json_payload`, the recursive freeze | Insert-only, no update or delete; the payload is converted back to plain JSON types only at the persistence boundary; a non-finite float is refused at construction |
| **Credential** | `build_values_reader`, `_read_only_credentials`, `_build_read_only_reader` | Every failure shape becomes `SheetCredentialError` and a fixed operator string; both Google distributions are guarded; only the import statement is inside the ruling-B guard |
| **Failure** | All seven `log_expected_failure` sites and the CLI's exit-code translation | Re-proved end-to-end with canaries at DEBUG (§7.0.1). Unexpected exceptions still propagate: no `except Exception` anywhere on these paths |
| **Validation** | `parse_character_rows`, `rows_from_values` | The `Active` column is documented as `int` (0/1) in `sheet-inventory.md` §3 and is read with `UNFORMATTED_VALUE`, so `"1"`/`"0"` is the shape the parser receives. The layout guard checks each identity column's **name and position**, which is what stops an inserted column writing one character's data onto another |

**Revision 5 concluded that no new blocking defect existed and added no test or
fix. That conclusion was wrong**, as §0.3 records; the identity row above is the
one that failed. The other rows were re-read during revision 6 and still hold —
the mapping, transaction, audit, credential, failure and validation paths are
unchanged by this correction, except that the transaction row now also covers a
refused name change, which reaches `rollback()` by the same route as any other
ERROR issue.

Two things revision 5 confirmed as *documented open questions* rather than new
findings remain for the maintainer at §11, and one of them is now load-bearing:

- ~~`find_by_display_name` folds with SQL `lower()` while the parser folds with
  Python `casefold()`. … so the exemption is internally consistent; the
  `lower()` divergence sits in the *collision* lookup beside it.~~
  **INCORRECT — superseded by §0.4.** This was recorded as a documented open
  question about *creation*. It was a blocking defect about *identity*, and the
  reasoning above is where the mistake is visible: the exemption was not
  internally consistent with anything, because it did not merely sit beside the
  collision lookup — it **skipped** it. `_resolve` performed no name lookup at
  all when the two names were `casefold()`-equal, so `Test Straße -> Test
  STRASSE` was classified as a permitted re-capitalisation *and* never checked
  against the character already holding `Test STRASSE`, committing two
  characters under one display name. Codex raised it as I-01; revision 7 fixes
  it (§2.14). The database-uniqueness half of §11 item 8 remains open.
- `rows_from_values` keys rows by header **name**, so two columns sharing a
  header would collapse to the last one. The layout guard pins the five identity
  columns by name *and* position, which stops the identity fields being affected;
  a duplicate header elsewhere in the tab is not read by this importer at all.

**Outside the gate, and open:** OD-17 and OD-39 are real, unfixed risks in the
legacy Discord command surface. Phase 2 neither introduced nor worsened either
one, and they are answered at the Phase 3 and Phase 5.7/5.8 gates respectively
(§3). No Phase 3 work and no part of the plan §7.4 magic-item catalogue has been
started.

### 13.2 Revision 7 — what this correction did and did not touch

Traced against the approved gate — *data integrity and migration safety for
import/reconciliation* — for the paths this change reaches:

| Path | What changed | State |
|---|---|---|
| **Name comparison** | One policy in `domain/names.py`; parser, service, fake repository and PostgreSQL adapter all call it; no `casefold()` or `lower()` remains on the importer's identity path | Fixed, with a table-driven agreement test run against fakes **and** real PostgreSQL |
| **Collision lookup** | Performed for every creation and every non-exact mapped name, including a capitalisation-only one; previously skipped whenever the two names were `casefold()`-equal | Fixed; `name_collision` now also covers a re-spelling onto a claimed name |
| **Identity** | `is_semantic_name_change` delegates to the policy. `Test Straße -> Test STRASSE` is a rename, refused like any other; `Test Smith A -> TEST SMITH A` still applies, after the lookup | Fixed |
| **Transaction** | Unchanged. The new refusal is an ERROR issue and reaches `rollback()` by the same route as every other one | Unchanged, re-proved: a mixed run of update + refusal + creation rolls back characters, versions, mappings and audit together, against PostgreSQL |
| **Audit** | Unchanged. No new action, no new payload field, no new writer | Unchanged; a refused run writes nothing, checked by `correlation_id` against PostgreSQL |
| **Migrations / schema** | None. `alembic check` reports no new upgrade operations | Unchanged |
| **CLI** | Unchanged. No new exit code; the new refusal is exit `1` like every other reported error | Unchanged, 40 tests green |
| **Credential / logging / failure** | Not touched by this revision | Unchanged from revision 6 |
| **Legacy bot** | `models/actor.py`'s `AmbiguousActorError` still uses `str.lower()` on the Sheet value. Deliberately not touched: it reads the live Sheet, it is not on the importer's path, and changing a live lookup is a behaviour change outside this correction | Open, §11 item 8 |

**What this revision does not claim.** It closes one blocking defect. It does
not close the Phase 2 gate: the Foundry snapshot importer, the exhaustive field
profile, the reconciliation/correction controls, the runtime-role and
concurrency evidence and the supervised real-snapshot rehearsal are all still
outstanding (issue **I-02**). The normalization correction was independently
reviewed by Codex and accepted by Peter Duscha on 2026-08-02; **I-01 is closed**.
The Phase 2 gate remains deferred.
