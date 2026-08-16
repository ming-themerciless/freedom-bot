# Claude prompt — Phase 3 P3.0 remediation after Codex review

Use this prompt from `/opt/discord-bots/freedom-bot` in a fresh Claude Code
session.

---

Remediate **Phase 3 package P3.0 documentation and design only** after the Codex
architecture/security review and Peter Duscha's 2026-08-13 decision. Do not
start P3.1, add runtime code, dependencies, migrations, routes, services or
deployment configuration. Do not contact external services, inspect secrets or
production data, or edit the frozen prototype.

Read completely before editing:

1. `AGENTS.md`, `.agents/AGENTS.md`, `CLAUDE.md` and
   `docs/implementation-plan.md`;
2. `docs/review/phase-3-delivery-plan.md`;
3. `docs/review/phase-3-p3-0-claude-prompt.md` and
   `docs/review/phase-3-p3-0-submission.md`;
4. every Phase 3 contract under `docs/contracts/` and ADR 0010;
5. migrations 0001–0005 and the current audit, authorization, snapshot-import
   and repository models/tests relevant to these findings; and
6. the P3.G0 decision in the change log, status, decision register and numeric
   policy register.

Peter's decision is authoritative:

- D-1 separate `freedom-worker`: approved.
- D-2 apply as a durable job: approved, subject to retry-state remediation.
- D-3 tighter break-glass surface: conditionally approved. Emergency authority
  must not be convertible into later Council, character or import authority.
- D-4 numerics: N-30–N-42 and N-44–N-66 provisionally approved; N-43 withheld.
- D-5 ADR 0010 direction: conditionally approved, pending the audit-attribution
  and break-glass corrections below.

## Blocking finding 1 — account attribution versus the legacy audit constraint

The proposed `actor_platform_account_id` check does not replace migration
0001's `human_action_has_an_actor`, which still requires a Discord user ID for
every human capability. A Discord-independent break-glass audit insert would
therefore fail.

Revise the schema and migration contracts so new account-attributed human events
are legal without rewriting any historical row and without disabling the
append-only mutation trigger. Define explicit, visible DDL that replaces or
renames the old check with an account-aware constraint, preferably staged with
`NOT VALID` where appropriate. Preserve all existing historical rows and both
machine-capability cases. Cover `audit_events` and audit any analogous legacy
constraints on `foundry_snapshots` and `snapshot_imports`; do not assume they
have the same shape. Add named real-PostgreSQL tests proving:

- old Discord-attributed history remains readable and unchanged;
- new ordinary-provider and break-glass account attribution inserts succeed;
- an unattributed human action is rejected;
- system/service-principal actions remain valid; and
- `UPDATE`/`DELETE` append-only denial still holds for runtime and owner roles.

## Blocking finding 2 — indirect Council escalation from break-glass

R-33 currently lets `BG` create arbitrary role-capability mappings. TC-BG-05
even treats success as expected. A compromised emergency session can map a role
it controls to Council, log in through Discord, and then apply imports.

Keep D-3's approved narrow emergency surface, but define a server-side allowlist
for administrator-continuity repair that cannot create, alter or prepare a
mapping conferring `guild_council`, character ownership, DM/game authority or
import authority. Do not rely on the current session's short-circuited
capability set as the only control. Align the route matrices, application-service
authorization, ADR D9, state machines, threat model, view models and tests.
Replace TC-BG-05 with direct-service and direct-HTTP negative tests proving no
sequence of BG mapping changes followed by ordinary login yields Council/import
authority. State exactly which mapping operations BG may perform and why each is
needed for administrator continuity.

## Blocking finding 3 — unreachable job attempt exhaustion

The reaper requeues only when `attempts < 3`; after the third lease expires the
job remains `running`. A fourth claim also conflicts with `attempts <= 3`.

Redesign N-43 and SM-05 with one unambiguous meaning for `attempts`. Prefer an
atomic reaper transition that requeues an expired lease while attempts remain
and moves the exhausted attempt directly to `failed` with
`attempts_exhausted`; do not depend on an impossible fourth claim. Supply the
exact guarded SQL/pseudocode, constraint-compatible states, concurrent-reaper
behavior and lost-worker behavior. Update TC-JOB-05 and TC-JOB-13 to exercise
attempts one through exhaustion using real PostgreSQL, including two concurrent
reapers and proof that no job remains indefinitely `running`.

## Important finding 4 — PKCE verifier contradiction

The route contract says the OAuth transaction stores hashes of both state and
verifier, while the schema correctly says the verifier is encrypted because it
must be recovered for the code exchange. Make every contract consistently say:
state is hashed; the PKCE verifier is encrypted with the approved authenticated-
encryption boundary and deleted on consumption/retention expiry. Add or update a
named test proving plaintext is absent, decryption is bound to the transaction,
and callback can supply the original verifier exactly once.

## Reconciliation and handoff

- Search every P3.0 artifact for assumptions invalidated by these fixes and keep
  route, schema, state, threat, numeric and test terminology consistent.
- Preserve D-1/D-2 and all provisionally approved numeric values except the
  necessary corrected N-43 definition. Do not silently change another accepted
  policy.
- Keep ADR 0010 marked conditionally accepted and P3.G0 open. Do not mark P3.1
  authorized or the remediation accepted.
- Update management records only to say remediation was submitted for re-review.
- Create `docs/review/phase-3-p3-0-remediation-submission.md` containing a
  finding-by-finding change map, files changed, decisions preserved, commands
  and exact outcomes, checks not run, and a request for Codex independent
  architecture/security re-review.
- Run repository-local documentation/link/policy checks, `git diff --check`,
  relevant narrow tests if documentation checkers exist, and the full available
  suite only if required by the repository instructions. Report skips and
  missing database evidence honestly.

End the handoff with exactly:

`P3.0 remediation submitted for Codex re-review; P3.G0 remains open and P3.1 has not started.`

---
