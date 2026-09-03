# Package 5.0 pre-implementation evidence-harness authorization — draft

Date: 2026-09-02

Status: **Approved 2026-09-02; evidence harness only**

Decision owner: Peter Duscha, Operations Owner and Acceptance Authority

Executor if approved: Claude, Package 5.0 implementer and working Technical Lead

Reviewers: Codex, Security Reviewer and Independent Reviewer

## Decision requested

Authorize a temporary, narrowly bounded evidence harness whose sole purpose is
to determine whether the already approved OD-64 A, OD-65 B and OD-66 A/J-1
design can be implemented safely on the intended Linux/PostgreSQL topology and
to produce the operational evidence needed to resolve P5.0-R4 and P5.0-R5.

This is a change-controlled exception to the normal rule that implementation
waits for package readiness. It authorizes evidence scaffolding only; it does
not authorize Package 5.0 product implementation or any migration/cutover.

## Why a decision is necessary

The current controls form a circular dependency:

1. Package 5.0 cannot be ready while P5.0-R5 is Blocking.
2. P5.0-R5 cannot close without C-3/C-4 and journal/capability evidence.
3. The evidence runbook classifies those checks as requiring objects and tools
   that cannot exist until implementation is authorized.

Without a bounded exception, the gate cannot be satisfied honestly. Waiving
P5.0-R5, treating an unrun check as passed, or starting migration `0014` would
weaken a production-integrity gate and is not permitted.

## Authorized scope if approved

The executor may, only in a disposable or explicitly isolated evidence
environment:

- correct the operational runbook's A-5.0-3/A-5.0-4 taxonomy and turn its
  illustrative commands into reviewed, deterministic harness steps;
- create temporary `freedomcoord`, `freedomsheet` and `fbprobe` OS identities
  and the `freedomjournal` group with the approved membership matrix;
- create temporary PostgreSQL roles, a disposable database/schema facsimile,
  narrowly scoped peer/HBA and identity-map entries, and reload the disposable
  PostgreSQL configuration;
- create a disposable journal/probe hierarchy on a filesystem representative
  of the intended production journal filesystem;
- build only the minimum probe, verifier and synthetic schema objects needed to
  exercise C-3, C-4, the peer/HBA boundary, capability construction,
  append-only behavior, sandbox behavior, provenance omission/refusal,
  journal-generation validation and recovery paths;
- run transient systemd units, `chattr`/`lsattr`, `capsh`, controlled `fsync`
  failure injection and the specified positive/negative identity cases;
- perform the privileged read-only C-1 inspection of existing `sudoers`
  configuration and the read-only pre-change HBA/identity-map inspection;
- retain sanitized evidence artifacts under `docs/review/` that contain no
  secrets, credential contents, player data or unrelated host configuration;
  and
- destroy or explicitly inventory every temporary object after evidence
  collection, with cleanup failure treated as a stop condition.

The harness may use synthetic identifiers and data only. It must not use a
production Google Sheet, service-account credential, player record or live
character state.

## Explicit exclusions

Approval would **not** authorize:

- migration `0014` or any production schema migration;
- deployment or activation of Package 5.0 application code;
- creation of production coordinator, writer, journal, provenance or approval
  objects;
- modification or restart of the live bot, web, worker, PostgreSQL or Foundry
  services;
- modification of production `pg_hba.conf`, `pg_ident.conf`, `sudoers`, systemd
  units, filesystem attributes, accounts, groups or credentials;
- access to or mutation of the live Google Sheet, live Drive permissions,
  Discord, Foundry or production PostgreSQL data;
- an authority transition, cutover, rollback rehearsal against live state, or
  a binding OD-62 ruling;
- Package 5.1 or later work; or
- acceptance of R-5.0-8 or R-5.0-12 through R-5.0-16.

## Execution and review separation

- Claude writes and runs the mutation-bearing harness and supplies a complete
  handback.
- Codex reviews the harness before its first privileged execution, observes or
  reviews the privileged evidence, and independently decides whether the
  evidence supports closing P5.0-R4/P5.0-R5.
- Peter authorizes the disposable target and every production-host read. Any
  request to mutate a non-disposable host is a new decision and stops this work.
- The executor cannot close findings, confirm assumptions on their own, approve
  readiness or convert provisional OD-62 G-A into a ruling.

## Required sequence

1. Name the disposable target, filesystem and PostgreSQL instance. Prove no
   production credentials or data are present.
2. Correct the runbook taxonomy and submit the exact harness commands and
   cleanup plan to Codex for pre-execution review.
3. Complete privileged **read-only** discovery: C-1 and pre-change HBA/identity
   mapping. Stop on an unexpected broad grant or unsafe `sudoers` rule.
4. Provision disposable identities, groups, database roles/configuration and
   probe paths. Capture before/after inventories.
5. Run positive controls before interpreting negative results. An unexpected
   identity, capability mask, securebit, mount property or `errno` is
   `inconclusive` or failed, never passed.
6. Execute the C-3/C-4, peer/HBA, capability, sandbox, journal, provenance and
   recovery bands required by the approved design.
7. Clean the disposable environment. Record and stop on any residue that cannot
   be removed by the approved cleanup path.
8. Produce a traceable evidence handback. Codex independently reviews it and
   recommends closure, remediation or continued blocking.

## Stop conditions

Stop without broadening authority if:

- the target cannot be proved disposable or isolated;
- a command would read a secret or unrelated private host configuration;
- a production service, database, account, permission or external system would
  be mutated;
- the filesystem is not representative or does not enforce the expected
  append/immutable semantics;
- the launching capability bounding set cannot construct the declared E1-E8
  identities;
- a positive control fails, a refusal has an unexpected cause, or evidence is
  ambiguous;
- cleanup cannot restore the recorded starting state;
- the harness needs product code or schema beyond the minimum synthetic
  evidence facsimile; or
- a finding would need to be waived to proceed.

## Required handback

The executor reports exact commands, target identity, before/after state,
positive and negative results, capability masks and securebits, exact refusal
causes, PostgreSQL grants/configuration ordering, skipped cases, cleanup,
residue, secrets/privacy review and a criterion-to-evidence table. No passing
claim may rely only on a mocked method call or on output from a different tree
or host.

## Effect of approval

Approval authorizes only the bounded evidence work above. Package 5.0 remains
`not ready`; migration `0014`, production mutation, deployment, cutover and
Package 5.1+ remain unauthorized. After independent review, Peter separately
decides residual-risk dispositions, the binding OD-62 ruling, Package 5.0
readiness and implementation authorization.

## Approval record

- Operations Owner: **Approved — Peter Duscha**
- Acceptance Authority: **Approved — Peter Duscha**
- Decision: **Authorize the Package 5.0 pre-implementation evidence harness as
  drafted, with every scope limit, sequence requirement and stop condition above
  binding**
- Date: **2026-09-02**
