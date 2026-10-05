# Independent re-review — `oracle-test` one-host H-1 design remediation R3

Date: 2026-10-04

Reviewer: Codex

Design author: Claude

Work ID: `C-P5.0-R5-RP11-H1-D3-R3`

Reviewed return: [D3-R3 remediation and handback](phase-5-0-p5-r5-rp11-h1-oracle-test-one-host-design-amendment-proposal.md#14-d3-r3-remediation-and-handback-d3-r3-2026-10-04).

## Outcome

Claude's **BLOCKED REMEDIATION** return is valid. I find no Blocking,
Important or Optional defect in the return itself.

`OH-H1-D3-R2-2` is remediated by GP-R3 and is ready to close. The current
design cannot remediate `OH-H1-D3-R2-1` without changing the reviewed C11 unit
and rule text and the interruption route. That finding remains open pending
the maintainer decision identified as OH-D-10. `OH-H1-D3-R1-1` and
`OH-H1-D3-2` remain open. Nothing in this review accepts or activates H-1.

## Review

The impossibility argument holds. The grant is live throughout the pass, an
uncooperative pass can end at any instant, and an unlink plus Polkit reload
triggered at that instant necessarily completes later. Event-driven cleanup
can reduce that interval but cannot make it zero. The proposal correctly
withdraws D3-R2's polling-based boundary claim instead of redefining OH-D-7.

GP-R3 completes attributable activation cleanup when evidence is unwritable.
It removes the A1-intact rule first, performs the grant post-check, then removes
the A1-intact pass configuration and attributable activation directories,
with descriptor re-verification before every removal. It writes no record and
claims no removal without durable evidence. Foreign, damaged or unverifiable
objects remain retained and escalated. The later `absent-before-removal` or
`cleared-by-boot` classification is appropriately narrower than a claimed
removal.

The `/run` boot boundary, PID-1 supervision, automatic backstop, accepted
D3-R1 publication protocol, attribution rules and separately authorized RB-1
remain intact.

## Recommendation

Peter should:

1. close `OH-H1-D3-R2-2` as remediated;
2. decide OH-D-10 as **Option A with interruption route iii-a**: grant only
   `start`, consume and PK-verify that grant in the capture unit before
   `ExecStart=`, and retain manual interruption through the executor's
   A-2-authorized root `systemctl stop`; and
3. authorize one narrow repository-only R4 remediation to adopt that decision
   into the inactive proposal, followed by independent Codex re-review.

`OH-H1-D3-R2-1`, `OH-H1-D3-R1-1` and `OH-H1-D3-2` remain open until that
successor is reviewed and accepted.

## Checks and authority boundary

I read the canonical current-state documents, R3 authority and prompt, prior
reviews and the complete D3-R3 proposal. I performed repository-local,
read-only consistency inspection. No host, network/Git retrieval, credential,
retained-path inspection, upstream research, implementation, build,
installation, H-0/H-1/H-2, activation, evidence, rollback, cleanup, test
suite, commit or push action occurred.

