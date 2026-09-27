# Independent review — I3 verifier decision handback — 2026-09-19

## Disposition

**Stop accepted; the required maintainer decisions have now been supplied.
The review identified one Important correction in the decision record.** Peter Duscha
accepted the recommendation and issued the consolidated ruling
recorded at the top of `docs/review/Handover information`. The ruling closes
PR-20260919-LAB-I3R1-1 at the decision level; its contract and code corrections
remain unimplemented and require fresh independent review.

Claude correctly invoked C-P5.0-LAB-I3-R1's stop clause. The current controlled
sources do not define one safe, complete I3 verifier: they disagree about P2's
owner and mode, they do not define an execution state that isolates the claimed
`CAP_FOWNER` condition, and decision B reserves creation of the sole canonical
`R` to the concrete plan's `mkroot`. Implementing the requested verifier would
therefore choose security, authority and topology policy that the assignment
explicitly withheld.

No I3 implementation or operational run is accepted or authorized. I3 remains
unconfirmed, V7 remains excluded, V8 and V10 remain unperformed,
`plan.is_executable` remains false, and Package 5.0 remains not ready.

## Finding

### PR-20260919-LAB-I3R1-1 — Important — `CapBnd` is not proof that P2 holds `CAP_DAC_OVERRIDE`

Decision 3 reaches the right stop but overstates its evidence. P-01 requires the
launcher's **bounding** set to contain `CAP_DAC_OVERRIDE` and `CAP_FOWNER`.
Membership in `CapBnd` says that a capability remains obtainable; it does not
say the executor currently has that capability in `CapEff`, or that it will be
effective at P2's `linkat`.

The documented protected-hardlink rule does confirm the underlying security
point: read/write permission may be satisfied through suitable capabilities,
and `CAP_DAC_OVERRIDE` bypasses discretionary read/write checks. Therefore a
P2 executor that actually has effective `CAP_DAC_OVERRIDE` cannot demonstrate
that success required `CAP_FOWNER`. But the reviewed contract must establish
that premise from P2's actual capability state, not infer it from P-01's
bounding-set observation.

The maintainer's capability ruling must consequently state P2's complete
execution identity and relevant capability masks at the operation, including
whether `CAP_DAC_OVERRIDE` and `CAP_FOWNER` are effective, and the verifier must
observe that state before its first write. If the ruling removes
`CAP_DAC_OVERRIDE` to isolate `CAP_FOWNER`, that is the new reduced-capability
security design already identified by the handback and requires amendment and
review; it cannot be selected by the implementer.

## Confirmed contradictions and decisions

The remaining analysis is accepted:

1. **Owner:** r6 §§1.4.4 and 3 call the payload root-owned; r6 §§6.2 and 7.2(6)
   say P2 changes it away from the executor without naming the new owner; the
   executable plan passes `root:root`. The owner and group require one ruling.
2. **Mode:** r6 specifies `0555`, while `case_runtime.CASE_PROGRAM_MODE` and the
   concrete plan specify `0755`. The production contract and assertions must be
   reconciled before a verifier can reproduce P2.
3. **Hard-link condition:** after correcting the `CapBnd` overclaim above, the
   contract still must say whether P2 relies on ownership, ordinary/elevated
   read-write permission, or `CAP_FOWNER`. A test cannot prove one branch while
   the reviewed identity also satisfies another.
4. **Topology authority:** decision B calls `/var/lib/fb-evidence-p5-0` the sole
   canonical `R`, created by the reviewed concrete plan rather than prerequisite
   provisioning, and §1.3.3 says it is created exclusively by that plan's
   `mkroot`. A standalone verifier needs an explicit exception defining its
   temporary creation and identity-guarded removal of `R` and `R/bin`, or a
   separately reviewed topology. Neither exists now.

The proposed separate `linkat` step is designable only after those rulings. It
may be acceptable because the existing `renameat(noreplace=True)` abstraction
immediately removes the temporary and cannot expose the required two-name
observation, but any duplicate must remain one reviewed primitive with the same
exclusive, no-follow, partial-state, guarded-cleanup and barrier guarantees.

## Evidence reviewed

I compared the handback against runner contract r6 §§1.3.3, 1.4.2, 1.4.4, 3,
6.2, 7.1–7.3 and 9.3; the I3 implementation prompt; the P-01 execution-plan
row; `case_runtime`'s P2 constants; the concrete P2 plan; and
`DescriptorBoundEffects.install_case_program`. The handback's recorded source
digests and HEAD match the current workspace.

The installed `proc_sys_fs(5)` text states the three protected-hardlink
alternatives and expressly permits the read/write alternative through suitable
capabilities. The installed `capabilities(7)` text defines
`CAP_DAC_OVERRIDE` as bypassing file read, write and execute permission checks.

No suite was run: this handback adds no implementation, and the active
restriction prohibits SSH, synchronization, host inspection, database access
and operational I3 execution. No host action or filesystem effect was taken.

## Required next action

Peter must decide and record P2's owner/group, mode, actual operation-time
capability state and intended protected-hardlink authorization branch, plus the
standalone verifier's authority over `R`. The correction for
PR-20260919-LAB-I3R1-1 should be incorporated with those decisions. Only then
may a bounded follow-up implementation be assigned for fresh independent
technical and security review before any operational I3 run.
