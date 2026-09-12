# Package 5.0 — reserved disposable laboratory direction

Date: 2026-09-10. Author: Codex. Change record: C-P5.0-LAB-1.

## Decision and scope

Peter agreed in conversation to an exclusively reserved disposable environment,
trusted host administrators and explicitly scoped adversarial cases, and asked
Codex to proceed after assessing repercussions. Codex recommends proceeding:
this removes the proposed VM controller, image pipeline and libvirt management
boundary from Package 5.0's critical path. It does **not** guarantee a completion
date or establish that the target satisfies the prerequisites.

This records authorization for the direction, documentation and the bounded
local Claude remediation in the linked prompt. It does not assert that a host
has been reserved or inspected. ADR 0011 stays Proposed and is deferred from
the current work; its findings remain historical, unresolved findings against
that alternative. No VM implementation or feasibility work is needed now.

The September 2 evidence-only exception remains the basis for minimum synthetic
probes. Production OD-63/64/65/66 controls, schema, authority, security and
recovery requirements are unchanged. OD-62 and Package 5.0 readiness remain
separate decisions. No product implementation, migration 0014, deployment,
cutover, new operational permission or execution digest is approved here.

## Boundary to implement and demonstrate

Use the already named disposable target, oracle-test, subject to its existing
identity, synthetic-data and topology checks. Reserve the **whole host**, including
freedom_test and freedom_dev, for one accountable executor during a run. Other
agents, maintainers, CI, synchronization, dependency updates and database suites
must not perform independent work there during the reservation. Host
administrators are trusted to obey this rule; this is an operational exclusion,
not a claim that root is technically unable to interfere.

The bounded implementation must combine an owner/run/target/release record with
one host-wide admission lock used by all project test entry points. A lock alone
cannot establish that unmanaged writers are absent. Before mutation, inventory
relevant sessions, test processes, timers and services; account for each writer
as a required service, a reviewed test process or a reason to refuse. Never kill
an unknown process or disable an unknown service to obtain admission. No polling
scheme is to be described as proof against malicious host root.

Reservation states are requested, admitted, running, recovering, released or
quarantined. A crash, expired reservation or released process lock does not imply
that child processes or server transactions ended. No automatic takeover:
an uncertain run stays quarantined until the operator establishes termination,
accounts for residue and verifies restoration or separately approved rebuild.
Use the existing command/run deadlines; specify any missing reservation deadline
and recovery owner in the exact pre-execution plan. This is a single-host
operational record, not a distributed lease service.

Experimental identities and processes are **not** made trusted by this decision.
Each adversarial case names its identity, capabilities, writable objects, timing,
expected observation and positive control. Test concurrency required by the
package remains inside that case. Quiesce those processes before dependent
cleanup; do not infer quiescence from the parent command exiting. Unknown or
uncontained writers make the affected evidence inconclusive and block reuse.

Keep reviewed source and recovery inputs outside experimental writable paths.
Preserve capture-before-mutation, exact verified bytes on restore, destination
custody, configuration order, reload and verification. If a case can modify the
recovery source, staging name or destination, reservation alone does not fix it:
use the previously required bounded protection or refuse that case. A deliberately
root-capable case needs its own accounting of possible effects; administrator
trust does not make the experiment harmless.

## Repercussions and controls

| Repercussion | Required treatment |
|---|---|
| Whole-host reservation reduces test availability | Serialize runs and publish owner/state; do not add another environment automatically. Existing bot/web serial execution remains mandatory. |
| Unmanaged process or stale lock undermines exclusion | Inventory before admission; durable quarantine on uncertainty; no timeout-based takeover or guessed cleanup. |
| Test-created writers survive commands | Prove the relevant process/service/transaction has ended before dependent actions. Include crash and delayed-transaction tests. |
| Trusted administrators could still interfere accidentally | Cooperative admission plus operational reservation; detected interference invalidates affected results. Do not promise detection of every root action. |
| Disposable host is mistaken for permission to erase anything | Preserve pre-existing-object refusal and exact target checks. Rebuild is recovery only when separately authorized; it never turns an experiment into a pass. |
| Synthetic producer is mistaken for production verification | Label feasibility evidence separately from implementation evidence; carry actual production-code tests into the implementation/release gate. |
| Setup reset invalidates target facts | Bind facts and evidence to exact target, boot/configuration where relevant, source digest and run; revalidate changed facts after reset. |
| Harness simplification weakens production controls | No change to production threat model, immutable audit, journal, authorization or recovery acceptance. Explicitly trace every retained requirement. |

## Resolve the dependency before declaring progress

The three missing C-7 producers are `JNL-51-PROVENANCE-OMITTED`,
`JNL-47-NO-GENERATION-ON-FAILURE` and `JNL-47-RECOVERY-STATE`.
The September 2 exception permits minimum synthetic evidence facsimiles; it does
not permit a second implementation of the production coordinator.

Claude must identify what each case can establish before product implementation.
Where a bounded facsimile can produce meaningful feasibility observations, build
that local producer with actual failure injection and controls. A supplied JSON
record, mocked success flag or future producer name is not a producer. A case
that necessarily proves future product behavior remains unverified and must be
assigned to its implementation acceptance test. If current readiness text requires
that future behavior before implementation, submit the exact criterion split and
impact for maintainer decision. Do not silently delete the requirement or claim
the laboratory direction approved that split.

Likewise, the twelve target facts remain unconfirmed until the existing Codex
preflight occurs after implementation review. Local work must not fill them by
assumption. Existing unconditional operational-ineligibility and missing-coverage
controls stay effective until independently reviewed replacements are accepted.

## Progress and checkpoint

One consolidated Claude handback must contain the small CRP fix separately,
the reservation/admission changes, an operation-level ownership and recovery
account, the three producer dispositions, required permission differences and
criterion-to-test traceability. Codex reviews before any privileged execution.
If the producer analysis cannot break the readiness dependency within existing
scope, return that single concrete decision with a recommendation; do not spend
another cycle expanding the harness or VM design.

Success is a reviewed route to real evidence with fewer infrastructure components,
not a larger document set or test count. No finding is closed by this direction.
The immediate assignment is
[Claude remediation prompt](phase-5-0-reserved-laboratory-claude-prompt.md).
