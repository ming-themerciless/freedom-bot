## Current action and restrictions

Gemini is assigned the bounded R4 recovery of Claude's historical I-7/I-7-R1
`cc1.v` bytes. A candidate is accepted only if its SHA-256 is exactly
`b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`.

- [R4 baseline-recovery prompt](phase-5-0-p5-r5-rp11-i1-r3-r4-r5-r4-cc1-baseline-recovery-gemini-prompt.md)

Gemini may create only the exact-match fixture
`infra/rp11-launch/verify/fixtures/cc1.v.baseline` and the prescribed R4
handback. If the exact bytes cannot be recovered within the prompt's
authorized sources, Gemini writes the handback and stops; a separate
maintainer decision is then required before any reference reproduction.
Success authenticates only the historical artifact: it does not explain
Gemini's differing `cc1.v` (`cdc0fe11…45f9`) and does not accept R-5. Either
result requires independent review and Peter's acceptance.

**R4 authorizes no rebuild, baseline or reference-environment reproduction,
SSH, rsync, `oracle-test` access, network access, download, `sudo`, package
action, provisioning, build-root creation, R-5 rerun, service or database
action, H-1/H-2, PO-14 discharge, RP-11 wiring, controlled write, reboot,
evidence band, harness `--execute`, operational path, protected-artifact
access, secrets scan, commit or push.**

R-5 remains stopped, Blocking and unaccepted. RP-11 remains unwired and unmet;
neither pass is executable or authorized; `plan.is_executable=False`; PO-9 and
PO-14 remain open; OD-62 G-A remains conditional; and Package 5.0 remains not
ready.
