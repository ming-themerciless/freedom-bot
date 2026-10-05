# Handback — static-launcher H-1 installed-host evidence assignment preparation

Work ID: `C-P5.0-R5-RP11-H1-A1`  
Date: 2026-10-04  
Author: Claude  
Independent reviewer: Codex  
Decision owner: Peter Duscha

Assignment:
[`phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-claude-prompt.md`](phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-claude-prompt.md)
(SHA-256 `f07d0228122fd1e59c5cc5e6bc91163caf2a2572a46e3ba0271204f43e2dcaaa`, 8,662 bytes)  
Authority:
[`project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation-authority.md`](project-review-2026-10-04-p5-r5-rp11-h1-assignment-preparation-authority.md)
(SHA-256 `6f4f7497972e83d776389a9d2e781d5d62c79ee602ae6c89bab5e8ae5bdb682a`)

## 0. Outcome

**BLOCKED PREPARATION.** The repository is not ready for an exact, safely
executable H-1 assignment. **No H-1 assignment was written**, and
`docs/review/phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment.md`
does not exist. No Gemini invocation is issued, because nothing exists to
invoke.

There are three kinds of block, and each one is enough on its own:

1. **Four of the five H-1 inputs do not exist in any form.** These are the
   unit, the polkit rule, the bootstrap and the pass configuration, together
   with its schema and its `entry_environment` dependency. They are the
   output of the unimplemented R2 slice I-6, which in turn depends on
   decisions that have not been made (M-12, D-2, M-11, D-1, MD-C11, and the
   maintainer input `⟨MI.operator_account⟩`).
2. **The fifth input, the launcher image, has no defined installation
   source.** Its expected bytes are fully bound: `expected.sha256`, manifest
   v31 and the accepted R5 record agree on
   `04218ed2…2668572`. But no reviewed decision says where H-1 obtains those
   bytes. The only known copy is retained R5 evidence on `oracle-test`, which
   is not an installation source and is not the target host.
3. **The H-1 target, the procedure and the evidence contract are
   unspecified.** No repository record identifies the "repository host" on
   which the accepted designs place H-1. There are no install paths or modes
   for four of the files, no polkit install path, no parent-directory
   requirements, no install order, atomicity rule or failure handling, no H-1
   record schema, and no version-specific citations (D9-1, PO-8, PO-11,
   PO-12, PO-14, PO-15). Several of these need host facts that only a
   separately authorized read-only step can supply.

§5 gives the prerequisite sequence and the bounded successor assignments.

---

## 1. Requirements examined and governing sections

| Source | Sections read | Used for |
|---|---|---|
| `.agents/AGENTS.md` | complete | gate discipline, secrets, Gemini invocation rule, handoff contents |
| `docs/implementation-plan.md` | reading map, §0, §16, §20 | current action, review checkpoints, §16.3 report |
| `docs/review/Handover information` | complete | active restriction: repository-only; no host, implementation or H-1 execution authority |
| Preparation authority (above) | complete | boundary |
| `project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass-acceptance.md` (SHA-256 `e8157a16…98adbe6`) | complete | D9-3 Complete; `P5.0-R5`, PO-9, PO-14, D9-4 and H-1 open |
| `project-review-2026-10-04-p5-r5-rp11-fresh-r5-pass.md` | complete | normative output digests; retained-evidence status |
| `phase-5-0-p5-r5-rp11-fresh-independent-rebuild-r5-handback.md` (SHA-256 `6e94b7cb…1afb2c`, which equals the value Codex reviewed) | S11 digests, §13–§16 | the only recorded image copy is at `oracle-test:/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/rp11-launch` |
| D2 design (SHA-256 `4859ab4e…366174`) | header, §0–§3, §5.4–§5.13, §6, §8–§11 | launcher facts, H-1 record content (§5.11), D9-1 … D9-5 (§6.2), evidence classes (§6.3), rollback (§5.13) |
| C11/R2 contract (SHA-256 `f6405cd9…12f70b`, equal to the value D2 cites) | §4.4.3.1–§4.4.3.7, §6.5, §7.9, §9, §11–§15 | unit and polkit text, five-file H-1, H-1 record (§4.4.3.7), slices (§12), decisions (§13), PO-8 … PO-16 (§14) |
| `project-review-2026-09-29-p5-r5-rp11-r4-d1-r2-launch-boundary-decision.md` | complete | M-14 design only; M-9 LB-2S **conditional**; M-10; D-1, D-2 and MD-C11 **not** decided |
| `project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md` | complete | LD-7 … LD-9 |
| `project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md` | complete | XD-11 332/332, XD-9 pass, HR-1 … HR-6 supported |
| `project-review-2026-10-01-p5-r5-rp11-i7-r1-acceptance.md` | complete | I-7-R1 accepted; manifest v28 at that time |
| D1-R2 review and handback; D2-R2, I-7 and I-7-R1 handbacks | H-1, PO-, D9- and install references | none claims D9-1, D9-4, PO-14, PO-17 or PO-18 |
| `phase-5-0-evidence-harness-review-manifest.json` (v31, SHA-256 `b9f03a47…66b17a`) | `rp11_launch` section | review input only; `installed: false`, `wired: false` |
| `phase-5-0-evidence-harness-concrete-plan.md` | searched | contains no RP-11 or H-1 installation content |
| `infra/rp11-launch/**`, `tools/phase_5_0_evidence/rp11_launch.py`, `tests/test_rp11_launch_source.py` | inventory and the relevant parts | binding code; T-L2 half owed by I-6 |

**Citation note.** The assignment cites D2 "§§5.11, 6.2, 6.3 and 12". D2 has
no §12. I read D2 §5.12 (tests, inspection, reproducibility) and C11 §12
(rollout and rollback), and treated both as intended.

**Naming collisions kept distinct.** Static-launcher **H-1** is not any
finding or RAID entry with that name. Static-launcher **R-5** (accepted; D9-3
Complete) is not package RAID item **`P5.0-R5`**, which remains Blocking. R2
decision **D-2** (the A1-12 text, undecided) is not I-7 discrepancy **D-2**
(the IC-1 environment, accepted as implemented). R2 decision **D-1** (the
draft amendment) is not I-7 discrepancy **D-1**.

---

## 2. Mandatory readiness audit

### 2.1 The five H-1 inputs (audit item 1)

Verified from repository bytes at `HEAD`
`236872647f3edd5fed5c7f14512518e13eeb8f07`, working tree included, and
across Git history on all refs.

| Input | Expected path (C11 §4.4.3.4, §9) | State | Evidence |
|---|---|---|---|
| systemd unit | `infra/systemd/rp11-capture-pass-a.service` | **absent** | `infra/systemd/` holds only the three `freedom-*.service.tmpl` files. No renamed unit exists in the tracked or untracked tree, and none appears in history. The only text is the *proposed* unit in C11 §4.4.3.4, which contains the unresolved substitution `⟨MI.operator_account⟩` |
| polkit rule | `infra/polkit/50-freedom-blades-rp11.rules` | **absent** | `infra/polkit/` does not exist, and no `*.rules` file is tracked. The only text is C11 §4.4.3.4's proposal, with the same substitution |
| `rp11-launch` image | built output; installed at `/usr/local/libexec/freedom-blades-rp11/rp11-launch` | **no committed image** | `infra/rp11-launch/` holds sources, the lock, the build-root manifest, the listing, `expected.sha256`, the build root and verifiers, but no image. Its expected bytes are fully bound (§2.2) |
| bootstrap | `tools/phase_5_0_evidence/execution/rp11_entry.py`, installed at `/usr/local/libexec/freedom-blades-rp11/rp11_entry.py` | **absent** | not in `execution/`, not in history. Its dependency `execution/entry_environment.py` is also absent. `rp11_launch.py` lines 12–21 and `tests/test_rp11_launch_source.py:123,161` record that the `entry_environment` half of T-L2 is "owed by R2 slice I-6" |
| pass configuration | `/etc/freedom-blades-rp11/pass-a.json` | **absent, with no schema and no deterministic construction** | C11 §9 requires a schema "in `entry_environment.py` or a sibling module"; none exists. Its fields cannot all be computed today. `catalogue_sha256` needs I-2's catalogue, the manifest digest needs I-6's manifest increment, the unit digest needs the substituted unit bytes, and the values are maintainer inputs bound by A-2 (C11 §11) |

The C11 slices that produce these inputs are I-1 … I-6. None is implemented:
neither hook defines `evaluate`, and `guard_gate.py`, `act_catalogue.py`,
`launcher_environment.py`, `rp11_entry.py` and `entry_environment.py` are all
absent. C11 §12 makes I-6 the slice that creates the bootstrap, the
`entry_environment` module and the boundary files as repository text.

**Design status of the unit and rule text.** D2 §1 expressly leaves "the unit
text, polkit rule and bootstrap" outside its scope. C11 is a proposal: its
§0-R2 and §13 state "No recommendation is ready", and the launch-boundary
decision selected LB-2S only **conditionally**. So **no accepted design
fixes the unit and rule bytes.** C11's text is reviewed proposal text, not
accepted repository input.

### 2.2 Launcher bytes and their binding (audit item 2)

The expected bytes are bound consistently. All of the following were
recomputed locally from repository bytes:

| Binding | Value | Result |
|---|---|---|
| `infra/rp11-launch/expected.sha256`, `rp11-launch` row | `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572` | — |
| manifest v31 `rp11_launch.expected_sha256.image` | same | equal |
| manifest listing, map and `launch.s` vs `expected.sha256` | `8c1fedee…cd188`, `5a8b0580…bc34d`, `b37280d5…27706` | all equal |
| committed listing file digest vs manifest | `8c1fedee…cd188` | equal |
| `toolchain.lock` and `build-root.manifest` file digests vs manifest | `f704c0f4…63d6`, `f08ba9de…e76f` | equal |
| accepted R5 S11 image digest | `04218ed2…2668572` | equal (handback line 251) |
| I-7 Codex XD-11 image | `04218ed2…2668572` | equal |
| `expected.sha256` file digest | `6e87a54207f7f7aa3392fcd61f2f1c3303c0c7823fb1ef746dd28f5527a83625` | recorded for later binding |

**Not ready: the installation source.** No repository copy of the image
exists. The only recorded copy is retained R5 evidence at
`oracle-test:/var/tmp/p5-r5-fresh-20261004T110421Z-b9e8f92d-work/co-r2/build-out/rp11-launch`.
It is retained evidence pending Peter's cleanup decision, and it is on the
disposable server, which D2 OD-5 and C11 §12 say is **not** the H-1 target.
Using it would turn evidence into an installation source without a decision,
which the assignment forbids. A SHA-256 match would authenticate the bytes
from any source. **Which source H-1 uses, and how the bytes reach the target,
is a maintainer decision (U-4).**

**D9-2 has no formal disposition.** The evidence exists: Codex's I-7 review
records an independent XD-11 decode with 332/332 agreement (decoder
`48594e41…c04e3e`, stream `eb9c584a…500b1a`), XD-9 passing, T-L11 → T-L10
binding, and support for HR-1 … HR-6. I-7-R1 was then accepted. However, no
record declares **D9-2 Complete** in the way the R5 acceptance declares D9-3
Complete. D2 §5.11 requires the H-1 record to carry "the record of Codex's
independently prepared D9-2 decoding under XD-11". That decoder and stream
were scratch files outside the repository, and only their digests are
recorded. A documentation-only disposition is needed (U-5).

### 2.3 D9-1 for the prospective kernel (audit item 3)

**Not complete, and not startable.** D9-1 cites the installed kernel series'
`fs/binfmt_elf.c` and `fs/exec.c`, `binfmt_misc` ordering, the x86-64 process
entry ABI, the no-handler `EINTR` behaviour, `kernel/signal.c` forced signals
and `arch/x86/entry` syscall return and restart, for AD-3, AD-4, AD-6, AD-8,
AD-11 and AD-12 (D2 §2.2, §2.3, §6.2). It needs the target's kernel release
(D2 §6.2: "it needs the kernel release, which is PO-18"). D2 OD-6 records that
no repository document gives the repository host's architecture or kernel.
The order must therefore be: a **read-only host-facts step** (§5, S-E), then a
**citation record** for that series (S-F), and only then H-1. AD-13 is not
load-bearing. AE-1 … AE-5 belong to D9-5, not to H-1.

### 2.4 PO-14 and PO-15 (audit item 4)

**Not cited for any version.** C11 §14 makes PO-14 load-bearing: "If refuted,
LB-2S is withdrawn for that version". It needs the installed systemd
version's source, especially the `systemd-executor` environment (AS-13) for
version 255 and later. PO-15 needs the same version's documentation and source
for the `FragmentPath`, `DropInPaths` (top-level and run-time drop-ins) and
`NeedDaemonReload` semantics. AD-7 (the `INVOCATION_ID` format) is cited with
PO-14 (D2 §2.2). The systemd version is unknown in repository bytes. **PO-14
must be cited and reviewed before H-1**, because installing the files under a
refuted PO-14 would install a withdrawn boundary.

### 2.5 PO-8, PO-11 and PO-12 (audit item 5)

**None is cited.** The H-1 record must name "the systemd, polkit, glibc and
CPython package versions against which PO-8, PO-11, PO-12 and PO-14 were
cited" (C11 §4.4.3.7):

* PO-8: S-1 … S-10 for the installed systemd;
* PO-11: polkit `action.lookup("unit")` and `("verb")` for
  `manage-units`, on the installed systemd and polkit; and
* PO-12: CPython 3.12 `-I -S` behaviour and `getpath`.

C11 §4.4.3.4's "What reaches which image" table also names `ld.so.cache` and
`/etc/ld.so.preload` as R-8 trusted inputs of `/usr/bin/python3.12`. No
glibc-version citation obligation is numbered, and that gap needs to be stated
(U-9). Every one of these needs the versions from S-E.

### 2.6 Paths, owners, modes and properties (audit item 6)

| Item | Specified? | Source or gap |
|---|---|---|
| launcher path, `root:root`, `0755`, no set-ID bit, no file capability, no write-granting ACL, parents to `/` root-owned and not group- or world-writable | **yes** | D2 §5.11, C11 §4.4.3.4 |
| unit path `/etc/systemd/system/rp11-capture-pass-a.service` | path yes; owner "root-owned"; **mode not specified** | C11 §4.4.3.4 |
| polkit rule **installed path** | **not specified anywhere** | `rules.d` and `polkit-1` appear in no RP-11 design. The conventional `/etc/polkit-1/rules.d/` and its required ownership (polkitd must be able to read it) depend on the installed polkit version (PO-11) |
| bootstrap path | path yes (M-12 proposal); **M-12 undecided; owner and mode unspecified** | C11 §9, §13 |
| pass configuration path | path yes; "root-owned, not group- or world-writable"; **exact mode unspecified** | C11 §6.5, §9 |
| parent directories `/usr/local/libexec/freedom-blades-rp11/`, `/etc/freedom-blades-rp11/` | **creation, owner and mode unspecified** for the second; the first only inherits the launcher's parent rule | — |
| `⟨MI.operator_account⟩` | **undecided maintainer input** | C11 §4.4.3.4 (used in `User=` and in the rule's `subject.user`) |
| H-1 manager properties | `FragmentPath`, `DropInPaths` (must be empty), `NeedDaemonReload` (must be `no`) | C11 §4.4.3.5, §4.4.3.7 |
| "exact effective properties" | **assigned to H-2, not H-1** | C11 §4.4.3.7 puts the effective `ExecStart`, `User`, `NoNewPrivileges`, `PAMName`, `PassEnvironment`, limit and confinement properties and the manager's `Default*=` values in H-2. H-2 "re-reports the H-1 … manager properties" and stops on "any difference from H-1". If H-1 records only the three properties, H-2 has no H-1 baseline for the rest. The assignment asks H-1 to require them. Requiring them at H-1 extends the accepted design (U-7) |
| package-version commands | **unspecified** | depend on the target's package manager (S-E) |

### 2.7 Order, atomicity, capture, failure and rollback (audit item 7)

**Rollback is specified. Nothing else is.** C11 §4.4.3.7 and §12, and D2
§5.13, specify rollback: remove the five files, run `systemctl
daemon-reload`, and touch no capture root. No design specifies:

* install order;
* atomic replacement;
* behaviour when a target path already exists;
* pre-mutation capture of prior state;
* partial-failure handling; or
* whether rollback is automatic or separately authorized.

These are new safety-relevant procedure content. Under AGENTS.md they need
design and review, not assignment-time invention. §6 outlines a proposal.

### 2.8 The H-1 record contract (audit item 8)

**Absent.** C11 §4.4.3.7 and D2 §5.11 give the record's **content**. No
design defines:

* a schema or identifier;
* canonical serialization;
* the installed destination;
* ownership and mode;
* the digest procedure; or
* the mechanical A-2 and H-2 binding.

No code exists either: no repository module builds or verifies an H-1 record,
and `rp11_launch.manifest_section` only says a later H-1 "would compare".
PO-17's matching rule is specified in words ("magic, mask and offset" over the
first 128 bytes). There is no reviewed implementation, and an executor would
otherwise have to write one ad hoc. The "no environment content" rule is
stated (C11 §4.4.3.5, D2 §5.11), but nothing enforces it mechanically.

### 2.9 Avoiding services, databases, capture roots, secrets and harness execution (audit item 9)

**In principle yes, with one material exception.** H-1's specified actions
are file installation, `daemon-reload` and read-only manager queries. They
touch no database, capture root, secret or harness. **The exception:** once
the polkit rule and unit are installed and reloaded, the named operator can
`systemctl start` the unit without further privilege. That runs `rp11-launch`
→ the bootstrap → the entry, which is the capture mechanism and acts against
`oracle-test`. H-1 itself never starts the unit, but it **creates a standing
authorization to start a pass** that lasts until H-2 and A-2, or until
rollback. Today only the bootstrap's own refusals stand between that grant and
an evidence pass: the pass configuration and manifest pins, and the unwired
entry. Whether H-1 may leave a startable unit and live polkit grant is an
authority question (U-8).

### 2.10 Unresolved decisions (audit item 10)

| # | Decision | Why it is not mine | Owner |
|---|---|---|---|
| U-1 | **Target host identity.** The designs say "the repository host" (C11 §12; D2 OD-5, OD-6), which is not `oracle-test` and is not recorded. It needs a stable identity (hostname plus a machine-identity digest), and acceptance that a non-disposable host may receive a root-installed unit and polkit grant | changes operational scope and the host on which privilege is granted | Peter |
| U-2 | **Executor and privilege mechanism** on that host: who runs as root (Gemini, Codex or Peter), and how (`sudo`, a root shell). The Gemini `/goal` form presumes an agent with root on the repository host | authority | Peter |
| U-3 | `⟨MI.operator_account⟩` | maintainer input (C11 §4.4.3.4) | Peter |
| U-4 | **Launcher installation source**: (a) commit the image as a reviewed repository artifact; (b) a separately authorized pinned rebuild on the target (the existing R-2 mechanism), verified against `expected.sha256`; (c) transfer the retained R5 output; (d) a build on another designated host plus transfer | changes the installation source and the evidence chain | Peter, on Codex review |
| U-5 | D9-2 formal completion disposition | gate disposition | Codex recommendation, then Peter |
| U-6 | C11 decisions that fix the inputs' bytes: M-12, D-2 (A1-12), M-11, D-1, MD-C11, and the remaining M-1 … M-8 to the extent I-2 … I-6 depend on them. C11 §13 order: D-2 and M-11, then D-1, then MD-C11 | architecture and authority | Peter |
| U-7 | Whether H-1 also records the effective unit properties and manager `Default*=` values as the baseline H-2 compares against (§2.6) | extends accepted evidence semantics | Peter, on Codex review |
| U-8 | Whether H-1 may leave a startable unit and live polkit grant before A-2 and H-2. Alternatives: install the rule only at A-2 or H-2; or accept the standing grant with the bootstrap's refusals as the only control | authority and evidence semantics. Moving the rule out of H-1 changes C11's five-file H-1 | Peter |
| U-9 | Whether a glibc/`ld.so` citation obligation is to be numbered for H-1 (§2.5) | evidence semantics | Peter, on Codex review |
| U-10 | Authority for the citation work to read upstream source (network or package source) | access authority | Peter |

---

## 3. Prerequisite matrix

| # | Prerequisite | Exists? | Creates it | Gate |
|---|---|---|---|---|
| P-1 | target host, executor, privilege, operator account, installation source, U-7 … U-10 | no | Peter's decision record | Codex records |
| P-2 | D9-2 disposition | evidence yes, disposition no | Codex recommendation and Peter | documentation |
| P-3 | C11 decisions M-12, D-2, M-11, D-1, MD-C11 (and the M-1 … M-8 that I-2 … I-6 need) | no | Peter | Codex review of any wording |
| P-4 | H-1 installation specification and record contract: paths, owners, modes, parents, polkit path, order, atomicity, pre-existing-path policy, capture, failure, rollback, `rp11-h1-record/1` schema and serialization, PO-17 algorithm, property set | no | Claude design (repository-only) | Codex review, then Peter acceptance |
| P-5 | repository implementation: C11 I-1 … I-6 (unit, rule, bootstrap, `entry_environment`, pass-configuration schema plus deterministic builder, manifest increment, T-L2's owed half); plus H-1 record builder and verifier and the PO-17 matcher with tests | no | Claude implementation (repository-only), one or more slices | Codex review per slice (§16.4: first database mutation does not apply; authorization and security review do) |
| P-6 | read-only host facts on the target: `uname -m`/`-r`; systemd, polkit, glibc and CPython package versions; `/usr/bin/python3.12`; PID 1 is systemd; state of every target path and parent; `binfmt_misc` mount and registrations (read-only); existing unit and drop-in collisions. No environment content | no | separately authorized read-only assignment (H-0) | Codex review |
| P-7 | version-specific citations: D9-1 (AD-3, -4, -6, -8, -11, -12), PO-8, PO-11, PO-12, PO-14 (with AD-7), PO-15, and glibc if U-9 | no | Claude citation record (repository-only, given U-10) | Codex review, then Peter. **A refuted PO-14 withdraws LB-2S and ends this sequence** |
| P-8 | installable launcher bytes on the target, digest-verified | no | per U-4 | its own review |
| P-9 | a focused commit of every reviewed H-1 input and tool | no | Peter's commit decision | controlled-path identity |
| P-10 | H-1 assignment (this task, re-run) | no | Claude | Codex review, Peter acceptance and activation |

**Dependency order:**

```text
P-1 ─┬─> P-3 ─> P-4 ─> P-5 ──┐
     │                        ├─> P-9 ─> P-10 ─> (Codex, Peter) ─> H-1
     ├─> P-6 ─> P-7 ──────────┤
     └─> P-8 (after P-6) ─────┘
P-2 ─────────────────────────────────────────────> P-10
```

P-6 can run as soon as P-1 names the host. It does not depend on P-3 … P-5.
P-7 may be started on P-6's output in parallel with P-4 and P-5. If PO-14 is
refuted, P-4 and P-5 are moot for LB-2S, so P-7's PO-14 limb can usefully go
first.

---

## 4. Files created or changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md` | **created** (this file) |

No other file was created, changed or deleted. The assignment output path
`…-h1-installed-host-evidence-assignment.md` was **not** created, so there is
no proposed assignment SHA-256 or byte length. The pre-existing uncommitted
changes are preserved untouched:

* `docs/implementation-plan.md`;
* `docs/operations/disposable-test-server.md`;
* `docs/project-management/{change-log,decision-register,status}.md`;
* `docs/review/Handover information`; and
* the two untracked authority and prompt files.

`status.md`, Handover and §20 were not updated. Recording this return is
Codex's step.

---

## 5. Proposed bounded successor assignments

Each assignment below is a proposal only. None is active.

| Order | Proposed path | Assignee | Scope | Authority needed |
|---|---|---|---|---|
| S-A | `docs/review/project-review-2026-10-XX-p5-r5-rp11-h1-prerequisite-decisions.md` | Peter (recorded by Codex) | decide U-1 … U-4 and U-6 … U-10 | maintainer decision |
| S-B | `docs/review/project-review-2026-10-XX-p5-r5-rp11-d9-2-disposition.md` | Codex recommends, Peter decides | declare D9-2 complete or name what is missing; fix the repository reference to the XD-11 record the H-1 record will cite | documentation only |
| S-C | `docs/review/phase-5-0-p5-r5-rp11-h1-installation-specification-claude-prompt.md` → `…-h1-installation-specification-proposal.md` | Claude | the P-4 design: an amendment to C11 §4.4.3.7 and D2 §5.11 for every §2.6 to §2.8 gap, written to an accepted target and source | repository documentation only |
| S-D | `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-i6-boundary-files-claude-prompt.md` (split I-1 … I-5 as Peter prefers) | Claude | P-5: C11 I-1 … I-6 under S-A's decisions; unit and rule text with the decided operator substitution; bootstrap; `entry_environment`; pass-configuration schema and a deterministic builder; manifest increment; H-1 record and PO-17 tooling per S-C; tests | repository implementation, unwired, nothing installed |
| S-E | `docs/review/phase-5-0-p5-r5-rp11-h0-target-host-facts-assignment.md` | executor named in S-A | P-6, read-only, on the target only; no `sudo`, no mutation, no environment content, no `systemctl` beyond `show`/`--version` if authorized | separate read-only host authority |
| S-F | `docs/review/phase-5-0-p5-r5-rp11-h1-version-citations-claude-prompt.md` | Claude | P-7 for S-E's recorded versions; PO-14 first | repository documentation, plus U-10 source-reading authority |
| S-G | `docs/review/phase-5-0-p5-r5-rp11-h1-launcher-staging-assignment.md` | per U-4 | P-8: produce or transfer the image to a fixed, root-owned, non-installed staging path on the target; verify `04218ed2…2668572` | build or transfer authority as decided |
| S-H | re-run of this preparation, producing `…-h1-installed-host-evidence-assignment.md` | Claude | P-10, with every input committed (P-9) | repository-only |

---

## 6. Outline of what the eventual H-1 assignment must contain

This outline is for reviewer orientation only. It is not a specification and
authorizes nothing. S-C must specify each point and have it reviewed.

* **Preflight, read-only, stop on any mismatch:**
  * host identity equals S-A;
  * the repository commit and the controlled-path identities match;
  * the authority record digests match;
  * S-B, S-E and S-F are accepted and the kernel and package versions
    re-observed equal S-E's;
  * PO-18: `x86_64` and release ≥ 5.9, compared numerically;
  * every target path is absent, and every parent exists with the specified
    owner and mode or is absent where S-C allows creation;
  * the staged image digest equals `expected.sha256`, manifest v⟨n⟩ and the
    pass configuration's `launcher_sha256`; and
  * PO-17 is evaluated before mutation, and again after it.
* **Mutation point, one marked boundary.** Install each file by
  `install -o root -g root -m ⟨mode⟩` to a temporary name in the destination
  directory, then rename with `mv -T --no-clobber`, so that no path is ever
  partially written. A pre-existing destination is a HARD STOP, never a
  replacement. Order:
  1. the launcher, the bootstrap and the pass configuration;
  2. the polkit rule, unless U-8 defers it;
  3. the unit, last; and
  4. one `systemctl daemon-reload`.

  The unit then never names an absent file. No `start`, `stop` or `enable`.
* **Post-checks, read-only:**
  * all five digests;
  * `stat` owner, mode and set-ID bits; `getfattr`/`getcap` (no
    `security.capability`); `getfacl` (no write-granting entry); and every
    parent through `/`;
  * `systemctl show -p FragmentPath -p DropInPaths -p NeedDaemonReload` (plus
    U-7's set) with exact expected values; and
  * PO-17 against the installed file's first 128 bytes.
* **Record.** A canonical `rp11-h1-record/1` written root-owned and read-only
  to S-C's path. Its SHA-256 is reported for A-2 and H-2. It contains no
  environment content.
* **Terminal states.** PASS; INVALID RUN (stopped before the mutation point,
  host unchanged); HARD STOP (any failure after it). After a HARD STOP, the
  S-C-specified rollback removes only files whose digest equals the installed
  value, then runs `daemon-reload`, and touches no capture root. Whether that
  rollback is automatic is U-8 or S-C's decision.
* **Explicit non-authority.** H-1 does not authorize H-2, D9-5, PO-16,
  starting the unit, an evidence pass, RP-11 wiring, service or database
  mutation, R4/R5 cleanup, a commit or a push.

---

## 7. Commands and checks run

All were run on the repository working tree, read-only, from
`/opt/freedom-blades/platform`.

| Command or check | Result |
|---|---|
| `test -e` on the five expected paths | all five **ABSENT** |
| `ls infra infra/systemd infra/rp11-launch infra/polkit tools/phase_5_0_evidence/execution` | as §2.1. `infra/polkit` does not exist |
| `git ls-files -co --exclude-standard` filtered for unit, rule, entry, environment, launcher and pass-configuration names | only unrelated RP-11 capture documents and `tests/phase_5_0_evidence/test_rp11_capture.py` |
| `git log --all --name-status` on the same patterns | no unit, rule, bootstrap, environment, image or pass configuration ever committed |
| `grep` for code references (`rp11_entry`, `entry_environment`, `launcher_sha256`, unit and rule names, `pass-a.json`) outside `docs/` | only the manifest, `rp11_launch.py` and `test_rp11_launch_source.py`, all recording the I-6 debt or the literal path |
| `grep 'def evaluate' .claude/hooks/*.py`; listing of `guard_gate`, `act_catalogue`, `launcher_environment` | none (I-1 … I-3 unimplemented) |
| `grep` for `rules.d`, `polkit-1` and directory modes in the RP-11 designs | none |
| `grep` for an H-1 record schema in code | none |
| Python (system `python3`, standard library `json` and `hashlib`): manifest v31 `rp11_launch` vs `expected.sha256` and committed files | image, listing, map and `launch.s` equal; listing, lock and build-root manifest file digests equal; `installed: false`, `wired: false` |
| `sha256sum` of governing inputs | as cited in §1 and §2.2 |
| `git diff --check` (tracked tree) | no output, pass |
| `git diff --no-index --check /dev/null ⟨this file⟩` | reports only the deliberate two-space Markdown line breaks in header lines 3–6 and 11, the same style as the authority record. No other whitespace issue |

## 8. Checks not run, and why

* **No test suites were run.** No code, test or configuration changed. The
  only change is one new Markdown file, so no suite exercises it. The bot,
  web and Foundry suites, and the `oracle-test` procedure, are outside this
  authority. No suite figure is claimed.
* **No formatter, linter or type checker was run.** No code changed, and
  memory records that mypy and ruff are not configured here.
* **No host fact was observed.** I ran no `uname`, package query, `systemctl`,
  `/proc` or `binfmt_misc` read on any host, including the one holding this
  checkout. Host inspection is not repository inspection, and the authority
  excludes it. Every host-dependent statement above is a stated gap, not an
  observation.
* **No upstream source was read** for D9-1 or PO-8 … PO-15. That needs U-10
  and the S-E versions.
* No SSH, rsync, `oracle-test` access, retained R4/R5 path inspection, build,
  install, `systemctl`, privilege, service, database, capture-root, secrets,
  cleanup, commit or push occurred.

## 9. Security, operational and rollback implications

* **This return:** none on any host. It adds one documentation file. Reverting
  it is deleting the file.
* **The eventual H-1** is a root mutation of a host that is not disposable
  (U-1). It creates a polkit grant that lets a named non-root account start a
  root-defined unit (U-8). PO-14's outcome can withdraw the whole boundary
  (C11 §14). Because of these three properties, the assignment must not be
  written before P-1 … P-9.
* **Rollback** is specified only at design level (§2.7). Executable rollback
  needs S-C.

## 10. Proposed reviewer focus

1. Whether any of the four absent inputs exists under a name or path my search
   missed (§7). The assignment's initial inventory and mine agree.
2. Whether "the repository host" is correctly read as the H-1 target, distinct
   from `oracle-test` (D2 OD-5; C11 §4.4.3.6, §12). Everything in U-1, U-2 and
   S-E rests on that reading.
3. The D9-2 disposition gap (U-5): whether the I-7 review and I-7-R1
   acceptance already amount to D9-2 Complete.
4. The H-1 and H-2 effective-property baseline gap (U-7) and the standing
   polkit grant (U-8). Both are semantics questions, which I have not
   resolved.
5. Whether the prerequisite order in §3 is minimal, in particular running S-E
   and S-F's PO-14 limb before the I-1 … I-6 implementation investment.

## 11. Statement of authority used

I used only the repository-documentation and read-only repository-inspection
authority of `C-P5.0-R5-RP11-H1-A1`. **No host action and no execution
authority was used.** No H-1 assignment is proposed, and no executor
invocation is issued. Static-launcher R-5 and D9-3 remain accepted and
Complete. D9-4, PO-9, PO-14, PO-17, PO-18 and H-1 remain open. RP-11 remains
unwired and unmet. Package RAID item `P5.0-R5` remains Blocking.
`plan.is_executable=False`. Package 5.0 remains not ready.

Claude stops here, pending Codex's independent review and Peter Duscha's
decisions.
