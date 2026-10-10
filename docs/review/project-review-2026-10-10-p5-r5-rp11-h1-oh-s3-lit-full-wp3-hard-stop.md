# Independent review — LIT-FULL WP-3 HARD STOP return

Date: 2026-10-10

Reviewer: Codex, independent of the Claude executor

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP3-20261009-20`

## Conclusion

**REMEDIATION REQUIRED; THE UNDERLYING HARD STOP REMAINS VALID.**

Finding counts: **0 Blocking, 2 Important, 0 Optional**.

The accepted repository sources do not establish the complete loader-free
client-side systemd and Polkit contracts required by Q3-1 through Q3-7 and
Q3-9. The WP-3 return was therefore correct not to close those questions, and
WP-4 remains unauthorized. Two documentation defects must be corrected before
the return can be accepted as complete evidence.

## Important findings

### `WP3-HS-R1` — cancellation gaps are not completely registered

The accepted WP-3 prompt, lines 120–124, requires request, response, value
encoding, completion, cancellation and failure semantics for every interface.
The interface contract addresses cancellation for DI-1 and DI-5, but its DI-2,
DI-3, DI-4 and DI-S sections do not state cancellation semantics or identify
the missing cancellation facts. `UF-05` names only the job-completion mechanism.

Impact: the unsupported-fact registry is not complete. Supplying the currently
listed facts would still leave unanswered what happens when a client wait is
cancelled or abandoned, whether an already queued mutating job continues, and
how its eventual effect and result are observed. This distinction is
load-bearing for the accepted no-silent-retry and unknown-effect rules.

Smallest sufficient correction: expand `UF-05` and every affected interface,
closure and summary entry to include client cancellation/abandonment, queued-job
fate, eventual result observation and the resulting fail-closed/unknown-effect
boundary. State cancellation treatment explicitly for all seven interfaces.
Do not invent the missing upstream behavior or answer Q6-6/Q6-7.

### `WP3-HS-R2` — the reading ledger does not establish the accepted precondition

The accepted prompt, lines 27–58, requires every item without an expressly
named subset to be read completely before the first edit, and requires the
handback to state that this occurred. Handback rows 3 and 5–19 instead say
`completely, or the sections cited in the contract`, and the handback contains
no unambiguous statement that every required read was completed as specified
before editing.

Impact: the original return does not durably establish compliance with the
reading prerequisite on which its absence claims rely.

Smallest sufficient correction: do not rewrite history or assert what the
original executor cannot now prove. A separately authorized remediation
execution must read every required source completely before its first edit and
record that fact unambiguously in a new cumulative handback. The original
handback remains historical and its ambiguous ledger is not used as evidence
for the remediated contract. If the remediation executor cannot complete the
required reads, it must return `HARD STOP` before editing the contract.

## Verified evidence

- Interface contract: 419 lines, 39,708 bytes, SHA-256
  `050254be8d42533301d24fe9df55e7ce839893b2c7a49e382310235d8816f733`.
- Original handback: 122 lines, 11,019 bytes, SHA-256
  `b7a8e3724b5c6e5ac4ca18a2b0c8b5730137e255f317be00d02d1bd84e8b1416`.
- The 41 call sites reconcile as 23/1/1/3/6/6/1.
- The contract contains 18 unsupported-fact rows and 32 citation entries.
- Required-source identities and the four return-snapshot hashes match the
  original handback.
- `git diff --check` completed cleanly.

No host, network, retained-evidence, test, formatter, package, service or
database operation was performed. This review neither accepts WP-3 nor
authorizes WP-4 or any later package.
