# Active handover — I-7-R1 IC-1 environment remediation returned for Codex re-review — 2026-10-01

This is the concise active assignment and restriction entry point. The complete
pre-cleanup state is preserved verbatim in
[`Handover-information-through-2026-10-01-d2-r2-acceptance.md`](Handover-information-through-2026-10-01-d2-r2-acceptance.md).

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

## Active assignment

Peter Duscha accepted Codex's I-7 recommendations: D-1 is accepted, while D-2
is not accepted until the Blocking IC-1 exact-environment finding is remediated
and independently re-reviewed. Claude performed the narrow I-7-R1 repository
remediation and **has stopped**; Codex independently re-reviews it.

- [I-7 review](project-review-2026-10-01-p5-r5-rp11-i7-static-launcher-implementation.md)
- [I-7-R1 remediation prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-claude-prompt.md)
- [I-7-R1 remediation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-r1-ic1-environment-remediation-handback.md)

Returned: IC-1 now requires the exact ordered sequence of ten `execve` calls,
and each one's complete environment, as specified for the run's controlled
checkout. The four driver values are derived from `build.sh` and the pinned
driver, not taken from a trace. 368 focused IC-1 tests cover missing, changed,
extra, duplicate and malformed variables, `PWD`/`OLDPWD` at R-2 and R-4(a), and
each driver variable. The pre-remediation checker passed 42 missing and 24
changed mutations. A freshly provisioned root gives R-1 equal and R-2
unchanged. IC-1 passes at `/rp11/co` and `/rp11/alt/checkout` with outputs
byte-identical to R-2. T-L11/T-L10 pass, and every frozen digest is
unchanged. The manifest is version 28, digest `02d660c3…5abb`. One derivation
correction is disclosed for review: R1-D-1, GCC's `prune_options` drops
`-fno-pic`. R-5 is not performed.

- [I-7 implementation prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-claude-prompt.md)
- [I-7 implementation handback](phase-5-0-p5-r5-rp11-i1-r3-r4-i7-static-launcher-implementation-handback.md)
- [Accepted D2 proposal](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-static-launcher-design-proposal.md)
- [D2-R2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-d2-r2-zero-ret-decoding-remediation-handback.md)
- [Acceptance and LD-9 decision](project-review-2026-10-01-p5-r5-rp11-r4-d2-r2-acceptance.md)

## Return gate and restrictions

The remediation prompt authorized narrow repository changes, isolated toolchain
acquisition where required, local build/verifier work and repository tests. It
does not authorize R-5 on Claude's own authority, host
installation, H-1/H-2, PO-14 discharge, RP-11 wiring or an operational pass.

**No SSH, rsync, `oracle-test` access, `sudo`, package installation, system
configuration, service operation, database access, provisioning, launcher
installation, controlled write, reboot, evidence band, harness `--execute`,
real participant, real capture root, operational path, protected-artifact
access, secrets scan, commit or push is authorized.**

RP-11 remains unwired and unmet; neither pass is executable or authorized;
`plan.is_executable=False`; P5.0-R5 remains Blocking; OD-62 G-A remains
conditional; and Package 5.0 remains not ready.

## Archives

- [Pre-cleanup handover snapshot](Handover-information-through-2026-10-01-d2-r2-acceptance.md)
- [Handover archive index](handover-archive/README.md)
