# Claude handback — C-P5.0-R5-RP11-I1-R1 — publication contract and portability remediation — 2026-09-28

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-claude-prompt.md).
Controlling review:
[`project-review-2026-09-28-p5-r5-rp11-capture-mechanism.md`](project-review-2026-09-28-p5-r5-rp11-capture-mechanism.md)
(RP11-I1-1 and RP11-I1-2, both Blocking).
Accepted requirements baseline, unchanged in authority: the R5 bytes of the
[operational-evidence draft](phase-5-0-p5-r5-operational-evidence-authorization-prompt.md),
SHA-256 `5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3`.

## 1. Outcome

* **Amended draft, for review only.** The operational-evidence draft is
  amended in place. Its new SHA-256 is
  **`186ff546a7f31ccf16461d0d3fec83978af643bd8d2e63dbac2e9dc2f3a2f9c6`**. These
  bytes are **unreviewed and unaccepted**. Until Codex reviews them and Peter
  Duscha accepts these exact bytes, the R5 bytes (`5e06a388…`) remain the
  baseline. No implementation may claim to satisfy the amendment.
* **Diagnosis.** RP11-I1-2 has a mechanism explanation, but its **attribution
  is unresolved**:
  * The same tree, interpreter, kernel and filesystem pass here: **1170
    passed, 0 failed, 0 skipped**.
  * Two distinct kernel-level routes both give Codex's exact `ENOENT`, and
    both were reproduced.
  * I cannot observe which route applied in Codex's context. No record
    describes that context, and inspecting it is outside this assignment.
* **Blocker returned.** The `O_TMPFILE` plus `/proc/self/fd` route cannot be
  **guaranteed** on a repository-host runtime that no one has named. The
  amendment therefore:
  * adds a pre-admission publication capability check (§9.5.4) that must pass
    in the mechanism's own process before X-1; and
  * keeps "the route works in the selected runtime" as an explicit,
    unresolved blocker for both passes.

  No fallback was proposed or implemented.
* **No production source changed.** `git status` shows no change under
  `tools/`. The review manifest, the dry-run digest (`adeabe17…`) and both
  generated artifacts are byte-identical to `c9ee66d`.

**Both findings remain Open.** The implementation remains unaccepted and
unwired, and RP-11 remains unmet. Neither pass is executable or authorized.
P5.0-R5 remains Blocking, OD-62 G-A remains conditional,
`plan.is_executable=False`, and Package 5.0 remains not ready.

No SSH, rsync, network access, host inspection, `sudo`, database access,
verifier, evidence band, harness `--execute`, real participant, real capture
root, operational path, protected `/tmp` artifact, secrets scan, guard or hook
change, commit or push. No guard refused a call.

## 2. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` | amended in place (§3 below). `5e06a388…` → `186ff546…` |
| `tests/phase_5_0_evidence/test_rp11_publication_portability.py` | **new**, diagnostic only, 10 tests. SHA-256 `1f029491b185e1608c98f0054a6ca9b6545a59f40791126480d6ae0c793d192a`. Not a covered source |
| this handback | new |
| `docs/review/Handover information`, `docs/project-management/status.md`, `docs/implementation-plan.md` §20, the first banner of `docs/operations/disposable-test-server.md` | current-state pointers on return |

No existing test, fixture, assertion or structural guard was modified.

## 3. RP11-I1-1 — the publication contract, before and after

### 3.1 Before (accepted R5 bytes)

P-5 completes a record **under a temporary name** that is distinguishable by a
fixed rule. P-6 applies the file barrier to that temporary file. P-7 **renames**
it to the final name atomically, replacing nothing. P-8 applies the directory
barrier. X-1 … X-3 publish index states by the same "temporary name → file
barrier → atomic publication → directory barrier" sequence. X-3 "creates
nothing but *F* (its temporary file and its final name)". The unadmitted set
includes "a temporary file".

### 3.2 After (proposed, `186ff546…`)

* **Terms (§9.5.1).**
  * *Temporary name* is removed. The contract says so: "There is no temporary
    name in this contract."
  * **Unnamed inode**: an `O_TMPFILE` file opened for writing **without
    `O_EXCL`**, mode `0600` and operator-owned, created in the destination
    directory. It is verified as regular with link count 0.
  * **Exclusive first link (atomic publication)**: one link from the fixed
    source `/proc/self/fd/<decimal fd>`, where the fd is the mechanism's own
    descriptor, with `AT_SYMLINK_FOLLOW`. It gives the inode its first and
    only name.
    * An occupied name is `EEXIST`, which is a capture failure and never an
      overwrite.
    * Link count 0 is re-verified immediately before the link, so a hard-link
      alias cannot be created.
    * No rename, no replacing call, no second link and no other source.
* **P-5 … P-8** are restated on those terms. **Publication succeeds only when
  P-8's directory barrier succeeds.**
* **Failure semantics**, new and applying equally to index states:
  * **A failure before the link** leaves no directory entry, and nothing is
    recorded as unadmitted.
  * **`EEXIST`** creates and replaces nothing. The occupant is not recorded as
    unadmitted, so B0-RA later stops on it (fail-closed).
  * **A link reported as failed or unconfirmed** gets one no-follow identity
    inspection of the exact name. If exactly one named object of the
    mechanism's own exists there, it is **exactly one named, unadmitted
    object**, which X-3 records and B0-RA accounts for.
  * **A successful link followed by a failed P-8 barrier** leaves exactly one
    named, unadmitted object.
  * **Every case** is an `inconclusive` stop, with no retry, repair, cure,
    re-link or republication.
* **The shared call site, stated as two reviewed contracts (§9.5.1).**
  1. The existing I3 named-source caller, `PosixFilesystem.linkat`, uses
     no-follow semantics.
  2. RP-11's `link_unnamed_descriptor` uses follow semantics **only** for the
     fixed `/proc/self/fd/<decimal-fd>` source it builds internally for an
     inode with `st_nlink == 0`.

  No other caller and no other followed source is permitted. The draft states
  that **this amends the previously reviewed I3 primitive's contract**
  (`EXCLUSIVE_LINK_PRIMITIVE`), not only RP-11.
* **Platform prerequisites (§9.5.1).**
  * Linux.
  * A filesystem that supports `O_TMPFILE`.
  * A procfs at `/proc` in the mechanism's mount namespace, on which
    `/proc/self` is the caller and `/proc/self/fd/<n>` resolves.
  * An execution context (sandbox, namespace, LSM or emulation layer) that
    permits the link.

  The draft states explicitly that **creation support does not establish
  naming support**.
* **Consistency edits.** The prompt's list names RP-11, P-5 … P-8, X-1 … X-3,
  C-10, C-13 … C-15, the stop and finalization rules, rollback and §14. Each is
  amended as follows:

| Place | Change |
|---|---|
| Header | Records the R5 acceptance, the RP-11 review and this unaccepted I1-R1 amendment. The R5 bytes remain the baseline |
| §0 table | §9 row names §9.5.4 |
| §4.3 | Preamble notes that I1-R1 re-derived no pin. `PIN.capture_tool_sha256` gets its exact scope (§5 below) |
| §4.4 RP-11 | Temporary name and rename replaced by unnamed inode and exclusive link. Adds (a) the §9.5.4 check, (b) the two-contract call site, (c) the behavioural seal and (d) the binding block. **C-11 and the launcher environment are kept as explicit unresolved blockers.** No wiring is allowed while either is open |
| §4.5 | `MI.pass_a_handback` is parsed **only** through its binding block. New typed blocker `MI.publication_probe_directory_A/_B`, which is **not chosen**. Both capture roots need their own pass's successful check |
| A0-08, B0-08 | The capability check runs in the same mechanism process after the digest/absence checks and before X-1. Failure stops the pass before any root or host command, with no retry. Pass A's result is never reused for Pass B |
| B0-RA (§7.1) | Parses only the binding block and requires `pass_id: C-P5.0-R5-OP1-A`. Root equality is checked against the block |
| C-5, C-7, C-10, C-12, C-13, C-14 | "renamed" wording replaced. C-7 states that no alias can be created. C-10 forbids "linked or renamed into place, re-linked". C-12 moves the parsed binding into the §14 block |
| §9.5 introduction | Names the publication route as a requirement because it has platform prerequisites. All other interfaces remain RP-11's obligation |
| §9.5.2 X-1, X-3 | X-1 follows a successful §9.5.4 check. X-3 publishes *F* by the unnamed-inode sequence and creates only "its unnamed inode and … its one final name" |
| §9.5.3 unadmitted | "Temporary file" removed. Adds names left by a failed or unconfirmed link or a failed P-8. States that a pre-link failure leaves no object |
| §9.5.3 step 4 | Read-only is defined as the behavioural terminal seal (§6 below) |
| §9.5.4 (new) | The pre-admission publication capability check (§4.6 below) |
| §10 items 9–10 | Unadmitted link residue is retained and never re-linked. Read-only changes no permission. The probe's single fixed-name removal is its only removal act, and failed-check residue is preserved |
| §11.2, §11.3 | New stop conditions: unnamed-inode, link and capability-check failures; a missing or ambiguous binding block. Nothing is retried |
| §14 | The `rp11-capture-binding/1` block and its rules (§7 below). The template's outer fence is widened to four backticks so the inner block renders |
| Closing reminder | Records that the amendment is unaccepted, the X-1 capability precondition, and the C-11 and launcher blockers |

**Not weakened.** None of these changed: B0-RA conditions 1–5 and their
evidentiary limit, X-4, the durability ordering (every barrier is still
required, and in the same order), the no-retry rule, or the treatment of
unadmitted objects (retained, never digested, never evidence).

## 4. RP11-I1-2 — portability diagnosis

### 4.1 Local facts (this session)

Recorded without printing the environment and without reading secrets. The
only procfs files read were `/proc/self/status`,
`/proc/self/mountinfo`, `/proc/self/ns/*` and `/proc/sys/fs/protected_hardlinks`.

| Fact | Value |
|---|---|
| Interpreter | `/opt/freedom-blades/runtime/venv-web/bin/python` → CPython 3.12.3, glibc 2.39 |
| Kernel | Linux `6.8.0-139-generic`, x86_64 |
| `os.O_TMPFILE` | present (`0x410000`) |
| `os.link` follow / dir_fd support | both `True` |
| pytest temporary base | `/tmp/pytest-of-foundry/…` on `/` **ext4** (`rw,relatime,discard`) |
| Alternate base used once | `/dev/shm`, **tmpfs** (`rw,nosuid,nodev,inode64`) |
| procfs | `/proc`, type `proc` (`rw,nosuid,nodev,noexec,relatime`). `/proc/self` resolves to the caller |
| Execution context | initial pid, mount and user namespaces (`pid:[4026531836]` …); `Seccomp: 0`; `NoNewPrivs: 0`; `CapEff: 0`; uid 1000; umask 0002; `fs.protected_hardlinks = 1` |
| Magic-link form of an unnamed inode | `/…/#<ino> (deleted)` |

### 4.2 Commands and exact results

All commands ran serially from `/opt/freedom-blades/platform`, with the prefix
`env -u TEST_DATABASE_URL PYTHONDONTWRITEBYTECODE=1
/opt/freedom-blades/runtime/venv-web/bin/python -m pytest -q -rs -p no:cacheprovider`.

| # | Selection | Result |
|---|---|---|
| 1 | the handback's exact eleven-file focused selection, **before any edit** | **1170 passed, 0 failed, 0 skipped** |
| 2 | `test_rp11_publication_portability.py` alone (`-rP` to show recorded facts) | **10 passed, 0 failed, 0 skipped** |
| 3 | as 2, with `TMPDIR=/dev/shm` (tmpfs base; the pytest base directory was removed afterwards) | **10 passed, 0 failed, 0 skipped** |
| 4 | `test_rp11_publication_portability.py` alone, final bytes | **10 passed, 0 failed, 0 skipped** |
| 5 | `test_rp11_capture.py test_rp11_retention.py` | **267 passed, 0 failed, 0 skipped** |
| 6 | selection 1 plus the new module (final tree) | **1180 passed, 0 failed, 0 skipped** |
| 7 | `-m tools.phase_5_0_evidence.execution.cli` (dry run) | `DRY RUN — nothing was executed.`; `review manifest digest: adeabe17…f7de3`; `executable : False` |

Each pytest run printed only pytest's two "Unknown config option" warnings,
for the asyncio options in the shared `pytest.ini`. No test in these files
reads `TEST_DATABASE_URL`, and no skip occurred. An unsupported route would
fail these tests, not skip them.

### 4.3 What the diagnostic establishes

These are **observations** in this context.

1. **Success route, reproduced.** The production path succeeded on ext4 and on
   tmpfs: `PosixCaptureFilesystem.create_unnamed`, then the file barrier, then
   `link_unnamed`, then the directory barrier. The name appeared only after
   the link, as one inode with link count 1. A second link of the same inode
   was refused before linking (`ValueError`).
2. **Creation is not naming.** `O_TMPFILE` creation succeeds with or without
   `O_EXCL`, and in both cases gives a regular inode with link count 0 and no
   entry.
3. **Failing route A, reproduced: a non-linkable inode.** An unnamed inode
   created with `O_EXCL` and passed to the **unmodified production**
   `link_unnamed_descriptor` fails with `FileNotFoundError` / `ENOENT` and
   leaves no entry. That is Codex's exact error.
   * **Attribution: excluded for the reviewed bytes.**
     `PosixCaptureFilesystem.create_unnamed` passes
     `O_TMPFILE | O_WRONLY | O_CLOEXEC` with no `O_EXCL`.
4. **Failing route B, reproduced in model: a magic link that does not resolve
   in the caller's procfs view.** Linking `/proc/self/fd/<n>` for a descriptor
   number the caller does not hold also fails with `ENOENT` and leaves no
   entry.
   * **The errno cannot distinguish route A from route B.**
   * A real absent `/proc`, a procfs from another pid namespace, or a
     sandbox/emulation layer that does not follow the magic link could not be
     constructed here. The suite forbids starting processes, and mounting
     would need privilege or `ctypes`.
5. **Follow semantics are necessary.** Without `AT_SYMLINK_FOLLOW`, the same
   link fails with `EXDEV`: the source is the procfs link itself. This is why
   the RP-11 caller, unlike the I3 caller, needs follow semantics.
6. **The capability-check prototype works.** The prototype in the test module
   is not production source. In an empty directory it:
   * succeeds and leaves the directory empty;
   * with a forced non-linkable inode, fails `unnamed-link:ENOENT` before any
     entry exists; and
   * refuses a non-empty directory without touching the occupant.

### 4.4 Which named prerequisite decides the result

| Candidate | Status |
|---|---|
| Filesystem type | **Not the cause in this context.** ext4 and tmpfs both pass. Codex reported that creation succeeded, so the filesystem supported `O_TMPFILE`. Creation support does not prove naming support (item 2) |
| `O_EXCL` / linkability of the inode | Reproduces the errno. **Excluded for the reviewed source**, which does not pass `O_EXCL` |
| Python `os.link` | Same interpreter path and version. `os.link` supports follow and dir_fd, and the success route passes through it. **Not the cause here.** It cannot be excluded for Codex's context without that context's interpreter facts |
| Kernel | `6.8.0-139-generic` here, where the route passes. **Unknown for Codex's run** |
| procfs view / execution context | **Remaining candidate, consistent with every observation** (route B). This session is unsandboxed; Codex's context was not recorded. Unverified possibilities include a sandbox or namespace whose `/proc/self/fd` does not resolve the caller's descriptor, a missing `/proc`, or an emulated kernel. **None was observed** |

### 4.5 Status of the 1170-pass discrepancy

* **The 1170-pass figure is reproduced here**: 1170 passed, 0 skipped, same
  command, same tree (`c9ee66d`, with production source unchanged).
* **Codex's 991 passed / 179 failed is consistent with route B**, in an
  execution context where the magic link does not resolve.
* **The precise cause in Codex's context is unresolved.**
* The earlier handback's statement "confirmed locally on ext4 (`/tmp`)" was
  true for that session's unsandboxed context only. **It did not establish
  portability**, and it named no execution-context prerequisite. It should not
  have been read as one.

To resolve the cause: rerun `test_rp11_publication_portability.py` in the
review context, with `-rP`. Its `RP11-PORTABILITY-FACTS` line and pass/fail
pattern separate the candidates.
* A failure of `test_the_platform_facts_…` on `proc_self_is_caller` or
  `proc_mount` points to procfs.
* A pass of `test_a_non_linkable_…` together with a failure of
  `test_the_production_route_…` points to the execution context's handling of
  the magic link.

### 4.6 Proposed capability check (draft §9.5.4)

* **Where and when.** Once per pass, **in the same mechanism process that then
  performs X-1**, so that no change of process, sandbox or namespace separates
  the check from the capture. It runs in a maintainer-approved, empty,
  `0700` probe directory on the same device as the capture root's container.
  **No location is chosen here.**
* **Steps**, each done once:
  1. no-follow reach of the directory, its ownership, mode, emptiness and
     device;
  2. `/proc/self` is the caller;
  3. P-5 create and verify;
  4. write at most 64 bytes, then the file barrier;
  5. link using the **production** `link_unnamed_descriptor`;
  6. the directory barrier;
  7. identity and byte verification of the new name;
  8. remove that one fixed name after an identity recheck, apply the
     directory barrier, and **verify the directory is empty**.
* **Failure.** Any failed step stops the pass before X-1, with no root, no
  genesis, no host command and no X-3. It is never retried and never answered
  by a fallback. Residue is preserved and reported.
* **Limit.** It establishes the route only for that process at that moment.

## 5. Capture-tool digest scope (clarification 3)

* **Source set.** The draft now states the exact set: seven whole files, in the
  fixed order `capture_contract.py`, `errors.py`, `execution/boundary.py`,
  `execution/capture_mechanism.py`, `execution/capture_store.py`,
  `execution/descriptors.py` and `execution/retention_check.py`.
* **Construction.** The source's own `rp11-capture-tool/1` construction: the
  SHA-256 of canonical JSON of `[path, file SHA-256]` pairs.
* **Why whole modules.** The launcher lives in `boundary.py`, and the link
  call site lives in `descriptors.py`. No reviewed canonical construction
  exists for a partial-module digest, and none was invented.
* **Stated consequence.** Any byte change to any of the seven files, including
  a change to either shared module that is unrelated to RP-11, invalidates the
  pin.

## 6. Read-only after X-3 (clarification 1)

* **Definition.** Draft §9.5.3 step 4 defines read-only as a **behavioural
  terminal seal**: descriptors are released and every writing API refuses. No
  `chmod` is performed, so the C-7 modes are unchanged.
* **What it is not.** The draft states plainly that this is **not
  operating-system write protection**. It relies on the operator's conduct and
  on the repository host's access boundary (the `0700` root is writable only
  by the operator's account and by root).
* **Detection.** B0-RA detects, at the moment of its check only, the changes
  it can.

## 7. Handback binding (clarification 2)

The `rp11-capture-binding/1` block is now in draft §14's template, and its
rules are stated above the template. `MI.pass_a_handback` and B0-RA refer to
it.

* **Presence.** A pass whose X-1 created its root carries the block exactly
  once. A pass whose X-1 did not create its root carries none. For Pass A,
  that means B0-RA cannot admit Pass B.
* **Parsing.**
  * The file is UTF-8 with LF line endings.
  * Exactly one line equals `` ```rp11-capture-binding ``, and that fence text
    occurs nowhere else.
  * Seven keys follow in this fixed order: `format`, `pass_id`,
    `capture_root`, `x3_outcome`, `x4_validity`, `final_state`,
    `capture_index_sha256`.
  * Each line is `key: value`: one space, a non-empty value, no surrounding
    whitespace and no CR.
  * The closing `` ``` `` is the line immediately after the seventh key.
* **Values.** These match the returned parser's grammars: the identifier
  pattern, the capture-root grammar with no normalization, the fixed
  vocabularies, `index/NNNNNN.final.json` with a state number of at least 1,
  and 64 lowercase hex; `none` is allowed where stated.
* **What B0-RA reads.** It authenticates the handback digest, then parses
  **only** the block. It requires `pass_id: C-P5.0-R5-OP1-A`, `succeeded`,
  `valid`, and a final state and digest that are not `none`. Prose is never
  parsed, and a disagreement between prose and block is a review defect.

**Assumption for review.** The draft states the rules as the returned parser
implements them. A separate check is a proof obligation for the next
implementation review: whether `parse_handback_binding` also refuses a CR
elsewhere in the file, or a CRLF line ending, rather than only inside values.

## 8. Platform prerequisites and residual uncertainty

* **Prerequisites.** Linux; `O_TMPFILE` on the capture filesystem; `/proc`
  mounted in the mechanism's mount namespace with `/proc/self` = caller; an
  execution context that permits `linkat(AT_SYMLINK_FOLLOW)` through that
  magic link; `fs.protected_hardlinks` compatible with linking one's own
  inode (observed `1` here, passing); and directory `fsync` honoured as a
  barrier. The last is unchanged from the earlier handback and is **not
  tested**.
* **Residual uncertainty.**
  * The cause in Codex's context.
  * The runtime that will operate the passes: its sandbox, interpreter and
    kernel.
  * Crash and power-loss behaviour of the barriers. **No crash test was run.**
* **Returned blocker.** The route cannot be guaranteed for an unnamed runtime.
  A maintainer and reviewer must accept the selected repository-host runtime,
  and the §9.5.4 check must pass there. If the route cannot be made to work,
  a different mechanism needs a **new** requirements proposal and review. No
  replacing rename, overwrite, pathname race, shell, `ctypes` or second link
  primitive is proposed.

## 9. Independent-review scope for the shared link primitive

This **is an amendment of the previously reviewed I3 primitive**. Re-review
together:

* **Source**
  * `tools/phase_5_0_evidence/execution/descriptors.py`:
    `EXCLUSIVE_LINK_PRIMITIVE` (the amended text), `PosixFilesystem.linkat`,
    `_exclusive_link`, `UNNAMED_PUBLICATION` and `link_unnamed_descriptor`.
  * `tools/phase_5_0_evidence/execution/capture_store.py`:
    `PosixCaptureFilesystem.create_unnamed`, `PosixCaptureFilesystem.link_unnamed`,
    `CaptureRootStore.publish` and `CaptureRootStore._probe_regular`.
* **Tests**
  * `test_i3_verifier.py`:
    * `test_there_is_one_exclusive_link_and_the_fused_publication_uses_it`
    * `test_reversal_a_non_exclusive_link_overwrites_the_occupant`
    * `test_both_names_are_one_inode_with_link_count_two_and_exact_bytes_before_removal`
    * `test_a_replaced_published_name_is_left_alone`
    * `test_p2_is_root_root_0555_on_the_descriptor_before_linkat`
  * `test_rp11_capture.py`:
    * `test_a_published_name_is_never_replaced`
    * `test_the_unnamed_link_refuses_an_inode_that_already_has_a_name`
    * `test_the_package_still_has_one_link_call_and_linkat_does_not_follow`
    * `test_a_real_linkat_through_the_shared_site_still_refuses_to_replace`
  * The new `test_rp11_publication_portability.py`.

Existing tests and the manifest digest (`adeabe17…`) are review inputs and
**are not acceptance**.

## 10. Checks not run, and why

* The full bot and web suites, and anything on `oracle-test`: excluded by the
  assignment.
* A formatter, linter or type checker: **none is configured** in the
  repository (no `pyproject.toml`, `setup.cfg`, ruff, mypy or flake8
  configuration). This is not a pass.
* Reproduction of the failing route in Codex's actual context: not observable,
  and outside the assignment.
* A crash or power-loss test: not run.
* A secrets scan: prohibited.
* The eventual operational capability check: no location was chosen or
  created.

## 11. Git status (task-relevant)

* **Branch.** `docs/platform-plan`, at `c9ee66d`.
* **Uncommitted before this pass.** The earlier pointer and handback edits
  were already in the tree, together with the assignment prompt and the Codex
  review files, which were untracked.
* **This pass.** It modified the draft and the four pointer files, and added
  the diagnostic test and this handback.
* **Other files.** Unrelated earlier modifications were preserved. There is no
  change under `tools/`.
* `git diff --check` on the task files was clean.
* The draft's relative Markdown links resolve (27 links; the link to this
  handback resolves now that it exists).
* No commit and no push.

## 12. Proposed independent-review focus

1. Whether §9.5.1's unnamed-inode route preserves every accepted P-5 … P-8
   semantic, especially the "failure reported after the link" rule and its
   one-object bound.
2. The two-contract statement for the shared `os.link` call site, as an I3
   amendment (§9).
3. Whether §9.5.4 is sufficient and deterministic, and whether "same process,
   immediately before X-1" is the right binding.
4. The diagnosis in §4, and a rerun of the diagnostic module in the review
   context to attribute `ENOENT`.
5. The binding-block rules (§7), including the CR/CRLF proof obligation.
6. The behavioural-seal wording (§6) and the whole-module digest scope (§5).
7. Confirmation that C-11 and the launcher environment remain open blockers.

Independent Codex technical, security, operational and evidence review is
required. Claude has stopped.
