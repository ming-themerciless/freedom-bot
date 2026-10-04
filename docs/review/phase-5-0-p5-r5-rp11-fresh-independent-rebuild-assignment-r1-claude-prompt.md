# Claude prompt — remediate the fresh R-5 assignment draft

Work ID: `C-P5.0-R5-RP11-FRESH-A1-R1`

Date: 2026-10-02

Assignee: Claude

Status: **proposed documentation-only remediation; not executable until Product Owner Peter Duscha explicitly accepts this drafting task and appoints Claude**

## 1. Objective and disposition

Remediate five findings from Codex's independent review of Claude's proposed
fresh R-5 assignment:

1. `FRESH-A1-R1-1` — **Blocking:** required commands can mask a failed build,
   verifier or test behind a successful `echo`;
2. `FRESH-A1-R1-2` — **Blocking:** expected-absence checks return nonzero while
   the assignment declares every nonzero result a hard stop;
3. `FRESH-A1-R1-3` — **Blocking:** the proposed `git archive` transport has no
   accepted fail-closed secrets boundary;
4. `FRESH-A1-R1-4` — **Important:** the draft leaves unresolved whether a
   bubblewrap version-only difference qualifies as HA-3 variation; and
5. `FRESH-A1-R1-5` — **Important:** Claude did not completely read all sources
   that the preparation prompt made mandatory.

Correct the assignment so it is deterministic, fail-closed and decision-ready.
This remains documentation preparation only. Do not execute, simulate or test
R-5.

## 2. Required context and mandatory complete reading

Before editing, read completely, from first byte to last byte:

1. `.agents/AGENTS.md`;
2. the original preparation prompt:
   `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-preparation-claude-prompt.md`;
3. the proposed assignment and preparation handback;
4. `docs/review/Handover information`;
5. `docs/project-management/status.md`;
6. `docs/operations/disposable-test-server.md`;
7. the accepted D2/D2-R2 proposal, handbacks, reviews and decision records;
8. the I-7 and I-7-R1 prompts, handbacks, Codex reviews and acceptance records;
9. the original R-5 assignment, its independent review and acceptance, the
   stopped handback, bubblewrap review and bubblewrap authority;
10. every R2, R3, R4 and R4-R1 prompt and handback, plus their review and
    acceptance records where present;
11. every B1, B1-R1, B1-R2, B1-R3 and B1-R4 prompt and handback, plus their
    review and acceptance records where present;
12. `infra/rp11-launch/buildroot/provision.py`;
13. `infra/rp11-launch/buildroot/enter.py`;
14. `infra/rp11-launch/verify/cc1check.py`;
15. `tests/test_rp11_launch_toolchain.py`; and
16. this remediation prompt.

For `docs/implementation-plan.md`, read its reading map and then §0, §13, §16,
§17 and §20 completely, as the repository entry instructions require.

Do not substitute `rg`, excerpts, file sizing or keyword searches for the
complete reads required above. The remediation handback must list every file
read completely and explicitly confirm completion.

Inspect `git status` before editing. Preserve every unrelated change.

## 3. Required corrections

### 3.1 Preserve failing exit statuses

Audit every executable command in the proposed assignment, not only the three
examples Codex identified.

For any command whose status is printed or logged:

- capture its status immediately;
- print or record that exact status;
- exit the command context with the same status; and
- ensure no later `echo`, `printf`, pipe, semicolon-separated command or
  redirection masks it.

Correct at minimum:

- the same-invocation `enter.py build` command;
- the `cc1check.py` command;
- the pytest command; and
- the `ld.so.preload` absence check.

Use an explicit, reviewable shell form such as:

```bash
command_to_check
status=$?
printf 'exit=%s\n' "$status"
exit "$status"
```

where that form runs within one remote shell command and the final status is
observable by the caller. Do not use `set -e` as a substitute for explicit
status handling, because evidence still requires the exact status to be
recorded.

Where several checks are intentionally grouped, define precisely which status
governs and stop before any later check if the earlier one failed.

### 3.2 Make expected-absence checks unambiguous

Replace commands whose successful observation naturally returns nonzero with
explicit conditionals that return zero only for the accepted condition and
return a distinct nonzero status for a violation.

Correct at minimum:

- the optional
  `/proc/sys/kernel/apparmor_restrict_unprivileged_userns` observation: record
  the exact value if present and a literal `absent` marker if not present;
- proof that no `/tmp/<RUN>*` path exists before creation;
- proof that `/etc/ld.so.preload` is absent; and
- proof that the build root's `/tmp` and `/var/tmp` contain no entries.

Do not use an unmatched glob through `ls` as an absence proof. Avoid pipelines
whose status comes from only their final process. State the accepted output and
exit status for each conditional.

### 3.3 Replace the unresolved checkout transport

Remove the proposed `git archive` plus single-file `rsync` transport and remove
U-5 as an unresolved execution assumption.

Use the repository's documented secret-excluding `rsync` procedure from
`docs/operations/disposable-test-server.md`, adapted only as necessary to send
the current repository tree into the run's unique fresh checkout path rather
than the shared `/opt/freedom-blades/platform` path.

The command must retain all documented exclusions and their accepted quoting,
including the ordering requirement for `.env.example`. It must not use
`--delete-excluded`, an exclusions file, a shell substitution, a chained
command, or an archive containing every tracked file without exclusions.

If the enforced guard does not admit a fresh-path destination or the documented
procedure cannot be safely adapted without a new policy decision, do not invent
an alternative. Mark the assignment as blocked on a specific maintainer ruling
and stop the drafting remediation with a partial handback.

After synchronization, retain the remote exact-digest verification of every
controlling file. Remove archive-specific paths, commands, digests and handback
requirements that no longer apply.

### 3.4 Resolve HA-3 conservatively

State normatively that a bubblewrap **version-only** difference does not, by
itself, qualify as the “different entry mechanism” required by D2/LD-8.

For this assignment:

- HA-1 qualifies only through a different kernel release;
- HA-2 qualifies only through a different CPU model because no accepted
  reference feature list exists; and
- HA-3 qualifies only through a materially different entry mechanism or
  materially different entry configuration accepted in advance—not merely a
  different version of the same `/usr/bin/bwrap` mechanism using the same
  vector.

Because the current implementation supports only the accepted bubblewrap
mechanism, do not add a new entry mechanism or source change. The run must rely
on an actually measured HA-1 or HA-2 difference unless Peter separately accepts
a materially different HA-3 configuration before execution.

Remove U-4 as an unresolved assumption. Preserve the rule that a run with no
qualifying HA-1 through HA-3 difference is INVALID and stops before
provisioning.

### 3.5 Reconcile all disclosed unresolved items

Review U-1 through U-9 after completing the mandatory source reading.

- Retain U-1 only as diagnostic context; exact `cc1.v` mismatch remains a hard
  stop and no GGC-only exception is authorized.
- Confirm or remove U-2 based on the actual `provision.py resolve` contract.
  Retain the signature gate if it is supported as written and fail-closed.
- Retain the truthful limitation in U-3, but make its operational consequence
  normative rather than unresolved.
- Resolve U-4 and U-5 as required above.
- Convert U-6 into an explicit evidence-retention rule or a clearly identified
  Product Owner decision request; do not leave the executor to choose.
- Replace placeholder identifiers only if Peter has already decided them;
  otherwise keep them clearly pending acceptance.
- Keep governance-document updates outside the executor's authority.
- Preserve the disclosed tree movement in the preparation handback as
  historical drafting context; the execution assignment binds exact bytes,
  not Claude's preparation-time commit.

No unresolved item may affect execution safety, independence, admissibility,
PASS eligibility, transport security or evidence availability. Such an item
must instead be resolved in the assignment or explicitly block its acceptance.

## 4. Preserve accepted boundaries

Do not weaken or remove:

- Claude's ineligibility to execute R-5;
- the TBD executor selected only by Peter;
- wholly fresh roots, caches, checkouts, work paths and evidence;
- the prohibition on reuse of earlier R-5, B1, I-7 or I-7-R1 artifacts;
- manifest version 30 and all accepted digests;
- the distinction between four normative outputs and diagnostic
  `cc1.v.baseline`;
- the same-invocation R-1/R-2 gate;
- exact-byte equality as the only `cc1check.py` PASS route;
- the 12-test, zero-skip corroborating requirement;
- the one-run, no-retry, no-remediation rule;
- the prohibition on privilege escalation or prerequisite repair;
- PASS, INVALID RUN and HARD STOP precedence;
- the executor handback and immediate stop; or
- the rule that Codex review and Peter's later decision are required after the
  run.

Do not change the baseline fixture, manifest, concrete plan, launcher source,
tests, toolchain lock, build-root manifest or normative digests.

## 5. Authorized files

Claude may modify only:

- `docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`;
  and
- the R1 remediation handback required by §7.

Do not amend the original preparation handback. It remains historical evidence
of the first draft and its disclosed shortfalls.

## 6. Authority and restrictions

This is documentation-only remediation. Claude may perform repository-local,
read-only inspection and syntax analysis needed to correct the proposal.

Claude may not:

- execute any proposed R-5 command, even locally;
- access `oracle-test` or another remote host;
- use SSH, rsync, network access or downloads;
- access retained `/tmp` evidence;
- provision, build, run tests or execute a verifier;
- run `provision.py`, `enter.py`, `cc1check.py`, IC-1, B1 or R-5;
- use `sudo`, change packages, services, databases or host configuration;
- edit existing governance or current-state documents;
- modify implementation, tests, fixtures, manifests or generated artifacts;
- stage, commit or push; or
- select, appoint, review or accept the R-5 executor.

R-5 remains stopped, Blocking, unaccepted and unauthorized throughout this
task.

## 7. Required handback

Write:

`docs/review/phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md`

Include:

- all five finding identifiers and their exact dispositions;
- exact before/after command forms for every exit-status and absence-check
  correction;
- the final synchronization command and its source in the operations document;
- the final normative HA-1 through HA-3 qualification rules;
- disposition of every former U-1 through U-9 item;
- a complete list of mandatory documents read fully;
- every read-only command actually run;
- every file modified or created;
- before/after SHA-256 of the proposed assignment;
- confirmation that all accepted input values remain unchanged;
- relative-link and whitespace-check results for the two authorized outputs;
- final `git status --short`;
- confirmation that no host, remote, build, test, verifier or execution action
  occurred; and
- confirmation that R-5 remains unaccepted and unauthorized.

## 8. Stop conditions

Stop and write a partial R1 handback if:

- a mandatory document cannot be read completely;
- a controlling digest differs;
- the secret-excluding synchronization procedure cannot be adapted to the
  unique fresh destination within existing accepted policy;
- resolving a finding requires implementation or test changes;
- an execution-safety or PASS-eligibility ambiguity remains;
- another agent modifies either authorized output path; or
- any required work would cross the documentation-only boundary.

After writing the corrected assignment and R1 handback, stop. Do not execute
R-5 or begin another task.
