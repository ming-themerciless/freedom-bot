**Current action, 2026-10-01 — Gemini performs only the bounded
[R-5 R4 `cc1.v` baseline recovery](review/phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-gemini-prompt.md):
recover Claude's historical I-7/I-7-R1 `cc1.v` bytes and accept a candidate
only if its SHA-256 is exactly
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.
R4 authorizes no rebuild, baseline reproduction, SSH, `oracle-test`, download,
provisioning or R-5 rerun. If the exact bytes are not recovered, Gemini hands
back and stops. Success authenticates only the historical artifact; it does not
explain Gemini's differing `cc1.v` or accept R-5. Either result requires
independent review and Peter's acceptance.**
