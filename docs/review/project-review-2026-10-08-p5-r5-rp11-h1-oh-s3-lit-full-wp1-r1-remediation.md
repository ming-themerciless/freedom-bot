# Independent re-review — LIT-FULL WP-1 R1 remediation

Date: 2026-10-08

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R1-20261007-10`

Reviewed deliverables:

- [R1 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-proposal.md)
- [R1 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-handback.md)
- [Consumed R1 prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-claude-prompt.md)
- [Consumed R1 authority](project-review-2026-10-07-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r1-remediation-authority.md)

## Recommendation

**Changes requested. Do not accept WP-1 or authorize WP-2.**

WP1-R1's missing successor gate is repaired: the proposal and all four
current-state pointers now require complete implementation-plan §0.2 change
control before WP-2 may be prompted, authorized or rely on an exception-bearing
boundary. They also preserve the literal no-exception design fork, keep BC-2
unresolved, and decide neither BQ-2 nor BQ-3.

WP1-R2's complete-read requirement is evidenced, and the resulting audit finds
material corrections that the original return missed. The cumulative proposal
cannot yet be accepted because its final exception/dependency table contradicts
that audit, and two decision-facing summaries promote or misplace unsettled work.

### WP1-R1R-1 — Blocking — B2-F-B is incorrectly classified as an LR-4 exception

Proposal §10.1 says B2-F-B carries EX-3 for “LR-2 and, for DI-2, LR-4.” That
contradicts the proposal's own COR-09, COR-16 and §7.5: if `AP-2` is outside the
root-procedure set, LR-4 does not reach DI-2. Accepted R8 §9.2 applies LR-4 to
each root procedure in the set, while §12.2 BC-4 describes the relevant change
as excepting `sudo`-started procedures from LR-1 through LR-2. Leaving `AP-2`
outside the set may be a wider BC-4 boundary exception, but this record has not
established a separate LR-4 exception.

This is the proposal's required canonical table of every LR exception and §0.2
item. An erroneous entry could alter the scope of the later change-control
impact assessment and Peter's decision. Correct §10.1 and every dependent
summary so EX-3 is described consistently with COR-09/COR-16, without silently
expanding BC-4 or LR-4.

### WP1-R1R-2 — Important — the decision matrix misstates FR-1 as a prerequisite design package

Proposal §2.2 labels its column “New design package before WP-2 can be
meaningful,” then puts B2-F-A's `start` and `stop` roles there as “FR-1,
documentation amendment only.” Elsewhere (§10.1–§10.2 and §11) those roles are
work for WP-2 through WP-7: WP-2 inventories them, WP-3 specifies their
interfaces, and WP-4 supplies images. No separately completed pre-WP-2 design
package is identified for B2-F-A after its exception has passed §0.2.

Correct the column or the row so the gate does not imply both that FR-1 is a
pre-WP-2 design package and that it is only a documentation amendment. Keep the
actual pre-WP-2 blockers distinct: §0.2 closure for an exception path, versus
the separately authorized loader-free privileged-start design for B2-S.

### WP1-R1R-3 — Important — the proposed BQ-3 decision sentence turns the H-1R invocation inference into fact

Proposal §5.3 and COR-13 correctly say no accepted record states H-1R's
invocation and that use of the verified-exec stub is inferred. Proposed approval
sentence §9.2 nevertheless defines the class including H-1R as “the installer
tool run through the verified-exec stub,” without preserving that qualification.
Peter should not be asked to approve an exception sentence whose factual premise
the same audit marks unestablished.

Rewrite the sentence to classify H-1R expressly while leaving its invocation
unasserted, or require a separately authorized record to establish the literal
before the sentence relies on it. This does not decide whether H-1R belongs in
the installer class; PD-3 remains Peter's decision.

### WP1-R1R-4 — Optional — correction count is inconsistent

Proposal §0.1 says the complete reading corrected fourteen places, while §6.4
contains COR-01 through COR-16 and the handback/current pointers say sixteen.
Use sixteen consistently.

## Checks and evidence

- The R1 prompt identity matches its authority pin: 7,482 bytes, SHA-256
  `2724e5c19d4edf9084200dc7bde58853864b19d41fadfbebbde4a2b508f4f127`.
- The proposal matches the handback pin: 75,452 bytes, 997 lines, SHA-256
  `121969c4e305a7d2cbba587b82bbaf43ec2124ba5b4250ddfd4a963caf7bdf8c`.
- The proposal was read completely. The governing agreement, implementation-plan
  §§0, 16 and 20, active handover, restriction banner, R1 authority and prompt,
  original independent review, and the relevant accepted R8/design passages were
  checked repository-only.
- The exact §2.4 gate is present in the four current-state pointers. Each says
  WP-1 is changes-requested/not accepted and BQ-2/BQ-3 are undecided.
- No local link defect was found in the reviewed deliverables.

No host, retained-evidence, network, secret, service, database, package, build,
test, formatter, implementation, activation, rollback, commit or push operation
was performed. Tests were neither authorized nor relevant to this documentation
review.

This review accepts nothing, decides neither BQ-2 nor BQ-3, opens no §0.2 change,
and authorizes no successor. After remediation, independent Codex re-review is
still required before Peter can accept WP-1.
