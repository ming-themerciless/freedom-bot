# Claude handback — LB-2S static-launcher design

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D2`

Date: 2026-09-29

Assignment:
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-claude-prompt.md)
(SHA-256 `4a3176dfbdb32eed9aad60e27aeddcfa250879c6c414cde93d88e6aabfea53ba`)

Proposal (new):
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
(SHA-256 `adc114bf795985ce1af5c90e3b9d8e7ca1cb012e1551e6eab590cfb8f28d8093`,
954 lines)

State: **returned as documentation only, for mandatory independent Codex
review. Claude has stopped.** Nothing is accepted, decided, built or
implemented. PO-9 and PO-14 remain open.

## 1. Summary

* **A design is selected, not an impossibility result.** `D-S1` is a
  freestanding C11 image with a hand-written x86-64 `_start`, inline `syscall`
  instructions and **no C library, runtime, loader, start-up file or
  `libgcc`** (proposal §4.4, §5).
* **Its PO-9 argument is structural** (proposal §6.1):
  * the kernel starts an `ET_EXEC` image with no `PT_INTERP` directly at
    `e_entry` (AD-3);
  * `e_entry` is the reviewed `_start`, and the image holds no constructor,
    TLS, relocation or dynamic section (BI-1 … BI-5);
  * the complete disassembly has no indirect branch, so every instruction that
    can run is in one reviewed listing (BI-6); and
  * that listing is tied to the installed file by reproducibility and digest
    (D9-3, D9-4).

  No test outcome is a premise. The hostile-environment experiment only
  corroborates (§5.12.4).
* **The toolchain is not trusted for correctness.** The listing is reviewed,
  and the pin exists only so that anyone can regenerate the same bytes
  (§5.3.1).
* **Every candidate the assignment named was assessed** (§4.3). musl, Rust
  `no_std`, `nolibc` and pure assembly are credible, but none is selected;
  pure assembly is the fallback. Rust `std`, Go, glibc-static and
  distribution static utilities are rejected. §4.5 states when the result
  would reverse into withdrawal of LB-2S.
* **Seven findings** (FD-1 … FD-7, proposal §0). Four change the design:
  * **FD-1:** a dual-mode image would let the untrusted block select its
    behaviour. The image therefore has one mode, and LB-1 loses its image
    (V-5);
  * **FD-2:** C-library signal wrappers cannot reset signals 32 … 34, so a raw
    system call is required;
  * **FD-3:** `binfmt_misc` is consulted before the ELF handler, so a matching
    root registration would run code before `_start`. This adds **PO-17**; and
  * **FD-7:** closed standard descriptors could mix evidence streams, so a
    stdio check is added (V-1).
* **Nothing is discharged.** PO-9 needs D9-1 … D9-4, produced under later
  authority. PO-14 is untouched. LB-2S stays conditional as decided.

## 2. Requirement → proposal section map

| Assignment requirement | Proposal sections |
|---|---|
| §2 controlling inputs read; retained constraints preserved | header; §1; §3 (K-1 … K-9); §7 (every refinement of R2 listed) |
| §3 compare approaches: freestanding/syscall-only, musl, Rust `no_std`, simpler approaches | §4.2, §4.3 (C-1, C-1A, C-1N, C-2, C-3, C-3S, C-4, C-5, C-6, C-7) |
| §3 per-candidate criteria (pre-entry execution, environment/auxv/locale/tunable/NSS/iconv/configuration reads, dynamic loading, architecture and ABI, binary format, toolchain, reproducibility, source-to-binary review, installed-digest binding, maintenance and supply chain, how PO-9 is proved) | §4.1; §4.3 (tables for C-1 and C-2, and a paragraph per other candidate) |
| select only if the evidence supports it | §4.4; §4.5 |
| item 1: language/runtime and the pre-entry argument | §5.1; §6.1 |
| item 2: source and build-input boundary | §5.2 |
| item 3: pinned toolchain and reproducible build | §5.3.1 … §5.3.6 |
| item 4: architecture and kernel ABI | §5.4 |
| item 5: argv exactly `--pass A` | §5.5 |
| item 6: `envp`: one grammar-valid `INVOCATION_ID`, nothing else copied, duplicates and malformed entries | §5.6 |
| item 7: descriptors, signals, mask, umask, working directory, in order, with failure semantics | §5.7 |
| item 8: the literal `execve` | §5.8 |
| item 9: fixed exit statuses and non-sensitive diagnostics | §5.9 |
| item 10: partial failure, interruption, unexpected kernel results | §5.10 |
| item 11: manifest, pass configuration, H-1 and H-2 binding | §5.11 |
| item 12: repository tests, binary inspection, reproducibility, later hostile experiment | §5.12.1 … §5.12.4 |
| item 13: rollback and replacement | §5.13 |
| §4: separate evidence classes; PO-14 not discharged | §6.2, §6.3; K-9; §10 |
| §4: clean output is corroboration; the static label is not proof; no glibc-static; no unknown runtime; no dynamic cleansing helper | FD-4; §4.3 (C-3S, C-5, C-6); §5.12.4 "What it cannot show"; §6.1 |
| §4: impossibility result if unsupported | §0 "Why no impossibility result"; §4.5 |
| §5: deliverables and pointers | this handback; §4 below |
| §6: scope and prohibitions | §7 below; proposal §1, §11 |

## 3. Requirements implemented

**Documentation only.** No source, build script, toolchain file, test,
binary, manifest, generated artifact, systemd or polkit file, configuration,
migration, dependency or executable content was added. The C, assembly,
linker-script and flag text in the proposal is specification inside a design
document. It is not a repository file.

## 4. Files changed

| File | Change |
|---|---|
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md` | **new**: the design |
| `docs/review/phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-handback.md` | **new**: this handback |
| `docs/review/Handover information` | title, and a concise *Return state* section. The accepted decisions, assignment, restrictions and archive links are unchanged |
| `docs/project-management/status.md` | a new current-status block. The previous block is relabelled *Superseded current status*, with its text unchanged |
| `docs/implementation-plan.md` §20 | a new current action (Codex reviews). The previous current action is relabelled *Superseded current action*, with its text unchanged |
| `docs/operations/disposable-test-server.md` | a *Restriction at LB-2S static-launcher design return* banner. Earlier banners are unchanged |

**Not changed:** the R2 proposal (still `f6405cd9…12f70b`), every earlier
handback, review, decision and assignment, every snapshot and archive, D-1,
D-2, the operational draft (still `5c6046fc…dcca7de6`), the manifest (still
version 26, `526dd446…`), every Python file, hook, test and `settings.json`.

## 5. Migrations

None.

## 6. Security implications

* **The environment-prevention claim moves into ~300 lines that can be
  reviewed completely.** Its remaining weak point is the human review of the
  listing (proposal §8). That is mitigated by size, by the absence of indirect
  branches, by mechanical checks and by two independent reviewers.
* **A new trusted-state item is named instead of hidden:** `binfmt_misc`
  registrations (FD-3, PO-17). The R2 analysis did not consider them.
* **A new build dependency with no runtime dependency.** A compiler and
  binutils are needed only to build. The installed image depends on nothing
  but the kernel's system-call ABI, so no library security update requires a
  rebuild (§5.13).
* **No environment content is recorded** anywhere in the design (K-6). The
  diagnostics are fixed literals.
* **The launcher refuses rather than degrades.** Every one of its seven
  failure classes exits without `execve`, and it has no fallback.

## 7. Commands run and results

Tools used: Bash, Read, Write, Edit. Every command was a repository read or a
documentation write.

| Command | Result |
|---|---|
| `cat`, `sed -n`, `grep` and `wc` of CLAUDE.md, AGENTS.md (complete), the plan's reading map, §0, §16 and §20, the Handover, the assignment, the decision record, Codex's R2 review, the R2 handback, and the R2 proposal (§0-R2, §1 … §4.4, §6.5, §6.8, §6.9, §7.7 … §15, Appendices A and B), the head of `status.md` and the test-server banners | read. No secret file was named or opened |
| `grep` of `docs/` and `.agents/` for architecture names; `sed -n` of the concrete plan's §1 | OD-5 and OD-6 |
| `sha256sum` of the assignment, the R2 proposal, the decision, the R2 review, the R2 handback, the operational draft and the four pointer files | as cited here and in the proposal header. The R2 proposal equals its R2 return (`f6405cd9…`) |
| `git status --short`, saved to the session scratch directory | 71 entries before this work |
| Python one-off scripts that inserted the pointer text, each asserting that its anchor occurred exactly once | applied |
| `sha256sum` and `wc -l` of the new proposal | `adc114bf…f28d8093`, 954 lines |
| `git diff --check`, whitespace, link and status checks | §8 |

**Not run, as the assignment prohibits:** any compiler, assembler, linker,
`objdump`, `readelf`, `strace`, package manager, download, test suite, hook,
loader or interpreter probe, `systemctl`, `systemd-run`, `loginctl`, `busctl`,
`sudo`, `ssh`, `rsync`, `uname` or other host inspection. No guard or tool
refusal occurred.

## 8. Documentation checks

| Check | Result |
|---|---|
| `git diff --check` over the four edited tracked files | exit 0; no whitespace error |
| `git diff --no-index --check /dev/null ⟨file⟩` for the two new files | no whitespace error printed (exit 1 only signals the difference). Trailing-space count 0 in both |
| relative-link resolution (Python, `pathlib`) over the six touched files | 330 links. 3 resolve only once URL-decoded; these are the pre-existing `%20`-encoded links to `Handover information`. **0 broken** |
| `git status --short \| wc -l` | 71 before; 73 after (the two new files). The four pointer files were already modified. Unrelated user changes were preserved |

## 9. Checks not run, and why

* **No test suite, formatter, linter or type checker.** No code changed, and
  the assignment requires none. No suite figure is cited.
* **No build, binary inspection or reproducibility check.** Prohibited. BI-1
  … BI-9 and R-1 … R-5 are specified, not performed.
* **No hostile-environment experiment.** Prohibited, and separately
  authorized later if at all.
* **No verification of AD-1 … AD-10.** Each is marked for citation. AD-1 and
  AD-2, the repository host's architecture and kernel, are unrecorded in the
  repository (OD-6).
* **No toolchain version is pinned.** Pinning needs access to the archive
  (§5.3.2).
* **Manifest not regenerated or incremented.** No covered source changed.
* **No commit or push.** Not authorized.

## 10. Configuration, deployment and rollback

* **Configuration and deployment:** none.
* **Rollback of this return:** delete the two new files, and revert the four
  pointer edits: the Handover's title and *Return state* section, the new
  `status.md` block and relabel, the new §20 action and relabel, and the new
  test-server banner.
* **Rollback of the later implementation:** proposal §5.13.

## 11. Assumptions, proof obligations, decisions and questions for Codex

**Assumptions:** AD-1 … AD-10 (proposal §2.2). AD-3, AD-4, AD-6 and AD-8
are load-bearing for PO-9 and are discharged by the D9-1 citation. AD-5 is
deliberately not relied on. AD-9 and AD-10 matter only to rejected
candidates.

**Proof obligations:**

* PO-9 now has components D9-1 … D9-5 (§6.2), and is discharged only by
  D9-1 … D9-4;
* PO-14 and PO-16 are unchanged;
* PO-17 (`binfmt_misc`) and PO-18 (architecture and kernel release) are new.

**Maintainer decisions:** LD-1 … LD-6 (proposal §9), after Codex's review.
The M-14 implementation authority, H-1, H-2 and the remaining R2 decisions are
still required.

**Questions for Codex:**

1. **Pre-entry path.** Is AD-3 right that the kernel runs no user-space code
   before `e_entry` for an `ET_EXEC` image without `PT_INTERP`? Is anything
   missing from P-1 … P-7 (proposal §6.1)? For example: the vDSO, a
   `PT_GNU_PROPERTY` action, `personality` flags, or LSM behaviour on
   `execve`.
2. **`binfmt_misc`.** Is FD-3's ordering claim (AD-4) correct? Is PO-17's
   check (no enabled registration matching the first 128 bytes, or
   `binfmt_misc` not mounted) sufficient, and is classifying a later
   registration as R-10-style root input acceptable?
3. **Structural proof.** Do BI-1 … BI-9 together exclude every way a static
   ELF can run code outside `_start`'s call tree? Is "no indirect branch"
   enough to call the listing's control-flow graph complete?
4. **Toolchain trust.** Is it sound to treat the compiler as untrusted, and
   rely on the reviewed listing plus reproducibility (FD-6, §5.3.1)? Is R-5
   (an independent rebuild in a separately provisioned environment) strong
   enough, or should LD-5 require a second, different toolchain source?
5. **Flag vectors.** Is anything missing from §5.3.3, for example a default of
   the suggested distribution's compiler that neither the flags nor BI-1 …
   BI-9 would catch?
6. **Selection logic.** Is §5.6 right to ignore malformed entries of other
   names rather than refuse them? Is treating a bare `INVOCATION_ID` (with no
   `=`) as an invalid occurrence correct?
7. **State order.** Is S-1 … S-9 the right order? In particular: dispositions
   before the mask; the new stdio check S-3; and leaving rlimits, seccomp and
   interval timers untouched under R-10.
8. **FD-1 / V-5.** Is dropping LB-1 support from the image the right
   consequence of "the block must not select behaviour"? Does it contradict
   anything in R2 that the decision record relies on?
9. **Candidate honesty.** Are musl, Rust `no_std`, `nolibc` and pure assembly
   assessed fairly (§4.3)? Are the rejections of Rust `std`, Go, glibc-static
   and distribution utilities supported? Does §4.5 state the withdrawal
   conditions completely?
10. **Evidence separation.** Does §6.2 and §6.3 keep source, build output,
    reproducibility, binary inspection, installed-host evidence, hostile
    testing and PO-14 apart? Does any sentence credit corroboration or a check
    with proof?
11. **Binding.** Is the chain in §5.11 complete, from covered source to the
    installed file? Are the H-1 and H-2 launcher facts sufficient, and correctly
    labelled as review rather than prevention?
12. **Recommendation discipline.** Is "a recommendation for the launcher
    design only, with PO-9 undischarged and LB-2S still conditional"
    consistent with assignment §4 and decision `…-R4-D1-R2-A1`?

## 12. Return state

Pointers were updated as listed in §4. **Claude has stopped.**

* **Next:** Codex independently reviews:
  * runtime start-up and the PO-9 reasoning;
  * the toolchain and reproducibility;
  * the exact system-call and state contract;
  * evidence separation;
  * the manifest and installation binding; and
  * the honesty of the recommendation.

  Peter Duscha then decides whether to accept a launcher design and whether
  to authorize a later implementation slice.
* **No implementation assignment exists.**

Throughout: PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
neither pass is executable or authorized; `plan.is_executable=False`; P5.0-R5
remains Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not
ready.
