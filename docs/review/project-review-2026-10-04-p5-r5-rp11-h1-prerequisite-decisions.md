# Static-launcher H-1 prerequisite decisions

Date: 2026-10-04  
Decision owner: Peter Duscha, Maintainer and Acceptance Authority  
Recorded by: Codex

## Decision

Peter Duscha accepts Codex's independent review of Claude's BLOCKED
PREPARATION return and makes the following prerequisite decisions. These
decisions select the direction for later design and assignments; they do not
activate host access, implementation, installation or H-1.

| Item | Decision |
|---|---|
| **U-1 — target host** | The H-1 launcher host is the **Freedom-Blades production server that also hosts production Foundry**. `oracle-test` remains the disposable test target and is not the H-1 launcher host. A later read-only host-facts assignment must record and bind the production server's technical hostname and machine-identity digest before any mutation. |
| **U-2 — executor and privilege** | **Gemini** is the intended H-1 executor under a later, separately accepted, digest-bound assignment with only the exact required privilege. This decision does not appoint or activate Gemini yet. |
| **U-3 — operator account** | The fixed non-root operator account is **`foundry`**. Later read-only host facts must confirm that account, its UID and primary group, and stop on any mismatch before implementation bytes or an H-1 assignment are finalized. No new `test` account is to be created. |
| **U-4 — launcher source** | Use a separately authorized pinned rebuild on the H-1 host and require the resulting image SHA-256 to equal `04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572`. Do not silently reuse retained R5 evidence as an installation source. |
| **U-5 — D9-2** | **D9-2 is Complete.** The I-7 independent review supplies the required XD-11 decode and its bindings; I-7-R1 closed the unrelated IC-1 issue without changing that evidence. |
| **U-6 — C11 direction** | Continue the reviewed **LB-2S direction with a root-installed bootstrap**. Before implementation, present the individual M-/D-decision wording and exact resulting bytes for review; this is not a blanket acceptance of unresolved proposal text. |
| **U-7 — H-1 property baseline** | H-1 must record the complete effective unit-property and manager-default baseline that H-2 will later re-report and compare, in addition to `FragmentPath`, empty `DropInPaths` and `NeedDaemonReload=no`. |
| **U-8 — standing authorization** | H-1 must not leave a usable Polkit start grant standing before the later pass authorization. Installation and activation must be separated through an explicit reviewed amendment to the present five-file H-1 design. |
| **U-9 — glibc/loader evidence** | Add an explicit numbered, version-specific glibc/dynamic-loader proof obligation covering the trusted loader inputs relevant to `/usr/bin/python3.12`. |
| **U-10 — citation-source access** | Version-specific upstream-source reading is approved in principle as read-only citation work after the target's versions are recorded. Its concrete assignment must name the versions, sources and output and must not access secrets or mutate a host. |

## Consequences and order

The target role and operator identity are decided. Their host-observed facts
remain verification inputs, not policy questions. A mismatch in the later
read-only observation is a stop condition and returns to Peter; it is not
permission to substitute another host or account.

D9-2 is Complete. D9-1, D9-4, PO-9, PO-14, PO-17, PO-18 and H-1 remain open.
PO-14 remains load-bearing: if the installed systemd version refutes it, LB-2S
is withdrawn for that version and the sequence stops.

The next proposed work is:

1. a separately authorized, read-only H-0 facts assignment on the named
   production server, with no environment, secret or application-data reads;
2. version-specific citation work, with the PO-14 limb first;
3. in parallel where safe, a reviewed H-1 installation/record amendment that
   implements U-7 through U-9, followed by the missing repository-only C11
   implementation slices;
4. a separately authorized pinned launcher rebuild and staging step;
5. a focused controlled commit and a fresh H-1 assignment preparation; and
6. independent review and Peter's explicit acceptance before Gemini is
   appointed or any H-1 mutation occurs.

## Authority boundary

This record is a maintainer decision, not an execution assignment. It grants
no SSH, host inspection, build, package, privilege, systemd, Polkit,
installation, service/database, capture-root, evidence-pass, cleanup, commit
or push authority. It does not authorize H-0, citation work, implementation,
launcher staging, H-1 or H-2. The retained R4 and R5 evidence remains
untouched.

