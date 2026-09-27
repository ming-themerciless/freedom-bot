# Claude remediation handback — V6 post-creation partial-state accounting

Authorization: **C-P5.0-LAB-V6-R2**, one bounded repository-local remediation of
Codex Blocking finding **PR-20260916-LAB-V6R1-1** from the
[R1 review](project-review-2026-09-16-reserved-laboratory-v6-provisioning-remediation.md).

Date: 2026-09-16. Author: Claude. Returned for independent Codex technical and
security re-review.

**No host was touched.** No SSH, no synchronization, no target inspection, no
`sudo`, no user or group creation, no edit under `/etc`, nothing created under
real `/run`, `/var/lib` or `/opt/freedom-blades`, no `systemd-tmpfiles`, no
provisioning applied, no `lifecycle.json` initialized, no hard link created, no
controlled I3 write verification, no V8 or V10, no participant wired or invoked,
no database operation, no generated vector executed, no real boundary or
materializer, and no `--execute`. Every object any test created was under
`pytest`'s `tmp_path`.

**This handback closes no finding, resolves none of LAB-V6-1 through LAB-V6-3,
confirms no V6 or I3 fact, approves no digest and advances no gate.**

## 1. The defect, reproduced before the fix

Both of Codex's reproductions were reproduced on the submitted tree before
anything was changed, over real temporary directories, by injecting a failure at
the named `os` call:

```text
injected os.fsync failure (parent barrier):
  path exists             = True
  ProvisioningRun.applied = ()
  ProvisioningRun.created = ()
  refusal                 = durability-barrier-failed
  provisioner.created     = (('V11', 'created'),)

injected os.fchmod failure (mode):
  path exists             = True
  raw OSError escaped     = PermissionError
  provisioner.created     = ()

injected os.fchown failure (ownership):
  path exists             = True
  raw OSError escaped     = PermissionError
  provisioner.created     = ()
```

The same script against the repaired tree:

```text
injected os.fsync failure (parent barrier):
  path exists             = True
  ProvisioningRun.applied = ('V11',)
  ProvisioningRun.created = ('V11',)
  refusal                 = durability-barrier-failed

injected os.fchmod failure (mode):
  path exists             = True
  ProvisioningRun.applied = ('V11',)
  ProvisioningRun.created = ('V11',)
  refusal                 = post-creation-mode-not-applied

injected os.fchown failure (ownership):
  path exists             = True
  ProvisioningRun.applied = ('V11',)
  ProvisioningRun.created = ('V11',)
  refusal                 = post-creation-ownership-not-applied
```

## 2. The rule, stated once

`mkdirat` is the line either side of which a failure is a different fact. Before
it, nothing exists and `creation-refused` is the whole story. After it, a
directory is at a provisioned name, and three rules hold with no exception:

1. **the failure is classified, not raised** — into a closed vocabulary that
   names no path, no directory content and no operating-system message;
2. **the object travels with the refusal** — `ProvisioningRefused.partial`
   carries the `AppliedItem`, `apply()` puts it in the returned
   `ProvisioningRun.applied`, and the live provisioner's private `_created` list
   is no longer the only place it appears; and
3. **identity is preserved where the object can still be observed, and claimed
   nowhere else.**

`_create()` is now split at exactly that line: it performs the exclusive
`mkdirat` and hands everything after it to `_complete_creation()`.

## 3. Every post-creation failure point, and what it becomes

`provisioner.POST_CREATION_REFUSALS` is the closed set, and the suite asserts
that the six injections produce exactly it.

| Failure point | Classification | Identity | Why |
|---|---|---|---|
| `open` of the created directory | `post-creation-open-failed` | **unknown** | no descriptor was ever held on the object |
| `fchown` | `post-creation-ownership-not-applied` | known | the created descriptor is still held |
| `fchmod` | `post-creation-mode-not-applied` | known | same |
| read-back `fstat` | `post-creation-verification-unreadable` | **unknown** | the identity comes from that same `fstat` |
| read-back listing | `post-creation-verification-failed` | known | the listing failure is a discrepancy the object carries; `fstat` succeeded |
| parent `fsync` | `durability-barrier-failed` | known | unchanged classification, now reported |

**The identity column is derived, not chosen.** Every failure after the open
still holds the descriptor the creation opened, so `(st_dev, st_ino)` is read
from the object itself. If the open is what failed there is no such descriptor,
and resolving the name a second time would record an identity this application
cannot attribute to its own `mkdirat` — precisely the substitution the reversal
guard exists to catch. `_identity_of()` therefore returns empty rather than
raising, and empty is a real answer: it is what makes the outcome
`CREATED_IDENTITY_UNKNOWN`.

## 4. The result schema, and its invariant

`ProvisioningRun` remains the durable handoff shape. `applied` answers *what is
on disk* and now includes the refusing item whenever that item created
something; the refusal says it is unfinished, and `not_attempted` names every
later item.

`Outcome` gains a third value, `CREATED_IDENTITY_UNKNOWN`. It is neither
`CREATED` — which promises a recorded identity a reversal can re-observe — nor
`ALREADY_PROVISIONED`, which says somebody else's object was verified.

**Invalid combinations are unconstructible.** `AppliedItem.__post_init__`
refuses a `CREATED` item without a well-formed `dev:ino`, and refuses an
identity on an `ALREADY_PROVISIONED` or `CREATED_IDENTITY_UNKNOWN` item. The
first would be a removal guard that compares nothing; the second an invitation
to remove an object this application cannot attribute to itself.

Four derived readings sit on the run, so the residue question and the removal
question are never the same question:

| Property | Answers |
|---|---|
| `created` | everything this application put on disk, identified or not |
| `removable` | the subset a guarded reversal may take |
| `unidentified` | created objects with no recorded identity — residue |
| `recoverable` | whether guarded rollback can reverse everything it created |

## 5. Rollback

Unchanged in its three guards: created-by-this-application, an immediately
re-observed `(st_dev, st_ino)`, and emptiness before the `rmdir`. **No automatic
rollback was added to `apply()`.**

One guard is added: an unidentified residue refuses the **whole** reversal,
before the first `rmdir`, rather than when the reversal reaches that item. A
partial reversal that removed the identified objects and then stopped would
leave a host in a third state nobody asked for. Classification
`rollback-identity-never-established`.

## 6. Tests and reversals

**15 new tests**, all over real temporary-directory objects with a real failure
injected at a real syscall; the module moves from **45** to **60** and the suite
total by the same 15. The six-row parametrized case asserts, for each failure
point: no raw `OSError`; the closed classification; the exact on-disk residue
and that no later item exists; the current object present in `applied` and
`created`; every later item `not_attempted`; whether the identity is known,
stated the same way through four independent readings; that a known identity is
the object's own; and that the refusal text carries neither the injected
path-shaped message, nor the model root, nor `errno` text.

Beside it: the two reviewer reproductions asserted as reported; a failure landing
on **V9** part-way through the sequence, which reports V11 and V4 too and whose
residue observably lacks V9's `3770` — the one item whose reviewed mode differs
from the `mkdirat` mode; rollback of a known-identity residue; rollback refused
for unknown identity, for a replaced object and for a non-empty residue; the
unidentified-residue case that stops the whole reversal with V11 still present;
the `AppliedItem` invariant; and a structural check that the six classifications
are distinct, closed and all reachable.

**All 45 R1 tests are retained and pass unchanged** — successful creation, the
idempotent re-run, every existing-object refusal, the parent and identity
refusals, the partial-later-item failure, the four rollback boundaries and the
V7 stop.

**Nine single-point reversals, all nine caught.**

| Reversal | Caught by |
|---|---|
| **`RV-apply-partial`** — drop the partial item from the returned run | **10 tests. This is Codex reproduction 1** |
| **`RV-translate-fchmod`** — let `fchmod` raise | **6 tests. This is Codex reproduction 2** |
| `RV-translate-fchown` — let `fchown` raise | the `fchown` row |
| `RV-translate-open` — let the post-creation `open` raise | 3 tests |
| `RV-translate-readback` — let the read-back `fstat` raise | the read-back row |
| `RV-identity-tolerant` — make `_identity_of` raise instead of returning empty | the read-back row |
| `RV-created-widened` — narrow `created` back to identified objects | 3 tests |
| `RV-rollback-unknown` — delete the unidentified-residue guard | 2 tests |
| `RV-outcome-invariant` — delete the `AppliedItem` pairing check | the invariant test |

## 7. Evidence

Local, restricted, **`TEST_DATABASE_URL` unset**, suites run serially.

| Check | Result |
|---|---|
| New fault-injection regressions | **15 passed** |
| Focused V6 provisioning module | **60 passed**, 2 warnings |
| `tests/phase_5_0_evidence` | **2 303 passed, 0 failed, 0 skipped**, 2 warnings |
| `tests/test_*.py` (bot) | 3 026 passed, 326 skipped |
| `tests/web` | 1 609 passed, **1 failed**, 1 362 skipped |
| `foundry-module/tests` | 171 passed |
| Guards (`.claude/hooks/test_guards.py`) | **31/31** — 19 refused, 12 allowed |
| `compileall` | passed |
| `git diff --check` | clean |

The two warnings are the pre-existing `PytestConfigWarning: Unknown config
option` pair (`asyncio_mode`, `asyncio_default_fixture_loop_scope`).

**The one web failure is pre-existing and unrelated.**
`tests/web/test_p3_4_static_assets.py::test_the_discovery_enumerates_untracked_files_rather_than_directories`
fails on its own premise — it asserts that this tree contains an untracked
*directory*, and it does not. The same single failure is recorded in the D12-R1
and V6-R1 handbacks. **This pass created no untracked directory**: the two
files it touched under `tools/` and `tests/` were already untracked from
C-P5.0-LAB-V6-R1, and the one path it adds — this handback — is a file in an
existing tracked directory. The test's premise was already false at the start of
this pass, and it is false for the same reason afterwards.

**Checks not run, and why.**

* **The 80-skip PostgreSQL database run was not performed.** This authorization
  permits `TEST_DATABASE_URL` unset only, so **every skip above is unverified
  and none of it is PostgreSQL evidence.**
* **No check was run on `oracle-test`.** No host action is authorized. The
  figures above are from local runners on this workstation and are not
  canonical-environment evidence; `.agents/AGENTS.md` names
  `/opt/freedom-blades/runtime/venv-web/bin/python` **on `oracle-test`**, and
  that path existing here establishes nothing about there.
* **No formatter, linter or type checker was run** — none is configured in this
  repository. That is a statement about the repository, not a check skipped.
* Interpreters: `/opt/freedom-blades/runtime/venv-web/bin/python` (3.12.3,
  pytest 9.1.1) for the evidence suite; `/opt/discord-bots/venv/bin/python` and
  `/opt/discord-bots/venv-web/bin/python` (3.12.3, pytest 8.4.2) for bot and
  web; node v24.20.0.

## 8. Generated artifacts

One covered source changed, so the artifacts were regenerated through the
**non-executing** CLI only:

```text
python -m tools.phase_5_0_evidence.execution.cli --manifest-out <scratch>/genN/manifest.json --render <scratch>/genN/plan.md
```

No `--execute`, no `--confirm-target`, no `--reviewed-digest`.

* Three consecutive generations are **byte-identical**, and the third was
  installed and compared byte for byte.
* `COVERED_SOURCES` is **44** paths, equal to the manifest's path set. All 44
  hashes recomputed from disk: **zero mismatches**.
* **Exactly one `source_digests` entry moved** —
  `tools/phase_5_0_evidence/execution/provisioner.py`. No entry was added or
  removed, and **`manifest_version` stays 13**: this pass changes a covered
  source's bytes, not what a digest covers.
* The installed plan differs from the previous one in **one line**, its digest.
* Dry run: `executable : False`; `unresolved conflicts : 3 (C-7)`; twelve
  unconfirmed facts listed, each refusing the executor before any command
  starts.

New review-input digest
`ac3ce2b7c3cc17faf2f280e6ba546c24af60ff467c60dcd2ab48fe6a0f6550fd`, replacing
`326764327034549a4667528690ad13192c9597748c39b1e9c3415dd466ed63e2`.
**Review input only. Do not pass it to `--execute`.**

## 9. Files changed

| File | Change |
|---|---|
| `tools/phase_5_0_evidence/execution/provisioner.py` | `_create` split at the `mkdirat`; new `_complete_creation`, `_record`, `_residue`; tolerant `_identity_of`; `ProvisioningRefused.partial`; five new closed classifications and `POST_CREATION_REFUSALS`; `Outcome.CREATED_IDENTITY_UNKNOWN` and `CREATING_OUTCOMES`; the `AppliedItem` invariant and `removable`; `ProvisioningRun.removable`/`unidentified`/`recoverable` and a widened `created`; `apply()` carries the partial; `rollback()` refuses unidentified residue; module docstring section; `__all__` |
| `tests/phase_5_0_evidence/test_v6_provisioning.py` | new section 9 — the `failing` injector and **15 tests**; imports. The 45 existing tests are unchanged |
| `docs/review/phase-5-0-reserved-laboratory-runner-contract-r6.md` | dated V6-R2 amendment note; §7.1's applier row and its new *"What a partial application returns"* rule; §9.2 row **87** |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json`, `…-concrete-plan.md` | regenerated (§8) |
| `docs/operations/disposable-test-server.md` | dated restriction banner |
| `docs/project-management/raid-register.md` | dated entry |
| `docs/review/Handover information` | dated entry at the top |
| this handback | new |

**Not changed, deliberately:** `provisioning.py` — no reviewed item definition,
owner, group, mode, creation, persistence, verification or rollback field moves,
and V11's rollback text already required the recorded identity, so an
unidentified residue refusing is that text applied rather than a new policy.
`review_manifest.py` — the covered set and the manifest version are unchanged.
`docs/implementation-plan.md` §20 — the action pointer is the maintainer's.

## 10. Rollback of this repository change

Revert the two source files to their C-P5.0-LAB-V6-R1 state, revert the three
amended passages in r6, regenerate the two artifacts through the non-executing
CLI, and the digest returns to
`326764327034549a4667528690ad13192c9597748c39b1e9c3415dd466ed63e2`. Nothing
outside this repository is affected, because nothing outside it was touched.

## 11. Scope, and what is still open

This pass fixed **PR-20260916-LAB-V6R1-1 only**. Not decided, not worked around,
and still maintainer stop conditions: **LAB-V6-1** (`/opt/freedom-blades` owned
by `ubuntu`, defeating V11's root-only entry claim), **LAB-V6-2**
(`/var/lib/freedom-blades` absent with no provisioning item) and **LAB-V6-3**
(r6's `R` conflicting with the approved target root, and `EVIDENCE_ROLE` with no
production registration). **V11 must remain unapplied while they are open.**

No implicit parent was defined, no mode widened, `R` was not relocated, no
production evidence role was registered, and LAB-X1's execution route was not
chosen. V11's reviewed definition, the separation of actual provisioning
identity from declared owner, V7's exclusion, the V7-absent fail-closed state,
the read-only verification boundary and the pre-`rmdir` emptiness check are all
preserved.

`plan.is_executable` is **False** and `reservation.REAL_EXECUTION_REFUSAL` is
unconditional. V6 remains performed but **not closed**; **I3 unconfirmed**; V7
excluded; V8 and V10 unperformed; C-7, EH-R16-1, LAB-R6, LAB-X1, LAB-V6-1,
LAB-V6-2, LAB-V6-3, P5.0-R5 and OD-62 **Open**; Package 5.0 **not ready**.

## 12. Proposed reviewer focus

1. Whether the six failure points are genuinely all of them — that no call in
   `_complete_creation` can still raise an unclassified error.
2. Whether refusing to re-resolve the name after a failed open is the right
   trade, against recording an identity the guard could not trust.
3. Whether `applied` including the refusing item is the right shape, or whether
   a separate residual collection would read better to an operator.
4. Whether refusing the whole reversal on one unidentified residue is
   proportionate, or whether reversing the identified objects first is safer.
5. Whether `Outcome`'s third value is correctly excluded from every place
   `CREATED` is treated as removable.

**Next action: independent Codex technical and security re-review.**
