# Claude handback — remediation of the C-11 launcher-contract design

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D1-R1`

Date: 2026-09-29

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-claude-prompt.md)
(SHA-256 `7ca4cf766377e09307bb5a7786fb630ffcff210ad423fdba3170c66e5c5ffc1b`)

Controlling review:
[`project-review-2026-09-29-p5-r5-rp11-r4-d1-c11-launcher-contract.md`](project-review-2026-09-29-p5-r5-rp11-r4-d1-c11-launcher-contract.md)
(`C-P5.0-R5-RP11-I1-R3-R4-D1-REV1`, SHA-256
`e5e62cd6a9865fbb0521ef72dbfcf5e49598a0cdf732153d6cdfe54ee0aef4dc`)

Amended proposal (in place):
[`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)

* the bytes Codex reviewed: SHA-256
  `e026ecf51f2dacf15bcc1871b97f09b72cceadb42bc4d968139080c4e2ff0751`;
* the amended bytes: SHA-256
  `a402f579e3e8276e092cd74b814ad25da2e37ac0b40ceccdc9f8937c62a49368`,
  1859 lines.

The original R4-D1 handback is unchanged.

State: **returned as documentation only, for mandatory independent Codex
re-review. Claude has stopped.** Neither Blocking finding is claimed closed.
Nothing is accepted, decided or implemented.

## 1. Summary

The amended proposal is a **decision-ready impossibility result with the
minimum maintainer choices**. It is not a recommendation that satisfies
today's constraints. It also states a **conditional direction**: what the
proposal would recommend if Peter Duscha makes the named choices.

**R4-D1-1: loader state acts before the entry.**

* **The finding is confirmed.** The client's shell, the client's hooks
  (`#!/usr/bin/env python3`, OB-11) and every image the shell starts are
  loaded with the client environment *E_c* before any repository byte runs.
* **The impossibility.** With a repository-only implementation and no host
  configuration, **no design on the client's ordinary path prevents ambient
  loader state from reaching the entry** (proposal §4.3, §4.4.7).
* **What prevention needs.** An exec boundary whose process state does not
  come from *E_c*. Three are specified with exact client-inspected invocations:
  * **LB-2**, a system service-manager unit started by a polkit-restricted
    `systemctl start --wait`. It is the only option that also removes seccomp,
    Landlock, namespace and ancestry inheritance;
  * **LB-3**, a single-command `sudo` rule; and
  * **LB-1**, a static first-exec launcher.
* **The cost.** Each needs host provisioning (H-1) or a new build dependency,
  so it is decision **M-9**. Threat scope is decision **M-10**.
* **What stays exposed under every option.** The client shell and hooks, as on
  the direct path today (R-6).
* **The old name check** is kept only as the diagnostic
  `entry-environment-unexpected`.

**R4-D1-2: the hook cannot see A1-12's final command.**

* **The finding is confirmed.** Every catalogue entry is classified by when its
  final text becomes knowable (§6.6.1). **In Pass A, A1-12 is the only
  runtime-completed text.**
* **Why A1-12 can be fixed.** The draft already stops the pass whenever A1-11
  differs from the pinned statement (§4.6, §4.7(4); OB-14). So whenever A1-12
  runs, its value is known before the pass.
* **The remedy (D-2).** Either **D-2a**, a reviewed literal
  `sha256sum /opt/freedom-blades/runtime/venv-web/bin/python`, or **D-2b**,
  instantiation from the pinned statement. Either makes every Pass A text
  inspectable before start.
* **The alternatives.** R-c (a control channel) and R-d (split sessions) are
  rejected. R-e, a narrow requirement amendment, is the fallback.
* **Pass B.** It has runtime slots that cannot exist before start: B2's
  `--at`, `--requested-at` and the B1-Q flags. It also has K-U placeholders
  and a mid-session live gate (B6.3, F-4). **The pre-start criterion is
  unsatisfiable for Pass B as drafted.** Decision M-11 scopes this C-11
  decision to Pass A.
* **D-1 is rewritten** (§5.3, §5.4). It separates literal text, template,
  typed instantiation and executed argv, and it states which layer inspects
  each and when.

**Conditional direction**, only if M-9 = LB-2, M-10 = T-A, D-2 = D-2a,
M-11 = Pass A only, M-12 = root-installed, and D-1 as rewritten is accepted:
**O-2, carried by LB-2, for Pass A.**

## 2. Finding → amended sections

| Finding | Required correction (assignment) | Amended proposal sections |
|---|---|---|
| **R4-D1-1** | a complete, timed trust boundary from the running client to the entry | §4.3 (stages T0 … T7, timing rule, T-A/T-B) |
| | distinguish inputs to the client or shell from inputs to each newly executed image | §4.3 stages table, columns "image" and "consumed before" |
| | the earliest trusted component, and how its bytes, invocation and environment are bound | §4.3 "Earliest trusted component"; §4.4.3; §7.9 |
| | the dynamic loader consumes `LD_*`, audit, debug and profile variables and platform equivalents first | §4.3 reassessment table, first row; §4.4.1 |
| | prevent, rather than detect, unreviewed loader state in any enforcing process | §4.4.2 … §4.4.5; §4.4.7 (impossibility under current constraints) |
| | reassess interpreter lookup, substitution, working directory, module lookup, shell start-up, Python start-up and descriptors | §4.3 reassessment table (every row; also signals, rlimits, umask, confinement, ancestry, caller values); F-6 |
| | the exact client-inspected invocation per option; no wrapper exemption; §5's text not hidden | §1 table; §4.4.2 … §4.4.5, closing paragraph; §9 grammar |
| | what protects non-Claude agents when hooks are absent | §4.4.6; §6.2 non-Claude row |
| | bind every new component, literal and configuration byte into the manifest and tests | §7.9; §9; §10.3; §11 (with "what the manifest cannot bind"); §12 I-6 and H-1 |
| | at least two viable options, each analysed | LB-1, LB-2 and LB-3 (§4.4.2 … §4.4.4), each on loader timing, bypass, TOCTOU, portability, non-Claude and testability |
| | reject cleansing after an untrusted loader has acted | §4.4.1; §8 (added rows) |
| | if impossible, say so and give the minimum decision | §0; §4.4.7; §13 M-9 and M-10 |
| **R4-D1-2** | enumerate every literal and parameterised entry and when it becomes knowable | §6.6.1 (Pass A entry by entry; Pass B by class) |
| | separately: what the hook inspects, what the gate inspects before X-1, and before each launch | §5.4 table; §6.6.1 closing paragraph |
| | no option called compliant for a K-O text | §5.4 "Consequences"; §6.2 row; §6.3 |
| | compare remedies: separate invocation, granularity, typed operation, narrow amendment | §6.6.2 (R-c, R-d, D-2a and D-2b, R-e) |
| | analyse each against lifecycle, capture, stop transition, record, guard decision and caller argv | §6.6.2 matrix |
| | rewrite D-1 | §5.3 |
| | revise the option matrix, recommendation, threats, records, interfaces, tests, manifest, rollout and decisions | §6.2, §6.3, §6.9, §6.8, §9, §10.4, §11, §12, §13 |
| | do not treat a template as inspecting its instantiation | §5.4 "template" row; §8 added row; T-K6 |

Every withdrawn claim is quoted verbatim in the proposal's Appendix A.

## 3. Requirements implemented

**Documentation only.** Nothing was implemented: no launcher, guard bridge,
catalogue, environment builder, parser, entry point, bootstrap, wrapper,
session transport, unit, polkit rule, sudoers rule, wiring or feature flag.

## 4. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md` | amended in place, with a provenance header, §0 remediation note, the amended sections listed in §2, and Appendix A |
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | concise return-state pointer added; assignment and restrictions unchanged |
| `docs/project-management/status.md` | current-status block updated to the return state; records list gains this handback |
| `docs/implementation-plan.md` §20 | new current action (Codex re-reviews); the previous current action is relabelled *Superseded action*, with its text unchanged |
| `docs/operations/disposable-test-server.md` | a *Restriction at remediation return* banner is added. Earlier banners are unchanged |

**Not changed:**

* the original R4-D1 handback, the Codex review and any archive;
* any Python, hook, hook test, `settings.json`, manifest source or generated
  artifact;
* the operational draft (still `5c6046fc…dcca7de6`) and §5's command;
* any configuration or executable file.

**Provenance caveat.** The proposal file is **untracked** in Git. The bytes
Codex reviewed are therefore identified in the repository only by their SHA-256
and by Appendix A's verbatim quotations, not by a Git object. A verbatim copy
is held outside the repository, in this session's scratch directory, which is
not durable. Peter Duscha may want a verbatim snapshot committed or archived
before the in-place amendment becomes the only copy (§11, question Q-10).

## 5. Migrations

None.

## 6. Security implications

* **Earlier claims were untrue, and are corrected here.** The reviewed bytes
  said the in-process gate "cannot be bypassed", that hook absence has "no
  effect on enforcement", and that non-Claude callers were "fully" protected.
  None of that holds without an M-9 boundary, and each claim is withdrawn.
* **Without M-9, C-11 stays open.** This is presented as a decision, not as a
  residual risk.
* **The client-hook layer was exposed before this work, on the direct path
  too.** It starts through `/usr/bin/env python3` under the client
  environment (F-5, R-6). This amendment makes no change to it. M-13 offers
  optional narrowing.
* **The evidence package imports two uncovered modules** (F-6):
  `application/__init__.py` and `application/idempotency.py` are imported but
  not covered by the review digest. An entry verifying `COVERED_SOURCES` would
  still execute them unverified. The closure must be covered (§11, T-B4).
* **A0-05 and A0-06 run under the client environment, outside RP-11** (R-9).
  They are flagged for Codex, not changed.
* **Same-account forgery (T-B) is not defended by any option** (R-7, M-10).

## 7. Commands run and results

The session used the Bash, Read, Edit and Write tools, and one AskUserQuestion.
No test suite, interpreter-entry probe, loader experiment, hook probe, `ssh`,
`rsync`, `systemctl`, `sudo` or network command was run.

| Command | Result |
|---|---|
| `cat`, `sed -n`, `grep` and `wc` of the assignment, AGENTS.md, Handover, the plan's reading map, §0, §16 and §20, the original assignment, proposal and handback, the Codex review, the draft (§4.5 … §7 in full), the hook sources, `settings.json` and the status and test-server heads | read. No secret file was named or opened |
| `grep` of `import` lines under `tools/phase_5_0_evidence`, and of `application/__init__.py` and `idempotency.py`; `sed -n` of `review_manifest.py` `COVERED_SOURCES` | OB-13 and F-6 |
| `sha256sum` of the draft, the proposal before amendment, the assignment and the review | as cited |
| `cp` of the proposal into the session scratch directory, and `git status --short` into a scratch file | 62 status entries before this work |
| Python one-off scripts that spliced amended sections into the proposal, each asserting that its anchor text occurred exactly once | applied |
| **`ls -la /opt/freedom-blades/runtime/venv-web/bin/python`**, run inadvertently as part of a combined read command | **Disclosure.** This lists a runtime path on the repository host, which is arguably host inspection and outside this assignment's allowance. Its output was **not used** in the proposal or this handback, and the command was not repeated |
| a Bash command that would have inserted §10.3 and §10.4 | **refused by `guard-secrets.py`** (below). Not executed; no change |
| three Bash attempts, for the quotation check and `git diff --check` | not run. The client's auto-mode safety classifier returned no verdict, which is a transient tool failure and not a refusal. They were repeated unchanged once it recovered |
| `git diff --check`, link checks, a re-check of Appendix A's quotations, the final `sha256sum` of the proposal and draft, and `git status` | §8 |

**Guard refusal and maintainer direction, verbatim.** The refused Bash command
was a Python heredoc that edited the proposal. Its text contained the existing
T-G14 test description, which names a shell `cat` of the environment file. The
hook's output:

> PreToolUse:Bash hook error: [$CLAUDE_PROJECT_DIR/.claude/hooks/guard-secrets.py]: Refused by the repository secrets guard (.agents/AGENTS.md, Configuration and secrets).
> The call would read or publish '.env', a secret-bearing artifact that must never be read, printed, copied, modified or committed.
> If a secret may have entered Git history or logs, stop and notify a maintainer: deleting the visible line is insufficient and the credential must be rotated.
> `.env.example` is exempt and may be edited with safe placeholders.

Claude treated this as a stop (assignment §6; CLAUDE.md). It did not retry in
another form, and it asked the maintainer. The question and answer were:

> **Q:** "guard-secrets.py refused a Bash command that edited documentation text. The text already contains the literal test string `; cat .env` in the proposal's T-G14 row. How should I proceed?"
> **A:** "Continue via Edit/Write" — *"You authorize finishing the documentation with the Edit/Write tools, which the guard checks by file path only. The refusal and your direction are recorded verbatim in the handback. No Bash command will carry that literal."*

After that direction, the remaining edits used the Edit and Write tools. No
Bash command carried the literal. No secret file was read, opened or named as a
path operand. The refusal was a pattern match on documentation text, not an
attempted access. **Codex should judge** whether the direction's scope was
respected (Q-11).

## 8. Documentation checks

| Check | Result |
|---|---|
| `git diff --check` over the four edited tracked files | exit 0; no whitespace error |
| `git diff --no-index --check /dev/null <file>` for the two untracked review files | no whitespace error printed (exit 1 only signals the difference). Trailing-space count 0 in both |
| relative-link resolution (Python, `pathlib`) over the six touched files | 325 links. 3 unresolved as written, all the pre-existing `%20`-encoded links to `Handover information` in `implementation-plan.md` and `disposable-test-server.md`, which resolve once decoded. **0 broken links introduced** |
| Appendix A's quotations compared with the reviewed bytes (the scratch copy, `e026ecf5…`), whitespace-normalised | **16 of 16 found verbatim.** The two D-1 quotations match once the blockquote `> ` markers are removed |
| `git status --short \| wc -l` after the work | 63 (62 before, plus this handback). The proposal was already untracked, and the four pointer files were already modified. Unrelated user changes were preserved |
| the operational draft's SHA-256 after the work | `5c6046fc…`, unchanged |

## 9. Checks not run, and why

* **No test suite, formatter, linter or type checker was run.** No code
  changed, and the assignment requires none.
* **No loader experiment, interpreter-entry probe or hook run against a real
  command was performed.** The assignment forbids them. PO-7 … PO-13 remain
  open. In particular, PO-8 (LB-2 prevention) is **not repository-testable**.
* **No `systemctl`, polkit, `sudo`, `ssh`, `rsync` or host check was made.**
  AS-6 … AS-10 are assumptions.
* **The manifest was not regenerated or incremented.** No covered source
  changed. The manifest stays at version 26, digest `526dd446…`.
* **No commit or push.** Not authorized.

## 10. Configuration, deployment and rollback

* **Configuration and deployment:** none.
* **Rollback of this return:**
  * delete this handback;
  * restore the proposal to the reviewed bytes (`e026ecf5…`), for which the
    only full copy is the non-durable scratch copy (§4 caveat), or else rebuild
    it from Appendix A and the unchanged sections;
  * revert the four pointer edits.
* **Rollback of the later implementation:** proposal §12, including H-1.

## 11. Unresolved proof obligations, decisions and Codex re-review questions

**Maintainer decisions** (proposal §13, in the stated order):

* M-9, the launch boundary;
* M-10, threat scope;
* D-2, the A1-12 remedy;
* M-11, Pass A only;
* M-12, the bootstrap location;
* M-13, optional hook narrowing;
* D-1, as rewritten;
* MD-C11; and
* the unchanged M-1 … M-8 (M-5 and M-6 amended).

**Open proof obligations:** PO-1 … PO-3 (unchanged) and PO-7 … PO-13 (new).

**Questions for Codex:**

1. **Timing.** Is §4.3's timing rule and its stage table complete? Is any input
   consumed before T5 missing from the reassessment table (for example
   personality flags, `/proc/self` attributes, controlling-terminal state)?
2. **Impossibility.** Is §4.4.7's result correct: that no repository-only
   design on the ordinary path prevents loader state from reaching the entry?
   Or is there a repository-only mechanism this proposal missed?
3. **LB-2 soundness.** Does a system unit started by `systemctl start` really
   receive no requester-derived state (AS-6, PO-8)? Are the unit, polkit rule
   and pass configuration sufficient and minimal? Is `stop` in the polkit rule
   right?
4. **The earliest trusted component.** Under M-12, the bootstrap is
   root-installed and verifies the repository sources before executing them.
   Is the remaining trust in PID 1, polkit, `/usr/bin/python3.12`, the standard
   library and `ld.so.preload` (R-8) acceptable, and correctly stated?
5. **Diagnostic versus prevention.** Are `entry-environment-unexpected`,
   `entry-boundary-absent` and `entry-unit-mismatch` presented anywhere as
   prevention?
6. **D-2a equivalence.** Is hashing through the venv entry an acceptable
   corroboration of `OP.interpreter_sha256`? Is D-2a+'s bracket needed? Is
   OB-14's reading of §4.6 and §4.7(4) correct, which is what makes D-2b
   byte-identical to the draft?
7. **Knowability.** Is §6.6.1 complete for Pass A? Does any Pass A text depend
   on a pass-produced value other than A1-12?
8. **Pass B.** Is excluding Pass B (M-11) the right scope, and is F-4 (B6.3's
   mid-session human gate) correctly identified as incompatible with per-pass
   M-6?
9. **Manifest.** Is the added coverage (bootstrap, entry environment,
   `application` closure, boundary files) sufficient? Is "what the manifest
   cannot bind" stated truthfully?
10. **Provenance.** Should a verbatim snapshot of the reviewed bytes
    (`e026ecf5…`) be added to the repository, given that the proposal file is
    untracked?
11. **Guard refusal.** Was the continuation after the `guard-secrets.py`
    refusal (§7) within the maintainer's direction and the stop rule?
12. **Disclosure.** Does the inadvertent `ls -la` of the runtime interpreter
    path (§7) need any further record?

## 12. Return state

Pointers were updated as listed in §4. **Claude has stopped.**

* **Next:** Codex independently re-reviews both Blocking findings, the
  corrected trust boundary, parameterised-act timing, non-Claude behaviour,
  environment completeness and manifest implications. Peter Duscha then
  decides whether to accept a design direction or to request further
  remediation.
* **No implementation assignment exists** until that decision is recorded.

Throughout: RP-11 remains unwired and unmet; neither pass is executable or
authorized; `plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A
remains conditional; and Package 5.0 remains not ready.
