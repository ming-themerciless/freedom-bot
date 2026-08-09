# Phase 2 owner recommendations

Date: 2026-08-10
Recorded by: Peter Duscha, who holds all four accountable roles
Prepared by: Claude, from the day's evidence; **each role's acceptance is the
Data/Security/Operations/Product Owner's own and is marked below as given or
outstanding**

Closeout runbook §13 asks for these four role recommendations before the gate
decision. They are recommendations to the Acceptance Authority, not the decision
itself, and the same person holds both — so the distinction is kept explicit
rather than collapsed.

## Data Owner

**Given 2026-08-10.**

I accept field profile **`2026-08-09.1`**
([review record](phase-2-field-profile-maintainer-review-2026-08-10.md)) and the
signed active-folder reconciliation attestation
([attestation](phase-2-data-owner-attestation-2026-08-09.md)): 32 of 32 Actors
accounted for, zero unexplained identity discrepancies, nothing applied, nothing
committed.

## Security Owner

**Outstanding — requires an explicit yes.**

The evidence offered for acceptance:

| Area | Evidence |
|---|---|
| Credential confidentiality | §8.1 both halves on module 1.0.5: no setting named for a credential, and the secret absent from the world state vended to an ordinary player. Rehearsal A §C |
| Credential lifecycle | A real rotation: new principal, old credential proven dead with `401`, old secret shredded |
| Browser origin | §8.2 positive **and negative** — the negative case had never been run. A removed origin refused the preflight and the browser never sent the body. Rehearsal A §D |
| Authorization | Submit-only scope applies nothing; an unauthenticated request writes no audit event; a refused submission writes exactly one |
| Restricted storage | Root anchoring and `link(2)` publication, accepted at the fourth re-review 2026-08-05; artifacts `0600`, named for their own digest |

Known limits, stated rather than buried: storage guarantees are proven against
substitutions performed by the test process, **not** by a cross-account
experiment or a multi-process stress test — neither of which is a gate
requirement. Finding RA-3 (a `401` on a large upload surfacing as
`network_failure`) is bounded to the `wsgiref` rehearsal launcher and is
referred to Phase 3.

## Operations Owner

**Outstanding — requires an explicit yes.**

| Area | Evidence |
|---|---|
| Deployment prerequisites | Module install requires no Foundry restart and caused no downtime; rollback is deleting the directory |
| Recovery | §9 lost-pin reconciliation **executed against PostgreSQL**, twice — synthetic and real. Corrected step 10 produced its stated outcome |
| Retention | D-c: 30-day maximum for unclaimed raw artifacts, earlier deletion once the rehearsal, retry or incident closes. Both real artifacts shredded the same evening |
| Temporary-file hygiene | Operations §5.6 procedure, proven against synthetic files |
| Performance | Change-log C-11: throughput ≤ 1,200 ms/MB, observed 587 real and 728 synthetic |
| Migration and restore | upgrade/downgrade/upgrade and backup/restore/rerun, 2026-08-05, plus direct restricted-role denial of `UPDATE`, `DELETE`, `TRUNCATE` |

One operations item is **not** closed: the temporary Caddy route published for
the rehearsal was still present after the first revert attempt, because the
backup it was restored from had been captured after the route was added. The
clean source is `Caddyfile.phase2-active-backup-2026-08-06`.

## Product Owner

**Outstanding — requires an explicit yes.**

Change-log entries for disposition: **C-3 through C-11**, including the two
ruled today — **C-10** (ECMAScript canonical key order) and **C-11**
(performance threshold restated per megabyte, amending C-9).

## Scope of these recommendations

They cover the Phase 2 package as it stands at the end of 2026-08-09/10. They do
**not** close the gate, and they do not substitute for the independent review,
which does not exist yet and which none of today's implementers can supply.

Signed: **_______________________** (Peter Duscha)

Date: **_______________**
