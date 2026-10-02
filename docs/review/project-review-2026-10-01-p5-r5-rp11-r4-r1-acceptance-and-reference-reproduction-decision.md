# Decision — accept R4-R1 and authorize `cc1.v` reference reproduction

Date: 2026-10-01

Decision authority: Peter Duscha

## Decision

Peter accepts Gemini's R4-R1 record correction and the corrected R4 Branch B
result on Codex's recommendation. The bounded recovery found no historical
baseline artifact, created no fixture and performed no host build. R-5 remains
stopped and unaccepted.

Peter selects Option 1: a controlled reference reproduction on the repository
host, whose currently observed facts match Claude's recorded reference facts
(`6.8.0-139-generic`, AMD EPYC-Milan, bubblewrap 0.9.0). Gemini is assigned the
bounded procedure in the linked prompt. A reproduced `cc1.v` may be retained
as the authenticated baseline only if its SHA-256 is exactly
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.
Any mismatch or changed required host fact is a mandatory stop.

This decision authorizes neither `oracle-test` access nor an R-5 rerun. A
successful reproduction authenticates baseline bytes only; comparison with a
fresh independent build and acceptance of R-5 remain separately reviewed and
authorized steps.

- [R4 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-handback.md)
- [R4-R1 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-r1-baseline-recovery-record-remediation-handback.md)
- [Reference-reproduction assignment](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-gemini-prompt.md)

