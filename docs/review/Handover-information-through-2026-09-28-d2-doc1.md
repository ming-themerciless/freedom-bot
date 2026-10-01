# Active handover — RP-11 policy decided; acceptance remediation required — 2026-09-28

This file is the active assignment and restriction entry point. Handover history
through 2026-09-28 is preserved verbatim in
[`Handover-information-through-2026-09-28.md`](Handover-information-through-2026-09-28.md).
Dedicated prompts, handbacks, reviews and decision records remain the durable
records of their work.

## Current state

Peter Duscha accepted **Option 1, permit the recorded unadmitted pair by
metadata only**, following Codex's independent review and recommendation.
[Decision and review record](project-review-2026-09-28-p5-r5-rp11-i1-r3-r2-and-unadmitted-pair-decision.md).

The rule is deliberately narrow. It permits exactly the staging/final names
that Pass A's final state records for one unadmitted regular file when both
names are present, share one inode at link count two and share that inode with
no other name. Neither name is opened, read, digested or admitted. Any missing
member, divergent inode, third link, cross-object alias, duplicate category,
wrong type, unexpected name, escape or incomplete comparison stops fail closed.

Codex independently re-reviewed C-P5.0-R5-RP11-I1-R3-R2 with no new Blocking
or Important finding. The descriptor-release correction reproduced at
**3348 passed, 0 skipped** both under a 1024 soft descriptor limit and at the
default limit; the generated version-24 artifacts reproduced byte-identically.
`RP11-I1-R3-2` and `RP11-I1-R3-3` are Closed as remediated.
`RP11-I1-R3-1` is Closed by the recorded Option-1 decision.

## Next required work

An independent reviewer must review the completed documentation alignment and
exact bytes without treating the policy decision as implementation acceptance:
[Alignment handback](phase-5-0-p5-r5-rp11-i1-r3-d2-option-1-documentation-alignment-handback.md).

1. operational draft SHA-256 `48bef661…`;
2. version-25 review manifest and deterministic dry-run artifacts at
   review-input digest `f63cf359…`;
3. the unchanged Option-1 behavior and updated decision provenance; and
4. the focused **774 passed, 0 skipped** and whole-package **3348 passed,
   0 skipped** results at both the 1024 and default descriptor limits.

Separately, the post-open failure leaks observed in
`PosixFilesystem.create_file` and `openat` should receive a bounded reliability
assignment. They do not reopen the repaired `DurableRecordStore` defect.

## Restrictions and gates

The documentation alignment is returned and no dependent work is authorized
until independent review. **No SSH, rsync,
network or host inspection, `sudo`, database access, provisioning, controlled
write, reboot, verifier, evidence band, harness `--execute`, real participant,
real capture root, protected-artifact access, secrets scan, commit or push is
authorized.**

The policy decision does not accept the operational draft or RP-11 mechanism.
RP-11 remains unwired and unmet; C-11 and the pinned launcher environment
remain unresolved; neither pass is executable or authorized; P5.0-R5 remains
Blocking; OD-62 G-A remains conditional; `plan.is_executable=False`; and
Package 5.0 remains not ready.

## Archives

- [Handover history through 2026-09-28](Handover-information-through-2026-09-28.md)
- [Handover archive index](handover-archive/README.md)
