# H-1 topology correction — local execution on `oracle-test`

Date: 2026-10-04  
Decision owner: Peter Duscha, Maintainer and Acceptance Authority  
Recorded by: Codex

## Correction

Peter Duscha supersedes the U-1 and U-3 dispositions in
[`project-review-2026-10-04-p5-r5-rp11-h1-prerequisite-decisions.md`](project-review-2026-10-04-p5-r5-rp11-h1-prerequisite-decisions.md).

The complete RP-11 H-1 installation and test/evidence workflow will run on the
dedicated disposable Linux test server **`oracle-test`**. The Freedom-Blades
production server, including its production Foundry service, is outside this
workflow and must not be inspected, changed, used as a controller or used as
an H-1 target.

| Item | Corrected decision |
|---|---|
| **U-1 — topology and target** | `oracle-test` is both the H-1 installation host and the local RP-11 test/evidence host. The earlier production-host launcher decision is withdrawn. No third Linux host and no macOS execution path are required. |
| **U-3 — operator account** | Use the existing unprivileged `ubuntu` account documented for `oracle-test`. Do not create `test`, `foundry`, `evidence` or another account for H-1. A later read-only preflight must re-observe the account, UID, primary group and repository ownership and stop on any mismatch. |

U-2 and U-4 through U-10 remain as decided, interpreted for the corrected
single-host topology. In particular, the pinned launcher rebuild under U-4 is
performed on `oracle-test`, only under later explicit authority, and must
produce SHA-256
`04218ed2d834c1c7abe417a850831d8956f087711befd692eefc2e61b2668572`.
D9-2 remains Complete.

## Design consequence

The current C11/D2 proposal language distinguishes a repository/controller
host from `oracle-test`. That distinction is no longer the selected topology.
Before implementation or H-1 assignment preparation, a repository-only design
amendment must:

1. define the local, one-host control and execution path on `oracle-test`;
2. remove assumptions that require SSH or rsync from a separate controller to
   `oracle-test` during the evidence pass;
3. preserve the closed environment, reviewed-byte, authorization, audit,
   failure and rollback properties of the selected LB-2S direction;
4. preserve U-7 through U-9, including the complete H-1 property baseline,
   absence of a standing pre-authorization Polkit grant, and the numbered
   glibc/loader obligation;
5. state explicitly that nothing in RP-11 H-1 authorizes access to or mutation
   of the production server; and
6. receive independent Codex review and Peter's acceptance before repository
   implementation or host work.

This is a simplification of deployment topology, not an assertion that the
existing two-host design can be executed unchanged on one host.

## Current boundary

This decision authorizes documentation of the correction only. It grants no
SSH, rsync, `oracle-test` inspection, retained-path inspection, build,
installation, package, privilege, `systemctl`, Polkit, service/database,
capture-root, evidence-pass, cleanup, commit or push authority. H-0, the
one-host design amendment, citation work, implementation, launcher staging,
H-1 and H-2 each require their later bounded authority.

