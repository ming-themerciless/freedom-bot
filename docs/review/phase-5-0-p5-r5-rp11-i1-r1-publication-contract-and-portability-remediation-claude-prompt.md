# Claude prompt — RP-11 I1-R1 publication-contract and portability remediation

Prompt ID: `C-P5.0-R5-RP11-I1-R1`

Date: 2026-09-28

State: **assigned; repository-only requirements remediation and local diagnosis;
no host or operational authority**

## 1. Assignment

Claude, remediate the two Blocking findings in Codex's independent review of
the returned RP-11 implementation, without crossing the requirements-review
gate.

Read, in this order, before planning or editing:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 13, 14,
   16 and 20 and the Package 5.0 milestone and acceptance criteria;
3. `docs/review/Handover information`;
4. the first restriction banners and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-09-28-p5-r5-rp11-capture-mechanism.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-capture-mechanism-implementation-claude-prompt.md`;
7. `docs/review/phase-5-0-p5-r5-rp11-capture-mechanism-implementation-handback.md`;
8. `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`,
   especially §§4.3–4.5, 7.1, 9.1, 9.4, 9.5, 10, 11 and 14;
9. the accepted R5 review and maintainer acceptance; and
10. the RP-11 implementation, its focused tests, the shared I3 publication
    primitive and the review manifest.

The R5-amended operational draft at SHA-256
`5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3`
remains the accepted requirements baseline. This assignment may prepare an
amended draft for review, but **must not treat that amendment as accepted and
must not change implementation source to conform to it in the same pass**.
Independent Codex review and Peter Duscha's acceptance of the exact amended
requirements are required before a later implementation pass.

## 2. Findings to remediate

### RP11-I1-1 — publication-contract mismatch

The accepted contract says that a record or index state is completed under a
temporary name and published by a non-replacing atomic rename. The returned
implementation instead writes an unnamed `O_TMPFILE` inode and gives it its
first name with an exclusive `linkat` through `/proc/self/fd/N`.

Prepare a controlled requirements amendment that describes the intended
unnamed-inode publication route exactly, rather than continuing to call it a
temporary-name rename. Preserve all required semantics:

* complete-or-absent visibility;
* no replacement of an existing destination;
* file synchronization before publication;
* containing-directory synchronization after publication;
* publication succeeds only after that directory barrier succeeds;
* a failed or unconfirmed barrier is an inconclusive stop with no retry,
  repair, cure or republication;
* a failure before the exclusive link leaves no directory entry;
* a failure reported after the link may leave exactly one named, unadmitted
  object that X-3 records and B0-RA later accounts for; and
* a source inode with an existing name is refused before linking, so this route
  cannot create a hard-link alias.

Amend every affected statement consistently, including RP-11, P-5 through
P-8, X-1 through X-3, C-10, C-13 through C-15, stop/finalization rules,
rollback language and the §14 handback template. Do not weaken B0-RA, X-4,
durability ordering, no-retry behavior or the evidentiary treatment of
unadmitted objects.

The amendment must explicitly state that the shared `os.link` call site serves
two reviewed contracts:

* the existing I3 named-source caller uses no-follow semantics; and
* RP-11 may use follow semantics only for the fixed `/proc/self/fd/<decimal-fd>`
  source produced internally for an unnamed inode whose `st_nlink == 0`.

State whether this is an amendment to the previously reviewed I3 primitive and
identify the exact source and tests an independent reviewer must re-review. Do
not claim that existing tests or a manifest digest are acceptance.

### RP11-I1-2 — publication evidence not reproducible

Codex reran the handback's focused command locally with `TEST_DATABASE_URL`
unset and obtained **991 passed, 179 failed, 0 skipped**. The ordinary success
paths stopped before genesis because the exclusive link through
`/proc/self/fd/N` returned `FileNotFoundError` (`errno 2`).

Diagnose that discrepancy using repository-local, non-privileged, synthetic
tests only. The diagnosis must:

1. reproduce or explicitly report inability to reproduce both the failing
   route and any successful route;
2. record the relevant local Python, kernel-exposed API, filesystem and procfs
   capability facts without printing the environment, reading secrets or
   inspecting another host;
3. distinguish filesystem support for creating an `O_TMPFILE` from support for
   giving that inode a name through the selected link route;
4. determine whether the observed result depends on the filesystem, mount,
   procfs behavior, Python `os.link` implementation, kernel behavior or another
   named prerequisite;
5. explain the earlier 1170-pass claim or mark the discrepancy unresolved; and
6. propose a deterministic, bounded, disposable and cleanup-verified
   pre-admission capability check that fails before X-1 creates a real pass
   root or any host command is issued.

The capability check may use a disposable pytest temporary directory in this
assignment. The eventual operational check must use an explicitly approved
repository-host location outside the worktree and `/tmp`; do not choose or
create that operational location here.

If the `O_TMPFILE` plus `/proc/self/fd` route cannot be guaranteed on the
selected repository-host filesystem/runtime, return that as a blocker. Do not
silently fall back to a replacing rename, an overwrite, a pathname race, shell
execution, `ctypes`, a second unreviewed link primitive, or any weaker
publication rule. A different mechanism requires a new explicit requirements
proposal and independent review.

## 3. Additional contract clarifications in this remediation

Make these already-returned choices explicit in the amended draft so the next
review can accept or reject them as controlled requirements:

1. **Read-only after X-3.** Define it as a behavioural terminal seal: after
   X-3 succeeds or fails, the mechanism releases its descriptors and every
   writing API refuses. No `chmod` is performed. State plainly that this is
   not operating-system write protection and relies on the operator and
   repository-host access boundary stated by the prompt.
2. **Handback binding.** Add the fixed `rp11-capture-binding/1` fenced block to
   §14 and to `MI.pass_a_handback`. Specify its exact seven-key order, single
   occurrence, parsing rules and values, and state that B0-RA parses only that
   block after authenticating the handback digest.
3. **Capture-tool digest scope.** State the exact source set the digest covers
   and why. If whole shared modules remain in scope, state that any change to
   any byte of either shared module invalidates the pin even when unrelated to
   RP-11. Do not invent a narrower derived digest without a reviewed canonical
   construction.

Do **not** resolve C-11 synchronization routing or the launcher environment by
guessing. Preserve both as explicit blockers unless an already accepted record
supplies the answer. Do not wire the mechanism to a command.

## 4. Deliverables

1. Amend
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
   consistently as described above.
2. Add focused repository-local diagnostic tests only if needed to establish
   the portability facts. Tests must not weaken or skip existing assertions.
3. Do not edit RP-11 production implementation source in this pass. If a
   minimal test-only diagnostic cannot express a required observation, report
   the limitation rather than changing production code.
4. Create
   `docs/review/phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-handback.md`
   containing:
   * the amended draft's SHA-256;
   * exact files changed;
   * a mapping from RP11-I1-1 and RP11-I1-2 to the amendments and evidence;
   * the publication contract before and after;
   * local diagnostic commands and exact results;
   * all platform prerequisites and residual uncertainty;
   * the status of the earlier 1170-pass discrepancy;
   * checks not run;
   * task-relevant Git status; and
   * proposed independent-review focus.
5. On return only, update `docs/review/Handover information`,
   `docs/project-management/status.md`, implementation-plan §20 and the first
   disposable-server restriction banner to point to this remediation, its
   handback and the required independent Codex review.

Do not add acceptance records, pins that purport to be approved, or language
that marks either finding closed. Stop after the handback and current-state
pointer updates.

## 5. Required validation

Run only repository-local tests relevant to the publication mechanism,
contract structure, manifest consistency and no-execution guards, serially,
with `TEST_DATABASE_URL` explicitly unset and the cache provider disabled.

At minimum:

* run any new diagnostic test in isolation;
* rerun the two RP-11 focused suites and directly affected structural tests;
* record exact passed, failed and skipped counts without converting an
  unsupported platform into a skip; and
* run `git diff --check` scoped to task files and verify the amended document's
  relevant Markdown links.

A failure caused by an unsupported publication route is evidence for the
remediation, not permission to weaken or skip the test. Zero skips are required
for tests claimed as gate evidence. Do not run the full bot/web suites.

## 6. Authorization and prohibitions

This assignment authorizes:

* repository reads;
* the scoped requirements, test and handback edits above; and
* bounded local synthetic tests under pytest temporary directories with
  `TEST_DATABASE_URL` unset.

It does **not** authorize:

* SSH, rsync, synchronization, network access or inspection of `oracle-test` or
  any other host;
* `sudo`, database access, provisioning, a controlled write, reboot, verifier,
  evidence band, harness `--execute` or real participant invocation;
* creation, inspection or reuse of a real capture root or operational path;
* access to any protected historical `/tmp` artifact;
* a secrets scan or a command expected to engage the secrets guard;
* changing a guard, hook or governing rule;
* production-source remediation, wiring, another RP, MD-1 through MD-6 or an
  opportunistic cleanup;
* acceptance of the amended draft or implementation;
* marking RP-11 satisfied, setting `plan.is_executable=True`, accepting either
  pass, closing P5.0-R5, binding OD-62 G-A or declaring Package 5.0 ready; or
* a commit or push.

Do not read secrets or print the environment. Preserve all unrelated worktree
changes. A guard or tool refusal is a stop condition and must not be retried,
rephrased, bypassed or escalated.

## 7. Return state

Return the amended requirements, portability diagnosis and handback for
independent Codex technical, security, operational and evidence review.

Until that review and a later explicit maintainer acceptance:

* both Blocking findings remain Open;
* the implementation remains unaccepted and unwired;
* RP-11 remains unmet;
* neither pass is executable or authorized;
* P5.0-R5 remains Blocking;
* OD-62 G-A remains conditional;
* `plan.is_executable=False`; and
* Package 5.0 remains not ready.
