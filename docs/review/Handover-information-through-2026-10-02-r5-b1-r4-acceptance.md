## Current action and restrictions

Gemini completed reference reproduction B1/B1-R1 on this repository host,
retaining the diagnostic baseline fixture `infra/rp11-launch/verify/fixtures/cc1.v.baseline`
(5,120 bytes, SHA-256 `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`).
Gemini's B1-R2 integrated the fixture into `RP11_LAUNCH_COVERED` and manifest
version 29. Codex's independent review raised two Blocking findings:
`B1-R3-1` (`ReviewManifest.build()` contained a synthetic-placeholder bypass
accepting 51-byte stubs) and `B1-R3-2` (required B1-R2 handback was missing).
Peter Duscha accepted work ID `C-P5.0-R5-RP11-I1-R3-R4-R5-B1-R3` and appointed
Gemini to execute the remediation.

- [B1 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-cc1-reference-reproduction-handback.md)
- [B1-R1 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r1-reference-reproduction-record-remediation-handback.md)
- [B1-R2 prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-gemini-prompt.md)
- [B1-R2 handback](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r2-baseline-contract-integration-remediation-handback.md)
- [Active B1-R3 remediation prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-b1-r3-baseline-contract-verification-remediation-gemini-prompt.md)

Gemini removes the synthetic-placeholder bypass completely so fixture bytes
are verified unconditionally against the exact length and SHA-256 contract,
updates shared test fixtures to load real baseline bytes, adds regression tests,
advances `MANIFEST_VERSION` to 30, files the missing B1-R2 handback, and produces
the B1-R3 handback.

**This assignment authorizes no `sudo`, package change, host configuration,
SSH, rsync, `oracle-test`, R-5 rerun, service or database action, H-1/H-2,
PO-14 discharge, RP-11 wiring, controlled write, reboot, evidence band,
harness `--execute`, operational path, secrets scan, commit or push.**

R-5 remains stopped, Blocking and unaccepted. RP-11 remains unwired and unmet;
neither pass is executable or authorized; `plan.is_executable=False`; PO-9 and
PO-14 remain open; OD-62 G-A remains conditional; and Package 5.0 remains not
ready.
