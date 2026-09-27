# Claude prompt — implement RP-11 client-side evidence capture and retention verification

Prompt ID: `C-P5.0-R5-RP11-I1`

Date: 2026-09-27

State: **assigned; repository implementation and local tests only; no host or operational authority**

## 1. Assignment

Claude, implement repository prerequisite **RP-11**, the client-side evidence-
capture mechanism and read-only Pass A retention verification required by the
accepted R5-amended operational-evidence draft.

Read, in this order, before planning or editing:

1. `.agents/AGENTS.md` completely;
2. `docs/implementation-plan.md` using its reading map, including §§0, 13, 14,
   16 and 20 and the Package 5.0 milestone and acceptance criteria;
3. `docs/review/Handover information`;
4. the first restriction banners and relevant contract in
   `docs/operations/disposable-test-server.md`;
5. `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`,
   especially §§4.3–4.5, 7.1, 9.1, 9.4, 9.5, 10, 11 and 14;
6. Codex's accepted
   `docs/review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5.md`;
7. Peter Duscha's
   `docs/review/project-review-2026-09-27-p5-r5-operational-evidence-prompt-r5-acceptance.md`;
8. the R5 assignment and handback, and earlier OP1 reviews needed to preserve
   their resolved conclusions; and
9. the existing `tools/phase_5_0_evidence/` architecture, its review manifest,
   and relevant `tests/phase_5_0_evidence/` structural and no-execution guards.

The exact R5-amended draft at SHA-256
`5e06a38811462613244ee258524461eb23b5598862ce43efa3ec77365040acb3`
is the controlling RP-11 requirements contract. Do not amend it in this pass.
If its requirements are contradictory or cannot be implemented safely, stop
and return the contradiction rather than silently choosing a weaker reading.

## 2. Deliverables

1. Implement repository-owned RP-11 source under
   `tools/phase_5_0_evidence/`, fitting the existing package structure and
   separating process execution, durable storage, index validation and
   retention verification where their responsibilities differ.
2. Provide callable, testable boundaries for creating a pass-specific capture
   root and genesis state, issuing one exact argv without a shell, making the
   single X-3 finalization attempt, and running B0-RA read-only against a
   digest-pinned Pass A handback. Do not wire them into or invoke a real
   operational-pass command in this assignment.
3. Add focused tests under `tests/phase_5_0_evidence/` covering §§3–5 below,
   including injected publication/barrier failures and hostile retained trees.
4. Update the review manifest and generated review artifacts if, and only if,
   its existing contract requires the new or changed source to be covered. A
   generated digest is review input, not acceptance.
5. Create
   `docs/review/phase-5-0-p5-r5-rp11-capture-mechanism-implementation-handback.md`
   with exact files changed, architecture and interfaces, requirement-to-test
   mapping, test results, injected failures, unresolved questions, manifest
   effects, checks not run and task-relevant Git status.
6. On return only, update `docs/review/Handover information`,
   `docs/project-management/status.md`, implementation-plan §20 and the first
   disposable-server restriction banner to point to this assignment, the
   handback and the required independent Codex review.

Stop after the handback and pointer updates. Do not accept your own work or
amend the operational draft to mark RP-11 satisfied or insert pins.

## 3. Capture and publication requirements

Implement §9.5 exactly, including C-1 through C-15, P-1 through P-8 and X-1
through X-4.

### 3.1 Process boundary and captured facts

* Accept argv as an explicit sequence and execute it directly, never through a
  shell, shell string, pipe, redirection, command substitution or expansion.
* Record exact argv, pass ID, strictly increasing gap-free `capture_seq`, step
  or case ID, client UTC start and end, exit status, and separate stdout and
  stderr identities.
* Capture stdout and stderr completely and separately as raw bytes. Do not
  decode, normalize, combine, summarize or substitute a terminal transcript.
* Enforce declared stream bounds without truncation. A start, capture, close,
  bound, digest or publication failure is an inconclusive stop.
* Never create a capture file on the invoked command's target. The capture
  root and every evidence file belong to the repository host only.

### 3.2 Crash-consistent publication

* Create each pass-specific capture root exclusively, outside the worktree and
  `/tmp`, and durably publish its genesis state before the first command.
  Reject an existing root. Pass A and Pass B roots and chains are independent.
* Publish streams, records and immutable index states using the exact ordering
  and successful file/directory barriers of P-1 … P-8 and X-1 … X-4. Atomic
  publication must replace nothing.
* Advance the index durably before another act starts. Published names and
  bytes are immutable and never reused.
* Put filesystem and process operations behind narrow interfaces so tests can
  fail every stage deterministically without weakening the production path.
* A failed or unconfirmed barrier fails. Do not retry it, cure it with later
  synchronization, repair or republish an object, or issue the command again.

### 3.3 Stops, finalization and unadmitted objects

Implement §9.5.3's one order:

1. stop commands immediately and issue no further command;
2. only while the mechanism and repository host remain available and a durable
   genesis exists, make exactly one X-3 attempt as the only later write;
3. record its one success or failure without retry or repair;
4. make the root read-only at that outcome; and
5. apply X-4 without reconstructing a missing or invalid final state.

After an interruption of the mechanism or repository host, perform no X-3
attempt after recovery. A root with no durable genesis has no chain to finalize.

The final state records every mechanism-created subdirectory and every
unadmitted object the mechanism knows exists by exact relative name and object
type. Do not digest, complete, adopt or use an unadmitted object as evidence.
A failed creation that produced no directory entry is not an existing
unadmitted object.

## 4. B0-RA retention verification

Implement B0-RA as a separate, non-mutating, one-shot operation before Pass B
creates its root. It must:

1. authenticate the supplied Pass A handback by expected SHA-256 and parse only
   fixed contract fields;
2. require successful X-3, valid X-4, a final-state name and index SHA-256;
3. require the supplied Pass A root to equal the recorded root byte for byte;
4. re-derive the final digest and re-apply X-4 to the complete chain, admitted
   records and bound streams; and
5. compare one complete recursive enumeration of observed relative names and
   types with the complete accounted set from the final state and fixed naming
   rules, in both directions.

Define one documented byte-safe relative-name representation. Reject or make
structurally impossible:

* absolute names, empty or dot components, `..`, NUL and traversal;
* duplicate/ambiguous encodings and duplicate category membership;
* symbolic links and path aliases, including hard-link aliases;
* resolution outside the root;
* unexpected types, mismatches and non-regular evidence files;
* either non-empty name-set difference, including an absent unadmitted name;
* change during enumeration or verification where stable identity and
  completeness cannot be proven; and
* any incomplete enumeration, digest, parse or comparison.

Use descriptor-relative, no-follow operations and identity rechecks where
needed to resist path replacement and time-of-check/time-of-use races. Do not
use lexical normalization or a prior `resolve()` as a security boundary. If
the repository-host filesystem or Python API cannot support a required
guarantee, return the blocker rather than dilute the contract.

B0-RA may list names and types and read/digest admitted bytes only. It must not
write, move, rename, truncate, complete, repair, adopt, delete, chmod, create or
otherwise mutate the retained root. For unadmitted objects and recorded
subdirectories it establishes presence, exact relative name and type only,
never unchanged bytes or metadata. It must not digest an unadmitted object.

## 5. Required tests and proofs

Use pytest temporary directories; do not use a fixed `/tmp` path. Tests may
execute only bounded local fixture programs or the current Python interpreter
with inert test arguments. They must not invoke SSH, rsync, sudo, PostgreSQL,
the harness `--execute` branch, a real participant or any operational command.

Cover at least:

* exact argv and separate raw stdout/stderr, including non-UTF-8 bytes, empty
  streams, interleaving, nonzero exit and bounded-output refusal;
* exclusive root creation, modes, pass separation, genesis and gap-free order;
* successful P-1 … P-8, X-1 … X-4 and one-shot X-3;
* deterministic failure at every close, digest, file barrier, directory
  barrier, atomic publication and index-advance stage, proving no retry, no
  next command, no repair and the correct unadmitted/final state;
* interruption before/after durable genesis and at every X-3 stage;
* tampered handback, wrong root, absent/multiple final states, broken chain,
  record gap, missing/changed record or stream, stale digest and unexpected
  published record;
* both name-set differences, every type mismatch, duplicate category,
  ambiguous encoding, symlink, hard-link alias, traversal/escape, unsupported
  type and incomplete enumeration;
* deleted/replaced unadmitted objects while proving content is not read;
* nested mechanism-created directories and recursion at multiple depths;
* mutation/race injection during enumeration and digest verification, failing
  closed; and
* structural no-execution/no-network proof for imports and default entry points.

Assert externally visible state and invariants, not only mock calls. Record
every platform-specific assumption.

## 6. Authorization and prohibitions

This assignment authorizes repository reads, scoped source/test/documentation
edits and local tests with `TEST_DATABASE_URL` unset. It does **not** authorize:

* SSH, rsync, synchronization, network access or host inspection;
* `sudo`, database access, provisioning, controlled writes, reboot, verifier,
  evidence band, harness `--execute` or real participant invocation;
* creation, inspection or reuse of a real capture root or operational path;
* protected historical `/tmp` artifact access;
* a secrets scan or command expected to engage the secrets guard;
* changing a guard, hook or governing rule;
* filling another RP, changing MD-1 through MD-6, or opportunistic remediation;
* marking RP-11 satisfied, setting `plan.is_executable=True`, accepting either
  pass, closing P5.0-R5, binding OD-62 G-A or declaring Package 5.0 ready; or
* committing or pushing.

Do not read secrets or print the environment. Preserve unrelated worktree
changes. A guard refusal is a stop condition. Report any required local test
that cannot run within these boundaries.

## 7. Validation and return

Run only focused RP-11 and directly affected structural/no-execution tests,
serially, with `TEST_DATABASE_URL` explicitly unset and the cache provider
disabled. Do not run the full suite. Record exact commands and pass/fail/skip
counts. Zero focused-test skips are required; a skip is a returned blocker.

Run `git diff --check` scoped to task files, inspect the scoped diff, verify
relevant Markdown links, and report task-relevant Git status without modifying
unrelated changes. Return the implementation and handback for independent
Codex technical, security, operational and evidence review, then stop.
