# Independent review — I12/V6 closure — 2026-09-19

## Disposition

Closure recommended and accepted. Every required I12/V6 read-only observation
matched its reviewed definition after the seven released prerequisite items
were applied. There was no discrepancy, refusal, unclassified result or
unaccounted residue, and the synchronized target matched all 45 reviewed source
digests.

Peter Duscha accepts the independent review of the I12/V6 evidence and closes
V6. Closure confirms only the approved read-only prerequisite survey. I3
remains unconfirmed and requires separate authorization; V7 remains excluded,
V8 and V10 remain unperformed, `plan.is_executable` remains false, and Package
5.0 remains not ready.

## Basis

The evidence records the required execution identity and group membership,
capability state, `protected_hardlinks=1`, mount and filesystem types, exact
object types, ownership, modes, identities and contents, safe parent ownership
and permissions, and the required absence of both V7 lifecycle names. The four
directory identities equal the identities recorded by the provisioning CLI.

V6 was deliberately scoped as a read-only prerequisite survey. It does not
prove that a real `linkat` succeeds and does not close I3. It also does not
confirm V8, V10 or I8, authorize lifecycle initialization or execution, approve
a digest, or advance a package gate.

The earlier one-pass `--exclude-from` synchronization deviation remains a
separate maintainer decision. It does not invalidate the V6 observations: the
target's 45 reviewed source digests matched the reviewed tree.
