# C-P5.0-LAB-V6-D — provisioning-topology disposition handback — 2026-09-17

Peter approved decisions A–D on 2026-09-17. This bounded repository-local pass
records and implements those decisions. It performs no host action and returns
the result for independent technical and security review.

## Implemented disposition

- The accepted R4 review closes PR-20260916-LAB-V6R3-1.
- The unreproducible R3 digest `5602eb95…` is not approved and is superseded by
  the reproducible current artifact as review input only.
- V11 and `/opt/freedom-blades/evidence` are withdrawn. No ownership change to
  `/opt/freedom-blades` is made.
- `/var/lib/fb-evidence-p5-0` is the sole canonical disposable root `R` and is
  created by the reviewed concrete plan, not prerequisite provisioning.
- V12 explicitly defines persistent `/var/lib/freedom-blades`, `root:root
  0755`, before V4 and V5. The directory applier creates it with the same
  exclusive descriptor-bound, verified and guarded sequence as the other
  directory items.
- Production `EVIDENCE_ROLE` registration remains absent and is deferred until
  a real consumer receives separate implementation and review authority.

The prerequisite directory order is now V12, V4, V9, V5. V7 remains excluded;
I3 remains unconfirmed; `plan.is_executable` remains false; and
`reservation.REAL_EXECUTION_REFUSAL` remains unconditional.

## Evidence

Local only, `TEST_DATABASE_URL` unset, serial:

- focused V6 provisioning module: **124 passed**, 2 warnings;
- complete `tests/phase_5_0_evidence`: **2,367 passed**, zero failed, zero
  skipped, 2 warnings;
- structural guards: **31/31 passed**;
- scoped `compileall`: passed;
- `git diff --check`: passed.

The warnings are the existing unknown pytest configuration options
`asyncio_mode` and `asyncio_default_fixture_loop_scope`.

Covered artifacts were generated three times through the non-executing CLI.
All generations were byte-identical and the installed artifacts match them.
Manifest version remains 13; all 44 covered hashes independently match. New
review-input digest:

`7a3bc0a8291c91416d6a8164ff726d7fc39b7fc55f8eed623cc37abf09ed71ec`

This digest is review input only and must not be passed to `--execute`.

## Restrictions and next action

No SSH, synchronization, host inspection, provisioning, permission change,
database operation, controlled write verification, generated-vector execution,
real participant, real boundary/materializer or `--execute` was performed or is
authorized. Nothing was created under real `/run`, `/var/lib`, `/etc` or
`/opt/freedom-blades`.

Next action: independent technical and security review of this bounded
repository remediation. Package 5.0 remains not ready.
