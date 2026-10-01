# Claude prompt — implement the accepted zero-ret static launcher and independent decoder

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-I7`

Date: 2026-10-01

Assignee: Claude, implementing agent

Independent reviewer: Codex

State: **assigned repository implementation and repository-host evidence only.**
Stop after the implementation handback for independent Codex review.

## 1. Objective

Implement I-7 from the accepted D2-R2 static-launcher design, including the
zero-`ret` image, its reproducible build boundary, the independently
implemented XD decoder, T-L1 … T-L12, and the repository evidence needed for
later D9-1 … D9-4 work.

The controlling design is
[`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md`](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md).
Its accepted LD-7, LD-8 and LD-9 decisions are normative. Where this prompt is
silent, implement that proposal exactly; do not redesign it by convenience.

## 2. Controlling inputs

Read completely before editing:

* `.agents/AGENTS.md`;
* the implementation-plan reading map, §0, §13, §16, §17 and §20;
* `docs/review/Handover information`;
* the accepted D2 proposal;
* the
  [D2-R2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md);
* the
  [D2-R2 acceptance and LD-9 decision](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md);
* the controlling R2 launcher contract cited by the D2 proposal; and
* the current review-manifest and evidence-harness contracts before changing
  any covered-source or generated-artifact input.

Inspect and preserve unrelated worktree changes. Stop on a conflict between
the accepted design and the current source or manifest rather than silently
choosing one.

## 3. Required implementation

Implement the complete accepted I-7 repository slice:

1. `infra/rp11-launch/` source and build inputs described by proposal §5.2,
   including `_start`, `rp11_main`, `select.h`, the linker script, build script,
   toolchain lock, build-root manifest, expected digests and committed listing.
2. The selected zero-`ret` form from the first build: exactly `_start` and
   `rp11_main`; one direct entry `jmp`; no `call`, `ret`, indirect transfer,
   compiler-created executable helper or out-of-line selection function.
3. The exact state machine, literals, diagnostics, statuses, bounds, signal
   handling, syscall inventory, stack discipline, input discipline and
   fail-closed behavior in proposal §§5.4–5.10 and §5.14.
4. The pinned build root and reproducibility inputs in §§5.3.1–5.3.8. IC-1
   must trace every class-B process and pass. Record HA-1 … HA-5 without
   claiming they are eliminated.
5. T-L1 … T-L10 exactly as specified, including the narrowed T-L8 and the
   listing-based control-transfer verifier. T-L10 is not evidence unless its
   T-L11 precondition holds on the same digests.
6. XD and its spelling table under §5.15. XD must use its own ELF reader and
   closed encoding table written from cited Intel and AMD manual sections; it
   must not use or derive from binutils code, tables, libraries, output or the
   committed listing.
7. T-L11 exact stream agreement and T-L12's complete positive and negative
   corpus. Every XD-5 failure class and every forbidden encoding named by
   XD-10 must be covered.
8. Repository tests, manifest coverage and deterministic generated artifacts
   required by the existing evidence-harness contract. Advance versions only
   where the contract requires it and regenerate only through the documented
   non-executing path.

If the selected C form cannot satisfy XD, T-L11, T-L10 and HR-1 … HR-6, apply
FA-1 and then FA-3 exactly as proposal §5.14.5 permits. Do not introduce a
return-based fallback. If no zero-`ret` form passes, stop and recommend
withdrawal of LB-2S.

## 4. Build and evidence rules

Repository-host compilation, assembly, linking, decoding, verifier execution
and tests are authorized for this implementation. A pinned toolchain or build
root may be downloaded into an isolated repository or scratch location when
the accepted design requires it. Record exact sources, versions and digests.
Do not install or replace host packages, alter system configuration, or treat
the ambient host toolchain as a substitute for the pinned root.

Produce R-1 … R-4 and IC-1 where the accepted design assigns them to the
implementer. R-5 must be performed later by a party other than Claude in a
separately provisioned environment; Claude may implement and test its
mechanism but must not claim the independent rebuild complete.

Likewise, implement the inputs and tooling for D9-2, but do not perform or
claim XD-9 or XD-11 on Codex's behalf. Under decided LD-9 option (i), Codex
must later decode the actual `.text` independently using its own decoder or a
byte-by-byte manual derivation prepared without reading XD's table.

Any unexplained build, listing, decoder, stream, table, digest, trace or
reproducibility difference is a hard stop. Never resolve a disagreement by
preferring `objdump`, XD or T-L10.

## 5. Required verification

Run the narrow tests first, then all repository-local suites affected by the
new source and manifest coverage. At minimum report:

* T-L1 … T-L12 individually, with exact results and digests;
* XD's self-test corpus and all injected failure classes;
* IC-1 and its trace summary;
* deterministic rebuild/listing checks available on the implementation host;
* focused evidence-harness tests and all structural no-execution guards;
* the complete `tests/phase_5_0_evidence` suite under its documented local
  restrictions; and
* `git diff --check`, relevant syntax/type checks, and generated-artifact
  byte equality.

Do not cite a carried-over suite figure. Do not claim R-5, D9-1, D9-2, D9-4,
PO-9, PO-14, PO-17 or PO-18 complete merely because repository tests pass.

## 6. Restrictions

No SSH, rsync, synchronization, `oracle-test` access, host inspection outside
the repository implementation needs, `sudo`, package installation, system
configuration, service operation, database access, provisioning, installation
of `rp11-launch`, H-1, H-2, controlled write, reboot, evidence band, harness
`--execute`, real participant, real capture root, operational path,
protected-artifact access, secrets scan, commit or push is authorized.

Do not wire RP-11, change the operational authorization draft, run D9-5 or
PO-16, discharge PO-14, or make either pass executable. Do not weaken LD-7,
LD-8, LD-9, XD-1 … XD-11, the CT/RI rules, evidence separation or any existing
fail-closed gate.

PO-9 and PO-14 remain open; RP-11 remains unwired and unmet;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## 7. Handback and review gate

Create
`phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md`.
Include:

* requirements implemented and exact files changed;
* toolchain/build-root provenance, versions and digests;
* manifest and generated-artifact version/digest changes;
* exact build outputs and T-L1 … T-L12 results;
* IC-1 evidence and the status of R-1 … R-5;
* the complete instruction/syscall/function/stack summary required for
  HR-1 … HR-6;
* security implications and the remaining TD-1 … TD-4 trust;
* exact tests and results, plus every check not run;
* rollback/recovery instructions;
* unresolved assumptions, discrepancies and proof obligations; and
* focused questions for Codex, especially XD-9, XD-11, T-L11/T-L10 binding,
  zero-`ret` completeness and LD-8's R-5 condition.

Update only the concise current-state pointers needed to return the work.
Do not amend prior assignments, handbacks, reviews, decisions, snapshots or
archives. Stop after the handback. Codex independently reviews the exact
returned bytes; Peter Duscha alone accepts the implementation or authorizes
later host and operational work.
