# Decision request — TC-BG-05b/c/e require direct-HTTP evidence that P3.1 cannot produce

**Prepared:** 2026-08-14 · **For:** Peter Duscha (Acceptance Authority,
Security Reviewer) · **Prepared by:** Claude (Working Technical Lead) ·
**Status:** **Option 1 approved by Peter Duscha on 2026-08-14. No P3.2 route is
authorized before P3.G1 closes.**

**Raised by:** Codex blocking finding 3 against P3.1, recorded in
`docs/review/Handover information`.

**Blocks:** the correctness of P3.1's TC-BG-05 evidence claim, and therefore
P3.G1.

---

## 1. The conflict, stated precisely

`docs/contracts/phase-3-test-traceability.md` requires direct HTTP evidence for
three of the five replacement break-glass escalation tests:

| Test | Level required by the accepted contract | Routes it must exercise |
|---|---|---|
| TC-BG-05b | **direct HTTP** | R-33, R-34, R-38 |
| TC-BG-05c | service **+ direct HTTP** | R-33, R-38, every Council and import route |
| TC-BG-05e | service **+ direct HTTP** | R-38 |

R-33, R-34 and R-38 are **P3.2** routes. The delivery plan's stop gate P3.G1
blocks P3.2 from starting, and `adapters/web/app.py`'s `DEFERRED_ROUTES` plus
`test_a_route_owned_by_a_later_package_is_absent_from_this_build` assert their
absence as a control. The evidence the contract demands at P3.1 therefore cannot
be produced at P3.1 without breaking the gate that P3.1 exists to reach.

The P3.1 submission recorded TC-BG-05a–05e as "Implemented, passing" in §10 and
then acknowledged in §10.1 that TC-BG-05b cannot be issued. Those two statements
are inconsistent, and the first is the one a reviewer reads. **That overstatement
has been corrected in the remediation submission ahead of this decision** — see
§4 below.

Service and database evidence is real and was produced: the escalation sequence,
the N-67 application refusal, and the check constraint with the application
bypassed entirely. It is **not** equivalent to route-level evidence. Only a
request issued at the route proves the authorization chain's *order* — that the
refusal happens before the service is reached, and that a forged submission
carrying no rendered form is refused rather than merely unrendered.

## 2. Options

### Option 1 — Reallocate the direct-HTTP portions to P3.2/P3.G2 (**recommended**)

Split each affected row into the portion P3.1 can prove and the portion its
routes own:

- TC-BG-05a, 05d and the **service and constraint halves** of 05b/c/e stay at
  P3.1 and are evidence at P3.G1;
- the **direct-HTTP halves** of 05b/c/e move to P3.2 and become **required
  evidence at P3.G2**, against the real R-33/R-34/R-38 with their real
  authorization dependencies.

The independent HTTP evidence still exists **before the affected production
routes can be accepted**, because those routes are accepted at P3.G2 and nowhere
earlier. Nothing is weakened; the evidence is placed at the gate that owns the
thing it tests.

**Condition that must be recorded with it:** closing P3.G1 does not accept the
break-glass HTTP boundary. The acceptance record must state that the HTTP halves
of TC-BG-05b/c/e are outstanding and are blocking evidence for P3.G2.

### Option 2 — A minimal contract-test route harness at P3.1

Register R-33/R-34/R-38 in a test-only application factory that wires the real
authorization dependencies.

Rejected on inspection. Either the harness reuses the real handlers — which do
not exist, since the handler *is* the P3.2 work — or it re-implements the
authorization chain in test code. The second produces evidence about the test
harness, not about the platform, which is precisely the "misleading evidence"
the handover warns against. A harness faithful enough to be evidence is a
production route with a different registration site, and adding it is the scope
expansion this option was meant to avoid.

### Option 3 — Change the package/gate order

Move R-33/R-34/R-38 (and the parts of P3.2 they depend on) into P3.1, or merge
P3.G1 into P3.G2.

Coherent, and the largest change: it enlarges the package under review, delays
the authentication-boundary gate that every later package depends on, and merges
two review scopes that were separated deliberately so a blocking authentication
finding could not be traded against read-path progress. Not recommended unless
you want the gates restructured for reasons beyond this finding.

## 3. Recommendation

**Option 1.** It is the least scope-expanding option, it preserves independent
HTTP evidence before the affected routes can be accepted, and it records the
outstanding evidence as a named P3.G2 blocker rather than losing it.

This required Acceptance Authority approval because it edits accepted contracts
(traceability and the delivery plan's gate allocation). That approval is now
recorded in §5. The correction below preceded the ruling and needed no contract
change.

## 4. What was corrected without waiting for this decision

Applied in `docs/review/phase-3-p3-1-remediation-submission.md`, because these
are corrections to a claim rather than changes to a contract:

- TC-BG-05a–05e are **no longer** described collectively as "Implemented,
  passing";
- each row reports its service, constraint, sequence and HTTP portions
  **separately**, with the HTTP portions marked **unrun, blocked on this
  decision**;
- P3.G1 is **not** marked ready or closed;
- no mocked function call is presented as direct-HTTP evidence anywhere.

If you approve Option 1, the traceability contract, the delivery plan's §11
allocation, the RAID and change records, the tests and the submission are updated
consistently, through a **dated controlled entry**. Historical accepted records
are amended by addition, not rewritten.

## 5. Acceptance Authority ruling — 2026-08-14

Peter Duscha approves **Option 1**. TC-BG-05a, TC-BG-05d and the service and
database-constraint portions of TC-BG-05b/c/e remain required P3.G1 evidence.
The direct-HTTP portions of TC-BG-05b/c/e are allocated to P3.2 and are blocking
evidence at P3.G2 against the real R-33, R-34 and R-38 handlers and their real
authorization chain.

This is a timing/allocation correction, not a waiver. P3.G1 does not accept the
break-glass HTTP boundary, and P3.G2 cannot close until the direct-HTTP evidence
passes. No test-only substitute route and no early P3.2 implementation is
authorized. This ruling resolves the decision blocker only; P3.G1 remains open
for the I-07 implementation and required re-review.
