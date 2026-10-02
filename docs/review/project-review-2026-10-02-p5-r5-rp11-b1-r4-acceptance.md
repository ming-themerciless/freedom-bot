# B1-R4 acceptance and baseline-contract disposition

Date: 2026-10-02

Acceptance Authority: Peter Duscha

## Decision

Peter Duscha accepts Gemini's B1-R4 verification-record accuracy remediation
on Codex's independent recommendation. This decision accepts the corrected
B1-R3 and B1-R4 records; closes `B1-R3-1` and `B1-R3-2` as remediated; and
accepts manifest version 30 and aggregate digest
`28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`
as the current baseline-contract review input.

The diagnostic `cc1.v.baseline` contract is accepted at exactly 5,120 bytes
and SHA-256
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.
It remains diagnostic comparison evidence, not one of the four normative
launcher outputs in `expected.sha256`.

The self-referential request that the B1-R4 handback embed its own stable
SHA-256 is waived as unsatisfiable. Codex independently measured the completed
handback as
`ca2a3462ffa5c2bf8e2caf59635dd4731edc9d35ae40ffd3f00e37e194b79ed1`.

## Evidence accepted

- [B1-R2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md)
- [B1-R3 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-handback.md)
- [B1-R4 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r4-verification-record-accuracy-remediation-handback.md)

Codex independently reproduced the version-30 manifest and concrete plan
byte-for-byte, verified the fixture and normative-output hashes, reproduced
4,034 focused tests with 12 explicitly unavailable toolchain cases during the
B1-R3 review, and reproduced 309 bounded tests during the B1-R4 review.

## Boundaries and next gate

This is repository evidence and documentation acceptance only. It does not
accept an earlier R-5 run or grant execution authority. R-5 remains stopped,
Blocking and unaccepted. A fresh R-5 run requires a new, explicitly accepted
assignment naming an independent assignee and requiring fresh disposable
resources. Until then there is no SSH, `oracle-test`, provisioning, build,
package, service, database, harness `--execute`, H-1/H-2, PO-14, RP-11 wiring,
commit or push authority. `plan.is_executable=False`, RP-11 remains unwired and
unmet, PO-9 and PO-14 remain open, and Package 5.0 is not ready.
