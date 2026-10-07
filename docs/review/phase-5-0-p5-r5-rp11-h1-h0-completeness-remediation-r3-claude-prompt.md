# Claude prompt — R2 review findings remediation (R3)

Status: **authorized by Peter Duscha on 2026-10-06**

Work ID:
`C-P5.0-R5-RP11-H1-OH-S0B-S1-H0-R5-DR3-20261006-05`

## Start instruction

Start Claude Code in `/opt/freedom-blades/platform`, then paste:

```text
Execute the authorized repository-only assignment in docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-claude-prompt.md. Remediate independent-review findings R2-F1 through R2-F3, produce a self-contained cumulative R3 proposal and durable handback, update only the three authorized current-state pointers, and stop for independent Codex re-review. Do not access oracle-test, any retained evidence path, credentials, or secrets; do not perform cleanup, tests, builds, network access, or any host mutation.
```

## Authority and terminal boundary

Peter Duscha, Product Owner and Acceptance Authority, authorizes this exact
repository-only documentation assignment. Its authority record is
[`project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-authority.md`](project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r3-authority.md).

This assignment repairs the cumulative proposal only. It does **not** accept
R2 or authorize network or `oracle-test` access, retained-evidence access,
cleanup, deletion, checkout creation, credential or secret access, privilege,
package operations, installation, build, application tests, service/database
mutation, H-0G, OH-S2, H-1/H-2, activation, rollback, commit or push. Stop
after writing the documentation and handback for independent Codex re-review.

## Required reading

Read completely before editing:

1. `.agents/AGENTS.md`;
2. the reading map and §§0, 16, 17 and 20 of `docs/implementation-plan.md`;
3. `docs/review/Handover information`;
4. the restriction banner in `docs/operations/disposable-test-server.md`;
5. the R2 authority, consumed prompt, cumulative proposal and handback;
6. `docs/review/project-review-2026-10-06-p5-r5-rp11-h1-h0-completeness-remediation-r2-findings.md`;
7. the complete DR1 proposal and handback; and
8. the R5 prompt, handback through “Checks not run”, independent review, and
   the accepted one-host sections cited by R2 for repository provenance,
   source consumption, retention and cleanup.

Inspect `git status` first. Preserve all unrelated and pre-existing changes.
Do not inspect any remote host or retained remote path.

## Findings that must be remediated

### 1. R2-F1 — replace CK-9 with a complete deterministic contract

R2 left CK-9's `.git` top-level closed set “to be fixed by review.” Replace
that placeholder and remove the corresponding open review question.

The R3 rule must be executable and fail-closed without asking the reviewer to
invent an allowlist or choose its evidentiary basis. Ground it in the accepted
CR retrieval sequence and the security properties actually required. Use one
of these defensible forms, explaining the choice:

- a complete exact allowlist derived from durable accepted evidence for the
  same `init --template=`, shallow fetch and detached-checkout procedure; or
- a bounded structural inventory plus explicit rejection of every Git
  mechanism that can redirect, replace, execute, import or borrow state,
  without pretending an unobserved incidental file set is authoritative.

At minimum, the final contract must continue to reject remotes; unexpected
local configuration; includes; credential, URL-rewrite, transport, filter,
hook, fsmonitor and maintenance configuration; active hooks; gitlinks and
submodule state; replace refs; grafts; alternates; worktree indirection;
`commondir`; unexpected object borrowing; and any path or file type that can
defeat the anonymous pinned-source boundary. State exact permitted outcomes,
exact `HARD STOP` outcomes and the bounded evidence recorded. Do not weaken
CR-1 through CR-4 or CK-0 through CK-11.

### 2. R2-F2 — make symlink inventory and source consumption distinct

The pinned repository contains the intentional tracked `venv` symlink whose
committed link text is `/opt/freedom-blades/runtime/venv-bot`; therefore do
not claim that merely matching Git mode `120000` prevents escape, and do not
silently ban it without reconciling the accepted tree.

Amend CK-3 and every affected source-consumption rule so that:

1. inventory uses `lstat` and never dereferences a symlink;
2. every worktree symlink must correspond to mode `120000` in the pinned tree,
   and its exact link text must equal the pinned blob bytes;
3. absolute targets and relative targets that resolve lexically outside the
   checkout are recorded as checkout-escaping and **non-consumable**, not
   incorrectly described as rejected merely by inventory;
4. every path an RP-11 slice actually consumes as repository source is named
   by that slice's accepted covered-source list, has no symlink in any path
   component, terminates in a regular file owned by `ubuntu:ubuntu`, is not
   group- or world-writable, and has bytes equal to its applicable accepted
   digest;
5. no RP-11 command may open, execute, hash as source, import, traverse through
   or otherwise dereference a checkout-escaping symlink; and
6. an attempted consumption of a symlink or a path with a symlink component is
   a pre-use `HARD STOP`, with nothing repaired or followed.

Reconcile CK-10, the slice matrix, `source_checkout`, A-2, ACT, TR-2, TR-10,
A0-02 and any launcher/build/test path that consumes repository bytes. Make
clear that invoking the separately installed interpreter or runtime by its
fixed accepted host path is not consumption through the checkout's `venv`
symlink.

### 3. R2-F3 — correct the retained-evidence rationale

Remove the assertion that manifests and digests reproduce retained bytes.
State instead:

- manifests and digests authenticate or describe retained bytes but do not
  reproduce them;
- no retained path becomes cleanup-eligible merely because its digest appears
  in a durable handback;
- cleanup eligibility requires explicit closure of every dependency on the
  host bytes, or Peter's explicit abandonment of that evidence, followed by
  the existing CE enumeration, independent review, literal-list approval and
  separately authorized cleanup; and
- if any future review or recovery step requires the retained bytes rather
  than only the durable record, that path remains retained unless a separately
  authorized preservation/export step succeeds and is accepted.

Preserve the existing prohibition on writing an executable cleanup command or
creating cleanup authority in this assignment.

## Preserve the accepted substance

Produce a self-contained cumulative R3 proposal. Preserve R2's sound HF-15
repair, D-1 through D-7, Route 1, P-0p/AM-0, HF-20/CL-21i, FI-1 through FI-5,
composition anchors, slice gates, lifecycle policy and every other unaffected
DR1/R2 amendment. Do not reopen Peter's recorded decisions or weaken a gate.

Resolve the three findings in the proposal itself. Questions for review may
ask whether the completed solution is sufficient; they must not ask the
reviewer to supply a missing allowlist, security rule, normative value or
design decision.

## Deliverables

Create:

1. `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-proposal.md` — a self-contained cumulative proposal superseding R2 if accepted;
2. `docs/review/phase-5-0-p5-r5-rp11-h1-h0-completeness-remediation-r3-handback.md` — the complete durable handback.

Do not rewrite any consumed prompt, authority, proposal, handback or review.

Update only these current-state pointers:

- `docs/review/Handover information`;
- `docs/project-management/status.md`; and
- §20 of `docs/implementation-plan.md`.

The handback must distinguish pre-existing changes; list files changed and
their exact outcomes; report checks run and not run; confirm that no host,
network, retained-path, credential or secret access occurred; map R2-F1
through R2-F3 to exact R3 sections; and identify independent Codex re-review
as the next gate.

## Verification

Run only local documentation checks:

- `git diff --check`;
- repository-relative link-target checks;
- a targeted scan proving no unresolved phrase such as “to be fixed by
  review” remains in a normative CK rule;
- a targeted trace from every source-consuming slice to the no-symlink-
  component and digest checks;
- a targeted scan proving the proposal does not claim that mode `120000`
  alone prevents an escaping symlink;
- a targeted scan proving it does not claim manifests or digests reproduce
  retained bytes; and
- a scope review for accidental execution authority, cleanup commands,
  secrets, player data, network access, commit or push language.

Do not run application tests, formatters, builds or remote checks.

End the handback exactly:

`R3 remediation awaits independent Codex review; no host cleanup, H-0G, OH-S2 or later slice is authorized.`

