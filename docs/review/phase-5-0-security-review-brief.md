# Package 5.0 — Security Reviewer briefing pack

Date: 2026-08-31 · **updated for the revision-12 re-review**
Reviewer: **Codex**, named Package 5.0 Security Reviewer by Peter Duscha
(Acceptance Authority / Product Owner) on 2026-08-31, closing OD-61 / D5.0-8.
Prepared by: Claude, implementer and working Technical Lead.

This pack discharged required action 1 of `docs/review/Handover information`.
It is a briefing, not a review, not a recommendation and not an authorization.

**Disposition, 2026-09-02.** Codex completed the revision-12 re-review in
`phase-5-0-security-rereview-revision-12.md`. P5.0-SR1 and P5.0-SR2 are Closed
on design and the twelve-surface design review is delivered. C-1/C-3/C-4 and
the remaining operational evidence are still outstanding; no readiness
recommendation was made.

## 0. What has happened since this pack was first written

**The first pass ran on 2026-08-31 and returned `changes requested` with no
readiness recommendation** — `docs/review/phase-5-0-security-review.md`, against
revision 11. Two findings:

| Finding | Severity | What it said |
|---|---|---|
| **P5.0-SR1** | **Blocking** | The deployment integrity check can be skipped silently. `deployment_manifest_digest()` compares a digest of the live deployed bytes with a caller-supplied copy of that same value, which proves consistency after deployment and **not provenance from the reviewed commit**; nothing required a trusted reviewed-commit manifest, and no step refused when the comparison was omitted |
| **P5.0-SR2** | Important | The OS identity contract contradicted the journal group contract: §2.12.2 said `freedomcoord` and `freedomsheet` were in their own groups only, while §2.13.3 and the E1–E8 identities required both to be in `freedomjournal` |

**Revision 12 is the remediation of both, and claims neither closed.** What it
adds, and what to re-review:

- **§2.12.5a** — the reviewed-source provenance contract: an out-of-band
  `root:root 0444` approval record; a **bare** `root:root 0700` Git object store
  addressed **by object id**, with no ref, branch or tag resolved anywhere; a
  trusted manifest computed from **Git object bytes**; a **closed two-region
  partition** of the deployed root; **Algorithm D `D0 … D8`** with refusals
  `DEP-01 … DEP-09` and a rollback; and a provenance record written last and
  outside the deployed root.
- **§2.13.5a C0**, **§2.13.5b W11a and V-R**, **§2.13.6 J-26 … J-28**, and — in
  the logical schema — the seventh table **`approved_source_revisions`** with a
  **`NOT NULL`** foreign key from `sheet_writer_journal_generations`, which is
  the fail-closed half: **an unprovenanced generation cannot be inserted, so
  activation cannot be reached.**
- **`JNL-51` case (g)** is the negative test the finding required.
- **§2.12.2** is now the single canonical primary/supplementary membership table;
  the isolation sentence that denied `freedomjournal` is **withdrawn**; **`E8`
  gains `freedomjournal`**; and **`JNL-52`**'s eight cases are your check
  **C-4**.

**At submission, nothing else moved.** `C-1` was not completed, `C-3` and `C-4`
were not run, the residuals were unaccepted and **P5.0-R5 was Blocking**. The
2026-09-02 re-review closes the two design findings but does not change those
operational facts or the Blocking risk.

**Read §1 through §8 below as still current**, with three amendments: the surface
count is **twelve**, the estimate is **4.5–5.5 reviewer-days**, and there are
**five** residuals, all unaccepted.

## 1. The assignment, and its two conditions

You hold three roles on this package: Independent Reviewer, independent
logical-schema reviewer and — from today — Security Reviewer. The assignment is
compatible with implementation-plan §0.3, which bars a reviewer from approving
their own implementation: you did not implement Package 5.0.

Two conditions attach, and both are recorded in the OD-61 trace:

1. **This is a distinct security-focused pass.** Package plan §9.2 sizes it at
   **4.5–5.5 reviewer-days** over **twelve surfaces**. The revision-11 design
   re-review you returned on 2026-08-31 is **not** this pass and must not be
   cited as one. A design re-review that found no Blocking finding says nothing
   about whether the host privilege boundary holds.
2. **The concentration is known.** Because you hold the design and security
   roles together, the two judgements are no longer independent of each other.
   The Acceptance Authority accepted that knowingly. Where your security
   conclusion depends on a design claim you previously accepted, say so, so the
   Acceptance Authority can see which findings rest on a single reviewer.

**What a recommendation can and cannot do.** You may recommend readiness. You
**cannot approve the package gate** — that is the Acceptance Authority's, under
§0.3. Blocking security findings require remediation and independent re-review.

## 2. What you are reviewing

| Artifact | Path | Revision |
|---|---|---|
| Package plan | `docs/review/phase-5-0-package-plan.md` | **12** |
| Logical schema | `docs/review/phase-5-0-logical-schema.md` | **12** |
| Threat and authority model | package plan §2.13.5c | eleven authorities `A1 … A11`, **`A5` widened**; **fourteen** falsification rows, **F-13** new |
| **Reviewed-source provenance contract** | package plan **§2.12.5a**; logical schema **§3.7**, **§3.8** | **new in revision 12** |
| **Canonical identity and group membership** | package plan **§2.12.2** | **new in revision 12** — the single place a membership is stated |
| **Remediation handback** | `docs/review/phase-5-0-remediation-r11-handback.md` | the response to your two findings |
| Open decisions | `docs/discovery/open-decisions.md`, OD-62 … OD-66 | all Open; OD-65 extended, OD-66 gains an unadopted **option A-3** |
| Scope statement | package plan §9.2 | **twelve** surfaces |
| Verified host facts | package plan §8.1, `H-1 … H-6` | read, not assumed |
| Governing rules | `.agents/AGENTS.md`, implementation-plan §0.2–§0.3, §16.4 | — |

The R2–R10 handbacks (`docs/review/phase-5-0-remediation-r*-handback.md`) are
decision history. They are available but are not required reading for this pass.

## 3. The twelve surfaces (package plan §9.2)

1. an authorization-bearing operator command that can change which store is
   authoritative;
2. **five** append-only histories whose integrity depends on withheld grants and
   triggers — *four before revision 12 added `approved_source_revisions`*;
3. a database-enforced activation precondition that is the platform's only fence
   against dual write authority;
4. a new database principal and `pg_hba.conf` entry (D5.0-11);
5. the relocation of the Google service-account credential out of the Freedom
   bot into `freedom-sheet-writer`, plus a procedure that changes a **production
   Drive permission** at each cutover (D5.0-9);
6. two new operating-system identities, a `sudoers` drop-in, `pg_hba.conf`
   ordering and a `pg_ident.conf` map (D5.0-11, D5.0-12);
7. a root-owned deployment path (§2.12.5). **Your first pass found that its
   digest verification was not provenance — P5.0-SR1.** Surface 12 is what
   replaces the check, so this surface is now the path and its ownership;
8. the pre-existing group-writable repository tree (H-1) and the unhardened
   `freedom-bot` unit (H-2). Neither is created by this package; both are
   load-bearing for §2.12.6's argument;
9. a **second privileged tool that runs as root** — `freedom-journal-admin`,
   with its own `sudoers` drop-in (§2.13.7). It is the only thing in this package
   that runs as root and the only path that can destroy evidence. Review it as a
   privileged tool, not a maintenance script;
10. a root-owned durable state hierarchy carrying integrity evidence
    (§2.13.3–§2.13.4). The question is not *"can the writer append?"* but
    **"can anything the writer controls make history disappear?"**; and
11. **four deliberate relaxations of the §2.13.3 permission model**, each a
    grant to the identity the section exists to constrain: the `freedomjournal`
    group and the writer-readable seal; the transient probe arena the writer's
    identity may fully write; the transient `systemd-run` unit **started as root
    at provisioning**, carrying directives read from a file on disk with one
    substitution the tool performs itself; and the second transient directory
    `…/probe-ro`. The implementer's argument that these are safe is exactly the
    kind of argument this review should **test rather than accept**; and
12. **the reviewed-source provenance chain** (§2.12.5a) — **new in revision 12,
    and the direct consequence of P5.0-SR1**: an approval record whose only
    integrity is root ownership and mode, and which is the single point where a
    human's approval enters the design; a root-owned bare Git object store
    refreshed from an authenticated origin; a reviewed deployment map that
    decides which files are installed **and with what owner and mode**; a
    hash-pinned dependency region bound by a lock file rather than by review; and
    a root-run algorithm that installs the program carrying authority over the
    authority plane and the journal evidence. **The design states plainly that
    root remains inside the trust boundary — R-5.0-15** — and prices the signed
    alternative as OD-66 option A-3 without adopting it.

## 4. The four checks the implementer could not run — these are yours

Recorded as not run rather than assumed clear. Each is a host read, not a
mutation.

| # | Check | Why it was not run | What it bears on |
|---|---|---|---|
| C-1 | Enumerate `/etc/sudoers.d/` | Not readable by the implementing account | Whether the two proposed `sudoers` drop-ins collide with, or are pre-empted by, an existing rule |
| C-2 | Host-wide setuid audit | Same | Whether some existing setuid binary already gives a service identity a path to the authority the design withholds |
| C-3 | Confirm `chattr +a` is honoured at the journal path | Needs `CAP_LINUX_IMMUTABLE`; setting it would be an unauthorized environment change | The **second** independent layer of §2.13.3. Note this is assumption **A-5.0-5** and is properly discharged by `verify-capability` under authorized operational evidence, not by this review |
| C-4 | Confirm the `0750`/`0440` grant gives `freedomsheet` read access to the seal and gives `discordbot` and `freedomweb` none | The hierarchy does not exist yet | Surface 11's claim that the `freedomjournal` relaxation is a net **tightening**. **Revision 12 specifies this check as `JNL-52`** — eight cases of positive and negative `id`, `namei -l` and `open` evidence for all four identities, each first asserting `getent group` against §2.12.2 exactly. **Specifying it is not running it**, and it remains outstanding |

C-1 and C-2 are answerable by reading this host. C-3 and C-4 are not, and should
be returned as conditions on operational evidence rather than as review findings.

## 5. The five residuals this design does not refuse

Do not treat these as findings to be closed. They are acceptance questions, and
they belong to the Acceptance Authority and the Data Owner under OD-66. Your job
is to confirm the enumeration is complete and correctly bounded — that is, that
there is no **sixth**. *Revision 11 offered three and asked whether there was a
fourth; revision 12 adds two of its own and asks the same question one number
higher.*

- **R-5.0-12 — combined authority.** An attacker holding host root *and*
  PostgreSQL superuser authority writes both copies the design compares. Nothing
  here refuses it. Detected by `sudo log_output`, journald, `audit_events` and
  offline backups.
- **R-5.0-13 — forged matching host identity.** An actor holding root on
  whichever host the tree is read on can rewrite `/etc/machine-id` to the
  recorded value, after which neither the writer nor the coordinator refuses,
  because every copy of that fact carries the same value. **Option A-2** (a
  TPM-sealed key or coordinator-signed host token) would make this a refusal; it
  is priced in OD-66 and deliberately **not adopted**, because it makes a
  legitimate restore onto replacement hardware fail closed.
- **R-5.0-14 — cleanup residue.** A failed privileged cleanup leaves a
  writer-writable transient directory, and generation creation is blocked, until
  an operator acts.
- **R-5.0-15 — the provenance trust anchor is a root-owned file.** *New in
  revision 12.* An actor holding **A5** rewrites the approval record, the object
  store and the provenance record so that every host copy agrees on a tree it
  chose. The database still refuses, because the generation needs an
  `approved_source_revisions` row and that needs **A8** — **but an actor holding
  A5 *and* A8 approves and registers its own revision, and nothing here refuses
  it.** That boundary is **operator trust, not a technical control**. **Option
  A-3** — a signed approval record verified against a root-held keyring — would
  narrow it to the A5-only case; it is priced in OD-66 and deliberately **not
  adopted**, because it needs a signing key with a custody model this project
  does not have and it makes a legitimate emergency deployment fail closed when
  the signer is unavailable.
- **R-5.0-16 — provenance unavailability.** *New in revision 12.* A deployment
  with no approval record, no provenance record or a drifted tree cannot produce
  a generation at all, and a running writer whose provenance record is removed
  refuses every Sheet mutation at **W11a**. Fail-closed and intended; the cost is
  an emergency redeployment that stops until an approval exists.

## 6. The specific questions to answer

Beyond the §9.2 scope, these are the points where the design asks to be trusted
rather than proved:

1. **Does the `pg_hba`/`pg_ident` ordering hold?** One `peer` line with
   `map=freedom_coord` above `local all … reject` and three written-out
   `host`/`hostssl`/`hostnossl` rejects. Note **H-3**: `/var/run/postgresql` is
   `drwxrwsr-x`, so every local identity reaches the socket and the isolation is
   the map, not the path. Confirm no later broad rule can silently expose the
   role, and that `PASSWORD NULL` makes a leaked `.pgpass` worthless.
2. **Is the eleven-authority register correct against the kernel contract?**
   `FS_IOC_SETFLAGS` makes **two** checks — effective UID equal to the inode
   owner **or** `CAP_FOWNER`, in addition to `CAP_LINUX_IMMUTABLE` for the
   immutable and append flags. Revision 9 got this wrong and revision 10
   corrected it with `A10`/`A11`. Confirm the correction, then confirm the
   **holder table** identity by identity and the eleven changed falsification
   rows.
3. **Does the root-owned deployment path actually escape H-1?** The whole
   §2.12.6 argument is that a coordinator running from the group-writable
   repository would execute code a compromised service process can choose.
   Confirm the digest verification cannot be skipped without detection —
   surface 7 fails **silently**.
4. **Is the transient root-started `systemd-run` unit a widening?** It reads its
   directive set from the deployed unit file and applies one substitution itself.
   Confirm that substitution cannot be induced to redirect `ReadWritePaths=`
   somewhere that matters.
5. **Can anything the writer controls make history disappear?** §2.13.4's
   manipulation matrix answers this one `errno` at a time across fifteen rows.
   Test the matrix, not the summary.
6. **Is the `freedomjournal` relaxation really a tightening?** It grants the
   constrained identity a read it did not have, while removing *other*'s
   traverse. Both halves need to be true for the claim to hold. **And it is now
   answerable**: revision 11's §2.12.2 said the group did not exist, which is why
   this could not be settled last time; §2.12.2 is now canonical and `JNL-52`
   specifies the evidence.
7. **New for revision 12 — does the provenance chain bind what it claims to?**
   Is `0700 root:root` on a bare object store sufficient, or can an object enter
   it short of root — a fetch run by the wrong identity, an alternates file, a
   submodule, a hook, a `packed-refs` edit? **Is the SHA-1 argument sound** —
   that recomputing `source_manifest_digest` from the object bytes and comparing
   with the approval record's SHA-256 makes a Git object-id collision
   insufficient — or does the extraction path trust an object id somewhere the
   recomputation does not cover? Is the two-region partition genuinely closed,
   and is a hash-pinned lock an adequate binding for the unreviewed half? Does
   any ordering of `D0 … D8` leave the deployed root live while `PVR` is absent
   or stale?
8. **New for revision 12 — is the `NOT NULL` foreign key the fence the plan says
   it is?** The claim is that an unprovenanced generation cannot be inserted **by
   any principal including the schema owner**, and that §3.4's activation trigger
   therefore cannot be satisfied. Test it by direct statement rather than through
   the command, and check that no other path — a data-only restore, a deferred
   constraint, `session_replication_role`, a `TRUNCATE` and reload — reaches an
   inserted row without it.
9. **New for revision 12 — is R-5.0-15 correctly bounded?** Is there any identity
   short of root that can write `/etc/freedom-blades/`, and does the `sudo` path
   to **A8** widen the residual in a way §2.12.4 does not already bound?

## 7. What this review does not decide

- It does not rule OD-62, OD-63, OD-64, OD-65 or OD-66. OD-64, OD-65 and OD-66
  are owned *on your review*; the ruling itself is the Product Owner's,
  Operations Owner's and Data Owner's.
- It does not accept R-5.0-12 through **R-5.0-16**. Those are the Acceptance
  Authority's.
- It does not confirm A-5.0-3, A-5.0-4 or A-5.0-5, and it does not substitute
  for the operational evidence P5.0-R5 is blocked on. **Design closure is not
  evidence closure.**
- It does not authorize implementation, migration `0014`, principal creation,
  host changes, deployment or cutover.

## 8. State carried into this review

- **P5.0-SR1: remediated on paper, not closed. P5.0-SR2: remediated on paper,
  not closed.** Both are yours to close.
- P5.0-R1: **open**. P5.0-R4: **open**. P5.0-R2: **closed**.
- P5.0-R5: **Blocking**, operational evidence outstanding.
- OD-62 … OD-66: **Open**. OD-61: **closed 2026-08-31**.
- A-5.0-3, A-5.0-4, A-5.0-5: **unconfirmed**; A-5.0-5 widened again at R11.
- **C-1: not completed. C-2: completed as an inventory. C-3, C-4: not run** —
  C-4 now has a specified test, `JNL-52`, which has not been executed.
- **R-5.0-12 … R-5.0-16: unaccepted.**
- Package 5.0: **not ready**. Implementation, migration, deployment, cutover and
  Package 5.1+: **unauthorized**.
- **No host object named by §2.12.5a or §2.12.2 exists.** `freedomcoord`,
  `freedomsheet`, `freedomjournal` and `fbprobe` do not exist; no Git object
  store, approval record or provenance record was created; **no `git` write was
  performed**.
- `git diff --check`: clean, 2026-08-31.
