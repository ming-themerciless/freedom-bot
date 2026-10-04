# Active handover — baseline contract accepted; fresh R-5 decision pending — 2026-10-02

This is the concise active assignment and restriction entry point. The complete
superseded R2-assignment state is preserved verbatim in
[`Handover-information-through-2026-10-01-r5-r3-acceptance.md`](Handover-information-through-2026-10-01-r5-r3-acceptance.md).

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

## R-5 history to date

Peter accepted the Antigravity-reviewed R-5 assignment and named Gemini. The
first attempt stopped on missing `bubblewrap`; Peter authorized only its
installation. The resumed run reproduced the four frozen outputs across HA-1 …
HA-3 variation, but Codex found that R-1 and R-2 were not gated by one
`enter.py build` invocation and that `cc1.v` changed without explanation.

- [R-5 assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-assignment.md)
  · [stopped R-5 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-independent-rebuild-handback.md)
  · [acceptance](project-review-2026-10-01-p5-r5-rp11-r5-assignment-acceptance.md)
  · [bubblewrap review](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-stop.md)
  · [bubblewrap authority](project-review-2026-10-01-p5-r5-rp11-r5-bwrap-install-authority.md)

**R2 (completed).** Gemini added the same-invocation R-1/R-2 manifest gate to
`enter.py build` and `ic1`, corrected the snapshot date, and withdrew the
erroneous R-5 PASS in the stopped handback.
[Prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-gemini-prompt.md)
· [handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r2-orchestration-remediation-handback.md).

**R3 (accepted).** Gemini removed the unsafe caller-supplied regex override
from `cc1check.py`; byte equality is now the only route to `PASS`, and every
non-identical pair is `HARD_STOP` with exact byte offsets, lengths and values.
Codex independently reproduced 4,019 passing repository tests, with 12
toolchain-dependent skips because no accepted local root was available, plus
clean compilation, byte-range and unreadable-input checks and `git diff
--check`. Peter Duscha accepted R3 on that recommendation.
[Prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-gemini-prompt.md)
· [handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r3-cc1-comparison-remediation-handback.md)
· [acceptance](project-review-2026-10-01-p5-r5-rp11-r5-r3-acceptance.md).

## Current action and restrictions

Peter Duscha accepted B1-R4 and the corrected B1-R3 record on Codex's
independent recommendation. `B1-R3-1` and `B1-R3-2` are Closed as remediated.
The accepted baseline contract is manifest version 30, aggregate digest
`28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`.
The diagnostic fixture remains exactly 5,120 bytes with SHA-256
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.

- [Acceptance decision](project-review-2026-10-02-p5-r5-rp11-b1-r4-acceptance.md)
- [B1-R3 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-handback.md)
- [B1-R4 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r4-verification-record-accuracy-remediation-handback.md)

The next controlled step is preparation, review and explicit acceptance of a
fresh R-5 assignment naming an independent assignee and requiring wholly fresh
disposable resources. No fresh assignment has yet been accepted.

**The acceptance decision authorizes no `sudo`, package change, host configuration,
SSH, rsync, `oracle-test`, R-5 rerun, service or database action, H-1/H-2,
PO-14 discharge, RP-11 wiring, controlled write, reboot, evidence band,
harness `--execute`, operational path, secrets scan, commit or push.**

R-5 remains stopped, Blocking and unaccepted. RP-11 remains unwired and unmet;
neither pass is executable or authorized; `plan.is_executable=False`; PO-9 and
PO-14 remain open; OD-62 G-A remains conditional; and Package 5.0 remains not
ready.

## Archives

- [Superseded B1-R3/B1-R4 current-action block](Handover-information-through-2026-10-02-r5-b1-r4-acceptance.md)
- [Superseded B1 current-action block](Handover-information-through-2026-10-01-r5-b1-reference-reproduction.md)
- [Superseded R4 current-action block](Handover-information-through-2026-10-01-r5-r4-branch-b.md)
- [Superseded R2-assignment snapshot](Handover-information-through-2026-10-01-r5-r3-acceptance.md)
- [Handover archive index](handover-archive/README.md)

