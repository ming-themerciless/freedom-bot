# Claude handback — C-P5.0-R5-RP11-I1-R2 — capability-prototype evidence remediation — 2026-09-28

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r2-capability-prototype-evidence-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r2-capability-prototype-evidence-remediation-claude-prompt.md).
Controlling review:
[`project-review-2026-09-28-p5-r5-rp11-i1-r1.md`](project-review-2026-09-28-p5-r5-rp11-i1-r1.md)
(RP11-I1-R1-1, Important).
Historical evidence narrowed by the erratum in §2, and not edited:
[I1-R1 handback](phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-handback.md).

**Assignment basis.** The prompt is marked *draft* and takes effect "only after
the maintainer assigns it". No handover record assigned it. Peter Duscha
instructed Claude directly in this session to carry it out, and this pass
proceeded on that instruction. The maintainer should confirm that the
instruction is the assignment of record.

## 1. Outcome

* **Option 1 of the review.** The prototype and its tests now exercise every
  locally testable step of the proposed §9.5.4 check. §9.5.4 was not
  weakened.
* **The prototype, `probe_unnamed_publication(probe, container)`.** It performs
  the ten steps of assignment §3 once each, in order. The order is recorded
  and asserted. The steps:
  * reaches both directories from `/` one component at a time, following no
    link;
  * checks owner, exact mode `0700`, emptiness and device equality;
  * checks `/proc/self`;
  * creates the inode through the production `create_unnamed` and verifies it;
  * writes with a checked loop and verifies the size;
  * links through the production `link_unnamed_descriptor`;
  * reads the name back, comparing identity, metadata and exact bytes;
  * rechecks identity;
  * only then removes the one fixed name and proves the directory empty.
* **Result in this execution context.** The complete check **succeeds** and
  leaves the probe directory empty. The non-linkable route still fails with
  **`unnamed-link:ENOENT`** and leaves no entry.
* **Tests.** The diagnostic module is **30 passed, 0 failed, 0 skipped**, and
  the directly affected selection is **1200 passed, 0 failed, 0 skipped**.
* **No other file changed in substance.** The amended operational draft is
  unchanged at `186ff546…`, and no wording contradiction required editing it.
  Production source, the review manifest and generated artifacts are
  unchanged. Only the diagnostic module and the documentation listed in §3
  changed.

**RP11-I1-R1-1 remains Open, Important,** and **RP11-I1-2 remains Open,
Blocking**. Both stay open until independent Codex review and explicit
maintainer acceptance. The requirements amendment and the implementation
remain unaccepted, and RP-11 remains unmet. Neither pass is executable or
authorized. P5.0-R5 remains Blocking, OD-62 G-A remains conditional,
`plan.is_executable=False`, and Package 5.0 remains not ready.

None of the following occurred: SSH, rsync, network access, host inspection,
`sudo`, database access, verifier, evidence band, harness `--execute`, a real
participant, a real capture root, an operational probe path, a protected `/tmp`
artifact, a secrets scan, a guard or hook change, a commit or a push. No guard
refused a call.

## 2. Erratum to the I1-R1 handback — dated 2026-09-28

The I1-R1 handback (SHA-256
`a2dfe6eb329768b9b89284dae335b15049a5b23e9be6762d8a82f5af3cb8dd5d`, unchanged
by this pass) is durable history. This erratum narrows or supersedes the
following claims. Its original context-specific figures are preserved as
stated there, and are not re-asserted for the new bytes.

| I1-R1 location | Original claim | Correction |
|---|---|---|
| §4.3 item 6, heading | "**The capability-check prototype works.**" | **Narrowed.** For the I1-R1 bytes (`1f029491…`), the code demonstrated only the unnamed-inode link route and a cleanup skeleton, **not the proposed §9.5.4 check as a whole**. It did not check the probe directory's owner, mode or device. It did not compare the device with the capture root's container. It wrote once with a bare `os.write()`, without proving a complete payload. It never opened or read the published name. It unlinked the name without verifying its bytes. **Superseded** by the I1-R2 prototype (§4) |
| §4.3 item 6, first bullet | "succeeds and leaves the directory empty" | True as an observation of that skeleton in that context. It is **not** evidence that the full check succeeds. For the full check see §6, row 1 |
| §4.3 item 6, second and third bullets | the forced non-linkable case fails `unnamed-link:ENOENT` before any entry exists; a non-empty directory is refused without touching the occupant | **Preserved.** Both are re-established through the complete check by the renamed tests in the next row. The refusal code is unchanged |
| §2 table, diagnostic row; §4.2 rows 2, 3, 4 and 6 | the module has "10 tests" at `1f029491…`; 10 passed three times, and 1180 passed for the focused selection plus the module | **Preserved** as figures for the I1-R1 bytes and Claude's context only. The current bytes have 30 tests (§3) and the results in §6. Codex's independent run of the I1-R1 bytes gave **8 passed, 2 failed, 0 skipped**. That result also belongs to those bytes and remains the independent reference for them |
| §4.5, final paragraph | "rerun `test_rp11_publication_portability.py` … `test_the_platform_facts_…`, `test_a_non_linkable_…`, `test_the_production_route_…`" | **Still valid.** Those three tests are unchanged. The old prototype tests were renamed: `test_the_capability_probe_succeeds_here_and_leaves_the_directory_empty` → `test_the_complete_check_succeeds_here_in_order_and_leaves_the_directory_empty`; `test_the_capability_probe_fails_closed_before_any_entry_when_naming_is_impossible` → `test_the_non_linkable_route_still_fails_with_enoent_and_leaves_no_entry`; `test_the_capability_probe_refuses_a_directory_that_is_not_empty` → `test_an_occupied_probe_directory_is_refused_and_left_untouched` |
| Module docstring (I1-R1 bytes) | "A prototype … runs the production `link_unnamed_descriptor` once, verifies the result, removes its one probe name and proves the probe directory empty" | **Superseded** by the docstring of the current bytes, which describes the complete check |

The rest of the I1-R1 handback is not affected by this erratum. That covers the
amended draft, the diagnosis of the two `ENOENT` routes, the platform facts and
the unresolved attribution.

## 3. Files changed and SHA-256

| File | Change | SHA-256 |
|---|---|---|
| `tests/phase_5_0_evidence/test_rp11_publication_portability.py` | prototype section replaced; docstring and imports corrected; the six pre-existing diagnostic test functions (seven collected cases) unchanged; 23 new cases | `f2845fd655fcca0029e15e2383018c37d947e505ef079e11b359e4333c446f2a` (was `1f029491…`) |
| this handback | new | not self-digestable; the reviewer derives it |
| `docs/review/Handover information` | current-state pointer on return | see §10 |
| `docs/project-management/status.md` | current-state pointer on return | see §10 |
| `docs/implementation-plan.md` §20 | current-state pointer on return | see §10 |
| `docs/operations/disposable-test-server.md`, first banner | current-state pointer on return | see §10 |

Unchanged, with the SHA-256 re-derived after this pass:

* the amended operational draft
  `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`:
  `186ff546a7f31ccf16461d0d3fec83978af643bd8d2e63dbac2e9dc2f3a2f9c6`;
* the I1-R1 handback: `a2dfe6eb…` (above).

The diagnostic module is test-only, and is not a covered source of the review
manifest.

## 4. The prototype

### 4.1 Inputs and seams

`probe_unnamed_publication(probe_directory, container_directory, *,
operations=PRODUCTION_OPERATIONS, trace=None)`.

* **Explicit inputs only.** The probe directory and the directory that will
  contain the capture root are passed in as paths. The prototype reads no
  configuration and no environment. The expected owner is `os.geteuid()`.
* **`ProbeOperations`.** A frozen dataclass of five narrow seams, each with a
  production default:

  | Seam | Default |
  |---|---|
  | `fstat` | `os.fstat` |
  | `create_unnamed` | the production `PosixCaptureFilesystem.create_unnamed` bound method |
  | `write` | `os.write` |
  | `link` | `descriptors.link_unnamed_descriptor` itself |
  | `read` | `os.read` |

  Tests replace exactly one seam per fault. No production object is
  monkeypatched or edited.
* **Other production calls.** Directory opening
  (`PosixCaptureFilesystem.open_directory`), `fsync` and `open_read` also go
  through the production filesystem object.
* **`trace`.** A test-only list that records each step code as that step
  completes.

### 4.2 Steps (assignment §3 numbering)

| # | Step code | What the prototype does | Refusals (`CapabilityAbsent("<step>:<detail>")`) |
|---|---|---|---|
| 1 | `probe-open` | Checks the path text as given. It must be absolute, with no empty, `.` or `..` component; such a path is **refused, not normalized**. Then it opens `/` and each component with `O_DIRECTORY \| O_NOFOLLOW` through production `open_directory`, and holds the final descriptor. That descriptor, not the path, is used from here on | `path`; the errno of an open (a link gives `ENOTDIR` on Linux, or `ELOOP`) |
| 2 | `probe-verify` | `fstat` of the held descriptor: a directory, `st_uid == geteuid()`, `S_IMODE == 0o700`, and `listdir(fd)` empty | `type`, `owner`, `mode`, `not-empty` |
| 3 | `container-device` | Reaches the container the same way, no-follow from `/`. It must be a directory, and its `st_dev` must equal the probe directory's `st_dev` | `path`, errno, `type`, `device` |
| 4 | `procfs-self` | `readlink("/proc/self") == str(getpid())` | `not-caller`, errno |
| 5 | `unnamed-create` | Production `create_unnamed(dir_fd, 0o600)`. The inode must be regular, owned by the effective user, `S_IMODE == 0o600`, `st_nlink == 0`, and on the probe directory's device. Its `(st_dev, st_ino)` is bound | errno, `type`, `owner`, `mode`, `nlink`, `device` |
| 6 | `payload-write` | A loop that refuses a zero-length write and a count outside `1 … remaining`. Then `fstat(fd).st_size` must equal the payload length (36 bytes, at most 64). Then the file barrier (`fsync`) | `zero-length-write`, `incomplete-write`, `size`, errno |
| 7 | `unnamed-link` | Production `link_unnamed_descriptor(fd, dir_fd, PROBE_NAME)`, then the directory barrier | errno (for example `ENOENT`), `refused` for its `ValueError` |
| 8 | `published-verify` | Opens `PROBE_NAME` relative to the directory descriptor through production `open_read` (`O_NOFOLLOW`). `fstat` of that descriptor must show the bound identity, regular type, the owner, `0600` and `st_nlink == 1`. Then it reads to end of file, bounded at 65 bytes, and requires exact equality with the fixed payload | `identity`, `type`, `owner`, `mode`, `nlink`, `oversize`, `payload`, errno |
| 9 | `cleanup-recheck` | No-follow `stat(PROBE_NAME, dir_fd=…)` immediately before removal. It must show the bound identity and a regular file | `identity`, errno |
| 10 | `cleanup-remove` | `unlink(PROBE_NAME, dir_fd=…)`, the directory barrier, closing both file descriptors, then `listdir(fd)` must be empty. Directory descriptors are closed on exit | errno, `not-empty` |

**Failure behaviour.**

* Every failure raises one `CapabilityAbsent`. There is no retry, fallback,
  repair or second publication route.
* Held descriptors are always closed. Nothing is removed on a failed path, so
  residue — at most the one fixed name — stays for the caller to report.
* The prototype contains no `os.link`, no `/proc/self/fd` and no `O_TMPFILE`
  of its own. A test asserts this.

**Stricter than the minimum, where this directly represents §9.5.4:**

* the component-wise walk from `/`: the draft's "reached from `/` without
  following a symbolic link";
* refusal of an unnormalized path;
* the size check after the write loop;
* the device check of the created inode; and
* the bounded read.

## 5. Requirement-to-test map

All tests are in `tests/phase_5_0_evidence/test_rp11_publication_portability.py`.

### 5.1 Assignment §3 — required prototype behaviour

| Requirement | Test(s) |
|---|---|
| §3.1 open the probe no-follow and bind its descriptor | `test_the_complete_check_succeeds_here_in_order_and_leaves_the_directory_empty` (trace step `probe-open`; directory identity unchanged); `test_a_symbolic_link_on_the_probe_path_is_never_followed[final, intermediate]`; `test_a_probe_path_needing_normalization_is_refused_not_normalized[dot, dotdot, trailing, empty]` |
| §3.2 directory, owner, exact `0700`, empty | `test_a_wrong_probe_owner_refuses_before_unnamed_inode_creation`; `test_a_wrong_probe_mode_refuses_before_unnamed_inode_creation[0750, 0755, 0500, 1700]`; `test_an_occupied_probe_directory_is_refused_and_left_untouched` |
| §3.3 container no-follow, a directory, equal `st_dev` | `test_a_different_container_device_refuses_before_unnamed_inode_creation`; `test_a_container_that_is_not_a_directory_refuses`; trace step `container-device` in the success test |
| §3.4 `/proc/self` is the caller | trace step `procfs-self` in the success test; `test_the_platform_facts_that_decide_the_route_are_recorded`. **No negative test**: the condition cannot be falsified in-process without a seam over `readlink`, and none was added. Recorded in §7 |
| §3.5 production creation; regular, owner, `0600`, `nlink` 0 | `test_success_uses_the_production_creation_and_link_functions`; `test_the_non_linkable_route_still_fails_with_enoent_and_leaves_no_entry` (its inode passes all these checks before the link refuses) |
| §3.6 complete write with a checked loop, then the file barrier | `test_a_partial_write_then_a_zero_length_write_refuses_before_any_entry`; `test_a_write_that_reports_more_than_it_wrote_is_not_taken_as_complete`; `test_a_write_count_larger_than_requested_is_refused` |
| §3.7 production `link_unnamed_descriptor`, then the directory barrier | `test_success_uses_the_production_creation_and_link_functions`; `test_the_non_linkable_route_still_fails_with_enoent_and_leaves_no_entry` |
| §3.8 open no-follow; identity, type, owner, `0600`, `nlink` 1; read all bytes; exact equality | `test_published_bytes_that_differ_from_the_payload_refuse_before_cleanup_and_remain`; the success test |
| §3.9 identity recheck immediately before cleanup | `test_a_name_replaced_before_cleanup_is_refused_and_the_replacement_is_untouched` |
| §3.10 remove the one name, barrier, close, verify empty | the success test (empty directory, trace step `cleanup-remove`) |
| "Once, in order" | the success test asserts `trace == PROBE_STEPS`; the production-functions test asserts `create_unnamed` and `link` are each called exactly once |
| Descriptor-relative operations for the probe name; no `Path.resolve()` or lexical normalization | by construction (§4.2 steps 7–10 use `dir_fd`); the normalization test |
| One fixed refusal, no retry, fallback or repair; residue not removed | every failure test matches one exact `^step:detail$`; the bytes-differ and replacement tests assert that residue remains |
| Not production code or an operational entry point | the module lives under `tests/` only; `git status` shows no change under `tools/` (§9) |

### 5.2 Assignment §4 — required tests

| Required test | Test |
|---|---|
| Successful complete check leaves the directory empty | `test_the_complete_check_succeeds_here_in_order_and_leaves_the_directory_empty` |
| A partial-write seam cannot be mistaken for a complete payload | `test_a_partial_write_then_a_zero_length_write_refuses_before_any_entry` (5 bytes, then 0, gives `payload-write:zero-length-write`; no link attempted; no entry); `test_a_write_that_reports_more_than_it_wrote_is_not_taken_as_complete` (writes 5 bytes but reports all, gives `payload-write:size`; no link; no entry) |
| Wrong owner and wrong mode refuse before inode creation | `test_a_wrong_probe_owner_refuses_before_unnamed_inode_creation` (the `fstat` seam reports `st_uid + 1` for the probe only); `test_a_wrong_probe_mode_refuses_before_unnamed_inode_creation` (real `chmod`). Both assert that `create_unnamed` was never called |
| A different `st_dev` refuses before inode creation, through a narrow seam | `test_a_different_container_device_refuses_before_unnamed_inode_creation` (the `fstat` seam reports `st_dev + 1` for the container only; no mount is needed) |
| An occupied probe directory remains untouched | `test_an_occupied_probe_directory_is_refused_and_left_untouched` (inode, size, `mtime_ns`, link count and bytes unchanged) |
| Different published bytes refuse before cleanup and remain as residue | `test_published_bytes_that_differ_from_the_payload_refuse_before_cleanup_and_remain` (the `write` seam writes a same-length, different payload and reports it truthfully; gives `published-verify:payload`; the name remains with those bytes and link count 1) |
| A name whose identity changes before cleanup refuses; the replacement stays untouched | `test_a_name_replaced_before_cleanup_is_refused_and_the_replacement_is_untouched` (the `read` seam replaces the name at end of file, after the bytes matched; gives `cleanup-recheck:identity`; the replacement's inode and bytes are unchanged) |
| The non-linkable route still gives `ENOENT` and leaves no entry | `test_the_non_linkable_route_still_fails_with_enoent_and_leaves_no_entry` (an `O_EXCL` inode injected at the `create_unnamed` seam; gives `unnamed-link:ENOENT`; the trace stops before `unnamed-link`; the directory is empty) |
| Success uses the production creation and link functions, not copied logic | `test_success_uses_the_production_creation_and_link_functions` (default `link is descriptors.link_unnamed_descriptor`; `create_unnamed.__func__ is PosixCaptureFilesystem.create_unnamed`; a delegating recorder sees exactly `["create_unnamed", "link"]`; the prototype source has no `os.link`, `/proc/self/fd` or `O_TMPFILE`) |

Unchanged from I1-R1, and still collected:

* the platform facts test;
* creation either way (two cases);
* the production route;
* the non-linkable `ENOENT` route;
* the absent magic link; and
* the no-follow `EXDEV` test.

Added: `test_the_probe_payload_is_within_the_proposed_limit`.

## 6. Commands and results

All runs were serial, from `/opt/freedom-blades/platform`, on the final module
bytes (`f2845fd6…`). The pytest prefix `P` was:

```bash
env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 \
  /opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p no:cacheprovider
```

| # | Command | Result |
|---|---|---|
| 1 | `P -rP tests/phase_5_0_evidence/test_rp11_publication_portability.py` | **30 passed, 0 failed, 0 skipped** |
| 2 | `P tests/phase_5_0_evidence/test_rp11_capture.py tests/phase_5_0_evidence/test_rp11_retention.py` | **267 passed, 0 failed, 0 skipped** |
| 3 | `P` with the I1-R1 handback's exact eleven-file selection (`test_rp11_capture`, `test_rp11_retention`, `test_no_execution`, `test_concrete_plan`, `test_r16_remediation`, `test_i3_verifier`, `test_boundary_identity`, `test_lab_integration`, `test_v6_provisioning`, `test_lab_implementation`, `test_r5_r4_s4_3_producer_reporting`) **plus** `test_rp11_publication_portability.py` | **1200 passed, 0 failed, 0 skipped** (1170 + 30) |
| 4 | `env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1 /opt/freedom-blades/runtime/venv-web/bin/python -m tools.phase_5_0_evidence.execution.cli` (dry run; never `--execute`) | `DRY RUN — nothing was executed.`; `review manifest digest: adeabe172a89c181a397a7df62cb46895b7b864975a18b70bb278d9d2a1f7de3`; `executable            : False` |

**Notes on the runs.**

* **Warnings.** Each pytest run printed only pytest's two "Unknown config
  option" warnings, for the asyncio options in the shared `pytest.ini`.
* **Skips.** `-rs` reported no skip reason. No test in these files reads
  `TEST_DATABASE_URL`.
* **One intermediate failure.** Before the final bytes, one intermediate run
  had **1 failed, 28 passed**. The symbolic-link test had expected `ELOOP`, but
  Linux returns `ENOTDIR` for `O_DIRECTORY | O_NOFOLLOW` on a final-component
  link. The test now accepts either errno, and the refusal is unchanged. Every
  figure above comes from the final bytes.

**Recorded facts in this context (`-rP`).**

```text
RP11-PORTABILITY-FACTS PlatformFacts(python='3.12.3', implementation='CPython', kernel_release='6.8.0-139-generic', has_o_tmpfile=True, link_follow_supported=True, link_dir_fd_supported=True, directory_mount=('/', 'ext4'), proc_mount=('/proc', 'proc'), proc_self_is_caller=True)
RP11-PORTABILITY-NOFOLLOW errno=EXDEV
```

### 6.1 Result in this execution context

* **The complete check passes.** It runs in Claude's unsandboxed local session,
  as uid 1000, on ext4 under `/tmp/pytest-of-foundry/…`. It succeeds and leaves
  the probe directory empty.
* **The forced non-linkable route** gives **`unnamed-link:ENOENT`** before any
  entry exists.
* **Expected result in Codex's I1-R1 review context.** On the evidence so far,
  these tests would fail with `unnamed-link:ENOENT`, because that context's
  production link returned `ENOENT`:
  * `test_the_complete_check_succeeds_here_in_order_and_leaves_the_directory_empty`;
  * `test_success_uses_the_production_creation_and_link_functions`;
  * `test_the_production_route_names_a_linkable_unnamed_inode_once`;
  * `test_published_bytes_that_differ_from_the_payload_refuse_before_cleanup_and_remain`;
  * `test_a_name_replaced_before_cleanup_is_refused_and_the_replacement_is_untouched`.

  The last two need a successful link to reach their fault. **That is an
  expected blocker, not a defect.** None of these tests skips, and none
  substitutes another publication method. This is a prediction only; it was
  not observed.

`git diff --check` is not applicable to the untracked module.
`git diff --no-index --check /dev/null <module>` printed no whitespace error;
its exit status 1 reflects only that the files differ. A direct search found no
trailing whitespace and no tab, and the file ends with a newline.

## 7. What the prototype establishes, and what remains unresolved

**Establishes, in this context only.**

* **§9.5.4 is implementable as written.** Every locally testable step can run
  in order, once each: descriptor-relative, no-follow, through the production
  creation and link functions, with a checked write and exact readback. No
  step needs a weaker rule, a fallback or a second link primitive.
* **The prototype refuses the tested faults at the right step.** Each fault
  gives the stated fixed refusal: wrong owner, wrong mode, a different device,
  an occupied directory, a symbolic link on the path, an unnormalized path, a
  partial or misreported write, wrong published bytes, a replaced name and a
  non-linkable inode.
* **Failures before the link leave no entry.** Failures after the link leave
  exactly the one name, which is not removed. Pre-existing objects are never
  touched.
* **No wording contradiction with draft `186ff546…` was found.** The draft
  combines assignment §3 steps 1–3 into its step 1, and places cleanup-time
  closing before the emptiness check. The prototype does the same: it closes
  file descriptors before the emptiness check, and directory descriptors after
  it. The draft was not edited.

**Does not establish, and remains unresolved.**

* **The cause of `ENOENT` in Codex's context (RP11-I1-2).** It remains
  unresolved and Blocking.
* **The selected repository-host runtime and its probe location.** Neither
  was chosen, and no real probe path was used.
* **Owner and device refusals use metadata injected by a seam.** A real
  foreign-owned directory or a real second device was not constructed, which
  would need privilege or a mount.
* **The `/proc/self`-not-caller refusal has no negative test** (§5.1).
* **The window between the step 9 recheck and the step 10 `unlink`.** POSIX
  has no unlink conditioned on identity, so the recheck narrows this window
  but cannot close it. The same limit applies to the draft's step 8, and a
  reviewer should decide whether §9.5.4 must state it.
* **The created inode's mode.** It depends on the process umask
  clearing no bit of `0600`. A umask such as `0277` would make step 5 refuse
  `mode`. That is fail-closed, but the operational umask is not pinned.
* **"Owner" means the effective uid of the probing process.** Whether that is
  "the operator's account" of §4.5 is an operational binding, not tested.
* **Directory `fsync` as a durable barrier.** It is not proved, and no crash
  or power-loss test was run.
* **Same-device equality (`st_dev`).** It is what the draft requires. It does
  not distinguish two mounts of one filesystem.

## 8. Checks not run, and why

* **Full bot and web suites, and anything on `oracle-test`.** Excluded by
  assignment §6 and §7.
* **Formatter, linter and type checker.** None is configured in the
  repository. This is not a pass.
* **A real different-owner or different-device probe.** It would need
  privilege or a mount, and neither is authorized. Seams were used instead
  (§7).
* **A rerun in Codex's context.** It is not observable from here and is
  outside the assignment.
* **Crash and power-loss tests.** Not run.
* **Secrets scan.** Prohibited.
* **`python3 .claude/hooks/test_guards.py`.** No guard or hook was changed.

## 9. Confirmation of unchanged artifacts

* **Production source.** `git diff --stat HEAD -- tools/` is empty, and
  `git status --short --untracked-files=all tools/` is empty. No production
  source was edited or monkeypatched.
* **Review manifest.** It is unchanged. The dry-run digest is still
  `adeabe17…f7de3`.
* **Generated artifacts.** Nothing under `tools/` or any generated-artifact
  path appears in `git status`.
* **Operational draft.** It is unchanged at `186ff546…`.
* **I1-R1 handback.** It is unchanged at `a2dfe6eb…`.

## 10. Git status (task-relevant)

* **Branch.** `docs/platform-plan`, at `c9ee66d`.
* **Before this pass.** The tree already carried the I1-R1 pass's uncommitted
  work, which this pass preserved:
  * the modified draft, the four pointer files and the I1 implementation
    handback;
  * the untracked I1-R1 prompt and handback, the two Codex reviews, this
    pass's prompt, and the diagnostic module.
* **This pass.**
  * modified the untracked diagnostic module;
  * created this handback;
  * updated the four current-state pointer files.
* **Pointer-file digests after this pass's edits.**
  * `docs/review/Handover information`: `fb7d3d6bf8e5171bd27fa64533ad3a12582e60cbfd2a8ebab553a63d71b786c2`
  * `docs/project-management/status.md`: `c82d9efe4df61c5cdab5d12dc25eb075a424f27c3b768b50a1c847e4d6780b1c`
  * `docs/implementation-plan.md`: `e7bfbf8f13a7da578d112a43ce4fc171a5a17687661c43912f4982615b1856be`
  * `docs/operations/disposable-test-server.md`: `8bf40ee38b315e551ced6d5f0b5ef01c7593290dab9edafee98de27edb328531`
* **Relative Markdown links** in this handback and in the new pointer blocks
  resolve.
* No commit and no push.

## 11. Proposed independent-review focus

1. **Faithfulness.** Whether §4.2 exercises each §9.5.4 step, and whether
   anything is stricter than the draft or weaker than it.
2. **Seams.** Whether the injection points are narrow enough. Whether the
   `fstat`-injected owner and device refusals, and the absent `/proc/self`
   negative test, are acceptable evidence.
3. **The recheck-to-unlink window** (§7), and whether §9.5.4 should state it.
4. **The erratum** (§2). Whether it narrows the I1-R1 claims precisely enough
   while preserving their context-specific figures.
5. **Portability.** A rerun of the module in the review context, which is
   expected to fail the five link-dependent tests with `unnamed-link:ENOENT`
   (§6.1). That keeps RP11-I1-2 Blocking.

Independent Codex technical, security, operational and evidence review is
required. **No acceptance record is created.** RP11-I1-R1-1 is not marked
closed. Claude has stopped.
