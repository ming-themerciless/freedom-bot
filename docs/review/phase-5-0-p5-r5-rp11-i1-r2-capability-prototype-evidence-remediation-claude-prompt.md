# Claude prompt — RP-11 I1-R2 capability-prototype evidence remediation

Prompt ID: `C-P5.0-R5-RP11-I1-R2`

Date: 2026-09-28

State: **draft; repository-only diagnostic-test and evidence remediation; no
host or operational authority**

## 1. Assignment

Claude, remediate exactly the Important finding
**RP11-I1-R1-1** from Codex's independent review of I1-R1. Make the diagnostic
prototype and its tests faithfully exercise the locally testable parts of the
proposed §9.5.4 publication capability check, then correct the I1-R1 handback's
evidence claims to match the resulting tests.

Read, in this order, before planning or editing:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 13, 14,
   16 and 20 and the Package 5.0 milestone and acceptance criteria;
3. `docs/review/Handover information`;
4. the first restriction banners and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/project-review-2026-09-28-p5-r5-rp11-i1-r1.md`;
6. `docs/review/phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-claude-prompt.md`;
7. `docs/review/phase-5-0-p5-r5-rp11-i1-r1-publication-contract-and-portability-remediation-handback.md`;
8. the proposed amended
   `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`,
   especially §9.5.4; and
9. `tests/phase_5_0_evidence/test_rp11_publication_portability.py` and the
   production publication functions it invokes, read-only.

The amended operational draft at SHA-256
`186ff546a7f31ccf16461d0d3fec83978af643bd8d2e63dbac2e9dc2f3a2f9c6`
resolved RP11-I1-1 in substance according to Codex, but remains a proposed,
unaccepted requirements amendment. Do not amend it in this pass unless a
minimal wording correction is strictly necessary to remove a contradiction
exposed by the faithful prototype. If that occurs, identify every changed byte
semantically, compute the new digest and return it for independent review;
never treat it as accepted.

## 2. Finding to remediate

Codex found that `probe_unnamed_publication()` demonstrates only a narrower
link-and-cleanup skeleton while the handback describes it as a prototype of the
full proposed §9.5.4 check. In particular, it currently:

* checks initial emptiness but not the probe directory's owner and exact mode;
* does not explicitly compare the probe directory's device with a supplied
  capture-root-containing directory;
* uses one bare `os.write()` without proving every payload byte was written;
* verifies the published name's identity and link count but does not open and
  read it back;
* does not compare the read bytes with the exact fixed payload; and
* unlinks the name before those omitted validations could succeed.

Correct the tests and evidence rather than weakening §9.5.4.

## 3. Required prototype behavior

Keep the prototype diagnostic-only and under pytest temporary directories. It
must accept enough explicit inputs to test the proposed binding without reading
configuration or the environment. At minimum, one successful invocation must
perform these operations once, in order:

1. open the probe directory no-follow and bind its descriptor identity;
2. verify it is a directory owned by the effective user, with exact mode
   `0700`, and empty;
3. open or receive the intended capture-root-containing directory no-follow,
   verify it is a directory, and require its `st_dev` to equal the probe
   directory's `st_dev`;
4. establish that `/proc/self` resolves to the current process;
5. create the unnamed inode through the production creation route and verify
   it is regular, owner-owned, mode `0600`, and has link count zero;
6. write the complete fixed payload with a loop that refuses a zero-length or
   incomplete write, then apply the file barrier;
7. publish through the production `link_unnamed_descriptor`, then apply the
   probe-directory barrier;
8. open the published name no-follow, compare its identity with the unnamed
   inode, require regular type, owner, mode `0600`, and link count one, read all
   bytes, and require exact equality with the fixed payload;
9. recheck the name's identity immediately before cleanup;
10. remove exactly that fixed name, apply the directory barrier, close held
    descriptors, and verify the directory is empty.

Use descriptor-relative operations for the probe name. Do not use
`Path.resolve()` or lexical normalization as a security boundary. A failure
must raise the fixed diagnostic refusal without retry, fallback, repair or a
second publication route. Do not remove residue on a failed path merely to make
the test pass.

The prototype is allowed to be stricter than the minimum above where that
directly represents proposed §9.5.4. It must not become production code or an
operational entry point.

## 4. Required tests

Add focused tests proving externally visible behavior, not only mocked calls.
Cover at least:

* the successful complete check leaves the probe directory empty;
* a partial-write seam cannot be mistaken for a complete payload;
* wrong probe owner and wrong probe mode refuse before unnamed-inode creation;
* a different `st_dev` refuses before unnamed-inode creation, using a narrow
  injected/stat seam rather than requiring a privileged mount;
* an occupied probe directory remains untouched;
* a published file whose bytes differ from the fixed payload refuses before
  cleanup and remains present as residue;
* a published name whose identity changes before cleanup refuses and the
  replacement remains untouched;
* the non-linkable-inode route still returns the recorded `ENOENT` result and
  leaves no entry; and
* success uses the production creation and link functions, not copied link
  logic.

Where deterministic fault injection is necessary, inject the smallest narrow
operation seam into the **test-only prototype**. Do not monkeypatch or edit
production source. A test that is unsupported in the current execution context
must fail and be reported; it must not skip or silently substitute another
publication method.

## 5. Evidence and documentation deliverables

1. Update only the diagnostic module and, where needed, its test-only helpers.
2. Do **not** amend the existing I1-R1 handback. It is durable historical
   evidence. Record the correction as a dated I1-R2 erratum in the new
   handback, identifying the exact I1-R1 claims it narrows or supersedes while
   preserving the original context-specific figures.
3. Create
   `docs/review/phase-5-0-p5-r5-rp11-i1-r2-capability-prototype-evidence-remediation-handback.md`
   with:
   * exact files changed and SHA-256 values;
   * a requirement-to-test map for every item in §§3–4 above;
   * exact commands and pass/fail/skip counts;
   * the result in this execution context, including any `ENOENT`;
   * a precise statement of what the prototype establishes and what remains
     unresolved;
   * confirmation that production source, the review manifest and generated
     artifacts are unchanged;
   * checks not run and why;
   * task-relevant Git status; and
   * proposed independent-review focus.
4. On return only, update `docs/review/Handover information`,
   `docs/project-management/status.md`, implementation-plan §20 and the first
   disposable-server restriction banner to point to this remediation, its
   handback and the required independent Codex review.

Do not add an acceptance record or mark RP11-I1-R1-1 closed. Stop after the
handback and current-state pointer updates.

## 6. Required validation

Run serially, with `TEST_DATABASE_URL` explicitly unset,
`PYTHONDONTWRITEBYTECODE=1`, and the pytest cache provider disabled:

1. the portability diagnostic module alone, with pass-output reporting;
2. the RP-11 capture and retention suites;
3. the exact directly affected structural/no-execution selection from the
   I1-R1 handback, plus the portability module; and
4. the harness CLI dry run only, never `--execute`.

Record exact results. Zero skips are required. A context-sensitive publication
failure is an expected blocker to report, not permission to skip or alter the
test. Run `git diff --check` scoped to task files and verify relevant Markdown
links.

Do not run the full bot/web suites.

## 7. Authorization and prohibitions

This draft assignment authorizes, only after the maintainer assigns it:

* repository reads;
* scoped edits to the test-only portability diagnostic, the new I1-R2 handback
  and current-state pointers; and
* bounded local synthetic tests under pytest temporary directories with
  `TEST_DATABASE_URL` unset.

It does **not** authorize:

* edits to any file under `tools/`, the review manifest, generated artifacts,
  guards, hooks or governing rules;
* SSH, rsync, synchronization, network access or inspection of `oracle-test` or
  any other host;
* `sudo`, database access, provisioning, a controlled write, reboot, verifier,
  evidence band, harness `--execute` or real participant invocation;
* creation, inspection or reuse of a real capture root or operational probe
  path;
* access to any protected historical `/tmp` artifact;
* a secrets scan or command expected to engage the secrets guard;
* wiring, C-11 or launcher-environment decisions, another RP, MD-1 through
  MD-6 or opportunistic remediation;
* acceptance of the amended requirements or implementation;
* marking RP-11 satisfied, setting `plan.is_executable=True`, accepting either
  pass, closing P5.0-R5, binding OD-62 G-A or declaring Package 5.0 ready; or
* a commit or push.

Do not read secrets or print the environment. Preserve unrelated worktree
changes. A guard or tool refusal is a stop condition and must not be retried,
rephrased, bypassed or escalated.

## 8. Return state

Return the corrected diagnostic evidence for independent Codex technical,
security, operational and evidence review.

Until that review and a later explicit maintainer acceptance:

* RP11-I1-R1-1 remains Open, Important;
* RP11-I1-2 remains Open, Blocking;
* the requirements amendment and implementation remain unaccepted;
* RP-11 remains unmet;
* neither pass is executable or authorized;
* P5.0-R5 remains Blocking;
* OD-62 G-A remains conditional;
* `plan.is_executable=False`; and
* Package 5.0 remains not ready.
