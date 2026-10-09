# Independent re-review — LIT-FULL WP-1 R3 remediation

Date: 2026-10-08

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R3-20261008-12`

Reviewed deliverables:

- [R3 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md)
- [R3 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md)
- [Consumed R3 prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-claude-prompt.md)
- [Consumed R3 authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-authority.md)

## Recommendation

**Changes requested. Do not accept WP-1 or authorize WP-2.**

The two findings assigned to R3 are materially repaired: PD-2b and conditional
EX-3 now appear across all sixteen combinations, and the reproduced R8 count is
eight matching lines and eleven occurrences. The returned proposal nevertheless
contains two new Blocking contradictions in the pre-WP-2 boundary/gate and one
Important archival defect.

### WP1-R3R-1 — Blocking — the canonical B2-S boundary contradicts itself

B2-N is defined as a loader-free privileged-start path that is not `sudo` and
replaces `sudo` for every in-set act under B2-S. Canonical Table A nevertheless
says that after B2-N each in-set act begins at B2-N's start path while “`sudo` is
inside the tree.” Section 12.2 repeats the contradiction: it answers “no” to
whether `sudo` is outside an inventoried B2-S tree, then says that the tree starts
at B2-N rather than `sudo`.

Those statements cannot both be true. Once B2-N replaces the current `sudo`
start for an in-set act, the resulting inventoried procedure starts at B2-N's
loader-free path and contains no `sudo`. An act classified out remains outside
the boundary under EX-3 and may retain its current `sudo` plus distribution-client
path. Correct canonical Table A, §12.2 and every dependent summary so this
distinction is mechanical and unambiguous.

### WP1-R3R-2 — Blocking — the compact gate permits only one of two required prerequisites

Section 0.2 step 5 says WP-2 follows “steps 1–3 and 4 or 4′.” Several B2-S
combinations require both step 4 (§0.2 closure for EX-2 and/or EX-3) and step 4′
(B2-N and/or the installer design). The next paragraph and union rule U6 state
the correct cumulative rule, but the compact gate can be read to release WP-2
after only one prerequisite.

Replace that condition with “steps 1–3 and every applicable item among 4 and 4′”
or equally exact wording. Recheck every gate summary against U6 so no combination
can bypass either governance closure or a design prerequisite.

### WP1-R3R-3 — Important — superseded current-state text was not durably archived

The handback says that the R3-authorization wording overwritten in all four
current-state pointers was saved only in an external session scratchpad, and no
repository archive snapshot was created because the prompt prohibited archive
work. That conflicts with implementation-plan §16.3, which requires consumed and
superseded current-state blocks to move verbatim to dated, indexed snapshots.
The R3 authority and prompt preserve the assignment's substance, but not the
overwritten pointer text verbatim.

Remediation must not invent or silently reconstruct missing historical bytes.
If the exact pre-edit copies cannot be proved from repository evidence, add a
dated erratum that records the four hashes from the R3 handback, the missing
snapshot limitation, the authority/prompt records that preserve the substantive
authorization, and the forward archival control. Index it from each affected
archive. The current R3-returned pointers must be snapshotted before the R4
authorization replaces them.

## Checks and evidence

- The R3 prompt matches its authority pin: 11,277 bytes, SHA-256
  `73238176135e73f71fc3cfe8049d15e6af6234d6b125c7ab61ff5f17558da03b`.
- The proposal matches the handback pin: 1,339 lines, 111,399 bytes, SHA-256
  `07f2d4851c3b339f90ba3ceda66c98af349d34ddd75e2886d295de053306c84d`.
- The proposal and handback were read completely. The governing agreement,
  implementation-plan §§0, 12, 13, 16 and 20, active handover, restriction
  banner, R3 authority and prompt, R2 re-review and relevant decision passages
  were checked repository-only.
- The exact successor-gate paragraph is present in the proposal and all four
  returned pointers. All retain the no-host restriction and say WP-1 remains
  changes-requested/not accepted, BQ-2/BQ-3 are undecided, concrete Route 3 is
  unestablished and WP-2 is not authorized.

No host, retained-evidence, network, secret, service, database, package, build,
test, formatter, implementation, activation, rollback, commit or push operation
was performed.

This review accepts nothing, decides neither BQ-2 nor BQ-3, opens no §0.2 change,
and authorizes no successor implementation. Independent Codex re-review remains
required after remediation before Peter can accept WP-1.
