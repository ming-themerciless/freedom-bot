# Decision proposal — C-11 guard-preserving capture and the pinned launcher environment

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D1`

Date: 2026-09-29

Author: Claude, design author

Independent reviewer: Codex

Decision owner: Peter Duscha

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-claude-prompt.md)
(SHA-256 `10ebc921…71962d6`)

Handback:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-c11-launcher-contract-handback.md)

Remediation: `C-P5.0-R5-RP11-I1-R3-R4-D1-R1`, 2026-09-29, Claude, amended in
place under
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-claude-prompt.md)
(SHA-256 `7ca4cf76…5c5ffc1b`) in response to Codex review
[`C-P5.0-R5-RP11-I1-R3-R4-D1-REV1`](project-review-2026-09-29-p5-r5-rp11-r4-d1-c11-launcher-contract.md)
(SHA-256 `e5e62cd6…0aef4dc`). The bytes Codex reviewed had SHA-256
`e026ecf51f2dacf15bcc1871b97f09b72cceadb42bc4d968139080c4e2ff0751`. See §0.

Remediation handback:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r1-c11-launcher-contract-remediation-handback.md)

Second remediation: `C-P5.0-R5-RP11-I1-R3-R4-D1-R2`, 2026-09-29, Claude, amended
in place under
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-claude-prompt.md)
(SHA-256 `77fbf40f…5cab8cdb6`) in response to Codex re-review
[`C-P5.0-R5-RP11-I1-R3-R4-D1-R1-REV1`](project-review-2026-09-29-p5-r5-rp11-r4-d1-r1-c11-launcher-contract.md)
(SHA-256 `04cef19f…3e243c67`). The bytes Codex re-reviewed had SHA-256
`a402f579e3e8276e092cd74b814ad25da2e37ac0b40ceccdc9f8937c62a49368`. See §0-R2.

R2 remediation handback:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d1-r2-system-manager-environment-remediation-handback.md)

State: **proposal only — amended twice, not re-reviewed since R2, undecided,
unimplemented. No recommendation is ready.** No Blocking finding is claimed
closed. This document
changes no source, hook, test, manifest, artifact, configuration or draft
text, and it creates no implementation or operational authority. **RP-11
remains unwired and unmet. Neither pass is executable or authorized.
`plan.is_executable=False`. P5.0-R5 remains Blocking. OD-62 G-A remains
conditional. Package 5.0 remains not ready.** Choosing an option here does not
satisfy RP-11 or make either pass executable. It only makes a later, bounded
implementation assignment possible.

---

## 0-R2. Remediation note — R4-D1-R2, 2026-09-29

Codex re-review `C-P5.0-R5-RP11-I1-R3-R4-D1-R1-REV1` found one remaining
Blocking defect in the bytes it reviewed (`a402f579…c62a49368`):

* **`R4-D1-R1-1`.** The recommended LB-2 unit added `PATH` and `LC_ALL` to the
  system manager's environment but did not establish a closed environment
  before the dynamic loader starts `/usr/bin/python3.12`. Manager-level loader
  state could therefore act before the entry's diagnostic check.

This amendment corrects the design text only. **It does not claim the finding
closed.** Only Codex's independent re-review and Peter Duscha's later decision
can do that.

**Outcome, in the assignment's terms (R2 prompt §4).**

1. **LB-2 as returned is rejected as prevention (outcome 3 for that form).**
   Under the systemd semantics relied upon (§4.4.3.1, S-1 … S-10), a system
   unit's environment consists of three parts:
   * the manager's global environment;
   * the variables the manager defines itself; and
   * the unit's own settings,

   less a finite, named `UnsetEnvironment=` list. **No unit directive builds an
   allow-list.** The global environment is fed by configuration, the kernel
   command line, generators and a run-time API. So no unit text can keep a
   manager-level loader input away from a dynamically linked `ExecStart=`
   image. Codex's finding is confirmed.
2. **The corrected mechanism, LB-2S, is specified (outcome-1 shape; §4.4.3.4).**
   The unit's `ExecStart=` names a root-installed, **statically linked first
   image**, `rp11-launch`. Its start-up reads no environment (PO-9). It
   discards the block it was given, except one grammar-checked
   `INVOCATION_ID`, and calls `execve` on the interpreter with a **literal**
   three-entry environment (`rp11-entry-env/1`, §7.9). The
   manager's environment reaches only that image, which never uses it. The
   entry's allow-list is therefore built by reviewed code **before** the
   entry's loader runs.
3. **One trust is narrowed explicitly (an outcome-2 component; R-10).** The
   manager's **execution settings** cannot be excluded by any unit text. They
   are `Default*=` values, top-level and unit drop-ins, run-time properties and
   unit-path resolution (S-5). The design trusts them as root-controlled input,
   reviewed and bound at installation (H-1) and before each pass (H-2). That is
   review, not prevention. Whether it is acceptable is decision M-10, as
   revised.
4. **LB-1 and LB-3 are reassessed under the same rule** (§4.4.2, §4.4.4).
   * **LB-1** meets the environment rule, because it is the same static image.
     It still inherits client process state.
   * **LB-3** does not build a closed environment. `sudo`'s PAM session can
     merge root-configured variables into the command's environment (AS-12).
     The `sudo` image itself is also loaded under glibc's secure-mode deny-list
     filter of the client's environment.
5. **No recommendation is ready.** LB-2S needs a compiled static image, which
   is a new build dependency, and a design pass for its runtime (**M-14**). It
   also needs M-10 as revised. §1 states a conditional direction with those
   prerequisites, labelled as such. It is not a recommendation.

**Threat scope (not redefined).** As §4.3 defines it, T-A is ambient
configuration "not aimed at this design". That includes ambient **manager**
state. Examples:

* `DefaultEnvironment=LD_PRELOAD=libeatmydata.so` on a build host;
* a top-level `service.d/` drop-in; and
* a system environment generator.

The R1 bytes called T-A in scope for every option, yet listed "the manager's
environment" among trusted root state (R-8). That inconsistency is withdrawn.
Under LB-2S the manager's environment is **not trusted and not needed**.

**R4-D1-2 is not reopened.** D-1's issue clause (§5.3) is the only
R4-D1-2-adjacent text touched. Its bracket changes from `[M-9 = LB-2]` to
`[M-9 = LB-2S]`, and its environment sentence changes, because the environment
source changed. The client-inspected invocation is unchanged. §5.4, §6.6.1,
§6.6.2, D-2 and M-11 are unchanged.

| Finding | Where it is corrected |
|---|---|
| **`R4-D1-R1-1`** (Blocking) | §0-R2; §1 (table, R2 result, conditional direction); §2.3 AS-6 (rewritten), AS-11 … AS-13 (new); §4.2 C-5, C-6; §4.3 (T-A, stages T4 and T5, reassessment table, earliest trusted component); §4.4.1 (added rows); §4.4.2 (R2 note); **§4.4.3 (rewritten: semantics, sources, allow-list question, LB-2/LB-2U/LB-2T/LB-2S, classification, installation and pre-pass checks)**; §4.4.4 (R2 reassessment); §4.4.5; §4.4.6; §4.4.7; §5.3 (issue clause and presupposed decisions); §6.1 (meaning of "an M-9 boundary"); §6.5; §7.7; §6.8; §6.9 R-8 (amended), R-10, R-11 (new); **§7.9 (rewritten)**; §8; §9; §10.3; §11; §12; §13 (M-9, M-10 revised; M-14 new); §14 (PO-8, PO-9, PO-10 revised; PO-14 … PO-16 new); §15; **Appendix B** |

Appendix B quotes every claim withdrawn or narrowed by this amendment verbatim.
Appendix A, the R1 change record, is unchanged.

---

## 0. Remediation note — R4-D1-R1, 2026-09-29

Codex review `C-P5.0-R5-RP11-I1-R3-R4-D1-REV1` found two Blocking defects in
the bytes it reviewed (`e026ecf5…2e2ff0751`). This amendment corrects both **as
design text only**. It does not claim either finding closed. Only Codex's
independent re-review and Peter Duscha's later decision can do that.

| Finding | Defect in the reviewed bytes | Where it is corrected |
|---|---|---|
| **R4-D1-1** (Blocking) | The entry was started by the operator's shell with its ambient environment. A post-start check for loader-variable names (old §6.9 R-4, §7.7) was presented as a refusal, but the dynamic loader acts before any Python code runs. The claims that the in-process gate "cannot be bypassed", that hook absence has "no effect on enforcement" and that non-Claude callers were "fully" protected were therefore untrue | §1; §2.2 OB-11 … OB-16; §2.3 AS-6 … AS-10; new **§4.3** (timed trust boundary) and **§4.4** (launch-boundary options and the impossibility result); §4.2; §5.2; §6.2; §6.3; §6.5; §6.9; §7.7; new §7.9; §8; §9; §10.3; §11; §12; §13; §14; §15 |
| **R4-D1-2** (Blocking) | O-2 and D-1 claimed that the client hook inspects every semantically complete command before any process starts. A1-12's final text exists only after A1-11 has run inside the session, so the hook could inspect only a template | §1; new **§5.4** (the four representations and which layer inspects each, and when); **§5.3** D-1 rewritten; §6.2; §6.3; new **§6.6.1** (knowability of every catalogue entry) and **§6.6.2** (A1-12 remedies); §6.8; §9; §10.4; §11; §12; §13 |

**Form of the result.** This is a **decision-ready impossibility result with
the minimum maintainer choices**. It is not a recommendation that meets the
constraints as they stand today.

* **R4-D1-1.** With a repository-only implementation, no host configuration
  and the entry created by the client's ordinary execution path, **no design
  prevents unreviewed loader state from reaching the entry.** Prevention is
  possible, but only across a boundary the repository cannot create alone
  (§4.4). The earliest client-side components, which are the client's shell and
  the client hooks, stay exposed to the client environment under every option.
  The direct path has the same exposure today.
* **R4-D1-2.** For **Pass A** the defect can be removed completely. With draft
  amendment D-2 (§6.6.2), every Pass A catalogue entry is a reviewed literal,
  so the pre-start criterion can hold for Pass A. For **Pass B** it cannot hold
  as drafted. B2's `--at` value is defined as the time at issue and cannot
  exist before the entry starts. Pass B is therefore out of this decision's
  scope (M-11).

A **conditional direction** is stated in §1: what this proposal would
recommend if Peter Duscha makes the named choices. It is labelled as
conditional and is not presented as satisfying the current constraints.

Appendix A records every withdrawn claim verbatim, so that the reviewed bytes'
content stays traceable after this in-place amendment.

---

## 1. Summary

*Amended R4-D1-R1. The reviewed summary's claims that the in-process gate
"cannot be bypassed" and that the client hooks inspect "the semantically
complete commands before any process starts" are withdrawn (Appendix A).*

*Amended R4-D1-R2. The R1 summary's LB-2 row, which credited the unit with
preventing loader state, and its conditional direction are withdrawn and
replaced (Appendix B). LB-2 is corrected to LB-2S, and no recommendation is
ready.*

**What survives review unchanged.** Codex's review called the proposal
*"careful about the closed catalogue, exact argv binding, environment key
classification, authentication uncertainty, manifest effects, test design and
retained gate state"*. This amendment keeps those. It also keeps the one
canonical guard policy, executed from the hooks' own digest-pinned bytes before
X-1 and again before every launch. That policy is now assessed only together
with a launch boundary.

**The closed child environment was already a correct loader boundary for the
children.** `rsync` and `ssh` are started by the entry with a map built only
from reviewed literals, so no ambient loader state can reach them. The defect
lay one level up: in the process that builds that map.

**R4-D1-1 — the result.** Every process the client's shell creates, and the
shell itself, is loaded with the client's environment *E_c* before any
repository byte runs (§4.3). A check inside the entry therefore runs after
`LD_PRELOAD`, `LD_AUDIT`, `GLIBC_TUNABLES`, `BASH_ENV` and the Python startup
inputs have already acted. A cleansing utility started by that shell
(`env -i`, `unset`, an assignment prefix) is loaded the same way. Examples of
ambient, non-malicious preloads that would silently defeat this entry's own
checks:

* `libeatmydata`, which turns `fsync` into a no-op and so defeats the §9.5.1
  durability barrier and the X-1 capability test;
* `libfaketime`, which alters the UTC times recorded; and
* `fakeroot`, which alters the `lstat` ownership that §6.7's executable check
  relies on.

**Prevention needs an exec boundary whose process state is not derived from
*E_c*.** Three exist, and none can be built from repository bytes alone
(§4.4). *(R2)* **A boundary that is not derived from *E_c* is still not
enough.** The environment the entry's loader sees must also be closed. Under
every option that closure comes from one place: a static image that reads no
environment performs the entry's `execve` with a literal (§4.4.7).

| Option | Client-inspected invocation (exact) | What it prevents | What it needs |
|---|---|---|---|
| **LB-2S**, service manager with a static first image *(R2; corrects the R1 LB-2 unit, which is withdrawn as prevention)* | `/usr/bin/systemctl --no-ask-password start --wait rp11-capture-pass-a.service` (unchanged) | **all client-derived process state**, because PID 1 creates the entry (S-8). **The manager's environment** reaches only the static image `rp11-launch`, whose start-up reads none (PO-9), and which starts the interpreter with a literal environment. Manager **execution settings** are not excluded: they are reviewed root input (R-10, M-10) | the unit, polkit rule, pass configuration, bootstrap **and a compiled static image** on the repository host. That is **host provisioning** (M-9, H-1, H-2) **and a new build dependency** (M-14) |
| **LB-3**, `sudo` command rule | `/usr/bin/sudo -n -u ⟨MI.operator_account⟩ -- /usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_entry.py run --pass A` | client loader state and descriptors for the entry (setuid `AT_SECURE`, `env_reset`, `closefrom`). *(R2)* **Not a closed environment**: `sudo`'s PAM session can merge root-configured variables (AS-12), and the `sudo` image is loaded under a deny-list filter of the client's environment (§4.4.4) | a root-owned sudoers rule: host provisioning. The entry still inherits seccomp, Landlock, namespaces and ancestry |
| **LB-1**, static first-exec launcher | `/usr/local/libexec/freedom-blades-rp11/rp11-launch --pass A` | environment, loader and descriptors for the entry. *(R2)* It is the same static image LB-2S uses, started by the client | a compiled artifact: a new toolchain dependency, a reproducible build and an installed binary (M-14). The same inheritance as LB-3 |

Under every option the client shell and the client hooks keep running under
*E_c*. The client-hook layer is therefore **defense in depth whose own
integrity rests on the client environment**, for the captured path and for the
direct path alike (OB-11). It is never the enforcement, and no record claims
that it ran (§6.8).

**R4-D1-2 — the result.** A catalogue entry's final text is knowable at one of
four times (§6.6.1):

* reviewed literal (**K-L**);
* pre-bound reviewed value (**K-R**);
* runtime observation (**K-O**); or
* unresolved placeholder (**K-U**).

**Pass A** has exactly one K-O entry, A1-12. The draft already stops the pass
whenever A1-11 differs from the pinned statement (§4.6, §4.7(4)), so
**whenever A1-12 runs, its value is already known before the pass**.

Two remedies make it knowable before the entry starts:

* **D-2a:** hash through the venv entry, as a reviewed literal; or
* **D-2b:** instantiate from the pinned statement.

With either, the client hook, the in-process admission and the pre-launch
evaluation all inspect the same complete text for every Pass A act.
**Pass B** contains K-O slots that cannot exist before the entry starts (B2's
`--at`, `--requested-at` and the B1-Q-conditional flags), a mid-session human
gate (B6.3) and K-U placeholders. For those, the pre-start criterion is
unsatisfiable as drafted (M-11).

**D-1 is rewritten** (§5.3, §5.4). It distinguishes four representations:

* fixed literal text;
* reviewed template;
* typed runtime instantiation; and
* executed argv.

It states truthfully which layer inspects each one, and when.

**R4-D1-R1-1 — the result (*R2*).** The R1 LB-2 unit is withdrawn as
prevention, for three reasons:

* **The environment was never closed.** A systemd unit's environment is
  assembled from open sources: the manager's global environment, the
  variables the manager defines itself, and the unit's own settings
  (§4.4.3.1, S-1).
* **The unit cannot filter it closed.** The only filter is a finite
  `UnsetEnvironment=` list of names (S-4).
* **The global environment is not fixed.** It is fed by `DefaultEnvironment=`,
  `systemd.setenv=`, generators and `set-environment`, and it can change at run
  time (S-7).

`/usr/bin/python3.12`'s loader would consume whatever that block holds before
§7.9's check could run.

**The correction is LB-2S** (§4.4.3.4). `ExecStart=` names a static image,
`rp11-launch`. It reads nothing from the block except one grammar-checked
`INVOCATION_ID`, and it starts the interpreter with exactly
`{INVOCATION_ID, LC_ALL=C, PATH=/usr/bin}`.

LB-2S leaves one explicit trust. The manager's execution settings (limits,
confinement, drop-ins and the loaded `ExecStart=`) are root input. They are
reviewed and bound at H-1 and H-2, not prevented (R-10).

The LB-2S design depends on two load-bearing proof obligations:

* **PO-9**, that the static image's start-up reads no environment; and
* **PO-14**, that the installed systemd does not start its executor under the
  unit's block.

**No recommendation is ready.** The minimum decisions are:

* **M-14**, whether to accept a compiled static image, which is a new build
  dependency, and to commission its runtime design;
* **M-10**, as revised: whether manager execution settings may be trusted as
  reviewed root input; and
* **M-9**, the boundary itself.

**Conditional direction — not a recommendation.** It applies only if Peter
Duscha decides all of the following:

* M-9 = LB-2S;
* M-14 = accept, and the runtime design pass then meets PO-9;
* M-10 = T-A in scope, with manager execution settings trusted as reviewed
  root input (R-10);
* D-2 = D-2a;
* M-11 = Pass A only; and
* D-1 as rewritten.

Under those choices:

* **Option.** O-2 (corrected), carried by LB-2S, with a root-installed
  bootstrap (M-12).
* **R4-D1-1 and R4-D1-R1-1.** No client-derived process state reaches the
  entry. **No environment variable reaches the entry's loader except the three
  literal-grammar entries `rp11-launch` writes.** The canonical policy
  therefore runs in a process that neither *E_c*'s nor the manager's loader
  state touched. This holds subject to PO-9 and PO-14, which a later,
  separately authorized host step must discharge.
* **R4-D1-2.** Every Pass A text is a K-L literal. For a Claude operator the
  client hooks inspect each of them before the invocation starts (defense in
  depth), and the entry inspects each before X-1 and again before its launch
  (enforcement).

Without M-9, or with M-9 but without M-14, **no option satisfies R4-D1-1's
requirement as sharpened by R4-D1-R1-1, and C-11 stays open.** That outcome is
correct if the maintainer declines, and this proposal does not conceal it as a
residual risk.

**The environment contract for the children is unchanged** (§7): `PATH=/usr/bin`,
`LC_ALL=C` and, only under agent authentication, a maintainer-fixed
`SSH_AUTH_SOCK`. It is now accompanied by a separate contract for the entry's
**own** environment, `rp11-entry-env/1` (§7.9). *(R2)* That contract is a
literal written by `rp11-launch`, not an environment assembled by the manager.

**Honest limit, and the minimum baseline amendment** (unchanged from the
reviewed bytes). No option satisfies all three of the following at once:

* the draft's literal wording that the §5 `rsync` is issued *"as one plain call
  through the client's ordinary execution path"* (§5), and that every A1 host
  command is *"one plain `ssh oracle-test "…"` call, as written"* (§6.2);
* C-2's separate, complete, byte-exact streams; and
* the launcher's no-shell exact-argv contract.

**Every viable option therefore needs amendment D-1**, now rewritten in §5.3.

Findings that bear on the later implementation:

* **F-1.** The exact §5 text is **not** a committed guard test case.
  `test_guards.py` allows two shorter rsync forms that lack the
  `__pycache__/`, `*.py[cod]` and `.pytest_cache/` exclusions. By reading the
  hook source, the §5 text would be allowed. This was not executed, as the
  assignment requires (§2.2).
* **F-2.** The capture mechanism has no way to reopen a root. A capture
  session therefore lives in **one process per pass**, and the entry has to be
  a per-pass invocation (decision M-6).
* **F-3.** `guard-git.py`'s publishing rule depends on the current branch,
  which it reads by running `git rev-parse` in the caller's working directory.
  The canonical evaluation must therefore be branch-independent by
  construction (§6.4).
* **F-4 (new).** Pass B needs Peter Duscha's live reboot confirmation
  (B6.3, `MI.reboot_go`) *after* B6.1 has been reported, in the middle of the
  session. A per-pass entry with no control channel cannot receive it. Pass B
  also has runtime slots (§6.6.1). The reviewed bytes' hook grammar
  `--pass (A|B)` and their unqualified per-pass M-6 were wrong for Pass B
  (M-11).
* **F-5 (new).** The client hooks themselves start as `#!/usr/bin/env python3`.
  `/usr/bin/env` and a `PATH`-resolved `python3` are loaded, and Python
  starts, with the client's environment and without `-E` or `-I` (OB-11). The
  client-hook layer is therefore exposed to ambient loader and Python startup
  state on the direct path today.
* **F-6 (new).** The evidence package imports `application.idempotency` from
  `manifest.py`, `records.py` and `review_manifest.py`. Neither
  `application/__init__.py` nor `application/idempotency.py` is a covered
  source (OB-13). So an entry that verifies `COVERED_SOURCES` before executing
  them would still execute unverified repository bytes. The entry's import
  closure must be covered or removed (§11).

---

## 2. Sources, observations and assumptions

### 2.1 Read for this proposal

* `.agents/AGENTS.md` (complete)
* `CLAUDE.md`
* `docs/implementation-plan.md`: reading map, §0, §16, §20
* `docs/review/Handover information`
* the assignment
* The operational draft
  `phase-5-0-p5-r5-operational-evidence-authorization-prompt.md` (SHA-256
  `5c6046fc…dcca7de6`, unaccepted): §0–§6, §9.5 C-1…C-15, §11 and §12.
* `docs/operations/disposable-test-server.md`: banner, §1–§3
* The hook sources and their tests:
  * `.claude/hooks/guard-secrets.py` (`789223f5…baafd7ea65`)
  * `guard-git.py` (`cd9cfe49…aebcd9`)
  * `test_guards.py` (`ad8eee8f…26697`)
  * `.claude/settings.json` (`84bef3c1…c68de`)
* The capture source:
  * `tools/phase_5_0_evidence/execution/boundary.py`, `StreamCaptureLauncher`
    (`329d0001…f2397b25`)
  * `execution/capture_mechanism.py` (`b64d92cb…c14a`)
  * `capture_contract.py` (`437d663e…dd7`): `validate_argv`, `CaptureRecord`
  * `review_manifest.py`: `MANIFEST_VERSION = 26`, `COVERED_SOURCES`

**Added for R4-D1-R1:**

* the remediation assignment (`7ca4cf76…5c5ffc1b`);
* Codex's review (`e5e62cd6…0aef4dc`);
* the draft's §4.5 … §4.7, §6.1 and §7 in full, which is Pass B's command
  inventory (`5c6046fc…dcca7de6`, unchanged);
* the `import` statements of `tools/phase_5_0_evidence/**`, and
  `application/__init__.py` and `application/idempotency.py`; and
* `infra/systemd/`, listed by name only.

### 2.2 Observations (from repository bytes only)

| # | Observation | Source |
|---|---|---|
| OB-1 | The §5 command block and the disposable-test-server §3.2 block are byte-identical. As 12 lines without a trailing newline, the block is 381 bytes, SHA-256 `4b4096d727e24e5cb9b3e86255420e8644b23fd8cf7cc568442bd13fa9fb69cc` | computed locally from both files |
| OB-2 | `guard-secrets.py` applies the rsync-exclusion exemption only when, after backslash-newline removal, the text contains none of `` $ ` ; & \| < > ( ) # \ `` or a newline or carriage return, and its first word is `rsync`. A wrapper is therefore never exempt | `_without_rsync_exclusions`, `RSYNC_UNSAFE` |
| OB-3 | `guard-secrets.py` ignores `tool_name`. It inspects `file_path`/`path`/`notebook_path` and `command`. A payload that cannot be parsed is refused (exit 2) | `main()` |
| OB-4 | `guard-git.py` refuses history rewrites on any branch. It refuses commits and pushes only when `git rev-parse --abbrev-ref HEAD`, run in the hook's working directory, returns `main` or `master`. If that call fails, the branch is `""` and the publishing rules are silently skipped | `current_branch()`, `main()` |
| OB-5 | `test_guards.py` has 41 cases: 27 refuse and 14 allow. Its two rsync ALLOW cases are **not** the §5 text. Both lack the `__pycache__/`, `*.py[cod]` and `.pytest_cache/` exclusions (**F-1**) | `CASES` |
| OB-6 | `StreamCaptureLauncher.launch` refuses unless armed. It requires `argv[0]` to be absolute, with no NUL in any element. It refuses an environment key that is empty or contains `=` or NUL, and a value that contains NUL. It then runs `Popen(shell=False, stdin=DEVNULL, cwd="/", close_fds=True, env=dict(environment))`. It does **not** refuse an empty value, an unexpected key or a `=` in a value | `boundary.py` 1190–1234 |
| OB-7 | `validate_argv` states: *"There is no shell anywhere in RP-11, so the command text as issued and the vector the client process received are the same object."* `CaptureRecord` has no command-text field and no environment binding. This clashes with C-1, which requires both forms when the reviewed text is shell syntax, as §5's single quotes are | `capture_contract.py` 586–606, 658–670 |
| OB-8 | `ActRequest` carries a caller-supplied `argv` and `environment`. `create_capture_session` creates the root exclusively, and no function opens an existing root, so one session equals one process (**F-2**) | `capture_mechanism.py` docstring, 224–238, 775–800 |
| OB-9 | The documented SSH access is key-based, `IdentityFile ~/.ssh/id_ed25519`, through a `~/.ssh/config` host alias `oracle-test` with `User ubuntu` and **`StrictHostKeyChecking accept-new`**. The repository does not say whether the key is passphrase-protected or served by an agent | disposable-test-server §1–§2 (documentation, not read from the host) |
| OB-10 | `COVERED_SOURCES` covers `tools/phase_5_0_evidence/**` files only. The hook files and `.claude/settings.json` are not covered, so today a hook edit does not change the review digest | `review_manifest.py` 508–560 |
| OB-11 | *(R1)* `.claude/settings.json` registers each hook as `$CLAUDE_PROJECT_DIR/.claude/hooks/<name>.py`. Both files begin `#!/usr/bin/env python3`. The client therefore starts `/usr/bin/env` (dynamically linked), which resolves `python3` through the client's `PATH` and starts it without `-E`, `-I` or `-S`. Loader variables, `PYTHON*` variables and user-site `.pth` files in the client's environment reach both hooks before their first line runs (**F-5**) | `settings.json`; the first line of each hook |
| OB-12 | *(R1)* `guard-secrets.py` removes quoted spans before its verb search (`QUOTED`). For every `ssh oracle-test "…"` text, the verb search sees only `ssh oracle-test`, so its decision cannot depend on anything inside the double quotes. `guard-git.py` searches the whole text, quoted parts included, so its decision **can** depend on a substituted value. For example, a path containing `git` followed by `rebase` would match | `QUOTED`, `HISTORY_REWRITE` |
| OB-13 | *(R1)* `tools/phase_5_0_evidence/manifest.py`, `records.py` and `review_manifest.py` import `application.idempotency.canonical_request_hash`. `application/__init__.py` and `application/idempotency.py` are **not** in `COVERED_SOURCES` (**F-6**). `idempotency.py` imports only the standard library. `execution/case_program.py` imports `ctypes` and calls `ctypes.CDLL(None)` | `grep` of `import` lines; `review_manifest.py` 508–560 |
| OB-14 | *(R1)* In Pass A, the only command text that contains a value produced during the pass is A1-12 (*"with the literal A1-11 output substituted by the operator"*). The draft makes A1-11 and A1-12 A1-C steps. §4.6 says `OP.interpreter_real_path` must **stop** the pass *"if it differs from the statement"*, and §4.7(4) says *"A mismatch stops the band"*. So A1-12 runs only when A1-11's value equals the pinned statement's value | draft §6.2, §4.6, §4.7 |
| OB-15 | *(R1)* Pass B's command texts contain the following slots: `⟨PIN.*⟩` and `⟨MI.*⟩`, fixed before the pass; `⟨OP.at⟩`, *"the client UTC time at issue"*; `⟨OP.requested_at⟩`; three flags passed *"only if B1-Q observed each condition"*; `⟨RP-3.*⟩`, `⟨RP-5.*⟩` and `⟨RP-12.*⟩` paths; and `⟨MI.producer_argv.*⟩`, which is unresolved. B6.3 requires Peter Duscha's live confirmation after B6.1 has been reported. B6.5 repeats a literal text up to 12 times, depending on the connection outcome | draft §7.2 … §7.6 |
| OB-16 | *(R1)* The reviewed bytes' entry invocation (old §9) passed `--reviewed-digest`, `--authorization` and `--authorization-sha256` on the client command line. It named the entry by module (`-m`), which puts the working directory on `sys.path` when `-I` is absent, and it ran the venv interpreter `/opt/freedom-blades/runtime/venv-web/bin/python` | old §9 |

### 2.3 Assumptions (stated as assumptions and not verified here)

| # | Assumption | Why it is not verified |
|---|---|---|
| AS-1 | `rsync` and `ssh` on the repository host are `/usr/bin/rsync` and `/usr/bin/ssh` | host inspection is prohibited. Decision M-5 pins them, and an admission check verifies them |
| AS-2 | OpenSSH resolves `~` in `~/.ssh/config`, `IdentityFile` and `UserKnownHostsFile` from the password database (`getpwuid`), not from `$HOME` | behaviour of the installed version. Proof obligation PO-1 |
| AS-3 | With `RSYNC_RSH` unset and no `-e`, `rsync` starts its remote shell as `ssh`, found through its own `PATH`, and passes its environment to that child unchanged | behaviour of the installed version. Proof obligation PO-2 |
| AS-4 | `rsync`'s option parser may consult a user-level `popt` alias file. Whether it locates that file through `$HOME` or the password database is not established | PO-3 |
| AS-5 | If the client's system `ssh_config` has `SendEnv LANG LC_*`, as distribution defaults commonly do, `LC_ALL` is offered to the remote host. Whether the remote accepts it depends on the remote `sshd` | client and remote configuration are not inspected. §7.6 |
| AS-6 | *(R1; rewritten R2)* The repository host runs systemd as PID 1, with polkit and a system D-Bus. `systemctl start` sends the unit name and job mode, and **no** caller environment, descriptor, working directory, limit or confinement (S-8). The installed version's environment and configuration semantics are those stated in §4.4.3.1 (S-1 … S-10). *The R1 wording, which listed a started unit's environment as if it were a short closed set, is withdrawn (Appendix B). Its first item, "the manager's environment", is an open, mutable set (S-1, S-7)* | host inspection is prohibited. PO-8 (revised), PO-14, PO-15 |
| AS-7 | *(R1)* glibc's dynamic loader, when the kernel sets `AT_SECURE` (for a setuid image), ignores or filters `LD_PRELOAD` paths, `LD_LIBRARY_PATH`, `LD_AUDIT` and its other unsecure variables, and `sudo` then builds the command's environment afresh under `env_reset` | version behaviour. PO-10 (LB-3 only) |
| AS-8 | *(R1)* CPython 3.12 started as `/usr/bin/python3.12 -I -S <script>` reads no `PYTHON*` variable, adds neither the script directory nor the working directory to `sys.path`, imports no `site` (so no `.pth`, `sitecustomize` or `usercustomize`), and otherwise locates only files under its root-owned installation prefix | version behaviour. PO-12 |
| AS-9 | *(R1)* GNU coreutils `sha256sum` opens its operands without `O_NOFOLLOW`, so hashing a symbolic link hashes the file it resolves to at that moment | version behaviour. PO-7 (D-2a only) |
| AS-10 | *(R1)* Whether the operator's client applies a sandbox (seccomp, Landlock, namespaces or `no_new_privs`) to the commands it runs is client-defined and is not established here. Such confinement is inherited across `execve` | not inspected. §4.3 |
| AS-11 | *(R2)* In a statically linked glibc program, start-up code that runs before `main` still initialises tunables from `GLIBC_TUNABLES`. Later library calls may `dlopen` NSS or iconv modules. A static image built against glibc therefore does **not** by itself satisfy PO-9 | C-library version behaviour. PO-9. Choosing a runtime is M-14 |
| AS-12 | *(R2)* On Debian-family systems, `sudo`'s PAM stack includes `pam_env`, which reads `/etc/environment` and may read `/etc/default/locale` and `/etc/security/pam_env.conf`. `sudo` merges the resulting PAM environment into the command's environment, even under `env_reset` | `sudo` and PAM version and configuration. PO-10 (extended) |
| AS-13 | *(R2)* systemd 255 and later start each command through a separate `systemd-executor` image. PID 1 starts that image with **PID 1's own process environment**, not with the unit's assembled block, and the executor assembles the block and calls `execve` on the command. Earlier versions do the same work in a forked copy of PID 1, with no new `execve` before the command's | systemd version behaviour, stated from the author's understanding and not verified. PO-14. **Load-bearing for LB-2S** (§4.4.3.4) |

---

## 3. Governing constraints this design must preserve

| # | Constraint | Source |
|---|---|---|
| G-1 | §5's argv is fixed. It is never changed, re-quoted, reordered, extended or wrapped merely to obtain guard approval | draft §5 |
| G-2 | The secrets hook's exemption holds only for exactly one plain `rsync`. A wrapper is intentionally not exempt | `guard-secrets.py`; test-server §3.2 |
| G-3 | The launcher runs one exact argv with `shell=False`, separate streams, `stdin=/dev/null`, `cwd=/` and `close_fds=True`, with an explicit environment. It is unarmed by default | `boundary.py` |
| G-4 | A guard consulted only as advice, a hand-copied rule set, or a capture path that may choose whether to consult is not a solution | assignment §2 |
| G-5 | A refusal is a stop. The operator never re-quotes, hides operands, changes tool shape or retries by another path | draft §11.1; `CLAUDE.md` |
| G-6 | No secret, key, agent socket, credential or host authentication state is read to prepare this proposal | assignment §2, §6 |
| G-7 | RP-11 remains unwired and unmet. No design decision satisfies it | assignment §2 |
| G-8 | C-1 records both the command text and the executed argv. C-9 puts no environment in the handback | draft §9.5 |
| G-9 | Non-Claude agents are bound by `.agents/AGENTS.md` without hooks. The tooling creates no second standard | AGENTS.md "Skills and enforced guards" rule 3 |

---

## 4. The trust boundary, request to argv

### 4.1 The direct guarded path (today, Claude client)

| Step | Actor | What decides | What can go wrong |
|---|---|---|---|
| D-1 | the operator | writes a Bash tool call whose `command` is the §5 text | — |
| D-2 | the client permission layer, classifier or sandbox | may deny. A denial is a §11.1 stop | — |
| D-3 | the `PreToolUse` hooks | `guard-secrets.py` and `guard-git.py` each read `{"tool_name":"Bash","tool_input":{"command":<text>}}` and exit 0 or 2 | the hooks see the text only, not the argv |
| D-4 | the client shell (`bash`) | tokenises the text, removes quotes, joins continuations and looks up `rsync` in the **operator's `PATH`** | the operator's ambient environment is inherited in full |
| D-5 | `rsync` | starts `ssh`, found through the inherited `PATH` or `RSYNC_RSH`, with the inherited environment | ambient `SSH_AUTH_SOCK`, `RSYNC_RSH`, locale and so on all reach the child |
| D-6 | the client tool | returns merged, possibly truncated output | **not evidence**: no separate streams and no digests |

### 4.2 The captured path (O-2 corrected, carried by LB-2S under the conditional direction)

*Amended R4-D1-R1.* The reviewed rows C-3 to C-6 described an entry started by
the client shell as `python -E -s -m …`, with digests supplied on the command
line. §4.3 shows why that entry was reached by ambient loader state before its
own checks could run. The rows below follow the conditional direction (LB-2S since R2,
§4.4.3.4). LB-1 and LB-3 replace rows C-4 and C-5 as §4.4 states. Rows C-7 to
C-12 are unchanged.

*Amended R4-D1-R2.* Row C-5 now follows LB-2S. The R1 row said PID 1 creates
the entry with "the unit's closed environment". That was untrue: the unit's
block is open (S-1, S-4), and the phrase is withdrawn (Appendix B). Row C-6
marks the environment check as diagnostic.

| Step | Actor | What decides | Mutation before this step |
|---|---|---|---|
| C-1 | the operator | writes one Bash tool call: the **exact reviewed invocation** for Pass A, `/usr/bin/systemctl --no-ask-password start --wait rp11-capture-pass-a.service` (§4.4.3). It takes no operand, digest or path | none |
| C-2 | the client permission layer | as D-2 | none |
| C-3 | the `PreToolUse` hooks (Claude only) | *unchanged rules* on the literal invocation text; **plus** resolution of the unit name to Pass A's catalogue, whose file digest must equal the value pinned in the root-owned pass configuration; **plus** the unchanged rules on every Pass A text, all of which are reviewed literals under D-2a (§6.6.1). Any refusal, unknown unit, digest mismatch or load failure refuses. **These processes run under the client environment *E_c* (OB-11): defense in depth, not enforcement** | none |
| C-4 | the client shell, then `/usr/bin/systemctl` | the shell runs the literal by absolute path. `systemctl` (under *E_c*) sends one D-Bus request. **polkit** allows only `start` or `stop` of this one unit for the operator's account (§4.4.3) | none |
| C-5 | PID 1 (systemd), then `rp11-launch` *(amended R2)* | PID 1 creates the process from the **loaded** unit configuration: the unit file, any drop-ins and the manager's `Default*=` settings (S-5). Under systemd 255 or later it does so through `systemd-executor` (AS-13). It assembles the unit's environment block from **open** sources (S-1) and calls `execve` on the fixed `ExecStart=` image, the root-installed static `rp11-launch` (§4.4.3.4). That image's start-up reads nothing from the block (PO-9). It checks its argv and selects `INVOCATION_ID` by exact name and grammar. It closes descriptors ≥ 3, resets signal state, sets the umask and calls `chdir("/")`. It then calls `execve("/usr/bin/python3.12", […, "-I", "-S", ⟨bootstrap⟩, "run", "--pass", "A"], ⟨rp11-entry-env/1 literal⟩)`. **That `execve` is the first point at which the entry's environment exists, and only literals and one grammar-checked value make it up.** The entry is not a descendant of the client. `rp11-launch` is the earliest component the design trusts **for the entry's environment**. PID 1 and the loaded unit configuration are trusted root state **for the rest of its process state** (§4.3, R-10) | the entry process exists; nothing else |
| C-6 | the bootstrap | chdirs to `/` and sets `umask 077`. It reads the root-owned pass configuration and every covered source **once**, recomputes the review-manifest digest, and compares it with the pinned digest in the pass configuration. It then installs an import finder that serves **only** those verified in-memory bytes for repository packages. It checks its own environment against `rp11-entry-env/1` (§7.9; **diagnostic**, R2) and records `INVOCATION_ID`. Every failure refuses before X-1 | none |
| C-7 | the policy loader | reads each hook file **once**, compares its SHA-256 with the pinned value, compiles **from those bytes** into a private namespace and obtains `evaluate` | none |
| C-8 | the environment builder | builds the closed map from reviewed literals and the authorization-bound typed input. It validates the map and runs the socket checks only in agent mode | none |
| C-9 | the admission gate | evaluates **every** catalogue entry of the pass with both policies under every branch context. Everything must be allowed | none |
| C-10 | X-1 | creates the capture root exclusively and publishes the genesis state | **first mutation** |
| C-11 | each act | resolves the text, re-evaluates it with the same loaded policy, parses it with the reviewed grammar, compares the tokens with the pinned vector, maps `argv[0]`, launches with the closed map and records the bindings of §6.8 | the act's stream files |
| C-12 | `/usr/bin/rsync` or `/usr/bin/ssh` | runs with exactly the closed map. `rsync`'s child `ssh` inherits the same map | host effect |


### 4.3 The timed trust boundary, from the running client to the entry (*new, R4-D1-R1*)

**Terms.**

* ***E_c*** is the environment and process state of the operator's client
  when it runs a tool call. It covers environment variables, the working
  directory, descriptors, signal dispositions and mask, rlimits, umask, and any
  seccomp, Landlock, namespace or `no_new_privs` confinement (AS-10).
* **T-A, ambient state.** State present through configuration, tooling or
  habit, not aimed at this design. Examples are a profiling or test preload
  (`libeatmydata`, `libfaketime`, `fakeroot`), an `LD_LIBRARY_PATH` left by a
  toolchain, `PYTHONPATH`, `BASH_ENV`, or a client sandbox. **R4-D1-1 is about
  T-A, and T-A is in scope for every option.**
  *(R2)* By this definition, **T-A includes ambient manager state** when
  configuration or tooling puts it there and it is not aimed at this design.
  That covers the following (§4.4.3.2):
  * a `DefaultEnvironment=` or `systemd.setenv=` entry;
  * a run-time `systemctl set-environment`;
  * a system environment generator;
  * a top-level `service.d/` drop-in; and
  * manager `Default*=` settings.

  The R1 bytes nevertheless listed "the manager's environment" as trusted root
  state (R-8). That is withdrawn (Appendix B). T-A is **not** redefined here.
  Any narrowing of it is decision M-10.
* **T-B, a targeted adversary controlling the operator's account.** Such an
  adversary can forge any artifact that account can write, capture roots
  included. It can trace the account's descendant processes and run the direct
  path itself. No option below defends record integrity against T-B. Whether
  T-B must be in scope is decision **M-10**.

**Timing rule.** A process can refuse an input only if its own reviewed code
runs before that input is consumed. Anything the dynamic loader, the C-library
start-up, the shell's start-up or the interpreter's start-up consumes happens
**before** that process's first reviewed instruction. A check inside the
process can therefore only *detect* such an input, never *prevent* it. A
process started by one that has already consumed the input is protected only
if the image that performs the start does not consume it itself, or runs
outside the reach of the contaminated state (a static image, a kernel
secure-mode transition, or a process created by another parent), and does not
pass the input on (§4.4).

**Stages.** These hold for every option. *Controlled* means that some
repository-reviewed or root-owned byte decides the stage.

| Stage | Process image, and how it is selected | Consumed before that image's own code can act | Controlled? |
|---|---|---|---|
| **T0** client, already running | the client binary, started earlier by the operator | all of *E_c*, fixed when the client started | **no.** This precedes every design |
| **T1** client hooks (Claude only) | the registered command runs a hook file whose shebang is `#!/usr/bin/env python3`. `/usr/bin/env` is dynamically linked, resolves `python3` through *E_c*'s `PATH`, and starts it without `-E`, `-I` or `-S` (OB-11) | the loader inputs of *E_c* (`LD_*`, `GLIBC_TUNABLES`), `/etc/ld.so.preload`, `PATH`, `PYTHON*`, user-site `.pth` files, and any client sandbox | **no.** Registration and start-up are client-defined. The same is true of the **direct path today** (F-5) |
| **T2** client shell | the client's shell for the Bash tool, dynamically linked | the loader inputs of *E_c*; shell start-up inputs (for `bash`, `BASH_ENV`, `SHELLOPTS`, `BASHOPTS` and exported functions; any client-defined profile or snapshot); the working directory, descriptors, signal state, rlimits, umask and sandbox | **no.** Every option inherits this, as does the direct path |
| **T3** the first image the invocation names | selected by the T2 shell. An absolute path avoids a `PATH` lookup under T-A. A T2 shell subverted under T-B can run anything | that image's own loader processes *E_c*, unless the image is static or the kernel starts it in secure mode | **per option** |
| **T4** the boundary transition | LB-1: `execve` by a static image with a literal environment. LB-2S *(amended R2)*: PID 1, or `systemd-executor` (AS-13), `execve`s the static `rp11-launch` with the unit's **open** assembled block (S-1). `rp11-launch` ignores the block and `execve`s the interpreter with a literal. LB-3: a setuid `execve` of `sudo`, which builds a new environment that is **not closed** (AS-12) | per option (the table below). Under LB-2S the static image consumes nothing before `main` (PO-9) | **per option** |
| **T5** the entry's interpreter | `/usr/bin/python3.12 -I -S <bootstrap>`, root-owned (M-5) | its own environment, which T4 produced; `/etc/ld.so.preload` and `ld.so.cache` (root-owned); interpreter-location files under `/usr` (AS-8) | **yes** for LB-1 and LB-2S, where T4 is `rp11-launch`'s literal. *(amended R2)* For the R1 LB-2 unit and for LB-3, T4 produced an **open** environment (S-1, AS-12), so T5 is **not** controlled |
| **T6** the bootstrap and covered sources | the bootstrap (root-installed under M-12), then only digest-verified in-memory bytes for repository packages | none unverified, provided the import closure is covered (F-6) | **yes** |
| **T7** the children | `/usr/bin/rsync` and `/usr/bin/ssh`, started by the entry with `rp11-launcher-env/1` (§7) | the closed map only, plus root-owned loader configuration | **yes.** This was already correct in the reviewed bytes |

**Consequence.** Every option leaves T0 to T2 exposed to *E_c*. What an option
decides is whether T5 and T6 can be reached by what T0 to T2 consumed. The
reviewed bytes (LB-0) let everything through.

**Reassessment of every pre-entry input under the timing rule.** In the table
below, "reaches" means the input reaches T5 or T6.

*Amended R4-D1-R2.* The LB-2 column now describes LB-2S. The R1 cell for loader
variables under LB-2 read "do not reach. The environment comes from the unit
and the manager (AS-6, PO-8)". It treated the manager's block as closed and is
withdrawn (Appendix B). Two rows for manager state are added.

| Input | LB-0 (reviewed bytes) | LB-1, static launcher | LB-2S, service manager with static first image | LB-3, `sudo` rule |
|---|---|---|---|---|
| `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, `LD_DEBUG`/`LD_PROFILE`, `GLIBC_TUNABLES`, `MALLOC_*` **from the client** | **reach**, and act before the entry's check. This is the defect | do not reach. The static image consults no loader input (PO-9) and passes a literal environment | do not reach. `systemctl start` carries no environment (S-8) | do not reach the entry: `env_reset` drops them (AS-7, PO-10). *(R2)* The `sudo` image itself is loaded under glibc's secure-mode filter, which is a deny-list and not an allow-list (§4.4.4) |
| *(R2)* the same names, and any other name, **from the manager's global environment** (S-1: `DefaultEnvironment=`, `systemd.setenv=`, generators, `set-environment`, locale) or from a unit drop-in's `Environment=` | not involved | not involved | reach **only the static image**, which has no dynamic loader, reads none of them before `main` (PO-9) and passes none on. The entry receives the literal. This depends on PO-14: the executor must not be loaded under the block | not involved. *The analogous root-configured source is `sudo`'s PAM environment (AS-12), which **reaches** the entry unless it is proven absent (PO-10)* |
| *(R2)* manager **execution settings** (S-5: `Default*=`, top-level and unit drop-ins, run-time properties, unit-path resolution) | not involved | not involved | **shape the entry's process**: its limits, its confinement and, at worst, the loaded `ExecStart=`. No unit text can exclude them. They are trusted root input, reviewed and bound at H-1 and H-2 (R-10, M-10). **Not prevention** | the analogue is `sudo`'s defaults and PAM configuration |
| `/etc/ld.so.preload`, `ld.so.cache` | consulted by every dynamic image in every option. Root-owned system state, trusted as R-2 | same | same | same |
| interpreter lookup | absolute venv path, plus `pyvenv.cfg` in an operator-writable tree | `/usr/bin/python3.12`, a literal in the launcher | *(R2)* `/usr/bin/python3.12`, a literal in `rp11-launch`; `ExecStart=` names `rp11-launch` | `/usr/bin/python3.12` fixed in the sudoers rule |
| substitution of the first word | the T2 shell runs it, under *E_c* | absolute launcher path; the T2 shell runs it | absolute `/usr/bin/systemctl`. **The entry's image is fixed by root-installed bytes (the loaded `ExecStart=` and `rp11-launch`'s literal), whatever the requester is.** *(R2)* The loaded `ExecStart=` is root input reviewed at H-2 (S-5) | absolute `/usr/bin/sudo`. The entry's image is fixed by the root-owned rule |
| working directory | inherited. `-m` put it on `sys.path` (OB-16): **module lookup from the working directory** | the launcher calls `chdir("/")` | `WorkingDirectory=/`, and `rp11-launch` calls `chdir("/")` *(R2)* | inherited, because `sudo` keeps it. The bootstrap's first statement is `chdir("/")`, and `-I` keeps the working directory off `sys.path` |
| module lookup | working directory, venv site-packages, `.pth` files and `__pycache__` | `-I -S`: the root-owned standard library, and verified bytes only for repository packages. No `.pyc` is read or written for them | same | same |
| shell start-up | T2 only; not avoidable | T2 only. No shell after T3 | T2 only. No shell after T3 (`ExecStart` is not a shell) | T2 only. `sudo` without `-s`/`-i` runs the command directly |
| Python start-up inputs | `-E -s` ignore `PYTHON*` and the user site, but **not** venv `.pth` files | `-I -S` | `-I -S` | `-I -S` |
| inherited descriptors | all of the client's | the launcher closes every descriptor ≥ 3 | none from the client: `StandardInput=null`, and stdout and stderr go to the journal. *(R2)* `rp11-launch` also closes every descriptor ≥ 3 | `closefrom` 3 by default (PO-10) |
| signal dispositions and mask, umask, rlimits | inherited | the launcher resets dispositions, the mask and the umask. Rlimits are inherited | from the manager and the loaded unit configuration, not the client. *(R2)* That is root input (R-10). `rp11-launch` resets dispositions, the mask and the umask | partly reset (PO-10). The bootstrap sets the umask |
| seccomp, Landlock, namespaces, cgroup, `no_new_privs` (AS-10) | inherited | inherited. **Cannot be removed** | **not inherited from the client**. The entry is a child of PID 1. *(R2)* Confinement that the loaded unit configuration sets (for example a top-level drop-in) applies and is root input (R-10) | inherited. Under `no_new_privs`, `sudo` cannot elevate and **fails closed** |
| ancestry (tracing by the client under Yama scope 1; T-B only) | descendant | descendant | **not a descendant** | descendant, after the target identity is restored |
| caller-supplied values | digests and a path on the command line (OB-16) | none. The pass configuration is at a fixed root-owned path | none | none |

**Earliest trusted component, and how it is bound.**

* **LB-2S** *(amended R2)*. The earliest trusted components are PID 1, polkit
  and the **loaded** unit configuration. That configuration is the unit file,
  whose installed digest the pass configuration records, plus any drop-ins and
  manager defaults, which H-1 and H-2 review (S-5, R-10). Next comes the
  executor under systemd 255 or later (AS-13, PO-14). Then comes **the static
  `rp11-launch`**, root-installed with its digest in the pass configuration.
  **It is the earliest component that fixes the entry's environment.** Then
  come `/usr/bin/python3.12` (root-owned, M-5) and the bootstrap (M-12).
  * **Fixed by root-installed bytes:** the entry's image, argv and
    environment. The environment is `rp11-launch`'s literal.
  * **Not requester-derived:** the entry's other process state. It is not
    fixed by the unit file alone, because manager execution settings shape it
    (R-10).
  * **Withdrawn:** the R1 sentence that the environment was "fixed by
    root-owned bytes" through the unit (Appendix B).
* **LB-3.** The kernel's setuid transition, then `sudo` and the sudoers rule,
  both root-owned. The image and argv are fixed by the rule, and the
  environment is built by `sudo`.
* **LB-1.** The static launcher image. Its bytes are bound by an installation
  digest; its invocation comes from the T2 shell; its own environment is
  ignored.
* **LB-0.** None. The first reviewed instruction runs after *E_c*'s loader has
  acted, which is Codex's finding.

**Narrowing T1, which is not prevention.** Changing each hook's shebang to
`#!/usr/bin/python3 -I` would remove the `PATH` lookup and the Python start-up
inputs from T1. The loader inputs would remain. This is offered as optional
decision **M-13**, and it is never described as protecting the hook layer.

### 4.4 Launch-boundary options (*new, R4-D1-R1*)

#### 4.4.1 Rejected: forms that cleanse after an untrusted loader has acted

Each form below is rejected for the same reason. **The component that does the
cleansing or checking was itself loaded under *E_c*** (§4.3), so at most it
detects.

| Form | Why it is not prevention |
|---|---|
| the reviewed bytes' name check (old §6.9 R-4, old `entry-loader-variable`) | it runs inside the process the loader has already populated. It is kept only as the **diagnostic** `entry-environment-unexpected` (§7.7, §7.9) and is never called a refusal that protects the boundary |
| `env -i …`, `env -u LD_PRELOAD …`, `exec env -i …` | `/usr/bin/env` is dynamically linked and is loaded with *E_c*'s preload before it clears anything |
| `unset LD_PRELOAD; …`, or an assignment prefix `LD_PRELOAD= …` | the T2 shell was loaded with it already. It is a deny-list over an open set. It also makes the invocation a compound or prefixed command, which changes what the guard inspects |
| re-executing the entry with a clean environment (`os.execve(sys.executable, …, clean)`) | the first image ran preloaded code, which can intercept `execve` |
| `python -I` or `-E -s` alone | Python-level inputs only. The loader acts earlier |
| an explicit loader invocation (`ld.so --library-path …`) | the loader still reads its environment variables |
| *(R2)* a unit `UnsetEnvironment=` listing `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, `GLIBC_TUNABLES` and others (LB-2U, §4.4.3.3) | the filtering happens before `execve`, but it is a finite deny-list over an open, version-dependent set (S-1, S-3, S-4). It has no pattern form, so it cannot name a future, platform-specific or unknown loader input |
| *(R2)* `ExecStart=/usr/bin/env -i …`, or a shell as `ExecStart=` | `/usr/bin/env` and the shell are dynamically linked, so they are loaded under the unit's assembled block before they clear anything |
| *(R2)* a distribution-provided static `env -i` or multi-call binary | a cleansing utility. If it is linked against static glibc, its start-up processes `GLIBC_TUNABLES` before `main` (AS-11) |
| *(R2)* an `ExecStartPre=` that inspects `systemctl show-environment` and fails the start | the checking image is loaded under the same block. What it checks can change between that check and `ExecStart=` (S-7). At most it detects |
| *(R2)* treating root ownership of the unit files as closing the manager's environment | the block's contents come from sources that are not the unit file (S-1, E-2 … E-8), and some of them change at run time (S-7) |

**What is not a cleansing form** *(R2)*. LB-2S's `rp11-launch` (§4.4.3.4)
differs from every row above on the timing rule of §4.3.

* **Nothing runs before its code.** It has no dynamic loader, and under PO-9
  its start-up consults no environment.
* **It removes nothing.** It discards the block wholesale and constructs a
  literal. The only thing it takes from the block is one exact name,
  `INVOCATION_ID`, whose value it checks against a grammar as data.

If PO-9 fails for the chosen runtime (AS-11), `rp11-launch` falls into the
rows above and LB-2S is withdrawn.

#### 4.4.2 LB-1: a static first-exec launcher

**Client-inspected invocation:** `/usr/local/libexec/freedom-blades-rp11/rp11-launch --pass A`

This is a compiled, statically linked executable. It is built so that no
C-library start-up code consults the environment: no `GLIBC_TUNABLES`
processing, no `dlopen`, no NSS and no iconv (PO-9). It never reads `envp`. It
then does the following, in order:

1. closes every descriptor ≥ 3;
2. resets every signal disposition to its default and clears the mask;
3. sets `umask 077`;
4. calls `chdir("/")`; and
5. calls `execve("/usr/bin/python3.12", ["python3.12", "-I", "-S", "<bootstrap>", "run", "--pass", "A"], <rp11-entry-env/1 literal>)`.

It accepts `--pass A` and nothing else.

*(R2)* **Under the pre-loader rule, LB-1 meets the environment requirement.**
Its image is the same `rp11-launch` that LB-2S uses (§4.4.3.4). Started by the
client, it writes the two-entry literal `{LC_ALL=C, PATH=/usr/bin}`, because no
`INVOCATION_ID` exists. It depends on PO-9. A glibc-static build does not
qualify (AS-11), and the runtime is decision M-14. **Its limit is unchanged:**
it is a descendant of the client and inherits the client's execution state
(below). No image can remove that state.

| Criterion | Assessment |
|---|---|
| native-loader timing | prevents loader and Python start-up inputs from reaching T5. T2 is still exposed |
| *(R2)* start-up runtime | PO-9: nothing that runs before `main` may read the environment, `dlopen`, or initialise NSS, iconv, locale or tunables. A glibc-static build is excluded unless PO-9 disproves AS-11. Choosing the runtime is M-14 |
| other process state | **inherits** the client's seccomp, Landlock, namespaces, cgroup and rlimits. A client sandbox filter could, for example, make `fsync` return success without doing anything. The launcher cannot remove that. It is still a descendant |
| bypass | under T-A, none that reaches the entry. Under T-B, the T2 shell need not run it (M-10) |
| TOCTOU | its image is bound by an installation digest only; nothing rechecks it at run time. If the file sits in an operator-writable location, T-B can replace it |
| portability | Linux, one architecture per build. **It adds a compiled language, a toolchain and a reproducible-build step to a pure-Python repository**, which AGENTS.md requires to be a deliberate dependency decision |
| non-Claude | same entry guarantee, no hook layer (§4.4.6) |
| repository-only testability | the build and the launcher's behaviour under a poisoned environment can be tested in the repository, **but only by running a loader experiment in a later, authorized implementation slice**. Installation is a host act |
| provisioning | a root-owned installation location is recommended, which is host provisioning |

#### 4.4.3 LB-2 and its correction LB-2S: the system service-manager boundary (*rewritten R4-D1-R2*)

**Client-inspected invocation (unchanged from R1):**
`/usr/bin/systemctl --no-ask-password start --wait rp11-capture-pass-a.service`

*The R1 subsection is replaced. It presented a unit that added `PATH` and
`LC_ALL` to the manager's environment as a boundary that "prevents" loader
state. Codex's re-review found that the unit left that environment open
(`R4-D1-R1-1`). The R1 unit text is kept below in §4.4.3.3 as the withdrawn
form. Every R1 claim that is withdrawn or narrowed is quoted in Appendix B.*

##### 4.4.3.1 The system-manager semantics relied upon

These are stated from the author's understanding of `systemd.exec(5)`,
`systemd.unit(5)`, `systemd-system.conf(5)`, `systemd(1)` and
`systemd.environment-generator(7)` for systemd 25x. **None was verified against
the repository host's installed version**, because host inspection is
prohibited. PO-8 (revised) requires each to be confirmed by version before
implementation. If any one is wrong in the direction of *more* sources, the
analysis below still holds. If S-4 is wrong because a directive that discards
the global environment exists, §4.4.3.3 must be revisited.

| # | Semantics | Consequence here |
|---|---|---|
| **S-1** | **Assembly order.** A system service's environment block is assembled from these sources, in increasing precedence. (a) **The manager's global environment**: `DefaultEnvironment=` in `system.conf` and `system.conf.d/*.conf`; `systemd.setenv=` on the kernel command line; the output of system environment generators; the locale PID 1 applies from `/etc/locale.conf` or `locale.LANG=`; and run-time `systemctl set-environment` and `import-environment` (D-Bus `SetEnvironment` and `UnsetAndSetEnvironment`). (b) **Variables the manager defines itself** (S-3). (c) Names from **PID 1's own process environment** listed in `PassEnvironment=`. (d) `Environment=`. (e) `EnvironmentFile=`. (f) The **PAM environment** when `PAMName=` is set. A later source wins on a name collision | (a) is open. It is the source Codex identified |
| **S-2** | **PID 1's own process environment** is not passed, except for names listed in `PassEnvironment=`, whose default is empty. PID 1's own environment is set at boot by the kernel and the initrd | excluded by default. A drop-in can add `PassEnvironment=` (S-5) |
| **S-3** | **Manager-defined variables** depend on the version and have grown over time. `PATH` gets a fixed default. `USER`, `LOGNAME`, `HOME` and `SHELL` are set for units with `User=`. `INVOCATION_ID` is always set, and `JOURNAL_STREAM` is set when an output goes to the journal. Each of the following is set when its feature applies: `NOTIFY_SOCKET`, `WATCHDOG_*`, `LISTEN_*`, `*_DIRECTORY`, `CREDENTIALS_DIRECTORY`, `TRIGGER_*`, `MONITOR_*`, `SERVICE_RESULT`, `EXIT_*` and `TERM`. Newer versions add `SYSTEMD_EXEC_PID` and `MEMORY_PRESSURE_WATCH`/`_WRITE` | **not a closed set across versions**, so no fixed key list can describe it for every host |
| **S-4** | **No allow-list directive.** `UnsetEnvironment=` takes names or exact `NAME=VALUE` assignments. It has no pattern form and is applied as the last step. No unit directive discards source (a) as a whole. *This is stated to the author's knowledge of documented directives through systemd 256. PO-8 confirms or refutes it for the installed version* | a unit can add names and remove a finite, named set. It cannot construct an allow-list |
| **S-5** | **The loaded configuration is not one file.** For a unit name, PID 1 uses the fragment with the highest priority in the unit search path. `/etc/systemd/system.control`, `/run/systemd/system.control`, `/run/systemd/transient` and `/run/systemd/generator.early` precede `/etc/systemd/system`. On top of the fragment come all drop-ins: `⟨unit⟩.d/*.conf` in every search directory; top-level type drop-ins `service.d/*.conf`, which apply to every service (systemd 246 and later); and the run-time drop-ins written by `systemctl set-property --runtime` or `systemctl edit --runtime`. The manager's `Default*=` settings (limits, accounting and others) also apply. Generators run at boot and at every `daemon-reload`, and they may write units and drop-ins | **what PID 1 executes, and with which environment and execution settings, is not fixed by the installed unit file alone** |
| **S-6** | **When filtering happens.** The block is assembled, and `UnsetEnvironment=` applied, in the process that will `execve` the command, immediately before that `execve`. Under AS-13 that process is `systemd-executor`, and otherwise it is a forked copy of PID 1. Nothing systemd does after the `execve` changes the command's environment | the timing is right, but the result is open. **The `ExecStart=` image's loader sees whatever the block holds** |
| **S-7** | **Run-time mutation.** A caller authorised for `org.freedesktop.systemd1.set-environment` (by default an administrator) can change source (a) at any time. So can a `daemon-reload`, which re-runs generators and, depending on the version, re-reads `system.conf` (PO-8). A unit started after the change receives the changed block | root ownership of files does not fix the block. A check made earlier is a snapshot |
| **S-8** | **The requester.** `systemctl start` sends `StartUnit(name, mode)` over the system bus, and polkit decides whether it is allowed (PO-11). The call carries **no** environment, descriptor, working directory, limit or confinement of the requester | this is the part of R1 that stands: **no client-derived state reaches the unit** |
| **S-9** | **`User=` is not a secure-mode transition.** Credentials are switched before the command's `execve`. The command is not set-id, so the kernel does not set `AT_SECURE` for it and glibc applies no secure-mode filtering to the entry. `NoNewPrivileges=yes` does not filter the environment either | no kernel or C-library filter helps LB-2 |
| **S-10** | **PAM.** Without `PAMName=` no PAM module runs and no PAM environment is added. A drop-in could add `PAMName=` (S-5) | excluded by the unit text. Whether it stays excluded is an H-2 check |

##### 4.4.3.2 Every source that can reach the `ExecStart=` image's `execve`

*Class* uses the assignment's distinctions:

* *unit bytes*: the repository file as installed;
* *manager configuration*: files read by PID 1;
* *boot*: set before PID 1 ran;
* *run-time API*: held by PID 1 and changed through D-Bus;
* *derived*: computed by systemd; and
* *post-`execve`*: exists only after the image ran.

| # | Source | Class | Who can change it | Can the unit text exclude it? | Precedence (S-1) |
|---|---|---|---|---|---|
| E-1 | `Environment=` in the unit file | unit bytes | root, by installing | — (it is the unit). **LB-2S sets none** | (d) |
| E-2 | `Environment=`, `EnvironmentFile=`, `PassEnvironment=`, `UnsetEnvironment=` or `PAMName=` in a unit or top-level drop-in, run-time drop-ins included | manager configuration (S-5) | root, generators, `systemctl edit` and `set-property` | **no**: a drop-in adds to or overrides the unit | by directive, (c) … (f) |
| E-3 | `DefaultEnvironment=` | manager configuration | root. It takes effect at re-execution or reload (PO-8) | **no** | (a), lowest |
| E-4 | `systemd.setenv=` | boot | bootloader configuration | **no** | (a) |
| E-5 | system environment generators' output | manager configuration (root executables) | root and packages | **no** | (a) |
| E-6 | `set-environment` and `import-environment` | run-time API | an authorised caller, at any time (S-7) | **no** | (a) |
| E-7 | locale (`/etc/locale.conf`, `locale.LANG=`) | manager configuration and boot | root | only by naming each variable in `UnsetEnvironment=` | (a) |
| E-8 | manager-defined variables (S-3) | derived | the systemd version and the unit's features | only by name, and the set depends on the version | (b), which overrides (a) |
| E-9 | PID 1's own process environment | boot | kernel and initrd | **yes, by default** (S-2), unless a drop-in adds `PassEnvironment=` | (c) |
| E-10 | PAM environment (`/etc/environment`, `pam_env.conf`) | manager configuration, only with `PAMName=` | root | **yes**, by omitting `PAMName=` (S-10), unless a drop-in adds it | (f), highest |
| E-11 | variables the command sets for itself | post-`execve` | the command | irrelevant to the loader: they exist only after it ran | — |

**Collision and filtering.** A name set by a later source replaces the earlier
value. `UnsetEnvironment=` then removes named entries, **immediately before
the `execve`** (S-6). Filtering therefore happens at the right time, but only
over names someone thought to list. **Every name from E-3 … E-7 that no later
source overrides and no `UnsetEnvironment=` entry names is presented to the
`ExecStart=` image's loader.**

##### 4.4.3.3 Can a unit construct an allow-list before `execve`? No

A unit can do three things to the environment:

* add names (E-1);
* remove a finite, named set (`UnsetEnvironment=`); and
* leave out PID 1's own environment and PAM (E-9, E-10), which it does by
  default.

It cannot discard E-3 … E-7 as a class (S-4), and E-8 grows by version (S-3).
**So a system unit cannot, by itself, make the environment of a dynamically
linked `ExecStart=` image closed.** Four variants follow from that.

**LB-2, the R1 form: withdrawn as prevention.** Its unit text was:

```ini
[Service]
Type=exec
User=⟨MI.operator_account⟩
ExecStart=/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_entry.py run --pass A
WorkingDirectory=/
UMask=0077
StandardInput=null
StandardOutput=journal
StandardError=journal
Environment=LC_ALL=C
Environment=PATH=/usr/bin
NoNewPrivileges=yes
```

`/usr/bin/python3.12` is dynamically linked. Its loader consumes the whole
block, E-3 … E-8 included, before §7.9's check runs. An ambient
`DefaultEnvironment=LD_PRELOAD=libeatmydata.so` would turn the §9.5.1 `fsync`
barrier into a no-op inside the entry, exactly as the client-side example in
§1 did. **Codex's finding is confirmed.** The R1 statements that relied on
this unit are withdrawn (Appendix B).

**LB-2U, the R1 unit plus `UnsetEnvironment=` of the known loader names:
rejected.** It is a deny-list over an open, version-dependent set (S-3, S-4).
It cannot name future, platform-specific or unknown loader inputs, and it has
no pattern form. Adding such a list as unclaimed hardening is possible. It is
not proposed, because nothing may credit it.

**LB-2T, narrowed trust (outcome 2): assessed and not recommended.** Keep the
R1 unit, and declare E-2 … E-8 **trusted root input**. H-1 and H-2 review them
before each pass: `show-environment`, the unit's effective `Environment`,
`FragmentPath` and `DropInPaths`, the digests of `system.conf*` and the
generator directories, and the kernel command line. It fails on three counts.

1. **It contradicts T-A as defined.** Ambient manager state is T-A (§4.3).
   Adopting LB-2T means moving E-3 … E-7 out of T-A, which is a redefinition.
   This proposal does not make it. It is offered only as an explicit M-10
   option, so that the maintainer can see what it costs.
2. **The review is a snapshot.** S-7 lets E-3, E-5 and E-6 change between the
   review and the start. The only process positioned to check at start time is
   the entry, and that check comes after the loader.
3. **It reads and records environment content.** Reviewing E-6 means printing
   the manager's environment into evidence, which C-9 forbids for handbacks
   and which could carry values nobody reviewed.

So LB-2T gives **review, not prevention**.

**LB-2S: the corrected form (outcome-1 shape).** It is specified next.

##### 4.4.3.4 LB-2S: the unit, the static first image, and what they establish

**The unit** is a proposed repository file,
`infra/systemd/rp11-capture-pass-a.service`. It is installed under H-1 at
`/etc/systemd/system/`, root-owned. Its installed bytes are the repository
bytes with one maintainer substitution, `⟨MI.operator_account⟩`. The pass
configuration records the installed bytes' digest.

```ini
[Unit]
Description=Freedom Blades RP-11 capture entry, Pass A (reviewed bytes; installed only under authorization)

[Service]
Type=exec
User=⟨MI.operator_account⟩
ExecStart=/usr/local/libexec/freedom-blades-rp11/rp11-launch --pass A
WorkingDirectory=/
UMask=0077
StandardInput=null
StandardOutput=journal
StandardError=journal
NoNewPrivileges=yes
```

**Changes from the R1 unit, and why.**

* `ExecStart=` names the static first image instead of the interpreter.
* The two `Environment=` lines are **removed**. Nothing relies on the block any
  more. Keeping them would suggest that the unit establishes the entry's
  environment, which it does not.

The unit still has no `EnvironmentFile=`, `PassEnvironment=`,
`UnsetEnvironment=`, `PAMName=`, `ExecStartPre=` or `ExecStartPost=`, no
credential import and no template instance. **Those absences are properties
of the text** (T-B1). They say nothing about the **loaded** configuration
(S-5), which H-1 and H-2 check.

**The static first image, contract `rp11-launch/1`.** Its source and build
definition are proposed repository files under M-14. Its binary is installed
under H-1, root-owned, mode `0755`, at
`/usr/local/libexec/freedom-blades-rp11/rp11-launch`. Every parent directory up
to `/` is root-owned and not group- or world-writable. The installed digest is
in the pass configuration.

1. **Start-up.** Nothing that runs before `main` reads an environment
   variable, calls `dlopen`, or initialises NSS, iconv, locale or tunables
   (**PO-9**). The runtime is decision M-14. A glibc-static build is excluded
   unless PO-9 disproves AS-11.
2. **Arguments.** Exactly two operands after `argv[0]`: `--pass` and `A`.
   Anything else exits with a fixed usage status and no `execve`.
3. **The block.** `envp` is scanned byte-wise for entries whose name is
   exactly `INVOCATION_ID`. Exactly one is required, with a value matching
   `[0-9a-f]{32}`. Otherwise the image exits with a fixed status and no
   `execve`. **No other entry is copied, parsed, interpreted or passed on.**
   Under S-1, E-8 overrides E-3 … E-7 for this name. A unit drop-in's
   `Environment=INVOCATION_ID=…` could still override E-8. The value is
   therefore used only as provenance, which is diagnostic (§6.8).
4. **State.** In order, it closes every descriptor ≥ 3, resets every signal
   disposition to its default, clears the signal mask, sets `umask 077` and
   calls `chdir("/")`.
5. **The `execve`.** It calls `execve("/usr/bin/python3.12",
   ["/usr/bin/python3.12", "-I", "-S",
   "/usr/local/libexec/freedom-blades-rp11/rp11_entry.py", "run", "--pass",
   "A"], ["LC_ALL=C", "PATH=/usr/bin", "INVOCATION_ID=⟨value⟩"])`. The vector
   and the environment are compiled literals, except for the checked value.
6. **Failure.** Any failed step exits with a fixed status per step. It never
   falls back, retries or `execve`s anything else. Its only output is a fixed
   one-line class name on standard error, which goes to the journal. That line
   contains no value.

**Polkit rule, pass configuration and bootstrap.** They are as in R1:
`infra/polkit/50-freedom-blades-rp11.rules`, verbs `start` and `stop` only,
for one unit and one subject user. The pass configuration
`/etc/freedom-blades-rp11/pass-a.json` gains one field, `launcher_sha256`. The
bootstrap is unchanged except that its environment check uses the LB-2S key set
(§7.9). The R1 polkit rule text is unchanged:

```js
polkit.addRule(function (action, subject) {
  if (action.id == "org.freedesktop.systemd1.manage-units" &&
      action.lookup("unit") == "rp11-capture-pass-a.service" &&
      (action.lookup("verb") == "start" || action.lookup("verb") == "stop") &&
      subject.user == "⟨MI.operator_account⟩") {
    return polkit.Result.YES;
  }
});
```

`stop` is allowed so that the operator can interrupt a hung pass. A stop is an
interruption under draft §9.5.3, not new semantics (PO-11).

**What reaches which image.**

| Image | Loaded or started under | Consumes before its own code |
|---|---|---|
| PID 1 | its boot environment (E-9) | root state, trusted (R-8) |
| `systemd-executor` (systemd 255 and later) | PID 1's own process environment (AS-13) | root state, trusted. **If PO-14 finds that it is loaded under the unit's block, LB-2S is withdrawn for that version**, because a dynamically linked image that chooses and starts `rp11-launch` would then be exposed to E-3 … E-8 |
| `rp11-launch` | the unit's **open** block (E-1 … E-8) | **nothing** (PO-9) |
| `/usr/bin/python3.12`, then the bootstrap | the literal `rp11-entry-env/1` only | the literal, `/etc/ld.so.preload` and `ld.so.cache` (root-owned, R-8), and the interpreter prefix (AS-8) |

**The allow-list question, answered for LB-2S.** Yes. The entry's environment
is an allow-list, and it exists before the entry's `execve`. **It is built by
`rp11-launch`, not by systemd.** systemd's part is to create the process
outside the client's reach (S-8) and to start a fixed image. Only PO-9 and
PO-14 condition that answer.

##### 4.4.3.5 What LB-2S prevents, what it trusts, and what it only diagnoses

| Property | Kind | How it would be established | Credited as |
|---|---|---|---|
| the unit text has the stated keys and `ExecStart=` literal, and no environment, PAM or pre-start directive | **repository-testable configuration-text property** | T-B1 | text only. It says nothing about the loaded configuration (S-5) |
| `rp11-launch`'s source holds the exact `execve` vector and environment literal recorded in the manifest, and reads `envp` only for `INVOCATION_ID` | **repository-testable** property of the source | T-B13, T-B14 | text only. It does not show how the built image behaves |
| the image's start-up reads nothing (PO-9) | **build and host proof obligation** | a runtime-source citation (M-14 design pass), then a later authorized loader experiment on the built image | a **prerequisite** for prevention |
| the executor is not loaded under the block (PO-14) | **host proof obligation** | a citation of the installed systemd version's source | a **prerequisite** for prevention |
| the installed digests of the unit, rule, launcher, bootstrap and pass configuration; `FragmentPath` is `/etc/systemd/system/rp11-capture-pass-a.service`; `DropInPaths` is empty; `NeedDaemonReload=no` | **installation-time check** (H-1) | root, under its own authority | binding of root-controlled input. **Not prevention** |
| the same, plus the effective `ExecStart`, `User`, `NoNewPrivileges`, limit, confinement and `PAMName` properties, and the manager's `Default*=` values | **pre-pass check** (H-2) | a separately authorized host step before each pass, bound into that pass's authorization | review of trusted root input (R-10). **Not prevention**, and open to S-7 changes afterwards |
| **the entry's environment is exactly `rp11-entry-env/1`** | **prevention** | the literal `execve` by `rp11-launch`, given PO-9 and PO-14 | **the only environment-prevention claim in this proposal** |
| **no client-derived process state reaches the entry** | **prevention** | PID 1 creates the process (S-8) | as in R1 |
| the entry's own environment check, `INVOCATION_ID` and parent PID 1 | **diagnostic** | §6.5, §7.9 | never prevention |
| a drill in which a poisoned manager environment leaves the entry's environment digest unchanged | **host proof obligation** (PO-16) | a later, separately authorized drill | corroboration for one host at one time. **Not proof of the contract** |

**The manager's global environment is not inspected or recorded** under
LB-2S. The design does not rely on it, and recording it would put unreviewed
environment content into evidence (C-9).

##### 4.4.3.6 Assessment

| Criterion | Assessment |
|---|---|
| native-loader timing | **prevents, for the entry.** Client loader state never reaches the unit (S-8). Manager loader state reaches only `rp11-launch`, which consumes none of it (PO-9, PO-14). The entry's loader sees the literal only. *The R1 cell ("PID 1 creates the entry. No client-derived variable exists in its environment") is withdrawn as a prevention claim: true about the client, silent about the manager* |
| other process state | **client-derived state is prevented.** The working directory, descriptors, signal state and umask are also reset by `rp11-launch`. **Manager-derived execution state is not prevented**: limits, confinement and drop-in settings come from the loaded configuration (S-5). It is trusted root input, reviewed at H-1 and H-2 (R-10) |
| bypass | the client (T2, `systemctl`) can decline to request the unit, or request another unit it may already start. **It cannot change what this unit runs, with what argv or with what environment.** Under T-B it can still run the direct path, or forge files under the operator's account (M-10) |
| TOCTOU | the files are root-owned and fixed before the pass. The repository sources are read once and verified before any executes. The hook's catalogue view is tied to the same bytes (§5.4). *(R2)* **The loaded configuration and the manager's defaults can change between H-2 and the start (S-7).** For the environment that does not matter, because `rp11-launch` ignores the block. For execution settings it is the R-10 trust |
| portability | needs systemd as PID 1, polkit and a system bus (AS-6), **and a static image for the host's architecture** (M-14). A sandboxed client that cannot reach the system bus **fails closed**, because no entry process exists |
| non-Claude | identical literal, identical entry guarantee (§4.4.6) |
| provenance | `INVOCATION_ID`, copied by `rp11-launch`, is recorded in the genesis state. It is provenance evidence, not integrity against T-B |
| repository-only testability | the text properties in §4.4.3.5 only. **The prevention property depends on PO-9 and PO-14, which are not repository-testable here** |
| provisioning | host provisioning on the repository host (H-1): root installation of five files (unit, rule, pass configuration, bootstrap and launcher) and `systemctl daemon-reload`. Plus H-2 before each pass, and the build dependency (M-14). All of this is outside every current authority |

##### 4.4.3.7 Installation record, pre-pass check, rollback and later drill

**The H-1 installation record** is written by root under its own future
authority and bound into the A-2 authorization by digest. It holds:

* the SHA-256 of each installed file (unit, polkit rule, `rp11-launch`,
  bootstrap and pass configuration) and of each repository source;
* the unit's `FragmentPath`, `DropInPaths` and `NeedDaemonReload` as reported
  by the manager, with `DropInPaths` required to be empty; and
* the systemd, polkit, glibc and CPython package versions against which PO-8,
  PO-11, PO-12 and PO-14 were cited.

It holds **no** environment content.

**The H-2 pre-pass check** is made immediately before each pass, under the
same authority. It re-reports the H-1 digests and manager properties, plus
the effective `ExecStart`, `User`, `NoNewPrivileges`, `PAMName`,
`PassEnvironment`, limit and confinement properties of the loaded unit, and
the manager's `Default*=` values. The pass's authorization binds its digest.
Any difference from H-1 stops the pass before it is requested. **H-2 is a
review of trusted root input at one moment. It is never described as
preventing a later change** (S-7).

**Rollback.** H-1's rollback removes the five installed files and runs
`systemctl daemon-reload`. No capture root is touched. The repository slices
roll back as in §12.

**The later host drill (PO-16)** is a separately authorized step and may run
only on a host where a manager-wide change is permitted. It would set a
harmless sentinel variable in the manager's environment, start the unit with a
test pass configuration, and compare the entry's recorded
`entry_environment_sha256` with the literal's digest. At most it corroborates
PO-9 and PO-14 for one host, one version and one moment. It does not prove
the contract, and no record may present it as proof.

#### 4.4.4 LB-3: a `sudo` command rule

**Client-inspected invocation:** `/usr/bin/sudo -n -u ⟨MI.operator_account⟩ -- /usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_entry.py run --pass A`

A root-owned drop-in, `/etc/sudoers.d/freedom-blades-rp11`, allows exactly
that command for the operator, running as the operator, with `NOPASSWD`. A
command-specific `Defaults` entry resets the environment with an empty keep
list and `secure_path=/usr/bin`. The exact sudoers syntax and semantics for the
installed version are PO-10.

**Reassessment under the pre-loader rule** *(R2)*. `sudo` does build a new
environment before the entry's `execve`, and the entry's loader sees only
that environment. That environment is **not closed**, for two reasons:

1. **The `env_reset` base is not empty.** It carries `sudo`'s own keep and
   check defaults, which differ by distribution and version. A command-specific
   `Defaults` entry may be able to clear them (PO-10).
2. **The PAM environment is added.** On Debian-family systems it comes from
   `/etc/environment`, `pam_env.conf` and `/etc/default/locale` (AS-12). It is
   a root-configured, open source, and it is the exact analogue of the
   manager's global environment under LB-2. Unless PO-10 shows that the
   installed `sudo` merges no PAM environment for this command, ambient
   configuration there reaches the entry's loader.

The `sudo` image itself is also loaded under the client's environment as
glibc's secure mode filters it. That filter is a **deny-list** maintained by
glibc. Some tunables, for example, are retained for set-id images. So the
component that builds the entry's environment has consumed a filtered, not a
closed, input.

A variant, **LB-3S**, names `rp11-launch` as the ruled command. It would close
the entry's environment as LB-2S does. It would still leave the `sudo` image's
deny-list exposure, the inheritance of client confinement, and the current
prohibition on `sudo`. It is strictly weaker than LB-2S, and it is not
developed further.

| Criterion | Assessment |
|---|---|
| native-loader timing | *(amended R2)* client loader variables do not reach the entry: `AT_SECURE` for `sudo`, then `env_reset` (AS-7). **Root-configured PAM variables can reach it (AS-12). The `sudo` image is filtered by a deny-list, not closed.** Not prevention of all unreviewed loader state |
| other process state | the working directory, some signal state and rlimits are inherited (PO-10). **Seccomp, Landlock and namespaces are inherited.** It is a descendant after the identity is restored |
| bypass | as LB-2S: `sudo` runs only the ruled command |
| TOCTOU | as LB-2S, for the rule and the bootstrap |
| portability | needs `sudo` on the repository host. Under `no_new_privs` it fails closed. Distribution defaults such as `use_pty` change the entry's own standard streams, which are not evidence |
| non-Claude | as LB-2S |
| repository-only testability | the rule text only. Its effect is a host property |
| provisioning | a root-owned sudoers drop-in: host provisioning. The current restrictions also forbid `sudo` on any host |

#### 4.4.5 Comparison

*Amended R4-D1-R2.* The R1 table credited LB-2 with "yes (PO-8)" for
preventing loader state from reaching the entry. That is withdrawn (Appendix
B). The R1 unit is kept as a column to show why.

| | LB-0 (reviewed bytes) | LB-1 | LB-2 (R1 unit, withdrawn) | **LB-2S** | LB-3 |
|---|---|---|---|---|---|
| the entry's environment is an allow-list built before its `execve` | no | yes (PO-9) | **no**: an open manager block (S-1, S-4) | **yes** (PO-9, PO-14) | **no**: PAM merge and `sudo` defaults (AS-12, PO-10) |
| client loader state kept from the entry | **no** | yes | yes | **yes** | yes |
| manager or PAM loader state kept from the entry | not involved | not involved | **no** | **yes** | **no** (PAM) |
| enforcing images before the entry loaded only under closed or root-boot state | no | yes (the static image) | no | **yes**, given PO-14 | no: `sudo` is loaded under a deny-list-filtered client environment |
| all client-derived process state kept from the entry | no | no | yes | **yes** | no |
| manager-derived execution state | not involved | not involved | trusted, unreviewed | **trusted root input, reviewed at H-1 and H-2 (R-10)** | the `sudo` and PAM analogue |
| entry is a descendant of the client | yes | yes | no | **no** | yes |
| caller-supplied values in the invocation | yes | no | no | **no** | no (except the fixed account name) |
| new build dependency | no | **yes** (M-14) | no | **yes** (M-14) | no |
| host provisioning on the repository host | no | yes (installation) | yes | **yes** (H-1, H-2) | yes, and `sudo` is prohibited now |
| implementable repository-only | yes, but defective | no | no | **no** | no |
| **ready for recommendation** | no | no | **no** (withdrawn) | **no**: needs M-14, M-10 (revised), PO-9, PO-14 | no |

**No option grants a wrapper exemption or hides §5's text.** Each
client-inspected invocation takes **no command operand**. The hooks apply
their unchanged rules to the literal, which names no secret and contains no
metacharacter. Under O-2 they then *add* evaluations of every catalogue text.
An exact match never skips a rule, and a near match is refused (§9). §5's text
never travels on the command line, so nothing hides it. The canonical policy
inspects it **unchanged** inside the entry (§5.4). The invocation is a fixed
request for one reviewed program, not a prefix that runs whatever follows it.

#### 4.4.6 What protects a non-Claude operator when client hooks are absent

* **No client-side pre-start inspection exists**, under any option. The direct
  path gives a non-Claude operator no guard at all today (AGENTS.md "Skills and
  enforced guards", rule 3).
* **Under LB-1, LB-2S or LB-3,** every act the entry executes was allowed by
  the canonical policy before X-1 and again immediately before its launch,
  **in a process that *E_c*'s loader state never reached.** Under LB-2S it is
  also a process that no client-derived state reached at all. This guarantee
  is identical for Claude and non-Claude operators.
* *(R2)* **Only under LB-2S and LB-1 is the entry's environment a closed
  literal** (subject to PO-9, and PO-14 for LB-2S). Under the R1 LB-2 unit and
  under LB-3, root-configured manager or PAM variables can still reach the
  entry's loader. So their in-process gate is **not** fail-closed against
  ambient manager or PAM state, for any operator.
* **Not protected, under any option:**
  * whether the operator issues the invocation at all, or runs §5 directly
    outside RP-11. That is governed by AGENTS.md prose and by the draft's rule
    that only RP-11 records are evidence;
  * forgery of files under the operator's account (T-B, M-10).
* **Under LB-2S,** a genesis `INVOCATION_ID` with no matching journal entry
  written by PID 1 marks a record set that the unit did not produce. This is
  diagnostic provenance only.
* **If M-9 is declined,** a non-Claude operator has **no** protection against
  ambient loader state in the entry. The in-process gate is then not
  fail-closed, exactly as Codex found.

#### 4.4.7 The result, and the minimum maintainer choices

**Impossibility under the current constraints.** The constraints as they stand
are:

* the entry is created through the client's ordinary execution path;
* the implementation is repository-only, with no host configuration and no new
  build toolchain; and
* unreviewed loader state must be prevented from reaching the process whose
  in-process checks enforce C-11.

**No design satisfies all three.** Every process the client's shell creates is
loaded under *E_c*, and so is the shell. Prevention needs an image that
ignores the loader (LB-1: a new build dependency), or a transition
established by root (LB-3), or a process that does not descend from the client
(LB-2). Each is outside the constraints.

**Sharpened by R4-D1-R1-1** *(R2)*. A root transition (LB-3) or a process
outside the client's ancestry (LB-2) is **not enough on its own**. Each hands
the entry an environment assembled from open, root-configured sources: the
manager's global environment (S-1), or `sudo`'s PAM environment (AS-12).
**In every viable design, the entry's environment is closed for one reason
only: a static image that reads no environment performs the entry's `execve`
with a literal.** That is LB-1's image. The service manager adds one thing: it
keeps client process state away (S-8). Hence LB-2S. It combines both, and it
needs both a build dependency and host provisioning.

**Minimum choices for Peter Duscha** *(amended R2)*:

* **M-9, the launch boundary.**
  * LB-2S, the service manager with a static first image. This is the
    conditional direction, needing M-14;
  * LB-1, the static launcher started by the client. It needs M-14, and it
    inherits client execution state;
  * LB-2T, the R1 unit with manager state trusted and reviewed. It is **not
    prevention**, and it is admissible only if M-10 explicitly moves ambient
    manager state out of T-A;
  * LB-3. **Not ready**, because of the PAM merge and the deny-list-filtered
    `sudo` image (§4.4.4), and because `sudo` is currently prohibited; or
  * **decline.** C-11 then stays open, because R4-D1-1's requirement cannot be
    met. Any later text that describes the in-process gate as fail-closed
    against ambient state would be untrue.
* **M-14, the static first image** *(new R2)*. Accept a compiled, statically
  linked image as a new build dependency, and commission a design pass. That
  pass chooses a runtime whose start-up meets PO-9, a reproducible build, a
  pinned toolchain, and how the installed digest is bound. **Without M-14,
  neither LB-2S nor LB-1 exists, and no option prevents unreviewed loader
  state from reaching the entry.**
* **M-10, threat scope** *(revised R2)*.
  * **T-A in scope, with manager execution settings trusted as reviewed root
    input (R-10).** This is the conditional direction. Ambient manager
    *environment* stays in scope and is prevented by LB-2S. Manager
    *execution settings* are reviewed and bound at H-1 and H-2, not prevented.
    T-B is out of scope for record integrity, with LB-2S provenance as
    partial evidence;
  * **T-A narrowed to exclude ambient manager state.** This is the only form
    under which LB-2T is admissible. It is a redefinition of T-A, stated here
    so that it is never adopted silently; or
  * **T-A and T-B.** That needs a dedicated capture account, and therefore a
    new SSH authentication design for that account, because M-1 assumes the
    operator's key or agent. It needs its own design pass.

**M-9, M-14 and M-10 are all needed before any C-11 implementation
assignment.** Under
every option, the T1 and T2 exposure of the client-hook layer remains, as it
does on the direct path. D-1 (§5.3) states it as a property of the baseline,
not as a residual risk.

---

## 5. Why a baseline amendment is unavoidable

### 5.1 The conflict

* **§5 and §6.2** say the operator issues the command as *"one plain call
  through the client's ordinary execution path"*.
* **C-2** requires separate, complete, byte-exact streams, captured on the
  repository host, and **C-1** requires the argv the client process received.
* **The RP-11 row** requires the synchronization to be captured *"without
  changing the command `guard-secrets.py` inspects"*.

The client's Bash tool owns the pipes of the command it runs, and its output
is not evidence (§6.2: *"The client transcript is a convenience and is not
evidence"*). For a capture process to own the pipes, that process must be the
thing the client starts. So the operator's client call cannot be the plain
`rsync` text itself. The alternatives either wrap the text, which violates
G-1 and G-2, or reroute it invisibly, which is a bypass (§8).

### 5.2 What can be preserved exactly

Everything with security meaning can be preserved exactly:

* the command text, byte for byte;
* the fact that the canonical `guard-secrets.py` and `guard-git.py` code
  inspects exactly that text as a Bash `command`;
* *(amended R4-D1-R1)* for a Claude operator, the fact that the client hooks
  inspect it before the invocation starts (O-2 only). This holds for every
  text that is a reviewed literal (K-L, §6.6.1), which under D-2a is every
  Pass A text. The hooks run under the client environment, so this is defense
  in depth (§4.3 T1); and
* the argv, derived deterministically from that text.

What changes is the *carrier*: which process the client starts. Under M-9 it
also changes *which process creates the entry* (§4.4).

### 5.3 Amendment D-1 — the minimum wording change, for the maintainer (*rewritten R4-D1-R1*)

*The reviewed wording is withdrawn (Appendix A). It said that every A1 text is
fixed byte for byte and inspected by the client hooks before the invocation
starts, while §6.6 created a runtime-substituted A1-12 text. It also described
an entry that ambient loader state could reach.*

D-1 would amend draft §5, §6.2 (A1 preamble, A1-12), §9.5 C-1 and C-11, and
the RP-11 row. It **presupposes decisions M-9 and D-2** and names them. *(R2)* Under M-9 = LB-2S it also presupposes M-14 and M-10 (revised). It
applies to **Pass A only** (M-11). The bracketed text states which choice each
clause depends on.

> **Pass A command texts.** The §5 synchronization and every Pass A host
> command are **reviewed literal command texts**, fixed byte for byte in this
> draft and in the pinned act catalogue. [D-2a: A1-12 is the literal
> `ssh oracle-test "sha256sum /opt/freedom-blades/runtime/venv-web/bin/python"`.]
> [D-2b: A1-12 is a reviewed template whose one slot is instantiated, before
> the pass starts, from the digest-pinned `MI.target_fact_statement`. A1-12 is
> launched only if A1-11's admitted stdout equals that value.] No Pass A text
> is completed from a value that the pass itself produces.
>
> **Issue.** The operator issues them only through the one reviewed RP-11
> invocation for the pass, [M-9 = LB-2S]
> `/usr/bin/systemctl --no-ask-password start --wait rp11-capture-pass-a.service`,
> through the client's ordinary execution path. That invocation takes no
> operand. It causes only the reviewed entry to run. The entry's image and
> argv are fixed by root-installed bytes. Its environment is the literal that
> the root-installed static first image writes, and nothing from the client or
> the service manager's environment. Its other process state comes from the
> reviewed, root-configured service manager, not from the client.

*(R2)* The issue clause's bracket and last sentence changed from the R1 wording
(Appendix B), because the environment source changed. The invocation literal
did not. D-1's text, template, inspection and record clauses are unchanged.
>
> **Inspection.** The canonical guard policy — the pinned bytes of
> `guard-secrets.py` and `guard-git.py` — inspects each reviewed text
> **unchanged**, as a Bash command, inside the entry: once before X-1 and again
> immediately before that text's launch. For a Claude operator, the client
> hooks also inspect every reviewed text of the pass before the invocation
> starts. They run under the client's environment, so this is defense in depth.
> The entry does not rely on it, and no record claims it.
>
> **Execution and record.** The executed argv is the reviewed parse of the text,
> with `argv[0]` replaced by its pinned absolute path. The record carries the
> text, its digest and the argv (C-1). A refusal at any of these points is a
> §11.1 stop.

**If D-2 is declined, D-1 cannot carry its first sentence.** A1-12 then stays a
runtime instantiation (K-O), and no layer inspects its complete text before the
entry starts. The only truthful replacement is R-e (§6.6.2): a narrowly stated
amendment of the pre-start requirement for that one step.

**Without D-1, no option in this proposal is admissible, and C-11 stays open.**
That is the correct outcome if the maintainer declines D-1. D-1 does **not**
resolve Pass B (M-11).

### 5.4 Four representations: which layer inspects each, and when (*new, R4-D1-R1*)

**The representations.**

1. **Reviewed literal text (K-L).** A complete command text, fixed byte for
   byte in the draft and the pinned catalogue.
2. **Reviewed template.** A text with typed slots. **It is not a command.**
   Inspecting it is never described as inspecting its instantiation.
3. **Typed instantiation.** The template with each slot filled. A slot is
   either **K-R**, a reviewed value fixed before the pass (a maintainer input
   or a pinned statement), or **K-O**, a value the pass itself produces (an
   earlier act's admitted stdout, the clock, a human decision).
4. **Executed argv.** The reviewed parse of (1) or (3), with `argv[0]` mapped.

**Who inspects what, and when.** *Hook* means the client hook, which is Claude
only, runs under *E_c* and acts before the invocation's process starts. *Gate*
means the canonical policy in the entry.

| Representation | Hook | Gate before X-1 | Gate immediately before launch | Record |
|---|---|---|---|---|
| **K-L literal** | **yes**: the unchanged rules on the exact text, read from a catalogue file whose digest must equal the root-owned pinned value | **yes** | **yes**, the same text | text, text digest |
| **template** | the template text only. **Never described as inspecting the command** | the template only, as a well-formedness and refusal screen | — | template digest |
| **K-R instantiation** | only if the hook itself reads the digest-authenticated pre-bound value (D-2b) | **yes** | **yes** | text, text digest, template digest, slot source |
| **K-O instantiation** | **never**: the value does not exist yet | **never** | **yes, and this is the only inspection** | text, text digest, template digest, slot source record |
| **executed argv** | not inspected. Every guard inspects text, never argv | K-L: the parse equals the pinned tokens | the parse is redone and must equal the pinned tokens (K-L), or the template's tokens with the slot token substituted (instantiations) | argv |

**Consequences.**

* The assignment's criterion that *the client hook inspects the semantically
  complete command before any process or capture-root mutation* can hold only
  for K-L texts, and for K-R texts under D-2b.
* It **cannot** hold for a K-O text, by any design, because the value does not
  exist before the entry starts. The pre-launch gate is then the sole
  inspection of the complete text.
* Under **D-2a**, every Pass A text is K-L, and all three inspection points see
  the identical complete text.
* **Hook-to-gate equivalence** holds because the hook evaluates catalogue bytes
  whose digest equals the root-owned pinned value. The entry executes only
  bytes whose manifest digest equals the pinned value, and that manifest covers
  the same catalogue file. A catalogue swap between hook time and entry time is
  therefore refused by one side or the other. The hook, which runs under *E_c*,
  could be subverted to allow a text the gate then refuses. The reverse cannot
  happen: the gate never relies on the hook.
---

## 6. C-11 options

### 6.1 The four candidates

* **O-1: closed catalogue plus an in-process canonical gate.** The entry
  accepts a pass identifier only. Command texts come from a pinned catalogue.
  The hooks' own bytes, loaded by digest, evaluate every text before X-1 and
  before each launch. The client hooks are unchanged: they see only the
  invocation.
* **O-2 (conditional direction; amended R4-D1-R1): O-1 plus catalogue-resolving
  client hooks.** This is O-1 with one addition. Each hook recognises the one
  exact invocation (§4.4) and resolves it to the pass's catalogue, whose file
  digest must equal the root-owned pinned value. It then applies its unchanged
  rules to every **complete** catalogue text (K-L, and K-R under D-2b; §5.4).
  It also applies them to the literal invocation.

*O-1 and O-2 describe **what** is inspected. The launch boundary (LB-1, LB-2
or LB-3, §4.4) decides **whether the inspecting entry runs in a process that
ambient loader state never reached**. The reviewed bytes combined O-1 and O-2
with LB-0, which is the R4-D1-1 defect. Every row of §6.2 below now assumes an
M-9 boundary, and says so wherever the answer depends on it.* *(R2) Here and in
§6.3 and §6.5, "an M-9 boundary" means one that closes the entry's
environment: LB-2S or LB-1 (§4.4.5). The R1 LB-2 unit, LB-2T and LB-3 do not.*
* **O-3: an inspected prefix wrapper.** The operator issues
  `⟨entry⟩ -- rsync …`. The hook recognises the prefix and evaluates the tail.
  The entry receives shell-tokenised argv.
* **O-4: a hook-side rewrite.** The operator issues the plain §5 text. A
  third `PreToolUse` hook rewrites it (`updatedInput`) into a capture
  invocation after the guards allow it.

### 6.2 Assessment against the required criteria

| Criterion | O-1 | O-2 | O-3 | O-4 |
|---|---|---|---|---|
| **One canonical policy**, not drifting copies | **yes.** The gate executes the hook files' own bytes, digest-pinned | **yes**, and at both points | only if the hook's tail evaluation reuses the same function. The prefix grammar is new hook code | **no.** The rewrite hook is a second decision point, and its ordering relative to the guards is client-defined |
| **Client hook inspects the complete command** before any process or root mutation *(amended R4-D1-R1)* | **no.** It sees the invocation only. The in-process gate inspects the texts before any child process or X-1, but after the entry starts | **K-L texts only** (§5.4). **For Pass A under D-2a (or D-2b), yes, for every text.** Without D-2, A1-12's complete text is **not** inspected by the hook (only its template). **For Pass B, no** (M-11). The hooks run under *E_c*, so this is defense in depth (§4.3 T1) | **yes**, but it inspects a *changed* text: the prefix plus the tail | it inspects the plain text, **then executes something else** |
| **Can capture run an argv the direct path would refuse?** | **no.** There is no caller argv. Only catalogue texts run, each allowed by the canonical policy, and the parse must equal the pinned vector | **no**, as O-1 | **yes, unless combined with a catalogue**: any tail the guard allows can be run | depends on rewrite correctness. The executed form was never inspected |
| **Fail-closed**: malformed payload, unknown tool, policy-load failure, hook absence, version/digest mismatch, refusal *(amended R4-D1-R1)* | **only with an M-9 boundary.** Then yes, for everything the entry controls (§6.5), and hook absence does not weaken the entry's gate. **Under LB-0, no**: ambient loader state can alter every in-process check (R4-D1-1) | as O-1. The hook layer additionally refuses a malformed, near-match or unknown invocation, and a catalogue whose digest differs from the pinned value | partial. The prefix recognition is a new exemption surface | **no.** If the rewrite hook is absent, the plain text runs uncaptured. That fails open for evidence |
| **TOCTOU / substitution** *(amended R4-D1-R1)* | text, policy and catalogue are read once. The digest-verified bytes live in memory. There is no shell between the gate and `execve`. **Entry substitution is prevented only by the M-9 boundary** (§4.3) | as O-1. The hook verifies the catalogue digest against the root-owned pinned value. The entry verifies the manifest over the same file. A swap is refused on one side or the other (§5.4) | shell-tokenised argv arrives after the hook's inspection. Equivalence depends on `bash` matching the hook's model | the rewrite happens after inspection, which **is** a substitution |
| **Exact argv identity bound into the record** | **yes**: text, digest, entry identifier, pinned vector, policy digests (§6.8) | **yes** | yes (tokens) | no reliable binding |
| **Both guards, without an arbitrary wrapper exemption** | **yes.** No exemption exists, and both policies run on every text | **yes.** The hooks *add* an evaluation and never skip one | a narrow but real **wrapper exemption**, rejected by G-2 | not applicable |
| **Non-Claude agents** *(amended R4-D1-R1)* | **with an M-9 boundary:** the entry's gate runs in a process that ambient loader state never reached (§4.4.6). There is no client-side inspection. **Without M-9: none against ambient loader state** | as O-1. The hook layer adds only to Claude | hooks only. Non-Claude agents get whatever the entry checks | Claude-only. **Fails** G-9 |
| **Manifest coverage** | hooks, catalogue, gate, parser, both environment contracts, record schema, bootstrap, the entry's import closure and the boundary files of the chosen M-9 option (§11) | as O-1, plus `.claude/settings.json` | hooks and wrapper | hooks and settings |
| **Testable without secrets, a host or a sync** *(amended R4-D1-R1)* | the policy, catalogue, bootstrap and boundary-file **text**: yes (§10). **The M-9 prevention property itself: no.** It is a host property (§4.4) | as O-1 | yes | only inside a live client |
| **Needs D-1** *(amended R4-D1-R1)* | yes, the rewritten D-1, plus M-9 and D-2 | yes, the same | yes, plus a G-1/G-2 exception | yes, and it contradicts G-4 |

### 6.3 Disposition

* **O-3 is rejected.** It changes the command the guard inspects, and it
  needs a wrapper exemption that G-2 forbids. Without a catalogue it also lets
  capture run any guard-allowed tail.
* **O-4 is rejected.** It inspects one command and executes another, depends
  on client-specific ordering and output-rewriting semantics, and fails open
  when absent.
* **O-1 is viable only with an M-9 boundary.** It fails one criterion: the
  client hook does not inspect the semantically complete command.
* *(amended R4-D1-R1)* **O-2 is viable only with an M-9 boundary**, and it meets
  every §6.2 criterion **for Pass A** only under the rewritten D-1 and D-2.
  Without M-9, neither O-1 nor O-2 is fail-closed (R4-D1-1). Without D-2,
  O-2's pre-start criterion fails for A1-12 (R4-D1-2). For Pass B it fails as
  drafted (M-11).
* The reviewed bytes' statement *"O-2 is viable and meets every criterion in
  §6.2 under D-1"* is withdrawn (Appendix A).

### 6.4 The canonical policy — one implementation, two callers

**Refactor, specified here and implemented later.** Each hook file gains a
pure function whose rules are **byte-for-byte those of today's `main()`**:

```python
# .claude/hooks/guard-secrets.py
def evaluate(payload: Mapping[str, object]) -> Decision: ...

# .claude/hooks/guard-git.py
def evaluate(payload: Mapping[str, object], *, branch: str) -> Decision: ...
```

`Decision` is a frozen value: `allowed: bool` and `message: str`. Each `main()`
becomes a thin shell:

1. read stdin;
2. on a parse failure, exit 2;
3. `guard-git` only: `current_branch()`;
4. call `evaluate`;
5. print the message and exit 0 or 2.

`test_guards.py` keeps its 41 cases unchanged and adds the §5 text as an ALLOW
case (fixing F-1). It becomes 27 refuse and 15 allow, and `CLAUDE.md`'s figures
change with it.

**Loading, in the entry (`guard_gate.load_policy`):**

1. For each of the two paths, relative to the pinned repository root, read the
   whole file into memory **once**.
2. Compute its SHA-256 and compare it with the pinned digest, which is a
   covered-source digest in the reviewed manifest.
3. `compile(bytes, path, "exec")` and `exec` into a fresh dictionary with
   `__name__ = "rp11_policy_<name>"`, so the `__main__` block does not run.
   Then take `evaluate`.
4. Treat any exception, a missing attribute or a non-callable value as
   `guard-policy-unavailable`.

The file is never imported by module name, so there is no `sys.path` or cache
substitution.

**Branch independence (F-3).** The gate evaluates `guard-git` under
`branch ∈ {"main", "master", "⟨non-default⟩", ""}` and requires every result to
allow. A catalogue text is admissible only if its decision is the same in every
branch context. That makes the captured decision at least as strict as any
direct decision, and the gate never runs `git`.

**Payload construction.** The gate constructs exactly
`{"tool_name": "Bash", "tool_input": {"command": text}}`. No other tool name
and no other key is ever built. A catalogue entry whose kind is not `bash-text`
is refused as `guard-unknown-tool`.

### 6.5 Fail-closed matrix (O-2)

*Amended R4-D1-R1.* **Every row assumes an M-9 boundary.** Without one, every
row is a check that ambient loader state may already have altered (R4-D1-1),
and **none** of them is fail-closed. *(R2)* The M-9 boundary must be one that
closes the entry's environment: LB-2S or LB-1. Under the R1 LB-2 unit or LB-3,
root-configured manager or PAM variables can alter every row, so **none** is
fail-closed against that state either. Rows marked *diagnostic* detect a
condition after the process exists. They refuse before X-1, but they are never
described as preventing what they detect.

| Condition | Where detected | Result |
|---|---|---|
| malformed entry arguments, extra or unknown options | entry grammar (C-6) | `entry-malformed`. No X-1 |
| unknown pass identifier | catalogue lookup | `catalogue-unknown-pass`. No X-1. Also refused by the hooks at C-3 |
| pass configuration missing, not a regular file, not root-owned, group- or world-writable, or malformed *(R1)* | C-6 | `entry-pass-config-unavailable`. No X-1 |
| recomputed manifest digest ≠ the pass configuration's pinned digest | C-6 | `manifest-digest-mismatch`. No X-1 |
| an import of a repository module outside the verified set *(R1, F-6)* | C-6 import finder | `entry-import-unverified`. No X-1 |
| interpreter flags are not `isolated` and `no_site` (`-I -S`) | C-6 (`sys.flags`) | `entry-interpreter-flags`. No X-1. *Diagnostic* |
| *(R2, LB-2S)* `rp11-launch`'s argv is not exactly `--pass A`, or the block has no `INVOCATION_ID`, more than one, or one that is not 32 lowercase hex digits | `rp11-launch`, before any `execve` (§4.4.3.4) | the image exits with a fixed status. **No entry process exists.** The unit fails, and the pass stops under §11.1 |
| *(R1; amended R2, LB-2S)* `INVOCATION_ID` absent, or the parent process is not PID 1 | C-6 | `entry-boundary-absent`. No X-1. *Diagnostic.* It catches the honest error of starting the bootstrap directly from a shell. It is not a proof of provenance |
| *(R1; amended R2, LB-2S)* the installed unit's bytes ≠ the pass configuration's unit digest | C-6, reading `/etc/systemd/system/rp11-capture-pass-a.service` | `entry-unit-mismatch`. No X-1. *Diagnostic*: the unit has already run. *(R2)* The loaded configuration can differ from the installed file (S-5). H-2, not this row, reviews it |
| *(R2, LB-2S)* the installed `rp11-launch` bytes ≠ the pass configuration's `launcher_sha256` | C-6, reading the installed image | `entry-launcher-mismatch`. No X-1. *Diagnostic*: the image has already run |
| *(R1; amended R2)* the entry's own environment ≠ `rp11-entry-env/1` (§7.9) | C-6 | `entry-environment-unexpected`. No X-1. *Diagnostic.* It replaces the reviewed bytes' `entry-loader-variable`, which was described as a refusal protecting the boundary. That description is withdrawn. *(R2)* Under LB-2S a difference means `rp11-launch` did not perform the entry's `execve`. The check still proves nothing about what a loader consumed |
| hook file missing, unreadable, digest ≠ pin, compile error, no `evaluate` | C-7 | `guard-policy-unavailable`. No X-1 |
| a hook not registered, or not run, in the client | not detectable in-process | *(amended R4-D1-R1)* **with an M-9 boundary**, the entry's gate is unaffected: C-9 and C-11 still run in a process ambient loader state never reached. Client-side pre-start inspection is then simply absent (§4.4.6). **Without M-9**, the reviewed bytes' *"no effect on enforcement"* is untrue and is withdrawn |
| `settings.json` bytes ≠ pin | C-6 (covered source) | `manifest-digest-mismatch` |
| any catalogue text refused under any branch context | C-9 | `guard-refused` with the entry identifier. **§11.1 stop before X-1**. The refusal message is recorded in the stopped-pass handback |
| a text refused at a per-act re-evaluation (should be unreachable) | C-11 | `guard-refused`, act not launched, §9.5.3 stop transition (one X-3) |
| a parse error, or tokens ≠ pinned vector | C-11 | `argv-parse-mismatch`, act not launched, stop transition |
| `evaluate` raises or returns anything but a `Decision` | C-9 / C-11 | `guard-policy-unavailable`, stop |
| environment refusal (§7.7) | C-8 | `environment-*`. No X-1 |
| a hook-side catalogue load failure, or a catalogue file digest ≠ the pinned value *(R1)* | C-3 | the hook refuses the invocation (exit 2) |
| *(R1)* the invocation is refused by polkit, the system bus is unreachable, or `sudo` cannot elevate | C-4 | no entry process exists. The pass stops under §11.1, and nothing is reissued in another form |

**Refusal is never followed by a reshaped attempt.** The entry has no flag,
environment variable or argument that disables, weakens or skips the gate.

### 6.6 The act catalogue

A new covered module, `tools/phase_5_0_evidence/execution/act_catalogue.py`,
holds a tuple of frozen entries per pass. Each entry has these fields:

| Field | Type and rule |
|---|---|
| `entry_id` | the draft step identifier, e.g. `A1-00`, `A1-01` |
| `kind` | `bash-text` only |
| `command_text` | the exact reviewed text as a `str`, ASCII only. For `A1-00` it is the OB-1 block: 381 bytes, no trailing newline, SHA-256 `4b4096d7…9cc` |
| `command_text_sha256` | pinned. A test recomputes it |
| `tokens` | the pinned token vector (`("rsync", "-avz", "--delete", "--include=.env.example", …)`) |
| `program` | `rsync` or `ssh`. It must equal `tokens[0]` |
| `parameters` | empty, or typed slots (below). *(R1)* Under D-2a, empty for every Pass A entry |
| `enabled_by` | always, or a named maintainer flag (A1-C steps; A1-D steps under AUTH-DBREAD) |

**Parameterised entries** *(amended R4-D1-R1)*. The reviewed bytes made A1-12
a runtime substitution of A1-11's stdout. They then described its text as
fixed in the catalogue and inspected by the hook before start. That
contradiction is R4-D1-2.

* **Under D-2a** (§6.6.2), Pass A has **no parameterised entry**, and every
  `parameters` field is empty. The slot machinery is not built for Pass A.
* **Under D-2b,** A1-12 has one **K-R** slot, filled from the digest-pinned
  statement before the entry starts.
* **Under R-e,** A1-12 keeps one **K-O** slot, filled from A1-11's admitted
  stdout. It is validated against a grammar: an absolute normalised path of
  `[A-Za-z0-9._/-]`, at most 4096 bytes, with no `..` segment. It is
  substituted before the pre-launch evaluation and parse, and it is **never**
  described as inspected before start.

**Drift tests** bind the catalogue to the documents. `A1-00`'s text must equal
the fenced block of draft §5 **and** disposable-test-server §3.2. Each A1 entry
must equal the draft's table cell after Markdown code-span unescaping. A draft
change therefore fails the suite rather than silently diverging.

*(R1)* A1-32's cell is not a complete text (*"the same, with `--command …`"*).
Its catalogue text is A1-31's text with that one operand replaced, and its
drift test asserts exactly that derivation.

#### 6.6.1 When each entry's final text and argv first become knowable (*new, R4-D1-R1*)

**Classes.**

* **K-L:** complete when the draft is reviewed.
* **K-R:** complete once a reviewed pre-pass value exists (`PIN.*`, `MI.*`, an
  `RP-x` reviewed value, the pinned statement), which is before the entry
  starts.
* **K-O:** complete only after something inside the pass has happened: an
  earlier act's output, the clock at issue, or a human decision.
* **K-U:** no text exists, because the input is unresolved.

**Two things never change a text.** *Enablement* (A1-C only if A0-09
referenced the statement; A1-D only under AUTH-DBREAD) is fixed by the
authorization before the pass. *Runtime stop predicates* (for example, A1-19
must exit `1`) decide whether the pass continues.

**Pass A** (the scope of this decision, M-11):

| Entry | Final text and argv first knowable | Class | Enabled by |
|---|---|---|---|
| A1-00 (§5 `rsync`) | at review | K-L | AUTH-SYNC |
| A1-S1, A1-S2 | at review | K-L | always |
| A1-01 … A1-10 | at review | K-L | always |
| A1-11 | at review | K-L | A1-C |
| **A1-12, as drafted** | **only after A1-11's record is admitted, inside the running session** | **K-O** | A1-C |
| A1-12 under **D-2a** | at review | K-L | A1-C |
| A1-12 under **D-2b** | when the statement is pinned, before the pass | K-R | A1-C |
| A1-13, A1-16, A1-17, A1-18 | at review | K-L | always |
| A1-14, A1-15 | at review | K-L | A1-C |
| A1-19 … A1-22, A1-24 | at review | K-L | always |
| A1-23a … A1-23g: four `getent group` and three `getent passwd` calls, one call each | at review | K-L | always |
| A1-25 … A1-28 | at review | K-L | always |
| A1-29 … A1-31, A1-33 | at review | K-L | AUTH-DBREAD |
| A1-32 (derived from A1-31, above) | at review | K-L | AUTH-DBREAD |
| A1-Z: repeats of A1-19, A1-21 … A1-24 and, under AUTH-DBREAD, A1-29 … A1-33, each as its own entry | at review | K-L | as the original step |

**Pass B** (listed to show why it is out of scope; OB-15, F-4):

| Entry | Class | Why |
|---|---|---|
| B1: §5 and A1 repeats | K-L | only the expected values change |
| B1-V7 `⟨MI.producer_argv.v7_init⟩` | K-U | no producer exists |
| **B2 harness invocation** | K-R for `⟨PIN.*⟩` and `⟨MI.*⟩`; **K-O** for `⟨OP.at⟩` (*"the client UTC time at issue"*), for `⟨OP.requested_at⟩` (its source is not fixed by the draft) and for the three quiescence flags (present *"only if B1-Q observed each condition"*, which depends on A1-25 … A1-28's output) | **the pre-start criterion is unsatisfiable as drafted.** A value defined as the time at issue cannot exist before the entry starts |
| B4a, B4b, B6.1a, B6.9 | K-U | `⟨MI.producer_argv.*⟩`, `⟨RP-3.*⟩` and `⟨RP-12.*⟩` are unresolved |
| B6.1b | K-U until RP-5 exists, then K-R | `⟨RP-5.*⟩` paths |
| B6.3 | **not a command**: a live human gate *after* B6.1 is reported | a per-pass entry with no control channel cannot receive it (F-4) |
| B6.5 | K-L text; **the repetition count is K-O** | it depends on the connection outcome |
| B6.1c, B6.4, B6.6 … B6.8 | K-L | — |
| B7 (the §13.2 survey) | not classified here | §13.2 was not read for this amendment. It is classified in the Pass B draft amendment |

**Who inspects what, and when.** The rule is §5.4, applied:

* **Pass A under D-2a.** Every text is K-L. The hook (Claude, defense in
  depth), the gate before X-1 and the gate before each launch inspect the
  identical complete text.
* **Pass A as drafted, or under R-e.** A1-12's complete text is inspected
  **only** by the gate immediately before its launch.
* **Pass B.** B2's complete text can be inspected only before its launch, never
  before the entry starts.

#### 6.6.2 Remedies for A1-12 (*new, R4-D1-R1*)

**The key fact (OB-14).** The draft stops the pass whenever A1-11's value
differs from the pinned statement (§4.6, §4.7(4)). So in **every** execution
that reaches A1-12, the value A1-12 would substitute is already known before
the pass: it is the statement's value.

The remedies:

* **D-2a: eliminate substitution with a reviewed literal.** A1-12 becomes
  `ssh oracle-test "sha256sum /opt/freedom-blades/runtime/venv-web/bin/python"`.
  `sha256sum` follows the link (AS-9, PO-7), so it hashes the file the venv
  entry resolves to. A1-11 still records the real path, and both are compared
  with the statement. `OP.interpreter_sha256` (draft §4.6) is redefined as
  *the digest of the file the venv entry resolves to when A1-12 runs*.
  *Optional D-2a+:* a literal repeat of A1-11 after A1-12 (A1-12b) brackets the
  window between them, and any difference stops the pass.
* **D-2b: instantiate from the pinned statement.** A1-12 stays
  `ssh oracle-test "sha256sum ⟨path⟩"`, with `⟨path⟩` taken from the
  digest-pinned `MI.target_fact_statement` before the entry starts. The entry
  launches A1-12 only if A1-11's admitted stdout equals that value followed by a
  newline. By OB-14 the pass would otherwise already have stopped. **So the
  executed text is byte-identical to the draft's in every execution that
  reaches A1-12.**
* **R-c: a separately inspected invocation.** A second client call carries the
  value into the running session over a control channel.
* **R-d: change the session granularity.** End the session after A1-11 and
  start a new one for A1-12 onward.
* **R-e: a narrow amendment of the requirement.** A1-12 stays K-O, and the
  pre-start criterion is amended for that one step.

| Against | D-2a | D-2b | R-c | R-d | R-e |
|---|---|---|---|---|---|
| **complete text inspected by the hook before start** | **yes** | yes, **if** the hook reads and authenticates the statement | no. It is inspected before that step, but after the entry and X-1 | no. It is inspected before the second session, after the first root was created | **no**, by definition |
| **retained root and session lifecycle** (F-2, C-6, C-8, C-14) | unchanged | unchanged | a control channel into the live session: a new IPC trust boundary, which under LB-2 crosses from a client process under *E_c* into the unit | **breaks one root per pass**: two roots and two index chains, or a root reopened (unsupported) | unchanged |
| **exact stream capture** | unchanged | unchanged | unchanged | split across two roots | unchanged |
| **stop transition** (§9.5.3) | unchanged. A K-L refusal happens before X-1 | unchanged. The predicate "A1-11 ≠ statement" is the existing §4.6 stop | a missing or late request needs a new stop case | a stop between sessions needs a new definition | **a guard refusal can now occur after X-1**, because `guard-git.py`'s decision can depend on the value (OB-12). It becomes a mid-pass stop transition |
| **command-text/argv record** (§6.8) | literal fields only | adds a template digest and the slot source (the statement's digest) | adds a template digest and the request provenance | spread over two roots | adds a template digest and the slot source record |
| **canonical guard decision** | fixed at review, repeated before X-1 and before launch | fixed before X-1, on the instantiation | only before launch | before the second session | **only before launch** |
| **caller-supplied argv or value** | none | none | **the operator transcribes the value**: caller-supplied, bounded by the grammar and by equality with A1-11 | as R-c, or reduces to D-2b | none |
| **new machinery** | none; the slot machinery is removed from Pass A | slot machinery; the hook reads and parses the statement, **whose format does not exist yet** (RP-10) | IPC, authentication of requests, a session state machine | a lifecycle redesign | slot machinery |
| **draft amendment** | A1-12 row text and the §4.6 definition (D-2) | the A1-12 row wording (D-2) | substantial | substantial | the pre-start criterion (the named exception) |

**Disposition.**

* **R-c and R-d are rejected.** They satisfy the criterion no better than
  D-2b, and they break the lifecycle or introduce a caller-supplied value.
* **D-2a is the conditional direction.** It is the only remedy that makes
  every Pass A text a reviewed literal with no new machinery and no dependency
  on the unwritten statement format.
* **D-2b is the alternative** if the maintainer requires A1-12's text to keep
  hashing the real path by name. Its semantics are exactly the draft's
  whenever A1-12 runs.
* **R-e is the fallback** if D-2 is declined. It must be adopted as an explicit
  requirement amendment, with this replacement property:

  > the executed A1-12 text is exactly the reviewed template instantiated with
  > A1-11's admitted stdout, validated against the slot grammar and allowed by
  > the canonical policy under every branch context, in the M-9-protected entry,
  > immediately before its launch. The client hook inspects only the template and
  > is never described as inspecting A1-12's command.

### 6.7 The reviewed parse (C-1 both forms)

This is a new pure function, `act_catalogue.parse_reviewed_text(text) -> tuple[str, ...]`.
It accepts a strict subset of POSIX shell word syntax, the subset that the
secrets hook and the draft's texts use, and refuses everything else.

* **Blanks.** Space and tab separate words.
* **Continuation.** Backslash-newline outside quotes is removed first, as
  `guard-secrets.py` does.
* **Single quotes.** A single-quoted span is literal.
* **Double quotes.** Inside a double-quoted span, only `\"`, `\\`, `\$` and
  `` \` `` are escapes, as in `A1-17`'s `\${Package}`. Any **unescaped** `$` or
  backtick is refused. Any other backslash is kept literally, as in `bash`.
* **Unquoted characters.** Refused when unquoted: `` | & ; < > ( ) $ ` # ``,
  `* ? [ ] { } ~ !`, a backslash that is not a continuation, a newline or
  carriage return that is not a continuation, and any non-ASCII byte.
* **Result.** Adjacent quoted and unquoted parts of one word concatenate.
  Empty words are refused.

**Equivalence proof obligation (PO-5).** For every catalogue text, a test
compares `parse_reviewed_text(text)` with the tokenisation `bash --noprofile
--norc` produces. The oracle replaces the leading program word with
`printf '%s\0'` and runs **no** `rsync` or `ssh`. Every text satisfies the
grammar, so no expansion can occur in the oracle.

**`argv[0]` mapping.** `program → absolute path` is a fixed reviewed literal:
`rsync → /usr/bin/rsync` and `ssh → /usr/bin/ssh` (decision M-5). The executed
vector is `(pinned_path,) + tokens[1:]`. Before X-1 the entry checks each path
with `lstat`. It must be a regular file (not a symlink), owned by uid 0, not
group- or world-writable, and each parent directory up to `/` must be root-owned
and not group- or world-writable. Failure is `executable-check-failed`. Whether
to also pin the binaries' SHA-256 is decision M-5(b).

### 6.8 What the per-act record binds

`CaptureRecord` (the schema change comes later) gains these fields, all
validated in `__post_init__`:

| Field | Content |
|---|---|
| `catalogue_entry_id` | e.g. `A1-00` |
| `command_text` | the exact reviewed text (C-1 "as issued"). It is not secret: it is reviewed repository text |
| `command_text_sha256` | its digest. For a K-L entry it must equal the catalogue pin. *(R1)* For an instantiation, it is the digest of the instantiated text |
| `text_class` *(R1)* | `literal` or `instantiated`. Under D-2a, every Pass A record is `literal` |
| `template_sha256` *(R1)* | instantiations only: the reviewed template's pinned digest |
| `slot_bindings` *(R1)* | instantiations only: for each slot, its name, its class (`K-R` or `K-O`), its source (the statement's digest for K-R, or the index of the admitted source record for K-O) and the SHA-256 of its value |
| `inspections` *(R1)* | the inspection points **the entry itself performed**: `admission` (before X-1, K-L and K-R only) and `pre_launch`. **The client hook is never listed**: the entry cannot observe whether it ran, and no record claims it |
| `argv` | the executed vector, already present (C-1 "received") |
| `argv0_token` | `rsync` or `ssh`: the word the text named |
| `guard_policy` | `{"guard-secrets.py": <sha256>, "guard-git.py": <sha256>}`: the bytes that allowed it |
| `guard_contexts` | the branch contexts evaluated, in fixed order |
| `environment_contract` | `rp11-launcher-env/1` |
| `environment_sha256` | the digest of the canonical serialisation of the exact map (§7.8). **No key or value is recorded** |

The genesis state also records the manifest digest the entry verified. That
lets every record be traced to the reviewed bytes of the hooks, the catalogue
and the environment contract.

*(R1)* The genesis state additionally records:

* `launch_boundary`: the M-9 option, for example `LB-2S`;
* `invocation_id`: under LB-2S, the unit's `INVOCATION_ID` as copied by
  `rp11-launch`. It is diagnostic provenance only, because a unit drop-in could
  override it (§4.4.3.4);
* `launcher_sha256` *(R2)*: the pass configuration's pinned digest of
  `rp11-launch`;
* `pass_config_sha256`: the root-owned pass configuration's digest;
* `bootstrap_sha256`;
* `entry_environment_contract`: `rp11-entry-env/1`; and
* `entry_environment_sha256`: the digest of the entry's own environment
  (§7.9). No key or value is recorded.

### 6.9 Residual risks of O-2, stated plainly

* **R-1. The client-hook layer can be sidestepped** *(amended R4-D1-R1)*. An
  operator can invoke something the hooks do not recognise, and the hooks
  themselves run under *E_c* (§4.3 T1). **With an M-9 boundary,** the entry's
  image and argv are fixed by root-owned bytes, so a disguised invocation can
  only fail to start the entry. It cannot start a different one. The in-process
  gate still runs in a process ambient loader state never reached, and it is
  the enforcement. **Without M-9,** a disguised or preloaded invocation defeats
  both layers. That is R4-D1-1, and it is not a residual risk.
* **R-2. The executables are trusted.** `/usr/bin/rsync` and `/usr/bin/ssh`
  are trusted as root-owned system binaries. The direct path trusts them the
  same way. M-5(b) optionally pins their digests.
* **R-3. The `ssh` configuration and `known_hosts` sit outside the manifest.**
  They affect behaviour and are not pinned by this design (M-3, M-4).
* **R-4. *Withdrawn R4-D1-R1.*** The reviewed text (Appendix A) treated a
  name check inside the entry as a refusal that protects against loader
  variables. That is not a residual risk; it is the R4-D1-1 defect. It is
  replaced by the M-9 boundary (§4.4), which prevents them. The name check
  survives only as the diagnostic `entry-environment-unexpected` (§7.9).
* **R-6** *(new)*. **The client-hook layer and the client shell run under
  *E_c* under every option** (§4.3 T1, T2). The same holds for the direct path
  (F-5). This is a property of the baseline and is stated in D-1. M-13 narrows
  T1's Python inputs but does not prevent loader inputs.
* **R-7** *(new)*. **Same-account forgery (T-B).** Anything running as the
  operator's account can write files under the capture root after, or instead
  of, the entry. No option prevents that (M-10). LB-2S's `INVOCATION_ID` and the
  journal's trusted fields are provenance evidence only.
* **R-8** *(new, LB-2; amended R2)*. **Root-owned system state is trusted:**
  PID 1 and its boot environment, the executor (AS-13), polkit,
  `/etc/ld.so.preload`, `ld.so.cache`, the standard library and
  `/usr/bin/python3.12`, in the same way as R-2. The entry's diagnostic checks
  detect some misconfiguration of that state (§6.5). They do not make it
  untrusted-safe. *(R2)* **"The manager's environment" is removed from this
  list** (Appendix B). It is ambient T-A state (§4.3). Under LB-2S it is
  neither trusted nor needed, because it reaches only `rp11-launch`, which
  ignores it.
* **R-10** *(new R2, LB-2S)*. **Manager execution settings are trusted root
  input, reviewed and not prevented.** No unit text can exclude them (S-5):
  * the manager's `Default*=` values;
  * top-level `service.d/` and unit drop-ins;
  * run-time properties; and
  * unit-path precedence.

  They shape the entry's limits and confinement and, at worst, the loaded
  `ExecStart=`. H-1 and H-2 review and bind them, but S-7 lets them change
  afterwards. The entry diagnoses some effects, such as its parent PID, its
  environment and the installed unit and launcher digests. It does not prevent
  them. **This trust is only admissible if M-10 accepts it explicitly.** It is
  stated here so that it is not mistaken for prevention.
* **R-11** *(new R2, LB-2S)*. **Two load-bearing proof obligations, not
  residual risks.** If either fails, LB-2S is withdrawn:
  * **PO-9**: the static image's start-up reads no environment; and
  * **PO-14**: the installed systemd does not load its executor under the
    unit's block.

  They are listed here only so that nobody reads them as accepted risk.
* **R-9** *(new)*. **A0-05 and A0-06 run under *E_c*.** The dry-run digest
  check and the local classifier tests of Band A0 run through the ordinary
  client path, outside RP-11, and are exposed to the same ambient state. They
  are admission steps, not capture, and this amendment does not change them.
  Codex should judge whether that exposure matters for the admission result.

---

## 7. The launcher-environment contract, `rp11-launcher-env/1`

### 7.1 Principle

* **One closed map.** A single map is built once per session by
  `launcher_environment.build(authorization)`. It is supplied unchanged to
  every `rsync` act and every `ssh` act.
* **Never read from the entry's environment.** The builder does not read
  `os.environ`, and a structural test enforces that.
* **One contract for both programs.** `rsync` passes its environment to its
  child `ssh` (AS-3, PO-2). A separate `ssh` map that differed would therefore
  describe a state that never occurs for `A1-00`. The contract states the
  `rsync` set and the `ssh` set separately below, and they are **equal by
  construction and by test**.

### 7.2 Variable matrix

Dispositions:

* **L**: fixed reviewed literal.
* **M**: typed maintainer input, digest-bound and validated before X-1.
* **A**: deliberately absent. The builder never supplies it, and a request to
  include it is `environment-unexpected-key`.
* **P**: prohibited. It is named because its presence would alter
  authentication, the transfer or the executed program, and a request to
  include it is `environment-prohibited-key`.

In practice A and P are both absent. They differ in their refusal class and in
the documented reason.

| Variable | `rsync` | `ssh` | Value / reason |
|---|---|---|---|
| `PATH` | **L** | **L** | `/usr/bin`, exactly. `rsync` finds its child `ssh` only here, so that child is `/usr/bin/ssh`, the same as the pinned `ssh` path. `ssh` itself execs nothing by `PATH` without `ProxyCommand`, `LocalCommand` or askpass (see M-4) |
| `LC_ALL` | **L** | **L** | `C`. POSIX guarantees it exists, it gives deterministic, byte-oriented output (non-ASCII names in `rsync -v` are escaped), and it overrides every `LC_*` and `LANG`. It may be offered to the remote host through `SendEnv` (AS-5, §7.6) |
| `SSH_AUTH_SOCK` | **M** or **P** | **M** or **P** | **M** only under M-1 = agent (§7.4); otherwise **P** |
| `HOME` | **A** | **A** | not needed, on AS-2. OpenSSH locates `~/.ssh/*` through the password database. Absence also removes `$HOME`-based lookups by `rsync`'s option parser, if any (AS-4, PO-3). See §7.5 |
| `LANG`, `LANGUAGE`, `LC_CTYPE`, `LC_MESSAGES`, other `LC_*` | **A** | **A** | `LC_ALL` supersedes them. Their absence stops them from being offered by `SendEnv` |
| `TERM`, `COLUMNS`, `LINES` | **A** | **A** | no pty is requested: no `-t`, `stdin` is `/dev/null`. `TERM` is sent only with a pty |
| `SHELL` | **A** | **A** | used by `ssh` only to run `ProxyCommand`/`LocalCommand`, with a fallback to `/bin/sh`. M-4 requires that neither is configured |
| `USER`, `LOGNAME` | **A** | **A** | `ssh` takes the local user from the password database. The remote user comes from `User ubuntu` in the configuration |
| `TZ` | **A** | **A** | neither program prints times for these acts. Record times come from the entry's UTC clock |
| `TMPDIR` | **A** | **A** | the sending `rsync` creates no local temporary file. The receiver's temporary files are remote |
| `PWD`, `OLDPWD` | **A** | **A** | the working directory is `/`. All local paths in the texts are absolute |
| `RSYNC_RSH` | **P** | — | would replace the remote shell. The direct path does not set it, and the §5 argv has no `-e` |
| `RSYNC_PROXY`, `RSYNC_CONNECT_PROG`, `RSYNC_PASSWORD` | **P** | — | daemon or proxy transport and daemon credentials; not this transfer |
| `RSYNC_PROTECT_ARGS`, `RSYNC_OLD_ARGS` | **P** | — | change how the argv is sent to the remote side |
| `RSYNC_ICONV`, `RSYNC_CHECKSUM_LIST`, `RSYNC_COMPRESS_LIST`, `RSYNC_MAX_ALLOC`, `RSYNC_PARTIAL_DIR` | **P** | — | change negotiation, encoding or behaviour outside the reviewed argv |
| `CVSIGNORE` | **P** | — | a filter input, if `-C` were ever present |
| `SSH_ASKPASS`, `SSH_ASKPASS_REQUIRE`, `DISPLAY`, `XAUTHORITY` | **P** | **P** | would enable a credential prompt program. Without them, a key that needs a passphrase fails closed (`stdin` is `/dev/null`, there is no tty) |
| `SSH_AGENT_PID` | **P** | **P** | not used by the client. Its presence would signal ambient agent state |
| `SSH_SK_PROVIDER` | **P** | **P** | security-key middleware: an authentication input |
| `KRB5CCNAME`, `KRB5_CONFIG`, `KRB5_KTNAME` | **P** | **P** | GSSAPI authentication input. A new design is needed if it is ever wanted |
| `SSH_CONFIG` | **P** | **P** | not an OpenSSH variable (configuration is `-F`, which the argv does not carry). It is prohibited so that nobody mistakes it for a pin |
| `SSH_CONNECTION`, `SSH_CLIENT`, `SSH_TTY`, `SSH_ORIGINAL_COMMAND` | **P** | **P** | ambient state of an operator who is logged in over SSH |
| `http_proxy`, `https_proxy`, `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `all_proxy`, `NO_PROXY`, `no_proxy`, `ftp_proxy` | **P** | **P** | not used by either program. They are prohibited so that no configured tunnel is implied |
| `LD_PRELOAD`, `LD_LIBRARY_PATH`, `LD_AUDIT`, any `LD_*`, `GLIBC_TUNABLES`, `MALLOC_*` | **P** | **P** | would alter the loaded program. *(amended R4-D1-R1)* The closed map already keeps them away from the children. For the entry process itself, the reviewed bytes' *"prohibited-loader set … (R-4)"* is withdrawn. The entry's own environment is governed by §7.9 and the M-9 boundary |
| `IFS`, `ENV`, `BASH_ENV`, `CDPATH`, `PS4`, `SHELLOPTS`, `BASHOPTS` | **P** | **P** | shell startup and parsing inputs. No shell runs, but `SHELL`-run commands would read them |
| `PYTHON*` | **P** | **P** | irrelevant to both programs. They are prohibited so that the map cannot carry the entry's own configuration |
| any other name | **A** (unexpected) | **A** (unexpected) | the contract is closed |

**Resulting key sets:**

* **Key-file mode:** `rsync` = `ssh` = `{LC_ALL, PATH}`.
* **Agent mode:** `rsync` = `ssh` = `{LC_ALL, PATH, SSH_AUTH_SOCK}`.

### 7.3 Grammar and limits

| Key | Grammar (Python `re.fullmatch`, ASCII) | Maximum bytes |
|---|---|---|
| key names, generally | `[A-Z_][A-Z0-9_]{0,31}` (lowercase proxy names are matched only to refuse them) | 32 |
| `PATH` | exactly `/usr/bin` | 8 |
| `LC_ALL` | exactly `C` | 1 |
| `SSH_AUTH_SOCK` | `/(?:[A-Za-z0-9._-]+/)*[A-Za-z0-9._-]+`, with no segment equal to `.` or `..`, no `//` and no trailing `/` | 107, the Linux `sun_path` size of 108 less its NUL |

**Structural refusals.** These apply to the authorization's input, which is a
**sequence of `(key, value)` pairs** and not a mapping, so a duplicate can be
detected:

* a duplicate key;
* an empty key or value;
* NUL anywhere;
* `=` in a key;
* `=` in a value, which no grammar above permits;
* a non-ASCII byte;
* a key outside the mode's key set; and
* a value that fails its grammar or length.

The launcher's own check (OB-6) stays in place underneath as a second layer.

### 7.4 Authentication — decision M-1 (the repository does not establish it)

OB-9 establishes key-based access through `IdentityFile ~/.ssh/id_ed25519`. It
does **not** establish whether that key is used directly or through an agent,
and this proposal does not guess.

| Option | Contract | Works with this environment? | Consequences |
|---|---|---|---|
| **M-1a, key file only** | `SSH_AUTH_SOCK` **P** | yes, **if** the key file is usable without a passphrase. `ssh` reads it itself, and neither the operator nor the entry reads it | if the key needs a passphrase, `ssh` cannot prompt: there is no tty, `stdin` is `/dev/null` and askpass is prohibited. `A1-00` exits 255 before any transfer, which is a §11.1/§11.2 stop that consumes Pass A. It fails closed, but at the cost of the pass. There is no ambient state and no dynamic input |
| **M-1b, agent at a maintainer-fixed socket** | `SSH_AUTH_SOCK` **M** | yes, if the maintainer runs an agent bound to a path of their choosing, for example with `ssh-agent -a ⟨path⟩`, holding the key before the pass | the value is **supplied by the maintainer** in the A-2 authorization as `MI.ssh_auth_sock`, never read from the operator's environment. It must be printed nowhere. Before X-1 the entry runs `lstat` only, with **no connect**: a socket (`S_ISSOCK`), owned by the operator's uid, whose parent directory is owned by that uid with mode `0700` and no group or other bits, and not a symlink at any component. There is no key listing and no agent query |
| M-1c, the ambient agent socket, digest-checked | — | — | **rejected.** It is inherited state even when verified against a digest, and establishing the value would require printing the environment (§12) |
| M-1d, GSSAPI, a security key or another mechanism | — | — | out of scope. It needs a new design |

**Binding without content.** Under M-1b, the authorization carries
`MI.ssh_auth_sock` and `MI.ssh_auth_sock_sha256`, the SHA-256 of the UTF-8
value. The builder refuses if they disagree (`environment-binding-mismatch`).
Records carry only `environment_sha256` over the whole map (§7.8), and
handbacks carry no environment (C-9). The socket path is not a secret, but it
is treated as authentication state, and no refusal message ever echoes it.

**Socket TOCTOU.** The socket could be replaced between the `lstat` check and
`ssh`'s connect. A parent directory owned by the operator with mode `0700`
limits replacement to the operator's own uid, which the direct path trusts
equally. This is stated as residual R-5.

### 7.5 `HOME`, configuration and `known_hosts` — relied on, not read

On AS-2, `ssh` locates the following through the password database, whatever
`HOME` says:

* the user configuration `~/.ssh/config`, which holds the `oracle-test`
  alias, `HostName`, `User`, `IdentityFile` and `StrictHostKeyChecking
  accept-new` (OB-9);
* `~/.ssh/known_hosts` (and `known_hosts2`); and
* the identity file named in the configuration.

It also reads `/etc/ssh/ssh_config`, `/etc/ssh/ssh_config.d/*.conf` and
`/etc/ssh/ssh_known_hosts`.

**None of these was read for this proposal (G-6).** All of them sit outside the
manifest. So `HOME` is **A**. If PO-1 finds that the installed `ssh` honours
`HOME`, the contract must change to `HOME` = **M** (the operator's home as a
typed, maintainer-stated absolute path) and be re-reviewed. The fix is not to
inherit `HOME`.

**`accept-new` is a material concern (M-3).** If `oracle-test`'s key is absent
from the known-hosts files, the first connection **trusts on first use and
writes** `known_hosts` on the repository host, silently. A changed key is
refused, which B6 relies on. The environment cannot change this: `ssh` options
live in the configuration or the argv, and both are fixed. See M-3 for the
options.

**Effective-configuration pin (M-4).** `ssh -G oracle-test` prints the
effective client configuration without connecting and without reading key
material. Run under the closed map, its output (for example `hostname`, `user`,
`identityfile`, `stricthostkeychecking`, `sendenv`, `proxycommand`,
`localcommand`) could be digest-compared, at admission, with a maintainer-pinned
digest. That is an inspection of host authentication configuration, so it
**needs its own later authorization**. It is proposed and not performed here.

### 7.6 Locale and the remote side

`LC_ALL=C` governs the local programs. Whether the remote shell inherits it
depends on the client's `SendEnv` and the remote `sshd`'s `AcceptEnv`, and
neither is inspected. The draft's A1 expected values are ASCII tokens (`Test`,
`x86_64`, `fs.protected_hardlinks = 1` and so on). The contract claims **no**
control over the remote locale. If Codex judges that A1 comparisons need it,
that belongs in the A1 texts, which is a draft amendment and not an
environment change.

### 7.7 Operator-facing refusal classifications

Each refusal happens before X-1 unless noted otherwise. A message names the
class and, where safe, the key name. **No message contains a value.**

| Class | Trigger |
|---|---|
| `environment-contract-unavailable` | the contract module is missing or its digest does not match |
| `environment-mode-unknown` | M-1 mode is not `key-file` or `agent` |
| `environment-duplicate-key` | the same key appears twice in the input sequence |
| `environment-empty` | an empty key or value |
| `environment-nul` | NUL in a key or value |
| `environment-key-equals` | `=` in a key |
| `environment-non-ascii` | a non-ASCII byte |
| `environment-unexpected-key` | a key not in the mode's set and not in the prohibited set. The key name is echoed only if it matches the key grammar, otherwise `⟨malformed⟩` |
| `environment-prohibited-key` | a key in the §7.2 **P** set |
| `environment-missing-key` | agent mode without `SSH_AUTH_SOCK` |
| `environment-literal-mismatch` | `PATH` or `LC_ALL` ≠ its literal |
| `environment-value-grammar` | a value fails its grammar or length |
| `environment-binding-mismatch` | the digest of `MI.ssh_auth_sock` ≠ `MI.ssh_auth_sock_sha256` |
| `environment-socket-check-failed` | an M-1b `lstat` condition fails. The failing condition is named, never the path |
| ~~`entry-loader-variable`~~ | *withdrawn R4-D1-R1* (Appendix A). It was a post-start name check described as a refusal. It is replaced by `entry-environment-unexpected` |
| `entry-environment-unexpected` *(R1)* | the entry's own environment differs from `rp11-entry-env/1` (§7.9). **Diagnostic**: it detects misconfiguration of the root-owned boundary. It does not prevent what it detects. No value is echoed |
| `entry-boundary-absent`, `entry-unit-mismatch`, `entry-pass-config-unavailable`, `entry-import-unverified` *(R1)*; `entry-launcher-mismatch` *(R2)* | §6.5. All **diagnostic** |
| `launch-usage`, `launch-invocation-id` *(R2, LB-2S)* | `rp11-launch` refused before any `execve` (§4.4.3.4). This is a journal line, not an RP-11 record, because no entry process exists |
| `environment-launch-refused` | the launcher's own check refused (OB-6). This should be unreachable, and it is a C-10 act failure after X-1 |

### 7.8 Canonical serialisation and digest

`environment_sha256 = SHA-256( b"rp11-launcher-env/1\n" + b"".join(k + b"=" + v + b"\0" for k, v in sorted(map)) )`

The keys and values are ASCII. The digest is recorded in the genesis state and
in every per-act record. In key-file mode the digest is a reviewed constant
that the manifest can pin. In agent mode it depends on the maintainer-bound
value.

### 7.9 The entry's own environment, `rp11-entry-env/1` (*new, R4-D1-R1; rewritten R4-D1-R2*)

`rp11-launcher-env/1` governs what the entry **gives** its children. This
contract governs what the entry **is started with**. The reviewed bytes left it
to the operator's shell, which is R4-D1-1.

*The R1 version of this section said the environment "is established by the
M-9 boundary". Its LB-2 table took `PATH` and `LC_ALL` from the unit's
`Environment=`, the `User=`-derived variables and `JOURNAL_STREAM` from
systemd, and `LANG` "if the installed systemd passes it". It described what an
open manager block might contain, not a closed contract. That text is withdrawn
(Appendix B).*

**Who establishes it.** Under LB-2S and LB-1, the environment is the
**literal** that `rp11-launch` passes to the entry's `execve` (§4.4.3.4). No
manager, unit, PAM or client source contributes to it, except the one value
`INVOCATION_ID` under LB-2S. That value is selected by exact name and checked
against a grammar. The entry cannot clean an environment its loader has
already consumed, and it does not try.

**The entry's check is diagnostic.** Before X-1 the entry compares its own
environment with the contract and refuses on any difference
(`entry-environment-unexpected`). The check can show that something other than
`rp11-launch` started the entry. It can never show what a loader consumed, and
it is never credited with preventing anything. The entry passes none of these
variables to a child (§7.1).

| M-9 option | Exact key set | Values | Established by |
|---|---|---|---|
| **LB-2S** | `{INVOCATION_ID, LC_ALL, PATH}`, and no other key | `INVOCATION_ID`: `[0-9a-f]{32}`, recorded in the genesis state (§6.8). `LC_ALL`: exactly `C`. `PATH`: exactly `/usr/bin` | `rp11-launch`'s literal `execve` (prevention, given PO-9 and PO-14) |
| **LB-1** | `{LC_ALL, PATH}`, and no other key | as above | the same image, started by the client (prevention of environment only, given PO-9) |
| LB-2 (R1 unit), LB-2T | **no closed contract exists** | — | an open manager block (S-1). Withdrawn |
| LB-3 | **no closed contract exists** until PO-10 shows `sudo` adds no PAM environment and no default keep or check variables for this command | — | `sudo`, not ready (§4.4.4) |

**Keys that R1 allowed and that now refuse.** Under LB-2S, the presence of any
of the following refuses (`entry-environment-unexpected`):

* `USER`, `LOGNAME`, `HOME`, `SHELL`;
* `JOURNAL_STREAM`;
* `LANG`; and
* any other manager-defined name (S-3).

Each one means that the entry's `execve` did not come from `rp11-launch`. The
entry needs none of them: `-I -S` reads no `HOME`, and `LC_ALL` supersedes
`LANG`.

**Digest.** `entry_environment_sha256` uses §7.8's serialisation with the
prefix `b"rp11-entry-env/1\n"`. It is recorded in the genesis state only. The
values are not secret, but are still not recorded (C-9). Under LB-2S the digest
varies with `INVOCATION_ID`. The manifest pins the key set, the literals and
the grammar, not the digest.

**One contract, two copies, tested for drift.** The contract lives in
`entry_environment.py`, which the Python check reads, and as compiled literals
in `rp11-launch`'s source, which the image writes. T-B14 asserts that the two
agree byte for byte.

---

## 8. Rejected non-solutions

| Proposal | Why it is not a solution |
|---|---|
| A blanket allowlist for the capture wrapper in `guard-secrets.py` | an arbitrary exemption (G-2). Anything behind the wrapper escapes the secret search |
| Rebuilding a shell string from argv and running it through `bash -c` | a shell between the check and execution. Quoting differences reopen every case `test_guards.py` refuses. It violates G-3 |
| A second launcher that is not gated, "for the synchronization only" | exactly the bypass C-11 forbids. The captured path would run what the direct path refuses |
| A `guard_passed=True` flag, an allow token or a pre-approved argv passed into `ActRequest` | trusts a value instead of evaluating. Under O-1/O-2 no caller-supplied argv exists at all |
| Running the hook as an advisory subprocess whose result the capture may ignore | G-4 |
| Copying the rsync-exclusion rules into the capture module | two drifting policies (G-4) |
| Changing §5's text (for example to `--exclude=.env*` or adding `-e`), or splitting it | G-1. The guard deliberately refuses the unquoted form |
| Interposing a shim `rsync` on `PATH` or through `BASH_ENV` so the plain command is captured | hides execution from review. The executed program is not the inspected one |
| A `PostToolUse` capture of the client's output | merged and possibly truncated (§6.2 draft). Not C-2 evidence |
| Inheriting `SSH_AUTH_SOCK`, `HOME` or `PATH` "after checking" | inheritance by another name (assignment §1, item 2) |
| *(R1)* A post-start check, `unset`, `env -i`, an assignment prefix or a self-re-exec to "clean" the entry's own environment | the loader has already acted in the process doing the cleaning (§4.3, §4.4.1). At most diagnostic |
| *(R1)* `systemd-run` with caller-supplied properties or command, or a templated unit whose instance string carries a value | caller-supplied argv or environment by another name. LB-2 uses one fixed, non-templated unit per pass |
| *(R1)* A sudoers rule with a wildcard, `SETENV`, `env_keep` of anything, or a shell | makes `sudo` a general wrapper. LB-3 allows exactly one argv |
| *(R1)* Describing the client hook as inspecting a template's instantiation | not inspection of the command (§5.4). A K-O text is inspected only before its launch |
| *(R2)* A unit whose `ExecStart=` is a dynamically linked image, with `Environment=` lines, presented as establishing a closed environment | the block is the open manager environment plus the unit's settings (S-1). `Environment=` adds to it and does not replace it. That is `R4-D1-R1-1` |
| *(R2)* `UnsetEnvironment=` of loader names, presented as closing the environment | a finite deny-list over an open, version-dependent set (S-3, S-4) |
| *(R2)* A pre-pass snapshot of `show-environment`, presented as prevention | a snapshot of mutable state (S-7). It also puts environment content into evidence (C-9). LB-2S neither needs nor takes it |
| *(R2)* Root ownership of the installed unit file, presented as fixing what PID 1 runs | the loaded configuration also depends on drop-ins, unit-path precedence, generators and manager defaults (S-5) |
| *(R2)* A glibc-static `rp11-launch`, presented as meeting PO-9 without evidence | its start-up processes `GLIBC_TUNABLES` before `main` (AS-11) |

---

## 9. Proposed interfaces (for a later bounded implementation)

**New modules**, all covered sources:

| Module | Public surface |
|---|---|
| `tools/phase_5_0_evidence/execution/guard_gate.py` | `load_policy(repo_root, pins) -> Policy`; `Policy.evaluate_text(text) -> GateDecision`, which evaluates both hooks under every branch context; `GateDecision(allowed, entry_id, policy_digests, contexts, message)` |
| `tools/phase_5_0_evidence/execution/act_catalogue.py` | `CatalogueEntry`; `PASS_A: tuple[CatalogueEntry, ...]`; `parse_reviewed_text(text) -> tuple[str, ...]`; `PROGRAM_PATHS = {"rsync": "/usr/bin/rsync", "ssh": "/usr/bin/ssh"}` |
| `tools/phase_5_0_evidence/execution/launcher_environment.py` | `CONTRACT_ID`; `build(mode, pairs, binding) -> LauncherEnvironment`; `LauncherEnvironment.mapping` (a read-only view); `.sha256`; `EnvironmentRefused(classification)` |
| ~~`tools/phase_5_0_evidence/execution/rp11_cli.py`~~ | *withdrawn R4-D1-R1.* It was started by the client shell under *E_c*, with digests on the command line (OB-16). It is replaced by the bootstrap below |
| `tools/phase_5_0_evidence/execution/rp11_entry.py` *(R1)* | the bootstrap: `run --pass A` and nothing else. It uses only the standard library. Its first statements are `chdir("/")` and `umask(0o077)`. It reads `/etc/freedom-blades-rp11/pass-a.json` and requires it to be root-owned and not group- or world-writable. It reads every covered source once, verifies the manifest digest, and installs a `sys.meta_path` finder that serves only verified bytes for `tools` and `application`, refusing any other repository import. It checks `rp11-entry-env/1` (diagnostic), and under LB-2S `INVOCATION_ID` and parent PID 1. Only then does it import the entry proper. Under M-12 it is installed root-owned at `/usr/local/libexec/freedom-blades-rp11/rp11_entry.py`. **Installing or wiring it is a separate authority, not granted by choosing an option** |
| `tools/phase_5_0_evidence/execution/entry_environment.py` *(R1; amended R2)* | `ENTRY_CONTRACT_ID = "rp11-entry-env/1"`; `KEY_SETS = {"LB-2S": ("INVOCATION_ID", "LC_ALL", "PATH"), "LB-1": ("LC_ALL", "PATH")}`; `LITERALS`; `check(environ_items, boundary) -> EntryEnvironment`; `.sha256`; `EntryEnvironmentUnexpected(key_name_or_malformed)`. This is the one place where the entry reads its own environment, and it does so only for this **diagnostic**. *(R2)* It declares no key set for LB-2 (R1), LB-2T or LB-3, because none is closed |
| `infra/rp11-launch/` *(R2, LB-2S or LB-1; exists only under M-14)* | the static first image's source and build definition, implementing `rp11-launch/1` (§4.4.3.4): argv exactly `--pass A`; `envp` read only for `INVOCATION_ID` under LB-2S; descriptor, signal, umask and working-directory reset; one literal `execve`; fixed exit status per failure class (`launch-usage`, `launch-invocation-id`, `launch-exec-failed`). Its language, runtime and toolchain are the M-14 design pass's to choose, subject to PO-9. **Building it for installation, installing it or wiring it is a separate authority** |

**New boundary files** *(R1)*. They are repository text, installed only under
H-1. The set depends on M-9:

| M-9 | Files |
|---|---|
| LB-2S *(amended R2)* | `infra/systemd/rp11-capture-pass-a.service` (the §4.4.3.4 text, with `ExecStart=` naming `rp11-launch` and no `Environment=`), `infra/polkit/50-freedom-blades-rp11.rules`, and `infra/rp11-launch/` (M-14); a schema for `pass-a.json`, including `launcher_sha256`, in `entry_environment.py` or a sibling module |
| LB-3 | `infra/sudoers/freedom-blades-rp11` (§4.4.4); the same schema |
| LB-1 | the launcher's source, build definition and pinned toolchain (§4.4.2); the same schema |

**Changed modules:**

* `capture_contract.py` gains the §6.8 record fields and the corrected
  `validate_argv` docstring (OB-7).
* In `capture_mechanism.py`, `ActRequest` loses `argv` and `environment`. The
  session receives `entry_id` and derives the argv and the map internally,
  through the gate and the builder.
* `boundary.py` is unchanged. The launcher's existing checks remain as a
  second layer.
* Each hook file gains `evaluate` (O-1/O-2) and invocation resolution (O-2
  only).

**Hook invocation grammar (O-2)** *(amended R4-D1-R1)*. The reviewed bytes'
grammar (`… python -E -s -m …rp11_cli run --pass (A|B) --reviewed-digest …`)
is withdrawn. It named a client-started entry (R4-D1-1) and admitted Pass B
(F-4). The whole command must match exactly one of these, depending on M-9:

```
LB-2S: ^/usr/bin/systemctl --no-ask-password start --wait rp11-capture-pass-a\.service$
LB-3: ^/usr/bin/sudo -n -u [a-z_][a-z0-9_-]{0,31} -- /usr/bin/python3\.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_entry\.py run --pass A$
LB-1: ^/usr/local/libexec/freedom-blades-rp11/rp11-launch --pass A$
```

The rules are:

* **Exact match.** The hook first applies its unchanged rules to the literal
  text. It then reads Pass A's catalogue file and requires its SHA-256 to equal
  the `catalogue_sha256` in the root-owned `/etc/freedom-blades-rp11/pass-a.json`.
  It applies its unchanged rules to **every** Pass A text, whether or not that
  text is enabled for this pass. All must allow. Under D-2a every such text is
  complete (K-L). Under D-2b the hook must also authenticate the statement by
  its digest in the pass configuration and instantiate A1-12. Under R-e it
  evaluates A1-12's template only, and nothing describes that as inspecting
  A1-12.
* **Near match.** If the text contains `rp11-capture-`, `rp11_entry` or
  `rp11-launch` but does not match exactly, the hook refuses
  (`rp11-invocation-malformed`).
* **Load or digest failure.** A missing or unreadable pass configuration, a
  catalogue digest mismatch, or a load failure refuses.

The hook reads the catalogue by reading the file at a fixed repository path
and executing it in a private namespace, as §6.4 does in reverse. It does not
verify the whole manifest: the entry does that. **All of this runs under
*E_c*, so it is defense in depth** (§4.3 T1).

**Invocation granularity (F-2, decision M-6).** A session cannot be reopened,
so the whole pass runs inside one entry process. Step-level operator judgement
in the draft then has to become catalogue data:

* A1-C conditionality becomes `enabled_by` flags from the authorization.
* *(amended R4-D1-R1)* A1-12's substitution is removed under D-2a (a literal),
  becomes a K-R slot under D-2b, or stays a K-O slot under R-e (§6.6.2).
* Expected-value stops become typed predicates over the admitted stdout of an
  act. Examples are exact bytes for `A1-01` and exit `1` for `A1-19`.

The alternative is a long-lived session process that receives step
identifiers over a local control channel. That adds an IPC trust boundary and
is not recommended in this proposal.

*(R1)* **This holds for Pass A only.** Pass B's live reboot confirmation (B6.3)
and its K-O slots (§6.6.1) cannot be pre-start data for a per-pass entry
(F-4). Pass B needs either that control channel or a draft redesign, and
either needs its own design pass (M-11).

---

## 10. Test matrix

None of these tests reads a secret, contacts a host, runs a real
synchronization or creates a real capture root. All filesystem work is under
pytest temporary directories with fake or temporary roots.

### 10.1 Guard boundary (C-11)

| ID | Test | Expected |
|---|---|---|
| T-G1 | the refactored hooks: all 41 existing `test_guards.py` cases, via the executable, unchanged | 27 refuse, 14 allow (behaviour preserved) |
| T-G2 | §5 text (OB-1) added as an ALLOW case (F-1) | allowed. Counts become 27/15 |
| T-G3 | **direct versus captured decision equivalence**: for every `test_guards.py` Bash case and every catalogue text, the hook executable's exit (0/2) equals `Policy.evaluate_text` | identical in every case |
| T-G4 | branch invariance: each catalogue text under `main`, `master`, a non-default name and `""` | allowed in all four. A synthetic `git commit` text is refused in the gate under every context |
| T-G5 | policy digest mismatch: a temporary copy of a hook with one byte changed | `guard-policy-unavailable`. Recording fakes observe **zero** filesystem, launcher and X-1 calls |
| T-G6 | policy missing, unreadable, syntax error, `evaluate` absent or not callable, or `evaluate` raising | `guard-policy-unavailable`, zero calls |
| T-G7 | a synthetic catalogue whose entry is each `test_guards.py` BLOCK text | admission refusal `guard-refused` before X-1, zero calls |
| T-G8 | a per-act re-evaluation refusal, injected by a fake policy after admission | act not launched, one X-3, session sealed |
| T-G9 | parser: every catalogue text equals its pinned `tokens`, and equals the `bash --noprofile --norc` `printf '%s\0'` oracle (PO-5) | equal |
| T-G10 | parser refusals: each unsafe character unquoted, unbalanced quotes, unescaped `$` or backtick inside double quotes, globs, `~`, non-ASCII, empty word | refused |
| T-G11 | drift: `A1-00` text equals draft §5 and test-server §3.2 fenced blocks, and each A1 text equals its draft cell | equal |
| T-G12 | structural: no public path passes a caller argv to `StreamCaptureLauncher.launch`, and `ActRequest` has no `argv` field | AST and inspection assertions |
| T-G13 | *(amended R1)* entry grammar: an unknown pass, `--pass B`, an extra option, a pass-configuration digest mismatch, or an interpreter without `-I` or `-S` | refused, zero calls |
| T-G14 | (O-2) hook resolution in `test_guards.py`: exact invocation → allow; unknown pass → refuse; exact invocation followed by `; cat .env` → refuse; near-match invocation → refuse; catalogue file unloadable (temporary repository copy) → refuse. *(R1)* The grammar is now the M-9 literal; see T-B11 | as stated |
| T-G15 | record binding: text, text digest, entry identifier, policy digests, contexts and environment digest round-trip through `CaptureRecord` validation. A mutated field is refused | as stated |

### 10.2 Environment contract

| ID | Test | Expected |
|---|---|---|
| T-E1 | **empty inherited environment.** With `os.environ` poisoned (`PATH=/poison`, `HOME=/poison`, `SSH_AUTH_SOCK=/poison`, `RSYNC_RSH=x`, `LC_ALL=xx`), `build("key-file", …)` returns exactly `{"LC_ALL": "C", "PATH": "/usr/bin"}` | exact equality. A structural test finds no `os.environ` or `getenv` use in the builder |
| T-E2 | **child observation.** The armed launcher, run on a test-owned temporary root with argv `("/usr/bin/env", "-0")` and the built map, produces stdout that parses to exactly the map | nothing inherited (proves G-3 with the real `execve`) |
| T-E3 | missing required input: agent mode without `SSH_AUTH_SOCK` | `environment-missing-key` before X-1 |
| T-E4 | extra variables: each §7.2 **P** name → `environment-prohibited-key`, and an arbitrary name → `environment-unexpected-key` | as stated. No value appears in the message |
| T-E5 | mutated values: `PATH` as `/usr/bin:/bin`, `/usr/bin/`, `/usr/bin ` or `/usr/local/bin`; `LC_ALL` as `C.UTF-8` or `c`; socket as relative, containing `..`, containing `//`, 108 bytes long, containing `=`, or non-ASCII | `environment-literal-mismatch` or `environment-value-grammar` |
| T-E6 | structural: a duplicate pair, empty key, empty value, NUL, `=` in a key | the matching class |
| T-E7 | binding: `MI.ssh_auth_sock_sha256` off by one hex digit | `environment-binding-mismatch`. The value is absent from the exception, `caplog` and any record |
| T-E8 | socket checks on a test-created `AF_UNIX` socket, bound but never connected by the builder: OK case accepted; regular file; symlink; parent mode `0750`; parent owned by another uid (skipped with a reason if the test cannot `chown`) | the correct refusal for each. A fake `socket` module asserts no `connect` |
| T-E9 | **direct versus captured equivalence of the map**: the map given to an `rsync` act and to an `ssh` act in one session are the same object and digest, and `environment_sha256` in every record equals the genesis value | equal |
| ~~T-E10~~ | *withdrawn R4-D1-R1.* It tested a post-start name check as if it were prevention. It is replaced by T-B7, which is explicitly diagnostic | — |
| T-E11 | *(optional; needs explicit maintainer permission because it executes the real `rsync` binary locally)*: `/usr/bin/rsync` with a local-only source and a destination `stub:/x`, a `PATH` pointing at a test directory whose `ssh` is a stub that writes its environment and exits 1 | the stub's environment equals the map (PO-2). No network, no transfer |

### 10.3 Launch boundary (R4-D1-1, R4-D1-R1-1) (*new, R4-D1-R1; amended R4-D1-R2*)

**What these tests can and cannot prove.** Every test below is
repository-only. None of them runs a loader experiment, a real hook against a
secret name, `systemctl`, `sudo`, `ssh` or `rsync`. **None can prove the M-9
prevention property itself.** That is a property of systemd, polkit, `sudo` or
the static image on the host (PO-8 … PO-11, and *(R2)* PO-14 … PO-16). Establishing it needs a later,
separately authorized host drill. This proposal requests no such drill, and no
implementation slice may claim the property from these tests.

*(R2)* In particular, **no test below shows that the entry's environment is
closed.** That depends on PO-9 (the built image's start-up) and PO-14 (the
installed executor), neither of which is repository-testable here. T-B1 and
T-B13 … T-B15 test text. T-B7 tests a diagnostic.

| ID | Test | Expected |
|---|---|---|
| T-B1 | *(LB-2S; amended R2)* the unit text: the exact key set; `ExecStart=` exactly `/usr/local/libexec/freedom-blades-rp11/rp11-launch --pass A`; `WorkingDirectory=/`; `StandardInput=null`; `NoNewPrivileges=yes`; **no** `Environment=`, `EnvironmentFile=`, `PassEnvironment=`, `UnsetEnvironment=`, `PAMName=`, `ExecStartPre=`, `ExecStartPost=` or credential import; a non-templated name. **The docstring states that this is a property of the text, not of the loaded configuration (S-5)** | as stated |
| T-B2 | *(LB-2S)* the polkit rule text: one action identifier, one unit, the verbs `start` and `stop` only, one subject-user placeholder | as stated |
| T-B3 | bootstrap verifies before executing: in a temporary tree, one covered byte changed and a sentinel covered module that writes a marker if executed | `manifest-digest-mismatch`, marker absent, zero filesystem, launcher and X-1 calls |
| T-B4 | import closure (F-6): the entry's imports are all served by the verified finder. `application/__init__.py` and `application/idempotency.py` are in the verified set (or no longer imported). An attempted import of any other repository module is refused | `entry-import-unverified` for the unverified import |
| T-B5 | no bytecode: a forged `__pycache__/*.pyc` beside a covered source in a temporary tree | never loaded (marker absent); no `__pycache__` written |
| T-B6 | working directory: the bootstrap is started from a temporary working directory containing a shadow `tools/` package | shadow never imported (marker absent); `os.getcwd() == "/"` before any repository import |
| T-B7 | *(diagnostic, replaces T-E10)* `entry_environment.check` over synthetic mappings: *(amended R2)* exactly `{INVOCATION_ID, LC_ALL, PATH}` (LB-2S) or `{LC_ALL, PATH}` (LB-1) with the literal values is accepted; any additional key (`LD_PRELOAD`, `GLIBC_TUNABLES`, `PYTHONPATH`, `BASH_ENV`, `USER`, `HOME`, `JOURNAL_STREAM`, `LANG`, an arbitrary name), a missing key, a non-literal value or a malformed `INVOCATION_ID` is refused; no key set exists for the R1 LB-2 unit, LB-2T or LB-3. **The test docstring states that this proves detection, not prevention** | `entry-environment-unexpected`; no value appears in the message, `caplog` or any record |
| T-B8 | *(LB-2S)* `INVOCATION_ID` absent, malformed, or a parent PID other than 1, through injected fakes | `entry-boundary-absent` |
| T-B9 | pass configuration: missing, a symlink, not root-owned (through a fake `stat`), group- or world-writable, malformed JSON, an unknown key | `entry-pass-config-unavailable` |
| T-B10 | structural: only `entry_environment.py` reads `os.environ` or calls `getenv`; no `shell=True`; before verification, the bootstrap imports only an allow-listed set of standard-library modules | AST assertions |
| T-B11 | hook grammar in `test_guards.py`: the chosen M-9 literal → allow (with a temporary pass configuration and catalogue); the other two options' literals, `--pass B`, `rp11-capture-pass-b.service`, a prefix or suffix, and an extra space → refuse; catalogue digest ≠ the temporary pass configuration → refuse | as stated |
| T-B12 | *(M-13, only if chosen)* each hook's first line is `#!/usr/bin/python3 -I` | as stated. It is not a test of loader behaviour |
| T-B13 | *(R2, M-14)* `rp11-launch` source, structural: the `execve` path, argument vector and environment array are compiled literals equal to the manifest's `rp11-launch/1` data; `envp` is referenced only in the `INVOCATION_ID` selection; the argv check accepts exactly `--pass A`; every failure path exits without `execve`; no `dlopen`, `getenv`, `setlocale`, NSS or iconv call appears | as stated. **The docstring states that this checks source text, not the start-up behaviour of the built image (PO-9)** |
| T-B14 | *(R2)* drift: `rp11-launch`'s environment literal and `INVOCATION_ID` grammar equal `entry_environment.KEY_SETS["LB-2S"]` and `LITERALS`, and the LB-1 variant equals `KEY_SETS["LB-1"]` | equal |
| T-B15 | *(R2)* `rp11-launch/1` selection logic, as a pure function tested over synthetic `envp` vectors (the same selection compiled into the image and exercised through a test harness under M-14): zero, two or malformed `INVOCATION_ID` entries refuse; any other entries, including `LD_PRELOAD` and `GLIBC_TUNABLES`, never appear in the output environment | as stated. It tests the selection, not the loader |

### 10.4 Knowability and inspection (R4-D1-2) (*new, R4-D1-R1*)

| ID | Test | Expected |
|---|---|---|
| T-K1 | *(D-2a)* every Pass A catalogue entry has `parameters == ()` and is a literal. The set of entry identifiers equals the §6.6.1 Pass A table, including A1-23a … A1-23g and each A1-Z repeat | as stated |
| T-K2 | *(D-2a)* A1-12's text equals the **amended** draft cell. It fails until D-2 is applied to the draft, which is intended | equal after D-2 |
| T-K3 | A1-32's text equals A1-31's text with only its `--command` operand replaced | equal |
| T-K4 | the hook's resolution evaluates every Pass A text, enabled or not: a fake policy records the evaluated identifiers | all identifiers |
| T-K5 | no Pass B catalogue exists, and every Pass B form of the invocation is refused by the entry and by the hook (M-11) | refused |
| T-K6 | record: `inspections` never lists the client hook; a `literal` record with `template_sha256` or `slot_bindings` is refused; an `instantiated` record without them is refused | as stated |
| T-K7 | *(D-2b or R-e only)* slot grammar refusals. A K-O value is taken only from the named admitted record. D-2b: A1-11 ≠ statement → A1-12 not launched. R-e: a `guard-git.py` refusal of an instantiated text at pre-launch → act not launched and one X-3 | as stated |

---

## 11. Manifest impact (for the later implementation; **no increment now**)

**Added to `COVERED_SOURCES`:**

* `.claude/hooks/guard-secrets.py`
* `.claude/hooks/guard-git.py`
* `.claude/settings.json` (O-2: the registration that makes the hook layer exist)
* `tools/phase_5_0_evidence/execution/guard_gate.py`
* `tools/phase_5_0_evidence/execution/act_catalogue.py`
* `tools/phase_5_0_evidence/execution/launcher_environment.py`
* ~~`tools/phase_5_0_evidence/execution/rp11_cli.py`~~ *(withdrawn R1; §9)*
* *(R1)* `tools/phase_5_0_evidence/execution/rp11_entry.py` (the bootstrap)
* *(R1)* `tools/phase_5_0_evidence/execution/entry_environment.py`
* *(R1, F-6)* `application/__init__.py` and `application/idempotency.py`, or
  whatever the entry's import closure contains outside
  `tools/phase_5_0_evidence/**` at implementation time. T-B4 enforces the
  closure. The alternative is to remove those imports from the covered sources
  the entry loads
* *(R1; amended R2)* the chosen M-9 boundary files (§9): under LB-2S,
  `infra/systemd/rp11-capture-pass-a.service`,
  `infra/polkit/50-freedom-blades-rp11.rules` and every source and build
  definition file under `infra/rp11-launch/` (M-14). Under LB-1, the last of
  these only

**Changed covered sources:** `capture_contract.py` and `capture_mechanism.py`.

**New serialised manifest content**, which is data and not only file digests:

* each catalogue entry's `entry_id`, `command_text_sha256`, `tokens` and
  `program`;
* `PROGRAM_PATHS`;
* the environment contract's identifier, key sets per mode, literals,
  grammars and prohibited set;
* the key-file-mode `environment_sha256`; and
* the two policy digests.

*(R1)* Additionally:

* each Pass A entry's `text_class`, which is `literal` for every entry under
  D-2a. The manifest thereby states that no Pass A text is completed at run
  time;
* the `rp11-entry-env/1` contract: its key set per M-9 option, its literals and
  its grammars;
* the M-9 option identifier and the client-inspected invocation literal (§4.4);
  and
* the pass-configuration schema. Its per-pass **values** are not manifest
  content: they are maintainer inputs, bound by the pass configuration's digest
  in the A-2 authorization.

*(R2)* Additionally:

* the `rp11-launch/1` contract: the accepted argv, the literal `execve` path
  and vector, the literal environment array, the `INVOCATION_ID` grammar and
  the exit status per failure class;
* `rp11-entry-env/1` as a key set **per closed option only** (LB-2S and LB-1).
  The absence of any key set for the R1 LB-2 unit, LB-2T and LB-3 is itself
  manifest content; and
* if M-14 adopts a reproducible build, the expected digest of the built image
  for the pinned toolchain and architecture.

**What the manifest cannot bind** *(R1; amended R2)*. The root-owned
**installed** copies on the repository host are the unit, the polkit rule, the
bootstrap, the pass configuration and *(R2)* the `rp11-launch` binary. The
manifest binds their repository sources. Their installed digests are bound by
the pass configuration and by H-1's installation record. The entry re-checks
the unit's and the launcher's digests and its own environment, but **only
diagnostically** (§6.5). PID 1, the executor, polkit, `sudo`, the interpreter
and the loader configuration are trusted system state (R-8), not manifest
content. *(R2)* Four further things are outside the manifest:

* **the toolchain** that builds `rp11-launch`. M-14 pins it;
* **the loaded unit configuration and the manager's execution settings**
  (S-5, R-10). H-1 and H-2 bind them at one moment each, and nothing binds
  them afterwards (S-7);
* **the manager's global environment.** It is not bound, not recorded and
  not relied on; and
* **PO-9 and PO-14.** They are properties of a built image and an installed
  systemd, not of bytes the manifest covers.

**Bytes that invalidate the reviewed digest:** any byte of the files above.
That includes any hook edit, which is intended: a guard change must be
re-reviewed before capture relies on it. It also includes any catalogue text,
token, program path, contract literal or grammar. The draft is **not** a covered
source. It is bound by `PIN.prompt_sha256` (A-1) and, for its command texts, by
T-G11.

**Version.** The later implementation raises `MANIFEST_VERSION` from 26 to 27,
with a rationale comment in the file's established style. The digest is review
input only.

`.claude/hooks/test_guards.py` stays a test, not a covered source.

---

## 12. Rollout and rollback

**Proposed implementation slices.** Each slice is repository-only, unwired,
separately assigned and reviewed:

| Slice | Content | Behaviour change |
|---|---|---|
| I-1 | the hook `evaluate` refactor and T-G1–T-G3 (F-1 fixed) | **none** for the client. Proven by 41 unchanged cases plus T-G3 |
| I-2 | `act_catalogue`, `parse_reviewed_text`, `guard_gate` and T-G4–T-G13 | none. Unwired |
| I-3 | `launcher_environment` and T-E1–T-E9 (T-E10 is withdrawn) | none. Unwired |
| I-4 | record schema, `ActRequest` change and T-G15. Manifest version 27 | capture internals only. Unwired |
| I-5 | (O-2) hook resolution and T-G14, T-B11, T-K4 and T-K5. `settings.json` covered | Claude client: the exact M-9 literal now resolves, and a near-match refuses |
| *(R1)* I-6 | `rp11_entry` bootstrap, `entry_environment`, the M-9 boundary **files as repository text**, the import-closure coverage (F-6), and T-B1 … T-B10 and T-K1, T-K3, T-K6 (and T-K7 if applicable) | none. Unwired. Nothing is installed |
| D-1 | draft amendment §5.3, with a new draft digest and re-review | documents |
| *(R1)* D-2 | the A1-12 text (D-2a or D-2b) and the §4.6 definition, applied to the draft together with D-1; then T-K2 | documents |
| *(R2)* I-7 | only under M-14: `infra/rp11-launch/` source and build definition implementing `rp11-launch/1`, the toolchain pin, and T-B13 … T-B15. Building for tests is in the slice only if M-14 authorises the toolchain | none. Unwired. **Nothing is installed.** PO-9 is not discharged by this slice |
| *(R1; amended R2)* **H-1** | **host provisioning on the repository host**: install the chosen M-9 boundary files root-owned, which under LB-2S includes the `rp11-launch` binary; under LB-2S, `systemctl daemon-reload`; record the installed digests in the pass configuration; write the §4.4.3.7 installation record, including `FragmentPath`, an empty `DropInPaths` and `NeedDaemonReload=no` | **not repository-only.** It needs its own maintainer authority, which this proposal does not request. Until H-1 exists, the conditional direction's prevention property does not exist on any host |
| *(R2)* **H-2** | **the pre-pass check**, before each pass (§4.4.3.7): re-report the H-1 digests and the loaded unit's effective properties and manager defaults; the pass's authorization binds the digest; any difference stops the pass before it is requested | **not repository-only**, and a review, not prevention (R-10). It needs its own authority for each pass |
| *(R2)* PO-9, PO-14, PO-16 | the citations of runtime and systemd source; the later loader experiment on the built image; the manager-environment drill | **host or build steps**, each separately authorized. None is requested here |

**Rollback.**

* Each slice is one reviewable change set, reverted by an ordinary follow-up
  change and never by a history rewrite.
* I-1's rollback restores today's hooks exactly. `test_guards.py` is the
  regression gate.
* I-5's rollback leaves O-1's guarantees intact.
* *(R1; amended R2)* H-1's rollback, under its own authority: remove the
  installed files, including `rp11-launch`, then `systemctl daemon-reload`
  (LB-2S); or remove the sudoers drop-in (LB-3); or remove the launcher (LB-1).
  H-2 changes nothing on the host and needs no rollback. No capture root is touched by H-1 or by its
  rollback.
* Nothing is wired, so no operational rollback exists or is needed.
* There is no feature flag. Absence of wiring is the off state.

---

## 13. Maintainer decisions required

| # | Decision | Options | Recommendation |
|---|---|---|---|
*Amended R4-D1-R1.* The reviewed table's recommendation of **O-2** as though it
met every constraint is withdrawn. The decisions below are the **minimum
choices**. The "Conditional direction" column states what this proposal would
recommend **if** the listed prerequisite choices are made. It is not a claim
that any option satisfies today's constraints (§4.4.7).

*Amended R4-D1-R2.* **No recommendation is ready** (§0-R2). The column below
still states a conditional direction for each decision, which applies only if
the prerequisites are chosen. The R1 row for M-9 named LB-2 as the conditional
direction. It is withdrawn (Appendix B).

**Decision order.** M-9, M-14 and M-10 come first, then D-2 and M-11, then
D-1, and only then MD-C11. D-1's wording depends on all of them.

| # | Decision | Options | Conditional direction |
|---|---|---|---|
| ***M-9*** *(R1; amended R2)* | The launch boundary that keeps ambient loader and process state from the entry (R4-D1-1, R4-D1-R1-1, §4.4) | **LB-2S**, service manager with a static first image (needs M-14, H-1, H-2); **LB-1**, static launcher started by the client (needs M-14; inherits client execution state); **LB-2T**, the R1 unit with manager state trusted (**review, not prevention**; only under the narrowed M-10); **LB-3**, `sudo` rule (**not ready**, §4.4.4); **decline** (C-11 stays open, and nothing may describe the in-process gate as fail-closed against ambient state). *The R1 LB-2 unit is withdrawn as an option* | **none ready.** Conditionally **LB-2S**: the only option that keeps both client-derived process state and every environment source except its own literal from the entry. It needs M-14, H-1 and H-2, and PO-9 and PO-14 must hold |
| ***M-14*** *(new R2)* | Accept a compiled static first image as a new build dependency, and commission its design pass (§4.4.7) | **accept**: a design pass chooses a runtime meeting PO-9 (a glibc-static build is excluded by AS-11 unless disproved), a pinned toolchain, a reproducible build and the installed-digest binding; or **decline**: neither LB-2S nor LB-1 exists, and no option prevents unreviewed loader state from reaching the entry | **accept**, if C-11 is to be met at all. It is AGENTS.md's "deliberate dependency" decision, and it is the maintainer's |
| ***M-10*** *(R1; revised R2)* | Threat scope | **T-A in scope, with manager execution settings trusted as reviewed root input** (R-10). Ambient manager environment is prevented by LB-2S. T-B is out of scope for record integrity, with LB-2S provenance as partial evidence (R-7); **T-A narrowed to exclude ambient manager state**, the only form under which LB-2T is admissible (a redefinition, stated so that it is never silent); or **T-A and T-B**: needs a dedicated capture account and a new authentication design | **T-A in scope, with R-10 accepted explicitly.** Not the narrowing. T-B needs its own design pass |
| ***D-2*** *(R1)* | A1-12's text (R4-D1-2, §6.6.2) | **D-2a**, a literal hashed through the venv entry (optionally D-2a+, which brackets A1-11); **D-2b**, instantiated from the pinned statement; **decline**, leaving **R-e** as the only truthful form | **D-2a**. D-2b if A1-12 must keep naming the real path |
| ***M-11*** *(R1)* | Scope of this C-11 decision | **Pass A only**. Pass B's K-O slots (B2 `--at`, `--requested-at` and the flags), its K-U placeholders and its mid-session gate (B6.3, F-4) go to the Pass B draft amendment, where the pre-start criterion must be amended for named slots (R-e form) or the draft's semantics changed. Or **Pass A and B now**: not decision-ready, because no Pass B catalogue can exist | **Pass A only** |
| ***M-12*** *(R1, LB-2S or LB-3)* | Where the bootstrap lives | **root-installed copy** at `/usr/local/libexec/freedom-blades-rp11/`, with its digest in the pass configuration; or the **repository path**, operator-writable, which is adequate under T-A only | root-installed |
| ***M-13*** *(R1, optional)* | Narrow the client hooks' own start-up (§4.3 T1) | change each shebang to `#!/usr/bin/python3 -I`, which removes the `PATH` lookup and Python start-up inputs but **not** loader inputs; or leave the hooks unchanged | the maintainer's choice. It is narrowing, never protection, and it is a hook change covered by M-7 |
| **D-1** | Amend the draft's "one plain call … as written" wording as §5.3 *(rewritten R1; issue clause amended R2)* | accept; decline (C-11 then stays open and RP-11 cannot be met) | accept, **after** M-9, M-14, M-10, D-2 and M-11. Without it, no option is admissible |
| **MD-C11** | The C-11 option *(amended R1; R2)* | O-2; O-1 (no hook change, and the client hook does not see the texts). **Either is admissible only with an M-9 boundary that closes the entry's environment** (LB-2S or LB-1) | **O-2**, carried by LB-2S, for Pass A, conditionally on M-9, M-14 and M-10 |
| **M-1** | SSH authentication input | M-1a key file; M-1b agent at a maintainer-fixed socket | the maintainer's to choose from knowledge of the key; this proposal does not select. M-1a if the key needs no passphrase; otherwise M-1b |
| **M-2** | Locale literal | `LC_ALL=C`; `LC_ALL=C.UTF-8` (not guaranteed to exist) | `C` |
| **M-3** | Host-key trust given `accept-new` | (a) accept as documented, with residual TOFU; (b) admission verifies, read-only, that the known-hosts files already hold a key for `oracle-test` whose fingerprint equals a maintainer-pinned value, which needs its own authorization to read host authentication state; (c) the maintainer changes their own configuration to `StrictHostKeyChecking yes`, outside the repository | (b) or (c); not (a) |
| **M-4** | Effective `ssh` configuration | (a) maintainer attestation that no `ProxyCommand`, `LocalCommand`, `PermitLocalCommand yes` or askpass applies to `oracle-test`; (b) an admission digest of `ssh -G oracle-test` under the closed map against a pinned value, needing later authorization | (b), with (a) as the interim statement |
| **M-5** | Program paths and binary pinning *(extended R1)* | (a) `/usr/bin/rsync`, `/usr/bin/ssh`, `PATH=/usr/bin`, with `lstat` ownership and mode checks, **and the entry interpreter `/usr/bin/python3.12`** under the same checks; (b) additionally pin each binary's SHA-256 | (a). (b) is optional, because a system update would then invalidate the pin |
| **M-6** | Invocation granularity (F-2) *(amended R1)* | per-pass invocation with catalogue-encoded conditions and stop predicates; a long-lived session with a control channel | per-pass **for Pass A**. Pass B is open under M-11 (F-4) |
| **M-7** | Hook files as covered sources | yes; no | yes |
| **M-8** | Permission for optional test T-E11 (local real `rsync`, stub `ssh`) | grant; withhold (PO-2 then rests on documentation) | the maintainer's to choose |

---

## 14. Proof obligations left to implementation and review

| # | Obligation | How it would be discharged |
|---|---|---|
| PO-1 | The installed `ssh` locates the user configuration, known hosts and identity through the password database, not `HOME` (AS-2) | source or manual of the pinned OpenSSH version, cited by version, plus an `ssh -G` comparison with and without `HOME` under M-4(b) authority |
| PO-2 | `rsync` with `RSYNC_RSH` unset execs `ssh` by `PATH` and passes its environment unchanged (AS-3) | T-E11 if permitted; otherwise the pinned version's source |
| PO-3 | Whether `rsync` reads a user `popt` alias file, and how it finds it (AS-4) | the pinned version's source. If it does, and uses the password database, M-4's attestation must cover that file |
| PO-4 | The current `guard-secrets.py` allows the OB-1 text | T-G2 (F-1) |
| PO-5 | `parse_reviewed_text` equals `bash` tokenisation for every catalogue text | T-G9 |
| PO-6 | The refactored hooks decide exactly as today's | T-G1 and T-G3 |
| PO-7 *(R1, D-2a)* | GNU coreutils `sha256sum` on `oracle-test` follows a symbolic-link operand (AS-9) | the pinned coreutils version's source, which opens operands without `O_NOFOLLOW` |
| PO-8 *(R1, LB-2; revised R2)* | *The R1 statement, that a started unit's environment "is exactly the manager's plus `Environment=`, the `User=`-derived variables, `INVOCATION_ID` and `JOURNAL_STREAM`", is withdrawn as a closed description (Appendix B).* Now: (a) semantics S-1 … S-10 (§4.4.3.1) hold for the installed systemd version, S-4 in particular, and no directive that discards the global environment exists; (b) `systemctl start` carries no requester environment, descriptor, working directory, limit or confinement (S-8); (c) the precedence and re-read behaviour of `DefaultEnvironment=` and generators on `daemon-reload` (S-7). **PO-8 no longer carries any environment-prevention claim**: under LB-2S, prevention rests on PO-9 and PO-14 | the installed systemd version's documentation and source, cited by version. (b) may be corroborated by a later, separately authorized host drill. **Not repository-testable** |
| PO-9 *(R1, LB-1; extended R2 to LB-2S; load-bearing)* | The static image's start-up consults no environment before `main`: no tunables, `dlopen`, NSS, iconv or locale initialisation. Its only read of `envp` is `rp11-launch/1`'s `INVOCATION_ID` selection. *(R2)* A glibc-static build is presumed **not** to qualify (AS-11) | the chosen runtime's start-up source, cited by version, in the M-14 design pass; then a later, separately authorized loader experiment on the built image, with a poisoned block and the entry's environment digest compared with the literal |
| PO-10 *(R1, LB-3; extended R2)* | The installed `sudo`: secure-mode loading, the `env_reset` key set, `closefrom`, signal and rlimit restoration, command-specific `Defaults` syntax, and behaviour under `no_new_privs` (AS-7). *(R2)* Also: whether it merges any PAM environment (AS-12) or default keep or check variables into this command's environment, and whether a command-specific `Defaults` can remove them. Until that is shown, LB-3 has no closed contract | the installed version's documentation and source; a later authorized host check |
| PO-11 *(R1, LB-2)* | polkit's `action.lookup("unit")` and `("verb")` for `org.freedesktop.systemd1.manage-units` on the installed systemd and polkit versions, and that `stop` produces a §9.5.3 interruption | versioned documentation; a later authorized host check |
| PO-12 *(R1)* | CPython 3.12 `-I -S <script>` reads no `PYTHON*` variable, adds neither the working directory nor the script directory to `sys.path`, imports no `site`, and locates only files under its root-owned prefix (AS-8) | the pinned CPython version's documentation and `getpath` source |
| PO-13 *(R1, F-6)* | The entry's complete repository import closure is within the verified set | T-B4, and an import trace in the implementation slice |
| PO-14 *(new R2, LB-2S; load-bearing)* | On the installed systemd, the image that calls `execve` on `ExecStart=` is not loaded under the unit's assembled block. Under systemd 255 or later, `systemd-executor` is started with PID 1's own environment (AS-13). Earlier versions use a forked copy of PID 1. **If refuted, LB-2S is withdrawn for that version** | the installed systemd version's source, cited by version. Not repository-testable |
| PO-15 *(new R2, LB-2S)* | The installed manager reports the **loaded** configuration completely: `FragmentPath` reflects unit-path precedence, `DropInPaths` includes top-level type drop-ins and run-time drop-ins, and `NeedDaemonReload` reflects unapplied changes. This makes H-1 and H-2 meaningful | versioned documentation and source; exercised at H-1 under its own authority |
| PO-16 *(new R2, LB-2S)* | A later drill: a harmless sentinel set in the manager's environment is absent from the entry's environment, and `entry_environment_sha256` equals the literal's digest for the recorded `INVOCATION_ID` | a separately authorized host drill. **Corroboration only**: one host, one version, one moment |

---

## 15. What this proposal does not establish

* It does not make RP-11 met, wire the mechanism, pin `PIN.capture_tool_sha256`
  or make either pass executable.
* It reads no key, agent, socket, known-hosts file, SSH configuration or
  environment. Every statement about them is documentation-derived (OB-9) or an
  assumption (AS-1–AS-5).
* It does not choose M-1. The repository does not establish the deployed
  mechanism.
* It does not verify F-1's "would be allowed" by running the hook.
* It does not amend the draft. D-1 is proposed wording only.
* *(R1)* It does not close R4-D1-1 or R4-D1-2. Only Codex's independent
  re-review and Peter Duscha's decision can.
* *(R1)* It does not establish that any launch boundary prevents anything on
  any host. No loader experiment, interpreter-entry probe, `systemctl`, `sudo`,
  polkit or host inspection was performed. PO-8 … PO-12 are open, and *(R2)*
  so are PO-14 … PO-16.
* *(R1)* It does not authorize, request or design in detail H-1, the host
  provisioning that LB-1, LB-2S or LB-3 needs.
* *(R2)* It does not establish that systemd can build a closed environment.
  §4.4.3.3 concludes that it cannot, and relies on semantics S-1 … S-10 stated
  from documentation knowledge, not verified against the installed version
  (PO-8).
* *(R2)* It does not choose a runtime, language or toolchain for
  `rp11-launch`, or show that any runtime meets PO-9. That is M-14's design
  pass.
* *(R2)* It does not establish PO-14, on which LB-2S depends.
* *(R2)* It does not request H-2 or any drill (PO-16), and it does not treat
  H-1 or H-2 as prevention.
* *(R2)* It makes **no recommendation**. The conditional direction in §1 and
  §13 applies only if M-9, M-14 and M-10 are decided as stated.
* *(R1)* It does not resolve Pass B (M-11, F-4).
* *(R1)* It does not change A0-05 or A0-06, which remain exposed to the client
  environment (R-9).

Throughout: RP-11 remains unwired and unmet; neither pass is executable or
authorized; `plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A
remains conditional; and Package 5.0 remains not ready.

---

## Appendix A — R4-D1-R1 change record and withdrawn claims

The reviewed bytes (`e026ecf5…2e2ff0751`) were amended in place. Every claim
that Codex found untrue, or that depended on one, is quoted here verbatim, with
its replacement. Text outside the sections listed is unchanged.

| Reviewed location | Withdrawn text (verbatim) | Replaced by |
|---|---|---|
| §1, item 1 | "Inside the capture entry, which cannot be bypassed." | §1 and §4.4: the entry cannot be bypassed only with an M-9 boundary |
| §1, item 2 | "Nothing is exempted, so the client guard inspects the semantically complete commands before any process starts." | §5.4: the hook inspects K-L texts only; under D-2a, every Pass A text |
| §5.2 | "the fact that the Claude client hooks inspect it before any process starts (O-2 only)" | §5.2 (amended) |
| §5.3 D-1 | "The §5 synchronization and every A1 host command are **reviewed command texts**, fixed byte for byte in the pinned act catalogue and in this draft. … and [O-2] the client hooks inspect each resolved text before the invocation starts." | §5.3 (rewritten), with §5.4 |
| §4.2 C-4 … C-6 | the entry started by the client shell as "the interpreter (`-E -s`)", with "the digest supplied on its command line" | §4.2 (amended), §4.3, §4.4 |
| §6.2, the "client hook inspects" row, O-2 | "**yes.** The hooks resolve and evaluate every text before the client starts anything." | §6.2 (amended) |
| §6.2, the fail-closed row | "Hook absence has no effect, because the entry does not depend on the hooks" | §6.2 and §6.5 (amended) |
| §6.2, the non-Claude row | "**full**: the gate is in the entry" | §6.2 (amended), §4.4.6 |
| §6.3 | "**O-2 is viable** and meets every criterion in §6.2 under D-1." | §6.3 (amended) |
| §6.5 | "**no effect on enforcement**: C-9 and C-11 still run." | §6.5 (amended) |
| §6.6 | "It is substituted into the text *before* policy evaluation and parsing, and the substituted text's digest is recorded." (the text was otherwise described as fixed and hook-inspected) | §6.6, §6.6.1, §6.6.2 |
| §6.9 R-4 | "The entry refuses to start if any name in the prohibited-loader set of §7.2 is **present** in its own environment." | §4.4.1; the diagnostic `entry-environment-unexpected` (§7.9) |
| §7.2 | "They are also the **prohibited-loader set** for the entry process itself (R-4)" | §7.2 (amended), §7.9 |
| §7.7 | `entry-loader-variable` | `entry-environment-unexpected`, marked diagnostic |
| §9 | the `rp11_cli` invocation and the hook grammar `… --pass (A\|B) --reviewed-digest …` | §9 (amended): the bootstrap, the M-9 literals, Pass A only |
| §10.2 T-E10 | "`entry-loader-variable` and zero calls" | T-B7, explicitly diagnostic |
| §13 | "**O-2**" as an unconditional recommendation | §13 (amended): minimum choices and a conditional direction |

---

## Appendix B — R4-D1-R2 change record and withdrawn or narrowed claims

The bytes Codex re-reviewed (`a402f579…c62a49368`) were amended in place.
Every claim that `R4-D1-R1-1` showed untrue, or that depended on the R1 LB-2
unit's environment being closed, is quoted below verbatim with its disposition.
*Withdrawn* means the claim is no longer made. *Narrowed* means it is true only
in the stated, smaller scope. Text outside the sections listed in §0-R2 is
unchanged. Appendix A is unchanged.

| R1 location | R1 text (verbatim) | Disposition | Replaced by |
|---|---|---|---|
| §1 table, LB-2 row, "What it prevents" | "**All** client-derived process state: environment, loader, Python startup, cwd, descriptors, signals, rlimits, umask, seccomp, Landlock, namespaces and ancestry. The entry is created by PID 1 from root-owned unit bytes" | **narrowed**: true for client-derived state, but silent about the open manager environment, which a reader took as closed | §1 LB-2S row; §4.4.3.4 |
| §1 table, LB-3 row | "environment, loader and descriptors (setuid `AT_SECURE`, `env_reset`, `closefrom`)" | **narrowed**: client loader state only. The environment is not closed (PAM merge) | §1 LB-3 row; §4.4.4 |
| §1, conditional direction | "**Conditional direction — only if Peter Duscha decides M-9 = LB-2, M-10 = T-A in scope, D-2 = D-2a, M-11 = Pass A only, and accepts D-1 as rewritten.**" | **withdrawn** | §1: no recommendation ready; a conditional direction on LB-2S, M-14 and M-10 (revised) |
| §1, conditional direction, R4-D1-1 bullet | "The canonical policy runs in a process that the loader state of *E_c* never touched." | **narrowed**: true, but insufficient. The manager's loader state was not addressed | §1 (R2 bullet), §4.4.3.4 |
| §1 | "It is now accompanied by a separate, root-established contract for the entry's **own** environment, `rp11-entry-env/1` (§7.9)." | **withdrawn** ("root-established" meant the manager's block) | §1 (R2), §7.9 |
| §2.3 AS-6 | "A started unit receives only the manager's environment, the unit's `Environment=`, the variables systemd derives from `User=` (`USER`, `LOGNAME`, `HOME`, `SHELL`), `INVOCATION_ID` and, when an output goes to the journal, `JOURNAL_STREAM`" | **withdrawn** as a closed description. "The manager's environment" is an open, mutable set | AS-6 (rewritten); §4.4.3.1 S-1 … S-10 |
| §4.2 C-5 | "the unit's closed environment" | **withdrawn**: untrue | §4.2 C-5 (amended) |
| §4.3 stage T4 | "LB-2: PID 1 forks from unit bytes. LB-3: a setuid `execve` of `sudo`, which builds a fresh environment" | **narrowed**: neither transition produces a closed environment by itself | §4.3 T4 (amended) |
| §4.3 stage T5 | "**yes** for LB-1, LB-2 and LB-3" | **withdrawn** for LB-2 (R1 unit) and LB-3 | §4.3 T5 (amended) |
| §4.3 reassessment, loader row, LB-2 column | "do not reach. The environment comes from the unit and the manager (AS-6, PO-8)" | **withdrawn**: they reach the entry from the manager | §4.3 reassessment (LB-2S column; two manager rows added) |
| §4.3, earliest trusted component, LB-2 | "**The invocation, image and environment of the entry are all fixed by root-owned bytes. None comes from the requester.**" | **narrowed**: "none comes from the requester" stands. "Environment … fixed by root-owned bytes" is withdrawn for the unit | §4.3 LB-2S bullet |
| §4.4.3, unit paragraph | "The entry's environment check (§7.9) diagnoses any added variable." | **narrowed**: diagnosis after the loader has acted. It was read as covering drop-in additions | §4.4.3.4, §4.4.3.5, §7.9 |
| §4.4.3, criterion "native-loader timing" | "**prevents.** PID 1 creates the entry. No client-derived variable exists in its environment (AS-6, PO-8)" | **withdrawn** as a prevention claim | §4.4.3.6 |
| §4.4.3, criterion "other process state" | "**prevents.** Working directory, descriptors, signals, rlimits, umask, seccomp, Landlock, namespaces and cgroup all come from the manager and the unit." | **narrowed**: prevents client-derived state only. Manager-derived state is trusted root input (R-10) | §4.4.3.6; R-10 |
| §4.4.3, criterion "TOCTOU" | "the unit, polkit rule, pass configuration and bootstrap are root-owned and fixed before the pass." | **narrowed**: the files are, but the loaded configuration and the manager's defaults can change (S-5, S-7) | §4.4.3.6 |
| §4.4.3, the unit's `ExecStart=` and `Environment=` lines | "ExecStart=/usr/bin/python3.12 -I -S /usr/local/libexec/freedom-blades-rp11/rp11_entry.py run --pass A" | **withdrawn** as the conditional direction's unit. It is kept as the LB-2 (R1) form in §4.4.3.3 | §4.4.3.4 (LB-2S unit) |
| §4.4.5, comparison | "\| prevents loader state reaching the entry \| **no** \| yes (PO-9) \| **yes** (PO-8) \| yes (PO-10) \|" | **withdrawn** for LB-2 and LB-3 | §4.4.5 (amended) |
| §4.4.7 | "Prevention needs an image that ignores the loader (LB-1: a new build dependency), or a transition established by root (LB-3), or a process that does not descend from the client (LB-2)." | **narrowed**: only the first closes the entry's environment. The other two are not enough on their own | §4.4.7 (R2 paragraph) |
| §5.3 D-1, issue clause | "It causes only the reviewed entry to run, and the entry's image, argv, environment and process state are fixed by root-owned configuration and not derived from the client." | **withdrawn**, bracket `[M-9 = LB-2]` included | §5.3 issue clause (amended) |
| §6.9 R-8 | "PID 1, polkit, the manager's environment, `/etc/ld.so.preload`, the standard library and `/usr/bin/python3.12`" | **withdrawn** for "the manager's environment", which is T-A state | R-8 (amended); R-10 |
| §7.9 | "**The environment is established by the M-9 boundary, not by the entry.**" | **withdrawn** for LB-2 and LB-3. Under LB-2S and LB-1 the environment is `rp11-launch`'s literal | §7.9 (rewritten) |
| §7.9 table, `LANG` row | "the manager's locale, if the installed systemd passes it (PO-8)" | **withdrawn**: the table described an open block | §7.9 (rewritten) |
| §9, boundary files | "\| LB-2 \| `infra/systemd/rp11-capture-pass-a.service` and `infra/polkit/50-freedom-blades-rp11.rules` (§4.4.3); a schema for `pass-a.json` in `entry_environment.py` or a sibling module \|" | **replaced** | §9 LB-2S row |
| §10.3 T-B1 | "`Environment=` exactly `PATH=/usr/bin` and `LC_ALL=C`" | **withdrawn**: LB-2S sets no `Environment=` | T-B1 (amended) |
| §13, M-9 | "**LB-2**. It is the only option that prevents *all* client-derived process state. It needs H-1" | **withdrawn** as the conditional direction | §13 M-9 (amended), M-14 (new) |
| §14 PO-8 | "Its environment is exactly the manager's plus `Environment=`, the `User=`-derived variables, `INVOCATION_ID` and `JOURNAL_STREAM` (AS-6)." | **withdrawn** as a closed description | PO-8 (revised); PO-14 |
