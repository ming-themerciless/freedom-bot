# Package 5.0 — design remediation R4 handback

> **Independent re-review disposition, 2026-08-29: changes requested.** This
> handback is retained as revision-5 history, but P5.0-R5 remains Blocking. The
> design has a circular seal/genesis hash dependency, gives the writer no read
> access to the seal it must validate, uses ordinary permissions that invalidate
> the append-only capability probe, risks destructive probing of live evidence,
> and overstates what `CHECK (append_only_verified)` proves. Remediation R5 is
> governed by [`Handover information`](Handover%20information). Package 5.0
> remains not ready and implementation remains unauthorized.

Date: 2026-08-29 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 — design
remediation R4 handoff*, which **authorizes documentation and design remediation
only**.

> **Claude claims no finding closed.** P5.0-R1, P5.0-R4 and P5.0-R5 are closed by
> the Independent Reviewer, not here.
>
> **The three findings are in three different states, and the difference is the
> point of this handback.**
>
> - **P5.0-R5** is the one a design pass could actually answer, because it was a
>   defect in this package's own design rather than a limit of an external
>   service. The journal's storage, identity, integrity format, failure states and
>   privileged lifecycle are **replaced, not patched** — package plan **§2.13** —
>   and the contradiction about completeness is resolved by **withdrawing the
>   false statement and keeping the control**.
> - **P5.0-R4** is unchanged from revision 4 apart from two added denial rows for
>   the second `sudoers` drop-in. **No operational evidence is claimed to have
>   passed.** OD-64, OD-65, the Security Reviewer and the two privileged checks
>   remain open, exactly as the handoff requires.
> - **P5.0-R1** is unchanged and still open. §2.10.2's conclusion stands: no
>   accepted-request completion barrier exists in the published Google surface.
>   **Making the journal durable does not create one**, and package plan §2.13.10
>   exists specifically so no later reader can mistake it for one.

---

## The revised artifacts, and the revision-4-to-revision-5 change table

| Artifact | Revision | What is new |
|---|---|---|
| [`phase-5-0-package-plan.md`](phase-5-0-package-plan.md) | **5 — remediation R4** | **New §2.13** in eleven subsections; §1.1, §1.2 (deliverable 13 new, 2, 3 and 5 amended), §2.8, §2.9, §2.10.3 (W-2, W-3 rewritten), §2.12.5 (the `/run` row withdrawn, three rows added), §3 (**WP-15 new**; WP-2, WP-3, WP-4b, WP-6, WP-7, WP-8, WP-9, WP-14 grow), §4 (PERT 35.5, decomposed), §5.1 (**A-5.0-5**), §5.3 (**D5.0-13 new**, D5.0-10 extended to nine), §6.1 (deliverable 13), §6.3, §6.5 (items 12–14), §7.1 (rows 19–21), §7.2 (precondition 1b, step 5, a new *unknown journal* branch), §7.4 (**R-5.0-10**, **R-5.0-11**, **A-5.0-5**; R-5.0-9 extended), §8.1 (**H-4**, **H-5**, the withdrawn filesystem row, four checks not run), §8.3 (N5.0-21 … N5.0-23), §8.4 (a fourth check), §9.1, §9.2 (surfaces 9–10, four reviewer questions), §9.3 (stop conditions 10b, 10c, 10d, 10e, 13), §9.4, §10, §12 |
| [`phase-5-0-logical-schema.md`](phase-5-0-logical-schema.md) | **5 — remediation R4** | Status block; the revision-5 change table; §0.2 (two consumers added), §0.3 (the fifth command), §1 (four conventions), §2.2B items 2–3, §2.3 (protocol steps 6 and the activation test), §2.4 (the fifth evidence kind rewritten, a third residual), §2.8 (two rows), **new §2.9**, §3.0 (the ER diagram), §3.4 (**trigger condition 5**), §3.5 (**three columns, two constraints**), §3.6, **new §3.7**, §4 (a table row), §4.1, §4.2, §4.3.1, §4.3.4, §4.3.5, §4.3.8 (**Band 3**, two Band-2 rows), §5, §6, §7 (three rows added, one rewritten), §8, §9 (six rows), §10 (**D5.0-13**) |
| This handback | **new** | the eight items |

**Change table — revision 4 → revision 5.**

| # | Change | Where | Why |
|---|---|---|---|
| 1 | The journal moves from `/run` to **`/var/lib/freedom-sheet-writer/journal/`**, on a filesystem **read** rather than inferred | plan §2.13.2, §8.1 H-4/H-5 | `/run` is `tmpfs` on this host and is emptied at every boot |
| 2 | The **directory** becomes the primary protection: root-owned, not writable by the writer, so it cannot unlink, rename, link, create or replace | plan §2.13.3, §2.13.4 | revision 4 relied on a file attribute alone — **and assumed it** |
| 3 | `chattr +a` becomes a **second, independent** layer and is **probed** at provisioning and at every writer start | plan §2.13.2 | a filesystem type is not a runtime capability test |
| 4 | systemd `StateDirectory=` is **explicitly rejected**, with the reason | plan §2.13.2 S-3 | it would create the directory **owned by the writer** |
| 5 | A **sealed, registered generation** — `chattr +i` seal, genesis record, and a row in a new sixth table that must all agree | plan §2.13.5, schema §3.7 | so a new or reset journal is never a valid empty history, and so the trigger can refuse stale evidence |
| 6 | A **hash-chained, sequence-numbered** record format, with a torn tail counted as one unresolved entry of unknown identity | plan §2.13.8 | truncation, reordering, splicing and rewriting must be detectable |
| 7 | A **twenty-one-condition** fail-closed state table, covering all fifteen the handoff names plus six more | plan §2.13.6 | **no row resolves to "continue"** |
| 8 | A **privileged lifecycle** — `freedom-journal-admin`, root, its own `sudoers` drop-in — for seal, rotate, repair, archive-verify and a gated `dispose` | plan §2.13.7 | the writer must not be able to erase evidence it authored, and clearing must not be an ambient capability |
| 9 | Revision 4's *"nothing in the fence depends on the journal being complete"* is **withdrawn as false**; the method is kept | plan §2.13.9, schema §2.9, §2.4 | it contradicted `dispatch_journal_clear` being required |
| 10 | **A sixth table, three evidence columns, a fifth trigger condition, a fifth command, scope and audit action** are added | schema §3.7, §3.5, §3.4, §0.3, §3.6 | a trigger cannot refuse what the database has never heard of. **Revision 4's "no table is added" claim is superseded** |
| 11 | The writer is **removed from the runtime database role**; it holds no credential and opens no connection | schema §4.3.1, §4.3.5 | a tightening, stated rather than made silently — and it is what keeps the legacy mutation path free of a PostgreSQL dependency |
| 12 | **N5.0-21, N5.0-22, N5.0-23** added; D5.0-10 grows six → nine, with N5.0-23 owned by the **Data Owner** | plan §8.3, §5.3 | the storage lifecycle had no numbers at all |
| 13 | **R-5.0-10** and **R-5.0-11** raised; **A-5.0-5** raised; **D5.0-13 / OD-66** raised; R-5.0-3 and R-5.0-9 extended | plan §7.4, §5.3 | the limit of completeness, the cost of fail-closed, and the host change are decisions and risks, not design details |
| 14 | **WP-15** added; WP-2, WP-3, WP-4b, WP-6, WP-7, WP-8, WP-9, WP-14 grow. Estimate **29.2 → 35.5** | plan §3, §4 | decomposed line by line in §4 |
| 15 | Stop conditions **10d** and **10e** added, **10b** extended, **13** added | plan §9.3 | standing guards against a repeat of P5.0-R5 |
| 16 | **P5.0-R1 is untouched**, and §2.13.10 is added to say a durable journal is not a barrier | plan §2.13.10 | the failure mode this section most needed to prevent |

---

## The eight required remediation items

### 1. A durable filesystem, not `/run`

**Read from this host on 2026-08-29, rather than inferred** — which is the
methodological half of the finding:

| Fact | How it was read | Result |
|---|---|---|
| `/run`'s filesystem | `/proc/mounts`, `df -T /run` | `tmpfs /run tmpfs rw,nosuid,nodev,noexec,relatime,size=806112k,mode=755,inode64` — **volatile, emptied at every boot** |
| `/run`'s attribute support | `lsattr -d /run` | prints an **empty** attribute field, where ext4 paths print `--------------e-------` |
| The proposed journal filesystem | `df -T`, `/proc/mounts` | `/`, `/var`, `/var/lib` and `/opt/freedom-blades` are **one ext4 filesystem on `/dev/vda1`**, `rw,relatime,discard,errors=remount-ro`, 135 GiB free |
| `/var/lib` | `ls -ld` | `drwxr-xr-x root:root`; `/var/lib/freedom-sheet-writer` **does not exist** |
| Tooling | `command -v` | `chattr`, `lsattr` at `/usr/bin/`; `tune2fs`, `dumpe2fs` at `/usr/sbin/` |
| systemd | `systemctl --version` | **255** — `StateDirectory=`, `ReadWritePaths=`, `ProtectSystem=strict`, `CapabilityBoundingSet=` all available |

**The journal moves to `/var/lib/freedom-sheet-writer/journal/`.** Package plan
§2.13.2 compares six candidates and rejects five with reasons, including two that
matter:

- **systemd `StateDirectory=` is rejected**, because it creates the directory
  **owned by the unit's `User=`**. The convenient mechanism is precisely the one
  that would let the writer unlink and replace its own evidence. The directory is
  created by root at provisioning and merely *made writable through*
  `ReadWritePaths=`.
- **A PostgreSQL table is rejected**, unchanged from revision 4 and for the same
  reason: a database write before every Sheet write would give the Freedom bot's
  legacy mutation path a standing PostgreSQL availability dependency, which
  withdrawing the lease removed. **The writer opens no database connection at
  all.**

**The append-only capability is probed, never inferred.**
`freedom-journal-admin verify-capability` asserts, at provisioning, that a
non-append write, `O_TRUNC`, `ftruncate`, `unlink` **by `freedomsheet`** and
`chattr -a` **by `freedomsheet`** each fail with the expected `errno`; the writer
re-runs the unprivileged half at every start; and **a generation whose probe did
not pass cannot be registered**, because the column is `CHECK
(append_only_verified)`.

**Whether `chattr +a` works on this host is a check that was NOT run** — setting
the attribute needs `CAP_LINUX_IMMUTABLE`, which the reading account does not
hold, and running it would have been an environment change this remediation is not
authorized to make. It is **assumption A-5.0-5**, and the degraded path if it
turns out unavailable is stated in §2.13.2 rather than left to be discovered.

### 2. Owner, group, mode, filesystem, authorities — and protection beyond writes to an open file

Package plan **§2.13.3** gives the hierarchy: every path with its owner, group,
mode, filesystem, creation authority, writer capability, reader capability and
privileged maintenance authority. **§2.13.4** gives the manipulation matrix.

**The load-bearing property is a permission fact, not an attribute.**

> `…/journal` is `root:freedomcoord 0751`. `freedomsheet` is *other*, so it has
> `--x`: **traverse only**. Every one of `unlink(2)`, `rename(2)`, `link(2)`,
> `creat(2)` and `open(O_CREAT)` requires write permission **on the directory**,
> which it does not have. `chattr +a` on the file is a **second, independent**
> layer over that, not the only one — which is the structural answer to revision
> 4, where the attribute was the whole of the protection *and* was assumed.

| Attempt as `freedomsheet` | First refusal | Second, independent refusal | Expected |
|---|---|---|---|
| `unlink` the journal | no write permission on `…/journal` | `chattr +a` | `EACCES` |
| `rename` the journal | as above | as above | `EACCES` |
| create a replacement and `rename` over it | as above | the coordinator's `(st_dev, st_ino)` check | `EACCES` |
| `open` without `O_APPEND`, `pwrite` at 0 | `chattr +a` | the hash chain detects it afterwards | `EPERM` |
| `O_TRUNC` / `ftruncate` | `chattr +a` | chain and sequence check | `EPERM` |
| `chattr -a` | `CAP_LINUX_IMMUTABLE` absent from the bounding set | `NoNewPrivileges=true` | `EPERM` |
| `rename`/`rmdir` the parent | `/var/lib/freedom-sheet-writer` is `root:root` | `/var/lib` is `root:root 0755` | `EACCES` |
| read or alter the seal | mode `0440 root:freedomcoord` | `chattr +i` | `EACCES` |
| touch anything in `…/archive` | mode `0750 root:freedomcoord`, no traverse for *other* | `chattr +i` per file | `EACCES` |
| repoint `…/journal/current` | root-owned symlink in a directory it cannot write | the writer re-verifies `(st_dev, st_ino)` | `EACCES` |

The unit is hardened to match: `NoNewPrivileges=true`, an **empty**
`CapabilityBoundingSet=` (so `CAP_LINUX_IMMUTABLE` is unreachable even at uid 0),
`ProtectSystem=strict`, `ReadOnlyPaths=/var/lib/freedom-sheet-writer` with
`ReadWritePaths=` narrowed to the journal directory — which **grants nothing the
directory mode does not already grant** and exists only so that a refusal is
always the journal's and never systemd's.

### 3. A durable generation bound to the writer deployment and the cutover observation

Package plan **§2.13.5** and logical schema **§3.7**.

A **generation** is the durable identity of one journal file, carrying its
`generation_id`, a strictly increasing `generation_seq`, the writer unit, the
**deployed writer's digest**, the host machine id, the journal's `(device,
inode)`, the genesis record's digest, the seal's digest, the filesystem type and
the capability-probe result. It lives in **three places that must agree**: the
`chattr +i` seal file, the genesis record inside the journal, and the registered
row in PostgreSQL.

**Why a new or reset journal can never be mistaken for a valid empty history —
three independent reasons:**

1. **A valid journal is never empty.** Record 0 is a `genesis` record whose digest
   is inside the immutable seal. A zero-length file, or one whose first record is
   not the record the seal names, is **invalid**, and invalid is a refusal.
2. **The generation must be registered, current and unsuperseded.** The activation
   trigger's **new condition 5** refuses evidence whose generation is not the head
   of the registered chain, and refuses evidence observed **before** a later
   generation was registered.
3. **Creating a generation requires sealing the one before it.**
   `predecessor_close_digest` is `NOT NULL` whenever a predecessor exists, and a
   `.close` manifest exists only after `seal`. **"Reset the journal so it looks
   empty" therefore requires first sealing and archiving the history it was meant
   to erase**, as root, audited, into an immutable file the writer cannot read.

**The binding to the cutover observation** is the three new evidence columns —
`journal_generation_id`, `journal_last_sequence`, `journal_head_digest` —
biconditionally `CHECK`ed against `fence_method = 'dispatch_journal_clear'`, so a
journal observation without a journal identity cannot be recorded at all.

**The writer still never touches PostgreSQL.** Registration is a human act at
provisioning and rotation, through the coordinator. No Sheet write and no
Freedom-bot command causes it.

### 4. Startup and recovery behaviour for every named condition

Package plan **§2.13.6** — twenty-one rows, two actors, two different refusals,
and **no row resolves to "continue"**.

| Handoff condition | Row | Writer | Coordinator |
|---|---|---|---|
| reboot | **J-01** | validates and continues appending | **a pre-reboot unresolved entry is still unresolved** — the property `/run` destroyed |
| unclean shutdown | **J-02** | refuse; generation `suspect` | the torn tail is **one unresolved dispatch of unknown identity**; refuse |
| missing file | **J-03** | refuse; **it cannot create one** | refuse. *Missing* is not *empty* |
| empty new file | **J-04** | refuse | refuse — **this is the P5.0-R5 case** |
| wrong owner/mode | **J-05** | refuse | refuse |
| unsupported filesystem flags | **J-06** | refuse | refuse |
| malformed/truncated record | **J-02**, **J-07** | refuse | refuse |
| sequence gap | **J-08** | refuse | refuse |
| checksum failure | **J-09** | refuse | refuse |
| duplicate sequence | **J-10** | refuse | refuse |
| replaced inode | **J-11** | refuse | refuse |
| unreadable file | **J-12** | refuse | refuse — ***unreadable* is never *clear*** |
| full filesystem | **J-13** | **refuse before dispatch** (N5.0-21) | refuse |
| failed `fsync` | **J-14** | refuse; generation `suspect`; exit non-zero | refuse |
| failed outcome append | **J-15** | request stays **unresolved**; refuse further dispatch | refuse |
| *(added)* unregistered/superseded generation | **J-16** | — | refuse |
| *(added)* seal missing, mutable or failing its digest | **J-17** | refuse | refuse |
| *(added)* a record from another generation | **J-18** | refuse | refuse |
| *(added)* a dispatch after a `seal` record | **J-19** | refuse | refuse |
| *(added)* non-empty unresolved set | **J-20** | — | refuse (N5.0-20 = zero) |
| *(added)* non-monotonic timestamp | **J-21** | refuse | refuse |

Every writer refusal is **typed and named** — codes `SW-J01 … SW-J21`, on the
existing `S-01 … S-15` precedent — and is **not a crash**: the Freedom bot stays
online, reads and every non-mutating command are unaffected, and the affected
mutation is refused with a message carrying no exception text, path or `errno`.
The availability cost of that is named as **R-5.0-11** rather than left implicit.

### 5. Privileged sealing, rotation, archival, retention, clearing and disposal

Package plan **§2.13.7**. `freedom-journal-admin` is a second root-owned wrapper
under **its own `sudoers` drop-in**, deliberately separate from the coordinator's
so the two authorities are revoked independently. It runs **as root**, because
setting and clearing `+a`/`+i` needs `CAP_LINUX_IMMUTABLE`; `NOPASSWD` is absent;
`env_reset`, `!setenv`, `secure_path` and `log_output` apply.

| Event | Preconditions, all refusing |
|---|---|
| `verify-capability` | the directory exists with the expected owner and mode |
| `init-generation` | writer **inactive**; predecessor **sealed and archived**; probe passed in this invocation; deployment digest supplied |
| `seal` | writer **inactive**; chain validates. Appends a `seal` record, clears `+a`, moves to `…/archive` as `root:freedomcoord 0440` `+i`, writes a `.close` manifest naming the final digest, the record count and **the unresolved set at seal time** |
| `rotate` | `seal` then `init-generation`; refuses while the writer is active |
| `repair` | only for a `suspect` generation; it **seals**, it never edits, and the torn tail is preserved verbatim |
| `archive-verify` | re-reads an archive and re-validates its chain against its `.close` manifest |
| `dispose` | **N5.0-23 elapsed, plan §15.1's gate closed, a Data Owner approval reference supplied, and `archive-verify` passed.** It is the only path that destroys evidence |

**The writer cannot erase or replace evidence it authored** — §2.13.4's ten rows,
each with an expected `errno`, tested under the `freedomsheet` uid.

**Clearing does not require an undocumented ambient capability.** Revision 4's
sentence *"clearing it needs `CAP_LINUX_IMMUTABLE`"* is **withdrawn as a
specification**. The capability is real; the *documented procedure* is `seal`
followed, much later and under approval, by `dispose` — named commands with named
preconditions, a named invoker and three independent records (`sudo`
`log_output`, journald, `audit_events`). A bare `chattr -a` by a human is not a
procedure this design offers, and the operations document will say so.

### 6. What completeness is trusted to establish, and the contradiction removed

Package plan **§2.13.9**, logical schema **§2.9**.

> **Withdrawn.** *"Nothing in the fence depends on the journal being complete"* —
> revision 4, package plan §2.10.3 W-2 and logical schema §2.4. **It is false
> while `dispatch_journal_clear` is a required fence method, and it is withdrawn
> rather than defended.**

**The statement that replaces it:**

- **Trusted to establish:** *for a writer that executed its own dispatch path, the
  set of requests dispatched without a recorded outcome is the set the coordinator
  enumerates.* Trusted against crash, `SIGKILL`, power loss, reboot, unclean
  shutdown, disk-full, `fsync` failure, partial writes and defects elsewhere in
  the writer — because each of those **refuses** rather than under-reports.
- **The single direction of dependency:** the journal **can refuse** an activation
  the other four methods would permit; it **can never permit** one they would
  refuse, because all five are required and a clear journal is necessary and not
  sufficient.
- **Therefore an incomplete journal removes a refusal that should have occurred.**
  It never manufactures a permission. That is the direction in which the design is
  weakened, and it is bounded by durable storage, the directory permissions, the
  append-only attribute, the hash chain, the sequence, the seal, the registered
  generation and the fail-closed treatment of every unknown state.
- **What remains outside it:** **a writer whose dispatch path was itself replaced
  can call Google without journalling at all.** No record it authors bounds that.
  **R-5.0-10, new, and not mitigated away.**
- **What bounds that instead:** not the journal — the writer is dead, its cgroup
  is empty, a host scan found nothing, and Google refuses its access. And a writer
  compromised that deeply could have written the Sheet arbitrarily long before the
  fence, which is a condition no fence was ever going to repair.

**The alternative the handoff permits was considered and is offered rather than
taken.** Dropping `dispatch_journal_clear` and the journal would also remove the
contradiction — and would remove **the only control that refuses a cutover when a
request is *known* to be outstanding**, which is the case P5.0-R1 is actually
about. It is **D5.0-13 / OD-66 option C** so the choice is Peter's, and §2.13.9
states the reason it is not recommended so that reason can be disagreed with.

### 7. The Google residual, kept separate

Package plan **§2.13.10**.

- **§2.10.2's conclusion is unchanged.** No accepted-request completion barrier
  exists in the published Sheets v4 / Drive v3 surface; the thirteen-candidate
  search stands and is not re-opened.
- **A durable journal is not a fourteenth candidate.** Durability, a generation, a
  seal, a hash chain, an inode check and an immutable archive are all properties
  of **our** record. They observe nothing whatever about what **Google** has
  applied.
- **R-5.0-8 is not narrowed by one case.** A request Google accepted, whose
  response never reached the writer, and which Google applies after the final
  import, is exactly as unprevented and exactly as unprovable as in revision 4.
  What changed is that the *enumeration* is now trustworthy across a reboot, so
  the operator adjudicates a set that is real rather than one a `tmpfs` may have
  emptied.
- **Nothing is relabelled.** Stop condition **10b** is extended to name the
  journal's durability, generation, seal and archive among the things that must
  never be described as a barrier, and **10d** is added to forbid treating any
  unknown journal state as clear or inferring the append-only capability from a
  filesystem type — a standing guard against a repeat of P5.0-R5.

### 8. Re-pricing, and the rest of the design updated for the chosen lifecycle

**Estimate: PERT 35.5 implementer-days**, up from 29.2. Decomposed in package plan
§4: **+1.0** WP-4b's durable journal client; **+0.5** WP-2's sixth table and fifth
trigger condition; **+0.2** WP-3's generation value object and fifth command;
**+0.5** WP-6's registration and verification; **+0.2** WP-7's fourth check;
**+1.2** WP-8's twenty-six-case journal band; **+0.3** WP-9's rotation and
supervised reboot; **+0.2** WP-1's three numbers; **+0.2** WP-14's second
`sudoers` rows; **+2.0** the new **WP-15**.

Remediation allowance **10.3** days (30 % of ML); contingency **4.0**; security
review **2.0–3.0** reviewer-days; independent implementation review **2.5–3.0**.
Confidence low-to-moderate, with nine named drivers in §4 — including that **four**
design revisions have now been returned with Blocking findings.

| Area | Change |
|---|---|
| **Work packages** | **WP-15 new** (journal storage, generation lifecycle, `freedom-journal-admin`). WP-2, WP-3, WP-4b, WP-6, WP-7, WP-8, WP-9 and WP-14 all grow, each with its new closing evidence stated |
| **Numeric controls** | six → **nine**. **N5.0-21** free-space floor, **1 GiB**; **N5.0-22** rotation size ceiling, **64 MiB**; **N5.0-23** archive retention, **until §15.1's gate and not less than 365 days**, owned by the **Data Owner** |
| **Schema** | a **sixth table**, three evidence columns, a **fifth activation-trigger condition**, a **fifth command and idempotency scope**, a **fifth audit action**, a second sequence, a fourth append-only trigger. The "no mutable table anywhere" property is **preserved**: supersession is the successor's own row |
| **Operations** | §7.2 gains precondition **1b** (a registered, current, validating generation) and a rewritten step 5; a new *"if the journal itself is not in a known-good state"* branch that offers **repair-and-rotate or abandon and nothing else**; and a restore procedure that additionally compares the registered head against the on-disk seal and runs `archive-verify` |
| **Recovery** | §2.13.6 in full, plus the operations document's per-condition recovery and the `repair` command that seals rather than edits |
| **Monitoring** | a fourth `/healthz` check, `migration_journal_generation`, evaluated **against PostgreSQL alone** because the web identity has, by design, no access to the journal |
| **Risks** | **R-5.0-10** (a replaced dispatch path is outside what the journal bounds) and **R-5.0-11** (fail-closed refusal is an availability cost) are new; **R-5.0-3** and **R-5.0-9** are extended |
| **Assumptions** | **A-5.0-5** new and unconfirmed — a root-owned durable hierarchy, a **verified** `chattr +a`, `fsync` fault injection and a supervised reboot |
| **Decisions** | **D5.0-13 / OD-66 new**; **D5.0-10 / OD-63 extended to nine**; D-5.0-1 and D-5.0-2 extended |
| **Review scope** | security-relevant surfaces eight → **ten**, adding the root-run privileged tool and the durable evidence hierarchy; two further explicit questions for the Security Reviewer |

---

## The falsification and evidence plan, mapped

Package plan **§2.13.8** carries the `TC-5.0-JNL-01 … 26` band, one test per
bullet of the handoff's plan. §6.5 grows from eleven items to **fourteen**;
logical schema §4.3.8 gains **Band 3** and §9 gains five traceability rows.

| Handoff bullet | Test | What is asserted |
|---|---|---|
| verify the actual filesystem and append/immutability behaviour at the journal path | `JNL-01` | the path is on a **non-`tmpfs`, block-backed** filesystem; `+a` set; non-append write, `O_TRUNC`, `ftruncate`, `unlink` and `chattr -a` each fail with the expected `errno` |
| reboot between dispatch and outcome preserves an unresolved entry | `JNL-02a` | process-level: killed after the dispatch record, restarted, still unresolved |
| — | `JNL-02b` | boot-level: **a supervised host reboot in the WP-9 rehearsal.** This cannot be produced by an automated test on this host and, if the Operations Owner will not authorize a reboot, **is recorded as a check not run rather than claimed** |
| service restart cannot reset a non-empty or indeterminate generation | `JNL-03` | the writer **appends** and does not create; `seq` continues; creation fails `EACCES`; a `suspect` generation refuses to start |
| missing, replaced, truncated, corrupt, wrong-owner, wrong-mode, wrong-inode, sequence-gap, checksum-failure refuse clear evidence | `JNL-04 … 12` | one per condition **J-03 … J-12**, asserting the writer's named refusal code **and** the coordinator recording nothing |
| a compromised `freedomsheet` cannot unlink, rename, replace, truncate, rotate, clear or alter prior records or its parent | `JNL-13` | the ten rows above, under the `freedomsheet` uid, each with its `errno` |
| `SIGKILL` after durable intent, before dispatch, safely over-reports | `JNL-14` | the entry exists, is unresolved, **and the request was never sent** |
| `SIGKILL` after dispatch, before outcome, leaves a durable unresolved entry | `JNL-15` | it survives and names its ranges and payload digest |
| disk-full and `fsync` failure prevent dispatch | `JNL-16`, `JNL-17` | a loopback filesystem at `ENOSPC`; an injected `fsync` failure; **the Sheets client asserted never called** |
| outcome-append failure leaves the request unresolved and prevents activation | `JNL-18` | unresolved; `dispatch_journal_clear` refused; activation refused |
| privileged rotation and generation change preserve prior evidence and cannot fabricate an empty history | `JNL-19` | `init-generation` refused while unsealed; the archive `+i` and unmodifiable; `predecessor_close_digest` required; a second chain head refused by the partial unique index |
| coordinator observation binds generation, inode/content identity, writer unit, authority revision and observation time | `JNL-20` | the three evidence columns and the registered generation's inode, unit and deployment digest |
| reboot, restore or deployment rollback cannot reuse stale clear evidence | `JNL-21` | a generation registered after the evidence → activation refused; a restore predating a rotation → `status` refuses before any service starts |
| the activation trigger refuses missing, stale, cross-generation, corrupt or incomplete journal evidence | `JNL-22 … 26` | five trigger-refusal tests, each asserting its named reason, by direct statement against real PostgreSQL |
| the revision-4 host-boundary denial matrix remains planned and unchanged | §6.5 item 11 | **unchanged**, plus two rows: `sudo -l -U` lists **neither** `Cmnd_Alias` for any service identity, and an unauthorized `freedom-journal-admin` invocation is refused |

**Synthetic and disposable artifacts only.** Every case runs against a harness
writer, a disposable generation under a path the test creates and removes, and the
disposable `freedom_test` database. **No live Google Sheet, credential, production
database or production service is touched.**

---

## Traceability from the findings to the revised design

| Finding | Where the design answers it | Where the evidence is |
|---|---|---|
| **P5.0-R1** — no enforceable Sheet quiescence boundary | **Unchanged.** Plan §2.10.1 (the search), §2.10.2 (the conclusion), §2.10.3 (W-1 … W-6, with W-2 and W-3 strengthened by §2.13), §2.10.4 (the seven cases), §2.10.5 (G-A … G-D). Schema §2.2B, §2.8. **§2.13.10 records that durability is not a barrier** | §6.5 items 1–10; schema §9. **Item 9 remains recorded as *not met* for the Sheet path**, not substituted |
| **P5.0-R4** — shared-role proof ownership | **Unchanged.** Plan §2.11, §2.12 in full; schema §4.3.1 … §4.3.7. Two rows added to §4.3.8 Band 2 for the second `sudoers` drop-in; §4.3.1 additionally **removes `freedom-sheet-writer` from the runtime role**, since it holds no credential | §6.5 item 11; schema §4.3.8 Band 2. **Requires A-5.0-4, unconfirmed. No operational evidence is claimed passed** |
| **P5.0-R5** — the journal's storage and lifecycle | **Plan §2.13 in eleven subsections**: what was wrong, the storage decision, the hierarchy, the manipulation matrix, the generation, the twenty-one states, the privileged lifecycle, the record format, the completeness statement, the Google separation, and the priced options. **Schema §2.9, §3.4 condition 5, §3.5's three columns, §3.7's sixth table** | §6.5 items 12–14; §6.1 deliverable 13; schema §4.3.8 Band 3 and §9's five new rows. **Requires A-5.0-5, unconfirmed** |
| **P5.0-R2** | **Closed and preserved** — see below | schema §2.1, §2.5 |

---

## What P5.0-R2, OD-55 and OD-58 look like after this remediation

**P5.0-R2 — preserved, unchanged.** The accepted state matrix is restated in full
in logical schema §2.1 and the effective-time model in §2.5, both unchanged from
the text the re-review closed. Every accepted element stands: PostgreSQL is read-
and write-authoritative in `cutover`; `database` is accepted completion; authority
transfers at `shadow → cutover`; authorization and activation are separate;
authority is read only from an activated disposition and never from the revision
table; `effective_at` is the earliest instant a revision may be **activated**;
`verification_until` is required for `cutover` and forbidden for `database`; **no
state dual-writes in any of the four columns**. Revision 5 touches none of it.

**OD-55 — preserved.** Package 5.0 still creates no comparison-telemetry table,
column, grant, write path, decision-table row, access pattern, evidence claim or
risk. The common contract remains prose in package plan §11, **unchanged**, with
package 5.1 recorded as the implementation and schema owner and OD-56's
constraints carried into it. R-5.0-4 stays re-owned by 5.1. **The sixth table is
not telemetry**: it holds no comparison, no value, no character reference and no
outcome of any game operation — it registers the identity of a host file.

**OD-58 — preserved.** No ledger table. R-P4-4 remains Active and owned by 5.2.

**OD-59, OD-60 — unaffected, and worth stating because revision 5 adds a tool.**
`freedom-journal-admin` is a **host-local privileged operator command**, not a web
route, not a Discord command and **not a service principal**;
`application/service_principals.py` is untouched. It creates no mutation surface
for any player-facing behaviour.

---

## Estimates, risks, decisions, and the checks that were not run

**Estimates.** PERT **35.5** implementer-days; remediation allowance **10.3**;
contingency **4.0**; security review **2.0–3.0** reviewer-days; independent
implementation review **2.5–3.0**; supervised rehearsal **1.5–2.0** days of
Operations Owner time.

**Risks.** **R-5.0-10 new** — a replaced dispatch path is outside what the journal
can bound; owned by the Technical Lead with the Security Reviewer; **not
mitigated away**. **R-5.0-11 new** — fail-closed journal refusals are a Sheet
mutation outage; owned by the Operations Owner; **it is the price of the trade and
is named rather than discovered**. **R-5.0-3 extended** — a restore can also
return the generation register to a pre-rotation state, so the post-restore
procedure gains a seal comparison and an `archive-verify`. **R-5.0-9 extended** —
host-boundary drift now includes the journal hierarchy's owners, modes and
attributes. R-5.0-5, R-5.0-7 and **R-5.0-8 are unchanged**; R-5.0-8 in particular
is **not narrowed by this remediation**.

**Assumptions.** **A-5.0-5 new and unconfirmed.** A-5.0-3 and A-5.0-4 unchanged
and unconfirmed.

**Decisions.** **D5.0-13 / OD-66 new** — the journal's durable storage, generation
lifecycle and evidence-disposal authority, four things ruled together, options
J-1 … J-4. **D5.0-10 / OD-63 extended to nine** controls. D5.0-9 / OD-62,
D5.0-11 / OD-64 and D5.0-12 / OD-65 unchanged in substance; **D5.0-9 must not be
ruled until the Independent Reviewer accepts that G-A's enumeration control is
itself fail-closed**, which is what the handoff required and what §2.13 is for.

**Checks that could not be run, named rather than omitted:**

| Check | Why not | Who must complete it |
|---|---|---|
| **Whether `chattr +a` actually works on the journal filesystem** | setting the attribute needs `CAP_LINUX_IMMUTABLE`; the reading account is `uid=1000(foundry)` and setting it would have been an environment change this remediation is not authorized to make. **A-5.0-5** | Operations Owner, at WP-15 provisioning, through `verify-capability` |
| A supervised host reboot between a dispatch and its outcome (`JNL-02b`) | a reboot of this host is an operational action, not a test | Operations Owner, in the WP-9 rehearsal — **or recorded as not run** |
| An injected `fsync` failure (`JNL-17`) | needs a loopback device with `dm-error` or a syscall interposer, both host changes | Operations Owner / implementer at WP-8, under A-5.0-5 |
| Enumerate `/etc/sudoers.d/` | permission denied without privilege on 2026-08-29 | Security Reviewer |
| Host-wide setuid audit (`find / -perm -4000`) | not performed; a partial listing of `/usr/bin`, `/usr/sbin`, `/bin`, `/sbin` is not an audit and is not offered as one | Security Reviewer |
| PostgreSQL `log_connections` current value | `postgresql.conf` not readable without privilege | Operations Owner |
| Read the live `pg_hba.conf` / `pg_ident.conf` | not readable without privilege | Operations Owner |
| Confirm A-5.0-3, A-5.0-4 and **A-5.0-5** | all three are host or account provisioning decisions | Delivery Lead / Operations Owner |

---

## Exact commands run, and their results

Read-only, on 2026-08-29, as `uid=1000(foundry)`:

| Command | Result |
|---|---|
| `df -T /run /var/lib /opt/freedom-blades /var /tmp` | `/run` → `tmpfs`; the other four → `ext4` on `/dev/vda1` |
| `grep -E ' (/\|/var\|/var/lib\|/run\|/opt) ' /proc/mounts` | `tmpfs /run tmpfs rw,nosuid,nodev,noexec,relatime,size=806112k,mode=755,inode64`; `/dev/vda1 / ext4 rw,relatime,discard,errors=remount-ro` |
| `command -v chattr lsattr tune2fs dumpe2fs` | `/usr/bin/chattr`, `/usr/bin/lsattr`, `/usr/sbin/tune2fs`, `/usr/sbin/dumpe2fs` |
| `lsattr /opt/freedom-blades/platform/CLAUDE.md`, `lsattr -d /var/lib`, `lsattr -d /run` | `--------------e-------` for both ext4 paths; an **empty** field for `/run` |
| `ls -ld /var/lib /run /var/lib/freedom* /etc/freedom-blades /opt/freedom-blades` | `/var/lib` `drwxr-xr-x root:root`; `/var/lib/freedom*` **No such file or directory**; `/etc/freedom-blades` `drwxr-x--- root:root`; `/opt/freedom-blades` `drwxrwsr-x foundry:nogroup` |
| `id` | `uid=1000(foundry) gid=1000(foundry) groups=1000(foundry),27(sudo),100(users)` |
| `uname -r` | `6.8.0-138-generic` |
| `systemctl --version` | `systemd 255 (255.4-1ubuntu8.17)`, unified hierarchy |
| `systemctl list-units --type=service --all \| grep -i freedom` | `freedom-bot`, `freedom-web`, `freedom-worker` — all `loaded active running` |
| `wc -l` over the plan, schema, handbacks and registers | used to plan the reading; no file was truncated or generated |
| **`git diff --check`** | **clean — no output, exit 0.** Run against the working tree being submitted |
| `git status --porcelain` | the changed files are the two design artifacts, this handback, and the status, RAID, decision, open-decision and change-log registers, alongside the pre-existing unrelated working-tree changes this remediation did not touch |

**No test suite was run, because no code exists for this package.** No figure from
any suite is cited for package 5.0, and **no executable control is claimed to have
passed.** Formatter, linter and type checker: **none is configured** in this
repository, recorded as *not configured* and never as *passed*.

---

## Explicit statement that no implementation or environment change occurred

**No implementation or environment change occurred in producing this
remediation.**

- No production code was written or modified.
- No migration was written; migration `0014` does not exist and the head remains
  `0013`.
- No table, index, trigger, sequence, grant, database role, `pg_hba.conf`,
  `pg_ident.conf` or `postgresql.conf` entry was created or altered, in any
  database. No configuration was reloaded.
- No operating-system account, group, `sudoers` file or deployment path was
  created or altered. `freedomcoord`, `freedomsheet`,
  `/opt/freedom-blades/coordinator` and `freedom-journal-admin` are proposals in a
  document; none exists on this host.
- **No directory, file, file mode or filesystem attribute was created or
  altered.** `/var/lib/freedom-sheet-writer` **does not exist on this host and was
  not created**; **no `chattr` was run**; the only attribute interaction was
  `lsattr`, which reads.
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

**The host was read and never written.** The changed files are
`docs/review/phase-5-0-package-plan.md`,
`docs/review/phase-5-0-logical-schema.md`, this handback, and the status, RAID,
decision-register, open-decisions and change-log documents.

---

## What is requested next

1. **Codex independent re-review** of both design artifacts. For **P5.0-R5**,
   against §2.13 as a whole — **the most useful disagreement would be a journal
   condition §2.13.6 does not list, or a manipulation §2.13.4 does not refuse.**
   For **P5.0-R4**, against the unchanged boundary and the two added rows. For
   **P5.0-R1**, against §2.10.1's search, whose conclusion a single published
   citation would overturn — an outcome this package would prefer to the one
   recorded.
2. **Peter's rulings** on **D5.0-13 / OD-66** (new; four things together,
   including option **J-3**, which would drop the journal and is his to take),
   D5.0-9 / OD-62 (**a risk acceptance**, and one the R4 handoff says must wait
   until the enumeration control is itself fail-closed), D5.0-10 / OD-63 (nine
   controls, N5.0-23 the Data Owner's), D5.0-11 / OD-64 and D5.0-12 / OD-65.
3. **A named Security Reviewer**, whose scope grew again: a second privileged tool
   that runs as root, a root-owned durable evidence hierarchy with filesystem
   attributes, and an evidence-disposal path, on top of everything R3 named. **Two
   checks in §2.12.6 and one in §2.13.2 are theirs**, not the implementer's.
4. **Confirmation of A-5.0-3, A-5.0-4 and A-5.0-5.** Without A-5.0-4 the R3-B
   evidence is unproducible; **without A-5.0-5 no journal generation can be
   registered at all and the whole `TC-5.0-JNL` band is unproducible**, so
   P5.0-R5 cannot close on evidence.

**Implementation remains unauthorized.** No work package starts while any Blocking
finding, D5.0-9, D5.0-10, D5.0-11, D5.0-12, D5.0-13 or the Security Reviewer
assignment remains open.
