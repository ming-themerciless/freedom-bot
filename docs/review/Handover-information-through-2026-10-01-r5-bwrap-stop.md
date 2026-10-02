# Active handover — Gemini assigned the accepted R-5 independent rebuild — 2026-10-01

This is the concise active assignment and restriction entry point. The complete
superseded re-review state is preserved verbatim in
[`Handover-information-through-2026-10-01-i7-r1-review.md`](Handover-information-through-2026-10-01-i7-r1-review.md).

## Accepted decisions

Peter Duscha accepted Codex's D2-R1 recommendations:

* **LD-7:** require FA-2's zero-`ret` image from the start. Permitting `ret`
  later requires a separate reviewed decision.
* **LD-8:** accept the bound build root plus HA-1 … HA-5, provided IC-1 passes,
  R-5 actually varies and records at least one of HA-1 … HA-3, unexplained
  differences stop, and the independent-decoding finding is resolved.
* archive the displaced Handover and status text as verbatim, hash-indexed
  snapshots.
* **LD-9:** require Codex to independently decode the actual `.text` at D9-2
  using its own decoder or byte-by-byte manual derivation prepared without
  reading XD's table. An independent exercise of XD alone is not sufficient.

- [Independent review and decision record](project-review-2026-09-30-p5-r5-rp11-r4-d2-r1-decisions.md)
- [D2-R2 acceptance and LD-9 decision](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)

## Accepted I-7-R1 decision

Peter Duscha accepts Claude's I-7-R1 remediation on Codex's independent
recommendation. `I7-R1-1` is Closed as remediated and D-2 is accepted as
implemented. Claude and Codex have stopped. The durable decision record is:

- [I-7-R1 acceptance](project-review-2026-10-01-p5-r5-rp11-i7-r1-acceptance.md)
- [I-7-R1 independent re-review](project-review-2026-10-01-p5-r5-rp11-i7-r1-ic1-environment-remediation.md)

- [I-7 review](project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md)
- [I-7-R1 remediation prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md)
- [I-7-R1 remediation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-handback.md)

Accepted: IC-1 requires the exact ordered sequence of ten `execve` calls,
and each one's complete environment, as specified for the run's controlled
checkout. The four driver values are derived from `build.sh` and the pinned
driver, not taken from a trace. 368 focused IC-1 tests cover missing, changed,
extra, duplicate and malformed variables, `PWD`/`OLDPWD` at R-2 and R-4(a), and
each driver variable. The pre-remediation checker passed 42 missing and 24
changed mutations. A freshly provisioned root gives R-1 equal and R-2
unchanged. IC-1 passes at `/rp11/co` and `/rp11/alt/checkout` with outputs
byte-identical to R-2. T-L11/T-L10 pass, and every frozen digest is
unchanged. The manifest is version 28, digest `02d660c3…5abb`. One derivation
correction R1-D-1 is accepted: GCC's `prune_options` drops
`-fno-pic`. R-5 is not performed.

- [I-7 implementation prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md)
- [I-7 implementation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)
- [Accepted D2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)
- [Acceptance and LD-9 decision](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)

## Current action and restrictions

Peter Duscha accepted the independently reviewed R-5 prompt and assigned it
to Gemini:

- [Active R-5 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-assignment.md)
- [Antigravity review](project-review-2026-10-01-p5-r5-rp11-r5-assignment-antigravity.md)
- [Acceptance](project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md)

Gemini may execute only the prompt's bounded R-5 procedure on `oracle-test`.
The run must actually vary and record at least one of HA-1 … HA-3 and stop on
every unexplained difference. Gemini writes the prescribed handback and stops;
the result then requires independent review and Peter's acceptance. No host
installation, H-1/H-2, PO-14 discharge, RP-11 wiring or operational pass is
authorized.

**Only Gemini has the assignment's bounded SSH, synchronization, target-fact,
fresh disposable `/tmp` provisioning, pinned acquisition, build, verifier and
repository-handback authority. No `sudo`, host package installation, persistent
configuration, service or database operation, launcher installation,
controlled write, reboot, evidence band, harness `--execute`, real participant,
real capture root, operational path, protected-artifact access, secrets scan,
commit or push is authorized.**

RP-11 remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## Archives

- [Superseded I-7-R1 re-review snapshot](Handover-information-through-2026-10-01-i7-r1-review.md)
- [Handover archive index](handover-archive/README.md)
