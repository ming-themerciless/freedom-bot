# RP-11 I1-R3 publication redesign proposal

Proposal ID: `C-P5.0-R5-RP11-I1-R3`

Date: 2026-09-28

State: **proposed requirements and implementation direction; repository-only;
not accepted, assigned, executable or operationally authorized**

## 1. Decision sought

Stop remediating the `O_TMPFILE` plus `/proc/self/fd/N` capability probe. Replace
that publication approach with an exclusively created **named staging inode**
and the repository's existing descriptor-relative, non-replacing hard-link
primitive. Retain both names as indexed objects; do not unlink the staging
name automatically.

This proposal responds to:

* **RP11-I1-2:** the current publication call returns `ENOENT` in Codex's
  execution context despite the reported platform prerequisites;
* **RP11-I1-R2-1:** a separate identity check followed by pathname `unlink`
  can remove an unchecked replacement; and
* the absence of `renameat2(RENAME_NOREPLACE)` from Python 3.12's `os` API and
  the repository's prohibition on adding a new `ctypes` syscall wrapper.

It does not amend the operational-evidence draft, production source or the
review manifest. Those changes require a separately assigned implementation
and independent review after this proposal is accepted.

## 2. Alternatives considered

| Candidate | Non-replacing publication | Python 3.12 standard library | Crash residue | Disposition |
|---|---:|---:|---|---|
| Current `O_TMPFILE` + `/proc/self/fd/N` link | yes | yes | final name only | reject: context-dependent `ENOENT` remains unexplained |
| Named staging + ordinary `os.rename` | no | yes | staging or final | reject: ordinary rename may replace the final name |
| Named staging + `renameat2(RENAME_NOREPLACE)` | yes | no | staging or final | reject for this package unless the repository separately approves a reviewed native wrapper |
| Named staging + hard link + automatic staging unlink | yes | yes | one or two names | reject: cleanup introduces the recheck-to-unlink race and an additional failure state |
| **Named staging + hard link + retained indexed alias** | **yes** | **yes** | **staging only, or staging plus final** | **recommend** |

The recommended route uses the same underlying no-follow, descriptor-relative
exclusive-link behavior already used by the reserved-laboratory D1 contract.
RP-11 must still receive its own contract and tests; prior review of another
caller is not acceptance of RP-11.

## 3. Proposed publication contract

For each record or index state, in order:

1. Open the destination directory through the reviewed descriptor walk.
2. Create one deterministic, object-specific staging name relative to that
   descriptor using `O_CREAT | O_EXCL | O_WRONLY | O_NOFOLLOW | O_CLOEXEC`,
   mode `0600`. An occupied staging name is a fail-closed stop and is never
   removed or replaced.
3. Bind and verify the opened inode: regular file, operator-owned, exact mode
   `0600`, link count one and the expected device.
4. Write the complete bytes with a checked loop, verify the final length and
   digest, and apply the file barrier.
5. Publish the final name with exactly one descriptor-relative, no-follow
   hard link from the staging name. The kernel's `EEXIST` refusal supplies
   non-replacement. No pre-check substitutes for this exclusive operation.
6. Apply the containing-directory barrier.
7. Open both names no-follow and verify that they identify the bound inode,
   are regular, operator-owned, mode `0600`, have link count two and expose
   the exact bytes and digest.
8. Record **both names and their shared inode identity** in the next durable
   index state. Only after that index publication succeeds may the object be
   admitted and the next act begin.

There is deliberately **no automatic unlink, rename, repair or alias cleanup**.
The staging name is not temporary after publication; it is a retained,
expected alias. This trades one additional directory entry per published
object for removal of both the procfs dependency and the cleanup race. It does
not duplicate file data on normal POSIX filesystems.

## 4. Interruption and admission semantics

The revised contract must distinguish these states without mutation:

* **Before staging creation:** no object exists.
* **After staging creation and before a confirmed final link:** the staging
  name is an unadmitted object. It is retained and recorded by finalization if
  finalization remains available; after process interruption it is discovered
  and reported, never adopted or completed.
* **After the final link but before the directory barrier or verification:**
  both names may exist and identify one inode. Both are unadmitted and retained.
* **After verification but before index admission:** both names remain
  unadmitted and retained.
* **After index admission:** both names are expected members of the final
  state. Their shared `(st_dev, st_ino)`, link count, types, modes, sizes and
  digests are checked by X-4 and B0-RA.

B0-RA's current blanket refusal of aliases must be amended narrowly: only the
one staging/final pair explicitly recorded for a published object is permitted
to share an inode. Any additional alias, missing member, identity mismatch,
wrong link count, unexpected name or unrecorded object remains a fail-closed
stop. An unadmitted object receives no inferred digest or admission.

## 5. Capability and portability check

The proposed §9.5.4 `O_TMPFILE`/procfs probe is removed rather than repaired.
A replacement pre-admission check, if retained, uses only a disposable
approved directory and the exact named-source hard-link primitive:

1. verify directory ownership, exact mode, emptiness and device;
2. exclusively create and verify one staging object;
3. completely write, synchronize and verify a fixed payload;
4. create one non-replacing final hard link;
5. synchronize the directory and verify both names and exact bytes; and
6. **do not perform race-prone cleanup**.

Because a successful check would otherwise leave names behind, the operational
design must choose one of two independently reviewed policies before the check
is implemented:

* use a fresh, pass-specific probe directory and retain it with both names as
  non-evidence until later maintainer-authorized recovery; or
* omit the mutating probe and treat filesystem/mount support plus the first
  real X-1 publication as the fail-closed capability test.

This proposal recommends the second policy. It avoids creating cleanup debt
before the capture root exists and tests the exact real operation rather than a
facsimile. X-1 failure leaves only the bounded, classified staging/final state
described above and issues no host command.

## 6. Required implementation slice after acceptance

A separately assigned implementer must:

1. amend every `O_TMPFILE`, `/proc/self/fd`, first-and-only-name, link-count-one
   and §9.5.4 statement in the operational draft consistently;
2. amend X-4, B0-RA, the handback binding and unadmitted-object grammar for the
   retained staging/final pair;
3. replace RP-11's unnamed-inode source implementation without changing the
   separately reviewed I3 caller;
4. remove the portability diagnostic or preserve it explicitly as historical
   diagnosis with no gate role;
5. add deterministic tests for every interruption boundary, occupied names,
   unexpected third aliases, missing pair members, wrong identity/link count,
   partial writes and barrier failures;
6. regenerate the review manifest and report every digest change; and
7. return the requirements and implementation together for independent
   technical, security, operational and evidence review.

No implementation may be wired to a command while C-11 or the launcher
environment remains unresolved.

## 7. Authority and current state

This proposal changes direction only. It authorizes no production-source edit,
manifest regeneration, host command, SSH, synchronization, network access,
database access, `sudo`, provisioning, controlled write, reboot, verifier,
evidence band, harness `--execute`, real participant, capture root, operational
probe, protected-artifact access, secrets scan, commit or push.

**RP11-I1-R1-1, RP11-I1-R2-1 and RP11-I1-2 remain Open.** RP-11 remains unmet.
Neither pass is executable or authorized. P5.0-R5 remains Blocking, OD-62 G-A
remains conditional, `plan.is_executable=False`, and Package 5.0 remains not
ready.
