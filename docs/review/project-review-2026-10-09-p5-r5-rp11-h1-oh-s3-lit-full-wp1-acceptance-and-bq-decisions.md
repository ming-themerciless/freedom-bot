# LIT-FULL WP-1 acceptance and BQ-2/BQ-3 decisions — 2026-10-09

Peter Duscha, acting as Product Owner and Acceptance Authority, accepts the
independent R6 re-review recommendation and the cumulative R6 remediation
proposal as the completed LIT-FULL WP-1 boundary analysis. The review reported
no Blocking, Important or Optional finding. WP1-R4R-1 and WP1-R4R-2 remain
closed.

Peter records the following three decisions exactly as recommended by WP-1,
including the proposed §9.1 and §9.2 decision sentences subject to their stated
§0.2 effectiveness conditions:

1. **PD-2a / BQ-2 start boundary: B2-F.** A `sudo`-started root procedure in
   the final set begins at its first design-controlled image. This selects the
   proposed EX-1 treatment of `sudo` as a launch preamble outside the
   inventoried tree; EX-1 is an exception to LR-2 only.
2. **PD-2b / BQ-2 membership: both acts in.** `AP-2` belongs to the final
   root-procedure set as the static `start` role, and the OS-6 interruption
   `stop` belongs to it as the static `stop` role. No EX-3 whole-act boundary
   exception is selected. Their role design remains work allocated to WP-2
   through WP-7 after the gate; it is not a prerequisite design package.
3. **PD-3 / BQ-3 installer boundary: B3-OUT.** The installer class—H-1,
   RB-1, RS-1 and H-1R—stays outside the LIT-FULL root-procedure set. This
   selects proposed EX-2, with HB-1 as the stated residual. The decision asserts
   no invocation literal for H-1R.

This combination is B2-F with both acts in and B3-OUT. It requires no B2-N
loader-free privileged-start design and no Python-free installer design before
WP-2. It does select EX-1 and EX-2. The choices therefore trigger mandatory
implementation-plan §0.2 change control for both exceptions and the affected
BC-4 boundary.

This record accepts WP-1 and records the boundary choices. It does **not** make
EX-1 or EX-2 effective, approve or widen BC-4, close §0.2 change control, change
the controlled baseline, establish concrete Route 3, decide BC-2, authorize
WP-2, or authorize host or implementation work. Peter's boundary decisions are
not themselves §0.2 approval. WP-2 remains blocked until one complete §0.2
change item covering EX-1 and one covering EX-2 have satisfied steps 1–5,
including impact assessment, Product Owner recommendation, Technical Lead
review, Acceptance Authority approval and any required new baseline version.

- [Independent R6 re-review](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation.md)
- [Accepted cumulative R6 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-proposal.md)
- [R6 handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r6-remediation-handback.md)
- [Open §0.2 change control](../project-management/change-log.md)
- [Archived pre-decision handover](Handover-information-through-2026-10-09-lit-full-wp1-r6-remediation-review.md)
