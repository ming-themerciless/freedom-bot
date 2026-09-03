# Package 5.0 — design remediation R3 handback

Date: 2026-08-29 · Package 5.0 — Migration and cutover harness

Prepared by: Claude — implementer and working Technical Lead (designated, OD-61)

Returned to: Peter Duscha (Acceptance Authority, Product Owner, Data Owner,
Operations Owner, Delivery Lead) and Codex (Independent Reviewer and independent
logical-schema reviewer, OD-61).

In response to: `docs/review/Handover information`, *Package 5.0 — design
remediation R3 handoff*, which **authorizes design and documentation remediation
only**.

> **Claude claims no finding closed.** P5.0-R1 and P5.0-R4 are closed by the
> Independent Reviewer, not here.
>
> **The two findings are answered differently, and the difference is the point of
> this handback.** For **P5.0-R4** the handoff asked for a boundary and a
> boundary is supplied: a dedicated operating-system identity, an exact peer
> mapping, a host privilege model and a per-identity denial matrix. For
> **P5.0-R1** the handoff permitted two answers, and this remediation takes the
> **second**: after searching thirteen candidate barriers against the published
> Google surface, it concludes that **the published APIs cannot supply the
> accepted-request completion barrier**, states precisely which invariant cannot
> be guaranteed, states the weaker guarantees that can be, and returns a newly
> priced choice to Peter. **No barrier was invented, and nothing was relabelled
> as one.**

---

## The nine required handback items

### 1. The revised plan and schema, with a revision-4/R3 change table

| Artifact | Revision | What is new |
|---|---|---|
| [`phase-5-0-package-plan.md`](phase-5-0-package-plan.md) | **4 — remediation R3** | §2.9 (two new evidenced facts about the client), §2.10 rewritten as a barrier search with the conclusion, the achievable guarantees, the seven required cases and four priced options, plus §2.10.6 retaining revision 3's comparison; **new §2.12** for the coordinator host boundary; §3 (WP-4b extended, **WP-14 new**, WP-13 demoted); §4 (PERT 29.2); §5.3 (D5.0-9 reframed, D5.0-10 extended, D5.0-11 extended, **D5.0-12 new**); §6.1 and §6.5 (new evidence bands); §7.1 (two new failure modes), §7.2 (the ordering change), §7.4 (**R-5.0-8**, **R-5.0-9**, **A-5.0-4**); §8.1 (**H-1, H-2, H-3** and four checks not run); §8.3 (six controls); §9.2, §9.3, §9.4, §10 |
| [`phase-5-0-logical-schema.md`](phase-5-0-logical-schema.md) | **4 — remediation R3** | §2.2B rewritten around what cannot be guaranteed; §2.3 protocol re-ordered; §2.4 (the fifth evidence kind, with its weaker standing stated where a reader meets it); §2.7; **new §2.8** stating the boundary of every claim in one table; §3.5 (`dispatch_journal_clear`, five required methods); **§4.3 rewritten and roughly trebled** into the identity, authentication, grant and evidence model; §7 (three rows rewritten or added, including one revision-3 answer explicitly withdrawn); §8; §9; §10 |
| This handback | **new** | the nine items |

**Change table — revision 3 → revision 4.**

| # | Change | Where | Why |
|---|---|---|---|
| 1 | The claim that termination + revocation is an **enforceable** Sheet fence is **withdrawn** | plan §2.10, schema §2.2B | it is not one; neither control speaks to an accepted request |
| 2 | A thirteen-candidate barrier search and its conclusion are **added** | plan §2.10.1–2.10.2 | the handoff requires the barrier to be evidenced or rejected explicitly |
| 3 | Six achievable weaker guarantees **W-1 … W-6** are **added** | plan §2.10.3, schema §2.8 | so what *is* true is stated as precisely as what is not |
| 4 | The fence ordering changes to **drain → terminate → revoke** | plan §7.2, schema §2.3 | revoking first converts *completed and known* into *failed and unknown* |
| 5 | An **explicit request timeout** and a **host-local dispatch journal** are added to the writer | plan §2.9, §2.10.3, WP-4b | today no timeout is set, so the in-flight window is unbounded; the journal makes the unresolved set enumerable |
| 6 | `dispatch_journal_clear` becomes a **fifth required fence method**, with N5.0-20 fixing the permitted unresolved set at zero | schema §3.5, §2.4 | a non-empty set must refuse a cutover rather than be waited out |
| 7 | Two **post-import divergence re-reads** are added | plan §7.2, schema §2.3 | a late apply cannot be prevented, so it must be detected |
| 8 | A **dedicated `freedomcoord` OS identity**, `pg_hba` ordering, a single `pg_ident` map line, a `sudoers` boundary, a root-owned deployment path, ownership and modes, and a per-vector argument are **added** | plan §2.12, schema §4.3 | R3-B |
| 9 | A **host-boundary evidence band** is added, and needs a disposable OS identity (**A-5.0-4**) | schema §4.3.8 Band 2, plan §6.5 item 11 | the handoff requires real PostgreSQL and host tests |
| 10 | **H-1, H-2, H-3** and four *checks not run* are recorded | plan §8.1 | the design must not assume away the host it runs on |
| 11 | N5.0-17 and N5.0-18 **reframed**; N5.0-19 and N5.0-20 **new**; WP-13 **demoted** | plan §8.3, §3 | neither reframed number bounded what revision 3 said it bounded |
| 12 | **R-5.0-8** and **R-5.0-9** raised; **D5.0-12 / OD-65** raised; D5.0-9 reframed a third time; D5.0-11 extended | plan §5.3, §7.4 | the residual and the host topology are decisions, not design details |
| 13 | Estimate **23.7 → 29.2**; remediation allowance 6.8 → 8.4; contingency 3.0 → 3.5; security review 1.0–1.5 → **1.5–2.5** | plan §4, §9.2 | decomposed line by line in §4 |
| 14 | **No table is added.** Five tables, as in revision 3 | schema §3 | the journal is a host file precisely so the legacy mutation path keeps taking no database dependency |

### 2. The Google accepted-request completion argument, or the proof that no adequate barrier was found

**No adequate barrier was found.** This is the handoff's option 2, taken
deliberately.

**The invariant.**

> **I-SHEET-COMPLETE.** Every `spreadsheets.values.batchUpdate` request Google
> accepted before the fence began is durably reflected in the spreadsheet before
> the final import reads it.

**The search.** Thirteen candidates, each judged against one question — *does it
distinguish "applied" from "not applied **yet**"?* The full table is package plan
§2.10.1. In summary:

| Verdict | Candidates |
|---|---|
| **The only affirmative fact that exists**, and only for requests whose response the client received | B-1, the `batchUpdate` response itself |
| **Does not exist** in the published surface | B-2 operation id, B-3 idempotency token, B-4 conditional write / ETag / `If-Match`, B-12 a document-level flush |
| **Describes applied state**, so it can only support a quiet period | B-5 Drive `files.version`, B-6 `revisions.list`, B-13 waiting |
| **Documented as unreliable** for this purpose | B-7 Activity API, B-8 push notifications |
| **Rests on an unpublished implementation property** | B-9 a marker write (and it adds nothing over B-1 even if it held), B-10 protected ranges, B-11 `files.copy` |

**And one further question, because revision 3 leaned on it implicitly:** does
revoking the Drive permission cancel a request Google already accepted? **No
published statement was found** about when authorization is evaluated relative to
application, so revocation bounds *new* requests and must not be argued to abort
accepted ones. Revision 3 came close to arguing that; revision 4 withdraws it.

**Standing of these claims.** Each is an *implementer's reading of the published
reference surface as of 2026-08-29*, stated as **not found**, never as a proof of
absence — the same register revision 3 used for the no-conditional-write claim.
**A single citation contradicting any row would overturn the conclusion, and that
outcome is preferred to the one recorded here.**

**The conclusion.** No observable fact available to this project separates
*"applied"* from *"not applied yet"* for a request whose response was lost.
**I-SHEET-COMPLETE cannot be guaranteed with the published Google APIs, and
P5.0-R1's Sheet half is not closed by this revision.**

**Which weaker guarantee is achievable** — plan §2.10.3, schema §2.8:

- **W-1** every request whose response the writer received is proved applied;
- **W-2** the unresolved set is enumerable and normally empty, from a
  `fsync`-ed, append-only, host-local journal written **before** dispatch —
  *a completeness aid, not a proof*, and nothing in the fence depends on it;
- **W-3** a non-empty unresolved set **refuses the activation** (N5.0-20 = zero);
- **W-4** nothing that happens on the Sheet afterwards can reach PostgreSQL;
- **W-5** two post-import re-reads detect a late apply within the window; and
- **W-6** a `→ legacy` replay is blocked until the divergence report exists.

**The residual, in one sentence:** *a `values.batchUpdate` request Google
accepted, whose response never reached the writer, and which Google applies after
the final import has read the Sheet, is not prevented and cannot be proved
absent — it is enumerated if the writer was working correctly, it refuses the
cutover while outstanding, it cannot corrupt PostgreSQL, and it is detected within
the verification window.*

### 3. The revised option comparison and the concrete decision Peter must make

**D5.0-9 / OD-62, reframed a third time.** Both earlier framings are withdrawn:
revision 2's was priced on a lease that did not close the finding, revision 3's on
an enforceability claim that item 2 retracts. The question is no longer *which
fence*; it is **what is accepted in place of one.**

| | Option | What it gives | What it costs |
|---|---|---|---|
| **G-A** *(recommended)* | Drain-first boundary with an enumerable unresolved set, fail-closed activation, containment and detection (W-1 … W-6) | the strongest set of *verifiable* properties available | a fourth systemd unit and a fifth OS identity; a Sheet-mutation outage per fence window; a production Drive-permission change per cutover; an `fsync` on the legacy mutation path; an operator adjudication step; **and an explicitly accepted residual** |
| **G-B** | Pre-cutover write-path retirement: deploy a build without the unit's Sheet write path, refuse those mutations for an accepted period, then import | stronger *in kind* — the in-flight set is empty by deployment, not by timing | a mutation outage measured in days, roughly forty times. **Variant G-B′** does it once for the whole bot |
| **G-C** | Accept a measured quiet period as the boundary | simplicity | **this is what the re-review rejected.** Listed so the residual can be accepted knowingly rather than relabelled. Not recommended |
| **G-D** | Cut no Sheet-authoritative unit over; 5.0 still delivers the PostgreSQL fence, the isolated writer, the journal, the access control, the detection and the monitoring | nothing untrue is claimed | Phase 5's field cutovers do not proceed. Shadow comparison and the platform build continue |

**Why this is Peter's and not the implementer's.** `.agents/AGENTS.md` gates bot
degradation and production access changes, and that still holds. Revision 4 adds
a stronger reason: **G-A, G-B and G-C all require someone to accept an unprovable
residual on the authoritative store of a live community's game state.** That is a
risk acceptance under plan §0.2 and §0.3 and belongs to the Acceptance Authority.

**Three further decisions are open**, priced in package plan §5.3: **D5.0-10 /
OD-63** (six numeric controls, two reframed and two new), **D5.0-11 / OD-64**
(extended: the database principal **and** its OS identity and host boundary), and
**D5.0-12 / OD-65** (new: the `freedomsheet` identity and credential relocation,
hardening on the live `freedom-bot` unit, and a ruling on the group-writable
repository tree).

### 4. The named OS/database identity mapping and host privilege model

**The identity.** `freedomcoord` : `freedomcoord` — a system account for this
purpose alone. No password, `/usr/sbin/nologin`, no home directory, no SSH key, no
supplementary groups. Distinct from `discordbot` (the bot), `freedomweb` (web and
worker), the proposed `freedomsheet` (the Sheet writer) and `foundry` (the
maintainer), and in no group any of them holds.

**The mapping.** `pg_hba.conf`, placed above any broader `local all all` line
because PostgreSQL takes the first matching rule:

```
local        __PROD_DB__     freedom_migration_coordinator            peer    map=freedom_coord
local        all             freedom_migration_coordinator            reject
host         all             freedom_migration_coordinator   all      reject
hostssl      all             freedom_migration_coordinator   all      reject
hostnossl    all             freedom_migration_coordinator   all      reject
```

`pg_ident.conf`, one line, no regular expression:

```
freedom_coord    freedomcoord       freedom_migration_coordinator
```

and the role created `LOGIN … PASSWORD NULL CONNECTION LIMIT 2`, with `CONNECT`
revoked from `PUBLIC` and granted to it alone.

**Four independent layers must all hold**, and each fails differently: the kernel
reports the peer uid (unforgeable); `pg_ident` translates only `freedomcoord`;
the first matching `pg_hba` rule requires local transport and one database, with
every other combination written out as a `reject` so a later broad `host` line
cannot silently expose it; and `PASSWORD NULL` makes password authentication
impossible, so a leaked `.pgpass` or environment file is worthless. **The socket
path is deliberately not a layer** — `/var/run/postgresql` is world-reachable
(H-3), so the map is the control, and a private socket directory was considered
and rejected as a failure mode without a benefit.

**The host privilege model.** One `sudoers` drop-in, `root:root 0440`, naming
`foundry` only, with `env_reset`, `!setenv`, `secure_path` and `log_output`, **no
`NOPASSWD`**, and **one fixed absolute executable path** — a root-owned wrapper
rather than `python -m …`, because `-m` resolves through a path a caller could
influence. The wrapper unsets the `PYTHON*` and `PG*` families, sets a working
directory the services cannot write, and runs `python -I -P -m migration_authority`.

**Ownership and modes** are in package plan §2.12.5. The load-bearing one:
`/opt/freedom-blades/coordinator` is `root:root`, **outside** the repository —
because observation **H-1** is that `/opt/freedom-blades/platform` is
`drwxrwsr-x foundry:discordbot` with group-writable files, and `freedomweb` is in
group `discordbot`, so **the bot, web and worker processes can today rewrite every
module in this repository including `tools/`.** A coordinator that ran
`python -m tools.migration_authority` from that tree would execute code a
compromised service process can choose. **That is the vector revision 3 failed**,
and it is closed by the deployment path plus a digest comparison at deploy, not by
an argument.

**Per-vector answers** are package plan §2.12.6 and the two authentication and
authorization matrices are schema §4.3.5. **Two rows rest on checks that could
not be run**: `/etc/sudoers.d/` was refused without privilege, and no host-wide
setuid audit was performed. Both are recorded as *not run* rather than assumed
clear, and the Security Reviewer must complete them.

**Provisioning, audit, revocation, recovery and rotation** are schema §4.3.7.
There is **no secret to rotate**: rotation means changing which OS account the map
names, in two testable steps. Every revocation route is fail-closed — it can
prevent a cutover and never permit one.

### 5. The complete per-principal and per-OS-identity grant/authentication matrix

Schema §4.3.5, in two tables.

**Authentication.** `discordbot`, `freedomweb` and `freedomsheet` can each
authenticate as `__APP_ROLE__` (they hold its credential) and as **nothing else**;
none can become `freedom_migration_coordinator`, refused at layers 1 and 2.
`freedomcoord` can become the coordinator over the local socket to one database,
and is refused over TCP and by password. `foundry` reaches the coordinator **only
through the `sudoers` rule** — and, being in `sudo`, can reach root anyway, so the
boundary is against service compromise and operator mistake, not against the
maintainer. `root` is above every boundary here and the design says so rather than
pretending otherwise.

**Authorization.** On the five package-5.0 tables: the schema owner has DDL and
the seed, with `UPDATE`/`DELETE` refused by trigger on the three append-only
tables; `__APP_ROLE__` has `SELECT` on four and **nothing at all** on
`migration_quiescence_evidence`; the coordinator has `SELECT, INSERT` on the three
append-only tables and `SELECT` on the two reference tables, with
`UPDATE`/`DELETE`/`TRUNCATE` revoked **and** trigger-refused everywhere.

**The two tables together are the claim.** Forging a fence observation needs both
an OS identity the map accepts and a grant on the evidence table. No service
identity has either, and no application principal has the second at any privilege
level.

### 6. The falsification tests and supervised evidence, mapped to both findings

Package plan §6.5 carries the handoff's evidence plan, now **eleven** items;
schema §4.3.8 carries the database and host bands; schema §9 carries the
traceability matrix.

**Mapped to P5.0-R1:**

- a transaction opened at `cutover`, held by a barrier across an activation of
  `cutover → legacy`, then committed — **refused by the trigger**, asserted on the
  refusal;
- a `SIGSTOP`ped harness writer terminated through its unit, cgroup asserted
  empty, resumption asserted impossible;
- a **drained** writer completing an outstanding call and recording its outcome;
- a journal entry present after a `SIGKILL` between the `fsync` and the dispatch;
- a **killed** writer leaving an unresolved entry, `dispatch_journal_clear`
  refused, and the activation refused;
- a call dispatched after revocation refused at the API boundary;
- an out-of-systemd duplicate detected by host scan and refused at the boundary;
- the fenced ranges mutated out-of-band after the import, both re-reads reporting
  the divergence, and a `→ legacy` replay refused until the report exists.

**No test asserts that a dispatched call has completed**, because nothing can.
The revision-3 test that did is **withdrawn**, and schema §7's corresponding row
records the withdrawal rather than quietly replacing it.

**Mapped to P5.0-R4:**

- the full direct-SQL denial matrix under every principal, against PostgreSQL;
- forged evidence recorded as **unconstructable**, with the `has_table_privilege`
  proof rather than a test that tries and fails;
- missing, stale and cross-revision proof each refused by the activation trigger,
  asserting the named refusal reason;
- **peer attempts as the coordinator role under `discordbot`, `freedomweb`,
  `freedomsheet` and `foundry`, each refused by PostgreSQL**;
- the dedicated identity accepted on the socket and refused over TCP with and
  without a password, and against a second database;
- `sudo -l -U` empty for every service identity, and an unauthorized invocation
  refused;
- `EACCES` writing the root-owned deployment path under each service identity;
- `PYTHONPATH`/`PYTHONHOME`/`PGSERVICE` stripped across the `sudo` boundary and a
  planted shadowing module not imported; and
- **the positive invariant: no entry on the effective `sys.path` is writable by
  any service identity**, computed under each uid rather than reasoned about;
- a `pg_ident` rotation exercised in both intermediate states.

**Supervised evidence:** the WP-9 rehearsal on the disposable database, witnessed
by the Operations Owner, now including a drain proof, a termination proof, an
access revocation, an unresolved-set adjudication, both divergence re-reads and a
rollback.

**One dependency is stated rather than discovered later.** The host band needs a
**disposable OS identity, a `pg_hba`/`pg_ident` entry and a configuration
reload**. The attacking side can use the existing service identities read-only;
the coordinator side cannot be simulated. This is **assumption A-5.0-4,
unconfirmed**, and without it P5.0-R4 cannot close on evidence.

### 7. Changes to decisions, topology, credentials, estimates, risks and tests

**Decisions.**

| Ref | Change |
|---|---|
| **D5.0-9 / OD-62** | **Reframed a third time.** No barrier exists, so the question becomes what is accepted in place of one: G-A, G-B, G-C or G-D. **It is now a risk acceptance and belongs to the Acceptance Authority.** Both earlier framings withdrawn and retained as history |
| **D5.0-10 / OD-63** | **Extended from four to six.** N5.0-14 and N5.0-16 unchanged; **N5.0-17 reframed** as the writer drain timeout; **N5.0-18 reframed** as a post-revocation margin explicitly labelled *not a barrier*; **N5.0-19 new** (explicit request timeout, 30 s proposed); **N5.0-20 new** (unresolved entries permitted at activation, **zero**) |
| **D5.0-11 / OD-64** | **Extended.** It now covers the database principal **and** the dedicated OS identity, the peer map, the `sudoers` boundary and the root-owned deployment path. Approving the role alone would approve a control that does not exist. Blocks WP-2 **and WP-14** |
| **D5.0-12 / OD-65** | **New.** The `freedomsheet` identity and the Google credential relocated into `root:freedomsheet 0640`; hardening directives on the live `freedom-bot` unit (Phase 0 finding F-3); and a ruling on the group-writable repository tree (H-1). Blocks WP-4b and WP-14 |
| D5.0-1 … D5.0-8 | Unchanged. **OD-60 is again explicitly unaffected**: the coordinator is a database principal reached by a human through `sudo`, not a service principal, and `application/service_principals.py` is untouched |

**Topology and credentials — proposed, none adopted.**

- one new database role, peer-authenticated, **no secret to distribute**;
- **two new OS identities**, `freedomcoord` and `freedomsheet`;
- a `sudoers` drop-in naming `foundry` only, without `NOPASSWD`;
- `pg_hba.conf` ordering and one `pg_ident.conf` map line, applied by reload;
- a **root-owned deployment path outside the repository**, with digest
  verification at deploy;
- the Google service-account credential relocated out of the bot process;
- hardening directives added to a live `freedom-bot` unit; and
- **unchanged:** OD-20/21/22 — same host, loopback, separate roles and environment
  files. No service moves, no port opens, no credential is shared.
- **Still withdrawn from revision 2 and not given back:** the standing PostgreSQL
  availability dependency for Freedom-bot mutations. The dispatch journal is a
  **host file**, chosen precisely so the legacy mutation path keeps taking no
  database dependency.

**Estimate.** PERT **29.2** implementer-days, up from 23.7. Decomposed: **+1.0**
drain, timeout and journal; **+0.5** journal reading, ACL readback and divergence
re-read; **+1.0** host-boundary denial matrix; **+0.4** rehearsal additions;
**+0.4** contract numbers; **+2.2** the new WP-14. Remediation allowance **8.4**
days (30 % of ML); contingency **3.5**; security review **1.5–2.5**
reviewer-days; independent implementation review 2.0–2.5. Confidence
low-to-moderate, with the drivers in plan §4 — including that the package's
completion now depends on a risk-acceptance decision rather than on
implementation quality.

**Risks.** **R-5.0-8 new** — the accepted, unprovable Sheet residual, **owned by
the Acceptance Authority** rather than by the Technical Lead, because it is not a
thing implementation can close. **R-5.0-9 new** — host-boundary drift after
provisioning, detected on re-run rather than prevented. **A-5.0-4 new and
unconfirmed** — a disposable OS identity and `pg_hba` reload for the R3-B
evidence. R-5.0-5 unchanged; R-5.0-7 unchanged; A-5.0-3 unchanged but less
consequential, because N5.0-18 is now a margin rather than a control; **D-5.0-1**
grew again with the security-review scope; **D-5.0-2** extended to four rulings.

**Tests.** Added: the drain and journal band (six cases); the two divergence
re-reads; the host-boundary band (ten cases). **Rewritten:** handoff evidence item
3, whose revision-3 form asserted a property that cannot be established.
**Recorded as not met rather than substituted:** handoff evidence item 9 for the
Sheet path.

### 8. Confirmation that P5.0-R2 and OD-55 remain preserved

**P5.0-R2 — preserved.** The accepted state matrix is restated in full in logical
schema §2.1 and the effective-time model in §2.5, both unchanged from the text the
re-review closed. Every accepted element stands: PostgreSQL is read- and
write-authoritative in `cutover`; `database` is accepted completion; authority
transfers at `shadow → cutover`; authorization and activation are separate;
authority is read only from an activated disposition and never from the revision
table; `effective_at` is the earliest instant a revision may be **activated**;
`verification_until` is required for `cutover` and forbidden for `database`; no
state dual-writes in any of the four columns.

**Revision 4 changes nothing in that area.** Its changes are to §2.2B, §2.3's
ordering, §2.4's fifth evidence kind, the new §2.8, §3.5's vocabulary, §4.3, §7,
§8, §9 and §10.

**OD-55 — preserved.** Package 5.0 still creates no comparison-telemetry table,
column, grant, write path, decision-table row, access pattern, evidence claim or
risk. The common contract remains prose in package plan §11, unchanged, with
package 5.1 recorded as the implementation and schema owner and OD-56's
constraints carried into it. R-5.0-4 stays re-owned by 5.1.

**OD-58 — preserved.** No ledger table; R-P4-4 remains Active and owned by 5.2.

**OD-54, OD-56 … OD-61** are traced in package plan §5.2.

### 9. Explicit statement of what was not run, and that nothing changed

**No implementation or environment change occurred in producing this
remediation.**

- No production code was written or modified.
- No migration was written; migration `0014` does not exist and the head remains
  `0013`.
- No table, index, trigger, sequence, grant, database role, `pg_hba.conf`,
  `pg_ident.conf` or `postgresql.conf` entry was created or altered, in any
  database. No configuration was reloaded.
- **No operating-system account, group, `sudoers` file, deployment path,
  directory, file mode or filesystem attribute was created or altered.**
  `freedomcoord`, `freedomsheet` and `/opt/freedom-blades/coordinator` are
  proposals in a document; none exists on this host.
- No configuration file, environment variable, `.env`, systemd unit or deployment
  artifact was created or altered. `freedom-sheet-writer` is a proposal, not a
  unit on this host.
- No credential was read, written, created, rotated, revoked or distributed.
- **No Google access was changed.** No Drive permission, spreadsheet ACL or
  service-account key was read, modified or exercised. No Sheet was accessed, in
  any mode. **No Google API was called**, including for the §2.10.1 search, which
  is a reading of published documentation and not a probe.
- No service was deployed, started, stopped or restarted.
- No data was mutated, in any database.
- No authority cutover occurred; every migration unit remains `Legacy` in the
  controlled register, and no control plane exists to record otherwise.
- No Package 5.1+ work was begun.

**What was run, and what was not.**

- **The host was read and never written.** The §8.1 observations are the output of
  `ls -l`, `ls -ld`, `getent`, `id`, `df -T`, `find`, `systemctl show` and
  `wc`/`grep` over repository files, on 2026-08-29.
- **`git diff --check` was run and is clean.** The documentation diff was reviewed
  for secrets, production identifiers and accidental authorization.
- **No test was run for this package, because no code exists for it.** No figure
  from any suite is cited for package 5.0, and **no executable control is claimed
  to have passed.**
- **Formatter, linter and type checker: none is configured** in this repository.
  That is recorded as *not configured*, never as *passed*.

**Checks that could not be run, named rather than omitted:**

| Check | Why not | Who must complete it |
|---|---|---|
| Enumerate `/etc/sudoers.d/` | permission denied without privilege on 2026-08-29 | Security Reviewer |
| Host-wide setuid audit (`find / -perm -4000`) | not performed. A partial listing of `/usr/bin`, `/usr/sbin`, `/bin`, `/sbin` showed the distribution's usual set; that is not an audit and is not offered as one | Security Reviewer |
| PostgreSQL `log_connections` current value | `postgresql.conf` not readable without privilege | Operations Owner |
| Read the live `pg_hba.conf` / `pg_ident.conf` | not readable without privilege | Operations Owner |
| Confirm A-5.0-3 (disposable Google resources) and **A-5.0-4** (disposable OS identity and reload) | both are host or account provisioning decisions | Delivery Lead / Operations Owner |

The changed files are the two design artifacts, this handback, and the status,
RAID, decision, open-decision and change-log registers.

---

## What is requested next

1. **Codex independent re-review** of both design artifacts. For **P5.0-R4**,
   against the boundary and the evidence plan supplied. For **P5.0-R1**, against
   the *search* in package plan §2.10.1 and the conclusion in §2.10.2 — the
   productive disagreement here would be a published Google mechanism the search
   missed, and a citation would be welcomed rather than resisted.
2. **Peter's rulings** on D5.0-9 / OD-62 (reframed a third time; **now a risk
   acceptance**), D5.0-10 / OD-63 (six controls), D5.0-11 / OD-64 (extended to the
   OS identity and host boundary) and D5.0-12 / OD-65 (new).
3. **A named Security Reviewer**, whose scope grew again: two OS identities, a
   `sudoers` drop-in, `pg_hba`/`pg_ident` ordering, a root-owned deployment path,
   hardening on a live unit, the pre-existing group-writable repository tree, a
   credential relocation and a production-access procedure. **Two checks in §2.12.6
   are theirs to complete**, not the implementer's.
4. **Confirmation of A-5.0-3 and A-5.0-4.** Without A-5.0-4 the entire R3-B
   evidence plan is unproducible and P5.0-R4 cannot close on evidence.

**Implementation remains unauthorized.** No work package starts while either
Blocking finding, D5.0-9, D5.0-10, D5.0-11, D5.0-12 or the Security Reviewer
assignment remains open.
