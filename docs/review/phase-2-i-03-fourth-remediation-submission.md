# Phase 2 I-03 — fourth remediation submission and Phase 2 gate-readiness audit

Implementer: Claude, implementing agent and working Technical Lead
Date: 2026-08-05
Repository: `/opt/discord-bots/freedom-bot`
Branch: `docs/platform-plan`, `HEAD` at `3abb5ba`, package in the **uncommitted**
working tree (baseline before it: `c8a3da9`)
Remediates:
[`phase-2-i-03-third-remediation-codex-re-review.md`](phase-2-i-03-third-remediation-codex-re-review.md)
finding **I-3R-1**

**This is an implementer's submission, not an approval.** No finding is closed on
my authority, no gate is claimed, and Phase 2 is **not** finished. Peter Duscha
is the Acceptance Authority and records the gate decision after the required
independent recommendations and supervised evidence exist.

Two things are in this document and they are deliberately separate:

1. **§§1–3, the remediation of I-3R-1** — one Important evidence-accuracy finding
   about what the artifact store guarantees when temporary cleanup fails; and
2. **§§4–7, a gate-readiness audit of the whole Phase 2 handoff** — every Phase 2
   acceptance criterion, mandatory test, required operational evidence item and
   §13.3 evidence requirement, each with exactly one current disposition.

The second exists because the first is a symptom. Three re-reviews in a row found
a correction that was real and stopped one level short of the rule, and the
fourth found the *evidence* claiming more than the implementation did. So the
audit assumes the same failure mode recurred in the evidence and looks for it.
**§4.9 states plainly that Phase 2 is not gate-ready**, and §5 is the
traceability table that says why, item by item.

---

## 1. I-3R-1 — the handoff overstated temporary cleanup

### 1.1 The finding, and that it is about the record rather than the code

> The third-remediation request says "no temporary survives success or an
> ordinary failure" because `_discard` runs on each path. That is not what the
> implementation guarantees. `_discard` intentionally swallows `OSError`, and
> `test_a_failing_cleanup_leaves_the_published_artifact_alone` proves that a
> successful store may leave one private `.incoming-*` hard link behind.

The reviewer is right, and the shape of the error is worth stating exactly,
because it is the same shape as the previous three rounds. **Running a cleanup
function is not evidence that the cleanup happened.** The row reasoned from
control flow — `_discard` is called on the success path and on both failure paths
— to a durable-state guarantee, over a function whose documented and deliberate
behaviour is to swallow the error. The implementation never claimed it. The
`_discard` docstring said "best effort". The operations document said "best
effort". The regression test asserts the opposite of the row and had done since
the third remediation. Only the review evidence was wrong, and it was wrong in a
structural-guarantee table, which is the part of a handoff a reader is most
entitled to trust.

**Why it mattered rather than being a wording slip.** The false row was in a
table headed "the structural guarantee now provided". A storage-capacity or
hygiene assessment reading it would conclude that the artifact root contains
exactly the artifacts, that leftover files indicate a fault, and that no
operator procedure is needed for them. All three are wrong, and the third is why
this remediation adds an operator procedure rather than only editing sentences.

**No code change was required and the mechanism was not touched.** The
`os.link` publication design and the test-only bounded ancestor walk were both
accepted by the third re-review, and neither was reopened: no contradictory
evidence was found, and the prompt for this round was explicit that finding an
excuse to change publication so the old sentence became true would be the wrong
move. It would also be the wrong engineering. Making cleanup failure fail the
submission would turn a correctly published artifact into a refusal over an
`unlink`, which is the exact failure direction I-2 exists to prevent.

### 1.2 The contract, stated once, as it now reads everywhere

| # | Statement | Where it is enforced |
|---|---|---|
| 1 | Publication never removes or overwrites the final checksum entry | `os.link` creates the entry or fails `EEXIST`; there is no mode in which it removes what is there |
| 2 | Cleanup can only ever name an internally generated `.incoming-*` entry | `_discard` returns before the `unlink` unless the name carries the prefix, and every caller passes a name this process generated |
| 3 | Temporary cleanup is **best effort** | `_discard` swallows `OSError` and reports nothing; `store()` never learns whether the removal happened |
| 4 | A failure to remove a temporary does not invalidate or delete a correctly published artifact | by the time `_discard` runs the checksum entry exists and has been proved; the submission still succeeds |
| 5 | A failed cleanup **may leave a private, unservable hard link consuming storage** | `test_a_failing_cleanup_leaves_the_published_artifact_alone` asserts exactly one surviving `.incoming-*` file after a **successful** store |
| 6 | Operator hygiene detects and handles such leftovers under a read-only procedure | operations §5.6, "Temporary files left by a failed cleanup"; proved against synthetic files by three tests |
| 7 | No statement promises zero surviving temporaries unless its preconditions exclude cleanup failure **and** a test proves them | true of exactly two assertions in the suite, both of which now say so in the test itself |

On statement 5, the precise cost, because "harmless" was the word the operations
document used and it was doing too much work: a leftover is `0600`, owned by the
service account, inside a `0700` root, and **no route resolves any name but the
checksum one**, so it cannot be served, listed or read through the application.
It consumes an inode and, once the artifact is deleted under the retention rule,
a full second copy of the bytes. It is a storage item, not a confidentiality or
correctness one.

On statement 7, the two exceptions and why they are allowed to be absolute:
`test_two_writers_of_identical_bytes_converge_on_one_artifact` and
`test_the_startup_probe_leaves_nothing_behind` both run with cleanup working,
which is the precondition, and both now state it in the test body rather than
leaving a reader to infer it.

### 1.3 Every file changed by this remediation

| File | Change | Kind |
|---|---|---|
| `adapters/artifacts/filesystem.py` | the "Publication never overwrites" section's third bullet now states the best-effort limit, the leftover it can produce, what that costs and who removes it; the `store()` comment above `_discard`/`_fsync_root` says the swallow makes the removal best effort rather than guaranteed; `_discard`'s docstring says the caller is told nothing and points at the operator procedure; `_prove_publication_refuses_to_overwrite`'s docstring carries the same limit for the startup probe | docstring/comment only — **no executable line changed** |
| `docs/operations/foundry-snapshot-submission.md` | §5.6's "Durability ordering" paragraph replaces "a cleanup failure leaves a harmless leftover" with the actual cost; **new §5.6 subsection "Temporary files left by a failed cleanup"** — read-only detection, age bound, link-count table, confirmation commands, "report, then remove deliberately"; §9 recovery gains a paragraph distinguishing a leftover temporary from an unclaimed artifact | operator-facing |
| `.env.example` | the artifact-root block gains a paragraph for whoever sizes the filesystem: leftovers can survive a **successful** store, the service never reports them, they cannot affect the published artifact, and repeated ones mean the `unlink` is failing | configuration contract |
| `tests/test_artifact_store.py` | three new tests (§1.4); the two absolute assertions gain their stated precondition; `test_a_failing_cleanup_leaves_the_published_artifact_alone` **preserved unchanged** in substance, with its comment pointing at the new group | tests |
| `docs/review/phase-2-i-03-remediation-review-request.md` | the false structural-guarantee row is **struck through and marked superseded in place**, naming I-3R-1; a corrected six-row table follows it; the "two concurrent writers → no surviving temporary" evidence row gains its precondition | review record |
| `docs/review/phase-2-i-03-remediation-submission.md` | §13.1's "`_discard` removes the temporary" bullet gains the best-effort limit and points here; the corresponding named-test row gains its precondition | review record |
| `docs/review/phase-2-i-03-package-plan.md` | **new §10 amendment**: D10 restated (the trade is a link plus a *best-effort* removal), R9 sharpened, **D11 added** (detection is an operator procedure, deliberately not an application capability), **R11 added** (leftovers accumulate unnoticed) | package plan |
| `docs/project-management/change-log.md` | **new C-7**, dated, with what is superseded, alternatives rejected, and every required field. C-6 is *not* otherwise superseded — it did not repeat the claim | controlled record |
| `docs/project-management/raid-register.md` | **R-18 added** (leftover temporaries consume storage unnoticed, Low/Low, Operations Owner); R-16's cleanup sentence points at R-18 for what a failed cleanup *can* do | controlled record |
| `docs/project-management/status.md` | the I-03 row and the narrative record the fourth remediation and this audit | controlled record |
| `docs/review/Handover information` | rewritten as the **fourth** re-review request | review record |
| `docs/review/phase-2-i-03-fourth-remediation-submission.md` | this document | review record |

**Nothing else in the working tree was touched.** No application module, no
adapter behaviour, no migration, no schema, no route, no configuration variable,
no capability.

### 1.4 Named tests

All in `tests/test_artifact_store.py`, section "operator hygiene: finding what a
failed cleanup left". They run the operations §5.6 detection rule through the
real `find`, against files the test wrote. They add nothing to the application:
there is still no listing endpoint, no deletion endpoint and no automatic
removal of an unknown entry.

**Precisely what "the documented rule" means here, because the distinction is
the same one I-3R-1 was about.** The *selection* is character for character the
documented one — `-maxdepth 1 -type f -name '.incoming-*' -mmin +60` — and that
is the part that decides what an operator deletes. Only `-printf` differs: the
document prints size, timestamp and link count for a human to read, and the
tests print name and link count so they can be compared. Which files match does
not change, and the link count the procedure's table is read from comes from the
same `%n`. **The tests do not prove the document's exact output line.**

| Test | Proves |
|---|---|
| `test_the_hygiene_rule_finds_a_leftover_a_successful_store_left` | the success-path case the false row denied: the store returns a reference, the artifact is published and correct, one temporary survives, and the documented rule finds it and reports **two** links — which is what tells an operator that removing it frees an inode and no bytes |
| `test_the_hygiene_rule_reports_one_link_for_an_unpublished_leftover` | the failure-path case: publication refused and cleanup then failed, so the surviving temporary is the only name for those bytes and the rule reports **one** link. Nothing was published |
| `test_the_hygiene_rule_does_not_match_an_artifact_or_a_submission_in_flight` | the two false positives that matter, because the operator's next step after the rule is deletion: an aged published artifact is never matched, and a `.incoming-*` file younger than the age bound is not matched either — removing one would break a live upload |
| `test_a_failing_cleanup_leaves_the_published_artifact_alone` | **preserved.** The finding's own evidence: a successful store with the `unlink` refused leaves exactly one `.incoming-*` file and a correct published artifact |

`tests/test_artifact_store.py` is now **94 tests, was 91**. The three are
synthetic, read-only against the filesystem, and skip with a stated reason if
`find` is absent (it is present here, and the suite reported **no skips**).

### 1.5 Operational effect, recovery behaviour, and residual risk

**Operational effect.** Operators gain a documented, read-only way to find
leftover temporaries and a rule for reading the link count before removing one.
Whoever sizes the artifact filesystem is told in `.env.example` that leftovers
are possible after a *successful* store. Nothing is automated, no new
configuration variable exists, and no capability was added to the service.

**Recovery behaviour.** Unchanged, and one clarification added. A leftover
temporary needs no recovery: it is private, unservable, and cannot affect the
published artifact. Operations §9 now says that explicitly so an operator does
not treat it as the unclaimed-artifact case or as the unexpected-entry case,
which have different and more serious procedures. What §9 now also says is when
it *does* deserve investigation: repeatedly, because an `unlink` only fails when
the root's mode or ownership has drifted or the filesystem is full or read-only
— all conditions the store refuses on its other paths, which makes a leftover a
leading indicator rather than a silent cost.

**Residual risk, registered as R-18 and not closed.** Nothing counts, alerts on
or removes leftovers. How often an operator should run the procedure is an
operations decision that **has not been taken**, and it belongs with the
retention decision D-c, which is Peter's. Adding automatic cleanup was
considered and rejected: it would broaden the service's filesystem authority
beyond "create a temporary, and unlink one created in the attempt that is
running", and that narrowness is precisely what makes a cleanup failure
structurally unable to delete an artifact.

**Security effect: none claimed, and none requested.** No security-relevant code
or contract changed. Publication, root anchoring, the credential boundary
(S-B-1) and the CORS policy (S-I-1) are untouched, and the third security
re-review had already described the best-effort cleanup correctly — it is the
implementation re-review's evidence table that was wrong. **A new security
re-review is therefore not requested.** If the reviewer disagrees that a
documented operator deletion procedure is security-neutral, that is worth saying
and I will request one.

---

## 2. What I looked for beyond the reported sentence

The finding named one sentence. Per §2 of the fourth-remediation prompt I audited
every place the same absolute claim or an equivalent could appear.

| Searched | Result |
|---|---|
| `docs/review/phase-2-i-03-remediation-review-request.md` | **one occurrence** (the reported row) plus one weaker equivalent in the evidence list. Both corrected |
| `docs/review/phase-2-i-03-remediation-submission.md` | **one** equivalent in the named-test table, plus a "`_discard` removes the temporary" bullet with no qualifier. Both corrected |
| `docs/review/Handover information` | **one** equivalent ("two writers … with no surviving temporary"). The file is rewritten as the fourth request and the claim is stated correctly there |
| `docs/review/phase-2-i-03-package-plan.md` | **none.** D10 and R9 were accurate but incomplete; both amended in §10 |
| `docs/operations/foundry-snapshot-submission.md` | **none false.** §5.6 already said "best effort"; "a harmless leftover" understated the cost and is corrected, and the missing operator procedure is added |
| `.env.example` | **none.** It said nothing about cleanup at all, which for a file whose job is to tell an operator what the artifact root needs is its own gap. Corrected |
| `docs/project-management/change-log.md`, `status.md`, `raid-register.md` | **none false.** C-6 and R-16 describe the structural guard, which is true. R-16 sharpened, R-18 added |
| module and application docstrings | `adapters/artifacts/filesystem.py` only. `_discard` and operations were right; the module docstring's publication section and the `store()` comment implied completion. Corrected. `application/artifacts.py` makes no cleanup claim |
| tests whose names, comments or assertions describe cleanup guarantees | four. `test_a_failing_cleanup_leaves_the_published_artifact_alone` and `test_cleanup_can_only_ever_remove_a_temporary` were already correct; `test_two_writers_of_identical_bytes_converge_on_one_artifact` and `test_the_startup_probe_leaves_nothing_behind` asserted absolutes whose precondition was unstated, and now state it |

Command used, for reproduction:

```bash
grep -rniE "no temporary survives|no surviving temporar|zero surviving|leaves nothing behind|harmless leftover" \
  docs/ .env.example adapters/ application/ tests/ tools/ foundry-module/
```

---

## 3. What I did **not** change, and why

- **the `os.link` publication design.** Accepted by both third re-reviews. Not
  reopened; no contradictory evidence found;
- **the test-only bounded ancestor walk.** Accepted as an implementation choice
  not requiring escalation. Not reopened;
- **`_discard`'s swallow.** It is the correct behaviour. Raising would fail a
  submission whose artifact is published and correct;
- **any list or delete capability in the service.** Deliberately absent (D11);
- **any automatic deletion of unknown entries.** Deliberately absent. The
  operations procedures for unclaimed artifacts and for unexpected entries both
  begin with "do not delete";
- **the multi-process publication experiment.** The deterministic two-store test
  is **not** relabelled as a process test. It remains residual evidence (R-16);
- **anything requiring Peter.** No credential was issued, no Foundry module was
  installed, no Foundry world, LevelDB, compendium pack or player data was read,
  no real Actor export was used, and nothing was committed or pushed.

---

## 4. Gate-readiness: the states, stated separately

### 4.1 Implementation state

**Complete for the I-03 package as scoped**, in the uncommitted working tree.
The Foundry v14 module, the submission endpoint, the restricted artifact store,
the Council preview contract and migration `0004` are implemented; the four
Phase 2 remediation packages R1–R4 are implemented. Nothing is committed and
nothing is pushed. This is a statement about code existing and passing its
tests, and it is **not** a statement that the work is accepted.

### 4.2 Independent-review state

| Round | Result | Status |
|---|---|---|
| 1 (2026-08-04) | B-1, S-B-1, S-B-2 Blocking; I-1, I-2, S-I-1 | superseded by later rounds |
| 2 (2026-08-04) | I-1 and S-B-2 **not actually fixed** | superseded |
| 3 (2026-08-04) | root anchoring materially correct; **publication Blocking**, I-1 again, test evidence | remediated; re-reviewed in round 4 |
| 4 (2026-08-05) | publication, I-1, I-2, root anchoring, S-B-1, S-I-1 **all found resolved or preserved**; one Important evidence finding, **I-3R-1** | I-3R-1 remediated by this document; **awaiting a narrow independent re-review** |

**No finding is closed.** The fourth-round reports recommend closure of the
publication finding; a recommendation is not a closure, and Peter records it.
The narrow re-review requested in §8 is required before this package can be
considered independently reviewed.

### 4.3 Automated evidence — this run, 2026-08-05

| Check | Command | Result |
|---|---|---|
| Foundry module | `(cd foundry-module && node --test "tests/*.test.mjs")` | **81 pass, 0 fail, 0 skipped** |
| Narrow Python suites | the eight-file `pytest -q` in §6 | **376 passed** (was 373; +3 hygiene tests) |
| Full Python suite | `pytest -q -rs` | **1944 passed, 1 warning, no skips** (was 1941) |
| Byte compilation | `python -m compileall -q application adapters domain tools tests migrations` | exit 0 |
| Migration consistency | `alembic check` | `No new upgrade operations detected.` |
| Whitespace/conflict | `git diff --check` | exit 0 |
| JavaScript syntax | `node --check` over 16 files | all clean |
| Formatter, linter, type checker | — | **not configured** in this repository and not installed in `venv`. None was installed to manufacture a check |

The single warning is the pre-existing `audioop` deprecation from the vendored
`discord` library and is unrelated to this package.

### 4.4 Disposable operational evidence — this run, 2026-08-05

Four rehearsals were run in the disposable environment (`freedom_test`, local
Unix-domain socket, synthetic fixtures only). **No production Discord, Sheets,
Foundry, PostgreSQL or external service was contacted, no real credential was
issued, and no real Actor data was used.** §7 has the exact commands and output.

| Rehearsal | Result | Cleanup |
|---|---|---|
| upgrade → downgrade-to-base → upgrade | **passed.** 13 tables before, 1 (`alembic_version`) at base, 13 after; a 205-line column/constraint/index digest hashed **identically** before and after (`5b472c49…65c6`) | database left at `0004 (head)` |
| backup / restore / rerun | **passed.** `pg_dump -Fc` of a *populated* database, checksum recorded, `public` schema dropped, restored, inventory compared; identity and audit rows byte-identical after the restore; the importer rerun created nothing | dumps deleted; database returned to head with every table empty |
| direct restricted-runtime-role denial | **passed**, as part of the automated suite against the real `freedom_runtime_test` role over `SET ROLE` | transactional; `RESET ROLE` in fixture teardown |
| operations §5.8 server-half smoke test | **passed.** `201` then `200 duplicate:true` with the same `snapshot_id`; one `0600` artifact named for its own SHA-256; **no `.incoming-*` leftover**; preflight `204` with an exact `Access-Control-Allow-Origin` for the allowed origin and `403 origin_not_allowed` with no permission header for another; `401` unauthenticated; the request log carried status codes only | rehearsal server stopped, tables truncated, work directory removed |

**What these are not.** None of them is a browser, none involves Foundry, and
none uses a real credential or a real export. They are the checks that *can* be
made without Peter, run for real rather than argued from construction.

### 4.5 Supervised evidence still pending — none of it optional

| # | Evidence | Accountable | Why automation is not a substitute |
|---|---|---|---|
| S1 | operations §8.1 — the credential is absent from the state a live **second** Foundry client is vended | Peter Duscha (Data/Security Owner) | The claim is about what Foundry delivers to another user's browser. Source analysis established the mechanism; only a second client in a second browser profile observes the delivery |
| S2 | operations §8.2 — a real browser origin passing the preflight, **and failing when the origin is removed** | Peter Duscha (Operations Owner) | `curl` does not enforce CORS. B-1 existed precisely because a server that answers correctly was mistaken for a workflow that works. The negative case is what proves the allowlist is load-bearing |
| S3 | Rehearsal A (operations §6) — inactive-folder transport rehearsal | Peter Duscha | Needs a running Foundry client and the module installed. Neither has ever happened here, by instruction |
| S4 | Rehearsal B (operations §7) — active-folder Phase 2 gate rehearsal, with the **signed Data Owner attestation** and zero unexplained identity discrepancies | Peter Duscha (Data Owner) | This is the Phase 2 acceptance criterion. It is an observation about the real world's Actors, and no synthetic fixture can stand in. **Never simulate it with real Actor data, and never commit an artifact** |
| S5 | maintainer review of field profile `2026-08-03.1` | Peter Duscha | Phase 2 requires the profile to be "reviewed by a maintainer". Tests prove it is exhaustive, versioned and fails closed on an unknown path; **no record of a maintainer review of this version exists**, and a test cannot supply one |
| S6 | cross-account artifact-root experiment | Peter Duscha | Requires a second POSIX account and privilege. **Not run, and not to be run** unless Peter supplies an approved disposable second account and supervises it (R-15) |
| S7 | multi-process publication experiment | Peter Duscha / Technical Lead | Residual evidence, not a gate condition (R-16). The deterministic two-store test enters the exact window and is **not** relabelled as a process test |

§8 is a copyable run sheet for S1 and S2, which are the two that block least and
cost least.

### 4.6 Owner recommendations still required

| Role | Required for | Status |
|---|---|---|
| Data Owner | the §7 reconciliation attestation, and acceptance of field profile `2026-08-03.1` | **not given** |
| Security Owner | acceptance of the S-B-1/S-B-2/S-I-1 dispositions, informed by the third security re-review and by S1/S2 | **not given** |
| Operations Owner | acceptance of the deployment prerequisites (R-17), the storage hygiene cadence (R-18) and the recovery procedures | **not given** |
| Product Owner | the C-3 … C-7 change-log entries | **not given** |
| Technical Lead | — | the implementing agent holds this role for the package and **cannot approve its own recommendation** |

### 4.7 Acceptance Authority decision

**Not recorded, and not requested by this document.** Three decisions remain
reserved to Peter and are unchanged: **D-a** (short-lived token exchange),
**D-b** (repair policy), **D-c** (retention of database-unclaimed artifacts —
which now also covers how often leftover-temporary hygiene should run).

### 4.8 What construction proves, and what it does not

The phrase to avoid is "remediated by construction", used as though it were a
disposition. It is not one. Construction and tests support a *recommendation*;
an acceptance criterion that requires an observation stays pending until it is
observed. Concretely, in this package: B-1 and S-B-1 are implemented, tested and
argued from Foundry's own source, and they are **still** listed as S1 and S2
above, because what they claim is about a live client and a live browser.

### 4.9 Is Phase 2 gate-ready?

**No.** Phase 2 is **not** gate-ready, and no formulation such as "complete
except for" applies while mandatory evidence is missing.

What is missing is not paperwork:

- the **signed Data Owner attestation from a supervised rehearsal with the real
  snapshot** is a named Phase 2 acceptance criterion and a named required
  operational evidence item. It has not been performed (S4);
- **neither rehearsal has been run at all** (S3, S4). The Foundry module has
  never been installed;
- **two supervised security observations are outstanding** (S1, S2), each
  attached to a finding that was Blocking when it was found;
- **maintainer review of the field profile version** is required by the
  acceptance criteria and is unrecorded (S5);
- **independent review closure of every blocking finding** is itself a required
  operational evidence item. No finding is closed, and I-3R-1 awaits a re-review;
- **every owner recommendation is outstanding** (§4.6).

What *is* ready is narrower and worth stating precisely, because it is the thing
this turn moved: the implementation and its automated and disposable-environment
evidence are, to the best of my knowledge, complete, reproducible and honestly
described, and the package is ready for a **narrow independent re-review of
I-3R-1 and of the truthfulness of this document's traceability claims**.

---

## 5. Traceability — every criterion, one disposition each

Dispositions are exactly one of: `automated — passed`, `disposable rehearsal —
passed`, `supervised — pending`, `not applicable`, `failed/blocked`. Aggregate
test counts are **not** used as a substitute for a named test.

### 5.1 Phase 2 acceptance criteria (plan §12 Phase 2, "Acceptance")

| # | Criterion | Disposition | Evidence |
|---|---|---|---|
| A1 | every §6.5 invariant implemented and enforced below the web/Discord UI | `automated — passed` | `test_snapshot_import_service.py::test_an_audit_write_failure_rolls_back_the_import`, `::test_each_injected_failure_point_leaves_no_partial_state`, `::test_authorization_is_rechecked_at_apply_not_carried_from_the_preview`; `test_snapshot_database.py::test_an_applied_import_commits_character_mapping_record_and_audit` |
| A2a | the field profile is exhaustive, versioned, and contains no unclassified supported field | `automated — passed` | `test_field_profile.py::test_the_profile_is_versioned`, `::test_every_snapshot_path_has_exactly_one_mode`, `::test_the_fixture_actor_has_no_unclassified_path`, `::test_a_new_supported_schema_field_fails_closed`; `test_field_ownership_document.py` keeps document and module in step |
| A2b | …**reviewed by a maintainer** | `supervised — pending` (**S5**) | No maintainer review of profile `2026-08-03.1` is recorded anywhere in `docs/project-management/`. A test cannot supply one. Next action: Peter reviews the profile and the record carries the date |
| A3 | no Phase 2 process requires network or live Foundry access | `automated — passed` | `test_snapshot_import_service.py::test_the_service_needs_no_network_or_live_foundry`; module test "no Foundry mutation API is invoked, and no forbidden source is read" |
| A4 | the importer verifies checksum, triggering authority, world, Foundry/system versions, exporter schema and folder identity before proposing changes | `automated — passed` | `test_snapshot_artifact.py::test_verify_refuses_bytes_that_no_longer_hash_to_the_recorded_checksum`; `test_snapshot_parser.py::test_the_wrong_world_is_refused_and_names_both_values`, `::test_an_unsupported_exporter_schema_version_fails_closed`, `::test_an_unselected_folder_cannot_be_imported_from`; `test_snapshot_import_service.py::test_a_wrong_deployment_is_refused_with_no_transaction_opened`, `::test_one_council_member_is_sufficient` |
| A5 | altered bytes are a different snapshot and cannot inherit another's identity, preview or audit record | `automated — passed` | `test_snapshot_artifact.py::test_one_changed_byte_is_a_different_snapshot`; `test_snapshot_import_service.py::test_a_tampered_artifact_cannot_inherit_another_snapshot_identity`; `test_snapshot_database.py::test_a_tampered_artifact_is_a_different_snapshot_in_the_database` |
| A6a | the mapping rule — every Actor maps, is a create-candidate, or is explicitly unresolved | `automated — passed` | `test_snapshot_reconciliation.py::test_every_actor_is_mapped_a_create_candidate_or_explicitly_unresolved`, `::test_a_dangling_mapping_blocks_rather_than_creating_a_character` |
| A6b | …applied to the **real** `Characters (active)` folder | `supervised — pending` (**S4**) | Rehearsal B. Synthetic fixtures cannot establish a fact about the deployment's Actors |
| A7 | duplicate external IDs, malformed fields, unsupported versions, missing Actors and ambiguous mappings are reported | `automated — passed` | `test_snapshot_parser.py::test_a_duplicate_actor_id_is_ambiguous_and_refused`, `::test_a_malformed_actor_id_is_refused`; `test_snapshot_reconciliation.py::test_an_absent_actor_warns_and_deletes_nothing`, `::test_an_ambiguous_legacy_candidate_lookup_fails_closed_and_names_every_candidate` |
| A8 | repeated imports do not create duplicates | `automated — passed` | `test_snapshot_import_service.py::test_reapplying_the_same_input_under_a_new_request_key_is_a_typed_duplicate`; `test_snapshot_database.py::test_reapplying_the_same_checksum_is_a_no_op_against_postgresql`, `::test_the_same_input_cannot_be_applied_twice`. Also observed in the §7.2 rehearsal |
| A9 | import failure cannot partially commit | `automated — passed` | `test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state`, `::test_a_record_write_failure_leaves_no_partial_state`, `::test_an_audit_write_failure_rolls_back_the_import` |
| A10 | stale or concurrent import previews apply nothing | `automated — passed` | `test_snapshot_import_service.py::test_a_changed_snapshot_makes_the_preview_stale`, `::test_a_changed_database_version_makes_the_preview_stale`, `::test_a_changed_profile_version_makes_the_preview_stale`, `::test_a_stale_preview_records_one_refused_attempt_and_no_success` |
| A11 | preview and dry-run persist no character or mapping change | `automated — passed` | `test_snapshot_reconciliation.py::test_a_preview_persists_no_character_or_mapping`, `::test_a_preview_rolls_back_rather_than_committing`; `test_snapshot_database.py::test_a_preview_against_postgresql_writes_nothing`; `test_import_cli.py::test_the_default_run_is_a_dry_run`. Also observed in §7.2 |
| A12 | database-owned disagreements reported only where an accepted typed value exists; otherwise `legacy_authority_deferred` naming the owning package, with no equality comparison | `automated — passed` | `test_snapshot_reconciliation.py::test_a_legacy_field_reports_deferred_authority_and_its_owning_package`, `::test_a_legacy_field_is_never_reported_as_matching_or_differing`, `::test_a_deferred_field_says_whether_foundry_holds_a_value_but_not_what`; `test_field_profile.py::test_a_deferred_field_cannot_be_compared`. Observed live in §7.2: 24 `legacy_authority_deferred` warnings, 0 errors |
| A13 | snapshot-only fields readable for calculations without becoming a second managed representation | `automated — passed` | `test_snapshot_roll_inputs.py::test_a_projection_exposes_no_way_to_write_a_snapshot_only_field`; `test_field_profile.py::test_snapshot_only_inputs_cannot_be_selected_for_database_write`; `test_rejected_scope_absent.py::test_an_import_writes_no_character_game_state_field` |
| A14 | calculations identify the snapshot and profile versions they used and refuse missing required inputs | `automated — passed` | `test_snapshot_roll_inputs.py::test_a_roll_input_carries_the_snapshot_and_profile_it_came_from`, `::test_a_missing_required_input_refuses_rather_than_defaulting`, `::test_a_skill_the_snapshot_does_not_record_is_not_no_proficiency` |
| A15 | an Actor missing from a later snapshot stays intact and mapped until a Council correction | `automated — passed` | `test_snapshot_reconciliation.py::test_an_absent_actor_warns_and_deletes_nothing`; `test_rejected_scope_absent.py::test_a_second_import_of_a_changed_actor_still_writes_no_field` |
| A16 | every applied character and mapping traces to the snapshot checksum and triggering actor | `automated — passed` | `test_snapshot_import_service.py::test_every_applied_character_and_mapping_traces_to_the_snapshot_and_actor`, `::test_the_success_audit_names_the_snapshot_the_actor_and_the_authority`; `test_snapshot_database.py::test_the_stored_mapping_traces_to_the_snapshot_and_the_folder` |
| A17 | the restricted runtime role cannot update, delete or truncate audit and import-history records | `automated — passed` | `test_runtime_grants_live.py::test_set_role_denies_update_on_every_append_only_table`, `::test_set_role_denies_delete_on_every_append_only_table`, `::test_set_role_denies_truncate_on_every_append_only_table`, `::test_the_denials_still_hold_as_the_role_after_public_drift` — real role, real PostgreSQL |
| A18 | rollback/recovery and snapshot-retention procedures are documented | `failed/blocked` | The **procedures** are documented and exercised (`docs/operations/database-development.md`, `foundry-snapshot-submission.md` §9, `foundry-snapshot-import.md` §7; §7.1–7.2 exercised them). The **retention policy** is not settled: **D-c** — how long a database-unclaimed artifact is kept, and now the leftover-temporary hygiene cadence — is explicitly reserved to Peter and open. Next action: Peter records D-c |
| A19 | a maintainer-supervised rehearsal with the real immutable snapshot produces a reviewed reconciliation report without committing the artifact | `supervised — pending` (**S4**) | Operations §7. Not performed. **Never simulate with real Actor data** |
| A20 | real data is not copied into tests | `automated — passed` | `test_fixtures.py`; `test_exporter_contract.py::test_the_fixture_ids_match_the_javascript_fixture`. Confirmed independently by the §9 diff review: no artifact, dump, export or Actor value in the package |

### 5.2 Mandatory Phase 2 tests (plan §12 Phase 2)

Every one is `automated — passed` in this run. Named, not counted.

| # | Mandatory scenario | Named test |
|---|---|---|
| M1 | valid synthetic snapshot preview and apply creating only provenance, identity and mappings | `test_snapshot_import_service.py::test_a_clean_import_creates_a_character_a_mapping_and_a_record`, `::test_an_imported_character_starts_with_identity_and_nothing_else` |
| M2 | checksum mismatch after any byte changes | `test_snapshot_artifact.py::test_one_changed_byte_is_a_different_snapshot` |
| M3 | oversized, excessively nested, unknown-shape and path-bearing input refused before a transaction | `test_snapshot_artifact.py::test_an_oversized_artifact_is_refused_without_being_parsed`, `::test_excessive_nesting_is_refused_by_scanning_not_by_parsing`, `::test_path_bearing_and_unsafe_names_are_refused_not_sanitised`; `test_snapshot_parser.py::test_an_unknown_top_level_key_is_refused_not_ignored` |
| M4 | denial for an ordinary member, acceptance for one Council member, refusal after revocation | `test_snapshot_import_service.py::test_an_ordinary_member_is_denied`, `::test_one_council_member_is_sufficient`, `::test_authorization_is_rechecked_at_apply_not_carried_from_the_preview` |
| M5 | wrong world, unsupported Foundry/system version, wrong folder, unsupported exporter schema | `test_snapshot_parser.py::test_the_wrong_world_is_refused_and_names_both_values`, `::test_every_deployment_difference_is_named_individually`, `::test_a_selection_naming_an_absent_folder_is_refused`, `::test_an_unsupported_exporter_schema_version_fails_closed` |
| M6 | malformed Actor data, duplicate external ID, duplicate display name, missing and ambiguous mapping | `test_snapshot_parser.py::test_a_malformed_actor_id_is_refused`, `::test_a_duplicate_actor_id_is_ambiguous_and_refused`; `test_snapshot_reconciliation.py::test_two_actors_sharing_a_display_name_are_two_create_candidates`, `::test_an_ambiguous_legacy_candidate_lookup_fails_closed_and_names_every_candidate` |
| M7 | Actor rename under the same external ID; Actor absent from a later snapshot | `test_snapshot_reconciliation.py::test_a_renamed_actor_under_a_stable_id_stays_the_same_character`, `::test_a_foundry_rename_leaves_the_character_mapped_and_unmodified`, `::test_an_absent_actor_warns_and_deletes_nothing` |
| M8 | repeated preview and repeated apply of the same checksum | `test_snapshot_database.py::test_reapplying_the_same_checksum_is_a_no_op_against_postgresql`; `test_snapshot_import_service.py::test_repeating_the_same_request_returns_the_original_result` |
| M9 | stale preview after a database edit, profile change, folder change or snapshot change, each committing nothing | `test_snapshot_import_service.py::test_a_changed_database_version_makes_the_preview_stale`, `::test_a_changed_profile_version_makes_the_preview_stale`, `::test_an_administrator_folder_change_between_preview_and_apply_is_stale`, `::test_a_changed_snapshot_makes_the_preview_stale` |
| M10 | two concurrent applies of the same or overlapping snapshot cannot duplicate anything | `test_snapshot_database.py::test_two_concurrent_applies_of_the_same_input_produce_one_effect`, `::test_two_concurrent_applies_of_the_same_key_produce_one_effect` — real PostgreSQL, real concurrent sessions |
| M11 | an Actor missing from a later snapshot warns without deletion, deactivation or unmapping | `test_snapshot_reconciliation.py::test_an_absent_actor_warns_and_deletes_nothing` |
| M12 | migrated fields warn on mismatch and not on match; legacy fields produce `legacy_authority_deferred` naming their package and are never reported as matching or differing | `test_snapshot_reconciliation.py::test_a_mapped_actor_that_agrees_produces_no_warning`, `::test_a_legacy_field_is_never_reported_as_matching_or_differing`, `::test_the_deferred_warning_names_the_owning_package` |
| M13 | no Phase 2 API, service or repository can persist a Sheet-era field or copy a Foundry comparison value into managed state | `test_rejected_scope_absent.py::test_an_import_writes_no_character_game_state_field`, `::test_the_profile_offers_no_field_that_a_snapshot_may_write`, `::test_no_service_api_accepts_a_field_selection` |
| M14 | Council and Platform Administrators can read and search import audit records while update and delete are denied | `test_runtime_grants_live.py::test_set_role_permits_the_allowed_operations` with `::test_set_role_denies_update_on_every_append_only_table` and `::test_set_role_denies_delete_on_every_append_only_table` |
| M15 | snapshot-only proficiency and stat inputs reach roll calculations without editable database fields, and results record provenance | `test_snapshot_roll_inputs.py::test_every_declared_roll_input_is_reachable_from_the_projection`, `::test_provenance_renders_as_facts_a_result_can_record`, `::test_a_projection_exposes_no_way_to_write_a_snapshot_only_field` |
| M16 | a missing, malformed or unsupported required snapshot value produces the defined typed refusal, not a default | `test_snapshot_roll_inputs.py::test_a_missing_required_input_refuses_rather_than_defaulting`, `::test_an_optional_input_answers_none_rather_than_a_substituted_value` |
| M17 | every supported path and field has exactly one classification, and an unknown new path fails closed | `test_field_profile.py::test_every_snapshot_path_has_exactly_one_mode`, `::test_a_path_cannot_be_classified_twice`, `::test_a_new_supported_schema_field_fails_closed`, `::test_an_unknown_path_classifies_as_nothing_at_all` |
| M18 | the resulting dataset contains no generic character-state, balance or transaction rows and no second editable copy of a legacy field | `test_rejected_scope_absent.py::test_the_migrated_schema_is_exactly_the_retained_set`, `::test_no_snapshot_record_type_carries_a_transaction`, `::test_the_migrated_schema_contains_no_rejected_table` |
| M19 | parser, constraint and injected mid-import failure each leave state unchanged, write no success audit, and record at most one safe attempted/refused event | `test_snapshot_import_service.py::test_each_injected_failure_point_leaves_no_partial_state`, `::test_a_stale_preview_records_one_refused_attempt_and_no_success`, `::test_a_refusal_audit_carries_no_traceback_or_artifact_content` |
| M20 | injected audit-write failure rolls back the corresponding import | `test_snapshot_import_service.py::test_an_audit_write_failure_rolls_back_the_import` |
| M21 | direct runtime-role `UPDATE`, `DELETE`, `TRUNCATE` against audit and history tables rejected by PostgreSQL | `test_runtime_grants_live.py` (three denial tests) and `test_snapshot_database.py::test_updating_an_append_only_table_is_rejected_by_the_database`, `::test_deleting_from_an_append_only_table_is_rejected_by_the_database`, `::test_the_trigger_applies_to_the_schema_owner_too` |
| M22 | constraints preventing two records claiming the same world/Actor identity, against PostgreSQL | `test_snapshot_database.py::test_a_world_actor_pair_can_only_be_mapped_once`, `::test_a_character_has_one_mapping_per_world`; `test_database_postgresql.py::test_duplicate_foundry_actor_mapping_is_rejected` |

### 5.3 Required operational evidence before the gate (plan §12 Phase 2)

| # | Required | Disposition | Detail |
|---|---|---|---|
| O1 | a **signed reconciliation report** from a maintainer-supervised preview of the real export, every Actor accounted for, zero unexplained identity discrepancy | `supervised — pending` (**S4**) | Operations §7; attestation format in plan §12 Phase 2. Not performed, and the module has never been installed |
| O2 | an **upgrade/downgrade/upgrade migration rehearsal** against a disposable PostgreSQL database | `disposable rehearsal — passed` | §7.1. `freedom_test`, local socket. 13 tables → base → 13 tables; a 205-line schema digest identical before and after (`5b472c49…65c6`); left at `0004 (head)` |
| O3 | a **backup and restore rehearsal** proving the pre-import state can be restored and the importer rerun without duplicate identity or audit effects | `disposable rehearsal — passed`, with one stated limitation | §7.2. Populated database dumped, schema dropped, restored; identity and audit rows byte-identical afterwards; the importer rerun created nothing. **Limitation:** the operator-visible rerun is `tools.bootstrap_manager` — its rehearsal mode, plus the closed-bootstrap refusal. A Council-authorized *repeat apply* has no CLI and is covered by automated tests (M8) rather than by this rehearsal |
| O4 | **direct restricted-runtime-role denial** of `UPDATE`, `DELETE`, `TRUNCATE` against every append-only Phase 2 table | `automated — passed` | `test_runtime_grants_live.py`, against the real `freedom_runtime_test` role over `SET ROLE`, on real PostgreSQL, with no skips in this run. This closes the A-02 gap recorded on 2026-08-02 |
| O5 | **independent review closure** of every blocking security, identity, atomicity, migration and recovery finding | `failed/blocked` | **No finding is closed.** Round 4 recommends closure of the publication finding and preserves the rest; a recommendation is not a closure. I-3R-1 awaits the narrow re-review requested in §8. Next action: that re-review, then Peter records the closures |

### 5.4 Plan §13.3 review-gate evidence

| # | Requirement | Disposition | Detail |
|---|---|---|---|
| E1 | a traceability table mapping every criterion and mandatory scenario to named tests or an identified supervised check | **delivered by §5 of this document** | §§5.1–5.4. Every item carries exactly one disposition and a named test or a named supervised check |
| E2 | unit and application tests for parsing, field policy, authorization, reconciliation and typed failures | `automated — passed` | `test_snapshot_parser.py` (41), `test_field_profile.py` (41), `test_snapshot_import_service.py` (67), `test_snapshot_reconciliation.py` (33), `test_snapshot_values.py` (27) |
| E3 | repository/contract tests proving the same transaction and audit behaviour for fakes and the PostgreSQL adapter | `automated — passed` | `tests/fakes.py` drives the same service under `test_snapshot_import_service.py`; `test_snapshot_database.py` and `test_submission_database.py` drive it against PostgreSQL |
| E4 | PostgreSQL integration tests for migrations, uniqueness, foreign keys, optimistic concurrency, idempotency, rollback and runtime-role audit immutability | `automated — passed` | `test_database_postgresql.py` (39), `test_snapshot_database.py` (43), `test_runtime_grants_live.py` (13), `test_migration_safety.py` (14) |
| E5a | web surfaces — authentication, current-role authorization, input limits, escaping, stale-submission | `automated — passed` | `test_http_submission.py` (66): authentication, scope, body and length limits, content-type, checksum, safe error bodies, CORS positive and negative |
| E5b | web surfaces — **CSRF** | `not applicable` | ADR 0009 (accepted 2026-08-04): the endpoint is a machine API taking a bearer credential per request, with no cookie, no session, no OAuth flow, and the module sends `credentials: "omit"`. There is no ambient authority for a cross-site request to ride |
| E5c | web surfaces — **object-level authorization** | `not applicable` for this package | Submission stores an immutable artifact and creates no per-object access decision; the preview route is disabled until the Phase 3 authentication boundary (`authentication_unavailable`, asserted by `test_http_submission.py`). Object-level authorization belongs to Phase 3 |
| E6 | Discord surfaces | `not applicable` | Phase 2 exposes no Discord surface. The live bot is untouched by this package |
| E7 | CLI/operator surfaces — filesystem and artifact limits, authority, refusal, exit codes, safe output, non-interactive recovery | `automated — passed` | `test_bootstrap_cli.py` (11), `test_import_cli.py` (30), `test_artifact_store.py` (94), `test_database_backup_restore.py` (8) |
| E8 | database mutations — real transaction, constraint, concurrent outcome, restricted-role and recovery evidence | `automated — passed` **and** `disposable rehearsal — passed` | M10, M21, M22 above; plus §§7.1–7.2 |
| E9 | deterministic synthetic snapshot fixtures covering the supported schema without real character data | `automated — passed` | `tests/foundry_fixtures.py`, `test_fixtures.py` (26), `test_exporter_contract.py::test_the_fixture_ids_match_the_javascript_fixture` |
| E10 | the narrow relevant suite followed by the full configured suite, exact commands and results reported | `automated — passed` | §6, from this run. Not copied from a historical report |
| E11 | formatter, linter, type checker, migration consistency and `compileall`, or an explicit statement that a check is not configured | **partly `not applicable`** | `alembic check` and `compileall` passed (§6). **Formatter, linter and type checker are not configured** in this repository and are not installed in `venv`. None was installed to manufacture a check. This is a standing repository gap, not one this package introduced |
| E12 | diff review for secrets, raw snapshots, unsafe logs and accidental production data | `automated — passed` (mechanical) plus manual review | §9: what was inspected, how, and the limits of it |
| E13 | recovery documentation exercised against a disposable environment wherever the phase introduces a new persistent mutation | `disposable rehearsal — passed` | §§7.1–7.2 exercised `database-development.md`'s drill and downgrade strategy. `foundry-snapshot-submission.md` §9's *unexpected-entry* branch is exercised by tests rather than by a rehearsal, because producing the condition means planting a hostile file in a real store |
| E14 | skipped tests, mocks and synthetic fixtures reported accurately | `automated — passed` | `pytest -q -rs` reported **no skips** in this run. Every fixture is synthetic. The three new hygiene tests skip only if `find` is absent; it is present here and they ran |

---

## 6. Verification — exact commands and exact results from this run

2026-08-05, on this host, after all changes in §1.3. Not copied from a previous
report.

```bash
cd /opt/discord-bots/freedom-bot

(cd foundry-module && node --test "tests/*.test.mjs")
# tests 81 | pass 81 | fail 0 | cancelled 0 | skipped 0 | todo 0

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test ./venv/bin/python -m pytest -q \
  tests/test_artifact_store.py tests/test_snapshot_submission.py \
  tests/test_storage_claim_vocabulary.py tests/test_submission_composition.py \
  tests/test_http_submission.py tests/test_snapshot_preview_service.py \
  tests/test_exporter_contract.py tests/test_submission_database.py
# 376 passed in 2.66s

TEST_DATABASE_URL=postgresql+psycopg:///freedom_test \
  ./venv/bin/python -m pytest -q -rs
# 1944 passed, 1 warning in 10.50s        (no skips reported)

./venv/bin/python -m compileall -q application adapters domain tools tests migrations
# exit 0

APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test' \
  ./venv/bin/alembic check
# No new upgrade operations detected.

git diff --check
# exit 0

for file in foundry-module/scripts/*.js foundry-module/tests/*.mjs; do
  node --check "$file"
done
# 16 files, all clean
```

**Counts moved, and why.** Module tests **81**, unchanged — no module file was
touched. Named suites 373 → **376**; full suite 1941 → **1944**. The difference
is exactly the three operator-hygiene tests in §1.4. **No test was deleted,
weakened or renamed.**

The one warning is `audioop` deprecation from the vendored `discord` library.

**Formatter, linter, type checker: `not configured`.** `ruff`, `black` and
`mypy` are absent from `venv`, and there is no `pyproject.toml`, `setup.cfg`,
`.flake8` or `ruff.toml`. None was installed.

---

## 7. Disposable-environment rehearsals — exact commands and results

All against `freedom_test` over the local Unix-domain socket, synthetic fixtures
only. **No production service was contacted and no real credential existed at
any point.**

### 7.1 Upgrade → downgrade → upgrade (O2)

```bash
export APP_ENVIRONMENT=test DATABASE_URL='postgresql+psycopg:///freedom_test'
./venv/bin/alembic current                      # 0004 (head)
./venv/bin/alembic downgrade base               # 0004→0003→0002→0001→base
./venv/bin/alembic upgrade head                 # base→0001→0002→0003→0004
```

| Observation | Result |
|---|---|
| tables before | 13 |
| tables at `base` | 1 (`alembic_version` only) |
| tables after | 13, identical names |
| full column/constraint/index digest (205 lines) | `sha256 5b472c49d08e05dda60a461b5c86910800b77689609c6f9e501d98a2b4ef65c6` **before and after** |
| final revision | `0004 (head)` |

The digest compares every `information_schema.columns` row, every
`pg_constraint` definition and every `pg_indexes` definition — so this is a
schema-equality claim, not a table-name one.

### 7.2 Backup, restore and importer rerun (O3)

```bash
# 1. populate: rehearsal first (writes nothing), then the supervised bootstrap
./venv/bin/python -m tools.bootstrap_manager --snapshot "$WORK/synthetic.json"
./venv/bin/python -m tools.bootstrap_manager --snapshot "$WORK/synthetic.json" \
    --bootstrap --supervisor "disposable rehearsal operator"

# 2. dump, checksum, destroy the schema, restore, compare the inventory
./infra/postgresql/backup-restore-drill.sh freedom_test "$WORK/drill"

# 3. rerun against the restored database
./venv/bin/python -m tools.bootstrap_manager --snapshot "$WORK/synthetic.json" \
    --bootstrap --supervisor "disposable rehearsal operator"
./venv/bin/python -m tools.bootstrap_manager --snapshot "$WORK/synthetic.json"
```

| Step | Result |
|---|---|
| rehearsal before the bootstrap | `actors 2, would create 2, already mapped 0, blocked 0, absent 0`; **0 rows written** (all five counters 0) |
| supervised bootstrap | `Applied. 2 character(s) created.` Rows: 2 characters, 2 mappings, 1 import, 4 audit events, 1 initialization |
| drill step 0 | `Target verified: database 'freedom_test', Unix-domain socket` |
| drill steps 1–6 | dump `sha256 09966f94…96e46`; inventory recorded; `public` schema dropped; restored; **`Restore verified for freedom_test`**, exit 0 |
| identity after restore | `external_actor_mappings` rows **byte-identical** to the pre-drill capture |
| audit after restore | `audit_events` rows **byte-identical** to the pre-drill capture |
| rerun as bootstrap | correctly refused: *"The bootstrap disables itself after its first success; later imports require one currently authorized Guild Council member."* Row counts unchanged: `2|2|1|4|1` |
| rerun as rehearsal | `actors 2, would create 0, already mapped 2, blocked 0, absent 0`; `0 error(s), 24 warning(s)`, all `legacy_authority_deferred` naming packages 5.1, 5.2 and 5.6a; **nothing written** |
| duplicate identity or audit effect from the rerun | **none.** Both captures diffed clean |

**Cleanup performed:** `alembic downgrade base && alembic upgrade head`, leaving
`freedom_test` at `0004 (head)` with every table empty — its documented state.
Both dumps and the work directory were deleted. Nothing was retained outside the
session scratch directory, and nothing entered the repository (`git status`
confirms no new file).

### 7.3 Operations §5.8 server-half smoke test

Run exactly as documented: a freshly generated **synthetic** secret held only in
the shell, its digest in configuration, a bundle built from the committed test
fixtures, and a rehearsal server on `127.0.0.1:8757`.

| Check | Expected | Observed |
|---|---|---|
| first POST | `201` + receipt | `201`, `duplicate:false`, `actor_count:1`, `canonical_encoding:true`, one folder |
| second POST, same key and bytes | `200`, `duplicate:true`, same `snapshot_id` | exactly that, same `snapshot_id` and same `correlation_id` |
| artifact root | one `0600` file named for its own SHA-256 | `-rw------- … 661278bf….json` |
| leftover temporaries | none | `find … -name '.incoming-*'` matched nothing |
| preflight, allowed origin | `204` + exact `Access-Control-Allow-Origin` | `204`, `Access-Control-Allow-Origin: https://foundry1.example.org`, methods `POST`, exactly the four headers, `Vary` naming Origin |
| preflight, unlisted origin | `403 origin_not_allowed`, no permission header | exactly that; no `Access-Control-Allow-Origin` in the response |
| unauthenticated POST | `401` | `401` |
| database after | one snapshot row, `received_via=foundry_module`, `submitted_by_principal` set; 0 characters, 0 imports | `foundry_module|foundry-the-guild`; `1|0|0|1` (one audit event) |
| request log | status codes only | `request handled status=201/200/204/403/401` — no secret, no path, no Actor value |

**Cleanup:** server stopped, the four tables truncated, the work directory
removed, the synthetic secret never written to any file.

**One honest observation.** `tools.snapshot_api` prints the configured artifact
root path in its **startup banner** on the operator's own console. That is the
rehearsal launcher's banner, not the endpoint's request logging — the request
log carried a status and nothing else, as §5.7 requires — but it is a path on an
operator console and worth a reviewer's eye rather than my assurance.

**This is not a substitute for S1 or S2.** `curl` sends no `Origin` unless told
to and enforces no CORS; a `204` from a server is not a browser completing a
preflight, and no Foundry client was involved at any point.

---

## 8. Supervised run sheet — for Peter

Exact, copyable, and containing **no** real secret, origin, Actor name, raw
snapshot, private filesystem path or player data. Everything in angle brackets
is a **placeholder you replace**.

### 8.1 Prerequisites (both checks)

- a **disposable rehearsal** Foundry world and a **non-production** ingestion
  endpoint. Not the live world, not the live service;
- a **synthetic** credential, generated for this exercise and rotated afterwards
  whatever the outcome;
- two browser profiles, so an ordinary player session is genuinely separate from
  the GM session;
- a place to record observations that is **not** this repository until the notes
  have been redacted.

Generate the synthetic credential and the digest configuration holds
(operations §5.2). The secret goes to your password manager and nowhere else:

```bash
SECRET=$(./venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))')
./venv/bin/python -c \
  'import sys; from adapters.http.credentials import secret_digest; print(secret_digest(sys.argv[1]))' \
  "$SECRET"
# put ONLY the printed digest into FREEDOM_SNAPSHOT_PRINCIPALS
```

**Abort conditions for both checks.** Stop, record what you saw, and do not
continue if: the world is not the rehearsal world; the endpoint is production;
any real player is in the world; the credential turns out not to be synthetic;
or a check reveals the credential anywhere it should not be — that last one is a
finding, and the exercise has succeeded at its job.

### 8.2 S1 — credential confidentiality from a live second client (operations §8.1)

1. As a **GM**, open the Actor Directory, open the Freedom Blades export dialog,
   and submit with the synthetic credential. Confirm a receipt appears.
2. In the **GM** console:

   ```js
   const M = "freedom-blades-export";
   [...game.settings.settings.keys()].filter(k => k.startsWith(M));
   // EXPECT: the endpoint and version settings. NO credential, secret or token key.

   game.settings.storage.get("world")
     .filter(s => /credential|secret|token/i.test(s.key));
   // EXPECT: empty.
   ```
3. **This is the point of the exercise.** Join the same world as an **ordinary
   player**, in the second browser profile, and in *that* player's console:

   ```js
   JSON.stringify([...game.settings.storage.get("world")].map(s => s.value))
     .includes("<the synthetic secret>");
   // EXPECT: false
   ```
4. Re-open the dialog as the GM. **Expected:** the credential field is present,
   masked, and **empty** — never pre-filled, because nothing stores it.

**Record:** each expectation and whether it held; the Foundry and system
versions; the date; and that the credential was synthetic. **Record no secret,
no world path and no Actor name.** **Rotate the synthetic credential
afterwards regardless of the outcome.**

**Why no automated test can replace this:** the claim is about what the Foundry
*server* delivers into another user's browser. Source analysis established the
mechanism; only a second live client observes the delivery. This is the exact
class of failure that produced S-B-1.

### 8.3 S2 — the browser origin actually passes the preflight (operations §8.2)

1. Put the rehearsal Foundry instance's **exact** origin in
   `FREEDOM_SNAPSHOT_ALLOWED_ORIGINS` (scheme, host, port; no path, no trailing
   slash, no wildcard) and reload the service.
2. Submit from the Foundry **browser** client. **Expected:** a receipt.
3. In the browser's network panel: an `OPTIONS` preceded the `POST` and returned
   `204` with `Access-Control-Allow-Origin` naming **that** origin.
4. **The negative case, which is what makes this worth doing.** Remove the
   origin from the allowlist, reload, submit again. **Expected:** the module
   reports a network failure, and the server logs a refused preflight. If the
   submission still succeeds, the allowlist is decorative and that is a finding.
5. Restore the allowlist and confirm step 2 works again.

**Record:** the four expectations, the status codes seen, and the date.
**Record the origin as `<rehearsal-origin>`, not the literal value**, unless
Peter decides the literal origin is safe to store.

**Why no automated test can replace this:** `curl` does not enforce CORS. B-1
existed precisely because a correctly answering server was mistaken for a
working workflow.

### 8.4 What is *not* in this run sheet, deliberately

**S3 and S4** (the two rehearsals) are covered by operations §§6 and 7 and are
not restated here — they involve a real export, and their procedure belongs
where the redaction rules for it already are. **S6** (cross-account) requires a
second POSIX account and privilege escalation, and must not be attempted without
Peter supplying and supervising an approved disposable account.

---

## 9. Diff and working-tree review

**What was inspected.** The complete diff from `c8a3da9` plus the full contents
of every untracked file in the package — 28,620 lines assembled into one stream
and reviewed for the categories below.

| Looked for | Method | Result |
|---|---|---|
| secrets and key material | pattern scan for private-key headers, AWS/Slack/GitHub/OpenAI token shapes, long bearer values and assigned password literals | **one hit, benign**: the synthetic literal `Bearer wrong.credentialcredential…` in an HTTP refusal test. `.env.example` holds placeholders and digests only |
| raw snapshots or artifacts | every `.json`, `.dump`, `.sql`, `.log` in the package listed | only `foundry-module/module.json` and `package.json`, both module manifests. **No artifact, no dump, no export** |
| Actor or player data | fixture inspection; search for the authorized export directory | fixtures are synthetic and shared with the JavaScript side (`test_the_fixture_ids_match_the_javascript_fixture`). `/opt/discord-bots/foundry-actor-exports` appears in **prose only** and was never read |
| unsafe logs | reviewed against `adapters/safe_logging.py` and observed live in §7.3 | request logging emitted a status and nothing else. The §7.3 startup-banner path is noted honestly there |
| generated files | `git status` and the untracked list | none. No `__pycache__`, no build output, no editor file |
| unrelated changes | file-by-file against §1.3 | none. Every file in the working tree belongs to this package or its predecessors |
| migration reversibility | `0003` and `0004` read; exercised in §7.1 | both additive with working `downgrade()`. `0004` downgrade **discards provenance values**, which operations §9 states and instructs a backup first |
| false claims | §2's targeted audit, plus reading every disposition in §5 against the thing it names | the I-3R-1 family corrected; A2b and A18 are dispositions this audit **changed for the worse** because the honest answer was worse |

**Limits of this review, stated rather than implied.**

1. It is a review by the author of the change. That is exactly why the narrow
   independent re-review in §10 is requested;
2. the secret scan is pattern-based. It would not catch a credential that looks
   like ordinary prose;
3. "no unsafe log" is established from the logging boundary, the tests and one
   live rehearsal — not from an exhaustive trace of every call site;
4. **the working tree is not thereby ready to commit.** Tests passing is not a
   commit decision, nothing here is committed or pushed, and the commit decision
   is Peter's.

---

## 10. What I am asking for

A **narrow independent implementation re-review**, not a full re-review:

1. **I-3R-1** — is the temporary-cleanup contract now stated correctly and
   consistently in the adapter docstring, operations §5.6/§9, `.env.example`, the
   review record and the controlled records? Is the corrected six-row table in
   §1.2 actually what the implementation guarantees, and does anything anywhere
   still promise zero surviving temporaries without a proven precondition?
2. **the new tests** — do the three hygiene tests prove the *documented* rule
   rather than a convenient restatement of it, and is the age bound and
   link-count reading right for an operator whose next step is deletion?
3. **the traceability and evidence claims in §5** — are they **truthful**? Every
   `automated — passed` names a test I believe covers the criterion; the useful
   thing a reviewer can do is find one that does not, or a criterion I gave a
   better disposition than the evidence supports. **A2b, A18 and O5 are where I
   downgraded my own earlier position**, and §4.9's "not gate-ready" is the
   conclusion I most want checked.

**A security re-review is not requested**, because no security-relevant code or
contract changed: publication, anchoring, S-B-1 and S-I-1 are untouched, and the
third security re-review already described the best-effort cleanup correctly. If
you consider a documented operator deletion procedure security-relevant, say so
and I will request one.

**Please do not implement fixes** — report findings and let me address them, so
the next re-review has something independent to check. Classify per plan §16.4.
**I close no finding here.**

Peter Duscha remains the Acceptance Authority and records the decision. This
document claims no gate, and Phase 2 is not finished.
