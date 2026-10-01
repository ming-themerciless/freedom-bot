# Claude handback — C-P5.0-R5-RP11-I1 — RP-11 capture mechanism and B0-RA retention verification — 2026-09-28

Assignment:
[`phase-5-0-p5-r5-rp11-capture-mechanism-implementation-claude-prompt.md`](phase-5-0-p5-r5-rp11-capture-mechanism-implementation-claude-prompt.md).
Controlling requirements: the R5-amended
[operational-evidence draft](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md),
SHA-256 `5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3`,
§§4.4 RP-11, 7.1 B0-RA, 9.1, 9.4, 9.5 (C-1 … C-15, P-1 … P-8, X-1 … X-4), 10,
11 and 14. The draft was verified at that digest and was **not amended**.

## 1. Outcome

RP-11's client-side capture mechanism and B0-RA's read-only retention check are
implemented in repository source, with focused local tests. They are **not wired
to any command**, and nothing outside `tests/` constructs an armed launcher or a
capture session. **RP-11 is not satisfied**: it has had no independent review, the
digest in `PIN.capture_tool_sha256` has not been computed from reviewed bytes,
and the open questions in §8 remain.

Neither pass is accepted, executable or authorized. P5.0-R5 remains
**Blocking**, OD-62 G-A remains conditional, `plan.is_executable=False`, and
Package 5.0 remains not ready. No SSH, rsync, network access, host inspection,
`sudo`, database access, verifier, evidence band, harness `--execute`, real
capture root, protected `/tmp` artifact access, secrets scan, guard or hook
change, commit or push was performed by Claude. No guard refused a call.

## 2. Maintainer decisions made during the pass

Three points could not be met literally with the permitted primitives. The
prompt says not to choose silently, so Claude asked Peter Duscha in the
session. He decided each one on 2026-09-27. They are **deviations for Codex to
review**, not amendments of the draft.

1. **P-7 publication primitive — `O_TMPFILE` + `linkat`.**
   * **The constraint.** Python 3.12's `os` module has no `RENAME_NOREPLACE`,
     and `ctypes` is structurally refused outside `case_program.py`.
   * **The mechanism.** A record or index state is written into an *unnamed*
     `O_TMPFILE` inode in its destination directory, and file-synchronized.
     One `linkat` through `/proc/self/fd/N` (`AT_SYMLINK_FOLLOW`) then gives it
     its first and only name, followed by a directory barrier.
   * **What is kept.** Every semantic P-5 … P-8 names: the publication is
     complete or absent, it never replaces an entry (the kernel's `EEXIST`),
     and it can never be mistaken for a published file.
   * **What departs.** P-5's "temporary name" becomes an inode with no name,
     and P-7's "rename" becomes a link. A failure before the link leaves no
     directory entry at all.
2. **Read-only after X-3 is a behavioural seal.** The session enters a terminal
   state in which every writing call refuses, and it releases its descriptors.
   No `chmod` is issued. That keeps C-7's `0700`/`0600` modes and X-3's "only
   permitted write", and it applies equally after an interruption.
3. **The package's one `os.link` call site is shared.** The structural test
   `test_i3_verifier.py::test_there_is_one_exclusive_link_and_the_fused_publication_uses_it`
   allows exactly one `os.link` call in the package.
   * That call moved into the private helper `descriptors._exclusive_link`.
   * `PosixFilesystem.linkat` calls it with `follow=False`, so its behaviour,
     flags and no-follow guarantee are unchanged.
   * The new `link_unnamed_descriptor` calls it with `follow=True`, only for
     `/proc/self/fd/N`. It refuses a descriptor whose inode already has a name
     (`st_nlink != 0`), so it can never create a hard-link alias.
   * `EXCLUSIVE_LINK_PRIMITIVE` is amended to state this, and
     `UNNAMED_PUBLICATION` is added. The guard test is **unmodified** and
     passes. **This changes a reviewed I3 primitive's stated contract.**

## 3. Architecture and interfaces

The responsibilities are split as the assignment asked: process execution,
durable storage, index validation and retention verification.

| Module | Tier | Responsibility |
|---|---|---|
| `tools/phase_5_0_evidence/capture_contract.py` | planning (no I/O) | The fixed layout and name rules. The byte-safe `RelativeName`. Canonical JSON with a single accepted encoding. The `CaptureRecord` and `IndexState` schemas and their validation. The accounted set *R* (`accounted_objects`). The handback binding block (`HandbackBinding`, `parse_handback_binding`). The capture-root grammar. `capture_tool_sha256` over `RP11_SOURCES` |
| `execution/boundary.py` → `StreamCaptureLauncher` | execution | The only process start: one exact argv, `shell=False` as a literal, `argv[0]` absolute, `stdin=/dev/null`, `cwd=/`, an explicit environment with nothing inherited, and two pipes copied as raw bytes into two caller-supplied sinks. A per-stream bound is enforced by killing the child, while every delivered byte is still written, so nothing is truncated. A drain limit applies after exit. Unarmed by default. It lives here because `boundary.py` is the one module the structural guard allows to import `subprocess` |
| `execution/capture_store.py` | execution | The narrow `CaptureFilesystem` seam, every call labelled with its contract stage. `PosixCaptureFilesystem`. `RootPolicy`. `CaptureRootStore`: X-1's no-follow ancestor walk, forbidden-location checks by name and by identity, exclusive creation, mode checks, stream-file creation and completion (P-1 … P-4), unnamed-file publication (P-5 … P-8, X-1 genesis, X-2, X-3), and tracking of the names it knows exist. `StoreFailure`; `CaptureInterrupted` (a `BaseException`) |
| `execution/capture_mechanism.py` | execution | `create_capture_session` (X-1) and `CaptureSession`: `run_act` (P-1 … P-8 then X-2), `complete()`, `stop(reason=…)`, the single `_stop_transition`, the one-shot `_finalize_once`, the seal, X-4 via `verify_final_state`, and `binding()` for the handback. `ACT_STAGES` enumerates every act stage |
| `execution/retention_check.py` | execution, read-only | `ReadOnlyFilesystem` has no writing operation. `PosixReadOnlyFilesystem` opens everything `O_RDONLY`. `verify_final_state` is X-4. `RetentionCheck` is B0-RA: one-shot, the handback authenticated by SHA-256, fixed fields only, byte-for-byte root equality, then X-4 plus the bidirectional comparison |

**Layout under a capture root.** Every name comes from one fixed rule:

* the subdirectories `index`, `records`, `streams`, `streams/stdout` and
  `streams/stderr`, all created in X-1 before the genesis state, each followed by
  a directory barrier on its container;
* `streams/{stdout,stderr}/NNNNNN` for each act's two stream files;
* `records/NNNNNN.json` for each per-act record;
* `index/NNNNNN.open.json` for an open state (genesis is `000000`);
* `index/NNNNNN.final.json` for the final state *F*, whose number is the last
  open state's number plus one.

**Byte-safe name representation.** A relative name is the tuple of its
raw-byte components. Two names are the same name exactly when those tuples are
equal: there is no decoding, case folding, Unicode or path normalization.

* A component that is empty, `.` or `..`, or that contains `/` or NUL, is
  refused.
* Every name the mechanism creates is ASCII in a fixed lowercase grammar, so a
  duplicate or ambiguous encoding is impossible by construction.
* Observed names are displayed with every byte outside 0x21 … 0x7E, and the
  backslash, escaped as `\xHH`. That display form is injective.

**Handback binding.** The §14 prose lines are not parseable, because a path
followed by a full stop is ambiguous. RP-11 therefore fixes one fenced block
that the Pass A handback must carry verbatim:

````text
```rp11-capture-binding
format: rp11-capture-binding/1
pass_id: …
capture_root: …
x3_outcome: succeeded|failed|not-made
x4_validity: valid|inconclusive
final_state: index/NNNNNN.final.json|none
capture_index_sha256: <64 hex>|none
```
````

B0-RA reads this block and nothing else in the handback. The block must occur
exactly once, with its seven keys in this fixed order and nothing extra.

**Stop transition (§9.5.3).** Every stop follows the same order:

1. The session leaves `OPEN` before anything else, so every later `run_act`
   refuses without a filesystem call or a launch.
2. One X-3 attempt is made, and only if the session has a durable genesis state
   and was not interrupted. `_x3_attempted` is set before the attempt's first
   call.
3. The attempt has one outcome, which is recorded.
4. The session is sealed.
5. X-4 is re-applied to the bytes on disk, or is `inconclusive` if X-3 failed
   or was not made. Nothing is reconstructed.

An interruption during X-3 is recorded as the attempt's failure, in memory
only. After an interruption, every call refuses, `complete()` and `stop()`
included. **No function opens an existing root**, so a recovered process cannot
resume, adopt or finalize one.

**What *F* records as unadmitted.** Every name the store knows exists: names it
created, or names positively identified by a no-follow `lstat` after a creating
call failed, when the inode matches where one is known. It excludes the chain,
the admitted records and the streams they bind, and the subdirectories. It
never records a pre-existing object at a name the store was about to create (an
`EEXIST`), which B0-RA then finds unaccounted: the fail-closed direction.

**B0-RA order.**

* **Condition 0:** the handback's SHA-256, then its binding block, pass ID,
  X-3 = succeeded, X-4 = valid, and a final state and digest present.
* **Condition 1:** the supplied root equals the recorded root byte for byte.
* **Condition 2:** the root is walked from `/` one component at a time, no-follow.
* **First complete recursive enumeration.** Each directory's identity,
  modification and change times, and link count are compared before and after
  it is listed. Each subdirectory's `fstat` must equal its `lstat`. A second
  entry with an already-seen identity, a regular file whose link count is not
  1, a different `st_dev`, or an ambiguous listing stops the check.
* ***F* is present.** Its bytes are read bound to the enumerated identity, and
  unchanged before and after the read.
* **Condition 3:** the digest of *F*.
* **Condition 4:** *F* is the only final state; *F* parses and matches its
  binding; the chain is intact back to *I*-0; the records and bound streams have
  their digests; and every published record is accounted for.
* **Condition 5:** *R* is formed, with duplicate categories refused, and
  compared with the enumeration in both directions, including types.
* **Then** a second complete enumeration must equal the first, and the root
  path is re-walked and must still reach the same directory.

Any exception is reported as a `verification-incomplete:*` stop. Unadmitted
objects and recorded subdirectories are established by `lstat` only: they are
never opened, read or digested.

## 4. Requirement-to-test map

The tests are in `tests/phase_5_0_evidence/test_rp11_capture.py` (**C**) and
`test_rp11_retention.py` (**R**); the shared fixtures are in `rp11_fixtures.py`.

| Requirement | Tests |
|---|---|
| C-1 exact argv, no shell | C `test_exact_argv_and_separate_raw_streams_are_captured`, `test_no_shell_interprets_any_element`, `test_the_launcher_is_unarmed_by_default_and_refuses_a_relative_vector`, `test_the_environment_is_exactly_the_one_supplied`, `test_a_malformed_request_stops_the_pass_before_any_file_or_process` |
| C-2 separate, complete streams; bound without truncation | C `test_exact_argv_…` (non-UTF-8, NUL, CR), `test_empty_streams_are_stream_files_with_the_empty_digest`, `test_interleaved_writes_stay_in_their_own_channel`, `test_exceeding_a_bound_stops_the_pass_without_truncating`, `test_a_channel_held_open_past_the_drain_limit_is_an_incomplete_stream` |
| C-3 digests; C-4 time and status | C `test_exact_argv_…` (the digests, the clock source, start before end, exit 7), `test_a_terminating_signal_is_recorded_as_a_signal` |
| C-5 one record per act, gap-free sequence | C `test_three_acts_publish_a_gap_free_chain_and_a_valid_final_state` |
| C-6 one exclusive, distinct root per pass, outside forbidden locations | C `test_the_root_is_created_exclusively_with_the_fixed_layout_and_modes`, `test_an_existing_root_is_refused_and_left_untouched`, `test_a_root_inside_a_forbidden_location_is_refused_before_creation`, `test_a_forbidden_location_is_also_refused_by_identity`, `test_a_symbolic_link_anywhere_on_the_root_path_is_refused`, `test_pass_a_and_pass_b_roots_are_independent_and_never_nested` |
| C-7 modes and immutability; P-7 never replaces | C `test_the_root_is_created_…`, `test_three_acts_…` (every file `0600`, link count 1), `test_a_published_name_is_never_replaced`, `test_the_unnamed_link_refuses_an_inode_that_already_has_a_name`, `test_a_real_linkat_through_the_shared_site_still_refuses_to_replace` |
| C-10, C-13, P-1 … P-8, X-2: every close, digest, file barrier, directory barrier, publication and index-advance stage failed | C `test_the_suites_act_stage_list_is_complete`; `test_every_act_stage_fails_closed_once_with_the_correct_final_state`, parametrized over all 34 `ACT_STAGES` plus three "error after effect" cases. It asserts the stage reached once (no retry), no next launch, later `run_act` and `complete()` refused (no next command), stream bytes unchanged (no repair), *F*'s records and **exact unadmitted set**, X-3 succeeded, X-4 valid, and B0-RA admitting the resulting root |
| C-14, X-1 | C `test_x1_has_the_stages_the_suite_fails`, `test_the_suites_x1_stage_list_is_complete`, `test_a_failed_x1_stage_leaves_no_genesis_and_no_x3` (all 16 X-1 stages) |
| C-15 interruption before and after a durable genesis, and at every X-3 stage | C `test_an_interruption_during_x1_makes_no_further_call` (16), `test_an_interruption_at_any_act_stage_ends_the_pass_with_no_x3` (34), `test_an_interruption_during_x3_is_its_failure_and_nothing_follows` (7), `test_there_is_no_way_to_resume_or_finalize_an_existing_root` |
| X-3 one attempt, one outcome, then read-only | C `test_a_failed_x3_attempt_is_recorded_not_retried_and_x4_is_inconclusive` (7 stages; earlier objects byte-identical; at most *F* created), `test_an_operator_stop_is_one_transition_and_seals_the_session` |
| B0-RA condition 0: handback | R `test_a_tampered_handback_stops`, `test_a_handback_that_records_no_admissible_final_state_stops` (6 variants), `test_a_handback_without_or_with_two_binding_blocks_stops`; C `test_the_binding_block_round_trips_…`, `test_the_binding_block_refuses_every_other_shape` |
| Condition 1: root equality | R `test_a_supplied_root_that_is_not_byte_for_byte_the_record_stops` (4 variants) |
| Condition 2: presence | R `test_an_absent_root_stops_at_presence`, `test_an_absent_final_state_stops` |
| Condition 3: stale digest | R `test_a_stale_capture_index_digest_stops` |
| Condition 4: X-4 | R `test_a_second_final_state_stops`, `test_a_broken_chain_stops`, `test_a_missing_chain_state_stops`, `test_a_forged_final_state_with_a_record_gap_stops`, `test_a_forged_final_state_that_disagrees_with_its_chain_stops`, `test_a_missing_or_changed_record_or_stream_stops` (4), `test_an_unexpected_published_record_stops` |
| Condition 5: both name-set differences at every depth | R `test_an_observed_name_not_recorded_stops_at_any_depth` (5), `test_a_name_nested_inside_an_unexpected_directory_is_reported_by_its_full_path`, `test_a_deleted_unadmitted_object_stops` (2), `test_a_deleted_recorded_subdirectory_stops` |
| Every type mismatch; unsupported types | R `test_every_type_mismatch_stops_and_nothing_is_followed` (regular → directory, symlink or FIFO; admitted record → symlink), `test_an_empty_recorded_subdirectory_replaced_by_a_file_is_a_type_mismatch`, `test_an_unsupported_object_type_is_never_accounted` |
| Duplicate category; ambiguous encoding; traversal | R `test_a_duplicate_category_in_a_forged_final_state_stops`, `test_names_are_compared_as_raw_bytes_without_normalization`, `test_an_ambiguous_listing_stops` (4), `test_a_traversing_or_non_canonical_recorded_name_is_refused` (4); C `test_a_relative_name_refuses_every_ambiguous_component`, `test_a_created_name_has_one_spelling`, `test_the_display_form_is_injective_over_raw_bytes`, `test_a_name_in_two_categories_is_refused_when_r_is_formed`, `test_a_capture_root_is_absolute_and_unnormalized` |
| Symbolic links, hard-link aliases, escape | R `test_a_symbolic_link_to_an_admitted_object_is_an_unexpected_name`, `test_a_hard_link_alias_stops` (3), `test_a_hard_link_from_outside_the_root_is_an_alias`, `test_an_entry_on_another_device_escapes_the_root` |
| Incomplete enumeration | R `test_an_incomplete_enumeration_stops` (3) |
| Deleted or replaced unadmitted objects, content not read | R `test_b0_ra_never_opens_an_unadmitted_object` (mode `000`), `test_a_replaced_unadmitted_object_of_the_same_type_passes_and_is_not_read`, `test_a_deleted_unadmitted_object_stops` |
| Races during enumeration and digests | R `test_a_name_added_while_the_root_is_listed_stops`, `test_a_directory_swapped_between_lstat_and_open_stops`, `test_an_admitted_file_replaced_after_enumeration_stops`, `test_an_admitted_file_appended_to_while_it_is_read_stops`, `test_a_same_size_rewrite_while_an_admitted_file_is_read_stops`, `test_a_name_added_after_every_digest_is_caught_by_the_second_enumeration`, `test_a_root_replaced_during_verification_stops` |
| Non-mutating and one-shot | R `test_b0_ra_passes_on_an_intact_root_and_changes_nothing` (full no-follow snapshot before and after, and exactly which files were opened), `test_b0_ra_runs_once`, `test_the_verifier_module_cannot_write` (syntax tree: no mutating `os` call, no `open()`, no write/create flag, no import of the store) |
| Structural no-execution and no-network | C `test_the_rp11_modules_are_inert_on_import_and_have_no_entry_point`, `test_nothing_outside_tests_arms_the_launcher_or_creates_a_session`, `test_the_harness_cli_does_not_reach_the_capture_mechanism`, `test_the_package_still_has_one_link_call_and_linkat_does_not_follow`; the existing `test_no_execution.py` scans, with the new modules declared in their tiers and no rule relaxed |
| `PIN.capture_tool_sha256` input | C `test_the_tool_digest_covers_exactly_the_rp11_sources` |

**Mutation check.** Each of the following deliberate source mutations was run
against the suites and then reverted, with the revert verified by SHA-256.
Every one made tests fail:

* no post-failure probe;
* *F* without unadmitted objects;
* stdout and stderr merged;
* a barrier retried;
* the comparison in one direction only;
* no second enumeration;
* no link-count check;
* no after-read `fstat`.

The last two survived at first and needed the two tests added for them: the
outside hard link and the same-size rewrite.

## 5. Validation

The focused RP-11 suites and the directly affected structural suites, run
serially:

```bash
env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 \
  /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p no:cacheprovider \
  tests/phase_5_0_evidence/test_rp11_capture.py tests/phase_5_0_evidence/test_rp11_retention.py \
  tests/phase_5_0_evidence/test_no_execution.py tests/phase_5_0_evidence/test_concrete_plan.py \
  tests/phase_5_0_evidence/test_r16_remediation.py tests/phase_5_0_evidence/test_i3_verifier.py \
  tests/phase_5_0_evidence/test_boundary_identity.py tests/phase_5_0_evidence/test_lab_integration.py \
  tests/phase_5_0_evidence/test_v6_provisioning.py tests/phase_5_0_evidence/test_lab_implementation.py \
  tests/phase_5_0_evidence/test_r5_r4_s4_3_producer_reporting.py
```

Result: **1170 passed, 0 failed, 0 skipped.** The RP-11 suites alone: 196 + 71
passed, 0 skipped. `TEST_DATABASE_URL` was explicitly unset, and no test here
consults it. The only warnings were pytest's two "Unknown config option"
warnings (the asyncio options from `pytest.ini`, which is shared with the web
suite).

`git diff --check` on the task files was clean.

## 6. Manifest effects

* `review_manifest.COVERED_SOURCES` gains four files: `capture_contract.py`,
  `execution/capture_store.py`, `execution/capture_mechanism.py` and
  `execution/retention_check.py`. The covered set grows from 48 to 52.
  `test_the_covered_sources_are_exactly_the_package` requires every package
  module to be covered.
* `MANIFEST_VERSION` moves **21 → 22**, with a docstring entry. The pin in
  `test_r16_remediation.py` was updated to 22.
* Both generated artifacts were regenerated with the default dry run, which
  printed `DRY RUN — nothing was executed.` and `executable : False`:
  `… -m tools.phase_5_0_evidence.execution.cli --manifest-out docs/review/phase-5-0-evidence-harness-review-manifest.json --render docs/review/phase-5-0-evidence-harness-concrete-plan.md`.
  * `docs/review/phase-5-0-evidence-harness-review-manifest.json`: SHA-256
    `3c3a6d79d70989c3180992db9cd2a50d984c171c3bfb3a244b7cc09cc94cff57`.
  * `docs/review/phase-5-0-evidence-harness-concrete-plan.md`: SHA-256
    `4fc2e9e99e9405d995b78bb57780027b35badf916c3c6257d3a329c41d39a618`.
  * New review-input digest:
    `adeabe172a89c181a397a7df62cb46895b7b864975a18b70bb278d9d2a1f7de3`.
    It replaces `ac5ffb3c…` as review input only. **It is not an approval.**
    The draft's `PIN.reviewed_digest` and `PIN.manifest_json_sha256` are
    therefore stale, and a later amended draft must re-pin them.
* No vector, step, mutation, expectation, target fact, required case or
  unresolved entry changed. The dry-run figures are unchanged: 138 steps, 43
  mutations, 47 cleanup steps, 4 unresolved conflicts (C-7, C-S4-3), twelve
  unconfirmed facts.

## 7. Files changed

**New:**

* `tools/phase_5_0_evidence/capture_contract.py`
* `tools/phase_5_0_evidence/execution/capture_store.py`
* `tools/phase_5_0_evidence/execution/capture_mechanism.py`
* `tools/phase_5_0_evidence/execution/retention_check.py`
* `tests/phase_5_0_evidence/rp11_fixtures.py`
* `tests/phase_5_0_evidence/test_rp11_capture.py`
* `tests/phase_5_0_evidence/test_rp11_retention.py`
* this handback

**Changed:**

* `tools/phase_5_0_evidence/execution/boundary.py`: `StreamCaptureLauncher`
  and a docstring section.
* `tools/phase_5_0_evidence/execution/descriptors.py`: `_exclusive_link`,
  `link_unnamed_descriptor`, `UNNAMED_PUBLICATION`, and the amended
  `EXCLUSIVE_LINK_PRIMITIVE`.
* `tools/phase_5_0_evidence/review_manifest.py`
* `tests/phase_5_0_evidence/test_no_execution.py`: tier declarations only.
* `tests/phase_5_0_evidence/test_r16_remediation.py`: the version pin.
* The two generated review artifacts.
* The pointer updates on return: `docs/review/Handover information`,
  `docs/project-management/status.md`, `docs/implementation-plan.md` §20, and
  the first restriction banner of `docs/operations/disposable-test-server.md`.

## 8. Unresolved questions

1. **C-11, how the §5 synchronization is issued.** Unresolved. No entry point
   exists. `guard-secrets.py` exempts only a command that is exactly one plain
   `rsync` invocation, so any wrapper that carries the §5 text through RP-11
   would be *refused*, not hidden from the guard. It fails closed, but the pass
   cannot proceed either. Reshaping the command to pass the guard would be a
   bypass and was not attempted. A maintainer and reviewer decision is needed.
2. **The launcher environment.** The launcher inherits nothing. Which exact
   environment the operational `ssh`/`rsync` invocations receive (for example
   `HOME` or `SSH_AUTH_SOCK`) is undecided and must be fixed before any wiring.
3. **The binding block and §14.** The fixed block must be pinned into the
   draft's §14 handback template and into `MI.pass_a_handback`'s definition.
   That is a draft amendment, which this pass does not make.
4. **The three decisions in §2** need Codex's review, especially the
   `O_TMPFILE` deviation from the P-5/P-7 wording and the change to the I3
   link primitive.
5. **A foreign object at a reserved name is never recorded in *F*.** B0-RA
   will then stop on it. That is fail-closed, but it means a Pass A that
   stopped on `publication-exists` can never admit Pass B.
6. **Metadata is not verified.** B0-RA establishes bytes for admitted objects
   and presence, name and type for unadmitted ones and subdirectories. It does
   not verify owner or mode. That matches the draft, whose R5 handback noted it
   as point 5.
7. **The tool digest** (`capture_tool_sha256`) covers `RP11_SOURCES`, which
   includes the whole of `boundary.py` and `descriptors.py`. Whether the pin
   should cover narrower units is a review question.

## 9. Platform assumptions and residuals

* Linux, with `O_TMPFILE` support on the capture-root filesystem (ext4, xfs,
  btrfs and tmpfs have it) and a mounted `/proc`. `linkat` through
  `/proc/self/fd` with `AT_SYMLINK_FOLLOW` is used for unprivileged linking.
  This was confirmed locally on ext4 (`/tmp`).
* `fsync` on a directory descriptor opened `O_RDONLY` is the directory barrier,
  and `fsync` on a read-only file descriptor is the file barrier. Whether the
  accepted repository-host filesystem honours these as crash barriers is an
  RP-11 review and acceptance item (`MI.capture_root_*` "on a filesystem
  RP-11's review has accepted"). **No crash or power-loss test was run.**
* Change detection relies on the kernel updating `st_ctime` on every content,
  name and link change, on timestamp granularity finer than the changes it must
  distinguish, and on the `0700` root being writable only by the operator's
  account and root. Retention is established at the moment of the check only.
* The mode checks assume the operator's umask does not remove owner bits. A
  deviating mode refuses; it is not repaired.
* The capture-root grammar is `[A-Za-z0-9_-][A-Za-z0-9._-]*` per component, so
  a root under a dot-directory is refused.
* Local environment: uid 1000, umask 0002, Python 3.12.3 from
  `/opt/freedom-blades/runtime/venv-web`. Tests launch only the current
  interpreter with `-I -S` and inert inline programs, through the reviewed
  launcher. This differs from the harness suite's earlier "no test starts a
  process" premise, and the prompt permits it.

## 10. Checks not run

* The full test suites (bot and web), and anything on `oracle-test`: excluded
  by the assignment.
* Formatter, linter and type checker: none is configured for this package.
* A crash or power-loss durability test of the barriers.
* A secrets scan: prohibited.

## 11. Git status

At the end of the pass, the maintainer's Git identity committed the whole
working tree, including the RP-11 work, as `c9ee66d` on `docs/platform-plan`
("feat: add phase 5.0 evidence harness execution tools, tests, and review
documentation"). **Claude made no commit and no push.** The committed RP-11
source and tests are the bytes tested above. The later edits to this handback
and to the pointer documents are uncommitted on top of `c9ee66d`. Nothing
unrelated was modified.

## 12. Proposed review focus

* The publication and link decisions (§2).
* Whether B0-RA's descriptor-relative walk and two-enumeration stability check
  satisfy "stable identity and completeness".
* The unadmitted-set rule and the probe.
* The launcher's bound and drain behaviour.
* C-11.
* The binding-block format.

Independent Codex technical, security, operational and evidence review is
required. Claude has stopped.
