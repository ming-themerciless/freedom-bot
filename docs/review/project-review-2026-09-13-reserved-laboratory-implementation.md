# Codex technical and security review — reserved-laboratory implementation

Date: 2026-09-13. Authorization: C-P5.0-LAB-I.
Submission: [Claude handback](phase-5-0-reserved-laboratory-implementation-handback.md).
Design basis: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

## Recommendation

**Changes requested.** The bounded C-7 producer adapter, the shared lifecycle
validators, the real-filesystem record adapters and much of the descriptor and
barrier mechanism are useful implementation progress. They are not yet an
integrated implementation of r6. Two Blocking fail-open defects permit an
effect without the recovery or ownership binding the contract requires, and an
Important integration defect leaves every new enforcement object outside the
actual executor, CLI and six non-harness participant entry points.

C-7 remains unresolved, EH-R16-1 remains Open, `is_executable` remains False,
the twelve target facts remain unconfirmed, Package 5.0 remains not ready,
package-level P5.0-R5 remains Blocking and OD-62 remains Open. No digest is
approved and no execution, preflight or provisioning is authorized.

## Findings

### PR-20260913-LABI-1 — Blocking — a recovery record for the wrong destination still authorizes mutation

`RecoveryStore.publish()` accepts the caller's `sources` mapping without
checking that each record destination is the configuration object captured
through `configuration_role`. `_verify()` checks only the stored-copy digest.
The final decision then sets `mutation_permitted` solely from the five barrier
names. A durably published copy whose record says `/wrong/destination` therefore
authorizes M1 even though `restore_configuration()` will later refuse to restore
the actual PostgreSQL configuration file because its destination binding is
wrong.

Independent reproduction through the public mechanism returned:

```text
published= True mutation_permitted= True destination= /wrong/destination
```

This violates the governing recovery rule: the first configuration mutation
may occur only after the recoverable bytes **and all metadata needed to discover
and restore them** are durably published. A record deliberately rejected at
restore time is not a recovery basis at mutation time.

Required correction: bind the accepted source components and record
destinations to the reviewed configuration targets before creating the recovery
run directory or writing any object; reject missing, additional, duplicate or
cross-directory destinations; and make publication verification establish the
same destination/copy correspondence restoration consumes. Add a public
publication regression and a negative control showing that removing this
binding makes `mutation_permitted=True` again.

### PR-20260913-LABI-2 — Blocking — missing ownership records are treated as successful pre-checks

Both ownership comparisons are conditional on the recorded identity being
non-empty. `_open_and_verify()` proceeds to the inode ioctl when `_recorded`
has no `(directory_role, name)` entry. `remove_object()` likewise proceeds when
the identity is missing; it also reaches `unlinkat` unless the found identity is
both present and different. This changes the contract's prerequisite — “the
file is the object the creating step recorded” — into an optional comparison.

Independent reproduction created a file directly under the held journal
directory, never called `record_identity()`, and invoked the public
`remove_object()` method. The result was:

```text
removed_without_record= True recorded_identity= ''
```

An armed issuer with quiescence can therefore remove an object the run did not
create or record. The analogous flag path can issue `FS_IOC_SETFLAGS` against
such an unbound object.

Required correction: absence of a recorded identity and absence at the
pre-check must each refuse before an ioctl or removal; equality with a required,
non-empty recorded identity must be the only admitting branch. Add public tests
for set, clear and removal with a missing binding, plus the absent-at-pre-check
case and conjunct-level negative controls.

### PR-20260913-LABI-3 — Important — the mechanism is test-only and does not enforce any participant or executor path

The assignment explicitly requires executor descriptor issuance and integration
points for all seven participants. Repository search finds the new
`LaboratorySession`, `ParticipantRunLedger`, `RecoveryStore` and
`DescriptorBoundEffects` consumers only in their defining modules and the new
tests. The executable CLI still constructs the old `ExecutingRunner` with
`SubprocessBoundary` and `SystemMaterializer`; `ExecutingRunner` does not own or
invoke the new session, inventory, recovery store or effect issuer. No wrapper
for the bot suite, web suite, Foundry tests, synchronization, dependency update
or environment reset invokes the lock and ledger protocol. The descriptor
transfer declarations are similarly not connected to boundary launch.

Consequently the statement that the reservation and executor mechanism “exists
in code” is true only of isolated classes. It is enforced by no real entry
point, even if the unresolved execution refusals were later removed. Deferring
the plan generator's migration from `install` and `chattr` is not merely a
twenty-versus-twenty-two allowlist discrepancy: it leaves the reviewed command
vectors on the old pathname-based effects instead of the new descriptor-bound
ones.

Required correction: integrate admission, per-participant durable begin and
completion, descriptor issuance/transfer, independent recovery publication,
descriptor-bound effects, cleanup/restoration and terminal publication along
the actual call paths named by the assignment, while retaining the current
unconditional operational refusals. Replace the old generator effects and
remove their executable permissions as r6 §6.4 requires. Add structural and
behavioral tests proving each of the seven entry points cannot reach its first
effect without the shared protocol and that the executable branch uses the new
mechanism rather than the legacy boundary path.

## Disposition of the handback's design questions

- **D1:** `linkat` followed by `unlinkat` is technically acceptable for
  exclusive publication of these regular files if the contract is amended to
  name its two-syscall, two-name interruption state and tests retain the
  unexplained temporary. It is not an implementation of r6's stated
  `renameat2(RENAME_NOREPLACE)` syscall. V6 may cease to be a prerequisite for
  this publication only after that contract change; this review does not close
  or remove V6.
- **D2:** the short-lived `.`-relative listing descriptor is a reasonable
  mechanism, but it adds descriptor mode/use outside the accepted complete
  inventory. Amend r6 explicitly before accepting it; do not treat the
  implementation as retroactive authorization.
- **D3:** rejected as a scope boundary. Executor issuance, participant
  integration and the replacement of the old effects were explicit assignment
  items and are necessary for the mechanism to enforce anything.
- Reusing `lifecycle_storage`'s codec and validators is the right dependency
  direction. `DescriptorRefused` inheriting `ModelRefused` is an unfortunate
  infrastructure name, not a security defect in this bounded scope.
- Fixed refusal roles are acceptable only after caller-controlled run IDs are
  bounded before becoming role labels. The current broader integration gap
  prevents relying on the present call graph for that guarantee.
- Inventory ownership of long-lived descriptors is sound; a per-publication
  adapter should not close them.

## Independent evidence and limits

- Complete local synthetic harness: **2,074 passed, zero skipped**.
- `git diff --check`: passed before this review record was added.
- Two direct public-interface reproductions established LABI-1 and LABI-2.
- Interpreter: `/opt/discord-bots/venv-web/bin/python`, with
  `TEST_DATABASE_URL` explicitly unset under the task-specific local-only
  restriction.

No SSH, synchronization, host inspection, preflight, provisioning, permission
change, database operation, generated-vector execution, `--execute`, real
boundary/materializer use, deployment or service change was performed. The bot,
web and Foundry suites were not rerun. The implementer's other suite figures
remain implementer evidence rather than independent evidence from this review.

