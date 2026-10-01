# Claude handback — R4-D1-R2 remediation of the LB-2 system-manager environment

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D1-R2`

Date: 2026-09-29

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md)
(SHA-256 `77fbf40f7c019cebc17bb87c6ccca89f5e0b08da37153268cb9eeaf5cab8cdb6`)

Controlling review:
[`project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md`](project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md)
(`C-P5.0-R5-RP11-I1-R3-R4-D1-R1-REV1`, SHA-256
`04cef19fa66ca1cc1be27209238e75adf11ce3b2df3ca4c5448ef61b3e243c67`)

Amended proposal (in place):
[`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md)

* the bytes Codex re-reviewed: SHA-256
  `a402f579e3e8276e092cd74b814ad25da2e37ac0b40ceccdc9f8937c62a49368`,
  1859 lines;
* the amended bytes: SHA-256
  `f6405cd94a826e7883b80589c1edcd2be1e5b56b4481987d7cacdea96312f70b`,
  2539 lines.

The R4-D1 and R4-D1-R1 handbacks and both Codex reviews are unchanged.

State: **returned as documentation only, for mandatory independent Codex
re-review. Claude has stopped.** `R4-D1-R1-1` is not claimed closed. **No
recommendation is ready.** Nothing is accepted, decided or implemented.

## 1. Summary

**Codex's finding is confirmed.** The R1 LB-2 unit added `PATH` and `LC_ALL`
to an environment that is open. A system unit's environment is assembled from
three sources (proposal §4.4.3.1, S-1):

* the manager's global environment, which is fed by `DefaultEnvironment=`,
  `systemd.setenv=`, generators, locale and run-time `set-environment`;
* the variables the manager defines itself; and
* the unit's own settings.

The only filter is `UnsetEnvironment=`, a finite list of names with no pattern
form (S-4). **No unit directive builds an allow-list** (§4.4.3.3). The block is
assembled immediately before `execve` (S-6), and it can change at run time
(S-7). A dynamically linked `ExecStart=` image such as `/usr/bin/python3.12` is
therefore loaded under whatever the manager holds.

**Outcome, in the assignment's §4 terms:**

* **Outcome 3 for LB-2 as returned.** It is withdrawn as prevention. Two
  variants are also assessed: LB-2U, which adds an `UnsetEnvironment=`
  deny-list, is rejected. LB-2T trusts the manager's state after review; it is
  review, not prevention, and it contradicts T-A as defined, so it is
  admissible only under an explicit M-10 narrowing (§4.4.3.3).
* **The corrected mechanism is specified (outcome-1 shape).** Under **LB-2S**
  the unit's `ExecStart=` names a root-installed, statically linked first
  image, `rp11-launch`. Its start-up reads no environment (**PO-9**). It
  selects only a grammar-checked `INVOCATION_ID`, resets descriptors, signal
  state, umask and working directory, and calls `execve` on the interpreter
  with the literal `{INVOCATION_ID, LC_ALL=C, PATH=/usr/bin}`. The entry's
  allow-list is thus built by reviewed code before the entry's loader runs
  (§4.4.3.4). This also depends on **PO-14**: the installed systemd must not
  load its executor under the unit's block (AS-13).
* **An outcome-2 component, stated explicitly.** Manager **execution
  settings** cannot be excluded by any unit text (S-5, R-10). These are
  `Default*=` values, top-level and unit drop-ins, run-time properties and
  unit-path precedence. They are trusted root input, reviewed and bound at H-1
  (installation) and H-2 (before each pass). That is review, not prevention,
  and it is M-10's to accept.
* **LB-1 and LB-3 are reassessed** (§4.4.2, §4.4.4).
  * **LB-1** meets the environment rule, because it is the same static image,
    but it inherits client execution state.
  * **LB-3** is not ready. `sudo` merges the PAM environment (AS-12), which is
    the analogue of the manager's environment, and the `sudo` image is loaded
    under a glibc secure-mode deny-list filter. `sudo` is also currently
    prohibited.
* **No recommendation is ready** (§0-R2, §1, §13). The minimum decisions are:
  * **M-14 (new):** accept a compiled static image as a new build dependency,
    and commission its runtime design against PO-9. A glibc-static build is
    presumed not to qualify (AS-11);
  * **M-10 (revised):** T-A stays in scope, with manager execution settings
    trusted as reviewed root input; and
  * **M-9**, with LB-2S as the conditional direction.

**Threat scope.** T-A is not redefined. Ambient manager state is T-A (§4.3).
The R1 bytes listed "the manager's environment" as trusted root state in R-8
while calling T-A in scope. That is withdrawn (Appendix B). Under LB-2S the
manager's environment is neither trusted nor needed.

**The diagnostic stays diagnostic.** `rp11-entry-env/1` is now a literal
contract written by `rp11-launch` (§7.9). The Python check is diagnostic only
and is never credited with prevention.

**R4-D1-2 is not reopened.** The only adjacent change is D-1's issue clause
(§5.3). Its bracket becomes `[M-9 = LB-2S]`, and its environment sentence
changes, because the environment source changed. The client-inspected
invocation is unchanged. §5.4, §6.6.1, §6.6.2, D-2 and M-11 are unchanged.

## 2. Finding → amended sections

| Assignment requirement (§3) | Amended proposal sections |
|---|---|
| exact systemd system-manager semantics for `Environment=`, `DefaultEnvironment=`, manager run-time environment, `PassEnvironment=`, `UnsetEnvironment=`, `User=`, PAM and systemd-generated variables | §4.4.3.1 S-1 … S-10; AS-6 (rewritten), AS-13 |
| distinguish unit bytes, PID 1-held state, manager configuration, run-time APIs, derived variables and post-`execve` additions | §4.4.3.2 table, column "Class" (E-1 … E-11) |
| every source reaching the entry's `execve`, which wins on collision, and when filtering occurs | §4.4.3.2 (precedence column, "Collision and filtering"); S-1, S-6 |
| whether the unit can build a true allow-list before `execve` | §4.4.3.3 (no), §4.4.3.4 ("The allow-list question, answered for LB-2S") |
| `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, debug and profile variables, `GLIBC_TUNABLES`, `MALLOC_*` and platform equivalents, with no deny-list credited as closed | §4.3 reassessment table (client and manager rows); §4.4.1 (added rows, LB-2U); §4.4.3.3; §8 (added rows); AS-11 |
| the Python `rp11-entry-env/1` check as diagnostic only | §7.9 (rewritten); §6.5; §4.4.3.5 "diagnostic" row; T-B7 |
| the earliest trusted component, how it is bound, and what root-controlled state stays outside the manifest | §4.2 C-5; §4.3 "Earliest trusted component" (LB-2S); §4.4.3.4 "What reaches which image"; §11 "What the manifest cannot bind" |
| whether ambient manager state is inside T-A, with no silent redefinition | §0-R2 "Threat scope"; §4.3 T-A (R2 paragraph); §6.9 R-8 (amended); §13 M-10 (revised) |
| reassess the unit, pass configuration, installation record, drop-in and manager-state checks, admission, rollback and later drill | §4.4.3.4 (unit, launcher, polkit, pass configuration); §4.4.3.7 (H-1 record, H-2 check, rollback, PO-16 drill); §6.5; §12 (I-7, H-1, H-2) |
| keep configuration-text property, installation-time check, host proof obligation and prevention distinct | §4.4.3.5 classification table |
| dependent statements: AS-6; §4.2 and §4.3 timing; LB-2 §4.4.3; §4.4.5; non-Claude; fail-closed matrix; residual risks; `rp11-entry-env/1`; interfaces; tests; manifest; rollout and rollback; M-9, M-10 and M-12; PO-8 and new obligations; the conditional recommendation; limitation and state language | AS-6; §4.2; §4.3; §4.4.3; §4.4.5; §4.4.6; §6.5; §6.9 (R-8, R-10, R-11); §7.9; §9; §10.3 (T-B1, T-B7, T-B8, T-B13 … T-B15); §11; §12; §13 (M-9, M-10, M-12, M-14, MD-C11, D-1); §14 (PO-8, PO-9, PO-10 revised; PO-14 … PO-16 new); §1 and §13 conditional direction; header state line; §15 |
| outcome discipline (assignment §4) | §0-R2 "Outcome"; §4.4.7; §13 |
| dated R2 note and every withdrawn or narrowed claim | §0-R2; **Appendix B** (26 rows, each verified verbatim against `a402f579…`) |

## 3. Requirements implemented

**Documentation only.** Nothing was implemented: no launcher, static image,
unit, polkit rule, sudoers rule, guard bridge, catalogue, environment builder,
parser, entry point, bootstrap, wrapper, session transport, wiring or feature
flag.

## 4. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-proposal.md` | amended in place: provenance header and state line, §0-R2, the sections in §2, and Appendix B. §4.4.3 and §7.9 were rewritten |
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | title, and a concise R2 return-state section. The assignment, restrictions and archive links are unchanged |
| `docs/project-management/status.md` | new current-status block; the previous block is relabelled *Superseded current status* with its text unchanged; the records list gains this handback |
| `docs/implementation-plan.md` §20 | new current action (Codex re-reviews); the previous current action is relabelled *Superseded current action* with its text unchanged |
| `docs/operations/disposable-test-server.md` | a *Restriction at R4-D1-R2 remediation return* banner is added. Earlier banners are unchanged |

**Not changed:**

* earlier handbacks, reviews, assignments and any archive;
* any Python, hook, hook test, `settings.json`, manifest source or generated
  artifact;
* the operational draft (still
  `5c6046fc3dc0b9a931cc32076233b1ea9185dc14c5d0ea1abc193687dcca7de6`) and §5's
  command;
* any configuration, systemd, polkit or executable file.

**Provenance caveat, repeated from R1 (Q-10 there).** The proposal file is
still **untracked** in Git. The bytes Codex re-reviewed (`a402f579…`) are
identified in the repository only by their SHA-256 and by Appendix B's verbatim
quotations. A verbatim copy is held in this session's scratch directory,
`proposal-r1-reviewed.md`, which is not durable. The same applies to the R4-D1
bytes (`e026ecf5…`). Peter Duscha may want verbatim snapshots committed or
archived.

## 5. Migrations

None.

## 6. Security implications

* **A prevention claim is withdrawn.** The R1 bytes credited the LB-2 unit
  with keeping loader state from the entry ("**yes** (PO-8)"). That was untrue
  for manager-level state, and it is withdrawn with its dependents
  (Appendix B).
* **LB-2S moves the environment boundary into one small component.** That
  component is a static image whose correctness depends on two things: its
  runtime's start-up (PO-9) and the installed systemd's executor (PO-14). If
  either fails, LB-2S is withdrawn (R-11). Neither is repository-testable
  here.
* **A trust is stated rather than hidden.** Manager execution settings can
  shape the entry's limits, its confinement and, at worst, the loaded
  `ExecStart=`. H-1 and H-2 review them at one moment each. They are not
  prevented (R-10), and M-10 must accept this explicitly.
* **A new build dependency.** Under M-14, a compiled artifact enters a
  pure-Python repository. That is a supply-chain surface: toolchain,
  reproducibility and installed-digest binding. It needs its own design pass.
* **No environment content is recorded.** LB-2S does not inspect or record the
  manager's global environment (§4.4.3.5), which keeps C-9 intact.
* **R1's other residuals are unchanged:** R-6 (client hooks under *E_c*), R-7
  (T-B forgery) and R-9 (A0-05 and A0-06).

## 7. Commands run and results

The session used the Bash, Read, Edit and Write tools. No test suite,
interpreter-entry probe, loader experiment, hook run, `systemctl`,
`systemd-run`, `loginctl`, `busctl`, `sudo`, `ssh`, `rsync` or network
command was run. No runtime or system path on the host was listed or
inspected.

| Command | Result |
|---|---|
| `cat`, `sed -n`, `grep` and `wc` of AGENTS.md, the Handover, the plan's reading map, §0, §16 and §20, the R2 assignment, the R4-D1 and R1 assignments, the proposal, both Claude handbacks, both Codex reviews, and the heads of `status.md` and the test-server document | read. No secret file was named or opened |
| `sha256sum` of the proposal before amendment, the R2 assignment and the controlling review | as cited above. The proposal matched the R1 return (`a402f579…`) |
| `cp` of the proposal into the session scratch directory; `git status --short` into a scratch file | 65 status entries before this work |
| Python one-off scripts that spliced amended text into the proposal, each asserting that its anchor occurred exactly once | applied. The replaced §4.4.3 and §7.9 texts were saved to scratch before splicing |
| a Python script comparing every Appendix B quotation with the R1 scratch copy, whitespace-normalised, with blockquote markers and table-escaped pipes removed | **26 of 26 found verbatim** |
| `sha256sum` of the amended proposal and the operational draft | `f6405cd9…12f70b`; draft `5c6046fc…`, unchanged |
| `git diff --check`, `git diff --no-index --check`, link check and `git status` | §8 |

No guard or tool refusal occurred.

## 8. Documentation checks

| Check | Result |
|---|---|
| `git diff --check` over the four edited tracked files | exit 0; no whitespace error |
| `git diff --no-index --check /dev/null <file>` for the proposal and this handback | no whitespace error printed (exit 1 only signals the difference). Trailing-space count 0 in both |
| relative-link resolution (Python, `pathlib`) over the six touched files | see the figure recorded after this handback was written, below |
| `git status --short \| wc -l` | 65 before; 66 after (this handback added). The proposal was already untracked, and the four pointer files were already modified. Unrelated user changes were preserved |

**Link-check figure:** 345 links. 3 resolve only once URL-decoded; these are
the pre-existing `%20`-encoded links to `Handover information`. **0 broken
links.**

## 9. Checks not run, and why

* **No test suite, formatter, linter or type checker.** No code changed, and
  the assignment requires none.
* **No loader experiment, interpreter-entry probe or hook run.** The
  assignment forbids them. PO-9 and PO-14 … PO-16 are open.
* **No `systemctl`, `systemd-run`, `busctl`, polkit, `sudo`, `ssh`, `rsync` or
  host check.** S-1 … S-10 and AS-11 … AS-13 are stated from documentation
  knowledge and are **not verified** against any installed version. PO-8
  (revised) requires that citation.
* **The manifest was not regenerated or incremented.** No covered source
  changed. The manifest stays at version 26, digest `526dd446…`.
* **No commit or push.** Not authorized.

## 10. Configuration, deployment and rollback

* **Configuration and deployment:** none.
* **Rollback of this return:**
  * delete this handback;
  * restore the proposal to the re-reviewed bytes (`a402f579…`), from the
    non-durable scratch copy (§4 caveat), or rebuild them by reversing
    Appendix B and removing the R2-marked text;
  * revert the four pointer edits.
* **Rollback of the later implementation:** proposal §12 and §4.4.3.7.

## 11. Unresolved assumptions, proof obligations, decisions and re-review questions

**Assumptions:** AS-6 (rewritten), AS-11, AS-12 and AS-13, together with
semantics S-1 … S-10. They are unverified against any host.

**Proof obligations:**

* PO-8 is revised and **no longer carries an environment-prevention claim**;
* PO-9 is extended to LB-2S and is **load-bearing**;
* PO-10 is extended to the PAM merge;
* PO-14 is new and **load-bearing**; and
* PO-15 and PO-16 are new.

PO-1 … PO-7 and PO-11 … PO-13 are unchanged.

**Maintainer decisions, in order** (proposal §13):

* M-9, M-14 and M-10 (revised);
* then D-2 and M-11;
* then D-1;
* then MD-C11.

M-1 … M-8, M-12 and M-13 are unchanged in substance.

**Questions for Codex:**

1. **Semantics.** Are S-1 … S-10 correct and complete for current systemd?
   * Is there any source of a system unit's environment missing from E-1 …
     E-11?
   * Is there any directive, in any version, that discards the manager's
     global environment and would make S-4 false?
2. **Allow-list conclusion.** Is §4.4.3.3's conclusion right that no unit text
   can close a dynamically linked `ExecStart=` image's environment? Is LB-2T
   correctly characterised as review, not prevention?
3. **LB-2S.** Does `rp11-launch/1` (§4.4.3.4) establish a closed environment
   before the entry's `execve`, given PO-9 and PO-14?
   * Is its `INVOCATION_ID` selection an acceptable allow-list read, or does
     it reintroduce a dependency on the block?
   * Is it correctly distinguished from the rejected cleansing forms
     (§4.4.1)?
4. **PO-14.** Is AS-13 right that `systemd-executor` starts under PID 1's own
   environment and not the unit's block? If not, is withdrawing LB-2S for that
   version the correct consequence, or is another fix available?
5. **PO-9 and AS-11.** Is excluding a glibc-static build correct? Should M-14
   name candidate runtimes now, or leave that wholly to the design pass?
6. **Threat scope.** Is the treatment of ambient manager state consistent?
   * Environment: prevented under LB-2S.
   * Execution settings: trusted and reviewed under R-10.

   Is R-10 an acceptable explicit trust, or does it amount to a redefinition
   of T-A that M-10 must decide differently?
7. **LB-3 and LB-1.** Is the PAM-merge reasoning (AS-12) sound for LB-3? Is
   LB-1 correctly placed: meeting the environment rule but inheriting client
   execution state?
8. **Classification.** Does §4.4.3.5 keep text properties, installation
   checks, host proof obligations, prevention and diagnostics strictly apart?
   Does any row still credit a diagnostic or a review with prevention?
9. **Manifest.** Is "what the manifest cannot bind" (§11) complete and
   truthful for LB-2S, including the toolchain, the loaded configuration and
   PO-9 and PO-14?
10. **Recommendation discipline.** Is "no recommendation is ready", with a
    labelled conditional direction on M-9, M-14 and M-10, consistent with
    assignment §4? Or should the conditional direction be removed?
11. **R4-D1-2 scope.** Is the D-1 issue-clause change a traced consequence
    only, leaving R4-D1-2's remediated design intact?

## 12. Return state

Pointers were updated as listed in §4. **Claude has stopped.**

* **Next:** Codex independently re-reviews the following:
  * whether LB-2S prevents unreviewed loader state before the entry starts;
  * the exact system-manager semantics;
  * threat-scope consistency;
  * non-Claude behaviour;
  * the manifest limits; and
  * the honesty of the conditional direction.

  Peter Duscha then decides whether to accept a design direction or to request
  further remediation.
* **No implementation assignment exists** until that decision is recorded.

Throughout: RP-11 remains unwired and unmet; neither pass is executable or
authorized; `plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A
remains conditional; and Package 5.0 remains not ready.
