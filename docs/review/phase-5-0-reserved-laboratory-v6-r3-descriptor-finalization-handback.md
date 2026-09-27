# C-P5.0-LAB-V6-R3 — descriptor finalization, remediation handback — 2026-09-16

One bounded repository-local remediation of Codex Blocking finding
**PR-20260916-LAB-V6R2-1**, from the independent re-review of C-P5.0-LAB-V6-R2.

**Nothing here closes a finding, resolves LAB-V6-1 through LAB-V6-3, confirms a
V6 or I3 fact, approves a digest or advances a gate. No host was touched.**

Returned for **independent Codex technical and security re-review**.

---

## 1. The defect, reproduced before the fix

The R2 pass classified every *operation* after a successful `mkdirat`. It did
not classify the **release of the descriptor those operations were issued
through**, which is the last thing each of them does.

Codex's reproduction — the first `os.close(fd)` at the end of
`_complete_creation()` closing the real descriptor and then raising — run
against the submitted R2 tree:

```text
OSError: [Errno 5] injected close failure at /secret
V11 exists on disk        : True
provisioner.created       : ()
ProvisioningRun returned  : None
```

Driving every release site, in both orders a `close()` can fail in, against the
same tree:

| Injection | Result before the fix |
|---|---|
| created-object descriptor, close-then-raise | `*** RAW OSError ***`, V11 on disk, `created=0` |
| created-object descriptor, raise-before-close | `*** RAW OSError ***`, V11 on disk, `created=0` |
| synchronizable + traversal parent descriptors | `*** RAW OSError ***`, V11 on disk, `created=1` |
| traversal parent descriptor alone | `*** RAW OSError ***`, V11 on disk, `created=1` |
| **primary `fchown` refusal** + close failure | `*** RAW OSError ***` — `OWNERSHIP_NOT_APPLIED` **erased** |
| **primary `fchmod` refusal** + close failure | `*** RAW OSError ***` — `MODE_NOT_APPLIED` **erased** |
| **primary barrier refusal** + close failure | `*** RAW OSError ***` — `BARRIER_FAILED` **erased** |

The second half of that table is the part the finding names and the R2 tree made
worse than a bare escape: `finally: os.close(fd)` raising **while a
`ProvisioningRefused` was unwinding through it** replaced a classified fact
about the operator's object with an unclassified error about a descriptor.

The same three injections after the fix:

| Injection | Result after the fix |
|---|---|
| created-object descriptor, either order | `descriptor-not-released`, V11 on disk, `created=1` |
| synchronizable + traversal parents | `descriptor-not-released`, V11 on disk, `created=1` |
| traversal parent alone | `descriptor-not-released`, V11 on disk, `created=1` |
| primary `fchown` refusal + close failure | **`post-creation-ownership-not-applied`** preserved |
| primary `fchmod` refusal + close failure | **`post-creation-mode-not-applied`** preserved |
| primary barrier refusal + close failure | **`durability-barrier-failed`** preserved |

## 2. The fix, and the invariant it rests on

**Releasing a descriptor is an operation, not cleanup.** `_release(fd) -> bool`
closes once and **reports** whether the system said it worked. Reporting rather
than raising is what makes the two situations a `finally` conflated
distinguishable:

1. **a refusal is already in flight.** It is the causal one, it already carries
   the object, and it is preserved **exactly** — classification, item and
   detail. Both descriptors are still released whichever reports first, so a
   failure on one does not leak the one after it. This is the precedence rule,
   and it is stated in `ensure`'s and `_complete_creation`'s docstrings and
   asserted in fourteen tests; and
2. **nothing else failed.** Then the failure to release is the whole story:
   `DESCRIPTOR_NOT_RELEASED`, a **seventh** member of
   `POST_CREATION_REFUSALS`, exposing no path, no content, no `errno` name or
   number and no operating-system message.

**The object travels exactly once.** `_unreleased` carries the `AppliedItem`
the item had already reached — the one `_record` made when the creation
completed, or the `ALREADY_PROVISIONED` one a verification returned. It
constructs nothing and records nothing, so the returned `ProvisioningRun` and
the provisioner's live `created` account agree, and one directory is never
reported as two. `RV-duplicate-item` reverses exactly this and is caught.

**Identity is preserved where it was established.** The read-back that sets
`(st_dev, st_ino)` is issued on the created descriptor **before** it is
released, so every release failure on the application path leaves an
`Outcome.CREATED` item with an identity and guarded rollback available. The
`CREATED_IDENTITY_UNKNOWN` residue path is untouched and still refuses automatic
rollback for the whole reversal.

**The barrier is not issued after the decision to refuse.** When the created
object's own descriptor will not release, `fsync` on the parent is not called:
this application refuses before an effect rather than after it. The consequence
is stated rather than hidden — the refusal's detail says the entry is visible
and is not durable, and the object is recorded so an operator can reverse it.
Asserted by counting `os.fsync` calls (`barriers == 0`).

**An ambiguous close is treated as ambiguous.** The descriptor is not reused and
`close()` is **not retried** on it: a second `close()` of a number the kernel
has already released can close a descriptor something else has since been
handed. `_release` contains exactly one `close` call and no `raise`, asserted
structurally, and no descriptor is passed to `os.close` twice, asserted
behaviourally. **Nothing here establishes that a descriptor leaked and nothing
establishes that it did not.** What is refused on is this application's
inability to say the step finished cleanly — which is observable — not the
descriptor's fate, which is not.

### Every descriptor, and what happens to it

| Descriptor | Released in | Before | After |
|---|---|---|---|
| the created object's | `_complete_creation`, after the read-back | `finally: os.close(fd)` — raised, and replaced the primary refusal | `_release`; primary preserved, else `DESCRIPTOR_NOT_RELEASED` with identity |
| the parent's synchronizable | `ensure` | `finally:` — raised, and skipped the traversal close | `_release`; both always attempted |
| the parent's traversal | `ensure` | `finally:` — leaked whenever the first raised | `_release`; both always attempted |
| both parents, on `_open_parent`'s own error paths | `_open_parent` | bare `os.close` — replaced `PARENT_REPLACED`/`PARENT_UNSAFE_OWNERSHIP` | `_release`; primary preserved |

## 3. What is reported rather than repaired — please scope this

**Four bare `os.close` calls are unchanged, and they still raise** — two in
`_verify_one` (the object's descriptor and the parent's) and two in `_remove`
(the same pair). They are the only direct `os.close` calls left in the module
besides the one inside `_release`. Reproduced against the submitted tree, by
entry point:

```text
verify() -> _verify_one(): object descriptor      *** RAW OSError ***
verify() -> _verify_one(): parent descriptor      *** RAW OSError ***
_existing() -> _verify_one(), inside ensure()     *** RAW OSError ***
rollback() -> _remove(): object descriptor        *** RAW OSError ***
```

They are left alone deliberately, and the reasoning is offered for the reviewer
to accept or overrule:

* all four are **outside the window PR-20260916-LAB-V6R2-1 names** — they are
  reached before any `mkdirat` or after a reversal has begun — and the
  assignment enumerates three descriptors, which are the three in §2;
* `_verify_one` is `verify()`'s, and `verify()` is the **read-only V6
  re-observation** of r6 §9.3 **I12**, whose stated contract is to return every
  finding rather than to refuse on the first. Making its releases swallow or
  refuse changes that contract, and a contract change is a maintainer's
  decision, not a widening an implementer may take; and
* the scope section of this assignment says this pass fixes
  **PR-20260916-LAB-V6R2-1 only**.

The `_existing` row is the one most worth a decision: it is reachable from
`ensure()` on the application path, so a raw `OSError` can still leave `ensure`
when the object is **already provisioned**. Nothing is created on that path, so
no partial state is misreported — but it is the same defect shape in the same
call path. `test_an_already_provisioned_item_whose_descriptor_will_not_release_refuses`
breaks the third release for that reason, and its docstring records why.

**Recommendation: a bounded R4 covering `_verify_one` and `_remove`**, with the
`verify()` contract question decided explicitly. This pass does not take it.

## 4. Tests

**28 new tests**, all over real temporary-directory objects with a real failure
injected at a real `os.close`. The focused module moves **60 → 88**, and the
evidence suite total by the same 28.

| Test | Count | What it holds |
|---|---|---|
| `…_at_each_descriptor_is_closed_and_accounts_for_the_object` | 6 | three descriptors x both close orders: no raw `OSError`; the closed classification; the residue's exact owner and mode; the object in `applied` and `created` **exactly once**; later items `not_attempted`; identity recorded and rollback available; no injected message, model root or `errno` text in the detail; private account equals the returned run |
| `…_the_reviewer_reproduction_is_closed` | 2 | Codex's four reported symptoms, in both orders |
| `…_refuses_before_the_barrier` | 1 | `os.fsync` call count is **0**; the detail says the entry is not durable |
| `…_reports_the_objects_completed_before_it` | 1 | breaks V4's release: V11 complete, V4 unfinished, V9/V5 untried, both reversible |
| `…_still_releases_the_descriptor_after_it` | 1 | three descriptors opened, **three** releases attempted, all distinct |
| `…_is_never_closed_again` | 1 | no descriptor passed to `os.close` twice, including one whose release released nothing |
| `…_never_replaces_an_established_refusal` | 12 | all six row-87 refusals x both close orders; each primary classification survives |
| `…_replaces_a_refusal_raised_before_any_creation` | 1 | `PARENT_UNSAFE_OWNERSHIP` and `OBJECT_WRONG_MODE` survive |
| `…_keeps_guarded_rollback` | 1 | reversal succeeds; and refuses `ROLLBACK_IDENTITY_MISMATCH` on a replaced object, removing nothing |
| `…_already_provisioned_item_…_refuses` | 1 | `applied` holds it, `created` is empty, inode and `st_ctime_ns` unchanged |
| `…_releases_every_descriptor_through_one_helper` | 1 | structural: no bare `os.close` in the three releasing functions; `_release` has exactly one `close` and no `raise` |

**All 60 R2 tests are retained and pass unchanged** — successful creation, the
idempotent re-run, every existing-object refusal, the parent and identity
refusals, all six R2 post-creation failure rows, the partial-later-item failure,
every rollback boundary and the V7 stop. One existing test was **extended**, not
altered: `test_every_post_creation_failure_point_has_its_own_closed_classification`
moves from six classifications to seven and derives the union from the two
injection tables rather than typing it.

**Twelve single-point reversals, all twelve caught.**

| Reversal | Caught by |
|---|---|
| **`RV-release-raises`** — `_release` raises instead of reporting | **10 tests. This is Codex's reproduction** |
| `RV-complete-finally` — restore `finally: os.close(fd)` in `_complete_creation` | 8 tests |
| `RV-ensure-finally` — restore `finally:` releasing both parents in `ensure` | 6 tests |
| `RV-retry-close` — retry `close()` on a descriptor whose state is unknown | 5 tests |
| `RV-no-refusal` — swallow the release failure and report the item clean | 3 tests |
| `RV-duplicate-item` — record a second `AppliedItem` for the same object | 3 tests |
| `RV-precedence-ensure` — let the parent release failure replace the primary | 2 tests |
| `RV-post-creation-set` — drop the seventh classification from the closed set | 2 tests |
| `RV-precedence-complete` — let the finalization failure replace the primary | 1 test |
| `RV-skip-traversal` — short-circuit the two releases | 1 test |
| `RV-barrier-after-refusal` — issue the barrier after deciding to refuse | 1 test |
| `RV-open-parent-close` — restore bare `os.close` in `_open_parent`'s cleanup | 1 test |

## 5. Evidence

Local, restricted, **`TEST_DATABASE_URL` unset** (verified unset before the
run), suites run **serially**, against the tree being submitted.

| Check | Result |
|---|---|
| New close-failure regressions | **28 passed** |
| Focused V6 provisioning module | **88 passed**, 2 warnings |
| `tests/phase_5_0_evidence` | **2 331 passed, 0 failed, 0 skipped**, 2 warnings |
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
fails on its own premise with `no untracked directory in this tree; this test
proves nothing`. The same single failure is recorded in the D12-R1, V6-R1 and
V6-R2 handbacks. **This pass created no untracked directory** — it modified two
already-untracked files and adds one file to an existing tracked directory —
and `git status` confirms the tree contains no untracked directory at all.

**Checks not run, and why.**

* **The 80-skip PostgreSQL database run was not performed.** This authorization
  permits `TEST_DATABASE_URL` unset only, so **every skip above is unverified
  and none of it is PostgreSQL evidence.**
* **No check was run on `oracle-test`, and no host was touched.** No host action
  is authorized. The figures above are from local runners on this workstation
  and are **not canonical-environment evidence**; `.agents/AGENTS.md` names
  `/opt/freedom-blades/runtime/venv-web/bin/python` **on `oracle-test`**, and
  that path existing here establishes nothing about there.
* **No formatter, linter or type checker was run** — none is configured in this
  repository. That is a statement about the repository, not a check skipped.
* One command was **refused by the repository secrets guard** and was not
  retried in a form that would defeat it: a `grep` whose *pattern* listed
  secret-file names. The scan was re-run without those tokens over the files
  this pass touched; no credential-shaped content was found, and no
  secret-bearing file was read at any point.
* Interpreters, each verified before use: `/opt/freedom-blades/runtime/venv-web/bin/python`
  (3.12.3, pytest 9.1.1) for the evidence suite; `/opt/discord-bots/venv/bin/python`
  and `/opt/discord-bots/venv-web/bin/python` (3.12.3, pytest 8.4.2) for bot and
  web; node v24.20.0.

## 6. Generated artifacts

One covered source changed, so the artifacts were regenerated through the
**non-executing** CLI only:

```text
python -m tools.phase_5_0_evidence.execution.cli \
  --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`.

* Three consecutive generations are **byte-identical** — manifest and plan — and
  the third was installed and compared byte for byte.
* `source_digests` is **44** paths, the same path set as before: **zero added,
  zero removed**, and **exactly one entry moved** —
  `tools/phase_5_0_evidence/execution/provisioner.py`.
* All 44 hashes independently recomputed from disk: **zero mismatches**.
* **`manifest_version` stays 13.** This pass changes a covered source's bytes,
  not what a digest covers. `source_digests` is the only top-level key that
  differs.
* The installed plan differs from the previous one in **one line**, its digest.
* Dry run: `executable : False`; `unresolved conflicts : 3 (C-7)`; twelve
  unconfirmed facts listed, each refusing the executor before any command
  starts.

New review-input digest
`5602eb95251f07f4942fd3c49b9f5461ce245c96b8848c4b4d87d6605fcba500`, replacing
the R2 digest `ac3ce2b7c3cc17faf2f280e6ba546c24af60ff467c60dcd2ab48fe6a0f6550fd`
recorded in the R2 handback. **Review input only. Do not pass it to
`--execute`.**

## 7. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/provisioner.py` | new `_release` and `_unreleased`; `DESCRIPTOR_NOT_RELEASED` added to `PROVISIONER_REFUSALS` and `POST_CREATION_REFUSALS`; `_complete_creation`'s `finally` split into a precedence-preserving `except` and a refusing release; `ensure`'s `finally` likewise, with both parents always released; `_open_parent`'s two cleanup paths routed through `_release`; `ProvisioningRefused.partial` contract amended; module docstring section; `__all__` |
| `tests/phase_5_0_evidence/test_v6_provisioning.py` | new section 10 — the `failing_close` injector, the two tables and **28 tests**; `test_every_post_creation_failure_point_has_its_own_closed_classification` extended to seven; imports. The 60 existing tests are otherwise unchanged |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | §7.1's applier row and its *"What a partial application returns"* rule extended with rules 4 and 5, the ambiguous-close statement and the two unchanged sites; §9.2 row **88** |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated (§6) |
| `docs/operations/disposable-test-server.md` | dated restriction banner |
| `docs/project-management/raid-register.md` | dated entry |
| `docs/review/Handover information` | dated entry at the top |
| this handback | new |

**Not changed, deliberately:** `provisioning.py` — no reviewed item definition,
owner, group, mode, creation, persistence, verification or rollback field moves.
`review_manifest.py` — the covered set and the manifest version are unchanged.
`_verify_one` and `_remove` — §3. `docs/implementation-plan.md` §20 — the action
pointer is the maintainer's.

## 8. Rollback of this repository change

Revert `tools/phase_5_0_evidence/execution/provisioner.py` and
`tests/phase_5_0_evidence/test_v6_provisioning.py` to their C-P5.0-LAB-V6-R2
state, revert the three amended passages and row 88 in r6, regenerate the two
artifacts through the non-executing CLI, and the digest returns to
`ac3ce2b7c3cc17faf2f280e6ba546c24af60ff467c60dcd2ab48fe6a0f6550fd`. Nothing
outside this repository is affected, **because nothing outside it was touched.**

## 9. Scope, and what is still open

This pass fixed **PR-20260916-LAB-V6R2-1 only**. Not decided, not worked around,
and still maintainer stop conditions: **LAB-V6-1** (`/opt/freedom-blades` owned
by `ubuntu`, defeating V11's root-only entry claim), **LAB-V6-2**
(`/var/lib/freedom-blades` absent with no provisioning item) and **LAB-V6-3**
(r6's `R` conflicting with the approved target root, and `EVIDENCE_ROLE` with no
production registration). **V11 must remain unapplied while they are open.**

No implicit parent was defined, no mode widened, `R` was not relocated, no
production evidence role registered, LAB-X1's route not chosen, no real
participant, boundary or materializer wired, and the accepted trusted-operator
boundary is unaltered. V11's reviewed definition, the separation of actual
provisioning identity from declared owner, V7's exclusion, the V7-absent
fail-closed state, the read-only verification boundary, the pre-`rmdir`
emptiness check, the `CREATED_IDENTITY_UNKNOWN` residue path and the guarded,
operator-directed reversal are all preserved. **No automatic rollback was added
to `apply()`, and the released provisioning subset was not broadened.**

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

## 10. Proposed reviewer focus

1. **The scope call in §3.** Four release sites still raise. Is leaving
   `_verify_one` and `_remove` to a bounded R4 right, or does the `_existing`
   path make them part of this finding?
2. Whether `DESCRIPTOR_NOT_RELEASED` belongs in `POST_CREATION_REFUSALS` given
   it is also raised on the already-provisioned path, where no `mkdirat`
   occurred.
3. Whether refusing **before** the barrier — rather than issuing it and then
   refusing — is the right trade when the created object's descriptor will not
   release. The entry is then visible and not durable, and the refusal says so.
4. Whether the precedence rule is the right one: the primary refusal is
   preserved and the subordinate release failure is **dropped entirely**, not
   recorded on the exception. An operator learns their object's real cause and
   learns nothing about the descriptor.
5. Whether an `ALREADY_PROVISIONED` item is the right thing for `_unreleased`
   to carry on `partial`, given `applied` answers *what is on disk* and
   `created` correctly stays empty.
6. Whether `_release` returning a bool — rather than raising a typed internal
   error — keeps the two call sites honest, and whether any release path
   remains where a failure is silently discarded without a refusal.

**Next action: independent Codex technical and security re-review.** The
implementer closes no finding, resolves no LAB-V6 decision, confirms no V6/I3
fact, approves no digest and advances no gate.
