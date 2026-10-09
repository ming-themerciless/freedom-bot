# Independent review — LIT-FULL WP-1 boundary proposal

Date: 2026-10-07

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-20261007-09`

Reviewed deliverables:

- [WP-1 boundary proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-boundary-proposal.md)
- [WP-1 handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-handback.md)
- [Consumed WP-1 prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-claude-prompt.md)

## Recommendation

**Changes requested. Do not accept WP-1 or authorize WP-2.**

### WP1-R1 — Blocking — mandatory §0.2 gate omitted from the successor condition

The proposal correctly records that its recommended BQ-2 and BQ-3 answers each
require a BC-4 exception and the full implementation-plan §0.2 process. Its
current-state pointers nevertheless say that WP-2 may be prompted after only
independent review and Peter's BQ-2/BQ-3 decisions. That is insufficient. An
exception changes the accepted security boundary; WP-2 may not rely on it until
the §0.2 change-log entry, impact assessment, Product Owner recommendation,
Technical Lead review and Acceptance Authority approval have closed, with a new
baseline version if required.

The corrected state must preserve the decision fork: an exception answer enters
§0.2 change control; a literal no-exception answer requires a separately designed
loader-free privileged start path (or withdrawal). Neither route is approved by
this review.

### WP1-R2 — Important — required complete reading was not performed

The exact prompt says, "Before working, read completely," and names the accepted
R8 proposal. The handback explicitly reports that R8 was read only in selected
sections and by targeted search. R8 is the controlling cumulative authority, and
the WP-1 return itself found root paths not enumerated in R8 §9.3. The proposal
cannot be accepted until Claude reads R8 completely and re-audits every WP-1
claim, source classification, boundary member, exception, follow-on gate and
current-state statement against the entire record.

## Other review dispositions

- Including the OS-6 root stop path and H-1R in the boundary analysis is a
  reasonable recommendation, but remains unaccepted pending remediation.
- B3-OUT is a BC-4 exception under the accepted R8 wording, not merely a harmless
  membership classification.
- The BQ-2/BQ-3 alternatives are understandable, but any exception-bearing choice
  changes the boundary Peter directed the investigation to preserve.
- Prompt identity, proposal digest, local links and whitespace checks passed. No
  host operation or test was authorized or performed.

This review accepts nothing, decides neither BQ-2 nor BQ-3, opens no §0.2 change
and authorizes no successor.

