# Claude prompt — remediate the zero-ret and independent-decoding design

Work ID: `C-P5.0-R5-RP11-I1-R3-R4-D2-R2`

Date: 2026-09-30

Assignee: Claude, remediation author

Independent reviewer: Codex

State: **assigned repository-only, documentation and read-only analysis only.**
Stop after the amended proposal and remediation handback for independent Codex
re-review.

## Objective

Apply Peter Duscha's accepted LD-7 and LD-8 decisions and remediate exactly
Blocking finding `R4-D2-R1-1` from the independent D2-R1 review:

1. make FA-2's zero-`ret` image the required initial design rather than a
   fallback;
2. preserve LD-8's accepted bound-root model and make its conditions normative;
   and
3. add an independent machine-code decoder whose decoding must agree exactly
   with the committed listing before T-L10 evidence can be accepted.

Do not implement, compile, build, inspect or test the design.

## Controlling inputs

Read completely before editing:

* `.agents/AGENTS.md`;
* the implementation-plan reading map, §0, §16, §17 and §20;
* `docs/review/Handover information`;
* [the independent review and decisions](project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md);
* [the D2-R1 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md);
* [the D2-R1 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-claude-prompt.md); and
* [the D2-R1 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r1-static-launcher-design-remediation-handback.md).

The original D2 and D2-R1 constraints, threats, evidence separation,
prohibitions and recommendation discipline remain in force except where the
accepted decisions and this prompt expressly change them.

## Required corrections

### Zero-ret form

Make the first build and every accepted installed image contain no `ret`:

* promote FA-2 into the selected design and revise the function/call structure,
  CT set, RI rules, source discipline and expected listing shape together;
* remove or supersede every recommendation that permits `ret` under RI;
* state the accepted narrowing of T-L8 precisely; and
* retain fail-closed withdrawal if no build satisfies the revised checks.

Do not silently preserve a return-based alternative. A future `ret` design
requires a new maintainer decision.

### Independent decoding

Specify a second, independently implemented decoder that consumes `.text`
bytes rather than `objdump` mnemonics or boundaries. It must:

* decode the complete `.text` byte sequence from `_start` under the closed
  instruction and transfer set;
* emit instruction starts, lengths, operands and direct targets;
* require exact agreement with every listing boundary, byte field, mnemonic,
  operand and target used by T-L10;
* fail on ambiguity, unsupported encoding, undecoded byte, overlapping decode,
  target into an instruction, or any disagreement;
* be evidence tooling, independently reviewed and version-recorded, not a
  build input; and
* be re-derived or independently exercised by Codex at D9-2 so the pinned
  binutils decoder is not a common-mode authority.

Trace the change through RI-2, BI-6, BI-10, T-L7, T-L10, P-3, P-4, D9-2,
§6.3 and §8. State exactly what remains trusted.

### LD-8 conditions

Record that IC-1 must pass, R-5 must actually vary at least one of HA-1 … HA-3
and identify it, and any unexplained difference remains a hard stop. Do not
require diverse double compilation and do not claim reproducibility proves
instruction-decoder correctness.

## Deliverables and gate

Amend the existing D2 proposal in place with a dated D2-R2 remediation note and
create
`phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md`.
Update only concise current-state pointers necessary to return the work. Do not
edit prior assignments, handbacks, reviews, decisions, snapshots or archives.

Neither deliverable may claim `R4-D2-R1-1` closed. Codex independently
re-reviews; Peter Duscha then decides.

## Prohibitions

Documentation and repository reads only. No source, build script, decoder,
test, dependency, toolchain, binary, manifest, generated artifact,
configuration, host or operational change is authorized. No compilation,
installation, download, binary inspection, verifier execution, test suite,
SSH, rsync, network or host inspection, `sudo`, database access, provisioning,
controlled write, reboot, evidence band, harness `--execute`, real participant,
real capture root, operational path, protected-artifact access, secrets scan,
commit or push is authorized.

Preserve unrelated worktree changes. A guard or tool refusal is a stop
condition and must not be routed around.

PO-9 and PO-14 remain open; RP-11 remains unwired and unmet; neither pass is
executable or authorized; `plan.is_executable=False`; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; and Package 5.0 remains not ready.
