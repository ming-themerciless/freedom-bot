# Package 5.0 — Gemini operational evidence runbook

**Prepared by:** Gemini (adversarial readiness analyst, per
`docs/review/phase-5-0-gemini-preimplementation-prompt.md`).

**Date:** 2026-09-01

**Last revised:** 2026-09-02 — authorization reconciliation. Peter Duscha
approved the bounded pre-implementation evidence harness in
`phase-5-0-evidence-harness-authorization-draft.md`. This revision corrects the
A-5.0-3/A-5.0-4 taxonomy and permits minimum disposable evidence scaffolding
under that authorization; it does not authorize Package 5.0 product
implementation, migration `0014`, production mutation, deployment or cutover.

**Authority:** This runbook remains a planning aid rather than an executable
script. The separately approved evidence-harness authorization permits Claude
to implement minimum synthetic/disposable scaffolding, but only after exact
commands, target and cleanup pass Codex pre-execution review. No command is
approved merely because it appears here, and no unexecuted check has passed.

Commands requiring elevation, a disposable environment, or external-state
mutation are marked with explicit authorization requirements. They may not be
executed without the authorization specified.

---

## Purpose

This runbook provides an ordered evidence plan for:

- **P5.0-R5** (Blocking risk: append-only capability not confirmed)
- **C-1** (incomplete check: `/etc/sudoers.d/` contents)
- **C-3** (not run: append-only capability probe)
- **C-4** (not run: OS identity and filesystem-access denial matrix — JNL-49,
  JNL-50, JNL-52)
- **G-EVIDENCE-1 pre-change discovery** (not run: `pg_hba.conf`/`pg_ident.conf`
  existing-file inspection before any Package 5.0 lines are inserted; this is a
  separate pre-provisioning step, not the C-4 matrix)

For each evidence item, this document states:

- Intended identity
- Prerequisites
- Expected safe result
- Expected refusal/failure result
- Cleanup and recovery steps
- Evidence captured
- Whether explicit authorization or elevation is required

---

## Evidence categories

Evidence in this runbook falls into four categories:

| Category | Definition | Who may authorize |
|----------|-----------|-------------------|
| **R** — Safe read-only host discovery | No elevation; no state change; no secrets | Any analyst with filesystem read access |
| **D** — Disposable-environment mutation | Requires a separately authorized disposable environment; creates host state that must be cleaned | Operations Owner authorization required before any D step |
| **P** — Privileged production-like evidence | Requires `sudo`, `systemd-run`, `chattr`, or equivalent on a production or production-like host | Acceptance Authority authorization required; Security Reviewer present |
| **E** — Evidence-harness scaffolding | Requires temporary host/database objects or probe binaries that do not yet exist | Permitted only by the approved bounded evidence-harness authorization after Codex pre-execution review; never production Package 5.0 implementation |

---

## Part 1 — C-1: `/etc/sudoers.d/` contents

**Relevant surfaces:** 9 (`freedom-journal-admin` sudoers drop-in), 6 (new OS
identities and sudoers).

**Current status:** Permission denied on 2026-08-29 for the identities that
performed prior review sessions. C-1 is recorded as incomplete. The package
plan §8.1 H-7 documents the denial.

### C-1-R-1 — Attempt read of `/etc/sudoers.d/` directory listing

**Category:** R (read-only, no elevation)

**Intended identity:** The analyst identity that has filesystem read access (the
current session identity).

**Prerequisite:** None. This is a safe, non-mutating probe.

**Command:**
```sh
ls -la /etc/sudoers.d/ 2>&1 || echo "DENIED: $(id)"
```

**Expected safe result:** A directory listing showing `freedom-coord-run` and
`freedom-journal-admin` drop-in files (once provisioned), with `root:root 0440`
or equivalent modes.

**Expected denial result:** `ls: cannot open directory '/etc/sudoers.d/':
Permission denied` and the current identity printed. This is the result recorded
in §8.1 H-7. Record the identity and the denial, do not retry with elevated
identity without P authorization.

**Cleanup:** None required.

**Evidence captured:** The directory listing (if accessible) or the explicit
denial. If accessible, each file's name, owner, mode, and byte count.

**Authorization required:** None for the read attempt. If denied, stop. Do not
attempt to work around the denial.

### C-1-P-1 — Privileged read of `/etc/sudoers.d/` (requires P authorization)

**Category:** P (privileged)

**Intended identity:** A role with `sudo cat /etc/sudoers.d/*` permission, or
root.

**Authorization required before running:** Explicit authorization from the
Acceptance Authority; Security Reviewer present or reviewing output.

**Prerequisites:**
- Explicit written authorization from the Acceptance Authority.
- Security Reviewer informed and available to review output.
- No service or session change made to the production host.

**Command (do not run without P authorization):**
```sh
sudo ls -la /etc/sudoers.d/
sudo cat /etc/sudoers.d/freedom-coord-run     2>/dev/null || echo "NOT FOUND"
sudo cat /etc/sudoers.d/freedom-journal-admin 2>/dev/null || echo "NOT FOUND"
```

**Expected safe result:** Two files, one per tool; each containing exactly one
line; no `NOPASSWD` for any action not explicitly specified; no wildcard in the
executable path; `log_output` present.

**Expected failure result:** Files absent (provisioning not yet run), or a file
contains unexpected rules. Record exact content; do not interpret; pass verbatim
to Security Reviewer.

**Cleanup:** None (read-only).

**Evidence captured:** Exact content of each file, verbatim. SHA-256 of each file.

---

## Part 2 — C-3: Append-only capability probe

**Relevant surfaces:** 10 (root-owned durable state hierarchy), 11 (probe arena).

**Current status:** Not run. Requires OS accounts (`freedomsheet`), the
`freedom-journal-admin` tool, `chattr` (or equivalent), and a host that has
completed the provisioning steps of §2.12. All of these are absent.

**Dependency:** C-3 is an assumption-confirmation exercise for A-5.0-5. It
cannot run until A-5.0-4's disposable OS identity/HBA environment exists and
the approved evidence harness has provisioned its minimum synthetic database
facsimile. **A-5.0-3 is the separate disposable Google Sheet/service-account
assumption for WP-13 and is not a prerequisite for this filesystem probe.**

### C-3-E-1 — `FS_APPEND_FL` capability probe (authorized harness; pre-execution review required)

**Category:** E (evidence that cannot exist before implementation)

**Intended identity:** `freedomsheet` (the writer's OS identity), not root.

**Authorization required before running:** The bounded evidence-harness
authorization is approved. Codex must additionally approve the exact commands,
named disposable target and cleanup plan before execution; the Security
Reviewer must review the resulting evidence.

**Prerequisites:**
- A separately authorized disposable environment with the OS identities
  provisioned per §2.12.2.
- `verify-capability` deployed and probed in `…/probe` with correct permissions.
- `…/probe` and `…/probe-ro` absent before the test begins.
- Root has set `FS_APPEND_FL` on the test target inside `…/probe`.
- The writer unit is **inactive**.

**Procedure (do not run without E authorization):**

Step C3-1 (root): Create `…/probe`; create a test file; set `FS_APPEND_FL` via
`chattr +a`. Verify with `lsattr`.
```sh
# (root) — do not run without E authorization
install -d -m 0770 -o root -g freedomsheet /var/lib/freedom-sheet-writer/probe
touch /var/lib/freedom-sheet-writer/probe/test-target
chattr +a /var/lib/freedom-sheet-writer/probe/test-target
lsattr /var/lib/freedom-sheet-writer/probe/test-target
```

Step C3-2 (freedomsheet): Attempt to open the append-only file with `O_TRUNC`.
Must receive `EPERM`.
```sh
# (freedomsheet) — do not run without E authorization
python3 -c "
import os, errno
try:
    fd = os.open(
        '/var/lib/freedom-sheet-writer/probe/test-target',
        os.O_WRONLY | os.O_TRUNC
    )
    os.close(fd)
    print('FAIL: open succeeded; FS_APPEND_FL did not refuse')
except OSError as e:
    if e.errno == errno.EPERM:
        print('PASS: EPERM received as expected')
    else:
        print(f'UNEXPECTED errno {e.errno}: {e}')
"
```

**Expected safe result:** `PASS: EPERM received as expected`.

**Expected failure result:** `FAIL: open succeeded` — means `FS_APPEND_FL` is
not enforced on this filesystem, and the append-only claim cannot be confirmed
by capability probe. This would make A-5.0-5 unconfirmable on this filesystem
type.

**Cleanup (root):**
```sh
# (root) — do not run without E authorization
chattr -a /var/lib/freedom-sheet-writer/probe/test-target
rm -f /var/lib/freedom-sheet-writer/probe/test-target
rmdir /var/lib/freedom-sheet-writer/probe
```
If cleanup fails, record the residue path and stop. Do not retry automatically.

**Evidence captured:** The exact output of each step; the filesystem type of
`/var/lib/freedom-sheet-writer` (`stat -f --format='%T'`); the `lsattr` output;
and whether `EPERM` was returned or not.

---

## Part 3 — C-4: OS identity and filesystem-access denial matrix

**Relevant surfaces:** 6 (OS identities), 10 (manipulation matrix), 11
(probe arena).

**Taxonomy note:** C-4 covers the OS identity and filesystem-access (capability)
denial matrix. It includes:

- **JNL-49 / JNL-50** — filesystem capability denial matrix (E-category).
- **JNL-52** — OS identity and group membership matrix (D-category).

C-4 / JNL-52 is the OS membership and filesystem-access check. It is **not** the
`pg_hba.conf` / `pg_ident.conf` authentication test. The database host-boundary
authentication evidence is a Band 2 matrix defined separately in the package plan
and logical schema; see the G-EVIDENCE-1 pre-change discovery step (Part 3a)
for the database configuration inspection.

**Current status:** Not run.

### C-4-D-1 — JNL-52: Membership matrix verification (requires D authorization)

**Category:** D (disposable-environment mutation)

**Intended identity:** root (to run `id`, `getent`, `namei -l` for each identity).

**Authorization required before running:** Operations Owner written authorization
for a disposable environment with OS accounts created per §2.12.2.

**Prerequisites:**
- Separately authorized disposable environment.
- OS accounts `freedomcoord`, `freedomsheet` created; group `freedomjournal`
  created; both accounts added to `freedomjournal` per §2.12.2.
- No other steps run (the membership check is the first step of provisioning per
  §2.12.5a algorithm D item 1).

**Commands (do not run without D authorization):**
```sh
# (root) — do not run without D authorization
# Step 1: Confirm freedomjournal membership
getent group freedomjournal
# Expected: freedomjournal:x:<gid>:freedomcoord,freedomsheet (exactly two members)

# Step 2: Confirm identity of each account
id freedomcoord
id freedomsheet
# Expected: each shows primary group matching its own group, supplementary
# group freedomjournal, and no other supplementary groups

# Step 3: Confirm no other identity is in freedomjournal
getent group freedomjournal | cut -d: -f4
# Expected: "freedomcoord,freedomsheet" and nothing else

# Step 4: Confirm freedomcoord is NOT in freedomsheet and vice versa
id freedomcoord | grep -c freedomsheet
# Expected: 0
id freedomsheet | grep -c freedomcoord
# Expected: 0
```

**Expected safe result:** Each command returns exactly the membership specified
in §2.12.2; no additional members or groups present. **Note:** this check
requires a disposable environment with the accounts already provisioned; it does
not validate existing production state and produces no expected result before
provisioning has occurred.

**Expected failure result:** An unexpected identity in `freedomjournal`, or
`freedomcoord` appearing in `freedomsheet`'s supplementary groups (or vice
versa). This would mean provisioning did not match §2.12.2 and must be corrected
before any further step.

**Cleanup:** If the disposable environment is temporary, it must be destroyed
after evidence collection. No production state is created by this check.

**Evidence captured:** Full output of each command, verbatim.

---

## Part 3a — G-EVIDENCE-1 pre-change discovery: `pg_hba.conf` / `pg_ident.conf` existing-file inspection

**Relevant surfaces:** 4 (new database principal), 6 (`pg_hba`/`pg_ident`
ordering).

**Taxonomy:** This is a **pre-provisioning discovery step**, not part of the C-4
OS identity and filesystem-access matrix. It must be performed before any Package
5.0 lines are inserted into `pg_hba.conf` or `pg_ident.conf`. Its purpose is to
confirm that pre-existing rules will not undermine the insertion ordering the
design specifies.

**Current status:** Not run. Cannot be run without Operations Owner authorization
and access to the production or staging host.

**Category:** D (or R if the target host is already accessible to the authorized
identity without elevation)

**Intended identity:** root or the postgres superuser.

**Authorization required:** Operations Owner authorization. This check does not
change any file and creates no host state.

**Commands (do not run without authorization):**
```sh
# (root or postgres superuser) — do not run without authorization
psql -U postgres -c "SHOW hba_file;"
psql -U postgres -c "SHOW ident_file;"
# Then read the files at the paths shown:
cat <hba_file_path>
cat <ident_file_path>
```

**What this step establishes (pre-provisioning discovery):** The current
`pg_hba.conf` and `pg_ident.conf` contents, before any Package 5.0 lines are
added. The purpose is to identify any pre-existing `trust`, `md5`, or wildcard
lines that would appear before the Package 5.0 `reject` lines once added. If
such a line exists, insertion ordering must account for it, or the rehearsal
must stop until the issue is resolved.

**This step does not validate post-change state.** Post-reload positive and
negative authentication tests are a separate, post-provisioning step that
cannot be performed until the Package 5.0 lines have been inserted and the
configuration reloaded.

**Discovery finding — a pre-existing broad rule found:** Not a confirmed defect;
it is a constraint on how the Package 5.0 lines must be ordered. Record it,
stop the rehearsal, and report to the Security Reviewer before proceeding.

**Discovery finding — no broad rule found:** The required Package 5.0 additions
may proceed in the order specified in §2.12.3.

**Cleanup:** None (read-only).

**Evidence captured:** Full `pg_hba.conf` and `pg_ident.conf` contents,
verbatim. SHA-256 of each file at the time of capture.

### C-4-E-1 — JNL-49 / JNL-50: Filesystem capability denial matrix (requires E authorization)

**Category:** E (evidence that cannot exist before implementation)

**Intended identities:** The eight executable identities E1 through E8 as
specified in §2.13.5c.

**Authorization required:** Approved bounded evidence-harness authorization,
plus Codex pre-execution approval of the exact commands, disposable target and
cleanup plan. Package-gate implementation authorization is neither required nor
granted for this synthetic evidence scaffolding.

**Prerequisites:**
- A fully provisioned disposable environment per §2.12.2.
- `freedomcoord`, `freedomsheet`, `freedomjournal` accounts and group in place
  and verified by C-4-D-1.
- `freedom-journal-admin` and `verify-capability` deployed.
- The journal hierarchy (`…/journal`, `…/archive`) in place with correct
  ownership and modes.
- `FS_APPEND_FL` set on the journal (C-3 confirmed it works on this filesystem).
- A-5.0-5 confirmed (the seven-step `capsh` construction and mask-versus-recipe
  comparison verified by the Security Reviewer).

**Procedure overview (do not run without E authorization):**

JNL-49 and JNL-50 test twelve cases each, every negative case with a positive
control. The cases are specified in §2.13.5c. The high-level structure is:

For each identity E1 through E8:
1. Construct the identity using `capsh` as specified in §2.13.5c step-by-step.
2. Verify the resulting capability sets (`CapPrm`, `CapEff`, `CapInh`, `CapAmb`,
   `CapBnd`, securebits) match the declared mask for that identity.
3. Attempt the specific file operation the identity is testing (e.g., E4 tests
   the owner authorization for `FS_IOC_SETFLAGS` without `CAP_LINUX_IMMUTABLE`;
   E6 tests `FS_IOC_SETFLAGS` with `CAP_LINUX_IMMUTABLE`).
4. Record the exact `errno` returned.
5. Compare against the expected value in the manipulation matrix (§2.13.4).

**Evidence format for each case:**
- Identity construction command (verbatim `capsh` invocation).
- `cat /proc/self/status` fields `CapPrm`, `CapEff`, `CapInh`, `CapAmb`,
  `CapBnd`, `Secbits`, `Uid`, `Gid`, `Groups` (from inside the constructed
  identity).
- The file operation attempted and the exact `errno` (or 0 for success).
- Pass/fail against the matrix.

**Expected safe result:** Every case produces the `errno` specified in the matrix.
E4 produces `EPERM` for `FS_IOC_SETFLAGS` without owner authorization (the
check this design depends on). E6 produces `EPERM` with `CAP_LINUX_IMMUTABLE`
but without the owner authorization — verifying the two-permission check is
actually enforced.

**Expected failure result:** Any case produces an unexpected `errno` or succeeds
when it should refuse. This would require a design revision and must be reported
to the Security Reviewer immediately.

**Cleanup:** Destroy the disposable environment. No production state is created
by these checks.

**Evidence captured:** Per case: the `capsh` invocation, `/proc/self/status`
extract, the file operation, the `errno`, pass/fail. Total: 96 case records
(12 × 8). Syscall trace (`strace -e trace=ioctl`) for the E4 and E6 cases.

---

## Part 4 — P5.0-R5: Blocking risk evidence

**Risk description:** The append-only capability of the journal has not been
confirmed by privileged evidence on this host. A-5.0-5 is unconfirmed.

**Current state:** P5.0-R5 remains Blocking. It depends on C-3 and C-4 for its
operational evidence. Until those checks run in a separately authorized
disposable environment, P5.0-R5 cannot be resolved.

### P5.0-R5 resolution path

P5.0-R5 closes when the following conditions are all met:

1. **A-5.0-4 confirmed:** a disposable OS identity can be provisioned, narrowly
   mapped through `pg_hba.conf`/`pg_ident.conf`, and exercised against the
   disposable PostgreSQL instance with every unauthorized identity refused.
   Minimum synthetic roles and objects exist only as evidence facsimiles.
   Evidence includes configuration ordering, role attributes, grants and the
   positive/negative connection matrix. **Category: E.**

   **A-5.0-3 is not part of this closure path.** It is the disposable Google
   Sheet and service-account assumption for WP-13 and remains separately
   unconfirmed unless the maintainer supplies those disposable resources.

3. **A-5.0-5 confirmed:** The `capsh` construction of identities E1–E8 is
   correct step by step; the `mask-versus-recipe` comparison holds; and the
   E4/E6 pair genuinely isolates the owner check (JNL-50 cases 4 and 6). This
   confirmation is the Security Reviewer's, not the Operations Owner's. The
   Security Reviewer must agree the seven-step derivation is correct against
   `capabilities(7)` before any privileged case is attempted.
   **Category: P (Security Reviewer authorization for the conceptual confirmation;
   E for the execution).**

4. **C-3 executed and passed:** The `FS_APPEND_FL` capability probe returned
   `EPERM` for `O_TRUNC` on an append-only file, executed as `freedomsheet`
   in a disposable environment. **Category: E.**

5. **C-4 JNL-49 and JNL-50 executed and passed:** All 96 cases produced the
   expected `errno`. **Category: E.**

6. **The Security Reviewer has reviewed all evidence** and determined that
   A-5.0-5 is confirmed and P5.0-R5 is resolved.

### Ordering constraint

Steps (1) through (5) may run only under the approved bounded evidence-harness
authorization and after Codex pre-execution review of the exact target,
commands and cleanup. They do not require and do not imply Package 5.0 product
implementation authorization. Step (6) is the Security Reviewer's
determination; it cannot be made by the executor.

---

## Part 5 — Boundary between harness evidence and product implementation

The approved exception permits minimum synthetic facsimiles for the evidence
below where the authorization names them. It does not permit migration `0014`,
production schema objects, production deployment or activation. The executor
must stop if a case cannot be demonstrated without crossing that boundary.

| Evidence | Reason not runnable |
|----------|---------------------|
| JNL-46 — manifest-function identity | Minimum test-only implementation permitted; no production deployment |
| JNL-51 — Algorithm D omission/refusal | Synthetic object-store/APR/PVR facsimiles permitted on the disposable target only |
| JNL-52 — Membership matrix | Temporary disposable identities permitted; production accounts forbidden |
| JNL-53 — Writer W11a self-check | Minimum probe implementation permitted; production writer implementation forbidden |
| `TC-5.0-JNL-49`, `TC-5.0-JNL-50` | Temporary identities and paths permitted after command-plan review |
| Database trigger, grant or constraint evidence | Minimum synthetic schema facsimile permitted; migration `0014` and production schema changes forbidden |

---

## Part 6 — Authorization checkpoints

Before any non-R evidence is collected, the following authorizations must be
obtained and documented:

| Required for | Authorization needed | Who authorizes |
|-------------|---------------------|----------------|
| Any D-category step | Approved bounded evidence-harness authorization plus a named disposable target and Codex pre-execution review | Peter Duscha has authorized the category; Codex reviews the concrete plan |
| Any P-category step | Approved bounded evidence-harness authorization plus Codex pre-execution review and evidence oversight | Peter Duscha has authorized the category; Codex reviews the concrete plan and evidence |
| Any E-category step | Approved bounded evidence-harness authorization **and Codex pre-execution approval** of exact commands, disposable target and cleanup | Peter Duscha already authorized the category; Codex supplies the required pre-execution review |
| Retention of collected evidence | Data Owner approval for any data that constitutes a record under the platform's retention policy | Peter Duscha |

---

## Part 7 — Confirmation of no evidence collected

The 2026-09-02 Codex read-only preflight is recorded in
`phase-5-0-read-only-evidence-preflight.md`. No privileged C-1, C-3 or C-4 case
has run; no evidence-harness host/database object has been created; and no
credential has been accessed.

P5.0-R5 remains Blocking. A-5.0-3, A-5.0-4 and A-5.0-5 remain unconfirmed.
C-1 remains incomplete. C-3 and C-4 have not run.

Package 5.0 remains `not ready`. Product implementation remains unauthorized;
only the bounded evidence harness is authorized.
