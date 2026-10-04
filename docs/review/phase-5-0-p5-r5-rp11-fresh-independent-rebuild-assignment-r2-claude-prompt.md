# Claude prompt — remediate fresh R-5 assignment timestamp contract

Work ID: `C-P5.0-R5-RP11-FRESH-A1-R2`

Date: 2026-10-02

Assignee: Claude

Status: **proposed documentation-only remediation; not executable until Product Owner Peter Duscha explicitly accepts this drafting task and appoints Claude**

## 1. Objective and disposition

Remediate Codex finding `FRESH-A1-R2-1` (**Important**) from the independent
R1 review:

> The executor handback requires start and end UTC timestamps for the whole run
> and for each step, but the authorized procedure records timestamps only in
> S2.1 and S11.7. The executor cannot add the missing timestamp commands because
> every command not written in the assignment is an unexpected command and a
> HARD STOP.

Make the execution procedure and handback contract mutually satisfiable,
mechanically unambiguous and fail-closed. This is documentation preparation
only. Do not execute, simulate or test R-5.

## 2. Required context and complete reading

Before editing, read completely, from first byte to last byte:

1. `.agents/AGENTS.md`;
2. `docs/review/Handover information`;
3. `docs/project-management/status.md`;
4. `docs/operations/disposable-test-server.md`;
5. the fresh-assignment preparation prompt and handback;
6. the R1 remediation prompt and handback;
7. the current proposed fresh R-5 assignment;
8. Codex's R1 independent review,
   `docs/review/project-review-2026-10-02-p5-r5-rp11-fresh-assignment-r1.md`;
9. the accepted B1-R4 decision that controls the current restriction; and
10. this R2 prompt.

For `docs/implementation-plan.md`, read its reading map and then §0, §13, §16,
§17 and §20 completely.

Do not substitute searches, excerpts or file sizing for a required complete
read. Inspect `git status --short` before editing and preserve every unrelated
change.

## 3. Required correction

Retain the existing handback requirement for start and end UTC timestamps for
the whole run and each ordered step or separately invoked step-part. Add the
missing timestamp capture to the authorized procedure rather than weakening
the evidence contract.

### 3.1 Timestamp coverage

Define exactly which invocation supplies the start and end timestamps for:

- the whole run;
- step 1;
- step 2;
- step 3;
- step 4a;
- step 4b, the standalone synchronization command;
- step 4c;
- step 4d;
- step 5;
- the combined steps 6/7 block, with the combined scope stated explicitly;
- step 8;
- step 9;
- step 10;
- step 11; and
- step 12, the repository handback and immediate stop.

If “each step” is intended to mean each separately invoked block or command,
say that normatively and use the same labels in §6 and §10. Do not leave the
executor to infer whether a substep, block or prose action needs its own pair.

### 3.2 Authorized command form

For every shell block, capture UTC start and end values inside that block with
explicit labels. Each timestamp command must have its status captured
immediately, printed and enforced under the existing fail-closed convention.
Use a stable UTC format such as `%Y-%m-%dT%H:%M:%SZ`.

The standalone step-4b `rsync` command must remain byte-for-byte in the
accepted secret-guard shape apart from the already permitted `<RUN>`
substitution. Do not prepend, append, wrap, redirect or chain anything to it.
Authorize separate, explicitly written repository-host timestamp blocks
immediately before and after the `rsync` invocation. Each timestamp block must
preserve and expose its own status. The `rsync` invocation's status must remain
directly observable and governing.

For step 12, specify an authorized, workable way to record the handback start
and end without requiring the executor to alter an earlier transcript or issue
an undocumented command. The final timestamp may be part of the handback
content if the contract clearly defines how it is obtained using an authorized
command and how its status is recorded.

The whole-run start must occur before the first substantive preflight action.
The whole-run end must occur after the handback is complete and immediately
before the required stop. State how both values enter the handback evidence.

### 3.3 Reconcile all affected text

Update every affected part of the assignment consistently, including:

- §6.0 substitutions, block and status conventions;
- the ordered commands in §6;
- §7's exhaustive authorization summary and unexpected-command rule;
- PASS/HARD STOP conditions where needed;
- §10 item 2 and the transcript/evidence requirements in §10.1; and
- any step descriptions or expected-output text affected by the new labels.

Every timestamp command must be visible in the assignment and therefore
reviewable before acceptance. A timestamp failure is a HARD STOP. No required
timestamp may depend only on an operator's wall clock, terminal metadata,
shell history, an SSH client log or an unstated wrapper.

## 4. Preserve the accepted R1 corrections and boundaries

Do not reopen or weaken:

- the immediate capture and propagation of checked command statuses;
- explicit successful absence checks and distinct violation statuses;
- the documented secret-excluding `rsync` transport and its exact guard-safe
  command shape;
- the post-transfer local and remote exact-byte checks;
- the normative HA-1 and HA-2 rules and the rule that a bubblewrap version-only
  difference does not qualify as HA-3;
- Claude's ineligibility to execute R-5;
- the TBD executor selected only by Peter Duscha;
- wholly fresh roots, caches, checkout, work paths, pytest tree and evidence;
- the prohibition on reusing earlier R-5, B1, I-7 or I-7-R1 artifacts;
- manifest version 30 and every accepted digest and length;
- the distinction between four normative outputs and diagnostic
  `cc1.v.baseline`;
- the same-invocation R-1/R-2 gate;
- exact-byte equality as the only `cc1check.py` PASS route;
- the 12-test, zero-skip corroborating requirement;
- the one-run, no-retry, no-remediation rule;
- the prohibition on privilege escalation or prerequisite repair;
- PASS, INVALID RUN and HARD STOP precedence;
- evidence retention and the executor's immediate stop; or
- independent Codex review and Peter's later decision after any run.

Do not change implementation, tests, fixtures, manifests, generated artifacts,
the concrete plan, launcher sources, `toolchain.lock`,
`build-root.manifest`, `expected.sha256` or any accepted digest.

## 5. Authorized files

Claude may modify only:

- `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`;
  and
- `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r2-handback.md`,
  which Claude must create.

Do not amend the preparation handback, R1 handback, Codex review, active
handover, status, implementation plan or operations document. Those remain
historical evidence or current authority.

## 6. Authority and restrictions

This task authorizes repository-local documentation editing and read-only
inspection only. Claude may use syntax-only analysis of extracted shell or
Python text, provided no proposed R-5 command or program is executed.

Claude may not:

- access `oracle-test` or any other remote host;
- use SSH, rsync, network access or downloads;
- execute any proposed block, synchronization command or R-5 action, locally
  or remotely;
- access retained `/tmp` run evidence;
- provision, build, run tests or execute a verifier;
- run `provision.py`, `enter.py`, `cc1check.py`, IC-1, B1 or R-5;
- use `sudo`, install or change packages, or change services, databases or host
  configuration;
- modify implementation, tests, fixtures, manifests or generated artifacts;
- update governance or current-state documents;
- stage, commit or push; or
- select, appoint, review or accept the R-5 executor.

R-5 remains stopped, Blocking, unaccepted and unauthorized throughout this
task.

## 7. Required R2 handback

The R2 handback must include:

- the exact disposition of `FRESH-A1-R2-1` without claiming Codex or Peter has
  closed it;
- a timestamp-coverage table mapping every scope listed in §3.1 to the exact
  authorized command labels that produce its start and end values;
- exact before/after text for the handback timestamp requirement;
- the final step-4b `rsync` command and confirmation that its guard-safe bytes
  were not changed except for the existing `<RUN>` placeholder;
- an explanation of how step 12 and whole-run end timestamps are obtained
  without an unauthorized command or circular handback edit;
- confirmation that every timestamp status is captured and that failure is a
  HARD STOP;
- confirmation that all five earlier R1 corrections remain intact;
- every mandatory document read completely;
- every read-only or syntax-only command actually run;
- every file modified or created;
- before/after SHA-256 for the assignment;
- confirmation that all accepted baseline values and controlling-file bytes
  remain unchanged;
- relative-link and whitespace-check results for both authorized outputs;
- final `git status --short`;
- confirmation that no host, remote, build, test, verifier, provisioning,
  synchronization, commit or push action occurred; and
- confirmation that R-5 remains unaccepted and unauthorized.

## 8. Stop conditions

Stop and write a partial R2 handback if:

- a mandatory document cannot be read completely;
- a controlling digest or accepted baseline value differs;
- step-4b's guard-safe `rsync` form would need to change;
- the timestamp contract cannot be made executable without a command outside
  the bounded assignment;
- remediation requires implementation, test, fixture, manifest or governance
  changes;
- another execution-safety or PASS-eligibility ambiguity is discovered;
- another agent modifies either authorized output path; or
- any required work would cross the documentation-only boundary.

After writing the corrected assignment and R2 handback, stop. Do not execute
R-5, update current-state documents or begin another task.
