# Decision — `oracle-test` one-host design semantics

Date: 2026-10-04  
Decision owner: Peter Duscha, Maintainer and Acceptance Authority  
Recorded by: Codex

## Decision

Peter Duscha accepts Codex's independent conclusion that Claude's
`BLOCKED DESIGN` return is valid and accepts OH-D-1 through OH-D-9 as follows.
The proposal remains inactive and is not accepted as a complete H-1 design;
Blocking findings `OH-H1-D3-1` and `OH-H1-D3-2` require repository-only
design remediation and independent re-review.

| Decision | Accepted disposition |
|---|---|
| **OH-D-1 — repository source and transport** | The current workspace host is the Freedom-Blades production server and is prohibited as a source, controller, relay, destination, fallback or rollback target. `oracle-test` retrieves the pinned commit directly from the canonical Git remote. Public read access is used if available. If authentication is required, a narrowly scoped read-only repository credential may be used only after its own explicit installation and handling authority. Received bytes are verified locally against the accepted commit and pinned file digests before use. |
| **OH-D-2 — client placement** | Operator and executor processes run locally on `oracle-test` as `ubuntu`, reached through an interactive login session. No scripted remote controller is used. No model-provider credential is installed on `oracle-test` without separate authority. |
| **OH-D-3 — capture root and clock** | Accept a pass-specific capture root on `oracle-test`, on a filesystem accepted after H-0 and review. The loss of observer and clock independence is explicit evidence semantics, not silently preserved from the two-host design. |
| **OH-D-4 — synchronization** | Pass A contains no synchronization act. Retrieval/synchronization occurs before the pass and outside the trusted execution path; the trusted path verifies the resulting bytes. |
| **OH-D-5 — privileged Pass A acts** | Keep `NoNewPrivileges=yes`. A1-14, A1-15 and A1-31 through A1-33 are recorded `not_run (one-host: no privilege in RP-11)`. Do not weaken the unit to run them. |
| **OH-D-6 — `ubuntu` authority** | Accept that staging and activation separation is an authority boundary, not a privilege boundary, because `ubuntu` has unrestricted sudo on the disposable host. Every later record must state that limit and must not call ST-1 privilege-inert. |
| **OH-D-7 — activation authority** | A-2 authorizes `ACT` for exactly one pass and one boot. `DEACT` is mandatory and automatically authorized at every terminal state. No live Polkit grant may exist before A-2 or remain after the pass. |
| **OH-D-8 — rollback** | H-1 installation rollback is not automatic and requires separate authority so failure evidence remains intact. Activation cleanup is automatic and pre-authorized by A-2: on ACT failure or pass termination it removes both the live Polkit rule and `pass-a.json` under a crash-consistent, digest- and identity-guarded procedure, while retaining an immutable activation/failure record. |
| **OH-D-9 — record return** | The retained record on `oracle-test` is authoritative. The executor reports its exact SHA-256 and byte length, and every transferred copy is verified against them. No repository-write credential is implied. |

## Consequences

The design remediation must close both Blocking findings from
[`project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md`](project-review-2026-10-04-p5-r5-rp11-h1-oracle-test-one-host-design-amendment.md):

1. `OH-H1-D3-1`: make H-1 publication and recovery crash-consistent across
   every namespace and journal durability boundary; and
2. `OH-H1-D3-2`: specify ACT/DEACT identity, record, publication,
   partial-failure, automatic cleanup and retained evidence mechanically.

The remediation must incorporate the accepted OH-D dispositions without
turning them into host authority. It remains repository-only and must return a
revised inactive proposal for Codex re-review.

## Authority boundary

This decision grants no SSH, Git/network retrieval, credential installation,
host inspection, retained-path inspection, implementation, build,
installation, H-0/H-1/H-2, activation, evidence pass, rollback, cleanup,
commit or push authority. In particular, selecting direct Git retrieval does
not itself authorize network access or a credential on `oracle-test`.

D9-2 and D9-3 remain Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18 and H-1
remain open. RP-11 remains unwired and unmet; package RAID item `P5.0-R5`
remains Blocking; `plan.is_executable=False`; Package 5.0 remains not ready.
