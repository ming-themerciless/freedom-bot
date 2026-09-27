# C-P5.0-LAB-V6-R4 — verification and rollback descriptor finalization, remediation handback — 2026-09-16

One bounded repository-local remediation of Codex Blocking finding
**PR-20260916-LAB-V6R3-1**, from the independent technical and security
re-review of C-P5.0-LAB-V6-R3.

**Nothing here closes a finding, resolves LAB-V6-1 through LAB-V6-3, confirms a
V6 or I3 fact, approves a digest or advances a gate. No host was touched.**

Returned for **independent Codex technical and security re-review**.

---

## 1. The defect, reproduced before the fix

The R3 pass routed the three descriptors the *application* path holds through
`_release`, and reported that four bare `os.close` calls were left: the observed
object's and its parent's in `_verify_one`, and the same pair in `_remove`. All
four still raised. Driven against that tree, over real temporary-directory
objects with a real failure injected at a real `os.close`:

```text
== 1. verify(): the read-only V6 re-observation ==
object descriptor, close-then-raise            *** RAW OSError *** [Errno 5] injected close failure
a later target still observed                  *** RAW OSError *** [Errno 5] injected close failure

== 2. apply() over an already-provisioned host ==
idempotent apply, object descriptor            *** RAW OSError *** [Errno 5] injected close failure

== 3. primary-refusal precedence ==
wrong mode + failing release, via apply()      *** RAW OSError *** [Errno 5] injected close failure
replaced object + failing release, rollback    *** RAW OSError *** [Errno 5] injected close failure

== 4. accounting after a successful rmdir ==
parent descriptor after rmdir                  *** RAW OSError *** [Errno 5] injected close failure
   object removed from disk                    True
   provisioner.created still says              ['V11']
   a second rollback would target              ['V11']
```

The same six, after the fix:

| Reproduction | Result after the fix |
|---|---|
| `verify()`, object descriptor | **4 observations**, first `discrepancies=['descriptor-not-released']` |
| `verify()`, a later target | **4 observations** — the failure lands on the third target and the fourth is still observed |
| idempotent `apply()` | `refusal=descriptor-not-released`, `applied=['V11']`, `outcome=['already-provisioned']`, `created=[]` |
| wrong mode + failing release | **`object-wrong-mode`** preserved |
| replaced object + failing release | **`rollback-identity-mismatch`** preserved |
| parent descriptor after `rmdir` | `rollback-descriptor-not-released-object-removed`, `removed=['V11']`, object gone `True`, `created=[]` |

The last row is the one the finding calls untruthful live recovery accounting,
and it is the reason a bounded R4 was the right call rather than a tidy-up: the
object was **gone**, and the provisioner went on saying it was there.

## 2. The fix, and the rules it rests on

**No release anywhere in the module is a bare close any more.** `_release` is
the one function in `provisioner.py` that calls `os.close` at all, it calls it
once, and it reports instead of raising. That is asserted structurally over the
module's syntax tree rather than by reading the four sites, so a release added
to a new function tomorrow is caught by the suite rather than by whoever runs
the reversal.

### 2.1 Verification stays complete, and stays read-only

`verify()` is the read-only V6 re-observation of r6 §9.3 **I12** and its
contract is to return findings. A release that does not report success is now a
finding **about the observation**: `DESCRIPTOR_NOT_RELEASED`, **appended** to
that item's `discrepancies`, never displacing the owner, group, mode, link count
and content already read, and never an exception. One `ItemObservation` is
returned for every target, in the order given, and a failure on the first target
does not cost the three after it — which is what a raise did, over a descriptor
rather than over anything about an object.

`_verify_one` is split so that the parent's release is **one statement on every
path out of the observation** rather than a `finally` the object's release can
raise through. That is the specific replacement the finding names: the object's
close being swallowed by the parent's.

`OBSERVATION_DISCREPANCIES` is the closed vocabulary, enforced at construction,
so a read-only finding handed to an operator cannot acquire a new meaning
either.

### 2.2 The same condition through `ensure()` is a closed refusal

`_existing()` reaches the same code on the application path, where a raw
`OSError` would be a refusal nobody classified. The object's own findings decide
first: if the object disagrees with its definition, **that disagreement is the
refusal** and the release is subordinate — reported in the list of
disagreements, never in its place. If the object matches, the release failure is
the whole story: `DESCRIPTOR_NOT_RELEASED`, carrying the `ALREADY_PROVISIONED`
result the verification reached, **exactly once**, with `created` empty because
nothing was created and not a byte written — asserted on `st_ctime_ns`, not
merely on the inode.

### 2.3 A reversal refuses before an effect, and reports the effects it had

The `rmdir` is the line, exactly as the `mkdirat` is on the application path:

| Where the release fails | What happens |
|---|---|
| while an identity-mismatch, not-empty or `rmdir` refusal is unwinding | that refusal is preserved exactly; both descriptors are still released; nothing is removed |
| on the object's descriptor, nothing else in flight | the `rmdir` is **not issued**. `rollback-descriptor-not-released-nothing-removed`; the object is exactly where it was and is still this application's to reverse |
| on the parent's descriptor, after `rmdir` returned success | the object **is** gone. `rollback-descriptor-not-released-object-removed`, the object in the refusal's `removed` account, out of `created` exactly once, and a retry cannot aim at it |

**The live account is updated per removal, not at the end of the loop.** That is
a second, smaller untruth the same shape: any refusal part-way through a
reversal used to leave every object it had already removed in `created`. A
reversal that removes V5 and V9 and then refuses on V4's content now says so —
`removed=['V5','V9']`, `created=['V11','V4']` — and it is asserted without any
close failure at all.

`ROLLBACK_REFUSALS` is the closed vocabulary of what a reversal may refuse with,
and `RollbackRefused` makes the combination that would lie about an effect
unconstructible: the one classification that says *removed* requires the object
in the account, every other requires it absent, and no object appears twice.
`RemovalEffect` has **no member for a removal that did not happen**, because a
refusal is not an effect — so no caller can update an account for an object that
is still there.

### 2.4 What is unchanged, deliberately

An ambiguous `close()` is still treated as ambiguous: not reused, not retried,
and **no leak claimed in either direction**. `_release` still closes once and
still contains no `raise`. Every descriptor after a failing release is still
attempted, and no descriptor is passed to `os.close` twice. No identity is
manufactured, no `AppliedItem` is duplicated, no unexplained object is adopted,
and no verification finding is collapsed into a generic error. No refusal or
discrepancy carries a path, directory content, an `errno` name or number, or an
operating-system message.

Rollback remains guarded and operator-directed. **No automatic rollback was
added to `apply()`**, no identity or emptiness guard was weakened, no implicit
parent was created, V7 was not initialized and the released provisioning subset
was not broadened.

### Every descriptor, and what happens to it

| Descriptor | Released in | Before | After |
|---|---|---|---|
| the created object's | `_complete_creation` | `_release` (R3) | unchanged |
| the parent's synchronizable and traversal | `ensure`, `_open_parent` | `_release` (R3) | unchanged |
| the **observed object's** | `_verify_one` / `_observe_under` | `finally: os.close(fd)` — raised, and was replaceable by the parent's close | `_release`; appended discrepancy, or a closed refusal through `_existing` |
| the **observed parent's** | `_verify_one` | `finally: os.close(parent)` — raised, and replaced the object's failure | `_release`; both always attempted |
| the **reversal's object descriptor** | `_remove` | `finally: os.close(fd)` — raised, and replaced the identity/emptiness refusal | `_release`; primary preserved, else refuse **before** the `rmdir` |
| the **reversal's parent descriptor** | `_remove` | `finally: os.close(parent)` — raised after a successful `rmdir`, before the account was updated | `_release`; the removal is reported as real and leaves `created` |

## 3. Tests

**36 new tests**, all over real temporary-directory objects with a real failure
injected at a real `os.close`, in **both** orders a close can fail in. The
focused module moves **88 → 124**, and the evidence suite total by the same 36.

| Test | Count | What it holds |
|---|---|---|
| `…_verification_returns_every_observation_when_a_release_fails` | 4 | two descriptors x both orders: four observations in target order; the closed appended discrepancy; the facts already read still returned; the three later targets clean; no inode and no `st_ctime_ns` moved |
| `…_verification_release_failure_does_not_stop_the_later_targets` | 2 | the failure lands on the **third** target and the fourth is still observed |
| `…_verification_release_failure_never_replaces_the_objects_findings` | 4 | `(OBJECT_WRONG_MODE, DESCRIPTOR_NOT_RELEASED)`, in that order |
| `…_already_provisioned_apply_whose_verification_cannot_release_refuses` | 4 | closed refusal; the item once, as `already-provisioned`; `created` empty; later items `not_attempted`; `st_ctime_ns` unchanged; nothing removable |
| `…_verification_release_failure_never_replaces_an_apply_refusal` | 4 | `object-wrong-mode` survives, and the release is still listed rather than dropped |
| `…_reversal_release_failure_never_replaces_the_causal_refusal` | 6 | identity mismatch, not empty and a refused `rmdir` x both orders; nothing removed; the live account unchanged |
| `…_release_failure_before_the_rmdir_removes_nothing` | 2 | the object is the same inode afterwards, `created` still names it, and the reversal it was offered still works |
| `…_release_failure_after_the_rmdir_reports_the_removal` | 2 | the object is gone; `removed=['V11']`; `created == ()`; a retry removes nothing rather than reaching for the name |
| `…_reversal_that_refuses_part_way_reports_what_it_already_removed` | 1 | V5 and V9 removed, V4 refuses, and both accounts agree — **no close failure involved** |
| `…_every_verification_descriptor_after_a_failing_release_is_still_attempted` | 1 | **eight** descriptors, eight releases attempted, all distinct |
| `…_reversals_parent_descriptor_is_released_after_its_object_descriptor_fails` | 1 | both attempted, neither closed twice |
| `…_the_four_reported_release_sites_no_longer_raise` | 1 | the R3 handback's own reproduction table |
| `…_no_release_anywhere_in_the_module_is_a_bare_close` | 1 | structural: `_release` is the only function that calls `os.close` |
| `…_reversal_refusal_cannot_disagree_with_what_it_removed` | 1 | the invalid effect/outcome combinations are unconstructible |
| `…_observation_reports_only_findings_from_the_closed_vocabulary` | 1 | closed, additive and idempotent |
| `…_removal_effect_exists_only_where_the_object_is_gone` | 1 | no member for a removal that did not happen |

**All 88 R3 tests are retained and pass unchanged** — successful creation, the
idempotent re-run, every existing-object refusal, the parent and identity
refusals, all six R2 post-creation rows, all R3 close-failure rows, the partial
application, every rollback guard and the V7 stop. **No existing test was
altered.**

**The new tests fail against the tree R3 submitted.** With the four bare
`os.close` sites restored and nothing else changed, the focused module reports
**32 failed, 92 passed**: 32 of the 36 new tests fail, and all 88 R3 tests still
pass — which is the point, because none of them injects into these four sites.

**The four that survive are named rather than glossed**, because a control that
passes under the defect is a control that is not testing the correction:
`…_reversal_that_refuses_part_way_reports_what_it_already_removed` (the
end-of-loop accounting is not one of the four closes),
`…_reversal_refusal_cannot_disagree_with_what_it_removed`,
`…_observation_reports_only_findings_from_the_closed_vocabulary` and
`…_removal_effect_exists_only_where_the_object_is_gone` (schema rules, reversed
by their own single-point reversals below).

**Sixteen single-point reversals, all sixteen caught.**

| Reversal | Caught by |
|---|---|
| **`RV-verify-object-close`** — restore the bare close on the observed object | **13 tests** |
| **`RV-verify-parent-close`** — restore the bare close on the observed parent | **11 tests** |
| **`RV-remove-object-close`** — restore the bare close before the `rmdir` | **9 tests** |
| **`RV-remove-parent-close`** — restore the bare close after the `rmdir` | **9 tests** |
| `RV-verify-raises-late` — collect the findings, then raise | 12 tests |
| `RV-forget-at-end` — update the created account after the loop, as before | 8 tests |
| `RV-existing-no-refusal` — swallow the release failure on the idempotent path | 5 tests |
| `RV-observation-replaces` — let the release finding replace the object's | 5 tests |
| `RV-existing-unfiltered` — let the release finding be the refusal | 4 tests |
| `RV-rmdir-issued-anyway` — issue the `rmdir` after the decision to refuse | 4 tests |
| `RV-precedence-remove` — let the reversal's release replace the causal refusal | 4 tests |
| `RV-precedence-verify-parent` — let the parent's release replace the findings | 4 tests |
| `RV-observation-not-idempotent` — report one release failure twice | 2 tests |
| `RV-effect-ignored` — do not refuse on a removal whose finalization failed | 2 tests |
| `RV-refusal-account-unchecked` — drop the effect/outcome agreement check | 1 test |
| `RV-observation-vocabulary-open` — drop the closed discrepancy vocabulary | 1 test |

**One conjunct is not independently falsifiable and is stated rather than
claimed.** Taking `about_the_object[0]` rather than `discrepancies[0]` as the
primary refusal in `_existing` is caught by no test on its own, because the
release finding is **appended last** and the two indices therefore select the
same value. The ordering is the load-bearing part, and `RV-observation-replaces`
and `RV-precedence-verify-parent` are what hold it. The reversal that removes
the filtering entirely — `RV-existing-unfiltered` — is caught.

## 4. Evidence

Local, restricted, **`TEST_DATABASE_URL` unset** (verified unset before each
run), suites run **serially**, against the tree being submitted.

| Check | Result |
|---|---|
| New verification and rollback close-failure regressions | **36 passed** |
| Focused V6 provisioning module | **124 passed**, 2 warnings |
| `tests/phase_5_0_evidence` | **2 367 passed, 0 failed, 0 skipped**, 2 warnings |
| `tests/test_*.py` (bot) | 3 026 passed, 326 skipped, 1 warning |
| `tests/web` | 1 609 passed, **1 failed**, 1 362 skipped |
| `foundry-module/tests` | 171 passed, 0 failed |
| Guards (`.claude/hooks/test_guards.py`) | **31/31** — 19 refused, 12 allowed |
| `compileall` (scoped) | passed |
| `git diff --check` | clean |

The two warnings are the pre-existing `PytestConfigWarning: Unknown config
option` pair (`asyncio_mode`, `asyncio_default_fixture_loop_scope`).

**The one web failure is pre-existing and unrelated, and it says so itself.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own premise: `no untracked directory in this tree; this test proves
nothing`. The same single failure is recorded in the D12-R1, V6-R1, V6-R2 and
V6-R3 handbacks. **This pass created no untracked directory** — it modified
already-untracked and tracked files and added one file to the existing tracked
`docs/review/` directory — and `git status` confirms the tree contains no
untracked directory at all.

**Checks not run, and why.**

* **The 80-skip PostgreSQL database run was not performed.** This authorization
  permits `TEST_DATABASE_URL` unset only, so **every skip above is unverified and
  none of it is PostgreSQL evidence.**
* **No check was run on `oracle-test`, and no host was touched.** No host action
  is authorized. The figures above are from local runners on this workstation and
  are **not canonical-environment evidence**; `.agents/AGENTS.md` names
  `/opt/freedom-blades/runtime/venv-web/bin/python` **on `oracle-test`**, and that
  path existing here establishes nothing about there.
* **No formatter, linter or type checker was run** — none is configured in this
  repository. That is a statement about the repository, not a check skipped.
* Interpreters, each verified before use:
  `/opt/freedom-blades/runtime/venv-web/bin/python` (3.12.3) for the evidence
  suite and the artifact regeneration; `/opt/discord-bots/venv/bin/python` and
  `/opt/discord-bots/venv-web/bin/python` (3.12.3) for bot and web; node
  v24.20.0.

## 5. Generated artifacts

One covered source changed — `tools/phase_5_0_evidence/execution/provisioner.py`
— so the artifacts were regenerated through the **non-executing** CLI only:

```text
python -m tools.phase_5_0_evidence.execution.cli \
  --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`.

* Three consecutive generations are **byte-identical** — manifest and plan — and
  the third was installed and compared byte for byte with the first.
* `source_digests` is **44** paths: **zero added, zero removed**, and **exactly
  one entry moved**, `execution/provisioner.py`.
* All 44 hashes independently recomputed from disk: **zero mismatches**.
* **`manifest_version` stays 13.** `source_digests` is the only top-level key
  that differs from the previously installed manifest.
* Dry run: `executable : False`; `unresolved conflicts : 3 (C-7)`; twelve
  unconfirmed facts listed, each refusing the executor before any command starts.

New review-input digest
`ec55c72106a37a15b9e26e581d1fcfe44f658f4bcdce3e4e5680ecaea9a05de4`. **Review
input only. Do not pass it to `--execute`.**

**One discrepancy in the previously installed artifacts, reported and not
resolved.** The installed concrete plan carried
`5df172565b3b27fe769a87a56f9638e33f25c33c779178d62f0e35a15125d957` — the
**C-P5.0-LAB-D12-R1** digest — and was otherwise byte-identical to the version
at `HEAD`. The R3 handback reports its new digest as `5602eb95…` and states that
the installed plan differs from the previous one in one line, its digest; the
plan on disk does not carry that value, so either the regenerated plan was not
installed or the reported digest was computed from a tree that was not
submitted. R3's digest cannot be recomputed from here, because it is a digest of
source bytes that no longer exist. **This is reported as an observation. The
implementer approves no digest and reconciles none.**

## 6. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/provisioner.py` | `_verify_one` split into itself and `_observe_under`, both releasing through `_release`; `ItemObservation` gains the closed `OBSERVATION_DISCREPANCIES` check and `with_discrepancy`; `_existing` separates the object's findings from the observation's and refuses `DESCRIPTOR_NOT_RELEASED` carrying the `ALREADY_PROVISIONED` item; `_remove` releases through `_release`, refuses before the `rmdir` and returns a `RemovalEffect`; `rollback` forgets each removal as it goes and raises `RollbackRefused` with its removed account; new `RollbackRefused`, `RemovalEffect`, `ROLLBACK_NOT_REMOVED_NOT_RELEASED`, `ROLLBACK_REMOVED_NOT_RELEASED`, `ROLLBACK_REFUSALS`, `ROLLBACK_REMOVING_REFUSALS`; `ProvisioningRefused` records its own `detail`; module docstring section; `__all__` |
| `tests/phase_5_0_evidence/test_v6_provisioning.py` | new section 11 — two release tables, three helpers and **36 tests**; imports. The 88 existing tests are unchanged |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | §7.1's *"two release sites are reported and deliberately unchanged"* passage replaced by rules 6, 7 and 8; §9.2 row **89** |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated (§5) |
| `docs/operations/disposable-test-server.md` | dated restriction banner |
| `docs/project-management/raid-register.md` | dated entry |
| `docs/review/Handover information` | dated entry at the top |
| this handback | new |

**Not changed, deliberately:** `provisioning.py` — no reviewed item definition,
owner, group, mode, creation, persistence, verification or rollback field moves.
`review_manifest.py` — the covered set and the manifest version are unchanged.
r6 §9.3 **I12** — the check is still unperformed and nothing has been applied to
`oracle-test`, so its substance does not move. `docs/implementation-plan.md` §20
— the action pointer is the maintainer's.

## 7. Rollback of this repository change

Revert `tools/phase_5_0_evidence/execution/provisioner.py` and
`tests/phase_5_0_evidence/test_v6_provisioning.py` to their C-P5.0-LAB-V6-R3
state, revert §7.1's replaced passage and row 89 in r6, revert the banner, the
RAID entry and the handover entry, delete this handback, and regenerate the two
artifacts through the non-executing CLI. Nothing outside this repository is
affected, **because nothing outside it was touched.**

## 8. Scope, and what is still open

This pass fixed **PR-20260916-LAB-V6R3-1 only**. Not decided, not worked around,
and still maintainer stop conditions: **LAB-V6-1** (`/opt/freedom-blades` owned
by `ubuntu`, defeating V11's root-only entry claim), **LAB-V6-2**
(`/var/lib/freedom-blades` absent with no provisioning item) and **LAB-V6-3**
(r6's `R` conflicting with the approved target root, and `EVIDENCE_ROLE` with no
production registration). **V11 must remain unapplied while they are open.**

No implicit parent was defined, no mode widened, `R` was not relocated, no
production evidence role registered, LAB-X1's route not chosen, no real
participant, boundary or materializer wired, and the accepted trusted-operator
boundary is unaltered. V7's exclusion, the V7-absent fail-closed state, the
read-only verification boundary, the pre-`rmdir` emptiness check, the
`CREATED_IDENTITY_UNKNOWN` residue path and the guarded, operator-directed
reversal are all preserved.

`plan.is_executable` is **False** and `reservation.REAL_EXECUTION_REFUSAL` is
unconditional. V6 remains performed but **not closed**; **I3 unconfirmed**; V7
excluded; V8 and V10 unperformed; C-7, EH-R16-1, LAB-R6, LAB-X1, LAB-V6-1,
LAB-V6-2, LAB-V6-3, P5.0-R5 and OD-62 **Open**; Package 5.0 **not ready**.

**No host action was performed or is authorized.** No SSH, synchronization,
inspection, `sudo`, user or group creation, `/etc` edit, `/run`, `/var/lib` or
`/opt/freedom-blades` creation, `systemd-tmpfiles`, link, controlled write
verification, provisioning, `lifecycle.json` initialization, database operation,
generated-vector execution, real participant, boundary, materializer or
`--execute`.

## 9. Proposed reviewer focus

1. **The two new rollback classifications.** Is
   `rollback-descriptor-not-released-object-removed` the right operator-facing
   outcome for *removed, finalization uncertain*, and is
   `…-nothing-removed` the right one for a release failure that stops the
   `rmdir`? They are the schema extension this assignment asked for.
2. **`RollbackRefused` carrying a `removed` account on every reversal refusal**,
   including the guards that predate this pass. That is a behaviour change to
   the existing guards' exception type — a subclass, so `ProvisioningRefused`
   callers are unaffected — and it is what makes a part-way reversal readable.
3. **Updating `created` per removal rather than at the end of the loop.** It
   repairs a second untruth of the same shape that the finding does not name.
   Is it in scope, or should it have been reported for a further pass?
4. Whether appending `descriptor-not-released` to an observation's
   discrepancies is the right shape, given `ItemObservation.matches` now returns
   `False` for an object that matches its definition perfectly and whose
   descriptor merely would not release.
5. Whether refusing **before** the `rmdir` when the object's descriptor will not
   release is the right trade. Nothing is removed and the operator must run the
   reversal again; the alternative is removing an object through a descriptor
   whose state this application cannot state.
6. Whether any release path remains where a failure is silently discarded
   without a refusal or a discrepancy — the structural guard proves only that no
   bare `os.close` remains, not that every `_release` result is consumed.
7. **The digest discrepancy in §5.** It is a maintainer and reviewer matter, not
   an implementer's to reconcile.

**Next action: independent Codex technical and security re-review.** The
implementer closes no finding, resolves no LAB-V6 decision, confirms no V6/I3
fact, approves no digest and advances no gate.
