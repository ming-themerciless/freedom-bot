# Claude handback — C-P5.0-R5-RP11-I1-R3-I1 — retained-alias publication, requirements and source — 2026-09-28

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-retained-alias-implementation-claude-prompt.md).
Controlling decision:
[I1-R3 proposal](phase-5-0-p5-r5-rp11-i1-r3-publication-redesign-proposal.md)
and its [acceptance](project-review-2026-09-28-p5-r5-rp11-i1-r3-redesign-acceptance.md).
Context: Codex's [I1-R2 review](project-review-2026-09-28-p5-r5-rp11-i1-r2.md),
[I1-R1 review](project-review-2026-09-28-p5-r5-rp11-i1-r1.md) and
[I1 review](project-review-2026-09-28-p5-r5-rp11-capture-mechanism.md).
Accepted requirements baseline, unchanged in authority: the R5 bytes of the
operational-evidence draft, SHA-256 `5e06a388…`.

## 1. Outcome

* **Requirements and source amended together, for review only.** RP-11
  publishes every record and index state as one inode with two retained names:
  1. an exclusively created **staging name**;
  2. one non-replacing, no-follow, descriptor-relative hard link to the
     **final name**;
  3. both names verified after the directory barrier;
  4. both names and their shared inode recorded in the **next durable index
     state**, which alone admits the object.

  No name is ever unlinked, renamed, repaired or cleaned up.
* **Removed.**
  * The `O_TMPFILE` inode.
  * The `/proc/self/fd` link and its follow-semantics caller,
    `link_unnamed_descriptor`.
  * The I1-R1 mutating §9.5.4 capability probe and its probe-directory
    maintainer inputs.
  * The I1-R1/R2 portability diagnostic module.
* **Capability test.** The first real publication, X-1's genesis state, is now
  the fail-closed capability test before any host command. Its failure has the
  same bounded-residue and stop semantics as every later publication.
* **One in-session maintainer decision (§4)** settles an ambiguity between the
  assignment and the accepted proposal: how X-4 and B0-RA treat a recorded
  *unadmitted* staging/final pair.
* **Draft SHA-256:** `186ff546…` →
  **`402126322f341d378c569cc302c8eb3607b746a1b5c8fc81a91d6af8b19cbe28`**. It
  is unreviewed and unaccepted, and the R5 bytes remain the baseline.
* **Manifest.** Version **22 → 23**. The review-input digest is
  **`264674daf8ac4f6a385e3c056510d213321c767b1d482a143b18a139b108df1e`**. **It
  is not an approval** and must never reach `--execute`.
* **Unwired.** No command, CLI or default/dry-run path reaches RP-11.
  `plan.is_executable=False`.
* **Local results, with `TEST_DATABASE_URL` unset.**
  * RP-11 suites: **367 passed, 0 skipped**.
  * The I1 focused selection: **1270 passed, 0 skipped**.
  * All of `tests/phase_5_0_evidence`: **3320 passed, 0 skipped**.

**Findings.** RP11-I1-R1-1, RP11-I1-R2-1 and RP11-I1-2 all remain **Open**.
The requirements, the implementation and the digest remain unaccepted, and
RP-11 remains unmet.

**Gates.** Neither pass is executable. P5.0-R5 remains Blocking and OD-62 G-A
remains conditional. `plan.is_executable=False`, and Package 5.0 remains not
ready.

None of the following occurred: SSH, rsync, network or host inspection,
`sudo`, database access, verifier, evidence band, harness `--execute`, real
participant, real capture root, operational path, protected `/tmp` artifact,
secrets scan, guard or hook change, commit or push. No guard refused a call.

## 2. Files and digests

All SHA-256 values below were recomputed independently after the final edit.

| File | Change | SHA-256 before → after |
|---|---|---|
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | amended in place (§3) | `186ff546…` → `402126322f341d378c569cc302c8eb3607b746a1b5c8fc81a91d6af8b19cbe28` |
| `tools/phase_5_0_evidence/capture_contract.py` | staging names, roles, index schema `/2`, pair-aware *R* | `e7a42d10…` → `437d663e6cf79ac3d4cd62c0cbf7955a8fe9b207c680b144af6b9cd3beb60dd7` |
| `tools/phase_5_0_evidence/execution/capture_store.py` | retained-alias `publish`, `PublicationState`, content check | `4dfb5cee…` → `c038174db4e7293637eee831b58a0fd54dcc4194c5065fd90fd324e54a3fd081` |
| `tools/phase_5_0_evidence/execution/capture_mechanism.py` | admission by the next state, *F* self-pair, not-made residue | `a1c75889…` → `b64d92cb7fcbd6176dee616d312ab24132a5d780cb7ebae7fe04922088c3c14a` |
| `tools/phase_5_0_evidence/execution/retention_check.py` | the one alias exception; admitted-pair X-4 checks | `7bfb2116…` → `482e1a5a1d1b3fcb093544cd6634a6003f3e1ac288095bd6b9b4c43cd3e3668a` |
| `tools/phase_5_0_evidence/execution/descriptors.py` | `_exclusive_link` loses `follow`; `link_named_exclusive` replaces `link_unnamed_descriptor` | `499ea15a…` → `84db093593bb1d5f844e66ec3391f6fd182b9982bcdbb974d687586d347a9a04` |
| `tools/phase_5_0_evidence/review_manifest.py` | `MANIFEST_VERSION` 23 and its reason | `e35435a0…` → `b7e7cabe7b169d4a8eaa900323b2c64c72b43ab484ebb5ec42b718479084af96` |
| `docs/review/phase-5-0-evidence-harness-review-manifest.json` | regenerated (dry run) | `3c3a6d79…` → `f4f2453768bb3da5eda1a0ca7ce4a640d0a612066746c6734bfa83ba94353d5a` |
| `docs/review/phase-5-0-evidence-harness-concrete-plan.md` | regenerated (dry run) | `4fc2e9e9…` → `ddb51460b742d857c132f629854d421fc77ad1aad0e1db4932f603abf1fa6caf` |
| `tests/phase_5_0_evidence/rp11_fixtures.py` | `link_exclusive` seam; false-success write modes | `6df09b8a…` → `8fe61df47268730620110cba7980cafc6d98dddb936351be9b63534c175d6df0` |
| `tests/phase_5_0_evidence/test_rp11_capture.py` | updated and new tests (§6) | `24114c0f…` → `053de064dc2668087f2a37d13e72292c2367a7d6237e14d51f1240061bd2366a` |
| `tests/phase_5_0_evidence/test_rp11_retention.py` | pair and alias tests (§6) | `a825981…` → `0863414c0664f33a5e5a5cc813956cdee283283703e73d3edffb19adb75666ea` |
| `tests/phase_5_0_evidence/test_r16_remediation.py` | version pin 22 → 23 | `38646749…` → `2a1dd50b53fe4ca601bdc49582fe0f8bfe246d3742b350a5b1e71ecdb2de1935` |
| `tests/phase_5_0_evidence/test_no_execution.py` | one tier comment | → `76e5da9b351d40fa0a572cf93106adad2df41d95570b118fa6fb9b44f3cb3eb6` |
| `tests/phase_5_0_evidence/test_rp11_publication_portability.py` | **deleted** (untracked; last digest `f2845fd6…`) | — |
| this handback; `Handover information`, `status.md`, plan §20, the first disposable-server banner | new / return pointers | — |

**Unchanged by this pass, with their digests:**

* `errors.py` (`6686cdf0…`).
* `execution/boundary.py` (`329d0001…`).
* The I3 caller `PosixFilesystem.linkat`: its behaviour, flags and refusals
  are unchanged. Its one keyword argument to `_exclusive_link` was dropped,
  because no-follow is now fixed at the call site.
* The historical handbacks and reviews. The I1 handback appears as modified
  in `git status`, but it was already modified before this session and was
  not touched.

**Candidate `capture_tool_sha256`** (schema `rp11-capture-tool/1`, over the
seven `RP11_SOURCES`): `9c1b02a1b7ef861ffb177b162427a185b90d86c3aa25d3a64573848d36a1d992`.
It is review input only and is not pinned.

## 3. Semantic draft changes

Each item was changed coherently throughout the draft.

* **Header.** Records the I1-R1/R2 reviews, the I1-R3 acceptance and this
  amendment. The amendment **supersedes only the I1-R1 publication
  amendment** and reopens no accepted R5 retention requirement.
* **§0.** The §9 row names the retained-alias route and its X-1 capability
  test.
* **§4.3.** Records that I1 (v22, `adeabe17…`) and I1-R3 (v23, `264674da…`)
  changed covered sources, so the drafting-time manifest pins are stale and a
  later draft must re-pin them. The capture-tool digest scope is unchanged.
* **RP-11 row.** Replaces unnamed-inode publication with the staging name, the
  exclusive final link, retained both names and admission by the next durable
  state. The I1-R1 (a)–(d) list becomes (a) the X-1 capability test with no
  separate probe, (b) one no-follow link site serving two named-source
  contracts, (c) the seal, (d) the binding block and (e) the one alias
  exception. C-11 and the launcher environment remain blockers.
* **§4.5.** `MI.capture_root_A` and `MI.capture_root_B` are tested by their
  own X-1. The **`MI.publication_probe_directory_A/_B` row is removed**.
* **A0-08 and B0-08.** The probe steps are removed. The genesis publication is
  the capability test. On failure: stop before any host command, no X-3,
  residue retained and reported, no retry. Pass A's result is never reused
  for Pass B.
* **B0-RA.** Adds the one alias exception.
  * **Admitted pairs:** names, roles, owner, mode, device/inode, link count
    two, and size and digest through the final name must all agree.
  * **Unadmitted recorded pairs:** metadata only (§4).
  * Everything else is a stop.
* **§9.5 introduction and C-5, C-7, C-10, C-13, C-14.** Durability and
  admission are restated for pairs. C-7 makes the recorded pair the only
  permitted alias, and no name is ever removed.
* **§9.5.1.** New terms:
  * *Staging name*: exact flags; an occupied name refuses unread.
  * *Exclusive final link*: exactly one call; `EEXIST` is the only
    non-replacement check; no pre-check.
  * *Retained alias pair*.
  * *Shared no-follow call site*: the I1-R1 follow contract is withdrawn.
  * *Platform prerequisites*: no procfs and no `O_TMPFILE`.

  P-5 … P-8 gain the checked write and content check, and the P-8 pair
  verification. A new **six-row publication-state table** covers every state
  from *no staging entry* to *both admitted*, with fail-closed semantics for
  each.
* **§9.5.2.** Each state records `owner_uid`, a predecessor link (both names,
  digest, inode) and every entry's pair. *F* records its own pair.
  * X-1 is the capability test.
  * X-2 admits record *n* and *I*-(*n* − 1).
  * X-3 creates only *F*'s two names. Its finalization point is verification
    of both names after the directory barrier.
  * X-4 gains the pair conditions and the alias exception.
* **§9.5.3.**
  * Unadmitted objects now include staging names and pairs.
  * X-3 may account for already-created names but never completes a
    publication.
  * The success point is updated.
* **§9.5.4.** **Replaced.** There is no separate mutating probe; the first
  real X-1 publication is the fail-closed test.
* **§10.**
  * Item 9: staging names are retained evidence, never cleaned up.
  * Item 10: there is no probe.
* **§11.2 and §11.3.** Stop conditions are restated for staging, content
  check, final link, pair verification and the X-1 capability test. The probe
  directory and probe-emptiness conditions are removed.
* **§14 template.** The probe line becomes the X-1 capability-test result.
  Unadmitted lines include staging names and pairs. The binding block is
  unchanged.
* **Closing reminder.** Updated.

Remaining textual mentions of `O_TMPFILE`, `/proc/self/fd` and "probe" are
history, explicit negations, or the harness's unrelated probe bands.

## 4. In-session maintainer decision — unadmitted recorded pairs

**The conflict.**

* Assignment §4 limits the alias exception to "the recorded staging/final
  pair for one **admitted** object".
* The accepted proposal §4 says "the one staging/final pair explicitly
  recorded for a **published** object".

**Why it matters.** A stop between the final link and admission leaves an
unadmitted pair: two names on one inode, link count two. Read literally,
assignment §4 would make X-4 inconclusive for the **whole pass** after any
such stop, discarding earlier admitted acts, and B0-RA would refuse Pass B.

**The decision.** Asked in session on 2026-09-28, **Peter Duscha chose
"Permit, metadata-only".** A pair *F* records as unadmitted may share one
inode only if:

* both recorded names are present;
* both are regular files;
* they share one inode;
* the link count is exactly two; and
* no other name reaches that inode.

Nothing is opened, read or digested for it, and no identity is recorded or
compared, because none is recorded for unadmitted objects. A divergent pair
(`pair-divergent`), a third link, or a lone staging name with a second link
is a stop.

**Status.** This is a proposed reading for Codex review, recorded here and in
the draft's B0-RA text. The maintainer should confirm that this in-session
answer is the decision of record.

## 5. Architecture and interfaces

* **`descriptors`**
  * `_exclusive_link(source, destination, *, source_dir_fd, destination_dir_fd)`
    always passes `follow_symlinks=False`. It is the package's only `os.link`.
  * New `link_named_exclusive(source_dir_fd, source_name, destination_dir_fd, destination_name)`:
    one component each; raises `OSError` unchanged; removes nothing.
  * New constant `RETAINED_ALIAS_PUBLICATION`. `EXCLUSIVE_LINK_PRIMITIVE`'s I1
    paragraph is replaced by the I1-R3 statement.
  * Removed: `link_unnamed_descriptor`, `UNNAMED_PUBLICATION` and their
    exports.
* **`capture_contract`**
  * New: `STAGING_SUFFIX`, `staging_name()`, `role_of()`, and `ROLE_*`.
  * `IndexEntry(capture_seq, name, staging, sha256, device, inode)`.
  * New: `StateLink`, `SelfPublication`.
  * `IndexState` gains `owner_uid`, `previous` (a property keeps
    `previous_state_sha256`) and `publication` (final only).
  * `INDEX_SCHEMA = rp11-capture-index/2`. `RECORD_SCHEMA` and
    `BINDING_FORMAT` are unchanged.
  * `accounted_objects(final, chain, records)` returns `AccountedObject`s with
    role, partner and recorded identity.
  * New refusal: `pair-mismatch`.
* **`capture_store`**
  * The `CaptureFilesystem` seam drops `create_unnamed` and `link_unnamed`
    and adds `link_exclusive(dir_fd, source, destination)`.
  * `write_all` refuses no-progress writes.
  * `publish(name, bytes | (device, inode) -> bytes, stages) -> Publication`.
  * `PublicationStages` gains `verify_content` and `verify_pair`, plus
    `ordered()`.
  * New: `PublicationState`, `publication_states`, `mark_admitted()` (only
    `VERIFIED` → `ADMITTED`), and `owner_uid`.
  * New store failure: `content-mismatch`.
* **`capture_mechanism`**
  * X-2 marks record *n* and *I*-(*n* − 1) admitted after *I*-*n* verifies;
    X-3 success marks the last state and *F*.
  * *F* embeds its own pair through the content callback.
  * `FinalizationOutcome` gains `final_staging_present`. The not-made outcome
    reports X-1 residue by name.
  * New: `CaptureSession.publication_states`, read-only.
* **`retention_check`**
  * `_Facts` gains owner and permissions.
  * Enumeration refuses link count > 2 and more names than the link count;
    whether a second name is the recorded partner is decided against *R*.
  * New X-4 check `_admitted_pairs`, with reasons `pair-member-absent`,
    `-not-regular`, `-identity-mismatch`, `-link-count` and
    `-owner-or-mode`.
  * New `_aliases` check, with reasons `path-alias` and `pair-divergent`.
  * The evidentiary limit states that staging names are proved to be the
    same inode by metadata.

## 6. Requirement-to-test map

All tests below are in `tests/phase_5_0_evidence/`.

| Requirement (assignment §) | Tests |
|---|---|
| Success creates exactly the pair, one inode, link count two, exact bytes, the barriers in order (§6.1) | `test_rp11_capture.py::test_each_publication_is_exactly_the_accepted_sequence` (genesis, record, advance and final; exact call and stage order; one link; no `lstat` pre-check; no rename or unlink); `…::test_a_successful_publication_is_one_inode_with_two_names_and_exact_bytes`; `…::test_the_root_is_created_exclusively_with_the_fixed_layout_and_modes`; `…::test_three_acts_publish_a_gap_free_chain_and_a_valid_final_state` |
| An occupied staging or final name refuses without mutation (§6.2) | `…::test_an_occupied_staging_name_refuses_without_reading_or_removing_it` (mode `000` occupant, unchanged `lstat`); `…::test_an_occupied_final_name_is_never_replaced` |
| Partial, zero-length and falsely reported writes never admit (§6.3) | `…::test_a_partial_empty_or_falsely_reported_write_never_admits` (3 modes × genesis, record and advance); `…::test_the_write_loop_completes_short_writes_and_refuses_no_progress` |
| Every §3 interruption leaves its exact classified state; no retry, repair or clean-up; the next act is prevented (§6.4) | `…::test_every_publication_interruption_leaves_its_exact_classified_state` (18 stages); `…::test_every_act_stage_fails_closed_once_with_the_correct_final_state` (every act stage plus 5 after-effect cases, with state assertions); `…::test_an_interruption_at_any_act_stage_ends_the_pass_with_no_x3`; `…::test_a_failed_x3_attempt_is_recorded_not_retried_and_x4_is_inconclusive` (9 stages); `…::test_the_first_genesis_publication_is_the_fail_closed_capability_test` (9 stages) |
| A barrier failure stays terminal (§6.5) | `…::test_a_failed_barrier_is_terminal_and_never_cured` (no re-sync; `mark_admitted` refuses); the `count(stage) == 1` assertions throughout |
| X-4 and B0-RA accept only a recorded pair (§6.6) | `test_rp11_retention.py::test_every_admitted_object_is_a_recorded_pair_and_b0_ra_accepts_it`; `…missing_staging_member…` (4 pairs); `…missing_final_member…`; `…replaced_by_an_identical_copy…`; `…third_link…` (inside and outside); `…cross_object_alias…`; `…two_accounted_names_that_are_not_partners…`; `…mode_changed…`; `…recorded_identity_that_differs…` (the publication and previous links); `…staging_name_that_is_not_the_rule_s…`; `…name_in_two_pairs_or_categories…`; `…unexpected_staging_name…`; `…unrecorded_published_pair…`; every pre-existing hostile-tree and race test, unchanged |
| Unadmitted states are retained and never read as evidence (§6.7) | `…::test_a_recorded_unadmitted_pair_is_retained_and_never_read` (4 stop stages, X-4 and B0-RA); `…pair_whose_members_diverge…`; `…unadmitted_pair_with_a_third_link…`; `…deleted_member_of_an_unadmitted_pair…`; `…unadmitted_staging_name_hard_linked_elsewhere…`; the existing `…never_opens_an_unadmitted_object` and `…replaced_unadmitted_object…` |
| Source and AST guards (§6.8) | `test_rp11_capture.py::test_no_unnamed_inode_procfs_ctypes_rename_or_removal_on_the_rp11_route` (5 modules); `…::test_the_store_links_only_through_the_shared_named_primitive`; `…::test_the_package_has_one_link_call_it_never_follows_and_two_callers_reach_it`; `…::test_a_real_named_link_refuses_to_replace_and_keeps_both_names`; `…::test_nothing_outside_tests_arms_the_launcher_or_creates_a_session`; `…::test_the_harness_cli_does_not_reach_the_capture_mechanism`; `test_rp11_retention.py::test_the_verifier_module_cannot_write` |
| Unchanged I3 and shared-primitive behaviour (§6.9) | `test_i3_verifier.py` in full, including `test_there_is_one_exclusive_link_and_the_fused_publication_uses_it`; `test_lab_implementation.py` |
| Contract encodings | `test_rp11_capture.py::test_an_index_state_refuses_a_gap_and_a_final_state_its_own_shape` (round trip; missing or foreign self-pair; wrong predecessor); `…::test_a_staging_name_is_fixed_by_rule_and_names_only_its_own_object`; `…::test_a_name_in_two_categories_is_refused_when_r_is_formed` |

**No focused test skips.** No test depends on a publication feature being
present or absent.

**Mutation check.** Each mutation was applied, both RP-11 suites were run, and
the file was restored and verified by SHA-256. Killed:

* an accepted third link;
* the content check dropped;
* the staging name unlinked after publish;
* admission marking dropped;
* unadmitted divergence accepted;
* the alias partner check dropped (after adding
  `…two_accounted_names_that_are_not_partners…`).

**One survives by design.** The admitted-pair `pair-link-count` check cannot
fire first: when both names sit on the recorded inode the count is at least
two, and more than two is refused during enumeration. It is kept as defence in
depth.

## 7. Interruption-state evidence

The store's `PublicationState` makes the draft's six §9.5.1 states explicit.
The test `…every_publication_interruption_leaves_its_exact_classified_state`
asserts each state from memory and from the files on disk:

| Interrupted or failed stage | State | Names on disk |
|---|---|---|
| `create` | `no-staging-entry` | none |
| `verify`, `write`, `verify-content`, `file-barrier`, `publish` | `staging-without-confirmed-final-link` | staging |
| `publish` (effect then error, positively probed) | `both-names-before-directory-barrier` | staging + final |
| `directory-barrier` | `both-names-before-directory-barrier` | staging + final |
| `verify-pair` | `both-names-after-barrier-unverified` | staging + final |
| `close` | `both-names-verified-not-admitted` | staging + final |
| next state durable | `both-names-admitted` | staging + final |

After an interruption:

* no filesystem call is made, not even a close;
* `complete`, `stop` and `run_act` refuse;
* no X-3 is attempted and no final name exists; and
* every pre-existing object is byte-for-byte unchanged.

## 8. Commands and results

**Environment.** Interpreter `/opt/freedom-blades/runtime/venv-web/bin/python`
(CPython 3.12.3), Linux 6.8.0-139-generic, repository host only, pytest
temporary directories only.

**Prefix.** Every command below ran serially with this prefix:
`env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 … -m pytest -q -rs -p no:cacheprovider`.

| # | Selection | Result |
|---|---|---|
| 0 | `test_rp11_capture.py test_rp11_retention.py`, **before any edit** | 267 passed, 0 skipped |
| 1 | `test_rp11_capture.py` (final tree) | **264 passed, 0 skipped** |
| 2 | `test_rp11_retention.py` (final tree) | **103 passed, 0 skipped** |
| 3 | 1 + 2 together | **367 passed, 0 skipped** |
| 4 | the I1 focused selection: the RP-11 suites plus `test_no_execution`, `test_concrete_plan`, `test_r16_remediation`, `test_i3_verifier`, `test_boundary_identity`, `test_lab_integration`, `test_v6_provisioning`, `test_lab_implementation` and `test_r5_r4_s4_3_producer_reporting` | **1270 passed, 0 skipped** |
| 5 | `tests/phase_5_0_evidence` (the whole package directory) | **3320 passed, 0 skipped** |
| 6 | `-m tools.phase_5_0_evidence.execution.cli --manifest-out … --render …` (dry run, twice; the second run on the final source) | `DRY RUN — nothing was executed.`; 138 steps, 43 mutations, 47 cleanup steps, 4 unresolved (C-7, C-S4-3); twelve unconfirmed facts; `review manifest digest: 264674da…`; `executable : False` |

* **Item 2 of the assignment's §8.** The replacement/current publication
  diagnostic tests are the §6 publication tests in `test_rp11_capture.py`.
  The old diagnostic module was removed as obsolete.
* **Warnings.** Each pytest run printed only pytest's two "Unknown config
  option" warnings (the asyncio options in the shared `pytest.ini`).
* **Other checks.** `git diff --check` (scoped to the changed paths) was clean.
  `compileall` of the package was clean.
* **Digests.** Every digest in §2 was recomputed with `sha256sum` after the
  final edit.
* **Links.** The links in this handback and in the new draft header resolve to
  existing files.

## 9. Manifest and artifact effects

* **Version.** `MANIFEST_VERSION` moves 22 → 23, with a docstring reason:
  * five covered files change;
  * the covered set does not;
  * no vector, step, mutation, expectation, target fact, required case or
    unresolved entry changes;
  * all schema and verb-table versions are unchanged.

  The pin in `test_r16_remediation.py` moves to 23.
* **Generated diffs.** The artifact diffs are exactly the version, six covered
  source digests and the review digest line.
* **Digest.** The new review-input digest is `264674da…`. It replaces
  `adeabe17…` **as review input only**. It is not an approval and must never
  be supplied to `--execute`.

## 10. Unwired confirmation

* Nothing outside `tests/` constructs a session or arms `StreamCaptureLauncher`
  (`test_nothing_outside_tests_arms_the_launcher_or_creates_a_session`).
* `execution/cli.py` names no RP-11 module.
* The dry run executed nothing and reports `executable : False`.

## 11. Implications, security and operations

* **Security.**
  * Publication is exclusive at both names and never follows a link.
  * The staging creation uses `O_NOFOLLOW|O_EXCL`; the final link fixes
    `follow_symlinks=False` and relies on the kernel's `EEXIST`.
  * Nothing in RP-11 removes a name, so the I1-R2 recheck-to-unlink race no
    longer exists.
  * The procfs dependency that failed in Codex's context is gone.
* **One inode, two names.** This is by design. It costs one extra directory
  entry per record and state; the data is not duplicated.
* **Recorded identity (`st_dev`, `st_ino`).** B0-RA compares the device and
  inode recorded in Pass A's durable state.
  * **A change of `st_dev` between Pass A and B0-RA stops Pass B,
    fail-closed.** It could come from a re-mount, a device renumbering, or a
    repository-host reboot on some storage stacks.
  * This is stricter than R5, not weaker. It should be weighed when the
    capture-root filesystem is chosen.
* **Deployment, configuration, migration.** None. There is no database, no
  migration and no configuration change.
* **Rollback.** Revert the listed files. There is nothing operational to roll
  back.
* **Not established.** It is not established that the route works on the
  repository-host runtime that will operate the passes. Each pass's X-1
  decides that, fail-closed. The local runs establish behaviour on this host
  only.

## 12. Checks not run, and why

* **Not authorized by the assignment:**
  * the full bot and web suites;
  * `oracle-test`, SSH and synchronization;
  * any database;
  * crash or power-loss testing;
  * a real capture root;
  * a secrets scan.
* **Not configured:** a formatter, linter or type checker. `ruff` and `mypy`
  are not installed in the interpreter.
* **Not re-run:** the removed I1-R2 diagnostic. It depends on the deleted
  route.

## 13. Git status

* Working-tree changes as in §2, plus the pre-existing unrelated modified and
  untracked documents, which were preserved.
* No commit, no push, no history operation.

## 14. Unresolved questions

1. **Confirmation of the §4 decision** as the decision of record.
2. **C-11**: how the §5 synchronization is issued through the mechanism
   without changing what `guard-secrets.py` inspects. Unchanged, and still a
   blocker.
3. **The launcher environment.** Unchanged, and still a blocker.
4. **`st_dev` stability** of the chosen capture-root filesystem across the
   interval between Pass A and B0-RA (§11).

## 15. Independent-review focus

* The draft's coherence. Every §9.5.1 state, stop, X-4 and B0-RA statement
  should agree with every other, and nothing should be weakened in R5.
* Whether admission of index states works:
  * each state by its successor's predecessor link; and
  * *F* by its self-recorded pair, embedded through the content callback
    before *F*'s bytes are written.
* Whether the §4 unadmitted-pair exception is bounded as stated.
* That `_aliases` and `_admitted_pairs` refuse every third link, cross-object
  alias, missing member and identity drift, including links from outside the
  root.
* The unchanged I3 contract, and the removal of the follow parameter from the
  shared link site.
* That the X-1 genesis publication really is the capability test, with no
  path to a host command on failure.
* Reproduce §8 in the review context. The route no longer depends on procfs,
  so RP11-I1-2's `ENOENT` should not recur. **This is expected, not
  established.**

**Stopped.** No further work proceeds without independent Codex review and a
maintainer decision.
