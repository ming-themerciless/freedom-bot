# Codex review — P5.0-R5 operational-evidence prompt R4 — 2026-09-27

Reviewer: Codex, independent of the Claude R4 remediation

Reviewed bytes:

* `docs/review/phase-5-0-p5-r5-operational-evidence-authorization-prompt.md`
* SHA-256: `20fa2ce07b391d430569df0e513d687859a1032cfc37bc4c6c0e4dda883b486b`
* R4 handback:
  `docs/review/phase-5-0-p5-r5-operational-evidence-prompt-r4-retention-verification-remediation-handback.md`
* R4 handback SHA-256:
  `0e387f9a7fb3b0e74e5c2052c77a59e0d46080dbe387e3d9ad356734c4aa9d8e`

## Result — changes requested

The R4 correction resolves OP1-R3-1 for the capture root, final state, index
chain, admitted records and bound stream files. B0-RA is correctly ordered
before B0-08, Pass B's X-1 and every Pass B host command.

One Blocking evidence-retention defect remains.

### OP1-R4-1 — deleted unadmitted files are not detected — Blocking

C-8 requires every unadmitted file to remain retained and unmodified. B0-RA
requires every name currently observed under `MI.capture_root_A` to be
accounted for by Pass A's final state *F*, but it does not require every
unadmitted name recorded by *F* to remain present. Deleting a named unadmitted
file before B0-RA reduces the observed name set and can therefore pass the
one-directional check.

B0-RA must require bidirectional name-set agreement:

1. every name observed under the root is accounted for by *F*; and
2. every name *F* accounts for — including every name it records as
   unadmitted — still exists under the root at the expected relative name and
   object type.

Absence, an unexpected name, duplicate/ambiguous representation, type
mismatch, or inability to enumerate and compare the complete sets must stop
Pass B fail-closed before B0-08.

Unadmitted files have no recorded content digest. The corrected draft may
claim only their presence, relative name and recorded object type where *F*
provides one. It must not claim that B0-RA proves their byte content unchanged.
That evidentiary limit must be explicit rather than silently treating presence
as content integrity.

The correction is requirements-only. Its exact enumeration, path-resolution
and comparison interfaces and their proof remain part of RP-11's later
implementation and review.

## Preserved conclusions

* OP1-R3-1 is otherwise resolved for the root, final index, index chain,
  admitted records and bound stream files.
* Barrier success is appropriately inherited from the digest-pinned Pass A
  handback because it cannot be re-observed from retained bytes.
* OP1-R2-1 and OP1-R2-2 remain resolved.
* RP-11 remains absent and unmet; neither operational pass is executable or
  authorized.
* P5.0-R5 remains Blocking, OD-62 G-A remains conditional,
  `plan.is_executable=False`, and Package 5.0 remains not ready.

No host command, suite, database operation, secrets scan or protected-artifact
access was performed for this review.
