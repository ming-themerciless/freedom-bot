# Independent re-review — LIT-FULL WP-1 R2 remediation

Date: 2026-10-08

Reviewer: Codex, Independent Reviewer

Reviewed work ID: `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R2-20261008-11`

Reviewed deliverables:

- [R2 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-proposal.md)
- [R2 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-handback.md)
- [Consumed R2 prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-claude-prompt.md)
- [Consumed R2 authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r2-remediation-authority.md)

## Recommendation

**Changes requested. Do not accept WP-1 or authorize WP-2.**

The four findings assigned to R2 are substantially repaired: EX-3 is no longer
classified as an LR-4 exception; FR-1 is separated from pre-WP-2 design
prerequisites; the H-1R fact and invocation inference are separated; and
COR-01 through COR-16 are consistently described as sixteen corrections.

The repaired matrix nevertheless drops one decision dimension on the B2-S
path. That omission can bypass both a required Peter decision and §0.2 change
control, so the cumulative proposal is not yet decision-ready.

### WP1-R2R-1 — Blocking — B2-S omits PD-2b and conditional EX-3

Proposal §2.2 correctly defines the governance prerequisite as Peter's recorded
PD-2a, PD-2b and PD-3 decisions. Rows 5 and 6 then omit PD-2b even though their
work column depends on “the acts PD-2b puts in the set.” Those rows say B2-S plus
B3-OUT carries EX-2 only and B2-S plus B3-IN carries no exception. Proposal
§13.2, however, correctly says each PD-2b “out” answer adds an EX-3 part.

The same omission appears in canonical table §10.1: B2-S records only PD-2a,
while its work depends on PD-2b. Section 12.2 then hard-codes both the `start`
and `stop` acts as absent under B2-S rather than making them conditional on
PD-2b.

B2-S decides where a `sudo`-started procedure begins; it does not decide whether
AP-2 or the OS-6 stop belongs to the final root-procedure set. For every act
Peter puts in the set, B2-N must provide the loader-free privileged start and
the corresponding role remains work for WP-2 through WP-7. For every act Peter
leaves outside, EX-3 remains a proposed wider BC-4 boundary exception and must
complete §0.2 change control before WP-2 may be prompted, authorized or rely on
that boundary. PD-2b is therefore required on every B2-S combination.

Replace the collapsed B2-S rows with an explicit complete matrix, or an equally
unambiguous orthogonal matrix, covering both PD-2b membership choices for each
act and both B3 answers. Correct §§2.2, 10.1 and 12.2 and every dependent summary
so no combination loses PD-2b, EX-3, §0.2 or its later-WP role.

### WP1-R2R-2 — Optional — one stale `sudo -n` line count remains

Proposal §1.2 and the handback report the reproduced R8 count as eight lines and
identify nine as the non-reproducing R1 count. Proposal §13.1 Q-2 still says
there are nine R8 lines. Change that stale count to eight; no conclusion changes.

## Checks and evidence

- The R2 prompt identity matches its authority pin: 10,678 bytes, SHA-256
  `bb88208f76a4d9dcfd7f76cb0678c3e44193a4b9e9a25af0a1b7fb450300256f`.
- The proposal matches the handback pin: 95,541 bytes, 1,168 lines, SHA-256
  `8881f4ba5d96c9be4f1dfb6f79115a43154e633f384ac250e6401d9ae31bacce`.
- The proposal and handback were read completely. The governing agreement,
  implementation-plan §§0, 12, 16 and 20, active handover, restriction banner,
  R2 authority and prompt, prior independent findings and relevant decision
  passages were checked repository-only.
- The four current-state pointers retain the no-host restriction and say WP-1
  remains changes-requested/not accepted, BQ-2/BQ-3 are undecided, concrete
  Route 3 is unestablished and WP-2 is not authorized.

No host, retained-evidence, network, secret, service, database, package, build,
test, formatter, implementation, activation, rollback, commit or push operation
was performed.

This review accepts nothing, decides neither BQ-2 nor BQ-3, opens no §0.2 change,
and authorizes no successor. After remediation, independent Codex re-review is
still required before Peter can accept WP-1.
