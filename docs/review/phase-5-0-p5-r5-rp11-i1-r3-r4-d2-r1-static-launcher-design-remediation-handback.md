# Claude handback — D2-R1 static-launcher design remediation

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D2-R1`

Date: 2026-09-29

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md)
(SHA-256 `57500b5b95822a01c6770368e8352fbefdc6629aba7f5abd82f154d7360ade76`)

Amended proposal:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)

* reviewed D2 bytes: SHA-256
  `adc114bf795985ce1af5c90e3b9d8e7ca1cb012e1551e6eab590cfb8f28d8093`
  (954 lines);
* returned D2-R1 bytes: SHA-256
  `a70f013f77c83f448a03fc08b15b2075aa47efaa09da5e9290af3f1bfc295b81`
  (1 774 lines).

Original D2 assignment (still controlling except as corrected):
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md)

State: **returned as documentation only, for independent Codex re-review.
Claude has stopped. No finding is claimed closed.** Nothing is accepted,
decided, built or implemented. PO-9 and PO-14 remain open.

## 1. Summary

**Outcome: D-S1 retained, not withdrawn.** The amended design supplies a
PO-9 argument that covers every transfer out of fall-through, `ret` included.
It supplies a build and test contract that can be run as written. D-S1 stays
conditional, and it gains one further withdrawal condition (proposal §4.5): if
no build passes the new discipline under any of the fail-closed alternatives
FA-1 … FA-3, LB-2S is withdrawn.

* **`R4-D2-1` (Blocking): the control-flow proof.**
  * A closed set of control-transfer classes, CT-1 … CT-9, is enumerated.
    It covers direct branches and calls, `ret`, `syscall`, `ud2`, faults and
    asynchronous signals. Everything else is forbidden, including
    transactional-memory aborts and string instructions (proposal §5.14.1).
  * **`ret` is permitted** only where RI-1 … RI-7 hold, and never in `_start`
    or `rp11_main` (§5.14.2). The rules require:
    * a statically balanced stack at every instruction;
    * every store other than `push` and `call` to be a constant-displacement
      `%rsp` store strictly inside its own frame; and
    * no inventory system call to receive a user-memory output pointer, and no
      signal handler to be able to exist.

    Together these fix every return target to the instruction after its
    matching direct `call`.
  * **No store address depends on hostile input** (IN-1 … IN-4, §5.14.3). The
    `INVOCATION_ID` copy is 32 constant-index assignments, and the selection
    functions return values only.
  * The evidence is named. The new verifier **T-L10** is mechanical and
    toolchain-free; T-L7 ties the listing to `.text` byte for byte; BI-6 and
    BI-7 are rewritten; **BI-10 and BI-11** are new; human review is
    **HR-1 … HR-6**; and D9-1 gains the new citations **AD-11 and AD-12**.
  * P-3, P-4, P-5 and the §6.1 proof text are revised. **Every "no indirect
    branch" statement is withdrawn or qualified** (Appendix C, C-1 … C-11).
  * Fail-closed alternatives are stated but not assumed to work: FA-1,
    verified inlining; FA-2, a zero-`ret` image; FA-3, C-1A under the same
    rules (§5.14.5).
* **`R4-D2-2` (Important): the build-input closure.**
  * Every executable in R-1 … R-5 is traced and classified as B (can change
    image bytes), E (committed or digest-bound evidence) or P (provisioning
    and entry). The trace covers each tool's runtime inputs (§5.3.7, X-1 …
    X-16).
  * `/usr/bin/env` and `/bin/sh` are class B.
  * The whole build root is bound by a committed **`build-root.manifest`**,
    checked from inside the entered session (R-1). A later input-closure
    trace, **IC-1**, checks that nothing outside it is opened.
  * The inputs that no file can pin are **named, not denied**: kernel, CPU,
    entry mechanism, time and identity (HA-1 … HA-5, §5.3.8). The text says
    what R-5 does and does not show about them. "Complete closed toolchain"
    is **not** claimed.
  * R-2 is an exact vector. The compiler runs with `-S`, and the pinned `as`
    runs directly, so no temporary file or `PATH` lookup is needed.
  * The ineffective `TMPDIR` and caller-`umask` variations are removed from
    R-4, which now varies path, time and identity, each with a stated purpose.
  * The absolute `-ffile-prefix-map` is removed from the "fixed" flag vector.
* **`R4-D2-3` (Important): the hostile-environment contract.**
  * The versioned `execve` limits AE-1 … AE-5 are stated, including their
    dependence on `RLIMIT_STACK`.
  * HX-3 is split into HX-3a … HX-3d, with concrete sizes that keep every
    vector within HD-1 (75 % of the per-string limit) and HD-2 (25 % of the
    aggregate limit), asserted before each `execve`.
  * Entry is established by EN-1 … EN-3: an `O_CLOEXEC` pipe separates
    `DRIVER-EXEC-FAILED`; the trace must show `execve(⟨image⟩) = 0`; and the
    process's next calls must match the golden sequence.
  * **HX-5 now requires `W(launch-usage, 28)` and then `exit_group(111)`.**
    HX-4 and HX-7 are made exact, and HX-7 is split by descriptor. HX-8 and
    HX-9 cover statuses 114 … 117.
  * The closed, blocked and broken-pipe states of descriptor 2 are specified.
    Omitting the diagnostic when descriptor 2 is usable fails the case.
  * The experiment remains corroboration only.

## 2. Finding → amended section map

| Finding | Assignment requirement | Proposal sections |
|---|---|---|
| **`R4-D2-1`** | enumerate every permitted control-transfer class | §5.14.1 (CT-1 … CT-9, forbidden list, permitted instruction list) |
| | state whether `ret` is permitted; prove each target and saved-address integrity | §5.14.2 (RI-1 … RI-7); §5.1 (`rp11_main` `noreturn`, `_start` has no `ret`) |
| | `_start`'s call, non-inlined calls, epilogues, tail calls, thunks, fall-through between symbols and sections | §5.1; §5.14.1 (CT-3, CT-4); §5.14.2 RI-1 (compiler-created symbols and thunks), RI-2 (tiling, decoding), RI-3 (terminal instructions, `exit_group` + `ud2`); §5.3.3 (flags suppressing sibling calls, partitioning, cloning, thunks and padding) |
| | stack-frame and stack-write review for hostile `argv`/`envp`, the `INVOCATION_ID` copy and every local | §5.14.3 (SR-1 … SR-6, frame table, IN-1 … IN-4); §5.14.4 HR-1 … HR-3; §5.10 (stack bound, fault on exhaustion) |
| | strengthen BI-6, BI-7, T-L4 and related checks | §5.12.1 (T-L1, T-L4 narrowed, T-L7 extended, **T-L10 new**); §5.12.2 (BI-6 rewritten, BI-7 amended, **BI-10, BI-11 new**, closing text) |
| | revise P-3, P-4, §6.1 with exact mechanical and human evidence | §6.1 (P-3, P-4, P-5, "what makes the graph complete"); §6.2 (D9-1, D9-2); §6.3 (control-transfer verification row); §2.3 (AD-11, AD-12) |
| | remove or qualify "no indirect branch" | §0 (result text, FD-6); §4.3 C-1; §4.4 item 2; §5.3.3; §8; Appendix C (C-1 … C-11) |
| | fail-closed alternative | §5.14.5 (FA-1 … FA-3); §4.5 (new withdrawal conditions); §9 LD-7 |
| **`R4-D2-2`** | trace every executable in R-1 … R-5 | §5.3.7 (X-1 … X-16) |
| | shared libraries, program data, configuration, runtime inputs | §5.3.7 (runtime-input column); §5.3.2 (`build-root.manifest`); §2.3 (AB-1 … AB-4) |
| | include `/bin/sh`, `env` and runtime closure, or narrow the claim truthfully | both: X-5 and X-6 are class B and in the bound tree (§5.3.2, §5.3.7); the unpinnable inputs are HA-1 … HA-5 with R-5's limits (§5.3.8); §5.2 boundary rewritten |
| | distinguish byte-affecting from evidence tools; pin both where output is committed | §5.3.7 (classes B, E, P; "pinned or bound by" column); X-14 and X-16 cross-checks |
| | reconcile R-2, `build_env`, `TMPDIR`, `umask 022`; R-4 varies only inputs that reach the build | §5.3.2 (`build_argv`, `build_env`, `shell_added_env`); §5.3.3 (`-S`; `-ffile-prefix-map` removed); §5.3.4 (rows rewritten); §5.3.5 (R-2 exact, R-4 (a)–(c) with purposes, withdrawn variations) |
| | revise §5.2, §5.3.2, §5.3.4, §5.3.5, R-1 … R-5, manifest binding, evidence table together | §5.2; §5.3.1 … §5.3.8; §5.11 (binding row, manifest content, H-1 record); §5.12.1 (T-L3, T-L6); §5.12.3; §6.2 D9-3; §6.3 (build-environment row); §8; §9 LD-8 |
| | an unexplained difference is a stop, not a digest update | §5.3.5, closing paragraph (kept, and extended to correlation with HA-1 … HA-5) |
| **`R4-D2-3`** | versioned per-string and aggregate `execve` limits | §2.3 (AE-1 … AE-5); §5.12.4 (limits table, HD-1, HD-2) |
| | concrete HX-3 sizes and counts with headroom | §5.12.4 (HX-3a … HX-3d) |
| | distinguish the driver's initial `execve` failure from launcher refusal | §5.12.4 (harness; EN-1 … EN-3; `DRIVER-EXEC-FAILED`) |
| | split cases that cannot fit | HX-3a (long), HX-3b (many), HX-3c (malformed), HX-3d (near-name) |
| | HX-5 requires `launch-usage` write then `exit_group(111)` | §5.12.4 HX-5 → G-111; §5.9 normative-order bullet |
| | review HX-4, HX-7 and every other refusal | G-112, G-113(k), G-114, G-115a(s), G-115b, G-116, G-117(e); HX-4, HX-7a … HX-7f, HX-8a … HX-8d, HX-9a … HX-9c |
| | closed or blocked standard error | §5.9 ("when the line may be absent or short"); HX-7c, HX-7d, HX-7e, HX-7f |
| | stay corroborative | §5.12.4 "What it cannot show"; §6.3 hostile-testing row |

The remediation note §0-D2R1 has its own section map. Appendix C quotes all
26 withdrawn, narrowed or replaced claims verbatim, and a script asserted each
quotation against the reviewed D2 bytes.

## 3. Requirements implemented

**Documentation only.** The D2 proposal is amended in place, with its
provenance preserved: the original header, the reviewed-bytes digest, a
dated §0-D2R1 note, *(amended D2-R1)* markers on changed sections, and
Appendix C. This handback is new. Four concise pointer files are updated.

The C, assembly, flag, linker, trace and table text in the proposal is
specification inside a design document. **No source, build script,
toolchain file, test, binary, manifest, generated artifact, systemd or
polkit file, configuration, migration, dependency or executable content was
added or changed.**

## 4. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md` | amended in place, as §2 maps (`adc114bf…` → `a70f013f…`) |
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md` | **new**: this handback |
| `docs/review/Handover information` | title; *Active assignment* now names D2-R1 and the three findings, keeping the D2 assignment link; *Return state* rewritten for this return. Accepted decisions, restrictions and archive links are unchanged |
| `docs/project-management/status.md` | new current-status block. The previous block is relabelled *Superseded current status*, text unchanged |
| `docs/implementation-plan.md` §20 | new current action (Codex re-reviews). The previous current action is relabelled *Superseded current action*, text unchanged |
| `docs/operations/disposable-test-server.md` | a *Restriction at D2-R1 static-launcher remediation return* banner. Earlier banners are unchanged |

**Not changed:**

* the R2 proposal (still `f6405cd9…`);
* the D2 assignment (`4a3176df…`);
* the D2 handback (`2acd6b24…`);
* the decision record (`10daa599…`);
* the D2-R1 assignment (`57500b5b…`);
* every other assignment, handback, review, decision, snapshot and archive;
* D-1, D-2, the operational-evidence draft and the manifest; and
* every Python file, hook, test and `settings.json`.

**Snapshot note.** The Handover's displaced D2 *Active assignment* and
*Return state* text was not moved to a new dated snapshot. Two reasons:

* the assignment forbids editing archives, and indexing a new snapshot would
  have required editing `handover-archive/README.md`; and
* the displaced text is durably recorded in the D2 assignment and D2
  handback, which remain linked from the Handover.

If the maintainer wants a verbatim snapshot, that is a separate archive step.

## 5. Migrations

None.

## 6. Security implications

* **The PO-9 claim is narrower and better supported.**
  * Reachability no longer depends on a reviewer inferring completeness from
    missing mnemonics. It is computed mechanically from rules that also bind
    `ret` (T-L10).
  * The remaining human judgement is named precisely (HR-1 … HR-6).
  * The verifier is class-E tooling. A defect in it is a common-mode risk,
    mitigated by the reviewer's independent re-derivation and by review of the
    raw listing (proposal §8).
* **Two new kernel semantics are load-bearing**, AD-11 (forced synchronous
  signals) and AD-12 (system-call return and restart). They join AD-3, AD-4,
  AD-6 and AD-8 in the D9-1 citation. If D9-1 refutes either, LB-2S is
  withdrawn (§4.5).
* **The build's trusted base is now stated honestly.** The build root is
  bound. The kernel, CPU and entry mechanism of the build host remain inputs,
  and independent reproducibility only detects drift they cause on the
  variants tested. The entry mechanism is trusted for the interval between
  R-1 and R-2 (HA-3).
* **The hostile experiment can no longer mistake a kernel `E2BIG` or a harness
  failure for a launcher refusal.** It also cannot load a hostile preload into
  the tracer or supervisor, because the case's vector exists only as the
  arguments of the child's `execve`.
* **No environment content is recorded.** The test vectors are synthetic, and
  the harness processes start with literal environments.

## 7. Commands run and results

Tools used: Bash, Read, Edit, Write. Every command was a repository read, a
scratch-directory write or a documentation write.

| Command | Result |
|---|---|
| `cat`, `sed -n`, `grep`, `wc` of CLAUDE.md; AGENTS.md (complete); the plan's reading map, §0, §16 and §20; the Handover; the D2-R1 assignment; the D2 assignment, proposal (complete) and handback; the decision record; Codex's R2 review; and the R2 proposal (§0-R2, §4.3, §4.4.1 … §4.4.3.7, §7.9, §9 … §15) | read. No secret file was named or opened |
| `git status --short`, saved to the session scratch directory | 74 entries before this work |
| `sha256sum` of the assignment, both D2 files, the D2 assignment, the R2 proposal, the decision and the four pointer files | as cited. The proposal equalled the reviewed D2 bytes (`adc114bf…`) before amendment |
| a copy of the pre-amendment proposal into the scratch directory | used as the source of Appendix C's quotations |
| Python one-off scripts that replaced proposal and pointer text, each asserting that its anchor occurred exactly once | applied |
| a Python script that asserted each of Appendix C's 26 quotations is a substring of the reviewed D2 bytes | all 26 present. One quotation was corrected for line breaks before the append succeeded |
| `python3` byte-length computation of the seven diagnostic lines | 28, 36, 28, 34, 30, 28, 34 (proposal §5.9) |
| a Python table-shape check over the proposal (pipe count per row, ignoring code spans) | 0 mismatched rows |
| `sha256sum` and `wc -l` of the amended proposal | `a70f013f…fc295b81`, 1 774 lines |
| documentation checks | §8 |

**Not run, as the assignment prohibits:** any compiler, assembler, linker,
`objdump`, `readelf`, `strace`, package manager, download, test suite, hook,
loader or interpreter probe, `systemctl`, `systemd-run`, `loginctl`, `busctl`,
`sudo`, `ssh`, `rsync`, `uname` or other host inspection. No kernel or
toolchain source was fetched, so AD-11 … AD-13, AB-1 … AB-4 and AE-1 … AE-5
are uncited assumptions. No guard or tool refusal occurred.

## 8. Documentation checks

| Check | Result |
|---|---|
| `git diff --check` over the four tracked pointer files | exit 0; no whitespace error |
| `git diff --no-index --check /dev/null ⟨file⟩` for the amended proposal and this handback (both untracked) | no whitespace error printed. Exit 1 only signals the difference. Trailing-whitespace count 0 and tab count 0 in both |
| relative-link resolution (Python, `pathlib`) over the six touched files | 342 links. 3 resolve only once URL-decoded: the pre-existing `%20`-encoded links to `Handover information`. **0 broken** |
| `git status --short \| wc -l`, compared with the saved listing | 74 before, 75 after. The only new entry is this handback. The proposal and the four pointer files were already listed. Unrelated user changes were preserved |

## 9. Checks not run, and why

* **No test suite, formatter, linter or type checker.** No code changed, and
  the assignment permits only documentation, link and diff checks. No suite
  figure is cited.
* **No build, binary inspection, verifier run, IC-1 trace or reproducibility
  check.** All are prohibited. T-L10, BI-10, BI-11, IC-1 and R-1 … R-5 are
  specified, not performed. The expected frame layout and function shape are
  design expectations, not observations.
* **No hostile-environment experiment.** Prohibited, and separately authorized
  later if at all.
* **No citation of kernel, compiler, binutils or strace source.** Host
  inspection and downloads are prohibited. Every such statement is an
  assumption marked for citation.
* **Manifest not regenerated or incremented.** No covered source changed.
* **No commit or push.** Not authorized.

## 10. Configuration, deployment and rollback

* **Configuration and deployment:** none.
* **Rollback of this return:**
  * restore the proposal to the reviewed D2 bytes (`adc114bf…`). The file is
    untracked, so Git holds no earlier version. A copy was kept in the
    session scratch directory, which is not durable, and the bytes are
    identifiable by digest;
  * delete this handback;
  * revert the four pointer edits: the Handover title, *Active assignment* and
    *Return state*; the new `status.md` block and relabel; the new §20 action
    and relabel; and the new test-server banner.
* **Rollback of the later implementation:** proposal §5.13, unchanged.

## 11. Assumptions, proof obligations, decisions and questions for Codex

**Assumptions added:**

* **AD-11, AD-12:** load-bearing for PO-9 and cited in D9-1;
* **AD-13:** `argc` 0; not load-bearing;
* **AB-1 … AB-4:** build tools, checked by IC-1; wrong assumptions fail
  closed;
* **AE-1 … AE-5:** `execve` limits; proof inputs of the experiment, not of
  PO-9.

**Residual inputs named:** HA-1 … HA-5 (proposal §5.3.8).

**Proof obligations:** PO-9's components are extended:

* D9-1 adds AD-11 and AD-12;
* D9-2 adds BI-10, BI-11, T-L10 and HR-1 … HR-6; and
* D9-3 adds the tree manifest and IC-1.

PO-14, PO-16, PO-17 and PO-18 are unchanged. Everything remains open.

**Maintainer decisions:** LD-1 … LD-6 as before, plus two new ones:

* **LD-7:** `ret` under CT and RI, or zero-`ret` FA-2 from the start;
* **LD-8:** accept a bound build root with named residual inputs, or require
  more, such as a diverse toolchain.

The M-14 implementation authority, H-1, H-2 and the remaining R2 decisions are
still required.

**Focused re-review questions for Codex:**

1. **Completeness of CT.** Does CT-1 … CT-9 with the forbidden list cover
   every way x86-64 user-space control can leave fall-through? Consider in
   particular: TSX aborts, `syscall` restart, faults, `ud2`, and signal
   delivery with no handler. Is anything missing, such as a CPU erratum
   class, `#DB` from a stray trap flag, or a vsyscall-page access?
2. **Return integrity.** Does RI-4 … RI-6 suffice for RI-7? Is the store
   rule `0 ≤ disp` and `disp + width ≤ o(i)` correct and complete? Is it
   right to exclude the red zone with `-mno-red-zone` rather than allow
   negative displacements? Does RI-6 overlook any kernel write to user
   memory for the nine inventory calls as used?
3. **Tiling and decoding.** Is RI-2 enough to rule out an instruction stream
   that overlaps its own decoding? That means a direct target inside another
   instruction, given linear-sweep decoding and the listing-to-`.text` byte
   equality.
4. **Input independence.** Do SR-1 … SR-6 and IN-1 … IN-4 establish that
   hostile `argv` and `envp` cannot influence any store address, count or
   stack adjustment? Is the 32-assignment copy the right design, or should a
   bounded indexed store be allowed with a reviewed bound?
5. **Verifier trust.** Is T-L10, a class-E tool whose verdict the reviewer
   re-derives and whose tables HR-1 … HR-6 check against the raw listing,
   adequate? Or should LD-7 require a second, independent verifier?
6. **FA-2 honesty.** Is the stated narrowing of T-L8 under FA-2 accurate and
   sufficient?
7. **Closure completeness.** Does X-1 … X-16 trace every executable in
   R-1 … R-5? Are any runtime inputs missing, for example compiler plugins,
   `LD_BIND_NOW`-style loader defaults, `/etc/gcc` configuration or
   `binfmt_misc` on the build host itself?
8. **Manifest exclusions.** Is excluding package-manager state, cache and
   logs acceptable, given the rule that nothing IC-1 sees opened may be
   excluded?
9. **Honest narrowing.** Do HA-1 … HA-5 and §5.3.8's statement of what R-5
   does and does not show meet the assignment's requirement not to treat
   independent reproducibility as removing an input? Is HA-3's short trust
   interval acceptable?
10. **R-4.** Does each variation (a) … (c) reach the build as stated? Is
    anything that does reach the build left unvaried, without a stated
    reason?
11. **Limits.** Are AE-1 … AE-5 right for Linux 5.9 through the current
    series? Are HD-1 and HD-2 sufficient headroom? Does any HX-3 vector, as
    specified, breach them?
12. **Entry evidence.** Does EN-1 … EN-3 establish that `rp11-launch`, and not
    the harness or the kernel, produced each result? Is an empty `tmpfs`
    over `/usr/bin` in a private namespace an acceptable way to produce
    `ENOENT`, instead of strace fault injection?
13. **Descriptor 2.** Is §5.9's treatment of closed, read-only, broken-pipe
    and blocking descriptor 2 complete and consistent with HX-7c … HX-7f?
14. **Evidence separation.** Does any sentence now credit T-L10, IC-1,
    R-5 or the experiment with more than §6.3 allows?
15. **Retention versus withdrawal.** Is retaining D-S1 honest, given that
    every new element is specified but unobserved? Do §4.5's added conditions
    state when it must be withdrawn?

## 12. Return state

The §8 checks ran against the returned proposal bytes (`a70f013f…`). This
handback was edited only to record their results.

**Claude has stopped.**

* **Next:** Codex independently re-reviews:
  * the complete reachable control-flow proof, including returns and stack
    integrity;
  * the build-input and tool-runtime closure;
  * the feasibility and exact expected traces of the hostile vectors;
  * all dependent PO-9 premises, binary-inspection checks, reproducibility
    claims and evidence-class boundaries; and
  * the honesty of the retained recommendation.

  Peter Duscha then decides whether to accept the launcher design or request
  further remediation.
* **No implementation assignment exists.**

Throughout: PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
neither pass is executable or authorized; `plan.is_executable=False`; P5.0-R5
remains Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not
ready.
