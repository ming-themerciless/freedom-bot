# Package 5.0 — design remediation R5 handback

> **Disposition: independently re-reviewed 2026-08-30; changes requested.
> Superseded by [`phase-5-0-remediation-r6-handback.md`](phase-5-0-remediation-r6-handback.md).**
> Revision 6 did not close P5.0-R5. The probe-report lifecycle contradicted its
> deployment-time fourth stage, F-1 overclaimed writer-only detection of every
> seal-byte alteration, and `JNL-32` contradicted the W9/W17 order. **This file
> also contained merged and truncated verification bullets and ended
> mid-sentence, which is R6-D**; the R6 handback replaces it, and the corrupt
> text is preserved here and in Git history as review evidence rather than
> repaired. This handback is retained as submission history and is **not current
> authority**.

Date: 2026-08-30 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 remediation R5 —
implementation instructions*, which **authorizes documentation and design
remediation only**. No production code, migration `0014`, database or
operating-system change, service change, Google access, deployment, cutover or
Package 5.1+ work is authorized, and none occurred.

> **Claude claims no finding closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are closed by
> the Independent Reviewer, not here.
>
> **The four R5 findings are conceded, not argued with.** Each was an error in
> this package's own mechanics rather than a limit of an external service, and
> each is replaced rather than patched. The concession is written into the
> documents themselves, at package plan **§2.13.1 rows 5–9**, *before* the
> replacements are stated — so a reader meets the defect before the fix.
>
> - **R5-A.** The revision-5 generation **could not be created.** The seal
>   contained `genesis_record_digest` while the genesis record's `prev_hash` was
>   `seal_digest`. Replaced by an acyclic construction: **package plan §2.13.5a**.
> - **R5-B.** The revision-5 permission model and the revision-5 startup contract
>   **described two different designs.** Replaced by one: **§2.13.3** and
>   **§2.13.5b**.
> - **R5-C.** The revision-5 probe's refusals were **attributable to ordinary
>   permissions**, and its startup re-probe could have **destroyed the evidence it
>   was checking**. Replaced by: **§2.13.2a**.
> - **R5-D.** `CHECK (append_only_verified)` **cannot prove a host probe ran.**
>   The claim and the column are withdrawn: **§2.13.8a**, **logical schema §3.7**
>   and **new §3.7.1**.
>
> **P5.0-R1 is unchanged and still open.** §2.10.2's conclusion stands: no
> accepted-request completion barrier exists in the published Google surface, and
> **a durable journal is not one**. Revision 6 narrows **R-5.0-8 by no cases at
> all**. **P5.0-R4 is unchanged** and **no operational evidence is claimed
> passed**. **P5.0-R2 remains closed**; **OD-55** and **OD-58** remain preserved.

---

## The revised artifacts, and the revision-5-to-revision-6 change table

| Artifact | Revision | What is new |
|---|---|---|
| [`phase-5-0-package-plan.md`](phase-5-0-package-plan.md) | **6 — remediation R5** | Header and status block; the revision-6 change table (revision 5's retained); §1.2 deliverable 13; **§2.13 rewritten** — §2.13.1 gains defects 5–9, §2.13.2 corrected, **new §2.13.2a**, §2.13.3 and §2.13.4 rewritten, §2.13.5 regrouped, **new §2.13.5a, §2.13.5b, §2.13.5c**, §2.13.6 grows to twenty-five rows, §2.13.7 extended, §2.13.8 grows to forty-one cases, **new §2.13.8a**, §2.13.9–§2.13.11 updated; §3 (WP-0, WP-2, WP-4b, WP-6, WP-8, WP-9, WP-15); §4 (PERT **37.7**, decomposed; allowance 11.0; security review 2.5–3.5; confidence driver **(j)**); §5.1 (A-5.0-5); §5.3 (**OD-62 impact**, **OD-63 unchanged**, **OD-65 extended**, **OD-66 option A re-stated**); §6.5 (items 12, 14 amended; **15 and 16 new**); §7.1 (row 19 corrected, **row 22 new**); §7.2 (precondition 1b); §7.4 (R-5.0-9, R-5.0-11, A-5.0-5, D-5.0-1, D-5.0-2, the 37.7 estimate); §8.1 (two rows corrected); §8.3 (no new number, stated); §8.4 (the fourth check's access); §9.1; §9.2 (**surface 11**, two new reviewer questions, 2.5–3.5); §9.3 (10b, 10d, 10e extended; **10f and 10g new**); §9.4; §10 (three new non-claims); §12 |
| [`phase-5-0-logical-schema.md`](phase-5-0-logical-schema.md) | **6 — remediation R5** | Status block; the revision-6 change table (revision 5's retained); §2.4 (two rows corrected for the readable seal and the derived genesis); §3.0 (the ER diagram's generation box); **§3.7 — `append_only_verified` and its `CHECK` withdrawn; `seal_body_digest`, `append_only_probe_version`, `append_only_probe_digest`, `append_only_probe_at` added; `genesis_record_digest` and `seal_digest` documented with their construction order; two constraints added, one withdrawn**; **new §3.7.1**; §4.3.2 (the proposed `freedomjournal` group); §4.3.5 (a clarifying note); §4.3.8 (Band 3 corrected and extended); §9 (four new traceability rows); §10 (OD-62, OD-63, OD-64, OD-65, OD-66) |
| This handback | **new** | the eight items |
| [`phase-5-0-remediation-r4-handback.md`](phase-5-0-remediation-r4-handback.md) | superseded | retained as review history, with its disposition banner |

**Change table — revision 5 → revision 6.** Every row is a defect the re-review
named.

| # | Change | Where | Why |
|---|---|---|---|
| 1 | The seal is **split into a body and a binding section**; the genesis record's `prev_hash` becomes **`seal_body_digest`**; `seal_digest` becomes a **leaf** that no on-disk artifact contains | plan §2.13.5a, §2.13.8; schema §3.7 | revision 5's two digests each required the other, so **no generation could be created** |
| 2 | The genesis record's whole content becomes a **pure function of the seal body**, so any reader **derives** its digest instead of trusting it | plan §2.13.5a step C3, §2.13.5b **W5**, `JNL-31` | derivation is what makes the acyclicity checkable at runtime rather than asserted in prose |
| 3 | **Algorithm C** — twelve ordered creation steps with the exact canonical bytes, the excluded fields, the actor, the artifact that already exists, and the placement of every `fsync`, `rename`, `+a` and `+i`; plus a dependency graph and a first-generation/successor table | plan §2.13.5a | the handoff requires all of it stated, per digest |
| 4 | **Algorithms V-W, V-C and V-R** — the writer's eighteen-step startup validation, the coordinator's observation, and registration — with a table of what each verifier **cannot** establish | plan §2.13.5b | unequal verifiers are only safe if the inequality is written down |
| 5 | A third system group **`freedomjournal`** holds exactly `freedomcoord` and `freedomsheet`; `…/journal` becomes `root:freedomjournal 0750` and the seal `root:freedomjournal 0440`, **readable by the writer** | plan §2.13.3, §2.13.4; schema §4.3.2 | revision 5 denied the read and required the validation. **A `0444` seal under the old `0751` directory was rejected in the same paragraph**, because it would have been readable by `discordbot` and `freedomweb` too |
| 6 | Every other local identity **loses** the traverse `0751` gave it | plan §2.13.3, §8.4 | the net change to the boundary is a tightening with one deliberate exception |
| 7 | The capability probe becomes **four stages in a disposable arena the tested identity owns**, with a **control stage** that must pass before any refusal is interpreted, or the result is `inconclusive` | plan §2.13.2a, `JNL-27` | revision 5's probe would have "passed" identically on a filesystem with no `FS_APPEND_FL` support |
| 8 | An **attribution table** separates `EACCES` (DAC), `EROFS` (read-only mount or systemd sandbox), `EPERM` with the flag present (append-only) and `ENOTTY` (no flag interface); Stage 4 separates the sandbox from the filesystem | plan §2.13.2a, `JNL-28`, `JNL-29` | *"each expected refusal must be attributable to `FS_APPEND_FL`"* |
| 9 | **Startup performs no destructive operation against live evidence.** V-W is read-only apart from one appended `startup` record | plan §2.13.5b, §2.13.8, `JNL-32`, stop condition **10f** | revision 5's re-probe would have **succeeded and corrupted the journal** in exactly the state it existed to detect |
| 10 | **Privileged cleanup specified**: refusal while the unit is active, residue reported and cleaned first, a `finally` that clears attributes and removes the arena, a non-zero exit naming any residue, and `init-generation` refusing while the arena exists | plan §2.13.2a, §2.13.7, `JNL-30` | a failed cleanup must be loud, not silent |
| 11 | **`append_only_verified` and its `CHECK` are withdrawn**, with the sentence that described them as enforcement | plan §2.13.8a; schema §3.7 | a `CHECK` on a supplied Boolean proves the value was supplied |
| 12 | Replaced by `seal_body_digest`, `append_only_probe_version` (closed vocabulary), `append_only_probe_digest` and `append_only_probe_at`, with the **probe report held inside the `+i` seal** | schema §3.7, plan §2.13.2a | an attestation **bound to a re-derivable artifact** is detectably false; a Boolean is not |
| 13 | **New §3.7.1 / §2.13.8a** — the authenticated actor, the immutable fields, the binding to generation/filesystem/probe version, and a line-by-line **enforces versus records** table | schema §3.7.1; plan §2.13.8a | *"state what PostgreSQL enforces versus merely records"* |
| 14 | **Four new fail-closed conditions**, `J-22` … `J-25`; refusal codes become `SW-J01 … SW-J25` | plan §2.13.6 | the readable seal lets the writer check the deployment digest, the host identity, the seal's own derivation and the probe report — none of which it could check before |
| 15 | **The evidence band grows from twenty-six to forty-one cases**, `JNL-27 … 41`, including the **eight independent falsification cases** of the new §2.13.5c | plan §2.13.8, §2.13.5c; §6.5 items 15–16 | every corrected claim is mapped to a named check |
| 16 | Estimate **35.5 → 37.7**; allowance 10.3 → **11.0**; security review 2.0–3.0 → **2.5–3.5**; **no new work package and no new numeric control** | plan §4, §8.3 | re-priced where revision 6 changed the work, and stated where it did not |
| 17 | **Stop conditions 10f and 10g new**, 10b, 10d and 10e extended; **security-review surface 11 new** with two questions | plan §9.3, §9.2 | standing guards against a repeat of each R5 defect |
| 18 | **OD-66 option A re-stated**; **OD-65 extended** by one system group; **OD-62 impact recorded, not decided**; **OD-63 unchanged** | plan §5.3; schema §10 | the handoff requires option and impact updates where cost, topology, authority, retention or failure behaviour changed |
| 19 | **P5.0-R1 and P5.0-R4 untouched** | plan §2.10, §2.12; schema §2.2B, §2.8, §4.3 | the handoff requires R4 kept open pending evidence and R2 kept closed |

---

## The eight required remediation items

### 1. Acyclic creation and verification algorithms — **R5-A**

**Where:** package plan **§2.13.5a** (creation), **§2.13.5b** (verification),
**§2.13.5c** (falsification); logical schema **§3.7** (the registered columns) and
**§3.0** (the ER box).

**The defect, conceded.** Revision 5 wrote that the genesis record's `prev_hash`
is `seal_digest` and that the seal carries `genesis_record_digest`. `seal_digest`
is a digest of a file containing `genesis_record_digest`, which is a digest of a
record containing `seal_digest`. **Neither can be computed first. No generation
could be created as specified.**

**The replacement, in one sentence.** The seal is split into a **body**, fixed
before the journal file exists, and a **binding section**, fixed after it exists;
the genesis record is anchored to **`seal_body_digest`**; and `seal_digest` is a
**leaf** that no on-disk artifact contains.

**Algorithm C, the creation order.** Twelve numbered steps, each naming the exact
canonical bytes hashed, the fields deliberately excluded, the artifact that
already exists, the actor, and the durability operation:

| Step | Actor | What it produces |
|---|---|---|
| C0 | root | refusals: unit inactive, arena absent, predecessor sealed and archived, `verify-capability` passed **in this invocation**, deployment digest supplied |
| C1 | root | the **probe report** `PR`, and `probe_report_digest` |
| C2 | root | the **seal body** `SB` — and it **excludes** `genesis_record_digest`, `journal_device`, `journal_inode`, `sealed_at` and `seal_digest`; that exclusion is the remediation — and `seal_body_digest` |
| C3 | root | the **derived genesis record** `G`: `prev_hash = seal_body_digest`, body a pure function of `SB`; `genesis_record_digest = G.record_hash`, **computable before the file exists** |
| C4 | root | the journal file: `O_CREAT\|O_EXCL`, `fchown`, `fchmod 0640`, write `G`, **`fsync(file)` then `fsync(dir)`** |
| C5 | root | `chattr +a`, re-read and refused if not set |
| C6 | root | `fstat` → `(journal_device, journal_inode)`; refuse unless the device equals the one the probe tested |
| C7 | root | the **binding section** `BND` — genesis digest, device, inode, `sealed_at` |
| C8 | root | the seal file as `SB ‖ BND`: written to `.tmp`, `fchown root:freedomjournal`, `fchmod 0440`, **`fsync`, atomic `rename`, `fsync(dir)`** |
| C9 | root | `chattr +i` — **after** the rename, because an immutable file cannot be renamed |
| C10 | root | the `current` symlink, replaced atomically, last |
| C11 | root | `seal_digest`, computed over the finished file's exact bytes; **nothing on disk contains it** |
| C12 | coordinator | Algorithm V-R, then one transaction: row + receipt + audit |

**The dependency graph is printed in §2.13.5a**, so acyclicity is checkable rather
than claimed: every arrow points forward in time and no value appears upstream of
itself.

**First generation versus successor** is a table in the same subsection: typed
nulls for the predecessor triple, a different C0 precondition, a different
registration index, and a different thing proved.

**Verification.** **V-W** (writer, eighteen steps, unprivileged, read-only apart
from one appended `startup` record), **V-C** (coordinator, V-W's checks plus
thirteen comparisons against the registered row plus the unresolved-set
enumeration) and **V-R** (registration, plus the predecessor's `.close` manifest
and `archive-verify`). §2.13.5b closes with a table of **what each verifier
cannot establish**.

**Disk versus PostgreSQL, without a cycle.** Registration is a **one-directional
projection**: the coordinator reads the finished artifacts, recomputes every
digest, and inserts them. **No on-disk artifact depends on any database value**,
so there is no direction in which the comparison could close a loop.

**Falsification.** §2.13.5c gives **F-1 … F-8** — the seal, the genesis record,
the registered digests, the predecessor close manifest, the inode, the deployment
digest, the host identity and the probe report — each altered **independently**,
each with the first refusal, the actor, the algorithm step, the refusal code and
the test. Two properties are the point of it: **every alteration is refused by an
actor that did not author the altered artifact**, and **F-1/F-2 are refused with
no database while F-3 is refused with no host access**, so each half fails closed
alone.

### 2. The corrected authority and permission matrix — **R5-B**

**Where:** package plan **§2.13.3** (hierarchy, and why), **§2.13.4** (the
manipulation matrix), **§2.13.5b** (who validates what), **§2.13.6** (J-01 …
J-25), **§9.2** (surface 11 and two questions); logical schema **§4.3.2** (the
group), **§4.3.5** (unchanged, and stated as unchanged), **§2.4**.

**The defect, conceded.** Revision 5 said `freedomsheet` *"cannot even read"* the
seal, and simultaneously required the writer to validate the seal, the genesis
digest, the inode, the ownership and the mode at start. **A process cannot
validate a file it cannot open.**

**The contract chosen, and why.** The handoff permits two. This design takes the
first — **grant the minimum read-only access to a non-sensitive seal** — because
the second would move the genesis, inode, ownership and mode checks out of the
writer, and those must happen **before the writer appends**, in a process with no
database and no human to wait for.

**How the grant is made minimal.** Not by making the seal world-readable. A third
system group, **`freedomjournal`**, holds exactly `freedomcoord` and
`freedomsheet`; `…/journal` becomes `root:freedomjournal 0750` and the seal
`root:freedomjournal 0440`. The obvious edit — a `0444` seal under the old `0751`
directory — is rejected in the same paragraph, because `0751` grants traverse to
*other* and the seal would have been readable by `discordbot` and `freedomweb`
too.

**The net effect is a tightening with one deliberate exception.** `freedomsheet`
gains read on one directory and one file it is required to validate; **every
identity that is neither the writer nor the coordinator loses the traverse it
had.** `/healthz`, served as `freedomweb`, now has *less* access than revision 5
gave it, and §8.4 says so.

**The writer's authority, complete.** *Read the journal and the seal; append to
the journal; nothing else.* §2.13.4's thirteen rows give the mechanism and the
`errno` for each refusal, including three new rows: **read the seal — permitted**;
**modify, truncate or replace the seal — `EPERM`**; **unlink or rename the seal —
`EACCES`**. The archive stays `root:freedomcoord 0750` with the writer as *other*
and **no access at all**. **The writer remains unable to modify, replace, rotate,
seal, archive or dispose of evidence**, and `JNL-33` proves the whole of V-W
completes using only the read it is granted.

**The disclosure, assessed rather than asserted.** The seal carries the generation
identity, the writer unit, the deployment digest, `/etc/machine-id`, the expected
uid/gid/mode, the filesystem type, the predecessor identifiers and the probe
report. **None is credential material or player data**, and the writer already
knows or can compute most of it. It is nevertheless a deliberate grant to the
identity §2.13 exists to constrain, so it is **referred to the Security Reviewer
as surface 11**, with two questions attached, rather than settled by the
implementer.

**Updated together, as the handoff requires:** the hierarchy (§2.13.3), the
manipulation matrix (§2.13.4), the systemd hardening (§2.13.3 — `ReadWritePaths=`
unchanged, and the arena deliberately outside it), **J-01 … J-25** (§2.13.6), the
startup algorithm (§2.13.5b V-W), the threat model (§2.13.3's disclosure
assessment, §7.1 row 22, §9.2 surface 11) and the tests (`JNL-33`, `JNL-13`,
`JNL-32`).

### 3. The safe append-only capability-probe procedure — **R5-C**

**Where:** package plan **§2.13.2a** in full, **§2.13.2** (where the result goes),
**§2.13.5b V-W** (the startup subset), **§2.13.7** (`verify-capability`'s
preconditions and cleanup), **§9.3 stop condition 10f**.

**The two defects, conceded.** The revision-5 probe file was `root:root 0600`
inside a directory `freedomsheet` cannot write, so **every negative case would
have failed on discretionary permissions** whether or not `FS_APPEND_FL` did
anything — the probe would have "passed" identically on a filesystem with no
append-only support. And revision 5 told the writer to **re-run the destructive
half against the live journal at every start**, which, in exactly the state the
check exists to detect, would have **succeeded** and destroyed the evidence.

**The arena.** `…/probe`, `root:freedomsheet 0770`, holding files owned
`freedomsheet:freedomsheet 0600`. **The tested identity has full ordinary file and
directory permission — that is the point.** Nothing in it is evidence; it does not
exist while the writer unit is active; `verify-capability` refuses to start while
the unit is active and `init-generation` refuses while the arena exists.

**Stage 1, the control stage.** Six operations — non-append write, `O_TRUNC`,
`ftruncate`, `rename`, `unlink`, append — must **succeed** as `freedomsheet` on a
file with the arena's ownership and **no** `+a`. **If any control case fails the
result is `inconclusive`, never `passed`**, and `verify-capability` exits non-zero
naming the case and its `errno`. This single rule is what revision 5 lacked.

**Stage 2, the capability stage.** Nine cases with their expected results:
`open(O_WRONLY)` → `EPERM`; `O_APPEND|O_TRUNC` → `EPERM`; `ftruncate` → `EPERM`;
`rename` → `EPERM`; `unlink` → `EPERM`; `O_APPEND` write → **succeeds**;
`pwrite` at offset 0 on an `O_APPEND` fd → **succeeds and lands at EOF, and is
deliberately *not* a refusal**, because POSIX requires the offset to be ignored;
`FS_IOC_SETFLAGS` clearing the flag → `EPERM` **with the flag still present on
read-back**; `FS_IOC_GETFLAGS` → reports `FS_APPEND_FL`.

**Stage 3 and Stage 4, attribution.** Stage 3 reads `/proc/mounts` and `statvfs`
and binds the report to the `st_dev` actually tested, which C6 later re-checks.
Stage 4 runs a `systemd-run` unit carrying the writer's hardening and asserts that
an append inside `ReadWritePaths=` succeeds and one outside it fails `EROFS`.

**The attribution table** states what each observation means **and what it does
not**: `EACCES` is DAC and can only mean the arena is mis-provisioned; `EROFS` is
a read-only mount or the sandbox; `EPERM` **with `FS_IOC_GETFLAGS` confirming the
flag** is append-only enforcement and is the only observation accepted as a pass;
`ENOTTY`/`EOPNOTSUPP` is a **failed** probe; a failing control case is
`inconclusive`.

**Never destructive against live evidence.** V-W performs `FS_IOC_GETFLAGS`,
`fstat`, `statvfs` and a chain read, and its **only** write is one `startup`
record — a legitimate journal record, not a probe. **`JNL-32` asserts this by
syscall trace and re-runs it with `+a` absent**, the case revision 5 would have
corrupted, and asserts the file is byte-identical afterwards except for that
record. **Stop condition 10f** makes it a stop condition rather than an intention,
and it binds health and monitoring checks too.

**Safe startup checks are separated from privileged provisioning tests.** The
destructive matrix runs **only** inside `verify-capability`, as root dropping to
the writer's uid with `setpriv`, against the disposable arena.

**Privileged cleanup, specified.** Refuse while the unit is active; report and
clean any residue from a crashed run **as an explicit first step**; run stages;
then in a `finally` on every exit path clear `FS_APPEND_FL` and `FS_IMMUTABLE_FL`
as root, unlink every artifact, `rmdir` the arena; and **exit non-zero naming the
residue if cleanup did not complete**. `init-generation` refuses while the arena
exists, so a failed cleanup cannot be walked past.

### 4. Revised registration and evidence semantics — **R5-D**

**Where:** package plan **§2.13.8a**; logical schema **§3.7** and **new §3.7.1**;
**§4.3.8 Band 3**.

**The defect, conceded.** `CHECK (append_only_verified)` constrains a supplied
Boolean to `true`. **It proves the coordinator supplied `true`.** It cannot
observe a host, cannot know whether `verify-capability` ran, and cannot
distinguish a passing probe from a typed word. Every sentence that described it as
enforcement is withdrawn, and **the column is withdrawn with the claim**.

**The authenticated actor.** `RegisterJournalGeneration`, connecting as
`freedom_migration_coordinator`, peer-authenticated as the dedicated `freedomcoord`
operating-system identity, reachable only through the `sudo` wrapper, naming a
real `platform_accounts` row resolved at execution. **No application principal
holds any privilege on the table**, and the writer the row is about holds no
database credential at all.

**The immutable evidence fields.** All of them: `UPDATE`, `DELETE` and `TRUNCATE`
revoked from every principal **and** refused by `reject_history_mutation`,
including for the schema owner; supersession is the successor's own row. Outside
the database: the `chattr +i` seal, the `chattr +i` archive, an
`idempotency_keys` receipt and an `audit_events` row in the same transaction, and
`sudo log_output` plus journald.

**The binding to the exact generation, filesystem and probe version.** The probe
report names its procedure version, the filesystem type and the `st_dev` tested;
step C6 refuses unless the created journal is on that same device; the report then
lives **inside that generation's seal body**, covered by `seal_body_digest`,
anchored by the genesis record and sealed under `+i`. Three independent readers
recompute its digest: the writer at **W4**, the coordinator at **C-d**, and
`archive-verify` at every restore.

**What PostgreSQL enforces versus records** is a table in both artifacts. In
brief: it **enforces** digest shape, closed vocabularies, `append_only_probe_at <=
created_at`, chain linearity, one registration per inode, append-only history, the
identity of the inserting principal, and the activation trigger's fifth condition.
It **records** — and cannot verify — that the values still describe the files on
disk, that the predecessor was genuinely sealed, and **whether the probe ran at
all**.

**Why this is stronger, and why it is still not a proof.** Stronger: a false
attestation is now **detectable**, because the report is inside the `+i` seal and
every reader recomputes its digest — `JNL-41` asserts that a row **can** be
inserted with a well-formed but false digest and that the writer and the
coordinator both then refuse it. Not a proof: **no database constraint can observe
a host**, and neither document now says one does. What establishes that the probe
ran is the seal, `sudo log_output`, journald, `audit_events` and `archive-verify`
— four records, three of them outside PostgreSQL.

**The writer keeps no PostgreSQL dependency.** It validates the probe report from
the seal it can read; the database comparison is the coordinator's alone.

### 5. Updated failure-state and falsification matrices

**Failure states — §2.13.6, now twenty-five rows.** Four are new, and each exists
because R5-B gave the writer a check it could not previously perform:

| Row | Condition | Detected at |
|---|---|---|
| **J-22** | the running writer's deployment digest ≠ the seal's | V-W **W11**; coordinator **C-d** |
| **J-23** | `/etc/machine-id` ≠ the seal's | V-W **W10**; coordinator **C-d** |
| **J-24** | the seal's structure fails, or the **derived** genesis digest ≠ the binding section's | V-W **W3**, **W5** |
| **J-25** | the probe report is absent, altered, unsupported, or not a pass | V-W **W4**; coordinator **C-d** |

Refusal codes become `SW-J01 … SW-J25`. **No row resolves to "continue."** Rows
J-03, J-04, J-06, J-11, J-12, J-13, J-17 and J-20 gain the algorithm step that
detects them, so a reader can trace each to executable behaviour.

**Falsification — §2.13.5c, eight independent cases**, mapped to `JNL-34 … 41`;
plus §2.13.8's **`TC-5.0-JNL-01 … 41`** band, fifteen cases larger than revision
5's; plus §6.5's new items **15** and **16**; plus §7.1's new row **22**, which
names the failure mode this whole remediation is about — *the journal's own
integrity machinery is wrong* — and answers it with tests rather than arguments.

**Every corrected claim is mapped to a named check.**

| Corrected claim | Check |
|---|---|
| the construction is acyclic and byte-exact | `JNL-31` — an **independent implementation** re-derives the genesis record from the seal body alone, and the body is asserted to exclude the four downstream values |
| the writer can perform every check it is required to perform | `JNL-33` — the whole of V-W completes using only the granted read |
| the writer still cannot alter or replace evidence | `JNL-13` (thirteen rows), `JNL-33` |
| the probe's refusals are attributable to `FS_APPEND_FL` | `JNL-27` (control stage), `JNL-28` (attribution), `JNL-29` (sandbox) |
| startup destroys nothing | `JNL-32`, **including a run with `+a` absent** |
| the probe cleans up | `JNL-30` |
| the database records rather than proves | `JNL-41`, plus the §3.7.1 division asserted case by case, plus an assertion that migration `0014` contains **no** `append_only_verified` |
| the eight falsification cases refuse at the right boundary | `JNL-34 … 41` |

**Checks not run, and marked as such rather than omitted.**

| Check | Why not | Who must complete it |
|---|---|---|
| **Whether `chattr +a` actually works on the journal filesystem** | needs `CAP_LINUX_IMMUTABLE`; the reading account is `uid=1000(foundry)`, and setting it would be an environment change this remediation is not authorized to make. **A-5.0-5** | Operations Owner, at WP-15, through `verify-capability` |
| **The whole `TC-5.0-JNL` band, all forty-one cases** | no code exists; package 5.0 is design-only and implementation is unauthorized | implementer at WP-8/WP-15, after the gate |
| A supervised host reboot between a dispatch and its outcome (`JNL-02b`) | a reboot is an operational action, not a test | Operations Owner, in the WP-9 rehearsal — **or recorded as not run** |
| An injected `fsync` failure (`JNL-17`) | needs a loopback device with `dm-error` or a syscall interposer, both host changes | Operations Owner / implementer at WP-8, under A-5.0-5 |
| Whether `setpriv` is present on this host | **not checked**; §2.13.2a assumes it for the privilege drop, and §8.1 now records the check as not run | Operations Owner |
| Enumerate `/etc/sudoers.d/` | permission denied without privilege | Security Reviewer |
| Host-wide setuid audit | not performed; a partial listing is not an audit and is not offered as one | Security Reviewer |
| PostgreSQL `log_connections`; the live `pg_hba.conf` / `pg_ident.conf` | not readable without privilege | Operations Owner |
| Confirm A-5.0-3, A-5.0-4 and **A-5.0-5** | host or account provisioning decisions | Delivery Lead / Operations Owner |
| **Every security check** — surfaces 1–11 and the six reviewer questions | the Security Reviewer is **unnamed** (OD-61) | Acceptance Authority, then the named reviewer |

### 6. Estimate, RAID, decision, status and change-control impacts

**Estimates.** PERT **37.7** implementer-days, up from 35.5, decomposed line by
line in §4: WP-15 +0.7, WP-4b +0.4, WP-8 +0.5, WP-6 +0.3, WP-2 +0.2, WP-9 +0.1.
**No work package is added.** Remediation allowance **11.0** (30 % of ML 36.5);
contingency **4.0**, unchanged; security review **2.5–3.5** reviewer-days, up from
2.0–3.0; independent implementation review 2.5–3.0, unchanged; supervised
rehearsal 1.5–2.0 days of Operations Owner time, unchanged in duration and larger
in content.

**Risks.** **R-5.0-11 extended** — four more fail-closed conditions, and **J-22 is
the one an operator will meet in normal work**, because an ordinary writer
redeployment now requires a rotation and a re-registration before Sheet mutations
resume. **R-5.0-9 extended** — host-boundary drift now includes the
`freedomjournal` group's membership and any residue of the probe arena.
**R-5.0-8 unchanged and not narrowed by one case.** R-5.0-10, R-5.0-3, R-5.0-5 and
R-5.0-7 unchanged. **No risk is closed.**

**Assumptions.** **A-5.0-5 restated**: it now names the writer-owned probe arena
and `setpriv` execution under the writer's uid, and — the correction — states that
without it `verify-capability` produces no passing report and **`init-generation`
refuses to create a generation at all**, a host-side refusal rather than a database
constraint. A-5.0-3 and A-5.0-4 unchanged and unconfirmed.

**Decisions.** **OD-66 option A is re-stated**, because its construction,
permission model, probe and registration semantics all changed; its options,
owners and retention rule are unchanged. **OD-65 extended** by the `freedomjournal`
group. **OD-62's impacts recorded, not decided**: G-A's enumeration control was
found not implementable and is replaced, so the R4 precondition — that the
Independent Reviewer accept the control as fail-closed — **still stands and is
still unmet**; and G-A's availability cost widens under R-5.0-11. **OD-63
unchanged**: revision 6 adds no numeric control and changes no value. **OD-64
unchanged.** **OD-61 unchanged**: the Security Reviewer is unnamed.

**Status, RAID, decision and change control — all five registers are updated in
this submission.** `docs/project-management/status.md` gains the
one-hundred-thirtieth update and demotes the previous blocks to superseded
updates 129 and 128; `raid-register.md` updates its header and P5.0-R5's state,
R-5.0-9, R-5.0-11, A-5.0-5, D-5.0-1 and D-5.0-2; `decision-register.md` updates
its header, the readiness summary, and D5.0-9, D5.0-10, D5.0-12 and D5.0-13;
`docs/discovery/open-decisions.md` gains a *Remediation R5 submitted* block and
updates OD-62 (impacts and G-A's cost line), OD-65 (a fourth item) and OD-66
(option A re-stated), together with the Package 5.0 row of the OD-01–OD-66
summary; and `change-log.md` gains **C-P5.0-K**. **Nothing is approved by these
entries**; they record a submission.

### 7. Exact commands run, and their results

Read-only, on 2026-08-29 and 2026-08-30, as `uid=1000(foundry)`.

| Command | Result |
|---|---|
| `cat docs/review/Handover\ information` | the R5 remediation brief, read in full |
| `cat CLAUDE.md`, `cat .agents/AGENTS.md` | read in full, as both require |
| `wc -l` over the plan, the schema, the R4 handback and the five registers | 603 / 2522 / 2509 / 1694 / 557 and the register sizes; used to plan the reading. No file was truncated or generated |
| `grep -n` and `sed -n` over both design artifacts and the five registers | located every section, every stale reference to `append_only_verified`, `twenty-one`, `0444`, `twenty-six-case` and `35.5`, and every cross-reference that had to move |
| `git status --porcelain` | the changed files are the two design artifacts, this handback, and the status, RAID, decision, open-decisions and change-log registers, alongside the pre-existing unrelated working-tree changes this remediation did not touch and did not modify |
| **`git diff --check`** | **clean — no output, exit 0.** Run against the working tree being submitted |
| Markdown inspection of every edited file | every table's column count re-checked against its header; every spliced boundary re-read; no truncated sentence, no duplicated fragment, no missing word found. The `---` rule preceding §3 was re-spaced after the §2.13 splice, and that is the only formatting repair made |

**No host command was run for this remediation.** Every §8.1 observation is
carried forward from revision 5's reading of the host on 2026-08-29, and each
still says how it was observed. **No new host fact is asserted.**

**No test suite was run, because no code exists for this package.** No figure from
any suite is cited for package 5.0, and **no executable control is claimed to have
passed**. Formatter, linter and type checker: **none is configured** in this
repository, recorded as *not configured* and never as *passed*.

### 8. Explicit statement that no implementation or environment mutation occurred

**No implementation or environment change occurred in producing this
remediation.**

- No production code was written or modified.
- No migration was written; migration `0014` does not exist and the head remains
  `0013`.
- No table, column, index, trigger, sequence, grant, database role, `pg_hba.conf`,
  `pg_ident.conf` or `postgresql.conf` entry was created or altered, in any
  database. No configuration was reloaded. **`append_only_verified` is withdrawn
  from a proposal, not dropped from a table: no such column has ever existed.**
- No operating-system account, **group**, `sudoers` file or deployment path was
  created or altered. `freedomcoord`, `freedomsheet`, **`freedomjournal`**,
  `/opt/freedom-blades/coordinator` and `freedom-journal-admin` are proposals in a
  document; none exists on this host.
- **No directory, file, file mode or filesystem attribute was created or
  altered.** `/var/lib/freedom-sheet-writer` **does not exist on this host and was
  not created**; no `…/probe` arena was created; **no `chattr` was run**; no
  `setpriv` was run; no probe of any kind was executed.
- No configuration file, environment variable, `.env`, systemd unit or deployment
  artifact was created or altered. `freedom-sheet-writer` is a proposal, not a
  unit on this host.
- No credential was read, written, created, rotated, revoked or distributed.
- **No Google access was changed.** No Drive permission, spreadsheet ACL or
  service-account key was read, modified or exercised. **No Google API was
  called.**
- No service was deployed, started, stopped or restarted.
- No data was mutated, in any database.
- No authority cutover occurred; every migration unit remains `Legacy` in the
  controlled register, and no control plane exists to record otherwise.
- No Package 5.1+ work was begun.
- **Unrelated working-tree changes were preserved.** The pre-existing modified and
  untracked files listed by `git status` at the start of this remediation were not
  read for content, edited, staged, reverted or committed.

**The host was neither read nor written for this remediation.** The changed files
are `docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md`, this handback, and the status, RAID,
decision-register, open-decisions and change-log documents.

---

## Traceability from the findings to the revised design

| R5 finding | Conceded at | Replaced by | Evidence |
|---|---|---|---|
| **R5-A** circular construction | plan §2.13.1 row 5 | §2.13.5a Algorithm C, §2.13.5b V-W/V-C/V-R, §2.13.5c F-1 … F-8; schema §3.7 columns | `JNL-31`, `JNL-34 … 41` |
| **R5-B** permission versus duty | plan §2.13.1 row 6 | §2.13.3 (`freedomjournal`, `0750`, `0440`), §2.13.4 (three rows changed), §2.13.5b (the split), §2.13.6 (J-22 … J-25); schema §4.3.2 | `JNL-33`, `JNL-13` |
| **R5-C** invalid and unsafe probe | plan §2.13.1 rows 7–8 | §2.13.2a (four stages, control stage, attribution, cleanup), §2.13.5b V-W (non-destructive), §2.13.7, stop condition 10f | `JNL-27 … 30`, `JNL-32` |
| **R5-D** the database claim | plan §2.13.1 row 9 | §2.13.8a; schema §3.7 (column withdrawn, four added) and §3.7.1 | `JNL-41`, plus an assertion that the withdrawn `CHECK` is absent from `0014` |
| **Corrupted handoff / `git diff --check`** | — | every edited file re-read; boundaries re-checked | **`git diff --check` clean, exit 0** |

## What P5.0-R1, P5.0-R2, P5.0-R4, OD-55 and OD-58 look like after this remediation

- **P5.0-R1 — open, unchanged, and not claimed closed.** §2.10.1's thirteen-candidate
  search and §2.10.2's conclusion are untouched. §2.13.10 is unchanged and still
  says a durable journal is not a fourteenth candidate. **Revision 6 narrows
  R-5.0-8 by no cases**, and stop condition 10b now additionally forbids
  describing the **acyclic construction** as a barrier.
- **P5.0-R2 — closed, and preserved.** §2.1's authority-state matrix and §2.5's
  effective-time model are untouched. Revision 6 changes no state, no transition,
  no epoch rule and no activation instant.
- **P5.0-R4 — open, unchanged, and **no operational evidence is claimed
  passed**.** §2.12's host boundary, §4.3's principals, layers, grants and denial
  matrix stand exactly as revision 4 left them. The one addition is the
  `freedomjournal` **filesystem** group, which carries **no database privilege**
  and changes no cell of §4.3.5.
- **OD-55 — preserved.** No comparison-telemetry table, column, write path or
  schema in this package.
- **OD-58 — preserved.** No ledger table; R-P4-4 stays open and owned by 5.2.

## What is requested next

1. **Codex independent re-review** of both design artifacts. The most useful
   disagreements would be: **a step in Algorithm C whose inputs do not yet exist**
   (§2.13.5a); **a check in V-W the writer still cannot perform with the access it
   is granted** (§2.13.5b, §2.13.3); **a probe case whose `errno` is attributable
   to something other than `FS_APPEND_FL`** (§2.13.2a); **a claim anywhere that
   still credits PostgreSQL with observing a host** (§2.13.8a, schema §3.7.1); or
   **a journal condition §2.13.6's twenty-five rows do not list.**
2. **Peter's rulings** on **D5.0-13 / OD-66** — whose **option A is re-stated**,
   so it must be re-read rather than carried forward — **D5.0-12 / OD-65**, now
   including a third system group, **D5.0-9 / OD-62**, which the R4 handoff says
   must wait until the Independent Reviewer accepts that the enumeration control
   is fail-closed and which **revision 6 has just rebuilt**, **D5.0-10 / OD-63**
   and **D5.0-11 / OD-64**.
3. **A named Security Reviewer.** The scope grew again: **surface 11** — a seal the
   writer may read and a transient arena the writer's identity may write — on top
   of everything R3 and R4 named. **Two of the six questions in §9.2 are new and
   are theirs**, not the implementer's.
4. **Confirmation of A-5.0-3, A-5.0-4 and A-5.0-5.** Without A-5.0-4 the R3-B
   evidence is unproducible; **without A-5.0-5 no capability probe can run, so no
   generation can be created at all and the whole forty-one-case `TC-5.0-JNL` band
   is unproducible**, and P5.0-R5 cannot close on evidence.

**Implementation remains unauthorized.** Package 5.0 remains `not ready`. No work
package starts while any Blocking finding, D5.0-9, D5.0-10, D5.0-11, D5.0-12,
D5.0-13 or the Security Reviewer assignment remains open.
