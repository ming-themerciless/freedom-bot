# Package 5.0 security re-review — revision 12

Date: 2026-09-02
Reviewer: Codex, Package 5.0 Security Reviewer and Independent Reviewer
Outcome: **P5.0-SR1 and P5.0-SR2 Closed; security design review delivered; no Package 5.0 readiness recommendation**

## Scope and authority

This is the independent re-review required by the revision-12 R11 handback. It
reviews the remediation of P5.0-SR1 and P5.0-SR2 and completes the remaining
design review of the twelve §9.2 security surfaces. It is documentation/design
review only. No host object, database object, account, group, credential,
deployment, migration or production state was created or changed.

This review closes security findings; it does not confirm A-5.0-3 through
A-5.0-5, supply C-1/C-3/C-4 evidence, close P5.0-R1/R4/R5, accept a residual,
rule OD-62/64/65/66, approve the package gate or authorize implementation.

## P5.0-SR1 — Closed on design

Revision 12 replaces the circular live-deployment digest with a fail-closed
four-fact provenance chain:

1. `APR`, installed out of band, names the approved commit, tree and SHA-256
   source-manifest digest;
2. `TM` is derived from immutable Git object bytes in a root-owned bare object
   store addressed by object ID, never a mutable ref;
3. `SM` is independently derived from the bytes actually deployed, with a
   closed reviewed-source/hash-pinned-dependency partition; and
4. `ASR` is append-only PostgreSQL provenance linked to every registered
   generation by `NOT NULL` and composite foreign keys.

Algorithm D refuses missing approval, missing objects, manifest disagreement,
dependency drift, unaccounted files and post-installation disagreement. C0 and
W11a recheck provenance. `JNL-51(g)` explicitly omits provenance and requires
generation creation and activation to remain unreachable, including direct-SQL
foreign-key tests under both coordinator and schema-owner roles. This answers
the finding's required negative proof shape on paper.

The design does not claim host root is outside the trust boundary. The remaining
A5+A8 combination is stated as R-5.0-15 and the signed-record alternative is
routed to OD-66 option A-3. That is a decision/residual, not an unreported gap in
the revised control.

## P5.0-SR2 — Closed on design

Package-plan §2.12.2 is now the sole authority for primary and supplementary
group membership. Provisioning, holder analysis, E1–E8 and the logical schema
cite that table rather than restating membership. E8 now represents the actual
`freedomcoord` membership. Stop condition 10p treats any second membership
statement as a defect.

`JNL-52` specifies exact `getent group` membership plus positive and negative
`id`, `namei` and `open` evidence for `freedomsheet`, `freedomcoord`,
`discordbot` and `freedomweb`. The positive controls make the denials
attributable to the intended path boundary rather than an invalid test identity
or an earlier traversal failure. This is a coherent specification for C-4.

## Remaining security surfaces

No new Blocking or Important design finding was identified in the database
role/HBA ordering, append-only histories and activation trigger, credential
separation, journal lifecycle, capability/holder model, sandbox construction,
provenance model, canonical membership model or recovery contracts.

The following remain evidence or governance work, not passed controls:

- C-1 complete `sudoers` inspection;
- C-3/C-4 and the peer-authentication, HBA-ordering, capability, sandbox,
  journal, provenance and recovery evidence bands;
- confirmation or rejection of A-5.0-3 through A-5.0-5;
- disposition of R-5.0-12 through R-5.0-16;
- OD-64, OD-65 and OD-66, which are now rulable because the required Security
  Reviewer recommendation exists; and
- OD-62 last, after those rulings price the residual cutover risk.

## Recommendation

Close P5.0-SR1 and P5.0-SR2. Treat the required Package 5.0 security design
review as delivered, with **no readiness recommendation** until the named
operational evidence, assumptions, decisions and Blocking P5.0-R5 disposition
are complete. Package 5.0 remains `not ready`; implementation and migration
`0014` remain unauthorized.

## Checks

- reviewed revision-12 R11 handback, package-plan security/provenance/identity
  sections, logical-schema constraints and updated security brief;
- cross-document targeted search for every finding, control, residual and test
  identifier;
- `git diff --check`: required after controlled-record updates.

No Python, web, Node or privileged host suite was required for this
documentation/design re-review. Earlier current-tree regression evidence is not
relabelled as operational Package 5.0 evidence.
