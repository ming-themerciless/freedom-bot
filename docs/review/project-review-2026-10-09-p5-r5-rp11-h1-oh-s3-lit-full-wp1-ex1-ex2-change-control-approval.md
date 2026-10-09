# EX-1 and EX-2 §0.2 approval; baseline v1.8 — 2026-10-09

Peter Duscha explicitly said “I approve” after receiving the complete plain-
language approval question and explanation. Acting as Product Owner, he adopts
the prepared recommendation. Acting as Acceptance Authority, he approves EX-1
and EX-2 exactly as assessed, makes their existing BC-4 uses effective without
widening BC-4, accepts HB-1 for EX-2 and adopts controlled baseline v1.8.

## Effective boundary

- **EX-1:** for `attest`, the `AP-2` holder-creation act and the OS-6
  interruption, the root procedure begins at the first design-controlled static
  image that `sudo` executes. `sudo`, and nothing else, is a launch preamble
  outside the inventoried tree and an exception to LR-2 only. LR-1 and LR-3
  through LR-6 apply in full from the first image downward.
- **EX-2:** H-1, RB-1, RS-1 and H-1R are outside the LIT-FULL root-procedure
  set as an exception to LR-1 and LR-2 under BC-4. HB-1 is accepted for the
  installer members that run under `sudo`'s environment. No H-1R invocation
  literal is asserted. Independent pre-use verification against the H-1 record
  and maintainer-supplied A-2 pins remains mandatory.

EX-3 is not selected. B2-N and a Python-free installer are not prerequisites
for WP-2 under the selected F-1 combination. BC-4 is not widened: its existing
`sudo`-started-procedure and installer-class wording covers these two uses.

## §0.2 closure

For both exception-specific change items:

1. requester, reason and affected requirements are recorded in the change log;
2. scope, dependencies, estimate, risk, testing, migration and operations are
   assessed in the linked assessment;
3. the Product Owner recommendation is adopted and the Technical Lead review
   recommends approval;
4. the Acceptance Authority approves the changes; and
5. controlled baseline v1.8 is adopted because the release boundary changes.

The EX-1 and EX-2 §0.2 items are therefore **closed and effective**.

This approval changes the design boundary only. It does not select LIT-FULL for
implementation, establish concrete Route 3, resolve BC-2, authorize WP-2,
authorize any host or retained-evidence access, or authorize implementation,
build, test, package, service, database, activation, commit or push work. The
next permissible action is preparation and independent review of a separate
WP-2 assignment under the accepted F-1 boundary.

- [Impact assessment and Technical Lead review](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-ex1-ex2-change-control-assessment.md)
- [WP-1 acceptance and BQ decisions](project-review-2026-10-09-p5-r5-rp11-h1-oh-s3-lit-full-wp1-acceptance-and-bq-decisions.md)
- [Change log](../project-management/change-log.md)
- [Archived pre-approval handover](Handover-information-through-2026-10-09-lit-full-wp1-ex1-ex2-change-control-review.md)
