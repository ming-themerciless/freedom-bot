# Codex review — static-launcher H-1 assignment preparation

Work ID: `C-P5.0-R5-RP11-H1-A1-R1`  
Date: 2026-10-04  
Author reviewed: Claude  
Independent reviewer: Codex  
Decision owner: Peter Duscha

Reviewed handback:
[`phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md`](phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment-preparation-handback.md)
(SHA-256 `5c118cc7a38afe7cfe09d8989090dbad57fbc62a616f5e254e116318590dbc59`,
33,609 bytes).

## Disposition

**The BLOCKED PREPARATION return is complete and correct. No Blocking,
Important or Optional finding is recorded.** The repository cannot yet support
an exact, safely executable H-1 assignment. The required unit, polkit rule,
bootstrap, entry-environment implementation and pass configuration are absent;
the accepted launcher bytes have no approved installation source; the target
host and operator are undecided; version-specific proof obligations are open;
and the installation and H-1-record contracts are incomplete.

Claude correctly did not write
`phase-5-0-p5-r5-rp11-h1-installed-host-evidence-assignment.md`. The proposed
P-1 through P-10 dependency sequence and bounded S-A through S-H successors are
a sound basis for later decisions. They are proposals only and authorize
nothing.

Peter Duscha remains the acceptance and decision authority. No host,
implementation, citation-source access, launcher staging, installation, H-1,
H-2, evidence-pass, cleanup, commit or push authority is active.

## Independent verification

I independently confirmed:

* the prompt and authority digests are exactly
  `f07d0228122fd1e59c5cc5e6bc91163caf2a2572a46e3ba0271204f43e2dcaaa`
  and `6f4f7497972e83d776389a9d2e781d5d62c79ee602ae6c89bab5e8ae5bdb682a`;
  the prompt is 8,662 bytes;
* the proposed H-1 assignment does not exist;
* `infra/systemd/rp11-capture-pass-a.service`,
  `infra/polkit/50-freedom-blades-rp11.rules`,
  `infra/rp11-launch/rp11-launch`,
  `tools/phase_5_0_evidence/execution/rp11_entry.py` and
  `tools/phase_5_0_evidence/execution/entry_environment.py` are absent from the
  current working tree;
* the accepted expected launcher digest is
  `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572`,
  while the review manifest still records `installed: false` and
  `wired: false`;
* C11 §4.4.3.7 specifies H-1 record content but not a canonical schema,
  serialization, destination, mode or mechanical later binding;
* D2 §5.11 adds the launcher, D9-2, PO-17 and PO-18 record facts, but does not
  close that record-contract gap;
* C11 assigns the complete effective-unit and manager-default report to H-2,
  even though H-2 also requires comparison with H-1, confirming the U-7
  baseline ambiguity;
* PO-14 is open and load-bearing: a refutation for the installed systemd
  version withdraws LB-2S for that version; and
* the active restriction forbids every host action, so no host-dependent fact
  in the handback was treated as observed evidence.

The handback's shorthand that paths or modes are missing for four files is
read conjunctively: several destination paths are proposed, but only the
launcher has a complete path-and-mode contract. That wording does not affect
the readiness result or successor sequence.

## D9-2 recommendation

**Recommend that Peter declare D9-2 Complete in the next decision record.**
The I-7 independent review already records Codex's separately prepared decode
of the actual expected image, its frozen decoder and stream digests, complete
1,295-byte `.text` tiling, 332/332 agreement with XD and the listing, XD-9,
T-L11 to T-L10 binding, and HR-1 through HR-6 support. The later I-7-R1
acceptance closed the unrelated IC-1 defect without changing the image or
decoding evidence. No technical D9-2 work is missing; only an explicit gate
disposition and stable citation to that existing record are missing.

This recommendation does not discharge D9-1, D9-4, PO-9, PO-14, PO-17 or
PO-18 and does not make H-1 executable.

## Required decisions before successor work

The next controlled step is Peter's decision record for U-1 through U-4 and
U-6 through U-10, together with the D9-2 disposition above. In particular:

* name the H-1 target, executor, privilege mechanism and operator account;
* choose the authenticated launcher installation source;
* decide the remaining C11 design choices that determine repository bytes;
* decide whether H-1 records the full effective-property baseline later used
  by H-2;
* decide whether a startable unit and live polkit grant may exist between H-1
  and the later authorization, or require a reviewed design change;
* decide whether the glibc/loader citation receives an explicit numbered
  obligation; and
* authorize or refuse the version-specific upstream-source reading needed
  after read-only target facts exist.

The safest order remains: decisions first; then read-only host facts and the
PO-14 citation limb as early as practical; in parallel, the reviewed
installation/record design and repository-only boundary implementation; then
launcher staging and a focused controlled commit; only after all reviews and
acceptances, rerun H-1 assignment preparation.

## Checks performed

All checks were repository-local and read-only:

* `sha256sum` and `wc -c` on the prompt, authority and handback: the cited
  prompt/authority identifiers match; handback SHA-256 and length are recorded
  above;
* `test -e` on the proposed assignment and five implementation paths: all are
  absent;
* targeted `rg` over the accepted D1-R2, D2-R2, I-7 and I-7-R1 records and the
  C11/D2 designs for D9-1/D9-2, PO-14/15/17/18, H-1 record content, manager
  properties, installation paths and maintainer decisions: supports the
  dispositions above;
* review of the current manifest bindings and accepted R5 records: expected
  image identity agrees and installation/wiring remain false; and
* `git status --short` and scoped diffs: pre-existing maintainer/Claude changes
  were preserved.

No test suite was run because the reviewed return changes documentation only
and the active restriction forbids the documented remote test path. No SSH,
rsync, retained-path inspection, build, package query, upstream network read,
installation, `systemctl`, privilege, service/database, capture-root, secret,
cleanup, commit or push action occurred.

## Current state

Static-launcher R-5 remains accepted and D9-3 remains Complete. D9-2 is
recommended Complete but awaits Peter's disposition. D9-1, D9-4, PO-9,
PO-14, PO-17, PO-18 and H-1 remain open. RP-11 remains unwired and unmet;
package RAID item `P5.0-R5` remains Blocking; `plan.is_executable=False`; and
Package 5.0 remains not ready.

