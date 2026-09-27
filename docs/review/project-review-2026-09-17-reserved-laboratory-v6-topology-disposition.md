# Independent project review — V6 provisioning-topology disposition (C-P5.0-LAB-V6-D) — 2026-09-17

Reviewer: Codex, independent of the Claude implementation and repair pass.

Subject: the bounded repository-local disposition returned in
[the handback](phase-5-0-reserved-laboratory-v6-topology-disposition-handback.md),
including Claude's seven self-review repairs previously recorded at this path.

## Verdict

**Changes requested: one Blocking finding.** The code repair for V12's topology
is sound within the reviewed repository boundary, but the governing r6 contract
still contains two operative statements for the withdrawn topology. The
disposition therefore is not yet one unambiguous contract and cannot be accepted
for provisioning or later V6 re-observation.

Nothing in this review approves a digest, authorizes provisioning or execution,
closes a gate, or confirms a host fact. V6 remains performed-but-not-closed, I3
unconfirmed, V7 excluded, V8 and V10 unperformed, `plan.is_executable` false,
and Package 5.0 not ready.

## Finding

### PR-20260917-LAB-V6D-R1-1 — Blocking — the contract still operates on the withdrawn `/opt` topology

The repair correctly amends the D1 row and the released-subset rows, but it does
not remove the old topology from all operative statements:

1. In r6 §1.3.3, immediately under **“The complete descriptor inventory,”**
   line 340 still states ``R = /opt/freedom-blades/evidence/<run>``. The D1 row
   six lines later says the opposite: the evidence root is
   `/var/lib/fb-evidence-p5-0` and V11 is withdrawn. Nothing on the stale `R =`
   line marks it as historical or struck.
2. In r6 §7's eleven-item table, the live V6 row at line 2074 still instructs
   the survey to observe `/opt/freedom-blades/evidence`, then reports the
   preflight as **unperformed**. The current disposition withdrew that path, and
   the repository's `UNCONFIRMED_TARGET_FACTS` and active handover both record
   V6 as **performed-but-not-closed**.

These are not harmless historical mentions. They occur in the current descriptor
inventory and current §7 item table, while nearby amended rows assert the new
topology. The self-review's earlier Blocking PR-20260917-LAB-V6D-2 identified
the same control failure: a banner or later narrative is not a substitute for
correcting normative rows. Leaving two more such statements permits a later
review or operational procedure to use the withdrawn location or report the
wrong V6 state.

**Required remediation:** make §1.3.3's `R` definition name the sole canonical
`/var/lib/fb-evidence-p5-0` topology, and amend the live V6 table row to remove
the withdrawn `/opt` target and state the survey's actual performed-but-not-closed
status. Preserve the distinction between the completed read-only survey and the
still-unauthorized post-provision repetition/controlled write verification.
Then search the current operative contract for remaining unmarked old-topology
definitions and return the bounded documentation repair for re-review.

## Accepted portions of the submitted repair

Within the reviewed scope, no additional code or security finding was found:

- `directory_targets()` derives V12 from both independent child paths, refuses
  divergent parents, duplicate child names and malformed paths before creating
  anything, and derives `expected_children` from the actual basenames.
- The refusal reuses the closed `creation-refused` classification and exposes no
  pathname or operating-system error in the operator-facing exception.
- The production defaults resolve V12 to `/var/lib/freedom-blades`, before V4
  and V5, while V7 remains excluded and real execution remains unconditionally
  refused.
- `EVIDENCE_ROOT` now has one code source, `APPROVED_TARGET.root_path`; the dead
  V11 source string is gone; the item count, approval provenance and applier
  description are corrected.
- The generated manifest and plan are deterministic for the reviewed tree and
  match the installed artifacts byte for byte. The manifest has 44 covered
  sources, version 13, and zero independently recomputed hash mismatches. Its
  recomputed review-input digest is
  `6b3ec46f82fa55983d52765cedf32e6d61723059ebe816269c112716dd478973`.
  Because the Blocking finding remains, this value is **not approved** and must
  not be passed to `--execute`.

## Evidence run

Repository-local only, with `TEST_DATABASE_URL` unset and no host access:

- focused V6 provisioning module: **131 passed**, 2 warnings;
- complete `tests/phase_5_0_evidence`: **2,374 passed**, zero skipped, 2 warnings;
- structural guards: **31/31 passed**;
- scoped `compileall`: passed;
- `git diff --check`: passed;
- non-executing CLI dry generation: installed manifest and plan both matched;
- independent manifest verification: **44 hashes, zero mismatches**, manifest
  version 13, digest as stated above.

The two warnings are the existing unknown pytest options `asyncio_mode` and
`asyncio_default_fixture_loop_scope`. No PostgreSQL evidence was produced. No
formatter, linter or type checker is configured. The bot, web and Foundry suites
were not re-run for this documentation-focused residual review; the submitted
figures remain implementer evidence, not this reviewer's evidence.

## Restrictions observed and next action

No SSH, synchronization, host inspection, provisioning, permission change,
database operation, controlled write verification, generated-vector execution,
real participant, real boundary/materializer or `--execute` was performed.

Next action: one bounded repository-local correction of
PR-20260917-LAB-V6D-R1-1, followed by independent Codex re-review. No dependent
host or gate action is released.
