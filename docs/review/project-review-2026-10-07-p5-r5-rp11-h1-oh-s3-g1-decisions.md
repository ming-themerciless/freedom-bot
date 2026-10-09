# Decision — OH-S3 G-1 design choices and LIT-FULL readiness direction

Date: 2026-10-07

Decision maker: Peter Duscha, Product Owner and Acceptance Authority

Peter Duscha accepts the recommendations in the accepted cumulative OH-S3 R8
proposal for all six G-1a activation-design decisions:

- **DEC-1:** accept RO-1, together with RO-4 and RO-6, as the named,
  outside-guarantee, pre-pass and inert residual. Do not add ALT-SENT.
- **DEC-2:** adopt the recommended operational parameters and BS-RM exactly as
  stated in R8 §12.1.
- **DEC-3:** use the root-only object K under `/run` with `grant.id`.
- **DEC-4:** use the separate privileged read-only H-0M2 slice before H-1.
- **DEC-5:** retire CX-4 for systemd `259.5-0ubuntu3.4`, subject to the
  version-bound drift trigger in R8 §6.8.
- **DEC-6:** adopt SG-1 through SG-8, GR-2 and the single-routine GRR as the
  removal and signal contract.

For G-1b, Peter commissions the **LIT-FULL** Route 3 readiness investigation:
WP-1 through WP-7 in the dependency order recorded in R8 §9.5. This chooses the
R3-ROOT reading for investigation and does not commission the larger LIT-DR1
WP-8 work. It does not select LIT-FULL for implementation; WP-9 remains Peter's
later decision after the readiness packages and independent review.

This direction preserves the accepted Route 3 boundary. It does not open §0.2
change control for SSW, SCDC or ACCEPT-X1 and does not withdraw RP-11. No
exception to LR-1 through LR-6 is approved here.

R8 §11 requires a separate prompt, authority record, work ID and Codex review
for every readiness package. Therefore this record commissions the sequence but
does not make WP-2 through WP-7 current merely by naming them. WP-1 is the first
current repository-only assignment. Its boundary proposal must return the
remaining BQ-2 and BQ-3 interpretations for Peter's explicit approval before
WP-2 is authorized. The LIT-FULL definition answers BQ-4 with no dynamic-child
exception; any proposed exception must instead stop and enter §0.2 change
control.

No host or retained-evidence access, network research, implementation, launcher
work, build, test, package or service/database operation, OH-S4/OH-S4p or later
slice, H-1/H-2, activation, rollback, commit or push is authorized.

- [Accepted cumulative R8 proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-r8-remediation-proposal.md)
- [R8 acceptance](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-r8-acceptance.md)

