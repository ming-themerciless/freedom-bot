# Independent review — fresh R-5 assignment R1

Date: 2026-10-02

Reviewer: Codex

Reviewed inputs:

- [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment.md), SHA-256 `f4f4e1a3e48d6968215596432af6a08218f91dbf9b60c458fd50f969cfa89ff7`;
- [`phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md`](phase-5-0-p5-r5-rp11-fresh-independent-rebuild-assignment-r1-handback.md), SHA-256 `0946d03b7308ba46d7c5a7ddb4f1b794e180ee810c3aa9c1e64bd74b1a0e5e8e`; and
- the controlling R1 prompt, active handover, current status, implementation-plan requirements and disposable-server restriction.

Disposition: **one Important finding; do not accept the assignment for execution yet.** R-5 remains stopped, Blocking, unaccepted and unauthorized. No remote, build, test, verifier, provisioning, synchronization, commit or push action was performed.

## Finding

### `FRESH-A1-R2-1` — Important — required per-step timestamps cannot be produced by the authorized procedure

The handback contract requires “start and end UTC timestamps for the whole run and for each step” (§10 item 2). The procedure records `date -u` only in S2.1 and S11.7. Steps 1, 3, 4a–4d, 5, 6/7, 8, 9 and 10 have no authorized start or end timestamp command.

This cannot be repaired by executor discretion: §7 authorizes only the blocks and synchronization command written in §6, and says any other command or any block-text change beyond the listed substitutions is an unexpected command and a HARD STOP. The executor therefore cannot both obey the procedure and satisfy the handback contract.

Required remediation: either add explicitly labelled UTC timestamp capture around every required step/step-part and include those commands in the authorized blocks, or narrow §10 item 2 to timestamps that the procedure actually records. The chosen contract must be mechanically unambiguous before acceptance.

## Earlier finding dispositions

- `FRESH-A1-R1-1`: remediated. Checked command statuses are captured before later display/logging actions, and pytest success is supplemented by an exact JUnit count gate.
- `FRESH-A1-R1-2`: remediated. Expected-absence observations now return zero for the accepted state and distinct nonzero statuses for violations.
- `FRESH-A1-R1-3`: remediated. The unaccepted archive transport was removed in favor of the documented secret-excluding synchronization form, with the fresh destination and post-transfer byte checks.
- `FRESH-A1-R1-4`: remediated. A bubblewrap version-only difference cannot qualify as HA-3; this run must qualify through measured HA-1 or HA-2 variation.
- `FRESH-A1-R1-5`: remediated for the R1 drafting task. The handback records complete reading of the mandatory sources and preserves the earlier shortfall as history.

## Additional review notes

The accepted baseline inputs remain stated as manifest version 30, aggregate digest `28a4f4c2b7596e9042f6b12a34f5684b3499a3fafd997e306fe25f6798e8a526`, and the 5,120-byte diagnostic fixture with SHA-256 `b77f92dcdcf899c5459fec606f16dc325ed5329516cbab5faea86b479992905b`. The draft preserves exact-byte equality as the only `cc1check.py` PASS route, the one-run/no-retry rule, and the requirement for Peter Duscha to accept the assignment and name an independent executor before any host action.

No claim is made that R-5 passed or that RP-11, PO-9, PO-14, D9-3 or Package 5.0 is complete. `plan.is_executable` remains `False`.
