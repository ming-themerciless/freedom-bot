# Decision register

Status date: 2026-08-12

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

All other OD entries marked closed or ruled remain decisions, not open actions.
The Delivery Lead reviews this index before baselining every phase. A decision is
closed only when the authoritative OD entry records the ruling, date, rationale
and affected requirements; an implementation does not silently make policy.
