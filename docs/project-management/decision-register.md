# Decision register

Status date: 2026-08-14 (I-07 and I-08 ruled; P3.G1 remediation remains open)

The authoritative decision text is
[`docs/discovery/open-decisions.md`](../discovery/open-decisions.md). This file is
the management index: it identifies what remains actionable, who owns it and
which milestone it blocks. It does not restate or supersede a ruling.

| Decision | Status | Accountable role | Required before | Management action |
|---|---|---|---|---|
| OD-03 | Partly answered | Product Owner | Phase 5.3 | Close remaining downtime/living-cost behavior before package readiness |
| OD-04 | Partly answered | Product Owner | Phase 5.3 and Frank-interest job | Define remaining lender behavior and acceptance examples |
| OD-05 | Open | Product Owner | Phase 5.6 crafting | Rule whether fancy meals incur the downtime percentage |
| OD-09 | Open | Product Owner | Phase 5.5 learning | Set disguise/forgery learning cost policy |
| OD-16 | **Closed 2026-08-12** | Product Owner / Security Reviewer | Phase 3 | `/info` is ephemeral and limited to linked characters plus Guild Council |
| OD-17 | **Closed 2026-08-12** | Product Owner / Security Reviewer | Phase 3 planning | Attribute legacy mutations through the Phase 3 gate; the first post-acceptance deployment requires verified `character_access` and precedes every later feature deployment |
| OD-25 | Verification open | Operations Owner | Production readiness | Verify Foundry network exposure and record evidence |
| OD-28 | Partly implemented | Product Owner | Phase 5.5 | Define auditable tribute-item mechanism |
| OD-39 | Open | Product Owner / Security Reviewer | Phase 5.7/5.8 cutover | Close unauthenticated trade/sale mutation policy and interim control |
| OD-41 | **Closed 2026-08-02** | Product Owner / Acceptance Authority | Phase 2 remediation | ADR 0008 rejected; the controlled migration register assigns every Sheet-era field, including `character.downtime_progress`, to one typed owning package |
| OD-42 | **Closed 2026-08-02** | Data Owner / Acceptance Authority | Phase 2 remediation plan approval | Ruled: display names are not unique identities; multiple characters may share one; stable character IDs and external Actor IDs provide identity; any legacy name-based candidate lookup fails closed when more than one candidate exists. **No unique display-name constraint is added.** Closes I-05. Package R2 corrects the single-value claim lookup to return every candidate and refuse on more than one |
| OD-43 | **Closed 2026-08-13; design accepted at P3.G0** | Product Owner / Security Reviewer / Acceptance Authority | Phase 3 P3.G0 | Peter accepted [ADR 0010](../adr/0010-provider-neutral-identity-and-emergency-administration.md) and the complete remediated P3.0 baseline after Codex architecture/security re-review. Acceptance includes corrected N-43, widened N-65, new N-67, account-aware audit attribution, mapping provenance and R-38. P3.1 is authorized subject to its disposable-PostgreSQL readiness condition. |
| OD-44 | **Closed 2026-08-14** | Product Owner / Security Reviewer / Acceptance Authority | Phase 3 P3.G1 | Peter approved the durable one-way OAuth completion binding in the [I-07 decision](../review/phase-3-p3-1-sm-01-completion-binding-decision.md): a unique, required `sessions.oauth_transaction_id` for Discord OAuth plus an atomic `completion_claimed_at` claim in the provider-I/O-free session transaction. No reverse `oauth_transactions.session_id` is added. **Implemented 2026-08-14** as migration 0009 with the required PostgreSQL concurrency, constraint, rollback and mutation evidence; the unique index is scoped to non-rotated sessions so N-08 rotation remains possible, declared for confirmation in `../review/phase-3-p3-1-od-44-remediation-submission.md`. **Confirmed 2026-08-14** (decision record §8): Peter approves that scoped index as the authoritative interpretation, conditionally on rotation integrity — one successor per predecessor, a rotation's account, authentication method and OAuth binding equal to its predecessor's, only a live unrotated predecessor rotatable, atomic insert-and-revoke, deterministic concurrent rotation, no arbitrary session labellable a rotation, and break-glass rotations unbound. The same ruling covers the re-review finding that the claim did not bind the provider. Implemented 2026-08-14 in migration 0009 and the OAuth, session and provider boundaries; see `../review/phase-3-p3-1-od-44-provider-binding-remediation-submission.md`. Independent and distinct security re-review remain required. |
| OD-45 | **Closed 2026-08-14** | Product Owner / Acceptance Authority | Phase 3 P3.G1/P3.G2 | Peter approved the [I-08 allocation](../review/phase-3-p3-1-tc-bg-05-http-evidence-decision.md): service/constraint portions remain at P3.G1; direct-HTTP portions of TC-BG-05b/c/e are mandatory blocking evidence at P3.G2 against the real P3.2 routes. This is not a waiver and does not authorize early P3.2 work. |

**OD-44 addendum, 2026-08-15 (no decision changed).** The OD-44 ruling's condition
that "only a live unrotated predecessor" may be rotated is recorded here as having
required two corrections to be true of the implementation, both now made and
neither yet re-reviewed: the rotation liveness predicates on 2026-08-14, and the
same class in the idle refresh on 2026-08-15, which additionally applied N-06's
idle window to break-glass sessions. The clarified reading of N-07, N-08 and N-15
that follows from the ruling is recorded in the numeric policy register; **no
accepted numeric value changed**, so this is an addendum and not a change request
under that register's §5. See
`../review/phase-3-p3-1-od-44-session-lifetime-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

**OD-44 addendum continued, 2026-08-15 later the same day (no decision changed).**
Codex's independent implementation and security re-reviews of that submission
returned one blocking finding: the idle-policy correction had been made in the
session service while the repository API still accepted a refresh duration and an
authentication method as independent arguments, so N-15's 15-minute window could
still be bypassed by a caller naming a break-glass row's true method beside N-06's
duration. The correction removes the duration from the API at both layers and
selects it inside the atomic statement from the persisted `auth_method`, using an
immutable validated policy injected once at the composition root. **No accepted
numeric value changed and no decision changed**; N-06 and N-15 keep their values and
configuration remains their source. This also reverses one alternative recorded as
rejected in change record C-P3.1-G — "deriving the idle duration inside the
repository" — on the ground that the objection was to adapter-owned *constants*,
not to configuration-owned policy consumed by the adapter. See
`../review/phase-3-p3-1-od-44-session-touch-policy-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

**OD-44 addendum continued, 2026-08-15, third entry of that day (no decision
changed).** Codex's independent re-review of the preceding submission returned one
blocking finding, and it is the same authority in a third position rather than a
new one. Removing `idle` and `expected_auth_method` from the repository API had
moved the method-to-duration pairing into `SessionIdlePolicy`'s public dataclass
constructor: a complete, duplicate-free, positive mapping assigning N-06's
60-minute window to *every* method satisfied every invariant that constructor
validated, so a repository built with it selected 60 minutes for persisted
WebAuthn and recovery-grant rows and N-15's 15-minute limit was bypassed again, up
to the 60-minute emergency absolute bound. Two statements in the preceding
submission — that no supported API could pair a method with another policy's
duration, and that policy was built once and injected — were false; the second was
false of the composition as well, since `SessionService` derived its own policy
while `WebComposition.services()` derived another for the repository. The
correction closes construction rather than adding a predicate: the policy has no
public constructor, its only factory takes `SessionSettings`, the mapping is
derived internally from `AuthMethod.is_break_glass`, and one instance is built at
the composition root and injected into both the repository and the service.
**No accepted numeric value changed and no decision changed**; N-06 and N-15 keep
their values, `SessionSettings` remains their sole source, and every pair of
values the configuration contract accepts — including an ordinary window shorter
than the emergency one — maps by method classification. No schema change and no
migration edit was required. See
`../review/phase-3-p3-1-od-44-session-idle-policy-construction-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

**OD-44 addendum continued, 2026-08-15, fourth entry of that day (no decision
changed).** Codex's independent re-review of the preceding submission returned
three counterexamples that survived it, and their combined lesson is recorded here
because it changed the *shape* of the implementation rather than a decision. (F1)
`from_settings()` validated only positivity while `SessionSettings` was a public
frozen dataclass with no construction-time validation, so an out-of-register
settings object was accepted and the derived policy gave both break-glass methods
sixty minutes; closing the policy's constructor was beside the point while the
numbers it read were unconstrained. (F2) The refresh SQL was generated by
iterating the policy's public, overridable `__iter__`, so a subclass inheriting
the supported factory replaced the mapping the database used while the
service-facing method still reported fifteen minutes — ordinary Python
subclassing, which the preceding submission wrongly characterised as out-of-scope
forgery. (F3) `SessionService` accepted a policy beside the repository and
required no relationship between them, so correct production wiring was a
convention rather than an invariant. The correction removes the extensible
boundary instead of guarding it: `SessionIdlePolicy` is deleted, `SessionSettings`
enforces the accepted register in its own constructor, `SessionRepository` derives
and owns the bounds, `SessionService` reads the repository's, and which window a
method receives is an explicit classification table that refuses an unclassified
method at startup rather than defaulting it. **No accepted numeric value changed,
no decision changed, no configuration variable was renamed and no deployment value
moved**; N-04, N-06, N-07, N-15 and N-66 keep their values and `SessionSettings`
remains their sole source, now validated at every construction rather than only at
environment load. No schema change and no migration edit was required. See
`../review/phase-3-p3-1-od-44-session-bounds-construction-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

**OD-44 addendum continued, 2026-08-15, fifth entry of that day (no decision
changed).** Codex's independent re-review of the preceding submission returned
**one** blocking counterexample, described from two perspectives — F1 in the
implementation review and S1 in the distinct security-focused pass. It is recorded
here because it is a lesson about where an accepted policy is *defined*, not about
what it says. `SESSION_CEILINGS` had given both enforcement gates the same bounds
and left each to state independently what a value of these fields may **be**:
`SessionSettings.__post_init__` required an actual `int`, never a `bool`, positive
and within its ceiling, while the derived-policy gate restated the rule as the two
ordering comparisons `value < 1` and `value > ceiling`. Two ordering comparisons
are not a whole-number rule — `float("nan")` makes both false — so a non-finite
`max_sessions_per_account` survived `SessionPolicy.derive()` and
`len(live) >= maximum` was false for every live-session count, leaving **N-66
inoperative**. The route was ordinary: `derive()` accepts `SessionSettings`
subclasses deliberately, so a subclass whose inherited `__post_init__` observes
the valid stored integer can answer differently on the single later derivation
read. The correction makes the rule **one runtime definition** rather than a third
restatement: `session_policy_problem`/`session_policy_problems` live beside
`SESSION_CEILINGS` in `application/web/config.py`, and both gates call them; the
accepted type is recorded in the numeric policy register as `int` and never
`bool`, with floats refused as a class. **No accepted numeric value changed and no
decision changed**; N-04, N-06, N-07, N-15 and N-66 keep their values and their
sole source. No schema change and no migration edit was required. See
`../review/phase-3-p3-1-od-44-session-policy-numeric-validation-remediation-submission.md`.
Independent and distinct security re-review still block P3.G1.

All other OD entries marked closed or ruled remain decisions, not open actions.
The Delivery Lead reviews this index before baselining every phase. A decision is
closed only when the authoritative OD entry records the ruling, date, rationale
and affected requirements; an implementation does not silently make policy.
