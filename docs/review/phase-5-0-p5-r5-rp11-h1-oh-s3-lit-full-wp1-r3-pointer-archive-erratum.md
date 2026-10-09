# Erratum — missing archive snapshot of the R3-authorization current-state pointers

Date: 2026-10-08

Authority: the [R4 remediation authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-authority.md)
(Peter Duscha, Product Owner and Acceptance Authority), work ID
`C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R4-20261008-13`, executing the exact
[R4 remediation prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r4-remediation-claude-prompt.md)
(12,936 bytes, SHA-256 `218040bc5bc5ee34e27cb1e1eeaceb66443992f25ebb30629a2053ae7c473620`).

Remediates: finding **WP1-R3R-3** (Important) of the
[independent R3 re-review](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation.md).

Affected archives: the [handover archive](handover-archive/README.md),
the [status archive](../project-management/status-archive/README.md),
the [implementation-plan archive](../implementation-plan-archive/README.md) and
the [disposable-test-server archive](../operations/disposable-test-server-archive/README.md).

**This erratum records a historical gap. It recreates no snapshot, changes no decision,
authorizes no work and does not make WP-1 acceptable. WP-1 remains `changes requested` and is
not accepted; BQ-2 and BQ-3 are undecided; concrete Route 3 remains unestablished; WP-2 is not
authorized.**

## 1. What is missing

The R3 remediation (work ID `C-P5.0-R5-RP11-H1-OH-S3-RT3-WP1-R3-20261008-12`) rewrote the four
current-state pointers when it returned:

* `docs/review/Handover information`;
* `docs/project-management/status.md`;
* §20 of `docs/implementation-plan.md`; and
* the restriction banner of `docs/operations/disposable-test-server.md`.

Before that return each pointer carried the **R3-authorization** wording: the text that made the R3
remediation the current assignment. The R3 return replaced it. Implementation-plan §16.3 and the
"Current-state documents and archives" section of `.agents/AGENTS.md` require consumed and
superseded current-state blocks to move verbatim to dated, indexed snapshots. **No such snapshot of
the R3-authorization pointer text exists in this repository.**

The [R3 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md)
§3 states why: the R3 prompt permitted only the four pointer edits and forbade edits to archive
indexes, so no archive snapshot was created, and verbatim pre-edit copies were saved only outside
the repository, in the executing session's scratchpad. That scratchpad is not part of the repository
and is not evidence that the repository can present.

## 2. What the repository does hold

| Evidence | Identity | What it preserves |
|---|---|---|
| [R3 authority](project-review-2026-10-08-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-authority.md) | 2,386 bytes, SHA-256 `29b492720fca0aa5ea4be564fd673232bcdbca77714a3000dd51115c541cda7a` | the substance of Peter's R3 authorization |
| [R3 exact prompt](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-claude-prompt.md) | 11,277 bytes, SHA-256 `73238176135e73f71fc3cfe8049d15e6af6234d6b125c7ab61ff5f17558da03b` | the exact assignment, its restrictions and its permitted edits |
| [R3 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md) | 111,399 bytes, 1,339 lines, SHA-256 `07f2d4851c3b339f90ba3ceda66c98af349d34ddd75e2886d295de053306c84d` | the returned work |
| [R3 remediation handback](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-handback.md) | 16,550 bytes, 194 lines, SHA-256 `9d659ce2068174cae593fe279871edcbe911aca269684d655ade411eb101ca8a` | the return, the four pre-edit digests (§3 below) and the admission that no snapshot was made |
| the four **R3-return** snapshots (controller-created before the R4 authorization became current) | digests in §4 below | what the four pointers said **after** the R3 return, not before it |

These records preserve the **substance** of the R3 authorization and of the R3 return. They do not
preserve the **verbatim bytes** of the overwritten pointer text.

## 3. The four pre-edit digests, exactly as the R3 handback records them

The R3 handback §3 records these digests of the four pointer files as they stood before the R3
return edited them, **abbreviated exactly as shown there**:

| Pointer | Digest as recorded in R3 handback §3 |
|---|---|
| `docs/review/Handover information` | `69f5c8cc8e09…10e9cb` |
| `docs/project-management/status.md` | `25cf5bc954d6…0b488b` |
| `docs/implementation-plan.md` | `7e0486d0c1eb…3883bc` |
| `docs/operations/disposable-test-server.md` | `bd15b1637606…a2ce4c` |

**The R3 handback §3 does not contain the full values.** Full values appear elsewhere, as a matter of
what those documents state:

* the R3 handback §2 gives the full `status.md` pre-edit digest,
  `25cf5bc954d62c8477d536bf9f4800b472ced9c2e41e8983dc0af6c4fa0b488b`;
* the [R3 remediation proposal](phase-5-0-p5-r5-rp11-h1-oh-s3-lit-full-wp1-r3-remediation-proposal.md)
  §1.1, items 2, 3 and 4, gives the full pre-edit digests of the other three:
  `docs/implementation-plan.md` `7e0486d0c1eb32a3c6beb8b65d96b6824e43d05149422ab127c487b5733883bc`,
  `docs/review/Handover information` `69f5c8cc8e09e9fd1e1eed99ab329ea97d92424238157bd62fa6d3978310e9cb`
  and `docs/operations/disposable-test-server.md`
  `bd15b16376066432bca822b85108872e1c2aa1a38c18f4f4973024be70a2ce4c`.

These values are reproduced here **as a record of what those two documents state**. They are not a
verification. **No digest match can be performed**, because the bytes they describe are not in the
repository. Searches made for the R4 remediation (proposal §1.2) found that none of the four digests
equals the SHA-256 of any file now under `docs/` or `.agents/`, of any committed revision of the four
pointer paths in any ref, or of the one stash entry. The R4 return therefore **neither reconstructs
the pointer text nor claims it verbatim**.

## 4. The R3-return snapshots, which are unchanged

The controller created these snapshots from the pointers as the R3 return left them, before the R4
authorization became current. Their digests are those recorded by the four archive indexes and equal
the digests of the files on disk when this erratum was written. This return did not open them for
editing and did not change them.

| Snapshot | SHA-256 at archival |
|---|---|
| [`Handover-information-through-2026-10-08-lit-full-wp1-r3-remediation-return.md`](Handover-information-through-2026-10-08-lit-full-wp1-r3-remediation-return.md) | `0ede35e56f8497eb991786275afeefdd5c0bbbc75ac3a59a1b7164fb7bb8256f` |
| [`status-through-2026-10-08-lit-full-wp1-r3-remediation-return.md`](../project-management/status-through-2026-10-08-lit-full-wp1-r3-remediation-return.md) | `e45b221d604eb8c3e35aa4bbbfd68b32198d14ab09d675a3ca92347b0d05ba07` |
| [`implementation-plan-through-2026-10-08-lit-full-wp1-r3-remediation-return.md`](../implementation-plan-through-2026-10-08-lit-full-wp1-r3-remediation-return.md) | `0c45cc6a5092336d231266a9f433e54883b35886c076bd2b2f74eaff35f4cf01` |
| [`disposable-test-server-through-2026-10-08-lit-full-wp1-r3-remediation-return.md`](../operations/disposable-test-server-through-2026-10-08-lit-full-wp1-r3-remediation-return.md) | `388b655f8b43067e7d534acf64c7bd57942d108ba4ffae4e6c5aa5dca073ee9a` |

## 5. What this erratum does not do

* It does **not** recreate the missing snapshots, and it contains no text of the overwritten
  R3-authorization pointers. Nothing in it is taken from the lost scratchpad.
* It does **not** claim that any digest in §3 matches any file.
* It does **not** edit any archived snapshot, any archive entry other than the one new entry in each
  of the four indexes, or any earlier proposal, handback, review, authority, exact prompt, register or
  accepted record.
* It does **not** change a decision, finding, gate, authority or disposition. It does not decide BQ-2
  or BQ-3 or PD-2a, PD-2b or PD-3; approve EX-1, EX-2, EX-3 or BC-4; open or execute
  implementation-plan §0.2 change control; resolve BC-2; accept WP-1; establish concrete Route 3;
  authorize WP-2; or select LIT-FULL for implementation.
* It does **not** make WP-1 acceptable. The independent R3 re-review requested changes, and the R4
  remediation it accompanies still requires independent Codex re-review.

## 6. The authority for this erratum

The authority for this erratum is the **R4 remediation authority** linked at the head of this record,
which names the erratum as a required deliverable of the exact R4 prompt, and the four archive-index
entries as the only archive-index edits that the prompt permits.

## 7. Forward control

**Current-state text must be snapshotted and indexed before it is replaced.** The snapshot is a
verbatim, dated copy kept beside the canonical file so that its relative links continue to resolve,
and it is indexed in the relevant archive directory, as implementation-plan §16.3 and
`.agents/AGENTS.md` ("Current-state documents and archives") already require.

**A task prompt may not prohibit a governing §16.3 archival obligation without an approved
governing-document change.** A prompt that permits only particular edits must either leave the
archival step to the controller before it activates the prompt, as the R4 assignment did, or be
accompanied by an approved change to the governing documents. A prompt's prohibition on archive-index
edits is not, by itself, a reason to skip the snapshot.

This erratum states how the existing control is applied. It does not edit `.agents/AGENTS.md` or the
implementation plan.

## 8. Index entries

One entry for this erratum is added to each of the four archive indexes:

* [`handover-archive/README.md`](handover-archive/README.md);
* [`status-archive/README.md`](../project-management/status-archive/README.md);
* [`implementation-plan-archive/README.md`](../implementation-plan-archive/README.md); and
* [`disposable-test-server-archive/README.md`](../operations/disposable-test-server-archive/README.md).

Each entry links this erratum, states the gap in one sentence and states that no snapshot was
recreated. No archived snapshot is edited.
