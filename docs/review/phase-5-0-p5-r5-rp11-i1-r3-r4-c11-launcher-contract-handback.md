# Claude handback — C-11 guard-preserving capture and pinned launcher-environment design

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D1`

Date: 2026-09-29

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-claude-prompt.md)

Proposal:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)

State: **returned as documentation only, for mandatory independent Codex review.
Claude has stopped.** Nothing is accepted, decided or implemented.

## 1. Summary

**Recommendation: O-2.** It combines a closed act catalogue with one canonical
guard policy, which is the digest-pinned bytes of `guard-secrets.py` and
`guard-git.py`, executed at two points:

* **Mandatory, in-process in the capture entry.** It runs before X-1 and again
  before every launch. No caller-supplied argv exists.
* **Defense in depth, in the client `PreToolUse` hooks.** The hooks resolve the
  one exact entry invocation through the same catalogue and apply their
  unchanged rules to every resolved text.

**Environment contract `rp11-launcher-env/1`.** The contract is closed, and
`rsync`, its child `ssh` and every direct `ssh` receive the same map:

* `PATH=/usr/bin`;
* `LC_ALL=C`; and
* `SSH_AUTH_SOCK`, only under agent authentication, as a maintainer-fixed,
  digest-bound socket checked with `lstat` only.

Every other variable is deliberately absent or prohibited, each with a named
refusal class. The environment builder never reads `os.environ`.

**Honest limit.** No option satisfies the draft's literal *"one plain call
through the client's ordinary execution path"* together with C-2's separate
byte-exact streams. Every viable option therefore needs baseline amendment
**D-1** (proposal §5.3). If Peter Duscha declines D-1, C-11 stays open.

**Findings for the later implementation:**

* **F-1.** The exact §5 text is not a committed guard test case.
* **F-2.** A capture session cannot be reopened, so there is one entry process
  per pass.
* **F-3.** `guard-git.py`'s decision depends on the working directory's branch,
  so the canonical evaluation must be branch-independent.

## 2. Requirements addressed (assignment §3–§5)

| Requirement | Where |
|---|---|
| complete trust boundary, request → argv | proposal §4 (direct §4.1, captured §4.2) |
| at least two viable options, each assessed on all ten criteria | §6.1 (O-1 … O-4), §6.2 matrix, §6.3 disposition |
| unsafe and non-solutions rejected explicitly | §8, including all five the assignment names |
| one recommendation with a precise reason, or the minimum decision | §1, §6.3; D-1 in §5.3 |
| closed typed environment contract, for `rsync` and for `ssh` separately | §7.2 matrix (both columns), key sets, §7.1 equality |
| key sets, grammar and limits; refusals for duplicate, empty, NUL, `=` and unexpected keys | §7.3, §7.7 |
| authentication without reading a credential or inheriting | §7.4, M-1 |
| digest-binding a non-literal value without recording content | §7.4, §7.8 |
| `HOME`, configuration and known-hosts reliance | §7.5 |
| `SSH_AUTH_SOCK` requirement and pinning | §7.4 |
| `rsync`'s child `ssh` | §7.1, §7.2 `PATH`/`RSYNC_RSH` rows, PO-2 |
| operator-facing refusal classes | §6.5, §7.7 |
| tests: empty inherited environment, missing input, extra variables, mutated values, direct versus captured | §10.2 T-E1, T-E3, T-E4, T-E5, T-E9; §10.1 T-G3 |
| interfaces, manifest impact, rollout and rollback, maintainer decisions | §9, §11, §12, §13 |

**Proposed but not implemented:** everything in the proposal. No hook, gate,
catalogue, environment builder, entry point, wrapper, wiring or flag exists.

## 3. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md` | **new** — the proposal |
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md` | **new** — this handback |
| `docs/review/Handover information` | concise return-state pointer added; assignment and restrictions unchanged |
| `docs/project-management/status.md` | current-status block updated to the return state; records list gains the two new files |
| `docs/implementation-plan.md` §20 | new current action (Codex reviews); the assignment paragraph is relabelled *Superseded action* with its text unchanged |
| `docs/operations/disposable-test-server.md` | a *Restriction at review return* banner is added. Earlier banners are unchanged |

**Nothing else changed:**

* no Python, hook, hook test, `settings.json`, manifest source or generated
  artifact;
* not the operational draft, whose SHA-256 is still `5c6046fc…dcca7de6`;
* not §5's command;
* no configuration and no executable file; and
* no historical or archived record.

No migrations were added. The manifest stays at version 26, digest
`526dd446…`, and was not regenerated.

## 4. Security implications

* **The recommended boundary is stricter than the direct path for every
  agent.** The in-process gate applies to non-Claude operators, who have no
  hooks. It also makes the captured path at least as strict as the direct
  path's most restrictive branch context.
* **Residuals are stated plainly** (proposal §6.9, §7.4):
  * **R-1.** The client-hook layer can be sidestepped by disguising the
    invocation. The in-process gate cannot be sidestepped.
  * **R-2.** The system binaries are trusted.
  * **R-3.** The SSH configuration and `known_hosts` sit outside the manifest.
  * **R-4.** Loader variables in the entry process are refused by name only.
  * **R-5.** The socket could be swapped between the `lstat` check and use.
* **`StrictHostKeyChecking accept-new`** means a missing known-hosts entry is
  silently trusted on first use and written on the repository host. This is
  raised as M-3. The environment cannot fix it.
* **Adding the hook files to the covered sources** means any hook change
  invalidates the reviewed digest. That is intended.

## 5. Commands run and results

Every command below was read-only, local to the repository host, and issued
through the client's ordinary path. No interpreter or test suite was run.

| Command | Result |
|---|---|
| `cat` / `sed -n` / `grep -n` of the assignment, AGENTS.md, Handover, plan §0, §16, §20, draft, test-server doc, hook sources, `test_guards.py`, `settings.json`, `boundary.py`, `capture_mechanism.py`, `capture_contract.py`, `review_manifest.py`, status, prior handback | read. No secret file was named or opened |
| `sha256sum` over the cited inputs (proposal §2.1) | digests as cited |
| extraction of the fenced `bash` block from draft §5 and test-server §3.2, string comparison, `sha256sum`, `wc` | **identical**; 381 bytes, 12 lines, no trailing newline; `4b4096d7…9cc` |
| `git status --short \| wc -l` | 58 entries before this work. Unrelated user changes were preserved |
| `git diff --check` and link checks (§6) | see §6 |

## 6. Documentation checks

| Check | Result |
|---|---|
| `git diff --check` over the four edited tracked files | exit 0; no whitespace error |
| `git diff --no-index --check /dev/null <new file>` for both new files | no whitespace error printed (exit 1 only signals the difference) |
| relative-link resolution (Python script, `pathlib`) over the six touched files | 309 links; 3 reported unresolved, all pre-existing `%20`-encoded links to `Handover information` in `implementation-plan.md` and `disposable-test-server.md` that resolve once URL-decoded; **0 broken links introduced** |
| `git status --short \| wc -l` after the work | 60 (58 before, plus the two new files); unrelated changes preserved |

## 7. Checks not run, and why

* **The hook was not run on the §5 text (F-1 / PO-4).** The assignment forbids
  running it against a real command as a probe. Hook source and committed
  synthetic tests were read only.
* **No test suite, formatter, linter or type checker was run.** No code
  changed, and the assignment requires none.
* **No SSH, rsync, `ssh -G`, host, agent, socket, known-hosts, configuration,
  environment or credential inspection was made.** It is prohibited. PO-1 to
  PO-3 remain open.
* **The manifest was not regenerated and no dry run was performed.** No
  covered source changed, and the assignment forbids an increment.
* **No commit or push was made.** Not authorized.

## 8. Configuration and deployment changes

None.

## 9. Rollback

* **For this return:** delete the two new files and revert the four pointer
  edits.
* **For the later implementation:** see proposal §12.

## 10. Unresolved questions and proposed Codex review focus

**Decisions for Peter Duscha:** D-1, MD-C11, and M-1 … M-8 (proposal §13).

**Review questions for Codex:**

1. **Is D-1 really necessary?** Is there a design that meets C-2 with the
   operator's client call being the plain §5 text, without hiding or rerouting
   it? If there is, O-1 and O-2 are over-built.
2. **Does O-2's in-process gate preserve the direct decision?**
   * Is executing the hook files' own digest-verified bytes, with the branch
     context forced across `{main, master, non-default, ""}`, equivalent to the
     client decision or strictly stronger in every case?
   * Is T-G3 a sufficient equivalence test?
3. **Is the capture path a new way to run what the direct path refuses?** With
   no caller argv, a closed catalogue and a pinned token-vector comparison, can
   any route through `ActRequest`, `CaptureSession` or `StreamCaptureLauncher`
   execute a vector that is not a catalogue entry?
4. **Parser fidelity (§6.7).** Is the accepted subset of shell syntax exactly
   what `bash` and `guard-secrets.py`'s model agree on? Is the double-quote
   escape set right for `A1-17`?
5. **Environment completeness (§7.2).**
   * Is any variable that `rsync` 3.x or OpenSSH consult missing from the
     matrix?
   * Is `PATH=/usr/bin` sufficient for `rsync`'s child `ssh`?
   * Are AS-2 to AS-4 correct for the versions likely on the repository host?
6. **Authentication (M-1).**
   * Is M-1b's `lstat`-only socket check adequate?
   * Is rejecting a digest-checked ambient socket (M-1c) the right call?
7. **`accept-new` (M-3).** Should RP-11 admission require (b) or (c), and is
   either within a later repository-only assignment?
8. **Non-Claude behaviour.** Does the entry's own gate give Codex-operated
   passes the same guarantee, given that a Codex operator's *direct* path has
   no hook at all?
9. **Manifest (§11).**
   * Is covering `.claude/settings.json` right?
   * Should `test_guards.py` also be covered?
   * Is the serialised catalogue and contract data sufficient for the
     reviewed digest?
10. **F-2 and M-6.** Is a per-pass invocation with catalogue-encoded stop
    predicates compatible with the draft's operator duties, or does it need its
    own design pass before implementation?

## 11. Current-state pointers and return state

Pointers were updated as listed in §3.

**Return state:** Claude has stopped. Codex reviews independently, then Peter
Duscha chooses an option and the decisions of §10 or requests remediation. **No
implementation assignment exists until that decision is recorded.**

**Checks at return:** as §6 states. No other check applies.

Throughout: RP-11 remains unwired and unmet; neither pass is executable or
authorized; `plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A
remains conditional; and Package 5.0 remains not ready.
