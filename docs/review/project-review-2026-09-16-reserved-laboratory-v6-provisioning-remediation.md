# Codex independent review — V6 provisioning remediation — 2026-09-16

Submission: [C-P5.0-LAB-V6-R1 handback](phase-5-0-reserved-laboratory-v6-provisioning-remediation-handback.md).
Contract: [runner contract r6](phase-5-0-reserved-laboratory-runner-contract-r6.md).

## Recommendation

**Changes requested. Do not apply provisioning.** The submission correctly
makes V11 exact, keeps V7 excluded, preserves I3 and the execution stop, and
reports rather than conceals LAB-V6-1 through LAB-V6-3. One Blocking defect
remains: failures after `mkdirat` can leave a directory on disk without a
truthful, recoverable partial-application record.

## Finding

### PR-20260916-LAB-V6R1-1 — Blocking — post-creation failures can leave unreported provisioning residue

`DirectoryProvisioner._create()` creates the directory at
`execution/provisioner.py:752`, then opens it and performs `fchown`, `fchmod`
and read-back verification. Its recovery accounting catches only
`ProvisioningRefused`; an ordinary `OSError` from the post-`mkdirat` `open`,
`fchown`, `fchmod` or read-back path escapes. The directory already exists,
`apply()` returns no `ProvisioningRun`, `_created` may remain empty, and guarded
rollback therefore has no recorded identity for it.

The handled barrier-failure path is also reported incorrectly. `_create()`
adds the current item to private `_created` and raises; `apply()` catches that
refusal but returns only items completed before the current call. Thus
`ProvisioningRun.applied` and its `created` property omit a directory that the
same result says is visible and not durable.

Restricted local reproductions over temporary directories:

```text
injected os.fsync failure:
  path exists = True
  ProvisioningRun.applied = ()
  ProvisioningRun.created = ()
  provisioner.created = (V11 CREATED,)
  refusal = durability-barrier-failed

injected os.fchmod failure:
  raw OSError escaped
  path exists = True
  provisioner.created = ()
```

This contradicts the contract that a partial application returns what now
exists and preserves guarded recovery. It is Blocking because an operator can
believe nothing was created while a root-owned object remains at the target.

Required correction:

1. Define a closed result for every failure after successful `mkdirat`,
   including open, ownership, mode, read-back and barrier failures.
2. Translate operating-system errors to the closed refusal vocabulary without
   exposing paths or OS messages.
3. Include the current created/residual object in returned partial-state data,
   or add an equally explicit residual collection; private live-object state is
   insufficient.
4. Preserve identity evidence for guarded recovery whenever re-observation is
   possible. If identity is unknown, say so and refuse automatic removal.
5. Add fault-injection regressions at post-`mkdirat` open, `fchown`, `fchmod`,
   read-back and parent `fsync`, asserting residue, returned state, later items
   not attempted, and rollback behavior.

The existing partial-application test encounters a pre-existing wrong-type
object in a later item; it does not inject a failure inside creation. All 45
focused tests pass while both reproductions remain.

## Other dispositions

V11's `root:root 0700` definition and identity trace are internally coherent;
V7's exclusion and the absent-record refusal are correct; verification remains
read-only and cannot close I3; unsafe or absent parents correctly refuse.

LAB-V6-1, LAB-V6-2 and LAB-V6-3 are genuine maintainer stop conditions. V11
must not be applied while its authoritative root and consumer remain
unresolved. The parent check should continue to test the actual provisioning
identity separately from the declared owner. If the `/var/lib/freedom-blades`
hierarchy is retained, its parent should be proposed as an explicit unapproved
item, never created implicitly. `expected_children=("runs",)` is correct while
V7 is excluded and must change with a later V7 release. The pre-`rmdir`
emptiness check is acceptable defense in depth.

## Evidence and limits

Authorized local checks with `TEST_DATABASE_URL` unset:

| Check | Result |
|---|---|
| Focused provisioning tests | **45 passed**, 2 pre-existing warnings |
| Complete Phase 5.0 evidence suite | **2,288 passed, zero skipped**, 2 warnings |
| Guard suite | **31/31 passed** |
| `compileall` | passed |
| `git diff --check` | clean before this review record |
| Injected `fsync` and `fchmod` failures | Blocking behavior reproduced |

No SSH, synchronization, target inspection, provisioning, permission/group
change, `systemd-tmpfiles`, controlled write, database operation, participant,
boundary/materializer, generated-vector execution or `--execute` was used. No
PostgreSQL evidence was produced. The review-input digest remains unapproved.

V6 remains performed but not closed; I3 unconfirmed; V7 excluded; V8/V10
unperformed; `plan.is_executable` False; C-7, EH-R16-1, LAB-R6, LAB-X1,
P5.0-R5 and OD-62 Open; Package 5.0 not ready.

## Next action

One bounded repository-local remediation of PR-20260916-LAB-V6R1-1, followed
by independent re-review. No host provisioning follows automatically.
